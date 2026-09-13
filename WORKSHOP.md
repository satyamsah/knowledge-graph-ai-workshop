# Knowledge Graphs for AI
## Workshop Guide — 3.5 hours

> **How to use this file:**
> - `📖 CONCEPT` — read along while the presenter explains
> - `👀 DEMO` — watch the presenter's screen
> - `💻 EXERCISE` — your turn to code
>
> Follow top to bottom. Each section ends with a ✅ checkpoint.
> Don't move on until you hit it.

---

# PART 0 — Setup (0:00–0:15)

---

## 💻 Get everything running

Run these one at a time. Wait for each to finish before the next.

**1. Start the graph database**
```bash
docker compose up -d
```
Wait 20 seconds, then open **http://localhost:7474** in your browser.
Log in with username `neo4j` and password `workshop123`.

✅ You see the Neo4j Browser homepage.

---

**2. Set up Python**
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

✅ Packages install with no errors.

---

**3. Add your Anthropic API key**
```bash
cp .env.example .env
```

Open `.env` in any text editor. Replace `sk-ant-your-key-here` with your real key:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
```

Get a free key at → **https://console.anthropic.com** → Get API Keys → Create Key

✅ Key is saved in `.env`.

---

**4. Verify everything works**
```bash
python check_setup.py
```

✅ You see:
```
✓ Neo4j connected (localhost:7687)
✓ Anthropic API reachable
✓ You're all set — see you at the workshop!
```

**Something broken? Check this table:**

| Error | Fix |
|-------|-----|
| `command not found: python` | Use `python3` instead |
| `source: no such file or directory: .venv` | Run `python3 -m venv .venv` first |
| Neo4j not connecting | `docker compose up -d`, wait 20 sec, retry |
| `Client.__init__() got an unexpected keyword argument 'proxies'` | `pip install --upgrade anthropic httpx` |
| `API key is not scoped to a workspace` | Go to console.anthropic.com → delete key → create a new one |
| API key error | Open `.env` — no quotes around key, no trailing spaces |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

---

# PART 1 — Why We Need This (0:15–0:45)

> **New to RAG?** Read every section below — it builds the context you need before the demo.
> **Already know RAG?** Skim the concept pages and jump straight to the demo. You'll see exactly where graphs fill the gap RAG can't.

---

## 📖 The problem with plain LLMs

Ask ChatGPT: *"What is the last Spider-Man movie?"*

It answers confidently — but its knowledge has a **cutoff date**.
It might be wrong. It can't tell you when it's wrong.

**Why?** The LLM memorised patterns from training data.
It doesn't *look things up* — it *remembers* (imperfectly).

---

## 📖 What is RAG?

**R**etrieval-**A**ugmented **G**eneration

The fix: before the LLM answers, *fetch relevant context* and include it in the prompt.

```
┌─────────────────────────────────────────────────────────────┐
│                        RAG Pipeline                         │
└─────────────────────────────────────────────────────────────┘

  User question: "Which companies make cloud products?"
        │
        ▼
  ┌─────────────────┐
  │  Embed question │  — turn question into a vector
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────────────────┐
  │           Vector Search                 │
  │  Doc 1: "AWS is Amazon's cloud..."  0.91│  ← top match
  │  Doc 2: "Azure is Microsoft's..."   0.88│  ← top match
  │  Doc 3: "Apple makes iPhones..."    0.12│  ← ignored
  └────────┬────────────────────────────────┘
           │  top-k chunks retrieved
           ▼
  ┌─────────────────────────────────────────┐
  │  Augmented Prompt                       │
  │  "Answer using these passages:          │
  │   Passage 1: AWS is Amazon's cloud...   │
  │   Passage 2: Azure is Microsoft's...    │
  │   Question: Which companies make        │
  │   cloud products?"                      │
  └────────┬────────────────────────────────┘
           │
           ▼
  ┌─────────────────┐
  │       LLM       │  — generates answer from passages
  └────────┬────────┘
           │
           ▼
  "Amazon and Microsoft make cloud products."
