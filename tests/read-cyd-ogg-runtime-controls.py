"""Data-only typed Ogg runtime-control reader. Synthetic tests never qualify native execution."""
import hashlib
import re


def need(value, reason):
    if not value:
        raise ValueError(reason)


def runtime_contract(original):
    """Keep the complete immutable asset/reference input; declare only new output legs."""
    def one(reference):
        return next(row for row in original['cases'] if row['id'] == 'T0' and row['reference'] == reference)
    small, large = one(2), one(12)
    reverse = next(row for row in original['cases'] if row['name'] == 'REVERSE_120_CHAIN')
    begins = [
        ('BYTE_FALLBACK', 'CONTROL', small, 1, 1, 0),
        ('DUAL_OOM', 'CONTROL', reverse, 2, 2, 2),
        ('DUAL_OOM', 'REOPEN', reverse, 5, 0, 0),
        ('SCRATCH_OOM', 'CONTROL', large, 0, 3, 0),
        ('SCRATCH_OOM', 'REOPEN', large, 1, 0, 0),
        ('RING_RELEASE', 'CONTROL', small, 1, 0, 0),
        ('RING_STOP', 'CONTROL', small, 1, 0, 0),
        ('RING_STOP', 'REOPEN', small, 1, 0, 0),
        ('RING_MAINTENANCE', 'CONTROL', small, 1, 0, 0),
        ('RING_MAINTENANCE', 'RESUME', small, 1, 0, 0),
    ]
    sessions, cases = [], []
    for epoch, (control, leg, source, count, mode, target) in enumerate(begins, 1):
        plan = dict(source, id=control, leg=leg, epoch=epoch, mode=mode, target_link=target,
                    expected_links=count, complete_fixture_links=source['links'], links=source['links'][:count],
                    allocation_error=int(mode in (2, 3)), cancelled=int(epoch in (7, 9)))
        plan['expected_detail'] = 15360 if mode == 2 else 23040 if mode == 3 else 0
        sessions.append(plan)
        if not plan['cancelled']:
            cases.append(plan)
    return dict(original, cases=cases, runtime_sessions=sessions, complete_output_cases=8,
                application_http_sessions=10, application_decoder_handles=57,
                original_positive_cases=48, ordinary_deadline_ms=30000, normalizer_enabled=False,
                actual_heap_pressure=True, scripted_allocator_returns=False, runtime_controls=6,
                normalizer_enabled_qualified=False, original_production_watchdog_equivalence=False)


