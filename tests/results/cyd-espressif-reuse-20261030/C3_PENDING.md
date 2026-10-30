# C3 public decoder input-prefix checkpoint

The C3 service now retains a successful vendor call's unconsumed short input
and appends the next packet before retrying. Complete packets remain borrowed
without copying. This uses the same checked task-owned helper as CYD through
a C3 forwarding header; no additional IDF component is selected.

The change applies only to the public simple-decoder branch. Native AAC keeps
its existing consumed-input handling on `BUFF_NOT_ENOUGH` and its zero-input
PCM retry. The private Vorbis repair configuration and code, task placement,
priorities and stack sizes are unchanged.

Pending capacity is released on generation changes, codec changes, failed
opens, terminal failures and EOF. The maintenance quiet predicate includes
that owner before acknowledgment. Vendor EOF with remaining bytes and no
progress reports `DATA_LACK`; empty EOF drains normally.

## Verified behavior

- **39 actual generic-loop cases** under GCC `-Werror`, ASan, UBSan and leak
  detection: the original 30 cases, a native AAC consumed-on-resize/zero-input
  retry regression, and eight vendor input cases. Incrementing encoded bytes
  check that one-byte, borrowed-suffix and owned-suffix schedules lose or
  duplicate no bytes. Other cases check first-retain OOM, growth OOM, OOM after
  partial consumption, truncated EOF and empty EOF. Pending storage is cleared
  on every exercised terminal path.
- **152 whole-owner maintenance cases**: 37 native-staged, 39 native-direct,
  37 custom-staged and 39 custom-direct. The new case blocks a public vendor
  call with an allocated pending owner, verifies that maintenance cannot
  acknowledge early, then checks cleanup, Stop cleanup and a following native
  AAC Play. All **13 existing semantic controls** reject their deliberately
  broken frozen source at the expected assertions.
- The current production `audio_service.c` compiles with actual RV32 GCC
  15.2 and the existing `build-c3-transfer` compilation database/configuration.
  The fresh object and log are retained. This compiles one translation unit;
  it does not link or execute C3 firmware.

Codec, RTOS, HTTP, allocator-accounting and output boundaries in these host
tests are explicit seams. They do not establish real decoder PCM quality,
private allocator behavior, radio/TLS/DMA timing or physical audio performance.
The separate [Espressif reuse design](../../../docs/CYD_ESPRESSIF_VORBIS_REUSE.md)
records the actual public-vendor QEMU diagnostic and remaining production gates.

## Evidence

Final campaigns:

- `.build/c3-vendor-pending-segment-20261030-03/`
- `.build/c3-vendor-pending-maintenance-20261030-01/` — focused new owner case,
  all four variants.
- `.build/c3-vendor-pending-maintenance-20261030-02/` — full matrix and controls.
- `.build/c3-vendor-pending-gcc-20261030-01/`

All processes are terminal. Every current source hash matches the final
reports; all seven changed/new C3 files use LF. Earlier segment attempt 01
failed before producing compiler output; attempt 02 was a passing preliminary
run before LF normalization. Their available files/logs remain separate and
do not replace the final run.

`c3-pending-captures.zip` stores reports, commands, logs, generated/frozen source,
platform seams, real host executables, the RV32 object and exact source inputs.
It deduplicates identical content into `blobs/<sha256>` members. The
`c3-pending-manifest.json` maps all 622 logical paths to 222 physical blobs and
hashes every blob plus the archive. SDK configuration and compilation-database
locations/hashes are recorded without copying unrelated build scratch files.

Archive SHA-256:
`001350eafc6c77e9167891324df03ef57d99a7c22a58b15f6d62c418d43f9500`.
