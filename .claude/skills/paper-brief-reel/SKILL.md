---
name: paper-brief-reel
description: Produce a production-grade vertical tech-news Reel (1080x1920) in the "paper brief" editorial design language — cream press stock, technical-manual spec cards, real brand logos, and AI-generated footage matted in as photographic plates. Accepts a topic, article links, and reference images. Costs roughly $2-4 per video (Seedance 2.0 plates). Triggers include "paper brief video", "spec sheet reel", "editorial tech video", "make a video with the product logos".
---

# Paper Brief Reel

The premium counterpart to `ai-news-reel`. Where that one is dark-terminal and
free, this is **light editorial**: a technical field brief on cream stock, with
real brand marks and generated footage matted into the page as plates.

Reference build: `projects/paper-brief-template/` — read
`reference/composition-template.html` for the working mechanics.

## Inputs

| Input | Handling |
|---|---|
| Topic / article link | Research it; extract the 4 spec-card facts |
| **Reference images** (screenshots, product shots, brand assets) | Feed to image-to-video / reference-to-video conditioning for plates; also usable directly as card figures |
| Brand names mentioned | Source their **real** logos (see Logos below) |
| Duration hint | Default ~15-20s |

References are optional. With them, condition the plates. Without them, write
text-to-video prompts and source logos yourself.

## Design system (do not drift)

```
ground      #efece3   cream press stock (+ subtle tooth texture)
card        #fbf9f3   slightly lighter paper
ink         #16161a   rules, borders, headlines
body        #44444b   captions
annotation  #6a6a70   FIG. NN corner marks  (never lighter — fails AA)
accent      #b0353c   kicker, gauge needle, stamps ONLY — never body text
```

- **Headline:** Inter 800, tight tracking (-0.8 to -1.6px)
- **Everything else:** JetBrains Mono — captions, annotations, folio, stamps
- **Never** add a third font or a second accent color.

### Page anatomy

```
kicker          FIELD BRIEF / NO. NN        (mono, red, wide tracking)
title           2 lines max, 74px, Inter 800
rule            3px full-width ink rule
board           2x2 grid of spec cards, each:
                  ├ 4 separately-drawn border edges
                  ├ FIG. NN (top-left) + CATEGORY (top-right)
                  ├ figure  — line art, logo grid, gauge, stamp, or video plate
                  ├ headline (52px Inter 800, ends in a period)
                  └ caption  (mono, 2 lines max)
folio           SUBJECT ............ SHEET 01 / 01
```

Headlines are **declarative and end in a period** — "One Protocol." "Industry
Default." That full stop is part of the voice.

### Length: one sheet, or two

Four cards carry roughly 20-30s. Past that the camera dwells too long on each
and the piece goes static. **For 45-70s, use two sheets of four.**

Author `#sheet1` and `#sheet2` as siblings absolutely positioned in the *same*
board slot (`.sheet { position:absolute; left:0; top:0 }`, `#sheet2` starting at
`opacity:0`) and cross-fade between them. Every camera stop is then reused
unchanged for the second sheet — no new transform math.

Sell the turn: swap the sheet on a narration line that marks a real pivot in the
story, retitle the masthead, and flip the folio to `SHEET 02 / 02`. Do the swap
**on a wide shot** with the frame furniture visible, so the viewer sees the page
turn rather than a cut. Reference run: `projects/gemini-38-flash-brief/`
(62s, 8 cards, swap at 31.8s on "Then there's the cyber variant").

Card numbering runs straight through both sheets — `FIG. 01` to `FIG. 08`.

## Motion vocabulary

The design is static-looking by nature; these five moves make it move.

| Move | Mechanic |
|---|---|
| **Edge draw-on** | Each card's 4 border divs `scaleX/scaleY` 0→1 in sequence with `transformOrigin` set. Stagger cards 0.22s apart. |
| **Camera push** | The whole board scales/translates between a wide shot and each quadrant. This is the primary engine of engagement — see the math below. |
| **Logo stamp** | Brand marks `scale` 0.55→1 with `back.out(2.2)`, staggered 0.1s. |
| **Needle sweep** | Gauge needle `rotation` -78°→74°, `power2.inOut`. |
| **Stamp slam** | `scale` 2.1→1 + slight `rotation`, `power4.out` — lands like a rubber stamp. |

