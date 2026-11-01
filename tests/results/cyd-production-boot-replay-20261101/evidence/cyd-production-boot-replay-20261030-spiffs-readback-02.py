"""Complete SPIFFS readback with equivalent batched QTest register accesses."""
import hashlib
import importlib.util
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.build/cyd-production-boot-replay-20261030-spiffs-readback-02'
BASE = ROOT / '.build/cyd-production-boot-replay-20261030-pdm-01/qemu-flash.bin'
QEMU = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
COMMON = Path('C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat/tools/test_esp32_idf6_compat.py')
COMMON_SHA = '09146e1c15c90fc2d0b8c81eb0c3c2cbd057ac86254c0069440427a7d0d3f01b'
QTEST = COMMON.parents[1] / 'system/qtest.c'
ROM = Path('C:/Work/QEMU-ESP32/pc-bios')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not OUT.exists() and sha(QEMU) == QEMU_SHA and sha(COMMON) == COMMON_SHA
assert sha(BASE) == '4eb701f7c78a1a7aa88c1f2cd72c355f626c9cb9db0d503012fc177a03125e2a'
OUT.mkdir()
shutil.copyfile(__file__, OUT / 'controller.py')
shutil.copyfile(COMMON, OUT / 'scalar-qtest-controller.py')
shutil.copyfile(QTEST, OUT / 'qtest-protocol-source.c')
flash = OUT / 'qemu-flash.bin'
shutil.copyfile(BASE, flash)
image = flash.read_bytes()
expected = image[0x370000:0x400000]
spec = importlib.util.spec_from_file_location('reviewed_spi_qtest', COMMON)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
paths = [QEMU, COMMON, QTEST, BASE, flash, Path(__file__).resolve(), ROM / 'esp32-v3-rom.bin', ROM / 'esp32-v3-rom-app.bin']
before = {str(path): sha(path) for path in paths}
command = [str(QEMU), '-M', 'esp32,audiodev=quiet', '-smp', '2', '-accel', 'qtest', '-S', '-L', str(ROM),
           '-drive', 'file=' + str(flash) + ',if=mtd,format=raw', '-snapshot', '-nic', 'none', '-audiodev', 'none,id=quiet',
           '-display', 'none', '-serial', 'none', '-monitor', 'none', '-qtest', 'stdio', '-qtest-log', 'none']
report = dict(passed=False, completed=False, command=command, inputs_before=before, scalar_batch_checks=[],
              guest_cpus_resumed=False, production_firmware_executed=False, data_volume_substituted=False,
              application_or_config_modified=False, physical_device=False, external_network=False,
              exact_saved_flash_layout_present=True, full_read_chunks_completed=0,
              source_volume_sha256=hashlib.sha256(expected).hexdigest(), host_deadline_seconds=60,
              spi_transaction=dict(mode='qio', address_bits=28, dummy_clocks=6, source_clock_hz=80000000))


def save():
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def write_bytes(vm, address, body):
    assert vm.command('write ' + hex(address) + ' ' + hex(len(body)) + ' 0x' + body.hex()) == ''


def read_bytes(vm, address, length):
    answer = vm.command('read ' + hex(address) + ' ' + hex(length))
    assert answer.startswith('0x')
    body = bytes.fromhex(answer[2:])
    assert len(body) == length
    return body


def batch_read(vm, address, count):
    assert 0 < count <= 64
    vm.write(common.SPI + 8, (1 << 13) | (1 << 24))
    vm.write(common.SPI + 4, (address << 8) | 0xff)
    user = (1 << 31) | (1 << 30) | (1 << 29) | (1 << 28)
    registers = struct.pack('<IIIII', user, (27 << 26) | 5, (7 << 28) | 0xeb, 0, count * 8 - 1)
    write_bytes(vm, common.SPI + 0x1c, registers)
    write_bytes(vm, common.SPI + 0x80, b'\xa5' * 64)
    vm.write(common.SPI + 0x34, 6)
    vm.write(common.SPI, 1 << 18)
    return read_bytes(vm, common.SPI + 0x80, count)


vm = None
save()
try:
    vm = common.StoppedQTest(command, OUT)
    report['owned_qemu_pid'] = vm.proc.pid
    save()
    vm.write(common.SPI + 0x18, 1 << 31)
    assert common.transfer(vm, 0x9f, rx=3) == b'\xc8\x40\x16'
    common.transfer(vm, 0x06)
    common.transfer(vm, 0x31, tx=b'\x02')
    assert common.transfer(vm, 0x35, rx=3) == b'\x02' * 3
    for address in (0x370000, 0x3700fc, 0x3710fc, 0x3fffbc):
        for count in (2, 4, 16, 64):
            scalar = common.transfer(vm, 0xeb, address=address, rx=count, mode='qio', addr_bits=28, dummy_clocks=6)
            batched = batch_read(vm, address, count)
            expect = image[address:address + count]
            report['scalar_batch_checks'].append(dict(address=address, bytes=count,
                scalar_sha256=hashlib.sha256(scalar).hexdigest(), batch_sha256=hashlib.sha256(batched).hexdigest(),
                expected_sha256=hashlib.sha256(expect).hexdigest(), passed=scalar == batched == expect))
    assert all(row['passed'] for row in report['scalar_batch_checks'])
    save()
    full = bytearray()
    for relative in range(0, 0x90000, 64):
        full.extend(batch_read(vm, 0x370000 + relative, 64))
        report['full_read_chunks_completed'] += 1
        if not report['full_read_chunks_completed'] % 256:
            save()
    (OUT / 'spiffs-readback.bin').write_bytes(full)
    report.update(complete_readback_bytes=len(full), complete_readback_sha256=hashlib.sha256(full).hexdigest(),
                  all_spiffs_bytes_equal=bytes(full) == expected, completed=True)
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
                            report['stdout_actual_eof'] and report['stdout_reader_joined'] and report['inputs_unchanged'] and
                            report.get('all_spiffs_bytes_equal') and all(row['passed'] for row in report['scalar_batch_checks']))
    save()
print(json.dumps(dict(passed=report['passed'], completed=report['completed'],
    scalar_batch_checks=len(report['scalar_batch_checks']), full_read_chunks_completed=report['full_read_chunks_completed'],
    complete_readback_bytes=report.get('complete_readback_bytes'), complete_readback_sha256=report.get('complete_readback_sha256'),
    inputs_unchanged=report['inputs_unchanged'], guest_cpus_resumed=False)))
raise SystemExit(0 if report['passed'] else 1)
