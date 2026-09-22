# OAuth — configuração única do projeto

Depois que estes três aplicativos OAuth forem registrados, usuários do ExtNest apenas clicam em **Conectar** e autorizam no navegador. Eles não criam nem digitam tokens.

Os Client IDs são identificadores públicos; podem ficar no repositório.

Preencha:

```text
native-host/oauth-clients.json
```

## 1. GitHub

Crie um **OAuth App** em GitHub → Settings → Developer settings → OAuth Apps.

Configuração sugerida:

```text
Application name: ExtNest
Homepage URL: https://github.com/rabrunos/ExtNest
Authorization callback URL: http://localhost
```

Depois:

1. habilite **Device Flow**;
2. copie somente o **Client ID**;
3. coloque em `github.client_id`;
4. não coloque `client_secret` no projeto.

Escopos solicitados pelo protótipo:

```text
repo
read:user
offline_access
```

`repo` é necessário para os repositórios privados que o usuário escolher.

Documentação oficial:
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps

## 2. Microsoft / OneDrive

Crie um App Registration no Microsoft Entra.

Para permitir OneDrive pessoal e corporativo, selecione um tipo de conta compatível com:
- contas em diretórios organizacionais;
- contas pessoais Microsoft.

Em **Authentication**:
1. adicione a plataforma **Mobile and desktop applications**;
2. configure `http://localhost`;
3. habilite fluxos de cliente público quando aplicável.

Permissões delegadas Microsoft Graph:

```text
User.Read
Files.ReadWrite.AppFolder
```

O fluxo também solicita:

```text
openid
profile
offline_access
```

Copie o **Application (client) ID** para `microsoft.client_id`.

Não use client secret: o helper é um cliente público e usa Authorization Code + PKCE.

O OneDrive cria o espaço do aplicativo em:

```text
Apps/ExtNest
```

O escopo `Files.ReadWrite.AppFolder` limita o acesso do ExtNest a esse espaço.

Documentação oficial:
https://learn.microsoft.com/en-us/entra/identity-platform/scenario-desktop-app-configuration
https://learn.microsoft.com/en-us/graph/onedrive-sharepoint-appfolder

## 3. Google / Google Drive

No Google Cloud:

1. crie/selecione um projeto;
2. habilite **Google Drive API**;
3. configure a tela de consentimento OAuth;
4. crie um OAuth Client do tipo **Desktop app**;
5. copie o Client ID para `google.client_id`.

O ExtNest usa navegador do sistema + PKCE + callback de loopback `127.0.0.1`.

Não usamos OOB/manual copy-paste.

Escopo de backup:

```text
https://www.googleapis.com/auth/drive.appdata
```

Além de:

```text
openid
email
profile
```

`drive.appdata` dá acesso somente à pasta especial oculta `appDataFolder`. Ela não aparece no Meu Drive e outros apps do Drive não conseguem acessá-la.

Documentação oficial:
https://developers.google.com/identity/protocols/oauth2/native-app
https://developers.google.com/workspace/drive/api/guides/appdata

## Resultado para o usuário

### GitHub

```text
Conectar com GitHub
→ página oficial
→ inserir o código temporário
→ autorizar
→ pronto
```

### OneDrive

```text
Conectar OneDrive
→ página oficial Microsoft
→ escolher conta
→ autorizar
→ retorno automático
```

### Google Drive

```text
Conectar Google Drive
→ página oficial Google
→ escolher conta
→ autorizar
→ retorno automático
```

Tokens de acesso e refresh tokens são protegidos localmente pelo Windows DPAPI.
