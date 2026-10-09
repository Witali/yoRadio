# Compact TCP telemetry and extended HE-AACv2 trial

See [the report](../../../docs/ESP32C3_WEB_TCP_V2_20261009.md). Application
acceptance and TCP trace integrity are separate gates; the final observations
are reproduced in `review.json`. No absence of a TCP packet may be inferred
outside a CRC/sequence/watermark-qualified interval.

The controller passes 17/17 checks, including its TLS-specific integrity
gate. Additional replay passes nine phase intervals and rejects the two
HEv2 EOF intervals: sequences 1067 and 1198 are missing. All retained v2
frames pass CRC; that does not prove all events were retained. The original
17/17 report and these stricter failures are both preserved.

`physical/` retains the application-only OTA identities, three codec-switch
cycles, four HTTPS EOF cases, a 180-second HE-AACv2 TLS-record-growth case,
quiet idle, settings-equality checks and production restoration. Filtered
serial observations and host socket timing/port metadata exclude payloads,
settings contents and private keys. Public CA/leaf certificates are included.

`host/` preserves sanitizer checks and actual C-generated frames decoded
independently by Python. `parser-tests.log` covers corrupt/deleted hex digits,
merged records, missing tail events, gaps, drops and counter wrap. `audit/`
contains linked routes and unchanged codec object-section comparisons. The
separate wire audit handles compiler inlining and the ROM CRC symbol alias.
`sources/` freezes firmware main files and the shared test/server helpers.
The unrelated inactive CLZ CMake block was not compiled.

Offline replay requires no board or network:

```powershell
python tests/results/esp32c3-web-tcp-v2-20261009/replay.py --output NEW_DIRECTORY
```

It verifies exact archived bytes, saved firmware/config/source identities,
restoration and independent analysis. The original local build/controller
recipes use explicit laboratory addresses and short-lived test trust. The
private key is intentionally absent; prepare fresh paths and certificates
before a new physical run. Existing captured results must not be overwritten.
