# Minimum input prefill of 500 ms: TLS renegotiation experiment

## Result

Physical acceptance: **30/34**.
Failed checks: `he-44100-stereo:small:output`, `he-44100-stereo:large:output`, `hev2-44100-stereo:small:output`, `hev2-44100-stereo:large:output`.
The larger minimum startup prefill does not establish uninterrupted output
under TLS renegotiation and is **not adopted as a production default**.

| Stream / record size | Handshake, ms | Queue drops / write errors | Min free / largest, B | Max status + health, ms |
| --- | ---: | ---: | ---: | ---: |
| he-44100-stereo:small | 505.4 | 6 / 0 | 32,644 / 24,576 | 193.6 |
| he-44100-stereo:large | 524.7 | 5 / 0 | 21,408 / 12,800 | 350.8 |
| hev2-44100-stereo:small | 540.0 | 8 / 0 | 32,604 / 24,576 | 203.0 |
| hev2-44100-stereo:large | 570.8 | 9 / 0 | 24,264 / 17,408 | 184.8 |

The campaign contains 313 health observations. SDK lifetime minimum
free heap is 16,324 bytes.
All observations retain the same boot ID, with zero allocation failures,
watchdog events and I2S write errors. All four full renegotiations complete.
All verdicts are reproduced offline from the frozen measurements and test
sources. Replay PASS means the saved results, including failures, reproduce;
it does not mean physical acceptance passed.

## Controlled change and scope

Only `CONFIG_YORADIO_INPUT_PREFILL_MIN_MS` changes from 250 to 500 ms.
The maximum remains 500 ms. The four input slots, TLS reservation, decoder
precision, read timeout, scheduling priorities and nominal 48 kHz output
remain unchanged. All 119 AAC/FLAC code and constant sections in 18 objects
are identical to the baseline. Of 50 application objects, only
`audio_service.c.obj` changes; static IRAM, DRAM and RTC section sizes are
unchanged. Image size is 1,456,288 bytes, 64 bytes below the laboratory baseline.

Each case runs 75 seconds with a full, server-requested TLS 1.2 renegotiation
at 30 seconds, using either 1 KiB or 16 KiB records. Session cache and tickets
are disabled. Certificate verification stays enabled. HE-AAC and HE-AACv2
both use 44.1 kHz stereo fixtures. The test firmware includes a laboratory CA
and is not a release image.

Output deltas cover the steady interval after startup and before Stop.
They count lost I2S completion notifications, not measured missing analog
samples. `correlation.json` retains counter-change intervals near each
handshake; it cannot locate the exact ISR event or establish an audible gap.

## Comparison and conclusion

The [250..500 ms baseline](ESP32C3_TLS_RENEGOTIATION_20261010.md)
recorded HE-AAC queue-drop counts of 4 and 13 with 1 KiB records, and 23 with
16 KiB records. Its HE-AACv2 1 KiB case had zero. The present run is a bounded
comparison, not a statistical distribution of failures. Increasing startup
prefill alone is insufficient to qualify this path. Input starvation versus
CPU/scheduling delays during cryptography still requires causal measurement.

The exact previously listened application was restored by app-only OTA.
Wi-Fi, playlist and settings match their pre-test snapshot, and three
post-restoration observations confirm stopped playback. The restored ELF is
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.

[Frozen evidence and replay](../tests/results/esp32c3-prefill500-reneg-20261010/README.md).
