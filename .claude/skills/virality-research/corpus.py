"""The findings store: what we currently believe about why video travels.

    python .claude/skills/virality-research/corpus.py list [--slot open] [--platform youtube]
    python .claude/skills/virality-research/corpus.py add   --file new_findings.json
    python .claude/skills/virality-research/corpus.py audit

The corpus is deliberately NOT a pile of tips. Every entry carries the grade of
its evidence, the contrast class it was measured against, the scope it applies
to, and the date it was observed — because the single most common failure in
this subject is a claim with no denominator repeated until it sounds like a law.

`audit` is the important verb. It ages findings out by grade rather than
globally: a platform's ranking behaviour goes stale in months, and a result
about human arousal does not go stale at all. Treating those the same is how a
corpus rots without anyone noticing.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE / "corpus" / "findings.json"

# How long a finding of each grade stays trustworthy without re-observation.
# None means it does not decay: a controlled result about human psychology is
# not invalidated by a platform shipping a new ranking model.
HALF_LIFE_MONTHS = {
    "experimental": None,
    "observational": 18,
    "platform": 6,
    "practitioner": 6,
    "folklore": 0,
}

GRADES = list(HALF_LIFE_MONTHS)
SLOTS = ["open", "structure", "register", "share_trigger", "metadata"]

# Only these grades may become a binding authoring constraint. A practitioner
# claim can suggest; it cannot compel. See reference/method.md.
BINDING_GRADES = {"experimental", "observational", "platform"}


def load() -> dict:
    if not STORE.exists():
        return {"version": "1.0", "updated": str(date.today()), "findings": []}
    return json.loads(STORE.read_text(encoding="utf-8"))


def save(doc: dict) -> None:
    doc["updated"] = str(date.today())
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")


def months_since(iso: str) -> float:
    then = datetime.strptime(iso, "%Y-%m-%d").date()
    today = date.today()
    return (today.year - then.year) * 12 + (today.month - then.month) + \
           (today.day - then.day) / 30.0


def validate(f: dict) -> list[str]:
    """Structural problems that make a finding unusable, not merely weak."""
    bad = []
    for key in ("id", "claim", "grade", "scope", "slot", "observed_on", "sources"):
        if not f.get(key):
            bad.append(f"missing {key}")
    if f.get("grade") not in GRADES:
        bad.append(f"grade {f.get('grade')!r} not one of {GRADES}")
    if f.get("slot") not in SLOTS:
        bad.append(f"slot {f.get('slot')!r} not one of {SLOTS}")
    # The base-rate rule. An observational claim without a contrast class is a
    # claim about viral videos, not a claim about what MAKES videos viral.
    if f.get("grade") == "observational" and not f.get("contrast_class"):
        bad.append("observational finding has no contrast_class — "
                   "without a denominator this is survivorship, not evidence")
    if f.get("grade") in BINDING_GRADES and not f.get("application"):
        bad.append("binding finding has no `application` — a finding that does not "
                   "become an authoring constraint is trivia")
    return bad


def status_of(f: dict) -> str:
    """Current standing, recomputed rather than trusted from the file."""
    if f.get("status") == "refused":
        return "refused"
    hl = HALF_LIFE_MONTHS.get(f.get("grade"))
    if hl is None:
        return "active"
    if hl == 0:
        return "refused"
    age = months_since(f["observed_on"])
    if age > hl * 2:
        return "expired"
    if age > hl:
        return "stale"
    return "active"


def active(doc: dict, slot: str | None = None, platform: str | None = None,
           binding_only: bool = False) -> list[dict]:
    out = []
    for f in doc.get("findings", []):
        if status_of(f) not in ("active", "stale"):
            continue
        if binding_only and f.get("grade") not in BINDING_GRADES:
            continue
        if slot and f.get("slot") != slot:
            continue
        if platform:
            plats = (f.get("scope") or {}).get("platforms") or ["any"]
            if platform not in plats and "any" not in plats:
                continue
        out.append(f)
    return out


def cmd_list(args) -> int:
    doc = load()
    rows = active(doc, args.slot, args.platform, args.binding_only)
    if not rows:
        print("no findings match")
        return 0
    for f in rows:
        sc = f.get("scope", {})
        print(f"\n[{f['id']}] {f['grade']:<13} {status_of(f):<7} "
              f"slot={f['slot']:<12} {','.join(sc.get('platforms', ['any']))}"
              f" / {sc.get('duration_band', 'any')}")
        print(f"  {f['claim']}")
        if f.get("contrast_class"):
            print(f"  vs: {f['contrast_class']}")
        if f.get("effect"):
            print(f"  effect: {f['effect']}")
        if f.get("application"):
            print(f"  -> {f['application']}")
    print(f"\n{len(rows)} finding(s)")
    return 0


def cmd_add(args) -> int:
    doc = load()
    incoming = json.loads(Path(args.file).read_text(encoding="utf-8"))
    new = incoming if isinstance(incoming, list) else incoming.get("findings", [])
    have = {f["id"] for f in doc["findings"]}
    added, rejected = 0, 0
    for f in new:
        bad = validate(f)
        if bad:
            print(f"REJECTED {f.get('id', '?')}: {'; '.join(bad)}", file=sys.stderr)
            rejected += 1
            continue
        if f["id"] in have:
            doc["findings"] = [f if g["id"] == f["id"] else g for g in doc["findings"]]
            print(f"  updated {f['id']}")
        else:
            doc["findings"].append(f)
            print(f"  added   {f['id']}")
        added += 1
    save(doc)
    print(f"\n{added} written, {rejected} rejected -> {STORE}")
    return 1 if rejected else 0


def cmd_audit(args) -> int:
    doc = load()
    counts: dict[str, int] = {}
    problems = []
    for f in doc.get("findings", []):
        st = status_of(f)
        counts[st] = counts.get(st, 0) + 1
        bad = validate(f)
        if bad:
            problems.append((f.get("id", "?"), "; ".join(bad)))
        if st in ("stale", "expired"):
            problems.append((f["id"],
                             f"{st}: {f['grade']} finding observed {months_since(f['observed_on']):.0f} "
                             f"months ago (half-life {HALF_LIFE_MONTHS[f['grade']]}mo) — re-harvest before relying on it"))
    print(f"corpus: {len(doc.get('findings', []))} finding(s), last updated {doc.get('updated')}")
    for k in ("active", "stale", "expired", "refused"):
        if counts.get(k):
            print(f"  {k:<8} {counts[k]}")
    if problems:
        print()
        for fid, msg in problems:
            print(f"  ! {fid}: {msg}")
    return 1 if any("missing" in m or "no contrast_class" in m for _, m in problems) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="show findings")
    p.add_argument("--slot", choices=SLOTS)
    p.add_argument("--platform")
    p.add_argument("--binding-only", action="store_true",
                   help="only grades that may compel an authoring decision")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("add", help="merge findings from a harvest")
    p.add_argument("--file", required=True)
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("audit", help="recompute standing and report rot")
    p.set_defaults(fn=cmd_audit)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
