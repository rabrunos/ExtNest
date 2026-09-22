$ErrorActionPreference = "Stop"

$StableRoot = Join-Path $env:LOCALAPPDATA "ExtNest\NativeHostDev"
$Output = Join-Path $StableRoot "oauth-private.json"

New-Item -ItemType Directory -Force -Path $StableRoot | Out-Null

$Secure = Read-Host "Cole o Client Secret do OAuth App ExtNest" -AsSecureString
$Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)

try {
    $Secret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr)

    if ([string]::IsNullOrWhiteSpace($Secret)) {
        throw "Client Secret vazio."
    }

    $Payload = @{
        github = @{
            client_secret = $Secret
        }
    } | ConvertTo-Json -Depth 5

    [System.IO.File]::WriteAllText(
        $Output,
        $Payload,
        [System.Text.UTF8Encoding]::new($false)
    )

    Write-Host ""
    Write-Host "Client Secret salvo fora do repositorio:" -ForegroundColor Green
    Write-Host $Output
    Write-Host ""
    Write-Host "Apagar ou reclonar C:\Dev\ExtNest nao remove mais essa configuracao." -ForegroundColor Cyan
}
finally {
    if ($Ptr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }
}
