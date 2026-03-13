import json

from typer.testing import CliRunner

from talentgraph.cli.app import app

runner = CliRunner()


def test_evaluate_alice():
    result = runner.invoke(app, ["evaluate", "--person", "Alice Chen"])
    assert result.exit_code == 0
    assert "Data Engineering" in result.output


def test_evaluate_json_format():
    result = runner.invoke(app, ["evaluate", "--person", "Alice Chen", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 3


def test_evaluate_nonexistent():
    result = runner.invoke(app, ["evaluate", "--person", "Nobody"])
    assert result.exit_code == 1


def test_show_people():
    result = runner.invoke(app, ["show", "people"])
    assert result.exit_code == 0
    assert "Alice Chen" in result.output


def test_show_departments():
    result = runner.invoke(app, ["show", "departments"])
    assert result.exit_code == 0
    assert "Data Engineering" in result.output


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
