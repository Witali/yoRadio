# BC68 / flash QEMU full regression — 2026-10-18

The preceding goal turn made verified progress: shared NOR/cache corrections,
raw settings observer correction, scoped real persistence/NVS and AP service
allocation evidence were committed and pushed. This run tests their integration.

The current firmware is app `bc68d346…`, ELF `4fde010e…`, production source
aggregate `5586ef61…`; QEMU is `20b133d9…` from commit `0860e568d4`.
All 59 generated/production source records match the archived candidate.

Before launch, 533 exact inputs were frozen: 129 test/fixture files and 404
additional production, build, SDK/oracle and relevant QEMU inputs. The exact
list and identities are in `ap-services-flash-full-start-20261018.json`; the
verified detached process identity is in the companion launch record.

This includes the new AP service and raw persistence observer gates. No test,
application, fixture, ELF or emulator input may change while the run is live.
This journal is outside that input set; the source WORK_LOG/WORKING_NOTES
snapshot is frozen, so record live progress here until the terminal audit.

The full controller writes to
`C:/Work/yoRadio/.build/small-tv-functional/ap-services-flash-full-20261018`.
Only its own disposable headless VMs are used. No board is flashed or reset.
The earlier app26C6/B44 H10 process was revalidated alive and is not stopped or
relabelled as validation of BC68/20B. Its previous file-only diagnostic was pending.

Launch is not completion. A terminal full result, rechecked frozen inputs and
separate H10/browser/hardware evidence are still required. The known CYD PHY
assertion reproduced before and after the flash patch remains a separate
emulator defect; passing Small TV tests does not close CYD compatibility.
