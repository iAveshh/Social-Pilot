---
name: ai-news-reel
description: Produce a 15-25s vertical AI/tech-news explainer Reel (1080x1920) with narration, music, and story-driven motion graphics, rendered locally via HyperFrames. Give it a topic, article link, or raw notes and it researches, scripts, narrates, animates, renders, and self-reviews end to end for roughly $0.03. Triggers include "make a reel about X", "turn this article into a video", "AI news short", "optimalgradient video".
---

# AI/Tech-News Reel Producer

Turns a topic, link, or pile of notes into a finished vertical Reel in the
"dev-tool telemetry" visual language: dark terminal aesthetic, monospace
diagrams, narration over a music bed, and **motion graphics that enact what the
narration says** rather than decorate it.

Proven reference production: `projects/how-agents-work-reel/` (19.5s, $0.034).

## Inputs

Accept any of these, in any combination:

| Input | Example | What it drives |
|---|---|---|
| Topic | `/ai-news-reel MCP explained` | Research stage finds the angle |
| Article/link | `/ai-news-reel https://...` | Fetch it, use as the primary source |
| Raw notes | pasted text | Use as-is; skip broad research |
| Duration hint | "make it 15s" | Word budget (~2.5 words/sec of narration) |
| Angle hint | "contrarian take" | Steers concept selection |

**Missing inputs are not a blocker.** With only a vague topic, run research and
pick the strongest angle yourself. Only stop to ask if the request is genuinely
ambiguous about *what story to tell*.

## The Format (the reusable spine)

Three acts. This structure is what makes the format work — keep it. The *visual
device* in each act should change per story (see "Vary the visuals" below).

| Act | Narration beat | What the motion does |
|---|---|---|
| **1 — Setup & rupture** | The hook + the surprising turn | Draw a system diagram, populate it, then **break it** on the hook's turn. The viewer watches the claim happen. |
| **2 — Evidence chain** | The specifics: what happened, in order | Build a staged chain/list/chart. A traveling indicator moves through it, **lighting each stage exactly as the narration names it**. End on a critical state (red ring, spike, flashing node). |
| **3 — Resolution** | The takeaway | Assemble the answer visually — elements fly in and lock into place around a core node — then land a short tagline card. |

Reference implementation of all three acts:
`reference/composition-template.html` (the shipped how-agents-work-reel build).
Read it as a **mechanics codex** — the CSS primitives, the tween patterns, the
timing structure — not as a fixed look to re-skin.

### Vary the visuals per story

Per `AGENT_GUIDE.md` atelier doctrine: reuse engine knowledge, never freeze the
creative. Keep the palette family and typographic system so the series reads as
one account, but pick a **diagram device that fits this story**:

| Story shape | Act 1 device | Act 2 device |
|---|---|---|
| Breach / failure | Container that ruptures | Incident chain with a packet |
| Benchmark / comparison | Two labeled nodes side by side | Bars racing / counters ticking |
| Cost / scaling | A small box that grows | Curve climbing against a flat line |
| Protocol / architecture | Nodes + connectors wiring up | Request/response hops along the wires |
| Adoption / survey stat | A grid of dots (population) | Dots filling / splitting into segments |
| Release / pricing | Version chips landing in cadence | The headline number **flipping** to a worse one |
| Gated launch | — | A lock + bordered gate panel that slams shut |

If the new video would look identical to the last one, change the device.

Two built references, deliberately sharing zero devices:

- `reference/composition-template.html` — sandbox container that ruptures, then
  an incident chain with a travelling packet (`how-agents-work-reel`).
- `reference/devices-example.html` — release chips landing in cadence, a price
  that flips `$0.75 → $1.50` in red, four benchmark bars racing with only the
  narrated two in accent, and a lock/gate close (`gemini-flash-reel`).

**The rupture does not have to be a break.** In the second example it is a
number turning against the viewer — same three-act shape, no broken container
anywhere. Look for the turn the story already contains.

## Workflow

Run this end to end. Announce provider/model before the first paid call, then
proceed — do not stop for approval at every stage unless the user asked to review.

### 1. Set up the project
```bash
python -c "from lib.checkpoint import init_project; init_project('<slug>', title='<Title>', pipeline_type='animation')"
python -m backlot open <slug>
```
Slug is kebab-case from the title. The board is an observer — never a blocker.

### 2. Research (free)
Skip if the user supplied the full story. Otherwise 4-8 web searches: the
specific claim, current numbers, what's already been made, and one surprising
data point. **Every factual claim in the script must trace to a source.** Never
invent statistics, dates, or attributions.

Write `research_brief` and checkpoint the `research` stage.

### 3. Script (free)
Word budget = target seconds x 2.5, minus room for holds. For ~20s that's
**35-45 words**. Four beats matching the three acts (Act 2 gets two beats).

Rules:
- Hook under 12 words, states the surprising thing flatly. No hype.
- One idea per beat. Short declarative sentences.
- Name the concrete specifics (dates, numbers, systems) — they're what the
  Act 2 chain will display.
- Close on the takeaway a viewer repeats to someone else.

Write `script` + checkpoint. Include `voice_performance` and per-section
`delivery_cues`.

### 4. Narration (~$0.02)
Route through `tts_selector` — never call a provider tool directly.

