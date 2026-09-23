from __future__ import annotations

from reconio import common, flags, runner, target

VERB = "ssl"
BIN = flags.BINARY[VERB]


def run(tgt, raw=None):
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, selected = common.split(tokens, set())
    tgt = found or tgt
    host = target.parse(tgt)
    if not target.looks_like_target(host):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1
    extra = [f for f, _ in selected]
    cmd = f"{BIN} --quiet --color 0 {' '.join(extra)} {host}".replace("  ", " ")
    print("  note: testssl is thorough and slow, this may take a while")
    code, out = runner.run_with_loader(cmd, f"scanning tls/ssl on {host}")
    print(out)
    return code