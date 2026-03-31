"""
Book Selection Agent for a Literary Analysis YouTube channel.

Analyses Google Trends data, applies engagement scoring, and returns a
ranked list of book recommendations in the schema required by the brief.

Usage
-----
    python agent.py [--niche "Literary Analysis"] [--top N] [--output file.json]

or import and use programmatically:

    from agent import BookSelectionAgent
    agent = BookSelectionAgent()
    results = agent.run()
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Any

from config import (
    BOOK_DATABASE,
    MAX_SEARCH_VOLUME,
    SCORING_WEIGHTS,
    TRENDING_STATUS_THRESHOLDS,
)

try:
    from pytrends.request import TrendReq
    _PYTRENDS_AVAILABLE = True
except ImportError:
    _PYTRENDS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(value: float, max_value: float) -> float:
    """Return *value* normalised to the range [0, 1]."""
    if max_value == 0:
        return 0.0
    return min(value / max_value, 1.0)


def _trending_status(score: float) -> str:
    """Map a composite score (0–10) to a human-readable trending status."""
    for status, threshold in TRENDING_STATUS_THRESHOLDS.items():
        if score >= threshold:
            return status
    return "niche"


def _is_anniversary_year(publication_year: int, current_year: int) -> bool:
    """Return True if *current_year* is a round anniversary of *publication_year*."""
    if publication_year <= 0:
        return False
    age = current_year - publication_year
    return age > 0 and age % 25 == 0


# ---------------------------------------------------------------------------
# Google Trends integration
# ---------------------------------------------------------------------------

def fetch_google_trends(book_titles: list[str]) -> dict[str, float]:
    """
    Return a mapping of {book_title: trends_score (0–100)} using pytrends.

    Falls back to the base_search_volume from the database when pytrends is
    unavailable or the request fails.
    """
    if not _PYTRENDS_AVAILABLE:
        return {}

    results: dict[str, float] = {}
    pytrends = TrendReq(hl="en-US", tz=0)

    # Google Trends allows at most 5 keywords per request
    batch_size = 5
    for i in range(0, len(book_titles), batch_size):
        batch = book_titles[i : i + batch_size]
        try:
            pytrends.build_payload(batch, timeframe="today 12-m")
            interest = pytrends.interest_over_time()
            if interest.empty:
                continue
            for title in batch:
                if title in interest.columns:
                    results[title] = float(interest[title].mean())
        except Exception:  # noqa: BLE001
            pass

    return results


# ---------------------------------------------------------------------------
# Core agent
# ---------------------------------------------------------------------------

class BookSelectionAgent:
    """
    Selects and ranks books for a Literary Analysis YouTube channel.

    Decision framework
    ------------------
    - New releases that are trending  → highest priority
    - Classics on a publication anniversary → elevated priority
    - Evergreen classics               → steady pipeline

    Constraints
    -----------
    - Prefer books with film/TV adaptations (cross-promotion value)
    - Avoid overly niche titles (need a broad audience)
    - Balance: ~70 % classics, ~30 % contemporary
    """

    def __init__(
        self,
        niche: str = "Literary Analysis",
        top_n: int = 5,
        current_date: date | None = None,
    ) -> None:
        self.niche = niche
        self.top_n = top_n
        self.current_date = current_date or date.today()
        self._books = BOOK_DATABASE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> list[dict[str, Any]]:
        """
        Run the full selection pipeline and return a ranked list of dicts
        matching the required JSON schema.
        """
        trends_map = fetch_google_trends([b["title"] for b in self._books])
        scored = [self._score_book(book, trends_map) for book in self._books]
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Enforce balance: ~70 % classics, ~30 % contemporary from top_n
        balanced = self._balance(scored)
        return [self._format(rank, book) for rank, book in enumerate(balanced, start=1)]

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_book(
        self, book: dict[str, Any], trends_map: dict[str, float]
    ) -> dict[str, Any]:
        """Compute a composite relevance score (1–10) for a single book."""
        weights = SCORING_WEIGHTS
        current_year = self.current_date.year

        # 1. Search-volume component (0–1)
        if book["title"] in trends_map:
            # Google Trends returns 0–100; normalise to 0–1
            sv_score = _normalise(trends_map[book["title"]], 100.0)
        else:
            sv_score = _normalise(book["base_search_volume"], MAX_SEARCH_VOLUME)

        # 2. Adaptation bonus (0 or 1)
        adaptation_score = 1.0 if book["adaptations"] else 0.0

        # 3. Audience-breadth score (0–1): more audience segments = broader
        audience_score = min(len(book["estimated_audience"]) / 5.0, 1.0)

        # 4. Goodreads rating component (0–1); scale 0–5 → 0–1
        gr_score = _normalise(book["goodreads_rating"], 5.0)

        # 5. Anniversary bonus (0 or 1)
        anniversary_score = (
            1.0 if _is_anniversary_year(book["year"], current_year) else 0.0
        )

        # 6. Niche penalty: if only one audience segment listed (too niche)
        niche_penalty = 1.0 if len(book["estimated_audience"]) <= 1 else 0.0

        raw = (
            weights["search_volume"] * sv_score
            + weights["adaptation_bonus"] * adaptation_score
            + weights["audience_breadth"] * audience_score
            + weights["goodreads_rating"] * gr_score
            + weights["anniversary_bonus"] * anniversary_score
            - weights["niche_penalty"] * niche_penalty
        )

        # Map to 1–10 range; raw is between ~0 and 1
        relevance_score = round(max(1.0, min(10.0, raw * 10.0)), 2)

        estimated_search_volume = (
            int(trends_map.get(book["title"], 0) * MAX_SEARCH_VOLUME / 100)
            if book["title"] in trends_map
            else book["base_search_volume"]
        )

        return {
            **book,
            "relevance_score": relevance_score,
            "estimated_search_volume": estimated_search_volume,
            "trending_status": _trending_status(relevance_score),
        }

    # ------------------------------------------------------------------
    # Balancing
    # ------------------------------------------------------------------

    def _balance(self, scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Return *top_n* books respecting the 70/30 classic/contemporary split.
        If not enough books of a category exist, fill up with the other.
        """
        n_contemporary = max(1, round(self.top_n * 0.30))
        n_classics = self.top_n - n_contemporary

        classics = [b for b in scored if b["category"] == "classic"]
        contemporary = [b for b in scored if b["category"] == "contemporary"]

        selected: list[dict[str, Any]] = []
        selected.extend(classics[:n_classics])
        selected.extend(contemporary[:n_contemporary])

        # If either pool is short, fill from the other
        deficit = self.top_n - len(selected)
        if deficit > 0:
            remaining = [b for b in scored if b not in selected]
            selected.extend(remaining[:deficit])

        # Re-sort the balanced selection by relevance score
        selected.sort(key=lambda x: x["relevance_score"], reverse=True)
        return selected[: self.top_n]

    # ------------------------------------------------------------------
    # Output formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format(rank: int, book: dict[str, Any]) -> dict[str, Any]:
        """Produce the required output schema for a single book."""
        return {
            "book_title": book["title"],
            "author": book["author"],
            "publication_year": book["year"],
            "estimated_search_volume": book["estimated_search_volume"],
            "relevance_score": book["relevance_score"],
            "trending_status": book["trending_status"],
            "why_selected": _build_why_selected(book),
            "content_angle": book["content_angle"],
            "estimated_audience": book["estimated_audience"],
            "priority_ranking": rank,
        }


# ---------------------------------------------------------------------------
# Why-selected narrative builder
# ---------------------------------------------------------------------------

def _build_why_selected(book: dict[str, Any]) -> str:
    """Compose a short human-readable explanation for selecting a book."""
    reasons: list[str] = []

    if book["base_search_volume"] >= 8000:
        reasons.append("High consistent search demand")
    elif book["base_search_volume"] >= 4000:
        reasons.append("Consistent search demand")
    else:
        reasons.append("Steady niche search demand")

    if book["adaptations"]:
        reasons.append(f"film/TV adaptation(s) boosting interest")

    if book["category"] == "classic":
        reasons.append("proven evergreen classic")
    else:
        reasons.append("popular contemporary release")

    if book["goodreads_rating"] >= 4.2:
        reasons.append("highly rated on Goodreads")

    return ", ".join(reasons).capitalize()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Book Selection Agent for Literary Analysis YouTube channel"
    )
    parser.add_argument(
        "--niche",
        default="Literary Analysis",
        help="Target niche (default: 'Literary Analysis')",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Number of books to return (default: 5)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write JSON output to FILE instead of stdout",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    agent = BookSelectionAgent(niche=args.niche, top_n=args.top)
    results = agent.run()
    output = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main(sys.argv[1:])
