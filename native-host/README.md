# ExtNest Native Host

O Native Host executa operações que uma extensão de navegador não pode fazer diretamente:

- Git;
- `%LOCALAPPDATA%`;
- OAuth desktop/loopback;
- OneDrive/Google Drive;
- leitura e escrita de arquivos locais.

## Estrutura

```text
native-host/
├── extnest_host.py
├── launcher.cmd
├── oauth-clients.json
├── extnest/
│   ├── oauth/
│   ├── cloud/
│   ├── repos.py
│   ├── registry.py
│   ├── config_backup.py
│   └── protocol.py
└── setup/
    └── register-dev-host.ps1
```

## Desenvolvimento

```powershell
powershell -ExecutionPolicy Bypass -File .\native-host\setup\register-dev-host.ps1
```

Esse script é exclusivo do modo de desenvolvimento: ele aponta o registro do
Windows diretamente para o `launcher.cmd` desta cópia do repositório. Ele não
entra no pacote enviado às Stores.

Execute esse comando novamente sempre que trocar entre versões ou cópias do
ExtNest. O registro do Windows guarda um caminho absoluto; uma instalação v0.1
em `%LOCALAPPDATA%\ExtNest\Self` continuará sendo usada até o host ser
registrado outra vez.

O `launcher.cmd` é somente um launcher temporário do protótipo.

A versão de produção deve empacotar o host como `.exe`, eliminando dependência de Python e do launcher.

O instalador de produção deverá registrar esse `.exe` em um caminho local
estável, independente da pasta controlada pelo Edge/Chrome. A comunicação com a
extensão ocorre pelo ID presente em `allowed_origins`, não pelo caminho em que o
navegador instalou a extensão.

## Store

O Native Host **não** faz parte do ZIP enviado à Microsoft Edge Add-ons/Chrome Web Store.

Quando os IDs oficiais das Stores existirem, atualize `allowed_origins` do Native Messaging Host.
