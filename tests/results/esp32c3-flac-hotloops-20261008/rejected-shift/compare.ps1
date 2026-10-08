$ErrorActionPreference = 'Stop'
$lpcRoot = 'C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade'
$lpcOut = "$lpcRoot/.build/flac-hotloops-20261008/shift-codegen/frozen-audit"
$lpcDb = "$lpcRoot/idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof/compile_commands.json"
$lpcEntry = (Get-Content -LiteralPath $lpcDb -Raw | ConvertFrom-Json) | Where-Object { $_.file -match 'flac_decoder.cpp$' }
$lpcTokens = $lpcEntry.command -split '\s+'
$lpcCompiler = $lpcTokens[0]
$lpcBaseArgs = @($lpcTokens[1..($lpcTokens.Count - 1)] | ForEach-Object {
    if ($_.StartsWith('@"')) { '@' + $_.Substring(2, $_.Length - 3) }
    else { $_.Replace('\"', '"') }
})
$lpcBin = Split-Path -Parent $lpcCompiler
New-Item -ItemType Directory -Path $lpcOut -Force | Out-Null
$lpcInputs = "$lpcOut/inputs"
if (Test-Path -LiteralPath $lpcInputs) { throw 'Frozen inputs already exist; preserve this audit and choose a new directory.' }
New-Item -ItemType Directory -Path $lpcInputs | Out-Null
$lpcFrozenSource = "$lpcInputs/flac_decoder.cpp"
$lpcFrozenHeader = "$lpcInputs/flac_decoder.h"
$lpcFrozenFlags = "$lpcInputs/cxxflags"
Copy-Item -LiteralPath $lpcEntry.file -Destination $lpcFrozenSource
Copy-Item -LiteralPath (Join-Path (Split-Path -Parent $lpcEntry.file) 'flac_decoder.h') -Destination $lpcFrozenHeader
for ($lpcArgIndex = 0; $lpcArgIndex -lt $lpcBaseArgs.Count; ++$lpcArgIndex) {
    if ($lpcBaseArgs[$lpcArgIndex] -eq $lpcEntry.file) { $lpcBaseArgs[$lpcArgIndex] = $lpcFrozenSource }
    elseif ($lpcBaseArgs[$lpcArgIndex].StartsWith('@')) {
        Copy-Item -LiteralPath $lpcBaseArgs[$lpcArgIndex].Substring(1) -Destination $lpcFrozenFlags
        $lpcBaseArgs[$lpcArgIndex] = '@' + $lpcFrozenFlags
    }
}
$lpcEntry | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$lpcOut/original-command.json"
Get-FileHash -LiteralPath $lpcFrozenSource, $lpcFrozenHeader, $lpcFrozenFlags, $lpcCompiler -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath "$lpcOut/input-hashes.json"
$lpcCommands = @()
$lpcSymbols = @()
$lpcSizes = @()
$lpcSourceHash = (Get-FileHash -LiteralPath $lpcFrozenSource -Algorithm SHA256).Hash
$lpcVariants = @(
    @{ name = 'default'; defines = @() },
    @{ name = 'bounded-shift'; defines = @('-DFLAC_BOUNDED_LPC_SHIFT=1') }
)
foreach ($lpcCase in $lpcVariants) {
    $lpcVariant = $lpcCase.name
    $lpcObj = "$lpcOut/$lpcVariant.obj"
    $lpcArgs = @($lpcBaseArgs)
    $lpcOutputFlag = [Array]::IndexOf($lpcArgs, '-o')
    if ($lpcOutputFlag -lt 0) { throw 'No output flag in baseline command' }
    $lpcArgs[$lpcOutputFlag + 1] = $lpcObj
        for ($lpcArgIndex = 0; $lpcArgIndex -lt $lpcArgs.Count; ++$lpcArgIndex) {
        if ($lpcArgs[$lpcArgIndex] -eq '-MF') { $lpcArgs[++$lpcArgIndex] = "$lpcOut/$lpcVariant.d" }
        elseif ($lpcArgs[$lpcArgIndex] -eq '-MT' -or $lpcArgs[$lpcArgIndex] -eq '-MQ') { $lpcArgs[++$lpcArgIndex] = $lpcObj }
        elseif ($lpcArgs[$lpcArgIndex] -match '^-MF.+') { $lpcArgs[$lpcArgIndex] = '-MF' + "$lpcOut/$lpcVariant.d" }
        elseif ($lpcArgs[$lpcArgIndex] -match '^-(MT|MQ).+') { $lpcArgs[$lpcArgIndex] = '-MT' + $lpcObj }
    }
    $lpcArgs += @('-MMD', '-MF', "$lpcOut/$lpcVariant.d", '-MT', $lpcObj)
    $lpcArgs += $lpcCase.defines
    $lpcCommands += @{ variant = $lpcVariant; compiler = $lpcCompiler; args = $lpcArgs; directory = $lpcEntry.directory; source_sha256 = $lpcSourceHash }
    Push-Location $lpcEntry.directory
    try {
        & $lpcCompiler @lpcArgs 2>&1 | Set-Content -LiteralPath "$lpcOut/$lpcVariant.compile.log"
        if ($LASTEXITCODE -ne 0) { throw "$lpcVariant compilation failed: $LASTEXITCODE" }
    } finally { Pop-Location }
    $lpcNm = & "$lpcBin/riscv32-esp-elf-nm.exe" -C -S $lpcObj
    if ($LASTEXITCODE -ne 0) { throw 'nm failed' }
    $lpcNm | Set-Content -LiteralPath "$lpcOut/$lpcVariant.nm.txt"
    $lpcSymbols += "$lpcVariant`n" + (($lpcNm | Select-String 'restoreLinearPrediction|restoreSparseDeltaPrediction|decodeResiduals|readUint|readRice') -join "`n")
    & "$lpcBin/riscv32-esp-elf-objdump.exe" -dr -C $lpcObj | Set-Content -LiteralPath "$lpcOut/$lpcVariant.disassembly.txt"
    if ($LASTEXITCODE -ne 0) { throw 'objdump failed' }
    & "$lpcBin/riscv32-esp-elf-size.exe" $lpcObj | Set-Content -LiteralPath "$lpcOut/$lpcVariant.size.txt"
    $lpcSectionSizes = & "$lpcBin/riscv32-esp-elf-size.exe" -A $lpcObj
    $lpcSectionSizes | Set-Content -LiteralPath "$lpcOut/$lpcVariant.sections.txt"
    $lpcTextBytes = 0
    foreach ($lpcSizeLine in $lpcSectionSizes) {
        if ($lpcSizeLine -match '^\.text\S*\s+(\d+)\s+') { $lpcTextBytes += [int]$Matches[1] }
    }
    $lpcSizes += @{ variant = $lpcVariant; text_bytes = $lpcTextBytes; source_sha256 = $lpcSourceHash }
}
$lpcCommands | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$lpcOut/commands.json"
$lpcSymbols | Set-Content -LiteralPath "$lpcOut/symbol-comparison.txt"
$lpcSizes | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath "$lpcOut/text-comparison.json"
$lpcSymbols
$lpcSizes | ConvertTo-Json -Depth 3


