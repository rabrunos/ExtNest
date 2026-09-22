import { state } from "../state.js";
import { nativeOk } from "../api/native.js";
import { toast } from "../ui/toast.js";
import { openModal, closeModal } from "../ui/modal.js";

export function renderCloud() {
  for (const provider of ["microsoft", "google"]) {
    const connected = !!state.auth[provider];
    document.getElementById(`${provider}Disconnected`).classList.toggle("hidden", connected);
    document.getElementById(`${provider}Connected`).classList.toggle("hidden", !connected);

    if (connected) {
      const profile = state.auth[provider];
      document.getElementById(`${provider}User`).textContent =
        profile.name || profile.display_name || profile.email || "Conectado";
      document.getElementById(`${provider}Account`).textContent =
        profile.email || profile.user_principal_name || "";
    }
  }

  document.getElementById("primaryCloud").value = state.cloud.primary || "";
}

export async function connectCloud(provider, refreshAll) {
  const label = provider === "microsoft" ? "OneDrive" : "Google Drive";
  document.getElementById("waitTitle").textContent = `Conectar ${label}`;
  document.getElementById("waitMessage").textContent = "Conclua o login e a autorização no navegador…";
  openModal("waitModal");

  try {
    const response = await nativeOk("oauth_interactive_login", { provider });
    toast(`${label} conectado.`);
    await refreshAll();

    if (!state.cloud.primary) {
      await nativeOk("cloud_set_primary", { provider });
      await refreshAll();
    }

    return response;
  } finally {
    closeModal("waitModal");
  }
}

export async function disconnectCloud(provider, refreshAll) {
  await nativeOk("oauth_disconnect", { provider });
  if (state.cloud.primary === provider) {
    await nativeOk("cloud_set_primary", { provider:"" });
  }
  await refreshAll();
}

export async function setPrimaryCloud() {
  const provider = document.getElementById("primaryCloud").value;
  if (provider && !state.auth[provider]) throw new Error("Conecte esse provedor primeiro.");
  await nativeOk("cloud_set_primary", { provider });
  state.cloud.primary = provider;
  toast(provider ? "Destino principal atualizado." : "Backup em nuvem desativado.");
}

export async function syncCloudNow(refreshAll) {
  if (!state.cloud.primary) throw new Error("Selecione um destino principal.");
  await nativeOk("cloud_sync_vault");
  toast("Vault sincronizado com a nuvem.");
  await refreshAll();
}
