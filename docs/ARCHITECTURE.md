# Arquitetura do ExtNest

> O ExtNest pode ser instalado pela Edge Add-ons/Chrome Web Store. As extensões que ele gerencia permanecem privadas e unpacked.

## Componentes

### ExtNest Extension
Interface dentro do Edge.

Responsabilidades:
- UI;
- `chrome.management` para enxergar extensões instaladas;
- comunicação entre extensões;
- notificações;
- comandos para o Native Host.

### ExtNest Native Host
Programa local registrado como `com.extnest.host`.

Responsabilidades:
- `%LOCALAPPDATA%`;
- Git;
- GitHub API;
- credenciais locais;
- leitura/escrita da pasta sincronizada de nuvem;
- registry das extensões.

### GitHub
Fonte de verdade do código.

> Se a pasta local for apagada, deve ser possível reconstruí-la a partir do GitHub.

### Cloud Provider
Fonte de verdade das configurações pessoais/restauração. Não armazena código.

## Instalação de uma extensão

1. Usuário seleciona explicitamente um repositório GitHub.
2. ExtNest valida `manifest.json`.
3. Helper clona para `%LOCALAPPDATA%\\ExtNest\\Extensions\\<slug>`.
4. ExtNest mostra o caminho.
5. Usuário executa `Load unpacked` uma vez no Edge.
6. `chrome.management` detecta a extensão.
7. Com `manifest.key`, o ID é previsível e estável.
8. Se houver backup de configurações, ExtNest pode oferecer restauração.

## Atualização

1. ExtNest lê `manifest.version` remoto.
2. Compara com a versão instalada.
3. Apenas notifica.
4. Usuário clica Atualizar.
5. Backup de cfg, se bridge compatível.
6. Helper executa `git pull --ff-only`.
7. Bridge executa `chrome.runtime.reload()`.

Nunca sobrescrever working tree suja automaticamente.

## Segurança

- GitHub token: DPAPI local.
- Nuvem: sem tokens nos JSONs.
- Bridge: extensão gerenciada aceita somente o ID fixo do ExtNest.
- Backup: allow-list de chaves.
- Segredos, sessões, cookies e API keys ficam fora por padrão.
