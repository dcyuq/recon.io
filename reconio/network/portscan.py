from __future__ import annotations
import json

from reconio import common, flags, runner, target

VERB = "portscan"
BIN = flags.BINARY[VERB]
_VALUE_FLAGS = {"-p", "-top-ports", "-rate", "-c"}


def _parse(out):
    hosts = {}
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            d = json.loads(ln)
        except json.JSONDecodeError:
            continue
        ip = d.get("ip") or d.get("host") or ""
        port = str(d.get("port", ""))
        hosts.setdefault(ip, []).append(port)
    return [(ip, ", ".join(ports)) for ip, ports in hosts.items()]


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
    cmd = common.build(BIN, selected, target_flag="-host", tgt=host, trailing=["-json", "-silent"])
    code, out = runner.run_with_loader(cmd, f"port scanning {host}")
    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["IP", "PORTS"], rows, "no open ports")
    return code