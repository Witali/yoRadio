"""Pure manifest/literal/capture checks; no decoder, compiler or SDK execution."""
import copy
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('xiph_capture',ROOT/'tests/run-vorbis-xiph-qemu.py');subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
DATA='a'*64
COMPONENT='b'*64
ROWS=[]
for i in range(31):
    frames=[0]+[448]*12+[580 if i<30 else 584]
    ROWS.append(dict(case=i,id='case%02d'%i,rate=48000,channels=2,short_block=1024,long_block=2048,identification_hex='01766f72626973'+'00'*23,comment_hex='03766f72626973'+'00'*7,setup_hex='05766f72626973'+'00'*73,
        audio_hex='00'*14,offsets=list(range(15)),modes=[0,1]*7,granules=[-1]+list(range(13)),frames=frames,pcm_bytes=sum(frames)*4,reference_pcm_sha256='c'*64,reference_path='reference/case%02d.s16le'%i))
DOCUMENT=dict(schema='xiph-original31-raw-v1',contract_sha256='d'*64,pcm_policy={},policy={},relations=[],cases=ROWS)

def header_for(rows):
    lines=['#define XIPH_CASE_COUNT 31','#define XIPH_TOTAL_PACKETS 434','#define XIPH_EXPECTED_PCM_BYTES 738560']
    for i,row in enumerate(rows):
        for stem in ('identification','comment','setup','audio','modes'):
            values=list(bytes.fromhex(row[stem+'_hex']))if stem!='modes'else row[stem];lines.append('static const uint8_t xiph_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x%02x)'%x for x in values)+'};')
        for stem,ctype,macro in (('offsets','uint32_t','UINT32_C'),('frames','uint32_t','UINT32_C'),('granules','int64_t','INT64_C')):
            lines.append('static const '+ctype+' xiph_'+stem+'_'+str(i)+'[] = {'+','.join(macro+'('+str(x)+')'for x in row[stem])+'};')
    lines.append('static const xiph_case_t xiph_cases[XIPH_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        values=['"'+row['id']+'"']+[str(row[k])for k in ('rate','channels','short_block','long_block')]
        for stem in ('identification','comment','setup','audio'):values+=['xiph_'+stem+'_'+str(i),str(len(row[stem+'_hex'])//2)]
        values+=['xiph_'+stem+'_'+str(i)for stem in ('offsets','modes','granules','frames')]+['14',str(row['pcm_bytes'])];lines.append(' {'+','.join(values)+'},')
    return '\n'.join(lines+['};'])+'\n'
HEADER=header_for(ROWS)

def manifest_for():
    units=['upstream/libvorbis/lib/'+name+'.c'for name in subject.VORBIS_UNITS]+['upstream/libogg/src/bitwise.c','upstream/libogg/src/framing.c']
    paths=units+['CMakeLists.txt','SOURCE.json','platform/ogg/config_types.h','upstream/libvorbis/include/vorbis/codec.h','upstream/libogg/include/ogg/ogg.h']
    return dict(schema='native-vorbis-xiph-source-v1',files={name:'e'*64 for name in paths},compile_sources=units)

def log_for():
    def event(tag,**fields):return 'XIPH_'+tag+' '+' '.join(k+'='+str(v)for k,v in fields.items())
    lines=[event('BEGIN',cases=31,coordinator=0,worker=1,data=DATA,component=COMPONENT),event('WORKER',core=1,priority=3,stack=16384),event('CONTROLS',checks=17,core=1),event('VERSION',hex=b'Xiph.Org libVorbis 1.3.7'.hex(),core=1)]
    for i,row in enumerate(ROWS):
        lines.append(event('CASE',case=i,id=row['id'],packets=14,core=1))
        for h in range(3):lines.append(event('HEADER',case=i,header=h,status=-133 if i==2 and h==2 else 0,guards=1,unchanged=1,core=1))
        si=-99 if i==2 else-1 if i==3 else 0;bi=-99 if si else-1 if i==4 else 0;lines.append(event('INIT',case=i,synthesis_status=si,block_status=bi,core=1))
        if si==0:lines.append(event('INFO',case=i,rate=48000,channels=2,short_block=1024,long_block=2048,core=1))
        for p in range(14):
            lines.append(event('PACKET_BEGIN',case=i,packet=p,granule=row['granules'][p],eos=int(p==13),core=1))
            if i==0 and p==0:
                lines.append(event('PCM',case=i,packet=p,start=0,frames=128,samples=256,hex='0100ffff'*128,guards=1,core=1))
                lines.append(event('PCM',case=i,packet=p,start=256,frames=2,samples=4,hex='0000000000000000',guards=1,core=1))
            ss=-99 if i in(2,3,4)or(i==1 and p>0)else-135 if i==1 else 0;bs=-99 if ss else 0;frames=130 if i==0 and p==0 else 0
            lines.append(event('PACKET_END',case=i,packet=p,synthesis_status=ss,blockin_status=bs,read_status=0 if frames else-99,frames=frames,guards=1,unchanged=1,core=1))
        lines.append(event('CASE_END',case=i,frames=130 if i==0 else 0,pcm_bytes=520 if i==0 else 0,api_ok=int(i not in(1,2,3,4)),free_before=50000,free_open=30000,free_after=50000,minimum_free=20000,largest_before=30000,largest_after=30000,stack_before=15000,stack_after=12000,guards=1,unchanged=1,core=1))
    return '\n'.join(lines+[event('COMPLETE',cases=31,controls=17,core=1),'XIPH_STOP status=CAPTURED'])+'\n'

class Inputs(unittest.TestCase):
    def test_complete_manifest_and_original31_literal_readback(self):self.assertEqual(subject.validate_manifest(manifest_for())['compile_sources'][-1],'upstream/libogg/src/framing.c');self.assertEqual(subject.validate_cases(DOCUMENT,HEADER),ROWS)
    def test_manifest_escape_wrong_units_and_missing_platform_fail(self):
        for kind in range(4):
            value=manifest_for()
            if kind==0:value['files']['../escape']='e'*64
            elif kind==1:value['compile_sources'][0]=value['compile_sources'][1]
            elif kind==2:del value['files']['platform/ogg/config_types.h']
            else:value['schema']='other'
            with self.subTest(kind=kind),self.assertRaises(ValueError):subject.validate_manifest(value)
    def test_missing_commas_in_all_literal_types_and_descriptors_fail(self):
        for changed in (HEADER.replace('),UINT8_C',')UINT8_C',1),HEADER.replace('),UINT32_C',')UINT32_C',1),HEADER.replace('),INT64_C',')INT64_C',1),HEADER.replace(',14,23824},',',14,23824}',1)):
            self.assertNotEqual(changed,HEADER)
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)
    def test_changed_arrays_pointers_counts_and_nonliteral_fields_fail(self):
        first=next(line for line in HEADER.splitlines()if line.startswith(' {'))
        for changed in (HEADER.splitlines()[3]+'\n'+HEADER,HEADER.replace('xiph_audio_0','xiph_audio_1',1),HEADER.replace('UINT32_C(448)','UINT32_C(447)+1',1),HEADER.replace('#define XIPH_CASE_COUNT 31','#define XIPH_CASE_COUNT 30'),HEADER.replace(first+'\n','')):
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)
    def test_bad_original_model_metadata_schema_or_reference_fail(self):
        for key,value in (('case',1),('channels',True),('offsets',[0]*15),('frames',[0]*14),('granules',[1<<63]*14),('identification_hex','00'),('reference_pcm_sha256','x'*64)):
            model=copy.deepcopy(DOCUMENT);model['cases'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):subject.validate_cases(model,HEADER)
        model=copy.deepcopy(DOCUMENT);model['cases'].pop()
        with self.assertRaises(ValueError):subject.validate_cases(model,HEADER)

class Captures(unittest.TestCase):
    def parse(self,text):return subject.validate_log(text,ROWS,'esp32',DATA,COMPONENT)
    def test_complete_ordered_capture_retains_api_errors_and_pcm(self):
        result=self.parse('I boot\n'+log_for());self.assertEqual((result['cases'],result['packets'],result['pcm_bytes']),(31,434,520));self.assertEqual(result['rows'][0]['packets'][0]['frames'],130);self.assertEqual(result['rows'][1]['packets'][0]['synthesis_status'],-135);self.assertIsNone(result['rows'][2]['info']);self.assertFalse(result['rows'][4]['api_ok'])
    def test_changed_numerical_bytes_remain_for_independent_gate(self):self.assertTrue(self.parse(log_for().replace('hex=0100ffff','hex=0200ffff'))['rows'][0]['pcm_hex'].startswith('0200ffff'))
    def test_missing_duplicate_reordered_foreign_and_torn_events_fail(self):
        lines=log_for().splitlines()
        for changed in (lines[:5]+lines[6:],lines[:5]+[lines[5]]+lines[5:],lines[:5]+[lines[6],lines[5]]+lines[7:],['I '+lines[0]]+lines[1:],lines[:-1],lines+['XIPH_OTHER value=1']):
            with self.subTest(text=changed),self.assertRaises(ValueError):self.parse('\n'.join(changed))
    def test_chunk_holes_misalignment_hex_and_totals_fail(self):
        text=log_for()
        for changed in (text.replace('start=256','start=255'),text.replace('frames=128 samples=256','frames=129 samples=256'),text.replace('samples=256','samples=255'),text.replace('hex=0100ffff','hex=0100fffg'),text.replace('pcm_bytes=520','pcm_bytes=522')):
            with self.subTest(text=changed),self.assertRaises(ValueError):self.parse(changed)
    def test_wrong_source_core_guards_control_and_duplicate_keys_fail(self):
        text=log_for()
        for changed in (text.replace(DATA,'f'*64),text.replace(COMPONENT,'f'*64),text.replace('worker=1','worker=0'),text.replace('guards=1','guards=0'),text.replace('checks=17','checks=16'),text.replace('priority=3','priority=3 priority=3'),text.replace('eos=1','eos=0')):
            with self.subTest(text=changed),self.assertRaises(ValueError):self.parse(changed)
    def test_invalid_conditional_api_version_resources_or_panics_fail(self):
        text=log_for()
        for changed in (text.replace('case=3 synthesis_status=-1 block_status=-99','case=3 synthesis_status=0 block_status=-99'),text.replace('read_status=0 frames=130','read_status=-1 frames=130'),text.replace('stack_after=12000','stack_after=16000'),text.replace('minimum_free=20000','minimum_free=-0'),text.replace(b'1.3.7'.hex(),b'1.3.6'.hex()),text+'Guru Meditation\n'):
            self.assertNotEqual(changed,text)
            with self.subTest(text=changed),self.assertRaises(ValueError):self.parse(changed)
    def test_c3_requires_a_separate_future_baseline(self):
        with self.assertRaises(ValueError):subject.validate_log(log_for(),ROWS,'esp32c3',DATA,COMPONENT)
if __name__=='__main__':unittest.main()
