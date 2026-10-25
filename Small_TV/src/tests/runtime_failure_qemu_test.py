"""Verify failure metadata exists before cleanup of a real owned native QEMU VM."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import sys

from runtime_supervisor_fixture import process_creation


def main():
    """Inject one host exception after a genuine HTTP response; never patch the guest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    run = out / 'runtime'
    sys.path[:0] = [str(args.qemu_root.resolve() / 'tools'), str(root / 'Small_TV/qemu/parity')]
    import small_tv_vm as vm
    import small_tv_http_test as http
    import runtime_qemu
    from runtime_failure_capture import FailureCapture
    from gdb_observer import Observer
    names = ('runtime_failure_qemu_test.py', 'runtime_qemu.py', 'runtime_failure_capture.py',
             'runtime_failure_layout.py', 'runtime_memory.py', 'gdb_observer.py', 'runtime_supervisor_fixture.py')
    sources = [Path(__file__).with_name(name) for name in names]
    sources += [root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin',
                root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf', args.qemu.resolve()]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path): sha(path) for path in sources}
    report = dict(passed=False, all_functionality_verified=False, h10_checks_passed=False,
                  physical_hardware_tested=False, scope=__doc__, inputs_sha256=pins,
                  limitations=['This is an intentional host exception after a real successful start_upload response.',
                               'It proves diagnostic ordering and bounded reads, not the original H10 timeout cause.',
                               'The stop is arbitrary; task/heap metadata is diagnostic, not a stable allocator/TCP gate.'])
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle, session = None, None
    original_launch, original_control, original_http = vm.launch, vm.control, http.http
    original_capture, original_request = FailureCapture.capture, Observer.request
    active_capture, commands = [False], []
    injected = TimeoutError('Intentional diagnostic test timeout after actual HTTP 200')
    original_argv = sys.argv

    def launch(options, state):
        """Retain the newly launched VM's original kernel process object."""
        nonlocal handle, session
        session, prepared = original_launch(options, state)
        handle = kernel.OpenProcess(0x100000 | 0x1000, False, session['pid'])
        assert handle and kernel.WaitForSingleObject(handle, 0) == 258, 'Owned VM exited before observation'
        report['vm_owner'] = dict(pid=session['pid'], name=session['name'], creation=process_creation(handle))
        return session, prepared

    def guest_http(url, path, *arguments, **keywords):
        """Deliver real requests, then simulate a lost host response at one boundary."""
        result = original_http(url, path, *arguments, **keywords)
        if path == '/start_upload' and not report.get('fault_injected'):
            assert result[0] == 200, 'The real guest request did not succeed before injection'
            report['fault_injected'] = True
            report['real_guest_http_status_before_fault'] = result[0]
            raise injected
        return result

    def capture(owner, error_type):
        """Record actual diagnostic RSP commands separately from normal sampling."""
        active_capture[0] = True
        try:
            return original_capture(owner, error_type)
        finally:
            active_capture[0] = False

    def request(observer, command):
        """Audit the real observer allowlist without replacing its implementation."""
        if active_capture[0]:
            commands.append(command)
        return original_request(observer, command)

    def control(state, command):
        """Observe the artifact before quit, but never let an assertion skip cleanup."""
        if command == 'stop' and Path(state).resolve() == (run / 'vm').resolve():
            path = run / 'failure-state.json'
            report['artifact_existed_before_stop'] = path.is_file()
            if path.is_file():
                report['artifact_sha256_before_stop'] = sha(path)
        return original_control(state, command)

    vm.launch, vm.control, http.http = launch, control, guest_http
    FailureCapture.capture, Observer.request = capture, request
    try:
        sys.argv = [str(Path(runtime_qemu.__file__)), '--yoradio', str(root),
                    '--dependency-root', str(args.dependency_root.resolve()),
                    '--qemu-root', str(args.qemu_root.resolve()), '--qemu', str(args.qemu.resolve()),
                    '--output', str(run), '--cycles', '4', '--interval-seconds', '.2']
        try:
            runtime_qemu.main()
        except TimeoutError as error:
            assert error is injected, 'The original injected error was replaced'
        else:
            raise AssertionError('Intentional failure was not propagated')
        workload = json.loads((run / 'report.json').read_text())
        assert workload['passed'] is False and workload['error'] == str(injected)
        assert workload['inputs_unchanged'] and workload['no_panic'] and not workload.get('cleanup_error')
        meta = workload['failure_capture']; data = json.loads((run / meta['file']).read_text())
        assert meta['sha256'] == sha(run / meta['file']) == report['artifact_sha256_before_stop']
        assert report['artifact_existed_before_stop'] and report['fault_injected']
        assert data['vm_name'] == session['name'] and data['target_stopped'] is True
        assert data['operation'] == dict(kind='http', path='/start_upload')
        assert data['elf_sha256'] == workload['native_elf_sha256'] and data['app_sha256'] == workload['app_sha256']
        assert data['memory_reads'] <= data['memory_call_limit'] == 192
        assert data['memory_requested_bytes'] <= data['memory_read_limit'] == 32768
        assert data['elapsed_host_seconds'] < data['diagnostic_seconds_limit'] + .5
        assert set(data['registers']) == {'pc', 'sp', 'ra'}
        assert data['photo']['upload']['active'] == 1 and data['photo']['upload']['received'] == 0
        assert data['photo']['upload']['length'] == (root / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg').stat().st_size
        assert all(data['photo']['queues'][name]['address'] for name in ('jobs', 'codec_mutex', 'media_mutex'))
        assert commands and all(command.startswith(('p', 'm')) for command in commands), commands
        assert kernel.WaitForSingleObject(handle, 5000) == 0, 'Original owned VM remains alive'
        report.update(passed=True, original_vm_exited=True, diagnostic_rsp_commands=commands,
                      capture_status=data['status'], capture_errors=data['errors'],
                      capture_elapsed_host_seconds=data['elapsed_host_seconds'],
                      capture_memory_requested_bytes=data['memory_requested_bytes'])
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        sys.argv = original_argv
        vm.launch, vm.control, http.http = original_launch, original_control, original_http
        FailureCapture.capture, Observer.request = original_capture, original_request
        if handle:
            if kernel.WaitForSingleObject(handle, 0) == 258:
                report['test_fallback_cleanup_needed'] = True
                original_control(run / 'vm', 'stop')
                assert kernel.WaitForSingleObject(handle, 5000) == 0, 'Owned VM cleanup did not finish'
            kernel.CloseHandle(handle)
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path, digest in pins.items())
        report['passed'] &= report['inputs_unchanged'] and not report.get('test_fallback_cleanup_needed', False)
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({name: report.get(name) for name in ('passed', 'artifact_existed_before_stop',
          'original_vm_exited', 'capture_status', 'capture_elapsed_host_seconds', 'capture_memory_requested_bytes')}))


if __name__ == '__main__':
    main()
