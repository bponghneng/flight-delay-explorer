import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description="Example CLI using pandas and matplotlib")
    parser.add_argument("--csv", type=str, help="Path to a CSV file", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    print("DataFrame head:")
    print(df.head())

    df.hist()
    plt.suptitle("Histograms")
    plt.show()


if __name__ == "__main__":
    main()
