from __future__ import annotations
import json

from reconio import common, flags, runner, target

VERB = "tls"
BIN = flags.BINARY[VERB]
_VALUE_FLAGS = set()


def _parse(out):
    rows = []
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            d = json.loads(ln)
        except json.JSONDecodeError:
            continue
        host = d.get("host", "")
        cn = d.get("subject_cn", "") or ""
        issuer = d.get("issuer_cn", "") or ""
        expiry = d.get("not_after", "") or ""
        rows.append((host, cn, issuer, expiry))
    return rows


def run(tgt, raw=None):
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, selected = common.split(tokens, _VALUE_FLAGS)
    tgt = found or tgt
    host = target.parse(tgt)
    if not target.looks_like_target(host):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1
    if not selected and not raw:
        selected = common.prompt_flags(VERB)
    flags.preview(VERB, host, selected, binary=BIN)
    cmd = common.build(BIN, selected, target_flag="-u", tgt=host, trailing=["-json", "-silent"])
    code, out = runner.run_with_loader(cmd, f"checking tls on {host}")
    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["HOST", "CN", "ISSUER", "EXPIRES"], rows, "no tls data")
    return code