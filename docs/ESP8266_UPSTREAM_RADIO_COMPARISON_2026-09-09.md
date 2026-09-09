# ESP8266 web-radio: upstream source and memory comparison

Date: 2026-09-09. Baseline: yoRadio native production, not the Arduino or
KaRadio-derived variants in this repository.

## Scope and confidence

Downloaded five public project repositories and the actual ESP8266Audio fork
referenced by MrDIY. Copies are under
`.build/upstream-radio-review-2026-09-09/`, already excluded by `/.build/`.
No upstream build scripts were executed, no firmware was flashed, and no
Wi-Fi settings, serial ports or board state were changed.

This is a source/layout comparison, **not a new on-device speed or total-heap
benchmark of the reviewed projects**. Distinguish:

- Exact source constants and 32-bit Xtensa compiler `sizeof` measurements.
- Existing measured yoRadio codec allocation and physical RAM results.
- Historical upstream artifacts: their build settings need not match current
  source or each other.
- Unknown whole-application runtime RAM for upstream projects. Decoder
  payload, image size and static BSS are not substitutes for that measurement.

The working tree contained unrelated changes. They were not included in this
review's commit. Native audio/web sources match the saved production manifest.

## Pinned repositories

| Local directory | Repository | Commit |
| --- | --- | --- |
| esp8266audio | [ESP8266Audio](https://github.com/earlephilhower/ESP8266Audio) | `10d929ac01436dfe8856e0a06fd9ec35a848c6e2` |
| renat-radio | [renat2985/esp8266-Radio](https://github.com/renat2985/esp8266-Radio) | `b809a172ca44a1b10f2d810bd910c678f78f392d` |
| mrdiy-notifier | [MrDiy-Audio-Notifier](https://github.com/schmurtzm/MrDiy-Audio-Notifier) | `3bf5057a81d38835e9a081825832e65f23b1fc34` |
| mrdiy-audio | [MrDIY's configured dependency](https://github.com/schmurtzm/ESP8266Audio) | `3d851560edf5a9234d009eb69a80eb5012d5d59a` |
| myradio | [lechiJb/myRadio](https://github.com/lechiJb/myRadio) | `5195a17df5400e0afbe395e7c06c5ecc6ac7a780` |
| espressif-mp3 | [ESP8266_MP3_DECODER](https://github.com/espressif/ESP8266_MP3_DECODER) | `7552a62d425598d64ebc255d32fa4f20220e92f6` |

yoRadio checkout: `31de0e9e513a12275e1ffb69b7df6ceb08af6f6c`.
Production artifact:
`firmware/development/esp8266-i2s-pdm-production/app.bin`,
760080 bytes, SHA-256
`45D5A1A7A7FFFA937F3DBCCA2FB6DD824AF2E0A46BFC455532F068416D757227`.
The matching build-directory BIN has the same SHA-256; its ELF/map were used.
The artifact manifest records source revision `43e558a`; later commits include
reports/tests. This review does not relabel it as a newly compiled image.

## 1. Compressed input buffering

All numbers are bytes. These are **application compressed-data buffers**,
excluding lwIP's TCP receive window, packet buffers, HTTP/ICY scratch and MP3
bit reservoir. The latter is decoder state, not a queue of future audio.

| Profile | Additional stream FIFO | Decoder input | Combined capacity | Relative to native |
| --- | ---: | ---: | ---: | ---: |
| yoRadio native MP3/AAC | 0 | 1536 | **1536** | 1.00x |
| ESP8266Audio WebRadio MP3 | 5120 | 1536 | **6656** | 4.33x |
| ESP8266Audio WebRadio AAC-LC | 5120 | 1600 | **6720** | 4.38x |
| renat Radio MP3 | 4096 | 1536 | **5632** | 3.67x |
| MrDIY MP3, as checked out | **0**, despite a 4096 constant | 1536 | **1536** | 1.00x |
| MrDIY AAC-LC, as checked out | **0** | 1600 | **1600** | 1.04x |
| myRadio default, internal RAM | 1850 | 2106 | **3956** | 2.58x |
| Espressif default, external SPI RAM | **131072 external** | 2106 | **133178** | 86.70x, not a bare-board comparison |
| Espressif with FAKE_SPI_BUFF | 1850 | 2106 | **3956** | 2.58x |

WebRadio's 1536/1600-byte input is already included inside its decoder arena;
do not add it again when calculating RAM consumption below. Arduino audio
dependency versions are not pinned by renat; its 1536-byte decoder input here
uses the inspected ESP8266Audio implementation, not a claim about its binary.

Nominal full-buffer coverage, `bytes * 8 / bitrate`:

| Combined compressed bytes | At 128 kbit/s | At 320 kbit/s |
| ---: | ---: | ---: |
| 1536 | 96 ms | 38.4 ms |
| 3956 | 247.25 ms | 98.9 ms |
| 5632 | 352 ms | 140.8 ms |
| 6656 | 416 ms | 166.4 ms |
| 133178, mostly external RAM | 8.324 s | 3.329 s |

These are upper-bound capacity estimates, not guaranteed outage tolerance:
fill level, frame boundaries, scheduling and VBR matter. A larger FIFO cannot
fix a decoder/output path whose average production rate is below realtime.

Native's 16-KiB IRAM arena is **not** a 16-KiB compressed-input ring.
Its ordinary build has `YORADIO_ESP8266_KARADIO_PIPELINE=OFF`.
Read batch 1024, TCP receive window 2440 and input capacity 1536 are three
different quantities. Existing HTTP/ICY shared scratch is not another
independently filled audio queue.

Evidence:

- Native `components/helix_codecs/codec_bridge.cpp`: `kInputBytes`;
  `main/audio_service.c`; production CMakeCache and sdkconfig.
- WebRadio `examples/WebRadio/WebRadio.ino`: `preallocateBufferSize`;
  `src/AudioGeneratorMP3.h`, `src/AudioGeneratorAAC.h`.
- renat `Radio.ino`: `new AudioFileSourceBuffer(file, 4096)`.
- MrDIY `src/main.cpp`: `preallocateBuffer = NULL`, never assigned memory;
  passed to the external-buffer constructor. Its actual fork's
  `AudioFileSourceBuffer.cpp` keeps the NULL and `read()` falls through to
  `src->read()`; `fill()` does nothing. Thus 4096 is not allocated.
- Legacy projects `mp3/user/spiram_fifo.c`, `playerconfig.h`,
  `mp3/include/spiram.h`; `READBUFSZ=2106` in decoder task source.

## 2. Decoder RAM: actual structures, not comments

Reproducible Xtensa GCC 8.4.0 object-symbol measurements are in
[sizeof.json](benchmarks/esp8266-upstream-comparison-2026-09-09/sizeof.json).

| Decoder/layout | DRAM payload | Separate IRAM data reservation | Included |
| --- | ---: | ---: | --- |
| Native Helix MP3 mono/SSO | **8440** | **16384** | Codec/bridge state, input, 64-byte PCM block |
| Native Helix AAC-LC mono/block512 | **6804** | **16384** | Codec/bridge state, input, 1024-byte PCM block |
| ESP8266Audio libmad | **29184**, or **29192** in the aligned arena | No explicit dedicated arena in reviewed caller | Input 1536 + stream 2628 + frame 20784 + synth 4236 |
| ESP8266Audio AAC-LC | **26352** | No explicit dedicated arena in reviewed caller | Input 1600 + PCM 4096 + AACDecInfo 96 + PSInfoBase 20560 |
| Legacy Espressif/myRadio libmad | **at least 20615**, excluding input and stack | None explicitly reserved for data | Heap structs 13440 + static reservoir 2567 + static overlap 4608 |

Do not compare the last row's `mad_stream + mad_frame + mad_synth` alone
(13440 bytes) with a complete modern arena. The old code hides substantial
state in static globals and on the task stack. In particular:
`xr[2][576]` is 4608 bytes and short-block reorder scratch is another
2304 bytes. These already consume part of its **8400-byte decoder task
stack**, not additional memory to add on top of that stack.

Legacy task-stack arguments are words, not bytes: the downloaded
`third_party/freertos/tasks.c` multiplies depth by `sizeof(portSTACK_TYPE)`,
and that type is 32-bit. Decoder 2100 -> 8400 bytes; network reader is
920 bytes in Espressif and 800 in myRadio. Their transient connection tasks
and system tasks are separate.

Native code uses a 4096-byte audio stack, 5120-byte WebUI stack and 3072-byte
main stack. There is no separate input-button task. These are actual active
allocations/settings, not unused legacy `BOARD_TASK_STACK_AUDIO` constants.
Stacks are not included in the first table's decoder workspace.

Native numbers are the retained physical allocation measurements in
[PCM32/direct DMA](ESP8266_PCM32_DIRECT_DMA.md) and
[AAC block output](ESP8266_AAC_PCM_BLOCKS.md), cross-checked with the current
build configuration. Allocator metadata and other application objects are
not included in decoder payload. The IRAM reservation is real memory use,
not a free saving: total native codec reservations are 24824 bytes MP3 and
23188 bytes AAC. The large DRAM saving partly comes from moving aligned
32-bit state into IRAM, not deleting it.

ESP8266Audio WebRadio reserves the same 29192-byte arena even for AAC and
while stopped; it also keeps its 5120-byte stream buffer. Thus **34312 bytes
are reserved before DMA, wrapper objects, HTTP/Wi-Fi and stack**. Renat and
MrDIY allocate decoder structures individually; actual malloc overhead adds
to their payload. Their whole heap is not measured here.

The old ESP8266Audio `README.ESP8266` mentions approximately 34 KB heap and
transient allocations. Current source has the large scratch arrays embedded
in `mad_frame`; the compiler probe is the basis for this comparison, not
that historical estimate.

## 3. PCM and DMA buffering

| Profile | Intermediate PCM | DMA payload |
| --- | --- | ---: |
| Native MP3 mono | 32 frames / 64 bytes | 2 x 512 words x 4 = **4096 bytes** |
| Native AAC mono | 512 frames / 1024 bytes | same **4096 bytes**, not duplicated by codec |
| ESP8266Audio MP3 | 32 stereo frames / 128 bytes, inside mad_synth | **2048 bytes** with Arduino ESP8266 core 3.1.2 |
| ESP8266Audio AAC | 1024 stereo frames / 4096 bytes | same core DMA |
| Legacy Espressif/myRadio MP3 | 32 mono samples / 64 bytes on stack | 14 x 64 words x 4 = **3584 bytes** |

Arduino DMA was inspected in the locally installed core 3.1.2:
`core_esp8266_i2s.cpp`, `SLC_BUF_CNT=8`, `SLC_BUF_LEN=64`.
Upstream sketches do not pin that core version; do not attribute these
exact DMA settings to their historical prebuilt binaries.

At 48-kHz PCM and PDM32, 4096 payload bytes correspond to 21.33 ms for both
native buffers combined. One is producer-owned, so this is not a guaranteed
21.33-ms fully queued reserve. The corresponding combined nominal capacities
for Arduino/legacy are 10.67/18.67 ms at the **same** rate/PDM32. Real rates and
backends differ; this is a capacity comparison, not an output-speed benchmark.

Native already has more DMA payload than either alternative. Enlarging output
buffers consumes the same scarce DRAM and does not replace compressed-input
buffering.

## 4. How optimized are the implementations?

### Native yoRadio

- Explicit O3, measured Helix MP3 SSO, mono M/S optimization where valid,
  shared reorder/IMDCT storage and 32-frame PCM delivery.
- AAC block output saves 3072 bytes DRAM; its retained test showed roughly
  6.1% slower decode-only calls, so it is a memory/continuity trade-off,
  not a speed improvement.
- 16-KiB IRAM reuse, bounded lazy codec allocation, codec ownership/release,
  direct conversion into reserved DMA spans. No extra PCM-to-PDM copy buffer.
- Richer workload: two WebSockets, shared YoRadio UI, playlist indexing/cache,
  uploads/OTA, persistent settings and normalization.
- Weakness: ordinary receive/decode/output share the audio task and there is
  no independent compressed-data FIFO. During long decode/output work the
  application does not keep draining the TCP stream.

### ESP8266Audio WebRadio and renat

- Already use optimized fixed-point libmad with SSO, flash-resident constants,
  32-frame synthesis and bounded input. This is not an unoptimized reference.
- WebRadio preallocates memory to avoid repeated large allocations.
- Cooperative main loop: decoder returns when output is full; the source
  buffer's `loop()/fill()` opportunistically refills using `readNonBlock()`.
  This is not a parallel network worker or interrupt-driven HTTP decoding.
- Extra stream buffer buys burst tolerance, at a material DRAM cost.
- Renat's steady-state loop mostly services audio/logging; selecting stations
  relies on the author's external website. It does not carry our local WebUI
  feature set. Fewer features must not be called a decoder optimization.
- NoDAC conversion occurs before checking whether the first I2S word fits.
  On retry this deserves a separate state/bitstream audit; it is not proof
  that importing this output path would fix our underruns.

### MrDIY

- Same libmad/AAC layouts in its configured ESP8266Audio fork.
- The intended 4-KiB stream buffer is absent in the checked-out implementation.
- MQTT, configuration UI and optional speech/other codecs add work and RAM;
  source-level dynamic allocation makes a clean whole-RAM total impossible.
- Useful as an integration example, not evidence of superior audio buffering.

### Legacy Espressif and myRadio

- Modified fixed-point libmad, OPT_SPEED/OPT_SSO, flash tables, small mono PCM
  batches, DMA and a separate blocking network reader feeding a FIFO.
- The compiler optimization selection is `-Os`; declarations of `-funroll-loops`
  in the link command alone do not prove the C translation units were unrolled.
- Old mono output still synthesizes both input channels and sums them; it
  does not implement our valid M/S side-channel skip.
- Much of the robustness claim depends on external 128-KiB RAM.
- myRadio enables the small internal FIFO, but its HTML server is started in
  a separate AP/configuration mode, not concurrently with ordinary playback.
  Its smaller UI workload is not equivalent to our native firmware.
- The checked-in Espressif default is DELTA_SIGMA_HACK, not PWM_HACK;
  both NoDAC alternatives exist. Neither is our RC-PDM implementation.

No ranking of measured CPU throughput across these exact revisions is claimed:
that requires identical fixtures, rates, channel policy, output and board tests.

## 5. Whole firmware memory and existing physical evidence

Matching native production ELF:

| Section | Bytes |
| --- | ---: |
| .dram0.data | 1648 |
| .dram0.bss | 19784 |
| Static DRAM total | **21432** |
| IRAM vectors + text + bss | **27484** |
| flash.text | 530738 |
| flash.rodata | 204164 |

The 16-KiB runtime IRAM arena is not included in the linked static IRAM total.
Static DRAM includes the 4096-byte DMA payload, 1088-byte status message and
1024-byte static-file scratch. Do not add them again to static DRAM.

Saved physical tests of this exact production image on 2026-09-08:

- MP3 128, five minutes, 279 health samples: free heap **9996..13532 bytes**.
  This is whole-firmware remaining heap, not codec allocation. PCM/wall was
  0.9752 with 6559 additional DMA underruns: continuity **failed**.
- Radio stopped, two loaded browser pages: free heap **21328..22360 bytes**,
  lifetime minimum 16780. These are different conditions from playback.
- Page load under MP3 also had a saved incomplete HTTP transfer; the good
  stopped-radio page timings do not establish stable loaded playback.

See [full physical report](ESP8266_WIFI_RX_OPTIMIZATION_2026-09-08.md),
[MP3 raw samples](benchmarks/esp8266-wifi-rx-2026-09-08/production-mp3-300s.json)
and [two-page data](benchmarks/esp8266-wifi-rx-2026-09-08/production-web.json).
No fresh runtime RAM claims are made for upstream firmware.

Historical artifact sizes: renat ESP8266 BIN 487920 bytes; MrDIY v0.61 ESP8266
BIN 679632 bytes. They are not same-toolchain feature-matched builds.
myRadio includes an old map: heap starts at 0x3fff3660, leaving 51616 bytes
within its 98304-byte DRAM region before dynamic runtime allocations.
Its static occupancy **46688 bytes** includes old SDK static state, so it is
not directly comparable to a newer SDK which allocates more state dynamically.
The ESP32 ELF files bundled by renat were deliberately excluded.

## 6. Conclusions for our firmware

1. **Keep our codec/IRAM and bounded-PCM work.** The reviewed alternatives do
   not demonstrate a smaller equivalent DRAM footprint with the same features.
2. **Investigate a bounded compressed FIFO and scheduling**, not a bigger PCM
   frame. WebRadio's 4–5 KiB extra input reserve is useful design evidence.
   Start with explicit 2/4-KiB A/B budgets, not a blanket large default.
3. **Do not blindly enable the existing separate-reader experiment.** Its
   4096-byte ring + 2560-byte stack + 512-byte URL cost at least 7168 bytes,
   excluding TCB. The decoder's 1536-byte input remains. Current full-load
   headroom has not been shown sufficient.
4. If possible, reuse current HTTP/ICY scratch and avoid a second URL/metadata
   copy; separately prove task ownership and cancellation lifetimes. Sharing
   unowned scratch across two concurrent tasks would create a race.
5. Separate network starvation from output/CPU starvation. Saved tests include
   available TCP data and output underruns together. More input memory alone
   cannot fix that case.
6. For any implementation change, measure identical mono MP3 128/320 and AAC-LC
   low-bitrate fixtures with PDM32, zero-state/retry tests, two-tab stress,
   free/largest heap and DMA underruns. Include failures in results.
   No such firmware change is made by this review.

## Reproduction

Clone the repository URLs above into the named directories using
`git clone --depth 1 <URL> <directory>`. For future reproduction check out the
listed commit explicitly; a shallow clone of a future HEAD might need fetching
that commit. Repositories and compiler output remain temporary, not vendored.

Run from the project root:

```powershell
./tools/esp8266_upstream_compare/measure_sizes.ps1 -OutputPath .build/upstream-radio-review-2026-09-09/recheck.json
```

The script compiles only our small type-layout probes, never decoder code,
upstream scripts or an executable to run on the board. AAC stubs only supply
stdint and an empty PROGMEM placement marker; an assertion rejects SBR.
Pointer-size assertion requires 32-bit target ABI. JSON includes compiler and
source commits. The four MP3 and two AAC probe compilations all passed.
The `size_arena_1536` field for legacy libmad is only a synthetic aligned sum
of header structures plus 1536 bytes, **not its actual complete RAM budget**.
