from __future__ import annotations
import json
import os

from reconio import flags, runner, target

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"

VERB = "fuzz"
BIN = flags.BINARY[VERB]

_DEFAULT_WORDLIST = "/usr/share/wordlists/dirb/common.txt"
_VALUE_FLAGS = {"-w", "-mc", "-fc", "-e", "-t", "-p"}


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


def _fuzz_url(tgt: str) -> str:
    if "FUZZ" in tgt:
        return tgt
    if tgt.startswith("http://") or tgt.startswith("https://"):
        return tgt.rstrip("/") + "/FUZZ"
    return f"http://{tgt}/FUZZ"


def _parse(out):
    rows = []
    try:
        data = json.loads(out)
        for r in data.get("results", []):
            rows.append((r.get("url", ""), str(r.get("status", "")), str(r.get("length", ""))))
        return rows
    except json.JSONDecodeError:
        pass
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        rows.append((r.get("url", ""), str(r.get("status", "")), str(r.get("length", ""))))
    return rows


def _render(rows):
    if not rows:
        print("  no paths found")
        return
    if _RICH:
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        t.add_column("URL")
        t.add_column("STATUS")
        t.add_column("SIZE")
        for url, status, size in rows:
            t.add_row(url, status or "-", size or "-")
        _console.print(t)
    else:
        print(f"  {'URL':<48}{'STATUS':<8}SIZE")
        for url, status, size in rows:
            print(f"  {url:<48}{(status or '-'):<8}{size or '-'}")


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

    has_w = any(f == "-w" for f, _ in selected)
    if not has_w:
        if not os.path.exists(_DEFAULT_WORDLIST):
            print(f"  default wordlist not found: {_DEFAULT_WORDLIST}")
            print("  pass one with -w <path>")
            return 1
        selected.append(("-w", _DEFAULT_WORDLIST))

    url = _fuzz_url(tgt)
    flags.preview(VERB, url, selected, binary=BIN)
    parts = [BIN, "-u", url]
    for flag, value in selected:
        parts.append(flag)
        if value:
            parts.append(value)
    parts += ["-json", "-s"]
    code, out = runner.run_with_loader(" ".join(parts), f"fuzzing {url}")

    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    _render(rows)
    return code