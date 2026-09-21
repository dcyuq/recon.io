from __future__ import annotations

try:
    from rich.console import Console
    from rich.text import Text
    _RICH = True
except ImportError:
    _RICH = False

_WIDTH = 58
_ACCENT = "#00d7af"
_INTRO = "type a command to begin · targets must be authorized"

_COMMANDS = [
    ("target <url|ip|host>", "set the current target"),
    ("pscan <target>", "port + service scan"),
    ("results", "show / export findings"),
    ("tools", "show installed tools"),
    ("help", "show this menu"),
    ("exit", "quit"),
]


def render() -> None:
    if _RICH:
        _render_rich()
    else:
        _render_plain()


def _render_rich() -> None:
    console = Console()
    console.print(Text(_INTRO, style=f"dim {_ACCENT}"))
    console.print(Text("commands", style=f"bold {_ACCENT}"))
    for name, desc in _COMMANDS:
        row = Text()
        row.append(f"  {name:<24}", style=_ACCENT)
        row.append(desc, style="white")
        console.print(row)
    console.print("-" * _WIDTH, style="dim")


def _render_plain() -> None:
    print(_INTRO)
    print("commands")
    for name, desc in _COMMANDS:
        print(f"  {name:<24}{desc}")
    print("-" * _WIDTH)