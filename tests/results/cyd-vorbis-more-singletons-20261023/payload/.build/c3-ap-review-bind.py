import datetime,hashlib,json,pathlib
root=pathlib.Path.cwd();out=root/'.build/c3-ap-independent-review-01'
path=out/'review.json';report=json.loads(path.read_text(encoding='utf-8'))
evidence=root/'.build/c3-ap-timeout-final-02';raw=(evidence/'report.json').read_bytes();tests=json.loads(raw)
assert tests['passed'] and len(tests['cases'])==42 and len(tests['negative_controls'])==8 and len(tests['historical'])==3
assert all(case['passed'] and case['status']==0 for case in tests['cases'].values())
assert all(case['detected'] and case['status']==80 for case in tests['negative_controls'].values())
assert all(case['detected'] and case['status']==42 for case in tests['historical'].values())
final={};changed=[]
for name in sorted(set(report['source_sha256'])|set(tests['source_sha256'])):
    data=(root/name).read_bytes();digest=hashlib.sha256(data).hexdigest();final[name]=digest
    if name in tests['source_sha256']:assert digest==tests['source_sha256'][name],name
    target=out/'final-sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    if name in report['source_sha256'] and digest!=report['source_sha256'][name]:changed.append(name)
production=['idf/esp32c3-oled-native/main/network_service.c','idf/esp32c3-oled-native/main/runtime_settings.c','idf/esp32c3-oled-native/main/runtime_settings.h']
assert not(set(changed)&set(production)),changed
for name in ['restore','restore-invalid','concurrent-settings','pending-late-association','revision-exhaustion']:
    actual=evidence/('settings-boundary/test.log' if name=='revision-exhaustion' else 'current/'+name+'.log')
    assert actual.read_bytes()==('PASS:'+name+'\n').encode(),name
current=(evidence/'current/sources/idf/esp32c3-oled-native/main/runtime_settings.c').read_bytes()
assert current==(root/'idf/esp32c3-oled-native/main/runtime_settings.c').read_bytes()
boundary=(evidence/'settings-boundary/sources/idf/esp32c3-oled-native/main/runtime_settings.c').read_text(encoding='utf-8')
expected=current.decode().replace('\r\n','\n').replace('static atomic_uint s_softap_policy = (1U << 5) | RUNTIME_DEFAULT_SOFTAP_DELAY_MIN;','static atomic_uint s_softap_policy = (UINT32_MAX & ~31U) | 1U;')
assert boundary==expected,'boundary changes beyond documented static initialization seed'
target=out/'evidence/final-02-report.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
report['final_source_sha256']=final;report['inputs_changed_after_initial_snapshot']=changed
report['final_test_report_pending']=False
report['final_evidence_binding']={'report':'.build/c3-ap-timeout-final-02/report.json','report_sha256':hashlib.sha256(raw).hexdigest(),'positive_cases':42,'exact_semantic_controls':8,'historical_actual_callback_failures':3,'all_test_report_sources_match_current':True,'normal_complete_settings_tu_bytes_match_production':True,'boundary_variant_changes_only_static_revision_seed':True,'cases_independently_read':['restore','restore-invalid','concurrent-settings','pending-late-association','revision-exhaustion'],'reviewer_reran_test_suite':False}
report['test_scope_and_limits'][3]='Final42-case report now covers raw valid/invalid persisted-NVS restoration without rewrite, two actual settings writers/400commits with2000atomic snapshots, and isolated static max-revision admission seed; documented seed is not a normal NVS restoration state. Eight semantic controls and three historical failures were inspected and input hashes independently verified.'
report['reviewed_utc_final']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report['findings']=[];report['open_findings']=[]
report['result']='No actionable correctness regression found in reviewed final production repair; all recorded final inputs match the passing final-02 evidence.'
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Final independent review: no findings;42cases/8controls/3historical input binding verified')
print('Review SHA256',hashlib.sha256(path.read_bytes()).hexdigest())
