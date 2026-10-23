import hashlib,json
from pathlib import Path
root=Path.cwd(); path=root/'.build/cyd-network-lint-triage.json'
report=json.loads(path.read_text(encoding='utf-8'))
assert len(report['new_warning_instances'])==4 and not report['removed_warning_instances']
assert {r['check'] for r in report['new_warning_instances']}=={'bugprone-narrowing-conversions','bugprone-suspicious-memory-comparison'}
report['triage']=[
    dict(check='bugprone-narrowing-conversions',instances=3,
        files=['idf/esp32-cyd2usb-native/main/native_state.c:46','idf/esp32-cyd2usb-native/main/network_runtime.c:380','idf/esp32-cyd2usb-native/main/websocket_service.c:266'],
        classification='Value-range-preserving integer promotion; no unsafe narrowing or production defect found.',
        reasoning='Each conditional chooses either an int8_t RSSI field/parameter or integer zero. C promotes the conditional to int, but its result is always in [-128,127]. Assigning/passing it back to int8_t is representable and defined. Frozen network_status.h, native_state.h/.c and actual callback/WS code establish the field and parameter types. No cast, suppression or source rewrite is needed.',
        evidence=['.build/lint-cyd-network-vendor-final/analysis/idf__esp32-cyd2usb-native__main__native_state.c.log','.build/lint-cyd-network-vendor-final/analysis/idf__esp32-cyd2usb-native__main__network_runtime.c.log','.build/lint-cyd-network-vendor-final/analysis/idf__esp32-cyd2usb-native__main__websocket_service.c.log']),
    dict(check='bugprone-suspicious-memory-comparison',instances=1,
        files=['idf/esp32-cyd2usb-native/main/websocket_service.c:338'],
        classification='Nonblocking representation-portability caveat retained; no unsafe access, incorrect payload or new high-risk defect reproduced.',
        reasoning='The three added boolean flags introduce padding in the private ws_status_key_t. capture_status explicitly memset-zeroes the whole key before member population, and both previous/current objects have static storage; it then compares and copies them only in HTTPD owner context. This is not an uninitialized automatic struct or a credentials comparison. A portable C language guarantee that struct assignment preserves every padding byte is still absent: unusual compiler treatment could cause unnecessary status revisions/sends. This warning is not relabeled universally harmless or a memory-safety bug. Existing actual WS schedules cover unchanged suppression/heartbeat and all network validity changes; no new entire suite or cosmetic layout edit was requested.',
        evidence=['.build/lint-cyd-network-vendor-final/analysis/idf__esp32-cyd2usb-native__main__websocket_service.c.log','tests/native/cyd_websocket_test.c:637'])
]
report['novel_warning_classes']=2
report['novel_warning_instances']=4
report['custom_warning_triage']='The sole custom-focused warning is the pre-existing stream_frames.h zero-initialized enum finding also present in the vendor/baseline flow. No custom FLAC callback/lifecycle warning was introduced; this does not replace behavioral or target execution evidence.'
report['complete']=True
path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),vendor=report['vendor'],custom=report['custom'],novel_classes=2,novel_instances=4,new_reproduced_production_defects=0),indent=2))
