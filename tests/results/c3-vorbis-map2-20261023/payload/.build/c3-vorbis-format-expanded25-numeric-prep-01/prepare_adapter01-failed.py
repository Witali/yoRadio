"""Create a C3 numeric source proposal; never import/execute prepared runtime code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-format-expanded25-numeric-prep-01'
RUNTIME = ROOT / '.build/c3-vorbis-format-expanded25-prep-02'
BASE_SHA = '2fe6ca486c0031101f15c787a84c39c419840b914ae0c829c95bd4095ec37a08'
METRICS_SHA = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
POLICY_SHA = '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'
PINS = {
    'RUNNER': ('run-c3-vorbis-format-expanded25-qemu.py', 'e00a30172c3b4291f080b2eee937214108adda7b6a03178e2f9833cb44d92034'),
    'PROTOCOL': ('protocol.py', '961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba'),
    'CALLER': ('target/c3_vorbis_format_expanded25_qemu/main/main.c', '8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03'),
    'CONTRACT_FILE': ('contract.json', '717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d'),
    'DATA_HEADER': ('materialized01/data.h', '97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc'),
    'CASE_HEADER': ('target/c3_vorbis_format_expanded25_qemu/main/corpus_case.h', '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'),
    'SOURCE_MAP': ('source-map.json', '63f0eccf40044fabcc8d2b31c0a2094859258856e4948fe53a57cf8a9358301a'),
    'BINDING': ('reference-binding02.json', '802d0fe193991cfc40d388ad27594d8d0b632112f223cb6dee68226c07585f2c'),
    'BINDING_HELPER': ('reference_binding02.py', '3961e32fc5abb5a883260b2932a570908367c46ad2058a210a123336db7638ce'),
}

PLATFORM_FUNCTION = '''def c3_platform(inputs, target_root, target):
    need(target.get('platform') == 'esp32c3' and target.get('sdk_revision') == SDK_REVISION and
         type(target.get('elf_machine')) is int and target['elf_machine'] == 243 and
         type(target.get('coordinator_core')) is int and target['coordinator_core'] == 0 and
         type(target.get('worker_core')) is int and target['worker_core'] == 0,
         'Exact C3 SDK/RV32/unicore report facts required')
    for name in ('sdk-head', 'sdk-head-after'):
        row = next(row for row in target['commands'] if row['name'] == name)
        need(inputs.read('target/platform/' + name, target_root / (name + '.stdout.log'),
             row['stdout_sha256']).decode().strip() == SDK_REVISION, 'Actual C3 SDK terminal revision differs')
    setup_sha = target.get('selected_setup_sha256')
    need(isinstance(setup_sha, str) and re.fullmatch('[0-9a-f]{64}', setup_sha),
         'Actual C3 selected setup SHA256 required')
    source_name = 'sources/candidate/vorbis_repair/setup.c'
    source_rows = [row for row in target['inputs'].values() if relative(row['snapshot']) == source_name]
    need(len(source_rows) == 1 and source_rows[0]['sha256'] == setup_sha,
         'Selected C3 setup must bind exactly one frozen candidate source')
    inputs.read('target/platform/candidate-setup', target_root / source_name, setup_sha)
    variant_name = 'variant/vorbis_repair/setup.c'
    need(target.get('variant_sources', {}).get(variant_name) == setup_sha,
         'Actual compiled C3 variant setup differs from selected snapshot')
    inputs.read('target/platform/variant-setup', target_root / variant_name, setup_sha)
    outputs = target.get('build_outputs', {})
    compile_name = 'build/compile_commands.json'
    need(compile_name in outputs, 'Actual C3 compile rows required')
    rows = json.loads(inputs.read('target/platform/compile-commands', target_root / compile_name,
                                 outputs[compile_name]))
    row_source = lambda row: (Path(row['directory']) / row['file']).resolve()
    setup_rows = [row for row in rows if row_source(row) == target_root / variant_name]
    need(len(setup_rows) == 1 and setup_rows[0] == target['setup_macro_context']['row'],
         'Macro proof must describe the actual selected C3 setup compile row')
    command = next(row for row in target['commands'] if row['name'] == 'setup-macros')
    macros = inputs.read('target/platform/setup-macros', target_root / 'setup-macros.stdout.log',
                         command['stdout_sha256']).decode()
    for name, value in (('CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ', 160), ('CONFIG_FREERTOS_UNICORE', 1),
                        ('__riscv_xlen', 32), ('__SIZEOF_LONG__', 4), ('__SIZEOF_POINTER__', 4),
                        ('CONFIG_IDF_TARGET_ESP32C3', 1), ('ESP_PLATFORM', 1)):
        need(re.search(r'^#define ' + name + ' ' + str(value) + '$', macros, re.M),
             'Actual C3 compile macro differs: ' + name)
    need(not re.search(r'^#define LIMIT_TO_64kHz\\b', macros, re.M),
         'Actual C3 setup must retain unrestricted reviewed rate context')
    elf_names = [relative(name) for name in outputs if name.endswith('.elf')]
    need(len(elf_names) == 1 and elf_names[0].startswith('build/'), 'One actual C3 build ELF required')
    elf = inputs.read('target/platform/elf', target_root / elf_names[0], outputs[elf_names[0]])
    need(len(elf) >= 20 and elf[:6] == b'\\x7fELF\\x01\\x01' and
         struct.unpack_from('<H', elf, 18)[0] == 243, 'Actual build must be little-endian ELF32/RISC-V')
    return dict(platform='esp32c3', sdk_revision=SDK_REVISION, elf_machine=243, riscv_bits=32,
                coordinator_core=0, worker_core=0, cpu_mhz=160, unicore=True,
                selected_setup_sha256=setup_sha, setup_snapshot=source_name, compiled_setup=variant_name,
                actual_build_elf=elf_names[0], actual_build_elf_sha256=sha(elf),
                setup_identity_from_actual_report=True, assumed_CYD_binary_equivalence=False)


'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def write(name, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    with (HERE / name).open('xb') as stream:
        stream.write(data)


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def main():
    base = (BASE / 'compare_capture25.py').read_bytes()
    assert sha(base) == BASE_SHA
    original = base.decode('utf-8')
    tree = ast.parse(original)
    text = original
    runtime_facts = {}
    for constant, (name, expected) in PINS.items():
        row = fact(RUNTIME / name)
        assert row['sha256'] == expected, constant
        runtime_facts[constant] = row
        nodes = [node for node in tree.body if isinstance(node, ast.Assign) and
                 any(isinstance(target, ast.Name) and target.id == constant for target in node.targets)]
        assert len(nodes) == 1
        old = ast.literal_eval(nodes[0].value)
        if old != expected:
            text = one(text, constant + ' = ' + repr(old), constant + ' = ' + repr(expected))
    text = one(text, 'import sys\r\n', 'import struct\r\nimport sys\r\n')
    text = one(text, "sys.dont_write_bytecode = True\r\n", "sys.dont_write_bytecode = True\r\nSDK_REVISION = '9a97f6c54ec638111ce55cd36581b3c192f15207'\r\n")
    text = one(text, 'def wav_pcm(data, rate, frames):', PLATFORM_FUNCTION.replace('\n', '\r\n') + 'def wav_pcm(data, rate, frames):')
    anchor = "    inputs.read('target/controller', target_root / 'sources/helpers/run.py', RUNNER)\r\n"
    text = one(text, anchor, "    result['target_platform'] = c3_platform(inputs, target_root, target)\r\n    result['target_platform_verified'] = True\r\n" + anchor)
    text = one(text, "    complete_capture(target)\r\n", "    complete_capture(target)\r\n    need((target.get('platform'), target.get('sdk_revision'), target.get('elf_machine'),\r\n          target.get('coordinator_core'), target.get('worker_core')) ==\r\n         ('esp32c3', SDK_REVISION, 243, 0, 0), 'Only reviewed C3 capture platform supported')\r\n")
    text = one(text, "    result = dict(result='INCOMPLETE',checked_only=True,", "    result = dict(result='INCOMPLETE',target_platform_verified=False,checked_only=True,")
    ast.parse(text)
    write('compare_capture25.py', text)
    copied = {}
    for name, expected in (('pcm_metrics.py', METRICS_SHA), ('policy25.py', POLICY_SHA)):
        data = (BASE / name).read_bytes()
        assert sha(data) == expected
        write(name, data)
        copied[name] = fact(HERE / name)
    write('adapter-adaptation.diff', ''.join(difflib.unified_diff(
        original.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile='cyd-numeric-prep01/compare_capture25.py', tofile='c3-numeric-prep01/compare_capture25.py')))
    relation = dict(schema='c3-expanded25-numeric-source-relation-v1', source_only=True,
        adapter_imported_or_executed=False, metric_or_policy_executed=False,
        actual_PCM_read_or_compared=False, canonical_sources_mutated=False,
        original_adapter=fact(BASE / 'compare_capture25.py'), adapted_adapter=fact(HERE / 'compare_capture25.py'),
        byte_identical_modules=copied, runtime_inputs=runtime_facts,
        unchanged_contract_model_sha256='660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc',
        exact_cases=25, packets=350, expected_pcm_bytes=623360, events=778,
        runtime_pin_changes=['RUNNER', 'PROTOCOL', 'CALLER'],
        additional_source_changes=['struct import', 'SDK_REVISION constant', 'c3_platform verification function',
            'C3 platform gate before PCM access', 'verified C3 platform result facts', 'initial target_platform_verified false'],
        declared_metric_bound=2, optional_bound_default=None, policy_tolerance_not_normative=True,
        root_owns_all_actual_campaigns=True)
    write('source-relation.json', json.dumps(relation, indent=2) + '\n')
    print(json.dumps(dict(source_only=True, adapter=relation['adapted_adapter'], copied_modules=copied)))


if __name__ == '__main__':
    main()
