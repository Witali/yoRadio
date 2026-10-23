"""Owned QEMU pipe lifecycle; no sockets, serial devices or external processes.

Source-only proposal. This module creates real receipts only when root explicitly
runs the controller. COMPLETE is a request to stop our emulator, never a result.
"""
import hashlib
import json
from pathlib import Path
import queue
import re
import subprocess
import threading
import time


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(*, argv, cwd, env, report, save, taskkill, timeout=180):
    """Require greeting/capabilities/COMPLETE/quit ack/SHUTDOWN/owned exit0.

    QMP stdout is consumed by one bounded reader thread. Only this newly created
    process's stdin pipe receives qmp_capabilities and quit. Serial output goes
    to the controller's fresh campaign file supplied in the immutable argv.
    Every exceptional path remains NONPASS, even after a clean diagnostic quit.
    """
    out = Path(cwd)
    serial = out / 'qemu.serial.log'
    row = dict(name='qemu', argv=list(map(str, argv)), cwd=str(out), state='starting',
               exit_status=None, timed_out=False, interrupted=False, force_stopped=False,
               qmp_messages=[], qmp_requests=[], complete_observed=False,
               qmp_capabilities_acknowledged=False, qmp_quit_acknowledged=False,
               owned_shutdown_observed=False, stdout_eof_observed=False, reader_joined=False, lifecycle_qualified=False)
    report['commands'].append(row)
    save()
    proc = None
    reader = None
    received = queue.Queue(maxsize=1024)
    first_error = None
    eof = False
    greeting = None
    flags = dict(caps=False, quit=False, shutdown=False)
    request_ids = set()

    def problem(exc):
        nonlocal first_error
        if first_error is None:
            first_error = exc
            row['error'] = repr(exc)
        if isinstance(exc, KeyboardInterrupt):
            row['interrupted'] = True
        if isinstance(exc, (TimeoutError, subprocess.TimeoutExpired)):
            row['timed_out'] = True
        save()

    def pump():
        # Raw stdout is retained before parsing. There is no CLI fallback or
        # interpretation of emulator stdout as a shell/control instruction.
        try:
            with (out / 'qemu.qmp.stdout.log').open('xb') as raw:
                while True:
                    line = proc.stdout.readline(1024 * 1024 + 1)
                    if not line:
                        break
                    raw.write(line)
                    raw.flush()
                    if len(line) > 1024 * 1024:
                        received.put(('error', 'QMP line exceeds the declared bound'), timeout=2)
                        return
                    received.put(('line', line), timeout=2)
        except BaseException as exc:
            try:
                received.put(('error', repr(exc)), timeout=2)
            except queue.Full:
                pass
        finally:
            try:
                received.put(('eof', None), timeout=2)
            except queue.Full:
                pass

    def send(command, ident):
        need(proc is not None and proc.poll() is None and ident not in request_ids,
             'QMP request requires our live process and unique ID')
        need(command in ('qmp_capabilities', 'quit'), 'Only the reviewed QMP commands are allowed')
        item = dict(execute=command, id=ident)
        raw = (json.dumps(item, separators=(',', ':')) + '\r\n').encode('ascii')
        proc.stdin.write(raw)
        proc.stdin.flush()
        request_ids.add(ident)
        row['qmp_requests'].append(dict(message=item, actual_sent_time_ns=time.time_ns()))
        with (out / 'qemu.qmp.requests.jsonl').open('ab') as stream:
            stream.write((json.dumps(row['qmp_requests'][-1]) + '\n').encode())
        save()

    def consume(wait=0.05):
        nonlocal eof, greeting
        try:
            kind, value = received.get(timeout=wait)
        except queue.Empty:
            return
        if kind == 'eof':
            eof = True
            row['stdout_eof_observed'] = True
            save()
            return
        need(kind == 'line', 'QMP reader failure: ' + str(value))
        message = json.loads(value.decode('utf-8'))
        need(isinstance(message, dict), 'QMP message must be an object')
        row['qmp_messages'].append(dict(message=message, actual_received_time_ns=time.time_ns()))
        save()
        if 'QMP' in message:
            need(greeting is None and len(row['qmp_messages']) == 1,
                 'Exactly one initial QMP greeting required')
            need(isinstance(message['QMP'], dict) and isinstance(message['QMP'].get('version'), dict)
                 and isinstance(message['QMP'].get('capabilities'), list), 'Malformed actual QMP greeting')
            greeting = message
        elif 'return' in message:
            need(message.get('return') == {} and message.get('id') in request_ids,
                 'Unexpected QMP response')
            ident = message['id']
            key = 'caps' if ident == 'owned-capabilities' else 'quit'
            need(not flags[key], 'Duplicate QMP acknowledgement')
            flags[key] = True
            row['qmp_capabilities_acknowledged'] = flags['caps']
            row['qmp_quit_acknowledged'] = flags['quit']
        elif 'event' in message:
            need(message['event'] not in ('RESET', 'GUEST_PANICKED'), 'Target reset/panic QMP event')
            if message['event'] == 'SHUTDOWN':
                need('owned-quit' in request_ids and not flags['shutdown'], 'Unexpected/duplicate shutdown')
                need(message.get('data') == {'guest': False, 'reason': 'host-qmp-quit'},
                     'Require actual host-qmp-quit shutdown of our emulator')
                flags['shutdown'] = True
                row['owned_shutdown_observed'] = True
        else:
            raise RuntimeError('Unexpected or error QMP message: ' + repr(message))
        save()

    try:
        with (out / 'qemu.stderr.log').open('xb') as stderr:
            try:
                proc = subprocess.Popen(row['argv'], cwd=out, env=env,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW, bufsize=0)
                row.update(pid=proc.pid, state='running', actual_started_time_ns=time.time_ns())
                save()
                reader = threading.Thread(target=pump, name='owned-qmp-reader', daemon=True)
                reader.start()
                handshake = time.monotonic() + 15
                while greeting is None:
                    need(proc.poll() is None, 'QEMU exited before its QMP greeting')
                    if time.monotonic() >= handshake:
                        raise TimeoutError('QMP greeting deadline')
                    consume()
                send('qmp_capabilities', 'owned-capabilities')
                while not flags['caps']:
                    need(proc.poll() is None, 'QEMU exited before capabilities acknowledgement')
                    if time.monotonic() >= handshake:
                        raise TimeoutError('QMP capabilities deadline')
                    consume()
                deadline = time.monotonic() + timeout
                while not row['complete_observed']:
                    consume()
                    need(not serial.is_file() or serial.stat().st_size <= 2 * 1024 * 1024,
                         'Owned unit serial log exceeded its declared2MiB bound')
                    raw = serial.read_bytes() if serial.is_file() else b''
                    text = raw.decode('utf-8', errors='replace').replace('\r\n', '\n')
                    need(not re.search(r'PUBLIC_BOOK_CONSUMER_FAILURE|Guru Meditation|CORRUPT\s*HEAP|assert failed|abort\(\)|Brownout|Rebooting', text, re.I),
                         'Actual unit failure/panic/reset before terminal closure')
                    marker = re.search(r'^PUBLIC_BOOK_CONSUMER_COMPLETE cases=36 calls=365 unequal=([0-9]+) live=0 core=0$', text, re.M)
                    if marker is not None and int(marker[1]) <= 365:
                        row.update(complete_observed=True, serial_bytes_at_complete=len(raw),
                                   serial_sha256_at_complete=hashlib.sha256(raw).hexdigest())
                        save()
                        break
                    need(proc.poll() is None and not eof, 'QEMU exited before actual COMPLETE')
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Actual unit COMPLETE deadline')
            except BaseException as exc:
                problem(exc)
            finally:
                if proc is not None and proc.poll() is None:
                    # A failed unit may still be stopped cleanly for diagnostics;
                    # first_error and the false lifecycle result are preserved.
                    try:
                        need(flags['caps'], 'Cannot issue quit before acknowledged capabilities')
                        send('quit', 'owned-quit')
                        deadline = time.monotonic() + 15
                        while proc.poll() is None or not eof:
                            consume()
                            if time.monotonic() >= deadline:
                                raise TimeoutError('Owned QMP quit/terminal deadline')
                        proc.wait(timeout=1)
                    except BaseException as exc:
                        problem(exc)
                if proc is not None and proc.poll() is None:
                    row['force_stopped'] = True
                    save()
                    try:
                        cleanup = subprocess.run([str(taskkill), '/PID', str(proc.pid), '/T', '/F'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15,
                            creationflags=subprocess.CREATE_NO_WINDOW)
                        (out / 'qemu.cleanup.log').write_bytes(cleanup.stdout)
                        row['tree_cleanup_exit_status'] = cleanup.returncode
                    except BaseException as exc:
                        row['cleanup_error'] = repr(exc)
                    if proc.poll() is None:
                        proc.kill()  # Only the Popen-created direct child.
                    proc.wait(timeout=15)
                if proc is not None:
                    row['exit_status'] = proc.poll()
                    row['actual_terminal_time_ns'] = time.time_ns()
                    proc.stdin.close()
                if reader is not None:
                    reader.join(timeout=3)
                    row['reader_joined'] = not reader.is_alive()
                    save()
                    if reader.is_alive():
                        problem(RuntimeError('Owned QMP reader did not reach EOF'))
                    while not received.empty():
                        try:
                            consume(wait=0)
                        except BaseException as exc:
                            problem(exc)
                if proc is not None:
                    proc.stdout.close()
    finally:
        row['state'] = 'interrupted' if row['interrupted'] else ('failed' if first_error else 'complete')
        for path in (serial, out / 'qemu.stderr.log', out / 'qemu.qmp.stdout.log', out / 'qemu.qmp.requests.jsonl'):
            if path.is_file():
                row[path.name] = dict(bytes=path.stat().st_size, sha256=sha(path))
        save()
    if first_error is not None:
        raise first_error
    need(row['exit_status'] == 0 and row['complete_observed'] and not row['force_stopped']
         and not row['timed_out'] and not row['interrupted'] and eof and greeting is not None
         and row['stdout_eof_observed'] and row['reader_joined']
         and flags == dict(caps=True, quit=True, shutdown=True),
         'Require actual greeting, both acknowledgements, host shutdown and owned terminal0')
    row['lifecycle_qualified'] = True
    save()
    return serial.read_text(encoding='utf-8', errors='replace'), row
