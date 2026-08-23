import os
import json
from pathlib import Path
from functools import wraps
from datetime import timedelta

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, Response, send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

import database as db
from ai import ask_ai_stream
from crisis import is_crisis_message, crisis_response

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")

# Keep people signed in across visits - sign up / log in once, and the
# session then lasts 90 days (refreshed on every visit) instead of
# ending when the browser closes.
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=90)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

db.initialize_database()

TOPICS = [
    {"title": "General Chat", "icon": "💬"},
    {"title": "Heartbreak Recovery", "icon": "💔"},
    {"title": "Anxiety Relief", "icon": "🧘"},
    {"title": "Stress Management", "icon": "🌿"},
    {"title": "Depression Support", "icon": "❤️"},
    {"title": "Self Confidence", "icon": "⭐"},
    {"title": "Daily Motivation", "icon": "☀️"},
    {"title": "Bible Companion", "icon": "📖"},
    {"title": "Prayer Corner", "icon": "🙏"},
    {"title": "Sleep Better", "icon": "🌙"},
    {"title": "Meditation", "icon": "🌬️"},
    {"title": "Goal Planner", "icon": "🚩"},
    {"title": "Study Coach", "icon": "🎓"},
    {"title": "Career Coach", "icon": "💼"},
    {"title": "Financial Wellness", "icon": "💰"},
    {"title": "Relationships", "icon": "👥"},
    {"title": "Family Support", "icon": "🏠"},
    {"title": "Health Education", "icon": "🩺"},
    {"title": "Psychology", "icon": "🧠"},
    {"title": "Philosophy", "icon": "📚"},
    {"title": "Engineering Wisdom", "icon": "⚙️"},
    {"title": "Science Explorer", "icon": "🔬"},
    {"title": "Inspirational Quotes", "icon": "💡"},
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth"))
        # The session can outlive the actual user record - e.g. if the
        # database was reset (redeploy on a host with an ephemeral
        # filesystem) or the account was deleted. Without this check,
        # every route crashes with a 500 instead of just sending the
        # person back to log in again.
        if db.get_user(session["user_id"]) is None:
            session.clear()
            return redirect(url_for("auth"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return db.get_user(session["user_id"])


# ==========================================================
# AUTH
# ==========================================================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth"))


@app.route("/auth")
def auth():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html")


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not username or not email or len(password) < 6:
        return jsonify(ok=False, error="Please fill all fields (password 6+ characters)."), 400

    if db.get_user_by_email(email):
        return jsonify(ok=False, error="An account with that email already exists."), 400

    if db.get_user_by_username(username):
        return jsonify(ok=False, error="That username is taken."), 400

    user_id = db.create_user(
        username, email, generate_password_hash(password), full_name
    )
    session["user_id"] = user_id
    session.permanent = True
    return jsonify(ok=True)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify(ok=False, error="Incorrect email or password."), 400

    session["user_id"] = user["id"]
    session.permanent = True
    return jsonify(ok=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth"))


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    return render_template("dashboard.html", user=user, topics=TOPICS)


# ==========================================================
# CHAT
# ==========================================================

@app.route("/chat/<topic>")
@login_required
def chat_page(topic):
    user = current_user()
    history = db.load_messages(user["id"], topic)
    return render_template("chat.html", user=user, topic=topic, history=history)


def next_quote(topic):
    """
    Session-based shuffle bag: picks a quote for this topic without
    repeating any quote until every quote in that topic's pool has
    been shown once, then reshuffles. Fixes quotes repeating within
    the same conversation.
    """
    from quotes import QUOTES, TOPIC_CATEGORY
    import random

    category = TOPIC_CATEGORY.get(topic, "general")
    pool = QUOTES.get(category, QUOTES["general"])

    bags = session.get("quote_bags", {})
    bag = bags.get(category)

    if not bag:
        bag = list(range(len(pool)))
        random.shuffle(bag)

    index = bag.pop()
    bags[category] = bag
    session["quote_bags"] = bags
    session.modified = True

    return pool[index]


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    user = current_user()
    data = request.get_json(force=True)
    topic = data.get("topic", "General Chat")
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify(ok=False, error="Empty message."), 400

    db.save_message(user["id"], topic, "user", message)
    history = db.load_messages(user["id"], topic)

    # Crisis language is caught deterministically here, before the
    # message ever reaches the AI model - this does not depend on the
    # model's own judgment, which is not reliable enough on its own
    # for something this important.
    if is_crisis_message(message):
        last_index = session.get("last_crisis_index")
        reply_text, used_index = crisis_response(last_index)
        session["last_crisis_index"] = used_index

        db.save_message(user["id"], topic, "ai", reply_text)

        def generate_crisis():
            yield f"data: {json.dumps({'chunk': reply_text})}\n\n"
            # No encouragement quote here on purpose - a decorative
            # quote card isn't appropriate directly under a crisis
            # resource message.
            yield f"data: {json.dumps({'done': True})}\n\n"

        return Response(generate_crisis(), mimetype="text/event-stream")

    # Compute the quote here, in the actual request context, not
    # inside generate() below - a generator's body doesn't run until
    # it's iterated, which happens after this view function returns
    # and the request context is gone. Session access has to happen
    # out here.
    quote = next_quote(topic)

    def generate():
        full_reply = []
        try:
            for chunk in ask_ai_stream(topic, history[:-1], message):
                full_reply.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        finally:
            reply_text = "".join(full_reply).strip()
            if reply_text:
                db.save_message(user["id"], topic, "ai", reply_text)

            yield f"data: {json.dumps({'quote': quote})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


# ==========================================================
# JOURNAL
# ==========================================================

@app.route("/journal")
@login_required
def journal_page():
    user = current_user()
    entries = db.load_journal_entries(user["id"])
    return render_template("journal.html", user=user, entries=entries)


@app.route("/api/journal", methods=["POST"])
@login_required
def api_journal_save():
    user = current_user()
    data = request.get_json(force=True)
    entry = (data.get("entry") or "").strip()
    if not entry:
        return jsonify(ok=False, error="Write something first."), 400
    db.save_journal_entry(user["id"], entry)
    return jsonify(ok=True)


@app.route("/api/journal/<int:entry_id>", methods=["DELETE"])
@login_required
def api_journal_delete(entry_id):
    user = current_user()
    db.delete_journal_entry(entry_id, user["id"])
    return jsonify(ok=True)


# ==========================================================
# MOOD
# ==========================================================

@app.route("/mood")
@login_required
def mood_page():
    user = current_user()
    moods = db.load_moods(user["id"])
    return render_template("mood.html", user=user, moods=moods)


@app.route("/api/mood", methods=["POST"])
@login_required
def api_mood_save():
    user = current_user()
    data = request.get_json(force=True)
    mood = (data.get("mood") or "").strip()
    if not mood:
        return jsonify(ok=False, error="Pick a mood first."), 400
    db.save_mood(user["id"], mood)
    return jsonify(ok=True)


# ==========================================================
# SETTINGS
# ==========================================================

@app.route("/settings")
@login_required
def settings_page():
    user = current_user()
    return render_template("settings.html", user=user)


@app.route("/api/settings", methods=["POST"])
@login_required
def api_settings_save():
    user = current_user()
    data = request.get_json(force=True)

    db.update_preferences(
        user["id"],
        language=data.get("language", user["language"]),
        voice=data.get("voice", user["voice"]),
        theme=data.get("theme", user["theme"]),
        wallpaper=data.get("wallpaper", user["wallpaper"]),
        voice_reply=int(bool(data.get("voice_reply"))),
        daily_quotes=int(bool(data.get("daily_quotes"))),
        scripture=int(bool(data.get("scripture"))),
        notifications=int(bool(data.get("notifications"))),
    )
    return jsonify(ok=True)


@app.route("/api/settings/clear-history", methods=["POST"])
@login_required
def api_clear_history():
    user = current_user()
    db.delete_all_messages(user["id"])
    return jsonify(ok=True)


@app.route("/api/settings/delete-account", methods=["POST"])
@login_required
def api_delete_account():
    user = current_user()
    db.delete_user(user["id"])
    session.clear()
    return jsonify(ok=True)


# ==========================================================
# PWA
# ==========================================================

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")


@app.route("/offline")
def offline():
    return render_template("offline.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
