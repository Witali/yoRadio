"""Pure resource/source-binding checks; no SDK, compiler or decoder runs."""
import ast
import copy
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('port_capture',ROOT/'tests/run-vorbis-xiph-port-qemu.py');subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
BASE='a'*64
PORT='b'*64
ROWS=[dict(id='case%02d'%i)for i in range(31)]
BOOKS=123
BITS=456

@contextmanager
def workspace_temporary():
    workspace=ROOT.resolve();base=(workspace/'.build').resolve();prefix='xiph-port-protocol-'
    if base.parent!=workspace or base.name!='.build':raise ValueError('task-local temporary root')
    base.mkdir(exist_ok=True)
    folder=Path(tempfile.mkdtemp(dir=base,prefix=prefix)).resolve()
    try:
        if folder.parent!=base or not folder.name.startswith(prefix):raise ValueError('contained fresh temporary directory')
        yield folder
    finally:
        target=folder.resolve()
        if target.parent!=base or not target.is_relative_to(base)or not target.name.startswith(prefix):raise ValueError('contained temporary cleanup target')
        shutil.rmtree(target)

def resource_log():
    def record(**fields):return 'PORT_RESOURCE '+' '.join(k+'='+str(v)for k,v in dict(fields,live=0,bytes=0,core=1).items())
    lines=['XIPH_WORKER core=1 priority=3 stack=16384',record(phase='arena_before',base=BASE,port=PORT),record(phase='arena_after',checks=11),record(phase='books_before'),record(phase='books_after',checks=BOOKS),record(phase='bits_before'),record(phase='bits_after',checks=BITS),'XIPH_CONTROLS checks=17 core=1']
    for i in range(31):lines+=['XIPH_CASE case='+str(i)+' id=case%02d'%i,'XIPH_CASE_END case='+str(i)+' guards=1',record(phase='case',case=i)]
    return '\n'.join(lines+[record(phase='complete'),'XIPH_COMPLETE cases=31 controls=17 core=1'])+'\n'

def source_fixture(folder):
    base_root,port_root,generated=folder/'base',folder/'port',folder/'generated';base_root.mkdir();port_root.mkdir();generated.mkdir()
    units=['upstream/libvorbis/lib/'+name+'.c'for name in subject.VORBIS_UNITS]+['upstream/libogg/src/bitwise.c','upstream/libogg/src/framing.c']
    sources=['upstream/libvorbis/lib/block.c']+['upstream/libvorbis/lib/sharedbook.c']*3+['upstream/libogg/src/bitwise.c']*4
    original={name:('// '+name+'\n').encode()for name in units};port_bodies={'CMakeLists.txt':b'# test only\n','prepare.py':b'# no execution\n'};changes=[]
    for i,source in enumerate(sources):
        before,after=('before_'+str(i)+'\n').encode(),('after_'+str(i)+'\n').encode();original[source]+=before;before_name='edits/'+str(i)+'.before.c';after_name='edits/'+str(i)+'.after.c';port_bodies[before_name]=before;port_bodies[after_name]=after;changes.append(dict(source=source,before=before_name,after=after_name))
    def digest(body):return hashlib.sha256(body).hexdigest()
    base=dict(files={name:digest(body)for name,body in original.items()},compile_sources=units)
    original['component-manifest.json']=(json.dumps(base,sort_keys=True)+'\n').encode();port_bodies['edits.json']=(json.dumps(dict(schema='native-vorbis-xiph-exact-edits-v1',edits=changes))+'\n').encode()
    port=dict(schema='native-vorbis-xiph-resource-port-v1',base_manifest_sha256=BASE,files={name:digest(body)for name,body in port_bodies.items()})
    for root,bodies in ((base_root,original),(port_root,port_bodies)):
        for name,body in bodies.items():path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    modified={source:original[source]for source in set(sources)};applied=[]
    for change in changes:
        before,after=port_bodies[change['before']],port_bodies[change['after']];modified[change['source']]=modified[change['source']].replace(before,after)
        applied.append(dict(change,before_sha256=digest(before),after_sha256=digest(after)))
    bodies={'base/'+name:body for name,body in original.items()};bodies.update({'ported/'+Path(name).name:body for name,body in modified.items()})
    compiled=[dict(original=name,compiled='ported/'+Path(name).name if name in modified else'base/'+name)for name in units]
    record=dict(schema='native-vorbis-xiph-generated-port-v1',base_manifest_sha256=BASE,port_manifest_sha256=PORT,edits=applied,compiled_units=compiled,files={name:digest(body)for name,body in sorted(bodies.items())})
    for name,body in bodies.items():path=generated/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    path=generated/'PORTING.json';path.write_bytes((json.dumps(record,indent=2,sort_keys=True)+'\n').encode());return path,base,port,base_root,port_root

