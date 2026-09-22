# GitHub Auth — GitHub App

## Modelo adotado

O ExtNest usa um **GitHub App público**, não um OAuth App genérico.

Isso permite duas camadas de controle:

1. No GitHub, o usuário instala o GitHub App ExtNest somente nos repositórios que quiser permitir.
2. Dentro do ExtNest, o usuário escolhe quais desses repositórios autorizados realmente entram no Vault.

O token não recebe o escopo amplo `repo`.

## Permissões do GitHub App

Repository permissions:

```text
Contents: Read and write
```

Metadata read é implícito.

Não são necessários:
- Issues;
- Pull requests;
- Actions;
- Administration;
- Members;
- Secrets.

`Contents: write` é escolhido porque o roadmap inclui salvar alterações/push pelo ExtNest. Para clone/pull apenas, read seria suficiente.

## Onde o App pode ser instalado

Configure:

```text
Any account
```

Assim qualquer usuário do ExtNest pode instalar o GitHub App na própria conta ou organização, sujeito às políticas daquela organização.

## Device Flow

O helper usa GitHub App User Access Token via OAuth Device Flow.

Fluxo:

1. ExtNest solicita `device_code` usando o Client ID do GitHub App.
2. Abre `https://github.com/login/device`.
3. Usuário confirma o código.
4. ExtNest recebe um user access token.
5. O token é limitado pela interseção:
   - permissões do GitHub App;
   - repositórios selecionados na instalação;
   - permissões do próprio usuário.
6. Access/refresh tokens ficam protegidos localmente pelo Windows DPAPI.

Não há `client_secret` no ExtNest.

## Token expiration

Mantenha **User-to-server token expiration** ativado.

O GitHub App entrega access token curto e refresh token. Como o token original foi criado por Device Flow, o refresh não exige client secret.

## Instalação nos repositórios

ExtNest abre:

```text
https://github.com/apps/<APP_SLUG>/installations/new
```

O usuário deve preferir:

```text
Only select repositories
```

Depois, a API usada para descobrir repositórios é:

```text
GET /user/installations
GET /user/installations/{installation_id}/repositories
```

O ExtNest não usa mais `GET /user/repos` para montar a lista.

## Git

O user access token do GitHub App é usado como credencial HTTP temporária para clone/pull/push.

O remote continua limpo:

```text
https://github.com/owner/repo.git
```

Nunca gravar token na URL do remote.

## Configuração pública no projeto

`native-host/oauth-clients.json`:

```json
{
  "github": {
    "type": "github_app",
    "client_id": "Iv1....",
    "app_slug": "extnest"
  }
}
```

Client ID e slug são públicos.

Nunca commitar:
- client secret;
- private key do GitHub App;
- access tokens;
- refresh tokens.

O ExtNest, como native/public client, não precisa de private key nem installation access tokens.
