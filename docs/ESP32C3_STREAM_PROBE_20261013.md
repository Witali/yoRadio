# Incremental initial stream detection — 2026-10-13

First implementation stage of the [per-frame format plan](ESP32C3_OLED_NATIVE_TODO.md).
This changes initial AUTO selection only. Explicit/MIME-selected codecs and
existing per-frame AAC reconfiguration and decoded metadata remain intact.
MP3-to-AAC switching inside a connection is still pending.

## Behavior

- Remove the unknown-prefix-to-MP3 fallback. An unresolved stream ends with
  `unknown audio format` without opening a speculative MP3 decoder.
- Collect an at-most-ten-byte prefix across arbitrary reads after HTTP/ICY
  removal. Replay the identified header exactly once before unconsumed data.
- Recognize native FLAC with its mandatory first STREAMINFO block header;
  Ogg capture/version; validated MP3 Layer III header fields; ADTS sync,
  sample-rate index and minimum frame length. Legal free-bitrate MP3 is not
  rejected solely for bitrate index zero. Header recognition is not proof
  that every subsequent frame or payload is valid.
- Skip ID3v2.2/2.3/2.4 tags using synchsafe sizes, including v2.4's optional
  footer. ID3 does not imply MP3. Bound aggregate skipped tag size to 1 MiB
  and discarded synchronization bytes to 4,096. No tag payload allocation.
- The initial AUTO probe has a ten-second deadline, including tag reception,
  independent of the optional station watchdog. The HTTP read poll can add
  one read interval. Network read/unavailability errors retain their status.
- EOF during an incomplete prefix/tag remains unknown; it cannot silently
  select a codec. A new connection gets a new probe. No input pointer is held
  across reads. Existing generation checks cancel stale queue submissions.

The bounded prefix state is on the existing stream task stack, not a new
heap buffer or task. It measures 40 bytes on the host ABI; target stack-usage
evidence is retained with the build. Once selected, the probe adds no scan
of compressed payload. This does not implement per-frame cross-codec checks.

## Validation

`python -B -X utf8 tests/run-esp32c3-stream-probe.py` compiles the production
header and extracts the actual `send_stream_audio()` function. ASan/UBSan
checks every two-part split and byte-at-a-time reads for MP3/AAC/FLAC/Ogg,
exact replay, leading junk, consecutive tags, an AAC file with false MP3
bytes inside its tag, malformed/oversized tags, reserved header fields,
bounded unknown input, partial headers and output-queue failure. It also
checks 10,000 deterministic malformed prefixes. Decoder I/O is mocked.

Existing `run-esp32c3-stream-format.py` passes under ASan/UBSan (seven groups:
metadata/PCM/UI, workspace changes, Helix, framing, adaptive ADTS, SBR reserve,
scratch ownership). The native-IDF/static-worker/WebUI-OTA JavaScript suites
pass 55 tests. ESP-IDF 6.1 `9a97f6c5` successfully builds `idf61-stream-probe`
using the previous production-derived WebUI config.

The [saved image](../firmware/development/esp32c3-idf-6.1-r9a97-stream-probe/app.bin)
was initially build/host-tested only. The subsequent physical HTTP campaign
below tests the same image; it is still not production-qualified. A subsequent
laboratory HTTPS campaign and watchdog-disabled deadline tests are recorded
below. Cross-codec
switching, misleading MIME and stronger multi-frame confirmation remain open.

## Corpus and physical follow-up

Test implementation: `93dc6183`; firmware implementation: `cefbeb93`.
The host test now processes eleven hash-verified original synthetic encoded
files, including MP3, FLAC, Vorbis, Opus, LC, HE and HEv2. For each file it
checks 1-, 7- and 2,048-byte reads, both unchanged and with an additional ID3
tag containing misleading sync bytes. All **66 cases passed** under ASan/UBSan.
After legitimate tags are removed, every byte submitted by the actual
`send_stream_audio()` function matches the source audio. This establishes
transport byte preservation, not an independent PCM decoder comparison.

`tools/esp32c3_tests/stream_probe.py` installed the saved app through WebUI OTA
and served finite HTTP files with **no Content-Type header**. Server writes
paused at each of the first nine byte boundaries (20 ms per pause). TCP may
coalesce writes; every possible split is covered separately by host tests.

| Physical scenario | Result |
|---|---|
| MP3 320 kbit/s, FLAC level 8, Vorbis q10, Opus 510 kbit/s | 4/4 passed |
| AAC-LC 48 kHz, HE-AAC 48 kHz, HE-AACv2 44.1 kHz | 3/3 passed |
| HE-AAC and HE-AACv2 preceded by ID3 with false MP3 sync bytes | 2/2 passed |
| Unknown zeros, partial sync, truncated ID3 | 3/3 explicitly rejected |

