"""Pure Python reader rejection/contract checks. Never runs a decoder or native tool."""
import ast
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWNER_PROFILES = {role: dict(task_handle=handle, core=core, declared_priority=priority, priority_provenance=provenance)
    for role, handle, core, priority, provenance in [('controller', 100, 0, 1, 'sdk_main_startup'),
        ('stream', 200, 0, 3, 'wrapped_task_creation'), ('decode', 300, 1, 5, 'wrapped_task_creation'),
        ('output', 400, 1, 6, 'wrapped_task_creation')]}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('mutated evidence was accepted')


def allocator_fixture(legacy_nested=False, extra_calls=()):
    callbacks, allocations = [], []
    expected = list(extra_calls) + [(1, 3, 15360, 0, 1)] + [(1, 4, 1920, 0, 0)] * 8 + [
        (2, 3, 15360, 0, 1), (2, 4, 1920, 0, 1), (4, 5, 23040, 1, 1)]
    for epoch, scope, size, old, null in expected:
        before = len(callbacks)
        caps = 2052 if scope == 1 else 2050 if scope in (2, 4) else 0
        if null:
            # Legacy reproduces the rejected pre-review assumption; it is never
            # a positive fixture. Pinned SDK calls report exactly once.
            callback_caps = caps if caps else 4 if legacy_nested else 6144
            for _ in range(2 if legacy_nested and scope == 3 else 1):
                callbacks.append(dict(ordinal=len(callbacks) + 1, epoch=epoch, scope=scope, bytes=size, caps=callback_caps, decoder=1, forwarded=1))
        allocations.append(dict(ordinal=len(allocations) + 1, epoch=epoch, scope=scope, bytes=size, caps=caps,
                                old_present=old, returned_null=null, callbacks_before=before, callbacks_after=len(callbacks), held_blocks=8, held_bytes=32768,
                                real_call=1, fabricated_return=0))
    return callbacks, allocations, dict(callbacks=len(callbacks), allocation_failures=len(callbacks))


def duplicate_first_callback(callbacks, allocations, final):
    callbacks.insert(1, dict(callbacks[0]))
    for ordinal, callback in enumerate(callbacks, 1):callback['ordinal'] = ordinal
    for row in allocations:
        if row['callbacks_before'] >= 1:row['callbacks_before'] += 1
        if row['callbacks_after'] >= 1:row['callbacks_after'] += 1
    final['callbacks'] += 1;final['allocation_failures'] += 1


def gate_fixture():
    rows = []
    def add(tag, **row):rows.append((tag, row))
    for index, epoch in enumerate((6, 7, 9)):
        start = 1000 + index * 1000;generation = 20 + index
        add('CYD_RC_GATE_HELD', generation=generation, time_us=start, before_real_renderer=1, ring_bytes=8192, core=1, priority=6)
        for wait in range(2):
            add('CYD_RC_RING_TIMEOUT', ordinal=2 * index + wait + 1, generation=generation, gate_held=1, bytes=3092, wait_ticks=50,
                elapsed_ticks=50, elapsed_us=50000, free_before=0, free_after=0, max_item=4088, real_result=0, core=1, priority=5)
        add('CYD_RC_BLOCKED', epoch=epoch, id=('RING_RELEASE', 'RING_STOP', 'RING_MAINTENANCE')[index], generation=generation,
            timeout_base=2 * index, timeouts=2 * index + 2, ring_bytes=8192, gate_held=1, before_real_renderer=1, live_decoders=5, observed_us=start + 100)
        if epoch == 7:
            add('CYD_RC_STOP_REQUEST', epoch=7, generation=generation, time_us=start + 110)
            add('CYD_RC_STOP_RETURN', epoch=7, generation=generation + 1, time_us=start + 120, real_returned=1)
        if epoch == 9:
            add('CYD_RC_GATE_PAUSE', generation=generation, time_us=start + 120, real_pause_returned=1)
            add('CYD_F1_WRITE_RETURN', source_generation=generation, result=0x103, pause_requested=1, cancelling=1, return_us=start + 150)
        add('CYD_RC_GATE_RELEASE', generation=generation, time_us=start + 130, real_renderer_pending=1)
        if epoch != 6:
            add('CYD_RC_CANCEL_QUIET', epoch=epoch, kind='STOP' if epoch == 7 else 'MAINTENANCE', old_generation=generation,
                generation=generation + 1, discard_before=index, discard_after=index + 1, quiet_ms=25, no_eof=1, all_owners_quiet=1,
                ring_sends=4, ring_receives=4, ring_returns=4)
    return rows


