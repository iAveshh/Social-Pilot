# Authored skills

This repository is a fork of **OpenMontage** (calesthio, initial release
`a3e735c`, 29 Mar 2026). The great majority of the skills under
`.claude/skills/` and the whole `skills/` library came with that fork.

This file tracks the skills **written here**, so the line between upstream work
and our own stays visible.

Last updated: 9 Sep 2026.

---

## Summary

| Skill | Created | Size | Cost / video | What it does |
|---|---|---|---|---|
| [`ai-news-reel`](.claude/skills/ai-news-reel/SKILL.md) | 3 Sep 2026 | 13 files, 933 lines | ~$0.03 | 15-25s vertical tech-news Reel, researched and rendered end to end |
| [`paper-brief-reel`](.claude/skills/paper-brief-reel/SKILL.md) | 3 Sep 2026 | 5 files, 303 lines | ~$2-4 | The premium editorial counterpart - cream press stock, spec cards, matted plates |
| [`save-to-icloud`](.claude/skills/save-to-icloud/SKILL.md) | 3 Sep 2026 | 2 files, 131 lines | $0 | Publishes a finished reel to iCloud Drive, hash-verified |
| [`engaging-explainer`](.claude/skills/engaging-explainer/SKILL.md) | 4 Sep 2026 | 11 files, 2,333 lines | ~$1.00-1.40 | Long-form explanation video with engagement enforced by a linter |
| [`virality-research`](.claude/skills/virality-research/SKILL.md) | 10 Sep 2026 | 8 files, 1,388 lines | $0 | Live web harvest of why video travels, graded by evidence quality, gated so every finding is applied or refused on the record |

All four are authored by Avesh Mishra.

---

## `ai-news-reel`

> Produce a 15-25s vertical AI/tech-news explainer Reel (1080x1920) with
> narration, music, and story-driven motion graphics, rendered locally via
> HyperFrames.

Give it a topic, article link, or raw notes and it researches, scripts,
narrates, animates, renders and self-reviews end to end for roughly **$0.03**.

Also ships an autonomous agent of the same name, so a Reel can be produced
without stage-by-stage supervision.

**Triggers:** "make a reel about X", "turn this article into a video",
"AI news short", "optimalgradient video".

**History** - eight commits, largely findings folded back in after real runs:

| Commit | What it added |
|---|---|
| `0971987` | Initial skill + agent |
| `7f7986b` | Fixed monotone narration - `eleven-v3` with emotion tags |
| `68828f6` | Recorded a second device set |
| `3e63299` | Brand contract; captions, logos, receipts, plates, sound |
| `2c3fc03` | Reference imagery only - cut generated plates |
| `b73d5d1` | Lead with the hero; reference harvesting on any URL |
| `5f5b3bd` | Three generality bugs found testing a Hugging Face model card |
| `9bd0515` | Reel covers |

