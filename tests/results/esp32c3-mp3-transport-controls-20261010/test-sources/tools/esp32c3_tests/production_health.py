"""Read quiet-firmware health without accepting missing or reset counters."""
import re
import time

from common import Board, require

NUMERIC = ('uptime_ms', 'reset_reason', 'heap', 'largest', 'minimum_heap',
           'tasks', 'allocation_failures', 'task_watchdog_events')
OUTPUT_COUNTERS = ('completion_queue_drops', 'write_errors')
COUNTER_MASK = (1 << 32) - 1


def validate_pipeline(probe, output):
    """Keep only bounded numeric diagnostics; missing events stay missing."""
    def word(value):
        return type(value) is int and 0 <= value <= COUNTER_MASK
    require(type(probe) is dict, 'Invalid pipeline diagnostic')
    require(type(probe.get('timer_hz')) is int and probe['timer_hz'] == 1_000_000,
            'Invalid diagnostic timer frequency')
    sequence = probe.get('sequence')
    require(word(sequence) and output['available'] and
            sequence == output['completion_queue_drops'], 'Inconsistent pipeline sequence')
    histogram, events = probe.get('phase_drops'), probe.get('events')
    require(type(histogram) is list and len(histogram) == 8 and all(map(word, histogram)) and
            (sum(histogram) & COUNTER_MASK) == sequence, 'Invalid pipeline phase counts')
    require(type(events) is list and len(events) <= 16, 'Invalid pipeline event capacity')
    for index, event in enumerate(events):
        require(type(event) is list and len(event) == 7 and all(map(word, event)),
                'Invalid pipeline event')
        require(event[0] == ((sequence - len(events) + 1 + index) & COUNTER_MASK) and
                event[2] < 8, 'Invalid pipeline event order or phase')
    require(events or sequence == 0, 'Missing pipeline event history')
    result = dict(timer_hz=probe['timer_hz'], sequence=sequence,
                  phase_drops=list(histogram), events=[list(e) for e in events])
    if 'stream_failure' in probe:
        failure = probe['stream_failure']
        require(type(failure) is dict and all(word(failure.get(k))
                for k in ('sequence', 'timestamp_us')), 'Invalid stream failure identity')
        codes = ('http_result', 'esp_tls_error', 'tls_code', 'system_errno')
        require(all(type(failure.get(k)) is int and -(1 << 31) <= failure[k] < (1 << 31)
                    for k in codes), 'Invalid stream failure codes')
        result['stream_failure'] = {k: failure[k] for k in ('sequence', 'timestamp_us', *codes)}
    return result


def validate_output(output):
    require(type(output) is dict and type(output.get('available')) is bool,
            'Invalid output health availability')
    for key in OUTPUT_COUNTERS:
        require(type(output.get(key)) is int and 0 <= output[key] <= COUNTER_MASK,
                'Missing or invalid output counter: ' + key)
    return {key: output[key] for key in ('available', *OUTPUT_COUNTERS)}


def read_health(board):
    raw = board.json('/api/native/health')
    require(type(raw) is dict and type(raw.get('schema')) is int and
            raw['schema'] == 1, 'Missing supported health schema')
    require(type(raw.get('boot_id')) is str and
            re.fullmatch(r'[0-9a-f]{16}', raw['boot_id']), 'Invalid boot identity')
    for key in NUMERIC:
        require(type(raw.get(key)) is int and raw[key] >= 0,
                'Missing or invalid health field: ' + key)
    require(raw['tasks'] > 0 and raw['largest'] <= raw['heap'] and
            raw['minimum_heap'] <= raw['heap'], 'Inconsistent heap snapshot')
    # Never retain extra fields or response bodies from the device.
    result = {key: raw[key] for key in ('schema', 'boot_id', *NUMERIC)}
    # Schema 1 firmware predates output telemetry; basic health stays compatible.
    if 'output' in raw:
        result['output'] = validate_output(raw['output'])
    if 'pipeline' in raw:
        result['pipeline'] = validate_pipeline(raw['pipeline'], validate_output(raw.get('output')))
    return result


def output_window(samples):
    """Measure a caller-selected sustained-play window, excluding Start/Stop.

    Missing measurements fail closed. Modular increments handle uint32 wrap;
    a reboot is rejected by check_health. Compare adjacent samples so any
    observed increments cannot cancel out at the window endpoints.
    """
    check_health(samples)
    require(len(samples) >= 2, 'Need two output observations')
    require(samples[-1]['uptime_ms'] > samples[0]['uptime_ms'],
            'No elapsed output observation time')
    totals = {key: 0 for key in OUTPUT_COUNTERS}
    previous = None
    for row in samples:
        output = validate_output(row.get('output'))
        require(output['available'], 'Output health is unavailable on this backend')
        if previous is not None:
            for key in OUTPUT_COUNTERS:
                totals[key] += (output[key] - previous[key]) & COUNTER_MASK
        previous = output
    return dict(samples=len(samples),
                elapsed_ms=samples[-1]['uptime_ms']-samples[0]['uptime_ms'], **totals)


def check_health(samples):
    require(samples, 'No production health evidence')
    first = samples[0]
    previous = first
    for row in samples:
        require(row['boot_id'] == first['boot_id'], 'Firmware rebooted during observation')
        require(row['uptime_ms'] >= previous['uptime_ms'], 'Firmware uptime decreased')
        require(row['allocation_failures'] == 0, 'Firmware reported an allocation failure')
        require(row['task_watchdog_events'] == 0, 'Firmware reported a task watchdog event')
        previous = row
    return dict(samples=len(samples), boot_id=first['boot_id'],
                minimum_heap=min(r['heap'] for r in samples),
                minimum_largest=min(r['largest'] for r in samples),
                allocation_failures=0, task_watchdog_events=0)


class HealthBoard(Board):
    """Every status observation includes health; failures retain the offending row.

    Use a new instance after a deliberate OTA/reboot. Each observation performs
    two HTTP requests; status timing therefore includes the health request.
    This does not measure DMA continuity, PCM quality or all decoder errors.
    """
    def __init__(self, origin):
        super().__init__(origin)
        self.health_samples = []

    def status(self):
        state = super().status()
        started = time.perf_counter()
        health = read_health(self)
        self.health_samples.append(dict(at=time.perf_counter(),
            request_ms=(time.perf_counter()-started)*1000, **health))
        # Two endpoints plus this observation detect persistent fault counters
        # and a reboot without quadratic work over a long recording.
        check_health([self.health_samples[0], *self.health_samples[-2:]])
        return state
