# ExtNest Bridge Protocol v1

## Objetivo

Permitir backup/restauração das **configurações que o usuário criou dentro da extensão**.

A extensão gerenciada continua sendo dona dos próprios dados. ExtNest não tenta ler o armazenamento privado de outra extensão diretamente.

## ExtNest IDs

Development:

`econfanmnmmcggpgdflcipmdlmkcbiag`

Os IDs da Edge Add-ons e Chrome Web Store devem ser registrados em `docs/STORE_IDS.md`.

O Bridge deve aceitar a lista completa de IDs autorizados.

## Mensagens ExtNest → extensão

### `extnest.ping`
Resposta: `{"ok":true,"protocol":1,"schema":1}`

### `extnest.config.export`
A extensão retorna `ok`, `protocol`, `schema` e `data`.

### `extnest.config.import`
Recebe um payload exportado anteriormente, migra schema se necessário e grava as configurações.

### `extnest.reload`
Responde `ok` e chama `chrome.runtime.reload()`.

## Mensagem extensão → ExtNest

### `extnest.config.changed`
Dispara backup automático após alteração das configurações declaradas.

## Segurança

No receptor:

```js
if (!VAULT_IDS.includes(sender.id)) return;
```

No `manifest.json` da extensão gerenciada:

```json
{
  "externally_connectable": {
    "ids": ["econfanmnmmcggpgdflcipmdlmkcbiag"]
  }
}
```

## Schema

`schema` é a versão do **formato das configurações**, não da extensão.

Se o formato mudar, incremente o schema e mantenha uma migração em `importTransform`.
