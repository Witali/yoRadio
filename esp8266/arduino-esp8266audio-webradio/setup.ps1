[CmdletBinding()]
param([string]$DependencyRoot = "")

$ErrorActionPreference = "Stop"
$targetRoot = $PSScriptRoot
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $targetRoot "..\.."))
$gitCommon = (& git -C $targetRoot rev-parse --path-format=absolute --git-common-dir).Trim()
if ($LASTEXITCODE -ne 0) { throw "Cannot locate the repository common directory" }
$sharedRoot = Split-Path -Parent $gitCommon
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    # GCC 10 for Windows does not reliably open its target C++ headers when
    # installed below a long worktree path. Keep the pinned cache under the
    # short, already ignored common-repository .build directory.
    $DependencyRoot = Join-Path $sharedRoot ".build\dependencies\arduino-esp8266audio"
}
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$cliVersion = "1.5.1"
$cliArchiveName = "arduino-cli_${cliVersion}_Windows_64bit.zip"
$cliArchiveUrl = "https://github.com/arduino/arduino-cli/releases/download/v$cliVersion/$cliArchiveName"
$cliArchiveSha256 = "FABE42E0EB04D00E776A66178299FF95A46C623DBC260F997E58FD514853DD40"
$localCli = Join-Path $DependencyRoot "cli\arduino-cli.exe"
$downloads = Join-Path $DependencyRoot "downloads"

$installed = Get-Command arduino-cli -ErrorAction SilentlyContinue
if ($installed) {
    $cli = $installed.Source
    Write-Host "Using installed Arduino CLI: $cli"
} else {
    $cli = $localCli
    if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
        New-Item -ItemType Directory -Force -Path $downloads, (Split-Path -Parent $cli) | Out-Null
        $archive = Join-Path $downloads $cliArchiveName
        if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
            Invoke-WebRequest -Uri $cliArchiveUrl -OutFile $archive
        }
        $actualHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash
        if ($actualHash -ne $cliArchiveSha256) {
            throw "Arduino CLI checksum mismatch: expected $cliArchiveSha256, got $actualHash"
        }
        Expand-Archive -LiteralPath $archive -DestinationPath (Split-Path -Parent $cli) -Force
    }
    Write-Host "Using bundled Arduino CLI: $cli"
}

$env:ARDUINO_DIRECTORIES_DATA = Join-Path $DependencyRoot "data"
$env:ARDUINO_DIRECTORIES_DOWNLOADS = $downloads
$env:ARDUINO_DIRECTORIES_USER = Join-Path $DependencyRoot "user"
$indexUrl = "https://arduino.esp8266.com/stable/package_esp8266com_index.json"

& $cli core update-index --additional-urls $indexUrl
if ($LASTEXITCODE -ne 0) { throw "Arduino core index update failed" }
& $cli core install "esp8266:esp8266@3.1.2" --additional-urls $indexUrl
if ($LASTEXITCODE -ne 0) { throw "ESP8266 Arduino core installation failed" }
& $cli lib install "ESP8266Audio@2.4.1"
if ($LASTEXITCODE -ne 0) { throw "ESP8266Audio installation failed" }

Write-Host "ESP8266Audio build dependencies are ready in $DependencyRoot"
