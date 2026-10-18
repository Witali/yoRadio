#Requires -Version 7.5
# Windows process support for long QEMU workloads. No shell evaluates arguments.
Set-StrictMode -Version Latest

function ConvertTo-WindowsProcessArgument([AllowEmptyString()][string]$Value) {
    # Quote one argv element, including quotes and backslashes before its end.
    $escaped = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    return '"' + [regex]::Replace($escaped, '(\\+)$', '$1$1') + '"'
}

function Test-SmallTvProcessJob([Diagnostics.Process]$Process) {
    # Query the real kernel job membership; a detached launch must be outside it.
    if (-not ('SmallTv.RuntimeProcessNative' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
namespace SmallTv {
    public static class RuntimeProcessNative {
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool IsProcessInJob(IntPtr process, IntPtr job,
            [MarshalAs(UnmanagedType.Bool)] out bool result);
        public static bool InJob(IntPtr process) {
            bool result;
            if (!IsProcessInJob(process, IntPtr.Zero, out result))
                throw new Win32Exception(Marshal.GetLastWin32Error());
            return result;
        }
    }
}
'@
    }
    return [SmallTv.RuntimeProcessNative]::InJob($Process.Handle)
}

function Start-SmallTvDetachedProcess {
    # Use the Windows provider and CREATE_BREAKAWAY_FROM_JOB, then verify the
    # child's identity and job membership before reporting a successful launch.
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][AllowEmptyCollection()][AllowEmptyString()][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory
    )
    if (!$IsWindows) {throw 'Detached runtime launch requires Windows.'}
    $executable = (Get-Item -LiteralPath $FilePath -ErrorAction Stop)
    $directory = (Get-Item -LiteralPath $WorkingDirectory -ErrorAction Stop)
    if ($executable.PSIsContainer -or !$directory.PSIsContainer) {
        throw 'Expected an executable file and a working directory.'
    }
    $command = (@($executable.FullName) + $Arguments | ForEach-Object {
        ConvertTo-WindowsProcessArgument $_
    }) -join ' '
    $startup = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{
        ShowWindow=[uint16]0; CreateFlags=[uint32]0x01000000
    }
    $created = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine=$command; CurrentDirectory=$directory.FullName;
        ProcessStartupInformation=$startup
    } -ErrorAction Stop
    if ($created.ReturnValue -ne 0 -or !$created.ProcessId) {
        throw "Windows process creation failed: $($created.ReturnValue)"
    }
    $child = [Diagnostics.Process]::GetProcessById($created.ProcessId)
    $identityVerified = $false
    try {
        # Retaining the process handle also makes cleanup safe against PID reuse.
        $null = $child.Handle
        $identity = Get-CimInstance Win32_Process -Filter "ProcessId=$($created.ProcessId)" -ErrorAction Stop
        if (!$identity -or $identity.CommandLine -cne $command) {
            throw 'Detached child command does not match the requested launch.'
        }
        $identityVerified = $true
        if (Test-SmallTvProcessJob $child) {throw 'Detached child is still inside a Windows Job.'}
        return [ordered]@{
            pid=[int]$identity.ProcessId;
            created_utc=$identity.CreationDate.ToUniversalTime().ToString('o');
            command_line=$identity.CommandLine; parent_pid=[int]$identity.ParentProcessId;
            working_directory=$directory.FullName; in_job=$false;
            create_flags='CREATE_BREAKAWAY_FROM_JOB'; launcher_pid=$PID
        }
    } catch {
        # A process that exited before inspection may already have a reused PID.
        # Only clean up after the held handle and requested command were matched.
        if ($identityVerified -and !$child.HasExited) {$child.Kill(); [void]$child.WaitForExit(5000)}
        throw
    } finally {$child.Dispose()}
}

Export-ModuleMember -Function Start-SmallTvDetachedProcess
