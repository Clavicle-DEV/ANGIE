"""
A curated bank of short encouragements from historical figures across
philosophy, science, medicine, and engineering — plus scripture —
organized by the kind of situation someone might be in. One is
attached after each AI answer, matched to the current topic.

Every quote here is a well-documented historical statement (public
domain / widely attributed), not sourced from any single copyrighted
compilation.
"""

import random

QUOTES = {

    "anxiety": [
        {"text": "Nothing in life is to be feared, it is only to be understood.", "author": "Marie Curie"},
        {"text": "We suffer more often in imagination than in reality.", "author": "Seneca"},
        {"text": "Fear thou not; for I am with thee: be not dismayed; for I am thy God.", "author": "Isaiah 41:10"},
        {"text": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche"},
    ],

    "grief": [
        {"text": "The word 'happiness' would lose its meaning if it were not balanced by sadness.", "author": "Carl Jung"},
        {"text": "Weeping may endure for a night, but joy cometh in the morning.", "author": "Psalm 30:5"},
        {"text": "What we have once enjoyed we can never lose; all that we love deeply becomes a part of us.", "author": "Helen Keller"},
        {"text": "Grief is the price we pay for love.", "author": "Queen Elizabeth II"},
        {"text": "The pain passes, but the beauty remains.", "author": "Pierre-Auguste Renoir"},
        {"text": "Everything that has a beginning has an ending. Make your peace with that and all will be well.", "author": "Buddha"},
    ],

    "stress": [
        {"text": "It is not the man who has too little, but the man who craves more, that is poor.", "author": "Seneca"},
        {"text": "Cast thy burden upon the LORD, and he shall sustain thee.", "author": "Psalm 55:22"},
        {"text": "Nature does not hurry, yet everything is accomplished.", "author": "Lao Tzu"},
        {"text": "The greatest weapon against stress is our ability to choose one thought over another.", "author": "William James"},
    ],

    "depression": [
        {"text": "That which does not kill us makes us stronger.", "author": "Friedrich Nietzsche"},
        {"text": "He healeth the broken in heart, and bindeth up their wounds.", "author": "Psalm 147:3"},
        {"text": "Even a happy life cannot be without a measure of darkness.", "author": "Carl Jung"},
        {"text": "The wound is the place where the Light enters you.", "author": "Rumi"},
    ],

    "confidence": [
        {"text": "No one can make you feel inferior without your consent.", "author": "Eleanor Roosevelt"},
        {"text": "I can do all things through Christ which strengtheneth me.", "author": "Philippians 4:13"},
        {"text": "Whether you think you can, or you think you can't, you're right.", "author": "Henry Ford"},
        {"text": "Know thyself.", "author": "Socrates"},
    ],

    "motivation": [
        {"text": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
        {"text": "Let us run with patience the race that is set before us.", "author": "Hebrews 12:1"},
        {"text": "Genius is one percent inspiration and ninety-nine percent perspiration.", "author": "Thomas Edison"},
        {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
        {"text": "Our greatest glory is not in never falling, but in rising every time we fall.", "author": "Confucius"},
    ],

    "faith": [
        {"text": "Trust in the LORD with all thine heart; and lean not unto thine own understanding.", "author": "Proverbs 3:5"},
        {"text": "Now faith is the substance of things hoped for, the evidence of things not seen.", "author": "Hebrews 11:1"},
        {"text": "Science without religion is lame, religion without science is blind.", "author": "Albert Einstein"},
        {"text": "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil.", "author": "Jeremiah 29:11"},
    ],

    "sleep_calm": [
        {"text": "Thou wilt keep him in perfect peace, whose mind is stayed on thee.", "author": "Isaiah 26:3"},
        {"text": "The quieter you become, the more you are able to hear.", "author": "Rumi"},
        {"text": "Silence is a source of great strength.", "author": "Lao Tzu"},
        {"text": "Peace I leave with you, my peace I give unto you: let not your heart be troubled.", "author": "John 14:27"},
    ],

    "goals": [
        {"text": "A goal is a dream with a deadline.", "author": "Napoleon Hill"},
        {"text": "Commit thy way unto the LORD; trust also in him; and he shall bring it to pass.", "author": "Psalm 37:5"},
        {"text": "By failing to prepare, you are preparing to fail.", "author": "Benjamin Franklin"},
        {"text": "The unexamined life is not worth living.", "author": "Socrates"},
    ],

    "study": [
        {"text": "The more that you read, the more things you will know.", "author": "Aristotle"},
        {"text": "I am always doing that which I cannot do, in order that I may learn how to do it.", "author": "Pablo Picasso"},
        {"text": "Study without desire spoils the memory, and it retains nothing that it takes in.", "author": "Leonardo da Vinci"},
        {"text": "Get wisdom, get understanding: forget it not.", "author": "Proverbs 4:5"},
    ],

    "career": [
        {"text": "Choose a job you love, and you will never have to work a day in your life.", "author": "Confucius"},
        {"text": "Whatsoever thy hand findeth to do, do it with thy might.", "author": "Ecclesiastes 9:10"},
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin"},
    ],

    "financial": [
        {"text": "Wealth consists not in having great possessions, but in having few wants.", "author": "Epictetus"},
        {"text": "Commit thy works unto the LORD, and thy thoughts shall be established.", "author": "Proverbs 16:3"},
        {"text": "Do not save what is left after spending, but spend what is left after saving.", "author": "Benjamin Franklin"},
        {"text": "It's not your salary that makes you rich, it's your spending habits.", "author": "Charles A. Jaffe"},
    ],

    "relationships": [
        {"text": "Love is composed of a single soul inhabiting two bodies.", "author": "Aristotle"},
        {"text": "There is no fear in love; but perfect love casteth out fear.", "author": "1 John 4:18"},
        {"text": "The greatest gift that you can give to others is the gift of unconditional love and acceptance.", "author": "Brian Tracy"},
        {"text": "Where there is love there is life.", "author": "Mahatma Gandhi"},
    ],

    "family": [
        {"text": "The strength of a family, like the strength of an army, lies in its loyalty to each other.", "author": "Mario Puzo"},
        {"text": "Honour thy father and thy mother.", "author": "Exodus 20:12"},
        {"text": "In a family, love and forgiveness should be normal practice.", "author": "Desmond Tutu"},
        {"text": "The family is one of nature's masterpieces.", "author": "George Santayana"},
    ],

    "health": [
        {"text": "The natural healing force within each of us is the greatest force in getting well.", "author": "Hippocrates"},
        {"text": "He that loveth pureness of heart... the king shall be his friend.", "author": "Proverbs 22:11"},
        {"text": "Prevention is better than cure.", "author": "Desiderius Erasmus"},
        {"text": "Wear the old coat and buy the new book.", "author": "William Osler"},
    ],

    "psychology": [
        {"text": "Until you make the unconscious conscious, it will direct your life and you will call it fate.", "author": "Carl Jung"},
        {"text": "Between stimulus and response there is a space. In that space is our power to choose our response.", "author": "Viktor Frankl"},
        {"text": "The mind is everything. What you think you become.", "author": "Buddha"},
    ],

    "philosophy": [
        {"text": "The unexamined life is not worth living.", "author": "Socrates"},
        {"text": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche"},
        {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Aristotle"},
        {"text": "Man is not worried by real problems so much as by his imagined anxieties about real problems.", "author": "Epictetus"},
    ],

    "engineering": [
        {"text": "Scientists study the world as it is; engineers create the world that has never been.", "author": "Theodore von Karman"},
        {"text": "The engineer has been, and is, a maker of history.", "author": "James Kip Finch"},
        {"text": "Design is not just what it looks like and feels like. Design is how it works.", "author": "Steve Jobs"},
    ],

    "science": [
        {"text": "Somewhere, something incredible is waiting to be known.", "author": "Carl Sagan"},
        {"text": "Nothing in life is to be feared, it is only to be understood.", "author": "Marie Curie"},
        {"text": "The important thing is not to stop questioning.", "author": "Albert Einstein"},
        {"text": "Study hard what interests you the most in the most undisciplined, irreverent and original manner possible.", "author": "Richard Feynman"},
    ],

    "general": [
        {"text": "This is the day which the LORD hath made; we will rejoice and be glad in it.", "author": "Psalm 118:24"},
        {"text": "Turn your wounds into wisdom.", "author": "Oprah Winfrey"},
        {"text": "Do the best you can until you know better. Then when you know better, do better.", "author": "Maya Angelou"},
        {"text": "And we know that all things work together for good to them that love God.", "author": "Romans 8:28"},
        {"text": "The only true wisdom is in knowing you know nothing.", "author": "Socrates"},
    ],
}

# Map each app topic to the closest quote category above.
TOPIC_CATEGORY = {
    "Heartbreak Recovery": "grief",
    "Anxiety Relief": "anxiety",
    "Stress Management": "stress",
    "Depression Support": "depression",
    "Self Confidence": "confidence",
    "Daily Motivation": "motivation",
    "Bible Companion": "faith",
    "Prayer Corner": "faith",
    "Sleep Better": "sleep_calm",
    "Meditation": "sleep_calm",
    "Goal Planner": "goals",
    "Study Coach": "study",
    "Career Coach": "career",
    "Financial Wellness": "financial",
    "Relationships": "relationships",
    "Family Support": "family",
    "Health Education": "health",
    "Psychology": "psychology",
    "Philosophy": "philosophy",
    "Engineering Wisdom": "engineering",
    "Science Explorer": "science",
    "Inspirational Quotes": "general",
    "General Chat": "general",
    "Voice Companion": "general",
}


def pick_encouragement(topic, exclude_text=None):
    """
    Returns one {"text":..., "author":...} matched to the topic.
    Avoids repeating exclude_text twice in a row where possible.
    """
    category = TOPIC_CATEGORY.get(topic, "general")
    pool = list(QUOTES.get(category, QUOTES["general"]))

    if exclude_text:
        filtered = [q for q in pool if q["text"] != exclude_text]
        if filtered:
            pool = filtered

    return random.choice(pool)
