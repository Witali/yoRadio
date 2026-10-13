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
below tests the same image; it is still not production-qualified. HTTPS
detection and watchdog-disabled deadline tests remain required. Cross-codec
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

## Format references

- [ID3v2.4 header, size and footer](https://id3.org/id3v2.4.0-structure)
- [FLAC stream structure](https://www.rfc-editor.org/rfc/rfc9639.html#section-6)
- Existing ADTS validation in `native_aac_decoder.c` and the project's pinned
  decoder headers; this change does not claim support for raw AAC or new
  container formats.

[Evidence and source hashes](../tests/results/esp32c3-stream-probe-20261013/).
