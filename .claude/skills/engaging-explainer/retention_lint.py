"""Retention linter — the pre-render engagement gate.

Checks a project's script + scene_plan + beats against the measured engagement
rules in reference/engagement-model.md. Run it at the scene_plan gate, BEFORE
the assets stage spends anything.

    python .claude/skills/engaging-explainer/retention_lint.py <project-slug>
    python .claude/skills/engaging-explainer/retention_lint.py <slug> --json

Exit codes:  0 = clean (warnings allowed)   1 = one or more ERRORs   2 = bad input

The linter is only as good as the scene_plan's declarations. Each scene should
carry:

    "attention_event": "onset" | "cessation" | "freeze" | "none"
    "still_window":    true | false      # frame is static: safe to reveal detail
    "peak":            true | false      # exactly one scene in the piece
    "display_text":    ["ON-SCREEN TEXT", ...]

Missing fields degrade to WARN rather than silently passing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# --- thresholds, from reference/engagement-model.md -------------------------
COLD_OPEN_S = 3.0          # something must HAPPEN by here
TURN_BY_S = 12.0           # the premise must break by here
VELOCITY_WINDOW_S = 30.0   # the first-30s cliff — this one IS from the research
# NOTE: the gap figure below is a synthesis heuristic, not a measured constant.
# The literature establishes that the first 30s decides retention; it does not
# specify a change interval. 3.0s is a defensible working value — tight enough to
# prevent a dead open, loose enough to allow a deliberate beat after a strong
# event. Do not pad a video with invented events to satisfy it.
VELOCITY_MAX_GAP_S = 3.0
INTERRUPT_EARLY_S = 20.0   # cadence for the first 3 minutes
INTERRUPT_LATE_S = 40.0    # cadence after
EARLY_PHASE_S = 180.0
PEAK_LO, PEAK_HI = 0.66, 0.86   # peak position as a fraction of runtime
END_BEAT_S = 8.0           # the closing statement gets at least this
REDUNDANCY_NGRAM = 4       # shared word runs of this length are redundant
REDUNDANCY_WINDOW_S = 2.0


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, level: str, check: str, msg: str, fix: str = "") -> None:
        self.items.append({"level": level, "check": check, "message": msg, "fix": fix})

    error = lambda self, c, m, f="": self.add("ERROR", c, m, f)      # noqa: E731
    warn = lambda self, c, m, f="": self.add("WARN", c, m, f)        # noqa: E731
    ok = lambda self, c, m: self.add("OK", c, m)                     # noqa: E731

    @property
    def errors(self) -> int:
        return sum(1 for i in self.items if i["level"] == "ERROR")

    @property
    def warns(self) -> int:
        return sum(1 for i in self.items if i["level"] == "WARN")


def _words(s: str) -> list[str]:
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).split() if w]


def _ngrams(ws: list[str], n: int) -> set[tuple]:
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def check_cold_open(scenes, rep):
    """Something must HAPPEN by 0:03 — not merely be established."""
    first = scenes[0]
    ev = first.get("attention_event")
    if ev is None:
        rep.warn("cold_open", "Scene 1 does not declare attention_event — cannot verify the open.",
                 'Add "attention_event": "onset" to the first scene.')
        return
    if ev == "none":
        rep.error("cold_open", "Scene 1 has no attention event. The first 3 seconds decide retention.",
                  "Start motion in the first 3s: something arrives, moves, or breaks.")
        return
    if first["start_seconds"] > COLD_OPEN_S:
        rep.error("cold_open", f"First scene starts at {first['start_seconds']:.1f}s.",
                  "The open must be immediate.")
        return
    rep.ok("cold_open", f"Attention event '{ev}' at 0.0s.")


def check_turn(scenes, rep):
    """The premise must break by 0:12 — the most common structural failure."""
    turns = [s for s in scenes
             if s.get("attention_event") in ("onset", "cessation", "freeze")
             and s["start_seconds"] > 0.5]
    if not turns:
        rep.warn("turn_timing", "No turn found (no scene after 0.5s declares an attention event).")
        return
    t = turns[0]["start_seconds"]
    if t > TURN_BY_S:
        rep.error("turn_timing",
                  f"First turn lands at {t:.1f}s — the premise must break by {TURN_BY_S:.0f}s.",
                  "Move the reversal earlier. No amount of visual polish recovers a slow open.")
    else:
        rep.ok("turn_timing", f"Turn at {t:.1f}s.")


def check_velocity(scenes, beats, rep):
    """Frame must change measurably every ~2s through the first 30s."""
    events = sorted({s["start_seconds"] for s in scenes if s["start_seconds"] <= VELOCITY_WINDOW_S}
                    | {v for v in beats.values() if v <= VELOCITY_WINDOW_S})
    events = [0.0] + [e for e in events if e > 0.0] + [VELOCITY_WINDOW_S]
    gaps = [(a, b) for a, b in zip(events, events[1:]) if b - a > VELOCITY_MAX_GAP_S]
    if gaps:
        worst = max(gaps, key=lambda g: g[1] - g[0])
        rep.error("visual_velocity",
                  f"{len(gaps)} static gap(s) in the first {VELOCITY_WINDOW_S:.0f}s; "
                  f"worst is {worst[1] - worst[0]:.1f}s at {worst[0]:.1f}s.",
                  f"Add a visual event so nothing exceeds {VELOCITY_MAX_GAP_S:.1f}s early on.")
    else:
        rep.ok("visual_velocity", f"No gap over {VELOCITY_MAX_GAP_S:.1f}s in the first 30s.")


def check_interrupts(scenes, rep):
    """Progressive rhythm: 10-20s early, widening to 25-40s."""
    bad = []
    for a, b in zip(scenes, scenes[1:]):
        gap = b["start_seconds"] - a["start_seconds"]
        limit = INTERRUPT_EARLY_S if a["start_seconds"] < EARLY_PHASE_S else INTERRUPT_LATE_S
        if gap > limit:
            bad.append((a["id"], a["start_seconds"], gap, limit))
    if bad:
        for sid, at, gap, limit in bad:
            rep.error("interrupt_cadence",
                      f"{sid} holds {gap:.1f}s at {at:.1f}s (limit {limit:.0f}s).",
                      "Split the scene or add a vantage/scale/freeze interrupt.")
    else:
        rep.ok("interrupt_cadence", "All scene intervals within the progressive-rhythm limits.")


def check_same_subject_runs(scenes, rep):
    """A scene change is not an interrupt if the visual subject is unchanged."""
    runs, cur, start = [], None, 0
    for i, s in enumerate(scenes):
        subj = (s.get("required_assets") or [{}])[0].get("description", "")[:40]
        if subj != cur:
            if cur is not None and i - start >= 4:
                runs.append((scenes[start]["id"], i - start))
            cur, start = subj, i
    if cur is not None and len(scenes) - start >= 4:
        runs.append((scenes[start]["id"], len(scenes) - start))
    for sid, n in runs:
        rep.warn("subject_variety",
                 f"{n} consecutive scenes share a primary visual subject (from {sid}).",
                 "Consecutive scenes on one subject are ONE interrupt, not several.")
    if not runs:
        rep.ok("subject_variety", "No run of 4+ scenes on a single visual subject.")


def check_attention_events_are_qualitative(scenes, rep):
    """Ramps do not capture attention; onsets, cessations and freezes do."""
    declared = [s for s in scenes if "attention_event" in s]
    if not declared:
        rep.warn("qualitative_events", "No scene declares attention_event — cannot verify.")
        return
    freezes = [s for s in scenes if s.get("attention_event") == "freeze"]
    if not freezes:
        rep.warn("qualitative_events",
                 "No freeze anywhere in the piece.",
                 "Cessation of motion captures attention as strongly as onset, and costs nothing. "
                 "Freeze at act boundaries and at the peak.")
    else:
        rep.ok("qualitative_events", f"{len(freezes)} freeze event(s) declared.")


def check_still_windows(scenes, rep):
    """Detail revealed during motion is literally not perceived (motion silencing)."""
    if not any("still_window" in s for s in scenes):
        rep.warn("motion_silencing", "No scene declares still_window — check not performed.",
                 'Add "still_window": true/false so figure reveals can be verified.')
        return
    offenders = []
    for s in scenes:
        if "still_window" not in s:
            continue
        texts = s.get("display_text") or []
        has_figure = any(re.search(r"\d", t or "") for t in texts)
        if has_figure and s.get("still_window") is False:
            offenders.append(s["id"])
    if offenders:
        rep.error("motion_silencing",
                  f"Numeric display text lands during motion in: {', '.join(offenders)}.",
                  "Land figures only in a declared still_window — feature changes on moving "
                  "objects are not perceived.")
    else:
        rep.ok("motion_silencing", "No figures land during declared motion.")


def check_redundancy(scenes, script, rep):
    """Mayer redundancy, d=0.87 — the largest measured harm available."""
    sections = script.get("sections", [])
    if not sections:
        rep.warn("redundancy", "No script sections — cannot check display/narration overlap.")
        return
    if not any(s.get("display_text") for s in scenes):
        rep.warn("redundancy", "No scene declares display_text — check not performed.",
                 'Add "display_text": [...] listing on-screen text so the largest measured '
                 "harm in multimedia design (d=0.87) can actually be checked.")
        return

    # This check reads sec['text'] and sec['start_seconds']/['end_seconds']. Without
    # them `spoken` is empty for every scene past the first couple of seconds, the
    # comparison matches nothing, and the check reports OK while having examined
    # NOTHING. That is worse than no check, so it is an ERROR rather than a pass.
    # Enrich script.json with the measured read before linting — see
    # reference/production-pipeline.md §3.
    usable = [s for s in sections
              if _words(s.get("text", "")) and
              (s.get("start_seconds") is not None or s.get("end_seconds") is not None)]
    if not usable:
        rep.error("redundancy",
                  "Script sections carry no 'text' plus 'start_seconds'/'end_seconds', so this "
                  "check can compare nothing and would pass vacuously.",
                  "Write the measured narration timings and plain text onto each script "
                  "section before linting. Until then the LARGEST measured harm in the "
                  "model (d=0.87) is unchecked.")
        return

    compared = 0
    hits = []
    for s in scenes:
        texts = [t for t in (s.get("display_text") or []) if t]
        if not texts:
            continue
        lo = s["start_seconds"] - REDUNDANCY_WINDOW_S
        hi = s["end_seconds"] + REDUNDANCY_WINDOW_S
        spoken: list[str] = []
        for sec in sections:
            if sec.get("end_seconds", 0) >= lo and sec.get("start_seconds", 0) <= hi:
                spoken += _words(sec.get("text", ""))
        if len(spoken) < REDUNDANCY_NGRAM:
            continue
        compared += 1
        spoken_ng = _ngrams(spoken, REDUNDANCY_NGRAM)
        for t in texts:
            shared = _ngrams(_words(t), REDUNDANCY_NGRAM) & spoken_ng
            if shared:
                hits.append((s["id"], t[:48], " ".join(next(iter(shared)))))
    if hits:
        for sid, text, phrase in hits[:8]:
            rep.error("redundancy",
                      f'{sid}: display text "{text}" repeats narration ("{phrase}...").',
                      "One channel per fact. If the voice says it, the screen shows the object "
                      "instead — graphics+narration beats graphics+narration+text (d=0.87).")
    elif compared == 0:
        rep.error("redundancy",
                  "No scene's display text could be matched against any spoken window — "
                  "the check examined nothing.",
                  "Section timings probably do not overlap the scene timeline. Verify "
                  "script.json start_seconds/end_seconds come from the MEASURED read.")
    else:
        rep.ok("redundancy",
               f"No display text duplicates narration ({compared} scenes compared).")


def check_peak(scenes, total, rep):
    """Peak-end rule: one engineered maximum, at 70-80%."""
    peaks = [s for s in scenes if s.get("peak") is True]
    if not peaks:
        legacy = [s for s in scenes if s.get("hero_moment") is True]
        if len(legacy) == 1:
            rep.warn("single_peak",
                     f"No scene flagged peak; falling back to hero_moment ({legacy[0]['id']}).",
                     'Add "peak": true to exactly one scene.')
            peaks = legacy
        else:
            rep.error("single_peak",
                      f"No engineered peak declared ({len(legacy)} hero_moment scenes found).",
                      "Memory is the peak plus the ending. Engineer exactly ONE maximum: "
                      "largest scale + full saturation + total freeze + loudest sound.")
            return
    if len(peaks) > 1:
        rep.error("single_peak",
                  f"{len(peaks)} peaks declared ({', '.join(p['id'] for p in peaks)}).",
                  "Two or three medium peaks is strictly worse than one large one.")
        return
    p = peaks[0]
    pos = p["start_seconds"] / total if total else 0
    if not (PEAK_LO <= pos <= PEAK_HI):
        rep.warn("single_peak",
                 f"Peak {p['id']} sits at {pos * 100:.0f}% of runtime "
                 f"(target {PEAK_LO * 100:.0f}-{PEAK_HI * 100:.0f}%).",
                 "Too early and the tail sags; too late and the ending has no room.")
    else:
        rep.ok("single_peak", f"One peak, {p['id']}, at {pos * 100:.0f}% of runtime.")
    if p.get("attention_event") != "freeze":
        rep.warn("single_peak", f"Peak {p['id']} is not a freeze.",
                 "The peak should be the loudest attention event in the piece.")


def check_imagery(scenes, rep):
    """External material must be scarce, and must never appear untreated.

    A raw photograph in a drawn world reads as two unrelated pieces glued
    together — the most common reason an otherwise decent explainer looks cheap.
    """
    with_img = [s for s in scenes if s.get("imagery")]
    if not with_img:
        rep.ok("imagery", "No external imagery — the drawing carries the piece.")
        return

    share = len(with_img) / len(scenes)
    if share > 0.25:
        rep.error("imagery_scarcity",
                  f"Imagery appears in {share * 100:.0f}% of scenes ({len(with_img)}/{len(scenes)}).",
                  "Keep it under 25%. Past that it stops being evidence and becomes "
                  "decoration, and the drawn language loses its authority.")
    else:
        rep.ok("imagery_scarcity", f"Imagery in {share * 100:.0f}% of scenes.")

    untreated = []
    undeclared = []
    for s in with_img:
        for a in s["imagery"]:
            if not a.get("treatment") or a.get("treatment") == "none":
                untreated.append((s["id"], a.get("src", "?")))
            if not a.get("evidence_type"):
                undeclared.append(s["id"])
    if untreated:
        for sid, src in untreated[:6]:
            rep.error("imagery_treated",
                      f"{sid}: '{src}' has no treatment.",
                      "Every external asset passes through duotone / halftone / lineart / "
                      "posterize. A raw composite never ships.")
    else:
        rep.ok("imagery_treated", "Every external asset declares a treatment.")

    if undeclared:
        rep.warn("imagery_evidence",
                 f"No evidence_type on: {', '.join(sorted(set(undeclared))[:6])}.",
                 "Declare WHY imagery beats a drawing here — abstract mechanisms and "
                 "data should be drawn, not photographed.")


def check_end(scenes, total, rep):
    """The ending is half of what is remembered. It must be a statement."""
    last = scenes[-1]
    dur = last["end_seconds"] - last["start_seconds"]
    if dur < END_BEAT_S * 0.5:
        rep.warn("strong_end", f"Closing beat is only {dur:.1f}s.",
                 "Give the last idea room; the end is half of what gets remembered.")
    role = last.get("narrative_role")
    if role in ("transition", "establish_context"):
        rep.error("strong_end", f"Final scene's narrative_role is '{role}'.",
                  "End on a statement, not a fade or a transition.")
    else:
        rep.ok("strong_end", f"Closing beat {dur:.1f}s, role '{role}'.")


def check_gap_seeded(script, rep):
    """Small gaps produce high curiosity; large gaps produce low curiosity."""
    secs = script.get("sections", [])
    if not secs:
        return
    opening = _words(secs[0].get("text", ""))[:40]
    if not opening:
        return
    # A definitional open ("X is a Y", "what is X") is a large-gap open.
    joined = " ".join(opening)
    if re.search(r"\b(is|are) (a|an|the) \w+", joined[:120]) and joined.startswith(("a ", "an ", "the ")):
        rep.warn("gap_seeded", "The piece appears to open on a definition.",
                 "Definitions are large gaps, and large gaps produce LOW curiosity. "
                 "Seed something the viewer already knows first.")
    else:
        rep.ok("gap_seeded", "Opening is not a bare definition.")


# ---------------------------------------------------------------------------

def lint(slug: str) -> tuple[Report, dict]:
    proj = REPO / "projects" / slug
    art = proj / "artifacts"
    if not art.is_dir():
        print(f"error: no artifacts at {art}", file=sys.stderr)
        sys.exit(2)

    def load(name, required=True):
        p = art / name
        if not p.exists():
            if required:
                print(f"error: missing {p}", file=sys.stderr)
                sys.exit(2)
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    plan = load("scene_plan.json")
    script = load("script.json")
    beats_doc = load("beats.json", required=False)
    beats = {k: v["start"] for k, v in (beats_doc.get("beats") or {}).items()}

    scenes = sorted(plan.get("scenes", []), key=lambda s: s["start_seconds"])
    if not scenes:
        print("error: scene_plan has no scenes", file=sys.stderr)
        sys.exit(2)
    total = (plan.get("metadata", {}).get("total_seconds")
             or scenes[-1]["end_seconds"])

    rep = Report()
    check_cold_open(scenes, rep)
    check_gap_seeded(script, rep)
    check_turn(scenes, rep)
    check_velocity(scenes, beats, rep)
    check_interrupts(scenes, rep)
    check_same_subject_runs(scenes, rep)
    check_attention_events_are_qualitative(scenes, rep)
    check_still_windows(scenes, rep)
    check_redundancy(scenes, script, rep)
    check_imagery(scenes, rep)
    check_peak(scenes, total, rep)
    check_end(scenes, total, rep)
    return rep, {"slug": slug, "scenes": len(scenes), "total_seconds": total}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rep, meta = lint(args.slug)

    if args.json:
        print(json.dumps({"meta": meta, "errors": rep.errors, "warnings": rep.warns,
                          "items": rep.items}, indent=2))
        return 1 if rep.errors else 0

    icon = {"OK": "  ok  ", "WARN": " warn ", "ERROR": "ERROR "}
    print(f"\nretention lint — {meta['slug']}  "
          f"({meta['scenes']} scenes, {meta['total_seconds']:.1f}s)\n")
    for i in rep.items:
        print(f"  [{icon[i['level']]}] {i['check']:22s} {i['message']}")
        if i["fix"] and i["level"] != "OK":
            print(f"                                  -> {i['fix']}")
    print(f"\n  {rep.errors} error(s), {rep.warns} warning(s)\n")
    if rep.errors:
        print("  Fix every ERROR before the assets stage spends anything.\n")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
