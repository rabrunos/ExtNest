# OAuth — configuração única do projeto

Usuários finais do ExtNest não criam tokens nem Client IDs.

Nós registramos uma integração oficial ExtNest em cada provedor uma vez e distribuímos apenas identificadores públicos.

## 1. GitHub — fazer primeiro

Crie um **GitHub App**, não um OAuth App.

Caminho:

```text
GitHub
→ Settings
→ Developer settings
→ GitHub Apps
→ New GitHub App
```

### Campos principais

Use:

```text
GitHub App name:
ExtNest
```

Se o nome estiver indisponível, use algo como:

```text
ExtNest by rabrunos
```

Homepage URL:

```text
https://github.com/rabrunos/ExtNest
```

Callback URL:

Pode ficar vazio para o fluxo Device Flow. O ExtNest não usa Web Application Flow no GitHub.

### User authorization

- Request user authorization (OAuth) during installation: **desativado**
- Enable Device Flow: **ativado**
- User-to-server token expiration: **ativado**

### Webhook

Desative **Active**.

O ExtNest não precisa de webhook.

### Repository permissions

Configure somente:

```text
Contents: Read and write
```

Não habilite permissões adicionais sem necessidade.

### Organization permissions

Nenhuma.

### Account permissions

Nenhuma.

### Where can this GitHub App be installed?

Selecione:

```text
Any account
```

Isso torna o GitHub App instalável por qualquer usuário do ExtNest. Não significa publicar no GitHub Marketplace.

### Após criar

Na página do GitHub App copie:

1. **Client ID** — é diferente do App ID.
2. O **slug** do aplicativo, visível na URL:
   `https://github.com/apps/<slug>`

Preencha:

```text
native-host/oauth-clients.json
```

Exemplo:

```json
{
  "github": {
    "type": "github_app",
    "client_id": "Iv1.xxxxxxxxxxxxxxxx",
    "app_slug": "extnest"
  }
}
```

Não gere nem coloque no ExtNest:
- Client secret;
- private key.

O ExtNest é um native/public client e usa Device Flow.

### Teste

1. Recarregue o ExtNest.
2. Abra GitHub.
3. Clique **Conectar com GitHub**.
4. Autorize o código.
5. O ExtNest abrirá a instalação do GitHub App caso ainda não exista.
6. Selecione **Only select repositories**.
7. Marque um ou mais repositórios.
8. Volte ao ExtNest.
9. Clique **Carregar repositórios**.

Somente repositórios autorizados ao GitHub App devem aparecer.

---

## 2. Microsoft / OneDrive

Fazer depois que a integração GitHub estiver validada.

Os placeholders continuam em `native-host/oauth-clients.json`.

---

## 3. Google Drive

Fazer depois que a integração GitHub estiver validada.

Os placeholders continuam em `native-host/oauth-clients.json`.
