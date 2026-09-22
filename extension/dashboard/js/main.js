import { VIEWS, HELPER_INSTALLER_URL, HELPER_RELEASE_API, HELPER_ASSET_NAME } from "../../shared/constants.js";
import { nativeMessage, nativeOk } from "./api/native.js";
import { state } from "./state.js";
import { toast } from "./ui/toast.js";
import { wireModalClose, closeModal } from "./ui/modal.js";
import { renderExtensions } from "./views/extensions.js";
import {
  renderGitHub, connectGitHub, disconnectGitHubAccount, loadRepos,
  renderRepoList, addSelectedRepos, addPublicRepo
} from "./views/github.js";
import {
  renderCloud, connectCloud, disconnectCloud, setPrimaryCloud, syncCloudNow
} from "./views/cloud.js";
import { renderSettings, saveSettings } from "./views/settings.js";

const REQUIRED_NATIVE_PROTOCOL = 3;

let helperInstallerDownloadId = null;
let helperInstallerReady = false;
let helperPolling = false;

async function resolveHelperInstallerUrl() {
  let response;

  try {
    response = await fetch(HELPER_RELEASE_API, {
      headers: { "Accept": "application/vnd.github+json" },
      cache: "no-store"
    });
  } catch {
    throw new Error(
      "Não foi possível verificar o instalador do ExtNest. Tente novamente em alguns instantes."
    );
  }

  if (response.status === 404) {
    throw new Error(
      "O instalador do ExtNest ainda não foi publicado. A versão do Helper precisa ser gerada antes deste teste."
    );
  }

  if (!response.ok) {
    throw new Error(
      "Não foi possível verificar a versão do componente local do ExtNest."
    );
  }

  const release = await response.json();
  const asset = (release.assets || []).find(item => item.name === HELPER_ASSET_NAME);

  if (!asset?.browser_download_url) {
    throw new Error(
      "A última versão do ExtNest ainda não contém o instalador do componente local."
    );
  }

  return asset.browser_download_url || HELPER_INSTALLER_URL;
}

async function configureDevUpdate() {
  try {
    const self = await chrome.management.getSelf();
    const button = document.getElementById("devUpdateBtn");
    if (!button) return;
    button.classList.toggle("hidden", self.installType !== "development");
  } catch {}
}

async function installedDevelopmentExtensions() {
  const all = await chrome.management.getAll();
  return all.filter(item =>
    item.type === "extension" &&
    item.installType === "development" &&
    item.id !== chrome.runtime.id
  );
}

function versionTuple(value) {
  return String(value || "0")
    .split(".")
    .slice(0, 4)
    .map(part => Number.parseInt(part, 10) || 0)
    .concat([0,0,0,0])
    .slice(0,4);
}

function versionLt(a, b) {
  const av = versionTuple(a);
  const bv = versionTuple(b);
  for (let i = 0; i < 4; i++) {
    if (av[i] !== bv[i]) return av[i] < bv[i];
  }
  return false;
}

function setDot(id, status) {
  const el = document.getElementById(id);
  el.classList.remove("good","bad","warn");
  if (status) el.classList.add(status);
}

function updateNativeDependentControls() {
  const ids = [
    "addGithubAccountBtn",
    "loadReposBtn",
    "addSelectedReposBtn",
    "addPublicRepoBtn",
    "connectMicrosoftBtn",
    "connectGoogleBtn",
    "syncCloudNowBtn",
    "devUpdateBtn"
  ];

  for (const id of ids) {
    const el = document.getElementById(id);
    if (el) el.disabled = !state.helperOnline;
  }

  if (state.helperOnline) {
    const accountSelect = document.getElementById("githubAccountSelect");
    const loadRepos = document.getElementById("loadReposBtn");
    if (accountSelect && loadRepos) {
      loadRepos.disabled = !accountSelect.value;
    }
  }
}

function updateSidebar() {
  document.getElementById("helperLabel").textContent =
    state.helperOnline ? "online" : "offline";
  setDot("helperDot", state.helperOnline ? "good" : "bad");

  const accounts = state.auth.github_accounts || [];
  document.getElementById("gitLabel").textContent =
    accounts.length
      ? String(accounts.length) + " conta" + (accounts.length === 1 ? "" : "s")
      : "sem conta";
  setDot("gitDot", accounts.length ? "good" : "warn");

  const cloudLabel = state.cloud.primary === "microsoft"
    ? "OneDrive"
    : state.cloud.primary === "google"
      ? "Google Drive"
      : "não configurada";

  document.getElementById("cloudLabel").textContent = cloudLabel;
  setDot("cloudDot", state.cloud.primary ? "good" : "warn");
  document.getElementById("extCount").textContent = state.registry.length || "";

  const manifest = chrome.runtime.getManifest();
  document.getElementById("appVersion").textContent = "v" + (manifest.version || "—");
}

