# OAuth — configuração única do projeto

## 1. GitHub

O ExtNest usa um **OAuth App** porque queremos:

```text
Conectar
→ autorizar
→ pronto
```

Sem instalar um GitHub App na conta.

### Criar

GitHub:

```text
Settings
→ Developer settings
→ OAuth Apps
→ New OAuth App
```

Preencha:

```text
Application name:
ExtNest

Homepage URL:
https://github.com/rabrunos/ExtNest

Application description:
Gerenciador privado de extensões que usa o GitHub como fonte de código.

Authorization callback URL:
http://localhost
```

Ative:

```text
Enable Device Flow
Expire user access tokens
```

Depois clique em:

```text
Register application
```

Client ID configurado no projeto:

```text
Ov23liTysBeDh3EtPQrb
```

Não é necessário distribuir `Client secret` no ExtNest.

### Scopes pedidos pelo aplicativo

O ExtNest solicitará:

```text
repo
read:user
offline_access
```

### Atenção

O GitHub não oferece escopo OAuth de código privado somente leitura.

Para ler conteúdo privado, `repo` é necessário e tecnicamente concede read/write.

Mesmo assim, o ExtNest implementa exclusivamente operações de leitura/download e não possui push.

### Teste

1. Coloque o Client ID em `native-host/oauth-clients.json`.
2. Atualize/reinicie o Native Host.
3. Recarregue a extensão.
4. Clique **Conectar com GitHub**.
5. Autorize o código no GitHub.
6. Clique **Carregar repositórios**.
7. Repositórios públicos e privados acessíveis pela conta devem aparecer.
8. Não deve existir nenhuma etapa de instalação de GitHub App.

---

## 2. Microsoft / OneDrive

Fazer depois que a integração GitHub estiver validada.

---

## 3. Google Drive

Fazer depois que a integração GitHub estiver validada.
