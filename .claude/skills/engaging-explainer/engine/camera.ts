import { Easing, interpolate } from "remotion";
import type { Craft } from "./intensity";

// ---------------------------------------------------------------------------
// THE CAMERA RIG
//
// A piece with one camera position is a slide deck, however well the slides are
// drawn. The visual system has always prescribed a real distance range; this is
// the machinery that makes using it the path of least resistance.
//
// A 6% scale change is invisible. If a push is worth doing it is worth 1.4x.
// ---------------------------------------------------------------------------

export const SHOT = {
  establishing: 0.55,   // subject small in a large field, composed asymmetrically
  wide: 0.80,
  medium: 1.00,
  close: 1.60,
  detail: 2.40,         // crops off-frame deliberately
} as const;

export const FRAME_W = 1920;
export const FRAME_H = 1080;
const CX = FRAME_W / 2;
const CY = FRAME_H / 2;

export type Move = "cut" | "move" | "drift";

export interface Shot {
  /** seconds — always a real beat time, never a guess */
  at: number;
  scale: number;
  /** the point the camera centres on, in 1920x1080 layout coordinates */
  x?: number;
  y?: number;
  /** degrees. Keep it under ~1.2 or it reads as a mistake. */
  rot?: number;
  /** how the camera ARRIVES at this shot */
  move?: Move;
}

export interface CameraState {
  scale: number;
  x: number;
  y: number;
  rot: number;
}

const EASE: Record<Move, (n: number) => number> = {
  cut: () => 1,
  move: Easing.inOut(Easing.cubic),
  drift: Easing.inOut(Easing.sin),
};

/**
 * Resolve the camera at time `t`.
 *
 * `craft.camera` scales every move away from the resting medium shot, so the
 * same shot list reads restrained at `austere` and cinematic at `lush` without
 * re-authoring a single keyframe.
 */
export const camera = (t: number, shots: Shot[], craft: Craft): CameraState => {
  if (!shots.length) return { scale: 1, x: CX, y: CY, rot: 0 };
  const list = [...shots].sort((a, b) => a.at - b.at);

  const full = (s: Shot): CameraState => ({
    scale: s.scale, x: s.x ?? CX, y: s.y ?? CY, rot: s.rot ?? 0,
  });

  let state: CameraState;
  if (t <= list[0].at) {
    state = full(list[0]);
  } else {
    let i = list.length - 1;
    for (let j = 0; j < list.length - 1; j++) {
      if (t >= list[j].at && t < list[j + 1].at) { i = j; break; }
    }
    if (i === list.length - 1) {
      state = full(list[i]);
    } else {
      const a = list[i], b = list[i + 1];
      const mv = b.move ?? "move";
      // A cut holds the outgoing shot until the very frame it changes. That
      // hard switch between distances is one of the strongest attention events
      // available, and it costs nothing.
      const p = mv === "cut"
        ? (t >= b.at ? 1 : 0)
        : interpolate(t, [a.at, b.at], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE[mv],
          });
      const A = full(a), B = full(b);
      state = {
        scale: A.scale + (B.scale - A.scale) * p,
        x: A.x + (B.x - A.x) * p,
        y: A.y + (B.y - A.y) * p,
        rot: A.rot + (B.rot - A.rot) * p,
      };
    }
  }

  // Scale the whole move away from a resting medium shot by the intensity dial.
  const k = craft.camera;
  return {
    scale: 1 + (state.scale - 1) * k,
    x: CX + (state.x - CX) * k,
    y: CY + (state.y - CY) * k,
    rot: state.rot * k,
  };
};

/**
 * The CSS transform for a plane at depth `k`.
 *
 *   k = 0    infinitely far — never moves (the ground itself)
 *   k = 0.4  far background
 *   k = 1    the subject plane, exactly matching the camera
 *   k = 1.5  foreground occluders, moving MORE than the subject
 *
 * Parallax is what makes camera movement read as space rather than as zoom.
 * With every element on one plane a push is just a scale; with four planes the
 * same push builds a world.
 */
export const planeTransform = (cam: CameraState, k: number, craft: Craft): string => {
  const d = 1 + (k - 1) * craft.parallax;      // dial-scaled depth separation
  const s = 1 + (cam.scale - 1) * d;
  const x = CX + (cam.x - CX) * d;
  const y = CY + (cam.y - CY) * d;
  const tx = CX - x * s;
  const ty = CY - y * s;
  const rot = cam.rot * d;
  return `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${s.toFixed(4)}) rotate(${rot.toFixed(3)}deg)`;
};

/**
 * Breathing for a held shot — enough to keep the frame alive, far too slow to
 * notice as movement.
 *
 * Drive this from a held clock so a freeze genuinely arrests the camera too.
 * A "freeze" that leaves the camera drifting reads as a stutter, not a stop,
 * and wastes the single strongest attention event in the toolkit.
 */
export const breathe = (ct: number, craft: Craft, amount = 0.018): number =>
  1 + amount * craft.camera * Math.sin(ct * 0.19);

/** A handheld micro-sway. Use sparingly — it suits reportage, not diagrams. */
export const sway = (ct: number, craft: Craft, amount = 3): { x: number; y: number } => ({
  x: amount * craft.camera * Math.sin(ct * 0.23),
  y: amount * 0.6 * craft.camera * Math.sin(ct * 0.31 + 1.1),
});

/**
 * Build a shot list from act boundaries: establish wide, settle to medium,
 * and cut close for the peak.
 *
 * A reasonable default when a piece has no strong opinion about its own
 * camera — but a hand-authored list keyed to the beats is always better,
 * because the camera should be reacting to what is actually being said.
 */
export const shotsFromActs = (
  acts: Record<string, number>,
  peakAt: number,
  end: number,
): Shot[] => {
  const starts = Object.values(acts).sort((a, b) => a - b);
  const out: Shot[] = [];
  starts.forEach((s, i) => {
    out.push({ at: s, scale: i === 0 ? SHOT.wide : SHOT.establishing, move: "cut" });
    out.push({ at: s + 2.2, scale: SHOT.medium, move: "move" });
  });
  out.push({ at: peakAt - 0.9, scale: SHOT.medium, move: "move" });
  out.push({ at: peakAt, scale: SHOT.close, move: "cut" });     // the peak lands as a CUT
  out.push({ at: peakAt + 5.0, scale: SHOT.medium, move: "drift" });
  out.push({ at: end - 9, scale: SHOT.wide, move: "move" });
  return out.sort((a, b) => a.at - b.at);
};
