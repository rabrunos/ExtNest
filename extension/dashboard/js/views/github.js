import { state } from "../state.js";
import { nativeOk } from "../api/native.js";
import { toast } from "../ui/toast.js";

function esc(v = "") {
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

function identityApi() {
  const identity = globalThis.chrome?.identity ?? globalThis.browser?.identity;
  if (!identity?.getRedirectURL || !identity?.launchWebAuthFlow) {
    throw new Error(
      "API de identidade do navegador ainda não está carregada. " +
      "Recarregue o ExtNest em edge://extensions e abra o painel novamente."
    );
  }
  return identity;
}

export function renderGitHub() {
  const accounts = state.auth.github_accounts || [];
  const list = document.getElementById("githubAccountsList");
  const select = document.getElementById("githubAccountSelect");
  const previous = select.value;

  list.innerHTML = "";
  select.innerHTML = '<option value="">Selecione uma conta...</option>';

  if (!accounts.length) {
    list.innerHTML = '<div class="hint">Nenhuma conta GitHub conectada.</div>';
  }

  for (const account of accounts) {
    const row = document.createElement("div");
    row.className = "account-row";
    row.innerHTML =
      '<div class="avatar-placeholder">' +
      esc((account.login || "G").slice(0, 1).toUpperCase()) +
      '</div><div><strong>' +
      esc(account.name || account.login || "GitHub") +
      '</strong><span>' +
      (account.login ? "@" + esc(account.login) : "") +
      '</span></div><button class="secondary danger github-account-disconnect" data-account-id="' +
      esc(account.account_id) +
      '">Desconectar</button>';
    list.appendChild(row);

    const option = document.createElement("option");
    option.value = account.account_id;
    option.textContent = account.login ? "@" + account.login : account.account_id;
    select.appendChild(option);
  }

  if (accounts.some(account => account.account_id === previous)) {
    select.value = previous;
  } else if (accounts.length === 1) {
    select.value = accounts[0].account_id;
  }

  document.getElementById("loadReposBtn").disabled = !select.value;
}

export async function connectGitHub(refreshAll) {
  const identity = identityApi();
  const redirectUri = identity.getRedirectURL("github");

  const prepared = await nativeOk("oauth_github_prepare", {
    redirect_uri: redirectUri
  });

  const callbackUrl = await identity.launchWebAuthFlow({
    url: prepared.authorization_url,
    interactive: true
  });

  if (!callbackUrl) {
    throw new Error("O GitHub não retornou a autorização.");
  }

  const response = await nativeOk("oauth_github_complete", {
    callback_url: callbackUrl
  });

  toast("Conta @" + (response.profile?.login || "GitHub") + " adicionada.");
  await refreshAll();
}

export async function disconnectGitHubAccount(accountId, refreshAll) {
  const used = state.registry.filter(
    item => String(item.account_id || "") === String(accountId)
  );

  if (used.length) {
    const names = used.slice(0, 3).map(item => item.name || item.repo).join(", ");
    const extra = used.length > 3 ? " e mais " + (used.length - 3) : "";
    const message =
      "Essa conta é usada por " + used.length + " extensão(ões): " +
      names + extra +
      ". Elas continuarão cadastradas, mas repositórios privados não poderão atualizar até a conta ser conectada novamente. Desconectar?";
    if (!confirm(message)) return;
  }

  await nativeOk("oauth_github_disconnect", { account_id: accountId });
  state.repos = [];
  document.getElementById("repoList").innerHTML = "";
  await refreshAll();
}

export async function loadRepos() {
  const accountId = document.getElementById("githubAccountSelect").value;
  if (!accountId) throw new Error("Selecione uma conta GitHub.");

  const response = await nativeOk("github_list_repos", {
    account_id: accountId
  });

  state.repos = (response.repos || []).map(repo => ({
    ...repo,
    account_id: accountId
  }));
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
    wrap.innerHTML = '<div class="hint">Nenhum repositório carregado.</div>';
    return;
  }

  for (const repo of visible) {
    const already = managed.has(repo.full_name.toLowerCase());
    const row = document.createElement("label");
    row.className = "repo-row" + (repo.private ? " private" : " public");

    row.innerHTML =
      '<input type="checkbox" data-repo="' + esc(repo.full_name) + '"' +
      (already ? " disabled" : "") +
      '><div class="grow"><strong>' + esc(repo.full_name) + '</strong><span>' +
      esc(repo.description || "Sem descrição") + " · " +
      esc(repo.default_branch || "main") +
      '</span></div><span class="badge">' +
      (repo.private ? "Privado" : "Público") +
      '</span>' +
      (already ? '<span class="badge good">Adicionado</span>' : "");

    wrap.appendChild(row);
  }
}

export async function addSelectedRepos(refreshAll) {
  const selected = [...document.querySelectorAll("#repoList input:checked")]
    .map(el => el.dataset.repo);

  if (!selected.length) throw new Error("Selecione ao menos um repositório.");

  const byName = new Map(state.repos.map(repo => [repo.full_name, repo]));

  for (const fullName of selected) {
    const repo = byName.get(fullName);
    await nativeOk("repo_register", {
      repo: fullName,
      branch: repo?.default_branch || null,
      account_id: repo?.private ? repo.account_id : null
    });
  }

  await refreshAll();
}

export async function addPublicRepo(refreshAll) {
  const input = document.getElementById("publicRepoInput");
  const branchInput = document.getElementById("publicRepoBranch");
  const repo = input.value.trim();
  const branch = branchInput.value.trim() || null;

  if (!repo) {
    throw new Error("Informe owner/repo ou a URL do repositório público.");
  }

  const response = await nativeOk("repo_register", {
    repo,
    branch,
    account_id: null
  });

  input.value = "";
  branchInput.value = "";
  toast((response.item?.name || response.item?.repo || "Repositório") + " adicionado sem login.");
  await refreshAll();
}
