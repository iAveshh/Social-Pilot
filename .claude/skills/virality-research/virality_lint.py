"""The gate: does this piece actually apply what the corpus knows?

    python .claude/skills/virality-research/virality_lint.py <project-slug>

Reads `artifacts/virality_packet.json` alongside the script and scene plan, and
checks the piece against every ACTIVE BINDING finding in the corpus.

The check that matters most is `refusals_reasoned`. It is not enough to apply
the findings you liked — every binding finding must be either applied or
refused **with a reason on the record**. A corpus you can quietly ignore is a
corpus that does nothing, and silently skipping the inconvenient findings is
exactly how "we researched virality" becomes decoration.

The second most important is `applied_are_binding`. Practitioner claims and
folklore may inform a decision; they may never be cited as the reason for one.

This lint runs ALONGSIDE retention_lint and craft_lint, not instead of them.
They ask different questions:

    retention_lint  — is it built to be watched to the end?
    craft_lint      — is it built to be worth looking at?
    virality_lint   — is it built to be passed on, and did we say why?
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from corpus import BINDING_GRADES, active, load, status_of  # noqa: E402

REPO = HERE.parents[2]
TITLE_MAX = 70            # beyond this most surfaces truncate
STOP = {"the", "a", "an", "of", "and", "to", "in", "is", "it", "that", "this",
        "for", "on", "we", "you", "they", "with", "what", "how", "why"}


class Report:
    def __init__(self):
        self.items, self.errors, self.warns = [], 0, 0

    def ok(self, check, msg):
        self.items.append(("ok", check, msg, None))

    def warn(self, check, msg, fix=None):
        self.warns += 1
        self.items.append(("WARN", check, msg, fix))

    def error(self, check, msg, fix=None):
        self.errors += 1
        self.items.append(("ERROR", check, msg, fix))


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", (s or "").lower()) if w not in STOP}


def band_for(seconds: float) -> str:
    if seconds < 60:
        return "<60s"
    if seconds <= 300:
        return "1-5m"
    if seconds <= 1200:
        return "5-20m"
    return "20m+"


def scope_covers(f: dict, packet: dict) -> bool:
    sc = f.get("scope") or {}
    plats = sc.get("platforms") or ["any"]
    fmts = sc.get("formats") or ["any"]
    band = sc.get("duration_band", "any")
    if packet.get("platform") not in plats and "any" not in plats:
        return False
    if packet.get("format") not in fmts and "any" not in fmts:
        return False
    if band not in ("any", packet.get("duration_band")):
        return False
    return True


# --- checks ----------------------------------------------------------------

def check_scope(packet, script, rep):
    missing = [k for k in ("platform", "format", "duration_band") if not packet.get(k)]
    if missing:
        rep.error("scope_declared", f"packet does not declare {', '.join(missing)}.",
                  "Findings are scoped. An undeclared scope means every finding is "
                  "applied blind, including the ones about a different format entirely.")
        return
    total = script.get("total_duration_seconds") or 0
    want = band_for(total)
    if total and packet["duration_band"] != want:
        rep.error("scope_declared",
                  f"packet declares duration_band {packet['duration_band']!r} but the "
                  f"script is {total:.0f}s ({want}).",
                  "A Shorts finding must not be allowed to constrain a long-form piece.")
    else:
        rep.ok("scope_declared",
               f"{packet['platform']} / {packet['format']} / {packet['duration_band']}.")


def check_hook(packet, plan, corpus, rep):
    hook = packet.get("hook") or {}
    if not hook.get("promise"):
        rep.error("hook_promise", "No hook promise declared.",
                  "Name, in one sentence, what the first seconds promise the viewer. "
                  "If you cannot write it down you have not designed it.")
        return
    # Only a BINDING, IN-SCOPE finding may narrow the window. Without that
    # filter a three-second rule measured on vertical short-form would silently
    # govern a twenty-minute documentary.
    windows = [f for f in active(corpus, slot="open", platform=packet.get("platform"),
                                 binding_only=True)
               if f.get("hook_window_seconds") and scope_covers(f, packet)]
    limit = min((f["hook_window_seconds"] for f in windows), default=3.0)
    lands = hook.get("lands_by_seconds")
    if lands is None:
        rep.warn("hook_promise", "hook.lands_by_seconds not declared.")
        return
    if lands > limit:
        rep.error("hook_promise",
                  f"Hook lands at {lands:.1f}s; the corpus puts the window at {limit:.1f}s "
                  f"for this platform.",
                  "Everything after the window is spent on people who already left.")
        return
    scenes = sorted(plan.get("scenes", []), key=lambda s: s["start_seconds"])
    first_event = next((s for s in scenes
                        if s.get("attention_event") in ("onset", "cessation", "freeze")), None)
    if first_event and first_event["start_seconds"] > limit:
        rep.error("hook_promise",
                  f"First attention event is at {first_event['start_seconds']:.1f}s, "
                  f"outside the {limit:.1f}s window.")
    else:
        rep.ok("hook_promise", f"Promise declared, lands by {lands:.1f}s (window {limit:.1f}s).")


def check_share_trigger(packet, rep):
    st = packet.get("share_trigger")
    if not st:
        rep.error("share_trigger", "No share trigger declared.",
                  "Sharing is a separate design object from watching. Name the ONE moment "
                  "built to be sent to someone, and say who they send it to.")
        return
    if isinstance(st, list):
        rep.error("share_trigger", f"{len(st)} share triggers declared.",
                  "One. Several weak reasons to share is worse than one strong one, for "
                  "the same reason several medium peaks is worse than one large one.")
        return
    missing = [k for k in ("kind", "why_they_send_it") if not st.get(k)]
    if missing:
        rep.error("share_trigger", f"share_trigger missing {', '.join(missing)}.")
    else:
        rep.ok("share_trigger", f"One trigger: {st['kind']}.")


def check_register(packet, rep):
    reg = packet.get("register") or {}
    if not reg.get("arousal"):
        rep.error("register_declared", "No arousal register declared.")
        return
    if not reg.get("cost_accepted"):
        rep.error("register_declared",
                  f"Register {reg['arousal']!r} declared with no cost stated.",
                  "Low-arousal content measurably spreads less. Choosing it is legitimate "
                  "and it is not free — write down what you are giving up.")
    else:
        rep.ok("register_declared", f"{reg['arousal']} arousal, cost stated.")


def check_metadata(packet, script, rep):
    md = packet.get("metadata") or {}
    if not md.get("title"):
        rep.error("metadata", "No title.")
        return
    title = md["title"]
    if len(title) > TITLE_MAX:
        rep.warn("metadata", f"Title is {len(title)} chars; most surfaces truncate near {TITLE_MAX}.")
    if not md.get("thumbnail_concept"):
        rep.error("metadata", "No thumbnail concept.",
                  "The thumbnail is half the click. Design it here, not after the render.")
        return
    secs = script.get("sections") or []
    if secs:
        overlap = words(title) & words(secs[0].get("text", ""))
        if len(overlap) >= 4:
            rep.warn("metadata",
                     f"Title shares {len(overlap)} content words with the opening line.",
                     "A title that restates the first sentence spends the promise twice.")
            return
    rep.ok("metadata", f"Title {len(title)} chars, thumbnail concept present.")


def check_applied(packet, corpus, rep):
    by_id = {f["id"]: f for f in corpus.get("findings", [])}
    applied = packet.get("applied") or []
    if not applied:
        rep.error("applied_are_binding", "No findings applied.",
                  "If the corpus changed nothing about this piece, either the corpus is "
                  "empty or it was not consulted.")
        return
    bad, weak, unscoped = [], [], []
    for a in applied:
        f = by_id.get(a.get("finding_id"))
        if not f:
            bad.append(f"{a.get('finding_id')} is not in the corpus")
            continue
        if not a.get("how"):
            bad.append(f"{f['id']} applied with no `how`")
        if f.get("grade") == "folklore" or status_of(f) in ("refused", "expired"):
            bad.append(f"{f['id']} is {f.get('grade')}/{status_of(f)} and may not be applied")
        elif f.get("grade") not in BINDING_GRADES:
            weak.append(f"{f['id']} is {f['grade']} — may inform, may not justify")
        if not scope_covers(f, packet):
            unscoped.append(f"{f['id']} scope does not cover this piece")
    for b in bad:
        rep.error("applied_are_binding", b)
    for w in weak:
        rep.warn("applied_are_binding", w)
    for u in unscoped:
        rep.error("scope_respected", u,
                  "Applying an out-of-scope finding is worse than applying none — it is "
                  "a rule from a different format wearing the authority of evidence.")
    if not bad and not unscoped:
        rep.ok("applied_are_binding", f"{len(applied)} finding(s) applied, all in scope.")
        rep.ok("scope_respected", "Every applied finding covers this platform and format.")


def check_refusals(packet, corpus, rep):
    relevant = [f for f in active(corpus, platform=packet.get("platform"), binding_only=True)
                if scope_covers(f, packet)]
    seen = {a.get("finding_id") for a in (packet.get("applied") or [])}
    refused = {r.get("finding_id"): r for r in (packet.get("refused") or [])}
    unaddressed, unreasoned = [], []
    for f in relevant:
        if f["id"] in seen:
            continue
        if f["id"] not in refused:
            unaddressed.append(f["id"])
        elif not refused[f["id"]].get("because"):
            unreasoned.append(f["id"])
    if unaddressed:
        rep.error("refusals_reasoned",
                  f"{len(unaddressed)} binding finding(s) neither applied nor refused: "
                  f"{', '.join(unaddressed[:8])}.",
                  "Every in-scope binding finding must be decided on the record. A corpus "
                  "you can quietly skip is a corpus that does nothing.")
    for fid in unreasoned:
        rep.error("refusals_reasoned", f"{fid} refused with no reason.")
    if not unaddressed and not unreasoned:
        rep.ok("refusals_reasoned",
               f"All {len(relevant)} in-scope binding finding(s) decided on the record.")


def check_freshness(packet, corpus, rep):
    by_id = {f["id"]: f for f in corpus.get("findings", [])}
    stale = [a["finding_id"] for a in (packet.get("applied") or [])
             if by_id.get(a.get("finding_id")) and status_of(by_id[a["finding_id"]]) == "stale"]
    if stale:
        rep.warn("corpus_freshness",
                 f"{len(stale)} applied finding(s) are past their half-life: {', '.join(stale[:6])}.",
                 "Re-harvest. Platform behaviour is the fastest-rotting thing in the corpus.")
    else:
        rep.ok("corpus_freshness", "No applied finding is past its half-life.")


def check_promise_kept(packet, script, rep):
    """The hook promises something; the piece has to be about that thing."""
    promise = ((packet.get("hook") or {}).get("promise")) or ""
    if not promise:
        return
    body = " ".join(s.get("text", "") for s in (script.get("sections") or []))
    pw = words(promise)
    if not pw:
        return
    hit = len(pw & words(body)) / len(pw)
    if hit < 0.34:
        rep.warn("promise_kept",
                 f"Only {hit * 100:.0f}% of the hook's content words appear anywhere in the read.",
                 "The commonest cause of a steep 30-second drop is a title-and-hook promise "
                 "the piece never fulfils.")
    else:
        rep.ok("promise_kept", f"{hit * 100:.0f}% of the hook's content words recur in the read.")


# --- driver ----------------------------------------------------------------

def lint(slug: str):
    art = REPO / "projects" / slug / "artifacts"
    if not art.is_dir():
        print(f"error: no artifacts at {art}", file=sys.stderr)
        sys.exit(2)

    def load_art(name, required=True):
        p = art / name
        if not p.exists():
            if required:
                print(f"error: missing {p}", file=sys.stderr)
                sys.exit(2)
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    packet = load_art("virality_packet.json")
    script = load_art("script.json")
    plan = load_art("scene_plan.json", required=False)
    corpus = load()

    rep = Report()
    check_scope(packet, script, rep)
    check_hook(packet, plan, corpus, rep)
    check_share_trigger(packet, rep)
    check_register(packet, rep)
    check_metadata(packet, script, rep)
    check_applied(packet, corpus, rep)
    check_refusals(packet, corpus, rep)
    check_freshness(packet, corpus, rep)
    check_promise_kept(packet, script, rep)
    return rep, {"slug": slug, "corpus_size": len(corpus.get("findings", []))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rep, meta = lint(args.slug)
    if args.json:
        print(json.dumps({"meta": meta, "errors": rep.errors, "warnings": rep.warns,
                          "items": rep.items}, indent=2))
        return 1 if rep.errors else 0

    print(f"\nvirality lint — {meta['slug']}  ({meta['corpus_size']} findings in corpus)\n")
    for level, check, msg, fix in rep.items:
        tag = "  ok  " if level == "ok" else level.center(6)
        print(f"  [{tag}] {check:<22} {msg}")
        if fix:
            print(f"{'':<34}-> {fix}")
    print(f"\n  {rep.errors} error(s), {rep.warns} warning(s)\n")
    if rep.errors:
        print("  Fix every ERROR before publishing.")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
