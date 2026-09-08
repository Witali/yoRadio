param(
    [ValidateSet(1, 2, 3, 4, 5)][int]$Sweep = 1,
    [ValidateRange(1, 100)][int]$Rounds = 10,
    [string]$SourceUrl = 'http://192.168.100.253:8765',
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$taskVariant = "esp8266-network-sweep$Sweep-r$Rounds"
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
    if ($SourceUrl -notmatch '^http://[A-Za-z0-9.:-]+$') { throw 'Use the LAN HTTP origin without a path' }
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$taskRoot/.build/esp8266-tools"
    $taskCompiler = "$taskRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin"
    $env:PATH = "$taskRoot/.build/esp8266-python/Scripts;$taskCompiler;$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0;$taskRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$env:PATH"
    New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
    $taskDefaults = (Get-Content esp8266/rtos-sdk-native/sdkconfig.defaults -Raw) + "`n" +
        (Get-Content tools/esp8266_audio_profile/network_cpu.defaults -Raw)
    [IO.File]::WriteAllText("$taskBuild/combined.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    Write-Output "Configuring $taskVariant (diagnostic only; no flashing or serial reset)"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
        '-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
        "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/combined.defaults",
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK=ON',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK_CPU_ONLY=ON',
        '-DYORADIO_ESP8266_NETWORK_BENCHMARK_BULK_ONLY=OFF',
        "-DYORADIO_ESP8266_NETWORK_BENCHMARK_URL=$SourceUrl",
        "-DYORADIO_ESP8266_NETWORK_BENCHMARK_SWEEP=$Sweep",
        "-DYORADIO_ESP8266_NETWORK_BENCHMARK_ROUNDS=$Rounds",
        '-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=OFF',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF',
        '-DYORADIO_ESP8266_AUDIO_PROFILE=OFF', '-DYORADIO_ESP8266_MEMORY_PROFILE=OFF',
        '-DYORADIO_ESP8266_WEB_PROFILE=OFF', '-DYORADIO_ESP8266_AUDIO_TRACE=OFF',
        '-DYORADIO_ESP8266_KARADIO_PIPELINE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    foreach ($taskRequired in @('CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER=y',
        'CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y', 'CONFIG_LOG_DEFAULT_LEVEL=3',
        'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y',
        'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y', 'CONFIG_YORADIO_HELIX_MP3_SSO=y',
        'CONFIG_YORADIO_HELIX_AAC=y', 'CONFIG_YORADIO_AUDIO_MONO=y')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired" }
    }
    Write-Output "Building $taskVariant; $Rounds attempts per source/variant, 20 seconds each"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
    $taskHashes = [ordered]@{}
    foreach ($taskFile in @('audio_service.c', 'network_benchmark.inc', 'stream_read_wait.h', 'web_upload.c')) {
        $taskHashes[$taskFile] = (Get-FileHash "esp8266/rtos-sdk-native/main/$taskFile").Hash
    }
    $taskHashes['httpd_txrx.c'] = (Get-FileHash 'esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_txrx.c').Hash
    $taskManifest = [ordered]@{
        purpose='Diagnostic network sweep; retained decoder allocation and I2S DMA; not production'
        built_utc=[DateTime]::UtcNow.ToString('o'); source_revision=(git rev-parse HEAD)
        source_files_sha256=$taskHashes
        sweep=$Sweep; rounds=$Rounds; window_seconds=20; server=$SourceUrl
        app_sha256=(Get-FileHash "$taskArtifact/app.bin").Hash
        bytes=(Get-Item "$taskArtifact/app.bin").Length
        config_sha256=(Get-FileHash "$taskArtifact/sdkconfig").Hash
        cpu_mhz=160; flash='QIO40'; playback_cases=($Sweep -ge 4)
        serial_rx_commands=$false; auto_flash=$false
    }
    if ($taskManifest.bytes -gt 0xf0000) { throw 'App exceeds OTA slot' }
    $taskManifest | ConvertTo-Json -Depth 4 | Out-File "$taskArtifact/manifest.json" -Encoding utf8
    Write-Output "Saved $taskArtifact/app.bin ($($taskManifest.bytes) bytes). Upload via authorized OTA separately."
} finally {
    $env:PATH=$taskSavedPath; $env:IDF_PATH=$taskSavedIdf; $env:IDF_TOOLS_PATH=$taskSavedTools
    Pop-Location
}
