# -*- coding: utf-8 -*-
"""Caption groups from word timings + a synthesised UI sound stem.

    python build-captions-and-sfx.py <project-slug> [narration-offset]

Captions: whisper word timestamps grouped into 2-3 word chunks so they read at
Reel speed instead of flashing one word at a time.

SFX: no sound-effects tool is wrapped in this repo, so the beats are voiced with
ffmpeg-synthesised UI tones. For a terminal aesthetic these beat real foley
anyway, and they cost nothing.
"""
import os, sys, json, subprocess
REPO = r'D:\Github Forks\Social-Pilot'
os.chdir(REPO); sys.path.insert(0, REPO)

slug = sys.argv[1] if len(sys.argv) > 1 else 'gemini-flash-reel'
PROJ = 'projects/' + slug.replace('projects/', '')
NARR_OFFSET = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4   # narration data-start

# ---------------------------------------------------------------- captions
tj = None
for cand in os.listdir(os.path.join(PROJ, 'artifacts')):
    if cand.endswith('.json') and 'transcri' in cand.lower():
        tj = os.path.join(PROJ, 'artifacts', cand)
if tj is None:
    from tools.tool_registry import registry
    registry.discover()
    r = registry._tools.get('transcriber').execute({
        'input_path': PROJ + '/assets/audio/narration.mp3',
        'model_size': 'base', 'language': 'en',
        'output_dir': PROJ + '/artifacts'})
    data = r.data
else:
    data = json.load(open(tj, encoding='utf-8'))

words = []
for seg in data.get('segments', []):
    for w in seg.get('words', []):
        t = w['word'].strip()
        if t:
            words.append((t, float(w['start']), float(w['end'])))

# Group into chunks of <=3 words, breaking on punctuation -- but never split a
# number away from the words that carry it. A naive break renders lines like
# "BUGS 2" / ".6" and "CLAUDE OPUS ON 4" / "OF 6 BENCHMARKS", which read as
# broken text on screen. So look at both boundaries before closing a chunk.
def bare_num(tok):
    return tok.strip('.,').replace(',', '').isdigit()


def opens_ok(tok):
    """A line may not start on a stray decimal, a lone digit or a symbol."""
    return tok[0].isalnum() and not (len(tok) <= 1 and tok.isdigit())


def closes_ok(tok):
    """A line may not end on a bare numeral unless punctuation closes it."""
    return tok.endswith(('.', ',', '?', '!')) or not bare_num(tok)


chunks, cur = [], []
for i, (t, s, e) in enumerate(words):
    cur.append((t, s, e))
    nxt = words[i + 1][0] if i + 1 < len(words) else None
    if (nxt is None or opens_ok(nxt)) and closes_ok(t) and \
       (len(cur) >= 3 or t.endswith(('.', ',', '?', '!'))):
        chunks.append(cur); cur = []
if cur:
    # a one- or two-word tail reads as an orphan; fold it into the previous line
    if chunks and len(cur) <= 2:
        chunks[-1] += cur
    else:
        chunks.append(cur)

# Whisper reliably mishears a few things. Correct them here rather than in the
# composition, so the burned captions match what the narrator actually said.
# Extend per story; spelled-out acronyms and compound words are the usual cases.
FIX = {'M I T': 'MIT', 'A P I': 'API', 'L L M': 'LLM', 'G P U': 'GPU',
       'WEIGHT LIST': 'WAITLIST', 'WAIT LIST': 'WAITLIST',
       'OPEN A I': 'OPENAI', 'CYBERVERSION': 'CYBER VERSION'}

caps = []
for c in chunks:
    text = ' '.join(w[0] for w in c).upper().replace(' %', '%').replace(' .', '.')
    for bad, good in FIX.items():
        text = text.replace(bad, good)
    start = c[0][1] + NARR_OFFSET
    end = c[-1][2] + NARR_OFFSET
    caps.append({'text': text, 'start': round(start, 2),
                 'dur': round(max(end - start, 0.35), 2)})
json.dump(caps, open(os.path.join(PROJ, 'artifacts', 'captions.json'), 'w',
                     encoding='utf-8'), indent=1)
print('captions:', len(caps), 'chunks, first 4:', caps[:4])

# ------------------------------------------------------------------- sfx
SFX_DIR = os.path.join(PROJ, 'assets', 'sfx')
os.makedirs(SFX_DIR, exist_ok=True)