```

**How retrieval works:**
1. Split documents into chunks, turn each chunk into a vector (embedding)
2. Turn your question into a vector
3. Find the chunks most similar to your question
4. Pass them to the LLM as context

RAG is great for: answering questions about documents, summarising PDFs, "chat with your codebase."

---

## 📖 Where RAG falls short

RAG retrieves *similar text*. It doesn't retrieve *structured relationships*.

> *"Which companies make products that compete with the iPhone?"*

To answer this from documents you'd need to:
- Find every mention of iPhone competitors across thousands of pages
- Figure out that Samsung Galaxy and Google Pixel are products
- Know they are made by different companies

Vector search can't do this reliably. The answer isn't in a paragraph — it's in the **connections** between things.

| Question type | RAG | Knowledge Graph |
|---|---|---|
| "What does this document say about X?" | ✓ | — |
| "Who is related to whom?" | ✗ | ✓ |
| "What are all products made by company X?" | ✗ | ✓ |
| "Find the path between A and B" | ✗ | ✓ |
| "Count or rank things" | ✗ | ✓ |

---

## 📖 The fix — GraphRAG

Instead of retrieving text chunks, retrieve **graph facts**:

```
┌─────────────────────────────────────────────────────────────┐
│                     GraphRAG Pipeline                       │
└─────────────────────────────────────────────────────────────┘

  User question: "Which companies make cloud products?"
        │
        ▼
  ┌─────────────────────────────────────────┐
  │  LLM Call 1 — Text → Cypher            │
  │                                         │
  │  "Translate this question into Cypher   │
  │   using the graph schema below..."      │
  └────────┬────────────────────────────────┘
           │  generates:
           │  MATCH (c:Company)-[:MAKES]->(p:Product)
           │  WHERE p.category = "cloud"
           │  RETURN c.name, p.name
           ▼
  ┌─────────────────────────────────────────┐
  │  Neo4j — Graph Query                    │
  │                                         │
  │  (Amazon) ──[:MAKES]──> (AWS)           │
  │  (Microsoft) ──[:MAKES]──> (Azure)      │
  │  (Google) ──[:MAKES]──> (Google Cloud)  │
  └────────┬────────────────────────────────┘
           │  exact structured results:
           │  [Amazon→AWS, Microsoft→Azure,
           │   Google→Google Cloud]
           ▼
  ┌─────────────────────────────────────────┐
  │  LLM Call 2 — Results → Plain English   │
  │                                         │
  │  "Answer using ONLY this graph data:    │
  │   [Amazon→AWS, Microsoft→Azure...]"     │
  └────────┬────────────────────────────────┘
           │
           ▼
  "Amazon (AWS), Microsoft (Azure), and Google
   (Google Cloud) all make cloud products."
```

This is **GraphRAG** — and it's what we build today.

```
Plain LLM  →  fast but makes things up
    ↓
RAG        →  grounded in documents, but misses relationships
    ↓
