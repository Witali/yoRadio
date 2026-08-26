[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-overclock",
    [string]$DependencyRoot = "",
    [string]$Sdkconfig = "build-overclock/sdkconfig",
    [switch]$Setup,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
$buildArguments = @{
    BuildDirectory = $BuildDirectory
    Sdkconfig = $Sdkconfig
    SdkconfigDefaults = @(
        "sdkconfig.defaults"
        "sdkconfig.overclock.defaults"
    )
    IdfArguments = @(
        "-D", "YORADIO_OVERCLOCK_EXPERIMENT=ON"
    ) + $IdfArguments
}
if (-not [string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $buildArguments.DependencyRoot = $DependencyRoot
}
if ($Setup) {
    $buildArguments.Setup = $true
}

& (Join-Path $PSScriptRoot "build.ps1") @buildArguments
exit $LASTEXITCODE
