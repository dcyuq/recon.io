from __future__ import annotations
import sys
 
from reconio.bootstrap import bootstrap
 
__version__ = "0.1.0"
 
 
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
 
    if argv and argv[0] in ("-v", "--version"):
        print(f"shard recon.io {__version__}")
        return 0
 
    bootstrap()
 
    from reconio import banner, help as menu, pscan
 
    if not argv or argv[0] in ("-h", "--help", "help"):
        banner.render()
        menu.render()
        return 0
 
    verb, rest = argv[0], argv[1:]
 
    if verb == "pscan":
        if not rest:
            print("usage: recon pscan <target> [flags]")
            return 1
        return pscan.run(rest[0], rest[1:])
 
    print(f"unknown command: {verb}")
    return 1
 
 
if __name__ == "__main__":
    sys.exit(main())
 