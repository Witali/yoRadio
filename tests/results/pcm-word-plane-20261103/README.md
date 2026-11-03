# Packed PCM word-plane checkpoint

This component preserves every S16 bit pattern while accessing plane storage
through aligned `volatile uint32_t`. Two samples share a word; partial writes
retain the neighboring sample. The caller still owns bounds, alignment,
initialization, synchronization and storage lifetime.

The current HOST02 capture passed ASan/UBSan: **127 groups, 468228 exact sample
checks and all 65536 bit patterns**. It includes odd sizes, odd-first and partial
writes, reuse, canaries and immutable unaligned caller DRAM. These tests execute
on HOST memory and do not prove that an ESP32 allocation is IRAM-accessible.

The fresh 3 November standalone capture compiled the unchanged helper at O2/O3
with the installed Xtensa toolchain and inspected the resulting instructions.
Actual byte, halfword and FP-memory controls produced `l8ui`, `s16i` and `lsi`
and were rejected. Both current 1728-byte objects have SHA256
`709320d78df7a5eff7f28b11befbb84ab49aea91ca61b1d76eba4859bdbde96a`.
The runner now works without historical objects; `--historical-capture` is an
explicit optional input. No SDK build, linking, object execution or QEMU occurs
in this standalone check.

The installed compiler entrypoints are dispatch launchers. Their hashes and
version logs are retained along with the original attestation and fresh
read-only hashes of the actual gcc, objdump, assembler and cc1 payloads.

## Historical outcomes

| Capture | Original outcome | Meaning |
| --- | --- | --- |
| HOST01 | PASS, historical | Tested the earlier helper bytes; not current-source proof. |
| Xtensa01 | NONPASS | The original inspector incorrectly rejected a legal 32-bit `L32R` literal read. The complete original report and decisive disassembly are retained. |
| Xtensa02 | NONPASS | The intended FP control optimized to a safe integer load. It did not prove rejection of FP memory access. The original report, source and disassembly are retained. |
| Xtensa03 | PASS, historical | Correct controls and explicit readonly-literal inspection; still depended on an old local capture. It does not change either prior NONPASS outcome. |
| HOST02 / current Xtensa | PASS | Current helper contract and reusable standalone runner, respectively. |

The unchanged reports, selected original logs and frozen source bytes are bound
by `manifest.json`. Every excluded original has a local locator, byte count,
SHA256, reason and explicit whole-file retention statement. Executables,
relocatable objects and tool binaries remain complete and local; no executable
or binary payload is published here. The verifier does not read omitted bytes,
import captured scripts, invoke compilers or re-run old tests.

```text
python tests/results/pcm-word-plane-20261103/verify.py --require-current
```

`--require-current` also checks all six repository source files against the
recorded raw bytes. The ordinary invocation verifies this historical package
without requiring today's sources to match. Neither mode qualifies native IRAM
allocation, the production family1 dispatch, full application memory fit,
throughput, watchdog behavior or physical hardware. Those remain separate gates.
