import datetime,hashlib,json,pathlib,re
root=pathlib.Path.cwd();out=root/'.build/cyd-output-telemetry-independent-review-01';path=out/'review.json';review=json.loads(path.read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def freeze(path):
    path=path.resolve();raw=path.read_bytes();digest=sha(raw);snapshot=out/'snapshots'/digest
    if not snapshot.exists():snapshot.write_bytes(raw)
    review['input_sha256'][str(path)]=digest;review['snapshot_map'][str(path)]=str(snapshot.relative_to(out));return digest
freeze(pathlib.Path(__file__))
review['raw_evidence_sha256']={}
for relative in review['evidence_sha256']:
    directory=(root/relative).parent
    for log in directory.rglob('*.log'):
        if 'sources' in log.relative_to(directory).parts:continue
        review['raw_evidence_sha256'][str(log.relative_to(root))]=freeze(log)
metrics=json.loads((root/'.build/cyd-output-metrics-03/report.json').read_bytes())
backend=json.loads((root/'.build/cyd-output-telemetry-01/report.json').read_bytes())
for directory,data in [(root/'.build/cyd-output-metrics-03',metrics),(root/'.build/cyd-output-telemetry-01',backend)]:
    assert data['passed']
    for name,case in data['cases'].items():
        if name.endswith('/count-limit'):
            variant=name.split('/')[0];log=directory/variant/'count-boundary/test.log';expected='count-limit'
        else:log=directory/(name+'.log');expected=name.split('/')[-1]
        assert case['passed'] and case['status']==0 and log.read_bytes()==('PASS:'+expected+'\n').encode()
    for name,control in data['negative_controls'].items():
        assert control['detected'] and control['status']==80
        raw=(directory/'mutants'/name/'test.log').read_bytes()
        assert raw.startswith(('SEMANTIC_FAILURE:'+control['marker']+':').encode())
        assert b'AddressSanitizer' not in raw and b'runtime error:' not in raw
health=json.loads((root/'.build/cyd-health-output-telemetry-01/report.json').read_bytes())
for variant,text in health['variants'].items():
    lines=text.splitlines();line=next(line for line in lines if line.startswith('HEALTH_MAX='));maximum=json.loads(line.split('=',1)[1])
    assert len(line.split('=',1)[1].encode())==2000
    assert (root/'.build/cyd-health-output-telemetry-01'/(variant+'-test.log')).read_bytes().decode()==text
    assert all(marker in lines for marker in ['HEALTH_UNAVAILABLE_OK','HEALTH_NO_TIMING_SAMPLES_OK','HEALTH_MEASURED_ZERO_OK'])
    assert maximum['output_driver']['requested_bytes']==(1<<64)-1 and maximum['output_driver']['completion_queue_drops']==(1<<32)-1
stream=(root/'.build/cyd-stream-output-telemetry-03/test.log').read_text()
assert '50' in stream and '80' in stream
stream_health=json.loads(next(line for line in stream.splitlines() if line.startswith('HEALTH=')).split('=',1)[1])
assert stream_health['output_driver']==dict(writes=19,requested_bytes=2048,written_bytes=1024,errors=3,timeouts=2,short_writes=1,write_us=123456,max_write_us=6543,timing_samples=17,invalid_time_samples=2,completion_queue_drops=11,timing_enabled=True,saturated=False)
def reference(relative,needle):
    text=(root/relative).read_text();assert needle in text
    return {'file':relative,'line':next(i for i,line in enumerate(text.splitlines(),1) if needle in line)}
main='idf/esp32-cyd2usb-native/main/'
review['reviewed_contracts']=[
 {'subject':'PDM callback lifetime and order','conclusion':'Callback is registered after successful PDM mode initialization and before any preload/enable. Registration failure takes the existing release(false) cleanup and propagates its original error. The SDK copies the stack-local callback descriptor while READY; user_data is NULL. Callback ignores channel/event/context and touches only boot-lifetime metrics state, so it retains no descriptor, event or destroyed channel pointer. Queue availability is explicitly boot-cumulative, including successful registration before a later startup failure.','references':[reference(main+'native_audio_output.c','static bool IRAM_ATTR pdm_completion_queue_drop'),reference(main+'native_audio_output.c','const i2s_event_callbacks_t callbacks')]},
 {'subject':'Pinned classic ESP32 I2S API and queue semantics','conclusion':'SDK6.0.2 i2s_common.h documents ISR callbacks and READY/REGISTERED registration; i2s_common.c copies callbacks and validates IRAM/internal context when configured. Its classic interrupt path invokes on_send_q_ovf after removing a full completion-queue entry and ORs the returned wake flag. Returning false does not erase other SDK wake requests. This is a lost completion-queue event, not evidence of an audible underrun. Existing disable/stop and channel deletion remove the source through SDK ownership; no new callback context requires explicit deregistration.'},
 {'subject':'IRAM and lock structure','conclusion':'New PDM wrapper is IRAM_ATTR and calls only the previously audited IRAM queue-drop helper. Static state and lock are DRAM_ATTR; the helper uses ISR critical entry/exit and no allocator, log or timer API. Task begin/end/snapshot never hold metrics lock across driver calls or clock reads. Prior helper target-object review remains applicable because helper source hashes match exactly. Final linked integrated callback/helper placement and hardware IRQ timing are not established by these host tests.'},
 {'subject':'All three backend write accounting','conclusion':'PDM, continuous DAC and legacy adapter hooks surround their synchronous write APIs, preserve every original return and incomplete-write check, and pass requested/reported bytes in the API caller buffer units. Every DAC written pointer is initialized by its caller. Legacy passes frames*sizeof(uint32_t), not frame or input-PCM count. Prime/bias/idle writes through these APIs are included; PDM preload_data is deliberately excluded and documented separately. Paused paths that return before the driver create no observation.','references':[reference(main+'native_audio_output.c','static esp_err_t pdm_write_block'),reference(main+'native_audio_output.c','static esp_err_t dac_write_block'),reference(main+'native_audio_output.c','static esp_err_t legacy_write_frames')]},
 {'subject':'Snapshot and health publication','conclusion':'The handler obtains one coherent metrics snapshot by value and forwards all fields to the runtime struct. JSON uses exact PRIu32/PRIu64 widths, preserves saturation and timing counters, emits null for unavailable queue/time observations and numeric zero after a valid zero observation. It never reports zero as measured when no timer sample exists. New groups stay below the 256-byte formatting chunk and existing 2304-byte response capacity. Worst-width integration evidence is 2000 bytes and capacity canaries cover all boundaries.','references':[reference(main+'web_service.c','.output_driver=native_output_metrics_snapshot()'),reference(main+'native_health_json.c','const native_output_metrics_t *driver=')]},
 {'subject':'Evidence attribution','conclusion':'Byte-exact complete output and metrics TUs are compiled as separate host units in all three backends and quiet/diagnostic modes. Metrics16/7 and backend22/8 raw positive and named semantic mutant logs match reports. Health three profiles and maximum JSON/null/zero markers match raw logs. Stream handler forwards every supplied driver field and retains50 stream/80 settings cases. Their scopes correctly identify SDK/platform/release/snapshot seams; no backend or physical qualification is inferred from serializer/HTTP-only tests.'}
]
review['actionable_findings']=[]
review['uncovered_or_seamed_paths']=[
 'Backend fixture replaces SDK driver operations, IRAM/DRAM attributes, GPIO, clock and ISR/portMUX behavior with explicit host seams. Its pthread concurrency test does not simulate ESP32 interrupt masking, actual SDK queue scheduling or prove interrupt-latency/performance bounds.',
 'PDM cleanup after registration failure is exercised with successful channel deletion. Delete/disable failure-and-retry and preload/enable failure combinations are not exhaustively injected by this new telemetry suite. Source review found no new changed ownership branch defect; most surrounding cleanup/retry code predates telemetry.',
 'The PDM callback registration struct and event types in host platform.h are models. Actual pinned SDK declaration/implementation compatibility was reviewed directly; parent firmware/target compile remains the gate for integrated compiler/linker ABI and final wrapper/helper IRAM placement.',
 'Health tests supply synthetic driver snapshots to the serializer; stream tests supply a snapshot seam to the real handler. They complement complete-backend tests and do not independently exercise driver allocation, callback registration or DMA.',
 'No TSAN, physical board playback, DMA-transmitted byte count, audible underrun rate, resource-margin, heap-saving or throughput claim is established. Requested/reported buffer bytes, completion queue drops and whole API wall time retain their documented narrower meanings.'
]
review['limits']=['No production/test/Git changes, SDK/app build, test-suite rerun or device operation occurred in this independent review.','Empty actionable findings are not hardware approval; existing target helper review and current host evidence are retained with their explicit scope limits.']
review['input_unchanged_after']={name:sha(pathlib.Path(name).read_bytes())==digest for name,digest in review['input_sha256'].items()}
review['snapshots_unchanged_after']={name:sha((out/review['snapshot_map'][name]).read_bytes())==digest for name,digest in review['input_sha256'].items()}
assert all(review['input_unchanged_after'].values()) and all(review['snapshots_unchanged_after'].values())
review['evidence_verified']={'metrics_positive':len(metrics['cases']),'metrics_semantic_controls':len(metrics['negative_controls']),'backend_positive':len(backend['cases']),'backend_semantic_controls':len(backend['negative_controls']),'health_profiles':list(health['variants']),'health_maximum_bytes':2000,'handler_all_driver_fields_forwarded':True,'raw_log_count':len(review['raw_evidence_sha256'])}
review['passed']=True;review['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'report':str(path),'sha256':sha(path.read_bytes()),'findings':len(review['actionable_findings']),'inputs':len(review['input_sha256']),'evidence':review['evidence_verified']},indent=2))
