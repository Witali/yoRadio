param(
    [string[]]$Variants = @('original', 'limit', 'unroll4', 'unroll8', 'unroll32', 'mask8', 'branchless8'),
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [switch]$DisableBatch,
    [switch]$SimpleUnroll4,
    [string]$ArtifactSuffix = '',
    [switch]$Radio
)
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$oldPath = $env:PATH
Push-Location $radioRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$radioRoot/.build/esp8266-tools"
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PATH = "$radioRoot/.build/esp8266-python/Scripts;$radioRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$radioRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin;$radioRoot/.build/esp8266-tools/tools/ninja/1.9.0;$env:PATH"
    $cmake = "$radioRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe"
    $build = '.build/rcpdm-speed'
    New-Item -ItemType Directory -Path $build -Force | Out-Null
    if (-not (Test-Path "$build/sdkconfig")) {
        Copy-Item docs/benchmarks/esp8266-output-compare-2026-09-06/sdkconfig-rcpdm "$build/sdkconfig"
    }
    foreach ($variant in $Variants) {
        if ($variant -notmatch '^(production|simple|original|limit|unroll4|unroll8|unroll32|mask8|branchless8)$') { throw 'Unknown variant' }
        if ($SimpleUnroll4 -and $variant -ne 'simple') { throw 'SimpleUnroll4 requires the simple variant' }
        $label = if ($DisableBatch) { "$variant-no-batch" } else { $variant }
        if ($ArtifactSuffix) {
            if ($ArtifactSuffix -notmatch '^[a-z0-9-]+$') { throw 'Invalid artifact suffix' }
            $label += "-$ArtifactSuffix"
        }
        if ($Radio) {
            if ($variant -ne 'production') { throw 'Radio only permits the production implementation' }
            $label += '-radio'
        }
        $isolated = if ($Radio) { 'OFF' } else { 'ON' }
        $batch = if ($DisableBatch) { 'OFF' } else { 'ON' }
        $simpleUnroll = if ($SimpleUnroll4) { 'ON' } else { 'OFF' }
        $artifact = "firmware/development/esp8266-rcpdm-speed/$label"
        $logs = ".build/rcpdm-speed-results/$label"
        New-Item -ItemType Directory -Path $artifact, $logs -Force | Out-Null
        Write-Output "Building RCPDM $variant"
        & $cmake -S esp8266/rtos-sdk-native -B $build -G Ninja "-DSDKCONFIG=$radioRoot/$build/sdkconfig" `
            "-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=$isolated" "-DYORADIO_ESP8266_OUTPUT_COMPARE=$isolated" `
            "-DYORADIO_ESP8266_RCPDM_VARIANT=$variant" -DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF `
            "-DYORADIO_ESP8266_RCPDM_BATCH=$batch" `
            "-DYORADIO_ESP8266_RCPDM_SIMPLE_UNROLL4=$simpleUnroll" `
            -DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF -DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF `
            -DYORADIO_ESP8266_AUDIO_PROFILE=OFF -DYORADIO_ESP8266_AUDIO_TRACE=OFF `
            -DYORADIO_ESP8266_MEMORY_PROFILE=OFF -DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF *> "$logs/configure.log"
        if ($LASTEXITCODE) { throw "Configure failed: $logs" }
        & "$radioRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" -C $build *> "$logs/build.log"
        if ($LASTEXITCODE) { throw "Build failed: $logs" }
        Copy-Item "$build/yoradio_esp8266_helix_native.bin" "$artifact/app.bin"
        Copy-Item "$build/yoradio_esp8266_helix_native.elf" "$logs/app.elf"
        & xtensa-lx106-elf-size.exe -A "$logs/app.elf" > "$logs/sections.txt"
        & xtensa-lx106-elf-nm.exe -S --size-sort "$logs/app.elf" > "$logs/symbols.txt"
        & xtensa-lx106-elf-objdump.exe -d "$logs/app.elf" > "$logs/disassembly.txt"
        $purpose = if ($Radio) { 'Ordinary native radio with optimized RCPDM32; alternate output, not board default' } else { 'Diagnostic RCPDM exactness and speed, not ordinary radio' }
        $manifest = [ordered]@{ variant=$label; purpose=$purpose; source=(git rev-parse HEAD); compiled_working_tree=$true; batch=(-not $DisableBatch); simple_unroll4=[bool]$SimpleUnroll4; cpu_mhz=160; flash='QIO40'; app_address='0x10000'; bytes=(Get-Item "$artifact/app.bin").Length; sha256=(Get-FileHash "$artifact/app.bin").Hash }
        $manifest | ConvertTo-Json | Out-File "$artifact/manifest.json" -Encoding utf8
        Write-Output "$variant SHA256=$($manifest.sha256)"
    }
} finally { $env:PATH = $oldPath; Pop-Location }
