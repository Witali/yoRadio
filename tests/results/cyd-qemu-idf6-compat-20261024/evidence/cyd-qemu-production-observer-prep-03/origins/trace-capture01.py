"""Observe the original production flash failure with existing QEMU trace events."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import socket
import subprocess
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ('m25p80_command_decoded', 'm25p80_complete_collecting', 'm25p80_select',
          'm25p80_transfer', 'm25p80_read_data', 'm25p80_reset_done')


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def fact(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--pins-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pins_path = args.pins.resolve()
    need(fact(pins_path)['sha256'] == args.pins_sha256, 'Exact original production-input inventory')
    pins = json.loads(pins_path.read_bytes())
    out = args.output.resolve()
    need(out.parent == ROOT / '.build' and not out.exists(), 'Fresh bounded output')
    out.mkdir()
    report_path = out / 'report.json'
    report = {'scope': __doc__, 'result': 'PREPARING', 'qualified_radio_startup': False,
              'physical_device': False, 'firmware_or_model_patched': False,
              'guest_network_enabled': False, 'source_commit_of_original_image': pins['source_commit'],
              'pins': fact(pins_path), 'runner': fact(Path(__file__)), 'commands': []}

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    process = None
    channel = None
    reader = None
    incoming = queue.Queue()
    messages = []
    before = {}
    host_quit_requested = False
    started = time.monotonic()
    reader_eof = threading.Event()
    try:
        selected = pins['profiles']['pdm']
        identity_rows = [*pins['tools'].values(), *selected['files'].values(),
                         *pins['source_evidence'],
                         {'path': str(pins_path), **fact(pins_path)},
                         {'path': str(Path(__file__).resolve()), **fact(Path(__file__))}]
        for row in identity_rows:
            path = Path(row['path'])
            need(fact(path) == {'bytes': row['bytes'], 'sha256': row['sha256']}, 'Original input identity: ' + str(path))
            before[str(path)] = fact(path)
        need(before[pins['tools']['qemu']['path']]['sha256'] ==
             'f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35', 'Reviewed QEMU executable')
        image = bytearray(b'\xff') * 0x400000
        occupied = []
        for part in selected['flash_parts']:
            path = Path(selected['files'][part['file_key']]['path'])
            raw, offset = path.read_bytes(), part['offset']
            need(0 <= offset and offset + len(raw) <= len(image), 'Flash component bounds')
            need(all(offset + len(raw) <= a or offset >= b for a, b in occupied), 'Nonoverlapping flash components')
            image[offset:offset + len(raw)] = raw
            occupied.append((offset, offset + len(raw)))
        need(image[0x9000:0xe000] == b'\xff' * 0x5000, 'Fresh emulated NVS')
        flash = out / 'qemu-flash.bin'
        flash.write_bytes(image)
        flash_before = fact(flash)
        for part in selected['flash_parts']:
            raw = Path(selected['files'][part['file_key']]['path']).read_bytes()
            need(flash.read_bytes()[part['offset']:part['offset'] + len(raw)] == raw, 'Byte-exact original image components')
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
        probe.close()
        qemu = pins['tools']['qemu']['path']
        guest_name = 'cyd-flash-observer-' + uuid.uuid4().hex
        trace = out / 'flash-trace.log'
        serial = out / 'qemu.log'
        argv = [qemu, '-name', guest_name, '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet',
                '-smp', '2', '-L', str(Path(pins['tools']['rom']['path']).parent),
                '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
                '-snapshot', '-nic', 'none', '-S', '-qmp',
                'tcp:127.0.0.1:' + str(port) + ',server=on,wait=off', '-D', str(trace),
                '-drive', 'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw']
        report.update(argv=argv, flash=flash_before, original_inputs=before,
                      qmp_host='127.0.0.1', qmp_port=port, guest_name=guest_name, result='RUNNING')
        save()
        with serial.open('wb') as log:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report['owned_pid'] = process.pid
            save()
            deadline = time.monotonic() + 8
            while channel is None:
                need(process.poll() is None, 'QEMU exited before QMP connection')
                need(time.monotonic() < deadline, 'QMP connection deadline')
                try:
                    channel = socket.create_connection(('127.0.0.1', port), timeout=.25)
                    channel.settimeout(.25)
                except OSError:
                    time.sleep(.025)

            def read_qmp():
                buffer = bytearray()
                try:
                    with (out / 'qmp-received.jsonl').open('wb') as raw:
                        while True:
                            try:
                                data = channel.recv(65536)
                            except socket.timeout:
                                continue
                            if not data:
                                reader_eof.set()
                                break
                            raw.write(data)
                            raw.flush()
                            buffer.extend(data)
                            while b'\n' in buffer:
                                line, _, rest = buffer.partition(b'\n')
                                buffer[:] = rest
                                if line.strip():
                                    value = json.loads(line)
                                    messages.append(value)
                                    incoming.put(value)
                except BaseException as error:
                    incoming.put({'reader_error': type(error).__name__ + ': ' + str(error)})
                finally:
                    incoming.put({'reader_terminal': True})

            reader = threading.Thread(target=read_qmp, daemon=True)
            reader.start()

            def receive(predicate, limit=3):
                end = time.monotonic() + limit
                while True:
                    need(time.monotonic() < end, 'QMP response deadline')
                    try:
                        value = incoming.get(timeout=max(.001, min(.25, end - time.monotonic())))
                    except queue.Empty:
                        continue
                    need('reader_error' not in value and not value.get('reader_terminal'), 'QMP reader ended before response')
                    if predicate(value):
                        return value

            greeting = receive(lambda value: 'QMP' in value)
            report['qmp_greeting'] = greeting

            def command(name, arguments=None):
                ident = 'root-' + str(len(report['commands']))
                request = {'execute': name, 'id': ident}
                if arguments is not None:
                    request['arguments'] = arguments
                report['commands'].append({'request': request})
                channel.sendall(json.dumps(request).encode() + b'\n')
                response = receive(lambda value: value.get('id') == ident)
                report['commands'][-1]['response'] = response
                save()
                need('error' not in response and 'return' in response, 'QMP command rejected: ' + name)
                return response['return']

            command('qmp_capabilities')
            observed_name = command('query-name')
            need(process.poll() is None and observed_name == {'name': guest_name},
                 'Positive owned-instance identity before changing guest or trace state')
            report['owned_instance_name_verified'] = True
            initial = command('trace-event-get-state', {'name': 'm25p80_*'})
            states = {row['name']: row['state'] for row in initial}
            need(all(states.get(name) == 'disabled' for name in EVENTS), 'Selected compiled trace events initially disabled')
            for name in EVENTS:
                command('trace-event-set-state', {'name': name, 'enable': True, 'ignore-unavailable': False})
            enabled = command('trace-event-get-state', {'name': 'm25p80_*'})
            states = {row['name']: row['state'] for row in enabled}
            need(all(states.get(name) == 'enabled' for name in EVENTS), 'Selected runtime tracing enabled before guest execution')
            need(all(state == 'disabled' for name, state in states.items() if name not in EVENTS), 'Unselected byte/program traces remain disabled')
            report['trace_states_before_cont'] = enabled
            command('cont')
            end = time.monotonic() + 20
            panic_at = None
            while process.poll() is None:
                need(time.monotonic() < end, 'Bounded diagnostic guest deadline')
                need(not trace.exists() or trace.stat().st_size < 32 * 1024 * 1024, 'Bounded trace output')
                text = serial.read_text(encoding='utf-8', errors='replace')
                if 'assert failed:' in text:
                    # Poll normally while the original -no-reboot path exits.
                    panic_at = time.monotonic() if panic_at is None else panic_at
                    if time.monotonic() - panic_at >= 3:
                        host_quit_requested = True
                        command('quit')
                        break
                time.sleep(.025)
            process.wait(timeout=5)
            reader.join(timeout=3)
            need(not reader.is_alive() and reader_eof.is_set(), 'Actual QMP EOF and reader join')
        text = serial.read_text(encoding='utf-8', errors='replace')
        need('Failed to set QIE bit' in text and 'esp_flash_spi_init.c:654' in text, 'Same original flash-init failure observed')
        need('Starting pure ESP-IDF yoRadio' not in text, 'No application startup claim')
        need(trace.is_file() and 0 < trace.stat().st_size <= 32 * 1024 * 1024,
             'Actual trace backend output within final size bound')
        trace_text = trace.read_text(encoding='utf-8', errors='replace')
        recorded_events = re.findall(r'\b(m25p80_[a-z0-9_]+)\b', trace_text)
        event_counts = {name: recorded_events.count(name) for name in EVENTS}
        need(set(recorded_events) <= set(EVENTS) and event_counts['m25p80_command_decoded'] > 0
             and event_counts['m25p80_transfer'] > 0, 'Actual selected command/transfer trace records')
        need(process.returncode == 0, 'Normal actual QEMU terminal status')
        shutdowns = [m.get('data', {}) for m in messages if m.get('event') == 'SHUTDOWN']
        expected_shutdown = {'guest': not host_quit_requested,
                             'reason': 'host-qmp-quit' if host_quit_requested else 'guest-reset'}
        need(len(shutdowns) == 1 and shutdowns[0] == expected_shutdown,
             'Expected observed QMP shutdown, separate from startup qualification')
        report.update(result='ORIGINAL_BOOT_FAILURE_TRACED', guest_flash_assert_observed=True,
                      qmp_eof_observed=reader_eof.is_set(), qmp_reader_joined=True,
                      qmp_events=[m for m in messages if 'event' in m],
                      trace=fact(trace), serial=fact(serial), qemu_exit_code=process.returncode,
                      trace_event_counts=event_counts, expected_shutdown=expected_shutdown,
                      host_quit_requested=host_quit_requested)
        need(fact(flash) == flash_before, 'Disposable snapshot leaves image unchanged')
        need(all(fact(Path(name)) == row for name, row in before.items()), 'Every selected original input unchanged')
        report['all_original_inputs_unchanged'] = True
        report['scratch_flash_unchanged'] = True
    except BaseException as error:
        report.update(result='DIAGNOSTIC_INCOMPLETE', error_type=type(error).__name__, reason=str(error))
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            report['forced_process_cleanup'] = True
        if channel is not None:
            channel.close()
        if reader is not None:
            reader.join(timeout=2)
        changed = []
        for name, row in before.items():
            try:
                if fact(Path(name)) != row:
                    changed.append(name)
            except OSError:
                changed.append(name)
        report['changed_input_paths'] = changed
        report['all_original_inputs_unchanged'] = not changed
        if changed:
            report.update(result='DIAGNOSTIC_INCOMPLETE', reason='A pinned input changed')
        report.update(elapsed_seconds=time.monotonic() - started,
                      actual_qemu_exit_code=process.returncode if process is not None else None)
        save()
    print(json.dumps({k: report[k] for k in ('result', 'qualified_radio_startup', 'physical_device')}))
    return 0 if report['result'] == 'ORIGINAL_BOOT_FAILURE_TRACED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
