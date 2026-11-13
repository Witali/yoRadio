"""Read-only Wi-Fi station/peer lifetime probe for the pinned Small TV app/ELF."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace


G_IC = 0x3FCB5524
BSS_SLOTS = tuple(0x3FCB4508 + 8 + 976*i for i in range(4))
ANCHORS = {
    'station_alloc_call': ('wifi_create_sta', 0x2E, '8297'),
    'station_alloc_return': ('wifi_create_sta', 0x30, '2A84'),
    'station_publish': ('wifi_create_sta', 0x48, '80C8'),
    'dedicated_alloc_call': ('wifi_create_sta', 0x66, '8297'),
    'dedicated_alloc_return': ('wifi_create_sta', 0x68, '2324A40E'),
    'dedicated_backpointer': ('wifi_create_sta', 0xB2, '80C3'),
    'active_publish': ('ieee80211_mlme_connect_bss', 0x16, '23A2A70E'),
    'active_clear': ('cnx_sta_leave', 0x22A, '23A2090E'),
    'active_cleared': ('cnx_sta_leave', 0x22E, 'BC4F'),
    'associated': ('cnx_sta_associated', 0, '4111'),
    'station_clear': ('wifi_destroy_sta', 0x48, '23280400'),
    'dedicated_free_call': ('wifi_destroy_sta', 0x5C, '8297'),
    'dedicated_free_return': ('wifi_destroy_sta', 0x5E, '832789DD'),
    'station_free_call': ('wifi_destroy_sta', 0x68, '8297'),
    'station_free_return': ('wifi_destroy_sta', 0x6A, 'EFA0AF84'),
}
APP_ELF = {
    '564ea463fc98d4a6a72e076e829106433d0cd7465f7f0f6a821c7100d92f50bb':
        'e01db928f75fdd6c09d2ce9b49e2d512b75ab1dfe5eaaa132963492c197709c4',
    '88927726d7408c605dfb1f8eec416a602c6039ecf7f58b6f83ed3d9b58debf82':
        '3bf88f53f31803386b055aa89e55aada48a30306a6f98201c27a3154d10fa002',
}
QEMU_SHA = '2df903276e66afe0095ad19afd6d8b7201bcca3fbda073f3edb958934aef0001'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ram(address, size):
    assert address % 4 == 0 and 0x3FCA0000 <= address <= 0x3FCE0000 - size
    return address


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('repo', 'dependency-root', 'qemu-tools', 'qemu', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    parser.add_argument('--artifact-root', type=Path)
    parser.add_argument('--elf', type=Path)
    parser.add_argument('--cancel-association', action='store_true')
    parser.add_argument('--observe-restart', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = args.repo.resolve()
    deps = args.dependency_root.resolve()
    sys.path[:0] = [str(root/'Small_TV/src/tests'), str(root/'Small_TV/qemu/parity'),
                   str(deps/'.build/small-tv-parity/oracle-deps'), str(args.qemu_tools/'tools')]
    import compare
    import small_tv_vm as vm
    import time_qemu
    from elftools.elf.elffile import ELFFile
    from gdb_observer import Observer
    from small_tv_http_test import clean_uart, http, wait_for, wait_http
    from weather_qemu import read_bytes

    artifacts = args.artifact_root.resolve() if args.artifact_root else root
    elf = args.elf or root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    archive = artifacts/'firmware/development/small-tv-esp32c2-reconstructed'
    app = archive/'app.bin'
    rom = deps/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    profile = root/'Small_TV/qemu/profiles/small-tv-c2.json'
    app_sha, elf_sha = sha(app), sha(elf)
    assert elf_sha == APP_ELF[app_sha] and sha(args.qemu) == QEMU_SHA
    assert app.read_bytes()[176:208].hex() == elf_sha
    anchors = {}
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        symbols = image.get_section_by_name('.symtab')
        connected = symbols.get_symbol_by_name('connected')
        assert len(connected) == 1 and connected[0]['st_size'] == 1
        connected = connected[0]['st_value']
        assert symbols.get_symbol_by_name('g_ic')[0]['st_value'] == G_IC
        mgr = symbols.get_symbol_by_name('g_cnxMgr')[0]
        assert mgr['st_value'] == 0x3FCB4508 and mgr['st_size'] >= 8 + 4 * 976
        alloc, = symbols.get_symbol_by_name('wifi_zalloc_wrapper')
        release, = symbols.get_symbol_by_name('free')
        alloc_target, free_target = alloc['st_value'], release['st_value']
        segments = list(image.iter_segments(type='PT_LOAD'))
        for name, (function, offset, expected) in ANCHORS.items():
            if name == 'associated' and not args.cancel_association:
                continue
            if not args.observe_restart and name.startswith(('station_clear', 'dedicated_free', 'station_free')):
                continue
            function_symbol, = symbols.get_symbol_by_name(function)
            assert offset < function_symbol['st_size']
            pc = function_symbol['st_value'] + offset
            data = bytes.fromhex(expected)
            segment, = (s for s in segments if s['p_flags'] & 1 and
                        s['p_vaddr'] <= pc <= s['p_vaddr'] + s['p_filesz'] - len(data))
            i = pc - segment['p_vaddr']
            assert segment.data()[i:i+len(data)] == data, hex(pc)
            anchors[name] = pc
    files = [Path(__file__), elf, args.qemu, rom, profile, root/'Small_TV/src/tests/gdb_observer.py',
             root/'Small_TV/qemu/parity/compare.py', root/'Small_TV/src/tests/time_qemu.py',
             root/'Small_TV/src/tests/weather_qemu.py']
    files.extend(args.qemu_tools.glob('tools/*.py'))
    files.extend(archive/name for name in ('app.bin', 'assets.bin', 'bootloader.bin',
                                           'partition-table.bin', 'manifest.json'))
    pins = {path: sha(path) for path in files}
    result = dict(passed=False, firmware_sha256=app_sha, elf_sha256=elf_sha, qemu_sha256=QEMU_SHA,
                  events=[], http_statuses=[], no_debugger_writes=True, full_lifecycle_proved=False,
                  cancel_association_requested=args.cancel_association,
                  anchors={name: hex(pc) for name, pc in anchors.items()},
                  osi_targets=dict(zalloc=alloc_target, free=free_target))
    observer = session = None
    folder = args.output/'vm'
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    options = SimpleNamespace(yoradio=str(artifacts), qemu=str(args.qemu), rom_elf=str(rom),
        hardware_profile=str(profile), firmware='reconstructed', network='clock',
        display='none', persistent=False, paused=True, gdb_port=port, service_port=0)
    vm.seed_clock_network = compare.seed_settings
    compare.CURRENT_THEME = 'simple'
    try:
        session, _ = vm.launch(options, folder)
        observer = Observer(port)
        observer.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        def word(address):
            return int.from_bytes(observer.memory(ram(address, 4), 4), 'little')
        def state():
            sta = word(G_IC + 16)
            active, dedicated = (word(sta+228), word(sta+232)) if sta else (0, 0)
            row = dict(station=sta, active_peer=active, dedicated_peer=dedicated)
            if dedicated:
                row['dedicated_backpointer'] = word(dedicated)
            return row

        def snapshot(phase, **values):
            row = dict(phase=phase, pc=observer.register(32), **state(), **values)
            result['events'].append(row)
            return row
        def stop_at(name, async_wait=False):
            pc = anchors[name]
            with observer.time_limit(30):
                if async_wait:
                    assert observer.receive().startswith(('T05','S05'))
                    assert observer.register(32) == pc
                else:
                    observer.breakpoint(pc)
                    observer.continue_to(pc)
                observer.breakpoint(pc, False)
        def status(url):
            code, _ = http(url, '/getclocktype', timeout=10)
            result['http_statuses'].append(code)
            assert code == 200
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            time_qemu.service(qmp, 1781265600, 0, False)
            stop_at('station_alloc_call')
            assert observer.register(10) == 536 and word(G_IC+16) == 0
            assert observer.register(15) == alloc_target
            stop_at('station_alloc_return')
            station = ram(observer.register(10), 536)
            snapshot('station-allocation-return', returned=station, requested=536)
            stop_at('dedicated_alloc_call')
            assert observer.register(10) == 976 and word(G_IC+16) == station
            assert observer.register(15) == alloc_target
            stop_at('dedicated_alloc_return')
            dedicated = ram(observer.register(10), 976)
            assert word(station+232) == 0
            snapshot('dedicated-allocation-return', returned=dedicated, requested=976)
            stop_at('active_publish')
            candidate = ram(observer.register(10), 976)
            before = snapshot('initial-publication', candidate=candidate)
            assert before['active_peer'] == 0 and before['dedicated_peer'] == dedicated
            assert before['dedicated_backpointer'] == station and candidate != dedicated
            assert candidate in BSS_SLOTS and word(candidate) == station
            if args.cancel_association:
                # Remove the AP at the first candidate publication and require
                # the leave path to clear it before SDK association succeeds.
                qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=False)
                assert not qmp.execute('qom-get', path='/machine/wifi', property='station-ap-online')
                observer.breakpoint(anchors['associated'])
                observer.breakpoint(anchors['active_clear'])
                observer.resume()
                with observer.time_limit(25):
                    assert observer.receive().startswith(('T05', 'S05'))
                    cancelled = snapshot('association-stop')
                assert cancelled['pc'] == anchors['active_clear'], 'Association succeeded before cancellation'
                assert (cancelled['station'], cancelled['active_peer'], cancelled['dedicated_peer'],
                        cancelled['dedicated_backpointer']) == (station, candidate, dedicated, station)
                observer.breakpoint(anchors['associated'], False)
                observer.breakpoint(anchors['active_clear'], False)
                stop_at('active_cleared')
                assert snapshot('association-cleared')['active_peer'] == 0
                observer.breakpoint(anchors['active_publish'])
                observer.resume()
                qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=True)
                stop_at('active_publish', True)
                candidate = ram(observer.register(10), 976)
                retry = snapshot('post-cancellation-retry', candidate=candidate)
                assert (retry['station'], retry['active_peer'], retry['dedicated_peer'],
                        retry['dedicated_backpointer']) == (station, 0, dedicated, station)
                assert candidate in BSS_SLOTS and word(candidate) == station
            observer.resume()
            url = session['web_urls']['station']
            wait_http(url, '/getclocktype', seconds=45)
            status(url)
            observer.interrupt()
            up = snapshot('initial-connected')
            assert up['station'] == station and up['active_peer'] == candidate
            observer.breakpoint(anchors['active_clear'])
            observer.resume()
            qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=False)
            stop_at('active_clear', True)
            before_clear = snapshot('before-active-clear')
            assert before_clear['active_peer'] == candidate
            stop_at('active_cleared')
            after_clear = snapshot('after-active-clear')
            assert after_clear['active_peer'] == 0
            observer.resume()
            wait_for(lambda: read_bytes(qmp, connected, 1) == b'\0',
                     'Station did not report link loss', seconds=10)
            observer.interrupt()
            down = snapshot('disconnected')
            assert down['active_peer'] == 0
            observer.breakpoint(anchors['active_publish'])
            observer.resume()
            qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=True)
            stop_at('active_publish', True)
            next_peer = ram(observer.register(10), 976)
            republish = snapshot('reconnect-publication', candidate=next_peer)
            assert republish['active_peer'] == 0 and next_peer != dedicated
            assert next_peer in BSS_SLOTS and word(next_peer) == station
            observer.resume()
            wait_http(url, '/getclocktype', seconds=45)
            status(url)
            observer.interrupt()
            after = snapshot('reconnected')
            assert after['active_peer'] == next_peer
            for row in (up, before_clear, after_clear, down, republish, after):
                assert (row['station'], row['dedicated_peer'], row['dedicated_backpointer']) == (
                    station, dedicated, station)
            if args.observe_restart:
                observer.breakpoint(anchors['station_clear'])
                observer.resume()
                status_code, _ = http(url, '/restart', payload={}, timeout=10, origin=url)
                result['restart_http_status'] = status_code
                assert status_code == 200
                stop_at('station_clear', True)
                stopping = snapshot('stop-before-station-clear')
                assert stopping['station'] == station and stopping['dedicated_peer'] == dedicated
                assert stopping['active_peer'] == 0
                stop_at('dedicated_free_call')
                assert observer.register(10) == dedicated and observer.register(15) == free_target
                assert snapshot('stop-dedicated-free-call', argument=dedicated)['station'] == 0
                stop_at('dedicated_free_return')
                assert snapshot('stop-dedicated-free-return')['station'] == 0
                stop_at('station_free_call')
                assert observer.register(10) == station and observer.register(15) == free_target
                assert snapshot('stop-station-free-call', argument=station)['station'] == 0
                stop_at('station_free_return')
                assert snapshot('stop-station-free-return')['station'] == 0
                stop_at('station_alloc_call')
                assert snapshot('new-boot-station-allocation')['station'] == 0
                observer.resume()
                wait_http(url, '/getclocktype', seconds=45)
                status(url)
            result['passed'] = True
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        if observer:
            observer.close()
        if session:
            try:
                vm.control(folder, 'stop')
                vm.ensure_stopped(folder)
                result['vm_stopped'] = True
                result['uart_clean'] = clean_uart(folder)
            except Exception as error:
                result['cleanup_error'] = type(error).__name__
        result['inputs_unchanged'] = all(sha(p) == digest for p, digest in pins.items())
        result['passed'] &= all(result.get(key, False) for key in ('vm_stopped','uart_clean','inputs_unchanged'))
        vm.save_json(args.output/'report.json', result)
    if not result['passed']:
        raise SystemExit(1)
    print(f"Checked {len(result['events'])} station snapshots and {len(result['http_statuses'])} HTTP responses")


if __name__ == '__main__':
    main()
