param(
    [Parameter(Mandatory = $true)]
    [string]$Fixture,
    [Parameter(Mandatory = $true)]
    [int]$BitrateKbps,
    [Parameter(Mandatory = $true)]
    [ValidateSet("audio/mpeg", "audio/aac")]
    [string]$MimeType,
    [string]$Port = "COM10",
    [int]$CaptureSeconds = 40,
    [string]$FixtureDirectory = ".build/esp8266-audio-profile/fixtures",
    [string]$ResultDirectory = ".build/esp8266-audio-profile/results",
    [string]$PythonPath = "python"
)

$ErrorActionPreference = "Stop"
$fixtureRoot = (Resolve-Path $FixtureDirectory).Path
$fixturePath = Join-Path $fixtureRoot $Fixture
if (-not (Test-Path -LiteralPath $fixturePath)) {
    throw "Fixture not found: $fixturePath"
}
New-Item -ItemType Directory -Path $ResultDirectory -Force | Out-Null
$resultRoot = (Resolve-Path $ResultDirectory).Path
$caseName = [IO.Path]::GetFileNameWithoutExtension($Fixture)

Copy-Item -LiteralPath $fixturePath -Destination (Join-Path $fixtureRoot "stream.bin") -Force
[IO.File]::WriteAllText(
    (Join-Path $fixtureRoot "stream.kbps"),
    "$BitrateKbps" + [Environment]::NewLine,
    [Text.Encoding]::ASCII)
[IO.File]::WriteAllText(
    (Join-Path $fixtureRoot "stream.mime"),
    "$MimeType" + [Environment]::NewLine,
    [Text.Encoding]::ASCII)

$serverScript = (Resolve-Path "tools/esp8266_audio_profile/stream_server.py").Path
$serverOut = Join-Path $resultRoot "$caseName-server.log"
$serverErr = Join-Path $resultRoot "$caseName-server.err"
$server = Start-Process -FilePath $PythonPath -ArgumentList @("-u", $serverScript, "--directory", $fixtureRoot, "--port", "8765", "--chunk-bytes", "256") -WindowStyle Hidden -RedirectStandardOutput $serverOut -RedirectStandardError $serverErr -PassThru

try {
    Start-Sleep -Milliseconds 500
    $serial = [System.IO.Ports.SerialPort]::new($Port, 115200, "None", 8, "One")
    $serial.ReadTimeout = 100
    $serial.DtrEnable = $false
    $serial.RtsEnable = $false
    $serial.Open()
    try {
        $serial.RtsEnable = $true
        Start-Sleep -Milliseconds 120
        $serial.RtsEnable = $false
        $deadline = [DateTime]::UtcNow.AddSeconds($CaptureSeconds)
        $log = [Text.StringBuilder]::new()
        while ([DateTime]::UtcNow -lt $deadline) {
            $chunk = $serial.ReadExisting()
            if ($chunk) { [void]$log.Append($chunk) }
            Start-Sleep -Milliseconds 40
        }
    }
    finally {
        $serial.Close()
    }
    $logPath = Join-Path $resultRoot "$caseName-run.log"
    [IO.File]::WriteAllText($logPath, $log.ToString(), [Text.UTF8Encoding]::new($false))
    $log.ToString() -split "[\r\n]+" |
        Where-Object { $_ -match "audio_profile:|DECODER|ERROR|free heap|Profile detection" }
}
finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id -Force
        $server.WaitForExit()
    }
}