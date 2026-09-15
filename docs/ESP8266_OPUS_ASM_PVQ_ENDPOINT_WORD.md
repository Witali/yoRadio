# Opus ASM: original endpoint costs through word loads

2026-09-15. Parent: accepted row-word82.00615% raw CPU192.
Accepted experimental candidate after30 physical A/B/A runs:80.99456% raw
CPU192. The80% target and live I2S/WebUI qualification remain unproven.

## Minimal change and ABI

Upper at0x4024e21f reuses the existing a10 word leaf0x4024ddec. Change the
preceding ADD destination a9->a10; replace L8UI with CALL0. Original a9 is
overwritten by the next SUB without being read. a0/a11 are proven dead
across both outcomes; the original return remains at sp+108.

Lower at0x4024e22a uses a J to0x4024e403. The26-byte,9-instruction fragment
saves SAR in dead a0, extracts the byte into a11 and restores SAR before
jumping to the fixed continuation0x4024e22d. This is not a callable function
or RET ABI; the continuation is the same for every recursive invocation.
No original return, stack pointer or memory is written by the fragment.

Storage is the entire48-byte original encoder-only tail. All19 original
instructions and the incoming branch are independently proven unreachable
for immutable ctx.encode=0, preserving both successors of audio-dependent
branches. No bitrate assumption or runtime bitrate cap is introduced.
The preceding row helper returns before its own padding. New code uses26
bytes plus22 zero padding. Four patches,total56 bytes; all other bytes,
addresses, tables,112-byte frame, DRAM/IRAM and image size remain unchanged.

## Local verification

[Host census](ESP8266_OPUS_PVQ_ENDPOINT_WORD_PROFILE.md):at192,
1765 upper+1647 lower reads per0.24s,14216.67/s. Counts are semantic host
observations, not measured LX106 instruction timing.

- Symbolic lower extraction:all32 word bits,4 phases,arbitrary SAR; every
  register except result a11/dead a0 preserved, fixed continuation checked.
- Upper reuses the previously proved25-byte a10 leaf. Validate only those
  live bytes, not the adjacent a4 leaf stored in the same older57-byte slot.
-50176 direct endpoint cases (392 bytes*64 SAR values*2 paths).
-378304 actual linked complete searches (23 rows,each budget-64..16383).
  Exact q/cost at the unchanged remaining_bits loop; same caller branches
  and read order.804309 additional word loads checked, upper403392/lower400917.
  Instruction totals30454838->37693619 exclude old exception emulation and
  are NOT a timing result.
-24 exact host PCM/state/PLC/reset/OOM scenarios under ASan/UBSan, including
  320/510kbps, phase corpus and compound120ms packets.
- Actual SDK level1/task context saves/restores a0 and SAR:xtensa_vectors.S,
  xtensa_context.S,os_cpu_a.S and xtensa_rtos.h hashes recorded by the proof.
  The fragment does not mask interrupts; this is not a latency measurement.

The initial whole-function disassembly comparison stopped because the new
jump disconnected120 other encoder-only instructions from the generic CFG
walker. These bytes are still in the image, not deleted. Every omitted
instruction is matched to the unchanged original and independently proven
dead; missing live instructions or changed visible instructions fail. Whole
ELF/app equality outside declared patches remains mandatory. The shared
disassembler and all previous immutable recipes are unchanged.

A second local check treated the older a10+a4 storage as one leaf; restricted
the new proof's view to the actual first25 live bytes. Both failed logs are
retained. Neither failure was a target crash or PCM mismatch.

Recipes:pvq_endpoint_word.cjs,commented pvq_endpoint_word.s,
pvq_endpoint_word_proof.cjs. Original C and GCC snapshots unchanged.

## Physical gate

Full packaging/parent-chain verification passed. Candidate SHA256:
07a3969d773ff59a9b7a610003248a8bd1820a6827412f54803a49d8239e0200.
Control SHA256:
80c1faedc43b99bc78a90138f2bb11d1a9820b3def222c64064b4ec51e9731df.
Both images903216 B. Artifacts are in
firmware/development/esp8266-opus-pvq-endpoint-word-{control,candidate}-v1.

