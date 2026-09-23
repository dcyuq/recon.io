from __future__ import annotations
import json
import tempfile

from reconio import common, flags, runner, target

VERB = "fingerprint"
BIN = flags.BINARY[VERB]
_VALUE_FLAGS = {"-a"}


def _parse(text):
    rows = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return rows
    for e in data:
        tgt = e.get("target", "")
        status = str(e.get("http_status", "") or "")
        plugins = e.get("plugins", {})
        tech = ", ".join(sorted(plugins.keys()))
        rows.append((tgt, status, tech))
    return rows


def run(tgt, raw=None):
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, selected = common.split(tokens, _VALUE_FLAGS)
    tgt = found or tgt
    if not target.looks_like_target(target.parse(tgt)):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1
    if not selected and not raw:
        selected = common.prompt_flags(VERB)
    flags.preview(VERB, tgt, selected, binary=BIN)
    with tempfile.NamedTemporaryFile("r", suffix=".json", delete=True) as f:
        cmd = common.build(BIN, selected, tgt=tgt, trailing=["--color=never", f"--log-json={f.name}"])
        code, out = runner.run_with_loader(cmd, f"fingerprinting {tgt}")
        try:
            text = open(f.name).read()
        except OSError:
            text = ""
    rows = _parse(text)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["TARGET", "STATUS", "TECH"], rows, "no fingerprint")
    return code