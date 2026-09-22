# GitHub Auth

## v0.2

O PAT manual foi removido.

ExtNest usa OAuth 2.0 Device Flow:

1. ExtNest solicita `device_code` + `user_code`.
2. Abre `github.com/login/device`.
3. O usuário confirma o código temporário.
4. ExtNest faz polling respeitando o intervalo informado pelo GitHub.
5. Access/refresh tokens são armazenados localmente com DPAPI.
6. O helper renova tokens expirados automaticamente quando um refresh token estiver disponível.

Não há `client_secret` no projeto.

## Permissões

```text
repo
read:user
offline_access
```

A lista de repositórios continua sendo selecionada manualmente pelo usuário dentro do ExtNest.

## Git

O token OAuth é usado temporariamente como header HTTP para `git clone`/`git pull`.

Nunca gravar token na URL do remote.

Documentação:
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
