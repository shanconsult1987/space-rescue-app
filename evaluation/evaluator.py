
def evaluate_case(case, evidence):

    required = case["required_endpoint"]

    if required is None:
        passed = evidence["tests_passed"]
        reason = "Unit tests passed" if passed else "Unit tests failed"
    else:
        response = evidence["endpoints"][required]
        baseline = evidence["endpoints"]["/missions"]
        if response["error"]:
            passed = False
            reason = response["error"]
        elif baseline["error"]:
            passed = False
            reason = f"Cannot establish mission baseline: {baseline['error']}"
        else:
            filters = case["filter"]
            missions = baseline["data"]
            if not all(
                field in mission for mission in missions for field in filters
            ):
                passed = False
                reason = "Mission baseline is missing filter fields"
            else:
                expected = [
                    mission for mission in missions
                    if all(mission[field] == value for field, value in filters.items())
                ]
                passed = response["data"] == expected
                reason = (
                    "HTTP 200 JSON matches the expected filtered missions"
                    if passed else "HTTP JSON does not match the expected filtered missions"
                )

    return {
        "case_id": case["id"],
        "passed": passed,
        "reason": reason
    }
