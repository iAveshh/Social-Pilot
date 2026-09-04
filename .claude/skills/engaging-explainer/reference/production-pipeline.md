# Production pipeline

The creative layer is in the other four references. This one is the build: how
an approved scene plan becomes a verified file, and the specific places that
process bites.

Everything here was paid for in wasted time or money at least once.

---

## The order, and why it is this order

```
narration  →  measure  →  beats  →  scene_plan  →  LINT  →  assets  →  author  →  frames  →  render  →  verify
   $$          free       free       free         free      $        free      free       free      free
```

Narration comes **first**, before the scene plan, because every visual beat keys
off real word timings. Reversing these two means authoring against estimates and
re-timing everything afterwards.

The lint sits before `assets` because that is the last free moment. After it,
you are spending.

---

## 1. Narration: measure the voice, never assume it

**Do not trust a words-per-minute estimate.** The common ~145 WPM figure is not
what a warm, well-tagged read actually does.

| | assumed | measured |
|---|---|---|
| ElevenLabs `eleven_v3`, voice "George", speed 0.98 | 145 WPM | **~164 WPM** |
| 646-word script | 276 s | **239 s** |

That is a 13% overshoot — over four minutes, ~37 seconds. Write the script, then
**generate and measure before planning a single scene.** If the delivered length
matters, iterate on word count against the measured rate, not against a table.

### Cost, from actual invoices

ElevenLabs bills **$0.0003 per character**, direct. A 3,500-character read
(~4 minutes) is **~$1.05**. Budget the whole episode at **$1.00–1.40** for a
4–5 minute read; everything else in the pipeline is free.

> Earlier guidance in this skill claimed ~$0.40 via the fal.ai gateway. On a
> gated account the gateway 403s every ElevenLabs TTS model, so the direct rate
> is the one to plan against. Confirm before quoting a number to the user.

### Provider 403s — diagnose before retrying

A 403 from fal.ai usually means **a tier-gated variant or parameter**, not an
outage and not a rate limit. It does not return 429 or 402, and the message
names only the URL.

Confirmed cases:

- `output_format: "mp3_44100_192"` → 403 every time. `mp3_44100_128` or omitting
  the field → succeeds.
- `kling-video` `v3/standard` **and** `v2.1/standard` → 403, $0.00 charged.

**Protocol, in order:**

1. Diff the failing call's parameters against the last successful one.
2. Test the cheapest differing parameter in isolation, with the shortest input
   that can possibly work.
3. Only then consider capacity.

Retry loops with exponential backoff cannot clear a tier gate. They just spend
money — chasing outage → length-limit → throttling hypotheses with long probes
cost **$1.25** on one episode, more than the narration it was debugging.

### Character limits and scored pauses

`eleven_v3` enforces a per-request character limit (~1,200 is safe; 3,467 was
refused). Chunk the read **by act**, then assemble.

This turns out better than one long request: `eleven_v3` and `multilingual_v2`
**do not support SSML**, so `<break>` tags are stripped and every scored pause is
lost. Generating per section lets you put the holds back exactly, in post:

```bash
ffmpeg -i s1.mp3 -af "apad=pad_dur=0.6" ...   # the hold the peak depends on
```

Keep one voice, one settings block, and assemble in order — prosodic continuity
survives chunking; it does not survive re-tuning between chunks.

---

## 2. Transcribe, then enrich the script

Run `transcriber` on the **assembled** master, not the parts.

Then write the measured timings and plain text back onto each script section:

```json
{ "id": "s2", "text": "Now the model itself did get better...",
  "start_seconds": 36.153, "end_seconds": 91.171 }
```

**This is not optional bookkeeping.** `retention_lint.py` reads
`sec['text']` and `sec['start_seconds']`/`['end_seconds']` to run the redundancy
check. Without them the check compares against an empty word list for every
scene past the first couple of seconds, finds nothing, and reports **OK** while
having examined nothing — the largest measured harm in the model (d = 0.87)
silently unchecked. The linter now errors instead of passing vacuously, but the
fix is upstream: enrich the script.

On one episode, enriching it immediately surfaced four collisions that were
already written into the scene plan.

---

## 3. Beats

```bash
python .claude/skills/engaging-explainer/scripts/find_beats.py <slug>
```

Write `artifacts/beat_spec.json` as a phrase map; the script locates each phrase
in the real word stream and reports what was *actually said* when a phrase
misses, so fixing it takes a minute rather than a transcript dump.

Two ASR behaviours break naive matching, and both are handled for you:

- **numerals are written as digits and split across tokens** — `24.7%` arrives as
  `' 24'` + `'.7'` + `'%'`. Write `"scored 247"` in the spec, or just let the
  miss-context tell you.
- **punctuation-only tokens** normalise to nothing and must be dropped.

Never hand-write a timestamp.

---

## 4. Scene plan, then lint

Declare all four lint fields on **every** scene, honestly:
`attention_event`, `still_window`, `peak`, `display_text`.

