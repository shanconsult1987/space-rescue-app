
import unittest

from app.missions import (
    MISSIONS,
    get_missions,
    get_mission,
    create_mission,
    delete_mission
)


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
