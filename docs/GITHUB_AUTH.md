# GitHub Auth — múltiplas contas, OAuth App + PKCE

## UX

O ExtNest suporta várias contas GitHub simultaneamente.

```text
Adicionar conta
→ GitHub abre na janela OAuth do navegador
→ usuário autoriza
→ janela fecha automaticamente
→ conta entra na lista do ExtNest
```

Cada conta recebe um `account_id` baseado no ID numérico retornado pelo GitHub.

Tokens de contas diferentes nunca compartilham o mesmo arquivo. Cada conjunto de tokens é salvo separadamente via Windows DPAPI.

## Repositórios privados

Cada extensão privada guarda:

```json
{
  "repo": "owner/private-extension",
  "private": true,
  "account_id": "<github-user-id>"
}
```

Clone, pull, leitura de manifest e verificação de versão usam somente o token da conta associada àquele repositório.

Se a conta for desconectada:
- a extensão continua registrada;
- os arquivos locais continuam no computador;
- operações que exigem o repositório privado ficam indisponíveis;
- ao reconectar a mesma conta, o mesmo `account_id` volta a funcionar.

## Repositórios públicos sem conta

Repositórios públicos não armazenam `account_id`.

```json
{
  "repo": "thirdparty/public-extension",
  "private": false,
  "account_id": null
}
```

O ExtNest pode:
- consultar metadados públicos sem token;
- ler o `manifest.json` pela API pública;
- clonar por HTTPS sem credenciais;
- atualizar com `git pull` sem credenciais.

Isso permite instalar extensões públicas de terceiros sem conectar conta GitHub.

## Registro

Novos slugs usam:

```text
owner--repo
```

para evitar colisões entre, por exemplo:

```text
alice/my-extension
bob/my-extension
```

Registros antigos preservam o slug existente para não quebrar o caminho local já instalado.

## OAuth

A extensão usa:
- `chrome.identity.getRedirectURL("github")`;
- `chrome.identity.launchWebAuthFlow`;
- Authorization Code;
- PKCE S256;
- `state` aleatório;
- validação de redirect;
- validação do issuer quando presente.

A conta só é adicionada depois que o Native Host troca o code por token e confirma a identidade em `GET /user`.

## Permissões

Scopes atuais:

```text
repo
read:user
offline_access
```

O GitHub OAuth App não oferece um escopo equivalente a conteúdo privado somente leitura. Por isso o token é mais amplo que o comportamento do ExtNest.

O ExtNest restringe sua própria camada GitHub a leitura/download:
- listar/GET;
- clone/fetch/pull;
- sem push;
- push URL do clone operacional bloqueado.

## Client Secret

O Client Secret pertence ao OAuth App ExtNest, não a uma conta do usuário.

No desenvolvimento ele fica somente em:

```text
native-host/oauth-private.json
```

e esse arquivo está no `.gitignore`.

Na distribuição final ele faz parte da configuração do Native Host, então o usuário final não precisa fornecer Client ID ou Client Secret.
