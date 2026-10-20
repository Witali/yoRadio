"""Read seven completed exports; never build, run a qualifier or operate a device."""
from pathlib import Path
import hashlib
import json
import os
import re
import struct
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SDK = Path('C:/Work/yoRadio/.idf/v6.0.2')
os.environ['GIT_OPTIONAL_LOCKS'] = '0'
count = int(os.environ.get('GIT_CONFIG_COUNT', '0'))
os.environ['GIT_CONFIG_KEY_'+str(count)] = 'core.longpaths'
os.environ['GIT_CONFIG_VALUE_'+str(count)] = 'true'
os.environ['GIT_CONFIG_COUNT'] = str(count+1)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.longpaths=true', *args], cwd=ROOT)
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

assert not (OUT/'review.json').exists()
inputs = {}
def freeze(path, retain=True):
    path = Path(path).resolve()
    key = str(path)
    if key in inputs:
        return path.read_bytes()
    raw = path.read_bytes()
    row = {'source': key, 'bytes': len(raw), 'sha256': sha(raw), 'retained': retain}
    if retain:
        if path.is_relative_to(ROOT):
            label = 'repository/'+path.relative_to(ROOT).as_posix()
        else:
            assert path.is_relative_to(SDK), path
            label = 'sdk/'+path.relative_to(SDK).as_posix()
        target = OUT/'frozen_inputs'/label
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['snapshot'] = target.relative_to(OUT).as_posix()
    inputs[key] = row
    return raw
def load(path):
    return json.loads(freeze(path))
def frozen_module(path, name):
    raw = freeze(path)
    namespace = {'__file__': str(path), '__name__': name}
    exec(compile(raw, str(path), 'exec'), namespace)
    return namespace

marker_path = ROOT/'.build/input-reclaim-production-source.json'
marker = load(marker_path)
profiles_path = ROOT/'.build/input-reclaim-production-profiles.json'
profiles = load(profiles_path)
report_path = ROOT/'tests/results/cyd-input-reclaim-20261020/SDK.json'
qualification = load(report_path)
prior_review = load(ROOT/'.build/cyd-input-reclaim-sdk-review-02/review.json')
contract = frozen_module(ROOT/'.build/input_reclaim_sdk_contract.py', 'frozen_contract')
exporter = frozen_module(ROOT/'tools/export_cyd_production.py', 'frozen_exporter')
# Only the exported READ-ONLY snapshot function is called. No build/export/
# qualification entrypoint, toolchain, nm, SDK program or device is executed.
source_before = exporter['source_snapshot'](ROOT)
contract['source'](source_before, marker)
contract['profiles'](ROOT, profiles)
assert qualification['passed'] is True and qualification['physical_tested'] is False
assert qualification['source_commit'] == marker['source_commit']
assert qualification['source_content_sha256'] == marker['source_content_sha256']
assert qualification['source_marker_sha256'] == sha(freeze(marker_path))
assert qualification['profiles_sha256'] == marker['profiles_sha256'] == sha(freeze(profiles_path))
assert qualification['qualifier_tools_sha256'] == marker['qualifier_tools_sha256']
for name, digest in marker['qualifier_tools_sha256'].items():
    assert sha(freeze(ROOT/name)) == digest
    assert prior_review['reviewed_entrypoint_sha256'][Path(name).name] == digest
assert len(qualification['images']) == 7
qualified = {row['variant']: row for row in qualification['images']}
assert len(qualified) == 7 and set(qualified) == {row['variant'] for row in profiles}

def cstring(raw):
    return raw.split(b'\0', 1)[0].decode('utf-8')
