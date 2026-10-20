import datetime, difflib, hashlib, json, pathlib
ROOT=pathlib.Path.cwd(); OUT=pathlib.Path(__file__).resolve().parent
SDK=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2')
cap=json.loads((OUT/'capture.json').read_text()); assert not (OUT/'report.json').exists()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
extra={}
def freeze(path,role,copy=True):
 path=path.resolve();raw=path.read_bytes();digest=sha(raw);record={'sha256':digest,'bytes':len(raw),'role':role}
 if copy:
  target=OUT/'snapshots'/digest
  if not target.exists():target.write_bytes(raw)
  record['snapshot']=str(target.relative_to(OUT))
 extra[str(path)]=record
for name in ['components/esp_security/src/init.c','components/esp_security/src/esp32/esp_crypto_clk.h','components/esp_security/src/esp_crypto_periph_clk.c',
 'components/mbedtls/mbedtls/tf-psa-crypto/core/psa_crypto_driver_wrappers.h','components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c',
 'components/mbedtls/mbedtls/tf-psa-crypto/include/mbedtls/platform_util.h','components/mbedtls/port/bignum/bignum_alt.c','components/mbedtls/port/include/bignum_impl.h',
 'components/esp-tls/esp_tls_mbedtls.c']:
 freeze(SDK/name,'Additional SDK source discovered while tracing startup/allocator ownership')
freeze(ROOT/'idf/esp32-cyd2usb-native/main/compat/input_reclaim/enable.cmake','Existing CYD allocator wrapper integration')
for name in ['mbedtls/library/libmbedtls.a','mbedtls/library/libtfpsacrypto.a','mbedtls/tf-psa-crypto/platform/libplatform.a']:
 freeze(ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer/esp-idf/mbedtls'/name,'Existing linked-library identity; hash-only, no decoder/crypto execution',False)
freeze(pathlib.Path(__file__),'Audit analysis helper')
save('supplement.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':extra})
inputs=cap['inputs']|extra
def text(path):
 key=str(path.resolve()); return (OUT/inputs[key]['snapshot']).read_text(encoding='utf-8')
def entry(path,token):
 path=path.resolve();raw=text(path);line=next(i for i,s in enumerate(raw.splitlines(),1) if token in s)
 return {'path':str(path),'line':line,'token':token,'sha256':inputs[str(path)]['sha256'],'snapshot':inputs[str(path)].get('snapshot'),
         'link':'['+path.name+':'+str(line)+']('+str(path).replace('\\','/')+':'+str(line)+')'}
