# Civil Career Portal

A focused, Taiwan-first static job portal for civil engineering, sustainable construction materials, and applied R&D roles across nearby Asian markets.

## MVP scope

- Separate academic and industry match profiles
- Taiwan search in Traditional Chinese and English; English search elsewhere
- Academic, Research Institute, and Industry categories
- Transparent weighted scores: location 30%, research/technical 30%, skills 20%, career level 10%, language 5%, company priority 5%
- Location, category, and minimum-score filters
- Original posting language and official URL, with an English aid for Chinese postings
- New labels, last-updated metadata, and browser-local favorites
- No account, notifications, external AI API, or broader career-intelligence features

## Run locally

Serve the repository root (opening `index.html` directly will not load JSON):

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Update jobs

`scripts/update_jobs.py` checks the official pages in `sources.json`. Taiwan sources use Traditional Chinese and English keywords; other markets use English keywords. Automatically discovered links preserve their source title and official URL.

The GitHub Actions workflow checks for updates once every hour. Favorites remain in each visitor's browser `localStorage`.
