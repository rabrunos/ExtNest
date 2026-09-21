#!/usr/bin/env python3
import sys, os, json, struct, subprocess, urllib.request, urllib.parse, urllib.error
import base64, hashlib, re, shutil, ctypes, ctypes.wintypes
from pathlib import Path
from datetime import datetime, timezone

APP='ExtNest'; HOST_NAME='com.extnest.host'
LOCAL=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/APP
DATA=LOCAL/'Data'; EXTENSIONS=LOCAL/'Extensions'; SECRETS=DATA/'secrets'
REGISTRY=DATA/'registry.json'; SETTINGS=DATA/'settings.json'; TOKEN_FILE=SECRETS/'github.token'
for d in (DATA,EXTENSIONS,SECRETS): d.mkdir(parents=True,exist_ok=True)

def jload(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except:return default

def jsave(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)

def now_iso():return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
def defaults():return {'auto_check':True,'check_interval':360,'auto_config_backup':True,'ask_restore':True,'cloud':None}
def settings():
    s=defaults();s.update(jload(SETTINGS,{}));return s
def registry():return jload(REGISTRY,{'schema':1,'extensions':[]})
def save_registry(r):jsave(REGISTRY,r);sync_vault_files()

class DATA_BLOB(ctypes.Structure):
    _fields_=[('cbData',ctypes.wintypes.DWORD),('pbData',ctypes.POINTER(ctypes.c_byte))]
def _blob(data):
    buf=ctypes.create_string_buffer(data);return DATA_BLOB(len(data),ctypes.cast(buf,ctypes.POINTER(ctypes.c_byte))),buf
def protect(data):
    if os.name!='nt':return b'DEV0'+data
    i,k=_blob(data);o=DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(i),None,None,None,None,0,ctypes.byref(o)):raise ctypes.WinError()
    try:return ctypes.string_at(o.pbData,o.cbData)
    finally:ctypes.windll.kernel32.LocalFree(o.pbData)
def unprotect(data):
    if data.startswith(b'DEV0'):return data[4:]
    if os.name!='nt':return data
    i,k=_blob(data);o=DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(i),None,None,None,None,0,ctypes.byref(o)):raise ctypes.WinError()
    try:return ctypes.string_at(o.pbData,o.cbData)
    finally:ctypes.windll.kernel32.LocalFree(o.pbData)
def set_token(t):TOKEN_FILE.write_bytes(protect(t.encode()))
def get_token():
    if not TOKEN_FILE.exists():return None
    try:return unprotect(TOKEN_FILE.read_bytes()).decode()
    except:return None

