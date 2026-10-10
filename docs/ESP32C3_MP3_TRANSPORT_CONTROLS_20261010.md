# ESP32-C3 MP3 transport controls — 2026-10-10

The diagnostic image played both paced local MP3 controls without output
counter increments. Public MP3 stopped over both HTTP and HTTPS. Therefore
the public failure is not limited to TLS or to the 44.1 kHz decoder rate.
This comparison does not isolate a single cause: public and local content,
network paths, server behavior and individual connection timing differ.

## Configuration and method

Same image as the [HTTP/TLS read diagnostic](ESP32C3_PUBLIC_READ_DIAGNOSTIC_20261010.md):
ESP-IDF 6.1 revision `9a97f6c54ec638111ce55cd36581b3c192f15207`, QIO 80 MHz,
fractional 48 kHz output, one-second prefill, normal trust, optional pipeline
diagnostics, no deep sleep. App SHA-256:
`174d78968f7e02b37fc05d0d9ae00ad9d342b4bb4b615ce831e771fa6b15947d`.

Four sequential 90-second observations, with 15 seconds excluded from output
and memory windows. Local fixtures are 130-second original synthetic stereo
MP3, CBR 256 kbit/s, verified by FFprobe and full FFmpeg decode, served at 1x.
Public source: `ice5.somafm.com/groovesalad-256-mp3`. The plain HTTP precheck
returned 200 without a redirect. Concurrent independent FFmpeg clients
completed 95 decoded seconds over both public transports with no error output.

## Results

| Source | Playback | Active-window I2S completion queue drops | Minimum sampled free / largest block (bytes) | New captured fatal reads |
|---|---|---:|---:|---:|
| Local HTTP, 44.1 kHz | PASS, 90 s | 0 | 79,088 / 65,536 | 0 |
| Local HTTP, 48 kHz | PASS, 90 s | 0 | 79,448 / 63,488 | 0 |
| Public HTTP | Stopped at 25.602 s | 777 | 82,492 / 69,632 | 0 |
| Public HTTPS | Stopped at 26.073 s | 615 | 78,920 / 65,536 | 1 |

Output counts above end before the first sampled stopped state. The raw test
also retains its original full-window checks; they fail for both public cases.
These are lost completion notifications, not counts of lost audio samples or
audible clicks. Phase checkpoints are not scheduler-state measurements.

The HTTPS event recorded `esp_tls_error=32797`, `tls_code=29312` (`0x7280`,
connection EOF), `system_errno=128`, and 61 valid bytes returned by the HTTP
read. No captured fatal-read event for HTTP is not proof of successful
playback; the observed stop remains a failure.

All cases passed sampled memory thresholds. Across the campaign there were
zero reported allocation failures and watchdog events, no unexpected reboot,
and the post-stop heap recovery check passed. Public interruptions remain
unresolved; this is not a full production qualification.

## Evidence and harness correction

[Archive](../tests/results/esp32c3-mp3-transport-controls-20261010/) contains
controllers, source snapshots, generated fixtures, server delivery events,
status/health samples, FFmpeg logs, replay checks and restoration evidence.
`review.py` replays checks, verifies hashes, checks host decoded duration
(exit status alone is insufficient), and validates both restorations.

The first controller completed its local 44.1 kHz observation but its analysis
raised `KeyError: label`: it used the generic fixture loader instead of the
C3 wrapper which supplies display labels. The second controller corrects the
loader and checks labels before OTA. The failed attempt and its successful
restoration are retained; it was a harness error, not a firmware crash.

Both attempts restored the exact previously listened-to image, verified three
stopped states and unchanged Wi-Fi, playlist and settings. Raw settings and
credentials were kept only in memory. Subsequent production deployment is
documented separately.
