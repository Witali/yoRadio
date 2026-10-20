# CYD early MPI mutex evidence — 2026-10-20

The canonical source is integrated and **disabled by default**. Fresh canonical
host checks and the isolated two-core ESP32 SDK/QEMU fixture passed. Production
firmware exports, the actual radio's pre-application mutex state and physical
benefit remain open. This archive makes no RAM, fragmentation, latency, audio,
RF, DMA or hardware improvement claim.

The production helper acquires and releases the existing SDK-owned MPI mutex at
normal `app_main` entry before application services. It changes no cryptographic
calculation, private mutex value or task profile. ESP-IDF's void lock API aborts
if its lazy mutex allocation fails; this is not a recoverable OOM API.

Authoritative raw reports are [host02](reports/host-02.json),
[QEMU01](reports/qemu-01.json), [aggregate qualification](reports/qualification-01.json),
[preflight02](reports/preflight-02.json) and the independent
[initial review](reports/review-01.json) / [closure](reports/review-02.json).
Original report bytes have not been rewritten. [HOST.md](HOST.md) states the
precise observations and boundaries.

`host01` is historical ordering evidence only. Its duplicated network-stack
constant was 7168 while the actual CYD profile uses 6144 bytes, invalidating its
board-profile claim. Host02 removes the duplicate constants and board stub;
GCC `-H` confirms the frozen actual `board_config.h` in all five builds.
Prototype reports and errors under `reports/history/` are historical, not fresh
canonical qualification. SDK-pin rejection changes the expected pin in a test
runner, without modifying the installed SDK checkout.

`path-map.json` maps each selected original path and content version to stored
raw bytes, lossless gzip bytes or an explicit omission with size and SHA-256.
Content-addressed payloads avoid long Windows paths and duplicate snapshots.
Multiple hashes for the same source path preserve historical versions.
`bindings.json` connects original JSON hash fields to their mapped payloads.
`current-verification.json` records the archival before/after check, not a claim
that a later working tree still has the same contents. `index.json` identifies
the authoritative reports and status.

ELF, application/full-flash/ROM images, objects, archives and tool executables
are omitted. Their byte counts and hashes remain in the mappings and original
bundles. Replaceable external compiled-header payloads and selected historical
build details may also be omitted; the explicit frozen SDK pins and sources are
retained. Large compile databases, Ninja/dependency text and other large text
are gzip-compressed without changing decoded bytes. Unreferenced working-build
and temporary files are outside this compact archive's scope. Nested original
manifests are preserved historical documents and can reference omitted files;
the root manifest defines this archive's complete file set.

Run the standalone verifier with Python 3.9 or newer, from any directory:

```text
python -B tests/results/cyd-early-mpi-20261020/verify.py
```

It reads only this archive. It checks the full root manifest, decoded payload
bytes, source/report mappings and JSON hash bindings, authoritative report
statuses and selected exact runtime markers. It does not reconstruct omitted
binaries, redisassemble code, rerun a test or establish physical behavior.
