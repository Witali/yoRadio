# ESP8266 AAC bounded PCM output — 2026-09-06

## Selected default

`YORADIO_ESP8266_AAC_BLOCK_OUTPUT=ON` and
`YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=512`.

The native mono build now allocates **1024 bytes**, not 4096 bytes, for AAC
PCM. Actual codec workspace falls from **9876 to 6804 bytes DRAM**, saving
**3072 bytes**. The existing 16384-byte IRAM coefficient/overlap arena and
two 512-word I2S-PDM DMA payloads are unchanged. Stereo builds need 2048
PCM bytes at this block size. No new task or full-frame scratch is added.

512 is the selected compromise for the current ESP8266/mono/PDM32 profile,
not a universal optimum for other processors or outputs. At 48 kHz, one
512-frame mono block fills one DMA payload. Smaller blocks allowed partial
handoffs and reduced queued audio coverage of the next long AAC transform.
32/64/128/256 remain available for experiments; OFF retains the full-frame
AAC bridge as an A/B control. Existing CMake caches need an explicit update.

## Implementation and invariants

- `AACDecode()` remains the legacy full-frame API. The new native AAC-LC
  `AACDecodeBlocks()` emits chronological, reusable PCM blocks after parsing
  a complete raw data block. SBR-enabled and non-native builds keep their
  original path.
- The four window sequences have equivalent indexed current/next-overlap
  formulas. Coefficients remain read-only during emission; an overlap word
  is replaced only after reading its contribution to current PCM.
- Both channels are retained through the inverse transform. Mono averages
  the separately clipped int16 L/R samples, exactly like the previous bridge.
  It does not discard a side channel or introduce a new downmix approximation.
- Two separate SCEs retain their coefficients in the existing two channel
  slots. Local helper indexing is restored by a scoped guard, including on
  errors. The final frame metadata is ready before the first callback.
- The consumer may modify PCM. Callback cancellation stops further output
  and clears partially updated overlap. Invalid capacities are rejected
  before parsing; truncated ADTS frames are rejected before the bit decoder.
- All coefficient/overlap IRAM access remains aligned 32-bit access. PCM
  is int16 in DRAM; it is not aliased onto IRAM or DMA-owned memory.
- PDM already writes directly into producer-owned DMA memory for all codecs.
  This change removes most of the *preceding AAC PCM* buffer, not another
  DMA copy. Playback DMA ownership and its neutral underrun policy are intact.
- Stage profiling excludes the output callback's DMA wait from the new
  synthesis stage. Whole decode-call timing can still include backpressure.

## Physical buffer-size comparison

Wemos D1 mini / ESP8266, COM8, CPU 160 MHz, QIO40, SDK v3.4/GCC 8.4, O3,
mono Helix AAC-LC, PDM32 at nominal 1.536 MHz. The retained stereo
48-kHz/320-kbit/s AAC fixture supplies one complete frame copied to RAM,
8 warm-up frames and 200 measured frames. Wi-Fi/WebUI are not started.
Physical-output tests use volume 128 and normalization OFF in RAM only;
saved settings, SPIFFS and the partition table are not written.

All output runs produce 4.266666 seconds of audio. Wall time includes output
waits and is not a CPU utilization measurement. Queued DMA data crosses the
measurement boundary, explaining wall times slightly below audio duration.

| PCM policy | Mono PCM bytes | Codec DRAM bytes | Physical wall, s | Neutral underruns | Partial handoffs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Previous stereo frame + mono downmix | 4096 | 9876 | 4.254142 | 0 | 0 |
| 32 frames | 64 | 5844 | 6.193784 | 1462 | 1038 |
| 64 frames | 128 | 5908 | 4.700555 | 340 | 172 |
| 128 frames | 256 | 6036 | 4.366126 | 84 | 36 |
| 256 frames | 512 | 6292 | 4.257972 | 3 | 0 |
| **512 frames, selected** | **1024** | **6804** | **4.254014** | **0** | **0** |

All cases reported zero FIFO-empty flags. MP3 remained at 8440 DRAM /
16384 IRAM bytes and had zero output underruns in these physical cases.
The physical benchmark task retained 1496 stack bytes; 50 create/switch
cycles returned heap to the initial value (delta 0).

Initial decode-only averages: full frame 17859 us; 32 = 18909 us;
64 = 18783 us; 128 = 18786 us; 256 = 18949 us; selected 512 = 18945 us.
The selected path takes about 6.1% longer per decode-only call (88.8% of
this frame's audio-time budget, compared with 83.7% previously). Sequential
window output has a CPU cost: do not describe this as a speed optimization.
This is a memory reduction with physical-output continuity retained for
the selected size. These short RAM tests do not prove uninterrupted live
streaming or resolve the separate Wi-Fi/WebUI instability.

## Regression coverage

- Exact versus SSO arithmetic: 1280 synthetic vectors each, all four window
  sequences and both shapes, distinct L/R windows, mono/stereo, every size.
  PCM **and next overlap** match the previous functions; coefficients and
  allocation guards remain unchanged.
- Complete ADTS streams at 22050/44100/48000 Hz, mono/stereo, deterministic
  transients and 320-kbit/s noise. Every block size matches legacy PCM,
  including the previous mono rounding. The sink overwrites each PCM block.
- Cancellation at every block boundary, two-SCE stereo elements, reset,
  invalid capacity, null callback and each truncated length of a test frame.
- Direct PDM equivalence also covers 256/512-frame chunks, six input rates,
  normalization on/off, mono/stereo, PDM32/RCPDM/PDM128 and DMA ownership.

## Reproduce

Run from the repository root with the existing local ESP8266 SDK/tools:

```powershell
./tools/esp8266_audio_profile/run_aac_block_matrix.ps1 -Port COM8
./tools/esp8266_audio_profile/run_aac_block_matrix.ps1 -Port COM8 -PhysicalOutput
node --test tests/*.test.js
```

The script builds, saves diagnostic images under `firmware/development/`,
flashes **app0 only at 0x10000**, resets with RTS and captures UART TX.
It sends no application UART bytes and changes no computer Wi-Fi settings.
Its default build directory reuses the documented production sdkconfig;
inspect that configuration before interpreting timings from a different
machine. **Restore the ordinary firmware after the matrix.**
