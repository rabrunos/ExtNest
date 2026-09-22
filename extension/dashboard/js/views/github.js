import { state } from "../state.js";
import { nativeOk, nativeMessage } from "../api/native.js";
import { toast } from "../ui/toast.js";
import { openModal, closeModal } from "../ui/modal.js";

let pollCancelled = false;

function esc(v = "") {
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

async function openGithubAppAccess() {
  const response = await nativeOk("github_installation_status");

  if (response.installations?.length === 1 && response.installations[0].manage_url) {
    await chrome.tabs.create({ url: response.installations[0].manage_url });
    return;
  }

  await chrome.tabs.create({ url: response.install_url });
}

export function renderGitHub() {
  const connected = !!state.auth.github;
  document.getElementById("githubDisconnected").classList.toggle("hidden", connected);
  document.getElementById("githubConnected").classList.toggle("hidden", !connected);

  if (connected) {
    const profile = state.auth.github;
    document.getElementById("githubUser").textContent =
      profile.name || profile.login || "GitHub";
    document.getElementById("githubAccountDetail").textContent =
      profile.login ? `@${profile.login}` : "";
    document.getElementById("githubAvatar").textContent =
      (profile.login || "G").slice(0, 1).toUpperCase();
  }
}

export async function connectGitHub(refreshAll) {
  const begin = await nativeOk("oauth_github_begin");
  pollCancelled = false;

  document.getElementById("deviceCode").textContent = begin.user_code;
  document.getElementById("deviceHint").textContent =
    `Expira em aproximadamente ${Math.ceil(begin.expires_in / 60)} minutos.`;
  openModal("deviceModal");

  await chrome.tabs.create({ url: begin.verification_uri });

  let interval = Math.max(5, Number(begin.interval || 5));
  const expiresAt = Date.now() + Number(begin.expires_in || 900) * 1000;

  while (!pollCancelled && Date.now() < expiresAt) {
    await new Promise(resolve => setTimeout(resolve, interval * 1000));

    const response = await nativeMessage("oauth_github_poll");

    if (response?.ok && response.connected) {
      closeModal("deviceModal");
      toast(`GitHub conectado como @${response.profile?.login || "usuário"}.`);
      await refreshAll();

      const access = await nativeOk("github_installation_status");
      if (!access.count) {
        toast("Agora selecione no GitHub quais repositórios o ExtNest pode acessar.");
        await chrome.tabs.create({ url: access.install_url });
      }
      return;
    }

    if (response?.status === "slow_down") {
      interval += 5;
      continue;
    }

    if (response?.status === "authorization_pending") continue;

    if (!response?.ok) {
      throw new Error(response?.error || "Falha na autenticação GitHub.");
    }
  }

  if (!pollCancelled) {
    throw new Error("A autorização do GitHub expirou.");
  }
}

export function cancelGitHubPolling() {
  pollCancelled = true;
}

export async function disconnectGitHub(refreshAll) {
  await nativeOk("oauth_disconnect", { provider:"github" });
  state.repos = [];
  document.getElementById("repoList").innerHTML = "";
  document.getElementById("githubInstallNotice").classList.add("hidden");
  await refreshAll();
}

export async function loadRepos() {
  if (!state.auth.github) {
    throw new Error("Conecte o GitHub primeiro.");
  }

  const response = await nativeOk("github_list_repos");
  state.repos = response.repos || [];

  document.getElementById("githubInstallNotice").classList.toggle(
    "hidden",
    Number(response.count || 0) > 0
  );

  renderRepoList();

  if (!response.count) {
    throw new Error(
      "O GitHub App ExtNest ainda não foi instalado em nenhum repositório."
    );
  }
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
    wrap.innerHTML = '<div class="hint">Nenhum repositório autorizado encontrado.</div>';
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
        <span>
          ${esc(repo.description || "Sem descrição")} ·
          ${esc(repo.default_branch || "main")} ·
          acesso via ${esc(repo.installation_account || "GitHub App")}
        </span>
      </div>
      ${already ? '<span class="badge good">Adicionado</span>' : ""}
    `;

    wrap.appendChild(row);
  }
}

export async function addSelectedRepos(refreshAll) {
  const selected = [...document.querySelectorAll("#repoList input:checked")]
    .map(el => el.dataset.repo);

  if (!selected.length) {
    throw new Error("Selecione ao menos um repositório.");
  }

  const byName = new Map(state.repos.map(repo => [repo.full_name, repo]));

  for (const fullName of selected) {
    const repo = byName.get(fullName);

    await nativeOk("repo_register", {
      repo: fullName,
      branch: repo?.default_branch || "main"
    });
  }

  await refreshAll();
}

export function wireGitHubAccessButtons() {
  document.getElementById("manageGithubAccessBtn")
    .addEventListener("click", () =>
      openGithubAppAccess().catch(error => toast(error.message))
    );

  document.getElementById("installGithubAppBtn")
    .addEventListener("click", () =>
      openGithubAppAccess().catch(error => toast(error.message))
    );
}
