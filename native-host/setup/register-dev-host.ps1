$ErrorActionPreference = "Stop"
$HostRoot = Split-Path -Parent $PSScriptRoot
$SourceManifest = Join-Path $HostRoot "com.extnest.host.json"
$Manifest = Get-Content $SourceManifest -Raw | ConvertFrom-Json
$Launcher = (Resolve-Path (Join-Path $HostRoot "launcher.cmd")).Path
$Manifest.path = $Launcher
$Generated = Join-Path $HostRoot "com.extnest.host.generated.json"
$ManifestJson = $Manifest | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText(
    $Generated,
    $ManifestJson,
    [System.Text.UTF8Encoding]::new($false)
)

$Edge = "HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"
$Chrome = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"
$PreviousEdge = (Get-Item -Path $Edge -ErrorAction SilentlyContinue).GetValue("")
$PreviousChrome = (Get-Item -Path $Chrome -ErrorAction SilentlyContinue).GetValue("")
New-Item -Force -Path $Edge | Out-Null
New-Item -Force -Path $Chrome | Out-Null
Set-Item -Path $Edge -Value $Generated
Set-Item -Path $Chrome -Value $Generated

Write-Host "ExtNest Native Host registrado para desenvolvimento." -ForegroundColor Green
Write-Host "Manifest: $Generated"
Write-Host "Launcher: $Launcher"
if ($PreviousEdge -and $PreviousEdge -ne $Generated) {
    Write-Host "Edge atualizado: $PreviousEdge -> $Generated" -ForegroundColor Yellow
}
if ($PreviousChrome -and $PreviousChrome -ne $Generated) {
    Write-Host "Chrome atualizado: $PreviousChrome -> $Generated" -ForegroundColor Yellow
}
Write-Host "ExtNest dev ID: econfanmnmmcggpgdflcipmdlmkcbiag"
