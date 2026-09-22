import { nativeOk } from "../shared/native-client.js";

async function managedExtensionInfo(extensionId) {
  try {
    const info = await chrome.management.get(extensionId);
    if (!info || info.type !== "extension" || info.installType !== "development") return null;
    return info;
  } catch {
    return null;
  }
}

export async function exportAndBackupConfig(extensionId, reason = "manual") {
  const info = await managedExtensionInfo(extensionId);
  if (!info) throw new Error("Extensão não está instalada como development.");

  const lookup = await nativeOk("registry_find_extension", { extension_id: extensionId });
  if (!lookup.item) throw new Error("Extensão não está registrada no ExtNest.");

  const response = await chrome.runtime.sendMessage(extensionId, {
    type: "extnest.config.export",
    protocol: 1
  });
  if (!response?.ok) throw new Error(response?.error || "A extensão não respondeu ao Bridge.");

  return nativeOk("config_backup", {
    slug: lookup.item.slug,
    extension_id: extensionId,
    extension_version: info.version,
    reason,
    payload: response
  });
}

export async function restoreConfig(extensionId) {
  const lookup = await nativeOk("registry_find_extension", { extension_id: extensionId });
  if (!lookup.item) throw new Error("Extensão não registrada.");

  const backup = await nativeOk("config_restore", { slug: lookup.item.slug });
  if (!backup.payload) throw new Error("Backup não encontrado.");

  const result = await chrome.runtime.sendMessage(extensionId, {
    type: "extnest.config.import",
    protocol: 1,
    payload: backup.payload
  });
  if (!result?.ok) throw new Error(result?.error || "Falha ao restaurar.");
  return result;
}

export async function reloadManagedExtension(extensionId) {
  return chrome.runtime.sendMessage(extensionId, {
    type: "extnest.reload",
    protocol: 1
  });
}
