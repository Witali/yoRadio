import datetime,hashlib,json,pathlib
root=pathlib.Path.cwd();out=root/'.build/cyd-output-telemetry-independent-review-01';out.mkdir(parents=True,exist_ok=False)
reports=['.build/cyd-output-metrics-review-01/review.json','.build/cyd-output-metrics-03/report.json','.build/cyd-output-telemetry-01/report.json','.build/cyd-health-output-telemetry-01/report.json','.build/cyd-stream-output-telemetry-03/report.json']
files=set();evidence={};binding={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
for name in reports:
    path=root/name;raw=path.read_bytes();data=json.loads(raw);evidence[name]=sha(raw);files.add(path)
    binding[name]={}
    for relative,digest in data.get('source_sha256',{}).items():
        source=root/relative;files.add(source);binding[name][relative]=sha(source.read_bytes())==digest
files.update((root/'idf/esp32-cyd2usb-native/main'/name) for name in ['native_audio_output.c','native_health.h','native_health_json.c','web_service.c','native_output_metrics.c','native_output_metrics.h','native_health.c','compat/idf6_i2s_compat.h','compat/idf5_legacy_dac_backend.cpp','CMakeLists.txt'])
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2')
files.update((sdk/'components'/name) for name in ['esp_driver_i2s/i2s_common.c','esp_driver_i2s/i2s_private.h','esp_driver_i2s/include/driver/i2s_common.h','esp_driver_i2s/include/driver/i2s_types.h','esp_driver_dac/dac_continuous.c','esp_driver_dac/include/driver/dac_continuous.h'])
files.add(root/'idf/esp32-cyd2usb-native/build-c3-transfer/config/sdkconfig.h')
files.add(pathlib.Path(__file__).resolve())
hashes={};mapping={}
for path in sorted(files):
    raw=path.read_bytes();digest=sha(raw);snapshot=out/'snapshots'/digest;snapshot.parent.mkdir(exist_ok=True)
    if not snapshot.exists():snapshot.write_bytes(raw)
    hashes[str(path.resolve())]=digest;mapping[str(path.resolve())]=str(snapshot.relative_to(out))
report={'passed':False,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only independent review of frozen integrated CYD output-backend telemetry, pinned SDK driver callback/IRAM contracts, health serialization/HTTP forwarding and host evidence. No production/test/Git edits, SDK/app builds, rerun of test suites or device access.','input_sha256':hashes,'snapshot_map':mapping,'evidence_sha256':evidence,'evidence_inputs_current_at_capture':binding,'actionable_findings':[],'limits':[]}
assert all(all(values.values()) for values in binding.values())
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n')
print('Captured',len(hashes),'inputs; all report source bindings current')
