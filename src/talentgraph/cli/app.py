from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from talentgraph import __version__
from talentgraph.cli.display import render_results, render_results_json
from talentgraph.data.loader import load_company, save_company
from talentgraph.data.seed import create_sample_company
from talentgraph.scoring.engine import FitScoreEngine
from talentgraph.scoring.weights import ScoringWeights

app = typer.Typer(
    name="talentgraph",
    help="TalentGraph - Ontology-driven workforce simulation engine",
    no_args_is_help=True,
)
console = Console()


@app.command()
def evaluate(
    person: str = typer.Option(..., "--person", "-p", help="Person name to evaluate"),
    data: Optional[Path] = typer.Option(None, "--data", "-d", help="Company JSON file"),
    top: int = typer.Option(3, "--top", "-n", help="Number of top results"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Show score breakdown"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table or json"),
) -> None:
    """Evaluate a person's fit across all departments and roles."""
    company = load_company(data) if data else create_sample_company()

    engine = FitScoreEngine(company)
    try:
        results = engine.evaluate_person_by_name(person)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    top_results = engine.top_n(results, top)

    if format == "json":
        console.print(render_results_json(top_results))
    else:
        person_obj = next(p for p in company.people if p.name.lower() == person.lower())
        render_results(top_results, person_obj, explain=explain)


@app.command()
def show(
    entity: str = typer.Argument(help="Entity type: people, departments, roles, skills"),
    data: Optional[Path] = typer.Option(None, "--data", "-d", help="Company JSON file"),
) -> None:
    """Display ontology objects."""
    company = load_company(data) if data else create_sample_company()

    if entity == "people":
        for p in company.people:
            skills_str = ", ".join(f"{_skill_name(company, ps.skill_id)}({ps.level.value})"
                                   for ps in p.skills)
            console.print(f"  [bold]{p.name}[/bold] | {p.tenure_years}yr | {skills_str}")
    elif entity == "departments":
        for d in company.departments:
            role_names = [r.title for r in company.roles if r.id in d.roles]
            console.print(f"  [bold]{d.name}[/bold] | Roles: {', '.join(role_names)}")
    elif entity == "roles":
        for r in company.roles:
            console.print(f"  [bold]{r.title}[/bold] (L{r.level}) | "
                          f"{len(r.required_skills)} required skills")
    elif entity == "skills":
        for s in company.skills:
            console.print(f"  [bold]{s.name}[/bold] ({s.category.value})")
    else:
        console.print(f"[red]Unknown entity: {entity}. Use: people, departments, roles, skills[/red]")
        raise typer.Exit(1)


@app.command()
def seed(
    output: Path = typer.Option("company.json", "--output", "-o", help="Output JSON path"),
) -> None:
    """Generate sample company data."""
    company = create_sample_company()
    save_company(company, output)
    console.print(f"[green]Sample data saved to {output}[/green]")


@app.command()
def version() -> None:
    """Show version info."""
    console.print(f"TalentGraph v{__version__}")


def _skill_name(company, skill_id):
    for s in company.skills:
        if s.id == skill_id:
            return s.name
    return "?"


if __name__ == "__main__":
    app()
