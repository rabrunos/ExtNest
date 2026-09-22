# Changelog

## 0.2.0

### Autenticação
- removido Personal Access Token manual do GitHub;
- GitHub OAuth Device Flow;
- refresh automático de token GitHub quando disponível;
- Microsoft OAuth Authorization Code + PKCE;
- Google OAuth Installed App + PKCE;
- tokens protegidos localmente com Windows DPAPI.

### Nuvem
- OneDrive usando `Files.ReadWrite.AppFolder`;
- Google Drive usando `drive.appdata`;
- Google Drive salva dados na `appDataFolder` oculta;
- OneDrive salva em `Apps/ExtNest`;
- lista de extensões/configurações gerais pode ser restaurada em PC novo;
- configuração das extensões continua em JSON separado por extensão.

### Arquitetura
- extensão dividida em módulos;
- Native Host dividido em módulos;
- `AGENTS.md`;
- `docs/MODULE_MAP.md`;
- documentação OAuth;
- validador do projeto;
- Bridge preparado para IDs Development, Edge Store e Chrome Store.

### Comportamento
- atualização continua manual;
- verificação de nova versão pode ser automática;
- código das extensões continua apenas no GitHub;
- AppData continua sendo a cópia operacional local.