def maintenance_fixture(gates):
    rows = copy.deepcopy(gates)
    def add(tag, **row):rows.append((tag, row))
    for role, owner in OWNER_PROFILES.items():
        add('CYD_F1_CONTROL_OWNER', role=role, **owner, effective_priority_limit=25, live_base_query=0, creation_profile_checked=1)
    for acquire, start, generation, token in ((1, 3110, 22, 1), (2, 40000, 30, 2)):
        add('CYD_F1_CONTROL_ACQUIRE_START', acquire=acquire, timeout_ms=10000, time_us=start, source_generation=generation)
        add('CYD_F1_CONTROL_ACQUIRE_RETURN', acquire=acquire, time_us=start + 100, source_generation=generation, result=0, real_returned=1, token_epoch=token)
        add('CYD_F1_CONTROL_ACQUIRE_HELD', acquire=acquire, time_us=start + 101, token_epoch=token, live_clients=0, live_decoders=0,
            input_ready=0, input_reading=0, input_writing=0, driver_live=0, input_available=1, input_leased=1, pauses_before=acquire - 1, pauses_after=acquire)
    for pause, acquire, start, requested, active in ((1, 1, 3111, 1, 1), (2, 1, 30000, 0, 0), (3, 2, 40001, 1, 1)):
        role = 'controller' if requested else 'stream';owner = OWNER_PROFILES[role]
        arguments = dict(pause=pause, acquire=acquire, acquire_active=active, requested=requested, fixture='default8',
                         **owner, owner_role=role, priority=owner['declared_priority'])
        add('CYD_F1_CONTROL_PAUSE_START', **arguments, time_us=start)
        add('CYD_F1_CONTROL_PAUSE_RETURN', **arguments, time_us=start + 1, real_returned=1)
    for index, quiet in enumerate(row for tag, row in rows if tag == 'CYD_RC_CANCEL_QUIET'):
        released = [row for tag, row in rows if tag == 'CYD_RC_GATE_RELEASE'][index + 1]
        discard = released['time_us'] + 10
        quiet['quiet_start_us'] = discard + (100 if index else 10);quiet['time_us'] = quiet['quiet_start_us'] + 25000
        add('CYD_F1_CONTROL_DISCARD', sequence=quiet['discard_after'], real_returned=1, time_us=discard)
    next(row for tag, row in rows if tag == 'CYD_F1_WRITE_RETURN').update(acquire_return=1, pause_acquire=1, pause_start=1)
    return rows


def health_fixture(cases):
    """Independent finite public-data fixture; never represents native execution."""
    callbacks, allocations, _ = allocator_fixture()
    counter_table = {1:(0, 0, 0, 1), 2:(0, 1, 1, 3), 3:(1, 1, 3, 3), 4:(1, 2, 3, 4),
                     5:(2, 2, 4, 4), 6:(2, 2, 4, 4), 8:(2, 2, 4, 4), 10:(2, 2, 4, 4)}
    plan_by_epoch = {p['epoch']:p for p in cases};rows = []
    decoder = dict(decoder_generation=0, decoder_codec=0, decoder_stage=0, decoder_result=0,
                   decoder_completion=0, decoder_input_bytes=0, decoder_allocation_sequence=0)
    for epoch in range(1, 11):
        plan = plan_by_epoch.get(epoch)
        rows.append(('CYD_RC_BEGIN', dict(epoch=epoch, expected_detail={2:15360, 4:23040}.get(epoch, 0))))
        rows.extend(('CYD_RC_CALLBACK', copy.deepcopy(x)) for x in callbacks if x['epoch'] == epoch)
        rows.extend(('CYD_RC_ALLOC', copy.deepcopy(x)) for x in allocations if x['epoch'] == epoch)
        if plan is None:continue
        before_decoder, after_decoder, before_alloc, after_alloc = counter_table[epoch]
        error = int(epoch in (2, 4));detail = {2:15360, 4:23040}.get(epoch, 0)
        if error:
            decoder = dict(decoder_generation=epoch, decoder_codec=4, decoder_stage=2, decoder_result=detail,
                           decoder_completion=9, decoder_input_bytes=512, decoder_allocation_sequence=3 if epoch == 2 else 4)
        last_callback = callbacks[after_alloc - 1]
        common = dict(epoch=epoch, id=plan['id'], leg=plan['leg'], generation=epoch)
        health = dict(common, expected_detail=detail, callbacks_seen=after_alloc,
            before_decoder_failures=before_decoder, decoder_failures=after_decoder,
            before_allocation_failures=before_alloc, allocation_failures=after_alloc,
            before_stream_failures=0, before_output_failures=0, allocation_size=last_callback['bytes'], allocation_caps=last_callback['caps'],
            stream_failures=0, stream_generation=0, stream_completion=0, stream_result=0,
            output_failures=0, output_generation=0, output_stage=0, output_write_errors=0, output_configure_errors=0, output_flush_errors=0, output_result=0,
            **decoder)
        rows.append(('CYD_RC_HEALTH', health))
        rows.append(('CYD_RC_TERMINAL', dict(common, allocation_error=error, decoder_delta=error, stream_delta=0, output_delta=0, allocation_delta=after_alloc-before_alloc)))
    return rows, dict(decoder_failures=2, stream_failures=0, output_failures=0, allocation_failures=4)


