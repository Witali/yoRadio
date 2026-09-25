[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build",
    [string]$DependencyRoot = "",
    [switch]$Setup,
    [switch]$DeepSleepClock,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
if ($DeepSleepClock -and -not $PSBoundParameters.ContainsKey("BuildDirectory")) {
    $BuildDirectory = "build-deep-sleep-clock"
}
$nativeBuild = Join-Path $PSScriptRoot "idf\esp32c3-oled-native\build.ps1"

& $nativeBuild `
    -BuildDirectory $BuildDirectory `
    -DependencyRoot $DependencyRoot `
    -Setup:$Setup `
    -DeepSleepClock:$DeepSleepClock `
    -IdfArguments $IdfArguments
if ($LASTEXITCODE -ne 0) {
    throw "Native ESP32-C3 build failed with exit code $LASTEXITCODE"
}
