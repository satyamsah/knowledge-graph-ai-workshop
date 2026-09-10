"""
Demo — RAG vs GraphRAG
======================
This demo runs BEFORE we build anything.
It shows the same question answered two ways:

  1. Plain LLM  — answers from memory, no data source
  2. GraphRAG   — answers from the knowledge graph we built

Run:  python demos/rag_vs_graph.py

Watch the difference. That difference is what we spend today fixing.
"""

import os
import re
import time
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import anthropic
from neo4j import GraphDatabase
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

load_dotenv()
console = Console()

llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── The questions we'll compare ───────────────────────────────────────────
#
# These are RELATIONSHIP questions — the kind RAG handles poorly.
# A plain LLM will answer from memory (possibly wrong).
# A graph will answer from structured data we control.
#
QUESTIONS = [
    "Which companies make products that compete with AWS?",
    "What products did companies founded by Elon Musk make?",
    "Which companies make both a cloud product and an AI product?",
]

# ── Graph schema for LLM Call 1 ───────────────────────────────────────────

GRAPH_SCHEMA = """
Nodes: Company {name, founded, hq}
       Product {name, category, launched}
       Person  {name}

Relationships:
  (Person)  -[:FOUNDED]->       (Company)
  (Person)  -[:CEO_OF]->        (Company)
  (Company) -[:MAKES]->         (Product)
  (Company) -[:ACQUIRED]->      (Company)
  (Product) -[:COMPETES_WITH]-> (Product)

Companies : Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla, SpaceX
People    : Steve Jobs, Steve Wozniak, Bill Gates, Jeff Bezos, Mark Zuckerberg,
            Elon Musk, Sundar Pichai, Sam Altman, Jensen Huang, Dario Amodei
Products  : iPhone, MacBook, Android, Google Cloud, Gemini, Windows, Azure,
            VS Code, GitHub, Copilot, AWS, ChatGPT, Claude, H100
"""

CYPHER_SYSTEM = f"""You are a Cypher expert for Neo4j 5.
Translate the question into a valid Cypher READ query.
Return ONLY the Cypher — no markdown, no explanation.
{GRAPH_SCHEMA}"""

PLAIN_LLM_SYSTEM = """You are a helpful assistant who knows about the tech industry.
Answer the question from your general knowledge in 2-3 sentences.
Be honest if you are not certain."""

ANSWER_SYSTEM = """You are a helpful assistant.
Answer the question using ONLY the structured data provided from a knowledge graph.
Be concise — 2-3 sentences. Never make up facts not in the data."""


# ── Helpers ───────────────────────────────────────────────────────────────

def plain_llm_answer(question: str) -> str:
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=PLAIN_LLM_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


def to_cypher(question: str) -> str:
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=CYPHER_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:cypher)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def run_cypher(cypher: str) -> tuple[list[dict], str | None]:
    try:
        with neo4j_driver.session() as session:
            return [dict(r) for r in session.run(cypher)], None
    except Exception as e:
        return [], str(e)


def graph_answer(question: str, results: list[dict]) -> str:
    data = str(results) if results else "(no results found)"
    response = llm.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": f"Question: {question}\n\nData: {data}"}],
    )
    return response.content[0].text.strip()


# ── Main demo ─────────────────────────────────────────────────────────────

def run_comparison(question: str):
    console.print(Rule(f"[bold white]{question}[/bold white]"))

    # ── Left side: Plain LLM ──────────────────────────────────────────────
    console.print("\n[bold red]❌  Plain LLM — answering from memory[/bold red]")
    console.print("[dim]No data source. Just pattern-matching from training data.[/dim]\n")

    with console.status("Thinking..."):
        llm_answer = plain_llm_answer(question)

    console.print(Panel(
        llm_answer,
        title="[red]Plain LLM Answer[/red]",
        border_style="red",
    ))
    console.print("[dim]Notice: no source, no structure, could be outdated or wrong.[/dim]")

    time.sleep(1)

    # ── Right side: GraphRAG ──────────────────────────────────────────────
    console.print("\n[bold green]✅  GraphRAG — answering from the knowledge graph[/bold green]")
    console.print("[dim]Step 1: LLM translates question to Cypher.[/dim]")
    console.print("[dim]Step 2: Neo4j runs the query against real data.[/dim]")
    console.print("[dim]Step 3: LLM formats the results into an answer.[/dim]\n")

    with console.status("Generating Cypher..."):
        cypher = to_cypher(question)

    console.print(Panel(
        cypher,
        title="[dim]Generated Cypher (Step 1)[/dim]",
        border_style="dim",
    ))

    with console.status("Running query..."):
        results, err = run_cypher(cypher)

    if err:
        console.print(f"[red]Query error: {err}[/red]")
        return

    if results:
        cols = list(results[0].keys())
        table = Table(*cols, show_header=True, header_style="bold green")
        for r in results:
            table.add_row(*[str(r[c]) for c in cols])
        console.print(table)
    else:
        console.print("[dim](empty result — question may need rephrasing)[/dim]")

    with console.status("Synthesising answer..."):
        answer = graph_answer(question, results)

    console.print(Panel(
        answer,
        title="[green]GraphRAG Answer (Step 3)[/green]",
        border_style="green",
    ))
    console.print("[dim]Source: your knowledge graph. Structured. Explainable. Yours to control.[/dim]\n")


def main():
    console.print()
    console.print(Panel(
        "[bold]RAG vs GraphRAG — Live Comparison[/bold]\n\n"
        "We'll ask the same question two ways:\n"
        "  [red]❌ Plain LLM[/red]  — answers from memory, no data source\n"
        "  [green]✅ GraphRAG[/green]  — answers from the knowledge graph we built\n\n"
        "Watch the difference. That difference is what we spent today building.",
        border_style="white",
    ))

    for i, question in enumerate(QUESTIONS, 1):
        console.print(f"\n[bold]Question {i} of {len(QUESTIONS)}[/bold]")
        run_comparison(question)
        if i < len(QUESTIONS):
            input("  [Press Enter for next question]\n")

    console.print(Rule("[bold green]End of Demo[/bold green]"))
    console.print("\n[bold]The key insight:[/bold]")
    console.print("  Plain LLM  → fast, but guesses. No source. Hard to trust.")
    console.print("  GraphRAG   → grounded in data you control. Explainable. Updatable.")
    console.print("\n[dim]Now you know why we built the graph. Everything else today was to get here.[/dim]\n")

    neo4j_driver.close()


if __name__ == "__main__":
    main()
