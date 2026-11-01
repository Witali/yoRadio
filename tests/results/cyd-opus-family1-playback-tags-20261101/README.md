# Public family1 adapter: streamed Tags and scratch reuse

This successor integrates the separately qualified `opus_tags_stream.h` into
the new, still unselected `opus_family1_playback.h`. It validates completed
comment fields/text before opening public raw handles. Invalid Tags retain the
actual held page and unchanged parser state. No existing `ogg_playback.h`,
`audio_service.c` or physical output source is edited here.

After all needed raw PCM has been copied into unique mapped-channel planes,
the bounded full logical-C gather reuses the owned raw scratch. The synchronous
output callback must consume/copy it before returning; no next decode or close
occurs during that lease. All-silent maps use immutable static zero storage.
The callback asserts actual scratch or zero-buffer identity, preserving all
prior close-pending, cancellation and partial-send ownership checks.

Actual HOST layout compilation measures the adapter at 2768 bytes before and
776 bytes after: 2048 embedded bytes removed and 56 bytes of streamed Tags state
added. Public raw owner (304 bytes) and packet owner (128 bytes) are unchanged.
The actual read-only zero symbol is 2048 bytes in the consuming HOST binary.
These are HOST layout/storage measurements, not a target task-stack result.
No task allocation is enlarged. Real production resources remain unmeasured.

The fresh GCC ASan/UBSan/leak capture 06 passes 34 positive schedules and 27
labelled HOST contract controls, 63 creator libogg walks, 1213 actual page ACKs
and 3975424 exact mapped/trimmed creator PCM samples. All 92 original 120 ms
packet bodies remain present in both public output-cache models. Default
3/6/8 mappings, selected C1–8 duplicate/silent/unused maps, grouped/continued/nil
pages, large Tags, ID extension, sequential chains, empty links and the prior
EOS/abandon close refusals remain covered. Added cross-page UTF-8 success and
malformed UTF-8/length refusals occur before any public open. The separate PLC
growth cases measure the 92160-byte plane peak; they do not establish active
audio behavior for every maximum-size mapping. Header gain stays metadata only.

Capture 05 preserves a genuine linker refusal: the layout helper's output name
collided with its source directory. Capture 06 changes that output filename and
completes the gate. The original adapter checkpoint 04 remains immutable in
`cyd-opus-family1-playback-20261101`; its default verifier still passes.
This is no native OOM, formal numeric conformance or full-format qualification.
Actual-task playback, hardware resources and remaining container gates are
still required before production selection.

Run `python -B tests/verify-opus-tags-playback-host.py --checkpoint playback --require-current`.
The verifier checks only data evidence. Executable, encoded and PCM payloads
remain local by hash and size and are not read by it.
