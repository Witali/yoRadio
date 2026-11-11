"""Boot the diagnostic CYD application and sample its real WebUI over QEMU OpenETH."""
import argparse
from contextlib import ExitStack
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FATAL = re.compile(r'Guru Meditation|assert failed:|abort\(\) was called|watchdog got triggered|'
                   r'SPIFFS mount failed|Audio service failed|Radio control failed|Web server failed|'
                   r'opencores\.emac: no mem for receive buffer', re.I)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def flash_parts(build):
    spec = json.loads((build / 'flasher_args.json').read_bytes())
    if spec['extra_esptool_args']['chip'] != 'esp32' or spec['flash_settings']['flash_size'] != '4MB':
        raise ValueError('Expected a classic ESP32 4 MiB image')
    flash = bytearray(b'\xff' * (4 * 1024 * 1024))
    parts = []
    end = 0
    for address, name in sorted((int(offset, 0), name) for offset, name in spec['flash_files'].items()):
        source = (build / name).resolve(strict=True)
        if not source.is_relative_to(build):
            raise ValueError('Flash component is outside the diagnostic build')
        body = source.read_bytes()
        if not end <= address < address + len(body) <= len(flash):
            raise ValueError('Overlapping or invalid flash component extent')
        end = address + len(body)
        flash[address:end] = body
        parts.append(dict(file=source.relative_to(build).as_posix(), offset=address,
                          bytes=len(body), sha256=digest(body)))
    if {p['offset'] for p in parts} != {0x1000, 0x8000, 0xe000, 0x10000, 0x370000}:
        raise ValueError('Unexpected bootloader, application or SPIFFS layout')
    return flash, parts


def request(port, uri, method='GET'):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=8)
    try:
        connection.request(method, uri)
        response = connection.getresponse()
        data = response.read(64 * 1024 + 1)
        if response.status != 200 or len(data) > 64 * 1024:
            raise RuntimeError(f'{uri}: HTTP {response.status}, {len(data)} bytes')
        return data
    finally:
        connection.close()


def sample(port):
    report = json.loads(request(port, '/api/native/health'))
    if report['schema'] != 1 or report['cores'] != 2:
        raise RuntimeError('Unexpected production health endpoint schema or core count')
    for group, key in (('decoder_failure', 'sequence'), ('stream_failure', 'sequence'), ('output', 'failures')):
        if report[group][key] != 0:
            raise RuntimeError(f'Unexpected {group} counter')
    if report['allocation_failures'] != 0:
        raise RuntimeError('Unexpected allocation failure')
    if not 0 < report['minimum_heap'] <= report['heap'] or not 0 < report['largest'] <= report['heap']:
        raise RuntimeError('Invalid production heap sample')
    return {key: report[key] for key in ('uptime_ms', 'heap', 'largest', 'minimum_heap', 'tasks', 'memory', 'cpu', 'output_driver')}


def tls_station(material):
    sys.path.insert(0, str(ROOT / 'tools'))
    from audio_test_server.server import Server

    folder = ROOT / 'tests/fixtures/esp32c3_calibration'
    fixture, = [row for row in json.loads((folder / 'manifest.json').read_bytes())['fixtures'] if row['file'] == 'opus-510.ogg']
    data = (folder / fixture['file']).read_bytes()
    if digest(data) != fixture['sha256']:
        raise ValueError('Calibration Opus file differs from its fixture manifest')
    return Server('127.0.0.1', 0, {'station': dict(data=data, seconds=11, codec='opus', mime='audio/ogg')},
                  material / 'server.pem', material / 'server-key.pem', pacing_ratio=0.5)


def check_asset(port):
    expected = (ROOT / 'yoRadio/data/www/script.js.gz').read_bytes()
    data = request(port, '/script.js')
    if data != expected:
        raise RuntimeError('WebUI did not serve the exact packaged SPIFFS asset')
    return dict(bytes=len(data), sha256=digest(data))


def guest_log(log_path):
    if log_path.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError('QEMU UART log exceeded its bound')
    return log_path.read_text(encoding='utf-8', errors='replace')


