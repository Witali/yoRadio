"""Test idempotent VM cleanup with real Windows processes and stale identities."""
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from runtime_supervisor_fixture import process_creation, stop_vm


def read_record(path):
    """Retry a transient Windows sharing conflict without restarting its producer."""
    deadline = time.monotonic() + 5
    while True:
        try:
            return json.loads(path.read_text())
        except (PermissionError, FileNotFoundError, json.JSONDecodeError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(.02)


def owned_process(identity):
    """Retain the fixture's kernel identity and read its actual executable image."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                ctypes.POINTER(wintypes.DWORD))
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, identity['pid'])
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        assert process_creation(handle) == identity['creation'], 'Fixture PID was reused'
        buffer = ctypes.create_unicode_buffer(32768); size = wintypes.DWORD(len(buffer))
        if not kernel.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        return kernel, handle, buffer.value
    except BaseException:
        kernel.CloseHandle(handle)
        raise


def main():
    """Keep live canaries intact while exercising real helper success and refusal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    fixture = Path(__file__).with_name('runtime_supervisor_fixture.py')
    module = root / 'Small_TV/src/tools/runtime_cleanup.psm1'
    pwsh = Path(shutil.which('pwsh') or '')
    assert pwsh.is_file(), 'PowerShell 7 is required'
    sources = [Path(__file__), fixture, module, pwsh, Path(sys.executable)]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path): sha(path) for path in sources}
    probe = out / 'probe.ps1'
    probe.write_text('''param($Module,$Python,$Helper,$Session,$Control,$Output)
$ErrorActionPreference='Stop'
Import-Module $Module -Force
$state=[ordered]@{status='failed';passed=$false;cleanup_errors=[Collections.Generic.List[object]]::new()}
Invoke-SmallTvRuntimeVmCleanup $Python $Helper $Session $Control $state
$state|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $Output -Encoding utf8
''')
    helper = out / 'helper.py'
    helper.write_text('''import ctypes,json,sys
from ctypes import wintypes
from pathlib import Path
sys.path.insert(0,''' + repr(str(fixture.parent)) + ''')
from runtime_supervisor_fixture import stop_vm,process_creation
state=Path(sys.argv[-1]);session=json.loads((state/'session.json').read_text())
(state.parent/'helper-called').write_text('called')
print('helper stdout retained',flush=True);print('helper stderr retained',file=sys.stderr,flush=True)
if session['helper_mode']=='fail':sys.exit(7)
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);kernel.OpenProcess.restype=wintypes.HANDLE
kernel.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD)
kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
handle=kernel.OpenProcess(0x100000|0x1000,False,session['fixture_pid'])
assert handle and process_creation(handle)==session['creation']
try:
 stop_vm(session)
 assert kernel.WaitForSingleObject(handle,5000)==0,'Original fixture did not exit'
finally:kernel.CloseHandle(handle)
sys.exit(7 if session['helper_mode']=='close-error' else 0)
''')
    cases = []
    modes = ('already-exited', 'live-helper-fails', 'helper-stops-then-fails', 'helper-stops-success',
             'later-process-at-pid', 'different-image', 'legacy-live-helper-fails', 'legacy-stops-success',
             'malformed-time', 'invalid-pid', 'string-pid', 'negative-pid', 'malformed-time-helper-stops')
    for mode in modes:
        folder = out / mode; folder.mkdir()
        run = folder / 'run'; vm_dir = run / 'vm'; vm_dir.mkdir(parents=True)
        control = folder / 'control'; control.mkdir()
        spec = folder / 'fixture.json'
        spec.write_text(json.dumps(dict(mode='normal', token=mode + '-owned-canary', output=str(run))))
        vm = subprocess.Popen([sys.executable, '-B', str(fixture), '--role', 'vm', '--spec', str(spec)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        kernel = handle = fixture_record = None
        try:
            deadline = time.monotonic() + 10
            while not (folder / 'vm-ready.json').exists():
                assert vm.poll() is None and time.monotonic() < deadline, 'Fixture startup failed'
                time.sleep(.02)
            fixture_record = read_record(folder / 'vm-ready.json')
            session = dict(fixture_record)
            kernel, handle, image = owned_process(session)
            session.update(qemu=image, started_utc=datetime.now(timezone.utc).isoformat(),
                           fixture_pid=session['pid'], helper_mode='fail')
            if mode == 'already-exited':
                stop_vm(session); vm.wait(timeout=5)
            elif mode in ('helper-stops-success', 'legacy-stops-success'):
                session['helper_mode'] = 'close-success'
            elif mode == 'helper-stops-then-fails': session['helper_mode'] = 'close-error'
            elif mode == 'later-process-at-pid':
                session['started_utc'] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            elif mode == 'different-image': session['qemu'] = str(pwsh)
            elif mode.startswith('malformed-time'):
                session['started_utc'] = 'not-a-time'
                if mode.endswith('helper-stops'): session['helper_mode'] = 'close-success'
            elif mode == 'invalid-pid': session['pid'] = 0
            elif mode == 'string-pid': session['pid'] = str(session['pid'])
            elif mode == 'negative-pid': session['pid'] = -session['pid']
            if mode.startswith('legacy-'):
                session.pop('qemu'); session.pop('started_utc')
            (vm_dir / 'session.json').write_text(json.dumps(session))
            output = folder / 'state.json'
            result = subprocess.run([str(pwsh), '-NoProfile', '-NonInteractive', '-File', str(probe),
                                     '-Module', str(module), '-Python', sys.executable, '-Helper', str(helper),
                                     '-Session', str(vm_dir), '-Control', str(control), '-Output', str(output)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            assert result.returncode == 0, result.stderr.decode(errors='replace')
            state = json.loads(output.read_text(encoding='utf-8-sig'))
            assert state['passed'] is False and state['status'] == 'failed', 'Workload failure was hidden'
            failed = mode in ('live-helper-fails', 'legacy-live-helper-fails', 'malformed-time',
                              'invalid-pid', 'string-pid', 'negative-pid', 'malformed-time-helper-stops')
            assert bool(state['cleanup_errors']) == failed, state
            called = (run / 'helper-called').exists()
            expected_called = mode not in ('already-exited', 'later-process-at-pid', 'different-image')
            assert called == expected_called, (mode, state)
            should_exit = mode in ('already-exited', 'helper-stops-then-fails', 'helper-stops-success',
                                   'legacy-stops-success', 'malformed-time-helper-stops')
            if should_exit:
                vm.wait(timeout=5)
            else:
                assert vm.poll() is None, 'Unrelated/live canary was stopped'
            if called:
                log = (control / 'vm-cleanup.log').read_text()
                assert 'helper stdout retained' in log and 'helper stderr retained' in log
                assert state['vm_cleanup_exit_code'] == (7 if session['helper_mode'] in ('fail', 'close-error') else 0)
            cases.append(dict(mode=mode, passed=True, helper_called=called, canary_exited=should_exit,
                              cleanup_errors=state['cleanup_errors'],
                              action=state.get('vm_cleanup_action'), owner_status=state.get('vm_cleanup_owner_status')))
        finally:
            if vm.poll() is None:
                stop_vm(fixture_record or read_record(folder / 'vm-ready.json'))
                vm.wait(timeout=5)
            if handle is not None:
                kernel.CloseHandle(handle)
    assert all(sha(Path(path)) == digest for path, digest in pins.items())
    report = dict(passed=True, scope=__doc__, all_functionality_verified=False, h10_checks_passed=False,
                  no_physical_hardware_access=True, cases=cases, inputs_sha256=pins, inputs_unchanged=True,
                  limitations=['Owned real OS canaries; the later-process case supplies a deliberately stale session time.',
                               'This test does not claim an actual kernel PID-reuse event or exercise QMP/firmware.'])
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=True, cases=len(cases), inputs_unchanged=True)))


if __name__ == '__main__':
    main()