GraphRAG   →  grounded in structured facts + relationships  ← we build this
```

---

## 📖 The three approaches — and why we need all three

| Approach | Data source | Handles relationships? | Trustworthy? |
|---|---|---|---|
| Plain LLM | Training memory | ❌ No | ❌ No source |
| RAG | Text chunks | ⚠ Weak | ⚠ Hard to verify |
| GraphRAG | Knowledge graph | ✅ Yes | ✅ Traceable facts |

**Plain LLM** — fast, but answers from memory. Could be wrong, outdated, no source.

**RAG** — retrieves relevant text passages and passes them to the LLM. Better. But text passages can't tell you *which company makes which competing product* — that information is in the *connections*, not the text.

**GraphRAG** — queries structured facts and relationships directly. Precise, explainable, and grounded in data you control.

---

## 👀 DEMO — see all three live

### What is a graph database?

A **graph database** stores data as **nodes** (things) and **relationships** (connections between things) — not tables and rows.

| Relational DB | Graph DB |
|---|---|
| Tables, rows, columns | Nodes, relationships, properties |
| Foreign keys to connect data | Direct pointers — no JOINs needed |
| Good for flat records | Good for connected data |

The key insight: **relationships are first-class citizens**. You don't have to compute them — they are stored directly in the graph.

---

### Why do we use a graph database here?

Questions like *"What did Elon Musk's companies build?"* or *"Which companies make both a cloud AND an AI product?"* require following connections across multiple entities.

- In SQL: you need multiple JOINs across tables
- In a graph: you just **follow the arrows**

Graph databases are purpose-built for traversal — finding paths and patterns through connected data. That makes them a natural fit for Knowledge Graphs.

---

### Why is seed.py important?

`seed.py` is what **puts the knowledge into the Knowledge Graph**. Without it, the graph is empty — and an empty graph gives you nothing.

Think of it as the "import" step:
- It defines the facts (Apple makes iPhone, Elon Musk founded Tesla)
- It creates the nodes and relationships in Neo4j
- It is idempotent — you can run it multiple times safely (MERGE, not CREATE)

In a real production system, seed.py is replaced by a pipeline that pulls data from APIs, databases, or documents. But the pattern is the same: **structured facts go in, graph comes out**.

> Run seed.py once before every demo or exercise — it is the foundation everything else builds on.

---

First load the dataset so the graph has data:

```bash
python exercises/02-modeling/seed.py
```

✅ You see:
```
Seeding companies...    ✓ 10 companies
Seeding people...       ✓ 10 people
Seeding products...     ✓ 25 products
Seeding relationships...  ✓ done
Graph is ready! Open http://localhost:7474
```

Now run the comparison:

```bash
python demos/rag_vs_graph.py
```

### 📂 What is this file?

`demos/rag_vs_graph.py` — a comparison script, not production code. Three answer functions, three questions, side by side.

**Watch for:**
- 👀 **Plain LLM** — confident but no source
- 👀 **RAG chunks** — raw text fragments, cloud and AI facts for the same company are in separate chunks — RAG can't connect them
- 👀 **Generated Cypher** — LLM writing a query in real time from your question
- 👀 **GraphRAG answer** — precise, sourced from the graph

Watch the same question answered three ways. That difference is what we spend today building.

✅ You understand why we need a Knowledge Graph. Move to Part 2.

---

# PART 2 — Knowledge Graphs 101 (0:45–1:00)

---

## 📖 Three building blocks

A Knowledge Graph stores information as **things** and **relationships between things**.

### 1. Node — a thing

```
(Apple:Company  {name:"Apple",  founded:1976, hq:"Cupertino"})
(iPhone:Product {name:"iPhone", category:"smartphone", launched:2007})
(Steve Jobs:Person {name:"Steve Jobs"})
```

- The label (`:Company`, `:Product`) is the *type*
- `{}` contains properties — key-value facts about this thing
- Every node has an internal ID

### 2. Relationship — a connection

```
(Steve Jobs)-[:FOUNDED]->(Apple)
(Apple)-[:MAKES]->(iPhone)
(iPhone)-[:COMPETES_WITH]->(Android)
```

- Always has a **direction** — the arrow matters
- The type is in `[:UPPERCASE_SNAKE]`
- Relationships can also have properties: `[:FOUNDED {year:1976}]`

### 3. Property — a fact

```
(Apple {name:"Apple", founded:1976, hq:"Cupertino"})
```

Simple key-value pairs. Put facts here when you don't need to traverse them.

---

## 📖 Why graphs beat tables for connected data

**In a relational database**, finding "products made by companies founded by Elon Musk" needs:
```sql
SELECT p.name FROM products p
JOIN company_products cp ON p.id = cp.product_id
JOIN companies c ON cp.company_id = c.id
JOIN founders f ON c.id = f.company_id
WHERE f.name = 'Elon Musk'
```

**In a graph** — just follow the arrows:
```
(Elon Musk)-[:FOUNDED]->(Company)-[:MAKES]->(Product)
```

Each arrow you follow is called a **hop**. One hop = one relationship crossed.
SQL needs one JOIN per hop — two hops means two JOINs, four hops means four JOINs, and the query becomes a mess.
In a graph you just keep following arrows — the pattern stays simple no matter how many hops you need.
The deeper the question, the bigger the advantage of a graph.

---

## 📖 Our graph today

```
(Person) ──[:FOUNDED]──────> (Company) ──[:MAKES]──> (Product)
(Person) ──[:CEO_OF]───────> (Company)
(Company)──[:ACQUIRED]─────> (Company)
(Product)──[:COMPETES_WITH]─>(Product)
```

**Real data we'll use:**
- Companies: Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla, SpaceX
- People: Steve Jobs, Steve Wozniak, Bill Gates, Jeff Bezos, Mark Zuckerberg, Elon Musk, Sam Altman, Jensen Huang, Sundar Pichai, Dario Amodei
- Products: iPhone, MacBook, Android, Windows, AWS, Azure, ChatGPT, Claude, Gemini, VS Code, GitHub, and more...

---

## 👀 DEMO — your first Cypher in the browser

Watch the presenter type this in the Neo4j browser at http://localhost:7474:

```cypher
CREATE (apple:Company {name:"Apple"})-[:MAKES]->(iphone:Product {name:"iPhone"})
RETURN apple, iphone
```

Two nodes appear. One arrow. That's a Knowledge Graph.

```cypher
MATCH (apple:Company {name:"Apple"})
CREATE (jobs:Person {name:"Steve Jobs"})-[:FOUNDED]->(apple)
RETURN jobs, apple
```

The graph grows by connection — Apple already existed, we just linked Steve Jobs to it.

> **Try it yourself** — type these two queries in the Neo4j browser right now. Don't copy-paste — type them. The muscle memory of writing `(node)-[:RELATIONSHIP]->(node)` is what makes the next exercise click.

✅ You understand nodes, relationships, and properties. Move to Exercise 1.

---

# PART 3 — Exercise 1: Your First Graph (1:00–1:15)

You just typed Cypher in the browser. Now you'll do the same thing from Python — connecting to Neo4j, creating nodes, and linking them with relationships. Same concepts, different interface.

---

## 💻 Run the starter file

```bash
python exercises/01-basics/exercise.py
```

✅ You see:
```
Hello, graph!
Companies created — check http://localhost:7474
Products linked!
```

---

## 💻 See it in the Neo4j browser

Open **http://localhost:7474** and run:
```cypher
MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p
```

✅ A small graph appears — Apple and Google with their products connected by arrows.
Click on a node to see its properties.

---

## 📖 Cypher syntax you need for the exercise

Before you write anything, here are the five building blocks you will use:

**`MERGE` — create if it doesn't exist, find it if it does**
```cypher
MERGE (c:Company {name: "Apple"})
```
Safe to run multiple times. If Apple already exists, nothing changes. If it doesn't, it gets created.
This is different from `CREATE` which always makes a new node — even duplicates.

**`MATCH` — find something that already exists**
```cypher
MATCH (c:Company {name: "Apple"})
```
Finds the Apple node. If it doesn't exist, the query returns nothing and stops.

**`ON CREATE SET` — set properties only when first created**
```cypher
MERGE (c:Company {name: "Apple"})
ON CREATE SET c.founded = 1976, c.hq = "Cupertino"
```
The `founded` and `hq` properties are only written if Apple was just created. If it already existed, they are left alone.

**`(n:Label {prop: $value})` — node pattern**
```cypher
(:Person {name: $name})
```
`:Person` is the label (the type). `{name: $name}` is a property filter or setter. `$name` is a parameter — the actual value comes from Python.

**`(a)-[:TYPE]->(b)` — relationship pattern**
```cypher
MERGE (p)-[:FOUNDED]->(c)
```
Creates a `FOUNDED` relationship from `p` to `c`. The arrow direction matters — always left to right here.

**Putting it together — what you will write:**
```python
def create_person(tx, name):
    tx.run("MERGE (:Person {name: $name})", name=name)
    #       ↑ Cypher string              ↑ Python value passed as parameter

