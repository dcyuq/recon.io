from __future__ import annotations
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

_IP = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_HOST = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$")
_PROBE_PORTS = (80, 443, 22, 445, 3389)


@dataclass
class Target:
    raw: str
    host: str
    ip: str | None
    reachable: bool


_current: Target | None = None


_SINGLE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")


def looks_like_target(tok: str) -> bool:
    if tok == "localhost":
        return True
    return bool(_IP.match(tok) or _HOST.match(tok) or _SINGLE.match(tok))


def parse(raw: str) -> str:
    s = raw.strip()
    if "://" in s:
        p = urlparse(s)
        s = p.netloc or p.path
    s = s.split("/")[0]
    if ":" in s and not s.count(":") > 1:
        s = s.split(":")[0]
    return s


def resolve(host: str) -> str | None:
    if _IP.match(host):
        return host
    try:
        return socket.gethostbyname(host)
    except OSError:
        return None


def reachable(ip: str) -> bool:
    for port in _PROBE_PORTS:
        try:
            with socket.create_connection((ip, port), timeout=1):
                return True
        except OSError:
            continue
    return False


def set_target(raw: str) -> Target:
    global _current
    host = parse(raw)
    ip = resolve(host)
    ok = reachable(ip) if ip else False
    _current = Target(raw=raw, host=host, ip=ip, reachable=ok)
    return _current


def get() -> Target | None:
    return _current