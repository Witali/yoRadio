"""Read actual SPI1 registers after an unchanged normal guest's SPIFFS error."""
import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.build/cyd-production-boot-replay-20261030-guest-spi-observer-01'
REPLAY = ROOT / 'tests/run-cyd-production-boot-replay.py'
COMMON = Path('C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat/tools/test_esp32_idf6_compat.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert not OUT.exists() and sha(REPLAY) == '0da3d484d7d7ed3becb5e2764a4d47780e779dccdae4f23984fff144a2068be0'
assert sha(COMMON) == '09146e1c15c90fc2d0b8c81eb0c3c2cbd057ac86254c0069440427a7d0d3f01b'
replay = load(REPLAY, 'canonical_production_replay')
common = load(COMMON, 'reviewed_qtest_pipe_transport')
facts, bindings, image, rom = replay.prepare('pdm')
for name, path in (('observer', Path(__file__).resolve()), ('qtest_pipe_controller', COMMON)):
    bindings[name] = dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
OUT.mkdir()
for name in ('observer', 'runner', 'qtest_pipe_controller'):
    shutil.copyfile(bindings[name]['path'], OUT / (name + '.py'))
flash = OUT / 'qemu-flash.bin'
flash.write_bytes(image)
assert sha(flash) == facts['original_flash_sha256']
console = OUT / 'qemu-console.log'
trace = OUT / 'nor-trace.log'
command = [str(replay.QEMU), '-M', 'esp32,st7789=on,audiodev=quiet', '-smp', '2', '-accel', 'tcg',
           '-L', str(rom), '-drive', 'file=' + str(flash) + ',if=mtd,format=raw', '-snapshot', '-nic', 'none',
           '-audiodev', 'none,id=quiet', '-display', 'none', '-serial', 'file:' + str(console), '-monitor', 'none',
           '-no-reboot', '-qtest', 'stdio', '-qtest-log', 'none', '-trace', 'enable=m25p80_complete_collecting',
           '-trace', 'enable=m25p80_command_decoded', '-trace', 'enable=m25p80_read_byte', '-D', str(trace)]
report = dict(completed=False, observation_qualified=False, original_boot_still_nonpass=True, command=command,
              facts=facts, bindings=bindings, debugger_or_pc_writes=False, qtest_writes_issued=False,
              guest_accelerator='tcg', guest_halt_requested=False, firmware_or_volume_modified=False,
              static_rx_loan_exercised=False, full_radio_startup_qualified=False,
              physical_device=False, external_network=False)


def save():
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


vm = None
save()
try:
    vm = common.StoppedQTest(command, OUT)  # Reuse its pipe/owner handling, not its usual stopped-CPU command.
    report['owned_qemu_pid'] = vm.proc.pid
    save()
    while True:
        assert not vm.errors and vm.proc.poll() is None
        assert not console.exists() or console.stat().st_size <= 8 * 1024 * 1024
        assert not trace.exists() or trace.stat().st_size <= 32 * 1024 * 1024
        if console.exists():
            text = console.read_text('utf-8', errors='replace')
            report.update(replay.observations(text, facts['app_version'], facts['elf_sha256']))
            if 'SPIFFS: mount failed, -10025' in text:
                before_address = vm.read(common.SPI + 4)
                offsets = dict(ctrl=8, clock=0x18, user=0x1c, user1=0x20, user2=0x24,
                               mosi_dlen=0x28, miso_dlen=0x2c, pin=0x34)
                registers = {name: vm.read(common.SPI + offset) for name, offset in offsets.items()}
                physical_address = before_address >> 8
                if physical_address in (0x3700fc, 0x3700fe, 0x3710fc):
                    registers['public_magic_buffer_word'] = vm.read(common.SPI + 0x80)
                after_address = vm.read(common.SPI + 4)
                report.update(registers=registers, address_register_before=before_address,
                              address_register_after=after_address,
                              coherent_address=before_address == after_address,
                              physical_address_if_usr=physical_address, completed=True)
                break
        assert time.monotonic() < vm.deadline
        time.sleep(0.01)
except BaseException as error:
    report.update(error_type=type(error).__name__, error=str(error))
finally:
    if vm is not None:
        vm.close()
        report.update(qemu_exit_status=vm.proc.returncode,
                      actual_cleanup='terminate-owned-normal-guest-observation',
                      transport_helper_cleanup_label=vm.cleanup_method,
                      stdout_actual_eof=vm.eof.is_set(), stdout_reader_joined=vm.reader is not None and not vm.reader.is_alive(),
                      controller_errors=vm.errors)
    changed = [name for name, pin in bindings.items() if sha(Path(pin['path'])) != pin['sha256']]
    report.update(changed_bound_inputs=changed, all_bound_inputs_current=not changed,
                  flash_unchanged_after_snapshot=sha(flash) == facts['original_flash_sha256'])
    report['observation_qualified'] = bool(report['completed'] and report.get('coherent_address') and
        report.get('old_flash_boundary_passed') and report.get('early_mpi_return_log_observed') and
        report.get('stdout_actual_eof') and report.get('stdout_reader_joined') and not report.get('controller_errors') and
        not changed and report['flash_unchanged_after_snapshot'])
    for name, path in (('console', console), ('nor_trace', trace)):
        if path.exists():
            report[name + '_sha256'] = sha(path)
    save()
summary = {name: report.get(name) for name in ('completed', 'observation_qualified', 'coherent_address',
    'physical_address_if_usr', 'old_flash_boundary_passed', 'early_mpi_return_log_observed', 'all_bound_inputs_current',
    'flash_unchanged_after_snapshot')}
if 'registers' in report:
    summary['control_registers'] = {k: v for k, v in report['registers'].items() if k != 'public_magic_buffer_word'}
    if 'public_magic_buffer_word' in report['registers']:
        address = report['physical_address_if_usr']
        summary['public_magic_word_matches_source'] = report['registers']['public_magic_buffer_word'] & 0xffff == int.from_bytes(image[address:address+2], 'little')
print(json.dumps(summary))
raise SystemExit(0 if report['observation_qualified'] else 1)
