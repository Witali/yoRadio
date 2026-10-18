"""Verify AP setup settings/LCD stability and station-only service allocation.

Factory and native images execute unchanged in owned disposable VMs. Only
synthetic flash settings and loopback HTTP are supplied. Hardware breakpoints
and read-only RSP inspect native tasks/cache at an SDK delay entry; no guest
instructions, registers, clock values or RAM are patched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    """Bind immutable inputs and complete RGB frames to their actual bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exercise(options, folder, variant, layout, app_state, weather_layout, weather_objects):
    """Exercise one real AP while preserving its code, screen, cache and role."""
    options = SimpleNamespace(**vars(options), firmware=variant)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        options.gdb_port = reservation.getsockname()[1] if variant == 'reconstructed' else 0
    prepared = vm.prepare(options, folder)
    data = (folder / 'flash.bin').read_bytes()
    protected = [(a, b, hashlib.sha256(data[a:b]).hexdigest())
                 for a, b in ((0, 0x9000), (0x10000, 0x3e7000))]
    row = {'passed': False, 'sources': prepared['sources'], 'http': [], 'snapshots': {}}
    session = observer = None
    counters = RomHeapCounters(Path(options.rom_elf)) if variant == 'reconstructed' else None
    try:
        session, _ = vm.launch(options, folder)
        row['session'] = {key: session[key] for key in ('name', 'pid', 'web_urls')}
        if variant == 'reconstructed':
            observer = Observer(options.gdb_port)
            observer.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            observer.socket.settimeout(20)
            reader = MemorySnapshot(observer.memory, layout, counters.validate)
            cache = WeatherSnapshot(reader.memory, weather_layout, weather_objects, layout['elf_sha256'])
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            require(direct_flash_backing(qmp, folder), 'AP test flash is not direct writable raw')

            def seconds():
                """Read the short run's low radio counter without changing time."""
                return int.from_bytes(read_bytes(qmp, 0x6004d000, 4), 'little') / 1e6

            def until(target):
                """Wait past startup and asynchronous cleanup with a separate host bound."""
                deadline = time.monotonic() + 240
                while seconds() < target:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('AP guest time did not reach ' + str(target))
                    time.sleep(.2)

            def capture(label):
                """Observe complete AP frames and native typed state at a safe SDK entry."""
                if observer:
                    observer.interrupt()
                    address = layout['symbols']['vTaskDelay']['address']
                    if observer.register(32) != address:
                        observer.breakpoint(address)
                        observer.continue_to(address)
                        observer.breakpoint(address, False)
                else:
                    qmp.execute('stop')
                try:
                    image = folder / (label + '.png')
                    vm.capture_png(qmp, image)
                    pixels = vm.ppm_pixels(image.with_suffix('.ppm'))
                    require(any(pixels), 'AP screen is blank')
                    state = {'guest_seconds': seconds(), 'frame_sha256': hashlib.sha256(pixels).hexdigest()}
                    if observer:
                        state.update(tasks=reader.tasks(), heap=reader.heaps(), weather=cache.sample(seconds()),
                                     role=vm.application_state(qmp, app_state))
                        names = {task['name'] for task in state['tasks']}
                        require(not names & {'time_sync', 'weather_http', 'wifi_fallback'},
                                'AP allocated station-only workers: ' + str(sorted(names)))
                        require(state['weather'] == {'worker_state': 0, 'valid': False, 'generation': 0},
                                'AP weather request/cache changed despite no station worker')
                        require(state['role']['ap_active'] is True and state['role']['connected'] is False and
                                state['role']['time_synced'] is False, 'Native AP role/time changed')
                    else:
                        require(read_bytes(qmp, 0x3fcc3a74, 1) == b'\x05' and
                                read_bytes(qmp, 0x3fcc3ab8, 1) == b'\0', 'Factory AP init/time state differs')
                    row['snapshots'][label] = state
                finally:
                    if observer:
                        observer.resume()
                    else:
                        qmp.execute('cont')

            if observer:
                observer.resume()
            else:
                qmp.execute('cont')
            url = session['web_urls']['setup']
            wait_http(url, expected=b'/configure')
            until(30)
            capture('ready')
            requests = [('/updateCity', {'city': 'Fixture,GB'}),
                        ('/advancedset', {'ntp': 'time-test.invalid', 'openweathermapKey': 'fixture-key', 'clickCount': 0}),
                        # Stock UI serializes the select.value string. Its
                        # literal handler reads clocktype+12, after the quote.
                        ('/settings', {'timeSync': 1}), ('/setclocktype', {'clocktype': '3'})]
            for path, payload in requests:
                status, _ = http(url, path, payload, timeout=20)
                row['http'].append({'method': 'POST', 'path': path, 'status': status})
                require(status == 200, 'AP setting was rejected: ' + path)
            status, body = http(url, '/getsettings', timeout=20)
            row['http'].append({'method': 'GET', 'path': '/getsettings', 'status': status})
            require(status == 200 and json.loads(body)['timeSync'] == 1, 'AP browser-time setting was not retained')
            status, body = http(url, '/getclocktype', timeout=20)
            row['http'].append({'method': 'GET', 'path': '/getclocktype', 'status': status})
            require(status == 200 and body.strip() == b'3', 'AP theme setting was not retained')
            wait_http(url, expected=b'/configure')
            until(max(45, seconds() + 3))
            capture('after-settings')
            require(row['snapshots']['ready']['frame_sha256'] == row['snapshots']['after-settings']['frame_sha256'],
                    'AP settings changed the setup instruction frame')
            row['passed'] = True
    except Exception as error:
        row['error'] = str(error)
        raise
    finally:
        if observer:
            observer.close()
        if session:
            vm.control(folder, 'stop')
            vm.ensure_stopped(folder)
        after = (folder / 'flash.bin').read_bytes()
        row['executable_media_unchanged'] = all(hashlib.sha256(after[a:b]).hexdigest() == expected
                                               for a, b, expected in protected)
        row['uart'] = inspect_uart((folder / 'uart.log').read_bytes()) if session else {'passed': False}
        row['rom_counter_checks'] = counters.checks if counters else None
        row['passed'] &= row['executable_media_unchanged'] and row['uart']['passed'] and row['uart']['rom_boots'] == 1
        vm.save_json(folder / 'report.json', row)
    return row


