param(
    [ValidateSet('pdm','continuous','legacy','custom-pdm','custom-continuous','custom-legacy')][string]$Backend,
    [switch]$Child
)
$ErrorActionPreference = 'Stop'
if ($Child) {
    $env:PYTHONUTF8 = '1'
    $n5GitConfigCount = if ($env:GIT_CONFIG_COUNT) { [int]$env:GIT_CONFIG_COUNT } else { 0 }
    Set-Item -Path "Env:GIT_CONFIG_KEY_$n5GitConfigCount" -Value 'core.longpaths'
    Set-Item -Path "Env:GIT_CONFIG_VALUE_$n5GitConfigCount" -Value 'true'
    $env:GIT_CONFIG_COUNT = ($n5GitConfigCount + 1).ToString()
    $custom = $Backend.StartsWith('custom-')
    $audioBackend = if ($custom) { $Backend.Substring(7) } else { $Backend }
    $variant = "esp32-cyd2usb-native-output-telemetry-$audioBackend"
    $evidence = @('tests/results/cyd-output-telemetry-20261020/README.md','tests/results/cyd-http-request-buffer-20261020/README.md')
    if ($custom) {
        $variant = "esp32-cyd2usb-native-output-telemetry-custom-flac-$audioBackend"
        $evidence += 'tests/results/cyd-flac-runtime-20261019/README.md'
        if ($audioBackend -eq 'pdm') {
            $build = [IO.Path]::GetFullPath((Join-Path (Get-Location) '.build/cyd-flac-runtime-sdk-custom'))
        } else {
            $build = [IO.Path]::GetFullPath((Join-Path (Get-Location) "idf/esp32-cyd2usb-native/build-custom-flac-network-settings-$audioBackend"))
            if (-not (Test-Path -LiteralPath $build)) {
                New-Item -ItemType Directory -Path $build | Out-Null
                $seedPath = Join-Path (Get-Location) "firmware/development/esp32-cyd2usb-native-network-power-$audioBackend/sdkconfig"
                $seed = [IO.File]::ReadAllText($seedPath)
                if (-not $seed.Contains('CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF=y') -or
                    -not $seed.Contains('# CONFIG_YORADIO_FLAC_DECODER_CUSTOM is not set')) {
                    throw 'Unexpected vendor FLAC seed'
                }
                $seed = $seed.Replace('CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF=y', '# CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF is not set')
                $seed = $seed.Replace('# CONFIG_YORADIO_FLAC_DECODER_CUSTOM is not set', 'CONFIG_YORADIO_FLAC_DECODER_CUSTOM=y')
                [IO.File]::WriteAllText((Join-Path $build 'sdkconfig'), $seed, [Text.UTF8Encoding]::new($false))
            }
        }
    } else {
        $build = switch ($audioBackend) { 'pdm' { 'build-c3-transfer' } 'continuous' { 'build-c3-transfer-dac' } 'legacy' { 'build-c3-transfer-legacy' } }
    }
    & ./idf/esp32-cyd2usb-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -AudioBackend $audioBackend -Variant $variant -Evidence $evidence
    exit $LASTEXITCODE
}
$n5LogBase = Join-Path (Get-Location) ".build/output-telemetry-production-$Backend"
$n5Arguments = @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Backend',$Backend)
$n5Process = Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $n5Arguments -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$n5LogBase.out.log" -RedirectStandardError "$n5LogBase.err.log"
if ($n5Process.ExitCode -ne 0) {
    Get-Content -LiteralPath "$n5LogBase.out.log" -Tail 12
    Get-Content -LiteralPath "$n5LogBase.err.log" -Tail 12
    exit $n5Process.ExitCode
}
Get-Content -LiteralPath "$n5LogBase.out.log" -Tail 5
exit 0
