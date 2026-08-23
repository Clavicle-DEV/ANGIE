(function () {
  const fab = document.getElementById("voice-fab");
  const overlay = document.getElementById("voice-overlay");
  const closeBtn = document.getElementById("voice-close");
  const orb = document.getElementById("voice-orb");
  const statusEl = document.getElementById("voice-status");
  const transcriptEl = document.getElementById("voice-transcript");
  const unsupportedEl = document.getElementById("voice-unsupported");
  const fallbackCloseBtn = document.getElementById("voice-fallback-close");

  if (!fab || !overlay) return;

  const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
  const speechSupported = !!SpeechRecognitionCtor && "speechSynthesis" in window;

  const GREETING = "What can I help you about? Feel free to talk to me.";
  const VOICE_TOPIC = "Voice Companion";
  const VOICE_PREF = (document.body.dataset.voicePref || "female").toLowerCase();

  // Common name fragments used by browsers/OSes for their built-in voices.
  const FEMALE_HINTS = [
    "female", "zira", "samantha", "victoria", "susan", "karen", "tessa",
    "moira", "fiona", "hazel", "salli", "joanna", "kendra", "kimberly",
    "amy", "emma", "ava", "serena", "allison", "sara",
  ];
  const MALE_HINTS = [
    "male", "david", "mark", "daniel", "alex", "fred", "james", "george",
    "matthew", "justin", "brian", "eric", "guy", "ryan", "arthur",
  ];

  let cachedVoice = null;

  function pickVoice() {
    const voices = window.speechSynthesis.getVoices();
    if (!voices.length) return null;

    const hints = VOICE_PREF === "male" ? MALE_HINTS : FEMALE_HINTS;

    // Locale tags whose voices tend to sound noticeably different from
    // US/UK English. Some devices only ship one of these as their sole
    // "English" voice - if that's genuinely all that's available it's
    // still used (last tier below), but only as a last resort, never
    // picked over a real en-US/en-GB voice or a recognizable standard
    // voice name.
    const AVOID_LOCALES = ["en-in", "en-za", "en-ng", "en-ph", "en-sg", "en-hk", "en-ke"];

    // Specific, very common voice names for US/UK English across major
    // platforms (Android's Google TTS, Windows, macOS/iOS, Chrome/Edge).
    // Matching on these directly is more reliable than locale tags
    // alone, since some devices mislabel or omit locale info entirely
    // but still use one of these well-known engines.
    const US_UK_NAMES = [
      "google us english", "google uk english", "microsoft david",
      "microsoft zira", "microsoft mark", "samantha", "alex", "victoria",
      "daniel", "karen", "moira", "tessa", "fiona", "arthur", "serena",
    ];

    const lang = (v) => (v.lang || "").toLowerCase();
    const name = (v) => (v.name || "").toLowerCase();

    const enUS = voices.filter((v) => lang(v) === "en-us");
    const enGB = voices.filter((v) => lang(v) === "en-gb");
    const knownGoodName = voices.filter((v) => US_UK_NAMES.some((n) => name(v).includes(n)));
    const anyEnNotAvoided = voices.filter(
      (v) => lang(v).startsWith("en") && !AVOID_LOCALES.includes(lang(v))
    );
    const anyEn = voices.filter((v) => lang(v).startsWith("en"));

    // Tiered fallback - each tier is only used if every tier before it
    // is completely empty on this device.
    const tiers = [enUS, enGB, knownGoodName, anyEnNotAvoided, anyEn, voices];

    for (const tier of tiers) {
      if (!tier.length) continue;
      const byHint = tier.find((v) => hints.some((hint) => name(v).includes(hint)));
      if (byHint) return byHint;
    }

    for (const tier of tiers) {
      if (tier.length) return tier[0];
    }

    return null;
  }

  function ensureVoiceLoaded() {
    return new Promise((resolve) => {
      const existing = window.speechSynthesis.getVoices();
      if (existing.length) {
        cachedVoice = pickVoice();
        resolve();
        return;
      }
      window.speechSynthesis.onvoiceschanged = () => {
        cachedVoice = pickVoice();
        resolve();
      };
      // Fallback in case voiceschanged never fires on this browser.
      setTimeout(() => {
        if (!cachedVoice) cachedVoice = pickVoice();
        resolve();
      }, 800);
    });
  }

  let recognition = null;
  let active = false; // whether the overlay session is open
  let listening = false;

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function setOrbState(state) {
    orb.classList.remove("listening", "thinking", "speaking");
    if (state) orb.classList.add(state);
  }

  function speak(text, onEnd) {
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;

    // Pitch is set based on the preference regardless of whether a
    // distinctly male/female-named voice was found - some phones only
    // expose one or two voices total with no gendered variants, so
    // this guarantees an audible difference between the two settings
    // even there, instead of both sounding identical.
    utter.pitch = VOICE_PREF === "male" ? 0.82 : 1.05;

    if (cachedVoice) {
      utter.voice = cachedVoice;
      utter.lang = cachedVoice.lang;
    }
    setOrbState("speaking");
    setStatus("Speaking…");
    utter.onend = () => {
      if (onEnd) onEnd();
    };
    utter.onerror = () => {
      if (onEnd) onEnd();
    };
    window.speechSynthesis.speak(utter);
  }

  function startListening() {
    if (!active || !recognition) return;
    try {
      recognition.start();
    } catch (err) {
      /* already started - ignore */
    }
  }

  function openOverlay() {
    overlay.classList.remove("hidden");
    active = true;

    if (!speechSupported) {
      unsupportedEl.classList.remove("hidden");
      orb.classList.add("hidden");
      return;
    }

    unsupportedEl.classList.add("hidden");
    orb.classList.remove("hidden");
    transcriptEl.textContent = "";
    setStatus(GREETING);
    setOrbState(null);

    ensureVoiceLoaded().then(() => {
      speak(GREETING, () => {
        if (active) startListening();
      });
    });
  }

  function closeOverlay() {
    active = false;
    listening = false;
    window.speechSynthesis.cancel();
    if (recognition) {
      try { recognition.stop(); } catch (err) { /* ignore */ }
    }
    overlay.classList.add("hidden");
    setOrbState(null);
  }

  async function sendToAngie(message) {
    setOrbState("thinking");
    setStatus("Thinking…");

    let fullReply = "";
    let quoteText = "";

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: VOICE_TOPIC, message }),
      });

      if (!res.ok || !res.body) {
        speak("Sorry, I couldn't reach the server just now.", () => {
          if (active) startListening();
        });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          const line = part.replace(/^data: /, "").trim();
          if (!line) continue;
          try {
            const payload = JSON.parse(line);
            if (payload.chunk) {
              fullReply += payload.chunk;
              transcriptEl.textContent = fullReply;
            }
            if (payload.quote) {
              quoteText = `Also — a thought from ${payload.quote.author}: ${payload.quote.text}`;
            }
          } catch (err) {
            /* ignore partial chunk */
          }
        }
      }

      const spoken = quoteText ? `${fullReply.trim()} ${quoteText}` : fullReply.trim();

      speak(spoken || "I didn't quite catch a response — could you say that again?", () => {
        if (active) startListening();
      });
    } catch (err) {
      speak("Sorry, something went wrong reaching the server.", () => {
        if (active) startListening();
      });
    }
  }

  if (speechSupported) {
    recognition = new SpeechRecognitionCtor();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = document.documentElement.lang || "en-US";

    recognition.onstart = () => {
      listening = true;
      setOrbState("listening");
      setStatus("Listening…");
      transcriptEl.textContent = "";
    };

    recognition.onresult = (event) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) final += t;
        else interim += t;
      }
      transcriptEl.textContent = final || interim;

      if (final.trim()) {
        listening = false;
        try { recognition.stop(); } catch (err) { /* ignore */ }
        sendToAngie(final.trim());
      }
    };

    recognition.onerror = (event) => {
      listening = false;
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        setStatus("Microphone access was blocked. Allow it in your browser settings and try again.");
        setOrbState(null);
        return;
      }
      if (event.error === "no-speech") {
        if (active) startListening();
        return;
      }
      setStatus("Something went wrong with the microphone. Tap the orb to try again.");
      setOrbState(null);
    };

    recognition.onend = () => {
      listening = false;
    };

    orb.addEventListener("click", () => {
      if (!active) return;
      if (!listening) startListening();
    });
  }

  fab.addEventListener("click", openOverlay);
  closeBtn.addEventListener("click", closeOverlay);
  if (fallbackCloseBtn) fallbackCloseBtn.addEventListener("click", closeOverlay);
})();
