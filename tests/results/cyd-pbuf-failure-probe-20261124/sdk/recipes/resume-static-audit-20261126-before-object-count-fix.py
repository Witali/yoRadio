"""Read-only resumed qualification audit; no builds, guests, index writes or network."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];DEP=Path('C:/Work/yoRadio/.idf')
SOURCE='f7dee344fb30ce109f2d30a01f0325d353e3b2eb'
VERIFIER='d4e636beb193d9a52460f587300cc07cae4b93285e3b8b3a04cd7a7337dcd90b'

def load(path):return json.loads(path.read_bytes())
def ident(body):return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
def pin(path):return ident(path.read_bytes())
def same(path,want):return pin(path)=={k:want[k]for k in ('bytes','sha256')}
def git(folder,*args):
    r=subprocess.run(['git','--no-optional-locks','-c','core.longpaths=true','-C',str(folder),*args],capture_output=True)
    assert r.returncode==0,'Read-only Git inspection failed; diagnostics withheld'
    return r.stdout

candidate=load(BASE/'candidate-inputs.json')
assert candidate['source_commit']==SOURCE and git(ROOT,'rev-parse','HEAD').decode().strip()==SOURCE
assert not git(ROOT,'diff','--name-only')and not git(ROOT,'diff','--cached','--name-only')
assert pin(BASE/'qualify-linked-pbuf.py')['sha256']==VERIFIER
report=dict(passed=False,source_commit=SOURCE,scope='All preserved source/protected/object bytes and final static qualifications revalidated; no native runtime, rebuild or repeated successful analysis.',
            compilers_run=0,qemu_run=False,source_pins=0,protected_bindings=0,sdk_repositories={},profiles={},failures=[])
for name,want in candidate['sources'].items():
    assert same(ROOT/name,want),'Candidate source changed: '+name
    report['source_pins']+=1
for item in candidate['protected']:
    assert same(ROOT/item['path'],item),'Protected input changed: '+item['path']
    report['protected_bindings']+=1
for name,want in candidate['sdk_repositories'].items():
    folder=DEP/name;head=git(folder,'rev-parse','HEAD').decode().strip();dirty=git(folder,'status','--porcelain','--untracked-files=no')
    assert head==want and not dirty,'SDK repository identity/cleanliness changed: '+name
    report['sdk_repositories'][name]=dict(head=head,clean=True)
for backend in ('legacy','pdm','continuous'):
    d=BASE/'sdk'/backend;old=ROOT/'.build/cnortc24'/backend;before=BASE/'sdk-baseline'/backend
    q=load(d/'qualification.json');static=load(d/'static-qualification.json');clang=load(d/'clang-status.json');link=load(d/'link-qualification.json')
    assert q['passed']and static['passed']and q['source_commit']==SOURCE and q['backend']==backend
    assert q['physical_tested']is False and q['native_run']is False
    assert q['effective_config_delta']=={}and q['cmake_flag_delta']=={'CYD_OPENETH_PBUF_FAILURE_PROBE':{'before':False,'after':True}}
    assert q['rtc_workspace']is False and q['rtc_probe_enabled']and q['pbuf_probe_enabled']
    assert q['memory_delta']==dict(dram_data_bytes=136,dram_bss_bytes=0,heap_start_bytes=144,linker_alignment_bytes=8)
    assert q['geometry']==dict(rtc_used_bytes=104,rtc_reserved_bytes=24,rtc_free_bytes=8064)
    assert q['frames']=={'__wrap_pbuf_alloc':48,'cyd_openeth_pbuf_failure_dump':192,'__wrap_native_audio_output_flush_pcm':160,'__wrap_native_audio_output_write_pcm':48}
    assert not q['total_stack_depth_verified']
    assert clang['state']=='TERMINAL_PASS'and all(row['state']=='TERMINAL'and row['exit_status']==0 for row in clang['children'])
    assert len(q['project_clang'])==3 and all(row['warnings']==row['errors']==0 for row in q['project_clang'])
    assert len(q['sdk_frontends'])==2 and all(row['exit_status']==0 and row['baseline_command_equivalent']and row['config_header_identical']for row in q['sdk_frontends'])
    warnings=load(d/'lint-pbuf-system-inclusive.json');assert warnings['warnings']==18 and warnings['errors']==0 and warnings['returncode']==0
    assert q['sdk_header_warnings']==18 and link['passed']and link['verifier']['sha256']==VERIFIER
    assert same(d/'link-qualification.json',q['link_verification']['report'])and q['link_verification']['verifier']==pin(BASE/'qualify-linked-pbuf.py')
    assert link['wrapper_real_call_dominates_exits_without_cycle']and len(link['tcp_out_sites'])==4
    assert {name for call in link['wrapper_calls']for name in call['target']['names']}=={'pbuf_alloc','xPortEnterCriticalTimeout','vPortExitCritical'}
    assert same(d/'compiled/yoradio_cyd2usb_native.elf',q['elf'])and same(d/'fixture/yoradio_cyd2usb_native.bin',q['image'])
    assert same(d/'compiled/config/sdkconfig.json',q['config'])and same(d/'fixture/config/sdkconfig.json',q['config'])
    assert q['elf']=={k:link['elf'][k]for k in ('bytes','sha256')}
    for path in ('config/sdkconfig.json','config/sdkconfig.h'):
        assert(d/'compiled'/path).read_bytes()==(old/'compiled'/path).read_bytes()
        if path.endswith('.json'):assert(d/'compiled'/path).read_bytes()==(d/'fixture'/path).read_bytes()
    old_files={p.relative_to(old/'fixture').as_posix():p for p in (old/'fixture').rglob('*')if p.is_file()}
    new_files={p.relative_to(d/'fixture').as_posix():p for p in (d/'fixture').rglob('*')if p.is_file()}
    assert old_files.keys()==new_files.keys()
    nonapp=0
    for name,path in old_files.items():
        if name=='yoradio_cyd2usb_native.bin':continue
        assert pin(path)==pin(new_files[name]),'Nonapplication fixture changed: '+backend+'/'+name
        nonapp+=1
    assert same(before/'snapshot.json',q['baseline_snapshot'])and same(before/'objects.zip',q['baseline_objects_zip'])
    objects=load(before/'objects.json');comparison=load(d/'object-comparison.json');changes={x['path']:x for x in comparison['changed_existing']}
    assert len(objects)==2855 and len(changes)==1 and next(iter(changes)).endswith('/pcm.c.obj')
    snapshot=load(before/'snapshot.json');cache=ROOT/snapshot['cache'];missing=[];changed=[]
    with zipfile.ZipFile(before/'objects.zip')as archive:
        assert set(archive.namelist())=={item['zip_member']for item in objects}
        for item in objects:
            assert ident(archive.read(item['zip_member']))=={k:item[k]for k in ('bytes','sha256')}
            actual=ROOT/item['path'];want=changes[item['path']]['after']if item['path']in changes else item
            if not actual.exists():missing.append(item['path'])
            elif not same(actual,want):changed.append(item['path'])
    assert not missing and not changed,'Current compiled cache differs from its preserved qualification: '+backend
    new=Path(comparison['new_probe_command']['output']);assert same(cache/new,q['new_probe_object'])
    with zipfile.ZipFile(d/'compiled/changed-objects.zip')as archive:
        for item in objects:
            if item['path']in changes:assert ident(archive.read(item['zip_member']))==changes[item['path']]['after']
        assert ident(archive.read(new.as_posix()))==q['new_probe_object']
    report['profiles'][backend]=dict(qualification=pin(d/'qualification.json'),image=q['image'],elf=q['elf'],config=q['config'],
        original_objects_verified=len(objects),current_cache_objects_verified=len(objects)+1,nonapp_fixture_files_verified=nonapp,
        final_link_report=pin(d/'link-qualification.json'),system_header_warnings=18,memory_delta=q['memory_delta'],frames=q['frames'])
report['passed']=True
out=BASE/'resume-static-audit-20261126.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(passed=True,source_pins=report['source_pins'],protected_bindings=report['protected_bindings'],profiles=list(report['profiles']),object_checks=sum(x['original_objects_verified']+x['current_cache_objects_verified']for x in report['profiles'].values()))))
