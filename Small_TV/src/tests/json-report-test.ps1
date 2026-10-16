#Requires -Version 7.5
[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputPath)
$ErrorActionPreference="Stop"
. (Join-Path $PSScriptRoot "read-result.ps1")
$folder=Split-Path -Parent ([IO.Path]::GetFullPath($OutputPath))
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$inputPath=Join-Path $folder "aggregation-date-input.json"
$roundTripPath=Join-Path $folder "aggregation-date-roundtrip.json"
$fixture=@'
{"passed":true,"count":14,"nested":{"label":"sunday","dates":["2026-10-17T23:59:59+08:00","2026-10-18T00:00:00+08:00","2026-11-01T01:59:59-04:00","2026-11-01T01:00:00-05:00","2026-01-01T23:59:59+05:45","2026-10-16T17:50:43.178681+00:00"]}}
'@
[IO.File]::WriteAllText($inputPath,$fixture,[Text.UTF8Encoding]::new($false))
$expected=@('2026-10-17T23:59:59+08:00','2026-10-18T00:00:00+08:00',
    '2026-11-01T01:59:59-04:00','2026-11-01T01:00:00-05:00',
    '2026-01-01T23:59:59+05:45','2026-10-16T17:50:43.178681+00:00')
$checks=0
foreach ($phase in 0..1) {
    $result=Read-SmallTvTestResult $(if($phase){$roundTripPath}else{$inputPath})
    if (!$result.passed -or $result.count -ne 14 -or $result.nested.label -cne 'sunday') {
        throw 'JSON aggregation changed scalar values'
    }
    ++$checks
    if ($result.nested.dates.Count -ne $expected.Count) {throw 'JSON aggregation omitted dates'}
    foreach ($index in 0..($expected.Count-1)) {
        if ($result.nested.dates[$index] -isnot [string] -or
            $result.nested.dates[$index] -cne $expected[$index]) {
            throw "JSON aggregation changed country/calendar reference at $phase/$index"
        }
        ++$checks
    }
    if (!$phase) {$result | ConvertTo-Json -Depth 24 | Set-Content -Encoding utf8 -LiteralPath $roundTripPath}
}
@{passed=$true;checks=$checks;preserved_dates=$expected;scope='Actual suite JSON reader and serializer preserve country offsets, midnight, DST overlap and fractional UTC offsets as strings'} |
    ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 -LiteralPath $OutputPath
Write-Host "PASS JSON aggregation: $checks checks"
