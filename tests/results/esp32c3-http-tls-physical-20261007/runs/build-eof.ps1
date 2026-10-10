$Mode = 'dynamic'
$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
$variant = "memory-icy-tlslab-rx6-eof"
$build = "build-idf-6.1-$variant"
$tls = if ($Mode -eq 'dynamic') { 'sdkconfig.tls-dynamic.defaults' } else { [IO.Path]::GetFullPath('.build/c3-tls-records-20261007/static.defaults') }
$defaults = @('sdkconfig.defaults', 'sdkconfig.tcp-pcb-pool.defaults',
    [IO.Path]::GetFullPath('.build/c3-memory-20261007/network-base.defaults'),
    [IO.Path]::GetFullPath('.build/c3-memory-20261007/rx-copy.defaults'), $tls,
    'sdkconfig.cpu-profile.defaults', 'sdkconfig.cpu-profile-http.defaults',
    [IO.Path]::GetFullPath('.build/c3-tls-records-20261007/lab-ca.defaults'),
    'sdkconfig.tcp-rx-six-segments.defaults')
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults $defaults -IdfArguments @('-D', "PROJECT_VER=tlslab-rx6-eof", 'build')
if ($LASTEXITCODE -ne 0) { throw 'Window build failed' }
& $py -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant $variant
if ($LASTEXITCODE -ne 0) { throw 'Window export failed' }
& $py -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build "idf/esp32c3-oled-native/$build" --objdump $objdump --output ".build/c3-rfc-qualification-20261007/verify-aac-eof.json"
if ($LASTEXITCODE -ne 0) { throw 'Window AAC audit failed' }

& $py -X utf8 tools/esp32c3_tests/verify_http_link.py --elf "idf/esp32c3-oled-native/$build/yoradio_esp32c3_oled_native.elf" --objdump $objdump --output ".build/c3-rfc-qualification-20261007/verify-http-eof.json"
if ($LASTEXITCODE -ne 0) { throw "HTTP linked call audit failed" }
