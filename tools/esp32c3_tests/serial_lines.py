"""Read passive serial telemetry in chunks and preserve lines across timeouts."""
import time

FINAL_LINE_GRACE_SECONDS = 0.5


def serial_lines(port, closed):
    pending = bytearray()
    close_deadline = None
    while True:
        closing = closed.is_set()
        if closing:
            if not pending:
                return
            if close_deadline is None:
                close_deadline = time.perf_counter() + FINAL_LINE_GRACE_SECONDS
            if time.perf_counter() >= close_deadline:
                yield 'serial capture interrupted: incomplete final line'
                return
        try:
            # Finish only the current line on requested shutdown. Single-byte
            # reads stop at its newline without starting another partial line.
            # A missing newline still fails closed after the bounded grace.
            data = port.read(1 if closing else min(4096, port.in_waiting or 1))
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
