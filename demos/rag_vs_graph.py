"""
Demo — Plain LLM vs RAG vs GraphRAG
=====================================
This demo shows the SAME question answered three ways:

  1. Plain LLM   — answers from memory, no data source
  2. RAG          — retrieves text chunks, but misses relationships
  3. GraphRAG     — queries structured graph facts, precise and explainable

Run:  python demos/rag_vs_graph.py

Watch how the quality improves at each step — and WHY.
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
from rich.columns import Columns

load_dotenv()
console = Console()

llm = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
)

# ── Simulated document corpus for RAG ────────────────────────────────────
#
# Key design decision: cloud and AI facts for the same company are
# intentionally split across SEPARATE documents.
# This mirrors real-world RAG — information about one entity is scattered
# across many documents. RAG retrieves top-k chunks independently and
# cannot JOIN facts across chunks for the same entity.
# The graph answers this trivially because relationships are explicit.
#
DOCUMENTS = [
    "Microsoft Azure is one of the leading cloud computing platforms used by enterprises worldwide.",

    "Microsoft Copilot is an AI assistant integrated into Office 365 and Windows products.",

    "Google Cloud Platform provides infrastructure and data services to thousands of businesses.",

    "Google Gemini is a large language model developed by Google DeepMind for AI applications.",

    "Amazon Web Services (AWS) is the market leader in cloud computing, offering EC2, S3, and Lambda.",

    "Microsoft offers many products including Windows, Azure, GitHub, VS Code, and Copilot. "
    "Copilot is an AI assistant integrated into Microsoft products.",

    "Elon Musk co-founded Tesla in 2003 and SpaceX in 2002. "
    "Tesla makes electric vehicles including Model S and Model 3. "
    "SpaceX develops rockets and spacecraft.",

    "Tesla's Autopilot is an AI-powered driver assistance system. "
    "It uses cameras and sensors to enable semi-autonomous driving.",

    "OpenAI was founded in 2015 by Sam Altman, Elon Musk, and others. "
    "ChatGPT is OpenAI's flagship AI product launched in 2022.",

    "Google's AI products include Gemini, a large language model that competes with ChatGPT. "
    "Google also makes Android, the mobile operating system.",

    "Apple makes the iPhone, MacBook, iPad, and Apple Watch. "
    "The iPhone competes with Android smartphones.",

    "GitHub is a code hosting platform owned by Microsoft since 2018. "
    "VS Code is a popular code editor also made by Microsoft.",
]


def simulate_rag_retrieval(question: str, top_k: int = 3) -> list[str]:
    """
    Simulate RAG retrieval using simple keyword matching.
    Real RAG uses vector embeddings — same idea, more sophisticated.
    The key point: it returns TEXT CHUNKS, not structured facts.
    """
    question_words = set(question.lower().split())
    scored = []
    for doc in DOCUMENTS:
        doc_words = set(doc.lower().split())
        score = len(question_words & doc_words)
        scored.append((score, doc))
    scored.sort(reverse=True)
    return [doc for _, doc in scored[:top_k]]


# ── LLM system prompts ────────────────────────────────────────────────────

PLAIN_LLM_SYSTEM = """You are a helpful assistant who knows about the tech industry.
Answer the question from your general knowledge in 2-3 sentences.
Be direct and specific."""

RAG_SYSTEM = """You are a helpful assistant.
Answer the question using ONLY the text passages provided below.
If the passages don't contain enough information to answer precisely, say so.
Do not add information not present in the passages."""

CYPHER_SYSTEM = """You are a Cypher expert for Neo4j 5.
Translate the question into a valid Cypher READ query.
Return ONLY the Cypher — no markdown fences, no explanation.

Graph schema:
  Nodes: Company {name, founded, hq}
         Product {name, category, launched}
         Person  {name}

  Relationships:
    (Person)  -[:FOUNDED]->      (Company)
    (Person)  -[:CEO_OF]->       (Company)
    (Company) -[:MAKES]->        (Product)
    (Company) -[:ACQUIRED]->     (Company)
    (Product) -[:COMPETES_WITH]- (Product)

  IMPORTANT — COMPETES_WITH is stored one-way but is symmetric.
  Always match it WITHOUT a direction arrow: -[:COMPETES_WITH]-
  To find what competes with AWS:
    MATCH (aws:Product {name:'AWS'})-[:COMPETES_WITH]-(competitor:Product)
    RETURN competitor.name
  To find companies that make competitors of AWS:
    MATCH (aws:Product {name:'AWS'})-[:COMPETES_WITH]-(competitor:Product)<-[:MAKES]-(c:Company)
    RETURN DISTINCT c.name

  Sample data:
    Companies : Apple, Google, Microsoft, Amazon, Meta, OpenAI, Anthropic, Nvidia, Tesla, SpaceX
    People    : Steve Jobs, Steve Wozniak, Bill Gates, Jeff Bezos, Mark Zuckerberg,
                Elon Musk, Sundar Pichai, Sam Altman, Jensen Huang, Dario Amodei
    Products  : iPhone, MacBook, iPad, Android, Google Cloud, Gemini, Windows, Azure,
                VS Code, GitHub, Copilot, AWS, ChatGPT, Claude, H100, Tesla Model S, Autopilot
