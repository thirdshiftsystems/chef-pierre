#!/usr/bin/env python3
"""Kroger API helper for Chef Pierre — OAuth2 + product search + cart add.

Zero-dependency (stdlib only). Creds live in creds.json (chmod 600) next to
this script; user tokens in tokens.json (chmod 600).

SETUP (you do the registration once, ~5 min):
  1. https://developer.kroger.com  ->  Sign In  ->  Create an Account
  2. Create an Application -> get Client ID + Client Secret
  3. Register redirect URI  ->  http://localhost:8787/callback  (exact)
  4. Put the pair into creds.json next to this script (chmod 600)

FLOW:
  kroger.py config                       # what's set up / missing
  kroger.py authorize                    # consent URL: you log in, tokens are saved
  kroger.py stores --zip <ZIP>           # find nearby stores, pick locationId
  kroger.py search "eggs" --json         # find productIds (app token, no user login)
  kroger.py add --product-id 0001111047923 --qty 2
  kroger.py add "whole milk" --qty 1     # convenience: search + add top match
  kroger.py show                         # best-effort cart dump (public tier is add-only)

All commands print JSON with --json (for agent parsing); default is human text.
"""
import argparse
import base64
import json
import os
import secrets
import stat
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
# OPTIONAL: route Kroger API calls through an HTTP proxy if your network
# requires one (set HTTPS_PROXY in the environment before running).

HERE = os.path.dirname(os.path.abspath(__file__))
CREDS = os.path.join(HERE, "creds.json")
TOKENS = os.path.join(HERE, "tokens.json")
OAUTH2 = "https://api.kroger.com/v1/connect/oauth2"
API = "https://api.kroger.com"
# --- least privilege by default -------------------------------------------------
# Read-only until the household explicitly opts in to cart writes. The OAuth
# token itself carries no write capability until then, so an agent that "decides"
# to fill a cart cannot: the grant doesn't allow it.
READ_ONLY_SCOPE = "product.compact"
WRITE_SCOPE = "cart.basic:write product.compact"
DEFAULT_SCOPE = READ_ONLY_SCOPE
DEFAULT_REDIRECT = "http://localhost:8787/callback"
# OPTIONAL: if the browser doing the consent lives on ANOTHER machine (e.g.
# your laptop while the agent runs on a server), register a second redirect
# URI in the developer portal using that box's tailnet/LAN IP, e.g.
#   http://<your-box-ip>:8787/callback
# Set it below to make that redirect work without an SSH tunnel. Leave empty
# to use only the localhost redirect (which needs ssh -L 8787:127.0.0.1:8787).
# Redirect host of this box — the redirect that actually works from the
# browser on any device (laptop/phone) without an SSH tunnel. Keep in sync
# with the Web Redirect URI registered in the Kroger developer portal.
TAILNET_REDIRECT = ""  # e.g. "http://<your-box-ip>:8787/callback" if the browser lives on another machine
USER_AGENT = "chef-pierre/1.0 (Hermes agent)"


class KrogerError(Exception):
    pass


def _load_creds():
    if not os.path.exists(CREDS):
        raise KrogerError(
            f"No {CREDS}. Register at developer.kroger.com, create an app, "
            "register the redirect URI, then put client_id/client_secret here:\n"
            f'{{"client_id": "...", "client_secret": "...", "redirect_uri": "{DEFAULT_REDIRECT}"}}'
        )
    with open(CREDS) as f:
        c = json.load(f)
    if not c.get("client_id") or not c.get("client_secret"):
        raise KrogerError("creds.json is missing client_id or client_secret.")
    _harden(CREDS)
    c.setdefault("redirect_uri", DEFAULT_REDIRECT)
    # NOTE: no scope is set by default. The scope actually requested is derived
    # from cart_enabled (see _effective_scope), so the token is read-only until
    # the household opts in. Setting "scope" explicitly overrides that.
    _check_dir()
    c.setdefault("zip_code", "")
    return c


def _load_tokens():
    if not os.path.exists(TOKENS):
        raise KrogerError("No user tokens yet — run 'kroger.py authorize' first.")
    with open(TOKENS) as f:
        return json.load(f)


