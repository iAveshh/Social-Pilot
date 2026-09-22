# Method

How to traverse the web on this subject without coming back with confident
nonsense.

---

## 1. The denominator is the whole discipline

Every claim about virality has the same shape: *videos that did X went viral.*
The question that decides whether it means anything is always the same:

> **What fraction of videos that did X did *not* go viral?**

Nobody publishes that number, because the people writing about virality are
looking at winners. So the corpus makes it structural: an observational finding
without a `contrast_class` is demoted to `practitioner` automatically, and
`corpus.py` refuses to store it as observational at all.

**A good contrast class names a population, not a vibe.** "All 6,956 NYT
articles published in the window" is a contrast class. "Compared to typical
content" is not.

### The two questions to ask any source

1. **Where are the failures?** A source that shows only successes has no
   denominator, whatever its N.
2. **Would this claim survive if the outcome were reversed?** If a feature is
   present in the hits *and* in everything else, it explains nothing.

---

## 2. Prestige does not upgrade evidence

A large media brand reporting an industry study with no published method is
still `practitioner`. A vendor blog quoting a platform's own documentation and
linking it is `platform`. The grade attaches to **the traceable method**, never
to the masthead.

This is why `harvest.py grade` flags a `platform`-graded finding with no
first-party source. In practice most "the algorithm changed in 2026" claims
trace back to a handful of SEO aggregators restating each other, and none of
them to the platform. Grade them honestly and they become useful anyway — as
`practitioner` findings that inform without compelling.

---

## 3. Record the refusals

When the DISCONFIRM band turns up a claim that does not survive — a round number
with no origin, a statistic that traces to nothing — **write it into the corpus
as `folklore` with `status: refused` and a reason.**

This is the least obvious and most useful habit here. An unrecorded refusal
comes back as a fresh discovery on the next harvest, and eventually somebody
acts on it. A recorded one is permanently disarmed, and `virality_lint` will
error if anyone tries to apply it.

---

## 4. Scope before belief

A finding is never true in general. It is true for a platform, a format and a
duration band. The three-second hook window is a real, measured property of
vertical short-form; applied to a twenty-minute documentary it is a superstition
wearing the authority of evidence.

Since the short and long surfaces on YouTube were decoupled, this stopped being
a nicety: findings genuinely do not transfer between them, and the lint enforces
scope as an ERROR rather than a warning.

---

## 5. Age by grade, not by date

Three kinds of knowledge rot at three different speeds:

- **How people work** — arousal, curiosity, memory. Does not rot.
- **How a platform ranks** — rots in months, silently, and the platform will not
  announce it.
- **What creators believe** — rots fastest of all, and circulates longest.

A single "refresh every six months" policy either throws away durable results or
keeps stale ranking claims. `corpus.py audit` recomputes standing per grade from
`observed_on`, and `observed_on` is the date *we* last checked — so re-running a
harvest genuinely revalidates rather than just re-dating.

---

## 6. Harvest cadence

| When | What |
|---|---|
| Start of any production | `corpus.py audit`. If nothing is stale, do not harvest. |
| A platform finding goes stale | Re-run the PLATFORM and DISCONFIRM bands only. |
| New format or platform | Full four-band harvest, scoped to it. |
| A piece under-performs against its band | Harvest DISCONFIRM first, not PRACTICE. The failure is more informative than the advice. |

Harvesting when nothing is stale wastes the run and tempts you to add
low-grade findings for the sake of a result.

---

## 7. What a finished harvest looks like

- Every band ran, including DISCONFIRM.
- Every new finding has a grade, a scope, a source, and — if it is binding — an
  `application` written as one imperative sentence.
- At least one refusal recorded, or a note saying the DISCONFIRM band found
  nothing new to refuse.
- `corpus.py audit` exits clean.

If the harvest produced only findings that agree with each other, it is not
finished. It is a reading list with a date on it.
