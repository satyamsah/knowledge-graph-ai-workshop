# Slide Deck: 01 — RAG, the Big Picture
### (0:15–0:45, 30 min)

---

## Slide 1 — The problem with plain LLMs

You ask ChatGPT: *"What is the latest iPhone model?"*

It answers confidently — but its knowledge has a **cutoff date**.
It might be wrong. It can't tell you when it's wrong.

**Root cause:** The LLM has memorised patterns from training data.
It doesn't *look things up* — it *remembers* (imperfectly).

---

## Slide 2 — What is RAG?

**R**etrieval-**A**ugmented **G**eneration

The idea: before the LLM answers, *fetch relevant context* and include it in the prompt.

```
User question
     ↓
[Retrieval step]  →  find relevant documents / chunks
     ↓
Augmented prompt  =  question + retrieved context
     ↓
LLM generates answer grounded in that context
```

---

## Slide 3 — How retrieval works (vector search)

1. At index time: split documents into chunks, embed each chunk → vector
2. At query time: embed the question → vector, find nearest chunks by cosine similarity
3. Pass top-k chunks as context to the LLM

```
"Who is the CEO of Apple?"
         ↓ embed
[0.23, -0.11, 0.87, ...]
         ↓ nearest neighbours
"Tim Cook became CEO in 2011..."   ← chunk retrieved
         ↓ LLM
"The CEO of Apple is Tim Cook."
```

---

## Slide 4 — RAG works well for…

- Answering questions about a document corpus
- Summarising a PDF
- "Chat with your codebase" tools

---

## Slide 5 — Where RAG struggles

**Relationships are hidden in text.**

> "Which companies make products that compete with the iPhone?"

To answer this from documents you'd need to:
- Find every mention of iPhone competitors
- Resolve that Samsung Galaxy, Google Pixel, etc. are products
- Know they are made by different companies

Vector search gives you *similar text* — it doesn't give you *structured relationships*.

---

## Slide 6 — The gap RAG can't fill

| Question type | RAG | Knowledge Graph |
|---|---|---|
| "What does document X say about Y?" | ✓ | — |
| "Who is related to whom?" | ✗ | ✓ |
| "What are all products made by company X?" | ✗ | ✓ |
| "Find the path between A and B" | ✗ | ✓ |
| "Count / aggregate facts" | ✗ | ✓ |

---

## Slide 7 — The fix: add a Knowledge Graph

Instead of retrieving text chunks, we retrieve **graph facts**.

```
User question
     ↓
LLM translates question → structured graph query (Cypher)
     ↓
Graph database returns exact facts + relationships
     ↓
LLM synthesises answer from structured results
```

This is **GraphRAG** — and it's what we'll build today.

---

## Live demo (5 min) — feel the difference

Show two answers side by side:

**Plain LLM:**
```
Q: Which Google products compete with Microsoft products?
A: Google Workspace and Microsoft 365 are competitors... [generic, possibly stale]
```

**GraphRAG (what we'll build):**
```
Q: Which Google products compete with Microsoft products?
A: From the knowledge graph:
   - Google Docs ↔ Microsoft Word
   - Google Sheets ↔ Microsoft Excel
   - Google Meet ↔ Microsoft Teams
   - Chrome OS ↔ Windows
```

---

## Facilitator notes

- Keep slides fast here — the goal is intuition, not completeness
- The live demo is the most important part: show the output difference
- Good question to ask the room: "What kind of questions do you ask where the answer depends on *relationships*?"
