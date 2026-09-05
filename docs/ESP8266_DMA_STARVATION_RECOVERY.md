# ESP8266 DMA starvation recovery — 2026-09-05

The user confirmed that PCM32/balance-fix firmware produces sound, but it
still has growling distortion. The balance fix solved silence, not this
separate continuity defect. Listening acceptance is still pending.

## Measured problem

With the original full-buffer-only handoff, a live Retro FM MP3 128-kbit/s
window produced 3.915 s of audio in 5.023 s. DMA had 106 missing-buffer
events (all 106 with a partial producer buffer), zero observed I2S FIFO-empty
flags, and about 14070 words still missing at those deadlines. Each miss
replayed a complete **512-word neutral block**, approximately 10.65 ms.
This is strong evidence of periodic audio gaps, not proof of analog quality.

Even a small missed deadline could therefore add an entire 10.65 ms silence
interval. Waiting for all 512 words also prevented use of an already
committed prefix. Producer/network jitter was amplified by the output policy.

## Corrected ownership and recovery

- Keep exactly two payload buffers with capacity 512 words each (4096 bytes).
- Reserve/commit and EOF share a critical-section-protected ownership state.
- A live reserve loan prevents DMA handoff, including every individual store.
- At EOF, a committed prefix with no outstanding loan may be submitted with
  its exact byte length. Ownership of the **entire** buffer transfers to DMA;
  the producer never keeps or writes a suffix of that buffer.
- Set descriptor lengths during commit, outside the ISR's decision path.
- On a real underrun while playing, emit **64 neutral words** (about 1.33 ms)
  before retrying, instead of adding another 512-word interval.
- Stop uses the original 512-word neutral cadence. Neutral PDM remains
  `0xAAAAAAAA`, not logic zero and not repeated audio.
- Finite descriptors still prevent prefetch of a producer-owned buffer.
- The ISR uses size optimization in both ordinary and diagnostic builds;
  GCC emits a 32-byte frame with no added helper calls. This retained the
  16-KiB IRAM codec arena in the successful diagnostic build. Earlier, larger
  instrumented prototypes fell back to DRAM and are not valid timing controls.

There is no added production PCM buffer, task, allocation or stack reduction.
An extra playing-state flag controls the neutral retry interval.

## Reproducible physical comparison without Wi-Fi

The isolated codec benchmark can now include the actual output path:

```text
-DYORADIO_ESP8266_CODEC_RAM_BENCHMARK=ON
-DYORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT=ON
-DYORADIO_ESP8266_AUDIO_PROFILE=OFF
-DYORADIO_ESP8266_AUDIO_TRACE=OFF
```

It copies the retained 320-kbit/s MP3/AAC frame into static test-only RAM,
does eight warm-up frames and 200 measured frames, and sends decoded PCM
through volume, PDM packing and the real GPIO3 I2S/SLC DMA. Wi-Fi/WebUI are
not started. Normalization is off and volume 128 is applied in RAM only;
saved station, volume and normalization settings are not overwritten.

`YORADIO_ESP8266_DMA_COMMITTED_PREFIX=OFF` restores the full-buffer handoff
and long-neutral-block policy for A/B testing. It defaults to ON. The flag
covers both safe-prefix handoff and short neutral retry, not only the prefix.

All runs used CPU 160 MHz, QIO40, mono Helix MP3 SSO/AAC, PDM32, the same
two buffers, and the intended 16384-byte IRAM arena.

| Policy | Codec | Audio produced | Wall time | Underrun events | FIFO-empty |
| --- | --- | ---: | ---: | ---: | ---: |
| Original full blocks | MP3 | 4.800 s | 4.785245 s | 0 | 0 |
| Prefix only (rejected intermediate) | MP3 | 4.800 s | 4.786369 s | 0 | 0 |
| Prefix + short neutral retry | MP3 | 4.800 s | 4.785525 s | 0 | 0 |
| Original full blocks | AAC | 4.266666 s | 4.371473 s | 11 | 0 |
| Prefix only (rejected intermediate) | AAC | 4.266666 s | 6.381378 s | 200 | 0 |
| Prefix + short neutral retry | AAC | 4.266666 s | 4.259223 s | 4 | 0 |

Prefix-only was not accepted: the AAC workload remained sensitive to long
neutral-block insertion and had a bad timing phase. Short retries remove
that amplification. These aligned 48-kHz fixtures generated no partial
handoffs; the host interleaving test and live diagnostics exercise prefixes.
The short-retry AAC result is approximately realtime, not a claim of zero
gaps: four 64-word neutral retries still occurred. DMA carries queued data
across measurement boundaries, so small audio/wall differences are expected.
These are wall/output measurements, not decoder-only CPU percentages.

MP3 workspace: DRAM 8440 / IRAM 16384. AAC: DRAM 9876 / IRAM 16384.
The benchmark's task stack retained 1496 bytes and 50 create/switch cycles
returned heap to its initial value. The first combined test overflowed the
3-KiB app stack with a local 1536-byte fixture; moving that test fixture to
static RAM fixed the test without changing any production task stack.

## Tests and remaining limits

- Actual C reserve/commit and prefix decision compiled on the host; EOF
  injected during every store and before/after commit, 1000 randomized loans.
  Actual DMA payload sequence equals input without losses, duplication or
  reading uncommitted data. Stop restores the long idle-neutral cadence.
- PCM/PDM remains bit-exact across 1/32/64/128/576-frame chunks, six rates,
  mono/stereo, normalization on/off, PDM32/RCPDM/PDM128.
- The ordinary radio still needs a listening and longer streaming check.
- RF/TCP problems are separate: the live station reconnected repeatedly, and
  even a local, paced HTTP fixture delivered only 1–2 kbit/s in some windows
  with multi-second receive gaps. The LAN test is not a valid throughput
  acceptance result. No computer Wi-Fi configuration was changed.
- Short retries cost more ISR entries during a prolonged playing underrun;
  stopped playback retains the original low-frequency neutral cadence.

Build artifacts and filtered captures are saved with the firmware changelog.
