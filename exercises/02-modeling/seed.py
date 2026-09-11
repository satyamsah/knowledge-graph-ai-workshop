"""
Exercise 2 — seed the full tech knowledge graph.
Run:  python exercises/02-modeling/seed.py
"""

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console

load_dotenv()
console = Console()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── Data ──────────────────────────────────────────────────────────────────

COMPANIES = [
    {"name": "Apple",     "founded": 1976, "hq": "Cupertino"},
    {"name": "Google",    "founded": 1998, "hq": "Mountain View"},
    {"name": "Microsoft", "founded": 1975, "hq": "Redmond"},
    {"name": "Amazon",    "founded": 1994, "hq": "Seattle"},
    {"name": "Meta",      "founded": 2004, "hq": "Menlo Park"},
    {"name": "OpenAI",    "founded": 2015, "hq": "San Francisco"},
    {"name": "Nvidia",    "founded": 1993, "hq": "Santa Clara"},
    {"name": "Tesla",     "founded": 2003, "hq": "Austin"},
    {"name": "SpaceX",    "founded": 2002, "hq": "Hawthorne"},
    {"name": "Anthropic", "founded": 2021, "hq": "San Francisco"},
]

PEOPLE = [
    {"name": "Steve Jobs"},
    {"name": "Steve Wozniak"},
    {"name": "Bill Gates"},
    {"name": "Jeff Bezos"},
    {"name": "Mark Zuckerberg"},
    {"name": "Elon Musk"},
    {"name": "Sundar Pichai"},
    {"name": "Sam Altman"},
    {"name": "Jensen Huang"},
    {"name": "Dario Amodei"},
    {"name": "Larry Page"},
    {"name": "Sergey Brin"},
]

PRODUCTS = [
    {"name": "iPhone",        "company": "Apple",     "category": "smartphone",   "launched": 2007},
    {"name": "MacBook",       "company": "Apple",     "category": "laptop",       "launched": 2006},
    {"name": "iPad",          "company": "Apple",     "category": "tablet",       "launched": 2010},
    {"name": "Apple Watch",   "company": "Apple",     "category": "wearable",     "launched": 2015},
    {"name": "Xcode",         "company": "Apple",     "category": "dev tool",     "launched": 2003},
    {"name": "Android",       "company": "Google",    "category": "mobile OS",    "launched": 2008},
    {"name": "Google Search", "company": "Google",    "category": "web service",  "launched": 1998},
    {"name": "Gmail",         "company": "Google",    "category": "email",        "launched": 2004},
    {"name": "Google Cloud",  "company": "Google",    "category": "cloud",        "launched": 2008},
    {"name": "Gemini",        "company": "Google",    "category": "AI",           "launched": 2023},
    {"name": "Windows",       "company": "Microsoft", "category": "desktop OS",   "launched": 1985},
    {"name": "Azure",         "company": "Microsoft", "category": "cloud",        "launched": 2010},
    {"name": "VS Code",       "company": "Microsoft", "category": "dev tool",     "launched": 2015},
    {"name": "GitHub",        "company": "Microsoft", "category": "dev platform", "launched": 2008},
    {"name": "Copilot",       "company": "Microsoft", "category": "AI",           "launched": 2023},
    {"name": "AWS",           "company": "Amazon",    "category": "cloud",        "launched": 2006},
    {"name": "Alexa",         "company": "Amazon",    "category": "AI assistant", "launched": 2014},
    {"name": "Facebook",      "company": "Meta",      "category": "social media", "launched": 2004},
    {"name": "Instagram",     "company": "Meta",      "category": "social media", "launched": 2010},
    {"name": "WhatsApp",      "company": "Meta",      "category": "messaging",    "launched": 2009},
    {"name": "ChatGPT",       "company": "OpenAI",    "category": "AI",           "launched": 2022},
    {"name": "Claude",        "company": "Anthropic", "category": "AI",           "launched": 2023},
    {"name": "H100",          "company": "Nvidia",    "category": "GPU",          "launched": 2022},
    {"name": "Tesla Model S", "company": "Tesla",     "category": "EV",           "launched": 2012},
    {"name": "Autopilot",     "company": "Tesla",     "category": "AI",           "launched": 2014},
]

