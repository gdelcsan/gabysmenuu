# Gaby's Menu — Flask Website

A Python/Flask cooking website with dark theme and gold accents (logo included).

## Features
- Home feed with recipe cards
- Search across titles, ingredients, and tags
- Tag filter + max time slider (input)
- ES/EN language toggle (session)
- Favorites (session)
- Recipe details with shareable URL
- Add Recipe form (adds to session) and **Export** updated `recipes.json`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # set FLASK_SECRET_KEY
python app.py              # http://127.0.0.1:5000
```

## Deploy (Render example)
- Start command: `gunicorn app:app`

## Structure
```
app.py
data/recipes.json
static/
  logo.png
  style.css
templates/
  base.html index.html recipe.html search.html favorites.html add.html
```

