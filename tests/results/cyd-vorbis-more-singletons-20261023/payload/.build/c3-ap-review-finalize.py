import datetime,hashlib,json,pathlib
root=pathlib.Path.cwd();out=root/'.build/c3-ap-independent-review-01';report=json.loads((out/'review.json').read_text(encoding='utf-8'))
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
for relative in ['components/esp_wifi/include/esp_wifi.h','components/esp_netif/include/esp_netif.h','components/esp_netif/lwip/esp_netif_lwip.c','components/esp_netif/esp_netif_handlers.c']:
    source=sdk/relative;raw=source.read_bytes();target=out/'sdk'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    report.setdefault('sdk_source_sha256',{})[str(source)]=hashlib.sha256(raw).hexdigest()
production=['idf/esp32c3-oled-native/main/network_service.c','idf/esp32c3-oled-native/main/runtime_settings.c','idf/esp32c3-oled-native/main/runtime_settings.h']
report['production_unchanged_after_review']={name:hashlib.sha256((root/name).read_bytes()).hexdigest()==report['source_sha256'][name] for name in production}
assert all(report['production_unchanged_after_review'].values())
report['reviewed_contracts']=[
 'One deadline/policy owner is the existing wifi_rssi task at100ms; RSSI cadence2s, priority2/stack2048/task placement unchanged; no timer callback, new task or direct AP esp_restart remains.',
 'Facts are coherent under a short portMUX; no Wi-Fi/netif/restart SDK call executes under that mux. Callback/retry/sleep operation count and monotonic version reject overlapping or stale owner observations.',
 'Facts version UINT64_MAX is fail-closed through valid=false rather than wrapping authorization. Operation count is balanced on all modified actual entry/exit paths.',
 'Default0, failed AP configuration, online state, disabled setting, negative clock, unavailable/full-interval saturation and sleep operations cannot admit restart.',
 'Every accepted softap save, including same-value and0->1 coalescing, advances one packed27-bit revision. Value and revision are observed in one atomic32-bit load.',
 'Softap setter serializes under existing finite writer lock, rejects revision exhaustion before NVS writes, preserves runtime namespace/key and only atomically publishes after successful commit; no fallible step remains between commit and publication.',
 'runtime_settings_init is still sequential boot startup at its sole production caller; reload creates fresh boot-local revision1, not a runtime writer operation.',
 'Due restart proves APSTA mode, exact NOT_CONNECT, down station netif and successful zero-IP read, then rechecks facts/config. Mode/association/IP query failures suppress admission.',
 'Activity ownership excludes the actual deep-sleep CAS; existing OTA owns its own activity and exact reboot lease. AP reserve failure stores no ordinary deferred reboot and rearms from fresh SDK return time.',
 'Final successful lease ownership does not replace eligibility: actual live facts/config/SDK checks run again before immediate restart; only own lease is cancelled on a returning seam/rejection.',
 'Pending async-connect intent is not cleared by elapsed grace or NOT_CONNECT alone. Cancellation is requested only after live disconnected proof; pending clears only after ESP_OK and unchanged operation version, never over a newer callback/retry.',
 'Cancellation and restart are separate branches. A successful cancellation cannot restart in that same iteration and always requires a fresh full interval and new live proof; failed cancellation stays pending.',
 'Pinned SDK esp_wifi_sta_get_ap_info documents disconnect status but does not prove every async command finished. esp_wifi_disconnect ESP_OK is treated as accepted cancellation; later final SDK/live checks remain necessary.',
 'Pinned default DHCP netif disconnected handler calls esp_netif_down; active DHCP down resets IP info before netif down. Requiring a successfully read zero stored IP is a conservative live guard.',
 'Settings/RF/callbacks arriving after the documented final application arbitration check cannot be atomically excluded by this SDK restart API; this review does not introduce a stronger history/RF contract.'
]
report['findings']=[]
report['result']='No actionable correctness regression found in the reviewed production repair.'
report['reviewed_utc_final']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report['test_scope_and_limits']=[
 'Frozen initial runner compiles complete runtime_settings.c and exact network prefix/function spans (startup, callback, retry, sleep preparation, RSSI loop and AP helpers), not the entire network_service translation unit.',
 'The active credential loader is a seam that fills one boot profile. No AP facts, owner policy, acknowledgement or deadline is privately assigned by the fixture.',
 'SDK/netif layouts and observations, RTOS clock/notifications, deep-sleep activity, reboot lease internals and shared power policy are modeled seams in this AP runner; actual reboot and shared power implementations have separate suites.',
 'The initial frozen37-case runner did not cover restored-NVS delay, packed revision exhaustion or concurrent writers/snapshots. Integration agent is adding these tests without production changes; final report binding will identify coverage actually executed.',
 'Read-only review did not run target GCC/Clang, physical RF/DHCP, reset, OTA flash power loss, heap/stack HWM or physical sleep timing. SDK call durations are not proven bounded.'
]
report['final_test_report_pending']=True
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Read-only production review: no findings; final test-report binding pending')
