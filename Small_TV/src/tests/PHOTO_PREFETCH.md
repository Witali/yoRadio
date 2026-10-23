# Show the first ready photo without warming unrelated slots

Checkpoint 2026-10-23. The previous real LCD check found a startup regression:
23.389901 guest seconds to the first complete native photo, versus 20.565822 for
the same stock profile. Slot 0 was ready around 5.3 seconds, but the slideshow
waited while the worker held its codec ownership for four unrelated warm-ups.
The isolated new timing criterion fails on that retained old measurement.

## Scheduling and invariants

`factory_photo_prefetch` in the display module chooses one next eligible source.
The original five-slot round-robin selector is shared with `factory_photo_step`.
At startup only the next photo is requested, and only for the photo theme. While
idle after a completed fade, the next source is prepared before its timer event.
No unrelated background decode is started during fade phases 1, 3, 4 or 5.
Selection phase 2 rechecks readiness if the source changed meanwhile.

The selector waits for a valid pending next slot instead of jumping to a later
cached photo. Empty sources and stable invalid/unsupported inputs may skip.
The worker exposes a failed-source mask only when its recorded length still
matches current settings. Normal upload invalidation clears both readiness and
failure state, including same-length replacements. Transient read/allocation
failure and foreground cancellation remain retryable. Source serialization,
bounded queue, foreground ownership and durable cache publication are unchanged.
No new sleeps, polling delays or network/display coupling were introduced.

## Evidence

- 6,077 native assertions plus direct privacy controls and 12 inventory omission
  controls pass. Policy cases cover initial readiness, later ready slots, mask
  changes, wrap, empty/bad sources, idle waits and fade preservation. Real worker
  tests cover damaged-source failure publication, obsolete lengths, read retry,
  foreground cancellation with zero cache writes and subsequent successful retry.
- A compiled normal policy control passes. Six compiled unsafe variants fail real
  assertions: ignore fade, ignore failures, ignore configured sources, prefer a
  cached later photo, wrong round-robin and unrelated cache warm-up. Compile or
  loader failures are not counted as rejection.
- 13,440 transitions execute literal stock and current native RV32 instructions:
  32 masks, six initial fade phases, five initial slots, repeated events, blocked
  steps and changed masks. Selection, duty requests, returned state and completion
  flags match. This is an output-boundary control check, separate from real pixels.
- Six artifact checks pass. The reviewed inventory is 176 selected stock /217
  app /532 total source functions, without claiming whole-image equivalence.

Five owned cold QEMU processes, all stopped/reaped, exercise the actual main app:

| Profile | Complete frames | First completed frame, guest seconds |
| --- | --- | --- |
| All five valid photos | 28 | 5.560901 |
| Mask 10, delayed actual night synchronization | 22 | 5.914457 |
| Empty mask / dark restoration | 4 | 2.240142 |
| Damaged source 0, other four valid | 22 | 7.114731 |
| Next process over the actual warm all-photo flash | 28 | 2.251859 |

All 104 frames /5,990,400 pixels match full literal stock replay, with no crop,
tolerance or difference mask. The damaged-source fixture explicitly clears the
JPEG SOI byte at `0x200000`; its skip is a declared input-error correction, not
a hidden pixel difference. Other photos remain in order. Night restoration uses
the actual calendar observed at `backlight_update`, retaining the known stock
brightness bug fix. Seventeen negative report controls reject incomplete scenes,
unready selection, later startup, unrelated warming, missing cold frames/writes,
wrong duty, missing synchronization or process reap and false network labeling.

The first valid photo is shown with readiness mask 1: later sources are still
uncached. The earlier current-app pilot measured 5.619954 seconds and the same
28 full frames. Startup measurements include warm-up, using the guest timer;
host load and physical-board timing are not inferred from them.

The cold process starts with the exact entire flash from the stopped warm process,
without reseeding settings or resetting NVS. Hardware breakpoints on the two
unique actual JPEG platform callbacks, `flash_program` and `flash_erase`, fail on
any attempted JPEG write/erase. Neither is hit. All candidate sectors remain
exact, and the entire 4 MiB also remains byte-identical in this fixture. These
traps cover JPEG storage; they do not claim a global absence of SDK NVS writes.
Warm and damaged-input runs preserve every byte outside declared NVS/preferences
and generated candidate extents, including all source photos and immutable media.

App SHA: `abf14143e9b0c07fe201c9417a8135b17bd61ea618b2b21cb361cda148eb46e6`.
ELF: `896558f5fef83461fb1f549f65e5cb63578e50d33f2e1dccc4766ac5ee34ab94`.
Source: `64edeef96caf232da8b84e7d167e132241a88605195dba7b9d8c246b0b46f02d`.
App 1,466,800 bytes /69,200 partition bytes free, DEBUG off. Matching assets
1032119B and codec/layout identities are unchanged. Saved under
`firmware/development/small-tv-esp32c2-reconstructed/`.

Exact source/raw evidence:
`Small_TV/qemu/parity/photo-prefetch-validation-20261023.json`. PNG/RGB hashes and
ten full physical before/after images can be independently verified. Sector and
payload deduplication reuse previous evidence instead of copying full dumps.

## Reproduction and scope

```powershell
pwsh -File Small_TV/src/tests/run.ps1 -PythonPath SDK_PYTHON
python -B Small_TV/src/tests/photo_prefetch_mutation.py --output NEW_MUTANTS
pwsh -File Small_TV/src/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
python -B Small_TV/src/tests/photo_cache_frames_qemu.py --qemu-root FROZEN_QEMU --dependency-root C:/Work/yoRadio --output NEW_RUN
python -B Small_TV/src/tests/verify_photo_prefetch_evidence.py --proof Small_TV/qemu/parity/photo-prefetch-validation-20261023.json
```

This closes the measured first-photo delay and current photo LCD/cold-hit cases.
It does not close classic/simple/dial clock continuity during foreground decode,
the complete target JPEG memory/stack/format/fault matrix, publication power cuts,
network lifecycle/churn, whole-image audit/full/24h/hardware acceptance. A complex
valid next photo may still take longer than its prefetch interval; the UI waits
for that source instead of displaying partial data or skipping it. No physical
device operation, shared SDK change or frozen QEMU change was performed.
