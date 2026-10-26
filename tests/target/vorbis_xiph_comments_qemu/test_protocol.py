"""Pure metadata protocol/source-selection checks; no SDK or test executable."""
import ast
import copy
from pathlib import Path
import types
import unittest

ROOT=Path(__file__).resolve().parents[3]
CONTROLLER=ROOT/'tests/run-vorbis-xiph-comments-qemu.py'
subject=types.ModuleType('metadata_controller_under_test');subject.__file__=str(CONTROLLER)
exec(compile(CONTROLLER.read_bytes(),str(CONTROLLER),'exec'),subject.__dict__)
BASE,PORT,FIXTURE='a'*64,'b'*64,'c'*64

def log():
    return '\n'.join([
        'I (1) boot: metadata fixture',
        'COMMENTS_BEGIN coordinator=0 worker=1 base='+BASE+' port='+PORT+' fixture='+FIXTURE+' expected=37',
        'COMMENTS_WORKER core=1 priority=3 stack=16384',
        'COMMENTS_PASS cases=37 live=0 bytes=0 core=1 minimum_free=200000 remaining_stack=15000',
        'COMMENTS_STOP status=PASSED'])+'\n'

class MetadataProtocol(unittest.TestCase):
    def test_complete_exact_metadata_run(self):
        actual=subject.validate_log(log(),BASE,PORT,FIXTURE,37)
        self.assertEqual(actual,dict(cases=37,live=0,bytes=0,coordinator_core=0,worker_core=1,priority=3,configured_stack=16384,protocol_lines=4,minimum_free=200000,remaining_stack=15000))

    def test_wrong_count_identity_ownership_core_and_extra_fields_fail(self):
        original=log()
        for changed in(original.replace('cases=37','cases=38'),original.replace('live=0','live=1'),
                        original.replace('bytes=0','bytes=1'),original.replace('core=1','core=0'),
                        original.replace(BASE,'d'*64),original.replace(PORT,'d'*64),original.replace(FIXTURE,'d'*64),
                        original.replace('status=PASSED','status=FAILED'),original.replace('live=0','live=0 live=0'),
                        original.replace('stack=16384','stack=32768'),original.replace('minimum_free=200000','minimum_free=0'),
                        original.replace('remaining_stack=15000','remaining_stack=16385')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,BASE,PORT,FIXTURE,37)
        for count in(0,-1,True):
            with self.subTest(count=count),self.assertRaises(ValueError):subject.validate_log(original,BASE,PORT,FIXTURE,count)

    def test_missing_duplicate_reordered_and_torn_events_fail(self):
        lines=log().splitlines()
        for changed in(lines[:2]+lines[3:],lines+[lines[-1]],lines[:2]+[lines[3],lines[2]]+lines[4:],
                       lines[:2]+['I (2) '+lines[2]]+lines[3:],lines+['COMMENTS_UNKNOWN value=1']):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log('\n'.join(changed),BASE,PORT,FIXTURE,37)

    def test_runtime_diagnostics_are_never_filtered(self):
        for message in('Task watchdog got triggered','Guru Meditation','Backtrace:','CORRUPT HEAP','assert failed','stack overflow','timed out'):
            with self.subTest(message=message),self.assertRaisesRegex(ValueError,'native diagnostic'):
                subject.validate_log(log()+message+'\n',BASE,PORT,FIXTURE,37)

    def test_exact_twenty_five_compilation_rows(self):
        folder=(ROOT/'.build/metadata-protocol-virtual').resolve();generated=folder/'generated'
        fixtures=[('fixture',folder/'main.c'),('vorbis_xiph_alloc.c',folder/'vorbis_xiph_alloc.c'),('vorbis_xiph_comments.c',folder/'vorbis_xiph_comments.c')]
        units=['upstream/libvorbis/lib/'+name+'.c'for name in subject.VORBIS_UNITS]+['upstream/libogg/src/bitwise.c','upstream/libogg/src/framing.c']
        porting=dict(compiled_units=[dict(original=name,compiled=('ported/'+Path(name).name if name in subject.PORTED_UNITS else'base/'+name))for name in units])
        sources=fixtures+[(row['original'],generated/row['compiled'])for row in porting['compiled_units']]
        database=[dict(file=str(path),command='pure-fixture-only',output=str(index)+'.o')for index,(_,path)in enumerate(sources)]
        selected=subject.validate_compile_sources(database,fixtures,porting,generated)
        self.assertEqual(len(selected),25);self.assertEqual(set(selected),{name for name,_ in sources})
        for changed in(database[:-1],database+[database[-1]],database[1:]):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_compile_sources(changed,fixtures,porting,generated)
        with self.assertRaises(ValueError):subject.validate_compile_sources(database,fixtures[:-1],porting,generated)
        changed=copy.deepcopy(porting);changed['compiled_units'][0]['compiled']='base/'+changed['compiled_units'][0]['original']
        with self.assertRaises(ValueError):subject.validate_compile_sources(database,fixtures,changed,generated)

    def test_scope_does_not_execute_decoding_or_change_scheduling(self):
        source=(ROOT/'tests/target/vorbis_xiph_comments_qemu/main/main.c').read_text()
        self.assertNotRegex(source,r'\b(?:vorbis_synthesis\w*|vorbis_dsp_clear|xiph_dsp_tests|xiph_header_tests|vTaskDelay|taskYIELD|esp_task_wdt_delete)\s*\(')
        self.assertIn('xiph_comment_tests()',source)
        tree=ast.parse(CONTROLLER.read_text());self.assertTrue(any(isinstance(node,ast.FunctionDef)and node.name=='validate_log'for node in tree.body))
        self.assertIn('native diagnostic rejects metadata qualification',CONTROLLER.read_text())

if __name__=='__main__':unittest.main()
