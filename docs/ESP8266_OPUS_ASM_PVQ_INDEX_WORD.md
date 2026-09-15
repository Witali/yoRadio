# Opus ASM: signed PVQ index through a word load

2026-09-15. Parent: accepted endpoint-word80.99456% raw CPU192.
Experimental v2;30 physical A/B/A completed. Raw CPU19280.08060%;80% and
live I2S/WebUI qualification still pending. Not a firmware default.

## Instruction and memory contract

Move the original return store from0x4024db36 to0x4024db22 (sp+108),
and defer the original signed index load to a fixed J at0x4024db36.
Seven intervening instructions neither read nor write a2/a0. Their memory
accesses are RAM, not the static flash index. Original return restoration
at0x4024e434 is unchanged; a0 is dead before the next private CALL0.

The fixed-continuation helper at0x4024dc95 uses a0 for SAR, aligned L32I for
the index, and SLLI16/SRAI16 for exact sign extension. It restores SAR and
jumps to0x4024db39 without CALL/RET. All29 bytes are live,10 instructions.
It reuses11 original encoder-only instructions; their sole external entry
is also encoder-only. Parent ELF bytes are independently authenticated.
No branch/bitrate restriction, new stack slot, RAM allocation or table.

Three patches,total35 bytes. All other ELF/app bytes and addresses remain
unchanged. The index has105 signed elements,210 bytes at0x402d5984.
A full last word needs two padding bytes: both images authenticate these
zero bytes and the complete212-byte region within flash.rodata. The host
model copies only the final two valid C-object bytes into a zeroed word.

## Local evidence

- [Census](ESP8266_OPUS_PVQ_INDEX_WORD_PROFILE.md):3026 reads/0.24s at192,
  12608.33/s; last index24 reads. Semantic host counts, not target timing.
- Symbolic extraction:all32 word bits,both halfword phases,arbitrary SAR.
- Actual linked prefix:131072 cases covering every16-bit value/both phases,
  plus6720 cases covering105 actual indices/all64 SAR values.
  All live GPRs, final stack contents and saved original return identical.
  137792 word loads checked. Instruction totals1240128->2618048 exclude
  original load-exception emulation and are NOT a performance measurement.
-24 host PCM/state/PLC/reset/OOM cases exact under ASan/UBSan, including
  320/510kbps, phase fixtures and compound120ms packets.
- SDK level1/task context a0/SAR save/restore contract inherited and hashed;
  no interrupts masked. This is not an interrupt-latency measurement.

Initial v1 failed assembly because this LX106 configuration rejects SEXT.
The failure log is retained; no v1 image was packaged or flashed. v2 uses
the exact two-shift sequence verified by the actual target assembler.
Original C fallback and saved GCC snapshots are unchanged.

Initial preflight had153 passes and one test-harness failure: the negative
padding test called an executable-section-only ELF locator for flash.rodata.
Corrected only that test to locate the allocated data section, then flip the
padding byte and require rejection. The full initial log is retained; no
firmware/proof/image changed because of this harness fix.

## Artifacts and remaining physical gate

Full packaging passed:903216-byte image,zero static RAM/IRAM/frame growth.
Candidate SHA256:
42f3b445aa7515c69cdcc1f563f9f177f7ed16b75bbabd4eb62358f0bbff5391.
Control SHA256:
07a3969d773ff59a9b7a610003248a8bd1820a6827412f54803a49d8239e0200.
Artifacts:firmware/development/esp8266-opus-pvq-index-word-{control,candidate}-v2.

Recipes:pvq_index_word.cjs,commented pvq_index_word.s,
pvq_index_word_proof.cjs. Host/source and negative regression tests retained.
Full154 related preflight regressions PASS,0 failures/skips,229.79seconds.
The complete log is retained beside the image; this is not the whole repository.
## Physical results

Completed10 A/10 B/10 A at160MHz/runtime QIO40 with packets in RAM,
no output/network audio input/stage or function profiler. All30 attempts
retained and exact PCM hashes checked; no observation or decoder errors.

| kbps | A control CPU% | B candidate CPU% | A2 control CPU% | Maximum call A/B/A2, us |
|---|---:|---:|---:|---:|
|12 mono|23.09056|23.08538|23.08613|7771 /7393 /7768|
|24 mono|54.11052|54.12444|54.11308|14224 /13929 /14995|
|64 stereo|62.87167|62.64767|62.84769|16515 /16816 /18108|
|128 stereo|72.59440|72.02094|72.60467|19272 /18818 /20403|
|192 stereo|80.97738|80.08060|80.99402|21047 /21318 /20826|

Relative192 time reduction1.1074/1.1278%;128 reduction0.78995/0.80398%.
Both exceed mono24 slowdown0.02572/0.02098%; both acceptance gates pass.
Accepted experimentally, not production.80.08060 is still greater than80:
another0.10065% relative time reduction is needed even for the raw gate.
The21.318ms maximum did not improve; raw mean is not a DMA deadline proof.

Sampled minDRAM A/B/A2:8528 /8168 /8176 B;192-only9976 /9800 /9800 B.
Post-run minimum26476 /26300 /26300 B; free stack minimum1660 B for all.
Static RAM/IRAM/frame unchanged by byte/section proof; sampled heap changes
are not interpreted as a changed decoder allocation. A2/run10 mono12 had
task_us553794 versus wall_us553010:784us accounting excess retained,
without subtracting the55us empty estimate or removing the observation.

Ordinary C radio restored through application-only OTA to0x10000.
Restoration evidence checks HTTP/WS, stopped station167 and playlist hash.
This is not a live20second qualification of the ASM candidate. Firmware
default and SPIFFS/settings unchanged. Current CPU threshold80%; legacy70%
report field is not the goal.

Reproduce report:node tools/esp8266_opus_asm/report_pvq_index_word.cjs.
Raw JSON/logs and comparison.json are retained with the candidate image.
Final156 related regressions PASS/0skip in244.84seconds, including independent
physical-report and ordinary-restoration checks. Full final-tests.log retained.
Restored root HTTP200,27249 gzip bytes in110.54ms; free heap27628 B,
minimum24748 B,RSSI-72dBm. Root transfer is not a full-browser latency test.
