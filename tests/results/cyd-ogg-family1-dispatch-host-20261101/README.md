# Integrated Ogg family1 dispatch: creator-backed HOST gate

The current `ogg_playback.h` passes 43 positive schedules and 12 explicitly
labelled HOST controls under GCC ASan/UBSan/leak checks, with 12983296 exact
creator PCM samples, 20052 family1-layout chunks and 552 legacy chunks. Real
creator raw handles are supplied by the immutable lower-component harness,
included under a renamed main with its stable owner bound to `wrapper.family1`.
The simple legacy branch uses creator libogg and real public Opus synthesis;
its HOST state is owned by the test, not an invented vendor ABI structure.

The finite corpus covers default 3/6/8 and selected C1–8 duplicate/silent/unused
maps, whole/grouped/continued/nil pages, both full stereo 120 ms buffer-cache
models and active C8 120/100 ms packets. Signed gain extremes and explicit
Vorbis speaker-layout forwarding are checked without applying gain to PCM.
Both family1→family0→family1 and family0→family1→family0 orders pass in whole
and split feeds. A previously prepared simple handle/output is retired before
family1 raw synthesis starts. These tests do not claim every arbitrary map,
Vorbis synthesis, full RTOS/application execution or native ESP OOM qualification.

Scripted HOST close refusal keeps a real creator object alive and its config
address, held EOS page/token, prefix and planes unchanged. Yield/retry closes
it without repeated synthesis/output. Cancellation and missing-yield paths
retain ownership; a refused reset preserves generation and input bytes until
a later real creator close succeeds. Partial output/cancellation, malformed
Tags and CRC, missing layout callback, open refusal and normal allocator seams
also pass with no live objects/storage after cleanup. The refused statuses are
test doubles; no creator open/close is called at the refused ordinal. This is
not a native fault-injection or vendor-allocation observation.

The active C8 stress is made by actual libopus 1.4 public repacketization:
all 55 cat calls succeed, stable TOC configurations form six- and five-frame
groups, and every original coded frame stays byte-identical and ordered.
Preskip 312, logical 9600 and raw 10560 frames remain unchanged. Independent
creator multistream float output before/after is exactly equal; no tolerance or
re-encode is introduced. The resulting transport is 15447 bytes, SHA256
`c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757`.

Both legacy wrapper regressions also pass: 108 lifecycle/allocation cases and
136 gain-metadata cases. Their runners now freeze actual pinned public vendor
headers and all consumed raw/Tags/shared owners; the former stub header is not
selected. An explicit unselected-raw seam aborts if accidentally reached. The
only existing C harness adaptation is the established fifth `int16_t` callback
parameter plus a zero-gain assertion; prior assertions/goldens and the gain
harness are unchanged. Historical captures are not rewritten.

Integrated capture 01 preserves an initial new-harness indentation diagnostic
under `-Werror`. Fresh capture 02 fixes that statement layout and passes with
unchanged production bytes. The saved data verifier checks exact process/source
identities and case records; it does not recompute PCM without omitted payloads.

Run `python -B tests/results/cyd-ogg-family1-dispatch-host-20261101/verify.py --require-current`.
It executes no captured/native code and reads no omitted executable, encoded or
PCM payload. Actual task, output queue and hardware resources remain later gates.
