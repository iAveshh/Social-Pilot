---
name: virality-research
description: Goes and looks at what actually makes video travel — live web harvest, graded by evidence quality into a persistent corpus — then forces every finding to be applied or refused on the record before a piece ships. Use when producing any video meant to reach people beyond an existing audience, or when the user asks what makes content go viral.
---

# Virality Research

Two halves that only work together:

1. **Harvest.** Traverse the web on demand, grade what comes back by the quality
   of its evidence, and keep it in a corpus that ages out by grade.
2. **Apply.** Every in-scope finding must be applied or refused **with a reason
   on the record** before the piece ships. `virality_lint.py` enforces it.

Without the second half the first is a reading list. Without the first the
second enforces whatever the model remembered.

## The thing this is really guarding against

Almost everything written about why videos go viral is **derived from winners
only**. "90% of viral videos hook in three seconds" is not a finding unless you
also know what fraction of *all* videos hook in three seconds. The graveyard is
invisible, so the same tactics keep getting credited for outcomes they did not
cause.

So the corpus refuses to store a claim without its **contrast class** — the
population it was compared against. An observational claim with no denominator
is automatically demoted to `practitioner`, however respectable the outlet.

**Read [`reference/method.md`](reference/method.md) before your first harvest.**
It is short and it is the part that makes this skill different from a listicle.

## Evidence grades

| Grade | What it takes | Half-life | May compel a decision? |
|---|---|---|---|
| `experimental` | Controlled or natural experiment with an effect size | never expires | **yes** |
| `observational` | Large-N correlation **with a stated contrast class** | 18 months | **yes** |
| `platform` | The platform's own documentation or statement | 6 months | **yes** |
| `practitioner` | Creator or agency claim, no visible denominator | 6 months | informs only |
| `folklore` | Repeated between blogs, no traceable origin | refused on sight | **never** |

Half-lives are **per grade, not global** — that is the whole point. A platform's
ranking behaviour rots in months. A result about human arousal does not rot at
all. Ageing them together is how a corpus quietly becomes wrong.

`observed_on` is the date **we** last verified a finding, not its publication
date. Re-harvesting refreshes it, which is why a 2012 paper sits in the corpus
as `active`.

## Running a harvest

```bash
python .claude/skills/virality-research/harvest.py plan --platform youtube --format long_form
```

That prints four bands of queries. Run **all four**, using your web tools:

| Band | What it is for |
|---|---|
| MECHANISM | why anything spreads. Peer-reviewed where it exists. |
| PLATFORM | how this surface ranks and distributes, right now. |
| PRACTICE | what working creators say. Mostly ungraded, and that's fine — grade it honestly. |
| **DISCONFIRM** | **who says the rest is wrong, and what the base rates are.** |

**A harvest that returns nothing from DISCONFIRM is not finished.** It has only
found the sources that agree with each other. That band is where the corpus gets
its `folklore` entries, and recording a refusal is as valuable as recording a
finding — it stops the same claim arriving as news on the next harvest.

Then grade the drafts before they go in:

```bash
python .claude/skills/virality-research/harvest.py grade --file draft.json
python .claude/skills/virality-research/corpus.py add --file draft.json
python .claude/skills/virality-research/corpus.py audit
```

`audit` is the maintenance verb. Run it at the start of any production — it
recomputes standing from dates rather than trusting the stored status, and tells
you what needs re-harvesting.

## Applying it to a piece

Write `artifacts/virality_packet.json` at the **proposal** stage, not after the
render — the title and the share trigger are structural decisions, and bolting
them on at the end is how a good piece ends up with a dishonest title.

```json
{
  "version": "1.0",
  "platform": "youtube", "format": "long_form", "duration_band": "5-20m",
  "hook":     { "promise": "...", "lands_by_seconds": 3.0 },
  "share_trigger": { "kind": "...", "at_seconds": 0, "why_they_send_it": "..." },
  "register": { "arousal": "low", "chosen_because": "...", "cost_accepted": "..." },
  "metadata": { "title": "...", "thumbnail_concept": "...", "description_first_line": "..." },
  "applied":  [{ "finding_id": "f-001", "how": "..." }],
  "refused":  [{ "finding_id": "f-004", "because": "..." }]
}
```

Then:

```bash
python .claude/skills/virality-research/virality_lint.py <project-slug>
```

## The hard rule

> **A virality finding may change HOW something is said. It may never change
> WHAT is true, what the piece argues, or whether the title is honest.**

If a finding can only be satisfied by overstating the content, it is **refused,
with that as the reason.** Write the refusal down — an unresolvable conflict
between reach and honesty is a real finding about the format, and the record of
it is worth more than the click.

This is not squeamishness. A title the piece does not deliver produces exactly
the steep early drop-off that every one of these findings says is fatal.

## Where it conflicts with the engagement model

[`engaging-explainer`](../engaging-explainer/SKILL.md) optimises for **being
watched to the end**. This skill optimises for **being passed on**. They are
different objectives and they genuinely collide:

| Tension | Resolution |
|---|---|
| Arousal lifts sharing (f-001), but a high-arousal register can undercut a teaching piece | The brief's `delivery_promise` wins. Keep the register low and spend the entire arousal budget on the single engineered peak — which is what both models want anyway. |
| A curiosity gap sells the click; a large gap kills curiosity (Loewenstein) | The title carries a **small** gap. Titles that promise a whole field produce low curiosity, not high. |
| On-screen text helps a muted scroll; duplicate text harms comprehension (Mayer, d=0.87) | Captions stay, styled recessive. Display text never restates narration. Unchanged. |
| Reach as an objective vs. f-003 (cascades die after one hop) | Never design for reach. Design for one deliberate share by someone who already trusts you. |

**When the two skills disagree, `engaging-explainer` wins on structure and this
skill wins on metadata.** Structure is what the viewer experiences; metadata is
what decides whether they arrive.

## What is in the corpus today

Ten findings, and the shape of them is the honest headline: **three are binding.
Six inform only. One is refused.** That ratio is not a failure of the harvest —
it is what this subject actually looks like once you insist on denominators.

The three that carry weight are arousal (f-001), practical utility (f-002), and
the cascade-death result (f-003), and all three point the same way: make one
thing worth passing to one person.

## Files

| File | What it is |
|---|---|
| `harvest.py` | The search plan, and the grader that keeps ungraded claims out |
| `corpus.py` | The store: `list`, `add`, `audit`. Ages findings out by grade. |
| `virality_lint.py` | The gate. Applied-or-refused, on the record. |
| `corpus/findings.json` | What we currently believe, and why |
| `reference/method.md` | How to traverse the web without fooling yourself |
| `reference/application.md` | How a finding becomes an authoring constraint |
| `reference/what-we-know.md` | The standing summary, rewritten after each harvest |

## Anti-patterns

- **Harvesting only winners.** Without a base rate you have described viral videos, not explained them.
- **Citing a practitioner claim as a reason.** It may inform. It may not justify.
- **Applying a short-form finding to long-form.** Scope is enforced for a reason; the surfaces were decoupled.
- **Writing the title after the render.** By then the piece cannot be changed to deserve it.
- **Treating reach as the objective.** f-003 says you cannot engineer it. Engineer the one share you can.
- **A corpus nobody audits.** Platform findings rot in months and nothing tells you except the audit.
