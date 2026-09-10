# Demo Script — Knowledge Graphs for AI
### Facilitator guide: exact commands, expected outputs, talking points

---

## Before the session (T-30 min)
### 🔒 FACILITATOR ONLY — do this alone before anyone arrives

Do this yourself before anyone arrives.

```bash
# Start Neo4j
docker compose up -d

# Wait 20 seconds, then activate your environment and verify
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python check_setup.py
```

Expected:
```
✓ Neo4j connected (localhost:7687)
✓ Anthropic API reachable
✓ You're all set — see you at the workshop!
```

Open two terminal windows and keep them ready:
- **Terminal A** — you'll run Python scripts here
- **Terminal B** — spare, in case someone needs help

Open two browser tabs:
- **Tab 1** — `http://localhost:7474` (Neo4j browser, logged in)
- **Tab 2** — your slides (the markdown files, or a rendered version)

---

## Block 0 — Setup & Welcome (0:00–0:15)
### 👥 EVERYONE — session starts here

### Everyone runs the setup check

Say:
> "First thing — let's get everyone's environment running. Follow along with me one command at a time."

```bash
# 1. Start the database
docker compose up -d

# 2. Create Python environment (Mac/Linux)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the env file and add your API key
cp .env.example .env
# open .env and paste your ANTHROPIC_API_KEY

# 5. Verify
python check_setup.py
```

**If someone sees `command not found: python`:**
> "On Mac use `python3` not `python` for the venv step — that's normal."

**If someone sees `source: no such file or directory: .venv/bin/activate`:**
> "You need to create the venv first — run `python3 -m venv .venv` then try again."

**If someone gets a Neo4j error:**
```bash
docker compose up -d
# wait 20 seconds
python check_setup.py
```

**If someone gets an API error:**
> "Open your `.env` file — it's in the project folder — and paste your Anthropic API key where it says `sk-ant-your-key-here`."

**If Docker isn't installed:**
> "Go to https://www.docker.com/get-started, install Docker Desktop, then run `docker compose up -d`. Takes about 3 minutes."

Wait until at least 80% of the room is green before moving on. The rest will catch up.

### Talking point — what we're building

Open `slides/00-welcome.md`, show slide 2 (the Q&A example output).

Say:
> "By the end of today, you'll have built this. You type a question in plain English.
> The system figures out how to query a graph database, gets back structured facts,
> and gives you a grounded answer. Not a guess — actual data you put in yourself.
> Let's understand how we get there."

---

## Block 1 — RAG, the Big Picture (0:15–0:45)

Open `slides/01-rag.md`.

### Slide 1 — The problem with plain LLMs

Say:
> "Ask ChatGPT something time-sensitive and it might be confidently wrong.
> That's not a bug — it's how language models work. They memorise patterns.
> They don't look things up."

### Slide 2–3 — What RAG is

Say:
> "RAG fixes this by adding a retrieval step. Before the LLM answers,
> you fetch relevant documents and include them in the prompt.
> Now the LLM is reasoning over your data, not its memory."

Draw this on screen or whiteboard:
```
question → [retrieve chunks] → [question + chunks] → LLM → answer
```

### Slide 5–6 — Where RAG struggles

Say:
> "RAG is great for document questions. But what about relationship questions?
> 'Which companies make products that compete with the iPhone?'
> That answer isn't in a paragraph — it's in the *connections* between things."

Pause here. Ask the room:
> "Can anyone think of a question where the answer depends on how things are *related*
> rather than what's *written* about them?"

Take 2–3 answers. This is the mental hook.

### Live demo — the difference (most important moment in this block)

Run in **Terminal A**:

```bash
python exercises/04-llm-integration/exercise.py
```

Ask (before the graph is seeded — it will return empty/generic):
```
Ask the graph > Which Google products compete with Microsoft products?
```

Show the output. Then say:
> "Right now this is answering from an empty graph — we haven't loaded our data yet.
> By the end of the session, this will return precise, structured answers.
> Let's build the foundation."

`Ctrl+C` to exit.

---

## Block 2 — Knowledge Graphs 101 (0:45–1:15)

Open `slides/02-knowledge-graphs.md`.

### Slide 1–3 — Nodes, relationships, properties

Draw this live in the Neo4j browser (go to Tab 1, use the query editor):

```cypher
CREATE (apple:Company {name:"Apple"})-[:MAKES]->(iphone:Product {name:"iPhone"})
RETURN apple, iphone
```

Click run. A tiny graph with two nodes and one relationship appears.

Say:
> "That's it. That's a knowledge graph. Two things and the relationship between them.
> Everything we build today is just more of this — more nodes, more relationships,
> richer properties."

Add one more:
```cypher
MATCH (apple:Company {name:"Apple"})
CREATE (jobs:Person {name:"Steve Jobs"})-[:FOUNDED]->(apple)
RETURN jobs, apple
```

