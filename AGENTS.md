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
- `native-host/extnest/repos.py` contém download ZIP, extração e implantação das extensões.
- `native-host/extnest/registry.py` contém a lista de extensões.
- `native-host/extnest/config_backup.py` contém backup/restauração das configurações das extensões.
- Extensões gerenciadas usam o ExtNest Bridge v1.
- Todo repositório gerenciado deve possuir `.extnest.json` válido na raiz; a listagem GitHub mostra somente repositórios com esse marcador.
- Segredos/tokens nunca entram em Git, OneDrive ou Google Drive.
- OAuth tokens ficam protegidos localmente por DPAPI.
- Client IDs OAuth são identificadores públicos e ficam em `native-host/oauth-clients.json`.
- Atualização de extensões gerenciadas é manual: detectar/notificar automaticamente, atualizar somente após ação do usuário.
- GitHub é fonte **somente de leitura/download** para o ExtNest.
- Nunca implementar push, criação de commits remotos ou edição remota de código no ExtNest.
- O escopo OAuth `repo` é tecnicamente read/write porque o GitHub não fornece read-only para código privado; portanto essa restrição deve ser reforçada no código.
- Edição de código acontece fora do ExtNest, no repositório-fonte normal.
- O Helper final é instalado por `ExtNestHelperSetup.exe`; nunca exigir PowerShell, Python, Git for Windows, edição de JSON ou Registro do usuário final.
- Scripts em `native-host/setup/` são exclusivamente para desenvolvimento.
- O Helper distribuído deve ser autocontido: `ExtNestHost.exe` + configuração OAuth empacotada. Não incluir Git.
- A Edge Add-ons instala somente a extensão. Quando o Helper estiver ausente, a UI deve oferecer **Finalizar instalação** e nunca exibir o erro cru de Native Messaging como instrução ao usuário.

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
- não existe dependência de Git para instalar/atualizar extensões gerenciadas;
- `native-host/extnest/dev_update.py` pode usar o Git já instalado apenas no fluxo DEV de auto-update do próprio checkout ExtNest; esse Git nunca é empacotado no Helper final;
- ZIP de Store coloca `manifest.json` na raiz.
