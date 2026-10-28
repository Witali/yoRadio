"""Preserve bounded read-only failure metadata before the VM owner cleans up."""
import hashlib
import json
import time

from runtime_memory import LISTS, MemorySnapshot


class DeadlineStream:
    """Bound the existing QMP stream, including events and partial JSON lines."""
    def __init__(self, stream, sock, deadline):
        self.stream, self.socket, self.deadline, self.bytes = stream, sock, deadline, 0

    def limit(self):
        """Apply the remaining shared budget before each potentially blocking I/O."""
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Failure QMP diagnostic deadline expired')
        self.socket.settimeout(remaining)

    def write(self, data):
        """Send only the literal read-only query supplied by the capture owner."""
        self.limit()
        return self.stream.write(data)

    def flush(self):
        """Do not let buffered query transmission outlive its diagnostic."""
        self.limit()
        self.stream.flush()

    def readline(self):
        """Limit total JSON response bytes even if unrelated QMP events arrive."""
        data = bytearray()
        while True:
            self.limit()
            part = self.stream.read(1)
            if not part:
                raise ConnectionError('Failure QMP stream closed')
            data += part; self.bytes += 1
            if self.bytes > 65536:
                raise ValueError('Oversized failure QMP response')
            if part == b'\n':
                return bytes(data)


def qmp_read(qmp, deadline, command, **arguments):
    """Reuse the sole owned QMP connection; restore its stream even on failure."""
    if command not in ('query-status', 'human-monitor-command') or command == 'human-monitor-command' and arguments != {'command-line': 'info usernet'}:
        raise ValueError('Failure capture only permits status and usernet inspection')
    stream, timeout = qmp.file, qmp.sock.gettimeout()
    qmp.file = DeadlineStream(stream, qmp.sock, deadline)
    try:
        result = qmp.execute(command, **arguments)
        # A large socket inventory must not crowd the essential CPU/photo
        # observations out of the bounded final artifact.
        if command == 'human-monitor-command' and (not isinstance(result, str) or
                len(json.dumps(result).encode()) > 16384):
            raise ValueError('Oversized failure usernet metadata')
        return result
    finally:
        qmp.file = stream
        qmp.sock.settimeout(timeout)


