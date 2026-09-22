# OAuth — configuração única do projeto

## GitHub — OAuth App + PKCE

OAuth App atual:

```text
Client ID:
Ov23liTysBeDh3EtPQrb
```

### Configuração no GitHub

Abra:

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
http://127.0.0.1

Allow wildcard matching:
DESATIVADO

Enable Device Flow:
DESATIVADO

Expire user access tokens:
ATIVADO
```

O ExtNest usa Authorization Code + PKCE com callback de loopback em porta aleatória.

Exemplo:

```text
Callback cadastrado:
http://127.0.0.1

Callback durante o login:
http://127.0.0.1:53142
```

### Client Secret para desenvolvimento

Na página do OAuth App:

```text
Client secrets
→ Generate a new client secret
```

Não envie esse valor para o GitHub do ExtNest.

No PC de desenvolvimento, rode:

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\set-dev-github-secret.ps1
```

Cole o Client Secret quando solicitado.

O script cria:

```text
native-host/oauth-private.json
```

Esse arquivo é ignorado pelo Git.

### Teste

1. `git pull`
2. gere e salve o Client Secret local;
3. recarregue a extensão em `edge://extensions`;
4. clique **Conectar com GitHub**;
5. GitHub abre;
6. escolha/autorize a conta;
7. GitHub retorna automaticamente ao loopback local;
8. clique **Carregar repositórios**.

Não deve existir código de Device Flow nem instalação de GitHub App.

---

## Microsoft / OneDrive

Fazer depois do GitHub.

## Google Drive

Fazer depois do GitHub.
