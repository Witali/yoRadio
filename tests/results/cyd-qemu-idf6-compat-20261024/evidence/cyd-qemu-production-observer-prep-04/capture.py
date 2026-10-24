"""Observe unchanged production PDM on one separately pinned emulator; no boot qualification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
import time
import uuid


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_PINS_SHA256 = 'f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12'
ORIGINAL_QEMU_SHA256 = 'f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35'
ORIGINAL_SOURCE = '3a563324abdca56144a40d5759def0ccfe708b3c'
ORIGINAL_APP_SHA256 = '66e99cfb4773bad31cd646ec22e0cdda5d1231bf9b3ea74a6940401aea98ecf3'
EXPECTED_NEW_QEMU = ROOT / '.build/cyd-qemu-idf6-build-02/qemu-system-xtensa.exe'
ORIGINS = (
    (ROOT / '.build/cyd-qemu-production-observer-prep-03/capture.py',
     'd3ffa0230bb7caa983fc04758176222230074d55b54f985ececeb90370b0d1f6'),
    (ROOT / '.build/cyd-qemu-flash-trace-prep-01/capture.py',
     'e353d95cfd22faf0282a4357d8d7bea8f7ec82b60e6b38a5a12749a089a5a652'),
    (ROOT / 'tests/results/cyd-production-radio-boot-20261020/preparation/capture.py',
     'abc29b18e694d7a48abd5a90ed30da983cfea0650e40ec0a468b0afde2205f80'),
    (ROOT / '.build/cyd-qemu-production-observer-prep-02/capture.py',
     'dea7385425b2a05a0d57f769bafb84a00b8dc528ea45681ba190de0391722d7b'),
    (ROOT / '.build/cyd-qemu-idf6-compat-review-20261024-01/review.json',
     '2de220f1c540ea4db351b318feee0a256b502f7164ef50badfb2bf583b26480d'),
)
EVENTS = ('m25p80_command_decoded', 'm25p80_complete_collecting', 'm25p80_select',
          'm25p80_transfer', 'm25p80_read_data', 'm25p80_reset_done')
MAX_BYTES = 32 * 1024 * 1024
OBSERVATION_SECONDS = 20
PANIC_GRACE_SECONDS = 3
PANIC = re.compile(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|'
                   r'watchdog.*triggered|LoadProhibited|StoreProhibited', re.I)
STARTUP_ERROR = re.compile(r'NVS init failed|SPIFFS mount failed|Audio service failed|'
                           r'Radio control failed|Web server failed|Health sampler initialization failed|'
                           r'Time service unavailable|Network settings unavailable|'
                           r'TLS input reclamation not attached', re.I)


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def fact(path):
    raw = Path(path).read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def observation(text):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    markers = dict(
        after_early_mpi=text.count('Starting pure ESP-IDF yoRadio (Arduino-free)') == 1,
        display_driver_entered='ST7789: SPI2 DMA' in text,
        pipeline_owners_ready='Pipeline ready: I2S PDM,' in text,
        radio_control_entered='Smart Start state: 2' in text,
        web_service_ready=bool(re.search(r'Native HTTPS? server started', text)))
    return dict(markers=markers,
                application_start_banner_count=text.count('Starting pure ESP-IDF yoRadio (Arduino-free)'),
                network_failure_observed='Network failed:' in text,
                early_mpi_prepare_returned=markers['after_early_mpi'],
                display_init_and_clear_returned=markers['pipeline_owners_ready'] or markers['web_service_ready'],
                audio_owners_created=markers['pipeline_owners_ready'],
                radio_control_initialized=markers['radio_control_entered'] and markers['web_service_ready'],
                panic_observed=bool(PANIC.search(text)),
                startup_error_observed=bool(STARTUP_ERROR.search(text)),
                original_qie_failure_observed='Failed to set QIE bit' in text,
                original_flash_assert_observed='esp_flash_spi_init.c:654' in text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--pins-sha256', required=True)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--qemu-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pins_path, qemu, out = args.pins.resolve(), args.qemu.resolve(), args.output.resolve()
    need(args.pins_sha256 == ORIGINAL_PINS_SHA256, 'Reviewed original production inventory digest')
    need(fact(pins_path)['sha256'] == ORIGINAL_PINS_SHA256, 'Original production inventory bytes')
    need(qemu == EXPECTED_NEW_QEMU.resolve(), 'Task-local rebuilt executable path')
    need(re.fullmatch(r'[0-9a-f]{64}', args.qemu_sha256), 'Explicit lowercase rebuilt executable digest')
    need(fact(qemu)['sha256'] == args.qemu_sha256, 'Rebuilt executable bytes')
    need(out.parent == ROOT / '.build' and not out.exists(), 'Fresh direct .build child')
    pins = json.loads(pins_path.read_bytes())
    out.mkdir()
    report_path = out / 'report.json'
    serial, stderr, trace, qmp_log = (out / name for name in
                                     ('uart.log', 'qemu-stderr.log', 'flash-trace.log', 'qmp-received.jsonl'))
    artifact_paths = (serial, stderr, trace, qmp_log)
    report = dict(scope=__doc__, result='PREPARING', profile='pdm',
                  source_commit_of_original_image=ORIGINAL_SOURCE,
                  full_radio_startup_qualified=False, startup_qualified=False,
                  network_association_qualified=False, network_traffic_qualified=False,
                  audio_output_qualified=False, physical_qualification=False,
                  static_rx_loan_exercised=False, reserve_performance_qualified=False,
                  firmware_patched=False, emulator_model_patched=True,
                  firmware_or_model_patched=True, host_network_backend='none',
                  host_audio_backend='none', physical_device=False,
                  qmp_transport='owned-child-stdio', commands=[],
                  guest_execution_started=False,
                  original_pins=fact(pins_path), runner=fact(Path(__file__)),
                  qemu=fact(qemu), observation_seconds=OBSERVATION_SECONDS,
                  per_artifact_size_limit=MAX_BYTES)
    report.update(observation(''))

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def check_bounds():
        for path in artifact_paths:
            need(not path.exists() or path.stat().st_size <= MAX_BYTES,
                 'Artifact exceeds accepted size bound: ' + path.name)

    process = reader = None
    incoming = queue.Queue()
    messages = []
    reader_status = dict(actual_eof=False, joined=False, error=None,
                         bytes_received=0, controller_closed_stdout=False)
    before = {}
    preflight_completed = False
    flash = out / 'qemu-flash.bin'
    flash_before = None
    host_quit_requested = False
    started = time.monotonic()
    save()
    try:
        selected = pins['profiles']['pdm']
        need(pins['source_commit'] == selected['source_commit'] == ORIGINAL_SOURCE,
             'Original production source identity')
        need(selected['backend'] == 'pdm' and selected['app_sha256'] == ORIGINAL_APP_SHA256,
             'Original saved PDM application identity')
        need(pins['tools']['qemu']['sha256'] == ORIGINAL_QEMU_SHA256, 'Original emulator identity retained')
        identity_rows = [*pins['tools'].values(), *selected['files'].values(), *pins['source_evidence'],
                         {'path': str(pins_path), **fact(pins_path)},
                         {'path': str(qemu), **fact(qemu)},
                         {'path': str(Path(__file__).resolve()), **fact(Path(__file__))}]
        for path, digest in ORIGINS:
            current = fact(path)
            need(current['sha256'] == digest, 'Unchanged source origin: ' + str(path))
            identity_rows.append({'path': str(path), **current})
        for row in identity_rows:
            path = Path(row['path'])
            current = fact(path)
            need(current == {'bytes': row['bytes'], 'sha256': row['sha256']},
                 'Pinned input identity: ' + str(path))
            before[str(path)] = current
        need(before[str(qemu)]['sha256'] == args.qemu_sha256, 'Explicit rebuilt executable pin retained')
        preflight_completed = True
        report.update(input_preflight_completed=True, original_inputs=before)
        image = bytearray(b'\xff') * 0x400000
        occupied = []
        for part in selected['flash_parts']:
            raw = Path(selected['files'][part['file_key']]['path']).read_bytes()
            offset = part['offset']
            need(0 <= offset and offset + len(raw) <= len(image), 'Flash component bounds')
            need(all(offset + len(raw) <= a or offset >= b for a, b in occupied),
                 'Nonoverlapping original components')
            image[offset:offset + len(raw)] = raw
            occupied.append((offset, offset + len(raw)))
        need(image[0x9000:0xe000] == b'\xff' * 0x5000, 'Fresh emulated NVS')
        flash.write_bytes(image)
        flash_before = fact(flash)
        need(flash.read_bytes() == image, 'Byte-exact scratch flash write')
        for part in selected['flash_parts']:
            raw = Path(selected['files'][part['file_key']]['path']).read_bytes()
            need(image[part['offset']:part['offset'] + len(raw)] == raw,
                 'Byte-exact original flash components')
        serial.touch(exist_ok=False)
        guest_name = 'cyd-production-observer-' + uuid.uuid4().hex
        argv = [str(qemu), '-name', guest_name, '-audiodev', 'none,id=quiet',
                '-M', 'esp32,st7789=on,audiodev=quiet', '-smp', '2',
                '-L', str(Path(pins['tools']['rom']['path']).parent),
                '-display', 'none', '-monitor', 'none',
                '-serial', 'file:' + str(serial).replace(',', ',,'),
                '-no-reboot', '-snapshot', '-nic', 'none', '-S', '-qmp', 'stdio',
                '-D', str(trace), '-drive',
                'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw']
        report.update(argv=argv, guest_name=guest_name, flash_before=flash_before, result='RUNNING')
        save()
        with stderr.open('wb') as errors:
            process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=errors, bufsize=0,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report['owned_pid'] = process.pid
            save()

            def read_qmp():
                buffer = bytearray()
                try:
                    with qmp_log.open('wb') as raw:
                        while True:
                            data = os.read(process.stdout.fileno(), 65536)
                            if data == b'':
                                reader_status['actual_eof'] = True
                                need(not buffer.strip(), 'QMP EOF with incomplete JSON frame')
                                break
                            reader_status['bytes_received'] += len(data)
                            raw.write(data)
                            raw.flush()
                            need(reader_status['bytes_received'] <= MAX_BYTES, 'QMP output size bound')
                            buffer.extend(data)
                            while b'\n' in buffer:
                                line, _, rest = buffer.partition(b'\n')
                                buffer[:] = rest
                                if line.strip():
                                    value = json.loads(line)
                                    need(isinstance(value, dict), 'QMP dictionary frame')
                                    messages.append(value)
                                    incoming.put(value)
                except BaseException as error:
                    reader_status['error'] = type(error).__name__ + ': ' + str(error)
                    incoming.put({'reader_error': reader_status['error']})
                finally:
                    incoming.put({'reader_terminal': True})

            reader = threading.Thread(target=read_qmp, daemon=True)
            reader.start()

            def receive(predicate, limit=3):
                end = time.monotonic() + limit
                while True:
                    check_bounds()
                    need(time.monotonic() < end, 'QMP response deadline')
                    try:
                        value = incoming.get(timeout=max(.001, min(.25, end - time.monotonic())))
                    except queue.Empty:
                        continue
                    need('reader_error' not in value and not value.get('reader_terminal'),
                         'QMP reader ended before response')
                    if predicate(value):
                        return value

            def command(name, arguments=None):
                ident = 'root-' + str(len(report['commands']))
                request = {'execute': name, 'id': ident}
                if arguments is not None:
                    request['arguments'] = arguments
                report['commands'].append({'request': request})
                payload = json.dumps(request).encode() + b'\n'
                need(process.stdin.write(payload) == len(payload), 'Full owned QMP request write')
                process.stdin.flush()
                response = receive(lambda value: value.get('id') == ident)
                report['commands'][-1]['response'] = response
                save()
                need('error' not in response and 'return' in response, 'QMP command rejected: ' + name)
                return response['return']

            report['qmp_greeting'] = receive(lambda value: 'QMP' in value)
            command('qmp_capabilities')
            observed_name = command('query-name')
            need(process.poll() is None and observed_name == {'name': guest_name},
                 'Owned unique guest before VM or trace mutations')
            report['owned_instance_name_verified'] = True
            initial = command('trace-event-get-state', {'name': 'm25p80_*'})
            states = {row['name']: row['state'] for row in initial}
            need(all(states.get(name) == 'disabled' for name in EVENTS), 'Required compiled events initially disabled')
            for name in EVENTS:
                command('trace-event-set-state', {'name': name, 'enable': True, 'ignore-unavailable': False})
            enabled = command('trace-event-get-state', {'name': 'm25p80_*'})
            states = {row['name']: row['state'] for row in enabled}
            need(all(states.get(name) == 'enabled' for name in EVENTS), 'Required events enabled before cont')
            need(all(state == 'disabled' for name, state in states.items() if name not in EVENTS),
                 'Unselected event states remain disabled')
            report['trace_states_before_cont'] = enabled
            command('cont')
            report['guest_execution_started'] = True
            guest_started = time.monotonic()
            end = guest_started + OBSERVATION_SECONDS
            panic_at = None
            while process.poll() is None:
                check_bounds()
                need(reader_status['error'] is None, 'QMP reader error during observation')
                now = time.monotonic()
                current = observation(serial.read_text(encoding='utf-8', errors='replace'))
                report.update(current)
                if current['panic_observed']:
                    panic_at = now if panic_at is None else panic_at
                if now >= end or (panic_at is not None and now - panic_at >= PANIC_GRACE_SECONDS):
                    host_quit_requested = True
                    report['host_stop_reason'] = ('panic_grace_expired' if panic_at is not None
                                                  else 'observation_deadline')
                    command('quit')
                    break
                time.sleep(.025)
            process.wait(timeout=5)
            reader.join(timeout=3)
            reader_status['joined'] = not reader.is_alive()
            need(reader_status['joined'] and reader_status['actual_eof'] and reader_status['error'] is None,
                 'Strict actual QMP EOF, no reader error and reader join')
            report['guest_observation_seconds'] = time.monotonic() - guest_started
        check_bounds()
        need(all(path.is_file() for path in artifact_paths), 'All observation artifacts exist')
        report.update(observation(serial.read_text(encoding='utf-8', errors='replace')))
        trace_text = trace.read_text(encoding='utf-8', errors='replace')
        emitted = re.findall(r'\b(m25p80_[a-z0-9_]+)\b', trace_text)
        counts = {name: emitted.count(name) for name in EVENTS}
        need(set(emitted) <= set(EVENTS) and counts['m25p80_command_decoded'] > 0
             and counts['m25p80_transfer'] > 0, 'Actual selected command and transfer trace records')
        need(process.returncode == 0, 'Normal actual QEMU terminal status')
        shutdowns = [m.get('data', {}) for m in messages if m.get('event') == 'SHUTDOWN']
        expected_shutdown = {'guest': not host_quit_requested,
                             'reason': 'host-qmp-quit' if host_quit_requested else 'guest-reset'}
        need(len(shutdowns) == 1 and shutdowns[0] == expected_shutdown, 'Exact expected QMP SHUTDOWN')
        need(fact(flash) == flash_before, 'Scratch snapshot remains unchanged')
        need(all(fact(Path(name)) == row for name, row in before.items()), 'Every selected input remains unchanged')
        report.update(result='OBSERVATION_COMPLETED', trace_event_counts=counts,
                      expected_shutdown=expected_shutdown, host_quit_requested=host_quit_requested)
    except BaseException as error:
        report.update(result='DIAGNOSTIC_INCOMPLETE', error_type=type(error).__name__, reason=str(error))
    finally:
        cleanup_errors = []
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                report['forced_process_cleanup'] = True
            except BaseException as error:
                cleanup_errors.append(type(error).__name__ + ': ' + str(error))
        if reader is not None:
            reader.join(timeout=3)
            reader_status['joined'] = not reader.is_alive()
        if process is not None:
            for stream_name in ('stdin', 'stdout'):
                stream = getattr(process, stream_name)
                if stream is not None:
                    try:
                        if stream_name == 'stdout' and reader is not None and reader.is_alive():
                            reader_status['controller_closed_stdout'] = True
                        stream.close()
                    except BaseException as error:
                        cleanup_errors.append(type(error).__name__ + ': ' + str(error))
        report.update(qmp_reader=reader_status, qmp_events=[m for m in messages if 'event' in m],
                      host_quit_requested=host_quit_requested, cleanup_errors=cleanup_errors,
                      actual_qemu_exit_code=process.returncode if process is not None else None)
        after, changed = {}, []
        for name, expected in before.items():
            try:
                after[name] = fact(Path(name))
                if after[name] != expected:
                    changed.append(name)
            except OSError as error:
                after[name] = {'error': type(error).__name__ + ': ' + str(error)}
                changed.append(name)
        report.update(inputs_after=after, changed_input_paths=changed,
                      input_preflight_completed=preflight_completed,
                      all_selected_inputs_unchanged=preflight_completed and not changed)
        scratch_unchanged = False
        if flash_before is not None:
            try:
                report['flash_after'] = fact(flash)
                scratch_unchanged = report['flash_after'] == flash_before
            except OSError as error:
                report['flash_after'] = {'error': type(error).__name__ + ': ' + str(error)}
        report['scratch_flash_unchanged'] = scratch_unchanged
        artifacts = {}
        for path in artifact_paths:
            try:
                if path.is_file():
                    artifacts[path.name] = fact(path)
            except OSError as error:
                artifacts[path.name] = {'error': type(error).__name__ + ': ' + str(error)}
        report['artifacts'] = artifacts
        if report['result'] == 'OBSERVATION_COMPLETED':
            terminal_ok = (not cleanup_errors and not changed and preflight_completed and scratch_unchanged
                           and reader_status['actual_eof'] and reader_status['joined']
                           and reader_status['error'] is None and not reader_status['controller_closed_stdout']
                           and all(artifacts.get(path.name, {}).get('bytes', MAX_BYTES + 1) <= MAX_BYTES
                                   for path in artifact_paths))
            if not terminal_ok:
                report.update(result='DIAGNOSTIC_INCOMPLETE', reason='Final identity/artifact/lifecycle closure')
        report['elapsed_seconds'] = time.monotonic() - started
        save()
    print(json.dumps({name: report[name] for name in
                      ('result', 'full_radio_startup_qualified', 'physical_qualification')}))
    return 0 if report['result'] == 'OBSERVATION_COMPLETED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
