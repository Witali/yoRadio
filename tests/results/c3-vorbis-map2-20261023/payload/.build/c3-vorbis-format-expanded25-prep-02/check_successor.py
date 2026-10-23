"""Independent restricted-C source readback; no runtime/protocol/decoder imports."""
import ast
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT/'.build/c3-vorbis-format-expanded25-prep-01'
CYD = ROOT/'.build/cyd-vorbis-format-expanded25-prep-02'
RUNNER = 'run-c3-vorbis-format-expanded25-qemu.py'
OLD_READINESS = '73cf6cc976a7300cd23ca1f47fcc778da9e67bfd277dd0b7cc842c2bee362003'
OLD_CONTROLLER = '7a7ba50fd01656c7e3a29e9d2e72a8d75f6d15a105e57f0f25bdfc638a4270f4'
OLD_DATA = '4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757'
NEW_DATA = '97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc'


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(bytes=len(data),sha256=sha(data))


def constant(tree,name):
    values = [node.value for node in tree.body if isinstance(node,ast.Assign) and
        any(isinstance(t,ast.Name) and t.id == name for t in node.targets)]
    need(len(values) == 1,'UNIQUE_PYTHON_CONSTANT:'+name)
    return ast.literal_eval(values[0])


def number(text):
    need(re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)[uU]?',text) is not None,'RESTRICTED_C_INTEGER')
    return int(text.rstrip('uU'),0 if text.lower().startswith('0x') else 10)


def macro(text,name):
    matches = re.findall(r'^#define '+re.escape(name)+r' ([^\r\n]+)$',text,re.M)
    need(len(matches) == 1,'UNIQUE_C_MACRO:'+name)
    return matches[0]


def descriptor_body(text):
    values = list(re.finditer(r'static const corpus_case_t corpus_cases\[CORPUS_CASE_COUNT\] = \{\n(.*?)\n\};',text,re.S))
    need(len(values) == 1,'UNIQUE_CORPUS_DESCRIPTOR_ARRAY')
    return values[0]


