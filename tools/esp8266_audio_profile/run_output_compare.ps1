param(
    [string]$Port = 'COM8',
    [int]$Repeats = 2,
    [Parameter(Mandatory=$true)][string]$RestoreImage,
    [string]$ResultDirectory = '.build/output-compare-results/ab',
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
# Writes app0 only; preserves bootloader, partition table, NVS and SPIFFS.
# Runtime test settings are never persisted. No application UART RX commands.
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $radioRoot
try {
    $python = Join-Path $radioRoot '.build/esp8266-python/Scripts/python.exe'
    $esptool = Join-Path (Resolve-Path $SdkPath).Path 'components/esptool_py/esptool/esptool.py'
    $restore = (Resolve-Path $RestoreImage).Path
    $env:PYTHONIOENCODING = 'utf-8'
    $images = @('pdm', 'rcpdm') | ForEach-Object {
        (Resolve-Path "firmware/development/esp8266-output-compare-$_/app.bin").Path
    }
    New-Item -ItemType Directory -Path $ResultDirectory -Force | Out-Null
    function Install-App([string]$Binary, [string]$Log) {
        & $python $esptool --chip esp8266 --port $Port --baud 460800 --before default_reset --after no_reset write_flash --flash_mode keep --flash_size 4MB --flash_freq keep 0x10000 $Binary *> $Log
        if ($LASTEXITCODE) { throw "Flash failed: $Log" }
    }
    try {
        for ($round = 1; $round -le $Repeats; ++$round) {
            for ($index = 0; $index -lt $images.Count; ++$index) {
                $mode = @('pdm', 'rcpdm')[$index]
                $prefix = Join-Path $ResultDirectory "round-$round-$mode"
                Write-Output "Round $round : $mode"
                Get-FileHash -LiteralPath $images[$index] -Algorithm SHA256 | Format-List | Out-File "$prefix-sha256.log"
                Install-App $images[$index] "$prefix-flash.log"
                & $python tools/monitor_esp8266.py --port $Port --reset --seconds 20 *> "$prefix-uart.log"
                if ($LASTEXITCODE) { throw "Capture failed: $prefix-uart.log" }
                $capture = Get-Content -LiteralPath "$prefix-uart.log"
                $capture | Where-Object { $_ -match 'audio_output_bench:' }
                if (-not ($capture -match 'audio_output_bench: complete')) { throw "Incomplete benchmark: $prefix-uart.log" }
                if ($capture -match '(invalid=[1-9]|PCM write failed|stalled producer.*FAIL)') { throw "Invalid output benchmark: $prefix-uart.log" }
            }
        }
    } finally {
        Write-Output "Restoring ordinary firmware: $restore"
        Install-App $restore (Join-Path $ResultDirectory 'restore-flash.log')
        & $python tools/monitor_esp8266.py --port $Port --reset --seconds 50 *> (Join-Path $ResultDirectory 'restore-uart.log')
        if ($LASTEXITCODE) { throw 'Ordinary firmware boot capture failed' }
        Write-Output 'Ordinary firmware restored; inspect restore-uart.log for boot/network status.'
    }
} finally { Pop-Location }