export async function refreshState() {
  state.installed = await installedDevelopmentExtensions();

  try {
    const response = await nativeMessage("state_get");
    if (!response?.ok) throw new Error(response?.error || "Native Host indisponível.");

    const protocolVersion = Number(response.host?.protocol_version || 0);
    if (protocolVersion < REQUIRED_NATIVE_PROTOCOL) {
      throw new Error(
        "Native Host desatualizado (protocolo " +
        String(protocolVersion || 1) +
        "; esperado " +
        String(REQUIRED_NATIVE_PROTOCOL) +
        "). Atualize ou reinstale o ExtNest Native Host."
      );
    }

    const appVersion = chrome.runtime.getManifest().version || "0.0.0";
    const helperVersion = response.host?.version || "0.0.0";

    if (versionLt(helperVersion, appVersion)) {
      throw new Error(
        "Native Host desatualizado (Helper " + helperVersion +
        "; ExtNest " + appVersion + "). Atualize o componente local."
      );
    }

    state.helperOnline = true;
    state.helperError = "";
    state.helperVersion = helperVersion;
    state.registry = response.registry || [];
    state.auth = response.auth || {
      github_accounts: [],
      github: null,
      microsoft: null,
      google: null
    };
    state.cloud = response.cloud || { primary:"" };
    state.settings = response.settings || {};
    state.paths = response.paths || null;
  } catch (error) {
    state.helperOnline = false;
    state.helperError = error?.message || "Native Host indisponível.";
    state.helperVersion = "";
    state.registry = [];
    state.auth = {
      github_accounts: [],
      github: null,
      microsoft: null,
      google: null
    };
    state.cloud = { primary:"" };
    state.settings = {};
    state.paths = null;
  }

  const helperBanner = document.getElementById("helperBanner");
  helperBanner.classList.toggle("hidden", state.helperOnline);

  if (!state.helperOnline) {
    const outdated = state.helperError.includes("desatualizado");
    document.getElementById("helperBannerTitle").textContent =
      outdated ? "Atualize o componente local do ExtNest" : "Finalize a instalação do ExtNest";
    document.getElementById("helperBannerMessage").textContent =
      outdated
        ? "Instale a versão mais recente do componente local para continuar."
        : "Instale o componente local uma única vez. Não é necessário configurar pastas, Registro ou PowerShell.";
    if (!helperInstallerReady) {
      document.getElementById("installHelperBtn").textContent =
        outdated ? "Atualizar componente" : "Finalizar instalação";
    }
  }

  updateSidebar();
  updateNativeDependentControls();
  await renderExtensions(refreshState);
  renderGitHub();
  renderCloud();
  renderSettings();
}

async function startHelperPolling() {
  if (helperPolling) return;
  helperPolling = true;

  try {
    const deadline = Date.now() + 120000;

    while (!state.helperOnline && Date.now() < deadline) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await refreshState();
    }

    if (state.helperOnline) {
      helperInstallerReady = false;
      helperInstallerDownloadId = null;
      toast("Componente local instalado. ExtNest pronto para uso.");
    }
  } finally {
    helperPolling = false;
  }
}

function setView(name) {
  document.querySelectorAll(".view").forEach(view => view.classList.add("hidden"));
  document.getElementById("view-" + name).classList.remove("hidden");
  document.querySelectorAll(".nav").forEach(button => {
    button.classList.toggle("active", button.dataset.view === name);
  });

  document.getElementById("viewTitle").textContent = VIEWS[name].title;
  document.getElementById("viewSubtitle").textContent = VIEWS[name].subtitle;
  document.getElementById("headerActions").classList.toggle("hidden", name !== "extensions");
}

