# Local Opus radio, Internet excluded — 2026-09-18

## Setup

PC Ethernet192.168.100.253 -> local router -> ESP8266 Wi-Fi192.168.100.6.
No WAN/DNS/external audio source in these trials. Wi-Fi, TCP/lwIP, decoding
and PCM/PDM output remain in the path. No PC adapter/firewall changes.

Same previously flashed quietclock image:890272B, SHA256
3b5e113cadecee605686a96fc48811e6647b1c86eb16e4400b9da9dfdee77cb7,
slot0x110000, all18 ASM stages, CPU160/QIO40, I2S PDM32 GPIO3, app PCM2x960,
DMA128, input2048, scratch6144/reserve4096, clock compensation ON, LED OFF.
No new firmware, SPIFFS upload, playlist or Wi-Fi changes. TCP MSS536 was
also observed on the local server. The three-PCM-slot option remains untested.

Own reproducible five-minute tone/chirp/seeded-noise files:
tests/fixtures/opus_local_radio. Hybrid24kb/s mono/60ms and SILK12kb/s
mono/20ms, continuously encoded (not looping encoded packets). Correct CRC,
SHA256,300s granules and full FFmpeg decode were checked. Both server modes
send exactly the same bytes and Content-Length/Connection:close framing.
Buffered mode is TCP-backpressured; paced mode has a1s initial lead.

## Results: none qualifies as reliable continuous playback

| Case | Closed autonomous window(s) | Other observations |
| --- | --- | --- |
| Hybrid24 buffered, warm board | 11 underruns/25.008s | Later TCP timeout/reconnect and decoder allocation failure; second snapshot stale, not a second successful interval |
| Hybrid24 paced, same fragmented heap | No new valid window | Initialization failed before playback; old-generation windows rejected |
| Hybrid24 paced, after software reboot | 21/25.001s and20/25.010s | Reconnects occurred outside these windows; status took7.064s, then timed out at15s |
| SILK12 paced, after software reboot | Scheduled snapshot timed out at15s | Historical post-failure snapshot held73 underruns/25.000s; age61.170s, not a fresh qualified run |

The diagnostic windows run on the board without HTTP requests from the
runner inside its65s wait. Health/status are queried afterwards. They can
still disturb playback outside that closed window; observed reconnects and
timeouts are retained, not discarded. Times are wall time, NOT CPU usage.
No acoustic recording/listening qualification was performed.

Observed playing free DRAM:7596B(buffered24),8000/5868/6512B(paced24 at
different snapshots). Last SILK12 snapshot was already stopped with26476B
free and a boot minimum4784B; do not report26476B as playing headroom.

Definite allocation failures(stage8, scratch6144B):

| Case | Total free DRAM at failure | Largest block |
| --- | ---: | ---: |
| Buffered24 reconnect | 8216B | 4400B |
| Paced24 warm restart | 10212B | 5600B |
| SILK12 reconnect | 8484B | 4920B |

Total free memory does not guarantee a contiguous scratch allocation.
The failure snapshots prove insufficient contiguous memory at those moments;
they do not by themselves identify the allocator/lifetime causing it.

## Conclusions and next checks

Internet is NOT the sole cause: underruns and restart failures reproduce
from a wired local source with RSSI roughly-54..-62dBm. Server TCP telemetry
also shows retransmissions, including fast retransmit, but those alone do
not prove radio-frequency packet loss (window/congestion effects remain).
Nor does this experiment isolate decoder CPU cost from output/scheduling.

Next useful investigations: preserve/reuse large decoder allocations across
recoverable reconnects; identify why servicing diagnostic HTTP coincides with
long stream stalls; separate decoder-deadline misses from local TCP waits.
The third PCM slot and full-MSS profile should be tested against this local
source, with unchanged memory guards. No such firmware change was made here.

## Reproduction and retained evidence

See tests/fixtures/opus_local_radio/README.md for server/generator commands.
tools/esp8266_opus_profile/run_local_station.cjs records playback and RAM;
summarize_local_radio.cjs produces an offline comparison. Raw logs, all
failed attempts, software-reboot acknowledgements, health, manifests and
TCP telemetry are retained in docs/results/esp8266-local-radio-20260918/.

Host tests passed3/3 in each of5 repeats. An initial timing assertion wrongly
rounded the final page's993.5ms deadline to1000ms; it was corrected to use
the parsed granule. Its failure log is retained and is not a codec failure.
Both long files decoded completely with FFmpeg without errors.

At completion, playback was explicitly stopped through WebUI(error cleared)
and only the two test server processes were stopped. No servers remain
listening on8765/8766. Board keeps the same firmware and saved settings.