All nine positive cases repeatedly reported the expected format, remained
playing during a three-second active counter window, and ended with
`stream ended`. Negative cases ended with `unknown audio format`. No new
allocation failures, watchdog events or restarts were recorded. Active-window
output counters did not increase; idle/EOF counter growth was excluded.
This short check is not a long-duration or analog-audio continuity test.

The original `idf61-production-prefill1000` application was restored and its
hash verified; playback is stopped as initially. Wi-Fi, playlist and settings
were compared in RAM and are unchanged. No private data/hashes are saved.
Raw [physical evidence](../tests/results/esp32c3-stream-probe-20261013/physical-01/)
and [corpus evidence](../tests/results/esp32c3-stream-probe-20261013/corpus-01/)
include exact runner sources and checksums. The earlier build-only evidence
remains unchanged. The fixture server's new `mime=None` behavior passed an
exact-byte HTTP test and six existing HTTP/HTTPS server regression tests.

## HTTPS and AAC transitions

Runner `ef732899` adds verified laboratory TLS and ordered format-transition
checks. Two continuous AUTO/no-MIME HTTP cases passed on `idf61-stream-probe`:

- `changing`: LC 44.1 kHz stereo → LC 48 kHz stereo → HE 48 kHz stereo →
  HEv2 44.1 kHz stereo.
- `implicit-sbr`: LC 22.05 kHz mono → HEv2 44.1 kHz stereo → LC 48 kHz stereo.
  The first transition retains the same ADTS core configuration.

Each format required repeated observations in order, followed by correct EOF.
Active transition health had 77 and 59 samples respectively. All format,
allocation, watchdog, restart and output-counter checks passed.

The separate `idf61-probe-tls-lab` image, ELF SHA-256
`220c3310596f0d58bcc2e9db78cbd263cc0881f5d70d2d5e986bf02e0419f8f0`,
adds one ephemeral test CA. Its enabled sdkconfig differs only in the custom
CA switch/path; full public roots, peer verification, 16 KiB TLS RX capacity,
codec options, buffers and compact-storage precision are unchanged. It is
**laboratory-only**, not a production replacement. No operating-system trust
store was changed, and no private keys are committed.

On this image **14/14 HTTPS cases passed**: the original 12 no-MIME cases plus
both AAC transitions. All connections have server-side negotiated evidence:
TLS 1.2, `ECDHE-RSA-AES256-GCM-SHA384`. The TLS server writes normally contain
1,024 audio bytes, with fragmented initial writes; this is not a maximum TLS
record-size or handshake-variant matrix.

| Observation | System free heap | Largest free block |
|---|---:|---:|
| HTTP changing, sampled minimum | 37,028 B | 22,528 B |
| HTTP implicit SBR, sampled minimum | 31,160 B | 20,480 B |
| HTTPS HE-AAC, active-window end | 36,752 B | 23,552 B |
| HTTPS HE-AACv2, active-window end | 37,036 B | 23,552 B |
| HTTPS changing, sampled minimum | 34,408 B | 22,528 B |
| HTTPS implicit SBR, sampled minimum | 29,732 B | 20,480 B |

These are observations, not guaranteed bounds or isolated TLS allocation
costs. No allocation failure/watchdog event was recorded; compared active
output counters stayed unchanged. No unexpected restart occurred. Both runs
restored the original `idf61-production-prefill1000` image/hash and stopped
state; in-memory comparisons verified Wi-Fi, playlist and settings unchanged.

Evidence: [HTTP transitions](../tests/results/esp32c3-stream-probe-20261013/transitions-http-01/),
[HTTPS matrix, public test CA and exact configuration delta](../tests/results/esp32c3-stream-probe-20261013/physical-tls-01/),
and [labelled laboratory artifact](../firmware/development/esp32c3-idf-6.1-r9a97-stream-probe-tls-lab/manifest.json).
These tests cover changes within AAC, not MP3 ↔ AAC family switching.
Long public-station playback, misleading MIME, stronger frame confirmation
and cross-codec switching remain
open. No full production qualification is claimed.

## Incomplete prefix: deadline, Stop and replacement

The HTTP prefix-control campaign on `idf61-stream-probe` passed all three
cases with the station watchdog explicitly disabled and read back:

| Case | Result | Observed response |
|---|---|---:|
| Incomplete ADTS header, connection still open | PASS: `unknown audio format` | 10.300 s from server delivery start |
| Stop while waiting for header | PASS: stayed stopped | 0.145 s to first stopped observation |
| Replace incomplete stream with valid HE-AAC | PASS: repeated correct format and steady output counters | 2.132 s to three confirmations |

The fault server pauses two seconds after each initial byte; fewer than the
seven ADTS header bytes had arrived when the deadline fired. HTTP EOF and
header completion therefore cannot explain the timeout. No restart,
allocation failure or task-watchdog counter increase occurred. Settled idle
medians before and after were identical: 140,068 bytes free, largest block
110,592 bytes and 16 tasks. These checks cover HTTP control and sampled heap
recovery, not long playback, HTTPS cancellation or analog audio continuity.