function wire() {
  wireModalClose();

  document.querySelectorAll(".nav").forEach(button => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });

  document.getElementById("refreshBtn").addEventListener("click", () =>
    refreshState().then(() => toast("Atualizado."))
  );

  document.getElementById("devUpdateBtn").addEventListener("click", async () => {
    const button = document.getElementById("devUpdateBtn");
    const original = button.textContent;
    button.disabled = true;
    button.textContent = "Atualizando...";

    try {
      const result = await nativeOk("dev_self_update");

      if (!result.changed) {
        button.textContent = original;
        toast("ExtNest DEV já está atualizado.");
        return;
      }

      button.textContent = "Recarregando...";
      toast("ExtNest atualizado. Recarregando a extensão...");
      setTimeout(() => chrome.runtime.reload(), 600);
    } catch (error) {
      button.textContent = original;
      toast(error.message);
    } finally {
      button.disabled = false;
    }
  });

  document.getElementById("installHelperBtn").addEventListener("click", async () => {
    const button = document.getElementById("installHelperBtn");

    if (helperInstallerReady && helperInstallerDownloadId != null) {
      try {
        await chrome.downloads.open(helperInstallerDownloadId);
        button.textContent = "Aguardando instalação...";
        toast("Conclua o instalador. O ExtNest detectará o componente automaticamente.");
        startHelperPolling();
      } catch (error) {
        chrome.downloads.show(helperInstallerDownloadId);
        toast(error?.message || "Abra o instalador pela pasta de Downloads.");
      }
      return;
    }

    button.disabled = true;
    button.textContent = "Baixando...";

    try {
      const installerUrl = await resolveHelperInstallerUrl();

      helperInstallerDownloadId = await new Promise((resolve, reject) => {
        chrome.downloads.download({
          url: installerUrl,
          filename: "ExtNest/ExtNestHelperSetup.exe",
          saveAs: false
        }, id => {
          const error = chrome.runtime.lastError;
          if (error || id == null) {
            reject(new Error(error?.message || "Falha ao baixar o instalador."));
          } else {
            resolve(id);
          }
        });
      });

      await new Promise((resolve, reject) => {
        const listener = delta => {
          if (delta.id !== helperInstallerDownloadId || !delta.state) return;

          if (delta.state.current === "complete") {
            chrome.downloads.onChanged.removeListener(listener);
            resolve();
          } else if (delta.state.current === "interrupted") {
            chrome.downloads.onChanged.removeListener(listener);
            reject(new Error("O download do componente local foi interrompido."));
          }
        };

        chrome.downloads.onChanged.addListener(listener);
      });

      helperInstallerReady = true;
      button.textContent = "Abrir instalador";
      toast("Download concluído. Clique em Abrir instalador.");
      startHelperPolling();
    } catch (error) {
      helperInstallerDownloadId = null;
      helperInstallerReady = false;
      button.textContent = "Finalizar instalação";
      toast(error.message);
    } finally {
      button.disabled = false;
    }
  });
  document.getElementById("addRepoBtn").addEventListener("click", () => setView("github"));

  document.getElementById("addGithubAccountBtn").addEventListener("click", () =>
    connectGitHub(refreshState).catch(error => toast(error.message))
  );

  document.getElementById("githubAccountsList").addEventListener("click", event => {
    const button = event.target.closest(".github-account-disconnect");
    if (!button) return;
    disconnectGitHubAccount(button.dataset.accountId, refreshState)
      .catch(error => toast(error.message));
  });

  document.getElementById("githubAccountSelect").addEventListener("change", event => {
    document.getElementById("loadReposBtn").disabled = !event.target.value;
    state.repos = [];
    renderRepoList();
  });

  document.getElementById("loadReposBtn").addEventListener("click", () =>
    loadRepos().catch(error => toast(error.message))
  );
  document.getElementById("repoSearch").addEventListener("input", renderRepoList);

  document.getElementById("addSelectedReposBtn").addEventListener("click", () =>
    addSelectedRepos(refreshState).then(() => {
      setView("extensions");
      toast("Repositórios adicionados.");
    }).catch(error => toast(error.message))
  );

  document.getElementById("addPublicRepoBtn").addEventListener("click", () =>
    addPublicRepo(refreshState)
      .then(() => setView("extensions"))
      .catch(error => toast(error.message))
  );

  document.getElementById("connectMicrosoftBtn").addEventListener("click", () =>
    connectCloud("microsoft", refreshState).catch(error => toast(error.message))
  );
  document.getElementById("disconnectMicrosoftBtn").addEventListener("click", () =>
    disconnectCloud("microsoft", refreshState).catch(error => toast(error.message))
  );
  document.getElementById("connectGoogleBtn").addEventListener("click", () =>
    connectCloud("google", refreshState).catch(error => toast(error.message))
  );
  document.getElementById("disconnectGoogleBtn").addEventListener("click", () =>
    disconnectCloud("google", refreshState).catch(error => toast(error.message))
  );
  document.getElementById("primaryCloud").addEventListener("change", () =>
    setPrimaryCloud().catch(error => toast(error.message))
  );
  document.getElementById("syncCloudNowBtn").addEventListener("click", () =>
    syncCloudNow(refreshState).catch(error => toast(error.message))
  );

  for (const id of ["autoCheck","checkInterval","autoConfigBackup","askRestore"]) {
    document.getElementById(id).addEventListener("change", () =>
      saveSettings().catch(error => toast(error.message))
    );
  }

  document.getElementById("copyInstallPath").addEventListener("click", async () => {
    await navigator.clipboard.writeText(document.getElementById("installPath").textContent);
    toast("Caminho copiado.");
  });

  document.getElementById("openExtensionsPage").addEventListener("click", () =>
    chrome.tabs.create({ url:"chrome://extensions/" })
  );

  document.getElementById("modalBackdrop").addEventListener("click", () => {
    for (const id of ["installModal","waitModal"]) closeModal(id);
  });
}

wire();
configureDevUpdate();
refreshState().catch(error => toast(error.message));
