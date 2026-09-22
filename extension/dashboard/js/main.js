import { VIEWS } from "../../shared/constants.js";
import { nativeMessage } from "./api/native.js";
import { state } from "./state.js";
import { toast } from "./ui/toast.js";
import { wireModalClose, closeModal } from "./ui/modal.js";
import { renderExtensions } from "./views/extensions.js";
import {
  renderGitHub, connectGitHub, disconnectGitHub, loadRepos,
  renderRepoList, addSelectedRepos, cancelGitHubPolling
} from "./views/github.js";
import {
  renderCloud, connectCloud, disconnectCloud, setPrimaryCloud, syncCloudNow
} from "./views/cloud.js";
import { renderSettings, saveSettings } from "./views/settings.js";

const REQUIRED_NATIVE_PROTOCOL = 2;

async function installedDevelopmentExtensions() {
  const all = await chrome.management.getAll();
  return all.filter(item =>
    item.type === "extension" &&
    item.installType === "development" &&
    item.id !== chrome.runtime.id
  );
}

function setDot(id, status) {
  const el = document.getElementById(id);
  el.classList.remove("good","bad","warn");
  if (status) el.classList.add(status);
}

function updateSidebar() {
  document.getElementById("helperLabel").textContent =
    state.helperOnline ? "online" : "offline";
  setDot("helperDot", state.helperOnline ? "good" : "bad");

  document.getElementById("gitLabel").textContent =
    state.auth.github?.login || "não conectado";
  setDot("gitDot", state.auth.github ? "good" : "warn");

  const cloudLabel = state.cloud.primary === "microsoft"
    ? "OneDrive"
    : state.cloud.primary === "google"
      ? "Google Drive"
      : "não configurada";

  document.getElementById("cloudLabel").textContent = cloudLabel;
  setDot("cloudDot", state.cloud.primary ? "good" : "warn");
  document.getElementById("extCount").textContent = state.registry.length || "";
}

export async function refreshState() {
  state.installed = await installedDevelopmentExtensions();

  try {
    const response = await nativeMessage("state_get");
    if (!response?.ok) throw new Error(response?.error || "Native Host indisponível.");

    const protocolVersion = Number(response.host?.protocol_version || 0);
    if (protocolVersion < REQUIRED_NATIVE_PROTOCOL) {
      throw new Error(
        `Native Host desatualizado (protocolo ${protocolVersion || 1}; esperado ${REQUIRED_NATIVE_PROTOCOL}). ` +
        "Atualize ou reinstale o ExtNest Native Host."
      );
    }

    state.helperOnline = true;
    state.helperError = "";
    state.registry = response.registry || [];
    state.auth = response.auth || { github:null, microsoft:null, google:null };
    state.cloud = response.cloud || { primary:"" };
    state.settings = response.settings || {};
    state.paths = response.paths || null;
  } catch (error) {
    state.helperOnline = false;
    state.helperError = error?.message || "Native Host indisponível.";
    state.registry = [];
    state.auth = { github:null, microsoft:null, google:null };
    state.cloud = { primary:"" };
    state.settings = {};
    state.paths = null;
  }

  const helperBanner = document.getElementById("helperBanner");
  helperBanner.classList.toggle("hidden", state.helperOnline);
  document.getElementById("helperBannerTitle").textContent =
    state.helperError.includes("desatualizado")
      ? "Native Host desatualizado."
      : "Native Host não encontrado.";
  document.getElementById("helperBannerMessage").textContent =
    state.helperError ||
    "O ExtNest precisa do helper local para Git e arquivos no AppData.";

  updateSidebar();
  await renderExtensions(refreshState);
  renderGitHub();
  renderCloud();
  renderSettings();
}

function setView(name) {
  document.querySelectorAll(".view").forEach(view => view.classList.add("hidden"));
  document.getElementById(`view-${name}`).classList.remove("hidden");
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
  document.getElementById("addRepoBtn").addEventListener("click", () => setView("github"));

  document.getElementById("connectGithubBtn").addEventListener("click", () =>
    connectGitHub(refreshState).catch(error => toast(error.message))
  );
  document.getElementById("disconnectGithubBtn").addEventListener("click", () =>
    disconnectGitHub(refreshState).catch(error => toast(error.message))
  );
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

  document.getElementById("copyDeviceCode").addEventListener("click", async () => {
    await navigator.clipboard.writeText(document.getElementById("deviceCode").textContent);
    toast("Código copiado.");
  });

  document.querySelector('[data-close="deviceModal"]').addEventListener("click", cancelGitHubPolling);
  document.getElementById("modalBackdrop").addEventListener("click", () => {
    cancelGitHubPolling();
    for (const id of ["installModal","deviceModal","waitModal"]) closeModal(id);
  });
}

wire();
refreshState().catch(error => toast(error.message));
