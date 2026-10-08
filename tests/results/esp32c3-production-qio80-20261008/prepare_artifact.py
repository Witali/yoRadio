import hashlib
import json
from pathlib import Path
import re
import shutil
from elftools.elf.elffile import ELFFile

root = Path('.build/c3-production-qio80-20261008')
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-qio80')
artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80')
config = (build / 'sdkconfig').read_text()
options = dict(re.findall(r'^CONFIG_(\w+)=(.+)$', config, re.M))
on = ('ESPTOOLPY_FLASHMODE_QIO', 'ESPTOOLPY_FLASHFREQ_80M', 'ESPTOOLPY_FLASHSIZE_4MB',
      'ESP_CONSOLE_NONE', 'YORADIO_OUTPUT_TASK_FIRST', 'YORADIO_AAC_PLUS',
      'YORADIO_AAC_HIGH_HISTORY_PC19', 'YORADIO_AAC_LATE_SBR')
off = ('ESPTOOLPY_FLASHMODE_QOUT', 'ESPTOOLPY_FLASHMODE_DIO', 'ESPTOOLPY_FLASHMODE_DOUT',
       'YORADIO_DEEP_SLEEP_CLOCK', 'SPI_FLASH_AUTO_SUSPEND', 'MBEDTLS_DYNAMIC_BUFFER',
       'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')
assert all(options.get(k) == 'y' for k in on)
assert all(options.get(k) != 'y' for k in off)
assert options['LOG_DEFAULT_LEVEL'] == options['LOG_MAXIMUM_LEVEL'] == '0'
assert not any(v == 'y' and re.match(r'YORADIO_.*(?:PROFIL|QEMU|BENCH)', k)
               for k, v in options.items())
commands = json.loads((build / 'compile_commands.json').read_text())
assert not any(Path(row['file']).name in ('boot_probe.c', 'boot_benchmark.cpp') for row in commands)
with (build / 'yoradio_esp32c3_oled_native.elf').open('rb') as f:
    elf = ELFFile(f)
    symbols = {s.name for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert '__wrap_app_main' not in symbols
    sections = {s.name: dict(address=s['sh_addr'], bytes=s['sh_size']) for s in elf.iter_sections()
                if s.name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.flash.text', '.flash.rodata')}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(build / 'bootloader/bootloader.bin', artifact / 'bootloader.bin')
manifest = json.loads((artifact / 'manifest.json').read_text())
manifest.update(bootloader_sha256=sha(artifact / 'bootloader.bin'),
    production_profile=True, production_qualified=False, expected_flash_mode='qio', flash_mhz=80,
    deep_sleep=False, console_and_logs=False, flash_probe=False, lab_ca=False,
    source_overlay_sha256={p: sha(Path(p)) for p in (
        'idf/esp32c3-oled-native/sdkconfig.qio80.defaults',
        'idf/esp32c3-oled-native/main/CMakeLists.txt')},
    source_note='The local main CMake file includes an inactive CLZ benchmark block. '
                'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF; no CLZ/probe source or app_main wrapper is compiled.',
    build_recipe='tests/results/esp32c3-production-qio80-20261008/build.ps1',
    qualification='Build and AAC/HTTP link audits passed; physical installation and smoke checks pending')
(artifact / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(root / 'quiet-audit.json').write_text(json.dumps(dict(result='PASS',
    required_on=on, required_off=off, sections=sections,
    no_boot_benchmark_sources=True, no_app_main_wrapper=True,
    app_sha256=sha(artifact / 'app.bin'), bootloader_sha256=sha(artifact / 'bootloader.bin')),
    indent=2) + '\n')
for path in (build / 'log').glob('*'):
    if path.is_file():
        dest = root / 'build-logs' / path.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, dest)
print(json.dumps(dict(result='PASS', bytes=(artifact/'app.bin').stat().st_size, sections=sections)))
