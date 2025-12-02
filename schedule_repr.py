"""
schedule_repr.py

Representation and pretty-printing for schedules.

- A single schedule is represented as:
    schedule[activity_name] = {
        "room": <room_name:str>,
        "time": <time_slot:str>,
        "facilitator": <facilitator_name:str>,
    }

Example:
    schedule = {
        "SLA101A": {"room": "Frank 119", "time": "10 AM", "facilitator": "Glen"},
        "SLA101B": {"room": "Roman 201", "time": "11 AM", "facilitator": "Banks"},
    }
"""

from typing import Dict, Any, List, Literal

from data import ACTIVITIES, ROOMS, TIMES


Schedule = Dict[str, Dict[str, str]]  # activity -> {"room": ..., "time": ..., "facilitator": ...}


def validate_schedule_structure(schedule: Schedule) -> bool:
    """
    Quick structural check:
    - all activities present
    - each assignment has 'room', 'time', 'facilitator'
    - room / time values are from the known domains

    This does NOT check fitness or constraints; it only checks basic structure.
    """
    # 1) 每个活动都应该在 schedule 里
    if set(schedule.keys()) != set(ACTIVITIES.keys()):
        return False

    for activity, assignment in schedule.items():
        # 必须包含这三个 key
        for key in ("room", "time", "facilitator"):
            if key not in assignment:
                return False

        room = assignment["room"]
        time = assignment["time"]
        facilitator = assignment["facilitator"]

        if room not in ROOMS:
            return False
        if time not in TIMES:
            return False
        # facilitator 我们允许是任意字符串（fitness 再决定加减分）

        if not isinstance(facilitator, str):
            return False

    return True


def schedule_to_rows(schedule: Schedule) -> List[Dict[str, Any]]:
    """
    Convert a schedule dict into a list of row dicts, which is easier to sort and print.

    Each row dict has:
        {
            "activity": ...,
            "room": ...,
            "time": ...,
            "facilitator": ...,
            "enrollment": <expected enrollment from ACTIVITIES>,
        }
    """
    rows: List[Dict[str, Any]] = []
    for activity, assignment in schedule.items():
        row = {
            "activity": activity,
            "room": assignment["room"],
            "time": assignment["time"],
            "facilitator": assignment["facilitator"],
            "enrollment": ACTIVITIES[activity]["enrollment"],
        }
        rows.append(row)
    return rows


def print_schedule(
    schedule: Schedule,
    order_by: Literal["time", "activity"] = "time",
    max_activities: int | None = None,
) -> None:
    """
    Pretty-print a schedule.

    :param schedule: the schedule dict
    :param order_by: "time" or "activity"
    :param max_activities: if given, only print the first N activities after sorting
    """
    rows = schedule_to_rows(schedule)

    if order_by == "time":
        # 先按时间顺序，再按教室、活动名排序
        time_order = {t: i for i, t in enumerate(TIMES)}
        rows.sort(key=lambda r: (time_order[r["time"]], r["room"], r["activity"]))
    else:
        # 默认按活动名
        rows.sort(key=lambda r: r["activity"])

    if max_activities is not None:
        rows = rows[:max_activities]

    print("Activity  | Time  | Room        | Facilitator | Enroll")
    print("----------+-------+------------+------------+-------")
    for r in rows:
        print(
            f"{r['activity']:<9} | "
            f"{r['time']:<5} | "
            f"{r['room']:<10} | "
            f"{r['facilitator']:<10} | "
            f"{r['enrollment']:>5}"
        )
