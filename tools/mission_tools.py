from app.missions import (
    get_mission,
    get_missions,
    get_active_missions
)


def get_mission_status(mission_id):

    mission = get_mission(mission_id)

    if mission is None:

        return {
            "success": False,
            "error": "Mission not found"
        }

    return {
        "success": True,
        "mission_id": mission["id"],
        "name": mission["name"],
        "status": mission["status"],
        "priority": mission["priority"]
    }


def list_all_missions():

    return get_missions()


def list_active_missions():

    return get_active_missions()