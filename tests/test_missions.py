
import unittest
import json
from threading import Thread
from urllib.request import urlopen
from http.server import HTTPServer

from app.missions import (
    MISSIONS,
    get_missions,
    get_active_missions,
    get_high_priority_missions,
    get_mission,
    create_mission,
    delete_mission
)
from app.server import MissionHandler
from tools.mission_tools import list_active_missions


class MissionHTTPTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.server = HTTPServer(("127.0.0.1", 0), MissionHandler)
        cls.server_thread = Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):

        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def test_get_active_missions_returns_json(self):

        with urlopen(f"{self.base_url}/missions/active") as response:
            data = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(
            data,
            [MISSIONS[0], MISSIONS[2]]
        )

    def test_get_active_missions_returns_empty_json_array(self):

        original_statuses = [mission["status"] for mission in MISSIONS]

        try:
            for mission in MISSIONS:
                mission["status"] = "pending"

            with urlopen(f"{self.base_url}/missions/active") as response:
                data = json.loads(response.read())

            self.assertEqual(response.status, 200)
            self.assertEqual(data, [])
        finally:
            for mission, status in zip(MISSIONS, original_statuses):
                mission["status"] = status

    def test_get_high_priority_missions_returns_json(self):

        with urlopen(f"{self.base_url}/missions/high-priority") as response:
            data = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(data, [MISSIONS[0]])

    def test_existing_get_routes_are_unchanged(self):

        with urlopen(f"{self.base_url}/missions") as response:
            missions = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(missions, MISSIONS)

        with urlopen(f"{self.base_url}/missions/1") as response:
            mission = json.loads(response.read())

        self.assertEqual(response.status, 200)
        self.assertEqual(mission, MISSIONS[0])


class MissionTests(unittest.TestCase):

    def setUp(self):

        self.original = [
            mission.copy()
            for mission in MISSIONS
        ]

    def tearDown(self):

        MISSIONS.clear()
        MISSIONS.extend(self.original)

    def test_get_missions(self):

        self.assertEqual(
            len(get_missions()),
            3
        )

    def test_get_existing_mission(self):

        self.assertEqual(
            get_mission(1)["name"],
            "Mars Alpha"
        )

    def test_get_active_missions(self):

        expected = [MISSIONS[0], MISSIONS[2]]

        self.assertEqual(get_active_missions(), expected)
        self.assertEqual(list_active_missions(), expected)
        self.assertEqual(MISSIONS, self.original)

    def test_get_active_missions_with_no_matches(self):

        for mission in MISSIONS:
            mission["status"] = "pending"

        self.assertEqual(get_active_missions(), [])

    def test_get_active_missions_with_empty_list(self):

        MISSIONS.clear()

        self.assertEqual(get_active_missions(), [])

    def test_get_high_priority_missions(self):

        self.assertEqual(
            get_high_priority_missions(),
            [MISSIONS[0]]
        )

    def test_get_high_priority_missions_with_no_matches(self):

        for mission in MISSIONS:
            mission["priority"] = "medium"

        self.assertEqual(get_high_priority_missions(), [])

    def test_get_high_priority_missions_with_empty_list(self):

        MISSIONS.clear()

        self.assertEqual(get_high_priority_missions(), [])

    def test_get_missing_mission(self):

        self.assertIsNone(
            get_mission(999)
        )

    def test_create_mission(self):

        result = create_mission(
            "Mars Delta",
            "Explore south pole",
            "high"
        )

        self.assertEqual(
            result["status"],
            "pending"
        )

    def test_reject_invalid_names(self):

        invalid_names = [
            "", " ", "\t", "\n", " \t\r\n ",
            None, 0, 1, False, [], {}
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError,
                    "^Mission name is required$"
                ):
                    create_mission(name, "Test")

                self.assertEqual(MISSIONS, self.original)

    def test_reject_invalid_priority(self):

        invalid_priorities = [
            "urgent", "", " ", "\t\n", "HIGH", "Medium", " high ",
            None, 0, 1, False, [], {}
        ]

        for priority in invalid_priorities:
            with self.subTest(priority=priority):
                with self.assertRaisesRegex(
                    ValueError,
                    "^Invalid priority$"
                ):
                    create_mission(
                        "Mars Epsilon",
                        "Test",
                        priority
                    )

                self.assertEqual(MISSIONS, self.original)

    def test_delete_existing_mission(self):

        self.assertTrue(
            delete_mission(1)
        )

    def test_delete_missing_mission(self):

        self.assertFalse(
            delete_mission(999)
        )


if __name__ == "__main__":

    unittest.main()
