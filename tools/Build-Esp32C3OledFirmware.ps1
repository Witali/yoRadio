[CmdletBinding()]
param(
    [string]$ArduinoCli,
    [string]$Libraries,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$sketch = Join-Path $repository "yoRadio"
$fqbn = "esp32:esp32:esp32c3:FlashSize=4M,PartitionScheme=min_spiffs,CDCOnBoot=cdc"

function Resolve-ArduinoCli {
    param([string]$ExplicitPath)

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "Arduino CLI was not found at $ExplicitPath"
        }
        return [IO.Path]::GetFullPath($ExplicitPath)
    }

    $command = Get-Command arduino-cli -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) { return $command.Source }

    $candidate = Join-Path $sharedRoot "local_tools\arduino-cli\arduino-cli.exe"
    if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    return $null
}

function Resolve-SharedRepositoryRoot {
    $commonDir = (& git -C $repository rev-parse --git-common-dir 2>$null)
    if ($LASTEXITCODE -ne 0 -or -not $commonDir) { return $repository }
    $absoluteCommonDir = if ([IO.Path]::IsPathRooted($commonDir)) {
        [IO.Path]::GetFullPath($commonDir)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repository $commonDir))
    }
    return Split-Path -Parent $absoluteCommonDir
}

$sharedRoot = Resolve-SharedRepositoryRoot
$setupScript = Join-Path $repository "tools\Setup-Esp32C3OledArduino.ps1"
$resolvedArduinoCli = Resolve-ArduinoCli $ArduinoCli
$configPath = Join-Path $sharedRoot ".build\arduino-cli.yaml"
$coreDirectory = Join-Path $sharedRoot ".build\arduino\data\packages\esp32\hardware\esp32\3.3.8"
$defaultLibraries = Join-Path $sharedRoot ".build\arduino\user\libraries"
$requiredLibraryDirectories = @(
    "Adafruit_BusIO",
    "Adafruit_GFX_Library",
    "Adafruit_ST7735_and_ST7789_Library",
    "RTClib",
    "XPT2046_Touchscreen"
)
$librariesReady = @($requiredLibraryDirectories | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $defaultLibraries $_) -PathType Container)
}).Count -eq 0

$toolchainReady = $resolvedArduinoCli -and
    (Test-Path -LiteralPath $configPath -PathType Leaf) -and
    (Test-Path -LiteralPath $coreDirectory -PathType Container) -and
    $librariesReady
if (-not $toolchainReady) {
    Write-Host "Preparing the repository-local ESP32-C3 toolchain..."
    $setupArguments = @()
    if ($resolvedArduinoCli) { $setupArguments += @("-ArduinoCli", $resolvedArduinoCli) }
    & $setupScript @setupArguments
    if ($LASTEXITCODE -ne 0) { throw "Toolchain setup failed with exit code $LASTEXITCODE" }
    $resolvedArduinoCli = Resolve-ArduinoCli $ArduinoCli
}
if (-not $resolvedArduinoCli) { throw "Arduino CLI setup did not produce a usable executable" }

$buildDirectory = Join-Path $sharedRoot ".build\esp32c3-oled-042"
$localLibraries = if ($Libraries) {
    [IO.Path]::GetFullPath($Libraries)
} else {
    $defaultLibraries
}
if (-not (Test-Path -LiteralPath $localLibraries -PathType Container)) {
    throw "Local Arduino libraries were not found at $localLibraries"
}

$fontSource = Join-Path $sketch "fonts\glcdfont.c"
$fontDestination = Join-Path $localLibraries "Adafruit_GFX_Library\glcdfont.c"
if (-not (Test-Path -LiteralPath $fontDestination -PathType Leaf)) {
    throw "Adafruit GFX was not found at $fontDestination"
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $fontSource).Hash -ne
    (Get-FileHash -Algorithm SHA256 -LiteralPath $fontDestination).Hash) {
    Copy-Item -LiteralPath $fontSource -Destination $fontDestination -Force
}

$arguments = @("compile")
if ($Clean) { $arguments += "--clean" }
$arguments += @(
    "--fqbn", $fqbn,
    "--build-path", $buildDirectory,
    "--libraries", $localLibraries,
    "--build-property", "compiler.optimization_flags=-O3",
    "--build-property", "compiler.c.extra_flags=-DYORADIO_BOARD_ESP32C3_OLED_042=1",
    "--build-property", "compiler.cpp.extra_flags=-DYORADIO_BOARD_ESP32C3_OLED_042=1",
    $sketch
)

& $resolvedArduinoCli --config-file $configPath @arguments
if ($LASTEXITCODE -ne 0) { throw "ESP32-C3 build failed with exit code $LASTEXITCODE" }

Write-Host "ESP32-C3 OLED firmware built successfully:"
Write-Host "  Application: $(Join-Path $buildDirectory 'yoRadio.ino.bin')"
Write-Host "  Bootloader:  $(Join-Path $buildDirectory 'yoRadio.ino.bootloader.bin')"
Write-Host "  Partitions:  $(Join-Path $buildDirectory 'yoRadio.ino.partitions.bin')"
