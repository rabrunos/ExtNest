# Conectar este projeto ao GitHub

Repositório:

```text
https://github.com/rabrunos/ExtNest
```

## Fluxo recomendado

Crie uma pasta vazia, abra-a no VS Code e execute:

```powershell
git clone https://github.com/rabrunos/ExtNest.git .
```

Depois copie/extrai os arquivos deste pacote para essa pasta.

Então:

```powershell
git add .
git commit -m "Initial ExtNest prototype"
git push
```

## Se os arquivos já estiverem numa pasta que NÃO é um clone

```powershell
git init
git branch -M main
git remote add origin https://github.com/rabrunos/ExtNest.git
git add .
git commit -m "Initial ExtNest prototype"
git push -u origin main
```

Se o repositório remoto já tiver README/licença/commit inicial, prefira o fluxo com `git clone` para evitar históricos independentes.
