[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-production",
    [string]$DependencyRoot = "",
    [string]$Sdkconfig = "build-production/sdkconfig",
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
        "sdkconfig.production.defaults"
    )
    IdfArguments = $IdfArguments
}
if (-not [string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $buildArguments.DependencyRoot = $DependencyRoot
}
if ($Setup) {
    $buildArguments.Setup = $true
}

& (Join-Path $PSScriptRoot "build.ps1") @buildArguments
exit $LASTEXITCODE
