# ExtNest

ExtNest é um gerenciador privado de extensões Chromium/Edge.

## Arquitetura

```text
GitHub público ou privado
    │ código
    ▼
ExtNest Native Host
    │
    ├── %LOCALAPPDATA%\ExtNest\Extensions
    │       │
    │       └── extensões privadas carregadas como unpacked
    │
    └── backup de configurações
            │
            ├── Google Drive appDataFolder (oculta)
            └── OneDrive App Folder (Apps/ExtNest)
```

O **ExtNest em si** pode ser publicado na Microsoft Edge Add-ons e Chrome Web Store.

As extensões gerenciadas podem vir de repositórios privados ou públicos. Repositórios públicos podem ser usados sem login.

## v0.5

- Git removido completamente do Helper;
- instalação e atualização usam o ZIP oficial da branch pelo GitHub API;
- repositórios privados usam a conta GitHub já conectada;
- repositórios públicos continuam funcionando sem conta;
- verificação periódica continua lendo o `manifest.json` remoto e comparando versões;
- atualização continua manual: o ExtNest apenas avisa até o usuário clicar;
- extração segura com bloqueio de caminhos fora da pasta da extensão;
- atualização troca a pasta de forma transacional e restaura a anterior se falhar;
- clones antigos com `.git` são migrados automaticamente na próxima instalação/atualização;
- Git portátil removido do instalador, reduzindo drasticamente o tamanho do Helper;
- `.extnest.json` é o marcador obrigatório de compatibilidade;
- a lista do GitHub mostra somente repositórios compatíveis;
- o ExtNest carregado como extensão DEV pode atualizar o próprio checkout local pelo botão **Atualizar ExtNest**, sem terminal.

## v0.4

- primeira execução com **Finalizar instalação** quando o Helper estiver ausente;
- download do instalador diretamente pelo ExtNest;
- botão muda para **Abrir instalador** quando o download termina;
- detecção automática do Helper após a instalação;
- `ExtNestHost.exe` empacotado com PyInstaller;
- Git portátil incluído no Helper (removido na v0.5);
- instalador por usuário em `%LOCALAPPDATA%\ExtNest\NativeHost`;
- registro de Native Messaging para Edge/Chrome automático;
- sem Python, Git for Windows, PowerShell, JSON ou Registro para usuário final;
- pipeline GitHub Actions gera `ExtNestHelperSetup.exe`;
- Release pública serve como origem do instalador;
- suporte a IDs DEV + Edge Add-ons + Chrome Web Store no manifest nativo.

## v0.3

- múltiplas contas GitHub simultâneas;
- cada repositório privado fica vinculado à conta correta;
- repositórios públicos podem ser adicionados sem conta;
- seletor de contas do GitHub forçado no login;
- OAuth via `chrome.identity.launchWebAuthFlow`;
- PKCE S256 + state;
- tokens GitHub separados por conta e protegidos por DPAPI;
- clones públicos sem credenciais;
- clones privados usam somente o token da conta associada;
- slugs novos usam `owner--repo` para evitar colisões.

## v0.2

- projeto refatorado em módulos pequenos;
- GitHub PAT removido;
- GitHub OAuth (substituído pelo fluxo PKCE/chrome.identity na v0.3);
- refresh de token automático;
- Microsoft OAuth Authorization Code + PKCE;
- Google OAuth Installed App + PKCE;
- OneDrive `Files.ReadWrite.AppFolder`;
- Google Drive `drive.appdata`;
- Google backup oculto no `appDataFolder`;
- bootstrap da lista de extensões em PC novo;
- tokens locais protegidos por Windows DPAPI;
- Git continua sendo a fonte do código;
- atualização detectada automaticamente, mas executada apenas quando o usuário clicar.

## Estrutura

```text
extension/
├── background/
├── dashboard/
│   ├── css/
│   └── js/
│       ├── api/
│       ├── ui/
│       └── views/
├── shared/
└── icons/

native-host/
├── extnest/
│   ├── oauth/
│   └── cloud/
├── oauth-clients.json
├── extnest_host.py
└── setup/

docs/
templates/
tools/
```

## Para IA/agentes

Leia primeiro:

```text
AGENTS.md
docs/MODULE_MAP.md
```

Não leia o repositório inteiro sem necessidade.

Para criar uma extensão compatível:

```text
docs/AI_EXTENSION_STANDARD.md
```

## Configuração OAuth antes de testar

Leia:

```text
docs/OAUTH_SETUP.md
```

É necessário cadastrar uma vez os Client IDs do:
- GitHub;
- Microsoft;
- Google.

Depois disso, o usuário final não digita tokens.

## Desenvolvimento local

ExtNest development ID:

```text
econfanmnmmcggpgdflcipmdlmkcbiag
```

Para testar o Native Host a partir do repositório:

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\register-dev-host.ps1
```

Depois carregue `extension/` como unpacked.

## Store

Gere o ZIP da extensão:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build-store-package.ps1
```

O Native Host não entra no ZIP da Store.

## Validação

```powershell
python .\tools\validate_project.py
```

## Repositório

https://github.com/rabrunos/ExtNest
