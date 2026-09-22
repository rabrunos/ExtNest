# GitHub Auth — OAuth App

## Objetivo

O ExtNest deve ter o fluxo mais simples possível:

```text
Conectar com GitHub
→ autorizar a conta
→ pronto
```

Não existe instalação de GitHub App e não existe seleção de repositórios no GitHub.

## Por que OAuth App

Um OAuth App pode acessar os repositórios que o próprio usuário autenticado já consegue acessar.

Isso combina com o ExtNest porque:
- o processamento acontece no computador do usuário;
- o GitHub serve apenas como fonte do código;
- o ExtNest não precisa agir independentemente do usuário;
- o usuário escolhe dentro do ExtNest quais repositórios quer gerenciar.

## Limitação importante do GitHub

Para ler código de **repositórios privados**, um OAuth App precisa solicitar:

```text
repo
```

O GitHub atualmente não oferece um escopo OAuth que limite código privado a read-only.

O escopo `repo` tecnicamente permite operações de escrita também.

Portanto, o read-only do ExtNest é garantido pelo **desenho do aplicativo**, não pelo escopo OAuth.

## Regra de implementação

O ExtNest pode:
- `GET` em APIs GitHub;
- listar repositórios;
- ler arquivos;
- clone;
- fetch;
- pull;
- verificar versões;
- baixar código.

O ExtNest não implementa:
- push;
- criação de commits no GitHub;
- edição de arquivos remotos;
- branches remotos;
- merges;
- administração de repositório.

O clone operacional do ExtNest também recebe um `pushurl` inválido como proteção adicional contra push acidental.

## Scopes

```text
repo
read:user
offline_access
```

- `repo`: necessário para conteúdo de repositórios privados.
- `read:user`: perfil básico.
- `offline_access`: access token expirável + refresh token.

## Device Flow

ExtNest usa OAuth Device Flow.

1. O helper solicita `device_code`.
2. Abre `https://github.com/login/device`.
3. Usuário autoriza.
4. ExtNest recebe token.
5. Tokens ficam somente no computador do usuário e são protegidos por Windows DPAPI.
6. Refresh ocorre automaticamente quando necessário.

## Segurança do token

No desenho atual o ExtNest não possui servidor para receber tokens e não transmite tokens para infraestrutura própria.

O token é enviado somente ao GitHub para autenticação.

Tecnicamente, qualquer software que tenha acesso a um token poderia ser programado para transmiti-lo. Por isso:
- o projeto deve permanecer auditável;
- tokens nunca entram no Git;
- tokens ficam protegidos por DPAPI;
- não existe telemetria contendo credenciais.

## Configuração pública

`native-host/oauth-clients.json`:

```json
{
  "github": {
    "type": "oauth_app",
    "client_id": "CLIENT_ID_PUBLICO",
    "scopes": ["repo", "read:user", "offline_access"]
  }
}
```

Nenhum client secret é distribuído com o ExtNest.