```python
{'text': <narration with inline emotion tags>, 'voice_id': 'pNInz6obpgDQGcFmaJgB',
 'model_id': 'eleven-v3', 'stability': 0.35,
 'similarity_boost': 0.75, 'style': 0.6,
 'output_path': 'projects/<slug>/assets/audio/narration_full.mp3'}
```

**Use `eleven-v3` with inline emotion tags — not v2 settings.** Early videos in
this series shipped a flat, monotone read. The fix is *not* the stability/style
knobs; changing them on `eleven_multilingual_v2` does essentially nothing.
Measured across five variants of the same script:

| variant | median pitch | pitch variation | range |
|---|---|---|---|
| v2, "professional" (stability .7 / style .1) | 127 Hz | 3.92 st | 10.41 st |
| v2, "energetic" (stability .35 / style .6) | 133 Hz | 3.77 st | 9.58 st |
| v2, energetic, George voice | 124 Hz | 3.04 st | 6.86 st |
| v3, no tags | 155 Hz | 3.70 st | 9.11 st |
| **v3 + emotion tags** | **157 Hz** | **4.49 st** | **11.25 st** |

Only the model-plus-tags combination moved the needle. Tag the turns, not every
line — `[excited]` on the hook, `[emphatic]` on the number that matters,
`[intrigued]` on the closing catch. Four or five tags in a 40-word script.

Loudness is the wrong thing to measure here: RMS spread was flat across all five
variants. **Monotone is a pitch property**, so measure F0 variation in semitones
(autocorrelation per 40 ms frame, median-normalised). Under ~3 st reads flat;
4+ reads lively.

The writing carries as much as the settings. Fragments and repetition give the
voice something to perform — "Third. In six weeks." lands; a smooth clause does
not.

Keep the voice ID stable across the series so the account sounds like one
person.

### 5. Get real timings (free, and non-negotiable)
Do **not** guess when sentences land. Measure:
```bash
ffmpeg -i projects/<slug>/assets/audio/narration_full.mp3 \
  -af "silencedetect=noise=-32dB:d=0.22" -f null - 2>&1 | grep -E "silence_(start|end)"
```
Each gap is a sentence boundary. Add the audio's `data-start` offset (0.2) to
convert to composition time. Every visual beat keys off these numbers — this is
what makes the motion feel authored rather than approximate.

(`transcriber` gives word-level timings if `faster-whisper` is installed; it
usually isn't, and silence detection is enough.)

### 6. Music (free)
Try free search first — it has consistently beaten paying:
```python
pixabay_music: {'query': '<mood> technology', 'min_duration': 20,
                'max_duration': 60, 'output_path': 'projects/<slug>/assets/music/bed.mp3'}
```
Only fall back to `fal_elevenlabs_music` ($0.80/track) if nothing fits. Bed sits
at `volume: 0.22` under narration, ducking to 0 over the last second.

### 7. Compose (free)
Author `projects/<slug>/hyperframes/index.html` from the template, plus
`hyperframes.json`. Copy audio into `hyperframes/assets/`.

Then, in order — **all three, every time**:
```bash
cd projects/<slug>/hyperframes
npx hyperframes check      # lint + runtime + layout + motion + contrast
npx hyperframes render --quality standard --workers 1
```
`check` must pass with **0 errors** before rendering. Do not render past errors.

> Use `check`, never `validate`. `validate` is deprecated and has hung
> indefinitely in practice; `check` is its superset and returns in ~30s.

### 8. Self-review (mandatory, free)
A green render is not proof. Extract frames at each act's key beat and **look at
them**:
```bash
for t in 1.2 4.8 8.6 11.4 15.9 17.5; do
  ffmpeg -y -ss $t -i renders/<file>.mp4 -frames:v 1 -update 1 /tmp/f_$t.jpg
done
ffmpeg -i <file>.mp4 -af volumedetect -f null -   # mean ~-17dB, max < 0dB
```
Read the frames. Confirm each act shows its intended motion, text is legible,
nothing is off-canvas or invisible. Layout bugs that pass `check` have shipped
before — the frame check is what catches them.

Copy to `projects/<slug>/renders/final.mp4`, write `render_report` +
`final_review`, checkpoint `compose`.

### 9. Deliver
`SendUserFile` the final MP4. Report: runtime, actual cost, what each act does,
any bug found and fixed. Offer a caption + hashtags. Posting happens outside
this repo.

## Cost model

| Line | Typical |
|---|---|
| Narration (35-45 words) | $0.02 |
| Music (free search) | $0.00 |
| Motion graphics + render (local) | $0.00 |
| **Total** | **~$0.03** |

Budget cap for the `animation` pipeline is $2.00 — this format uses ~2% of it.
No image or video generation is needed; if you find yourself reaching for
either, the concept has drifted from this format.

## Hard-won gotchas

Read `reference/gotchas.md` before authoring the composition. It documents the
bugs this format has actually hit — the `.clip` height trap, cold-seek
invisibility, tween overlap, ticker/headline collisions, and the `validate`
hang. Each cost a render cycle to find.

## Quality bar

Before delivering, confirm:
- [ ] Every claim traces to a real source
- [ ] Visual beats land on the measured narration timings, not guesses
- [ ] Act 2's indicator lights each stage as it's named
- [ ] The diagram device differs from the previous video in the series
- [ ] `check` passed 0 errors; frames visually reviewed
- [ ] Runtime 15-25s, no dead air after narration ends (max ~2.5s tail)
- [ ] Text legible at phone size — nothing under ~24px, contrast passes AA
