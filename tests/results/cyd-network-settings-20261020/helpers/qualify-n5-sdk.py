"""Check all six linked N5 applications against their saved raw build receipts."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
out = root / 'tests/results/cyd-network-settings-20261020'
sys.path.insert(0, str(root / 'tools'))
from export_cyd_production import image_descriptor, partition_slots
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
expected_switch = {'YORADIO_FLAC_DECODER_CUSTOM': {'previous': False, 'current': True},
                   'YORADIO_FLAC_DECODER_ESPRESSIF': {'previous': True, 'current': False}}
results = []
for selection in ['vendor', 'custom']:
    for backend in ['pdm', 'continuous', 'legacy']:
        suffix = backend if selection == 'vendor' else 'custom-flac-' + backend
        variant = 'esp32-cyd2usb-native-network-settings-' + suffix
        folder = root / 'firmware/development' / variant
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        assert manifest['source_commit'] == head and manifest['source_dirty'] is False
        assert manifest['build_check'] == 'PASS' and manifest['physical_tested'] is False
        assert manifest['target'] == 'esp32' and manifest['backend'] == backend
        assert sha(Path(manifest['compiler'])) == manifest['compiler_sha256']
        for filename, key in [('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256'),
            ('sdkconfig.json', 'sdkconfig_json_sha256'), ('partition-table.bin', 'partition_table_sha256'),
            ('flasher_args.json', 'flasher_args_sha256'), ('project_description.json', 'project_description_sha256')]:
            assert sha(folder / filename) == manifest[key], (variant, filename)
        for entry in manifest['evidence']:
            assert sha(Path(entry['path'])) == entry['sha256'], entry
        for entry in manifest['build_logs']:
            assert sha(folder / entry['file']) == entry['sha256'], entry
        image = (folder / 'app.bin').read_bytes()
        assert len(image) == manifest['app_bytes']
        descriptor = image_descriptor(image)
        assert descriptor['elf_sha256'] == manifest['elf_sha256']
        assert descriptor['version'] == manifest['app_version'] and head[:8] in descriptor['version']
        assert not descriptor['version'].endswith('-dirty')
        assert image[0] == 0xe9 and 1 <= image[1] <= 16 and struct.unpack_from('<H', image, 12)[0] == 0
        position, checksum = 24, 0xef
        for segment in range(image[1]):
            assert position + 8 <= len(image)
            size = struct.unpack_from('<I', image, position + 4)[0]
            position += 8
            assert size > 0 and position + size <= len(image)
            if segment == 0:
                assert size >= 256 and struct.unpack_from('<I', image, position)[0] == 0xabcd5432
            for value in image[position:position + size]:
                checksum ^= value
            position += size
        at = ((position + 16) // 16) * 16 - 1
        assert at < len(image) and image[at] == checksum and image[23] == 1
        assert len(image) == at + 1 + 32 and hashlib.sha256(image[:at + 1]).digest() == image[at + 1:]
        slots = partition_slots((folder / 'partition-table.bin').read_bytes(), 4 * 1024 * 1024)
        limit = min(slot['bytes'] for slot in slots)
        assert limit == 0x1b0000 and len(image) <= limit
        config = json.loads((folder / 'sdkconfig.json').read_text(encoding='utf-8'))
        previous = json.loads((root / 'firmware/development' /
                               ('esp32-cyd2usb-native-network-power-' + backend) / 'sdkconfig.json').read_text(encoding='utf-8'))
        changes = {key: {'previous': previous.get(key), 'current': config.get(key)}
                   for key in sorted(set(previous) | set(config)) if previous.get(key) != config.get(key)}
        assert changes == (expected_switch if selection == 'custom' else {}), (variant, changes)
        build = Path(manifest['build_directory'])
        if not build.is_absolute():
            build = root / build
        description = json.loads((build / 'project_description.json').read_text(encoding='utf-8'))
        assert sha(build / 'config/sdkconfig.json') == manifest['sdkconfig_json_sha256']
        elf = build / description['app_elf']
        data = elf.read_bytes()
        assert data[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', data, 18)[0] == 94
        assert sha(elf) == manifest['elf_sha256']
        nm = Path(description['c_compiler']).with_name('xtensa-esp32-elf-nm.exe')
        command = [str(nm), '--defined-only', str(elf)]
        raw = subprocess.check_output(command)
        symbols_file = out / ('sdk-symbols-' + suffix + '.log')
        symbols_file.write_bytes(raw)
        names = {line.split()[-1] for line in raw.decode().splitlines() if line.split()}
        assert ('custom_flac_decoder_feed' in names) == (selection == 'custom')
        assert ('esp_flac_dec_register' in names) == (selection == 'vendor')
        warnings = [line for entry in manifest['build_logs']
                    for line in (folder / entry['file']).read_text(encoding='utf-8', errors='replace').splitlines()
                    if re.search(r'\bwarning:', line)]
        # The vendor legacy build can reuse the unchanged deprecated driver
        # object. The new custom legacy directory compiles it from scratch.
        expected_counts = {0, 3} if backend == 'legacy' else {0}
        assert len(warnings) in expected_counts, (variant, warnings)
        assert all(re.search(r"periph_rtc_apll_(?:freq_set|acquire|release)' is deprecated", warning)
                   and '/v5.5.4/components/driver/deprecated/i2s_legacy.c:' in warning
                   for warning in warnings), warnings
        if selection == 'custom' and backend == 'legacy':
            assert len(warnings) == 3
        results.append(dict(variant=variant, backend=backend, flac_selection=selection,
            app_bytes=len(image), ota_slot_bytes=limit, ota_free_bytes=limit-len(image),
            app_sha256=manifest['app_sha256'], elf_sha256=manifest['elf_sha256'],
            manifest_sha256=sha(folder / 'manifest.json'), config_changes=changes,
            warnings=warnings, symbol_command=command, symbols_sha256=sha(symbols_file)))

def task_calls(text):
    calls = []
    for match in re.finditer(r'\bxTaskCreatePinnedToCore\s*\(', text):
        depth, quote, escaped = 0, None, False
        for index in range(match.end() - 1, len(text)):
            character = text[index]
            if quote:
                if escaped:
                    escaped = False
                elif character == '\\':
                    escaped = True
                elif character == quote:
                    quote = None
            elif character in {'"', "'"}:
                quote = character
            elif character == '(':
                depth += 1
            elif character == ')':
                depth -= 1
                if not depth:
                    calls.append(text[match.start():index + 1])
                    break
        else:
            raise AssertionError('Unterminated task call')
    return calls

bindings = {}
for name, expected_count in [('audio_service.c', 1), ('app_main.c', 2), ('network_runtime.c', 1)]:
    relative = 'idf/esp32-cyd2usb-native/main/' + name
    previous = subprocess.check_output(['git', 'show', 'c64fc8b42:' + relative], cwd=root).decode()
    current = (root / relative).read_text(encoding='utf-8')
    before, after = task_calls(previous), task_calls(current)
    assert len(before) == expected_count and before == after, relative
    bindings[relative] = dict(source_sha256=sha(root / relative), unchanged_task_calls=after)
    if name == 'audio_service.c':
        # Three owners use one gated-task creation call in a three-row loop.
        # Compare the complete unchanged source, including its loop and table.
        assert previous.replace('\r\n', '\n') == current
        table = re.search(r'static const pipeline_task_t task_config\[3\] = \{(.*?)\n    \};', current, re.S)
        assert table
        for row in [
            '{stream_task, "radio_stream", BOARD_TASK_STACK_RADIO_STREAM, 3, 0}',
            '{decoder_task, "audio_decode", BOARD_TASK_STACK_AUDIO_DECODER, 5, 1}',
            '{output_task, "audio_output", BOARD_TASK_STACK_AUDIO_OUTPUT, 6, 1}']:
            assert row in table.group(1)
        bindings[relative]['unchanged_three_owner_table'] = table.group(1)
relative = 'idf/esp32-cyd2usb-native/main/board_config.h'
assert subprocess.check_output(['git', 'show', 'c64fc8b42:' + relative], cwd=root).replace(b'\r\n', b'\n') == (root / relative).read_bytes().replace(b'\r\n', b'\n')
(out / 'SDK.json').write_text(json.dumps(dict(passed=True, source_commit=head, physical_tested=False,
    images=results, unchanged_task_bindings=bindings, board_config_sha256=sha(root / relative),
    scope='Six complete actual GCC Xtensa application links/exports; raw receipts, target/image checksums, OTA bounds, configuration and actual selected FLAC ELF symbols. No flash, target execution, RF, stack/HWM or performance claim.'), indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'source_commit': head, 'images': [
    {key: item[key] for key in ['variant', 'app_bytes', 'ota_free_bytes']} for item in results]}, indent=2))
