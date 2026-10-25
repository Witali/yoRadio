"""Independent, offset-named reference models of the two event-11 algorithms.

These describe the selected code bodies, not the meaning or reachability of
every synthetic SDK state. Timer/RF helpers are explicit external boundaries.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    """Only input fields actually read by either qualified algorithm."""
    byte1: int = 0
    byte14: int = 1
    byte15: int = 1
    byte16: int = 0
    byte488: int = 0
    word36: int = 0
    enabled52: int = 1
    period72: int = 10
    fallback28: int = 0
    adjustment56: int = 0


def expected(variant, state):
    """Return observable calls and PM writes, preserving RV32 arithmetic wrap."""
    calls, writes = [], []
    if variant == 'factory':
        if state.enabled52 and not state.word36:
            calls.extend([['disarm'], ['arm224', state.period72 << 9, 0]])
    elif variant == 'native':
        if state.enabled52:
            delay = ((state.period72 << 10) * 1000 - state.adjustment56) & 0xffffffff
        else:
            delay = state.fallback28
        if state.enabled52 or delay:
            calls.extend([['disarm'], ['arm240', delay, 0]])
        if not state.byte15:
            return dict(calls=calls, writes=[[288, 1, 1], [488, 1, 1], [576, 1, 1]], return_value=1)
    else:
        raise ValueError('Unknown SDK version')
    active = state.byte14 and state.byte15 and not state.byte16
    if active and (variant == 'factory' or not state.byte488):
        writes.append([488, 1, 1])
        if not state.word36:
            calls.append(['wake', 0, 0])
        else:
            if state.byte1:
                calls.append(['dream'])
            calls.append(['null', int(bool(state.byte1))])
        if variant == 'native':
            calls.append(['log', 6, 4096, 4])
    return dict(calls=calls, writes=writes, return_value=1)


def configured(variant, state, period):
    """Model the actual setter's representation before comparing timer periods."""
    assert 0 <= period <= 65535
    writes, calls = [], []
    if variant == 'factory':
        if period:
            encoded = period if period <= 4 else max(period, 2 * (period - 4)) & 65535
            writes = [[52, 1, 1], [72, 2, encoded]]
            if not state.word36:
                calls = [['disarm'], ['arm224', encoded << 9, 0]]
            state = replace(state, enabled52=1, period72=encoded)
        else:
            writes = [[52, 1, 0]]
            calls = [['disable']]
            state = replace(state, enabled52=0)
    elif variant == 'native':
        if period:
            adjustment = 500000 if period <= 3 else 2000000
            writes = [[52, 1, 1], [72, 2, period], [56, 4, adjustment]]
            state = replace(state, enabled52=1, period72=period, adjustment56=adjustment)
        else:
            writes = [[52, 1, 0]]
            state = replace(state, enabled52=0)
    else:
        raise ValueError('Unknown SDK version')
    return state, dict(calls=calls, writes=[], cfg_writes=writes)
