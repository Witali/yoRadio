[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^COM[0-9]+$')]
    [string]$Port,

    [ValidateSet("DAC", "PDM")]
    [string]$AudioOutput = "DAC",

    [ValidateSet(115200, 230400, 460800, 921600)]
    [int]$Baud = 460800,

    [switch]$SkipBuild,

    [switch]$FlashFilesystem,

    [string]$ArduinoCli
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\..\.."))
$sketch = Join-Path $repository "yoRadio"
$fqbn = "esp32:esp32:esp32:FlashSize=4M,PartitionScheme=min_spiffs,PSRAM=disabled"
$buildName = if ($AudioOutput -eq "PDM") { "cyd2usb-pdm" } else { "cyd2usb-min-spiffs" }
$buildDirectory = Join-Path $repository ".build\$buildName"
$spiffsImage = Join-Path $buildDirectory "yoRadio.spiffs.bin"
$spiffsOffset = "0x3D0000"
$spiffsSize = 0x20000

function Resolve-ArduinoCli {
    param([string]$ExplicitPath)

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "Arduino CLI was not found at $ExplicitPath"
        }
        return [IO.Path]::GetFullPath($ExplicitPath)
    }

    $command = Get-Command arduino-cli.exe -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) {
        return $command.Source
    }

    $knownPaths = @(
        (Join-Path $repository "local_tools\arduino-cli\arduino-cli.exe"),
        "C:\Work\HLV-codec\local_tools\arduino-cli\arduino-cli.exe"
    )
    foreach ($candidate in $knownPaths) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    throw "arduino-cli.exe was not found. Pass its full path with -ArduinoCli."
}

