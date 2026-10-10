# AAC frame growth over verified local HTTPS

**15/16 original checks pass.** Preserve `he-44100-stereo-growth` as a
headroom failure (minimum largest block 7,424 B versus budget 8,192 B).
All six files actually complete the expected profile/rate/channels, duration
and EOF with zero allocation failures, watchdog events, sustained I2S
completion-queue drops or write errors. There are 522 lifetime health samples
with one boot identity. Settings and exact listened-image restoration pass.

This extends the independently decoded baseline/growth fixture pairs in
`tests/results/esp32c3-aac-growth-20261010/` to TLS. AAC-LC/HE-AAC grow to
1,543 bytes per frame; HE-AACv2 grows to 775 bytes, after 15 seconds. The
existing reference evidence verifies identical PCM within FFmpeg and within
unquantized FAAD. Raw audio is not copied into this archive. Input payloads
and independent-reference hashes are retained in the manifest/report; the
physical runner revalidated the exact fixture bytes before OTA.

| Case | Minimum free / largest, bytes | Queue / write errors |
| --- | ---: | ---: |
| LC baseline | 63,588 / 55,296 | 0 / 0 |
| LC growth | 54,520 / 40,960 | 0 / 0 |
| HE baseline | 31,768 / 22,528 | 0 / 0 |
| HE growth | 20,832 / 7,424 | 0 / 0 |
| HEv2 baseline | 32,180 / 24,576 | 0 / 0 |
| HEv2 growth | 26,192 / 14,336 | 0 / 0 |

Each of six connections negotiates TLS 1.2 / ECDHE-RSA-AES256-GCM-SHA384,
delivers the full payload without retries, and uses pacing 1.0. Largest
status/health duration is 389.3 ms. The server uses 1,024-byte application
writes; this is not a full-record-size or TLS-renegotiation qualification.
Heap changes also include the higher network bitrate after frame growth.

## Firmware and trust

Saved image: `firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls/`.
Application SHA-256:
`7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd`.
ELF SHA-256:
`83171cab66b28bc680c28a9335b60fe02303a60b9c08754269d2707acd45ae5a`.
All 50 application objects retain identical code/constants to the quiet
output-health image. Static RAM is unchanged. Full public trust is retained:
145 original entries plus exactly one test CA. This is a laboratory image,
not a production release. Only public certificates are archived; private
keys and board settings are excluded.

After testing, app-only OTA restores `idf61-listen48-8c1f2d`, ELF
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`,
with verified Wi-Fi/playlist/settings persistence and three stopped states.
Controller exit 1 retains the headroom failure; restoration itself succeeds.

## Offline replay

From the worktree root, run:

```text
python -B tests/results/esp32c3-aac-growth-tls-20261010/review.py
```

It uses frozen test sources to reproduce numeric results and verdicts from
the raw observations and checks exact restoration. Replay PASS means evidence
agreement, not 16/16 physical success. `index.json` covers all archived files
except itself. Do not run the retained physical/build controllers as a replay.

Remaining work is to establish applicable allocation requirements, especially
late TLS requests and other record/transition patterns, before changing the
reserve policy or interpreting a lower headroom threshold as sufficient.
