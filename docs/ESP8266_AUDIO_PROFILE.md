# ESP8266 audio CPU and memory profile

Measured from 2026-08-31 to 2026-09-01 on a Wemos D1 mini (ESP8266EX) running at 160 MHz.
The native RTOS SDK firmware was compiled with the component performance
profile (-O3). The board read a paced HTTP stream over Wi-Fi from the local
test server. Each fixture is a deterministic, 45-second, 48 kHz stereo signal
with independent white-noise channels (seeds 8266 and 8267). This makes the
codec input repeatable and avoids an AAC encoder silently undershooting the
requested high bitrate.

The table reports the median of complete five-second steady-state windows.
Realtime is decoded PCM duration divided by wall time; playback needs at
least 100%. CPU busy/idle comes from FreeRTOS runtime counters. Heap total is
the sum of allocatable 32-bit heap regions, used is total minus free, and
Min free is the lowest value observed since boot.

The original measurements below used QIO at 40 MHz.

| Mode | Codec/bitrate | Windows | Realtime | CPU busy | CPU idle | Decoder | PCM output | PDM compute | Free heap | Used heap | Min free |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full output | MP3 32 kbit/s | 2 | 43.5% | 97.3% | 2.7% | 83.4% | 15.1% | 11.9% | 6,616 B | 96,212 B | 5,680 B |
| Full output | MP3 128 kbit/s | 3 | 37.6% | 97.5% | 2.5% | 83.0% | 13.2% | 10.4% | 7,380 B | 95,448 B | 5,688 B |
| Full output | MP3 320 kbit/s | 4 | 32.1% | 97.5% | 2.5% | 79.1% | 11.1% | 8.6% | 6,284 B | 96,544 B | 5,492 B |
| Full output | AAC 48 kbit/s | 3 | 58.1% | 80.5% | 19.5% | 58.5% | 38.0% | 16.1% | 11,704 B | 91,124 B | 5,688 B |
| Full output | AAC 128 kbit/s | 4 | 52.2% | 82.0% | 17.9% | 59.1% | 34.0% | 14.3% | 11,286 B | 91,542 B | 5,688 B |
| Full output | AAC 320 kbit/s | 3 | 41.5% | 85.0% | 15.0% | 58.2% | 27.2% | 11.2% | 11,448 B | 91,380 B | 5,688 B |
| Decode only | MP3 320 kbit/s | 5 | 38.4% | 99.4% | 0.6% | 89.0% | 0.0% | 0.0% | 6,276 B | 96,552 B | 5,452 B |
| Decode only | AAC 320 kbit/s | 2 | 58.0% | 99.0% | 0.9% | 80.7% | 0.0% | 0.0% | 11,446 B | 91,382 B | 5,688 B |

PCM output includes normalization, volume/balance processing, PDM conversion,
queueing, and queue wait. PDM compute excludes normalization and queue wait,
so it is a subset of PCM output, not another additive load.

## Decode-only rerun with QIO at 80 MHz

The same six deterministic fixtures were rerun on the physical board after
switching flash from QIO 40 MHz to QIO 80 MHz. The decode-only wrapper returns
before `native_audio_output_write()`, so normalization, volume/balance, PDM
conversion, SPI queueing, and physical audio output are all bypassed. Runtime
counters confirmed zero normalizer calls and zero SPI queue waits.

| Codec/bitrate | Windows | Realtime | CPU busy | CPU idle | Decoder | PCM output | PDM compute | Free heap | Used heap | Min free |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MP3 32 kbit/s | 5 | 73.2% | 99.9% | 0.1% | 99.3% | 0.0% | 0.0% | 6,724 B | 96,104 B | 5,684 B |
| MP3 128 kbit/s | 4 | 60.7% | 99.5% | 0.5% | 98.3% | 0.0% | 0.0% | 7,376 B | 95,452 B | 5,684 B |
| MP3 320 kbit/s | 5 | 53.8% | 99.0% | 1.0% | 96.4% | 0.0% | 0.0% | 6,104 B | 96,724 B | 5,480 B |
| AAC 48 kbit/s | 5 | 96.0% | 77.5% | 22.5% | 74.5% | 0.0% | 0.0% | 13,988 B | 88,840 B | 5,684 B |
| AAC 128 kbit/s | 4 | 99.2% | 93.2% | 6.8% | 88.8% | 0.0% | 0.0% | 12,694 B | 90,134 B | 5,684 B |
| AAC 320 kbit/s | 3 | 80.8% | 98.4% | 1.6% | 93.9% | 0.0% | 0.0% | 11,468 B | 91,360 B | 5,684 B |

The 320 kbit/s cases allow both changes to be separated because earlier
QIO 40 MHz measurements exist in both full-output and decode-only modes:

| Codec | Full output, QIO 40 | Decode only, QIO 40 | Decode only, QIO 80 | Output bypass gain | QIO 80 gain |
|---|---:|---:|---:|---:|---:|
| MP3 320 kbit/s | 32.1% | 38.4% | 53.8% | +19.6% | +40.1% |
| AAC 320 kbit/s | 41.5% | 58.0% | 80.8% | +39.8% | +39.3% |

At 320 kbit/s, the median maximum decoder call fell from 62,017 to
45,767 microseconds for MP3 (-26.2%) and from 36,814 to 27,359 microseconds
for AAC (-25.7%) when QIO increased from 40 to 80 MHz. Heap headroom was
effectively unchanged, as expected: this profile removes work from the hot
path but retains the production buffers and tasks.

## Conclusions

- Helix MP3 is CPU-bound on this ESP8266 build at every measured bitrate. It
  consumes about 97.5% of the processor and produces only 32-44% of realtime
  PCM.
- AAC leaves more idle time with physical output enabled, but still produces
  only 42-58% of realtime PCM.
- Removing normalization, PDM conversion, SPI queueing, and physical output
  improves MP3 320 throughput from 32.1% to 38.4% (about 20%) and AAC 320 from
  41.5% to 58.0% (about 40%).
- With output already bypassed, QIO 80 MHz adds about 40% decode throughput at
  320 kbit/s for both codecs. This, together with the shorter maximum decoder
  calls, indicates that the Helix decoder is strongly flash/cache-bound.
- QIO 80 MHz plus output bypass raises MP3 320 from 32.1% to 53.8% and AAC 320
  from 41.5% to 80.8% versus the original full-output QIO 40 profile. These
  combined figures must not be attributed to output removal alone.
- Decode-only CPU approaches 99% because the audio task no longer blocks on
  the output queue and instead spends the released time decoding more frames.
  The increased decoder percentage is therefore expected.
- Output optimization is worthwhile, especially for AAC, but cannot by itself
  make these Helix stereo streams realtime at 160 MHz. The decoder path still
  needs a substantially faster backend, reduced decode work, or a lower
  sample-rate/channel profile.
- AAC 128 reaches 99.2% in this synthetic decode-only test, which is still not
  sufficient production margin. No tested configuration reaches safe realtime
  throughput once normalization and SPI-PDM output are restored.
- MP3 has only about 6-7 kB free heap in steady state and reached 5,452 bytes
  minimum. AAC keeps about 11-12 kB free because its active codec workspace is
  smaller. MP3 memory headroom remains the higher stability risk.

The production application was restored after the measurement. Its UART boot
was verified through Wi-Fi association, DHCP, WebUI startup, and SPI-PDM
initialization.

## Reproducing

The scripts and parser are in tools/esp8266_audio_profile. See that
directory's README for fixture generation, physical capture, the decode-only
build flag, and summarization. Raw logs and generated media remain under the
ignored .build directory.
