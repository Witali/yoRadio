"""Source AST/hash and recorded JSON/log metadata closure only; no proposed imports."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'.build/cyd-vorbis-more-singletons-runtime-prep-01'
EXPECTED={'qualify.py','carrier.py','pins.json','README.md','check_source.py','qualifier-adaptation.diff',
    'source-relation.json','source-checks.json','readiness.json','provenance/singletons8-qualify.py',
    'provenance/singletons8-pins.json','provenance/singletons8-carrier.py'}


def sha(data):return hashlib.sha256(data).hexdigest()


def fact(path):
    data=path.read_bytes();return dict(bytes=len(data),sha256=sha(data))


def write_new(name,value):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def main():
    trees={path.relative_to(HERE).as_posix():ast.parse(path.read_bytes().decode(),filename=str(path))
        for path in HERE.rglob('*.py')}
    assert (HERE/'carrier.py').read_bytes()==(BASE/'carrier.py').read_bytes()
    for name in ('qualify.py','pins.json','carrier.py'):
        assert (HERE/'provenance'/('singletons8-'+name)).read_bytes()==(BASE/name).read_bytes()
    before=ast.parse((BASE/'qualify.py').read_bytes().decode())
    for name in ('need','sha','relative','terminal','decoded_pcm'):
        old=next(node for node in before.body if isinstance(node,ast.FunctionDef) and node.name==name)
        new=next(node for node in trees['qualify.py'].body if isinstance(node,ast.FunctionDef) and node.name==name)
        assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
    expected=''.join(difflib.unified_diff((BASE/'qualify.py').read_bytes().decode().splitlines(True),
        (HERE/'qualify.py').read_bytes().decode().splitlines(True),fromfile='singletons8/qualify.py',tofile='zero8/qualify.py'))
    assert (HERE/'qualifier-adaptation.diff').read_bytes()==expected.encode()
    pins=json.loads((HERE/'pins.json').read_bytes());profile=pins['profiles']['zero8']
    assert (profile['case_count'],profile['native_compared'],profile['native_lookup2_refusals'],profile['native_packet_decode_failures'],profile['xiph_relations'])==(8,4,0,4,4)
    assert pins['cross_reference_policy']['max_abs_error']==2
    for row in pins['supporting_source_inputs']:
        assert fact(ROOT/row['path'])=={key:row[key] for key in ('bytes','sha256')}
    host=ROOT/'.build'/profile['campaign'];report=json.loads((host/'report.json').read_bytes())
    assert sha((host/'report.json').read_bytes())==profile['report_sha256']
    assert sha((ROOT/'.build/cyd-vorbis-singleton-zero-bit-host-01-command.json').read_bytes())==profile['outer_sha256']
    assert [case['id'] for case in report['cases']]==profile['case_ids']
    for index,case in enumerate(report['cases']):
        row=profile['native_outcomes'][case['id']];folder=host/'cases'/case['id'];path=folder/'decode-vorbis.json'
        receipt=json.loads(path.read_bytes())
        assert sha(path.read_bytes())==row['receipt_sha256'] and receipt['returncode']==row['returncode']==(4294967295 if index<4 else 0)
        assert (folder/'vorbis.wav').is_file() and (folder/'vorbis.wav').stat().st_size==row['wav_bytes']
        assert row['kind']==('packet_decode_failure_no_PCM' if index<4 else 'accepted')
        assert set(case['decoded'])==({'libvorbis'} if index<4 else {'libvorbis','vorbis'})
        if index>=4:assert case['cross_reference_max_abs_error']==1
    controls=ROOT/'.build/cyd-vorbis-singleton-zero-bit-prep-02/test_zero_controls.py'
    tree=ast.parse(controls.read_bytes().decode());methods=[node for node in ast.walk(tree)
        if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')]
    assert len(methods)==28
    relation=json.loads((HERE/'source-relation.json').read_bytes())
    assert relation['qualifier']==fact(HERE/'qualify.py') and relation['pins']==fact(HERE/'pins.json')
    actual={path.relative_to(HERE).as_posix() for path in HERE.rglob('*') if path.is_file()}
    assert actual|{'source-checks.json','readiness.json'}==EXPECTED
    files={path.relative_to(HERE).as_posix():fact(path) for path in sorted(HERE.rglob('*')) if path.is_file()}
    write_new('source-checks.json',dict(schema='zero8-reference-source-checks-v1',source_only=True,
        allowed_scope='AST_RAW_HASH_RECORDED_JSON_LOG_METADATA_ONLY',files=files,exact_inventory_count=len(EXPECTED),
        unchanged_carrier_and_full_PCM_helpers=True,unchanged_cross_reference_bound_LSB=2,
        qualifier_carrier_generator_witness_controls_references_compiler_SDK_QEMU_Git_device_executed=False,
        actual_PCM_read_or_compared=False))
    files={path.relative_to(HERE).as_posix():fact(path) for path in sorted(HERE.rglob('*')) if path.is_file()}
    write_new('readiness.json',dict(schema='zero8-reference-source-readiness-v1',source_only=True,
        ready_for_root_review=True,root_owns_actual_qualification=True,qualifier_executed=False,files=files))
    assert {path.relative_to(HERE).as_posix() for path in HERE.rglob('*') if path.is_file()}==EXPECTED
    print(json.dumps(dict(source_only=True,qualifier=fact(HERE/'qualify.py'),pins=fact(HERE/'pins.json'),
        checks=fact(HERE/'source-checks.json'),readiness=fact(HERE/'readiness.json'),exact_inventory_count=len(EXPECTED))))


if __name__=='__main__':main()
