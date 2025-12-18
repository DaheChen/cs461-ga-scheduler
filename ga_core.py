"""
ga_core.py

Genetic algorithm engine for the SLA scheduling problem.

Key ideas:
- A schedule is represented as a mapping:
      schedule[activity_name] = {
          "room": <room_name:str>,
          "time": <time_slot:str>,
          "facilitator": <facilitator_name:str>,
      }
- The population is a list of such schedules.
- We use a fitness function from fitness.py to evaluate each schedule.
- Selection is done with softmax-normalized fitness values.
- Crossover is done per-activity (uniform crossover).
- Mutation randomly changes room/time/facilitator for each activity
  with a given mutation rate.
"""

from __future__ import annotations

import math
import random
from typing import List, Dict, Any, Tuple

from data import ACTIVITIES, ROOMS, TIMES, FACILITATORS
from schedule_repr import Schedule, validate_schedule_structure
from fitness import compute_schedule_fitness


Population = List[Schedule]


def _copy_schedule(schedule: Schedule) -> Schedule:
    """Deep copy a schedule (only one level deep, since values are simple dicts)."""
    return {act: dict(assign) for act, assign in schedule.items()}


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def _random_assignment(rng: random.Random) -> Dict[str, str]:
    """
    Create a random assignment for a single activity:
    - room: any room from ROOMS
    - time: any time slot from TIMES
    - facilitator: any facilitator from FACILITATORS

    Note: we intentionally use the full domains here, as the spec suggests:
    "Use the preferred/other listing for scoring purposes, not for selecting faculty."
    """
    room = rng.choice(list(ROOMS.keys()))
    time = rng.choice(TIMES)
    facilitator = rng.choice(FACILITATORS)
    return {"room": room, "time": time, "facilitator": facilitator}


def create_random_schedule(rng: random.Random) -> Schedule:
    """Create a random schedule with assignments for all activities."""
    schedule: Schedule = {}
    for activity in ACTIVITIES.keys():
        schedule[activity] = _random_assignment(rng)
    # Basic structural check (optional but helpful for debugging)
    assert validate_schedule_structure(schedule)
    return schedule


def initialize_population(pop_size: int, rng: random.Random) -> Population:
    """Create an initial population of random schedules."""
    return [create_random_schedule(rng) for _ in range(pop_size)]


# ---------------------------------------------------------------------------
# Fitness evaluation and selection probabilities
# ---------------------------------------------------------------------------

def evaluate_population(population: Population) -> List[float]:
    """Compute fitness values for all individuals in the population."""
    return [compute_schedule_fitness(ind) for ind in population]


def softmax(fitnesses: List[float]) -> List[float]:
    """
    Convert fitness scores into a probability distribution using softmax.

    We subtract max(fitness) for numerical stability:
        p_i = exp(f_i - max_f) / sum_j exp(f_j - max_f)
    """
    if not fitnesses:
        return []

    max_f = max(fitnesses)
    exps = [math.exp(f - max_f) for f in fitnesses]
    total = sum(exps)

    if total <= 0.0:
        # Fallback to a uniform distribution if something goes wrong.
        n = len(fitnesses)
        return [1.0 / n] * n

    return [e / total for e in exps]


def build_selection_cdf(fitnesses: List[float]) -> List[float]:
    """
    Build a cumulative distribution function (CDF) from softmax probabilities.
    This allows O(n) sampling via a single random number and linear scan.
    """
    probs = softmax(fitnesses)
    cdf: List[float] = []
    cumulative = 0.0
    for p in probs:
        cumulative += p
        cdf.append(cumulative)
    # Ensure the last value is exactly 1.0 (or very close).
    if cdf:
        cdf[-1] = 1.0
    return cdf


def sample_index_from_cdf(cdf: List[float], rng: random.Random) -> int:
    """Sample a single index from a CDF using a random number in [0, 1)."""
    r = rng.random()
    for i, threshold in enumerate(cdf):
        if r <= threshold:
            return i
    return len(cdf) - 1  # Fallback (should rarely happen due to cdf[-1] == 1.0)


# ---------------------------------------------------------------------------
# Crossover and mutation
# ---------------------------------------------------------------------------

def crossover(parent1: Schedule, parent2: Schedule, rng: random.Random) -> Schedule:
    """
    Uniform crossover:
    For each activity, randomly choose the assignment from parent1 or parent2.
    """
    child: Schedule = {}
    for activity in ACTIVITIES.keys():
        if rng.random() < 0.5:
            src = parent1
        else:
            src = parent2
        child[activity] = dict(src[activity])
    assert validate_schedule_structure(child)
    return child


