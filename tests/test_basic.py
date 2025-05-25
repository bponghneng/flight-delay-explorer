def test_imports():
    import pandas
    import matplotlib
    import argparse
    import typer

def test_hello():
    from src.main import hello
    result = hello()
    assert isinstance(result, str)
    assert "hello" in result.lower()
