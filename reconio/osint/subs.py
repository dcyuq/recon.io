from __future__ import annotations

from reconio import common, flags, runner, target

VERB = "subs"
BIN = flags.BINARY[VERB]
_VALUE_FLAGS = {"-timeout", "-t"}


def _parse(out):
    rows = []
    for ln in out.splitlines():
        ln = ln.strip()
        if ln and "." in ln and " " not in ln:
            rows.append((ln,))
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
    cmd = common.build(BIN, selected, target_flag="-d", tgt=host, trailing=["-silent"])
    code, out = runner.run_with_loader(cmd, f"enumerating subdomains of {host}")
    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["SUBDOMAIN"], rows, "no subdomains found")
    return code