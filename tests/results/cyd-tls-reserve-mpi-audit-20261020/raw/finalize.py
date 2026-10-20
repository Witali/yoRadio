"""Add final discovered guard observations; retain initial report unchanged."""
import hashlib,json,pathlib,re
OUT=pathlib.Path(__file__).resolve().parent
path=OUT/'report.json'; initial=path.read_bytes(); assert not (OUT/'report-initial.json').exists()
(OUT/'report-initial.json').write_bytes(initial)
report=json.loads(initial); inputs=report['evidence']['inputs']; sha=lambda b:hashlib.sha256(b).hexdigest()
tool=next((p,v) for p,v in inputs.items() if p.endswith('tools\\patch_tls_rx_reserve.py'))
source=(OUT/tool[1]['snapshot']).read_text(encoding='utf-8')
expected=re.search(r"SOURCE_SHA256 = '([a-f0-9]{64})'",source)[1]
comparison=report['donor_dynamic_comparison']['sdk_comparison']
actual=comparison['esp_mbedtls_dynamic_impl.c']
report['donor_dynamic_comparison']['hash_guard_observation']={
 'donor_patch_expected_normalized_sha256':expected,
 'cyd_sdk602_actual_normalized_sha256':actual['cyd_lf_sha256'],
 'installed_donor_sdk61_actual_normalized_sha256':actual['donor_lf_sha256'],
 'cyd_matches_donor_patch_guard':actual['cyd_lf_sha256']==expected,
 'installed_donor_sdk61_matches_guard':actual['donor_lf_sha256']==expected,
 'interpretation':'The existing donor RX patch hash guard does not admit either of these current installed source snapshots. This is a static compatibility observation, not an executed failed build or a claim about historical donor qualified builds/options. The preserved diff shows the installed6.1 vs6.0.2 difference is in TLS1.3 CCS sizing conditions; the frozen CYD profile has TLS1.3 disabled and dynamic buffers disabled. Do not weaken the old guard or port that unrelated SDK behavior as part of the static reserve candidate.'}
report['frozen_profile_context']='Existing build-c3-transfer metadata at capture time, including opt-in TLS_INPUT_RECLAIM=y; this is not an assertion that the production Kconfig default was changed (it remains n in captured source).'
record={'sha256':sha(pathlib.Path(__file__).read_bytes()),'bytes':pathlib.Path(__file__).stat().st_size,'role':'Final audit binding helper','snapshot':None}
target=OUT/'snapshots'/record['sha256']; target.write_bytes(pathlib.Path(__file__).read_bytes()); record['snapshot']=str(target.relative_to(OUT));inputs[str(pathlib.Path(__file__).resolve())]=record
report['evidence']['before_after']={p:{'before_sha256':v['sha256'],'after_sha256':sha(pathlib.Path(p).read_bytes()),'unchanged':sha(pathlib.Path(p).read_bytes())==v['sha256']} for p,v in inputs.items()}
assert all(v['unchanged'] for v in report['evidence']['before_after'].values())
report['evidence']['all_inputs_unchanged_after']=True
report['evidence']['initial_report_sha256']=sha(initial)
report['evidence']['payloads']={str(p.relative_to(OUT)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file() and p!=path}
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'report_sha256':sha(path.read_bytes()),'inputs':len(inputs),'payloads':len(report['evidence']['payloads']),'all_inputs_current':True,
                  'donor_patch_guard_matches_cyd':False,'builds_crypto_network_runs':0},indent=2))
