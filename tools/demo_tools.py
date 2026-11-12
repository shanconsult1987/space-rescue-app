from tools.mission_tools import (
    get_mission_status,
    list_all_missions,
    list_active_missions
)

print("MISSION STATUS")

print(get_mission_status(1))

print("\nALL MISSIONS")

print(list_all_missions())

print("\nACTIVE MISSIONS")

print(list_active_missions())