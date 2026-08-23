(function () {
  const el = document.getElementById("welcome-greeting");
  if (!el) return;

  const name = el.dataset.name || "";
  const suffix = name ? `, ${name}` : "";

  const hour = new Date().getHours();

  // Each bucket has several distinct phrasings (not just "Good X") so the
  // greeting doesn't feel repetitive across visits at the same time of day.
  const BUCKETS = [
    {
      test: (h) => h >= 4 && h < 7,
      lines: [
        "Up before the sun",
        "The world's still quiet",
        "First light",
        "An early start",
        "Rise and shine",
      ],
    },
    {
      test: (h) => h >= 7 && h < 12,
      lines: [
        "Good morning",
        "Hope your morning's off to a good start",
        "New day, clean slate",
        "Morning",
        "Here's to a good morning",
        "Ready when you are",
      ],
    },
    {
      test: (h) => h >= 12 && h < 14,
      lines: [
        "Good afternoon",
        "Midday check-in",
        "Halfway through the day",
        "Hope the day's treating you well",
      ],
    },
    {
      test: (h) => h >= 14 && h < 17,
      lines: [
        "Good afternoon",
        "Afternoon",
        "Hope your day's going smoothly",
        "Good to see you this afternoon",
      ],
    },
    {
      test: (h) => h >= 17 && h < 20,
      lines: [
        "Good evening",
        "Evening",
        "Hope your day treated you kindly",
        "Winding down for the evening",
        "Glad you're here this evening",
      ],
    },
    {
      test: (h) => h >= 20 && h < 23,
      lines: [
        "Good evening",
        "Settling in for the night",
        "Hope today went okay",
        "Evening check-in",
      ],
    },
    {
      test: (h) => h >= 23 || h < 2,
      lines: [
        "Still up",
        "Burning the midnight oil",
        "Late night check-in",
        "Here for you, even now",
        "Can't sleep? I'm here",
      ],
    },
    {
      test: (h) => h >= 2 && h < 4,
      lines: [
        "Wide awake at this hour",
        "The quiet hours",
        "Middle of the night",
        "I'm here, whatever the hour",
      ],
    },
  ];

  const bucket = BUCKETS.find((b) => b.test(hour)) || BUCKETS[1];
  const line = bucket.lines[Math.floor(Math.random() * bucket.lines.length)];

  el.textContent = `${line}${suffix}`;
})();
