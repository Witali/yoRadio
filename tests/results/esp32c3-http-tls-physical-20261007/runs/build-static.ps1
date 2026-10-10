$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
$build = 'build-idf-6.1-compact-icy-quiet-eof'
$taskBuildPath = Join-Path 'idf/esp32c3-oled-native' $build
New-Item -ItemType Directory -Path $taskBuildPath -Force | Out-Null
Copy-Item -LiteralPath 'firmware/development/esp32c3-idf-6.1-compact-icy-quiet/sdkconfig' -Destination (Join-Path $taskBuildPath 'sdkconfig')
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -IdfArguments @('-D','PROJECT_VER=compact-icy-quiet-eof','build')
if ($LASTEXITCODE -ne 0) { throw 'Static TLS build failed' }
& $py -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant compact-icy-quiet-eof
if ($LASTEXITCODE -ne 0) { throw 'Static TLS export failed' }
& $py -X utf8 tools/esp32c3_tests/verify_http_link.py --sdkconfig "$taskBuildPath/sdkconfig" --elf "$taskBuildPath/yoradio_esp32c3_oled_native.elf" --objdump $objdump --output .build/c3-rfc-qualification-20261007/verify-http-static.json
if ($LASTEXITCODE -ne 0) { throw 'Static TLS linked audit failed' }
& $py -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build $taskBuildPath --objdump $objdump --output .build/c3-rfc-qualification-20261007/verify-aac-static.json
if ($LASTEXITCODE -ne 0) { throw 'Static TLS AAC audit failed' }
