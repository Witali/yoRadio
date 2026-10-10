# One-second prefill: public HTTPS qualification

## Decision

The overall playback/memory-stability goal remains open. The exact normal-trust
candidate passed **6/10**
original gates in this campaign. Retain the failed checks; do not promote the
candidate to production defaults on the strength of local playback and OTA alone.

- `https:groovesalad-64-aac`: Progressive heap loss in public playback.
- `https:groovesalad-32-aac`: Progressive heap loss in public playback.
- `https:groovesalad-16-aac`: In-playback memory below existing budget.
- `https:groovesalad-256-mp3`: Insufficient actual playback samples.

## Physical observations

Five live HTTPS variants of SomaFM Groove Salad were observed for 60 seconds
each. These are five bitrate/codec variants, not five independent stations.
FFprobe and the unquantized FAAD reference independently identify the source
format; they do not establish sample-for-sample identity or analog audio quality.
TLS certificate verification is enabled. Public audio is not archived.

| Public variant | Reference PCM | Original gate | Min free / largest, B | Lost I2S notifications / write errors | Max status + health, ms |
| --- | --- | --- | ---: | ---: | ---: |
| groovesalad-128-aac | LC, 44100 Hz, 2 ch | PASS | 56,492 / 38,912 | 0 / 0 | 1080.29 |
| groovesalad-64-aac | HE-AAC, 44100 Hz, 2 ch | FAIL | 20,940 / 8,704 | 56 / 0 | 195.70 |
| groovesalad-32-aac | HE-AAC, 44100 Hz, 2 ch | FAIL | 21,020 / 8,192 | 0 / 0 | 191.28 |
| groovesalad-16-aac | HE-AAC, 32000 Hz, 2 ch | FAIL | 21,004 / 6,656 | 0 / 0 | 247.06 |
| groovesalad-256-mp3 | mp3, 44100 Hz, 2 ch | FAIL | 80,440 / 65,536 | 3667 / 0 | 398.04 |

The table's memory/output observations use the supplementary paired window
after a 15-second warmup. Original live verdicts remain unchanged. Their memory
cutoff starts just before Play, whereas the supplementary cutoff starts with
the observation batch just after Play. A borderline early sample can therefore
produce different trend verdicts. The exact pre-Play timestamp was not retained;
the supplementary calculation is not an exact replay of the original gate.

There are 558 health observations, 0
registered allocation failures and 0 watchdog
events. The SDK lifetime minimum free heap is 14,588 B,
including transient setup. This differs from sampled steady-state minima.
Idle recovery gate: **PASS**. Settled free heap changes
from 139,980 to 139,752 B; largest free block
from 114,688 to 114,688 B;
task counts are 16 and 16.

An in-playback heap decline alone does not prove a leak: queued network data and
deferred allocations can also consume RAM. Recovery after Stop and bounded
steady-state behaviour must be distinguished from progressive unrecovered loss.
The existing gates remain 16,384 B free / 8,192 B contiguous, with median start/end
loss tolerances of 2,048 B free / 4,096 B contiguous. No threshold was relaxed.

## Previous evidence and next work

The same image already passed [42/42 local gates, 22/22 short output windows and
15/15 OTA gates](ESP32C3_PREFILL1000_QUIET_20261010.md). The corresponding
[laboratory image passed 34/34 TLS-renegotiation gates](ESP32C3_PREFILL1000_RENEGOTIATION_20261010.md).
Those results remain valid for their recorded scenarios; they do not erase
the public memory failures above.

The supplementary output check also fails for HE-AAC 64 kbit/s: 56 I2S completion
notifications were lost during the measured window. These counters are not a
count of missing PCM samples or audible clicks. MP3 reports playing in
39/103 observations and ends with
`stream read failed`. Its output-window counter includes the subsequent
non-playing interval, so it must not be presented as thousands of audible gaps
during successful playback. The source/network/firmware cause is not established.

Next diagnose the HE-AAC output notifications and MP3 read failure, and isolate
the live HE-AAC memory trajectory and contiguous headroom, separating
bounded TCP/TLS occupancy from retained allocations. Repeat the failing cases on
any proposed fix and preserve local/OTA/format coverage. The goal should close
only after the remaining concrete qualification failures are resolved.

## Identity and restoration

App SHA-256: `e15c8a37a9c06a069e8146b00e305cb5aa176a52cfa4a1d7381fd8d9dca6754a`.
ELF SHA-256: `c313596b699973d3000b768edec9781848bd1741b033da765b6e0a40382c2cd5`.
No application source, codec arithmetic or build default changed in this campaign.
The [previous archive](../tests/results/esp32c3-prefill1000-quiet-20261010/README.md)
contains the build source/configuration audit; its index hash is referenced here.

The controller restored the exact listened application by app-only OTA,
verified settings/Wi-Fi/playlist equality and recorded three stopped states.
Private settings and credentials are not serialized in the evidence.

[Frozen evidence and review](../tests/results/esp32c3-prefill1000-public-20261010/README.md).
