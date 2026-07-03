"""
HomePilot AI — Tool Unit Tests

Tests for all six tools: property search, google maps, school,
crime, price history, and neighborhood.
"""

import pytest
from tools.property_search import property_search, get_property_by_id, get_all_properties
from tools.google_maps import google_maps_tool
from tools.school_tool import school_tool
from tools.crime_tool import crime_tool
from tools.price_history import price_history_tool
from tools.neighborhood import neighborhood_tool


# ── Property Search Tests ────────────────────────────────────────────────────


class TestPropertySearch:
    """Tests for the property_search tool."""

    def test_search_all_returns_results(self):
        result = property_search.invoke({})
        assert result["total_count"] > 0
        assert len(result["properties"]) > 0

    def test_search_by_city(self):
        result = property_search.invoke({"city": "Mumbai"})
        assert result["total_count"] > 0
        for prop in result["properties"]:
            assert prop["city"] == "Mumbai"

    def test_search_by_bedrooms(self):
        result = property_search.invoke({"bedrooms": 3})
        assert result["total_count"] > 0
        for prop in result["properties"]:
            assert prop["bedrooms"] == 3

    def test_search_by_budget(self):
        result = property_search.invoke({
            "budget_max": 10000000,  # 1 crore
        })
        for prop in result["properties"]:
            assert prop["price"] <= 10000000

    def test_search_by_budget_range(self):
        result = property_search.invoke({
            "budget_min": 5000000,
            "budget_max": 10000000,
        })
        for prop in result["properties"]:
            assert 5000000 <= prop["price"] <= 10000000

    def test_search_combined_filters(self):
        result = property_search.invoke({
            "city": "Bangalore",
            "bedrooms": 3,
            "budget_max": 20000000,
        })
        for prop in result["properties"]:
            assert prop["city"] == "Bangalore"
            assert prop["bedrooms"] == 3
            assert prop["price"] <= 20000000

    def test_search_no_results(self):
        result = property_search.invoke({
            "city": "NonexistentCity",
        })
        assert result["total_count"] == 0

    def test_search_has_formatted_price(self):
        result = property_search.invoke({"city": "Mumbai"})
        for prop in result["properties"]:
            assert "formatted_price" in prop
            assert "₹" in prop["formatted_price"]

    def test_get_property_by_id(self):
        prop = get_property_by_id("prop-mum-001")
        assert prop is not None
        assert prop["id"] == "prop-mum-001"
        assert prop["city"] == "Mumbai"

    def test_get_property_by_id_not_found(self):
        prop = get_property_by_id("nonexistent-id")
        assert prop is None

    def test_get_all_properties_count(self):
        all_props = get_all_properties()
        assert len(all_props) >= 30  # At least 30 as specified

    def test_all_properties_have_required_fields(self):
        all_props = get_all_properties()
        required = ["id", "title", "price", "city", "locality", "bedrooms", "bathrooms", "area_sqft"]
        for prop in all_props:
            for field in required:
                assert field in prop, f"Missing field '{field}' in property {prop.get('id', 'unknown')}"


# ── Google Maps Tool Tests ───────────────────────────────────────────────────


class TestGoogleMapsTool:
    """Tests for the google_maps_tool."""

    def test_known_locality(self):
        result = google_maps_tool.invoke({"locality": "Andheri West", "city": "Mumbai"})
        assert "commute_time_min" in result
        assert "nearest_metro" in result
        assert "metro_distance_km" in result
        assert result["metro_distance_km"] > 0

    def test_unknown_locality_returns_defaults(self):
        result = google_maps_tool.invoke({"locality": "UnknownPlace", "city": "TestCity"})
        assert "commute_time_min" in result
        assert "nearest_metro" in result

    def test_nearby_facilities(self):
        result = google_maps_tool.invoke({"locality": "Koramangala"})
        assert "nearby_hospitals" in result
        assert "nearby_shopping" in result
        assert len(result["nearby_hospitals"]) > 0


# ── School Tool Tests ────────────────────────────────────────────────────────


class TestSchoolTool:
    """Tests for the school_tool."""

    def test_known_locality(self):
        result = school_tool.invoke({"locality": "Powai", "city": "Mumbai"})
        assert "nearby_schools" in result
        assert result["school_count"] > 0
        assert result["average_rating"] > 0

    def test_schools_have_ratings(self):
        result = school_tool.invoke({"locality": "Whitefield"})
        for school in result["nearby_schools"]:
            assert "rating" in school
            assert "distance_km" in school
            assert 0 <= school["rating"] <= 10

    def test_best_school(self):
        result = school_tool.invoke({"locality": "Koramangala"})
        assert result["best_school"] is not None
        assert result["best_school"]["rating"] >= result["average_rating"]


# ── Crime Tool Tests ─────────────────────────────────────────────────────────


class TestCrimeTool:
    """Tests for the crime_tool."""

    def test_known_locality(self):
        result = crime_tool.invoke({"locality": "Powai", "city": "Mumbai"})
        assert "safety_score" in result
        assert "crime_index" in result
        assert 0 <= result["safety_score"] <= 100
        assert 0 <= result["crime_index"] <= 100

    def test_safety_and_crime_inverse(self):
        result = crime_tool.invoke({"locality": "Jubilee Hills"})
        assert result["safety_score"] + result["crime_index"] == 100

    def test_crime_types(self):
        result = crime_tool.invoke({"locality": "Andheri West"})
        assert "crime_types" in result
        assert "theft" in result["crime_types"]


# ── Price History Tool Tests ─────────────────────────────────────────────────


class TestPriceHistoryTool:
    """Tests for the price_history_tool."""

    def test_returns_history(self):
        result = price_history_tool.invoke({
            "property_id": "prop-mum-001",
            "current_price": 15000000,
            "locality": "Andheri West",
        })
        assert "price_history" in result
        assert len(result["price_history"]) > 0
        assert "appreciation_rate_annual" in result

    def test_history_chronological(self):
        result = price_history_tool.invoke({
            "property_id": "test",
            "current_price": 10000000,
            "locality": "Powai",
        })
        history = result["price_history"]
        # Prices should generally increase over time
        assert history[-1]["price"] >= history[0]["price"]

    def test_appreciation_positive(self):
        result = price_history_tool.invoke({
            "property_id": "test",
            "current_price": 10000000,
            "locality": "Gachibowli",
        })
        assert result["appreciation_rate_annual"] > 0
        assert result["total_appreciation_5y"] > 0


# ── Neighborhood Tool Tests ──────────────────────────────────────────────────


class TestNeighborhoodTool:
    """Tests for the neighborhood_tool."""

    def test_known_locality(self):
        result = neighborhood_tool.invoke({"locality": "Koramangala", "city": "Bangalore"})
        assert "parks" in result
        assert "restaurants" in result
        assert "supermarkets" in result
        assert "walkability_score" in result

    def test_walkability_range(self):
        result = neighborhood_tool.invoke({"locality": "Indiranagar"})
        assert 0 <= result["walkability_score"] <= 100

    def test_counts(self):
        result = neighborhood_tool.invoke({"locality": "Koregaon Park"})
        assert result["parks_count"] >= 0
        assert result["restaurants_count"] >= 0
        assert result["supermarkets_count"] >= 0
