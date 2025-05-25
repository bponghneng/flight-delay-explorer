# def test_imports():
#     import pandas
#     import matplotlib
#     import argparse
#     import typer


from typer.testing import CliRunner
from flight_delay_explorer.main import app

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "hello" in result.output.lower()
