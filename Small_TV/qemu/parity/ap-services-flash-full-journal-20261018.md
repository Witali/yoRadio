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

## Integration progress during the first run

The controller was revalidated alive as PID10836. The host/machine phase
finished and QEMU has passed boot, fallback, netif roles, AP services, startup,
held weather, advanced editor, fragmented/stalled HTTP body and concurrency
(34 checks / 16 paired batches). Photo flows are now running. There is no
terminal full result yet. All 533 frozen inputs still match in the interim audit.

The old app26C6/B44 H10 was deliberately superseded after committed intent and
an exact BC68/20B eight-cycle supervisor/guard preflight (64 HTTP, 4 outages,
9 parsed weather generations). Its 214-cycle incomplete prefix and original
failed/-1 terminal status were preserved. Current H10 is in the separate
`small-tv-h10-ap-services` worktree: supervisor23548, workload5036, guard22392,
VM18128. Its source proof was committed as `ee896b31`; it remains pending.

A standalone actual-Chrome photo gate was added in `codex/small-tv-browser-photo`
commit21943e31 without editing any input of this run. It passed23browser and6
storage controls on the exact BC68/20B candidate: pointer crop resize, selected
RGB pixels, synthetic metadata removal, mobile viewport,12multipart chunks,
cancel/Escape and exact new-process cold readback. This does not retroactively
add a group to the frozen suite or close physical/phone/H10 acceptance.
