"""Qualify whole CYD reclaim service and canonical queue with explicit host seams.

Strict ASan/UBSan; original TLS allocation, heap accounting and pthread RTOS are
modeled. No private runtime registry/queue writes, SDK/target build, actual SDK
OOM, startup/health integration or physical timing qualification is claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('idf/esp32-cyd2usb-native/main')
SHARED=Path('idf/components/native_stream')
TEST=Path('tests/native/cyd_input_reclaim')
CASES=['registry','unbound','first-success','malformed-null','malformed-sentinel','isr',
       'exhaustion','repeat-exhaustion','zero-budget','recovery','floor-recovery','restore',
       'control-writing','control-ready','control-reading','no-idle','pinned-detach',
       'free-detach','retry-detach','fixed-budget','concurrent']


def sha(raw):return hashlib.sha256(raw).hexdigest()


def host(path):
    text=Path(path).resolve().as_posix()
    return '/mnt/'+text[0].lower()+text[2:] if sys.platform=='win32' else text


def execute(command):
    result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    return result.returncode,result.stdout


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    if not out.is_relative_to(ROOT/'.build'):parser.error('Use a fresh .build output')
    out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__).resolve().relative_to(ROOT),MAIN/'native_input_reclaim.c',MAIN/'native_input_reclaim.h',
           SHARED/'adaptive_input.c',SHARED/'include/adaptive_input.h',*[TEST/name for name in ['platform.h','test.c','README.md']]]
    report={'passed':False,'scope':__doc__,'sanitizers':['ASan','UBSan'],'source_sha256':{},'cases':{},'negative_controls':{},
            'physical_hardware':False,'actual_sdk_allocator':False,'private_runtime_state_seeded':False}
    def save():(out/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    frozen=out/'sources'
    for relative in files:
        raw=(ROOT/relative).read_bytes();target=frozen/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        report['source_sha256'][relative.as_posix()]=sha(raw)
    save()
    stubs=out/'stubs'
    for name in ['FreeRTOS.h','semphr.h','task.h']:
        path=stubs/'freertos'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "platform.h"\n')
    status,log=execute(['gcc','--version']);(out/'compiler.log').write_bytes(log);assert status==0,log
    report['compiler']=log.decode().splitlines()[0]
    module=(frozen/MAIN/'native_input_reclaim.c').read_text()
    queue=(frozen/SHARED/'adaptive_input.c').read_text()
    flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pthread',
           '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
           '-I'+host(stubs),'-I'+host(frozen/MAIN),'-I'+host(frozen/SHARED/'include'),'-I'+host(frozen/TEST)]

    def queue_object(directory,source):
        directory.mkdir(parents=True,exist_ok=True);obj=directory/'adaptive_input.o'
        command=flags+['-Dmalloc=cyd_test_malloc','-Dcalloc=cyd_test_calloc','-Dfree=cyd_test_free',
                       '-c',host(source),'-o',host(obj)]
        (directory/'queue-command.json').write_text(json.dumps(command,indent=2)+'\n')
        code,log=execute(command);(directory/'queue-build.log').write_bytes(log);save()
        assert code==0,log.decode(errors='replace');return obj

    queue_obj=queue_object(out/'positive',frozen/SHARED/'adaptive_input.c')

    def build(directory,source,queue_object,unused=False):
        directory.mkdir(parents=True,exist_ok=True);binary=directory/'test'
        command=flags+(['-Wno-unused-function'] if unused else [])+[host(source),host(frozen/TEST/'test.c'),host(queue_object),
                  '-Wl,--wrap=adaptive_input_release_one','-o',host(binary)]
        (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        code,log=execute(command);(directory/'build.log').write_bytes(log);save()
        assert code==0,log.decode(errors='replace');return binary

    def run(directory,binary,case,marker=None):
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks='+('0' if marker else '1')+':halt_on_error=1',
                          'UBSAN_OPTIONS=halt_on_error=1',host(binary),case])
        (directory/'run.log').write_bytes(log)
        assert not any(token in log for token in [b'AddressSanitizer',b'LeakSanitizer',b'runtime error:']),log
        if marker:assert code==80 and re.fullmatch(rb'SEMANTIC_FAILURE:'+marker.encode()+rb':\d+\n',log),(case,code,log)
        else:assert code==0 and log==''.join('PASS:'+name+'\n' for name in CASES).encode(),(code,log)
        return code,log

    binary=build(out/'positive',frozen/MAIN/'native_input_reclaim.c',queue_obj)
    code,log=run(out/'positive',binary,'all')
    for name in CASES:report['cases'][name]={'passed':True,'marker':'PASS:'+name}
    report['concurrent_fifo_packets']=10000;print('PASS complete module/queue: '+str(len(CASES))+' cases',flush=True);save()
    changes=[
      ('preclaim-before-original','    void *result = __real_esp_mbedtls_mem_calloc(count, size);',
       '    adaptive_input_t *early = pin_input();\n    if (early) { adaptive_input_release_one(early); unpin_input(); }\n    void *result = __real_esp_mbedtls_mem_calloc(count, size);','first-success','original_allocator_first_no_preclaim'),
      ('reclaim-malformed','result || !count || !size || size > SIZE_MAX / count || xPortInIsrContext()',
       'result || xPortInIsrContext()','malformed-null','malformed_delegates_once_without_reclaim'),
      ('reclaim-isr','size > SIZE_MAX / count || xPortInIsrContext()',
       'size > SIZE_MAX / count','isr','critical_not_nested_or_isr'),
      ('bind-not-idempotent','(!s_owner || s_owner == input)','(!s_owner)','registry','same_active_bind_idempotent'),
      ('overwrite-owner','!s_retiring && (!s_owner || s_owner == input)','!s_retiring','registry','null_conflicting_bind_rejected'),
      ('detach-wrong-owner','if (s_owner != input)','if (false)','registry','wrong_owner_no_effect'),
      ('detach-pinned-owner','result = NATIVE_INPUT_RECLAIM_BUSY;','result = NATIVE_INPUT_RECLAIM_DETACHED;','pinned-detach','pinned_owner_is_busy'),
      ('retire-admission-open','        s_retiring = true;','        s_retiring = false;','pinned-detach','retiring_bind_denied'),
      ('admit-new-pins','s_owner && !s_retiring && s_pins != SIZE_MAX','s_owner && s_pins != SIZE_MAX','pinned-detach','retiring_new_pins_denied'),
      ('last-unpin-clears-owner','    --s_pins;','    if (--s_pins == 0 && s_retiring) { s_owner = NULL; s_retiring = false; }','pinned-detach','retired_owner_requires_explicit_detach'),
      ('missing-unpin','    unpin_input();\n    return result;','    return result;','recovery','all_allocator_pins_drained'),
      ('budget-from-resident','stats.target - stats.minimum','stats.resident - stats.minimum','fixed-budget','fixed_target_budget'),
      ('unbounded-refill-loop','attempt < budget','(attempt < budget || budget > 0)','fixed-budget','bounded_retry_budget'),
      ('retry-before-free','        if (!adaptive_input_release_one(input)) break;\n        result = __real_esp_mbedtls_mem_calloc(count, size);',
       '        result = __real_esp_mbedtls_mem_calloc(count, size);\n        if (!adaptive_input_release_one(input)) break;','recovery','retry_after_completed_slot_free'),
      ('registry-lock-across-queue','    adaptive_input_stats_t stats = adaptive_input_stats(input);',
       '    portENTER_CRITICAL(&s_reclaim_lock);\n    adaptive_input_stats_t stats = adaptive_input_stats(input);\n    portEXIT_CRITICAL(&s_reclaim_lock);','exhaustion','critical_not_nested_or_isr'),
    ]
    for name,old,new,case,marker in changes:
        assert module.count(old)==1,(name,module.count(old));directory=out/'mutants'/name;directory.mkdir(parents=True)
        source=directory/'native_input_reclaim.c';source.write_text(module.replace(old,new,1))
        binary=build(directory,source,queue_obj,unused=name=='missing-unpin')
        code,log=run(directory,binary,case,marker)
        report['negative_controls'][name]={'detected':True,'exit_status':code,'case':case,'expected_marker':marker,'source_sha256':sha(source.read_bytes())}
        print('CONTROL '+name,flush=True);save()
    start=queue.index('bool adaptive_input_release_one(')
    for name,old,new,case,marker in [
        ('queue-reclaims-leased','if (slot->state != IDLE) continue;','if (slot->state != IDLE && slot->state != WRITING) continue;','no-idle','no_live_lease_is_freed'),
        ('queue-below-floor','if (input->resident > input->minimum)','if (input->resident > 0)','repeat-exhaustion','repeated_pressure_keeps_floor')]:
        assert queue[start:].count(old)==1
        directory=out/'mutants'/name;directory.mkdir(parents=True);source=directory/'adaptive_input.c'
        source.write_text(queue[:start]+queue[start:].replace(old,new,1))
        mutated_queue=queue_object(directory,source)
        binary=build(directory,frozen/MAIN/'native_input_reclaim.c',mutated_queue)
        code,log=run(directory,binary,case,marker)
        report['negative_controls'][name]={'detected':True,'exit_status':code,'case':case,'expected_marker':marker,'source_sha256':sha(source.read_bytes())}
        print('CONTROL '+name,flush=True);save()
    report['input_unchanged_after']={name:sha((ROOT/name).read_bytes())==digest for name,digest in report['source_sha256'].items()}
    report['snapshots_unchanged_after']={name:sha((frozen/name).read_bytes())==digest for name,digest in report['source_sha256'].items()}
    assert all(report['input_unchanged_after'].values()) and all(report['snapshots_unchanged_after'].values())
    report['generated_sha256']={path.relative_to(out).as_posix():sha(path.read_bytes()) for path in out.rglob('*') if path.is_file() and path.name not in ['report.json','test']}
    report['complete_normal_module_source_matches_frozen_bytes']=True
    report['complete_canonical_queue_source_matches_frozen_bytes']=True
    report['limitations']=['TLS failure and heap capacity are host seams, not actual SDK OOM. Success uses ordinary libc calloc/free.',
        'pthread critical/ISR/barrier seams do not establish ESP32 kernel timing, target ABI or TSAN evidence.',
        'The representable registry pin-count overflow guard is source-reviewed; the suite does not create SIZE_MAX simultaneous real pins or write private runtime state.',
        'Startup publication, native_health callback integration, target link/wrapper references and actual QEMU/board qualification are separate gates.']
    report['passed']=True;save();print('PASS reclaim host service: '+str(len(CASES))+' cases, '+str(len(report['negative_controls']))+' exact semantic controls',flush=True)


if __name__=='__main__':main()
