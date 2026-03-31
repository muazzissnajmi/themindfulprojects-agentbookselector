"""
Configuration for the Book Selection Agent.
Contains the curated book database and scoring weights.
"""

# ---------------------------------------------------------------------------
# Scoring weights (must sum to 1.0)
# ---------------------------------------------------------------------------
SCORING_WEIGHTS = {
    "search_volume": 0.30,   # Normalised Google Trends score
    "adaptation_bonus": 0.20,  # +1 if film/TV adaptation exists
    "audience_breadth": 0.20,  # How broad the target audience is
    "goodreads_rating": 0.15,  # Goodreads average rating (normalised)
    "anniversary_bonus": 0.10,  # Publication-anniversary boost
    "niche_penalty": 0.05,    # Penalty for overly niche content
}

# ---------------------------------------------------------------------------
# Book database
# 70 % classics, 30 % contemporary — as per the brief.
# Fields:
#   title, author, year, category ("classic" | "contemporary"),
#   genres, adaptations (list of adaptation titles, empty = none),
#   goodreads_rating (float out of 5), estimated_audience (list),
#   content_angle (str), base_search_volume (monthly searches, int)
# ---------------------------------------------------------------------------
BOOK_DATABASE = [
    # ── CLASSICS (70 %) ────────────────────────────────────────────────────
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": 1813,
        "category": "classic",
        "genres": ["romance", "literary fiction", "social commentary"],
        "adaptations": [
            "Pride & Prejudice (2005 film)",
            "Pride and Prejudice (1995 BBC series)",
        ],
        "goodreads_rating": 4.28,
        "estimated_audience": ["students", "literature enthusiasts", "romance fans"],
        "content_angle": "Romance, class dynamics, female agency",
        "base_search_volume": 5400,
    },
    {
        "title": "Jane Eyre",
        "author": "Charlotte Brontë",
        "year": 1847,
        "category": "classic",
        "genres": ["gothic fiction", "bildungsroman", "romance"],
        "adaptations": [
            "Jane Eyre (2011 film)",
            "Jane Eyre (2006 BBC series)",
        ],
        "goodreads_rating": 4.13,
        "estimated_audience": ["students", "literature enthusiasts", "gothic fiction fans"],
        "content_angle": "Female independence, gothic atmosphere, moral growth",
        "base_search_volume": 4900,
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "category": "classic",
        "genres": ["dystopian fiction", "political fiction", "science fiction"],
        "adaptations": ["Nineteen Eighty-Four (1984 film)"],
        "goodreads_rating": 4.19,
        "estimated_audience": ["students", "political readers", "sci-fi fans", "general public"],
        "content_angle": "Totalitarianism, surveillance, language as control",
        "base_search_volume": 12000,
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "year": 1960,
        "category": "classic",
        "genres": ["southern gothic", "bildungsroman", "legal drama"],
        "adaptations": ["To Kill a Mockingbird (1962 film)"],
        "goodreads_rating": 4.27,
        "estimated_audience": ["students", "history buffs", "social justice readers"],
        "content_angle": "Racial injustice, moral courage, loss of innocence",
        "base_search_volume": 8100,
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "category": "classic",
        "genres": ["literary fiction", "social commentary", "tragedy"],
        "adaptations": [
            "The Great Gatsby (2013 film)",
            "The Great Gatsby (1974 film)",
        ],
        "goodreads_rating": 3.93,
        "estimated_audience": ["students", "literature enthusiasts", "history buffs"],
        "content_angle": "American Dream, wealth, illusion vs reality",
        "base_search_volume": 9900,
    },
    {
        "title": "Hamlet",
        "author": "William Shakespeare",
        "year": 1603,
        "category": "classic",
        "genres": ["tragedy", "drama", "philosophical fiction"],
        "adaptations": [
            "Hamlet (1996 film)",
            "Hamlet (2009 RSC production)",
        ],
        "goodreads_rating": 4.02,
        "estimated_audience": ["students", "theatre fans", "philosophy readers"],
        "content_angle": "Revenge, mortality, indecision, madness",
        "base_search_volume": 7400,
    },
    {
        "title": "Wuthering Heights",
        "author": "Emily Brontë",
        "year": 1847,
        "category": "classic",
        "genres": ["gothic fiction", "romance", "tragedy"],
        "adaptations": ["Wuthering Heights (2011 film)"],
        "goodreads_rating": 3.87,
        "estimated_audience": ["literature enthusiasts", "romance fans", "gothic fiction fans"],
        "content_angle": "Obsessive love, class struggle, revenge",
        "base_search_volume": 3600,
    },
    {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "year": 1866,
        "category": "classic",
        "genres": ["psychological fiction", "philosophical novel", "crime fiction"],
        "adaptations": [],
        "goodreads_rating": 4.23,
        "estimated_audience": ["students", "philosophy readers", "literary fiction fans"],
        "content_angle": "Guilt, redemption, psychology of crime",
        "base_search_volume": 4400,
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "year": 1932,
        "category": "classic",
        "genres": ["dystopian fiction", "science fiction", "satire"],
        "adaptations": ["Brave New World (2020 TV series)"],
        "goodreads_rating": 3.99,
        "estimated_audience": ["students", "sci-fi fans", "political readers"],
        "content_angle": "Consumerism, freedom vs stability, dehumanisation",
        "base_search_volume": 5900,
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "year": 1951,
        "category": "classic",
        "genres": ["literary fiction", "coming-of-age"],
        "adaptations": [],
        "goodreads_rating": 3.81,
        "estimated_audience": ["students", "young adults", "literature enthusiasts"],
        "content_angle": "Adolescent alienation, identity, phoniness",
        "base_search_volume": 6600,
    },
    {
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "year": 1818,
        "category": "classic",
        "genres": ["gothic fiction", "science fiction", "horror"],
        "adaptations": [
            "Frankenstein (1931 film)",
            "Victor Frankenstein (2015 film)",
        ],
        "goodreads_rating": 3.97,
        "estimated_audience": ["students", "sci-fi fans", "horror fans", "literature enthusiasts"],
        "content_angle": "Creation vs creator, scientific ethics, monstrosity",
        "base_search_volume": 6800,
    },
    {
        "title": "Anna Karenina",
        "author": "Leo Tolstoy",
        "year": 1878,
        "category": "classic",
        "genres": ["literary fiction", "romance", "tragedy"],
        "adaptations": ["Anna Karenina (2012 film)"],
        "goodreads_rating": 4.03,
        "estimated_audience": ["literature enthusiasts", "romance fans", "history buffs"],
        "content_angle": "Love, society, moral hypocrisy",
        "base_search_volume": 3200,
    },
    {
        "title": "The Odyssey",
        "author": "Homer",
        "year": -800,
        "category": "classic",
        "genres": ["epic poetry", "mythology", "adventure"],
        "adaptations": [
            "O Brother, Where Art Thou? (2000 film)",
            "Ulysses (1967 film)",
        ],
        "goodreads_rating": 3.77,
        "estimated_audience": ["students", "mythology fans", "literature enthusiasts"],
        "content_angle": "Heroic journey, identity, homecoming",
        "base_search_volume": 5100,
    },
    # ── CONTEMPORARY (30 %) ────────────────────────────────────────────────
    {
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "year": 2020,
        "category": "contemporary",
        "genres": ["literary fiction", "fantasy", "self-help fiction"],
        "adaptations": [],
        "goodreads_rating": 3.98,
        "estimated_audience": ["general public", "self-help readers", "fantasy fans"],
        "content_angle": "Regret, alternate lives, mental health",
        "base_search_volume": 8100,
    },
    {
        "title": "Normal People",
        "author": "Sally Rooney",
        "year": 2018,
        "category": "contemporary",
        "genres": ["literary fiction", "romance", "coming-of-age"],
        "adaptations": ["Normal People (2020 Hulu/BBC series)"],
        "goodreads_rating": 3.87,
        "estimated_audience": ["young adults", "romance fans", "literary fiction fans"],
        "content_angle": "Modern relationships, class, vulnerability",
        "base_search_volume": 9900,
    },
    {
        "title": "Fourth Wing",
        "author": "Rebecca Yarros",
        "year": 2023,
        "category": "contemporary",
        "genres": ["fantasy", "romance", "new adult"],
        "adaptations": [],
        "goodreads_rating": 4.56,
        "estimated_audience": ["young adults", "fantasy fans", "romance fans"],
        "content_angle": "Power, destiny, enemies-to-lovers romance",
        "base_search_volume": 22000,
    },
    {
        "title": "Tomorrow, and Tomorrow, and Tomorrow",
        "author": "Gabrielle Zevin",
        "year": 2022,
        "category": "contemporary",
        "genres": ["literary fiction", "friendship", "creative industry"],
        "adaptations": [],
        "goodreads_rating": 4.23,
        "estimated_audience": ["gamers", "young adults", "literary fiction fans"],
        "content_angle": "Creativity, friendship, ambition, failure",
        "base_search_volume": 6500,
    },
    {
        "title": "Lessons in Chemistry",
        "author": "Bonnie Garmus",
        "year": 2022,
        "category": "contemporary",
        "genres": ["historical fiction", "feminist fiction", "humor"],
        "adaptations": ["Lessons in Chemistry (2023 Apple TV+ series)"],
        "goodreads_rating": 4.33,
        "estimated_audience": ["general public", "feminist readers", "history buffs"],
        "content_angle": "Female empowerment, science, 1960s society",
        "base_search_volume": 9200,
    },
    {
        "title": "Intermezzo",
        "author": "Sally Rooney",
        "year": 2024,
        "category": "contemporary",
        "genres": ["literary fiction", "family drama"],
        "adaptations": [],
        "goodreads_rating": 3.72,
        "estimated_audience": ["literary fiction fans", "Sally Rooney fans"],
        "content_angle": "Grief, siblings, unconventional relationships",
        "base_search_volume": 7800,
    },
]

# ---------------------------------------------------------------------------
# Trending status thresholds (based on normalised score 0–10)
# ---------------------------------------------------------------------------
TRENDING_STATUS_THRESHOLDS = {
    "trending_viral": 9.0,
    "trending_high": 7.5,
    "evergreen_high": 6.5,
    "evergreen_medium": 5.0,
    "evergreen_low": 3.0,
    "niche": 0.0,
}

# Maximum monthly search volume in the database (used for normalisation)
MAX_SEARCH_VOLUME = 22000
