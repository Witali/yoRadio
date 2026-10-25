"""Pure residue literal/conditional/chunk checks; execute no component or SDK."""
import ast
import copy
import importlib.util
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('residue_capture',ROOT/'tests/run-vorbis-residue-qemu.py');subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
DATA='a'*64
ROWS=[dict(id=name,identification_hex='01766f72626973'+'00'*23,identification_bits=240,setup_hex='05766f72626973'+'00'*80,setup_bits=696,
    packet_hex='00'*32,packet_bits=256,start_bit=3 if name=='invalid'else 0,initial_eop=name=='sticky',mapping=0,bins=65 if name=='normal'else 0 if name=='measure_bad'else 32,floor_present=[1,1])for name in ('normal','partial','invalid','zero','measure_bad','sticky')]
DOCUMENT=dict(schema='native-vorbis-residue-cases-v1',cases=ROWS)

def header_for(rows):
    lines=['#define RESIDUE_CASE_COUNT '+str(len(rows))]
    for i,r in enumerate(rows):
        for stem in ('identification','setup','packet','flags'):
            values=r['floor_present']if stem=='flags'else list(bytes.fromhex(r[stem+'_hex']))
            if values:lines.append('static const uint8_t residue_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x%02x)'%x for x in values)+'};')
    lines.append('static const residue_case_t residue_cases[RESIDUE_CASE_COUNT] = {')
    for i,r in enumerate(rows):
        fields=['"'+r['id']+'"']
        for stem in ('identification','setup','packet'):fields += ['residue_'+stem+'_'+str(i)if r[stem+'_hex']else'NULL',str(len(r[stem+'_hex'])//2),'UINT64_C(%d)'%r[stem+'_bits']]
        fields += ['UINT64_C(%d)'%r['start_bit'],str(int(r['initial_eop'])),str(r['mapping']),str(r['bins']),'residue_flags_'+str(i)if r['floor_present']else'NULL',str(len(r['floor_present']))]
        lines.append(' {'+','.join(fields)+'},')
    return '\n'.join(lines+['};'])+'\n'
HEADER=header_for(ROWS)

def log_for(target):
    core=1 if target=='esp32'else 0
    def event(tag,**fields):return 'RESIDUE_'+tag+' '+' '.join(k+'='+str(v)for k,v in fields.items())
    def chunks(tag,index,values):
        return [event(tag,case=index,start=start,total=len(values),count=len(values[start:start+128]),hex=''.join('%08x'%v for v in values[start:start+128])if values else'-',core=core)for start in range(0,max(1,len(values)),128)]
    lines=[event('BEGIN',cases=6,coordinator=0,worker=core,data=DATA),event('WORKER',core=core,priority=3,stack=16384),event('CONTROLS',checks=37,core=core)]
    for i,row in enumerate(ROWS):
        ms=-1 if i==4 else 0;ps=-99 if i==4 else-1 if i==2 else 0;cs=0 if ps==0 else-99
        lines.append(event('CASE',case=i,id=row['id'],mapping=0,bins=row['bins'],measure_status=ms,packet_status=ps,coupling_status=cs,core=core))
        count=0
        if ms==0:
            limbs=2 if i==0 else 0 if i==3 else 1;channels=1 if i==0 else 2;count=channels*row['bins']*limbs
            lines.append(event('LAYOUT',case=i,mapping=0,bins=row['bins'],channels=channels,limbs=limbs,magnitude_bits=32 if i==0 else 0 if i==3 else 6,exponent=-788 if i==0 else 0,sample_count=channels*row['bins'],limb_count=count,classification_count=8,core=core))
        if ps==0:lines.append(event('STATE',case=i,classwords=0 if i==5 else 2,vectors=0 if i==5 else 1,values=0 if i==5 else 1,stopped_on_eop=int(i==1),core=core))
        values=[1,0xffffffff]+[0]*(count-2)if ps==0 and count else[];lines += chunks('DECODED',i,values)+chunks('COUPLED',i,values)
        lines.append(event('END',case=i,position=(12,3,3,5,0,0)[i],end_of_packet=int(i in(1,5)),guards=1,unchanged=1,core=core))
    return '\n'.join(lines+[event('COMPLETE',cases=6,controls=37,core=core),'RESIDUE_STOP status=CAPTURED'])+'\n'

class Readback(unittest.TestCase):
    def test_complete_literal_inputs_and_boolean_cursor(self):self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT),HEADER),ROWS);self.assertEqual(subject.CONTROL_COUNT,37)
    def test_missing_byte_flag_and_descriptor_commas_fail(self):
        for text in (HEADER.replace('),UINT8_C',')UINT8_C',1),HEADER.replace('0x01),UINT8_C(0x01)','0x01)UINT8_C(0x01)',1),HEADER.replace(',2},',',2}',1)):
            self.assertNotEqual(text,HEADER)
            with self.subTest(text=text),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,text)
    def test_changed_pointers_fields_and_nonliteral_tokens_fail(self):
        for text in (HEADER.replace('residue_packet_0','residue_packet_1',1),HEADER.replace('UINT64_C(240)','UINT64_C(239)+1',1),HEADER.replace('UINT8_C(0x01)','UINT8_C(0x02)',1)):
            with self.subTest(text=text),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,text)
    def test_duplicate_arrays_counts_and_descriptors_fail(self):
        descriptors=[line for line in HEADER.splitlines()if line.startswith(' {')]
        for text in (HEADER.splitlines()[1]+'\n'+HEADER,'#define RESIDUE_CASE_COUNT 6\n'+HEADER,HEADER.replace(descriptors[0],descriptors[1]),HEADER.replace(descriptors[1]+'\n','')):
            with self.subTest(text=text),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,text)
    def test_invalid_schema_extents_and_caller_types_fail(self):
        for key,value in (('packet_bits',257),('bins',True),('start_bit',257),('initial_eop',1),('floor_present',[True]),('setup_hex','zz'),('id','bad id')):
            document=copy.deepcopy(DOCUMENT);document['cases'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):subject.validate_cases(document,HEADER)
        document=copy.deepcopy(DOCUMENT);document['schema']='other'
        with self.assertRaises(ValueError):subject.validate_cases(document,HEADER)
    def test_legacy_launchers_capture_current_six_source_closure(self):
        sources=set(re.findall(r'"([A-Za-z0-9_]+\.c)"',(ROOT/'idf/components/native_vorbis_numeric/CMakeLists.txt').read_text()))
        for name in ('floor0-numeric','floor0-angles','quantization','codebook','setup','floor-packet'):
            tree=ast.parse((ROOT/('tests/run-vorbis-'+name+'-qemu.py')).read_text(encoding='utf-8-sig'))
            values={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('PARTS','DEPENDENCIES')}
            self.assertTrue(sources<=set(values['PARTS'].values())|set(values['DEPENDENCIES']));self.assertIn('include/native_vorbis_residue.h',values['DEPENDENCIES'])