class FailureCapture:
    """Capture the actual stop without advancing to a convenient SDK entry point."""
    def __init__(self, observer, qmp, layout, photo_layout, folder, result, session, seconds=5):
        self.observer, self.qmp, self.layout, self.photo = observer, qmp, layout, photo_layout
        self.folder, self.result, self.session, self.seconds = folder, result, session, seconds
        self.operation = {'kind': 'startup'}

    def __enter__(self):
        """Normal workloads incur no extra guest stop or diagnostic I/O."""
        return self

    def __exit__(self, kind, error, traceback):
        """Keep the original exception and cleanup path even if diagnostics fail."""
        if kind is None or not issubclass(kind, Exception):
            return False
        try:
            record = self.capture(kind.__name__)
            raw = (json.dumps(record, sort_keys=True, indent=2) + '\n').encode()
            if len(raw) > 65536:
                raise ValueError('Oversized failure-state metadata')
            path = self.folder / 'failure-state.json'
            with path.open('xb') as stream:
                stream.write(raw)
            self.result['failure_capture'] = dict(file=path.name, sha256=hashlib.sha256(raw).hexdigest(),
                                                  status=record['status'], bytes=len(raw))
        except Exception as failure:
            self.result['failure_capture'] = dict(status='unavailable', error_type=type(failure).__name__)
        return False

    def capture(self, error_type):
        """Read typed scalar/control metadata only; never export payload or stack bytes."""
        started = time.monotonic(); deadline = started + self.seconds
        record = dict(schema='small-tv-failure-state-v1', status='partial', error_type=error_type,
                      operation=dict(self.operation), vm_name=self.session['name'],
                      app_sha256=self.result['app_sha256'], elf_sha256=self.result['native_elf_sha256'],
                      qemu_sha256=self.result['qemu_sha256'], completed_cycles=self.result['completed_cycles'],
                      memory_read_limit=32768, memory_call_limit=192, diagnostic_seconds_limit=self.seconds,
                      errors={}, scope='Arbitrary failure stop; no stable heap/TCP or H10 acceptance.',
                      no_guest_memory_or_register_writes=True, no_guest_functions_called=True)
        cache, reads = {}, [0, 0]

        def step(name, action):
            """Retain independent partial observations without hiding the failure."""
            try:
                record[name] = action()
                return record[name]
            except Exception as error:
                record['errors'][name] = type(error).__name__
                return None

        def read(address, size):
            """Cap actual target reads and reuse immutable bytes from the stopped VM."""
            key = address, size
            if key not in cache:
                if time.monotonic() >= deadline or reads[0] >= 192 or reads[1] + size > 32768:
                    raise TimeoutError('Failure metadata read budget exhausted')
                reads[0] += 1; reads[1] += size
                cache[key] = self.observer.memory(address, size)
            return cache[key]

        reader = MemorySnapshot(read, self.layout)
        with self.observer.time_limit(self.seconds):
            status = step('qmp_status_before_stop', lambda: qmp_read(self.qmp, min(deadline, time.monotonic() + .5), 'query-status'))
            stopped = bool(status and status.get('running') is False)
            if not stopped:
                step('rsp_interrupt', self.observer.interrupt)
                stopped = 'rsp_interrupt' in record
            record['target_stopped'] = stopped
            if stopped:
                step('registers', lambda: {name: self.observer.register(number) for name, number in (('pc', 32), ('sp', 2), ('ra', 1))})
                step('station_connected_byte', lambda: reader.memory(self.layout['symbols']['connected']['address'], 1)[0])
                step('photo', lambda: self.photo_state(reader))
                step('heap', reader.heaps)
                step('tasks', lambda: self.tasks(reader))
                if not record['errors'].get('qmp_status_before_stop'):
                    step('usernet', lambda: qmp_read(self.qmp, deadline, 'human-monitor-command', **{'command-line': 'info usernet'}))
        record['memory_reads'], record['memory_requested_bytes'] = reads
        record['elapsed_host_seconds'] = time.monotonic() - started
        record['status'] = 'captured' if not record['errors'] else 'partial'
        return record

    def tasks(self, reader):
        """Read TCB metadata and list membership without scanning used stack memory."""
        pointers, lists = set(), {}
        size = self.layout['structures']['xLIST']['size']
        for name in LISTS:
            symbol = self.layout['symbols'][name]
            if symbol['size'] % size:
                raise ValueError('Invalid diagnostic task-list extent')
            for offset in range(0, symbol['size'], size):
                owners = reader.task_list(symbol['address'] + offset)
                lists[name + ':' + str(offset // size)] = owners
                pointers.update(owners)
                if len(pointers) > 64:
                    raise ValueError('Too many diagnostic task owners')
        current = reader.symbol('pxCurrentTCBs'); pointers.add(current)
        rows = []
        for pointer in sorted(pointers):
            task = reader.structure('tskTaskControlBlock', pointer)
            fields = {name: reader.number('tskTaskControlBlock', task, name) for name in ('pxStack', 'pxEndOfStack', 'pxTopOfStack')}
            rows.append(dict(address=pointer, name=reader.field('tskTaskControlBlock', task, 'pcTaskName').split(b'\0')[0].decode('utf-8', errors='replace'), **fields))
        return dict(current_tcb=current, declared_tasks=reader.symbol('uxCurrentNumberOfTasks'), lists=lists, rows=rows)

    def photo_state(self, reader):
        """Decode only selected worker/upload and queue counters from native DWARF."""
        def scalar(row, base=0):
            address = row.get('address', base + row.get('offset', 0))
            return int.from_bytes(reader.memory(address, row['size']), 'little', signed=row['signed'])

        worker = {name: scalar(row) for name, row in self.photo['worker'].items()}
        upload = {name: scalar(row) for name, row in self.photo['upload'].items()}
        queues = {}
        for name in ('jobs', 'codec_mutex', 'media_mutex'):
            pointer = worker[name]
            fields = {key: scalar(row, pointer) for key, row in self.photo['queue'].items()
                      if pointer and (key != 'mutex_holder_tcb' or name != 'jobs')}
            queues[name] = dict(address=pointer, fields=fields)
        return dict(worker=worker, upload=upload, queues=queues)
