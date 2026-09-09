[CmdletBinding()]
param(
    [string]$ReviewRoot,
    [string]$ToolchainBin,
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if (-not $ReviewRoot) {
    $ReviewRoot = Join-Path $repoRoot '.build/upstream-radio-review-2026-09-09'
}
if (-not $ToolchainBin) {
    $ToolchainBin = Join-Path $repoRoot '.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin'
}
$gcc = Join-Path $ToolchainBin 'xtensa-lx106-elf-gcc.exe'
$nm = Join-Path $ToolchainBin 'xtensa-lx106-elf-nm.exe'
foreach ($path in @($gcc, $nm, $ReviewRoot)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Not found: $path" }
}
$probeRoot = Join-Path $ReviewRoot 'size-probes'
New-Item -ItemType Directory -Path $probeRoot -Force | Out-Null
$sources = @(
    @{ Name='esp8266audio'; Mad='src/libmad'; Aac='src/libhelix-aac' },
    @{ Name='mrdiy-audio'; Mad='src/libmad'; Aac='src/libhelix-aac' },
    @{ Name='espressif-mp3'; Mad='mp3/mad'; Aac=$null },
    @{ Name='myradio'; Mad='mp3/mad'; Aac=$null }
)
function Read-Sizes([string]$ObjectPath) {
    $lines = & $nm -S --size-sort -t d $ObjectPath
    if ($LASTEXITCODE) { throw "nm failed: $ObjectPath" }
    $sizes = [ordered]@{}
    foreach ($line in $lines) {
        if ($line -match '^\s*\d+\s+(\d+)\s+\w\s+(size_\w+)\s*$') {
            $sizes[$Matches[2]] = [int]$Matches[1]
        }
    }
    if (-not $sizes.Count) { throw "No size symbols: $ObjectPath" }
    return $sizes
}
$results = foreach ($source in $sources) {
    $sourcePath = Join-Path $ReviewRoot $source.Name
    $revision = & git -C $sourcePath rev-parse HEAD
    if ($LASTEXITCODE) { throw "Not a cloned repository: $sourcePath" }
    $objectPath = Join-Path $probeRoot ($source.Name + '-mad.o')
    & $gcc -c -Os -I (Join-Path $sourcePath $source.Mad) (Join-Path $PSScriptRoot 'mad_sizes.c') -o $objectPath
    if ($LASTEXITCODE) { throw "MP3 size compilation failed: $($source.Name)" }
    $mad = Read-Sizes $objectPath
    if ($mad['size_pointer'] -ne 4) { throw 'This comparison requires 32-bit pointers' }
    $aac = $null
    if ($source.Aac) {
        $objectPath = Join-Path $probeRoot ($source.Name + '-aac.o')
        & $gcc -c -Os -DESP8266 -DARDUINO -I (Join-Path $PSScriptRoot 'stubs') -I (Join-Path $sourcePath $source.Aac) (Join-Path $PSScriptRoot 'aac_sizes.c') -o $objectPath
        if ($LASTEXITCODE) { throw "AAC size compilation failed: $($source.Name)" }
        $aac = Read-Sizes $objectPath
    }
    [ordered]@{ name=$source.Name; revision=$revision.Trim(); mp3=$mad; aac=$aac }
}
$json = [ordered]@{
    method='Xtensa GCC object symbol sizes, not runtime heap or speed'
    compiler=(& $gcc -dumpfullversion).Trim()
    sources=@($results)
} | ConvertTo-Json -Depth 8
if ($OutputPath) {
    $outputParent = Split-Path -Parent ([IO.Path]::GetFullPath($OutputPath))
    New-Item -ItemType Directory -Path $outputParent -Force | Out-Null
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}
$json
