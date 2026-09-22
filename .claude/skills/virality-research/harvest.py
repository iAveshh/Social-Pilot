"""Emit a search plan for a live harvest, and grade what comes back.

    python .claude/skills/virality-research/harvest.py plan --platform youtube --format long_form
    python .claude/skills/virality-research/harvest.py grade --file draft_findings.json

This script does not browse. It cannot: the agent holds the web tools, and a
subprocess that scraped on its own would bypass the approval surface the user
sees. What it does is stop the harvest from being improvised — it fixes the
queries, insists on the adversarial ones, and refuses to let an ungraded claim
into the corpus.

The queries in `plan` come in four bands, and the fourth is the one that makes
this worth running:

  1. MECHANISM   — why anything spreads at all. Peer-reviewed where possible.
  2. PLATFORM    — how the specific platform ranks and surfaces, right now.
  3. PRACTICE    — what working creators say, which is mostly ungraded.
  4. DISCONFIRM  — who says the above is wrong, and what the base rates are.

Skipping band 4 is how you end up with a corpus of folklore that agrees with
itself. Any harvest that returns nothing from band 4 has not finished.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import BINDING_GRADES, GRADES, SLOTS, validate  # noqa: E402

YEAR = date.today().year

BANDS = {
    "mechanism": [
        "why content spreads social transmission research effect size",
        "arousal emotion sharing study journal replication",
        "curiosity information gap study effect size",
        "narrative transportation persuasion meta-analysis",
    ],
    "platform": [
        "{platform} algorithm ranking factors {year} confirmed changes",
        "{platform} {format} retention benchmarks {year} data",
        "{platform} creator documentation recommendation system how it works",
        "{platform} {format} length data {year}",
    ],
    "practice": [
        "{platform} hook formulas {format} {year}",
        "{platform} thumbnail title click-through rate test data",
        "what makes videos go viral {year} playbook",
    ],
    "disconfirm": [
        "survivorship bias viral content base rate criticism",
        "{platform} algorithm myths debunked creator experiment failed",
        "viral video advice does not work evidence contradicts",
        "replication failure social media engagement study",
    ],
}


def cmd_plan(args) -> int:
    ctx = {"platform": args.platform, "format": args.format, "year": YEAR}
    plan = {band: [q.format(**ctx) for q in qs] for band, qs in BANDS.items()}
    if args.json:
        print(json.dumps(plan, indent=2))
        return 0
    print(f"harvest plan — {args.platform} / {args.format} / {YEAR}\n")
    for band, qs in plan.items():
        print(f"  {band.upper()}")
        for q in qs:
            print(f"    - {q}")
        print()
    print("Run every band. A harvest with no DISCONFIRM results is not finished —")
    print("it has only found the sources that agree with each other.\n")
    print("Then write each observation into a draft file and grade it:")
    print("  python .claude/skills/virality-research/harvest.py grade --file draft.json")
    return 0


TEMPLATE = {
    "id": "f-XXX",
    "claim": "one sentence, with the number in it",
    "grade": "|".join(GRADES),
    "contrast_class": "what the viral set was compared against — REQUIRED for observational",
    "effect": "the size, in the source's own units",
    "scope": {"platforms": ["youtube"], "formats": ["long_form"], "duration_band": "5-20m"},
    "slot": "|".join(SLOTS),
    "observed_on": str(date.today()),
    "sources": ["https://..."],
    "application": "the authoring constraint this becomes, as one imperative sentence",
}


def cmd_grade(args) -> int:
    if args.template:
        print(json.dumps({"findings": [TEMPLATE]}, indent=2))
        return 0
    doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
    rows = doc if isinstance(doc, list) else doc.get("findings", [])
    fatal = 0
    for f in rows:
        bad = validate(f)
        notes = []

        # The demotion rule. A source's prestige does not upgrade its evidence:
        # a claim with no visible denominator is a practitioner claim however
        # respectable the outlet, and the corpus records the demotion so the
        # same claim is not re-promoted on the next harvest.
        if f.get("grade") in ("experimental", "observational") and not f.get("contrast_class"):
            notes.append("DEMOTE to practitioner — no contrast class, so this describes "
                         "viral videos rather than explaining them")
        if f.get("grade") in BINDING_GRADES and len(f.get("sources") or []) < 1:
            notes.append("binding grades need at least one traceable source")
        FIRST_PARTY = ("youtube.com", "tiktok.com", "instagram.com",
                       "support.google.com", "developers.", "blog.google")
        if f.get("grade") == "platform" and not any(
                d in s for s in (f.get("sources") or []) for d in FIRST_PARTY):
            notes.append("graded `platform` but no first-party source — a blog reporting "
                         "on a platform change is `practitioner` until the platform says it")

        status = "OK" if not bad and not notes else ("FATAL" if bad else "REVIEW")
        if bad:
            fatal += 1
        print(f"[{status:<6}] {f.get('id', '?')}  {str(f.get('claim'))[:72]}")
        for b in bad:
            print(f"           ! {b}")
        for n in notes:
            print(f"           ~ {n}")
    print(f"\n{len(rows)} graded, {fatal} unusable")
    print("Fix the unusable ones, then: corpus.py add --file " + (args.file or "draft.json"))
    return 1 if fatal else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="print the search plan for a live harvest")
    p.add_argument("--platform", default="youtube")
    p.add_argument("--format", default="long_form")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("grade", help="check drafted findings before they enter the corpus")
    p.add_argument("--file")
    p.add_argument("--template", action="store_true", help="print a blank finding")
    p.set_defaults(fn=cmd_grade)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
