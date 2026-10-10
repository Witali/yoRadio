"""Verify the narrow clock-only build before app-only OTA."""
import hashlib
import json
from pathlib import Path
import re
import sys
from elftools.elf.elffile import ELFFile

REPO = Path.cwd()
EVIDENCE = Path(__file__).resolve().parent
ROOT = REPO / '.build/c3-pdm-listening-20261010'
BUILD = ROOT / 'build'
SOURCE = ROOT / 'source'
ART = REPO / 'firmware/development/esp32c3-idf61-listen-48k'
OLD = REPO / 'firmware/development/esp32c3-idf-6.1-r9a97-production-qio80'
BASE_BUILD = REPO / 'idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-qio80'
sys.path[:0] = [str(REPO / 'tools/esp32c3_tests'), str(EVIDENCE / 'overlay/tools')]
from ota import image_info
from patch_i2s_pdm_clock import patch


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config(path):
    return dict(re.findall(r'^(CONFIG_\w+)=(.+)$', path.read_text(), re.M))


def code_sections(path):
    with path.open('rb') as stream:
        return {s.name: dict(bytes=s['sh_size'], sha256=hashlib.sha256(s.data()).hexdigest())
                for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.text', '.rodata')) and s['sh_size']}


def objects(folder):
    paths = []
    for pattern in ('flac_decoder.cpp.obj', 'custom_flac_adapter.cpp.obj',
                    'native_aac_decoder.c.obj', 'aac_*.c.obj', 'native_audio_output.c.obj'):
        paths += list(folder.rglob(pattern))
    paths += list((folder / 'esp-idf/main/compact5').glob('*.obj'))
    result = {}
    for path in paths:
        assert path.name not in result
        result[path.name] = code_sections(path)
    return result


def main():
    source_manifest = json.loads((EVIDENCE / 'source-manifest.json').read_text())
    overlays = source_manifest['changed_or_added_source_sha256']
    for name, digest in source_manifest['original_source_sha256'].items():
        assert sha(SOURCE / name) == overlays.get(name, digest), name
    for name, digest in overlays.items():
        assert sha(SOURCE / name) == digest == sha(EVIDENCE / 'overlay' / name), name
    before, after = config(OLD / 'sdkconfig'), config(ART / 'sdkconfig')
    changes = {k: [before.get(k), after.get(k)] for k in before.keys() | after.keys()
               if before.get(k) != after.get(k)}
    assert changes == {'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK': [None, 'y']}, changes
    assert after['CONFIG_ESPTOOLPY_FLASHMODE_QIO'] == 'y'
    assert after['CONFIG_ESPTOOLPY_FLASHFREQ_80M'] == 'y'
    for disabled in ('YORADIO_DEEP_SLEEP_CLOCK', 'YORADIO_PDM_INTEGER_FIR',
                     'YORADIO_PDM_INTEGER_RATE_COMPENSATION', 'YORADIO_PDM_CLOCK_DIAGNOSTICS'):
        assert after.get('CONFIG_' + disabled) != 'y', disabled
    image = image_info((ART / 'app.bin').read_bytes())
    assert image['bytes'] <= 1900544
    elf_path = BUILD / 'yoradio_esp32c3_oled_native.elf'
    assert image['app_elf_sha256'] == sha(elf_path)
    decoded = (ART / 'app.bin').read_bytes()[48:80].split(b'\0')[0].decode()
    assert decoded == 'idf61-listen48-8c1f2d', decoded
    sdk_driver = Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_driver_i2s/i2s_pdm.c')
    assert (BUILD / 'yoradio_i2s/i2s_pdm.c').read_bytes() == patch(sdk_driver.read_bytes())
    commands = json.loads((BUILD / 'compile_commands.json').read_text())
    driver_commands = [c for c in commands if c['file'].replace('\\', '/').endswith('/i2s_pdm.c')]
    assert len(driver_commands) == 1 and 'yoradio_i2s' in driver_commands[0]['file']
    assert not any('flac_clz' in c['file'] or 'boot_probe.c' in c['file'] for c in commands)
    candidate_objects, baseline_objects = objects(BUILD), objects(BASE_BUILD)
    assert len(candidate_objects) >= 19
    assert candidate_objects == baseline_objects, 'AAC/FLAC/PCM executable sections changed'
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        sections = {s.name: s['sh_size'] for s in elf.iter_sections()
                    if s.name.startswith(('.iram0.', '.dram0.', '.rtc.'))
                    or s.name in ('.flash.text', '.flash.rodata')}
    with (BASE_BUILD / elf_path.name).open('rb') as stream:
        elf = ELFFile(stream)
        baseline_sections = {s.name: s['sh_size'] for s in elf.iter_sections() if s.name in sections}
    for name in sections:
        if name.startswith(('.iram0.', '.dram0.', '.rtc.')):
            assert sections[name] == baseline_sections[name], name
    result = dict(result='PASS', image=image, config_changes=changes,
                  sections=sections, baseline_sections=baseline_sections,
                  unchanged_code_objects=len(candidate_objects),
                  unchanged_code_sections=sum(len(v) for v in candidate_objects.values()),
                  driver_source_sha256=sha(BUILD / 'yoradio_i2s/i2s_pdm.c'),
                  analog_listening='pending', physical_clock_measurement=False)
    (EVIDENCE / 'build-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    (EVIDENCE / 'code-objects.json').write_text(json.dumps(candidate_objects, indent=2) + '\n')
    manifest = dict(profile='production-config-with-experimental-fractional-clock',
        embedded_project_version=decoded, base_commit=source_manifest['base_commit'],
        idf_git_revision='9a97f6c54ec638111ce55cd36581b3c192f15207', image=image,
        sdkconfig_sha256=sha(ART / 'sdkconfig'), clock_mode='fractional',
        nominal_pcm_hz=48000, expected_flash_mode='qio', flash_mhz=80,
        deep_sleep=False, console_and_logs=False, lab_ca=False,
        fir=False, software_integer_rate_compensation=False,
        hardware_tested=False, production_qualified=False, listening_result='pending',
        rollback_app_sha256=sha(OLD / 'app.bin'),
        build_recipe='tests/results/esp32c3-pdm-listening-20261010/build.ps1',
        report='docs/ESP32C3_PDM_LISTENING_20261010.md')
    (ART / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
