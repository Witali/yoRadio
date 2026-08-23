[CmdletBinding()]
param(
    [string]$Port = "COM9",
    [string]$FixtureDirectory = "",
    [string]$DependencyRoot = "",
    [ValidateRange(12, 60)]
    [int]$TestSeconds = 18,
    [switch]$SkipRestore
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$project = Join-Path $repository "idf\esp32c3-oled-native"
$builder = Join-Path $PSScriptRoot "build.ps1"
$generator = Join-Path $PSScriptRoot "generate.ps1"
if ([string]::IsNullOrWhiteSpace($FixtureDirectory)) {
    $FixtureDirectory = Join-Path $repository ".build\codec-benchmark"
}
if ([string]::IsNullOrWhiteSpace($DependencyRoot)) {
    $DependencyRoot = Join-Path $repository ".idf"
}
$FixtureDirectory = [IO.Path]::GetFullPath($FixtureDirectory)
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$python = Join-Path $DependencyRoot "tools-v6.0.2\python_env\idf6.0_py3.12_env\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "ESP-IDF Python is missing; run .\setup.ps1 first"
}

$fixture = Join-Path $FixtureDirectory "mp3-320.mp3"
if (-not (Test-Path -LiteralPath $fixture -PathType Leaf)) {
    & $generator -OutputDirectory $FixtureDirectory -DurationSeconds 11
    if ($LASTEXITCODE -ne 0) { throw "Fixture generation failed" }
}
$fixtureSize = (Get-Item -LiteralPath $fixture).Length
if ($fixtureSize + 16 -gt 0x220000) {
    throw "MP3 fixture exceeds the codec_test partition"
}

$stagedFixture = Join-Path $FixtureDirectory "fixture-mp3-320.bin"
$stream = [IO.File]::Open($stagedFixture, [IO.FileMode]::Create,
                          [IO.FileAccess]::Write, [IO.FileShare]::None)
try {
    $writer = [IO.BinaryWriter]::new($stream)
    $writer.Write([uint32]0x59434658)
    $writer.Write([uint32]1)
    $writer.Write([uint32]$fixtureSize)
    $writer.Write([uint32]0)
    $writer.Flush()
    $input = [IO.File]::OpenRead($fixture)
    try { $input.CopyTo($stream) } finally { $input.Dispose() }
    $writer.Dispose()
} finally {
    $stream.Dispose()
}

$resultDirectory = Join-Path $FixtureDirectory "results\mp3-backends"
New-Item -ItemType Directory -Force -Path $resultDirectory | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)

function Invoke-Esptool {
    param([string[]]$EsptoolArguments)
    & $python -m esptool @EsptoolArguments
    if ($LASTEXITCODE -ne 0) {
        throw "esptool failed with exit code $LASTEXITCODE"
    }
}

function Receive-SerialLog {
    param([int]$Seconds)
    $serial = [System.IO.Ports.SerialPort]::new($Port, 115200)
    $serial.ReadTimeout = 200
    $serial.DtrEnable = $false
    $serial.RtsEnable = $false
    $serial.Open()
    $text = [Text.StringBuilder]::new()
    try {
        $end = [DateTime]::UtcNow.AddSeconds($Seconds)
        while ([DateTime]::UtcNow -lt $end) {
            Start-Sleep -Milliseconds 50
            [void]$text.Append($serial.ReadExisting())
        }
    } finally {
        $serial.Close()
        $serial.Dispose()
    }
    return $text.ToString()
}

function Match-Unsigned {
    param([Text.RegularExpressions.Match]$Match, [int]$Group)
    if (-not $Match.Success) { return $null }
    return [uint32]$Match.Groups[$Group].Value
}

