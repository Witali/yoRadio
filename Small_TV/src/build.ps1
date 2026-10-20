[CmdletBinding()]
param(
    [string]$DependencyRoot = "",
    [string]$BuildDirectory = "",
    [switch]$DebugLogging,
    [switch]$NoArchive
)
$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if (!$DependencyRoot) { $DependencyRoot = Join-Path $repo ".idf" }
if (!$BuildDirectory) {
    $buildVariant = if ($DebugLogging) { "small-tv-esp32c2-debug" } else { "small-tv-esp32c2" }
    $BuildDirectory = Join-Path $repo ".build\$buildVariant"
}
$BuildDirectory = [IO.Path]::GetFullPath($BuildDirectory)
$idf = Join-Path $DependencyRoot "v6.1-9a97f6c54ec6"
$expected = "9a97f6c54ec638111ce55cd36581b3c192f15207"
if (!(Test-Path -LiteralPath (Join-Path $idf "export.ps1"))) { throw "Install the pinned ESP-IDF checkout ($expected) in $idf first. See README.md." }
$actual = (& git -C $idf rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actual -ne $expected) { throw "ESP-IDF revision differs from $expected" }
$bootstrap = Join-Path $DependencyRoot "python-3.12.10\tools"
& (Join-Path $bootstrap "python.exe") -B (Join-Path $PSScriptRoot "tools\prepare_resources.py") --output (Join-Path $BuildDirectory "resources")
if ($LASTEXITCODE -ne 0) { throw "Resource preparation failed" }
$saved = @{}
foreach ($key in @("Path","IDF_PATH","IDF_TOOLS_PATH","IDF_COMPONENT_MANAGER","PYTHONNOUSERSITE","PYTHONIOENCODING","PYTHONUTF8","PYTHONDONTWRITEBYTECODE")) { $saved[$key] = [Environment]::GetEnvironmentVariable($key) }
try {
    $env:IDF_TOOLS_PATH = Join-Path $DependencyRoot "tools-v6.1"
    $env:IDF_COMPONENT_MANAGER = "0"
    $env:PYTHONNOUSERSITE = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $env:Path = "$bootstrap;$bootstrap\Scripts;$env:Path"
    . (Join-Path $idf "export.ps1")
    $python = (Get-Command python.exe -CommandType Application | Select-Object -First 1).Source
    $toolPath = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -First 1 -ExpandProperty Value)[0]
    $jpegTools = @{}
    foreach ($name in @('riscv32-esp-elf-gcc.exe','cmake.exe','ninja.exe')) {
        $jpegTools[$name] = (Get-Command $name -CommandType Application | Select-Object -First 1).Source
    }
    & $python -B (Join-Path $PSScriptRoot 'tools/build_jpeg_library.py') --output (Join-Path $BuildDirectory 'jpeg-library') --toolchain-bin (Split-Path $jpegTools['riscv32-esp-elf-gcc.exe']) --cmake $jpegTools['cmake.exe'] --ninja $jpegTools['ninja.exe']
    if ($LASTEXITCODE -ne 0) { throw 'Offline JPEG dependency build failed' }
    $jpegSelection = Get-Content -LiteralPath (Join-Path $BuildDirectory 'jpeg-library/selection.json') -Raw | ConvertFrom-Json
    Push-Location $PSScriptRoot
    try {
        $debugValue = if ($DebugLogging) { "ON" } else { "OFF" }
        $arguments = @('-B', (Join-Path $idf "tools\idf.py"), "-B", $BuildDirectory, "--no-ccache", "-D", "SDKCONFIG=$BuildDirectory/sdkconfig", "-D", "SDKCONFIG_DEFAULTS=$PSScriptRoot/sdkconfig.defaults", "-D", "DEBUG=$debugValue", '-D', "JPEG_LIBRARY_BUILD=$($jpegSelection.build_directory)", "build")
        $process = Start-Process -Wait -PassThru -NoNewWindow -FilePath $python -ArgumentList $arguments -Environment @{ PATH = $toolPath }
        if ($process.ExitCode -ne 0) { throw "Firmware build failed" }
    } finally { Pop-Location }
    $builtSources = Get-Content -LiteralPath (Join-Path $BuildDirectory 'resources/source-manifest.json') -Raw | ConvertFrom-Json
    foreach ($entry in $builtSources.files) {
        $sourcePath = if ($entry.file.StartsWith('generated/')) { Join-Path $BuildDirectory ('resources/' + $entry.file.Substring(10)) } else { Join-Path $PSScriptRoot $entry.file }
        if ((Get-FileHash -LiteralPath $sourcePath).Hash.ToLower() -ne $entry.sha256) { throw "Source changed during firmware build: $($entry.file)" }
    }
    # Recheck the imported archive/private headers after the SDK's compile/link.
    & $python -B (Join-Path $PSScriptRoot 'tools/build_jpeg_library.py') --output (Join-Path $BuildDirectory 'jpeg-library') --toolchain-bin (Split-Path $jpegTools['riscv32-esp-elf-gcc.exe']) --cmake $jpegTools['cmake.exe'] --ninja $jpegTools['ninja.exe']
    if ($LASTEXITCODE -ne 0) { throw 'JPEG dependency changed during firmware build' }
} finally {
    foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key,$saved[$key]) }
}
if (!$NoArchive) {
    $archiveVariant = if ($DebugLogging) { "small-tv-esp32c2-reconstructed-debug" } else { "small-tv-esp32c2-reconstructed" }
    $destination = Join-Path $repo "firmware\development\$archiveVariant"
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "small_tv_reconstructed.bin") -Destination (Join-Path $destination "app.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "bootloader\bootloader.bin") -Destination (Join-Path $destination "bootloader.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "partition_table\partition-table.bin") -Destination (Join-Path $destination "partition-table.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\assets.bin") -Destination (Join-Path $destination "assets.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\assets-manifest.json") -Destination (Join-Path $destination "assets-manifest.json")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\source-manifest.json") -Destination (Join-Path $destination "source-manifest.json")
    Copy-Item -LiteralPath (Join-Path $jpegSelection.build_directory 'report.json') -Destination (Join-Path $destination 'jpeg-library-build.json')
    $archivedConfig = [IO.File]::ReadAllText((Join-Path $BuildDirectory "sdkconfig")).Replace("`r`n", "`n")
    [IO.File]::WriteAllText((Join-Path $destination "sdkconfig"), $archivedConfig, [Text.UTF8Encoding]::new($false))
    $images = @(@{file="bootloader.bin"; offset="0x0"},@{file="partition-table.bin";offset="0x8000"},@{file="app.bin";offset="0x10000"},@{file="assets.bin";offset="0x200000"})
    foreach ($image in $images) { $image.sha256 = (Get-FileHash -LiteralPath (Join-Path $destination $image.file) -Algorithm SHA256).Hash.ToLower(); $image.bytes = (Get-Item -LiteralPath (Join-Path $destination $image.file)).Length }
    $source=Get-Content -LiteralPath (Join-Path $destination "source-manifest.json") -Raw | ConvertFrom-Json
    $smallTvArchiveManifest = @{target="esp32c2";idf_revision=$expected;source_sha256=$source.aggregate_sha256;debug_logging=[bool]$DebugLogging;xtal_mhz=26;flash_bytes=4194304;status="compiled; hardware unverified";images=$images;elf_sha256=(Get-FileHash -LiteralPath (Join-Path $BuildDirectory 'small_tv_reconstructed.elf')).Hash.ToLower();jpeg_dependency_sha256=$jpegSelection.library_sha256;jpeg_dependency_report_sha256=(Get-FileHash -LiteralPath (Join-Path $destination 'jpeg-library-build.json')).Hash.ToLower()} | ConvertTo-Json -Depth 5
    # Keep fingerprinted archive metadata identical after Git's LF checkout filter.
    [IO.File]::WriteAllText((Join-Path $destination "manifest.json"), $smallTvArchiveManifest.Replace("`r`n", "`n") + "`n", [Text.UTF8Encoding]::new($false))
    Write-Host "Saved firmware to $destination"
}
