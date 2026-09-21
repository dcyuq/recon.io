from __future__ import annotations
 
from reconio import flags, runner
 
VERB = "pscan"
BIN = flags.BINARY[VERB]
 
 
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
 
 
def _passthrough(raw: list[str]) -> list[tuple[str, str | None]]:
    selected = []
    i = 0
    while i < len(raw):
        tok = raw[i]
        if tok.startswith("-"):
            if i + 1 < len(raw) and not raw[i + 1].startswith("-"):
                selected.append((tok, raw[i + 1]))
                i += 2
            else:
                selected.append((tok, None))
                i += 1
        else:
            i += 1
    return selected
 
 
def run(target: str, raw: list[str] | None = None) -> int:
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    selected = _passthrough(raw) if raw else _prompt_flags()
    cmd = flags.preview(VERB, target, selected, binary=BIN)
    code, out = runner.run_with_loader(cmd, f"scanning {target}")
    print(out)
    return code
 