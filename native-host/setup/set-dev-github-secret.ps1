$ErrorActionPreference = "Stop"

$NativeHostRoot = Split-Path -Parent $PSScriptRoot
$Output = Join-Path $NativeHostRoot "oauth-private.json"

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
    Write-Host "Client Secret salvo localmente em:" -ForegroundColor Green
    Write-Host $Output
    Write-Host ""
    Write-Host "Esse arquivo esta no .gitignore e nao deve ser commitado." -ForegroundColor Yellow
}
finally {
    if ($Ptr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }
}
