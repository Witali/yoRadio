# Windowing the reused Vorbis transform

The public [window API](../idf/components/native_vorbis_window/include/native_vorbis_window.h)
applies the window defined by [Vorbis I sections4.3.1 and4.3.8](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
For each legal size N it prepares N/2 binary64 rising coefficients:

```
rise[i] = sin((pi/2) * sin((pi/N)*(i+.5))^2)
```

The [pinned Xiph implementation](../idf/components/native_vorbis_xiph/upstream/libvorbis/lib/window.c)
uses the same curve, stored as binary32 tables. This adapter constructs it in
binary64, matching the wider transform representation. It keeps the reference
transition geometry. For a current block N and slope sizes P and Q, the rising
half is centered on N/4 and the falling half on3N/4; their lengths are P/2 and
Q/2. Outside support is zero, and the region between slopes is unity. Short
blocks force both slopes short regardless of neighbor flags.

The specification's section4.3.1 step8 appears to name the start of the right
slope as the start of trailing silence. That contradicts the slope written in
the preceding step. The reference implementation zeros from the **end** of
that slope; the adapter follows this internally consistent reference behavior.

Caller storage and immutable plans replace allocation. Size/capacity/descriptor
checks and a complete finite-input scan precede all output writes. Failed
application preserves output and result. Successful application keeps the
source's full signed64 exponent without adding or narrowing it. The plateau
preserves input bits; slopes use one binary64 multiplication; outside support
is canonical positive zero. An input may contain any finite binary64 magnitude,
including DBL_MAX and subnormals. Factors never exceed one, avoiding overflow.
Usual binary64 underflow remains possible and is explicit in the test bound.

Preparing a size8192 lookup uses32768bytes. Application uses separate caller
input/output arrays of N doubles; it introduces no task, heap operation, VLA,
PCM clipping or production selection. These storage requirements are costs,
not a measured CYD memory optimization. Cores and audio backends are unchanged.

The host suite checks every coefficient against a70-digit Decimal sine series,
monotonicity and power complementarity, and every coordinate/output for all36
short<=long configurations and eight current/neighbor flag combinations.
The source sequence is independently reconstructed bit-for-bit, including
signed zeros, DBL_MAX, minimum subnormals and a large exponent span. Every
refusal snapshots input bytes and the actual supplied descriptors immediately,
including intentionally nonfinite values; retry uses unchanged output storage.
Eight damaged captures are rejected by the pure reader. No tolerance or corpus
is reduced after observing results.

This is full-window application, not an overlap decoder. The next stream layer
must prime with the first block, emit (previous_size+current_size)/4 samples,
retain the current unwindowed right half and keep separate exponents until
addition. Xiph infers the slopes from actual adjacent sizes, which section1.3.2
permits. Reset and granule/EOS trimming require their own tests. A zero current
floor must still preserve the preceding block's tail. Do not flush by inventing
a terminal zero packet or erase a small overlap term by prematurely selecting
one common exponent. Arbitrary floor0 finite gains, poles and mapping domains,
full31 PCM/bound2/all14 relations, SDK/runtime and physical acceptance remain
open. See the [qualification record](../tests/results/vorbis-window-20261028/CHECKPOINT.md).
