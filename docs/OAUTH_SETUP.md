# OAuth — configuração única do projeto

Usuários finais do ExtNest não criam tokens nem Client IDs.

Nós registramos uma integração oficial ExtNest em cada provedor uma vez e distribuímos apenas identificadores públicos.

## 1. GitHub — configuração atual

O ExtNest usa um **GitHub App**.

### App criado

Owner:

```text
@rabrunos
```

Client ID:

```text
Iv23liGji2rZOiSvippM
```

O **App ID não é necessário** para o fluxo atual.

Ainda falta preencher o slug em:

```text
native-host/oauth-clients.json
```

### Repository permissions

Configure somente:

```text
Contents: Read-only
```

Todo o restante deve continuar sem acesso, salvo Metadata implícito.

O ExtNest é um gerenciador: ele baixa, lê e atualiza a cópia local. Ele não envia alterações de código ao GitHub.

### User authorization

- Request user authorization (OAuth) during installation: **desativado**
- Enable Device Flow: **ativado**
- Expire user authorization tokens: **ativado**

### Webhook

Desative **Active**.

### Organization permissions

Nenhuma.

### Account permissions

Nenhuma.

### Where can this GitHub App be installed?

Selecione:

```text
Any account
```

### App slug

Na página do App, observe a URL:

```text
https://github.com/apps/<slug>
```

Copie apenas `<slug>` e coloque em:

```json
"app_slug": "<slug>"
```

Não gere nem coloque no ExtNest:
- Client secret;
- private key.

### Teste

1. Atualize o repositório local.
2. Recarregue o ExtNest.
3. Abra a aba GitHub.
4. Clique **Conectar com GitHub**.
5. Autorize o Device Flow.
6. O ExtNest abrirá a instalação do GitHub App se necessário.
7. Escolha **Only select repositories**.
8. Selecione um ou mais repositórios.
9. Volte ao ExtNest.
10. Clique **Carregar repositórios**.

Somente repositórios autorizados ao GitHub App devem aparecer.

---

## 2. Microsoft / OneDrive

Fazer depois que a integração GitHub estiver validada.

---

## 3. Google Drive

Fazer depois que a integração GitHub estiver validada.
