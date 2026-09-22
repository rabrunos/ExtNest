export function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
  document.getElementById("modalBackdrop").classList.remove("hidden");
}
export function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
  const anyOpen = [...document.querySelectorAll(".modal")].some(x => !x.classList.contains("hidden"));
  document.getElementById("modalBackdrop").classList.toggle("hidden", !anyOpen);
}
export function wireModalClose() {
  document.querySelectorAll("[data-close]").forEach(button => {
    button.addEventListener("click", () => closeModal(button.dataset.close));
  });
}
