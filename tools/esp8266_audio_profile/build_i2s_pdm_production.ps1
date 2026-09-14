param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [string]$RuntimeRoot = '',
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
    [ValidateSet('c', 'gcc-asm', 'optimized-asm', 'hoisted-asm', 'bands-intensity-asm', 'bands-blocks-asm', 'bands-combined-asm', 'bands-pulse-lookup-asm', 'bands-tell-inline-asm', 'bands-fused-asm', 'bands-tell-intensity-asm', 'bands-update-fast-asm', 'bands-tell-update-asm', 'bands-tell-bits1-asm', 'bands-layout32-asm', 'bands-layout128-asm', 'bands-cache-reuse-asm', 'bands-inner4-asm', 'bands-logp-asm', 'bands-pvq-addx-asm', 'bands-small-div-asm')]
    [string]$OpusBackend = 'c',
    [switch]$OpusBandsTextLiterals,
    [ValidateSet(1024, 1536, 2048, 3072, 4096)]
    [int]$OpusInputBytes = 1024,
    [switch]$OpusLowRam,
    [ValidateSet(4352, 6144)]
    [int]$OpusScratchBytes = 6144,
    [switch]$NoSpiffsCache,
    [switch]$OpusWordAsm,
    [switch]$OpusIcdfFlashWord,
    [switch]$OpusFirFlashWord,
    [switch]$OpusPvqIram,
    [switch]$OpusFunctionProfile,
    [switch]$OpusFunctionProfileCoarse,
    [switch]$OpusCeltDecodeOnly,
    [switch]$OpusRotationLx106,
    [switch]$OpusDivOnce,
    [switch]$OpusPcmPublish,
    [switch]$OpusPcmLeases,
    [switch]$OpusPcmQueue,
    [ValidateSet(1536, 2048)]
    [int]$PcmStackBytes = 2048,
    [switch]$Pdm32Iram,
    [switch]$Pdm32Batch,
    [ValidateSet(64, 128, 256, 512)]
    [int]$Pdm32LoanWords = 512,
    [ValidateSet(256, 512, 768)]
    [int]$DmaBufferWords = 512,
    [ValidateRange(250, 60000)]
    [int]$StreamIdleTimeoutMs = 1000,
    [switch]$SdkRxDiag,
    [switch]$OpusStreamTest,
    [switch]$OpusBenchmark,
    [switch]$OpusBenchmarkOutput,
    [switch]$OpusDivisionBenchmark,
    [string]$OpusDivisionFixtures = '.build/opus-bands-division-census',
    [ValidateRange(0, 11)]
    [int]$OpusProfileStage = 0,
    [string]$OpusBenchmarkFixtures = '.build/esp8266-opus-board-fixtures'
)
$ErrorActionPreference = 'Stop'
if (($SpiffsLog -or $SpiffsLogHttp -or $MemoryProfile) -and -not $Diagnostic) {
    throw 'Diagnostic facilities require -Diagnostic; production must not contain SPIFFS logging/HTTP export'
}
if ($SpiffsLogHttp -and -not $SpiffsLog) { throw '-SpiffsLogHttp requires -SpiffsLog' }
if ($OpusBenchmark -and (-not $Diagnostic -or -not $EnableOpus)) { throw '-OpusBenchmark requires -Diagnostic and -EnableOpus' }
if ($OpusDivisionBenchmark -and (-not $OpusBenchmark -or -not $Diagnostic -or $OpusBackend -ne 'bands-small-div-asm' -or $OpusBenchmarkOutput -or $OpusFunctionProfile -or $OpusProfileStage)) { throw '-OpusDivisionBenchmark requires diagnostic raw small-div ASM without profiling/output' }
if ($OpusPvqIram -and (-not $Diagnostic -or -not $EnableOpus)) { throw '-OpusPvqIram requires diagnostic Opus' }
if ($OpusFunctionProfile -and (-not $Diagnostic -or -not $EnableOpus -or -not $OpusBenchmark -or $OpusBenchmarkOutput -or $OpusProfileStage)) { throw '-OpusFunctionProfile requires diagnostic raw-only Opus' }
if ($OpusFunctionProfileCoarse -and -not $OpusFunctionProfile) { throw '-OpusFunctionProfileCoarse requires -OpusFunctionProfile' }
if ($OpusBackend -ne 'c') {
    if (-not $Diagnostic -or -not $EnableOpus) { throw 'Opus ASM backend requires diagnostic Opus' }
    if (-not $OpusWordAsm -or -not $OpusIcdfFlashWord -or -not $OpusFirFlashWord) { throw 'Pinned ASM requires -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord' }
    if ($OpusLowRam -or $OpusPcmLeases -or $OpusCeltDecodeOnly -or $OpusRotationLx106 -or $OpusDivOnce -or $OpusProfileStage) { throw 'Other decoder experiments require a separately regenerated ASM snapshot' }
}
if ($OpusBandsTextLiterals -and (-not $Diagnostic -or $OpusBackend -ne 'bands-tell-inline-asm')) { throw '-OpusBandsTextLiterals requires diagnostic bands-tell-inline-asm' }
if ($OpusBenchmarkOutput -and -not $OpusBenchmark) { throw '-OpusBenchmarkOutput requires -OpusBenchmark' }
if ($OpusProfileStage -and (-not $OpusBenchmark -or $OpusBenchmarkOutput)) { throw '-OpusProfileStage requires a raw-only Opus benchmark' }
if ($OpusStreamTest -and (-not $Diagnostic -or -not $EnableOpus)) { throw '-OpusStreamTest requires -Diagnostic and -EnableOpus' }
if ($OpusWordAsm -and -not $EnableOpus) { throw '-OpusWordAsm requires -EnableOpus' }
if ($OpusIcdfFlashWord -and -not $EnableOpus) { throw '-OpusIcdfFlashWord requires -EnableOpus' }
if ($OpusFirFlashWord -and -not $EnableOpus) { throw '-OpusFirFlashWord requires -EnableOpus' }
if ($OpusLowRam -and (-not $EnableOpus -or -not $Diagnostic)) { throw '-OpusLowRam requires diagnostic Opus until device qualification' }
if ($OpusScratchBytes -ne 6144 -and -not $OpusLowRam) { throw 'Reduced Opus scratch requires -OpusLowRam' }
if ($OpusCeltDecodeOnly -and -not $EnableOpus) { throw '-OpusCeltDecodeOnly requires -EnableOpus' }
if ($OpusDivOnce -and -not $EnableOpus) { throw '-OpusDivOnce requires -EnableOpus' }
if ($OpusPcmPublish -and (-not $EnableOpus -or -not $Diagnostic)) { throw '-OpusPcmPublish requires diagnostic Opus until board qualification' }
if ($OpusPcmQueue) {
    if (-not $EnableOpus -or -not $Diagnostic -or $OpusBenchmark -or $OpusPcmPublish -or $WebAudioPause -ne 'off') {
        throw '-OpusPcmQueue requires diagnostic live Opus without benchmark/publication/WebUI pause'
    }
    $OpusPcmLeases = $true
}
if ($DmaBufferWords -eq 256 -and -not $OpusPcmQueue) { throw 'DMA256 requires -OpusPcmQueue' }
if ($PcmStackBytes -ne 2048 -and -not $OpusPcmQueue) { throw 'PCM stack override requires -OpusPcmQueue' }
if ($OpusPcmLeases -and (-not $EnableOpus -or -not $Diagnostic)) { throw '-OpusPcmLeases requires diagnostic Opus until queue qualification' }
if ($OpusRotationLx106 -and (-not $EnableOpus -or -not $Diagnostic)) { throw '-OpusRotationLx106 requires diagnostic Opus until board qualification' }
if ($Pdm32Iram -and -not $Diagnostic) { throw '-Pdm32Iram requires -Diagnostic until board qualification' }
if ($Pdm32Batch -and -not $Diagnostic) { throw '-Pdm32Batch requires -Diagnostic until board qualification' }
if ($Pdm32LoanWords -ne 512 -and -not $Diagnostic) { throw 'Short PDM32 loans require -Diagnostic' }
if ($DmaBufferWords -ne 512 -and (-not $Diagnostic -or -not $EnableOpus)) { throw 'Larger DMA buffers require diagnostic Opus' }
if ($SdkRxDiag -and -not $Diagnostic) { throw '-SdkRxDiag requires -Diagnostic' }
if ($NoSpiffsCache -and -not $EnableOpus) { throw '-NoSpiffsCache requires -EnableOpus' }
$taskOpusStreamTestEnabled = [bool]($OpusStreamTest -or $OpusBenchmark)
if ($OpusInputBytes -ne 1024 -and (-not $Diagnostic -or -not $EnableOpus)) {
    throw '-OpusInputBytes changes require diagnostic Opus until RAM qualification'
}
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
if (-not $RuntimeRoot) { $RuntimeRoot = "$taskRoot/.build" }
$taskRuntime = (Resolve-Path -LiteralPath $RuntimeRoot).Path.Replace('\', '/')
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
function Set-TaskSpiffsCacheDefaults([string]$Defaults, [bool]$Disabled) {
    if (-not $Disabled) { return $Defaults }
    # Replace only cache options, never filesystem geometry or file limits.
    $taskText = $Defaults -replace '(?m)^(?:CONFIG_SPIFFS_CACHE(?:_WR)?=[^\r\n]*|# CONFIG_SPIFFS_CACHE(?:_WR)? is not set)\r?\n?', ''
    return $taskText + "`n# CONFIG_SPIFFS_CACHE is not set`n# CONFIG_SPIFFS_CACHE_WR is not set`n"
}
function Get-TaskSpiffsCacheProfile([string]$Config, [bool]$Disabled) {
    $taskReadCache = $Config -match '(?m)^CONFIG_SPIFFS_CACHE=y\r?$'
    $taskWriteCache = $Config -match '(?m)^CONFIG_SPIFFS_CACHE_WR=y\r?$'
    if ($taskReadCache -eq $Disabled -or $taskWriteCache -ne $taskReadCache) {
        throw 'Wrong cached SPIFFS cache profile; use a fresh -Variant build directory'
    }
    return [pscustomobject]@{ enabled = $taskReadCache; write_enabled = $taskWriteCache }
}
function Set-TaskOpusRuntimeDefaults([string]$Defaults, [bool]$Benchmark) {
    # Runtime stats select trace/formatting and enlarge every task/queue. A live
    # URL probe does not need them; explicitly disable stale benchmark defaults.
    $taskStats = 'CONFIG_FREERTOS_(?:GENERATE_RUN_TIME_STATS|USE_TRACE_FACILITY|USE_STATS_FORMATTING_FUNCTIONS|RUN_TIME_STATS_USING_ESP_TIMER|RUN_TIME_STATS_USING_CPU_CLK)'
    $taskText = $Defaults -replace "(?m)^(?:$taskStats=[^\r\n]*|# $taskStats is not set)\r?\n?", ''
    foreach ($taskOption in @('GENERATE_RUN_TIME_STATS', 'USE_TRACE_FACILITY', 'USE_STATS_FORMATTING_FUNCTIONS', 'RUN_TIME_STATS_USING_ESP_TIMER')) {
        $taskText += $(if ($Benchmark) { "`nCONFIG_FREERTOS_$taskOption=y" } else { "`n# CONFIG_FREERTOS_$taskOption is not set" })
    }
    return $taskText + "`n# CONFIG_FREERTOS_RUN_TIME_STATS_USING_CPU_CLK is not set`n"
}
function Get-TaskOpusRuntimeProfile([string]$Config, [bool]$Benchmark) {
    foreach ($taskOption in @('GENERATE_RUN_TIME_STATS', 'USE_TRACE_FACILITY', 'USE_STATS_FORMATTING_FUNCTIONS', 'RUN_TIME_STATS_USING_ESP_TIMER')) {
        $taskEnabled = $Config -match "(?m)^CONFIG_FREERTOS_$taskOption=y`r?$"
        if ($taskEnabled -ne $Benchmark) {
            throw "Wrong cached FreeRTOS runtime profile: $taskOption; use a fresh -Variant build directory"
        }
    }
    if ($Config -match '(?m)^CONFIG_FREERTOS_RUN_TIME_STATS_USING_CPU_CLK=y\r?$') {
        throw 'Wrong cached FreeRTOS runtime clock; use a fresh -Variant build directory'
    }
    return [pscustomobject]@{ enabled = $Benchmark }
}
function Set-TaskStreamIdleDefaults([string]$Defaults, [int]$TimeoutMs) {
    if ($TimeoutMs -lt 250 -or $TimeoutMs -gt 60000) { throw 'Stream idle timeout must be 250..60000 ms' }
    $taskText = $Defaults -replace '(?m)^CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=[^\r\n]*\r?\n?', ''
    return $taskText + "`nCONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=$TimeoutMs`n"
}
function Assert-TaskStreamIdleConfig([string]$Config, [int]$TimeoutMs) {
    $taskMatches = [regex]::Matches($Config, '(?m)^CONFIG_YORADIO_STREAM_IDLE_TIMEOUT_MS=(\d+)\r?$')
    if ($taskMatches.Count -ne 1 -or [int]$taskMatches[0].Groups[1].Value -ne $TimeoutMs) {
        throw 'Wrong cached stream idle timeout; use a fresh -Variant build directory'
    }
}
Push-Location $taskRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$taskRuntime/esp8266-tools"
    $taskCompiler = "$taskRuntime/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin"
    $env:PATH = "$taskRuntime/esp8266-python/Scripts;$taskCompiler;$taskRuntime/esp8266-tools/tools/ninja/1.9.0;$taskRuntime/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$env:PATH"
    New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
    # Inherit canonical I2S PDM/codec/RAM/flash defaults, suppress routine logs.
    $taskDefaults = Get-Content esp8266/rtos-sdk-native/sdkconfig.defaults -Raw
    $taskDefaults = $taskDefaults.Replace('CONFIG_LOG_DEFAULT_LEVEL_INFO=y', 'CONFIG_LOG_DEFAULT_LEVEL_ERROR=y')
    $taskDefaults = $taskDefaults.Replace('CONFIG_LOG_BOOTLOADER_LEVEL_WARN=y', 'CONFIG_LOG_BOOTLOADER_LEVEL_ERROR=y')
    $taskDefaults = $taskDefaults -replace 'CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=\d+', "CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=$LedUpdateHz"
    if ($NoAudioLevelLed) { $taskDefaults = $taskDefaults.Replace('CONFIG_YORADIO_STATUS_LED=y', '# CONFIG_YORADIO_STATUS_LED is not set') }
    if ($EnableOpus) { $taskDefaults += "`nCONFIG_YORADIO_OGG_OPUS=y`nCONFIG_YORADIO_OPUS_INPUT_BYTES=$OpusInputBytes`nCONFIG_YORADIO_OPUS_SCRATCH_BYTES=$OpusScratchBytes`n" }
    $taskDefaults = Set-TaskSpiffsCacheDefaults $taskDefaults ([bool]$NoSpiffsCache)
    $taskDefaults = Set-TaskOpusRuntimeDefaults $taskDefaults ([bool]$OpusBenchmark)
    $taskDefaults = Set-TaskStreamIdleDefaults $taskDefaults $StreamIdleTimeoutMs
    if ($OpusBenchmark) {
        $OpusBenchmarkFixtures = (Resolve-Path $OpusBenchmarkFixtures).Path.Replace('\', '/')
    }
    [IO.File]::WriteAllText("$taskBuild/production.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    Write-Output "Configuring $taskVariant on GPIO3/RX (no flashing)"
    $taskMemoryProfile = if ($MemoryProfile) { 'ON' } else { 'OFF' }
    $taskSpiffsLog = if ($SpiffsLog) { 'ON' } else { 'OFF' }
    $taskSpiffsLogHttp = if ($SpiffsLogHttp) { 'ON' } else { 'OFF' }
    $taskDiagnostic = if ($Diagnostic) { 'ON' } else { 'OFF' }
    $taskOpusBenchmark = if ($OpusBenchmark) { 'ON' } else { 'OFF' }
    $taskOpusBenchmarkOutput = if ($OpusBenchmarkOutput) { 'ON' } else { 'OFF' }
    $taskOpusDivisionBenchmark = if ($OpusDivisionBenchmark) { 'ON' } else { 'OFF' }
    if ($OpusDivisionBenchmark) { $OpusDivisionFixtures = (Resolve-Path $OpusDivisionFixtures).Path.Replace('\', '/') }
    $taskOpusStreamTest = if ($taskOpusStreamTestEnabled) { 'ON' } else { 'OFF' }
    $taskOpusWordAsm = if ($OpusWordAsm) { 'ON' } else { 'OFF' }
    $taskOpusBandsTextLiterals = if ($OpusBandsTextLiterals) { 'ON' } else { 'OFF' }
    $taskOpusIcdfFlashWord = if ($OpusIcdfFlashWord) { 'ON' } else { 'OFF' }
    $taskOpusFirFlashWord = if ($OpusFirFlashWord) { 'ON' } else { 'OFF' }
    $taskOpusPvqIram = if ($OpusPvqIram) { 'ON' } else { 'OFF' }
    $taskOpusFunctionProfile = if ($OpusFunctionProfile) { 'ON' } else { 'OFF' }
    $taskOpusFunctionCoarse = if ($OpusFunctionProfileCoarse) { 'ON' } else { 'OFF' }
    $taskOpusLowRam = if ($OpusLowRam) { 'ON' } else { 'OFF' }
    $taskOpusCeltDecodeOnly = if ($OpusCeltDecodeOnly) { 'ON' } else { 'OFF' }
    $taskOpusRotationLx106 = if ($OpusRotationLx106) { 'ON' } else { 'OFF' }
    $taskOpusDivOnce = if ($OpusDivOnce) { 'ON' } else { 'OFF' }
    $taskPdm32Iram = if ($Pdm32Iram) { 'ON' } else { 'OFF' }
    $taskPdm32Batch = if ($Pdm32Batch) { 'ON' } else { 'OFF' }
    $taskOpusPcmPublish = if ($OpusPcmPublish) { 'ON' } else { 'OFF' }
    $taskOpusPcmLeases = if ($OpusPcmLeases) { 'ON' } else { 'OFF' }
    $taskOpusPcmQueue = if ($OpusPcmQueue) { 'ON' } else { 'OFF' }
    $taskSdkRxDiag = if ($SdkRxDiag) { 'ON' } else { 'OFF' }
    Invoke-TaskTool "$taskRuntime/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
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
        "-DYORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT=$taskOpusBenchmarkOutput",
        "-DYORADIO_ESP8266_OPUS_DIVISION_BENCHMARK=$taskOpusDivisionBenchmark",
        "-DYORADIO_ESP8266_OPUS_DIVISION_FIXTURES=$OpusDivisionFixtures",
        "-DYORADIO_ESP8266_OPUS_STREAM_TEST=$taskOpusStreamTest",
        "-DYORADIO_OPUS_WORD_ASM=$taskOpusWordAsm",
        "-DYORADIO_OPUS_BACKEND=$OpusBackend",
        "-DYORADIO_OPUS_BANDS_TEXT_LITERALS=$taskOpusBandsTextLiterals",
        "-DYORADIO_OPUS_ICDF_FLASH_WORD=$taskOpusIcdfFlashWord",
        "-DYORADIO_OPUS_FIR_FLASH_WORD=$taskOpusFirFlashWord",
        "-DYORADIO_OPUS_PVQ_IRAM=$taskOpusPvqIram",
        "-DYORADIO_OPUS_FUNCTION_PROFILE=$taskOpusFunctionProfile",
        "-DYORADIO_OPUS_FUNCTION_PROFILE_COARSE=$taskOpusFunctionCoarse",
        "-DYORADIO_OPUS_LOW_RAM=$taskOpusLowRam",
        "-DYORADIO_OPUS_CELT_DECODE_ONLY=$taskOpusCeltDecodeOnly",
        "-DYORADIO_OPUS_ROTATION_LX106=$taskOpusRotationLx106",
        "-DYORADIO_OPUS_DIV_ONCE=$taskOpusDivOnce",
        "-DYORADIO_OPUS_PROFILE_STAGE=$OpusProfileStage",
        "-DYORADIO_ESP8266_PDM32_IRAM=$taskPdm32Iram",
        "-DYORADIO_ESP8266_PDM32_BATCH=$taskPdm32Batch",
        "-DYORADIO_ESP8266_OPUS_PCM_PUBLISH=$taskOpusPcmPublish",
        "-DYORADIO_OPUS_PCM_LEASES=$taskOpusPcmLeases",
        "-DYORADIO_ESP8266_OPUS_PCM_QUEUE=$taskOpusPcmQueue",
        "-DYORADIO_ESP8266_PCM_STACK_BYTES=$PcmStackBytes",
        "-DYORADIO_ESP8266_PDM32_LOAN_WORDS=$Pdm32LoanWords",
        "-DYORADIO_ESP8266_DMA_BUFFER_WORDS=$DmaBufferWords",
        "-DYORADIO_ESP8266_SDK_RX_DIAG=$taskSdkRxDiag",
        "-DYORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES=$OpusBenchmarkFixtures",
        '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    $taskSpiffsCache = Get-TaskSpiffsCacheProfile $taskConfig ([bool]$NoSpiffsCache)
    $taskOpusRuntime = Get-TaskOpusRuntimeProfile $taskConfig ([bool]$OpusBenchmark)
    Assert-TaskStreamIdleConfig $taskConfig $StreamIdleTimeoutMs
    foreach ($taskRequired in @('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y', 'CONFIG_ESPTOOLPY_FLASHMODE_QIO=y', 'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y', 'CONFIG_LOG_DEFAULT_LEVEL=1', 'CONFIG_LOG_BOOTLOADER_LEVEL=1', 'CONFIG_YORADIO_HELIX_MP3_SSO=y', 'CONFIG_YORADIO_HELIX_AAC=y', 'CONFIG_YORADIO_AUDIO_MONO=y', 'CONFIG_YORADIO_STREAM_READ_WAIT_MS=0')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired" }
    }
    if ($taskConfig -match '(?m)^CONFIG_YORADIO_AUDIO_OUTPUT_(SPI_PDM|I2S_RCPDM|I2S_PCM)=y') { throw 'Only standard I2S PDM is allowed' }
    foreach ($taskRequired in @('CONFIG_YORADIO_STREAM_INPUT_BYTES=4096', 'CONFIG_YORADIO_STREAM_PREFILL_MS=1000', 'CONFIG_LWIP_SO_LINGER=y')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired; use a fresh -Variant build directory" }
    }
    $taskGzipEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y\r?$'
    $taskOpusEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_OGG_OPUS=y\r?$'
    if ($taskOpusEnabled -ne [bool]$EnableOpus) { throw 'Wrong cached Opus profile; use a fresh -Variant build directory' }
    if ($taskOpusEnabled -and $taskConfig -notmatch "(?m)^CONFIG_YORADIO_OPUS_INPUT_BYTES=$OpusInputBytes`r?$") { throw 'Wrong cached Opus input size; use a fresh -Variant build directory' }
    if ($taskOpusEnabled -and $taskConfig -notmatch "(?m)^CONFIG_YORADIO_OPUS_SCRATCH_BYTES=$OpusScratchBytes`r?$") { throw 'Wrong cached Opus scratch size; use a fresh -Variant build directory' }
    $taskLedEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_STATUS_LED=y\r?$'
    if ($taskLedEnabled -eq [bool]$NoAudioLevelLed) { throw 'Wrong cached LED profile; use a fresh -Variant build directory' }
    if ($taskLedEnabled -and $taskConfig -notmatch "(?m)^CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=$LedUpdateHz`r?$") { throw 'Wrong cached LED refresh rate; use a fresh -Variant build directory' }
    Write-Output "Building $taskVariant, CPU160, QIO40"
    Invoke-TaskTool "$taskRuntime/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
    if ($SdkRxDiag) {
        Copy-Item "$taskBuild/sdk-rxdiag/manifest.json" "$taskArtifact/sdk-rxdiag-manifest.json"
    }
    $taskManifest = [ordered]@{
        purpose=$(if ($EnableOpus) { 'Experimental Opus native radio, I2S PDM32 DMA; not device-qualified; build does not flash' } elseif ($Diagnostic) { 'Diagnostic native radio, I2S PDM32 DMA, error logs only; build does not flash' } else { 'Production native radio, I2S PDM32 DMA, UART error logs only; build does not flash' })
        diagnostic=[bool]$Diagnostic
        experimental_opus=[bool]$taskOpusEnabled
        opus_input_bytes=$(if ($taskOpusEnabled) { $OpusInputBytes } else { 0 })
        opus_scratch_bytes=$(if ($taskOpusEnabled) { $OpusScratchBytes } else { 0 })
        opus_low_ram=[bool]$OpusLowRam
        opus_backend=$OpusBackend
        opus_bands_small_div_manifest_sha256=$(if ($OpusBackend -eq 'bands-small-div-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-small-div.json").Hash } else { $null })
        opus_bands_pvq_addx_manifest_sha256=$(if ($OpusBackend -eq 'bands-pvq-addx-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-pvq-addx.json").Hash } else { $null })
        opus_bands_logp_manifest_sha256=$(if ($OpusBackend -eq 'bands-logp-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-logp.json").Hash } else { $null })
        opus_bands_cache_reuse_manifest_sha256=$(if ($OpusBackend -eq 'bands-cache-reuse-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-cache-reuse.json").Hash } else { $null })
        opus_bands_inner4_manifest_sha256=$(if ($OpusBackend -eq 'bands-inner4-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-inner4.json").Hash } else { $null })
        opus_bands_text_literals=[bool]$OpusBandsTextLiterals
        opus_bands_layout_manifest_sha256=$(if ($OpusBackend -match '^bands-layout(32|128)-asm$') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-layout$($Matches[1]).json").Hash } else { $null })
        opus_bands_tell_bits1_manifest_sha256=$(if ($OpusBackend -eq 'bands-tell-bits1-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-tell-bits1.json").Hash } else { $null })
        opus_bands_tell_update_manifest_sha256=$(if ($OpusBackend -eq 'bands-tell-update-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-tell-update.json").Hash } else { $null })
        opus_bands_tell_inline_manifest_sha256=$(if ($OpusBackend -eq 'bands-tell-inline-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-tell-inline.json").Hash } else { $null })
        opus_bands_fused_manifest_sha256=$(if ($OpusBackend -eq 'bands-fused-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-fused.json").Hash } else { $null })
        opus_bands_tell_intensity_manifest_sha256=$(if ($OpusBackend -eq 'bands-tell-intensity-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-tell-intensity.json").Hash } else { $null })
        opus_bands_update_fast_manifest_sha256=$(if ($OpusBackend -eq 'bands-update-fast-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-update-fast.json").Hash } else { $null })
        opus_bands_pulse_lookup_manifest_sha256=$(if ($OpusBackend -eq 'bands-pulse-lookup-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-pulse-lookup.json").Hash } else { $null })
        opus_bands_combined_manifest_sha256=$(if ($OpusBackend -eq 'bands-combined-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-combined.json").Hash } else { $null })
        opus_bands_blocks_manifest_sha256=$(if ($OpusBackend -eq 'bands-blocks-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-blocks.json").Hash } else { $null })
        opus_asm_manifest_sha256=$(if ($OpusBackend -ne 'c') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/manifest.json").Hash } else { $null })
        opus_asm_optimization_sha256=$(if ($OpusBackend -eq 'optimized-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/optimized.json").Hash } elseif ($OpusBackend -eq 'hoisted-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/hoisted.json").Hash } elseif ($OpusBackend -eq 'bands-intensity-asm') { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/asm/lx106/bands-intensity.json").Hash } else { $null })
        opus_plc_source_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/upstream/silk/PLC.c").Hash
        opus_lpc_source_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/celt_lpc.c").Hash
        opus_memory_source_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/opus_memory.c").Hash
        opus_memory_header_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/opus_memory.h").Hash
        opus_benchmark=[bool]$OpusBenchmark
        opus_benchmark_output=[bool]$OpusBenchmarkOutput
        opus_division_benchmark=[bool]$OpusDivisionBenchmark
        opus_division_source_sha256=$(if ($OpusDivisionBenchmark) { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/main/opus_division_benchmark.inc").Hash } else { $null })
        opus_division_header_sha256=$(if ($OpusDivisionBenchmark) { (Get-FileHash "$OpusDivisionFixtures/opus_division_fixtures.h").Hash } else { $null })
        opus_benchmark_source_sha256=$(if ($OpusBenchmark) { (Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/main/opus_benchmark.cpp").Hash } else { $null })
        opus_benchmark_manifest_sha256=$(if ($OpusBenchmark) { (Get-FileHash "$OpusBenchmarkFixtures/manifest.json").Hash } else { $null })
        opus_benchmark_header_sha256=$(if ($OpusBenchmark) { (Get-FileHash "$OpusBenchmarkFixtures/opus_board_fixtures.h").Hash } else { $null })
        opus_stream_test=[bool]$taskOpusStreamTestEnabled
        freertos_runtime_stats=[bool]$taskOpusRuntime.enabled
        opus_word_asm=[bool]$OpusWordAsm
        opus_icdf_flash_word=[bool]$OpusIcdfFlashWord
        opus_fir_flash_word=[bool]$OpusFirFlashWord
        opus_pvq_iram=[bool]$OpusPvqIram
        opus_function_profile=[bool]$OpusFunctionProfile
        opus_function_profile_coarse=[bool]$OpusFunctionProfileCoarse
        opus_pvq_iram_fragment_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/components/opus_decoder/opus_pvq_iram.lf").Hash
        opus_celt_decode_only=[bool]$OpusCeltDecodeOnly
        opus_rotation_lx106=[bool]$OpusRotationLx106
        opus_div_once=[bool]$OpusDivOnce
        opus_pcm_publish=[bool]$OpusPcmPublish
        opus_pcm_leases=[bool]$OpusPcmLeases
        opus_pcm_queue=[bool]$OpusPcmQueue
        opus_pcm_stack_bytes=$(if ($OpusPcmQueue) { $PcmStackBytes } else { 0 })
        opus_pcm_queue_source_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/main/audio_pcm_queue.c" -Algorithm SHA256).Hash
        opus_pcm_queue_header_sha256=(Get-FileHash "$taskRoot/esp8266/rtos-sdk-native/main/audio_pcm_queue.h" -Algorithm SHA256).Hash
        opus_mathops_header_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/mathops.h).Hash
        opus_rotation_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/opus_rotation_lx106.S).Hash
        opus_rotation_header_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/opus_rotation.h).Hash
        opus_vq_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/vq.c).Hash
        opus_rotation_implementation='stride1-register-carry-v2'
        opus_celt_bands_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/bands.c).Hash
        opus_profile_stage=$OpusProfileStage
        opus_fir_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/silk/resampler_private_IIR_FIR.c).Hash
        opus_fir_table_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/silk/resampler_rom.c).Hash
        opus_fir_helper_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/opus_fir_word.h).Hash
        pdm32_iram=[bool]$Pdm32Iram
        pdm32_batch=[bool]$Pdm32Batch
        pdm32_loan_words=$Pdm32LoanWords
        sdk_rx_diag=[bool]$SdkRxDiag
        sdk_rx_diag_manifest_sha256=$(if ($SdkRxDiag) { (Get-FileHash "$taskArtifact/sdk-rxdiag-manifest.json").Hash } else { $null })
        opus_max_packet_ms=$(if ($taskOpusEnabled) { 120 } else { 0 })
        opus_max_coded_frame_ms=$(if ($taskOpusEnabled) { 20 } else { 0 })
        opus_block_output=[bool]$taskOpusEnabled
        opus_adapter_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/native_opus.c).Hash
        opus_decoder_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/opus_decoder/upstream/src/opus_decoder.c).Hash
        tone_test=$false
        web_profile=$false
        memory_profile=[bool]$MemoryProfile
        spiffs_log=[bool]$SpiffsLog
        spiffs_log_http=[bool]$SpiffsLogHttp
        spiffs_cache=[bool]$taskSpiffsCache.enabled
        spiffs_write_cache=[bool]$taskSpiffsCache.write_enabled
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
        stream_read_wait_ms=0; stream_idle_timeout_ms=$StreamIdleTimeoutMs
        stream_input_bytes=4096; stream_prefill_ms=1000
        codec_bridge_sha256=(Get-FileHash esp8266/rtos-sdk-native/components/helix_codecs/codec_bridge.cpp).Hash
        stream_input_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_input_buffer.h).Hash
        stream_refill_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/stream_input_refill.inc).Hash
        network_benchmark=$false
        cpu_mhz=160; flash='QIO40'; output='I2S PDM32 SLC-DMA'; data_gpio=3; dma_buffers=2; dma_words_per_buffer=$DmaBufferWords
        dma_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/esp8266_nodac_i2s.c).Hash
        dma_header_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/esp8266_nodac_i2s.h).Hash
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
