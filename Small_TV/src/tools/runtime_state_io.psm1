#Requires -Version 7.5
# Atomic supervisor-state output; independent of process cleanup and guest timing.
Set-StrictMode -Version Latest

function Get-SmallTvRuntimeStateSharingError([string]$Temporary, [string]$Target) {
    # Distinguish a rename-sharing conflict from an actual access denial. Merely
    # opening DELETE access never deletes a file; no DELETE_ON_CLOSE is requested.
    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    if (-not ('SmallTv.RuntimeStateFile' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace SmallTv {
    public static class RuntimeStateFile {
        [DllImport("kernel32.dll", EntryPoint = "CreateFileW", ExactSpelling = true,
            CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern IntPtr CreateFileW(string name, uint access,
            uint sharing, IntPtr security, uint mode, uint flags, IntPtr template);
        [DllImport("kernel32.dll")]
        private static extern bool CloseHandle(IntPtr handle);
        public static int DeleteAccessError(string name) {
            IntPtr handle = CreateFileW(name, 0x10000, 7, IntPtr.Zero, 3, 0, IntPtr.Zero);
            if (handle == new IntPtr(-1)) return Marshal.GetLastWin32Error();
            CloseHandle(handle);
            return 0;
        }
    }
}
'@
    }
    foreach ($path in @($Temporary,$Target)) {
        $code = [SmallTv.RuntimeStateFile]::DeleteAccessError($path)
        if ($code -notin @(0,2)) {return $code}
    }
    return 0
}

function Write-SmallTvRuntimeState($State, [string]$Control, [switch]$Final) {
    # FIXED_TEST: keep valid old JSON during a rename-sharing conflict. Retry at
    # the existing heartbeat; never defer permission/disk errors or final state.
    $temporary = Join-Path $Control 'supervisor.json.tmp'
    $target = Join-Path $Control 'supervisor.json'
    [IO.File]::WriteAllText($temporary, ($State | ConvertTo-Json -Depth 12) + "`n", [Text.UTF8Encoding]::new($false))
    try {
        [IO.File]::Move($temporary, $target, $true)
    } catch {
        $failure = $_
        $code = $failure.Exception.GetBaseException().HResult -band 0xffff
        if (!$Final -and $IsWindows) {
            if ($code -eq 5) {
                # Windows can report ACCESS_DENIED for a reader denying rename.
                # If the reader already closed, one immediate retry is sufficient.
                $code = Get-SmallTvRuntimeStateSharingError $temporary $target
                if ($code -eq 0) {
                    try {[IO.File]::Move($temporary, $target, $true); return} catch {
                        $failure = $_
                        $code = $failure.Exception.GetBaseException().HResult -band 0xffff
                        if ($code -eq 5) {$code = Get-SmallTvRuntimeStateSharingError $temporary $target}
                    }
                }
            }
            if ($code -in @(32,33)) {
                $State.deferred_state_writes++
                return
            }
        }
        throw $failure
    }
}

Export-ModuleMember -Function Write-SmallTvRuntimeState
