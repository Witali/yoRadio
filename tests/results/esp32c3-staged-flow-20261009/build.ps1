$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$variant = 'r9a97-staged-flow'
$build = "build-idf-6.1-$variant"
$directory = "idf/esp32c3-oled-native/$build"
$output = '.build/c3-staged-flow-20261009'
New-Item -ItemType Directory -Force $directory | Out-Null
if (Test-Path "$directory/sdkconfig") { throw 'Preserve existing build' }
$base = Get-Content firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail/sdkconfig -Raw
if ($base.Contains('CONFIG_YORADIO_PIPELINE_PROFILE')) { throw 'Unexpected base profile' }
$base += "`nCONFIG_YORADIO_PIPELINE_PROFILE=y`n"
[IO.File]::WriteAllText([IO.Path]::GetFullPath("$directory/sdkconfig"), $base, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', 'PROJECT_VER=idf61-staged-flow', '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=ON', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build') *> "$output/build.log"
if ($LASTEXITCODE -ne 0) { throw 'Staged-flow build failed' }
& $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
if ($LASTEXITCODE -ne 0) { throw 'Artifact export failed' }
Copy-Item -LiteralPath "$directory/bootloader/bootloader.bin" -Destination "firmware/development/esp32c3-idf-6.1-$variant/bootloader.bin"
Write-Output 'SAVED staged-flow candidate'
