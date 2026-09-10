param(
    [Parameter(Mandatory=$true)][string]$Directory,
    [ValidateRange(10,100)][int]$Runs=10,
    [ValidateRange(10,150)][int]$MaxAttempts=15,
    [ValidateRange(250,60000)][int]$IntervalMs=30000,
    [ValidateRange(0,30000)][int]$RestMs=5000,
    [string]$Fixtures=''
)
$ErrorActionPreference='Stop'
if($MaxAttempts -lt $Runs){throw 'MaxAttempts must be at least Runs'}
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskDirectory=[IO.Path]::GetFullPath((Join-Path $taskRoot $Directory))
if(-not $taskDirectory.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Reports must stay in repository'}
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null
if(Test-Path -LiteralPath (Join-Path $taskDirectory 'attempt1.json')){throw 'Existing attempts must not be overwritten'}
$taskCompleted=0
for($taskAttempt=1;$taskAttempt -le $MaxAttempts -and $taskCompleted -lt $Runs;$taskAttempt++) {
    $taskReport=Join-Path $taskDirectory "attempt$taskAttempt.json"
    Write-Output "START attempt $taskAttempt; completed $taskCompleted/$Runs"
    $taskArguments=@('--interval-ms',$IntervalMs,'--output',$taskReport)
    if($Fixtures){$taskArguments+=@('--fixtures',$Fixtures)}
    & node (Join-Path $PSScriptRoot 'run_board.cjs') @taskArguments *> (Join-Path $taskDirectory "attempt$taskAttempt.log")
    $taskExit=$LASTEXITCODE
    if(-not (Test-Path -LiteralPath $taskReport)){throw 'No report; inspect board before another POST'}
    $taskResult=Get-Content -LiteralPath $taskReport -Raw | ConvertFrom-Json
    if($taskResult.final.state -notin @(3,4)){throw 'Non-terminal/unknown board state; do not restart benchmark automatically'}
    if($taskExit -ne 0 -and $taskResult.final.state -eq 3){throw 'Completed firmware run failed validation; inspect report before retry'}
    if($taskExit -eq 0 -and $taskResult.final.state -eq 3) {
        $taskCompleted++
        Copy-Item -LiteralPath $taskReport -Destination (Join-Path $taskDirectory "run$taskCompleted.json")
        $taskMinimum=($taskResult.final.results.min_dram | Measure-Object -Minimum).Minimum
        $taskCpu=($taskResult.comparison | ForEach-Object {'{0:F2}' -f $_.task_budget_percent}) -join ', '
        Write-Output "DONE $taskCompleted/$Runs; min DRAM $taskMinimum; CPU [%] $taskCpu"
    } else {
        Write-Output "FAILED attempt $taskAttempt; device=$($taskResult.final.error); $($taskResult.error); retained"
    }
    if($taskCompleted -lt $Runs -and $taskAttempt -lt $MaxAttempts){Start-Sleep -Milliseconds $RestMs}
}
if($taskCompleted -ne $Runs){throw "Only $taskCompleted complete runs; all attempts retained"}
