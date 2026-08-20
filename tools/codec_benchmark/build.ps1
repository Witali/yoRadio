[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-codec-benchmark",
    [string]$DependencyRoot = "",
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
$arguments = @("-D", "YORADIO_CODEC_BENCHMARK=ON") + $IdfArguments

& $builder `
    -BuildDirectory $BuildDirectory `
    -DependencyRoot $DependencyRoot `
    -Sdkconfig "sdkconfig.codec-benchmark" `
    -SdkconfigDefaults $defaults `
    -Setup:$Setup `
    -IdfArguments $arguments
if ($LASTEXITCODE -ne 0) {
    throw "Codec benchmark build failed with exit code $LASTEXITCODE"
}
