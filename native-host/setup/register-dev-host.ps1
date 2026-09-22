$ErrorActionPreference = "Stop"

$HostRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $HostRoot

$StableRoot = Join-Path $env:LOCALAPPDATA "ExtNest\NativeHostDev"
$StableLauncher = Join-Path $StableRoot "launcher.cmd"
$StableRepoPath = Join-Path $StableRoot "repo-path.txt"
$StableManifest = Join-Path $StableRoot "com.extnest.host.json"

New-Item -ItemType Directory -Force -Path $StableRoot | Out-Null

# Keep only a pointer to the current development checkout.
[System.IO.File]::WriteAllText(
    $StableRepoPath,
    $RepoRoot,
    [System.Text.UTF8Encoding]::new($false)
)

$LauncherContent = @'
@echo off
setlocal

set "ROOT=%~dp0"
set "REPO_FILE=%ROOT%repo-path.txt"

if not exist "%REPO_FILE%" exit /b 2

set /p EXTNEST_REPO=<"%REPO_FILE%"

if not exist "%EXTNEST_REPO%\native-host\extnest_host.py" exit /b 3

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%EXTNEST_REPO%\native-host\extnest_host.py"
  exit /b %errorlevel%
)

python "%EXTNEST_REPO%\native-host\extnest_host.py"
exit /b %errorlevel%
'@

[System.IO.File]::WriteAllText(
    $StableLauncher,
    $LauncherContent,
    [System.Text.ASCIIEncoding]::new()
)

$SourceManifest = Join-Path $HostRoot "com.extnest.host.json"
$Manifest = Get-Content $SourceManifest -Raw | ConvertFrom-Json
$Manifest.path = $StableLauncher

$ManifestJson = $Manifest | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText(
    $StableManifest,
    $ManifestJson,
    [System.Text.UTF8Encoding]::new($false)
)

$Edge = "HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"
$Chrome = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"

$PreviousEdge = (Get-Item -Path $Edge -ErrorAction SilentlyContinue).GetValue("")
$PreviousChrome = (Get-Item -Path $Chrome -ErrorAction SilentlyContinue).GetValue("")

New-Item -Force -Path $Edge | Out-Null
New-Item -Force -Path $Chrome | Out-Null

Set-Item -Path $Edge -Value $StableManifest
Set-Item -Path $Chrome -Value $StableManifest

Write-Host ""
Write-Host "ExtNest Native Host DEV registrado em caminho estavel." -ForegroundColor Green
Write-Host "Bootstrap: $StableLauncher"
Write-Host "Manifest:  $StableManifest"
Write-Host "Repo:      $RepoRoot"
Write-Host ""

if ($PreviousEdge -and $PreviousEdge -ne $StableManifest) {
    Write-Host "Edge migrado do registro antigo:" -ForegroundColor Yellow
    Write-Host "  $PreviousEdge"
    Write-Host "  -> $StableManifest"
}

if ($PreviousChrome -and $PreviousChrome -ne $StableManifest) {
    Write-Host "Chrome migrado do registro antigo:" -ForegroundColor Yellow
    Write-Host "  $PreviousChrome"
    Write-Host "  -> $StableManifest"
}

Write-Host ""
Write-Host "Enquanto o projeto continuar no mesmo caminho, apagar/reclonar o repo nao exige novo registro." -ForegroundColor Cyan
Write-Host "ExtNest dev ID: econfanmnmmcggpgdflcipmdlmkcbiag"
