import { state } from "../state.js";
import { nativeOk } from "../api/native.js";
import { UPDATE_ALARM } from "../../../shared/constants.js";

export function renderSettings() {
  const settings = state.settings || {};
  document.getElementById("autoCheck").checked = settings.auto_check !== false;
  document.getElementById("checkInterval").value = String(settings.check_interval || 360);
  document.getElementById("autoConfigBackup").checked = settings.auto_config_backup !== false;
  document.getElementById("askRestore").checked = settings.ask_restore !== false;
  document.getElementById("extensionsPath").textContent = state.paths?.extensions || "—";
  document.getElementById("dataPath").textContent = state.paths?.data || "—";
}

export async function saveSettings() {
  const settings = {
    auto_check: document.getElementById("autoCheck").checked,
    check_interval: Number(document.getElementById("checkInterval").value),
    auto_config_backup: document.getElementById("autoConfigBackup").checked,
    ask_restore: document.getElementById("askRestore").checked
  };

  await nativeOk("settings_set", { settings });
  state.settings = { ...(state.settings || {}), ...settings };

  if (settings.auto_check) {
    await chrome.alarms.create(UPDATE_ALARM, { periodInMinutes: settings.check_interval });
  } else {
    await chrome.alarms.clear(UPDATE_ALARM);
  }
}
