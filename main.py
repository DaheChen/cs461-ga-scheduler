from data import ACTIVITIES, ROOMS, TIMES
from schedule_repr import print_schedule, Schedule
from fitness import compute_schedule_fitness
from ga_core import run_ga
import csv


def export_fitness_history(history, filename: str = "fitness_history.csv") -> None:
    """Export per-generation fitness statistics to a CSV file."""
    with open(filename, "w", newline="") as f:
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


def save_schedule(schedule: Schedule, filename: str = "best_schedule_by_time.txt") -> None:
    """
    Save the best schedule to a text file, ordered by time.

    This is useful for documentation and for including in the video/report.
    """
    # Redirect the printed schedule into a file by temporarily using print_schedule.
    # For simplicity, we rebuild the sorted view here.

    # Build a list of rows (activity, time, room, facilitator, enrollment)
    rows = []
    for activity, info in schedule.items():
        rows.append(
            (
                activity,
                info["time"],
                info["room"],
                info["facilitator"],
                # We can look up enrollment from ACTIVITIES if needed
                ACTIVITIES[activity]["enrollment"],
            )
        )

    # Sort by time, then by activity name
    rows.sort(key=lambda x: (TIMES.index(x[1]), x[0]))

    with open(filename, "w") as f:
        f.write("Best schedule (ordered by time):\n")
        f.write(f"{'Activity':<10}  {'Time':<5}  {'Room':<10}  {'Facilitator':<10}  {'Enroll':>6}\n")
        f.write(f"{'-'*10}  {'-'*5}  {'-'*10}  {'-'*10}  {'-'*6}\n")
        for activity, time, room, facilitator, enroll in rows:
            f.write(
                f"{activity:<10}  {time:<5}  {room:<10}  {facilitator:<10}  {enroll:6d}\n"
            )


def main():
    print("=== SLA Genetic Scheduler ===")
    print("CS 461 – Program 2: Genetic Algorithm\n")

    # ------------------------------------------------------------------
    # 1) Data summary
    # ------------------------------------------------------------------
    print("[1] Data summary")
    print(f"- Activities: {len(ACTIVITIES)}")
    print(f"- Rooms:      {len(ROOMS)}")
    print(f"- Time slots: {len(TIMES)}")
    sample_activities = list(ACTIVITIES.keys())[:5]
    print(f"- Sample activities: {sample_activities}\n")

    # ------------------------------------------------------------------
    # 2) Sample schedule and fitness (sanity check)
    # ------------------------------------------------------------------
    print("[2] Sample schedule (sanity check)")
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

    print("Sample schedule (ordered by time, first 6 activities):")
    print_schedule(sample_schedule, order_by="time", max_activities=6)

    sample_fitness = compute_schedule_fitness(sample_schedule)
    print(f"\nFitness of sample schedule: {sample_fitness:.3f}\n")

    # ------------------------------------------------------------------
    # 3) GA configuration
    # ------------------------------------------------------------------
    print("[3] Genetic Algorithm configuration")
    population_size = 300     # Required: N >= 250
    mutation_rate = 0.01      # Required: start with 0.01
    min_generations = 100     # Required: at least 100 generations
    max_generations = 500     # Allow enough room to converge
    rng_seed = 42

    print(f"- population_size = {population_size}")
    print(f"- mutation_rate   = {mutation_rate}")
    print(f"- min_generations = {min_generations}")
    print(f"- max_generations = {max_generations}")
    print(f"- rng_seed        = {rng_seed}\n")

    # ------------------------------------------------------------------
    # 4) Run GA
    # ------------------------------------------------------------------
    print("[4] Running genetic algorithm ...")
    best_schedule, best_fitness, history = run_ga(
        population_size=population_size,
        mutation_rate=mutation_rate,
        min_generations=min_generations,
        max_generations=max_generations,
        rng_seed=rng_seed,
    )

    print(f"\nGA finished after {len(history)} generations.")
    print(f"Best fitness in final generation: {best_fitness:.3f}\n")

    # ------------------------------------------------------------------
    # 5) Print best schedule (preview)
    # ------------------------------------------------------------------
    print("[5] Best schedule (preview)")
    print_schedule(best_schedule, order_by="time", max_activities=6)

    # ------------------------------------------------------------------
    # 6) Print last few generations' statistics
    # ------------------------------------------------------------------
    print("\n[6] Last 5 generations (best / avg / worst / improvement%)")
    for entry in history[-5:]:
        print(
            f"Gen {entry['generation']:3d} | "
            f"best={entry['best_fitness']:.3f}, "
            f"avg={entry['avg_fitness']:.3f}, "
            f"worst={entry['worst_fitness']:.3f}, "
            f"improv={entry['improvement_percent']:.2f}%"
        )

    # ------------------------------------------------------------------
    # 7) Export artifacts (CSV + best schedule)
    # ------------------------------------------------------------------
    export_fitness_history(history, "fitness_history.csv")
    save_schedule(best_schedule, "best_schedule_by_time.txt")

    print('\n[7] Artifacts exported:')
    print('- fitness_history.csv')
    print('- best_schedule_by_time.txt')


if __name__ == "__main__":
    main()
