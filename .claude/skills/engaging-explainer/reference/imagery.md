# Imagery

How photographs, generated plates and video clips join a drawn world without
looking glued on.

---

## The problem is reconciliation, not sourcing

Sourcing is easy and nearly free. **Making external material *belong* is the
whole job.** A raw photograph dropped into a drafted vector language reads as
two unrelated pieces stuck together — and that single mismatch is the most
common reason an otherwise decent explainer looks cheap.

So the rule is absolute:

> **No external asset ever appears untreated.** Every photograph, generated
> plate and video frame passes through a treatment that remaps it onto the
> episode's palette and surface.

All of it is SVG filters running in Remotion: deterministic, and **$0**.

---

## The four treatments

Implemented in the channel system's `Plate.tsx`.

| Treatment | Mechanism | Use when |
|---|---|---|
| **duotone** | `feColorMatrix` (luma) → `feComponentTransfer` table mapping shadows to the accent's deepest tint and highlights to paper | **The default.** Binds any photo to the palette while keeping the subject readable. |
| **halftone** | duotone + a fine dot screen at `mixBlendMode: screen` | Makes photography read as **print**, which is what a paper ground demands. |
| **lineart** | luma → `feConvolveMatrix` edge kernel → **linear amplification** → invert → gamma → map to ink | The image literally *becomes drawing* and joins the language rather than sitting beside it. |
| **posterize** | luma → `feComponentTransfer type="discrete"` over the palette's tonal steps | Collapses the image onto the same five-tint depth ladder as everything else. |

### Two gotchas found the hard way

1. **Lineart needs amplification before inversion.** The raw edge response from
   `feConvolveMatrix` is weak; without a `feFuncR type="linear" slope="7"` stage
   the plate comes out almost blank. Amplify, *then* invert, *then* gamma to
   deepen the surviving strokes.
2. **Small plates need contrast, not tonal range.** Mapping shadows to the
   deepest tint collapses a 140px plate into a black rectangle. Below roughly
   200px, use the **mid** tint as the dark end.

---

## Containment and scarcity

**Contain it.** Imagery lives inside a drawn aperture — a plate, a window, a
pinned card — with registration ticks. Never full-bleed. It should read as *an
artifact on the drawing*, not as a different video. A room's window, a device
screen, a held photograph: the composition should already have somewhere for it
to go.

**Grain last.** The paper grain runs *over* image and drawing alike so both sit
on one surface. Cheapest trick in the set, outsized effect.

**Reveal like a drawing.** Wipe, don't fade. It matches the draw-on language.

**Keep it scarce.** Imagery in **≤ 25% of scenes**. Past that it stops being
evidence and becomes decoration, and the drawn language loses its authority.

---

## When imagery earns its place

The default is *draw it*. Imagery is warranted only when it does something a
drawing cannot:

| `evidence_type` | Imagery? | Why |
|---|---|---|
| **abstract mechanism** | No | A photo adds nothing to "how attention works". Draw it. |
| **real-world referent** | Yes | A product, person, place or physical process — imagery *proves the thing exists*, which a drawing can't. |
| **archival / historical** | Yes | The artefact is the point. |
| **texture / atmosphere** | Sparingly | A treated still under a transition, never as a subject. |
| **data / quantity** | No | Charts are drawing. A photo of a server rack proves nothing. |

Declare `evidence_type` at proposal, before sourcing anything. It decides
*whether* imagery belongs before anyone decides *what* to source.

---

## Sourcing, with real costs

| Path | Cost | Best for |
|---|---|---|
| **Unsplash MCP** | **$0** | Real photography. Already connected — start here. |
| Pexels / Pixabay | $0 (free key) | Broader stock library |
| **`recraft_image`** | **$0.04** | **SVG vector output** — natively belongs to a drawn world |
| `flux_image` | $0.05 | Photoreal plates |
| `seedream_image` | $0.135 | Dense layouts, accurate on-image text |
| `kling_video` | **$0.10 / 5s** | The only video that fits a minimal budget |
| heygen / gemini_omni | $0.50–0.65 / 5s | — |
| seedance / veo | $1.52–2.00 / 5s | Breaks the budget at any useful length |

**`recraft_image` is the standout.** It emits actual SVG for four cents — vector
output that can be recoloured to the episode palette and needs no treatment at
all. For anything illustrative it beats a treated photograph outright.

**On video:** `kling_video` is 15–20× cheaper than Veo. Twenty seconds across a
five-minute episode is $0.40. The same twenty seconds on Veo is $8.

> **Both video providers are tier-gated on some accounts.** `kling-video` has
> returned 403 on every variant with $0.00 charged. That is a gate, not an
> outage — see `production-pipeline.md` §1. When it happens, take the declared
> fallback (a treated still, usually with a synthesised drift) and **say so**.
> Never silently substitute a pricier generator; a treatment layer erases most
> of what the extra money buys anyway.

Generated video also carries its own drifty motion character that will fight a
drafted motion language. Use it for **1–3 beats maximum**, treat it identically,
and constrain or freeze it — **a treated still pulled from a clip is often
stronger than the clip.**

**Known constraint:** `bg_remove` and `upscale` are unavailable, so subjects
cannot be cleanly cut from their backgrounds. Prefer full-frame treated plates
inside drawn apertures over cut-out compositing — which is the better look here
anyway.

---

## Attribution

Record source, photographer, licence and URL in `artifacts/imagery.json` and in
the asset manifest, even where the licence does not require it.

---

## Lint

Two checks enforce this (`retention_lint.py`):

- `imagery_scarcity` — external assets appear in ≤ 25% of scenes.
- `imagery_treated` — every scene declaring an external asset also declares a
  treatment. A raw composite is an ERROR.

Scenes carrying imagery declare:

```json
{
  "imagery": [{ "src": "public/images/x.jpg", "treatment": "duotone",
                "evidence_type": "real-world referent" }]
}
```
