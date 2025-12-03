# CS 461 – Program 2: Genetic Algorithm Scheduler

This project implements a genetic algorithm (GA) to build an activity schedule for the
Seminar Learning Association (SLA), based on the constraints and fitness function
described in the assignment specification.

The goal is to assign, for each activity:

- a room
- a time slot
- a facilitator

such that the overall schedule fitness is maximized under various soft and hard
constraints (room capacity, conflicts, facilitator load, SLA101/191 rules, etc.).

------------------------------------------------------------
1. Project Structure
------------------------------------------------------------

All code is organized in a single, self-contained Python project.
The main modules are:

- data.py
  - Defines all static problem data:
    - Activities and their expected enrollments
    - Preferred and secondary facilitators
    - Rooms and their capacities / equipment
    - Time slots
    - Facilitator time preferences (optional part of the fitness)

- schedule_repr.py
  - Defines the internal schedule representation:
    - A schedule is a dict[str, dict] that maps each activity ID to a dictionary
      with "room", "time", and "facilitator".
  - Provides a helper function:
    - print_schedule(schedule, order_by="time", max_activities=None)
      - Pretty-prints a schedule ordered by time or by activity.
      - Used both for debugging and for the final output.

- fitness.py
  - Implements the fitness function from Appendix A of the assignment, including:
    - Room size penalties (too small, too large, good fit)
    - Room conflicts (two activities in the same room at the same time)
    - Facilitator conflicts and load:
      - double-booking in the same time slot
      - too many / too few total activities
      - special case for Dr. Tyler
    - Activity-specific rules for SLA101 and SLA191:
      - distance between their sections in time
      - penalties for overlapping in the same time slot
      - bonuses/penalties for specific combinations (e.g. consecutive time slots)
    - Optional additional constraints (if enabled in the code):
      - Facilitator time preferences
      - Equipment requirements (lab / projector)

  - The schedule fitness is the sum of the individual activity fitness values.

- ga_core.py
  - Implements the genetic algorithm:
    - Population initialization with random schedules
    - Fitness evaluation for each schedule
    - Softmax-based selection:
      - Converts fitness values into a probability distribution using softmax.
      - Higher-fitness schedules are more likely to be selected as parents.
    - Crossover:
      - Uniform crossover by activity:
        - For each activity, the child schedule inherits the assignment from
          parent A or parent B with 50/50 probability.
    - Mutation:
      - Field-wise mutation with a fixed mutation rate (e.g. 0.05):
        - Each assignment (room, time, facilitator) has a chance to be replaced
          by a random value from the corresponding domain.
    - Stopping criterion:
      - The GA always runs at least min_generations.
      - After that, it stops when the improvement in average fitness
        between generations falls below 1% (or when max_generations is reached).
    - Returns:
      - best_schedule: the best schedule found in the last generation
      - best_fitness: its fitness value
      - history: per-generation statistics

- main.py
  - Main entry point for the project. It:
    1. Prints a data summary (number of activities, rooms, time slots).
    2. Builds a sample schedule and evaluates its fitness as a sanity check.
    3. Prints the GA configuration (population size, mutation rate, etc.).
    4. Runs the genetic algorithm via run_ga(...) with a fixed random seed.
    5. Prints:
       - The number of generations
       - The best fitness in the final generation
       - A preview of the best schedule (first few activities, ordered by time)
       - Statistics for the last 5 generations:
         - best / average / worst fitness
         - improvement percentage
    6. Exports two artifacts:
       - fitness_history.csv
       - best_schedule_by_time.txt

- plots.py (optional)
  - A small helper script to visualize the GA behavior using Matplotlib:
    - Loads fitness_history.csv
    - Plots best / average / worst fitness over generations
    - This corresponds to the “Charts” requirement in the assignment.

------------------------------------------------------------
2. Requirements
------------------------------------------------------------

The core GA implementation (main.py, data.py, fitness.py, ga_core.py,
schedule_repr.py) uses only the Python standard library.

To run the main program, you only need:

- Python 3.9+ (tested with Python 3.10+)
- No additional packages required.

To run the plotting script (plots.py), you additionally need:

    pip install matplotlib pandas

------------------------------------------------------------
3. How to Run
------------------------------------------------------------

3.1 Clone the repository

    git clone https://github.com/DaheChen/cs461-ga-scheduler.git
    cd cs461-ga-scheduler

3.2 Run the main program

    python main.py

(or: python3 main.py, depending on your environment)

This will:

