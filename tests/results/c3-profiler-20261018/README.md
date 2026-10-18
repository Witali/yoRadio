# C3 diagnostic sampler task lifetime

The host test compiles the actual `cpu_profiler.c` with ASan/UBSan. Its kernel
seam deletes all task names when the scheduler resumes, reproducing the lifetime
explicitly documented by `TaskStatus_t.pcTaskName` in pinned IDF `task.h`.

Two negative controls precede the fix:

- [Original sampler](negative-name-uaf.log): ASan heap-use-after-free in
  `cpu_profiler_sample` when classifying the first task name.
- [Name copy alone](negative-reused-tcb.log): the reused TCB test fails because
  the old task's runtime counter is subtracted from the new task's smaller one.

The fix copies bounded names while the single-core scheduler remains suspended,
then resumes before logging. This adds 512 diagnostic-only static bytes, without
growing the sampler stack. Task identity includes the copied task number.
The static assertion deliberately prevents applying this lifetime strategy to
multi-core targets; CYD uses registered handles and no borrowed task-name reads.

[Final report](report.json): counter32 and counter64 both pass deletion, delayed
stack survey, TCB reuse, runtime wrap, zero interval and unavailable snapshot.
The host deletion/scheduler seams do not qualify actual kernel timing, interrupt
latency or physical playback. No on-board crash is claimed. Quiet C3 builds do
not compile the diagnostic sampler.

Pinned IDF `9a97f6c5`/GCC 15.2 builds clean source `ca69e1f9` with runtime stats
enabled and the tested radio profile. The saved [image manifest](../../../firmware/development/esp32c3-oled-native-profiler-fix/manifest.json)
records 1,477,808 bytes and its ELF/image hashes. Production logging stays off;
this image proves compilation of the sampler branch, not collected CPU data.
The [full Clang report](../native-lint-20261018/c3-profiler/report.json) completes
all 49 own units, 106 warnings, zero errors. Eight additional dead-store warnings
are the diagnostic percentages consumed only by logs compiled out in this profile.
