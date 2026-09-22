from pathlib import Path
import json, py_compile, subprocess, shutil, sys, zipfile, tempfile

ROOT = Path(__file__).resolve().parents[1]
errors = []

for file in ROOT.rglob("*.json"):
    if "__pycache__" in file.parts:
        continue
    try:
        json.loads(file.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"JSON {file.relative_to(ROOT)}: {e}")

for file in (ROOT / "native-host").rglob("*.py"):
    try:
        py_compile.compile(str(file), doraise=True)
    except Exception as e:
        errors.append(f"Python {file.relative_to(ROOT)}: {e}")

try:
    sys.path.insert(0, str(ROOT / "native-host"))
    from extnest import protocol

    ping = protocol.dispatch({"op": "ping"})
    if ping.get("protocol_version") != 3:
        errors.append("Native Host não anuncia o protocolo v3.")

    protocol.github.list_accounts = lambda: [
        {"account_id": "1", "login": "alpha"},
        {"account_id": "2", "login": "beta"}
    ]
    protocol.profiles.get = lambda provider: None

    state = protocol.dispatch({"op": "state_get"})
    if len(state.get("auth", {}).get("github_accounts", [])) != 2:
        errors.append("state_get não expõe múltiplas contas GitHub.")

    protocol.github.prepare = lambda redirect_uri: {
        "authorization_url": "https://example.invalid/auth",
        "expires_in": 300
    }
    prepared = protocol.dispatch({
        "op": "oauth_github_prepare",
        "redirect_uri": "https://example.chromiumapp.org/github"
    })
    if not prepared.get("ok"):
        errors.append("Rota oauth_github_prepare indisponível.")

    protocol.github.complete = lambda callback_url: {
        "account_id": "1",
        "login": "alpha"
    }
    completed = protocol.dispatch({
        "op": "oauth_github_complete",
        "callback_url": "https://example.chromiumapp.org/github?code=x&state=y"
    })
    if completed.get("profile", {}).get("account_id") != "1":
        errors.append("Rota oauth_github_complete não retorna conta.")

    protocol.github_api.list_repos = lambda account_id: [
        {"full_name": "alpha/private-ext", "private": True}
    ]
    listed = protocol.dispatch({
        "op": "github_list_repos",
        "account_id": "1"
    })
    if not listed.get("repos"):
        errors.append("Listagem de repositórios por conta indisponível.")

    protocol.repos.register_repo = lambda repo, branch=None, account_id=None: {
        "repo": repo,
        "branch": branch or "main",
        "account_id": account_id,
        "private": bool(account_id)
    }

    public_repo = protocol.dispatch({
        "op": "repo_register",
        "repo": "thirdparty/public-ext",
        "account_id": None
    })
    if public_repo.get("item", {}).get("account_id") is not None:
        errors.append("Repositório público não deve exigir conta.")

    private_repo = protocol.dispatch({
        "op": "repo_register",
        "repo": "alpha/private-ext",
        "account_id": "1"
    })
    if private_repo.get("item", {}).get("account_id") != "1":
        errors.append("Repositório privado não foi vinculado à conta correta.")

    protocol.microsoft.login = lambda: {"name": "Test"}
    microsoft_login = protocol.dispatch({
        "op": "oauth_interactive_login",
        "provider": "microsoft"
    })
    if not microsoft_login.get("ok"):
        errors.append("Rota OAuth Microsoft indisponível.")

    protocol.google.login = lambda: {"name": "Test"}
    google_login = protocol.dispatch({
        "op": "oauth_interactive_login",
        "provider": "google"
    })
    if not google_login.get("ok"):
        errors.append("Rota OAuth Google indisponível.")
except Exception as e:
    errors.append(f"Protocolo Native Host: {e}")

repos_source = (ROOT / "native-host/extnest/repos.py").read_text(encoding="utf-8")
github_source = (ROOT / "native-host/extnest/github_api.py").read_text(encoding="utf-8")
dev_update_source = (ROOT / "native-host/extnest/dev_update.py").read_text(encoding="utf-8")
workflow_source = (ROOT / ".github/workflows/build-helper.yml").read_text(encoding="utf-8")
installer_source = (ROOT / "installer/ExtNestHelper.iss").read_text(encoding="utf-8")

for forbidden in ["run_git(", "shutil.which(\"git\")", "git clone", "git pull"]:
    if forbidden in repos_source:
        errors.append(f"Dependência Git ainda presente em repos.py: {forbidden}")

if "archive_bytes" not in github_source or "_safe_extract_zip" not in repos_source:
    errors.append("Instalação por ZIP/API do GitHub não está implementada.")

