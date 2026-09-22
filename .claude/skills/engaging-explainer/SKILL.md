---
name: engaging-explainer
description: Produce an explanation video — any subject, any length from 60 seconds to 10+ minutes — that people watch to the end. Derives a fresh visual language per topic, keys every beat to the measured narration, and enforces engagement mechanically with a retention linter instead of relying on taste. Renders locally via Remotion; narration is the only real cost. Triggers include "make an explainer about X", "explain X in a video", "YouTube explainer", "teach X visually", "video essay", "break down this paper/article/launch", "engaging explainer video".
---

# Engaging Explainer

Turns any subject into an explanation video that holds attention — not by being
pretty, but by being **built on measured engagement psychology and checked
mechanically before render.**

The difference between this and a generic animated explainer is that structure,
timing and visual attention events are **constraints the linter enforces**, not
decisions left to whoever is writing that day.

> **Read [`reference/engagement-model.md`](reference/engagement-model.md) before
> writing a single line of script.** It is the research the whole format rests
> on, and several of its findings are counterintuitive enough that you WILL get
> them wrong from instinct. In particular: large curiosity gaps produce *low*
> curiosity, and on-screen text duplicating narration measurably *hurts*
> comprehension (d = 0.87).

## What this adapts to

The engagement structure is invariant. Everything else is derived per job.

| Dimension | Range | What changes |
|---|---|---|
| **Subject** | anything explicable | research depth, angle, signature device |
| **Length** | 60s – 10+ min | act count, interrupt cadence, peak position |
| **Format** | concept explainer, primary-source reading, news analysis, tutorial, video essay, product teardown | evidence type, register, citation weight |
| **Audience** | general → specialist | vocabulary ceiling, gap sizing, how much is assumed |
| **Register** | warm, urgent, institutional, playful | arousal dial, palette temperature, motion family |

A concept piece and a document reading are the *same machine* with different
inputs: the concept piece earns its authority from a well-built diagram, the
document reading from citation and restraint. Both still need a turn by 0:12 and
exactly one peak.

## Inputs

| Input | Example | What it drives |
|---|---|---|
| Topic | "how transformers work" | Research, angle, device selection |
| Audience | "non-technical", "engineers" | Vocabulary ceiling, gap sizing |
| Duration | "5 minutes" | Beat map scaling |
| Register hint | "warm", "urgent", "playful" | Arousal dial, palette, motion family |
| Reference links | article URLs, PDFs | Primary sources for claims |

Missing inputs are not a blocker. With only a topic, research it and choose the
angle yourself. Ask only when the request is genuinely ambiguous about *what
story to tell*.

## The pipeline

Run through `animated-explainer` (`pipeline_defs/animated-explainer.yaml`) and
obey Rule Zero — the stage gates still apply. This skill supplies the
**creative contract** for the idea, script, scene_plan and compose stages, and
[`reference/production-pipeline.md`](reference/production-pipeline.md) supplies
the **build contract** for everything downstream of the script.

```
research → proposal → script → narration → beats → scene_plan → [LINT] → assets → author → frames → render → verify
                                  $$        free      free       free      $      free     free     free    free
```

**Narration comes before the scene plan.** Every visual beat keys off real word
timings, so generating audio first is what makes the plan authorable in one pass
instead of two.

## 1. Derive the visual language from the topic — never reuse the last one

Read [`reference/device-catalog.md`](reference/device-catalog.md). It maps
**story shape → signature device**, and it exists so that two videos on
different topics cannot look the same.

Three things get derived per topic, and all three must be written into
`production_plan.art_direction` before authoring:

1. **Semantic palette** — a ground, an ink, and **exactly two accents with fixed
   meanings** carried through the whole piece. Colour must encode a concept, not
   decorate. (3Blue1Brown and Kurzgesagt both do this; it is why their videos
   feel authored rather than assembled.)
