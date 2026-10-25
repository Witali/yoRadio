"""Read event-11 registration metadata from two owned, unmodified firmware VMs."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import sha
from reverse.timer_event11_registration import qualify
from timer_registration_metadata import decode


def sample(qmp, layout, read):
    """Stop coherently, read only typed numeric metadata, and always resume."""
    qmp.execute('stop')
    try:
        raw = []
        def capture(address, size):
            """Keep only the decoder's explicit typed reads for offline replay."""
            data = read(qmp, address, size)
            raw.append(dict(address=address, size=size, hex=data.hex()))
            return data
        result = decode(capture, layout)
        result['raw_reads'] = raw
        return result
    finally:
        qmp.execute('cont')


def main():
    """Use fresh isolated VM copies; preserve original producer trees and long runs."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'native', 'old-pp', 'new-pp', 'old-net', 'new-net',
                 'yoradio', 'tools', 'qemu', 'rom', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(args.tools), str(args.yoradio / 'Small_TV/qemu/parity')]
    import small_tv_vm as vm
    from small_tv_http_test import wait_http, clean_uart
    import compare
    import weather_qemu as weather
    from weather_qemu import read_bytes
    layout = qualify(args.factory.read_bytes(), args.native.read_bytes(), args.old_pp, args.new_pp,
                     args.old_net, args.new_net)
    archive = args.yoradio / 'firmware/development/small-tv-esp32c2-reconstructed'
    files = [Path(__file__), args.factory, args.native, args.old_pp, args.new_pp, args.old_net, args.new_net,
             Path(__file__).with_name('timer_registration_metadata.py'),
             args.qemu, args.rom, args.yoradio / 'Small_TV/qemu/profiles/small-tv-c2.json',
             args.yoradio / 'Small_TV/full-flash.bin', args.yoradio / 'Small_TV/manifest.json',
             args.yoradio / 'Small_TV/qemu/parity/compare.py', Path(weather.__file__)]
    files += list(args.tools.glob('*.py'))
    files += list(archive.glob('*.json')) + list(archive.glob('*.bin'))
    source = Path(__file__).resolve().parents[1]
    files += [source / name for name in ('tools/audit_factory_xrefs.py', 'tools/reverse/elf_archive.py',
              'tools/reverse/rv32_link_match.py', 'tools/reverse/timer_event11_match.py',
              'tools/reverse/timer_event11_registration.py')]
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in files}
    assert sha(args.native.read_bytes()) == (archive / 'app.bin').read_bytes()[176:208].hex()
    weather.vm = vm
    fixture = weather.WeatherFixture(['Shenzhen,CN']); fixture.set_response(200)
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = compare.seed_settings; compare.CURRENT_THEME = 'simple'
    result = dict(passed=False, tested_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  inputs_sha256=pins, qemu_sha256=sha(args.qemu.read_bytes()), flows={},
                  full_runtime_lifecycle_proved=False, physical_hardware_tested=False)
    try:
        for variant, key in (('original','factory'), ('reconstructed','native')):
            options = SimpleNamespace(yoradio=str(args.yoradio), qemu=str(args.qemu), rom_elf=str(args.rom),
                hardware_profile=str(args.yoradio / 'Small_TV/qemu/profiles/small-tv-c2.json'),
                network='clock', firmware=variant, display='none', persistent=False, paused=False,
                gdb_port=0, service_port=fixture.port)
            folder, session = args.output / variant, None
            flow = dict(passed=False); result['flows'][key] = flow
            try:
                session, prepared = vm.launch(options, folder)
                flow.update(session=session, sources=prepared['sources'])
                print(json.dumps(dict(launched=key, pid=session['pid'], name=session['name'])), flush=True)
                body = wait_http(session['web_urls']['station'], expected=b'/setclocktype')
                assert b'/setclocktype' in body
                with vm.QMP(session['qmp_port'], session['name']) as qmp:
                    observed = sample(qmp, layout['layouts'][key], read_bytes)
                flow['metadata'] = observed
                prior = layout['layouts'][key]['prior']
                assert observed['osi_pointer'] == prior['osi_table']['address']
                assert observed['osi_table_sha256'] == prior['osi_table']['sha256']
                assert observed['post_callback'] and observed['post_callback'] % 2 == 0
                flow['passed'] = True
            finally:
                if session:
                    vm.control(folder, 'stop')
                    flow['owned_stop_completed'] = True
                flow['uart_clean'] = clean_uart(folder)
                flow['passed'] &= flow['uart_clean']
                vm.save_json(folder / 'registration-observation.json', flow)
            print(json.dumps(dict(finished=key, passed=flow['passed'],
                                 metadata={k:v for k,v in flow['metadata'].items() if k != 'raw_reads'})), flush=True)
        result['inputs_unchanged'] = all(sha(Path(path).read_bytes()) == digest for path, digest in pins.items())
        assert result['inputs_unchanged'] and all(flow['passed'] for flow in result['flows'].values())
        result['passed'] = True
    finally:
        vm.seed_clock_network = previous_seed
        fixture.close()
        vm.save_json(args.output / 'report.json', result)
    print(json.dumps(dict(passed=True, variants=list(result['flows']))))


if __name__ == '__main__': main()
