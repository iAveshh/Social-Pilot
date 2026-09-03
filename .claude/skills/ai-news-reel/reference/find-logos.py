# -*- coding: utf-8 -*-
"""Find the brand marks a story is actually about.

    python find-logos.py "Introducing Gemini 3.8 Flash and 3.8 Flash Cyber" [more text...]

Matches the story's own words against the installed simple-icons set and prints
the slugs, hero first. The hero is the brand named in the title -- that mark
belongs on screen in the opening beat, not buried mid-video.

Requires: npm install simple-icons@16 --no-save
"""
import io, json, os, re, sys

BASE = os.path.join('node_modules', 'simple-icons', 'icons')

# multi-word brands whose slug isn't a plain lowercase of the words
ALIASES = {
    'gemini': 'googlegemini', 'google gemini': 'googlegemini',
    'chatgpt': None, 'openai': None,          # removed from simple-icons
    'microsoft': None, 'copilot': 'githubcopilot',
    'github copilot': 'githubcopilot', 'claude': 'claude',
    'anthropic': 'anthropic', 'hugging face': 'huggingface',
    'deepmind': 'googlegemini', 'android studio': 'androidstudio',
    'google cloud': 'googlecloud', 'chrome': 'googlechrome',
    'vs code': 'vscode', 'visual studio code': 'vscode',
}

def available():
    if not os.path.isdir(BASE):
        sys.exit('simple-icons not installed: npm install simple-icons@16 --no-save')
    return {f[:-4] for f in os.listdir(BASE) if f.endswith('.svg')}


def find(text, have):
    words = re.findall(r"[A-Za-z][A-Za-z0-9+.\- ]{1,24}", text)
    hits, seen = [], set()

    def add(slug, term, rank):
        if slug and slug in have and slug not in seen:
            seen.add(slug)
            hits.append({'slug': slug, 'matched': term, 'rank': rank})

    # explicit aliases first - they carry the cases a naive slug misses
    low = text.lower()
    for term, slug in ALIASES.items():
        if term in low:
            if slug is None:
                hits.append({'slug': None, 'matched': term, 'rank': 99,
                             'note': 'not in simple-icons - use press-kit SVG or an Inter 800 wordmark'})
                seen.add(term)
            else:
                add(slug, term, low.index(term))
    # then bare single tokens
    for w in words:
        t = w.strip().lower()
        for cand in (t.replace(' ', ''), t.split()[0] if t.split() else ''):
            add(cand, t, low.find(t) if t in low else 999)
    return hits


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:])
    if not text:
        sys.exit(__doc__)
    hits = sorted(find(text, available()), key=lambda h: h['rank'])
    print(json.dumps({'hero': next((h for h in hits if h['slug']), None),
                      'all': hits}, indent=1))
