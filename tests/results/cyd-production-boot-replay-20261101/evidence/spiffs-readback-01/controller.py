"""Compare real SPI1 model reads with the unchanged original SPIFFS payload."""
import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.build/cyd-production-boot-replay-20261030-spiffs-readback-01'
BASE = ROOT / '.build/cyd-production-boot-replay-20261030-pdm-01/qemu-flash.bin'
QEMU = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
COMMON = Path('C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat/tools/test_esp32_idf6_compat.py')
COMMON_SHA = '09146e1c15c90fc2d0b8c81eb0c3c2cbd057ac86254c0069440427a7d0d3f01b'
ROM = Path('C:/Work/QEMU-ESP32/pc-bios')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not OUT.exists() and sha(QEMU) == QEMU_SHA and sha(COMMON) == COMMON_SHA
assert sha(BASE) == '4eb701f7c78a1a7aa88c1f2cd72c355f626c9cb9db0d503012fc177a03125e2a'
OUT.mkdir()
shutil.copyfile(__file__, OUT / 'controller.py')
shutil.copyfile(COMMON, OUT / 'qtest-controller.py')
flash = OUT / 'qemu-flash.bin'
shutil.copyfile(BASE, flash)
image = flash.read_bytes()
expected_spiffs = image[0x370000:0x400000]
assert len(expected_spiffs) == 0x90000
spec = importlib.util.spec_from_file_location('reviewed_spi_qtest', COMMON)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
paths = [QEMU, COMMON, BASE, flash, Path(__file__).resolve(), ROM / 'esp32-v3-rom.bin', ROM / 'esp32-v3-rom-app.bin']
before = {str(path): sha(path) for path in paths}
command = [str(QEMU), '-M', 'esp32,audiodev=quiet', '-smp', '2', '-accel', 'qtest', '-S', '-L', str(ROM),
           '-drive', 'file=' + str(flash) + ',if=mtd,format=raw', '-snapshot', '-nic', 'none', '-audiodev', 'none,id=quiet',
           '-display', 'none', '-serial', 'none', '-monitor', 'none', '-qtest', 'stdio', '-qtest-log', 'none']
report = dict(passed=False, completed=False, command=command, inputs_before=before, checks=[],
              guest_cpus_resumed=False, production_firmware_executed=False, data_volume_substituted=False,
              application_or_config_modified=False, physical_device=False, external_network=False,
              exact_saved_flash_layout_present=True, full_read_chunks_completed=0, source_volume_sha256=hashlib.sha256(expected_spiffs).hexdigest())


def save():
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def equal(label, observed, expected, **fields):
    report['checks'].append(dict(case=label, passed=observed == expected, bytes=len(observed),
        actual_sha256=hashlib.sha256(observed).hexdigest(), expected_sha256=hashlib.sha256(expected).hexdigest(), **fields))


save()
vm = None
try:
    vm = common.StoppedQTest(command, OUT)
    report['owned_qemu_pid'] = vm.proc.pid
    save()
    vm.write(common.SPI + 0x18, 1 << 31)  # Actual documented 80 MHz source-clock selection.
    equal('JEDEC identity', common.transfer(vm, 0x9f, rx=3), b'\xc8\x40\x16')
    common.transfer(vm, 0x06)
    common.transfer(vm, 0x31, tx=b'\x02')
    equal('written GD QE continuous readback', common.transfer(vm, 0x35, rx=3), b'\x02' * 3)
    for mode, bits, dummy in (('slow', 24, 1), ('fast', 24, 9), ('dio', 28, 3), ('qio', 28, 6)):
        for block in range(144):
            address = 0x370000 + block * 4096 + 252
            for count in (2, 4):
                observed = common.transfer(vm, common.MODES[mode][0], address=address, rx=count, mode=mode,
                                           addr_bits=bits, dummy_clocks=dummy)
                equal('block magic and aligned read', observed, image[address:address + count],
                      mode=mode, addr_bits=bits, dummy_clocks=dummy, block=block, address=address)
        save()
    full = bytearray()
    for relative in range(0, 0x90000, 64):
        full.extend(common.transfer(vm, 0xeb, address=0x370000 + relative, rx=64,
                                   mode='qio', addr_bits=28, dummy_clocks=6))
        report['full_read_chunks_completed'] += 1
        if not report['full_read_chunks_completed'] % 256:
            save()
    (OUT / 'spiffs-readback.bin').write_bytes(full)
    equal('complete SPIFFS via SDK QIO28 plus one sampling clock', bytes(full), expected_spiffs,
          mode='qio', addr_bits=28, dummy_clocks=6, start=0x370000)
    report['complete_readback_bytes'] = len(full)
    report['complete_readback_sha256'] = hashlib.sha256(full).hexdigest()
    report['completed'] = True
except BaseException as error:
    report.update(error_type=type(error).__name__, error=str(error))
finally:
    if vm is not None:
        vm.close()
        report.update(qemu_exit_status=vm.proc.returncode, cleanup_method=vm.cleanup_method,
                      stdout_actual_eof=vm.eof.is_set(), stdout_reader_joined=vm.reader is not None and not vm.reader.is_alive(),
                      controller_errors=vm.errors)
    after = {str(path): sha(path) for path in paths}
    report.update(inputs_after=after, inputs_unchanged=before == after)
    report['passed'] = bool(report['completed'] and vm is not None and not vm.errors and
                            report['stdout_actual_eof'] and report['stdout_reader_joined'] and
                            report['inputs_unchanged'] and all(row['passed'] for row in report['checks']))
    save()
print(json.dumps(dict(passed=report['passed'], completed=report['completed'],
    comparisons=len(report['checks']), failures=sum(not row['passed'] for row in report['checks']),
    full_read_chunks_completed=report['full_read_chunks_completed'],
    complete_readback_bytes=report.get('complete_readback_bytes'),
    complete_readback_sha256=report.get('complete_readback_sha256'),
    inputs_unchanged=report['inputs_unchanged'], guest_cpus_resumed=False)))
raise SystemExit(0 if report['passed'] else 1)
