# GitHub Auth

## v0.1
Token pessoal inserido manualmente e protegido por Windows DPAPI.

## Produção
Migrar para GitHub OAuth/GitHub App com Device Flow:
1. ExtNest solicita device code.
2. Abre a autorização GitHub.
3. Usuário confirma.
4. ExtNest recebe token.
5. Helper persiste credencial protegida.

Preferir permissões mínimas e repositórios selecionados.

Clones/pulls/pushes nunca devem embutir token na URL do remote.
