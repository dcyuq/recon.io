from __future__ import annotations
import html
import json
import time
from datetime import datetime, timezone
from pathlib import Path

_OUT = Path("output")
_ACCENT = "#00d7af"


class Session:
    def __init__(self):
        self.target = None
        self.started = time.time()
        self.results = []

    def set_target(self, tgt):
        self.target = tgt

    def record(self, tool, section, headers, rows, meta=None):
        self.results.append({
            "tool": tool,
            "section": section,
            "headers": list(headers),
            "rows": [list(r) for r in rows],
            "meta": meta or {},
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })

    def _slug(self):
        base = self.target or "session"
        return "".join(c if c.isalnum() or c in ".-_" else "_" for c in base)

    def _dir(self):
        d = _OUT / self._slug()
        d.mkdir(parents=True, exist_ok=True)
        return d

    def as_dict(self):
        return {
            "target": self.target,
            "started": datetime.fromtimestamp(self.started, timezone.utc).isoformat(timespec="seconds"),
            "duration_sec": round(time.time() - self.started, 1),
            "results": self.results,
        }

    def write_json(self):
        if not self.results:
            return None
        path = self._dir() / "report.json"
        path.write_text(json.dumps(self.as_dict(), indent=2), encoding="utf-8")
        return path

    def write_html(self):
        if not self.results:
            return None
        path = self._dir() / "report.html"
        path.write_text(_html(self.as_dict()), encoding="utf-8")
        return path

    def flush(self):
        j = self.write_json()
        h = self.write_html()
        return j, h


SESSION = Session()


def set_target(tgt):
    SESSION.set_target(tgt)


def record(tool, section, headers, rows, meta=None):
    SESSION.record(tool, section, headers, rows, meta)


def flush():
    return SESSION.flush()


def _esc(v):
    return html.escape(str(v)) if v not in (None, "") else "-"


def _block(entry):
    head = "".join(f"<th>{_esc(h)}</th>" for h in entry["headers"])
    body = ""
    for r in entry["rows"]:
        cells = "".join(f"<td>{_esc(c)}</td>" for c in r)
        body += f"<tr>{cells}</tr>"
    if not entry["rows"]:
        body = f'<tr><td colspan="{max(len(entry["headers"]),1)}" class="empty">no results</td></tr>'
    return (
        f'<section><h2>{_esc(entry["tool"])} '
        f'<span class="tag">{_esc(entry["section"])}</span></h2>'
        f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></section>'
    )


def _html(data):
    blocks = "".join(_block(e) for e in data["results"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>recon.io report — {_esc(data["target"])}</title>
<style>
:root{{color-scheme:dark;--a:{_ACCENT}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:2rem 1rem;background:#0b0f0e;color:#d7e0dc;font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}}
.wrap{{max-width:920px;margin:0 auto}}
h1{{color:var(--a);font-size:1.4rem;margin:0 0 .2rem;letter-spacing:.05em}}
.meta{{color:#6c7b76;margin-bottom:2rem;font-size:.85rem}}
.byline{{color:#6c7b76;margin-top:3rem;text-align:center;font-size:.8rem}}
section{{margin-bottom:2rem;border:1px solid #1c2621;border-radius:8px;overflow:hidden}}
h2{{margin:0;padding:.7rem 1rem;background:#111815;font-size:1rem;color:#e6efe9;font-weight:600}}
.tag{{color:var(--a);font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;margin-left:.5rem}}
table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:.5rem 1rem;border-top:1px solid #1c2621;vertical-align:top;word-break:break-all}}
th{{color:var(--a);font-size:.75rem;text-transform:uppercase;letter-spacing:.08em}}
tbody tr:hover{{background:#0f1512}}
.empty{{color:#6c7b76;font-style:italic}}
</style></head>
<body><div class="wrap">
<h1>recon.io</h1>
<div class="meta">target <b>{_esc(data["target"])}</b> · {len(data["results"])} runs · {_esc(data["started"])} · {data["duration_sec"]}s</div>
{blocks}
<div class="byline">© made by dycuq</div>
</div></body></html>"""