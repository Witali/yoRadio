[CmdletBinding()]
param(
    [string]$DependencyRoot = "",
    [string]$BuildDirectory = "",
    [switch]$NoArchive
)
$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if (!$DependencyRoot) { $DependencyRoot = Join-Path $repo ".idf" }
if (!$BuildDirectory) { $BuildDirectory = Join-Path $repo ".build\small-tv-esp32c2" }
$BuildDirectory = [IO.Path]::GetFullPath($BuildDirectory)
$idf = Join-Path $DependencyRoot "v6.1-9a97f6c54ec6"
$expected = "9a97f6c54ec638111ce55cd36581b3c192f15207"
if (!(Test-Path -LiteralPath (Join-Path $idf "export.ps1"))) { throw "Install the pinned ESP-IDF checkout ($expected) in $idf first. See README.md." }
$actual = (& git -C $idf rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actual -ne $expected) { throw "ESP-IDF revision differs from $expected" }
$bootstrap = Join-Path $DependencyRoot "python-3.12.10\tools"
& (Join-Path $bootstrap "python.exe") (Join-Path $PSScriptRoot "tools\prepare_resources.py") --output (Join-Path $BuildDirectory "resources")
if ($LASTEXITCODE -ne 0) { throw "Resource preparation failed" }
$saved = @{}
foreach ($key in @("Path","IDF_PATH","IDF_TOOLS_PATH","IDF_COMPONENT_MANAGER","PYTHONNOUSERSITE","PYTHONIOENCODING","PYTHONUTF8")) { $saved[$key] = [Environment]::GetEnvironmentVariable($key) }
try {
    $env:IDF_TOOLS_PATH = Join-Path $DependencyRoot "tools-v6.1"
    $env:IDF_COMPONENT_MANAGER = "0"
    $env:PYTHONNOUSERSITE = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:Path = "$bootstrap;$bootstrap\Scripts;$env:Path"
    . (Join-Path $idf "export.ps1")
    $python = (Get-Command python.exe -CommandType Application | Select-Object -First 1).Source
    $toolPath = @(Get-ChildItem Env: | Where-Object { $_.Name -imatch '^path$' -and $_.Value.Contains('tools\ninja') } | Select-Object -First 1 -ExpandProperty Value)[0]
    Push-Location $PSScriptRoot
    try {
        $arguments = @((Join-Path $idf "tools\idf.py"), "-B", $BuildDirectory, "--no-ccache", "-D", "SDKCONFIG=$BuildDirectory/sdkconfig", "-D", "SDKCONFIG_DEFAULTS=$PSScriptRoot/sdkconfig.defaults", "build")
        $process = Start-Process -Wait -PassThru -NoNewWindow -FilePath $python -ArgumentList $arguments -Environment @{ PATH = $toolPath }
        if ($process.ExitCode -ne 0) { throw "Firmware build failed" }
    } finally { Pop-Location }
} finally {
    foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key,$saved[$key]) }
}
if (!$NoArchive) {
    $destination = Join-Path $repo "firmware\development\small-tv-esp32c2-reconstructed"
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "small_tv_reconstructed.bin") -Destination (Join-Path $destination "app.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "bootloader\bootloader.bin") -Destination (Join-Path $destination "bootloader.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "partition_table\partition-table.bin") -Destination (Join-Path $destination "partition-table.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\assets.bin") -Destination (Join-Path $destination "assets.bin")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\assets-manifest.json") -Destination (Join-Path $destination "assets-manifest.json")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "resources\source-manifest.json") -Destination (Join-Path $destination "source-manifest.json")
    Copy-Item -LiteralPath (Join-Path $BuildDirectory "sdkconfig") -Destination (Join-Path $destination "sdkconfig")
    $images = @(@{file="bootloader.bin"; offset="0x0"},@{file="partition-table.bin";offset="0x8000"},@{file="app.bin";offset="0x10000"},@{file="assets.bin";offset="0x200000"})
    foreach ($image in $images) { $image.sha256 = (Get-FileHash -LiteralPath (Join-Path $destination $image.file) -Algorithm SHA256).Hash.ToLower(); $image.bytes = (Get-Item -LiteralPath (Join-Path $destination $image.file)).Length }
    $source=Get-Content -LiteralPath (Join-Path $destination "source-manifest.json") -Raw | ConvertFrom-Json
    $smallTvArchiveManifest = @{target="esp32c2";idf_revision=$expected;source_sha256=$source.aggregate_sha256;xtal_mhz=26;flash_bytes=4194304;status="compiled; hardware unverified";images=$images} | ConvertTo-Json -Depth 5
    # Keep fingerprinted archive metadata identical after Git's LF checkout filter.
    [IO.File]::WriteAllText((Join-Path $destination "manifest.json"), $smallTvArchiveManifest.Replace("`r`n", "`n") + "`n", [Text.UTF8Encoding]::new($false))
    Write-Host "Saved firmware to $destination"
}
