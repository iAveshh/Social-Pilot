// ---------------------------------------------------------------------------
// THE VISUAL INTENSITY DIAL
//
// One knob, chosen per topic alongside the palette and the signature device.
// It scales craft, never information: camera amplitude, depth, light, motion
// energy and type animation all move together, and none of them add a single
// fact to the frame.
//
// This is the distinction Mayer's coherence principle actually draws. The
// d=0.70 finding is about extraneous CONTENT — irrelevant anecdotes, decorative
// clip-art, competing music. Production craft is not extraneous material.
// Turning this dial up must never turn information density up with it.
// ---------------------------------------------------------------------------

export type Register = "austere" | "measured" | "rich" | "lush";

export interface Craft {
  /** multiplier on every camera move; 0 would lock the frame */
  camera: number;
  /** how far the depth planes separate — 0 collapses to one plane */
  parallax: number;
  /** vignette + directional falloff strength */
  light: number;
  /** halo on accent elements */
  bloom: number;
  /** overshoot / settle / follow-through amplitude */
  life: number;
  /** per-element arrival offset, in seconds at the widest */
  stagger: number;
  /** kinetic type: 0 = plain fade, 1 = per-word with rotation */
  kinetic: number;
  /** surface tooth */
  grain: number;
  /** how many tints of each accent are in play (3..5) */
  tints: number;
  /** accent saturation multiplier */
  saturation: number;
}

const TABLE: Record<Register, Craft> = {
  // A document read in front of you. Restraint IS the argument — but even here
  // the camera moves and the world has depth. Austere is not the same as inert,
  // and the flat version of this register is what made episode 3 read as slides.
  austere:  { camera: 0.55, parallax: 0.45, light: 0.40, bloom: 0.00,
              life: 0.35, stagger: 0.05, kinetic: 0.30, grain: 0.05,
              tints: 3, saturation: 0.85 },

  // The default. Journalistic, composed, clearly authored.
  measured: { camera: 1.00, parallax: 1.00, light: 0.75, bloom: 0.25,
              life: 0.70, stagger: 0.09, kinetic: 0.60, grain: 0.07,
              tints: 4, saturation: 1.00 },

  // Science, culture, anything with wonder in it.
  rich:     { camera: 1.35, parallax: 1.45, light: 1.00, bloom: 0.60,
              life: 1.00, stagger: 0.13, kinetic: 0.85, grain: 0.09,
              tints: 5, saturation: 1.15 },

  // Full colour and motion. Earn it — at this setting the craft is loud enough
  // to compete with the narration if the information density also rises.
  lush:     { camera: 1.70, parallax: 1.90, light: 1.25, bloom: 1.00,
              life: 1.30, stagger: 0.17, kinetic: 1.00, grain: 0.11,
              tints: 5, saturation: 1.30 },
};

export const craftFor = (r: Register): Craft => TABLE[r];

/** Lerp between two registers, for a piece that warms up across its acts. */
export const blendCraft = (a: Register, b: Register, k: number): Craft => {
  const A = TABLE[a], B = TABLE[b];
  const mix = (x: number, y: number) => x + (y - x) * Math.max(0, Math.min(1, k));
  return {
    camera: mix(A.camera, B.camera), parallax: mix(A.parallax, B.parallax),
    light: mix(A.light, B.light), bloom: mix(A.bloom, B.bloom),
    life: mix(A.life, B.life), stagger: mix(A.stagger, B.stagger),
    kinetic: mix(A.kinetic, B.kinetic), grain: mix(A.grain, B.grain),
    tints: Math.round(mix(A.tints, B.tints)),
    saturation: mix(A.saturation, B.saturation),
  };
};
