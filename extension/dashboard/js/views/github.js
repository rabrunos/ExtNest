import { state } from "../state.js";
import { nativeOk } from "../api/native.js";
import { toast } from "../ui/toast.js";
import { openModal, closeModal } from "../ui/modal.js";

function esc(v = "") {
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

export function renderGitHub() {
  const connected = !!state.auth.github;
  document.getElementById("githubDisconnected").classList.toggle("hidden", connected);
  document.getElementById("githubConnected").classList.toggle("hidden", !connected);

  if (connected) {
    const profile = state.auth.github;
    document.getElementById("githubUser").textContent = profile.name || profile.login || "GitHub";
    document.getElementById("githubAccountDetail").textContent = profile.login ? `@${profile.login}` : "";
    document.getElementById("githubAvatar").textContent = (profile.login || "G").slice(0, 1).toUpperCase();
  }
}

export async function connectGitHub(refreshAll) {
  document.getElementById("waitTitle").textContent = "Conectar GitHub";
  document.getElementById("waitMessage").textContent =
    "Conclua o login e a autorização na página oficial do GitHub…";
  openModal("waitModal");

  try {
    const response = await nativeOk("oauth_interactive_login", { provider:"github" });
    toast(`GitHub conectado como @${response.profile?.login || "usuário"}.`);
    await refreshAll();
  } finally {
    closeModal("waitModal");
  }
}

export async function disconnectGitHub(refreshAll) {
  await nativeOk("oauth_disconnect", { provider:"github" });
  state.repos = [];
  document.getElementById("repoList").innerHTML = "";
  await refreshAll();
}

export async function loadRepos() {
  if (!state.auth.github) throw new Error("Conecte o GitHub primeiro.");

  const response = await nativeOk("github_list_repos");
  state.repos = response.repos || [];
  renderRepoList();
}

export function renderRepoList() {
  const query = document.getElementById("repoSearch").value.trim().toLowerCase();
  const managed = new Set(state.registry.map(item => item.repo.toLowerCase()));
  const wrap = document.getElementById("repoList");
  wrap.innerHTML = "";

  const visible = state.repos.filter(repo =>
    !query || repo.full_name.toLowerCase().includes(query)
  );

  if (!visible.length) {
    wrap.innerHTML = '<div class="hint">Nenhum repositório encontrado.</div>';
    return;
  }

  for (const repo of visible) {
    const already = managed.has(repo.full_name.toLowerCase());
    const row = document.createElement("label");
    row.className = "repo-row" + (repo.private ? " private" : "");

    row.innerHTML = `
      <input type="checkbox" data-repo="${esc(repo.full_name)}" ${already ? "disabled" : ""}>
      <div class="grow">
        <strong>${esc(repo.full_name)}</strong>
        <span>${esc(repo.description || "Sem descrição")} · ${esc(repo.default_branch || "main")}</span>
      </div>
      ${already ? '<span class="badge good">Adicionado</span>' : ""}
    `;

    wrap.appendChild(row);
  }
}

export async function addSelectedRepos(refreshAll) {
  const selected = [...document.querySelectorAll("#repoList input:checked")].map(el => el.dataset.repo);
  if (!selected.length) throw new Error("Selecione ao menos um repositório.");

  const byName = new Map(state.repos.map(repo => [repo.full_name, repo]));
  for (const fullName of selected) {
    const repo = byName.get(fullName);
    await nativeOk("repo_register", { repo: fullName, branch: repo?.default_branch || "main" });
  }

  await refreshAll();
}
