param(
    [string]$SdkPath = '.worktree/esp8266-native-port/.build/esp8266-rtos-sdk',
    [string]$BaseConfig = '.build/esp8266-pcm32/sdkconfig'
)
$ErrorActionPreference = 'Stop'
$radioRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.Replace('\', '/')
$previousPath = $env:PATH
Push-Location $radioRoot
try {
    $env:IDF_PATH = (Resolve-Path $SdkPath).Path
    $env:IDF_TOOLS_PATH = Join-Path $radioRoot '.build/esp8266-tools'
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PATH = "$radioRoot/.build/esp8266-python/Scripts;$radioRoot/.build/esp8266-tools/tools/mconf/v4.6.0.0-idf-20190628/mconf-v4.6.0.0-idf-20190628-win32;$radioRoot/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin;$radioRoot/.build/esp8266-tools/tools/ninja/1.9.0;$env:PATH"
    $cmake = Join-Path $radioRoot '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe'
    $ninja = Join-Path $radioRoot '.build/esp8266-tools/tools/ninja/1.9.0/ninja.exe'
    New-Item -ItemType Directory -Path '.build/output-compare-results' -Force | Out-Null
    foreach ($mode in @('pdm', 'rcpdm')) {
        $build = ".build/output-compare-$mode"
        if (-not (Test-Path "$build/sdkconfig")) {
            New-Item -ItemType Directory -Path $build -Force | Out-Null
            $seed = Get-Content -LiteralPath $BaseConfig -Raw
            if ($seed -notmatch '(?m)^CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y\r?$') {
                throw 'BaseConfig must be the ordinary I2S PDM32 configuration'
            }
            if ($mode -eq 'rcpdm') {
                $seed = $seed.Replace('CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y', '# CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM is not set')
                $seed = $seed.Replace('# CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM is not set', 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y')
                $seed = $seed.Replace('CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y', '# CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 is not set')
            }
            [IO.File]::WriteAllText("$radioRoot/$build/sdkconfig", $seed)
        }
        $settings = Get-Content "$build/sdkconfig"
        foreach ($required in @('CONFIG_ESP8266_DEFAULT_CPU_FREQ_160=y', 'CONFIG_ESPTOOLPY_FLASHMODE_QIO=y', 'CONFIG_ESPTOOLPY_FLASHFREQ_40M=y')) {
            if (-not ($settings -contains $required)) { throw "Comparison requires $required in $build/sdkconfig" }
        }
        if ($mode -eq 'pdm' -and -not ($settings -contains 'CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y')) {
            throw 'Comparison requires PDM32, not PDM128'
        }
        $selected = if ($mode -eq 'pdm') { 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y' } else { 'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM=y' }
        if (-not ($settings -contains $selected)) { throw "Wrong backend: $build/sdkconfig" }
        Write-Output "Building generated-PCM $mode comparison (CPU160/QIO40, no radio or Wi-Fi)"
        & $cmake -S esp8266/rtos-sdk-native -B $build -G Ninja `
            "-DSDKCONFIG=$radioRoot/$build/sdkconfig" `
            -DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=OFF -DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=OFF `
            -DYORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON -DYORADIO_ESP8266_OUTPUT_COMPARE=ON `
            -DYORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST=OFF -DYORADIO_ESP8266_AUDIO_PROFILE=OFF `
            -DYORADIO_ESP8266_AUDIO_TRACE=OFF -DYORADIO_ESP8266_MEMORY_PROFILE=OFF `
            -DYORADIO_ESP8266_HELIX_STAGE_PROFILE=OFF *> ".build/output-compare-results/$mode-configure.log"
        if ($LASTEXITCODE) { throw "Configure failed for $mode" }
        & $ninja -C $build *> ".build/output-compare-results/$mode-build.log"
        if ($LASTEXITCODE) { throw "Build failed for $mode" }
        $artifact = "firmware/development/esp8266-output-compare-$mode"
        New-Item -ItemType Directory -Path $artifact -Force | Out-Null
        Copy-Item -LiteralPath "$build/yoradio_esp8266_helix_native.bin" -Destination "$artifact/app.bin"
        Get-FileHash "$artifact/app.bin" -Algorithm SHA256 | Format-List
    }
} finally { $env:PATH = $previousPath; Pop-Location }
