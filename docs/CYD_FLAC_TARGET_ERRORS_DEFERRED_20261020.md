# Deferred CYD FLAC target error/backpressure extension

Stage 12's existing custom decoder, 520-case adapter gate and three-case actual
audio-task gate remain in place. The additional task-level allocation-failure,
backpressure and exact-control work was stopped by an automatic content review
with the stated reason: "This content was flagged for possible cybersecurity
risk." This is a tooling restriction, not a confirmed firmware vulnerability.
The blocked work is deferred; it was not rephrased or delegated to bypass the
restriction, and its unqualified changes are not integrated into production.

The ignored draft is retained under `.build/cyd-flac-task-errors-draft-01/`.
Attempts 01/02 stopped on orchestration/compilation errors before QEMU.
Attempt 03 completed its SDK compilation but correctly rejected a source
snapshot changed by the concurrent early-MPI CMake/Kconfig integration; zero
runtime cases qualified. Attempt 04 used the stable metadata and reached QEMU,
then its runner ended with `AssertionError: []` when expected case markers were
absent. Zero new cases or semantic controls qualified. No successful error-path
gate or production defect is inferred from these rejected attempts.

After the agent stopped, read-only process inspection found no remaining draft
process. The runner's terminal traceback and nonpassing report were retained;
the parent did not restart the test or modify the draft. Relevant retained
artifacts are `attempt04-terminal.log`, `attempt04/report.json` and its command
logs. These remain development evidence, not a completed acceptance archive.

Resume later through the normal approved workflow. Remaining requirements are
unchanged: actual-task allocation failure/cleanup/reopen, full-queue cancellation,
exact semantic controls, watchdog/resources and physical vendor/custom A/B.
See [the transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md) and
[FLAC design](CYD_FLAC_TRANSFER_DESIGN.md).
