"""
HomePilot AI — Ranking Service Tests

Tests for the weighted scoring algorithm, weight normalization,
and dynamic weight adjustment.
"""

import pytest
from models.schemas import RankingWeights
from services.ranking_service import (
    compute_property_scores,
    adjust_weights_from_priorities,
    _calculate_budget_score,
    _calculate_commute_score,
    _calculate_safety_score,
    _calculate_data_completeness,
)


def _make_property(**overrides):
    """Create a test property dict with defaults."""
    base = {
        "id": "test-001",
        "title": "Test Property",
        "price": 10000000,
        "city": "Mumbai",
        "locality": "Andheri West",
        "address": "Test Address",
        "latitude": 19.0,
        "longitude": 72.8,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1200,
        "amenities": ["Gym", "Pool", "Parking"],
        "school_rating": 8.0,
        "crime_score": 75,
        "metro_distance_km": 1.0,
        "commute_time_min": 30,
        "walkability_score": 70,
        "appreciation_rate": 8.5,
        "parks_nearby": 2,
        "restaurants_nearby": 5,
        "supermarkets_nearby": 3,
    }
    base.update(overrides)
    return base


class TestRankingWeights:
    """Tests for RankingWeights normalization."""

    def test_default_weights_sum_to_one(self):
        w = RankingWeights()
        total = w.budget_match + w.commute + w.school + w.safety + w.amenities
        assert abs(total - 1.0) < 0.001

    def test_normalize_preserves_proportions(self):
        w = RankingWeights(budget_match=0.6, commute=0.4, school=0.4, safety=0.3, amenities=0.3)
        n = w.normalize()
        total = n.budget_match + n.commute + n.school + n.safety + n.amenities
        assert abs(total - 1.0) < 0.001

    def test_normalize_zero_weight_stays_zero(self):
        w = RankingWeights(budget_match=0.3, commute=0.2, school=0.0, safety=0.3, amenities=0.2)
        n = w.normalize()
        assert n.school == 0.0
        total = n.budget_match + n.commute + n.school + n.safety + n.amenities
        assert abs(total - 1.0) < 0.001

    def test_normalize_all_zero_resets_to_default(self):
        w = RankingWeights(budget_match=0, commute=0, school=0, safety=0, amenities=0)
        n = w.normalize()
        total = n.budget_match + n.commute + n.school + n.safety + n.amenities
        assert abs(total - 1.0) < 0.001


class TestPropertyScoring:
    """Tests for compute_property_scores."""

    def test_single_property_gets_score(self):
        prop = _make_property()
        weights = RankingWeights()
        ranked = compute_property_scores([prop], weights, {"budget_max": 15000000})
        assert len(ranked) == 1
        assert "overall_score" in ranked[0]
        assert 0 <= ranked[0]["overall_score"] <= 100

    def test_properties_ranked_by_score(self):
        props = [
            _make_property(id="a", price=8000000, crime_score=90, school_rating=9.0),
            _make_property(id="b", price=14000000, crime_score=50, school_rating=5.0),
        ]
        weights = RankingWeights()
        ranked = compute_property_scores(props, weights, {"budget_max": 10000000})
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2
        assert ranked[0]["overall_score"] >= ranked[1]["overall_score"]

    def test_empty_properties_returns_empty(self):
        result = compute_property_scores([], RankingWeights())
        assert result == []

    def test_score_breakdown_has_all_factors(self):
        prop = _make_property()
        ranked = compute_property_scores([prop], RankingWeights(), {"budget_max": 15000000})
        breakdown = ranked[0]["score_breakdown"]
        assert "budget_match" in breakdown
        assert "commute" in breakdown
        assert "school" in breakdown
        assert "safety" in breakdown
        assert "amenities" in breakdown

    def test_confidence_increases_with_data(self):
        prop_full = _make_property()
        prop_sparse = _make_property(
            id="sparse",
            school_rating=None,
            crime_score=None,
            metro_distance_km=None,
            walkability_score=None,
        )
        ranked = compute_property_scores(
            [prop_full, prop_sparse],
            RankingWeights(),
            {"budget_max": 15000000},
        )
        full_conf = next(p for p in ranked if p["id"] == "test-001")["confidence"]
        sparse_conf = next(p for p in ranked if p["id"] == "sparse")["confidence"]
        assert full_conf > sparse_conf


class TestBudgetScore:
    """Tests for budget matching logic."""

    def test_under_budget_scores_high(self):
        prop = {"price": 8000000}
        prefs = {"budget_max": 10000000}
        score = _calculate_budget_score(prop, prefs)
        assert score > 0.7

    def test_over_budget_scores_low(self):
        prop = {"price": 20000000}
        prefs = {"budget_max": 10000000}
        score = _calculate_budget_score(prop, prefs)
        assert score < 0.5

    def test_no_budget_neutral_score(self):
        prop = {"price": 10000000}
        prefs = {}
        score = _calculate_budget_score(prop, prefs)
        assert score == 0.7


class TestWeightAdjustment:
    """Tests for dynamic weight adjustment from priorities."""

    def test_safety_priority_increases_safety_weight(self):
        w = RankingWeights()
        adjusted = adjust_weights_from_priorities(w, ["safest neighborhood"])
        # After normalization, safety should be the dominant weight
        assert adjusted.safety >= 0.25
        assert adjusted.safety > w.safety

    def test_school_priority_increases_school_weight(self):
        w = RankingWeights()
        adjusted = adjust_weights_from_priorities(w, ["good schools", "family friendly"])
        assert adjusted.school >= 0.25
        assert adjusted.school > w.school

    def test_budget_priority_increases_budget_weight(self):
        w = RankingWeights()
        adjusted = adjust_weights_from_priorities(w, ["affordable", "best value"])
        assert adjusted.budget_match >= 0.30
        assert adjusted.budget_match > w.budget_match

    def test_adjusted_weights_sum_to_one(self):
        w = RankingWeights()
        adjusted = adjust_weights_from_priorities(w, ["safe", "good schools"])
        total = adjusted.budget_match + adjusted.commute + adjusted.school + adjusted.safety + adjusted.amenities
        assert abs(total - 1.0) < 0.001


class TestDataCompleteness:
    """Tests for data completeness calculation."""

    def test_full_data(self):
        prop = _make_property()
        completeness = _calculate_data_completeness(prop)
        assert completeness == 1.0

    def test_no_data(self):
        prop = {"id": "test"}
        completeness = _calculate_data_completeness(prop)
        assert completeness == 0.0
