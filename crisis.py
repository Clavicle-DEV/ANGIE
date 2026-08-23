"""
A safety layer that sits in front of the AI model. Relying on the model
alone to recognize crisis language and respond appropriately is not
reliable enough for a mental health support app - it can respond well
one turn and inconsistently the next. This module catches clear
self-harm/suicide language with simple pattern matching and returns a
fixed, warm, resource-forward response instead of ever sending that
message to the model.

Resources here (988, Crisis Text Line, Kenya lines) were verified
current as of this writing. If you deploy this for real users, recheck
these periodically - crisis line numbers do change.
"""

import re

# Deliberately kept narrow: explicit statements of suicidal intent or
# self-harm, not just sadness, grief, or hopelessness in general -
# those get a caring, substantive AI response instead, not a hotline
# dump, since that would feel dismissive for ordinary distress.
_PATTERNS = [
    r"\bkill(ing)? myself\b",
    r"\bend(ing)? my life\b",
    r"\bwant(ed)? to die\b",
    r"\bwish(ed)? i (was|were) dead\b",
    r"\bdon'?t want to (live|be alive)\b",
    r"\bno reason to live\b",
    r"\bsuicid(e|al)\b",
    r"\bhurt(ing)? myself\b",
    r"\bself[\s-]?harm\b",
    r"\bcut(ting)? myself\b",
    r"\bbetter off dead\b",
    r"\btake my (own )?life\b",
    r"\bplan to die\b",
    r"\bgoodbye forever\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]


def is_crisis_message(text):
    if not text:
        return False
    return any(p.search(text) for p in _COMPILED)


_RESPONSES = [
    (
        "I'm really glad you told me this, and I want to take it seriously. "
        "What you're feeling right now matters, and you don't have to carry "
        "it alone.\n\n"
        "Please reach out to someone who can support you right now:\n\n"
        "• US: call or text 988 (988 Suicide & Crisis Lifeline), 24/7\n"
        "• US: text HOME to 741741 (Crisis Text Line)\n"
        "• Kenya: call 0800 723 253 (EMKF Suicide Prevention & Crisis Line, "
        "free, 24/7) or +254 722 178 177 (Befrienders Kenya, Mon-Fri 9am-5pm)\n"
        "• Anywhere else: search \"crisis line\" + your country, or contact "
        "your local emergency number\n\n"
        "I'm here to keep talking with you too — you don't have to go "
        "figure this out on your own right this second."
    ),
    (
        "Thank you for saying that out loud instead of keeping it in — that "
        "took something. I'm not able to be the only support for something "
        "this heavy, but I don't want you to be alone with it either.\n\n"
        "Please reach out to one of these, right now if you can:\n\n"
        "• US: call or text 988 (988 Suicide & Crisis Lifeline), 24/7\n"
        "• US: text HOME to 741741 (Crisis Text Line)\n"
        "• Kenya: call 0800 723 253 (EMKF Suicide Prevention & Crisis Line, "
        "free, 24/7) or +254 722 178 177 (Befrienders Kenya, Mon-Fri 9am-5pm)\n"
        "• Anywhere else: search \"crisis line\" + your country\n\n"
        "I'm still here if you want to keep talking while you decide who "
        "else to reach out to."
    ),
]

_counter = {"i": 0}


def crisis_response(last_index=None):
    """
    Rotates between two warm phrasings of the same accurate resources,
    so it doesn't read as a copy-pasted bot reply on repeat triggers.
    Pass the previously-used index (per user session) to avoid an
    immediate repeat; returns (text, index_used).
    """
    index = 0
    if last_index is not None and len(_RESPONSES) > 1:
        index = (last_index + 1) % len(_RESPONSES)
    return _RESPONSES[index], index
