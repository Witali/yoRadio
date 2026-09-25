[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-production",
    [string]$DependencyRoot = "",
    [string]$Sdkconfig = "build-production/sdkconfig",
    [string]$FirmwareOutputDirectory = "",
    [switch]$NoFirmwareExport,
    [switch]$Setup,
    [switch]$DeepSleepClock,
    [switch]$Rtc32kCrystal,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IdfArguments = @("build")
)

$ErrorActionPreference = "Stop"
if ($DeepSleepClock -or $Rtc32kCrystal) {
    if (-not $PSBoundParameters.ContainsKey("BuildDirectory")) {
        if ($DeepSleepClock) { $BuildDirectory += "-deep-sleep-clock" }
        if ($Rtc32kCrystal) { $BuildDirectory += "-rtc32k" }
    }
    if (-not $PSBoundParameters.ContainsKey("Sdkconfig")) {
        $Sdkconfig = "$BuildDirectory/sdkconfig"
    }
}
$buildArguments = @{
    DeepSleepClock = $DeepSleepClock
    Rtc32kCrystal = $Rtc32kCrystal
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
$buildExitCode = $LASTEXITCODE

$applicationCommands = @("all", "build", "app", "app-flash", "flash")
$shouldExportApplication = @(
    $IdfArguments | Where-Object { $_ -in $applicationCommands }
).Count -gt 0

if ($buildExitCode -eq 0 -and $shouldExportApplication -and -not $NoFirmwareExport) {
    $resolvedBuildDirectory = if ([IO.Path]::IsPathRooted($BuildDirectory)) {
        $BuildDirectory
    } else {
        Join-Path $PSScriptRoot $BuildDirectory
    }
    $applicationImage = Join-Path $resolvedBuildDirectory "yoradio_esp32c3_oled_native.bin"
    if (-not (Test-Path -LiteralPath $applicationImage -PathType Leaf)) {
        throw "Production build succeeded but application image was not found: $applicationImage"
    }

    $repositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
    $resolvedFirmwareOutput = if ([string]::IsNullOrWhiteSpace($FirmwareOutputDirectory)) {
        if ($DeepSleepClock -and $Rtc32kCrystal) {
            Join-Path $repositoryRoot "firmware\development\esp32c3-oled-native-deep-sleep-clock-rtc32k"
        } elseif ($Rtc32kCrystal) {
            Join-Path $repositoryRoot "firmware\development\esp32c3-oled-native-production-rtc32k"
        } elseif ($DeepSleepClock) {
            Join-Path $repositoryRoot "firmware\development\esp32c3-oled-native-deep-sleep-clock"
        } else {
            Join-Path $repositoryRoot "firmware\development\esp32c3-oled-native-production"
        }
    } elseif ([IO.Path]::IsPathRooted($FirmwareOutputDirectory)) {
        $FirmwareOutputDirectory
    } else {
        Join-Path $repositoryRoot $FirmwareOutputDirectory
    }

    New-Item -ItemType Directory -Force -Path $resolvedFirmwareOutput | Out-Null
    $savedImage = Join-Path $resolvedFirmwareOutput "app.bin"
    Copy-Item -LiteralPath $applicationImage -Destination $savedImage -Force
    Write-Host "Production firmware saved to $savedImage"
}

exit $buildExitCode
