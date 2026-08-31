# Exercise 3 — Querying the Graph
### Module: Cypher Queries (2:00–2:30)

**Goal:** Write Cypher queries that answer real questions about the tech world.
**Time:** ~20 minutes
**You'll see:** How graph traversal finds answers that SQL would struggle with.

---

## Open the query file

```bash
# Run queries from Python
python exercises/03-querying/queries.py
```

Or paste each query directly into the Neo4j browser at http://localhost:7474.

---

## Query 1 — Basic lookup

**"What products does Apple make?"**

```cypher
MATCH (c:Company {name: "Apple"})-[:MAKES]->(p:Product)
RETURN p.name, p.category, p.launched
ORDER BY p.launched
```

---

## Query 2 — Multi-hop: founders and their products

**"What products were made by companies that Elon Musk founded?"**

```cypher
MATCH (person:Person {name: "Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN c.name AS company, p.name AS product, p.category
```

---

## Query 3 — Competition network

**"What products compete with AWS, and who makes them?"**

```cypher
MATCH (aws:Product {name: "AWS"})-[:COMPETES_WITH]->(competitor:Product)<-[:MAKES]-(c:Company)
RETURN c.name AS made_by, competitor.name AS product
```

---

## Query 4 — Aggregation

**"Which company makes the most products? Rank them."**

```cypher
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COUNT(p) AS num_products
ORDER BY num_products DESC
```

---

## Query 5 — Filter by property

**"Which AI products launched after 2022?"**

```cypher
MATCH (p:Product)
WHERE p.category = "AI" AND p.launched >= 2022
RETURN p.name, p.launched
ORDER BY p.launched
```

---

## Query 6 — YOUR TURN (harder)

Write a query that answers:

**"Which companies have both a cloud product AND an AI product?"**

```cypher
-- Your query here
-- Hint: use two MATCH patterns or WHERE + EXISTS
```

**"Who is the CEO of a company that was also founded by someone else?"**

```cypher
-- Your query here
-- Hint: MATCH two separate relationship patterns on the same company
```

---

## What just happened

Notice how the multi-hop queries in #2 and #3 would require multiple JOINs in SQL — in Cypher you just follow the arrows. This is the core power of graph databases for connected data.
