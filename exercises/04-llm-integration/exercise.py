"""
Exercise 4 — natural language Q&A over the knowledge graph.
Run:  python exercises/04-llm-integration/exercise.py
"""

import os
import re
from dotenv import load_dotenv
import anthropic
from neo4j import GraphDatabase
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)
llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Graph schema given to the LLM ─────────────────────────────────────────
GRAPH_SCHEMA = """
Node labels and key properties:
  Company  { name, founded (year), hq (city) }
  Product  { name, category (e.g. "AI", "cloud", "smartphone", "laptop", "mobile OS"), launched (year) }
  Person   { name }

Relationship types (direction matters):
  (Person)  -[:FOUNDED]->       (Company)
  (Person)  -[:CEO_OF]->        (Company)
  (Company) -[:MAKES]->         (Product)
  (Company) -[:ACQUIRED]->      (Company)
  (Product) -[:COMPETES_WITH]-> (Product)

Example data:
  Companies : Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla
  People    : Steve Jobs, Elon Musk, Sam Altman, Jensen Huang, Mark Zuckerberg
  Products  : iPhone, Android, Windows, AWS, Azure, ChatGPT, Gemini, Claude, VS Code
"""

CYPHER_SYSTEM = f"""You are a Cypher expert for Neo4j.
Given the graph schema below, translate the user's question into a valid Cypher query.
Return ONLY the Cypher query — no explanation, no markdown fences, no comments.

{GRAPH_SCHEMA}"""

ANSWER_SYSTEM = """You are a helpful assistant answering questions about the tech industry.
You will be given a question and structured data from a knowledge graph.
Answer conversationally in 2–4 sentences using only the provided data.
If the data is empty, say the graph doesn't have that information."""


def question_to_cypher(question: str) -> str:
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=CYPHER_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    cypher = response.content[0].text.strip()
    # Strip markdown fences if the model adds them anyway
    cypher = re.sub(r"^```(?:cypher)?\s*", "", cypher, flags=re.IGNORECASE)
    cypher = re.sub(r"\s*```$", "", cypher)
    return cypher.strip()


def run_cypher(cypher: str) -> list[dict]:
    with neo4j_driver.session() as session:
        return [dict(r) for r in session.run(cypher)]


def results_to_answer(question: str, results: list[dict]) -> str:
    data_str = str(results) if results else "(no results found)"
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": f"Question: {question}\n\nGraph data: {data_str}"}],
    )
    return response.content[0].text.strip()


def ask(question: str):
    console.print(f"\n[bold]Question:[/bold] {question}")

    # Step 1 — generate Cypher
    try:
        cypher = question_to_cypher(question)
        console.print(Panel(cypher, title="[dim]Generated Cypher[/dim]", border_style="dim"))
    except Exception as e:
        console.print(f"[red]LLM error: {e}[/red]")
        return

    # Step 2 — run query
    try:
        results = run_cypher(cypher)
    except Exception as e:
        console.print(f"[red]Query error: {e}[/red]")
        console.print("[dim]The LLM generated invalid Cypher. Try rephrasing your question.[/dim]")
        return

    # Step 3 — synthesise answer
    answer = results_to_answer(question, results)
    console.print(Panel(answer, title="[green]Answer[/green]", border_style="green"))


def main():
    console.print("\n[bold green]Knowledge Graph Q&A[/bold green]")
    console.print("Ask anything about tech companies and products. Type [bold]quit[/bold] to exit.\n")

    while True:
        try:
            question = input("Ask the graph > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break

        ask(question)

    neo4j_driver.close()
    console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()
