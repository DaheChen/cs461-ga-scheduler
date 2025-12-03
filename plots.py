"""
plots.py

Read fitness_history.csv and plot best / average / worst
fitness over generations. Save the figure as fitness_curves.png
in the same directory as this script.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


# Base directory = folder where this file (plots.py) is located
BASE_DIR = Path(__file__).resolve().parent


def load_fitness_history(csv_name: str = "fitness_history.csv"):
    """
    Load GA fitness history from a CSV file located
    in the same folder as this script.

    :param csv_name: name of the CSV file (default: fitness_history.csv)
    :return: dict with lists: generation, best, avg, worst
    """
    csv_path = BASE_DIR / csv_name

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    generations = []
    best = []
    avg = []
    worst = []

    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            generations.append(int(row["generation"]))
            best.append(float(row["best_fitness"]))
            avg.append(float(row["avg_fitness"]))
            worst.append(float(row["worst_fitness"]))

    return {
        "generation": generations,
        "best": best,
        "avg": avg,
        "worst": worst,
    }


def plot_fitness_curves(history: dict, png_name: str = "fitness_curves.png"):
    """
    Plot best / average / worst fitness over generations and
    save the figure as a PNG file in the same folder as this script.

    :param history: dict returned by load_fitness_history
    :param png_name: file name for the output image
    """
    out_path = BASE_DIR / png_name

    gens = history["generation"]
    best = history["best"]
    avg = history["avg"]
    worst = history["worst"]

    plt.figure(figsize=(8, 4))

    # one line for each metric
    plt.plot(gens, best, label="Best fitness")
    plt.plot(gens, avg, label="Average fitness")
    plt.plot(gens, worst, label="Worst fitness")

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("GA fitness over generations")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(out_path, dpi=150)
    print(f"Saved fitness curves to {out_path}")


def main():
    # fitness_history.csv must be in the same folder as plots.py
    history = load_fitness_history("fitness_history.csv")
    plot_fitness_curves(history, "fitness_curves.png")


if __name__ == "__main__":
    main()
