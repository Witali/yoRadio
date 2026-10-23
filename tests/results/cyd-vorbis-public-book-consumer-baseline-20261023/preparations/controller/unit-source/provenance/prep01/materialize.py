"""Root-only source/data materialization. Never compiles or executes any C/codec."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from oracle import describe, need, patch_zero_fields

HERE = Path(__file__).resolve().parent


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def array(values): return ','.join(str(v) for v in values)


def host_table(description):
    """Independent prefix-trie serialization of known valid owned leaf arrays.

    Byte1 split-leaf records use two heads followed by left/right leaf tails.
    Their preorder storage may differ from the production parser's repacking;
    the host test does not claim those synthetic arrays were target-published.
    """
    root = {}
    for p in description['probes']:
        tree = root
        code = p['code_msb']
        for digit in code[:-1]: tree = tree.setdefault(int(digit), {})
        bit = int(code[-1]); need(bit not in tree, 'distinct known valid prefix leaves'); tree[bit] = p['leaf']
    node, leafwords = description['dec_nodeb'], description['dec_leafw']
    if node == 4 or leafwords == 1:
        records = []
        def append(tree):
            index = len(records); records.append([0, 0])
            for bit in (0, 1):
                child = tree[bit]
                records[index][bit] = append(child) if isinstance(child, dict) else child | (0x80000000 if node == 4 else 0x80)
            return index
        append(root)
        values = sum(records, [])
        if node == 4:
            while len(values) * 4 < description['table_bytes']: values.append(0)
        result = b''.join(value.to_bytes(node, 'little') for value in values)
    else:
        need(node == 1 and leafwords == 2, 'finite split leaf format')
        out = []
        def append(tree):
            offset = len(out); leaves = [not isinstance(tree[b], dict) for b in (0, 1)]
            out.extend([0] * (2 + sum(leaves)))
            tail = offset + 2
            for bit in (0, 1):
                child = tree[bit]
                if leaves[bit]:
                    need(0 <= child < 0x8000, 'known split leaf range')
                    out[offset + bit] = 0x80 | child >> 8; out[tail] = child & 255; tail += 1
                else:
                    child_offset = append(child); need(child_offset < 128, 'known internal byte offset'); out[offset + bit] = child_offset
            return offset
        append(root); result = bytes(out)
    need(len(result) == description['table_bytes'], 'finite owned host table size')
    return result


def render(model, setups):
    lines = ['/* Independent raw-book/Fraction fixture materialization; no codec execution. */', '#pragma once',
        '#include <stdint.h>', '#include <stddef.h>', f'#define CONSUMER_CONTRACT_SHA "{sha(canonical(model))}"',
        f'#define CONSUMER_CASES {len(model["cases"])}U', f'#define CONSUMER_CALLS {model["vector_calls"]}U',
        'typedef struct { uint32_t wire; unsigned bits; int32_t expected[3][16]; } consumer_probe_t;',
        'typedef struct { const char *id; const uint8_t *setup; unsigned setup_bytes,first,end;',
        ' int dim,entries,used,maxlen,node,leafwords,type,qbits,qpack,sequence,minp,delp; int32_t qmin,qdel;',
        ' unsigned table_bytes,qval_bytes; const void *qval,*host_table; int host_node,host_leafwords;',
        ' const consumer_probe_t *probes; unsigned probe_count,point_count; int points[3]; } consumer_case_t;']
    for i, (c, setup) in enumerate(zip(model['cases'], setups)):
        d = c['book']; lines.append(f'static const uint8_t raw_{i}[] = {{{array(setup)}}};')
        qbytes, table = bytes.fromhex(d['qval_hex']), bytes.fromhex(c['host_table_hex'])
        if qbytes:
            width = 1 if d['q_bits'] <= 8 else 2
            values = [int.from_bytes(qbytes[j:j + width], 'little') for j in range(0, len(qbytes), width)]
            lines.append(f'static const uint{width * 8}_t quant_{i}[] = {{{array(values)}}};')
        width = d['dec_nodeb']
        values = [int.from_bytes(table[j:j + width], 'little') for j in range(0, len(table), width)]
        lines.append(f'static const uint{width * 8}_t table_{i}[] = {{{array(str(v)+"U" for v in values)}}};')
        lines.append(f'static const consumer_probe_t probes_{i}[] = {{')
        for probe in d['probes']:
            expected = ','.join('{' + array(probe['expected_by_point'][str(point)]) + '}' for point in d['points'])
            lines.append('{' + f'{probe["wire"]}U,{probe["bits"]},{{{expected}}}' + '},')
        lines.append('};')
    lines.append('static const consumer_case_t consumer_cases[] = {')
    fields = dict(dim='dim',entries='entries',used='used_entries',maxlen='dec_maxlength',node='dec_nodeb',leafwords='dec_leafw',
        type='dec_type',qbits='q_bits',qpack='q_pack',sequence='q_seq',qmin='q_min',minp='q_minp',qdel='q_del',delp='q_delp',table_bytes='table_bytes')
    for i, c in enumerate(model['cases']):
        d = c['book']; values = ','.join('.' + key + '=' + str(d[value]) for key, value in fields.items())
        lines.append('{' + f'.id="{c["id"]}",.setup=raw_{i},.setup_bytes={len(setups[i])},.first={d["raw_book"]["first"]},.end={d["raw_book"]["end"]},' + values +
            f',.qval_bytes={len(bytes.fromhex(d["qval_hex"]))},.qval=' + (f'quant_{i}' if d['qval_hex'] else 'NULL') +
            f',.host_table=table_{i},.host_node={d["dec_nodeb"]},.host_leafwords={d["dec_leafw"]},.probes=probes_{i},.probe_count={len(d["probes"])},.point_count={len(d["points"])},.points={{{array(d["points"])}}}' + '},')
    lines += ['};', '_Static_assert(sizeof(consumer_cases)/sizeof(consumer_cases[0]) == CONSUMER_CASES,"full cases");', '']
    return '\n'.join(lines).encode()


def materialize(output, readiness_sha):
    raw = (HERE / 'readiness.json').read_bytes(); need(sha(raw) == readiness_sha, 'reviewed source readiness SHA')
    ready = json.loads(raw)
    for row in ready['files']:
        data = (HERE / row['path']).read_bytes(); need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'frozen source identity')
    need(not output.exists() and output.parent == HERE.parent and output != HERE, 'fresh separate direct-child runtime')
    source = json.loads((HERE / 'fixture-inputs.json').read_bytes()); cases, setups = [], []
    for i, row in enumerate(source['cases']):
        original = (HERE / row['setup']).read_bytes(); need(sha(original) == row['setup_sha256'], 'exact original raw setup')
        raw, edits = patch_zero_fields(original, row['book_index'], row['overrides'])
        points = (-8, -24) if 'floor0-even6-' in row['id'] else (0, -8, -24)
        description = describe(raw, row['book_index'], points)
        table = host_table(description)
        cases.append(dict(index=i,id=row['id'],input=row,materialized_setup_sha256=sha(raw),zero_field_edits=edits,
            book=description,host_table_hex=table.hex(),host_table_is_independent_owned_format=True,
            host_table_claimed_target_publication=False))
        setups.append(raw)
    model = dict(schema='public-owned-book-consumer-model-v1',cases=cases,case_count=len(cases),
        codeword_probes=sum(len(c['book']['probes']) for c in cases),
        vector_calls=sum(len(c['book']['probes']) * len(c['book']['points']) for c in cases),
        point_semantics='integer=exact_quantized_value*2**(-point); canonical q_del already scaled by q_bits',
        independent_oracle='exact Fraction from raw fields; retained canonical q_del scaling identity',
        physical_device=False,vendor_decoder=False,PCM=False,full_G6_qualified=False)
    need((model['case_count'],model['codeword_probes'],model['vector_calls']) == (36,123,365), 'complete predeclared finite coverage')
    output.mkdir()
    for q in sorted((HERE / 'project').rglob('*')):
        if q.is_file():
            destination = output / 'project' / q.relative_to(HERE / 'project');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(q.read_bytes())
    for name in ('consumer_unit.c','consumer_port.inc','host_codebook.h','host_ogg.h'):
        (output / 'project/main' / name).write_bytes((HERE / name).read_bytes())
    header = render(model, setups); (output / 'project/main/consumer_data.h').write_bytes(header)
    # Independent restricted array readback, without a C compiler.
    text = header.decode()
    for i, raw in enumerate(setups):
        match = re.search(r'static const uint8_t raw_' + str(i) + r'\[\] = \{([0-9,]+)\};', text)
        need(match is not None and bytes(map(int, match[1].split(','))) == raw, 'all full raw C arrays independently recovered')
    (output / 'contract.json').write_text(json.dumps(dict(contract_sha256=sha(canonical(model)),model=model),indent=2)+'\n',encoding='utf-8')
    (output / 'source-preparation.json').write_text(json.dumps(dict(source_readiness_sha256=readiness_sha,
        cases=36,codeword_probes=123,vector_calls=365,header_sha256=sha(header),
        compiled=False,target_executed=False,host_executed=False,numeric_qualified=False),indent=2)+'\n',encoding='utf-8')
    runtime_files=[]
    for path in sorted(output.rglob('*')):
        if path.is_file():
            data=path.read_bytes();runtime_files.append(dict(path=path.relative_to(output).as_posix(),bytes=len(data),sha256=sha(data)))
    (output/'readiness.json').write_text(json.dumps(dict(schema='public-book-consumer-generated-runtime-readiness-v1',
        source_readiness_sha256=readiness_sha,files=runtime_files,compiled=False,target_executed=False,host_executed=False),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(output),cases=36,codeword_probes=123,vector_calls=365,compiled=False)))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--readiness-sha256',required=True)
    args=parser.parse_args();materialize(args.output.resolve(),args.readiness_sha256)
