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

## MP3 SSO and 384 kHz SPI-PDM8 profile

On 2026-09-01 the optimized Helix MP3 SSO backend and exact AAC backend were
measured again at 320 kbit/s. This profile used QIO 80 MHz, CPU 160 MHz,
`-O3`, and mono SPI-PDM on GPIO13 at 384.615 kHz (eight PDM bits per 48-kHz
output sample). The full-output and decode-only builds consumed the same
paced deterministic input files.

| Mode | Codec | Windows | Realtime | CPU busy | Decoder | PCM output | PDM compute | Free heap | Min free |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full output | MP3 320 kbit/s | 6 | 95.2% | 97.7% | 81.2% | 12.1% | 12.0% | 5,864 B | 5,416 B |
| Full output | AAC 320 kbit/s | 8 | 77.0% | 91.0% | 77.0% | 17.1% | 9.4% | 11,066 B | 10,020 B |
| Decode only | MP3 320 kbit/s | 6 | 99.0% | 97.8% | 92.6% | 0.0% | 0.0% | 5,856 B | 5,508 B |
| Decode only | AAC 320 kbit/s | 7 | 96.7% | 97.8% | 92.0% | 0.0% | 0.0% | 11,084 B | 10,024 B |

The internal stage hooks give the following steady-state medians in the
full-output build. `Wall` is the share of the five-second window; `Decoder`
is the share of measured decoder-core time. Nested MP3 synthesis rows are
subsets of the synthesis total and must not be added to it.

| Codec | Internal stage | Wall | Decoder |
|---|---:|---:|---:|
| MP3 | Huffman | 16.6% | 20.4% |
| MP3 | Dequantization | 3.5% | 4.3% |
| MP3 | IMDCT | 18.2% | 22.5% |
| MP3 | Synthesis total | 39.9% | 49.2% |
| MP3 | Synthesis DCT | 21.4% | 26.5% |
| MP3 | Synthesis polyphase | 17.1% | 21.1% |
| AAC | Huffman | 33.8% | 43.9% |
| AAC | Dequantization | 2.9% | 3.8% |
| AAC | Stereo filter | 2.0% | 2.6% |
| AAC | IMDCT | 37.5% | 48.7% |

For MP3 the decoder is slower than the physical output producer, so the
12-block SPI queue does not fill in steady state: measured queue wait is
0.0%, while gain, stereo-to-mono, resampling, and PDM generation consume
12.0%. AAC produces PCM in larger bursts; its 17.1% output time splits into
7.6% queue wait and 9.4% output computation. Normalization is below 0.1% for
both fixtures.

The profiler originally never opened a reporting window when the first codec
was created rather than switched. The profile now wraps both
`helix_codec_create()` and `helix_codec_switch()`. The SPI ISR also only sends
a task notification while the producer is actually blocked, preventing stale
notifications from accumulating. A decoder-free generated-PCM run after this
change completed at 96.8% physical realtime with zero invalid queue events.

## Conclusions

- The optimized MP3 path is close to realtime at 320 kbit/s, but 95.2% leaves
  no safety margin and predicts periodic underruns. It also leaves only
  5.4 kB minimum heap.
- AAC 320 is not realtime with SPI-PDM8: it produces 77.0% of the required PCM.
  Decode-only reaches 96.7%, so output optimization alone cannot provide a
  safe production margin.
- Both decode-only cases keep the CPU about 97.8% busy. CPU busy falls to 91%
  for full-output AAC because queue backpressure limits how many frames can be
  decoded; that lower number does not mean playback has spare capacity.
- MP3 synthesis is the primary target, consuming about half of decoder time;
  DCT and polyphase are nearly the entire synthesis cost. AAC work is split
  mainly between Huffman (44%) and IMDCT (49%).
- The older QIO40 and pre-SSO tables remain useful historical baselines, but
  they no longer describe the current optimized decoder throughput.
- A production-safe 320-kbit/s profile still requires faster hot kernels,
  reduced channel/sample-rate work, or the hardware I2S/SLC output path.

The production application was restored after the measurement. Its UART boot
was verified through Wi-Fi association, DHCP, WebUI startup, and SPI-PDM
initialization.

## Reproducing

The scripts and parser are in tools/esp8266_audio_profile. See that
directory's README for fixture generation, physical capture, the decode-only
build flag, and summarization. Raw logs and generated media remain under the
ignored .build directory.
