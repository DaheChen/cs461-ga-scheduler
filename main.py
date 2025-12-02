from data import ACTIVITIES, ROOMS, TIMES
from schedule_repr import print_schedule, Schedule
from fitness import compute_schedule_fitness

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

    # --- Construct a tiny sample schedule just for testing the representation ---
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

if __name__ == "__main__":
    main()