2. **Type pairing** — one face for spoken statements, one for machine/annotation
   text. The split must be *semantic*, so the viewer learns the rule without
   being told.
3. **Signature device** — from the catalog, matched to story shape, and used in
   **2-4 beats, not every scene.**

**Hard rule:** if the piece would look like the previous one, change the device.
Series identity comes from structure, pacing and voice — never from re-skinning
one look.

## 2. Write to the beat map, not to the topic

The structure is fixed by research; only its content varies. See
`reference/engagement-model.md` §Beat Map.

| Slot | Window | Job |
|---|---|---|
| COLD OPEN | 0:00–0:03 | One arresting frame. Motion **starts** here. |
| SEED | 0:03–0:08 | Give the viewer the knowledge the gap needs. |
| GAP | 0:08–0:12 | Name what's missing — small and closable. |
| TURN | by 0:12 | A **qualitative** motion event: something starts or stops. |
| ACTS | to ~75% | Interrupt every 10–20s early, widening to 25–40s. |
| PEAK | 66–86% | The single engineered maximum. One only. |
| END | last 8s | Strong. The last frame is half of what gets remembered. |

### Scaling by runtime

**The open does not scale.** Cold open at 0:03 and turn by 0:12 are absolute
facts about human attention, identical in a 60-second short and a 15-minute
essay. Only the middle stretches.

| Runtime | Acts | Interrupt cadence | Peak lands | End beat |
|---|---|---|---|---|
| 60 s | 2–3 | 8–15 s throughout | 0:40–0:52 | last 6 s |
| 3 min | 3–4 | 10–20 s | 1:59–2:35 | last 8 s |
| 5 min | 5 | 10–20 s → 25–40 s after 3:00 | 3:18–4:18 | last 8 s |
| 10 min | 6–8 | 10–20 s → 30–45 s after 3:00 | 6:36–8:36 | last 10 s |

The linter already encodes this: absolute thresholds for the open, a
percentage-based peak window, and a cadence that widens after the three-minute
mark.

**The most common failure is a slow open.** If your turn lands after 0:15, the
structure is wrong — no amount of visual polish recovers it.

## 3. Author with the visual system

Read [`reference/visual-system.md`](reference/visual-system.md) for the craft
layer: line-weight hierarchy, camera scale range, ground grain, the three timing
families, the type ramp, and the **freeze device**.

Read [`reference/motion-craft.md`](reference/motion-craft.md) for the layer that
decides whether any of it is worth looking at: the **camera rig**, **depth
planes**, **light**, **matter continuity**, the **life layer** and **kinetic
type** — all shipped as working code in [`engine/`](engine/).

Pick a **visual register** per topic, next to the palette and the device:

```ts
const craft = craftFor("austere" | "measured" | "rich" | "lush");
```

It scales craft and never information. `austere` is not `inert` — even at the
lowest setting the camera moves, the world has depth and the ground is lit.

Read [`reference/composition-scaffold.md`](reference/composition-scaffold.md)
for the file architecture — and specifically for **which components carry
forward and which must be rewritten.** Reusing the wrong half is how a series
turns into one template in different colours.

## 4. Lint before you render

```bash
python .claude/skills/engaging-explainer/retention_lint.py <project-slug>
python .claude/skills/engaging-explainer/craft_lint.py     <project-slug>
```

**Both.** The first checks whether the piece is structured to hold attention;
the second whether it is built to be worth looking at. Running only the first is
how episode 3 passed every engagement check on its first run while holding one
camera position for 239 seconds, on one plane, with 111 opacity gates against
10 transforms. Structure passing is not the same as being worth watching.

`craft_lint.py` reads the **composition source**, not a declaration, because the
defect it exists to catch is a composition that quietly ignores what the plan
promised.

`retention_lint.py` reads `artifacts/script.json`, `artifacts/scene_plan.json` and
`artifacts/beats.json` and fails on structural engagement defects — a slow open,
a missing attention event, a redundant caption, no engineered peak, a detail
revealed during motion, an interrupt gap that is too long.

