# GitHub Auth — GitHub App

## Modelo adotado

O ExtNest usa um **GitHub App público**.

Existem duas camadas de controle:

1. No GitHub, o usuário instala o GitHub App ExtNest somente nos repositórios que quiser permitir.
2. Dentro do ExtNest, o usuário escolhe quais desses repositórios autorizados realmente entram no Vault.

## Regra de segurança

O GitHub é **somente leitura para o ExtNest**.

O ExtNest pode:
- descobrir repositórios autorizados;
- ler `manifest.json`;
- baixar/clonar código;
- executar fetch/pull;
- verificar versões.

O ExtNest não pode:
- push;
- criar commits remotos;
- alterar arquivos no GitHub;
- criar branches;
- editar configurações do repositório.

Qualquer edição de código deve ser feita fora do ExtNest, usando o repositório-fonte normal da extensão.

## Permissões do GitHub App

Repository permissions:

```text
Contents: Read-only
```

Metadata read é implícito.

Não são necessários:
- Issues;
- Pull requests;
- Actions;
- Administration;
- Members;
- Secrets;
- Workflows;
- Webhooks.

`Contents: read` é suficiente para clone/fetch/pull autenticado. Write só seria necessário para push, que está fora do escopo do ExtNest.

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

Mantenha **Expire user authorization tokens** ativado.

O GitHub App entrega access token e refresh token. Como o token original foi criado por Device Flow, o ExtNest não precisa armazenar client secret.

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

O ExtNest não usa `GET /user/repos` para montar a lista.

## Git

O user access token do GitHub App é usado como credencial HTTP temporária para operações somente leitura.

Permitido:

```text
clone
fetch
pull
```

Não permitido pelo desenho do produto:

```text
push
```

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
    "client_id": "Iv23liGji2rZOiSvippM",
    "app_slug": "PREENCHER"
  }
}
```

Client ID e slug são públicos.

Nunca commitar:
- client secret;
- private key do GitHub App;
- access tokens;
- refresh tokens.

O ExtNest não precisa de private key nem installation access tokens para esse fluxo.
