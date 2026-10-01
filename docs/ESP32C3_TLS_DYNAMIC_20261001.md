# ESP32-C3 dynamic TLS buffers — 2026-10-01

## Result

**The option improves measured HTTPS working memory but does not yet enable
full public HE-AAC/HE-AACv2 playback.** LC and MP3 pass the 60-second radio
checks under frequent WebUI polling; all three HE/v2 streams still fail their
55128-byte SBR allocation. Keep this as a candidate for the next decoder RAM
reduction, not a completed HE-AAC fix or a production default.

The following table uses the same 5–35-second window after the first decoded
frame as the [earlier baseline](ESP32C3_PUBLIC_HTTPS_20261001.md). The separate
acceptance checks use the stable 15–60-second window. Rows are stereo except
the explicitly identified core-only HEv2 fallback.

| HTTPS input | Observed output / result | Mean total / decode CPU | Minimum free / largest RAM, bytes | Earlier baseline minimum free, bytes |
| --- | --- | ---: | ---: | ---: |
| AAC-LC 128 kbit/s | 44.1 kHz; PASS | 53.417% / 20.750% | 54052 / 43008 | 32100 |
| HE-AAC 64 kbit/s | Core 22.05 kHz; **FAIL** | 36.633% / 10.167%* | 51048 / 34816 | 30376 |
| HE-AAC 32 kbit/s | Core 22.05 kHz; **FAIL** | 34.167% / 9.450%* | 50904 / 36864 | 30552 |
| HE-AACv2 16 kbit/s | Core 16 kHz mono; **FAIL** | 26.350% / 4.583%* | 49064 / 38912 | 28972 |
| MP3 256 kbit/s | 44.1 kHz; PASS | 66.367% / 26.483% | 79476 / 65536 | 60644 |

\* Fallback CPU is not full HE-AAC decoding cost and cannot qualify its speed.

LC has 21952 more observed free bytes (21.44 KiB), MP3 18832 (18.39 KiB).
These are sequential live-stream observations, not a guaranteed fixed saving:
music, packet sizes, Wi-Fi conditions and allocator placement vary. Total CPU
is about 0.43/0.88 percentage points higher for LC/MP3 than the earlier run;
both meet the existing budgets and real-time progress gate. This does not
prove a worst-case performance bound or a precise isolated TLS overhead.

The failed SBR requests show the remaining problem directly:

| Input | Requested bytes | Free bytes at failure | Largest block |
| --- | ---: | ---: | ---: |
| HE 64 | 55128 | 53504 | 47104 |
| HE 32 | 55128 | 60212 | 51200 |
| HEv2 16 | 55128 | 60164 | 51200 |

The first case lacks total space as well as a large enough block. The other
two have enough total free memory for the owner but no contiguous block.
SBR control, TLS records, WebUI and network allocations must still fit after
the owner succeeds, so merely fitting that one allocation is insufficient.

There are no retained TLS errors, panics, capture interruptions or unexpected
reboots during these five playback windows. Idle memory and task count
recover, and settings, Wi-Fi and playlist compare equal after the deliberate
final reboot. No broadcast audio or private configuration is saved.

### Controlled switching and certificate rejection

All 21 local HTTP station changes pass (three cycles of MP3, FLAC, Vorbis,
Opus, AAC-LC 48 kHz stereo, HE-AAC 48 kHz stereo and HE-AACv2 44.1 kHz stereo).
Idle heap recovers between cycles. Two WebSocket reconnects also preserve
matching REST/WebSocket format and playback state. These are short switching
checks, not a CPU/soak qualification for every codec.

The initial certificate-rejection case reports FAIL and is retained unchanged
in `local/report.json`. The server actually receives
`TLSV1_ALERT_ACCESS_DENIED`, but the old test recognizes only certificate/CA
alerts. The audited ESP-IDF path explains it:

1. `esp_crt_verify_callback` reports `Failed to verify certificate` and returns
   `MBEDTLS_ERR_X509_CERT_VERIFY_FAILED` for the untrusted root.
2. `x509_crt_verify_restartable_ca_cb` treats a callback failure as fatal and
   sets verification flags to all ones.