def main():
    """Compare AP behavior and require the tested app/ELF/helper identities to stay fixed."""
    global vm, read_bytes, direct_flash_backing, Observer, MemorySnapshot, WeatherSnapshot, RomHeapCounters
    global http, wait_http, require, inspect_uart
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, default=ROOT)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.qemu_root / 'tools'), str(args.dependency_root / '.build/small-tv-parity/oracle-deps')]
    import small_tv_vm as vm
    import weather_qemu as weather
    from weather_qemu import read_bytes
    from qemu_storage import direct_flash_backing
    from gdb_observer import Observer
    from runtime_memory import MemorySnapshot, native_layout
    from runtime_weather import WeatherSnapshot
    from runtime_heap_rom import RomHeapCounters
    from netif_observer import require, FACTORY_SHA
    from small_tv_http_test import http, wait_http
    from esp_elf import object_symbols
    sys.path.insert(0, str(ROOT / 'Small_TV/src/tools'))
    from runtime_run_guard import inspect_uart
    root = args.yoradio.resolve()
    weather.ROOT, weather.vm = root, vm
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require(digest(root / 'Small_TV/full-flash.bin') == FACTORY_SHA, 'Unknown factory image')
    require((archive / 'app.bin').read_bytes()[176:208] == bytes.fromhex(digest(elf)), 'Native app/ELF mismatch')
    layout = native_layout(elf)
    weather_layout = weather.native_layout()
    objects = object_symbols(elf.read_bytes(), ('cached_weather', 'request_state'))
    options = SimpleNamespace(yoradio=str(root), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(root / 'Small_TV/qemu/profiles/small-tv-c2.json'),
        network='setup', display='none', persistent=True, paused=True)
    app_state = vm.application_state_layout(options)
    paths = [Path(__file__), elf, root / 'Small_TV/full-flash.bin', root / 'Small_TV/manifest.json',
             Path(options.qemu), Path(options.rom_elf), Path(options.hardware_profile)]
    paths += [Path(__file__).with_name(name) for name in ('weather_qemu.py', 'qemu_storage.py', 'gdb_observer.py',
              'runtime_memory.py', 'runtime_weather.py', 'runtime_heap_rom.py', 'netif_observer.py')]
    paths.append(ROOT / 'Small_TV/src/tools/runtime_run_guard.py')
    paths += [args.qemu_root / 'tools' / name for name in ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py',
                                                         'small_tv_web.py', 'esp_elf.py', 'esp_board.py', 'esp_services.py')]
    paths += [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin',
                                         'manifest.json', 'source-manifest.json', 'assets-manifest.json')]
    pins = {str(path): digest(path) for path in paths}
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'passed': False, 'all_functionality_verified': False, 'scope': __doc__, 'inputs_sha256': pins,
              'app_sha256': digest(archive / 'app.bin'), 'native_elf_sha256': digest(elf),
              'qemu_sha256': digest(Path(options.qemu)), 'flows': {}}
    active = None
    try:
        for variant in ('original', 'reconstructed'):
            active = args.output / variant
            report['flows'][variant] = exercise(options, active, variant, layout, app_state, weather_layout, objects)
            require(report['flows'][variant]['passed'], 'AP services flow failed: ' + variant)
            print('PASS real AP settings/LCD/services:', variant, flush=True)
        before = report['flows']['original']['snapshots']['ready']['frame_sha256']
        after = report['flows']['reconstructed']['snapshots']['ready']['frame_sha256']
        require(before == after, 'Factory and native AP instruction frames differ')
        report['factory_native_frame_identical'] = True
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        if active and (active / 'report.json').exists():
            report['flows'][active.name] = json.loads((active / 'report.json').read_text(encoding='utf-8-sig'))
        raise
    finally:
        report['inputs_unchanged'] = all(digest(Path(path)) == expected for path, expected in pins.items())
        report['passed'] &= report['inputs_unchanged']
        vm.save_json(args.output / 'report.json', report)
    require(report['passed'], 'AP services regression failed')


if __name__ == '__main__':
    main()
