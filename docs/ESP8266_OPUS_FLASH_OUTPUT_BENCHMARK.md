# Opus: flash → PCM → physical PDM/DMA, 2026-09-10

## Method and limits

Source `391a85b`, CPU160/QIO40, fixed-point Opus, WordASM/ICDF-word,
standard PDM32 IRAM/batch, GPIO3, two 512-word physical DMA buffers.
The two builds differ only in the producer publication limit: 512 or 128
words. No change to the physical buffers, PCM algorithm or PDM algorithm.

Five own tone/noise fixtures, 12 × 20-ms packets, one warmup round and 100
measured rounds: 24 seconds of PCM per case. The decoder resets every round;
DMA does not reset between measured rounds. This tests repeated short
fixtures, not 24 seconds of distinct continuous decoder history. Packets come
from flash; no audio TCP, Ogg or ICY is involved. Wi-Fi, WebUI, OTA and their
interruptions remain active. The observer polls every 30 seconds. These are
one run per build, not a statistically qualified A/B speed comparison.

All five reference PCM fingerprints match in both builds. The check happens
before normalization/output changes PCM. No new intermediate PCM buffer.

`pipeline_task_us / 24 s` is full-path task CPU budget, including flash copy,
hash, normalization/PDM and ISR charged to the task. It is **not decoder-only
CPU**. Decode/output wall times include preemption; output also includes DMA
waits. Raw decoder-only CPU is recorded separately in
[the arithmetic audit](ESP8266_OPUS_FIXED_POINT.md).

## Results

| Input fixture | CPU budget, 512 | CPU budget, 128 | DMA misses, 512 / 128 | PCM / elapsed, 512 / 128 |
|---|---:|---:|---:|---:|
| SILK mono12 | 70.84% | 72.12% | 0 / 1 | 1.0030 / 1.0029 |
| Hybrid mono24 | 104.92% | 106.51% | 2096 / 2626 | 0.8984 / 0.8753 |
| CELT stereo64 → mono | 86.48% | 87.80% | 148 / 123 | 0.9948 / 0.9962 |
| CELT stereo128 → mono | 107.94% | 108.06% | 2749 / 2860 | 0.8701 / 0.8655 |
| CELT stereo510 → mono | 189.97% | 179.22% | 20642 / 15948 | 0.4672 / 0.5319 |

Only SILK12/512 passed the strict digital continuity gate in this single run:
24 seconds submitted, 2400 DMA EOFs, no misses, no latched FIFO-empty event.
Every other case failed. FIFO-empty was zero in every case: the DMA silence
fallback can keep hardware fed while missing real audio. Thus FIFO-empty=0
alone is not a continuity test. Miss counts are descriptor fallback events,
not distinct audible glitches or packet losses; 128-word partial publication
also changes descriptor lengths, so counts alone are not an A/B speed metric.

CELT64 has average CPU headroom but still misses output deadlines. Hybrid24
and CELT128 exceed the average budget even without the audio network. The
510-kbit cases are overloaded and have very different observed preemption;
their difference does not establish that the 128-word change accelerates
the codec. No reliable overall benefit for 128 words: keep default512.

Memory minima are CAP8 **free DRAM**, sampled during each case:

| Fixture | 512 / 128, bytes |
|---|---:|
| SILK12 | 9712 / 9212 |
| Hybrid24 | 10152 / 6828 |
| CELT64 | 7512 / 9992 |
| CELT128 | 3808 / 780 |
| CELT510 | 380 / 10152 |

These minima include system/network allocations, not just codec ownership.
512 run global minimum was 208 bytes; this fails the RAM safety gate.
After benchmark cleanup DRAM was 26852 in both runs. This is not proof of
either a memory leak or leak freedom; investigate transient allocations in
overloaded runs separately. Minimum reported lifetime audio-stack watermark
was 1660 bytes of the 5120-byte stack.

The benchmark adds runtime-statistics kernel code/storage: compared with
the live profile, `.iram0.text` is 0x5974 rather than 0x5940,
`.iram0.bss` 0xfcc rather than 0xfc8, `.dram0.bss` 0x49f0 rather than 0x4848.
Do not describe this diagnostic image as identical in RAM to production.

## Artifacts and reproduction

- [512 image, manifest and raw report](../firmware/development/esp8266-opus-flash-output512/CHANGELOG.md): 912512 bytes.
- [128 image, manifest and raw report](../firmware/development/esp8266-opus-flash-output128/CHANGELOG.md): 912560 bytes.

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-flash-output512 -Diagnostic -EnableOpus -OpusBenchmark -OpusBenchmarkOutput -OpusWordAsm -OpusIcdfFlashWord -NoSpiffsCache -Pdm32Iram -Pdm32Batch -Pdm32LoanWords 512 -WebAudioPause off -SdkRxDiag
node tools/esp8266_opus_profile/run_board.cjs --interval-ms 30000 --output .build/opus-flash512-run1.json
```

Build does not flash; use the documented app-only OTA workflow. The runner
returns failure while retaining the complete report if any case fails.
Repeat with a fresh variant and loan128. Do not restart a still-running
benchmark on an observation timeout; use `--observe`.

Host tests passed for actual raw/output benchmark allocation and cleanup,
PCM hash-before-mutation, output cancellation/failure, oversized PCM, retained
DMA and FIFO failures, actual build gates, and strict report analysis.

## Live follow-up and decision

Returned via OTA to the live diagnostic `esp8266-opus-stage-wall-icdf`
(884864 bytes), default512, without benchmark runtime counters or fixture
storage. SPIFFS, Wi-Fi and saved playlist were not uploaded.

The HTTP 56-kbit Opus station `http://secure.live-streams.nl/opus.opus` started
with RSSI -56 dBm and 8016 free heap, but the subsequent 25-second observation
failed: first health request timed out; the second showed transport timeout
errno116, no recent PCM and accumulated underruns. This is **not** a passing
live-radio interval and cannot provide a valid two-snapshot timing breakdown.
Playback was then explicitly stopped. Raw observations are retained with
the 128 artifact as `live-followup.json`.

The goal of gap-free real Opus radio remains open. Next priorities are
decoder-stage profiling and reducing actual compute/flash-access cost,
not hiding underruns or loosening the memory reserve.
