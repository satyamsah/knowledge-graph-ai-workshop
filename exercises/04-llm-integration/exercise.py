"""
Exercise 4 — Natural Language Q&A over the Knowledge Graph
===========================================================
In this exercise you will see the full GraphRAG pipeline in action:

  Your question
      → LLM Call 1: translates your question into a Cypher query
      → Neo4j runs the Cypher query
      → LLM Call 2: turns the raw results into a plain English answer

You don't write Cypher — the LLM writes it for you.
But you can see exactly what Cypher it generated in the output.

Run:  python exercises/04-llm-integration/exercise.py
"""

import os
import re
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import anthropic
from neo4j import GraphDatabase
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

# ── Clients ───────────────────────────────────────────────────────────────

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)
llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Graph schema ──────────────────────────────────────────────────────────
#
# This is what we give to the LLM so it knows how to write Cypher.
# It describes the nodes, their properties, and the relationships.
# The better the schema, the better the Cypher the LLM generates.
#
# Important: the category values here must match what's in the database.
# They were set by seed.py — check seed.py if you're unsure.
#
GRAPH_SCHEMA = """
Node labels and key properties:
  Company { name, founded (year as integer), hq (city as string) }
  Product { name,
            category — one of: "AI", "cloud", "smartphone", "laptop", "tablet",
                       "wearable", "mobile OS", "desktop OS", "dev tool",
                       "dev platform", "email", "web service", "social media",
                       "messaging", "AI assistant", "GPU", "EV",
            launched (year as integer) }
  Person  { name }

Relationship types — direction matters, always use exactly as shown:
  (Person)  -[:FOUNDED]->       (Company)
  (Person)  -[:CEO_OF]->        (Company)
  (Company) -[:MAKES]->         (Product)
  (Company) -[:ACQUIRED]->      (Company)
  (Product) -[:COMPETES_WITH]-> (Product)

Sample node values:
  Companies : Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla, SpaceX
  People    : Steve Jobs, Steve Wozniak, Bill Gates, Jeff Bezos, Mark Zuckerberg,
              Elon Musk, Sundar Pichai, Sam Altman, Jensen Huang, Dario Amodei
  Products  : iPhone, MacBook, iPad, Apple Watch, Xcode, Android, Google Search,
              Gmail, Google Cloud, Gemini, Windows, Azure, VS Code, GitHub,
              Copilot, AWS, Alexa, Facebook, Instagram, WhatsApp, ChatGPT, Claude,
              H100, Tesla Model S, Autopilot
"""

# ── LLM Call 1 — translate question to Cypher ────────────────────────────
#
# We give the LLM the schema and ask it to return ONLY a Cypher query.
# The system prompt is the instruction, the user message is the question.
#
CYPHER_SYSTEM = f"""You are a Cypher expert for Neo4j 5.
Translate the user's question into a valid Cypher READ query.

Rules:
- Return ONLY the Cypher — no explanation, no markdown fences, no comments.
- Use MATCH, OPTIONAL MATCH, WHERE, RETURN, ORDER BY, LIMIT only.
- Never use CREATE, MERGE, DELETE, or SET.
- Limit results to 20 rows unless the question asks for all.

Graph schema:
{GRAPH_SCHEMA}"""


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


# ── Run the Cypher query ──────────────────────────────────────────────────

def run_cypher(cypher: str) -> list[dict]:
    with neo4j_driver.session() as session:
        return [dict(r) for r in session.run(cypher)]


# ── LLM Call 2 — turn results into plain English ─────────────────────────
#
# We give the LLM the original question and the raw graph results.
# It formats them into a readable answer.
# It is told to ONLY use the provided data — no guessing.
#
ANSWER_SYSTEM = """You are a helpful assistant answering questions about the tech industry.
You are given a question and structured data retrieved from a knowledge graph.
Answer conversationally in 2-4 sentences using ONLY the provided data.
If the data is empty, say the graph does not have that information."""


def results_to_answer(question: str, results: list[dict]) -> str:
    data = str(results) if results else "(no results found in the graph)"
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": f"Question: {question}\n\nGraph data: {data}"}],
    )
    return response.content[0].text.strip()


# ── The full pipeline ─────────────────────────────────────────────────────

def ask(question: str):
    console.print(f"\n[bold]Question:[/bold] {question}")

    # Step 1 — LLM generates Cypher
    try:
        cypher = question_to_cypher(question)
        console.print(Panel(cypher, title="[dim]Generated Cypher (LLM Call 1)[/dim]", border_style="dim"))
    except Exception as e:
        console.print(f"[red]LLM error: {e}[/red]")
        return

    # Step 2 — Neo4j runs the Cypher
    try:
        results = run_cypher(cypher)
    except Exception as e:
        console.print(f"[red]Query error: {e}[/red]")
        console.print("[dim]The LLM generated invalid Cypher. Try rephrasing your question.[/dim]")
        return

    # Step 3 — LLM synthesises the answer
    answer = results_to_answer(question, results)
    console.print(Panel(answer, title="[green]Answer (LLM Call 2)[/green]", border_style="green"))


# ── Main loop ─────────────────────────────────────────────────────────────

def main():
    console.print("\n[bold green]Knowledge Graph Q&A[/bold green]")
    console.print("Ask anything about tech companies and products.")
    console.print("Watch the [dim]Generated Cypher[/dim] panel — the LLM writes the query for you.")
    console.print("Type [bold]quit[/bold] to exit.\n")

    # Suggested starter questions
    console.print("[dim]Try these to get started:[/dim]")
    console.print("[dim]  What products does Apple make?[/dim]")
    console.print("[dim]  Which companies make AI products?[/dim]")
    console.print("[dim]  What did Elon Musk's companies build?[/dim]")
    console.print("[dim]  Which products compete with ChatGPT?[/dim]\n")

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
