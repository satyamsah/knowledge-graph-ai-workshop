# Slide Deck: 05 — Connecting the LLM to the Graph
### (2:30–3:00, 30 min)

---

## Slide 1 — The last piece

We have:
- ✓ A Knowledge Graph with real data
- ✓ Cypher queries that answer structured questions

Missing:
- ✗ A way for a user to ask questions in plain English

Solution: **let the LLM translate natural language → Cypher → answer**

---

## Slide 2 — The GraphRAG loop

```
User: "Which companies make AI products?"
          ↓
[LLM — Step 1: text → Cypher]
          ↓
"MATCH (c:Company)-[:MAKES]->(p:Product)
 WHERE p.category = 'AI'
 RETURN c.name, p.name"
          ↓
[Neo4j executes the query]
          ↓
[{company: "OpenAI", product: "ChatGPT"},
 {company: "Google", product: "Gemini"}, ...]
          ↓
[LLM — Step 2: results → natural language]
          ↓
"Based on the knowledge graph, companies making AI products include
 OpenAI (ChatGPT), Google (Gemini), Microsoft (Copilot)..."
```

---

## Slide 3 — The schema prompt

The LLM needs to know the graph's structure.

```python
SCHEMA = """
Node labels and properties:
- Company {name, founded, hq}
- Product  {name, category, launched}
- Person   {name}
- Division {name}

Relationship types:
- (Person)-[:FOUNDED]->(Company)
- (Person)-[:CEO_OF]->(Company)
- (Company)-[:MAKES]->(Product)
- (Company)-[:ACQUIRED]->(Company)
- (Product)-[:COMPETES_WITH]->(Product)
- (Division)-[:PART_OF]->(Company)
"""
```

---

## Slide 4 — Prompt design

```python
SYSTEM_PROMPT = f"""
You are a Cypher expert. Given a graph schema and a user question,
return ONLY a valid Cypher query — no explanation, no markdown.

Schema:
{SCHEMA}
"""
```

---

## Slide 5 — Two-step LLM calls

**Call 1 — translate question to Cypher:**
```python
cypher = llm.ask(system=SYSTEM_PROMPT, user=question)
```

**Run the query:**
```python
results = neo4j.run(cypher)
```

**Call 2 — synthesise the answer:**
```python
answer = llm.ask(
    system="You are a helpful assistant. Answer using only the provided data.",
    user=f"Question: {question}\n\nData: {results}"
)
```

---

## Slide 6 — What can go wrong (and how to handle it)

| Problem | Fix |
|---------|-----|
| LLM generates invalid Cypher | Catch the error, retry with the error message appended |
| Query returns empty results | Tell the LLM "no results found", let it say so honestly |
| LLM adds markdown fences to Cypher | Strip ` ```cypher ` blocks before running |
| Hallucinated property names | Include example values in the schema prompt |

---

## Slide 7 — Why this is powerful for your resume

- **GraphRAG** is a production pattern used at LinkedIn, Airbnb, JPMorgan
- Combines two hot skills: graph databases + LLM engineering
- Demonstrates you understand *when* to use a graph vs. vector search
- You built the whole stack: data model → query layer → LLM integration

---

## Facilitator notes

- Live demo: type a question, show the generated Cypher, show the result
- Ask: "What question would you most want to ask this graph?"
- Transition: "Let's now wire the whole thing together in the project"
