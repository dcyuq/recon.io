from __future__ import annotations

from reconio import common, target

try:
    import requests
    _REQ = True
except ImportError:
    _REQ = False

VERB = "crt"


def run(tgt, raw=None):
    if not _REQ:
        print("  requests not installed")
        return 1
    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, _ = common.split(tokens, set())
    tgt = found or tgt
    host = target.parse(tgt)
    if not target.looks_like_target(host):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1
    url = f"https://crt.sh/?q=%25.{host}&output=json"
    print(f"  querying crt.sh for {host} ...")
    try:
        r = requests.get(url, timeout=20)
        data = r.json()
    except Exception as e:
        print(f"  crt.sh request failed: {e}")
        return 1
    names = set()
    for entry in data:
        for n in str(entry.get("name_value", "")).splitlines():
            n = n.strip().lstrip("*.")
            if n and host in n:
                names.add(n)
    rows = [(n,) for n in sorted(names)]
    common.table(["SUBDOMAIN"], rows, "no certs found")
    return 0