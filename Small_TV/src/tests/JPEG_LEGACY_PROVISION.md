# Legacy JPEG resource adoption

Checkpoint 2026-10-23: matching older native assets can be retained during an
application-only update. This does not install or reset a physical board and
does not authorize replacing a user's photo bank with packaged defaults.

## Permission and data invariants

`jpeg_guard_verify` remains read-only. A separate startup-only
`jpeg_transport_provision` revokes all old ports and holds one shared I/O/time
budget until a complete physical guard succeeds. Ordinary ports are unavailable
during bootstrap. The ESP-IDF entry performs the existing complete raw partition
table/MD5/flags verification, SDK cross-check and physical/configured geometry
check before this step. A missing/foreign partition never reaches a stamp write.

The generated `jpeg_layout_stamp` binds 64 canonical bytes to an existing resource
descriptor in protected padding. Its SHA is checked even when the physical
stamp is already valid. Current location: `0x28f720`, within one program page.
The 64-byte value is `STVOWN1\0`, 32 bytes ownership ID and 24 bytes FF.

For a matching existing stamp, only the normal physical guard is needed; owned
cache/scratch is allowed to contain data. No stamp program/erase is issued.

For missing/torn legacy stamps, all of the following must succeed:

1. Verify the complete immutable/layout descriptors and all 27 physical payloads.
   The prospective stamp is supplied by an explicit read-only overlay solely to
   validate its descriptor/hash; this step grants no capabilities.
2. Fresh double-read the existing stamp. Every observed zero must also be zero
   in the canonical target, so only monotonic 1-to-0 completion is possible.
   If any header byte is nonerased, the identity must already be exactly complete.
3. Double-read every byte of every generated candidate extent, including spare
   sectors. All must be FF. Photos, settings and other protected bytes are not
   scanned or reclassified. A single silent read cannot hide occupied data.
4. Recheck compatibility; program the 32-byte identity first if incomplete, then
   fresh double-read its exact readback. Only then program the 8-byte header if
   incomplete and double-read its exact readback. The 24-byte FF tail is untouched.
   No erase, read-modify-write or surrounding animation page/sector program.
5. Fresh double-read all 64 bytes and repeat the complete physical guard.
   Check the last hash callback's deadline before publishing ordinary capability
   maps. Any error leaves them revoked, even if the stamp physically completed.

The bootstrap writer independently restricts both address and data. It has no
erase callback, no writable sector capability and no source supplied by HTTP.
Startup permits at most 40 program bytes and zero erases. Discovery and all
verification phases share the original count/byte/time limit; fallback cannot
reset the budget. Counters describe bytes submitted to SDK callbacks, not a
measurement of chip command count.

A torn stamp can resume on a later boot only while the same immutable/blank/
monotonic and ordered-state preconditions still hold. An incompatible zero is refused. An occupied
unclaimed region, foreign stamp or resource mismatch is retained, not repaired by
erasing it. Clocks/network can start with photo-cache access disabled. These are
content/layout checks, not firmware publisher authentication. They do not claim
automatic conversion of arbitrary stock/foreign assets into our native layout.

An initial, uncommitted single-program prototype accepted a complete foreign
header with a compatible but wrong ID as though it were a torn record. A new
negative test failed before the ordered protocol fixed it. Recovery now accepts
arbitrary torn bit subsets within the ID phase with an erased header, or within
the header phase with a complete ID. Unsupported write orderings are refused.
Historical failing sources/logs are retained separately from final acceptance.

## Evidence

Independent host NOR/Windows SHA contracts passed 23,409 scenarios:

- 786 occupied-byte cases across every candidate sector;
- 524 single hidden-read cases across every candidate sector;
- 452 partial-stamp recoveries, including 128 non-prefix bit patterns;
- 352 incompatible stamp bits;
- 14,599 injected read-failure and 6,325 hash-failure cases, spanning every physical
  read/provider point plus repeated final boundaries;
- exact global quota/deadline boundaries and stale-port revocation;
- complete 4 MiB preservation outside the exact 64 bytes, with synthetic data in
  every photo slot, boot/application region and settings.

Eight compiled unsafe provision variants and 14 previous transport variants fail
actual assertions; compile/loader failure is not counted as successful rejection.
Ordinary transport's 31 cases pass. Generator qualification passes 12 rejected inputs
and 12 controls; existing layout and cache codec IDs remain byte-identical to
`d6adaa7d3`. Current native app passed 5,995 assertions plus direct privacy controls,
and 6 artifact checks passed. This inventory is 176 factory/212 app/527 total source
functions, not proof of whole-image semantic equivalence.

