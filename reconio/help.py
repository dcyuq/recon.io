from __future__ import annotations

try:
    from rich.console import Console
    from rich.text import Text
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_WIDTH = 64
_ACCENT = "#00d7af"
_INTRO = "select a section or command · targets must be authorized"

_SECTIONS = [
    ("NETWORK", [
        ("pscan", "nmap", True),
        ("portscan", "masscan/naabu", False),
    ]),
    ("WEB", [
        ("probe", "httpx", True),
        ("fingerprint", "whatweb", False),
        ("fuzz", "ffuf", True),
        ("crawl", "katana", True),
    ]),
    ("OSINT", [
        ("whois", "whois", False),
        ("dns", "dnsx", False),
        ("subs", "subfinder", False),
        ("crt", "crt.sh", False),
    ]),
    ("TLS", [
        ("tls", "tlsx", False),
        ("ssl", "testssl.sh", False),
    ]),
]

_CORE = [
    ("target <url|ip|host>", "set the current target"),
    ("tools", "show installed tools"),
    ("clean", "uninstall tools + caches"),
    ("help", "show this menu"),
    ("exit", "quit"),
]


_NOTES = {
    "WEB": [
        "fuzz wordlist defaults to /usr/share/wordlists/dirb/common.txt",
        "override with -w <path>, e.g.:",
        "  /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt (big)",
        "  /usr/share/seclists/Discovery/Web-Content/common.txt (needs seclists)",
    ],
}


def section(key: str):
    for name, cmds in _SECTIONS:
        if name == key.upper():
            return name, cmds
    return None


def render() -> None:
    _render_rich() if _RICH else _render_plain()


def _render_rich() -> None:
    c = _console
    c.print(Text(_INTRO, style=f"dim {_ACCENT}"))
    c.print()
    for i, (name, cmds) in enumerate(_SECTIONS, 1):
        line = Text()
        line.append(f"  {i}. {name:<9}", style=f"bold {_ACCENT}")
        line.append("- ", style="dim")
        for j, (cmd, tool, built) in enumerate(cmds):
            if j:
                line.append(", ", style="dim")
            line.append(cmd, style="white" if built else "dim")
            line.append(f" ({tool})", style="dim")
            if not built:
                line.append(" ·soon", style="dim yellow")
        c.print(line)
    c.print()
    c.print(Text("  CORE", style=f"bold {_ACCENT}"))
    for cmd, desc in _CORE:
        row = Text()
        row.append(f"     {cmd:<22}", style="white")
        row.append(desc, style="dim")
        c.print(row)
    c.print("-" * _WIDTH, style="dim")


def _render_plain() -> None:
    print(_INTRO)
    print()
    for i, (name, cmds) in enumerate(_SECTIONS, 1):
        parts = []
        for cmd, tool, built in cmds:
            tag = "" if built else " ·soon"
            parts.append(f"{cmd} ({tool}){tag}")
        print(f"  {i}. {name:<9}- " + ", ".join(parts))
    print()
    print("  CORE")
    for cmd, desc in _CORE:
        print(f"     {cmd:<22}{desc}")
    print("-" * _WIDTH)


def render_section(key: str) -> None:
    sec = section(key)
    if not sec:
        return
    _section_rich(sec) if _RICH else _section_plain(sec)


def _section_rich(sec) -> None:
    name, cmds = sec
    c = _console
    c.print(Text(f"  {name}", style=f"bold {_ACCENT}"))
    c.print()
    for cmd, tool, built in cmds:
        row = Text()
        row.append(f"     {cmd:<14}", style="white" if built else "dim")
        row.append(f"{tool}", style="dim")
        if built:
            row.append(f"    usage: {cmd} <target> [flags]", style="dim")
        else:
            row.append("    ·soon", style="dim yellow")
        c.print(row)
    c.print()
    for note in _NOTES.get(name, []):
        c.print(Text(f"     note: {note}" if note == _NOTES.get(name, [""])[0] else f"           {note}", style="dim yellow"))
    c.print(Text("     back", style=f"bold {_ACCENT}"), Text("return to main", style="dim"))
    c.print("-" * _WIDTH, style="dim")


def _section_plain(sec) -> None:
    name, cmds = sec
    print(f"  {name}")
    print()
    for cmd, tool, built in cmds:
        if built:
            print(f"     {cmd:<14}{tool}    usage: {cmd} <target> [flags]")
        else:
            print(f"     {cmd:<14}{tool}    ·soon")
    print()
    for k, note in enumerate(_NOTES.get(name, [])):
        print(f"     note: {note}" if k == 0 else f"           {note}")
    print("     back           return to main")
    print("-" * _WIDTH)


if __name__ == "__main__":
    render()
    print()
    render_section("NETWORK")