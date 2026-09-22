# Motion craft

The engagement model decides **what happens when**. This decides whether it is
worth looking at.

Both halves are enforced. `retention_lint.py` checks structure; `craft_lint.py`
checks craft. Running only the first is how a piece ends up with a flawless beat
map rendered as slides — which is exactly what happened on episode 3:

| | episode 3, first render |
|---|---|
| retention lint | **0 errors, 0 warnings** |
| craft lint | **7 errors** |
| camera positions in 239 s | **1** |
| depth planes | **0** |
| transforms vs opacity gates | **10 vs 111** |
| share of all easing that was one curve | **80%** |

Every frame was competently drawn. The piece still read as tasteful slides,
because nothing moved, nothing had depth, nothing was lit, and nothing had mass.

---

## The intensity dial

Choose a register per topic, alongside the palette and the signature device.
It scales **craft, never information**.

| Register | Use for | Camera | Parallax | Light | Life |
|---|---|---|---|---|---|
| `austere` | primary-source readings, institutional, sceptical | 0.55 | 0.45 | 0.40 | 0.35 |
| `measured` | the default — journalistic, composed | 1.00 | 1.00 | 0.75 | 0.70 |
| `rich` | science, culture, anything with wonder in it | 1.35 | 1.45 | 1.00 | 1.00 |
| `lush` | full colour and motion — earn it | 1.70 | 1.90 | 1.25 | 1.30 |

```ts
import { craftFor } from "./engine/intensity";
const craft = craftFor("measured");
```

**`austere` is not `inert`.** Even at the lowest setting the camera moves, the
world has depth and the ground is lit. The restrained register is a choice about
*amplitude*, not about whether the craft exists. Episode 3's mistake was reading
restraint as an excuse for a locked frame.

`blendCraft(a, b, k)` warms a piece up across its acts — open austere, finish
rich — which is its own engagement device.

### Why this is not a coherence violation

Mayer's coherence principle (d = 0.70) says removing extraneous material
improves learning. That finding is about extraneous **content**: irrelevant
anecdotes, decorative clip-art, music competing with narration.

Camera, light, depth and motion quality are not extraneous material. They are
how a viewer's visual system decides whether it is looking at a space or a
diagram. The rule that keeps this honest is **craft up, information flat** —
turning the dial up must never add a fact, a label or a second thing to read.

---

## 1. The camera

A piece with one camera position is a slide deck, however well the slides are
drawn.

```ts
const cam = camera(t, shots, craft);
```

```ts
const shots: Shot[] = [
  { at: 0,            scale: SHOT.wide,         move: "cut"   },
  { at: b.a1_same,    scale: SHOT.close,  x: 960, y: 480, move: "cut" },
  { at: b.a1_same+3,  scale: SHOT.medium,       move: "drift" },
  { at: PEAK,         scale: SHOT.close,        move: "cut"   },
];
```

- **A 6% scale change is invisible.** If a push is worth doing it is worth
  **1.4x**. The lint fails a range under that.
- **Cut, don't always glide.** A hard change of distance is one of the strongest
  attention events available and costs nothing. Put one on the peak.
- **Re-frame at act boundaries at minimum.** The lint fails any hold over 28 s.
- **Compose asymmetrically and let things crop.** An object running off frame
  implies a world larger than the frame; everything fully contained reads as a
  diagram of a thing rather than the thing.
- **Drive breathing from a held clock** so a freeze arrests the camera too. A
  freeze with a drifting camera reads as a stutter and wastes the strongest
  attention event in the toolkit.

## 2. Depth

```tsx
<Plane cam={cam} craft={craft} z={Z.far}>     {furniture}   </Plane>
<Plane cam={cam} craft={craft} z={Z.subject}> {diagram}     </Plane>
<Foreground cam={cam} craft={craft}>          {occluders}   </Foreground>
```

Parallax is what makes a camera move read as **space** rather than as zoom. On
one plane a push is just a scale; across four planes the same push builds a
world. Depth is carried by **tone** as much as by movement, so `depthDim()`
drops contrast on far planes automatically — flat-contrast parallax still reads
flat.

Minimum three distinct depths. Ground plus subject is not depth.

## 3. Light

