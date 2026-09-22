# Backup na nuvem

## Princípio

```text
GitHub = código-fonte
AppData = cópia local usada pelo navegador
OneDrive/Google Drive = estado e configurações
```

Nenhum código de extensão é duplicado no Drive.

## Estrutura lógica

```text
ExtNest/
├── vault/
│   ├── settings.json
│   └── extensions.json
└── extensions/
    └── <slug>/
        ├── metadata.json
        └── config.json
```

## Google Drive

Provider: `GoogleDriveProvider`

Escopo:

```text
drive.appdata
```

Os arquivos são armazenados na `appDataFolder`, que é:
- oculta no Meu Drive;
- acessível apenas pelo ExtNest;
- destinada a dados/configurações do aplicativo.

Fisicamente, o protótipo pode armazenar os objetos em arquivos planos com nomes determinísticos; a hierarquia acima é a estrutura lógica apresentada pelo ExtNest.

## OneDrive

Provider: `OneDriveProvider`

Escopo:

```text
Files.ReadWrite.AppFolder
```

Usa:

```text
/me/drive/special/approot
```

O OneDrive cria:

```text
Apps/ExtNest/
```

O ExtNest cria dentro dela a estrutura lógica de `vault/` e `extensions/`.

Diferente da `appDataFolder` do Google, o App Folder do OneDrive não é totalmente invisível ao usuário: ele fica em `Apps/ExtNest`. Porém fica isolado da raiz normal e o aplicativo só recebe permissão para esse espaço.

## Bootstrap em novo PC

Quando um provedor vira destino principal:

1. ExtNest procura `vault/extensions.json`.
2. Se o registry local estiver vazio e existir backup remoto, restaura a lista.
3. Restaura configurações gerais portáveis.
4. Mantém caminhos locais e credenciais fora da nuvem.
5. Sincroniza novamente o estado.

## Nunca enviar

- OAuth access token;
- refresh token;
- GitHub credentials;
- cookies;
- sessões;
- chaves privadas;
- paths absolutos específicos daquele PC.
