# Slide Deck: 00 — Welcome & Setup
### (0:00–0:15, 15 min)

---

## Slide 1 — Welcome

**Knowledge Graphs for AI**
*A 3.5-hour hands-on workshop*

Today you will:
- Understand what a Knowledge Graph is and why it matters
- Build one from scratch using real data
- Connect it to an LLM to create a smart Q&A assistant
- Walk away with a project you can put on your resume

---

## Slide 2 — What we're building

A question-answering assistant that knows the tech world:

```
You:  Who founded Apple and what products did they make?
AI:   Steve Jobs and Steve Wozniak co-founded Apple. Their flagship
      products include the iPhone, MacBook, iPad, and macOS.
      Jobs also founded Pixar and NeXT.
```

The AI doesn't just guess — it queries a graph database and reasons over structured facts.

---

## Slide 3 — The journey today

```
Plain LLM      →  fast, but makes things up
    ↓
RAG            →  grounds answers in documents, but misses relationships
    ↓
Knowledge Graph →  captures who, what, and how things relate
    ↓
GraphRAG       →  LLM + graph = accurate, relationship-aware answers  ← we build this
```

---

## Slide 4 — Setup check

Ask everyone to run:

```bash
python check_setup.py
```

Expected output:
```
✓ Neo4j connected
✓ Anthropic API reachable
✓ Ready for the workshop!
```

> **If Neo4j fails:** `docker compose up -d` then wait 20 seconds and retry.
> **If API fails:** open `.env` and paste your key.

---

## Facilitator notes

- Do the setup check live on screen so people can follow along
- Have a Slack/Discord/chat open for people to paste errors
- If someone can't get Docker running: Neo4j AuraDB has a free cloud tier at aura.neo4j.io
