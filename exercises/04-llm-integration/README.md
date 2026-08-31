# Exercise 4 — Connect the LLM
### Module: LLM Integration (2:30–3:00)

**Goal:** Ask questions in plain English and get answers from the graph.
**Time:** ~25 minutes
**You'll see:** Natural language → Cypher → answer, live in your terminal.

---

## Step 1 — Run the starter

```bash
python exercises/04-llm-integration/exercise.py
```

It will prompt you:
```
Ask the graph > 
```

Type any question about the tech world. Start with something simple:
```
Ask the graph > What products does Microsoft make?
```

---

## Step 2 — Understand what's happening

Open `exercise.py` and read through it. The flow is:

```
1. Your question
      ↓
2. LLM call #1 — translates your question into a Cypher query
      ↓
3. Neo4j runs the Cypher query
      ↓
4. LLM call #2 — turns the raw results into a plain English answer
      ↓
5. Answer printed to terminal
```

The file also prints the generated Cypher so you can see what the LLM produced.

---

## Step 3 — Try these questions

Each one tests something different:

```
# Basic lookup
What products does Apple make?

# Multi-hop relationship
What products were made by companies that Elon Musk founded?

# Competition
Which products compete with ChatGPT?

# Aggregation
Which company makes the most products?

# Cross-company
Which cloud products are there and who makes them?
```

---

## Step 4 — YOUR TURN: improve the schema prompt

The LLM's quality depends on the schema you give it. Open the file and find `GRAPH_SCHEMA`.

Try adding more detail — for example, add example values:

```python
# Before
- Product {name, category, launched}

# After  
- Product {name, category (e.g. "AI", "cloud", "smartphone", "laptop"), launched (year)}
```

Does the LLM generate better Cypher with more context?

---

## Step 5 — What happens when it fails?

Try a question the graph can't answer:
```
Ask the graph > What is Apple's stock price?
```

The graph doesn't have stock data. Watch how the system handles an empty result — and think: how would you make it fail more gracefully?

---

## Reflection

- When would you use GraphRAG over plain RAG?
- What data in your own work would benefit from a graph structure?
- What would you add to this graph to make it more useful?
