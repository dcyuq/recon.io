from __future__ import annotations

from reconio import banner, clean, help as menu
from reconio.network import pscan


def clear() -> None:
    print("\033[2J\033[H", end="")


def _show(render) -> None:
    clear()
    banner.render()
    render()


_SECTIONS = {
    "1": "NETWORK", "network": "NETWORK",
    "2": "WEB", "web": "WEB",
    "3": "OSINT", "osint": "OSINT",
    "4": "TLS", "tls": "TLS",
}

_HANDLERS = {
    "pscan": pscan.run,
}


def run() -> int:
    while True:
        _show(menu.render)
        choice = input("  recon.io > ").strip().lower()
        if choice in ("exit", "quit", "q"):
            clear()
            return 0
        if choice in ("help", ""):
            continue
        if choice == "clean":
            clear()
            banner.render()
            clean.run()
            input("\n  enter to return")
            continue
        key = _SECTIONS.get(choice)
        if key:
            _section(key)
        else:
            input("  unknown option — enter to continue")


def _section(key: str) -> None:
    while True:
        _show(lambda: menu.render_section(key))
        raw = input(f"  recon.io/{key.lower()} > ").strip()
        low = raw.lower()
        if low in ("back", "b", "return", ""):
            return
        if low in ("exit", "quit", "q"):
            clear()
            raise SystemExit(0)
        parts = raw.split()
        cmd, rest = parts[0], parts[1:]
        handler = _HANDLERS.get(cmd)
        if not handler:
            input(f"  not available yet: {cmd} — enter to continue")
            continue
        if not rest:
            input(f"  usage: {cmd} <target> [flags] — enter to continue")
            continue
        clear()
        banner.render()
        handler(rest[0], rest[1:])
        input("\n  enter to return")