FOUNDED = [
    ("Steve Jobs",       "Apple"),
    ("Steve Wozniak",    "Apple"),
    ("Bill Gates",       "Microsoft"),
    ("Jeff Bezos",       "Amazon"),
    ("Mark Zuckerberg",  "Meta"),
    ("Elon Musk",        "Tesla"),
    ("Elon Musk",        "SpaceX"),
    ("Sam Altman",       "OpenAI"),
    ("Jensen Huang",     "Nvidia"),
    ("Dario Amodei",     "Anthropic"),
    ("Larry Page",       "Google"),
    ("Sergey Brin",      "Google"),
]

CEO_OF = [
    ("Sundar Pichai",    "Google"),
    ("Sam Altman",       "OpenAI"),
    ("Mark Zuckerberg",  "Meta"),
    ("Jensen Huang",     "Nvidia"),
    ("Dario Amodei",     "Anthropic"),
    ("Jeff Bezos",       "Amazon"),
]

ACQUIRED = [
    ("Microsoft", "GitHub"),    # GitHub was a company before acquisition
    ("Meta",      "Instagram"),
    ("Meta",      "WhatsApp"),
    ("Google",    "Android"),   # Android Inc. acquired 2005
]

COMPETES_WITH = [
    ("iPhone",       "Android"),
    ("MacBook",      "Windows"),
    ("AWS",          "Azure"),
    ("AWS",          "Google Cloud"),
    ("Azure",        "Google Cloud"),
    ("ChatGPT",      "Gemini"),
    ("ChatGPT",      "Claude"),
    ("Gemini",       "Claude"),
    ("Copilot",      "ChatGPT"),
    ("VS Code",      "Xcode"),
    ("Facebook",     "Instagram"),
    ("Alexa",        "Siri"),
]

# ── Seed functions ────────────────────────────────────────────────────────

def seed(session):
    console.print("[bold]Seeding companies...[/bold]", end="  ")
    for c in COMPANIES:
        session.run(
            "MERGE (n:Company {name:$name}) ON CREATE SET n.founded=$founded, n.hq=$hq",
            **c,
        )
    console.print(f"[green]✓ {len(COMPANIES)} companies[/green]")

    console.print("[bold]Seeding people...[/bold]", end="    ")
    for p in PEOPLE:
        session.run("MERGE (:Person {name:$name})", **p)
    console.print(f"[green]✓ {len(PEOPLE)} people[/green]")

    console.print("[bold]Seeding products...[/bold]", end="   ")
    for p in PRODUCTS:
        session.run(
            "MERGE (c:Company {name:$company}) "
            "MERGE (p:Product {name:$name}) "
            "ON CREATE SET p.category=$category, p.launched=$launched "
            "MERGE (c)-[:MAKES]->(p)",
            **p,
        )
    console.print(f"[green]✓ {len(PRODUCTS)} products[/green]")

    console.print("[bold]Seeding relationships...[/bold]", end=" ")
    for person, company in FOUNDED:
        session.run(
            "MATCH (p:Person {name:$p}), (c:Company {name:$c}) MERGE (p)-[:FOUNDED]->(c)",
            p=person, c=company,
        )
    for person, company in CEO_OF:
        session.run(
            "MATCH (p:Person {name:$p}), (c:Company {name:$c}) MERGE (p)-[:CEO_OF]->(c)",
            p=person, c=company,
        )
    for acquirer, acquired in ACQUIRED:
        session.run(
            "MATCH (a:Company {name:$a}), (b {name:$b}) MERGE (a)-[:ACQUIRED]->(b)",
            a=acquirer, b=acquired,
        )
    for p1, p2 in COMPETES_WITH:
        session.run(
            "MATCH (a {name:$a}), (b {name:$b}) MERGE (a)-[:COMPETES_WITH]->(b)",
            a=p1, b=p2,
        )
    console.print("[green]✓ done[/green]")

    console.print("\n[green bold]Graph is ready! Open http://localhost:7474[/green bold]\n")


with driver.session() as s:
    seed(s)

driver.close()
