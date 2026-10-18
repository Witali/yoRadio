"""Measure the first native clock frame after an actual UDP SNTP notification."""
import argparse
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--yoradio', type=Path, default=ROOT)
parser.add_argument('--dependency-root', type=Path)
parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
dependencies = args.dependency_root or args.yoradio
sys.path[:0] = [str(args.qemu_root / 'tools'),
               str(dependencies / '.build/small-tv-parity/oracle-deps')]
import small_tv_vm as vm
from small_tv_http_test import clean_uart, wait_for
from gdb_observer import Observer
import weather_qemu as weather
import scene_qemu as scene
from elftools.elf.elffile import ELFFile

weather.vm = vm
weather.wait_for = wait_for
scene.vm = vm
args.output.mkdir(parents=True, exist_ok=False)
elf_path = args.yoradio / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
app_path = args.yoradio / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
elf_sha = vm.digest(elf_path.read_bytes())
app_sha = vm.digest(app_path.read_bytes())
if app_path.read_bytes()[176:208] != bytes.fromhex(elf_sha):
    raise ValueError('App/ELF pair mismatch')
with elf_path.open('rb') as stream:
    elf = ELFFile(stream)
    table = list(elf.get_section_by_name('.symtab').iter_symbols())
    symbols = {item.name: item['st_value'] for item in table if item['st_value']}
    for name in ('time_sync_notify', 'factory_draw_classic', 'connected', 'time_synced'):
        if len([item for item in table if item.name == name and item['st_value']]) != 1:
            raise ValueError('Missing or ambiguous compiled symbol: ' + name)

fixture = weather.WeatherFixture(['Shenzhen,CN'])
fixture.set_response(200)
with socket.socket() as reservation:
    reservation.bind(('127.0.0.1', 0))
    port = reservation.getsockname()[1]
options = SimpleNamespace(
    yoradio=str(args.yoradio), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
    rom_elf=str(dependencies / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
    hardware_profile=str(args.yoradio / 'Small_TV/qemu/profiles/small-tv-c2.json'),
    network='clock', display='none', persistent=False, paused=True, gdb_port=port,
    firmware='reconstructed', service_port=fixture.port)
paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
                         ('gdb_observer.py', 'weather_qemu.py', 'scene_qemu.py')]]
fingerprints = {str(path.relative_to(ROOT)).replace('\\', '/'): vm.digest(path.read_bytes())
                for path in paths}
helpers = {name: vm.digest((args.qemu_root / 'tools' / name).read_bytes()) for name in
           ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py',
            'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py', 'small_tv_display.py')}
result = {'passed': False, 'scope': __doc__, 'app_sha256': app_sha,
          'native_elf_sha256': elf_sha, 'test_inputs': fingerprints,
          'helper_sha256': helpers, 'qemu_sha256': vm.digest(Path(options.qemu).read_bytes())}
session = observer = None


def completed_call(qmp, name):
    """Observe entry/return with hardware breakpoints; verify the guest instructions stay intact."""
    entry = symbols[name]
    observer.breakpoint(entry)
    observer.continue_to(entry)
    entry_code = observer.memory(entry, 4)
    started = weather.virtual_seconds(qmp)
    target = observer.register(1)
    return_code = observer.memory(target, 4)
    observer.breakpoint(entry, False)
    observer.breakpoint(target)
    observer.continue_to(target)
    observer.breakpoint(target, False)
    if observer.memory(entry, 4) != entry_code or observer.memory(target, 4) != return_code:
        raise AssertionError('Hardware breakpoint changed guest code')
    return {'entry_guest_seconds': started, 'return_guest_seconds': weather.virtual_seconds(qmp)}


try:
    session, prepared = vm.launch(options, args.output)
    result['sources'] = prepared['sources']
    observer = Observer(port)
    observer.socket.settimeout(45)
    with vm.QMP(session['qmp_port'], session['name']) as qmp:
        result['sync'] = completed_call(qmp, 'time_sync_notify')
        if not observer.memory(symbols['connected'], 1)[0] or not observer.memory(symbols['time_synced'], 1)[0]:
            raise AssertionError('Actual SNTP notification did not produce a usable station clock')
        result['first_clock'] = completed_call(qmp, 'factory_draw_classic')
        rgb = scene.picture(qmp, args.output, 'first-clock')
        result['rgb_sha256'] = vm.digest(rgb)
        result['different_colors'] = len({rgb[index:index + 3] for index in range(0, len(rgb), 3)})
        delay = result['first_clock']['entry_guest_seconds'] - result['sync']['return_guest_seconds']
        result['ready_wait_guest_seconds'] = delay
        observer.resume()
        if result['different_colors'] < 2:
            raise AssertionError('First clock frame is blank')
        if not 0 <= delay <= .5:
            raise AssertionError('Ready clock remained on the startup screen: ' + str(delay))
        result['passed'] = clean_uart(args.output)
except Exception as error:
    result['error'] = str(error)
    raise
finally:
    if observer:
        observer.close()
    if session:
        try:
            vm.control(args.output, 'stop')
        finally:
            vm.ensure_stopped(args.output)
    fixture.close()
    result['inputs_unchanged'] = (
        elf_sha == vm.digest(elf_path.read_bytes()) and app_sha == vm.digest(app_path.read_bytes()) and
        result['qemu_sha256'] == vm.digest(Path(options.qemu).read_bytes()) and
        all(vm.digest((ROOT / name).read_bytes()) == sha for name, sha in fingerprints.items()) and
        all(vm.digest((args.qemu_root / 'tools' / name).read_bytes()) == sha for name, sha in helpers.items()))
    result['passed'] &= result['inputs_unchanged']
    vm.save_json(args.output / 'report.json', result)
raise SystemExit(0 if result['passed'] else 1)
