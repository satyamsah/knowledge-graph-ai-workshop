"""
GraphRAG assistant — complete end-to-end project.

The full pipeline in one file:
  seed data → ask questions → get answers from the graph via LLM

Usage:
  python project/src/assistant.py
"""

import os
import warnings
warnings.filterwarnings("ignore")
import re
import sys
from dotenv import load_dotenv
import anthropic
from neo4j import GraphDatabase
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()
console = Console()

# ── Clients ───────────────────────────────────────────────────────────────

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)
llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Schema ────────────────────────────────────────────────────────────────

GRAPH_SCHEMA = """
Node labels and key properties:
  Company  { name, founded (year int), hq (city string) }
  Product  { name, category (one of: "AI", "cloud", "smartphone", "laptop",
             "tablet", "wearable", "mobile OS", "desktop OS", "dev tool",
             "dev platform", "email", "web service", "social media",
             "messaging", "AI assistant", "GPU", "EV"), launched (year int) }
  Person   { name }

Relationship types (always use this exact direction):
  (Person)  -[:FOUNDED]->       (Company)
  (Person)  -[:CEO_OF]->        (Company)
  (Company) -[:MAKES]->         (Product)
  (Company) -[:ACQUIRED]->      (Company or Product node)
  (Product) -[:COMPETES_WITH]-> (Product)

Sample values — Companies: Apple, Google, Microsoft, Amazon, Meta, OpenAI,
Anthropic, Nvidia, Tesla, SpaceX
Sample values — People: Steve Jobs, Steve Wozniak, Bill Gates, Jeff Bezos,
Mark Zuckerberg, Elon Musk, Sundar Pichai, Sam Altman, Jensen Huang, Dario Amodei
Sample values — Products: iPhone, MacBook, iPad, Apple Watch, Xcode,
Android, Google Search, Gmail, Google Cloud, Gemini, Windows, Azure, VS Code,
GitHub, Copilot, AWS, Alexa, Facebook, Instagram, WhatsApp, ChatGPT, Claude,
H100, Tesla Model S, Autopilot
"""

CYPHER_SYSTEM = f"""You are a Cypher expert for Neo4j 5.
Translate the user's natural language question into a valid Cypher READ query.
Rules:
- Return ONLY the Cypher — no markdown fences, no explanation, no comments.
- Use MATCH, OPTIONAL MATCH, WHERE, RETURN, ORDER BY, LIMIT only.
- Never use CREATE, MERGE, DELETE, SET.
- Use case-insensitive matching with toLower() when filtering string properties.
- Limit results to 20 rows unless the question asks for all.

Graph schema:
{GRAPH_SCHEMA}"""

ANSWER_SYSTEM = """You are a knowledgeable tech industry analyst.
Answer the user's question using ONLY the structured data provided from a knowledge graph.
- Be conversational but precise.
- Use 2-5 sentences.
- If data is empty or null, say the knowledge graph doesn't have that information
  and suggest what kind of data would be needed.
- Never make up facts not present in the data."""

# ── Core pipeline ─────────────────────────────────────────────────────────

def to_cypher(question: str) -> str:
    msg = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=CYPHER_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```(?:cypher)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def run_query(cypher: str) -> tuple[list[dict], str | None]:
    try:
        with neo4j_driver.session() as session:
            return [dict(r) for r in session.run(cypher)], None
    except Exception as e:
        return [], str(e)


def synthesise(question: str, results: list[dict]) -> str:
    data = str(results) if results else "(empty — no matching data in graph)"
    msg = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=ANSWER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Question: {question}\n\nKnowledge graph results: {data}",
        }],
    )
    return msg.content[0].text.strip()


def ask(question: str, verbose: bool = True):
    if verbose:
        console.print(f"\n[bold]Q:[/bold] {question}")

    cypher = to_cypher(question)

    if verbose:
        console.print(Panel(cypher, title="[dim]Cypher[/dim]", border_style="dim"))

    results, err = run_query(cypher)

    if err:
        console.print(f"[red]Query failed:[/red] {err}")
        console.print("[dim]Tip: rephrase your question and try again.[/dim]")
        return

    answer = synthesise(question, results)
    console.print(Panel(answer, title="[green bold]Answer[/green bold]", border_style="green"))
    return answer

# ── Demo questions ────────────────────────────────────────────────────────

DEMO_QUESTIONS = [
    "What products does Apple make, and when were they launched?",
    "Which companies make AI products?",
    "What products compete with ChatGPT?",
    "Which companies has Elon Musk founded, and what do they make?",
    "Which company makes the most products? Show me the ranking.",
    "What cloud products exist and who makes them?",
    "Which products compete with AWS?",
    "Who are the CEOs of AI companies?",
]

# ── CLI ───────────────────────────────────────────────────────────────────

def demo_mode():
    console.print("\n[bold cyan]Running demo questions...[/bold cyan]")
    for q in DEMO_QUESTIONS:
        ask(q)
        input("\n[Press Enter for next question]")


def interactive_mode():
    console.print(Panel(
        "[bold green]Knowledge Graph Q&A Assistant[/bold green]\n\n"
        "Ask anything about tech companies, products, and people.\n"
        "Type [bold]demo[/bold] to run sample questions, [bold]quit[/bold] to exit.",
        border_style="green",
    ))

    while True:
        try:
            question = input("\nAsk the graph > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        if question.lower() == "demo":
            demo_mode()
            continue

        ask(question)

    console.print("\n[dim]Session ended.[/dim]")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "interactive"
    if mode == "demo":
        demo_mode()
    else:
        interactive_mode()
    neo4j_driver.close()
