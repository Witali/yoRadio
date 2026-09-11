param(
    [Parameter(Mandatory=$true)][string]$Directory,
    [Parameter(Mandatory=$true)][string]$Fixtures,
    [ValidateRange(10,100)][int]$Attempts=10,
    [ValidateRange(250,60000)][int]$IntervalMs=1500
)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskDirectory=[IO.Path]::GetFullPath((Join-Path $taskRoot $Directory))
if(-not $taskDirectory.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Reports must stay in repository'}
if(Test-Path -LiteralPath (Join-Path $taskDirectory 'run1.json')){throw 'Existing attempts must not be overwritten'}
if(-not(Test-Path -LiteralPath (Join-Path $Fixtures 'manifest.json'))){throw 'Explicit fixture manifest required'}
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
for($taskAttempt=1;$taskAttempt -le $Attempts;$taskAttempt++) {
    $taskReport=Join-Path $taskDirectory "run$taskAttempt.json"
    $taskLog=Join-Path $taskDirectory "run$taskAttempt.log"
    Write-Output "START raw attempt $taskAttempt/$Attempts"
    try {
        $ErrorActionPreference='Continue'
        & node (Join-Path $PSScriptRoot 'run_board.cjs') --interval-ms $IntervalMs --fixtures $Fixtures --output $taskReport *> $taskLog
    } finally { $ErrorActionPreference='Stop' }
    if(-not(Test-Path -LiteralPath $taskReport)){throw 'Missing report; inspect board before another POST'}
    $taskClassification=& node (Join-Path $PSScriptRoot 'classify_raw_run.cjs') $taskReport
    if($LASTEXITCODE -ne 0){throw 'Unknown/invalid observation; preserve report and do not restart'}
    $taskResult=$taskClassification | ConvertFrom-Json
    # Every requested attempt keeps its number; never replace failures with
    # success-only files. compare_raw rejects incomplete/errorful series.
    if($taskResult.completed) {
        $taskCpu=($taskResult.cases | ForEach-Object {'{0:F2}' -f $_.cpu_budget_percent}) -join ', '
        Write-Output "MEASURED $taskAttempt/$Attempts; min DRAM $($taskResult.min_dram); raw CPU [%] $taskCpu"
    } else {
        Write-Output "FAILED $taskAttempt/$Attempts; device=$($taskResult.device_error); retained"
    }
    if($taskAttempt -lt $Attempts){Start-Sleep -Milliseconds 5000}
}
