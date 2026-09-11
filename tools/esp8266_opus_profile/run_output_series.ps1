param(
    [Parameter(Mandatory=$true)][string]$Directory,
    [Parameter(Mandatory=$true)][string]$Fixtures,
    [ValidateRange(10,100)][int]$Attempts=10,
    [ValidateRange(250,60000)][int]$IntervalMs=30000,
    [ValidateRange(0,30000)][int]$RestMs=5000
)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskDirectory=[IO.Path]::GetFullPath((Join-Path $taskRoot $Directory))
if(-not $taskDirectory.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Reports must stay in repository'}
if(Test-Path -LiteralPath (Join-Path $taskDirectory 'attempt1.json')){throw 'Existing attempts must not be overwritten'}
if(-not(Test-Path -LiteralPath (Join-Path $Fixtures 'manifest.json'))){throw 'Explicit fixture manifest required'}
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
for($taskAttempt=1;$taskAttempt -le $Attempts;$taskAttempt++) {
    $taskReport=Join-Path $taskDirectory "attempt$taskAttempt.json"
    $taskLog=Join-Path $taskDirectory "attempt$taskAttempt.log"
    Write-Output "START output attempt $taskAttempt/$Attempts"
    try {
        $ErrorActionPreference='Continue'
        & node (Join-Path $PSScriptRoot 'run_board.cjs') --interval-ms $IntervalMs --fixtures $Fixtures --output $taskReport *> $taskLog
    } finally { $ErrorActionPreference='Stop' }
    if(-not(Test-Path -LiteralPath $taskReport)){throw 'No report; inspect board before another POST'}
    $taskClassification=& node (Join-Path $PSScriptRoot 'classify_output_run.cjs') $taskReport
    if($LASTEXITCODE -ne 0){throw 'Unknown/invalid observation; preserve report and do not restart'}
    $taskResult=$taskClassification | ConvertFrom-Json
    # No success-only copies and no replacement attempts: every requested run
    # remains in the series, including device errors and failed continuity.
    if($taskResult.completed) {
        $taskCpu=($taskResult.cases | ForEach-Object {'{0:F2}' -f $_.pipeline_cpu_budget_percent}) -join ', '
        Write-Output "MEASURED $taskAttempt/$Attempts; continuous $($taskResult.continuous_cases)/$($taskResult.total_cases); min DRAM $($taskResult.min_dram); pipeline CPU [%] $taskCpu"
    } else {
        Write-Output "FAILED $taskAttempt/$Attempts; device=$($taskResult.device_error); retained"
    }
    if($taskAttempt -lt $Attempts){Start-Sleep -Milliseconds $RestMs}
}
