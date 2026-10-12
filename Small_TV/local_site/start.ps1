param([ValidateRange(1024, 65535)][int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$taskSiteRoot = $PSScriptRoot
$taskRuntime = Join-Path $taskSiteRoot '.runtime'
$taskServer = Join-Path $taskSiteRoot 'server.py'
$taskUrl = "http://127.0.0.1:$Port/"

try {
    $taskHealth = Invoke-RestMethod "${taskUrl}_local/health" -TimeoutSec 2
    if ($taskHealth.application -eq 'SmallTVLocal') {
        Write-Output "Local: $taskUrl"
        return
    }
} catch { }

$taskPython = $null
$taskPrefix = @()
$taskBundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $taskBundled) {
    $taskPython = $taskBundled
} else {
    $taskCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($taskCommand -and $taskCommand.Source -notlike '*WindowsApps*') {
        $taskPython = $taskCommand.Source
    } else {
        $taskCommand = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($taskCommand) { $taskPython = $taskCommand.Source; $taskPrefix = @('-3') }
    }
}
if (-not $taskPython) { throw 'Python 3.10 or newer is required. You can also run: python server.py' }
[System.IO.Directory]::CreateDirectory($taskRuntime) | Out-Null
$taskArguments = $taskPrefix + @('-u', ('"' + $taskServer + '"'), '--port', "$Port",
    '--state-dir', ('"' + $taskRuntime + '"'))
$taskProcess = Start-Process -FilePath $taskPython -ArgumentList $taskArguments -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $taskRuntime 'server.stdout.log') `
    -RedirectStandardError (Join-Path $taskRuntime 'server.stderr.log')
for ($taskAttempt = 0; $taskAttempt -lt 30; $taskAttempt++) {
    Start-Sleep -Milliseconds 150
    $taskProcess.Refresh()
    if ($taskProcess.HasExited) { throw "Server stopped. See $taskRuntime\server.stderr.log; the port may be in use." }
    try {
        $taskHealth = Invoke-RestMethod "${taskUrl}_local/health" -TimeoutSec 1
        if ($taskHealth.application -eq 'SmallTVLocal') {
            [System.IO.File]::WriteAllText((Join-Path $taskRuntime 'server.pid'), "$($taskProcess.Id)")
            Write-Output "Local: $taskUrl"
            Write-Output 'Pages: /settings, /photo, /setup. Stop with .\stop.ps1.'
            return
        }
    } catch { }
}
throw "Server did not become ready. See $taskRuntime\server.stderr.log."
