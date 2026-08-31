"""Exercise 1 — complete solution."""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

with driver.session() as session:
    print(session.run("RETURN 'Hello, graph!' AS message").single()["message"])

def create_company(tx, name, founded, hq):
    tx.run(
        "MERGE (c:Company {name: $name}) ON CREATE SET c.founded=$founded, c.hq=$hq",
        name=name, founded=founded, hq=hq,
    )

def create_product_and_link(tx, company_name, product_name, category, launched):
    tx.run(
        "MERGE (c:Company {name:$company_name}) "
        "MERGE (p:Product {name:$product_name}) "
        "ON CREATE SET p.category=$category, p.launched=$launched "
        "MERGE (c)-[:MAKES]->(p)",
        company_name=company_name, product_name=product_name,
        category=category, launched=launched,
    )

def create_person(tx, name):
    tx.run("MERGE (:Person {name: $name})", name=name)

def link_founder(tx, person_name, company_name):
    tx.run(
        "MATCH (p:Person {name:$person_name}), (c:Company {name:$company_name}) "
        "MERGE (p)-[:FOUNDED]->(c)",
        person_name=person_name, company_name=company_name,
    )

with driver.session() as session:
    session.execute_write(create_company, "Apple",  1976, "Cupertino")
    session.execute_write(create_company, "Google", 1998, "Mountain View")
    session.execute_write(create_product_and_link, "Apple",  "iPhone",  "smartphone", 2007)
    session.execute_write(create_product_and_link, "Apple",  "MacBook", "laptop",     2006)
    session.execute_write(create_product_and_link, "Google", "Search",  "web service",1998)
    session.execute_write(create_product_and_link, "Google", "Android", "mobile OS",  2008)
    session.execute_write(create_person,    "Steve Jobs")
    session.execute_write(link_founder,     "Steve Jobs", "Apple")
    print("Done! Verify at http://localhost:7474")

driver.close()
