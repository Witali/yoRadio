import hashlib,json,pathlib,datetime,subprocess
root=pathlib.Path.cwd()
out=root/'.build/n5-independent-review-01'
out.mkdir(parents=True,exist_ok=False)
main=pathlib.Path('idf/esp32-cyd2usb-native/main')
names=['network_runtime.c','network_runtime.h','network_status.h','network_settings.c','network_settings.h','network_service.c','network_service.h','app_main.c','CMakeLists.txt','web_service.c','web_network_settings.c','web_network_settings.h','web_pages.cpp','web_reboot.c','web_reboot.h','web_time.c','web_time.h','web_ota.c','web_wifi.c','board_config.h']
sources={}
for name in names:
    p=root/main/name
    if not p.exists():continue
    raw=p.read_bytes();target=out/'sources'/main/name
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    sources[(main/name).as_posix()]=hashlib.sha256(raw).hexdigest()
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2')
for name in ['components/esp_netif/include/esp_netif.h','components/esp_netif/lwip/esp_netif_lwip.c','components/esp_system/include/esp_system.h']:
    p=sdk/name;raw=p.read_bytes();target=out/'sdk'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    sources[str(p)]=hashlib.sha256(raw).hexdigest()
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],text=True).strip(),'scope':'Independent read-only N5 integration correctness review. Frozen production inputs and pinned local SDK. Runtime/UI tests may still be changing; no hardware, scheduler, target ABI or live RF proof. No production or index edits.','source_sha256':sources,'findings':[]}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Frozen',len(sources),'production/SDK inputs')
