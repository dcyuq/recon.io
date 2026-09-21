from __future__ import annotations
import json

from reconio import flags, runner, target

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"

VERB = "probe"
BIN = flags.BINARY[VERB]

_VALUE_FLAGS = {"-p", "-timeout", "-t", "-mc", "-o"}
_DEFAULTS = ["-title", "-tech-detect", "-status-code", "-follow-redirects"]


def _split(tokens):
    tgt = None
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
        if tgt is None and target.looks_like_target(target.parse(tok)):
            tgt = tok
        i += 1
    return tgt, selected


def _prompt_flags():
    flags.menu(VERB)
    raw = input("  select numbers (e.g. 1,2,3): ").strip()
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
        url = d.get("url") or d.get("input") or ""
        status = str(d.get("status_code", ""))
        title = d.get("title", "") or ""
        tech = d.get("tech") or d.get("technologies") or []
        tech = ", ".join(tech) if isinstance(tech, list) else str(tech)
        rows.append((url, status, title, tech))
    return rows


def _render(rows):
    if not rows:
        print("  no live http services")
        return
    if _RICH:
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        t.add_column("URL")
        t.add_column("CODE")
        t.add_column("TITLE")
        t.add_column("TECH")
        for url, status, title, tech in rows:
            t.add_row(url, status, title or "-", tech or "-")
        _console.print(t)
    else:
        print(f"  {'URL':<34}{'CODE':<6}{'TITLE':<22}TECH")
        for url, status, title, tech in rows:
            print(f"  {url:<34}{status:<6}{(title or '-'):<22}{tech or '-'}")


def run(tgt: str, raw: list | None = None) -> int:
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1

    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, selected = _split(tokens)
    tgt = found or tgt

    if not target.looks_like_target(target.parse(tgt)):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1

    if not selected and not raw:
        selected = _prompt_flags()

    have = {f for f, _ in selected}
    for d in _DEFAULTS:
        if d not in have:
            selected.append((d, None))
    selected.append(("-json", None))
    selected.append(("-silent", None))

    flags.preview(VERB, tgt, selected, binary=BIN)
    parts = [BIN, "-u", tgt]
    for flag, value in selected:
        parts.append(flag)
        if value:
            parts.append(value)
    run_cmd = " ".join(parts)
    code, out = runner.run_with_loader(run_cmd, f"probing {tgt}")

    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    _render(rows)
    return code