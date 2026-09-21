# Estrutura de nuvem

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

## vault/settings.json
Preferências do ExtNest que fazem sentido em outro PC.

Não incluir paths absolutos, tokens, credenciais ou caches.

## vault/extensions.json
Lista de repositórios que o usuário selecionou manualmente.

## extensions/<slug>/config.json
Último backup das configurações do usuário naquela extensão.

Não há versionamento próprio do ExtNest. Se o provedor tiver histórico, isso é responsabilidade do OneDrive/Google Drive.

> Código = GitHub. Estado/configuração = nuvem. Cache/instalação = AppData.
