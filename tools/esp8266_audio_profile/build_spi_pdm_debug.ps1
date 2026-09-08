param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [switch]$ToneTest,
    [switch]$WebProfile,
    [switch]$NoPlaylistGzip
)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
if ($ToneTest -and $NoPlaylistGzip) { throw 'Use NoPlaylistGzip with the normal-radio profile' }
$taskVariant = if ($ToneTest) { 'esp8266-spi-pdm-tone' } elseif ($NoPlaylistGzip) { 'esp8266-spi-pdm-raw-playlist' } else { 'esp8266-spi-pdm-debug' }
if ($WebProfile) { $taskVariant += '-web-trace' }
$taskToneFlag = if ($ToneTest) { 'ON' } else { 'OFF' }
$taskWebFlag = if ($WebProfile) { 'ON' } else { 'OFF' }
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
    # Mechanically overlay only these audio choices; inherit current RAM,
    # codecs, HTTP, partition table, clocks and logging from board defaults.
    $taskDefaults = Get-Content esp8266/rtos-sdk-native/sdkconfig.defaults -Raw
    if ($NoPlaylistGzip) {
        $taskDefaults = $taskDefaults.Replace('CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y', 'CONFIG_YORADIO_PLAYLIST_WEB_GZIP=n')
    }
    foreach ($taskLine in Get-Content esp8266/rtos-sdk-native/sdkconfig.spi-pdm-debug.defaults) {
        if ($taskLine -match '^(CONFIG_[A-Z0-9_]+)=') {
            $taskPattern = '(?m)^' + $Matches[1] + '=.*$'
            if ($taskDefaults -notmatch $taskPattern) { throw "Overlay key missing from canonical defaults: $taskLine" }
            $taskDefaults = [regex]::Replace($taskDefaults, $taskPattern, $taskLine)
        }
    }
    [IO.File]::WriteAllText("$taskBuild/spi.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    Write-Output "Configuring $taskVariant on GPIO13/D7 (no flashing)"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
        '-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
        "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/spi.defaults",
        '-DYORADIO_ESP8266_FIXED_I2S=OFF', '-DYORADIO_ESP8266_SPI_PDM_FAST_ISR=ON',
        "-DYORADIO_ESP8266_WEB_PROFILE=$taskWebFlag",
        "-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=$taskToneFlag", '-DYORADIO_ESP8266_OUTPUT_COMPARE=OFF',
        "-DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=$taskToneFlag", '-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF',
        '-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF', '-DYORADIO_ESP8266_AUDIO_PROFILE=OFF',
        '-DYORADIO_ESP8266_AUDIO_TRACE=OFF', '-DYORADIO_ESP8266_MEMORY_PROFILE=OFF',
        '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    foreach ($taskRequired in @('CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM=y', 'CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y', 'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Wrong cached profile: $taskRequired" }
    }
    if ($taskConfig -match '(?m)^CONFIG_YORADIO_AUDIO_OUTPUT_I2S_(PDM|RCPDM|PCM)=y') { throw 'I2S must be disabled' }
    $taskGzipEnabled = $taskConfig -match '(?m)^CONFIG_YORADIO_PLAYLIST_WEB_GZIP=y\r?$'
    if ($taskGzipEnabled -eq [bool]$NoPlaylistGzip) { throw 'Wrong cached playlist compression choice' }
    Write-Output "Building $taskVariant, CPU160, QIO40"
    Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
    $taskManifest = [ordered]@{
        purpose=if ($ToneTest) { '1 kHz sine, 500 ms on/off, no Wi-Fi or decoder; build does not flash' } else { 'Temporary normal radio SPI-PDM debug profile; build does not flash' }
        tone_test=[bool]$ToneTest
        web_profile=[bool]$WebProfile
        playlist_web_gzip=[bool]$taskGzipEnabled
        built_utc=[DateTime]::UtcNow.ToString('o'); source_revision=(git rev-parse HEAD)
        app_sha256=(Get-FileHash "$taskArtifact/app.bin").Hash
        bytes=(Get-Item "$taskArtifact/app.bin").Length; app_address='0x10000'
        config_sha256=(Get-FileHash "$taskArtifact/sdkconfig").Hash
        output_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/native_audio_output.c).Hash
        web_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/web_service.c).Hash
        playlist_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/playlist_service.c).Hash
        cpu_mhz=160; flash='QIO40'; output='HSPI PDM8'; data_gpio=13; clock_gpio=14
        pcm_rate=48000; bit_rate_hz=384615; i2s=$false
        partition_layout='app0/app1 960 KiB, SPIFFS 256 KiB; flash app only'
    }
    if ($taskManifest.bytes -gt 0xf0000) { throw 'App exceeds OTA slot' }
    $taskManifest | ConvertTo-Json | Out-File "$taskArtifact/manifest.json" -Encoding utf8
    Write-Output "Saved $taskArtifact/app.bin ($($taskManifest.bytes) bytes); board default unchanged"
} finally {
    $env:PATH=$taskSavedPath; $env:IDF_PATH=$taskSavedIdf; $env:IDF_TOOLS_PATH=$taskSavedTools
    Pop-Location
}
