from __future__ import annotations
import importlib.util
import os
import shutil
import subprocess
import sys
import time

_ACCENT = "\033[38;2;0;215;175m"
_R = "\033[0m"
_DIM = "\033[2m"
_GRN = "\033[92m"
_RED = "\033[91m"
_YEL = "\033[93m"

PIP = ["rich", "dnspython", "jinja2", "requests"]

SYSTEM_DEPS = ["build-essential", "libpcap-dev", "ruby"]

APT = {
    "nmap": "nmap",
    "masscan": "masscan",
    "whois": "whois",
    "dig": "dnsutils",
    "ffuf": "ffuf",
    "gobuster": "gobuster",
}

GEM = {
    "whatweb": "whatweb",
}

GO = {
    "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "dnsx": "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "naabu": "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "httpx": "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "katana": "github.com/projectdiscovery/katana/cmd/katana@latest",
    "nuclei": "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
}


def clear():
    print("\033[2J\033[H", end="")


def add_go_bin():
    p = os.path.expanduser("~/go/bin")
    if p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")


def persist_go_bin():
    rc = os.path.expanduser("~/.bashrc")
    line = 'export PATH="$HOME/go/bin:$PATH"'
    try:
        if os.path.exists(rc):
            with open(rc) as f:
                if line in f.read():
                    return
        with open(rc, "a") as f:
            f.write(f"\n{line}\n")
    except OSError:
        pass


def has(tool):
    return shutil.which(tool) is not None


def run(cmd):
    return subprocess.run(
        cmd, shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def _pip_missing():
    out = []
    for m in PIP:
        name = "dns" if m == "dnspython" else m
        if importlib.util.find_spec(name) is None:
            out.append(m)
    return out


def _tools_missing():
    add_go_bin()
    return [t for t in list(APT) + list(GEM) + list(GO) if not has(t)]


def ensure_go():
    return has("go") or run("sudo apt-get install -y golang-go")


def init_screen(n):
    clear()
    print(f"{_ACCENT}  recon.io — initializing{_R}")
    print(f"{_DIM}  preparing environment for first run{_R}\n")
    print(f"{_DIM}  {n} item(s) missing — installing...{_R}\n")


def line(msg, done=False, ok=False):
    if not done:
        print(f"  {_YEL}...{_R} {msg}", end="", flush=True)
    else:
        mark = f"{_GRN}ok{_R}" if ok else f"{_RED}x{_R}"
        print(f"\r  [{mark}] {msg}{' ' * 24}")


def _do(msg, cmd):
    line(msg)
    ok = run(cmd)
    line(msg, True, ok)
    return ok


def confirm(fail):
    print()
    if not fail:
        print(f"{_GRN}  environment ready — all set{_R}")
    else:
        print(f"{_YEL}  ready with warnings — install manually:{_R}")
        print(f"{_DIM}    {', '.join(fail)}{_R}")
    print(f"{_DIM}  © made by dycuq{_R}")
    time.sleep(1.6)
    clear()


def bootstrap():
    pip = _pip_missing()
    tools = _tools_missing()
    if not pip and not tools:
        return True

    init_screen(len(pip) + len(tools))
    fail = []

    for m in pip:
        if not _do(m, f"{sys.executable} -m pip install -q {m}"):
            fail.append(m)

    need_apt = any(t in APT for t in tools)
    need_gem = any(t in GEM for t in tools)
    need_go = any(t in GO for t in tools)

    if tools:
        run("sudo apt-get update -qq")

    if need_go or need_gem or need_apt:
        for dep in SYSTEM_DEPS:
            _do(f"dep: {dep}", f"sudo apt-get install -y {dep}")

    if need_go and not has("go"):
        line("golang toolchain")
        line("golang toolchain", True, ensure_go())
        add_go_bin()

    for t in tools:
        if t in APT:
            ok = _do(t, f"sudo apt-get install -y {APT[t]}")
        elif t in GEM:
            ok = _do(t, f"sudo gem install {GEM[t]}")
        else:
            ok = _do(t, f"go install -v {GO[t]}")
        if not ok:
            fail.append(t)

    if need_go:
        add_go_bin()
        persist_go_bin()

    verify_fail = [t for t in tools if t not in fail and not has(t)]
    for t in verify_fail:
        fail.append(t)

    time.sleep(0.4)
    confirm(fail)
    return not fail