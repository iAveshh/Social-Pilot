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

### 5. Get real timings + captions (free, and non-negotiable)
Do **not** guess when sentences land. `transcriber` (local faster-whisper, no
API cost) gives **word-level** timestamps — richer than silence detection and
the source for captions too:

```python
transcriber: {'input_path': 'projects/<slug>/assets/audio/narration_full.mp3',
              'model_size': 'base', 'language': 'en',
              'output_dir': 'projects/<slug>/artifacts'}
```
If it reports unavailable, `pip install faster-whisper` once — free and local.
Fallback if you truly can't: `ffmpeg -af "silencedetect=noise=-32dB:d=0.22"`
gives sentence gaps only.

Add the audio's `data-start` offset to convert to composition time. Every visual
beat keys off these numbers — it's what makes the motion feel authored.

### 5b. Captions (free, and the biggest engagement win available)
Most Reel viewing is muted. A reel with no captions is a reel most viewers watch
with the script missing.

`reference/build-captions-and-sfx.py` turns the transcript into 2-3 word chunks
and writes `artifacts/captions.json`, then emits one timed clip per chunk (all
on a single track — they never overlap). Styling and the rules that stop
captions reading as gibberish are in `../brand.md`; the one that bites is:

> A chunk may never open on `%`, `.6` or a bare stub. Peek at the next token
> before closing a chunk — "BUGS 2" / ".6" shipped into a render before this
> rule existed.

Correct whisper's mis-joins by hand ("cyberversion" → "cyber version"). These
are designed on-screen text, not a transcript.

### 5c. Sound design (free)
No SFX tool is wrapped in this repo, so the beats are voiced with
ffmpeg-synthesised UI cues — which suit a terminal aesthetic better than real
foley anyway. Recipes and the mixing gotcha (**a sparse `amix` lands near
-30 dBFS; boost ~+24 dB and limit**) are in `../brand.md`. Same script builds
the bed.

Put a cue on every beat the eye already registers: each chip landing, the
rupture, each bar filling, the gate closing. Ride it at `volume: 0.55`.

### 6. Music (free)
Try free search first — it has consistently beaten paying:
```python
pixabay_music: {'query': '<mood> technology', 'min_duration': 20,
                'max_duration': 60, 'output_path': 'projects/<slug>/assets/music/bed.mp3'}
```
Only fall back to `fal_elevenlabs_music` ($0.80/track) if nothing fits. Bed sits
at `volume: 0.22` under narration, ducking to 0 over the last second.

### 6b. Grounding: logos, receipts, plates
Read `../brand.md` first — it governs all three, and getting them wrong is what
makes a series look generic.

- **Logos (free).** Real vector marks via simple-icons, monochrome, in a
  bordered chip. When the story names a product, show its mark.
- **Receipts (free).** `node reference/receipt.mjs <url> <out.png> [clipHeight]`
  screenshots the actual source page. Crop to the headline block, mat it, label
  it `SOURCE / <domain>`. Leave it bright against the dark ground — it reads as
  holding up the document. Nothing else buys this much credibility for $0.
- **Image plates (paid, ~$0.04-0.05 each).** `image_selector` against the brand
  image spine, one per act at most, always matted. Six stills beat one video
  clip at this budget.

Keep them sparse. This format is strong *because* it's designed — plates are
punctuation, never wallpaper.

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

Costs are written as `USD n.nn` — a bare dollar-sign before a digit gets eaten
by argument substitution when a skill is invoked with arguments.

| Line | Typical |
|---|---|
| Narration, `eleven-v3` (35-45 words) | USD 0.03 |
| Music (free search) | USD 0.00 |
| Captions, logos, receipts, SFX (all local) | USD 0.00 |
| Image plates, `image_selector` | USD 0.04-0.05 each |
| Motion graphics + render (local) | USD 0.00 |

**Two tiers, both real:**

- **Lean — ~USD 0.03.** Narration + free music + vector devices. Add captions,
  logos, receipts and SFX and it is *still* USD 0.03, because all four are free.
  That combination is most of the quality.
- **Full — ~USD 0.20-0.35.** The above plus 3-6 matted image plates.

The budget is rarely the constraint here. **Spend the free wins first** — a reel
with captions, a real vendor mark, a source receipt and sound design beats one
with three AI images and none of those. Video generation stays out of this
format: one 5s clip costs more than six stills and buys less.

## Hard-won gotchas

Read `reference/gotchas.md` before authoring the composition. It documents the
bugs this format has actually hit — the `.clip` height trap, cold-seek
invisibility, tween overlap, ticker/headline collisions, and the `validate`
hang. Each cost a render cycle to find.

Two more from the captions/plates build:

- **An exit tween that lands exactly on the *next* clip's start boundary needs
  its own hard kill** at that timestamp — not at the fading clip's own end.
  Lint names the exact time; use it verbatim.
- **`amix` of sparse SFX cues comes out around -30 dBFS.** Boost ~+24 dB and
  limit, or the sound design is inaudible under narration and you will not
  notice until you play the render.

## Reference files

| File | What it is |
|---|---|
| `../brand.md` | **Read first.** Palette, type, logo/image/caption/sound contract shared with `paper-brief-reel`. |
| `reference/composition-template.html` | Build 1 — sandbox rupture + incident chain |
| `reference/devices-example.html` | Build 2 — release chips, price flip, racing bars, gate |
| `reference/full-stack-example.html` | Build 3 — everything: captions, logo chip, receipt, matted plates, SFX bed |
| `reference/build-captions-and-sfx.py` | Transcript → caption chunks; synthesises + mixes the SFX bed |
| `reference/receipt.mjs` | `node receipt.mjs <url> <out.png> [clipH]` — source-page capture |
| `reference/measure-pitch.py` | Compare narration takes for monotone (F0 semitone variation) |
| `reference/gotchas.md` | Ten failure modes, each one a lost render cycle |

## Quality bar

Before delivering, confirm:
- [ ] Every claim traces to a real source
- [ ] Visual beats land on the measured narration timings, not guesses
- [ ] Act 2's indicator lights each stage as it's named
- [ ] The diagram device differs from the previous video in the series
- [ ] `check` passed 0 errors; frames visually reviewed
- [ ] Runtime 15-25s, no dead air after narration ends (max ~2.5s tail)
- [ ] Text legible at phone size — nothing under ~24px, contrast passes AA
