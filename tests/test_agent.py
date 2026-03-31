"""
Unit tests for the Book Selection Agent.
"""

import json
from datetime import date
from unittest.mock import patch

import pytest

from agent import (
    BookSelectionAgent,
    _build_why_selected,
    _is_anniversary_year,
    _normalise,
    _trending_status,
)
from config import BOOK_DATABASE, SCORING_WEIGHTS


# ---------------------------------------------------------------------------
# Helper / utility tests
# ---------------------------------------------------------------------------

class TestNormalise:
    def test_zero_max_returns_zero(self):
        assert _normalise(100, 0) == 0.0

    def test_value_above_max_is_clamped_to_one(self):
        assert _normalise(200, 100) == 1.0

    def test_half_value_returns_half(self):
        assert _normalise(50, 100) == 0.5

    def test_zero_value_returns_zero(self):
        assert _normalise(0, 100) == 0.0


class TestTrendingStatus:
    def test_viral_threshold(self):
        assert _trending_status(9.5) == "trending_viral"

    def test_high_threshold(self):
        assert _trending_status(8.0) == "trending_high"

    def test_evergreen_high_threshold(self):
        assert _trending_status(7.0) == "evergreen_high"

    def test_evergreen_medium_threshold(self):
        assert _trending_status(5.5) == "evergreen_medium"

    def test_evergreen_low_threshold(self):
        assert _trending_status(4.0) == "evergreen_low"

    def test_niche_threshold(self):
        assert _trending_status(1.0) == "niche"


class TestIsAnniversaryYear:
    def test_25_year_anniversary(self):
        assert _is_anniversary_year(2000, 2025) is True

    def test_50_year_anniversary(self):
        assert _is_anniversary_year(1975, 2025) is True

    def test_100_year_anniversary(self):
        assert _is_anniversary_year(1925, 2025) is True

    def test_non_anniversary(self):
        assert _is_anniversary_year(1813, 2025) is False

    def test_zero_age_returns_false(self):
        assert _is_anniversary_year(2025, 2025) is False

    def test_bc_year_returns_false(self):
        assert _is_anniversary_year(-800, 2025) is False


# ---------------------------------------------------------------------------
# Output schema tests
# ---------------------------------------------------------------------------

class TestOutputSchema:
    """Verify that every item in the output matches the required JSON schema."""

    REQUIRED_KEYS = {
        "book_title",
        "author",
        "publication_year",
        "estimated_search_volume",
        "relevance_score",
        "trending_status",
        "why_selected",
        "content_angle",
        "estimated_audience",
        "priority_ranking",
    }

    def setup_method(self):
        with patch("agent.fetch_google_trends", return_value={}):
            self.agent = BookSelectionAgent(top_n=5, current_date=date(2025, 1, 1))
            self.results = self.agent.run()

    def test_returns_correct_number_of_books(self):
        assert len(self.results) == 5

    def test_all_required_keys_present(self):
        for item in self.results:
            assert self.REQUIRED_KEYS.issubset(item.keys()), (
                f"Missing keys in: {item}"
            )

    def test_relevance_score_in_range(self):
        for item in self.results:
            assert 1.0 <= item["relevance_score"] <= 10.0, (
                f"Score out of range: {item['relevance_score']}"
            )

    def test_priority_ranking_is_sequential(self):
        rankings = [item["priority_ranking"] for item in self.results]
        assert rankings == list(range(1, len(self.results) + 1))

    def test_priority_ranking_ordered_by_score(self):
        scores = [item["relevance_score"] for item in self.results]
        assert scores == sorted(scores, reverse=True)

    def test_estimated_search_volume_is_positive_int(self):
        for item in self.results:
            assert isinstance(item["estimated_search_volume"], int)
            assert item["estimated_search_volume"] > 0

    def test_estimated_audience_is_list(self):
        for item in self.results:
            assert isinstance(item["estimated_audience"], list)
            assert len(item["estimated_audience"]) > 0

    def test_output_is_json_serialisable(self):
        try:
            json.dumps(self.results)
        except (TypeError, ValueError) as exc:
            pytest.fail(f"Output is not JSON serialisable: {exc}")

    def test_publication_year_is_int(self):
        for item in self.results:
            assert isinstance(item["publication_year"], int)

    def test_trending_status_is_valid_string(self):
        valid_statuses = {
            "trending_viral",
            "trending_high",
            "evergreen_high",
            "evergreen_medium",
            "evergreen_low",
            "niche",
        }
        for item in self.results:
            assert item["trending_status"] in valid_statuses, (
                f"Unknown status: {item['trending_status']}"
            )


