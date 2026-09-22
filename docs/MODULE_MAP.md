# Mapa de módulos

Use este arquivo para decidir o que precisa ser lido antes de modificar o ExtNest.

## Login GitHub

Leia somente:
- `native-host/extnest/oauth/github.py`
- `native-host/extnest/oauth/tokens.py`
- `native-host/extnest/github_api.py`
- `extension/dashboard/js/views/github.js`

## Login Microsoft / OneDrive

Leia:
- `native-host/extnest/oauth/microsoft.py`
- `native-host/extnest/oauth/loopback.py`
- `native-host/extnest/cloud/onedrive.py`
- `extension/dashboard/js/views/cloud.js`

## Login Google / Google Drive

Leia:
- `native-host/extnest/oauth/google.py`
- `native-host/extnest/oauth/loopback.py`
- `native-host/extnest/cloud/google_drive.py`
- `extension/dashboard/js/views/cloud.js`

## Git / instalação / atualização de extensões

Leia:
- `native-host/extnest/repos.py`
- `native-host/extnest/github_api.py`
- `native-host/extnest/registry.py`
- `extension/dashboard/js/views/extensions.js`

## Lista de extensões

Leia:
- `native-host/extnest/registry.py`
- `native-host/extnest/protocol.py`
- `extension/dashboard/js/views/extensions.js`

## Backup de configurações de extensões

Leia:
- `native-host/extnest/config_backup.py`
- `native-host/extnest/cloud/manager.py`
- `extension/background/config-bridge.js`
- `templates/managed-extension/extnest/bridge.js`
- `docs/BRIDGE_PROTOCOL.md`

## OneDrive

Leia:
- `native-host/extnest/cloud/onedrive.py`
- `native-host/extnest/oauth/microsoft.py`

## Google Drive

Leia:
- `native-host/extnest/cloud/google_drive.py`
- `native-host/extnest/oauth/google.py`

## Protocolo Extension ↔ Native Host

Leia:
- `native-host/extnest/protocol.py`
- `native-host/extnest_host.py`
- `extension/shared/native-client.js`

## Service worker do ExtNest

Leia:
- `extension/background/service-worker.js`
- `extension/background/config-bridge.js`
- `extension/background/update-checker.js`

## Dashboard

Leia:
- `extension/dashboard/index.html`
- o arquivo específico em `extension/dashboard/js/views/`
- CSS necessário em `extension/dashboard/css/`

Não existe motivo para ler todos os módulos OAuth para modificar uma tela.

## Configuração OAuth do projeto

Leia:
- `native-host/oauth-clients.json`
- `docs/OAUTH_SETUP.md`

## Nova extensão compatível

Leia:
- `docs/AI_EXTENSION_STANDARD.md`
- `docs/BRIDGE_PROTOCOL.md`
- `templates/managed-extension/`
