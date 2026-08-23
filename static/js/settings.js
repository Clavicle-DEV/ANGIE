function val(id) { return document.getElementById(id).value; }
function checked(id) { return document.getElementById(id).checked; }

const message = document.getElementById("settings-message");

function showMessage(text, isError) {
  message.textContent = text;
  message.classList.remove("hidden");
  message.classList.toggle("success", !isError);
  clearTimeout(showMessage._t);
  showMessage._t = setTimeout(() => message.classList.add("hidden"), 3500);
}

document.getElementById("settings-save").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const payload = {
    language: val("s-language"),
    voice: val("s-voice"),
    theme: val("s-theme"),
    wallpaper: val("s-wallpaper"),
    voice_reply: checked("s-voice-reply"),
    daily_quotes: checked("s-daily-quotes"),
    scripture: checked("s-scripture"),
    notifications: checked("s-notifications"),
  };

  btn.disabled = true;

  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      showMessage(`Couldn't save settings (server said: ${res.status}).`, true);
      return;
    }

    const data = await res.json();

    if (data.ok) {
      showMessage("Settings saved.", false);
      document.body.className = "theme-" + payload.theme;
      document.body.dataset.wallpaper = payload.wallpaper;
    } else {
      showMessage(data.error || "Couldn't save settings.", true);
    }
  } catch (err) {
    showMessage("Couldn't reach the server. Check your connection and try again.", true);
  } finally {
    btn.disabled = false;
  }
});

// ---------------------------------------------------------
// Danger zone confirmations
// ---------------------------------------------------------
const modal = document.getElementById("confirm-modal");
const confirmText = document.getElementById("confirm-text");
const confirmOk = document.getElementById("confirm-ok");
const confirmCancel = document.getElementById("confirm-cancel");
let pendingAction = null;

function openConfirm(text, action) {
  confirmText.textContent = text;
  pendingAction = action;
  modal.classList.remove("hidden");
}

confirmCancel.addEventListener("click", () => {
  modal.classList.add("hidden");
  pendingAction = null;
});

confirmOk.addEventListener("click", async () => {
  if (!pendingAction) {
    modal.classList.add("hidden");
    return;
  }
  confirmOk.disabled = true;
  try {
    await pendingAction();
  } finally {
    confirmOk.disabled = false;
    modal.classList.add("hidden");
  }
});

document.getElementById("clear-history-btn").addEventListener("click", () => {
  openConfirm(
    "This deletes every conversation you've had. This cannot be undone.",
    async () => {
      try {
        const res = await fetch("/api/settings/clear-history", { method: "POST" });
        if (!res.ok) {
          showMessage(`Couldn't clear history (server said: ${res.status}).`, true);
          return;
        }
        const data = await res.json();
        showMessage(data.ok ? "Chat history cleared." : (data.error || "Couldn't clear history."), !data.ok);
      } catch (err) {
        showMessage("Couldn't reach the server. Check your connection and try again.", true);
      }
    }
  );
});

document.getElementById("delete-account-btn").addEventListener("click", () => {
  openConfirm(
    "This permanently deletes your account, chat history, journal entries, and mood log. This cannot be undone.",
    async () => {
      try {
        const res = await fetch("/api/settings/delete-account", { method: "POST" });
        if (!res.ok) {
          showMessage(`Couldn't delete account (server said: ${res.status}).`, true);
          return;
        }
        const data = await res.json();
        if (data.ok) {
          window.location.href = "/auth";
        } else {
          showMessage(data.error || "Couldn't delete account.", true);
        }
      } catch (err) {
        showMessage("Couldn't reach the server. Check your connection and try again.", true);
      }
    }
  );
});
