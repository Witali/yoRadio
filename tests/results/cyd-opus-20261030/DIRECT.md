# Unchanged Espressif Opus: direct LX6 checkpoint

The pinned ESP-IDF 6.0.2 and Espressif archives execute through the public Ogg
interface on ESP32 LX6 QEMU. The first stream supplies the complete borrowed
706,319-byte fixture with data-bearing EOS, without either shared input adapter.
Its actual output establishes the raw vendor integration reference. The next
three streams use the production pending-prefix and one-byte EOF helpers with
4096, 257 and one-byte input fragments, followed by a separate caller EOF.
The PCM buffer remains 12,288 bytes. No private decoder ABI, custom repair,
physical board or external network is used.

All four streams consume every encoded byte and produce **2,115,840 PCM16
stereo bytes at 48 kHz**, SHA-256
`a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b`.
Every public output frame has the checked source geometry. Data-bearing EOS
is followed by empty draining until both input consumption and output are zero.

| Stream | Input feeds | Public process calls | PCM frames returned |
| --- | ---: | ---: | ---: |
| Unadapted complete-input baseline | 1 | 552 | 551 |
| Adapted 4096-byte input | 173 | 725 | 551 |
| Adapted 257-byte input | 2,749 | 5,499 | 551 |
| Adapted one-byte input | 706,319 | 706,320 | 551 |

For this Opus fixture the vendor consumes each supplied byte; every measured
schedule has zero pending-prefix coalesces. The shared pending owner is called,
but its allocation/recovery path is not exercised by these native streams.
Existing host pending-input tests remain separate evidence for that behavior.

The coordinator runs on core 0; the diagnostic worker runs on core 1 with
priority 3 and a 16,384-byte stack. Assertions, stack canaries, light heap
poisoning, heap integrity and both idle watchdogs remain enabled. Free heap
returns to exactly 270,632 bytes after each adapted stream. First use retains
100 bytes, also observed after unregister; zero total retention is explicitly
false. Passing attempt 02 observes minimum free heap of 236,248 bytes and unused worker
stack is 4,316 bytes. These are diagnostic measurements, not radio/TLS/TFT
production timing or memory margins.

## Required Opus trimming correction remains open

This raw vendor output is **not standard-complete playback**. The standalone
data-only verifier independently reconstructs the encoded fixture, checks all
15 page CRCs and consecutive page sequence numbers, joins continued packets,
then accounts for 551 CELT 20 ms packets from their TOC/frame-count fields.
This yields 528,960 raw stereo frames. The Opus header declares pre-skip 312;
the final EOS granule is 528,312, with zero initial granule offset. Playback
therefore requires 528,000 frames after removing the 312-frame prefix and
648-frame tail. These timeline rules come from
[RFC 7845 sections 4.2–4.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2);
the packet duration accounting follows
[RFC 6716 section 3.1](https://www.rfc-editor.org/rfc/rfc6716.html#section-3.1).

The vendor emits all raw frames for this fixture. Keeping that raw identity
across fragments proves caller integration, not correct playback trimming or
exact sample alignment. Correct trimming and alignment remain required work in
[the Ogg/Opus plan](../../../docs/CYD_OGG_OPUS_EOF.md).

A separate FFmpeg `libopus` wrapper observation decodes this same fixture to
2,112,000 PCM16 stereo bytes, SHA-256
`3a151988347648e60bf750822116edad2e5237f0263b5e522c36921535b4c2b3`.
The exact command, executable hash, version output, native statuses and PCM are
retained. The wrapper does not report its bundled libopus version. This is a
playback-length observation, not an independent exact numeric conformance oracle
for the Espressif output or proof that the extra raw samples are aligned.

## Original failure and fresh passing run

Attempt 01 completes every SDK/QEMU command and all target assertions with exit
0. Its outer reader incorrectly requires the one-byte schedule to coalesce a
pending prefix. The vendor legally consumes every byte, so the reader returns
nonpass. That original report and its frozen controller remain unchanged.

The corrected canonical reader removes exactly that one unsupported assertion.
No native harness, fixture, vendor or adapter source changes. Fresh attempt 02
repeats the actual SDK build and QEMU run; its outer report is `passed=true`
and `completed=true`, with actual native commands and SDK child all terminal 0.
The verifier proves the exact one-line reader delta, unchanged remaining frozen
inputs and both original transcripts. Attempt 01 remains historical nonpass.

## Preserved evidence and limits

`direct-captures.zip` deduplicates published bytes under `blobs/<sha256>`;
`direct-manifest.json` maps every logical path to its size, hash and blob.
The package retains both campaigns' frozen harness/controller, fixture,
registration and shared headers, public vendor source/headers/archives, selected
configuration/link/build records, exact command logs and actual child statuses.
Replaceable unselected SDK build scratch is inventoried by hash. The installed
SDK/toolchain is pinned by revision, configuration and tool hashes rather than
claimed to be republished completely.

All 20 ELF/app/merged-flash/boot/partition image payloads are omitted from the
public archive by design. Exact original hashes, byte counts, roles and explicit
local-only provenance remain in the manifest; originals remain unchanged in
ignored local campaigns. Neither the archive nor verifier contains an encoded
copy of those images. The data-only verifier checks their recorded hash bindings
without claiming to check omitted binary bytes. No semantic scanner override is
used to publish a flagged payload.

Run the standalone data-only verifier:

```text
python -B tests/verify-cyd-opus-direct-checkpoint.py
```

It imports only the pinned reviewed canonical transcript reader, checks every
published byte and binding, independently recalculates fixture CRC/timeline
accounting, and starts no archived program, compiler, decoder or emulator.
The images are diagnostics and must not be flashed as production firmware.
SILK/hybrid modes, 120 ms packets and resize behavior, chaining, corruption,
backpressure, real HTTP/TLS/TFT, production resources and physical audio remain
separate gates. Passing the raw baseline does not close the required trim fix.
