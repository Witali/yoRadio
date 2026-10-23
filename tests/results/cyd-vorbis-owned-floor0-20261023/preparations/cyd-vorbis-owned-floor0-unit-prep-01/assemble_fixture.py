"""Create-only source assembly from frozen metadata/raw bytes; never run C/reader/tests."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETUP = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
ABI = 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build():
    rows, raw_setups = [], []
    for group in ('original','minp1'):
        base = HERE/'inputs'/group
        matrix = json.loads((base/'matrix.json').read_bytes())
        construction = json.loads((base/'construction-fields.json').read_bytes())
        cases = [c for c in matrix['cases'] if c['id'].startswith('floor0-')]
        need(len(cases)==6,'All original6/equivalent6 source cases')
        for case in cases:
            raw = (base/case['setup']).read_bytes()
            identity = (base/case['identification']).read_bytes()
            fields = {f['name']:f for f in construction['variants'][case['variant']]['setup']['fields']}
            def metadata(name,width):
                f=fields[name]
                need(f['width']==width,'Declared field width')
                value=(int.from_bytes(raw,'little')>>f['offset'])&((1<<width)-1)
                need(value==f['value'],'Source assembly raw/metadata field match')
                return value
            count=metadata('floor0.books_minus_1',4)+1
            books=[metadata(f'floor0.book[{i}]',8) for i in range(count)]
            start=fields['floor0.order']['offset']
            end=fields[f'floor0.book[{count-1}]']['offset']+8
            parsed=8+16+16+6+8+4+count*8
            need(end-start==parsed and parsed in (66,74),'Explicit complete floor0 bitspan')
            floor_value=(int.from_bytes(raw,'little')>>start)&((1<<parsed)-1)
            total_books=metadata('books_minus_1',8)+1
            need(identity[:7]==b'\x01vorbis' and len(identity)==30 and identity[11]==2,'Source identification')
            row=dict(id=case['id'],group=group,setup_snapshot=f'inputs/{group}/{case["setup"]}',
                identification_snapshot=f'inputs/{group}/{case["identification"]}',setup_sha256=sha(raw),
                identification_sha256=sha(identity),setup_bytes=len(raw),first_bit=start,end_bit=end,parse_bits=parsed,
                floor_bits_le_hex=floor_value.to_bytes((parsed+7)//8,'little').hex(),total_books=total_books,
                order=metadata('floor0.order',8),rate=metadata('floor0.rate',16),barkmap=metadata('floor0.barkmap',16),
                ampbits=metadata('floor0.amplitude_bits',6),ampdB=metadata('floor0.amplitude_offset',8),books=books,
                short=1<<(identity[28]&15),long=1<<(identity[28]>>4),channels=identity[11],publication_bytes=40)
            need(all(0<=book<total_books for book in books),'Actual source book bounds')
            rows.append(row);raw_setups.append(raw)
    pairs=[[i,i+6] for i in range(6)]
    for a,b in pairs:
        for key in ('first_bit','end_bit','parse_bits','floor_bits_le_hex','total_books','order','rate','barkmap',
                    'ampbits','ampdB','books','short','long','channels'):
            need(rows[a][key]==rows[b][key],'Exact original/equivalent floor publication source relation')
    model=dict(schema='owned-floor0-fixtures-v1',setup_sha256=SETUP,ABI_sha256=ABI,cases=rows,case_count=12,pairs=pairs,
        protocol_lines=32,publication_bytes=40,independent_fixture_reader_pending=True,
        source_scope='Metadata/raw source assembly only; mandatory independent syntax reader before SDK')
    digest=sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())
    contract=dict(model=model,contract_sha256=digest)
    header=['/* Frozen original raw setup arrays; expectations require independent runtime syntax verification. */',
        '#pragma once','#include <stddef.h>','#include <stdint.h>',
        f'#define UNIT_CONTRACT_SHA256 "{digest}"','#define UNIT_CASE_COUNT 12','#define UNIT_PAIR_COUNT 6',
        'typedef struct { const char *id,*group; const uint8_t *setup; size_t setup_bytes; uint32_t first_bit,end_bit;',
        ' int total_books,order,rate,barkmap,ampbits,ampdB,numbooks; uint8_t books[2]; int short_samples,long_samples,channels; } floor_unit_case_t;']
    for i,raw in enumerate(raw_setups):
        header.append(f'static const uint8_t floor_setup_{i:02d}[] = {{'+','.join(str(x) for x in raw)+'};')
    header.append('static const floor_unit_case_t unit_cases[UNIT_CASE_COUNT] = {')
    for i,c in enumerate(rows):
        books=c['books']+[0]*(2-len(c['books']))
        values=[f'"{c["id"]}"',f'"{c["group"]}"',f'floor_setup_{i:02d}',f'sizeof(floor_setup_{i:02d})']
        values+=list(map(str,[c['first_bit'],c['end_bit'],c['total_books'],c['order'],c['rate'],c['barkmap'],c['ampbits'],c['ampdB'],len(c['books'])]))
        values+=['{'+','.join(map(str,books))+'}',str(c['short']),str(c['long']),str(c['channels'])]
        header.append('  {'+','.join(values)+'},')
    header.append('};')
    return contract,('\n'.join(header)+'\n').encode()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-in-place',action='store_true',required=True)
    args=parser.parse_args()
    contract,header=build()
    destinations=[HERE/'fixture-contract.json',HERE/'project/main/unit_data.h',HERE/'source-assembly.json']
    need(not any(p.exists() for p in destinations),'Create-only source assembly')
    destinations[0].write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    destinations[1].write_bytes(header)
    receipt=dict(result='OWNED_FLOOR0_SOURCE_ARRAYS_ASSEMBLED',cases=12,pairs=6,prospective_protocol_lines=32,
        floor_bitspans=[c['parse_bits'] for c in contract['model']['cases']],contract_sha256=contract['contract_sha256'],
        contract_file_sha256=sha(destinations[0].read_bytes()),data_header_sha256=sha(header),
        production_parser_or_independent_reader_or_semantic_controls_executed=False,SDK_compiler_QEMU_or_unit_executed=False)
    destinations[2].write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))


if __name__=='__main__':main()
