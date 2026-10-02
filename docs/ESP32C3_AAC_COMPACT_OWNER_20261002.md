# Combined lossless SBR owner: production adapter experiment

The guarded QEMU experiment and the real decoder adapter now combine five-entry
smoothing pointer tables with PS-control relocation. Requested SBR storage drops
from **55,128 to 49,708 bytes** (5,420 bytes). The unguarded allocator probe measures
**55,296 to 51,200 bytes: 4,096 bytes saved**. No PCM arithmetic is compressed.

This remains an experimental build. Public HE-AAC playback is **not qualified**.

## Implementation and checks

The adapter scopes vendor calls with FreeRTOS TLS slot 1 (slot 0 belongs to
pthreads), keeps owner state per decoder and requires two TLS pointers. A pinned
archive and compiler-derived ABI offsets select the patched native functions;
the SDK archive itself is unchanged. The shared symbolic reset repairs the stale
core offset and preserves initialized PS state. Allocation failure returns a
memory error with no PCM; it does not accept an AAC-core-only fallback.

QEMU evidence includes:

- 81 paired comparisons across six synthetic formats and five captured streams,
  all with zero PCM error;
- all 24 smoothing FIR combinations, checked table initializers and allocation
  guards, reset and failure cleanup;
- the actual production adapter with two failed allocations, two concurrent
  tasks and two resets under heap poisoning;
- exact comparison of the adapter's format sequence with retained native PCM.

The known implicit-SBR change with an identical ADTS header still needs a restart.
That limitation is recorded, not counted as a full-format pass. QEMU instruction
counts are not physical CPU/cache measurements.

## Board results

Awake QIO 80 MHz build, safe IRAM profile, fixed TCP PCB pool and dynamic TLS.
The exact image, configuration and manifest are in
[`firmware/development/esp32c3-aac-compact-owner`](../firmware/development/esp32c3-aac-compact-owner/).

| Check | Result |
| --- | --- |
| OTA while playing controlled AAC-LC | PASS; 21.453 s, target ELF/slot verified |
| Wi-Fi, playlist and settings after OTA | Unchanged |
| Public AAC-LC 128 kbps over HTTPS, 60 s + WebUI polling | PASS; mean CPU 53.73% |
| Public MP3 256 kbps over HTTPS, 60 s + WebUI polling | PASS; mean CPU 65.26% |
| HE-AAC/HE-AACv2 64/32/16 kbps over HTTPS | FAIL: allocation/TLS failures or request failure |
| Same HE cases over HTTP | FAIL: network allocation pressure or timeouts |
| Idle recovery after HTTPS set | FAIL: 2,764 bytes below baseline; ownership not isolated |
| Idle recovery after HTTP set | PASS |
| Restore saved station and settings after each set | PASS |

Failed runtime requests include 1,700-byte network buffers when the largest
free block is only 1,408–1,664 bytes. The smaller SBR owner removes one obstacle,
but the complete radio still lacks headroom. This evidence does not establish
a decoder leak, and the failed cases have no valid steady-state CPU benchmark.

Full [evidence](../tests/results/esp32c3-aac-compact-owner-20261002/) includes raw
QEMU logs, source snapshots, build logs, sanitized board diagnostics and failed
verdicts. Run `python tests/test-aac-compact-owner.py` to verify retained results.

Production's numerical tolerance is now +/-3 PCM units per channel/sample;
this lossless layout still requires exactly zero. Lossy QMF/PS experiments and
their cumulative precision are tracked separately. No default is promoted here.
