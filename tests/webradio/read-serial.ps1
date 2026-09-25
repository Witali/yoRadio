[CmdletBinding()]
param(
    [string]$Port = "COM8",
    [int]$DurationSeconds = 15,
    [switch]$Reset
)

$ErrorActionPreference = "Stop"
$serial = [System.IO.Ports.SerialPort]::new($Port, 115200, "None", 8, "One")
$serial.ReadTimeout = 100
$serial.DtrEnable = $false
$serial.RtsEnable = $false

try {
    $serial.Open()
    if ($Reset) {
        $serial.DtrEnable = $false
        $serial.RtsEnable = $true
        Start-Sleep -Milliseconds 100
        $serial.RtsEnable = $false
    }

    $deadline = [DateTime]::UtcNow.AddSeconds($DurationSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        $text = $serial.ReadExisting()
        if ($text.Length -gt 0) { Write-Host -NoNewline $text }
        Start-Sleep -Milliseconds 25
    }
} finally {
    if ($serial.IsOpen) { $serial.Close() }
    $serial.Dispose()
}
