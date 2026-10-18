param(
    [ValidateSet('c3','cyd')][string]$Board,
    [string]$Build,
    [string]$Log,
    [ValidateSet('clang','gcc')][string]$Toolchain='clang',
    [switch]$OtaOnly,
    [switch]$Child
)
$ErrorActionPreference='Stop'
if ($Child) {
    $script=if($Board -eq 'c3'){'./idf/esp32c3-oled-native/build.ps1'}else{'./idf/esp32-cyd2usb-native/build.ps1'}
    $targets=@('__idf_custom_flac')
    & $script -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $Build -Sdkconfig "$Build/sdkconfig" -IdfArguments (@('-D',"IDF_TOOLCHAIN=$Toolchain") + $targets)
    exit $LASTEXITCODE
}
$base=[IO.Path]::GetFullPath((Join-Path (Get-Location) ".build/$Log"))
$childArgs=@('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Board',$Board,'-Build',$Build,'-Toolchain',$Toolchain)
if ($OtaOnly) { $childArgs+='-OtaOnly' }
$job=Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $childArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$base.out.log" -RedirectStandardError "$base.err.log"
if ($job.ExitCode -ne 0) {
    Get-Content -LiteralPath "$base.out.log" -Tail 18
    Get-Content -LiteralPath "$base.err.log" -Tail 18
    exit $job.ExitCode
}
Get-Content -LiteralPath "$base.out.log" -Tail 6
exit 0