def read_header(text,contract):
    model = contract['model']; cases = model['cases']
    # Macro count is checked against the model BEFORE interpreting any C arrays.
    capacity = number(macro(text,'CORPUS_CASE_COUNT'))
    need(capacity == len(cases),'CAPACITY_MODEL_MISMATCH')
    pcm_macro = number(macro(text,'CORPUS_EXPECTED_PCM_BYTES'))
    need(pcm_macro == model['total_pcm'],'EXPECTED_PCM_MODEL_MISMATCH')
    need(json.loads(macro(text,'CORPUS_CONTRACT_SHA256')) == contract['contract_sha256'],'MODEL_HASH_MACRO_MISMATCH')
    need(json.loads(macro(text,'CORPUS_CONTRACT_FILE_SHA256')) == sha((HERE/'contract.json').read_bytes()),'CONTRACT_FILE_MACRO_MISMATCH')
    container = descriptor_body(text)
    entry_pattern = re.compile(r'\s*\{([^{}]*)\},',re.S)
    entries = list(entry_pattern.finditer(container.group(1)))
    need(entry_pattern.sub('',container.group(1)).strip() == '','RESTRICTED_DESCRIPTOR_GRAMMAR')
    need(len(entries) == capacity == len(cases),'DESCRIPTOR_MODEL_MISMATCH')
    arrays = {}
    pattern = re.compile(r'static const (uint8_t|uint32_t) ([A-Za-z_]\w*)\[([0-9]+)\] = \{\n(.*?)\n\};',re.S)
    for match in pattern.finditer(text):
        typ,name,size,body = match.groups()
        need(name not in arrays,'DUPLICATE_C_ARRAY')
        tokens = [token.strip() for token in body.strip().split(',')]
        need(tokens[-1] == '','ARRAY_TRAILING_COMMA')
        values = [number(token) for token in tokens[:-1]]
        need(len(values) == int(size) and all(0 <= value < 2**(8 if typ == 'uint8_t' else 32) for value in values),'ARRAY_SIZE_OR_RANGE')
        arrays[name] = (typ,values)
    needed_arrays,rows = set(),[]
    fields_expected = {'id','identification','identification_size','setup','setup_size','audio','audio_size',
        'offsets','offset_count','modes','mode_count','rate','channels','short_block','long_block','expected_pcm_bytes'}
    for index,(entry,case) in enumerate(zip(entries,cases)):
        field_pattern = re.compile(r'\s*\.([A-Za-z_]\w*) = ([^,\n]+),')
        fields = list(field_pattern.finditer(entry.group(1)))
        need(field_pattern.sub('',entry.group(1)).strip() == '','RESTRICTED_DESCRIPTOR_FIELDS')
        values = {match[1]:match[2] for match in fields}
        need(len(fields) == len(values) and set(values) == fields_expected,'DESCRIPTOR_FIELD_SET')
        need(json.loads(values['id']) == case['id'],'CASE_ID_OR_ORDER')
        recovered = {}
        for kind in ('identification','setup','audio','offsets','modes'):
            name = f'corpus_{index:03d}_{kind}'
            need(values[kind] == name and name in arrays,'ARRAY_REFERENCE_OR_ORDER')
            needed_arrays.add(name)
            typ,items = arrays[name]
            need(typ == ('uint32_t' if kind == 'offsets' else 'uint8_t'),'ARRAY_ELEMENT_TYPE')
            count = kind[:-1]+'_count' if kind in ('offsets','modes') else kind+'_size'
            expected_expr = f'sizeof({name}) / sizeof({name}[0])' if kind in ('offsets','modes') else f'sizeof({name})'
            need(values[count] == expected_expr,'RESTRICTED_SIZE_EXPRESSION')
            recovered[kind] = items if kind in ('offsets','modes') else bytes(items)
        need(recovered['offsets'] == case['offsets'] and recovered['modes'] == case['modes'],'OFFSETS_OR_MODES_MODEL')
        need(len(recovered['modes']) == 14 and len(recovered['offsets']) == 15 and recovered['offsets'][0] == 0 and
             recovered['offsets'][-1] == len(recovered['audio']) and all(a < b for a,b in zip(recovered['offsets'],recovered['offsets'][1:])),'COMPLETE_PACKET_OFFSETS')
        for kind in ('identification','setup','audio'):
            need(sha(recovered[kind]) == case['raw_sha256'][kind],'RAW_MODEL_HASH:'+kind)
        ident = recovered['identification']
        need(len(ident) == 30 and ident[:7] == b'\x01vorbis' and ident[7:11] == bytes(4) and ident[11] == case['channels'] and
             int.from_bytes(ident[12:16],'little') == case['rate'] and ident[29] == 1 and
             (1 << (ident[28]&15),1 << (ident[28]>>4)) == (case['short'],case['long']),'IDENTIFICATION_FIELDS')
        need(recovered['setup'][:7] == b'\x05vorbis','PREFIXED_COMPLETE_SETUP')
        for field,expected in (('rate',case['rate']),('channels',case['channels']),('short_block',case['short']),
            ('long_block',case['long']),('expected_pcm_bytes',case['total_pcm'])):
            need(number(values[field]) == expected,'SCALAR_MODEL:'+field)
        blocks = [case['long'] if mode else case['short'] for mode in recovered['modes']]
        frames = [0]+[(a+b)//4 for a,b in zip(blocks,blocks[1:])]
        need(frames == case['frames'] and [n*case['channels']*2 for n in frames] == case['pcm'] and sum(case['pcm']) == case['total_pcm'],'OVERLAP_PCM_ACCOUNTING')
        rows.append(dict(case=index,id=case['id'],array_count=5,packet_count=14,rate=case['rate'],channels=case['channels'],
            short=case['short'],long=case['long'],frames=frames,expected_pcm_bytes=case['total_pcm'],raw_sha256=case['raw_sha256']))
    need(set(arrays) == needed_arrays and len(arrays) == len(cases)*5,'EXACT_ARRAY_SET')
    need(sum(row['packet_count'] for row in rows) == model['total_packets'] and sum(row['expected_pcm_bytes'] for row in rows) == pcm_macro,'TOTAL_MODEL_ACCOUNTING')
    return dict(capacity=capacity,actual_descriptors=len(entries),model_cases=len(cases),recovered_arrays=len(arrays),
        packets=sum(row['packet_count'] for row in rows),expected_pcm_bytes=pcm_macro,cases=rows)


def main():
    paths = [path for path in sorted(HERE.rglob('*')) if path.is_file()]
    before = {str(path.relative_to(HERE)):fact(path) for path in paths}
    old = json.loads((OLD/'readiness.json').read_bytes())
    need(sha((OLD/'readiness.json').read_bytes()) == OLD_READINESS and fact(OLD/RUNNER)['sha256'] == OLD_CONTROLLER,'FROZEN_C3_01_PINS')
    for name,row in old['files'].items(): need(fact(OLD/name) == row,'OLD_SOURCE_CHANGED:'+name)
    for name,row in old['external_inputs'].items(): need(fact(ROOT/name) == row,'OLD_EXTERNAL_CHANGED:'+name)
    relation = json.loads((HERE/'source-relation.json').read_bytes())
    for name,row in relation['source_files'].items():
        data = (HERE/name).read_bytes(); original = (OLD/name).read_bytes()
        need(fact(HERE/name) == row['successor'] and fact(OLD/name) == row['original'],'SOURCE_RELATION_PIN')
        need(data.replace(NEW_DATA.encode(),OLD_DATA.encode()) == original if name == RUNNER else data == original,'SOLE_DATA_PIN_CHANGE')
    parsed = [str(path.relative_to(HERE)) for path in paths if path.suffix == '.py' and ast.parse(path.read_bytes()) is not None]
    controller = ast.parse((HERE/RUNNER).read_bytes())
    need(constant(controller,'DATA_HEADER_SHA') == NEW_DATA,'NEW_DATA_PIN')
    need(constant(controller,'SDK_HEAD') == '9a97f6c54ec638111ce55cd36581b3c192f15207','SDK61_PIN')
    need(constant(controller,'CONTRACT_ID') == '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc','MODEL_PIN')
    data = (HERE/'materialized01/data.h').read_bytes()
    need(sha(data) == NEW_DATA and data == (CYD/'materialized01/data.h').read_bytes(),'BYTE_IDENTICAL_CORRECTED_DATA')
    contract = json.loads((HERE/'contract.json').read_bytes())
    need(fact(HERE/'contract.json')['sha256'] == '717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d','CONTRACT_PIN')
    recovered = read_header(data.decode(),contract)
    need((recovered['capacity'],recovered['actual_descriptors'],recovered['model_cases'],recovered['packets'],recovered['expected_pcm_bytes']) == (25,25,25,350,623360),'EXACT25_REQUIRED')
    olddata = (ROOT/'.build/cyd-vorbis-format-expanded25-prep-01/materialized01/data.h').read_bytes()
    need(sha(olddata) == OLD_DATA,'ORIGINAL17_HEADER_PIN')
    text = data.decode(); container = descriptor_body(text)
    missing = re.sub(r'\s*\{[^{}]*\},','',container.group(1),count=1,flags=re.S)
    controls = [('original17_data',olddata.decode(),'CAPACITY_MODEL_MISMATCH'),
        ('forced_capacity17',text.replace('#define CORPUS_CASE_COUNT 25U','#define CORPUS_CASE_COUNT 17U'),'CAPACITY_MODEL_MISMATCH'),
        ('obsolete_pcm_macro398080',text.replace('#define CORPUS_EXPECTED_PCM_BYTES 623360U','#define CORPUS_EXPECTED_PCM_BYTES 398080U'),'EXPECTED_PCM_MODEL_MISMATCH'),
        ('one_descriptor_removed',text[:container.start(1)]+missing+text[container.end(1):],'DESCRIPTOR_MODEL_MISMATCH')]
    control_rows = []
    for name,mutant,expected in controls:
        need(mutant != text,'CONTROL_MUST_CHANGE_SOURCE')
        try: read_header(mutant,contract)
        except ValueError as error: need(str(error) == expected,'WRONG_CONTROL_REJECTION:'+name)
        else: raise ValueError('CONTROL_UNDETECTED:'+name)
        control_rows.append(dict(name=name,input_sha256=sha(mutant.encode()),rejection=expected,source_only=True))
    for name,row in before.items(): need(fact(HERE/name) == row,'SOURCE_CHANGED_DURING_CHECK')
    for name,row in old['files'].items(): need(fact(OLD/name) == row,'OLD_SOURCE_CHANGED_DURING_CHECK')
    for name,row in old['external_inputs'].items(): need(fact(ROOT/name) == row,'OLD_EXTERNAL_CHANGED_DURING_CHECK')
    report = dict(schema='c3-expanded25-source-closure-v2',scope='SOURCE_AST_RESTRICTED_C_READBACK_ONLY',source_only=True,
        runtime_imported_or_executed=False,protocol_tests_executed=False,SDK_compiler_QEMU_reference_PCM_Git_executed=False,
        old_readiness_sha256=OLD_READINESS,old_inputs_unchanged=True,controller=fact(HERE/RUNNER),python_ast_parsed=parsed,
        sole_functional_change='DATA_HEADER_SHA literal',corrected_data=fact(HERE/'materialized01/data.h'),recovery=recovered,
        negative_controls=control_rows,inputs=before)
    with (HERE/'source-closure02.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(scope=report['scope'],controller=report['controller'],corrected_data=report['corrected_data'],
        capacity=recovered['capacity'],actual_descriptors=recovered['actual_descriptors'],model_cases=recovered['model_cases'],
        recovered_arrays=recovered['recovered_arrays'],packets=recovered['packets'],expected_pcm_bytes=recovered['expected_pcm_bytes'],
        negative_controls=control_rows,old_inputs_unchanged=True)))


if __name__ == '__main__': main()
