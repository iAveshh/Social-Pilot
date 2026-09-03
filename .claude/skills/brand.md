# Brand contract — OptimalGradient video

Both video pipelines (`ai-news-reel`, `paper-brief-reel`) render to this
contract. It exists so that twenty videos across two visual formats still read
as one publisher. Read it before authoring a composition or writing an image
prompt.

## Palette

Two grounds, one ink, one accent family, one alert. Nothing else.

| Token | Dark format | Paper format |
|---|---|---|
| ground | `#0a0a0c` (+ `#15151c` radial lift) | `#efece3` press stock |
| surface | `rgba(22,22,28,0.85)` panels | `#fbf9f3` card |
| ink / primary text | `#e8e8ea` | `#16161a` |
| secondary text | `#b6b6bd` | `#44444b` |
| annotation | `#8f8f98` | `#6a6a70` (never lighter — fails AA) |
| accent | `#ff7a45` | `#b0353c` |
| alert | `#ff5c5c` | `#b0353c` |

Accent is for **the turn** — the kicker, the needle, a stamp, the one metric
that matters. The moment a third of the frame is accent-coloured, it has
stopped meaning anything.

## Type

- **Inter 800** — headlines only, tracking -0.5 to -1.6px
- **JetBrains Mono** — everything else: captions, annotations, labels, stamps,
  folio, chip text
- Never a third family. `Space Grotesk` silently falls back to Arial in the
  deterministic font compiler — do not reach for it.

## Annotation grammar

The series has a house voice for small text. Reuse it:

- `FIG. 01` … `FIG. 08` — figure numbering, top-left of a card
- `SHEET 01 / 02` — folio, bottom-right
- `[ok]` `[warn]` `[fail]` `[crit]` — status lines in a terminal feed
- `SOURCE / <domain>` — above a receipt
- Headlines are declarative and end in a period. "One Protocol." "It Fell."

## Real brand marks

Never let a generator draw a logo — it will be subtly wrong, and it is a
trademark problem. Source official vector marks:

```bash
npm install simple-icons@16 --no-save
python .claude/skills/paper-brief-reel/reference/extract-logos.py <slug> ...
```

**Treatment is monochrome, always.** `#e8e8ea` on dark, `#16161a` on paper,
fixed cell size, in a bordered chip. Six logos in their own brand colours turn
the frame into a rainbow and destroy the palette in one shot.

> **OpenAI and Microsoft are not in simple-icons** (both requested removal).
> Use their official press-kit SVG, or set the name as an Inter 800 wordmark.
> Never substitute a lookalike.

## Imagery — reference only, never generic

**Every image on screen must carry information the narration cannot.** If it is
mood, texture, or vibe, cut it. A macro photo of a circuit board says nothing a
viewer could not have assumed; the vendor's own benchmark chart says 71.0%.

Ranked by value:

1. **Charts and tables from the source.** A benchmark chart with real numbers is
   the single most valuable thing you can put on screen. It proves the claim,
   carries data the voice-over cannot, and costs nothing.
2. **The source page itself** — headline, date, byline. See Receipts below.
3. **Product / UI screenshots** where the story is about a product surface.
4. **Real brand marks** (above).
5. **Generated imagery — default to none.** It is permitted only when a specific
   physical object *is* the story and no capture of it exists. "Some servers" is
   never that. Assume the answer is no.

This rule was learned the expensive way: an early cut carried three generated
plates — server blades, a circuit trace, a latch — which looked handsome and
informed nobody. Replacing them with one real chart from the announcement made
the piece both cheaper and more credible.

### Capturing reference material

`node ai-news-reel/reference/capture-refs.mjs <url> <outDir> <spec>...` grabs
specific elements — `img:2:name` for the nth substantial image, `sel:<css>:name`
for a selector, `clip:x,y,w,h:name` for a region. It scrolls the page first so
lazy-loaded charts actually render. Inspect what a page holds before choosing:
`node ai-news-reel/reference/inspect-page.mjs <url>` lists headings, tables and
images with their positions.

### Treatment

Every reference image is matted — **never full-bleed**:

```css
.ref {
  border: 3px solid #3a3a44;     /* #16161a on paper */
  border-radius: 14px;           /* always round the corners */
  object-fit: cover;
  background: #fbfbfd;
}
```

Leave captured charts and pages **bright**. A white chart in a near-black frame
reads as evidence held up to the camera, and that contrast is the point — do not
desaturate or dim it into the palette. Label it `SOURCE / <domain>` or
`MEASURED / <org>` in accent above the mat, so the viewer knows whose number it
is.

Size for a phone. A chart narrower than ~85% of frame width is decoration; its
axis labels have to be readable or it is not doing its job.

**Quote the source exactly.** If the chart says 71.0%, the on-screen stat says
71.0% — not "70%+". A designed stat that disagrees with the chart beside it
destroys the credibility both were there to build.

## Captions

Most Reel viewing is muted, so captions are not optional.

- JetBrains Mono, ~46px, weight 700, uppercase, centered
- `bottom: 380px` — clear of the Instagram UI, which eats roughly the bottom 300px
- Heavy text-shadow, no box: `0 3px 22px rgba(0,0,0,0.95)`
- 2-3 words per chunk, from **word-level** whisper timings
- A chunk may never open on `%`, `.6`, or a bare stub — pull those back into
  the previous chunk or the caption reads as gibberish
- Correct whisper's mis-joins ("cyberversion" → "cyber version"). Captions are
  designed on-screen text, not a raw transcript.

## Sound

No sound-effects tool is wrapped in this repo. Synthesise UI cues with ffmpeg
instead — for a terminal aesthetic they beat real foley and cost nothing.

| Cue | Recipe |
|---|---|
| tick (item lands) | sine 1180 Hz, 75 ms, exponential fade |
| tick_hi (emphasis) | sine 1560 Hz, 85 ms |
| blip (reveal) | sine 880 Hz, 110 ms |
| thud (the rupture) | sine 72 Hz + brown noise through a 320 Hz lowpass |
| sweep (a bar filling) | pink noise, 600–5200 Hz band, fade in/out |
| latch (gate closes) | 420 Hz then 300 Hz, 60 ms apart |

Pre-mix the cues onto one silent bed with `adelay`, then **boost about +24 dB
and limit** — an `amix` of sparse cues lands around -30 dBFS, far too quiet to
hear under narration. Ride it at `volume: 0.55` between the voice and the music.

## Audio balance

`narration 1.0` · `sfx 0.55` · `music 0.13` under speech, `0.30` in the clear.
Target the finished mix at roughly -17 dB mean, peak under -0.5 dB.
