"""Read passive serial telemetry in chunks and preserve lines across timeouts."""


def serial_lines(port, closed):
    pending = bytearray()
    while not closed.is_set():
        try:
            data = port.read(min(4096, port.in_waiting or 1))
        except OSError:
            yield 'serial capture interrupted'
            return
        pending.extend(data)
        while b'\n' in pending:
            line, _, rest = pending.partition(b'\n')
            pending = rest
            yield line.decode('utf-8', errors='replace').strip()
        if len(pending) > 65536:
            # Do not retain unbounded/no-newline output or expose its contents.
            yield 'serial capture interrupted: overlong line'
            return
    if pending:
        yield 'serial capture interrupted: incomplete final line'