3. `mbedtls_ssl_verify_certificate` prioritizes `MBEDTLS_X509_BADCERT_OTHER`
   and sends `ACCESS_DENIED`.

The corrected test requires **both** this server alert and a freshly captured,
exact certificate-verification-failure message. Neither a generic TLS error,
an unreachable server nor the alert alone is sufficient. A physical repeat
passes rejection and subsequent HTTP recovery. Host regressions exercise the
missing/ambiguous-evidence failures. No TLS validation or firmware behavior was
relaxed to obtain that result.

### OTA and remaining qualification

All 15 repeat-OTA cases pass: malformed/incompatible images, interrupted and
stalled uploads, two normal round trips, upload during playback, slow upload,
and saved-settings restoration. The accompanying serial-health check passes.
The initial installation also requires actual controlled AAC PCM before
uploading a different image and verifies the target slot/hash afterward.

The board is returned to `esp32c3-tcp-pcb-pool-fixed` after this experiment.
Its known public HE/v2 limitations remain; returning to it is not a claim that
all formats are qualified. The dynamic image is saved for the next RAM trial.

Still required before promotion: full public HE/v2 without fallback or
allocation failures, trusted controlled HTTPS with large TLS records,
reconnect/record-size stress, longer CPU/heap soaks, maximum audio-buffer
settings, and the remaining codec/implicit-transition gates. No arithmetic
change or new PCM accuracy claim is made here.

## Scope

This is an optional RAM experiment for full radio playback. Add
`sdkconfig.tls-dynamic.defaults` after the existing bounded-Wi-Fi, profiling,
conservative IRAM and fixed RTC TCP-pool profiles. Product defaults are unchanged.

The generated configuration differs from the
[fixed-pool image](ESP32C3_PUBLIC_HTTPS_20261001.md) in exactly one enabled
setting: `CONFIG_MBEDTLS_DYNAMIC_BUFFER=y`. RX capacity remains 16384 bytes,
TX capacity 4096 bytes, and the full certificate bundle remains enabled.
`MBEDTLS_DYNAMIC_FREE_CONFIG_DATA` and its CA-freeing child stay disabled.
AAC arithmetic, formats, SBR/PS, rates, channels and decoder allocations are
unchanged. Deep sleep and Flash Auto Suspend are off.

## Allocation lifetime audit

The inspected ESP-IDF v6.0.2 implementation provides these lifetimes:

- `esp_mbedtls_add_tx_buffer` allocates a record buffer when writing;
  `esp_mbedtls_free_tx_buffer` replaces a consumed buffer with a small idle
  object while preserving counters/IV state.
- `esp_mbedtls_add_rx_buffer` reads the TLS header and allocates according to
  the record length. Unconsumed records retain their buffer. For TLS 1.3's
  encrypted-extensions handshake state the implementation explicitly reserves
  the maximum input size.
- The wrapped read calls `esp_mbedtls_free_rx_buffer` after consuming the
  record. Reset/free paths release the remaining objects.
- ESP-TLS can force RX back to a permanent buffer after handshake through
  `ESP_TLS_DYN_BUF_RX_STATIC`. The radio's zero-initialized
  `esp_http_client_config_t` leaves that strategy disabled.

This changes transport buffer lifetime, not TLS receive capacity or decoder
precision. A server sending large records can still require a large allocation
while SBR is active. Transient savings and a successful short playback test do
not establish a safe worst-case budget. Dynamic allocations may also affect
fragmentation and CPU; those need measurement.

SDK source hashes are retained with the experiment's evidence. No SDK files
were patched for this option.

## Reproduce

Use a fresh build directory: existing sdkconfig values override defaults.

```powershell
./idf/esp32c3-oled-native/build.ps1 `
  -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-tls-dynamic `
  -Sdkconfig build-tls-dynamic/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults','sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults','sdkconfig.iram-safe.defaults','sdkconfig.tcp-pcb-pool.defaults','sdkconfig.tls-dynamic.defaults')
```

