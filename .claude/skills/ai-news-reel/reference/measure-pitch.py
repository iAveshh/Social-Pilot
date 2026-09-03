# -*- coding: utf-8 -*-
"""Measure pitch variation - the actual definition of a monotone read.

Autocorrelation F0 per 40ms frame, reported in semitones so the numbers are
perceptual. A flat read sits under ~2 semitones of variation; lively speech
runs 3-5+.
"""
import subprocess, wave, os, math, contextlib, sys
import numpy as np

BASE = os.environ.get('NARRATION_DIR', '.')
VARIANTS = sys.argv[1:]  # basenames (no .mp3) inside NARRATION_DIR
SR = 16000

def load(mp3):
    wav = mp3.replace('.mp3', '.p.wav')
    subprocess.run(['ffmpeg', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wav],
                   capture_output=True)
    with contextlib.closing(wave.open(wav)) as w:
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    os.remove(wav)
    return d / 32768.0

def f0_track(x):
    win = int(0.040 * SR)                 # 40 ms
    hop = int(0.020 * SR)
    lo, hi = int(SR / 300.0), int(SR / 70.0)   # 70-300 Hz male speech
    out = []
    for i in range(0, len(x) - win, hop):
        fr = x[i:i+win]
        if math.sqrt(float(np.mean(fr * fr))) < 0.02:
            continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, 'full')[win-1:]
        if ac[0] <= 0:
            continue
        seg = ac[lo:hi]
        if len(seg) == 0:
            continue
        lag = int(np.argmax(seg)) + lo
        if ac[lag] / ac[0] < 0.3:         # unvoiced / unreliable
            continue
        out.append(SR / float(lag))
    return np.array(out)

print('%-16s %8s %9s %9s %8s' % ('variant', 'medHz', 'semi_std', 'semi_p10-90', 'frames'))
print('-' * 56)
for v in VARIANTS:
    f0 = f0_track(load(os.path.join(BASE, v + '.mp3')))
    if len(f0) < 20:
        print('%-16s  (too few voiced frames)' % v); continue
    semi = 12 * np.log2(f0 / np.median(f0))
    semi = semi[np.abs(semi) < 12]        # drop octave errors
    print('%-16s %8.1f %9.2f %9.2f %8d' % (
        v, float(np.median(f0)), float(semi.std()),
        float(np.percentile(semi, 90) - np.percentile(semi, 10)), len(f0)))
