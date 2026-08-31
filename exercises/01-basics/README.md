# Exercise 1 — Your First Graph
### Module: Knowledge Graphs 101 (0:45–1:15)

**Goal:** Connect to Neo4j from Python and create your first nodes and relationships.
**Time:** ~20 minutes
**You'll see:** A small graph appear in the Neo4j browser at http://localhost:7474

---

## Step 1 — Connect to Neo4j

Open a new file `exercises/01-basics/exercise.py` and paste this:

```python
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123"))
)

# Quick connectivity test
with driver.session() as session:
    result = session.run("RETURN 'Hello, graph!' AS message")
    print(result.single()["message"])
```

Run it:
```bash
python exercises/01-basics/exercise.py
```

Expected output:
```
Hello, graph!
```

---

## Step 2 — Create your first node

Add this to your file:

```python
def create_company(tx, name, founded, hq):
    tx.run(
        "MERGE (c:Company {name: $name}) "
        "ON CREATE SET c.founded = $founded, c.hq = $hq",
        name=name, founded=founded, hq=hq
    )

with driver.session() as session:
    session.execute_write(create_company, "Apple", 1976, "Cupertino")
    session.execute_write(create_company, "Google", 1998, "Mountain View")
    print("Companies created!")
```

Run it, then open http://localhost:7474 and run:
```cypher
MATCH (c:Company) RETURN c
```

You should see two nodes appear. Click on them to see their properties.

---

## Step 3 — Create a product and link it

```python
def create_product_and_link(tx, company_name, product_name, category, launched):
    tx.run(
        "MERGE (c:Company {name: $company_name}) "
        "MERGE (p:Product {name: $product_name}) "
        "ON CREATE SET p.category = $category, p.launched = $launched "
        "MERGE (c)-[:MAKES]->(p)",
        company_name=company_name,
        product_name=product_name,
        category=category,
        launched=launched
    )

with driver.session() as session:
    session.execute_write(create_product_and_link, "Apple",  "iPhone",  "smartphone", 2007)
    session.execute_write(create_product_and_link, "Apple",  "MacBook", "laptop",     2006)
    session.execute_write(create_product_and_link, "Google", "Search",  "web service",1998)
    session.execute_write(create_product_and_link, "Google", "Android", "mobile OS",  2008)
    print("Products linked!")
```

In the Neo4j browser run:
```cypher
MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p
```

You should now see a small graph with relationships.

---

## Step 4 — Your turn

Add a person node and connect them as a founder.

```python
# TODO: create a Person node for "Steve Jobs"
# TODO: create a FOUNDED relationship: (Steve Jobs)-[:FOUNDED]->(Apple)
# TODO: verify in Neo4j browser:
#   MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c
```

**Hint:** Use the same `MERGE` + `MERGE (a)-[:REL]->(b)` pattern from Step 3.

---

## What you just did

- Connected Python to a graph database
- Created nodes with labels and properties
- Created typed, directed relationships
- Ran your first Cypher queries

Next: we'll load a full dataset and explore richer queries.
