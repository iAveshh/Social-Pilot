# Production Gotchas

Every item here cost a real render cycle to discover during
`projects/how-agents-work-reel/`. Read before authoring a composition.

---

## 1. `.clip` forces `height: 100%` — it will silently break your centering

The HyperFrames runtime's `.clip` class sets:
```css
position: absolute; top: 0; left: 0; width: 100%; height: 100%;
```

So a clip element you style with `top: 50%; transform: translateY(-50%)` for
vertical centering does **not** center. `height: 100%` makes the box span the
whole frame, `top: 50%` + `translateY(-50%)` cancels back to `top: 0`, and the
content renders pinned to the **top of the frame**.

Same trap with `bottom: 140px` — combined with the inherited `top: 0`, the box
stretches from 0 to (frame − 140) and the text sits at the *top* of that box.

**Fix:** explicitly override on the element (an ID selector beats `.clip`):
```css
#my-clip { height: auto; top: auto; bottom: 140px; }
```

**This passes `check` cleanly.** Only frame inspection catches it. It shipped
into a render before being caught.

---

## 2. `fromTo()` that starts hidden must set the visible state in the *destination*

```js
// BROKEN — lint: gsap_cold_seek_hidden_fromto_missing_reveal
tl.fromTo("#strike", { opacity: 1, scaleX: 0 }, { scaleX: 1, duration: 0.45 }, 11.15);

// CORRECT
tl.fromTo("#strike", { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.45 }, 11.15);
```
The element is authored `opacity: 0` in CSS. Cold render workers restore the
authored state before seeking, so if the destination vars don't explicitly
establish `opacity: 1`, the element encodes **invisible** — even though
sequential preview looks correct. `check` catches this one; don't ignore it.

---

## 3. Two tweens on the same property/element at overlapping times

A yoyo pulse that runs long will collide with a later tween on the same
property. GSAP's overwrite behavior is order-dependent and can differ between
renders (a determinism violation).

```js
// pulse: start 2.2, duration 0.9, repeat 2 → runs until 4.9s
// escape: starts 3.5, also animates opacity → OVERLAP
```
**Fix:** shorten the repeat so the pulse finishes before the next tween starts
(`duration: 0.6, repeat: 1` → ends 3.4), or pass `overwrite: "auto"`.

---

## 4. Layout checks measure raw bounding boxes, ignoring `overflow: hidden`

A scrolling ticker clipped to a 200px window still reports its **full content
height** (e.g. 12 lines x 30px = 360px) to the layout checker. That phantom box
collides with anything nearby and produces a wall of `content_overlap` errors.

**Fixes, in order of preference:**
1. Shrink the actual content so the raw box stays inside its zone (fewer lines).
2. Keep foreground content clear of the raw box's footprint.
3. Only as a last resort: `data-layout-allow-overlap="true"`.

`data-layout-allow-*` attributes on a **parent** did not reliably suppress
findings on its children. Fixing the geometry is more dependable than the
escape hatch.

---

## 5. Overlapping acts collide even while fading

If Act 1 is still fading out while Act 2's elements exist, the checker flags
their text as overlapping — opacity does not exempt them.

**Fix:** make act handoffs strictly sequential.
```
act1: start 0     duration 5.6   (inner fades 5.05–5.4, hard-kill set at 5.6)
act2: start 5.45  duration 6.9   (first tween at 5.5)
act3: start 12.35 duration 7.15  (first tween at 12.6)
```
Fade the **inner wrapper**, not the clip element itself, and always pair the
fade with a `tl.set(..., { opacity: 0 }, <clip end>)` hard kill — otherwise
lint raises `gsap_exit_missing_hard_kill`.

---

## 6. Use `check`, never `validate`

`npx hyperframes validate` is deprecated and **hung indefinitely** (killed after
8+ minutes, twice, with no output past the GPU probe). `npx hyperframes check`
is its superset — lint + runtime + layout + motion + contrast — and returns in
~30s.

