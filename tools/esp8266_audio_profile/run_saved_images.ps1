param(
    [Parameter(Mandatory=$true)][string[]]$Images,
    [string]$Port = 'COM8',
    [int]$Repeats = 2,
    [string]$ResultDirectory = '.build/aac-speed/ab',
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $radioRoot
try {
    $python = Join-Path $radioRoot '.build/esp8266-python/Scripts/python.exe'
    $esptool = Join-Path (Resolve-Path $SdkPath).Path 'components/esptool_py/esptool/esptool.py'
    $env:PYTHONIOENCODING = 'utf-8'
    $resolved = @($Images | ForEach-Object { (Resolve-Path $_).Path })
    New-Item -ItemType Directory -Path $ResultDirectory -Force | Out-Null
    for ($round = 1; $round -le $Repeats; ++$round) {
        for ($index = 0; $index -lt $resolved.Count; ++$index) {
            $binary = $resolved[$index]
            $prefix = Join-Path $ResultDirectory "round-$round-image-$index"
            Write-Output "Round $round image $index : $binary"
            Get-FileHash -LiteralPath $binary -Algorithm SHA256 | Format-List | Out-File "$prefix-sha256.log"
            & $python $esptool --chip esp8266 --port $Port --baud 460800 --before default_reset --after no_reset write_flash --flash_mode keep --flash_size 4MB --flash_freq keep 0x10000 $binary *> "$prefix-flash.log"
            if ($LASTEXITCODE) { throw "Flash failed: $prefix-flash.log" }
            # Never transmit UART application bytes: GPIO3 is I2S data output.
            & $python tools/monitor_esp8266.py --port $Port --reset --seconds 12 *> "$prefix-uart.log"
            if ($LASTEXITCODE) { throw "Capture failed: $prefix-uart.log" }
            $capture = Get-Content -LiteralPath "$prefix-uart.log"
            $capture | Where-Object { $_ -match 'codec_ram:.*(RAM frame|physical wall|stack free|lifecycle)' }
            if (-not ($capture -match 'codec_ram: complete')) { throw "Incomplete benchmark: $prefix-uart.log" }
            if (-not ($capture -match 'lifecycle .*delta=0')) { throw "Lifecycle leak: $prefix-uart.log" }
        }
    }
    Write-Output 'Diagnostic image remains installed. Restore ordinary radio firmware.'
} finally { Pop-Location }
