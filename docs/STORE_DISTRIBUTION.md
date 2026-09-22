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

### Canais separados

Em desenvolvimento, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\register-dev-host.ps1
```

Esse registro aponta para o `launcher.cmd` do checkout atual e autoriza apenas
o ID de desenvolvimento. O manifesto gerado fica ignorado pelo Git e não deve
entrar no ZIP da Store.

Em produção, o instalador do Native Host deverá:

1. instalar o helper em um caminho por usuário estável, por exemplo
   `%LOCALAPPDATA%\Programs\ExtNest\NativeHost`;
2. criar um manifesto Native Messaging com o caminho absoluto do executável;
3. registrar o manifesto para Edge e Chrome;
4. incluir em `allowed_origins` os IDs oficiais das duas Stores;
5. atualizar o helper sem depender ou alterar a pasta interna da extensão.

Edge e Chrome podem mover ou substituir a pasta da extensão durante uma
atualização. Isso não afeta o Native Host: o vínculo é feito pelo nome
`com.extnest.host` e pelo ID da extensão, nunca pelo caminho da Store.

## IDs

ID development atual:

`econfanmnmmcggpgdflcipmdlmkcbiag`

Após publicar nas lojas, preencher `docs/STORE_IDS.md`.

Depois atualizar a lista de IDs autorizados do Bridge.
