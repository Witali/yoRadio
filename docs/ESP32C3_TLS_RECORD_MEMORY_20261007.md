# ESP32-C3 HE-AAC memory and full-sized TLS records, 2026-10-07

## Scope and configuration

This follow-up runs on the physical ESP32-C3 OLED board in the separate
`codex/esp32c3-idf-upgrade` branch, with ESP-IDF 6.1. The compact HE-AAC settings
remain enabled in board defaults: full-rate SBR/PS, PC19, compact smoothing,
scoped low-QMF workspace, asymmetric owner and late SBR activation. Each new
ELF passes the linked-code audit: **32,744 B SBR owner, 204 B native adapter,
160 B high-history runtime**. The owner saves 22,384 B against its original
55,128 B allocation; this is not a measurement of total radio heap savings.

The network experiments add heap functions in Flash, the optional TCP PCB
pool and L2-to-L3 copying. They use CPU/network diagnostics without a separate
profiling task, native USB capture and a 0.1-second delay between WebUI requests.
Sleep, external RTC crystal, Auto Suspend and direct DMA PCM remain disabled.
RX/TX TLS capacities remain **16,384 / 4,096 B**. CPU is informational; runtime
errors, playback progress, heap, request latency and recovery retain their gates.

These experiments follow the [ICY/RX memory report](ESP32C3_ICY_RX_MEMORY_20261007.md).
Network settings are not promoted to defaults by a successful compact PCM test.
No decoding arithmetic changes in this follow-up; the prior 2-LSB corpus result
is retained evidence, not a newly captured physical PCM comparison.

## Public HTTPS with permanent TLS buffers

The ordinary-root `memory-icy-static-profile` image was tested against five
Groove Salad URLs, 60 seconds each, with independent FFprobe/FAAD source checks.

| Stream | Original result | Mean CPU in bounded window | Allocation failure |
| --- | --- | ---: | --- |
| AAC-LC, 128 kbit/s | PASS | 52.733% | None |
| HE-AAC stereo, 64 kbit/s | FAIL | No aggregate: no first full PCM | 32,744 B requested; 38,824 free; largest 25,600 B |
| HE-AAC stereo, 32 kbit/s | FAIL | No aggregate: no first full PCM | 32,744 B requested; 35,640 free; largest 27,648 B |
| HE-AAC mono, 16 kbit/s | FAIL | No aggregate: no first full PCM | 32,744 B requested; 40,020 free; largest 29,696 B |
| MP3, 256 kbit/s | PASS | 64.733% | None |

Idle baseline, settled recovery and settings restoration pass. These results
show insufficient contiguous space for the SBR owner despite enough aggregate
free bytes. They do not prove that placing the owner earlier will leave enough
memory throughout playback. FAAD confirms the 16 kbit/s stream is mono HE;
it is not an active-PS fixture. These are five variants from one public station,
not a survey of five independent broadcasters.

## Controlled record-size experiment

The shared server uses TLS 1.2 with `ECDHE-RSA-AES128-GCM-SHA256`, observes the
actual encrypted records and sends a repeated HE-AAC v2 44.1 kHz stereo ADTS
fixture at 1.02 times its nominal byte rate. Modes are 1 KiB, 16 KiB, growth
from 1 to 16 KiB after 30 seconds, and alternating sizes. Each case observes
75 seconds of playback; the server has a longer 90-second limit so normal EOF
does not explain an early stop. This is a short allocation-boundary test, not
a ten-minute soak or acoustic continuity measurement.