The actual main application ran in twelve owned cold QEMU processes:

| Fixture | Authorized | SDK stamp bytes |
| --- | --- | --- |
| Erased legacy stamp | yes |40 |
| Same persistent image, next process | yes |0 |
| Non-prefix torn ID, erased header | yes |40 |
| Complete ID, erased header | yes |8 |
| Complete ID, torn header | yes |8 |
| Last candidate byte occupied | no |0 |
| Incompatible foreign stamp | no |0 |
| Complete foreign header, wrong compatible ID | no |0 |
| Immutable payload changed | no |0 |
| Unknown raw partition flag with valid MD5 | no |0 |
| Valid stamp, nonempty owned candidates | yes |0 |
| Application update over real retained old-main flash | yes |0 |

The last fixture is decompressed from the previous committed main-app proof,
retaining its actual SDK NVS, entire photo banks and cache. Declared synthetic
dial/mask preferences disable unrelated cache warm-up; the replacement application
then boots with those existing resources. Whole physical comparison after each stopped VM verifies every
byte outside NVS and the expected stamp; persistent cold/upgrade cases also
require exact NVS. Every fixture preserves all five photo slots and the entire
preferences sector. Read-only QMP observations use storage/type offsets from the
exact ELF to verify real authorization/counters; HTTP readiness alone is not
treated as authorization. No RAM, PC or executable guest state is patched.

This is a storage/bootstrap gate, without LCD/RF/network acceptance criteria.
The partial-stamp fixture models interrupted data; it is not a physical power-cut
during SDK programming. Normal SDK initialization of previously empty NVS is
allowed and distinguished from the bootstrap's zero-NVS-write capability.

RV32 standalone core object: 1,331 combined text/readonly bytes, 0 data/bss; largest
individual compiler frame 464 bytes (`read_twice` 304, `write_part` 96). These are not whole-call-chain
stack or complete application heap measurements.

Development app 1,466,576 bytes, 69,424 app-partition bytes free, DEBUG off.
App SHA: `034287c7102784fdf2fb44f374d5ef6408dabb370a7276637381a94059b3f304`.
ELF: `bb7fd7a180a5536b031531653fa84d29b4cdaa3e22439d7c11fd84680f6f0da6`.
Source: `1d1f52ce1499c15e6a1fefdf1b2f412c69fcf2f1d7af1606dbb0702b243a8202`.
Assets remain 1032119B; layout 44268211 and codec B33BC0A1 are unchanged.
Exact inputs/raw results: `Small_TV/qemu/parity/jpeg-legacy-provision-validation-20261023.json`.

The 24 complete physical before/after images are stored losslessly as one gzip
base and deduplicated 4 KiB sector deltas, rather than 24 repeated full dumps.
`jpeg_provision/verify_evidence.py` reconstructs every image, checks its full SHA,
independently compares protected bytes and checks the current firmware/source pins.
Six negative archive controls pass, including a forbidden photo write whose
sector, image and report checksums are all updated consistently. Preservation
verification still rejects it. Compressed evidence occupies about 2.2 MB.

## Reproduction and remaining acceptance

```powershell
pwsh -File Small_TV/src/tests/jpeg_provision/run.ps1 -OutputDirectory NEW_UNIT
python -B Small_TV/src/tests/jpeg_provision/mutation_contract.py --fixtures NEW_UNIT --output NEW_MUTANTS
pwsh -File Small_TV/src/tests/jpeg_transport/run.ps1 -OutputDirectory NEW_TRANSPORT
python -B Small_TV/src/tests/jpeg_transport/mutation_contract.py --fixtures NEW_TRANSPORT --output NEW_TRANSPORT_MUTANTS
pwsh -File Small_TV/src/tests/run.ps1 -PythonPath SDK_PYTHON
pwsh -File Small_TV/src/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf
python -B Small_TV/src/tests/jpeg_provision/qemu_main.py --qemu-root FROZEN_QEMU --output NEW_TARGET
python -B Small_TV/src/tests/jpeg_provision/verify_evidence.py --proof Small_TV/qemu/parity/jpeg-legacy-provision-validation-20261023.json
python -B Small_TV/src/tests/jpeg_provision/test_evidence.py --proof Small_TV/qemu/parity/jpeg-legacy-provision-validation-20261023.json
```

Still open: independent full LCD/clock-continuity gate, complete target JPEG
memory/stack/format/fault matrix, real upload/decode/publication power-cut tests,
network lifecycle/churn, whole factory-image audit, current-image full/24h suite
and physical hardware acceptance. Earlier decoder/HTTP tests remain tied to
their original image hashes and are not relabeled as current-image acceptance.
