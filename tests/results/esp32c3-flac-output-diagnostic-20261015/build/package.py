"""Export and audit this production build before deployment."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

sys.path.insert(0, 'tools/esp32c3_tests')
from ota import image_info

BUILD = Path('idf/esp32c3-oled-native/build-flac-output-diagnostic-20261015')
ART = Path('firmware/development/esp32c3-idf61-flac-output-diagnostic')
OUT = Path('.build/c3-flac-output-diagnostic-20261015')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = dict(re.findall(r'^(CONFIG_\w+)=(.+)$', (BUILD/'sdkconfig').read_text(), re.M))
enabled = ('YORADIO_PIPELINE_HEALTH_DIAGNOSTIC', 'YORADIO_INPUT_TAIL_COALESCE', 'MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL', 'YORADIO_FRAME_ROUTER', 'YORADIO_STREAM_CONFIRM', 'YORADIO_AAC_COMPACT_EARLY_OWNER', 'ESPTOOLPY_FLASHMODE_QIO', 'ESPTOOLPY_FLASHFREQ_80M',
    'ESP_CONSOLE_NONE', 'YORADIO_PDM_FRACTIONAL_CLOCK', 'YORADIO_OUTPUT_TASK_FIRST',
    'YORADIO_AAC_PLUS', 'YORADIO_AAC_LATE_SBR', 'YORADIO_AAC_COMPACT_SBR',
    'YORADIO_AAC_HIGH_HISTORY_PC19', 'YORADIO_AAC_SMOOTHING_HISTORY',
    'YORADIO_AAC_LOW_WORKSPACE', 'YORADIO_AAC_ASYMMETRIC_OWNER',
    'YORADIO_TLS_RX_ONLY_RESERVE', 'YORADIO_TLS_EARLY_MPI_LOCK',
    'YORADIO_ADAPTIVE_INPUT_BUFFER', 'YORADIO_HTTP_RELEASE_REQUEST_BUFFER',
    'YORADIO_TCP_PCB_POOL', 'YORADIO_VORBIS_REPAIR')
disabled = ('YORADIO_DEEP_SLEEP_CLOCK', 'YORADIO_QEMU', 'YORADIO_AAC_EARLY_SBR_RESERVE',
    'YORADIO_SHARED_DECODER_ARENA', 'YORADIO_DIRECT_DMA_PCM',
    'YORADIO_PIPELINE_PROFILE',
    'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')
for key in enabled:
    assert config.get('CONFIG_'+key) == 'y', key
for key in disabled:
    assert config.get('CONFIG_'+key) != 'y', key
assert config['CONFIG_LOG_MAXIMUM_LEVEL'] == '0'
assert config['CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS'] == '0'
assert config['CONFIG_YORADIO_INPUT_PREFILL_MS'] == '1000'
for key, value in config.items():
    if re.search(r'WIFI.*(?:SSID|PASSWORD)|PASSWORD|SECRET', key):
        assert value in ('""', 'n', '0'), key
elfpath = BUILD/'yoradio_esp32c3_oled_native.elf'
with elfpath.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {s.name: s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert symbols['s_tls_large_storage']['st_size'] == 17058
    assert symbols['s_audio_pipeline_probe']['st_size'] == 540
    assert 'adaptive_input_reopen_tail' in symbols
    sections = {s.name: s['sh_size'] for s in elf.iter_sections()
        if s.name.startswith(('.iram0.', '.dram0.', '.rtc.')) or s.name in ('.flash.text', '.flash.rodata')}
objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
rx = list(BUILD.rglob('esp_mbedtls_dynamic_impl.c.obj'))
assert len(rx) == 1
for tool, args, name in (
    ('tools/codec_benchmark/verify_aac_network_build.py', ['--build', str(BUILD)], 'aac'),
    ('tools/esp32c3_tests/verify_http_link.py', ['--sdkconfig', str(BUILD/'sdkconfig'), '--elf', str(elfpath)], 'http'),
    ('tools/esp32c3_tests/verify_adaptive_input_link.py', ['--sdkconfig', str(BUILD/'sdkconfig'), '--elf', str(elfpath), '--tls-rx-object', str(rx[0])], 'allocator')):
    with (OUT/(name+'-audit.log')).open('wb') as log:
        subprocess.run([sys.executable, '-B', '-X', 'utf8', tool, *args, '--objdump', objdump,
            '--output', str(OUT/(name+'-audit.json'))], stdout=log, stderr=subprocess.STDOUT, check=True)
for source, dest in (('sdkconfig', 'sdkconfig'), ('bootloader/bootloader.bin', 'bootloader.bin'),
                     ('partition_table/partition-table.bin', 'partition-table.bin')):
    shutil.copyfile(BUILD/source, ART/dest)
image = image_info((ART/'app.bin').read_bytes())
assert image['app_elf_sha256'] == sha(elfpath)
assert image['bytes'] <= 1900544
manifest = dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    embedded_version='idf61-flacdiag-20261015', image=image,
    idf_revision=Path('idf/esp32c3-oled-native/idf-revision.txt').read_text().strip(),
    profile='TestedRadioProfile + FRAME_ROUTER + STREAM_CONFIRM + AAC_COMPACT_EARLY_OWNER + INPUT_TAIL_COALESCE', production_profile=False, pipeline_health_diagnostic=True,
    production_qualified=False, hardware_tested=False, deep_sleep=False, flash_mode='qio', flash_mhz=80,
    nominal_pcm_output_hz=48000, tls_rx_reserve_bytes=17058,
    input_prefill_ms=1000, laboratory_ca=False, console_and_logs=False,
    experimental_frame_router=True, experimental_early_sbr_owner=True, continuous_confirmation=True, input_tail_coalesce=True, aac_input_extra_slots=0,
    files={p.name: sha(p) for p in ART.iterdir() if p.is_file() and p.name!='manifest.json'}, sections=sections,
    qualification='Build/link audits passed; physical deployment pending. Full qualification remains open.')
(ART/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
(OUT/'build-audit.json').write_text(json.dumps(dict(result='PASS', image=image, sections=sections), indent=2)+'\n')
print(json.dumps(dict(result='PASS', image=image, sections=sections)))
