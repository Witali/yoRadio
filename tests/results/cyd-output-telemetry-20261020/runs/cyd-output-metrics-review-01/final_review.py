"""Bind the narrow review to final host evidence and unchanged target helper."""
import hashlib
import json
from pathlib import Path
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
HOST=ROOT/'.build/cyd-output-metrics-03'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


objects=json.loads((OUT/'compile-report.json').read_text())
host=json.loads((HOST/'report.json').read_text())
assert objects['passed'] and host['passed']
assert len(host['cases'])==16 and len(host['negative_controls'])==7
assert host['complete_normal_tu_matches_frozen_bytes']
assert all(sha(ROOT/name)==digest for name,digest in host['source_sha256'].items())
helper_files=[MAIN/name for name in ('native_output_metrics.c','native_output_metrics.h')]
assert all(sha(path)==objects['source_sha256'][str(path)] for path in helper_files)
verified_callees={}
for variant,item in objects['variants'].items():
    assert all(sha(Path(path))==digest for path,digest in item['dependency_sha256'].items())
    assert sha(OUT/('objects-'+variant)/'metrics.obj')==item['object_sha256']
    assert sha(OUT/('objects-'+variant)/'sdkconfig.h')==item['config_sha256']
    # objdump -dr does not print literal-data R_XTENSA_32 records. Verify
    # the actual function-call expansion records in all IRAM text sections.
    disassembly=(OUT/(variant+'-disassembly.log')).read_text()
    sections=re.split(r'Disassembly of section ([^:\n]+):\n',disassembly)
    iram='\n'.join(body for name,body in zip(sections[1::2],sections[2::2]) if name.startswith('.iram1.'))
    callees=set(re.findall(r'R_XTENSA_ASM_EXPAND\s+(\w+)',iram))
    assert callees=={'xPortEnterCriticalTimeout','vPortExitCritical'}
    verified_callees[variant]=sorted(callees)
    compile_log=(OUT/(variant+'-compile.log')).read_text(errors='replace')
    assert not re.search(r'\b(?:warning|error):',compile_log)
sdk_symbols=(OUT/'sdk-elf-symbols.log').read_text()
symbol_lines={name:next(line for line in sdk_symbols.splitlines() if line.endswith(' '+name))
    for name in ('xPortEnterCriticalTimeout','vPortExitCritical','esp_cpu_compare_and_set','__assert_func',
                 '_xtos_set_intlevel','memcpy','port_uxCriticalNesting','port_uxOldInterruptState')}
assert all('.iram0.text' in symbol_lines[name] for name in ('xPortEnterCriticalTimeout','vPortExitCritical','esp_cpu_compare_and_set','__assert_func'))
assert all('.dram0.bss' in symbol_lines[name] for name in ('port_uxCriticalNesting','port_uxOldInterruptState'))
assert '*ABS*' in symbol_lines['_xtos_set_intlevel'] and symbol_lines['_xtos_set_intlevel'].startswith('4000')
assert '*ABS*' in symbol_lines['memcpy'] and symbol_lines['memcpy'].startswith('4000')
for name in ('wrap-valid-timing-counter','wrap-invalid-timing-counter'):
    item=host['negative_controls'][name]
    assert item['detected'] and item['status']==80 and item['marker']=='timing_event_counts_saturate'
    assert item['explicit_static_initial_counter_seed']
    source=HOST/'mutants'/name/'native_output_metrics.c'
    assert sha(source)==item['generated_sha256']
    output=(HOST/'mutants'/name/'test.log').read_text()
    assert output.startswith('SEMANTIC_FAILURE:timing_event_counts_saturate:')
    assert 'AddressSanitizer' not in output and 'runtime error:' not in output
snapshot=OUT/'host-metrics-03'
snapshot.mkdir(exist_ok=False)
for name in ('report.json','diagnostic/count-boundary/test.log',
             'mutants/wrap-valid-timing-counter/test.log','mutants/wrap-invalid-timing-counter/test.log'):
    target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((HOST/name).read_bytes())
for name in host['source_sha256']:
    target=snapshot/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