def _save_tokens(t):
    with open(TOKENS, "w") as f:
        json.dump(t, f, indent=2)
    os.chmod(TOKENS, 0o600)


def _harden(path):
    """Enforce owner-only perms on a credential file (create-then-chmod safe)."""
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            os.chmod(path, 0o600)
            print(f"NOTE: tightened {os.path.basename(path)} from {oct(mode)} to 0600 "
                  f"(credentials must not be group/world readable).", file=sys.stderr)
    except FileNotFoundError:
        pass


def _check_dir():
    """Warn (do not silently break shared setups) if the tool dir is not private."""
    try:
        mode = stat.S_IMODE(os.stat(HERE).st_mode)
        if mode & 0o077:
            print(f"NOTE: {HERE} is mode {oct(mode)} — credentials live here. "
                  f"chmod 700 it if no other account needs this directory.",
                  file=sys.stderr)
    except OSError:
        pass


def _effective_scope(creds):
    """Least privilege: read-only unless cart writes were explicitly enabled."""
    if creds.get("scope"):
        return creds["scope"]  # explicit override (advanced)
    return WRITE_SCOPE if creds.get("cart_enabled") is True else READ_ONLY_SCOPE


def _require_cart_enabled(creds):
    """Machine-enforced gate: no cart mutation without an explicit opt-in."""
    if creds.get("cart_enabled") is not True:
        raise KrogerError(
            "Cart writes are DISABLED for this account (read-only by default).\n"
            "To enable: the household must consent, then set \"cart_enabled\": true in\n"
            f"{CREDS} and re-run 'authorize' so the token carries cart.basic:write.\n"
            "Nothing was added to the cart."
        )


