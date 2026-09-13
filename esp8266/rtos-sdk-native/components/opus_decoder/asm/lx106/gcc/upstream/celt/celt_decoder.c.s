# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/celt_decoder.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"celt_decoder.c"
# GNU C99 (crosstool-NG esp-2020r3-49-gd5524c1) version 8.4.0 (xtensa-lx106-elf)
#	compiled by GNU C version 6.3.0 20170516, GMP version 6.1.2, MPFR version 4.0.1, MPC version 1.1.0, isl version isl-0.19-GMP

# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed:
# -I C:/Work/yoRadio/.build/esp8266-opus-baseline6144-raw192/config
# -I @OPUS@/.
# -I @OPUS@/upstream/include
# -I @OPUS@/upstream/celt
# -I @OPUS@/upstream/silk
# -I @OPUS@/upstream/silk/fixed
# -I @OPUS@/upstream/src
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/newlib/platform_include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include/freertos
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/include/freertos/private
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/freertos/port/esp8266/include/freertos
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/heap/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/heap/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/log/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/include/apps
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/include/apps/sntp
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/lwip/src/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/port/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/lwip/port/esp8266/include/arch
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/include/driver
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp_common/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp_event/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/tcpip_adapter/include
# -I C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/vfs/include
# -iprefix c:\work\yoradio\.build\esp8266-tools\tools\xtensa-lx106-elf\esp-2020r3-49-gd5524c1-8.4.0\xtensa-lx106-elf\bin\../lib/gcc/xtensa-lx106-elf/8.4.0/
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\celt_decoder.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\celt_decoder.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\celt_decoder.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\celt_decoder.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\celt_decoder.c.s.raw
# -g0 -Os -O3 -Wno-frame-address -Wall -Werror=all
# -Wno-error=unused-function -Wno-error=unused-but-set-variable
# -Wno-error=unused-variable -Wno-error=deprecated-declarations -Wextra
# -Wno-unused-parameter -Wno-sign-compare -Wno-old-style-declaration
# -std=gnu99 -ffunction-sections -fdata-sections
# -fstrict-volatile-bitfields -fwrapv -fverbose-asm
# options enabled:  -faggressive-loop-optimizations -falign-functions
# -falign-jumps -falign-labels -falign-loops -fauto-inc-dec
# -fbranch-count-reg -fcaller-saves -fchkp-check-incomplete-type
# -fchkp-check-read -fchkp-check-write -fchkp-instrument-calls
# -fchkp-narrow-bounds -fchkp-optimize -fchkp-store-bounds
# -fchkp-use-static-bounds -fchkp-use-static-const-bounds
# -fchkp-use-wrappers -fcode-hoisting -fcombine-stack-adjustments -fcommon
# -fcompare-elim -fcprop-registers -fcrossjumping -fcse-follow-jumps
# -fdata-sections -fdefer-pop -fdelete-null-pointer-checks -fdevirtualize
# -fdevirtualize-speculatively -fearly-inlining
# -feliminate-unused-debug-types -fexpensive-optimizations
# -fforward-propagate -ffp-int-builtin-inexact -ffunction-cse
# -ffunction-sections -fgcse -fgcse-after-reload -fgcse-lm -fgnu-runtime
# -fgnu-unique -fguess-branch-probability -fhoist-adjacent-loads -fident
# -fif-conversion -fif-conversion2 -findirect-inlining -finline
# -finline-atomics -finline-functions -finline-functions-called-once
# -finline-small-functions -fipa-bit-cp -fipa-cp -fipa-cp-clone -fipa-icf
# -fipa-icf-functions -fipa-icf-variables -fipa-profile -fipa-pure-const
# -fipa-ra -fipa-reference -fipa-sra -fipa-vrp -fira-hoist-pressure
# -fira-share-save-slots -fira-share-spill-slots
# -fisolate-erroneous-paths-dereference -fivopts -fkeep-static-consts
# -fleading-underscore -flifetime-dse -floop-interchange
# -floop-unroll-and-jam -flra-remat -flto-odr-type-merging -fmath-errno
# -fmerge-constants -fmerge-debug-strings -fmove-loop-invariants
# -fomit-frame-pointer -foptimize-sibling-calls -foptimize-strlen
# -fpartial-inlining -fpeel-loops -fpeephole -fpeephole2 -fplt
# -fpredictive-commoning -fprefetch-loop-arrays -freg-struct-return
# -freorder-functions -frerun-cse-after-loop
# -fsched-critical-path-heuristic -fsched-dep-count-heuristic
# -fsched-group-heuristic -fsched-interblock -fsched-last-insn-heuristic
# -fsched-rank-heuristic -fsched-spec -fsched-spec-insn-heuristic
# -fsched-stalled-insns-dep -fschedule-fusion -fschedule-insns
# -fschedule-insns2 -fsemantic-interposition -fshow-column -fshrink-wrap
# -fshrink-wrap-separate -fsigned-zeros -fsplit-ivs-in-unroller
# -fsplit-loops -fsplit-paths -fsplit-wide-types -fssa-backprop
# -fssa-phiopt -fstdarg-opt -fstore-merging -fstrict-aliasing
# -fstrict-volatile-bitfields -fsync-libcalls -fthread-jumps
# -ftoplevel-reorder -ftrapping-math -ftree-bit-ccp -ftree-builtin-call-dce
# -ftree-ccp -ftree-ch -ftree-coalesce-vars -ftree-copy-prop -ftree-cselim
# -ftree-dce -ftree-dominator-opts -ftree-dse -ftree-forwprop -ftree-fre
# -ftree-loop-distribute-patterns -ftree-loop-distribution
# -ftree-loop-if-convert -ftree-loop-im -ftree-loop-ivcanon
# -ftree-loop-optimize -ftree-loop-vectorize -ftree-parallelize-loops=
# -ftree-partial-pre -ftree-phiprop -ftree-pre -ftree-pta -ftree-reassoc
# -ftree-scev-cprop -ftree-sink -ftree-slp-vectorize -ftree-slsr -ftree-sra
# -ftree-switch-conversion -ftree-tail-merge -ftree-ter -ftree-vrp
# -funit-at-a-time -funswitch-loops -fverbose-asm -fwrapv
# -fzero-initialized-in-bss -mserialize-volatile

	.text
	.global	__divsi3
	.section	.text.deemphasis,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.align	4
	.type	deemphasis, @function
