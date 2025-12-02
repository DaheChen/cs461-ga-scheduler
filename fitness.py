"""
fitness.py

Implements the fitness function for the SLA scheduling problem.

A schedule is represented as:
    schedule[activity_name] = {
        "room": <room_name:str>,
        "time": <time_slot:str>,
        "facilitator": <facilitator_name:str>,
    }

The main entry point is:
    compute_schedule_fitness(schedule) -> float

This function encodes the rules described in Appendix A:
- Room conflicts
- Room size penalties/bonuses
- Facilitator preferences (preferred/other/other)
- Facilitator load (per time-slot and total load)
- Activity-specific rules for SLA101A/B and SLA191A/B
- Optional rules for time preferences and equipment requirements
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from data import (
    ACTIVITIES,
    ROOMS,
    TIMES,
    FACILITATORS,
    FACILITATOR_TIME_PREFERENCES,
    COURSE_EQUIPMENT_REQUIREMENTS,
)
from schedule_repr import Schedule


# Precompute a simple index for time slots (10 AM -> 0, 11 AM -> 1, ...)
TIME_INDEX: Dict[str, int] = {t: i for i, t in enumerate(TIMES)}


def _get_building(room_name: str) -> str:
    """
    Extract the building name from a room string like "Beach 201" or "Roman 216".
    We simply take the first token before the space.
    """
    return room_name.split()[0]


def compute_schedule_fitness(schedule: Schedule) -> float:
    """
    Compute the total fitness of a schedule.

    The fitness is the sum of:
    - per-activity scores (room size, room conflicts, facilitator preference,
      per-time-slot facilitator load)
    - per-facilitator load penalties/bonuses (total number of activities)
    - activity-specific rules for SLA101 / SLA191
    - optional time preferences and equipment requirements

    :param schedule: mapping from activity -> {"room", "time", "facilitator"}
    :return: total fitness score as a float
    """

    total_fitness: float = 0.0

    # -------------------------------------------------------------------------
    # Precompute helper maps for conflicts and load:
    # -------------------------------------------------------------------------
    # (room, time) -> list of activities scheduled there
    room_time_to_activities: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    # (facilitator, time) -> list of activities for that facilitator at that time
    fac_time_to_activities: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    # facilitator -> list of (activity, time)
    fac_to_activities: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for activity, assignment in schedule.items():
        room = assignment["room"]
        time = assignment["time"]
        facilitator = assignment["facilitator"]

        room_time_to_activities[(room, time)].append(activity)
        fac_time_to_activities[(facilitator, time)].append(activity)
        fac_to_activities[facilitator].append((activity, time))

    # -------------------------------------------------------------------------
    # 1) Per-activity base fitness
    # -------------------------------------------------------------------------
    for activity, assignment in schedule.items():
        room = assignment["room"]
        time = assignment["time"]
        facilitator = assignment["facilitator"]

        act_info = ACTIVITIES[activity]
        enrollment = act_info["enrollment"]
        preferred = act_info["preferred"]
        others = act_info["others"]

        activity_score = 0.0

        # --- Room conflict: same time & same room as another activity ---
        activities_in_same_room_time = room_time_to_activities[(room, time)]
        if len(activities_in_same_room_time) > 1:
            # "Activity is scheduled at the same time in the same room as another of the activities: -0.5"
            activity_score -= 0.5

        # --- Room size rules (capacity vs expected enrollment) ---
        capacity = ROOMS[room]["capacity"]
        if capacity < enrollment:
            # "Activities is in a room too small for its expected enrollment: -0.5"
            activity_score -= 0.5
        else:
            ratio = capacity / enrollment
            # Note: check > 3x first so it overrides the 1.5x penalty.
            if ratio > 3.0:
                # "Activities is in a room with capacity > 3 times expected enrollment: -0.4"
                activity_score -= 0.4
            elif ratio > 1.5:
                # "Activities is in a room with capacity > 1.5 times expected enrollment: -0.2"
                activity_score -= 0.2
            else:
                # "Otherwise +0.3" (room is a reasonable size)
                activity_score += 0.3

        # --- Facilitator preference rules ---
        if facilitator in preferred:
            # "Activities is overseen by a preferred facilitator: +0.5"
            activity_score += 0.5
        elif facilitator in others:
            # "Activities is overseen by another facilitator listed for that activity: +0.2"
            activity_score += 0.2
        else:
            # "Activities is overseen by some other facilitator: -0.1"
            activity_score -= 0.1

        # --- Facilitator load at this time slot ---
        activities_for_fac_at_time = fac_time_to_activities[(facilitator, time)]
        if len(activities_for_fac_at_time) == 1:
            # "Activity facilitator is scheduled for only 1 activity in this time slot: +0.2"
            activity_score += 0.2
        elif len(activities_for_fac_at_time) > 1:
            # "Activity facilitator is scheduled for more than one activity at the same time: - 0.2"
            activity_score -= 0.2

        # --- Optional: facilitator time preferences ---
        # See "Time Slot Preferences" section (optional constraints).
        prefs = FACILITATOR_TIME_PREFERENCES.get(facilitator)
        if prefs is not None:
            like_map = prefs.get("like", {})
            avoid_map = prefs.get("avoid", {})
            # If the time is in a "like" list, we add a small bonus (e.g., +0.1).
            if time in like_map:
                activity_score += like_map[time]
            # If the time is in an "avoid" list, we add a small penalty (e.g., -0.2).
            if time in avoid_map:
                activity_score += avoid_map[time]

        # --- Optional: equipment requirements ---
        # "When both requirements are met +0.2, only one met -0.1, else -0.3"
        eq_req = COURSE_EQUIPMENT_REQUIREMENTS.get(activity)
        if eq_req is not None:
            required_lab = eq_req["lab"]
            required_proj = eq_req["projector"]
            room_has_lab = ROOMS[room]["has_lab"]
            room_has_proj = ROOMS[room]["has_projector"]

            # Count how many required features are satisfied.
            required_count = 0
            satisfied_count = 0

            if required_lab:
                required_count += 1
                if room_has_lab:
                    satisfied_count += 1

            if required_proj:
                required_count += 1
                if room_has_proj:
                    satisfied_count += 1

            if required_count > 0:
                if satisfied_count == required_count:
                    activity_score += 0.2
                elif satisfied_count > 0:
                    activity_score -= 0.1
                else:
                    activity_score -= 0.3

        # Accumulate per-activity score
        total_fitness += activity_score

    # -------------------------------------------------------------------------
    # 2) Facilitator total load rules (number of activities each facilitator has)
    # -------------------------------------------------------------------------
    for facilitator in FACILITATORS:
        activities_for_fac = fac_to_activities.get(facilitator, [])
        total_load = len(activities_for_fac)

        if total_load > 4:
            # "Facilitator is scheduled to oversee more than 4 activities total: -0.5"
            total_fitness -= 0.5

        if facilitator != "Tyler":
            # For normal facilitators: penalty if they are scheduled for <3 activities (but at least 1).
            if 0 < total_load < 3:
                # "Facilitator is scheduled to oversee only <3 activities*: -0.4"
                total_fitness -= 0.4
        else:
            # Special exception for Dr. Tyler:
            # "*No penalty if he’s only required to oversee < 2 activities."
            # We interpret this as: apply the "<3" penalty only when total_load == 2.
            if total_load == 2:
                total_fitness -= 0.4

    # -------------------------------------------------------------------------
    # 3) Activity-specific adjustments for SLA101A/B and SLA191A/B
    # -------------------------------------------------------------------------

    def _get_time_and_room(act_name: str) -> Tuple[str, str]:
        """Helper to fetch (time, room) for a specific activity."""
        a = schedule[act_name]
        return a["time"], a["room"]

    # SLA101 sections
    t_101a, r_101a = _get_time_and_room("SLA101A")
    t_101b, r_101b = _get_time_and_room("SLA101B")
    idx_101a = TIME_INDEX[t_101a]
    idx_101b = TIME_INDEX[t_101b]

    # "The 2 sections of SLA 101 are more than 4 hours apart: + 0.5"
    if abs(idx_101a - idx_101b) > 4:
        total_fitness += 0.5

    # "Both sections of SLA 101 are in the same time slot: -0.5"
    if idx_101a == idx_101b:
        total_fitness -= 0.5

    # SLA191 sections
    t_191a, r_191a = _get_time_and_room("SLA191A")
    t_191b, r_191b = _get_time_and_room("SLA191B")
    idx_191a = TIME_INDEX[t_191a]
    idx_191b = TIME_INDEX[t_191b]

    # "The 2 sections of SLA 191 are more than 4 hours apart: + 0.5"
    if abs(idx_191a - idx_191b) > 4:
        total_fitness += 0.5

    # "Both sections of SLA 191 are in the same time slot: -0.5"
    if idx_191a == idx_191b:
        total_fitness -= 0.5

    # Now consider all pairs of SLA 101 vs SLA 191 sections.
    pairs_101_191 = [
        ("SLA101A", "SLA191A"),
        ("SLA101A", "SLA191B"),
        ("SLA101B", "SLA191A"),
        ("SLA101B", "SLA191B"),
    ]

    for act_101, act_191 in pairs_101_191:
        t_101, r_101 = _get_time_and_room(act_101)
        t_191, r_191 = _get_time_and_room(act_191)
        i_101 = TIME_INDEX[t_101]
        i_191 = TIME_INDEX[t_191]
        dt = abs(i_101 - i_191)

        # "A section of SLA 191 and a section of SLA 101 are taught in the same time slot: -0.25"
        if dt == 0:
            total_fitness -= 0.25

        # "A section of SLA 191 and a section of SLA 101 are overseen in consecutive time slots: +0.5"
        if dt == 1:
            total_fitness += 0.5

            # "In this case only (consecutive time slots), one of the activities is in Roman or Beach,
            # and the other isn’t: -0.4"
            building_101 = _get_building(r_101)
            building_191 = _get_building(r_191)
            is_roman_beach_101 = building_101 in {"Roman", "Beach"}
            is_roman_beach_191 = building_191 in {"Roman", "Beach"}

            # Exactly one of them is in Roman/Beach -> penalty
            if is_roman_beach_101 ^ is_roman_beach_191:
                total_fitness -= 0.4

        # "A section of SLA 191 and a section of SLA 101 are taught separated by 1 hour: + 0.25"
        # (i.e., one time-slot gap, so dt == 2)
        if dt == 2:
            total_fitness += 0.25

    # -------------------------------------------------------------------------
    # NOTE: There is also a line in the spec:
    #   "If any facilitator scheduled for consecutive time slots:
    #    Same rules as for SLA 191 and SLA 101 in consecutive time slots—see below."
    #
    # This could be implemented as an additional bonus/penalty for any facilitator who
    # teaches back-to-back classes, similar to the +0.5 and -0.4 building-distance rule
    # above. For clarity and to avoid double-counting with the SLA101/SLA191 rules,
    # we keep the implementation focused on the explicitly named activities here.
    # -------------------------------------------------------------------------

    return total_fitness