```bash
python .claude/skills/engaging-explainer/retention_lint.py <slug>
```

Fix every ERROR before spending. Notes from real runs:

- **`visual_velocity` is the hard one.** Act 1 typically needs 10–13 scenes in
  its first 30 seconds to keep every gap under 3s. That is not padding — each
  one is a genuine state change in a continuous diagram.
- **`peak` position uses `start_seconds / total`.** If the peak scene starts
  slightly before the 66% line, split it so the scene *begins* on the peak
  moment rather than leading into it.
- **`display_text` with any digit forces `still_window: true`.** Design the
  animation so figures land after motion settles; that is the correct fix, not
  a relaxed declaration.
- **Write display text that carries *different* information from the narration**
  — a derived figure, a citation, a label — rather than an echo of the sentence
  being spoken.

---

## 5. Authoring and staging (Remotion atelier)

See [`composition-scaffold.md`](composition-scaffold.md) for the file layout.
The mechanics that are easy to get wrong:

**Staging is a COPY, not a symlink.** Remotion's webpack resolves modules by
walking up from the entry's *real* path, so a junction or symlink dereferences
straight out of the composer tree and `node_modules` disappears. `video_compose`
copies `.tsx`/`.ts` into `remotion-composer/projects/<slug>/` for exactly this
reason. Do not "help" by creating a link.

> If you already tried a symlink, **clear `remotion-composer/node_modules/.cache`**.
> The stale bundle keeps resolving the old real path and the error looks
> identical after you fix the staging.

**Props are passed, never imported.** Only `.tsx`/`.ts` are staged, so
`import props from "./props.json"` will not resolve. Pass `--props=<abs path>`
and read them from the component's props.

**Use `staticFile()` for images, not just audio.** A bare relative `src` on
`<Img>` resolves against the render page's base URL and fails with
`Error loading image with src: ...` — while audio from the same public dir loads
fine, which makes it look like an asset problem rather than an API one.

**Route with `operation: "render"`.** The atelier branch lives in the high-level
handler; `operation: "compose"` is the low-level concat path and will reject you
with `No cuts in edit_decisions`.

```python
registry._tools["video_compose"].execute({
    "operation": "render",
    "output_path": str(OUT),
    "edit_decisions": {
        "composition_mode": "atelier",
        "render_runtime": "remotion",          # required; never defaulted
        "bespoke": {
            "entry": "projects/<slug>/index.tsx",
            "composition_id": "<CompId>",
            "props_path": str(ART / "props.json"),
            "public_dir": str(PROJ / "public"),
            "crf": 18,
        },
    },
})
```

Keep a **small per-project `public/`** (`audio/`, `music/`, `imagery/`) and point
`--public-dir` at it rather than the bloated shared one.

---

## 6. Check frames before rendering four minutes

```bash
npx remotion still <entry> <CompId> out.png --frame=N --props=... --public-dir=... --scale=0.5
```

Pull one still per act plus the peak. On one episode this caught four real
defects in a single pass — a shape that never faded and merged with the diagram
in front of it, a vertical squash that turned every label into an illegible
smear, a headline sitting on top of the scale it was annotating, and both
imagery plates throwing at render.

All four would otherwise have surfaced after a full render, or worse, not at all.

A `--frames=0-60` draft render is also worth one minute before the real one: it
proves bundling, props, fonts and audio wiring in one shot.

---

## 7. Verify the file that ships

```bash
python .claude/skills/engaging-explainer/scripts/verify_render.py <slug>
```

Probes the container, then **re-transcribes the rendered audio** and re-locates
anchor phrases — including the declared peak — against the planned timeline.

Rendering from correct props is not evidence of a correct render. Frame-rate
rounding, an audio pad, a filter resample or a muxer offset each produce a file
whose sync differs from the timeline you authored, and none of them are visible
until someone watches it. Checking the source narration proves nothing about the
artefact you are about to publish.

Then the distinctness check from `SKILL.md` §6.

---

## Cost reference

| Item | Cost | Note |
|---|---|---|
| Narration, 4–5 min, ElevenLabs direct | **$1.00–1.40** | $0.0003/char |
| Narration via fal.ai gateway | ~$0.40 | **often gated — verify before quoting** |
| `transcriber` (local whisper) | $0.00 | non-negotiable, drives every beat |
| Unsplash photography | $0.00 | treated; see `imagery.md` |
| `recraft_image` (real SVG) | $0.04 | belongs natively, needs no treatment |
| `kling_video` 5s | $0.10 | cheapest clip; **gated on some accounts** |
| `seedance` / `veo` 5s | $1.52 / $2.00 | rarely worth it — treatment erases the fidelity |
| Pixabay music | $0.00 | scraper; a 403 on first call clears on retry |
| Remotion render | $0.00 | local |

**Budget caps are hard stops.** Track cumulative spend against the stated cap and
surface the position *before* the next paid call. When a paid asset turns out to
be unavailable, take the proposal's declared fallback and **say so** — never
silently substitute a pricier provider.
