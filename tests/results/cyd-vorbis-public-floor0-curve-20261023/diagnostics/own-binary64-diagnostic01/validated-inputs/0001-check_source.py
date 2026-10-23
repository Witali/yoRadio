"""Read source AST/hash and recorded JSON metadata only; never execute proposed code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'.build/cyd-vorbis-public-floor0-curve-prep-03'
EXPECTED={'compare_analytic.py','protocol.py','curve_diagnostic.py','public-portability.json',
          'source-origins.json','README.md','comparator-adaptation.diff','check_source.py','source-checks.json','readiness.json'}


def sha(data):return hashlib.sha256(data).hexdigest()


def row(path):
    data=path.read_bytes();return dict(bytes=len(data),sha256=sha(data))


def literal(tree,name):
    node=next(node for node in tree.body if isinstance(node,ast.Assign) and
        any(isinstance(target,ast.Name) and target.id==name for target in node.targets))
    return ast.literal_eval(node.value)


def write_new(name,value):
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def main():
    trees={path.name:ast.parse(path.read_bytes().decode(),filename=str(path)) for path in HERE.glob('*.py')}
    origins=json.loads((HERE/'source-origins.json').read_bytes())
    for group in ('runtime','unchanged_helpers','capture'):
        for item in origins[group].values():
            path=ROOT/item['path'];assert row(path)=={k:item[k] for k in ('bytes','sha256')}
    assert row(BASE/'compare_analytic.py')=={k:origins['base_comparator'][k] for k in ('bytes','sha256')}
    for name,source in (('protocol.py','protocol.py'),('curve_diagnostic.py','witness-source/curve_diagnostic.py'),('public-portability.json','public-portability.json')):
        assert (HERE/name).read_bytes()==(BASE/source).read_bytes()
    expected=''.join(difflib.unified_diff((BASE/'compare_analytic.py').read_bytes().decode().splitlines(True),
        (HERE/'compare_analytic.py').read_bytes().decode().splitlines(True),fromfile='curve-prep03/compare_analytic.py',tofile='analytic-prep01/compare_analytic.py'))
    assert (HERE/'comparator-adaptation.diff').read_bytes()==expected.encode()
    before=ast.parse((BASE/'compare_analytic.py').read_bytes().decode())
    def bin_loop(tree):
        return next(node for node in ast.walk(tree) if isinstance(node,ast.For) and isinstance(node.target,ast.Name)
            and node.target.id=='index' and isinstance(node.iter,ast.Call) and isinstance(node.iter.func,ast.Name)
            and node.iter.func.id=='range' and len(node.iter.args)==1 and isinstance(node.iter.args[0],ast.Constant)
            and node.iter.args[0].value==16)
    assert ast.dump(bin_loop(before),include_attributes=False)==ast.dump(bin_loop(trees['compare_analytic.py']),include_attributes=False)
    for name,key in (('REPORT_SHA','report'),('TERMINAL_SHA','terminal')):
        assert literal(trees['compare_analytic.py'],name)==origins['capture'][key]['sha256']
    for name,key in (('CONTROLLER_SHA','run-public-curve.py'),('RUNTIME_READINESS_SHA','runtime-readiness.json'),('CONTRACT_SHA','contract.json')):
        assert literal(trees['compare_analytic.py'],name)==origins['runtime'][key]['sha256']
    for name,path in (('PUBLIC_SHA',BASE/'project/main/public/floor0.c'),('PROTOCOL_SHA',HERE/'protocol.py'),('MATH_SHA',HERE/'curve_diagnostic.py')):
        assert literal(trees['compare_analytic.py'],name)==sha(path.read_bytes())
    report=json.loads((ROOT/origins['capture']['report']['path']).read_bytes())
    terminal=json.loads((ROOT/origins['capture']['terminal']['path']).read_bytes())
    assert terminal==dict(schema='direct-exec-tool-terminal-v1',session_id=43646,terminal_chunk_id='f26f66',exit_code=0,
        report_sha256=origins['capture']['report']['sha256'],entrypoint_sha256=origins['runtime']['run-public-curve.py']['sha256'])
    assert report['completed'] is True and report['passed'] is True and len(report['commands'])==22 and len(report['observed_curves'])==168
    assert report['observed']['bins']==58368
    actual={path.name for path in HERE.iterdir() if path.is_file()}
    assert actual|{'source-checks.json','readiness.json'}==EXPECTED
    files={path.name:row(path) for path in sorted(HERE.iterdir()) if path.is_file()}
    write_new('source-checks.json',dict(schema='public-floor0-analytic-source-checks-v1',source_only=True,
        allowed_scope='SOURCE_AST_RAW_HASH_RECORDED_JSON_METADATA_ONLY',files=files,
        exact_inventory_count=len(EXPECTED),unchanged_math_bin_loop_AST=True,unchanged_protocol_and_formula_bytes=True,
        actual_curves_read_or_compared=False,comparator_protocol_math_tests_compiler_SDK_QEMU_codec_Git_device_executed=False))
    files={path.name:row(path) for path in sorted(HERE.iterdir()) if path.is_file()}
    write_new('readiness.json',dict(schema='public-floor0-analytic-source-readiness-v1',source_only=True,
        ready_for_root_review=True,root_owns_all_execution=True,actual_diagnostic_run=False,files=files))
    assert {path.name for path in HERE.iterdir() if path.is_file()}==EXPECTED
    print(json.dumps(dict(source_only=True,comparator=row(HERE/'compare_analytic.py'),checks=row(HERE/'source-checks.json'),
        readiness=row(HERE/'readiness.json'),exact_inventory_count=len(EXPECTED))))


if __name__=='__main__':main()
