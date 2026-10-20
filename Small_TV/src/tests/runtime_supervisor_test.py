"""Exercise real Windows child cleanup when supervisor log/state writes fail."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from runtime_supervisor_fixture import process_creation, stop_vm


def main():
    """Retain process handles before releasing controlled filesystem faults."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--supervisor', type=Path, default=Path(__file__).resolve().parents[1] / 'tools/runtime_supervisor.ps1')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    fixture = Path(__file__).with_name('runtime_supervisor_fixture.py').resolve()
    supervisor = args.supervisor.resolve()
    pwsh = Path(shutil.which('pwsh') or '')
    assert pwsh.is_file(), 'PowerShell 7 required'
    sources = [Path(__file__), fixture, supervisor, pwsh, Path(sys.executable)]
    modules = [supervisor.with_name(name) for name in ('runtime_cleanup.psm1', 'runtime_state_io.psm1')
               if supervisor.with_name(name).exists()]
    sources += modules
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    hashes = {str(path): sha(path) for path in sources}
    report = dict(passed=False, all_functionality_verified=False, scope=__doc__,
                  limitations='Real OS processes and write errors with dummy workload/guard/VM. No firmware, QMP, or H10 acceptance.',
                  inputs_sha256=hashes, cases=[])
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    canary = subprocess.Popen([sys.executable, '-c', 'import sys; sys.stdin.buffer.read()'],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for mode in ('normal', 'state-reader', 'state-readonly', 'footer', 'guard', 'stdout', 'stderr', 'cleanup-log',
                     'state-and-logs', 'passed-with-log-fault'):
            owner = out / mode
            owner.mkdir()
            root = owner / 'fixture project & тест'
            tools = root / 'Small_TV/src/tools'
            tools.mkdir(parents=True)
            (root / 'Small_TV/src/tests').mkdir()
            qemu = owner / 'qemu'
            (qemu / 'tools').mkdir(parents=True)
            shutil.copyfile(supervisor, tools / 'runtime_supervisor.ps1')
            for module in modules:
                shutil.copyfile(module, tools / module.name)
            run = owner / 'run'
            spec = owner / 'fixture.json'
            spec.write_text(json.dumps(dict(mode=mode, token=uuid.uuid4().hex, output=str(run))) + '\n')
            for role, path in [('workload', root / 'Small_TV/src/tests/runtime_qemu.py'),
                               ('guard', tools / 'runtime_run_guard.py'),
                               ('cleanup', qemu / 'tools/small_tv_vm.py')]:
                path.write_text('import runpy,sys\nsys.argv=' + repr([str(fixture), '--role', role, '--spec', str(spec)]) +
                                '+sys.argv[1:]\nrunpy.run_path(' + repr(str(fixture)) + ',run_name="__main__")\n')
            row = dict(mode=mode, passed=False)
            vm = subprocess.Popen([sys.executable, '-X', 'utf8', '-B', str(fixture), '--role', 'vm', '--spec', str(spec)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            process, handles, logs = None, {}, []
            try:
                deadline = time.monotonic() + 10
                while not (owner / 'vm-ready.json').exists():
                    assert vm.poll() is None and time.monotonic() < deadline, 'Dummy VM failed to start'
                    time.sleep(.02)
                command = [str(pwsh), '-NoProfile', '-NonInteractive', '-File', str(tools / 'runtime_supervisor.ps1'),
                    '-YoradioRoot', str(root), '-QemuRoot', str(qemu), '-OutputDirectory', str(run),
                    '-DependencyRoot', str(args.dependency_root.resolve()), '-Cycles', '1']
                logs = [(owner / ('supervisor.'+stream+'.log')).open('wb') for stream in ('stdout','stderr')]
                process = subprocess.Popen(command, stdout=logs[0], stderr=logs[1],
                    creationflags=subprocess.CREATE_NO_WINDOW)
                deadline = time.monotonic() + 20
                while len(handles) < 2:
                    assert process.poll() is None and time.monotonic() < deadline, 'Supervisor lost a child before fault release'
                    for role in ('workload', 'guard'):
                        path = owner / (role + '-identity.json')
                        if role not in handles and path.exists():
                            identity = json.loads(path.read_text())
                            assert identity['token'] == json.loads(spec.read_text())['token']
                            handle = kernel.OpenProcess(0x100000 | 0x1000 | 1, False, identity['pid'])
                            assert handle and process_creation(handle) == identity['creation'], 'Owned child identity mismatch'
                            assert kernel.WaitForSingleObject(handle, 0) == 258, 'Child not alive before release'
                            handles[role] = handle
                    time.sleep(.02)
                (owner / 'release-workload').write_text('release\n')
                # Wait on the actual process, not EOF from a leaked child's pipe.
                process.wait(timeout=25)
                for log in logs:
                    log.flush()
                stderr = (owner / 'supervisor.stderr.log').read_bytes()
                row['exit_code'] = process.returncode
                row['children_stopped'] = {role: kernel.WaitForSingleObject(handle, 0) == 0 for role, handle in handles.items()}
                row['vm_stopped'] = vm.poll() is not None
                row['unrelated_process_preserved'] = canary.poll() is None
                row['cleanup_invoked'] = (owner / 'cleanup-called.json').exists()
                assert all(row['children_stopped'].values()) and row['vm_stopped'], 'Cleanup left an owned child or VM alive'
                assert row['unrelated_process_preserved'], 'Unrelated process was terminated'
                expected_pass = mode in ('normal', 'state-reader')
                assert (process.returncode == 0) == expected_pass, 'Wrong supervisor acceptance'
                control = Path(str(run) + '-supervisor')
                state = json.loads((control / 'supervisor.json').read_text(encoding='utf-8-sig'))
                fallback = [line.split('SMALL_TV_SUPERVISOR_FINAL_STATE ', 1)[1]
                            for line in stderr.decode('utf-8', errors='replace').splitlines()
                            if line.startswith('SMALL_TV_SUPERVISOR_FINAL_STATE ')]
                if mode in ('state-and-logs', 'state-readonly'):
                    assert fallback, 'No terminal state on surviving stderr channel'
                    state = json.loads(fallback[-1])
                assert state['passed'] == expected_pass
                assert state['status'] == ('complete' if expected_pass else 'failed')
                if mode == 'state-reader':
                    assert state['deferred_state_writes'] >= 1
                if mode == 'state-readonly':
                    assert state['deferred_state_writes'] == 0, 'Real write denial was mistaken for a reader lock'
                if mode not in ('normal', 'state-reader', 'passed-with-log-fault'):
                    assert row['cleanup_invoked'], 'VM cleanup helper was skipped'
                if mode in ('stdout', 'state-and-logs'):
                    assert 'workload stderr preserved' in (control / 'workload.stderr.log').read_text()
                if mode == 'stderr':
                    assert 'workload stdout preserved' in (control / 'workload.stdout.log').read_text()
                if mode in ('stdout', 'stderr', 'cleanup-log', 'state-and-logs', 'passed-with-log-fault'):
                    assert state['cleanup_errors'], 'Write failure missing from terminal diagnostics'
                row['terminal_state'] = state
                row['passed'] = True
            except Exception as error:
                row['error'] = str(error)
                row['children_stopped'] = {role: kernel.WaitForSingleObject(handle, 0) == 0 for role, handle in handles.items()}
                row['vm_stopped'] = vm.poll() is not None
                row['supervisor_process_exited'] = process is not None and process.poll() is not None
                row['unrelated_process_preserved'] = canary.poll() is None
                row['cleanup_invoked'] = (owner / 'cleanup-called.json').exists()
            finally:
                if process is not None and process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                for handle in handles.values():
                    if kernel.WaitForSingleObject(handle, 0) == 258:
                        kernel.TerminateProcess(handle, 1)
                        kernel.WaitForSingleObject(handle, 5000)
                    kernel.CloseHandle(handle)
                if vm.poll() is None:
                    stop_vm(json.loads((owner / 'vm-ready.json').read_text()))
                    vm.wait(timeout=5)
                for log in logs:
                    log.close()
            report['cases'].append(row)
            print(mode, row['passed'], row.get('error', ''), flush=True)
    finally:
        canary.stdin.close()
        try:
            canary.wait(timeout=5)
        except subprocess.TimeoutExpired:
            canary.terminate()
            canary.wait(timeout=5)
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path,digest in hashes.items())
        report['passed'] = len(report['cases']) == 10 and all(row['passed'] for row in report['cases']) and report['inputs_unchanged']
        (out / 'report.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
