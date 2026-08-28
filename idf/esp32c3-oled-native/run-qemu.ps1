[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$QemuExecutable = $env:YORADIO_QEMU_RISCV32,
    [string]$QemuBiosDirectory = $env:YORADIO_QEMU_BIOS,
    [string]$BuildDirectory = "build-qemu",
    [string]$DependencyRoot = "",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$project = $PSScriptRoot
$worktreeRoot = [IO.Path]::GetFullPath((Join-Path $project "..\.."))
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $DependencyRoot = Join-Path $worktreeRoot ".idf"
}
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$buildPath = [IO.Path]::GetFullPath((Join-Path $project $BuildDirectory))

if (-not $SkipBuild) {
    & (Join-Path $project "build-qemu.ps1") `
        -BuildDirectory $BuildDirectory `
        -Sdkconfig (Join-Path $BuildDirectory "sdkconfig") `
        -DependencyRoot $DependencyRoot
    if ($LASTEXITCODE -ne 0) { throw "QEMU firmware build failed" }
}

if ([string]::IsNullOrWhiteSpace($QemuExecutable)) {
    $command = Get-Command qemu-system-riscv32.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) { $QemuExecutable = $command.Source }
}
if ([string]::IsNullOrWhiteSpace($QemuExecutable) -or
    -not (Test-Path -LiteralPath $QemuExecutable -PathType Leaf)) {
    throw "Set -QemuExecutable or YORADIO_QEMU_RISCV32 to qemu-system-riscv32.exe"
}
$QemuExecutable = [IO.Path]::GetFullPath($QemuExecutable)

if ([string]::IsNullOrWhiteSpace($QemuBiosDirectory)) {
    $candidate = [IO.Path]::GetFullPath((Join-Path (
        Split-Path -Parent $QemuExecutable) "..\pc-bios"))
    if (Test-Path -LiteralPath $candidate -PathType Container) {
        $QemuBiosDirectory = $candidate
    }
}

$esptool = Join-Path $DependencyRoot `
    "tools-v6.0.2\python_env\idf6.0_py3.12_env\Scripts\esptool.exe"
if (-not (Test-Path -LiteralPath $esptool -PathType Leaf)) {
    throw "esptool is unavailable under $DependencyRoot; run setup.ps1 first"
}

$flashImage = Join-Path $buildPath "qemu-flash.bin"
& $esptool --chip esp32c3 merge-bin -o $flashImage `
    --flash-mode dio --flash-freq 80m --flash-size 4MB `
    0x0 (Join-Path $buildPath "bootloader\bootloader.bin") `
    0x8000 (Join-Path $buildPath "partition_table\partition-table.bin") `
    0xe000 (Join-Path $buildPath "ota_data_initial.bin") `
    0x10000 (Join-Path $buildPath "yoradio_esp32c3_oled_native.bin") `
    0x3b0000 (Join-Path $buildPath "spiffs.bin") `
    --pad-to-size 4MB
if ($LASTEXITCODE -ne 0) { throw "QEMU flash image merge failed" }

$qemuArguments = @("-M", "esp32c3", "-nographic", "-no-reboot", "-snapshot")
if (-not [string]::IsNullOrWhiteSpace($QemuBiosDirectory)) {
    $qemuArguments += @("-L", [IO.Path]::GetFullPath($QemuBiosDirectory))
}
$qemuArguments += @(
    "-drive", "file=$flashImage,if=mtd,format=raw"
)

$log = Join-Path $buildPath "qemu-smoke.log"
$output = @(& $QemuExecutable @qemuArguments 2>&1 |
    Tee-Object -FilePath $log)
$qemuExitCode = $LASTEXITCODE
$joinedOutput = $output -join "`n"
if ($qemuExitCode -ne 0 -or $joinedOutput -notmatch "QEMU_SMOKE_PASS") {
    throw "QEMU smoke test failed (exit $qemuExitCode); see $log"
}

Write-Host "QEMU smoke test passed; log: $log"
