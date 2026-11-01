# Actual CYD public AAC-Plus tasks, 2026-11-01

Native campaign02 passed all 48 cases with the actual ESP-IDF 6.0.2 stream,
decoder and output tasks, whole audio/state/health/registration/output TUs,
shared settings/normalizer components, and the unchanged public Espressif AAC
decoder archives. These are **same-vendor integration checks**, not independent
AAC numerical or standards conformance. Only HTTP transport and public PDM/GPIO
hardware calls are replaced. There is no board, Wi-Fi, external network,
private decoder ABI, reset hook, production firmware, OOM injection or artificial
output backpressure in this diagnostic.

The original task bindings remain stream core0/priority3/6144B, decoder
core1/priority5/16384B, output core1/priority6/4096B. Both idle watchdogs, light
heap poisoning, assertions and stack canaries remain enabled. The complete
compiler witness joins 17 selected TUs and 450 actual dependencies to frozen
sources. The root-authorized 12-file release is
`73599ab651a72f153e777bc47dec5d816e1e38224e0795195db426da11c1d3e7`;
historical verification authenticates those frozen bytes without requiring
later production sources to remain equal.

Each of the six complete synthetic FDK 2.0.3 fixtures exercises mixed input
EOF, partial Stop/reopen, partial maintenance/resume with consumed and stale
tokens, one-byte input, 257-byte input and 4096-byte input. Whole PCM and
per-geometry run hashes agree with the committed 36-case public configuration
checkpoint. Stop and maintenance begin only after the real stream task is held
at the independently parsed third ADTS frame boundary and real PCM exists.
Stop forwarding records the actual output-owner discard sequence/time/core,
then proves all input owners and source/driver counters quiet for 25 ticks
before reopening. No ACK or task/control state is fabricated.

| Complete source | PCM bytes | Published PCM rate/channels |
| --- | ---: | --- |
| LC 44.1k stereo | 98,304 | 44,100 / 2 |
| LC 22.05k mono | 26,624 | 22,050 / 1 |
| LC 48k stereo | 106,496 | 48,000 / 2 |
| HE 44.1k stereo | 114,688 | 44,100 / 2 |
| HE 48k stereo | 122,880 | 48,000 / 2 |
| HEv2 44.1k stereo | 122,880 | 44,100 / 2 |

Four concatenated inputs each run under three transport schedules. Before the
application tasks start, ten isolated references (six bases plus four
concatenations) use genuine continuous public open/process/get-info/close
handles with whole remaining input, real EOS and an empty drain. No reference
concatenates separate decoded PCM hashes. The application matches each full
continuous reference hash and every metadata run:

| Continuous observation | Complete PCM bytes | Actual PCM runs |
| --- | ---: | --- |
| `LC_RATE` | 204,800 | 44,100/2 then 48,000/2 |
| `LC_LAYOUT` | 124,928 | 22,050/1 then 44,100/2 |
| `LATE_HE` | 83,968 | 22,050/1 then 22,050/2 |
| `LATE_HEV2` | 57,344 | 22,050/1 throughout |

The last two are truthful public decoder observations. Late SBR does not
restore the nominal 44.1k rate here, and unchanged-ADTS late HEv2 does not restore
nominal stereo. Matching these observations does not qualify full late-SBR/PS
transition support. Both inputs do consume all encoded bytes and drain without
a public error. Production publishes actual PCM geometry and the `PCM` label;
it does not infer a source AAC object type from that output.

The final census is 60/60 application decoder handles and HTTP clients closed,
1,232 process calls, 48 real EOF flushes, 2,174 ordered zero-header/LEGACY-layout
metadata stamps and 7/7 PDM channels deleted. No output buffer resize was
needed. Whole source PCM is hashed before forwarding to the real output TU and
checked immutable afterward; actual configure/write/flush/preload/discard
paths execute. Driver byte counts are observations, not an independent
resampling, normalization or physical sound oracle. Free stack was
3612/13376/2368B for stream/decode/output; final heap213436B, minimum82224B,
largest internal block110580B. These QEMU figures are not radio/TLS/TFT memory
margins.

Native01 remains a failed compile before QEMU: SDK driver exit1, real SDK child
exit2. The new diagnostic reference TU included `freertos/task.h` before
`freertos/FreeRTOS.h`. The exact 111 failure/error records, original logs,
source snapshots and statuses remain unchanged. Native02's sole source
correction adds the required preceding FreeRTOS include; no production byte,
private decoder state or deadline changed. Native02 SDK/QEMU both exited0
(205.39s/18.156s). The data-only witness rejects all 40 contradictory transcript
copies and verifies the originals stayed unchanged without another native run.

Run the read-only checkpoint verifier from the repository worktree:

```powershell
python -B -X utf8 tests/results/cyd-aac-playback-task-20261101/verify.py
```

`captures.zip` preserves original evidence with deduplicated whole-file blobs.
Compiled images, objects, archives, generated binary fixture storage and
contact-bearing installed headers remain local whole, with size/hash omission
identities. No omitted payload, compiled program or archived Python code is
executed by the verifier. Original AAC fixture bytes are synthetic test data;
raw decoded PCM is not published. Current reviewed canonical readers recount
both complete original public and task transcripts.

The new controller supports preparation without a production freeze, tool
preflight and a fresh native campaign. Coordinate the latter with source owners
and the shared SDK build slot. Full public/implicit codec conformance, injected
OOM/backpressure, Wi-Fi/TLS/TFT resources and physical audio remain separate
qualifications. Deferred private/compact AAC owners are not implemented here.
