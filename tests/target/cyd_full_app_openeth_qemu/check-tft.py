"""Compare the emulated CYD network-status framebuffer in two diagnostic builds."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('openeth_runner', ROOT / 'tests/run-cyd-full-app-openeth.py')
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def qmp_request(stream, command, **arguments):
    stream.write(json.dumps(dict(execute=command, arguments=arguments)).encode() + b'\r\n')
    while reply := stream.readline():
        message = json.loads(reply)
        if 'return' in message:
            return message['return']
        if 'error' in message:
            raise RuntimeError(f'QMP {command} failed: {message["error"]["desc"]}')
    raise RuntimeError(f'QMP disconnected during {command}')


def read_frame(path):
    with path.open('rb') as frame:
        if frame.readline().strip() != b'P6':
            raise RuntimeError('Expected QEMU PPM output')
        width, height = map(int, frame.readline().split())
        if frame.readline().strip() != b'255':
            raise RuntimeError('Unexpected PPM depth')
        rgb = frame.read()
    if sorted((width, height)) != [240, 320] or len(rgb) != width * height * 3:
        raise RuntimeError('Unexpected ST7789 framebuffer geometry')
    return width, height, rgb


def capture(build, qemu, rom, output):
    output.mkdir()
    flash, parts = RUNNER.flash_parts(build)
    image = output / 'qemu-flash.bin'
    image.write_bytes(flash)
    log = output / 'qemu.log'
    port = RUNNER.local_port()
    arguments = [
        qemu, '-global', 'driver=ssi.esp32.spi,property=input-delay-ns,value=25',
        '-global', 'driver=st7789,property=controls,value=off',
        '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet', '-smp', '2',
        '-L', rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
        '-qmp', f'tcp:127.0.0.1:{port},server=on,wait=off', '-no-reboot', '-snapshot',
        '-nic', 'user,model=open_eth,restrict=on',
        '-drive', f'file={str(image).replace(",", ",,")},if=mtd,format=raw',
    ]
    with log.open('xb') as uart, subprocess.Popen(arguments, stdout=uart, stderr=subprocess.STDOUT,
                                                  stdin=subprocess.DEVNULL, cwd=output) as guest:
        try:
            for _ in range(400):
                startup = RUNNER.guest_log(log)
                if guest.poll() is not None or RUNNER.FATAL.search(startup):
                    raise RuntimeError('CYD stopped or logged a startup failure')
                if 'Native HTTP server started' in startup and 'CYD_OPENETH_READY' in startup:
                    break
                time.sleep(0.25)
            else:
                raise RuntimeError('CYD startup deadline expired')
            screen = output / 'screen.ppm'
            with socket.create_connection(('127.0.0.1', port), timeout=8) as connection:
                with connection.makefile('rwb', buffering=0) as stream:
                    if 'QMP' not in json.loads(stream.readline()):
                        raise RuntimeError('Expected QMP greeting')
                    qmp_request(stream, 'qmp_capabilities')
                    for _ in range(60):
                        qmp_request(stream, 'screendump', filename=str(screen))
                        width, height, rgb = read_frame(screen)
                        colors = Counter(rgb[i:i + 3] for i in range(0, len(rgb), 3))
                        if len(colors) == 2 and colors[b'\0\0\0'] == 51200:
                            break
                        time.sleep(0.25)
                    else:
                        raise RuntimeError('Did not observe the complete network-client status frame')
        finally:
            if guest.poll() is None:
                guest.terminate()
                guest.wait(timeout=10)
    uart = log.read_bytes()
    if RUNNER.FATAL.search(uart.decode(errors='replace')) or image.read_bytes() != flash:
        raise RuntimeError('Unexpected guest fault or flash modification')
    return dict(width=width, height=height, framebuffer_sha256=RUNNER.digest(rgb),
                colors={color.hex(): pixels for color, pixels in sorted(colors.items())},
                app_sha256=next(part['sha256'] for part in parts if part['offset'] == 0x10000),
                uart_sha256=RUNNER.digest(uart))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'build', 'qemu', 'rom', 'output'):
        parser.add_argument(f'--{name}', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        parser.error('use a fresh directory under .build')
    output.mkdir(parents=True)
    results = {name: capture(build.resolve(strict=True), args.qemu.resolve(strict=True),
                             args.rom.resolve(strict=True), output / name)
               for name, build in (('baseline', args.baseline), ('candidate', args.build))}
    passed = all(results['baseline'][key] == results['candidate'][key]
                 for key in ('width', 'height', 'framebuffer_sha256'))
    report = dict(passed=passed, **results)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
