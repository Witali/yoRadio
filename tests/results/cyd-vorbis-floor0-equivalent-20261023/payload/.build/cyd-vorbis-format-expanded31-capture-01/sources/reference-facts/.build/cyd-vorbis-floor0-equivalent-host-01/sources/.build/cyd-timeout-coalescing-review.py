import datetime,hashlib,json,pathlib
root=pathlib.Path.cwd();main=pathlib.Path('idf/esp32-cyd2usb-native/main')
files=[main/'network_runtime.c',main/'network_settings.c',main/'network_settings.h',main/'web_network_settings.c',pathlib.Path('docs/CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md'),pathlib.Path('tests/results/network-power-transfer-20261019/n5-integration-plan.json')]
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Quick independent read-only code/contract sanity check of CYD desired timeout coalescing. No CYD production/test edits, no new runtime execution or physical-device proof.','source_sha256':{p.as_posix():hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},'scenario':'An offline AP timer is armed for timeout1; two durable saves1->0->1 complete between owner observations, advancing desired revision twice. The next owner observation sees timeout1 again.','facts':[
 'network_settings publishes only the latest coherent committed record/revision; it does not maintain an event history or per-field change generation.',
 'owner_step refresh_settings samples that latest record at the next owner iteration; ordinary cadence is100ms with no hard SDK latency bound.',
 'poll_ap_timeout rearms on unarmed state, changed sampled timeout value or changed connection epoch. It does not rearm solely because desired_revision changed, preserving hostname-only edit behavior.',
 'Therefore a transient saved0 overwritten by saved1 before owner sampling can retain the original deadline; this is a real consequence of the current code, not a claim every durable mutation was applied.',
 'If zero is the latest value during poll, the owner cancels. If zero becomes latest during either final eligibility check, the desired revision/value comparison rejects restart. If zero was observed then later1 is observed, the new interval arms from that later owner observation.',
 'POST explicitly reports application_pending:true and rebooting:false. The integration plan specifies latest committed RAM snapshots and rearm from owner observation time; it does not promise lossless application of every intermediate save.'
 ],'classification':'Latest-desired coalescing/observation boundary; no demonstrated violation of the agreed sampling contract. A stronger promise that every transient durable0 cancels an existing timer would require explicit per-field generation/history or synchronous application acknowledgement, which is not currently agreed.','suggested_tests':[
 'Arm1, advance near due, save0 then1 without fixture_step, then fixture_step: verify/document retained deadline and no false claim that transient0 was applied.',
 'Arm1, save0 then fixture_step: assert cancelled. Save1 then fixture_step: assert a fresh full interval from this observation, never the old deadline.',
 'At due block a live-query seam, save0 and leave it latest, release: assert final revision/value validation suppresses restart.',
 'During a final check save0 then1 after the owner snapshot: changed revision must suppress that stale authorization, followed by conservative fresh interval.'
 ],'requested_change':'No CYD code change requested by this review. Parent may add explicit boundary documentation/regression if useful; do not silently impose a stronger history-processing requirement.'}
out=root/'.build/cyd-n5-timeout-coalescing-review.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Recorded CYD latest-desired coalescing facts and test proposal')
