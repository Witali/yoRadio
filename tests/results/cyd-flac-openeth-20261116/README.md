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

Use the [matched FLAC profile](../../target/cyd_full_app_openeth_qemu/README.md)
with the [validated QEMU build profile](../cyd-pdm-static-rx-20261113/README.md).
The vendor decoder remains the default. Physical Wi-Fi, DAC timing and the
production watchdog under simultaneous network and display load remain open.
