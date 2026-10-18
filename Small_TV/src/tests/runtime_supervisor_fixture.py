"""Owned process fixtures for host-supervisor faults; no firmware or QMP."""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import socket
import stat
import sys
import time


def process_creation(handle):
    """Read kernel creation time so test cleanup cannot target a reused PID."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetProcessTimes.argtypes = (wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4))
    times = [wintypes.FILETIME() for _ in range(4)]
    if not kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in times)):
        raise ctypes.WinError(ctypes.get_last_error())
    return times[0].dwHighDateTime << 32 | times[0].dwLowDateTime


def write_json(path, value):
    """Write only this fixture's small local records."""
    temporary = path.with_name(path.name + '.fixture-tmp')
    temporary.write_text(json.dumps(value) + '\n', newline='\n')
    temporary.replace(path)


def stop_vm(session):
    """Stop the owned dummy through its nonce-checked loopback protocol, not QMP."""
    with socket.create_connection(('127.0.0.1', session['port']), 2) as connection:
        connection.sendall((session['token'] + '\n').encode())
        assert connection.recv(4096).decode() == session['token'], 'Wrong fixture VM'


def wait_for(path):
    """Coordinate fixture processes without sleeps or changes in guest code."""
    deadline = time.monotonic() + 20
    while not path.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError(str(path))
        time.sleep(.02)


def main():
    """Run one dummy role and introduce an actual filesystem write failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', choices=('vm', 'workload', 'guard', 'cleanup'), required=True)
    parser.add_argument('--spec', type=Path, required=True)
    args, _ = parser.parse_known_args()
    spec = json.loads(args.spec.read_text(encoding='utf-8-sig'))
    owner, run = args.spec.parent, Path(spec['output'])
    control = Path(str(run) + '-supervisor')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    identity = dict(pid=os.getpid(), token=spec['token'], creation=process_creation(kernel.GetCurrentProcess()))
    write_json(owner / (args.role + '-identity.json'), identity)
    print(args.role + ' stdout preserved', flush=True)
    print(args.role + ' stderr preserved', file=sys.stderr, flush=True)

    if args.role == 'vm':
        with socket.socket() as server:
            server.bind(('127.0.0.1', 0))
            server.listen(1)
            write_json(owner / 'vm-ready.json', dict(identity, port=server.getsockname()[1]))
            with server.accept()[0] as connection:
                connection.settimeout(3)
                assert connection.recv(4096).decode().strip() == spec['token']
                connection.sendall(spec['token'].encode())
        return 0
    if args.role == 'cleanup':
        write_json(owner / 'cleanup-called.json', identity)
        stop_vm(json.loads((run / 'vm/session.json').read_text(encoding='utf-8-sig')))
        return 0
    if args.role == 'guard':
        if spec['mode'] == 'guard':
            wait_for(owner / 'release-workload')
            return 3
        while True:
            data = json.loads((run / 'report.json').read_text(encoding='utf-8-sig'))
            if 'journal' in data:
                write_json(run / 'uptime-guard.json', dict(status='complete', passed=True, workload_passed=True))
                return 0
            time.sleep(.02)

    (run / 'vm').mkdir(parents=True)
    write_json(run / 'vm/session.json', json.loads((owner / 'vm-ready.json').read_text(encoding='utf-8-sig')))
    write_json(run / 'report.json', dict(passed=False))
    wait_for(owner / 'release-workload')
    mode = spec['mode']
    if mode == 'state-reader':
        # Model a real Windows reader that permits reads/writes but denies rename.
        kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.CreateFileW(str(control / 'supervisor.json'), 0x80000000, 3, None, 3, 0, None)
        assert handle and handle != wintypes.HANDLE(-1).value
        try:
            deadline = time.monotonic() + 8
            while True:
                try:
                    pending = json.loads((control / 'supervisor.json.tmp').read_text(encoding='utf-8-sig'))
                    if pending.get('deferred_state_writes', 0) >= 1:
                        break
                except (OSError, json.JSONDecodeError):
                    pass
                assert time.monotonic() < deadline, 'Sharing lock was not deferred'
                time.sleep(.02)
        finally:
            kernel.CloseHandle(handle)
    if mode == 'passed-with-log-fault':
        (control / 'workload.stdout.log').mkdir()
    if mode in ('normal', 'state-reader', 'passed-with-log-fault'):
        stop_vm(json.loads((run / 'vm/session.json').read_text(encoding='utf-8-sig')))
        write_json(run / 'report.json', dict(passed=True, journal={'complete': True}, inputs_unchanged=True))
        return 0
    if mode in ('stdout', 'stderr', 'state-and-logs'):
        stream = 'stderr' if mode == 'stderr' else 'stdout'
        (control / ('workload.' + stream + '.log')).mkdir()
    if mode == 'cleanup-log':
        (control / 'vm-cleanup.log').mkdir()
    if mode == 'guard':
        wait_for(owner / 'never-release')
    if mode == 'state-readonly':
        (control / 'supervisor.json').chmod(stat.S_IREAD)
        wait_for(owner / 'never-release')
    if mode == 'state-and-logs':
        # The supervisor may briefly own its temporary file during a heartbeat.
        deadline = time.monotonic() + 5
        while True:
            try:
                (control / 'supervisor.json.tmp').mkdir()
                break
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.02)
        wait_for(owner / 'never-release')
    return 7  # Missing terminal footer must never become a successful run.


if __name__ == '__main__':
    raise SystemExit(main())
