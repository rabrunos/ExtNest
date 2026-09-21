(() => {
  const C = globalThis.EXTNEST_BRIDGE_CONFIG;
  if (!C?.vaultExtensionId) { console.warn('[ExtNest] bridge-config.js não carregado.'); return; }
  let notifyTimer=null, suppressChanges=false;

  async function exportConfig(){
    const raw=await chrome.storage.local.get(Array.isArray(C.backupKeys)?C.backupKeys:[]);
    const data=C.exportTransform?await C.exportTransform(raw):raw;
    return {ok:true,protocol:C.protocol||1,schema:C.schema||1,data};
  }
  async function importConfig(payload){
    if(!payload||typeof payload!=='object')throw new Error('Payload inválido.');
    const fromSchema=Number(payload.schema||1);let data=payload.data||{};
    if(C.importTransform)data=await C.importTransform(data,fromSchema);
    suppressChanges=true;try{await chrome.storage.local.set(data)}finally{setTimeout(()=>suppressChanges=false,500)}
    return {ok:true};
  }

  chrome.runtime.onMessageExternal.addListener((message,sender,sendResponse)=>{
    if(sender.id!==C.vaultExtensionId)return;
    (async()=>{try{
      if(message?.type==='extnest.ping'){sendResponse({ok:true,protocol:C.protocol||1,schema:C.schema||1});return}
      if(message?.type==='extnest.config.export'){sendResponse(await exportConfig());return}
      if(message?.type==='extnest.config.import'){sendResponse(await importConfig(message.payload));return}
      if(message?.type==='extnest.reload'){sendResponse({ok:true});setTimeout(()=>chrome.runtime.reload(),60);return}
      sendResponse({ok:false,error:'Comando ExtNest desconhecido.'});
    }catch(e){sendResponse({ok:false,error:e.message})}})();return true;
  });

  chrome.storage.onChanged.addListener((changes,area)=>{
    if(area!=='local'||suppressChanges)return;
    const keys=new Set(C.backupKeys||[]);if(!Object.keys(changes).some(k=>keys.has(k)))return;
    clearTimeout(notifyTimer);notifyTimer=setTimeout(()=>{
      chrome.runtime.sendMessage(C.vaultExtensionId,{type:'extnest.config.changed',protocol:C.protocol||1}).catch(()=>{});
    },1500);
  });
})();
