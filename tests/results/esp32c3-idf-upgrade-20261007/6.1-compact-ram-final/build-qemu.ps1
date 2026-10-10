param([Parameter(Mandatory)][string]$Version, [ValidateSet('vorbis','aac')][string]$Codec)
$ErrorActionPreference = 'Stop'
$defaults = @('sdkconfig.defaults','sdkconfig.qemu.defaults')
if ($Codec -eq 'vorbis') {
    $defaults += @('sdkconfig.qemu-vorbis-lifecycle.defaults','sdkconfig.qemu-vorbis-repair.defaults')
} else {
    $overlay = [IO.Path]::GetFullPath('.build/idf-upgrade/qemu-aac.defaults')
    [IO.File]::WriteAllText($overlay, "CONFIG_YORADIO_QEMU_AAC_TEST=y`nCONFIG_YORADIO_QEMU_AAC_PROFILE=y`n# CONFIG_MBEDTLS_HARDWARE_SHA is not set`n")
    $defaults += $overlay
}
$parameters = @{
    DependencyRoot = 'C:/Work/yoRadio/.idf'
    BuildDirectory = "build-idf-$Version-qemu-$Codec"
    Sdkconfig = "build-idf-$Version-qemu-$Codec/sdkconfig"
    SdkconfigDefaults = $defaults
    IdfArguments = @('build')
}
& ./idf/esp32c3-oled-native/build.ps1 @parameters
exit $LASTEXITCODE
