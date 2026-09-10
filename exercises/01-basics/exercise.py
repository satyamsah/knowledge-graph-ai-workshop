"""
Exercise 1 — starter file.
Fill in the TODOs, then run:  python exercises/01-basics/exercise.py
"""

from neo4j import GraphDatabase
import os
import warnings
from dotenv import load_dotenv

# suppress noisy shutdown warnings from the Neo4j driver on Python 3.14
warnings.filterwarnings("ignore")

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── Step 1: connectivity test ──────────────────────────────────────────────
with driver.session() as session:
    result = session.run("RETURN 'Hello, graph!' AS message")
    print(result.single()["message"])

# ── Step 2: create companies ───────────────────────────────────────────────
def create_company(tx, name, founded, hq):
    tx.run(
        "MERGE (c:Company {name: $name}) "
        "ON CREATE SET c.founded = $founded, c.hq = $hq",
        name=name, founded=founded, hq=hq,
    )

with driver.session() as session:
    session.execute_write(create_company, "Apple",  1976, "Cupertino")
    session.execute_write(create_company, "Google", 1998, "Mountain View")
    print("Companies created — check http://localhost:7474")

# ── Step 3: create products and link them ─────────────────────────────────
def create_product_and_link(tx, company_name, product_name, category, launched):
    tx.run(
        "MERGE (c:Company {name: $company_name}) "
        "MERGE (p:Product {name: $product_name}) "
        "ON CREATE SET p.category = $category, p.launched = $launched "
        "MERGE (c)-[:MAKES]->(p)",
        company_name=company_name,
        product_name=product_name,
        category=category,
        launched=launched,
    )

with driver.session() as session:
    session.execute_write(create_product_and_link, "Apple",  "iPhone",  "smartphone", 2007)
    session.execute_write(create_product_and_link, "Apple",  "MacBook", "laptop",     2006)
    session.execute_write(create_product_and_link, "Google", "Search",  "web service",1998)
    session.execute_write(create_product_and_link, "Google", "Android", "mobile OS",  2008)
    print("Products linked!")

# ── Step 4: YOUR TURN ──────────────────────────────────────────────────────
# TODO 1: Write a function create_person(tx, name) that MERGEs a Person node.

# TODO 2: Write a function link_founder(tx, person_name, company_name) that
#         MERGEs a (Person)-[:FOUNDED]->(Company) relationship.

# TODO 3: Call both functions to link "Steve Jobs" → "Apple".

# TODO 4: In the Neo4j browser verify with:
#   MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c

driver.close()
