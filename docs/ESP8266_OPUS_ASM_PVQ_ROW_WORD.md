# Opus ASM: PVQ row-length word load

2026-09-15. Accepted experimentally after30 physical A/B/A:82.00615% CPU192.
Default unchanged. Parent was a4-word82.83819%.80% and live audio still pending.

## Change and ABI

Replace L8UI a6,a2,0 at0x4024db47 with CALL0 to0x4024e3e8. The9-instruction
leaf saves SAR in a11, uses the low address bits for byte extraction, reads
one aligned word and restores SAR. Source a2 is preserved, a6 is unsigned
byte result. a0/a11 are dead at the caller continuation; the original
function return was already saved to sp+108.

Reuse27 bytes of original encoder-only instructions,25 live plus2 padding
after RET. The independently authenticated encode=0 CFG retains every
audio-dependent branch and proves this storage dead. Its only incoming
edge at0x4024dbd5 is also dead; no fallthrough or interior entry exists.
This is a decoder-only storage contract, not a bitrate restriction.
All outside bytes/addresses, tables,112-byte frame, DRAM/IRAM and image size
903216 B are unchanged. No new target table, allocation or task stack.

## Local evidence

- [Census](ESP8266_OPUS_PVQ_ROW_WORD_PROFILE.md):3026 reads/0.24s at192,
  12608.33 reads per second of audio; includes LM==-1.
- Symbolic verification covers all32 word bits,4 byte phases, arbitrary SAR,
  unchanged a2 and every register other than result a6/dead a11.
- Actual linked interpreter checks all392 table bytes times64 SAR values,
  plus160080 prefix cases:23 rows,580 budgets including signed extremes,
  LM=-1/0/3 and N=1/2/3/32. Both split and full search outcomes are retained.
  Total185168 new word reads; instruction counts exclude old exception
  handling and must not be interpreted as CPU time.
- Original mode/index pointers,392-byte bits storage and210-byte signed
  row-index table verified in the ELF, including complete word bounds.
- Parent proofs independently recheck the existing a4/a10 helpers and
  exhaustive search. Private CALL0 liveness uses only actual a0/a11 clobbers,
  not the larger generic C caller-scratch set.
-24 host PCM/state/PLC/reset/OOM cases exact under ASan/UBSan, including
  320/510kbps, all phase fixtures and120ms compound packets.

Recipes: pvq_row_word.cjs, commented pvq_row_word.s, pvq_row_word_proof.cjs.
Candidate SHA256:80c1faedc43b99bc78a90138f2bb11d1a9820b3def222c64064b4ec51e9731df.
Control SHA256:fe34751b8dae0cbd87a58a1b767aa02a82b006aa8b452f66065446dbc9dbdae9.
Artifacts are under firmware/development/esp8266-opus-pvq-row-word-{control,candidate}-v1.

## Required physical qualification

Full136 related preflight regressions PASS,0 failures/skips,162.29seconds.
preflight-tests.log is retained beside the candidate image.

Completed10 A/10 B/10 A at160MHz/QIO40, identical RAM-preloaded fixtures,
no network input/output/function or stage profiling. Retain every attempt,
error, maximum and minimum RAM, including low-rate regressions. Compare both
controls using the high-bitrate gate; then restore ordinary radio via OTA.
No UART/GPIO3 commands or reset. A host pass is not an LX106 speed result.

## Physical results

All30 attempts completed, exact PCM. Median raw CPU, percent:

|kbps|A:a4-word|B:row-word|A2:a4-word|Maximum call A/B/A2,us|
|---|---:|---:|---:|---|
|12|23.08594|23.08904|23.10325|6888 /8001 /7964|
|24|54.18119|54.16227|54.20265|15934 /14653 /21689|
|64|63.43300|63.24248|63.45488|18257 /17746 /43023|
|128|73.78213|73.28558|73.80594|19574 /19510 /27755|
|192|82.82325|82.00615|82.84056|21154 /21528 /29603|

Both high-bitrate gates PASS:192 relative time gain0.98656% /1.00726%,
128 gain0.67298% /0.70503%. Mono12 loss against A is0.013446%; against A2
no lower-rate median is worse. Accepted as the new experimental raw control,
not a production/default switch. To reach80%, another2.44634% relative
decode-time reduction is needed. B192 range81.96696..82.14008%,mean82.02641%.

Static RAM/IRAM/frame unchanged. Free stack minimum1660 B in all groups.
Observed free DRAM minima8036 /6976 /800 B; at192:9836 /9800 /1116 B.
Post-run raw free DRAM minima26336 /26192 /17684 B. These are dynamic
observations, not allocation sizes or proof that the optimization saves RAM.

All errors/outliers remain in comparison.json. A2/run5 and A2/run6 each
had one HTTP observation timeout; both completed with exact PCM. A/B have
none. A2/run5 minDRAM800 B, allocator lifetime minimum776 B, CPU19295.38921%;
status RSSI before/after -59/-90dBm. A2/run6 RSSI -89/-57dBm, minDRAM4560 B,
max64 call43.023ms. This correlation does not prove network/fragmentation
causation. After each attempt the status showed26488 B free.

Timing-window task>wall excess is retained without subtraction/clamping:
A/run10 mono12:2625us; B/run2:2420us,B/run9:392us; A2/run1:994us.
Maximum B19221.528ms is worse than A21.154ms and exceeds20ms; improved
median CPU is not an I2S DMA deadline guarantee.

Source/proofs commit e18626d8; host-census8a59c30a.
[All30 attempts, manifests, hashes and independent comparisons](../firmware/development/esp8266-opus-pvq-row-word-candidate-v1/comparison.json)
are archived with the candidate image.

## Ordinary restoration

Ordinary live512-idle3s C-backend restored through OTA to0x10000, app885552 B,
SHA256661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
CPU160/QIO40,I2S PDM32 GPIO3,2x512 DMA; benchmark OFF. Station167 unchanged,
stopped, empty error; HTTP/WebSocket/getindex/playerwrap and playlist SHA
checked. Root HTTP200,27249 gzip bytes,104.8326ms; free heap27628/min24748,
RSSI-58dBm. Root transfer is not a full browser load measurement; restoring
a stopped ordinary image is not a20second live test of the new ASM candidate.
No UART/reset or SPIFFS update.

Current80% goal and>=20seconds uninterrupted I2S PDM with WebUI remain unproven.

Final138 related regressions PASS,0 failures/skips,182.53seconds. The results
test independently recomputes all30 attempts/medians/maxima/minima/gates,
revalidates linked proofs and ordinary restoration. final-tests.log is
archived with the image; this is the related suite, not every repository test.
