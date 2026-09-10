# Knowledge Graphs for AI — Workshop Guide

> Follow this file top to bottom during the session.
> Each step has a ✅ checkpoint — don't move on until you see it.

---

## Step 0 — Setup (0:00–0:15)

### 0.1 Start the database

```bash
docker compose up -d
```

Wait 20 seconds, then open **http://localhost:7474** in your browser.
Log in with:
- Username: `neo4j`
- Password: `workshop123`

✅ You should see the Neo4j Browser homepage.

---

### 0.2 Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

✅ You should see packages installing with no errors.

---

### 0.3 Add your API key

```bash
cp .env.example .env
```

Open the `.env` file in your editor and replace `sk-ant-your-key-here` with your real key:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
```

Get a free key at: https://console.anthropic.com → Get API Keys → Create Key

✅ The key is saved in `.env`.

---

### 0.4 Verify everything works

```bash
python check_setup.py
```

✅ You should see:
```
✓ Neo4j connected (localhost:7687)
✓ Anthropic API reachable
✓ You're all set — see you at the workshop!
```

**Common errors:**

| Error | Fix |
|-------|-----|
| `command not found: python` | Use `python3` instead |
| `source: no such file or directory: .venv` | Run `python3 -m venv .venv` first |
| Neo4j not connecting | `docker compose up -d`, wait 20 seconds, retry |
| API key error | Check `.env` — no quotes around the key, no trailing spaces |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |

---

## Step 1 — What is RAG? (0:15–0:45)

### The problem with plain LLMs

Ask ChatGPT something time-sensitive and it might be confidently wrong.
That's not a bug — language models memorise patterns from training data.
They don't look things up.

### What RAG does

**R**etrieval-**A**ugmented **G**eneration — before the LLM answers,
fetch relevant context and include it in the prompt.

```
question → [retrieve relevant chunks] → [question + chunks] → LLM → answer
```

### Where RAG falls short

RAG retrieves *similar text* — it doesn't retrieve *structured relationships*.

> "Which companies make products that compete with the iPhone?"

To answer this from documents you'd need to find every mention of iPhone competitors,
resolve that Samsung Galaxy and Google Pixel are products, and know they are made by
different companies. Vector search can't do that reliably.

### The fix — Knowledge Graphs

Instead of retrieving text chunks, retrieve **graph facts**:

```
question
  → LLM translates question to a graph query
  → Graph database returns exact facts + relationships
  → LLM turns results into a plain English answer
