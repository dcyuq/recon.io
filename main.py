from __future__ import annotations
import argparse
import sys

from reconio import banner

__version__ = "0.1.0"

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="recon.io", add_help=False)
    p.add_argument("target", nargs="?")
    p.add_argument("-h", "--help", action="store_true",)
    p.add_argument("-v", "--version", action="store_true",)
    return p


def main(argv: list[str]| None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(f"recon.io {__version__}")
        return 0

    if args.help or args.target is None: 
        banner.render()
        help.render()
        return 0

    banner.render()

if __name__ == "__main__":
    sys.exit(main())