def link_founder(tx, person, company):
    tx.run("""
        MATCH (p:Person  {name: $person})
        MATCH (c:Company {name: $company})
        MERGE (p)-[:FOUNDED]->(c)
    """, person=person, company=company)
    # MATCH finds existing nodes, MERGE creates the relationship between them
```

---

## 💻 Your turn — add a real founder

We'll add **Linus Torvalds** — the creator of Linux.
This data is NOT in `seed.py` so you're genuinely adding something new.

Open `exercises/01-basics/exercise.py` in your editor and scroll to the bottom — you'll see the TODO section.

You need to write two functions:
1. `create_person(tx, name)` — creates a Person node
2. `link_founder(tx, person, company)` — creates a `[:FOUNDED]` relationship

**The Cypher patterns are in the comments** — read them carefully.

When done, uncomment Step d and re-run:
```bash
python exercises/01-basics/exercise.py
```

Verify in the browser:
```cypher
MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c
```

✅ Linus Torvalds appears connected to Linux Foundation.

**Stuck?** Full solution in `exercises/01-basics/solution.py`

---

# ☕ Break (1:15–1:30)

---

# PART 4 — Modeling Real-World Information (1:30–1:45)

---

## 📖 Modeling is a design skill

There is no single "correct" graph model.
Good modeling asks one question: **what do I need to answer?**

Design around your queries — not around your data source.

**The three questions to ask before you model anything:**
1. What are my entities? → these become **nodes**
2. How are they related? → these become **relationships**
3. What do I need to know about each? → these become **properties**

---

## 📖 Good habits vs. common mistakes

| Do | Don't |
|----|-------|
| Use nouns for node labels | Use verbs as labels |
| Use `UPPER_SNAKE` for relationship types | Use vague `RELATED_TO` for everything |
| Put simple facts as properties on nodes | Turn every property into its own node |
| Model for the queries you need | Mirror your source data structure blindly |

**Mistake 1 — over-normalising:**
```
❌  (iPhone)-[:HAS_ATTRIBUTE]->(Attribute {key:"category", value:"smartphone"})
✓   (iPhone:Product {name:"iPhone", category:"smartphone"})
```

**Mistake 2 — vague relationships:**
```
❌  (Apple)-[:RELATED_TO]->(iPhone)
✓   (Apple)-[:MAKES]->(iPhone)
```

Relationship types are your vocabulary. Rich types = richer queries.

---

## 📖 The hard truth — AI won't build this for you

When people first hear about Knowledge Graphs and LLMs together, the natural reaction is:

> *"LLMs understand language and can extract information from text. So I'll just point an AI agent at my data, it'll pull out all the entities and relationships automatically, and I'll have a Knowledge Graph. How hard can it be?"*

This sounds reasonable. And it kind of works — the AI will generate a graph. The problem is **what it generates**.

The LLM doesn't know what questions you need to answer. So it extracts *everything* it can find. The result looks impressive. Hundreds of nodes, thousands of relationships. But when you start querying it, you discover most of it is noise.

### A concrete example

Say you feed this paragraph to an AI agent:

> *"Apple was founded by Steve Jobs and Steve Wozniak in 1976 in a garage in Los Altos. Jobs was known for his obsession with design. The iPhone, launched in 2007, changed the smartphone industry. Apple's main competitor in smartphones is Samsung, which makes the Galaxy series."*

The AI extracts something like this:

```
(Apple)-[:FOUNDED_BY]->(Steve Jobs)
(Apple)-[:FOUNDED_BY]->(Steve Wozniak)
(Apple)-[:FOUNDED_IN]->(1976)
(Apple)-[:FOUNDED_IN]->(Los Altos)
(Apple)-[:FOUNDED_IN]->(garage)          ← a garage is now a node
(Steve Jobs)-[:KNOWN_FOR]->(design obsession)
(Steve Jobs)-[:OBSESSED_WITH]->(design)  ← duplicate meaning
(iPhone)-[:LAUNCHED_IN]->(2007)
(iPhone)-[:CHANGED]->(smartphone industry)
(Apple)-[:HAS_COMPETITOR]->(Samsung)
(Samsung)-[:MAKES]->(Galaxy series)
(Apple)-[:MAKES]->(iPhone)
(iPhone)-[:COMPETES_WITH]->(Galaxy series)
```

Now ask: *"Which companies make competing products?"*

Only 2 of those 13 relationships actually help answer it:
```
(Apple)-[:MAKES]->(iPhone)
(iPhone)-[:COMPETES_WITH]->(Galaxy series)
```

The other 11 are noise — `FOUNDED_IN garage`, `KNOWN_FOR design obsession`,
`CHANGED smartphone industry` — none of these help you traverse the graph for real questions.

That's 85% noise from a single paragraph. Imagine running this over 10,000 documents.

### What we designed instead

```
(Apple)-[:MAKES]->(iPhone)
(iPhone)-[:COMPETES_WITH]->(Android)
(Steve Jobs)-[:FOUNDED]->(Apple)
```

3 relationships. All queryable. No noise. That's the result of asking:
**"What questions do I need to answer?"** before writing a single line of code.

The dataset we're using today has 10 companies, 10 people, 25 products, and 5 relationship types. Every single node is reachable. Every single relationship answers a real question. Not because we used better AI — because we **designed it**.

> A small, intentional graph beats a large, AI-generated one every time.

The hard work is the design work. And that's the valuable work — because anyone can call an API, but not everyone can look at a domain and know what structure will make it queryable.

---

## 📖 The data model — what's in the graph

Before we explore, open **[DATA_MODEL.md](DATA_MODEL.md)** — it has the full reference:
- All node types and their properties
- All relationship types with examples
- Complete list of every company, person, and product loaded
- Useful exploration queries

**Quick summary:**
```
(Person)  -[:FOUNDED]->       (Company) ──[:MAKES]──> (Product)
(Person)  -[:CEO_OF]->        (Company)
(Company) -[:ACQUIRED]->      (Company)
(Product) -[:COMPETES_WITH]-> (Product)
```

**12 people · 10 companies · 25 products · 5 relationship types**

---

## 💻 Exercise 2 — Explore the full dataset (1:45–2:00)

The graph is already loaded from the demo earlier.
Let's explore it properly now that you understand the model.

Open http://localhost:7474 and run these one at a time:

**See everything:**
```cypher
MATCH (n) RETURN n LIMIT 60
```

**Just the companies and their products:**
```cypher
MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p
```

**Just the people and who they founded:**
```cypher
MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c
```

**Acquisitions:**
```cypher
MATCH (a:Company)-[:ACQUIRED]->(b) RETURN a, b
```

✅ A rich connected graph fills the screen — the entire tech world in a graph.

> **If your graph is empty** (you cleared it in Exercise 1):
> ```bash
> python exercises/02-modeling/seed.py
> ```

---

# PART 5 — Exercise 3: Querying the Graph (2:00–2:30)

You've already written Cypher in Exercise 1 and explored the graph in Exercise 2.
Now let's run more powerful queries and see multi-hop traversal in action.

---

## 💻 Run the query suite

```bash
python exercises/03-querying/queries.py
```

This runs 5 queries, each explained inline. Watch the output — especially Query 2 and Query 3 where we traverse multiple relationships in one go.

✅ All 5 queries return results in your terminal.

---

## 💻 Two challenges — try these in the Neo4j browser

**Challenge 1:** Which companies have both a cloud product AND an AI product?
```cypher
MATCH (c:Company)-[:MAKES]->(cloud:Product {category:"cloud"})
MATCH (c)-[:MAKES]->(ai:Product {category:"AI"})
RETURN c.name, cloud.name AS cloud_product, ai.name AS ai_product
```

**Challenge 2:** Who is CEO of a company that was founded by someone else?
```cypher
MATCH (ceo:Person)-[:CEO_OF]->(c:Company)
WHERE NOT (ceo)-[:FOUNDED]->(c)
RETURN ceo.name AS ceo, c.name AS company
```

✅ Both challenges return results.

---

# ☕ Short Break (2:30–2:40)

Take 10 minutes. The next section connects everything — LLM + graph + natural language. It is the most rewarding part of the day.

---

# PART 6 — Connecting the LLM (2:40–3:10)

---

## 📖 The missing piece

We now have:
- ✓ A Knowledge Graph with real data
- ✓ Cypher queries that answer structured questions

What's missing:
- ✗ A way for anyone to ask questions in plain English

**Solution: let the LLM translate natural language → Cypher → answer**

---

## 📖 The GraphRAG pipeline

```
Your question: "Which companies make AI products?"
          ↓
