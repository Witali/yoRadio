[CmdletBinding()]
param(
    [string]$DependencyRoot = "",
    [string]$BuildDirectory = "",
    [switch]$Setup,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$targetRoot = $PSScriptRoot
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $targetRoot "..\.."))
$gitCommon = (& git -C $targetRoot rev-parse --path-format=absolute --git-common-dir).Trim()
if ($LASTEXITCODE -ne 0) { throw "Cannot locate the repository common directory" }
$sharedRoot = Split-Path -Parent $gitCommon
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $DependencyRoot = Join-Path $sharedRoot ".build\dependencies\arduino-esp8266audio"
}
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
if ([string]::IsNullOrWhiteSpace($BuildDirectory)) {
    $BuildDirectory = Join-Path $repositoryRoot ".build\esp8266audio-webradio"
}
$BuildDirectory = [IO.Path]::GetFullPath($BuildDirectory)

if ($Setup) {
    & (Join-Path $targetRoot "setup.ps1") -DependencyRoot $DependencyRoot
    if ($LASTEXITCODE -ne 0) { throw "Dependency setup failed" }
}

$installed = Get-Command arduino-cli -ErrorAction SilentlyContinue
$localCli = Join-Path $DependencyRoot "cli\arduino-cli.exe"
if ($installed) {
    $cli = $installed.Source
} elseif (Test-Path -LiteralPath $localCli -PathType Leaf) {
    $cli = $localCli
} else {
    throw "Arduino CLI is unavailable. Run build.ps1 -Setup first."
}

$env:ARDUINO_DIRECTORIES_DATA = Join-Path $DependencyRoot "data"
$env:ARDUINO_DIRECTORIES_DOWNLOADS = Join-Path $DependencyRoot "downloads"
$env:ARDUINO_DIRECTORIES_USER = Join-Path $DependencyRoot "user"
if ($Clean -and (Test-Path -LiteralPath $BuildDirectory)) {
    Remove-Item -LiteralPath $BuildDirectory -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $BuildDirectory | Out-Null

$fqbn = "esp8266:esp8266:d1_mini:xtal=160,vt=flash,exception=disabled,stacksmash=enabled,ssl=basic,mmu=3232,non32xfer=fast,eesz=4M2M,ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600"
$sketch = Join-Path $targetRoot "ESP8266AudioWebRadio"
& $cli compile --fqbn $fqbn `
    --build-property "build.flash_mode=qio" `
    --build-property "build.flash_flags=-DFLASHMODE_QIO" `
    --build-property "build.flash_freq=40" `
    --output-dir $BuildDirectory $sketch
if ($LASTEXITCODE -ne 0) { throw "WebRadio build failed" }

$app = Get-ChildItem -LiteralPath $BuildDirectory -Filter "*.ino.bin" | Select-Object -First 1
if (-not $app) { throw "Arduino CLI did not produce an application binary" }
$firmwareDirectory = Join-Path $repositoryRoot "firmware\development\web-radio"
New-Item -ItemType Directory -Force -Path $firmwareDirectory | Out-Null
Copy-Item -LiteralPath $app.FullName -Destination (Join-Path $firmwareDirectory "app.bin") -Force

Write-Host "Firmware: $(Join-Path $firmwareDirectory 'app.bin')"
