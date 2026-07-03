"""
HomePilot AI — API Endpoint Tests

Tests for all FastAPI endpoints using httpx TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data

    def test_health_returns_app_name(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["app_name"] == "HomePilot AI"


class TestSearchEndpoint:
    """Tests for the /api/search endpoint."""

    def test_search_all(self):
        response = client.post("/api/search", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_count"] > 0
        assert len(data["properties"]) > 0

    def test_search_by_city(self):
        response = client.post("/api/search", json={"city": "Mumbai"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] > 0
        for prop in data["properties"]:
            assert prop["city"] == "Mumbai"

    def test_search_by_budget(self):
        response = client.post("/api/search", json={"budget_max": 8000000})
        assert response.status_code == 200
        data = response.json()
        for prop in data["properties"]:
            assert prop["price"] <= 8000000

    def test_search_by_bedrooms(self):
        response = client.post("/api/search", json={"bedrooms": 2})
        assert response.status_code == 200
        data = response.json()
        for prop in data["properties"]:
            assert prop["bedrooms"] == 2

    def test_search_no_results(self):
        response = client.post("/api/search", json={"city": "Atlantis"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0

    def test_search_response_has_required_fields(self):
        response = client.post("/api/search", json={"city": "Bangalore"})
        data = response.json()
        if data["total_count"] > 0:
            prop = data["properties"][0]
            assert "id" in prop
            assert "title" in prop
            assert "price" in prop
            assert "formatted_price" in prop
            assert "bedrooms" in prop


class TestPropertyDetailEndpoint:
    """Tests for the /api/property/{id} endpoint."""

    def test_get_existing_property(self):
        response = client.get("/api/property/prop-mum-001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["property"]["id"] == "prop-mum-001"

    def test_get_nonexistent_property(self):
        response = client.get("/api/property/nonexistent")
        assert response.status_code == 404

    def test_property_detail_has_fields(self):
        response = client.get("/api/property/prop-blr-001")
        data = response.json()
        prop = data["property"]
        assert "title" in prop
        assert "price" in prop
        assert "city" in prop
        assert "bedrooms" in prop
        assert "amenities" in prop


class TestHistoryEndpoint:
    """Tests for the /api/history/{id} endpoint."""

    def test_get_history(self):
        response = client.get("/api/history/prop-mum-001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["price_history"]) > 0
        assert data["appreciation_rate"] is not None

    def test_history_nonexistent(self):
        response = client.get("/api/history/nonexistent")
        assert response.status_code == 404


class TestPropertiesListEndpoint:
    """Tests for the /api/properties endpoint."""

    def test_list_all_properties(self):
        response = client.get("/api/properties")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 30
        assert len(data["properties"]) >= 30

    def test_list_properties_have_images(self):
        response = client.get("/api/properties")
        data = response.json()
        for prop in data["properties"]:
            assert "image_url" in prop
