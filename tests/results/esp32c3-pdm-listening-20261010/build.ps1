$ErrorActionPreference = 'Stop'
$taskRoot = Join-Path (Get-Location) '.build/c3-pdm-listening-20261010'
$taskProject = Join-Path $taskRoot 'source/idf/esp32c3-oled-native'
$taskBuild = Join-Path $taskRoot 'build'
& (Join-Path $taskProject 'build.ps1') -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $taskBuild -Sdkconfig (Join-Path $taskBuild 'sdkconfig') -IdfArguments @('-D', 'PROJECT_VER=idf61-listen48-8c1f2d', '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=OFF', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build')
if ($LASTEXITCODE -ne 0) { throw 'Listening firmware build failed' }
$taskFirmware = Join-Path (Get-Location) 'firmware/development/esp32c3-idf61-listen-48k'
New-Item -ItemType Directory -Force -Path $taskFirmware | Out-Null
Copy-Item -LiteralPath (Join-Path $taskBuild 'yoradio_esp32c3_oled_native.bin') -Destination (Join-Path $taskFirmware 'app.bin')
Copy-Item -LiteralPath (Join-Path $taskBuild 'sdkconfig') -Destination (Join-Path $taskFirmware 'sdkconfig')
Write-Host "Listening application saved to $taskFirmware/app.bin"
