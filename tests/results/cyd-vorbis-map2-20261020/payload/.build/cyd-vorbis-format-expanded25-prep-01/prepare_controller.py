"""Write an unapplied25-case controller adaptation; AST-read, never execute it."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / ".build/cyd-vorbis-format-corpus-checked-prep-02/run-cyd-vorbis-format-corpus-checked-qemu.py"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sha(OLD) != "3aa167fe4b231d2c15b91b1b5c78b24da3410d18eaacc0709d6afe0c33ea902d": raise ValueError("prior controller pin")
    original = OLD.read_bytes().decode(); text = original
    def once(old, new):
        nonlocal text
        if text.count(old) != 1: raise ValueError("controller adaptation anchor: " + old[:90])
        text = text.replace(old, new, 1)
    once('from protocol import load_contract, validate_log\n', 'from protocol import load_contract, validate_log\nfrom reference_binding import verify as verify_source_binding\n')
    once("('.build/cyd-vorbis-books-prep-01/generated01/matrix.json',\n     '38e38f1f5ada7cd84a6ea91c5b46e0680ee62a7f511c9a72bfa7b6d7eb64cd2e')",
         "('.build/cyd-vorbis-format-expanded25-prep-01/inputs/books16/matrix.json',\n     '" + sha(HERE / "inputs/books16/matrix.json") + "')")
    start, end = text.index('REFERENCE_PROOFS = {'), text.index('\nCONTRACT_ID =')
    proof = {}
    for p in ('.build/cyd-vorbis-format-corpus-qualified-01/qualification.json', '.build/cyd-vorbis-format-corpus-host-01/report.json', '.build/cyd-vorbis-format-corpus-host-01-command.json',
              '.build/cyd-vorbis-map2-regression-qualified-01/qualification.json', '.build/cyd-vorbis-map2-regression-host-01/report.json', '.build/cyd-vorbis-map2-regression-host-01-command.json'):
        proof[p] = sha(ROOT / p)
    text = text[:start] + 'REFERENCE_PROOFS = ' + repr(proof) + text[end:]
    for old, new in [('847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a', '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc'),
        ('6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391', sha(HERE / 'contract.json')),
        ('b4db391fda10e7361f57fe4242574593902042f0e0ef9a48fe24aac144bb153d', sha(HERE / 'materialized01/data.h'))]: once(old, new)
    once("SDK_HEAD =", "SOURCE_MAP_SHA = '" + sha(HERE / 'source-map.json') + "'\nREFERENCE_BINDING_SHA = '" + sha(HERE / 'reference-binding.json') + "'\nREFERENCE_HELPER_SHA = '" + sha(HERE / 'reference_binding.py') + "'\nSDK_HEAD =")
    once("harness = Path(__file__).resolve().parent / 'target/cyd_vorbis_format_corpus_checked_qemu'", "harness = Path(__file__).resolve().parent / 'target/cyd_vorbis_format_expanded25_qemu'\n    source_map_path = Path(__file__).with_name('source-map.json')\n    binding_path = Path(__file__).with_name('reference-binding.json')\n    binding_helper = Path(__file__).with_name('reference_binding.py')")
    once('protected = (candidate,harness,contract_path,data_header,sdk,tools,codec,ps.parent,qemu.parent,rom,', 'protected = (candidate,harness,contract_path,data_header,source_map_path,binding_path,binding_helper,sdk,tools,codec,ps.parent,qemu.parent,rom,')
    once("repo/'.build/cyd-vorbis-format-corpus-qualified-01',repo/'.build/cyd-vorbis-format-corpus-host-01')", "repo/'.build/cyd-vorbis-format-corpus-qualified-01',repo/'.build/cyd-vorbis-format-corpus-host-01',\n                 repo/'.build/cyd-vorbis-map2-regression-qualified-01',repo/'.build/cyd-vorbis-map2-regression-host-01')")
    once("*[repo/name for name in REFERENCE_PROOFS], harness/'main/main.c',", "*[repo/name for name in REFERENCE_PROOFS], source_map_path, binding_path, binding_helper, harness/'main/main.c',")
    once("'Contract differs from the exact two qualified source matrices/raw packets'", "'Contract differs from exact merged books16 plus original floor9 source matrices/raw packets'")
    start = text.index("        qualified = json.loads((repo/'.build/cyd-vorbis-format-corpus-qualified-01/qualification.json')")
    end = text.index("        shutil.copytree(out/'sources/candidate'", start)
    text = text[:start] + '''        need(sha(source_map_path)==SOURCE_MAP_SHA and sha(binding_path)==REFERENCE_BINDING_SHA and
             sha(binding_helper)==REFERENCE_HELPER_SHA,'Expanded25 source binding/helper pins')
        freeze(source_map_path,Path('corpus/source-map.json'))
        freeze(binding_path,Path('reference/reference-binding.json'))
        freeze(binding_helper,Path('helpers/reference_binding.py'))
        mapping = json.loads(source_map_path.read_bytes())
        binding = json.loads(binding_path.read_bytes())
        verify_source_binding(contract,mapping,binding)
        need(len(binding['cases'])==25 and binding['new_reference_commands_executed'] is False and
             binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False,
             'Exact coherent25 source bindings required; historical dual NONPASS remains')
        for item in binding['proof_facts']:
            path = Path(item['path'])
            need(path.is_relative_to(repo) and sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],
                 'Actual original/copied raw or frozen historical reference fact differs')
            freeze(path,Path('reference-facts')/path.relative_to(repo))
        report['corpus'] = dict(contract_sha256=CONTRACT_ID,contract_file_sha256=args.contract_sha256,
            data_header_sha256=args.data_sha256,manifest_sha256=model['manifest_sha256'],cases=25,packets=350,
            expected_pcm=623360,source_map_sha256=SOURCE_MAP_SHA,reference_binding_sha256=REFERENCE_BINDING_SHA,
            source_reference_scopes=binding['source_scopes'],new_reference_commands_executed=False,
            aggregate_reference_campaign_exists=False,dual_reference_passed=False)
''' + text[end:]
    for old, new in [('17', '25'), ('238', '350'), ('398080', '623360'), ('131071', '33554431'), ('530', '778')]: text = re.sub(r'\b' + old + r'\b', new, text)
    text = text.replace('reviewed17-case', 'reviewed25-case').replace('All17', 'All25')
    once("source_index=case['source_index'],reference_id=f\"{case['source_index']}-{case['id']}\",", "source_index=case['source_index'],reference_id=binding['cases'][index]['original_reference_id'],\n                reference_scope=binding['cases'][index]['original_group'],\n                reference_qualification_sha256=binding['cases'][index]['qualification_sha256'],")
    # AST-only relation checks: do not import/execute the target controller.
    old_ast, new_ast = ast.parse(original), ast.parse(text)
    for name in ('save', 'freeze', 'current', 'execute'):
        old_nodes = [n for n in ast.walk(old_ast) if isinstance(n, ast.FunctionDef) and n.name == name]
        new_nodes = [n for n in ast.walk(new_ast) if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(old_nodes) != 1 or len(new_nodes) != 1 or ast.dump(old_nodes[0], include_attributes=False) != ast.dump(new_nodes[0], include_attributes=False): raise ValueError('inherited runtime helper changed: ' + name)
    for name in ('ARCHIVES', 'SDK_HEAD', 'MODULES', 'CALLER_SHA', 'PROTOCOL_SHA', 'CASE_HEADER_SHA', 'RAW_HELPER_SHA'):
        def value(tree):
            return ast.dump(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)), include_attributes=False)
        if value(old_ast) != value(new_ast): raise ValueError('inherited fixed identity changed ' + name)
    with (HERE / 'run-cyd-vorbis-format-expanded25-qemu.py').open('xb') as stream: stream.write(text.encode())
    with (HERE / 'controller-adaptation.diff').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile=str(OLD), tofile='run-cyd-vorbis-format-expanded25-qemu.py')))
    report = dict(schema='expanded25-controller-source-relation-v1', ast_only=True, controller_executed=False,
        original_sha256=sha(OLD), adapted_sha256=hashlib.sha256(text.encode()).hexdigest(),
        byte_equal_runtime_helpers=['save','freeze','current','execute'], fixed_identity_AST_equal=['ARCHIVES','SDK_HEAD','MODULES','CALLER_SHA','PROTOCOL_SHA','CASE_HEADER_SHA','RAW_HELPER_SHA'],
        expected_cases=25, packets=350, pcm=623360, events=778, mask=33554431,
        original17_qualification_not_relabelled25=True, real_reference_source_scopes=['old17','new8'])
    with (HERE / 'controller-source-relation.json').open('x', encoding='utf-8', newline='\n') as stream: json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