def s(name,token):return entry(SDK/name,token)
def r(name,token):return entry(ROOT/name,token)
cfg={}
for line in text(ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer/sdkconfig').splitlines():
 if line.startswith('CONFIG_') and '=' in line:
  k,v=line.split('=',1);cfg[k]=v
 elif line.startswith('# CONFIG_') and line.endswith(' is not set'):cfg[line[2:-11]]='n'
selected=['CONFIG_IDF_TARGET','CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC','CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC','CONFIG_MBEDTLS_DYNAMIC_BUFFER',
 'CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH','CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN','CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN','CONFIG_MBEDTLS_SSL_PROTO_TLS1_2',
 'CONFIG_MBEDTLS_SSL_PROTO_TLS1_3','CONFIG_MBEDTLS_CIPHER_MODE_CBC','CONFIG_MBEDTLS_HARDWARE_MPI','CONFIG_LIBC_PICOLIBC','CONFIG_FREERTOS_UNICORE',
 'CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS','CONFIG_ESP_TLS_USING_MBEDTLS','CONFIG_YORADIO_TLS_INPUT_RECLAIM','CONFIG_MBEDTLS_MPI_USE_INTERRUPT']
profile={k:cfg.get(k,'absent') for k in selected}
assert profile['CONFIG_MBEDTLS_DYNAMIC_BUFFER']=='n' and profile['CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH']=='n'
assert profile['CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN']=='16384' and profile['CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN']=='4096'
rows=json.loads(text(ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer/compile_commands.json'))
names=['/library/ssl_tls.c','/platform/platform.c','/port/esp_mem.c','/src/locks.c','/src/esp_crypto_lock.c','/port/esp_psa_crypto_init.c','/esp_security/src/init.c']
rows=[row for row in rows if any(row['file'].replace('\\','/').endswith(name) for name in names)]
save('selected-compile-rows.json',{'executed':False,'purpose':'Existing actual target compile-command metadata only; no compile/preprocessor/tool run by this audit.','rows':rows})
comparison={}
for name in ['esp_mbedtls_dynamic_impl.c','esp_mbedtls_dynamic_impl.h']:
 left=pathlib.Path('C:/Work/yoRadio/.idf/v6.1/components/mbedtls/port/dynamic')/name;right=SDK/'components/mbedtls/port/dynamic'/name
 a=text(left);b=text(right);diff=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(left),tofile=str(right)))
 (OUT/(name+'.diff')).write_text(diff,encoding='utf-8')
 comparison[name]={'donor_raw_sha256':inputs[str(left)]['sha256'],'cyd_raw_sha256':inputs[str(right)]['sha256'],
                   'donor_lf_sha256':sha(a.encode()),'cyd_lf_sha256':sha(b.encode()),'same_normalized_text':a==b,'diff_payload':name+'.diff'}
save('sdk-dynamic-comparison.json',comparison)
report={
 'status':'read_only_audit_complete_both_candidates_unimplemented_and_unqualified',
 'stage':13,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':cap['scope'],'no_claims':['No guessed reserve byte count (including17058).','No heap saving, reduced fragmentation, CPU/timing gain or hardware qualification claimed.',
 'No default TLS record sizes, cores, timings, input pool, stacks or IRAM choices changed.','No compilation, preprocessor, crypto or network operations ran.'],
 'frozen_cyd_profile':profile,
 'summary':[
  'C3 dynamic RX reserve cannot be copied into the current CYD static profile. Prefer a distinct opt-in static RX call-site reserve using the existing SDK full-record buffer formula and exact free pairing; it is not a heap-capacity saving.',
  'Current CYD idle-input reclaim already has stronger pin/detach/bounded retry ownership than the donor TLS input wrapper. Do not replace it or import donor pool-floor/headroom policies.',
  'SDK6.0.2 explicitly initializes common libc/PSA objects before app_main, but no eager initializer for s_crypto_mpi_lock was found. The normal MPI API remains lazy and can be warmed in normal app_main before service allocations. Exact first-use boot tracing remains required before claiming benefit.',
  'Early MPI APIs return void. The underlying lazy mutex constructor calls abort on allocation failure; no recoverable esp_err_t contract exists.'],
 'allocator_and_static_routes':{
  'public_pair':{'description':'mbedtls_calloc/free dispatch through process-wide function pointers initialized to ESP SDK esp_mbedtls_mem_calloc/free. INTERNAL_MEM_ALLOC calloc uses heap_caps_calloc(INTERNAL|8BIT), free uses heap_caps_free. Reserved static storage must be intercepted by the matching free route before heap_caps_free; never send it to libc realloc/free or heap_caps_free.',
   'entries':[s('components/mbedtls/port/include/mbedtls/esp_config.h','#define MBEDTLS_PLATFORM_STD_CALLOC'),s('components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c','static void * (*mbedtls_calloc_func)'),s('components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c','int mbedtls_platform_set_calloc_free('),s('components/mbedtls/port/esp_mem.c','void *esp_mbedtls_mem_calloc('),s('components/mbedtls/port/esp_mem.c','void esp_mbedtls_mem_free(')]},
  'static_setup':{'description':'With DYNAMIC_BUFFER=n, mbedtls_ssl_setup allocates in_buf directly as calloc(1, MBEDTLS_SSL_IN_BUFFER_LEN), then out_buf as calloc(1, MBEDTLS_SSL_OUT_BUFFER_LEN), then handshake structures. No dynamic struct header precedes these allocations. Error cleanup frees both and clears pointers/config. The RX allocation statement is the bounded source-patch candidate.',
    'entries':[s('components/mbedtls/mbedtls/library/ssl_tls.c','int mbedtls_ssl_setup('),s('components/mbedtls/mbedtls/library/ssl_tls.c','ssl->in_buf = mbedtls_calloc(1, in_buf_len);'),s('components/mbedtls/mbedtls/library/ssl_tls.c','ssl->out_buf = mbedtls_calloc(1, out_buf_len);')]},
  'size_formula':{'description':'Static slot capacity should be exactly MBEDTLS_SSL_IN_BUFFER_LEN under the audited full RX16384 configuration, including SDK header and configured cipher overhead. Do not add SSL_BUF_HEAD_OFFSET_SIZE or a second TLS header/payload-overhead term. That extra allowance belongs to the donor dynamic set-static path, not static setup. TX remains4096 content; no literal allocation-size claim is derived without actual compiler macro/config qualification.',
   'entries':[s('components/mbedtls/mbedtls/library/ssl_misc.h','#define MBEDTLS_SSL_PAYLOAD_OVERHEAD'),s('components/mbedtls/mbedtls/library/ssl_misc.h','#define MBEDTLS_SSL_HEADER_LEN 13'),s('components/mbedtls/mbedtls/library/ssl_misc.h','#define MBEDTLS_SSL_IN_BUFFER_LEN'),r('idf/esp32c3-oled-native/main/tls_large_reserve.c','TLS_RESERVE_CAPACITY =')]},
  'reset_and_free':{'description':'Static session reset retains both buffer allocations and clears the full configured lengths; it must not release the slot. Final mbedtls_ssl_free calls mbedtls_zeroize_and_free, which zeroizes and calls mbedtls_free. Setup error paths use mbedtls_free directly, so the free wrapper must zeroize its claimed bytes before marking the slot available even when the SDK has not zeroized first.',
   'entries':[s('components/mbedtls/mbedtls/library/ssl_tls.c','void mbedtls_ssl_session_reset_msg_layer('),s('components/mbedtls/mbedtls/library/ssl_tls.c','void mbedtls_ssl_free('),s('components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c','void mbedtls_zeroize_and_free(')]},
  'resize':{'description':'VARIABLE_BUFFER_LENGTH=n in the frozen profile. If enabled later, resize_buffer allocates a new mbedtls_calloc buffer, copies min(old,new), zeroizes/frees old, and only then publishes the new pointer/length. This is not libc realloc. Current bounded reserve should reject that option until all resize/copy/failure/reuse paths are qualified; passing static storage to a heap realloc remains forbidden.',
   'entry':s('components/mbedtls/mbedtls/library/ssl_tls.c','static int resize_buffer(')},
  'runtime_pair_risk':'mbedtls_platform_set_calloc_free changes both process-wide callbacks without live-owner synchronization. No call was found in current CYD main or ESP-TLS. Do not use a temporary allocator swap to tag RX. Future callback replacement while any reserved allocation is live must be rejected by integration contract or be separately paired/qualified.'},
 'donor_dynamic_comparison':{
  'facts':'C3 Kconfig requires DYNAMIC_BUFFER and INTERNAL_MEM_ALLOC. Broad reserve is size-eligible (minimum full RX content), so an unrelated large allocation may occupy it. RX-only option avoids this using four explicit dynamic call sites. Its minimum1 accepts small cached RX too; not a size tag. C3 input wrapper pre-reclaims on largest-block observations and automatically trims/funds the reserve at bind/connection, unlike current CYD service.',
  'entries':[r('idf/esp32c3-oled-native/main/Kconfig.projbuild','config YORADIO_TLS_LARGE_BLOCK_RESERVE'),r('idf/esp32c3-oled-native/main/Kconfig.projbuild','config YORADIO_TLS_RX_ONLY_RESERVE'),r('tools/patch_tls_rx_reserve.py','RX_FUNCTIONS ='),r('idf/esp32c3-oled-native/main/tls_input_reserve.c','void tls_input_reserve_prepare_connection(void)')],
  'sdk_comparison':comparison,
  'dynamic_routes':'SDK CMake adds dynamic sources only when DYNAMIC_BUFFER is set. Four RX sites allocate header+post-handshake static-conversion buffer, reset full RX, record-sized RX, and small16-byte cached RX. esp_mbedtls_free_buf converts interior buf back to its header/base before mbedtls_free. Dynamic wrappers replace setup/free/reset and require exact paired call-site review. Even if donor normalized source hash matches6.0.2, those functions are not the current static RX route.',
  'dynamic_entries':[s('components/mbedtls/CMakeLists.txt','if(CONFIG_MBEDTLS_DYNAMIC_BUFFER)'),s('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','void esp_mbedtls_free_buf('),s('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','esp_err_t esp_mbedtls_dynamic_set_rx_buf_static('),s('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','int esp_mbedtls_reset_add_rx_buffer('),s('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','int esp_mbedtls_add_rx_buffer('),s('components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','int esp_mbedtls_free_rx_buffer(')],
  'not_ported':'Do not enable DYNAMIC_BUFFER to make the donor patch fit; do not transplant donor minimum queue limit,32KiB headroom, large allocation threshold, reserve byte count or per-codec expansion policy.'},
 'static_reserve_candidate_unimplemented':{
  'preferred_scope':'New explicit static RX-only call-site hook in a generated build-local copy of actual ssl_tls.c; no SDK checkout edit, no wholesale crypto allocator or record-size change.',
  'configuration_guards':['Defaultn and IDF_TARGET_ESP32 with ESP_TLS_USING_MBEDTLS, MBEDTLS_INTERNAL_MEM_ALLOC and !MBEDTLS_CUSTOM_MEM_ALLOC.',
    '!MBEDTLS_DYNAMIC_BUFFER and !MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH; full RXcontent==16384 and current TXcontent==4096 compile assertions for this initial profile.',
    'Recoverable-failure profile !HEAP_ABORT_WHEN_ALLOCATION_FAILS for OOM return tests. Do not silently select or alter any dependency.',
    'Strict default calloc/free callback pair, no process-wide callback replacement while reserve live. Preserve native_health sole failed-allocation hook and existing native_input_reclaim owner/pins.'],
  'guarded_files':[s('components/mbedtls/mbedtls/library/ssl_tls.c','int mbedtls_ssl_setup('),s('components/mbedtls/mbedtls/library/ssl_misc.h','#define MBEDTLS_SSL_PAYLOAD_OVERHEAD'),s('components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c','static void * (*mbedtls_calloc_func)'),s('components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c','void mbedtls_zeroize_and_free('),s('components/mbedtls/port/esp_mem.c','void *esp_mbedtls_mem_calloc('),s('components/mbedtls/port/include/mbedtls/esp_config.h','#define MBEDTLS_PLATFORM_STD_FREE')],
  'source_patch_contract':'Guard SDK version6.0.2, selected actual component directory, exact raw source hashes and the generated configuration/header tuple. Replace exactly the one RX allocation statement inside mbedtls_ssl_setup, leave TX/handshake/all unrelated bytes unchanged. Replace exactly one target source, preserve original per-source flags/includes/config, set configure dependencies on source/tool/guard headers. New revisions or dynamic sources fail closed. No private context-layout manipulation.',
  'slot_contract':'One max_align_t-aligned static slot sized by the SDK IN_BUFFER_LEN expression; CAS ownership, zero requested bytes before publishing, record used size. Reject zero/overflow/oversize/reserve claim from ISR; delegate ordinary SDK semantics. Concurrent contexts fall back to their normal allocator. Free intercept recognizes exact base pointer, wipes before release publication, never forwards that address to heap free, preserves other pointers/NULL. SDK allocator ownership forbids stale/double free; no ABA protection for invalid stale pointers is claimed.',
  'composition':'RX hook tries its static slot, otherwise calls the normal public mbedtls_calloc route so current input-reclaim wrapper still delegates original once first and retains its bounded retry/pin behavior. Add one esp_mbedtls_mem_free owner-aware wrapper; avoid duplicate calloc wrapper definitions. Keep --undefined retention for callback-pointer routes and verify actual final ELF. Slot release does not rebind/detach/destroy input or allocate/restore slots.',
  'cost_and_measurement':'The .bss slot consumes permanent internal RAM even for HTTP/no TLS, reduces boot heap availability and serves at most one eligible live RX buffer. It can replace one heap request, not create free RAM. Busy contexts still need full ordinary heap storage. Measure .bss/link map, free/largest/internal actual heap, retained slot occupation, input residency and concurrent HTTPS/OTA playback before deciding whether it is worth enabling.'},
 'early_mpi_candidate_unimplemented':{
  'source_verdict':'No explicit before-app MPI mutex creation found in the pinned normal ESP32 SDK path. s_crypto_mpi_lock is static zero; public acquire uses the legacy lazy _lock_acquire route, including when LIBC_PICOLIBC is enabled. libc common static mutex initialization does not initialize this separate variable. An indirect earlier user can still acquire it; only an actual boot trace can settle its first runtime use.',
  'entries':[s('components/esp_security/src/esp_crypto_lock.c','static _lock_t s_crypto_mpi_lock;'),s('components/esp_security/src/esp_crypto_lock.c','void esp_crypto_mpi_lock_acquire(void)'),s('components/esp_libc/src/locks.c','static void LIBC_LOCKS_IRAM_ATTR lock_init_generic('),s('components/esp_libc/src/locks.c','void esp_libc_locks_init(void)'),s('components/esp_libc/src/init.c','ESP_SYSTEM_INIT_FN(init_libc,'),s('components/esp_security/src/init.c','ESP_SYSTEM_INIT_FN(esp_security_init,'),s('components/esp_security/src/esp32/esp_crypto_clk.h','static inline void esp_crypto_clk_init(void) {}'),s('components/mbedtls/port/esp_psa_crypto_init.c','ESP_SYSTEM_INIT_FN(mbedtls_psa_crypto_init_fn,'),s('components/mbedtls/mbedtls/tf-psa-crypto/core/psa_crypto_driver_wrappers.h','static inline psa_status_t psa_driver_wrapper_init(')],
  'preapp_distinction':'libc CORE102 initializes common locks; security SECONDARY103 performs target clock/security setup (ESP32 clock helper empty); PSA SECONDARY104 initializes driver wrappers/key slots/RNG/transaction. PSA mutexes and RNG initialization are not the MPI peripheral lock. The examined driver initializer has only optional test-driver initialization. No claim that every possible build/constructor never performs MPI is made.',
  'startup_plan':'Add a default-off CYD option guarded ESP_TLS_USING_MBEDTLS && MBEDTLS_HARDWARE_MPI && SOC_MPI_SUPPORTED && IDF_TARGET_ESP32 in normal non-bootloader/non-NON_OS application. Include public esp_crypto_lock.h and declare explicit esp_security component dependency (PRIV_REQUIRES is sufficient for app_main-only use). Call public acquire then release once at start of ordinary app_main, with scheduler running and before health/NVS/display/network/audio task allocations. Do not copy C3 deep-sleep fast-path or benchmark behavior into CYD. No constructor/pre-RTOS call, private lock replacement or freeing, crypto calculation, peripheral clock operation or task-affinity change.',
  'oom_and_locking':'_lock_acquire is void and discards its internal int result; lock_init_generic serializes construction using lock_init_spinlock, calls xQueueCreateMutex, and aborts when that returns NULL. Before the scheduler, acquire is a no-op and does not prove initialization. No recoverable ESP_ERR_NO_MEM can be promised. Normal successful warmup must release the same SDK lock; early OOM remains documented SDK abort unless a separately reviewed SDK API is introduced. Other tasks can later block normally; do not hold another application registry/queue lock while warming it.',
  'oom_entry':s('components/esp_libc/src/locks.c','abort(); /* No more semaphores available or OOM */'),
  'public_contract':s('components/esp_security/include/esp_crypto_lock.h','void esp_crypto_mpi_lock_acquire(void);'),
  'real_hardware_lock_route':s('components/mbedtls/port/bignum/bignum_alt.c','esp_crypto_mpi_lock_acquire();'),
  'current_app_entry':r('idf/esp32-cyd2usb-native/main/app_main.c','void app_main(void)'),
  'guarding':'Public API warmup need not patch SDK bytes, but qualify exact SDK lock/header/esp_security init/libc locks/FreeRTOS queue/config hashes and explicit component dependency. A future eager initializer or changed void/OOM behavior invalidates benefit assumptions and requires reevaluation; sourcehash guards are mandatory for any private source instrumentation or patch, not an invented permanent public ABI restriction.',
  'measurement':'Moves at most this SDK mutex first allocation earlier when it was not already created. Does not remove its lifetime allocation or guarantee larger heap blocks. Record actual allocator size and first-use point; no guessed semaphore size, C3 bytes or fragmentation/latency benefit.'},
 'existing_cyd_reclaim_to_preserve':{'description':'Current qualified service keeps owner/pins/retiring, explicit detach, real allocator first and bounded initial target-minus-minimum release budget. The donor atomic raw input pointer, pre-reclaim heuristic and startup pool floor are not an appropriate replacement.',
  'entries':[r('idf/esp32-cyd2usb-native/main/native_input_reclaim.c','void *__wrap_esp_mbedtls_mem_calloc('),r('idf/esp32-cyd2usb-native/main/compat/input_reclaim/enable.cmake','function(native_enable_tls_input_reclaim)')]},
 'unrun_gates':[
  {'id':'R1','name':'Static profile/config/target ABI and hash preflight','checks':'Actual SDK6.0.2 compile of whole patched ssl_tls TU with existing Xtensa flags/includes, SDK IN/OUT capacity symbols and max_align_t checks, full RX16384 unchanged. Exact source replacement/config negative controls, wrong version/source/variable/dynamic/custom/external/abort profile rejection. This audit did not preprocess capacity.'},
  {'id':'R2','name':'Actual allocator/free pairing','checks':'Whole actual SDK setup/reset/free/error paths plus real public mbedtls_calloc/free function-pointer dispatch in target ELF. Pointer of reserved base never reaches heap free/realloc; ordinary pointers/NULL still do. SDK source host seams supplement actual target; no direct fake private function proof. Corrupt free route exact named failure.'},
  {'id':'R3','name':'Reserve lifetime/OOM/two-core concurrency','checks':'Two real FreeRTOS contexts on cores0/1 with barrier-controlled claim and free/zeroization overlap: one slot owner, fallback second, no publication until zeroed, no re-claim before wipe completes. Setup failure at TX or later handshake frees RX; reset retains it; final free releases; repeated lifecycle. Actual allocator failures, fallback+native_input_reclaim pins/detach and malformed zero/overflow requests preserve contracts. No application lock allocation/logging/wait in new slot critical path.'},
  {'id':'R4','name':'Record/protocol/resource and physical gate','checks':'Future encrypted full16384 records, fragmented reads/CBC/GCM/certificates/errors, reset/reuse, simultaneous HTTPS/OTA and streaming, all codecs/output variants. Original app behavior and record sizes unchanged; measure permanent .bss cost and real heap/stack/CPU before enablement. No such network/crypto run occurred here.'},
  {'id':'M1','name':'Fresh boot observation before warmup','checks':'Actual SDK2-core boot traces external _lock_acquire and mutex-create calls in fixed storage without allocation or crypto. Identify MPI lock through public acquire path, then inspect earlier trace by exact lock pointer. Determine whether any constructor/security/PSA path acquired it before app_main; do not write private lock state or assume all preapp allocations are MPI.'},
  {'id':'M2','name':'Real API startup and contention','checks':'With actual SDK esp_crypto_lock.c + esp_libc locks.c + FreeRTOS queue, first normal app_main warmup creates at most one mutex, subsequent calls allocate none. Two-core concurrent first acquire creates once; hold/release contention provides mutual exclusion and no deadlock. Pre-scheduler no-op must not be counted as initialized. Verify startup ordering before service allocations and option-off no extra call; no RSA operation needed.'},
  {'id':'M3','name':'Void API OOM and exact controls','checks':'Fresh isolated boot for injected actual xQueueCreateMutex failure: expected named SDK abort/panic path, not fabricated recoverable error. Finite terminal logs and explicit expected status; no private reset of persistent lock. Controls late/no warmup, missing release, false early pre-RTOS initialization and duplicate lazy construction must trigger named failures. Avoid ordinary uncontrolled crash as success.'},
  {'id':'M4','name':'Production and useful-effect gate','checks':'Full option-on/off builds/lint for all CYD outputs and actual2CPU scheduler, public esp_security dependency, header/config hashes, final ELF symbol routing. Measure first-use actual allocation size and settled memory/largest-block history across fresh boots and later approved TLS/playback/OTA; preserve all existing cores/stacks/timings. Public mutex warmup does not by itself prove fragmentation improvement.'}],
 'evidence':{'capture_sha256':sha((OUT/'capture.json').read_bytes()),'supplement_sha256':sha((OUT/'supplement.json').read_bytes()),'inputs':inputs,
 'existing_compile_rows':'selected-compile-rows.json','dynamic_diff':'sdk-dynamic-comparison.json',
 'before_after':{p:{'before_sha256':v['sha256'],'after_sha256':sha(pathlib.Path(p).read_bytes()),'unchanged':sha(pathlib.Path(p).read_bytes())==v['sha256']} for p,v in inputs.items()}}
}
report['evidence']['all_inputs_unchanged_after']=all(v['unchanged'] for v in report['evidence']['before_after'].values())
assert report['evidence']['all_inputs_unchanged_after'],[p for p,v in report['evidence']['before_after'].items() if not v['unchanged']]
report['evidence']['payloads']={str(p.relative_to(OUT)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file()}
save('report.json',report)
print(json.dumps({'report_sha256':sha((OUT/'report.json').read_bytes()),'inputs':len(inputs),'payloads':len(report['evidence']['payloads']),
 'compile_rows_metadata_only':len(rows),'dynamic_source_same':comparison['esp_mbedtls_dynamic_impl.c']['same_normalized_text'],'all_inputs_current':True,'builds_crypto_network_runs':0},indent=2))
