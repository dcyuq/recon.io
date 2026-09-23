from __future__ import annotations

from reconio import common, flags, runner

VERB = "sherlock"
BIN = flags.BINARY[VERB]
_VALUE_FLAGS = {"-timeout"}


def _split(tokens):
    uname = None
    selected = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            if tok in _VALUE_FLAGS and i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                selected.append((tok, tokens[i + 1]))
                i += 2
                continue
            selected.append((tok, None))
            i += 1
            continue
        if uname is None:
            uname = tok
        i += 1
    return uname, selected


def _parse(out, show_all):
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("[+]"):
            body = line[3:].strip()
            if ": " in body:
                site, url = body.split(": ", 1)
                rows.append((site, url, "found"))
        elif line.startswith("[-]") and show_all:
            body = line[3:].strip()
            site = body.split(":", 1)[0]
            rows.append((site, "-", "not found"))
    return rows


def run(uname, raw=None):
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    tokens = ([uname] + list(raw)) if raw else [uname]
    found, selected = _split(tokens)
    uname = found or uname
    if not uname or uname.startswith("-"):
        print("  usage: sherlock <username> [flags]")
        return 1
    show_all = any(f == "-all" for f, _ in selected)
    passthrough = [(f, v) for f, v in selected if f != "-all"]
    flags.preview(VERB, uname, passthrough, binary=BIN)
    parts = [BIN, uname, "--no-color"]
    if show_all:
        parts.append("--print-all")
    for f, v in passthrough:
        parts.append(f)
        if v:
            parts.append(v)
    code, out = runner.run_with_loader(" ".join(parts), f"hunting username {uname}")
    rows = _parse(out, show_all)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["SITE", "URL", "STATUS"], rows, "no accounts found")
    return code