### Camera-stop math (board 1600x1200, cards 780x580)

With the board anchored at screen (540, 1030) and `transformOrigin` at its
center, a point `p` maps to `boardScreenCenter + (p - boardCenter) * scale`.
Solving for "put card N's center at the frame focus point (540, 950)":

```js
const WIDE = { scale: 0.60, x: 0,      y: 0 };
const C1   = { scale: 1.05, x:  430.5, y:  275.5 };   // top-left
const C2   = { scale: 1.05, x: -430.5, y:  275.5 };   // top-right
const C3   = { scale: 1.05, x:  430.5, y: -375.5 };   // bottom-left
const C4   = { scale: 1.05, x: -430.5, y: -375.5 };   // bottom-right
```
Hold each stop ~2.6s, then return to WIDE for the closing beat.

**Hide the masthead, rule and folio while pushed in** (fade at the first push,
restore on the final pull-back). Otherwise the magnified card covers them and
the layout checker flags occluded text — correctly, it looks wrong.

## Logos — use the real marks

Never let a generator draw a logo; it will be subtly wrong and it's a trademark
problem. Source official vector marks:

```bash
npm install simple-icons@16 --no-save
# icons live in node_modules/simple-icons/icons/<slug>.svg
```
Extract the `<path d="...">` and inline it as
`<svg viewBox="0 0 24 24"><path d="..."/></svg>`, filled with the ink color.
**Copy the path programmatically** — hand-transcribing truncates long paths
(Hugging Face is 2,911 chars) and renders a broken glyph.

> **OpenAI and Microsoft are NOT in simple-icons** — both requested removal.
> For those, use the company's official press-kit SVG, or set the name as a
> bold wordmark in Inter 800. Do not substitute a lookalike.

Verified-present slugs used so far: `anthropic`, `googlegemini`, `huggingface`,
`cursor`, `ollama`, `langchain`, `nvidia`, `perplexity`, `mistralai`, `vercel`,
`docker`, `github`, `replicate`.

## Video plates (the paid layer)

Generated footage sits **inside** a card's figure area, matted with a 3px ink
border and `filter: grayscale(0.35) contrast(1.05)` so it belongs to the paper
palette. Full-bleed AI footage fights this design — don't.

### The root-child constraint (critical)

HyperFrames only seeks media that is a **direct child of the composition root**.
A `<video>` inside the board renders blank. So:

1. Put the `<video>` at root level, `muted playsinline`.
2. Position it in **screen space** where the card's figure area lands at that
   card's camera stop. For C1 with the geometry above, the figure centre is
   screen (540, 868) → `left: 320px; top: 744px; width: 440px; height: 248px`.
3. Show it only during that card's visit window; fade the card's drawn figure
   out as the plate fades in ("the diagram becomes real footage"), and restore
   the figure afterwards.

### Prompting (read `.agents/skills/seedance-2-0/SKILL.md` first)

Route via `video_selector` with `preferred_provider: "seedance"`. Recipe that
works for editorial plates:

```
One continuous locked-off macro shot, no cuts, no zoom, only a slow subtle push-in.
<subject, concrete and physical>. Shallow depth of field, foreground softly defocused.
Cool neutral daylight from one soft overhead source, deep shadows, muted desaturated
palette, no colored neon.
0-2s: … 2-4s: … 4-5s: …
Photorealistic, 35mm film grain, ARRI ALEXA aesthetic, real material texture.
No text, no logos, no lettering, no people, no 3D, no cartoon, no VFX aesthetic.
```
`No text, no logos, no lettering` is load-bearing — generated lettering always
looks wrong, and real logos are supplied as vector instead.

**Security and failure topics trip the content filter.** A plate prompt for a
vulnerability-discovery card ("a hairline fracture creeping across a surface")
came back `422 Unprocessable Entity` from the provider, while structurally
identical prompts on neutral subjects passed. Describe the *instrument*, not the
damage: a magnifier travelling over machined grooves reads as "discovery"
without naming a flaw; solder flowing into a seam reads as "patching" without
naming a breach. Budget one retry, and reword rather than resubmit.

With reference images supplied, use image-to-video / reference-to-video
conditioning instead of pure text-to-video.

**Always re-encode before staging** (dense keyframes, drop the generated audio):
```bash
ffmpeg -y -i raw.mp4 -an -c:v libx264 -r 30 -g 30 -keyint_min 30 \
  -sc_threshold 0 -pix_fmt yuv420p -movflags +faststart -crf 20 plate01.mp4
```

