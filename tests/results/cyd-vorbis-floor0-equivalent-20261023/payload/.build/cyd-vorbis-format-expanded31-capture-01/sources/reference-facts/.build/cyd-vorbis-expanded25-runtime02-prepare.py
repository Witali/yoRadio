"""Create an independent successor for the failed25 test materialization."""
from pathlib import Path
import difflib
import hashlib
import importlib.util
import json
import shutil

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / '.build/cyd-vorbis-format-expanded25-prep-01'
NEW = ROOT / '.build/cyd-vorbis-format-expanded25-prep-02'
assert not NEW.exists()
NEW.mkdir()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


for name in ('contract.json', 'source-map.json', 'reference-binding02.json',
             'reference_binding02.py', 'protocol.py', 'windows_compile_command.py'):
    (NEW / name).write_bytes((OLD / name).read_bytes())
shutil.copytree(OLD / 'target', NEW / 'target')
(NEW / 'README.md').write_text('''# Expanded25 test materialization revision02

The first SDK capture failed compilation before QEMU: its data header contained
25 descriptors but still declared CORPUS_CASE_COUNT17 and expected PCM398080.
Its restricted reader mirrored those old constants. Every original source and
failed capture remains unchanged. The decoder candidate itself is unchanged.

Render and recovery now derive both macros from the exact model, and recovery
independently requires declared C capacity == actual descriptor count == model
and raw case counts. Two exact corruptions restore only the old count or PCM
macro. All125 arrays/75 full raw payloads and all descriptor fields remain exact.
The same25 contract/source mapping and existing17+8 reference bindings apply.
Only this successor's data hash and controller data pin change; SDK gates,
caller, protocol and references are unchanged. No target qualification is
claimed by materialization. The known floor0 numerical NONPASS stays open.
''', encoding='utf-8')
old_materializer = (OLD / 'materialize.py').read_text(encoding='utf-8')
materializer = replace_once(old_materializer, '"#define CORPUS_CASE_COUNT 17U\\n"',
    'f"#define CORPUS_CASE_COUNT {len(contract[\'model\'][\'cases\'])}U\\n"')
materializer = replace_once(materializer, '"#define CORPUS_EXPECTED_PCM_BYTES 398080U\\n\\n"',
    'f"#define CORPUS_EXPECTED_PCM_BYTES {contract[\'model\'][\'total_pcm\']}U\\n\\n"')
materializer = replace_once(materializer,
    '(("CORPUS_CASE_COUNT", "17U"), ("CORPUS_EXPECTED_PCM_BYTES", "398080U"),',
    '(("CORPUS_CASE_COUNT", f"{len(contract[\'model\'][\'cases\'])}U"),\n'
    '                           ("CORPUS_EXPECTED_PCM_BYTES", f"{contract[\'model\'][\'total_pcm\']}U"),')
materializer = replace_once(materializer, '    need(len(blocks) == 25, "all_25_descriptors")',
    '    need(len(blocks) == 25, "all_25_descriptors")\n'
    '    declared_count = int(re.findall(r"^#define CORPUS_CASE_COUNT ([0-9]+)U$", text, re.M)[0])\n'
    '    need(declared_count == len(blocks) == len(items) == len(contract["model"]["cases"]),\n'
    '         "declared_capacity_descriptor_model_raw_count")')
materializer = replace_once(materializer, '        controls = [',
    '        controls = [\n'
    '            ("declared_case_count17", text.replace("#define CORPUS_CASE_COUNT 25U", "#define CORPUS_CASE_COUNT 17U", 1), "identity_macro:CORPUS_CASE_COUNT"),\n'
    '            ("declared_pcm_total17", text.replace("#define CORPUS_EXPECTED_PCM_BYTES 623360U", "#define CORPUS_EXPECTED_PCM_BYTES 398080U", 1), "identity_macro:CORPUS_EXPECTED_PCM_BYTES"),')
(NEW / 'materialize.py').write_text(materializer, encoding='utf-8', newline='\n')
(NEW / 'materializer-revision02.diff').write_text(''.join(difflib.unified_diff(
    old_materializer.splitlines(keepends=True), materializer.splitlines(keepends=True),
    fromfile='expanded25-prep01/materialize.py', tofile='expanded25-prep02/materialize.py')), encoding='utf-8')
spec = importlib.util.spec_from_file_location('reviewed_materializer02', NEW / 'materialize.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.materialize(NEW / 'contract.json', NEW / 'materialized01')
old_data = (OLD / 'materialized01/data.h').read_bytes()
new_data = (NEW / 'materialized01/data.h').read_bytes()
expected_data = old_data.replace(b'#define CORPUS_CASE_COUNT 17U', b'#define CORPUS_CASE_COUNT 25U', 1)
expected_data = expected_data.replace(b'#define CORPUS_EXPECTED_PCM_BYTES 398080U', b'#define CORPUS_EXPECTED_PCM_BYTES 623360U', 1)
assert new_data == expected_data
contract, items = module.load(NEW / 'contract.json')
assert len(module.recover(new_data.decode('ascii'), contract, items)) == 25
try:
    module.recover(old_data.decode('ascii'), contract, items)
except RuntimeError as error:
    assert str(error) == 'identity_macro:CORPUS_CASE_COUNT'
else:
    raise AssertionError('Previously bad header must be rejected')
old_controller = (OLD / 'run-cyd-vorbis-format-expanded25-qemu02.py').read_bytes()
assert digest(old_controller) == '3a475dd5ac3719b40c54fde068e3079da9ef479571b6a839e1c3b8b19bbfedd7'
controller = old_controller.replace(b'4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757', digest(new_data).encode())
assert old_controller.count(b'4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757') == 1
(NEW / 'run-cyd-vorbis-format-expanded25-qemu02.py').write_bytes(controller)
(NEW / 'controller-revision02.diff').write_text(''.join(difflib.unified_diff(
    old_controller.decode().splitlines(keepends=True), controller.decode().splitlines(keepends=True),
    fromfile='expanded25-prep01/controller02.py', tofile='expanded25-prep02/controller02.py')), encoding='utf-8')
facts = dict(schema='root-expanded25-corrected-materialization-v1',
    old_data_sha256=digest(old_data), data_sha256=digest(new_data),
    old_controller_sha256=digest(old_controller), controller_sha256=digest(controller),
    contract_sha256=digest((NEW / 'contract.json').read_bytes()), decoder_source_unchanged=True,
    only_two_data_macros_changed=True, old_header_rejected=True,
    all_raw_arrays=75, all_arrays=125, cases=25, packets=350, expected_pcm_bytes=623360,
    target_executed=False, numeric_qualified=False)
(NEW / 'source-relation.json').write_text(json.dumps(facts, indent=2) + '\n', encoding='utf-8')
inventory = {path.relative_to(NEW).as_posix(): dict(bytes=len(path.read_bytes()), sha256=digest(path.read_bytes()))
             for path in sorted(NEW.rglob('*')) if path.is_file()}
(NEW / 'readiness.json').write_text(json.dumps(dict(schema='root-expanded25-runtime02-readiness-v1', files=inventory), indent=2) + '\n', encoding='utf-8')
print(json.dumps(facts))
