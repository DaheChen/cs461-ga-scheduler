"""
data.py

All problem-specific data for the SLA scheduling problem:
- activities (enrollment, preferred/other facilitators)
- rooms (capacity, equipment)
- time slots
- facilitators
- optional time preferences
- optional equipment requirements
"""


# ---------- Activities ----------

# For each activity:
#   - enrollment: expected enrollment
#   - preferred: list of preferred facilitators
#   - others: list of other acceptable facilitators
ACTIVITIES = {
    "SLA101A": {
        "enrollment": 40,
        "preferred": ["Glen", "Lock", "Banks"],
        "others": ["Numen", "Richards", "Shaw", "Singer"],
    },
    "SLA101B": {
        "enrollment": 35,
        "preferred": ["Glen", "Lock", "Banks"],
        "others": ["Numen", "Richards", "Shaw", "Singer"],
    },
    "SLA191A": {
        "enrollment": 45,
        "preferred": ["Glen", "Lock", "Banks"],
        "others": ["Numen", "Richards", "Shaw", "Singer"],
    },
    "SLA191B": {
        "enrollment": 40,
        "preferred": ["Glen", "Lock", "Banks"],
        "others": ["Numen", "Richards", "Shaw", "Singer"],
    },
    "SLA201": {
        "enrollment": 60,
        "preferred": ["Glen", "Banks", "Zeldin", "Lock", "Singer"],
        "others": ["Richards", "Uther", "Shaw"],
    },
    "SLA291": {
        "enrollment": 50,
        "preferred": ["Glen", "Banks", "Zeldin", "Lock", "Singer"],
        "others": ["Richards", "Uther", "Shaw"],
    },
    "SLA303": {
        "enrollment": 25,
        "preferred": ["Glen", "Zeldin"],
        "others": ["Banks"],
    },
    "SLA304": {
        "enrollment": 20,
        "preferred": ["Singer", "Uther"],
        "others": ["Richards"],
    },
    "SLA394": {
        "enrollment": 15,
        "preferred": ["Tyler", "Singer"],
        "others": ["Richards", "Zeldin"],
    },
    "SLA449": {
        "enrollment": 30,
        "preferred": ["Tyler", "Zeldin", "Uther"],
        "others": ["Zeldin", "Shaw"],
    },
    "SLA451": {
        "enrollment": 90,
        "preferred": ["Lock", "Banks", "Zeldin"],
        "others": ["Tyler", "Singer", "Shaw", "Glen"],
    },
}


# ---------- Facilitators ----------

FACILITATORS = [
    "Lock",
    "Glen",
    "Banks",
    "Richards",
    "Shaw",
    "Singer",
    "Uther",
    "Tyler",
    "Numen",
    "Zeldin",
]


# ---------- Rooms & Capacities / Equipment ----------

# For each room:
#   - capacity: integer
#   - has_lab: whether the room has lab facilities
#   - has_projector: whether the room has a projector
ROOMS = {
    "Beach 201": {"capacity": 18, "has_lab": False, "has_projector": True},
    "Beach 301": {"capacity": 25, "has_lab": True, "has_projector": True},
    "Frank 119": {"capacity": 95, "has_lab": True, "has_projector": True},
    "Loft 206": {"capacity": 55, "has_lab": False, "has_projector": False},
    "Loft 310": {"capacity": 48, "has_lab": True, "has_projector": False},
    "James 325": {"capacity": 110, "has_lab": True, "has_projector": True},
    "Roman 201": {"capacity": 40, "has_lab": False, "has_projector": False},
    "Roman 216": {"capacity": 80, "has_lab": True, "has_projector": True},
    "Slater 003": {"capacity": 32, "has_lab": True, "has_projector": True},
}


# ---------- Time slots ----------

TIMES = [
    "10 AM",
    "11 AM",
    "12 PM",
    "1 PM",
    "2 PM",
    "3 PM",
]


# ---------- Optional: facilitator time preferences ----------

# These correspond to the "Time Slot Preferences" section (optional constraints).
# We store them here so the fitness function can choose to use them or not.
# Format:
#   FACILITATOR_TIME_PREFERENCES[name] = {
#       "like": {time_slot: bonus},
#       "avoid": {time_slot: penalty},
#   }
FACILITATOR_TIME_PREFERENCES = {
    "Glen": {
        "like": {"10 AM": 0.1, "11 AM": 0.1},
        "avoid": {"3 PM": -0.2},
    },
    "Banks": {
        "like": {"10 AM": 0.1, "12 PM": 0.1},
        "avoid": {"11 AM": -0.1, "1 PM": -0.1},
    },
    "Tyler": {
        "like": {"2 PM": 0.1, "3 PM": 0.1},
        "avoid": {"10 AM": -0.2, "11 AM": -0.2},
    },
    "Singer": {
        "like": {},
        "avoid": {"12 PM": -0.3},
    },
}


# ---------- Optional: course equipment requirements ----------

# From the "Equipment Requirements" section (optional constraints).
# Format:
#   COURSE_EQUIPMENT_REQUIREMENTS[activity] = {
#       "lab": bool,
#       "projector": bool,
#   }
COURSE_EQUIPMENT_REQUIREMENTS = {
    "SLA304": {"lab": True, "projector": False},
    "SLA303": {"lab": True, "projector": True},
    "SLA191A": {"lab": True, "projector": False},
    "SLA191B": {"lab": True, "projector": False},
    "SLA291": {"lab": True, "projector": False},
    "SLA449": {"lab": False, "projector": True},
    "SLA451": {"lab": True, "projector": True},
}
