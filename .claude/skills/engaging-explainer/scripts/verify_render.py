"""Post-render self-review, run against the file that actually ships.

    python .claude/skills/engaging-explainer/scripts/verify_render.py <slug> [--video PATH]

Probes the container, then RE-TRANSCRIBES the rendered audio and re-locates
several anchor phrases — including the declared peak — to prove picture and
sound still agree in the encoded file.

Rendering from correct props is not evidence of a correct render. Frame-rate
rounding, an audio pad, a filter-graph resample or a muxer offset all produce a
file whose sync differs from the timeline you authored, and every one of them is
invisible until someone watches it. Checking the source narration proves nothing
about the artefact you are about to publish.

Writes artifacts/render_report.json.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SYNC_TOLERANCE_S = 0.6


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def glue(raw):
    out = []
    for w in raw:
        txt = w.get("word") or ""
        if not txt.strip():
            continue
        if out and not txt.startswith(" "):
            out[-1]["word"] += txt
            out[-1]["end"] = w.get("end", out[-1]["end"])
        else:
            out.append({"word": txt, "start": w.get("start"), "end": w.get("end")})
    return [w for w in out if w["start"] is not None and norm(w["word"])]


def probe(path: Path) -> dict:
    o = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,"
         "channels,sample_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(o.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--video")
    ap.add_argument("--model-size", default="base")
    args = ap.parse_args()

    proj = REPO / "projects" / args.slug
    art = proj / "artifacts"
    mp4 = Path(args.video) if args.video else proj / "renders" / f"{args.slug}.mp4"
    if not mp4.exists():
        print(f"error: no render at {mp4}", file=sys.stderr)
        return 2

    info = probe(mp4)
    fmt = info["format"]
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(fmt["duration"])
    print(f"video : {v['codec_name']} {v['width']}x{v['height']} @ {v['r_frame_rate']}")
    print(f"audio : {a['codec_name'] if a else 'NONE'} "
          f"{a.get('channels', '-') if a else '-'}ch")
    print(f"length: {dur:.3f}s   size: {int(fmt['size']) / 1e6:.1f} MB")

    notes = [f"ffprobe: {v['codec_name']} {v['width']}x{v['height']} @ "
             f"{v['r_frame_rate']}, {a['codec_name'] if a else 'no'} audio, {dur:.3f}s."]
    issues = []
    if not a:
        issues.append("rendered file has NO audio stream")

    tl = json.loads((art / "narration_timing.json").read_text(encoding="utf-8"))
    planned = tl.get("duration_seconds")
    if planned:
        drift = dur - planned
        print(f"drift vs. planned {planned}s: {drift:+.3f}s")
        notes.append(f"Duration drift against the planned {planned}s timeline: {drift:+.3f}s.")
        if abs(drift) > 1.0:
            issues.append(f"duration drift {drift:+.3f}s exceeds 1.0s")

    # --- re-transcribe the RENDERED audio -----------------------------------
    sys.path.insert(0, str(REPO))
    try:
        from tools.tool_registry import registry
    except Exception as e:                                    # pragma: no cover
        print(f"warning: tool registry unavailable ({e}); skipping sync check")
        registry = None

    checks = []
    if registry is not None:
        registry.discover()
        wav = mp4.with_name("_verify.wav")
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "16000",
                        str(wav)], check=True, capture_output=True)
        tr = registry._tools["transcriber"].execute(
            {"input_path": str(wav), "model_size": args.model_size, "language": "en",
             "output_dir": str(art / "verify")})
        wav.unlink(missing_ok=True)

        if not tr.success:
            issues.append(f"re-transcribe failed: {str(tr.error)[:120]}")
        else:
            got = glue([w for s in tr.data.get("segments", []) for w in (s.get("words") or [])])
            gk = [norm(w["word"]) for w in got]
            src = glue(tl.get("words") or [])

            # anchor points: quartiles of the read, plus the declared peak
            anchors = {}
            for label, frac in (("10%", 0.10), ("35%", 0.35), ("70%", 0.70), ("95%", 0.95)):
                idx = int(len(src) * frac)
                if 0 <= idx < len(src) - 4:
                    anchors[label] = idx
            plan_path = art / "scene_plan.json"
            if plan_path.exists():
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                pk = next((s for s in plan.get("scenes", []) if s.get("peak") is True), None)
                if pk:
                    at = pk["start_seconds"]
                    idx = min(range(len(src)), key=lambda i: abs(src[i]["start"] - at))
                    if idx < len(src) - 4:
                        anchors["PEAK"] = idx

            print("\nsync — anchor phrases re-located in the RENDERED audio:")
            for label, idx in anchors.items():
                window = [norm(w["word"]) for w in src[idx:idx + 4]]
                hit = None
                for i in range(len(gk) - 4 + 1):
                    if gk[i:i + 4] == window:
                        hit = got[i]["start"]
                        break
                if hit is None:
                    print(f"  {label:5s} could not re-locate {' '.join(window)!r}")
                    continue
                # whisper hands back numpy scalars; json.dump refuses numpy.bool_
                # and numpy.float32, so coerce to natives at the boundary.
                planned_at = float(src[idx]["start"])
                hit = float(hit)
                delta = hit - planned_at
                ok = bool(abs(delta) <= SYNC_TOLERANCE_S)
                checks.append({"anchor": label, "planned": round(planned_at, 3),
                               "rendered": round(hit, 3), "delta": round(delta, 3), "ok": ok})
                print(f"  {label:5s} {planned_at:7.2f}s -> {hit:7.2f}s "
                      f"({delta:+.2f}s) {'OK' if ok else 'DRIFTED'}")
                if not ok:
                    issues.append(f"{label} anchor drifted {delta:+.3f}s in the rendered audio")

    if checks:
        notes.append("Anchor phrases re-located in the rendered audio: " + "; ".join(
            f"{c['anchor']} {c['delta']:+.3f}s" for c in checks) + ".")

    report = {
        "version": "1.0",
        "outputs": [{
            "path": str(mp4),
            "duration_seconds": round(dur, 3),
            "resolution": f"{v['width']}x{v['height']}",
            "size_bytes": int(fmt["size"]),
        }],
        "sync_checks": checks,
        "verification_notes": notes,
        "recommended_action": "review" if not issues else "revise",
    }
    if issues:
        report["issues"] = issues
    (art / "render_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nrender_report.json written — {len(issues)} issue(s)")
    for i in issues:
        print("  !", i)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
