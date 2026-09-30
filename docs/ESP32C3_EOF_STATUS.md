# ESP32-C3: playback status after EOF

## Problem and correction

The HTTP task used to enqueue an end-of-stream packet and immediately publish
`audio=false`. The decoder could still have compressed data queued. Its next
format callback set `audio=true` again, leaving REST, WebSocket and the OLED
in a playing state after a finite file ended. HE-AAC was one affected format;
the race also occurred with other decoders.

Completion now travels in order through both queues:

```text
HTTP data → encoded end marker → remaining decoder output → PCM end marker
                                                               ↓
                                                    publish "stream ended"
```

The output task consumes the marker after preceding PCM packets have been
handed to the audio driver. It clears stream parameters using the existing
shared state API, so REST, WebSocket and OLED agree. A generation check stops
an old stream's completion from ending a newly selected station. A decoder
error remains an error, rather than being overwritten by normal EOF. Network
read/stall errors carry their own terminal reason through the same queues.

This change concerns playback status. It does not change AAC profile detection,
sample rates, SBR/PS support, PCM synthesis, or the known full-radio SBR memory
limit. It does not claim measurement of the final physical DAC/PDM sample.

## Documentation and decoder references

- [HTTP/1.1, RFC 9112 §6.3 and §8](https://www.rfc-editor.org/rfc/rfc9112.html#name-message-body-length)
  defines body completion separately from an incomplete response. The HTTP
  reader retains its completeness/watchdog checks; a temporary lack of data
  is not treated as clean EOF.
- [Espressif simple decoder API](https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_codec/include/simple_dec/esp_audio_simple_dec.h)
  supplies an `eos` indication to flush parser data. The locally installed
  codec v2.6.2 header was checked as well. Decoder output and its format callback
  must finish before the player publishes its terminal state.
- [FFmpeg send/receive API](https://ffmpeg.org/doxygen/7.1/group__lavc__encdec.html)
  distinguishes input exhaustion from decoder drain completion. Buffered
  frames can still be returned after the final input packet.
- [FDK AAC v2.0.3 decoder API](https://github.com/mstorsjo/fdk-aac/blob/v2.0.3/libAACdec/include/aacdecoder_lib.h)
  documents input underflow separately from filterbank flushing. The reference
  driver stops supplying data at actual file EOF and flushes only the reported
  filterbank delay. It never treats repeated input-underflow responses as
  endless continued playback.

## Regression tests

`tests/run-esp32c3-eof.py` compiles the production packet/state functions and the
actual producer termination/output marker branches. Platform I/O is mocked to
force the problematic ordering deterministically:

- HTTP EOF arrives before a delayed HE-AAC format callback and two PCM packets.
- The playing state survives until those queued PCM packets are consumed.
- Completion clears parameters and retains the terminal status.
- Read errors, decoder failures, empty input, a new Play racing the old marker,
  and cancellation while the output queue is full are handled separately.
- PCM remains word-aligned, including when packet memory is reused.

The stream-format/real Helix/framing regressions also remain applicable. The
dedicated physical `--suite eof` checks decoded playback, then sustained
`stream ended` state with cleared PCM metadata and a stopped WebSocket snapshot.
It is separate from full-profile acceptance: a correct EOF result on an AAC
core fallback is **not** a passing full-rate HE-AAC result.

```powershell
python tools/esp32c3_tests/run.py --board http://BOARD_IP --host PC_LAN_IP --suite eof --output .build/c3-eof
```

### Independent complete-file references

FFmpeg 8.1.1 and unmodified FDK AAC v2.0.3
(`716f4394641d53f0d79c9ddac3fa93b03a49f278`) decoded the six original synthetic
AAC fixtures. FDK was fed in 1-, 7-, 257- and 2,048-byte chunks. All layouts and
decoded frame sample counts agreed with FFmpeg before FDK's explicit delay
flush. Each FDK run then successfully flushed its reported filterbank delay
in two additional calls. This is not a claim of bit-identical PCM between
different decoders or equal decoder delay conventions.

| Fixture | Rate / channels | Decoded samples per channel |
| --- | --- | ---: |
| AAC-LC | 44,100 Hz / 2 | 24,576 |
| AAC-LC | 22,050 Hz / 1 | 13,312 |
| AAC-LC | 48,000 Hz / 2 | 26,624 |
| HE-AAC | 44,100 Hz / 2 | 28,672 |
| HE-AAC | 48,000 Hz / 2 | 30,720 |
| HE-AAC v2 | 44,100 Hz / 2 | 30,720 |

Reproduce on a host with FFmpeg/FFprobe and a C++ compiler. Build
`tests/native/aac_eof_reference.cpp` against the unmodified, pinned FDK library
and its `lib*/include` directories, then run:

```sh
python3 tests/run-esp32c3-eof.py
python3 tests/run-esp32c3-stream-format.py
python3 tools/esp32c3_tests/reference_eof.py --fdk-reference /path/to/fdk-reference --output .build/eof-reference.json
```

Reference decoding validates the fixtures and EOF/drain distinction. Physical
firmware status must still pass the separate board test; reference results do
not replace it.
