#Requires -Version 7.5
<# Launch one supervised workload outside the caller's Windows Job.
   This survives caller exit, but not Windows shutdown or explicit termination.
   A launch record is not evidence of a terminal workload or an H10 pass. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$YoradioRoot,
    [Parameter(Mandatory)][string]$QemuRoot,
    [string]$QemuExecutable,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$DependencyRoot = $YoradioRoot,
    [ValidateRange(0,100000)][int]$Cycles = 0,
    [ValidateRange(1,604800)][int]$DurationSeconds = 86400,
    [ValidateRange(0.1,60)][double]$IntervalSeconds = 15,
    [ValidateRange(0,100000)][int]$OutageEvery = 60,
    [switch]$HeapTopology
)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot 'runtime_process.psm1') -Force
$YoradioRoot=[IO.Path]::GetFullPath($YoradioRoot)
$QemuRoot=[IO.Path]::GetFullPath($QemuRoot)
$DependencyRoot=[IO.Path]::GetFullPath($DependencyRoot)
$OutputDirectory=[IO.Path]::GetFullPath($OutputDirectory)
$supervisor=Join-Path $YoradioRoot 'Small_TV/src/tools/runtime_supervisor.ps1'
foreach ($file in @($supervisor, (Join-Path $QemuRoot 'tools/small_tv_vm.py'),
        (Join-Path $DependencyRoot '.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'))) {
    if (!(Test-Path -LiteralPath $file -PathType Leaf)) {throw "Missing runtime input: $file"}
}
foreach ($folder in @($OutputDirectory, ($OutputDirectory+'-supervisor'))) {
    if (Test-Path -LiteralPath $folder) {throw 'Use new runtime directories; existing evidence is preserved.'}
}
$recordPath=$OutputDirectory+'-launch.json'
$state=[ordered]@{schema_version=1;status='starting';all_functionality_verified=$false;
    captured_utc=[DateTime]::UtcNow.ToString('o');run_directory=$OutputDirectory;
    scope='Detached process launch only; not workload completion or H10 acceptance.';
    sources_sha256=@{}}
foreach ($source in @($PSCommandPath, (Join-Path $PSScriptRoot 'runtime_process.psm1'), $supervisor)) {
    $state.sources_sha256[$source]=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower()
}
# Reserve this run name before creating any process. A duplicate invocation must
# not start a second VM, overwrite an existing launch, or consume old evidence.
$reservation=[IO.File]::Open($recordPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
$reservation.Dispose()
try {
    $arguments=@('-NoProfile','-NonInteractive','-File',$supervisor,
        '-YoradioRoot',$YoradioRoot,'-QemuRoot',$QemuRoot,'-DependencyRoot',$DependencyRoot,
        '-OutputDirectory',$OutputDirectory,'-DurationSeconds',"$DurationSeconds",
        '-IntervalSeconds',$IntervalSeconds.ToString([Globalization.CultureInfo]::InvariantCulture),
        '-OutageEvery',"$OutageEvery")
    if ($Cycles) {$arguments+=@('-Cycles',"$Cycles")}
    # FIXED_TEST: preserve a separately pinned candidate through detached launch.
    if ($QemuExecutable) {$arguments+=@('-QemuExecutable',[IO.Path]::GetFullPath($QemuExecutable))}
    if ($HeapTopology) {$arguments+=@('-HeapTopology')}
    $state.process=Start-SmallTvDetachedProcess -FilePath (Get-Command pwsh).Source `
        -Arguments $arguments -WorkingDirectory $YoradioRoot
    $state.status='started_not_completed'
} catch {
    $state.status='launch_failed'
    $state.error=$_.Exception.Message
    throw
} finally {
    [IO.File]::WriteAllText($recordPath, ($state | ConvertTo-Json -Depth 8)+"`n", [Text.UTF8Encoding]::new($false))
}
$state | ConvertTo-Json -Depth 8
