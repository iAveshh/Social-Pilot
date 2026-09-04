# Composition scaffold

The file layout for a hand-authored (atelier) composition, and — more
importantly — **which parts you copy forward and which parts you must rewrite.**

Getting that split wrong is how a series starts looking like one template with
different colours.

---

## The split

| File | Role | Carry forward? |
|---|---|---|
| `theme.ts` | tokens, timing families, freeze, arousal, type ramp | **structure yes, values no** |
| `Surface.tsx` | ground, grain, tonal falloff, standing furniture | mechanism yes, furniture no |
| `Marks.tsx` | every diagram in the piece | **never** — this *is* the topic |
| `Type.tsx` | statement / annotation / leader / captions | primitives yes, ramp values no |
| `Plate.tsx` | imagery treatments (duotone, posterize, lineart) | **verbatim** |
| `Composition.tsx` | the assembly | never |
| `Root.tsx`, `index.tsx` | registration | verbatim, rename the id |

**Engine** = `Plate.tsx`, the easing/freeze/arousal helpers, the caption
component, the grain filter. These are mechanics. Reusing them is correct and
saves real time.

**Creative** = every colour, every weight number, the type pairing, the motion
character, and all of `Marks.tsx`. Re-derive these per topic from
[`device-catalog.md`](device-catalog.md). If you find yourself editing last
episode's `Marks.tsx`, stop — you are re-skinning.

---

## `theme.ts` — the shape to keep

```ts
// ---- creative: re-derived every episode ----------------------------------
export const GROUND = "#E8E8E6";          // deliberately not last episode's
export const INK    = "#111315";
export const ACCENT_A_5 = [...];           // 5 tints, ONE fixed meaning
export const ACCENT_B_5 = [...];           // 5 tints, the opposing meaning

export const W = { rule: 5.0, silhouette: 3.6, structure: 2.2,
                   detail: 1.3, construction: 0.7 };
export const TYPE = { hero, statement, sub, label, annotation, citation };

// ---- engine: carry forward -----------------------------------------------
export const ramp    = (t, a, b) => ...      // general
export const snap    = (t, at)   => ...      // a fact landing
export const seat    = (t, at)   => ...      // a part arriving
export const drift   = (t, a, b) => ...      // atmosphere
export const windowed= (t, a, b) => ...      // 0→1→0
export const freeze  = (t, ats)  => ...      // 0 while frozen
export const heldClock=(t, ats)  => ...      // clock that STOPS when frozen
export const arousal = (t, base, peakAt) => ...
```

Five tints per accent, not one. Depth inside a restricted palette comes from
tonal range; a single flat value has nowhere to recede to.

**Remotion's easing is `Easing.sin`, not `Easing.sine`.** It fails at runtime,
not at type-check.

### Drive continuous motion off the held clock

```tsx
const FREEZES = [act1Close, act2Close, PEAK, finalBeat];
const ct = heldClock(t, FREEZES, 0.4);
const breathe = 1 + 0.012 * Math.sin(ct * 0.22);   // ct, never t
```

Using `t` for ambient motion means a "freeze" only halts *new arrivals* while the
camera keeps breathing — which reads as a stutter rather than a stop. Cessation
of motion is one of the few attention events that costs nothing; do not waste it.

---

## `Marks.tsx` — one component per semantic object

Name components after **what they mean**, not what they look like:
`RiskScale`, `DotGrid`, `Door`, `Finding`, `Breach`, `Counter` — not `Chart2`,
`RedBox`, `BottomPanel`.

Every mark component takes:

- geometry (`x`, `y`, `w`, `h`)
- **progress values, never times** (`grow`, `reveal`, `open`, `draw`, `figure`)
- `o` for opacity

Keeping time out of the marks and in `Composition.tsx` is what lets you re-time
the whole piece from `beats.json` without touching a diagram.

### Reveal by drawing, not by fading

```tsx
pathLength={1} strokeDasharray={1} strokeDashoffset={Math.max(0, 1 - draw)}
```

A fade says "this appeared". A draw-on says "this is being constructed", which is
what an explainer is doing.

---

## `Composition.tsx` — assembly only

Structure it as: props contract → peak → freezes → per-act progress values →
JSX gated by act.

```tsx
const b = props.beats;              // word-level, from beats.json
const at = (id: string) => props.scenes[id]?.start ?? 0;

const PEAK = b.a4_notdown;                       // name the peak explicitly
const FREEZES = [at("sc18"), at("sc25"), PEAK];
const ct = heldClock(t, FREEZES, 0.4);

const barGrow = ramp(t, b.a2_247 - 0.9, b.a2_247 + 0.3);
const barFig  = snap(t, b.a2_247 + 0.45);        // figure AFTER the bar stops
```

**Every timing expression references a beat name.** If you type a literal second
into this file, you have just introduced drift that no linter will catch.

### Hand the frame over

The single most common authoring bug: an element that never fades, so the shape
it was replaced by overlaps it forever.

```tsx
<Form  o={formIn * (1 - doorsIn)} />    {/* explicitly hands over */}
<Door  o={doorsIn} />
```

Whenever B replaces A, A's opacity must reference B's arrival.

### Never scale type vertically

Compressing a chart with `scaleY` also compresses its labels into an illegible
smear that reads as noise. If a group must recede, **fade it as it compresses**:

```tsx
transform: `translateY(${-c * 96}px) scaleY(${1 - c * 0.72})`,
opacity: fieldIn * (1 - c * 0.86),
```

---

## Props contract

```ts
export interface SceneProps {
  totalSeconds: number;
  fps: number;
  narrationSrc: string;                    // public/-relative
  musicSrc: string;
  musicVolume: number;                     // ~0.30 against a -32 LUFS bed
  beats:  Record<string, number>;          // from beats.json
  acts:   Record<string, number>;
  scenes: Record<string, {start: number; end: number}>;
  subtitles: {start: number; end: number; text: string}[];
  imagery: Record<string, string>;         // public/-relative
}
```

Guard against an empty first render — Remotion evaluates the component before
props resolve:

```tsx
if (!props?.beats || !props?.scenes) return <AbsoluteFill style={{background: GROUND}} />;
```

`calculateMetadata` derives duration from props so the composition length always
matches the measured read:

```tsx
durationInFrames: Math.round((props.totalSeconds ?? FALLBACK) * (props.fps ?? 30))
```

---

## Layout conventions that hold up at 1920×1080

- Content margin **120px**; a standing header rule near y=118 and a footer rule
  near y=982 make every frame read as one document rather than a slide deck.
- Captions bottom **~54px**, at ~0.68 opacity — recessive by design, and
  suppressed entirely at the peak.
- Keep the peak's headline **beside** the diagram it annotates, never on top of
  it: both have to be readable in the same instant.
- Imagery is **never full-bleed**. Hold it in a drawn aperture with registration
  ticks — that is what keeps it evidence instead of backdrop.

---

## React rules that bite here

- **Hooks before any early return.** A `useMemo` after `if (!ready) return` is an
  order violation that only fires on some frames.
- Unused imports are harmless at render (esbuild does not type-check) but will
  fail a strict `tsc`. Keep them clean anyway.
