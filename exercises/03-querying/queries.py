"""
Exercise 3 — run Cypher queries and print results.
Run:  python exercises/03-querying/queries.py
"""

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)


def run_and_print(title, cypher, columns):
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    with driver.session() as session:
        records = list(session.run(cypher))

    if not records:
        console.print("[yellow]  (no results)[/yellow]")
        return

    table = Table(*columns, show_header=True, header_style="bold")
    for r in records:
        table.add_row(*[str(r[c]) for c in columns])
    console.print(table)


# ── Query 1: Apple products ───────────────────────────────────────────────
run_and_print(
    "1. Apple products",
    """
    MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
    RETURN p.name, p.category, p.launched
    ORDER BY p.launched
    """,
    ["p.name", "p.category", "p.launched"],
)

# ── Query 2: Elon Musk's companies and products ───────────────────────────
run_and_print(
    "2. Products from Elon Musk's companies",
    """
    MATCH (person:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(p:Product)
    RETURN c.name AS company, p.name AS product, p.category
    """,
    ["company", "product", "category"],
)

# ── Query 3: AWS competition ───────────────────────────────────────────────
run_and_print(
    "3. Products that compete with AWS",
    """
    MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
    RETURN c.name AS made_by, comp.name AS product
    """,
    ["made_by", "product"],
)

# ── Query 4: company product counts ───────────────────────────────────────
run_and_print(
    "4. Products per company (ranked)",
    """
    MATCH (c:Company)-[:MAKES]->(p:Product)
    RETURN c.name, COUNT(p) AS num_products
    ORDER BY num_products DESC
    """,
    ["c.name", "num_products"],
)

# ── Query 5: recent AI products ───────────────────────────────────────────
run_and_print(
    "5. AI products launched 2022+",
    """
    MATCH (p:Product)
    WHERE p.category = "AI" AND p.launched >= 2022
    RETURN p.name, p.launched
    ORDER BY p.launched
    """,
    ["p.name", "p.launched"],
)

# ── Query 6: YOUR TURN ────────────────────────────────────────────────────
# TODO: Companies with both cloud AND AI products
# TODO: CEO of a company where someone else is the founder

driver.close()
