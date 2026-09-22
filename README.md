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
