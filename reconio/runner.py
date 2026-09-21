from __future__ import annotations
import shutil
import subprocess
 
try:
    from rich.console import Console
    _RICH = True
except ImportError:
    _RICH = False
 
_console = Console() if _RICH else None
_ACCENT = "#00d7af"
 
 
def available(binary: str) -> bool:
    return shutil.which(binary) is not None
 
 
def run_with_loader(cmd: str, label: str) -> tuple[int, str]:
    if _RICH:
        with _console.status(f"[{_ACCENT}]{label}[/]", spinner="dots"):
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        print(f"{label} ...")
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).rstrip()
 