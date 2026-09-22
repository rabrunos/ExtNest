let timer;
export function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.remove("hidden");
  clearTimeout(timer);
  timer = setTimeout(() => el.classList.add("hidden"), 2800);
}