Say:
> "Notice we're not duplicating Apple — we're *matching* the existing node and
> attaching the new relationship to it. The graph grows by connection, not by copying."

### Slide 6–7 — Our graph today

Show the schema diagram from slide 7. Say:
> "This is what we're going to build. Real companies, real products, real people.
> Let's start building it right now."

Wipe the test data:
```cypher
MATCH (n) DETACH DELETE n
```

---

## Exercise 1 — Your First Graph (1:00–1:15)

Say:
> "Open `exercises/01-basics/exercise.py`. We're going to work through it step by step.
> Don't run the whole file yet — follow along."

Walk through each step live on screen. Run after Step 2:
```bash
python exercises/01-basics/exercise.py
```

Switch to the Neo4j browser and run:
```cypher
MATCH (n) RETURN n
```

**This is "wow" moment #1.** Two nodes appear. Say:
> "You just wrote data to a graph database from Python. Refresh the query and watch
> the graph grow as more people run their code."

Give 5 minutes for Step 4 (the TODO — create Steve Jobs and link him to Apple).

If anyone finishes early, bonus challenge:
```
Add Tim Cook as CEO_OF Apple — what relationship type would you use?
```

---

## ☕ Break (1:15–1:30)

Say:
> "Take 15 minutes. When you come back we're going to load 50+ nodes at once
> and start asking interesting questions."

---

## Block 3 — Modeling & Loading Data (1:30–2:00)

Open `slides/03-modeling.md`. Keep it fast — 10 minutes max.

### Key point to land

Say:
> "The most important modeling decision is: what questions do you need to answer?
> Model around your queries. If you never need to traverse it, don't make it a node."

