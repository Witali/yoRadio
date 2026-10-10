$ErrorActionPreference = 'Stop'
$buildName = 'build-idf-6.1-head9a97-qemu'
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $buildName -Sdkconfig "$buildName/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu.defaults',[IO.Path]::GetFullPath('.build/idf-upgrade/qemu-compact.defaults')) -IdfArguments @('-D','CMAKE_JOB_POOLS=compile_limit=2','-D','CMAKE_JOB_POOL_COMPILE=compile_limit','-D','CMAKE_JOB_POOL_LINK=compile_limit','build')
if ($LASTEXITCODE -ne 0) { throw 'QEMU firmware build failed' }
