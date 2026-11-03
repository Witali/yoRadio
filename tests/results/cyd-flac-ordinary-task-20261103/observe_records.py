"""Owned pure observation checking; captured modules are never imported."""
import re

CONFIG = dict(twdt_seconds=5, twdt_panic=0, int_wdt_ms=300, idle0=1, idle1=1,
              quiet_heap=1, diagnostics=0, ogg_timeline=1, aac_plus=1,
              custom_flac=1, real_output_driver=0, hardware=0)

FIXTURES = ('flac-24bit-mid-verbatim', 'flac-16bit-stereo-verbatim',
            'flac-24bit-mid-verbatim-block8192')

MINIMUM_US, DEADLINE_US = 15000000, 90000000

def need(value, reason):
    if not value:
        raise ValueError(reason)

def fields(line, tag):
    parts = line.split()
    need(parts and parts[0] == tag, 'ordered actual event: ' + tag)
    result = {}
    for item in parts[1:]:
        pair = item.split('=', 1)
        need(len(pair) == 2 and pair[0] not in result, 'unique complete event fields')
        result[pair[0]] = pair[1]
    return result

def numeric(row, keys):
    result = {}
    for key in keys:
        value = row.get(key, '')
        need(re.fullmatch(r'0|[1-9][0-9]*', value) is not None, 'unsigned actual field: ' + key)
        result[key] = int(value)
    return result

