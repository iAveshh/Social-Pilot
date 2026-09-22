import React from "react";
import type { CameraState } from "./camera";
import type { Craft } from "./intensity";

// ---------------------------------------------------------------------------
// LIGHT
//
// A flat fill is the difference between "a div with a background colour" and a
// surface. None of this is a shadow: it is a key direction, a falloff, and a
// vignette that tracks the camera, which together give the ground form.
// ---------------------------------------------------------------------------

/** Directional key. The bright side should agree with wherever the piece's
 *  attention sits, so the eye is led rather than merely lit. */
export const KeyLight: React.FC<{
  craft: Craft; cam: CameraState;
  /** degrees, 0 = from the left */
  angle?: number;
  warm?: string; cool?: string;
}> = ({ craft, cam, angle = 24, warm = "rgba(255,252,246,0.62)", cool = "rgba(8,12,20,0.09)" }) => {
  if (craft.light <= 0.01) return null;
  // the key drifts opposite the camera, so moving through the scene changes
  // how it is lit rather than sliding a gradient along with it
  const px = 50 - ((cam.x - 960) / 1920) * 26;
  const py = 42 - ((cam.y - 540) / 1080) * 18;
  return (
    <>
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: `radial-gradient(120% 96% at ${px.toFixed(1)}% ${py.toFixed(1)}%, ${warm} 0%, transparent 58%)`,
        opacity: craft.light,
      }} />
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: `linear-gradient(${angle + 90}deg, transparent 38%, ${cool} 100%)`,
        opacity: craft.light * 0.9,
      }} />
    </>
  );
};

/** Vignette that tightens as the camera pushes in — the frame closing around
 *  the subject is most of why a close-up feels closer. */
export const Vignette: React.FC<{ craft: Craft; cam: CameraState; tint?: string }> = ({
  craft, cam, tint = "rgba(10,14,20,0.30)",
}) => {
  if (craft.light <= 0.01) return null;
  const tighten = Math.max(0, Math.min(1, (cam.scale - 0.8) / 1.6));
  const stop = 78 - tighten * 20;
  return (
    <div style={{
      position: "absolute", inset: 0, pointerEvents: "none",
      background: `radial-gradient(122% 100% at 50% 48%, transparent ${stop}%, ${tint} 100%)`,
      opacity: craft.light * (0.72 + tighten * 0.28),
    }} />
  );
};

/** Surface tooth. Deterministic, and it unifies drawn marks with treated
 *  photography by putting both under one grain. */
export const Grain: React.FC<{ craft: Craft; seed?: number }> = ({ craft, seed = 11 }) => (
  <svg width="100%" height="100%" aria-hidden
       style={{ position: "absolute", inset: 0, opacity: craft.grain, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id={`grain-${seed}`}>
      <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves={2} seed={seed} stitchTiles="stitch" />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <rect width="100%" height="100%" filter={`url(#grain-${seed})`} />
  </svg>
);

/** A halo on an accent element. On a light ground a true bloom reads as a
 *  smudge, so this is a tight coloured spread rather than a glow. */
export const glow = (color: string, craft: Craft, px = 14): string | undefined =>
  craft.bloom <= 0.02
    ? undefined
    : `drop-shadow(0 0 ${(px * craft.bloom).toFixed(1)}px ${color})`;
