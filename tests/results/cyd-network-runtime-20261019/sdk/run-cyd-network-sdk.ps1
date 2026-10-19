param([switch]$Child)
$ErrorActionPreference='Stop'
if ($Child) {
    & ./idf/esp32-cyd2usb-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory build-c3-transfer -Sdkconfig build-c3-transfer/sdkconfig -IdfArguments @('-D','IDF_TOOLCHAIN=gcc','__idf_main')
    exit $LASTEXITCODE
}
$base=Join-Path (Get-Location) '.build/cyd-network-sdk'
$job=Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child') -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$base.out.log" -RedirectStandardError "$base.err.log"
if ($job.ExitCode -ne 0) {
    Get-Content "$base.out.log" -Tail 25
    Get-Content "$base.err.log" -Tail 8
    exit $job.ExitCode
}
Get-Content "$base.out.log" -Tail 6
exit 0
