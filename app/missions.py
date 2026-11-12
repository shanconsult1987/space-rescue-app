
MISSIONS = [
    {
        "id": 1,
        "name": "Mars Alpha",
        "status": "active",
        "priority": "high",
        "description": "Explore northern crater"
    },
    {
        "id": 2,
        "name": "Mars Beta",
        "status": "pending",
        "priority": "medium",
        "description": "Analyze soil samples"
    },
    {
        "id": 3,
        "name": "Mars Gamma",
        "status": "active",
        "priority": "low",
        "description": "Collect rock samples"
    }
]


def get_missions():
    return MISSIONS


def get_active_missions():
    return [
        mission
        for mission in MISSIONS
        if mission["status"] == "active"
    ]


def get_high_priority_missions():
    return [
        mission
        for mission in MISSIONS
        if mission["priority"] == "high"
    ]


def get_mission(mission_id):

    return next(
        (
            mission
            for mission in MISSIONS
            if mission["id"] == mission_id
        ),
        None
    )


def create_mission(name, description, priority="medium"):

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Mission name is required")

    if priority not in ["low", "medium", "high"]:
        raise ValueError("Invalid priority")

    mission = {
        "id": max(
            (item["id"] for item in MISSIONS),
            default=0
        ) + 1,
        "name": name.strip(),
        "status": "pending",
        "priority": priority,
        "description": description
    }

    MISSIONS.append(mission)

    return mission


def delete_mission(mission_id):

    mission = get_mission(mission_id)

    if mission is None:
        return False

    MISSIONS.remove(mission)

    return True
