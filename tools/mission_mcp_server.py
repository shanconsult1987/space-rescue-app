from mcp.server.fastmcp import FastMCP

from app.missions import (
    get_mission,
    get_active_missions,
    get_missions
)


server = FastMCP("SpaceRescue Mission Tool")


@server.tool()
def get_mission_status(mission_id: int) -> dict:
    """
    Get the current status of a mission.
    """

    mission = get_mission(mission_id)

    if mission is None:

        return {
            "success": False,
            "error": "Mission not found"
        }

    return {
        "success": True,
        "id": mission["id"],
        "name": mission["name"],
        "status": mission["status"],
        "priority": mission["priority"]
    }


@server.tool()
def list_missions() -> list:
    """
    Return all missions.
    """

    return get_missions()


@server.tool()
def list_active_missions() -> list:
    """
    Return active missions.
    """

    return get_active_missions()


if __name__ == "__main__":

    server.run()