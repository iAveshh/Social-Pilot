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

# Where a story lives is not what it is about. A model card hosted on Hugging
# Face is a story about the model; the platform is context and may appear as a
# small "hosted on" chip, never as the hero.
PLATFORMS = {
    'huggingface', 'github', 'gitlab', 'arxiv', 'medium', 'substack',
    'youtube', 'reddit', 'x', 'discord', 'npm', 'pypi', 'docker',
    'replicate', 'kaggle', 'notion',
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
            hits.append({'slug': slug, 'matched': term, 'rank': rank,
                         'role': 'platform' if slug in PLATFORMS else 'subject'})

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


def report(text):
    hits = sorted(find(text, available()), key=lambda h: h['rank'])
    subjects = [h for h in hits if h.get('slug') and h.get('role') == 'subject']
    platforms = [h for h in hits if h.get('role') == 'platform']
    out = {'hero': subjects[0] if subjects else None,
           'secondary': subjects[1:],
           'platform': platforms[0] if platforms else None,
           'unavailable': [h for h in hits if not h.get('slug')]}
    if not subjects:
        # The honest answer when the subject has no mark: set it as a wordmark.
        # Falling back to the host would put the wrong brand on a hero card.
        out['hero'] = None
        out['wordmark_required'] = True
        out['note'] = ('No mark for the story subject. Set the product name as an '
                       'Inter 800 wordmark in the hero lockup. Do NOT promote the '
                       'hosting platform to hero - it is where the story lives, '
                       'not what it is about.')
    return out


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:])
    if not text:
        sys.exit(__doc__)
    print(json.dumps(report(text), indent=1))
