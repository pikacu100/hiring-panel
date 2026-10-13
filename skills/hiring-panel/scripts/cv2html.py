#!/usr/bin/env python3
"""Render a hiring-panel CV Markdown file into a single-column, ATS-friendly A4 HTML page.

Usage:
    python cv2html.py <input.md> <output.html> <lang-code> "<page title>"

Supported Markdown subset (see SKILL.md, "CV Markdown format"):
    line 1   # NAME
    line 2   **Headline**
    line 3   contact line (emails, linkedin.com/..., github.com/..., https://... are auto-linked)
    ## SECTION
    **Job title** | Company | Location | MM/YYYY – present     (role header)
    *One-line italic description*
    - bullets, **bold**, *italic*, [label](https://url)

Standard library only. No tables or columns are produced, so ATS parsers read it in order.
"""
import html
import re
import sys
from urllib.parse import quote

CSS = """
@page { size: A4; margin: 14mm 16mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10.3pt;
       line-height: 1.38; color: #1d2430; margin: 0; background: #fff; }
.page { max-width: 178mm; margin: 0 auto; }
h1 { font-size: 22pt; letter-spacing: .5px; margin: 0; color: #12355b; }
.headline { font-size: 12pt; font-weight: 600; color: #2b5d8f; margin: 1px 0 3px; }
.contact { font-size: 9.6pt; color: #444; margin: 0 0 6px; }
a { color: #1f5ea8; text-decoration: none; }
h2 { font-size: 10.8pt; text-transform: uppercase; letter-spacing: .8px; color: #12355b;
     border-bottom: 1.4px solid #12355b; padding-bottom: 1px; margin: 10px 0 5px; }
p { margin: 0 0 4px; }
.job { margin: 6px 0 1px; }
.job b { color: #12355b; }
.tag { font-style: italic; color: #555; margin: 0 0 2px; }
ul { margin: 2px 0 4px; padding-left: 16px; }
li { margin: 1px 0; }
@media screen { body { padding: 24px 16px; } }
"""

BARE_URL = re.compile(
    r"(?<![\w/@.])(?:https?://[^\s·|,)<]+|(?:www\.)?(?:linkedin\.com|github\.com|gitlab\.com|behance\.net|dribbble\.com)/[^\s·|,)<]+)"
)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")


def _href(raw: str) -> str:
    url = raw if raw.startswith("http") else "https://" + raw
    return quote(url, safe="/:?=&.-_~%#+")


def inline(text: str) -> str:
    """Escape text, then apply [label](url) links, bare-URL and email autolinks, bold and italics."""
    links: list[tuple[str, str]] = []

    def stash(m: re.Match) -> str:
        links.append((m.group(1), m.group(2)))
        return f"\x00{len(links) - 1}\x00"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash, text)
    text = html.escape(text, quote=False)
    text = BARE_URL.sub(lambda m: f'<a href="{_href(m.group(0))}">{m.group(0)}</a>', text)
    text = EMAIL.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for i, (label, url) in enumerate(links):
        text = text.replace(f"\x00{i}\x00", f'<a href="{_href(url)}">{html.escape(label)}</a>')
    return text


def render(md: str, lang: str, title: str) -> str:
    out: list[str] = []
    in_list = False
    line_no = 0
    for line in md.splitlines():
        line = line.rstrip()
        if in_list and not line.startswith("- "):
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        line_no += 1
        if line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line_no == 2 and line.startswith("**"):
            out.append(f'<p class="headline">{inline(line.strip("*"))}</p>')
        elif line_no == 3:
            out.append(f'<p class="contact">{inline(line)}</p>')
        elif line.startswith("*") and not line.startswith("**"):
            out.append(f'<p class="tag">{inline(line.strip("*"))}</p>')
        elif line.startswith("**") and " | " in line:
            out.append(f'<p class="job">{inline(line)}</p>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    body = "\n".join(out)
    return (
        f'<!doctype html>\n<html lang="{html.escape(lang)}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n"
        f'<body><main class="page">\n{body}\n</main></body>\n</html>\n'
    )


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    src, dst, lang, title = sys.argv[1:5]
    with open(src, encoding="utf-8") as f:
        md = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(render(md, lang, title))
    sys.stdout.buffer.write(f"wrote {dst}\n".encode("utf-8"))


if __name__ == "__main__":
    main()
