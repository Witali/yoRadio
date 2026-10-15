$ErrorActionPreference = 'Stop'
$prepared = Join-Path $PWD '.build/c3-raw-tail-quiet-20261015/promotion-candidates/idf/esp32c3-oled-native/sdkconfig.radio-tested.defaults'
& ./idf/esp32c3-oled-native/build.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf `
    -BuildDirectory build-profile-preflight-20261015 `
    -Sdkconfig build-profile-preflight-20261015/sdkconfig `
    -SdkconfigDefaults @('sdkconfig.defaults', 'sdkconfig.production.defaults', $prepared) `
    -IdfArguments @('reconfigure')
exit $LASTEXITCODE
