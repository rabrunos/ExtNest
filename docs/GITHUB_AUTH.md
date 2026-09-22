# GitHub Auth — OAuth App + PKCE

## Experiência

O login do ExtNest é:

```text
Conectar com GitHub
→ navegador oficial do GitHub
→ escolher/autorizar conta
→ retorno automático para 127.0.0.1
→ conectado
```

Não existe:
- código de Device Flow;
- instalação de GitHub App;
- token manual.

## Authorization Code + PKCE

O ExtNest gera:
- `state` aleatório;
- `code_verifier`;
- `code_challenge` SHA-256 (`S256`);
- servidor loopback temporário em `127.0.0.1:<porta aleatória>`.

O callback cadastrado no GitHub deve ser:

```text
http://127.0.0.1
```

## Client Secret

Para OAuth Apps, o GitHub exige `client_secret` na troca do authorization code por token.

Por isso:
- o secret nunca é commitado;
- desenvolvimento usa `native-host/oauth-private.json`;
- esse arquivo está no `.gitignore`;
- alternativamente pode ser usado `EXTNEST_GITHUB_CLIENT_SECRET`.

Em produção sem backend, esse valor precisará estar no Native Host final e, por ser um cliente instalado no PC, deve ser considerado recuperável. O PKCE protege o authorization code contra interceptação, mas não torna um segredo embutido realmente confidencial.

## Acesso aos repositórios

Scopes:

```text
repo
read:user
offline_access
```

O GitHub não fornece um scope OAuth de conteúdo privado read-only.

O ExtNest reforça read-only no próprio desenho:
- apenas GET nas APIs;
- clone/fetch/pull;
- sem push;
- push URL do clone operacional é deliberadamente inválida.

## Tokens

Access token e refresh token:
- ficam somente no computador;
- são protegidos com Windows DPAPI;
- não são enviados para infraestrutura do ExtNest.