class Protocol(unittest.TestCase):
    def test_original_reader_ast_and_raw_caller_are_unchanged(self):
        old=ast.parse((ROOT/'tests/run-vorbis-xiph-qemu.py').read_text());new=ast.parse((ROOT/'tests/run-vorbis-xiph-port-qemu.py').read_text())
        for name in ('need','sha','normalize','sequence','validate_manifest','validate_cases','validate_log'):
            definitions=[[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name]for tree in (old,new)];self.assertEqual(ast.dump(definitions[0][0],include_attributes=False),ast.dump(definitions[1][0],include_attributes=False))
        baseline=(ROOT/'tests/target/vorbis_xiph_qemu/main/main.c').read_text();ported=(ROOT/'tests/target/vorbis_xiph_port_qemu/main/main.c').read_text()
        for begin,end,new_end in (('static int convert(','static void controls(','static void controls('),('static void capture(','static void worker(','static void port_resource_tests(')):
            self.assertEqual(baseline[baseline.index(begin):baseline.index(end)],ported[ported.index(begin):ported.index(new_end)])
    def test_complete_resource_sequence_binds_all_case_cleanup(self):
        value=subject.validate_resource_log(resource_log(),ROWS,BASE,PORT,BOOKS,BITS);self.assertEqual((value['records'],value['arena_checks'],value['per_case_zero_live']),(38,11,31))
        self.assertFalse(any('XIPH_'in line for line in resource_log().splitlines()if line.startswith('PORT_RESOURCE ')))
    def test_missing_duplicate_reordered_and_foreign_records_fail(self):
        lines=resource_log().splitlines()
        for changed in (lines[:2]+lines[3:],lines[:2]+[lines[2]]+lines[2:],lines[:2]+[lines[3],lines[2]]+lines[4:],['I '+lines[1]]+lines[:1]+lines[2:],lines[:-2]+lines[-1:],lines+['PORT_RESOURCE other=1']):
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_resource_log('\n'.join(changed),ROWS,BASE,PORT,BOOKS,BITS)
    def test_wrong_counts_ownership_core_source_or_case_order_fail(self):
        text=resource_log()
        for changed in (text.replace('checks=11','checks=10'),text.replace('checks=123','checks=124'),text.replace('checks=456','checks=455'),text.replace('live=0','live=1'),text.replace('bytes=0','bytes=1'),text.replace('core=1','core=0'),text.replace(BASE,'c'*64),text.replace(PORT,'c'*64),text.replace('phase=case case=0','phase=case case=1')):
            with self.subTest(text=changed),self.assertRaises(ValueError):subject.validate_resource_log(changed,ROWS,BASE,PORT,BOOKS,BITS)
    def test_complete_exact_generated_tree(self):
        with workspace_temporary()as folder:
            args=source_fixture(Path(folder));value=subject.validate_generated(*args,BASE,PORT);self.assertEqual(len(value['edits']),8);self.assertEqual(len(value['compiled_units']),22);self.assertEqual(sum(x['compiled'].startswith('ported/')for x in value['compiled_units']),3)
    def test_generated_byte_metadata_and_inventory_tampering_fail(self):
        for kind in range(4):
            with self.subTest(kind=kind),workspace_temporary()as folder:
                args=source_fixture(Path(folder));path=args[0]
                if kind==0:(path.parent/'ported/block.c').write_bytes(b'changed\n')
                elif kind==1:
                    record=json.loads(path.read_bytes());record['compiled_units'][0]['compiled']='ported/foreign.c';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
                elif kind==2:(path.parent/'foreign.c').write_text('extra')
                else:(path.parent/'base/upstream/libvorbis/lib/mdct.c').unlink()
                with self.assertRaises(ValueError):subject.validate_generated(*args,BASE,PORT)
    def test_nonunique_original_and_undeclared_edit_source_fail(self):
        for kind in range(2):
            with self.subTest(kind=kind),workspace_temporary()as folder:
                args=source_fixture(Path(folder));path,base,port,base_root,port_root=args
                if kind==0:
                    source=base_root/'upstream/libvorbis/lib/block.c';source.write_bytes(source.read_bytes()+b'before_0\n')
                else:
                    edits=json.loads((port_root/'edits.json').read_bytes());edits['edits'][0]['source']='../escape.c';(port_root/'edits.json').write_text(json.dumps(edits))
                with self.assertRaises(ValueError):subject.validate_generated(*args,BASE,PORT)
    def test_port_manifest_identity_and_contained_paths(self):
        port=dict(schema='native-vorbis-xiph-resource-port-v1',base_manifest_sha256=BASE,files={name:'e'*64 for name in ('CMakeLists.txt','prepare.py','edits.json')});self.assertEqual(subject.validate_port_manifest(port,BASE),port)
        for kind in range(3):
            value=copy.deepcopy(port)
            if kind==0:value['files']['../escape']='e'*64
            elif kind==1:value['base_manifest_sha256']=PORT
            else:value['files']['port-manifest.json']='e'*64
            with self.subTest(kind=kind),self.assertRaises(ValueError):subject.validate_port_manifest(value,BASE)
if __name__=='__main__':unittest.main()
