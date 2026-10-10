param([Parameter(Mandatory)][string]$Version)
$ErrorActionPreference = 'Stop'
$arguments = @{
    DependencyRoot = 'C:/Work/yoRadio/.idf'
    BuildDirectory = "build-idf-$Version-profile"
    Sdkconfig = "build-idf-$Version-profile/sdkconfig"
    SdkconfigDefaults = @('sdkconfig.defaults', 'sdkconfig.cpu-profile.defaults', 'sdkconfig.cpu-profile-http.defaults')
    IdfArguments = @('build')
}
& ./idf/esp32c3-oled-native/build.ps1 @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$target = "firmware/development/esp32c3-idf-$Version-profile"
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item "idf/esp32c3-oled-native/build-idf-$Version-profile/yoradio_esp32c3_oled_native.bin" "$target/app.bin"
Copy-Item "idf/esp32c3-oled-native/build-idf-$Version-profile/sdkconfig" "$target/sdkconfig"
