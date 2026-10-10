"""Read quiet-firmware health without accepting missing or reset counters."""
import re
import time

from common import Board, require

NUMERIC = ('uptime_ms', 'reset_reason', 'heap', 'largest', 'minimum_heap',
           'tasks', 'allocation_failures', 'task_watchdog_events')


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
    return {key: raw[key] for key in ('schema', 'boot_id', *NUMERIC)}


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
