"""Exercise 1 — complete solution."""

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

with driver.session() as session:
    print(session.run("RETURN 'Hello, graph!' AS message").single()["message"])

def create_company(tx, name, founded, hq):
    tx.run(
        """
        MERGE (c:Company {name: $name})
        ON CREATE SET c.founded = $founded, c.hq = $hq
        """,
        name=name, founded=founded, hq=hq,
    )

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

with driver.session() as session:
    session.execute_write(create_company, "Apple",  1976, "Cupertino")
    session.execute_write(create_company, "Google", 1998, "Mountain View")
    print("✓ Companies created")

    session.execute_write(create_product, "Apple",  "iPhone",  "smartphone", 2007)
    session.execute_write(create_product, "Apple",  "MacBook", "laptop",     2006)
    session.execute_write(create_product, "Google", "Search",  "web service",1998)
    session.execute_write(create_product, "Google", "Android", "mobile OS",  2008)
    print("✓ Products linked")

    session.execute_write(create_person,  "Linus Torvalds")
    session.execute_write(create_company, "Linux Foundation", 1991, "San Francisco")
    session.execute_write(link_founder,   "Linus Torvalds", "Linux Foundation")
    print("✓ Linus Torvalds linked to Linux Foundation")

print("\nVerify in Neo4j browser:")
print("  MATCH (p:Person)-[:FOUNDED]->(c:Company) RETURN p, c")

driver.close()
