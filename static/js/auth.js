const tabs = document.querySelectorAll(".tab");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const messageEl = document.getElementById("auth-message");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    messageEl.classList.add("hidden");
    if (tab.dataset.tab === "login") {
      loginForm.classList.remove("hidden");
      signupForm.classList.add("hidden");
    } else {
      signupForm.classList.remove("hidden");
      loginForm.classList.add("hidden");
    }
  });
});

document.querySelectorAll(".pwd-toggle").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.target);
    const hidden = input.type === "password";
    input.type = hidden ? "text" : "password";
    btn.textContent = hidden ? "🙈" : "👁️";
  });
});

function showMessage(text, isError = true) {
  messageEl.textContent = text;
  messageEl.classList.remove("hidden");
  messageEl.classList.toggle("success", !isError);
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (data.ok) {
    window.location.href = "/dashboard";
  } else {
    showMessage(data.error || "Login failed.");
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("signup-username").value;
  const full_name = document.getElementById("signup-fullname").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  const res = await fetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, full_name, email, password }),
  });
  const data = await res.json();
  if (data.ok) {
    window.location.href = "/dashboard";
  } else {
    showMessage(data.error || "Sign up failed.");
  }
});