If a node process does hang, `TaskStop` only kills the shell wrapper. Kill the
real process:
```powershell
Get-Process node | Select-Object Id, StartTime
Stop-Process -Id <id> -Force
```
Then delete the orphaned `renders/.hyperframes_*.hf-transaction-*` directory
before re-rendering.

---

## 7. Contrast: decorative text still has to pass WCAG AA

Ambient/background text is checked like any other text. `#4a4a52` on near-black
scored 2.25:1 (needs 4.5:1). Compounding a dim color *with* a parent
`opacity: 0.6` makes it worse.

**Fix:** pick one mechanism, not both. `#79797f` at full opacity passes and
still reads as subtle. `check` prints the exact passing color to use.

---

## 8. Stick to the deterministic property allowlist

Animate only: `opacity`, `x`, `y`, `scale`, `rotation`, `color`,
`backgroundColor`, `borderRadius`, transforms.

Notably **not** `background-position` — drift a grid by putting the pattern on
an oversized child and animating its `x`/`y` inside an `overflow: hidden`
parent instead. "Draw-on" lines are `scaleX`/`scaleY` from 0 with
`transformOrigin` set — no need for stroke-dashoffset or the paid DrawSVG
plugin.

Also banned: `repeat: -1` (use a finite count), `Math.random()` without a seed,
`Date.now()`, network fetches, and building timelines inside async callbacks.

---

## 9. Media and clip placement rules

- `<audio>`/`<video>` must be **direct children of the composition root**.
- Visible timed elements need `class="clip"` plus `data-start` and
  `data-duration`; clips must be direct children of the root.
- Clips sharing a `data-track-index` must not overlap in time — give
  concurrent layers distinct indices.
- Volume: a `volume` tween is **absolute** and replaces `data-volume`. Set
  `data-volume="1"` and carry the level entirely in the timeline
  (`tl.set("#bgm", { volume: 0.22 }, 0)`), or lint flags the conflict.

---

## 10. Fonts

The deterministic font compiler only inlines fonts it maps. Safe:
**Inter**, **JetBrains Mono**, Outfit, Montserrat, Poppins, Playfair Display.
`Space Grotesk` silently falls back to Arial.

---

## 11. Rotating an SVG shape about a hinge

Any device where a part swings — a padlock shackle opening, a gate arm, a
needle, a lid — rotates about a *hinge*, not its own centre. Two traps, and
both render silently wrong rather than erroring:

**CSS `transform-origin` does not resolve in viewBox units.** Given
`<svg width="260" height="292" viewBox="0 0 160 180">`, writing
`#shackle { transform-origin: 114px 80px; }` does **not** pivot at user-space
(114, 80) — the part detaches and swings from the wrong point. Use GSAP's
`svgOrigin`, which is specified in viewBox user units, and set it in **both**
`fromTo` vars:

```js
tl.fromTo("#shackle",
  { rotation: 0,  svgOrigin: "114 80" },
  { rotation: 38, svgOrigin: "114 80", duration: 0.45, ease: "back.out(1.6)" }, 11.62);
```

**The swung part leaves the viewBox and gets clipped.** SVG defaults to
`overflow: hidden`, so a shackle that rotates up past `y=0` simply vanishes and
you are left with a lone lock body. Add `#lock svg { overflow: visible; }` (and
`data-layout-allow-overflow="true"` on the wrapper).

Sign convention: **positive rotation is clockwise.** Hinging on the *right* leg
means positive lifts the left leg up and open; negative buries it in the body.
Work the destination corner out on paper before rendering — the checker cannot
tell "open" from "swung the wrong way through the lock".

`check` reports this as a `rotation_pivot_drift` **warning**, never an error,
and the number is the tell: a correct hinge drifts tens of pixels (a hinged
part's bbox centre legitimately moves), a broken one drifts hundreds. Chase the
number down, but do not expect it to reach zero — for a hinge it should not.
