param(
    [string[]]$Variants = @('original', 'limit', 'unroll4', 'unroll8', 'unroll32', 'mask8', 'branchless8'),
    [int]$Repeats = 1,
    [string]$Port = 'COM8',
    [string]$ResultDirectory = '.build/rcpdm-speed-results/matrix',
    [string]$RestoreImage = 'firmware/development/esp8266-native-aac-speed/app.bin'
)
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $radioRoot
try {
    $python = "$radioRoot/.build/esp8266-python/Scripts/python.exe"
    $esptool = "$radioRoot/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py"
    $restore = (Resolve-Path $RestoreImage).Path
    $env:PYTHONIOENCODING = 'utf-8'
    New-Item -ItemType Directory -Path $ResultDirectory -Force | Out-Null
    foreach ($variant in $Variants) {
        if ($variant -notmatch '^[a-z0-9-]+$' -or -not (Test-Path "firmware/development/esp8266-rcpdm-speed/$variant/app.bin")) { throw "Missing variant $variant" }
    }
    function Install-App([string]$Binary, [string]$Log) {
        & $python $esptool --chip esp8266 --port $Port --baud 460800 --before default_reset --after no_reset write_flash --flash_mode keep --flash_size 4MB --flash_freq keep 0x10000 $Binary *> $Log
        if ($LASTEXITCODE) { throw "Flash failed: $Log" }
    }
    try {
        for ($round = 1; $round -le $Repeats; ++$round) {
            foreach ($variant in $Variants) {
                $prefix = Join-Path $ResultDirectory "round-$round-$variant"
                $binary = "firmware/development/esp8266-rcpdm-speed/$variant/app.bin"
                Write-Output "Testing round $round : $variant"
                Get-FileHash $binary | Format-List | Out-File "$prefix-sha256.log"
                Install-App $binary "$prefix-flash.log"
                # RTS reset and TX capture only: GPIO3 is audio, never transmit UART commands.
                & $python tools/monitor_esp8266.py --port $Port --reset --seconds 25 *> "$prefix-uart.log"
                if ($LASTEXITCODE) { throw "Capture failed: $prefix" }
                $capture = Get-Content "$prefix-uart.log"
                $capture | Where-Object { $_ -match 'RCPDM bit-exact|audio_output_bench:' }
                if (-not ($capture -match 'bit-exact PASS: 493216') -or -not ($capture -match 'audio_output_bench: complete')) { throw "Incomplete/exactness failure: $prefix" }
                if ($capture -match 'invalid=[1-9]|PCM write failed|bit-exact FAIL|stalled producer.*FAIL') { throw "Invalid measurement: $prefix" }
            }
        }
    } finally {
        Write-Output 'Restoring ordinary PDM32 radio'
        Install-App $restore (Join-Path $ResultDirectory 'restore-flash.log')
        & $python tools/monitor_esp8266.py --port $Port --reset --seconds 50 *> (Join-Path $ResultDirectory 'restore-uart.log')
        if ($LASTEXITCODE) { throw 'Restore boot capture failed' }
    }
} finally { Pop-Location }
