"""Prepare source pins and exact pure carrier helpers; never qualify PCM."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if (HERE / 'pins.json').exists() or (HERE / 'carrier.py').exists():
        raise RuntimeError('Preserve previous proposal')
    parser = ROOT / '.build/cyd-vorbis-block-host-driver-01.py'
    data = parser.read_bytes()
    if sha(data) != '94af0cf07809bb4026afca47ec28d8b53aa91954965efd2ff07a6630f59d6665':
        raise RuntimeError('Frozen parser changed')
    source = data.decode()
    definitions = {node.name: ast.get_source_segment(source, node) for node in ast.parse(source).body
                   if isinstance(node, ast.FunctionDef)}
    names = ('need', 'crc', 'packets')
    helper = '"""Exact pure helper definitions from the pinned public carrier parser."""\nimport struct\n\n'
    helper += '\n\n'.join(definitions[name] for name in names) + '\n'
    (HERE / 'carrier.py').write_bytes(helper.encode())
    profiles = {}
    for profile, folder, count, status, native, refused, relations in (
        ('mono21', 'cyd-vorbis-mono-mapping-host-01', 21, 0, 21, 0, 0),
        ('map2-eight', 'cyd-vorbis-map2-regression-host-01', 8, 1, 0, 8, 4)):
        campaign = ROOT / '.build' / folder
        report_bytes = (campaign / 'report.json').read_bytes()
        outer_bytes = (ROOT / '.build' / (folder + '-command.json')).read_bytes()
        report = json.loads(report_bytes)
        profiles[profile] = dict(campaign=folder, report_sha256=sha(report_bytes),
            outer_sha256=sha(outer_bytes), outer_returncode=status, case_count=count,
            native_compared=native, native_lookup2_refusals=refused, xiph_relations=relations,
            source_matrices={case['source_matrix']: case['source_matrix_sha256'] for case in report['cases']},
            case_ids=[case['id'] for case in report['cases']])
    pins = dict(schema='public-vorbis-new-format-qualifier-pins-v1', profiles=profiles,
        driver_sha256='65a69cdada2c18f72420e348a76c1d5d19da2b4ce9c260a8df6c0e9804767704',
        parser_sha256=sha(data), capture_sha256='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e',
        tools={'ffmpeg.exe': '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73',
               'python.exe': '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'},
        carrier_source=dict(path=parser.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha(data),
            unchanged_definitions={name: sha(definitions[name].encode()) for name in names},
            proposed_helper_sha256=sha(helper.encode())),
        cross_reference_policy=dict(max_abs_error=2, predeclared=True,
            purpose='bounded-reference-crosscheck-not-standard-conformance'),
        qualifier_executed=False, target_executed=False)
    pins['supporting_source_inputs'] = []
    for rel in ('.build/cyd-vorbis-format-corpus-host-01.py', '.build/cyd-vorbis-format-corpus-host-02.py',
                '.build/cyd-vorbis-format-host-adaptation-02.diff'):
        raw = (ROOT / rel).read_bytes()
        pins['supporting_source_inputs'].append(dict(path=rel, bytes=len(raw), sha256=sha(raw)))
    (HERE / 'pins.json').write_bytes((json.dumps(pins, indent=2) + '\n').encode())
    print(json.dumps(dict(result='SOURCE_PINS_PREPARED', profiles=2, helper_definitions=3, qualifier_executed=False)))


if __name__ == '__main__':
    main()
