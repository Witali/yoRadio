# HE-AACv2: ten-minute memory investigation

## Outcome

The physical ESP32-C3 completed **600.141 seconds** of continuous HE-AACv2
44.1 kHz stereo with concurrent WebUI polling. No captured decoder/allocation
error, watchdog or reboot occurred. The original load outcome is **FAIL:
progressive heap loss during playback**. Stop recovery and runtime checks pass.
CPU percentage is informational, as requested on 7 October.

The full RX ownership capture is **rejected**: snapshot 128 has a merged,
truncated header/block line. The missing fields are not reconstructed and the
damaged snapshot is not discarded to manufacture a complete capture. CPU,
decoder, REST and post-Stop measurements remain independently available.

The user shortened the experiment from thirty to ten minutes. The preliminary
run was interrupted; its last saved checkpoint contains 77.125 seconds of
playback and remains explicitly incomplete. A fresh ten-minute run performed
all cleanup and restoration checks. Neither run satisfies the one-hour soak
criterion, and no physical audio waveform was captured.

## Configuration

- Awake, output task priority 8, decoder 7, stream 5; four 512-frame DMA blocks.
- Same full-rate AAC configuration and codec archives as `esp32c3-output-first`.
- The only sdkconfig change is `CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y`.
  Pipeline wait profiling remains disabled; network heap profiling remains on.
- Diagnostic BSS is 30,016 bytes versus 29,464 bytes: **552 additional bytes**.
- ELF SHA-256: `c043b4fe387aa33bbba590e05310a958580493e183ee7ee48ca5efd299290125`.
- The local server repeats the known ADTS fixture at the existing 1.02 pacing
  ratio, with a 100 ms delay between WebUI requests. Backpressure is expected;
  a host socket write is not a measurement of bytes consumed by the decoder.

## Measurements

The steady-state CPU/decoder window excludes the first ten seconds. Playback
heap endpoints are medians of the first/last three CPU samples. Idle values
are the measured settled checkpoints before playback and after Stop.

| Measurement | Result |
| --- | ---: |
| Status samples | 3,165 |
| CPU samples / decoder windows | 116 / 118 |
| Mean / peak CPU busy | 68.77% / 70.4% |
| Decoder time / decoded audio time | 49.51% |
| Decoded audio / wall time | 1.00160 |
| Initial / final playback free heap | 43,928 / 24,508 B |
| Minimum playback free heap | 20,952 B |
| Initial / final largest free block | 32,768 / 12,800 B |
| Minimum largest free block | 4,608 B |
| Maximum HTTP response | 391 ms |
| Minimum RSSI | -68 dBm |
| Idle free heap before / after Stop | 147,220 / 147,212 B |
| Idle largest block before / after Stop | 114,688 / 114,688 B |
| Idle task count before / after Stop | 17 / 17 |

The idle heap median differs by only **8 bytes**, and the largest block returns
fully. This distinguishes active allocation pressure from a large persistent
post-Stop leak. It does not prove every allocation has identical lifetime.

Valid RX observations show buffers accumulating while active heap decreases;
this directly establishes retained network allocations. However, the rejected
full capture cannot assign all heap movement to RX or establish a complete
time series. Logical TCP receive credit, allocated packet storage and allocator
headers are different quantities; asynchronous snapshots must not be subtracted
as if they were one simultaneous measurement.

The two independently validated **post-Stop** owner snapshots (180 and 181)
contain zero live RX owners and equal allocation/free counts. Their validation
does not repair the rejected full capture. The raw damaged line and all failed
checks are retained.

Real-time decoder progress and a continuously active REST status do not count
exact DMA underruns or missing output samples. This run therefore does not
certify gap-free sound, nor qualify the diagnostic firmware for production.

## Restoration, evidence and next work

Both OTA transitions pass, including preservation of Wi-Fi, playlist and other
settings using in-memory comparisons. The ordinary priority-8 image was restored
and verified playing AAC 44.1 kHz stereo, with deep sleep disabled. No flash/NVS
erase was used. Its ELF SHA-256 begins `7f7c1cd4a59c`.

[Retained evidence](../tests/results/esp32c3-hev2-rx-owner-20261007/manifest.json)
includes the original reports, incomplete preliminary capture, rejected RX
trace, exact firmware/configuration/source identities, OTA results and replay
tests. The diagnostic image is saved in
`firmware/development/esp32c3-output-first-rx-owner/`.

```text
python tools/esp32c3_tests/stream_memory_study.py --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --firmware firmware/development/esp32c3-output-first-rx-owner/app.bin --case hev2-44100-stereo --seconds 600 --output NEW_DIRECTORY
python tools/esp32c3_tests/summarize_stream_memory.py NEW_DIRECTORY --output SUMMARY.json
python tests/test-stream-memory-summary.py
python tests/test-stream-memory-evidence.py
```

Next: reduce diagnostic transport loss without hiding missing records, obtain
a complete RX-owner trace, then test a bounded receive-memory change against
the same stream and ordinary firmware. Keep the original memory failure.
Physical output continuity remains a separate requirement; reducing receive
buffers must not trade memory for audio gaps or break TLS/other codecs.
