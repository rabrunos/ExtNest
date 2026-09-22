# GitHub Auth — chrome.identity + OAuth App + PKCE

## UX

```text
Conectar com GitHub
→ GitHub abre em janela de autenticação
→ usuário autoriza
→ janela fecha automaticamente
→ ExtNest fica conectado
```

O fechamento é feito pelo próprio navegador através de `chrome.identity.launchWebAuthFlow`.

Quando o provedor redireciona para:

```text
https://<extension-id>.chromiumapp.org/github
```

o navegador encerra a janela do fluxo e entrega a URL final de volta à extensão.

## Responsabilidades

### Extensão

- gera a redirect URL com `chrome.identity.getRedirectURL("github")`;
- pede ao Native Host a authorization URL;
- executa `chrome.identity.launchWebAuthFlow`;
- envia a URL final ao Native Host.

### Native Host

- gera `state`;
- gera PKCE `code_verifier/code_challenge`;
- guarda a sessão OAuth por no máximo 5 minutos;
- valida redirect, state e issuer;
- troca authorization code por tokens;
- valida o usuário em `GET /user`;
- salva os tokens com DPAPI.

A conta só é considerada conectada depois de todo esse processo concluir.

## Client Secret

GitHub OAuth Apps exigem Client Secret na troca do code por token.

Como o ExtNest é um cliente público/nativo, o GitHub reconhece que esse segredo não pode ser mantido realmente secreto no dispositivo. PKCE deve ser usado para proteger o authorization code.

## Repositórios privados

Scopes:

```text
repo
read:user
offline_access
```

O GitHub não fornece um scope OAuth de conteúdo privado read-only. O token é mais amplo que a funcionalidade usada.

O ExtNest restringe seu comportamento:
- listar/GET;
- clone/fetch/pull;
- sem push;
- push URL bloqueado.

## Tokens

Tokens ficam no computador do usuário, protegidos via Windows DPAPI, e não são enviados para infraestrutura do ExtNest.