def main():
    reader = load('new_runtime_reader_checks', ROOT / 'tests/read-cyd-ogg-runtime-controls.py')
    for name in ('tests/read-cyd-ogg-runtime-controls.py', 'tests/run-cyd-ogg-runtime-controls-qemu.py'):
        ast.parse((ROOT / name).read_text(), filename=name)
    callback, allocation, final = allocator_fixture()
    reader.validate_allocator_records(callback, allocation, final)
    rejected_cases = 0
    rejected(lambda: reader.validate_allocator_records(*allocator_fixture(legacy_nested=True)));rejected_cases += 1
    helper_fixture = allocator_fixture(extra_calls=((1, 1, 4096, 0, 1), (1, 2, 4096, 0, 1)))
    reader.validate_allocator_records(*helper_fixture)
    pressure_source = (Path(__file__).parent / 'project/main/runtime_pressure.inc').read_text()
    callback_source = pressure_source.split('static void IRAM_ATTR runtime_failed_alloc', 1)[1].split('extern "C" esp_err_t __wrap_heap_caps_register', 1)[0]
    classifier_source = pressure_source.split('FORCE_INLINE_ATTR bool runtime_in_decoder_stack()', 1)[1].split('static void IRAM_ATTR runtime_failed_alloc', 1)[0]
    assert 'xTaskGetCurrentTaskHandle' not in callback_source + classifier_source
    assert 'esp_cpu_get_sp()' in classifier_source and 'xPortInIsrContext()' in classifier_source and 'esp_cpu_get_core_id()==1' in classifier_source
    assert 'static FORCE_INLINE_ATTR' not in pressure_source
    owner = dict(stack_low=0x3ffb0000, stack_high=0x3ffb4000, stack_bytes=16384, stream_low=0x3ffb5000, stream_high=0x3ffb6800,
                 output_low=0x3ffb7000, output_high=0x3ffb8000, public_bounds=1, disjoint=1, callback_task_lookup=0, stack_dereferenced=0, core=1, priority=5)
    reader.validate_owner_record(owner)
    for key, value in [('stack_high', owner['stack_high'] - 1), ('stream_low', owner['stack_low']), ('callback_task_lookup', 1), ('stack_dereferenced', 1), ('core', 0)]:
        changed = dict(owner);changed[key] = value
        rejected(lambda: reader.validate_owner_record(changed));rejected_cases += 1
    overlap=dict(owner,stream_low=owner["stack_low"],stream_high=owner["stack_low"]+6144)
    rejected(lambda: reader.validate_owner_record(overlap));rejected_cases += 1
    mutations = [
        lambda c, a, f: c.pop(),
        lambda c, a, f: a[0].update(fabricated_return=1),
        lambda c, a, f: a[0].update(real_call=0),
        lambda c, a, f: a[0].update(callbacks_after=0),
        lambda c, a, f: a[0].update(returned_null=0),
        lambda c, a, f: a[2].update(bytes=1918),
        lambda c, a, f: a[-1].update(old_present=0),
        lambda c, a, f: a[-1].update(held_blocks=0),
        lambda c, a, f: c[0].update(scope=1),
        lambda c, a, f: c[0].update(epoch=3),
        lambda c, a, f: c[0].update(forwarded=0),
        lambda c, a, f: c[0].update(bytes=15359),
        lambda c, a, f: c[0].update(caps=4),
        lambda c, a, f: c[0].update(caps=4096),
        lambda c, a, f: c[2].update(bytes=1924),
        lambda c, a, f: c[2].update(caps=6144),
        lambda c, a, f: c[-1].update(bytes=11520),
        lambda c, a, f: c[-1].update(caps=4),
        duplicate_first_callback,
        lambda c, a, f: a[0].update(callbacks_before=1, callbacks_after=2),
        lambda c, a, f: a[9].update(callbacks_before=0),
        lambda c, a, f: f.update(allocation_failures=0),
    ]
    for mutate in mutations:
        c, a, f = copy.deepcopy((callback, allocation, final));mutate(c, a, f)
        rejected(lambda: reader.validate_allocator_records(c, a, f));rejected_cases += 1
    for index, key, value in [(0, 'caps', 2050), (1, 'caps', 2052), (0, 'bytes', 4092), (1, 'bytes', 4095)]:
        c, a, f = copy.deepcopy(helper_fixture);c[index][key] = value
        rejected(lambda: reader.validate_allocator_records(c, a, f));rejected_cases += 1
    gates = gate_fixture();reader.validate_gate_records(gates, [])
    gate_mutations = [
        ('CYD_RC_RING_TIMEOUT', 'wait_ticks', 0),
        ('CYD_RC_RING_TIMEOUT', 'elapsed_ticks', 2),
        ('CYD_RC_RING_TIMEOUT', 'bytes', 9000),
        ('CYD_RC_RING_TIMEOUT', 'gate_held', 0),
        ('CYD_RC_RING_TIMEOUT', 'real_result', 1),
        ('CYD_RC_RING_TIMEOUT', 'free_before', 3092),
        ('CYD_RC_RING_TIMEOUT', 'free_after', 3092),
        ('CYD_RC_RING_TIMEOUT', 'free_before', -1),
        ('CYD_RC_RING_TIMEOUT', 'free_after', 4090),
        ('CYD_RC_GATE_PAUSE', 'real_pause_returned', 0),
        ('CYD_RC_STOP_RETURN', 'generation', 90),
        ('CYD_RC_CANCEL_QUIET', 'discard_after', 90),
        ('CYD_F1_WRITE_RETURN', 'result', 0),
    ]
    for tag, key, value in gate_mutations:
        changed = copy.deepcopy(gates);next(row for found, row in changed if found == tag)[key] = value
        rejected(lambda: reader.validate_gate_records(changed, []));rejected_cases += 1
    old_snapshot = copy.deepcopy(gates);wait = next(row for tag, row in old_snapshot if tag == 'CYD_RC_RING_TIMEOUT')
    wait['free_entry'] = wait.pop('free_after')
    rejected(lambda: reader.validate_gate_records(old_snapshot, []));rejected_cases += 1
    maintenance = maintenance_fixture(gates)
    reader.validate_maintenance_records(maintenance, reader.validate_gate_records(maintenance, []))
    for tag, key, value in [('CYD_F1_CONTROL_ACQUIRE_HELD', 'token_epoch', 0), ('CYD_F1_CONTROL_ACQUIRE_HELD', 'driver_live', 1),
                            ('CYD_F1_CONTROL_PAUSE_RETURN', 'real_returned', 0), ('CYD_F1_WRITE_RETURN', 'pause_acquire', 2),
                            ('CYD_RC_CANCEL_QUIET', 'time_us', 0)]:
        changed = copy.deepcopy(maintenance);next(row for found, row in changed if found == tag)[key] = value
        rejected(lambda: reader.validate_maintenance_records(changed, reader.validate_gate_records(changed, [])));rejected_cases += 1
    rejected(lambda: reader.parse_word_allocation_log('CYD_RC_WORD_COMPLETE attempts=1 successes=1 frees=0 refusals=0 live_planes=1 peak_planes=1 live_bytes=1920 peak_bytes=1920 private_heap=0 diagnostic_delays=1 owner_only_table=1'))
    rejected_cases += 1
    assert rejected_cases == 53, 'all original allocator/ring/maintenance controls retained'
    original_rejections = rejected_cases
    owner_positives, owner_rejections = [], []
    def pair(rows, pause, role=None, start_priority=None, return_priority=None, **changes):
        for tag, row in rows:
            if tag not in ('CYD_F1_CONTROL_PAUSE_START', 'CYD_F1_CONTROL_PAUSE_RETURN') or row['pause'] != pause:continue
            if role is not None:
                owner = OWNER_PROFILES[role];row.update(owner, owner_role=role, priority=owner['declared_priority'])
            if tag.endswith('_START') and start_priority is not None:row['priority'] = start_priority
            if tag.endswith('_RETURN') and return_priority is not None:row['priority'] = return_priority
            row.update(changes)
    for name, mutate in [
        ('controller boost1_to6', lambda rows: pair(rows, 1, start_priority=1, return_priority=6)),
        ('controller deboost6_to1', lambda rows: pair(rows, 1, start_priority=6, return_priority=1)),
        ('controller stable_boost6', lambda rows: pair(rows, 1, start_priority=6, return_priority=6)),
        *[(role + '_real_resume_owner', lambda rows, role=role: pair(rows, 2, role=role)) for role in ('stream', 'decode', 'output')],
    ]:
        changed = copy.deepcopy(maintenance);mutate(changed)
        reader.validate_maintenance_records(changed, reader.validate_gate_records(changed, []));owner_positives.append(name)
    def first(rows, tag):return next(row for found, row in rows if found == tag)
    def remove_first_owner(rows):rows.pop(next(i for i, (tag, _) in enumerate(rows) if tag == 'CYD_F1_CONTROL_OWNER'))
    def late_owners(rows):
        owners = [row for row in rows if row[0] == 'CYD_F1_CONTROL_OWNER']
        rows[:] = [row for row in rows if row[0] != 'CYD_F1_CONTROL_OWNER'] + owners
    owner_mutations = [
        ('missing_owner', remove_first_owner),
        ('duplicate_handle', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(task_handle=200)),
        ('null_handle', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(task_handle=0)),
        ('non_xtensa_handle', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(task_handle=2**32)),
        ('wrong_registered_role', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(role='stream')),
        ('wrong_registered_priority', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(declared_priority=2)),
        ('wrong_registered_core', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(core=1)),
        ('wrong_registered_provenance', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(priority_provenance='live_query')),
        ('live_base_claim', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(live_base_query=1)),
        ('unchecked_creation', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(creation_profile_checked=0)),
        ('changed_scheduler_limit', lambda rows: first(rows, 'CYD_F1_CONTROL_OWNER').update(effective_priority_limit=24)),
        ('identities_published_late', late_owners),
        ('return_handle_changed', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').update(task_handle=200)),
        ('return_role_changed', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').update(owner_role='stream')),
        ('return_core_changed', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').update(core=1)),
        ('return_declared_changed', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').update(declared_priority=3)),
        ('return_provenance_changed', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').update(priority_provenance='wrapped_task_creation')),
        ('return_identity_missing', lambda rows: first(rows, 'CYD_F1_CONTROL_PAUSE_RETURN').pop('task_handle')),
        ('unknown_handle', lambda rows: pair(rows, 1, task_handle=999)),
        ('wrong_role', lambda rows: pair(rows, 1, owner_role='output')),
        ('wrong_declared', lambda rows: pair(rows, 1, declared_priority=6)),
        ('wrong_core', lambda rows: pair(rows, 1, core=1)),
        ('start_priority_below_declared', lambda rows: pair(rows, 1, start_priority=0)),
        ('return_priority_below_declared', lambda rows: pair(rows, 1, return_priority=0)),
        ('start_priority_at_limit', lambda rows: pair(rows, 1, start_priority=25)),
        ('return_priority_at_limit', lambda rows: pair(rows, 1, return_priority=25)),
        ('pipeline_cannot_request_maintenance', lambda rows: pair(rows, 1, role='output')),
        ('controller_resume_not_positive', lambda rows: pair(rows, 2, role='controller')),
        ('controller_abort_not_positive', lambda rows: pair(rows, 2, role='controller', acquire_active=1)),
        ('resume_before_held', lambda rows: pair(rows, 2, time_us=3110)),
        ('output_below_creation_priority', lambda rows: pair(rows, 2, role='output', return_priority=5)),
        ('resume_after_final_maintenance', lambda rows: pair(rows, 2, acquire=2)),
    ]
    for name, mutate in owner_mutations:
        changed = copy.deepcopy(maintenance);mutate(changed)
        rejected(lambda: reader.validate_maintenance_records(changed, reader.validate_gate_records(changed, [])))
        owner_rejections.append(name);rejected_cases += 1
    assert reader.fields('CYD_F1_REFERENCE_PCM index=0 offset=0 bytes=2 hex=0000')[1]['hex'] == '0000'
    assets = load('new_runtime_exact_assets', ROOT / 'tests/prepare-cyd-family1-task-assets.py')
    original, blob, header, size_header, provenance = assets.prepare()
    plan = reader.runtime_contract(original)
    assert len(original['cases']) == 48 and len(plan['runtime_sessions']) == 10 and len(plan['cases']) == 8
    assert plan['cases'][1]['links'] == original['cases'][-1]['links'][:2]
    assert plan['cases'][2]['links'] == original['cases'][-1]['links']
    assert plan['cases'][3]['links'] == []
    assert plan['cases'][4]['links'] == next(row['links'] for row in original['cases'] if row['id'] == 'T0' and row['reference'] == 12)
    assert header and size_header and original['immutable_storage']['unique_blob_bytes'] == len(blob)
    assert plan['task_bindings'] == original['task_bindings'] and not plan['normalizer_enabled_qualified']
    assert rejected_cases == 85 and len(owner_positives) == 6, 'all original and owner controls retained'
    health_rows, health_final = health_fixture(plan['cases'])
    reader.validate_health_records(health_rows, plan['cases'], health_final)
    health_positives = ['two exact predeclared details with sticky healthy-reopen payload']
    # A later recovered ordinary NULL updates allocation metadata, never the
    # previous decoder failure's stored callback sequence or cause.
    recovered = copy.deepcopy(health_rows);recovered_final = dict(health_final, allocation_failures=5)
    index = next(i for i, (tag, p) in enumerate(recovered) if tag == 'CYD_RC_BEGIN' and p['epoch'] == 5) + 1
    recovered.insert(index, ('CYD_RC_CALLBACK', dict(ordinal=5, epoch=5, scope=6, bytes=64, caps=6144, decoder=1, forwarded=1)))
    recovered.insert(index + 1, ('CYD_RC_ALLOC', dict(ordinal=13, epoch=5, scope=6, bytes=64, caps=0, old_present=0,
        returned_null=1, callbacks_before=4, callbacks_after=5, held_blocks=0, held_bytes=0, real_call=1, fabricated_return=0)))
    for tag, row in recovered:
        if tag == 'CYD_RC_HEALTH' and row['epoch'] >= 5:
            row.update(allocation_failures=5, callbacks_seen=5, allocation_size=64, allocation_caps=6144)
            if row['epoch'] > 5:row['before_allocation_failures'] += 1
        if tag == 'CYD_RC_TERMINAL' and row['epoch'] == 5:row['allocation_delta'] += 1
    reader.validate_health_records(recovered, plan['cases'], recovered_final)
    health_positives.append('later recovered NULL preserves the earlier decoder cause/sequence')
    def health_row(rows, epoch=2):return next(p for tag, p in rows if tag == 'CYD_RC_HEALTH' and p['epoch'] == epoch)
    def terminal_row(rows, epoch=2):return next(p for tag, p in rows if tag == 'CYD_RC_TERMINAL' and p['epoch'] == epoch)
    def remove_health(rows):rows.pop(next(i for i, (tag, _) in enumerate(rows) if tag == 'CYD_RC_HEALTH'))
    def duplicate_health(rows):rows.insert(0, ('CYD_RC_HEALTH', copy.deepcopy(health_row(rows))))
    def late_health(rows):
        index = next(i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_HEALTH' and p['epoch'] == 2)
        row = rows.pop(index);rows.append(row)
    health_mutations = [
        *[(f'wrong_detail_{epoch}_{value}', lambda rows, epoch=epoch, value=value: health_row(rows, epoch).update(decoder_result=value))
          for epoch, value in [(2, 2), (2, -2), (4, 2), (4, -2), (2, 23040), (4, 15360)]],
        ('wrong_generation', lambda rows: health_row(rows).update(decoder_generation=1)),
        ('wrong_codec', lambda rows: health_row(rows).update(decoder_codec=0)),
        ('wrong_stage', lambda rows: health_row(rows).update(decoder_stage=1)),
        ('wrong_completion', lambda rows: health_row(rows).update(decoder_completion=8)),
        ('missing_input', lambda rows: health_row(rows).update(decoder_input_bytes=0)),
        ('zero_sequence', lambda rows: health_row(rows).update(decoder_allocation_sequence=0)),
        ('prior_byte_sequence', lambda rows: health_row(rows).update(decoder_allocation_sequence=2)),
        ('future_sequence', lambda rows: health_row(rows).update(decoder_allocation_sequence=4)),
        ('before_decoder_count', lambda rows: health_row(rows).update(before_decoder_failures=1)),
        ('after_decoder_count', lambda rows: health_row(rows).update(decoder_failures=0)),
        ('before_allocation_count', lambda rows: health_row(rows).update(before_allocation_failures=0)),
        ('after_allocation_count', lambda rows: health_row(rows).update(allocation_failures=2)),
        ('wrong_callback_count', lambda rows: health_row(rows).update(callbacks_seen=2)),
        ('wrong_terminal_delta', lambda rows: terminal_row(rows).update(allocation_delta=0)),
        ('wrong_last_size', lambda rows: health_row(rows).update(allocation_size=15360)),
        ('wrong_last_caps', lambda rows: health_row(rows).update(allocation_caps=6144)),
        ('hidden_stream_payload', lambda rows: health_row(rows).update(stream_generation=1)),
        ('hidden_output_counter', lambda rows: health_row(rows).update(output_write_errors=1)),
        ('lost_sticky_payload', lambda rows: health_row(rows, 3).update(decoder_result=0)),
        ('changed_healthy_sequence', lambda rows: health_row(rows, 3).update(decoder_allocation_sequence=0)),
        ('wrong_predeclared_detail', lambda rows: health_row(rows).update(expected_detail=2)),
        ('missing_health', remove_health), ('duplicate_health', duplicate_health), ('health_after_terminal', late_health),
        ('missing_field', lambda rows: health_row(rows).pop('decoder_result')),
        ('unknown_field', lambda rows: health_row(rows).update(unknown_fault_allowed=1)),
        ('missing_target_call', lambda rows: rows.pop(next(i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_ALLOC' and p['epoch'] == 2 and p['scope'] == 4))),
        ('wrong_target_callback', lambda rows: next(p for tag, p in rows if tag == 'CYD_RC_CALLBACK' and p['ordinal'] == 3).update(scope=5)),
    ]
    health_rejections = []
    for name, mutate in health_mutations:
        changed = copy.deepcopy(health_rows);mutate(changed)
        rejected(lambda: reader.validate_health_records(changed, plan['cases'], health_final));health_rejections.append(name);rejected_cases += 1
    rejected(lambda: reader.validate_health_records(health_rows, [], health_final));health_rejections.append('empty_case_census');rejected_cases += 1
    rejected(lambda: reader.validate_health_records(health_rows, plan['cases'], dict(health_final, decoder_failures=1)))
    health_rejections.append('wrong_final_census');rejected_cases += 1
    # Rejection/acceptance of synthetic records tests the reader only.
    print(json.dumps(dict(passed=True, synthetic_reader_rejections=rejected_cases, complete_original_asset_bytes=len(blob),
                          original_rejections=original_rejections, owner_positive_controls=owner_positives,
                          owner_rejection_controls=owner_rejections,
                          health_positive_controls=health_positives, health_rejection_controls=health_rejections,
                          original_positive_cases=48, new_sessions=10, typed_terminal_outputs=8,
                          target_executed=False, compiler_executed=False, native_qualified=False)))


if __name__ == '__main__':
    main()
