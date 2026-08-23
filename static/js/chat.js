const historyEl = document.getElementById("chat-history");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("chat-send");

historyEl.scrollTop = historyEl.scrollHeight;

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 120) + "px";
});

function addBubble(text, cls) {
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.textContent = text;
  historyEl.appendChild(div);
  historyEl.scrollTop = historyEl.scrollHeight;
  return div;
}

function addQuoteCard(quote) {
  const card = document.createElement("div");
  card.className = "quote-card";
  card.innerHTML = `
    <div class="quote-mark">&ldquo;</div>
    <p class="quote-text"></p>
    <p class="quote-author"></p>
  `;
  card.querySelector(".quote-text").textContent = quote.text;
  card.querySelector(".quote-author").textContent = `— ${quote.author}`;
  historyEl.appendChild(card);
  historyEl.scrollTop = historyEl.scrollHeight;
  return card;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addBubble(message, "user-msg");
  input.value = "";
  input.style.height = "auto";
  sendBtn.disabled = true;

  const aiBubble = addBubble("", "ai-msg");
  let full = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: window.ANGIE_TOPIC, message }),
    });

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
            full += payload.chunk;
            aiBubble.textContent = full;
            historyEl.scrollTop = historyEl.scrollHeight;
          }
          if (payload.quote) {
            addQuoteCard(payload.quote);
          }
        } catch (err) {
          /* ignore malformed partial chunk */
        }
      }
    }
  } catch (err) {
    aiBubble.textContent = "Connection error — please try again.";
  } finally {
    sendBtn.disabled = false;
  }
});