```

This is **GraphRAG** — what we build today.

✅ Concept clear? Move to Step 2.

---

## Step 2 — Knowledge Graphs 101 (0:45–1:15)

### Three building blocks

**Node** — a thing
```
(Apple:Company {name:"Apple", founded:1976})
(iPhone:Product {name:"iPhone", category:"smartphone"})
```

**Relationship** — a directed connection with a type
```
(Apple)-[:MAKES]->(iPhone)
```

**Property** — a key-value on a node or relationship
```
(Apple)-[:MAKES {since:2007}]->(iPhone)
```

### Why graphs beat tables for connected data

In a relational database, finding "what products are made by companies founded by Elon Musk"
needs 3 JOINs and a subquery.

In a graph — follow the arrows:
```
(Elon Musk)-[:FOUNDED]->(Company)-[:MAKES]->(Product)
```

### Our graph today

```
(Person) ──[:FOUNDED]──> (Company) ──[:MAKES]──> (Product)
(Person) ──[:CEO_OF]───> (Company)
(Company)──[:ACQUIRED]─> (Company)
(Product)──[:COMPETES_WITH]──> (Product)
```

Real data:
- Companies: Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla
- People: Steve Jobs, Elon Musk, Sam Altman, Jensen Huang, Mark Zuckerberg
- Products: iPhone, Android, Windows, AWS, ChatGPT, Claude, Gemini, VS Code...

✅ Concept clear? Move to Exercise 1.

---

## Exercise 1 — Your First Graph (1:00–1:15)

### Run the starter file

```bash
python exercises/01-basics/exercise.py
```

✅ You should see:
```
Hello, graph!
Companies created — check http://localhost:7474
Products linked!
```

### See it in the browser

Open http://localhost:7474 and run:

```cypher
MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p
```

✅ You should see a small graph with nodes and arrows.

### Your turn — add a founder

Open `exercises/01-basics/exercise.py` and fill in the TODOs at the bottom:
- Create a `Person` node for `"Steve Jobs"`
- Create a `[:FOUNDED]` relationship: Steve Jobs → Apple
- Verify in the browser:

```cypher
MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c
```

✅ Steve Jobs node appears connected to Apple.

**Stuck?** The solution is in `exercises/01-basics/solution.py`.

---

## ☕ Break (1:15–1:30)

---

## Step 3 — Modeling Real-World Information (1:30–1:40)

### The most important modeling question

> "What questions do I need to answer?"

Model around your queries — not around your data source.

### Do this, not that

| Do | Don't |
|----|-------|
| Use nouns for node labels | Use verbs as labels |
| Use UPPER_SNAKE for relationship types | Use generic `RELATED_TO` |
| Put simple facts as properties | Turn every property into a node |
| Model for traversal | Mirror your source data structure |

### The hard truth about AI-generated graphs

You might think: "I'll just get an AI to build my Knowledge Graph automatically."

Here's the reality: **90–95% of AI-generated tuples are useless** for the specific
questions you actually need to answer. You end up with:
- Duplicates (`Apple Inc.` vs `Apple` vs `apple`)
- Orphan nodes nothing connects to
- 40 relationship types that mean the same thing
- Relationships that are true but answer no useful question

The dataset we're using today is small and intentional — every node is reachable,
every relationship is queryable. That's the result of design, not automation.

> A small, intentional graph beats a large, AI-generated one every time.

✅ Concept clear? Move to Exercise 2.

---

## Exercise 2 — Load the Full Dataset (1:40–2:00)

### Clear previous data

In the Neo4j browser run:
```cypher
MATCH (n) DETACH DELETE n
```

### Seed the full dataset

```bash
python exercises/02-modeling/seed.py
```

✅ You should see:
```
Seeding companies...    ✓ 10 companies
Seeding people...       ✓ 10 people
Seeding products...     ✓ 25 products
Seeding relationships...  ✓ done
Graph is ready! Open http://localhost:7474
```

### Explore in the browser

```cypher
MATCH (n) RETURN n LIMIT 60
```

✅ A rich connected graph fills the screen — companies, people, products, all linked.

---

## Exercise 3 — Querying the Graph (2:00–2:30)

### Run all queries

```bash
python exercises/03-querying/queries.py
```

### Or run them one by one in the Neo4j browser

**Basic lookup:**
```cypher
MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
RETURN p.name, p.category, p.launched
ORDER BY p.launched
```

**Multi-hop — follow the arrows:**
```cypher
MATCH (person:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN c.name AS company, p.name AS product
```

**Competition network:**
```cypher
MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
RETURN c.name AS made_by, comp.name AS product
```

**Ranking:**
```cypher
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COUNT(p) AS num_products
ORDER BY num_products DESC
```

**AI products since 2022:**
```cypher
MATCH (p:Product)
WHERE p.category = "AI" AND p.launched >= 2022
RETURN p.name, p.launched
ORDER BY p.launched
```

✅ All queries return results.

### Your turn — two challenges

**Challenge 1:** Which companies have both a cloud product AND an AI product?

**Challenge 2:** Who is the CEO of a company that was founded by someone else?

**Hints in `exercises/03-querying/README.md` if you get stuck.**

---

## Exercise 4 — Connect the LLM (2:30–3:00)

### Run the Q&A assistant

```bash
python exercises/04-llm-integration/exercise.py
```

### Ask these questions one by one

```
What products does Microsoft make?
Which companies make AI products?
What products compete with ChatGPT?
Which company makes the most products?
What cloud products exist and who makes them?
```

Watch the **Generated Cypher** panel — the LLM is writing the query for you.

✅ You get a plain English answer grounded in graph data — not a guess.

### What just happened

```
Your question
    → LLM call 1: translates to Cypher
    → Neo4j runs the query
    → LLM call 2: turns results into plain English
    → Answer
```

The LLM never makes up facts — it only formats what the graph returns.

---

## Step 4 — End-to-End Project (3:00–3:30)

### Run the complete assistant

```bash
python project/src/assistant.py demo
```

This runs 8 pre-written questions automatically. Watch the full pipeline in action.

### Switch to interactive mode

```bash
python project/src/assistant.py
```

Ask anything:
```
Who founded companies that make AI products?
Which company has the most competition across its products?
What did Elon Musk's companies build?
Which cloud platforms are there and who runs them?
```

✅ You just built a GraphRAG system end to end.

---

## What you built today

| Component | Technology | What it does |
|-----------|-----------|--------------|
| Graph database | Neo4j | Stores entities and relationships |
| Query language | Cypher | Traverses the graph |
| LLM integration | Anthropic Claude | Translates questions → Cypher → answers |
| Data model | Custom designed | 10 companies, 10 people, 25 products |

**What to call this on your resume:**
- GraphRAG system
- Knowledge Graph with Neo4j and Cypher
- Text-to-Cypher LLM pipeline
- Multi-hop reasoning over structured data

---

## What's next

- `references/cypher-cheatsheet.md` — every Cypher pattern on one page
- `references/further-reading.md` — courses, books, production patterns
- Add a second domain to this graph (movies, your company's products, research papers)
- Explore [Neo4j Graph Academy](https://graphacademy.neo4j.com) — free, structured courses