def fields(line):
    tag, *tokens = line.split()
    pairs = [token.split('=', 1) for token in tokens]
    need(pairs and all(len(pair) == 2 for pair in pairs) and len({key for key, _ in pairs}) == len(pairs),
         'complete unique data fields')
    row = {}
    for key, value in pairs:
        need(re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', key) and re.fullmatch('[a-zA-Z0-9_.:+/-]+', value), 'plain data tokens')
        row[key] = int(value) if key not in ('sha256','render_sha256','hex') and re.fullmatch('-?[0-9]+', value) else value
    return tag, row


def validate_allocator_records(callbacks, allocations, complete):
    need([row['ordinal'] for row in callbacks] == list(range(1, len(callbacks) + 1)), 'every callback ordinal retained once')
    need([row['ordinal'] for row in allocations] == list(range(1, len(allocations) + 1)), 'every allocator observation retained once')
    need(complete['callbacks'] == complete['allocation_failures'] == len(callbacks), 'actual health callback count equals forwarded diagnostic census')
    need(all(sum(row['epoch'] == epoch for row in callbacks) <= 12 and sum(row['epoch'] == epoch for row in allocations) <= 12 for epoch in range(1, 11)),
         'small per-leg trace buffers are serialized without overflow or silently dropped records')
    # Pinned ESP-IDF6.0.2 no-SPIRAM path: libc realloc ->
    # heap_caps_realloc_default -> heap_caps_realloc reports one failure with
    # the original size and DEFAULT|INTERNAL (4096|2048). Public malloc likewise
    # reports once with its original size/caps; base routines do not report.
    covered = set();callback_cursor = 0
    for row in allocations:
        need(row['real_call'] == 1 and row['fabricated_return'] == 0 and 1 <= row['epoch'] <= 10 and
             row['scope'] in (1, 2, 3, 4, 5, 6) and row['bytes'] > 0 and row['old_present'] in (0, 1) and row['returned_null'] in (0, 1) and
             row['callbacks_before'] == callback_cursor and row['callbacks_before'] <= row['callbacks_after'] <= len(callbacks),
             'real positive-size synchronous calls with complete ordered callback intervals')
        realloc_call = row['scope'] in (3, 5) or row['scope'] == 6 and row['caps'] == 0
        if realloc_call:
            need(row['caps'] == 0, 'realloc record keeps the libc wrapper capability sentinel')
            callback_caps = 6144
        else:
            callback_caps = 2052 if row['scope'] == 1 else 2050
            need(row['old_present'] == 0 and row['caps'] == callback_caps, 'public heap_caps_malloc family has exact requested capability mask')
        if row['returned_null']:
            need(row['callbacks_after'] == row['callbacks_before'] + 1, 'pinned public allocator NULL emits exactly one callback; nesting/duplicates are NONPASS')
        else:
            need(row['callbacks_after'] == row['callbacks_before'], 'successful real candidate has no unaccounted callback')
        for index in range(row['callbacks_before'], row['callbacks_after']):
            event = callbacks[index]
            need(index not in covered and event['epoch'] == row['epoch'] and event['scope'] == row['scope'] and
                 event['decoder'] == event['forwarded'] == 1 and event['bytes'] == row['bytes'] and event['caps'] == callback_caps,
                 'every callback matches exactly one same-owner public call, requested size and pinned capability mask')
            covered.add(index)
        callback_cursor = row['callbacks_after']
    need(covered == set(range(len(callbacks))), 'no unrelated, missing, duplicated, bootstrap or unattributed allocation failures')
    targets = [row for row in allocations if row['scope'] in (3, 4, 5)]
    expected = [(1, 3, 15360, 0, 1)] + [(1, 4, 1920, 0, 0)] * 8 + [
        (2, 3, 15360, 0, 1), (2, 4, 1920, 0, 1), (4, 5, 23040, 1, 1)]
    need([(row['epoch'], row['scope'], row['bytes'], row['old_present'], row['returned_null']) for row in targets] == expected,
         'genuine15360 NULL→8x1920 success; dual NULL; genuine23040 old-scratch growth NULL')
    need(all(row['caps'] == 2050 for row in targets if row['scope'] == 4), 'word candidates use exact public INTERNAL|32BIT capability mask')
    need(all(0 < row['held_blocks'] <= 128 and row['held_bytes'] > 0 for row in targets), 'actual retained public pressure exists at every targeted real call')
    need(all(row['bytes'] > 0 and row['caps'] > 0 for row in callbacks), 'actual public failed-allocation callback request metadata')
    # Any natural failure is retained, correlated and separately visible. Its
    # successful full output is required by the enclosing typed terminal.
    ordinary = [row for row in allocations if row['scope'] == 6]
    need(all(row['returned_null'] == 1 and row['bytes'] > 0 for row in ordinary), 'ordinary failures are actual real NULLs')
    return dict(callbacks=callbacks, real_allocations=allocations, natural_nulls=ordinary,
                pressure_helper_nulls=[row for row in allocations if row['scope'] in (1, 2)], fabricated_return=False)


def validate_owner_record(owner):
    spans = [(owner['stack_low'], owner['stack_high'], 16384), (owner['stream_low'], owner['stream_high'], 6144),
             (owner['output_low'], owner['output_high'], 4096)]
    need(all(0 < low < high <= 2**32 - 1 and high - low == size for low, high, size in spans) and
         all(a[1] <= b[0] or b[1] <= a[0] for i, a in enumerate(spans) for b in spans[i + 1:]) and
         all(owner[key] == value for key, value in dict(stack_bytes=16384, public_bounds=1, disjoint=1, callback_task_lookup=0,
             stack_dereferenced=0, core=1, priority=5).items()), 'actual disjoint public original stack bounds; callback reads only hardware SP/core')
    return spans


def validate_gate_records(rows, sessions):
    def select(tag): return [row for found, row in rows if found == tag]
    held, released, blocked = select('CYD_RC_GATE_HELD'), select('CYD_RC_GATE_RELEASE'), select('CYD_RC_BLOCKED')
    need(len(held) == len(released) == len(blocked) == 3, 'three actual held output writes, releases and blocked-ring controls')
    need([row['epoch'] for row in blocked] == [6, 7, 9], 'release, Stop and maintenance block independently')
    for a, b, c in zip(held, released, blocked):
        need(a['generation'] == b['generation'] == c['generation'] > 0 and a['time_us'] <= c['observed_us'] <= b['time_us'] and
             a['before_real_renderer'] == b['real_renderer_pending'] == c['before_real_renderer'] == c['gate_held'] == 1 and
             a['ring_bytes'] == c['ring_bytes'] == 8192 and a['core'] == 1 and a['priority'] == 6,
             'gate holds one borrowed real write outside renderer internals until after observed blocked queue')
        waits = [row for found, row in rows if found == 'CYD_RC_RING_TIMEOUT' and row['generation'] == c['generation'] and
                 c['timeout_base'] < row['ordinal'] <= c['timeouts']]
        need(len(waits) >= 2 and len(waits) == c['timeouts'] - c['timeout_base'], 'at least two retained real wait failures before each control')
        need(all('free_before' in row and 'free_after' in row and 'free_entry' not in row for row in waits), 'distinct genuine pre-call and post-call free-entry-size snapshots')
        need(all(row['real_result'] == 0 and row['gate_held'] == 1 and row['wait_ticks'] == 50 and row['elapsed_ticks'] + 1 >= 50 and
                 0 <= row['free_before'] < row['bytes'] <= row['max_item'] and 0 <= row['free_after'] < row['bytes'] and
                 row['core'] == 1 and row['priority'] == 5 for row in waits), 'real valid-sized50ms ring timeouts, not fake returns or oversized requests')
    stops, stop_returns, pauses = select('CYD_RC_STOP_REQUEST'), select('CYD_RC_STOP_RETURN'), select('CYD_RC_GATE_PAUSE')
    need(len(stops) == len(stop_returns) == len(pauses) == 1, 'one actual Stop interval and one forwarded pause release')
    need(stops[0]['epoch'] == stop_returns[0]['epoch'] == 7 and stop_returns[0]['real_returned'] == 1 and
         stop_returns[0]['generation'] == stops[0]['generation'] + 1 and
         held[1]['time_us'] <= blocked[1]['observed_us'] <= stops[0]['time_us'] <= stop_returns[0]['time_us'] <= released[1]['time_us'],
         'Stop is issued while genuinely blocked and gate releases after real Stop returns')
    need(pauses[0]['real_pause_returned'] == 1 and pauses[0]['generation'] == held[2]['generation'] and
         blocked[2]['observed_us'] <= pauses[0]['time_us'] <= released[2]['time_us'], 'maintenance gate releases only after real pause(true)')
    quiet = select('CYD_RC_CANCEL_QUIET')
    need([row['epoch'] for row in quiet] == [7, 9] and [row['kind'] for row in quiet] == ['STOP', 'MAINTENANCE'], 'distinct cancelled owner fences')
    for row in quiet:
        need(row['generation'] == row['old_generation'] + 1 and row['discard_after'] == row['discard_before'] + 1 and
             row['quiet_ms'] == 25 and row['no_eof'] == row['all_owners_quiet'] == 1 and
             row['ring_sends'] == row['ring_receives'] == row['ring_returns'], 'real discard completion and bounded quiet fence precede exact recovery')
    cancelled = [row for tag, row in rows if tag == 'CYD_F1_WRITE_RETURN' and row['result']]
    need(len(cancelled) == 1 and cancelled[0]['result'] == 0x103 and cancelled[0]['source_generation'] == held[2]['generation'] and
         cancelled[0]['pause_requested'] == cancelled[0]['cancelling'] == 1 and
         pauses[0]['time_us'] <= cancelled[0]['return_us'], 'real renderer returns INVALID_STATE after public maintenance cancellation')
    return dict(blocked=blocked, held=held, released=released, cancel_quiet=quiet,
                cancelled_write_returns=cancelled, application_total_stall_deadline_claim=False)


def validate_maintenance_records(rows, gates):
    def select(tag):return [row for found, row in rows if found == tag]
    owners = select('CYD_F1_CONTROL_OWNER')
    profiles = [('controller', 0, 1, 'sdk_main_startup'), ('stream', 0, 3, 'wrapped_task_creation'),
                ('decode', 1, 5, 'wrapped_task_creation'), ('output', 1, 6, 'wrapped_task_creation')]
    need(len(owners) == 4, 'all four actual public control-owner identities required')
    for owner, (role, core, declared, provenance) in zip(owners, profiles):
        need(isinstance(owner.get('task_handle'), int) and 0 < owner['task_handle'] <= 0xffffffff and owner == dict(
            role=role, task_handle=owner['task_handle'], core=core, declared_priority=declared, priority_provenance=provenance,
            effective_priority_limit=25, live_base_query=0, creation_profile_checked=1),
            'exact startup/creation provenance, never a live base-priority query')
    owner_by_handle = {owner['task_handle']: owner for owner in owners}
    need(len(owner_by_handle) == 4, 'distinct actual controller/stream/decode/output public task handles')
    starts, returned, held = (select('CYD_F1_CONTROL_ACQUIRE_' + stage) for stage in ('START', 'RETURN', 'HELD'))
    need([row['acquire'] for row in starts] == [row['acquire'] for row in returned] == [row['acquire'] for row in held] == [1, 2],
         'blocked maintenance and final maintenance have actual complete public call intervals')
    need(max(i for i, (tag, _) in enumerate(rows) if tag == 'CYD_F1_CONTROL_OWNER') <
         min(i for i, (tag, _) in enumerate(rows) if tag == 'CYD_F1_CONTROL_ACQUIRE_START'),
         'owner identities published before any actual acquisition')
    for begin, end, quiet in zip(starts, returned, held):
        need(begin['timeout_ms'] == 10000 and begin['time_us'] <= end['time_us'] <= quiet['time_us'] and
             begin['source_generation'] == end['source_generation'] > 0 and end['result'] == 0 and end['real_returned'] == 1 and
             end['token_epoch'] == quiet['token_epoch'] > 0 and quiet['live_clients'] == quiet['live_decoders'] == quiet['input_ready'] ==
             quiet['input_reading'] == quiet['input_writing'] == quiet['driver_live'] == 0 and quiet['input_available'] == quiet['input_leased'] == 1 and
             quiet['pauses_after'] > quiet['pauses_before'], 'public HELD/token follows actual owner cleanup and real driver pause')
    pause_starts, pause_returns = select('CYD_F1_CONTROL_PAUSE_START'), select('CYD_F1_CONTROL_PAUSE_RETURN')
    need([row['pause'] for row in pause_starts] == [row['pause'] for row in pause_returns] == [1, 2, 3] and
         [row['requested'] for row in pause_starts] == [1, 0, 1], 'one real cancellation, one resume and one final pause')
    for before, after in zip(pause_starts, pause_returns):
        required = {'pause', 'acquire', 'acquire_active', 'requested', 'fixture', 'core', 'priority', 'time_us',
                    'task_handle', 'owner_role', 'declared_priority', 'priority_provenance'}
        need(required <= set(before) and required | {'real_returned'} <= set(after), 'complete public caller and effective-priority observations')
        need(all(before[key] == after[key] for key in ('pause', 'acquire', 'acquire_active', 'requested', 'fixture', 'core',
                 'task_handle', 'owner_role', 'declared_priority', 'priority_provenance')) and
             before['time_us'] <= after['time_us'] and after['real_returned'] == 1, 'each public pause argument is forwarded unchanged')
        need(before['task_handle'] in owner_by_handle, 'pause caller names a captured actual task handle')
        owner = owner_by_handle[before['task_handle']]
        for observed in (before, after):
            need(observed['owner_role'] == owner['role'] and observed['core'] == owner['core'] and
                 observed['declared_priority'] == owner['declared_priority'] and observed['priority_provenance'] == owner['priority_provenance'] and
                 owner['declared_priority'] <= observed['priority'] < owner['effective_priority_limit'],
                 'stable actual owner/creation priority with independently sampled effective priority in the pinned scheduler range')
        need(before['acquire'] in (1, 2), 'public pause belongs to an actual acquisition')
        acquire, quiet = starts[before['acquire'] - 1], held[before['acquire'] - 1]
        if before['requested']:
            need(owner['role'] == 'controller' and before['requested'] == before['acquire_active'] == 1 and
                 acquire['time_us'] <= before['time_us'] <= after['time_us'] <= quiet['time_us'],
                 'pause(true) belongs to the controller request-to-HELD interval')
        else:
            need(owner['role'] in ('stream', 'decode', 'output') and before['acquire_active'] == 0 and before['acquire'] == 1 and
                 quiet['time_us'] <= before['time_us'], 'real pipeline resume follows HELD; controller abort is not a positive allowance')
    cancelled = gates['cancelled_write_returns'][0];pause = pause_starts[0];gate_release = gates['released'][2]
    need(starts[0]['time_us'] <= pause['time_us'] <= gate_release['time_us'] <= cancelled['return_us'] <= held[0]['time_us'] and
         pause['acquire'] == pause['acquire_active'] == cancelled['acquire_return'] == cancelled['pause_acquire'] == 1 and
         cancelled['pause_start'] == 1 and cancelled['source_generation'] == starts[0]['source_generation'],
         'real INVALID_STATE return belongs to the same observed public maintenance interval before HELD')
    for quiet, release in zip(gates['cancel_quiet'], gates['released'][1:]):
        discards = [row for tag, row in rows if tag == 'CYD_F1_CONTROL_DISCARD' and row['sequence'] == quiet['discard_after']]
        need(len(discards) == 1 and discards[0]['real_returned'] == 1 and
             release['time_us'] <= discards[0]['time_us'] <= quiet['quiet_start_us'] <= quiet['time_us'] and
             quiet['time_us'] - quiet['quiet_start_us'] >= 24000, 'quiet fence follows real discard and at least24ms of the25-tick wait')
    return dict(starts=starts, returned=returned, held=held, pause_starts=pause_starts, pause_returns=pause_returns,
                public_owner_provenance=owners, live_base_priority_queried=False, effective_priority_may_change=True)


def parse_word_allocation_log(log, require_terminal=True):
    records = [fields(line)[1] for line in log.splitlines() if line.startswith('CYD_RC_WORD_COMPLETE ')]
    if not require_terminal and not records:
        return dict(terminal=False)
    need(len(records) == 1, 'one complete word-plane census')
    row = records[0]
    need(row['attempts'] == row['successes'] + row['refusals'] and row['successes'] == row['frees'] and
         row['live_planes'] == row['live_bytes'] == row['private_heap'] == 0 and row['diagnostic_delays'] == row['owner_only_table'] == 1 and
         0 < row['peak_planes'] <= 16 and row['peak_bytes'] > 0, 'all old/candidate public word planes actually freed')
    return row


def validate_health_records(rows, cases, final):
    """Match the full public snapshot to predeclared causes and real callback ordinals."""
    def select(tag):return [row for found, row in rows if found == tag]
    expected_epochs = [1, 2, 3, 4, 5, 6, 8, 10]
    need(len(cases) == 8 and [p['epoch'] for p in cases] == expected_epochs, 'complete fixed typed-health case census')
    health, terminals = select('CYD_RC_HEALTH'), select('CYD_RC_TERMINAL')
    need([p['epoch'] for p in health] == [p['epoch'] for p in terminals] == expected_epochs,
         'one full health snapshot before every typed terminal; no missing or duplicate rows')
    begins = select('CYD_RC_BEGIN');need([p['epoch'] for p in begins] == list(range(1, 11)), 'all predeclared session entries')
    callbacks, allocations = select('CYD_RC_CALLBACK'), select('CYD_RC_ALLOC')
    fault_keys = set(('allocation_failures allocation_size allocation_caps decoder_failures decoder_generation decoder_codec decoder_stage '
        'decoder_result decoder_completion decoder_input_bytes decoder_allocation_sequence stream_failures stream_generation stream_completion '
        'stream_result output_failures output_generation output_stage output_write_errors output_configure_errors output_flush_errors output_result').split())
    before_keys = {'before_' + kind + '_failures' for kind in ('decoder', 'stream', 'output', 'allocation')}
    context = {'epoch', 'id', 'leg', 'generation', 'expected_detail', 'callbacks_seen'}
    decoder_keys = {key for key in fault_keys if key.startswith('decoder_') and key != 'decoder_failures'}
    decoder_payload = dict.fromkeys(decoder_keys, 0)
    for row, terminal, plan in zip(health, terminals, cases):
        epoch = plan['epoch'];detail = {2:15360, 4:23040}.get(epoch, 0);error = int(detail != 0);begin = begins[epoch - 1]
        need(set(row) == fault_keys | before_keys | context, 'complete public fault snapshot and per-leg before counters')
        signed = {'decoder_result', 'stream_result', 'output_result'}
        need(all(isinstance(row[k], int) and (-(2**31) <= row[k] < 2**31 if k in signed else 0 <= row[k] < 2**32)
                 for k in fault_keys | before_keys), 'exact public signed/unsigned32-bit health field ranges')
        need(plan['expected_detail'] == begin['expected_detail'] == row['expected_detail'] == detail and
             row['id'] == terminal['id'] == plan['id'] and row['leg'] == terminal['leg'] == plan['leg'] and
             row['generation'] == terminal['generation'] > 0 and terminal['allocation_error'] == plan['allocation_error'] == error,
             'health result is the predeclared leg detail, not OGP_MEMORY status or a chosen tolerance')
        begin_at = next(i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_BEGIN' and p['epoch'] == epoch)
        snapshot_at = next(i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_HEALTH' and p['epoch'] == epoch)
        terminal_at = next(i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_TERMINAL' and p['epoch'] == epoch)
        next_at = next((i for i, (tag, p) in enumerate(rows) if tag == 'CYD_RC_BEGIN' and p['epoch'] == epoch + 1), len(rows))
        need(begin_at < snapshot_at < terminal_at < next_at, 'the actual pre-assert snapshot precedes its terminal in the same session')
        before_callbacks = [p for p in callbacks if p['epoch'] < epoch]
        through_callbacks = [p for p in callbacks if p['epoch'] <= epoch]
        prior_errors = sum(p['epoch'] < epoch for p in cases if p['allocation_error'])
        need(row['before_decoder_failures'] == prior_errors and row['decoder_failures'] == prior_errors + error and
             row['before_stream_failures'] == row['stream_failures'] == row['before_output_failures'] == row['output_failures'] == 0 and
             row['before_allocation_failures'] == len(before_callbacks) and row['allocation_failures'] == row['callbacks_seen'] == len(through_callbacks),
             'before/after counts account for every real health callback and exactly the two declared decoder errors')
        need(terminal['decoder_delta'] == row['decoder_failures'] - row['before_decoder_failures'] == error and
             terminal['stream_delta'] == terminal['output_delta'] == 0 and
             terminal['allocation_delta'] == row['allocation_failures'] - row['before_allocation_failures'], 'typed terminal deltas equal the retained health snapshot')
        last = through_callbacks[-1] if through_callbacks else dict(bytes=0, caps=0)
        need(row['allocation_size'] == last['bytes'] and row['allocation_caps'] == last['caps'], 'last actual callback request is preserved in health')
        need(all(row[k] == 0 for k in fault_keys if k.startswith(('stream_', 'output_'))), 'no hidden stream/output fault payload or write/configure/flush counter')
        observed_decoder = {key:row[key] for key in decoder_keys}
        if error:
            scope, size, caps = (4, 1920, 2050) if epoch == 2 else (5, 23040, 0)
            targeted = [p for p in allocations if p['epoch'] == epoch and p['scope'] == scope and p['returned_null'] == 1]
            need(len(targeted) == 1 and targeted[0]['bytes'] == size and targeted[0]['caps'] == caps,
                 'one actual failed word/scratch call supplies the declared health cause')
            sequence = targeted[0]['callbacks_after'];callback = [p for p in callbacks if p['ordinal'] == sequence]
            need(row['decoder_generation'] == row['generation'] and row['decoder_codec'] == 4 and row['decoder_stage'] == 2 and
                 row['decoder_result'] == detail and row['decoder_completion'] == 9 and row['decoder_input_bytes'] > 0 and
                 row['decoder_allocation_sequence'] == sequence == row['allocation_failures'] and len(callback) == 1 and
                 callback[0]['epoch'] == epoch and callback[0]['scope'] == scope and callback[0]['bytes'] == size and
                 callback[0]['caps'] == (caps or 6144), 'exact generation/OGG/PROCESS/allocation completion/detail and real callback sequence')
            decoder_payload = observed_decoder
        else:
            need(observed_decoder == decoder_payload, 'healthy reopens preserve the last fault payload while introducing zero new decoder faults')
    need(all(health[-1][kind + '_failures'] == final[kind + '_failures'] for kind in ('decoder', 'stream', 'output', 'allocation')),
         'final census retains the complete last public health counts')
    return dict(snapshots=health, live_fields_queried=True, health_result_is_detail=True,
                ogg_status_substituted=False, exact_predeclared_details=[15360, 23040], unknown_health_allowed=False)


def validate(log, contract):
    need(not re.search(r'(?i)(Guru Meditation|panic.ed|CORRUPT HEAP|stack smashing|stack overflow|assert failed|watchdog got triggered|CYD_F1_TASK_FAILURE|CYD_RC_FAILURE|abort\(\))', log), 'no panic, watchdog, stack/heap corruption or target assertion')
    rows = [fields(line) for line in log.splitlines() if line.startswith(('CYD_RC_', 'CYD_F1_'))]
    def select(tag): return [row for found, row in rows if found == tag]
    known = {'CYD_RC_OWNER', 'CYD_RC_BOOT', 'CYD_RC_BEGIN', 'CYD_RC_RING_CREATE', 'CYD_RC_RING_TIMEOUT', 'CYD_RC_GATE_HELD',
             'CYD_RC_GATE_RELEASE', 'CYD_RC_GATE_PAUSE', 'CYD_RC_BLOCKED', 'CYD_RC_STOP_REQUEST', 'CYD_RC_STOP_RETURN',
             'CYD_RC_CANCEL_QUIET', 'CYD_RC_PRESSURE', 'CYD_RC_TERMINAL', 'CYD_RC_HEALTH', 'CYD_RC_CALLBACK', 'CYD_RC_ALLOC', 'CYD_RC_COMPLETE', 'CYD_RC_WORD_COMPLETE'}
    need(all(tag in known for tag, _ in rows if tag.startswith('CYD_RC_')), 'known typed runtime events only')
    boot = select('CYD_RC_BOOT')
    need(len(boot) == 1 and all(boot[0][key] == value for key, value in dict(actual_tasks=1, actual_output=1, public_raw=1,
         hardware=0, diagnostic_delays=1, normalizer_enabled=0, twdt_seconds=20, twdt_panic=1, int_wdt_ms=1000).items()), 'explicit diagnostic scope/profile, normalizer-enabled gate remains open')
    owners=select('CYD_RC_OWNER');need(len(owners)==1,'one public decoder stack publication')
    validate_owner_record(owners[0])
    need(select('CYD_F1_TASK_PROFILE') == [dict(role=role, **contract['task_bindings'][role]) for role in ('stream', 'decode', 'output')], 'unchanged real dual-core task creation profiles')
    need(select('CYD_F1_REFERENCE_BUDGET') == [dict(fixed_ms=90000, ordinary_ms=30000, whole_qemu_ms=600000, reset_on_progress=0)], 'fixed entry deadlines')
    need(select('CYD_F1_REFERENCE_COMPLETE') == [dict(cases=13, live=0, private_helpers=0, production_tasks=0, heap_integrity=1)], 'all13 independent public references complete first')
    references = select('CYD_F1_REFERENCE_CASE');need([row['index'] for row in references] == list(range(13)), 'all reference identities')
    pcm = [bytearray() for _ in references]
    for row in select('CYD_F1_REFERENCE_PCM'):
        need(0 <= row['index'] < 13 and re.fullmatch('(?:[0-9a-f]{2})+', str(row['hex'])), 'complete raw reference hex')
        body = bytes.fromhex(row['hex']);output = pcm[row['index']]
        need(row['offset'] == len(output) and row['bytes'] == len(body) and 0 < len(body) <= 256, 'exact continuous reference bytes')
        output.extend(body)
    entries = {row['id']: row for row in contract['entries']};raw_refs = {}
    for row, body in zip(references, pcm):
        entry = entries[row['index']]
        need(row['complete'] == 1 and row['driver'] == row['live'] == row['private_helpers'] == 0 and
             row['channels'] == entry['channels'] and row['frames'] == entry['logical_frames'] and
             row['pcm_bytes'] == entry['pcm_bytes'] == len(body) and row['sha256'] == hashlib.sha256(body).hexdigest() and
             row['opens'] == row['closes'] == entry['streams'] and row['core'] == 1 and row['priority'] == 3,
             'every complete independent reference matches its original fixture geometry and bytes')
        raw_refs[row['index']] = dict(bytes=len(body), sha256=row['sha256'])
    begins, terminals = select('CYD_RC_BEGIN'), select('CYD_RC_TERMINAL')
    need(len(begins) == 10 and len(terminals) == 8, 'ten finite sessions, eight typed terminal outputs')
    for row, plan in zip(begins, contract['runtime_sessions']):
        expected_pcm = sum(entries[x['reference']]['pcm_bytes'] if x['reference'] < 13 else 2112000 for x in plan['links'])
        expected_mono = sum(entries[x['reference']]['logical_frames'] * 2 if x['reference'] < 13 else 1056000 for x in plan['links'])
        need(all(row[key] == value for key, value in dict(epoch=plan['epoch'], id=plan['id'], leg=plan['leg'], fixture=plan['name'],
             expected_links=plan['expected_links'], actual_links=len(plan['complete_fixture_links']), expected_pcm=expected_pcm,
             expected_mono=expected_mono, mode=plan['mode'], target_link=plan['target_link'], expected_detail=plan['expected_detail'], ordinary_deadline_ms=30000, normalizer_enabled=0).items()),
             'every source/prefix extent and fault target declared before playback')
    cases, render_cases, render_links = [], [], []
    for row, plan in zip(terminals, contract['cases']):
        begin = begins[plan['epoch'] - 1];padding = (-begin['expected_mono']) % 1024
        need(all(row[key] == value for key, value in dict(epoch=plan['epoch'], id=plan['id'], leg=plan['leg'], allocation_error=plan['allocation_error'],
             links=plan['expected_links'], pcm_bytes=begin['expected_pcm'], mono_bytes=begin['expected_mono'], wire_bytes=begin['expected_mono'] + padding,
             padding_bytes=padding, padding_blocks=int(padding > 0), running=0, pending=0, failed=0, decoder_delta=plan['allocation_error'], stream_delta=0, output_delta=0,
             live_clients=0, live_decoders=0, word_live=0, pressure_live=0, heap_integrity=1).items()) and row['generation'] > 0 and
             row['ring_sends'] == row['ring_receives'] == row['ring_returns'], 'exact typed prefix/full terminal after all public owners and real ring are quiet')
        need(re.fullmatch('[0-9a-f]{64}', row['sha256']) and re.fullmatch('[0-9a-f]{64}', row['render_sha256']), 'complete source and mono digests')
        cases.append(dict(fixture=plan['name'], sha256=row['sha256'], pcm_bytes=row['pcm_bytes']))
        render_cases.append(dict(fixture=plan['name'], sha256=row['render_sha256'], mono_bytes=row['mono_bytes']))
    groups = {};epoch = 0
    for tag, row in rows:
        if tag == 'CYD_RC_BEGIN':epoch = row['epoch'];groups[epoch] = []
        elif epoch:groups[epoch].append((tag, row))
    for plan in contract['cases']:
        links = [row for tag, row in groups[plan['epoch']] if tag == 'CYD_F1_LINK']
        rendered = [row for tag, row in groups[plan['epoch']] if tag == 'CYD_F1_RENDER_LINK']
        source_writes = [row for tag, row in groups[plan['epoch']] if tag == 'CYD_F1_WRITE_RETURN']
        need(sum(row['data_bytes'] for row in source_writes) == begins[plan['epoch'] - 1]['expected_pcm'] and
             all(row['result'] == 0 for row in source_writes), 'every typed full/prefix source byte has its own retained successful renderer return')
        need(len(links) == len(rendered) == len(plan['links']), 'every prefix/full logical source and mono span retained exactly once')
        for index, (source, mono, link) in enumerate(zip(links, rendered, plan['links'])):
            ref = link['reference'];channels = entries[ref]['channels'] if ref < 13 else 2
            need(source['index'] == mono['index'] == index and source['reference'] == mono['reference'] == ref and
                 source['channels'] == mono['channels'] == channels and source['gain_q8'] == mono['gain_q8'] == link['gain_q8'] and
                 mono['volume'] == plan['volume'], 'exact original ordered per-link public geometry/gain')
            render_links.append(mono)
    opens, closes = select('CYD_F1_OBS_OPEN'), select('CYD_F1_OBS_CLOSE')
    need([row['instance'] for row in opens] == list(range(1, 58)) and
         sorted(row['instance'] for row in closes) == list(range(1, 58)) and all(row['result'] == 0 for row in opens + closes),
         'all57 real raw/simple public owners open and close successfully exactly once')
    opened = {row['instance']: row for row in opens}
    need(all(row['kind'] == opened[row['instance']]['kind'] and row['link'] == opened[row['instance']]['link'] and
             row['stream'] == opened[row['instance']]['stream'] and row['pending'] == 0 for row in closes), 'same exact public owner/link/stream closes without abandoned ownership')
    calls = select('CYD_F1_OBS_CALL')
    need(calls and all(row['result'] in (0, -8) and 0 <= row['consumed'] <= row['input'] and
         0 <= row['decoded'] <= row['capacity'] and (row['result'] != -8 or row['decoded'] == 0 and row['needed'] > row['capacity']) for row in calls),
         'only genuine successful public decode or documented buffer growth with exact byte bounds')
    scratch_calls = [row for tag, row in groups[4] if tag == 'CYD_F1_OBS_CALL']
    need(len(scratch_calls) == 1 and scratch_calls[0]['kind'] == 'raw' and scratch_calls[0]['link'] == 0 and
         scratch_calls[0]['result'] == -8 and scratch_calls[0]['capacity'] == 11520 and scratch_calls[0]['needed'] == 23040 and
         scratch_calls[0]['decoded'] == scratch_calls[0]['retry'] == 0, 'scratch refusal follows a real fresh public11520→23040 BUFF_NOT_ENOUGH result')
    need(not [row for tag, row in groups[2] if tag == 'CYD_F1_OBS_CALL' and row['link'] == 2], 'dual workspace refusal occurs before any C8 raw decode')
    writes = select('CYD_F1_WRITE_RETURN')
    need(writes and [row['call'] for row in writes] == list(range(1, len(writes) + 1)) and all(
         row['before_status'] == row['after_status'] == 0 and row['before_bytes'] == row['after_bytes'] == 32 and row['equal'] == 1 and
         row['core'] == 1 and row['priority'] == 6 and 0 < row['data_bytes'] <= 3072 and row['start_us'] <= row['return_us'] for row in writes),
         'full borrowed source independently hashed before and after every real return, including cancellation')
    finals = select('CYD_RC_COMPLETE');need(len(finals) == 1, 'one final native typed-control census');final = finals[0]
    need(all(final[key] == value for key, value in dict(controls=6, terminals=8, healthy=6, allocation_errors=2, cancelled=2,
         opens=57, closes=57, HTTP_opens=10, HTTP_cleanup=10, decoder_failures=2, stream_failures=0, output_failures=0,
         diagnostic_delays=1, normalizer_enabled=0, enabled_normalizer_qualified=0, private_heap=0, actual_allocators=1, hardware=0, post_output_oracle_pending=1).items()) and
         final['pressure_allocations'] == final['pressure_frees'] > 0 and final['ring_sends'] == final['ring_receives'] == final['ring_returns'],
         'all actual resource owners close after finite controls; enabled normalizer/hardware remain unqualified')
    need(final['source_writes'] == final['layout_stamps'] == final['gain_stamps'] == len(writes), 'all real packets retain ordered layout/gain/write census')
    need(final['static_pressure_bytes'] == 512 and final['static_callback_bytes'] == 240 and final['static_alloc_event_bytes'] == 480 and
         0 < final['pressure_peak_blocks'] <= 128 and final['pressure_peak_bytes'] > 0, 'exact bounded32-bit static observer arrays and measured positive pressure witness')
    allocation = validate_allocator_records(select('CYD_RC_CALLBACK'), select('CYD_RC_ALLOC'), final)
    health = validate_health_records(rows, contract['cases'], final)
    gates = validate_gate_records(rows, contract['runtime_sessions'])
    maintenance = validate_maintenance_records(rows, gates)
    words = parse_word_allocation_log(log)
    pressure = select('CYD_RC_PRESSURE')
    need(len(pressure) == 8 and [row['mode'] for row in pressure] == [1, 2, 0, 3, 0, 0, 0, 0] and all(
         row['pressure_live'] == row['pressure_bytes'] == row['fabricated_return'] == 0 and row['pressure_allocations'] == row['pressure_frees'] for row in pressure),
         'pressure withdrawn before every typed terminal and recovery')
    for index, expected in [(0, dict(triggered=1, target_byte_nulls=1, target_word_nulls=0, target_scratch_nulls=0, target_word_successes=8)),
                            (1, dict(triggered=1, target_byte_nulls=1, target_word_nulls=1, target_scratch_nulls=0, target_word_successes=0)),
                            (3, dict(triggered=1, target_byte_nulls=0, target_word_nulls=0, target_scratch_nulls=1, target_word_successes=0, raw_growth=1))]:
        need(all(pressure[index][key] == value for key, value in expected.items()), 'exact real outcome for each predeclared pressure mode')
    need(final['pressure_allocations'] == pressure[-1]['pressure_allocations'] and
         pressure[-1]['pressure_probe_nulls'] == len(allocation['pressure_helper_nulls']), 'separate pressure-helper allocation/free/NULL census')
    need(all(not row['triggered'] and not row['target_byte_nulls'] and not row['target_word_nulls'] and not row['target_scratch_nulls'] and
         not row['target_word_successes'] for row in pressure if row['mode'] == 0), 'reopen/drain/resume legs contain no armed diagnostic allocation target')
    return dict(cases=cases, render_cases=render_cases, render_links=render_links, reference_pcm=raw_refs,
                allocation=allocation, health=health, gates=gates, maintenance=maintenance, words=words, complete=final,
                normalization_enabled=False, normalizer_enabled_qualified=False, hardware_qualified=False), [bytes(body) for body in pcm]
