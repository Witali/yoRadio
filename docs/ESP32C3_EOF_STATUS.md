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

- [FFmpeg ADTS header parser](https://ffmpeg.org/doxygen/7.1/adts__header_8c_source.html)
  reads `aac_frame_length` and the count of raw data blocks as frame boundaries.
  A complete ADTS frame is not a player-completion event: in these finite HTTP
  fixtures, body completion and decoder drain are separate stages. No ADTS
  syntax or HE-AAC profile handling was changed for this status fix.
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

## Physical verification, 2026-09-30

Both quiet builds use source `69410cd5`, ESP-IDF 6.0.2 and codec package 2.6.2
on the same ESP32-C3 SuperMini OLED board (160 MHz, 4 MiB flash, no PSRAM).
Deep sleep and profiling are disabled. Both Wi-Fi IRAM options remain disabled.
The exact images, matching bootloaders and configurations are retained under
`firmware/development/esp32c3-oled-native-{dio80,qio80}-eof/`.

The [retained results](../tests/results/esp32c3-eof-20260930/README.md) include
all attempts, technical REST observations, reference-decoder output and image
identities. EOF checks require decoded playback before completion, repeated
stopped REST samples with cleared PCM metadata, and a stopped WebSocket snapshot.

The first QIO matrix passed 21 of 22 EOF cases. An HTTP request failed during
the terminal observation of explicit-codec AAC-LC 320 kbit/s; the partial samples
and `URLError` remain in the initial report. A separate repeat of that fixture
passed with both AUTO and explicit AAC. All six HE/v2 EOF cases passed in the
initial run. Network drop/stall/503 recovery, redirect, jitter and WebSocket
reconnect also passed.

The DIO matrix passed all 22 EOF cases (eleven fixtures, AUTO and explicit
codec selection), including all six HE/v2 cases. Every successful case retained
the stopped status in both REST and a fresh WebSocket snapshot.
The five network fault/redirect/jitter checks and WebSocket reconnect passed
in DIO as well. The separate Stop/Play generation-replacement check passed.

All 15 DIO OTA/restoration cases passed on this exact image: ten invalid or
interrupted uploads, a round trip through both application slots, upload while
playing, slow upload and final restoration. Application ELF identity was checked
after boot; Wi-Fi, playlist and exposed settings were compared in memory and
remained unchanged. The final reboot resumed the saved station with decoded
AAC PCM at 44.1 kHz stereo. The board is left running the fixed DIO80 image
without deep sleep, also archived as `esp32c3-oled-native-production/app.bin`.

| Check | Result |
| --- | --- |
| DIO EOF, 11 fixtures × AUTO/explicit | 22/22 PASS |
| QIO initial EOF matrix | 21/22 PASS; one interrupted HTTP observation |
| QIO separate repeat of affected fixture | 2/2 PASS |
| Network faults/redirect/jitter | 5/5 PASS in each flash mode |
| WebSocket reconnect | PASS in each mode |
| Stop/Play generation replacement | PASS in DIO |
| Exact-image OTA and restoration | 15/15 PASS in DIO |
| C3/shared-WebUI Node tests | 151 PASS |
| Python acceptance infrastructure | 16 PASS |
| Production EOF and stream-format/Helix/framing host regressions | PASS |
| Firmware artifact consistency | 4 PASS |

No fresh CPU benchmark, optical OLED inspection or acoustic test is claimed
for this status correction. The terminal REST/WebSocket observations and
production-code state tests are retained independently of those measurements.

The HE/v2 board observations still show AAC-core fallback. Their passing EOF
status must not be described as successful full-rate SBR/PS playback. The six
full-profile FFmpeg/FDK references above are host results, not board results.

After installing the DIO application and its matching bootloader, the first
watchdog reset returned USB but did not make HTTP available within the helper's
25-second limit. One further watchdog reset returned HTTP successfully and
verified the exact application identity. This observation is retained separately
from EOF results; it is not evidence of a causal link between Wi-Fi and flash mode.

Only the bootloader and active application partition were written over USB.
The clean public `full.bin` was packaged from build outputs and was not flashed
over the user's configuration. The full QIO qualification gate remains separate;
the production default stays DIO 80 MHz.
