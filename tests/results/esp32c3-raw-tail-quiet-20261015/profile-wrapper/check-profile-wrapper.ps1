param([ValidateSet('fresh','cached')][string]$Mode)
$ErrorActionPreference = 'Stop'
$directory = "build-profile-wrapper-$Mode-20261015"
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf `
    -BuildDirectory $directory `
    -Sdkconfig "$directory/sdkconfig" `
    -TestedRadioProfile -NoFirmwareExport `
    -IdfArguments @('reconfigure')
exit $LASTEXITCODE
