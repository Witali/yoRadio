"""Exercise real Windows detached launch, argv fidelity and duplicate protection."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time


def main():
    """Exit the launcher before releasing its live child; retain the real handle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--yoradio-root', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    options = parser.parse_args()
    folder = options.output.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    tools = Path(__file__).resolve().parents[1] / 'tools'
    module = tools / 'runtime_process.psm1'
    wrapper = tools / 'start_runtime.ps1'
    source_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (module, wrapper)}
    pwsh = shutil.which('pwsh')
    assert pwsh, 'PowerShell 7 required'
    values = ['', 'space value', 'trailing slash \\', 'embedded "quote"',
              '& ; literal $() | >', 'кириллица', 'two\\\\slashes"quoted\\']
    arguments = folder / 'arguments.json'
    arguments.write_text(json.dumps(values), encoding='utf-8')
    observed = folder / 'observed.json'
    child = folder / 'child with space & проба.ps1'
    child.write_text(r'''param([string]$Output)
$ErrorActionPreference='Stop'
@{pid=$PID;values=@($args)} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Output
$deadline=[DateTime]::UtcNow.AddSeconds(30)
while(!(Test-Path -LiteralPath ($Output+'.release'))) {
    if([DateTime]::UtcNow -ge $deadline){throw 'Release deadline expired'}
    Start-Sleep -Milliseconds 100
}
'complete' | Set-Content -LiteralPath ($Output+'.done')
''', encoding='utf-8')
    launcher = folder / 'launcher.ps1'
    launcher.write_text(r'''param($ModulePath,$Program,$ChildPath,$Output,$ValuesPath,$WorkingDirectory)
$ErrorActionPreference='Stop'
Import-Module $ModulePath -Force
$values=Get-Content -LiteralPath $ValuesPath -Raw | ConvertFrom-Json
$arguments=@('-NoProfile','-NonInteractive','-File',$ChildPath,'-Output',$Output)+@($values)
Start-SmallTvDetachedProcess -FilePath $Program -Arguments $arguments -WorkingDirectory $WorkingDirectory | ConvertTo-Json -Depth 4
''', encoding='utf-8')

    def launch(program):
        """The real parent exits before any child completion is observed."""
        return subprocess.run([pwsh, '-NoProfile', '-NonInteractive', '-File', str(launcher),
            '-ModulePath', str(module), '-Program', str(program), '-ChildPath', str(child),
            '-Output', str(observed), '-ValuesPath', str(arguments), '-WorkingDirectory', str(folder)],
            capture_output=True, text=True, encoding='utf-8', timeout=20)

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.IsProcessInJob.argtypes = (wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL))
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = None
    try:
        parent = launch(pwsh)
        assert parent.returncode == 0, parent.stderr
        identity = json.loads(parent.stdout)
        handle = kernel.OpenProcess(0x100000 | 0x1000 | 1, False, identity['pid'])
        assert handle, 'Child disappeared after launcher exit'
        assert kernel.WaitForSingleObject(handle, 0) == 258, 'Child already exited'
        in_job = wintypes.BOOL()
        assert kernel.IsProcessInJob(handle, None, ctypes.byref(in_job))
        assert not in_job.value and identity['in_job'] is False, 'Child still belongs to a Job'
        deadline = time.monotonic() + 10
        while not observed.exists() and time.monotonic() < deadline:
            time.sleep(.1)
        result = json.loads(observed.read_text(encoding='utf-8-sig'))
        assert result['values'] == values, result
        assert result['pid'] == identity['pid']
        observed.with_suffix('.json.release').write_text('release', encoding='utf-8')
        assert kernel.WaitForSingleObject(handle, 10000) == 0, 'Child did not finish'
        assert observed.with_suffix('.json.done').read_text(encoding='utf-8-sig').strip() == 'complete'
        assert launch(folder / 'missing.exe').returncode != 0, 'Missing program accepted'
        invalid = folder / 'invalid.exe'
        invalid.write_bytes(b'not an executable\n')
        assert launch(invalid).returncode != 0, 'Windows creation failure accepted'
        # A reserved launch name must fail before spawning a supervisor or VM.
        duplicate = folder / 'duplicate-runtime'
        reservation = Path(str(duplicate) + '-launch.json')
        reservation.write_text('preserve-me', encoding='utf-8')
        rejected = subprocess.run([pwsh, '-NoProfile', '-NonInteractive', '-File', str(wrapper),
            '-YoradioRoot', str(options.yoradio_root.resolve()), '-QemuRoot', str(options.qemu_root.resolve()),
            '-DependencyRoot', str(options.dependency_root.resolve()), '-OutputDirectory', str(duplicate)],
            capture_output=True, text=True, encoding='utf-8', timeout=20)
        assert rejected.returncode != 0 and reservation.read_text() == 'preserve-me'
        assert not duplicate.exists() and not Path(str(duplicate) + '-supervisor').exists()
        assert source_hashes == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (module, wrapper)}
        report = {'passed': True, 'all_functionality_verified': False,
            'scope': 'Real Windows launcher exit, independent kernel Job query, exact argv, child completion, failed creation and duplicate reservation. Not a QEMU workload or H10 pass.',
            'checks': ['child_alive_after_parent_exit', 'child_outside_job', 'exact_argv',
                'child_completed', 'missing_executable_rejected', 'invalid_executable_rejected',
                'duplicate_reserved_name_preserved', 'launcher_sources_unchanged'],
            'process': identity, 'observed_values': result['values'], 'sources_sha256': source_hashes}
        (folder / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print('PASS detached Windows runtime launch: 8 checks')
    finally:
        if handle:
            if kernel.WaitForSingleObject(handle, 0) == 258:
                kernel.TerminateProcess(handle, 1)
                kernel.WaitForSingleObject(handle, 5000)
            kernel.CloseHandle(handle)


if __name__ == '__main__':
    main()
