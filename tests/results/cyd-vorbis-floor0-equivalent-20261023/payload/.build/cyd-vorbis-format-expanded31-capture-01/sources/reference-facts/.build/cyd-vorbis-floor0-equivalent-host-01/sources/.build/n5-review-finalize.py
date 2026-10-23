import datetime,hashlib,json,os,pathlib,subprocess
root=pathlib.Path.cwd();out=root/'.build/n5-independent-review-01'
report=json.loads((out/'review.json').read_text(encoding='utf-8'))
final={};changed=[]
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2')
for name,old in report['source_sha256'].items():
    source=pathlib.Path(name)
    if not source.is_absolute():source=root/name;target=out/'final-sources'/name
    else:target=out/'final-sdk'/source.relative_to(sdk)
    raw=source.read_bytes();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    final[name]=hashlib.sha256(raw).hexdigest()
    if old!=final[name]:changed.append(name)
assert set(changed)=={'idf/esp32-cyd2usb-native/main/web_pages.cpp','idf/esp32-cyd2usb-native/main/network_runtime.c'},changed
env=os.environ.copy();env['CYD_NATIVE_PAGE_SOURCE']=str(out/'final-sources/idf/esp32-cyd2usb-native/main/web_pages.cpp')
command=['C:/Program Files/nodejs/node.exe','--test','--test-reporter=tap','--test-name-pattern','^independent review:',str(out/'stale-timer-reproduction.test.js')]
result=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
(out/'stale-timer-fixed.log').write_bytes(result.stdout)
assert result.returncode==0 and b'# pass 1' in result.stdout,result.stdout
page_report=json.loads((root/'.build/n5-page-02/report.json').read_text(encoding='utf-8'))
assert page_report['passed'] and page_report['positive_groups']==48 and len(page_report['negative_controls'])==14
for name,digest in page_report['source_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
report['findings'][0]['status']='resolved in final frozen source; independent original reproduction now passes'
report['final_reviewed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report['final_source_sha256']=final
report['inputs_changed_since_initial_review']=changed
report['final_open_findings']=[]
report['checked_contracts']=[
 'network_settings init after NVS, nonfatal init error without erase/rewrite, source included in CMake',
 'initial hostname before owner admission and facade esp_wifi_start; retries apply only after checked NOT_CONNECT and before connect',
 'online saves desired only; successful stale apply records actual passed hostname; SDK OOM clears configured validity in line with pinned lwIP free-before-strdup',
 'same known hostname skips redundant netif allocation; failed set does not fabricate SDK acknowledgement',
 'AP timer absolute deadline in existing100ms owner; default0 disabled; interval changes/manual cycle rearm and hostname-only edits preserve interval',
 'online/AP unavailable/stop/settings unavailable cancel deadline; saturated full interval cannot authorize early restart',
 'due AP eligibility requires AP_IDLE/no active cycle/retry/manual admission/reconciliation/callback/queued event, unchanged version and RUNNING lifetime',
 'final runtime delta places the acquire link-version check after gate and queue checks; reviewed as correct strengthening of final late-notice exclusion',
 'actual STA association must return exact NOT_CONNECT; netif must be down and successfully read zero IPv4; final settings snapshot and local version checked again after lease reserve',
 'AP uses no ordinary durable pending queue; failed admission or eligibility rearms full interval, preserving OTA/credential priority and explicit final application linearization boundary',
 'immediate restart retains exact ready lease across outside-portMUX SDK call; unchanged existing request/cancel/commit semantics',
 'HTTP exact two complete query fields, duplicate/unknown/decoding rejection, checked canonical0..30 unsigned parse, ASCII hostname validation, bounded query and output',
 'HTTP persistence failure mappings and body rejection close/ESP_FAIL; POST persists only and explicitly separates application/reboot',
 'GET independently reports desired record, configured-host validity/error, pending by actual hostname and explicit runtime unavailable nulls',
 'two route entries and URI24 capacity precede wildcard and retain checked startup rollback',
 'UI exact capability limits, dirty form/request epoch protection, persistence failure retention, no await-restart on save, upload/OTA gating and existing sequential poll loop',
 'separate timer label invalidated after successful durable save followed by failed forced GET; original independent frozen-page reproduction fails and fixed frozen-page reproduction passes',
 'C3 production, board pin mapping, existing task stack/priority/affinity definitions and audio owner sources unchanged in this N5 integration'
]
report['final_verification']={'independent_reproduction_exit_status':result.returncode,'independent_reproduction_log':'stale-timer-fixed.log','independent_reproduction_log_sha256':hashlib.sha256(result.stdout).hexdigest(),'page_report':'.build/n5-page-02/report.json','page_report_sha256':hashlib.sha256((root/'.build/n5-page-02/report.json').read_bytes()).hexdigest(),'page_report_inputs_match_current':True,'page_positive_groups':48,'page_exact_negative_controls':14}
report['limitations']=['Read-only code/SDK review and actual page-script seams are not physical CYD, RF/DHCP, live reset, OTA-flash durability or target ABI evidence.','SDK event/config/lifecycle changes arriving after the documented final application check cannot be made atomic with esp_restart by this API.','Did not rerun the runtime/HTTP/production GCC/Clang suites as part of this independent review; implementation agents and parent own those gates.','Pinned sources were reviewed at recorded hashes; any later production changes require another delta review.']
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Independent review finalized: one reproduced UI finding resolved, no remaining actionable findings in reviewed scope')
print('Review SHA256',hashlib.sha256((out/'review.json').read_bytes()).hexdigest())
