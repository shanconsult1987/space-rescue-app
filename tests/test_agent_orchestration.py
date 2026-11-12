import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.agent_orchestration import (
    develop,
    invoke_agent,
    latest_plan_run,
    require_approval,
    validate_changes,
)


class AgentOrchestrationTests(unittest.TestCase):
    def test_allowed_application_changes(self):
        with patch(
            "tools.agent_orchestration.run",
            side_effect=["app/missions.py\0tests/test_missions.py\0",
                         "100644 abc 0\tapp/missions.py\n"],
        ):
            validate_changes()

    def test_reject_protected_paths(self):
        for path in [
            ".github/workflows/ci.yml", "tools/agent_orchestration.py",
            "tests/test_agent_orchestration.py", "app/AGENTS.md",
            "app/.env", "unexpected.txt",
        ]:
            with self.subTest(path=path):
                with patch("tools.agent_orchestration.run", return_value=path):
                    with self.assertRaisesRegex(ValueError, "protected path"):
                        validate_changes()

    def test_reject_symlinks(self):
        with patch(
            "tools.agent_orchestration.run",
            side_effect=["app/link\0", "120000 abc 0\tapp/link\n"],
        ):
            with self.assertRaisesRegex(ValueError, "Unsupported file mode"):
                validate_changes()

    def test_review_requires_explicit_approval(self):
        require_approval("APPROVE\n\n## Final recommendation\nReady for review")
        for review in ["REQUEST_CHANGES\nMissing tests", "Looks good", "\n"]:
            with self.subTest(review=review):
                with self.assertRaises(ValueError):
                    require_approval(review)

    def test_agent_failure_is_not_swallowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with patch(
                "tools.agent_orchestration.subprocess.run",
                side_effect=subprocess.CalledProcessError(1, "copilot"),
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    invoke_agent("planner", "Plan", directory / "plan.md", directory)

    def test_empty_agent_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with patch("tools.agent_orchestration.subprocess.run"):
                with self.assertRaisesRegex(ValueError, "empty report"):
                    invoke_agent("planner", "Plan", directory / "plan.md", directory)

    def test_select_latest_bot_plan_and_ignore_spoofed_comments(self):
        comments = [
            {"user": {"login": "github-actions[bot]"},
             "body": "<!-- spacerescue-plan run=10 -->"},
            {"user": {"login": "github-actions[bot]"},
             "body": "<!-- spacerescue-plan run=20 -->"},
            {"user": {"login": "another-user"},
             "body": "<!-- spacerescue-plan run=30 -->"},
        ]
        self.assertEqual(latest_plan_run(comments), "20")

    def test_missing_plan_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "No published plan"):
            latest_plan_run([])

    def test_developer_tests_and_reviewer_pass_before_patch_is_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "plan.md").write_text("Approved plan", encoding="utf-8")
            (directory / "issue.json").write_text('{"number": 1}', encoding="utf-8")

            def agent_result(agent, prompt, report, directory, **kwargs):
                report.write_text(
                    "APPROVE\nReady for human review" if agent == "reviewer"
                    else "Implemented approved plan",
                    encoding="utf-8",
                )

            with (
                patch("tools.agent_orchestration.invoke_agent", side_effect=agent_result) as agent,
                patch("tools.agent_orchestration.validate_changes"),
                patch("tools.agent_orchestration.run", side_effect=["", "patch", "patch"]),
                patch("tools.agent_orchestration.subprocess.run") as tests,
            ):
                develop(directory)

            self.assertEqual(
                [call.args[0] for call in agent.call_args_list],
                ["developer", "reviewer"],
            )
            self.assertEqual(
                tests.call_args.args[0],
                ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
            )
            self.assertEqual(
                (directory / "changes.patch").read_text(encoding="utf-8"), "patch"
            )

    def test_test_failure_prevents_review_and_patch_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "plan.md").write_text("Approved plan", encoding="utf-8")
            (directory / "issue.json").write_text('{"number": 1}', encoding="utf-8")
            with (
                patch("tools.agent_orchestration.invoke_agent") as agent,
                patch("tools.agent_orchestration.validate_changes"),
                patch("tools.agent_orchestration.run"),
                patch(
                    "tools.agent_orchestration.subprocess.run",
                    side_effect=subprocess.CalledProcessError(1, "unittest"),
                ),
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    develop(directory)
            self.assertEqual(agent.call_count, 1)
            self.assertFalse((directory / "changes.patch").exists())


if __name__ == "__main__":
    unittest.main()
