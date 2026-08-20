[CmdletBinding()]
param(
    [string]$Port = "COM9",
    [string]$BoardUrl = "http://192.168.100.4",
    [string]$FixtureDirectory = "",
    [ValidateRange(8, 30)]
    [int]$TestSeconds = 14
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if ([string]::IsNullOrWhiteSpace($FixtureDirectory)) {
    $FixtureDirectory = Join-Path $repository ".build\codec-benchmark"
}
$FixtureDirectory = [IO.Path]::GetFullPath($FixtureDirectory)
$python = Join-Path $repository ".idf\tools-v6.0.2\python_env\idf6.0_py3.12_env\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "ESP-IDF Python is missing; run .\setup.ps1 first"
}

$fixtures = @(
    @{ Name = "MP3 320"; Codec = "mp3"; File = "mp3-320.mp3" }
    @{ Name = "AAC-LC 320"; Codec = "aac"; File = "aac-lc-320.aac" }
    @{ Name = "FLAC level 8"; Codec = "flac"; File = "flac-level8.flac" }
    @{ Name = "Vorbis q10"; Codec = "ogg"; File = "vorbis-q10.ogg" }
    @{ Name = "Opus 510"; Codec = "ogg"; File = "opus-510.ogg" }
)
$resultDirectory = Join-Path $FixtureDirectory "results"
New-Item -ItemType Directory -Force -Path $resultDirectory | Out-Null

foreach ($fixture in $fixtures) {
    $file = Join-Path $FixtureDirectory $fixture.File
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Missing fixture: $file"
    }
    $size = (Get-Item -LiteralPath $file).Length
    if ($size -gt 0x240000) {
        throw "$($fixture.File) exceeds the 0x240000-byte codec_test partition"
    }

    Write-Host "Writing $($fixture.Name) to codec_test flash"
    & $python -m esptool --chip esp32c3 -p $Port -b 460800 `
        --before default-reset --after hard-reset write-flash `
        --flash-mode dio --flash-size 4MB --flash-freq 80m `
        0x190000 $file
    if ($LASTEXITCODE -ne 0) { throw "Fixture flash failed" }

    $deadline = [DateTime]::UtcNow.AddSeconds(25)
    do {
        Start-Sleep -Milliseconds 500
        try {
            $status = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 `
                -Uri "$BoardUrl/api/native/status"
        } catch {
            $status = $null
        }
    } until ($status -or [DateTime]::UtcNow -ge $deadline)
    if (-not $status) { throw "Board did not return after flashing fixture" }

    $serial = [System.IO.Ports.SerialPort]::new($Port, 115200)
    $serial.ReadTimeout = 200
    $serial.DtrEnable = $false
    $serial.RtsEnable = $false
    $serial.Open()
    try {
        $serial.DiscardInBuffer()
        Invoke-WebRequest -UseBasicParsing -Method Post `
            -Uri "$BoardUrl/api/native/benchmark?codec=$($fixture.Codec)&size=$size" | Out-Null
        $end = [DateTime]::UtcNow.AddSeconds($TestSeconds)
        $log = ""
        while ([DateTime]::UtcNow -lt $end) {
            Start-Sleep -Milliseconds 100
            $log += $serial.ReadExisting()
        }
    } finally {
        $serial.Close()
        $serial.Dispose()
    }
    $clean = $log -replace "`e\[[0-9;]*[A-Za-z]", ""
    $path = Join-Path $resultDirectory ($fixture.File + ".log")
    Set-Content -LiteralPath $path -Encoding utf8 -Value $clean
    $perf = @($clean -split "`r?`n" | Where-Object { $_ -match "PERF " })
    if (-not $perf.Count) {
        Write-Warning "No PERF line captured for $($fixture.Name)"
    } else {
        $perf | ForEach-Object { Write-Host $_ }
    }
}

