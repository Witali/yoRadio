"""Convert wrapping guest timestamps and journal bounded runtime observations."""
from collections import deque
from copy import deepcopy
import json


class GuestMicroseconds:
    """Unwrap the C2 QEMU radio clock, sampled at least once per 2**32 us period."""
    def __init__(self):
        self.previous, self.wraps = None, 0

    def update(self, raw):
        """Return monotonic microseconds; guest resets do not reset QEMU virtual time."""
        if type(raw) is not int or not 0 <= raw < 2 ** 32:
            raise ValueError('Expected an unsigned 32-bit guest clock sample')
        if self.previous is not None and raw < self.previous:
            self.wraps += 1
        self.previous = raw
        return self.wraps * 2 ** 32 + raw


class RuntimeJournal:
    """Append complete numeric observations once and retain only a bounded report tail."""
    def __init__(self, path, tail=32):
        self.stream = path.open('x', encoding='utf-8', newline='\n')
        self.events = self.snapshots = self.http_requests = self.outages = 0
        self.tail = deque(maxlen=tail)
        self.first = None
        self.minimum_free = self.minimum_sdk = None
        self.stack_minima = {}
        self.maximum_http_seconds = 0

    def append(self, kind, row):
        """Store no raw stack bytes, HTTP bodies, headers or credentials."""
        if kind not in ('snapshot', 'http', 'outage'):
            raise ValueError('Unknown runtime journal event')
        encoded = json.dumps({'kind': kind, 'data': row}, separators=(',', ':'), allow_nan=False)
        self.stream.write(encoded + '\n')
        self.stream.flush()
        self.events += 1
        if kind == 'snapshot':
            saved = deepcopy(row)
            self.first = self.first or saved
            self.tail.append(saved)
            self.snapshots += 1
            free, sdk = row['heap']['free_bytes'], row['heap']['minimum_free_bytes']
            self.minimum_free = free if self.minimum_free is None else min(self.minimum_free, free)
            self.minimum_sdk = sdk if self.minimum_sdk is None else min(self.minimum_sdk, sdk)
            for task in row['tasks']:
                name, free = task['name'], task['stack_high_water_free_bytes']
                self.stack_minima[name] = min(self.stack_minima.get(name, free), free)
        elif kind == 'http':
            self.http_requests += row.get('request_count', 1)
            self.maximum_http_seconds = max(self.maximum_http_seconds, row['guest_seconds'])
        else:
            self.outages += 1

    def summary(self):
        """Keep summary writes bounded even when the append-only journal spans days."""
        return {'events': self.events, 'snapshots': self.snapshots, 'http_requests': self.http_requests,
                'outages': self.outages, 'minimum_sampled_free_heap_bytes': self.minimum_free,
                'minimum_sdk_sum_of_per_heap_minima_bytes': self.minimum_sdk,
                'minimum_task_stack_fill_bytes_by_name': dict(self.stack_minima),
                'maximum_http_or_batch_guest_seconds': self.maximum_http_seconds,
                'first_snapshot': deepcopy(self.first), 'snapshot_tail': list(self.tail)}

    def close(self):
        """Flush the complete event stream before its final digest is recorded."""
        self.stream.close()