All145 related preflight regressions passed,0 failures/skips,180.14seconds.
The complete log is retained beside the candidate image. This is not the
whole repository suite and does not establish physical acceleration.

Completed10 A/10 B/10 A against row-word at160MHz/runtime QIO40. Identical
RAM-preloaded packets, no audio/network input or stage/function profiling.
Retain every attempt/error/maximum/minimum RAM and low-rate regression.
Accept only the high-bitrate criterion against both controls without RAM
growth; the current CPU target is80%, not the legacy70% report field.
Ordinary radio restored using OTA afterwards; no UART commands or reset.

## Physical results

All30 attempts completed with exact PCM. Median raw CPU, percent:

|kbps|A:row-word|B:endpoint-word|A2:row-word|Maximum call A/B/A2,us|
|---|---:|---:|---:|---|
|12|23.08423|23.09308|23.09133|7181 /7639 /7830|
|24|54.15513|54.10419|54.15635|15608 /14540 /14886|
|64|63.19948|62.86158|63.20721|17445 /16972 /17688|
|128|73.29400|72.59856|73.28813|20985 /18844 /20058|
|192|81.98187|80.99456|82.01310|22197 /20495 /21980|

Both high-bitrate gates PASS. Relative decode-time reduction at192 is
1.20431% /1.24193%, at1280.94883% /0.94089%. Mono12 is slower by
0.03836% /0.00758%, less than either high-bitrate gain. No bitrate cap.
New experimental control:80.9945625% CPU192. Its ten-run range is
80.94275..81.04154%,mean80.99285%. Another1.22794% relative time reduction
is needed to reach80%; do not mistake rounding to81% for passing the goal.

Static RAM/IRAM and112-byte frame unchanged. Free stack minimum1660 B in
every group. Observed free DRAM minima A/B/A2:8344 /8176 /8344 B;
at192:9800 /9792 /9800 B. Post-run free DRAM minimum26300 B in each group.
These are dynamic free-memory observations, not allocation sizes or a
claim that the ASM change saves RAM. No decoder or HTTP observation errors
occurred in these30 runs. A/run8 mono12 has task>wall excess267us; it is
retained without subtraction/clamping. All B/A2 windows are retained too.

Maximum B19220.495ms improved against both controls but still exceeds20ms;
raw median and this maximum do not establish uninterrupted I2S output.
The benchmark has no physical output and no network audio input.

Source/proofs commit8b0bdc7c; census0304c89f. [All30 attempts, manifests,
hashes and independently checked comparisons](../firmware/development/esp8266-opus-pvq-endpoint-word-candidate-v1/comparison.json)
are archived with the candidate image. Firmware default remains unchanged.

## Ordinary restoration

Restored ordinary live512-idle3s C-backend through OTA to0x10000,885552 B,
SHA256661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
CPU160/QIO40,I2S PDM32 GPIO3,2x512 DMA,benchmark OFF. HTTP/WebSocket/getindex/
playerwrap,stopped station167 and playlist hash match the fresh pre-test
snapshot. Empty error; heap27628/min24748 B,RSSI-61dBm.
Root returned HTTP200 in104.1972ms,27249gzip bytes,unchanged SHA256
7fdfd886707344338e824fe30430ee327482d627c153e322f7cc2fa321989a3f.
No SPIFFS/NVS update or UART/reset. Root transfer is not full-browser latency;
restoring a stopped ordinary image is not20seconds of live ASM playback.

Final147 related regressions PASS,0 failures/skips,206.19seconds. The new
results tests independently recompute all30 attempts, medians, maxima, free
memory, acceptance gates, image proofs and ordinary restoration. The complete
final-tests.log is archived beside the image; this is the related suite,
not every repository test. Current80% and live qualification remain pending.
