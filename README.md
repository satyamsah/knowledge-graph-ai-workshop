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
| Docker Desktop | See install steps below — must be running before the session |
| Anthropic API key | [console.anthropic.com](https://console.anthropic.com) — free tier works |
| A terminal | Terminal on Mac, PowerShell or Command Prompt on Windows |

No prior database or graph experience needed.

---

## Install Docker Desktop (do this first)

Docker runs the Neo4j graph database locally. You need it before anything else.

**Mac:**
1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Click **Download for Mac** — choose Apple Silicon if you have an M1/M2/M3 chip, Intel if older
3. Open the downloaded `.dmg` file and drag Docker to Applications
4. Open Docker from Applications — wait for the whale icon to appear in your menu bar
5. Verify: open Terminal and run `docker --version` — you should see a version number

**Windows:**
1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Click **Download for Windows**
3. Run the installer — leave all defaults, it will ask to enable WSL 2 (say yes)
4. Restart your computer when prompted
5. Open Docker Desktop from the Start menu — wait for it to say "Docker Desktop is running"
6. Verify: open PowerShell and run `docker --version` — you should see a version number

> **Important:** Docker Desktop must be open and running before you run `docker compose up -d`. If Docker is not running, the command will fail.

---

## Setup (do this before the session)

### 1. Get the code

```bash
git clone https://github.com/satyamsah/knowledge-graph-ai-workshop
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
├── WORKSHOP.md               ← follow this during the session
├── DATA_MODEL.md             ← full graph schema reference
├── README.md                 ← you are here
├── docker-compose.yml
├── requirements.txt
├── check_setup.py
├── .env.example
│
├── exercises/                hands-on coding exercises
│   ├── 01-basics/            Exercise 1 — your first graph
│   ├── 02-modeling/          Exercise 2 — seed the full dataset
│   ├── 03-querying/          Exercise 3 — Cypher queries
│   └── 04-llm-integration/   Exercise 4 — LLM Q&A pipeline
│
├── demos/
│   └── rag_vs_graph.py       Plain LLM vs RAG vs GraphRAG comparison
│
└── project/
    └── src/
        └── assistant.py      Complete end-to-end GraphRAG assistant
```
