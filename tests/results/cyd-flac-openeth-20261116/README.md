# CYD FLAC over TLS with TFT, continuous DAC and WebUI

Both diagnostic images use ESP-IDF 6.0.2, continuous DAC with the DMA wait
fix, dynamic Mbed TLS buffers, TCP receive window and mailbox 8640/8, and a
30-second task watchdog. OpenETH replaces Wi-Fi on the emulator. The two
generated SDK configurations differ only in the FLAC decoder selection.

The tracked level-8 calibration stream contains 528,000 stereo PCM16 frames
at 48 kHz and uses 4,608-sample blocks. The official Xiph FLAC 1.5.0 decoder
and FFmpeg independently produced the STREAMINFO MD5
`7e7636f603770391913d2d7521b969ea`. The application probe checks the
interleaved PCM accepted by the output task against that value.
[Xiph reference decoder](https://github.com/xiph/flac/releases/tag/1.5.0).
[STREAMINFO and sample order](https://www.rfc-editor.org/rfc/rfc9639.html#section-8.2).

| Decoder | Result | Minimum free heap |
| --- | --- | ---: |
| Espressif | One failed 18,432-byte allocation. The vendor decoder reported frame error 8 and eventually returned `ESP_AUDIO_ERR_FAIL`. Zero PCM frames reached the output. | 7,324 B |
| Transferred custom FLAC | Exact 528,000-frame flush and matching PCM MD5. WebUI served the same complete 13,588-byte asset before playback, during playback and after EOF. | 47,276 B |

The custom run received the entire 1,771,852-byte stream as 108 full
16,384-byte TLS application records and the 2,380-byte tail. It reported no
allocation failures, output errors, short writes, watchdog events or OpenETH
allocation waits. The vendor heap minimum is from a failed run that never
activated DAC playback. These measurements describe the two observed
workloads. The [observations](observed.json) include config and image hashes,
output counters, PCM checks and stack watermarks.

## Espressif block and EOF controls

Xiph FLAC re-encoded the identical PCM with two smaller block sizes. With
4,096 samples per block, the original Espressif image recorded a failed
16,384-byte request and produced zero PCM. With 2,048 samples it made
every allocation and reported normal EOF, but emitted only the first
526,336 frames. Their MD5 matched the corresponding Xiph PCM prefix. The
omitted 1,664 frames form the last encoded block.

The [decoder task](../../../idf/esp32-cyd2usb-native/main/audio_service.c)
now retains one final byte for the vendor FLAC path so the parser receives
actual input with the EOS flag. On the same 2,048-block stream it accepted all
528,000 PCM frames with the exact full MD5, zero allocation failures, and
working WebUI after EOF. Six ASan/UBSan lifecycle profiles passed, including
a FLAC regression that requires non-empty EOS after one-byte inputs. The
larger block allocation failures remain open.

To reproduce the controls, decode the tracked fixture to signed
little-endian raw PCM with Xiph FLAC 1.5.0. Encode it with
`--verify -8 --blocksize=2048 --force-raw-format --endian=little --sign=signed --channels=2 --bps=16 --sample-rate=48000`.
Use `--blocksize=4096` for the other control. Keep the new FLAC under
`.build` and run [run-block-control.py](run-block-control.py) from the
repository root with the FLAC path as the first argument, followed by the
full application runner arguments. It requires the original PCM length
and MD5 from the replacement fixture.

## Production watchdog and allocation traceback

The custom decoder passed the same complete TLS workload twice with the
production five-second task watchdog, both idle tasks subscribed, and
the 300 ms interrupt watchdog. Compared with the 30-second custom fixture,
the generated SDK configuration changed only the task watchdog timeout.
Both runs reached the full PCM MD5 and served WebUI after EOF, with zero
watchdog events, allocation failures or output faults. Minimum free heap
was 47,268 and 47,276 bytes. The smallest observed stack watermarks were
1,620 bytes for the stream task, 11,708 for decode, 2,932 for output and
1,228 for HTTP. [Watchdog configuration](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/wdts.html).

A separate Espressif build used a temporary allocation-failure probe.
The traceback and matching link map locate the failed 18,448-byte request
in `stream_decoder.c.obj` inside `read_frame_`, which called
`media_lib_module_malloc`. That size is consistent with 4,608 32-bit
samples plus four padding words in the reference decoder. A trial with a
1 KiB initial application PCM buffer still failed a separate 18,432-byte
request from `FLAC__memory_alloc_aligned_int32_array`. The trial was
discarded. [Xiph reference allocation layout](https://github.com/xiph/flac/blob/1.5.0/src/libFLAC/stream_decoder.c#L1459).

See [watchdog and heap evidence](watchdog-and-heap.json) for the two passes
and the allocation call sites. Use the
[matched FLAC profile](../../target/cyd_full_app_openeth_qemu/README.md)
with the [validated QEMU build profile](../cyd-pdm-static-rx-20261113/README.md)
and `CONFIG_ESP_TASK_WDT_TIMEOUT_S=5` to repeat the production watchdog runs.
The vendor decoder remains the default. The five-second watchdog result
covers custom FLAC over OpenETH. Physical Wi-Fi and physical audio output
tests remain open.

## Startup watchdog with the other output profiles

PDM and legacy DAC first hit the five-second watchdog before Play. The ELF
stacks located CPU0 in the synchronous SPIFFS mount scan while its idle
task waited. At idle priority the main task completed startup in 8.706 and
8.722 seconds of guest time respectively, without a watchdog event. A
continuous DAC control then exposed the same scheduling problem during
the playlist-index load in the network task.

The [CYD startup code](../../../idf/esp32-cyd2usb-native/main/app_main.c)
now uses idle priority around the SPIFFS mount and radio initialization,
then restores the caller's priority on success and failure. The 31-group
host suite passed under ASan/UBSan and detected all 13 semantic controls,
including omitting either priority change or its restoration. The
separate early-MPI startup suite passed. [ESP-IDF time slicing](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/system/freertos_idf.html#time-slicing).

A local OpenETH capture contained a TCP acknowledgment for a timed-out
`/script.js` request. The preceding asset response started 7.88 seconds
after the connection began, measured on QEMU's virtual clock. The runner
now allows 25 seconds per socket I/O operation on that SPIFFS read and
requires the exact body, same-generation playback progress and a separate
post-EOF read. JSON API requests have an eight-second timeout.

## Matched full-application results on all three outputs

Three builds from the corrected source passed with the production
five-second task watchdog and 300 ms interrupt watchdog. The generated
SDK configurations differ only in their audio-output selection.

| Output | Minimum free heap | Lowest sampled stream/decode/output/HTTP stack watermarks |
| --- | ---: | --- |
| PDM | 47,116 B | 1,588 / 11,788 / 2,804 / 1,216 B |
| Continuous DAC | 47,304 B | 1,620 / 11,708 / 2,948 / 1,228 B |
| Legacy DAC | 46,464 B | 1,620 / 11,788 / 2,868 / 1,228 B |

Each run received all 108 full TLS records and the final record, accepted
528,000 stereo PCM16 frames with the exact Xiph MD5, and read the byte-exact
13,588-byte WebUI asset during playback and after EOF. All three reported
zero allocation failures, driver errors, short writes and watchdog events.
PDM reported 11 completion-queue drops in the driver telemetry and accepted
all 1,058,176 expected driver bytes. The legacy test used the emulator's
96 kHz DAC clock ceiling.

[Startup and packet evidence](startup-matrix.json).
[Full playback matrix](output-matrix.json).
