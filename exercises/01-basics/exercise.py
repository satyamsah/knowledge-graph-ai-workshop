"""
Exercise 1 — Your First Graph
================================
In this exercise you will:
  1. Connect to Neo4j from Python
  2. Create your first nodes and relationships
  3. See them appear in the browser

Run:  python exercises/01-basics/exercise.py
Then: open http://localhost:7474
"""

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ── Connect to Neo4j ──────────────────────────────────────────────────────
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── Step 1: test the connection ───────────────────────────────────────────
with driver.session() as session:
    result = session.run("RETURN 'Hello, graph!' AS message")
    print(result.single()["message"])

# ── Step 2: create two Company nodes ─────────────────────────────────────
#
# MERGE = create if it doesn't exist, find it if it does.
# $name is a parameter — the actual value comes from Python.
#
def create_company(tx, name, founded, hq):
    tx.run(
        """
        MERGE (c:Company {name: $name})
        ON CREATE SET c.founded = $founded, c.hq = $hq
        """,
        name=name, founded=founded, hq=hq,
    )

with driver.session() as session:
    session.execute_write(create_company, "Apple",  1976, "Cupertino")
    session.execute_write(create_company, "Google", 1998, "Mountain View")
    print("✓ Companies created — check http://localhost:7474")

# ── Step 3: create Products and link them to Companies ────────────────────
#
# MERGE (c)-[:MAKES]->(p) creates the relationship between company and product.
# [:MAKES] is the relationship type — always UPPER_SNAKE_CASE.
#
def create_product(tx, company, name, category, launched):
    tx.run(
        """
        MERGE (c:Company {name: $company})
        MERGE (p:Product {name: $name})
        ON CREATE SET p.category = $category, p.launched = $launched
        MERGE (c)-[:MAKES]->(p)
        """,
        company=company, name=name, category=category, launched=launched,
    )

with driver.session() as session:
    session.execute_write(create_product, "Apple",  "iPhone",  "smartphone", 2007)
    session.execute_write(create_product, "Apple",  "MacBook", "laptop",     2006)
    session.execute_write(create_product, "Google", "Search",  "web service",1998)
    session.execute_write(create_product, "Google", "Android", "mobile OS",  2008)
    print("✓ Products linked!")

print("\nOpen http://localhost:7474 and run:")
print('  MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p')

# ── Step 4: YOUR TURN ─────────────────────────────────────────────────────
#
# Add Linus Torvalds as the founder of Linux Foundation.
# This data is NOT in seed.py — you are genuinely adding something new.
#
# The Cypher patterns to use:
#   MERGE (:Person  {name: $name})
#   MATCH (p:Person {name: $person}), (c:Company {name: $company})
#   MERGE (p)-[:FOUNDED]->(c)
#
# Step a — fill in this function:
def create_person(tx, name):
    tx.run("MERGE (:Person {name: $name})", name=name)

def link_founder(tx, person, company):
    tx.run(
        """
        MATCH (p:Person  {name: $person})
        MATCH (c:Company {name: $company})
        MERGE (p)-[:FOUNDED]->(c)
        """,
        person=person, company=company,
    )
# Step c — uncomment these lines once your functions above are ready:
with driver.session() as session:
    session.execute_write(create_person,  "Linus Torvalds")
    session.execute_write(create_company, "Linux Foundation", 1991, "San Francisco")
    session.execute_write(link_founder,   "Linus Torvalds", "Linux Foundation")
    print("✓ Linus Torvalds linked to Linux Foundation")

# Step d — verify in the Neo4j browser:
#   MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c

# Stuck? See exercises/01-basics/solution.py

driver.close()
