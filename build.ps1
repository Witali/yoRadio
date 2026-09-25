[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build",
    [string]$DependencyRoot = "",
    [switch]$Setup,
    [switch]$DeepSleepClock,
    [switch]$Rtc32kCrystal,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
if (-not $PSBoundParameters.ContainsKey("BuildDirectory")) {
    if ($DeepSleepClock) { $BuildDirectory += "-deep-sleep-clock" }
    if ($Rtc32kCrystal) { $BuildDirectory += "-rtc32k" }
}
$nativeBuild = Join-Path $PSScriptRoot "idf\esp32c3-oled-native\build.ps1"

& $nativeBuild `
    -BuildDirectory $BuildDirectory `
    -DependencyRoot $DependencyRoot `
    -Setup:$Setup `
    -DeepSleepClock:$DeepSleepClock `
    -Rtc32kCrystal:$Rtc32kCrystal `
    -IdfArguments $IdfArguments
if ($LASTEXITCODE -ne 0) {
    throw "Native ESP32-C3 build failed with exit code $LASTEXITCODE"
}
