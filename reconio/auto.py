from __future__ import annotations

from reconio import runner, target, report, flags
from reconio.network import pscan
from reconio.web import probe, fingerprint
from reconio.tls import tls

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False

_console = Console() if _RICH else None
_ACCENT = "#00d7af"

VERB = "auto"

_CHAIN = {
    "http": ["probe", "fingerprint"],
    "https": ["probe", "fingerprint", "tls"],
    "http-proxy": ["probe", "fingerprint"],
    "http-alt": ["probe", "fingerprint"],
}

_PORT_HINT = {
    21: ("ftp", "check anon login (USER anonymous), grab banner, look for writable dirs"),
    22: ("ssh", "note version for known CVEs, try key/user enum, weak creds only if in scope"),
    23: ("telnet", "cleartext auth, capture banner, try default creds"),
    25: ("smtp", "VRFY/EXPN/RCPT user enum, check open relay"),
    53: ("dns", "attempt AXFR zone transfer, run dns + subs for records"),
    69: ("tftp", "no auth, try grabbing config files by name"),
    80: ("http", "auto-chained probe/fingerprint; run fuzz + crawl for dirs and endpoints"),
    88: ("kerberos", "AS-REP roast (GetNPUsers), enumerate users, kerberoast SPNs"),
    110: ("pop3", "cleartext creds, banner grab"),
    111: ("rpcbind", "rpcinfo -p, look for NFS exports"),
    135: ("msrpc", "rpcdump, map endpoints, coercion primitives if AD"),
    139: ("netbios", "null session, nbtscan, enum shares"),
    143: ("imap", "banner, cleartext creds"),
    161: ("snmp", "snmpwalk with public/private community strings"),
    389: ("ldap", "anonymous bind ldapsearch, dump users, feed BloodHound"),
    443: ("https", "auto-chained probe/fingerprint/tls; also run fuzz + crawl"),
    445: ("smb", "null session shares (nxc smb -u '' -p ''), signing check, vuln scan"),
    636: ("ldaps", "ldapsearch over TLS, cert info via tls"),
    1433: ("mssql", "try sa/weak creds, xp_cmdshell if authed"),
    2049: ("nfs", "showmount -e, mount exports, check no_root_squash"),
    3306: ("mysql", "banner, weak root creds, version CVEs"),
    3389: ("rdp", "NLA check, version for BlueKeep-era CVEs, no brute unless scoped"),
    5432: ("postgres", "default postgres creds, version enum"),
    5900: ("vnc", "no-auth check, weak password"),
    5985: ("winrm", "auth with found creds (evil-winrm), part of AD lateral path"),
    6379: ("redis", "unauth access, INFO, config get dir for RCE paths"),
    8080: ("http-alt", "auto-chained probe/fingerprint; run fuzz + crawl"),
    8443: ("https-alt", "auto-chained probe/fingerprint/tls; run fuzz"),
    9200: ("elastic", "unauth _cat/indices, dump data"),
    27017: ("mongodb", "unauth connect, list dbs"),
}


def _open_ports():
    for entry in reversed(report.SESSION.results):
        if entry["tool"] == "pscan":
            out = []
            for row in entry["rows"]:
                port = row[0]
                svc = row[2] if len(row) > 2 else ""
                if str(port).isdigit():
                    out.append((int(port), svc))
            return out
    return []


def _suggest(ports):
    rows = []
    chained = []
    for port, svc in ports:
        name, hint = _PORT_HINT.get(port, (svc or "unknown", "manual review, grab banner and version"))
        tools = _CHAIN.get(svc) or _CHAIN.get(name) or []
        rows.append((str(port), name, ", ".join(tools) or "-", hint))
        for t in tools:
            if (t, port) not in [(c[0], c[1]) for c in chained]:
                chained.append((t, port))
    return rows, chained


def _render(rows):
    if _RICH:
        _console.print(f"  [bold {_ACCENT}]suggested next steps[/]")
        t = Table(show_edge=False, header_style=f"bold {_ACCENT}", pad_edge=False)
        t.add_column("PORT")
        t.add_column("SERVICE")
        t.add_column("AUTO-RUN")
        t.add_column("SUGGESTION")
        for port, name, tools, hint in rows:
            t.add_row(port, name, tools, hint)
        _console.print(t)
    else:
        print("  suggested next steps")
        print(f"  {'PORT':<7}{'SERVICE':<12}{'AUTO-RUN':<22}SUGGESTION")
        for port, name, tools, hint in rows:
            print(f"  {port:<7}{name:<12}{tools:<22}{hint}")


def run(tgt, raw=None):
    host = target.parse(tgt)
    if not target.looks_like_target(host):
        print(f"  no valid target found in: {tgt}")
        return 1
    if not runner.available(pscan.BIN):
        print(f"{pscan.BIN} not found — install it first")
        return 1

    print(f"  auto scan on {host} — starting with a service scan")
    scan_flags = list(raw) if raw else ["-sV"]
    pscan.run(host, scan_flags)

    ports = _open_ports()
    if not ports:
        print("  no open ports found, nothing to chain")
        return 0

    rows, chained = _suggest(ports)
    _render(rows)
    report.record(VERB, "network", ["PORT", "SERVICE", "AUTO-RUN", "SUGGESTION"], rows)

    if not chained:
        print("\n  no wrapped tools to auto-run for these ports, see suggestions above")
        return 0

    print(f"\n  auto-running {len(chained)} follow-up(s)")
    _HANDLERS = {"probe": probe.run, "fingerprint": fingerprint.run, "tls": tls.run}
    done = set()
    for name, port in chained:
        if name in done:
            continue
        done.add(name)
        handler = _HANDLERS.get(name)
        if not handler:
            continue
        print(f"\n  > {name} on {host}")
        handler(host)
    return 0