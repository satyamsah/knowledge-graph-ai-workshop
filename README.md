# Knowledge Graphs for AI
### A 3.5-hour hands-on workshop

> Build a GraphRAG system from scratch — powered by Neo4j and an LLM.

---

## What you will build

A question-answering assistant that knows about real tech companies and their products.
Ask it anything:

```
You: Which companies make products that compete with Apple?
AI:  Based on the knowledge graph: Google (Android, Chrome), Microsoft (Surface,
     Windows), and Samsung (Galaxy) all make products that directly compete with
     Apple's iPhone, Mac, and browser lineup.
```

The answer comes from a **Knowledge Graph** — structured, relationship-aware data —
not from the LLM's training memory. That means it's accurate, explainable, and yours
to control.

> **During the session — open [`WORKSHOP.md`](WORKSHOP.md) and follow it top to bottom.**

---

| Time | Block | Format |
|------|-------|--------|
| 0:00–0:15 | Setup & welcome | Setup |
| 0:15–0:45 | RAG — the big picture | Slides + demo |
| 0:45–1:15 | Knowledge Graphs 101 | Slides + exercise 1 |
| 1:15–1:30 | ☕ Break | — |
| 1:30–2:00 | Modeling & loading data | Slides + exercise 2 |
| 2:00–2:30 | Querying the graph | Slides + exercise 3 |
| 2:30–3:00 | Connecting the LLM | Slides + exercise 4 |
| 3:00–3:30 | End-to-end project + Q&A | Live coding |

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | `python3 --version` to check (Mac/Linux use `python3`) |
| Docker Desktop | [docker.com/get-started](https://www.docker.com/get-started) |
| Anthropic API key | [console.anthropic.com](https://console.anthropic.com) — free tier works |
| A terminal | Any OS |

No prior database or graph experience needed.

---

## Setup (do this before the session)

### 1. Get the code

```bash
git clone https://github.com/your-org/knowledge-graph-ai-workshop
cd knowledge-graph-ai-workshop
```

### 2. Start Neo4j (the graph database)

```bash
docker compose up -d
```

Wait about 20 seconds, then open **http://localhost:7474** in your browser.
You should see the Neo4j Browser. Log in with:
- Username: `neo4j`
- Password: `workshop123`

### 3. Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
```

Now open the `.env` file in any text editor and replace `sk-ant-your-key-here` with your real key:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Where to get a key:**
1. Go to https://console.anthropic.com
2. Sign up (free) or log in
3. Click **Get API Keys** → **Create Key**
4. Copy the key and paste it into `.env`

> The `.env` file stays on your machine only — it is in `.gitignore` and will never be pushed to GitHub.

### 5. Verify everything works

```bash
python check_setup.py
```

You should see:
```
✓ Neo4j connected
✓ Anthropic API reachable
✓ Ready for the workshop!
```

---

## Directory layout

```
knowledge-graph-ai-workshop/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── check_setup.py
├── .env.example
│
├── slides/                   presentation notes for each module
│   ├── 00-welcome.md
│   ├── 01-rag.md
│   ├── 02-knowledge-graphs.md
│   ├── 03-modeling.md
│   ├── 04-querying.md
│   └── 05-llm-integration.md
│
├── exercises/                hands-on coding exercises
│   ├── 01-basics/
│   ├── 02-modeling/
│   ├── 03-querying/
│   └── 04-llm-integration/
│
├── project/                  complete end-to-end demo
│   ├── data/
│   └── src/
│
└── references/               cheat sheets
    ├── cypher-cheatsheet.md
    └── further-reading.md
```
