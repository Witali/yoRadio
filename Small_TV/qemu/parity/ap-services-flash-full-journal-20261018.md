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

## Browser setup and continuing integration

The separate `codex/small-tv-browser-wifi` branch is committed/pushed as
`2c28b998`. Its exact-current BC68/20B real Chrome gate passed 93 browser and
18 raw-persistence/role checks over three independent setup/cold VM pairs:
normal discovered SSID, literal `manual`, and manual entry after a real empty
scan with the external AP offline. Invalid/cancelled input preserves the raw
record, AP role and boot count; successful setup reaches STA DHCP/SNTP and
cold persistence. The proof retains two failed harness-development attempts,
all 25 input hashes, 13 raw gzip artifacts and two actual screenshots.
All six browser VM PIDs were verified absent. This remains standalone evidence,
with no retroactive addition to this frozen full suite.

The full controller remains alive with its original process identity. QEMU
photo controls, active-photo reinitialization and all six setting-during-fade
cases passed for both firmware variants. Real initial Wi-Fi setup/persistence
and parsed weather HTTP have also passed for both. No terminal full result
exists yet. All 533 frozen inputs were rehashed after the browser work and
still match exactly.

The current H10 supervisor/workload/guard/VM identities were again verified
live. Its corrected start metadata is preserved in `c0fc3cb3` (also cherry-picked
as `b1bba736` in the browser branch); no runtime input or process was replaced.
A file-only diagnostic audited 63 complete cycles, 512 HTTP requests and one
external AP outage over 1070.210754 observed guest seconds. All 31 runtime
inputs and start record match; UART has one ROM boot and no panic. Status is
explicitly **pending**: this prefix is not a completed 86400-second H10 run.

## Separate JPEG table correction

Branch `codex/small-tv-jpeg-uploads` committed/pushed21633207 fixes reserved
all-one Huffman words and invalid unused AC symbols. The literal factory and
BC68 accept121new malformed cases; candidate0592 rejects them during preparation.
The exact same DHT harness/fixtures, public JPEG checks and real HTTP before/after
support the correction. The new candidate changes onlytjpgd.c among59production
inputs and adds32app bytes. Its scoped evidence is in
`jpeg-dht-validation-20261018.json` in that separate branch.

Its own full regression freezes539inputs and was revalidated live as controller
20380, creation2026-10-18T13:08:55.949427Z. This BC68 run and its533inputs were
not changed; all533were rehashed unchanged after that correction was committed.
BC68 regional persistence/NVS migration have passed and natural calendar cases
are now running. A terminal pass here still cannot validate candidate0592.
