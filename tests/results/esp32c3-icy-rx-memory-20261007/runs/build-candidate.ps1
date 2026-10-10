$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
foreach ($variant in @('memory-icy-rxcopy-profile', 'memory-icy-rxcopy-quiet')) {
    $build = "build-idf-6.1-$variant"
    $defaults = @('sdkconfig.defaults', 'sdkconfig.tcp-pcb-pool.defaults', 'sdkconfig.tls-dynamic.defaults',
        [IO.Path]::GetFullPath('.build/c3-memory-20261007/network-base.defaults'),
        [IO.Path]::GetFullPath('.build/c3-memory-20261007/rx-copy.defaults'))
    if ($variant.EndsWith('-profile')) {
        $defaults += @('sdkconfig.cpu-profile.defaults', 'sdkconfig.cpu-profile-http.defaults')
    } else {
        $defaults += @('sdkconfig.production.defaults', [IO.Path]::GetFullPath('.build/c3-memory-20261007/quiet.defaults'))
    }
    & ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults $defaults -IdfArguments @('build')
    if ($LASTEXITCODE -ne 0) { throw "Build failed $variant" }
    & $py -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant $variant
    if ($LASTEXITCODE -ne 0) { throw "Export failed $variant" }
    & $py -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build "idf/esp32c3-oled-native/$build" --objdump $objdump --output ".build/c3-memory-20261007/verify-$variant.json"
    if ($LASTEXITCODE -ne 0) { throw "AAC audit failed $variant" }
}