The original app hash, stopped state and private Wi-Fi/playlist/settings
were verified after restoration, including the original watchdog setting.
[Raw evidence and exact executed controller](../tests/results/esp32c3-stream-probe-20261013/prefix-control-01/)
are frozen with checksums. The reusable runner
`tools/esp32c3_tests/prefix_control.py` additionally returns failure after
restoration if any recorded case or heap-recovery check failed; the frozen
controller predates that exit-status guard.

## Short signatures after junk: follow-up correction

`e3c06954` corrects an initial-probe delay: a complete four-byte MP3 header
after one junk byte was not recognized until additional bytes arrived. The
same fixed ten-byte search window affected short ADTS/FLAC/Ogg prefixes.
The new regression failed on the previous parser. The parser now discards
impossible candidates immediately and rechecks retained suffixes, retaining
partial supported signatures across reads. ID3 size/skip validation and
search/time bounds remain in place; no heap allocation or state growth is
introduced. Supported prefix sizes have named constants.

ASan/UBSan passes exact-header cases for all four formats after 1–24 junk
bytes, every two-part split, byte-at-a-time reads, overlapping candidate
prefixes, incomplete headers and an empty ID3 tag after junk. The existing
66 encoded-corpus cases and 10,000 malformed-prefix trials also pass.
[Before/after host evidence](../tests/results/esp32c3-stream-probe-20261013/prefix-resync-01/)
retains the original assertion failure. Previous physical results above
apply to the earlier firmware; they are not hardware qualification of this
follow-up change.

ESP-IDF 6.1 built the follow-up as `idf61-probe-resync` (1,460,096 bytes),
saved under [firmware/development](../firmware/development/esp32c3-idf-6.1-r9a97-probe-resync/manifest.json).
Enabled sdkconfig values match the original non-laboratory probe image;
the ephemeral TLS test CA is absent. Compiler-reported stack frames remain
896 bytes for `stream_task` and 96 bytes for `send_stream_audio.part.0`;
these are individual frames, not measured total stack high-water marks.
The follow-up subsequently passed **14/14 physical HTTP cases**: the seven
codec files, two ID3 cases, three unknown/truncated cases and both AAC
transition sequences. For `changing`, 78 active health samples had minimum
free heap 37,136 bytes and largest block 22,528 bytes; `implicit-sbr` had 57
samples, minima 31,308 and 21,504 bytes. All cases passed their restart,
allocation/watchdog and active output-counter checks. The original image
hash, stopped state and private settings were verified after restoration.
[Physical evidence and executed runner](../tests/results/esp32c3-stream-probe-20261013/resync-physical-01/)
are retained. This image still needs HTTPS/long-play qualification; no full
production qualification or analog continuity claim is made.
The frozen runner is the one executed. The reusable runner subsequently
gained a nonzero exit status after restoration when any recorded case failed;
these results were independently checked for all 14 explicit PASS entries.

## Frame boundary walker for the next integration stage

`main/stream_frames.h` is an experimental allocation-free MP3/ADTS walker,
**not yet called by the firmware's audio path**. It starts at a known frame
boundary, collects at most seven header bytes across input reads, calculates
the frame length and skips exactly that payload before examining another
header. Payload sync patterns cannot trigger codec switching. It reports each
frame's family/core parameters and passes its original bytes synchronously to
a sink. No caller pointer survives a call. Host state is 16 bytes, with no
full-frame buffer. This is not a RAM improvement measurement of the firmware.

