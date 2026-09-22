import React from "react";
import { Easing, interpolate } from "remotion";
import type { Craft } from "./intensity";
import { stagger, settle } from "./motion";

// ---------------------------------------------------------------------------
// KINETIC TYPE
//
// Text that fades in is text arriving from nowhere. Text that rises into place,
// word by word, has been PUT there — and the eye reads the placement as intent.
//
// Motion-silencing constraint: the animation must be OVER before the words need
// to be read. Everything here settles inside ~0.5s and then holds absolutely
// still. Never stagger a line so long that its tail is still moving while the
// narration has moved on.
// ---------------------------------------------------------------------------

const clamp01 = (n: number) => Math.max(0, Math.min(1, n));

export const KineticText: React.FC<{
  text: string;
  t: number;
  at: number;
  craft: Craft;
  style?: React.CSSProperties;
  /** "word" reads as writing; "char" as stamping. Chars on long strings is noise. */
  unit?: "word" | "char" | "line";
  /** hide entirely once this passes 1 */
  out?: number;
}> = ({ text, t, at, craft, style, unit = "word", out = 0 }) => {
  const k = craft.kinetic;
  const parts = unit === "char" ? Array.from(text) : unit === "line" ? [text] : text.split(" ");
  const step = (craft.stagger * 0.6) * k;
  const vis = 1 - clamp01(out);
  if (vis <= 0.01) return null;

  return (
    <span style={{ display: "inline-block", whiteSpace: "pre-wrap", opacity: vis, ...style }}>
      {parts.map((p, i) => {
        const st = at + stagger(i, craft, step);
        const e = interpolate(t, [st, st + 0.34], [0, 1], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
        });
        if (e <= 0) return <span key={i} style={{ opacity: 0 }}>{p}{unit === "word" ? " " : ""}</span>;
        const wob = settle(t, st + 0.2, craft, 0.7, 0.5 * k);
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: Math.min(1, e * 1.5),
              transform:
                `translateY(${((1 - e) * 22 * k).toFixed(2)}px) ` +
                `rotate(${(((1 - e) * -2.2 + wob * 0.5) * k).toFixed(3)}deg)`,
              // the clip is what makes it read as revealed rather than faded
              clipPath: e < 1 ? `inset(${((1 - e) * 100).toFixed(1)}% 0 0 0)` : undefined,
              willChange: e < 1 ? "transform, opacity" : undefined,
            }}
          >
            {p}{unit === "word" ? "\u00a0" : ""}
          </span>
        );
      })}
    </span>
  );
};

/**
 * A figure that counts to its value.
 *
 * Use ONLY where the change itself is the subject — a bar growing to its
 * number. Everywhere else land the figure already settled, because a number
 * still ticking while the narration names it is a number the viewer never read.
 */
export const Counter: React.FC<{
  to: number; t: number; at: number; dur?: number;
  decimals?: number; suffix?: string; style?: React.CSSProperties;
}> = ({ to, t, at, dur = 0.55, decimals = 1, suffix = "", style }) => {
  const p = interpolate(t, [at, at + dur], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  return <span style={style}>{(to * p).toFixed(decimals)}{suffix}</span>;
};

/** A mask wipe — reveal by uncovering, matching the drawn language's draw-on. */
export const Wipe: React.FC<{
  p: number; from?: "left" | "up" | "right" | "down"; children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ p, from = "left", children, style }) => {
  const v = (1 - clamp01(p)) * 100;
  const inset =
    from === "left" ? `0 ${v}% 0 0` : from === "right" ? `0 0 0 ${v}%`
    : from === "up" ? `0 0 ${v}% 0` : `${v}% 0 0 0`;
  return <div style={{ clipPath: `inset(${inset})`, ...style }}>{children}</div>;
};
