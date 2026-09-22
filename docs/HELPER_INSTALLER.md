# ExtNest Helper — instalação para usuário final

## Objetivo

O usuário final não configura Native Messaging manualmente.

Fluxo:

```text
Edge Add-ons
→ instalar ExtNest
→ abrir ExtNest
→ Finalizar instalação
→ baixar ExtNestHelperSetup.exe
→ Abrir instalador
→ instalação por usuário, sem admin
→ ExtNest detecta Helper online
→ conectar contas
```

## O instalador faz automaticamente

Instala em:

```text
%LOCALAPPDATA%\ExtNest\NativeHost
```

Inclui:
- `ExtNestHost.exe` compilado com PyInstaller;
- Git portátil próprio;
- `oauth-clients.json`;
- configuração interna OAuth do build;
- manifest Native Messaging.

Registra por usuário:

```text
HKCU\Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host
HKCU\Software\Google\Chrome\NativeMessagingHosts\com.extnest.host
```

Não exige administrador.

## IDs de extensão permitidos

O build sempre inclui o ID de desenvolvimento.

Quando os IDs oficiais existirem, configure no repositório GitHub:

```text
Repository variables:
EXTNEST_EDGE_STORE_ID
EXTNEST_CHROME_STORE_ID
```

O workflow adiciona esses IDs a `allowed_origins` do Native Host.

## Client Secret

Configure uma única vez no repositório:

```text
Repository secret:
EXTNEST_GITHUB_CLIENT_SECRET
```

Esse segredo pertence ao OAuth App ExtNest, não aos usuários.

Ele entra no pacote do Helper durante o build e nunca é gravado no código-fonte ou nos logs.

Como o ExtNest é um cliente público instalado no computador, esse valor deve ser considerado recuperável do binário. A proteção do authorization code depende de PKCE + state.

## Build

Workflow:

```text
.github/workflows/build-helper.yml
```

Execução manual produz um artifact.

Criar uma tag `vX.Y.Z` também cria/atualiza uma GitHub Release e envia:

```text
ExtNestHelperSetup.exe
```

A extensão baixa sempre:

```text
https://github.com/rabrunos/ExtNest/releases/latest/download/ExtNestHelperSetup.exe
```

O repositório ExtNest é público, portanto o instalador pode ser baixado sem login no GitHub.

## Desenvolvimento

Para desenvolvimento local continuam existindo scripts em:

```text
native-host/setup/
```

Eles não fazem parte da experiência do usuário final.
