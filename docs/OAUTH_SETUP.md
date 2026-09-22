# OAuth — configuração única do projeto

## GitHub — OAuth App + PKCE + chrome.identity

OAuth App:

```text
Client ID:
Ov23liTysBeDh3EtPQrb
```

### Desenvolvimento atual

ExtNest development ID:

```text
econfanmnmmcggpgdflcipmdlmkcbiag
```

O redirect usado por `chrome.identity.launchWebAuthFlow` é:

```text
https://econfanmnmmcggpgdflcipmdlmkcbiag.chromiumapp.org/github
```

No GitHub:

```text
Settings
→ Developer settings
→ OAuth Apps
→ ExtNest
```

Configure:

```text
Homepage URL:
https://github.com/rabrunos/ExtNest

Redirect URI:
https://econfanmnmmcggpgdflcipmdlmkcbiag.chromiumapp.org/github

Allow wildcard matching:
DESATIVADO

Enable Device Flow:
DESATIVADO

Expire user access tokens:
ATIVADO
```

### Quando publicar nas Stores

Edge Add-ons e Chrome Web Store podem gerar IDs diferentes.

O OAuth App aceita vários Redirect URIs. Adicione também:

```text
https://<EDGE_STORE_ID>.chromiumapp.org/github
https://<CHROME_STORE_ID>.chromiumapp.org/github
```

sem remover o redirect de desenvolvimento enquanto ele ainda for usado.

### Client Secret

O GitHub exige Client Secret na troca de Authorization Code por token para OAuth Apps, mesmo com PKCE.

Para desenvolvimento:

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\set-dev-github-secret.ps1
```

O arquivo local `native-host/oauth-private.json` fica fora do Git.

### Fluxo

```text
Conectar com GitHub
→ chrome.identity.launchWebAuthFlow
→ GitHub
→ Autorizar
→ *.chromiumapp.org/github
→ navegador fecha a janela OAuth automaticamente
→ Native Host troca o code por token
→ ExtNest confirma /user
→ conectado
```

Não existe página `127.0.0.1` no fluxo GitHub e não existe código Device Flow.
