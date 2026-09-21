# Criar uma nova extensão para o ExtNest

1. Crie um repositório GitHub, público ou privado.
2. Faça a raiz do repo ser uma extensão Manifest V3 carregável.
3. Gere uma `manifest.key` fixa com `tools/generate-extension-key.ps1`.
4. Copie `templates/managed-extension/extnest/` para o projeto.
5. Ajuste `backupKeys` para conter apenas preferências reais do usuário.
6. Adicione o ID do ExtNest em `externally_connectable`.
7. Incremente `manifest.version` sempre que publicar uma nova versão no GitHub.
8. No ExtNest, conecte o GitHub, selecione o repositório e clique Instalar.
9. Na primeira vez naquele navegador, use Load unpacked apontando para a pasta que o ExtNest mostrar.

Para gerar a extensão com IA, envie também `AI_EXTENSION_STANDARD.md` ou o prompt em `templates/managed-extension/EXTENSION_AI_PROMPT.md`.