def parse(log, fixtures):
    # No-panic production policy still fails on a genuine SDK warning. Never
    # turn the absence of a reset into a passing watchdog observation.
    log = re.sub(r'\x1b\[[0-9;]*m', '', log)
    forbidden = (r'CYD_FLAC_TASK_FAILURE|Guru Meditation|assert failed|panic.ed|'
                 r'stack (?:smashing|overflow)|CORRUPT HEAP|'
                 r'Task watchdog|Interrupt wdt|watchdog[^\n]*(?:trigger|timeout|did not reset)|'
                 r'^[WE]\s*\([^\n)]*\)\s*(?:task_wdt|int_wdt):')
    need(re.search(forbidden, log, re.I | re.M) is None, 'no real assertion/heap/watchdog warning or timeout')
    rows = {row['name']: row for row in fixtures}
    need(len(rows) == len(fixtures) == 130 and all(name in rows for name in FIXTURES), 'all130 original fixture identities')
    events = [line for line in log.replace('\r\n', '\n').splitlines() if line.startswith('CYD_FLAC_')]
    need(len(events) >= 9, 'complete original and positive phase event sequence')
    boot = fields(events[0], 'CYD_FLAC_TASK_BOOT')
    need(boot == dict(actual_audio_service_tu='1', sdk='v6.0.2', core0_stream='1',
                      core1_decode_output='1', hardware='0'), 'exact SDK/owner scope')
    config = fields(events[1], 'CYD_FLAC_ORDINARY_CONFIG')
    need(set(config) == set(CONFIG) and numeric(config, CONFIG) == CONFIG, 'reviewed production watchdog/heap and metadata selectors')
    original = []
    for index, (name, marker) in enumerate(zip(FIXTURES, ('ordered_eof', 'stop_reopen', 'maintenance_resume'))):
        row = fields(events[2 + index], 'CYD_FLAC_TASK_CASE')
        need(set(row) == {'id', marker, 'byte_compare', 'pcm_bytes'} and row['id'] == 'T' + str(index), 'unchanged original lifecycle order')
        need(numeric(row, (marker, 'byte_compare', 'pcm_bytes')) ==
             {marker: 1, 'byte_compare': 1, 'pcm_bytes': rows[name]['pcm_bytes']}, 'complete original exact PCM case')
        original.append(row)
    begin = fields(events[5], 'CYD_FLAC_ORDINARY_POSITIVE_BEGIN')
    need(set(begin) == {'minimum_us', 'deadline_us', 'started_us'}, 'fixed positive phase policy fields')
    begin = numeric(begin, begin)
    need(begin['minimum_us'] == MINIMUM_US and begin['deadline_us'] == DEADLINE_US and begin['started_us'] > 0, 'unchanged positive phase policy')
    names = ('index elapsed_us pcm_bytes created destroyed http_cleanup writes layouts gains feed_calls decode_calls '
             'max_decode_call_us heap_free heap_min heap_largest internal_free internal_largest dma_free dma_largest '
             'stream_stack_free decode_stack_free output_stack_free idle0_status idle1_status workspace live_decoders '
             'live_clients allocation_failures decoder_failures stream_failures output_failures').split()
    expected = rows[FIXTURES[2]]
    observations = []
    previous = dict(elapsed_us=0, writes=0, feed_calls=0, decode_calls=0)
    cursor = 6
    while cursor < len(events) and events[cursor].startswith('CYD_FLAC_ORDINARY_ITERATION '):
        raw = fields(events[cursor], 'CYD_FLAC_ORDINARY_ITERATION')
        need(set(raw) == set(names) | {'sha256'}, 'exact actual resource/owner observations')
        row = numeric(raw, names)
        need(row['index'] == len(observations) and row['index'] < 10000, 'complete ordered iteration sequence')
        need(previous['elapsed_us'] < row['elapsed_us'] < DEADLINE_US and previous['elapsed_us'] < MINIMUM_US, 'positive phase stops at first sufficient complete file')
        need(raw['sha256'] == expected['pcm_sha256'] and row['pcm_bytes'] == expected['pcm_bytes'], 'actual whole original8192 PCM hash/length')
        need(row['created'] == row['destroyed'] == row['http_cleanup'] == row['index'] + 6, 'all five original and each new actual owner cleaned')
        need(row['writes'] == row['layouts'] == row['gains'] and
             all(row[key] > previous[key] for key in ('writes', 'feed_calls', 'decode_calls')),
             'actual PCM/metadata/feed/decode progress every complete file')
        need(row['max_decode_call_us'] > 0, 'genuine measured decoder calls')
        for free, largest in (('heap_free', 'heap_largest'), ('internal_free', 'internal_largest'), ('dma_free', 'dma_largest')):
            need(0 < row[largest] <= row[free], 'valid capability-specific heap observation')
        need(0 < row['heap_min'] <= row['heap_free'], 'valid minimum heap observation')
        for key, limit in (('stream_stack_free', 6144), ('decode_stack_free', 16384), ('output_stack_free', 4096)):
            need(0 < row[key] <= limit, 'original task stack observation: ' + key)
        need(all(row[key] == 0 for key in ('idle0_status', 'idle1_status', 'workspace', 'live_decoders',
                 'live_clients', 'allocation_failures', 'decoder_failures', 'stream_failures', 'output_failures')),
             'actual idle subscriptions and quiet positive owner/fault observations')
        row['sha256'] = raw['sha256']; observations.append(row); previous = row; cursor += 1
    need(observations and previous['elapsed_us'] >= MINIMUM_US, 'at least three actual five-second SDK periods')
    need(cursor < len(events), 'positive phase terminal exists')
    end = fields(events[cursor], 'CYD_FLAC_ORDINARY_POSITIVE_END'); cursor += 1
    need(set(end) == {'iterations', 'elapsed_us', 'last_completion_us', 'minimum_us', 'deadline_us'}, 'positive termination fields')
    end = numeric(end, end)
    need(end['iterations'] == len(observations) and end['last_completion_us'] == previous['elapsed_us'] and
         previous['elapsed_us'] <= end['elapsed_us'] < DEADLINE_US and
         end['minimum_us'] == MINIMUM_US and end['deadline_us'] == DEADLINE_US, 'exact actual positive terminal accounting')
    need(cursor < len(events), 'actual complete terminal exists')
    final = fields(events[cursor], 'CYD_FLAC_ORDINARY_COMPLETE'); cursor += 1
    target = dict(original_cases=3, positive_iterations=len(observations), actual_audio_service_tu=1,
                  created=len(observations)+5, destroyed=len(observations)+5,
                  real_http_cleanup=len(observations)+5, writes=previous['writes'],
                  layouts=previous['layouts'], gains=previous['gains'], core_bindings=1,
                  hardware=0, real_output_driver=0, oom_injection=0,
                  deliberate_backpressure=0, semantic_fault_controls=0)
    need(cursor == len(events) and set(final) == set(target) and numeric(final, target) == target,
         'one complete actual terminal with no unqualified scope claims')
    return dict(original_cases=original, positive_iterations=observations,
                positive_elapsed_us=end['elapsed_us'], actual_output_driver=False,
                physical_hardware=False, full_radio_resource_claim=False,
                native_fault_injection=False, production_watchdog_policy=CONFIG)
