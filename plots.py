"""
plots.py

Read fitness_history.csv and plot best / average / worst
fitness over generations. Save the figure as fitness_curves.png.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_fitness_history(csv_path: str = "fitness_history.csv"):
    """
    Load GA fitness history from a CSV file.

    :param csv_path: path to fitness_history.csv
    :return: dict with lists: generation, best, avg, worst
    """
    generations = []
    best = []
    avg = []
    worst = []

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with path.open("r", newline="") as f:
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


def plot_fitness_curves(history: dict, out_path: str = "fitness_curves.png"):
    """
    Plot best / average / worst fitness over generations and save as PNG.

    :param history: dict returned by load_fitness_history
    :param out_path: output image file path
    """
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
    history = load_fitness_history("fitness_history.csv")
    plot_fitness_curves(history, "fitness_curves.png")


if __name__ == "__main__":
    main()
