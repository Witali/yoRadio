"""Decode CRC-protected TCP probe v2 frames and reject incomplete trace windows."""
import math
import re
import zlib

KINDS = {'C': 'event', 'L': 'listener', 'S': 'watermark'}
MAX_WATERMARK_GAP_SECONDS = 2.5
COUNTER_MASK = (1 << 32) - 1


def parse(row):
    line = row['line']
    if not any('PERF T'+kind+'2' in line for kind in KINDS):
        return None
    match = re.fullmatch(r'PERF T([CLS])2:([0-9a-f]{48})', line)
    if not match:
        raise ValueError('Malformed or merged TCP v2 frame')
    if zlib.crc32(line[:49].encode('ascii')) != int(line[49:], 16):
        raise ValueError('TCP v2 CRC mismatch')
    at = float(row['at'])
    if not math.isfinite(at):
        raise ValueError('Invalid TCP capture time')
    words = [int(match[2][i:i+8], 16) for i in range(0, 40, 8)]
    a, b, c, d, e = words
    result = dict(at=at, kind=KINDS[match[1]])
    if match[1] == 'C':
        error = (d >> 16) & 255
        result.update(seq=a, us=b, port=c & 65535, dir=(c >> 16) & 255,
                      flags=c >> 24, before=d & 255, after=(d >> 8) & 255,
                      result=error if error < 128 else error-256, pending=d >> 24, dropped=e)
        if result['dir'] not in (0, 1):
            raise ValueError('Invalid TCP direction')
    elif match[1] == 'L':
        result.update(seq=a, age_ms=b, syn_rcvd=c & 65535, established=c >> 16,
                      listeners=d & 255, backlog=(d >> 8) & 255,
                      pending=(d >> 16) & 255, backlog_supported=d >> 24)
        if e or result['backlog_supported'] not in (0, 1):
            raise ValueError('Invalid TCP listener frame')
    else:
        result.update(generated=a, us=b, dropped=c, queued=d, emitted=e)
        if d > 64 or (a-e) & COUNTER_MASK != d:
            raise ValueError('Inconsistent TCP watermark')
    return result


def window(rows, start, end):
    """Qualify between complete periodic anchors, explicitly report edge gaps.

    Frames outside the requested observation remain available to the caller.
    No repair/resynchronization is attempted inside the qualified interval.
    """
    if not math.isfinite(start) or not math.isfinite(end) or start >= end:
        raise ValueError('Invalid TCP observation window')
    frames = [value for row in rows if start <= row['at'] <= end
              and (value := parse(row)) is not None]
    marks = [f for f in frames if f['kind'] == 'watermark']
    if len(marks) < 2:
        raise ValueError('Need two TCP watermarks')
    times = [start] + [f['at'] for f in marks] + [end]
    if any(b < a or b-a > MAX_WATERMARK_GAP_SECONDS for a, b in zip(times, times[1:])):
        raise ValueError('Incomplete TCP watermark coverage')
    begin, finish = frames.index(marks[0]), frames.index(marks[-1])
    last = marks[0]['emitted']
    events, listeners = [], []
    for frame in frames[begin:finish+1]:
        if frame.get('dropped', 0):
            raise ValueError('TCP ring dropped events')
        if frame['kind'] == 'event':
            if frame['seq'] != (last+1) & COUNTER_MASK:
                raise ValueError('Missing or duplicate TCP event')
            last = frame['seq']
            events.append(frame)
        elif frame['kind'] == 'watermark':
            if frame['emitted'] != last:
                raise ValueError('TCP watermark exposes missing events')
        else:
            if listeners and frame['seq'] != (listeners[-1]['seq']+1) & COUNTER_MASK:
                raise ValueError('Missing or duplicate listener sample')
            listeners.append(frame)
    if not listeners:
        raise ValueError('Missing listener snapshots')
    listener_times = [marks[0]['at']] + [f['at'] for f in listeners] + [marks[-1]['at']]
    if any(b-a > MAX_WATERMARK_GAP_SECONDS for a, b in zip(listener_times, listener_times[1:])):
        raise ValueError('Incomplete listener coverage')
    return dict(start=marks[0]['at'], end=marks[-1]['at'],
                first_edge_seconds=marks[0]['at']-start, last_edge_seconds=end-marks[-1]['at'],
                events=events, listeners=listeners, watermarks=marks)
