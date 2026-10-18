#Requires -Version 7.5
# Owned-process cleanup and best-effort diagnostics for the Windows soak runner.
Set-StrictMode -Version Latest

function Set-SmallTvRuntimeCleanupFailure($State, [string]$Operation, [string]$Message) {
    # FIXED_TEST: record failure in memory; a broken log sink must not stop cleanup.
    $State.passed = $false
    $State.status = 'failed'
    [void]$State.cleanup_errors.Add(@{operation=$Operation; message=$Message})
    try {[Console]::Error.WriteLine("Runtime cleanup failed ($Operation): $Message")} catch {}
}

function Stop-SmallTvRuntimeChild($Child, $State) {
    # FIXED_TEST: use the retained process handle, and continue after a failed stop.
    if ($null -eq $Child) {return}
    try {
        if (!$Child.process.HasExited) {
            $Child.process.Kill()
            if (!$Child.process.WaitForExit(5000)) {throw 'Owned child did not exit after termination.'}
        }
    } catch {
        Set-SmallTvRuntimeCleanupFailure $State ('stop '+$Child.name) $_.Exception.Message
    }
}

function Read-SmallTvRuntimePipe($Child, [string]$Stream, $State) {
    # Drain an exited child's asynchronous pipe without an unbounded cleanup wait.
    try {
        if (!$Child.process.HasExited) {throw 'Child is still running; pipe drain was skipped.'}
        $task = $Child[$Stream]
        if (!$task.Wait(5000)) {throw 'Child pipe remained open after process exit.'}
        return $task.GetAwaiter().GetResult()
    } catch {
        Set-SmallTvRuntimeCleanupFailure $State ('drain '+$Child.name+' '+$Stream) $_.Exception.Message
        return $null
    }
}

function Save-SmallTvRuntimeChildLogs($Child, [string]$Control, $State) {
    # FIXED_TEST: each stream is independent; one unwritable file cannot lose both.
    if ($null -eq $Child) {return}
    foreach ($stream in @('stdout','stderr')) {
        $text = Read-SmallTvRuntimePipe $Child $stream $State
        if ($null -ne $text) {
            try {
                [IO.File]::WriteAllText((Join-Path $Control ($Child.name+'.'+$stream+'.log')),
                    $text, [Text.UTF8Encoding]::new($false))
            } catch {
                Set-SmallTvRuntimeCleanupFailure $State ('save '+$Child.name+' '+$stream) $_.Exception.Message
            }
        }
    }
}

function Invoke-SmallTvRuntimeVmCleanup([string]$Python, [string]$Helper,
                                       [string]$SessionDirectory, [string]$Control, $State) {
    # FIXED_TEST: run the identity-checking VM helper before opening its log file.
    $child = $null
    try {
        $start = [Diagnostics.ProcessStartInfo]::new($Python)
        $start.UseShellExecute=$false
        $start.CreateNoWindow=$true
        $start.RedirectStandardOutput=$true
        $start.RedirectStandardError=$true
        $start.StandardOutputEncoding=[Text.UTF8Encoding]::new($false)
        $start.StandardErrorEncoding=[Text.UTF8Encoding]::new($false)
        foreach ($argument in @('-X','utf8','-B',$Helper,'stop','--state',$SessionDirectory)) {
            [void]$start.ArgumentList.Add($argument)
        }
        $process = [Diagnostics.Process]::new()
        $process.StartInfo=$start
        [void]$process.Start()
        $child = @{process=$process; name='vm-cleanup';
            stdout=$process.StandardOutput.ReadToEndAsync(); stderr=$process.StandardError.ReadToEndAsync()}
        if (!$process.WaitForExit(15000)) {throw 'Owned VM cleanup helper did not finish.'}
        $State.vm_cleanup_exit_code=$process.ExitCode
        if ($process.ExitCode -ne 0) {throw "Owned VM cleanup helper exited with $($process.ExitCode)."}
    } catch {
        Set-SmallTvRuntimeCleanupFailure $State 'stop owned VM' $_.Exception.Message
    } finally {
        if ($null -ne $child) {
            Stop-SmallTvRuntimeChild $child $State
            $stdout = Read-SmallTvRuntimePipe $child 'stdout' $State
            $stderr = Read-SmallTvRuntimePipe $child 'stderr' $State
            try {
                [IO.File]::WriteAllText((Join-Path $Control 'vm-cleanup.log'),
                    [string]$stdout+[string]$stderr, [Text.UTF8Encoding]::new($false))
            } catch {
                Set-SmallTvRuntimeCleanupFailure $State 'save VM cleanup log' $_.Exception.Message
            }
            $child.process.Dispose()
        }
    }
}

function Write-SmallTvRuntimeFallback($State) {
    # FIXED_TEST: retain a failed terminal state on stderr if disk state is unwritable.
    try {
        [Console]::Error.WriteLine('SMALL_TV_SUPERVISOR_FINAL_STATE '+
            ($State | ConvertTo-Json -Depth 12 -Compress -EscapeHandling EscapeNonAscii))
    } catch {}
}

Export-ModuleMember -Function Set-SmallTvRuntimeCleanupFailure, Stop-SmallTvRuntimeChild,
    Save-SmallTvRuntimeChildLogs, Invoke-SmallTvRuntimeVmCleanup, Write-SmallTvRuntimeFallback
