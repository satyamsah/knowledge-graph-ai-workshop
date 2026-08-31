# Cypher Cheat Sheet

Quick reference for the queries you'll use most in the workshop.

---

## Creating data

```cypher
-- Create a node
CREATE (n:Label {property: "value"})

-- Create only if it doesn't exist (upsert)
MERGE (n:Label {name: "Apple"})

-- Create with extra properties on first creation
MERGE (n:Company {name: "Apple"})
ON CREATE SET n.founded = 1976, n.hq = "Cupertino"

-- Create a relationship between two existing nodes
MATCH (a:Company {name:"Apple"}), (p:Product {name:"iPhone"})
MERGE (a)-[:MAKES]->(p)
```

---

## Reading data

```cypher
-- All nodes of a type
MATCH (c:Company) RETURN c

-- Filter by property
MATCH (c:Company {name: "Google"}) RETURN c

-- WHERE clause (more flexible)
MATCH (c:Company)
WHERE c.founded > 2000
RETURN c.name, c.founded

-- Traverse a relationship
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, p.name

-- Multi-hop traversal
MATCH (person:Person)-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
RETURN person.name, c.name, p.name

-- Variable-length path (1 to 3 hops)
MATCH (a)-[*1..3]->(b)
WHERE a.name = "Apple"
RETURN a, b
```

---

## Aggregation & sorting

```cypher
-- Count
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COUNT(p) AS total
ORDER BY total DESC

-- Collect into a list
MATCH (c:Company)-[:MAKES]->(p:Product)
RETURN c.name, COLLECT(p.name) AS products

-- LIMIT results
MATCH (p:Product) RETURN p.name LIMIT 10
```

---

## Useful functions

```cypher
toLower(n.name)          -- lowercase comparison
toUpper(n.name)          -- uppercase
toString(n.founded)      -- cast to string
n.launched IS NOT NULL   -- null check
n.name CONTAINS "AI"     -- substring match
n.name STARTS WITH "G"   -- prefix match
```

---

## Deleting data

```cypher
-- Delete a node (must have no relationships first)
MATCH (n:Company {name:"test"}) DELETE n

-- Delete node AND its relationships
MATCH (n:Company {name:"test"}) DETACH DELETE n

-- Wipe everything
MATCH (n) DETACH DELETE n
```

---

## Pattern quick reference

| Pattern | Meaning |
|---------|---------|
| `(n:Label)` | Node with label |
| `(n {key:"val"})` | Node with property |
| `-[:TYPE]->` | Directed relationship |
| `-[:TYPE]-` | Either direction |
| `(a)-[r]->(b)` | Relationship as variable `r` |
| `(a)-[*2]->(b)` | Exactly 2 hops |
| `(a)-[*1..3]->(b)` | 1 to 3 hops |
