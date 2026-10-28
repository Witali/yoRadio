"""Verify failed host-state writes clean up a real owned Small TV QEMU run."""
import argparse
import ctypes
from ctypes import wintypes
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from runtime_supervisor_fixture import process_creation


def main():
    """Fault only host output files after retaining verified native process handles."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--qemu', type=Path, help='Explicit candidate executable; preserve the frozen helper bundle')
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    root = args.yoradio.resolve()
    tools = root / 'Small_TV/src/tools'
    pwsh = Path(shutil.which('pwsh') or '')
    assert pwsh.is_file(), 'PowerShell 7 required'
    run = out / 'runtime'
    executable = (args.qemu or args.qemu_root / 'bin/qemu-system-riscv32.exe').resolve()
    control = Path(str(run) + '-supervisor')
    inputs = [Path(__file__), Path(__file__).with_name('runtime_supervisor_fixture.py'),
              tools / 'runtime_supervisor.ps1', tools / 'runtime_cleanup.psm1', tools / 'runtime_state_io.psm1',
              root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin',
              root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf',
              executable, pwsh]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    hashes = {str(path): sha(path) for path in inputs}
    report = dict(passed=False, all_functionality_verified=False, scope=__doc__,
                  limitations='A deliberate host filesystem fault tests process cleanup, not completed H10 or full firmware acceptance.',
                  inputs_sha256=hashes)
    command = [str(pwsh), '-NoProfile', '-NonInteractive', '-File', str(tools / 'runtime_supervisor.ps1'),
        '-YoradioRoot', str(root), '-QemuRoot', str(args.qemu_root.resolve()),
        '-DependencyRoot', str(args.dependency_root.resolve()), '-OutputDirectory', str(run),
        '-Cycles', '100000', '-IntervalSeconds', '15']
    if args.qemu:
        command += ['-QemuExecutable', str(executable)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    handles = {}
    try:
        deadline = time.monotonic() + 90
        while True:
            assert process.poll() is None, 'Supervisor exited before fault release'
            try:
                state = json.loads((control / 'supervisor.json').read_text(encoding='utf-8-sig'))
                session = json.loads((run / 'vm/session.json').read_text())
                if state.get('guard_pid') and (run / 'uptime-guard.json').exists():
                    break
            except (OSError, json.JSONDecodeError):
                pass
            assert time.monotonic() < deadline, 'Native workload/guard never became ready'
            time.sleep(.05)
        roles = dict(workload=int(state['workload_pid']), guard=int(state['guard_pid']), vm=int(session['pid']))
        # Only numeric PIDs enter this read-only OS command; no file paths are shell code.
        script = 'Get-CimInstance Win32_Process | Where-Object ProcessId -In ' + ','.join(map(str, roles.values()))
        script += ' | Select-Object ProcessId,ExecutablePath,CommandLine,CreationDate | ConvertTo-Json'
        identities = json.loads(subprocess.check_output([str(pwsh), '-NoProfile', '-NonInteractive', '-Command', script], encoding='utf-8-sig'))
        assert {row['ProcessId'] for row in identities} == set(roles.values())
        for role, pid in roles.items():
            identity = next(row for row in identities if row['ProcessId'] == pid)
            command_line = identity['CommandLine'].replace('/', '\\').lower()
            if role == 'vm':
                assert session['name'].lower() in command_line
                assert Path(identity['ExecutablePath']).resolve() == executable
            else:
                expected = 'runtime_qemu.py' if role == 'workload' else 'runtime_run_guard.py'
                assert expected in command_line and str(run).replace('/', '\\').lower() in command_line
            handle = kernel.OpenProcess(0x100000 | 0x1000 | 1, False, pid)
            assert handle, 'Owned native process disappeared before fault release'
            handles[role] = handle
            created = process_creation(handle)
            observed = dt.datetime.fromisoformat(identity['CreationDate']).timestamp()
            assert abs(created / 10000000 - 11644473600 - observed) < .002, 'PID was reused during identity check'
            assert kernel.WaitForSingleObject(handle, 0) == 258
        report['processes_before_fault'] = identities
        report['pre_fault_guard'] = json.loads((run / 'uptime-guard.json').read_text())
        (control / 'workload.stdout.log').mkdir()
        deadline = time.monotonic() + 5
        while True:
            try:
                (control / 'supervisor.json.tmp').mkdir()
                break
            except FileExistsError:
                assert time.monotonic() < deadline
                time.sleep(.02)
        stdout, stderr = process.communicate(timeout=30)
        (out / 'supervisor.stdout.log').write_bytes(stdout)
        (out / 'supervisor.stderr.log').write_bytes(stderr)
        report['supervisor_exit_code'] = process.returncode
        report['owned_processes_stopped'] = {role: kernel.WaitForSingleObject(handle, 0) == 0 for role,handle in handles.items()}
        assert process.returncode != 0 and all(report['owned_processes_stopped'].values())
        fallback = [line.split('SMALL_TV_SUPERVISOR_FINAL_STATE ', 1)[1]
                    for line in stderr.decode('utf-8', errors='replace').splitlines()
                    if line.startswith('SMALL_TV_SUPERVISOR_FINAL_STATE ')]
        assert fallback, 'Final failed state was lost when its disk file was unwritable'
        final = json.loads(fallback[-1])
        assert final['status'] == 'failed' and not final['passed'] and final['vm_cleanup_exit_code'] == 0
        assert final['cleanup_errors'] and final['finished_utc']
        report['failed_terminal_state'] = final
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if process.poll() is None:
            # Let the real supervisor perform its verified cleanup even if the
            # observer failed before it could retain every child handle.
            report['test_requested_supervisor_abort'] = True
            deadline = time.monotonic() + 2
            while control.exists() and time.monotonic() < deadline:
                try:
                    (control / 'supervisor.json.tmp').mkdir()
                    break
                except FileExistsError:
                    if (control / 'supervisor.json.tmp').is_dir():
                        break
                    time.sleep(.02)
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)
        report['test_cleanup_needed'] = []
        for role, handle in handles.items():
            if kernel.WaitForSingleObject(handle, 0) == 258:
                report['test_cleanup_needed'].append(role)
                kernel.TerminateProcess(handle, 1)
                kernel.WaitForSingleObject(handle, 5000)
            kernel.CloseHandle(handle)
        stdout, stderr = process.communicate(timeout=5)
        (out / 'supervisor.stdout.log').write_bytes(stdout)
        (out / 'supervisor.stderr.log').write_bytes(stderr)
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path,digest in hashes.items())
        report['passed'] = report['passed'] and report['inputs_unchanged'] and not report['test_cleanup_needed']
        (out / 'report.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print('PASS real QEMU supervisor write-failure cleanup')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
