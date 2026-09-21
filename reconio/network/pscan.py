from __future__ import annotations
import re

from reconio import flags, runner

VERB = "pscan"
BIN = flags.BINARY[VERB]

_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$")
_HOST = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$")
_VALUE_FLAGS = {"-p", "--min-rate", "--max-rate", "-T", "--top-ports", "-oN", "-oX", "-iL"}


def _looks_like_target(tok: str) -> bool:
    return bool(_IP.match(tok) or _HOST.match(tok))


def _split(tokens: list[str]) -> tuple[str | None, list[tuple[str, str | None]]]:
    target = None
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
        if target is None and _looks_like_target(tok):
            target = tok
        i += 1
    return target, selected


def _prompt_flags() -> list[tuple[str, str | None]]:
    flags.menu(VERB)
    raw = input("  select numbers (e.g. 1,2,8): ").strip()
    if not raw:
        return []
    specs = flags.FLAGS.get(VERB, [])
    chosen = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part) - 1
        if 0 <= idx < len(specs):
            flag, arg, _d = specs[idx]
            value = None
            if arg:
                value = input(f"  value for {flag} <{arg}>: ").strip() or None
            chosen.append((flag, value))
    return chosen


def run(target: str, raw: list[str] | None = None) -> int:
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1

    tokens = ([target] + list(raw)) if raw else [target]
    found, selected = _split(tokens)
    target = found or target

    if not _looks_like_target(target):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1

    if not selected and (not raw):
        selected = _prompt_flags()

    cmd = flags.preview(VERB, target, selected, binary=BIN)
    code, out = runner.run_with_loader(cmd, f"scanning {target}")
    print(out)
    return code