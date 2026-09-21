$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ExtensionDir = Join-Path $RepoRoot "extension"
$ManifestPath = Join-Path $ExtensionDir "manifest.json"

if (-not (Test-Path $ManifestPath)) {
  throw "manifest.json nao encontrado em extension/"
}

$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$Version = $Manifest.version

$Dist = Join-Path $RepoRoot "dist"
New-Item -ItemType Directory -Force -Path $Dist | Out-Null

$Zip = Join-Path $Dist ("ExtNest-store-" + $Version + ".zip")
if (Test-Path $Zip) { Remove-Item -Force $Zip }

Compress-Archive -Path (Join-Path $ExtensionDir "*") -DestinationPath $Zip -CompressionLevel Optimal

Write-Host ""
Write-Host "Pacote de Store criado:" -ForegroundColor Green
Write-Host $Zip
Write-Host ""
Write-Host "O manifest.json esta na raiz do ZIP, como esperado para upload."
