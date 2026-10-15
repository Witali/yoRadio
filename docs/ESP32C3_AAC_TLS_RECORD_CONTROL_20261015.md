# AAC-LC controlled TLS record sizes

## Result

Four requested 75-second observations of a local 128-kbit AAC-LC fixture
produce **zero steady DMA completion drops and write errors**. Format, actual
TLS record-size evidence, WebUI response and stopped-state recovery pass in
every mode. The campaign remains **29/30**, because the 16-KiB mode fails its
endpoint memory-trend gate. No recorded allocation, decoder or watchdog fault
occurs. This does not reproduce the quiet candidate's intermittent public-radio
output failure or qualify a production image.

| TLS plaintext records | Last observation | Steady output window | Drops / write errors | Memory gate |
| --- | ---: | ---: | ---: | --- |
| 1 KiB | 75.028 s | 59.444 s | 0 / 0 | PASS |
| 16 KiB | 74.041 s | 58.526 s | 0 / 0 | FAIL |
| 1 KiB, then 16 KiB after 30 s | 74.984 s | 59.475 s | 0 / 0 | PASS |
| Alternating 1 / 16 KiB | 75.041 s | 59.426 s | 0 / 0 | PASS |

Encrypted application-record lengths are measured as 1,048 and 16,408 bytes,
consistent with the intended plaintext sizes and the selected TLS 1.2
ECDHE-RSA-AES128-GCM-SHA256 cipher. The source is `lc-44100-stereo` at approximately
128,381 bit/s, paced at 1.0 times its encoded duration. The server records
completed socket writes, not board receive times. All observed output is
AAC-LC at 44.1 kHz stereo; first matching format appears in 2.30–2.36 seconds.

## Memory and pipeline evidence

All 330 retained health samples stay on one boot, with zero recorded
allocation/decoder/watchdog faults. Minimum sampled free heap and largest
block are 59,480 and 32,768 B. No traced HTTP request fails. The longest
status/health observation is 143.824 ms.

In the 16-KiB case, free heap ranges from 60,520 to 69,764 B. First/last
three-sample medians are 69,764 and 60,524 B, producing the retained failure.
No allocation ownership telemetry was captured, so neither a leak nor receive
buffer occupancy is established as the cause of that difference.

Settled free-heap medians are 138,948 B initially and 138,920 / 138,940 /
138,948 / 138,956 B after the four cases. Every settled largest block is
110,592 B. The independent replay retains all original gates. Each steady
pipeline window has zero new events; idle/startup events are excluded.
There is therefore no recorded event from which to attribute the public-radio
failure to scheduling or starvation. These measurements are not PCM or acoustic
continuity evidence.

## Exact diagnostic image and restoration

- Source commit: `4af8b8c9`.
- Version: `idf61-ctls-20261015`.
- App SHA-256: `cd9d9461cedafcab26ddcf05ec4ce8780b8a570f6d49b21f1e6e4d00dba39e85`.
- ELF SHA-256: `75a91acdca3c9c1ce4a13375f2487795a5581a2baaba4b3c5183b4dba38e2da8`.

The only normalized configuration changes from the public-root diagnostic
image are enabling the additional local CA and its path. The normal public
CA bundle remains enabled. Code/IRAM/DRAM sizes are unchanged; Flash rodata
grows by 352 bytes. AAC, HTTP-buffer-release, adaptive-allocator and ISR/timer
placement audits pass. The recorder still occupies 540 static bytes.

The laboratory CA/server certificates expire on 2026-10-17. Their public
certificates and generator are archived. No private key or user settings are
included; no OS trust store was changed. This image is labelled laboratory-only
and must not be used as the production release.

App-only OTA installation and restoration succeed. `idf61-prod-20261013` is
verified restored on app1, stopped, with Wi-Fi/playlist/settings unchanged.

[Build, certificates and audits](../tests/results/esp32c3-confirm-tls-lab-20261015/build/),
[raw observations and independent replay](../tests/results/esp32c3-confirm-tls-lab-20261015/physical/),
and [diagnostic firmware](../firmware/development/esp32c3-idf61-confirm-tls-lab/)
are preserved with hashes.

## Next experiment

Record size alone did not reproduce the fault. Add deterministic delivery
pauses over TLS using the already verified finite AAC fixture, bounded host
send buffering and the existing ISR recorder. Retain the firmware's numeric
input-queue occupancy in the host evidence as well. Compare identical schedules
before proposing a buffering or scheduling change. Keep the original public
output failures, this memory-gate failure and the WebUI TCP timeout open.
