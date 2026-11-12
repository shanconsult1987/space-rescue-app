
import json

import subprocess
import sys
import threading

from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from app.server import MissionHandler
from evaluation.evaluator import evaluate_case


ROOT = Path(__file__).resolve().parent.parent

CASES_FILE = ROOT / "evaluation" / "cases.json"

RESULTS_FILE = ROOT / "evaluation" / "results.json"


def run_tests():

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-v"
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    return {
        "passed": result.returncode == 0,
        "output": result.stdout + result.stderr
    }


def request_missions(base_url, endpoint):

    if not isinstance(endpoint, str) or not endpoint.startswith("/") or endpoint.startswith("//"):
        raise ValueError("Evaluation endpoints must be local absolute paths")

    try:
        with urlopen(base_url + endpoint, timeout=5) as response:
            if response.status != 200:
                return {"data": None, "error": f"HTTP {response.status} for {endpoint}; expected 200"}
            if response.headers.get_content_type() != "application/json":
                return {"data": None, "error": f"Expected application/json from {endpoint}"}
            data = json.load(response)
    except HTTPError as error:
        return {"data": None, "error": f"HTTP {error.code} for {endpoint}; expected 200"}
    except (URLError, TimeoutError, OSError) as error:
        return {"data": None, "error": f"Request failed for {endpoint}: {error}"}
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return {"data": None, "error": f"Invalid JSON from {endpoint}: {error}"}

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        return {"data": None, "error": f"Expected a JSON array of mission objects from {endpoint}"}

    return {"data": data, "error": None}


def run_evaluation():

    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation cases must be a nonempty list")

    test_result = run_tests()
    if not test_result["passed"]:
        print(test_result["output"], file=sys.stderr)

    with HTTPServer(("127.0.0.1", 0), MissionHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}"
            endpoints = {"/missions"}
            endpoints.update(
                case["required_endpoint"] for case in cases
                if case["required_endpoint"] is not None
            )
            evidence = {
                "endpoints": {
                    endpoint: request_missions(base_url, endpoint)
                    for endpoint in sorted(endpoints)
                },
                "tests_passed": test_result["passed"],
            }
            results = [evaluate_case(case, evidence) for case in cases]
        finally:
            server.shutdown()
            thread.join()


    passed = sum(
        result["passed"]
        for result in results
    )

    report = {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
        "unit_tests_passed": test_result["passed"]
    }

    RESULTS_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(
        json.dumps(report, indent=2)
    )

    return report


if __name__ == "__main__":

    report = run_evaluation()
    sys.exit(1 if report["failed"] or not report["unit_tests_passed"] else 0)
