# AGENTS.md — ExtNest

Este projeto é deliberadamente modular.

## Regra principal para IA/agentes

**NÃO leia o projeto inteiro por padrão.**

1. Leia primeiro `docs/MODULE_MAP.md`.
2. Identifique o módulo relacionado à tarefa.
3. Leia apenas os arquivos indicados para esse módulo e suas dependências diretas.
4. Só expanda para outros módulos se houver uma dependência concreta.

## Regras arquiteturais

- Não recriar arquivos monolíticos.
- UI não implementa OAuth, Git ou nuvem diretamente.
- `extension/` conversa com o sistema operacional apenas via Native Messaging.
- `native-host/extnest/oauth/` contém autenticação.
- `native-host/extnest/cloud/` contém armazenamento remoto.
- `native-host/extnest/repos.py` contém operações Git.
- `native-host/extnest/registry.py` contém a lista de extensões.
- `native-host/extnest/config_backup.py` contém backup/restauração das configurações das extensões.
- Extensões gerenciadas usam o ExtNest Bridge v1.
- Segredos/tokens nunca entram em Git, OneDrive ou Google Drive.
- OAuth tokens ficam protegidos localmente por DPAPI.
- Client IDs OAuth são identificadores públicos e ficam em `native-host/oauth-clients.json`.
- Atualização de extensões gerenciadas é manual: detectar/notificar automaticamente, atualizar somente após ação do usuário.
- **GitHub é somente leitura para o ExtNest.**
- O código pode usar clone/fetch/pull, mas nunca implementar push/commit remoto pelo ExtNest.
- Edição de código acontece fora do ExtNest, no repositório-fonte normal da extensão.

## IDs do ExtNest

Development ID atual:

`econfanmnmmcggpgdflcipmdlmkcbiag`

IDs das Stores devem ser registrados em `docs/STORE_IDS.md` quando existirem.

## Antes de entregar uma mudança

Execute:

```powershell
python .\tools\validate_project.py
```

E confirme:
- Python compila;
- JavaScript passa no `node --check`, se Node estiver instalado;
- JSONs são válidos;
- ZIP de Store coloca `manifest.json` na raiz.
