# CYD Ogg/Opus EOF regression and playback trimming

Opus shares the CYD `NATIVE_CODEC_OGG` caller with Vorbis, including the pending
input owner and final-byte EOS lookahead. The public Espressif Ogg interface
accepts arbitrary input sizes; raw Opus instead requires complete frames.
These are different contracts. The new regression uses the Ogg container path
and the unchanged LX6 archives, not C3's RISC-V archives or private repairs.

## Measured direct-vendor regression

The complete existing `tests/fixtures/esp32c3_calibration/opus-510.ogg` is
706319 bytes, SHA-256
`53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11`.
Its 15 Ogg pages have valid CRCs and consecutive sequence numbers. Continued
packets cross page boundaries. All 551 audio packets are CELT with a duration
of 20 ms; this fixture does not cover SILK, hybrid or longer packets.

An unadapted baseline supplies the entire borrowed encoded fixture with EOS,
then drains the public decoder completely. No pending-input or EOF adapter is
used for that baseline. Separate cases supply 4096, 257 and 1 byte at a time,
followed by separate caller EOF, using both exact production adapters. Every
case consumes all 706319 encoded bytes and produces the same 2115840 PCM16
stereo bytes at 48 kHz, SHA-256
`a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b`.

The one-byte Opus run consumes each byte immediately. It calls the shared
pending-input owner but does not exercise retained prefixes; the corresponding
Vorbis cases cover that behavior. An initial reader incorrectly required a
nonzero coalescing count and rejected an otherwise complete native run. Its
original report remains nonpassing. A fresh complete campaign with only that
unsupported reader assertion removed passes; the C harness, vendor and fixture
are unchanged. No report or child status was rewritten to claim success.

The initial output capacity remains 12288 bytes. Steady-state free heap is
270632 bytes before and after each adapted stream; final unregister leaves
100 bytes relative to the pre-registration observation. Minimum observed heap
is 236248 bytes. This is not a claim of zero total registry retention or of
production radio/TLS/TFT resource margins.

The [direct checkpoint](../tests/results/cyd-opus-20261030/DIRECT.md) preserves
the actual commands, source/image hashes, original failure and passing run.
The [complete CYD task checkpoint](../tests/results/cyd-opus-20261030/TASK.md)
also passes ordered EOF, partial Stop/reopen and three-owner maintenance/resume.
Every full playback matches the raw vendor reference. All five decoder/client
instances close; there are 2710 public process calls, no resize requests and no
pipeline allocation/stream/decode/output faults. The actual 12288-byte output
capacity is asserted at every public call.

Original task affinities, priorities and stacks remain unchanged. Observed free
stack is stream 4236, decode 4564 and output 2892 bytes; minimum observed heap
is 182548 bytes. These figures describe the synthetic transport/output diagnostic.
The build binds 11 selected translation units and 416 actual compiler
dependencies. Nineteen negative reference checks reject missing commands,
artifacts and harness sources, or changed QEMU/image/core/archive identities.

## Required playback-trimming correction

The measured raw output is **not standard-complete Ogg Opus playback**.
[RFC 7845 sections 4.2–4.4](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2)
define pre-skip and end trimming. This fixture has pre-skip 312 and terminal
granule 528312, with zero initial granule offset:

| Quantity | Frames per channel | PCM16 stereo bytes |
| --- | ---: | ---: |
| All 551 decoded packets | 528960 | 2115840 |
| Leading pre-skip | 312 | 1248 |
| Terminal padding | 648 | 2592 |
| Required playback | 528000 | 2112000 |

An independent complete decode through FFmpeg's `libopus` wrapper produces
2112000 bytes. Its executable, command, terminal statuses, source fixture and
output hash are recorded separately. The bundled libopus version is not
reported; this observation validates playback length, not byte-identical
numeric conformance between implementations.

The public simple-decoder metadata exposes no pre-skip or granule fields.
Before changing playback, establish an independent sample-position oracle and
derive trimming from each stream's actual headers/page timeline. Do not apply
fixture constants globally or silently trim twice. Initial granule offsets,
continued packets, terminal page bounds, Stop/generation changes and chained
logical streams need explicit ownership and tests. The raw vendor identity
above remains a decoder-integration reference, not the final playback oracle.

The [public parser observation](../tests/results/cyd-opus-20261030/PARSER.md)
uses Espressif's documented registration callback and unchanged vendor decoder
operations. Paired stock/pass-through instances produce identical whole PCM,
metadata and consumption for both 20 ms and 120 ms fixtures. Every one of 682
successful callbacks reports zero for sample count, duration, both padding
fields and total size. These fields therefore provide no observed trim bounds
for these fixtures. The reported extra-data frame-duration value also differs
from the encoded packet duration and must not be used as its timing oracle.

A separate read-only hash of raw emission positions [312,528312) is retained
for each fixture. It is a same-vendor position reference, not an implemented
trim filter or independent proof of sample alignment. The original missing
public-include-path compilation failure and corrected fresh passing campaign
are both preserved.

The next trim implementation needs an application-owned encoded timeline
observer while retaining Espressif synthesis. Bound its memory and expose input
progress plus an acknowledged link-boundary event, so later chained headers
cannot overwrite bounds for PCM still being drained. Feed original encoded
bytes once; pending-prefix replay and resize retries must not advance it twice.
Keep granules in checked 64-bit 48 kHz frame units. Separate provisional page
header bounds from CRC-verified completion, and report unknown alignment on
missing continuation, sequence gaps or truncation. Initial offsets, first-page
EOS, nil pages, multiple links in one input and lifecycle reset need host tests
before production integration. No new observer is selected by this checkpoint.

## Additional software gates

- Correct and qualify sample-accurate Ogg Opus pre-skip/end trimming against an
  independent reference before marking playback semantics complete.
- Cover legal packet modes and durations, including 120 ms stereo packets.
  The [official Opus decoder API](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html)
  requires capacity for up to 5760 samples per channel: 23040 PCM16 stereo bytes.
  These exceed the initial output buffer and require a measured public resize
  retry test, including input-consumption behavior.
  The [reproducible 120 ms fixture](../tests/fixtures/opus_ogg_long_packets/README.md)
  is ready: 92 legal packets, CRC/timeline guards and independent complete
  libopus playback pass. The [whole-input public resize checkpoint](../tests/results/cyd-opus-20261030/RESIZE.md)
  observes two genuine insufficient-buffer results: consumed=0, decoded=0,
  needed=23040 with initial capacity 12288. Both fresh retry strategies match
  the sufficient-capacity baseline of 2119680 raw bytes.
  [Fragmented-input resize](../tests/results/cyd-opus-20261030/STREAM_RESIZE.md)
  also passes 4096/257/1-byte feeds with the exact production pending/EOF
  helpers. Each schedule witnesses one nonterminal resize with consumed=0 and
  decoded=0, then matches all raw PCM. Actual-task resize, nonzero error
  consumption, empty-input retries and OOM remain unqualified. These results
  do not justify changing production input advancement.
- Deliberate backpressure, actual HTTP/TLS/TFT traffic, production resources
  and physical audio/output backends remain separate gates.

The deferred custom Vorbis arithmetic and private decoder work remain deferred.
