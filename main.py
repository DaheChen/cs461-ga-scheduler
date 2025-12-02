from data import ACTIVITIES, ROOMS, TIMES
from schedule_repr import print_schedule, Schedule
from fitness import compute_schedule_fitness
from ga_core import run_ga
import csv


def main():
    print("=== SLA Genetic Scheduler ===")
    print("This is a placeholder main function for CS 461 Program 2.\n")

    # --- Data summary ---
    print("Data summary:")
    print(f"- Activities: {len(ACTIVITIES)}")
    print(f"- Rooms:      {len(ROOMS)}")
    print(f"- Time slots: {len(TIMES)}")
    sample_activities = list(ACTIVITIES.keys())[:5]
    print(f"- Sample activities: {sample_activities}\n")

    # --- Sample schedule just for testing printing & fitness ---
    sample_schedule: Schedule = {
        "SLA101A": {"room": "Frank 119", "time": "10 AM", "facilitator": "Glen"},
        "SLA101B": {"room": "Roman 201", "time": "11 AM", "facilitator": "Banks"},
        "SLA191A": {"room": "Beach 301", "time": "10 AM", "facilitator": "Lock"},
        "SLA191B": {"room": "Slater 003", "time": "2 PM", "facilitator": "Singer"},
        "SLA201": {"room": "Loft 206", "time": "3 PM", "facilitator": "Tyler"},
        "SLA291": {"room": "James 325", "time": "1 PM", "facilitator": "Zeldin"},
        "SLA303": {"room": "Beach 201", "time": "12 PM", "facilitator": "Glen"},
        "SLA304": {"room": "Loft 310", "time": "11 AM", "facilitator": "Uther"},
        "SLA394": {"room": "Roman 216", "time": "2 PM", "facilitator": "Tyler"},
        "SLA449": {"room": "Frank 119", "time": "1 PM", "facilitator": "Singer"},
        "SLA451": {"room": "James 325", "time": "10 AM", "facilitator": "Banks"},
    }

    print("\nSample schedule (ordered by time, first 6 activities):")
    print_schedule(sample_schedule, order_by="time", max_activities=6)

    # --- Compute fitness for the sample schedule (for testing) ---
    sample_fitness = compute_schedule_fitness(sample_schedule)
    print(f"\nFitness of sample schedule: {sample_fitness:.3f}")

    # --- Run the genetic algorithm on a population (debug-sized) ---
    print("\n=== Running genetic algorithm ===")
    best_schedule, best_fitness, history = run_ga(
        population_size=80,    # smaller for quick debugging
        mutation_rate=0.05,    # slightly higher for diversity
        min_generations=20,    # fewer generations for quick run
        max_generations=40,    # hard cap
        rng_seed=42,
    )

    print(f"\nGA finished after {len(history)} generations.")
    print(f"Best fitness in final generation: {best_fitness:.3f}")

    print("\nBest schedule (first 6 activities, ordered by time):")
    print_schedule(best_schedule, order_by="time", max_activities=6)

    print("\nLast 5 generations (best / avg / worst / improvement%):")
    for entry in history[-5:]:
        print(
            f"Gen {entry['generation']:3d} | "
            f"best={entry['best_fitness']:.3f}, "
            f"avg={entry['avg_fitness']:.3f}, "
            f"worst={entry['worst_fitness']:.3f}, "
            f"improv={entry['improvement_percent']:.2f}%"
        )
    # --- Export fitness history to CSV for further analysis ---
    with open("fitness_history.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(
            ["generation", "best_fitness", "avg_fitness", "worst_fitness", "improvement_percent", "mutation_rate"]
        )
        # Rows
        for entry in history:
            writer.writerow(
                [
                    entry["generation"],
                    entry["best_fitness"],
                    entry["avg_fitness"],
                    entry["worst_fitness"],
                    entry["improvement_percent"],
                    entry["mutation_rate"],
                ]
            )

    print('\nFitness history exported to "fitness_history.csv".')


if __name__ == "__main__":
    main()
