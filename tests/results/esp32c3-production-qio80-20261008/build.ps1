$ErrorActionPreference = 'Stop'
$project = 'idf/esp32c3-oled-native'
$taskBuild = 'build-idf-6.1-r9a97-production-qio80'
$config = Join-Path (Join-Path $project $taskBuild) 'sdkconfig'
if (Test-Path -LiteralPath $config) { throw 'Use a fresh build directory; do not silently reuse configuration.' }
New-Item -ItemType Directory -Force -Path (Split-Path $config) | Out-Null
Copy-Item -LiteralPath "$project/sdkconfig.qio80.defaults" -Destination $config
& "$project/build-production.ps1" -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $taskBuild -Sdkconfig "$taskBuild/sdkconfig" -FirmwareOutputDirectory firmware/development/esp32c3-idf-6.1-r9a97-production-qio80 -IdfArguments @('-D', 'PROJECT_VER=idf61-qio80-8c1f2d2d', '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=OFF', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build')
if ($LASTEXITCODE -ne 0) { throw 'Production build failed' }
