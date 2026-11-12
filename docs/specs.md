# SpaceRescue Technical Specification

## Product

SpaceRescue Mission Control.

## Objective

Manage rover missions and mission status.

## Functional requirements

FR-001: List missions.

FR-002: Retrieve individual missions.

FR-003: Create missions.

FR-004: Delete missions.

FR-005: Retrieve active missions.

FR-006: Filter missions by priority.

## Non-functional requirements

NFR-001: Python 3.11+.

NFR-002: Minimal dependencies.

NFR-003: JSON API responses.

NFR-004: Unit test coverage for core logic.

NFR-005: No credentials in source code.

## Architecture

HTTP Server -> Mission Functions -> In-memory Data.

## Acceptance

All required unit tests must pass.