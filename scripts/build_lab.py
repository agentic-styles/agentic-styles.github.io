"""Build the architecture teaching module from editable source and Markdown.

Only build(output_root) writes generated HTML; no runtime agent implementation is
included. The output is a relocatable `lab/` sibling of `atlas/` and `course/`.
"""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "architecture-lab"
DOCS = ROOT / "docs" / "architecture-lab"

DOCUMENT_STYLE = """
:root{color-scheme:light;background:#f4f0e7;color:#172331;font-family:system-ui,sans-serif}
body{max-width:76ch;margin:0 auto;padding:2rem 1.4rem 5rem;line-height:1.8}
h1,h2,h3{font-family:Georgia,serif;line-height:1.25;margin-top:2rem}
a{color:#1c6e67;text-underline-offset:.2em}nav{display:flex;gap:1rem;flex-wrap:wrap;border-bottom:1px solid #c8c4bb;padding-bottom:1rem}
pre{overflow:auto;padding:1rem;background:#e9e4da}code{font-family:ui-monospace,monospace;font-size:.92em}
li{margin:.4rem 0}blockquote{border-left:3px solid #1c6e67;padding-left:1rem;margin-left:0}
@media print{nav{display:none}body{max-width:none;padding:0}}
"""


def inline(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)

    def link(match: re.Match[str]) -> str:
        label, target = match.groups()
        url = urlsplit(target)
        if not url.scheme and not url.netloc and url.path.endswith(".md"):
            target = urlunsplit((url.scheme, url.netloc, url.path[:-3] + ".html", url.query, url.fragment))
        return f'<a href="{target}">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value)


def markdown_to_html(markdown: str) -> str:
    """Render the deliberately small Markdown subset used by this module."""
    blocks: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    code: list[str] | None = None

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            blocks.append(f"</{list_type}>")
            list_type = None

    for line in markdown.splitlines():
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if code is None:
                code = []
            else:
                blocks.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        item = re.match(r"^(?:([-*])|\d+\.)\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading[1])
            blocks.append(f"<h{level}>" + inline(heading[2]) + f"</h{level}>")
        elif item:
            flush_paragraph()
            kind = "ul" if item[1] else "ol"
            if list_type != kind:
                close_list()
                blocks.append(f"<{kind}>")
                list_type = kind
            blocks.append("<li>" + inline(item[2]) + "</li>")
        else:
            close_list()
            paragraph.append(line)
    flush_paragraph()
    close_list()
    if code is not None:
        raise ValueError("Unclosed fenced code block")
    return "\n".join(blocks)


def page(title: str, content: str) -> str:
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Agentic Architecture Lab</title><style>{DOCUMENT_STYLE}</style></head>
<body><nav aria-label="课程导航"><a href="../atlas/">Pattern 图鉴</a><a href="../course/">Pattern 基础课</a><a href="index.html">实验课首页</a><a href="presentation.html">Slides</a><a href="tutorial.html">学习教程</a><a href="https://github.com/agentic-styles/labs/tree/v0.1.0/booking-precheck">实验工程 v0.1.0</a></nav>
<main>{content}</main></body></html>'''


def build(output_root: Path) -> Path:
    destination = Path(output_root) / "lab"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / "presentation.html.in", destination / "presentation.html")
    for name in ["styles.css", "slides.js", "deck.js"]:
        shutil.copy2(SOURCE / name, destination / name)
    for filename in ["README.md", "tutorial.md", "outline.md", "provenance.md"]:
        text = (DOCS / filename).read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ")
        target = "index.html" if filename == "README.md" else Path(filename).with_suffix(".html").name
        (destination / target).write_text(page(title, markdown_to_html(text)), encoding="utf-8")
    return destination


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=ROOT / "dist")
    args = parser.parse_args()
    print(build(args.output))