The measured voice finding here (`eleven-v3` plus inline emotion tags reaches
4.49 semitones of pitch variation against v2 knob-tuning's 3.77) is the basis
for the narration methodology the other video skills follow.

---

## `paper-brief-reel`

> Production-grade vertical tech-news Reel in the "paper brief" editorial design
> language - cream press stock, technical-manual spec cards, real brand logos,
> and AI-generated footage matted in as photographic plates.

The premium counterpart to `ai-news-reel`. Accepts a topic, article links and
reference images. **~$2-4 per video** (Seedance 2.0 plates), so it is a
deliberate choice rather than the default.

**Triggers:** "paper brief video", "spec sheet reel", "editorial tech video",
"make a video with the product logos".

**History:** `3d02556` (initial), `b959ff3` (corrected cost figures, recorded
run findings), `72c7738` (two-sheet format, findings from NO. 03).

---

## `save-to-icloud`

> Copy a finished reel's video and cover images from `projects/<slug>/renders`
> into iCloud Drive so they are on the phone for posting.

Verifies each copy **by hash** and reports whether the iCloud client is actually
running - the failure mode it exists to catch is a copy that appears to succeed
while iCloud is not syncing.

**Triggers:** "save to icloud", "put the video on my phone", "sync the reel to
icloud", "send the final to icloud".

**History:** `9bd0515`, alongside the reel-covers work.

---

## `engaging-explainer`

> An explanation video - any subject, any length from 60 seconds to 10+ minutes
> - that people watch to the end.

The premise is that structure, timing and visual attention events are
**constraints a linter enforces**, not decisions left to whoever is writing that
day. `retention_lint.py` runs at the scene_plan gate - the last free moment
before the pipeline starts spending - and fails on a slow open, a missing
attention event, a redundant caption, no engineered peak, a detail revealed
during motion, or an interrupt gap that is too long.

Adapts across subject, runtime (60s to 10+ min), format (concept piece,
primary-source reading, news analysis, tutorial, video essay), audience and
register. **The open does not scale:** cold open at 0:03 and turn by 0:12 are
absolute facts about attention, identical in a 60-second short and a 15-minute
essay. Only the middle stretches.

**Triggers:** "make an explainer about X", "explain X in a video", "YouTube
explainer", "teach X visually", "video essay", "break down this
paper/article/launch".

### Layout

| Path | What it is |
|---|---|
| `SKILL.md` | Entry point, beat map, runtime scaling table |
| `reference/engagement-model.md` | The measured research the format rests on |
| `reference/device-catalog.md` | Story shape to signature device, so episodes diverge |
| `reference/visual-system.md` | Weights, camera, grain, timing families, freeze device |
| `reference/imagery.md` | Treating external assets so they join a drawn world |
| `reference/production-pipeline.md` | The build: narration, staging, render, verification, costs |
| `reference/composition-scaffold.md` | File architecture; what carries forward vs. gets rewritten |
| `retention_lint.py` | The pre-render gate - 12 checks |
| `scripts/find_beats.py` | Locates beats in the measured read; explains its own misses |
| `scripts/build_captions.py` | Sentence-first caption chunker plus `.srt` |
| `scripts/verify_render.py` | Probes the container and re-transcribes the *rendered* audio |

**History:** `5da28cf`.

> **Status: on branch `skill/engaging-explainer`, not merged to `main` and not
> pushed.** Merge with
> `git checkout main && git merge --ff-only skill/engaging-explainer`.

### Episodes produced with it

Three, none tracked in git (`projects/` is gitignored):

| Episode | Length | Cost |
|---|---|---|
| How transformers work | 58s | $0.07 |
| What is an agentic harness | 4:43 | $0.43 |
| Fable 5.1 / Mythos 5.1 - "one model, two doors" | 3:59 | $2.49 |

---

## Not authored here

**Committed under our name but generated by a third-party tool.** The six
`openspec-*` skills arrived in `7840dcd "v1"` (31 Aug 2026). Their frontmatter
reads `author: openspec`, `generatedBy: 1.11.0`, MIT - output of the OpenSpec
CLI, committed rather than written.

**Upstream, from the fork:**

- ~51 skills from `a3e735c`, the OpenMontage initial release (calesthio,
  29 Mar 2026): the `threejs-*` set, `vercel-*`, `manim*`, `remotion*`,
  `elevenlabs`, `heygen`, `video-*`, and the rest.
- `azure-speech-to-text` and `azure-text-to-speech` - amartya-dev, Jul 2026.
- The whole `skills/` library: `core/`, `creative/`, `meta/`, `pipelines/`.
- `.claude/commands/` - `ink-art.md`, `animated-drawing.md`, `backlot.md`
  (calesthio, Jun-Jul 2026). These are commands, not skills, though they
  surface alongside skills.

---

## Keeping this current

Regenerate the authorship split with:

```bash
for d in .claude/skills/*/; do
  git log --diff-filter=A --format='%an|%ad' --date=short --reverse -- "$d" \
    | head -1 | awk -F'|' -v n="$(basename $d)" '{printf "%-26s %-14s %s\n", n, $1, $2}'
done | sort -k2
```

`--diff-filter=A` with `--reverse | head -1` gives the commit that genuinely
created a skill. Without `--reverse` you get the most recent commit that added
any file to it, which misattributes anything later extended.
