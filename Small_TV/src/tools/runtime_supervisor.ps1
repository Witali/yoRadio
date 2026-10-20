#Requires -Version 7.5
<# Run the native workload and UART guard as owned children; reject lost workers.
   Launch this script with Start-Process -WindowStyle Hidden for a background run.
   Its state is evidence only while the recorded supervisor process is alive or
   status is terminal. A stale running JSON file never proves a live workload. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$YoradioRoot,
    [Parameter(Mandatory)][string]$QemuRoot,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$DependencyRoot = $YoradioRoot,
    [ValidateRange(0,100000)][int]$Cycles = 0,
    [ValidateRange(1,604800)][int]$DurationSeconds = 86400,
    [ValidateRange(0.1,60)][double]$IntervalSeconds = 15,
    [ValidateRange(0,100000)][int]$OutageEvery = 60
)
$ErrorActionPreference = 'Stop'
$cleanupModule = Join-Path $PSScriptRoot 'runtime_cleanup.psm1'
Import-Module $cleanupModule -Force
$stateModule = Join-Path $PSScriptRoot 'runtime_state_io.psm1'
Import-Module $stateModule -Force
$YoradioRoot = [IO.Path]::GetFullPath($YoradioRoot)
$QemuRoot = [IO.Path]::GetFullPath($QemuRoot)
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
$DependencyRoot = [IO.Path]::GetFullPath($DependencyRoot)
$control = $OutputDirectory + '-supervisor'
if ((Test-Path -LiteralPath $OutputDirectory) -or (Test-Path -LiteralPath $control)) {
    throw 'Use new workload and supervisor directories; existing evidence is preserved.'
}
New-Item -ItemType Directory -Path $control | Out-Null
$python = Join-Path $DependencyRoot '.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$driver = Join-Path $YoradioRoot 'Small_TV/src/tests/runtime_qemu.py'
$guardSource = Join-Path $PSScriptRoot 'runtime_run_guard.py'
$sources = @($PSCommandPath, $cleanupModule, $stateModule, $driver, $guardSource, (Join-Path $QemuRoot 'tools/small_tv_vm.py'))
$state = [ordered]@{schema_version=1; status='starting'; passed=$false; all_functionality_verified=$false;
    supervisor_pid=$PID; supervisor_started_utc=[DateTime]::UtcNow.ToString('o');
    run_directory=$OutputDirectory; scope='Child process supervision only; not a 24-hour or memory-trend acceptance.';
    sources_sha256=@{}; cleanup_errors=[Collections.Generic.List[object]]::new(); deferred_state_writes=0}
foreach ($source in $sources) {$state.sources_sha256[$source]=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower()}

