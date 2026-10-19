param([switch]$Child,[ValidateSet('custom','vendor')][string]$Mode='custom')
$ErrorActionPreference='Stop'
$taskRoot=(Get-Location).Path
$build=Join-Path $taskRoot ".build/cyd-flac-runtime-sdk-$Mode"
if($Child) {
  $target=if($Mode -eq 'custom'){'__idf_custom_flac'}else{'reconfigure'}
  & ./idf/esp32-cyd2usb-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -IdfArguments @('-D','IDF_TOOLCHAIN=gcc',$target)
  exit $LASTEXITCODE
}
New-Item -ItemType Directory -Path $build -Force | Out-Null
$config=Get-Content -LiteralPath ./idf/esp32-cyd2usb-native/build-c3-transfer/sdkconfig -Raw
$config=$config -replace '(?m)^CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF=y\r?\n',''
$config=$config -replace '(?m)^# CONFIG_YORADIO_FLAC_DECODER_CUSTOM is not set\r?\n',''
if($Mode -eq 'custom') { $config += "`nCONFIG_YORADIO_FLAC_DECODER_CUSTOM=y`n# CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF is not set`n"
}
[IO.File]::WriteAllText((Join-Path $build 'sdkconfig'),$config,[Text.UTF8Encoding]::new($false))
$job=Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Mode',$Mode) -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$build/build.out.log" -RedirectStandardError "$build/build.err.log"
Get-Content "$build/build.out.log" -Tail 7
Get-Content "$build/build.err.log" -Tail 7
exit $job.ExitCode

