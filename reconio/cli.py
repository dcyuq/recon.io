from __future__ import annotations

from reconio import banner, clean, help as menu, target
from reconio.network import pscan


def clear() -> None:
    print("\033[2J\033[H", end="")


def _show(render) -> None:
    clear()
    banner.render()
    cur = target.get()
    if cur:
        who = cur.ip or cur.host
        tag = "reachable" if cur.reachable else "no response"
        print(f"  target: {who} ({cur.host}) [{tag}]")
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


def _set_target(args) -> None:
    if not args:
        input("  usage: target <url|ip|host> — enter to continue")
        return
    t = target.set_target(args[0])
    if not t.ip:
        input(f"  could not resolve {t.host} — enter to continue")
    else:
        tag = "reachable" if t.reachable else "no response (may be filtered)"
        input(f"  target set: {t.ip} ({t.host}) [{tag}] — enter to continue")


def run() -> int:
    while True:
        _show(menu.render)
        choice = input("  recon.io > ").strip().lower()
        first = choice.split()[0] if choice else ""
        if choice in ("exit", "quit", "q"):
            clear()
            return 0
        if choice in ("help", ""):
            continue
        if first == "target":
            _set_target(choice.split()[1:])
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
        if cmd == "target":
            _set_target(rest)
            continue
        handler = _HANDLERS.get(cmd)
        if not handler:
            input(f"  not available yet: {cmd} — enter to continue")
            continue
        tokens = list(rest)
        if not any(target.looks_like_target(t) for t in tokens):
            cur = target.get()
            if cur and (cur.ip or cur.host):
                tokens.append(cur.ip or cur.host)
        if not tokens:
            input(f"  no target — set one or pass it: {cmd} <target> [flags]")
            continue
        clear()
        banner.render()
        handler(tokens[0], tokens[1:])
        input("\n  enter to return")