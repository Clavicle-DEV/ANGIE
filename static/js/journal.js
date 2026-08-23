const saveBtn = document.getElementById("journal-save");
const entryInput = document.getElementById("journal-entry");
const list = document.getElementById("journal-list");

function flash(text) {
  const el = document.createElement("p");
  el.className = "auth-message success";
  el.textContent = text;
  saveBtn.insertAdjacentElement("afterend", el);
  setTimeout(() => el.remove(), 3000);
}

function flashError(text) {
  const el = document.createElement("p");
  el.className = "auth-message";
  el.textContent = text;
  saveBtn.insertAdjacentElement("afterend", el);
  setTimeout(() => el.remove(), 4000);
}

saveBtn.addEventListener("click", async () => {
  const entry = entryInput.value.trim();
  if (!entry) return;

  saveBtn.disabled = true;
  try {
    const res = await fetch("/api/journal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entry }),
    });

    if (!res.ok) {
      flashError(`Couldn't save (server said: ${res.status}).`);
      return;
    }

    const data = await res.json();
    if (data.ok) {
      entryInput.value = "";
      window.location.reload();
    } else {
      flashError(data.error || "Couldn't save entry.");
    }
  } catch (err) {
    flashError("Couldn't reach the server. Check your connection.");
  } finally {
    saveBtn.disabled = false;
  }
});

list.addEventListener("click", async (e) => {
  if (!e.target.classList.contains("entry-delete")) return;
  const id = e.target.dataset.id;
  const card = e.target.closest(".entry-card");

  try {
    const res = await fetch(`/api/journal/${id}`, { method: "DELETE" });
    if (res.ok) {
      card.remove();
    } else {
      flashError(`Couldn't delete (server said: ${res.status}).`);
    }
  } catch (err) {
    flashError("Couldn't reach the server. Check your connection.");
  }
});
