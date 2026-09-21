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

VERB = "crawl"
BIN = flags.BINARY[VERB]

_VALUE_FLAGS = {"-d", "-c", "-timeout", "-kf"}
_DEFAULTS = []


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
    raw = input("  select numbers (e.g. 1,2): ").strip()
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
        req = d.get("request", {})
        url = req.get("endpoint") or d.get("endpoint") or ""
        resp = d.get("response", {})
        status = str(resp.get("status_code", "") or "")
        ctype = resp.get("content_type") or resp.get("headers", {}).get("content_type", "") or ""
        ctype = ctype.split(";")[0]
        rows.append((url, status, ctype))
    return rows


def _render(rows):
    if not rows:
        print("  no urls found")
        return
    if _RICH:
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        t.add_column("URL")
        t.add_column("STATUS")
        t.add_column("TYPE")
        for url, status, ctype in rows:
            t.add_row(url, status or "-", ctype or "-")
        _console.print(t)
    else:
        print(f"  {'URL':<48}{'STATUS':<8}TYPE")
        for url, status, ctype in rows:
            print(f"  {url:<48}{(status or '-'):<8}{ctype or '-'}")


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

    flags.preview(VERB, tgt, selected, binary=BIN)
    parts = [BIN, "-u", tgt]
    for flag, value in selected:
        parts.append(flag)
        if flag == "-kf" and not value:
            value = "all"
        if value:
            parts.append(value)
    parts += ["-jsonl", "-silent"]
    code, out = runner.run_with_loader(" ".join(parts), f"crawling {tgt}")

    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    _render(rows)
    return code