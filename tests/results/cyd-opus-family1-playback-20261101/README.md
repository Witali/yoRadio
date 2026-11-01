# Unselected public family1 playback adapter: HOST checkpoint

The new adapter in `main/opus_family1_playback.h` uses the caller's existing,
CRC-verified page owner. It starts audio only after the committed OpusTags
completion event, then uses the anchored public raw-handle owner. It stages
only unique mapped decoded channels, aliases duplicates and emits silence for
mapping 255. It gathers at most 128 frames of all logical channels in Vorbis
speaker order, trims exactly once and forwards header gain as metadata.

This checkpoint is **not production-ready or full format qualification**.
The existing timeline checks only the OpusTags prefix, minimum size and page
boundaries. Vendor/comment lengths, counts and declared UTF-8 require a bounded
streaming validator before selecting this raw path. No stock Ogg parser remains
to supply those checks in the new path. Arbitrary binary tails are legal; the
audio packet limit must not become a blanket Tags limit. See
[RFC 7845 section 5.2](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.2).
Container live joins, concurrent serials, further codec modes, formal numeric
conformance, native resources and actual radio-task integration remain separate
gates. No existing production source is edited by this checkpoint.

The final GCC ASan/UBSan/leak run is capture 04, with 33 positive schedules,
25 explicitly HOST contract/refusal controls, 60 creator libogg walks,
1170 actual page ACKs and 3898624 exact mapped/trimmed creator PCM samples.
It covers default 3/6/8 mappings, C1–8 selected duplicate/silent/unused maps,
whole/grouped/continued/nil pages, 70000-byte valid Tags, compatible ID extension,
three sequential links and an empty link. These selected maps do not exhaust
all arbitrary mappings. All 92 original 120 ms audio packet bodies also run in
both consumed-all/cache and unconsumed output-resize models. The separate
20/120/20 ms zero-coded-frame PLC geometry controls reach 92160-byte unique
planes and 23040-byte scratch; they are not active-signal qualification of that
peak geometry. The largest full logical-C output chunk is 2048 bytes.

EOS closes every real creator-backed handle before the actual page ACK.
A scripted HOST close refusal preserves the held EOS page/token, packet
storage, planes and stable config address. An explicit retry closes the
remaining handle and ACKs without decoding or publishing the PCM again.
A separate abandon/Stop refusal preserves a held nil page and 255-byte partial
packet until cleanup succeeds. Blocked results continue to report real pending
handle ownership. Open/decode refusal ordinals, plane/scratch/prefix allocation
refusal, cancelled sends, cancellation during open/decode, moved-owner refusal
and malformed unused-stream duration controls leave no live creator objects or
tracked storage. Refused public statuses are labelled HOST test doubles, with
no creator call at the refused open/decode ordinal. This is no native ESP OOM
or formal codec conformance claim.

Capture 01 preserves the real sandbox WSL launch DWORD 4294967295. Capture 02
preserves the initial test-source indentation diagnostics under `-Werror`.
Capture 03 is the genuine initial 33/25 PASS. Capture 04 additionally verifies
that subsequent blocked calls retain the actual pending-handle witness.
No earlier capture is rewritten. Executables, encoded transport/Ogg and PCM
payloads are excluded from publication and retained locally by hash/size.

Run `python -B tests/results/cyd-opus-family1-playback-20261101/verify.py --require-current`
to verify current checkpoint bindings. Without that flag,
the verifier validates the immutable historical source closure, allowing the
new adapter to acquire its separately tested Tags validator later. It reads
only data evidence, executes no captured code and reads no omitted payload.