The [TLS 1.2 record limit](https://www.rfc-editor.org/rfc/rfc5246#section-6.2.1)
allows 16,384 plaintext bytes. For the selected
[AES-GCM construction](https://www.rfc-editor.org/rfc/rfc5288#section-3), the
observed encrypted payloads are 1,048 and 16,408 B. Host roundtrips verify those
exact lengths and every audio byte across fixture/record boundaries. Three
initial host tests pass, including four positive record modes, untrusted-CA
rejection and refusal to overwrite a generated private key. The final suite
has four passing tests, adding a live-connection check that saved observations
remain unchanged while the server sends later records.

Two explicitly labelled laboratory images add one short-lived local CA to
the normal bundle. A binary-bundle audit proves that all **147 normal roots**
remain, with exactly that one additional subject/public key: 148 entries and
68,164 B versus 67,817 B. Verification remains enabled. The test CA is not
installed in the host OS. The CA signing key is never saved; the temporary
server key is excluded from retained evidence and firmware artifacts.

The physical runner checks actual PCM metadata, runtime/heap/CPU traces,
record lengths, idle recovery and saved settings. The growth case requires
full-rate PCM before the first large record. A successful server write alone
does not qualify playback. The stricter retry guard also counts handshakes
which failed before a request mode was known. Original verdicts are retained.

### Physical results

CPU and sampled minima below cover first full PCM +5 seconds through the last
full-PCM observation. Idle after failure is excluded. Short failed cases have
no aggregate CPU value. Instantaneous allocation-failure logs are separate
evidence and can be much worse than periodic heap samples.

| TLS storage | Record mode | Original result | Mean CPU in active window | Sampled minimum free / largest block |
| --- | --- | --- | ---: | ---: |
| Dynamic | 1 KiB | PASS | 71.731% | 36,620 / 24,576 B |
| Dynamic | 16 KiB | FAIL: playback stops within the initial observation period | — | — |
| Dynamic | 1 → 16 KiB | FAIL: playback stops after record growth | 71.620% before failure | 36,612 / 24,576 B before failure |
| Dynamic | Alternating | FAIL: playback stops within the initial observation period | — | — |
| Permanent | 1 KiB | PASS | 75.685% | 14,200 / 7,936 B |
| Permanent | 16 KiB | FAIL: 86 allocation errors | 72.258% | 11,184 / 4,608 B |
| Permanent | 1 → 16 KiB | FAIL: 48 allocation errors | 74.785% | 14,668 / 7,936 B |
| Permanent | Alternating | FAIL: 33 allocation errors | 73.486% | 14,200 / 7,936 B |

Dynamic-buffer failures request **16,749 B**, including allocator/TLS overhead:

- Large from the beginning: 24,768 B free, largest block 13,824 B.
- Growth during playback: 24,752 B free, largest block 15,360 B.
- Alternating: 26,416 B free, largest block 16,384 B.

The large and alternating cases did briefly produce full-rate PCM (21 and 24
status samples). Their original `Insufficient actual playback samples` result
refers to the stable window after warm-up; it must not be described as never
decoding a frame. The growth case has 165 full-rate status samples before it
stops. CPU headroom does not explain these allocation failures.

With permanent buffers, all four modes produce full-rate PCM throughout their
checked stable windows. The three large-record modes nevertheless record
**167 failed allocations: 78 × 1,512 B and 89 × 1,700 B**. The first failure has
2,328 B free and a largest block of 1,024 B. Free/largest values in these failure
lines use the same capabilities mask as the failed allocation. This is why
apparently sufficient periodic heap minima cannot qualify the run. Audio status
and decoder counters are not proof of uninterrupted DMA/acoustic output.

Both images pass settled idle-memory recovery and saved-settings restoration;
both aggregate runtime checks fail for the recorded allocation errors.

### Record evidence and terminal-error follow-up

The original runners checked live server events before Stop, then saved the
final trace. Stop can cause one more generated record whose socket write fails.
The archive retains that entire trace. Its summary separately replays only
record/write timestamps through the recorded observation end: both small cases
retain 298 matching 1,048-byte records; the permanent-buffer large/grow/alternate
cases retain the exact 16,408-byte records as well. Dynamic failure cases retain
their generated/completed-write mismatch and remain FAIL. No failed result is
converted to PASS by truncating the analysis window.

The runner now saves the exact snapshot used by its record gate, independently
of later server activity. Historical runner versions and their hashes are saved
alongside the reports; the snapshot change has host coverage and does not claim
a new physical run of the updated runner.

The dynamic alternating case also logs a **46,622-byte** allocation attempt
immediately after the failed 16,749-byte attempt. The server's observed record
sizes remain bounded. A source audit finds that `esp_http_client_read` can return
already-read bytes after a fatal transport error, allowing a subsequent call
back into TLS. This suggests an error-retry/state issue; its exact cause remains
unconfirmed. Preserve this failure and add targeted fault-injection coverage
before changing the SDK's error path.

## Decision and remaining work

Keep the compact AAC defaults and their full format/rate support. Keep the
experimental network profile unqualified. A memory fix must satisfy all three
observed requirements:

1. Leave a contiguous 32,744-byte SBR owner under public HTTPS startup load.
2. Guarantee room for full TLS records after the decoder starts, including
   overhead; a 16,384-byte free block is insufficient for the dynamic request.
3. Preserve receive/packet headroom during large-record bursts, not just periodic
   average free heap. Permanent TLS allocation alone fails this requirement.

Audit allocation order and buffer ownership before adding reservations or
changing queue limits. Any compact-owner reservation must use the selected
layout and preserve LC, late SBR/PS, allocation-failure cleanup and repeated
switches. The old 55,128-byte early-reserve option is not compatible with the
compact adapter. Do not lower TLS capacity or AAC output rate to pass these gates.

After a concrete fix, rerun this matrix, public AAC/MP3, mixed codecs, ten-minute
load, late SBR/PS and OTA during playback on the exact candidate.

## Final board state

The normal diagnostic image rejects the temporary lab CA, with the certificate
bundle's explicit rejection log and matching TLS alerts. Settings and serial
health checks pass. App-only OTA then restores the normal quiet image:
ELF `da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0`,
partition `app0`. An independent read initially finds the normal boot autostart
playing AAC. Explicit Stop restores the pre-test stopped state, verified three
times over 15 seconds; Wi-Fi, playlist and settings are unchanged. No test trust
root remains in the running image.

## Evidence and reproduction

Firmware and exact SDK configurations are retained under
`firmware/development/esp32c3-idf-6.1-memory-icy-static-profile/`,
`...-memory-icy-tlslab-dynamic/` and `...-memory-icy-tlslab-static/`.
Both `tlslab` images are laboratory-only and must not be used as production
firmware; their manifests identify the extra trust root and restoration image.

The [evidence archive](../tests/results/esp32c3-tls-record-memory-20261007/)
contains original reports, filtered UART/status/server traces, source snapshots,
build/config audits, exact hashes and public certificates/bundles. `index.json`
checks stored and uncompressed bytes. Private keys and broadcast audio are
excluded. The ordinary static image was built from `d154276e`; laboratory images
from `f170f477`. Later commits change test evidence handling, not decoder code.

Use the [controlled TLS testing guide](ESP32C3_TESTING.md#controlled-tls-record-growth)
and [shared server documentation](../tools/audio_test_server/README.md#full-sized-tls-record-tests)
for generation and physical commands. Generate a fresh short-lived CA and
rebuild both laboratory images to reproduce the experiment after expiry;
keeping certificate verification enabled is part of the test.
