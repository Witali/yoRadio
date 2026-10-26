"""Independent observable-effect model of the two complete TIM handlers."""
from dataclasses import dataclass

from keep_alive_model import KeepState, MASK64

MASK32 = (1 << 32) - 1


@dataclass(frozen=True)
class TimState(KeepState):
    """Use byte offsets where the complete protocol meaning remains unproven."""
    byte20: int = 0
    byte27: int = 0
    byte468: int = 0
    window60: int = 1000
    deadline112: int = 0
    counter8: int = 0
    counter12: int = 0


def expected(variant, state, now, argument0=0, argument1=0, slice_allowed=1):
    """Model PM writes, wrapping counters and ordered external boundary calls."""
    calls, writes, counters, clocks = [], [], [], 0

    def clock():
        """Return the explicitly controlled RV32 a0/a1 clock sequence."""
        nonlocal clocks
        value = (now + 17 * clocks) & MASK64
        clocks += 1
        calls.append(['clock', value])
        return value

    due = False
    if variant == 'factory' and state.word36:
        current = clock()
        if state.enabled52:
            threshold = ((state.period72 << 9) * 1000) & MASK32
            if threshold & (1 << 31): threshold |= MASK32 << 32
            previous = state.last480
        else:
            threshold, previous = state.fallback28, state.last88
        due = ((current - previous) & MASK64) >= threshold

    def request_null(argument):
        """Record the old TIM request, without claiming actual RF transmission."""
        if state.enabled52: writes.append([488, 1, 1])
        calls.append(['null', argument])

    if state.byte1 == 1:
        if argument0 or argument1:
            current = clock()
            calls.append(['slice', current & MASK32, current >> 32, 5000 if argument0 else 1000])
            if not slice_allowed:
                if argument0: writes.append([27, 1, 1])
            else:
                writes.append([20, 1, 1])
                if not argument0: calls.append(['dream-timer'])
                if current < state.deadline112:
                    delay = (state.deadline112 - current) & MASK64
                    # The argument0 path intentionally passes just the low word;
                    # the other path caps the full-width difference at window60.
                    delay = delay & MASK32 if argument0 else min(delay, state.window60)
                    calls.append(['coex408', 1 if argument0 else 2, 0, delay])
                if argument0:
                    calls.append(['wake', 1, 0])
                    counters.append([8, 4, (state.counter8 + 1) & MASK32])
                else:
                    if variant == 'factory' and not state.byte21 and not state.byte22 and due:
                        request_null(1)
                    counters.append([12, 4, (state.counter12 + 1) & MASK32])
        else:
            writes.append([20, 1, 0])
            if not state.byte21 and not state.byte22:
                calls.append(['disable-sleep-delay'])
                if variant == 'factory' and due: request_null(1)
                else: calls.append(['sleep'])
    elif not state.byte1 and not argument0 and not argument1:
        writes.append([20, 1, 0])
        if state.byte468: calls.extend([['disable-active'], ['active-timeout', 0]])
        if variant == 'factory' and due: request_null(0)
    return dict(calls=calls, writes=writes, counter_writes=counters)
