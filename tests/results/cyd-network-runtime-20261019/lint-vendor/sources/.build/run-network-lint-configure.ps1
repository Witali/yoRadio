param([ValidateSet('vendor','custom')][string]$Mode, [switch]$Child)
$ErrorActionPreference = 'Stop'
$build = "build-lint-network-$Mode-final"
if ($Child) {
    & ./idf/esp32-cyd2usb-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -IdfArguments @('-D','IDF_TOOLCHAIN=clang','reconfigure')
    exit $LASTEXITCODE
}
$directory = Join-Path (Get-Location) "idf/esp32-cyd2usb-native/$build"
if (Test-Path -LiteralPath $directory) { throw "Preserve earlier configure: $directory" }
New-Item -ItemType Directory -Path $directory | Out-Null
$seed = [IO.File]::ReadAllText((Join-Path (Get-Location) 'idf/esp32-cyd2usb-native/build-c3-transfer/sdkconfig'))
if ($Mode -eq 'custom') {
    $seed = $seed.Replace('CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF=y', '# CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF is not set')
    $seed = $seed.Replace('# CONFIG_YORADIO_FLAC_DECODER_CUSTOM is not set', 'CONFIG_YORADIO_FLAC_DECODER_CUSTOM=y')
}
[IO.File]::WriteAllText((Join-Path $directory 'sdkconfig'), $seed, [Text.UTF8Encoding]::new($false))
$base = Join-Path (Get-Location) ".build/network-lint-configure-$Mode"
$childArgs = @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Mode',$Mode)
$job = Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $childArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$base.out.log" -RedirectStandardError "$base.err.log"
if ($job.ExitCode -ne 0) {
    Get-Content -LiteralPath "$base.out.log" -Tail 18
    Get-Content -LiteralPath "$base.err.log" -Tail 18
    exit $job.ExitCode
}
Get-Content -LiteralPath "$base.out.log" -Tail 6
exit 0
