# Allocation decoder-only hypothesis: conditional audit

2026-09-18. This is a read-only audit of the accepted eBands-final ASM,
not an implemented optimization or a speed claim.

`clt_compute_allocation` occupies2564 bytes, with the original192-byte task
stack frame. The radio's C decoder calls it with `encode=prev=signalBandwidth=0`.
In the actual linked caller, MOVI a8,0 at0x40244c6c dominates the CALL0 at
0x40244c85; all three incoming stack arguments40/44/48 are stored from a8.
No conditional/unconditional direct branch bypasses those initializations.

The callee reads encode at its SP+232 (caller SP+40) in three places:
0x40248832,0x40248908,0x40248982. It makes no direct writes to its incoming
stack arguments and does not form a pointer to its private frame. Its only
direct SP arithmetic is the192-byte prologue/epilogue.

Under the **assumption** that the incoming encode value stays zero, a
conservative CFG traversal finds three constant branches and67 unreachable
instructions occupying185 bytes. Every audio-data-dependent branch retains
both successors. With that assumption disabled, zero branches are folded
and zero instructions are dead. These counts are not a CPU estimate or an
application-size reduction; layout/branch relocation have not been changed.

The historical base linker's cross-reference lists only rate.c as definition
and celt_decoder.c as caller. That is supporting evidence, not a substitute
for an accepted-ELF-wide audit of indirect calls/address references.

## Before any deletion

- [x] Check the actual three stack arguments and direct-branch dominance.
- [x] Enumerate direct callee writes to incoming arguments and creation of
  private-frame pointers; preserve original ABI and stack size.
- [x] Count conditional dead code without restricting bitrates/modes or
  treating successful PCM fixtures as a universal reachability proof.
- [x] Negative tests reject a nonzero initializer, partial argument write,
  branch bypass, incoming-slot overwrite and unexpected stack alias.
- [ ] Prove all output-pointer ranges in the caller cannot alias
  callerSP+40..52, including earlier stack aliases and object bounds.
- [ ] Audit indirect callees and all symbol/address references in the
  accepted ELF, not just the original linker cross-reference.
- [ ] Only after that, generate a compact ASM candidate and independently
  compare the projected CFG, retained instructions, literal/call addresses
  and helper/storage boundaries. Keep C and the original ASM unchanged.
- [ ] Exact host PCM/state/PLC/OOM regression and >=10 physical A/B/A per
  variant. Check memory, stack, maxima and lower bitrates as usual.

No encoder branch was removed in this change. No new firmware was generated.
The checker deliberately reports `ready_for_specialization: false`.

Reproduce:

```text
node tools/esp8266_opus_asm/audit_allocation_decode.cjs
node --test tests/esp8266-opus-allocation-decode-audit.test.js
```

[Pinned linked instructions and conditional CFG result](results/esp8266-opus-allocation-decode-audit-20260918.json)
and [four passing tests](results/esp8266-opus-allocation-decode-audit-20260918.log).