# ---------------------------------------------------------------------------
# Balance constraint tests
# ---------------------------------------------------------------------------

class TestBalanceConstraint:
    """The agent must return ~70 % classics and ~30 % contemporary."""

    def _run(self, top_n: int) -> list[dict]:
        with patch("agent.fetch_google_trends", return_value={}):
            agent = BookSelectionAgent(top_n=top_n, current_date=date(2025, 1, 1))
            return agent.run()

    def _get_category_counts(self, results: list[dict]) -> tuple[int, int]:
        title_to_category = {b["title"]: b["category"] for b in BOOK_DATABASE}
        n_classic = sum(
            1 for r in results if title_to_category.get(r["book_title"]) == "classic"
        )
        n_contemporary = len(results) - n_classic
        return n_classic, n_contemporary

    def test_top_5_has_at_least_one_contemporary(self):
        results = self._run(top_n=5)
        _, n_contemporary = self._get_category_counts(results)
        assert n_contemporary >= 1

    def test_top_5_has_at_least_three_classics(self):
        results = self._run(top_n=5)
        n_classic, _ = self._get_category_counts(results)
        assert n_classic >= 3

    def test_top_10_has_at_least_two_contemporary(self):
        results = self._run(top_n=10)
        _, n_contemporary = self._get_category_counts(results)
        assert n_contemporary >= 2


# ---------------------------------------------------------------------------
# Google Trends integration tests
# ---------------------------------------------------------------------------

class TestGoogleTrendsIntegration:
    """When pytrends is available the score should reflect the trends data."""

    def test_trends_data_updates_score(self):
        fake_trends = {"1984": 95.0, "Pride and Prejudice": 50.0}
        agent = BookSelectionAgent(top_n=5, current_date=date(2025, 1, 1))

        with patch("agent.fetch_google_trends", return_value=fake_trends):
            results = agent.run()

        # "1984" should appear in the results (it has the highest trends score)
        titles = [r["book_title"] for r in results]
        assert "1984" in titles

    def test_fallback_to_base_volume_when_no_trends(self):
        agent = BookSelectionAgent(top_n=5, current_date=date(2025, 1, 1))

        with patch("agent.fetch_google_trends", return_value={}):
            results = agent.run()

        # All results should have positive search volumes (from base data)
        for item in results:
            assert item["estimated_search_volume"] > 0


# ---------------------------------------------------------------------------
# Why-selected narrative test
# ---------------------------------------------------------------------------

class TestBuildWhySelected:
    def _make_book(self, **overrides) -> dict:
        base = {
            "title": "Test Book",
            "category": "classic",
            "adaptations": [],
            "goodreads_rating": 4.0,
            "base_search_volume": 5000,
            "estimated_audience": ["students"],
            "relevance_score": 7.0,
            "estimated_search_volume": 5000,
            "trending_status": "evergreen_high",
        }
        base.update(overrides)
        return base

    def test_high_search_volume_mentioned(self):
        book = self._make_book(base_search_volume=10000)
        why = _build_why_selected(book)
        assert "high" in why.lower()

    def test_adaptation_mentioned(self):
        book = self._make_book(adaptations=["Some Film (2020)"])
        why = _build_why_selected(book)
        assert "adaptation" in why.lower()

    def test_contemporary_label(self):
        book = self._make_book(category="contemporary")
        why = _build_why_selected(book)
        assert "contemporary" in why.lower()

    def test_classic_label(self):
        book = self._make_book(category="classic")
        why = _build_why_selected(book)
        assert "classic" in why.lower()

    def test_result_is_non_empty_string(self):
        book = self._make_book()
        assert isinstance(_build_why_selected(book), str)
        assert len(_build_why_selected(book)) > 0


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_returns_valid_json_to_stdout(self, capsys):
        from agent import main
        with patch("agent.fetch_google_trends", return_value={}):
            main(["--top", "3"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_cli_writes_to_file(self, tmp_path):
        from agent import main
        output_file = tmp_path / "output.json"
        with patch("agent.fetch_google_trends", return_value={}):
            main(["--top", "3", "--output", str(output_file)])
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert len(data) == 3