LLM Call 1 — translate to Cypher:
  "MATCH (c:Company)-[:MAKES]->(p:Product)
   WHERE p.category = 'AI'
   RETURN c.name, p.name"
          ↓
Neo4j runs the query:
  [{company:"OpenAI", product:"ChatGPT"},
   {company:"Google", product:"Gemini"}, ...]
          ↓
LLM Call 2 — synthesise answer:
  "Companies making AI products include OpenAI (ChatGPT),
   Google (Gemini), Microsoft (Copilot), and Anthropic (Claude)."
```

Two LLM calls:
- **Call 1** is a translator — question → Cypher
- **Call 2** is a writer — raw results → plain English

The graph does the heavy lifting in the middle.
**The LLM never makes up facts — it only formats what the graph returns.**

---

## 📖 Why this works — the schema prompt

The LLM knows how to write Cypher because we tell it the graph's structure:

```python
SCHEMA = """
Nodes: Company {name, founded, hq}
       Product {name, category, launched}
       Person  {name}

Relationships:
  (Person)-[:FOUNDED]->(Company)
  (Person)-[:CEO_OF]->(Company)
  (Company)-[:MAKES]->(Product)
  (Product)-[:COMPETES_WITH]->(Product)
"""
```

Better schema prompt = better Cypher = better answers.

---

## 💻 Exercise 4 — Run the Q&A assistant (2:50–3:10)

### 📂 What is this file and what does it do?

`exercises/04-llm-integration/exercise.py` is the **learning version of GraphRAG**. Everything is deliberately exposed so you can see inside the pipeline. This is not a black box — it is a teaching tool.

Inside the file there are four things:
1. **`GRAPH_SCHEMA`** — a plain text description of your graph that gets passed to the LLM. This is what tells the LLM what nodes, relationships, and properties exist. Without this, the LLM would have to guess.
2. **`question_to_cypher()`** — LLM Call 1. Takes your question, sends it to Claude with the schema, returns raw Cypher.
3. **`run_cypher()`** — executes the Cypher against Neo4j and returns structured results.
4. **`results_to_answer()`** — LLM Call 2. Takes the question + graph results, returns a plain English answer.

**What to eyeball when it runs:**

- 👀 **Generated Cypher (LLM Call 1) panel** — this is the most important thing to watch. Read every query. Ask yourself: does it match the question? Is the direction of the arrows correct? Does it use MATCH or WHERE correctly? The LLM is writing this from scratch based only on the schema hint you gave it.
- 👀 **The results table** — raw data straight from Neo4j. Before the answer appears, look at this. Is the data correct? If the answer is wrong, the problem is almost always here — either bad Cypher or missing data.
- 👀 **Answer (LLM Call 2) panel** — the LLM is only allowed to use the data in the results. It cannot add facts from its training. If it says "I don't have that information" — the graph result was empty, not the LLM failing.

**What to say to the audience:**

> *"In production, you would hide the Cypher panel — users don't need to see it. But as a developer, this is exactly what you would monitor. If something goes wrong, the Cypher panel tells you whether the problem is in the LLM prompt, the graph schema, or the data. That's your debugging window."*

**The key difference from production:**
- No API layer — you are calling it directly from the terminal
- No auth, no logging, no error recovery
- The schema hint is hardcoded — in production it would be generated dynamically from the live graph schema

```bash
python exercises/04-llm-integration/exercise.py
```

Ask these questions one at a time and watch the **Generated Cypher** panel:

```
What products does Microsoft make?
Which companies make AI products?
What products compete with ChatGPT?
Which company makes the most products?
What cloud products exist and who makes them?
```

✅ You get plain English answers grounded in graph data — not guesses.

**Now ask your own question.** What do you want to know about the tech world?

---

# PART 7 — End-to-End Project (3:10–3:30)

---

## 💻 Run the complete assistant

```bash
python project/src/assistant.py demo
```

This runs 8 pre-written questions end to end. Watch the full pipeline:
question → Cypher → graph results → answer.

Then switch to interactive mode:
```bash
python project/src/assistant.py
```

Try these:
```
Who founded companies that make AI products?
Which company has the most competition across its products?
What did Elon Musk's companies build?
Which cloud platforms exist and who runs them?
```

Now try this one:
```
Which products compete with AWS?
```

---

## ⚠️ When it fails — relationship direction matters

> **Presenter note:** The question above will return an empty answer. This is intentional — do not fix the code in advance. Let it fail, diagnose it together, fix it live.

The assistant returns:
> *"I cannot answer this question because there is no data available in the knowledge graph about companies that compete with AWS."*

Say: *"We know Azure and Google Cloud compete with AWS. The data is in the graph. Why did the assistant return nothing?"*

---

**Step 1 — look at the Cypher the LLM generated**

The terminal already printed it. It looks like:
```cypher
MATCH (p:Product)-[:COMPETES_WITH]->(aws:Product {name:"AWS"})
RETURN p.name
```

Open http://localhost:7474, paste this query, run it. 0 results.

---

**Step 2 — show what is actually stored**

In the browser, run:
```cypher
MATCH (a)-[:COMPETES_WITH]->(b) RETURN a.name, b.name
```

Point out: every arrow points **away from** AWS:
```
AWS ──[:COMPETES_WITH]──> Azure
AWS ──[:COMPETES_WITH]──> Google Cloud
```

Say: *"The LLM query asked for arrows pointing AT AWS. The graph only has arrows pointing AWAY. One character difference — zero results."*

---

**Step 3 — fix it live in the browser**

Remove the `>` to match in either direction:
```cypher
MATCH (p:Product)-[:COMPETES_WITH]-(aws:Product {name:"AWS"})
RETURN p.name
```

Run it. Azure and Google Cloud appear.

Say: *"That's it. One character — the `>`. The difference between an answer and silence."*

---

**Step 4 — fix the schema hint in the code**

Open `project/src/assistant.py`. In the `GRAPH_SCHEMA` block, change:
```
(Product) -[:COMPETES_WITH]-> (Product)   ← intentionally directional; fixed live during demo
```
to:
```
(Product) -[:COMPETES_WITH]- (Product)   ← no arrow; competition is symmetric, always match undirected
```

Save. Ask the same question again. It now returns the correct answer.

---

**The lesson:**

> *"The graph had the right data. The LLM is capable. But the schema hint told the LLM the relationship has a direction — so it generated a directional query and got nothing.*
>
> *This is why data modeling matters. The direction of a relationship, whether it is symmetric — these decisions directly affect what questions your system can answer. A well-modeled small graph beats a poorly-modeled large one every time."*

✅ You just built a GraphRAG system — end to end. And you fixed a real bug in it.

---

## 📖 What you built today

| Component | Technology | What it does |
|-----------|-----------|--------------|
| Graph database | Neo4j | Stores entities and relationships |
| Query language | Cypher | Traverses the graph with pattern matching |
| LLM — Call 1 | Claude Haiku | Translates natural language → Cypher |
| LLM — Call 2 | Claude Haiku | Synthesises graph results → plain English |
| Data model | Custom designed | 10 companies, 10 people, 25 products, 5 relationship types |

---

## 📖 What to call this on your resume

- **GraphRAG system** — LLM-powered Q&A over a property graph
- **Knowledge Graph with Neo4j and Cypher** — graph database modeling and querying
- **Text-to-Cypher pipeline** — natural language to structured graph queries via LLM
- **Multi-hop reasoning** — answering questions that require traversing chains of relationships

---

## 📖 The skill that matters

Anyone can `pip install neo4j` and call an LLM API.

The skill — the thing worth putting on your resume — is:
- Knowing *what* to model and *why*
- Understanding *when* a graph beats vector search
- Recognising when a relationship adds value vs. noise
- Designing a graph that answers tomorrow's questions, not just today's

That judgment only comes from doing the work. You did it today.

---

## 📖 Real-world use case

Everything you built today is directly applicable in a real enterprise context.

Here is one example: **consultants spend the first days of every engagement just figuring out what environment they're working in** — which products are installed, which versions, which services are running, what depends on what. This is currently done manually by reading documentation, running CLI commands, and asking around.

**What a Knowledge Graph changes:**

Instead of manual discovery, an agent runs at the start of the engagement:

```
consultant runs: python inspect_env.py --target dev-subaccount

