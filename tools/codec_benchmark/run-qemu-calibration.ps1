[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$BuildDirectory = "build-qemu-aac",
    [string]$DependencyRoot = "",
    [string]$QemuExecutable = $env:YORADIO_QEMU_RISCV32,
    [string]$QemuBiosDirectory = $env:YORADIO_QEMU_BIOS,
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "../.."))
if (-not $DependencyRoot) { $DependencyRoot = Join-Path $repo ".idf" }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repo ".build/qemu-codec-calibration" }
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
$python = Join-Path $DependencyRoot "tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "ESP-IDF Python is unavailable: $python" }
$project = Join-Path $repo "idf/esp32c3-oled-native"
$log = Join-Path (Join-Path $project $BuildDirectory) "qemu-smoke.log"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$arguments = @{
    SkipBuild = $true; BuildDirectory = $BuildDirectory; DependencyRoot = $DependencyRoot
    QemuExecutable = $QemuExecutable; QemuBiosDirectory = $QemuBiosDirectory
}

# The firmware must already be built with the AAC test + instruction profile.
# Each run creates a disposable flash image; no physical board is accessed.
foreach ($codec in @("mp3", "flac", "vorbis", "opus")) {
    & (Join-Path $project "run-qemu.ps1") @arguments -CodecCalibration $codec
    Copy-Item -LiteralPath $log -Destination (Join-Path $OutputDirectory "qemu-$codec.log")
}
& (Join-Path $project "run-qemu.ps1") @arguments
$aacLog = Join-Path $OutputDirectory "qemu.log"
Copy-Item -LiteralPath $log -Destination $aacLog
$aacProfile = Join-Path $OutputDirectory "esp32c3-aac-160mhz.json"
& $python -X utf8 (Join-Path $PSScriptRoot "calibrate_qemu_aac.py") $aacLog --output $aacProfile
if ($LASTEXITCODE -ne 0) { throw "AAC calibration failed" }
& $python -X utf8 (Join-Path $PSScriptRoot "calibrate_qemu_codecs.py") `
    --logs $OutputDirectory --aac-calibration $aacProfile `
    --output (Join-Path $OutputDirectory "esp32c3-codecs-160mhz.json")
if ($LASTEXITCODE -ne 0) { throw "Codec calibration failed" }
& $python -X utf8 (Join-Path $PSScriptRoot "summarize_qemu_aac.py") $aacLog `
    --calibration $aacProfile --output (Join-Path $OutputDirectory "estimated-aac.json")
if ($LASTEXITCODE -ne 0) { throw "AAC estimate failed" }
Write-Host "Saved emulator-only calibration suite: $OutputDirectory"
