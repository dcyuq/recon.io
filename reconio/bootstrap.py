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
 
APT = {
    "nmap": "nmap",
    "masscan": "masscan",
    "whatweb": "whatweb",
    "whois": "whois",
    "dig": "dnsutils",
    "ffuf": "ffuf",
    "gobuster": "gobuster",
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
    print ("\033[2J\033[H", end="")  # ANSI escape code to clear the screen

def add_go_bin():
    p = os.path.expanduser("~/.go/bin")
    if p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

def has(tool): 
    return shutil.which(tool) is not None   

def _pip_missing():
    out = []
    for m in PIP:
        name = "dns" if m == "dnspython" else m
        if importlib.util.find_spec(name) is None:
            out.append(m)
        return out

def _tools_missing():
    add_go_bin()
    return [t for t in list(APT) + list(GO) if not has(t)]

def run(cmd):
    return subprocess.run(
        cmd, shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0

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
        line(m)
        ok = run(f"{sys.executable} -m pip install -q {m}")
        fail.append(m) if not ok else None
        line(m, True, ok)
 
    if any(t in GO for t in tools) and not has("go"):
        line("golang toolchain")
        line("golang toolchain", True, ensure_go())
        add_go_bin()
 
    if tools:
        run("sudo apt-get update -qq")
 
    for t in tools:
        line(t)
        ok = run(f"sudo apt-get install -y {APT[t]}") if t in APT else run(f"go install -v {GO[t]}")
        fail.append(t) if not ok else None
        line(t, True, ok)
 
    time.sleep(0.4)
    confirm(fail)
    return not fail
 



