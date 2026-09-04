"""Build burned-caption cues from the measured read, and an .srt for publishing.

    python .claude/skills/engaging-explainer/scripts/build_captions.py <slug> [--max-chars 54]

Reads  artifacts/narration_timing.json
Writes artifacts/captions.json   (cue list — feed into the composition props)
       renders/<slug>.srt        (for the publish bundle)

Chunk SENTENCE-FIRST, then at clause boundaries, and only then on length.

A plain word-count cap looks reasonable and reads badly: it splits mid-clause
("the only thing that / differs is the safeguards") and strands two-word tails
on their own line. Both are more distracting than no captions at all, which
matters because captions are already a redundancy cost you are paying
deliberately for muted viewing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]

MIN_TAIL_WORDS = 3          # never strand a shorter tail on its own cue
CLAUSE_MIN_RATIO = 0.5      # only break on a clause once the cue has some body


def glue(raw: list[dict]) -> list[dict]:
    """Rejoin ASR tokens split mid-numeral (' 24' + '.7'); drop empty tokens."""
    out: list[dict] = []
    for w in raw:
        txt = w.get("word") or ""
        if not txt.strip():
            continue
        if out and not txt.startswith(" "):
            out[-1]["word"] += txt
            out[-1]["end"] = w.get("end", out[-1]["end"])
        else:
            out.append({"word": txt, "start": w.get("start"), "end": w.get("end")})
    return [w for w in out if w["start"] is not None]


def split_sentence(run: list[dict], max_chars: int) -> list[list[dict]]:
    text_of = lambda ws: " ".join(w["word"].strip() for w in ws)
    if len(text_of(run)) <= max_chars:
        return [run]
    pieces: list[list[dict]] = []
    part: list[dict] = []
    for w in run:
        part.append(w)
        body = text_of(part)
        if re.search(r"[,;:—]$", w["word"].strip()) and len(body) >= max_chars * CLAUSE_MIN_RATIO:
            pieces.append(part); part = []
        elif len(body) >= max_chars:
            pieces.append(part); part = []
    if part:
        if pieces and len(part) < MIN_TAIL_WORDS:
            pieces[-1].extend(part)
        else:
            pieces.append(part)
    return pieces


def timestamp(x: float) -> str:
    h, rem = divmod(x, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--max-chars", type=int, default=54)
    args = ap.parse_args()

    proj = REPO / "projects" / args.slug
    art = proj / "artifacts"
    tl = json.loads((art / "narration_timing.json").read_text(encoding="utf-8"))
    words = glue(tl.get("words") or [])
    if not words:
        print("error: no word timestamps in narration_timing.json", file=sys.stderr)
        return 2

    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.!?]["”]?$', w["word"].strip()):
            sentences.append(cur); cur = []
    if cur:
        sentences.append(cur)

    cues = []
    for sent in sentences:
        for piece in split_sentence(sent, args.max_chars):
            if piece:
                cues.append({
                    "start": round(piece[0]["start"], 3),
                    "end": round(piece[-1]["end"], 3),
                    "text": " ".join(w["word"].strip() for w in piece).strip(),
                })

    (art / "captions.json").write_text(json.dumps(cues, indent=2), encoding="utf-8")
    srt = proj / "renders" / f"{args.slug}.srt"
    srt.parent.mkdir(parents=True, exist_ok=True)
    srt.write_text("\n".join(
        f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n"
        for i, c in enumerate(cues, 1)), encoding="utf-8")

    longest = max(cues, key=lambda c: len(c["text"]))
    fewest = min(cues, key=lambda c: len(c["text"].split()))
    print(f"{len(cues)} cues -> artifacts/captions.json, renders/{args.slug}.srt")
    print(f"  longest  {len(longest['text']):3d} chars : {longest['text']!r}")
    print(f"  shortest {len(fewest['text'].split()):3d} words : {fewest['text']!r}")
    if len(fewest["text"].split()) < MIN_TAIL_WORDS:
        print("  WARNING: an orphaned tail survived — check the sentence above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
