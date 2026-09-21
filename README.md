# ExtNest

ExtNest é um gerenciador privado de extensões Chromium/Edge.

Ele foi pensado para manter extensões pessoais fora das lojas, sem depender de pastas de projeto espalhadas pelo Windows:

- **GitHub privado** = fonte oficial do código das extensões gerenciadas.
- **`%LOCALAPPDATA%\ExtNest\Extensions`** = cópia operacional usada pelo navegador.
- **OneDrive / Google Drive** = configurações do ExtNest e configurações pessoais das extensões.
- **ExtNest em si** pode ser distribuído pela Microsoft Edge Add-ons e Chrome Web Store.
- As **extensões gerenciadas** continuam privadas e são carregadas como `unpacked/development`.

## Estado atual

Este repositório contém o protótipo v0.1:

- Manifest V3;
- painel do ExtNest;
- detecção de extensões `development` via `chrome.management`;
- Native Messaging;
- GitHub privado;
- seleção manual dos repositórios que representam extensões;
- clone/pull para AppData;
- comparação de `manifest.version`;
- atualização manual;
- detecção de OneDrive/Google Drive sincronizados;
- ExtNest Bridge v1 para backup/restauração das configurações internas de extensões;
- documentação para outras IAs criarem extensões compatíveis.

## Estrutura do repositório

```text
ExtNest/
├── extension/                 # extensão que vai para Edge/Chrome Store
│   ├── manifest.json
│   ├── service-worker.js
│   ├── dashboard.html
│   ├── dashboard.css
│   ├── dashboard.js
│   └── icons/
├── native-host/               # helper local via Native Messaging
├── docs/
├── templates/
│   └── managed-extension/     # bridge para futuras extensões
├── tools/
└── README.md
```

## ExtNest na Edge Add-ons / Chrome Web Store

O pacote enviado à loja deve conter **somente o conteúdo de `extension/`**, com `manifest.json` na raiz do ZIP.

Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build-store-package.ps1
```

O pacote será criado em:

```text
dist/ExtNest-store-<versao>.zip
```

### IDs das lojas

O ID local/development deste projeto é:

```text
econfanmnmmcggpgdflcipmdlmkcbiag
```

A Microsoft Edge Add-ons e a Chrome Web Store podem atribuir IDs próprios.

Depois da primeira publicação, registre os IDs definitivos em:

- `docs/STORE_IDS.md`
- `templates/managed-extension/extnest/bridge-config.js`
- `templates/managed-extension/manifest-snippet.json`

O Bridge aceita uma **lista** de IDs autorizados, permitindo que a mesma extensão gerenciada funcione com:

- ExtNest development;
- ExtNest da Edge Add-ons;
- ExtNest da Chrome Web Store.

## Native Host

Mesmo quando o ExtNest é instalado pela Store, operações como:

- Git clone/pull/push;
- leitura/escrita em `%LOCALAPPDATA%`;
- acesso à pasta sincronizada do OneDrive/Google Drive;
- gerenciamento de arquivos;

dependem do **Native Host**.

A Store instala apenas a extensão do navegador; ela não instala automaticamente um executável/helper do Windows.

O protótipo mantém o host em `native-host/`. A evolução prevista é empacotá-lo como um pequeno `.exe`/instalador independente.

## GitHub

Na v0.1, repositórios privados são acessados usando um Personal Access Token protegido localmente pelo Windows DPAPI.

Evolução planejada: GitHub OAuth Device Flow.

## Configurações das extensões

Extensões compatíveis implementam o **ExtNest Bridge**.

O Bridge permite:

- `extnest.ping`
- `extnest.config.export`
- `extnest.config.import`
- `extnest.config.changed`
- `extnest.reload`

Isso permite que as configurações criadas pelo usuário dentro da extensão sejam salvas/restauradas através do ExtNest.

## Documentação obrigatória para novas extensões

Ao pedir para uma IA criar uma extensão compatível, forneça:

```text
docs/AI_EXTENSION_STANDARD.md
```

Também existe um prompt curto em:

```text
templates/managed-extension/EXTENSION_AI_PROMPT.md
```

## Documentação

- `docs/ARCHITECTURE.md`
- `docs/AI_EXTENSION_STANDARD.md`
- `docs/BRIDGE_PROTOCOL.md`
- `docs/CLOUD_LAYOUT.md`
- `docs/GITHUB_AUTH.md`
- `docs/STORE_DISTRIBUTION.md`
- `docs/STORE_IDS.md`
- `docs/ROADMAP.md`

## Repositório oficial

```text
https://github.com/rabrunos/ExtNest
```
