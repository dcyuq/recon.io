from __future__ import annotations

from reconio import flags, target

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"


def split(tokens, value_flags):
    tgt = None
    selected = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            if tok in value_flags and i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                selected.append((tok, tokens[i + 1]))
                i += 2
                continue
            selected.append((tok, None))
            i += 1
            continue
        if tgt is None and target.looks_like_target(target.parse(tok)):
            tgt = tok
        i += 1
    return tgt, selected


def prompt_flags(verb):
    flags.menu(verb)
    raw = input("  select numbers (e.g. 1,2): ").strip()
    if not raw:
        return []
    specs = flags.FLAGS.get(verb, [])
    chosen = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part) - 1
        if 0 <= idx < len(specs):
            fl, arg, _d = specs[idx]
            val = None
            if arg:
                val = input(f"  value for {fl} <{arg}>: ").strip() or None
            chosen.append((fl, val))
    return chosen


def build(binary, selected, target_flag=None, tgt=None, trailing=None):
    parts = [binary]
    if target_flag and tgt is not None:
        parts += [target_flag, tgt]
    for fl, val in selected:
        parts.append(fl)
        if val:
            parts.append(val)
    if trailing:
        parts += trailing
    if not target_flag and tgt is not None:
        parts.append(tgt)
    return " ".join(parts)


def table(headers, rows, empty="no results"):
    if not rows:
        print(f"  {empty}")
        return
    if _RICH:
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        for h in headers:
            t.add_column(h)
        for r in rows:
            t.add_row(*[(str(c) if c not in (None, "") else "-") for c in r])
        _console.print(t)
    else:
        widths = [max(len(h), 14) for h in headers]
        print("  " + "".join(f"{h:<{w + 2}}" for h, w in zip(headers, widths)))
        for r in rows:
            cells = [(str(c) if c not in (None, "") else "-") for c in r]
            print("  " + "".join(f"{c:<{w + 2}}" for c, w in zip(cells, widths)))