**Run it at the scene_plan gate, before the assets stage spends anything.**
Fix every ERROR. WARNINGs are judgement calls — resolve them deliberately and
say so at the gate.

The linter needs four fields on each scene in `scene_plan.json`:

```json
{
  "attention_event": "onset" | "cessation" | "freeze" | "none",
  "still_window": true,
  "peak": false,
  "display_text": ["ANY ON-SCREEN TEXT", "one entry per element"]
}
```

It also needs `text` + `start_seconds` + `end_seconds` on each **script**
section, written from the measured read. Without them the redundancy check has
nothing to compare and would pass vacuously; it now errors instead. See
`production-pipeline.md` §2.

Populate all of it honestly. The lint is only as good as the declaration.

## 5. Narration

Follow the `ai-news-reel` voice methodology exactly — it is measured, not
opinion:

- Route through `tts_selector`, never a provider tool directly, unless a gateway
  failure has been diagnosed and the direct route explicitly approved.
- **`eleven-v3` with inline emotion tags.** v2 knob-tuning does essentially
  nothing to pitch variation (3.92 → 3.77 semitones measured); v3 + tags reaches
  4.49. Under ~3 semitones reads monotone.
- Tag the **turns**, not every line. Match tag valence to the arousal dial.
- **v3 has no SSML.** `<break>` tags are stripped. Chunk by act and restore the
  scored holds in post with `ffmpeg apad`.
- **Then `transcriber` for word-level timestamps.** Every visual beat keys off
  real timings. Never guess when a sentence lands — at five minutes, drift that
  is invisible in a 20-second reel becomes a visible sync failure.

**Measure the read; do not trust a WPM table.** A well-tagged `eleven_v3` voice
runs ~164 WPM, not the ~145 usually assumed — a 13% overshoot that cost one
episode 37 seconds against its script estimate.

Cost: **~$1.00–1.40** for a 4–5 minute read at ElevenLabs' direct rate of
$0.0003/char. The fal.ai gateway is cheaper (~$0.40) but is tier-gated on some
accounts — verify before quoting a number. Everything else is free.

## 6. Verify

Post-render, run the self-review against **the file that ships**:

```bash
python .claude/skills/engaging-explainer/scripts/verify_render.py <slug>
```

It probes the container, re-transcribes the rendered audio, and re-locates
anchor phrases including the peak. Rendering from correct props is not evidence
of a correct render.

Then the distinctness check:

> Could this be any other topic's video with the title swapped? Does it reuse a
> look from a previous one?

If either is yes, the art direction failed.

## Reach — the other half

This skill optimises for **being watched to the end**. It says nothing about
whether anyone arrives, or passes it on. For anything posted publicly, pair it
with [`virality-research`](../virality-research/SKILL.md), which harvests that
question live and gates on it.

The division of authority is fixed, so the two cannot fight:

> **Structure follows this skill. Metadata follows that one.**

Three things carry across from its corpus and are worth knowing before you write:

- **Arousal, not valence, drives sharing** — and low-arousal registers
  measurably travel less, controlling for interest and usefulness. That is the
  same finding behind this skill's arousal dial, and it argues for exactly what
  the beat map already asks: keep the piece calm and spend the whole budget on
  the single engineered peak.
- **Practically useful content is shared more**, independently of emotion. Give
  the viewer one thing they can repeat. In an explainer the peak is usually also
  the share trigger — if it is genuinely the most surprising thing in the piece,
  it is what gets pasted into a group chat with a timestamp.
- **Almost all sharing cascades die after one hop.** Reach is not engineerable
  for a single piece. Design the one deliberate share instead.

Its gate refuses to let a finding change what is true, what the piece argues, or
whether the title is honest — a title the piece does not deliver produces the
early drop-off that everything here is built to prevent.

