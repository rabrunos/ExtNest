const HOST = 'com.extnest.host';
const CHECK_ALARM = 'extnest-check-updates';

function nativeMessage(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendNativeMessage(HOST, message, response => {
      const err = chrome.runtime.lastError;
      if (err) reject(new Error(err.message));
      else resolve(response);
    });
  });
}

async function managedExtensionInfo(extensionId) {
  try {
    const info = await chrome.management.get(extensionId);
    if (!info || info.type !== 'extension' || info.installType !== 'development') return null;
    return info;
  } catch { return null; }
}

async function exportAndBackupConfig(extensionId, reason='manual') {
  const info = await managedExtensionInfo(extensionId);
  if (!info) throw new Error('Extensão não é uma extensão de desenvolvimento instalada.');
  const lookup = await nativeMessage({op:'registry_find_extension', extension_id:extensionId});
  if (!lookup?.ok || !lookup.item) throw new Error('Extensão não está registrada no ExtNest.');
  const response = await chrome.runtime.sendMessage(extensionId, {type:'extnest.config.export', protocol:1});
  if (!response?.ok) throw new Error(response?.error || 'A extensão não respondeu ao bridge.');
  return nativeMessage({
    op:'config_backup', slug:lookup.item.slug, extension_id:extensionId,
    extension_version:info.version, reason, payload:response
  });
}

chrome.action.onClicked.addListener(() => chrome.tabs.create({url: chrome.runtime.getURL('dashboard.html')}));
chrome.runtime.onInstalled.addListener(() => chrome.alarms.create(CHECK_ALARM, {periodInMinutes:360}));

chrome.alarms.onAlarm.addListener(async alarm => {
  if (alarm.name !== CHECK_ALARM) return;
  try {
    const r = await nativeMessage({op:'repo_check_all'});
    const outdated = (r?.items || []).filter(x => x.installed && x.update_available);
    if (outdated.length) {
      chrome.notifications.create('extnest-updates', {
        type:'basic', iconUrl:'icons/icon128.png', title:'ExtNest',
        message: outdated.length === 1 ? `${outdated[0].name} tem uma versão nova no GitHub.` : `${outdated.length} extensões têm versões novas no GitHub.`
      });
    }
  } catch {}
});

chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  if (!sender?.id || message?.type !== 'extnest.config.changed') return;
  (async () => {
    try {
      const cfg = await nativeMessage({op:'settings_get'});
      if (cfg?.settings?.auto_config_backup === false) { sendResponse({ok:true,skipped:true}); return; }
      await exportAndBackupConfig(sender.id, 'changed'); sendResponse({ok:true});
    } catch (e) { sendResponse({ok:false,error:e.message}); }
  })();
  return true;
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message?.type?.startsWith('extnest.ui.')) return;
  (async () => {
    try {
      if (message.type === 'extnest.ui.backup-config') {
        sendResponse(await exportAndBackupConfig(message.extensionId, 'manual')); return;
      }
      if (message.type === 'extnest.ui.restore-config') {
        const lookup = await nativeMessage({op:'registry_find_extension', extension_id:message.extensionId});
        if (!lookup?.ok || !lookup.item) throw new Error('Extensão não registrada.');
        const backup = await nativeMessage({op:'config_restore', slug:lookup.item.slug});
        if (!backup?.ok || !backup.payload) throw new Error(backup?.error || 'Backup não encontrado.');
        const result = await chrome.runtime.sendMessage(message.extensionId, {type:'extnest.config.import',protocol:1,payload:backup.payload});
        if (!result?.ok) throw new Error(result?.error || 'Falha ao restaurar.');
        sendResponse({ok:true,result}); return;
      }
      if (message.type === 'extnest.ui.reload') {
        const result = await chrome.runtime.sendMessage(message.extensionId, {type:'extnest.reload',protocol:1});
        sendResponse(result || {ok:true}); return;
      }
      throw new Error('Comando desconhecido.');
    } catch (e) { sendResponse({ok:false,error:e.message}); }
  })();
  return true;
});
