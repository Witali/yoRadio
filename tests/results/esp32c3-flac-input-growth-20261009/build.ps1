$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$output = '.build/c3-flac-input-growth-20261009'
foreach ($extra in @(0, 4)) {
    $variant = "r9a97-flac-input$extra"
    $build = "build-idf-6.1-$variant"
    $directory = "idf/esp32c3-oled-native/$build"
    if (Test-Path $directory) { throw 'Preserve existing build' }
    if (Test-Path "firmware/development/esp32c3-idf-6.1-$variant") { throw 'Preserve existing artifact' }
    New-Item -ItemType Directory -Force $directory | Out-Null
    $base = Get-Content firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/sdkconfig -Raw
    if ($base.Contains('CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS')) { throw 'Unexpected base profile' }
    $base += "`nCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=$extra`n"
    [IO.File]::WriteAllText([IO.Path]::GetFullPath("$directory/sdkconfig"), $base, [Text.UTF8Encoding]::new($false))
    & ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', "PROJECT_VER=idf61-flac-input$extra", '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=ON', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build') *> "$output/build$extra.log"
    if ($LASTEXITCODE -ne 0) { throw "Build $extra failed" }
    & $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
    if ($LASTEXITCODE -ne 0) { throw 'Artifact export failed' }
    Copy-Item -LiteralPath "$directory/bootloader/bootloader.bin" -Destination "firmware/development/esp32c3-idf-6.1-$variant/bootloader.bin"
    Write-Output "SAVED input-extra-$extra candidate"
}
