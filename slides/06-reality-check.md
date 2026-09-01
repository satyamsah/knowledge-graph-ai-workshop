# Slide Deck: 06 — The Hard Truth About Knowledge Graphs
### (after Exercise 2, ~10 min — before querying)

---

## Slide 1 — A confession

The dataset we just loaded took 10 minutes to seed.

It took much longer to *design*.

Every node, every relationship type, every property — each one was a decision.
That work doesn't go away just because we have AI.

---

## Slide 2 — The hype vs. the reality

**What people expect:**
> "LLMs understand semantics. I'll just feed my corpus to an AI agent
> and it'll build my Knowledge Graph for me. How hard can it be?"

**What actually happens:**
> 90–95% of the AI-generated tuples are useless for the
> specific questions you actually need to answer.

Your system ends up pursuing thousands of wrong paths on every query.

---

## Slide 3 — Why AI-generated graphs are noisy

LLMs are great at *extracting* relationships from text.
They are not good at *deciding which relationships matter* for your use case.

They will give you:
- Duplicates with slightly different names (`Apple Inc.` vs `Apple`)
- Orphan nodes nothing connects to
- Relationships that are technically true but answer no useful question
- Inconsistent relationship types (`WORKS_AT`, `EMPLOYED_BY`, `WORKS_FOR`)
- Properties that sound meaningful but add no traversal value

All of it *looks* like a graph. None of it *behaves* like one.

---

## Slide 4 — Occam's Razor is alive and well

> "The simplest graph that answers your questions is the best graph."

The dataset we built today has:
- 10 companies, 10 people, 25 products
- 5 relationship types
- Every single node is reachable
- Every single relationship is queryable

A naive AI-generated graph of the same domain might have 500 nodes,
40 relationship types, and answer your questions worse.

**Smaller. Intentional. Purposeful.**

---

## Slide 5 — The work that doesn't disappear

Building a Knowledge Graph still requires:

| Task | What it involves |
|------|-----------------|
| **Domain modeling** | What questions do I need to answer? What are the real entities? |
| **Relationship design** | What traversals matter? What types are distinct vs. redundant? |
| **Data cleaning** | Deduplication, orphan resolution, normalising property values |
| **Inference review** | If the AI inferred a relationship — is it actually true? |
| **Iteration** | Your first model will be wrong. Plan for it. |

AI can *assist* with each of these. It cannot replace the judgment.

---

## Slide 6 — The analogy that holds

This is exactly like data modeling.

Modern tooling makes it cheap to create a new data model per query —
so you end up with dashboard-driven development: a mess of schemas,
each optimised for one thing, none flexible enough to grow.

Building a data model with the flexibility to answer *future* questions
requires a more thoughtful, sophisticated design up front.

**Knowledge Graphs are the same.**

Building a KG is easy.
Building a *simple* KG that captures only the essential knowledge —
and evolves cleanly — takes longer and costs more than just AI tokens.

---

## Slide 7 — What this means for you

The hard work is the valuable work.

Anyone can run `pip install neo4j` and call an LLM API.
The skill — the thing worth putting on your resume — is:

- Knowing *what* to model and *why*
- Recognising when a relationship adds value vs. noise
- Designing a graph that answers tomorrow's questions, not just today's
- Understanding when GraphRAG is the right tool and when it isn't

That judgment only comes from doing the work.

---

## Facilitator talking points

This slide is most powerful if you make it personal. Say something like:

> "I want to be honest with you about something before we get into queries.
> The data we just loaded looks clean because it was designed carefully.
> I spent time on what to include and what to leave out.
> Let me tell you what happens when you skip that step..."

Then walk through slides 2–4. The audience will nod — they've felt this pain
in other contexts (messy databases, sprawling spreadsheets, over-engineered schemas).

Close with slide 7 — reframe the hard work as the competitive advantage.

> "The people who will do well with Knowledge Graphs are not the ones
> who find the best AI tool to generate them automatically.
> They're the ones who understand the domain well enough to know
> what a good graph looks like."
