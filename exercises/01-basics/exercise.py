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
#
# GraphDatabase.driver() opens a connection to Neo4j.
# We read the connection details from the .env file.
#
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── Step 1: test the connection ───────────────────────────────────────────
#
# session.run() sends a Cypher query to Neo4j.
# RETURN just sends back a value — like print() but in Cypher.
#
with driver.session() as session:
    result = session.run("RETURN 'Hello, graph!' AS message")
    print(result.single()["message"])

# ── Step 2: create two Company nodes ─────────────────────────────────────
#
# MERGE = create this node if it doesn't exist, find it if it does.
# :Company is the label (type of node).
# {name: $name} is a property — $name is a parameter filled in by Python.
#
# We use execute_write() to wrap our function in a transaction.
# A transaction means: do all of this, or none of it.
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
    print("✓ Companies created")

# ── Step 3: create Products and link them to Companies ────────────────────
#
# This time we create two nodes AND a relationship in one query.
#
# MERGE (c:Company {name: $company}) — find the existing company
# MERGE (p:Product {name: $name})    — create the product if it doesn't exist
# MERGE (c)-[:MAKES]->(p)            — create the relationship between them
#
# [:MAKES] is the relationship type — always UPPER_SNAKE_CASE
# The arrow -> shows direction: Company MAKES Product
#
def create_product(tx, company, name, category, launched):
    tx.run(
        """
        MERGE (c:Company  {name: $company})
        MERGE (p:Product  {name: $name})
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
    print("✓ Products linked")

print("\nOpen http://localhost:7474 and run:")
print('  MATCH (c:Company)-[:MAKES]->(p:Product) RETURN c, p')

# ── Step 4: YOUR TURN ─────────────────────────────────────────────────────
#
# Add a founder to the graph — using data NOT already in our main dataset.
#
# We'll add:  Linus Torvalds  -[:FOUNDED]->  Linux Foundation
#
# This is real data — Linus Torvalds created Linux in 1991.
# It's not in seed.py so you're genuinely adding something new.
#
# You need to:
#   a) Create a Person node for Linus Torvalds
#   b) Create a Company node for Linux Foundation
#   c) Create a [:FOUNDED] relationship between them
#
# The Cypher patterns:
#   MERGE (p:Person  {name: $name})
#   MERGE (c:Company {name: $name})
#   MATCH (p:Person  {name: $person}), (c:Company {name: $company})
#   MERGE (p)-[:FOUNDED]->(c)
#
# Step a — fill in this function:
def create_person(tx, name):
    pass  # TODO: replace 'pass' with a tx.run() that MERGEs a Person node

# Step b — fill in this function (reuse create_company from Step 2 above):
# create_company is already defined — you can call it directly.

# Step c — fill in this function:
def link_founder(tx, person, company):
    pass  # TODO: replace 'pass' with a tx.run() that MERGEs a [:FOUNDED] relationship

# Step d — uncomment these lines once your functions are ready:
# with driver.session() as session:
#     session.execute_write(create_person,  "Linus Torvalds")
#     session.execute_write(create_company, "Linux Foundation", 1991, "San Francisco")
#     session.execute_write(link_founder,   "Linus Torvalds", "Linux Foundation")
#     print("✓ Linus Torvalds linked to Linux Foundation")

# Step e — verify in the Neo4j browser:
#   MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c

# ── Stuck? See exercises/01-basics/solution.py ────────────────────────────

driver.close()
