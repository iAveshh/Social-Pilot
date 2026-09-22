# Application

How a finding stops being a fact and becomes a constraint on the piece.

---

## Findings land in exactly one of five slots

| Slot | Decides | Locked at |
|---|---|---|
| `open` | what the first seconds promise, and when the promise is legible | script |
| `structure` | beat map, pacing, interrupt cadence, where the piece ends | scene_plan |
| `register` | the arousal dial, and what that choice costs | proposal |
| `share_trigger` | the **one** thing built to be sent to someone | proposal |
| `metadata` | title, thumbnail, first line of the description | **proposal, not post-render** |

A finding that fits no slot is trivia. `corpus.py` refuses to store a binding
finding without an `application` sentence for exactly this reason.

---

## Metadata is a proposal decision

The strongest temptation in this whole process is to write the title after the
render, when you can see what you've got. Resist it, because at that point the
only tool left is overstatement — the piece is fixed, so the title has to stretch
to cover it.

Decide the title and thumbnail at proposal and then **build the piece that
deserves them.** If the finished piece no longer earns the title, the fix is to
change the title down, never the claim up.

---

## The share trigger

Sharing is a separate design object from watching, and it is the one most
explainers never build at all.

**Name one moment.** Not a general quality — a specific place in the piece with
a timestamp, and a sentence saying *who the viewer sends it to and why.*

The graded findings say it should be one of:

- **a takeaway they can use or repeat** (f-002: practical utility) — a rule, a
  test, a number worth quoting;
- **a single high-arousal beat** (f-001: awe or surprise) — usually a scale
  revelation or an inversion, which is the engineered peak you already have.

The cheapest correct answer for an explainer is usually: *the peak is the share
trigger.* If the peak is genuinely the most surprising thing in the piece, it is
also the thing someone will paste into a group chat with "watch from 3:50".

**One, not several.** Several weak reasons to share is worse than one strong
one, for the same reason two medium peaks are worse than one large one.

---

## The register dial, and its price

f-001 is graded and it is uncomfortable: low-arousal content measurably
travels less, controlling for how interesting or useful it is. Calm is a
**choice with a cost**, not a neutral default.

That does not mean shouting. It means:

1. Choose the register deliberately and **write the cost down** in the packet.
   `virality_lint` errors if `cost_accepted` is missing — not because the choice
   is wrong, but because an unexamined one is.
2. If the piece runs low-arousal by design — most good explainers do — then
   concentrate the **entire** arousal budget in the one engineered peak. Both
   models want this: the engagement model wants one maximum, and the arousal
   finding wants intensity somewhere.

A flat five minutes with no peak fails both.

---

## Refusal is a first-class outcome

`virality_lint` requires every in-scope binding finding to be applied **or
refused with a reason.** Refusing well is the skill.

Good refusals name the conflict:

> *f-004 refused: the three-second window is measured on vertical short-form and
> its scope does not cover a five-minute long-form explainer. The piece opens
> with an event at 0:00 anyway, for reasons from the engagement model rather
> than this one.*

> *f-008 refused: a face with a clear emotion is not available to a drawn
> explainer with no presenter, and inventing one would misrepresent the piece.
> The traceable part of the finding — contrast and word count — is applied.*

Bad refusals restate the finding and say "not applicable" with no reason. The
lint cannot tell the difference, which is precisely why the reason has to be
worth reading by a person.

---

## What a finding may never do

> **A finding may change HOW something is said. It may never change WHAT is
> true, what the piece argues, or whether the title is honest.**

Concretely, refuse — and record the refusal — if satisfying a finding would
require:

- a title the piece does not deliver;
- a number stated more strongly than the source supports;
- an omitted caveat that changes the meaning;
- a manufactured antagonist, or outrage the material does not contain;
- a peak placed where the argument does not actually peak.

Every one of those buys a click and pays for it with the early drop-off that the
same findings identify as fatal. The trade is not merely dishonest; on the
evidence, it does not even work.

---

## Post-publish, if numbers come back

If real performance data ever exists for a piece, it is the only
`experimental`-adjacent evidence this system can generate for itself. Record it:

- what the packet predicted,
- what happened,
- and — the valuable half — **which applied findings were followed by nothing.**

A finding that has now been applied three times with no visible effect should be
demoted, with that history as the reason. That is the one path by which this
corpus can get better than the internet it was harvested from.
