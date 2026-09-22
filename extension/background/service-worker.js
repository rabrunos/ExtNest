import { UPDATE_ALARM, DEFAULT_UPDATE_INTERVAL } from "../shared/constants.js";
import { checkForUpdatesAndNotify } from "./update-checker.js";
import { exportAndBackupConfig, restoreConfig, reloadManagedExtension } from "./config-bridge.js";

chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({ url: chrome.runtime.getURL("dashboard/index.html") });
});

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.alarms.create(UPDATE_ALARM, { periodInMinutes: DEFAULT_UPDATE_INTERVAL });
});

chrome.alarms.onAlarm.addListener(alarm => {
  if (alarm.name === UPDATE_ALARM) checkForUpdatesAndNotify();
});

chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  if (!sender?.id || message?.type !== "extnest.config.changed") return;

  (async () => {
    try {
      // Security boundary: native registry decides whether sender is managed.
      await exportAndBackupConfig(sender.id, "changed");
      sendResponse({ ok: true });
    } catch (error) {
      sendResponse({ ok: false, error: error.message });
    }
  })();

  return true;
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message?.type?.startsWith("extnest.ui.")) return;

  (async () => {
    try {
      if (message.type === "extnest.ui.backup-config") {
        sendResponse(await exportAndBackupConfig(message.extensionId, "manual"));
        return;
      }
      if (message.type === "extnest.ui.restore-config") {
        sendResponse({ ok: true, result: await restoreConfig(message.extensionId) });
        return;
      }
      if (message.type === "extnest.ui.reload") {
        sendResponse(await reloadManagedExtension(message.extensionId));
        return;
      }
      throw new Error("Comando desconhecido.");
    } catch (error) {
      sendResponse({ ok: false, error: error.message });
    }
  })();

  return true;
});
