# Packager preparation — archive not yet written

Only this new ignored prep folder may be changed in this preparation task.
Do not invoke the packager until root provides authoritative terminal PASS and
the exact final five-profile qualification SHA. No source, old MPI archive,
frozen campaign, SDK, firmware, Git metadata or build is modified here.

The default packager invocation collects and validates selected inputs, then
writes a fresh plan receipt only under this ignored folder. Sealing additionally
requires `--write-reviewed-archive`. The exact new destination is
`tests/results/cyd-early-mpi-sdk-20261020/`; existing destinations are rejected.
Every input and the complete exporter snapshot must remain unchanged before and
after. Root must keep source HEAD 1190 frozen through sealing.

```text
python -B -X utf8 .build/cyd-early-mpi-sdk-archive-prep-01/build_archive.py --backend-report-sha256 <ROOT_FINAL_SHA> --attempt attempt-01
python -B -X utf8 .build/cyd-early-mpi-sdk-archive-prep-01/build_archive.py --backend-report-sha256 <SAME_SHA> --attempt attempt-02 --write-reviewed-archive
```

Both immutable markers and the fixed original qualified report are required.
All two-plus-five selected qualification/marker hash maps, baseline pointer
bindings and complete frozen seeds/scripts/evidence are followed. Wrapper raw
commands, stdout/stderr/terminal receipts and actual compiler/ELF proof logs are
preserved. Selected canonical project/SDK text is stored; binaries are explicit
identity-only omissions. Long paths flatten into content-addressed payloads.
Only the raw reports and archive metadata receive readable top-level names.

Source snapshots are current at HEAD 1190; preparation failure/readiness files
are labelled historical and retained byte-exact. The first failed raw-LFS
comparison has no saved raw stderr and is not relabelled. No audit or original
MPI README/HOST is rewritten. The new README/HOST/SDK summary becomes immutable
when sealed; any root appendix afterward needs its own additive provenance and
manifest extension.

The offline verifier checks manifest, gzip/raw hashes, JSON bindings, seven
profiles, exact bool/config/seed scope, receipt/evidence, OTA, Xtensa identities,
actual call traces via nm/disassembly and recorded ELF data words, ordinary
allocator pointers, PDM-only IRAM and separate known warning classes. This
remains evidence integrity and selected static entry checks, not application or
device runtime testing. No new crypto/network/device/SDK qualification run is
performed by these tools. Deferred codec extensions and AAC are excluded.
