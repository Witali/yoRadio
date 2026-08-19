[CmdletBinding()]
param(
    [string]$ArduinoCli
)

# Optional legacy Arduino build setup. The repository default is native ESP-IDF.

$ErrorActionPreference = "Stop"
$arduinoCliVersion = "1.5.1"
$arduinoCliArchiveSha256 = "FABE42E0EB04D00E776A66178299FF95A46C623DBC260F997E58FD514853DD40"
$esp32CoreVersion = "3.3.8"
$esp32IndexUrl = "https://espressif.github.io/arduino-esp32/package_esp32_index.json"
$repository = [IO.Path]::GetFullPath($PSScriptRoot)

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

function Resolve-ArduinoCli {
    param([string]$ExplicitPath, [string]$LocalPath)

    if ($ExplicitPath) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "Arduino CLI was not found at $ExplicitPath"
        }
        return [IO.Path]::GetFullPath($ExplicitPath)
    }

    $command = Get-Command arduino-cli -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) { return $command.Source }
    if (Test-Path -LiteralPath $LocalPath -PathType Leaf) { return $LocalPath }
    return $null
}

$sharedRoot = Resolve-SharedRepositoryRoot
$localCliDirectory = Join-Path $sharedRoot "local_tools\arduino-cli"
$localCli = Join-Path $localCliDirectory "arduino-cli.exe"
$resolvedArduinoCli = Resolve-ArduinoCli $ArduinoCli $localCli

if (-not $resolvedArduinoCli) {
    $runningOnWindows = [Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [Runtime.InteropServices.OSPlatform]::Windows)
    if (-not $runningOnWindows -or -not [Environment]::Is64BitOperatingSystem) {
        throw "Automatic Arduino CLI installation currently supports 64-bit Windows. Install arduino-cli and rerun setup.ps1."
    }

    $downloadDirectory = Join-Path $sharedRoot ".build\downloads"
    $archive = Join-Path $downloadDirectory "arduino-cli_$arduinoCliVersion`_Windows_64bit.zip"
    $downloadUrl = "https://github.com/arduino/arduino-cli/releases/download/v$arduinoCliVersion/arduino-cli_$arduinoCliVersion`_Windows_64bit.zip"
    New-Item -ItemType Directory -Force -Path $downloadDirectory, $localCliDirectory | Out-Null

    Write-Host "Arduino CLI was not found in PATH; downloading version $arduinoCliVersion..."
    Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $archive
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
    if ($actualHash -ne $arduinoCliArchiveSha256) {
        throw "Arduino CLI archive checksum mismatch: expected $arduinoCliArchiveSha256, got $actualHash"
    }
    Expand-Archive -LiteralPath $archive -DestinationPath $localCliDirectory -Force
    if (-not (Test-Path -LiteralPath $localCli -PathType Leaf)) {
        throw "Arduino CLI archive did not contain arduino-cli.exe"
    }
    $resolvedArduinoCli = $localCli
} else {
    Write-Host "Using existing Arduino CLI: $resolvedArduinoCli"
}

$arduinoRoot = Join-Path $sharedRoot ".build\arduino"
$dataDirectory = Join-Path $arduinoRoot "data"
$downloadsDirectory = Join-Path $arduinoRoot "downloads"
$userDirectory = Join-Path $arduinoRoot "user"
$configPath = Join-Path $sharedRoot ".build\arduino-cli.yaml"
New-Item -ItemType Directory -Force -Path @(
    $dataDirectory,
    $downloadsDirectory,
    $userDirectory
) | Out-Null

function ConvertTo-YamlPath {
    param([string]$Path)
    return ([IO.Path]::GetFullPath($Path) -replace '\\', '/')
}

$config = @"
board_manager:
  additional_urls:
    - $esp32IndexUrl
directories:
  data: '$(ConvertTo-YamlPath $dataDirectory)'
  downloads: '$(ConvertTo-YamlPath $downloadsDirectory)'
  user: '$(ConvertTo-YamlPath $userDirectory)'
metrics:
  enabled: false
updater:
  enable_notification: false
"@
Set-Content -LiteralPath $configPath -Value $config -Encoding utf8

Write-Host "Installing ESP32 core $esp32CoreVersion into the repository toolchain..."
& $resolvedArduinoCli --config-file $configPath core update-index
if ($LASTEXITCODE -ne 0) { throw "Arduino core index update failed with exit code $LASTEXITCODE" }
& $resolvedArduinoCli --config-file $configPath core install "esp32:esp32@$esp32CoreVersion"
if ($LASTEXITCODE -ne 0) { throw "ESP32 core installation failed with exit code $LASTEXITCODE" }

& $resolvedArduinoCli --config-file $configPath lib update-index
if ($LASTEXITCODE -ne 0) { throw "Arduino library index update failed with exit code $LASTEXITCODE" }

$libraries = @(
    "Adafruit BusIO@1.17.4",
    "Adafruit GFX Library@1.12.6",
    "Adafruit ST7735 and ST7789 Library@1.11.0",
    "RTClib@2.1.4",
    "XPT2046_Touchscreen@1.4.0"
)
foreach ($library in $libraries) {
    Write-Host "Installing $library..."
    & $resolvedArduinoCli --config-file $configPath lib install --no-deps $library
    if ($LASTEXITCODE -ne 0) {
        throw "Arduino library installation failed for $library with exit code $LASTEXITCODE"
    }
}

Write-Host "ESP32-C3 OLED toolchain is ready."
Write-Host "  Arduino CLI: $resolvedArduinoCli"
Write-Host "  Configuration: $configPath"
Write-Host "  ESP32 core: $esp32CoreVersion"