function Save-State([switch]$Final) {
    # FIXED_TEST: state-file sharing conflicts and final writes have distinct rules.
    Write-SmallTvRuntimeState $state $control -Final:$Final
}
function Read-Report([string]$Path) {
    # A producer may be rewriting its report; wait for a later complete read.
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -Depth 100) } catch { return $null }
}
function Start-Child([string[]]$Arguments, [string]$Name) {
    # ArgumentList preserves path boundaries without constructing shell code.
    $start = [Diagnostics.ProcessStartInfo]::new($python)
    $start.UseShellExecute=$false
    $start.CreateNoWindow=$true
    $start.WorkingDirectory=$YoradioRoot
    $start.RedirectStandardOutput=$true
    $start.RedirectStandardError=$true
    $start.StandardOutputEncoding=[Text.UTF8Encoding]::new($false)
    $start.StandardErrorEncoding=[Text.UTF8Encoding]::new($false)
    foreach ($argument in @('-X','utf8','-B')+$Arguments) {[void]$start.ArgumentList.Add($argument)}
    $process = [Diagnostics.Process]::new()
    $process.StartInfo=$start
    [void]$process.Start()
    return @{process=$process; stdout=$process.StandardOutput.ReadToEndAsync();
             stderr=$process.StandardError.ReadToEndAsync(); name=$Name}
}
$workload = $guard = $null
try {
    $length = if ($Cycles) {@('--cycles', "$Cycles")} else {@('--duration-seconds', "$DurationSeconds")}
    $arguments = @($driver, '--yoradio', $YoradioRoot, '--dependency-root', $DependencyRoot,
        '--qemu-root', $QemuRoot, '--output', $OutputDirectory,
        '--interval-seconds', $IntervalSeconds.ToString([Globalization.CultureInfo]::InvariantCulture),
        '--outage-every', "$OutageEvery", '--outage-seconds', '1') + $length
    $workload = Start-Child $arguments 'workload'
    $state.workload_pid=$workload.process.Id
    $state.workload_started_utc=$workload.process.StartTime.ToUniversalTime().ToString('o')
    $state.status='running'
    Save-State
    while ($true) {
        $report = Read-Report (Join-Path $OutputDirectory 'report.json')
        if ($null -eq $guard -and $null -ne $report) {
            $guard = Start-Child @($guardSource, '--run', $OutputDirectory, '--qemu-tools', (Join-Path $QemuRoot 'tools')) 'guard'
            $state.guard_pid=$guard.process.Id
        }
        if ($workload.process.HasExited) {break}
        if ($null -ne $guard -and $guard.process.HasExited -and $guard.process.ExitCode -ne 0) {
            throw 'Independent UART guard failed while the workload was running.'
        }
        $state.observed_at_utc=[DateTime]::UtcNow.ToString('o')
        if ($null -ne $report) {$state.completed_cycles_observed=$report.completed_cycles}
        Save-State
        Start-Sleep -Seconds 1
    }
    $state.workload_exit_code=$workload.process.ExitCode
    $report = Read-Report (Join-Path $OutputDirectory 'report.json')
    $terminal = $null -ne $report -and $null -ne $report.journal -and $report.inputs_unchanged -eq $true
    if (!$terminal) {throw 'Workload exited without a successful terminal footer.'}
    if ($null -eq $guard -or !$guard.process.WaitForExit(15000)) {throw 'UART guard did not finish after the workload.'}
    $guardReport = Read-Report (Join-Path $OutputDirectory 'uptime-guard.json')
    $state.guard_exit_code=$guard.process.ExitCode
    $state.sources_unchanged=$true
    foreach ($source in $sources) {
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $state.sources_sha256[$source]) {
            $state.sources_unchanged=$false
        }
    }
    $state.passed=$state.workload_exit_code -eq 0 -and $state.guard_exit_code -eq 0 -and
        $report.passed -eq $true -and $guardReport.passed -eq $true -and
        $guardReport.status -eq 'complete' -and $guardReport.workload_passed -eq $true -and $state.sources_unchanged
    $state.status=if ($state.passed) {'complete'} else {'failed'}
} catch {
    $state.status='failed'
    $state.error=$_.Exception.Message
} finally {
    # FIXED_TEST: finish all process cleanup before best-effort log writes.
    # One inaccessible/full output sink must not leave later children alive.
    foreach ($child in @($workload,$guard)) {
        Stop-SmallTvRuntimeChild $child $state
    }
    try {
        if (!$state.passed -and (Test-Path -LiteralPath (Join-Path $OutputDirectory 'vm/session.json'))) {
            Invoke-SmallTvRuntimeVmCleanup $python (Join-Path $QemuRoot 'tools/small_tv_vm.py') `
                (Join-Path $OutputDirectory 'vm') $control $state
        }
    } catch {
        Set-SmallTvRuntimeCleanupFailure $state 'locate owned VM session' $_.Exception.Message
    }
    foreach ($child in @($workload,$guard)) {
        Save-SmallTvRuntimeChildLogs $child $control $state
    }
    $state.finished_utc=[DateTime]::UtcNow.ToString('o')
    try {Save-State -Final} catch {
        Set-SmallTvRuntimeCleanupFailure $state 'save final supervisor state' $_.Exception.Message
        Write-SmallTvRuntimeFallback $state
    }
}
if (!$state.passed) {exit 1}
exit 0