$summary = @()
try {
foreach ($backend in @("espressif", "helix", "minimp3")) {
    Write-Host ""
    Write-Host "=== MP3 backend: $backend ==="
    $buildDirectory = "build-codec-benchmark-$backend"
    & $builder -BuildDirectory $buildDirectory -DependencyRoot $DependencyRoot -Mp3Decoder $backend
    if ($LASTEXITCODE -ne 0) { throw "$backend benchmark build failed" }

    $build = Join-Path $project $buildDirectory
    $app = Join-Path $build "yoradio_esp32c3_oled_native.bin"
    $benchmarkFlash = @(
        "--chip", "esp32c3", "-p", $Port, "-b", "460800",
        "--before", "default-reset", "--after", "no-reset",
        "write-flash", "--flash-mode", "dio", "--flash-size", "4MB",
        "--flash-freq", "80m",
        "0x0", (Join-Path $build "bootloader\bootloader.bin"),
        "0x8000", (Join-Path $build "partition_table\partition-table.bin"),
        "0x10000", $app
    )
    Invoke-Esptool $benchmarkFlash

    $fixtureFlash = @(
        "--chip", "esp32c3", "-p", $Port, "-b", "460800",
        "--before", "default-reset", "--after", "hard-reset",
        "write-flash", "--flash-mode", "dio", "--flash-size", "4MB",
        "--flash-freq", "80m", "0x190000", $stagedFixture
    )
    Invoke-Esptool $fixtureFlash
    Start-Sleep -Milliseconds 100

    $log = Receive-SerialLog $TestSeconds
    $clean = $log -replace "$([char]27)\[[0-9;]*[A-Za-z]", ""
    $logPath = Join-Path $resultDirectory "$backend.log"
    [IO.File]::WriteAllText($logPath, $clean, $utf8)

    $open = [regex]::Match(
        $clean,
        "MEM MP3 open: heap_before (\d+), heap_now (\d+), heap_delta (\d+), largest (\d+), minimum (\d+), codec_payload (\d+)")
    $first = [regex]::Match(
        $clean,
        "MEM MP3 first-frame: heap_before (\d+), heap_now (\d+), heap_delta (\d+), largest (\d+), minimum (\d+), codec_payload (\d+)")
    $perf = [regex]::Matches(
        $clean,
        "PERF MP3:.*?decode (\d+) ms \((\d+)\.(\d+)%.*, x(\d+)\.(\d+)\).*?max (\d+) us")
    if (-not $open.Success -or -not $first.Success -or $perf.Count -eq 0) {
        throw "Incomplete $backend metrics; inspect $logPath"
    }

    $cpuValues = @()
    $speedValues = @()
    $maxCalls = @()
    foreach ($item in $perf) {
        $cpuValues += [double]::Parse(
            "$($item.Groups[2].Value).$($item.Groups[3].Value)",
            [Globalization.CultureInfo]::InvariantCulture)
        $speedValues += [double]::Parse(
            "$($item.Groups[4].Value).$($item.Groups[5].Value)",
            [Globalization.CultureInfo]::InvariantCulture)
        $maxCalls += [uint32]$item.Groups[6].Value
    }
    $payload = Match-Unsigned $first 6
    $summary += [pscustomobject]@{
        Backend = $backend
        AppBytes = (Get-Item -LiteralPath $app).Length
        HeapBefore = Match-Unsigned $open 1
        HeapOpenDelta = Match-Unsigned $open 3
        HeapFirstFrameDelta = Match-Unsigned $first 3
        CodecPayload = if ($payload) { $payload } else { $null }
        LargestAfterOpen = Match-Unsigned $open 4
        MinimumFree = Match-Unsigned $first 5
        CpuPercent = [Math]::Round(
            ($cpuValues | Measure-Object -Average).Average, 1)
        RealtimeX = [Math]::Round(
            ($speedValues | Measure-Object -Average).Average, 2)
        MaxCallUs = ($maxCalls | Measure-Object -Maximum).Maximum
        PerfWindows = $perf.Count
        Log = $logPath
    }
    $perf | ForEach-Object { Write-Host $_.Value }
}

$csv = Join-Path $resultDirectory "summary.csv"
$summary | Export-Csv -LiteralPath $csv -NoTypeInformation -Encoding utf8
$summary | Format-Table Backend,AppBytes,HeapOpenDelta,HeapFirstFrameDelta,
    CodecPayload,LargestAfterOpen,MinimumFree,CpuPercent,RealtimeX,MaxCallUs
Write-Host "Results saved to $csv"

} finally {
if (-not $SkipRestore) {
    Write-Host ""
    Write-Host "=== Restoring normal Espressif firmware ==="
    $normalBuilder = Join-Path $project "build.ps1"
    $normalBuildDirectory = "build-normal-after-codec-benchmark"
    $normalSdkconfig = Join-Path $normalBuildDirectory "sdkconfig"
    $normalDefaults = @(
        "sdkconfig.defaults",
        (Join-Path $PSScriptRoot "sdkconfig.mp3-espressif.defaults")
    )
    & $normalBuilder -BuildDirectory $normalBuildDirectory -DependencyRoot $DependencyRoot -Sdkconfig $normalSdkconfig -SdkconfigDefaults $normalDefaults
    if ($LASTEXITCODE -ne 0) { throw "Normal firmware restore build failed" }
    $normal = Join-Path $project $normalBuildDirectory
    $normalApp = Join-Path $normal "yoradio_esp32c3_oled_native.bin"
    $restoreFlash = @(
        "--chip", "esp32c3", "-p", $Port, "-b", "460800",
        "--before", "default-reset", "--after", "hard-reset",
        "write-flash", "--flash-mode", "dio", "--flash-size", "4MB",
        "--flash-freq", "80m",
        "0x0", (Join-Path $normal "bootloader\bootloader.bin"),
        "0x8000", (Join-Path $normal "partition_table\partition-table.bin"),
        "0xe000", (Join-Path $normal "ota_data_initial.bin"),
        "0x10000", $normalApp,
        "0x1e0000", $normalApp
    )
    Invoke-Esptool $restoreFlash
    Write-Host "Normal firmware restored; SPIFFS and NVS were preserved."
}
}
