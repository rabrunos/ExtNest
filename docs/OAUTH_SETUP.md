# OAuth — configuração do GitHub

## OAuth App

```text
Client ID:
Ov23liTysBeDh3EtPQrb
```

ExtNest development ID:

```text
econfanmnmmcggpgdflcipmdlmkcbiag
```

Redirect de desenvolvimento:

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

## Client Secret no desenvolvimento

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\set-dev-github-secret.ps1
```

O script cria:

```text
native-host/oauth-private.json
```

Esse arquivo é local e ignorado pelo Git.

O Client Secret é do aplicativo ExtNest. Ele é configurado uma vez no helper; cada usuário final não fornece um secret próprio.

## Múltiplas contas

O ExtNest pode manter várias contas GitHub conectadas ao mesmo tempo.

Cada autorização salva tokens separados usando o GitHub user ID como `account_id`.

Repositórios privados ficam vinculados à conta que possui acesso.

## Repositórios públicos

Também é possível adicionar diretamente:

```text
owner/repo
```

ou:

```text
https://github.com/owner/repo
```

sem nenhuma conta GitHub conectada.

O repositório precisa:
- ser público;
- possuir `manifest.json` na raiz;
- usar Manifest V3.

Branch é opcional. Quando omitida, o ExtNest usa a branch padrão retornada pelo GitHub.

## Stores

Quando houver IDs oficiais da Edge Add-ons e Chrome Web Store, adicione os respectivos redirects ao mesmo OAuth App:

```text
https://<EDGE_STORE_ID>.chromiumapp.org/github
https://<CHROME_STORE_ID>.chromiumapp.org/github
```

O OAuth App aceita vários Redirect URIs, então o redirect de desenvolvimento pode continuar cadastrado durante os testes.
