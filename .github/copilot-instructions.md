
# SpaceRescue Repository Instructions

## Project overview

SpaceRescue is a minimal Python application
for managing Mars rover missions.

## Technical constraints

- Python 3.11 or later.
- Prefer Python standard library.
- No FastAPI or Flask.
- No Uvicorn or Gunicorn.
- No database for the core workshop.
- Keep the application simple.

## Coding rules

- Use readable Python functions.
- Keep business logic in app/missions.py.
- Keep HTTP handling in app/server.py.
- Avoid unnecessary abstractions.
- Validate external input.
- Preserve existing API behavior.

## Testing rules

- Use unittest.
- Add tests for every new feature.
- Cover invalid inputs.
- Run:

  python -m unittest discover -s tests -v

## Security rules

- Never commit secrets.
- Never expose API keys.
- Do not disable security workflows.
- Do not bypass repository rulesets.

## Agent rules

- Understand the task before implementation.
- Produce a plan.
- Identify affected files.
- Define acceptance criteria.
- Implement only approved requirements.
- Run tests.
- Report test failures honestly.
- Never merge or deploy automatically.
- Request human review through a pull request.
