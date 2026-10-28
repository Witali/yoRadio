"""Independent models of selected predicate, timestamp and TX-completion bodies."""
from dataclasses import dataclass

from timer_event11_model import State

MASK64 = (1 << 64) - 1


@dataclass(frozen=True)
class KeepState(State):
    """Keep field names neutral until their complete SDK meaning is established."""
    last88: int = 0
    last480: int = 0
    byte26: int = 0
    byte9: int = 0
    byte21: int = 0
    byte22: int = 0


def expected(variant, name, state, now, success=0, argument2=0, idle=1, check=0, coex=1,
             argument1=0, station=2, peerflag=0):
    """Model exact observable calls/stores, including RV32/RV64 wrap boundaries."""
    calls, writes, clocks = [], [], 0
    def clock():
        """Return the controlled 64-bit clock sequence and record each backend call."""
        nonlocal clocks
        value = (now + clocks * 17) & MASK64; clocks += 1
        calls.append(['clock', value]); return value
    def stamp(offset, value):
        """Model the two separate RV32 stores of one timestamp."""
        writes.extend([[offset,4,value & 0xffffffff], [offset+4,4,value >> 32]])
    def reset():
        """Describe the old reset body without stubbing its clock/state logic."""
        if state.byte14:
            stamp(88, clock())
            if not state.word36:
                calls.append(['osi400'])
                if not coex: calls.append(['active'])
    def rearm():
        """Describe each SDK's real rearm boundary with its own units and gating."""
        if variant == 'factory':
            if state.enabled52 and not state.word36:
                calls.extend([['disarm'], ['arm224', state.period72 << 9, 0]])
        else:
            delay = (((state.period72 << 10) * 1000 - state.adjustment56) & 0xffffffff
                     if state.enabled52 else state.fallback28)
            if state.enabled52 or delay: calls.extend([['disarm'], ['arm240', delay, 0]])
    if name == 'pm_keep_alive':
        assert variant == 'factory'
        due = False
        if state.word36:
            current = clock()
            if state.enabled52:
                # The factory code sign-extends the wrapped 32-bit product.
                # Record this behavior; it is not a requirement to reproduce overflow.
                threshold = ((state.period72 << 9) * 1000) & 0xffffffff
                if threshold & 0x80000000: threshold |= 0xffffffff00000000
                previous = state.last480
            else:
                threshold, previous = state.fallback28, state.last88
            due = ((current - previous) & MASK64) >= threshold
        return dict(calls=calls, writes=writes, return_value=int(due))
    if name == 'pm_reset_keep_alive':
        assert variant == 'factory'; reset()
        return dict(calls=calls, writes=writes)
    if name == 'pm_tx_null_data_done_process':
        # Deliberate branch family: completed frame, existing PM link, no dream
        # or retry path, byte22 activity. Other branches are reported untested.
        assert (success,argument1,state.byte1,state.byte14,state.byte15,state.byte16,
                state.byte9,state.byte21,state.byte22) == (0,1,0,1,1,0,0,0,1)
        if variant == 'factory': reset()
        calls.append(['check'])
        assert check == 1
        if state.byte488:
            if variant == 'factory':
                if state.enabled52:
                    if state.word36: stamp(480,clock())
                    else: rearm()
                    writes.append([488,1,0])
            else:
                if station == 0:
                    calls.append(['log',1,8,4]); return dict(calls=calls,writes=writes)
                if station == 2 and (not peerflag or argument2):
                    rearm(); stamp(480,clock()); writes.append([488,1,0])
                    calls.append(['log',6,4096,4])
        writes.append([9,1,0])
        return dict(calls=calls,writes=writes)
    assert name == 'pm_tx_data_done_process'
    if success:
        if variant == 'factory': reset()
        calls.append(['beacon-reset'])
        if argument2:
            if variant == 'factory':
                if state.enabled52:
                    rearm(); stamp(480, clock())
            else:
                elapsed = (clock() - state.last480) & MASK64
                if elapsed > 100000:
                    rearm(); stamp(480, clock())
    calls.append(['tx-idle', 1])
    if not idle:
        if not state.byte14: calls.append(['disconnected-delay'])
        elif state.byte1 == 1: calls.append(['sleep-delay'])
    calls.append(['check'])
    if check and argument2:
        calls.append(['coex-increment'])
        if not state.byte26: writes.append([27,1,1])
        if not state.byte1: calls.append(['active'])
    return dict(calls=calls, writes=writes)
