# What we know

Standing summary. **Rewritten after each harvest** — the corpus is the source of
truth; this file is the readable version of it.

**Last harvest: 2026-09-10** · platform `youtube` · format `long_form` · all four
bands run.

---

## The headline

Ten findings survived the harvest. **Three are binding. Six inform only. One is
refused.**

That ratio is the most useful thing the harvest produced. Once you insist on a
contrast class, most of what is written about video virality stops qualifying as
evidence — not because it is false, but because nobody can say what it was
measured against.

---

## The three that carry weight

**f-001 — Arousal, not valence.** Content evoking high-arousal emotion (awe,
anger, anxiety) is passed on more; low-arousal deactivating emotion (sadness,
contentment) less — controlling for how interesting or useful it is. Measured
across the full population of 6,956 NYT articles in a three-month window, not a
sample of hits. *Published 2012 and it has not been dislodged.*

**f-002 — Practical utility travels.** Independently of emotional charge, content
someone can use or repeat is shared more. Same dataset, same denominator. This is
the finding that makes a takeaway worth designing.

**f-003 — Cascades die.** Almost all sharing chains stop after one hop. Broad
reach is overwhelmingly bought by a single large broadcast rather than earned
through person-to-person spread, and high structural virality is a statistical
outlier. Measured against the whole population of cascades, including the vast
majority that never propagate.

**Read together they say one thing:** you cannot engineer reach, so engineer the
one share you can — make the piece worth sending, once, by one person who
already trusts you, and give them something to say when they send it.

---

## The six that inform only

All six are `practitioner` grade. Every one may shape a decision; none may
justify one.

| | Claim | Why it is not binding |
|---|---|---|
| f-005 | YouTube now weights viewer *satisfaction* above raw watch time; session watch time is the heaviest input | Every source is an SEO aggregator restating the same claim. **Demoted from `platform`** — no first-party statement found. |
| f-006 | Shorts recommendation is fully decoupled from long-form | Structural claim, no measurement, no first-party source. |
| f-007 | Educational long-form averages 40–60% view duration | Aggregated benchmark blogs, no stated method. Useful as a sanity band, never as a target. |
| f-008 | Faces, ≤4 words of text, high contrast lift thumbnail CTR | Claims range +20% to 2.3×, all vendor blogs, no denominators. |
| f-009 | Psychological response and social motivation beat production quality; a small minority of sharers drive most shares | Very large view corpus, but method unpublished. Points the same way as f-001/f-002 — cite those instead. |
| — | *(f-004 is `platform`-graded but scoped to short-form; see below)* | |

**f-004 — the three-second window.** On vertical short-form, 50–65% of all
drop-off happens before 0:03, and platform guidance reports most
high-click-through videos establish their hook inside it. Graded `platform`,
scoped strictly to `<60s` vertical. It does **not** transfer to long-form, and
the lint enforces that as an error.

---

## The one refused

**f-010 — "a 3% share-to-view ratio means you've broken out."** A round number
recurring across content-marketing blogs with no traceable origin and no method.
Recorded as `folklore` with `status: refused` so it cannot arrive as a fresh
discovery on the next harvest.

---

## What the DISCONFIRM band found

Worth stating on its own, because it is the band most harvests skip.

The strongest disconfirming result is **f-003 itself**: the structure of sharing
means that reverse-engineering hits is close to worthless as a method. You are
looking at the tail of a distribution whose body is invisible, and the tactics
visible in the tail are usually present throughout the body too.

The practical consequence for this system: **treat every `practitioner` finding
as a hypothesis about a population you have never seen.** That is what the
grading is for.

---

## What is missing, and should be sought next harvest

- **A first-party YouTube source** for the satisfaction-signal reordering. If it
  exists, f-005 becomes binding and changes how pieces end.
- **Any controlled experiment on thumbnails** rather than vendor claims. YouTube's
  own Test & Compare generates exactly this data; published results would upgrade
  f-008 from practitioner to observational.
- **Base rates for the three-second rule on long-form.** Everything found is
  short-form. The equivalent number for a five-minute explainer is unknown here,
  and the corpus currently falls back to a conservative 3s default rather than
  guessing.
- **Post-publish outcomes from our own pieces** — see
  [`application.md`](application.md). It is the only route by which this corpus
  gets better than the internet it came from.