Saved application: `firmware/development/esp32c3-tls-dynamic/app.bin`, with
exact sdkconfig and manifest beside it. It is an application-only OTA image.
ELF SHA-256: `c597f9baff8001690a90198d7fea90f7968f28811d0ab25bb712d23244f40947`.
App SHA-256: `e432be0f6a03215fd3078d765020dc4ca6ae4b3fab2f1ba18b8b60d10acded79`.
Size: 1545184 bytes, 3248 more than the fixed-pool baseline.
The map sections are identical in both images: `.iram0.text` 43354,
`.dram0.data` 12620 and `.dram0.bss` 31384 bytes. This experiment frees runtime
allocations; it does not transfer static IRAM to DRAM.

```powershell
python tools/esp32c3_tests/diagnostic.py ota_transition --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --current-firmware firmware/development/esp32c3-tcp-pcb-pool-fixed/app.bin --firmware firmware/development/esp32c3-tls-dynamic/app.bin --output .build/tls-dynamic/install
python tools/esp32c3_tests/public_streams.py --board http://BOARD_IP --serial-port COM9 --firmware firmware/development/esp32c3-tls-dynamic/app.bin --seconds 60 --interval 0.1 --output .build/tls-dynamic/https
python tools/esp32c3_tests/summarize_public.py --input .build/tls-dynamic/https --output .build/tls-dynamic/https/summary.json
```

The [public-stream test](ESP32C3_TESTING.md#https) verifies the live reference
with FFprobe, requires full PCM output and applies existing CPU/heap budgets.
It now also retains sanitized TLS errors and rejects them even if playback
later recovers. Error messages can include private host/certificate text, so
only the TLS component and an allocation size, when present, are retained.

Other physical checks, with the candidate installed:

```powershell
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite switch --suite websocket --cycles 3 --case mp3-320 --case flac-level8 --case vorbis-q10 --case opus-510 --case lc-48000-stereo --case he-48000-stereo --case hev2-44100-stereo --sdkconfig firmware/development/esp32c3-tls-dynamic/sdkconfig --output .build/tls-dynamic/local
python tools/audio_test_server/make_test_certificate.py --host PC_LAN_IP --output .build/tls-dynamic/untrusted-tls
python tools/esp32c3_tests/diagnostic.py run --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --suite tls-rejection --case lc-48000-stereo --sdkconfig firmware/development/esp32c3-tls-dynamic/sdkconfig --https-origin https://PC_LAN_IP:8771 --tls-cert .build/tls-dynamic/untrusted-tls/cert.pem --tls-key .build/tls-dynamic/untrusted-tls/key.pem --output .build/tls-dynamic/tls-rejection
python tools/esp32c3_tests/ota_diagnostic.py --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 --firmware firmware/development/esp32c3-tls-dynamic/app.bin --output .build/tls-dynamic/ota
python tests/test-esp32c3-tls-dynamic-evidence.py
```

## Retained evidence

[Evidence directory](../tests/results/esp32c3-tls-dynamic-20261001/) contains
exact image/config/test-source hashes, sanitized status/performance records,
SDK implementation hashes and map section sizes:

- [Installation](../tests/results/esp32c3-tls-dynamic-20261001/install/report.json).
- [Public HTTPS results](../tests/results/esp32c3-tls-dynamic-20261001/https/report.json)
  and [CPU/RAM summary](../tests/results/esp32c3-tls-dynamic-20261001/https/summary.json).
- [Local switching and original TLS gate](../tests/results/esp32c3-tls-dynamic-20261001/local/report.json),
  [corrected certificate test](../tests/results/esp32c3-tls-dynamic-20261001/tls-rejection/report.json).
- [OTA matrix](../tests/results/esp32c3-tls-dynamic-20261001/ota/report.json)
  and [serial health](../tests/results/esp32c3-tls-dynamic-20261001/ota/serial-health.json).
- [Return to baseline](../tests/results/esp32c3-tls-dynamic-20261001/restore/report.json)
  and [final board identity](../tests/results/esp32c3-tls-dynamic-20261001/final-board.json).

The generated untrusted certificate/private key stay in ignored `.build/`;
they are not part of the saved evidence or firmware trust bundle.