1. Print a data summary.
2. Print a sample schedule (first 6 activities ordered by time).
3. Print the fitness of the sample schedule.
4. Show the GA configuration (population size, mutation rate, etc.).
5. Run the GA:
   - Display the final number of generations.
   - Display the best fitness of the final generation.
   - Display a preview of the best schedule (first 6 activities ordered by time).
   - Display statistics for the last 5 generations:
     - best / average / worst fitness
     - generation-to-generation improvement percentage.
6. Export two files in the project directory:
   - fitness_history.csv
   - best_schedule_by_time.txt

With a fixed rng_seed, running "python main.py" on different machines
will reproduce the same fitness history and best schedule.

------------------------------------------------------------
4. Output Files
------------------------------------------------------------

4.1 fitness_history.csv

Each row corresponds to one generation of the GA.
Columns:

- generation        – generation index (starting from 0)
- best_fitness      – best schedule fitness in this generation
- avg_fitness       – average fitness of the population
- worst_fitness     – worst fitness in the population
- improvement_percent – percentage improvement of avg_fitness over the previous generation
- mutation_rate     – the mutation rate used (useful if it is adjusted over time)

This file is used for:

- plotting fitness curves (best / avg / worst vs. generation)
- analyzing convergence behavior
- supporting the “Required performance assessment metrics” and “Charts” parts of the assignment.

4.2 best_schedule_by_time.txt

A text representation of the best schedule found by the GA, ordered by time.
Columns:

- Activity ID
- Time slot
- Room
- Facilitator
- Expected enrollment

This file is useful for:

- Inspecting whether the schedule looks reasonable (no obvious conflicts)
- Including a snapshot of the final timetable in the video report or written report
- Checking how the GA handled large-enrollment courses, special SLA101/191 rules, etc.

------------------------------------------------------------
5. Plotting Fitness Curves (Optional)
------------------------------------------------------------

To create charts for the assignment (best / average / worst fitness over generations):

1) Install plotting dependencies (if not already installed):

    pip install matplotlib pandas

2) Run the plotting script:

    python plots.py

or use a short snippet like:

    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv("fitness_history.csv")

    plt.figure(figsize=(7, 4))
    plt.plot(df["generation"], df["best_fitness"], label="Best fitness")
    plt.plot(df["generation"], df["avg_fitness"], label="Average fitness")
    plt.plot(df["generation"], df["worst_fitness"], label="Worst fitness")

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("GA Fitness over Generations")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

These plots can be included in the video presentation to illustrate how
the GA quickly improves in early generations and then gradually converges.

------------------------------------------------------------
6. Mapping to Assignment Requirements
------------------------------------------------------------

This implementation covers the main requirements as follows:

- Population of random schedules (N ≥ 250)
  - Implemented in ga_core.py (initialize_population).
  - Parameters (population size, mutation rate, min/max generations) are configured in main.py.

- Fitness function
  - Fully implemented in fitness.py following Appendix A:
    - Room size penalties
    - Room conflicts
    - Facilitator conflicts and load
    - SLA101/191 spacing and special rules
    - (Optionally) time preferences and equipment requirements

- Softmax normalization and selection
  - Implemented in ga_core.py:
    - Fitness scores are converted to a probability distribution using softmax
      before selecting parents.

- Mutation and rate adjustment
  - A fixed mutation rate is used per run (e.g. 0.05 for debugging or 0.01 for larger runs).
  - The code can be easily extended to adjust the mutation rate over time, as suggested in the assignment.

- Stopping condition based on average fitness improvement
  - The GA runs at least min_generations.
  - After that, if the improvement in average fitness between generations is below 1%,
    the algorithm stops (or stops at max_generations at the latest).

- Performance metrics (Fitness Matrix)
  - For each generation, the code records:
    - best fitness
    - average fitness
    - worst fitness
    - improvement percentage
  - All of these are exported to fitness_history.csv and summarized in the console.

- Printing the schedule
  - schedule_repr.print_schedule prints:
    - activity, time, room, facilitator, enrollment
    - ordered by time (or by activity)
  - main.py prints a preview (first 6 activities) and saves the full best schedule
    to best_schedule_by_time.txt.

- Charts
  - fitness_history.csv can be plotted using plots.py or the code snippet above
    to show best / average / worst fitness over generations.

------------------------------------------------------------
7. Reproducibility
------------------------------------------------------------

To keep the results reproducible:

- The GA uses a fixed random seed (rng_seed) specified in main.py.
- Given the same code and Python version, running:

    python main.py

on different machines should produce the same:

- console output (up to formatting)
- fitness_history.csv
- best_schedule_by_time.txt

This makes it easier to debug, grade, and discuss the results in the video/report.

------------------------------------------------------------

Author: Dahe Chen
Course: CS 461 – Introduction to Artificial Intelligence
Program 2 – Genetic Algorithm Scheduler
