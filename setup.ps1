[CmdletBinding()]
param(
    [string]$DependencyRoot = "",
    [switch]$SkipToolchain
)

$ErrorActionPreference = "Stop"
$nativeSetup = Join-Path $PSScriptRoot "idf\esp32c3-oled-native\setup.ps1"

& $nativeSetup -DependencyRoot $DependencyRoot -SkipToolchain:$SkipToolchain
if ($LASTEXITCODE -ne 0) {
    throw "Native ESP32-C3 setup failed with exit code $LASTEXITCODE"
}
