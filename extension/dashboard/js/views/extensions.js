import { state } from "../state.js";
import { nativeOk } from "../api/native.js";
import { toast } from "../ui/toast.js";
import { openModal } from "../ui/modal.js";

function esc(v = "") {
  return String(v).replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

function button(label, className, handler) {
  const el = document.createElement("button");
  el.textContent = label;
  if (className) el.className = className;
  el.addEventListener("click", async () => {
    try { await handler(); } catch (error) { toast(error.message); }
  });
  return el;
}

async function bridgePing(extensionId) {
  try {
    return await chrome.runtime.sendMessage(extensionId, { type:"extnest.ping", protocol:1 });
  } catch {
    return null;
  }
}

async function configAction(type, extensionId) {
  const response = await chrome.runtime.sendMessage({ type, extensionId });
  if (!response?.ok) throw new Error(response?.error || "Falha na operação.");
  return response;
}

export async function renderExtensions(refreshAll) {
  const wrap = document.getElementById("extensionCards");
  wrap.innerHTML = "";

  if (!state.registry.length) {
    wrap.innerHTML = `<div class="panel"><h2>Nenhuma extensão adicionada</h2><p>Conecte uma conta GitHub para repositórios privados ou adicione um repositório público sem login.</p></div>`;
    renderDetected();
    return;
  }

  for (const item of state.registry) {
    let status = null;
    try { status = await nativeOk("repo_status", { slug:item.slug }); } catch {}

    const expectedId = item.extension_id || status?.expected_extension_id;
    const installed = state.installed.find(x => x.id === expectedId);
    const bridge = installed ? await bridgePing(installed.id) : null;
    const updateAvailable = !!(installed && status?.update_available);
    const localExists = !!status?.local_exists;
    const account = (state.auth.github_accounts || []).find(
      x => String(x.account_id) === String(item.account_id || "")
    );
    const sourceLabel = item.private
      ? (account?.login ? "@" + account.login : "Conta desconectada")
      : "Público";

    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <div class="card-head">
        <div class="card-title">
          <div class="ext-icon"><img src="../icons/icon32.png" alt=""></div>
          <div><h3>${esc(item.name || item.slug)}</h3><span class="repo">${esc(item.repo)}</span></div>
        </div>
        <span class="badge ${updateAvailable ? "warn" : installed ? "good" : ""}">
          ${updateAvailable ? "Atualização disponível" : installed ? "Instalada" : localExists ? "Preparada" : "Na nuvem"}
        </span>
      </div>
      <div class="meta">
        <div class="meta-item"><span>Instalada</span><strong>${esc(installed?.version || status?.local_version || "—")}</strong></div>
        <div class="meta-item"><span>GitHub</span><strong>${esc(status?.remote_version || "—")}</strong></div>
        <div class="meta-item"><span>Origem</span><strong>${esc(sourceLabel)}</strong></div>
        <div class="meta-item"><span>Config Bridge</span><strong>${bridge?.ok ? "Compatível" : installed ? "Não detectado" : "—"}</strong></div>
        <div class="meta-item"><span>Config na nuvem</span><strong>${status?.config_backup ? "Salva" : "—"}</strong></div>
      </div>
      <div class="card-actions"></div>
    `;

    const actions = card.querySelector(".card-actions");

    if (!localExists) {
      actions.append(button("Instalar", "main", async () => {
        const result = await nativeOk("repo_install", { slug:item.slug });
        document.getElementById("installPath").textContent = result.path;
        openModal("installModal");
        await refreshAll();
      }));
    } else if (!installed) {
      actions.append(button("Carregar no navegador", "main", () => {
        document.getElementById("installPath").textContent = status.local_path;
        openModal("installModal");
      }));
    }

    if (updateAvailable) {
      actions.append(button("Atualizar", "main", async () => {
        if (!confirm(`Atualizar ${item.name || item.slug} a partir do GitHub?`)) return;

        if (bridge?.ok) {
          try {
            await configAction("extnest.ui.backup-config", installed.id);
          } catch {}
        }

        await nativeOk("repo_update", { slug:item.slug });

        if (bridge?.ok) {
          try { await configAction("extnest.ui.reload", installed.id); } catch {}
        } else {
          toast("Arquivos atualizados. Recarregue a extensão na página de extensões.");
        }
        await refreshAll();
      }));
    }

    if (localExists) {
      actions.append(button("Abrir pasta", "", () => nativeOk("repo_open", { slug:item.slug })));
    }

    if (installed && bridge?.ok) {
      actions.append(button("Backup cfg", "", async () => {
        await configAction("extnest.ui.backup-config", installed.id);
        toast("Configurações salvas.");
        await refreshAll();
      }));

      if (status?.config_backup) {
        actions.append(button("Restaurar cfg", "", async () => {
          if (!confirm("Substituir as configurações atuais pelas salvas na nuvem?")) return;
          await configAction("extnest.ui.restore-config", installed.id);
          toast("Configurações restauradas.");
        }));
      }
    }

    wrap.appendChild(card);
  }

  renderDetected();
}

export function renderDetected() {
  const managedIds = new Set(
    state.registry.flatMap(item => [item.extension_id, item.expected_extension_id]).filter(Boolean)
  );
  const unmanaged = state.installed.filter(item => !managedIds.has(item.id));
  const wrap = document.getElementById("detectedList");
  wrap.innerHTML = "";

  if (!unmanaged.length) {
    wrap.innerHTML = `<div class="hint">Nenhuma extensão de desenvolvimento não gerenciada detectada.</div>`;
    return;
  }

  for (const item of unmanaged) {
    const row = document.createElement("div");
    row.className = "detected";
    row.innerHTML = `
      <div class="grow"><strong>${esc(item.name)}</strong><span>${esc(item.id)} · v${esc(item.version)}</span></div>
      <span class="badge">development</span>
    `;
    wrap.appendChild(row);
  }
}
