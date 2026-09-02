"""Extract official brand marks from simple-icons into inline SVG cells.

    npm install simple-icons@16 --no-save
    python extract-logos.py anthropic googlegemini huggingface cursor ollama langchain

Copies paths programmatically — hand-transcribing truncates long paths and
renders a broken glyph. Prints markup ready to paste into #logo-grid.
NOTE: openai and microsoft are absent from simple-icons (removed at the
companies' request) — use their official press-kit SVG or a wordmark instead.
"""
import os, re, sys

BASE = os.path.join("node_modules", "simple-icons", "icons")

def cell(slug, index):
    path = os.path.join(BASE, slug + ".svg")
    if not os.path.exists(path):
        sys.exit("no mark for %r in simple-icons — use an official press-kit SVG "
                 "or a wordmark treatment instead" % slug)
    svg = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", svg).group(1)
    paths = "".join('<path d="%s"/>' % d for d in re.findall(r'<path d="(.*?)"', svg))
    return ('<div class="logo-cell" id="lg%d" title="%s">'
            '<svg viewBox="0 0 24 24">%s</svg></div>' % (index, title, paths))

if __name__ == "__main__":
    slugs = sys.argv[1:]
    if not slugs:
        sys.exit(__doc__)
    for i, s in enumerate(slugs, 1):
        print(cell(s, i))
