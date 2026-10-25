"""Pure floor literal/conditional/chunk checks; execute no component or SDK."""
import ast
import copy
import importlib.util
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('floor_capture',ROOT/'tests/run-vorbis-floor-packet-qemu.py');subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
DATA='a'*64
ROWS=[]
for name in ('present0','unused0','invalid0','prefix_eop','raw','present1'):
    ROWS.append(dict(id=name,operation='raw'if name=='raw'else'packet',identification_hex='01766f72626973'+'00'*23,identification_bits=240,
        setup_hex='05766f72626973'+'00'*80,setup_bits=696,packet_hex=''if name=='raw'else'00'*32,packet_bits=0 if name=='raw'else 256,start_bit=3 if name=='prefix_eop'else 0,
        floor_index=1 if name in('raw','present1')else 0,curve_n=130 if name=='present1'else 32,raw_y=[0xffffffff,0,0xffffffff]if name=='raw'else[]))
DOCUMENT=dict(schema='native-vorbis-floor-packet-cases-v1',cases=ROWS)

def header_for(rows):
    lines=['#define FLOOR_PACKET_CASE_COUNT '+str(len(rows))]
    for i,r in enumerate(rows):
        for stem in ('identification','setup','packet'):
            if r[stem+'_hex']:lines.append('static const uint8_t floor_packet_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x%02x)'%x for x in bytes.fromhex(r[stem+'_hex']))+'};')
        if r['raw_y']:lines.append('static const uint32_t floor_packet_raw_'+str(i)+'[] = {'+','.join('UINT32_C(%d)'%x for x in r['raw_y'])+'};')
    lines.append('static const floor_packet_case_t floor_packet_cases[FLOOR_PACKET_CASE_COUNT] = {')
    for i,r in enumerate(rows):
        fields=['"'+r['id']+'"',str(2 if r['operation']=='raw'else 1)]
        for stem in ('identification','setup','packet'):fields += ['floor_packet_'+stem+'_'+str(i)if r[stem+'_hex']else'NULL',str(len(r[stem+'_hex'])//2),'UINT64_C(%d)'%r[stem+'_bits']]
        fields += ['UINT64_C(%d)'%r['start_bit'],str(r['floor_index']),str(r['curve_n']),'floor_packet_raw_'+str(i)if r['raw_y']else'NULL',str(len(r['raw_y']))]
        lines.append(' {'+','.join(fields)+'},')
    return '\n'.join(lines+['};'])+'\n'
HEADER=header_for(ROWS)

def log_for(target):
    core=1 if target=='esp32'else 0
    def event(tag,**f):return 'FLOOR_PACKET_'+tag+' '+' '.join(k+'='+str(v)for k,v in f.items())
    def chunks(kind,index,values,digits):
        out=[]
        for start in range(0,max(1,len(values)),128):
            part=values[start:start+128];out.append(event(kind,case=index,start=start,total=len(values),count=len(part),hex=''.join(part)if part else'-',core=core))
            assert not part or len(out[-1].split('hex=')[1].split()[0])==digits*len(part)
        return out
    lines=[event('BEGIN',cases=6,coordinator=0,worker=core,data=DATA),event('WORKER',core=core,priority=3,stack=16384),event('CONTROLS',checks=46,core=core)]
    for i,row in enumerate(ROWS):
        ps=-99 if i==4 else-3 if i==3 else 0;fs=-99 if i in(3,4)else-1 if i==2 else 0;rs=cs=0 if i in(4,5)else-99;gs=0 if i in(0,1)else-99
        lines.append(event('CASE',case=i,id=row['id'],operation=2 if i==4 else 1,floor_index=row['floor_index'],curve_n=row['curve_n'],prefix_status=ps,floor_status=fs,reconstruct_status=rs,curve_status=cs,gain_status=gs,gain_consistent=int(gs==0),core=core))
        if ps==0:lines.append(event('PREFIX',case=i,mode=0,blockflag=0,previous_window=0,next_window=0,mapping=0,blocksize=64,core=core))
        if fs==0:lines.append(event('STATE',case=i,floor_index=row['floor_index'],type=int(i==5),present=int(i!=1),value_count=129 if i==0 else 3 if i==5 else 0,selected_book=257 if i==0 else 3 if i==1 else 0xffffffff,
            raw_amplitude='4611686018427387905'if i==0 else'31'if i==1 else'0',amplitude_bits=63 if i==0 else 6 if i==1 else 0,amplitude_offset=255 if i in(0,1)else 0,core=core))
        lines += chunks('COEFFICIENTS',i,['80000000628000010000000100000007']*129 if i==0 else[],32)
        raw=[0xffffffff,0,0xffffffff]if i==4 else[128,128,0]if i==5 else[]
        lines += chunks('RAW',i,['%08x'%x for x in raw],8)
        final=[255,0,0]if i==4 else[128,128,128]if i==5 else[];active=[1,1,1]if i==4 else[1,1,0]if i==5 else[]
        lines += chunks('FINAL',i,['%08x'%x for x in final],8)+chunks('ACTIVE',i,['%02x'%x for x in active],2)
        indices=[255,170,85]+[0]*29 if i==4 else[128]*130 if i==5 else[];lines += chunks('INDICES',i,['%02x'%x for x in indices],2)
        if gs==0:lines.append(event('GAIN',case=i,kind=0 if i==0 else 1,log2_bits='3fe0000000000000'if i==0 else'0000000000000000',log2_exponent=3 if i==0 else 0,core=core))
        lines.append(event('END',case=i,position=(250,17,2,3,0,20)[i],end_of_packet=int(i in(1,3)),guards=1,unchanged=1,core=core))
    return '\n'.join(lines+[event('COMPLETE',cases=6,controls=46,core=core),'FLOOR_PACKET_STOP status=CAPTURED'])+'\n'

class Readback(unittest.TestCase):
    def test_complete_literal_inputs_and_conditional_operations(self):self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT),HEADER),ROWS);self.assertEqual(subject.CONTROL_COUNT,46)
    def test_missing_commas_in_bytes_raw_and_descriptors_fail(self):
        for x in (HEADER.replace('),UINT8_C',')UINT8_C',1),HEADER.replace('4294967295),UINT32_C','4294967295)UINT32_C',1),HEADER.replace('NULL,0},','NULL,0}',1)):
            self.assertNotEqual(x,HEADER)
            with self.subTest(x=x),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,x)
    def test_changed_pointers_fields_and_nonliteral_tokens_fail(self):
        for x in (HEADER.replace('floor_packet_packet_0','floor_packet_packet_1',1),HEADER.replace('4294967295','4294967294',1),HEADER.replace('UINT64_C(240)','UINT64_C(239)+1',1)):
            with self.subTest(x=x),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,x)
    def test_duplicate_arrays_counts_and_descriptors_fail(self):
        desc=[x for x in HEADER.splitlines()if x.startswith(' {')]
        for x in (HEADER.splitlines()[1]+'\n'+HEADER,'#define FLOOR_PACKET_CASE_COUNT 6\n'+HEADER,HEADER.replace(desc[0],desc[1]),HEADER.replace(desc[1]+'\n','')):
            with self.subTest(x=x),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,x)
    def test_invalid_domains_schema_and_operation_payloads_fail(self):
        for key,val in (('packet_bits',257),('curve_n',True),('start_bit',-1),('raw_y',[1]),('setup_hex','zz'),('id','bad id')):
            d=copy.deepcopy(DOCUMENT);d['cases'][0][key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):subject.validate_cases(d,HEADER)
        d=copy.deepcopy(DOCUMENT);d['schema']='other'
        with self.assertRaises(ValueError):subject.validate_cases(d,HEADER)
    def test_legacy_source_closures_include_current_five_modules(self):
        sources=set(re.findall(r'"([A-Za-z0-9_]+\.c)"',(ROOT/'idf/components/native_vorbis_numeric/CMakeLists.txt').read_text()))
        for name in ('floor0-numeric','floor0-angles','quantization','codebook','setup'):
            tree=ast.parse((ROOT/('tests/run-vorbis-'+name+'-qemu.py')).read_text(encoding='utf-8-sig'))
            values={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('PARTS','DEPENDENCIES')}
            self.assertTrue(sources<=set(values['PARTS'].values())|set(values['DEPENDENCIES']));self.assertIn('include/native_vorbis_floor_packet.h',values['DEPENDENCIES'])
