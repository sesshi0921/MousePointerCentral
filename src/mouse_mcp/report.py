from __future__ import annotations

import html
from pathlib import Path


def generate_report(output_dir: str | Path, timestamp: str, log: list[dict]) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    for i, row in enumerate(log, start=1):
        action = row.get("action", {})
        rows.append(
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{row.get('t', 0):.3f}</td>"
            f"<td>{html.escape(str(action.get('type', '')))}</td>"
            f"<td><pre>{html.escape(str(action))}</pre></td>"
            "</tr>"
        )
    body = "".join(rows)
    content = f"""<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><title>Mouse Automation Report</title></head><body>
  <h1>実行レポート {html.escape(timestamp)}</h1>
  <video src=\"recording.mp4\" controls width=\"800\"></video>
  <table>
    <tr><th>#</th><th>t(s)</th><th>type</th><th>詳細</th></tr>
    {body}
  </table>
</body></html>
"""
    target = out_dir / "report.html"
    target.write_text(content, encoding="utf-8")
    return target
