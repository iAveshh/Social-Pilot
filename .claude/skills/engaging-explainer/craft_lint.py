"""Craft linter — the visual half of the pre-render gate.

    python .claude/skills/engaging-explainer/craft_lint.py <project-slug>
    python .claude/skills/engaging-explainer/craft_lint.py <slug> --json

`retention_lint.py` enforces whether the piece is STRUCTURED to hold attention.
This one enforces whether it is BUILT to be worth looking at. Running only the
first is how a project ends up with a perfect beat map rendered as slides:
episode 3 passed every engagement check on its first run while holding one
camera position for 239 seconds, on one plane, with 68 opacity gates against
6 transforms.

Unlike the retention lint, most of this reads the COMPOSITION SOURCE rather
than a declaration — because the defect it exists to catch is precisely a
composition that ignores what the plan said it would do.

Exit codes:  0 = clean (warnings allowed)   1 = one or more ERRORs   2 = bad input
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# --- thresholds -------------------------------------------------------------
MIN_DISTINCT_SHOTS = 3      # a piece with fewer is holding one distance
MIN_SHOT_RANGE = 1.4        # "a 6% push is invisible" — so is 1.2x
MAX_HOLD_S = 28.0           # longest the camera may sit still
MIN_DEPTH_PLANES = 3        # ground + subject alone is not depth
MIN_TRANSFORM_RATIO = 0.25  # proxy for crossfade-vs-transform; WARN only
MAX_EASING_SHARE = 0.70     # one easing family doing everything = one texture
MIN_KINETIC = 3             # text that is placed, not faded in
MIN_LIFE = 4                # overshoot / settle / stagger / anticipate calls


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, level, check, msg, fix=""):
        self.items.append({"level": level, "check": check, "message": msg, "fix": fix})

    error = lambda s, c, m, f="": s.add("ERROR", c, m, f)   # noqa: E731
    warn = lambda s, c, m, f="": s.add("WARN", c, m, f)     # noqa: E731
    ok = lambda s, c, m: s.add("OK", c, m)                  # noqa: E731

    @property
    def errors(self):
        return sum(1 for i in self.items if i["level"] == "ERROR")

    @property
    def warns(self):
        return sum(1 for i in self.items if i["level"] == "WARN")


def read_sources(proj: Path) -> str:
    """Every .tsx/.ts in the project root — the composition and its components."""
    parts = []
    for p in sorted(proj.glob("*.ts")) + sorted(proj.glob("*.tsx")):
        try:
            parts.append(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return "\n".join(parts)


def check_intensity(plan, src, rep):
    reg = (plan or {}).get("register")
    if reg:
        rep.ok("intensity", f"Register declared: '{reg}'.")
    elif "craftFor(" in src or "blendCraft(" in src:
        rep.warn("intensity", "Register chosen in source but not declared in craft_plan.json.",
                 'Add {"register": "austere|measured|rich|lush"} so the gate can see it.')
    else:
        rep.error("intensity", "No visual register chosen.",
                  'Pick one per topic: {"register": "measured"} in artifacts/craft_plan.json. '
                  "It scales camera, depth, light and motion together — craft up, information flat.")


def check_camera(plan, src, rep, total):
    if not re.search(r"\bcamera\s*\(", src):
        rep.error("camera_used", "The composition never calls camera().",
                  "One camera position for a whole piece is a slide deck, however well "
                  "the slides are drawn. Author a shot list keyed to the beats.")
        return
    shots = (plan or {}).get("shots") or []
    if not shots:
        rep.warn("camera_range", "camera() is used but no shot list is declared in craft_plan.json.",
                 'Declare shots: [{"at": 0, "scale": 0.8}, ...] so range and holds can be checked.')
        return

    scales = [float(s["scale"]) for s in shots if "scale" in s]
    distinct = sorted({round(v, 3) for v in scales})
    if len(distinct) < MIN_DISTINCT_SHOTS:
        rep.error("camera_range",
                  f"Only {len(distinct)} distinct camera distance(s): {distinct}.",
                  f"Use at least {MIN_DISTINCT_SHOTS}. Vary distance across acts; never hold "
                  "one distance for a whole piece.")
    else:
        span = max(scales) / max(1e-6, min(scales))
        if span < MIN_SHOT_RANGE:
            rep.error("camera_range",
                      f"Camera range is only {span:.2f}x ({min(scales):.2f}-{max(scales):.2f}).",
                      f"A 6% scale change is invisible. If a push is worth doing it is worth "
                      f"at least {MIN_SHOT_RANGE}x.")
        else:
            rep.ok("camera_range", f"{len(distinct)} distances spanning {span:.2f}x.")

    ats = sorted(float(s["at"]) for s in shots if "at" in s)
    if ats:
        bounds = [0.0] + ats + [total or ats[-1]]
        gaps = [(a, b - a) for a, b in zip(bounds, bounds[1:]) if b - a > MAX_HOLD_S]
        if gaps:
            worst = max(gaps, key=lambda g: g[1])
            rep.error("camera_holds",
                      f"{len(gaps)} camera hold(s) over {MAX_HOLD_S:.0f}s; worst is "
                      f"{worst[1]:.1f}s at {worst[0]:.1f}s.",
                      "Re-frame at act boundaries at minimum. A held frame is a deliberate "
                      "choice that has to be spent, not a default.")
        else:
            rep.ok("camera_holds", f"No camera hold over {MAX_HOLD_S:.0f}s.")


def check_depth(plan, src, rep):
    declared = (plan or {}).get("depth_planes")
    zs = set(re.findall(r"\bz=\{?\s*(?:Z\.(\w+)|([0-9.]+))", src))
    found = {a or b for a, b in zs if (a or b)}
    # <Foreground> carries its depth as a DEFAULT parameter, so it never appears
    # as an explicit z= and was being missed entirely.
    if "<Foreground" in src:
        found.add("fore")
    n = len(found) if found else (int(declared) if declared else 0)
    if not re.search(r"<Plane\b|planeTransform\s*\(", src):
        rep.error("depth_planes", "No depth planes — every element sits on one plane.",
                  "Parallax is what makes camera movement read as space rather than as "
                  "zoom. Wrap content in <Plane z={Z.far|mid|subject|fore}>.")
    elif n < MIN_DEPTH_PLANES:
        rep.error("depth_planes", f"Only {n} distinct depth(s) in use: {sorted(found)}.",
                  f"Use at least {MIN_DEPTH_PLANES}. Ground plus subject is not depth.")
    else:
        rep.ok("depth_planes", f"{n} distinct depths in use.")


def check_transitions(src, rep):
    """A crossfade says 'that was replaced'. A transformation says 'that BECAME
    this' — which is the entire grammar of explanation."""
    transforms = len(re.findall(r"transform:", src))
    fades = len(re.findall(r"\bo=\{|opacity:", src))
    total = transforms + fades
    if total < 8:
        rep.warn("transition_grammar", "Too little source to judge transition grammar.")
        return
    ratio = transforms / total
    if ratio < MIN_TRANSFORM_RATIO:
        # WARN, not ERROR. This counts every `transform:` against every `o={` and
        # `opacity:` in the source, and plenty of those opacity props are ordinary
        # state rather than a crossfade standing in for a transformation. The
        # ratio is a real smell -- 8% genuinely did mean "nothing ever moves" --
        # but it is a proxy, and a proxy should not block a render by itself.
        rep.warn("transition_grammar",
                  f"Only {ratio * 100:.0f}% of state changes move anything "
                  f"({transforms} transforms vs {fades} opacity gates).",
                  "Elements are appearing and disappearing rather than becoming each "
                  "other. Where two states share matter, transform between them — "
                  "see engine/motion.ts becomes() and rectLerp().")
    else:
        rep.ok("transition_grammar",
               f"{ratio * 100:.0f}% of state changes are transformations.")