Show slide 4 (Do / Don't table). One sentence per row is enough.

### Seed the full dataset

Say:
> "Let's load the real data now. One command."

```bash
python exercises/02-modeling/seed.py
```

Expected output:
```
Seeding companies...    ✓ 10 companies
Seeding people...       ✓ 10 people
Seeding products...     ✓ 25 products
Seeding relationships...  ✓ done
Graph is ready! Open http://localhost:7474
```

Switch to the Neo4j browser. Run:
```cypher
MATCH (n) RETURN n LIMIT 60
```

**This is "wow" moment #2.** A rich connected graph fills the screen. Say:
> "This is the tech world as a graph. Every node is a thing,
> every arrow is a relationship. Now let's query it."

### Reality check — open slides/06-reality-check.md (10 min)

This is the most important non-technical moment of the session. Don't skip it.

Say:
> "Before we start querying — I want to be honest with you about something.
> This data looks clean because it was designed carefully. I decided what to
> include and what to leave out. Let me tell you what happens when you skip that step."

Walk through the key slides:

**Slide 2 — the hype vs. reality**
> "Nine months ago I got sucked into the idea that AI agents could build a
> Knowledge Graph for me automatically. After all, LLMs understand semantics,
> GraphRAG rolls off the tongue... how hard could it be?
> The answer: 90 to 95% of what the AI generates is useless for the specific
> questions you actually need to answer."

**Slide 3 — why AI-generated graphs are noisy**
> "The LLM will extract every relationship it can find. That sounds good.
> But you end up with Apple Inc., Apple, and apple all as separate nodes.
> Orphan nodes nothing connects to. Five different ways to say the same relationship.
> It looks like a graph. It doesn't behave like one."

**Slide 4 — Occam's Razor**
> "Our graph today: 10 companies, 10 people, 25 products, 5 relationship types.
> Every single node is reachable. Every relationship is queryable.
> A naive AI-generated version of this same domain might have 500 nodes,
> 40 relationship types, and answer your questions worse."

**Slide 6 — the data modeling analogy**
> "This is exactly like data modeling. Cheap tooling makes it easy to create
> a new schema per query — you get dashboard-driven development, a mess that
> can't grow. The same trap exists here. Building a KG is easy.
> Building a simple, intentional KG that evolves cleanly — that takes work."

**Slide 7 — close strong**
> "The hard work is the valuable work. Anyone can call an LLM API.
> The skill — the thing worth putting on your CV — is knowing what to model
> and why. That judgment only comes from doing the work."

Pause. Let it land. Then:
> "OK — now that you know what good design looks like, let's write some queries
> and see why it matters."

---

## Block 4 — Querying the Graph (2:00–2:30)

Open `slides/04-querying.md`. Run each query live in the Neo4j browser as you explain it.

### Query 1 — Basic (slide 2)
```cypher
MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
RETURN p.name, p.category, p.launched
ORDER BY p.launched
```

Say:
> "Read it like English: find a Company named Apple that MAKES a Product, return the product."

### Query 2 — Multi-hop (slide 4) — the key moment in this block
```cypher
MATCH (person:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN c.name AS company, p.name AS product
```

Pause. Say:
> "This is two hops. Person → Company → Product. In SQL this would be two JOINs
> and a subquery. Here it's one line. This is what graphs are for."

### Query 3 — Competition network
```cypher
MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
RETURN c.name AS made_by, comp.name AS competing_product
```

Say:
> "We just traversed in two directions — forward to the competitor,
> then backwards to find who makes it. Graph queries read the *shape* of the data."

### Hand off to exercise
Say:
> "Open `exercises/03-querying/queries.py` and run it. Then try the two TODO queries
> at the bottom on your own."

```bash
python exercises/03-querying/queries.py
```

Give 10 minutes. Walk around and help with the TODOs.

**Answers for the TODOs (have these ready):**

Companies with both cloud AND AI products:
```cypher
MATCH (c:Company)-[:MAKES]->(cloud:Product {category:"cloud"})
MATCH (c)-[:MAKES]->(ai:Product {category:"AI"})
RETURN c.name, cloud.name AS cloud_product, ai.name AS ai_product
```

CEO of a company where someone else is founder:
```cypher
MATCH (ceo:Person)-[:CEO_OF]->(c:Company)<-[:FOUNDED]-(founder:Person)
WHERE ceo <> founder
RETURN ceo.name AS ceo, c.name AS company, founder.name AS founder
```

---

## Block 5 — Connecting the LLM (2:30–3:00)

Open `slides/05-llm-integration.md`. 10 minutes slides, then straight into exercise.

### Key diagram (slide 2) — draw or narrate slowly
```
question
  → LLM call 1: question → Cypher query
  → Neo4j runs the Cypher
  → LLM call 2: results → natural language answer
```

Say:
> "Two LLM calls. First one is a translator. Second one is a writer.
> The graph does the heavy lifting in the middle — the LLM never makes up facts,
> it only formats what the graph returns."

### Run the exercise

```bash
python exercises/04-llm-integration/exercise.py
```

Type these questions live — pause after each to show the generated Cypher:

```
Ask the graph > What products does Microsoft make?
```

Show the Cypher panel. Say:
> "The LLM wrote this Cypher query. We didn't. That's the translation step."

```
Ask the graph > Which companies make AI products?
Ask the graph > What products compete with ChatGPT?
```

Ask someone from the audience:
> "What would you ask this graph?"

Take their question and type it live. This is always a crowd pleaser.

---

## Block 6 — End-to-End Project (3:00–3:30)

Say:
> "Everything we've built — the data model, the seed script, the query layer,
> the LLM integration — is assembled in one file: `project/src/assistant.py`.
> This is the thing you put on your resume."

Run demo mode:
```bash
python project/src/assistant.py demo
```

It will run through 8 pre-written questions automatically. Let it play out.

**This is "wow" moment #3.**

After the demo, switch to interactive mode:
```bash
python project/src/assistant.py
```

Ask the room for questions. Write down what people suggest, type each one live.

Good questions to seed the room with if it goes quiet:
```
Who founded companies that make AI products?
Which company has the most competition across its products?
What did Elon Musk's companies build?
Which cloud platforms are there and who runs them?
```

---

## Closing (3:25–3:30)

Open `references/further-reading.md`. Show the "For your resume" section.

Say:
> "You built a GraphRAG system today. End to end — data model, graph database,
> Cypher queries, LLM integration. That's a real project with real tech that
> companies are using in production right now."
>
> "The keywords to use: GraphRAG, Knowledge Graph, Neo4j, Text-to-Cypher,
> multi-hop reasoning. These are searchable, recognisable, and genuinely what you did."
>
> "The best next step: add a second domain to this graph. Movies, your company's
> product catalogue, anything. The pattern is the same — entities, relationships,
> questions. Once you've done it twice it becomes instinct."

---

## Troubleshooting quick reference

| Symptom | Fix |
|---------|-----|
| Neo4j not connecting | `docker compose up -d`, wait 20s, retry |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| LLM generates bad Cypher | Rephrase the question; show the Cypher panel and explain why |
| Empty results | The data might not be seeded — run `python exercises/02-modeling/seed.py` |
| Neo4j browser blank | Hard refresh (`Cmd+Shift+R`), check Docker is still running |
| API key error | Check `.env` has no quotes around the key, no trailing spaces |

---

## Timing safety valves

Running ahead? Add these:
- Let people add their own nodes/companies in Exercise 1
- Do the bonus TODO queries in Exercise 3 together
- Ask the room to design a graph for a different domain (Netflix, Spotify, LinkedIn)

Running behind? Cut these:
- Slide 3 from `03-modeling.md` (over-normalizing example) — skip it
- Aggregation query in Exercise 3 — just show it, don't wait for everyone to run it
- `assistant.py` demo mode — go straight to interactive and ask 3 questions instead of 8