def github_api(path,method='GET',body=None):
    token=get_token()
    if not token:raise RuntimeError('GitHub não conectado.')
    headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28','User-Agent':'ExtNest/0.1'}
    data=None
    if body is not None:data=json.dumps(body).encode();headers['Content-Type']='application/json'
    req=urllib.request.Request('https://api.github.com'+path,data=data,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read();return json.loads(raw.decode()) if raw else None
    except urllib.error.HTTPError as e:
        text=e.read().decode('utf-8','replace')
        try:msg=json.loads(text).get('message',text)
        except:msg=text
        raise RuntimeError(f'GitHub HTTP {e.code}: {msg}')
def github_user():return github_api('/user')
def github_repos():
    out=[];page=1
    while True:
        batch=github_api(f'/user/repos?per_page=100&page={page}&affiliation=owner,collaborator,organization_member&sort=updated')
        if not batch:break
        out += [{'full_name':r['full_name'],'private':bool(r.get('private')),'description':r.get('description'),'default_branch':r.get('default_branch') or 'main','html_url':r.get('html_url')} for r in batch]
        if len(batch)<100 or page>=10:break
        page+=1
    return out
def github_file(repo,path,branch):
    q=urllib.parse.quote(path,safe='/');ref=urllib.parse.quote(branch,safe='');obj=github_api(f'/repos/{repo}/contents/{q}?ref={ref}')
    if obj.get('encoding')=='base64':return base64.b64decode(obj['content']).decode()
    raise RuntimeError('Conteúdo remoto inesperado.')

def git_exe():
    p=shutil.which('git')
    if not p:raise RuntimeError('Git não encontrado no PATH. Instale Git for Windows.')
    return p
def run_git(args,cwd=None,check=True):
    cmd=[git_exe()];tok=get_token()
    if tok:cmd += ['-c',f'http.extraHeader=Authorization: Bearer {tok}']
    cmd += args
    p=subprocess.run(cmd,cwd=str(cwd) if cwd else None,text=True,capture_output=True,encoding='utf-8',errors='replace')
    if check and p.returncode!=0:raise RuntimeError((p.stderr or p.stdout or 'Erro Git').strip())
    return p

def slugify(repo):return re.sub(r'[^a-zA-Z0-9._-]+','-',repo.split('/')[-1]).strip('-').lower()
def item_slug(slug):return next((x for x in registry()['extensions'] if x['slug']==slug),None)
def item_eid(eid):return next((x for x in registry()['extensions'] if x.get('extension_id')==eid or x.get('expected_extension_id')==eid),None)
def extid_from_key(key):
    try:
        raw=base64.b64decode(key);d=hashlib.sha256(raw).digest()[:16];a='abcdefghijklmnop';return ''.join(a[b>>4]+a[b&15] for b in d)
    except:return None
def local_manifest(slug):
    p=EXTENSIONS/slug/'manifest.json';return jload(p,None) if p.exists() else None
def remote_manifest(item):
    try:return json.loads(github_file(item['repo'],'manifest.json',item.get('branch','main')))
    except:return None
def cmpver(a,b):
    def p(v):return tuple(int(x) for x in re.findall(r'\d+',str(v))[:4])
    x,y=p(a),p(b);n=max(len(x),len(y));x+=((0,)*(n-len(x)));y+=((0,)*(n-len(y)));return (x>y)-(x<y)

def cloud_root():
    c=settings().get('cloud');return Path(c['path'])/'ExtNest' if c and c.get('path') else None
def sync_vault_files():
    root=cloud_root()
    if not root:return
    try:
        (root/'vault').mkdir(parents=True,exist_ok=True);jsave(root/'vault/extensions.json',registry());s=settings().copy();s.pop('cloud',None);jsave(root/'vault/settings.json',{'schema':1,'settings':s,'saved_at':now_iso()})
    except:pass
def cfgpath(slug):
    r=cloud_root();return (r/'extensions'/slug/'config.json') if r else (DATA/'CloudMirror/extensions'/slug/'config.json')
def metapath(slug):
    r=cloud_root();return (r/'extensions'/slug/'metadata.json') if r else (DATA/'CloudMirror/extensions'/slug/'metadata.json')
def detect_cloud():
    out=[];seen=set()
    def add(provider,p):
        if not p:return
        x=Path(p);k=str(x).lower()
        if x.exists() and k not in seen:seen.add(k);out.append({'provider':provider,'path':str(x)})
    for e in ('OneDrive','OneDriveConsumer','OneDriveCommercial'):add('OneDrive',os.environ.get(e))
    h=Path.home();
    for p in (h/'Google Drive',h/'My Drive',Path(os.environ.get('USERPROFILE',str(h)))/'Google Drive'):add('Google Drive',p)
    if os.name=='nt':
        for l in 'GHIJKLMNOPQRSTUVWXYZ':add('Google Drive',Path(f'{l}:/My Drive'))
    return out

def repo_status(item):
    local=local_manifest(item['slug']);remote=remote_manifest(item);lv=(local or {}).get('version');rv=(remote or {}).get('version');k=(local or remote or {}).get('key');expected=extid_from_key(k) if k else item.get('expected_extension_id')
    if expected and item.get('expected_extension_id')!=expected:
        r=registry()
        for x in r['extensions']:
            if x['slug']==item['slug']:x['expected_extension_id']=expected
        jsave(REGISTRY,r)
    return {'ok':True,'slug':item['slug'],'name':(remote or local or {}).get('name') or item.get('name') or item['slug'],'local_exists':(EXTENSIONS/item['slug']/'manifest.json').exists(),'local_path':str(EXTENSIONS/item['slug']),'local_version':lv,'remote_version':rv,'expected_extension_id':expected,'update_available':bool(lv and rv and cmpver(rv,lv)>0),'config_backup':cfgpath(item['slug']).exists(),'config_cloud':bool(cloud_root() and cfgpath(item['slug']).exists())}
def repo_register(repo,branch):
    m=json.loads(github_file(repo,'manifest.json',branch))
    if int(m.get('manifest_version',0))<3:raise RuntimeError('manifest.json não é Manifest V3.')
    slug=slugify(repo);r=registry();x=next((i for i in r['extensions'] if i['repo'].lower()==repo.lower()),None);expected=extid_from_key(m.get('key','')) if m.get('key') else None
    if x:x.update({'branch':branch,'name':m.get('name',slug),'expected_extension_id':expected or x.get('expected_extension_id')});item=x
    else:item={'slug':slug,'repo':repo,'branch':branch,'name':m.get('name',slug),'expected_extension_id':expected,'extension_id':None,'added_at':now_iso()};r['extensions'].append(item)
    save_registry(r);return item
def repo_install(item):
    path=EXTENSIONS/item['slug']
    if path.exists():
        if (path/'.git').exists():return path
        shutil.rmtree(path)
    run_git(['clone','--branch',item.get('branch','main'),'--single-branch',f"https://github.com/{item['repo']}.git",str(path)]);return path
def repo_update(item):
    path=EXTENSIONS/item['slug']
    if not (path/'.git').exists():raise RuntimeError('Repositório ainda não foi instalado.')
    if run_git(['status','--porcelain'],cwd=path).stdout.strip():raise RuntimeError('Há alterações locais. Envie ou reverta antes de atualizar.')
    run_git(['pull','--ff-only','origin',item.get('branch','main')],cwd=path)

def dispatch(req):
    op=req.get('op')
    if op=='ping':return {'ok':True,'name':'ExtNest Host','version':'0.1.0','python':sys.version.split()[0]}
    if op=='state_get':
        user=None
        if get_token():
            try:
                u=github_user();user={'login':u.get('login'),'name':u.get('name')}
            except:user={'login':'conectado','name':None}
        s=settings();return {'ok':True,'registry':registry()['extensions'],'github':user,'cloud':s.get('cloud'),'settings':s,'paths':{'extensions':str(EXTENSIONS),'data':str(DATA)}}
    if op=='settings_get':return {'ok':True,'settings':settings()}
    if op=='github_set_token':
        tok=(req.get('token') or '').strip()
        if not tok:raise RuntimeError('Token vazio.')
        set_token(tok)
        try:u=github_user()
        except:TOKEN_FILE.unlink(missing_ok=True);raise
        return {'ok':True,'user':{'login':u.get('login'),'name':u.get('name')}}
    if op=='github_clear_token':TOKEN_FILE.unlink(missing_ok=True);return {'ok':True}
    if op=='github_list_repos':return {'ok':True,'repos':github_repos()}
    if op=='repo_register':return {'ok':True,'item':repo_register(req['repo'],req.get('branch') or 'main')}
    if op=='repo_install':
        i=item_slug(req['slug']);
        if not i:raise RuntimeError('Extensão não registrada.')
        p=repo_install(i);return {'ok':True,'path':str(p),**repo_status(i)}
    if op=='repo_update':
        i=item_slug(req['slug']);
        if not i:raise RuntimeError('Extensão não registrada.')
        repo_update(i);return repo_status(i)
    if op=='repo_status':
        i=item_slug(req['slug']);
        if not i:raise RuntimeError('Extensão não registrada.')
        return repo_status(i)
    if op=='repo_check_all':
        arr=[]
        for i in registry()['extensions']:
            s=repo_status(i);s['installed']=s['local_exists'];arr.append(s)
        return {'ok':True,'items':arr}
    if op=='repo_open':
        i=item_slug(req['slug']);
        if not i:raise RuntimeError('Extensão não registrada.')
        p=EXTENSIONS/i['slug'];os.startfile(str(p)) if os.name=='nt' else subprocess.Popen(['xdg-open',str(p)]);return {'ok':True}
    if op=='registry_find_extension':return {'ok':True,'item':item_eid(req['extension_id'])}
    if op=='registry_link_extension':
        r=registry()
        for x in r['extensions']:
            if x['slug']==req['slug']:x['extension_id']=req['extension_id']
        save_registry(r);return {'ok':True}
    if op=='registry_set_restore_prompt':
        r=registry()
        for x in r['extensions']:
            if x['slug']==req['slug']:x['ask_restore']=bool(req.get('value'))
        save_registry(r);return {'ok':True}
    if op=='cloud_detect':return {'ok':True,'candidates':detect_cloud()}
    if op=='cloud_set':
        p=Path(req['path'])
        if not p.exists():raise RuntimeError('Pasta não existe.')
        # If this cloud already contains an ExtNest registry, restore the selected repo list first.
        remote_registry=jload(p/'ExtNest/vault/extensions.json',None)
        if isinstance(remote_registry,dict) and isinstance(remote_registry.get('extensions'),list):
            jsave(REGISTRY,remote_registry)
        remote_settings=jload(p/'ExtNest/vault/settings.json',None)
        s=settings()
        if isinstance(remote_settings,dict) and isinstance(remote_settings.get('settings'),dict):
            for k in ('auto_check','check_interval','auto_config_backup','ask_restore'):
                if k in remote_settings['settings']:s[k]=remote_settings['settings'][k]
        s['cloud']={'provider':req['provider'],'path':str(p),'set_at':now_iso()};jsave(SETTINGS,s);sync_vault_files();return {'ok':True,'cloud':s['cloud'],'registry_imported':bool(remote_registry)}
    if op=='settings_set':
        s=settings();inc=req.get('settings') or {}
        for k in ('auto_check','check_interval','auto_config_backup','ask_restore'):
            if k in inc:s[k]=inc[k]
        jsave(SETTINGS,s);sync_vault_files();return {'ok':True}
    if op=='config_backup':
        slug=req['slug'];payload=req.get('payload')
        if payload is None:raise RuntimeError('Payload ausente.')
        obj={'schema':1,'slug':slug,'extension_id':req.get('extension_id'),'extension_version':req.get('extension_version'),'saved_at':now_iso(),'reason':req.get('reason','manual'),'payload':payload};jsave(cfgpath(slug),obj);i=item_slug(slug) or {};jsave(metapath(slug),{'schema':1,'slug':slug,'repo':i.get('repo'),'saved_at':now_iso()});return {'ok':True,'path':str(cfgpath(slug)),'cloud':bool(cloud_root())}
    if op=='config_restore':
        obj=jload(cfgpath(req['slug']),None)
        return {'ok':True,'payload':obj.get('payload'),'saved_at':obj.get('saved_at')} if obj else {'ok':False,'error':'Backup de configurações não encontrado.'}
    raise RuntimeError('Operação desconhecida: '+str(op))

def read_message():
    raw=sys.stdin.buffer.read(4)
    if not raw:return None
    n=struct.unpack('=I',raw)[0];return json.loads(sys.stdin.buffer.read(n).decode())
def send_message(o):
    data=json.dumps(o,ensure_ascii=False,separators=(',',':')).encode();sys.stdout.buffer.write(struct.pack('=I',len(data)));sys.stdout.buffer.write(data);sys.stdout.buffer.flush()
def main():
    if os.name=='nt':
        try:
            import msvcrt;msvcrt.setmode(sys.stdin.fileno(),os.O_BINARY);msvcrt.setmode(sys.stdout.fileno(),os.O_BINARY)
        except:pass
    while True:
        req=read_message()
        if req is None:break
        try:resp=dispatch(req)
        except Exception as e:resp={'ok':False,'error':str(e)}
        send_message(resp)
if __name__=='__main__':main()
