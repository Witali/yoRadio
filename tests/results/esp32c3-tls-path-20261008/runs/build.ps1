$Mode = 'dynamic'
$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
$variant = "r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tlspath"
$build = "build-idf-6.1-$variant"
$tls = if ($Mode -eq 'dynamic') { 'sdkconfig.tls-dynamic.defaults' } else { [IO.Path]::GetFullPath('.build/c3-tls-records-20261007/static.defaults') }
$defaults = @('sdkconfig.defaults', 'sdkconfig.tcp-pcb-pool.defaults',
    [IO.Path]::GetFullPath('.build/c3-memory-20261007/network-base.defaults'),
    [IO.Path]::GetFullPath('.build/c3-memory-20261007/rx-copy.defaults'), $tls,
    'sdkconfig.cpu-profile.defaults', 'sdkconfig.cpu-profile-http.defaults',
    [IO.Path]::GetFullPath('.build/c3-tls-records-20261007/lab-ca.defaults'),
    'sdkconfig.tcp-rx-six-segments.defaults','sdkconfig.adaptive-input.defaults','sdkconfig.tls-large-reserve.defaults','sdkconfig.tls-rx-reserve.defaults','sdkconfig.staged-dma-profile.defaults','sdkconfig.tls-path-profile.defaults')
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults $defaults -IdfArguments @('-D', "PROJECT_VER=idf61-9a97-tlspath", '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
if ($LASTEXITCODE -ne 0) { throw 'Window build failed' }
& $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
if ($LASTEXITCODE -ne 0) { throw 'Window export failed' }
& $py -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build "idf/esp32c3-oled-native/$build" --objdump $objdump --output ".build/c3-tls-path-20261008/verify-aac.json"
if ($LASTEXITCODE -ne 0) { throw 'Window AAC audit failed' }

& $py -X utf8 tools/esp32c3_tests/verify_http_link.py --sdkconfig "idf/esp32c3-oled-native/$build/sdkconfig" --elf "idf/esp32c3-oled-native/$build/yoradio_esp32c3_oled_native.elf" --objdump $objdump --output ".build/c3-tls-path-20261008/verify-http.json"
if ($LASTEXITCODE -ne 0) { throw "HTTP linked call audit failed" }

& $py -X utf8 tools/esp32c3_tests/verify_adaptive_input_link.py --elf "idf/esp32c3-oled-native/$build/yoradio_esp32c3_oled_native.elf" --sdkconfig "idf/esp32c3-oled-native/$build/sdkconfig" --objdump $objdump --tls-rx-object "idf/esp32c3-oled-native/$build/esp-idf/mbedtls/mbedtls/library/CMakeFiles/mbedtls.dir/__/__/__/__/yoradio_mbedtls/esp_mbedtls_dynamic_impl.c.obj" --output ".build/c3-tls-path-20261008/verify-reserve.json"
if ($LASTEXITCODE -ne 0) { throw "RX reserve linked audit failed" }

