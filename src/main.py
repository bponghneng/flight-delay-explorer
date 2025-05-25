import pandas as pd
import matplotlib.pyplot as plt
import typer

app = typer.Typer(help="Example CLI using pandas and matplotlib")

@app.command()
def explore(csv: str = typer.Option(..., help="Path to a CSV file")):
    """
    Load a CSV file, print its head, and plot histograms of its columns.
    """
    df = pd.read_csv(csv)
    typer.echo("DataFrame head:")
    typer.echo(df.head())

    df.hist()
    plt.suptitle("Histograms")
    plt.show()

def main():
    app()

if __name__ == "__main__":
    main()
