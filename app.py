
import os, json
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, send_file
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key-change-me")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "recipes.json")

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.before_request
def set_lang():
    session.setdefault("es", False)
    g.es = session.get("es", False)
    session.setdefault("favorites", [])
    session.setdefault("new_recipes", [])

@app.post("/toggle-lang")
def toggle_lang():
    session["es"] = not session.get("es", False)
    nxt = request.form.get("next") or url_for("index")
    return redirect(nxt)

@app.get("/")
def index():
    data = load_data()
    all_tags = sorted({t for r in data for t in r.get("tags", [])})
    return render_template("index.html", recipes=data, all_tags=all_tags)

@app.get("/recipe/<rid>")
def recipe_detail(rid):
    data = load_data()
    rec = next((r for r in data if r["id"] == rid), None)
    if not rec:
        flash("Recipe not found.")
        return redirect(url_for("index"))
    is_fav = rid in session.get("favorites", [])
    return render_template("recipe.html", r=rec, is_fav=is_fav)

@app.post("/favorite/<rid>")
def toggle_favorite(rid):
    favs = set(session.get("favorites", []))
    if rid in favs:
        favs.remove(rid); msg = "Removed from favorites." if not g.es else "Quitado de favoritos."
    else:
        favs.add(rid); msg = "Added to favorites!" if not g.es else "¡Añadido a favoritos!"
    session["favorites"] = list(favs)
    flash(msg)
    return redirect(request.referrer or url_for("recipe_detail", rid=rid))

@app.get("/favorites")
def favorites():
    data = load_data()
    ids = set(session.get("favorites", []))
    recipes = [r for r in data if r["id"] in ids]
    return render_template("favorites.html", recipes=recipes)

@app.get("/search")
def search():
    data = load_data()
    q = (request.args.get("q") or "").lower().strip()
    tag = request.args.get("tag") or "Any"
    max_time = int(request.args.get("max_time") or 60)
    all_tags = sorted({t for r in data for t in r.get("tags", [])})
    results = None
    if "q" in request.args or "tag" in request.args or "max_time" in request.args:
        results = []
        for r in data:
            hay = " ".join([
                r["title_en"], r["title_es"],
                " ".join(r["ingredients_en"]), " ".join(r["ingredients_es"]),
                " ".join(r["tags"]),
            ]).lower()
            if q and q not in hay: continue
            if r.get("time_minutes", 0) > max_time: continue
            if tag != "Any" and tag not in r.get("tags", []): continue
            results.append(r)
    return render_template("search.html", results=results, q=q, tag=tag, max_time=max_time, all_tags=all_tags)

@app.route("/add", methods=["GET","POST"])
def add_recipe():
    if request.method == "POST":
        form = request.form
        item = {
            "id": form.get("id","").strip(),
            "title_en": form.get("title_en","").strip(),
            "title_es": (form.get("title_es","") or form.get("title_en","")).strip(),
            "level": form.get("level","Basic"),
            "time_minutes": int(form.get("time_minutes") or 30),
            "servings": int(form.get("servings") or 2),
            "tags": [t.strip() for t in (form.get("tags","")).split(",") if t.strip()],
            "hero_image": "",
            "ingredients_en": [l.strip() for l in (form.get("ingredients_en","")).splitlines() if l.strip()],
            "ingredients_es": [l.strip() for l in (form.get("ingredients_es","")).splitlines() if l.strip()],
            "steps_en": [l.strip() for l in (form.get("steps_en","")).splitlines() if l.strip()],
            "steps_es": [l.strip() for l in (form.get("steps_es","")).splitlines() if l.strip()],
        }
        session["new_recipes"].append(item)
        from flask import jsonify
        # Keep in session; let user export to file
        flash("Added to session. Export to save.")
        return redirect(url_for("add_recipe"))
    return render_template("add.html")

@app.post("/export")
def export_data():
    data = load_data()
    merged = data + session.get("new_recipes", [])
    from io import BytesIO
    buf = BytesIO()
    buf.write(json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8"))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="recipes.json", mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
