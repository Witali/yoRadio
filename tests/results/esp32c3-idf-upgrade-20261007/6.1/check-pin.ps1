$ErrorActionPreference = 'Stop'
$arguments = @{
    DependencyRoot = 'C:/Work/yoRadio/.idf'
    BuildDirectory = 'build-idf-6.1-pin-check'
    Sdkconfig = 'build-idf-6.1-pin-check/sdkconfig'
    IdfArguments = @('--version')
}
& ./idf/esp32c3-oled-native/build.ps1 @arguments
