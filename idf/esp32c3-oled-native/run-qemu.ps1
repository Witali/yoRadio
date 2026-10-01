[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$QemuExecutable = $env:YORADIO_QEMU_RISCV32,
    [string]$QemuBiosDirectory = $env:YORADIO_QEMU_BIOS,
    [string]$AudioOutput = "",
    [string]$BuildDirectory = "build-qemu",
    [string]$DependencyRoot = "",
    [ValidateSet("mp3", "flac", "vorbis", "opus")]
    [string]$CodecCalibration = "",
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
if ([string]::IsNullOrWhiteSpace($AudioOutput)) {
    $AudioOutput = Join-Path $buildPath "qemu-audio.wav"
}
$AudioOutput = [IO.Path]::GetFullPath($AudioOutput)

if (-not $SkipBuild) {
    & (Join-Path $project "build-qemu.ps1") `
        -BuildDirectory $BuildDirectory `
        -Sdkconfig (Join-Path $BuildDirectory "sdkconfig") `
        -DependencyRoot $DependencyRoot
    if ($LASTEXITCODE -ne 0) { throw "QEMU firmware build failed" }
}

$builtConfig = Get-Content -LiteralPath (Join-Path $buildPath "config/sdkconfig.h") -Raw
$instructionProfile = $builtConfig -match '#define CONFIG_YORADIO_QEMU_AAC_PROFILE 1'
$cacheProfile = $builtConfig -match '#define CONFIG_YORADIO_QEMU_CACHE_TEST 1'
$packedHistoryProfile = $builtConfig -match '#define CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST 1'
$bfp16Profile = $builtConfig -match '#define CONFIG_YORADIO_QEMU_AAC_BFP16_TEST 1'
if ($CodecCalibration -and -not $instructionProfile) {
    throw "Codec calibration requires CONFIG_YORADIO_QEMU_AAC_PROFILE=y"
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

if ($CodecCalibration) {
    $fixtureRoot = Join-Path $worktreeRoot "tests/fixtures/esp32c3_calibration"
    $manifest = Get-Content -LiteralPath (Join-Path $fixtureRoot "manifest.json") -Raw | ConvertFrom-Json
    $entry = $manifest.fixtures | Where-Object { $_.codec -eq $CodecCalibration }
    if (@($entry).Count -ne 1) { throw "Missing calibration fixture: $CodecCalibration" }
    $fixturePath = Join-Path $fixtureRoot $entry.file
    $fixture = [IO.File]::ReadAllBytes($fixturePath)
    if ($fixture.Length -ne $entry.bytes -or $fixture.Length -gt (0x1d0000 - 16) -or
        (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash -ne $entry.sha256) {
        throw "Calibration fixture size/hash mismatch: $CodecCalibration"
    }
    # Only modify the disposable QEMU image. No flashing or device I/O.
    $stream = [IO.File]::Open($flashImage, [IO.FileMode]::Open, [IO.FileAccess]::Write)
    try {
        $stream.Position = 0x1e0000
        foreach ($value in @(0x5143414c, $entry.id, $fixture.Length, 0)) {
            $bytes = [BitConverter]::GetBytes([uint32]$value)
            $stream.Write($bytes, 0, 4)
        }
        $stream.Write($fixture, 0, $fixture.Length)
    } finally { $stream.Dispose() }
}

if (Test-Path -LiteralPath $AudioOutput -PathType Leaf) {
    Remove-Item -LiteralPath $AudioOutput -Force
}
$qemuArguments = @(
    "-M", "esp32c3,audiodev=audio0",
    "-nographic", "-no-reboot", "-snapshot",
    "-audiodev", "wav,id=audio0,path=$AudioOutput,out.frequency=48000"
)
if ($instructionProfile -or $cacheProfile -or $bfp16Profile -or $packedHistoryProfile) {
    $qemuArguments += @("-icount", "shift=0,align=off,sleep=off")
}
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
if ($joinedOutput -notmatch "QEMU_OLED_PASS" -or
    $joinedOutput -notmatch "QEMU_AUDIO_PASS" -or
    -not (Test-Path -LiteralPath $AudioOutput -PathType Leaf) -or
    (Get-Item -LiteralPath $AudioOutput).Length -le 44) {
    throw "QEMU OLED/audio validation failed; see $log"
}

if (-not $cacheProfile -and $builtConfig -match '#define CONFIG_YORADIO_QEMU_AAC_TEST 1' -and
    $joinedOutput -notmatch 'QEMU_AAC_FORMAT_PASS') {
    throw "QEMU AAC validation failed; see $log"
}
if ($instructionProfile -and $joinedOutput -notmatch 'QEMU_AAC_WORK_PASS') {
    throw "QEMU AAC instruction profiling failed; see $log"
}
if ($bfp16Profile -and $joinedOutput -notmatch 'BFP16_EXPERIMENT_COMPLETE') {
    throw "QEMU BFP16 experiment incomplete; see $log"
}
if ($bfp16Profile -and $joinedOutput -match 'precision=FAIL') {
    Write-Warning "BFP16 exceeds the one-LSB PCM limit; see BFP16_RESULT in $log"
}
if ($instructionProfile -and $joinedOutput -notmatch 'QEMU_AAC_CAL_PASS') {
    throw "QEMU AAC hardware calibration fixture failed; see $log"
}
if ($CodecCalibration -and $joinedOutput -notmatch "QEMU_CODEC_CAL_PASS codec=$CodecCalibration") {
    throw "QEMU $CodecCalibration calibration failed; see $log"
}
if ($cacheProfile -and $joinedOutput -notmatch 'QEMU_CACHE_PASS') {
    throw "QEMU cache trace fixture failed; see $log"
}
if ($packedHistoryProfile -and $joinedOutput -notmatch 'PCX14_EXPERIMENT_COMPLETE') {
    throw "QEMU packed history experiment incomplete; see $log"
}
if ($packedHistoryProfile -and $joinedOutput -match 'precision=FAIL') {
    Write-Warning "Packed history exceeds its development PCM limit; see PCX14_LIMIT and PCX14_RESULT in $log"
}
Write-Host "QEMU smoke test passed; log: $log; audio: $AudioOutput"
