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

---

## 📖 The problem with plain LLMs

Ask ChatGPT: *"What is the latest iPhone model?"*

It answers confidently — but its knowledge has a **cutoff date**.
It might be wrong. It can't tell you when it's wrong.

**Why?** The LLM memorised patterns from training data.
It doesn't *look things up* — it *remembers* (imperfectly).

---

## 📖 What is RAG?

**R**etrieval-**A**ugmented **G**eneration

The fix: before the LLM answers, *fetch relevant context* and include it in the prompt.

```
Your question
     ↓
[Retrieval step] — find relevant documents / chunks
     ↓
Augmented prompt = question + retrieved context
     ↓
LLM generates answer grounded in that context
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
Your question
     ↓
LLM translates question → structured graph query
     ↓
Graph database returns exact facts + relationships
     ↓
LLM turns results into a plain English answer
```

This is **GraphRAG** — and it's what we build today.

The journey:
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

Watch the same question answered three ways.
Pay attention to the RAG chunks — notice they are text fragments that don't give you structured company → product relationships.
Then watch GraphRAG return an exact structured answer.

That difference is what we spend today building.

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

The more hops, the bigger the gap. Graphs are built for this.

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

✅ You understand nodes, relationships, and properties. Move to Exercise 1.

---

# PART 3 — Exercise 1: Your First Graph (1:00–1:15)

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

## 💻 Your turn — add Steve Jobs

Open `exercises/01-basics/exercise.py` in your editor.
Scroll to the bottom — you'll see the TODO section.

You need to:
1. Write a `create_person(tx, name)` function that creates a `Person` node
2. Write a `link_founder(tx, person_name, company_name)` function that creates a `[:FOUNDED]` relationship
3. Call both to link `"Steve Jobs"` → `"Apple"`

**Hint — the pattern looks like this:**
```python
def create_person(tx, name):
    tx.run("MERGE (:Person {name: $name})", name=name)

def link_founder(tx, person_name, company_name):
    tx.run(
        "MATCH (p:Person {name:$person_name}), (c:Company {name:$company_name}) "
        "MERGE (p)-[:FOUNDED]->(c)",
        person_name=person_name, company_name=company_name,
    )
```

When done, re-run the file:
```bash
python exercises/01-basics/exercise.py
```

Verify in the browser:
```cypher
MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c
```

✅ Steve Jobs appears connected to Apple.

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

You might think: *"I'll just get an AI to generate my Knowledge Graph automatically."*

Here's the reality: **90–95% of AI-generated tuples are useless** for the specific questions you actually need to answer.

The LLM will give you:
- Duplicates (`Apple Inc.` vs `Apple` vs `apple` — three separate nodes)
- Orphan nodes nothing connects to
- 40 relationship types that mean the same thing
- Relationships that are technically true but answer no useful question

All of it *looks* like a graph. None of it *behaves* like one.

The dataset we're using today is intentionally small — 10 companies, 10 people, 25 products, 5 relationship types. Every node is reachable. Every relationship is queryable. That's the result of **design**, not automation.

> A small, intentional graph beats a large, AI-generated one every time.
> — Occam's Razor applied to Knowledge Graphs

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

# PART 5 — Querying with Cypher (2:00–2:30)

---

## 📖 Meet Cypher

Neo4j's query language. Designed to look like the graph itself — you can almost read it as a sentence.

```cypher
MATCH (c:Company)-[:MAKES]->(p:Product)
WHERE c.name = "Apple"
RETURN p.name
```

*"Find a Company that MAKES a Product, where the company is Apple — return the product name."*

**The core structure:**
```cypher
MATCH  (pattern)        -- what shape to find in the graph
WHERE  condition        -- optional filter
RETURN what you want    -- what to output
```

---

## 👀 DEMO — watch these queries run live

Follow along in your own Neo4j browser at http://localhost:7474.

**Query 1 — basic lookup:**
```cypher
MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
RETURN p.name, p.category, p.launched
ORDER BY p.launched
```

**Query 2 — multi-hop (this is where graphs shine):**
```cypher
MATCH (person:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN c.name AS company, p.name AS product
```
Two hops. In SQL this would be two JOINs. Here it's one line.

**Query 3 — competition network:**
```cypher
MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
RETURN c.name AS made_by, comp.name AS product
```
Forward to the competitor, then backwards to find who makes it.

**Query 4 — ranking:**
```cypher
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COUNT(p) AS num_products
ORDER BY num_products DESC
```

---

## 💻 Exercise 3 — Run the queries yourself (2:10–2:30)

```bash
python exercises/03-querying/queries.py
```

✅ All 5 queries return results in your terminal.

**Now try these two challenges on your own in the Neo4j browser:**

**Challenge 1:** Which companies have both a cloud product AND an AI product?
```cypher
-- Hint: use two MATCH patterns on the same company node
MATCH (c:Company)-[:MAKES]->(cloud:Product {category:"cloud"})
MATCH (c)-[:MAKES]->(ai:Product {category:"AI"})
RETURN c.name, cloud.name AS cloud_product, ai.name AS ai_product
```

**Challenge 2:** Who is CEO of a company that was founded by someone else?
```cypher
-- Hint: match both relationships on the same company, check they're different people
MATCH (ceo:Person)-[:CEO_OF]->(c:Company)<-[:FOUNDED]-(founder:Person)
WHERE ceo <> founder
RETURN ceo.name AS ceo, c.name AS company, founder.name AS founder
```

✅ Both challenges return results.

---

# PART 6 — Connecting the LLM (2:30–3:00)

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

## 💻 Exercise 4 — Run the Q&A assistant (2:40–3:00)

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

# PART 7 — End-to-End Project (3:00–3:30)

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

✅ You just built a GraphRAG system — end to end.

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