def elf_symbols(raw):
    assert raw[:7] == b'\x7fELF\x01\x01\x01'
    assert struct.unpack_from('<H', raw, 18)[0] == 94
    shoff = struct.unpack_from('<I', raw, 32)[0]
    shsize, shcount = struct.unpack_from('<HH', raw, 46)
    assert shsize == 40 and shoff+shsize*shcount <= len(raw)
    sections = [struct.unpack_from('<10I', raw, shoff+i*shsize) for i in range(shcount)]
    symbols = {}
    for sec in sections:
        if sec[1] != 2:
            continue
        names = sections[sec[6]]
        strings = raw[names[4]:names[4]+names[5]]
        assert sec[9] == 16 and sec[4]+sec[5] <= len(raw)
        for pos in range(sec[4], sec[4]+sec[5], sec[9]):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', raw, pos)
            if name and index:
                text = cstring(strings[name:])
                symbols.setdefault(text, []).append({'address': value, 'bytes': size, 'info': info, 'section': index})
    def one(name):
        values = symbols[name]
        assert len(values) == 1, (name, values)
        return values[0]
    phoff = struct.unpack_from('<I', raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', raw, 42)
    assert phsize == 32 and phoff+phsize*phcount <= len(raw)
    segments = [struct.unpack_from('<8I', raw, phoff+i*phsize) for i in range(phcount)]
    def word(address):
        matching = [p for p in segments if p[0] == 1 and p[2] <= address and address+4 <= p[2]+p[4]]
        assert len(matching) == 1
        p = matching[0]
        return struct.unpack_from('<I', raw, p[1]+address-p[2])[0]
    return symbols, one, word

def image_check(raw, elf_sha, expected_version):
    assert len(raw) >= 288 and raw[0] == 0xe9 and 1 <= raw[1] <= 16
    assert struct.unpack_from('<H', raw, 12)[0] == 0
    assert struct.unpack_from('<I', raw, 32)[0] == 0xabcd5432
    assert raw[176:208].hex() == elf_sha
    assert cstring(raw[48:80]) == expected_version and not expected_version.endswith('-dirty')
    assert cstring(raw[80:112]) == 'yoradio_cyd2usb_native'
    assert cstring(raw[144:176]) == 'v6.0.2'
    pos, checksum = 24, 0xef
    for i in range(raw[1]):
        assert pos+8 <= len(raw)
        size = struct.unpack_from('<I', raw, pos+4)[0]
        pos += 8
        assert size > 0 and pos+size <= len(raw)
        for value in raw[pos:pos+size]:
            checksum ^= value
        pos += size
    checksum_offset = ((pos+1+15)//16)*16-1
    assert raw[checksum_offset] == checksum and raw[23] == 1
    assert len(raw) == checksum_offset+33
    assert hashlib.sha256(raw[:checksum_offset+1]).digest() == raw[checksum_offset+1:]
    return {'segments': raw[1], 'checksum_offset': checksum_offset, 'elf_descriptor_hash_matches': True}

checks = []
for profile in profiles:
    folder = ROOT/'firmware/development'/profile['variant']
    q = qualified[profile['variant']]
    receipt = load(folder/'manifest.json')
    expected_evidence = marker['expected_evidence'][profile['name']]
    assert contract['evidence'](ROOT, profile) == expected_evidence
    contract['receipt'](receipt, profile, marker, expected_evidence)
    assert receipt['target'] == 'esp32' and receipt['idf_version'] == 'v6.0.2'
    assert receipt['build_check'] == 'PASS' and receipt['physical_tested'] is False
    assert receipt['flash_bytes'] == 0x400000
    assert q['manifest_sha256'] == sha(freeze(folder/'manifest.json'))
    for name, key in [('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256'),
                      ('sdkconfig.json', 'sdkconfig_json_sha256'), ('partition-table.bin', 'partition_table_sha256'),
                      ('flasher_args.json', 'flasher_args_sha256'), ('project_description.json', 'project_description_sha256')]:
        assert sha(freeze(folder/name)) == receipt[key]
    for row in receipt['build_logs']:
        assert sha(freeze(folder/row['file'])) == row['sha256']
        assert freeze(row['original_path']) == freeze(folder/row['file'])
    for path, digest in expected_evidence.items():
        assert sha(freeze(path)) == digest
    assert sha(freeze(receipt['compiler'], retain=False)) == receipt['compiler_sha256']
    for row in receipt['sdkconfig_seed']['defaults']:
        assert sha(freeze(row['path'])) == row['sha256']
    baseline = Path(profile['baseline'])
    for name in ('manifest.json', 'sdkconfig', 'sdkconfig.json'):
        freeze(baseline/name)
    previous = contract['baseline'](ROOT, profile, git)
    baseline_receipt = load(baseline/'manifest.json')
    config = load(folder/'sdkconfig.json')
    changes = {key: {'previous': previous.get(key), 'current': config.get(key)}
               for key in sorted(set(previous)|set(config)) if previous.get(key) != config.get(key)}
    assert changes == q['config_changes'] == {'YORADIO_TLS_INPUT_RECLAIM': {'previous': None, 'current': profile['enabled']}}
    assert not config['FREERTOS_UNICORE'] and config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240
    assert config['ESPTOOLPY_FLASHSIZE_4MB'] and not config['YORADIO_NATIVE_DIAGNOSTICS']
    assert config['YORADIO_ADAPTIVE_INPUT_BUFFER'] and config['ESP_TLS_USING_MBEDTLS'] and config['MBEDTLS_INTERNAL_MEM_ALLOC']
    assert not config['MBEDTLS_CUSTOM_MEM_ALLOC'] and not config['HEAP_ABORT_WHEN_ALLOCATION_FAILS']
    assert receipt['partition_table_sha256'] == baseline_receipt['partition_table_sha256']
    assert receipt['ota_slots'] == baseline_receipt['ota_slots'] == [
        {'name': 'app0', 'offset': 0x10000, 'bytes': 0x1b0000},
        {'name': 'app1', 'offset': 0x1c0000, 'bytes': 0x1b0000}]
    # Raw prepared seed is retained in the independent prebuild review, whereas
    # generated current sdkconfig may legitimately have been normalized by IDF.
    old_inputs = json.loads((ROOT/'.build/cyd-input-reclaim-sdk-review-02/inputs.json').read_bytes())
    seed_row = next(x for x in old_inputs['inputs'] if Path(x['source']).resolve() == Path(profile['sdkconfig']).resolve())
    seed_path = ROOT/'.build/cyd-input-reclaim-sdk-review-02'/seed_row['snapshot']
    assert sha(freeze(seed_path)) == profile['prepared_sdkconfig_sha256'] == receipt['sdkconfig_seed']['source_sha256']
    build = Path(receipt['build_directory'])
    description = load(build/'project_description.json')
    assert freeze(build/'project_description.json') == freeze(folder/'project_description.json')
    elf_path = build/description['app_elf']
    raw = freeze(elf_path)
    assert sha(raw) == receipt['elf_sha256'] == q['elf_sha256']
    symbols, one, word = elf_symbols(raw)
    assert ('__wrap_esp_mbedtls_mem_calloc' in symbols) == profile['enabled']
    assert ('native_input_reclaim_bind' in symbols) == profile['enabled']
    assert '__wrap_esp_mbedtls_mem_free' not in symbols
    assert not any(name.startswith('tls_large_reserve_') for name in symbols)
    assert ('custom_flac_decoder_feed' in symbols) == profile['custom_flac']
    assert ('esp_flac_dec_register' in symbols) == (not profile['custom_flac'])
    for name in ('yoradio_http_client_release_request_buffer', 'native_output_metrics_snapshot', 'native_output_metrics_end_write'):
        one(name)
    pointers = {}
    for name, expected in [('mbedtls_calloc_func', '__wrap_esp_mbedtls_mem_calloc' if profile['enabled'] else 'esp_mbedtls_mem_calloc'),
                           ('mbedtls_free_func', 'esp_mbedtls_mem_free')]:
        symbol = one(name)
        assert symbol['bytes'] == 4
        value = word(symbol['address'])
        assert value == one(expected)['address']
        proof = {'address': symbol['address'], 'initial_value': value, 'expected_symbol': expected}
        assert proof == q['sdk_allocator_pointer_proof'][name]
        pointers[name] = proof
    for name, expected in q['integrated_symbols'].items():
        actual = one(name)
        assert actual['address'] == expected['address'] and actual['bytes'] == expected['bytes']
        if name.startswith('s_output_metrics'):
            assert 0x3ff80000 <= actual['address'] and actual['address']+actual['bytes'] <= 0x40000000
        else:
            assert profile['backend'] == 'pdm' and 0x40080000 <= actual['address'] and actual['address']+actual['bytes'] <= 0x400a0000
    app = freeze(folder/'app.bin')
    assert len(app) == receipt['app_bytes'] == q['app_bytes']
    assert sha(app) == q['app_sha256']
    app_proof = image_check(app, receipt['elf_sha256'], receipt['app_version'])
    assert marker['source_commit'][:8] in receipt['app_version']
    assert len(app) <= 0x1b0000 and q['ota_free_bytes'] == 0x1b0000-len(app)
    assert sha(freeze(build/'config/sdkconfig.json')) == receipt['sdkconfig_json_sha256']
    freeze(build/'config/sdkconfig.h')
    freeze(build/'toolchain/cflags')
    assert freeze(build/'sdkconfig') == freeze(folder/'sdkconfig')
    compile_rows = load(build/'compile_commands.json')
    reclaim = [r for r in compile_rows if Path(r['file']).name == 'native_input_reclaim.c']
    assert reclaim == q['reclaim_compile_rows'] and len(reclaim) == int(profile['enabled'])
    if reclaim:
        assert Path(reclaim[0]['file']).resolve() == (ROOT/'idf/esp32-cyd2usb-native/main/native_input_reclaim.c').resolve()
    ninja = freeze(build/'build.ninja').decode()
    for flag in ('--wrap=esp_mbedtls_mem_calloc', '--undefined=__wrap_esp_mbedtls_mem_calloc'):
        assert (flag in ninja) == profile['enabled']
    assert '--wrap=esp_mbedtls_mem_free' not in ninja
    overlay = [r for r in compile_rows if 'native-http-request-buffer' in r['file'] and Path(r['file']).name == 'esp_http_client.c']
    assert len(overlay) == 1 and overlay[0] == q['http_overlay_compile_row']
    assert sha(freeze(overlay[0]['file'])) == q['http_overlay_source_sha256'] == sha(freeze(ROOT/'.build/cyd-http-tx-target-01/esp_http_client.c'))
    nm_path = ROOT/'tests/results/cyd-input-reclaim-20261020'/('sdk-symbols-'+profile['name']+'.log')
    assert sha(freeze(nm_path)) == q['symbols_sha256']
    nm_symbols = {}
    for line in freeze(nm_path).decode().splitlines():
        fields = line.split()
        if len(fields) == 4:
            nm_symbols[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    for name in list(q['integrated_symbols'])+['mbedtls_calloc_func', 'mbedtls_free_func', 'esp_mbedtls_mem_calloc', 'esp_mbedtls_mem_free']:
        actual = one(name)
        assert nm_symbols[name] == (actual['address'], actual['bytes'])
    checks.append({'name': profile['name'], 'enabled': profile['enabled'], 'backend': profile['backend'],
        'custom_flac': profile['custom_flac'], 'app_bytes': len(app), 'ota_free_bytes': 0x1b0000-len(app),
        'app_sha256': sha(app), 'elf_sha256': sha(raw), 'manifest_sha256': sha(freeze(folder/'manifest.json')),
        'only_config_delta': changes, 'raw_elf_symbol_and_initializer_proof': pointers,
        'independent_image_checks': app_proof, 'baseline_partition_table_byte_hash_equal': True,
        'receipt_source_seed_evidence_artifact_and_log_hashes_current': True,
        'canonical_compile_and_link_flags': True, 'symbol_log_cross_checked_against_actual_elf': True})

freeze(ROOT/'.build/cyd-input-reclaim-sdk-review-02/inputs.json')
freeze(ROOT/'.build/input-reclaim-production-run.out.log')
freeze(ROOT/'.build/input-reclaim-production-run.err.log')
for name in ('build-production.ps1', 'build.ps1', 'partitions.csv'):
    freeze(ROOT/'idf/esp32-cyd2usb-native'/name)
for name in ('CMakeLists.txt', 'Kconfig.projbuild', 'compat/input_reclaim/enable.cmake',
             'native_input_reclaim.c', 'native_input_reclaim.h', 'native_audio_output.c', 'native_output_metrics.c'):
    freeze(ROOT/'idf/esp32-cyd2usb-native/main'/name)
for relative, proof in qualification['unchanged_task_bindings'].items():
    raw = freeze(ROOT/relative)
    assert sha(raw) == proof['source_sha256']
    current = raw.decode().replace('\r\n', '\n')
    old = git('show', 'edccc3ac:'+relative).decode().replace('\r\n', '\n')
    calls = lambda text: re.findall(r'\bxTaskCreatePinnedToCore\([^;]+;', text, re.S)
    assert calls(current) == calls(old) == proof['unchanged_task_calls'] and calls(current)
    if 'unchanged_three_owner_table' in proof:
        table = lambda text: re.search(r'static const pipeline_task_t task_config\[3\] = \{(.*?)\n    \};', text, re.S).group(1)
        assert table(current) == table(old) == proof['unchanged_three_owner_table']
board = 'idf/esp32-cyd2usb-native/main/board_config.h'
assert sha(freeze(ROOT/board)) == qualification['board_config_sha256']
assert freeze(ROOT/board).replace(b'\r\n', b'\n') == git('show', 'edccc3ac:'+board).replace(b'\r\n', b'\n')
freeze(ROOT/'tests/results/cyd-input-reclaim-20261020/HOST.md')
for relative in ('components/mbedtls/port/esp_mem.c', 'components/mbedtls/port/include/mbedtls/esp_config.h',
                 'components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c'):
    freeze(SDK/relative)
sdk_head = git('-C', str(SDK), 'rev-parse', 'HEAD').decode().strip()
sdk_status = git('-C', str(SDK), 'status', '--porcelain', '--untracked-files=no')
assert sdk_head == qualification['pinned_sdk_commit'] == '7101770dc6db2667b3c477cc31365dd1acd6db4e'
assert not sdk_status.strip()
(OUT/'sdk-tracked-status.log').write_bytes(sdk_status)
source_after = exporter['source_snapshot'](ROOT)
contract['source'](source_after, marker)
assert source_before == source_after
for row in inputs.values():
    row['after_sha256'] = sha(Path(row['source']).read_bytes())
    row['unchanged_after'] = row['sha256'] == row['after_sha256']
assert all(row['unchanged_after'] for row in inputs.values())
write('source-before-after.json', {'before': source_before, 'after': source_after, 'matches_marker': True,
    'note': 'Only excluded artifact/evidence paths can be dirty; complete included-source identity and HEAD remain equal.'})
write('images.json', {'passed': True, 'actual_completed_images': len(checks), 'images': checks})
write('inputs.json', {'inputs': list(inputs.values()), 'all_unchanged_after': True,
    'tool_executions': ['read-only git commands only'], 'tool_binaries_not_copied': True,
    'python': {'path': sys.executable, 'sha256': sha(Path(sys.executable).read_bytes()), 'version': sys.version}})
write('review.json', {'review_complete': True, 'passed': True, 'independent_actual_artifact_review': True,
    'findings': [], 'source_commit': marker['source_commit'], 'source_content_sha256': marker['source_content_sha256'],
    'source_marker_sha256': sha(freeze(marker_path)), 'qualifier_report_sha256': sha(freeze(report_path)),
    'seven_receipts_current': True, 'six_enabled_one_disabled': True,
    'actual_elf_symbol_and_pointer_initializers_independently_verified': True,
    'only_config_delta_new_bool': True, 'baseline_partition_table_identical': True,
    'full_current_included_source_snapshot_matches_before_after': True,
    'all_frozen_inputs_unchanged_after': True, 'input_count': len(inputs),
    'checks': 'images.json', 'inputs': 'inputs.json', 'source_check': 'source-before-after.json',
    'limitations': [
        'Read-only review of seven completed application exports; no SDK build, qualifier rerun, target runtime, nm process or device operation was executed.',
        'The reviewed app/ELF/config/receipt/log bindings establish linked build properties. The embedded calloc initializer selects the wrapper on six enabled images and ordinary SDK calloc on the disabled control; free remains ordinary SDK free in all seven.',
        'No RF, physical allocation failure, DMA, IRQ latency, audio quality, actual board playback or target runtime behavior is established by these exports.',
        'The existing target QEMU evidence is separate and is not requalified by this artifact review.',
        'Parent is preparing additive excluded SDK appendices; this review binds the completed SDK.json, frozen README/HOST and referenced evidence, not unfinalized future appendix text.',
        'Tool executables are hashed without copies; actual ELF/app/config/log inputs used here are retained in the ignored review folder.'
    ]})
files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path != OUT/'manifest.json':
        raw = path.read_bytes()
        files.append({'path': path.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
write('manifest.json', {'files': files})
print(json.dumps({'passed': True, 'findings': 0, 'images': len(checks), 'inputs': len(inputs),
    'files': len(files)+1, 'review_sha256': sha((OUT/'review.json').read_bytes()),
    'manifest_sha256': sha((OUT/'manifest.json').read_bytes())}, indent=2))
