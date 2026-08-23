const buttons = document.querySelectorAll(".mood-btn");
const message = document.getElementById("mood-message");

function showMessage(text, isError) {
  message.textContent = text;
  message.classList.remove("hidden");
  message.classList.toggle("success", !isError);
}

buttons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const mood = btn.dataset.mood;
    btn.disabled = true;

    try {
      const res = await fetch("/api/mood", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mood }),
      });

      if (!res.ok) {
        showMessage(`Couldn't save (server said: ${res.status}).`, true);
        return;
      }

      const data = await res.json();
      if (data.ok) {
        showMessage(`Saved: ${mood}`, false);
        setTimeout(() => window.location.reload(), 600);
      } else {
        showMessage(data.error || "Couldn't save mood.", true);
      }
    } catch (err) {
      showMessage("Couldn't reach the server. Check your connection.", true);
    } finally {
      btn.disabled = false;
    }
  });
});
