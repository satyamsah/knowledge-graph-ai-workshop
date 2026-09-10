"""
Setup verification script.
Run before the workshop:  python check_setup.py
"""

import os
import warnings
warnings.filterwarnings("ignore")
import sys
from dotenv import load_dotenv

load_dotenv()


def check_neo4j():
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "workshop123")),
        )
        with driver.session() as s:
            s.run("RETURN 1")
        driver.close()
        return True, None
    except Exception as e:
        return False, str(e)


def check_anthropic():
    try:
        import anthropic
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key or "your-key" in key:
            return False, "ANTHROPIC_API_KEY not set — edit .env and add your key"
        client = anthropic.Anthropic(api_key=key)
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            messages=[{"role": "user", "content": "hi"}],
        )
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print("\n[bold]Knowledge Graph AI Workshop — Setup Check[/bold]\n")

    checks = [
        ("Neo4j connected (localhost:7687)",  check_neo4j()),
        ("Anthropic API reachable",           check_anthropic()),
    ]

    table = Table(show_header=False, box=None, padding=(0, 2))
    all_ok = True
    for label, (ok, err) in checks:
        if ok:
            table.add_row("[green]✓[/green]", label)
        else:
            table.add_row("[red]✗[/red]", f"[red]{label}[/red]")
            table.add_row("",             f"[dim]  → {err}[/dim]")
            all_ok = False

    console.print(table)

    if all_ok:
        console.print("\n[green bold]✓ You're all set — see you at the workshop![/green bold]\n")
    else:
        console.print("\n[red bold]Fix the issues above before the session starts.[/red bold]")
        console.print("[dim]Neo4j not running?  →  docker compose up -d[/dim]")
        console.print("[dim]API key missing?    →  copy .env.example to .env and add your key[/dim]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
