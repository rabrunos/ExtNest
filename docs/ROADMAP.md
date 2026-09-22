# Roadmap

## v0.1 — protótipo inicial
- Native Messaging em Python;
- GitHub via PAT;
- seleção manual de repositórios;
- clones no AppData;
- detecção de versão;
- Bridge de configurações;
- nuvem via pastas sincronizadas.

## v0.2 — OAuth + nuvem real
- GitHub OAuth Device Flow;
- Microsoft OAuth + PKCE;
- Google OAuth + PKCE;
- OneDrive App Folder;
- Google Drive appDataFolder;
- bootstrap da lista do Vault em PC novo;
- modularização completa;
- mapa de módulos para IA/agentes.

## GitHub

Regra permanente:

- GitHub App com `Contents: Read-only`;
- ExtNest pode clone/fetch/pull;
- ExtNest nunca faz push;
- edição de código acontece no repositório-fonte normal, fora do ExtNest.

## Próximos passos
- helper `.exe` único;
- instalador dedicado do Native Host;
- prompt completo de restore após instalação;
- reparar instalação local;
- diff antes de atualizar;
- migração entre provedores de nuvem;
- espelhamento opcional em dois provedores;
- criptografia opcional de payloads sensíveis;
- testes automatizados de integração OAuth mockados.

## Distribuição
- ExtNest: Microsoft Edge Add-ons + Chrome Web Store.
- Extensões gerenciadas: privadas, GitHub + AppData + Load unpacked.

## Fora de escopo
- push/commit de código pelo ExtNest;
- publicar extensões gerenciadas em lojas;
- CRX privado para extensões gerenciadas;
- atualização silenciosa sem ação do usuário.
