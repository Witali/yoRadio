import datetime,hashlib,json,pathlib,subprocess
root=pathlib.Path.cwd();out=root/'.build/c3-ap-independent-review-01';out.mkdir(parents=True,exist_ok=False)
main=pathlib.Path('idf/esp32c3-oled-native/main')
files=[main/n for n in ['network_service.c','network_service.h','runtime_settings.c','runtime_settings.h','websocket_service.c','websocket_service.h','deep_sleep_clock.c','deep_sleep_clock.h','web_ota.c']]
files += [pathlib.Path('tests/run-c3-ap-timeout.py'),*list(pathlib.Path('tests/native/c3_ap_timeout').rglob('*'))]
hashes={}
for relative in files:
    source=root/relative
    if not source.is_file():continue
    raw=source.read_bytes();target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);hashes[relative.as_posix()]=hashlib.sha256(raw).hexdigest()
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],text=True).strip(),'scope':'Independent read-only C3 AP-timeout repair review: actual callback/owner/retry/sleep admission, packed revision/NVS publication, checked pending connection cancellation and immediate reboot lease. No deferred AAC work, production edits, tests edits, index changes, firmware builds or device operations. Inputs may change during integration.','source_sha256':hashes,'findings':[]}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Frozen',len(hashes),'production/test inputs')
