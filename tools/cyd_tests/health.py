"""Validate native CYD health without inventing unavailable measurements."""
import math
import re
import time

from tools.esp32c3_tests.common import exception_details, require
from .common import CydBoard

U32 = 0xffffffff
FAULT_FIELDS = {
    'last_allocation_failure': ('size', 'caps'),
    'decoder_failure': ('sequence', 'generation', 'codec', 'stage', 'result', 'completion',
                        'input_bytes', 'allocation_sequence'),
    'stream_failure': ('sequence', 'generation', 'completion', 'result'),
    'output': ('failures', 'write_errors', 'configure_errors', 'flush_errors', 'generation', 'stage', 'result'),
}
DRIVER_FIELDS = ('writes', 'requested_bytes', 'written_bytes', 'errors', 'timeouts',
                 'short_writes', 'timing_samples', 'invalid_time_samples')


def integer(value, maximum=U32, minimum=0):
    return type(value) is int and minimum <= value <= maximum


def percentage(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 100


def validate_health(raw, backend):
    require(type(raw) is dict and type(raw.get('schema')) is int and raw['schema'] == 1 and
            type(raw.get('boot_id')) is str and re.fullmatch('[0-9a-f]{16}', raw['boot_id']),
            'Invalid CYD health identity/schema')
    numeric = ('uptime_ms', 'reset_reason', 'heap', 'largest', 'minimum_heap', 'tasks', 'allocation_failures', 'cores')
    require(all(integer(raw.get(k), (1 << 64)-1 if k == 'uptime_ms' else U32) for k in numeric),
            'Missing or invalid CYD health counters')
    require(raw['cores'] == 2 and raw['tasks'] > 0 and raw['largest'] <= raw['heap'] and
            raw['minimum_heap'] <= raw['heap'], 'Inconsistent CYD heap/core snapshot')
    result = {k: raw[k] for k in ('schema', 'boot_id', *numeric)}
    result['backend'] = backend
    memory = raw.get('memory')
    keys = ('internal_free', 'internal_largest', 'dma_free', 'dma_largest')
    require(type(memory) is dict and all(integer(memory.get(k)) for k in keys) and
            memory['internal_largest'] <= memory['internal_free'] and
            memory['dma_largest'] <= memory['dma_free'], 'Invalid CYD memory capability snapshot')
    result['memory'] = {k: memory[k] for k in keys}
    for key, fields in FAULT_FIELDS.items():
        value = raw.get(key)
        require(type(value) is dict and all(integer(value.get(k), (1 << 31)-1, -(1 << 31))
                if k == 'result' else integer(value.get(k)) for k in fields), 'Invalid CYD fault group: ' + key)
        result[key] = {k: value[k] for k in fields}
    driver = raw.get('output_driver')
    require(type(driver) is dict and all(integer(driver.get(k), (1 << 64)-1 if k in
            ('requested_bytes', 'written_bytes') else U32) for k in DRIVER_FIELDS) and
            all(type(driver.get(k)) is bool for k in ('saturated', 'timing_enabled')),
            'Invalid CYD driver counters')
    drops = driver.get('completion_queue_drops')
    require((drops is None or integer(drops)) if backend == 'pdm' else drops is None,
            'Missing or invented backend completion-queue observation')
    timed = driver['timing_enabled'] and driver['timing_samples'] > 0
    require(all(integer(driver.get(k), (1 << 64)-1) if timed else driver.get(k) is None
                for k in ('write_us', 'max_write_us')), 'Invalid CYD driver timing availability')
    if timed:
        require(driver['max_write_us'] <= driver['write_us'], 'Inconsistent driver write timing')
    result['output_driver'] = {k: driver[k] for k in (*DRIVER_FIELDS, 'saturated', 'timing_enabled',
                                                    'completion_queue_drops', 'write_us', 'max_write_us')}
    queue = raw.get('input')
    keys = ('resident', 'minimum', 'target', 'limit', 'ready', 'reading', 'writing',
            'released', 'ready_payload_bytes', 'reading_payload_bytes')
    require(type(queue) is dict and all(type(queue.get(k)) is bool for k in ('available', 'leased')) and
            all(integer(queue.get(k)) for k in keys), 'Invalid CYD input snapshot')
    if queue['available']:
        require(0 < queue['minimum'] <= queue['resident'] and
                queue['minimum'] <= queue['limit'] <= queue['target'] and
                queue['ready'] + queue['reading'] + queue['writing'] <= queue['resident'],
                'Inconsistent CYD input ownership')
    result['input'] = {k: queue[k] for k in ('available', 'leased', *keys)}
    cpu = raw.get('cpu')
    require(type(cpu) is dict and all(type(cpu.get(k)) is bool for k in ('enabled', 'available')) and
            integer(cpu.get('sample_uptime_ms'), (1 << 64)-1) and integer(cpu.get('snapshot_failures')) and
            type(cpu.get('core_percent')) is list and len(cpu['core_percent']) == 2,
            'Invalid CYD CPU schema')
    available = cpu['available']
    require(not available or cpu['enabled'], 'CPU availability without diagnostic sampler')
    values = [cpu.get('overall_percent'), *cpu['core_percent']]
    require(all(percentage(v) if available else v is None for v in values), 'Invalid CPU observation availability')
    if available:
        require(0 <= raw['uptime_ms'] - cpu['sample_uptime_ms'] <= 15000 and
                abs(cpu['overall_percent'] - sum(cpu['core_percent'])/2) <= .15,
                'Stale or inconsistent two-core CPU snapshot')
    tasks, copied = cpu.get('tasks'), {}
    require(type(tasks) is dict, 'Missing CYD task CPU/stack snapshots')
    for role in ('stream', 'decode', 'output', 'http'):
        task = tasks.get(role)
        require(type(task) is dict and
                (task.get('percent_of_one_core') is None or available and percentage(task['percent_of_one_core'])) and
                (task.get('stack_free_min') is None or integer(task['stack_free_min'])),
                'Invalid CYD task observation: ' + role)
        copied[role] = {k: task[k] for k in ('percent_of_one_core', 'stack_free_min')}
    result['cpu'] = {k: cpu[k] for k in ('enabled', 'available', 'sample_uptime_ms',
                                       'snapshot_failures', 'overall_percent', 'core_percent')}
    result['cpu']['tasks'] = copied
    return result


def check_health(samples, *, require_cpu=False):
    require(samples, 'No CYD health observations')
    first, previous = samples[0], samples[0]
    for row in samples:
        require(row['boot_id'] == first['boot_id'] and row['uptime_ms'] >= previous['uptime_ms'],
                'CYD restarted or uptime decreased')
        require(row['allocation_failures'] == 0 and row['decoder_failure']['sequence'] == 0 and
                row['stream_failure']['sequence'] == 0 and row['output']['failures'] == 0 and
                all(row['output'][k] == 0 for k in ('write_errors', 'configure_errors', 'flush_errors')),
                'CYD reported an allocation/stream/decoder/output failure')
        require(not row['output_driver']['saturated'], 'CYD driver counters saturated')
        if require_cpu:
            require(row['cpu']['available'] and all(row['cpu']['tasks'][role]['percent_of_one_core'] is not None and
                    row['cpu']['tasks'][role]['stack_free_min'] is not None for role in ('stream', 'decode', 'output', 'http')),
                    'Missing diagnostic CPU/stack observations')
        for key in DRIVER_FIELDS:
            require(row['output_driver'][key] >= previous['output_driver'][key], 'CYD driver counter decreased')
        before, after = previous['output_driver']['completion_queue_drops'], row['output_driver']['completion_queue_drops']
        require(before is None or integer(after) and after >= before,
                'CYD queue counter availability changed or decreased')
        previous = row
    return dict(samples=len(samples), boot_id=first['boot_id'],
                minimum_heap=min(r['heap'] for r in samples), minimum_largest=min(r['largest'] for r in samples),
                watchdog_counter_available=False, cpu_observed=any(r['cpu']['available'] for r in samples))


def playback_window(states, samples, *, warmup=2, minimum=5, require_cpu=False):
    require(len(states) == len(samples) and all(b['seconds'] > a['seconds'] for a, b in zip(states, states[1:])),
            'Unpaired or nonmonotonic CYD status/health observations')
    selected = [(s, h) for s, h in zip(states, samples) if s['seconds'] >= warmup]
    require(len(selected) >= minimum and all(s['audio'] and s['pcm_sample_rate'] > 0 and
            s['pcm_channels'] > 0 for s, h in selected), 'Missing continuous decoded CYD playback')
    rows = [h for s, h in selected]
    result = check_health(rows, require_cpu=require_cpu)
    if rows[0]['backend'] == 'pdm':
        require(all(integer(r['output_driver']['completion_queue_drops']) for r in rows),
                'Missing PDM queue observation during decoded playback')
    require(rows[-1]['uptime_ms'] > rows[0]['uptime_ms'], 'No elapsed CYD playback window')
    deltas = {}
    for key in DRIVER_FIELDS:
        deltas[key] = rows[-1]['output_driver'][key] - rows[0]['output_driver'][key]
    require(deltas['writes'] > 0 and deltas['written_bytes'] > 0 and deltas['requested_bytes'] > 0,
            'No CYD driver output progress during decoded playback')
    require(all(deltas[k] == 0 for k in ('errors', 'timeouts', 'short_writes', 'invalid_time_samples')),
            'CYD driver error during playback')
    drops = rows[0]['output_driver']['completion_queue_drops']
    drops = None if drops is None else rows[-1]['output_driver']['completion_queue_drops'] - drops
    require(drops is None or drops == 0, 'CYD PDM completion queue drop during playback')
    return dict(health=result, driver_delta=deltas, completion_queue_drops=drops,
                queue_observation_available=drops is not None, cpu_and_stack=[r['cpu'] for r in rows])


class HealthBoard(CydBoard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health_samples = []

    def status(self):
        state = super().status()
        started = time.perf_counter()
        row = validate_health(self.json('/api/native/health'), self.artifact.backend)
        self.health_samples.append(dict(at=time.perf_counter(), request_ms=(time.perf_counter()-started)*1000, **row))
        require(row['cpu']['enabled'] == self.artifact.diagnostics and
                row['output_driver']['timing_enabled'] == self.artifact.diagnostics,
                'Live diagnostic availability differs from saved CYD profile')
        check_health([self.health_samples[0], *self.health_samples[-2:]])
        return state


def failure_snapshot(board):
    start = len(board.health_samples)
    result = {}
    try:
        result['status'] = board.status()
    except Exception as error:
        result['exception_chain'] = exception_details(error)
    result['health'] = board.health_samples[start:]
    return result
