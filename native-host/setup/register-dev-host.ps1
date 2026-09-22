$ErrorActionPreference = "Stop"

$HostRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $HostRoot

$StableRoot = Join-Path $env:LOCALAPPDATA "ExtNest\NativeHostDev"
$StableLauncher = Join-Path $StableRoot "launcher.exe"
$StableRepoPath = Join-Path $StableRoot "repo-path.txt"
$StableManifest = Join-Path $StableRoot "com.extnest.host.json"

New-Item -ItemType Directory -Force -Path $StableRoot | Out-Null

[System.IO.File]::WriteAllText(
    $StableRepoPath,
    $RepoRoot,
    [System.Text.UTF8Encoding]::new($false)
)

$LauncherSource = @'
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;

public static class ExtNestNativeLauncher
{
    static readonly string Root = AppDomain.CurrentDomain.BaseDirectory;
    static readonly string RepoFile = Path.Combine(Root, "repo-path.txt");

    static string ReadRepo()
    {
        if (!File.Exists(RepoFile))
            throw new FileNotFoundException("repo-path.txt not found", RepoFile);

        var repo = File.ReadAllText(RepoFile, Encoding.UTF8).Trim();
        if (String.IsNullOrWhiteSpace(repo))
            throw new InvalidOperationException("repo-path.txt is empty");

        return repo;
    }

    static Process StartPython(string repo)
    {
        var hostScript = Path.Combine(repo, "native-host", "extnest_host.py");
        if (!File.Exists(hostScript))
            throw new FileNotFoundException("extnest_host.py not found", hostScript);

        Exception last = null;
        string[] files = { "py.exe", "python.exe" };
        string[] args = {
            "-3 \"" + hostScript + "\"",
            "\"" + hostScript + "\""
        };

        for (int i = 0; i < files.Length; i++)
        {
            try
            {
                var psi = new ProcessStartInfo();
                psi.FileName = files[i];
                psi.Arguments = args[i];
                psi.UseShellExecute = false;
                psi.CreateNoWindow = true;
                psi.RedirectStandardInput = true;
                psi.RedirectStandardOutput = true;
                psi.RedirectStandardError = true;
                psi.WorkingDirectory = Path.Combine(repo, "native-host");

                var process = Process.Start(psi);
                if (process != null)
                    return process;
            }
            catch (Exception ex)
            {
                last = ex;
            }
        }

        throw new InvalidOperationException(
            "Python launcher not found. Install Python or py.exe and keep it in PATH.",
            last
        );
    }

    static void Pump(Stream input, Stream output)
    {
        try
        {
            var buffer = new byte[8192];
            int read;
            while ((read = input.Read(buffer, 0, buffer.Length)) > 0)
            {
                output.Write(buffer, 0, read);
                output.Flush();
            }
        }
        catch { }

        try { output.Close(); } catch { }
    }

    static int SelfTest()
    {
        try
        {
            var repo = ReadRepo();
            var hostScript = Path.Combine(repo, "native-host", "extnest_host.py");
            if (!File.Exists(hostScript))
            {
                Console.Error.WriteLine("Host script missing: " + hostScript);
                return 3;
            }

            Console.WriteLine("OK");
            Console.WriteLine("Repo=" + repo);
            Console.WriteLine("Host=" + hostScript);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.ToString());
            return 2;
        }
    }

    public static int Main(string[] args)
    {
        if (args.Length > 0 && args[0] == "--self-test")
            return SelfTest();

        try
        {
            var repo = ReadRepo();

            using (var python = StartPython(repo))
            {
                var stdinThread = new Thread(() =>
                    Pump(Console.OpenStandardInput(), python.StandardInput.BaseStream)
                );
                stdinThread.IsBackground = true;
                stdinThread.Start();

                var stderrThread = new Thread(() =>
                    Pump(python.StandardError.BaseStream, Console.OpenStandardError())
                );
                stderrThread.IsBackground = true;
                stderrThread.Start();

                Pump(python.StandardOutput.BaseStream, Console.OpenStandardOutput());
                python.WaitForExit();
                return python.ExitCode;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.ToString());
            return 1;
        }
    }
}
'@

if (Test-Path $StableLauncher) {
    Remove-Item -Force $StableLauncher
}

Add-Type -TypeDefinition $LauncherSource -Language CSharp -OutputAssembly $StableLauncher -OutputType ConsoleApplication

if (-not (Test-Path $StableLauncher)) {
    throw "Falha ao criar launcher.exe em $StableLauncher"
}

$SourceManifest = Join-Path $HostRoot "com.extnest.host.json"
$Manifest = Get-Content $SourceManifest -Raw | ConvertFrom-Json
$Manifest.path = $StableLauncher

$ManifestJson = $Manifest | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText(
    $StableManifest,
    $ManifestJson,
    [System.Text.UTF8Encoding]::new($false)
)

$EdgeReg = "HKCU\Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"
$ChromeReg = "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"

& reg.exe ADD $EdgeReg /ve /t REG_SZ /d $StableManifest /f | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao registrar Native Host no Microsoft Edge."
}

& reg.exe ADD $ChromeReg /ve /t REG_SZ /d $StableManifest /f | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao registrar Native Host no Google Chrome."
}

$EdgePs = "HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\com.extnest.host"
$ChromePs = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.extnest.host"

$EdgeValue = (Get-Item -Path $EdgePs -ErrorAction Stop).GetValue("")
$ChromeValue = (Get-Item -Path $ChromePs -ErrorAction Stop).GetValue("")

if ($EdgeValue -ne $StableManifest) {
    throw "Registro do Edge invalido. Atual: $EdgeValue | Esperado: $StableManifest"
}
if ($ChromeValue -ne $StableManifest) {
    throw "Registro do Chrome invalido. Atual: $ChromeValue | Esperado: $StableManifest"
}

$CheckManifest = Get-Content $StableManifest -Raw | ConvertFrom-Json

if ($CheckManifest.name -ne "com.extnest.host") {
    throw "Manifest Native Host possui nome invalido."
}
if ($CheckManifest.path -ne $StableLauncher) {
    throw "Manifest Native Host aponta para caminho incorreto: $($CheckManifest.path)"
}
if (-not (Test-Path $CheckManifest.path)) {
    throw "Binario do Native Host nao existe: $($CheckManifest.path)"
}
if ($CheckManifest.allowed_origins -notcontains "chrome-extension://econfanmnmmcggpgdflcipmdlmkcbiag/") {
    throw "Manifest Native Host nao permite o ExtNest DEV."
}

$SelfTest = & $StableLauncher --self-test 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "launcher.exe falhou no self-test: $($SelfTest -join ' | ')"
}

Write-Host ""
Write-Host "ExtNest Native Host DEV registrado e validado." -ForegroundColor Green
Write-Host "Launcher EXE: $StableLauncher"
Write-Host "Manifest:     $StableManifest"
Write-Host "Repo:         $RepoRoot"
Write-Host "Edge Registry:$EdgeValue"
Write-Host ""
Write-Host "Self-test:" -ForegroundColor Cyan
$SelfTest | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Feche abas antigas do ExtNest e clique Recarregar em edge://extensions/." -ForegroundColor Yellow