def _http(method, url, headers=None, body=None, raw_body=None):
    req = urllib.request.Request(url, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    req.add_header("User-Agent", USER_AGENT)
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    elif raw_body is not None:
        data = raw_body.encode()
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        try:
            raw = e.read()
            if (e.headers.get("Content-Encoding") or "").lower() == "gzip":
                import gzip

                raw = gzip.decompress(raw)
            detail = raw.decode(errors="replace")[:600]
        except Exception:
            detail = ""
        raise KrogerError(f"HTTP {e.code} {url}\n{detail}") from e


def _token_request(params):
    creds = _load_creds()
    auth = base64.b64encode(
        f"{creds['client_id']}:{creds['client_secret']}".encode("ascii")
    ).decode("ascii")
    body = urllib.parse.urlencode(params)
    status, raw = _http(
        "POST",
        f"{OAUTH2}/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        raw_body=body,
    )
    return json.loads(raw.decode())


def app_token():
    """Client-credentials token for product/location search (no user login)."""
    t = _token_request(
        {"grant_type": "client_credentials", "scope": "product.compact"}
    )
    return t["access_token"]


def _user_token(force_refresh=False):
    t = _load_tokens()
    if not force_refresh and t.get("expires_at", 0) > time.time() + 60:
        return t["access_token"]
    if not t.get("refresh_token"):
        raise KrogerError("No refresh token — run 'kroger.py authorize' again.")
    try:
        nt = _token_request(
            {"grant_type": "refresh_token", "refresh_token": t["refresh_token"]}
        )
    except KrogerError as e:
        raise KrogerError(f"Refresh failed ({e}). Re-run 'kroger.py authorize'.") from e
    t.update(
        access_token=nt["access_token"],
        expires_at=time.time() + int(nt.get("expires_in", 3600)) - 60,
    )
    if nt.get("refresh_token"):
        t["refresh_token"] = nt["refresh_token"]
    _save_tokens(t)
    return t["access_token"]


class _Callback(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in q:
            self.server.auth_code = q["code"][0]
            self.server.auth_error = None
            body = "<html><body><h2>Kroger linked to Chef Pierre — close this tab.</h2></body></html>".encode()
        else:
            self.server.auth_code = None
            self.server.auth_error = q.get("error", ["unknown_error"])[0]
            body = (
                "<html><body><h2>Authorization failed: %s</h2></body></html>"
                % self.server.auth_error
            ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # silence
        pass


def cmd_config(args):
    try:
        c = _load_creds()
    except KrogerError as e:
        print(e)
        return 1
    print(f"client_id:     {c['client_id']}")
    print(f"redirect_uri:  {c['redirect_uri']}")
    print(f"scope:         {c['scope']}")
    print(f"zip_code:      {c['zip_code']}")
    print(f"location_id:   {c.get('location_id') or '(unset — run stores)'}")
    if os.path.exists(TOKENS):
        t = _load_tokens()
        fresh = t.get("expires_at", 0) > time.time()
        print(f"user token:    {'present (expires %s)' % time.ctime(t.get('expires_at', 0)) if fresh else 'EXPIRED — refresh on next use'}")
    else:
        print("user token:    (none — run authorize)")
    return 0


def cmd_authorize(args):
    creds = _load_creds()
    state = secrets.token_urlsafe(16)
    redirect = creds["redirect_uri"]
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": _effective_scope(creds),
        "state": state,
    }
    url = f"{OAUTH2}/authorize?" + urllib.parse.urlencode(params)
    # Bind the callback listener where the browser can actually reach it:
    # if the redirect URI's host is an IP literal,
    # bind there; otherwise fall back to loopback (classic localhost flow).
    rp = urllib.parse.urlparse(redirect)
    # If the redirect URI's host is an IP literal,
    # bind there; otherwise bind loopback (localhost → SSH tunnel / local).
    host_literal = rp.hostname and all(ch.isdigit() or ch == "." for ch in rp.hostname)
    bind_host = rp.hostname if host_literal else "127.0.0.1"
    port = rp.port or 8787
    print("1) Open this URL in a browser (log in with the Kroger account):\n")
    print(f"   {url}\n")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    server = ThreadingHTTPServer((bind_host, port), _Callback)
    server.auth_code = None
    server.auth_error = None
    print(f"2) Waiting for the callback on {bind_host}:{port}/callback ... (Ctrl-C to abort)")
    while server.auth_code is None and server.auth_error is None:
        server.handle_request()
    if server.auth_error:
        raise KrogerError(f"Authorization refused: {server.auth_error}")
    t = _token_request(
        {
            "grant_type": "authorization_code",
            "code": server.auth_code,
            "redirect_uri": redirect,
        }
    )
    _save_tokens(
        {
            "access_token": t["access_token"],
            "refresh_token": t.get("refresh_token", ""),
            "expires_at": time.time() + int(t.get("expires_in", 3600)) - 60,
        }
    )
    print("Authorized! Tokens saved to", TOKENS)
    return 0


def cmd_token(args):
    print(_user_token(force_refresh=args.refresh))
    return 0


def _api_get(path, token, params=None):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    status, raw = _http("GET", url, headers={"Authorization": f"Bearer {token}"})
    return json.loads(raw.decode())


def cmd_stores(args):
    token = app_token()
    d = _api_get(
        "/v1/locations",
        token,
        {"filter.zipCode.near": args.zip or _load_creds()["zip_code"], "filter.limit": 8},
    )
    data = d.get("data", [])
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    if not data:
        print("No stores found for that zip.")
        return 1
    for s in data:
        a = s.get("address", {})
        print(
            f"{s['locationId']}  {s.get('name','?'):45.45} {a.get('addressLine1','')}, {a.get('city','')} {a.get('zipCode','')}"
        )
    print("\nSave your store: edit creds.json -> \"location_id\": \"<id>\"")
    return 0


def cmd_search(args):
    token = app_token()
    creds = _load_creds()
    loc = args.location or creds.get("location_id")
    if not loc:
        print("No location_id set. Run 'kroger.py stores --zip <ZIP>' and save one to creds.json.")
        return 1
    d = _api_get(
        "/v1/products",
        token,
        {
            "filter.term": args.term,
            "filter.locationId": loc,
            "filter.limit": args.limit,
        },
    )
    data = d.get("data", [])
    if args.json:
        out = [
            {
                "productId": p["productId"],
                "description": p.get("description", ""),
                "size": (p.get("items") or [{}])[0].get("size", ""),
                "price": ((p.get("items") or [{}])[0].get("price", {}) or {}).get("regular", None),
            }
            for p in data
        ]
        print(json.dumps(out, indent=2))
        return 0
    if not data:
        print("No products found.")
        return 1
    for p in data:
        it = (p.get("items") or [{}])[0]
        price = (it.get("price") or {}).get("regular", "?")
        print(f"{p['productId']}  ${price:>7}  {p.get('description','')}  {it.get('size','')}")
    return 0


def cmd_add(args):
    _require_cart_enabled(_load_creds())
    if args.product_id:
        pid, label = args.product_id, args.product_id
    elif args.item:
        creds = _load_creds()
        loc = args.location or creds.get("location_id")
        if not loc:
            print("No location_id set — run 'kroger.py stores' and save one to creds.json.", file=sys.stderr)
            return 1
        d = _api_get(
            "/v1/products",
            app_token(),
            {"filter.term": args.item, "filter.locationId": loc, "filter.limit": 5},
        )
        data = d.get("data", [])
        if not data:
            print(f"No Kroger product found for '{args.item}'.", file=sys.stderr)
            return 1
        p = data[0]
        pid = p["productId"]
        it = (p.get("items") or [{}])[0]
        label = f"{p.get('description', '')} {it.get('size', '')}".strip()
        if len(data) > 1:
            print(f"NOTE: {len(data)} matches; using top match: {label}", file=sys.stderr)
    else:
        print("Provide --product-id or a search term.", file=sys.stderr)
        return 1
    token = _user_token()
    body = {"items": [{"upc": pid, "quantity": args.qty}]}
    status, raw = _http(
        "PUT",
        f"{API}/v1/cart/add",
        headers={"Authorization": f"Bearer {token}"},
        body=body,
    )
    accepted = status in (200, 201, 202, 204)
    if args.json:
        print(json.dumps({
            # ACCEPTED is not VERIFIED. The public Cart API is fire-and-forget:
            # it returns 204 with no body for any GTIN-shaped value, including
            # ids that match no real product, and there is no read-back endpoint
            # (GET /v1/cart is 404 on this tier). So never report "the cart now
            # holds N items" as a fact — report N accepted adds and tell the
            # household to confirm in the app.
            "accepted": accepted,
            "verified": False,
            "status": status,
            "upc": pid,
            "quantity": args.qty,
            "label": label,
            "note": "accepted by the Cart API; presence in the cart is NOT verifiable via API — confirm in the app",
        }))
        return 0 if accepted else 1
    if accepted:
        print(f"Accepted: {args.qty} x {label} (HTTP {status}). "
              f"This API is fire-and-forget — {status} means the request was accepted, "
              f"NOT that the item is in the cart. Confirm in the app.")
        return 0
    print(f"FAILED: {args.qty} x {label} — HTTP {status}. Nothing added.", file=sys.stderr)
    return 1
    return 0


def cmd_show(args):
    token = _user_token()
    try:
        status, raw = _http("GET", f"{API}/v1/cart", headers={"Authorization": f"Bearer {token}"})
        if args.json:
            print(raw.decode())
        else:
            print(raw.decode(errors="replace")[:2000])
    except KrogerError as e:
        print(f"Cart read not available: {e}\n(Public tier is add-only — the Kroger app is the source of truth.)")
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description="Kroger API helper for Chef Pierre")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("config", help="show setup state")
    p.set_defaults(fn=cmd_config)

    p = sub.add_parser("authorize", help="run the user OAuth consent flow")
    p.add_argument("--no-browser", action="store_true", help="just print the URL, don't open a browser")
    p.set_defaults(fn=cmd_authorize)

    p = sub.add_parser("token", help="print a valid user access token (refreshing if needed)")
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_token)

    p = sub.add_parser("stores", help="find Kroger-family stores near a zip")
    p.add_argument("--zip", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_stores)

    p = sub.add_parser("search", help="search products (needs location_id in creds.json)")
    p.add_argument("term")
    p.add_argument("--location", default=None)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser("add", help="add an item to the Kroger cart")
    p.add_argument("--product-id", default=None, help="exact UPC/productId")
    p.add_argument("item", nargs="?", help="search term (convenience path not yet wired)")
    p.add_argument("--qty", type=int, default=1)
    p.add_argument("--location", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("show", help="dump the cart (best effort)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    try:
        return args.fn(args)
    except KrogerError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