function Find-Esp32Tool {
    param(
        [Parameter(Mandatory)][string]$PackageRoot,
        [Parameter(Mandatory)][string]$ToolDirectory,
        [Parameter(Mandatory)][string]$Executable
    )

    $tool = Get-ChildItem -LiteralPath (Join-Path $PackageRoot "tools\$ToolDirectory") `
        -Directory -ErrorAction Stop |
        Sort-Object Name -Descending |
        ForEach-Object { Join-Path $_.FullName $Executable } |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        Select-Object -First 1
    if (-not $tool) {
        throw "$Executable was not found under $PackageRoot"
    }
    return $tool
}

function Install-YoRadioGfxFont {
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "YoRadio GFX font is missing: $Source"
    }
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        throw "Adafruit GFX glcdfont.c is missing: $Destination"
    }

    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Source).Hash
    $destinationHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash
    if ($sourceHash -ne $destinationHash) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        $destinationHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash
        if ($destinationHash -ne $sourceHash) {
            throw "Failed to install the YoRadio GFX font at $Destination"
        }
        Write-Host "Installed the YoRadio Cyrillic/icon font in the local Adafruit GFX library."
    } else {
        Write-Host "YoRadio Cyrillic/icon font is already installed in the local Adafruit GFX library."
    }
}

if (-not $SkipBuild) {
    $resolvedArduinoCli = Resolve-ArduinoCli $ArduinoCli
    $localLibraries = Join-Path $repository ".build\libraries"
    $yoRadioFont = Join-Path $sketch "fonts\glcdfont.c"
    $adafruitFont = Join-Path $localLibraries "Adafruit_GFX_Library\glcdfont.c"
    $compileArguments = @(
        "compile",
        "--clean",
        "--fqbn", $fqbn,
        "--build-path", $buildDirectory,
        "--libraries", $localLibraries
    )
    if ($AudioOutput -eq "PDM") {
        $compileArguments += @(
            "--build-property", "compiler.c.extra_flags=-DI2S_INTERNAL_OUTPUT=1",
            "--build-property", "compiler.cpp.extra_flags=-DI2S_INTERNAL_OUTPUT=1"
        )
    }
    $compileArguments += $sketch

    if ($PSCmdlet.ShouldProcess($buildDirectory, "build the $AudioOutput YoRadio firmware")) {
        Install-YoRadioGfxFont -Source $yoRadioFont -Destination $adafruitFont
        & $resolvedArduinoCli @compileArguments
        if ($LASTEXITCODE -ne 0) {
            throw "Arduino build failed with exit code $LASTEXITCODE"
        }
    } else {
        return
    }
}

$buildOptionsPath = Join-Path $buildDirectory "build.options.json"
if (-not (Test-Path -LiteralPath $buildOptionsPath -PathType Leaf)) {
    throw "Firmware is not built: missing $buildOptionsPath"
}
$buildOptions = Get-Content -Raw -LiteralPath $buildOptionsPath | ConvertFrom-Json
$esp32Hardware = (($buildOptions.hardwareFolders -split ',') | Select-Object -First 1)
if (-not (Test-Path -LiteralPath $esp32Hardware -PathType Container)) {
    throw "ESP32 Arduino hardware directory was not found: $esp32Hardware"
}
$packageRoot = [IO.Path]::GetFullPath((Join-Path $esp32Hardware "..\..\.."))
$esptool = Find-Esp32Tool -PackageRoot $packageRoot -ToolDirectory "esptool_py" -Executable "esptool.exe"
$bootApp = Join-Path $esp32Hardware "tools\partitions\boot_app0.bin"

$images = [ordered]@{
    "0x1000" = Join-Path $buildDirectory "yoRadio.ino.bootloader.bin"
    "0x8000" = Join-Path $buildDirectory "yoRadio.ino.partitions.bin"
    "0xe000" = $bootApp
    "0x10000" = Join-Path $buildDirectory "yoRadio.ino.bin"
}
foreach ($image in $images.Values) {
    if (-not (Test-Path -LiteralPath $image -PathType Leaf)) {
        throw "Required flash image is missing: $image"
    }
}

if ($FlashFilesystem) {
    $mkspiffs = Find-Esp32Tool -PackageRoot $packageRoot -ToolDirectory "mkspiffs" -Executable "mkspiffs.exe"
    if ($PSCmdlet.ShouldProcess($spiffsImage, "create a 128 KiB SPIFFS image from yoRadio/data")) {
        & $mkspiffs -c (Join-Path $sketch "data") -p 256 -b 4096 -s $spiffsSize $spiffsImage
        if ($LASTEXITCODE -ne 0) {
            throw "mkspiffs failed with exit code $LASTEXITCODE"
        }
    } else {
        return
    }
    $images[$spiffsOffset] = $spiffsImage
}

Write-Host "YoRadio flash plan:"
Write-Host "  Port:         $Port"
Write-Host "  Audio output: $AudioOutput"
Write-Host "  Build:        $buildDirectory"
Write-Host "  Baud:         $Baud"
if ($FlashFilesystem) {
    Write-Warning "SPIFFS will be overwritten; saved Wi-Fi networks and playlists may be lost."
} else {
    Write-Host "  Settings:     preserved (NVS and SPIFFS are not written)"
}
foreach ($entry in $images.GetEnumerator()) {
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Value).Hash
    Write-Host ("  {0}: {1} (SHA256 {2})" -f $entry.Key, $entry.Value, $hash)
}

$flashArguments = @(
    "--chip", "esp32",
    "--port", $Port,
    "--baud", $Baud.ToString(),
    "--before", "default-reset",
    "--after", "hard-reset",
    "write-flash",
    "--flash-mode", "dio",
    "--flash-freq", "80m",
    "--flash-size", "4MB"
)
foreach ($entry in $images.GetEnumerator()) {
    $flashArguments += @($entry.Key, $entry.Value)
}

$flashOperation = if ($FlashFilesystem) {
    "erase affected sectors and flash $AudioOutput YoRadio plus SPIFFS"
} else {
    "flash $AudioOutput YoRadio while preserving NVS and SPIFFS settings"
}
if (-not $PSCmdlet.ShouldProcess($Port, $flashOperation)) {
    return
}

$savedConfig = $env:ESPTOOL_CFGFILE
$savedAttempts = $env:ESPTOOL_OPEN_PORT_ATTEMPTS
try {
    $env:ESPTOOL_CFGFILE = Join-Path $PSScriptRoot "..\esptool.cfg"
    $env:ESPTOOL_OPEN_PORT_ATTEMPTS = "60"
    & $esptool @flashArguments
    $flashExitCode = $LASTEXITCODE

    if ($flashExitCode -ne 0 -and $Baud -ne 115200) {
        Write-Warning "Flash at $Baud baud failed; retrying conservatively at 115200 baud."
        $baudIndex = [Array]::IndexOf($flashArguments, $Baud.ToString())
        $flashArguments[$baudIndex] = "115200"
        & $esptool @flashArguments
        $flashExitCode = $LASTEXITCODE
    }
    if ($flashExitCode -ne 0) {
        throw "esptool failed with exit code $flashExitCode"
    }
} finally {
    $env:ESPTOOL_CFGFILE = $savedConfig
    $env:ESPTOOL_OPEN_PORT_ATTEMPTS = $savedAttempts
}

if ($FlashFilesystem) {
    Write-Host "YoRadio $AudioOutput firmware and SPIFFS were flashed and hash-verified on $Port."
} else {
    Write-Host "YoRadio $AudioOutput firmware was flashed and hash-verified on $Port; NVS and SPIFFS settings were preserved."
}