def check_easing(src, rep):
    fams = re.findall(r"\b(ramp|snap|seat|slide|drift|windowed|overshoot|settle|anticipate|becomes)\s*\(", src)
    if len(fams) < 10:
        rep.warn("easing_variety", "Too few easing calls to judge variety.")
        return
    counts: dict[str, int] = {}
    for f in fams:
        counts[f] = counts.get(f, 0) + 1
    top, n = max(counts.items(), key=lambda kv: kv[1])
    share = n / len(fams)
    if share > MAX_EASING_SHARE:
        rep.error("easing_variety",
                  f"'{top}' is {share * 100:.0f}% of all {len(fams)} easing calls.",
                  "One curve for everything gives every event the same texture. Timing "
                  "families exist to be assigned by intent: snap for a fact landing, "
                  "seat for a part arriving, drift for atmosphere.")
    else:
        rep.ok("easing_variety",
               f"{len(counts)} easing families, largest share {share * 100:.0f}%.")


def check_kinetic(src, rep):
    n = len(re.findall(r"<KineticText\b|<Wipe\b|<Counter\b", src))
    if n < MIN_KINETIC:
        rep.warn("kinetic_type",
                 f"Only {n} kinetic text/reveal element(s).",
                 "Text that fades in arrives from nowhere; text that rises into place "
                 "has been PUT there, and the eye reads placement as intent.")
    else:
        rep.ok("kinetic_type", f"{n} kinetic text/reveal elements.")