"""

ANSWER_SYSTEM = """You are a helpful assistant.
Answer the question using ONLY the structured data provided from a knowledge graph.
Be concise — 2-3 sentences. Never add facts not present in the data."""


# ── Core functions ────────────────────────────────────────────────────────

def plain_llm_answer(question: str) -> str:
    r = llm.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200,
        system=PLAIN_LLM_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return r.content[0].text.strip()


def rag_answer(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(f"Passage {i+1}: {c}" for i, c in enumerate(chunks))
    r = llm.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200,
        system=RAG_SYSTEM,
        messages=[{"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"}],
    )
    return r.content[0].text.strip()


def to_cypher(question: str) -> str:
    r = llm.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        system=CYPHER_SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    raw = r.content[0].text.strip()
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
    r = llm.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200,
        system=ANSWER_SYSTEM,
        messages=[{"role": "user", "content": f"Question: {question}\n\nData: {data}"}],
    )
    return r.content[0].text.strip()


# ── The three-way comparison ──────────────────────────────────────────────

def run_comparison(question: str):
    console.print(Rule(f"[bold white]{question}[/bold white]"))

    # ── 1. Plain LLM ─────────────────────────────────────────────────────
    console.print("\n[bold red]1️⃣   Plain LLM — no data source[/bold red]")
    console.print("[dim]The LLM answers purely from its training memory.[/dim]\n")

    with console.status("Asking LLM..."):
        answer1 = plain_llm_answer(question)

    console.print(Panel(answer1, title="[red]Plain LLM[/red]", border_style="red"))
    console.print("[dim]⚠  Could be wrong. No source. No structure. Can't be verified.[/dim]\n")
    time.sleep(0.5)
    input("  [Press Enter to see RAG]\n")

    # ── 2. RAG ───────────────────────────────────────────────────────────
    console.print("[bold yellow]2️⃣   RAG — retrieves text chunks[/bold yellow]")
    console.print("[dim]Finds the most relevant text passages, passes them to the LLM.[/dim]\n")

    chunks = simulate_rag_retrieval(question)

    console.print("[dim]Retrieved chunks:[/dim]")
    for i, chunk in enumerate(chunks, 1):
        console.print(Panel(
            chunk,
            title=f"[dim]Chunk {i}[/dim]",
            border_style="yellow",
        ))

    with console.status("Asking LLM with context..."):
        answer2 = rag_answer(question, chunks)

    console.print(Panel(answer2, title="[yellow]RAG Answer[/yellow]", border_style="yellow"))
    console.print(
        "[dim]⚠  Better than nothing — but notice the chunks are text fragments.\n"
        "   RAG has no idea which company makes which competing product.\n"
        "   It can only guess from what's written in the passages.[/dim]\n"
    )
    time.sleep(0.5)
    input("  [Press Enter to see GraphRAG]\n")

    # ── 3. GraphRAG ──────────────────────────────────────────────────────
    console.print("[bold green]3️⃣   GraphRAG — queries structured graph facts[/bold green]")
    console.print("[dim]LLM writes a Cypher query → Neo4j returns exact facts → LLM formats answer.[/dim]\n")

    with console.status("Generating Cypher..."):
        cypher = to_cypher(question)

    console.print(Panel(cypher, title="[dim]Generated Cypher[/dim]", border_style="dim"))

    with console.status("Running query..."):
        results, err = run_cypher(cypher)

    if err:
        console.print(f"[red]Query error: {err}[/red]")
    elif results:
        cols = list(results[0].keys())
        table = Table(*cols, show_header=True, header_style="bold green")
        for r in results:
            table.add_row(*[str(r[c]) for c in cols])
        console.print(table)
    else:
        console.print("[dim](empty — query returned no results)[/dim]")

    with console.status("Synthesising answer..."):
        answer3 = graph_answer(question, results)

    console.print(Panel(answer3, title="[green]GraphRAG Answer[/green]", border_style="green"))
    console.print(
        "[dim]✓  Precise. Structured. Sourced from data YOU control.\n"
        "   Every fact is traceable back to a node or relationship in the graph.[/dim]\n"
    )


def main():
    console.print()
    console.print(Panel(
        "[bold]Plain LLM  vs  RAG  vs  GraphRAG[/bold]\n\n"
        "Same question. Three approaches. Watch the quality improve — and understand why.\n\n"
        "  [red]1️⃣  Plain LLM[/red]   — answers from memory. Fast but unreliable.\n"
        "  [yellow]2️⃣  RAG[/yellow]          — retrieves text chunks. Better, but can't follow relationships.\n"
        "  [green]3️⃣  GraphRAG[/green]     — queries a knowledge graph. Precise and explainable.",
        border_style="white",
    ))

    QUESTIONS = [
        "Which companies make products that compete with AWS?",
        "What products did companies founded by Elon Musk make?",
        # This is the killer question — RAG retrieves relevant chunks but
        # cannot JOIN two separate facts (cloud product + AI product) for
        # the same company. The graph does it in one query.
        "Which companies make both a cloud product and an AI product?",
    ]

    for i, question in enumerate(QUESTIONS, 1):
        console.print(f"\n[bold]Question {i} of {len(QUESTIONS)}[/bold]")
        run_comparison(question)
        if i < len(QUESTIONS):
            input("  [Press Enter for next question]\n")

    console.print(Rule("[bold green]Summary[/bold green]"))
    console.print()
    table = Table(show_header=True, header_style="bold")
    table.add_column("Approach",   style="bold")
    table.add_column("Data source")
    table.add_column("Handles relationships?")
    table.add_column("Trustworthy?")
    table.add_row("Plain LLM",  "Training memory",   "❌ No",  "❌ No source")
    table.add_row("RAG",        "Text chunks",        "⚠  Weak", "⚠  Hard to verify")
    table.add_row("GraphRAG",   "Knowledge graph",    "✅ Yes", "✅ Traceable facts")
    console.print(table)
    console.print()
    console.print("[dim]This is why we spent today building the graph. Everything else was to get here.[/dim]\n")

    neo4j_driver.close()


if __name__ == "__main__":
    main()
