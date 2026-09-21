$ErrorActionPreference = "Stop"

$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
  $candidates = @(
    "$env:ProgramFiles\Git\usr\bin\openssl.exe",
    "$env:ProgramFiles\Git\mingw64\bin\openssl.exe",
    "${env:ProgramFiles(x86)}\Git\usr\bin\openssl.exe"
  )
  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path $candidate)) { $openssl = $candidate; break }
  }
}
if (-not $openssl) { throw "OpenSSL nao encontrado. O Git for Windows normalmente inclui OpenSSL." }
if ($openssl -is [System.Management.Automation.ApplicationInfo]) { $openssl = $openssl.Source }

$temp = Join-Path $env:TEMP ("extnest-key-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $temp | Out-Null
$private = Join-Path $temp "private.pem"
$public = Join-Path $temp "public.der"
try {
  & $openssl genrsa -out $private 2048 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar chave RSA." }
  & $openssl rsa -in $private -pubout -outform DER -out $public 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao exportar chave publica." }

  $pub = [IO.File]::ReadAllBytes($public)
  $key = [Convert]::ToBase64String($pub)
  $sha = [System.Security.Cryptography.SHA256]::Create().ComputeHash($pub)
  $alphabet = "abcdefghijklmnop"
  $id = ""
  for ($i=0; $i -lt 16; $i++) {
    $b = $sha[$i]
    $id += $alphabet[($b -shr 4) -band 15]
    $id += $alphabet[$b -band 15]
  }

  Write-Host "manifest key:" -ForegroundColor Cyan
  Write-Output $key
  Write-Host ""
  Write-Host "Extension ID:" -ForegroundColor Cyan
  Write-Output $id
  Write-Host ""
  Write-Host "Coloque somente a chave PUBLICA no manifest.json. A chave privada temporaria foi descartada."
}
finally {
  Remove-Item -Recurse -Force $temp -ErrorAction SilentlyContinue
}
