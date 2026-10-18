"""Actual Chrome Wi-Fi setup, AP/STA transition and cold flash persistence."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
RAW = 0x3e7000


def digest(path):
    """Bind evidence to the exact bytes used by this standalone browser gate."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    """Stop on a missing observation, retaining the failed report and owned UART."""
    if not condition:
        raise AssertionError(message)


def main():
    """Exercise discovered/manual SSIDs using real scan responses and guest writes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--node', type=Path, required=True)
    parser.add_argument('--playwright-modules', type=Path, required=True)
    parser.add_argument('--browser-executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http, wait_for, clean_uart
    from qemu_storage import direct_flash_backing
    archive = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
    elf = ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require((archive / 'app.bin').read_bytes()[176:208] == bytes.fromhex(digest(elf)), 'ELF/app mismatch')
    rom = args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    profile = ROOT / 'Small_TV/qemu/profiles/small-tv-c2.json'
    options = SimpleNamespace(yoradio=str(ROOT), firmware='reconstructed',
        qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'), rom_elf=str(rom),
        network='setup', display='none', persistent=True, paused=True, gdb_port=0, http_base_port=0)
    layout = vm.application_state_layout(options)
    paths = [Path(__file__), Path(__file__).with_name('browser_wifi_flow.mjs'),
        Path(__file__).with_name('qemu_storage.py'), elf, rom, profile,
        args.node, args.browser_executable, Path(options.qemu)]
    paths += [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin',
        'assets.bin', 'manifest.json', 'source-manifest.json')]
    paths += [ROOT / 'Small_TV/local_site' / name for name in
        ('pages/setup.html', 'pages/settings.html', 'wifi_network.js')]
    paths += [args.qemu_root / 'tools' / name for name in ('small_tv_vm.py', 'small_tv_http_test.py',
        'small_tv_web.py', 'small_tv_network.py', 'esp_board.py', 'esp_elf.py', 'esp_services.py')]
    inputs = {str(path.resolve()): digest(path) for path in paths}
    report = dict(passed=False, all_functionality_verified=False, tested_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        app_sha256=digest(archive / 'app.bin'), native_elf_sha256=digest(elf), qemu_sha256=digest(Path(options.qemu)),
        inputs_sha256=inputs, application_layout=layout, flows={},
        scope='Real Chrome390x844, guest scan/configure, open synthetic AP, invalid password, manual/cancel/SSID collision, AP->STA, UDP SNTP and cold persistence. No WPA handshake, physical RF, desktop coverage or factory browser parity claim.')
    active = None

    def raw_settings(folder):
        """Read the documented complete 444-byte raw record independently of HTTP."""
        return (folder / 'flash.bin').read_bytes()[RAW:RAW+444]

    def state_observation(session):
        """Observe actual SDK flags and DHCP bytes using the matching ELF symbols."""
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            return vm.application_state(qmp, layout)

    def browser(stage, scenario, ssid, folder, session):
        """Run bounded UI work; only a successful hidden submit restores the AP."""
        command = [str(args.node), str(Path(__file__).with_name('browser_wifi_flow.mjs')),
            '--url', session['web_urls']['setup'] + '/', '--station', session['web_urls']['station'] + '/',
            '--ssid', ssid, '--scenario', scenario, '--stage', stage, '--output', str(folder),
            '--modules', str(args.playwright_modules), '--browser', str(args.browser_executable)]
        with (folder / ('node-' + stage + '.log')).open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 200
            restored = False
            try:
                while process.poll() is None:
                    if scenario == 'manual-entry' and stage == 'configure' and not restored and (folder / 'configuration-accepted.json').exists():
                        with vm.QMP(session['qmp_port'], session['name']) as qmp:
                            qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=True)
                        restored = True
                    require(time.monotonic() < deadline, 'Browser process exceeded its deadline')
                    time.sleep(.2)
            finally:
                if process.poll() is None:
                    process.terminate(); process.wait(timeout=10)
        result = json.loads((folder / ('browser-' + stage + '.json')).read_text())
        require(process.returncode == 0 and result['passed'], 'Browser ' + stage + ': ' + str(result.get('error')))
        if stage != 'cold':
            expected = hashlib.sha256((ROOT / 'Small_TV/local_site/pages/setup.html').read_text(encoding='utf-8').encode()).hexdigest()
            require(result['served_html_sha256'] == expected, 'Guest setup HTML differs from the generated page')
        else:
            expected = hashlib.sha256((ROOT / 'Small_TV/local_site/pages/settings.html').read_text(encoding='utf-8').encode()).hexdigest()
            require(result['station_html_sha256'] == expected, 'Guest settings HTML differs from the generated page')
        return result

    try:
        for scenario, ssid in [('discovered', 'yoRadio-QEMU'), ('literal-manual', 'manual'), ('manual-entry', 'yoRadio-QEMU')]:
            folder = args.output / scenario
            folder.mkdir()
            vm_folder = folder / 'vm'
            fixture = json.loads(profile.read_text())
            fixture['network']['station_ssid'] = ssid
            fixture_path = folder / 'profile.json'
            vm.save_json(fixture_path, fixture)
            options.hardware_profile = str(fixture_path)
            vm.prepare(options, vm_folder)
            before = (vm_folder / 'flash.bin').read_bytes()
            row = {'passed': False, 'checks': {}, 'stages': {}}
            report['flows'][scenario] = row
            for phase in ('setup', 'cold'):
                active = vm_folder
                session, _ = vm.launch(options, vm_folder)
                row['stages'][phase] = {key: session[key] for key in ('name', 'pid', 'web_urls')}
                with vm.QMP(session['qmp_port'], session['name']) as qmp:
                    require(direct_flash_backing(qmp, vm_folder), 'Not a writable raw flash backend')
                    qmp.execute('qom-set', path='/machine/wifi', property='ntp-unix-seconds', value=1792324800)
                    if phase == 'setup' and scenario == 'manual-entry':
                        qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=False)
                    qmp.execute('cont')
                if phase == 'setup':
                    wait_http(session['web_urls']['setup'], expected=b'/configure')
                    initial = raw_settings(vm_folder)
                    require(initial[4] == 0 and struct.unpack_from('<I', initial, 0x160)[0] == 2, 'Initial settings are not empty setup')
                    row['preflight'] = browser('preflight', scenario, ssid, folder, session)
                    require(raw_settings(vm_folder) == initial, 'Invalid/cancelled UI changed raw settings')
                    role = state_observation(session)
                    require(role['ap_active'] and not role['connected'], 'Invalid/cancelled UI changed the network role')
                    require((vm_folder / 'uart.log').read_bytes().count(b'ESP-ROM:esp32c2') == 1, 'Invalid UI rebooted the guest')
                    row['checks']['invalid_preserves_raw_role_and_boot'] = True
                    row['configure'] = browser('configure', scenario, ssid, folder, session)
                else:
                    require(session['name'] != row['stages']['setup']['name'], 'Cold boot reused the same VM')
                    wait_http(session['web_urls']['station'], expected=b'/setclocktype')
                    row['cold'] = browser('cold', scenario, ssid, folder, session)
                wait_for(lambda: state_observation(session)['time_synced'], 'STA did not synchronize its clock')
                role = state_observation(session)
                require(role['connected'] and not role['ap_active'] and role['station_address'] == '192.168.43.15', 'STA role or DHCP address differs')
                with vm.QMP(session['qmp_port'], session['name']) as qmp:
                    reply = json.loads(qmp.execute('qom-get', path='/machine/wifi', property='last-ntp-reply'))
                    clock = vm.ntp_reply_observation(qmp, vm_folder, True, False, layout)
                # Keep the legacy estimate visible, but compare real SDK UTC:
                # its HRT origin/correction change across the software reboot.
                row['stages'][phase].update(role=role, ntp_reply=reply, sdk_clock=clock,
                    legacy_clock_estimate=vm.read_guest_clock(vm_folder))
                require(clock is not None and reply['count'] >= 1 and reply['unix_seconds'] == 1792324800 and
                        abs(clock['difference_seconds']) < 1, 'SDK clock does not match synthetic UDP SNTP')
                vm.control(vm_folder, 'stop'); vm.ensure_stopped(vm_folder); active = None
                require(clean_uart(vm_folder), 'Guest panic during ' + phase)
                uart = (vm_folder / 'uart.log').read_bytes()
                boots = 2 if phase == 'setup' else 1
                require(uart.count(b'ESP-ROM:esp32c2') == boots, 'Unexpected ROM boot count during ' + phase)
                (folder / ('uart-' + phase + '.log.gz')).write_bytes(gzip.compress(uart, mtime=0))
                row['stages'][phase]['rom_boots'] = boots
                raw = raw_settings(vm_folder)
                require(raw[4:69].split(b'\0')[0] == ssid.encode() and raw[69] == 0 and struct.unpack_from('<I', raw, 0x160)[0] == 1, 'Persisted credentials or STA mode differ')
                row['checks'][phase + '_raw_credentials_and_mode'] = True
                row['checks'][phase + '_actual_station_dhcp_sntp'] = True
            after = (vm_folder / 'flash.bin').read_bytes()
            require(before[:0x9000] == after[:0x9000] and before[0xf000:RAW] == after[0xf000:RAW] and
                    before[RAW+0x1000:] == after[RAW+0x1000:], 'Executable/media/protected flash changed')
            row['checks']['protected_flash_unchanged'] = True
            row['passed'] = all(row['checks'].values())
            print('PASS real browser Wi-Fi:', scenario, flush=True)
        require(all(digest(Path(path)) == sha for path, sha in inputs.items()), 'Inputs changed during browser test')
        report['inputs_verified'] = len(inputs)
        report['passed'] = all(row['passed'] for row in report['flows'].values())
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if active is not None:
            vm.control(active, 'stop'); vm.ensure_stopped(active)
        vm.save_json(args.output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
