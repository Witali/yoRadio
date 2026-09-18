# Decoder-only quant_all_bands ASM — 2026-09-18

Experimental frozen-layout overlay over accepted eBands-final, not the
rejected allocation-decode candidate. No production/default change and
no speed claim before the fresh physical A/B/A gate. The active goal is
<=75% raw CPU at 192 kb/s, then >=20 seconds continuous I2S plus WebUI.

## Change and invariants

Use the actual linked GCC-derived `quant_all_bands` at 0x402507d8. Keep
the original 384-byte call0 frame, register assignments, all retained
arithmetic/memory operations, and addresses outside its 9416-byte slot.
Remove decoder-unreachable branches/code; do not enable the broad C
decode-only compiler option which regressed speed/stack in an older test.

- Native `celt_decode_with_ec_dred` has one call at 0x40244dbb; its argument
  setup establishes a2=0 without a bypass or intervening call.
- `ctx.encode` and `ctx.resynth` are set once and not modified through
  helpers. The 15-field, 32-bit ABI context occupies private SP+32..91.
  The sole escaping private-frame address is &ctx at SP+32. Private scalar
  slots SP+92..363 remain disjoint from valid array/entropy/scratch objects.
- Constant propagation kills outgoing/incoming and mutable-context memory
  facts at calls/indirect stores. It preserves only proven constants in
  unaliased private slots and immutable encode=0/resynth=1 fields. Removing
  these assumptions makes the analysis conservative, not more aggressive.
- The encoder RDO context/1275-byte array copies are already excluded by
  the bounded build. They are not counted as new memory savings here.
- All 11 indirect calls in the original function resolve to the pinned
  signed/unsigned ROM division routines, not arbitrary callbacks.
- Two apparent CALL0s in the global disassembly are bytes of HTTP literal
  pools. Classification checks exact map names, identical base/current ELF
  bytes and no covering STT_FUNC. Two raw pointer-pattern hits span real
  instructions in lmac_set_status/silk_PLC, verified by reachable disassembly.
  Other unclassified entry/address references make the checker fail.

This is the valid native decoder-object contract. Arbitrary encoder calls,
invalid pointers or corrupted RAM are not admitted as a new API. The C
fallback and saved original GCC ASM are untouched; no bitrate/mode ceiling.

## Preflight evidence

- 557 unreachable instructions (1551 original instruction bytes).
- Of 32 constant branch decisions, 27 instructions disappear and 5 become
  unconditional jumps. One decision is constant even without encode=0.
- 2786 retained instructions have a one-to-one linked operand/reference/CFG
  comparison. Live body 7687 bytes; 1729 bytes of unreachable padding keep
  other addresses unchanged. Application size remains 903216 bytes: this
  is not a 1729-byte application saving. Static RAM and frame delta are zero.
- Host C semantic mirror: 24 exact PCM/state cases under ASan/UBSan,
  including 12..510 kb/s, SILK/hybrid/CELT, mixed/reset/PLC/OOM, 2.5..20-ms
  frames, VBR/packed frames and 120-ms compound packets. It does not execute
  LX106 instructions or measure target speed.
- Negative regressions cover stack escapes/pivots, partial context writes,
  caller initializer/argument changes, and retained arithmetic, stack,
  literal, call and branch mutations.
- All 6 final preflight tests pass; combined memory/lifecycle/reconnect
  and specialization suite passes 25/25, zero skipped. These checks do not
  replace the physical timing or full-radio continuity gates.

Artifact pair: `firmware/development/esp8266-opus-quant-decode-`
`{control,candidate}-v2`. Candidate SHA256:
`714e7ca0b882a4289c50c0d511c911cf6eeca349bdea0a06ceb627e996000905`.
The never-flashed v1 prototype had a copied purpose label and an incomplete
branch-removal counter; v2 fixes metadata, with identical application bytes.
An initial negative test mutated an earlier textual register occurrence;
it now pins the actual call-argument address. The failed test log is retained.

## Required physical gate

- [ ] Fresh 10 A / 10 B / 10 A2 at CPU160/runtime QIO40, observation every15s.
- [ ] All attempts, exact target PCM, maxima, low DRAM and polling failures.
- [ ] Both relative high-bitrate versus low-bitrate gates, plus separate75% goal.
- [ ] Restore ordinary heapreserve ASM radio; verify HTTP/WS/playlist.
- [ ] Only if accepted: full-radio relocation and >=20s I2S/WebUI qualification.

No UART commands, GPIO3 reset, partition/SPIFFS or PC Wi-Fi changes.

```text
node tools/esp8266_opus_asm/audit_quant_decode.cjs
node tools/esp8266_opus_asm/quant_decode.cjs
node tools/esp8266_opus_asm/check_bands.cjs quant-decode
node --test tests/esp8266-opus-quant-decode.test.js
```
