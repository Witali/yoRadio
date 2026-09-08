param(
    [string]$Address = '192.168.100.6',
    [ValidateRange(1,600)][int]$Seconds = 180,
    [ValidateRange(100,5000)][int]$IntervalMs = 500,
    [string]$Output = '.build/esp8266-link-trace.json'
)
# Read-only ICMP diagnostics. Never configure adapters, routes or PC Wi-Fi.
$ErrorActionPreference = 'Stop'
$traceSamples = [Collections.Generic.List[object]]::new()
$tracePing = [Net.NetworkInformation.Ping]::new()
$traceClock = [Diagnostics.Stopwatch]::StartNew()
try {
    while ($traceClock.Elapsed.TotalSeconds -lt $Seconds) {
        $traceStart = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
        $traceOne = [Diagnostics.Stopwatch]::StartNew()
        try {
            $traceReply = $tracePing.Send($Address,750)
            $traceSamples.Add([ordered]@{startTime=$traceStart; elapsedMs=$traceOne.Elapsed.TotalMilliseconds;
                status=$traceReply.Status.ToString(); rttMs=if ($traceReply.Status -eq 'Success') {$traceReply.RoundtripTime} else {$null}})
        } catch {
            $traceSamples.Add([ordered]@{startTime=$traceStart; elapsedMs=$traceOne.Elapsed.TotalMilliseconds; status='Error'; rttMs=$null})
        }
        Start-Sleep -Milliseconds $IntervalMs
    }
} finally {
    $tracePing.Dispose()
    $traceParent = Split-Path -Parent $Output
    if ($traceParent) {New-Item -ItemType Directory -Force -Path $traceParent | Out-Null}
    [ordered]@{address=$Address;intervalMs=$IntervalMs;samples=$traceSamples.ToArray()} |
        ConvertTo-Json -Depth 5 | Out-File -LiteralPath $Output -Encoding utf8
    Write-Output "Saved $($traceSamples.Count) ICMP samples to $Output"
}