## Cost model (premium tier)

> Costs are written as `USD n.nn` on purpose. A bare dollar-sign followed by a
> digit gets eaten by argument substitution when this skill is invoked with
> arguments, which silently corrupted these figures before.

| Line | Cost |
|---|---|
| Seedance 2.0 plate, 5s (fal.ai standard T2V @ USD 0.3034/s) | **USD 1.52** each |
| Seedance 2.0 via Higgsfield, per 5s clip | USD 0.80 each |
| Narration (~40 words, ElevenLabs) | USD 0.02 |
| Music (free search) | USD 0.00 |
| Logos, figures, render | USD 0.00 (local) |

**2 plates ≈ USD 3.05** · **4 plates ≈ USD 6.10** on fal.ai. To hit a ~USD 3-4
target, either use 2 plates on fal.ai or route to Higgsfield for 4. Announce the
provider and per-clip cost before the first paid call, and **generate one plate
first and look at it** before batching the rest.

Measured on the reference runs:
- `projects/trust-gap-brief/` — 25.6s, 4 cards, 2 plates = **USD 3.06**
- `projects/gemini-38-flash-brief/` — 62s, 8 cards, 3 plates = **USD 4.64**
  (plus one filter-rejected plate that cost nothing but a retry)

Cost tracks plate count, not runtime. A 60s two-sheet brief needs only one more
plate than a 25s one — the extra four cards are carried by free figures.

Not every card needs a plate. Line art, a logo grid, a gauge and a stamp cost
nothing and carry most of the design's character.

## Workflow

1. `init_project(<slug>, pipeline_type='animation')`, open the board.
2. Research → the four card facts (each traceable to a source).
3. Write copy: kicker, title, and 4× (headline + 2-line caption).
4. Source logos for every brand named.
5. Decide which cards get plates; generate **one**, inspect it, then the rest.
6. Author the composition from the reference; re-encode and stage plates.
7. Optional narration (`tts_selector`) + free music bed.
8. `npx hyperframes check` → **0 errors** → `npx hyperframes render --workers 1`.
9. Extract frames at the wide shot and each camera stop and **look at them**.
10. Copy to `renders/final.mp4`, checkpoint, deliver with caption + hashtags.

## Gotchas

`.claude/skills/ai-news-reel/reference/gotchas.md` applies in full (the `.clip`
`height:100%` trap, cold-seek `fromTo` visibility, tween overlap, `check` not
`validate`). Additional to this template:

- **`.clip` also fights `left`+`right` pairs.** `#folio` with `left:84px;
  right:84px` still inherits `width:100%` and overflows 84px off-canvas. Set
  `width: auto`.
- **Don't caption a plate separately** — a caption under the plate collides
  with the card headline at the zoomed stop. The card's own caption is enough.
- **Reveal figures during the card draw-in**, not on the camera visit —
  otherwise the opening wide shot shows a grid of empty cards. Save a distinct
  *emphasis* beat (ping, roll-through, sweep, slam) for the visit.
- **Set `data-media-start` when the plate's payoff is late in the clip.** A 5s
  generation whose subject only resolves at 2-4s, shown in a 3s window, plays
  its boring first half and the payoff never appears. Check where the action
  actually lands in the raw clip and offset into it.
- **Restore the masthead only once the camera is nearly back to WIDE.** Fading
  it in while the board is still scaling out puts the title on top of a
  magnified card. Give the pull-back ~0.9s and start the fade near its end.
- **Rotating a needle trips a `rotation_pivot_drift` warning** while the parent
  camera is also moving. Harmless for a gauge pivoting at `50% 100%`, and it
  clears once the camera settles.
- **`tl.set(el, { text: "..." })` silently does nothing.** GSAP's TextPlugin is
  not loaded, so a folio or label that "updates" this way never changes — the
  render just keeps the original string. `check` reports it only as a console
  warning, not an error, so it will ship if you ignore warnings. Cross-fade two
  absolutely-positioned spans instead.
- **An absolutely-positioned second title lands at the masthead origin**, on top
  of the kicker. Give it the same offset the flowed title resolves to (`top:
  41px` under a 21px kicker with a 16px margin), or absolutely position both.
