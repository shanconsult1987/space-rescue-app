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
| `get_mission(mission_id)` | Returns a matching mission, or `None`. |
| `create_mission(name, description, priority="medium")` | Validates the name and priority, appends a pending mission, and returns it. Raises `ValueError` for invalid input. |
| `delete_mission(mission_id)` | Removes a matching mission; returns `True` on success or `False` if absent. |

### HTTP API

[MissionHandler](app/server.py) extends `BaseHTTPRequestHandler` and uses
`send_json(status, data)` to send JSON responses.

| Method | Endpoint | Success response |
| --- | --- | --- |
| `GET` | `/missions` | `200` with the mission array. |
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

The eight tests in [tests/test_missions.py](tests/test_missions.py) use Python's
built-in `unittest` framework. Run them from the project root:

```powershell
python -m unittest discover -s tests -v
```

The tests cover:

- Listing the three initial missions.
- Retrieving existing and missing missions.
- Creating a mission with `pending` status.
- Rejecting empty, whitespace-only, and non-string names.
- Rejecting unsupported, incorrectly cased, whitespace-padded, and non-string priorities.
- Ensuring rejected creation attempts leave the mission list unchanged.
- Deleting existing and missing missions.

Each test restores the original mission list afterward. The existing suite does
not test the HTTP handlers, request parsing, or response status codes.

## License

No license file is currently included in this project. A license has not been
specified; do not assume permission to use, modify, or redistribute the code.