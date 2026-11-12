import json
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

from evaluation.evaluator import evaluate_case
from evaluation.run_evaluation import request_missions, run_evaluation


class EvaluationTests(unittest.TestCase):
    def test_filter_requires_correct_and_complete_results(self):
        active = {"id": 1, "status": "active"}
        pending = {"id": 2, "status": "pending"}
        case = {
            "id": "active", "required_endpoint": "/missions/active",
            "filter": {"status": "active"},
        }
        for data, expected in [([active], True), ([], False), ([pending], False)]:
            with self.subTest(data=data):
                evidence = {
                    "endpoints": {
                        "/missions": {"data": [active, pending], "error": None},
                        "/missions/active": {"data": data, "error": None},
                    },
                }
                self.assertEqual(evaluate_case(case, evidence)["passed"], expected)

    def test_live_http_status_json_and_response_shape(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                responses = {
                    "/valid": (200, "application/json", b'[{"id": 1}]'),
                    "/missing": (404, "application/json", b'{"error": "Not found"}'),
                    "/invalid-json": (200, "application/json", b"not-json"),
                    "/wrong-shape": (200, "application/json", b'{"id": 1}'),
                    "/wrong-type": (200, "text/plain", b'[{"id": 1}]'),
                }
                status, content_type, body = responses[self.path]
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        with HTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = Thread(target=server.serve_forever)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"
                self.assertEqual(
                    request_missions(base_url, "/valid"),
                    {"data": [{"id": 1}], "error": None},
                )
                for endpoint, message in [
                    ("/missing", "HTTP 404"),
                    ("/invalid-json", "Invalid JSON"),
                    ("/wrong-shape", "JSON array"),
                    ("/wrong-type", "application/json"),
                ]:
                    with self.subTest(endpoint=endpoint):
                        self.assertIn(message, request_missions(base_url, endpoint)["error"])
            finally:
                server.shutdown()
                thread.join()

    def test_reject_external_endpoint_paths(self):
        for endpoint in [None, "", "https://example.com", "//example.com"]:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    request_missions("http://127.0.0.1", endpoint)

    def test_report_records_real_endpoint_and_unit_test_failures(self):
        cases = [
            {"id": "active", "required_endpoint": "/missions/active",
             "filter": {"status": "active"}},
            {"id": "missing", "required_endpoint": "/missions/evaluation-missing",
             "filter": {"status": "active"}},
            {"id": "tests", "required_endpoint": None},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            cases_path = Path(temporary) / "cases.json"
            results_path = Path(temporary) / "results.json"
            cases_path.write_text(json.dumps(cases), encoding="utf-8")
            with (
                patch("evaluation.run_evaluation.CASES_FILE", cases_path),
                patch("evaluation.run_evaluation.RESULTS_FILE", results_path),
                patch("evaluation.run_evaluation.run_tests",
                      return_value={"passed": False, "output": "test failure evidence"}),
                patch("builtins.print"),
            ):
                report = run_evaluation()
            self.assertEqual(report["passed"], 1)
            self.assertEqual(report["failed"], 2)
            self.assertIn("HTTP 400", report["results"][1]["reason"])
            self.assertFalse(report["unit_tests_passed"])
            self.assertEqual(json.loads(results_path.read_text(encoding="utf-8")), report)