MPEG-1/2/2.5 Layer III bitrate, padding and sample-count handling were checked
against [FFmpeg's MPEG header parser](https://www.ffmpeg.org/doxygen/7.0/mpegaudiodecheader_8c_source.html).
ADTS frame length, raw-block count and core-rate interpretation were checked
against [its ADTS parser](https://www.ffmpeg.org/doxygen/7.0/adts__header_8c_source.html).
PCE channel configuration remains unknown until decoded; SBR/PS output rate
and channels must continue to come from `native_aac_decoder`.

`tests/run-esp32c3-stream-frames.py` compares every frame offset/length with
ffprobe for 26 files (1,310 frames): eight existing MP3/AAC fixtures and 18
generated MP3 files covering all nine MPEG rates, mono/CBR and stereo/VBR.
Each file is replayed with 1-, 7- and 2,048-byte reads with exact byte checks.
A mixed MP3/AAC sequence adds 1,457 frames, compared with concatenated
per-file reference boundaries, using the same three read sizes. ASan/UBSan
also covers every split of a synthetic mixed stream, every truncation,
sync-shaped payload, callback failure and 100,000 random headers.
[Exact sources, results, generation commands and checksums](../tests/results/esp32c3-stream-probe-20261013/frame-walker-01/)
are retained. The reference executable versions are in `results.json`.

Explicit limits: free-format MP3 returns a distinct unresolved-length result
and retains its header; it is not rejected as invalid or assigned a guessed
length. Inter-frame tags, damaged-boundary resynchronization and container
transitions are not handled by this strict walker. It does not validate CRC
or decode audio, prove PCM continuity, or implement live decoder switching.

Integration work, based on `audio_service.c` ownership paths:

1. Coalesce frame spans into existing encoded-packet leases. Never allocate a
   full ADTS frame just to classify it, or consume a queue slot per header.
   `prefill_encoded_input()` currently measures occupied slots, so fragmenting
   packets would falsely signal a full audio queue.
2. Add an internal decoder-drain marker before a codec-family change.
   `return_decoded_packet()` currently forwards every nonzero end marker to
   PCM; the new marker must drain/release the old decoder without stopping
   queued playback. Verify the last old frame and first new frame by PCM.
3. Open the new decoder only after old allocations are released; retain the
   existing generation cancellation and PCM layout on each output packet.
   Avoid the initial one-second prefill delay on a live family transition.
4. Specify and test free-format, ID3, corruption and conflicting-MIME policy
   before enabling the router. Preserve existing FLAC/Ogg and AAC SBR/PS paths.
5. Test both directions on host and hardware, including repeated changes,
   Stop/replacement, EOF, heap recovery and output counters under HTTPS.

## Comparison with ffprobe / FFmpeg 8.1.1

The installed reference is ffprobe 8.1.1 (Gyan full build). Nine upstream
files were read at tag `n8.1.1`, commit
`239f2c733de417201d7ad3b3b8b0d9b63285b2b1`; their URLs and byte hashes are
recorded in the [audit evidence](../tests/results/esp32c3-stream-probe-20261013/ffmpeg-audit-01/).
ffprobe delegates to demuxers/parsers and, for stream information, decoders.
Our initial probe and experimental boundary walker are smaller, different
layers; matching packet boundaries does not imply matching recovery or PCM.

| Area | Upstream behavior | Our status / decision |
|---|---|---|
| Frame geometry | MPEG version/rate/bitrate/padding and ADTS length/raw blocks | Matches on the 26-file corpus; preserve this arithmetic |
| Format confidence | MP3 demux probe scores consecutive frames; seven initial frames earn its high score. AAC uses three. MP3 startup also looks for two compatible headers | Our initial probe trusts one header. Add bounded multi-header confirmation using existing input storage, with explicit short-file/EOF behavior |
| VBR and parameter changes | MPEG parser comparison mask excludes bitrate/padding; it tracks header confidence separately from parameter publication | Do not mistake changing bitrate/padding for another codec. Do not freeze decoded rate/channels based on initial headers |
| Recovery | MPEG/AAC parsers scan for sync when alignment is lost; AAC demuxer also handles ID3 between frames | Strict walker currently stops. Add bounded recovery and incremental tag skipping before production integration |
| HE-AAC metadata | Common AAC parser deliberately avoids treating ADTS rate/channels as decoded output parameters | Preserve our native decoder's SBR/PS/PCE metadata; ADTS alone cannot label HE-AAC output correctly |
| Free-format MP3 | Low-level header reader returns unresolved length; the higher-level helper and demuxer check do not establish that length | Our distinct FREE_FORMAT result is appropriate. Upstream is not a drop-in solution to full free-format support |
| Memory | `ff_combine_frame()` grows a buffer with `av_fast_realloc`; MP3 startup requests about 64 KiB of seek-back capacity | Reuse our queue and bounded header state. Do not import FFmpeg's buffering architecture into C3 |

Primary code references:
[MP3 probing/startup](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavformat/mp3dec.c),
[MPEG parser](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/mpegaudio_parser.c),
[AAC demuxer and inter-frame tags](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavformat/aacdec.c),
[AAC metadata policy](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/aac_ac3_parser.c),
[MPEG header reader](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/mpegaudiodecheader.c),
[frame assembly](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libavcodec/parser.c).

### Reproduced differences, not a passing qualification matrix

`tests/compare-esp32c3-ffprobe.py` compiles our actual headers under ASan/UBSan
and compares nine controlled inputs with the full ffprobe pipeline. Inputs
have no filename-extension hints. No firmware or board changes are involved.

| Input | Our initial probe / strict walker | ffprobe observation |
|---|---|---|
| Clean HE-AAC / MP3 | Complete; 15 / 460 frame headers | Same packet counts; 48 kHz stereo |
| False MP3 header then valid AAC | Initially chooses MP3; walker later rejects | Chooses AAC and reports 15 packets, **but rate/channels remain zero**; not successful decoding evidence |
| False AAC header then valid MP3 | Initially chooses AAC; walker later rejects | MP3, 460 packets, 48 kHz stereo |
| ID3 between AAC frames | Walker stops after first frame | All 15 packets and correct HE-AAC parameters |
| Junk between AAC frames | Walker stops after first frame | Resynchronizes; 15 packets, correct parameters |
| ID3v1 after MP3 | 460 frames emitted, then walker rejects tail | 460 packets; tail metadata is not audio |
| AAC payload shortened by three bytes | Explicit incomplete state | Still 15 packets and known parameters; packet count alone is not an integrity check |
| MP3 with bitrate-index-zero headers | Recognized MP3, explicit unresolved frame length | AUTO fails; forced MP3 reports zero rate/channels and `Header missing` despite exit code zero |

The last case changes only bitrate-index bits in the known 320 kb/s fixture;
it does not certify all free-format bitstreams. The earlier exploratory run
used `.bin` names, which allowed ffprobe's unrelated bintext extension fallback;
the retained final comparison removes extension hints. Tests must check valid
metadata and decoded output, not just ffprobe's exit code or codec name.

Keep intentional stricter checks: our ADTS validator requires layer zero and
space for the CRC field when present; the low-level FFmpeg ADTS header reader
skips the layer field and checks a seven-byte minimum. Our MP3 probe rejects
reserved emphasis, while FFmpeg's fast header check is more permissive. These
differences do not justify weakening validation without a real compatibility
case. CRC verification of payloads is still a separate, unimplemented gate.

Priority: multi-header confidence, inter-frame ID3 and bounded resync, then
coalesced queue integration and decoder draining. EOF tails and truncated
frames need separate handling. Retain reference tests, but add decoded-PCM
and live transition checks. No upstream code was copied into firmware;
downloaded LGPL source remains reference material under `.build`.

## Follow-up: incremental inter-frame ID3

The experimental walker now skips ID3v2.2/2.3/2.4 envelopes at known frame
boundaries. A shared `stream_tags.h` validates the header version, reserved
flags and synchsafe size for both initial probing and the walker. The optional
v2.4 footer adds ten bytes. Tag contents, extended headers, CRC and footer
contents are not validated or interpreted; their encoded bytes are skipped.
This follows the size rules in [ID3v2.4 section 3.1](https://id3.org/id3v2.4.0-structure),
[ID3v2.3](https://id3.org/id3v2.3.0) and [ID3v2.2](https://id3.org/id3v2-00).

No tag-body allocation or input pointer retention is needed. On the sanitizer
host the walker state grows from 16 to 28 bytes; initial-probe state remains
40 bytes. The application limit of 1 MiB counts consecutive tags including
headers/footers and resets after an audio frame. It is not a lifetime quota
or the ID3 format's maximum. Partial header/body/footer keeps EOF incomplete.
An audio-looking header inside a tag does not trigger a codec change, and
an ID3-looking sequence inside audio is delivered unchanged.

Validation, saved in [id3-boundaries-01](../tests/results/esp32c3-stream-probe-20261013/id3-boundaries-01/):

- ASan/UBSan unit checks cover every two-part split, one-byte input, all three
  supported versions, optional footer, every tag truncation, malformed flags
  and sizes, sticky errors, adjacent tags, the exact resource bound and its
  reset after an audio frame.
- The 26-file corpus contains 1,310 audio frames. Reads of 1, 7 and 2,048 bytes
  pass both clean and with a tag before every frame. Emitted bytes equal the
  original compressed data, including AAC-LC, HE-AAC and HE-AACv2 fixtures.
- The 1,457-frame mixed MP3/AAC sequence also passes clean and tagged, at all
  three read sizes. Existing ffprobe packet-boundary comparisons still pass.
- The production initial probe/send regression passes all 66 corpus cases.
- Repeating the nine-case ffprobe audit changes the inter-frame ID3 case from
  rejection after one frame to all 15 frames / 5,121 audio bytes, complete.
  The original audit above remains historical evidence; its other recovery,
  false-sync, free-format and ID3v1 limitations remain unresolved.

This is preparation for the live queue adapter. The walker is still not called
by production audio_service; these results do not establish live codec changes
or board playback qualification. The production initial probe only shares the
same envelope-size calculation, preserving its previous behavior.

ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207` builds this
change successfully. The development image `idf61-id3-boundaries` is saved at
[`firmware/development/esp32c3-idf-6.1-r9a97-id3-boundaries/`](../firmware/development/esp32c3-idf-6.1-r9a97-id3-boundaries/)
with the build log, source commit, image hashes and unchanged sdkconfig hash.
It has not been installed on the board or qualified for production.

## Follow-up: decoder-segment drain contract

`AUDIO_DRAIN_CODEC` is a new internal encoded-queue marker. Like EOF, its
nonzero value asks the current decoder to flush buffered output and release
its resources. Unlike a terminal stream marker, `return_decoded_packet()`
does not forward it to the PCM queue. Already queued PCM remains live, and
the output task does not flush/stop the DMA stream merely because a decoder
segment ended. True EOF and transport errors retain their terminal behavior.

The decoder's prefill gate now applies only when its old codec is AUTO.
Generation changes already reset that field to AUTO before processing new
packets. A live family change after a drain does not wait a second time for
the connection's startup prefill. Resource release completes synchronously
in the consumer before the next queued segment can open another decoder.
No extra data buffer or persistent state was added for this contract.

Tests in [codec-drain-01](../tests/results/esp32c3-stream-probe-20261013/codec-drain-01/):

- `run-esp32c3-eof.py` extracts the actual queue/completion operations and
  prefill gate. It checks old PCM, internal drain, subsequent PCM and final
  EOF ordering, cancellation, decode-failure status and live-switch prefill.
  Its stale extraction of the network terminal branch was updated; the
  current encoded-queue aliases and PCM-tail flush are modelled explicitly.
- `run-codec-segment-drain.py`: 24 ASan/UBSan cases execute the actual generic
  decoder loop and `return_decoded_packet`, with deterministic SDK/native-AAC
  substitutes. They cover multiple cached PCM outputs on drain/EOF, workspace
  growth, normal input, cancellation and errors. Freed decoder/PCM workspace
  does not invalidate the copied queued output.
- `run-custom-decoder-terminal.py`: 20 ASan/UBSan ownership cases now include
  the internal drain for custom FLAC, AAC and MP3 branches. Each branch emits
  its final callbacks before destroying its workspace; arena-busy and repeated
  terminal cleanup checks remain covered.

These are queue/lifetime tests, **not real decoder PCM or timing validation**.
No producer sends `AUDIO_DRAIN_CODEC` yet. The frame walker still needs the
coalescing queue adapter, recovery/confidence policy and hardware tests with
real MP3/AAC transitions before live switching can be claimed to work.

ESP-IDF 6.1 builds this contract successfully with the same sdkconfig as the
preceding image. The unqualified development image `idf61-codec-drain` is
saved in [`firmware/development/esp32c3-idf-6.1-r9a97-codec-drain/`](../firmware/development/esp32c3-idf-6.1-r9a97-codec-drain/),
with its source commit, hashes and build log. No board deployment was made.

## Follow-up: experimental encoded-queue integration

`CONFIG_YORADIO_FRAME_ROUTER=y` now connects the boundary walker to
`send_stream_audio()` for MP3/ADTS. It depends on the adaptive input queue and
defaults **off**. This is a testable integration, not a production qualification.
Both HTTP/ICY delivery and the flash benchmark path use it when enabled.

`stream_encoded_router.h` combines header/payload spans in an existing
2,048-byte encoded-packet lease. It commits on full packets, codec changes or
the end of the current send call. A partially filled lease never survives a
socket read. The assembled initial probe header joins the same packet as the
rest of that read, instead of consuming a separate queue slot. No full frame,
tag body or second staging buffer is allocated. Tiny network reads can still
produce small packets; this does not claim to eliminate transport fragmentation.

Before MP3/AAC family changes, the producer commits old bytes, enqueues
`AUDIO_DRAIN_CODEC` for the old codec, then publishes new-codec bytes. The
consumer's tested drain contract releases old resources before opening the
next decoder. AAC profile/rate changes remain within the AAC decoder, whose
decoded SBR/PS/PCE metadata stays authoritative. A first MP3/AAC header may
correct an explicit MP3/AAC hint without draining an unopened decoder.

The new `adaptive_input_cancel()` releases only the producer's uncommitted
WRITING lease. READY and READING buffers cannot be cancelled. It follows the
same deferred-shrink policy as consumer return and wakes waiters for space.
Stop, failed packet commit and rejected input return the lease rather than
leaving a permanent occupied slot. Already committed bytes remain owned by
the queue and retain their generation cancellation checks.

Limits remain explicit:

- FLAC/Ogg keep their opaque send path. Conflicting MIME versus container
  signatures and cross-container switching are not addressed here.
- Free-format MP3 preserves its header/data and hands the rest of the
  connection to the existing MP3 decoder. Further boundary switching in that
  connection is disabled; this is no new decoder support claim.
- Strict alignment remains: multi-header confidence, bounded resync, ID3v1
  and APE tails still need implementation before enabling this by default.
- Clean transport EOF with a partial routed frame/tag reports
  `truncated audio frame`. Existing transport failures retain their reason.
- No claim of gap-free playback or unchanged CPU load is made from host tests.

Evidence in [encoded-router-01](../tests/results/esp32c3-stream-probe-20261013/encoded-router-01/):

- The real `send_encoded()` / `send_stream_audio()` implementation and adapter
  run under ASan/UBSan with a bounded, synchronous queue substitute. Every
  two-part split and one-byte input preserve bytes and ordered drain markers.
  One hundred short ADTS frames in one read use one packet; 3,600 bytes use
  two packets. Failed commit, cancellation during/after acquire, parser
  rejection, free-format fallback, opaque formats and truncated EOF are tested.
- Actual MP3 + AAC-LC + HE-AAC + HE-AACv2 + MP3 fixtures with inter-segment ID3
  produce exactly 900,120 original audio bytes at read sizes 1, 7 and 2,048.
  The only drains occur at audio offsets 441,600 (old MP3) and 458,520 (old AAC).
  The 2,048-byte run uses 444 queue commits including both drain markers.
  These checks prove byte routing, not decoded PCM correctness.
- The real adaptive queue's sanitizer suite passes cancellation/state/shrink
  checks plus its existing 30,000 concurrent packet test and TLS-pressure cases.
- The default-off initial probe regression retains its 66 passing corpus cases;
  the decoder-drain and EOF host checks still pass.

Next qualification: run actual decoders through repeated MP3/AAC transitions,
compare boundary PCM, test Stop/replacement/EOF and allocation recovery on C3,
then combine with recovery and confidence work. Keep the production default off
until those checks and the other-codec/HTTPS regression pass.

The enabled ESP-IDF 6.1 build succeeds. Linker map assigns 32 bytes of BSS to
`s_frame_router`; no new heap buffer is reserved. Compiler `.su` reports 112
bytes for `send_stream_audio.part.0` (previous build: 96), 48 for each emitted
span/begin callback, and 896 for `stream_task`. These are individual static
stack frames, not the total call-chain depth or a runtime high-water measurement.
The image and these build measurements are saved under
[`firmware/development/esp32c3-idf-6.1-r9a97-frame-router/`](../firmware/development/esp32c3-idf-6.1-r9a97-frame-router/).
Its only added active sdkconfig setting relative to `r9a97-codec-drain` is
`CONFIG_YORADIO_FRAME_ROUTER=y`. Subsequent hardware results are recorded below.

## Physical frame-router follow-up

The `idf61-frame-router` image was installed by native WebUI OTA on the C3
and tested with two finite, paced HTTP connections, without a MIME hint.
Each connection changes codec family while keeping the same play generation.
The original application and private settings were verified after restoration.

| Sequence | Result | Active health samples | Lowest sampled free heap | Lowest sampled largest block |
|---|---|---:|---:|---:|
| MP3 48 kHz stereo → HE-AAC 48 kHz stereo → MP3 48 kHz stereo | PASS | 54 | 31,096 B | 15,872 B |
| AAC-LC 48 kHz stereo → MP3 48 kHz stereo → HE-AACv2 44.1 kHz stereo | PASS | 56 | 40,456 B | 30,720 B |

Every expected decoded format was observed in sequence with consecutive
confirmation samples. Both cases reached `stream ended`, retained the boot
identity, and had no increase in allocation-failure or task-watchdog counters.
Available output counters stayed unchanged within the sampled active-playback
windows. Completion-queue drops did grow across the wider before/after interval
that includes startup and idle/EOF; these are not zero-overrun lifetime runs.
The server completed the exact 980,589 / 687,288-byte
HTTP bodies. Idle snapshots after EOF were 140,024 / 140,032 bytes free with
110,592-byte largest blocks; these snapshots are not a long-run leak test.

[Frozen transition evidence](../tests/results/esp32c3-stream-probe-20261013/frame-router-physical-01/)
contains the exact executed controller. After this run the reusable controller
gained an explicit full-server-delivery acceptance check; the saved run's
complete delivery was checked separately before archiving. Wi-Fi, playlist
and settings equality is recorded only as booleans, never private contents.

These tests exercise actual decoders and their PCM-derived status, but do not
capture PCM samples or analog output. They do not prove exact sample continuity,
absence of every possible underrun, HTTPS stability, recovery from corruption
or long-running memory stability. Keep `CONFIG_YORADIO_FRAME_ROUTER` off by
default until the remaining qualification work is complete.

The same image then passed the complete 14-case HTTP regression: MP3, FLAC,
Vorbis, Opus, AAC-LC, HE-AAC, HE-AACv2, both HE variants with an initial ID3,
unknown bytes, partial header, truncated ID3, `changing` and `implicit-sbr`.
The last two AAC transition cases had sampled heap/largest-block minima of
37,116 / 23,552 bytes and 32,404 / 21,504 bytes respectively. Positive cases
passed the new exact-server-delivery check as well as format/EOF checks.
Allocation/watchdog counts and boot identity stayed unchanged; output checks
apply to the active windows described above, not idle/startup lifetime totals.

[Frozen 14-case evidence](../tests/results/esp32c3-stream-probe-20261013/frame-router-regression-01/)
records the final restoration to `idf61-production-prefill1000`, stopped,
with unchanged Wi-Fi, playlist and settings. The candidate manifest now records
hardware testing, while `production_qualified` remains false. The combined
16 passing cases do not close the remaining PCM-boundary, Stop/replacement
under the new route, HTTPS, corruption-recovery or long-playback gates.

### Stop/replacement after a codec-family change

The same enabled image passed eight additional HTTP control cases: two cycles
of Stop and replacement after MP3 → HE-AAC and HE-AAC → MP3. ffprobe placed
the host pause inside the fourth packet of the second codec. Both decoded
formats had to be observed before the action, with the server still short of
that packet's end. This proves the control exercised a connection with an
incomplete delivered frame after a real transition, not a precise instruction
location or WRITING-lease state inside the firmware.

| Check | Observed result |
|---|---|
| Stop confirmed, then remained stopped | 4/4; 0.140–0.156 s |
| Replacement confirmed as HE-AACv2, then stayed stable | 4/4; 2.373–2.445 s including three confirming polls |
| Idle free heap, median of three snapshots | 140,036 B before; 140,092 B after |
| Idle largest block, same sampling | 110,592 B before and after |
| Idle task count | 16 before and after |
| Boot identity, allocation failures, task watchdog | Unchanged in each case |

Each case also passed the existing recovery bounds (at most 2,048 B free-heap
loss, 4,096 B largest-block loss, no task growth); observed median free heap
never fell below the initial median. Available output counters were unchanged
in replacement's two-second active windows. Idle and deliberate input stalls
are not counted as uninterrupted-audio tests. Two cycles are not a long-run
fragmentation or leak qualification.

[Frozen controls and recovery evidence](../tests/results/esp32c3-stream-probe-20261013/frame-router-controls-01/)
records all cases, server pauses, ffprobe version, timings and health snapshots.
The original `idf61-production-prefill1000` app was restored and stopped;
Wi-Fi, playlist and settings equality was verified. The remaining gates are
sample-exact PCM boundaries, HTTPS, longer playback/repeated changes and
parser confidence/recovery before changing the default.

### HTTPS frame-router matrix

The laboratory `idf61-router-tls-lab` image passed all 16 finite HTTPS cases:
MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC, HE-AACv2, both HE variants with initial
ID3, three negative prefix cases, and all four parameter/codec-transition
sequences. Every case negotiated TLS 1.2 with
`ECDHE-RSA-AES256-GCM-SHA384`. All 13 positive cases completed the exact server
body and reached the expected EOF; the three negative cases were explicitly
rejected as unknown audio. All expected transition formats were observed.

The laboratory configuration adds only the test CA enable/path to the enabled
HTTP router configuration. The full public root bundle, certificate verification
and 16,384-byte TLS input-record limit are retained. The extra CA is laboratory
trust only; this artifact is not a production release.

| HTTPS case | Active health samples | Lowest sampled free heap | Lowest sampled largest block |
|---|---:|---:|---:|
| FLAC level 8 | 2 | 59,952 B | 45,056 B |
| HE-AAC 48 kHz stereo | 2 | 36,728 B | 23,552 B |
| HE-AACv2 44.1 kHz stereo | 2 | 34,728 B | 23,552 B |
| AAC parameter changes (`changing`) | 76 | 33,912 B | 19,456 B |
| Implicit SBR change | 56 | 28,596 B | 18,432 B |
| MP3 → HE-AAC → MP3 | 54 | 27,188 B | 12,288 B |
| AAC-LC → MP3 → HE-AACv2 | 55 | 36,748 B | 23,552 B |

These are sampled active-playback values, not absolute transient minima or a
guarantee for other stations. No reset, allocation failure or task-watchdog
event occurred. The offline audit checks every retained active health sample,
requires available output counters and confirms that they stayed unchanged.
Completion-queue drops increased over the wider intervals including startup
and idle/EOF, as in HTTP; no lifetime-zero-overrun claim is made. After each
case the observed largest block returned to 110,592 B; post-case free heap
ranged from 139,744 to 140,052 B. This short matrix is not a long-run leak test.

[Frozen HTTPS evidence and reproducible offline audit](../tests/results/esp32c3-stream-probe-20261013/frame-router-tls-01/)
includes the exact executed controller, source hashes, TLS negotiation and
complete-body evidence, health snapshots and per-case summary. Run `python -B
audit.py` from that evidence directory to recheck the recorded gates without
contacting the board. The laboratory image is archived in
[`firmware/development/esp32c3-idf-6.1-r9a97-frame-router-tls-lab/`](../firmware/development/esp32c3-idf-6.1-r9a97-frame-router-tls-lab/).
The original `idf61-production-prefill1000` app was restored, playback stopped,
and Wi-Fi, playlist and settings equality verified in memory.

This closes the finite HTTPS matrix for this candidate. Remaining gates before
enabling the router by default include sample-exact PCM boundaries, longer
playback/repeated changes, multi-header confidence, bounded corruption recovery
and metadata-tail handling, plus conflicting MIME/container policies.

## Format references

- [ID3v2.4 header, size and footer](https://id3.org/id3v2.4.0-structure)
- [FLAC stream structure](https://www.rfc-editor.org/rfc/rfc9639.html#section-6)
- Existing ADTS validation in `native_aac_decoder.c` and the project's pinned
  decoder headers; this change does not claim support for raw AAC or new
  container formats.

[Evidence and source hashes](../tests/results/esp32c3-stream-probe-20261013/).
