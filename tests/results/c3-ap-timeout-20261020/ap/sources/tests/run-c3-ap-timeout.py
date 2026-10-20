"""Execute historical C3 timer defects and actual repaired RSSI/AP owner paths.

Complete runtime_settings.c executes; selected network functions/helpers are
exact frozen spans. SDK/netif, RTOS, loader, activity and lease internals are
explicit seams, not target ABI/RF or a full application reconstruction.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('idf/esp32c3-oled-native/main')
TEST=Path('tests/native/c3_ap_timeout')
BASELINE='1256de5952d82486a73d21fb56d27d41e12185eb'
CASES=['restore','restore-invalid','default','deadline','thirty','online','disable','roundtrip','same-value','edit',
 'concurrent-settings','nvs-errors','writer-timeout','invalid-setting','ota','lease-error','sleep','associated',
 'netif-up','stale-ip','query-error','ip-error','mode-error','late-online','late-disable',
 'late-roundtrip','late-association','late-manual','activity-race','query-race','slow-lease',
 'prepare-sleep','sleep-error','failed-enable','pending-cancel','pending-cancel-error',
 'pending-late-online','pending-late-association','pending-new-attempt','clock-limit','clock-negative']

def sha(data):return hashlib.sha256(data).hexdigest()
def host(path):
 value=Path(path).resolve().as_posix()
 return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def execute(command):
 result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 return result.returncode,result.stdout
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 files=[Path(__file__).resolve().relative_to(ROOT),*[TEST/n for n in ['platform.h','platform.c','test.c','README.md']],
  *[MAIN/n for n in ['network_service.c','network_service.h','runtime_settings.c','runtime_settings.h','board_config.h','websocket_service.h','deep_sleep_clock.h']],
  Path('tests/run-network-runtime-baseline.py')]
 report={'passed':False,'scope':__doc__,'baseline_revision':BASELINE,'source_sha256':{},'historical':{},'cases':{},'negative_controls':{},'physical_hardware':False}
 def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 for rel in files:
  data=(ROOT/rel).read_bytes();dest=out/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);report['source_sha256'][rel.as_posix()]=sha(data)
 helper=out/'sources/tests/run-network-runtime-baseline.py';spec=importlib.util.spec_from_file_location('frozen_extract',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 stubs=out/'stubs';stubs.mkdir();(stubs/'freertos').mkdir()
 for name in ['esp_err.h','esp_check.h','esp_log.h','nvs.h','freertos/FreeRTOS.h','freertos/semphr.h']:(stubs/name).write_text('#pragma once\n#include "platform.h"\n')
 def build(directory,historical=False,mutation=None,settings_boundary=False,ignore_exhaustion=False):
  directory.mkdir(parents=True,exist_ok=True);src=directory/'sources'/MAIN;src.mkdir(parents=True,exist_ok=True)
  for name in ['network_service.c','runtime_settings.c','runtime_settings.h']:
   raw=subprocess.check_output(['git','-c','core.longpaths=true','show',BASELINE+':'+(MAIN/name).as_posix()],cwd=ROOT) if historical else (out/'sources'/MAIN/name).read_bytes()
   (src/name).write_bytes(raw)
   if historical:report.setdefault('historical_source_sha256',{})[(MAIN/name).as_posix()]=sha(raw)
  if settings_boundary:
   path=src/'runtime_settings.c';text=path.read_text();old='static atomic_uint s_softap_policy = (1U << 5) | RUNTIME_DEFAULT_SOFTAP_DELAY_MIN;'
   assert text.count(old)==1;text=text.replace(old,'static atomic_uint s_softap_policy = (UINT32_MAX & ~31U) | 1U;',1)
   if ignore_exhaustion:
    old='if ((previous >> 5) != (UINT32_MAX >> 5)) {';assert text.count(old)==1;text=text.replace(old,'if (true) {',1)
   path.write_text(text)
   report.setdefault('settings_initialization_seams',{})[directory.name]={'scope':'Test-only boot-local packed revision exhaustion seed; exact actual settings functions, no private owner phase/ACK writes. Not a normal NVS restoration state.','ignore_exhaustion_mutation':ignore_exhaustion,'generated_settings_sha256':sha(path.read_bytes())}
  text=(src/'network_service.c').read_text();prefix=text[text.index('#define WIFI_CONNECTED_BIT'):text.index('// Desired next-boot credential owner.')]
  names=['apply_power','rssi_task','select_credential','event_handler',*(['softap_reboot_callback'] if historical else []),'start_access_point','network_service_prepare_sleep','network_service_start','network_service_retry_client']
  spans=[module.function(text,name)[0] for name in names]
  unit=prefix+'\n'+'\n\n'.join(spans)+'\n'
  if mutation:
   for old,new in mutation:
    assert unit.count(old)==1,(old,unit.count(old));unit=unit.replace(old,new,1)
  (directory/'production.inc').write_text(unit)
  report.setdefault('network_spans',{})[directory.name]={'prefix_sha256':sha(prefix.encode()),'function_sha256':{n:sha(s.encode()) for n,s in zip(names,spans)},'generated_sha256':sha(unit.encode())}
  binary=directory/'test';command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-const-variable','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',*(['-DHISTORICAL=1'] if historical else []),'-include',host(out/'sources'/TEST/'platform.h'),'-I'+host(stubs),'-I'+host(src),'-I'+host(out/'sources'/TEST),'-I'+host(directory),host(src/'runtime_settings.c'),host(out/'sources'/TEST/'platform.c'),host(out/'sources'/TEST/'test.c'),'-o',host(binary)]
  (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n');code,log=execute(command);(directory/'build.log').write_bytes(log);save();assert code==0,log.decode(errors='replace')
  return binary
 def run(binary,case,leaks=True):return execute(['env','ASAN_OPTIONS=detect_leaks='+('1' if leaks else '0')+':halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case])
 code,log=execute(['gcc','--version']);assert code==0,log;(out/'compiler.log').write_bytes(log)
 baseline=build(out/'historical',True)
 for case in ['ota','online','disable']:
  code,log=run(baseline,case);(out/'historical'/(case+'.log')).write_bytes(log)
  assert code==42 and log==('SAFETY_FAILURE:ap_timeout_respects_'+case+'\n').encode(),(case,code,log)
  report['historical'][case]={'detected':True,'status':code,'marker':log.decode().strip()};save();print('HISTORICAL_DETECTED:'+case,flush=True)
 current=build(out/'current')
 for case in CASES:
  code,log=run(current,case);(out/'current'/(case+'.log')).write_bytes(log);report['cases'][case]={'passed':code==0,'status':code,'output':log.decode(errors='replace')};save()
  assert code==0 and log==('PASS:'+case+'\n').encode(),(case,code,log);print('PASS:'+case,flush=True)
 boundary=build(out/'settings-boundary',settings_boundary=True);code,log=run(boundary,'revision-exhaustion');(out/'settings-boundary/test.log').write_bytes(log)
 assert code==0 and log==b'PASS:revision-exhaustion\n',(code,log)
 report['cases']['revision-exhaustion']={'passed':True,'status':code,'output':log.decode(),'settings_initialization_seam':True};save();print('PASS:revision-exhaustion',flush=True)
 mutations=[
  ('skip-final-check', [('if (softap_live(&facts, desired.revision, esp_timer_get_time()))','if (true)')],
   'late-online','final_change_cancels_only_own_ap_lease'),
  ('ignore-armed-revision',[('policy->revision != desired.revision || ','')],
   'roundtrip','new_revision_invalidates_old_deadline_even_same_final_value'),
  ('ignore-final-revision',[('desired.revision == revision && desired.delay_min;','((void)revision, desired.delay_min);')],
   'late-roundtrip','final_change_cancels_only_own_ap_lease'),
  ('bypass-reservation',[('websocket_service_reboot_reserve(&lease) == ESP_OK','((void)lease, true)'),
    ('(void)websocket_service_reboot_restart_reserved_now(&lease);','esp_restart();')],
   'ota','blocked_admission_never_queues_ap_restart'),
  ('pending-restarts-without-cancel',[('if (facts.pending) softap_cancel_pending(&facts, desired.revision, now);','if (false && facts.pending) softap_cancel_pending(&facts, desired.revision, now);'),
    ('now >= 0 && !facts->pending && softap_disconnected(facts, revision)','now >= 0 && softap_disconnected(facts, revision)')],
   'pending-cancel','expired_connect_intent_cancelled_before_any_restart_admission'),
  ('old-cancel-clears-new-intent',[('s_softap.version == operation && s_softap.operations == 1 && result == ESP_OK',
     '((void)operation, s_softap.operations == 1) && result == ESP_OK')],
   'pending-new-attempt','older_cancel_does_not_clear_newer_connect_intent'),
  ('rearm-from-stale-time',[('int64_t rearm = esp_timer_get_time();','int64_t rearm = now;')],
   'slow-lease','slow_failed_admission_rearms_from_return_time'),
 ]
 for name,replacements,case,marker in mutations:
  directory=out/'mutants'/name;binary=build(directory,mutation=replacements);code,log=run(binary,case,False);(directory/'test.log').write_bytes(log)
  assert code==80 and log.startswith(('SEMANTIC_FAILURE:'+marker+':').encode()),(name,code,log)
  assert not any(error in log for error in [b'AddressSanitizer',b'LeakSanitizer',b'runtime error:']),log
  report['negative_controls'][name]={'detected':True,'status':code,'case':case,'marker':marker,'generated_sha256':sha((directory/'production.inc').read_bytes())};save();print('DETECTED:'+name,flush=True)
 directory=out/'mutants/ignore-exhaustion';binary=build(directory,settings_boundary=True,ignore_exhaustion=True);code,log=run(binary,'revision-exhaustion',False);(directory/'test.log').write_bytes(log)
 marker='exhausted_admission_rejects_before_nvs';assert code==80 and log.startswith(('SEMANTIC_FAILURE:'+marker+':').encode()),(code,log)
 assert not any(error in log for error in [b'AddressSanitizer',b'LeakSanitizer',b'runtime error:']),log
 report['negative_controls']['ignore-exhaustion']={'detected':True,'status':code,'case':'revision-exhaustion','marker':marker};save();print('DETECTED:ignore-exhaustion',flush=True)
 report['source_unchanged_after']={key:sha((ROOT/key).read_bytes())==value for key,value in report['source_sha256'].items()}
 assert all(report['source_unchanged_after'].values())
 report['stub_sha256']={p.relative_to(stubs).as_posix():sha(p.read_bytes()) for p in stubs.rglob('*') if p.is_file()}
 report['passed']=True;save()
if __name__=='__main__':main()