Agent automatically:
  → connects to cloud APIs and the target environment
  → discovers installed services, versions, dependencies
  → builds a Knowledge Graph on the fly:
      (ERP 2023)-[:REQUIRES]->(Database Cloud)
      (Database Cloud)-[:VERSION]->(2.0 SP07)
      (Cloud Subaccount)-[:CONTAINS]->(AI Service)
      (AI Service)-[:DEPENDS_ON]->(Object Store)
  → consultant asks in plain English:
      "Is anything approaching end of maintenance?"
      "What services does the AI Service depend on?"
      "Which products are not yet configured?"
  → GraphRAG answers from the graph — not from memory
```

---

### How the graph gets built — API response → graph mapping

This is where the real engineering work lives. **Someone has to define the mapping once.** It does not happen automatically or magically.

A developer looks at what the API returns and decides how it becomes graph data:

```
API response (JSON)                    Graph mapping (written by developer once)
──────────────────────────────────────────────────────────────────────────────
{                                      session.run("""
  "service": "AI Service",               MERGE (s:Service {name: $name})
  "depends_on": ["Object Store"],        MERGE (d:Service {name: $dep})
  "version": "2.1"                       ON CREATE SET s.version = $version
}                                        MERGE (s)-[:DEPENDS_ON]->(d)
                                       """,
                                         name="AI Service",
                                         dep="Object Store",
                                         version="2.1")
```

The developer is answering: *"What questions do I want to ask later?"*
That answer shapes how the graph is modeled — which fields become nodes, which become properties, which become relationships.

**Who does what:**

| Step | Who | How often |
|---|---|---|
| Define the graph model | Developer (human) | Once, upfront |
| Write the API → MERGE mapping | Developer (human) | Once per data source |
| Call the API and run the MERGEs | Agent / script | Automatically, on demand |
| Q&A on the graph | LLM | Every question |

**The analogy to today:**
- `seed.py` = you wrote the mapping by hand (Apple → iPhone, Elon Musk → Tesla)
- In production = a script calls the API and does the same MERGE statements automatically
- The mapping logic was still written by a human developer first

> **The graph does not design itself.** Human judgment defines the model. Automation fills it with data. LLM queries it.

---

**Why this matters:**
- Discovery that takes 2 days takes 2 minutes
- The graph persists — the next person inherits the knowledge
- Questions that require connecting multiple facts (versions + dependencies + status) are answered instantly
- Works across any cloud environment or API

**The pattern is identical to what you built today:**
- Data model → nodes for Service, Version, Dependency, Environment
- Seed script → replaced by an agent that calls cloud APIs
- GraphRAG pipeline → same two-LLM-call pattern
- Natural language Q&A → same `exercise.py` pattern

The only difference is the domain. The architecture is what you built.

> This is why understanding the fundamentals matters — the same pattern applies everywhere.

---

## What's next

| Resource | What's in it |
|----------|-------------|
| `references/cypher-cheatsheet.md` | Every Cypher pattern on one page |
| `references/further-reading.md` | Courses, books, production patterns, resume keywords |
| Neo4j Graph Academy | Free structured courses — graphacademy.neo4j.com |
| Microsoft GraphRAG | Production open-source GraphRAG — github.com/microsoft/graphrag |

**Best next step:** Add a second domain to this graph.
Pick anything — movies, your company's products, a research paper corpus.
The pattern is the same: entities → relationships → questions.
Once you've done it twice it becomes instinct.
