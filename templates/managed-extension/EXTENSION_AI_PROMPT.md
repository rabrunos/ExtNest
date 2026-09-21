# Prompt para IA — extensão compatível com ExtNest

Crie/modifique esta extensão para ser compatível com o ExtNest.

Siga integralmente `docs/AI_EXTENSION_STANDARD.md` do projeto ExtNest.

Requisitos essenciais:
- Manifest V3.
- ID fixo por `manifest.key`.
- ExtNest ID permitido: `econfanmnmmcggpgdflcipmdlmkcbiag`.
- Integrar o Bridge no service worker existente.
- Declarar explicitamente as chaves que representam configurações do usuário.
- Nunca incluir tokens, cookies, senhas, sessões, API keys ou caches no backup.
- Implementar export/import/reload/ping conforme Bridge Protocol v1.
- Manter `manifest.version` atualizado.
- A raiz clonada do GitHub deve ficar pronta para Load unpacked ou documentar o build.
