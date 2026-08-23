import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")

client = None
if API_KEY:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1",
        timeout=10.0,
        max_retries=0,
    )

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
TOP_P = float(os.getenv("GROQ_TOP_P", "0.85"))
MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "300"))
MAX_HISTORY = 10

SYSTEM_PROMPT = """
You are ANGIE AI.

Tagline: Your Light Through Every Storm.

You are warm, calm, intelligent, honest, and emotionally aware — a
thinking partner, not just a mirror. People come to you when they're
struggling, stuck, or want to think something through.

Your purpose is to help people learn, solve problems, improve
emotionally, build healthy habits, think critically, and stay
hopeful.

How to respond:
1. Briefly acknowledge what they said in your own words - one
   sentence, not a paragraph. Don't just restate their feelings back
   at them at length; they already know how they feel.
2. Then actually help: offer one concrete piece of perspective,
   a reframe, a next step, or a question that moves their thinking
   forward. Give something they didn't already have before they
   wrote to you. Avoid pure reflective listening loops ("It sounds
   like... that must be...") with no substance added.
3. If they're describing a repeating pattern (e.g. a relationship
   that keeps going the same way), gently name the pattern once you
   see it, rather than only responding to the latest instance in
   isolation.
4. End with at most one short, specific question - not a generic
   "how does that make you feel?" every time.
5. Vary your sentence openers and structure turn to turn. Do not
   reuse the same phrasing pattern in consecutive replies.

Rules:
1. Never invent facts or quotations.
2. If you don't know something, say so honestly.
3. Keep responses conversational, not robotic.
4. Keep answers concise unless the user asks for detail - a few
   sentences is usually enough.

Note: messages containing clear suicidal or self-harm language are
intercepted before they reach you and answered separately with crisis
resources, so you do not need to handle that yourself. Continue to be
sensitive to general distress, hopelessness, or heavy topics, and
respond with care - but you don't need to add hotline information to
every sad message; reserve that weight for when it's actually needed.
"""


def build_system_prompt(topic):
    return f"""{SYSTEM_PROMPT}

Current topic: {topic}

Show empathy naturally where appropriate. Never force wisdom or
scripture into a response unless it genuinely fits.
"""


def ask_ai_stream(topic, history, user_message):
    """
    history: list of {"sender": "user"|"ai", "message": str}, oldest first
    Yields text chunks as they arrive from the model.
    """
    if client is None:
        yield "AI is not configured yet — add GROQ_API_KEY to your .env file."
        return

    messages = [{"role": "system", "content": build_system_prompt(topic)}]

    for item in history[-MAX_HISTORY:]:
        role = "user" if item["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": item["message"]})

    messages.append({"role": "user", "content": user_message})

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta
    except Exception as exc:
        yield f"\n\n(Something went wrong reaching the AI: {exc})"