class Capture(unittest.TestCase):
    def test_both_cores_present_unused_invalid_prefix_eop_and_raw(self):
        for target in ('esp32','esp32c3'):
            r=subject.validate_log('I boot\n'+log_for(target),ROWS,target,DATA);self.assertEqual((r['cases'],r['protocol_lines'],r['metadata_controls']),(6,58,46));self.assertEqual(r['rows'][0]['state']['amplitude']['raw_amplitude'],'4611686018427387905');self.assertIsNone(r['rows'][2]['state']);self.assertEqual(r['rows'][1]['position'],17);self.assertTrue(r['rows'][1]['end_of_packet']);self.assertEqual(r['rows'][4]['raw_y'][0],0xffffffff)
    def test_well_formed_wrong_values_remain_for_independent_gate(self):
        x=log_for('esp32').replace('hex=ffffffff','hex=fffffffe');self.assertEqual(subject.validate_log(x,ROWS,'esp32',DATA)['rows'][4]['raw_y'][0],0xfffffffe)
    def test_missing_reordered_duplicate_foreign_and_torn_events_fail(self):
        lines=log_for('esp32').splitlines()
        for x in (lines[:4]+lines[5:],lines[:4]+[lines[4]]+lines[4:],lines[:4]+[lines[5],lines[4]]+lines[6:],['I '+lines[0]]+lines[1:],lines[:-1],lines+['FLOOR_PACKET_OTHER value=1']):
            with self.subTest(x=x),self.assertRaises(ValueError):subject.validate_log('\n'.join(x),ROWS,'esp32',DATA)
    def test_chunk_holes_totals_lengths_and_hex_fail(self):
        x=log_for('esp32')
        for y in (x.replace('start=128','start=127'),x.replace('total=129 count=1','total=130 count=1'),x.replace('count=128','count=129'),x.replace('hex=80','hex=8g',1)):
            with self.subTest(y=y),self.assertRaises(ValueError):subject.validate_log(y,ROWS,'esp32',DATA)
    def test_wrong_core_data_guards_controls_keys_and_conditional_records_fail(self):
        x=log_for('esp32')
        for y in (x.replace('worker=1','worker=0'),x.replace(DATA,'b'*64),x.replace('guards=1','guards=0'),x.replace('checks=46','checks=45'),x.replace('priority=3','priority=3 priority=3'),x.replace('floor_status=-1','floor_status=0')):
            with self.subTest(y=y),self.assertRaises(ValueError):subject.validate_log(y,ROWS,'esp32',DATA)
    def test_nonfinite_gain_bad_exponent_cursor_and_panics_fail(self):
        x=log_for('esp32')
        for y in (x.replace('3fe0000000000000','7ff0000000000000'),x.replace('log2_exponent=3','log2_exponent=2147483648'),x.replace('position=250','position=257'),x+'Guru Meditation\n'):
            with self.subTest(y=y),self.assertRaises(ValueError):subject.validate_log(y,ROWS,'esp32',DATA)
if __name__=='__main__':unittest.main()
