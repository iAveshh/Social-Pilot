"""Locate every visual beat against the words ACTUALLY spoken.

    python .claude/skills/engaging-explainer/scripts/find_beats.py <project-slug>

Reads  artifacts/narration_timing.json   (from `transcriber`)
       artifacts/beat_spec.json          (you write this — phrases to locate)
Writes artifacts/beats.json              (what the composition and linter read)

beat_spec.json is a plain phrase map. Write the phrase you EXPECT; this script
tells you what was actually said when it misses:

    {
      "acts":  {"act1": "so lets start at the beginning",
                "act2": "but here is what changed"},
      "beats": {"a1_gap":  "nobody could explain why",
                "a1_turn": "it was never the model"}
    }

Never hand-write a timestamp. A five-minute read drifts several seconds away
from any estimate, and every beat in the composition keys off these numbers.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def glue(raw: list[dict]) -> list[dict]:
    """Repair the two ways ASR word lists break phrase matching.

    Whisper writes numerals as digits and then splits them across tokens
    (' 24' + '.7' + '%'), and emits punctuation-only tokens that normalise to
    nothing. Both silently break a naive token match, and the failure looks like
    "the beat isn't in the script" rather than "the tokeniser split it".
    """
    out: list[dict] = []
    for w in raw:
        txt = w.get("word") or ""
        if not txt.strip():
            continue
        # a token with no leading space is a continuation of the previous one
        if out and not txt.startswith(" "):
            out[-1]["word"] += txt
            out[-1]["end"] = w.get("end", out[-1]["end"])
        else:
            out.append({"word": txt, "start": w.get("start"), "end": w.get("end")})
    return [w for w in out if w["start"] is not None and norm(w["word"])]


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    slug = argv[1]
    art = REPO / "projects" / slug / "artifacts"
    tl = json.loads((art / "narration_timing.json").read_text(encoding="utf-8"))
    spec_path = art / "beat_spec.json"
    if not spec_path.exists():
        print(f"error: write {spec_path} first (see this script's docstring)", file=sys.stderr)
        return 2
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    words = glue(tl.get("words") or [])
    keys = [norm(w["word"]) for w in words]
    if not keys:
        print("error: narration_timing.json has no usable word timestamps", file=sys.stderr)
        return 2

    def find(phrase: str):
        toks = [t for t in (norm(x) for x in phrase.split()) if t]
        n = len(toks)
        for i in range(len(keys) - n + 1):
            if keys[i:i + n] == toks:
                return round(words[i]["start"], 3), round(words[i + n - 1]["end"], 3)
        return None

    def context(phrase: str) -> str:
        """On a miss, show what was really said where the phrase starts to match.

        This is the whole difference between a two-minute fix and twenty minutes
        of dumping transcript segments by hand.
        """
        toks = [t for t in (norm(x) for x in phrase.split()) if t]
        for take in range(min(4, len(toks)), 0, -1):
            probe = toks[:take]
            for i in range(len(keys) - take + 1):
                if keys[i:i + take] == probe:
                    lo, hi = max(0, i - 2), min(len(words), i + len(toks) + 4)
                    said = " ".join(w["word"].strip() for w in words[lo:hi])
                    return f'matched {take}/{len(toks)} tokens at {words[i]["start"]:.2f}s — actually said: "{said}"'
        return "no prefix of this phrase appears anywhere in the read"

    out = {
        "duration_seconds": tl.get("duration_seconds"),
        "acts": {}, "beats": {}, "missing": [],
    }
    ok = True
    for group in ("acts", "beats"):
        print(f"--- {group.upper()} ---")
        for key, phrase in (spec.get(group) or {}).items():
            hit = find(phrase)
            if hit:
                entry = {"start": hit[0], "phrase": phrase}
                if group == "beats":
                    entry["end"] = hit[1]
                out[group][key] = entry
                print(f"  {key:16s} {hit[0]:8.2f}s")
            else:
                ok = False
                out["missing"].append(key)
                print(f"  {key:16s}  MISSING — {context(phrase)}")

    (art / "beats.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    total = len(out["acts"]) + len(out["beats"])
    print(f"\n{total} located, {len(out['missing'])} missing -> {art / 'beats.json'}")

    # the two structural facts worth knowing before the scene plan is written
    dur = out.get("duration_seconds") or 0
    turn = min((v["start"] for v in out["beats"].values() if v["start"] > 0.5), default=None)
    if turn is not None:
        print(f"earliest beat after 0.5s: {turn:.2f}s   (the TURN must land by 12.0s)")
    if dur:
        print(f"peak window for this runtime: {dur * 0.66:.1f}s – {dur * 0.86:.1f}s")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
