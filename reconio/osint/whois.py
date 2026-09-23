from __future__ import annotations

from reconio import common, flags, runner, target

VERB = "whois"
BIN = flags.BINARY[VERB]
_FIELDS = [
    ("registrar", "Registrar"),
    ("creation", "Creation Date"),
    ("expiry", "Registry Expiry"),
    ("expiry2", "Expiration Date"),
    ("updated", "Updated Date"),
    ("ns", "Name Server"),
]


def _parse(out):
    rows = []
    seen = set()
    for line in out.splitlines():
        low = line.lower()
        for _key, label in _FIELDS:
            if low.strip().startswith(label.lower()) and ":" in line:
                val = line.split(":", 1)[1].strip()
                if val and (label, val) not in seen:
                    seen.add((label, val))
                    rows.append((label, val))
    return rows


def run(tgt, raw=None):
    if not runner.available(BIN):
        print(f"{BIN} not found — install it first")
        return 1
    tokens = ([tgt] + list(raw)) if raw else [tgt]
    found, _ = common.split(tokens, set())
    tgt = found or tgt
    host = target.parse(tgt)
    if not target.looks_like_target(host):
        print(f"  no valid target found in: {' '.join(tokens)}")
        return 1
    code, out = runner.run_with_loader(f"{BIN} {host}", f"whois {host}")
    rows = _parse(out)
    if not rows and out.strip():
        print(out)
        return code
    common.table(["FIELD", "VALUE"], rows, "no whois data")
    return code