# Space Rescue Mission App

A simple Python HTTP API for listing, retrieving, creating, and deleting space
rescue missions. The application uses only the Python standard library.

## Requirements

- Python 3.11+
- Git
- VS Code

## Run application

From the project root:

```powershell
python -m app.server
```

The API listens at `http://127.0.0.1:8000`. Press `Ctrl+C` to stop it.

## Data classes and model

The application does not currently define Python `dataclass` classes. Missions
are dictionaries stored in the global `MISSIONS` list in
[app/missions.py](app/missions.py).

| Field | Description |
| --- | --- |
| `id` | Integer assigned as the current maximum ID plus one. |
| `name` | Required nonblank string; surrounding whitespace is removed. |
| `status` | New missions start as `pending`; sample data also includes `active`. |
| `priority` | One of `low`, `medium`, or `high`; defaults to `medium`. |
| `description` | Description supplied by the caller; not validated. |

Three sample missions are loaded at startup. Data is held in memory only, so
changes are lost when the process restarts. Retrieval functions return the
underlying mutable data rather than copies.

## Key interfaces

### Mission functions

Defined in [app/missions.py](app/missions.py):

| Function | Behavior |
| --- | --- |
| `get_missions()` | Returns the mission list. |
| `get_active_missions()` | Returns a list of missions whose status is `active`, or an empty list if none match. |
| `get_mission(mission_id)` | Returns a matching mission, or `None`. |
| `create_mission(name, description, priority="medium")` | Validates the name and priority, appends a pending mission, and returns it. Raises `ValueError` for invalid input. |
| `delete_mission(mission_id)` | Removes a matching mission; returns `True` on success or `False` if absent. |

### HTTP API

[MissionHandler](app/server.py) extends `BaseHTTPRequestHandler` and uses
`send_json(status, data)` to send JSON responses.

| Method | Endpoint | Success response |
| --- | --- | --- |
| `GET` | `/missions` | `200` with the mission array. |
| `GET` | `/missions/active` | `200` with the array of active missions (empty if none are active). |
| `GET` | `/missions/{id}` | `200` with a mission object. |
| `POST` | `/missions` | `201` with the created mission. |
| `DELETE` | `/missions/{id}` | `200` with `{"message": "Mission deleted"}`. |

Example POST body:

```json
{
  "name": "Mars Delta",
  "description": "Explore south pole",
  "priority": "high"
}
```

For POST requests, `name` is required; omitted `description` and `priority`
default to an empty string and `medium`, respectively.

Handled errors use `{"error": "..."}` responses: `400` for invalid input,
`404` for missing missions or unmatched GET/POST endpoints, and `413` when the
declared POST body exceeds 100,000 bytes. Request validation is limited: non-object
JSON is not handled gracefully, and DELETE does not validate the route prefix.

There are no external API dependencies, database connections, authentication,
or mission-update endpoints.

## Unit tests

The tests in [tests/test_missions.py](tests/test_missions.py) use Python's
built-in `unittest` framework. Run them from the project root:

```powershell
python -m unittest discover -s tests -v
```

The tests cover:

- Listing the three initial missions.
- Filtering active missions, including through the tools wrapper, with no-match and empty-list cases.
- Retrieving existing and missing missions.
- Creating a mission with `pending` status.
- Rejecting empty, whitespace-only, and non-string names.
- Rejecting unsupported, incorrectly cased, whitespace-padded, and non-string priorities.
- Ensuring rejected creation attempts leave the mission list unchanged.
- Deleting existing and missing missions.
- Exercising HTTP GET handlers for `/missions`, `/missions/active`, and `/missions/{id}`, including JSON responses and `200` status codes.

Each test restores the original mission list afterward. HTTP handler coverage is
limited to these GET routes; request parsing and other HTTP methods/status codes
are not covered.

## GitHub agent orchestration

[Planner Developer Reviewer](.github/workflows/agent-orchestration.yml) runs the
existing custom agents sequentially with Copilot CLI:

1. A repository writer adds the `agent-approved` label to an open issue.
2. Planner posts its plan on the issue and saves the exact issue snapshot.
3. Planning finishes without starting development.
4. A human repository writer reads the posted plan, waits for the planning run
   to succeed, then adds `plan-approved`. This starts a separate run using the
   immutable plan artifact and source commit from the planning run.
5. Developer implements that plan, then the workflow runs
   `python -m unittest discover -s tests -v`.
6. Reviewer independently assesses the code, plan and test evidence. A failed
   test or `REQUEST_CHANGES` stops publication; inspect the run artifacts.
7. A separate job publishes the reviewed patch as a **draft pull request** using
   the repository PR template. A human must review it; nothing merges or deploys.

### One-time repository setup

- Merge these workflow changes through normal human review. Issue-event
  workflows must exist on the default branch before they can run.
- Create the `agent-approved` and `plan-approved` issue labels. This two-label
  approval mechanism works for private repositories without Enterprise
  environment protection rules. Only human repository writers can approve.
- Add repository Actions secret `COPILOT_GITHUB_TOKEN`: a fine-grained PAT with
  the **Copilot Requests** permission and an eligible Copilot subscription.
  Do not grant this token repository-write permissions.
- Enable **Allow GitHub Actions to create and approve pull requests** in
  **Settings > Actions > General**. This workflow creates drafts, not approvals.

From another agent or GitHub CLI, start orchestration by labeling an issue:

```powershell
gh issue edit 123 --repo shanconsult1987/space-rescue-app --add-label agent-approved
```

After human review of the posted plan and successful planning run:

```powershell
gh issue edit 123 --repo shanconsult1987/space-rescue-app --add-label plan-approved
```

Do not let the initiating agent apply `plan-approved` on the human's behalf.
Only repository writers may trigger the workflow. Issue text is treated as
untrusted requirements. Title/body edits, closing the issue, or removing the
label while approval is pending prevent development from starting. To request
a fresh plan, remove both labels and re-add `agent-approved` after
finishing/cancelling the old run. Runs for the same issue are serialized.
Approval fails explicitly if the plan artifact has expired or planning failed.

Agent jobs do not receive a repository-write token. Publishing runs separately
and does not execute generated code. Automation rejects changes outside `app/`,
`tools/`, `tests/`, `docs/`, `README.md` and `requirements.txt`, as well as changes
to orchestration controls, hidden paths, `AGENTS.md`, symlinks and submodules.
Changes to workflows or agent definitions require a manual PR.
Copilot CLI tool permissions are not an OS sandbox; use this only for trusted,
human-approved work. Agents can read repository content and generated tests run
on the ephemeral runner. Do not put unrelated secrets in these jobs.

Plans, developer reports, test output and reviewer reports are saved as Actions
artifacts for seven days. PRs made with `GITHUB_TOKEN` may not trigger subsequent
CI workflows automatically; a maintainer must explicitly run required CI or use
an approved GitHub App publishing identity. Existing branch protections still
apply.

## License

No license file is currently included in this project. A license has not been
specified; do not assume permission to use, modify, or redistribute the code.