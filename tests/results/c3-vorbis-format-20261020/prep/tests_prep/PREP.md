# C3 canonical-test proposal (source-only)

The proposed/ tree maps directly to repository-relative destinations. It contains
nine files: the frozen native validator, its eight host tests, and the minimal
C3 target project/caller/fixture/README. No controller, SDK launcher, compile
helper API change or duplicated production implementation is proposed.

Two deliberate source adaptations are recorded in input-pins.json: the host
fixture lookup moves to the target tree, and the project takes an explicit
reviewed setup SHA so independent baseline/candidate/old-guard freezes can use
the same caller. Output/ABI/archive pins stay fixed. Caller, fixture, root CMake,
partitions/defaults and validator remain byte-identical to their frozen inputs.

The already terminal root-owned baseline is diagnostic: its qualification says
REGRESSION_REPRODUCED, passed=false, format_acceptance_qualified=false, 285 native
lines and 204 exact-pair packets/2452224 PCM bytes. Its report, actual RV32 macro
context, merge recipe and QEMU receipt are pinned only as historical inputs;
this prep does not modify or rerun them. Current candidate/control campaigns are
not read or changed, and no result is inferred for them.

Integration tradeoff: this is a small reusable target plus a strict offline
protocol oracle, not a one-command campaign manager. Root must keep the manual
source/tool freeze, exact RV32 macro context, bounded process receipts, flash
recipe and final semantic review described in the README. Future SDK/compiler/
archive changes deliberately require new pin review. The changed CMake setup
input is source-reviewed only; no target build is claimed for this proposal.

The eight adapted host tests passed (exit0, 8 methods, 0.827s). Their actual
receipt/logs are retained here; source-relation.json proves every proposed delta. No SDK/compiler/preprocessor,
QEMU, Git, reference encoder/decoder, board/network or production operation is
performed. Canonical source/tests and all previous preps/campaigns remain inputs.
