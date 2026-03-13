from __future__ import annotations

from pathlib import Path

from talentgraph.ontology.models import Company


def load_company(path: Path | str) -> Company:
    """Load a Company from a JSON file."""
    path = Path(path)
    return Company.model_validate_json(path.read_text(encoding="utf-8"))


def save_company(company: Company, path: Path | str) -> None:
    """Save a Company to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(company.model_dump_json(indent=2), encoding="utf-8")