class Capture(unittest.TestCase):
    def test_both_cores_partial_invalid_zero_width_and_sticky(self):
        for target in ('esp32','esp32c3'):
            result=subject.validate_log('I boot\n'+log_for(target),ROWS,target,DATA);self.assertEqual((result['cases'],result['metadata_controls']),(6,37));self.assertEqual(len(result['rows'][0]['decoded_limbs']),130);self.assertEqual(result['rows'][1]['state']['stopped_on_eop'],1);self.assertIsNone(result['rows'][2]['state']);self.assertEqual(result['rows'][3]['decoded_limbs'],[]);self.assertIsNone(result['rows'][4]['layout']);self.assertFalse(result['rows'][5]['state']['stopped_on_eop'])
    def test_well_formed_wrong_limb_is_retained_for_independent_gate(self):self.assertEqual(subject.validate_log(log_for('esp32').replace('hex=00000001','hex=00000002'),ROWS,'esp32',DATA)['rows'][0]['decoded_limbs'][0],2)
    def test_missing_reordered_duplicate_foreign_and_torn_events_fail(self):
        lines=log_for('esp32').splitlines()
        for text in (lines[:4]+lines[5:],lines[:4]+[lines[4]]+lines[4:],lines[:4]+[lines[5],lines[4]]+lines[6:],['I '+lines[0]]+lines[1:],lines[:-1],lines+['RESIDUE_OTHER value=1']):
            with self.subTest(text=text),self.assertRaises(ValueError):subject.validate_log('\n'.join(text),ROWS,'esp32',DATA)
    def test_chunk_holes_totals_counts_and_hex_fail(self):
        text=log_for('esp32')
        for changed in (text.replace('start=128','start=127'),text.replace('total=130 count=2','total=131 count=2'),text.replace('count=128','count=129'),text.replace('hex=00000001','hex=0000000g',1)):
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)
    def test_wrong_core_data_guards_controls_and_conditional_state_fail(self):
        text=log_for('esp32')
        for changed in (text.replace('worker=1','worker=0'),text.replace(DATA,'b'*64),text.replace('guards=1','guards=0'),text.replace('checks=37','checks=36'),text.replace('priority=3','priority=3 priority=3'),text.replace('packet_status=-1','packet_status=0')):
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)
    def test_bad_grid_exponent_cursor_eop_and_panics_fail(self):
        text=log_for('esp32')
        for changed in (text.replace('exponent=-788','exponent=-0'),text.replace('exponent=-788','exponent=2147483648'),text.replace('sample_count=65','sample_count=64'),text.replace('magnitude_bits=32','magnitude_bits=64'),text.replace('position=3 end_of_packet=0','position=4 end_of_packet=0'),text.replace('position=3 end_of_packet=1','position=3 end_of_packet=0'),text+'Guru Meditation\n'):
            self.assertNotEqual(changed,text)
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)
if __name__=='__main__':unittest.main()
