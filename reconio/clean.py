from __future__ import annotations
import os
import shutil
import subprocess

from reconio.bootstrap import APT, GEM, GO

try:
    from rich.console import Console
    from rich.text import Text
    _RICH = True
except ImportError:
    _RICH = False

_c = Console() if _RICH else None
_ACCENT = "#00d7af"


def _has(tool):
    return shutil.which(tool) is not None


def _go_bin(tool):
    p = os.path.expanduser(f"~/go/bin/{tool}")
    return p if os.path.exists(p) else None


def _run(cmd):
    return subprocess.run(cmd, shell=True).returncode == 0


def _plan():
    go_tools = [t for t in GO if _go_bin(t)]
    gem_tools = [t for t in GEM if _has(t)]
    apt_tools = [t for t in APT if _has(t)]
    return go_tools, gem_tools, apt_tools


def _line(text, style=""):
    if _RICH:
        _c.print(Text(text, style=style))
    else:
        print(text)


def run(_target=None, _flags=None) -> int:
    go_tools, gem_tools, apt_tools = _plan()

    _line("  full uninstall — the following will be removed:", f"bold {_ACCENT}")
    _line(f"    go tools    {', '.join(go_tools) or '-'}")
    _line(f"    gem tools   {', '.join(gem_tools) or '-'}")
    _line(f"    apt tools   {', '.join(apt_tools) or '-'}")
    _line("    caches      go build + module cache (~/go)")
    _line("    outputs     output/ and results/ folders")
    print()

    ans = input("  confirm full uninstall? [y/N] ").strip().lower()
    if ans not in ("y", "yes"):
        _line("  cancelled")
        return 0

    for t in go_tools:
        p = _go_bin(t)
        if p:
            try:
                os.remove(p)
            except OSError:
                pass

    if gem_tools:
        _run(f"sudo gem uninstall -x -a {' '.join(gem_tools)}")

    if apt_tools:
        _run(f"sudo apt-get remove -y {' '.join(APT[t] for t in apt_tools)}")

    _run("go clean -cache -modcache")

    for d in ("output", "results"):
        shutil.rmtree(d, ignore_errors=True)

    _line("  done — recon.io tools and caches removed", f"bold {_ACCENT}")
    return 0