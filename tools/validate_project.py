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
    if ping.get("protocol_version") != 2:
        errors.append("Native Host não anuncia o protocolo v2.")

    protocol.github.login = lambda: {"login": "test", "name": "Test"}
    github_login = protocol.dispatch({
        "op": "oauth_interactive_login",
        "provider": "github"
    })
    if not github_login.get("ok"):
        errors.append("Rota OAuth GitHub interativa indisponível.")

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
if 'run_git(["push"' in repos_source or "run_git(['push'" in repos_source:
    errors.append("ExtNest GitHub layer contains git push, which is forbidden.")

node = shutil.which("node")
if node:
    for file in (ROOT / "extension").rglob("*.js"):
        p = subprocess.run([node, "--check", str(file)], capture_output=True, text=True)
        if p.returncode:
            errors.append(f"JS {file.relative_to(ROOT)}: {p.stderr.strip()}")

manifest = json.loads((ROOT/"extension/manifest.json").read_text(encoding="utf-8"))
if int(manifest.get("manifest_version",0)) != 3:
    errors.append("Manifest não é V3.")

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
print("- Native protocol v2 / OAuth routing OK")
print("- JavaScript OK" if node else "- JavaScript: Node não instalado, check ignorado")
print("- Manifest V3 OK")
print("- Layout do Store ZIP OK")
