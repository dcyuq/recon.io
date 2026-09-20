from __future__ import annotations

try:
    from rich.console import Console
    from rich.text import Text
    _RICH = True
except ImportError:
    _RICH = False


_ART_LINES = ['██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗   ██╗ ██████╗', '██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║   ██║██╔═══██╗', '██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║   ██║██║   ██║', '██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║   ██║██║   ██║', '██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██╗██║╚██████╔╝', '╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝ ╚═════╝']

_BYLINE = "© made by dycuq @ 2026"
_TAGLINE = "recon orchestrator · ctf & authorized labs only"
_WIDTH = 58
_GRADIENT = ['#00d7ff', '#00d7d7', '#00d7af', '#00d787', '#00d75f', '#00d700']


def render() -> None:
    if _RICH:
        _render_rich()
    else:
        _render_plain()


def _render_rich() -> None:
    console = Console()
    art = Text()
    for i, line in enumerate(_ART_LINES):
        art.append(line + "\n", style=f"bold {_GRADIENT[i % len(_GRADIENT)]}")
    console.print(art)
    console.print(Text(_BYLINE, style="dim italic"))
    console.print(Text(_TAGLINE, style="dim"))
    console.print("-" * _WIDTH, style="dim")


def _render_plain() -> None:
    print("\n".join(_ART_LINES))
    print(_BYLINE)
    print(_TAGLINE)
    print("-" * _WIDTH)


if __name__ == "__main__":
    render()