param(
    [ValidateSet('pdm', 'production', 'simple-u4', 'feedback')]
    [string[]]$Modes = @('pdm', 'production', 'simple-u4', 'feedback'),
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk'
)
# Isolated generated-PCM comparison. Never flashes or changes production defaults.
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$taskSavedEnv = @{}
foreach ($key in @('PATH', 'IDF_PATH', 'IDF_TOOLS_PATH', 'PYTHONIOENCODING')) {
    $taskSavedEnv[$key] = [Environment]::GetEnvironmentVariable($key)
}
function Invoke-TaskTool([string]$Exe, [string[]]$Arguments, [string]$Log) {
    if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) { throw "Missing tool: $Exe" }
    $ErrorActionPreference = 'Continue' # PS5 native stderr warnings are not failures.
    & $Exe @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) { throw "Tool failed ($LASTEXITCODE): $Log" }
}
Push-Location $taskRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$taskRoot/.build/esp8266-tools"
    $env:PYTHONIOENCODING = 'utf-8'
    $taskCompiler = "$taskRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin"
    $env:PATH = "$taskRoot/.build/esp8266-python/Scripts;$taskCompiler;$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0;$taskRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$env:PATH"
    foreach ($mode in $Modes) {
        $taskBuild = "$taskRoot/.build/rcpdm-feedback-benchmark/$mode"
        $taskArtifact = "$taskRoot/firmware/development/esp8266-rcpdm-feedback-benchmark/$mode"
        New-Item -ItemType Directory -Path $taskBuild, $taskArtifact -Force | Out-Null
        # Keep a dedicated config per variant. Generate only on first configure.
        if (-not (Test-Path "$taskBuild/sdkconfig")) {
            $seed = Get-Content esp8266/rtos-sdk-native/sdkconfig.i2s-rcpdm.defaults -Raw
            if ($mode -eq 'pdm') {
                $seed = $seed.Replace('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=n', 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y')
                $seed = $seed.Replace('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y', 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=n')
                $seed = $seed.Replace('CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=n', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y')
            }
            $feedback = if ($mode -eq 'feedback') { 'y' } else { 'n' }
            $seed += "`nCONFIG_YORADIO_RCPDM_FEEDBACK=$feedback`n"
            [IO.File]::WriteAllText("$taskBuild/defaults", $seed, (New-Object Text.UTF8Encoding($false)))
        }
        $variant = if ($mode -eq 'simple-u4') { 'simple' } else { 'production' }
        $unroll = if ($mode -eq 'simple-u4') { 'ON' } else { 'OFF' }
        Write-Output "Building ${mode}: CPU160/QIO40, -O3, 32 bits at 48 kHz, no Wi-Fi/codecs"
        Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe" @(
            '-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
            "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/defaults",
            "-DYORADIO_ESP8266_RCPDM_VARIANT=$variant", "-DYORADIO_ESP8266_RCPDM_SIMPLE_UNROLL4=$unroll",
            '-DYORADIO_ESP8266_RCPDM_BATCH=ON', '-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON',
            '-DYORADIO_ESP8266_OUTPUT_COMPARE=ON', '-DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF',
            '-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF', '-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF',
            '-DYORADIO_ESP8266_AUDIO_PROFILE=OFF', '-DYORADIO_ESP8266_AUDIO_TRACE=OFF',
            '-DYORADIO_ESP8266_MEMORY_PROFILE=OFF', '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF'
        ) "$taskBuild/configure.log"
        $config = Get-Content "$taskBuild/sdkconfig" -Raw
        $required = @('CONFIG_ESP8266_DEFAULT_CPU_FREQ_160=y', 'CONFIG_ESPTOOLPY_FLASHMODE_QIO=y',
            'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y', 'CONFIG_FREERTOS_HZ=1000')
        if ($mode -eq 'pdm') { $required += @('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y') }
        else { $required += 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y' }
        foreach ($line in $required) { if ($config -notmatch "(?m)^$line`r?$") { throw "Unexpected config: $line" } }
        if (($config -match '(?m)^CONFIG_YORADIO_RCPDM_FEEDBACK=y\r?$') -ne ($mode -eq 'feedback')) { throw 'Feedback configuration mismatch' }
        Invoke-TaskTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
        Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
        Copy-Item "$taskBuild/sdkconfig" "$taskArtifact/sdkconfig"
        $elf = "$taskBuild/yoradio_esp8266_helix_native.elf"
        Invoke-TaskTool "$taskCompiler/xtensa-lx106-elf-size.exe" @('-A', $elf) "$taskBuild/sections.txt"
        Invoke-TaskTool "$taskCompiler/xtensa-lx106-elf-nm.exe" @('-S', '--size-sort', $elf) "$taskBuild/symbols.txt"
        Invoke-TaskTool "$taskCompiler/xtensa-lx106-elf-objdump.exe" @('-d', $elf) "$taskBuild/disassembly.txt"
        $manifest = [ordered]@{
            mode=$mode; purpose='Isolated PCM packer and I2S DMA speed benchmark, not radio'
            source=(git rev-parse HEAD); compiled_working_tree=$true; batch=$true; simple_unroll4=($mode -eq 'simple-u4')
            cpu_mhz=160; flash='QIO40'; pcm_rate=48000; bits=32; bit_rate_hz=1536000
            app_address='0x10000'; bytes=(Get-Item "$taskArtifact/app.bin").Length; sha256=(Get-FileHash "$taskArtifact/app.bin").Hash
            config_sha256=(Get-FileHash "$taskArtifact/sdkconfig").Hash
            feedback_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/rc_pdm_feedback.h).Hash
            output_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/native_audio_output.c).Hash
            benchmark_source_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/audio_output_benchmark.c).Hash
        }
        $manifest | ConvertTo-Json | Out-File "$taskArtifact/manifest.json" -Encoding utf8
        Write-Output "Saved $mode ($($manifest.bytes) bytes) SHA256=$($manifest.sha256)"
    }
} finally {
    foreach ($key in $taskSavedEnv.Keys) { [Environment]::SetEnvironmentVariable($key, $taskSavedEnv[$key]) }
    Pop-Location
}
