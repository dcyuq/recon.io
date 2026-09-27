# recon.io

A Linux Python CLI reconnaissance orchestrator. It wraps standard recon tools behind one consistent interface, one target, one flag menu, so you run each tool individually and get clean, parsed output instead of raw dumps.

© made by dycuq

## Scope

Strictly for CTF events, authorized engagements, and isolated lab testing. You are responsible for staying in scope. Do not point it at systems you do not own or have written permission to test.

## What it is

recon.io does not reimplement scanners. It orchestrates them:

- one target set once, reused across every command
- each tool runs on its own (no forced full chain, since steps like nmap take time)
- a preset flag menu per tool, or raw flag passthrough
- a command preview that shows the real command line and explains each flag before running
- a loading screen while a tool runs, then a clean parsed table
- an interactive paged menu with the banner pinned on every page
- a bootstrapper that auto-installs missing Python deps and tools on first run

Tools are branded under recon.io verbs (for example, `pscan` runs nmap underneath).

## Requirements

- Linux or WSL (bootstrap uses apt, gem, and go)
- Python 3.10+
- sudo access for tool install

Python deps: rich, dnspython, jinja2, requests.

## Install

```bash
git clone https://github.com/dcyuq/recon.io
cd recon.io
python3 main.py
```

On first run the bootstrapper checks for missing Python deps and external tools, installs them (apt for system tools, gem for whatweb, go install for the ProjectDiscovery tools), shows an init screen, confirms, then clears. It asks for sudo once. It also verifies the ProjectDiscovery tools are the real ones (not a name clash) and reinstalls if needed.

## Usage

```bash
python3 main.py            # interactive menu
python3 main.py --help     # banner + menu
python3 main.py --version
python3 main.py pscan <target> [flags]   # one-shot from shell
```

Inside the menu: type a section name or number to open it, run a tool, then `back` to return. Set a target once with `target`, then run tools without retyping it.

```
target 192.168.1.2
network
pscan -p- -sV -sC
```

Every command previews the real command line, explains each flag, shows a loading screen, then prints a parsed table.

## Sections and tools

| Section | Verb | Tool | Does |
|---|---|---|---|
| NETWORK | `pscan` | nmap | port + service scan, parsed port table |
| NETWORK | `portscan` | naabu | fast port sweep |
| WEB | `probe` | httpx | probe live http, title, tech, status |
| WEB | `fingerprint` | whatweb | tech stack detection |
| WEB | `fuzz` | ffuf | directory / content brute-force |
| WEB | `crawl` | katana | crawl for urls and endpoints |
| OSINT | `whois` | whois | registrar, dates, name servers |
| OSINT | `dns` | dnsx | resolve A / CNAME / MX records |
| OSINT | `subs` | subfinder | subdomain enumeration |
| OSINT | `crt` | crt.sh | subdomains from certificate transparency |
| OSINT | `sherlock` | sherlock | hunt a username across sites |
| TLS | `tls` | tlsx | certificate info (CN, issuer, expiry) |
| TLS | `ssl` | testssl.sh | deep TLS / cipher audit (raw output) |

## Core commands

| Command | Does |
|---|---|
| `target <url\|ip\|host>` | set the current target (parsed, resolved, reachability-checked) |
| `tools` | show installed tools |
| `clean` | uninstall tools + caches (with confirm) |
| `help` | show the menu |
| `exit` | quit |

## Targets

`target` accepts a URL, IP, hostname, or `localhost`. It strips the scheme, port, and path down to the host, resolves it, and checks reachability. Tools reuse the stored target, or you can pass one inline on any command. `sherlock` is the exception, it takes a username, not a host.

## Notes

- `fuzz` defaults to `/usr/share/wordlists/dirb/common.txt`. Override with `-w <path>` (e.g. the dirbuster medium list, or seclists). Add `-e .php,.txt` for extensions.
- `probe` supports `-raw` to dump full httpx output instead of the parsed table.
- Tools not yet installed will say so; the bootstrapper handles installation on launch.

## Project layout

```
recon.io/
├── main.py              entry point, flag + verb dispatch
├── requirements.txt
└── reconio/
    ├── banner.py        ascii banner
    ├── help.py          sectioned menu
    ├── cli.py           interactive page loop
    ├── bootstrap.py     auto-installer
    ├── runner.py        shared executor + loading screen
    ├── flags.py         flag registry + preview
    ├── common.py        shared split / prompt / table helpers
    ├── target.py        url/ip/host parser + resolve + reachability
    ├── clean.py         uninstaller
    ├── network/         pscan, portscan
    ├── web/             probe, fingerprint, fuzz, crawl
    ├── osint/           whois, dns, subs, crt, sherlock
    └── tls/             tls, ssl
```

## License

MIT