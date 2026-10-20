"""Source-only checked adapter projection; never import or run a comparator."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = ROOT / '.build/cyd-vorbis-format-numeric-prep-01'
CORE = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
ADAPTER = '0f99d051e10274d0d30755c61a36e7a8585891212feb040933302cd4deff6305'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    core, original = (BASE / 'pcm_metrics.py').read_bytes(), (BASE / 'compare_capture.py').read_bytes()
    if sha(core) != CORE or sha(original) != ADAPTER or (HERE / 'compare_capture.py').exists():
        raise RuntimeError('Frozen base changed or proposal exists')
    old = original.decode()
    edits = [
        ('Measure complete public PCM capture against Xiph; no codec/process execution.',
         'Measure complete checked-only17 PCM against Xiph; no codec/process execution.'),
        ('c78c5265173ebe2c8801d1f6f37ee8ab14811468b40fd5fbcc99a53f8193ff83',
         '3aa167fe4b231d2c15b91b1b5c78b24da3410d18eaacc0709d6afe0c33ea902d'),
        ('7b9912db4d5317376c22d4ab1f65a206941f84f6773b07cf37a522a3bc7f35f8',
         '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'),
        ("COMMANDS = (", "CONTRACT_FILE = '6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391'\n"
         "DATA_HEADER = 'b4db391fda10e7361f57fe4242574593902042f0e0ef9a48fe24aac144bb153d'\n"
         "CALLER = '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'\nCOMMANDS = ("),
        ("report.get('result') == 'RAW_CORPUS_PCM_CAPTURED'", "report.get('result') == 'CHECKED_CORPUS_PCM_CAPTURED'"),
        ("report.get('target_capture_completed') is True and report.get('vendor_checked_pcm_equal') is True,\n"
         "         'Only a complete original/checked capture is supported; partial/panicking captures are unusable'",
         "report.get('target_capture_completed') is True and report.get('checked_decode_completed') is True and\n"
         "         report.get('vendor_checked_pcm_equal') is False and report.get('vendor_comparison_available') is False,\n"
         "         'Only complete checked-only17 capture is supported; NONPASS/partial captures are unusable'"),
        ("contract_bytes = inputs.read('target/contract', target_root / 'sources/corpus/contract.json', target['corpus']['contract_file_sha256'])",
         "need(target['corpus']['contract_file_sha256'] == CONTRACT_FILE and\n"
         "         target['corpus']['data_header_sha256'] == DATA_HEADER and target['corpus']['cases'] == 17 and\n"
         "         target['corpus']['packets'] == 238 and target['corpus']['expected_pcm'] == 398080, 'Exact reviewed17 corpus/header facts required')\n"
         "    inputs.read('target/caller', target_root / 'sources/project/main/main.c', CALLER)\n"
         "    inputs.read('target/data-header', target_root / 'sources/project/main/data.h', DATA_HEADER)\n"
         "    contract_bytes = inputs.read('target/contract', target_root / 'sources/corpus/contract.json', CONTRACT_FILE)"),
        ("need(contract['contract_sha256'] == CONTRACT and contract['model'] == original_contract['model'],\n"
         "         'Relocation may change paths only, never source/model bytes')",
         "need(contract['contract_sha256'] == CONTRACT and contract['model'] == original_contract['model'] and\n"
         "         len(contract['model']['cases']) == 17 and contract['model']['total_packets'] == 238 and\n"
         "         contract['model']['total_pcm'] == 398080 and contract['model']['case_mask'] == 131071,\n"
         "         'Relocation is path-only; exactly17 cases required, never a partial or25case extension')"),
        ("observed['paired_packets'] == 238 and observed['pcm'] == 398080,",
         "observed['decoded_packets'] == 238 and observed['pcm'] == 398080 and\n"
         "         observed['protocol_lines'] == 530 and observed['checked_decode_completed'] is True and\n"
         "         observed['vendor_checked_pcm_equal'] is False and observed['vendor_comparison_available'] is False,"),
        ("    declared = qualified['xiph_metamorphic_checks']\n",
         "    declared = []\n"
         "    for mi, item in enumerate(relocated):\n"
         "        matrix = json.loads(inputs.read('target/matrix/' + str(mi), item['path'], item['sha256']))\n"
         "        for kind, field in (('equal', 'expected_same_decoder_pcm_equal_groups'), ('different', 'expected_same_decoder_pcm_different_pairs')):\n"
         "            for group in matrix.get(field, []):\n"
         "                declared.append(dict(decoder='libvorbis', kind=kind, cases=group, passed=True))\n"
         "    need(len(declared) == 4 and declared == qualified['xiph_metamorphic_checks'],\n"
         "         'All actual source-declared17 books relations must match the independent qualification')\n"),
        ("result = dict(result='INCOMPLETE', measurement_completed=False, actual_reference_compared=False,",
         "result = dict(result='INCOMPLETE', checked_only=True, vendor_comparison_available=False, vendor_checked_pcm_equal=False,\n"
         "        measurement_completed=False, actual_reference_compared=False,"),
    ]
    new = old
    for before, after in edits:
        if new.count(before) != 1:
            raise RuntimeError('Nonunique adaptation anchor: ' + repr(before))
        new = new.replace(before, after, 1)
    projected = new
    for before, after in reversed(edits):
        if projected.count(after) != 1:
            raise RuntimeError('Ambiguous source projection')
        projected = projected.replace(after, before, 1)
    if projected != old:
        raise RuntimeError('Non-exact projection')
    ast.parse(new)
    for name, data in [('pcm_metrics.py', core), ('compare_capture.py', new.encode())]:
        with (HERE / name).open('xb') as stream:
            stream.write(data)
    (HERE / 'adaptation.diff').write_bytes(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile='paired-numeric01/compare_capture.py', tofile='checked-numeric01/compare_capture.py')).encode())
    (HERE / 'source-relation.json').write_bytes((json.dumps(dict(schema='checked-numeric-adapter-source-projection-v1',
        core_original_path=(BASE / 'pcm_metrics.py').relative_to(ROOT).as_posix(), core_sha256=CORE,
        core_byte_identical=True, adapter_original_sha256=ADAPTER, adapter_proposed_sha256=sha(new.encode()),
        exact_reverse_projection=True, allowed_edits=[dict(before=a, after=b) for a, b in edits],
        actual_comparator_run=False), indent=2) + '\n').encode())
    print(json.dumps(dict(result='CHECKED_ADAPTER_SOURCE_PREPARED', core_byte_identical=True, actual_comparator_run=False)))


if __name__ == '__main__':
    main()