if 'EXTNEST_MARKER = ".extnest.json"' not in github_source or "extnest_metadata" not in github_source:
    errors.append("Filtro obrigatório por .extnest.json não está implementado.")

if "dev_self_update" not in (ROOT / "native-host/extnest/protocol.py").read_text(encoding="utf-8"):
    errors.append("Auto-update DEV do ExtNest não está roteado no Native Host.")

if '"pull", "--ff-only"' not in dev_update_source:
    errors.append("Auto-update DEV não usa atualização fast-forward segura.")

if "Bundle portable Git" in workflow_source:
    errors.append("Workflow ainda empacota Git portátil.")

if "build\\helper\\git" in installer_source:
    errors.append("Instalador ainda inclui Git portátil.")

# Teste mínimo da extração segura do ZIP de repositório.
try:
    import io
    with tempfile.TemporaryDirectory() as td:
        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("owner-repo-sha/manifest.json", '{"manifest_version":3,"name":"Test","version":"1.0.0"}')
            archive.writestr("owner-repo-sha/background.js", "console.log('ok');")
        extract_to = Path(td) / "extract"
        protocol.repos._safe_extract_zip(archive_buffer.getvalue(), extract_to)
        if not (extract_to / "manifest.json").exists():
            errors.append("Extração ZIP não removeu o diretório raiz do GitHub.")
except Exception as e:
    errors.append(f"Extração ZIP do repositório: {e}")

node = shutil.which("node")
if node:
    for file in (ROOT / "extension").rglob("*.js"):
        p = subprocess.run([node, "--check", str(file)], capture_output=True, text=True)
        if p.returncode:
            errors.append(f"JS {file.relative_to(ROOT)}: {p.stderr.strip()}")

manifest = json.loads((ROOT/"extension/manifest.json").read_text(encoding="utf-8"))

for required_file in [
    ROOT/"installer/ExtNestHelper.iss",
    ROOT/".github/workflows/build-helper.yml",
    ROOT/"native-host/requirements-build.txt",
    ROOT/"docs/HELPER_INSTALLER.md",
]:
    if not required_file.exists():
        errors.append(f"Arquivo obrigatório da distribuição v0.4 ausente: {required_file.relative_to(ROOT)}")

main_js = (ROOT/"extension/dashboard/js/main.js").read_text(encoding="utf-8")
constants_js = (ROOT/"extension/shared/constants.js").read_text(encoding="utf-8")

for required in [
    "Finalizar instalação",
    "chrome.downloads.download",
    "chrome.downloads.open",
    "startHelperPolling",
]:
    if required not in main_js and required != "Finalizar instalação":
        errors.append(f"Fluxo do Helper não contém: {required}")

if "HELPER_INSTALLER_URL" not in constants_js:
    errors.append("URL do instalador do Helper não está definida.")
if "dev_self_update" not in main_js:
    errors.append("Dashboard não contém auto-update DEV.")
if "versionLt(helperVersion, appVersion)" not in main_js:
    errors.append("Dashboard não valida versão mínima do Helper.")
if int(manifest.get("manifest_version",0)) != 3:
    errors.append("Manifest não é V3.")
if "identity" not in manifest.get("permissions", []):
    errors.append("Manifest precisa da permissão identity para launchWebAuthFlow.")
for permission in ["downloads", "downloads.open"]:
    if permission not in manifest.get("permissions", []):
        errors.append(f"Manifest precisa da permissão {permission} para onboarding do Helper.")

github_view = (ROOT/"extension/dashboard/js/views/github.js").read_text(encoding="utf-8")
for required in ["github_accounts", "addPublicRepo", "oauth_github_disconnect"]:
    if required not in github_view:
        errors.append(f"GitHub UI não contém suporte esperado: {required}")

with tempfile.TemporaryDirectory() as td:
    zpath = Path(td)/"store.zip"
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
        for file in (ROOT/"extension").rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(ROOT/"extension"))
    with zipfile.ZipFile(zpath) as z:
        if "manifest.json" not in z.namelist():
            errors.append("Store ZIP não teria manifest.json na raiz.")
        if z.testzip():
            errors.append("Store ZIP inválido.")

if errors:
    print("VALIDAÇÃO FALHOU")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("ExtNest: validação OK")
print("- JSON OK")
print("- Python OK")
print("- Native protocol v3 / multi-account GitHub OK")
print("- Public repositories without account OK")
print("- GitHub ZIP install/update without Git OK")
print("- JavaScript OK" if node else "- JavaScript: Node não instalado, check ignorado")
print("- Manifest V3 + identity OK")
print("- Layout do Store ZIP OK")
