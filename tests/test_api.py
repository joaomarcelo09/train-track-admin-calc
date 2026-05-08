import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestSimulationAPI:
    """Tests for the /simulate endpoint."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_simulate_endpoint_success(self, client):
        payload = {
            "train": {"weight": 2000, "train_cars": 12},
            "line": {"total_length": 12000},
            "tracks": [{"length": 500, "bending": 5, "elevation": 100}]
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "total_energy" in data
        assert "average_energy" in data
        assert "points" in data
        assert len(data["points"]) == 1

    def test_simulate_endpoint_multiple_tracks(self, client):
        payload = {
            "train": {"weight": 2000, "train_cars": 12},
            "line": {"total_length": 12000},
            "tracks": [
                {"length": 500, "bending": 5, "elevation": 100},
                {"length": 300, "bending": 10, "elevation": 50}
            ]
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["points"]) == 2
        assert data["points"][1]["distance"] == 800

    def test_simulate_invalid_input(self, client):
        payload = {
            "train": {"weight": -100, "train_cars": 12},
            "line": {"total_length": 12000},
            "tracks": [{"length": 500, "bending": 5, "elevation": 100}]
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_response_structure(self, client):
        payload = {
            "train": {"weight": 2000, "train_cars": 12},
            "line": {"total_length": 500},
            "tracks": [{"length": 500, "bending": 5, "elevation": 100}]
        }
        response = client.post("/simulate", json=payload)
        data = response.json()
        point = data["points"][0]
        assert point["track_index"] == 0
        assert point["distance"] == 500
        assert point["electricity_usage"] > 0
        assert point["track"]["length"] == 500
        assert point["track"]["bending"] == 5
        assert point["track"]["elevation"] == 100
