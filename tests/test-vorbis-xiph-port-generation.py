"""Pure exact-fragment generator tests. No decoder, compiler or SDK executes.

Every mutation is confined to a fresh temporary copy below this task's .build
folder. The real pinned baseline and resource-port trees stay byte-identical.
"""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import types
import unittest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'idf/components/native_vorbis_xiph'
PORT=ROOT/'idf/components/native_vorbis_xiph_port'
GENERATOR=PORT/'prepare.py'
GENERATOR_SHA='873472c0a30c955fa5d81528195ef71e4f476915b1ac8b64dd1d04dbae7f0251'
BASE_SHA='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT_SHA='400e4c3f3b01fec11d7d051d3a0cef62cc7e0528eb71962bd6e015ab8bf95355'

def sha(body):return hashlib.sha256(body).hexdigest()
def files(root):return {p.relative_to(root).as_posix():p.read_bytes()for p in root.rglob('*')if p.is_file()}

# Reading definitions this way creates no __pycache__ inside the strict input
# inventory, even when a caller forgets Python's -B option.
body=GENERATOR.read_bytes()
if sha(body)!=GENERATOR_SHA:raise RuntimeError('Reviewed generator source changed')
subject=types.ModuleType('owned_xiph_port_generator_under_test')
subject.__file__=str(GENERATOR)
exec(compile(body,str(GENERATOR),'exec'),subject.__dict__)


class PortGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=files(BASE);cls.port=files(PORT)
        if sha(cls.baseline['component-manifest.json'])!=BASE_SHA or sha(cls.port['port-manifest.json'])!=PORT_SHA:raise RuntimeError('Reviewed input manifests changed')

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='xiph-port-generator-unit-',dir=ROOT/'.build')
        self.root=Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to((ROOT/'.build').resolve()))
        self.upstream=self.root/'upstream';self.port_copy=self.root/'port';self.output=self.root/'generated'
        shutil.copytree(BASE,self.upstream,symlinks=True);shutil.copytree(PORT,self.port_copy,symlinks=True)

    def tearDown(self):
        try:
            self.assertEqual(files(BASE),self.baseline,'Real baseline input bytes changed')
            self.assertEqual(files(PORT),self.port,'Real port input bytes changed')
        finally:self.temporary.cleanup()

    def generate(self):return subject.materialize(self.upstream,self.port_copy,self.output)
    def reseal_port(self):
        path=self.port_copy/'port-manifest.json';manifest=json.loads(path.read_bytes())
        manifest['files']={name:sha(value)for name,value in files(self.port_copy).items()if name!='port-manifest.json'}
        path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

    def test_complete_exact_thirty_three_edit_eleven_unit_and_private_headers_output(self):
        upstream_before=files(self.upstream);port_before=files(self.port_copy);record=self.generate();result=files(self.output)
        self.assertEqual(len(upstream_before),116)
        self.assertEqual({name[5:]:value for name,value in result.items()if name.startswith('base/')},upstream_before)
        expected_ports={'ported/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info','bitwise','mdct','synthesis')}
        private_headers=('native_vorbis_xiph_header_error.h','native_vorbis_xiph_dsp_error.h','native_vorbis_xiph_comment_error.h','native_vorbis_xiph_packet_error.h')
        expected_ports.update('ported/'+name for name in private_headers)
        self.assertEqual({name for name in result if name.startswith('ported/')},expected_ports)
        self.assertEqual(len(result),132);self.assertEqual(json.loads(result['PORTING.json']),record)
        for name in private_headers:self.assertEqual(result['ported/'+name],port_before['include/'+name])
        self.assertEqual(record['base_manifest_sha256'],BASE_SHA);self.assertEqual(record['port_manifest_sha256'],PORT_SHA)
        changes=json.loads(port_before['edits.json'])['edits'];self.assertEqual(len(changes),33);self.assertEqual(len(record['edits']),33)
        # Independently splice the declared fragments at their unique split;
        # verify complete result bodies and every before/after identity.
        expected={}
        for change,applied in zip(changes,record['edits']):
            original=expected.get(change['source'],upstream_before[change['source']]);before=port_before[change['before']];after=port_before[change['after']]
            prefix,found,suffix=original.partition(before)
            self.assertEqual(found,before);self.assertNotIn(before,suffix)
            expected[change['source']]=prefix+after+suffix
            self.assertEqual(applied,dict(source=change['source'],before=change['before'],after=change['after'],before_sha256=sha(before),after_sha256=sha(after)))
        for name,value in expected.items():self.assertEqual(result['ported/'+Path(name).name],value)
        baseline=json.loads(upstream_before['component-manifest.json']);self.assertEqual(len(record['compiled_units']),22)
        self.assertEqual([row['original']for row in record['compiled_units']],baseline['compile_sources'])
        for row in record['compiled_units']:
            expected_path='ported/'+Path(row['original']).name if row['original']in expected else'base/'+row['original']
            self.assertEqual(row['compiled'],expected_path)
        self.assertEqual(record['files'],{name:sha(value)for name,value in result.items()if name!='PORTING.json'})
        self.assertEqual(files(self.upstream),upstream_before);self.assertEqual(files(self.port_copy),port_before)

    def test_identical_reconfiguration_does_not_rewrite_files(self):
        first=self.generate();before=files(self.output);times={p.relative_to(self.output).as_posix():p.stat().st_mtime_ns for p in self.output.rglob('*')if p.is_file()}
        second=self.generate();self.assertEqual(second,first);self.assertEqual(files(self.output),before)
        self.assertEqual({p.relative_to(self.output).as_posix():p.stat().st_mtime_ns for p in self.output.rglob('*')if p.is_file()},times)

    def test_changed_base_body_is_rejected_before_output_creation(self):
        path=self.upstream/'README.md';path.write_bytes(path.read_bytes()+b'changed\n')
        with self.assertRaisesRegex(ValueError,'every source file hash'):self.generate()
        self.assertFalse(self.output.exists())

    def test_changed_base_manifest_pin_is_rejected(self):
        path=self.upstream/'component-manifest.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'pinned manifest identity'):self.generate()
        self.assertFalse(self.output.exists())

    def test_extra_base_file_is_rejected(self):
        (self.upstream/'unlisted.txt').write_bytes(b'unlisted')
        with self.assertRaisesRegex(ValueError,'exact complete file inventory'):self.generate()
        self.assertFalse(self.output.exists())

    def test_missing_base_file_is_rejected(self):
        (self.upstream/'README.md').unlink()
        with self.assertRaisesRegex(ValueError,'exact complete file inventory'):self.generate()
        self.assertFalse(self.output.exists())

    def test_extra_port_file_is_rejected(self):
        (self.port_copy/'unlisted.txt').write_bytes(b'unlisted')
        with self.assertRaisesRegex(ValueError,'exact complete file inventory'):self.generate()
        self.assertFalse(self.output.exists())

    def test_changed_port_body_without_manifest_update_is_rejected(self):
        for name in('edits/block-ripcord.after.c','include/native_vorbis_xiph_header_error.h','include/native_vorbis_xiph_comment_error.h'):
            with self.subTest(name=name):
                path=self.port_copy/name;original=path.read_bytes();path.write_bytes(original+b'changed\n')
                with self.assertRaisesRegex(ValueError,'every source file hash'):self.generate()
                self.assertFalse(self.output.exists());path.write_bytes(original)

    def test_resealed_missing_before_marker_is_rejected(self):
        (self.port_copy/'edits/block-ripcord.before.c').write_bytes(b'not a source fragment\n');self.reseal_port()
        with self.assertRaisesRegex(ValueError,'one exact original fragment'):self.generate()
        self.assertFalse(self.output.exists())

    def test_resealed_ambiguous_before_marker_is_rejected(self):
        (self.port_copy/'edits/block-ripcord.before.c').write_bytes(b' ');self.reseal_port()
        with self.assertRaisesRegex(ValueError,'one exact original fragment'):self.generate()
        self.assertFalse(self.output.exists())

    def test_resealed_wrong_edit_count_is_rejected(self):
        path=self.port_copy/'edits.json';changes=json.loads(path.read_bytes());changes['edits'].pop();path.write_text(json.dumps(changes),encoding='utf-8');self.reseal_port()
        with self.assertRaisesRegex(ValueError,'thirty-three exact reviewed edits'):self.generate()
        self.assertFalse(self.output.exists())

    def test_resealed_source_escape_is_rejected(self):
        path=self.port_copy/'edits.json';changes=json.loads(path.read_bytes());changes['edits'][0]['source']='../escape.c';path.write_text(json.dumps(changes),encoding='utf-8');self.reseal_port()
        with self.assertRaisesRegex(ValueError,'contained canonical relative path'):self.generate()
        self.assertFalse(self.output.exists());self.assertFalse((self.root/'escape.c').exists())

    def test_extra_generated_file_is_rejected_without_repair(self):
        self.generate();path=self.output/'extra.txt';path.write_bytes(b'keep this failed-state witness');before=files(self.output)
        with self.assertRaisesRegex(ValueError,'generated output differs'):self.generate()
        self.assertEqual(files(self.output),before)

    def test_changed_generated_unit_is_rejected_without_repair(self):
        self.generate()
        for name in('ported/sharedbook.c','ported/native_vorbis_xiph_header_error.h','ported/native_vorbis_xiph_comment_error.h'):
            with self.subTest(name=name):
                path=self.output/name;original=path.read_bytes();path.write_bytes(original+b'changed\n');before=files(self.output)
                with self.assertRaisesRegex(ValueError,'generated output differs'):self.generate()
                self.assertEqual(files(self.output),before);path.write_bytes(original)

    def test_changed_generated_manifest_is_rejected_without_repair(self):
        self.generate();path=self.output/'PORTING.json';path.write_bytes(path.read_bytes()+b' ');before=files(self.output)
        with self.assertRaisesRegex(ValueError,'generated output differs'):self.generate()
        self.assertEqual(files(self.output),before)

    def test_source_output_overlap_is_rejected(self):
        before_upstream=files(self.upstream);before_port=files(self.port_copy)
        for output in(self.upstream,self.port_copy,self.upstream/'generated',self.port_copy/'generated',self.root):
            with self.subTest(output=output),self.assertRaisesRegex(ValueError,'source/output separation'):subject.materialize(self.upstream,self.port_copy,output)
        with self.assertRaisesRegex(ValueError,'source/output separation'):subject.materialize(self.upstream,self.upstream,self.output)
        self.assertEqual(files(self.upstream),before_upstream);self.assertEqual(files(self.port_copy),before_port);self.assertFalse(self.output.exists())

if __name__=='__main__':unittest.main()
