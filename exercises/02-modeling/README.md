# Exercise 2 — Load the Full Dataset
### Module: Modeling & Loading (1:30–2:00)

**Goal:** Seed the graph with all companies, people, products, and relationships.
**Time:** ~20 minutes
**You'll see:** A rich, connected graph of the tech world in Neo4j.

---

## Step 1 — Clear any previous data

In the Neo4j browser run:
```cypher
MATCH (n) DETACH DELETE n
```

This wipes the database so we start fresh with the full dataset.

---

## Step 2 — Run the seed script

```bash
python exercises/02-modeling/seed.py
```

Expected output:
```
Seeding companies...   ✓ 8 companies
Seeding people...      ✓ 9 people
Seeding products...    ✓ 22 products
Seeding relationships...  ✓ done
Graph is ready!
```

---

## Step 3 — Explore in the browser

Open http://localhost:7474 and run each of these — take a moment to look at the graph:

```cypher
-- See everything (keep it small)
MATCH (n) RETURN n LIMIT 50

-- Just companies and their products
MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p

-- Founders and their companies
MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c

-- Acquisitions
MATCH (a:Company)-[:ACQUIRED]->(b:Company) RETURN a, b
```

---

## Step 4 — What's in the graph?

Look at the seed data in `exercises/02-modeling/seed.py` and answer:

1. Which company has the most products?
2. Is there anyone who founded more than one company?
3. Which products compete with each other?

Try to answer with Cypher queries — not by reading the Python file!

```cypher
-- Your queries here
```

---

## Bonus: add your own node

Pick any real tech company, person, or product not already in the graph and add it:

```cypher
MERGE (c:Company {name:"Your Company", founded:2020, hq:"Your City"})
MERGE (p:Product {name:"Your Product", category:"your category"})
MERGE (c)-[:MAKES]->(p)
```
