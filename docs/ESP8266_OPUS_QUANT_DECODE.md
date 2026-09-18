# Decoder-only quant_all_bands ASM — 2026-09-18

Rejected frozen-layout overlay over accepted eBands-final, not the
rejected allocation-decode candidate. The fresh physical A/B/A below
shows a regression; no production/default change. The active goal is
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

- [x] Fresh 10 A / 10 B / 10 A2 at CPU160/runtime QIO40, observation every15s.
- [x] All attempts, exact target PCM, maxima, low DRAM and polling failures.
- [x] Both relative high-bitrate versus low-bitrate gates, plus separate75% goal.
- [x] Restore ordinary heapreserve ASM radio; verify HTTP/WS/playlist.
- [ ] Only if accepted: full-radio relocation and >=20s I2S/WebUI qualification.

No UART commands, GPIO3 reset, partition/SPIFFS or PC Wi-Fi changes.

## Physical result: reject, keep eBands-final

All30 fresh attempts completed with exact target PCM hashes, sample/packet
counts and unchanged scratch peaks. The10 earlier A-only runs are retained
separately as `preliminary-control`: the user's memory audit interrupted that
experiment before any B run, and ordinary radio was restored. They are not
silently discarded or pooled into the fresh A/B/A medians.

| Input kb/s | A CPU % | B CPU % | A2 CPU % |
| --- | ---: | ---: | ---: |
| mono12 | 23.103625 | 23.076813 | 23.081917 |
| mono24 | 53.890812 | 54.091875 | 53.879458 |
| stereo64 | 61.193021 | 63.346438 | 61.188521 |
| stereo128 | 70.394375 | 74.089958 | 70.363958 |
| stereo192 | 77.860125 | 81.874792 | 77.869875 |

Both high-bitrate gates FAIL. Relative time at192 worsens by5.156255% versus
A and5.143089% versus A2; at128 by5.249828% and5.295325%. The75% goal is not
met. Shorter live code is not faster here. Packing changes internal branch/
instruction placement even though all external addresses remain fixed;
cache/alignment is a hypothesis, not a measured cause of the regression.

All maxima and unusual observations remain in the reports:

- Max192 wall-call:28685/21016/19972us for A/B/A2. A/run6 includes an HTTP
  observation timeout and90.111542% raw CPU192; not removed as an outlier.
- Minimum sampled DRAM1052/1928/4648B; lifetime free stack1660B in all groups.
  Different sampled free heaps do not establish a decoder memory saving.
- B/run1 mono12 task exceeds its differently delimited wall window by185us;
  A2/run2 by414us. No clamping or subtraction. Charged ISR/bookkeeping remain
  within the established raw task-time metric, not ideal instruction cycles.
- Static RAM, original384-B function frame and903216-B image stay unchanged.
  This is not live decoding, PDM timing or an audio-continuity qualification.

The paired image/ELF/retained-CFG proof is rechecked by
`tools/esp8266_opus_asm/report_quant_decode.cjs`. Three passing result tests verify
every one of40 saved run files and hashes (30 fresh plus10 preliminary),
recompute both gates/medians and require confirmed ordinary-radio restoration.
The combined local ASM/memory/reconnect/diagnostic-HTTP suite passes27/27.

Ordinary heapreserve accepted ASM radio was restored by OTA HTTP200/OK,
slot0x110000 ->0x10000, app SHA256
`dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
Status: stopped, no error, original Nightwave selection, RSSI-53dBm,
combined free heap30188B. HTTP/WS/getindex/playlist passed. No browser-rendering
or acoustic qualification is claimed. Source-only cancellation fix0edf328d
is not in this restored existing image; its separate live qualification remains.

Evidence is next to the candidate image: `comparison.json`, all40 raw JSON/log
pairs, OTA records, `before-restore.json`, `restored-webui.json` and test logs.
Do not use this candidate as the next optimization parent: keep accepted
`esp8266-opus-ebands-final-candidate-v2`.

### Separate next hypothesis

A read-only census found18 remaining loads of immutable context fields
SP+32 (encode=0) and SP+36 (resynth=1) in the decoder-reachable original ASM.
Consider in-place constant materialization over the accepted parent, keeping
instruction widths and all internal addresses unchanged. Removing a load
altogether additionally requires register-liveness proof on every successor.
The census is not an implementation or a speed result; do not reapply this
rejected packed function or assume fewer DRAM reads guarantee an improvement.
Save a separate contract/linked proof, exact PCM and fresh physical A/B/A.

```text
node tools/esp8266_opus_asm/audit_quant_decode.cjs
node tools/esp8266_opus_asm/quant_decode.cjs
node tools/esp8266_opus_asm/check_bands.cjs quant-decode
node --test tests/esp8266-opus-quant-decode.test.js
```