## Anti-patterns

- **Opening on a definition.** Definitions are large gaps. Large gaps kill curiosity.
- **Captions that repeat the narration verbatim** while also carrying display text.
- **Gradual ramps as attention events.** Acceleration does not capture attention; starting and stopping do.
- **Two or three medium peaks** instead of one large one.
- **A quiet fade-out ending.** The end is half of what the viewer remembers.
- **Calm as a default register.** Low-arousal content measurably does not spread. Calm is a *choice* with a cost — make it knowingly.
- **A locked camera**, or a push under 1.4x, which amounts to the same thing.
- **Everything on one plane**, then wondering why the push reads as a zoom.
- **Crossfading two states that share matter** instead of transforming one into the other.
- **Secondary motion on a figure as it lands.** Wobble the frame, never the number.
- **Turning the intensity dial up and the information density up together.** That
  is the actual coherence violation, and the only one here that measurably costs
  comprehension.
- **Hand-written timestamps** anywhere in the composition.
- **Scaling type vertically** to compress a chart — it becomes an illegible smear.
- Architecture diagrams, boxes-and-arrows, robot imagery, glowing brains.
- Re-skinning the previous video's look.

## Files

| File | What it is |
|---|---|
| `reference/engagement-model.md` | The research, the beat map, the rules that follow from it |
| `reference/device-catalog.md` | Story shape → signature device, so videos diverge |
| `reference/visual-system.md` | Craft mechanics: weights, camera, grain, timing, type, freeze |
| `reference/imagery.md` | How photos, plates and clips join a drawn world without looking glued on |
| `reference/production-pipeline.md` | The build: narration, staging, render, verification, costs |
| `reference/composition-scaffold.md` | File architecture, and what carries forward vs. gets rewritten |
| `reference/motion-craft.md` | Camera, depth, light, matter continuity, the life layer, kinetic type |
| `engine/intensity.ts` | The visual register dial — austere / measured / rich / lush |
| `engine/camera.ts` | Camera rig, shot list, parallax transforms |
| `engine/depth.tsx` | `<Plane>` / `<Foreground>` and contrast falloff by distance |
| `engine/light.tsx` | `<KeyLight>`, `<Vignette>`, `<Grain>`, `glow()` |
| `engine/motion.ts` | overshoot, settle, anticipate, stagger, `becomes()`, `handover()` |
| `engine/kinetic.tsx` | `<KineticText>`, `<Wipe>`, `<Counter>` |
| `retention_lint.py` | The structural gate |
| `craft_lint.py` | The visual gate |
| `scripts/find_beats.py` | Locate beats in the measured read; explains its own misses |
| `scripts/build_captions.py` | Sentence-first caption chunker + `.srt` |
| `scripts/verify_render.py` | Post-render probe + re-transcribe sync check |

## Imagery

Default to **drawing it**. When a photograph, generated plate or video clip
genuinely earns its place, read
[`reference/imagery.md`](reference/imagery.md) first.

The rule that governs everything there: **no external asset ever appears
untreated.** Every one passes through duotone / halftone / lineart / posterize
so it is remapped onto the piece's palette and surface — all SVG filters, all
$0. A raw photo in a drafted world reads as two unrelated pieces glued together,
and that single mismatch is the most common reason an explainer looks cheap.

Decide `evidence_type` at proposal (see `device-catalog.md`) — it settles
*whether* imagery belongs before anyone decides *what* to source. Abstract
mechanisms and data get drawn; real-world referents and archival material earn
photography.

Cheapest paths: **Unsplash (free)**, then **`recraft_image` at $0.04 for actual
SVG** — vector output that belongs natively and needs no treatment. For video,
`kling_video` at $0.10/5s is the only one that fits a minimal budget; Veo is
20× that. Both video providers are tier-gated on some accounts: when a clip is
unavailable, take the declared fallback and say so rather than silently
substituting a pricier generator.
