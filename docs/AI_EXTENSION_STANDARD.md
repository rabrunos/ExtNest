# PADRÃO OBRIGATÓRIO — Extensões compatíveis com ExtNest

> Entregue este arquivo a outra IA antes de ela criar ou modificar uma extensão destinada ao ExtNest.

## 1. Requisitos gerais

A extensão deve:
- ser Manifest V3;
- ficar pronta para clone do GitHub;
- ter ID estável entre computadores;
- exportar/importar as configurações criadas pelo usuário;
- avisar o ExtNest quando essas configurações mudarem;
- nunca colocar segredos no backup.

## 2. Estrutura recomendada

```text
repo/
├── manifest.json
├── service-worker.js
├── ...
└── extnest/
    ├── bridge-config.js
    └── bridge.js
```

A raiz do repo deve ser carregável via **Load unpacked**. Se existir build obrigatório, documente claramente.

## 3. Manifest V3

Obrigatório:

```json
{"manifest_version":3}
```

## 4. ID estável

Toda extensão gerenciada deve possuir uma `key` pública fixa no `manifest.json`.

Use `tools/generate-extension-key.ps1` do ExtNest.

A chave pública pode ser commitada no GitHub.

## 5. Permitir somente o ExtNest

ExtNest ID:

`econfanmnmmcggpgdflcipmdlmkcbiag`

Adicionar:

```json
{
  "externally_connectable": {
    "ids": ["econfanmnmmcggpgdflcipmdlmkcbiag"]
  }
}
```

## 6. Bridge

Se o service worker é clássico:

```js
importScripts("extnest/bridge-config.js", "extnest/bridge.js");
```

Se já existe service worker, **não crie outro**. Integre o bridge ao existente.

## 7. Chaves de configuração

Defina explicitamente uma allow-list:

```js
backupKeys: ["theme", "layout", "preferences"]
```

### Deve entrar
- tema;
- preferências;
- filtros;
- regras;
- layout;
- opções definidas pelo usuário.

### Não deve entrar por padrão
- tokens;
- senhas;
- cookies;
- sessões;
- API keys;
- OAuth tokens;
- caches;
- logs;
- blobs grandes.

Nunca usar `chrome.storage.local.get(null)` como padrão automático.

## 8. Schema das configurações

Declare `schema: 1` e incremente quando o formato mudar. Implemente migração no `importTransform`.

## 9. Mudanças de configuração

O bridge observa apenas `backupKeys`, aplica debounce e envia `extnest.config.changed`.

## 10. Restore

`extnest.config.import` deve:
1. validar payload;
2. migrar schema;
3. gravar configurações;
4. evitar loop de backup durante importação.

## 11. Versões

`manifest.version` é usado para comparar instalação local com GitHub. Use `MAJOR.MINOR.PATCH` e incremente quando houver nova versão.

## 12. Git

ExtNest nunca deve sobrescrever uma working tree com alterações locais. O repo deve continuar Git válido.

## 13. `.extnest.json` opcional

```json
{
  "schema": 1,
  "displayName": "Minha Extensão",
  "entry": ".",
  "configBridge": true
}
```

## 14. Checklist para IA

- [ ] Manifest V3.
- [ ] `manifest.version` válido.
- [ ] `manifest.key` fixa.
- [ ] `externally_connectable` contém o ExtNest.
- [ ] bridge integrado ao worker existente.
- [ ] allow-list definida.
- [ ] nenhum segredo na allow-list.
- [ ] export funciona.
- [ ] import funciona.
- [ ] `extnest.ping` funciona.
- [ ] `extnest.reload` funciona.
- [ ] schema declarado.
- [ ] raiz do repo carregável via Load unpacked ou build documentado.

## 15. Modelos

Copie:
- `templates/managed-extension/extnest/bridge-config.js`
- `templates/managed-extension/extnest/bridge.js`

## Regra máxima

> Uma reinstalação em outro PC deve precisar apenas do GitHub para recuperar o código e do provedor de nuvem para recuperar as configurações pessoais.
