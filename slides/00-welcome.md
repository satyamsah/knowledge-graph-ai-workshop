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

Run these one at a time together with the room:

```bash
# 1. Start the database
docker compose up -d

# 2. Create Python environment (Mac/Linux use python3)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# open .env and paste your ANTHROPIC_API_KEY

# 5. Verify everything
python check_setup.py
```

Expected output:
```
✓ Neo4j connected (localhost:7687)
✓ Anthropic API reachable
✓ You're all set — see you at the workshop!
```

---

## Common errors and fixes

| Error | Fix |
|-------|-----|
| `command not found: python` | Use `python3` instead |
| `source: no such file or directory: .venv/bin/activate` | Run `python3 -m venv .venv` first |
| Neo4j not connecting | `docker compose up -d`, wait 20 seconds, retry |
| API key error | Check `.env` has the key, no quotes, no trailing spaces |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |

---

## Facilitator notes

- Run each command live on your screen — participants follow along
- Wait for the room before moving to the next command
- Have a chat window open for people to paste errors
- If someone can't get Docker running: Neo4j AuraDB free tier at aura.neo4j.io
