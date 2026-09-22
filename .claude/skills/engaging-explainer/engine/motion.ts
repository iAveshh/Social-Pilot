import { Easing, interpolate } from "remotion";
import type { Craft } from "./intensity";

// ---------------------------------------------------------------------------
// THE LIFE LAYER
//
// Why competent motion graphics still read as dead: everything eases in and
// stops on the exact value it was heading for. Real matter overshoots, settles,
// and carries its parts along behind it.
//
// The hard constraint: apply this to STRUCTURE — frames, rules, brackets,
// containers, whole groups arriving. Never to a figure at the moment it lands.
// A number that wobbles while being read is a number nobody reads, which is the
// motion-silencing finding restated as a rule.
// ---------------------------------------------------------------------------

const clamp01 = (n: number) => Math.max(0, Math.min(1, n));

/** Arrives past its target and comes back. `craft.life` scales the overshoot. */
export const overshoot = (t: number, at: number, craft: Craft, dur = 0.42, amount = 0.14) => {
  const p = clamp01((t - at) / dur);
  if (p <= 0) return 0;
  if (p >= 1) return 1;
  const over = 1 + amount * craft.life;
  return interpolate(p, [0, 1], [0, over], { easing: Easing.out(Easing.cubic) })
       - (over - 1) * interpolate(p, [0.55, 1], [0, 1],
           { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
};

/** Damped oscillation after an arrival — the wobble that says "this has mass".
 *  Returns a signed offset around 0, so add it to a position or rotation. */
export const settle = (t: number, at: number, craft: Craft, dur = 0.9, amount = 1) => {
  const p = clamp01((t - at) / dur);
  if (p <= 0 || p >= 1) return 0;
  return amount * craft.life * Math.exp(-5.2 * p) * Math.sin(p * Math.PI * 4.4);
};

/** A small counter-move before a large one. Anticipation is most of what makes
 *  a movement feel intended rather than triggered. */
export const anticipate = (t: number, at: number, craft: Craft, dur = 0.26, amount = 0.16) => {
  const lead = dur * 0.42;
  if (t < at - lead || t > at + dur) return 0;
  if (t < at) {
    const p = clamp01((t - (at - lead)) / lead);
    return -amount * craft.life * Math.sin(p * Math.PI);
  }
  return 0;
};

/**
 * Per-element arrival offset in seconds.
 *
 * A row of six bars that all arrive together is one event. The same six
 * staggered are a phrase, and the eye follows a phrase.
 */
export const stagger = (i: number, craft: Craft, spread?: number) =>
  i * (spread ?? craft.stagger);

/** Follow-through: a trailing part that lags its parent and catches up. */
export const lag = (t: number, at: number, craft: Craft, by = 0.08, dur = 0.4) =>
  clamp01((t - at - by * craft.life) / dur);

// --- MATTER CONTINUITY -----------------------------------------------------
// A crossfade says "that was replaced". A transformation says "that BECAME
// this", which is the whole grammar of explanation. Prefer the second wherever
// two states share any matter at all.

/** Progress of A turning into B. Feed to both: A uses it, B uses it inverted. */
export const becomes = (t: number, at: number, dur = 0.7) =>
  interpolate(t, [at, at + dur], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic),
  });

/**
 * Guard against the commonest authoring bug: an element that never fades, so
 * whatever replaced it sits on top forever.
 *
 *   <Old o={handover(oldIn, newIn)} />
 *
 * Multiply the outgoing element's opacity by this and it cannot outlive its
 * successor.
 */
export const handover = (mine: number, theirs: number) => mine * (1 - clamp01(theirs));

/** Interpolate between two rectangles — the cheap, reliable morph. Real path
 *  morphing needs matched point counts; a rect that travels and reshapes into
 *  its successor carries the same "same matter" reading for a fraction of the
 *  work. */
export const rectLerp = (
  a: { x: number; y: number; w: number; h: number },
  b: { x: number; y: number; w: number; h: number },
  p: number,
) => ({
  x: a.x + (b.x - a.x) * p, y: a.y + (b.y - a.y) * p,
  w: a.w + (b.w - a.w) * p, h: a.h + (b.h - a.h) * p,
});
