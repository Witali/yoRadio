"""Pure setup literal/chunk/event tests; run no component, SDK, QEMU or oracle."""
import ast
import copy
import importlib.util
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('setup_capture',ROOT/'tests/run-vorbis-setup-qemu.py')
subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
DATA='a'*64
ROWS=[dict(id='short',identification_hex='01766f72626973'+'00'*23,identification_bits=240,setup_hex='05766f72626973'+'00'*40,setup_bits=376,audio_hex='00',audio_bits=1,audio_start=0),
      dict(id='unaligned',identification_hex='01766f72626973'+'ff'*23,identification_bits=240,setup_hex='05766f72626973'+'11'*40,setup_bits=376,audio_hex='00'*17,audio_bits=130,audio_start=129)]
DOCUMENT=dict(schema='native-vorbis-setup-cases-v1',cases=ROWS)


def header_for(rows):
    lines=['#define SETUP_CASE_COUNT '+str(len(rows))]
    for i,row in enumerate(rows):
        for stem in ('identification','setup','audio'):
            if row[stem+'_hex']:lines.append('static const uint8_t setup_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x%02x)'%x for x in bytes.fromhex(row[stem+'_hex']))+'};')
    lines.append('static const setup_case_t setup_cases[SETUP_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        fields=['"'+row['id']+'"']
        for stem in ('identification','setup','audio'):
            fields += ['setup_'+stem+'_'+str(i)if row[stem+'_hex']else'NULL',str(len(row[stem+'_hex'])//2),'UINT64_C(%d)'%row[stem+'_bits']]
        lines.append(' {'+','.join(fields+['UINT64_C(%d)'%row['audio_start']])+'},')
    return '\n'.join(lines+['};'])+'\n'
HEADER=header_for(ROWS)


def log_for(target):
    core=1 if target=='esp32'else 0
    def event(kind,**fields):return 'SETUP_'+kind+' '+' '.join(k+'='+str(v)for k,v in fields.items())
    def chunks(kind,index,values,digits,book=None):
        result=[]
        for start in range(0,max(1,len(values)),128):
            part=values[start:start+128];fields=dict(case=index)
            if book is not None:fields['book']=book
            fields.update(start=start,total=len(values),count=len(part),hex=''.join(values[start:start+128])if part else'-',core=core)
            self_width=digits*len(part);assert not part or len(fields['hex'])==self_width
            result.append(event(kind,**fields))
        return result
    lines=[event('BEGIN',cases=2,coordinator=0,worker=core,data=DATA),event('WORKER',core=core,priority=3,stack=16384),event('CONTROLS',checks=60,core=core)]
    ident=dict(zip(subject.ID,(255,0xffffffff,0,0xffffffff,0x80000000,64,8192)))
    for i,row in enumerate(ROWS):
        # Artificial raw captures test grammar only; separate exact comparison qualifies values.
        lines.append(event('CASE',case=i,id=row['id'],id_status=0,measure_status=0,materialize_status=0,audio_status=0,core=core))
        lines.append(event('IDENT',case=i,**ident,core=core))
        layout={'id_'+k:v for k,v in ident.items()};layout.update(end_bit=375,codeword_count=129,multiplicand_count=129,
            book_count=2,time_count=1,floor_count=1,residue_count=1,mapping_count=1,mode_count=1,configuration_count=129,floor_table=0,residue_table=1,mapping_table=2,mode_table=3)
        lines.append(event('LAYOUT',case=i,**layout,core=core))
        for book in (0,1):
            count=129 if book==0 else 0
            lines.append(event('BOOK',case=i,book=book,start_bit=64,used_entries=count,maximum_length=8 if count else 0,
                dimensions=1,entries=count,lookup_type=2 if count else 0,minimum_bits='80000000'if count else'00000000',delta_bits='62800001'if count else'00000000',value_bits=16 if count else 0,sequence_p=1 if count else 0,
                multiplicand_count=count,quant_start_bit=80,multiplicand_bit=100,end_bit=200,core=core))
            lines += chunks('WORDS',i,['%08x%08x%08x'%(j<<24,j,8)for j in range(count)],24,book)
            lines += chunks('MULT',i,['%04x'%j for j in range(count)],4,book)
        lines += chunks('CONFIG',i,['%08x'%j for j in range(129)],8)
        lines += chunks('GETTERS',i,['%08x'%(0xffffffff-j)for j in range(129)],8)
        lines.append(event('AUDIO',case=i,mode=0,blockflag=0,previous_window=0,next_window=0,mapping=0,blocksize=64,position=row['audio_start']+1,end_of_packet=0,core=core))
        lines.append(event('END',case=i,id_truncation_checks=0,setup_truncation_checks=0,audio_truncation_checks=0,guards=1,unchanged=1,core=core))
    return '\n'.join(lines+[event('COMPLETE',cases=2,controls=60,core=core),'SETUP_STOP status=CAPTURED'])+'\n'


class LiteralReadback(unittest.TestCase):
    def test_all_packet_bytes_and_wide_metadata_are_read_back(self):
        self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT),HEADER),ROWS)
        self.assertEqual(subject.CONTROL_COUNT,60)

    def test_missing_byte_and_descriptor_commas_fail(self):
        for changed in (HEADER.replace('),UINT8_C',')UINT8_C',1),HEADER.replace('UINT64_C(0)},','UINT64_C(0)}',1)):
            self.assertNotEqual(changed,HEADER)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_changed_pointer_extent_start_and_nonliteral_fields_fail(self):
        for changed in (HEADER.replace('setup_audio_0','setup_audio_1',1),HEADER.replace('UINT64_C(129)','UINT64_C(128)',1),
                        HEADER.replace('UINT64_C(240)','UINT64_C(239)+1',1),HEADER.replace('0x01','0x02',1)):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_duplicate_array_counts_and_reordered_descriptors_fail(self):
        first=HEADER.splitlines()[1]+'\n';descriptors=[x for x in HEADER.splitlines()if x.startswith(' {')]
        for changed in (first+HEADER,'#define SETUP_CASE_COUNT 2\n'+HEADER,HEADER.replace(descriptors[0],descriptors[1]),HEADER.replace(descriptors[1]+'\n','')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_invalid_packet_extents_capacities_and_schema_fail(self):
        for key,value in (('identification_bits',241),('setup_bits',999999),('audio_start',2),('audio_bits',True),('setup_hex','zz'),('audio_hex','00'*16385),('id','bad id')):
            data=copy.deepcopy(DOCUMENT);data['cases'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):subject.validate_cases(data,HEADER)
        data=copy.deepcopy(DOCUMENT);data['schema']='other'
        with self.assertRaises(ValueError):subject.validate_cases(data,HEADER)

    def test_legacy_dependency_closures_include_all_current_module_sources(self):
        sources=set(re.findall(r'"([A-Za-z0-9_]+\.c)"',(ROOT/'idf/components/native_vorbis_numeric/CMakeLists.txt').read_text()));self.assertTrue(sources)
        for name in ('floor0-numeric','floor0-angles','quantization','codebook'):
            tree=ast.parse((ROOT/('tests/run-vorbis-'+name+'-qemu.py')).read_text(encoding='utf-8-sig'))
            values={node.targets[0].id:ast.literal_eval(node.value)for node in tree.body if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in ('PARTS','DEPENDENCIES')}
            self.assertTrue(sources<=set(values['PARTS'].values())|set(values['DEPENDENCIES']));self.assertIn('include/native_vorbis_setup.h',values['DEPENDENCIES'])


class EventCapture(unittest.TestCase):
    def test_both_core_profiles_all_chunks_empty_arrays_and_u32_bits(self):
        for target in ('esp32','esp32c3'):
            result=subject.validate_log('I normal boot\n'+log_for(target),ROWS,target,DATA)
            self.assertEqual((result['cases'],result['protocol_lines'],result['metadata_controls']),(2,39,60))
            self.assertEqual(result['rows'][0]['identification']['sample_rate'],0xffffffff)
            self.assertEqual(len(result['rows'][0]['books'][0]['words']),129);self.assertEqual(result['rows'][0]['books'][1]['words'],[])
            self.assertEqual(result['rows'][1]['position'],130)

    def test_well_formed_wrong_raw_and_getter_values_are_retained(self):
        changed=log_for('esp32').replace('hex=ffffffff','hex=fffffffe')
        result=subject.validate_log(changed,ROWS,'esp32',DATA)
        self.assertEqual(result['rows'][0]['getter_values'][0],0xfffffffe)

    def test_missing_reordered_duplicate_foreign_and_torn_events_fail(self):
        lines=log_for('esp32').splitlines()
        for changed in (lines[:6]+lines[7:],lines[:6]+[lines[6]]+lines[6:],lines[:6]+[lines[7],lines[6]]+lines[8:],
                        ['I noise '+lines[0]]+lines[1:],lines+['SETUP_OTHER value=1'],lines[:-1]):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log('\n'.join(changed),ROWS,'esp32',DATA)

    def test_chunk_holes_totals_width_bounds_and_noncanonical_numbers_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('start=128','start=127'),log.replace('total=129 count=1','total=130 count=1'),
                        log.replace('count=128','count=129'),log.replace('hex=0080 ','hex=080 '),log.replace('maximum_length=8','maximum_length=33'),
                        log.replace('sample_rate=4294967295','sample_rate=4294967296'),log.replace('position=130','position=0130')):
            self.assertNotEqual(changed,log)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_wrong_core_data_status_guards_counters_and_duplicate_keys_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('worker=1','worker=0'),log.replace(DATA,'b'*64),log.replace('audio_status=0','audio_status=-3'),
                        log.replace('guards=1','guards=0'),log.replace('unchanged=1','unchanged=0'),log.replace('setup_truncation_checks=0','setup_truncation_checks=1'),
                        log.replace('checks=60','checks=53'),log.replace('priority=3','priority=3 priority=3')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_incomplete_shared_storage_eop_cursor_range_and_panics_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('codeword_count=129','codeword_count=128'),log.replace('multiplicand_count=129 book_count','multiplicand_count=128 book_count'),
                        log.replace('end_of_packet=0','end_of_packet=1'),log.replace('position=130','position=131'),log+'Guru Meditation\n'):
            self.assertNotEqual(changed,log)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)


if __name__=='__main__':unittest.main()
