param(
    [string]$Port = 'COM8',
    [ValidateSet('full', '32', '64', '128', '256', '512')]
    [string[]]$Cases = @('full', '32', '64', '128', '256', '512'),
    [switch]$PhysicalOutput,
    [string]$BuildDirectory = '.build/esp8266-pcm32-dma-profile',
    [string]$ResultDirectory = '.build/esp8266-aac-blocks/results',
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $radioRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = Join-Path $radioRoot '.build/esp8266-tools'
    $env:PYTHONIOENCODING = 'utf-8'
    $radioOldPath = $env:PATH
    $env:PATH = "$radioRoot/.build/esp8266-python/Scripts;$radioRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$radioRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin;$radioRoot/.build/esp8266-tools/tools/ninja/1.9.0;$env:PATH"
    $python = Join-Path $radioRoot '.build/esp8266-python/Scripts/python.exe'
    $cmake = Join-Path $radioRoot '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe'
    $ninja = Join-Path $radioRoot '.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe'
    New-Item -ItemType Directory -Path $ResultDirectory -Force | Out-Null
    $mode = if ($PhysicalOutput) { 'output' } else { 'decode' }
    foreach ($case in $Cases) {
        $caseName = "$mode-$case"
        $prefix = Join-Path $ResultDirectory $caseName
        $blockOn = if ($case -eq 'full') { 'OFF' } else { 'ON' }
        $frames = if ($case -eq 'full') { '128' } else { $case }
        $outputOn = if ($PhysicalOutput) { 'ON' } else { 'OFF' }
        Write-Output "Building AAC $caseName"
        & $cmake -S esp8266/rtos-sdk-native -B $BuildDirectory -G Ninja `
            -DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=ON "-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=$outputOn" `
            -DYORADIO_ESP8266_AUDIO_PROFILE=OFF -DYORADIO_ESP8266_AUDIO_TRACE=OFF `
            -DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=OFF -DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF `
            "-DYORADIO_ESP8266_AAC_BLOCK_OUTPUT=$blockOn" "-DYORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=$frames" *> "$prefix-configure.log"
        if ($LASTEXITCODE) { throw "Configure failed: $prefix-configure.log" }
        & $ninja -C $BuildDirectory *> "$prefix-build.log"
        if ($LASTEXITCODE) { throw "Build failed: $prefix-build.log" }
        $artifact = "firmware/development/esp8266-native-aac-$caseName"
        New-Item -ItemType Directory -Path $artifact -Force | Out-Null
        Copy-Item -LiteralPath "$BuildDirectory/yoradio_esp8266_helix_native.bin" -Destination "$artifact/app.bin"
        Get-FileHash "$artifact/app.bin" -Algorithm SHA256 | Format-List | Out-File "$prefix-sha256.log"
        Write-Output "Flashing app0 only, AAC $caseName"
        & $python "$env:IDF_PATH/components/esptool_py/esptool/esptool.py" --chip esp8266 --port $Port --baud 460800 --before default_reset --after no_reset write_flash --flash_mode keep --flash_size 4MB --flash_freq keep 0x10000 "$artifact/app.bin" *> "$prefix-flash.log"
        if ($LASTEXITCODE) { throw "Flash failed: $prefix-flash.log; board may remain in downloader" }
        # No UART bytes while GPIO3 carries audio. Only RTS reset and TX capture.
        & $python tools/monitor_esp8266.py --port $Port --reset --seconds 20 *> "$prefix-uart.log"
        if ($LASTEXITCODE) { throw "Capture failed: $prefix-uart.log" }
        $capture = Get-Content -LiteralPath "$prefix-uart.log"
        $capture | Where-Object { $_ -match 'codec_ram:.*(RAM frame|physical wall|stack free|lifecycle)' }
        if (-not ($capture -match 'codec_ram:.*AAC RAM frame=')) { throw "No AAC result: $prefix-uart.log" }
    }
    Write-Output 'Diagnostic firmware remains installed: restore the ordinary app before hand-off.'
} finally {
    if ($radioOldPath) { $env:PATH = $radioOldPath }
    Pop-Location
}