# Function: deemphasis
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #ifndef RESYNTH
# C context: static
# C context: #endif
# C context: void deemphasis(celt_sig *in[], opus_val16 *pcm, int N, int C, int downsample, const opus_val16 *coef,
# C context: celt_sig *mem, int accum)
# C context: {
# C context: int c;
# C context: int Nd;
deemphasis:
	addi	sp, sp, -96	#,,
	s32i	a12, sp, 88	#,
	s32i	a13, sp, 84	#,
	s32i	a14, sp, 80	#,
	s32i.n	a5, sp, 36	# %sfp, C
	s32i	a0, sp, 92	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\celt\celt_decoder.c:297: {
	mov.n	a12, a2	# in, in
	s32i.n	a3, sp, 40	# %sfp, pcm
	s32i.n	a4, sp, 32	# %sfp, N
	s32i.n	a6, sp, 28	# %sfp, downsample
	mov.n	a14, a7	# coef, coef
	l32i	a13, sp, 96	# mem, mem
# @OPUS@\upstream\celt\celt_decoder.c:303:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:306:    if (downsample == 1 && C == 2 && !accum)
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:303:    SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:306:    if (downsample == 1 && C == 2 && !accum)
	bnei	a5, 1, .L2	#,,
	l32i.n	a9, sp, 36	# %sfp,
	bnei	a9, 2, .L2	#,,
# @OPUS@\upstream\celt\celt_decoder.c:306:    if (downsample == 1 && C == 2 && !accum)
	l32i	a5, sp, 100	# accum,
# @OPUS@\upstream\celt\celt_decoder.c:318:    ALLOC(scratch, downsample > 1 ? N : ALLOC_NONE, celt_sig);
	movi.n	a2, 0	# iftmp$106_100,
# @OPUS@\upstream\celt\celt_decoder.c:306:    if (downsample == 1 && C == 2 && !accum)
	bne	a5, a2, .L3	#,,
# @OPUS@\upstream\celt\celt_decoder.c:276:    for (j=0;j<N;j++)
	l32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:308:       deemphasis_stereo_simple(in, pcm, N, coef[0], mem);
	l16si	a7, a14, 0	# *coef_116(D), _5
# @OPUS@\upstream\celt\celt_decoder.c:272:    x0=in[0];
	l32i.n	a11, a12, 0	# *in_117(D), x0
# @OPUS@\upstream\celt\celt_decoder.c:273:    x1=in[1];
	l32i.n	a10, a12, 4	# MEM[(celt_sig * *)in_117(D) + 4B], x1
# @OPUS@\upstream\celt\celt_decoder.c:274:    m0 = mem[0];
	l32i.n	a5, a13, 0	# *mem_120(D), m0
# @OPUS@\upstream\celt\celt_decoder.c:275:    m1 = mem[1];
	l32i.n	a8, a13, 4	# MEM[(celt_sig *)mem_120(D) + 4B], m1
# @OPUS@\upstream\celt\celt_decoder.c:276:    for (j=0;j<N;j++)
	blti	a9, 1, .L4	#,,
	l32i.n	a6, sp, 40	# %sfp, ivtmp$130
	slli	a15, a9, 2	# tmp231,,
	l32r	a14, .LC1	#, tmp364
	l32r	a12, .LC0	#, tmp363
	add.n	a15, a6, a15	# _37, ivtmp$130, tmp231
.L9:
# @OPUS@\upstream\celt\celt_decoder.c:280:       tmp0 = x0[j] + VERY_SMALL + m0;
	l32i.n	a4, a11, 0	# MEM[base: _29, offset: 0B], MEM[base: _29, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:281:       tmp1 = x1[j] + VERY_SMALL + m1;
	l32i.n	a2, a10, 0	# MEM[base: _137, offset: 0B], MEM[base: _137, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:280:       tmp0 = x0[j] + VERY_SMALL + m0;
	add.n	a4, a5, a4	# tmp0, m0, MEM[base: _29, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:281:       tmp1 = x1[j] + VERY_SMALL + m1;
	add.n	a2, a8, a2	# tmp1, m1, MEM[base: _137, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:282:       m0 = MULT16_32_Q15(coef0, tmp0);
	srai	a9, a4, 16	# tmp234, tmp0,
	extui	a5, a4, 0, 16	# tmp237, tmp0,
# @OPUS@\upstream\celt\celt_decoder.c:283:       m1 = MULT16_32_Q15(coef0, tmp1);
	srai	a8, a2, 16	# tmp240, tmp1,
	extui	a3, a2, 0, 16	# tmp243, tmp1,
# @OPUS@\upstream\celt\celt_decoder.c:282:       m0 = MULT16_32_Q15(coef0, tmp0);
	mull	a9, a9, a7	# tmp235, tmp234, _5
	mull	a5, a5, a7	# tmp238, tmp237, _5
# @OPUS@\upstream\celt\celt_decoder.c:283:       m1 = MULT16_32_Q15(coef0, tmp1);
	mull	a8, a8, a7	# tmp241, tmp240, _5
	mull	a3, a3, a7	# tmp244, tmp243, _5
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	addmi	a4, a4, 0x800	# tmp246, tmp0,
	addmi	a2, a2, 0x800	# tmp258, tmp1,
# @OPUS@\upstream\celt\celt_decoder.c:282:       m0 = MULT16_32_Q15(coef0, tmp0);
	slli	a9, a9, 1	# tmp236, tmp235,
	srai	a5, a5, 15	# tmp239, tmp238,
# @OPUS@\upstream\celt\celt_decoder.c:283:       m1 = MULT16_32_Q15(coef0, tmp1);
	slli	a8, a8, 1	# tmp242, tmp241,
	srai	a3, a3, 15	# tmp245, tmp244,
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	srai	a4, a4, 12	# x, tmp246,
	srai	a2, a2, 12	# x, tmp258,
# @OPUS@\upstream\celt\celt_decoder.c:282:       m0 = MULT16_32_Q15(coef0, tmp0);
	add.n	a5, a9, a5	# m0, tmp236, tmp239
# @OPUS@\upstream\celt\celt_decoder.c:283:       m1 = MULT16_32_Q15(coef0, tmp1);
	add.n	a8, a8, a3	# m1, tmp242, tmp245
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a4, a14, .L5	# x, tmp364,
	mov.n	a4, a14	# x, tmp364
.L5:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	bge	a12, a4, .L6	# tmp363, x,
	mov.n	a4, a12	# x, tmp363
.L6:
# @OPUS@\upstream\celt\fixed_generic.h:184:    return EXTRACT16(x);
	s16i	a4, a6, 0	# MEM[base: _31, offset: 0B], x
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a2, a14, .L7	# x, tmp364,
	mov.n	a2, a14	# x, tmp364
.L7:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	bge	a12, a2, .L8	# tmp363, x,
	mov.n	a2, a12	# x, tmp363
.L8:
# @OPUS@\upstream\celt\fixed_generic.h:184:    return EXTRACT16(x);
	s16i	a2, a6, 2	# MEM[base: _31, offset: 2B], x
	addi.n	a6, a6, 4	# ivtmp$130, ivtmp$130,
	addi.n	a11, a11, 4	# ivtmp$128, ivtmp$128,
	addi.n	a10, a10, 4	# ivtmp$129, ivtmp$129,
# @OPUS@\upstream\celt\celt_decoder.c:276:    for (j=0;j<N;j++)
	bne	a6, a15, .L9	# ivtmp$130, _37,
.L4:
# @OPUS@\upstream\celt\celt_decoder.c:287:    mem[0] = m0;
	s32i.n	a5, a13, 0	# *mem_120(D), m0
# @OPUS@\upstream\celt\celt_decoder.c:288:    mem[1] = m1;
	s32i.n	a8, a13, 4	# MEM[(celt_sig *)mem_120(D) + 4B], m1
	j	.L1		#
.L2:
# @OPUS@\upstream\celt\celt_decoder.c:318:    ALLOC(scratch, downsample > 1 ? N : ALLOC_NONE, celt_sig);
	l32i.n	a5, sp, 28	# %sfp,
	blti	a5, 2, .L41	#,,
# @OPUS@\upstream\celt\celt_decoder.c:318:    ALLOC(scratch, downsample > 1 ? N : ALLOC_NONE, celt_sig);
	l32i.n	a2, sp, 32	# %sfp, iftmp$106_100
	j	.L3		#
.L41:
# @OPUS@\upstream\celt\celt_decoder.c:318:    ALLOC(scratch, downsample > 1 ? N : ALLOC_NONE, celt_sig);
	movi.n	a2, 0	# iftmp$106_100,
.L3:
# @OPUS@\upstream\celt\celt_decoder.c:318:    ALLOC(scratch, downsample > 1 ? N : ALLOC_NONE, celt_sig);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:323:    Nd = N/downsample;
	l32i.n	a3, sp, 28	# %sfp,
	l32i.n	a2, sp, 32	# %sfp,
	call0	__divsi3		#
# @OPUS@\upstream\celt\celt_decoder.c:300:    int apply_downsampling=0;
	movi.n	a9, 0	#,
	s32i.n	a9, sp, 24	# %sfp,
	l32i.n	a3, sp, 28	# %sfp,
	l32i.n	a9, sp, 32	# %sfp,
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:324:    c=0; do {
	l32i.n	a4, sp, 24	# %sfp,
	s32i.n	a12, sp, 20	# %sfp, in
	slli	a9, a9, 2	#,,
	slli	a3, a3, 2	#,,
# @OPUS@\upstream\celt\celt_decoder.c:322:    coef0 = coef[0];
	l16si	a6, a14, 0	# *coef_116(D), coef0
	l32r	a12, .LC0	#, tmp444
	slli	a11, a5, 1	# _439,,
	s32i.n	a9, sp, 44	# %sfp,
	s32i.n	a3, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:324:    c=0; do {
	s32i.n	a4, sp, 16	# %sfp,
.L36:
# @OPUS@\upstream\celt\celt_decoder.c:329:       x =in[c];
	l32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:347:       if (downsample>1)
	l32i.n	a9, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:328:       celt_sig m = mem[c];
	l32i.n	a3, a13, 0	# MEM[base: _417, offset: 0B], m
# @OPUS@\upstream\celt\celt_decoder.c:329:       x =in[c];
	l32i.n	a4, a5, 0	# MEM[base: _416, offset: 0B], x
# @OPUS@\upstream\celt\celt_decoder.c:347:       if (downsample>1)
	blti	a9, 2, .L11	#,,
# @OPUS@\upstream\celt\celt_decoder.c:350:          for (j=0;j<N;j++)
	l32i.n	a9, sp, 32	# %sfp,
	blti	a9, 1, .L12	#,,
	l32i.n	a5, sp, 44	# %sfp,
	l32i.n	a8, sp, 48	# %sfp, ivtmp$145
	add.n	a9, a4, a5	# _75, ivtmp$144,
.L13:
# @OPUS@\upstream\celt\celt_decoder.c:352:             celt_sig tmp = x[j] + VERY_SMALL + m;
	l32i.n	a5, a4, 0	# MEM[base: _70, offset: 0B], MEM[base: _70, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$144, ivtmp$144,
	add.n	a5, a3, a5	# tmp, m, MEM[base: _70, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:353:             m = MULT16_32_Q15(coef0, tmp);
	srai	a7, a5, 16	# tmp276, tmp,
	extui	a3, a5, 0, 16	# tmp279, tmp,
	mull	a7, a7, a6	# tmp277, tmp276, coef0
	mull	a3, a3, a6	# tmp280, tmp279, coef0
	slli	a7, a7, 1	# tmp278, tmp277,
	srai	a3, a3, 15	# tmp281, tmp280,
# @OPUS@\upstream\celt\celt_decoder.c:354:             scratch[j] = tmp;
	s32i.n	a5, a8, 0	# MEM[base: _71, offset: 0B], tmp
# @OPUS@\upstream\celt\celt_decoder.c:353:             m = MULT16_32_Q15(coef0, tmp);
	add.n	a3, a7, a3	# m, tmp278, tmp281
	addi.n	a8, a8, 4	# ivtmp$145, ivtmp$145,
# @OPUS@\upstream\celt\celt_decoder.c:350:          for (j=0;j<N;j++)
	bne	a9, a4, .L13	# _75, ivtmp$144,
	j	.L12		#
.L11:
# @OPUS@\upstream\celt\celt_decoder.c:360:          if (accum)
	l32i	a9, sp, 100	# accum,
	bnez.n	a9, .L14	#,
# @OPUS@\upstream\celt\celt_decoder.c:371:             for (j=0;j<N;j++)
	l32i.n	a9, sp, 32	# %sfp,
	bgei	a9, 1, .L15	#,,
	j	.L16		#
.L14:
# @OPUS@\upstream\celt\celt_decoder.c:362:             for (j=0;j<N;j++)
	l32i.n	a9, sp, 32	# %sfp,
	blti	a9, 1, .L17	#,,
	l32i.n	a5, sp, 16	# %sfp,
	l32r	a8, .LC1	#, tmp364
	slli	a10, a5, 1	# tmp282,,
	l32i.n	a5, sp, 40	# %sfp,
	l32r	a9, .LC0	#, tmp363
	add.n	a10, a5, a10	# ivtmp$150,, tmp282
	l32i.n	a5, sp, 44	# %sfp,
	mov.n	a7, a3	# m, m
	add.n	a14, a4, a5	# _166, ivtmp$149,
.L21:
# @OPUS@\upstream\celt\celt_decoder.c:364:                celt_sig tmp = x[j] + m + VERY_SMALL;
	l32i.n	a3, a4, 0	# MEM[base: _567, offset: 0B], MEM[base: _567, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:366:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(tmp))));
	l16si	a15, a10, 0	# MEM[base: _566, offset: 0B], _471
# @OPUS@\upstream\celt\celt_decoder.c:364:                celt_sig tmp = x[j] + m + VERY_SMALL;
	add.n	a3, a7, a3	# tmp, m, MEM[base: _567, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:365:                m = MULT16_32_Q15(coef0, tmp);
	extui	a7, a3, 0, 16	# tmp284, tmp,
	srai	a5, a3, 16	# tmp287, tmp,
	mull	a7, a7, a6	# tmp285, tmp284, coef0
	mull	a5, a5, a6	# tmp288, tmp287, coef0
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	addmi	a3, a3, 0x800	# tmp292, tmp,
# @OPUS@\upstream\celt\celt_decoder.c:365:                m = MULT16_32_Q15(coef0, tmp);
	srai	a7, a7, 15	# tmp286, tmp285,
	slli	a5, a5, 1	# tmp289, tmp288,
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	srai	a3, a3, 12	# x, tmp292,
# @OPUS@\upstream\celt\celt_decoder.c:365:                m = MULT16_32_Q15(coef0, tmp);
	add.n	a7, a7, a5	# m, tmp286, tmp289
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a3, a8, .L18	# x, tmp364,
	mov.n	a3, a8	# x, tmp364
.L18:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	mov.n	a5, a3	# x, x
	bge	a9, a3, .L19	# tmp363, x,
	mov.n	a5, a9	# x, tmp363
.L19:
# @OPUS@\upstream\celt\celt_decoder.c:366:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(tmp))));
	add.n	a5, a15, a5	# tmp362, _471, x
# @OPUS@\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	slli	a15, a5, 16	# tmp307, tmp362,
	mov.n	a3, a9	# iftmp$117_453, tmp363
	blt	a9, a5, .L20	# tmp363, tmp362,
	blt	a5, a8, .L43	# tmp362, tmp364,
	srai	a3, a15, 16	# iftmp$117_453, tmp307,
	j	.L20		#
.L43:
	mov.n	a3, a8	# iftmp$117_453, tmp364
.L20:
# @OPUS@\upstream\celt\celt_decoder.c:366:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(tmp))));
	s16i	a3, a10, 0	# MEM[base: _566, offset: 0B], iftmp$117_453
	addi.n	a4, a4, 4	# ivtmp$149, ivtmp$149,
	add.n	a10, a10, a11	# ivtmp$150, ivtmp$150, _439
# @OPUS@\upstream\celt\celt_decoder.c:362:             for (j=0;j<N;j++)
	bne	a14, a4, .L21	# _166, ivtmp$149,
	mov.n	a3, a7	# m, m
	j	.L17		#
.L15:
	l32i.n	a9, sp, 16	# %sfp,
	l32i.n	a5, sp, 40	# %sfp,
	slli	a10, a9, 1	# tmp308,,
	add.n	a10, a5, a10	# ivtmp$154,, tmp308
	l32i.n	a5, sp, 44	# %sfp,
	l32r	a8, .LC1	#, tmp364
	l32r	a9, .LC0	#, tmp363
	add.n	a14, a4, a5	# _443, ivtmp$153,
.L24:
# @OPUS@\upstream\celt\celt_decoder.c:373:                celt_sig tmp = x[j] + VERY_SMALL + m;
	l32i.n	a5, a4, 0	# MEM[base: _441, offset: 0B], MEM[base: _441, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$153, ivtmp$153,
	add.n	a3, a3, a5	# tmp, m, MEM[base: _441, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:374:                m = MULT16_32_Q15(coef0, tmp);
	srai	a15, a3, 16	# tmp310, tmp,
	extui	a7, a3, 0, 16	# tmp313, tmp,
	mull	a15, a15, a6	# tmp311, tmp310, coef0
	mull	a7, a7, a6	# tmp314, tmp313, coef0
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	addmi	a5, a3, 0x800	# tmp316, tmp,
# @OPUS@\upstream\celt\celt_decoder.c:374:                m = MULT16_32_Q15(coef0, tmp);
	slli	a15, a15, 1	# tmp312, tmp311,
	srai	a3, a7, 15	# tmp315, tmp314,
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	srai	a5, a5, 12	# x, tmp316,
# @OPUS@\upstream\celt\celt_decoder.c:374:                m = MULT16_32_Q15(coef0, tmp);
	add.n	a3, a15, a3	# m, tmp312, tmp315
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a5, a8, .L22	# x, tmp364,
	mov.n	a5, a8	# x, tmp364
.L22:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	bge	a9, a5, .L23	# tmp363, x,
	mov.n	a5, a9	# x, tmp363
.L23:
# @OPUS@\upstream\celt\fixed_generic.h:184:    return EXTRACT16(x);
	s16i	a5, a10, 0	# MEM[base: _442, offset: 0B], x
	add.n	a10, a10, a11	# ivtmp$154, ivtmp$154, _439
# @OPUS@\upstream\celt\celt_decoder.c:371:             for (j=0;j<N;j++)
	bne	a4, a14, .L24	# ivtmp$153, _443,
	j	.L16		#
.L30:
	l32i.n	a9, sp, 16	# %sfp,
	l32r	a8, .LC1	#, tmp364
	slli	a4, a9, 1	# tmp328,,
	l32i.n	a9, sp, 40	# %sfp,
	l32i.n	a7, sp, 48	# %sfp, ivtmp$137
# @OPUS@\upstream\celt\celt_decoder.c:387:             for (j=0;j<Nd;j++)
	l32i.n	a10, sp, 52	# %sfp, _537
	add.n	a4, a9, a4	# ivtmp$136,, tmp328
	movi.n	a5, 0	# j,
.L28:
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	l32i.n	a3, a7, 0	# MEM[base: _139, offset: 0B], MEM[base: _139, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:388:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(scratch[j*downsample]))));
	l16si	a9, a4, 0	# MEM[base: _145, offset: 0B], _558
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	addmi	a3, a3, 0x800	# tmp331, MEM[base: _139, offset: 0B],
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	srai	a3, a3, 12	# x, tmp331,
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a3, a8, .L25	# x, tmp364,
	mov.n	a3, a8	# x, tmp364
.L25:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	bge	a12, a3, .L26	# tmp444, x,
	mov.n	a3, a12	# x, tmp444
.L26:
# @OPUS@\upstream\celt\celt_decoder.c:388:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(scratch[j*downsample]))));
	add.n	a3, a9, a3	# tmp365, _558, x
# @OPUS@\upstream\celt\arch.h:157:    return x > 32767 ? 32767 : x < -32768 ? -32768 : (opus_int16)x;
	slli	a14, a3, 16	# tmp347, tmp365,
	mov.n	a9, a12	# iftmp$117_544, tmp444
	blt	a12, a3, .L27	# tmp444, tmp365,
	blt	a3, a8, .L45	# tmp365, tmp364,
	srai	a9, a14, 16	# iftmp$117_544, tmp347,
	j	.L27		#
.L45:
	mov.n	a9, a8	# iftmp$117_544, tmp364
.L27:
# @OPUS@\upstream\celt\celt_decoder.c:388:                y[j*C] = SAT16(ADD32(y[j*C], SCALEOUT(SIG2WORD16(scratch[j*downsample]))));
	s16i	a9, a4, 0	# MEM[base: _145, offset: 0B], iftmp$117_544
# @OPUS@\upstream\celt\celt_decoder.c:387:             for (j=0;j<Nd;j++)
	addi.n	a5, a5, 1	# j, j,
	add.n	a4, a4, a11	# ivtmp$136, ivtmp$136, _439
	add.n	a7, a7, a10	# ivtmp$137, ivtmp$137, _537
# @OPUS@\upstream\celt\celt_decoder.c:387:             for (j=0;j<Nd;j++)
	bne	a2, a5, .L28	# Nd, j,
.L31:
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	movi.n	a3, 1	#,
	s32i.n	a3, sp, 24	# %sfp,
	j	.L29		#
.L37:
# @OPUS@\upstream\celt\celt_decoder.c:387:             for (j=0;j<Nd;j++)
	bgei	a2, 1, .L30	# Nd,,
	j	.L31		#
.L35:
	l32i.n	a5, sp, 16	# %sfp,
	l32i.n	a9, sp, 40	# %sfp,
	slli	a4, a5, 1	# tmp348,,
	l32i.n	a7, sp, 48	# %sfp, ivtmp$140
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	l32i.n	a8, sp, 52	# %sfp, _537
	add.n	a4, a9, a4	# ivtmp$141,, tmp348
	movi.n	a5, 0	# j,
.L34:
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	l32i.n	a3, a7, 0	# MEM[base: _141, offset: 0B], MEM[base: _141, offset: 0B]
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	l32r	a9, .LC1	#,
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	addmi	a3, a3, 0x800	# tmp349, MEM[base: _141, offset: 0B],
# @OPUS@\upstream\celt\fixed_generic.h:181:    x = PSHR32(x, SIG_SHIFT);
	srai	a3, a3, 12	# x, tmp349,
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	addi.n	a5, a5, 1	# j, j,
# @OPUS@\upstream\celt\fixed_generic.h:182:    x = MAX32(x, -32768);
	bge	a3, a9, .L32	# x,,
	mov.n	a3, a9	# x,
.L32:
# @OPUS@\upstream\celt\fixed_generic.h:183:    x = MIN32(x, 32767);
	l32r	a9, .LC0	#,
	bge	a9, a3, .L33	#, x,
	mov.n	a3, a9	# x,
.L33:
# @OPUS@\upstream\celt\fixed_generic.h:184:    return EXTRACT16(x);
	s16i	a3, a4, 0	# MEM[base: _142, offset: 0B], x
	add.n	a7, a7, a8	# ivtmp$140, ivtmp$140, _537
	add.n	a4, a4, a11	# ivtmp$141, ivtmp$141, _439
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	bne	a2, a5, .L34	# Nd, j,
	j	.L31		#
.L38:
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	bgei	a2, 1, .L35	# Nd,,
	j	.L31		#
.L29:
# @OPUS@\upstream\celt\celt_decoder.c:396:    } while (++c<C);
	l32i.n	a3, sp, 16	# %sfp,
	l32i.n	a4, sp, 20	# %sfp,
	addi.n	a3, a3, 1	#,,
	addi.n	a4, a4, 4	#,,
	l32i.n	a5, sp, 36	# %sfp,
	s32i.n	a3, sp, 16	# %sfp,
	s32i.n	a4, sp, 20	# %sfp,
	addi.n	a13, a13, 4	# ivtmp$157, ivtmp$157,
	blt	a3, a5, .L36	#,,
# @OPUS@\upstream\celt\celt_decoder.c:397:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
	j	.L1		#
.L12:
# @OPUS@\upstream\celt\celt_decoder.c:385:          if (accum)
	l32i	a9, sp, 100	# accum,
# @OPUS@\upstream\celt\celt_decoder.c:379:       mem[c] = m;
	s32i.n	a3, a13, 0	# MEM[base: _417, offset: 0B], m
# @OPUS@\upstream\celt\celt_decoder.c:385:          if (accum)
	bnez.n	a9, .L37	#,
	j	.L38		#
.L17:
# @OPUS@\upstream\celt\celt_decoder.c:379:       mem[c] = m;
	s32i.n	a3, a13, 0	# MEM[base: _417, offset: 0B], m
# @OPUS@\upstream\celt\celt_decoder.c:381:       if (apply_downsampling)
	l32i.n	a3, sp, 24	# %sfp,
	bnez.n	a3, .L37	#,
.L39:
# @OPUS@\upstream\celt\celt_decoder.c:392:             for (j=0;j<Nd;j++)
	movi.n	a4, 0	#,
	s32i.n	a4, sp, 24	# %sfp,
	j	.L29		#
.L16:
# @OPUS@\upstream\celt\celt_decoder.c:381:       if (apply_downsampling)
	l32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:379:       mem[c] = m;
	s32i.n	a3, a13, 0	# MEM[base: _417, offset: 0B], m
# @OPUS@\upstream\celt\celt_decoder.c:381:       if (apply_downsampling)
	beqz.n	a5, .L39	#,
	j	.L38		#
.L1:
# @OPUS@\upstream\celt\celt_decoder.c:398: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	deemphasis, .-deemphasis
	.section	.text.prefilter_and_fold,"ax",@progbits
	.literal_position
	.literal .LC3, 2048
	.align	4
	.type	prefilter_and_fold, @function
# Function: prefilter_and_fold
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return pitch_index;
# C context: }
# C context:
# C context: static void prefilter_and_fold(CELTDecoder * OPUS_RESTRICT st, int N)
# C context: {
# C context: int c;
# C context: int CC;
# C context: int i;
prefilter_and_fold:
	addi	sp, sp, -128	#,,
	s32i	a0, sp, 124	#,
	s32i	a13, sp, 116	#,
	s32i	a14, sp, 112	#,
	mov.n	a13, a2	# st, st
	s32i	a15, sp, 108	#,
	s32i	a12, sp, 120	#,
# @OPUS@\upstream\celt\celt_decoder.c:537: {
	mov.n	a15, a3	# N, N
# @OPUS@\upstream\celt\celt_decoder.c:545:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:547:    overlap = st->overlap;
	l32i.n	a8, a13, 4	# *st_84(D).overlap,
# @OPUS@\upstream\celt\celt_decoder.c:545:    SAVE_STACK;
	s32i.n	a2, sp, 32	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:547:    overlap = st->overlap;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:548:    CC = st->channels;
	l32i.n	a8, a13, 8	# *st_84(D).channels,
# @OPUS@\upstream\celt\celt_decoder.c:549:    ALLOC(etmp, overlap, opus_val32);
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:548:    CC = st->channels;
	s32i.n	a8, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:546:    mode = st->mode;
	l32i.n	a8, a13, 0	# *st_84(D).mode,
# @OPUS@\upstream\celt\celt_decoder.c:545:    SAVE_STACK;
	s32i.n	a3, sp, 36	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:549:    ALLOC(etmp, overlap, opus_val32);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
# @OPUS@\upstream\celt\celt_decoder.c:546:    mode = st->mode;
	s32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:549:    ALLOC(etmp, overlap, opus_val32);
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:552:    } while (++c<CC);
	l32i.n	a8, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:549:    ALLOC(etmp, overlap, opus_val32);
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:551:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i.n	a14, a13, 44	# *st_84(D)._decode_mem, _104
# @OPUS@\upstream\celt\celt_decoder.c:552:    } while (++c<CC);
	blti	a8, 2, .L61	#,,
# @OPUS@\upstream\celt\celt_decoder.c:551:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i.n	a8, sp, 48	# %sfp,
	addmi	a2, a8, 0x800	# tmp126,,
	slli	a2, a2, 2	# tmp127, tmp126,
	add.n	a2, a14, a2	# tmp128, _104, tmp127
# @OPUS@\upstream\celt\celt_decoder.c:551:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i.n	a2, sp, 44	# decode_mem, tmp128
.L61:
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	l32i.n	a8, sp, 48	# %sfp,
	l32r	a3, .LC3	#, tmp141
	extui	a12, a8, 31, 1	# tmp133,,
	addi.n	a2, a8, -1	# tmp136,,
	add.n	a12, a12, a8	# tmp134, tmp133,
	slli	a4, a8, 1	# tmp138,,
	movi.n	a8, 0	#,
	s32i.n	a8, sp, 56	# %sfp,
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:558:       comb_filter(etmp, decode_mem[c]+DECODE_BUFFER_SIZE-N,
	slli	a5, a15, 2	# tmp131, N,
	slli	a2, a2, 2	# tmp137, tmp136,
	add.n	a2, a8, a2	#,, tmp137
	neg	a5, a5	# tmp132, tmp131
	sub	a3, a3, a15	# tmp140, tmp141, N
	addmi	a5, a5, 0x2000	#, tmp132,
	s32i	a2, sp, 80	# %sfp,
	slli	a3, a3, 2	#, tmp140,
	addi	a2, a4, -2	#, tmp138,
	s32i	a5, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	srai	a12, a12, 1	# _41, tmp134,
	s32i	a2, sp, 76	# %sfp,
	s32i	a3, sp, 72	# %sfp,
.L67:
# @OPUS@\upstream\celt\celt_decoder.c:558:       comb_filter(etmp, decode_mem[c]+DECODE_BUFFER_SIZE-N,
	l16ui	a2, a13, 76	# *st_84(D).postfilter_gain,
	l32i.n	a8, a13, 40	# *st_84(D).arch, *st_84(D).arch
	l16ui	a7, a13, 78	# *st_84(D).postfilter_gain_old,
	neg	a2, a2	# tmp153, *st_84(D).postfilter_gain
	l32i	a6, a13, 80	# *st_84(D).postfilter_tapset, *st_84(D).postfilter_tapset
	l32i	a3, a13, 84	# *st_84(D).postfilter_tapset_old, *st_84(D).postfilter_tapset_old
	l32i	a5, a13, 68	# *st_84(D).postfilter_period,
	l32i	a4, a13, 72	# *st_84(D).postfilter_period_old,
	slli	a2, a2, 16	# tmp155, tmp153,
	s32i.n	a8, sp, 20	#, *st_84(D).arch
	movi.n	a8, 0	#,
	srai	a2, a2, 16	# tmp154, tmp155,
	s32i.n	a8, sp, 16	#,
	s32i.n	a8, sp, 12	#,
	neg	a7, a7	# tmp143, *st_84(D).postfilter_gain_old
	l32i	a8, sp, 64	# %sfp,
	s32i.n	a6, sp, 8	#, *st_84(D).postfilter_tapset
	s32i.n	a2, sp, 0	#, tmp154
	slli	a7, a7, 16	# tmp145, tmp143,
	l32i.n	a6, sp, 48	# %sfp,
	l32i.n	a2, sp, 52	# %sfp,
	s32i.n	a3, sp, 4	#, *st_84(D).postfilter_tapset_old
	srai	a7, a7, 16	#, tmp145,
	add.n	a3, a14, a8	#, _104,
	call0	comb_filter		#
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	l32i.n	a8, sp, 48	# %sfp,
	bgei	a8, 2, .L62	#,,
.L66:
# @OPUS@\upstream\celt\celt_decoder.c:571:    } while (++c<CC);
	l32i.n	a8, sp, 56	# %sfp,
	movi.n	a2, 2	# tmp158,
	movi.n	a3, 1	#,
	moveqz	a2, a3, a8	# c,,
	l32i.n	a8, sp, 60	# %sfp,
	blt	a2, a8, .L63	# c,,
	j	.L69		#
.L62:
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a10, sp, 52	# %sfp, ivtmp$169
	l32i.n	a6, a8, 52	# *mode_85.window, ivtmp$164
	l32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	movi.n	a7, 0	# i,
	add.n	a9, a6, a8	# ivtmp$167, ivtmp$164,
	l32i	a8, sp, 72	# %sfp,
	add.n	a14, a14, a8	# ivtmp$170, _104,
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	l32i	a8, sp, 80	# %sfp, ivtmp$165
.L65:
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	l32i.n	a4, a8, 0	# MEM[base: _178, offset: 0B], _39
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	l32i.n	a3, a10, 0	# MEM[base: _176, offset: 0B], _58
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	l16si	a15, a6, 0	# MEM[base: _179, offset: 0B], _33
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	l16si	a11, a9, 0	# MEM[base: _177, offset: 0B], _55
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	extui	a2, a4, 0, 16	# tmp163, _39,
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	extui	a5, a3, 0, 16	# tmp166, _58,
	mull	a5, a5, a11	# tmp167, tmp166, _55
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	mull	a2, a2, a15	# tmp164, tmp163, _33
	srai	a4, a4, 16	# tmp170, _39,
	mull	a4, a4, a15	# tmp171, tmp170, _33
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	srai	a3, a3, 16	# tmp174, _58,
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	srai	a2, a2, 15	# tmp165, tmp164,
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	srai	a5, a5, 15	# tmp168, tmp167,
	mull	a11, a3, a11	# tmp175, tmp174, _55
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	add.n	a2, a2, a5	# tmp169, tmp165, tmp168
# @OPUS@\upstream\celt\celt_decoder.c:568:             MULT16_32_Q15(mode->window[i], etmp[overlap-1-i])
	slli	a4, a4, 1	# tmp172, tmp171,
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	add.n	a2, a2, a4	# tmp173, tmp169, tmp172
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	slli	a11, a11, 1	# tmp176, tmp175,
# @OPUS@\upstream\celt\celt_decoder.c:569:             + MULT16_32_Q15(mode->window[overlap-i-1], etmp[i]);
	add.n	a2, a2, a11	# tmp177, tmp173, tmp176
# @OPUS@\upstream\celt\celt_decoder.c:567:          decode_mem[c][DECODE_BUFFER_SIZE-N+i] =
	s32i.n	a2, a14, 0	# MEM[base: _175, offset: 0B], tmp177
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	addi.n	a7, a7, 1	# i, i,
	addi.n	a6, a6, 2	# ivtmp$164, ivtmp$164,
	addi	a8, a8, -4	# ivtmp$165, ivtmp$165,
	addi	a9, a9, -2	# ivtmp$167, ivtmp$167,
	addi.n	a10, a10, 4	# ivtmp$169, ivtmp$169,
	addi.n	a14, a14, 4	# ivtmp$170, ivtmp$170,
# @OPUS@\upstream\celt\celt_decoder.c:565:       for (i=0;i<overlap/2;i++)
	blt	a7, a12, .L65	# i, _41,
	j	.L66		#
.L63:
# @OPUS@\upstream\celt\celt_decoder.c:571:    } while (++c<CC);
	movi.n	a8, 1	#,
	l32i.n	a14, sp, 44	# decode_mem, _104
	s32i.n	a8, sp, 56	# %sfp,
	j	.L67		#
.L69:
# @OPUS@\upstream\celt\celt_decoder.c:572:    RESTORE_STACK;
	l32i.n	a2, sp, 32	# _saved_stack,
	l32i.n	a3, sp, 36	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_decoder.c:573: }
	l32i	a0, sp, 124	#,
	movi	a9, 0x80	#,
	l32i	a12, sp, 120	#,
	l32i	a13, sp, 116	#,
	l32i	a14, sp, 112	#,
	l32i	a15, sp, 108	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	prefilter_and_fold, .-prefilter_and_fold
	.section	.text.celt_synthesis,"ax",@progbits
	.literal_position
	.literal .LC4, -300000000
	.literal .LC5, 300000000
	.align	4
	.type	celt_synthesis, @function
# Function: celt_synthesis
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #ifndef RESYNTH
# C context: static
# C context: #endif
# C context: void celt_synthesis(const CELTMode *mode, celt_norm *X, celt_sig * out_syn[],
# C context: opus_val16 *oldBandE, int start, int effEnd, int C, int CC,
# C context: int isTransient, int LM, int downsample,
# C context: int silence, int arch)
# C context: {
celt_synthesis:
	movi	a9, 0x90	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 140	#,
	s32i	a12, sp, 136	#,
	s32i	a13, sp, 132	#,
	l32i	a12, sp, 156	# LM, LM
	mov.n	a13, a2	# mode, mode
	s32i	a14, sp, 128	#,
	s32i	a15, sp, 124	#,
# @OPUS@\upstream\celt\celt_decoder.c:407: {
	s32i	a4, sp, 96	# %sfp, out_syn
	mov.n	a15, a5	# oldBandE, oldBandE
	s32i	a6, sp, 76	# %sfp, start
	s32i	a7, sp, 80	# %sfp, effEnd
	s32i.n	a3, sp, 56	# %sfp, X
# @OPUS@\upstream\celt\celt_decoder.c:417:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:421:    N = mode->shortMdctSize<<LM;
	l32i.n	a4, a13, 36	# mode_116(D)->shortMdctSize, mode_116(D)->shortMdctSize
# @OPUS@\upstream\celt\celt_decoder.c:419:    overlap = mode->overlap;
	l32i.n	a8, a13, 4	# mode_116(D)->overlap,
# @OPUS@\upstream\celt\celt_decoder.c:421:    N = mode->shortMdctSize<<LM;
	ssl	a12	# LM
	sll	a4, a4	#, mode_116(D)->shortMdctSize
	s32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:420:    nbEBands = mode->nbEBands;
	l32i.n	a11, a13, 8	# mode_116(D)->nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:422:    ALLOC(freq, N, celt_sig); /**< Interleaved signal MDCTs */
	movi.n	a4, 1	#,
# @OPUS@\upstream\celt\celt_decoder.c:417:    SAVE_STACK;
	s32i.n	a2, sp, 16	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:422:    ALLOC(freq, N, celt_sig); /**< Interleaved signal MDCTs */
	l32i	a2, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:417:    SAVE_STACK;
	s32i.n	a3, sp, 20	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:419:    overlap = mode->overlap;
	s32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:422:    ALLOC(freq, N, celt_sig); /**< Interleaved signal MDCTs */
	movi.n	a3, 4	#,
# @OPUS@\upstream\celt\celt_decoder.c:423:    M = 1<<LM;
	ssl	a12	# LM
	sll	a8, a4	#, tmp173
# @OPUS@\upstream\celt\celt_decoder.c:420:    nbEBands = mode->nbEBands;
	s32i.n	a11, sp, 40	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:423:    M = 1<<LM;
	mov.n	a14, a4	# tmp173,
	s32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:422:    ALLOC(freq, N, celt_sig); /**< Interleaved signal MDCTs */
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:425:    if (isTransient)
	l32i	a11, sp, 152	# isTransient,
# @OPUS@\upstream\celt\celt_decoder.c:422:    ALLOC(freq, N, celt_sig); /**< Interleaved signal MDCTs */
	s32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:425:    if (isTransient)
	beqz.n	a11, .L71	#,
# @OPUS@\upstream\celt\celt_decoder.c:429:       shift = mode->maxLM;
	l32i.n	a8, a13, 28	# mode_116(D)->maxLM,
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	l32i	a11, sp, 148	# CC,
# @OPUS@\upstream\celt\celt_decoder.c:429:       shift = mode->maxLM;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:428:       NB = mode->shortMdctSize;
	l32i.n	a9, a13, 36	# mode_116(D)->shortMdctSize, NB
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	bnei	a11, 2, .L97	#,,
	l32i	a5, sp, 144	# C,
	beq	a5, a14, .L72	#,,
.L97:
# @OPUS@\upstream\celt\celt_decoder.c:423:    M = 1<<LM;
	l32i	a8, sp, 68	# %sfp,
	s32i.n	a8, sp, 32	# %sfp,
	j	.L74		#
.L71:
	mov.n	a5, a11	#,
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	l32i	a11, sp, 148	# CC,
# @OPUS@\upstream\celt\celt_decoder.c:433:       shift = mode->maxLM-LM;
	l32i.n	a3, a13, 28	# mode_116(D)->maxLM, mode_116(D)->maxLM
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	addi	a2, a11, -2	# tmp190,,
# @OPUS@\upstream\celt\celt_decoder.c:432:       NB = mode->shortMdctSize<<LM;
	l32i.n	a9, a13, 36	# mode_116(D)->shortMdctSize, mode_116(D)->shortMdctSize
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	moveqz	a5, a14, a2	#, tmp173, tmp190
# @OPUS@\upstream\celt\celt_decoder.c:433:       shift = mode->maxLM-LM;
	sub	a3, a3, a12	#, mode_116(D)->maxLM, LM
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	extui	a2, a5, 0, 8	# tmp193, tmp189
# @OPUS@\upstream\celt\celt_decoder.c:433:       shift = mode->maxLM-LM;
	s32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:432:       NB = mode->shortMdctSize<<LM;
	ssl	a12	# LM
	sll	a9, a9	# NB, mode_116(D)->shortMdctSize
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	beqz.n	a2, .L98	# tmp193,
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	l32i	a6, sp, 144	# C,
	l32i	a8, sp, 152	# isTransient,
	addi.n	a2, a6, -1	# tmp196,,
	moveqz	a8, a14, a2	#, tmp173, tmp196
# @OPUS@\upstream\celt\celt_decoder.c:436:    if (CC==2&&C==1)
	extui	a2, a8, 0, 8	# tmp199, tmp195
	bnez.n	a2, .L75	# tmp199,
.L98:
# @OPUS@\upstream\celt\celt_decoder.c:431:       B = 1;
	movi.n	a11, 1	#,
	s32i.n	a11, sp, 32	# %sfp,
	j	.L74		#
.L72:
# @OPUS@\upstream\celt\celt_decoder.c:440:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	l32i	a8, sp, 164	# silence,
	l32i	a11, sp, 160	# downsample,
	s32i.n	a8, sp, 8	#,
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a3, sp, 56	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i	a6, sp, 76	# %sfp,
	mov.n	a4, a2	#,
	mov.n	a5, a15	#, oldBandE
	mov.n	a2, a13	#, mode
	s32i.n	a11, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	s32i	a9, sp, 100	#,
	call0	denormalise_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i.n	a11, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:444:       OPUS_COPY(freq2, freq, N);
	l32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	extui	a12, a11, 31, 1	# tmp201,,
	add.n	a12, a12, a11	# tmp202, tmp201,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	srai	a12, a12, 1	# tmp203, tmp202,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i.n	a8, a11, 4	# MEM[(celt_sig * *)out_syn_138(D) + 4B], MEM[(celt_sig * *)out_syn_138(D) + 4B]
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	slli	a12, a12, 2	# tmp204, tmp203,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	add.n	a12, a8, a12	# freq2, MEM[(celt_sig * *)out_syn_138(D) + 4B], tmp204
# @OPUS@\upstream\celt\celt_decoder.c:444:       OPUS_COPY(freq2, freq, N);
	l32i	a3, sp, 72	# %sfp,
	movi.n	a5, 4	#,
	mov.n	a2, a12	#, freq2
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:445:       for (b=0;b<B;b++)
	l32i	a8, sp, 68	# %sfp,
	l32i	a9, sp, 100	#,
	bgei	a8, 1, .L77	#,,
.L82:
	l32i	a11, sp, 84	# %sfp,
	blti	a11, 1, .L78	#,,
	slli	a10, a11, 2	# _177,,
.L96:
	l32i	a8, sp, 96	# %sfp, ivtmp$177
# @OPUS@\upstream\celt\celt_decoder.c:468:          for (b=0;b<B;b++)
	movi.n	a7, 0	# c,
	l32r	a5, .LC4	#, tmp267
	l32r	a4, .LC5	#, tmp268
	l32i	a9, sp, 148	# CC, CC
	j	.L79		#
.L77:
	l32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:431:       B = 1;
	movi.n	a15, 0	# ivtmp$184,
	slli	a8, a8, 2	#,,
	addi	a14, a13, 56	# pretmp_273, mode,
	slli	a9, a9, 2	#, NB,
	add.n	a11, a12, a8	#, ivtmp$185,
	s32i.n	a13, sp, 36	# %sfp, mode
	mov.n	a13, a15	# ivtmp$184, ivtmp$184
	l32i	a15, sp, 96	# %sfp, out_syn
	s32i.n	a8, sp, 52	# %sfp,
	s32i.n	a9, sp, 32	# %sfp,
	s32i.n	a11, sp, 40	# %sfp,
.L80:
# @OPUS@\upstream\celt\celt_decoder.c:446:          clt_mdct_backward(&mode->mdct, &freq2[b], out_syn[0]+NB*b, mode->window, overlap, shift, B, arch);
	l32i.n	a8, sp, 36	# %sfp,
	l32i.n	a4, a15, 0	# *out_syn_138(D), *out_syn_138(D)
	l32i.n	a5, a8, 52	# mode_116(D)->window,
	l32i	a11, sp, 168	# arch,
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a6, sp, 44	# %sfp,
	add.n	a4, a4, a13	#, *out_syn_138(D), ivtmp$184
	mov.n	a3, a12	#, ivtmp$185
	s32i.n	a11, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	mov.n	a2, a14	#, pretmp_273
	call0	clt_mdct_backward_c		#
	l32i.n	a11, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:445:       for (b=0;b<B;b++)
	l32i.n	a8, sp, 40	# %sfp,
	addi.n	a12, a12, 4	# ivtmp$185, ivtmp$185,
	add.n	a13, a13, a11	# ivtmp$184, ivtmp$184,
	bne	a8, a12, .L80	#, ivtmp$185,
	l32i.n	a13, sp, 36	# %sfp, mode
	l32i	a12, sp, 72	# %sfp, ivtmp$181
	l32i.n	a11, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:445:       for (b=0;b<B;b++)
	movi.n	a15, 0	# ivtmp$180,
	add.n	a11, a12, a11	#, ivtmp$181,
	s32i.n	a13, sp, 40	# %sfp, mode
	mov.n	a13, a15	# ivtmp$180, ivtmp$180
	mov.n	a15, a12	# ivtmp$181, ivtmp$181
	l32i	a12, sp, 96	# %sfp, out_syn
	s32i.n	a11, sp, 36	# %sfp,
.L81:
# @OPUS@\upstream\celt\celt_decoder.c:448:          clt_mdct_backward(&mode->mdct, &freq[b], out_syn[1]+NB*b, mode->window, overlap, shift, B, arch);
	l32i.n	a8, sp, 40	# %sfp,
	l32i.n	a4, a12, 4	# MEM[(celt_sig * *)out_syn_138(D) + 4B], MEM[(celt_sig * *)out_syn_138(D) + 4B]
	l32i.n	a5, a8, 52	# mode_116(D)->window,
	l32i	a11, sp, 168	# arch,
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a6, sp, 44	# %sfp,
	add.n	a4, a4, a13	#, MEM[(celt_sig * *)out_syn_138(D) + 4B], ivtmp$180
	mov.n	a3, a15	#, ivtmp$181
	s32i.n	a11, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	mov.n	a2, a14	#, pretmp_273
	call0	clt_mdct_backward_c		#
	l32i.n	a11, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:447:       for (b=0;b<B;b++)
	l32i.n	a8, sp, 36	# %sfp,
	addi.n	a15, a15, 4	# ivtmp$181, ivtmp$181,
	add.n	a13, a13, a11	# ivtmp$180, ivtmp$180,
	bne	a8, a15, .L81	#, ivtmp$181,
	j	.L82		#
.L74:
# @OPUS@\upstream\celt\celt_decoder.c:449:    } else if (CC==1&&C==2)
	l32i	a11, sp, 148	# CC,
	bnei	a11, 1, .L83	#,,
	l32i	a5, sp, 144	# C,
	bnei	a5, 2, .L83	#,,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	l32i.n	a11, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:454:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	l32i	a7, sp, 80	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	extui	a8, a11, 31, 1	# tmp223,,
	add.n	a8, a8, a11	# tmp224, tmp223,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:454:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	l32i.n	a10, a11, 0	# *out_syn_138(D), *out_syn_138(D)
# @OPUS@\upstream\celt\celt_decoder.c:454:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	l32i	a11, sp, 164	# silence,
	l32i	a4, sp, 72	# %sfp,
	s32i.n	a11, sp, 8	#,
	l32i	a11, sp, 160	# downsample,
	l32i.n	a3, sp, 56	# %sfp,
	s32i.n	a11, sp, 4	#,
	l32i	a11, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	srai	a8, a8, 1	# tmp225, tmp224,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	slli	a8, a8, 2	# tmp226, tmp225,
# @OPUS@\upstream\celt\celt_decoder.c:454:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	mov.n	a5, a15	#, oldBandE
	mov.n	a2, a13	#, mode
	s32i.n	a11, sp, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:453:       freq2 = out_syn[0]+overlap/2;
	add.n	a14, a10, a8	# freq2, *out_syn_138(D), tmp226
# @OPUS@\upstream\celt\celt_decoder.c:454:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	s32i	a9, sp, 100	#,
	call0	denormalise_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:457:       denormalise_bands(mode, X+N, freq2, oldBandE+nbEBands, start, effEnd, M,
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:457:       denormalise_bands(mode, X+N, freq2, oldBandE+nbEBands, start, effEnd, M,
	l32i	a11, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:457:       denormalise_bands(mode, X+N, freq2, oldBandE+nbEBands, start, effEnd, M,
	slli	a5, a8, 1	# tmp228,,
# @OPUS@\upstream\celt\celt_decoder.c:457:       denormalise_bands(mode, X+N, freq2, oldBandE+nbEBands, start, effEnd, M,
	slli	a3, a11, 1	# tmp230,,
# @OPUS@\upstream\celt\celt_decoder.c:457:       denormalise_bands(mode, X+N, freq2, oldBandE+nbEBands, start, effEnd, M,
	l32i	a8, sp, 164	# silence,
	l32i	a11, sp, 160	# downsample,
	s32i.n	a8, sp, 8	#,
	s32i.n	a11, sp, 4	#,
	l32i	a8, sp, 68	# %sfp,
	l32i.n	a11, sp, 56	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i	a6, sp, 76	# %sfp,
	s32i.n	a8, sp, 0	#,
	add.n	a5, a15, a5	#, oldBandE, tmp228
	mov.n	a4, a14	#, freq2
	add.n	a3, a11, a3	#,, tmp230
	mov.n	a2, a13	#, mode
	call0	denormalise_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:459:       for (i=0;i<N;i++)
	l32i	a8, sp, 84	# %sfp,
	l32i	a9, sp, 100	#,
	blti	a8, 1, .L84	#,,
	l32i	a3, sp, 72	# %sfp, ivtmp$192
	slli	a10, a8, 2	# _177,,
	mov.n	a5, a14	# ivtmp$193, freq2
	add.n	a6, a3, a10	# _113, ivtmp$192, _177
.L85:
# @OPUS@\upstream\celt\celt_decoder.c:460:          freq[i] = ADD32(HALF32(freq[i]), HALF32(freq2[i]));
	l32i.n	a2, a3, 0	# MEM[base: _171, offset: 0B], MEM[base: _171, offset: 0B]
	l32i.n	a4, a5, 0	# MEM[base: _167, offset: 0B], MEM[base: _167, offset: 0B]
	srai	a2, a2, 1	# tmp233, MEM[base: _171, offset: 0B],
	srai	a4, a4, 1	# tmp235, MEM[base: _167, offset: 0B],
	add.n	a2, a2, a4	# tmp237, tmp233, tmp235
# @OPUS@\upstream\celt\celt_decoder.c:460:          freq[i] = ADD32(HALF32(freq[i]), HALF32(freq2[i]));
	s32i.n	a2, a3, 0	# MEM[base: _171, offset: 0B], tmp237
	addi.n	a3, a3, 4	# ivtmp$192, ivtmp$192,
	addi.n	a5, a5, 4	# ivtmp$193, ivtmp$193,
# @OPUS@\upstream\celt\celt_decoder.c:459:       for (i=0;i<N;i++)
	bne	a6, a3, .L85	# _113, ivtmp$192,
	j	.L120		#
.L95:
	l32i.n	a11, sp, 32	# %sfp,
	l32i	a15, sp, 72	# %sfp, ivtmp$189
	slli	a2, a11, 2	# tmp238,,
	add.n	a12, a15, a2	# _186, ivtmp$189, tmp238
# @OPUS@\upstream\celt\celt_decoder.c:431:       B = 1;
	movi.n	a14, 0	# ivtmp$188,
	addi	a8, a13, 56	#, mode,
	slli	a9, a9, 2	#, NB,
	s32i.n	a12, sp, 52	# %sfp, _186
	mov.n	a12, a14	# ivtmp$188, ivtmp$188
	l32i	a14, sp, 96	# %sfp, out_syn
	s32i.n	a8, sp, 40	# %sfp,
	s32i.n	a9, sp, 36	# %sfp,
.L87:
# @OPUS@\upstream\celt\celt_decoder.c:462:          clt_mdct_backward(&mode->mdct, &freq[b], out_syn[0]+NB*b, mode->window, overlap, shift, B, arch);
	l32i.n	a4, a14, 0	# *out_syn_138(D), *out_syn_138(D)
	l32i	a11, sp, 168	# arch,
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a5, a13, 52	# mode_116(D)->window,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a6, sp, 44	# %sfp,
	l32i.n	a2, sp, 40	# %sfp,
	add.n	a4, a4, a12	#, *out_syn_138(D), ivtmp$188
	mov.n	a3, a15	#, ivtmp$189
	s32i.n	a11, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	call0	clt_mdct_backward_c		#
	l32i.n	a11, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:461:       for (b=0;b<B;b++)
	l32i.n	a8, sp, 52	# %sfp,
	addi.n	a15, a15, 4	# ivtmp$189, ivtmp$189,
	add.n	a12, a12, a11	# ivtmp$188, ivtmp$188,
	bne	a8, a15, .L87	#, ivtmp$189,
	j	.L82		#
.L83:
	l32i.n	a11, sp, 32	# %sfp,
	l32i	a8, sp, 84	# %sfp,
	slli	a2, a11, 2	# tmp241,,
	slli	a8, a8, 1	#,,
	l32i.n	a11, sp, 40	# %sfp,
	s32i	a8, sp, 92	# %sfp,
	l32i	a8, sp, 72	# %sfp,
	slli	a11, a11, 1	#,,
	s32i	a15, sp, 64	# %sfp, oldBandE
	l32i	a15, sp, 96	# %sfp, ivtmp$203
	add.n	a14, a2, a8	#, tmp241,
	s32i	a11, sp, 88	# %sfp,
	slli	a9, a9, 2	#, NB,
# @OPUS@\upstream\celt\celt_decoder.c:465:       c=0; do {
	movi.n	a11, 0	#,
	addi	a8, a13, 56	#, mode,
	s32i.n	a14, sp, 36	# %sfp,
	s32i.n	a9, sp, 40	# %sfp,
	s32i.n	a11, sp, 60	# %sfp,
	s32i.n	a8, sp, 52	# %sfp,
	mov.n	a14, a15	# ivtmp$203, ivtmp$203
.L89:
# @OPUS@\upstream\celt\celt_decoder.c:466:          denormalise_bands(mode, X+c*N, freq, oldBandE+c*nbEBands, start, effEnd, M,
	l32i	a11, sp, 164	# silence,
	l32i	a8, sp, 160	# downsample,
	s32i.n	a11, sp, 8	#,
	l32i	a11, sp, 68	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i	a6, sp, 76	# %sfp,
	l32i	a5, sp, 64	# %sfp,
	l32i	a4, sp, 72	# %sfp,
	l32i.n	a3, sp, 56	# %sfp,
	s32i.n	a8, sp, 4	#,
	s32i.n	a11, sp, 0	#,
	mov.n	a2, a13	#, mode
	call0	denormalise_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:468:          for (b=0;b<B;b++)
	l32i.n	a8, sp, 32	# %sfp,
	l32i	a12, sp, 72	# %sfp, ivtmp$198
	movi.n	a15, 0	# ivtmp$197,
	bgei	a8, 1, .L122	#,,
.L91:
# @OPUS@\upstream\celt\celt_decoder.c:470:       } while (++c<CC);
	l32i.n	a11, sp, 60	# %sfp,
	l32i.n	a8, sp, 56	# %sfp,
	addi.n	a11, a11, 1	#,,
	s32i.n	a11, sp, 60	# %sfp,
	l32i	a11, sp, 92	# %sfp,
	addi.n	a14, a14, 4	# ivtmp$203, ivtmp$203,
	add.n	a8, a8, a11	#,,
	s32i.n	a8, sp, 56	# %sfp,
	l32i	a11, sp, 88	# %sfp,
	l32i	a8, sp, 64	# %sfp,
	add.n	a8, a8, a11	#,,
	s32i	a8, sp, 64	# %sfp,
	l32i	a11, sp, 148	# CC,
	l32i.n	a8, sp, 60	# %sfp,
	blt	a8, a11, .L89	#,,
	j	.L82		#
.L122:
	mov.n	a2, a14	# ivtmp$203, ivtmp$203
	mov.n	a14, a15	# ivtmp$197, ivtmp$197
	mov.n	a15, a2	# ivtmp$203, ivtmp$203
.L90:
# @OPUS@\upstream\celt\celt_decoder.c:469:             clt_mdct_backward(&mode->mdct, &freq[b], out_syn[c]+NB*b, mode->window, overlap, shift, B, arch);
	l32i.n	a4, a15, 0	# MEM[base: _268, offset: 0B], MEM[base: _268, offset: 0B]
	l32i	a8, sp, 168	# arch,
	l32i.n	a11, sp, 32	# %sfp,
	l32i.n	a5, a13, 52	# mode_116(D)->window,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a6, sp, 44	# %sfp,
	l32i.n	a2, sp, 52	# %sfp,
	add.n	a4, a4, a14	#, MEM[base: _268, offset: 0B], ivtmp$197
	mov.n	a3, a12	#, ivtmp$198
	s32i.n	a8, sp, 4	#,
	s32i.n	a11, sp, 0	#,
	call0	clt_mdct_backward_c		#
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:468:          for (b=0;b<B;b++)
	l32i.n	a11, sp, 36	# %sfp,
	addi.n	a12, a12, 4	# ivtmp$198, ivtmp$198,
	add.n	a14, a14, a8	# ivtmp$197, ivtmp$197,
	bne	a11, a12, .L90	#, ivtmp$198,
	mov.n	a14, a15	# ivtmp$203, ivtmp$203
	j	.L91		#
.L79:
	l32i.n	a3, a8, 0	# MEM[base: _228, offset: 0B], ivtmp$174
	add.n	a6, a10, a3	# _250, _177, ivtmp$174
.L94:
# @OPUS@\upstream\celt\celt_decoder.c:476:          out_syn[c][i] = SATURATE(out_syn[c][i], SIG_SAT);
	l32i.n	a2, a3, 0	# MEM[base: _266, offset: 0B], MEM[base: _266, offset: 0B]
	bge	a2, a5, .L92	# MEM[base: _266, offset: 0B], tmp267,
	mov.n	a2, a5	# MEM[base: _266, offset: 0B], tmp267
.L92:
# @OPUS@\upstream\celt\celt_decoder.c:476:          out_syn[c][i] = SATURATE(out_syn[c][i], SIG_SAT);
	bge	a4, a2, .L93	# tmp268, MEM[base: _266, offset: 0B],
	mov.n	a2, a4	# MEM[base: _266, offset: 0B], tmp268
.L93:
	s32i.n	a2, a3, 0	# MEM[base: _266, offset: 0B], MEM[base: _266, offset: 0B]
	addi.n	a3, a3, 4	# ivtmp$174, ivtmp$174,
# @OPUS@\upstream\celt\celt_decoder.c:475:       for (i=0;i<N;i++)
	bne	a3, a6, .L94	# ivtmp$174, _250,
# @OPUS@\upstream\celt\celt_decoder.c:477:    } while (++c<CC);
	addi.n	a7, a7, 1	# c, c,
	addi.n	a8, a8, 4	# ivtmp$177, ivtmp$177,
	blt	a7, a9, .L79	# c, CC,
.L78:
# @OPUS@\upstream\celt\celt_decoder.c:478:    RESTORE_STACK;
	l32i.n	a2, sp, 16	# _saved_stack,
	l32i.n	a3, sp, 20	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_decoder.c:479: }
	l32i	a0, sp, 140	#,
	movi	a9, 0x90	#,
	l32i	a12, sp, 136	#,
	l32i	a13, sp, 132	#,
	l32i	a14, sp, 128	#,
	l32i	a15, sp, 124	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L84:
# @OPUS@\upstream\celt\celt_decoder.c:461:       for (b=0;b<B;b++)
	l32i.n	a8, sp, 32	# %sfp,
	bgei	a8, 1, .L95	#,,
	j	.L78		#
.L120:
	l32i.n	a11, sp, 32	# %sfp,
	bgei	a11, 1, .L95	#,,
	j	.L96		#
.L75:
# @OPUS@\upstream\celt\celt_decoder.c:440:       denormalise_bands(mode, X, freq, oldBandE, start, effEnd, M,
	l32i	a8, sp, 68	# %sfp,
	l32i	a11, sp, 164	# silence,
	s32i.n	a8, sp, 0	#,
	l32i	a8, sp, 160	# downsample,
	l32i	a7, sp, 80	# %sfp,
	l32i	a6, sp, 76	# %sfp,
	l32i	a4, sp, 72	# %sfp,
	l32i.n	a3, sp, 56	# %sfp,
	mov.n	a5, a15	#, oldBandE
	mov.n	a2, a13	#, mode
	s32i.n	a11, sp, 8	#,
	s32i.n	a8, sp, 4	#,
	s32i	a9, sp, 100	#,
	call0	denormalise_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i.n	a11, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:444:       OPUS_COPY(freq2, freq, N);
	l32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	extui	a12, a11, 31, 1	# tmp261,,
	add.n	a12, a12, a11	# tmp262, tmp261,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	srai	a12, a12, 1	# tmp263, tmp262,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	l32i.n	a8, a11, 4	# MEM[(celt_sig * *)out_syn_138(D) + 4B], MEM[(celt_sig * *)out_syn_138(D) + 4B]
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	slli	a12, a12, 2	# tmp264, tmp263,
# @OPUS@\upstream\celt\celt_decoder.c:443:       freq2 = out_syn[1]+overlap/2;
	add.n	a12, a8, a12	# freq2, MEM[(celt_sig * *)out_syn_138(D) + 4B], tmp264
# @OPUS@\upstream\celt\celt_decoder.c:444:       OPUS_COPY(freq2, freq, N);
	l32i	a3, sp, 72	# %sfp,
	movi.n	a5, 4	#,
	mov.n	a2, a12	#, freq2
	call0	yoradio_opus_copy		#
	l32i	a9, sp, 100	#,
# @OPUS@\upstream\celt\celt_decoder.c:431:       B = 1;
	s32i	a14, sp, 68	# %sfp, tmp173
	j	.L77		#
	.size	celt_synthesis, .-celt_synthesis
	.section	.text.celt_decoder_get_size,"ax",@progbits
	.literal_position
	.literal .LC6, 48000
	.align	4
	.global	celt_decoder_get_size
	.type	celt_decoder_get_size, @function
# Function: celt_decoder_get_size
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: int celt_decoder_get_size(int channels)
# C context: {
# C context: const CELTMode *mode = opus_custom_mode_create(48000, 960, NULL);
# C context: return opus_custom_decoder_get_size(mode, channels);
# C context: }
celt_decoder_get_size:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 8	#,
	mov.n	a12, a2	# channels, channels
# @OPUS@\upstream\celt\celt_decoder.c:173:    const CELTMode *mode = opus_custom_mode_create(48000, 960, NULL);
	l32r	a2, .LC6	#,
	movi	a3, 0x3c0	#,
	movi.n	a4, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:172: {
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\celt_decoder.c:173:    const CELTMode *mode = opus_custom_mode_create(48000, 960, NULL);
	call0	opus_custom_mode_create		#
# @OPUS@\upstream\celt\celt_decoder.c:186:             + 4*2*mode->nbEBands*sizeof(opus_val16);
	slli	a3, a12, 1	# tmp57, channels,
	add.n	a3, a3, a12	# tmp58, tmp57, channels
	l32i.n	a2, a2, 8	# mode_3->nbEBands, mode_3->nbEBands
	slli	a3, a3, 4	# tmp59, tmp58,
# @OPUS@\upstream\celt\celt_decoder.c:175: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\celt_decoder.c:186:             + 4*2*mode->nbEBands*sizeof(opus_val16);
	slli	a2, a2, 4	# tmp54, mode_3->nbEBands,
	addi	a3, a3, 102	# tmp60, tmp59,
# @OPUS@\upstream\celt\celt_decoder.c:175: }
	add.n	a2, a2, a3	#, tmp54, tmp60
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	celt_decoder_get_size, .-celt_decoder_get_size
	.section	.text.celt_decode_with_ec_dred,"ax",@progbits
	.literal_position
	.literal .LC7, 32767
	.literal .LC8, 26214
	.literal .LC9, -32767
	.literal .LC10, 4096
	.literal .LC11, 2048
	.literal .LC12, 4000
	.literal .LC13, 65534
	.literal .LC14, 32440
	.literal .LC15, 1048512
	.literal .LC16, -300000000
	.literal .LC17, 300000000
	.literal .LC18, 10000
	.literal .LC19, tapset_icdf
	.literal .LC20, -20480
	.literal .LC21, tf_select_table
	.literal .LC22, trim_icdf
	.literal .LC23, -28672
	.literal .LC24, -1879011328
	.literal .LC25, spread_icdf
	.align	4
	.global	celt_decode_with_ec_dred
	.type	celt_decode_with_ec_dred, @function
# Function: celt_decode_with_ec_dred
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: RESTORE_STACK;
# C context: }
# C context:
# C context: int celt_decode_with_ec_dred(CELTDecoder * OPUS_RESTRICT st, const unsigned char *data,
# C context: int len, opus_val16 * OPUS_RESTRICT pcm, int frame_size, ec_dec *dec, int accum
# C context: #ifdef ENABLE_DEEP_PLC
# C context: ,LPCNetPLCState *lpcnet
# C context: #endif
celt_decode_with_ec_dred:
	movi	a9, 0x1d0	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1040:    const int CC = st->channels;
	l32i.n	a8, a2, 8	# *st_322(D).channels,
# @OPUS@\upstream\celt\celt_decoder.c:1059:    int C = st->stream_channels;
	l32i.n	a9, a2, 12	# *st_322(D).stream_channels,
# @OPUS@\upstream\celt\celt_decoder.c:1019: {
	s32i	a13, sp, 452	#,
# @OPUS@\upstream\celt\celt_decoder.c:1049:    int intensity=0;
	movi.n	a13, 0	# tmp1071,
# @OPUS@\upstream\celt\celt_decoder.c:1019: {
	s32i	a12, sp, 456	#,
	s32i	a14, sp, 448	#,
	s32i	a15, sp, 444	#,
	mov.n	a14, a6	# frame_size, frame_size
# @OPUS@\upstream\celt\celt_decoder.c:1040:    const int CC = st->channels;
	s32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1019: {
	s32i	a4, sp, 304	# %sfp, len
# @OPUS@\upstream\celt\celt_decoder.c:1059:    int C = st->stream_channels;
	s32i	a9, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1019: {
	s32i	a0, sp, 460	#,
# @OPUS@\upstream\celt\celt_decoder.c:1019: {
	s32i	a2, sp, 244	# %sfp, st
	mov.n	a12, a3	# data, data
	s32i	a5, sp, 364	# %sfp, pcm
	mov.n	a15, a7	# dec, dec
# @OPUS@\upstream\celt\celt_decoder.c:1049:    int intensity=0;
	s32i	a13, sp, 236	# intensity, tmp1071
# @OPUS@\upstream\celt\celt_decoder.c:1050:    int dual_stereo=0;
	s32i	a13, sp, 232	# dual_stereo, tmp1071
# @OPUS@\upstream\celt\celt_decoder.c:1065:    ALLOC_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:1068:    mode = st->mode;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	l32i	a11, sp, 312	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1068:    mode = st->mode;
	l32i.n	a10, a10, 0	# *st_322(D).mode,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	slli	a4, a11, 1	# tmp1076,,
# @OPUS@\upstream\celt\celt_decoder.c:1077:    lpc = st->_tail;
	l32i	a9, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1069:    nbEBands = mode->nbEBands;
	l32i.n	a8, a10, 8	# mode_328->nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	add.n	a4, a4, a11	# tmp1077, tmp1076,
# @OPUS@\upstream\celt\celt_decoder.c:1077:    lpc = st->_tail;
	addi	a9, a9, 100	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	slli	a4, a4, 4	#, tmp1077,
# @OPUS@\upstream\celt\celt_decoder.c:1068:    mode = st->mode;
	s32i	a10, sp, 288	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1074:    frame_size *= st->downsample;
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1082:    oldLogE = oldBandE + 2*nbEBands;
	slli	a10, a8, 2	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1069:    nbEBands = mode->nbEBands;
	s32i	a8, sp, 280	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1077:    lpc = st->_tail;
	s32i	a9, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	add.n	a8, a9, a4	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	l32i	a9, sp, 288	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1082:    oldLogE = oldBandE + 2*nbEBands;
	s32i	a10, sp, 296	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1074:    frame_size *= st->downsample;
	l32i.n	a6, a11, 16	# *st_322(D).downsample, *st_322(D).downsample
# @OPUS@\upstream\celt\celt_decoder.c:1082:    oldLogE = oldBandE + 2*nbEBands;
	add.n	a10, a8, a10	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1070:    overlap = mode->overlap;
	l32i.n	a11, a9, 4	# mode_328->overlap,
# @OPUS@\upstream\celt\celt_decoder.c:1082:    oldLogE = oldBandE + 2*nbEBands;
	s32i	a10, sp, 328	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	s32i	a4, sp, 284	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1081:    oldBandE = lpc+CC*CELT_LPC_ORDER;
	s32i	a8, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	l32i.n	a4, a9, 28	# mode_328->maxLM, _1191
# @OPUS@\upstream\celt\celt_decoder.c:1071:    eBands = mode->eBands;
	l32i.n	a8, a9, 24	# mode_328->eBands,
# @OPUS@\upstream\celt\celt_decoder.c:1073:    end = st->end;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1072:    start = st->start;
	l32i	a9, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1074:    frame_size *= st->downsample;
	mull	a6, a14, a6	#, frame_size, *st_322(D).downsample
# @OPUS@\upstream\celt\celt_decoder.c:1070:    overlap = mode->overlap;
	s32i	a11, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1083:    oldLogE2 = oldLogE + 2*nbEBands;
	l32i	a14, sp, 296	# %sfp,
	l32i	a11, sp, 328	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1072:    start = st->start;
	l32i.n	a9, a9, 20	# *st_322(D).start,
# @OPUS@\upstream\celt\celt_decoder.c:1073:    end = st->end;
	l32i.n	a10, a10, 24	# *st_322(D).end,
# @OPUS@\upstream\celt\celt_decoder.c:1083:    oldLogE2 = oldLogE + 2*nbEBands;
	add.n	a11, a11, a14	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1065:    ALLOC_STACK;
	s32i	a2, sp, 204	# _saved_stack,
	s32i	a3, sp, 208	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:1071:    eBands = mode->eBands;
	s32i	a8, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1072:    start = st->start;
	s32i	a9, sp, 268	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1073:    end = st->end;
	s32i	a10, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1074:    frame_size *= st->downsample;
	s32i	a6, sp, 352	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1083:    oldLogE2 = oldLogE + 2*nbEBands;
	s32i	a11, sp, 348	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	blt	a4, a13, .L373	# _1191,,
# @OPUS@\upstream\celt\celt_decoder.c:1113:          if (mode->shortMdctSize<<LM==frame_size)
	l32i	a8, sp, 288	# %sfp,
	l32i.n	a8, a8, 36	# mode_328->shortMdctSize,
	s32i	a8, sp, 300	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1113:          if (mode->shortMdctSize<<LM==frame_size)
	beq	a6, a8, .L340	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	s32i	a13, sp, 260	# %sfp, tmp1071
	mov.n	a2, a13	# LM, tmp1071
	mov.n	a5, a8	# _1186,
	j	.L127		#
.L128:
# @OPUS@\upstream\celt\celt_decoder.c:1113:          if (mode->shortMdctSize<<LM==frame_size)
	bne	a3, a6, .L127	# tmp1079, frame_size,
	s32i	a2, sp, 260	# %sfp, LM
	l32i	a9, sp, 260	# %sfp,
	movi.n	a2, 1	# tmp1080,
	l32i	a10, sp, 352	# %sfp,
	ssl	a9	#
	sll	a2, a2	#, tmp1080
	s32i	a2, sp, 400	# %sfp,
	s32i	a10, sp, 300	# %sfp,
	j	.L126		#
.L127:
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	addi.n	a2, a2, 1	# LM, LM,
# @OPUS@\upstream\celt\celt_decoder.c:1113:          if (mode->shortMdctSize<<LM==frame_size)
	ssl	a2	# LM
	sll	a3, a5	# tmp1079, _1186
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	bge	a4, a2, .L128	# _1191, LM,
	j	.L373		#
.L474:
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	l32i	a11, sp, 300	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i	a14, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	slli	a2, a11, 2	# tmp1083,,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i.n	a3, a14, 44	# *st_322(D)._decode_mem, _19
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	neg	a2, a2	# tmp1084, tmp1083
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i	a8, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	addmi	a2, a2, 0x2000	#, tmp1084,
	s32i	a2, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	addmi	a8, a8, 0x800	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	add.n	a2, a3, a2	# tmp1085, _19,
# @OPUS@\upstream\celt\celt_decoder.c:1127:    } while (++c<CC);
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i	a3, sp, 220	# decode_mem, _19
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	s32i	a2, sp, 212	# out_syn, tmp1085
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i	a8, sp, 376	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1127:    } while (++c<CC);
	blti	a9, 2, .L129	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	slli	a2, a8, 2	# tmp1086,,
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	l32i	a10, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	add.n	a3, a3, a2	# _24, _19, tmp1086
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	add.n	a2, a3, a10	# tmp1087, _24,
# @OPUS@\upstream\celt\celt_decoder.c:1125:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i	a3, sp, 224	# decode_mem, _24
# @OPUS@\upstream\celt\celt_decoder.c:1126:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	s32i	a2, sp, 216	# out_syn, tmp1087
.L129:
	l32i	a11, sp, 288	# %sfp,
	l32i	a14, sp, 264	# %sfp,
	l32i.n	a11, a11, 12	# mode_328->effEBands,
	s32i	a11, sp, 340	# %sfp,
	bge	a14, a11, .L130	#,,
	s32i	a14, sp, 340	# %sfp,
.L130:
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	movi.n	a4, 0	# tmp1095,
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	l32i	a8, sp, 304	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	movi.n	a2, 1	# tmp1094,
	mov.n	a3, a4	# tmp1093, tmp1095
	moveqz	a3, a2, a12	# tmp1093, tmp1094, data
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	blti	a8, 2, .L131	#,,
	mov.n	a2, a4	# tmp1096, tmp1095
.L131:
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	or	a2, a3, a2	# tmp1098, tmp1093, tmp1096
	extui	a2, a2, 0, 8	#, tmp1098
	s32i	a2, sp, 332	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1133:    if (data == NULL || len<=1)
	beqz.n	a2, .L132	#,
# @OPUS@\upstream\celt\celt_decoder.c:635:    const int C = st->channels;
	l32i	a9, sp, 244	# %sfp,
	l32i.n	a9, a9, 8	# *st_322(D).channels,
	s32i	a9, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:647:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:649:    mode = st->mode;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:649:    mode = st->mode;
	l32i.n	a10, a10, 0	# *st_322(D).mode,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	l32i.n	a4, a11, 44	# *st_322(D)._decode_mem, _541
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	l32i	a14, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:651:    overlap = mode->overlap;
	l32i.n	a12, a10, 4	# mode_537->overlap,
# @OPUS@\upstream\celt\celt_decoder.c:652:    eBands = mode->eBands;
	l32i.n	a6, a10, 24	# mode_537->eBands,
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	add.n	a5, a4, a14	# tmp1100, _541,
# @OPUS@\upstream\celt\celt_decoder.c:657:    } while (++c<C);
	l32i	a8, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:649:    mode = st->mode;
	s32i	a10, sp, 280	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:651:    overlap = mode->overlap;
	s32i	a12, sp, 296	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:647:    SAVE_STACK;
	s32i	a2, sp, 180	# _saved_stack,
	s32i	a3, sp, 184	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i	a4, sp, 196	# decode_mem, _541
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	s32i	a5, sp, 188	# out_syn, tmp1100
# @OPUS@\upstream\celt\celt_decoder.c:652:    eBands = mode->eBands;
	s32i	a6, sp, 256	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:650:    nbEBands = mode->nbEBands;
	l32i.n	a13, a10, 8	# mode_537->nbEBands, nbEBands
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	addmi	a14, a12, 0x800	# _542,,
# @OPUS@\upstream\celt\celt_decoder.c:657:    } while (++c<C);
	blti	a8, 2, .L133	#,,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	slli	a2, a14, 2	# tmp1101, _542,
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	l32i	a9, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	add.n	a4, a4, a2	# _547, _541, tmp1101
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	add.n	a2, a4, a9	# tmp1102, _547,
# @OPUS@\upstream\celt\celt_decoder.c:655:       decode_mem[c] = st->_decode_mem + c*(DECODE_BUFFER_SIZE+overlap);
	s32i	a4, sp, 200	# decode_mem, _547
# @OPUS@\upstream\celt\celt_decoder.c:656:       out_syn[c] = decode_mem[c]+DECODE_BUFFER_SIZE-N;
	s32i	a2, sp, 192	# out_syn, tmp1102
.L133:
# @OPUS@\upstream\celt\celt_decoder.c:668:    loss_duration = st->loss_duration;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:669:    start = st->start;
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:668:    loss_duration = st->loss_duration;
	l32i.n	a10, a10, 60	# *st_322(D).loss_duration,
# @OPUS@\upstream\celt\celt_decoder.c:669:    start = st->start;
	l32i.n	a11, a11, 20	# *st_322(D).start,
# @OPUS@\upstream\celt\celt_decoder.c:668:    loss_duration = st->loss_duration;
	s32i	a10, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:673:    noise_based = loss_duration >= 40 || start != 0 || st->skip_plc;
	movi.n	a2, 0x27	# tmp1105,
# @OPUS@\upstream\celt\celt_decoder.c:669:    start = st->start;
	s32i	a11, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:673:    noise_based = loss_duration >= 40 || start != 0 || st->skip_plc;
	blt	a2, a10, .L134	# tmp1105,,
# @OPUS@\upstream\celt\celt_decoder.c:673:    noise_based = loss_duration >= 40 || start != 0 || st->skip_plc;
	bnez.n	a11, .L134	#,
# @OPUS@\upstream\celt\celt_decoder.c:673:    noise_based = loss_duration >= 40 || start != 0 || st->skip_plc;
	l32i	a12, sp, 244	# %sfp,
	l32i	a12, a12, 64	# *st_322(D).skip_plc,
	s32i	a12, sp, 268	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:673:    noise_based = loss_duration >= 40 || start != 0 || st->skip_plc;
	bnez.n	a12, .L134	#,
# @OPUS@\upstream\celt\celt_decoder.c:737:       if (loss_duration == 0)
	bnez.n	a10, .L465	#,
	j	.L136		#
.L134:
# @OPUS@\upstream\celt\celt_decoder.c:683:       end = st->end;
	l32i	a8, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:684:       effEnd = IMAX(start, IMIN(end, mode->effEBands));
	l32i	a9, sp, 280	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:683:       end = st->end;
	l32i.n	a12, a8, 24	# *st_322(D).end, end
# @OPUS@\upstream\celt\celt_decoder.c:684:       effEnd = IMAX(start, IMIN(end, mode->effEBands));
	l32i.n	a2, a9, 12	# mode_537->effEBands, mode_537->effEBands
	bge	a12, a2, .L138	# end, mode_537->effEBands,
	mov.n	a2, a12	# mode_537->effEBands, end
.L138:
# @OPUS@\upstream\celt\celt_decoder.c:684:       effEnd = IMAX(start, IMIN(end, mode->effEBands));
	l32i	a10, sp, 276	# %sfp,
	s32i	a2, sp, 292	# %sfp, mode_537->effEBands
	bge	a2, a10, .L139	# mode_537->effEBands,,
	s32i	a10, sp, 292	# %sfp,
.L139:
# @OPUS@\upstream\celt\celt_decoder.c:686:       ALLOC(X, C*N, celt_norm);   /**< Interleaved normalised MDCTs */
	l32i	a11, sp, 272	# %sfp,
	l32i	a8, sp, 300	# %sfp,
	movi.n	a4, 0	#,
	mull	a2, a11, a8	#,,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:688:          OPUS_MOVE(decode_mem[c], decode_mem[c]+N,
	l32i	a9, sp, 300	# %sfp,
	l32i	a10, sp, 300	# %sfp,
	slli	a9, a9, 2	#,,
	sub	a14, a14, a10	#, _542,
	addi	a11, sp, 80	#,,
	s32i	a14, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:686:       ALLOC(X, C*N, celt_norm);   /**< Interleaved normalised MDCTs */
	s32i	a2, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:688:          OPUS_MOVE(decode_mem[c], decode_mem[c]+N,
	s32i	a9, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:687:       c=0; do {
	movi.n	a14, 0	# c,
	s32i	a11, sp, 308	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:690:       } while (++c<C);
	movi.n	a15, 1	# c,
.L140:
# @OPUS@\upstream\celt\celt_decoder.c:688:          OPUS_MOVE(decode_mem[c], decode_mem[c]+N,
	l32i	a8, sp, 308	# %sfp,
	slli	a2, a14, 2	# tmp1118, c,
	add.n	a2, a8, a2	# tmp1119,, tmp1118
	l32i	a2, a2, 116	# decode_mem, _575
	l32i	a9, sp, 264	# %sfp,
	l32i	a4, sp, 252	# %sfp,
	add.n	a3, a2, a9	#, _575,
	movi.n	a5, 4	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:690:       } while (++c<C);
	l32i	a10, sp, 272	# %sfp,
	addi.n	a2, a14, 1	# c, c,
	mov.n	a14, a15	# c, c
	blt	a2, a10, .L140	# c,,
# @OPUS@\upstream\celt\celt_decoder.c:692:       if (st->prefilter_and_fold) {
	l32i	a11, sp, 244	# %sfp,
	l32i	a2, a11, 88	# *st_322(D).prefilter_and_fold, *st_322(D).prefilter_and_fold
	beqz.n	a2, .L141	# *st_322(D).prefilter_and_fold,
# @OPUS@\upstream\celt\celt_decoder.c:693:          prefilter_and_fold(st, N);
	l32i	a3, sp, 300	# %sfp,
	mov.n	a2, a11	#,
	call0	prefilter_and_fold		#
.L141:
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	l32i	a14, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	l32i	a9, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	slli	a2, a14, 1	# tmp1124,,
	add.n	a2, a2, a14	# tmp1125, tmp1124,
# @OPUS@\upstream\celt\celt_decoder.c:697:       decay = loss_duration==0 ? QCONST16(1.5f, DB_SHIFT) : QCONST16(.5f, DB_SHIFT);
	l32i	a8, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	slli	a2, a2, 4	# tmp1126, tmp1125,
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	add.n	a2, a9, a2	#,, tmp1126
# @OPUS@\upstream\celt\celt_decoder.c:664:    oldLogE = oldBandE + 2*nbEBands;
	slli	a3, a13, 2	# tmp1127, nbEBands,
	slli	a6, a13, 3	# tmp1129, nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:697:       decay = loss_duration==0 ? QCONST16(1.5f, DB_SHIFT) : QCONST16(.5f, DB_SHIFT);
	movi	a7, 0x600	# tmp1996,
	movi	a4, 0x200	# tmp1997,
# @OPUS@\upstream\celt\celt_decoder.c:702:       } while (++c<C);
	l32i	a10, sp, 276	# %sfp, start
# @OPUS@\upstream\celt\celt_decoder.c:697:       decay = loss_duration==0 ? QCONST16(1.5f, DB_SHIFT) : QCONST16(.5f, DB_SHIFT);
	movnez	a7, a4, a8	# prephitmp_1981, tmp1997,
# @OPUS@\upstream\celt\celt_decoder.c:663:    oldBandE = lpc+C*CELT_LPC_ORDER;
	s32i	a2, sp, 284	# %sfp,
	add.n	a6, a6, a3	# _560, tmp1129, tmp1127
# @OPUS@\upstream\celt\celt_decoder.c:698:       c=0; do
	movi.n	a8, 0	# c,
# @OPUS@\upstream\celt\celt_decoder.c:702:       } while (++c<C);
	movi.n	a9, 1	# c,
	mov.n	a11, a2	# oldBandE,
.L144:
# @OPUS@\upstream\celt\celt_decoder.c:700:          for (i=start;i<end;i++)
	blt	a10, a12, .L143	# start, end,
.L148:
# @OPUS@\upstream\celt\celt_decoder.c:702:       } while (++c<C);
	addi.n	a2, a8, 1	# c, c,
	mov.n	a8, a9	# c, c
	blt	a2, a14, .L144	# c, C,
	j	.L466		#
.L143:
# @OPUS@\upstream\celt\celt_decoder.c:701:             oldBandE[c*nbEBands+i] = MAX16(backgroundLogE[c*nbEBands+i], oldBandE[c*nbEBands+i] - decay);
	mull	a2, a13, a8	# _585, nbEBands, c
	add.n	a5, a12, a2	# tmp1133, end, _585
	add.n	a3, a10, a2	# tmp1131, start, _585
	slli	a2, a3, 1	# tmp1132, tmp1131,
	slli	a5, a5, 1	# tmp1134, tmp1133,
	add.n	a2, a11, a2	# ivtmp$255, oldBandE, tmp1132
	add.n	a5, a11, a5	# _880, oldBandE, tmp1134
.L147:
	l16si	a3, a2, 0	# MEM[base: _2148, offset: 0B], tmp1136
	add.n	a4, a2, a6	# tmp1140, ivtmp$255, _560
	l16si	a4, a4, 0	# MEM[base: _2149, offset: 0B], tmp1141
	sub	a3, a3, a7	# tmp1135, tmp1136, prephitmp_1981
	bge	a3, a4, .L146	# tmp1135, tmp1141,
	mov.n	a3, a4	# tmp1135, tmp1141
.L146:
# @OPUS@\upstream\celt\celt_decoder.c:701:             oldBandE[c*nbEBands+i] = MAX16(backgroundLogE[c*nbEBands+i], oldBandE[c*nbEBands+i] - decay);
	s16i	a3, a2, 0	# MEM[base: _2148, offset: 0B], tmp1135
	addi.n	a2, a2, 2	# ivtmp$255, ivtmp$255,
# @OPUS@\upstream\celt\celt_decoder.c:700:          for (i=start;i<end;i++)
	bne	a5, a2, .L147	# _880, ivtmp$255,
	j	.L148		#
.L466:
# @OPUS@\upstream\celt\celt_decoder.c:703:       seed = st->rng;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	l32i	a11, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:703:       seed = st->rng;
	l32i.n	a6, a10, 48	# *st_322(D).rng, seed
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	blti	a11, 1, .L149	#,,
	l32i	a12, sp, 276	# %sfp,
	l32i	a14, sp, 292	# %sfp,
	l32i	a8, sp, 256	# %sfp,
	slli	a3, a12, 1	# tmp1144,,
	slli	a2, a14, 1	# tmp1145,,
	l32r	a15, .LC7	#, tmp1961
	movi.n	a7, 0	#,
	add.n	a3, a8, a3	#,, tmp1144
	add.n	a2, a8, a2	#,, tmp1145
	s32i	a7, sp, 252	# %sfp,
	s32i	a3, sp, 304	# %sfp,
	s32i	a2, sp, 256	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	s32i	a7, sp, 296	# %sfp,
	s32i	a6, sp, 264	# %sfp, seed
	s32i	a15, sp, 268	# %sfp, tmp1961
	j	.L150		#
.L153:
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	l16si	a2, a15, 0	# MEM[base: _1348, offset: 0B], _612
# @OPUS@\upstream\celt\celt_decoder.c:712:             blen = (eBands[i+1]-eBands[i])<<LM;
	l16si	a13, a15, 2	# MEM[base: _1348, offset: 2B], tmp1149
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	l32i	a9, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:712:             blen = (eBands[i+1]-eBands[i])<<LM;
	sub	a13, a13, a2	# tmp1152, tmp1149, _612
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	l32i	a10, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	ssl	a9	#
	sll	a14, a2	# tmp1148, _612
# @OPUS@\upstream\celt\celt_decoder.c:712:             blen = (eBands[i+1]-eBands[i])<<LM;
	ssl	a9	#
	sll	a13, a13	# blen, tmp1152
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	add.n	a14, a14, a10	# boffs, tmp1148,
# @OPUS@\upstream\celt\celt_decoder.c:713:             for (j=0;j<blen;j++)
	bgei	a13, 1, .L467	# blen,,
	slli	a14, a14, 1	#, boffs,
	s32i	a14, sp, 248	# %sfp,
	j	.L151		#
.L467:
	add.n	a12, a13, a14	# tmp1154, blen, boffs
	l32i	a11, sp, 240	# %sfp,
	slli	a14, a14, 1	#, boffs,
	slli	a12, a12, 1	# tmp1155, tmp1154,
	l32i	a2, sp, 264	# %sfp, seed
	s32i	a14, sp, 248	# %sfp,
	add.n	a12, a11, a12	# _1494,, tmp1155
	add.n	a14, a11, a14	# ivtmp$241,,
.L152:
# @OPUS@\upstream\celt\celt_decoder.c:715:                seed = celt_lcg_rand(seed);
	call0	celt_lcg_rand		#
# @OPUS@\upstream\celt\celt_decoder.c:716:                X[boffs+j] = (celt_norm)((opus_int32)seed>>20);
	srai	a3, a2, 20	# tmp1156, seed,
# @OPUS@\upstream\celt\celt_decoder.c:716:                X[boffs+j] = (celt_norm)((opus_int32)seed>>20);
	s16i	a3, a14, 0	# MEM[base: _80, offset: 0B], tmp1156
	addi.n	a14, a14, 2	# ivtmp$241, ivtmp$241,
# @OPUS@\upstream\celt\celt_decoder.c:713:             for (j=0;j<blen;j++)
	bne	a12, a14, .L152	# _1494, ivtmp$241,
	s32i	a2, sp, 264	# %sfp, seed
.L151:
# @OPUS@\upstream\celt\celt_decoder.c:718:             renormalise_vector(X+boffs, blen, Q15ONE, st->arch);
	l32i	a12, sp, 244	# %sfp,
	l32i	a14, sp, 240	# %sfp,
	l32i	a6, sp, 248	# %sfp,
	l32i.n	a5, a12, 40	# *st_322(D).arch,
	l32i	a4, sp, 268	# %sfp,
	mov.n	a3, a13	#, blen
	add.n	a2, a14, a6	#,,
	call0	renormalise_vector		#
# @OPUS@\upstream\celt\celt_decoder.c:706:          for (i=start;i<effEnd;i++)
	l32i	a7, sp, 256	# %sfp,
	addi.n	a15, a15, 2	# ivtmp$245, ivtmp$245,
	bne	a15, a7, .L153	# ivtmp$245,,
.L155:
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	l32i	a8, sp, 296	# %sfp,
	l32i	a9, sp, 252	# %sfp,
	l32i	a10, sp, 300	# %sfp,
	addi.n	a8, a8, 1	#,,
	add.n	a9, a9, a10	#,,
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	l32i	a11, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	s32i	a8, sp, 296	# %sfp,
	s32i	a9, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:704:       for (c=0;c<C;c++)
	beq	a11, a8, .L477	#,,
.L150:
# @OPUS@\upstream\celt\celt_decoder.c:706:          for (i=start;i<effEnd;i++)
	l32i	a12, sp, 276	# %sfp,
	l32i	a14, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:711:             boffs = N*c+(eBands[i]<<LM);
	l32i	a15, sp, 304	# %sfp, ivtmp$245
# @OPUS@\upstream\celt\celt_decoder.c:706:          for (i=start;i<effEnd;i++)
	blt	a12, a14, .L153	#,,
	j	.L155		#
.L477:
	l32i	a6, sp, 264	# %sfp, seed
.L149:
# @OPUS@\upstream\celt\celt_decoder.c:723:       celt_synthesis(mode, X, out_syn, oldBandE, start, effEnd, C, C, 0, LM, st->downsample, 0, st->arch);
	l32i	a8, sp, 244	# %sfp,
	l32i	a10, sp, 272	# %sfp,
	l32i.n	a3, a8, 40	# *st_322(D).arch, *st_322(D).arch
	l32i.n	a2, a8, 16	# *st_322(D).downsample, *st_322(D).downsample
# @OPUS@\upstream\celt\celt_decoder.c:721:       st->rng = seed;
	s32i.n	a6, a8, 48	# *st_322(D).rng, seed
# @OPUS@\upstream\celt\celt_decoder.c:723:       celt_synthesis(mode, X, out_syn, oldBandE, start, effEnd, C, C, 0, LM, st->downsample, 0, st->arch);
	l32i	a9, sp, 260	# %sfp,
	l32i	a11, sp, 308	# %sfp,
	movi.n	a12, 0	# tmp1162,
	s32i.n	a3, sp, 24	#, *st_322(D).arch
	s32i.n	a2, sp, 16	#, *st_322(D).downsample
	l32i	a7, sp, 292	# %sfp,
	l32i	a2, sp, 280	# %sfp,
	l32i	a6, sp, 276	# %sfp,
	l32i	a5, sp, 284	# %sfp,
	l32i	a3, sp, 240	# %sfp,
	s32i.n	a12, sp, 20	#, tmp1162
	s32i.n	a9, sp, 12	#,
	s32i.n	a12, sp, 8	#, tmp1162
	s32i.n	a10, sp, 4	#,
	s32i.n	a10, sp, 0	#,
	addi	a4, a11, 108	#,,
	call0	celt_synthesis		#
# @OPUS@\upstream\celt\celt_decoder.c:724:       st->prefilter_and_fold = 0;
	l32i	a14, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:726:       st->skip_plc = 1;
	movi.n	a2, 1	# tmp1166,
# @OPUS@\upstream\celt\celt_decoder.c:724:       st->prefilter_and_fold = 0;
	s32i	a12, a14, 88	# *st_322(D).prefilter_and_fold, tmp1162
# @OPUS@\upstream\celt\celt_decoder.c:726:       st->skip_plc = 1;
	s32i	a2, a14, 64	# *st_322(D).skip_plc, tmp1166
	j	.L156		#
.L136:
# @OPUS@\upstream\celt\celt_decoder.c:742:          st->last_pitch_index = pitch_index = celt_plc_pitch_search(decode_mem, C, st->arch);
	l32i	a8, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:528:    pitch_search(lp_pitch_buf+(PLC_PITCH_LAG_MAX>>1), lp_pitch_buf,
	movi	a13, 0x2d0	# tmp1172,
# @OPUS@\upstream\celt\celt_decoder.c:742:          st->last_pitch_index = pitch_index = celt_plc_pitch_search(decode_mem, C, st->arch);
	l32i.n	a15, a8, 40	# *st_322(D).arch, _642
# @OPUS@\upstream\celt\celt_decoder.c:524:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\celt_decoder.c:525:    ALLOC( lp_pitch_buf, DECODE_BUFFER_SIZE>>1, opus_val16 );
	l32i	a4, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:524:    SAVE_STACK;
	s32i	a2, sp, 80	# _saved_stack,
	s32i	a3, sp, 84	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:525:    ALLOC( lp_pitch_buf, DECODE_BUFFER_SIZE>>1, opus_val16 );
	movi	a2, 0x400	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:526:    pitch_downsample(decode_mem, lp_pitch_buf,
	l32r	a12, .LC11	#, tmp1965
	addi	a9, sp, 80	#,,
	l32i	a5, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:525:    ALLOC( lp_pitch_buf, DECODE_BUFFER_SIZE>>1, opus_val16 );
	mov.n	a14, a2	# lp_pitch_buf,
# @OPUS@\upstream\celt\celt_decoder.c:526:    pitch_downsample(decode_mem, lp_pitch_buf,
	mov.n	a6, a15	#, _642
	mov.n	a3, a2	#, lp_pitch_buf
	mov.n	a4, a12	#, tmp1965
	addi	a2, a9, 116	#,,
	s32i	a9, sp, 308	# %sfp,
	call0	pitch_downsample		#
# @OPUS@\upstream\celt\celt_decoder.c:528:    pitch_search(lp_pitch_buf+(PLC_PITCH_LAG_MAX>>1), lp_pitch_buf,
	l32i	a10, sp, 308	# %sfp,
	movi	a6, 0x94	# tmp1170,
	add.n	a2, a14, a13	#, lp_pitch_buf, tmp1172
	mov.n	a7, a15	#, _642
	mov.n	a3, a14	#, lp_pitch_buf
	add.n	a6, a10, a6	#,, tmp1170
	movi	a5, 0x26c	#,
	movi	a4, 0x530	#,
	call0	pitch_search		#
# @OPUS@\upstream\celt\celt_decoder.c:531:    pitch_index = PLC_PITCH_LAG_MAX-pitch_index;
	l32i	a4, sp, 228	# pitch_index, pitch_index
# @OPUS@\upstream\celt\celt_decoder.c:532:    RESTORE_STACK;
	l32i	a2, sp, 80	# _saved_stack,
	l32i	a3, sp, 84	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:531:    pitch_index = PLC_PITCH_LAG_MAX-pitch_index;
	sub	a13, a13, a4	# tmp1175, tmp1172, pitch_index
# @OPUS@\upstream\celt\celt_decoder.c:531:    pitch_index = PLC_PITCH_LAG_MAX-pitch_index;
	s32i	a13, sp, 228	# pitch_index, tmp1175
# @OPUS@\upstream\celt\celt_decoder.c:532:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_decoder.c:533:    return pitch_index;
	l32i	a11, sp, 228	# pitch_index,
# @OPUS@\upstream\celt\celt_decoder.c:742:          st->last_pitch_index = pitch_index = celt_plc_pitch_search(decode_mem, C, st->arch);
	l32r	a15, .LC7	#, tmp1961
	l32i	a14, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:533:    return pitch_index;
	s32i	a11, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:742:          st->last_pitch_index = pitch_index = celt_plc_pitch_search(decode_mem, C, st->arch);
	s32i.n	a11, a14, 56	# *st_322(D).last_pitch_index,
	s32i	a15, sp, 340	# %sfp, tmp1961
	j	.L157		#
.L465:
# @OPUS@\upstream\celt\celt_decoder.c:744:          pitch_index = st->last_pitch_index;
	l32i	a8, sp, 244	# %sfp,
	l32r	a9, .LC8	#,
	l32i.n	a8, a8, 56	# *st_322(D).last_pitch_index,
	addi	a10, sp, 80	#,,
	l32r	a15, .LC7	#, tmp1961
	l32r	a12, .LC11	#, tmp1965
	s32i	a8, sp, 260	# %sfp,
	s32i	a9, sp, 340	# %sfp,
	s32i	a10, sp, 308	# %sfp,
	mov.n	a11, a8	#,
.L157:
# @OPUS@\upstream\celt\celt_decoder.c:750:       exc_length = IMIN(2*pitch_index, MAX_PERIOD);
	slli	a11, a11, 1	#,,
	s32i	a11, sp, 348	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:750:       exc_length = IMIN(2*pitch_index, MAX_PERIOD);
	movi	a2, 0x400	# tmp1181,
	mov.n	a13, a11	# exc_length,
	bge	a2, a11, .L158	# tmp1181,,
	mov.n	a13, a2	# exc_length, tmp1181
.L158:
# @OPUS@\upstream\celt\celt_decoder.c:752:       ALLOC(_exc, MAX_PERIOD+CELT_LPC_ORDER, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	movi	a2, 0x418	#,
	call0	yoradio_opus_scratch_alloc		#
	l32i	a9, sp, 300	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:865:          extrapolation_len = N+overlap;
	l32i	a10, sp, 296	# %sfp,
	sub	a12, a12, a9	#, tmp1965,
	add.n	a10, a10, a9	#,,
# @OPUS@\upstream\celt\celt_decoder.c:841:             decay_length = exc_length>>1;
	srai	a14, a13, 1	#, exc_length,
# @OPUS@\upstream\celt\celt_decoder.c:752:       ALLOC(_exc, MAX_PERIOD+CELT_LPC_ORDER, opus_val16);
	s32i	a2, sp, 324	# %sfp,
	s32i	a12, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:839:             int shift = IMAX(0,2*celt_zlog2(celt_maxabs16(&exc[MAX_PERIOD-exc_length], exc_length))-20);
	movi	a5, 0x400	# tmp1187,
# @OPUS@\upstream\celt\celt_decoder.c:865:          extrapolation_len = N+overlap;
	s32i	a10, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:847:                e = exc[MAX_PERIOD-2*decay_length+i];
	movi	a7, 0x200	# tmp1201,
	add.n	a10, a10, a12	# tmp1204,,
	l32i	a12, sp, 300	# %sfp,
	sub	a8, a5, a14	# _2059, tmp1187,
	sub	a9, a7, a14	# tmp1202, tmp1201,
# @OPUS@\upstream\celt\celt_decoder.c:756:       exc = _exc+CELT_LPC_ORDER;
	l32i	a11, sp, 324	# %sfp,
	movi	a7, 0x7ff	# tmp1205,
	add.n	a3, a14, a8	# tmp1194,, _2059
# @OPUS@\upstream\celt\celt_decoder.c:841:             decay_length = exc_length>>1;
	s32i	a14, sp, 304	# %sfp,
	sub	a7, a7, a12	# tmp1206, tmp1205,
	l32i	a14, sp, 296	# %sfp,
	l32i	a12, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:756:       exc = _exc+CELT_LPC_ORDER;
	addi	a11, a11, 48	#,,
	s32i	a11, sp, 264	# %sfp,
	add.n	a11, a14, a12	# tmp1207,,
# @OPUS@\upstream\celt\celt_decoder.c:757:       window = mode->window;
	l32i	a14, sp, 280	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	neg	a2, a13	# tmp1184, exc_length
# @OPUS@\upstream\celt\celt_decoder.c:757:       window = mode->window;
	l32i.n	a14, a14, 52	# mode_537->window,
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	slli	a2, a2, 1	# tmp1185, tmp1184,
# @OPUS@\upstream\celt\celt_decoder.c:757:       window = mode->window;
	s32i	a14, sp, 356	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	l32i	a14, sp, 264	# %sfp,
	addmi	a2, a2, 0x800	# tmp1186, tmp1185,
	add.n	a2, a14, a2	#,, tmp1186
# @OPUS@\upstream\celt\celt_decoder.c:857:          OPUS_MOVE(buf, buf+N, DECODE_BUFFER_SIZE-N);
	l32i	a14, sp, 300	# %sfp,
	slli	a4, a8, 1	# tmp1192, _2059,
	slli	a14, a14, 2	#,,
	s32i	a14, sp, 344	# %sfp,
	l32i	a14, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:839:             int shift = IMAX(0,2*celt_zlog2(celt_maxabs16(&exc[MAX_PERIOD-exc_length], exc_length))-20);
	sub	a6, a5, a13	# tmp1188, tmp1187, exc_length
	slli	a8, a8, 1	# tmp1199, _2059,
	sub	a5, a5, a14	#, tmp1187,
	l32i	a14, sp, 324	# %sfp,
	neg	a8, a8	#, tmp1199
	addi	a4, a4, 48	# tmp1193, tmp1192,
	add.n	a4, a14, a4	#,, tmp1193
	s32i	a8, sp, 384	# %sfp,
	l32i	a14, sp, 264	# %sfp,
	l32i	a8, sp, 316	# %sfp,
	slli	a3, a3, 1	# tmp1195, tmp1194,
	slli	a9, a9, 2	#, tmp1202,
	slli	a6, a6, 1	#, tmp1188,
	add.n	a3, a3, a14	#, tmp1195,
	slli	a8, a8, 2	#,,
	slli	a10, a10, 2	#, tmp1204,
	slli	a7, a7, 2	#, tmp1206,
	s32i	a9, sp, 360	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	s32i	a2, sp, 336	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:839:             int shift = IMAX(0,2*celt_zlog2(celt_maxabs16(&exc[MAX_PERIOD-exc_length], exc_length))-20);
	s32i	a6, sp, 332	# %sfp,
	s32i	a5, sp, 256	# %sfp,
	s32i	a4, sp, 376	# %sfp,
	s32i	a3, sp, 368	# %sfp,
	s32i	a8, sp, 328	# %sfp,
	s32i	a10, sp, 284	# %sfp,
	s32i	a7, sp, 380	# %sfp,
	slli	a11, a11, 2	#, tmp1207,
# @OPUS@\upstream\celt\celt_decoder.c:769:             exc[i-CELT_LPC_ORDER] = SROUND16(buf[DECODE_BUFFER_SIZE-MAX_PERIOD-CELT_LPC_ORDER+i], SIG_SHIFT);
	l32r	a12, .LC9	#, tmp2529
	s32i	a11, sp, 372	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:758:       c=0; do {
	l32i	a9, sp, 268	# %sfp,
	s32i	a9, sp, 280	# %sfp,
.L205:
# @OPUS@\upstream\celt\celt_decoder.c:767:          buf = decode_mem[c];
	l32i	a10, sp, 280	# %sfp,
	l32i	a11, sp, 308	# %sfp,
	slli	a2, a10, 2	# tmp1209,,
	add.n	a2, a11, a2	# tmp1210,, tmp1209
	l32i	a14, a2, 116	# decode_mem, buf
	l32r	a2, .LC12	#,
	l32i	a4, sp, 324	# %sfp, ivtmp$329
	add.n	a3, a14, a2	# ivtmp$327, buf,
	addmi	a6, a14, 0x2000	# _1295, buf,
.L160:
# @OPUS@\upstream\celt\celt_decoder.c:769:             exc[i-CELT_LPC_ORDER] = SROUND16(buf[DECODE_BUFFER_SIZE-MAX_PERIOD-CELT_LPC_ORDER+i], SIG_SHIFT);
	l32i.n	a2, a3, 0	# MEM[base: _1298, offset: 0B], MEM[base: _1298, offset: 0B]
	mov.n	a5, a15	# iftmp$45_1993, tmp1961
	addmi	a2, a2, 0x800	# tmp1213, MEM[base: _1298, offset: 0B],
	srai	a2, a2, 12	# _1995, tmp1213,
	addi.n	a3, a3, 4	# ivtmp$327, ivtmp$327,
	blt	a15, a2, .L159	# tmp1961, _1995,
	slli	a7, a2, 16	# tmp1217, _1995,
	mov.n	a5, a12	# iftmp$45_1993, tmp2529
	blt	a2, a12, .L159	# _1995, tmp2529,
	srai	a5, a7, 16	# iftmp$45_1993, tmp1217,
.L159:
# @OPUS@\upstream\celt\celt_decoder.c:769:             exc[i-CELT_LPC_ORDER] = SROUND16(buf[DECODE_BUFFER_SIZE-MAX_PERIOD-CELT_LPC_ORDER+i], SIG_SHIFT);
	s16i	a5, a4, 0	# MEM[base: _1297, offset: 0B], iftmp$45_1993
	addi.n	a4, a4, 2	# ivtmp$329, ivtmp$329,
# @OPUS@\upstream\celt\celt_decoder.c:768:          for (i=0;i<MAX_PERIOD+CELT_LPC_ORDER;i++)
	bne	a6, a3, .L160	# _1295, ivtmp$327,
	l32i	a8, sp, 280	# %sfp,
	l32i	a9, sp, 248	# %sfp,
	slli	a10, a8, 1	# tmp1984,,
	add.n	a11, a10, a8	# tmp1220, tmp1984,
	slli	a11, a11, 4	# tmp1221, tmp1220,
	add.n	a9, a9, a11	#,, tmp1221
# @OPUS@\upstream\celt\celt_decoder.c:771:          if (loss_duration == 0)
	l32i	a8, sp, 320	# %sfp,
	s32i	a9, sp, 292	# %sfp,
	bnez.n	a8, .L161	#,
# @OPUS@\upstream\celt\celt_decoder.c:776:             _celt_autocorr(exc, ac, window, overlap,
	l32i	a9, sp, 244	# %sfp,
	l32i	a3, sp, 308	# %sfp,
	l32i.n	a2, a9, 40	# *st_322(D).arch, *st_322(D).arch
	l32i	a5, sp, 296	# %sfp,
	s32i.n	a2, sp, 0	#, *st_322(D).arch
	l32i	a4, sp, 356	# %sfp,
	l32i	a2, sp, 264	# %sfp,
	movi	a7, 0x400	#,
	movi.n	a6, 0x18	#,
	s32i	a10, sp, 404	#,
	s32i	a11, sp, 408	#,
	call0	_celt_autocorr		#
# @OPUS@\upstream\celt\celt_decoder.c:780:             ac[0] += SHR32(ac[0],13);
	l32i	a3, sp, 80	# ac, _669
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	l32i	a11, sp, 408	#,
# @OPUS@\upstream\celt\celt_decoder.c:780:             ac[0] += SHR32(ac[0],13);
	srai	a2, a3, 13	# tmp1223, _669,
# @OPUS@\upstream\celt\celt_decoder.c:780:             ac[0] += SHR32(ac[0],13);
	add.n	a2, a2, a3	# tmp1224, tmp1223, _669
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	l32i	a10, sp, 404	#,
	addi	a7, sp, 84	# ivtmp$317,,
# @OPUS@\upstream\celt\celt_decoder.c:780:             ac[0] += SHR32(ac[0],13);
	s32i	a2, sp, 80	# ac, tmp1224
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	movi.n	a6, 1	# i,
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	movi.n	a8, 0x19	# tmp1238,
.L162:
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	mul16s	a3, a6, a6	# tmp1226, i, i
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	l32i.n	a2, a7, 0	# MEM[base: _1320, offset: 0B], _673
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	slli	a3, a3, 17	# tmp1229, tmp1226,
	extui	a4, a2, 0, 16	# tmp1230, _673,
	srai	a3, a3, 16	# _677, tmp1229,
	mull	a5, a4, a3	# tmp1231, tmp1230, _677
	srai	a4, a2, 16	# tmp1234, _673,
	mull	a3, a4, a3	# tmp1235, tmp1234, _677
	srai	a4, a5, 15	# tmp1232, tmp1231,
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a2, a2, a4	# tmp1233, _673, tmp1232
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	slli	a3, a3, 1	# tmp1236, tmp1235,
# @OPUS@\upstream\celt\celt_decoder.c:789:                ac[i] -= MULT16_32_Q15(2*i*i, ac[i]);
	sub	a2, a2, a3	# tmp1237, tmp1233, tmp1236
	s32i.n	a2, a7, 0	# MEM[base: _1320, offset: 0B], tmp1237
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	addi.n	a6, a6, 1	# i, i,
	addi.n	a7, a7, 4	# ivtmp$317, ivtmp$317,
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	bne	a6, a8, .L162	# i, tmp1238,
# @OPUS@\upstream\celt\celt_decoder.c:794:             _celt_lpc(lpc+c*CELT_LPC_ORDER, ac, CELT_LPC_ORDER);
	l32i	a2, sp, 292	# %sfp,
	l32i	a3, sp, 308	# %sfp,
	movi.n	a4, 0x18	#,
	s32i	a10, sp, 404	#,
	s32i	a11, sp, 408	#,
	call0	_celt_lpc		#
# @OPUS@\upstream\celt\celt_decoder.c:803:                sum += ABS16(lpc[c*CELT_LPC_ORDER+i]);
	l32i	a10, sp, 404	#,
	l32i	a8, sp, 280	# %sfp,
	l32i	a9, sp, 244	# %sfp,
	add.n	a5, a10, a8	# tmp1241, tmp1984,
	slli	a5, a5, 4	# tmp1243, tmp1241,
	movi	a2, 0x94	# tmp1245,
	l32i	a11, sp, 408	#,
	addi	a5, a5, 100	# tmp1244, tmp1243,
	add.n	a2, a9, a2	# tmp1246,, tmp1245
	l32r	a7, .LC10	#, sum
	l32r	a10, .LC13	#, tmp1967
# @OPUS@\upstream\celt\celt_decoder.c:807:                tmp = MULT16_16_Q15(QCONST16(.99f,15), tmp);
	l32r	a4, .LC14	#, tmp2527
	add.n	a5, a9, a5	# ivtmp$309,, tmp1244
	add.n	a11, a2, a11	# _1343, tmp1246, tmp1221
.L166:
# @OPUS@\upstream\celt\celt_decoder.c:785:             for (i=1;i<=CELT_LPC_ORDER;i++)
	mov.n	a2, a5	# ivtmp$309, ivtmp$309
# @OPUS@\upstream\celt\celt_decoder.c:801:             opus_val32 sum=QCONST16(1., SIG_SHIFT);
	mov.n	a6, a7	# sum, sum
.L163:
# @OPUS@\upstream\celt\celt_decoder.c:803:                sum += ABS16(lpc[c*CELT_LPC_ORDER+i]);
	l16si	a3, a2, 0	# MEM[base: _1378, offset: 0B], tmp1247
	addi.n	a2, a2, 2	# ivtmp$309, ivtmp$309,
	abs	a3, a3	# tmp1250, tmp1247
# @OPUS@\upstream\celt\celt_decoder.c:803:                sum += ABS16(lpc[c*CELT_LPC_ORDER+i]);
	add.n	a6, a6, a3	# sum, sum, tmp1250
# @OPUS@\upstream\celt\celt_decoder.c:802:             for (i=0;i<CELT_LPC_ORDER;i++)
	bne	a11, a2, .L163	# _1343, ivtmp$309,
# @OPUS@\upstream\celt\celt_decoder.c:804:             if (sum < 65535) break;
	bge	a10, a6, .L161	# tmp1967, sum,
	mov.n	a3, a5	# ivtmp$302, ivtmp$309
# @OPUS@\upstream\celt\celt_decoder.c:800:             opus_val16 tmp=Q15ONE;
	mov.n	a2, a15	# tmp, tmp1961
.L165:
# @OPUS@\upstream\celt\celt_decoder.c:807:                tmp = MULT16_16_Q15(QCONST16(.99f,15), tmp);
	mul16s	a2, a2, a4	# tmp1252, tmp, tmp1253
# @OPUS@\upstream\celt\celt_decoder.c:808:                lpc[c*CELT_LPC_ORDER+i] = MULT16_16_Q15(lpc[c*CELT_LPC_ORDER+i], tmp);
	l16si	a6, a3, 0	# MEM[base: _1392, offset: 0B], tmp1255
# @OPUS@\upstream\celt\celt_decoder.c:807:                tmp = MULT16_16_Q15(QCONST16(.99f,15), tmp);
	srai	a2, a2, 15	# _710, tmp1252,
# @OPUS@\upstream\celt\celt_decoder.c:808:                lpc[c*CELT_LPC_ORDER+i] = MULT16_16_Q15(lpc[c*CELT_LPC_ORDER+i], tmp);
	mull	a6, a6, a2	# tmp1258, tmp1255, _710
# @OPUS@\upstream\celt\celt_decoder.c:807:                tmp = MULT16_16_Q15(QCONST16(.99f,15), tmp);
	slli	a2, a2, 16	# tmp1254, _710,
# @OPUS@\upstream\celt\celt_decoder.c:808:                lpc[c*CELT_LPC_ORDER+i] = MULT16_16_Q15(lpc[c*CELT_LPC_ORDER+i], tmp);
	srai	a6, a6, 15	# tmp1259, tmp1258,
# @OPUS@\upstream\celt\celt_decoder.c:808:                lpc[c*CELT_LPC_ORDER+i] = MULT16_16_Q15(lpc[c*CELT_LPC_ORDER+i], tmp);
	s16i	a6, a3, 0	# MEM[base: _1392, offset: 0B], tmp1259
	addi.n	a3, a3, 2	# ivtmp$302, ivtmp$302,
# @OPUS@\upstream\celt\celt_decoder.c:807:                tmp = MULT16_16_Q15(QCONST16(.99f,15), tmp);
	srai	a2, a2, 16	# tmp, tmp1254,
# @OPUS@\upstream\celt\celt_decoder.c:805:             for (i=0;i<CELT_LPC_ORDER;i++)
	bne	a11, a3, .L165	# _1343, ivtmp$302,
	j	.L166		#
.L161:
# @OPUS@\upstream\celt\celt_decoder.c:819:             SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 80	# _saved_stack,
	s32i	a3, sp, 84	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:820:             ALLOC(fir_tmp, exc_length, opus_val16);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a13	#, exc_length
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:820:             ALLOC(fir_tmp, exc_length, opus_val16);
	mov.n	a8, a2	# fir_tmp,
# @OPUS@\upstream\celt\celt_decoder.c:824:             celt_fir(exc+MAX_PERIOD-exc_length, lpc+c*CELT_LPC_ORDER,
	l32i.n	a7, a10, 40	# *st_322(D).arch,
	mov.n	a4, a2	#, fir_tmp
	l32i	a3, sp, 292	# %sfp,
	l32i	a2, sp, 336	# %sfp,
	movi.n	a6, 0x18	#,
	mov.n	a5, a13	#, exc_length
	s32i	a8, sp, 404	#,
	call0	celt_fir_c		#
# @OPUS@\upstream\celt\celt_decoder.c:826:             OPUS_COPY(exc+MAX_PERIOD-exc_length, fir_tmp, exc_length);
	l32i	a8, sp, 404	#,
	l32i	a2, sp, 336	# %sfp,
	mov.n	a3, a8	#, fir_tmp
	movi.n	a5, 2	#,
	mov.n	a4, a13	#, exc_length
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:828:             RESTORE_STACK;
	l32i	a2, sp, 80	# _saved_stack,
	l32i	a3, sp, 84	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	l32i	a11, sp, 348	# %sfp,
	blti	a11, 1, .L344	#,,
	l32i	a9, sp, 264	# %sfp,
	l32i	a10, sp, 332	# %sfp,
# @OPUS@\upstream\celt\mathops.h:84:    opus_val16 minval = 0;
	movi.n	a3, 0	# minval,
	add.n	a8, a9, a10	# ivtmp$291,,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	l32i	a6, sp, 268	# %sfp, i
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	mov.n	a7, a8	# ivtmp$295, ivtmp$291
# @OPUS@\upstream\celt\mathops.h:83:    opus_val16 maxval = 0;
	mov.n	a4, a3	# maxval, minval
.L170:
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	l16si	a2, a7, 0	# MEM[base: _1400, offset: 0B], _742
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	slli	a9, a2, 16	# tmp1985, _742,
	mov.n	a5, a2	# _742, _742
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	srai	a9, a9, 16	# tmp1272, tmp1985,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	bge	a2, a4, .L168	# _742, maxval,
	mov.n	a5, a4	# _742, maxval
.L168:
	slli	a5, a5, 16	# tmp1269, _742,
	srai	a4, a5, 16	# maxval, tmp1269,
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	bge	a3, a9, .L169	# minval, tmp1272,
	mov.n	a2, a3	# _742, minval
.L169:
	slli	a2, a2, 16	# tmp1276, _742,
	srai	a3, a2, 16	# minval, tmp1276,
	addi.n	a7, a7, 2	# ivtmp$295, ivtmp$295,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	blt	a6, a13, .L170	# i, exc_length,
# @OPUS@\upstream\celt\mathops.h:90:    return MAX32(EXTEND32(maxval),-EXTEND32(minval));
	neg	a5, a3	# _753, minval
	bge	a5, a4, .L171	# _753, maxval,
	mov.n	a5, a4	# _753, maxval
.L171:
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	beqz.n	a5, .L167	# _753,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a5	# _755, _753
# @OPUS@\upstream\celt\celt_decoder.c:839:             int shift = IMAX(0,2*celt_zlog2(celt_maxabs16(&exc[MAX_PERIOD-exc_length], exc_length))-20);
	movi.n	a2, 0x15	# tmp1281,
	sub	a2, a2, a3	# tmp1283, tmp1281, _755
	l32i	a5, sp, 268	# %sfp, _753
	bltz	a2, .L167	# tmp1283,
# @OPUS@\upstream\celt\mathops.h:84:    opus_val16 minval = 0;
	movi.n	a2, 0	# minval,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	mov.n	a6, a5	# i, _753
# @OPUS@\upstream\celt\mathops.h:83:    opus_val16 maxval = 0;
	mov.n	a3, a2	# maxval, minval
.L174:
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	l16si	a7, a8, 0	# MEM[base: _1407, offset: 0B], _767
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	slli	a4, a7, 16	# tmp1986, _767,
	srai	a9, a4, 16	# tmp1291, tmp1986,
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	mov.n	a4, a9	# tmp1298, tmp1291
# @OPUS@\upstream\celt\mathops.h:87:       maxval = MAX16(maxval, x[i]);
	mov.n	a5, a3	# maxval, maxval
	bge	a3, a9, .L172	# maxval, tmp1291,
	mov.n	a5, a7	# maxval, _767
.L172:
	slli	a3, a5, 16	# tmp1293, maxval,
	srai	a3, a3, 16	# maxval, tmp1293,
# @OPUS@\upstream\celt\mathops.h:88:       minval = MIN16(minval, x[i]);
	mov.n	a5, a2	# minval, minval
	bge	a4, a2, .L173	# tmp1298, minval,
	mov.n	a5, a7	# minval, _767
.L173:
	slli	a5, a5, 16	# tmp1300, minval,
	srai	a2, a5, 16	# minval, tmp1300,
	addi.n	a8, a8, 2	# ivtmp$291, ivtmp$291,
# @OPUS@\upstream\celt\mathops.h:85:    for (i=0;i<len;i++)
	blt	a6, a13, .L174	# i, exc_length,
# @OPUS@\upstream\celt\mathops.h:90:    return MAX32(EXTEND32(maxval),-EXTEND32(minval));
	neg	a2, a2	# _778, minval
	bge	a2, a3, .L175	# _778, maxval,
	mov.n	a2, a3	# _778, maxval
.L175:
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	movi.n	a5, -0x14	# _753,
	beqz.n	a2, .L167	# _778,
	movi.n	a5, 0x15	# tmp1305,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a2, a2	# _780, _778
	sub	a2, a5, a2	# tmp1307, tmp1305, _780
	slli	a5, a2, 1	# _753, tmp1307,
	j	.L167		#
.L344:
# @OPUS@\upstream\celt\celt_decoder.c:839:             int shift = IMAX(0,2*celt_zlog2(celt_maxabs16(&exc[MAX_PERIOD-exc_length], exc_length))-20);
	l32i	a5, sp, 268	# %sfp, _753
.L167:
# @OPUS@\upstream\celt\celt_decoder.c:842:             for (i=0;i<decay_length;i++)
	l32i	a11, sp, 304	# %sfp,
	blti	a11, 1, .L347	#,,
# @OPUS@\upstream\celt\celt_decoder.c:836:             opus_val32 E1=1, E2=1;
	movi.n	a3, 1	# E2,
# @OPUS@\upstream\celt\celt_decoder.c:842:             for (i=0;i<decay_length;i++)
	l32i	a4, sp, 376	# %sfp, ivtmp$284
# @OPUS@\upstream\celt\celt_decoder.c:836:             opus_val32 E1=1, E2=1;
	l32i	a7, sp, 360	# %sfp, _1893
	l32i	a8, sp, 368	# %sfp, _1901
	l32i	a9, sp, 384	# %sfp, tmp1200
	mov.n	a6, a3	# E1, E2
.L178:
# @OPUS@\upstream\celt\celt_decoder.c:847:                e = exc[MAX_PERIOD-2*decay_length+i];
	add.n	a2, a9, a4	# tmp1312, tmp1200, ivtmp$284
	add.n	a2, a2, a7	# tmp1313, tmp1312, _1893
# @OPUS@\upstream\celt\celt_decoder.c:845:                e = exc[MAX_PERIOD-decay_length+i];
	l16si	a10, a4, 0	# MEM[base: _482, offset: 0B], e
# @OPUS@\upstream\celt\celt_decoder.c:847:                e = exc[MAX_PERIOD-2*decay_length+i];
	l16si	a2, a2, 0	# MEM[base: _1894, offset: 0B], e
# @OPUS@\upstream\celt\celt_decoder.c:846:                E1 += SHR32(MULT16_16(e, e), shift);
	mull	a10, a10, a10	# tmp1310, e, e
# @OPUS@\upstream\celt\celt_decoder.c:848:                E2 += SHR32(MULT16_16(e, e), shift);
	mull	a2, a2, a2	# tmp1316, e, e
# @OPUS@\upstream\celt\celt_decoder.c:846:                E1 += SHR32(MULT16_16(e, e), shift);
	ssr	a5	# _753
	sra	a10, a10	# tmp1311, tmp1310
# @OPUS@\upstream\celt\celt_decoder.c:848:                E2 += SHR32(MULT16_16(e, e), shift);
	ssr	a5	# _753
	sra	a2, a2	# tmp1317, tmp1316
	addi.n	a4, a4, 2	# ivtmp$284, ivtmp$284,
# @OPUS@\upstream\celt\celt_decoder.c:846:                E1 += SHR32(MULT16_16(e, e), shift);
	add.n	a6, a6, a10	# E1, E1, tmp1311
# @OPUS@\upstream\celt\celt_decoder.c:848:                E2 += SHR32(MULT16_16(e, e), shift);
	add.n	a3, a3, a2	# E2, E2, tmp1317
# @OPUS@\upstream\celt\celt_decoder.c:842:             for (i=0;i<decay_length;i++)
	bne	a4, a8, .L178	# ivtmp$284, _1901,
	bge	a3, a6, .L179	# E2, E1,
	mov.n	a6, a3	# E1, E2
.L179:
	srai	a2, a6, 1	# _2081, E1,
	j	.L177		#
.L347:
	l32i	a2, sp, 268	# %sfp, _2081
# @OPUS@\upstream\celt\celt_decoder.c:836:             opus_val32 E1=1, E2=1;
	movi.n	a3, 1	# E2,
.L177:
# @OPUS@\upstream\celt\celt_decoder.c:851:             decay = celt_sqrt(frac_div32(SHR32(E1, 1), E2));
	call0	frac_div32		#
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\celt_decoder.c:857:          OPUS_MOVE(buf, buf+N, DECODE_BUFFER_SIZE-N);
	l32i	a8, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:851:             decay = celt_sqrt(frac_div32(SHR32(E1, 1), E2));
	slli	a2, a2, 16	# tmp1319,,
	srai	a2, a2, 16	#, tmp1319,
# @OPUS@\upstream\celt\celt_decoder.c:857:          OPUS_MOVE(buf, buf+N, DECODE_BUFFER_SIZE-N);
	l32i	a4, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:851:             decay = celt_sqrt(frac_div32(SHR32(E1, 1), E2));
	s32i	a2, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:857:          OPUS_MOVE(buf, buf+N, DECODE_BUFFER_SIZE-N);
	movi.n	a5, 4	#,
	add.n	a3, a14, a8	#, buf,
	mov.n	a2, a14	#, buf
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:867:          attenuation = MULT16_16_Q15(fade, decay);
	l32i	a9, sp, 252	# %sfp,
	l32i	a10, sp, 340	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	l32i	a11, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:867:          attenuation = MULT16_16_Q15(fade, decay);
	mull	a7, a9, a10	# tmp1321,,
# @OPUS@\upstream\celt\celt_decoder.c:867:          attenuation = MULT16_16_Q15(fade, decay);
	srai	a7, a7, 15	# attenuation, tmp1321,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	blti	a11, 1, .L348	#,,
	l32i	a8, sp, 256	# %sfp,
	l32i	a9, sp, 300	# %sfp,
	l32i	a11, sp, 328	# %sfp,
	sub	a2, a8, a9	# tmp1325,,
	l32i	a8, sp, 284	# %sfp,
	l32r	a10, .LC13	#, tmp1967
	add.n	a9, a14, a8	# _664, buf,
# @OPUS@\upstream\celt\celt_decoder.c:761:          opus_val32 S1=0;
	l32i	a8, sp, 268	# %sfp, S1
	addmi	a6, a2, 0x400	# _2084, tmp1325,
	add.n	a5, a14, a11	# ivtmp$281, buf,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	mov.n	a4, a8	# j, S1
.L185:
# @OPUS@\upstream\celt\celt_decoder.c:873:                attenuation = MULT16_16_Q15(attenuation, decay);
	l32i	a11, sp, 252	# %sfp,
	mov.n	a2, a7	# prephitmp_2090, attenuation
	mull	a3, a11, a7	# tmp1326,, attenuation
# @OPUS@\upstream\celt\celt_decoder.c:871:             if (j >= pitch_index) {
	l32i	a11, sp, 260	# %sfp,
	blt	a4, a11, .L181	# j,,
# @OPUS@\upstream\celt\celt_decoder.c:873:                attenuation = MULT16_16_Q15(attenuation, decay);
	srai	a2, a3, 15	# prephitmp_2090, tmp1326,
# @OPUS@\upstream\celt\celt_decoder.c:873:                attenuation = MULT16_16_Q15(attenuation, decay);
	slli	a7, a2, 16	# tmp1327, prephitmp_2090,
# @OPUS@\upstream\celt\celt_decoder.c:872:                j -= pitch_index;
	sub	a4, a4, a11	# j, j,
# @OPUS@\upstream\celt\celt_decoder.c:873:                attenuation = MULT16_16_Q15(attenuation, decay);
	srai	a7, a7, 16	# attenuation, tmp1327,
.L181:
# @OPUS@\upstream\celt\celt_decoder.c:876:                   SHL32(EXTEND32(MULT16_16_Q15(attenuation,
	l32i	a11, sp, 256	# %sfp,
	add.n	a3, a11, a4	# tmp1328,, j
	l32i	a11, sp, 264	# %sfp,
	slli	a3, a3, 1	# tmp1329, tmp1328,
	add.n	a3, a11, a3	# tmp1330,, tmp1329
	l16si	a11, a3, 0	# *_2077, tmp1331
# @OPUS@\upstream\celt\celt_decoder.c:880:             tmp = SROUND16(
	add.n	a3, a6, a4	# tmp1337, _2084, j
# @OPUS@\upstream\celt\celt_decoder.c:876:                   SHL32(EXTEND32(MULT16_16_Q15(attenuation,
	mull	a2, a11, a2	# tmp1334, tmp1331, prephitmp_2090
# @OPUS@\upstream\celt\celt_decoder.c:880:             tmp = SROUND16(
	slli	a3, a3, 2	# tmp1338, tmp1337,
# @OPUS@\upstream\celt\celt_decoder.c:876:                   SHL32(EXTEND32(MULT16_16_Q15(attenuation,
	srai	a2, a2, 15	# tmp1335, tmp1334,
	slli	a2, a2, 12	# tmp1336, tmp1335,
# @OPUS@\upstream\celt\celt_decoder.c:875:             buf[DECODE_BUFFER_SIZE-N+i] =
	s32i.n	a2, a5, 0	# MEM[base: _665, offset: 0B], tmp1336
# @OPUS@\upstream\celt\celt_decoder.c:880:             tmp = SROUND16(
	add.n	a3, a14, a3	# tmp1339, buf, tmp1338
	l32i.n	a2, a3, 0	# *_2057, *_2057
	addi.n	a5, a5, 4	# ivtmp$281, ivtmp$281,
	addmi	a2, a2, 0x800	# tmp1340, *_2057,
	srai	a2, a2, 12	# _2054, tmp1340,
# @OPUS@\upstream\celt\celt_decoder.c:883:             S1 += SHR32(MULT16_16(tmp, tmp), 10);
	mul16s	a3, a2, a2	# tmp1346, _2054, _2054
# @OPUS@\upstream\celt\celt_decoder.c:880:             tmp = SROUND16(
	add.n	a2, a2, a15	# tmp1342, _2054, tmp1961
# @OPUS@\upstream\celt\celt_decoder.c:883:             S1 += SHR32(MULT16_16(tmp, tmp), 10);
	srai	a3, a3, 10	# tmp1347, tmp1346,
# @OPUS@\upstream\celt\celt_decoder.c:880:             tmp = SROUND16(
	bltu	a10, a2, .L182	# tmp1967, tmp1342,
# @OPUS@\upstream\celt\celt_decoder.c:883:             S1 += SHR32(MULT16_16(tmp, tmp), 10);
	add.n	a8, a8, a3	# S1, S1, tmp1347
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	bne	a9, a5, .L185	# _664, ivtmp$281,
	j	.L180		#
.L182:
# @OPUS@\upstream\celt\celt_decoder.c:883:             S1 += SHR32(MULT16_16(tmp, tmp), 10);
	l32r	a2, .LC15	#,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\celt_decoder.c:883:             S1 += SHR32(MULT16_16(tmp, tmp), 10);
	add.n	a8, a8, a2	# S1, S1,
# @OPUS@\upstream\celt\celt_decoder.c:868:          for (i=j=0;i<extrapolation_len;i++,j++)
	bne	a5, a9, .L185	# ivtmp$281, _664,
	j	.L180		#
.L348:
# @OPUS@\upstream\celt\celt_decoder.c:761:          opus_val32 S1=0;
	l32i	a8, sp, 268	# %sfp, S1
.L180:
	l32i	a9, sp, 380	# %sfp,
	l32i	a3, sp, 308	# %sfp, ivtmp$278
# @OPUS@\upstream\celt\celt_decoder.c:890:                lpc_mem[i] = SROUND16(buf[DECODE_BUFFER_SIZE-N-1-i], SIG_SHIFT);
	l32r	a7, .LC9	#, tmp2522
	add.n	a4, a14, a9	# ivtmp$277, buf,
	addi	a6, a3, 48	# _659, ivtmp$278,
.L187:
	l32i.n	a2, a4, 0	# MEM[base: _656, offset: 0B], MEM[base: _656, offset: 0B]
	mov.n	a5, a15	# iftmp$56_2115, tmp1961
	addmi	a2, a2, 0x800	# tmp1349, MEM[base: _656, offset: 0B],
	srai	a2, a2, 12	# _2129, tmp1349,
	blt	a15, a2, .L186	# tmp1961, _2129,
	slli	a9, a2, 16	# tmp1353, _2129,
	mov.n	a5, a7	# iftmp$56_2115, tmp2522
	blt	a2, a7, .L186	# _2129, tmp2522,
	srai	a5, a9, 16	# iftmp$56_2115, tmp1353,
.L186:
# @OPUS@\upstream\celt\celt_decoder.c:890:                lpc_mem[i] = SROUND16(buf[DECODE_BUFFER_SIZE-N-1-i], SIG_SHIFT);
	s16i	a5, a3, 0	# MEM[base: _657, offset: 0B], iftmp$56_2115
	addi.n	a3, a3, 2	# ivtmp$278, ivtmp$278,
	addi	a4, a4, -4	# ivtmp$277, ivtmp$277,
# @OPUS@\upstream\celt\celt_decoder.c:889:             for (i=0;i<CELT_LPC_ORDER;i++)
	bne	a3, a6, .L187	# ivtmp$278, _659,
# @OPUS@\upstream\celt\celt_decoder.c:893:             celt_iir(buf+DECODE_BUFFER_SIZE-N, lpc+c*CELT_LPC_ORDER,
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:893:             celt_iir(buf+DECODE_BUFFER_SIZE-N, lpc+c*CELT_LPC_ORDER,
	l32i	a9, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:893:             celt_iir(buf+DECODE_BUFFER_SIZE-N, lpc+c*CELT_LPC_ORDER,
	l32i.n	a2, a10, 40	# *st_322(D).arch, *st_322(D).arch
# @OPUS@\upstream\celt\celt_decoder.c:893:             celt_iir(buf+DECODE_BUFFER_SIZE-N, lpc+c*CELT_LPC_ORDER,
	add.n	a11, a14, a9	# _891, buf,
# @OPUS@\upstream\celt\celt_decoder.c:893:             celt_iir(buf+DECODE_BUFFER_SIZE-N, lpc+c*CELT_LPC_ORDER,
	l32i	a7, sp, 308	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a3, sp, 292	# %sfp,
	s32i.n	a2, sp, 0	#, *st_322(D).arch
	mov.n	a4, a11	#, _891
	mov.n	a2, a11	#, _891
	movi.n	a6, 0x18	#,
	s32i	a8, sp, 404	#,
	s32i	a11, sp, 408	#,
	call0	celt_iir		#
# @OPUS@\upstream\celt\celt_decoder.c:897:             for (i=0; i < extrapolation_len; i++)
	l32i	a10, sp, 276	# %sfp,
	l32i	a8, sp, 404	#,
	l32i	a11, sp, 408	#,
	blti	a10, 1, .L188	#,,
	l32i	a9, sp, 328	# %sfp,
	l32i	a10, sp, 284	# %sfp,
	add.n	a4, a14, a9	# ivtmp$268, buf,
	l32r	a7, .LC16	#, tmp1968
	l32r	a5, .LC17	#, tmp1969
	add.n	a6, a14, a10	# _2105, buf,
	mov.n	a3, a4	# ivtmp$271, ivtmp$268
.L191:
# @OPUS@\upstream\celt\celt_decoder.c:898:                buf[DECODE_BUFFER_SIZE-N+i] = SATURATE(buf[DECODE_BUFFER_SIZE-N+i], SIG_SAT);
	l32i.n	a2, a3, 0	# MEM[base: _867, offset: 0B], MEM[base: _867, offset: 0B]
	bge	a2, a7, .L189	# MEM[base: _867, offset: 0B], tmp1968,
	mov.n	a2, a7	# MEM[base: _867, offset: 0B], tmp1968
.L189:
# @OPUS@\upstream\celt\celt_decoder.c:898:                buf[DECODE_BUFFER_SIZE-N+i] = SATURATE(buf[DECODE_BUFFER_SIZE-N+i], SIG_SAT);
	bge	a5, a2, .L190	# tmp1969, MEM[base: _867, offset: 0B],
	mov.n	a2, a5	# MEM[base: _867, offset: 0B], tmp1969
.L190:
	s32i.n	a2, a3, 0	# MEM[base: _867, offset: 0B], MEM[base: _867, offset: 0B]
	addi.n	a3, a3, 4	# ivtmp$271, ivtmp$271,
# @OPUS@\upstream\celt\celt_decoder.c:897:             for (i=0; i < extrapolation_len; i++)
	bne	a3, a6, .L191	# ivtmp$271, _2105,
	j	.L468		#
.L328:
# @OPUS@\upstream\celt\celt_decoder.c:909:                opus_val16 tmp = SROUND16(buf[DECODE_BUFFER_SIZE-N+i], SIG_SHIFT);
	l32i.n	a2, a4, 0	# MEM[base: _851, offset: 0B], MEM[base: _851, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$268, ivtmp$268,
	addmi	a2, a2, 0x800	# tmp1371, MEM[base: _851, offset: 0B],
	srai	a2, a2, 12	# _2168, tmp1371,
# @OPUS@\upstream\celt\celt_decoder.c:910:                S2 += SHR32(MULT16_16(tmp, tmp), 10);
	mul16s	a5, a2, a2	# tmp1377, _2168, _2168
# @OPUS@\upstream\celt\celt_decoder.c:909:                opus_val16 tmp = SROUND16(buf[DECODE_BUFFER_SIZE-N+i], SIG_SHIFT);
	add.n	a2, a2, a15	# tmp1373, _2168, tmp1961
# @OPUS@\upstream\celt\celt_decoder.c:910:                S2 += SHR32(MULT16_16(tmp, tmp), 10);
	srai	a5, a5, 10	# tmp1378, tmp1377,
# @OPUS@\upstream\celt\celt_decoder.c:909:                opus_val16 tmp = SROUND16(buf[DECODE_BUFFER_SIZE-N+i], SIG_SHIFT);
	bltu	a10, a2, .L193	# tmp1967, tmp1373,
# @OPUS@\upstream\celt\celt_decoder.c:910:                S2 += SHR32(MULT16_16(tmp, tmp), 10);
	add.n	a3, a3, a5	# S2, S2, tmp1378
# @OPUS@\upstream\celt\celt_decoder.c:907:             for (i=0;i<extrapolation_len;i++)
	bne	a4, a6, .L328	# ivtmp$268, _2105,
	j	.L195		#
.L193:
# @OPUS@\upstream\celt\celt_decoder.c:910:                S2 += SHR32(MULT16_16(tmp, tmp), 10);
	add.n	a3, a3, a7	# S2, S2, tmp2518
# @OPUS@\upstream\celt\celt_decoder.c:907:             for (i=0;i<extrapolation_len;i++)
	bne	a4, a6, .L328	# ivtmp$268, _2105,
.L195:
	srai	a2, a3, 2	# _2150, S2,
.L327:
# @OPUS@\upstream\celt\celt_decoder.c:914:             if (!(S1 > SHR32(S2,2)))
	blt	a2, a8, .L196	# _2150, S1,
# @OPUS@\upstream\celt\celt_decoder.c:923:                OPUS_CLEAR(buf+DECODE_BUFFER_SIZE-N, extrapolation_len);
	l32i	a3, sp, 276	# %sfp,
	movi.n	a4, 4	#,
	mov.n	a2, a11	#, _891
	call0	yoradio_opus_clear		#
	j	.L197		#
.L196:
# @OPUS@\upstream\celt\celt_decoder.c:928:             } else if (S1 < S2)
	bge	a8, a3, .L197	# S1, S2,
# @OPUS@\upstream\celt\celt_decoder.c:930:                opus_val16 ratio = celt_sqrt(frac_div32(SHR32(S1,1)+1,S2+1));
	srai	a2, a8, 1	# tmp1381, S1,
# @OPUS@\upstream\celt\celt_decoder.c:930:                opus_val16 ratio = celt_sqrt(frac_div32(SHR32(S1,1)+1,S2+1));
	addi.n	a3, a3, 1	#, S2,
	addi.n	a2, a2, 1	#, tmp1381,
	call0	frac_div32		#
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\celt_decoder.c:931:                for (i=0;i<overlap;i++)
	l32i	a11, sp, 296	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:930:                opus_val16 ratio = celt_sqrt(frac_div32(SHR32(S1,1)+1,S2+1));
	slli	a2, a2, 16	# tmp1383,,
	srai	a5, a2, 16	# ratio, tmp1383,
# @OPUS@\upstream\celt\celt_decoder.c:931:                for (i=0;i<overlap;i++)
	bgei	a11, 1, .L199	#,,
.L203:
	l32i	a8, sp, 372	# %sfp,
	l32i	a9, sp, 284	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:938:                for (i=overlap;i<extrapolation_len;i++)
	l32i	a10, sp, 296	# %sfp,
	l32i	a11, sp, 276	# %sfp,
	add.n	a3, a14, a8	# ivtmp$261, buf,
	add.n	a14, a14, a9	# _1110, buf,
	blt	a10, a11, .L204	#,,
	j	.L197		#
.L199:
	sub	a7, a15, a5	# tmp1384, tmp1961, ratio
	l32i	a9, sp, 328	# %sfp,
	l32i	a11, sp, 372	# %sfp,
	slli	a7, a7, 16	# tmp1386, tmp1384,
	l32i	a8, sp, 356	# %sfp, ivtmp$264
	srai	a7, a7, 16	# _2155, tmp1386,
	add.n	a6, a14, a9	# ivtmp$265, buf,
	add.n	a10, a14, a11	# _844, buf,
.L202:
# @OPUS@\upstream\celt\celt_decoder.c:934:                         - MULT16_16_Q15(window[i], Q15ONE-ratio);
	l16ui	a2, a8, 0	# MEM[base: _837, offset: 0B],
# @OPUS@\upstream\celt\celt_decoder.c:936:                         MULT16_32_Q15(tmp_g, buf[DECODE_BUFFER_SIZE-N+i]);
	l32i.n	a3, a6, 0	# MEM[base: _838, offset: 0B], _948
# @OPUS@\upstream\celt\celt_decoder.c:934:                         - MULT16_16_Q15(window[i], Q15ONE-ratio);
	mul16s	a2, a2, a7	# tmp1387, MEM[base: _837, offset: 0B], _2155
# @OPUS@\upstream\celt\celt_decoder.c:936:                         MULT16_32_Q15(tmp_g, buf[DECODE_BUFFER_SIZE-N+i]);
	srai	a4, a3, 16	# tmp1394, _948,
# @OPUS@\upstream\celt\celt_decoder.c:934:                         - MULT16_16_Q15(window[i], Q15ONE-ratio);
	srai	a2, a2, 15	# tmp1389, tmp1387,
# @OPUS@\upstream\celt\celt_decoder.c:933:                   opus_val16 tmp_g = Q15ONE
	sub	a2, a15, a2	# tmp1391, tmp1961, tmp1389
# @OPUS@\upstream\celt\celt_decoder.c:936:                         MULT16_32_Q15(tmp_g, buf[DECODE_BUFFER_SIZE-N+i]);
	slli	a2, a2, 16	# tmp1393, tmp1391,
	srai	a2, a2, 16	# _942, tmp1393,
	extui	a3, a3, 0, 16	# tmp1397, _948,
	mull	a4, a4, a2	# tmp1395, tmp1394, _942
	mull	a2, a3, a2	# tmp1398, tmp1397, _942
	slli	a3, a4, 1	# tmp1396, tmp1395,
	srai	a2, a2, 15	# tmp1399, tmp1398,
	add.n	a2, a3, a2	# tmp1400, tmp1396, tmp1399
# @OPUS@\upstream\celt\celt_decoder.c:935:                   buf[DECODE_BUFFER_SIZE-N+i] =
	s32i.n	a2, a6, 0	# MEM[base: _838, offset: 0B], tmp1400
	addi.n	a6, a6, 4	# ivtmp$265, ivtmp$265,
	addi.n	a8, a8, 2	# ivtmp$264, ivtmp$264,
# @OPUS@\upstream\celt\celt_decoder.c:931:                for (i=0;i<overlap;i++)
	bne	a10, a6, .L202	# _844, ivtmp$265,
	j	.L203		#
.L204:
# @OPUS@\upstream\celt\celt_decoder.c:941:                         MULT16_32_Q15(ratio, buf[DECODE_BUFFER_SIZE-N+i]);
	l32i.n	a2, a3, 0	# MEM[base: _2160, offset: 0B], _968
	srai	a4, a2, 16	# tmp1401, _968,
	extui	a2, a2, 0, 16	# tmp1404, _968,
	mull	a4, a4, a5	# tmp1402, tmp1401, ratio
	mull	a2, a2, a5	# tmp1405, tmp1404, ratio
	slli	a4, a4, 1	# tmp1403, tmp1402,
	srai	a2, a2, 15	# tmp1406, tmp1405,
	add.n	a2, a4, a2	# tmp1407, tmp1403, tmp1406
# @OPUS@\upstream\celt\celt_decoder.c:940:                   buf[DECODE_BUFFER_SIZE-N+i] =
	s32i.n	a2, a3, 0	# MEM[base: _2160, offset: 0B], tmp1407
	addi.n	a3, a3, 4	# ivtmp$261, ivtmp$261,
# @OPUS@\upstream\celt\celt_decoder.c:938:                for (i=overlap;i<extrapolation_len;i++)
	bne	a3, a14, .L204	# ivtmp$261, _1110,
.L197:
# @OPUS@\upstream\celt\celt_decoder.c:946:       } while (++c<C);
	l32i	a14, sp, 280	# %sfp,
	movi.n	a3, 1	# tmp1409,
	movi.n	a2, 2	# tmp1410,
	l32i	a8, sp, 272	# %sfp,
	moveqz	a2, a3, a14	# tmp1408, tmp1409,
	s32i	a3, sp, 280	# %sfp, tmp1409
	blt	a2, a8, .L205	# tmp1408,,
# @OPUS@\upstream\celt\celt_decoder.c:1004:       st->prefilter_and_fold = 1;
	l32i	a9, sp, 244	# %sfp,
	s32i	a3, a9, 88	# *st_322(D).prefilter_and_fold, tmp1409
.L156:
# @OPUS@\upstream\celt\celt_decoder.c:1008:    st->loss_duration = IMIN(10000, loss_duration+(1<<LM));
	l32i	a10, sp, 320	# %sfp,
	l32i	a11, sp, 400	# %sfp,
	l32r	a2, .LC18	#, tmp1418
	add.n	a4, a10, a11	# tmp1413,,
	bge	a2, a4, .L206	# tmp1418, tmp1413,
	mov.n	a4, a2	# tmp1413, tmp1418
.L206:
# @OPUS@\upstream\celt\celt_decoder.c:1008:    st->loss_duration = IMIN(10000, loss_duration+(1<<LM));
	l32i	a12, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1010:    RESTORE_STACK;
	l32i	a2, sp, 180	# _saved_stack,
	l32i	a3, sp, 184	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:1008:    st->loss_duration = IMIN(10000, loss_duration+(1<<LM));
	s32i.n	a4, a12, 60	# *st_322(D).loss_duration, tmp1413
# @OPUS@\upstream\celt\celt_decoder.c:1010:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_decoder.c:1140:       deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i	a9, sp, 308	# %sfp,
	l32i	a10, sp, 464	# accum,
	l32i	a14, sp, 288	# %sfp,
	l32i.n	a6, a12, 16	# *st_322(D).downsample,
# @OPUS@\upstream\celt\celt_decoder.c:1140:       deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	addi	a8, a12, 92	# tmp1422,,
# @OPUS@\upstream\celt\celt_decoder.c:1140:       deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i	a5, sp, 312	# %sfp,
	l32i	a4, sp, 300	# %sfp,
	l32i	a3, sp, 364	# %sfp,
	movi	a2, 0x84	# tmp1420,
	add.n	a2, a9, a2	#,, tmp1420
	addi	a7, a14, 16	#,,
	s32i.n	a10, sp, 4	#,
	s32i.n	a8, sp, 0	#, tmp1422
	call0	deemphasis		#
# @OPUS@\upstream\celt\celt_decoder.c:1141:       RESTORE_STACK;
	l32i	a2, sp, 204	# _saved_stack,
	l32i	a3, sp, 208	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\celt_decoder.c:1142:       return frame_size/st->downsample;
	l32i.n	a3, a12, 16	# *st_322(D).downsample,
	l32i	a2, sp, 352	# %sfp,
	call0	__divsi3		#
	j	.L124		#
.L132:
# @OPUS@\upstream\celt\celt_decoder.c:1153:    if (st->loss_duration == 0) st->skip_plc = 0;
	l32i	a11, sp, 244	# %sfp,
	l32i.n	a2, a11, 60	# *st_322(D).loss_duration, *st_322(D).loss_duration
	bnez.n	a2, .L207	# *st_322(D).loss_duration,
# @OPUS@\upstream\celt\celt_decoder.c:1153:    if (st->loss_duration == 0) st->skip_plc = 0;
	l32i	a14, sp, 332	# %sfp,
	s32i	a14, a11, 64	# *st_322(D).skip_plc,
.L207:
	addi	a8, sp, 80	#,,
	s32i	a8, sp, 308	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1155:    if (dec == NULL)
	bnez.n	a15, .L208	# dec,
# @OPUS@\upstream\celt\celt_decoder.c:1157:       ec_dec_init(&_dec,(unsigned char*)data,len);
	l32i	a4, sp, 304	# %sfp,
	mov.n	a3, a12	#, data
	mov.n	a2, a8	#,
	call0	ec_dec_init		#
# @OPUS@\upstream\celt\celt_decoder.c:1158:       dec = &_dec;
	l32i	a15, sp, 308	# %sfp, dec
.L208:
# @OPUS@\upstream\celt\celt_decoder.c:1161:    if (C==1)
	l32i	a9, sp, 272	# %sfp,
	beqi	a9, 1, .L209	#,,
	l32i	a10, sp, 280	# %sfp,
	slli	a10, a10, 1	#,,
	s32i	a10, sp, 336	# %sfp,
.L212:
# @OPUS@\upstream\celt\celt_decoder.c:1167:    total_bits = len*8;
	l32i	a11, sp, 304	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a12, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
# @OPUS@\upstream\celt\celt_decoder.c:1167:    total_bits = len*8;
	slli	a11, a11, 3	#,,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a2, a2	# _447, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a12, a12, -32	# tmp1429, MEM[(int *)dec_242 + 20B],
	addi	a14, a11, 32	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1167:    total_bits = len*8;
	s32i	a11, sp, 320	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a12, a12, a2	# tell, tmp1429, _447
	s32i	a14, sp, 388	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1170:    if (tell >= total_bits)
	bge	a12, a11, .L351	# tell,,
	j	.L469		#
.L209:
# @OPUS@\upstream\celt\celt_decoder.c:1163:       for (i=0;i<nbEBands;i++)
	l32i	a8, sp, 280	# %sfp,
	bgei	a8, 1, .L470	#,,
	slli	a9, a8, 1	#,,
	s32i	a9, sp, 336	# %sfp,
	j	.L212		#
.L470:
	l32i	a2, sp, 276	# %sfp, ivtmp$423
	slli	a10, a8, 1	#, tmp10,
	s32i	a10, sp, 336	# %sfp,
	add.n	a7, a2, a10	# _2046, ivtmp$423,
	mov.n	a8, a10	# _1847,
.L214:
# @OPUS@\upstream\celt\celt_decoder.c:1164:          oldBandE[i]=MAX16(oldBandE[i],oldBandE[nbEBands+i]);
	add.n	a3, a2, a8	# tmp1431, ivtmp$423, _1847
	l16si	a5, a3, 0	# MEM[base: _2080, offset: 0B], tmp1434
	l16si	a4, a2, 0	# MEM[base: _2087, offset: 0B], tmp1436
	l16ui	a6, a2, 0	# MEM[base: _2087, offset: 0B],
	l16ui	a3, a3, 0	# MEM[base: _2080, offset: 0B],
	bge	a5, a4, .L213	# tmp1434, tmp1436,
	mov.n	a3, a6	# MEM[base: _2080, offset: 0B], MEM[base: _2087, offset: 0B]
.L213:
# @OPUS@\upstream\celt\celt_decoder.c:1164:          oldBandE[i]=MAX16(oldBandE[i],oldBandE[nbEBands+i]);
	s16i	a3, a2, 0	# MEM[base: _2087, offset: 0B], MEM[base: _2080, offset: 0B]
	addi.n	a2, a2, 2	# ivtmp$423, ivtmp$423,
# @OPUS@\upstream\celt\celt_decoder.c:1163:       for (i=0;i<nbEBands;i++)
	bne	a7, a2, .L214	# _2046, ivtmp$423,
	j	.L212		#
.L469:
# @OPUS@\upstream\celt\celt_decoder.c:1175:       silence = 0;
	movi.n	a11, 0	#,
	s32i	a11, sp, 368	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1172:    else if (tell==1)
	bnei	a12, 1, .L215	# tell,,
# @OPUS@\upstream\celt\celt_decoder.c:1173:       silence = ec_dec_bit_logp(dec, 15);
	movi.n	a3, 0xf	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 368	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1176:    if (silence)
	beqz.n	a2, .L215	#,
	l32i.n	a2, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
	l32i	a14, sp, 388	# %sfp,
	nsau	a2, a2	# _447, MEM[(unsigned int *)dec_242 + 28B]
	l32i	a12, sp, 320	# %sfp, tell
	j	.L210		#
.L351:
# @OPUS@\upstream\celt\celt_decoder.c:1171:       silence = 1;
	movi.n	a12, 1	#,
	s32i	a12, sp, 368	# %sfp,
	mov.n	a12, a11	# tell,
.L210:
# @OPUS@\upstream\celt\celt_decoder.c:1180:       dec->nbits_total+=tell-ec_tell(dec);
	sub	a2, a14, a2	# tmp1439,, _447
	s32i.n	a2, a15, 20	# *dec_242.nbits_total, tmp1439
.L215:
# @OPUS@\upstream\celt\celt_decoder.c:1186:    if (start==0 && tell+16 <= total_bits)
	l32i	a8, sp, 268	# %sfp,
	bnez.n	a8, .L353	#,
# @OPUS@\upstream\celt\celt_decoder.c:1186:    if (start==0 && tell+16 <= total_bits)
	l32i	a9, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1186:    if (start==0 && tell+16 <= total_bits)
	addi	a2, a12, 16	# tmp1440, tell,
# @OPUS@\upstream\celt\celt_decoder.c:1186:    if (start==0 && tell+16 <= total_bits)
	blt	a9, a2, .L354	#, tmp1440,
# @OPUS@\upstream\celt\celt_decoder.c:1188:       if(ec_dec_bit_logp(dec, 1))
	movi.n	a3, 1	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 360	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1188:       if(ec_dec_bit_logp(dec, 1))
	bnez.n	a2, .L217	#,
# @OPUS@\upstream\celt\celt_decoder.c:1185:    postfilter_tapset = 0;
	l32i	a10, sp, 268	# %sfp,
	l32i.n	a12, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], _504
	nsau	a12, a12	# _519, MEM[(unsigned int *)dec_242 + 28B]
	s32i	a10, sp, 356	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1183:    postfilter_gain = 0;
	s32i	a10, sp, 372	# %sfp,
	j	.L218		#
.L217:
# @OPUS@\upstream\celt\celt_decoder.c:1191:          octave = ec_dec_uint(dec, 6);
	movi.n	a3, 6	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_uint		#
	mov.n	a12, a2	# _54,
# @OPUS@\upstream\celt\celt_decoder.c:1192:          postfilter_pitch = (16<<octave)+ec_dec_bits(dec, 4+octave)-1;
	addi.n	a3, a2, 4	#, _54,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bits		#
# @OPUS@\upstream\celt\celt_decoder.c:1192:          postfilter_pitch = (16<<octave)+ec_dec_bits(dec, 4+octave)-1;
	movi.n	a4, 0x10	# tmp1443,
	ssl	a12	# _54
	sll	a4, a4	# tmp1444, tmp1443
# @OPUS@\upstream\celt\celt_decoder.c:1192:          postfilter_pitch = (16<<octave)+ec_dec_bits(dec, 4+octave)-1;
	addi.n	a5, a2, -1	# tmp1445,,
# @OPUS@\upstream\celt\celt_decoder.c:1193:          qg = ec_dec_bits(dec, 3);
	movi.n	a3, 3	#,
# @OPUS@\upstream\celt\celt_decoder.c:1192:          postfilter_pitch = (16<<octave)+ec_dec_bits(dec, 4+octave)-1;
	add.n	a5, a4, a5	#, tmp1444, tmp1445
# @OPUS@\upstream\celt\celt_decoder.c:1193:          qg = ec_dec_bits(dec, 3);
	mov.n	a2, a15	#, dec
# @OPUS@\upstream\celt\celt_decoder.c:1192:          postfilter_pitch = (16<<octave)+ec_dec_bits(dec, 4+octave)-1;
	s32i	a5, sp, 360	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1193:          qg = ec_dec_bits(dec, 3);
	call0	ec_dec_bits		#
	mov.n	a13, a2	# qg,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a12, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1194:          if (ec_tell(dec)+2<=total_bits)
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], _504
# @OPUS@\upstream\celt\celt_decoder.c:1185:    postfilter_tapset = 0;
	l32i	a11, sp, 268	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1194:          if (ec_tell(dec)+2<=total_bits)
	addi	a3, a2, -30	# tmp1447, _504,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a12, a12	# _519, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1194:          if (ec_tell(dec)+2<=total_bits)
	l32i	a14, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1194:          if (ec_tell(dec)+2<=total_bits)
	add.n	a3, a3, a12	# tmp1448, tmp1447, _519
# @OPUS@\upstream\celt\celt_decoder.c:1185:    postfilter_tapset = 0;
	s32i	a11, sp, 356	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1194:          if (ec_tell(dec)+2<=total_bits)
	blt	a14, a3, .L219	#, tmp1448,
# @OPUS@\upstream\celt\celt_decoder.c:1195:             postfilter_tapset = ec_dec_icdf(dec, tapset_icdf, 2);
	l32r	a3, .LC19	#,
	movi.n	a4, 2	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
	l32i.n	a12, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
	s32i	a2, sp, 356	# %sfp,
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], _504
	nsau	a12, a12	# _519, MEM[(unsigned int *)dec_242 + 28B]
.L219:
# @OPUS@\upstream\celt\celt_decoder.c:1196:          postfilter_gain = QCONST16(.09375f,15)*(qg+1);
	addi.n	a3, a13, 1	# tmp1451, qg,
	slli	a4, a3, 1	# tmp1454, tmp1451,
	add.n	a3, a3, a4	# tmp1456, tmp1451, tmp1454
	slli	a3, a3, 26	# tmp1459, tmp1456,
	srai	a3, a3, 16	#, tmp1459,
	s32i	a3, sp, 372	# %sfp,
.L218:
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a12	# tmp1460, _504, _519
	addi	a12, a2, -32	# tell, tmp1460,
	j	.L216		#
.L353:
# @OPUS@\upstream\celt\celt_decoder.c:1185:    postfilter_tapset = 0;
	movi.n	a8, 0	#,
	s32i	a8, sp, 356	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1183:    postfilter_gain = 0;
	s32i	a8, sp, 372	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1184:    postfilter_pitch = 0;
	s32i	a8, sp, 360	# %sfp,
	j	.L216		#
.L354:
# @OPUS@\upstream\celt\celt_decoder.c:1185:    postfilter_tapset = 0;
	s32i	a8, sp, 356	# %sfp, tmp9
# @OPUS@\upstream\celt\celt_decoder.c:1184:    postfilter_pitch = 0;
	s32i	a8, sp, 360	# %sfp, tmp9
# @OPUS@\upstream\celt\celt_decoder.c:1183:    postfilter_gain = 0;
	s32i	a8, sp, 372	# %sfp, tmp9
.L216:
# @OPUS@\upstream\celt\celt_decoder.c:1201:    if (LM > 0 && tell+3 <= total_bits)
	l32i	a10, sp, 260	# %sfp,
	addi.n	a2, a12, 3	# _1823, tell,
	blti	a10, 1, .L356	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1207:       isTransient = 0;
	movi.n	a11, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:1201:    if (LM > 0 && tell+3 <= total_bits)
	l32i	a12, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1207:       isTransient = 0;
	s32i	a11, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1212:       shortBlocks = 0;
	s32i	a11, sp, 392	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1201:    if (LM > 0 && tell+3 <= total_bits)
	blt	a12, a2, .L221	#, _1823,
	movi.n	a12, 1	# tmp1461,
	bgei	a10, 2, .L222	#,,
	mov.n	a12, a11	# tmp1461,
.L222:
# @OPUS@\upstream\celt\celt_decoder.c:1203:       isTransient = ec_dec_bit_logp(dec, 3);
	movi.n	a3, 3	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 292	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _525, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a2, -32	# tmp1464, MEM[(int *)dec_242 + 20B],
# @OPUS@\upstream\celt\celt_decoder.c:1209:    if (isTransient)
	l32i	a14, sp, 292	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a3	# _527, tmp1464, _525
	extui	a12, a12, 0, 8	# _2230, tmp1461
	addi.n	a2, a2, 3	# _1823, _527,
# @OPUS@\upstream\celt\celt_decoder.c:1209:    if (isTransient)
	bnez.n	a14, .L223	#,
# @OPUS@\upstream\celt\celt_decoder.c:1212:       shortBlocks = 0;
	s32i	a14, sp, 392	# %sfp,
	j	.L220		#
.L223:
# @OPUS@\upstream\celt\celt_decoder.c:1210:       shortBlocks = M;
	l32i	a8, sp, 400	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1209:    if (isTransient)
	s32i	a12, sp, 332	# %sfp, _2230
# @OPUS@\upstream\celt\celt_decoder.c:1210:       shortBlocks = M;
	s32i	a8, sp, 392	# %sfp,
	j	.L220		#
.L356:
# @OPUS@\upstream\celt\celt_decoder.c:1207:       isTransient = 0;
	movi.n	a9, 0	#,
	s32i	a9, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1212:       shortBlocks = 0;
	s32i	a9, sp, 392	# %sfp,
.L220:
# @OPUS@\upstream\celt\celt_decoder.c:1215:    intra_ener = tell+3<=total_bits ? ec_dec_bit_logp(dec, 3) : 0;
	l32i	a10, sp, 320	# %sfp,
	blt	a10, a2, .L221	#, _1823,
# @OPUS@\upstream\celt\celt_decoder.c:1215:    intra_ener = tell+3<=total_bits ? ec_dec_bit_logp(dec, 3) : 0;
	movi.n	a3, 3	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
	mov.n	a6, a2	# _69,
# @OPUS@\upstream\celt\celt_decoder.c:1218:    if (!intra_ener && st->loss_duration != 0) {
	bnez.n	a2, .L224	# _69,
.L221:
# @OPUS@\upstream\celt\celt_decoder.c:1218:    if (!intra_ener && st->loss_duration != 0) {
	l32i	a11, sp, 244	# %sfp,
	l32i.n	a6, a11, 60	# *st_322(D).loss_duration, _69
# @OPUS@\upstream\celt\celt_decoder.c:1218:    if (!intra_ener && st->loss_duration != 0) {
	beqz.n	a6, .L224	# _69,
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	l32i	a12, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	movi.n	a2, 0xa	# tmp1468,
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	ssr	a12	#
	sra	a6, a6	# missing, _69
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	bge	a2, a6, .L225	# tmp1468, missing,
	mov.n	a6, a2	# missing, tmp1468
.L225:
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	l32i	a14, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	movi.n	a4, 2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	addi.n	a3, a14, -1	# tmp2552,,
# @OPUS@\upstream\celt\celt_decoder.c:1219:       c=0; do
	movi.n	a2, 0	# c,
# @OPUS@\upstream\celt\celt_decoder.c:1222:          int missing = IMIN(10, st->loss_duration>>LM);
	s32i	a4, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	movi	a4, 0x200	# tmp2551,
	movnez	a4, a2, a3	# tmp2551, c, tmp2552
# @OPUS@\upstream\celt\celt_decoder.c:1235:                E0 -= MAX32(0, (1+missing)*slope);
	addi.n	a6, a6, 1	# tmp2554, missing,
	s32i	a15, sp, 256	# %sfp, dec
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	s32i	a4, sp, 248	# %sfp, tmp2551
# @OPUS@\upstream\celt\celt_decoder.c:1236:                oldBandE[c*nbEBands+i] = MAX32(-QCONST16(20.f,DB_SHIFT), E0);
	l32r	a14, .LC20	#, tmp2555
	mov.n	a15, a6	# tmp2554, tmp2554
	j	.L228		#
.L360:
	s32i	a2, sp, 240	# %sfp, c
.L228:
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	l32i	a8, sp, 260	# %sfp,
	l32i	a9, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1225:          for (i=start;i<end;i++)
	l32i	a10, sp, 268	# %sfp,
	l32i	a11, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1223:          if (LM==0) safety = QCONST16(1.5f,DB_SHIFT);
	movi	a13, 0x600	# safety,
# @OPUS@\upstream\celt\celt_decoder.c:1224:          else if (LM==1) safety = QCONST16(.5f,DB_SHIFT);
	movnez	a13, a9, a8	# safety,,
# @OPUS@\upstream\celt\celt_decoder.c:1225:          for (i=start;i<end;i++)
	blt	a10, a11, .L227	#,,
.L234:
# @OPUS@\upstream\celt\celt_decoder.c:1244:       } while (++c<2);
	l32i	a12, sp, 240	# %sfp,
	movi.n	a2, 1	# c,
	bne	a12, a2, .L360	#,,
	l32i	a15, sp, 256	# %sfp, dec
	movi.n	a6, 0	# _69,
	j	.L224		#
.L227:
# @OPUS@\upstream\celt\celt_decoder.c:1227:             if (oldBandE[c*nbEBands+i] < MAX16(oldLogE[c*nbEBands+i], oldLogE2[c*nbEBands+i])) {
	l32i	a8, sp, 280	# %sfp,
	l32i	a12, sp, 276	# %sfp,
	mull	a2, a2, a8	# _72, c,
	l32i	a8, sp, 348	# %sfp,
	add.n	a7, a2, a10	# tmp1469, _72, tmp9
	add.n	a10, a11, a2	# tmp1470,, _72
	l32i	a11, sp, 328	# %sfp,
	slli	a7, a7, 1	# _2209, tmp1469,
	slli	a10, a10, 1	# tmp1471, tmp1470,
	add.n	a5, a12, a7	# ivtmp$411,, _2209
	add.n	a9, a8, a7	# ivtmp$412,, _2209
	add.n	a10, a12, a10	# _2128,, tmp1471
	add.n	a7, a11, a7	# ivtmp$413,, _2209
.L237:
# @OPUS@\upstream\celt\celt_decoder.c:1227:             if (oldBandE[c*nbEBands+i] < MAX16(oldLogE[c*nbEBands+i], oldLogE2[c*nbEBands+i])) {
	l16si	a2, a9, 0	# MEM[base: _2154, offset: 0B], _1936
	l16si	a6, a7, 0	# MEM[base: _2147, offset: 0B], _1934
	slli	a11, a2, 16	# tmp1971, _1936,
	srai	a12, a11, 16	# tmp1482, tmp1971,
# @OPUS@\upstream\celt\celt_decoder.c:1227:             if (oldBandE[c*nbEBands+i] < MAX16(oldLogE[c*nbEBands+i], oldLogE2[c*nbEBands+i])) {
	l16si	a4, a5, 0	# MEM[base: _2152, offset: 0B], _1938
# @OPUS@\upstream\celt\celt_decoder.c:1227:             if (oldBandE[c*nbEBands+i] < MAX16(oldLogE[c*nbEBands+i], oldLogE2[c*nbEBands+i])) {
	mov.n	a3, a6	# _1934, _1934
	slli	a8, a6, 16	# tmp1970, _1934,
	bge	a6, a12, .L230	# _1934, tmp1482,
	mov.n	a3, a2	# _1934, _1936
.L230:
# @OPUS@\upstream\celt\celt_decoder.c:1227:             if (oldBandE[c*nbEBands+i] < MAX16(oldLogE[c*nbEBands+i], oldLogE2[c*nbEBands+i])) {
	slli	a3, a3, 16	# tmp1485, _1934,
	srai	a3, a3, 16	# tmp1484, tmp1485,
	bge	a4, a3, .L229	# _1938, tmp1484,
# @OPUS@\upstream\celt\celt_decoder.c:1234:                slope = MAX32(E1 - E0, HALF32(E2 - E0));
	sub	a2, a2, a4	# tmp1487, _1936, _1938
	sub	a6, a6, a4	# tmp1489, _1934, _1938
# @OPUS@\upstream\celt\celt_decoder.c:1234:                slope = MAX32(E1 - E0, HALF32(E2 - E0));
	srai	a2, a2, 1	# slope, tmp1487,
	bge	a2, a6, .L231	# slope, tmp1489,
	mov.n	a2, a6	# slope, tmp1489
.L231:
# @OPUS@\upstream\celt\celt_decoder.c:1235:                E0 -= MAX32(0, (1+missing)*slope);
	mull	a2, a2, a15	# _1911, slope, tmp2554
	movi.n	a12, 0	#,
	movltz	a2, a12, a2	# _1911,, _1911
# @OPUS@\upstream\celt\celt_decoder.c:1235:                E0 -= MAX32(0, (1+missing)*slope);
	sub	a2, a4, a2	# E0, _1938, _1911
# @OPUS@\upstream\celt\celt_decoder.c:1236:                oldBandE[c*nbEBands+i] = MAX32(-QCONST16(20.f,DB_SHIFT), E0);
	bge	a2, a14, .L236	# E0, tmp2555,
	mov.n	a2, a14	# E0, tmp2555
	j	.L236		#
.L229:
# @OPUS@\upstream\celt\celt_decoder.c:1239:                oldBandE[c*nbEBands+i] = MIN16(MIN16(oldBandE[c*nbEBands+i], oldLogE[c*nbEBands+i]), oldLogE2[c*nbEBands+i]);
	srai	a11, a11, 16	# tmp1503, tmp1971,
	bge	a4, a11, .L235	# _1938, tmp1503,
	mov.n	a2, a4	# _1936, _1938
.L235:
	slli	a3, a2, 16	# tmp1509, _1936,
	bge	a8, a3, .L236	# tmp1970, tmp1509,
	mov.n	a2, a6	# _1936, _1934
.L236:
# @OPUS@\upstream\celt\celt_decoder.c:1242:             oldBandE[c*nbEBands+i] -= safety;
	sub	a2, a2, a13	# tmp1512, _1936, safety
	s16i	a2, a5, 0	# MEM[base: _2152, offset: 0B], tmp1512
	addi.n	a5, a5, 2	# ivtmp$411, ivtmp$411,
	addi.n	a9, a9, 2	# ivtmp$412, ivtmp$412,
	addi.n	a7, a7, 2	# ivtmp$413, ivtmp$413,
# @OPUS@\upstream\celt\celt_decoder.c:1225:          for (i=start;i<end;i++)
	bne	a5, a10, .L237	# ivtmp$411, _2128,
	j	.L234		#
.L224:
# @OPUS@\upstream\celt\celt_decoder.c:1248:    unquant_coarse_energy(mode, start, end, oldBandE,
	l32i	a8, sp, 272	# %sfp,
	l32i	a14, sp, 260	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a4, sp, 264	# %sfp,
	l32i	a3, sp, 268	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	mov.n	a7, a15	#, dec
	s32i.n	a8, sp, 0	#,
	s32i.n	a14, sp, 4	#,
	call0	unquant_coarse_energy		#
# @OPUS@\upstream\celt\celt_decoder.c:1253:    ALLOC(tf_res, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:491:    tell = ec_tell(dec);
	l32i.n	a6, a15, 20	# MEM[(int *)dec_242 + 20B], _996
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a7, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:490:    budget = dec->storage*8;
	l32i.n	a4, a15, 4	# *dec_242.storage, *dec_242.storage
# @OPUS@\upstream\celt\celt_decoder.c:492:    logp = isTransient ? 2 : 4;
	l32i	a9, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1253:    ALLOC(tf_res, nbEBands, int);
	s32i	a2, sp, 324	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a8, a7	# _998, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a6, -32	# tmp1515, _996,
# @OPUS@\upstream\celt\celt_decoder.c:490:    budget = dec->storage*8;
	slli	a4, a4, 3	# budget, *dec_242.storage,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a8	# tell, tmp1515, _998
# @OPUS@\upstream\celt\celt_decoder.c:492:    logp = isTransient ? 2 : 4;
	bnez.n	a9, .L361	#,
	movi.n	a5, 4	# prephitmp_1824,
	mov.n	a3, a5	# logp, prephitmp_1824
	j	.L238		#
.L361:
	movi.n	a5, 2	# prephitmp_1824,
	mov.n	a3, a5	# logp, prephitmp_1824
.L238:
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	l32i	a10, sp, 260	# %sfp,
	bgei	a10, 1, .L239	#,,
	movi.n	a11, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	l32i	a12, sp, 268	# %sfp,
	l32i	a14, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	s32i	a11, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:494:    budget -= tf_select_rsv;
	mov.n	a5, a4	# budget, budget
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	blt	a12, a14, .L240	#,,
	j	.L241		#
.L239:
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	addi.n	a8, a2, 1	# tmp1516, tell,
	add.n	a8, a8, a5	# _1005, tmp1516, prephitmp_1824
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	movi.n	a12, 1	# tmp1517,
	bgeu	a4, a8, .L242	# budget, _1005,
	movi.n	a12, 0	# tmp1517,
.L242:
	extui	a12, a12, 0, 8	#, tmp1517
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	l32i	a9, sp, 268	# %sfp,
	l32i	a10, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	s32i	a12, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:494:    budget -= tf_select_rsv;
	sub	a5, a4, a12	# budget, budget,
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	bge	a9, a10, .L243	#,,
.L240:
	l32i	a11, sp, 268	# %sfp,
	l32i	a14, sp, 292	# %sfp,
	l32i	a8, sp, 324	# %sfp,
	movi.n	a7, 4	# tmp1520,
	slli	a13, a11, 2	# tmp1522,,
# @OPUS@\upstream\celt\celt_decoder.c:495:    tf_changed = curr = 0;
	movi.n	a12, 0	# tf_changed,
	movi.n	a4, 5	# tmp1521,
# @OPUS@\upstream\celt\celt_decoder.c:495:    tf_changed = curr = 0;
	mov.n	a6, a15	# dec, dec
	mov.n	a15, a5	# budget, budget
	l32i	a5, sp, 264	# %sfp, end
	movnez	a4, a7, a14	# iftmp$78_1052, tmp1520,
	add.n	a13, a8, a13	# ivtmp$407,, tmp1522
# @OPUS@\upstream\celt\celt_decoder.c:493:    tf_select_rsv = LM>0 && tell+logp+1<=budget;
	mov.n	a14, a11	# i,
# @OPUS@\upstream\celt\celt_decoder.c:495:    tf_changed = curr = 0;
	mov.n	a7, a12	# tf_changed, tf_changed
.L247:
# @OPUS@\upstream\celt\celt_decoder.c:498:       if (tell+logp<=budget)
	add.n	a8, a3, a2	# tmp1523, logp, tell
# @OPUS@\upstream\celt\celt_decoder.c:498:       if (tell+logp<=budget)
	bltu	a15, a8, .L244	# budget, tmp1523,
# @OPUS@\upstream\celt\celt_decoder.c:500:          curr ^= ec_dec_bit_logp(dec, logp);
	mov.n	a2, a6	#, dec
	s32i	a4, sp, 404	#,
	s32i	a5, sp, 412	#,
	s32i	a6, sp, 416	#,
	s32i	a7, sp, 408	#,
	call0	ec_dec_bit_logp		#
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i	a6, sp, 416	#,
# @OPUS@\upstream\celt\celt_decoder.c:500:          curr ^= ec_dec_bit_logp(dec, logp);
	xor	a12, a12, a2	# curr, curr,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a8, a6, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a6, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
# @OPUS@\upstream\celt\celt_decoder.c:502:          tf_changed |= curr;
	l32i	a7, sp, 408	#,
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	l32i	a5, sp, 412	#,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a8, a8	# _1018, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a3, -32	# tmp1525, MEM[(int *)dec_242 + 20B],
# @OPUS@\upstream\celt\celt_decoder.c:504:       tf_res[i] = curr;
	s32i.n	a12, a13, 0	# MEM[base: _1589, offset: 0B], curr
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	addi.n	a14, a14, 1	# i, i,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a8	# tell, tmp1525, _1018
# @OPUS@\upstream\celt\celt_decoder.c:502:          tf_changed |= curr;
	or	a7, a7, a12	# tf_changed, tf_changed, curr
	addi.n	a13, a13, 4	# ivtmp$407, ivtmp$407,
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	l32i	a4, sp, 404	#,
	blt	a14, a5, .L245	# i, end,
	j	.L481		#
.L244:
# @OPUS@\upstream\celt\celt_decoder.c:504:       tf_res[i] = curr;
	s32i.n	a12, a13, 0	# MEM[base: _7, offset: 0B], curr
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	addi.n	a14, a14, 1	# i, i,
	addi.n	a13, a13, 4	# ivtmp$407, ivtmp$407,
# @OPUS@\upstream\celt\celt_decoder.c:496:    for (i=start;i<end;i++)
	bge	a14, a5, .L481	# i, end,
.L245:
# @OPUS@\upstream\celt\celt_decoder.c:505:       logp = isTransient ? 4 : 5;
	mov.n	a3, a4	# logp, iftmp$78_1052
	j	.L247		#
.L481:
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	l32i	a9, sp, 240	# %sfp,
	mov.n	a15, a6	# dec, dec
	beqz.n	a9, .L248	#,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	l32i	a10, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	l32i	a11, sp, 260	# %sfp,
	l32r	a3, .LC21	#, tmp1962
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	slli	a4, a10, 2	# tmp1527,,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	slli	a2, a11, 3	# tmp1978,,
	add.n	a2, a3, a2	# tmp1530, tmp1962, tmp1978
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	add.n	a6, a4, a7	# _1032, tmp1527, tf_changed
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	add.n	a6, a2, a6	# tmp1531, tmp1530, _1032
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	l8ui	a2, a6, 0	# tf_select_table,
	l8ui	a3, a6, 2	# tf_select_table,
# @OPUS@\upstream\celt\celt_decoder.c:507:    tf_select = 0;
	movi.n	a12, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	slli	a2, a2, 24	# tmp1539, tmp1538,
	slli	a3, a3, 24	# tmp1542, tmp1541,
# @OPUS@\upstream\celt\celt_decoder.c:507:    tf_select = 0;
	s32i	a12, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	beq	a3, a2, .L248	# tmp1542, tmp1539,
.L337:
# @OPUS@\upstream\celt\celt_decoder.c:512:       tf_select = ec_dec_bit_logp(dec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 240	# %sfp,
.L248:
# @OPUS@\upstream\celt\celt_decoder.c:514:    for (i=start;i<end;i++)
	l32i	a14, sp, 268	# %sfp,
	l32i	a8, sp, 264	# %sfp,
	blt	a14, a8, .L249	#,,
	l32i.n	a7, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
	l32i.n	a6, a15, 20	# MEM[(int *)dec_242 + 20B], _996
.L336:
	nsau	a8, a7	# _998, MEM[(unsigned int *)dec_242 + 28B]
	j	.L241		#
.L249:
# @OPUS@\upstream\celt\celt_decoder.c:516:       tf_res[i] = tf_select_table[LM][4*isTransient+2*tf_select+tf_res[i]];
	l32i	a9, sp, 292	# %sfp,
	l32i	a10, sp, 240	# %sfp,
	l32i	a11, sp, 260	# %sfp,
	slli	a4, a9, 1	# tmp1544,,
	l32r	a3, .LC21	#, tmp1962
	l32i	a9, sp, 324	# %sfp,
	add.n	a4, a4, a10	# tmp1545, tmp1544,
	slli	a2, a11, 3	# tmp1978,,
# @OPUS@\upstream\celt\celt_decoder.c:516:       tf_res[i] = tf_select_table[LM][4*isTransient+2*tf_select+tf_res[i]];
	add.n	a2, a3, a2	# tmp1551, tmp1962, tmp1978
# @OPUS@\upstream\celt\celt_decoder.c:516:       tf_res[i] = tf_select_table[LM][4*isTransient+2*tf_select+tf_res[i]];
	slli	a4, a4, 1	# _1040, tmp1545,
	slli	a12, a14, 2	# _396,,
	slli	a5, a8, 2	# tmp1547,,
	add.n	a3, a9, a12	# ivtmp$403,, _396
	add.n	a5, a9, a5	# _93,, tmp1547
# @OPUS@\upstream\celt\celt_decoder.c:516:       tf_res[i] = tf_select_table[LM][4*isTransient+2*tf_select+tf_res[i]];
	add.n	a4, a2, a4	# tmp1552, tmp1551, _1040
.L250:
	l32i.n	a2, a3, 0	# MEM[base: _119, offset: 0B], MEM[base: _119, offset: 0B]
	add.n	a2, a4, a2	# tmp1553, tmp1552, MEM[base: _119, offset: 0B]
	l8ui	a2, a2, 0	# tf_select_table,
	slli	a2, a2, 24	# tmp1556, tmp1555,
	srai	a2, a2, 24	# tmp1554, tmp1556,
	s32i.n	a2, a3, 0	# MEM[base: _119, offset: 0B], tmp1554
	addi.n	a3, a3, 4	# ivtmp$403, ivtmp$403,
# @OPUS@\upstream\celt\celt_decoder.c:514:    for (i=start;i<end;i++)
	bne	a5, a3, .L250	# _93, ivtmp$403,
	j	.L471		#
.L330:
	l32i	a14, sp, 384	# %sfp,
	l32i	a10, sp, 268	# %sfp,
	l32i	a11, sp, 252	# %sfp,
	add.n	a14, a14, a12	#,, _396
	slli	a13, a10, 1	# tmp1557,,
	s32i	a14, sp, 256	# %sfp,
	l32i	a6, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	l32i	a14, sp, 380	# %sfp, total_bits
	add.n	a13, a11, a13	#,, tmp1557
# @OPUS@\upstream\celt\celt_decoder.c:1290:          dynalloc_loop_logp = 1;
	mov.n	a3, a14	# total_bits, total_bits
	s32i	a13, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	movi.n	a8, 6	#,
	add.n	a13, a6, a12	# ivtmp$394,, _396
# @OPUS@\upstream\celt\celt_decoder.c:1290:          dynalloc_loop_logp = 1;
	mov.n	a14, a13	# ivtmp$394, ivtmp$394
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	s32i	a10, sp, 252	# %sfp,
	s32i	a8, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1290:          dynalloc_loop_logp = 1;
	mov.n	a2, a7	# tell, tell
	mov.n	a13, a3	# total_bits, total_bits
.L260:
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	l32i	a9, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	l32i	a10, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	l16si	a6, a9, 0	# MEM[base: _258, offset: 0B], tmp1561
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	l16si	a3, a9, 2	# MEM[base: _258, offset: 2B], tmp1558
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	l32i	a11, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	sub	a3, a3, a6	# tmp1564, tmp1558, tmp1561
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	mull	a3, a3, a10	# tmp1565, tmp1564,
# @OPUS@\upstream\celt\celt_decoder.c:1278:       quanta = IMIN(width<<BITRES, IMAX(6<<BITRES, width));
	movi.n	a4, 0x30	# tmp1571,
# @OPUS@\upstream\celt\celt_decoder.c:1275:       width = C*(eBands[i+1]-eBands[i])<<LM;
	ssl	a11	#
	sll	a3, a3	# width, tmp1565
# @OPUS@\upstream\celt\celt_decoder.c:1278:       quanta = IMIN(width<<BITRES, IMAX(6<<BITRES, width));
	mov.n	a6, a3	# width, width
	bge	a3, a4, .L252	# width, tmp1571,
	mov.n	a6, a4	# width, tmp1571
.L252:
	slli	a3, a3, 3	# tmp1572, width,
# @OPUS@\upstream\celt\celt_decoder.c:1278:       quanta = IMIN(width<<BITRES, IMAX(6<<BITRES, width));
	bge	a3, a6, .L253	# tmp1572, quanta,
	mov.n	a6, a3	# quanta, tmp1572
.L253:
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	l32i	a12, sp, 248	# %sfp,
	slli	a3, a12, 3	# tmp1573,,
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	add.n	a3, a3, a2	# tmp1574, tmp1573, tell
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	bge	a3, a13, .L254	# tmp1574, total_bits,
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	l32i.n	a3, a14, 0	# MEM[base: _264, offset: 0B], MEM[base: _264, offset: 0B]
	blti	a3, 1, .L255	# MEM[base: _264, offset: 0B],,
	mov.n	a3, a12	# dynalloc_loop_logp,
# @OPUS@\upstream\celt\celt_decoder.c:1280:       boost = 0;
	mov.n	a5, a14	# ivtmp$394, ivtmp$394
	movi.n	a12, 0	# boost,
.L257:
# @OPUS@\upstream\celt\celt_decoder.c:1284:          flag = ec_dec_bit_logp(dec, dynalloc_loop_logp);
	mov.n	a2, a15	#, dec
	s32i	a5, sp, 412	#,
	s32i	a6, sp, 416	#,
	call0	ec_dec_bit_logp		#
	mov.n	a14, a2	# flag,
# @OPUS@\upstream\celt\celt_decoder.c:1285:          tell = ec_tell_frac(dec);
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	addi.n	a3, a2, 8	# tmp1576, tell,
# @OPUS@\upstream\celt\celt_decoder.c:1286:          if (!flag)
	l32i	a5, sp, 412	#,
	l32i	a6, sp, 416	#,
	beqz.n	a14, .L483	# flag,
# @OPUS@\upstream\celt\celt_decoder.c:1289:          total_bits -= quanta;
	sub	a13, a13, a6	# total_bits, total_bits, quanta
# @OPUS@\upstream\celt\celt_decoder.c:1288:          boost += quanta;
	add.n	a12, a12, a6	# boost, boost, quanta
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	bge	a3, a13, .L483	# tmp1576, total_bits,
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	l32i.n	a4, a5, 0	# MEM[base: _264, offset: 0B], MEM[base: _264, offset: 0B]
# @OPUS@\upstream\celt\celt_decoder.c:1290:          dynalloc_loop_logp = 1;
	movi.n	a3, 1	# dynalloc_loop_logp,
# @OPUS@\upstream\celt\celt_decoder.c:1281:       while (tell+(dynalloc_loop_logp<<BITRES) < total_bits && boost < cap[i])
	blt	a12, a4, .L257	# boost, MEM[base: _264, offset: 0B],
	j	.L483		#
.L255:
# @OPUS@\upstream\celt\celt_decoder.c:1292:       offsets[i] = boost;
	l32i	a4, sp, 256	# %sfp,
	movi.n	a3, 0	# tmp1578,
	s32i.n	a3, a4, 0	# MEM[base: _283, offset: 0B], tmp1578
	j	.L258		#
.L254:
	l32i	a5, sp, 256	# %sfp,
	movi.n	a3, 0	# tmp1579,
	s32i.n	a3, a5, 0	# MEM[base: _276, offset: 0B], tmp1579
	j	.L258		#
.L483:
	l32i	a6, sp, 256	# %sfp,
	mov.n	a14, a5	# ivtmp$394, ivtmp$394
	s32i.n	a12, a6, 0	# MEM[base: _278, offset: 0B], boost
# @OPUS@\upstream\celt\celt_decoder.c:1294:       if (boost>0)
	blti	a12, 1, .L258	# boost,,
# @OPUS@\upstream\celt\celt_decoder.c:1295:          dynalloc_logp = IMAX(2, dynalloc_logp-1);
	l32i	a7, sp, 248	# %sfp,
	addi.n	a7, a7, -1	#,,
	s32i	a7, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1295:          dynalloc_logp = IMAX(2, dynalloc_logp-1);
	bgei	a7, 2, .L258	#,,
	movi.n	a8, 2	#,
	s32i	a8, sp, 248	# %sfp,
.L258:
# @OPUS@\upstream\celt\celt_decoder.c:1270:    for (i=start;i<end;i++)
	l32i	a9, sp, 252	# %sfp,
	l32i	a10, sp, 240	# %sfp,
	l32i	a11, sp, 256	# %sfp,
	addi.n	a9, a9, 1	#,,
	addi.n	a10, a10, 2	#,,
	addi.n	a11, a11, 4	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1270:    for (i=start;i<end;i++)
	l32i	a12, sp, 264	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1270:    for (i=start;i<end;i++)
	s32i	a9, sp, 252	# %sfp,
	s32i	a10, sp, 240	# %sfp,
	s32i	a11, sp, 256	# %sfp,
	addi.n	a14, a14, 4	# ivtmp$394, ivtmp$394,
# @OPUS@\upstream\celt\celt_decoder.c:1270:    for (i=start;i<end;i++)
	blt	a9, a12, .L260	#,,
	mov.n	a7, a2	# tell, tell
	mov.n	a14, a13	# total_bits, total_bits
.L333:
# @OPUS@\upstream\celt\celt_decoder.c:1298:    ALLOC(fine_quant, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	s32i	a7, sp, 408	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1299:    alloc_trim = tell+(6<<BITRES) <= total_bits ?
	l32i	a7, sp, 408	#,
# @OPUS@\upstream\celt\celt_decoder.c:1298:    ALLOC(fine_quant, nbEBands, int);
	s32i	a2, sp, 240	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1299:    alloc_trim = tell+(6<<BITRES) <= total_bits ?
	addi	a7, a7, 48	# tmp1582, tell,
# @OPUS@\upstream\celt\celt_decoder.c:1300:          ec_dec_icdf(dec, trim_icdf, 7) : 5;
	movi.n	a12, 5	# iftmp$16_281,
	blt	a14, a7, .L261	# total_bits, tmp1582,
# @OPUS@\upstream\celt\celt_decoder.c:1300:          ec_dec_icdf(dec, trim_icdf, 7) : 5;
	l32r	a3, .LC22	#,
	movi.n	a4, 7	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
	mov.n	a12, a2	# iftmp$16_281,
.L261:
# @OPUS@\upstream\celt\celt_decoder.c:1302:    bits = (((opus_int32)len*8)<<BITRES) - ec_tell_frac(dec) - 1;
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\celt_decoder.c:1302:    bits = (((opus_int32)len*8)<<BITRES) - ec_tell_frac(dec) - 1;
	l32i	a14, sp, 380	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	movi.n	a8, 0	#,
	l32i	a9, sp, 332	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1302:    bits = (((opus_int32)len*8)<<BITRES) - ec_tell_frac(dec) - 1;
	addi.n	a13, a14, -1	# tmp1584,,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	s32i	a8, sp, 252	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1302:    bits = (((opus_int32)len*8)<<BITRES) - ec_tell_frac(dec) - 1;
	sub	a13, a13, a2	# bits, tmp1584,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	beq	a9, a8, .L262	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	l32i	a10, sp, 260	# %sfp,
	addi.n	a2, a10, 2	# tmp1585,,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	slli	a2, a2, 3	# tmp1586, tmp1585,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	blt	a13, a2, .L262	# bits, tmp1586,
# @OPUS@\upstream\celt\celt_decoder.c:1303:    anti_collapse_rsv = isTransient&&LM>=2&&bits>=((LM+2)<<BITRES) ? (1<<BITRES) : 0;
	movi.n	a11, 8	#,
	addi	a13, a13, -8	# bits, bits,
	s32i	a11, sp, 252	# %sfp,
.L262:
# @OPUS@\upstream\celt\celt_decoder.c:1306:    ALLOC(pulses, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1307:    ALLOC(fine_priority, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1309:    codedBands = clt_compute_allocation(mode, start, end, offsets, cap,
	mov.n	a7, a12	#, iftmp$16_281
	l32i	a14, sp, 308	# %sfp,
	l32i	a11, sp, 260	# %sfp,
	l32i	a12, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1307:    ALLOC(fine_priority, nbEBands, int);
	s32i	a2, sp, 332	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1309:    codedBands = clt_compute_allocation(mode, start, end, offsets, cap,
	movi	a2, 0x9c	# tmp1593,
	add.n	a2, a14, a2	# tmp1594,, tmp1593
	s32i.n	a11, sp, 32	#,
	s32i.n	a12, sp, 28	#,
	l32i	a11, sp, 240	# %sfp,
	l32i	a12, sp, 248	# %sfp,
	movi	a9, 0x98	# tmp1591,
	add.n	a9, a14, a9	# tmp1592,, tmp1591
	addi	a10, a14, 100	# tmp1590,,
	l32i	a6, sp, 344	# %sfp,
	l32i	a14, sp, 332	# %sfp,
	l32i	a5, sp, 384	# %sfp,
	l32i	a4, sp, 264	# %sfp,
	l32i	a3, sp, 268	# %sfp,
	s32i.n	a2, sp, 0	#, tmp1594
	l32i	a2, sp, 288	# %sfp,
	movi.n	a8, 0	# tmp1587,
	s32i.n	a10, sp, 12	#, tmp1590
	s32i.n	a9, sp, 4	#, tmp1592
	s32i.n	a11, sp, 20	#,
	s32i.n	a12, sp, 16	#,
	s32i.n	a13, sp, 8	#, bits
	s32i.n	a8, sp, 48	#, tmp1587
	s32i.n	a8, sp, 44	#, tmp1587
	s32i.n	a8, sp, 40	#, tmp1587
	s32i	a8, sp, 404	#,
	s32i.n	a14, sp, 24	#,
	s32i.n	a15, sp, 36	#, dec
	call0	clt_compute_allocation		#
# @OPUS@\upstream\celt\celt_decoder.c:1315:    unquant_fine_energy(mode, start, end, oldBandE, fine_quant, dec, C);
	l32i	a14, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1309:    codedBands = clt_compute_allocation(mode, start, end, offsets, cap,
	s32i	a2, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1315:    unquant_fine_energy(mode, start, end, oldBandE, fine_quant, dec, C);
	l32i	a6, sp, 240	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a4, sp, 264	# %sfp,
	l32i	a3, sp, 268	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	s32i.n	a14, sp, 0	#,
	mov.n	a7, a15	#, dec
	call0	unquant_fine_energy		#
# @OPUS@\upstream\celt\celt_decoder.c:1319:       OPUS_MOVE(decode_mem[c], decode_mem[c]+N, DECODE_BUFFER_SIZE-N+overlap);
	l32i	a9, sp, 300	# %sfp,
	l32i	a10, sp, 376	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1318:    c=0; do {
	l32i	a8, sp, 404	#,
	sub	a10, a10, a9	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1319:       OPUS_MOVE(decode_mem[c], decode_mem[c]+N, DECODE_BUFFER_SIZE-N+overlap);
	slli	a14, a9, 2	# _133,,
	s32i	a10, sp, 256	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1318:    c=0; do {
	mov.n	a13, a8	# c, tmp1587
# @OPUS@\upstream\celt\celt_decoder.c:1320:    } while (++c<CC);
	movi.n	a12, 1	# c,
.L263:
# @OPUS@\upstream\celt\celt_decoder.c:1319:       OPUS_MOVE(decode_mem[c], decode_mem[c]+N, DECODE_BUFFER_SIZE-N+overlap);
	l32i	a11, sp, 308	# %sfp,
	slli	a2, a13, 2	# tmp1595, c,
	add.n	a2, a11, a2	# tmp1596,, tmp1595
	l32i	a2, a2, 140	# decode_mem, _132
	l32i	a4, sp, 256	# %sfp,
	add.n	a3, a2, a14	#, _132, _133
	movi.n	a5, 4	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:1320:    } while (++c<CC);
	l32i	a8, sp, 312	# %sfp,
	addi.n	a2, a13, 1	# c, c,
	mov.n	a13, a12	# c, c
	blt	a2, a8, .L263	# c,,
# @OPUS@\upstream\celt\celt_decoder.c:1323:    ALLOC(collapse_masks, C*nbEBands, unsigned char);
	l32i	a9, sp, 272	# %sfp,
	l32i	a10, sp, 280	# %sfp,
	movi.n	a4, 0	#,
	mull	a14, a9, a10	# _138,,
	movi.n	a3, 1	#,
	mov.n	a2, a14	#, _138
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1325:    ALLOC(X, C*N, celt_norm);   /**< Interleaved normalised MDCTs */
	l32i	a11, sp, 272	# %sfp,
	l32i	a8, sp, 300	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1323:    ALLOC(collapse_masks, C*nbEBands, unsigned char);
	s32i	a2, sp, 256	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1325:    ALLOC(X, C*N, celt_norm);   /**< Interleaved normalised MDCTs */
	mull	a2, a11, a8	#,,
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
	l32i	a9, sp, 304	# %sfp,
	l32i	a10, sp, 252	# %sfp,
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i	a8, sp, 272	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1325:    ALLOC(X, C*N, celt_norm);   /**< Interleaved normalised MDCTs */
	mov.n	a13, a2	# X,
	slli	a2, a9, 6	# tmp1601,,
	sub	a2, a2, a10	# _1837, tmp1601,
	addi	a10, a11, 48	# pretmp_1838,,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	bnei	a8, 2, .L264	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i	a11, sp, 300	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	addi.n	a8, a9, -1	# tmp1605,,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i	a9, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	movi.n	a6, 0	# tmp1607,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	slli	a7, a11, 1	# tmp1602,,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	mov.n	a3, a6	#, tmp1607
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i.n	a11, a9, 40	# *st_322(D).arch, _149
	l32i.n	a9, a9, 32	# *st_322(D).disable_inv,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	moveqz	a3, a12, a8	#, c, tmp1605
	mov.n	a8, a3	# tmp1604,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	s32i	a9, sp, 304	# %sfp,
	add.n	a7, a13, a7	# iftmp$21_443, X, tmp1602
	l32i	a5, sp, 232	# dual_stereo, dual_stereo$23_143
	l32i	a4, sp, 236	# intensity, intensity$24_144
	l32i	a3, sp, 180	# balance, balance$25_147
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	beq	a8, a6, .L367	# tmp1604,,
	l32i	a8, sp, 464	# accum,
	movnez	a12, a6, a8	# tmp1610, tmp1607,
	beq	a12, a6, .L367	# tmp1610,,
# @OPUS@\upstream\celt\celt_decoder.c:1337:          , CC==1 && C==2 && !accum && st->downsample==1 ? pcm : NULL, N
	l32i	a12, sp, 244	# %sfp,
	l32i	a8, sp, 364	# %sfp,
	l32i.n	a9, a12, 16	# *st_322(D).downsample, *st_322(D).downsample
	addi.n	a9, a9, -1	# tmp2061, *st_322(D).downsample,
	movnez	a8, a6, a9	#, tmp1607, tmp2061
	mov.n	a9, a8	# iftmp$26_284,
	j	.L265		#
.L367:
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	movi.n	a9, 0	# iftmp$26_284,
.L265:
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i	a12, sp, 344	# %sfp,
	movi.n	a8, 0	# tmp1615,
	s32i.n	a12, sp, 48	#,
	l32i	a12, sp, 260	# %sfp,
	s32i.n	a3, sp, 36	#, balance$25_147
	s32i.n	a12, sp, 44	#,
	l32i	a12, sp, 324	# %sfp,
	s32i.n	a4, sp, 24	#, intensity$24_144
	s32i.n	a12, sp, 28	#,
	l32i	a12, sp, 396	# %sfp,
	s32i.n	a5, sp, 20	#, dual_stereo$23_143
	s32i.n	a12, sp, 16	#,
	l32i	a12, sp, 392	# %sfp,
	s32i	a9, sp, 68	#, iftmp$26_284
	s32i.n	a12, sp, 12	#,
	l32i	a12, sp, 248	# %sfp,
	l32i	a9, sp, 304	# %sfp,
	s32i.n	a12, sp, 8	#,
	l32i	a12, sp, 256	# %sfp,
	l32i	a5, sp, 264	# %sfp,
	s32i.n	a12, sp, 0	#,
	l32i	a4, sp, 268	# %sfp,
	l32i	a12, sp, 300	# %sfp,
	l32i	a3, sp, 288	# %sfp,
	s32i.n	a2, sp, 32	#, _1837
	mov.n	a6, a13	#, X
	mov.n	a2, a8	#, tmp1615
	s32i.n	a10, sp, 52	#, pretmp_1838
	s32i.n	a15, sp, 40	#, dec
	s32i.n	a8, sp, 4	#, tmp1615
	s32i	a12, sp, 72	#,
	s32i	a9, sp, 64	#,
	s32i.n	a11, sp, 60	#, _149
	s32i.n	a8, sp, 56	#, tmp1615
	call0	quant_all_bands		#
# @OPUS@\upstream\celt\celt_decoder.c:1342:    if (anti_collapse_rsv > 0)
	l32i	a10, sp, 252	# %sfp,
	beqz.n	a10, .L266	#,
# @OPUS@\upstream\celt\celt_decoder.c:1344:       anti_collapse_on = ec_dec_bits(dec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_bits		#
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	l32i	a11, sp, 272	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	s32i.n	a11, sp, 8	#,
	s32i.n	a15, sp, 4	#, dec
# @OPUS@\upstream\celt\celt_decoder.c:1344:       anti_collapse_on = ec_dec_bits(dec, 1);
	mov.n	a12, a2	# _155,
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	l32i	a8, sp, 388	# %sfp,
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _530, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	sub	a2, a8, a2	# tmp1618,, MEM[(int *)dec_242 + 20B]
	sub	a2, a2, a3	# tmp1620, tmp1618, _530
	s32i.n	a2, sp, 0	#, tmp1620
	l32i	a7, sp, 332	# %sfp,
	l32i	a6, sp, 240	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a4, sp, 264	# %sfp,
	l32i	a3, sp, 268	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	unquant_energy_finalise		#
# @OPUS@\upstream\celt\celt_decoder.c:1352:    if (anti_collapse_on)
	beqz.n	a12, .L267	# _155,
# @OPUS@\upstream\celt\celt_decoder.c:1353:       anti_collapse(mode, X, collapse_masks, LM, C, N,
	l32i	a9, sp, 244	# %sfp,
	l32i	a10, sp, 248	# %sfp,
	l32i.n	a2, a9, 48	# *st_322(D).rng, *st_322(D).rng
	l32i.n	a3, a9, 40	# *st_322(D).arch, *st_322(D).arch
	l32i	a11, sp, 348	# %sfp,
	s32i.n	a10, sp, 20	#,
	l32i	a12, sp, 328	# %sfp,
	l32i	a8, sp, 276	# %sfp,
	l32i	a9, sp, 264	# %sfp,
	l32i	a10, sp, 268	# %sfp,
	s32i.n	a2, sp, 24	#, *st_322(D).rng
	l32i	a7, sp, 300	# %sfp,
	l32i	a6, sp, 272	# %sfp,
	l32i	a5, sp, 260	# %sfp,
	l32i	a4, sp, 256	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	s32i.n	a3, sp, 28	#, *st_322(D).arch
	s32i.n	a11, sp, 16	#,
	s32i.n	a12, sp, 12	#,
	s32i.n	a8, sp, 8	#,
	s32i.n	a9, sp, 4	#,
	s32i.n	a10, sp, 0	#,
	mov.n	a3, a13	#, X
	call0	anti_collapse		#
.L267:
# @OPUS@\upstream\celt\celt_decoder.c:1356:    if (silence)
	l32i	a11, sp, 368	# %sfp,
	bnez.n	a11, .L268	#,
.L271:
# @OPUS@\upstream\celt\celt_decoder.c:1361:    if (st->prefilter_and_fold) {
	l32i	a12, sp, 244	# %sfp,
	l32i	a2, a12, 88	# *st_322(D).prefilter_and_fold, *st_322(D).prefilter_and_fold
	beqz.n	a2, .L270	# *st_322(D).prefilter_and_fold,
	j	.L269		#
.L268:
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	blti	a14, 1, .L271	# _138,,
	l32i	a8, sp, 244	# %sfp,
	addi.n	a2, a14, -1	# tmp1628, _138,
	extui	a5, a8, 1, 1	# prolog_loop_niters$232,,,
	bltui	a2, 6, .L369	# tmp1628,,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	movi.n	a6, 0	# i,
	beq	a5, a6, .L273	# prolog_loop_niters$232,,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	l32r	a4, .LC23	#, tmp1972
	l32i	a9, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	movi.n	a6, 1	# i,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a9, 0	# *oldBandE_337, tmp1972
.L273:
	addi	a2, a5, 50	# tmp1630, prolog_loop_niters$232,
	l32i	a10, sp, 284	# %sfp,
	sub	a5, a14, a5	# niters$233, _138, prolog_loop_niters$232
	slli	a2, a2, 1	# tmp1631, tmp1630,
	l32i	a11, sp, 244	# %sfp,
	add.n	a2, a2, a10	# tmp1632, tmp1631,
	srli	a3, a5, 1	# bnd$234, niters$233,
	add.n	a2, a11, a2	# ivtmp$382,, tmp1632
	slli	a3, a3, 2	# tmp1634, bnd$234,
	l32r	a4, .LC24	#, tmp1973
	add.n	a3, a3, a2	# _529, tmp1634, ivtmp$382
.L274:
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s32i.n	a4, a2, 0	# MEM[base: _534, offset: 0B], tmp1973
	addi.n	a2, a2, 4	# ivtmp$382, ivtmp$382,
	bne	a3, a2, .L274	# _529, ivtmp$382,
	movi.n	a2, -2	# tmp1636,
	and	a2, a5, a2	# niters_vector_mult_vf$235, niters$233, tmp1636
	add.n	a3, a2, a6	# tmp$236, niters_vector_mult_vf$235, i
	bne	a2, a5, .L272	# niters_vector_mult_vf$235, niters$233,
	j	.L271		#
.L369:
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	movi.n	a3, 0	# tmp$236,
.L272:
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	l32i	a12, sp, 276	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	slli	a2, a3, 1	# _2104, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	l32r	a4, .LC23	#, tmp1972
	add.n	a2, a12, a2	# tmp1637,, _2104
	s16i	a4, a2, 0	# *_159, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	addi.n	a5, a3, 1	# i, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	bge	a5, a14, .L271	# i, _138,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a2, 2	# *_226, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	addi.n	a5, a3, 2	# i, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	bge	a5, a14, .L271	# i, _138,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a2, 4	# *_233, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	addi.n	a5, a3, 3	# i, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	bge	a5, a14, .L271	# i, _138,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a2, 6	# *_1696, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	addi.n	a5, a3, 4	# i, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	bge	a5, a14, .L271	# i, _138,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a2, 8	# *_77, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	addi.n	a3, a3, 5	# i, tmp$236,
# @OPUS@\upstream\celt\celt_decoder.c:1358:       for (i=0;i<C*nbEBands;i++)
	bge	a3, a14, .L271	# i, _138,
# @OPUS@\upstream\celt\celt_decoder.c:1359:          oldBandE[i] = -QCONST16(28.f,DB_SHIFT);
	s16i	a4, a2, 10	# *_1436, tmp1972
	j	.L271		#
.L269:
# @OPUS@\upstream\celt\celt_decoder.c:1362:       prefilter_and_fold(st, N);
	l32i	a3, sp, 300	# %sfp,
	mov.n	a2, a12	#,
	call0	prefilter_and_fold		#
.L270:
# @OPUS@\upstream\celt\celt_decoder.c:1365:    celt_synthesis(mode, X, out_syn, oldBandE, start, effEnd,
	l32i	a14, sp, 244	# %sfp,
	l32i	a8, sp, 368	# %sfp,
	l32i.n	a2, a14, 16	# *st_322(D).downsample, *st_322(D).downsample
	l32i.n	a3, a14, 40	# *st_322(D).arch, *st_322(D).arch
	l32i	a9, sp, 260	# %sfp,
	l32i	a11, sp, 312	# %sfp,
	l32i	a14, sp, 272	# %sfp,
	s32i.n	a8, sp, 20	#,
	l32i	a10, sp, 292	# %sfp,
	l32i	a8, sp, 308	# %sfp,
	s32i.n	a2, sp, 16	#, *st_322(D).downsample
	movi	a12, 0x84	# tmp1659,
	l32i	a7, sp, 340	# %sfp,
	l32i	a6, sp, 268	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	s32i.n	a3, sp, 24	#, *st_322(D).arch
	s32i.n	a9, sp, 12	#,
	s32i.n	a11, sp, 4	#,
	s32i.n	a14, sp, 0	#,
	mov.n	a3, a13	#, X
	s32i.n	a10, sp, 8	#,
	add.n	a4, a8, a12	#,, tmp1659
	call0	celt_synthesis		#
# @OPUS@\upstream\celt\celt_decoder.c:1370:    c=0; do {
	movi.n	a9, 0	# c,
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	l32i	a11, sp, 288	# %sfp, mode
	l32i	a13, sp, 244	# %sfp, st
	s32i	a15, sp, 240	# %sfp, dec
# @OPUS@\upstream\celt\celt_decoder.c:1371:       st->postfilter_period=IMAX(st->postfilter_period, COMBFILTER_MINPERIOD);
	movi.n	a14, 0xf	# tmp1671,
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	mov.n	a15, a9	# c, c
.L280:
	l32i	a9, sp, 308	# %sfp,
	slli	a8, a15, 2	# tmp1681, c,
# @OPUS@\upstream\celt\celt_decoder.c:1371:       st->postfilter_period=IMAX(st->postfilter_period, COMBFILTER_MINPERIOD);
	l32i	a5, a13, 68	# *st_322(D).postfilter_period, _166
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	add.n	a8, a9, a8	# tmp1682,, tmp1681
	add.n	a8, a8, a12	# tmp1684, tmp1682, tmp1683
# @OPUS@\upstream\celt\celt_decoder.c:1371:       st->postfilter_period=IMAX(st->postfilter_period, COMBFILTER_MINPERIOD);
	bge	a5, a14, .L277	# _166, tmp1671,
	mov.n	a5, a14	# _166, tmp1671
.L277:
# @OPUS@\upstream\celt\celt_decoder.c:1372:       st->postfilter_period_old=IMAX(st->postfilter_period_old, COMBFILTER_MINPERIOD);
	l32i	a10, a13, 72	# *st_322(D).postfilter_period_old, _168
# @OPUS@\upstream\celt\celt_decoder.c:1371:       st->postfilter_period=IMAX(st->postfilter_period, COMBFILTER_MINPERIOD);
	s32i	a5, a13, 68	# *st_322(D).postfilter_period, _166
# @OPUS@\upstream\celt\celt_decoder.c:1372:       st->postfilter_period_old=IMAX(st->postfilter_period_old, COMBFILTER_MINPERIOD);
	bge	a10, a14, .L278	# _168, tmp1671,
	mov.n	a10, a14	# _168, tmp1671
.L278:
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	l32i.n	a2, a13, 40	# *st_322(D).arch, *st_322(D).arch
	l32i	a9, sp, 316	# %sfp,
	s32i.n	a2, sp, 20	#, *st_322(D).arch
	s32i.n	a9, sp, 16	#,
	l32i.n	a7, a11, 52	# mode_328->window, mode_328->window
	l32i	a6, a13, 80	# *st_322(D).postfilter_tapset, *st_322(D).postfilter_tapset
	l32i	a4, a13, 84	# *st_322(D).postfilter_tapset_old, *st_322(D).postfilter_tapset_old
	l16si	a3, a13, 76	# *st_322(D).postfilter_gain, tmp1692
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	l32i.n	a2, a8, 0	# out_syn, _169
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	s32i.n	a4, sp, 4	#, *st_322(D).postfilter_tapset_old
	s32i.n	a3, sp, 0	#, tmp1692
	s32i.n	a7, sp, 12	#, mode_328->window
	s32i.n	a6, sp, 8	#, *st_322(D).postfilter_tapset
	l32i.n	a6, a11, 36	# mode_328->shortMdctSize,
	l16si	a7, a13, 78	# *st_322(D).postfilter_gain_old,
# @OPUS@\upstream\celt\celt_decoder.c:1372:       st->postfilter_period_old=IMAX(st->postfilter_period_old, COMBFILTER_MINPERIOD);
	s32i	a10, a13, 72	# *st_322(D).postfilter_period_old, _168
# @OPUS@\upstream\celt\celt_decoder.c:1373:       comb_filter(out_syn[c], out_syn[c], st->postfilter_period_old, st->postfilter_period, mode->shortMdctSize,
	mov.n	a4, a10	#, _168
	mov.n	a3, a2	#, _169
	s32i	a8, sp, 404	#,
	s32i	a11, sp, 408	#,
	call0	comb_filter		#
# @OPUS@\upstream\celt\celt_decoder.c:1376:       if (LM!=0)
	l32i	a10, sp, 260	# %sfp,
	l32i	a8, sp, 404	#,
	l32i	a11, sp, 408	#,
	beqz.n	a10, .L279	#,
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	l32i.n	a4, a8, 0	# out_syn, tmp1700
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	l32i.n	a2, a13, 40	# *st_322(D).arch, *st_322(D).arch
	l32i	a8, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	l32i.n	a6, a11, 36	# mode_328->shortMdctSize, _180
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	s32i.n	a2, sp, 20	#, *st_322(D).arch
	s32i.n	a8, sp, 16	#,
	l32i.n	a5, a11, 52	# mode_328->window, mode_328->window
	l32i	a3, a13, 80	# *st_322(D).postfilter_tapset, *st_322(D).postfilter_tapset
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	slli	a2, a6, 2	# tmp1699, _180,
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	l32i	a9, sp, 356	# %sfp,
	l32i	a10, sp, 372	# %sfp,
	l32i	a8, sp, 300	# %sfp,
	l16si	a7, a13, 76	# *st_322(D).postfilter_gain,
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	add.n	a2, a4, a2	# _183, tmp1700, tmp1699
# @OPUS@\upstream\celt\celt_decoder.c:1377:          comb_filter(out_syn[c]+mode->shortMdctSize, out_syn[c]+mode->shortMdctSize, st->postfilter_period, postfilter_pitch, N-mode->shortMdctSize,
	l32i	a4, a13, 68	# *st_322(D).postfilter_period,
	s32i.n	a5, sp, 12	#, mode_328->window
	l32i	a5, sp, 360	# %sfp,
	s32i.n	a3, sp, 4	#, *st_322(D).postfilter_tapset
	s32i.n	a9, sp, 8	#,
	s32i.n	a10, sp, 0	#,
	sub	a6, a8, a6	#,, _180
	mov.n	a3, a2	#, _183
	call0	comb_filter		#
	l32i	a11, sp, 408	#,
.L279:
# @OPUS@\upstream\celt\celt_decoder.c:1381:    } while (++c<CC);
	l32i	a9, sp, 312	# %sfp,
	addi.n	a2, a15, 1	# c, c,
	movi.n	a15, 1	# c,
	blt	a2, a9, .L280	# c,,
# @OPUS@\upstream\celt\celt_decoder.c:1383:    st->postfilter_period_old = st->postfilter_period;
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1386:    st->postfilter_period = postfilter_pitch;
	l32i	a11, sp, 360	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1383:    st->postfilter_period_old = st->postfilter_period;
	l32i	a4, a10, 68	# *st_322(D).postfilter_period, *st_322(D).postfilter_period
# @OPUS@\upstream\celt\celt_decoder.c:1384:    st->postfilter_gain_old = st->postfilter_gain;
	l16ui	a3, a10, 76	# *st_322(D).postfilter_gain,
# @OPUS@\upstream\celt\celt_decoder.c:1385:    st->postfilter_tapset_old = st->postfilter_tapset;
	l32i	a2, a10, 80	# *st_322(D).postfilter_tapset, *st_322(D).postfilter_tapset
# @OPUS@\upstream\celt\celt_decoder.c:1387:    st->postfilter_gain = postfilter_gain;
	l32i	a12, sp, 372	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1388:    st->postfilter_tapset = postfilter_tapset;
	l32i	a14, sp, 356	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1389:    if (LM!=0)
	l32i	a8, sp, 260	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1383:    st->postfilter_period_old = st->postfilter_period;
	s32i	a4, a10, 72	# *st_322(D).postfilter_period_old, *st_322(D).postfilter_period
# @OPUS@\upstream\celt\celt_decoder.c:1384:    st->postfilter_gain_old = st->postfilter_gain;
	s16i	a3, a10, 78	# *st_322(D).postfilter_gain_old, *st_322(D).postfilter_gain
# @OPUS@\upstream\celt\celt_decoder.c:1385:    st->postfilter_tapset_old = st->postfilter_tapset;
	s32i	a2, a10, 84	# *st_322(D).postfilter_tapset_old, *st_322(D).postfilter_tapset
# @OPUS@\upstream\celt\celt_decoder.c:1386:    st->postfilter_period = postfilter_pitch;
	s32i	a11, a10, 68	# *st_322(D).postfilter_period,
# @OPUS@\upstream\celt\celt_decoder.c:1387:    st->postfilter_gain = postfilter_gain;
	s16i	a12, a10, 76	# *st_322(D).postfilter_gain,
# @OPUS@\upstream\celt\celt_decoder.c:1388:    st->postfilter_tapset = postfilter_tapset;
	s32i	a14, a10, 80	# *st_322(D).postfilter_tapset,
	l32i	a15, sp, 240	# %sfp, dec
# @OPUS@\upstream\celt\celt_decoder.c:1389:    if (LM!=0)
	beqz.n	a8, .L281	#,
# @OPUS@\upstream\celt\celt_decoder.c:1391:       st->postfilter_period_old = st->postfilter_period;
	s32i	a11, a10, 72	# *st_322(D).postfilter_period_old,
# @OPUS@\upstream\celt\celt_decoder.c:1392:       st->postfilter_gain_old = st->postfilter_gain;
	s16i	a12, a10, 78	# *st_322(D).postfilter_gain_old,
# @OPUS@\upstream\celt\celt_decoder.c:1393:       st->postfilter_tapset_old = st->postfilter_tapset;
	s32i	a14, a10, 84	# *st_322(D).postfilter_tapset_old,
.L281:
# @OPUS@\upstream\celt\celt_decoder.c:1396:    if (C==1)
	l32i	a9, sp, 272	# %sfp,
	bnei	a9, 1, .L282	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1397:       OPUS_COPY(&oldBandE[nbEBands], oldBandE, nbEBands);
	l32i	a3, sp, 276	# %sfp,
	l32i	a10, sp, 336	# %sfp,
	l32i	a4, sp, 280	# %sfp,
	movi.n	a5, 2	#,
	add.n	a2, a3, a10	#,,
	call0	yoradio_opus_copy		#
.L282:
# @OPUS@\upstream\celt\celt_decoder.c:1399:    if (!isTransient)
	l32i	a11, sp, 292	# %sfp,
	beqz.n	a11, .L283	#,
# @OPUS@\upstream\celt\celt_decoder.c:1404:       for (i=0;i<2*nbEBands;i++)
	l32i	a12, sp, 336	# %sfp,
	l32i	a3, sp, 276	# %sfp, ivtmp$375
	l32i	a2, sp, 328	# %sfp, ivtmp$376
	l32i	a8, sp, 348	# %sfp, _586
	bgei	a12, 1, .L290	#,,
.L288:
	l32i	a8, sp, 264	# %sfp,
	l32i	a14, sp, 280	# %sfp,
	l32i	a12, sp, 284	# %sfp,
	sub	a14, a14, a8	#,,
	l32i	a9, sp, 296	# %sfp,
	l32i	a10, sp, 268	# %sfp,
	movi.n	a6, -2	# tmp1714,
	and	a11, a14, a6	#,, tmp1714
	addi	a12, a12, 100	#,,
	srli	a5, a14, 1	# bnd$208,,
	s32i	a14, sp, 256	# %sfp,
	l32i	a14, sp, 284	# %sfp,
	slli	a2, a9, 1	# _1992,,
	and	a13, a10, a6	# niters_vector_mult_vf$222,, tmp1714
	srli	a4, a10, 1	# bnd$221,,
	add.n	a9, a9, a12	#,,
	l32i	a10, sp, 296	# %sfp,
	s32i	a12, sp, 272	# %sfp,
	l32i	a12, sp, 284	# %sfp,
	addi	a14, a14, 104	#,,
	addi	a3, a2, 100	# tmp2537, _1992,
	slli	a4, a4, 2	#, bnd$221,
	addi	a2, a2, 104	# tmp2539, _1992,
	add.n	a3, a3, a12	#, tmp2537,
	add.n	a2, a2, a12	#, tmp2539,
	s32i	a4, sp, 336	# %sfp,
	slli	a5, a5, 2	#, bnd$208,
	add.n	a4, a11, a8	#,,
	add.n	a10, a10, a14	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1370:    c=0; do {
	movi.n	a8, 2	#,
	s32i	a11, sp, 324	# %sfp,
	l32i	a12, sp, 328	# %sfp, oldLogE
	s32i	a13, sp, 240	# %sfp, niters_vector_mult_vf$222
	s32i	a15, sp, 328	# %sfp, dec
	s32i	a14, sp, 292	# %sfp,
	s32i	a5, sp, 340	# %sfp,
	s32i	a4, sp, 248	# %sfp,
	s32i	a8, sp, 316	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1414:    c=0; do
	movi.n	a11, 0	# c,
	s32i	a9, sp, 304	# %sfp,
	s32i	a10, sp, 296	# %sfp,
	s32i	a3, sp, 252	# %sfp,
	s32i	a2, sp, 260	# %sfp,
	l32i	a13, sp, 276	# %sfp, oldBandE
	l32i	a15, sp, 348	# %sfp, _586
	j	.L285		#
.L283:
# @OPUS@\upstream\celt\celt_decoder.c:1401:       OPUS_COPY(oldLogE2, oldLogE, 2*nbEBands);
	l32i	a4, sp, 336	# %sfp,
	l32i	a3, sp, 328	# %sfp,
	l32i	a2, sp, 348	# %sfp,
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:1402:       OPUS_COPY(oldLogE, oldBandE, 2*nbEBands);
	l32i	a3, sp, 276	# %sfp,
	l32i	a2, sp, 328	# %sfp,
	l32i	a4, sp, 336	# %sfp,
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	l32i	a14, sp, 244	# %sfp,
	l32i	a8, sp, 400	# %sfp,
	l32i.n	a2, a14, 60	# *st_322(D).loss_duration, *st_322(D).loss_duration
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	movi	a3, 0xa0	# tmp1723,
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	add.n	a2, a8, a2	# tmp1717,, *st_322(D).loss_duration
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	bge	a3, a2, .L286	# tmp1723, tmp1717,
	mov.n	a2, a3	# tmp1717, tmp1723
.L286:
# @OPUS@\upstream\celt\celt_decoder.c:1411:    for (i=0;i<2*nbEBands;i++)
	l32i	a9, sp, 336	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	slli	a2, a2, 16	# tmp1724, tmp1717,
	srai	a7, a2, 16	# max_background_increase, tmp1724,
# @OPUS@\upstream\celt\celt_decoder.c:1411:    for (i=0;i<2*nbEBands;i++)
	bgei	a9, 1, .L287	#,,
	j	.L288		#
.L290:
# @OPUS@\upstream\celt\celt_decoder.c:1405:          oldLogE[i] = MIN16(oldLogE[i], oldBandE[i]);
	l16si	a5, a3, 0	# MEM[base: _713, offset: 0B], tmp1727
	l16si	a6, a2, 0	# MEM[base: _712, offset: 0B], tmp1729
	l16ui	a4, a3, 0	# MEM[base: _713, offset: 0B],
	l16ui	a7, a2, 0	# MEM[base: _712, offset: 0B],
	bge	a6, a5, .L289	# tmp1729, tmp1727,
	mov.n	a4, a7	# MEM[base: _713, offset: 0B], MEM[base: _712, offset: 0B]
.L289:
# @OPUS@\upstream\celt\celt_decoder.c:1405:          oldLogE[i] = MIN16(oldLogE[i], oldBandE[i]);
	s16i	a4, a2, 0	# MEM[base: _712, offset: 0B], MEM[base: _713, offset: 0B]
	addi.n	a2, a2, 2	# ivtmp$376, ivtmp$376,
	addi.n	a3, a3, 2	# ivtmp$375, ivtmp$375,
# @OPUS@\upstream\celt\celt_decoder.c:1404:       for (i=0;i<2*nbEBands;i++)
	bne	a8, a2, .L290	# _586, ivtmp$376,
	j	.L472		#
.L287:
	l32i	a10, sp, 348	# %sfp,
	l32i	a11, sp, 296	# %sfp,
	l32i	a5, sp, 276	# %sfp, ivtmp$370
# @OPUS@\upstream\celt\celt_decoder.c:1370:    c=0; do {
	l32i	a8, sp, 336	# %sfp, _1847
	add.n	a3, a10, a11	# ivtmp$371,,
	movi.n	a4, 0	# i,
.L293:
# @OPUS@\upstream\celt\celt_decoder.c:1412:       backgroundLogE[i] = MIN16(backgroundLogE[i] + max_background_increase, oldBandE[i]);
	l16si	a2, a3, 0	# MEM[base: _799, offset: 0B], tmp1732
	l16si	a6, a5, 0	# MEM[base: _854, offset: 0B], tmp1736
	add.n	a2, a2, a7	# tmp1731, tmp1732, max_background_increase
# @OPUS@\upstream\celt\celt_decoder.c:1411:    for (i=0;i<2*nbEBands;i++)
	addi.n	a4, a4, 1	# i, i,
# @OPUS@\upstream\celt\celt_decoder.c:1412:       backgroundLogE[i] = MIN16(backgroundLogE[i] + max_background_increase, oldBandE[i]);
	bge	a6, a2, .L292	# tmp1736, tmp1731,
	mov.n	a2, a6	# tmp1731, tmp1736
.L292:
# @OPUS@\upstream\celt\celt_decoder.c:1412:       backgroundLogE[i] = MIN16(backgroundLogE[i] + max_background_increase, oldBandE[i]);
	s16i	a2, a3, 0	# MEM[base: _799, offset: 0B], tmp1731
	addi.n	a5, a5, 2	# ivtmp$370, ivtmp$370,
	addi.n	a3, a3, 2	# ivtmp$371, ivtmp$371,
# @OPUS@\upstream\celt\celt_decoder.c:1411:    for (i=0;i<2*nbEBands;i++)
	blt	a4, a8, .L293	# i, _1847,
	j	.L288		#
.L371:
	s32i	a11, sp, 316	# %sfp, c
.L285:
# @OPUS@\upstream\celt\celt_decoder.c:1416:       for (i=0;i<start;i++)
	l32i	a14, sp, 268	# %sfp,
	bgei	a14, 1, .L294	#,,
.L307:
# @OPUS@\upstream\celt\celt_decoder.c:1421:       for (i=end;i<nbEBands;i++)
	l32i	a8, sp, 264	# %sfp,
	l32i	a9, sp, 280	# %sfp,
	blt	a8, a9, .L295	#,,
	j	.L296		#
.L294:
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	l32i	a10, sp, 280	# %sfp,
	l32i	a7, sp, 296	# %sfp,
	mull	a2, a11, a10	# _223, c,
	movi	a14, 0x11c	#,
	slli	a6, a2, 1	# _1634, _223,
	movi.n	a3, 1	#,
	add.n	a14, a14, sp	#,,
	s8i	a3, a14, 0	# %sfp,
	l32i	a4, sp, 272	# %sfp,
	l32i	a10, sp, 252	# %sfp,
	add.n	a14, a7, a6	# _1590,, _1634
	l32i	a7, sp, 292	# %sfp,
	l32i	a5, sp, 304	# %sfp,
	add.n	a8, a6, a4	# _1632, _1634,
	add.n	a7, a6, a7	#, _1634,
	add.n	a4, a10, a6	# _1556,, _1634
	l32i	a10, sp, 244	# %sfp,
	add.n	a9, a5, a6	# _1616,, _1634
	s32i	a7, sp, 276	# %sfp,
	add.n	a5, a10, a8	# vectp$217,, _1632
	add.n	a3, a10, a9	# vectp$219,, _1616
	bge	a4, a14, .L298	# _1556, _1590,
	movi	a10, 0x11c	#,
	movi.n	a7, 0	#,
	add.n	a10, a10, sp	#,,
	s8i	a7, a10, 0	# %sfp,
.L298:
	l32i	a7, sp, 260	# %sfp,
	add.n	a10, a7, a6	# tmp1750,, _1634
	movi.n	a7, 1	# tmp1751,
	bge	a9, a10, .L299	# _1616, tmp1750,
	movi.n	a7, 0	# tmp1751,
.L299:
	l32i	a10, sp, 260	# %sfp,
	add.n	a10, a10, a6	#,, _1634
	s32i	a10, sp, 344	# %sfp,
	movi	a10, 0x11c	#,
	add.n	a10, a10, sp	#,,
	l8ui	a10, a10, 0	# %sfp,
	or	a7, a10, a7	#,, tmp1751
	s32i	a7, sp, 284	# %sfp,
	movi	a7, 0x14c	#,
	movi.n	a10, 1	#,
	add.n	a7, a7, sp	#,,
	s8i	a10, a7, 0	# %sfp,
	l32i	a10, sp, 344	# %sfp, tmp1756
	bge	a8, a10, .L300	# _1632, tmp1756,
	movi.n	a10, 0	#,
	s8i	a10, a7, 0	# %sfp,
.L300:
	l32i	a7, sp, 276	# %sfp,
	movi.n	a10, 1	# tmp1759,
	bge	a4, a7, .L301	# _1556,,
	movi.n	a10, 0	# tmp1759,
.L301:
	movi	a7, 0x14c	#,
	add.n	a7, a7, sp	#,,
	l8ui	a7, a7, 0	# %sfp,
	or	a10, a7, a10	# tmp1761,, tmp1759
	l32i	a7, sp, 268	# %sfp,
	addi.n	a7, a7, -1	#,,
	s32i	a7, sp, 332	# %sfp,
	l32i	a7, sp, 284	# %sfp,
	and	a10, a7, a10	#,, tmp1761
	s32i	a10, sp, 284	# %sfp,
	movi	a10, 0x158	#,
	movi.n	a7, 1	#,
	add.n	a10, a10, sp	#,,
	s8i	a7, a10, 0	# %sfp,
	l32i	a7, sp, 332	# %sfp,
	movi.n	a10, 0xb	#,
	bltu	a10, a7, .L302	#,,
	movi	a10, 0x158	#,
	movi.n	a7, 0	#,
	add.n	a10, a10, sp	#,,
	s8i	a7, a10, 0	# %sfp,
.L302:
	movi	a10, 0x158	#,
	add.n	a10, a10, sp	#,,
	l32i	a7, sp, 284	# %sfp,
	l8ui	a10, a10, 0	# %sfp,
	and	a10, a7, a10	#,,
	l32i	a7, sp, 276	# %sfp,
	s32i	a10, sp, 284	# %sfp,
	movi.n	a10, 1	# tmp1771,
	bge	a9, a7, .L303	# _1616,,
	movi.n	a10, 0	# tmp1771,
.L303:
	movi.n	a9, 1	# tmp1773,
	bge	a8, a14, .L304	# _1632, _1590,
	movi.n	a9, 0	# tmp1773,
.L304:
	l32i	a8, sp, 284	# %sfp,
	or	a10, a10, a9	# tmp1775, tmp1771, tmp1773
	and	a7, a8, a10	# tmp1778,, tmp1775
	bbci	a7, 0, .L297	# tmp1778,,
	l32i	a9, sp, 252	# %sfp,
	l32i	a10, sp, 244	# %sfp,
	add.n	a7, a9, a6	# tmp1783,, _1634
	add.n	a7, a10, a7	# vectp$218,, tmp1783
	or	a7, a5, a7	# tmp1785, vectp$217, vectp$218
	or	a7, a3, a7	# tmp1786, vectp$219, tmp1785
	extui	a7, a7, 0, 2	# tmp1787, tmp1786,
	bnez.n	a7, .L297	# tmp1787,
	l32i	a14, sp, 336	# %sfp,
	l32r	a6, .LC24	#, tmp1973
	add.n	a4, a10, a4	# ivtmp$361,, _1556
	add.n	a8, a3, a14	# _943, ivtmp$359,
.L305:
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	s32i.n	a7, a5, 0	# MEM[base: _1004, offset: 0B], tmp1793
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a6, a4, 0	# MEM[base: _999, offset: 0B], tmp1973
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a6, a3, 0	# MEM[base: _986, offset: 0B], tmp1973
	addi.n	a3, a3, 4	# ivtmp$359, ivtmp$359,
	addi.n	a4, a4, 4	# ivtmp$361, ivtmp$361,
	addi.n	a5, a5, 4	# ivtmp$363, ivtmp$363,
	bne	a8, a3, .L305	# _943, ivtmp$359,
	l32i	a3, sp, 240	# %sfp,
	l32i	a8, sp, 268	# %sfp,
	beq	a3, a8, .L307	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	add.n	a2, a2, a3	# tmp1796, _223,
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	slli	a2, a2, 1	# _1507, tmp1796,
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	add.n	a4, a13, a2	# tmp1797, oldBandE, _1507
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	l32r	a3, .LC23	#, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	s16i	a7, a4, 0	# *_1506, tmp1793
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	add.n	a4, a15, a2	# tmp1799, _586, _1507
	s16i	a3, a4, 0	# *_1504, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	add.n	a2, a12, a2	# tmp1801, oldLogE, _1507
	s16i	a3, a2, 0	# *_1502, tmp1972
	j	.L307		#
.L297:
	l32i	a9, sp, 268	# %sfp,
	l32r	a3, .LC23	#, tmp1972
	add.n	a2, a9, a2	# tmp1803,, _223
	slli	a2, a2, 1	# tmp1804, tmp1803,
	add.n	a4, a13, a6	# ivtmp$350, oldBandE, _1634
	add.n	a5, a15, a6	# ivtmp$351, _586, _1634
	add.n	a2, a13, a2	# _1113, oldBandE, tmp1804
	add.n	a6, a12, a6	# ivtmp$352, oldLogE, _1634
# @OPUS@\upstream\celt\celt_decoder.c:1418:          oldBandE[c*nbEBands+i]=0;
	movi.n	a7, 0	# tmp1805,
.L309:
	s16i	a7, a4, 0	# MEM[base: _1169, offset: 0B], tmp1805
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s16i	a3, a5, 0	# MEM[base: _1167, offset: 0B], tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1419:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s16i	a3, a6, 0	# MEM[base: _1165, offset: 0B], tmp1972
	addi.n	a4, a4, 2	# ivtmp$350, ivtmp$350,
	addi.n	a5, a5, 2	# ivtmp$351, ivtmp$351,
	addi.n	a6, a6, 2	# ivtmp$352, ivtmp$352,
# @OPUS@\upstream\celt\celt_decoder.c:1416:       for (i=0;i<start;i++)
	bne	a2, a4, .L309	# _1113, ivtmp$350,
	j	.L307		#
.L296:
# @OPUS@\upstream\celt\celt_decoder.c:1426:    } while (++c<2);
	l32i	a10, sp, 316	# %sfp,
	movi.n	a11, 1	# c,
	bne	a10, a11, .L371	#,,
	j	.L485		#
.L295:
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	mull	a11, a11, a9	# _230, c, tmp14
	l32i	a6, sp, 292	# %sfp,
	add.n	a5, a11, a8	# tmp1808, _230,
	l32i	a9, sp, 272	# %sfp,
	slli	a5, a5, 1	# _1873, tmp1808,
	l32i	a10, sp, 304	# %sfp,
	l32i	a2, sp, 296	# %sfp,
	l32i	a4, sp, 252	# %sfp,
	add.n	a7, a9, a5	# _1866,, _1873
	add.n	a6, a6, a5	#,, _1873
	l32i	a9, sp, 244	# %sfp,
	add.n	a8, a10, a5	# _1839,, _1873
	add.n	a3, a4, a5	# _1743,, _1873
	add.n	a10, a2, a5	# _1782,, _1873
	s32i	a6, sp, 276	# %sfp,
	movi.n	a14, 1	# tmp1816,
	add.n	a4, a9, a7	# vectp$204,, _1866
	add.n	a2, a9, a8	# vectp$206,, _1839
	bge	a3, a10, .L313	# _1743, _1782,
	movi.n	a14, 0	# tmp1816,
.L313:
	l32i	a6, sp, 260	# %sfp,
	add.n	a9, a6, a5	# tmp1820,, _1873
	movi.n	a6, 1	# tmp1821,
	bge	a8, a9, .L314	# _1839, tmp1820,
	movi.n	a6, 0	# tmp1821,
.L314:
	l32i	a9, sp, 260	# %sfp,
	or	a6, a14, a6	#, tmp1816, tmp1821
	add.n	a9, a9, a5	#,, _1873
	s32i	a6, sp, 284	# %sfp,
	s32i	a9, sp, 332	# %sfp,
	movi.n	a6, 1	# tmp1827,
	bge	a7, a9, .L315	# _1866, tmp1826,
	movi.n	a6, 0	# tmp1827,
.L315:
	l32i	a14, sp, 276	# %sfp,
	movi.n	a9, 1	# tmp1829,
	bge	a3, a14, .L316	# _1743,,
	movi.n	a9, 0	# tmp1829,
.L316:
	l32i	a14, sp, 256	# %sfp,
	or	a6, a6, a9	# tmp1831, tmp1827, tmp1829
	addi.n	a9, a14, -1	# tmp1835,,
	l32i	a14, sp, 284	# %sfp,
	and	a6, a14, a6	#,, tmp1831
	s32i	a6, sp, 284	# %sfp,
	movi.n	a6, 0xb	#,
	movi.n	a14, 1	# tmp1836,
	bltu	a6, a9, .L317	#, tmp1835,
	movi.n	a14, 0	# tmp1836,
.L317:
	l32i	a9, sp, 284	# %sfp,
	and	a6, a9, a14	# tmp1840,, tmp1836
	l32i	a14, sp, 276	# %sfp,
	movi.n	a9, 1	# tmp1841,
	bge	a8, a14, .L318	# _1839,,
	movi.n	a9, 0	# tmp1841,
.L318:
	movi.n	a8, 1	# tmp1843,
	bge	a7, a10, .L319	# _1866, _1782,
	movi.n	a8, 0	# tmp1843,
.L319:
	or	a9, a9, a8	# tmp1845, tmp1841, tmp1843
	and	a6, a6, a9	# tmp1848, tmp1840, tmp1845
	bbci	a6, 0, .L312	# tmp1848,,
	l32i	a7, sp, 252	# %sfp,
	l32i	a8, sp, 244	# %sfp,
	add.n	a6, a7, a5	# tmp1853,, _1873
	add.n	a6, a8, a6	# vectp$205,, tmp1853
	or	a6, a4, a6	# tmp1855, vectp$204, vectp$205
	or	a6, a2, a6	# tmp1856, vectp$206, tmp1855
	extui	a6, a6, 0, 2	# tmp1857, tmp1856,
	bnez.n	a6, .L312	# tmp1857,
	l32i	a9, sp, 340	# %sfp,
	l32r	a6, .LC24	#, tmp1973
	add.n	a3, a8, a3	# ivtmp$345,, _1743
	add.n	a7, a2, a9	# _1249, ivtmp$343,
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	movi.n	a5, 0	# tmp1863,
.L320:
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	s32i.n	a5, a4, 0	# MEM[base: _1255, offset: 0B], tmp1863
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a6, a3, 0	# MEM[base: _1253, offset: 0B], tmp1973
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a6, a2, 0	# MEM[base: _1252, offset: 0B], tmp1973
	addi.n	a2, a2, 4	# ivtmp$343, ivtmp$343,
	addi.n	a3, a3, 4	# ivtmp$345, ivtmp$345,
	addi.n	a4, a4, 4	# ivtmp$347, ivtmp$347,
	bne	a7, a2, .L320	# _1249, ivtmp$343,
	l32i	a10, sp, 324	# %sfp,
	l32i	a14, sp, 256	# %sfp,
	beq	a10, a14, .L296	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	l32i	a2, sp, 248	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	l32r	a3, .LC23	#, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	add.n	a11, a11, a2	# tmp1866, _230,
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	slli	a11, a11, 1	# _1688, tmp1866,
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	add.n	a2, a13, a11	# tmp1867, oldBandE, _1688
	s16i	a5, a2, 0	# *_1687, tmp1863
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	add.n	a2, a15, a11	# tmp1869, _586, _1688
	s16i	a3, a2, 0	# *_1685, tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	add.n	a11, a12, a11	# tmp1871, oldLogE, _1688
	s16i	a3, a11, 0	# *_1683, tmp1972
	j	.L296		#
.L312:
	l32i	a8, sp, 280	# %sfp,
	l32r	a3, .LC23	#, tmp1972
	add.n	a2, a11, a8	# tmp1873, _230,
	slli	a2, a2, 1	# tmp1874, tmp1873,
	add.n	a4, a13, a5	# ivtmp$334, oldBandE, _1873
	add.n	a6, a15, a5	# ivtmp$335, _586, _1873
	add.n	a2, a13, a2	# _1265, oldBandE, tmp1874
	add.n	a5, a12, a5	# ivtmp$336, oldLogE, _1873
# @OPUS@\upstream\celt\celt_decoder.c:1423:          oldBandE[c*nbEBands+i]=0;
	movi.n	a7, 0	# tmp1875,
.L322:
	s16i	a7, a4, 0	# MEM[base: _1273, offset: 0B], tmp1875
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s16i	a3, a6, 0	# MEM[base: _1272, offset: 0B], tmp1972
# @OPUS@\upstream\celt\celt_decoder.c:1424:          oldLogE[c*nbEBands+i]=oldLogE2[c*nbEBands+i]=-QCONST16(28.f,DB_SHIFT);
	s16i	a3, a5, 0	# MEM[base: _1271, offset: 0B], tmp1972
	addi.n	a4, a4, 2	# ivtmp$334, ivtmp$334,
	addi.n	a6, a6, 2	# ivtmp$335, ivtmp$335,
	addi.n	a5, a5, 2	# ivtmp$336, ivtmp$336,
# @OPUS@\upstream\celt\celt_decoder.c:1421:       for (i=end;i<nbEBands;i++)
	bne	a2, a4, .L322	# _1265, ivtmp$334,
	j	.L296		#
.L485:
	l32i	a15, sp, 328	# %sfp, dec
# @OPUS@\upstream\celt\celt_decoder.c:1430:    deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i	a10, sp, 244	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1427:    st->rng = dec->rng;
	l32i.n	a9, a15, 28	# *dec_242.rng, *dec_242.rng
# @OPUS@\upstream\celt\celt_decoder.c:1430:    deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i	a11, sp, 288	# %sfp,
	l32i	a12, sp, 308	# %sfp,
	l32i	a14, sp, 464	# accum,
# @OPUS@\upstream\celt\celt_decoder.c:1427:    st->rng = dec->rng;
	s32i.n	a9, a10, 48	# *st_322(D).rng, *dec_242.rng
# @OPUS@\upstream\celt\celt_decoder.c:1430:    deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i.n	a6, a10, 16	# *st_322(D).downsample,
# @OPUS@\upstream\celt\celt_decoder.c:1430:    deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	addi	a8, a10, 92	# tmp1882,,
# @OPUS@\upstream\celt\celt_decoder.c:1430:    deemphasis(out_syn, pcm, N, CC, st->downsample, mode->preemph, st->preemph_memD, accum);
	l32i	a5, sp, 312	# %sfp,
	l32i	a4, sp, 300	# %sfp,
	l32i	a3, sp, 364	# %sfp,
	movi	a2, 0x84	# tmp1880,
	addi	a7, a11, 16	#,,
	add.n	a2, a12, a2	#,, tmp1880
	s32i.n	a8, sp, 0	#, tmp1882
	s32i.n	a14, sp, 4	#,
	call0	deemphasis		#
# @OPUS@\upstream\celt\celt_decoder.c:1432:    st->loss_duration = 0;
	l32i	a8, sp, 244	# %sfp,
	movi.n	a4, 0	# tmp1883,
# @OPUS@\upstream\celt\celt_decoder.c:1434:    RESTORE_STACK;
	l32i	a2, sp, 204	# _saved_stack,
	l32i	a3, sp, 208	# _saved_stack,
# @OPUS@\upstream\celt\celt_decoder.c:1432:    st->loss_duration = 0;
	s32i.n	a4, a8, 60	# *st_322(D).loss_duration, tmp1883
# @OPUS@\upstream\celt\celt_decoder.c:1433:    st->prefilter_and_fold = 0;
	s32i	a4, a8, 88	# *st_322(D).prefilter_and_fold, tmp1883
# @OPUS@\upstream\celt\celt_decoder.c:1434:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _533, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	addi	a2, a2, -32	# tmp1886, MEM[(int *)dec_242 + 20B],
# @OPUS@\upstream\celt\celt_decoder.c:1435:    if (ec_tell(dec) > 8*len)
	l32i	a9, sp, 320	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	add.n	a2, a2, a3	# tmp1888, tmp1886, _533
# @OPUS@\upstream\celt\celt_decoder.c:1435:    if (ec_tell(dec) > 8*len)
	blt	a9, a2, .L372	#, tmp1888,
# @OPUS@\upstream\celt\celt_decoder.c:1437:    if(ec_get_error(dec))
	l32i.n	a2, a15, 44	# MEM[(int *)dec_242 + 44B], MEM[(int *)dec_242 + 44B]
	beqz.n	a2, .L324	# MEM[(int *)dec_242 + 44B],
# @OPUS@\upstream\celt\celt_decoder.c:1438:       st->error = 1;
	l32i	a11, sp, 316	# %sfp,
	l32i	a10, sp, 244	# %sfp,
	s32i.n	a11, a10, 52	# *st_322(D).error,
.L324:
# @OPUS@\upstream\celt\celt_decoder.c:1439:    return frame_size/st->downsample;
	l32i	a12, sp, 244	# %sfp,
	l32i	a2, sp, 352	# %sfp,
	l32i.n	a3, a12, 16	# *st_322(D).downsample,
	call0	__divsi3		#
	j	.L124		#
.L372:
# @OPUS@\upstream\celt\celt_decoder.c:1436:       return OPUS_INTERNAL_ERROR;
	movi.n	a2, -3	# <retval>,
	j	.L124		#
.L373:
# @OPUS@\upstream\celt\celt_decoder.c:1116:          return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
	j	.L124		#
.L266:
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	l32i	a8, sp, 272	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	s32i.n	a8, sp, 8	#,
	s32i.n	a15, sp, 4	#, dec
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
	l32i	a9, sp, 388	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _1323, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1348:    unquant_energy_finalise(mode, start, end, oldBandE,
	sub	a2, a9, a2	# tmp1896,, MEM[(int *)dec_242 + 20B]
	sub	a2, a2, a3	# tmp1898, tmp1896, _1323
	s32i.n	a2, sp, 0	#, tmp1898
	l32i	a7, sp, 332	# %sfp,
	l32i	a6, sp, 240	# %sfp,
	l32i	a5, sp, 276	# %sfp,
	l32i	a4, sp, 264	# %sfp,
	l32i	a3, sp, 268	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	unquant_energy_finalise		#
	j	.L267		#
.L264:
	mov.n	a12, a11	#,
# @OPUS@\upstream\celt\celt_decoder.c:1328:    quant_all_bands(0, mode, start, end, X, C==2 ? X+N : NULL, collapse_masks,
	l32i.n	a8, a12, 32	# *st_322(D).disable_inv,
	movi.n	a7, 0	# iftmp$21_443,
	l32i	a5, sp, 232	# dual_stereo, dual_stereo$23_143
	l32i	a4, sp, 236	# intensity, intensity$24_144
	l32i	a3, sp, 180	# balance, balance$25_147
	l32i.n	a11, a11, 40	# *st_322(D).arch, _149
	s32i	a8, sp, 304	# %sfp,
	mov.n	a9, a7	# iftmp$26_284, iftmp$21_443
	j	.L265		#
.L340:
# @OPUS@\upstream\celt\celt_decoder.c:1113:          if (mode->shortMdctSize<<LM==frame_size)
	movi.n	a9, 1	#,
	s32i	a9, sp, 400	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1112:       for (LM=0;LM<=mode->maxLM;LM++)
	s32i	a13, sp, 260	# %sfp, tmp1071
.L126:
# @OPUS@\upstream\celt\celt_decoder.c:1120:    if (len<0 || len>1275 || pcm==NULL)
	l32i	a10, sp, 304	# %sfp,
	movi	a2, 0x4fb	# tmp1901,
	bltu	a2, a10, .L373	# tmp1901,,
# @OPUS@\upstream\celt\celt_decoder.c:1120:    if (len<0 || len>1275 || pcm==NULL)
	l32i	a11, sp, 364	# %sfp,
	bnez.n	a11, .L474	#,
	j	.L373		#
.L188:
	l32i	a2, sp, 268	# %sfp, _2150
# @OPUS@\upstream\celt\celt_decoder.c:906:             opus_val32 S2=0;
	mov.n	a3, a2	# S2, _2150
	j	.L327		#
.L468:
	l32i	a3, sp, 268	# %sfp, S2
	l32r	a10, .LC13	#, tmp1967
# @OPUS@\upstream\celt\celt_decoder.c:910:                S2 += SHR32(MULT16_16(tmp, tmp), 10);
	l32r	a7, .LC15	#, tmp2518
	j	.L328		#
.L472:
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	l32i	a12, sp, 244	# %sfp,
	l32i	a14, sp, 400	# %sfp,
	l32i.n	a2, a12, 60	# *st_322(D).loss_duration, *st_322(D).loss_duration
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	movi	a3, 0xa0	# tmp1914,
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	add.n	a2, a14, a2	# tmp1908,, *st_322(D).loss_duration
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	bge	a3, a2, .L329	# tmp1914, tmp1908,
	mov.n	a2, a3	# tmp1908, tmp1914
.L329:
# @OPUS@\upstream\celt\celt_decoder.c:1410:    max_background_increase = IMIN(160, st->loss_duration+M)*QCONST16(0.001f,DB_SHIFT);
	slli	a2, a2, 16	# tmp1915, tmp1908,
	srai	a7, a2, 16	# max_background_increase, tmp1915,
	j	.L287		#
.L475:
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a5, sp, 272	# %sfp,
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	s32i	a2, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a4, sp, 260	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	init_caps		#
# @OPUS@\upstream\celt\celt_decoder.c:1265:    ALLOC(offsets, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 384	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	movi.n	a8, 2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a7, a2	# tell,
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	s32i	a8, sp, 396	# %sfp,
	j	.L330		#
.L471:
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	l32i.n	a3, a15, 28	# MEM[(unsigned int *)dec_242 + 28B], MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	l32i.n	a2, a15, 20	# MEM[(int *)dec_242 + 20B], MEM[(int *)dec_242 + 20B]
	l32i	a9, sp, 320	# %sfp,
# @OPUS@\upstream\celt\entcode.h:112:   return _this->nbits_total-EC_ILOG(_this->rng);
	nsau	a3, a3	# _930, MEM[(unsigned int *)dec_242 + 28B]
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	addi	a2, a2, -28	# tmp1917, MEM[(int *)dec_242 + 20B],
	slli	a9, a9, 3	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	l32i	a10, sp, 320	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	add.n	a2, a2, a3	# tmp1919, tmp1917, _930
	s32i	a9, sp, 380	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	blt	a10, a2, .L475	#, tmp1919,
	j	.L331		#
.L476:
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a5, sp, 272	# %sfp,
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	s32i	a2, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a4, sp, 260	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	init_caps		#
# @OPUS@\upstream\celt\celt_decoder.c:1265:    ALLOC(offsets, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 384	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	movi.n	a11, 2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a7, a2	# tell,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	s32i	a14, sp, 380	# %sfp, total_bits
# @OPUS@\upstream\celt\celt_decoder.c:1257:    spread_decision = SPREAD_NORMAL;
	s32i	a11, sp, 396	# %sfp,
	j	.L333		#
.L331:
# @OPUS@\upstream\celt\celt_decoder.c:1259:       spread_decision = ec_dec_icdf(dec, spread_icdf, 5);
	l32r	a3, .LC25	#,
	movi.n	a4, 5	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
	s32i	a2, sp, 396	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a5, sp, 272	# %sfp,
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	s32i	a2, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a4, sp, 260	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	init_caps		#
# @OPUS@\upstream\celt\celt_decoder.c:1265:    ALLOC(offsets, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 384	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
	mov.n	a7, a2	# tell,
	j	.L330		#
.L334:
# @OPUS@\upstream\celt\celt_decoder.c:1259:       spread_decision = ec_dec_icdf(dec, spread_icdf, 5);
	l32r	a3, .LC25	#,
	movi.n	a4, 5	#,
	mov.n	a2, a15	#, dec
	call0	ec_dec_icdf		#
	s32i	a2, sp, 396	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a5, sp, 272	# %sfp,
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\celt_decoder.c:1261:    ALLOC(cap, nbEBands, int);
	s32i	a2, sp, 344	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1263:    init_caps(mode,cap,LM,C);
	l32i	a4, sp, 260	# %sfp,
	l32i	a2, sp, 288	# %sfp,
	call0	init_caps		#
# @OPUS@\upstream\celt\celt_decoder.c:1265:    ALLOC(offsets, nbEBands, int);
	l32i	a2, sp, 280	# %sfp,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 384	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	mov.n	a2, a15	#, dec
	call0	ec_tell_frac		#
	mov.n	a7, a2	# tell,
# @OPUS@\upstream\celt\celt_decoder.c:1269:    tell = ec_tell_frac(dec);
	s32i	a14, sp, 380	# %sfp, total_bits
	j	.L333		#
.L241:
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	add.n	a2, a6, a8	# tmp1922, _996, _998
	l32i	a12, sp, 320	# %sfp,
	addi	a2, a2, -28	# tmp1923, tmp1922,
	slli	a14, a12, 3	# total_bits,,
# @OPUS@\upstream\celt\celt_decoder.c:1258:    if (tell+4 <= total_bits)
	blt	a12, a2, .L476	#, tmp1923,
	j	.L334		#
.L243:
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	bltu	a4, a8, .L336	# budget, _1005,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	l32i	a14, sp, 260	# %sfp,
	l32r	a3, .LC21	#, tmp1962
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	l32i	a8, sp, 292	# %sfp,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	slli	a2, a14, 3	# tmp1978,,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	slli	a4, a8, 2	# _2033,,
# @OPUS@\upstream\celt\celt_decoder.c:509:      tf_select_table[LM][4*isTransient+0+tf_changed] !=
	add.n	a2, a3, a2	# tmp1926, tmp1962, tmp1978
	add.n	a2, a2, a4	# tmp1927, tmp1926, _2033
# @OPUS@\upstream\celt\celt_decoder.c:508:    if (tf_select_rsv &&
	l8ui	a3, a2, 0	# tf_select_table,
	l8ui	a4, a2, 2	# tf_select_table,
	slli	a2, a3, 24	# tmp1935, tmp1934,
	slli	a3, a4, 24	# tmp1938, tmp1937,
	beq	a3, a2, .L336	# tmp1938, tmp1935,
	j	.L337		#
.L124:
# @OPUS@\upstream\celt\celt_decoder.c:1440: }
	l32i	a0, sp, 460	#,
	movi	a9, 0x1d0	#,
	l32i	a12, sp, 456	#,
	l32i	a13, sp, 452	#,
	l32i	a14, sp, 448	#,
	l32i	a15, sp, 444	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	celt_decode_with_ec_dred, .-celt_decode_with_ec_dred
	.section	.text.celt_decode_with_ec,"ax",@progbits
	.literal_position
	.align	4
	.global	celt_decode_with_ec
	.type	celt_decode_with_ec, @function
# Function: celt_decode_with_ec
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return frame_size/st->downsample;
# C context: }
# C context:
# C context: int celt_decode_with_ec(CELTDecoder * OPUS_RESTRICT st, const unsigned char *data,
# C context: int len, opus_val16 * OPUS_RESTRICT pcm, int frame_size, ec_dec *dec, int accum)
# C context: {
# C context: return celt_decode_with_ec_dred(st, data, len, pcm, frame_size, dec, accum
# C context: #ifdef ENABLE_DEEP_PLC
celt_decode_with_ec:
	addi	sp, sp, -32	#,,
	l32i.n	a8, sp, 32	# accum, accum
	s32i.n	a0, sp, 28	#,
# @OPUS@\upstream\celt\celt_decoder.c:1445:    return celt_decode_with_ec_dred(st, data, len, pcm, frame_size, dec, accum
	s32i.n	a8, sp, 0	#, accum
	call0	celt_decode_with_ec_dred		#
# @OPUS@\upstream\celt\celt_decoder.c:1450: }
	l32i.n	a0, sp, 28	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	celt_decode_with_ec, .-celt_decode_with_ec
	.section	.text.opus_custom_decoder_ctl,"ax",@progbits
	.literal_position
	.literal .LC26, 4046
	.literal .LC27, 4027
	.literal .LC28, 4010
	.literal .LC29, 4011
	.literal .LC30, 4031
	.literal .LC31, 4033
	.literal .LC32, 4028
	.literal .LC33, 10010
	.literal .LC34, 10007
	.literal .LC35, 10008
	.literal .LC36, 4047
	.literal .LC37, 10015
	.literal .LC38, 10016
	.literal .LC39, 10012
	.literal .LC40, -1879011328
	.literal .LC41, -28672
	.align	4
	.global	opus_custom_decoder_ctl
	.type	opus_custom_decoder_ctl, @function
# Function: opus_custom_decoder_ctl
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context: st->arch = opus_select_arch();
# C context:
# C context: opus_custom_decoder_ctl(st, OPUS_RESET_STATE);
# C context:
# C context: return OPUS_OK;
# C context: }
# C context:
opus_custom_decoder_ctl:
	addi	sp, sp, -96	#,,
# @OPUS@\upstream\celt\celt_decoder.c:1521:    va_start(ap, request);
	s32i.n	a4, sp, 24	#,
	addi	a4, sp, 16	# tmp234,,
	s32i.n	a4, sp, 4	# MEM[(struct  *)&ap].__va_reg, tmp234
	addi	a4, sp, 64	# tmp235,,
	s32i.n	a4, sp, 0	# MEM[(struct  *)&ap].__va_stk, tmp235
# @OPUS@\upstream\celt\celt_decoder.c:1522:    switch (request)
	l32r	a8, .LC26	#, tmp237
# @OPUS@\upstream\celt\celt_decoder.c:1521:    va_start(ap, request);
	movi.n	a4, 8	# tmp236,
# @OPUS@\upstream\celt\celt_decoder.c:1518: {
	s32i	a12, sp, 88	#,
	s32i	a0, sp, 92	#,
	s32i	a13, sp, 84	#,
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\celt\celt_decoder.c:1521:    va_start(ap, request);
	s32i.n	a5, sp, 28	#,
	s32i.n	a6, sp, 32	#,
	s32i.n	a7, sp, 36	#,
	s32i.n	a4, sp, 8	# MEM[(struct  *)&ap].__va_ndx, tmp236
# @OPUS@\upstream\celt\celt_decoder.c:1518: {
	mov.n	a12, a2	# st, st
# @OPUS@\upstream\celt\celt_decoder.c:1522:    switch (request)
	beq	a3, a8, .L489	# request, tmp237,
	blt	a8, a3, .L490	# tmp237, request,
	l32r	a2, .LC27	#, tmp239
	beq	a3, a2, .L491	# request, tmp239,
	blt	a2, a3, .L492	# tmp239, request,
	l32r	a2, .LC28	#, tmp241
	beq	a3, a2, .L493	# request, tmp241,
	l32r	a2, .LC29	#, tmp242
	beq	a3, a2, .L494	# request, tmp242,
	j	.L587		#
.L492:
	l32r	a2, .LC30	#, tmp243
	beq	a3, a2, .L496	# request, tmp243,
	l32r	a2, .LC31	#, tmp244
	beq	a3, a2, .L497	# request, tmp244,
	l32r	a2, .LC32	#, tmp245
	beq	a3, a2, .L498	# request, tmp245,
	j	.L587		#
.L490:
	l32r	a2, .LC33	#, tmp246
	beq	a3, a2, .L499	# request, tmp246,
	blt	a2, a3, .L500	# tmp246, request,
	l32r	a2, .LC34	#, tmp248
	beq	a3, a2, .L501	# request, tmp248,
	l32r	a2, .LC35	#, tmp249
	beq	a3, a2, .L502	# request, tmp249,
	l32r	a2, .LC36	#, tmp250
	beq	a3, a2, .L503	# request, tmp250,
	j	.L587		#
.L500:
	l32r	a2, .LC37	#, tmp251
	beq	a3, a2, .L504	# request, tmp251,
	l32r	a2, .LC38	#, tmp252
	beq	a3, a2, .L505	# request, tmp252,
	l32r	a2, .LC39	#, tmp253
	beq	a3, a2, .L506	# request, tmp253,
.L587:
# @OPUS@\upstream\celt\celt_decoder.c:1666:   return OPUS_UNIMPLEMENTED;
	movi.n	a2, -5	# <retval>,
	j	.L488		#
.L493:
# @OPUS@\upstream\celt\celt_decoder.c:1526:           opus_int32 value = va_arg(ap, opus_int32);
	movi.n	a3, 0xc	# D.5241,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_158], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5241
# @OPUS@\upstream\celt\celt_decoder.c:1527:           if(value<0 || value>10)
	movi.n	a3, 0xa	# tmp260,
	bltu	a3, a2, .L510	# tmp260, value,
# @OPUS@\upstream\celt\celt_decoder.c:1531:           st->complexity = value;
	s32i.n	a2, a12, 36	# *st_52(D).complexity, value
# @OPUS@\upstream\celt\celt_decoder.c:1533:       break;
	j	.L511		#
.L494:
# @OPUS@\upstream\celt\celt_decoder.c:1536:           opus_int32 *value = va_arg(ap, opus_int32*);
	movi.n	a3, 0xc	# D.5253,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 * *)_169], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5253
# @OPUS@\upstream\celt\celt_decoder.c:1537:           if (!value)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1541:           *value = st->complexity;
	l32i.n	a3, a12, 36	# *st_52(D).complexity, _2
# @OPUS@\upstream\celt\celt_decoder.c:1541:           *value = st->complexity;
	s32i.n	a3, a2, 0	#* value, _2
# @OPUS@\upstream\celt\celt_decoder.c:1543:       break;
	j	.L511		#
.L499:
# @OPUS@\upstream\celt\celt_decoder.c:1546:          opus_int32 value = va_arg(ap, opus_int32);
	movi.n	a3, 0xc	# D.5265,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_180], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5265
# @OPUS@\upstream\celt\celt_decoder.c:1547:          if (value<0 || value>=st->mode->nbEBands)
	bltz	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1547:          if (value<0 || value>=st->mode->nbEBands)
	l32i.n	a3, a12, 0	# *st_52(D).mode, *st_52(D).mode
# @OPUS@\upstream\celt\celt_decoder.c:1547:          if (value<0 || value>=st->mode->nbEBands)
	l32i.n	a3, a3, 8	# _3->nbEBands, _3->nbEBands
	bge	a2, a3, .L510	# value, _3->nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:1549:          st->start = value;
	s32i.n	a2, a12, 20	# *st_52(D).start, value
# @OPUS@\upstream\celt\celt_decoder.c:1551:       break;
	j	.L511		#
.L506:
# @OPUS@\upstream\celt\celt_decoder.c:1554:          opus_int32 value = va_arg(ap, opus_int32);
	movi.n	a3, 0xc	# D.5277,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_191], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5277
# @OPUS@\upstream\celt\celt_decoder.c:1555:          if (value<1 || value>st->mode->nbEBands)
	blti	a2, 1, .L510	# value,,
# @OPUS@\upstream\celt\celt_decoder.c:1555:          if (value<1 || value>st->mode->nbEBands)
	l32i.n	a3, a12, 0	# *st_52(D).mode, *st_52(D).mode
# @OPUS@\upstream\celt\celt_decoder.c:1555:          if (value<1 || value>st->mode->nbEBands)
	l32i.n	a3, a3, 8	# _5->nbEBands, _5->nbEBands
	blt	a3, a2, .L510	# _5->nbEBands, value,
# @OPUS@\upstream\celt\celt_decoder.c:1557:          st->end = value;
	s32i.n	a2, a12, 24	# *st_52(D).end, value
# @OPUS@\upstream\celt\celt_decoder.c:1559:       break;
	j	.L511		#
.L502:
# @OPUS@\upstream\celt\celt_decoder.c:1562:          opus_int32 value = va_arg(ap, opus_int32);
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_202], value
	movi.n	a3, 0xc	# D.5289,
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5289
# @OPUS@\upstream\celt\celt_decoder.c:1563:          if (value<1 || value>2)
	addi.n	a3, a2, -1	# tmp289, value,
# @OPUS@\upstream\celt\celt_decoder.c:1563:          if (value<1 || value>2)
	bgeui	a3, 2, .L510	# tmp289,,
# @OPUS@\upstream\celt\celt_decoder.c:1565:          st->stream_channels = value;
	s32i.n	a2, a12, 12	# *st_52(D).stream_channels, value
# @OPUS@\upstream\celt\celt_decoder.c:1567:       break;
	j	.L511		#
.L501:
# @OPUS@\upstream\celt\celt_decoder.c:1570:          opus_int32 *value = va_arg(ap, opus_int32*);
	movi.n	a3, 0xc	# D.5301,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 * *)_213], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5301
# @OPUS@\upstream\celt\celt_decoder.c:1571:          if (value==NULL)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1573:          *value=st->error;
	l32i.n	a3, a12, 52	# *st_52(D).error, _9
# @OPUS@\upstream\celt\celt_decoder.c:1573:          *value=st->error;
	s32i.n	a3, a2, 0	# *value_67, _9
# @OPUS@\upstream\celt\celt_decoder.c:1574:          st->error = 0;
	movi.n	a2, 0	# tmp296,
	s32i.n	a2, a12, 52	# *st_52(D).error, tmp296
# @OPUS@\upstream\celt\celt_decoder.c:1576:       break;
	j	.L511		#
.L491:
# @OPUS@\upstream\celt\celt_decoder.c:1579:          opus_int32 *value = va_arg(ap, opus_int32*);
	movi.n	a2, 0xc	# D.5313,
	l32i.n	a13, sp, 24	# MEM[(opus_int32 * *)_224], value
	s32i.n	a2, sp, 8	# ap.__va_ndx, D.5313
# @OPUS@\upstream\celt\celt_decoder.c:1580:          if (value==NULL)
	beqz.n	a13, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1582:          *value = st->overlap/st->downsample;
	l32i.n	a3, a12, 16	# *st_52(D).downsample,
	l32i.n	a2, a12, 4	# *st_52(D).overlap,
	call0	__divsi3		#
# @OPUS@\upstream\celt\celt_decoder.c:1582:          *value = st->overlap/st->downsample;
	s32i.n	a2, a13, 0	# *value_71,
# @OPUS@\upstream\celt\celt_decoder.c:1584:       break;
	j	.L511		#
.L498:
# @OPUS@\upstream\celt\celt_decoder.c:1591:          OPUS_CLEAR(st->_decode_mem, (DECODE_BUFFER_SIZE+st->overlap)*st->channels);
	l32i.n	a2, a12, 4	# *st_52(D).overlap, *st_52(D).overlap
	l32i.n	a3, a12, 8	# *st_52(D).channels, *st_52(D).channels
	addmi	a2, a2, 0x800	# tmp307, *st_52(D).overlap,
	mull	a3, a2, a3	#, tmp307, *st_52(D).channels
	l32i.n	a2, a12, 44	# *st_52(D)._decode_mem,
	movi.n	a4, 4	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\celt_decoder.c:1596:          oldLogE = oldBandE + 2*st->mode->nbEBands;
	l32i.n	a3, a12, 0	# *st_52(D).mode, *st_52(D).mode
# @OPUS@\upstream\celt\celt_decoder.c:1595:          oldBandE = lpc+st->channels*CELT_LPC_ORDER;
	l32i.n	a2, a12, 8	# *st_52(D).channels, *st_52(D).channels
# @OPUS@\upstream\celt\celt_decoder.c:1596:          oldLogE = oldBandE + 2*st->mode->nbEBands;
	l32i.n	a14, a3, 8	# _22->nbEBands, _23
# @OPUS@\upstream\celt\celt_decoder.c:1595:          oldBandE = lpc+st->channels*CELT_LPC_ORDER;
	slli	a15, a2, 1	# tmp313, *st_52(D).channels,
	add.n	a15, a15, a2	# tmp314, tmp313, *st_52(D).channels
# @OPUS@\upstream\celt\celt_decoder.c:186:             + 4*2*mode->nbEBands*sizeof(opus_val16);
	slli	a3, a14, 1	# tmp319, _23,
# @OPUS@\upstream\celt\celt_decoder.c:1596:          oldLogE = oldBandE + 2*st->mode->nbEBands;
	slli	a6, a14, 2	# _25, _23,
# @OPUS@\upstream\celt\celt_decoder.c:1595:          oldBandE = lpc+st->channels*CELT_LPC_ORDER;
	slli	a15, a15, 4	# tmp315, tmp314,
# @OPUS@\upstream\celt\celt_decoder.c:186:             + 4*2*mode->nbEBands*sizeof(opus_val16);
	add.n	a3, a3, a14	# tmp320, tmp319, _23
	add.n	a5, a15, a6	# _77, tmp315, _25
	slli	a3, a3, 2	# tmp321, tmp320,
	add.n	a3, a3, a5	# tmp322, tmp321, _77
# @OPUS@\upstream\celt\celt_decoder.c:1598:          OPUS_CLEAR((char*)&st->DECODER_RESET_START,
	addi	a2, a12, 48	#, st,
# @OPUS@\upstream\celt\celt_decoder.c:1590:          lpc = st->_tail;
	addi	a13, a12, 100	# lpc, st,
# @OPUS@\upstream\celt\celt_decoder.c:1598:          OPUS_CLEAR((char*)&st->DECODER_RESET_START,
	movi.n	a4, 1	#,
	addi	a3, a3, 54	#, tmp322,
# @OPUS@\upstream\celt\celt_decoder.c:1596:          oldLogE = oldBandE + 2*st->mode->nbEBands;
	add.n	a13, a13, a5	# oldLogE, lpc, _77
# @OPUS@\upstream\celt\celt_decoder.c:1598:          OPUS_CLEAR((char*)&st->DECODER_RESET_START,
	s32i.n	a6, sp, 48	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\celt_decoder.c:1601:          for (i=0;i<2*st->mode->nbEBands;i++)
	l32i.n	a2, a12, 0	# *st_52(D).mode, *st_52(D).mode
# @OPUS@\upstream\celt\celt_decoder.c:1601:          for (i=0;i<2*st->mode->nbEBands;i++)
	l32i.n	a6, sp, 48	#,
# @OPUS@\upstream\celt\celt_decoder.c:1601:          for (i=0;i<2*st->mode->nbEBands;i++)
	l32i.n	a5, a2, 8	# _91->nbEBands, _91->nbEBands
	slli	a5, a5, 1	# _85, _91->nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:1601:          for (i=0;i<2*st->mode->nbEBands;i++)
	bgei	a5, 1, .L530	# _85,,
.L536:
# @OPUS@\upstream\celt\celt_decoder.c:1603:          st->skip_plc = 1;
	movi.n	a2, 1	# tmp327,
	s32i	a2, a12, 64	# *st_52(D).skip_plc, tmp327
# @OPUS@\upstream\celt\celt_decoder.c:1605:       break;
	j	.L511		#
.L530:
	slli	a14, a14, 3	# _311, _23,
	addi	a4, a15, 100	# tmp328, tmp315,
	addi	a2, a14, 100	# tmp400, _311,
	addi	a8, a15, 104	# tmp330, tmp315,
	add.n	a4, a4, a6	# _217, tmp328, _25
	add.n	a2, a2, a15	# _60, tmp400, tmp315
	add.n	a8, a8, a6	# tmp331, tmp330, _25
	add.n	a3, a12, a4	# vectp$428, st, _217
	movi.n	a7, 1	# tmp332,
	bge	a2, a8, .L532	# _60, tmp331,
	movi.n	a7, 0	# tmp332,
.L532:
	addi	a14, a14, 104	# tmp334, _311,
	add.n	a15, a14, a15	# tmp335, tmp334, tmp315
	movi.n	a8, 1	# tmp336,
	bge	a4, a15, .L533	# _217, tmp335,
	movi.n	a8, 0	# tmp336,
.L533:
	addi.n	a4, a5, -1	# tmp339, _85,
	movi.n	a9, 0xd	# tmp342,
	or	a7, a7, a8	# tmp338, tmp332, tmp336
	movi.n	a8, 1	# tmp340,
	bltu	a9, a4, .L534	# tmp342, tmp339,
	movi.n	a8, 0	# tmp340,
.L534:
	and	a7, a7, a8	# tmp344, tmp338, tmp340
	bbci	a7, 0, .L531	# tmp344,,
	or	a4, a12, a3	# tmp350, st, vectp$428
	extui	a4, a4, 0, 2	# tmp351, tmp350,
	bnez.n	a4, .L531	# tmp351,
	add.n	a2, a12, a2	# ivtmp$441, st, _60
	slli	a5, a5, 1	# tmp358, _85,
	l32r	a4, .LC40	#, tmp401
	add.n	a5, a5, a2	# _345, tmp358, ivtmp$441
.L535:
# @OPUS@\upstream\celt\celt_decoder.c:1602:             oldLogE[i]=oldLogE2[i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a4, a2, 0	# MEM[base: _341, offset: 0B], tmp401
# @OPUS@\upstream\celt\celt_decoder.c:1602:             oldLogE[i]=oldLogE2[i]=-QCONST16(28.f,DB_SHIFT);
	s32i.n	a4, a3, 0	# MEM[base: _342, offset: 0B], tmp401
	addi.n	a2, a2, 4	# ivtmp$441, ivtmp$441,
	addi.n	a3, a3, 4	# ivtmp$444, ivtmp$444,
	bne	a2, a5, .L535	# ivtmp$441, _345,
	j	.L536		#
.L531:
	slli	a2, a5, 1	# tmp361, _85,
	l32r	a3, .LC41	#, tmp402
	add.n	a2, a13, a2	# _334, ivtmp$438, tmp361
.L537:
# @OPUS@\upstream\celt\celt_decoder.c:1602:             oldLogE[i]=oldLogE2[i]=-QCONST16(28.f,DB_SHIFT);
	add.n	a4, a13, a6	# tmp362, ivtmp$438, _25
	s16i	a3, a4, 0	# MEM[base: _31, offset: 0B], tmp402
# @OPUS@\upstream\celt\celt_decoder.c:1602:             oldLogE[i]=oldLogE2[i]=-QCONST16(28.f,DB_SHIFT);
	s16i	a3, a13, 0	# MEM[base: _30, offset: 0B], tmp402
	addi.n	a13, a13, 2	# ivtmp$438, ivtmp$438,
# @OPUS@\upstream\celt\celt_decoder.c:1601:          for (i=0;i<2*st->mode->nbEBands;i++)
	bne	a13, a2, .L537	# ivtmp$438, _334,
	j	.L536		#
.L497:
# @OPUS@\upstream\celt\celt_decoder.c:1608:          opus_int32 *value = va_arg(ap, opus_int32*);
	movi.n	a3, 0xc	# D.5325,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 * *)_235], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5325
# @OPUS@\upstream\celt\celt_decoder.c:1609:          if (value==NULL)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1611:          *value = st->postfilter_period;
	l32i	a3, a12, 68	# *st_52(D).postfilter_period, _36
# @OPUS@\upstream\celt\celt_decoder.c:1611:          *value = st->postfilter_period;
	s32i.n	a3, a2, 0	#* value, _36
# @OPUS@\upstream\celt\celt_decoder.c:1613:       break;
	j	.L511		#
.L504:
# @OPUS@\upstream\celt\celt_decoder.c:1616:          const CELTMode ** value = va_arg(ap, const CELTMode**);
	movi.n	a3, 0xc	# D.5337,
	l32i.n	a2, sp, 24	# MEM[(const struct OpusCustomMode * * *)_246], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5337
# @OPUS@\upstream\celt\celt_decoder.c:1617:          if (value==0)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1619:          *value=st->mode;
	l32i.n	a3, a12, 0	# *st_52(D).mode, _37
# @OPUS@\upstream\celt\celt_decoder.c:1619:          *value=st->mode;
	s32i.n	a3, a2, 0	#* value, _37
# @OPUS@\upstream\celt\celt_decoder.c:1621:       break;
	j	.L511		#
.L505:
# @OPUS@\upstream\celt\celt_decoder.c:1624:          opus_int32 value = va_arg(ap, opus_int32);
	movi.n	a2, 0xc	# D.5349,
	s32i.n	a2, sp, 8	# ap.__va_ndx, D.5349
# @OPUS@\upstream\celt\celt_decoder.c:1625:          st->signalling = value;
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_257], MEM[(opus_int32 *)_257]
	s32i.n	a2, a12, 28	# *st_52(D).signalling, MEM[(opus_int32 *)_257]
# @OPUS@\upstream\celt\celt_decoder.c:1627:       break;
	j	.L511		#
.L496:
# @OPUS@\upstream\celt\celt_decoder.c:1630:          opus_uint32 * value = va_arg(ap, opus_uint32 *);
	movi.n	a3, 0xc	# D.5361,
	l32i.n	a2, sp, 24	# MEM[(opus_uint32 * *)_268], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5361
# @OPUS@\upstream\celt\celt_decoder.c:1631:          if (value==0)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1633:          *value=st->rng;
	l32i.n	a3, a12, 48	# *st_52(D).rng, _38
# @OPUS@\upstream\celt\celt_decoder.c:1633:          *value=st->rng;
	s32i.n	a3, a2, 0	#* value, _38
# @OPUS@\upstream\celt\celt_decoder.c:1635:       break;
	j	.L511		#
.L489:
# @OPUS@\upstream\celt\celt_decoder.c:1638:           opus_int32 value = va_arg(ap, opus_int32);
	movi.n	a3, 0xc	# D.5373,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 *)_279], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5373
# @OPUS@\upstream\celt\celt_decoder.c:1639:           if(value<0 || value>1)
	bgeui	a2, 2, .L510	# value,,
# @OPUS@\upstream\celt\celt_decoder.c:1643:           st->disable_inv = value;
	s32i.n	a2, a12, 32	# *st_52(D).disable_inv, value
# @OPUS@\upstream\celt\celt_decoder.c:1645:       break;
	j	.L511		#
.L503:
# @OPUS@\upstream\celt\celt_decoder.c:1648:           opus_int32 *value = va_arg(ap, opus_int32*);
	movi.n	a3, 0xc	# D.5385,
	l32i.n	a2, sp, 24	# MEM[(opus_int32 * *)_290], value
	s32i.n	a3, sp, 8	# ap.__va_ndx, D.5385
# @OPUS@\upstream\celt\celt_decoder.c:1649:           if (!value)
	beqz.n	a2, .L510	# value,
# @OPUS@\upstream\celt\celt_decoder.c:1653:           *value = st->disable_inv;
	l32i.n	a3, a12, 32	# *st_52(D).disable_inv, _40
# @OPUS@\upstream\celt\celt_decoder.c:1653:           *value = st->disable_inv;
	s32i.n	a3, a2, 0	#* value, _40
.L511:
# @OPUS@\upstream\celt\celt_decoder.c:1660:    return OPUS_OK;
	movi.n	a2, 0	# <retval>,
	j	.L488		#
.L510:
# @OPUS@\upstream\celt\celt_decoder.c:1663:    return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L488:
# @OPUS@\upstream\celt\celt_decoder.c:1667: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	opus_custom_decoder_ctl, .-opus_custom_decoder_ctl
	.section	.text.celt_decoder_init,"ax",@progbits
	.literal_position
	.literal .LC42, 48000
	.literal .LC43, 4028
	.align	4
	.global	celt_decoder_init
	.type	celt_decoder_init, @function
# Function: celt_decoder_init
# Module: upstream/celt/celt_decoder.c
# CELT frame decode, synthesis, packet-loss concealment and postprocessing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif /* CUSTOM_MODES */
# C context:
# C context: int celt_decoder_init(CELTDecoder *st, opus_int32 sampling_rate, int channels)
# C context: {
# C context: int ret;
# C context: ret = opus_custom_decoder_init(st, opus_custom_mode_create(48000, 960, NULL), channels);
# C context: if (ret != OPUS_OK)
celt_decoder_init:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	mov.n	a12, a2	# st, st
# @OPUS@\upstream\celt\celt_decoder.c:210:    ret = opus_custom_decoder_init(st, opus_custom_mode_create(48000, 960, NULL), channels);
	l32r	a2, .LC42	#,
# @OPUS@\upstream\celt\celt_decoder.c:208: {
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
	mov.n	a14, a4	# channels, channels
	mov.n	a15, a3	# sampling_rate, sampling_rate
# @OPUS@\upstream\celt\celt_decoder.c:210:    ret = opus_custom_decoder_init(st, opus_custom_mode_create(48000, 960, NULL), channels);
	movi.n	a4, 0	#,
	movi	a3, 0x3c0	#,
# @OPUS@\upstream\celt\celt_decoder.c:208: {
	s32i.n	a13, sp, 36	#,
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\celt\celt_decoder.c:210:    ret = opus_custom_decoder_init(st, opus_custom_mode_create(48000, 960, NULL), channels);
	call0	opus_custom_mode_create		#
	mov.n	a13, a2	# _1,
# @OPUS@\upstream\celt\celt_decoder.c:222:    if (channels < 0 || channels > 2)
	bgeui	a14, 3, .L592	# channels,,
# @OPUS@\upstream\celt\celt_decoder.c:225:    if (st==NULL)
	bnez.n	a12, .L590	# st,
.L591:
# @OPUS@\upstream\celt\celt_decoder.c:226:       return OPUS_ALLOC_FAIL;
	movi.n	a2, -7	# <retval>,
	j	.L588		#
.L590:
# @OPUS@\upstream\celt\celt_decoder.c:186:             + 4*2*mode->nbEBands*sizeof(opus_val16);
	slli	a2, a14, 1	# tmp71, channels,
	l32i.n	a3, a13, 8	# MEM[(const struct OpusCustomMode *)_1].nbEBands, MEM[(const struct OpusCustomMode *)_1].nbEBands
	add.n	a2, a2, a14	# tmp72, tmp71, channels
	slli	a2, a2, 4	# tmp73, tmp72,
	addi	a2, a2, 102	# tmp74, tmp73,
	slli	a3, a3, 4	# tmp75, MEM[(const struct OpusCustomMode *)_1].nbEBands,
# @OPUS@\upstream\celt\celt_decoder.c:228:    OPUS_CLEAR((char*)st, opus_custom_decoder_get_size(mode, channels));
	add.n	a3, a2, a3	#, tmp74, tmp75
	movi.n	a4, 1	#,
	mov.n	a2, a12	#, st
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\celt_decoder.c:232:    st->_decode_mem = yoradio_opus_history(channels*(DECODE_BUFFER_SIZE+mode->overlap)*sizeof(celt_sig));
	l32i.n	a2, a13, 4	# MEM[(const struct OpusCustomMode *)_1].overlap, MEM[(const struct OpusCustomMode *)_1].overlap
# @OPUS@\upstream\celt\celt_decoder.c:230:    st->mode = mode;
	s32i.n	a13, a12, 0	# st_7(D)->mode, _1
# @OPUS@\upstream\celt\celt_decoder.c:232:    st->_decode_mem = yoradio_opus_history(channels*(DECODE_BUFFER_SIZE+mode->overlap)*sizeof(celt_sig));
	addmi	a2, a2, 0x800	# tmp78, MEM[(const struct OpusCustomMode *)_1].overlap,
	mull	a2, a2, a14	# tmp80, tmp78, channels
	slli	a2, a2, 2	#, tmp80,
	call0	yoradio_opus_history		#
# @OPUS@\upstream\celt\celt_decoder.c:232:    st->_decode_mem = yoradio_opus_history(channels*(DECODE_BUFFER_SIZE+mode->overlap)*sizeof(celt_sig));
	s32i.n	a2, a12, 44	# st_7(D)->_decode_mem, _27
# @OPUS@\upstream\celt\celt_decoder.c:233:    if (!st->_decode_mem) return OPUS_ALLOC_FAIL;
	beqz.n	a2, .L591	# _27,
# @OPUS@\upstream\celt\celt_decoder.c:240:    st->end = st->mode->effEBands;
	l32i.n	a2, a12, 0	# st_7(D)->mode, st_7(D)->mode
# @OPUS@\upstream\celt\celt_decoder.c:239:    st->start = 0;
	movi.n	a4, 0	# tmp84,
# @OPUS@\upstream\celt\celt_decoder.c:235:    st->overlap = mode->overlap;
	l32i.n	a6, a13, 4	# MEM[(const struct OpusCustomMode *)_1].overlap, MEM[(const struct OpusCustomMode *)_1].overlap
# @OPUS@\upstream\celt\celt_decoder.c:240:    st->end = st->mode->effEBands;
	l32i.n	a5, a2, 12	# _29->effEBands, _29->effEBands
# @OPUS@\upstream\celt\celt_decoder.c:238:    st->downsample = 1;
	movi.n	a13, 1	# tmp83,
# @OPUS@\upstream\celt\celt_decoder.c:243:    st->disable_inv = channels == 1;
	mov.n	a3, a4	#, tmp84
	addi.n	a2, a14, -1	# tmp90, channels,
	moveqz	a3, a13, a2	#, tmp83, tmp90
	mov.n	a2, a3	# tmp89,
# @OPUS@\upstream\celt\celt_decoder.c:249:    opus_custom_decoder_ctl(st, OPUS_RESET_STATE);
	l32r	a3, .LC43	#,
# @OPUS@\upstream\celt\celt_decoder.c:239:    st->start = 0;
	s32i.n	a4, a12, 20	# st_7(D)->start, tmp84
# @OPUS@\upstream\celt\celt_decoder.c:247:    st->arch = opus_select_arch();
	s32i.n	a4, a12, 40	# st_7(D)->arch, tmp84
# @OPUS@\upstream\celt\celt_decoder.c:235:    st->overlap = mode->overlap;
	s32i.n	a6, a12, 4	# st_7(D)->overlap, MEM[(const struct OpusCustomMode *)_1].overlap
# @OPUS@\upstream\celt\celt_decoder.c:238:    st->downsample = 1;
	s32i.n	a13, a12, 16	# st_7(D)->downsample, tmp83
# @OPUS@\upstream\celt\celt_decoder.c:240:    st->end = st->mode->effEBands;
	s32i.n	a5, a12, 24	# st_7(D)->end, _29->effEBands
# @OPUS@\upstream\celt\celt_decoder.c:241:    st->signalling = 1;
	s32i.n	a13, a12, 28	# st_7(D)->signalling, tmp83
# @OPUS@\upstream\celt\celt_decoder.c:243:    st->disable_inv = channels == 1;
	s32i.n	a2, a12, 32	# st_7(D)->disable_inv, tmp89
# @OPUS@\upstream\celt\celt_decoder.c:236:    st->stream_channels = st->channels = channels;
	s32i.n	a14, a12, 8	# st_7(D)->channels, channels
# @OPUS@\upstream\celt\celt_decoder.c:236:    st->stream_channels = st->channels = channels;
	s32i.n	a14, a12, 12	# st_7(D)->stream_channels, channels
# @OPUS@\upstream\celt\celt_decoder.c:249:    opus_custom_decoder_ctl(st, OPUS_RESET_STATE);
	mov.n	a2, a12	#, st
	s32i.n	a4, sp, 0	#,
	call0	opus_custom_decoder_ctl		#
# @OPUS@\upstream\celt\celt_decoder.c:213:    st->downsample = resampling_factor(sampling_rate);
	mov.n	a2, a15	#, sampling_rate
	call0	resampling_factor		#
# @OPUS@\upstream\celt\celt_decoder.c:214:    if (st->downsample==0)
	l32i.n	a4, sp, 0	#,
# @OPUS@\upstream\celt\celt_decoder.c:213:    st->downsample = resampling_factor(sampling_rate);
	s32i.n	a2, a12, 16	# st_7(D)->downsample, _2
# @OPUS@\upstream\celt\celt_decoder.c:214:    if (st->downsample==0)
	movnez	a13, a4, a2	# tmp96, tmp84, _2
	neg	a2, a13	# <retval>, tmp96
	j	.L588		#
.L592:
# @OPUS@\upstream\celt\celt_decoder.c:223:       return OPUS_BAD_ARG;
	movi.n	a2, -1	# <retval>,
.L588:
# @OPUS@\upstream\celt\celt_decoder.c:218: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	celt_decoder_init, .-celt_decoder_init
	.section	.rodata.tapset_icdf,"a"
	.align	4
	.type	tapset_icdf, @object
	.size	tapset_icdf, 3
tapset_icdf:
	.byte	2
	.byte	1
	.byte	0
	.section	.rodata.spread_icdf,"a"
	.align	4
	.type	spread_icdf, @object
	.size	spread_icdf, 4
spread_icdf:
	.byte	25
	.byte	23
	.byte	2
	.byte	0
	.section	.rodata.trim_icdf,"a"
	.align	4
	.type	trim_icdf, @object
	.size	trim_icdf, 11
trim_icdf:
	.byte	126
	.byte	124
	.byte	119
	.byte	109
	.byte	87
	.byte	41
	.byte	19
	.byte	9
	.byte	4
	.byte	2
	.byte	0
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
