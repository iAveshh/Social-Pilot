# Visual system

The craft layer. These are **engine mechanics** — reuse them freely across every
episode. The creative tokens (palette, type pairing, signature device) are
derived per topic and must never be reused; see `device-catalog.md`.

Diagnostic origin: a frame-by-frame review of two finished episodes found that
**almost nothing contrasted with anything else** — every line 2.2–2.6px, every
easing the same cubic over 0.5–0.8s, one camera distance for 26 scenes, content
occupying ~35% of frame with even margins on all sides. That last one is the
amateur default: *small object, centred, in a big empty frame.* Professional work
either fills the frame or commits hard to emptiness.

Everything below is a contrast axis. Use all of them.

---

## 1. Line weight — four steps, never one

```ts
export const W = {
  silhouette: 3.4,   // the primary form. One per frame.
  structure:  2.0,   // walls, axes, containers
  detail:     1.2,   // furniture, ticks, sub-parts
  construction: 0.6, // guides, leaders, grid, measurement
};
```

The single biggest tell of amateur technical illustration is uniform stroke
weight. If a room's outer wall and a desk leg are the same weight, the drawing
has no hierarchy and reads as clip-art.

**Rule:** exactly one silhouette weight per frame. Everything else steps down.

## 2. Camera — a real range, and hold it still when it matters

```ts
export const SHOT = {
  establishing: 0.55,  // subject small in a large field, asymmetric
  wide:         0.80,
  medium:       1.00,
  close:        1.60,
  detail:       2.40,  // crops off-frame deliberately
};
```

A 6% scale change is invisible. If a push is worth doing it is worth **at least
1.4×**. Vary distance across acts; never hold one distance for a whole piece.

- **Compose asymmetrically.** Subject on a third, weight on one side, generous
  air on the other. Even margins on all four sides read as a slide.
- **Let things crop.** An object running off the frame edge implies a world
  larger than the frame. Everything fully contained reads as a diagram.
- **Stillness is a camera choice.** See the freeze device below — a locked frame
  after movement is more arresting than more movement.

## 3. Paper / ground — grain and tonal falloff

A flat fill is the difference between "a div with a background colour" and a
surface. Deterministic, free, ~15 lines:

```tsx
<svg style={{ position: "absolute", inset: 0, opacity: 0.035 }}>
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={7} />
    <feColorMatrix type="saturate" values="0" />
  </filter>
  <rect width="100%" height="100%" filter="url(#grain)" />
</svg>
```

Add a **tonal falloff** — a very slight darkening toward the frame edges (3–5%,
radial). It seats the content and stops the ground reading as pure #FFF-adjacent
flatness. Keep both static: animated grain is expensive and reads as video noise.

**Five tints per hue, not one.** Depth inside a restricted palette comes from
tonal range. A single flat teal has nowhere to go; five steps give you
foreground, midground and recession without adding a colour.

## 4. Timing — three families, not one easing

```ts
export const T = {
  SNAP:   { frames: 5,  ease: Easing.out(Easing.quad) },   // a fact landing
  SETTLE: { frames: 18, ease: Easing.out(Easing.back(1.6)) }, // a part seating
  DRIFT:  { frames: 75, ease: Easing.inOut(Easing.sine) },  // atmosphere
};
```

If a bar growing and a label appearing move at the same speed, the piece reads as
*animated* rather than *directed*. Assign a family by intent:

- **SNAP** — numbers, cuts, anything that must feel like a fact. 4–7 frames.
- **SETTLE** — physical arrivals. Anticipation, small overshoot, follow-through.
- **DRIFT** — camera, atmosphere, background. Slow enough to be felt, not seen.

**Stagger with overlap.** Elements arriving together read as a batch; each
starting before the previous finishes reads as choreography. 60–80ms offsets.

## 5. The freeze device — the most under-used tool available

Attention is captured by the **commencement or cessation** of motion, not by
acceleration. A hard stop is as powerful as a hard start, and costs nothing.

```ts
/** Total stillness for `dur` seconds at `at`. Returns a 0..1 multiplier
 *  every animated value should respect. */
export const freeze = (t: number, at: number, dur = 0.35) =>
  t >= at && t < at + dur ? 0 : 1;
```

Use it:
- at every act boundary,
- on each key claim,
- **at the peak** — where it is the loudest thing in the piece.

Corollary — the **motion silencing effect**: detail changes on fast-moving
objects are literally not perceived. **Never land a number, label or fine mark
while the frame is moving.** Declare a `still_window` and land it there.

## 6. Type ramp

Six steps with fixed roles. One size for everything is the typographic
equivalent of one line weight.

| Role | Size | Face | Tracking |
|---|---|---|---|
| Hero figure | 220–320 | statement | −0.03em |
| Statement | 52–64 | statement | −0.01em |
| Sub-statement | 34–40 | statement | 0 |
| Label | 16–18 | machine | 0.08em |
| Annotation | 13–15 | machine | 0.08em |
| Citation | 11–13 | machine | 0.10em |

The **hero figure is the one most commonly under-set.** A payoff number at 62px
is a caption; at 280px it is an event. If a number is the peak of the piece, it
should be the largest thing in the piece.

## 7. Depth and occlusion

Nothing overlapping anything is the flat-vector tell. Fake depth with contrast,
not with shadows:

```
background  → 25-35% ink opacity
midground   → 55-70%
foreground  → 100%, plus the silhouette weight
```

Let labels overlap the drawing. Let the device sit *in front of* the ground grid
and *behind* the type. Recede what is not the current subject rather than moving
it away.

## 8. Captions — recessive by design

Redundancy is the largest measured harm in Mayer's set (d = 0.87): on-screen text
duplicating narration *reduces* comprehension. But most viewing is muted, so
captions stay — styled to be ignorable by anyone listening:

- statement face, **recessive** — 26–30px at 70–80% ink,
- bottom-safe, never competing with display type,
- **display text never duplicates narration.** One channel per fact.

## 9. Sound design (near-free, disproportionate effect)

Perceived production value is carried by sound more than most visual polish.
Synthesise with ffmpeg for $0:

- a soft click when a part seats (short filtered noise burst),
- a low tone under the peak (sine sweep, −24 dB),
- paper movement on act transitions (filtered noise, 200ms),
- **silence** immediately before the peak — the audio equivalent of the freeze.

## 10. The arousal dial

Register is a parameter, not a constant. Low-arousal content measurably does not
spread; a piece can rest calm and spike hard.

```ts
// 0 = calm/editorial, 1 = urgent/high-arousal
export const arousal = (base: number, t: number, peakAt: number) =>
  base + (1 - base) * bump(t, peakAt, 4.0);
```

At the peak, ramp **contrast, saturation, scale and motion speed together** for
3–5 seconds, then release hard. The release is what makes the peak — a piece at
constant intensity has no peak at all.

---

## Checklist

- [ ] Four line weights present; exactly one silhouette per frame.
- [ ] Camera range spans at least 0.55× → 1.6×.
- [ ] Composition is asymmetric; something crops off-frame.
- [ ] Grain and tonal falloff on the ground; five tints per hue.
- [ ] All three timing families used; staggers overlap.
- [ ] Freezes at act boundaries and at the peak.
- [ ] No detail lands during motion.
- [ ] Six type steps; the hero figure is genuinely huge.
- [ ] Depth via contrast falloff, not shadows.
- [ ] Captions recessive; display text non-duplicative.
- [ ] Arousal ramps at the peak and releases after.
