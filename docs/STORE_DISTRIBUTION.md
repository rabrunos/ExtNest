# Distribuição do ExtNest

## ExtNest

O ExtNest propriamente dito será distribuído pelas lojas:

- Microsoft Edge Add-ons
- Chrome Web Store

Isso evita ter que manter a pasta da própria extensão manualmente.

## Extensões gerenciadas

As extensões que o ExtNest administra continuam privadas:

```text
GitHub privado
      ↓
ExtNest Native Host
      ↓
%LOCALAPPDATA%\ExtNest\Extensions\<slug>
      ↓
Load unpacked
```

Elas não precisam ser publicadas em nenhuma loja.

## Native Host

A extensão instalada pela loja não substitui o Native Host.

Browsers não permitem que uma extensão instalada pela Store instale silenciosamente um programa nativo.

Portanto, para usar Git/AppData/arquivos locais, o Native Host precisa ser instalado/registrado separadamente.

A versão final deverá usar um helper `.exe` com instalador próprio.

## IDs

ID development atual:

`econfanmnmmcggpgdflcipmdlmkcbiag`

Após publicar nas lojas, preencher `docs/STORE_IDS.md`.

Depois atualizar a lista de IDs autorizados do Bridge.
