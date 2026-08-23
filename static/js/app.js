// ==========================================================
// Service worker registration
// ==========================================================
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {});
  });
}

// ==========================================================
// Install prompt (Android/desktop Chrome/Edge)
// ==========================================================
let deferredPrompt = null;
const banner = document.getElementById("install-banner");
const installBtn = document.getElementById("install-btn");
const dismissBtn = document.getElementById("install-dismiss");

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (banner && !localStorage.getItem("angie-install-dismissed")) {
    banner.classList.remove("hidden");
  }
});

if (installBtn) {
  installBtn.addEventListener("click", async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    banner.classList.add("hidden");
  });
}

if (dismissBtn) {
  dismissBtn.addEventListener("click", () => {
    banner.classList.add("hidden");
    localStorage.setItem("angie-install-dismissed", "1");
  });
}

window.addEventListener("appinstalled", () => {
  if (banner) banner.classList.add("hidden");
});
