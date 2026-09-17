# Before-demux allocation experiment, 2026-09-17 — rejected

Allocate decoder state/scratch before OpusWorkspace, same sizes/guards.
Host ownership/fault tests pass, but9/10 final board diagnostics still show
scratch OOM;0/10 continuous windows. Runtime source change reverted.
No ASM speed claim. Full evidence is stored in the early-reserve directory.
