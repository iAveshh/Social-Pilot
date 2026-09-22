import React from "react";
import { planeTransform, type CameraState } from "./camera";
import type { Craft } from "./intensity";

// ---------------------------------------------------------------------------
// DEPTH
//
// Four planes is the difference between a camera move that reads as a zoom and
// one that reads as space. Nothing here adds information — it adds the spatial
// cues the eye uses to believe a frame has volume.
// ---------------------------------------------------------------------------

/** Conventional depths. Anything outside 0..1.6 starts to read as a mistake. */
export const Z = {
  ground: 0.0,     // the surface itself — never moves
  far: 0.40,       // distant structure, faint
  mid: 0.72,       // supporting marks
  subject: 1.0,    // what the narration is talking about
  fore: 1.45,      // occluders that pass in front
} as const;

/**
 * Contrast falls off with distance. Depth is carried by TONE far more than by
 * movement, which is why a flat-contrast parallax still reads flat.
 */
export const depthDim = (k: number, craft: Craft): number => {
  const d = 1 + (k - 1) * craft.parallax;
  if (d >= 1) return 1;
  return 0.34 + 0.66 * Math.max(0, d);
};

export const Plane: React.FC<{
  cam: CameraState;
  craft: Craft;
  z: number;
  /** override the automatic contrast falloff */
  dim?: number;
  children: React.ReactNode;
}> = ({ cam, craft, z, dim, children }) => {
  const o = dim ?? depthDim(z, craft);
  if (o <= 0.004) return null;
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        transform: planeTransform(cam, z, craft),
        transformOrigin: "0 0",
        opacity: o,
        willChange: "transform",
      }}
    >
      {children}
    </div>
  );
};

/**
 * A foreground element that crops off-frame as the camera moves.
 *
 * Objects running past the frame edge are what imply a world larger than the
 * frame. A composition where everything is fully contained reads as a diagram
 * of a thing rather than the thing itself.
 */
export const Foreground: React.FC<{
  cam: CameraState; craft: Craft; children: React.ReactNode; z?: number;
}> = ({ cam, craft, children, z = Z.fore }) => (
  <Plane cam={cam} craft={craft} z={z} dim={1}>{children}</Plane>
);
