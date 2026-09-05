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

Hardware trace and ordinary-build results will be recorded after installation.
