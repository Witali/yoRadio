# ESP8266 Opus: playlist cache and PDM batch retry — 2026-09-10

Source: `de73cf0`. Experimental diagnostic build, **not production-qualified**.
No production defaults have changed. The existing PDM batch experiment is ON
in this image only; its default remains OFF.

## Firmware and deployment

- Application: 883760 bytes, SHA-256
  `F58758AF46091C147899F657C7E8FC988D2A7BBB84198662F2FDC20DB0F44159`.
- Build: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1
  -Variant esp8266-opus-batch-resume -EnableOpus -OpusWordAsm -Diagnostic
  -OpusStreamTest -WebAudioPause off -NoSpiffsCache -Pdm32Iram -SdkRxDiag
  -Pdm32Batch` (one command).
- CPU160/QIO40, mono PCM48k, GPIO3 I2S PDM32, 2 x 512-word DMA.
  Opus input 1024 bytes, scratch 6144 bytes, maximum packet 20 ms;
  MP3/AAC input 4096 bytes. ICDF word-table optimization is OFF here.
- Application-only OTA returned HTTP 200 OK, slot changed from 0x10000 to
  0x110000. No USB, Wi-Fi configuration, playlist or SPIFFS image upload.

## Playlist fix verified on the board

The gzip cache used to survive an Opus OFF -> ON firmware change because the
source CSV itself was unchanged. Its version now includes Opus capability.
The original source playlist is preserved; only the derived cache is rebuilt.

Before: identity response contained 522 rows, stale gzip only 511, without Opus.
After: both responses contain 522 rows, identical decoded SHA-256
`682d1da77d0cc3e454a497fdaa66078424127df0ffd0572e3db9bc39068bb948`.
Both include R2Rock and Nightwave Plaza.

The repository-root playlist currently has **11** explicitly named Opus rows,
not 10. Nine use HTTPS, two HTTP. Native ESP8266 still rejects HTTPS because
TLS is not implemented; removing the Opus filter does not implement TLS.
522 is a visibility count, not a claim that all those stations are playable.

Four additional plaintext entry URLs returned HTTP 200 and Ogg/OpusHead after
HTTP-only redirects: Dance Wave, Deutschlandfunk 24/64 and DLF Kultur 24.
See `results/http-alternatives.json`. This establishes transport/container
availability only, not packet-duration support or real-time board playback.
No URLs were changed: the shared root playlist retains HTTPS for other boards.

## Physical PDM batch comparison

Own deterministic SILK12 fixture, local HTTP server, 48-kHz output, rare health
sampling (two snapshots approximately 27 seconds apart). Network/Wi-Fi and
PDM are included. These are **not** decode-only CPU measurements.

| Image / interval | Board time | PCM time | New DMA underruns | Minimum sampled free heap |
|---|---:|---:|---:|---:|
| Batch OFF, steady 1 | 26983 ms | 27040 ms | 39 | 6576 B |
| Batch OFF, steady 2 | 27798 ms | 14640 ms | 1515 | 6400 B |
| Batch ON, steady 1 | 26972 ms | 27040 ms | 23 | 6752 B |
| Batch ON, steady 2 | 27174 ms | 27250.67 ms | 22 | 6748 B |

Every continuity run **failed** its zero-underrun gate. The second OFF run
includes RX timeout/reconnect (errno 116), then DECODER INIT ERROR; it is not
a clean CPU-speed comparison and is retained rather than discarded.
The earlier OFF startup run had a sample-rate transition and is also retained
as invalid for steady-state comparison. Batch ON had fewer misses in these
observations, but too few uncontrolled intervals establish neither causality
nor a precise speedup. No claim of fixed/no-gap audio or analog quality.

Batch ON audio stack watermark: 1720 bytes free out of 5120; free IRAM 80 bytes.
Allocator minimum later observed: 4744 bytes, distinct from the table's sampled
free heap. The baseline allocator minimum fell to 2044 bytes on failure.
SDK RX/TX error counters stayed zero in these samples; this does not exclude
RF/network delay. Health-request latency still reached about three seconds.

## Local regression tests

- 9/9 passed: playlist install, streaming, gzip cache, PDM batch build-profile
  and backend restrictions. Cache test executes actual C with Opus OFF -> ON
  -> OFF against an unchanged source CSV, including unchanged-cache reuse.
- 10/10 output-channel-dispatch tests passed, with LED OFF/ON and PDM32 batch
  OFF/ON, RCPDM, feedback and simple backends. Each variant checks 6480 blocks,
  1841169 output words and 5670 failure cases. PDM32 runs actual output code
  under ASan/UBSan with a mock DMA sink: PCM, bitstream, state and reservation
  boundaries match the reference. This does not test real ISR scheduling.

Original station 284 (Radio Caprice - Hard Bop) and stopped state restored after
testing. Local fixture server stopped. Raw reports, including failures, are
saved under `results/`. Uninterrupted Opus playback remains unfinished.
