"""Pure codebook literal/event checks; run no component, compiler, SDK or QEMU."""
import ast
import copy
import importlib.util
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('codebook_capture',ROOT/'tests/run-vorbis-codebook-qemu.py')
subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
DATA='a'*64


def setup(dim,lengths,lookup=0,start=0):
    position,packed=start,0
    def field(value,width):
        nonlocal position,packed
        packed|=value<<position;position+=width
    field(0x564342,24);field(dim,16);field(len(lengths),24);field(0,1)
    sparse=any(x==0 for x in lengths);field(int(sparse),1)
    for length in lengths:
        if sparse:field(int(length!=0),1)
        if length:field(length-1,5)
    first=position;field(lookup,4)
    if lookup:
        field(0x80000000,32);field(0x62800001,32);field(2,4);field(1,1);multiplicand_bit=position;field(7,3)
    else:multiplicand_bit=position
    layout=dict(start_bit=start,used_entries=sum(x!=0 for x in lengths),maximum_length=max(lengths,default=0),
        quantization=dict(dimensions=dim,entries=len(lengths),lookup_type=lookup,minimum_bits=0x80000000 if lookup else 0,
            delta_bits=0x62800001 if lookup else 0,value_bits=3 if lookup else 0,sequence_p=1 if lookup else 0,
            multiplicand_count=int(lookup!=0),start_bit=first,multiplicand_bit=multiplicand_bit,end_bit=position))
    return packed.to_bytes((position+7)//8,'little').hex(),position,layout


ROWS=[];LAYOUTS=[]
for name,op,dim,lengths,lookup,start,payload,payload_bits,payload_start,length in (
    ('decode','decode',0,[1,1],0,0,'10',5,3,2),('vector','vector',3,[1,1],1,5,'01',1,0,3),
    ('floor','floor',3,[1,1],1,0,'02',2,0,4),('empty','decode',0,[],0,0,'',0,0,0),
    ('declared257','decode',65535,[1]+[0]*255+[1],1,0,'03',2,0,2),('zero_prefix','vector',3,[1,1],1,0,'',0,0,0)):
    packet,bits,layout=setup(dim,lengths,lookup,start);LAYOUTS.append(layout)
    ROWS.append(dict(id=name,operation=op,packet_hex=packet,packet_bits=bits,start_bit=start,payload_hex=payload,
                     payload_bits=payload_bits,payload_start=payload_start,length=length))
DOCUMENT=dict(schema='native-vorbis-codebook-cases-v1',cases=ROWS)


def header_for(rows):
    lines=['#define CODEBOOK_CASE_COUNT '+str(len(rows))]
    for i,row in enumerate(rows):
        for prefix,key in (('codebook_packet_','packet_hex'),('codebook_payload_','payload_hex')):
            if row[key]:lines.append('static const uint8_t '+prefix+str(i)+'[] = {'+','.join('UINT8_C(0x%02x)'%x for x in bytes.fromhex(row[key]))+'};')
    lines.append('static const codebook_case_t codebook_cases[CODEBOOK_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        pointer=lambda prefix,present:prefix+str(i) if present else 'NULL'
        fields=['"'+row['id']+'"',str({'decode':1,'vector':2,'floor':3}[row['operation']]),pointer('codebook_packet_',row['packet_hex']),str(len(row['packet_hex'])//2),
                'UINT64_C(%d)'%row['packet_bits'],'UINT64_C(%d)'%row['start_bit'],pointer('codebook_payload_',row['payload_hex']),str(len(row['payload_hex'])//2),
                'UINT64_C(%d)'%row['payload_bits'],'UINT64_C(%d)'%row['payload_start'],str(row['length'])]
        lines.append(' {'+','.join(fields)+'},')
    return '\n'.join(lines+['};'])+'\n'


HEADER=header_for(ROWS)


def log_for(target):
    core=1 if target=='esp32' else 0
    def event(kind,**fields):return 'CODEBOOK_'+kind+' '+' '.join(k+'='+str(v) for k,v in fields.items())
    lines=[event('BEGIN',cases=6,coordinator=0,worker=core,data=DATA),event('WORKER',core=core,priority=3,stack=16384),
           event('CONTROLS',checks=subject.CONTROL_COUNT,core=core)]
    for i,(row,layout) in enumerate(zip(ROWS,LAYOUTS)):
        q=layout['quantization'];count=row['length'] if row['operation']=='decode' else int(row['length']>0) if row['operation']=='vector' else (row['length']-1)//q['dimensions']+1
        lines.append(event('CASE',case=i,id=row['id'],operation={'decode':1,'vector':2,'floor':3}[row['operation']],length=row['length'],measure_status=0,materialize_status=0,operation_status=0,core=core))
        fields=dict(start_bit=layout['start_bit'],used_entries=layout['used_entries'],maximum_length=layout['maximum_length'])
        fields.update({('quant_start_bit' if k=='start_bit' else k):('%08x'%v if k in ('minimum_bits','delta_bits') else v) for k,v in q.items()})
        lines.append(event('LAYOUT',case=i,**fields,core=core))
        words='-' if not layout['used_entries'] else '00000000000000000000000180000000'+('%08x'%(256 if i==4 else 1))+'00000001'
        lines.append(event('WORDS',case=i,count=layout['used_entries'],hex=words,core=core))
        lines.append(event('MULT',case=i,count=q['multiplicand_count'],hex='0007' if q['multiplicand_count'] else '-',core=core))
        decoded=''.join('%08x%016x'%(256 if i==4 else step%2,row['payload_start']+step+1) for step in range(count))
        lines.append(event('DECODED',case=i,count=count,hex=decoded or '-',core=core))
        value_count=0 if row['operation']=='decode' else row['length']
        lines.append(event('VALUES',case=i,count=value_count,hex='80000000628000010000000100000007'*value_count if value_count else '-',core=core))
        lines.append(event('END',case=i,position=row['payload_start']+count,end_of_packet=0,truncation_checks=0,payload_truncation_checks=0,guards=1,unchanged=1,core=core))
    return '\n'.join(lines+[event('COMPLETE',cases=6,controls=subject.CONTROL_COUNT,core=core),'CODEBOOK_STOP status=CAPTURED'])+'\n'


class LiteralReadback(unittest.TestCase):
    def test_three_operations_empty_book_and_large_declared_metadata(self):
        self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT),HEADER),ROWS)
        self.assertEqual(LAYOUTS[4]['quantization']['entries'],257)
        self.assertEqual(LAYOUTS[4]['used_entries'],2)

    def test_missing_byte_and_descriptor_commas_fail(self):
        for changed in (HEADER.replace('),UINT8_C',')UINT8_C',1),HEADER.replace('UINT64_C(3),2},','UINT64_C(3),2}',1)):
            self.assertNotEqual(changed,HEADER)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_setup_payload_pointers_start_length_and_bytes_are_bound(self):
        for changed in (HEADER.replace('0x42','0x43',1),HEADER.replace('codebook_payload_0','codebook_payload_1',1),
                        HEADER.replace('UINT64_C(5),UINT64_C(3),2','UINT64_C(5),UINT64_C(2),2',1),HEADER.replace('UINT64_C(3),2}','UINT64_C(3),1}',1)):
            self.assertNotEqual(changed,HEADER)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_duplicate_arrays_counts_nonliteral_and_reordered_rows_fail(self):
        first=HEADER.splitlines()[1]+'\n';descriptors=[x for x in HEADER.splitlines() if x.startswith(' {')]
        for changed in (first+HEADER,'#define CODEBOOK_CASE_COUNT 6\n'+HEADER,HEADER.replace('UINT64_C(5)','UINT64_C(4)+1',1),
                        HEADER.replace(descriptors[0],descriptors[1]),HEADER.replace(descriptors[1]+'\n','')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_invalid_extent_capacity_id_schema_operation_and_sync_fail(self):
        for key,value in (('packet_bits',100000),('start_bit',100000),('payload_start',6),('payload_bits',9),('length',256),
                          ('length',True),('packet_hex','zz'),('operation','other'),('id','bad id')):
            document=copy.deepcopy(DOCUMENT);document['cases'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):subject.validate_cases(document,HEADER)
        document=copy.deepcopy(DOCUMENT);document['schema']='other'
        with self.assertRaises(ValueError):subject.validate_cases(document,HEADER)
        document=copy.deepcopy(DOCUMENT);document['cases'][0]['packet_hex']='43'+document['cases'][0]['packet_hex'][2:]
        with self.assertRaises(ValueError):subject.validate_cases(document,header_for(document['cases']))

    def test_legacy_runners_freeze_all_current_component_source_dependencies(self):
        cmake=(ROOT/'idf/components/native_vorbis_numeric/CMakeLists.txt').read_text()
        sources=set(re.findall(r'"([A-Za-z0-9_]+\.c)"',cmake));self.assertTrue(sources)
        for name in ('floor0-numeric','floor0-angles','quantization'):
            tree=ast.parse((ROOT/('tests/run-vorbis-'+name+'-qemu.py')).read_text(encoding='utf-8-sig'))
            values={node.targets[0].id:ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and
                    len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('PARTS','DEPENDENCIES')}
            self.assertTrue(sources<=set(values['PARTS'].values())|set(values['DEPENDENCIES']))
            self.assertIn('include/native_vorbis_codebook.h',values['DEPENDENCIES'])


class EventCapture(unittest.TestCase):
    def test_native_cores_mixed_shapes_empty_arrays_and_exact_sparse_index(self):
        self.assertEqual(subject.CONTROL_COUNT,719)
        for target in ('esp32','esp32c3'):
            result=subject.validate_log('I normal boot\n'+log_for(target),ROWS,target,DATA)
            self.assertEqual((result['cases'],result['protocol_lines'],result['metadata_controls']),(6,47,subject.CONTROL_COUNT))
            self.assertEqual(result['rows'][3]['words'],[]);self.assertEqual(result['rows'][4]['words'][1]['entry'],256)
            self.assertEqual(result['rows'][5]['decoded'],[]);self.assertEqual(result['rows'][5]['position'],0)

    def test_well_formed_wrong_exact_values_remain_for_independent_checker(self):
        changed=log_for('esp32').replace('hex=0007','hex=0006').replace('62800001','62800002')
        result=subject.validate_log(changed,ROWS,'esp32',DATA)
        self.assertEqual(result['rows'][1]['multiplicands'],[6]);self.assertEqual(result['rows'][1]['values'][0]['delta_bits'],0x62800002)

    def test_missing_duplicate_reordered_foreign_torn_or_extra_events_fail(self):
        lines=log_for('esp32').splitlines()
        for changed in (lines[:4]+lines[5:],lines[:4]+[lines[4]]+lines[4:],lines[:4]+[lines[5],lines[4]]+lines[6:],
                        ['I noise '+lines[0]]+lines[1:],lines+['CODEBOOK_OTHER value=1'],lines[:-1]):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log('\n'.join(changed),ROWS,'esp32',DATA)

    def test_core_data_status_guards_controls_or_duplicate_keys_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('worker=1','worker=0'),log.replace(DATA,'b'*64),log.replace('operation_status=0','operation_status=-3'),
                        log.replace('guards=1','guards=0'),log.replace('unchanged=1','unchanged=0'),log.replace('checks='+str(subject.CONTROL_COUNT),'checks=99999'),
                        log.replace('priority=3','priority=3 priority=3')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_hex_counts_layout_bounds_and_canonical_numbers_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('hex=0007','hex=007'),log.replace('count=1 hex=0007','count=2 hex=0007'),
                        log.replace('used_entries=2','used_entries=256'),log.replace('maximum_length=1','maximum_length=33'),
                        log.replace('minimum_bits=80000000','minimum_bits=8000000g'),log.replace('entries=2 ','entries=-2 '),
                        log.replace('position=5','position=05'),log.replace('hex=0007','hex=000G')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_cursor_progression_eop_truncation_claim_and_panics_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('position=5','position=4'),log.replace('end_of_packet=0','end_of_packet=1'),
                        log.replace('truncation_checks=0','truncation_checks=1'),log.replace('payload_truncation_checks=0','payload_truncation_checks=1'),
                        log.replace('0000000000000004','0000000000000006'),log+'Guru Meditation\n'):
            self.assertNotEqual(changed,log)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)


if __name__=='__main__':unittest.main()
