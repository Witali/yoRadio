"""Independent finite setup syntax witness; no production parser/curve/PCM."""
import hashlib
import json
from pathlib import Path
from fixture_bits import Reader, prefix, need


def sha(raw):return hashlib.sha256(raw).hexdigest()


def floor_setup(raw):
    r=Reader(raw);prefix(r,5)
    total=r.take('books_minus_1',8)+1
    need(total in (3,4),'three_or_four_actual_setup_books')
    for number in range(total):
        p=f'book[{number}].'
        r.expected(p+'sync',24,0x564342)
        dim,entries=r.take(p+'dimensions',16),r.take(p+'entries',24)
        need((dim,entries)==((1,1) if number==0 else (2,4) if number==1 else (3,2)),'finite_actual_book_shape')
        r.expected(p+'ordered',1,0);r.expected(p+'sparse',1,0)
        for i in range(entries):r.expected(p+f'length_minus_1[{i}]',5,1 if number==1 else 0)
        lookup=r.take(p+'maptype',4)
        need(lookup==(0 if number==0 else 1 if number==1 else 2),'finite_actual_book_maptype')
        if lookup:
            minimum,delta=r.take(p+'minimum',32),r.take(p+'delta',32)
            bits=r.take(p+'value_bits_minus_1',4)+1
            r.expected(p+'sequence_p',1,0)
            need(bits==(1 if number==1 else 5),'finite_actual_quantization_width')
            if number>1:need(minimum in (0,0x62000001) and delta==0x62000001,'original_or_minp1_representation')
            for i in range(2 if lookup==1 else entries*dim):r.take(p+f'multiplicand[{i}]',bits)
    for name,width,value in (('times_minus_1',6,0),('time.type',16,0),('floors_minus_1',6,0),('floor.type',16,0)):
        r.expected(name,width,value)
    first=r.position
    fields={name:r.take('floor0.'+name,width) for name,width in
        (('order',8),('rate',16),('barkmap',16),('ampbits',6),('ampdB',8))}
    count=r.take('floor0.books_minus_1',4)+1
    books=[r.take(f'floor0.book[{i}]',8) for i in range(count)]
    need((fields['order'],fields['rate'],fields['barkmap'],fields['ampbits'],fields['ampdB'],books) in
         ((6,48000,64,6,60,[2]),(5,48000,128,8,60,[2,3])),'actual_original_floor_configuration')
    need(count==total-2 and all(book<total for book in books),'actual_ci_book_bounds')
    end=r.position
    need(end-first==58+8*count and end-first in (66,74),'complete_absolute_floor_header_span')
    return dict(total_books=total,first_bit=first,end_bit=end,parse_bits=end-first,books=books,**fields)


def verify_contract(contract,source_root):
    model=contract['model']
    need(contract['contract_sha256']==sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode()),'contract_model_identity')
    need(model['schema']=='owned-floor0-fixtures-v1' and len(model['cases'])==model['case_count']==12
         and model['pairs']==[[i,i+6] for i in range(6)] and model['protocol_lines']==32,'complete12_case_source_contract')
    root=Path(source_root).resolve();observations=[]
    for index,case in enumerate(model['cases']):
        path=(root/case['setup_snapshot']).resolve();identity_path=(root/case['identification_snapshot']).resolve()
        need(path.is_relative_to(root) and identity_path.is_relative_to(root),'scoped_frozen_source_inputs')
        raw,identity=path.read_bytes(),identity_path.read_bytes()
        need(sha(raw)==case['setup_sha256'] and len(raw)==case['setup_bytes']
             and sha(identity)==case['identification_sha256'],'actual_raw_setup_identification_identity')
        actual=floor_setup(raw)
        for key,value in actual.items():need(value==case[key],'published_field:'+key)
        need(len(identity)==30 and identity[:7]==b'\x01vorbis' and identity[11]==case['channels']==2
             and int.from_bytes(identity[12:16],'little')==case['rate'],'actual_source_vi_context')
        need((1<<(identity[28]&15),1<<(identity[28]>>4))==(case['short'],case['long']),'actual_source_ci_block_context')
        bits=(int.from_bytes(raw,'little')>>actual['first_bit'])&((1<<actual['parse_bits'])-1)
        need(bits.to_bytes((actual['parse_bits']+7)//8,'little').hex()==case['floor_bits_le_hex'],'actual_floor_bitspan_identity')
        observations.append(dict(case=index,id=case['id'],**actual))
    for a,b in model['pairs']:
        need(all(observations[a][key]==observations[b][key] for key in observations[a] if key not in ('case','id')),
             'actual_original_equivalent_floor_fields_equal')
    return dict(schema='owned-floor0-independent-fixture-witness-v1',result='RAW_FLOOR0_CONTRACT_WITNESSED',
        cases=12,pairs=6,floor_bitspans=[x['parse_bits'] for x in observations],observations=observations,
        actual_production_parser_or_unit_executed=False,curve_or_PCM_computed=False,full_G6_qualified=False)
