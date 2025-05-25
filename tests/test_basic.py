# def test_imports():
#     import pandas
#     import matplotlib
#     import argparse
#     import typer


def test_hello():
    from flight_delay_explorer.main import main

    result = main()
    assert isinstance(result, str)
    assert "hello" in result.lower()
