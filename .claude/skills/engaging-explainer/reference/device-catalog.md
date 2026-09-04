# Device catalog

The signature device is the one visual object that carries a piece's argument.
This catalog exists for a single reason: **so two episodes cannot look the
same.** Pick by *story shape*, not by topic — the same topic can have several
shapes depending on the angle chosen at proposal.

> **Scarcity rule.** The device belongs in **2–4 beats**, usually including the
> peak. If it is on screen in every scene, it has stopped being a device and
> become wallpaper — and every scene then has the same primary visual subject,
> which is the failure mode `bespoke-composition.md` §1.5 warns about.
>
> The one legitimate exception is when the *thesis itself* is that two things
> are the same object. Take it knowingly and log the deviation.

---

## Shape → device

| Story shape | The claim underneath | Signature device | Peak move |
|---|---|---|---|
| **Mechanism** | "here is how the thing actually works" | A machine that runs — parts that engage and drive each other | Run it at speed, then freeze mid-cycle |
| **Hidden cost** | "this is why it's expensive" | Something whose *area* or *count* grows | Pull back until scale is shocking |
| **Misconception** | "you believe X; it's Y" | An object that **inverts** — the same form read two ways | The flip, held |
| **Comparison** | "A and B differ in a way that matters" | Two forms sharing one axis | Collapse them onto each other |
| **Threshold** | "below X nothing, above X everything" | A rising level against a marked line | Cross the line; everything changes state |
| **Composition** | "this is made of parts you didn't see" | An assembly that explodes and reassembles | Full explode, all parts labelled, frozen |
| **Sequence** | "order is the whole story" | A chain with a travelling indicator | Break one link; watch it stall |
| **Scale shift** | "this is far bigger/smaller than you think" | One reference object, repeatedly re-scaled | The final re-scale, no cut |
| **Network** | "the connections are the point" | Nodes and edges that light by traffic | Saturate, then kill all but one path |
| **Constraint** | "the limit is the design" | A container something presses against | The container fails, or holds visibly |
| **Trade-off** | "you cannot have both" | A balance or shared budget | Push one side to its extreme |
| **Emergence** | "simple rules, complex result" | Many identical small agents | Zoom out; the pattern resolves |

---

## Choosing

1. **Write the claim as one sentence.** "Attention is expensive because it
   compares everything to everything." That is *hidden cost*, not *mechanism* —
   even though the topic is a mechanism.
2. **Check the last three episodes.** If the shape repeats, pick the second-best
   shape rather than repeat a device. Variety across the series beats a locally
   optimal choice.
3. **Invert before you invent.** A gate slamming shut and a lock swinging open
   are the same mechanism carrying opposite meanings — and the second reads
   instantly because the first taught the grammar. Prefer inverting a device you
   have already used over adding an unrelated one.

---

## Evidence type — decide this before sourcing anything

Orthogonal to story shape. It answers *whether external imagery belongs at all*,
and it is a proposal-stage decision, not an asset-stage one.

| `evidence_type` | Imagery? | Because |
|---|---|---|
| **abstract mechanism** | No | A photo adds nothing to "how attention works". Draw it. |
| **real-world referent** | Yes | A product, person, place or physical process — imagery proves the thing exists, which a drawing cannot. |
| **archival / historical** | Yes | The artefact is the point. |
| **texture / atmosphere** | Sparingly | A treated still under a transition, never a subject. |
| **data / quantity** | No | Charts are drawing. A photo of a server rack proves nothing. |

Both worked examples below are **abstract mechanism**, which is why neither
episode uses photography as a subject — and why the one plate that does appear
sits in a window at the exact beat the narration claims contact with the real
world.

Treatment mechanics live in [`imagery.md`](imagery.md). The rule that governs
all of it: **no external asset ever appears untreated.**

## Palette derivation

Two accents, fixed meanings, derived from the subject — never from a default.

1. **Name the two forces in the claim.** Model/harness. Signal/noise. Cost/value.
   Old way/new way.
2. **Assign each a hue with a physical reason.** Terracotta for a mind because
   it is warm and organic; teal for machinery because it is cool and made. A
   viewer should feel the logic without being told it.
3. **Build 5 tints per hue**, not one. Depth comes from tonal range within a
   restricted palette — that is what separates a flat vector look from an
   illustrated one.
4. **The ground is the third decision.** Dark ground = technical, clinical,
   dramatic. Light ground = approachable, editorial, patient. It flips the
   entire read of the piece, so choose it against the audience.

**Never** carry the previous episode's palette. Never use purple-blue "AI"
gradients. Never let an accent appear decoratively — if it appears, it means
its concept.

---

## Type derivation

One face for **statements** (what a person asserts), one for **machine text**
(labels, figures, annotations, citations). The split must be semantic so the
viewer learns the rule in the first twenty seconds without instruction.

| Register | Statement face | Machine face |
|---|---|---|
| Editorial, patient, human | a serif — Newsreader, Source Serif, Spectral | IBM Plex Mono |
| Technical, precise, clinical | a grotesque — Inter, Archivo | JetBrains Mono |
| Bold, loud, urgent | a heavy display face | Space Mono |

Vary the pairing between episodes. Reusing a pairing is a weaker form of the
same mistake as reusing a palette.

---

## Worked examples

**"How transformers work" → hidden cost.**
Claim: attention compares every token to every token, and that shape is the
bill. Device: a lattice whose *area* is the argument. Peak: pull back past
legibility until the area is shocking. Palette: near-black ground, amber =
attention weight. *(Episode: `how-transformers-work`.)*

**"What is an agentic harness" → composition.**
Claim: the model is one part; everything around it is the rest. Device: a room
that gains fittings. Peak: the occupant dims while the machinery keeps running.
Palette: warm paper ground, terracotta = model, teal = harness.
*(Episode: `what-is-an-agentic-harness`.)*

Two topics that could both have been called "mechanism" — and they look nothing
alike, because the *claim* was shaped differently. That is the catalog working.
