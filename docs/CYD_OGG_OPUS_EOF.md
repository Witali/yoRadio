# CYD Ogg/Opus EOF regression and playback trimming

Opus shares the CYD `NATIVE_CODEC_OGG` caller with Vorbis, including the pending
input owner and final-byte EOS lookahead. The public Espressif Ogg interface
accepts arbitrary input sizes; raw Opus instead requires complete encoded packets.
These are different contracts. The new regression uses the Ogg container path
and the unchanged LX6 archives, not C3's RISC-V archives or private repairs.

The default CYD path now uses `YORADIO_OGG_TIMELINE`: one CRC-verified page,
stream-derived Opus clipping and a separately drained public decoder per
logical link. The original lookahead caller remains the explicitly disabled
timeline option's raw-vendor fallback. Historical raw-output measurements below
remain decoder regression references, rather than current default playback.

## Production task integration

The [actual CYD task checkpoint](../tests/results/cyd-ogg-playback-task-20261101/README.md)
passes nine EOF/Stop/maintenance cases across complete 20/120 ms Opus and Vorbis,
plus Opus→Vorbis→Opus chaining within one HTTP session/generation. Both Opus
streams emit 2112000 logical PCM bytes with the independently positioned
stock-vendor window hashes; Vorbis preserves its earlier complete PCM. One
terminal PCM EOF follows all three chain links. All 18 public decoders and
16 SDK HTTP clients close, with the original task cores/priorities/stacks.

All page/trim storage is released on generation change, codec change, terminal
completion and maintenance before its decoder acknowledgement. The six actual
long-packet resize/retry pairs remain measured. The 11-TU/421-dependency closure
and 18 contradictory transcript controls bind the production implementation.

The chain reaches a minimum of 52024 free heap bytes in this diagnostic. Full
network/TLS/TFT margins, linked production exports and physical output are still
required; a 65307-byte encoded page is additional storage. A
[complete paired observation](../tests/results/cyd-opus-header-gain-20261101/README.md)
found identical stock PCM for zero/+6/-6 dB headers. The
[output-owner correction](../tests/results/cyd-header-gain-output-20261101/README.md)
now combines header and player gain before wide mono mixing and final
saturation. Its three-backend host qualification preserves the zero-gain
regression exactly. The subsequent
[complete actual-task gain checkpoint](../tests/results/cyd-ogg-gain-task-20261101/README.md)
passes 24 SDK/QEMU cases through the real PDM renderer, including a nine-link
same-HTTP chain. Each queued PCM packet carries its signed gain, so opening a
later decoder cannot overwrite calibration for earlier queued audio. All 32
complete output links match independent full mono goldens, including Vorbis
bypass/reset and the +48 dB / low-player-volume anti-early-clipping case.
All 38 decoders and 30 clients close; original cores/priorities/stacks remain.
Minimum diagnostic heap is 51824 bytes; output unused stack is 1528 bytes.
Adaptive normalization is disabled through its real settings API for this
matrix. Enabled-normalizer, full radio/TLS/TFT and physical qualification remain
separate; this checkpoint does not claim universal codec conformance.

That gain experiment preserves all 551 original audio packets and every byte
outside the OpusHead gain/CRC fields. Six fresh public decoder handles
(zero/+6/-6 dB, whole/257-byte input) produce identical nonzero raw PCM, including
energy and peak. Independent public libopus float decoding followed by explicit
normative gain gives three distinct unclipped signals. This establishes ignored
gain for this fixture, without deriving behavior from missing public fields.
The correction must apply header gain in addition to player volume/normalization,
preserve unity output and qualify signed-range rounding/clipping and link resets.

The [required family-0/1 playback support](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5)
is another explicit open gate. A player must handle valid mappings in those
families even when channel count exceeds its physical outputs. Recognition of
family 1 by the metadata observer does not establish playback support. Current
clipping binds its channel count to OpusHead. The output API accepts nonzero
channel counts but its current mono renderer consumes only the first two;
acceptance of wide PCM is not correct surround mixing.

The [complete family-1 observation](../tests/results/cyd-opus-family1-20261101/README.md)
now establishes a real stock-Ogg gap: all twelve 3/6/8-channel stock/wrapper
whole/split cases return public NOT_SUPPORT without PCM. Creator libopus and
libogg independently validate the complete fixtures. This refusal is not a
permitted format simplification or a proved allocation failure.

The [public raw-handle composition](../tests/results/cyd-opus-multistream-public-20261101/README.md)
then decodes the same complete fixtures in six cases, with 22 real handle
open/close pairs and 242 successful calls. Original self-delimited segments
and independently reconstructed common framing produce byte-identical native
PCM. Every case returns to its original free heap. This proves an available
reuse mechanism for those default layouts, not completed production support.

