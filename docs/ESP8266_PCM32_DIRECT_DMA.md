# ESP8266: 32-frame PCM and direct PDM-to-DMA

## Data path

Helix MP3 now calls a synchronous sink after each 32-frame synthesis step,
reusing a 64-byte mono PCM buffer instead of a 1152-byte granule buffer.
Stereo uses 128 bytes instead of 2304 bytes. `MP3DecodeBlocks` is native-only;
the conventional frame and granule APIs remain available. AAC still requires
its complete decoded frame; experimental libmad retains granule-sized PCM.

Normalization, volume and resampling process the samples in the same order.
The PDM writer reserves the unfilled span of a producer-owned DMA buffer and
writes PDM words directly there, eliminating the temporary 64-word PDM array
and its memcpy. The PCM buffer remains separate because PCM and PDM formats
differ. Normalization windows, resampler phase and modulator state persist
across callbacks. Stream status is published only when its format changes.

## Ownership and backpressure

- One audio producer, one outstanding reserve/commit span at a time.
- Only FILLING memory is writable, never the buffer being read by DMA.
- Commit publishes only a complete 512-word buffer after a memory barrier.
- Partial commits accumulate; commit(0) cancels a span without publishing it.
- EOF may occur during any store; it cannot consume the FILLING buffer.
- No free buffer: block on the existing task notification, with a bounded
  timeout. No extra task, queue or stack, and no PDM conversion in the ISR.
- Stop discards queued/partial audio; underrun remains neutral 0xAAAAAAAA.
- Two 512-word DMA buffers and all task stack allocations remain unchanged.

Requested MP3 PCM allocation saves 1088 bytes mono / 2176 bytes stereo.
The writer structure shrinks from 264 to 16 bytes on 32-bit Xtensa, improving
stack headroom by 248 bytes before compiler frame-layout effects; this does
not return stack memory to the heap. The reservation counter adds one 4-byte
static variable, subject to linker alignment. This is primarily a RAM/copy
optimization; CPU speedup is not claimed without matched on-board timing.

## Silence regression found during validation

The previous `BALANCE_DENOMINATOR 16U` made its negative lower bound unsigned.
Consequently a saved balance of zero was clamped to runtime -16, making the
left gain zero. Stereo previously retained the right channel, but new mono
PCM was entirely muted. WebUI displayed the correct saved zero, hiding the
runtime conversion. The bound is now signed. Balance is ignored whenever
PCM has one channel, in all three ESP8266 output backends; its saved value is
retained for stereo. Fixed-point normalization and volume still apply.

## Reproducible tests

`node --test tests/esp8266-helix-golden.test.js tests/esp8266-direct-pdm.test.js tests/esp8266-mono-balance.test.js`

- Six MP3 vectors, MPEG1/2/2.5 and stereo-mode changes: frame, granule and
  32-frame output match byte for byte in Mono/Stereo, exact/SSO synthesis.
- PCM canaries, callback cancellation at all 18 boundaries, reset, malformed
  input/error concealment and undersized-capacity rejection.
- Actual production reserve/commit and PDM source compiled with a mocked
  RTOS/EOF boundary; only Xtensa MEMW is replaced by a host memory fence.
- Actual normalizer and output routines: equal PCM/PDM at six sample rates,
  mono/stereo, normalization on/off and 1/32/64/128/576-frame portions,
  including a non-divisible tail. PDM32, RCPDM32 and PDM128 are covered.
- EOF after every store, invalid/nested reservation, partial commit,
  cancellation, timeout, stop/restart and the legacy copying write API.
- Actual settings reload and runtime setter over all 256 int8 values;
  known nonzero mono PCM stays nonzero at balance 0/-16/+16. The test failed
  before the signed-clamp fix and passes afterward.

## Build and physical trace, 2026-09-05

All 337 root tests pass (95.46 s). The focused direct-PDM/ownership suite was
rerun after the final reservation-reset check: all 9 tests pass. Ordinary
and trace builds use Xtensa GCC 8.4/O3 and source `6bd547b`.

| Item | Previous mono/reorder | PCM32/direct DMA |
| --- | ---: | ---: |
| Mono MP3 PCM allocation | 1152 B | 64 B |
| Physical MP3 DRAM workspace | 9528 B | 8440 B |
| Reserved codec IRAM | 16384 B | 16384 B |
| ELF static DRAM data+bss | 20840 B | 20848 B |
| `native_audio_output_write` GCC stack frame | 352 B | 80 B |
| Ordinary app image | 686848 B | 687232 B |

Stack figures are function-local prologues, not total task high-water marks.
The 8-byte static DRAM increase includes linker alignment; no larger input
buffer or reduced task stack is selected as part of this change.

The Wemos D1 mini received an app-only diagnostic image at `0x10000` with
hash verification. It restored station 510 / volume 254 and 511 playlist
entries. Wi-Fi needed retries (DHCP at 19 s); initial HTTP/WebSocket attempts
timed out. After connection, Retro FM supplied MP3 128 kbit/s at 44.1 kHz.

Actual trace, after the expected startup zeros:

- Decoder PCM: 32 mono frames, min=-3/max=17, FNV `e24d7993`.
- Processed PCM: min=-3/max=17, the same FNV `e24d7993`; no mute at balance 0.
- Committed DMA-PDM: changing FNV `b2dc5eec`, `ecc79395`, `5e94c2f8`,
  including word `5555555a`, rather than only neutral `55555555`/`aaaaaaaa`.
- Decoder allocation: DRAM 8440, IRAM 16384, codec-arena used 22452 bytes.
- At the final trace status check: playing=true, free heap 15504, minimum
  heap 10988, web stack headroom 2328 bytes. ICY and stream feed continued.

This verifies nonzero PCM through processing into the DMA buffer. It is not
an electrical GPIO measurement or a listening test, nor a matched CPU-speed
benchmark. The preceding image also showed reconnects/AUDIO STREAM ERROR
and a 776-byte lifetime heap minimum; those broader network/memory issues
are not declared resolved by the balance fix.

Artifacts: `firmware/development/esp8266-native-pcm32/` (ordinary) and
`firmware/development/esp8266-native-pcm32-trace/` (diagnostic). Both retain
QIO40, CPU 160 MHz, Helix MP3 SSO/AAC, GPIO3 I2S PDM32 and 2 x 512 DMA words.
No bootloader, partition-table, NVS, SPIFFS or OTA-selection writes are needed.

The ordinary image was subsequently flashed to app0 with hash verification
and restarted. DHCP completed at 8.9 s; WebSocket `play=510` changed the
player to MP3 128 kbit/s, and `/` returned HTTP 200 in 0.192 s. One playing
snapshot showed free heap 14040, minimum heap 7192 and web stack headroom
2328 bytes. Clean stream EOF/reconnects and one failed stream-open attempt
were observed; there was also a WebSocket send warning after client closure.
The board was left playing for the user's listening check. No listening
confirmation has yet been received. Trace/profiling are off in this image.

Retained test output: [337-test regression](benchmarks/esp8266-pcm32-2026-09-05/regression.log),
[focused rerun](benchmarks/esp8266-pcm32-2026-09-05/direct-final.log),
[filtered diagnostic trace](benchmarks/esp8266-pcm32-2026-09-05/audio-path.log)
and [filtered ordinary boot/audio log](benchmarks/esp8266-pcm32-2026-09-05/ordinary-audio.log).
