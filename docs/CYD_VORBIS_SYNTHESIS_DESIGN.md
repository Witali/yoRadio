# Stateful exact synthesis after the reused inverse transform

The [API](../idf/components/native_vorbis_synthesis/include/native_vorbis_synthesis.h)
connects the existing timing and exact window/PCM components to all channels
of each unwindowed IMDCT block. The input is still an approximate binary64
transform with an independently retained scale. Complete window products and
their sum remain exact dyadics until one nearest-even S16 rounding/clamp.
This prevents new window/scale-alignment loss; it cannot recover preceding
gain/transform approximation or replace the unfinished wider routes.

## Half-history and whole-frame publication

For adjacent sizes A and B, let M=min(A,B), P=(A-M)/4 and Q=(B-M)/4. The ready
interval contains (A+B)/4 frames. At ready coordinate t<P, only the previous
unity plateau contributes. For P<=t<P+M/2, multiply history[t] by the reversed
M rising table and current[Q+t-P] by the forward table. Thereafter only the
current unity plateau contributes. Previous indices are confined to its
cached right half; current indices are confined to its left half.

History has fixed `long_size/2` stride per channel. The active size comes from
the shared timing state; unused tails stay untouched. Base exponents are kept
per channel and never aligned or subtracted. The first block caches its right
halves and emits nothing. There is no terminal zero packet to flush history.
Output at `frame*channels+channel` preserves the original channel order.

All descriptor, coefficient, capacity, source, history and timing checks finish
before output begins. Every current channel's complete source block is finite;
all previously active half-histories are checked, even when trimming discards
the whole ready interval. Priming/reset never read uninitialized history/base
elements. Prepared-window factors are checked by their binary64 bits, including
signaling nonfinite patterns, with no floating multiplication/classification.

Publication uses only checked immutable data and existing exact scalar APIs.
Every output channel is finished before any history is overwritten. Then all
current right halves and independent bases replace active history, and shared
timing/result are published last. Every returned failure preserves actual bytes
of all state/storage/output/result objects and permits retry. Read-only source
channels may share arrays; every writable destination/state is disjoint from
the descriptors, lookups and source borrows. Caller use is serialized.

## Timing and lifetime

The existing public timing component computes the contiguous subspan to emit.
Only that subspan is converted; all current right halves are still cached.
First-known anchors may trim the front; final EOS may trim the tail; late
anchors cannot retract previously emitted data. The metadata counter cap
retains all bounded trim decisions and is not an accepted-format limit.

A discontinuity follows Xiph's metadata policy and retains numeric overlap.
Hard reset is a separate operation that primes again, leaves old storage bytes
untouched and resets timing. EOS remains sticky bookkeeping; the transport or
logical-stream owner decides when a link terminates or a new setup begins.

Current IMDCT blocks must stay alive/immutable through push. They can be reused
after it returns because right halves are copied. Setup/frame and transform
scratch lifetimes remain the responsibility of their producers. The public
owner allocates nothing and introduces no task, lock, sample-rate conversion,
production selection or change to the CYD core0 stream/core1 audio bindings.

## Memory and verification scope

For C channels and largest block L, history costs `8*C*L/2` bytes and bases
`8*C` bytes; maximum interleaved output costs `2*C*L/2` bytes. These exclude
current transforms, lookups, packet/setup workspace, network, TLS and task
stacks. Requirements accept the whole legal64..8192/1..255 domain; the caller
must handle unavailable resources without turning them into new format caps.

The complete original31 corpus uses stereo, short64/256 and long256/2048.
Its raw identification/setup/audio bytes total7376; including comments gives
9174. Those sizes make full-corpus isolated MCU qualification practical; they
do not prove memory availability for8192 blocks,255 channels or the real radio.
The [qualification checkpoint](../tests/results/vorbis-synthesis-20261028/CHECKPOINT.md)
passes all31 streams/434 packets/738560 PCM bytes against both saved references
on host, with maximum absolute S16 error2 at the unchanged bound2 and all14
relations. Actual SDK/QEMU runs on ESP32/core1 and C3/core0 produce exactly the
same complete PCM bytes. The native parser directly checks the original
FFmpeg/libvorbis references; byte equality to the doubly checked host output
also binds it to the saved Xiph comparison. No captured gain, spectrum, IMDCT
or PCM is used as decoder input.

Host owner tests additionally cover all864 retained overlap rows, all20019
timing actions and every channel count1..255. Failures on late channels leave
the complete state/history/output bytes unchanged; all50 failure/retry controls
pass. ASan/UBSan is clean. Source-only C/C++ GCC profiles pass both ISAs, with
zero Clang warnings/errors in this owner. The shared helper/host fixture retains
17 reviewed warnings and no errors without new suppression.

Native workers retain a16384-byte stack and enabled watchdog/idle checks.
Observed minimum free worker stack is10876 bytes on ESP32 and11048 on C3.
The helper's tracked peak payload is128970 bytes on each target, with zero
remaining allocations after every stream. These are isolated fixture results;
they exclude production radio/TLS allocations and physical real-time behavior.

The corpus gate is now closed for this candidate. Universal floor0 gain error
certification, wider/precision routes, raw/Ogg/audio-task integration, target
resources beyond this stereo/2048 corpus and physical acceptance remain open.
Comments are retained but not consumed by the setup API; its raw input is the
identification/setup/audio data. No production decoder selection has changed.
