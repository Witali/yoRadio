[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-codec-benchmark",
    [string]$DependencyRoot = "",
    [ValidateSet("espressif", "helix", "minimp3")]
    [string]$Mp3Decoder = "espressif",
    [switch]$Setup,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$project = Join-Path $repository "idf\esp32c3-oled-native"
$builder = Join-Path $project "build.ps1"
$defaults = @(
    "sdkconfig.defaults",
    "sdkconfig.codec-benchmark.defaults"
)
$defaults += Join-Path $PSScriptRoot "sdkconfig.mp3-$Mp3Decoder.defaults"
$arguments = @("-D", "YORADIO_CODEC_BENCHMARK=ON") + $IdfArguments
$sdkconfig = Join-Path $BuildDirectory "sdkconfig"

& $builder `
    -BuildDirectory $BuildDirectory `
    -DependencyRoot $DependencyRoot `
    -Sdkconfig $sdkconfig `
    -SdkconfigDefaults $defaults `
    -Setup:$Setup `
    -IdfArguments $arguments
if ($LASTEXITCODE -ne 0) {
    throw "Codec benchmark build failed with exit code $LASTEXITCODE"
}
