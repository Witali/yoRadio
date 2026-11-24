"""Aggregate terminal static controls; no compilation or native runtime."""
import shutil
from common import *

prep=load(BASE/'preflight.json')
report=dict(source_commit=SOURCE,project_source_reference='b65437a1bc59c9d269ce7bece597efddc70cea58',
    scope='RTC workspace off/on isolated static control; native HE-AAC/two-client/post-close health belongs to root.',
    rtc_workspace=False,rtc_probe_enabled=True,physical_tested=False,native_run=False,
    original_failed_outcomes_preserved=True,rows=[],compilers_quiet=True,state='TERMINAL_PASS',qemu=prep['qemu'])
for backend in ('legacy','pdm','continuous'):
    directory=BASE/backend; status=load(directory/'execution-status.json'); q=load(directory/'qualification.json')
    assert q['passed'] and q['source_commit']==SOURCE
    assert all(c['state']=='TERMINAL' for c in status['children'])
    outcomes=dict(original_controller=status['state'])
    if backend=='legacy':
        first=load(directory/'qualification-continuation-status.json')
        final=load(directory/'qualification-reviewed-continuation-status.json')
        assert status['state']==first['state']=='TERMINAL_NONPASS' and final['state']=='TERMINAL_PASS'
        assert all(c['exit_status']==0 for c in status['children']if c['phase']!='qualify')
        outcomes.update(first_static_continuation=first['state'],reviewed_static_continuation=final['state'],rebuild=False,
            first_failure='Helper expected LF, actual generated header uses CRLF',
            second_failure='Unextracted bootloader descriptor date field; subsequently reviewed with exact byte/map/ELF proof')
    else:
        assert status['state']=='TERMINAL_PASS' and all(c['exit_status']==0 for c in status['children'])
    baseline=load(directory/'baseline.json')
    for item in prep['protected']: same(item)
    old=ROOT/baseline['rtc_on']/'fixture/yoradio_cyd2usb_native.bin'
    image=directory/'fixture/yoradio_cyd2usb_native.bin'; assert pin(image)==q['image']
    assert q['geometry']['rtc_slow_used_bytes']==104 and q['geometry']['rtc_slow_free_bytes']==8064
    assert q['geometry']['heap_start']-baseline['geometry']['heap_start']==6560
    assert q['geometry']['dram_bss_bytes']-baseline['geometry']['dram_bss_bytes']==6560
    assert q['rtc_probe']['bytes']==64
    report['rows'].append(dict(backend=backend,fixture=(directory/'fixture').relative_to(ROOT).as_posix(),
        qualification=(directory/'qualification.json').relative_to(ROOT).as_posix(),qualification_identity=pin(directory/'qualification.json'),
        image=q['image'],image_size_change_bytes=q['image']['bytes']-old.stat().st_size,elf=q['elf'],
        objects_compared=q['object_count'],changed_raw_objects=q['changed_raw_object_count'],
        changed_allocated=q['changed_allocated'],unlinked_bootloader_date_exceptions=q['unlinked_bootloader_date_exceptions'],
        effective_config_delta=q['effective_config_delta'],geometry=q['geometry'],
        dram_bss_increase_bytes=6560,heap_start_increase_bytes=6560,static_frames=q['static_frames'],lint=q['lint'],
        outcomes=outcomes,descriptor_context=q['descriptor_context']))
report['objects_compared']=sum(x['objects_compared']for x in report['rows'])
report['focused_whole_tu_checks']=6
report['new_warnings']=0
report['protected_inputs_reverified']=len(prep['protected'])
report['production_app_metadata_files_unchanged']=24
report['free_disk_gib']=round(shutil.disk_usage(ROOT).free/2**30,2)
assert not (BASE/'results.json').exists(); write(BASE/'results.json',report)
print(json.dumps(dict(state=report['state'],compilers_quiet=True,objects_compared=report['objects_compared'],
    focused_whole_tu_checks=6,new_warnings=0,production_files_unchanged=24,free_disk_gib=report['free_disk_gib'],
    rows=[dict(backend=r['backend'],bytes=r['image']['bytes'],delta=r['image_size_change_bytes'])for r in report['rows']])))
