from __future__ import annotations

try:
    from rich.console import Console
    from rich.text import Text
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"
_WIDTH = 58


FLAGS = {
    "pscan": [
        ("-sV", None, "service / version detection"),
        ("-sC", None, "run default NSE scripts"),
        ("-A", None, "aggressive: os, version, scripts, traceroute"),
        ("-O", None, "os detection"),
        ("-Pn", None, "skip host discovery, treat as online"),
        ("-sS", None, "syn stealth scan (needs root)"),
        ("-T4", None, "faster timing template"),
        ("-p", "ports", "ports to scan (e.g. 80,443 or - for all)"),
    ],
    "probe": [
        ("-title", None, "show page title"),
        ("-tech-detect", None, "fingerprint technologies"),
        ("-status-code", None, "show status code"),
        ("-follow-redirects", None, "follow redirects"),
        ("-p", "ports", "ports to probe (e.g. 80,443,8080)"),
    ],
    "crawl": [
        ("-d", "depth", "crawl depth (default 3)"),
        ("-jc", None, "crawl javascript files"),
        ("-kf", None, "known files (robots, sitemap)"),
    ],
    "fuzz": [
        ("-w", "wordlist", "wordlist path (default dirb/common.txt)"),
        ("-mc", "codes", "match status codes (e.g. 200,301)"),
        ("-fc", "codes", "filter out status codes (e.g. 404)"),
        ("-e", "exts", "extensions (e.g. .php,.txt)"),
        ("-ac", None, "auto-calibrate filtering"),
    ],
}

BINARY = {
    "pscan": "nmap",
    "probe": "httpx",
    "crawl": "katana",
    "fuzz": "ffuf",
}


def _line(text: str, style: str = "") -> None:
    if _RICH:
        _console.print(Text(text, style=style))
    else:
        print(text)


def menu(tool: str) -> None:
    specs = FLAGS.get(tool)
    if not specs:
        _line(f"no preset flags for {tool}")
        return
    _line(f"{tool} flags", f"bold {_ACCENT}")
    for i, (flag, arg, desc) in enumerate(specs, 1):
        label = f"{flag} <{arg}>" if arg else flag
        if _RICH:
            row = Text()
            row.append(f"  {i:>2}. ", style="dim")
            row.append(f"{label:<20}", style=_ACCENT)
            row.append(desc, style="white")
            _console.print(row)
        else:
            print(f"  {i:>2}. {label:<20}{desc}")
    _line("-" * _WIDTH, "dim")


def _desc(tool: str, flag: str) -> str:
    for f, _arg, desc in FLAGS.get(tool, []):
        if f == flag:
            return desc
    return ""


def cmdline(binary: str, target: str, selected: list[tuple[str, str | None]]) -> str:
    parts = [binary]
    for flag, value in selected:
        parts.append(flag)
        if value:
            parts.append(value)
    parts.append(target)
    return " ".join(parts)


def preview(tool: str, target: str, selected: list[tuple[str, str | None]], binary: str | None = None) -> str:
    binary = binary or tool
    cmd = cmdline(binary, target, selected)
    _line("command", f"bold {_ACCENT}")
    _line(f"  {cmd}", "white")
    if selected:
        _line("flags", f"bold {_ACCENT}")
        for flag, value in selected:
            shown = f"{flag} {value}" if value else flag
            desc = _desc(tool, flag) or "passthrough flag"
            if _RICH:
                row = Text()
                row.append(f"  {shown:<20}", style=_ACCENT)
                row.append(desc, style="white")
                _console.print(row)
            else:
                print(f"  {shown:<20}{desc}")
    _line("-" * _WIDTH, "dim")
    return cmd