def mutate(schedule: Schedule, mutation_rate: float, rng: random.Random) -> None:
    """
    Mutate a schedule in-place.

    For each activity and each of its fields (room, time, facilitator),
    we apply mutation with probability = mutation_rate.

    If mutation is triggered for a field, we randomly pick a new value from
    the appropriate domain (ROOMS, TIMES, FACILITATORS).
    """
    rooms = list(ROOMS.keys())

    for activity, assignment in schedule.items():
        # Mutate room
        if rng.random() < mutation_rate:
            assignment["room"] = rng.choice(rooms)

        # Mutate time
        if rng.random() < mutation_rate:
            assignment["time"] = rng.choice(TIMES)

        # Mutate facilitator
        if rng.random() < mutation_rate:
            assignment["facilitator"] = rng.choice(FACILITATORS)


# ---------------------------------------------------------------------------
# Main GA loop
# ---------------------------------------------------------------------------

def run_ga(
    population_size: int = 300,
    mutation_rate: float = 0.01,
    min_generations: int = 100,
    max_generations: int = 500,
    rng_seed: int | None = 42,
    improvement_threshold: float = 1.0,  # Stop when improvement < 1%
    mutation_halve_interval: int = 10,   # Check every N generations
) -> Tuple[Schedule, float, List[Dict[str, Any]]]:
    """
    Run the genetic algorithm with adaptive mutation rate.

    Returns:
        (best_schedule, best_fitness, fitness_history)

    fitness_history is a list of dicts with:
        {
            "generation": int,
            "best_fitness": float,
            "avg_fitness": float,
            "worst_fitness": float,
            "improvement_percent": float,
            "mutation_rate": float,
        }

    Stopping condition:
    - Always run at least min_generations
    - Stop when the improvement in average fitness from one generation to the next
      is less than 1% (after min_generations), or when max_generations is reached.

    Adaptive mutation:
    - Every mutation_halve_interval generations, if average fitness improved,
      halve the mutation rate (as per spec).
    """
    rng = random.Random(rng_seed)

    # 1) Initialize population
    population: Population = initialize_population(population_size, rng)
    fitnesses: List[float] = evaluate_population(population)

    history: List[Dict[str, Any]] = []
    prev_avg_fitness: float | None = None

    # Track for adaptive mutation rate
    current_mutation_rate = mutation_rate
    avg_at_last_mutation_check: float | None = None
    min_mutation_rate = 0.001  # Don't go below this

    for gen in range(max_generations):
        # --- Compute statistics for this generation ---
        best_f = max(fitnesses)
        worst_f = min(fitnesses)
        avg_f = sum(fitnesses) / len(fitnesses)

        if prev_avg_fitness is None or abs(prev_avg_fitness) < 1e-9:
            improvement_percent = 100.0
        else:
            improvement_percent = ((avg_f - prev_avg_fitness) / abs(prev_avg_fitness)) * 100.0

        history.append(
            {
                "generation": gen,
                "best_fitness": best_f,
                "avg_fitness": avg_f,
                "worst_fitness": worst_f,
                "improvement_percent": improvement_percent,
                "mutation_rate": current_mutation_rate,
            }
        )

        # --- Progress output every 10 generations ---
        if gen % 10 == 0:
            print(f"  Gen {gen:3d} | best={best_f:.3f}, avg={avg_f:.3f}, "
                  f"improv={improvement_percent:+.2f}%, mutation={current_mutation_rate:.4f}")

        # --- Adaptive mutation rate (halve if improving) ---
        if gen > 0 and gen % mutation_halve_interval == 0:
            if avg_at_last_mutation_check is not None:
                if avg_f > avg_at_last_mutation_check and current_mutation_rate > min_mutation_rate:
                    # Still improving, halve the mutation rate
                    current_mutation_rate = max(current_mutation_rate / 2, min_mutation_rate)
                    print(f"  >> Mutation rate halved to {current_mutation_rate:.4f}")
            avg_at_last_mutation_check = avg_f

        # --- Check stopping condition (after min_generations) ---
        if gen + 1 >= min_generations and abs(improvement_percent) < improvement_threshold:
            print(f"  >> Converged at generation {gen} (improvement {improvement_percent:.2f}% < {improvement_threshold}%)")
            break

        # --- Build selection CDF based on current fitnesses ---
        cdf = build_selection_cdf(fitnesses)

        # --- Create next generation ---
        new_population: Population = []

        while len(new_population) < population_size:
            # Select two parents (with replacement)
            idx1 = sample_index_from_cdf(cdf, rng)
            idx2 = sample_index_from_cdf(cdf, rng)
            parent1 = population[idx1]
            parent2 = population[idx2]

            # Produce two children via crossover
            child1 = crossover(parent1, parent2, rng)
            child2 = crossover(parent1, parent2, rng)

            # Mutate children with current (adaptive) mutation rate
            mutate(child1, current_mutation_rate, rng)
            mutate(child2, current_mutation_rate, rng)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        # Move to next generation
        population = new_population
        fitnesses = evaluate_population(population)
        prev_avg_fitness = avg_f

    # After the loop, pick the best schedule from the final population.
    best_index = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
    best_schedule = population[best_index]
    best_fitness = fitnesses[best_index]

    return best_schedule, best_fitness, history
