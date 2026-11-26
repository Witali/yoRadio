"""Root boundary check for the three frozen diagnostic fixtures; never starts QEMU."""
import hashlib
import json
from pathlib import Path
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
SOURCE='f7dee344fb30ce109f2d30a01f0325d353e3b2eb'
VERIFIER='d4e636beb193d9a52460f587300cc07cae4b93285e3b8b3a04cd7a7337dcd90b'

def load(path):return json.loads(path.read_bytes())
def pin(path):
    body=path.read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
def same(path,value):assert pin(path)=={key:value[key]for key in('bytes','sha256')}

assert subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==SOURCE
for args in [('diff','--quiet'),('diff','--cached','--quiet')]:
    assert subprocess.run(['git','-c','core.longpaths=true',*args],cwd=ROOT,capture_output=True).returncode==0
assert pin(BASE/'qualify-linked-pbuf.py')['sha256']==VERIFIER
result=dict(source_commit=SOURCE,all_sdk_passed=True,physical_tested=False,profiles={},
    scope='Observer-only RTC-off full-stream campaign. Original zero-allocation gate is unchanged; this release is not a memory fix or physical qualification.')
for name in('legacy','pdm','continuous'):
    folder=BASE/'sdk'/name;qpath=folder/'qualification.json';q=load(qpath)
    assert q['passed']is True and q['source_commit']==SOURCE and q['backend']==name
    assert q['physical_tested']is False and q['native_run']is False
    assert q['rtc_workspace']is False and q['rtc_probe_enabled']is True and q['pbuf_probe_enabled']is True
    assert q['effective_config_delta']=={}
    assert q['cmake_flag_delta']=={'CYD_OPENETH_PBUF_FAILURE_PROBE':{'before':False,'after':True}}
    assert len(q['changed_existing_objects'])==1 and q['changed_existing_objects'][0]['path'].endswith('/pcm.c.obj')
    assert q['owners']['s_pbuf_failures']['bytes']==128 and q['owners']['s_pbuf_failure_lock']['bytes']==8
    assert all(q['owners'][key]['section']=='.dram0.data'for key in('s_pbuf_failures','s_pbuf_failure_lock'))
    assert q['memory_delta']=={'dram_data_bytes':136,'dram_bss_bytes':0,'heap_start_bytes':144,'linker_alignment_bytes':8}
    assert q['geometry']=={'rtc_used_bytes':104,'rtc_reserved_bytes':24,'rtc_free_bytes':8064}
    assert q['frames']=={'__wrap_pbuf_alloc':48,'cyd_openeth_pbuf_failure_dump':192,'__wrap_native_audio_output_flush_pcm':160,'__wrap_native_audio_output_write_pcm':48}
    assert q['total_stack_depth_verified']is False
    assert len(q['project_clang'])==3 and all(row['warnings']==row['errors']==0 for row in q['project_clang'])
    assert len(q['sdk_frontends'])==2 and all(row['exit_status']==0 and row['baseline_command_equivalent']and row['config_header_identical']for row in q['sdk_frontends'])
    assert q['sdk_header_warnings']==18
    link=q['link_verification']
    assert link['four_tcp_sites_wrapped']and link['wrapper_real_once']and not link['hot_heap_log_or_unexpected_helper_calls']
    assert set(link['wrapper_calls'])=={'pbuf_alloc','vPortExitCritical','xPortEnterCriticalTimeout'}
    assert link['verifier']==pin(BASE/'qualify-linked-pbuf.py')
    candidates=list(BASE.glob('linked-*.json'))+list(folder.glob('*link*.json'))
    matching=[path for path in candidates if pin(path)==link['report']]
    assert matching,'Missing immutable final linked-target report'
    proof=load(matching[0]);assert proof['passed']and proof['wrapper_real_call_dominates_exits_without_cycle']
    assert {key:proof['elf'][key]for key in('bytes','sha256')}==q['elf']
    same(folder/'compiled/yoradio_cyd2usb_native.elf',q['elf'])
    image=folder/'fixture/yoradio_cyd2usb_native.bin';config=folder/'fixture/config/sdkconfig.json'
    same(image,q['image']);same(config,q['config'])
    for site,path in(('fixture','config/sdkconfig.json'),('compiled','config/sdkconfig.h')):
        assert(folder/site/path).read_bytes()==(ROOT/'.build/cnortc24'/name/site/path).read_bytes()
    assert all(q['image']['bytes']<slot['bytes']for slot in q['ota_slots'])
    result['profiles'][name]=dict(qualification=pin(qpath),image=pin(image),config=pin(config),elf=q['elf'],
        link_report=dict(file=matching[0].relative_to(ROOT).as_posix(),**pin(matching[0])))
output=BASE/'runtime-release.json';assert not output.exists();output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(runtime_released=True,source_commit=SOURCE,profiles=list(result['profiles']))))
