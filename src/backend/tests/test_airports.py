"""Tests for the reference endpoint. Copy this style for your track's endpoints."""

from fastapi.testclient import TestClient


def test_list_airports_returns_cph_with_coordinates(client: TestClient) -> None:
    response = client.get("/api/airports")

    assert response.status_code == 200
    airports = response.json()
    assert len(airports) >= 40
    cph = next(a for a in airports if a["iata"] == "CPH")
    assert cph["lat"] == 55.6179
    assert cph["lon"] == 12.656


def test_get_airport_is_case_insensitive(client: TestClient) -> None:
    response = client.get("/api/airports/fra")

    assert response.status_code == 200
    assert response.json()["city"] == "Frankfurt"


def test_get_unknown_airport_returns_404(client: TestClient) -> None:
    response = client.get("/api/airports/XXX")

    assert response.status_code == 404
