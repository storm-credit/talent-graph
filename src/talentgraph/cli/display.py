from __future__ import annotations

from rich.console import Console
from rich.table import Table

from talentgraph.ontology.models import Person
from talentgraph.scoring.engine import FitResult

console = Console()


def render_results(
    results: list[FitResult], person: Person, explain: bool = False
) -> None:
    """Render FitResults as a Rich table."""
    console.print()
    console.print(
        f"[bold]TalentGraph v0.1.0 - Evaluation: {person.name}[/bold]",
        style="cyan",
    )
    console.print(
        f"Tenure: {person.tenure_years}yr | Skills: {len(person.skills)}",
        style="dim",
    )
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Rank", justify="right", width=4)
    table.add_column("Department", min_width=20)
    table.add_column("Role", min_width=22)
    table.add_column("Fit", justify="right", width=6)
    table.add_column("Predicted Perf", justify="right", width=14)

    for i, r in enumerate(results, 1):
        fit_color = "green" if r.fit_score >= 0.7 else "yellow" if r.fit_score >= 0.4 else "red"
        table.add_row(
            str(i),
            r.department_name,
            r.role_title,
            f"[{fit_color}]{r.fit_score:.2f}[/{fit_color}]",
            f"{r.predicted_performance:.1f} / 5.0",
        )

    console.print(table)

    if explain and results:
        console.print()
        _render_breakdown(results[0])


def _render_breakdown(result: FitResult) -> None:
    """Render detailed score breakdown for a single result."""
    console.print(
        f"[bold]Score Breakdown: {result.role_title} @ {result.department_name}[/bold]"
    )
    console.print()

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("Factor", min_width=18)
    table.add_column("Raw Score", justify="right", width=10)
    table.add_column("Weighted", justify="right", width=10)

    factors = [
        ("Skill Match", result.skill_match_score, result.breakdown["skill_match"]),
        ("Historical Perf", result.historical_score, result.breakdown["historical"]),
        ("Level Match", result.level_match_score, result.breakdown["level_match"]),
        ("Burnout Risk", result.burnout_risk_score, result.breakdown["burnout_penalty"]),
    ]

    for name, raw, weighted in factors:
        sign = "+" if weighted >= 0 else ""
        console.print
        table.add_row(name, f"{raw:.3f}", f"{sign}{weighted:.4f}")

    console.print(table)
    console.print(f"\n[bold]Final Fit Score: {result.fit_score:.4f}[/bold]")
    console.print(f"[bold]Predicted Performance: {result.predicted_performance:.1f} / 5.0[/bold]")


def render_results_json(results: list[FitResult]) -> str:
    """Render results as JSON string."""
    import json

    return json.dumps([r.model_dump(mode="json") for r in results], indent=2)
