# themindfulprojects-agentbookselector

Identifikasi buku mana yang worth di-analyze berdasarkan trending, demand, & engagement potential.

> **Book Selection Agent** for a Literary Analysis YouTube channel — analyses Google Trends data,
> scores books on engagement potential (1–10), and returns a ranked, JSON-formatted recommendation list.

---

## Output schema

```json
{
  "book_title": "Pride and Prejudice",
  "author": "Jane Austen",
  "publication_year": 1813,
  "estimated_search_volume": 5400,
  "relevance_score": 8.5,
  "trending_status": "evergreen_high",
  "why_selected": "Consistent search demand, film/TV adaptation(s) boosting interest, proven evergreen classic",
  "content_angle": "Romance, class dynamics, female agency",
  "estimated_audience": ["students", "literature enthusiasts", "romance fans"],
  "priority_ranking": 1
}
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage

### Command line

```bash
# Top 5 books (default)
python agent.py

# Top 10 books
python agent.py --top 10

# Save to a file
python agent.py --top 5 --output recommendations.json
```

### Programmatic

```python
from agent import BookSelectionAgent

agent = BookSelectionAgent(niche="Literary Analysis", top_n=5)
results = agent.run()   # returns list[dict]
```

---

## Decision framework

| Signal | Priority |
|--------|----------|
| New release trending on Google Trends | **Highest** |
| Classic with upcoming publication anniversary (25-year multiples) | **Elevated** |
| Classic with film / TV adaptation | **High** |
| Evergreen classic with broad audience | **Ongoing pipeline** |

**Constraints**
- ~70 % classics, ~30 % contemporary in every output batch
- Books with film/TV adaptations are preferred (cross-promotion value)
- Overly niche titles (single audience segment) receive a scoring penalty

---

## Scoring weights

| Component | Weight |
|-----------|--------|
| Search volume (Google Trends / base data) | 30 % |
| Adaptation bonus | 20 % |
| Audience breadth | 20 % |
| Goodreads rating | 15 % |
| Anniversary bonus | 10 % |
| Niche penalty | − 5 % |

---

## Running tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Project structure

```
.
├── agent.py          # BookSelectionAgent class + CLI entry point
├── config.py         # Book database, scoring weights, thresholds
├── requirements.txt  # Python dependencies
└── tests/
    └── test_agent.py # Unit tests (38 tests)
```
