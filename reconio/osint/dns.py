from __future__ import annotations
import json

from reconio import common, flags, runner, target

VERB = "dns"
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
        a = ", ".join(d.get("a", []) or [])
        cname = ", ".join(d.get("cname", []) or [])
        mx = ", ".join(d.get("mx", []) or [])
        rows.append((host, a, cname, mx))
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
    extra = [f for f, _ in selected] or ["-a", "-cname", "-mx"]
    cmd = f"echo {host} | {BIN} {' '.join(extra)} -json -silent"
    code, out = runner.run_with_loader(cmd, f"resolving {host}")
    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["HOST", "A", "CNAME", "MX"], rows, "no records")
    return code