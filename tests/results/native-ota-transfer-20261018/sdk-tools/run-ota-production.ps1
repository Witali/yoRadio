param(
    [ValidateSet('c3','pdm','continuous','legacy')][string]$Backend,
    [switch]$Child
)
$ErrorActionPreference='Stop'
if ($Child) {
    if ($Backend -eq 'c3') {
        & ./idf/esp32c3-oled-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile -BuildDirectory build-c3-transfer -Sdkconfig build-c3-transfer/sdkconfig -FirmwareOutputDirectory firmware/development/esp32c3-oled-native-ota-transfer
    } else {
        $build = switch ($Backend) {'pdm' {'build-c3-transfer'} 'continuous' {'build-c3-transfer-dac'} 'legacy' {'build-c3-transfer-legacy'}}
        & ./idf/esp32-cyd2usb-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -AudioBackend $Backend -Variant "esp32-cyd2usb-native-ota-transfer-$Backend" -Evidence @('tests/results/native-ota-transfer-20261018/HOST.md')
    }
    exit $LASTEXITCODE
}
$base=[IO.Path]::GetFullPath((Join-Path (Get-Location) ".build/ota-production-$Backend"))
$childArgs=@('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Backend',$Backend)
$job=Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $childArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$base.out.log" -RedirectStandardError "$base.err.log"
if ($job.ExitCode -ne 0) {
    Get-Content -LiteralPath "$base.out.log" -Tail 20
    Get-Content -LiteralPath "$base.err.log" -Tail 20
    exit $job.ExitCode
}
Get-Content -LiteralPath "$base.out.log" -Tail 8
exit 0
