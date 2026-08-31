# Slide Deck: 04 — Querying with Cypher
### (2:00–2:30, 30 min)

---

## Slide 1 — Meet Cypher

Neo4j's query language. Designed to look like the graph itself.

```cypher
MATCH (c:Company)-[:MAKES]->(p:Product)
WHERE c.name = "Apple"
RETURN p.name
```

Read it like English: *"Find a Company that MAKES a Product, where the company is Apple, return the product name."*

---

## Slide 2 — The MATCH clause

`MATCH` describes a pattern to find in the graph.

```cypher
-- Find all companies
MATCH (c:Company) RETURN c.name

-- Find all products made by Google
MATCH (c:Company {name:"Google"})-[:MAKES]->(p:Product)
RETURN p.name

-- Find founders
MATCH (person:Person)-[:FOUNDED]->(company:Company)
RETURN person.name, company.name
```

---

## Slide 3 — Filtering with WHERE

```cypher
MATCH (p:Product)
WHERE p.category = "smartphone"
RETURN p.name, p.launched

-- Multiple conditions
MATCH (c:Company)
WHERE c.founded > 2000 AND c.hq = "San Francisco"
RETURN c.name
```

---

## Slide 4 — Multi-hop traversal

This is where graphs earn their keep.

```cypher
-- "What products are made by companies founded by Elon Musk?"
MATCH (person:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN c.name, p.name

-- "What products compete with Apple products?"
MATCH (apple:Company {name:"Apple"})-[:MAKES]->(ap:Product)-[:COMPETES_WITH]->(cp:Product)<-[:MAKES]-(competitor:Company)
RETURN competitor.name, ap.name AS apple_product, cp.name AS competing_product
```

---

## Slide 5 — Aggregation

```cypher
-- How many products does each company make?
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COUNT(p) AS product_count
ORDER BY product_count DESC

-- Which company has the most acquisitions?
MATCH (c:Company)-[:ACQUIRED]->(other:Company)
RETURN c.name, COUNT(other) AS acquisitions
ORDER BY acquisitions DESC
```

---

## Slide 6 — Creating data

```cypher
-- Create a node
CREATE (c:Company {name:"OpenAI", founded:2015, hq:"San Francisco"})

-- Create a relationship
MATCH (p:Person {name:"Sam Altman"}), (c:Company {name:"OpenAI"})
CREATE (p)-[:CEO_OF]->(c)

-- Create everything at once
CREATE (p:Person {name:"Sam Altman"})-[:CEO_OF]->(c:Company {name:"OpenAI"})
```

---

## Slide 7 — MERGE (upsert)

`MERGE` = create if it doesn't exist, match if it does. Safe for repeated loads.

```cypher
MERGE (c:Company {name:"Apple"})
ON CREATE SET c.founded = 1976, c.hq = "Cupertino"
```

---

## Facilitator notes

- Run each query live in the Neo4j browser — let people see the graph visualisation
- The multi-hop query on slide 4 is the "wow" moment — pause and let it land
- Good exercise: "write a query to find all AI products"
