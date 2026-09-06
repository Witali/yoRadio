param([string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk')
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$taskBuild = "$taskRoot/.build/rcpdm-feedback-radio"
$taskArtifact = "$taskRoot/firmware/development/esp8266-rcpdm-feedback"
$taskSavedPath = $env:PATH
$taskSavedIdf = $env:IDF_PATH
$taskSavedTools = $env:IDF_TOOLS_PATH
function Invoke-TaskBuildTool([string]$Executable, [string[]]$Arguments, [string]$Log) {
    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) { throw "Missing tool: $Executable" }
    # Windows PowerShell 5.1 wraps native stderr in ErrorRecord, even for a
    # successful SDK command printing a deprecation warning. Capture it, but
    # use the process exit code rather than stderr presence to decide failure.
    $ErrorActionPreference = 'Continue'
    & $Executable @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) { throw "Build command failed ($LASTEXITCODE): $Executable; see $Log" }
}
Push-Location $taskRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = "$taskRoot/.build/esp8266-tools"
    $taskCompiler = "$taskRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin"
    $env:PATH = "$taskRoot/.build/esp8266-python/Scripts;$taskCompiler;$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0;$taskRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$env:PATH"
    New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
    # This SDK accepts only one defaults filename, so generate a merged file.
    $taskDefaults = (Get-Content esp8266/rtos-sdk-native/sdkconfig.i2s-rcpdm.defaults -Raw) + "`n" +
                    (Get-Content esp8266/rtos-sdk-native/sdkconfig.rcpdm-feedback.defaults -Raw)
    [IO.File]::WriteAllText("$taskBuild/feedback.defaults", $taskDefaults, (New-Object Text.UTF8Encoding($false)))
    $taskCmake = "$taskRoot/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe"
    Write-Output 'Configuring experimental RC-PDM feedback radio (no flashing)'
    Invoke-TaskBuildTool $taskCmake @('-S', 'esp8266/rtos-sdk-native', '-B', $taskBuild, '-G', 'Ninja',
        "-DSDKCONFIG=$taskBuild/sdkconfig", "-DSDKCONFIG_DEFAULTS=$taskBuild/feedback.defaults",
        '-DYORADIO_ESP8266_RCPDM_VARIANT=production', '-DYORADIO_ESP8266_RCPDM_BATCH=ON',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=OFF', '-DYORADIO_ESP8266_OUTPUT_COMPARE=OFF',
        '-DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF', '-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF',
        '-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF', '-DYORADIO_ESP8266_AUDIO_PROFILE=OFF',
        '-DYORADIO_ESP8266_AUDIO_TRACE=OFF', '-DYORADIO_ESP8266_MEMORY_PROFILE=OFF',
        '-DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF') "$taskBuild/configure.log"
    $taskConfig = Get-Content "$taskBuild/sdkconfig" -Raw
    foreach ($taskRequired in @('CONFIG_YORADIO_RCPDM_FEEDBACK=y', 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y')) {
        if ($taskConfig -notmatch "(?m)^$taskRequired`r?$") { throw "Unexpected cached configuration: $taskRequired" }
    }
    Write-Output 'Building normal radio application with the experimental modulator'
    Invoke-TaskBuildTool "$taskRoot/.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe" @('-C', $taskBuild) "$taskBuild/build.log"
    Invoke-TaskBuildTool "$taskCompiler/xtensa-lx106-elf-gcc.exe" @('-std=c11', '-O3', '-Wall', '-Wextra', '-Werror',
        '-fstack-usage', '-Iesp8266/rtos-sdk-native/main', '-c', 'tests/native/rcpdm_feedback_codegen.c',
        '-o', "$taskBuild/feedback-codegen.o") "$taskBuild/codegen-build.log"
    Invoke-TaskBuildTool "$taskCompiler/xtensa-lx106-elf-nm.exe" @('-u', "$taskBuild/feedback-codegen.o") "$taskBuild/codegen-undefined.txt"
    Invoke-TaskBuildTool "$taskCompiler/xtensa-lx106-elf-objdump.exe" @('-d', "$taskBuild/feedback-codegen.o") "$taskBuild/feedback-disassembly.txt"
    Invoke-TaskBuildTool "$taskCompiler/xtensa-lx106-elf-size.exe" @('-A', "$taskBuild/yoradio_esp8266_helix_native.elf") "$taskBuild/sections.txt"
    New-Item -ItemType Directory -Path $taskArtifact -Force | Out-Null
    Copy-Item "$taskBuild/yoradio_esp8266_helix_native.bin" "$taskArtifact/app.bin"
    $taskManifest = [ordered]@{
        purpose='Normal radio with experimental RC-PDM feedback; not flashed or hardware-timed'
        source_revision=(git rev-parse HEAD); compiled_working_tree=$true
        algorithm_sha256=(Get-FileHash esp8266/rtos-sdk-native/main/rc_pdm_feedback.h).Hash
        app_sha256=(Get-FileHash "$taskArtifact/app.bin").Hash
        app_address='0x10000'; bytes=(Get-Item "$taskArtifact/app.bin").Length
        cpu_mhz=160; flash='QIO40'; pcm_rate=48000; nominal_bit_rate=1536000
        rc_shift=4; feedback_shift=0; dither='TPDF half-step'; interpolation='linear'
        modulator_state_bytes=16; dma_buffers='2 x 512 words'
    }
    $taskManifest | ConvertTo-Json | Out-File "$taskArtifact/manifest.json" -Encoding utf8
    Write-Output "Saved $taskArtifact/app.bin ($($taskManifest.bytes) bytes); no flash operation performed"
} finally {
    $env:PATH=$taskSavedPath; $env:IDF_PATH=$taskSavedIdf; $env:IDF_TOOLS_PATH=$taskSavedTools
    Pop-Location
}
