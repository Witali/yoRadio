param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$taskVariant = 'esp8266-i2s-pdm-production'
$taskBuild = "$taskRoot/.build/$taskVariant"
$taskArtifact = "$taskRoot/firmware/development/$taskVariant"
$taskSavedPath = $env:PATH
$taskSavedIdf = $env:IDF_PATH
$taskSavedTools = $env:IDF_TOOLS_PATH
function Invoke-TaskTool([string]$Executable, [string[]]$Arguments, [string]$Log) {
    $ErrorActionPreference = 'Continue'
    & $Executable @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Executable; see $Log" }
}
Push-Location $taskRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$taskRoot/.build/esp8266-tools"
    $taskCompiler = "$taskRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin"
    $env:PATH = "$taskRoot/.build/esp8266-python/Scripts;$taskCompiler;$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0;$taskRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$env:PATH"
    New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
    # Inherit canonical I2S PDM/codec/RAM/flash defaults, suppress routine logs.
    $taskDefaults = Get-Content esp8266/rtos-sdk-native/sdkconfig.defaults -Raw
    $taskDefaults = $taskDefaults.Replace('CONFIG_LOG_DEFAULT_LEVEL_INFO=y', 'CONFIG_LOG_DEFAULT_LEVEL_ERROR=y')
    $taskDefaults = $taskDefaults.Replace('CONFIG_LOG_BOOTLOADER_LEVEL_WARN=y', 'CONFIG_LOG_BOOTLOADER_LEVEL_ERROR=y')
    [IO.File]::WriteAllText("$taskBuild/production.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    Write-Output "Configuring $taskVariant on GPIO3/RX (no flashing)"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
        '-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
        "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/production.defaults",
        '-DYORADIO_ESP8266_FIXED_I2S=OFF', '-DYORADIO_ESP8266_SPI_PDM_FAST_ISR=ON',
        '-DYORADIO_ESP8266_WEB_PROFILE=OFF',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=OFF', '-DYORADIO_ESP8266_OUTPUT_COMPARE=OFF',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF', '-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF',
        '-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF', '-DYORADIO_ESP8266_AUDIO_PROFILE=OFF',
        '-DYORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=OFF',
        '-DYORADIO_ESP8266_CODEC_RAM_AAC_MATRIX=OFF',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK=OFF', '-DYORADIO_ESP8266_NETWORK_BENCHMARK_URL=',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY=OFF',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY=OFF',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP=0',
        '-DYORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY=OFF',
        '-DYORADIO_ESP8266_KARADIO_PIPELINE=OFF', '-DYORADIO_ESP8266_AUDIO_PROFILE_URL=',
        '-DYORADIO_ESP8266_AUDIO_TRACE=OFF', '-DYORADIO_ESP8266_MEMORY_PROFILE=OFF',
        '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    foreach ($taskRequired in @('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y', 'CONFIG_ESPTOOLPY_FLASHMODE_QIO=y', 'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y', 'CONFIG_LOG_DEFAULT_LEVEL=1', 'CONFIG_LOG_BOOTLOADER_LEVEL=1', 'CONFIG_YORADIO_HELIX_MP3_SSO=y', 'CONFIG_YORADIO_HELIX_AAC=y', 'CONFIG_YORADIO_AUDIO_MONO=y', 'CONFIG_YORADIO_STREAM_READ_WAIT_MS=0', 'CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=1000')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired" }
    }
    if ($taskConfig -match '(?m)^CONFIG_YORADIO_AUDIO_OUTPUT_(SPI_PDM|I2S_RCPDM|I2S_PCM)=y') { throw 'Only standard I2S PDM is allowed' }
    $taskGzipEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y\r?$'
    Write-Output "Building $taskVariant, CPU160, QIO40"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
    $taskManifest = [ordered]@{
        purpose='Production native radio, I2S PDM32 DMA, error logs only; build does not flash'
        tone_test=$false
        web_profile=$false
        log_level='error'
        playlist_web_gzip=[bool]$taskGzipEnabled
        built_utc=[DateTime]::UtcNow.ToString('o'); source_revision=(git rev-parse HEAD)
        app_sha256=(Get-FileHash "$taskArtifact/app.bin").Hash
        bytes=(Get-Item "$taskArtifact/app.bin").Length; app_address='0x10000'
        config_sha256=(Get-FileHash "$taskArtifact/sdkconfig").Hash
        output_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/native_audio_output.c).Hash
        web_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/web_service.c).Hash
        playlist_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/playlist_service.c).Hash
        audio_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/audio_service.c).Hash
        stream_wait_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_read_wait.h).Hash
        http_receive_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_txrx.c).Hash
        stream_read_wait_ms=0; stream_idle_timeout_ms=1000
        network_benchmark=$false
        cpu_mhz=160; flash='QIO40'; output='I2S PDM32 SLC-DMA'; data_gpio=3; dma_buffers=2; dma_words_per_buffer=512
        pcm_rate=48000; nominal_bit_rate_hz=1536000; bit_rate_hz=1538461; i2s=$true
        partition_layout='app0/app1 960 KiB, SPIFFS 256 KiB; flash app only'
    }
    if ($taskManifest.bytes -gt 0xf0000) { throw 'App exceeds OTA slot' }
    $taskManifest | ConvertTo-Json | Out-File "$taskArtifact/manifest.json" -Encoding utf8
    Write-Output "Saved $taskArtifact/app.bin ($($taskManifest.bytes) bytes); board default unchanged"
} finally {
    $env:PATH=$taskSavedPath; $env:IDF_PATH=$taskSavedIdf; $env:IDF_TOOLS_PATH=$taskSavedTools
    Pop-Location
}
