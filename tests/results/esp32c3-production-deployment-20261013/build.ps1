$ErrorActionPreference = 'Stop'
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile `
    -BuildDirectory build-production-20261013 `
    -Sdkconfig build-production-20261013/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-production-20261013 `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-prod-20261013',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4',
        '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
if ($LASTEXITCODE -ne 0) { throw 'Production build failed' }
