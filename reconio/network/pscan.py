from __future__ import annotations
import re
import xml.etree.ElementTree as ET

from reconio import flags, runner

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"

VERB = "pscan"
BIN = flags.BINARY[VERB]

_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$")
_HOST = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$")
_VALUE_FLAGS = {"-p", "--min-rate", "--max-rate", "-T", "--top-ports", "-iL"}
_DEFAULTS = ["-Pn", "--open"]


def _looks_like_target(tok: str) -> bool:
    return bool(_IP.match(tok) or _HOST.match(tok))


def _split(tokens: list[str]):
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


def _prompt_flags():
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


def _parse(xml_text: str):
    rows = []
    up = False
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return up, rows
    host = root.find("host")
    if host is None:
        return up, rows
    st = host.find("status")
    up = st is not None and st.get("state") == "up"
    for port in host.iterfind(".//port"):
        state = port.find("state")
        if state is None or state.get("state") != "open":
            continue
        svc = port.find("service")
        name = svc.get("name", "") if svc is not None else ""
        ver = ""
        if svc is not None:
            ver = " ".join(x for x in (svc.get("product"), svc.get("version")) if x)
        rows.append((port.get("portid"), port.get("protocol"), name, ver))
    return up, rows


def _render(target, up, rows):
    if _RICH:
        _console.print(f"  [bold {_ACCENT}]{target}[/]  " + ("up" if up else "down"))
        if not rows:
            _console.print("  [dim]no open ports[/]")
            return
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        t.add_column("PORT")
        t.add_column("PROTO")
        t.add_column("SERVICE")
        t.add_column("VERSION")
        for port, proto, name, ver in rows:
            t.add_row(port, proto, name, ver or "-")
        _console.print(t)
    else:
        print(f"  {target}  " + ("up" if up else "down"))
        if not rows:
            print("  no open ports")
            return
        print(f"  {'PORT':<7}{'PROTO':<7}{'SERVICE':<16}VERSION")
        for port, proto, name, ver in rows:
            print(f"  {port:<7}{proto:<7}{name:<16}{ver or '-'}")


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

    if not selected and not raw:
        selected = _prompt_flags()

    have = {f for f, _ in selected}
    for d in _DEFAULTS:
        if d not in have:
            selected.append((d, None))

    cmd = flags.preview(VERB, target, selected, binary=BIN)
    xml_cmd = cmd.replace(f" {target}", f" -oX - {target}", 1)
    code, out = runner.run_with_loader(xml_cmd, f"scanning {target}")

    up, rows = _parse(out)
    if not rows and "<?xml" not in out:
        print(out)
        return code
    _render(target, up, rows)
    return code