review={
 'passed':True,'actionable_production_findings':[],
 'scope':'Read-only narrow review of the unwired output metrics helper, host qualification and actual standalone SDK Xtensa objects. No production/test/Git edits, app build or physical device operations.',
 'helper_source_sha256':{str(path):sha(path) for path in helper_files},
 'target_compile_report_sha256':sha(OUT/'compile-report.json'),
 'final_host_report_sha256':sha(HOST/'report.json'),
 'final_host_cases':16,'final_exact_semantic_controls':7,
 'host_all_six_inputs_current':True,'unchanged_helper_allows_existing_target_objects':True,
 'counter_review':[
   'All shared state is accessed under one portMUX. Task writes/snapshot and ISR drops use the correct SDK task/ISR entry/exit APIs; snapshots copy all counters under the same lock.',
   'The uint32 increment and uint64 addition saturate only after range would be lost. Exact arrival at MAX without lost increments need not set saturated. Flag is sticky; max_write_us is a max of valid int64 nonnegative durations and cannot overflow its uint64 field.',
   'Elapsed subtraction is safe because it occurs only when started>=0 and ended>=started; the result cannot exceed INT64_MAX. Invalid timestamps do not turn into unsigned elapsed or erase byte/error observations.',
   'Error/timeout/short-write counters deliberately overlap. Incomplete ESP_OK results and impossible over-reports count as errors; written byte totals preserve the driver-reported quantity. They are not physical PCM/DMA bytes.',
   'Availability is boot-cumulative successful callback observation; ISR receipt also proves observation. No pause/reconfigure reset is introduced. Queue drops do not imply audible underruns.',
   'Quiet objects have no esp_timer_get_time reference. Diagnostic clocks are read before taking the metrics critical section and describe whole synchronous API wall time, including preemption.'
 ],
 'resolved_test_coverage_finding':{
   'finding':'Original count-limit seeded timing_samples/invalid_time_samples at UINT32_MAX but neither asserted these fields nor exercised invalid-time increment at the boundary. A per-field wrap regression could escape that saturation case.',
   'resolution':'Parent added a public invalid-clock write plus assertions that both timing counters stay UINT32_MAX while accumulated valid elapsed/max remain10. Two exact per-field wrap mutants fail the new timing_event_counts_saturate assertion.',
   'status':'resolved in fresh host metrics-03; helper source unchanged',
   'existing_target_report_context':'compile-report captured earlier test fixture/runner hashes for review context. Those noncompiler inputs were intentionally superseded; final host-metrics-03 is the current test evidence. Actual target dependency/source/config/object hashes remain current.'},
 'actual_sdk_object_evidence':{
   'sdk_commit':objects['sdk_commit'],'baseline_row':'original-command-row.json',
   'quiet_and_diagnostic_compiles':True,'warnings_errors':0,
   'new_queue_drop_code_bytes':50,'queue_section':'.iram1.2','literal_section':'.iram1.2.literal',
   'metrics_state_bytes':64,'lock_bytes':8,'state_sections':['.dram1.1','.dram1.0'],
   'new_isr_external_callees':['xPortEnterCriticalTimeout','vPortExitCritical'],
   'actual_IRAM_call_expansion_records':verified_callees,
   'increment_always_inlined':True,'no_allocation_libatomic_wall_clock_API_in_ISR_path':True,
   'sdk_baseline_symbols':symbol_lines,
   'normal_cache_safe_chain':'New IRAM helper calls SDK enter/exit in .iram0.text; compare-and-set is .iram0.text and interrupt-level restore is ROM. SDK nesting/old-state arrays are DRAM. No flash function is needed on a valid-lock normal path.',
   'clock_nuance':'The pinned SDK spinlock can read the raw CPU cycle counter during contention. No timer/wall-clock API is invoked by this ISR helper; no claim of zero CPU cycle-register reads is made.',
   'task_snapshot_copy':'GCC emits memcpy for the64-byte task snapshot while holding the lock; baseline ELF resolves memcpy to ROM0x4000c2c8. It is not an ISR helper call.'},
 'limits':[
   'Object section annotations are not a final integrated firmware memory map. Once wired, verify actual final placement and callback registration/driver write call sites independently.',
   'SDK primitive placement is checked against the frozen existing CYD baseline ELF/config; no new full app is linked.',
   'Normal lock-valid ISR path is audited. SDK corruption/assertion/panic handling is outside a whole-program certification claim, although __assert_func itself is IRAM and masks DROM strings with cache disabled.',
   'pthread tests do not reproduce target SMP/ISR scheduling or prove a TSAN result. No physical IRQ latency, DMA behavior, underrun rate, audible output, hardware resource margin or performance is established.',
   'Host byte-total boundary uses64-bit size_t; actual target objects are ILP32 and no physical billions-of-writes saturation experiment is claimed.',
   'No backend integration is present yet. The driver callback and synchronous-write hooks need their own source integration tests before stage acceptance.'
 ],
 'all_own_processes_terminal':True,'review_script_sha256':sha(Path(__file__).resolve())}
(OUT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print('PASS final review: no production defect; saturation test gap resolved; target IRAM/DRAM evidence; review SHA',sha(OUT/'review.json'))