def check_life(src, rep):
    n = len(re.findall(r"\b(overshoot|settle|anticipate|stagger|lag)\s*\(", src))
    if n < MIN_LIFE:
        rep.error("life_layer",
                  f"Only {n} secondary-motion call(s).",
                  "Everything eases in and stops dead on its target value, which is why "
                  "competent motion still reads as inert. Add overshoot / settle / "
                  "stagger to STRUCTURE — never to a figure at the moment it lands.")
    else:
        rep.ok("life_layer", f"{n} secondary-motion calls.")


def check_light(src, rep):
    has = bool(re.search(r"<Vignette\b|<KeyLight\b", src))
    if not has:
        rep.error("light", "No key light or vignette.",
                  "A flat fill is the difference between 'a div with a background colour' "
                  "and a surface. Add <KeyLight> and <Vignette>; both track the camera.")
    else:
        rep.ok("light", "Key light / vignette present.")


def lint(slug: str):
    proj = REPO / "projects" / slug
    art = proj / "artifacts"
    if not proj.is_dir():
        print(f"error: no project at {proj}", file=sys.stderr)
        sys.exit(2)

    src = read_sources(proj)
    if not src.strip():
        print(f"error: no .ts/.tsx composition source in {proj}", file=sys.stderr)
        sys.exit(2)

    plan = {}
    cp = art / "craft_plan.json"
    if cp.exists():
        plan = json.loads(cp.read_text(encoding="utf-8"))

    total = None
    tl = art / "narration_timing.json"
    if tl.exists():
        total = json.loads(tl.read_text(encoding="utf-8")).get("duration_seconds")

    rep = Report()
    check_intensity(plan, src, rep)
    check_camera(plan, src, rep, total)
    check_depth(plan, src, rep)
    check_light(src, rep)
    check_transitions(src, rep)
    check_easing(src, rep)
    check_life(src, rep)
    check_kinetic(src, rep)
    return rep, {"slug": slug, "seconds": total, "source_chars": len(src)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rep, meta = lint(args.slug)

    if args.json:
        print(json.dumps({"meta": meta, "errors": rep.errors,
                          "warnings": rep.warns, "items": rep.items}, indent=2))
        return 1 if rep.errors else 0

    icon = {"OK": "  ok  ", "WARN": " warn ", "ERROR": "ERROR "}
    secs = f", {meta['seconds']:.1f}s" if meta["seconds"] else ""
    print(f"\ncraft lint — {meta['slug']}{secs}\n")
    for i in rep.items:
        print(f"  [{icon[i['level']]}] {i['check']:20s} {i['message']}")
        if i["fix"] and i["level"] != "OK":
            print(f"                              -> {i['fix']}")
    print(f"\n  {rep.errors} error(s), {rep.warns} warning(s)\n")
    if rep.errors:
        print("  Structure passing is not the same as being worth watching.\n")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