def run(args):
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0:
        print('ffmpeg FAIL:', p.stderr.decode()[-400:])

def tone(name, freq, dur, gain=0.35, decay=None):
    """Short sine blip with a fast exponential decay - a UI tick."""
    decay = decay or dur
    run(['ffmpeg', '-y', '-f', 'lavfi', '-i',
         'sine=frequency=%d:duration=%.3f:sample_rate=48000' % (freq, dur),
         '-af', 'afade=t=out:st=0:d=%.3f:curve=exp,volume=%.3f' % (decay, gain),
         '-ac', '2', os.path.join(SFX_DIR, name)])

def thud(name, dur=0.45, gain=0.55):
    """Low body + noise transient - the rupture."""
    run(['ffmpeg', '-y',
         '-f', 'lavfi', '-i', 'sine=frequency=72:duration=%.3f:sample_rate=48000' % dur,
         '-f', 'lavfi', '-i', 'anoisesrc=d=%.3f:c=brown:r=48000:a=0.5' % dur,
         '-filter_complex',
         '[0:a]afade=t=out:st=0:d=%.3f:curve=exp[a];'
         '[1:a]lowpass=f=320,afade=t=out:st=0:d=0.10:curve=exp[b];'
         '[a][b]amix=inputs=2:duration=shortest,volume=%.3f' % (dur, gain),
         '-ac', '2', os.path.join(SFX_DIR, name)])

def sweep(name, dur=0.55, gain=0.22):
    """Filtered noise rising - a bar filling."""
    run(['ffmpeg', '-y', '-f', 'lavfi', '-i',
         'anoisesrc=d=%.3f:c=pink:r=48000:a=0.6' % dur,
         '-af', 'highpass=f=600,lowpass=f=5200,afade=t=in:st=0:d=%.3f,'
                'afade=t=out:st=%.3f:d=0.12,volume=%.3f' % (dur * 0.7, dur - 0.12, gain),
         '-ac', '2', os.path.join(SFX_DIR, name)])

tone('tick.wav', 1180, 0.075, gain=0.30)
tone('tick_hi.wav', 1560, 0.085, gain=0.34)
tone('blip.wav', 880, 0.11, gain=0.26)
thud('thud.wav')
sweep('sweep.wav')
tone('latch_a.wav', 420, 0.06, gain=0.40)
tone('latch_b.wav', 300, 0.09, gain=0.36)
print('sfx stems:', sorted(os.listdir(SFX_DIR)))

# --------------------------------------------------- mix stems onto a bed
CUES = [
    ('tick.wav', 1.50), ('tick.wav', 2.00), ('tick_hi.wav', 2.50),
    ('tick_hi.wav', 3.80), ('tick_hi.wav', 4.70),
    ('blip.wav', 6.30),
    ('thud.wav', 10.95),
    ('sweep.wav', 13.05), ('sweep.wav', 13.65),
    ('sweep.wav', 14.50), ('tick_hi.wav', 15.40),
    ('sweep.wav', 18.40), ('tick_hi.wav', 19.40),
    ('latch_a.wav', 23.05), ('latch_b.wav', 23.22),
]
TOTAL = 27.5
inputs, filters = [], []
for i, (stem, at) in enumerate(CUES):
    inputs += ['-i', os.path.join(SFX_DIR, stem)]
    filters.append('[%d:a]adelay=%d|%d[s%d]' % (i + 1, int(at * 1000), int(at * 1000), i))
mix = ''.join('[s%d]' % i for i in range(len(CUES)))
fc = ('anullsrc=r=48000:cl=stereo[base];' + ';'.join(filters) + ';' +
      '[base]' + mix + 'amix=inputs=%d:duration=first:normalize=0[out]' % (len(CUES) + 1))
run(['ffmpeg', '-y', '-f', 'lavfi', '-t', str(TOTAL), '-i',
     'anullsrc=r=48000:cl=stereo'] + inputs +
    ['-filter_complex', fc.replace('anullsrc=r=48000:cl=stereo[base];', '[0:a]acopy[base];'),
     '-map', '[out]', '-t', str(TOTAL),
     os.path.join(PROJ, 'assets', 'sfx', 'sfx_bed.mp3')])
print('sfx bed written')