def observe_playback(port, server, guest, log_path, report):
    radio = json.loads(request(port, '/api/native/radio'))
    if radio['count'] != 1 or radio['station'] != 'OpenETH fixture':
        raise RuntimeError('The expected SPIFFS station was not loaded')
    request(port, '/api/native/radio?action=play&station=1', 'POST')
    until = time.monotonic() + 40
    while time.monotonic() < until:
        uart = guest_log(log_path)
        if FATAL.search(uart) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure during playback')
        status = json.loads(request(port, '/api/native/status'))
        if status['audio'] and status['codec'].lower() == 'opus':
            first = sample(port)
            if first['output_driver']['written_bytes'] > 0:
                break
        time.sleep(0.2)
    else:
        raise RuntimeError('No active Opus playback with output writes before the deadline')
    report['playing_health'] = [first]
    report['web_asset_during_playback'] = check_asset(port)
    end = time.monotonic() + 5
    while time.monotonic() < end:
        if FATAL.search(guest_log(log_path)) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure during WebUI sampling')
        second = sample(port)
        status_after = json.loads(request(port, '/api/native/status'))
        if not status_after['audio'] or status_after['generation'] != status['generation']:
            raise RuntimeError('Playback stopped or changed generation during WebUI sampling')
        if second['output_driver']['written_bytes'] > first['output_driver']['written_bytes']:
            break
        time.sleep(0.2)
    else:
        raise RuntimeError('Audio output did not progress during the WebUI observation')
    events = [event for event in server.events if event.get('tls_version') and event['sent'] > 0]
    if len(events) != 1:
        raise RuntimeError('Expected one actual TLS audio response')
    report['playing_health'].append(second)
    report['tls_peer'] = {key: events[0][key] for key in ('tls_version', 'tls_cipher', 'sent')}
    report['playback'] = {key: status[key] for key in ('codec', 'format', 'pcm_sample_rate_hz', 'pcm_channels')}
    request(port, '/api/native/radio?action=stop', 'POST')
    report['observed'] += ['Opus audio over verified TLS', 'audio progress across WebUI asset read']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--qemu', required=True, type=Path)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--tls-material', type=Path, help='Local disposable CA and server certificate/key directory')
    args = parser.parse_args()
    build, qemu, rom = (path.resolve(strict=True) for path in (args.build, args.qemu, args.rom))
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh output directory under the project .build')
    config = json.loads((build / 'config/sdkconfig.json').read_bytes())
    if not (config['IDF_TARGET'] == 'esp32' and config['ETH_USE_OPENETH'] and not config['FREERTOS_UNICORE']):
        raise ValueError('Expected a dual-core CYD OpenETH diagnostic build')
    material = args.tls_material.resolve(strict=True) if args.tls_material else None
    if material is not None and (not material.is_relative_to(ROOT / '.build') or
                                 not config.get('MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')):
        raise ValueError('TLS workload requires local test credentials and a diagnostic CA bundle')
    flash, parts = flash_parts(build)
    output.mkdir(parents=True)
    flash_path = output / 'qemu-flash.bin'
    flash_path.write_bytes(flash)
    flash_sha = digest(flash)
    web_port = local_port()
    command = [str(qemu), '-global', 'driver=ssi.esp32.spi,property=input-delay-ns,value=25',
               '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet', '-smp', '2',
               '-L', str(rom), '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
               '-no-reboot', '-snapshot', '-nic', f'user,model=open_eth,restrict=on,hostfwd=tcp:127.0.0.1:{web_port}-:80',
               '-drive', f'file={str(flash_path).replace(",", ",,")},if=mtd,format=raw']
    log_path = output / 'qemu.log'
    report_path = output / 'report.json'
    report = dict(state='STARTING', scope='OpenETH full-application idle boot', passed=False,
                  flash_parts=parts, flash_sha256=flash_sha, qemu_sha256=digest(qemu.read_bytes()),
                  config_sha256=digest((build / 'config/sdkconfig.json').read_bytes()),
                  openeth=True, physical_tested=False, command=command,
                  runner_sha256=digest(Path(__file__).read_bytes()),
                  task_watchdog_seconds=config['ESP_TASK_WDT_TIMEOUT_S'],
                  native_diagnostics=config.get('YORADIO_NATIVE_DIAGNOSTICS', False))

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    guest = None
    server = None
    stack = ExitStack()
    try:
        server = stack.enter_context(tls_station(material)) if material else None
        if server:
            host_port = server.http.server_port
            net = command.index('-nic') + 1
            command[net] += f',guestfwd=tcp:10.0.2.100:18080-tcp:127.0.0.1:{host_port}'
            report['scope'] = 'OpenETH full-application boot and TLS audio with concurrent WebUI'
        with log_path.open('xb') as log:
            guest = subprocess.Popen(command, cwd=output, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report.update(state='RUNNING', qemu_pid=guest.pid)
            save()
            deadline = time.monotonic() + 100
            while time.monotonic() < deadline:
                uart = guest_log(log_path)
                if FATAL.search(uart) or guest.poll() is not None:
                    raise RuntimeError('Guest stopped or logged a startup failure')
                if 'CYD_OPENETH_READY' in uart and 'Native HTTP server started' in uart:
                    try:
                        first = sample(web_port)
                    except (OSError, http.client.HTTPException):
                        time.sleep(0.2)
                        continue
                    break
                time.sleep(0.2)
            else:
                raise RuntimeError('OpenETH/WebUI startup deadline exceeded')
            if 'ST7789: SPI2 DMA' not in uart or 'Pipeline ready:' not in uart:
                raise RuntimeError('Expected the production TFT and audio tasks')
            report['health'] = [first]
            save()
            asset = check_asset(web_port)
            second = sample(web_port)
            if second['uptime_ms'] < first['uptime_ms']:
                raise RuntimeError('Guest reset between the resource samples')
            report.update(health=[first, second], web_asset=asset,
                          observed=['ST7789', 'OpenETH IPv4', 'audio tasks', 'HTTP health', 'SPIFFS WebUI asset'])
            save()
            if server:
                observe_playback(web_port, server, guest, log_path, report)
            report['passed'] = True
    except (OSError, RuntimeError, ValueError, KeyError, http.client.HTTPException) as error:
        report['reason'] = str(error)
    finally:
        if guest is not None:
            if guest.poll() is None:
                report['controller_stop'] = True
                guest.terminate()
                guest.wait(timeout=10)
            report['qemu_exit_status'] = guest.returncode
        stack.close()
        if server:
            report['peer_observations'] = [{key: event.get(key) for key in ('tls_version', 'tls_cipher', 'sent', 'complete')}
                                           for event in server.events[:16]]
        report['flash_unchanged'] = digest(flash_path.read_bytes()) == flash_sha
        if log_path.is_file():
            uart = log_path.read_bytes()
            report['uart_sha256'] = digest(uart)
            report['guest_fault_observed'] = bool(FATAL.search(uart.decode('utf-8', errors='replace')))
        report['passed'] = bool(report['passed'] and report['flash_unchanged'] and not report.get('guest_fault_observed'))
        report['state'] = 'TERMINAL_PASS' if report['passed'] else 'TERMINAL_NONPASS'
        save()
    print(report['state'], report.get('reason', report.get('observed')))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
