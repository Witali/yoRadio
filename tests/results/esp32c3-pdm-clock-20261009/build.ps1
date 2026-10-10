$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$root = '.build/c3-pdm-clock-20261009'
foreach ($mode in @('integer','fractional')) {
    $variant = "r9a97-pdm-$mode"
    $build = "build-idf-6.1-$variant"
    $directory = "idf/esp32c3-oled-native/$build"
    New-Item -ItemType Directory -Force "$root/$mode", $directory | Out-Null
    if (Test-Path "$directory/sdkconfig") { throw "Do not overwrite prior $mode experiment" }
    $base = Get-Content firmware/development/esp32c3-idf-6.1-r9a97-flash-qio80/sdkconfig -Raw
    $fractional = if ($mode -eq 'fractional') { 'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y' } else { '# CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK is not set' }
    [IO.File]::WriteAllText([IO.Path]::GetFullPath("$directory/sdkconfig"), $base.TrimEnd() + "`nCONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS=y`n$fractional`n", [Text.UTF8Encoding]::new($false))
    Write-Output "BUILD $mode"
    & ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', "PROJECT_VER=idf61-pdm-$mode", '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=ON', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build') *> "$root/$mode/build.log"
    if ($LASTEXITCODE -ne 0) { throw "PDM $mode build failed" }
    & $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
    if ($LASTEXITCODE -ne 0) { throw "PDM $mode artifact export failed" }
    Copy-Item -LiteralPath "$directory/bootloader/bootloader.bin" -Destination "firmware/development/esp32c3-idf-6.1-$variant/bootloader.bin"
    Write-Output "SAVED $mode"
}
