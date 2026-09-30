# Full-radio QIO 80 MHz acceptance, 2026-09-30

See the [complete report](../../../docs/ESP32C3_QIO80_ACCEPTANCE_20260930.md).
Production default remains DIO 80 MHz; not all acceptance tests passed.

| Evidence | Scope |
| --- | --- |
| `qio80-production/` | Quiet candidate: HTTP/HTTPS matrix, transitions, faults, WebSocket |
| `qio80-load/`, `qio80-load-repeat/` | Both QIO profiling load attempts |
| `dio80-load/`, `dio80-load-repeat/` | Matched-source DIO controls |
| `qio80-switch-soak/` | Interrupted switching and one-hour soak attempts; no completed hour |
| `qio80-memory/` | Allocation/stack survey and AAC playback |
| `qio80-tls/` | Untrusted certificate rejection unverified: required alert absent |
| `dio80-boot/`, `qio80-boot/`, `boot-comparison.json` | 30 readiness samples per mode and gate |
| `qio80-ota.json` | Exact quiet image, 15 passing OTA/restoration checks |
| `host/` | Host checks, broad repository failures and C3-specific passes |
| `restoration.json` | Original full-flash equality and settings verification before EOF-fix work |
| `summary.json` | Case counts; restoration is a case, not a codec test |

Images were built from `6c3da5e9`. The initial host archive assertion was fixed
in `c4eb5f33`. The test runner began retaining partial observations in
`716f7964`; interrupted batches from earlier attempts may have no saved REST
samples, though their failures and serial records remain. Later reports record
the updated source hashes. The final DIO load runner also included the new EOF
suite definition, which was not selected and did not change the load checks.

Only whitelisted technical board fields and filtered performance logs are
retained. No Wi-Fi CSV, playlist contents, private TLS key, full-flash backup
or credential hash is included. Software reset is not a cold-power-cycle test.
RSSI changed between runs; no causal link to flash mode was established.

The recorded EOF failures precede the later EOF status correction. Keep this
evidence unchanged and store tests of a changed image in a separate result set.