```tsx
<KeyLight craft={craft} cam={cam} />
{/* ...content... */}
<Vignette craft={craft} cam={cam} />
<Grain craft={craft} />
```

A flat fill is the difference between "a div with a background colour" and a
surface. The key drifts *opposite* the camera, so moving through a scene changes
how it is lit rather than sliding a gradient along with it. The vignette
tightens as the camera pushes in — the frame closing around the subject is most
of why a close-up feels close.

`glow(color, craft)` puts a tight coloured spread on accent elements. On a light
ground a true bloom reads as a smudge, so keep it small and only on accents.

## 4. Matter continuity

**This is the one that matters most, and it is the hardest to retrofit.**

A crossfade says *"that was replaced."* A transformation says *"that BECAME
this"* — which is the entire grammar of explanation. Wherever two states share
any matter at all, transform between them.

```ts
const p = becomes(t, b.a1_same, 0.7);
const r = rectLerp(nameplateBox, formBox, p);   // the names ARE the form
```

Episode 3 had the two product names dissolve while a hatched block faded up
underneath. The names should have **collapsed into** it. Same information, same
timing, completely different reading — one is a slide change, the other is the
argument of the video happening in front of you.

`handover(mine, theirs)` guards the commonest authoring bug: an outgoing element
that never fades, so its replacement sits on top of it forever.

The lint fails when under 25% of state changes move anything.

## 5. The life layer

Why competent motion still reads as dead: everything eases in and stops on the
exact value it was heading for. Real matter overshoots, settles, and drags its
parts along behind it.

```ts
const p = overshoot(t, at, craft);            // arrives past, comes back
const w = settle(t, at, craft);               // damped wobble — add to y or rot
const a = anticipate(t, at, craft);           // small counter-move first
const off = stagger(i, craft);                // per-element arrival offset
```

**The hard constraint:** apply this to **structure** — frames, rules, brackets,
containers, groups arriving. **Never to a figure at the moment it lands.** A
number that wobbles while being read is a number nobody reads, which is the
motion-silencing finding restated as a rule.

Stagger is the cheapest of these and possibly the most effective. Six bars
arriving together are one event; the same six staggered are a phrase, and the
eye follows a phrase.

## 6. Kinetic type

```tsx
<KineticText text="one model, two doors" t={t} at={b.a5_doors} craft={craft} unit="word" />
```

Text that fades in arrives from nowhere. Text that rises into place, word by
word, has been **put** there — and the eye reads placement as intent.

Everything here settles inside ~0.5 s and then holds absolutely still. Never
stagger a line so long that its tail is still moving after the narration has
moved on. `unit="char"` reads as stamping and becomes noise on anything longer
than two or three words.

`<Wipe>` reveals by uncovering, which matches the drawn language's draw-on far
better than a fade. `<Counter>` ticks a figure to its value — use it **only**
where the change itself is the subject, such as a bar growing to its number.

---

## The gate

```bash
python .claude/skills/engaging-explainer/craft_lint.py <slug>
```

Run it beside the retention lint at the scene_plan/authoring gate. It reads the
**composition source**, not a declaration, because the defect it exists to catch
is precisely a composition that quietly ignores what the plan said it would do —
episode 3 imported `SHOT` nowhere and held one frame for four minutes while its
own art direction promised a full distance range.

Declare the checkable parts in `artifacts/craft_plan.json`:

```json
{
  "register": "measured",
  "shots": [
    {"at": 0,     "scale": 0.80, "move": "cut"},
    {"at": 11.12, "scale": 1.60, "move": "cut"},
    {"at": 36.04, "scale": 0.55, "move": "move"}
  ],
  "depth_planes": 4
}
```

## Anti-patterns

- **A locked camera**, or a push under 1.4x, which is the same thing.
- **Everything on one plane**, then wondering why the push reads as a zoom.
- **Crossfading two states that share matter.**
- **One easing curve for every event** — it gives them all the same texture.
- **Secondary motion on a figure as it lands.** Wobble the frame, never the number.
- **Bloom on a light ground.** It reads as a smudge, not as light.
- **Turning the dial up and the information density up together.** That is the
  actual coherence violation, and it is the one failure here that measurably
  costs comprehension.
