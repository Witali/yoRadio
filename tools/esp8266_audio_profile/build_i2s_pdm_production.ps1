param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [ValidatePattern('^[a-zA-Z0-9_-]+$')]
    [string]$Variant = 'esp8266-i2s-pdm-production',
    [ValidateSet('off', 'short', 'long')]
    [string]$WebAudioPause = 'off',
    [switch]$MemoryProfile,
    [switch]$SpiffsLog,
    [switch]$SpiffsLogHttp,
    [switch]$Diagnostic,
    [ValidateSet(10, 20)]
    [int]$LedUpdateHz = 10,
    [switch]$NoAudioLevelLed,
    [switch]$EnableOpus,
    [switch]$OpusBenchmark,
    [string]$OpusBenchmarkFixtures = '.build/esp8266-opus-board-fixtures'
)
$ErrorActionPreference = 'Stop'
if (($SpiffsLog -or $SpiffsLogHttp -or $MemoryProfile) -and -not $Diagnostic) {
    throw 'Diagnostic facilities require -Diagnostic; production must not contain SPIFFS logging/HTTP export'
}
if ($SpiffsLogHttp -and -not $SpiffsLog) { throw '-SpiffsLogHttp requires -SpiffsLog' }
if ($OpusBenchmark -and (-not $Diagnostic -or -not $EnableOpus)) { throw '-OpusBenchmark requires -Diagnostic and -EnableOpus' }
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$taskVariant = $Variant
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
    $taskDefaults = $taskDefaults -replace 'CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=\d+', "CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=$LedUpdateHz"
    if ($NoAudioLevelLed) { $taskDefaults = $taskDefaults.Replace('CONFIG_YORADIO_STATUS_LED=y', '# CONFIG_YORADIO_STATUS_LED is not set') }
    if ($EnableOpus) { $taskDefaults += "`nCONFIG_YORADIO_OGG_OPUS=y`nCONFIG_YORADIO_OPUS_INPUT_BYTES=1024`nCONFIG_YORADIO_OPUS_SCRATCH_BYTES=7680`n" }
    if ($OpusBenchmark) {
        $taskDefaults += "`nCONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y`nCONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER=y`n"
        $OpusBenchmarkFixtures = (Resolve-Path $OpusBenchmarkFixtures).Path.Replace('\', '/')
    }
    [IO.File]::WriteAllText("$taskBuild/production.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    Write-Output "Configuring $taskVariant on GPIO3/RX (no flashing)"
    $taskMemoryProfile = if ($MemoryProfile) { 'ON' } else { 'OFF' }
    $taskSpiffsLog = if ($SpiffsLog) { 'ON' } else { 'OFF' }
    $taskSpiffsLogHttp = if ($SpiffsLogHttp) { 'ON' } else { 'OFF' }
    $taskDiagnostic = if ($Diagnostic) { 'ON' } else { 'OFF' }
    $taskOpusBenchmark = if ($OpusBenchmark) { 'ON' } else { 'OFF' }
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
        '-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
        "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/production.defaults",
        '-DYORADIO_ESP8266_FIXED_I2S=OFF', '-DYORADIO_ESP8266_SPI_PDM_FAST_ISR=ON',
        '-DYORADIO_ESP8266_WEB_PROFILE=OFF',
        "-DYORADIO_ESP8266_WEB_AUDIO_PAUSE=$WebAudioPause",
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
        '-DYORADIO_ESP8266_AUDIO_TRACE=OFF', "-DYORADIO_ESP8266_MEMORY_PROFILE=$taskMemoryProfile",
        "-DYORADIO_ESP8266_SPIFFS_LOG=$taskSpiffsLog",
        "-DYORADIO_ESP8266_SPIFFS_LOG_HTTP=$taskSpiffsLogHttp",
        "-DYORADIO_ESP8266_DIAGNOSTIC=$taskDiagnostic",
        "-DYORADIO_ESP8266_OPUS_BENCHMARK=$taskOpusBenchmark",
        "-DYORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES=$OpusBenchmarkFixtures",
        '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    foreach ($taskRequired in @('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y', 'CONFIG_ESPTOOLPY_FLASHMODE_QIO=y', 'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y', 'CONFIG_LOG_DEFAULT_LEVEL=1', 'CONFIG_LOG_BOOTLOADER_LEVEL=1', 'CONFIG_YORADIO_HELIX_MP3_SSO=y', 'CONFIG_YORADIO_HELIX_AAC=y', 'CONFIG_YORADIO_AUDIO_MONO=y', 'CONFIG_YORADIO_STREAM_READ_WAIT_MS=0', 'CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=1000')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired" }
    }
    if ($taskConfig -match '(?m)^CONFIG_YORADIO_AUDIO_OUTPUT_(SPI_PDM|I2S_RCPDM|I2S_PCM)=y') { throw 'Only standard I2S PDM is allowed' }
    foreach ($taskRequired in @('CONFIG_YORADIO_STREAM_INPUT_BYTES=4096', 'CONFIG_YORADIO_STREAM_PREFILL_MS=1000', 'CONFIG_LWIP_SO_LINGER=y')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired; use a fresh -Variant build directory" }
    }
    $taskGzipEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y\r?$'
    $taskOpusEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_OGG_OPUS=y\r?$'
    if ($taskOpusEnabled -ne [bool]$EnableOpus) { throw 'Wrong cached Opus profile; use a fresh -Variant build directory' }
    if ($taskOpusEnabled -and $taskConfig -notmatch '(?m)^CONFIG_YORADIO_OPUS_SCRATCH_BYTES=7680\r?$') { throw 'Wrong cached Opus scratch size; use a fresh -Variant build directory' }
    $taskLedEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_STATUS_LED=y\r?$'
    if ($taskLedEnabled -eq [bool]$NoAudioLevelLed) { throw 'Wrong cached LED profile; use a fresh -Variant build directory' }
    if ($taskLedEnabled -and $taskConfig -notmatch "(?m)^CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=$LedUpdateHz`r?$") { throw 'Wrong cached LED refresh rate; use a fresh -Variant build directory' }
    Write-Output "Building $taskVariant, CPU160, QIO40"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
    $taskManifest = [ordered]@{
        purpose=$(if ($EnableOpus) { 'Experimental Opus native radio, I2S PDM32 DMA; not device-qualified; build does not flash' } elseif ($Diagnostic) { 'Diagnostic native radio, I2S PDM32 DMA, error logs only; build does not flash' } else { 'Production native radio, I2S PDM32 DMA, UART error logs only; build does not flash' })
        diagnostic=[bool]$Diagnostic
        experimental_opus=[bool]$taskOpusEnabled
        opus_input_bytes=$(if ($taskOpusEnabled) { 1024 } else { 0 })
        opus_scratch_bytes=$(if ($taskOpusEnabled) { 7680 } else { 0 })
        opus_benchmark=[bool]$OpusBenchmark
        opus_max_packet_ms=$(if ($taskOpusEnabled) { 20 } else { 0 })
        tone_test=$false
        web_profile=$false
        memory_profile=[bool]$MemoryProfile
        spiffs_log=[bool]$SpiffsLog
        spiffs_log_http=[bool]$SpiffsLogHttp
        audio_level_led=[bool]$taskLedEnabled
        audio_level_led_update_hz=$(if ($taskLedEnabled) { $LedUpdateHz } else { 0 })
        audio_level_led_max_brightness=$(if ($taskLedEnabled -and $taskConfig -match '(?m)^CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS=(\d+)') { [int]$Matches[1] } else { 0 })
        audio_gain_led_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/audio_gain_led.inc).Hash
        audio_level_led_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/status_led.c).Hash
        spiffs_log_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/spiffs_log.c).Hash
        web_audio_pause=$WebAudioPause
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
        web_audio_pause_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/audio_web_pause.inc).Hash
        stream_wait_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_read_wait.h).Hash
        http_receive_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_txrx.c).Hash
        stream_read_wait_ms=0; stream_idle_timeout_ms=1000
        stream_input_bytes=4096; stream_prefill_ms=1000
        codec_bridge_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/helix_codecs/codec_bridge.cpp).Hash
        stream_input_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_input_buffer.h).Hash
        stream_refill_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_input_refill.inc).Hash
        network_benchmark=$false
        cpu_mhz=160; flash='QIO40'; output='I2S PDM32 SLC-DMA'; data_gpio=3; dma_buffers=2; dma_words_per_buffer=512
        pcm_rate=48000; nominal_bit_rate_hz=1536000; bit_rate_hz=1538461; i2s=$true
        partition_layout='app0/app1 960 KiB, SPIFFS 256 KiB; flash app only'
    }
    if ($taskManifest.bytes -gt 0xf0000) { throw 'App exceeds OTA slot' }
    [IO.File]::WriteAllText("$taskArtifact/manifest.json", ($taskManifest | ConvertTo-Json), (New-Object Text.UTF8Encoding($false)))
    Write-Output "Saved $taskArtifact/app.bin ($($taskManifest.bytes) bytes); board default unchanged"
} finally {
    $env:PATH=$taskSavedPath; $env:IDF_PATH=$taskSavedIdf; $env:IDF_TOOLS_PATH=$taskSavedTools
    Pop-Location
}
