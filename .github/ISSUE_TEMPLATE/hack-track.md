---
name: Hack track task
about: One task for a CPH Agentic Hack track (created by you or by @architect)
title: "[track] <short task title>"
labels: ["hack"]
---

## Track
<!-- onboarding | flights | disruptions | gates | assistant -->

## Track guide
<!-- Link to the guide, e.g. docs/track-2-flight-plans.md -->

## Goal
<!-- One sentence: what this task delivers. -->

## Endpoints
<!-- Method, path, query parameters and response model, e.g.
GET /api/flights?direction=DEP&from=&to= -> list[FlightOut]
File: src/backend/app/routers/flights.py -->

## UI visualisation
<!-- What appears where, e.g. great-circle routes on the map + departures board in
src/frontend/tracks/flights.js; KPI tile "Departures next hour". -->

## Assistant tool(s) to expose
<!-- Copilot SDK tool name, parameters and what it returns, e.g. get_flights(direction, hours). -->

## Diagram
<!-- Optional: link to docs/diagrams/<track>-flow.drawio -->

## Acceptance criteria
- [ ] Endpoint returns data (no 501) and is listed at /docs
- [ ] Tests added; endpoint removed from STUBS in src/backend/tests/test_stubs.py; `pytest` passes
- [ ] UI shows the visualisation using theme.css variables only (no hard-coded colours)
- [ ] Status colours have text labels; keyboard and screen-reader friendly
- [ ] Matching HACK(<track>) markers removed
- [ ] Synthetic data only
