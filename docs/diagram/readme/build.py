#!/usr/bin/env python3
"""Build the standalone API-testing HTML review draft from editable local sources."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
OUTPUT = PROJECT / "docs" / "api-testing-readme-preview.html"


def main():
    body = (HERE / "content.html").read_text(encoding="utf-8")
    css = (HERE / "reader.css").read_text(encoding="utf-8")
    geometry = (HERE / "rendered-line-geometry.js").read_text(encoding="utf-8")
    reader = (HERE / "reader.js").read_text(encoding="utf-8")
    document = f'''<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="HTML review draft: Thai explanation of the three ITCS386 WooCommerce API testing suites and 15 cases.">
  <title>API Testing · README Review Draft — ITCS386 Phase 2</title>
  <style>{css}</style>
</head>
<body>
  <div class="toolbar" role="toolbar" aria-label="Reader controls">
    <span class="toolbar-brand">API TESTING · REVIEW DRAFT</span>
    <button type="button" data-action="zoom-out" aria-label="Zoom out">−</button>
    <span class="zoom-readout" aria-live="polite">100%</span>
    <button type="button" data-action="zoom-in" aria-label="Zoom in">+</button>
    <button type="button" data-action="zoom-reset" aria-label="Reset zoom">Reset</button>
    <button type="button" class="theme-button" aria-pressed="false">☾ Dark</button>
    <span class="hint">⌘ + drag pan · Ctrl + wheel zoom</span>
  </div>
  <div class="viewer" tabindex="0" aria-label="Scrollable document. Use Command plus drag to pan, Control plus wheel to zoom.">
    <div class="scale-frame"><div class="stage"><div class="paper-wrap"><aside class="line-gutter" aria-hidden="true"></aside>{body}</div></div></div>
  </div>
  <div class="line-hint" aria-hidden="true"></div>
  <script>{geometry}</script>
  <script>{reader}</script>
</body>
</html>
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Built {OUTPUT} ({len(document.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
