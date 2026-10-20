"""Compare actual STA/AP netif roles, retained driver NVS and setup scans.

Both firmware images first boot as real stations. The factory driver creates
synthetic SDK credentials, which are copied into each stopped setup fixture's
NVS partition; only the raw mode word is changed after that seed is prepared.
The native driver uses RAM storage and need not write redundant SDK credentials.
Guest instructions, RAM and registers are never patched; list reads use QMP
stop/read/continue, and network access goes through the real localhost HTTP.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

import netif_observer as observer

ROOT = Path(__file__).resolve().parents[3]
RAW_MODE = 0x3e7000 + 0x160
NVS = slice(0x9000, 0xf000)


def sample_netifs(qmp, layout):
    """Take one coherent read-only list snapshot and always resume the owned guest."""
    qmp.execute('stop')
    try:
        return observer.read_netifs(lambda address, size: read_bytes(qmp, address, size), layout)
    finally:
        qmp.execute('cont')


def exercise(options, folder, variant, settings, application, layout, seed=None):
    """Boot one real role, verify its HTTP page/list, and retain its stopped flash."""
    station = seed is None
    options = SimpleNamespace(**vars(options), firmware=variant)
    prepared, before = fallback.prepare_station(options, folder)
    row = {'passed': False, 'sources': prepared['sources'], 'observations': []}
    if seed is not None:
        image = bytearray(seed)
        struct.pack_into('<I', image, RAW_MODE, 2)
        observer.require(all(a == b or RAW_MODE <= index < RAW_MODE + 4
                             for index, (a, b) in enumerate(zip(seed, image))),
                         'Setup seed changed bytes beyond the raw mode')
        observer.require(image[NVS] == seed[NVS], 'Setup seed changed driver NVS')
        (folder / 'flash.bin').write_bytes(image)
        row['seeded_mode_only'] = True
        row['retained_driver_nvs'] = observer.driver_credentials(image[NVS], nvs_parser)
    session = None
    try:
        session, _ = vm.launch(options, folder)
        row['session'] = {key: session[key] for key in ('name', 'pid', 'web_urls')}
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            observer.require(direct_flash_backing(qmp, folder), 'Flash is not directly writable raw')
            qmp.execute('cont')
            row['ready'] = fallback.wait_observation(qmp, folder, variant, settings, application,
                (lambda state: state['connected']) if station else (lambda state: state['ap_active']),
                row['observations'], 150)
            key, marker = ('station', b'/setclocktype') if station else ('setup', b'/configure')
            body = wait_http(session['web_urls'][key], expected=marker)
            row['expected_http_page'] = marker in body
            row['netifs'] = sample_netifs(qmp, layout)
            observer.require_role(row['netifs'], station)
            if not station:
                observer.require(not row['ready']['connected'] and
                    (variant != 'original' or row['ready']['factory_apsta_got_ip_event'] is False),
                    'Setup unexpectedly has a station IP')
                status, body = http(session['web_urls']['setup'], '/scan', timeout=30)
                scan = json.loads(body)
                observer.require(status == 200 and isinstance(scan, list) and
                                 any(item.get('ssid') == 'yoRadio-QEMU' for item in scan),
                                 'Setup scan did not see the virtual station AP')
                row['scan'] = {'status': status, 'expected_public_ssid_present': True}
                wait_http(session['web_urls']['setup'], expected=b'/configure')
                row['netifs_after_scan'] = sample_netifs(qmp, layout)
                observer.require_role(row['netifs_after_scan'], False)
                row['after_scan'] = fallback.observe(qmp, folder, variant, settings, application)
                observer.require(row['after_scan']['ap_active'] and not row['after_scan']['connected'],
                                 'Scan changed the selected setup role')
            row['passed'] = row['expected_http_page']
    except Exception as error:
        row['error'] = str(error)
        raise
    finally:
        row['executable_media_unchanged'] = fallback.stop_and_verify(folder, session, before)
        row['uart_clean'] = clean_uart(folder)
        row['passed'] &= row['executable_media_unchanged'] and row['uart_clean']
        vm.save_json(folder / 'report.json', row)
    observer.require(row['passed'], 'Netif role VM checks failed')
    return row, (folder / 'flash.bin').read_bytes()


def main():
    """Run independent factory/native role flows and bind every source to the result."""
    global vm, fallback, read_bytes, direct_flash_backing, http, wait_http, clean_uart, nvs_parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--yoradio', type=Path, default=ROOT,
                        help='Explicit firmware/ELF root, also permits an unchanged old-image control')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    sys.path.insert(0, str(args.dependency_root / '.build/small-tv-parity/oracle-deps'))
    sdk_parser = args.dependency_root / '.idf/v5.5.4/components/nvs_flash/nvs_partition_tool/nvs_parser.py'
    sys.path.insert(0, str(sdk_parser.parent))
    import small_tv_vm as vm
    import wifi_fallback_qemu as fallback
    import nvs_parser
    from weather_qemu import read_bytes
    from qemu_storage import direct_flash_backing
    from small_tv_http_test import http, wait_http, clean_uart
    fallback.vm, fallback.read_bytes = vm, read_bytes
    fallback.clean_uart, fallback.wait_http = clean_uart, wait_http
    root = args.yoradio.resolve()
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    elf_path = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    native = observer.native_layout(elf_path, archive / 'app.bin')
    layouts = {'original': observer.factory_layout(root / 'Small_TV/full-flash.bin'), 'reconstructed': native}
    options = SimpleNamespace(yoradio=str(root), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(root / 'Small_TV/qemu/profiles/small-tv-c2.json'), network='setup',
        display='none', persistent=True, paused=True, gdb_port=0)
    application = vm.application_state_layout(options)
    paths = [Path(__file__), Path(observer.__file__), Path(fallback.__file__),
             Path(__file__).with_name('weather_qemu.py'), Path(__file__).with_name('qemu_storage.py'),
             Path(__file__).with_name('machine_oracle.py'), sdk_parser, elf_path,
             Path(options.qemu), Path(options.rom_elf), Path(options.hardware_profile),
             root / 'Small_TV/full-flash.bin', root / 'Small_TV/manifest.json']
    paths += [args.qemu_root / 'tools' / name for name in
              ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py',
               'small_tv_display.py', 'esp_elf.py', 'esp_board.py', 'esp_services.py')]
    paths += [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin',
                                         'manifest.json', 'source-manifest.json', 'assets-manifest.json')]
    pins = {str(path.resolve()): observer.digest(path) for path in paths}
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'passed': False, 'all_functionality_verified': False, 'scope': __doc__,
              'tested_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'inputs_sha256': pins,
              'app_sha256': observer.digest(archive / 'app.bin'), 'native_elf_sha256': observer.digest(elf_path),
              'factory_full_flash_sha256': observer.FACTORY_SHA, 'qemu_sha256': observer.digest(options.qemu),
              'native_layout': native, 'flows': {}}
    active = None
    driver_nvs = None
    try:
        for variant in ('original', 'reconstructed'):
            active = args.output / (variant + '-station')
            row, image = exercise(options, active, variant, native['settings'], application, layouts[variant])
            report['flows'][variant + '-station'] = row
            if variant == 'original':
                driver_nvs = image[NVS]
                report['synthetic_driver_nvs'] = observer.driver_credentials(driver_nvs, nvs_parser)
            seed = bytearray(image)
            seed[NVS] = driver_nvs
            observer.require(all(a == b or NVS.start <= index < NVS.stop
                                 for index, (a, b) in enumerate(zip(image, seed))),
                             'Shared synthetic NVS fixture changed other station bytes')
            print('PASS real netif STA:', variant, flush=True)
            active = args.output / (variant + '-setup')
            row, _ = exercise(options, active, variant, native['settings'], application, layouts[variant], seed)
            row['seed_provenance'] = {'driver_nvs_source': 'original-station',
                                      'station_nvs_replaced': image[NVS] != driver_nvs,
                                      'only_nvs_replaced_before_mode_change': True}
            report['flows'][variant + '-setup'] = row
            print('PASS real retained-SSID setup/APSTA scan netif:', variant, flush=True)
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        if active and (active / 'report.json').exists():
            report['flows'][active.name] = json.loads((active / 'report.json').read_text(encoding='utf-8-sig'))
        raise
    finally:
        report['inputs_unchanged'] = all(observer.digest(path) == expected for path, expected in pins.items())
        report['passed'] &= report['inputs_unchanged']
        vm.save_json(args.output / 'report.json', report)
    observer.require(report['passed'], 'Netif role regression failed')


if __name__ == '__main__':
    main()