The remaining implementation must reconstruct packets across verified pages,
preserve trim and queued gain, and mix every mapped speaker for CYD. It must
also handle valid duplicate indices, index255 silence and unused coded
channels: the output count need not equal the decoded count. The existing
first-two-channel renderer and default-layout-only diagnostics do not close
this gate.

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

This section retains the measurements and design requirements from before
integration. The current default implementation and its task gates are above.

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

The [independent full-stream position checkpoint](../tests/results/cyd-opus-position-20261101/README.md)
now compares both complete 20/120 ms fixtures against public libopus 1.4 packet
decoding. Every possible complete 528000-frame vendor window is compared over
all 1056000 interleaved samples: 961 and 1921 candidates, respectively. Both
have one best start at raw frame 312, matching their actual pre-skip; each ends
at raw frame 528312. Maximum numeric difference is 9 PCM16 units and measured
RMSE is approximately 1.17. This establishes an observed alignment for these
two fixtures, without introducing a numeric-conformance tolerance or applying
their constants to other streams. Production trimming is still not installed.

The public simple-decoder metadata exposes no pre-skip or granule fields.
Before changing playback, use the independent sample-position evidence and
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

### Bounded metadata observer checkpoint

The standalone [timeline observer](../idf/components/native_stream/include/ogg_opus_timeline.h)
now has a [host qualification checkpoint](../tests/results/ogg-opus-timeline-20261101/README.md).
It retains no encoded input pointer, packet body or PCM buffer. Its host state
is 512 bytes; events require generation/token acknowledgement before input can
advance past a logical-link boundary. It observes known mapping families
0/1/2/3/255 and separates provisional EOS-header bounds from CRC-verified pages.

The authoritative host run passes 525 cases, 159 semantic negatives, 403 reset
positions and ten whole/4096/257/one-byte/seeded fixture runs under GCC with
ASan, UBSan and leak detection. All 219 public packet-duration comparisons agree
with installed libopus 1.4. These compare timing metadata, not decoded PCM.
The initial sandbox launch failure and earlier passing pre-reference run are
preserved separately from the authoritative source snapshot.

This header is not connected to either production audio service. It does not
implement playback trimming, validate every compressed-packet/tag detail, or
establish sample alignment of Espressif output. Unknown mapping families,
concurrent serials and unaligned streams have explicit status results. MCU
execution, caller ordering/buffering and an independent sample-position oracle
remain required before integrating the trim correction.

The [nil-page differential checkpoint](../tests/results/ogg-opus-nil-page-20261101/README.md)
then found and corrected a continuation check: a zero-segment page has no first
packet segment for its continuation bit to describe. Packet state survives the
nil page while sequence checks still cover every page. Public libogg 1.3.5
comparisons pass all 140 split schedules after the fix; the original 60 valid
schedule rejections and five CRC-status mismatches remain preserved. The
unchanged original host suite also passes against the repaired header. The
historical checkpoint verifies its original source revision explicitly, and
the successor verifies this correction; neither qualifies PCM integration.

The [verified-page owner and PCM-span checkpoint](../tests/results/ogg-page-input-20261101/README.md)
supplies the next two building blocks. The owner copies at most one complete
encoded page (up to 65307 bytes) and exposes only its verified event/bytes.
The span helper clips already aligned raw PCM in 48 kHz frames per channel,
without changing samples or allocating PCM. Host ASan/UBSan/leak checks pass
276 page cases, 204 span cases and every allocation ordinal for both complete
fixtures, including refusal/retry and abandonment. The unchanged observer
regression also passes. Neither helper is production-selected yet; public
vendor ordering, target memory margins, independent sample alignment and the
complete task integration remain required. A full page is encoded storage,
not a promise of negligible extra heap in the CYD profile.

## Additional software gates

- The default production task now passes the qualified sample-accurate trim
  and ordered nonzero-header-gain cases above. Qualify other legal packet modes/mappings,
  broader rate semantics and remaining resource/error cases before claiming
  complete playback-format coverage.
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
  decoded=0, then matches all raw PCM. The [actual CYD task resize checkpoint](../tests/results/cyd-opus-20261030/LONG_TASK.md)
  also passes T0 EOF, T1 Stop/discard/reopen and T2 maintenance/resume. All five
  real decoder handles start at 12288 bytes, return a measured buffer error
  needing 23040, and immediately retry successfully with unchanged input and
  zero error consumption/output. Original task cores, priorities and stacks
  remain unchanged. Ten contradictory resize transcripts are rejected by the
  standalone evidence verifier. Nonzero error consumption, empty-input retries
  and OOM remain unqualified. These results do not justify changing production
  input advancement. These historical resize-only gates did not implement
  trimming; the current default is qualified by the later task gates above.
- Deliberate backpressure, actual HTTP/TLS/TFT traffic, production resources
  and physical audio/output backends remain separate gates.

The deferred custom Vorbis arithmetic and private decoder work remain deferred.
