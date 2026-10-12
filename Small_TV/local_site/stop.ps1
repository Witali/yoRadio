$ErrorActionPreference = 'Stop'
$taskPidFile = Join-Path $PSScriptRoot '.runtime\server.pid'
if (-not (Test-Path -LiteralPath $taskPidFile)) { Write-Output 'No managed server PID found.'; return }
$taskPidText = (Get-Content -LiteralPath $taskPidFile -Raw).Trim()
if ($taskPidText -notmatch '^\d+$') { throw 'Invalid server PID file.' }
$taskProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $taskPidText"
if ($taskProcess) {
    $taskExpectedScript = Join-Path $PSScriptRoot 'server.py'
    if (-not $taskProcess.CommandLine.Contains($taskExpectedScript)) {
        throw 'PID belongs to a different process; it was not stopped.'
    }
    Stop-Process -Id ([int]$taskPidText)
}
Remove-Item -LiteralPath $taskPidFile
Write-Output 'Small_TV local server stopped.'
