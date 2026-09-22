import { nativeMessage } from "../shared/native-client.js";

export async function checkForUpdatesAndNotify() {
  try {
    const response = await nativeMessage("repo_check_all");
    if (!response?.ok) return;

    const outdated = (response.items || []).filter(item => item.installed && item.update_available);
    if (!outdated.length) return;

    const message = outdated.length === 1
      ? `${outdated[0].name} tem uma versão nova no GitHub.`
      : `${outdated.length} extensões têm versões novas no GitHub.`;

    await chrome.notifications.create("extnest-updates", {
      type: "basic",
      iconUrl: chrome.runtime.getURL("icons/icon128.png"),
      title: "ExtNest",
      message
    });
  } catch {}
}
