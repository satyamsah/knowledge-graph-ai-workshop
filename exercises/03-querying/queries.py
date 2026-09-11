"""
Exercise 3 — Querying the Graph with Cypher
============================================
In this exercise you will run 5 queries that show the power of graph traversal.
Each query is explained before you run it.

Run:  python exercises/03-querying/queries.py

Or paste queries one by one into http://localhost:7474
"""

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console
from rich.table import Table
from rich.rule import Rule

load_dotenv()
console = Console()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)


def run(cypher, **params):
    with driver.session() as session:
        return [dict(r) for r in session.run(cypher, **params)]


def show(title, explanation, cypher, results):
    console.print(Rule(f"[bold cyan]{title}[/bold cyan]"))
    console.print(f"[dim]{explanation}[/dim]\n")
    console.print(f"[yellow]{cypher.strip()}[/yellow]\n")

    if not results:
        console.print("[dim](no results)[/dim]\n")
        return

    # print as a table using the first result's keys as columns
    cols = list(results[0].keys())
    table = Table(*cols, show_header=True, header_style="bold")
    for r in results:
        table.add_row(*[str(r[c]) for c in cols])
    console.print(table)
    console.print()


# ── Query 1 — basic lookup ────────────────────────────────────────────────
#
# MATCH finds nodes/relationships that match the pattern.
# {name:"Apple"} filters to just the Apple node.
# RETURN chooses what to output.
# ORDER BY sorts the results.
#
show(
    "Query 1 — What products does Apple make?",
    "Basic pattern: Company -[:MAKES]-> Product",
    """
    MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
    RETURN p.name, p.category, p.launched
    ORDER BY p.launched
    """,
    run("""
        MATCH (c:Company {name:"Apple"})-[:MAKES]->(p:Product)
        RETURN p.name, p.category, p.launched
        ORDER BY p.launched
    """),
)

# ── Query 2 — multi-hop traversal ─────────────────────────────────────────
#
# This query follows TWO relationships in one go:
#   Person -[:FOUNDED]-> Company -[:MAKES]-> Product
#
# In SQL this would need two JOINs. In Cypher — just follow the arrows.
#
show(
    "Query 2 — What did Elon Musk's companies build?",
    "Two hops: Person -[:FOUNDED]-> Company -[:MAKES]-> Product",
    """
    MATCH (p:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(prod:Product)
    RETURN c.name AS company, prod.name AS product, prod.category
    """,
    run("""
        MATCH (p:Person {name:"Elon Musk"})-[:FOUNDED]->(c:Company)-[:MAKES]->(prod:Product)
        RETURN c.name AS company, prod.name AS product, prod.category
    """),
)

# ── Query 3 — competition network ─────────────────────────────────────────
#
# This query goes forward AND backward:
#   AWS -[:COMPETES_WITH]-> competitor <-[:MAKES]- Company
#
# The arrow <-[:MAKES]- goes BACKWARDS — finding who makes the competitor.
#
show(
    "Query 3 — What competes with AWS, and who makes it?",
    "Forward to competitor, then backwards to find the maker",
    """
    MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
    RETURN c.name AS made_by, comp.name AS competing_product
    """,
    run("""
        MATCH (aws:Product {name:"AWS"})-[:COMPETES_WITH]->(comp:Product)<-[:MAKES]-(c:Company)
        RETURN c.name AS made_by, comp.name AS competing_product
    """),
)

# ── Query 4 — aggregation ─────────────────────────────────────────────────
#
# COUNT(p) counts how many products each company has.
# ORDER BY ... DESC sorts from highest to lowest.
#
show(
    "Query 4 — Which company makes the most products?",
    "COUNT() aggregates, ORDER BY ranks the results",
    """
    MATCH (c:Company)-[:MAKES]->(p:Product)
    RETURN c.name, COUNT(p) AS num_products
    ORDER BY num_products DESC
    """,
    run("""
        MATCH (c:Company)-[:MAKES]->(p:Product)
        RETURN c.name, COUNT(p) AS num_products
        ORDER BY num_products DESC
    """),
)

# ── Query 5 — filter by property ──────────────────────────────────────────
#
# WHERE filters nodes by their properties.
# You can combine conditions with AND / OR.
#
show(
    "Query 5 — Which AI products launched in 2022 or later?",
    "WHERE filters by property value — like SQL WHERE",
    """
    MATCH (p:Product)
    WHERE p.category = "AI" AND p.launched >= 2022
    RETURN p.name, p.launched
    ORDER BY p.launched
    """,
    run("""
        MATCH (p:Product)
        WHERE p.category = "AI" AND p.launched >= 2022
        RETURN p.name, p.launched
        ORDER BY p.launched
    """),
)

# ── YOUR TURN — two challenges ────────────────────────────────────────────
#
# Try these in the Neo4j browser at http://localhost:7474
#
# Challenge 1:
#   Which companies have BOTH a cloud product AND an AI product?
#   Hint: use two MATCH patterns on the same company node (c)
#
# Challenge 2:
#   Who is the CEO of a company that was founded by someone else?
#   Hint: match both [:CEO_OF] and [:FOUNDED] on the same company,
#         then check the two people are different (ceo <> founder)
#
console.print(Rule("[bold]Your Turn — Try These in the Browser[/bold]"))
console.print("""
[bold]Challenge 1:[/bold] Companies with both a cloud AND an AI product

  MATCH (c:Company)-[:MAKES]->(cloud:Product {category:"cloud"})
  MATCH (c)-[:MAKES]->(ai:Product {category:"AI"})
  RETURN c.name, cloud.name AS cloud_product, ai.name AS ai_product

[bold]Challenge 2:[/bold] Who is CEO of a company they did NOT found?

  MATCH (ceo:Person)-[:CEO_OF]->(c:Company)
  WHERE NOT (ceo)-[:FOUNDED]->(c)
  RETURN ceo.name AS ceo, c.name AS company
""")

driver.close()
