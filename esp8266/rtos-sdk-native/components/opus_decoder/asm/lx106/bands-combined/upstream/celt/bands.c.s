# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/bands.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"bands.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\bands.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\bands.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\bands.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\bands.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\bands.c.s.raw
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
	.section	.text.deinterleave_hadamard,"ax",@progbits
	.literal_position
	.literal .LC0, 1073741822
	.literal .LC1, ordery_table
	.align	4
	.type	deinterleave_hadamard, @function
# Function: deinterleave_hadamard
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: 15,  0,  8,  7, 12,  3, 11,  4, 14,  1,  9,  6, 13,  2, 10,  5,
# C context: };
# C context:
# C context: static void deinterleave_hadamard(celt_norm *X, int N0, int stride, int hadamard)
# C context: {
# C context: int i,j;
# C context: VARDECL(celt_norm, tmp);
# C context: int N;
deinterleave_hadamard:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
# @OPUS@\upstream\celt\bands.c:595:    N = N0*stride;
	mull	a12, a3, a4	# N$201_1, N0, stride
# @OPUS@\upstream\celt\bands.c:594:    SAVE_STACK;
	s32i.n	a5, sp, 16	#,
# @OPUS@\upstream\celt\bands.c:590: {
	s32i.n	a0, sp, 60	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\bands.c:590: {
	mov.n	a14, a3	# N0, N0
	mov.n	a15, a4	# stride, stride
	mov.n	a13, a2	# X, X
# @OPUS@\upstream\celt\bands.c:594:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:596:    ALLOC(tmp, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, N$201_1
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:598:    if (hadamard)
	l32i.n	a5, sp, 16	#,
	bnez.n	a5, .L2	# hadamard,
# @OPUS@\upstream\celt\bands.c:607:       for (i=0;i<stride;i++)
	blti	a15, 1, .L3	# stride,,
	blti	a14, 1, .L3	# N0,,
	slli	a3, a14, 1	# tmp93, N0,
	mov.n	a11, a3	# tmp96, tmp93
	slli	a10, a14, 2	# tmp114, N0,
	slli	a7, a15, 1	# _130, stride,
	mov.n	a8, a13	# ivtmp$261, X
	add.n	a3, a2, a3	# ivtmp$263, tmp, tmp93
	add.n	a14, a13, a7	# _132, X, _130
	neg	a11, a11	# tmp97, tmp96
	neg	a10, a10	# tmp115, tmp114
	j	.L4		#
.L2:
# @OPUS@\upstream\celt\bands.c:600:       const int *ordery = ordery_table+stride-2;
	l32r	a3, .LC0	#, tmp98
	add.n	a3, a15, a3	# _3, stride, tmp98
# @OPUS@\upstream\celt\bands.c:601:       for (i=0;i<stride;i++)
	blti	a15, 1, .L3	# stride,,
	blti	a14, 1, .L3	# N0,,
	l32r	a4, .LC1	#, tmp100
	slli	a3, a3, 2	# tmp99, _3,
	addi	a9, a4, -8	# tmp101, tmp100,
	slli	a5, a15, 3	# tmp103, stride,
	add.n	a3, a3, a4	# ivtmp$252, tmp99, tmp100
	mov.n	a8, a13	# ivtmp$254, X
	add.n	a9, a9, a5	# _77, tmp101, tmp103
	slli	a6, a15, 1	# _122, stride,
	j	.L5		#
.L6:
# @OPUS@\upstream\celt\bands.c:604:             tmp[ordery[i]*N0+j] = X[j*stride+i];
	l16si	a7, a5, 0	# MEM[base: _107, offset: 0B], _17
	add.n	a5, a5, a6	# ivtmp$247, ivtmp$247, _122
# @OPUS@\upstream\celt\bands.c:604:             tmp[ordery[i]*N0+j] = X[j*stride+i];
	s16i	a7, a4, 0	# MEM[base: _106, offset: 0B], _17
	addi.n	a4, a4, 2	# ivtmp$248, ivtmp$248,
# @OPUS@\upstream\celt\bands.c:603:          for (j=0;j<N0;j++)
	bne	a10, a4, .L6	# _99, ivtmp$248,
	addi.n	a3, a3, 4	# ivtmp$252, ivtmp$252,
	addi.n	a8, a8, 2	# ivtmp$254, ivtmp$254,
# @OPUS@\upstream\celt\bands.c:601:       for (i=0;i<stride;i++)
	beq	a9, a3, .L3	# _77, ivtmp$252,
.L5:
# @OPUS@\upstream\celt\bands.c:604:             tmp[ordery[i]*N0+j] = X[j*stride+i];
	l32i.n	a4, a3, 0	# MEM[base: _82, offset: 0B], MEM[base: _82, offset: 0B]
	mov.n	a5, a8	# ivtmp$247, ivtmp$254
	mull	a4, a14, a4	# _110, N0, MEM[base: _82, offset: 0B]
	add.n	a10, a14, a4	# tmp108, N0, _110
	slli	a10, a10, 1	# tmp109, tmp108,
	slli	a4, a4, 1	# tmp107, _110,
	add.n	a4, a2, a4	# ivtmp$248, tmp, tmp107
	add.n	a10, a2, a10	# _99, tmp, tmp109
	j	.L6		#
.L7:
# @OPUS@\upstream\celt\bands.c:609:             tmp[i*N0+j] = X[j*stride+i];
	l16si	a6, a5, 0	# MEM[base: _31, offset: 0B], _28
	add.n	a5, a5, a7	# ivtmp$257, ivtmp$257, _130
# @OPUS@\upstream\celt\bands.c:609:             tmp[i*N0+j] = X[j*stride+i];
	s16i	a6, a4, 0	# MEM[base: _30, offset: 0B], _28
	addi.n	a4, a4, 2	# ivtmp$258, ivtmp$258,
# @OPUS@\upstream\celt\bands.c:608:          for (j=0;j<N0;j++)
	bne	a4, a3, .L7	# ivtmp$258, ivtmp$263,
	addi.n	a8, a8, 2	# ivtmp$261, ivtmp$261,
	sub	a3, a9, a10	# ivtmp$263, _135, tmp115
# @OPUS@\upstream\celt\bands.c:607:       for (i=0;i<stride;i++)
	beq	a8, a14, .L3	# ivtmp$261, _132,
.L4:
	add.n	a9, a3, a11	# _135, ivtmp$263, tmp97
# @OPUS@\upstream\celt\bands.c:604:             tmp[ordery[i]*N0+j] = X[j*stride+i];
	mov.n	a4, a9	# ivtmp$258, _135
	mov.n	a5, a8	# ivtmp$257, ivtmp$261
	j	.L7		#
.L3:
# @OPUS@\upstream\celt\bands.c:611:    OPUS_COPY(X, tmp, N);
	mov.n	a3, a2	#, tmp
	mov.n	a4, a12	#, N$201_1
	mov.n	a2, a13	#, X
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:612:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\bands.c:613: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	deinterleave_hadamard, .-deinterleave_hadamard
	.global	__divsi3
	.section	.text.intensity_stereo$isra$1,"ax",@progbits
	.literal_position
	.align	4
	.type	intensity_stereo$isra$1, @function
# Function: intensity_stereo$isra$1
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
intensity_stereo$isra$1:
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	add.n	a2, a6, a2	# tmp106, bandID, ISRA$240
	slli	a2, a2, 2	# tmp107, tmp106,
	slli	a6, a6, 2	# tmp109, bandID,
# @OPUS@\upstream\celt\bands.c:394: static void intensity_stereo(const CELTMode *m, celt_norm * OPUS_RESTRICT X, const celt_norm * OPUS_RESTRICT Y, const celt_ener *bandE, int bandID, int N)
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	add.n	a2, a5, a2	# tmp108, bandE, tmp107
	add.n	a5, a5, a6	# tmp110, bandE, tmp109
# @OPUS@\upstream\celt\bands.c:394: static void intensity_stereo(const CELTMode *m, celt_norm * OPUS_RESTRICT X, const celt_norm * OPUS_RESTRICT Y, const celt_ener *bandE, int bandID, int N)
	s32i.n	a14, sp, 32	#,
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	l32i.n	a2, a2, 0	# *_8, _9
	l32i.n	a14, a5, 0	# *_12, _13
# @OPUS@\upstream\celt\bands.c:394: static void intensity_stereo(const CELTMode *m, celt_norm * OPUS_RESTRICT X, const celt_norm * OPUS_RESTRICT Y, const celt_ener *bandE, int bandID, int N)
	s32i.n	a15, sp, 28	#,
	s32i.n	a3, sp, 0	# %sfp, X
	s32i.n	a0, sp, 44	#,
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
# @OPUS@\upstream\celt\bands.c:394: static void intensity_stereo(const CELTMode *m, celt_norm * OPUS_RESTRICT X, const celt_norm * OPUS_RESTRICT Y, const celt_ener *bandE, int bandID, int N)
	s32i.n	a4, sp, 4	# %sfp, Y
	mov.n	a15, a7	# N, N
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	mov.n	a3, a2	# _14, _9
	bge	a2, a14, .L12	# _9, _13,
	mov.n	a3, a14	# _14, _13
.L12:
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	blti	a3, 1, .L19	# _14,,
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	movi.n	a4, 0x1f	# tmp114,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a3	# _16, _14
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	sub	a3, a4, a3	# _20, tmp114, _16
# @OPUS@\upstream\celt\bands.c:402:    int shift = celt_zlog2(MAX32(bandE[i], bandE[i+m->nbEBands]))-13;
	addi	a4, a3, -13	# shift, _20,
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	bgei	a4, 1, .L14	# shift,,
	movi.n	a4, 0xd	# tmp115,
	sub	a4, a4, a3	# prephitmp_157, tmp115, _20
	j	.L13		#
.L14:
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	ssr	a4	# shift
	sra	a14, a14	# tmp116, _13
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	ssr	a4	# shift
	sra	a4, a2	# tmp118, _9
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	slli	a14, a14, 16	# tmp117, tmp116,
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	slli	a4, a4, 16	# tmp119, tmp118,
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	srai	a14, a14, 16	# iftmp$169_23, tmp117,
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	srai	a12, a4, 16	# iftmp$172_29, tmp119,
	j	.L15		#
.L19:
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	movi.n	a4, 0xd	# prephitmp_157,
.L13:
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	ssl	a4	# prephitmp_157
	sll	a14, a14	# tmp120, _13
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	ssl	a4	# prephitmp_157
	sll	a4, a2	# tmp122, _9
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	slli	a14, a14, 16	# tmp121, tmp120,
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	slli	a4, a4, 16	# tmp123, tmp122,
# @OPUS@\upstream\celt\bands.c:404:    left = VSHR32(bandE[i],shift);
	srai	a14, a14, 16	# iftmp$169_23, tmp121,
# @OPUS@\upstream\celt\bands.c:405:    right = VSHR32(bandE[i+m->nbEBands],shift);
	srai	a12, a4, 16	# iftmp$172_29, tmp123,
.L15:
# @OPUS@\upstream\celt\bands.c:406:    norm = EPSILON + celt_sqrt(EPSILON+MULT16_16(left,left)+MULT16_16(right,right));
	mull	a3, a12, a12	# tmp125, iftmp$172_29, iftmp$172_29
# @OPUS@\upstream\celt\bands.c:406:    norm = EPSILON + celt_sqrt(EPSILON+MULT16_16(left,left)+MULT16_16(right,right));
	mull	a2, a14, a14	# tmp124, iftmp$169_23, iftmp$169_23
# @OPUS@\upstream\celt\bands.c:406:    norm = EPSILON + celt_sqrt(EPSILON+MULT16_16(left,left)+MULT16_16(right,right));
	add.n	a2, a2, a3	# tmp126, tmp124, tmp125
# @OPUS@\upstream\celt\bands.c:406:    norm = EPSILON + celt_sqrt(EPSILON+MULT16_16(left,left)+MULT16_16(right,right));
	addi.n	a2, a2, 1	#, tmp126,
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\bands.c:406:    norm = EPSILON + celt_sqrt(EPSILON+MULT16_16(left,left)+MULT16_16(right,right));
	addi.n	a5, a2, 1	# tmp129,,
# @OPUS@\upstream\celt\bands.c:407:    a1 = DIV32_16(SHL32(EXTEND32(left),14),norm);
	slli	a5, a5, 16	# tmp130, tmp129,
	srai	a13, a5, 16	# _48, tmp130,
	mov.n	a3, a13	#, _48
	slli	a2, a14, 14	#, iftmp$169_23,
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:407:    a1 = DIV32_16(SHL32(EXTEND32(left),14),norm);
	slli	a14, a2, 16	# tmp136,,
# @OPUS@\upstream\celt\bands.c:408:    a2 = DIV32_16(SHL32(EXTEND32(right),14),norm);
	mov.n	a3, a13	#, _48
	slli	a2, a12, 14	#, iftmp$172_29,
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:408:    a2 = DIV32_16(SHL32(EXTEND32(right),14),norm);
	slli	a2, a2, 16	# tmp142,,
# @OPUS@\upstream\celt\bands.c:407:    a1 = DIV32_16(SHL32(EXTEND32(left),14),norm);
	srai	a14, a14, 16	# a1, tmp136,
# @OPUS@\upstream\celt\bands.c:408:    a2 = DIV32_16(SHL32(EXTEND32(right),14),norm);
	srai	a2, a2, 16	# a2, tmp142,
# @OPUS@\upstream\celt\bands.c:409:    for (j=0;j<N;j++)
	blti	a15, 1, .L11	# N,,
	l32i.n	a3, sp, 0	# %sfp, ivtmp$267
	slli	a7, a15, 1	# tmp143, N,
	l32i.n	a4, sp, 4	# %sfp, ivtmp$268
	add.n	a7, a3, a7	# _138, ivtmp$267, tmp143
.L17:
# @OPUS@\upstream\celt\bands.c:414:       X[j] = EXTRACT16(SHR32(MAC16_16(MULT16_16(a1, l), a2, r), 14));
	l16ui	a5, a3, 0	# MEM[base: _144, offset: 0B],
	l16ui	a6, a4, 0	# MEM[base: _142, offset: 0B],
	mul16s	a5, a5, a14	# tmp144, MEM[base: _144, offset: 0B], a1
	mul16s	a6, a6, a2	# tmp146, MEM[base: _142, offset: 0B], a2
	addi.n	a4, a4, 2	# ivtmp$268, ivtmp$268,
	add.n	a5, a5, a6	# tmp148, tmp144, tmp146
	srai	a5, a5, 14	# tmp149, tmp148,
	s16i	a5, a3, 0	# MEM[base: _144, offset: 0B], tmp149
	addi.n	a3, a3, 2	# ivtmp$267, ivtmp$267,
# @OPUS@\upstream\celt\bands.c:409:    for (j=0;j<N;j++)
	bne	a3, a7, .L17	# ivtmp$267, _138,
.L11:
# @OPUS@\upstream\celt\bands.c:417: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	intensity_stereo$isra$1, .-intensity_stereo$isra$1
	.global	__udivsi3
	.section	.text.quant_partition,"ax",@progbits
	.literal_position
	.literal .LC2, -16384
	.literal .LC3, exp2_table8$4166
	.literal .LC4, 8277
	.literal .LC5, -7651
	.literal .LC6, -32768
	.literal .LC7, 16384
	.literal .LC8, -2597
	.literal .LC9, 7932
	.literal .LC10, 8192
	.literal .LC11, 1664525
	.literal .LC12, 1013904223
	.literal .LC13, 32768
	.align	4
	.type	quant_partition, @function
# Function: quant_partition
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: It can split the band in two and transmit the energy difference with
# C context: the two half-bands. It can be called recursively so bands can end up being
# C context: split in 8 parts. */
# C context: static unsigned quant_partition(struct band_ctx *ctx, celt_norm *X,
# C context: int N, int b, int B, celt_norm *lowband,
# C context: int LM,
# C context: opus_val16 gain, int fill)
# C context: {
quant_partition:
	addi	sp, sp, -112	#,,
# @OPUS@\upstream\celt\bands.c:981:    m = ctx->m;
	l32i.n	a8, a2, 8	# ctx_143(D)->m, m
# @OPUS@\upstream\celt\bands.c:965: {
	l32i	a9, sp, 112	# LM, LM
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i.n	a11, a8, 8	# m_144->nbEBands, m_144->nbEBands
# @OPUS@\upstream\celt\bands.c:965: {
	s32i	a12, sp, 104	#,
	mov.n	a12, a2	# ctx, ctx
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	addi.n	a2, a9, 1	# tmp522, LM,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	mull	a2, a2, a11	# tmp523, tmp522, m_144->nbEBands
# @OPUS@\upstream\celt\bands.c:982:    i = ctx->i;
	l32i.n	a10, a12, 12	# ctx_143(D)->i, i
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i	a11, a8, 88	# m_144->cache.index, m_144->cache.index
	add.n	a2, a2, a10	# tmp525, tmp523, i
	slli	a2, a2, 1	# tmp527, tmp525,
	add.n	a2, a11, a2	# tmp528, m_144->cache.index, tmp527
# @OPUS@\upstream\celt\bands.c:965: {
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i	a11, a8, 92	# m_144->cache.bits, _1
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l16si	a2, a2, 0	# *_9, _11
# @OPUS@\upstream\celt\bands.c:965: {
	mov.n	a15, a3	# X, X
	s32i.n	a7, sp, 24	# %sfp, lowband
	mov.n	a3, a4	# N, N
	l16si	a7, sp, 116	# gain,
# @OPUS@\upstream\celt\bands.c:984:    ec = ctx->ec;
	l32i.n	a4, a12, 28	# ctx_143(D)->ec,
# @OPUS@\upstream\celt\bands.c:965: {
	s32i	a13, sp, 100	#,
	s32i	a14, sp, 96	#,
	s32i	a0, sp, 108	#,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	add.n	a2, a11, a2	# tmp933, _1, _11
# @OPUS@\upstream\celt\bands.c:965: {
	s32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:984:    ec = ctx->ec;
	s32i.n	a4, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:965: {
	mov.n	a14, a5	# b, b
	mov.n	a13, a6	# B, B
# @OPUS@\upstream\celt\bands.c:980:    encode = band_encode(ctx);
	l32i.n	a7, a12, 0	# MEM[(int *)ctx_143(D)], _207
# @OPUS@\upstream\celt\bands.c:983:    spread = ctx->spread;
	l32i.n	a5, a12, 20	# ctx_143(D)->spread, spread
	l8ui	a6, a2, 0	# *cache_149, pretmp_483
# @OPUS@\upstream\celt\bands.c:988:    if (LM != -1 && b > cache[cache[0]]+12 && N>2)
	beqi	a9, -1, .L22	# LM,,
# @OPUS@\upstream\celt\bands.c:988:    if (LM != -1 && b > cache[cache[0]]+12 && N>2)
	add.n	a4, a2, a6	# tmp531, tmp933, pretmp_483
	l8ui	a4, a4, 0	# *_14, *_14
# @OPUS@\upstream\celt\bands.c:988:    if (LM != -1 && b > cache[cache[0]]+12 && N>2)
	addi.n	a4, a4, 12	# tmp533, *_14,
# @OPUS@\upstream\celt\bands.c:988:    if (LM != -1 && b > cache[cache[0]]+12 && N>2)
	bge	a4, a14, .L22	# tmp533, b,
# @OPUS@\upstream\celt\bands.c:988:    if (LM != -1 && b > cache[cache[0]]+12 && N>2)
	blti	a3, 3, .L22	# N,,
# @OPUS@\upstream\celt\bands.c:997:       N >>= 1;
	srai	a3, a3, 1	#, N,
# @OPUS@\upstream\celt\bands.c:998:       Y = X+N;
	slli	a5, a3, 1	#,,
# @OPUS@\upstream\celt\bands.c:998:       Y = X+N;
	add.n	a2, a15, a5	#, X,
# @OPUS@\upstream\celt\bands.c:999:       LM -= 1;
	addi.n	a9, a9, -1	#, LM,
# @OPUS@\upstream\celt\bands.c:997:       N >>= 1;
	s32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:998:       Y = X+N;
	s32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:998:       Y = X+N;
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\bands.c:999:       LM -= 1;
	s32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\celt\bands.c:1000:       if (B==1)
	bnei	a13, 1, .L25	# B,,
# @OPUS@\upstream\celt\bands.c:1001:          fill = (fill&1)|(fill<<1);
	l32i	a4, sp, 120	# fill,
	extui	a3, a4, 0, 1	# tmp540,,
# @OPUS@\upstream\celt\bands.c:1001:          fill = (fill&1)|(fill<<1);
	slli	a2, a4, 1	# tmp541,,
# @OPUS@\upstream\celt\bands.c:1001:          fill = (fill&1)|(fill<<1);
	or	a2, a3, a2	#, tmp540, tmp541
	s32i	a2, sp, 120	# fill,
.L25:
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l32i.n	a2, a8, 48	# m_144->logN, m_144->logN
	slli	a10, a10, 1	# tmp543, i,
	add.n	a10, a2, a10	# tmp544, m_144->logN, tmp543
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l16si	a4, a10, 0	# *_241, tmp545
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	slli	a2, a5, 3	# tmp548,,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	add.n	a4, a4, a2	# pulse_cap, tmp545, tmp548
# @OPUS@\upstream\celt\bands.c:658:    int N2 = 2*N-1;
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	srai	a2, a4, 1	# tmp550, pulse_cap,
# @OPUS@\upstream\celt\bands.c:658:    int N2 = 2*N-1;
	addi.n	a3, a5, -1	# N2,,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	addi	a2, a2, -4	# offset, tmp550,
# @OPUS@\upstream\celt\bands.c:664:    qb = celt_sudiv(b+N2*offset, N2);
	mull	a2, a2, a3	# tmp552, offset, N2
# @OPUS@\upstream\celt\bands.c:1002:       B = (B+1)>>1;
	addi.n	a5, a13, 1	# _26, B,
# @OPUS@\upstream\celt\bands.c:1002:       B = (B+1)>>1;
	srai	a5, a5, 1	#, _26,
# @OPUS@\upstream\celt\entcode.h:148:    return n/d;
	add.n	a2, a2, a14	#, tmp552, b
	s32i	a4, sp, 64	#,
	s32i	a7, sp, 68	#,
# @OPUS@\upstream\celt\bands.c:1002:       B = (B+1)>>1;
	s32i.n	a5, sp, 40	# %sfp,
# @OPUS@\upstream\celt\entcode.h:148:    return n/d;
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	l32i	a4, sp, 64	#,
	addi	a3, a14, -32	# tmp558, b,
	sub	a4, a3, a4	# tmp559, tmp558, pulse_cap
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	l32i	a7, sp, 68	#,
	bge	a4, a2, .L26	# tmp559, qb,
	mov.n	a2, a4	# qb, tmp559
.L26:
# @OPUS@\upstream\celt\bands.c:669:    if (qb<(1<<BITRES>>1)) {
	bgei	a2, 4, .L27	# qb,,
# @OPUS@\upstream\celt\bands.c:752:    if (encode)
	bnez.n	a7, .L28	# _207,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	l32i.n	a2, sp, 20	# %sfp,
	call0	ec_tell_frac		#
	mov.n	a11, a2	# _134,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i.n	a2, sp, 20	# %sfp,
	s32i	a11, sp, 72	#,
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i	a11, sp, 72	#,
	sub	a11, a2, a11	# qalloc,, _134
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a10, a14, a11	# _254, b, qalloc
	j	.L29		#
.L27:
# @OPUS@\upstream\celt\bands.c:667:    qb = IMIN(8<<BITRES, qb);
	movi.n	a3, 0x40	# tmp562,
	bge	a3, a2, .L30	# tmp562, qb,
	mov.n	a2, a3	# qb, tmp562
.L30:
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	extui	a3, a2, 0, 3	# tmp564, qb,
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	slli	a4, a3, 1	# tmp565, tmp564,
	l32r	a3, .LC3	#, tmp563
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	srai	a2, a2, 3	# tmp570, qb,
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	add.n	a3, a3, a4	# tmp566, tmp563, tmp565
	l16si	a3, a3, 0	# exp2_table8, tmp567
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	movi.n	a4, 0xe	# tmp571,
	sub	a2, a4, a2	# tmp572, tmp571, tmp570
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	ssr	a2	# tmp572
	sra	a2, a3	# qn, tmp567
# @OPUS@\upstream\celt\bands.c:673:       qn = (qn+1)>>1<<1;
	addi.n	a2, a2, 1	# _608, qn,
# @OPUS@\upstream\celt\bands.c:673:       qn = (qn+1)>>1<<1;
	movi.n	a3, -2	# tmp574,
	and	a3, a2, a3	#, _608, tmp574
	s32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:752:    if (encode)
	beqz.n	a7, .L128	# _207,
	j	.L31		#
.L84:
# @OPUS@\upstream\celt\bands.c:768:             if (!stereo && ctx->avoid_split_noise && itheta > 0 && itheta < qn)
	srai	a2, a2, 31	# tmp577, _263,
	sub	a2, a2, a7	# tmp578, tmp577, itheta
	slli	a6, a7, 14	# tmp931, itheta,
# @OPUS@\upstream\celt\bands.c:768:             if (!stereo && ctx->avoid_split_noise && itheta > 0 && itheta < qn)
	bgez	a2, .L33	# tmp578,
# @OPUS@\upstream\celt\bands.c:768:             if (!stereo && ctx->avoid_split_noise && itheta > 0 && itheta < qn)
	l32i.n	a2, sp, 28	# %sfp,
	bge	a7, a2, .L33	# itheta,,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a2	#,
	mov.n	a2, a6	#, tmp931
	s32i.n	a6, sp, 60	#,
	s32i	a7, sp, 68	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:774:                imid = bitexact_cos((opus_int16)unquantized);
	slli	a3, a2, 16	# tmp589,,
# @OPUS@\upstream\celt\bands.c:775:                iside = bitexact_cos((opus_int16)(16384-unquantized));
	l32r	a2, .LC7	#, tmp617
# @OPUS@\upstream\celt\bands.c:774:                imid = bitexact_cos((opus_int16)unquantized);
	srai	a3, a3, 16	# _273, tmp589,
# @OPUS@\upstream\celt\bands.c:775:                iside = bitexact_cos((opus_int16)(16384-unquantized));
	sub	a2, a2, a3	# tmp616, tmp617, _273
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	mul16s	a2, a2, a2	# tmp619, tmp616, tmp616
	mull	a3, a3, a3	# tmp590, _273, _273
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	addmi	a2, a2, 0x1000	# tmp620, tmp619,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a2, a2, 3	# tmp622, tmp620,
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	addmi	a3, a3, 0x1000	# tmp591, tmp590,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	srai	a4, a2, 16	# x2, tmp622,
	slli	a3, a3, 3	# tmp593, tmp591,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	movi	a2, -0x272	# tmp594,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	srai	a5, a3, 16	# x2, tmp593,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a3, a2, a4	# tmp624, tmp594, x2
	mul16s	a2, a2, a5	# tmp595, tmp594, x2
	l32r	a8, .LC4	#, tmp600
	addmi	a3, a3, 0x4000	# tmp625, tmp624,
	addmi	a2, a2, 0x4000	# tmp596, tmp595,
	srai	a3, a3, 15	# tmp626, tmp625,
	add.n	a3, a3, a8	# tmp628, tmp626, tmp600
	srai	a2, a2, 15	# tmp597, tmp596,
	add.n	a2, a2, a8	# tmp599, tmp597, tmp600
	mul16s	a3, a3, a4	# tmp630, tmp628, x2
	mul16s	a2, a2, a5	# tmp601, tmp599, x2
	l32r	a8, .LC5	#, tmp606
	addmi	a3, a3, 0x4000	# tmp631, tmp630,
	addmi	a2, a2, 0x4000	# tmp602, tmp601,
	srai	a3, a3, 15	# tmp632, tmp631,
	add.n	a3, a3, a8	# tmp634, tmp632, tmp606
	srai	a2, a2, 15	# tmp603, tmp602,
	add.n	a2, a2, a8	# tmp605, tmp603, tmp606
	mul16s	a3, a3, a4	# tmp636, tmp634, x2
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	l32r	a9, .LC6	#, tmp611
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a2, a2, a5	# tmp607, tmp605, x2
	addmi	a3, a3, 0x4000	# tmp637, tmp636,
	srai	a8, a3, 15	# tmp638, tmp637,
	addmi	a2, a2, 0x4000	# tmp608, tmp607,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a3, a9, a4	# tmp639, tmp611, x2
	add.n	a3, a8, a3	# tmp643, tmp638, tmp639
	sub	a4, a9, a5	# tmp610, tmp611, x2
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	srai	a2, a2, 15	# tmp609, tmp608,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	add.n	a2, a2, a4	# tmp614, tmp609, tmp610
	slli	a3, a3, 16	# tmp644, tmp643,
	srai	a3, a3, 16	# _323, tmp644,
	slli	a2, a2, 16	# tmp615, tmp614,
	srai	a4, a2, 16	# _297, tmp615,
# @OPUS@\upstream\celt\bands.c:85:    ls=EC_ILOG(isin);
	nsau	a9, a3	# _614, _323
# @OPUS@\upstream\celt\bands.c:84:    lc=EC_ILOG(icos);
	nsau	a8, a4	# _612, _297
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	addi	a2, a9, -17	# tmp645, _614,
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	ssl	a2	# tmp645
	sll	a2, a3	# isin, _323
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	addi	a3, a8, -17	# tmp648, _612,
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	ssl	a3	# tmp648
	sll	a3, a4	# icos, _297
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	slli	a2, a2, 16	# tmp647, isin,
	srai	a4, a2, 16	# _623, tmp647,
	l32r	a10, .LC8	#, tmp652
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	slli	a2, a3, 16	# tmp650, icos,
	srai	a5, a2, 16	# _635, tmp650,
	mul16s	a3, a5, a10	# tmp664, _635, tmp665
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a2, a4, a10	# tmp651, _623, tmp652
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a3, a3, 0x4000	# tmp666, tmp664,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	l32r	a10, .LC9	#, tmp657
	addmi	a2, a2, 0x4000	# tmp653, tmp651,
	srai	a2, a2, 15	# tmp654, tmp653,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a3, a3, 15	# tmp667, tmp666,
	add.n	a3, a3, a10	# tmp669, tmp667, tmp657
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a2, a2, a10	# tmp656, tmp654, tmp657
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mul16s	a5, a3, a5	# tmp671, tmp669, _635
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a2, a2, a4	# tmp658, tmp656, _623
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	sub	a3, a8, a9	# tmp661, _612, _614
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	slli	a4, a3, 11	# tmp662, tmp661,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	addmi	a2, a2, 0x4000	# tmp659, tmp658,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a3, a5, 0x4000	# tmp672, tmp671,
# @OPUS@\upstream\celt\bands.c:776:                delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	srai	a2, a2, 15	# tmp660, tmp659,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a2, a2, a4	# tmp663, tmp660, tmp662
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a3, a3, 15	# tmp673, tmp672,
# @OPUS@\upstream\celt\bands.c:776:                delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	addi.n	a4, a5, -1	# tmp675,,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	sub	a2, a2, a3	# tmp674, tmp663, tmp673
# @OPUS@\upstream\celt\bands.c:776:                delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	slli	a3, a4, 7	# tmp676, tmp675,
	mul16s	a2, a2, a3	# tmp677, tmp674, tmp676
# @OPUS@\upstream\celt\bands.c:777:                if (delta > *b)
	l32i.n	a6, sp, 60	#,
# @OPUS@\upstream\celt\bands.c:776:                delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	addmi	a2, a2, 0x4000	# tmp678, tmp677,
# @OPUS@\upstream\celt\bands.c:776:                delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	srai	a2, a2, 15	# delta, tmp678,
# @OPUS@\upstream\celt\bands.c:777:                if (delta > *b)
	l32i	a7, sp, 68	#,
	blt	a14, a2, .L85	# b, delta,
# @OPUS@\upstream\celt\bands.c:779:                else if (delta < -*b)
	neg	a3, a14	# tmp679, b
# @OPUS@\upstream\celt\bands.c:779:                else if (delta < -*b)
	bge	a2, a3, .L33	# delta, tmp679,
# @OPUS@\upstream\celt\bands.c:780:                   itheta = 0;
	movi.n	a7, 0	# itheta,
	mov.n	a6, a7	# tmp931, itheta
	j	.L33		#
.L76:
# @OPUS@\upstream\celt\bands.c:818:             ec_enc_uint(ec, itheta, qn+1);
	l32i.n	a2, sp, 28	# %sfp,
	mov.n	a3, a7	#, itheta
	addi.n	a4, a2, 1	#,,
	l32i.n	a2, sp, 20	# %sfp,
	s32i.n	a6, sp, 60	#,
	call0	ec_enc_uint		#
	l32i.n	a6, sp, 60	#,
	j	.L35		#
.L78:
# @OPUS@\upstream\celt\bands.c:820:             itheta = ec_dec_uint(ec, qn+1);
	l32i.n	a7, sp, 28	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	addi.n	a3, a7, 1	#,,
	call0	ec_dec_uint		#
	slli	a6, a2, 14	# tmp931,,
	j	.L35		#
.L130:
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	l32i.n	a3, sp, 28	# %sfp,
	srai	a2, a3, 1	# _402,,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	addi.n	a5, a2, 1	# _403, _402,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	mull	a5, a5, a5	# ft, _403, _403
# @OPUS@\upstream\celt\bands.c:828:             fs = itheta <= (qn>>1) ? itheta + 1 : qn + 1 - itheta;
	blt	a2, a7, .L36	# _402, itheta,
	addi.n	a4, a7, 1	# iftmp$151_198, itheta,
# @OPUS@\upstream\celt\bands.c:829:             fl = itheta <= (qn>>1) ? itheta*(itheta + 1)>>1 :
	mull	a3, a7, a4	# tmp682, itheta, iftmp$151_198
# @OPUS@\upstream\celt\bands.c:829:             fl = itheta <= (qn>>1) ? itheta*(itheta + 1)>>1 :
	srai	a3, a3, 1	# iftmp$152_410, tmp682,
	j	.L37		#
.L36:
# @OPUS@\upstream\celt\bands.c:828:             fs = itheta <= (qn>>1) ? itheta + 1 : qn + 1 - itheta;
	sub	a7, a3, a7	# _406, tmp4, itheta
# @OPUS@\upstream\celt\bands.c:828:             fs = itheta <= (qn>>1) ? itheta + 1 : qn + 1 - itheta;
	addi.n	a4, a7, 1	# iftmp$151_198, _406,
# @OPUS@\upstream\celt\bands.c:830:              ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	addi.n	a3, a7, 2	# tmp683, _406,
# @OPUS@\upstream\celt\bands.c:830:              ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	mull	a3, a3, a4	# tmp684, tmp683, iftmp$151_198
# @OPUS@\upstream\celt\bands.c:830:              ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	srai	a3, a3, 1	# tmp685, tmp684,
# @OPUS@\upstream\celt\bands.c:829:             fl = itheta <= (qn>>1) ? itheta*(itheta + 1)>>1 :
	sub	a3, a5, a3	# iftmp$152_410, ft, tmp685
.L37:
# @OPUS@\upstream\celt\bands.c:832:             ec_encode(ec, fl, fl+fs, ft);
	l32i.n	a2, sp, 20	# %sfp,
	add.n	a4, a4, a3	#, iftmp$151_198, iftmp$152_410
	s32i.n	a6, sp, 60	#,
	call0	ec_encode		#
	l32i.n	a6, sp, 60	#,
	j	.L35		#
.L81:
# @OPUS@\upstream\celt\bands.c:841:                itheta = (isqrt32(8*(opus_uint32)fm + 1) - 1)>>1;
	slli	a2, a2, 3	# tmp687, _424,
# @OPUS@\upstream\celt\bands.c:841:                itheta = (isqrt32(8*(opus_uint32)fm + 1) - 1)>>1;
	addi.n	a2, a2, 1	#, tmp687,
	call0	isqrt32		#
# @OPUS@\upstream\celt\bands.c:841:                itheta = (isqrt32(8*(opus_uint32)fm + 1) - 1)>>1;
	addi.n	a2, a2, -1	# tmp689,,
# @OPUS@\upstream\celt\bands.c:841:                itheta = (isqrt32(8*(opus_uint32)fm + 1) - 1)>>1;
	srli	a7, a2, 1	# itheta, tmp689,
# @OPUS@\upstream\celt\bands.c:842:                fs = itheta + 1;
	addi.n	a4, a7, 1	# fs, itheta,
# @OPUS@\upstream\celt\bands.c:843:                fl = itheta*(itheta + 1)>>1;
	mull	a3, a7, a4	# tmp690, itheta, fs
# @OPUS@\upstream\celt\bands.c:843:                fl = itheta*(itheta + 1)>>1;
	srai	a3, a3, 1	# fl, tmp690,
	j	.L38		#
.L132:
# @OPUS@\upstream\celt\bands.c:848:                 - isqrt32(8*(opus_uint32)(ft - fm - 1) + 1))>>1;
	l32i.n	a5, sp, 56	# %sfp,
	addi.n	a3, a5, -1	# tmp691,,
	sub	a2, a3, a2	# tmp692, tmp691, _424
	slli	a2, a2, 3	# tmp693, tmp692,
# @OPUS@\upstream\celt\bands.c:848:                 - isqrt32(8*(opus_uint32)(ft - fm - 1) + 1))>>1;
	addi.n	a2, a2, 1	#, tmp693,
	call0	isqrt32		#
# @OPUS@\upstream\celt\bands.c:847:                itheta = (2*(qn + 1)
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:850:                fl = ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	l32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:847:                itheta = (2*(qn + 1)
	addi.n	a3, a7, 1	# tmp695,,
	slli	a3, a3, 1	# tmp696, tmp695,
# @OPUS@\upstream\celt\bands.c:848:                 - isqrt32(8*(opus_uint32)(ft - fm - 1) + 1))>>1;
	sub	a2, a3, a2	# tmp697, tmp696,
# @OPUS@\upstream\celt\bands.c:849:                fs = qn + 1 - itheta;
	l32i.n	a3, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:848:                 - isqrt32(8*(opus_uint32)(ft - fm - 1) + 1))>>1;
	srli	a7, a2, 1	# itheta, tmp697,
# @OPUS@\upstream\celt\bands.c:849:                fs = qn + 1 - itheta;
	sub	a2, a3, a7	# _449,, itheta
# @OPUS@\upstream\celt\bands.c:849:                fs = qn + 1 - itheta;
	addi.n	a4, a2, 1	# fs, _449,
# @OPUS@\upstream\celt\bands.c:850:                fl = ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	addi.n	a3, a2, 2	# tmp698, _449,
# @OPUS@\upstream\celt\bands.c:850:                fl = ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	mull	a3, a3, a4	# tmp699, tmp698, fs
# @OPUS@\upstream\celt\bands.c:850:                fl = ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	srai	a3, a3, 1	# tmp700, tmp699,
# @OPUS@\upstream\celt\bands.c:850:                fl = ft - ((qn + 1 - itheta)*(qn + 2 - itheta)>>1);
	sub	a3, a5, a3	# fl,, tmp700
.L38:
# @OPUS@\upstream\celt\bands.c:853:             ec_dec_update(ec, fl, fl+fs, ft);
	l32i.n	a5, sp, 56	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	add.n	a4, a3, a4	#, fl, fs
	s32i	a7, sp, 68	#,
	call0	ec_dec_update		#
	l32i	a7, sp, 68	#,
	slli	a6, a7, 14	# tmp931, itheta,
.L35:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a3, sp, 28	# %sfp,
	mov.n	a2, a6	#, tmp931
	call0	__udivsi3		#
	s32i.n	a2, sp, 28	# %sfp,
.L83:
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i.n	a2, sp, 20	# %sfp,
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i.n	a7, sp, 48	# %sfp,
	sub	a11, a2, a7	# qalloc,,
# @OPUS@\upstream\celt\bands.c:895:    if (itheta == 0)
	l32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a10, a14, a11	# _254, b, qalloc
# @OPUS@\upstream\celt\bands.c:895:    if (itheta == 0)
	bnez.n	a2, .L39	#,
.L29:
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:899:       *fill &= (1<<B)-1;
	l32i.n	a4, sp, 40	# %sfp,
	slli	a2, a7, 15	# tmp710,,
	movi.n	a3, 1	# tmp706,
	sub	a2, a2, a7	# tmp711, tmp710,
	ssl	a4	#
	sll	a3, a3	# tmp707, tmp706
# @OPUS@\upstream\celt\bands.c:899:       *fill &= (1<<B)-1;
	l32i	a7, sp, 120	# fill,
# @OPUS@\upstream\celt\bands.c:899:       *fill &= (1<<B)-1;
	addi.n	a3, a3, -1	# tmp708, tmp707,
	addmi	a2, a2, 0x4000	# tmp712, tmp711,
# @OPUS@\upstream\celt\bands.c:899:       *fill &= (1<<B)-1;
	movi.n	a5, 0	#,
	srai	a2, a2, 15	#, tmp712,
	and	a7, a7, a3	#,, tmp708
	s32i.n	a2, sp, 48	# %sfp,
	s32i.n	a5, sp, 20	# %sfp,
	s32i	a7, sp, 120	# fill,
	s32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:900:       delta = -16384;
	l32r	a2, .LC2	#, delta
	j	.L40		#
.L39:
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\bands.c:901:    } else if (itheta == 16384)
	l32r	a2, .LC7	#, tmp713
	bne	a3, a2, .L41	#, tmp713,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	l32i.n	a4, sp, 40	# %sfp,
	l32i.n	a7, sp, 16	# %sfp,
	movi.n	a2, 1	# tmp714,
	ssl	a4	#
	sll	a2, a2	# tmp715, tmp714
	slli	a3, a7, 15	# tmp719,,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	addi.n	a2, a2, -1	# tmp716, tmp715,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	ssl	a4	#
	sll	a2, a2	# tmp717, tmp716
	sub	a3, a3, a7	# tmp720, tmp719,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	l32i	a4, sp, 120	# fill,
	addmi	a3, a3, 0x4000	# tmp721, tmp720,
	and	a4, a4, a2	#,, tmp717
	srai	a3, a3, 15	#, tmp721,
	movi.n	a5, 0	#,
	s32i	a4, sp, 120	# fill,
	s32i.n	a3, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:906:       delta = 16384;
	l32i.n	a2, sp, 28	# %sfp, delta
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	s32i.n	a5, sp, 48	# %sfp,
	j	.L40		#
.L41:
# @OPUS@\upstream\celt\bands.c:908:       imid = bitexact_cos((opus_int16)itheta);
	slli	a3, a3, 16	# tmp722, tmp7,
	srai	a3, a3, 16	# _518, tmp722,
# @OPUS@\upstream\celt\bands.c:909:       iside = bitexact_cos((opus_int16)(16384-itheta));
	sub	a2, a2, a3	# tmp749, tmp713, _518
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	mul16s	a2, a2, a2	# tmp752, tmp749, tmp749
	mull	a3, a3, a3	# tmp723, _518, _518
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	addmi	a2, a2, 0x1000	# tmp753, tmp752,
	addmi	a3, a3, 0x1000	# tmp724, tmp723,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a2, a2, 3	# tmp755, tmp753,
	srai	a2, a2, 16	# x2, tmp755,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	movi	a4, -0x272	# tmp727,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a3, a3, 3	# tmp726, tmp724,
	srai	a3, a3, 16	# x2, tmp726,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a5, a4, a2	# tmp757, tmp727, x2
	mul16s	a4, a4, a3	# tmp728, tmp727, x2
	l32r	a6, .LC4	#, tmp733
	addmi	a5, a5, 0x4000	# tmp758, tmp757,
	addmi	a4, a4, 0x4000	# tmp729, tmp728,
	srai	a5, a5, 15	# tmp759, tmp758,
	add.n	a5, a5, a6	# tmp761, tmp759, tmp733
	srai	a4, a4, 15	# tmp730, tmp729,
	add.n	a4, a4, a6	# tmp732, tmp730, tmp733
	mul16s	a5, a5, a2	# tmp763, tmp761, x2
	mul16s	a4, a4, a3	# tmp734, tmp732, x2
	l32r	a6, .LC5	#, tmp739
	addmi	a5, a5, 0x4000	# tmp764, tmp763,
	addmi	a4, a4, 0x4000	# tmp735, tmp734,
	srai	a5, a5, 15	# tmp765, tmp764,
	add.n	a5, a5, a6	# tmp767, tmp765, tmp739
	srai	a4, a4, 15	# tmp736, tmp735,
	add.n	a4, a4, a6	# tmp738, tmp736, tmp739
	mul16s	a5, a5, a2	# tmp769, tmp767, x2
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	l32r	a7, .LC6	#, tmp744
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a4, a4, a3	# tmp740, tmp738, x2
	addmi	a5, a5, 0x4000	# tmp770, tmp769,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a2, a7, a2	# tmp772, tmp744, x2
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	srai	a5, a5, 15	# tmp771, tmp770,
	addmi	a4, a4, 0x4000	# tmp741, tmp740,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a7, a7, a3	# tmp743, tmp744, x2
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	srai	a4, a4, 15	# tmp742, tmp741,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	add.n	a3, a5, a2	# tmp776, tmp771, tmp772
	slli	a3, a3, 16	# tmp777, tmp776,
	add.n	a2, a4, a7	# tmp747, tmp742, tmp743
	srai	a3, a3, 16	# _568, tmp777,
	slli	a2, a2, 16	# tmp748, tmp747,
	srai	a2, a2, 16	# _542, tmp748,
# @OPUS@\upstream\celt\bands.c:85:    ls=EC_ILOG(isin);
	nsau	a9, a3	# _650, _568
# @OPUS@\upstream\celt\bands.c:84:    lc=EC_ILOG(icos);
	nsau	a8, a2	# _648, _542
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	addi	a7, a9, -17	# tmp778, _650,
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	ssl	a7	# tmp778
	sll	a7, a3	# isin, _568
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	addi	a6, a8, -17	# tmp781, _648,
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	ssl	a6	# tmp781
	sll	a6, a2	# icos, _542
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	l32r	a5, .LC8	#, tmp785
	slli	a7, a7, 16	# tmp780, isin,
	srai	a7, a7, 16	# _659, tmp780,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	slli	a6, a6, 16	# tmp783, icos,
	srai	a6, a6, 16	# _671, tmp783,
	mov.n	a4, a5	# tmp798, tmp785
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a5, a7, a5	# tmp784, _659, tmp785
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mul16s	a4, a6, a4	# tmp797, _671, tmp798
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	l32r	a14, .LC9	#, tmp790
	addmi	a5, a5, 0x4000	# tmp786, tmp784,
	srai	a5, a5, 15	# tmp787, tmp786,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a4, a4, 0x4000	# tmp799, tmp797,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a5, a5, a14	# tmp789, tmp787, tmp790
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a4, a4, 15	# tmp800, tmp799,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a5, a5, a7	# tmp791, tmp789, _659
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	add.n	a4, a4, a14	# tmp802, tmp800, tmp790
	mul16s	a4, a4, a6	# tmp804, tmp802, _671
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	l32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	addmi	a5, a5, 0x4000	# tmp792, tmp791,
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	sub	a8, a8, a9	# tmp794, _648, _650
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	addi.n	a6, a7, -1	# tmp808,,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	srai	a5, a5, 15	# tmp793, tmp792,
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	slli	a8, a8, 11	# tmp795, tmp794,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a4, a4, 0x4000	# tmp805, tmp804,
	srai	a4, a4, 15	# tmp806, tmp805,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a5, a5, a8	# tmp796, tmp793, tmp795
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	sub	a5, a5, a4	# tmp807, tmp796, tmp806
	mull	a2, a2, a7	# tmp816, _542,
	mull	a4, a3, a7	# tmp812, _568,
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	slli	a6, a6, 7	# tmp809, tmp808,
	addmi	a3, a2, 0x4000	# tmp817, tmp816,
	addmi	a4, a4, 0x4000	# tmp813, tmp812,
	mul16s	a5, a5, a6	# tmp810, tmp807, tmp809
	slli	a4, a4, 1	# tmp815, tmp813,
	slli	a3, a3, 1	# tmp819, tmp817,
	srai	a4, a4, 16	#, tmp815,
	srai	a3, a3, 16	#, tmp819,
	addmi	a2, a5, 0x4000	# tmp811, tmp810,
	s32i.n	a4, sp, 20	# %sfp,
	s32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	srai	a2, a2, 15	# delta, tmp811,
# @OPUS@\upstream\celt\bands.c:1019:       if (B0>1 && (itheta&0x3fff))
	blti	a13, 2, .L40	# B,,
# @OPUS@\upstream\celt\bands.c:1019:       if (B0>1 && (itheta&0x3fff))
	l32i.n	a4, sp, 28	# %sfp,
	extui	a3, a4, 0, 14	# tmp820,,
# @OPUS@\upstream\celt\bands.c:1019:       if (B0>1 && (itheta&0x3fff))
	beqz.n	a3, .L40	# tmp820,
# @OPUS@\upstream\celt\bands.c:1021:          if (itheta > 8192)
	l32r	a3, .LC10	#, tmp821
	bge	a3, a4, .L42	# tmp821,,
# @OPUS@\upstream\celt\bands.c:1023:             delta -= delta>>(4-LM);
	l32i.n	a5, sp, 44	# %sfp,
	movi.n	a3, 4	# tmp822,
	sub	a3, a3, a5	# tmp823, tmp822,
# @OPUS@\upstream\celt\bands.c:1023:             delta -= delta>>(4-LM);
	ssr	a3	# tmp823
	sra	a3, a2	# tmp824, delta
# @OPUS@\upstream\celt\bands.c:1023:             delta -= delta>>(4-LM);
	sub	a2, a2, a3	# delta, delta, tmp824
	j	.L40		#
.L42:
# @OPUS@\upstream\celt\bands.c:1026:             delta = IMIN(0, delta + (N<<BITRES>>(5-LM)));
	l32i.n	a7, sp, 36	# %sfp,
	l32i.n	a5, sp, 44	# %sfp,
	movi.n	a4, 5	# tmp826,
	slli	a3, a7, 3	# tmp825,,
	sub	a4, a4, a5	# tmp827, tmp826,
	ssr	a4	# tmp827
	sra	a3, a3	# tmp828, tmp825
	add.n	a2, a2, a3	# delta, delta, tmp828
# @OPUS@\upstream\celt\bands.c:1026:             delta = IMIN(0, delta + (N<<BITRES>>(5-LM)));
	blti	a2, 1, .L40	# delta,,
	movi.n	a2, 0	# delta,
.L40:
# @OPUS@\upstream\celt\bands.c:1028:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	sub	a2, a10, a2	# tmp831, _254, delta
	extui	a14, a2, 31, 1	# tmp833, tmp831,
	add.n	a14, a14, a2	# tmp834, tmp833, tmp831
	srai	a14, a14, 1	# mbits, tmp834,
	bge	a10, a14, .L44	# _254, mbits,
	mov.n	a14, a10	# mbits, _254
.L44:
# @OPUS@\upstream\celt\bands.c:1030:       ctx->remaining_bits -= qalloc;
	l32i.n	a7, a12, 32	# ctx_143(D)->remaining_bits,
# @OPUS@\upstream\celt\bands.c:1033:          next_lowband2 = lowband+N; /* >32-bit split case */
	l32i.n	a4, sp, 24	# %sfp,
# @OPUS@\upstream\celt\bands.c:1030:       ctx->remaining_bits -= qalloc;
	sub	a3, a7, a11	# tmp837,, qalloc
	s32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:1033:          next_lowband2 = lowband+N; /* >32-bit split case */
	l32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:1028:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	movi.n	a2, 0	# tmp836,
# @OPUS@\upstream\celt\bands.c:1033:          next_lowband2 = lowband+N; /* >32-bit split case */
	add.n	a8, a4, a7	# tmp951,,
# @OPUS@\upstream\celt\bands.c:1028:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	movltz	a14, a2, a14	# mbits, tmp836, mbits
# @OPUS@\upstream\celt\bands.c:1030:       ctx->remaining_bits -= qalloc;
	s32i.n	a3, a12, 32	# ctx_143(D)->remaining_bits, tmp837
# @OPUS@\upstream\celt\bands.c:1033:          next_lowband2 = lowband+N; /* >32-bit split case */
	moveqz	a8, a2, a4	# next_lowband2, tmp836,
	l32i.n	a3, sp, 40	# %sfp,
	l32i	a2, sp, 120	# fill,
# @OPUS@\upstream\celt\bands.c:1029:       sbits = b-mbits;
	sub	a9, a10, a14	# sbits, _254, mbits
	ssr	a3	#
	sra	a2, a2	#,
	s32i.n	a2, sp, 32	# %sfp,
	srai	a13, a13, 1	# _854, B,
# @OPUS@\upstream\celt\bands.c:1036:       if (mbits >= sbits)
	blt	a14, a9, .L46	# mbits, sbits,
# @OPUS@\upstream\celt\bands.c:1038:          cm = quant_partition(ctx, X, N, mbits, B, lowband, LM,
	l32i	a4, sp, 120	# fill,
	l32i.n	a7, sp, 44	# %sfp,
	l32i.n	a5, sp, 48	# %sfp,
	s32i.n	a4, sp, 8	#,
	s32i.n	a7, sp, 0	#,
	l32i.n	a4, sp, 36	# %sfp,
	l32i.n	a7, sp, 24	# %sfp,
	s32i.n	a5, sp, 4	#,
	mov.n	a6, a3	#,
	mov.n	a5, a14	#, mbits
	mov.n	a3, a15	#, X
	mov.n	a2, a12	#, ctx
	s32i.n	a8, sp, 60	#,
	s32i	a9, sp, 68	#,
	s32i	a10, sp, 64	#,
	s32i	a11, sp, 72	#,
	call0	quant_partition		#
	mov.n	a15, a2	# cm,
# @OPUS@\upstream\celt\bands.c:1040:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	l32i.n	a4, sp, 16	# %sfp,
	l32i.n	a2, a12, 32	# ctx_143(D)->remaining_bits, ctx_143(D)->remaining_bits
	l32i	a11, sp, 72	#,
	sub	a2, a2, a4	# tmp838, ctx_143(D)->remaining_bits,
	add.n	a2, a2, a11	# _49, tmp838, qalloc
# @OPUS@\upstream\celt\bands.c:1041:          if (rebalance > 3<<BITRES && itheta!=0)
	movi.n	a3, 0x18	# tmp843,
# @OPUS@\upstream\celt\bands.c:1040:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	add.n	a14, a2, a14	# rebalance, _49, mbits
# @OPUS@\upstream\celt\bands.c:1041:          if (rebalance > 3<<BITRES && itheta!=0)
	l32i.n	a8, sp, 60	#,
	l32i	a9, sp, 68	#,
	l32i	a10, sp, 64	#,
	bge	a3, a14, .L47	# tmp843, rebalance,
# @OPUS@\upstream\celt\bands.c:1041:          if (rebalance > 3<<BITRES && itheta!=0)
	l32i.n	a5, sp, 28	# %sfp,
	beqz.n	a5, .L47	#,
# @OPUS@\upstream\celt\bands.c:1042:             sbits += rebalance - (3<<BITRES);
	addi	a9, a10, -24	# tmp850, _254,
	add.n	a9, a9, a2	# sbits, tmp850, _49
.L47:
# @OPUS@\upstream\celt\bands.c:1043:          cm |= quant_partition(ctx, Y, N, sbits, B, next_lowband2, LM,
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a7, sp, 32	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	s32i.n	a3, sp, 0	#,
	l32i.n	a6, sp, 40	# %sfp,
	l32i.n	a4, sp, 36	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
	s32i.n	a7, sp, 8	#,
	s32i.n	a2, sp, 4	#,
	mov.n	a7, a8	#, next_lowband2
	mov.n	a5, a9	#, sbits
	mov.n	a2, a12	#, ctx
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1044:                MULT16_16_P15(gain,side), fill>>B)<<(B0>>1);
	ssl	a13	# _854
	sll	a13, a2	# tmp851,
# @OPUS@\upstream\celt\bands.c:1043:          cm |= quant_partition(ctx, Y, N, sbits, B, next_lowband2, LM,
	or	a14, a13, a15	# <retval>, tmp851, cm
	j	.L21		#
.L46:
# @OPUS@\upstream\celt\bands.c:1046:          cm = quant_partition(ctx, Y, N, sbits, B, next_lowband2, LM,
	l32i.n	a5, sp, 20	# %sfp,
	l32i.n	a7, sp, 44	# %sfp,
	mov.n	a6, a3	#,
	l32i.n	a4, sp, 36	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
	s32i.n	a2, sp, 8	#, tmp4
	s32i.n	a5, sp, 4	#,
	s32i.n	a7, sp, 0	#,
	mov.n	a5, a9	#, sbits
	mov.n	a7, a8	#, next_lowband2
	mov.n	a2, a12	#, ctx
	s32i	a9, sp, 68	#,
	s32i	a11, sp, 72	#,
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1048:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	l32i.n	a3, a12, 32	# ctx_143(D)->remaining_bits, ctx_143(D)->remaining_bits
	l32i.n	a5, sp, 16	# %sfp,
	l32i	a11, sp, 72	#,
	sub	a3, a3, a5	# tmp852, ctx_143(D)->remaining_bits,
# @OPUS@\upstream\celt\bands.c:1048:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	l32i	a9, sp, 68	#,
# @OPUS@\upstream\celt\bands.c:1048:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	add.n	a3, a3, a11	# tmp854, tmp852, qalloc
# @OPUS@\upstream\celt\bands.c:1049:          if (rebalance > 3<<BITRES && itheta!=16384)
	movi.n	a4, 0x18	# tmp857,
# @OPUS@\upstream\celt\bands.c:1048:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	add.n	a9, a3, a9	# rebalance, tmp854, sbits
# @OPUS@\upstream\celt\bands.c:1046:          cm = quant_partition(ctx, Y, N, sbits, B, next_lowband2, LM,
	ssl	a13	# _854
	sll	a13, a2	# cm,
# @OPUS@\upstream\celt\bands.c:1049:          if (rebalance > 3<<BITRES && itheta!=16384)
	bge	a4, a9, .L50	# tmp857, rebalance,
# @OPUS@\upstream\celt\bands.c:1049:          if (rebalance > 3<<BITRES && itheta!=16384)
	l32i.n	a7, sp, 28	# %sfp,
	addmi	a2, a7, -0x4000	# tmp861,,
# @OPUS@\upstream\celt\bands.c:1049:          if (rebalance > 3<<BITRES && itheta!=16384)
	beqz.n	a2, .L50	# tmp861,
	addi	a14, a14, -24	# _755, mbits,
# @OPUS@\upstream\celt\bands.c:1050:             mbits += rebalance - (3<<BITRES);
	add.n	a14, a9, a14	# mbits, rebalance, _755
.L50:
# @OPUS@\upstream\celt\bands.c:1051:          cm |= quant_partition(ctx, X, N, mbits, B, lowband, LM,
	l32i.n	a4, sp, 44	# %sfp,
	l32i	a2, sp, 120	# fill,
	l32i.n	a3, sp, 48	# %sfp,
	s32i.n	a4, sp, 0	#,
	l32i.n	a7, sp, 24	# %sfp,
	l32i.n	a6, sp, 40	# %sfp,
	l32i.n	a4, sp, 36	# %sfp,
	s32i.n	a2, sp, 8	#,
	s32i.n	a3, sp, 4	#,
	mov.n	a5, a14	#, mbits
	mov.n	a3, a15	#, X
	mov.n	a2, a12	#, ctx
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1051:          cm |= quant_partition(ctx, X, N, mbits, B, lowband, LM,
	or	a14, a13, a2	# <retval>, cm,
# @OPUS@\upstream\celt\bands.c:989:    {
	j	.L21		#
.L22:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a9, a6, 1	# tmp865, hi,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a9, a9, 1	# lo, tmp865,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a4, a2, a9	# tmp866, tmp933, lo
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a4, a4, 0	# *_590, *_590
# @OPUS@\upstream\celt\rate.h:64:    bits--;
	addi.n	a8, a14, -1	# bits, b,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a4, a8, .L53	# *_590, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a9	# hi, lo
# @OPUS@\upstream\celt\rate.h:62:    lo = 0;
	movi.n	a9, 0	# lo,
.L53:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a4, a9, a6	# tmp868, lo, hi
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a4, a4, 1	# tmp869, tmp868,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a4, a4, 1	# mid, tmp869,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a10, a2, a4	# tmp870, tmp933, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a10, a10, 0	# *_975, *_975
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a10, a8, .L54	# *_975, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a4	# hi, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a4, a9	# mid, lo
.L54:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a9, a4, a6	# tmp872, mid, hi
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a9, a9, 1	# tmp873, tmp872,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a9, a9, 1	# mid, tmp873,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a10, a2, a9	# tmp874, tmp933, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a10, a10, 0	# *_708, *_708
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a10, a8, .L55	# *_708, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a9	# hi, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a9, a4	# mid, mid
.L55:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a4, a6, a9	# tmp876, hi, mid
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a4, a4, 1	# tmp877, tmp876,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a4, a4, 1	# lo, tmp877,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a10, a2, a4	# tmp878, tmp933, lo
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a10, a10, 0	# *_915, *_915
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a10, a8, .L56	# *_915, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a4	# hi, lo
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a4, a9	# lo, mid
.L56:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a9, a6, a4	# tmp880, hi, lo
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a9, a9, 1	# tmp881, tmp880,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a9, a9, 1	# lo, tmp881,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a10, a2, a9	# tmp882, tmp933, lo
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a10, a10, 0	# *_902, *_902
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a10, a8, .L57	# *_902, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a9	# hi, lo
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a9, a4	# lo, lo
.L57:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a4, a6, a9	# tmp884, hi, lo
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a4, a4, 1	# tmp885, tmp884,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a4, a4, 1	# q, tmp885,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a10, a2, a4	# tmp886, tmp933, q
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a10, a10, 0	# *_933, *_933
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	blt	a10, a8, .L58	# *_933, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a4	# hi, q
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a4, a9	# q, lo
.L58:
	add.n	a9, a2, a6	# tmp888, tmp933, hi
	l8ui	a9, a9, 0	# *_260, *_260
	sub	a9, a9, a8	# _982, *_260, bits
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	beqz.n	a4, .L59	# q,
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	add.n	a10, a2, a4	# tmp890, tmp933, q
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	l8ui	a11, a10, 0	# *_711, *_711
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	mov.n	a10, a4	# lo$230_710, q
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	sub	a8, a8, a11	# tmp892, bits, *_711
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	bge	a9, a8, .L60	# _982, tmp892,
.L80:
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	beqz.n	a6, .L61	# hi,
	mov.n	a10, a6	# lo$230_710, hi
	mov.n	a4, a6	# q, lo$230_710
.L60:
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	add.n	a10, a2, a10	# tmp894, tmp933, lo$230_710
	l8ui	a8, a10, 0	# *_210, *_210
# @OPUS@\upstream\celt\bands.c:1058:       ctx->remaining_bits -= curr_bits;
	l32i.n	a6, a12, 32	# ctx_143(D)->remaining_bits, ctx_143(D)->remaining_bits
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	addi.n	a8, a8, 1	# curr_bits, *_210,
# @OPUS@\upstream\celt\bands.c:1058:       ctx->remaining_bits -= curr_bits;
	sub	a6, a6, a8	# _92, ctx_143(D)->remaining_bits, curr_bits
	s32i.n	a6, a12, 32	# ctx_143(D)->remaining_bits, _92
# @OPUS@\upstream\celt\bands.c:1061:       while (ctx->remaining_bits < 0 && q > 0)
	bgez	a6, .L62	# _92,
.L63:
# @OPUS@\upstream\celt\bands.c:1063:          ctx->remaining_bits += curr_bits;
	add.n	a6, a6, a8	# _91, _92, curr_bits
# @OPUS@\upstream\celt\bands.c:1064:          q--;
	addi.n	a4, a4, -1	# q, q,
# @OPUS@\upstream\celt\bands.c:1063:          ctx->remaining_bits += curr_bits;
	s32i.n	a6, a12, 32	# ctx_143(D)->remaining_bits, _91
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	add.n	a8, a2, a4	# tmp897, tmp933, q
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	beqz.n	a4, .L61	# q,
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	l8ui	a8, a8, 0	# MEM[base: _893, offset: 0B], MEM[base: _893, offset: 0B]
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	addi.n	a8, a8, 1	# curr_bits, MEM[base: _893, offset: 0B],
# @OPUS@\upstream\celt\bands.c:1066:          ctx->remaining_bits -= curr_bits;
	sub	a6, a6, a8	# _92, _91, curr_bits
	s32i.n	a6, a12, 32	# ctx_143(D)->remaining_bits, _92
# @OPUS@\upstream\celt\bands.c:1061:       while (ctx->remaining_bits < 0 && q > 0)
	bltz	a6, .L63	# _92,
.L62:
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	blti	a4, 8, .L64	# q,,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	extui	a2, a4, 0, 3	# tmp899, q,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	srai	a4, a4, 3	# tmp901, q,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	addi.n	a2, a2, 8	# tmp900, tmp899,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	addi.n	a4, a4, -1	# tmp902, tmp901,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	ssl	a4	# tmp902
	sll	a4, a2	# q, tmp900
.L64:
# @OPUS@\upstream\celt\bands.c:1074:          if (encode)
	beqz.n	a7, .L65	# _207,
# @OPUS@\upstream\celt\bands.c:1076:             cm = alg_quant(X, N, K, spread, B, ec, gain, ctx->resynth, ctx->arch);
	l32i.n	a7, sp, 16	# %sfp,
	l32i.n	a6, a12, 44	# ctx_143(D)->arch, ctx_143(D)->arch
	l32i.n	a2, a12, 4	# ctx_143(D)->resynth, ctx_143(D)->resynth
	s32i.n	a7, sp, 0	#,
	l32i.n	a7, sp, 20	# %sfp,
	s32i.n	a6, sp, 8	#, ctx_143(D)->arch
	s32i.n	a2, sp, 4	#, ctx_143(D)->resynth
	mov.n	a6, a13	#, B
	mov.n	a2, a15	#, X
	call0	alg_quant		#
	mov.n	a14, a2	# <retval>,
	j	.L21		#
.L65:
# @OPUS@\upstream\celt\bands.c:1078:             cm = alg_unquant(X, N, K, spread, B, ec, gain);
	l32i.n	a7, sp, 16	# %sfp,
	mov.n	a6, a13	#, B
	s32i.n	a7, sp, 0	#,
	l32i.n	a7, sp, 20	# %sfp,
	mov.n	a2, a15	#, X
	call0	alg_unquant		#
	mov.n	a14, a2	# <retval>,
	j	.L21		#
.L61:
# @OPUS@\upstream\celt\bands.c:1083:          if (ctx->resynth)
	l32i.n	a2, a12, 4	# ctx_143(D)->resynth, ctx_143(D)->resynth
# @OPUS@\upstream\celt\bands.c:972:    unsigned cm=0;
	movi.n	a14, 0	# <retval>,
# @OPUS@\upstream\celt\bands.c:1083:          if (ctx->resynth)
	beq	a2, a14, .L21	# ctx_143(D)->resynth,,
# @OPUS@\upstream\celt\bands.c:1088:             cm_mask = (unsigned)(1UL<<B)-1;
	movi.n	a2, 1	# tmp906,
	ssl	a13	# B
	sll	a13, a2	# tmp907, tmp906
# @OPUS@\upstream\celt\bands.c:1089:             fill &= cm_mask;
	l32i	a2, sp, 120	# fill,
# @OPUS@\upstream\celt\bands.c:1088:             cm_mask = (unsigned)(1UL<<B)-1;
	addi.n	a13, a13, -1	# cm_mask, tmp907,
# @OPUS@\upstream\celt\bands.c:1089:             fill &= cm_mask;
	and	a14, a2, a13	# <retval>,, cm_mask
# @OPUS@\upstream\celt\bands.c:1090:             if (!fill)
	bnez.n	a14, .L66	# <retval>,
# @OPUS@\upstream\celt\bands.c:1092:                OPUS_CLEAR(X, N);
	movi.n	a4, 2	#,
	mov.n	a2, a15	#, X
	call0	yoradio_opus_clear		#
	j	.L21		#
.L66:
# @OPUS@\upstream\celt\bands.c:1094:                if (lowband == NULL)
	l32i.n	a4, sp, 24	# %sfp,
	beqz.n	a4, .L67	#,
# @OPUS@\upstream\celt\bands.c:1105:                   for (j=0;j<N;j++)
	bgei	a3, 1, .L68	# N,,
	j	.L69		#
.L67:
# @OPUS@\upstream\celt\bands.c:1097:                   for (j=0;j<N;j++)
	blti	a3, 1, .L88	# N,,
	slli	a6, a3, 1	# tmp908, N,
	l32i.n	a2, a12, 40	# ctx_143(D)->seed, ctx__seed_lsm$270
	l32r	a8, .LC11	#, tmp928
	l32r	a7, .LC12	#, tmp929
	mov.n	a4, a15	# ivtmp$274, X
	add.n	a6, a6, a15	# _921, tmp908, X
.L70:
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	mull	a2, a2, a8	# tmp909, ctx__seed_lsm$270, tmp928
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	add.n	a2, a2, a7	# ctx__seed_lsm$270, tmp909, tmp929
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	srai	a5, a2, 20	# tmp912, ctx__seed_lsm$270,
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	s16i	a5, a4, 0	# MEM[base: _907, offset: 0B], tmp912
	addi.n	a4, a4, 2	# ivtmp$274, ivtmp$274,
# @OPUS@\upstream\celt\bands.c:1097:                   for (j=0;j<N;j++)
	bne	a6, a4, .L70	# _921, ivtmp$274,
	j	.L129		#
.L68:
	slli	a9, a3, 1	# tmp913, N,
	l32i.n	a2, a12, 40	# ctx_143(D)->seed, ctx__seed_lsm$271
	l32r	a8, .LC11	#, tmp928
	l32r	a7, .LC12	#, tmp929
	l32r	a10, .LC13	#, tmp930
	mov.n	a5, a15	# ivtmp$278, X
	add.n	a9, a4, a9	# _943, ivtmp$277, tmp913
.L75:
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	mull	a2, a2, a8	# tmp914, ctx__seed_lsm$271, tmp928
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	l16ui	a6, a4, 0	#* ivtmp$277,
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	add.n	a2, a2, a7	# ctx__seed_lsm$271, tmp914, tmp929
	addi.n	a4, a4, 2	# ivtmp$277, ivtmp$277,
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	bany	a2, a10, .L72	# ctx__seed_lsm$271, tmp930,
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	addi	a6, a6, -4	# tmp920, MEM[base: _923, offset: 0B],
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	s16i	a6, a5, 0	#* ivtmp$278, tmp920
	addi.n	a5, a5, 2	# ivtmp$278, ivtmp$278,
# @OPUS@\upstream\celt\bands.c:1105:                   for (j=0;j<N;j++)
	bne	a4, a9, .L75	# ivtmp$277, _943,
	j	.L74		#
.L72:
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	addi.n	a6, a6, 4	# tmp922, MEM[base: _115, offset: 0B],
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	s16i	a6, a5, 0	#* ivtmp$278, tmp922
	addi.n	a5, a5, 2	# ivtmp$278, ivtmp$278,
# @OPUS@\upstream\celt\bands.c:1105:                   for (j=0;j<N;j++)
	bne	a4, a9, .L75	# ivtmp$277, _943,
.L74:
	s32i.n	a2, a12, 40	# ctx_143(D)->seed, ctx__seed_lsm$271
	j	.L69		#
.L129:
	s32i.n	a2, a12, 40	# ctx_143(D)->seed, ctx__seed_lsm$270
# @OPUS@\upstream\celt\bands.c:1097:                   for (j=0;j<N;j++)
	mov.n	a14, a13	# <retval>, cm_mask
	j	.L69		#
.L88:
	mov.n	a14, a13	# <retval>, cm_mask
.L69:
# @OPUS@\upstream\celt\bands.c:1116:                renormalise_vector(X, N, gain, ctx->arch);
	l32i.n	a5, a12, 44	# ctx_143(D)->arch,
	l32i.n	a4, sp, 16	# %sfp,
	mov.n	a2, a15	#, X
	call0	renormalise_vector		#
	j	.L21		#
.L85:
# @OPUS@\upstream\celt\bands.c:777:                if (delta > *b)
	l32i.n	a7, sp, 28	# %sfp, itheta
.L134:
	slli	a6, a7, 14	# tmp931, itheta,
.L33:
# @OPUS@\upstream\celt\bands.c:815:       } else if (B0>1 || stereo) {
	blti	a13, 2, .L130	# B,,
	j	.L76		#
.L128:
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	l32i.n	a2, sp, 20	# %sfp,
	call0	ec_tell_frac		#
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:815:       } else if (B0>1 || stereo) {
	blti	a13, 2, .L131	# B,,
	j	.L78		#
.L59:
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	bge	a9, a14, .L61	# _982, b,
	j	.L80		#
.L131:
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:837:             fm = ec_decode(ec, ft);
	l32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	srai	a5, a7, 1	# _758,,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	addi.n	a4, a5, 1	# _163, _758,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	mull	a7, a4, a4	#, _163, _163
# @OPUS@\upstream\celt\bands.c:837:             fm = ec_decode(ec, ft);
	s32i	a4, sp, 64	#,
	mov.n	a3, a7	#,
	s32i.n	a5, sp, 60	#,
# @OPUS@\upstream\celt\bands.c:823:          ft = ((qn>>1)+1)*((qn>>1)+1);
	s32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:837:             fm = ec_decode(ec, ft);
	call0	ec_decode		#
# @OPUS@\upstream\celt\bands.c:839:             if (fm < ((qn>>1)*((qn>>1) + 1)>>1))
	l32i	a4, sp, 64	#,
	l32i.n	a5, sp, 60	#,
	mull	a3, a4, a5	# tmp924, _163, _758
# @OPUS@\upstream\celt\bands.c:839:             if (fm < ((qn>>1)*((qn>>1) + 1)>>1))
	srai	a3, a3, 1	# tmp925, tmp924,
# @OPUS@\upstream\celt\bands.c:839:             if (fm < ((qn>>1)*((qn>>1) + 1)>>1))
	blt	a2, a3, .L81	# _424, tmp925,
	j	.L132		#
.L28:
# @OPUS@\upstream\celt\bands.c:758:       itheta = stereo_itheta(X, Y, stereo, N, ctx->arch);
	l32i.n	a6, a12, 44	# ctx_143(D)->arch,
	l32i.n	a5, sp, 36	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
	movi.n	a4, 0	#,
	mov.n	a2, a15	#, X
	call0	stereo_itheta		#
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	l32i.n	a2, sp, 20	# %sfp,
	call0	ec_tell_frac		#
	s32i.n	a2, sp, 48	# %sfp,
	j	.L83		#
.L31:
# @OPUS@\upstream\celt\bands.c:758:       itheta = stereo_itheta(X, Y, stereo, N, ctx->arch);
	l32i.n	a6, a12, 44	# ctx_143(D)->arch,
	l32i.n	a5, sp, 36	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
	movi.n	a4, 0	#,
	mov.n	a2, a15	#, X
	call0	stereo_itheta		#
	mov.n	a3, a2	# itheta,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	l32i.n	a2, sp, 20	# %sfp,
	s32i.n	a3, sp, 60	#,
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	l32i.n	a3, sp, 60	#,
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	mull	a2, a3, a7	# tmp926, itheta,
# @OPUS@\upstream\celt\bands.c:768:             if (!stereo && ctx->avoid_split_noise && itheta > 0 && itheta < qn)
	l32i.n	a3, a12, 56	# ctx_143(D)->avoid_split_noise, ctx_143(D)->avoid_split_noise
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	addmi	a2, a2, 0x2000	# _263, tmp926,
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	srai	a7, a2, 14	# itheta, _263,
# @OPUS@\upstream\celt\bands.c:768:             if (!stereo && ctx->avoid_split_noise && itheta > 0 && itheta < qn)
	bnez.n	a3, .L84	# ctx_143(D)->avoid_split_noise,
	j	.L134		#
.L21:
# @OPUS@\upstream\celt\bands.c:1123: }
	l32i	a0, sp, 108	#,
	mov.n	a2, a14	#, <retval>
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	quant_partition, .-quant_partition
	.section	.text.quant_band,"ax",@progbits
	.literal_position
	.literal .LC14, 16384
	.literal .LC15, -16384
	.literal .LC16, 23170
	.literal .LC17, bit_interleave_table$4327
	.literal .LC18, 1073741822
	.literal .LC19, ordery_table
	.literal .LC20, bit_deinterleave_table$4337
	.align	4
	.type	quant_band, @function
# Function: quant_band
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context:
# C context: /* This function is responsible for encoding and decoding a band for the mono case. */
# C context: static unsigned quant_band(struct band_ctx *ctx, celt_norm *X,
# C context: int N, int b, int B, celt_norm *lowband,
# C context: int LM, celt_norm *lowband_out,
# C context: opus_val16 gain, celt_norm *lowband_scratch, int fill)
# C context: {
quant_band:
	addi	sp, sp, -128	#,,
	s32i.n	a2, sp, 56	# %sfp, ctx
	s32i.n	a3, sp, 44	# %sfp, X
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a2, a4	#, N
	mov.n	a3, a6	#, B
# @OPUS@\upstream\celt\bands.c:1131: {
	s32i	a12, sp, 120	#,
	s32i	a13, sp, 116	#,
	s32i	a14, sp, 112	#,
	s32i	a0, sp, 124	#,
	s32i	a15, sp, 108	#,
# @OPUS@\upstream\celt\bands.c:1131: {
	s32i.n	a4, sp, 52	# %sfp, N
	s32i.n	a6, sp, 60	# %sfp, B
	s32i	a5, sp, 68	# %sfp, b
	s32i.n	a7, sp, 48	# %sfp, lowband
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
# ASM block division: a2=unsigned N, a3=unsigned B; result a2.
# a4/a5 are call-clobbered; no extra stack, loads or interrupt masking.
# Normal B=1,2,4,8 (TF may change it). Non-powers/zero retain libgcc.
	beqz	a3, .Lasm_block_quant_band_0_fallback
	addi	a4, a3, -1
	and	a4, a4, a3
	bnez	a4, .Lasm_block_quant_band_0_fallback
	nsau	a4, a3
	movi	a5, 31
	sub	a4, a5, a4
	ssr	a4
	srl	a2, a2
	j	.Lasm_block_quant_band_0_done
.Lasm_block_quant_band_0_fallback:
	call0	__udivsi3		#
.Lasm_block_quant_band_0_done:
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	l32i.n	a10, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:1131: {
	l16si	a8, sp, 136	# gain,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	l32i.n	a10, a10, 0	# MEM[(int *)ctx_92(D)],
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	l32i.n	a11, a11, 24	# ctx_92(D)->tf_change,
# @OPUS@\upstream\celt\bands.c:1152:    if (N==1)
	l32i.n	a12, sp, 52	# %sfp,
# @OPUS@\upstream\celt\bands.c:1131: {
	s32i	a8, sp, 72	# %sfp,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	s32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	s32i.n	a11, sp, 40	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a14, a2	# N_B,
# @OPUS@\upstream\celt\bands.c:1131: {
	l32i	a13, sp, 144	# fill, fill
# @OPUS@\upstream\celt\bands.c:1152:    if (N==1)
	bnei	a12, 1, .L136	#,,
# @OPUS@\upstream\celt\bands.c:937:       if (ctx->remaining_bits>=1<<BITRES)
	l32i.n	a14, sp, 56	# %sfp,
	l32i.n	a3, a14, 32	# ctx_92(D)->remaining_bits, ctx_92(D)->remaining_bits
# @OPUS@\upstream\celt\bands.c:932:    ec = ctx->ec;
	l32i.n	a2, a14, 28	# ctx_92(D)->ec, ec
# @OPUS@\upstream\celt\bands.c:937:       if (ctx->remaining_bits>=1<<BITRES)
	bgei	a3, 8, .L137	# ctx_92(D)->remaining_bits,,
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a2, a14, 4	# ctx_92(D)->resynth, ctx_92(D)->resynth
	beqz.n	a2, .L139	# ctx_92(D)->resynth,
.L138:
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	l32r	a2, .LC14	#, iftmp$138_161
	j	.L140		#
.L137:
# @OPUS@\upstream\celt\bands.c:939:          if (encode)
	beqz.n	a10, .L141	# tmp8,
# @OPUS@\upstream\celt\bands.c:941:             sign = x[0]<0;
	l32i.n	a10, sp, 44	# %sfp,
	mov.n	a4, a12	#,
	l16ui	a12, a10, 0	# *X_97(D), *X_97(D)
	srli	a12, a12, 15	# sign, *X_97(D),
# @OPUS@\upstream\celt\bands.c:942:             ec_enc_bits(ec, sign, 1);
	mov.n	a3, a12	#, sign
	call0	ec_enc_bits		#
	j	.L142		#
.L141:
	mov.n	a3, a12	#,
# @OPUS@\upstream\celt\bands.c:944:             sign = ec_dec_bits(ec, 1);
	call0	ec_dec_bits		#
	mov.n	a12, a2	# sign,
.L142:
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	l32i.n	a11, sp, 56	# %sfp,
	l32i.n	a2, a11, 32	# ctx_92(D)->remaining_bits, ctx_92(D)->remaining_bits
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a3, a11, 4	# ctx_92(D)->resynth, ctx_92(D)->resynth
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	addi	a2, a2, -8	# tmp344, ctx_92(D)->remaining_bits,
	s32i.n	a2, a11, 32	# ctx_92(D)->remaining_bits, tmp344
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	beqz.n	a3, .L139	# ctx_92(D)->resynth,
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	beqz.n	a12, .L138	# sign,
	l32r	a2, .LC15	#, iftmp$138_161
.L140:
	l32i.n	a12, sp, 44	# %sfp,
	s16i	a2, a12, 0	# *X_97(D), iftmp$138_161
.L139:
# @OPUS@\upstream\celt\bands.c:952:    if (lowband_out)
	l32i	a14, sp, 132	# lowband_out,
# @OPUS@\upstream\celt\bands.c:1154:       return quant_band_n1(ctx, X, NULL, lowband_out);
	movi.n	a15, 1	# <retval>,
# @OPUS@\upstream\celt\bands.c:952:    if (lowband_out)
	beqz.n	a14, .L135	#,
# @OPUS@\upstream\celt\bands.c:953:       lowband_out[0] = SHR16(X[0],4);
	l32i.n	a8, sp, 44	# %sfp,
	l16ui	a2, a8, 0	# *X_97(D),
	slli	a2, a2, 16	# tmp349, *X_97(D),
	srai	a2, a2, 20	# tmp350, tmp349,
	s16i	a2, a14, 0	# *lowband_out_98(D), tmp350
	j	.L135		#
.L136:
	movi.n	a2, 0	# tmp354,
	mov.n	a12, a11	#,
	l32i.n	a10, sp, 48	# %sfp,
	l32i	a11, sp, 140	# lowband_scratch,
	movi.n	a15, 1	# tmp353,
	mov.n	a3, a2	# tmp352, tmp354
	movnez	a3, a15, a10	# tmp352, tmp353,
	movnez	a2, a15, a11	# tmp356, tmp353,
	and	a2, a3, a2	# _822, tmp352, tmp356
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	bge	a12, a15, .L145	#,,
	movi.n	a8, -1	# tmp361,
	xor	a8, a8, a14	# tmp360, tmp361, N_B
	extui	a3, a12, 31, 1	# tmp365,,
	and	a8, a8, a3	# _1015, tmp360, tmp365
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	bnez.n	a2, .L146	# _822,
	j	.L258		#
.L145:
	mov.n	a9, a10	# lowband,
	beqz.n	a2, .L149	# _822,
	j	.L148		#
.L146:
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	beqz.n	a8, .L150	# _1015,
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	l32i.n	a4, sp, 52	# %sfp,
	mov.n	a3, a10	#,
	mov.n	a2, a11	#,
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
	l32i	a8, sp, 140	# lowband_scratch,
	s32i.n	a8, sp, 48	# %sfp,
	j	.L151		#
.L150:
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	l32i.n	a10, sp, 60	# %sfp,
	blti	a10, 2, .L152	#,,
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	l32i.n	a4, sp, 52	# %sfp,
	l32i.n	a3, sp, 48	# %sfp,
	mov.n	a2, a11	#,
	movi.n	a5, 2	#,
	s32i	a8, sp, 80	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:1147:    longBlocks = B0==1;
	l32i.n	a11, sp, 60	# %sfp,
	l32i	a8, sp, 80	#,
	addi.n	a2, a11, -1	# tmp371,,
	mov.n	a12, a8	#, _1015
	moveqz	a12, a15, a2	#, tmp353, tmp371
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:1147:    longBlocks = B0==1;
	s32i	a12, sp, 76	# %sfp,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	bnez.n	a10, .L207	#,
	mov.n	a12, a11	# B,
	l32i	a11, sp, 140	# lowband_scratch,
	s32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	s32i.n	a11, sp, 48	# %sfp,
	j	.L154		#
.L148:
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	l32i.n	a4, sp, 52	# %sfp,
	mov.n	a3, a10	#,
	mov.n	a2, a11	#,
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
	l32i	a12, sp, 140	# lowband_scratch,
	s32i.n	a12, sp, 48	# %sfp,
	mov.n	a9, a12	# lowband,
.L149:
	l32r	a15, .LC17	#, tmp520
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a5, 0	# k,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a14, sp, 64	# %sfp, N_B
.L164:
# @OPUS@\upstream\celt\bands.c:1172:       if (encode)
	l32i.n	a14, sp, 36	# %sfp,
	beqz.n	a14, .L155	#,
# @OPUS@\upstream\celt\bands.c:1173:          haar1(X, N>>k, 1<<k);
	l32i.n	a8, sp, 52	# %sfp,
	movi.n	a10, 1	#,
	ssr	a5	# k
	sra	a6, a8	# tmp375,
	ssl	a5	# k
	sll	a8, a10	# _12,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a10	#
	sra	a6, a6	# N0, tmp375
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a8, a10, .L156	# _12,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a7, 0	# i,
	bge	a6, a10, .L261	# N0,,
	j	.L156		#
.L158:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a5	# k
	sll	a2, a9	# tmp376, j
	slli	a2, a2, 1	# tmp377, tmp376,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a5	# k
	sll	a4, a11	# tmp380, ivtmp$338
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a7	# tmp378, tmp377, i
	slli	a2, a2, 1	# tmp379, tmp378,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a4, a4, a7	# tmp381, tmp380, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a3, a14, a2	# _176, X, tmp379
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a4, a4, 1	# tmp382, tmp381,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a10, a3, 0	# *_176,
	l32r	a2, .LC16	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a4, a14, a4	# _186, X, tmp382
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a12, a4, 0	# *_186,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a10, a10, a2	# tmp1, *_176,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a12, a12, a2	# tmp2, *_186, tmp8
	addmi	a2, a10, 0x4000	# _505, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a10, a12, a2	# tmp388, tmp2, _505
	srai	a10, a10, 15	# tmp389, tmp388,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a12	# tmp390, _505, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a10, a3, 0	# *_176, tmp389
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp391, tmp390,
	s16i	a2, a4, 0	# *_186, tmp391
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a9, a9, 1	# j, j,
	addi.n	a11, a11, 2	# ivtmp$338, ivtmp$338,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a6, a9, .L158	# N0, j,
	l32i	a8, sp, 76	# %sfp, _12
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a8, a7, .L159	# _12, i,
	j	.L157		#
.L261:
	l32i.n	a14, sp, 44	# %sfp, X
	s32i.n	a9, sp, 32	# %sfp, lowband
.L157:
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a11, 1	# ivtmp$338,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a9, 0	# j,
	s32i	a8, sp, 76	# %sfp, _12
	j	.L158		#
.L155:
# @OPUS@\upstream\celt\bands.c:1174:       if (lowband)
	beqz.n	a9, .L156	# lowband,
# @OPUS@\upstream\celt\bands.c:1175:          haar1(lowband, N>>k, 1<<k);
	l32i.n	a10, sp, 52	# %sfp,
	movi.n	a11, 1	#,
	ssr	a5	# k
	sra	a6, a10	# tmp393,
	ssl	a5	# k
	sll	a8, a11	# _12,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a11	#
	sra	a6, a6	# N0, tmp393
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bge	a8, a11, .L160	# _12,,
	j	.L156		#
.L161:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a5	# k
	sll	a2, a3	# tmp394, j
	slli	a2, a2, 1	# tmp395, tmp394,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a5	# k
	sll	a11, a4	# tmp398, ivtmp$332
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a7	# tmp396, tmp395, i
	slli	a2, a2, 1	# tmp397, tmp396,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a11, a11, a7	# tmp399, tmp398, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a10, a9, a2	# _208, lowband, tmp397
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a11, a11, 1	# tmp400, tmp399,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a12, a10, 0	# *_208,
	l32r	a2, .LC16	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a11, a9, a11	# _218, lowband, tmp400
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a14, a11, 0	# *_218,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a12, a12, a2	# tmp1, *_208,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a14, a14, a2	# tmp2, *_218, tmp8
	addmi	a2, a12, 0x4000	# _526, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a12, a14, a2	# tmp406, tmp2, _526
	srai	a12, a12, 15	# tmp407, tmp406,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a14	# tmp408, _526, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a12, a10, 0	# *_208, tmp407
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp409, tmp408,
	s16i	a2, a11, 0	# *_218, tmp409
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$332, ivtmp$332,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a3, a6, .L161	# j, N0,
	l32i.n	a8, sp, 32	# %sfp, _12
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a7, a8, .L162	# i, _12,
	j	.L156		#
.L160:
	blti	a6, 1, .L156	# N0,,
.L204:
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a7, 0	# i,
.L162:
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a4, 1	# ivtmp$332,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	s32i.n	a8, sp, 32	# %sfp, _12
	j	.L161		#
.L156:
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	srai	a2, a13, 4	# tmp414, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a2, a15, a2	# tmp415, tmp520, tmp414
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	extui	a13, a13, 0, 4	# tmp411, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a13, a15, a13	# tmp412, tmp520, tmp411
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a2, a2, 0	# bit_interleave_table, tmp416
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a13, a13, 0	# bit_interleave_table, _15
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	l32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	slli	a2, a2, 2	# _19, tmp416,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	addi.n	a5, a5, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	or	a13, a13, a2	# fill, _15, _19
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	bne	a10, a5, .L164	#, k,
	l32i	a14, sp, 64	# %sfp, N_B
	l32i.n	a11, sp, 60	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a8, 0	#,
	ssl	a10	#
	sll	a14, a14	# N_B, N_B
	ssr	a10	#
	sra	a12, a11	# B,
	s32i.n	a8, sp, 32	# %sfp,
	j	.L165		#
.L258:
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	beqz.n	a8, .L209	# _1015,
.L151:
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	movi.n	a10, 0	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l32r	a15, .LC16	#, tmp545
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	l32i.n	a12, sp, 60	# %sfp, B
	s32i.n	a10, sp, 32	# %sfp,
.L175:
# @OPUS@\upstream\celt\bands.c:1184:       if (encode)
	l32i.n	a11, sp, 36	# %sfp,
	srai	a14, a14, 1	# N_B, N_B,
	slli	a7, a12, 1	# B, B,
	beqz.n	a11, .L166	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bgei	a12, 1, .L259	# B,,
	j	.L167		#
.L259:
	l32i.n	a3, sp, 44	# %sfp, ivtmp$361
	slli	a6, a12, 2	# _902, B,
	add.n	a11, a3, a7	# _832, ivtmp$361, B
	bgei	a14, 1, .L168	# N_B,,
	j	.L167		#
.L169:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a9, a4, 0	# MEM[base: _843, offset: 0B],
	l32r	a2, .LC16	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a5, 0	# MEM[base: _841, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a9, a9, a2	# tmp1, MEM[base: _843, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a2	# tmp2, MEM[base: _841, offset: 0B], tmp11
	addmi	a2, a9, 0x4000	# _400, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a9, a10, a2	# tmp422, tmp2, _400
	srai	a9, a9, 15	# tmp423, tmp422,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp424, _400, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a9, a4, 0	# MEM[base: _843, offset: 0B], tmp423
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp425, tmp424,
	s16i	a2, a5, 0	# MEM[base: _841, offset: 0B], tmp425
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a8, a8, 1	# j, j,
	add.n	a4, a4, a6	# ivtmp$356, ivtmp$356, _902
	add.n	a5, a5, a6	# ivtmp$357, ivtmp$357, _902
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a8, a14, .L169	# j, N_B,
	l32i	a11, sp, 64	# %sfp, _832
	addi.n	a3, a3, 2	# ivtmp$361, ivtmp$361,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a11, a3, .L170	# _832, ivtmp$361,
.L168:
	add.n	a5, a7, a3	# ivtmp$357, B, ivtmp$361
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	mov.n	a4, a3	# ivtmp$356, ivtmp$361
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a8, 0	# j,
	s32i	a11, sp, 64	# %sfp, _832
	j	.L169		#
.L166:
# @OPUS@\upstream\celt\bands.c:1186:       if (lowband)
	l32i.n	a8, sp, 48	# %sfp,
	beqz.n	a8, .L167	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bgei	a12, 1, .L171	# B,,
	j	.L167		#
.L172:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a9, a3, 0	# MEM[base: _881, offset: 0B],
	l32r	a11, .LC16	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a2, a4, 0	# MEM[base: _879, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a9, a9, a11	# tmp1, MEM[base: _881, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a11, a2, a15	# tmp2, MEM[base: _879, offset: 0B], tmp545
	addmi	a2, a9, 0x4000	# _66, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a9, a2, a11	# tmp431, _66, tmp2
	srai	a9, a9, 15	# tmp432, tmp431,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a11	# tmp433, _66, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a9, a3, 0	# MEM[base: _881, offset: 0B], tmp432
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp434, tmp433,
	s16i	a2, a4, 0	# MEM[base: _879, offset: 0B], tmp434
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a8, a8, 1	# j, j,
	add.n	a3, a3, a6	# ivtmp$346, ivtmp$346, _902
	add.n	a4, a4, a6	# ivtmp$347, ivtmp$347, _902
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a8, a14, .L172	# j, N_B,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a10, a10, 1	# i, i,
	addi.n	a5, a5, 2	# ivtmp$351, ivtmp$351,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a10, a12, .L173	# i, B,
	j	.L167		#
.L171:
	blti	a14, 1, .L167	# N_B,,
	slli	a6, a12, 2	# _902, B,
.L205:
	l32i.n	a5, sp, 48	# %sfp, ivtmp$351
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a10, 0	# i,
.L173:
	add.n	a4, a7, a5	# ivtmp$347, B, ivtmp$351
	mov.n	a3, a5	# ivtmp$346, ivtmp$351
	movi.n	a8, 0	# j,
	j	.L172		#
.L167:
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	l32i.n	a8, sp, 32	# %sfp,
	l32i.n	a10, sp, 40	# %sfp,
	addi.n	a8, a8, 1	#,,
	add.n	a2, a8, a10	# _816,,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	movi.n	a11, -1	#,
	xor	a3, a11, a14	# tmp435,, N_B
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	extui	a2, a2, 31, 1	# tmp440, _816,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	ssl	a12	# B
	sll	a12, a13	# _20, fill
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	s32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	and	a3, a3, a2	# _150, tmp435, tmp440
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	or	a13, a13, a12	# fill, fill, _20
# @OPUS@\upstream\celt\bands.c:1189:       B <<= 1;
	mov.n	a12, a7	# B, B
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	bnez.n	a3, .L175	# _150,
	s32i.n	a3, sp, 40	# %sfp, _150
	j	.L165		#
.L209:
	l32i.n	a12, sp, 60	# %sfp, B
	s32i.n	a8, sp, 40	# %sfp, _1015
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i.n	a8, sp, 32	# %sfp, _1015
.L165:
# @OPUS@\upstream\celt\bands.c:1198:    if (B0>1)
	blti	a12, 2, .L176	# B,,
# @OPUS@\upstream\celt\bands.c:1147:    longBlocks = B0==1;
	l32i.n	a8, sp, 60	# %sfp,
	movi.n	a3, 1	# tmp447,
	addi.n	a15, a8, -1	# tmp446,,
	movi.n	a2, 0	# tmp448,
	moveqz	a2, a3, a15	# tmp448, tmp447, tmp446
	extui	a10, a2, 0, 8	#, tmp445
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i.n	a11, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:1147:    longBlocks = B0==1;
	s32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	beqz.n	a11, .L177	#,
	j	.L153		#
.L207:
	s32i.n	a8, sp, 40	# %sfp, _1015
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	l32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i	a8, sp, 140	# lowband_scratch,
	mov.n	a12, a11	# B,
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i.n	a10, sp, 32	# %sfp,
.L153:
# @OPUS@\upstream\celt\bands.c:1201:          deinterleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i.n	a11, sp, 40	# %sfp,
	l32i	a5, sp, 76	# %sfp,
	l32i.n	a2, sp, 44	# %sfp,
	ssl	a11	#
	sll	a4, a12	#, B
	ssr	a11	#
	sra	a3, a14	#, N_B
	call0	deinterleave_hadamard		#
.L177:
# @OPUS@\upstream\celt\bands.c:1202:       if (lowband)
	l32i.n	a8, sp, 48	# %sfp,
	beqz.n	a8, .L178	#,
.L154:
# @OPUS@\upstream\celt\bands.c:1203:          deinterleave_hadamard(lowband, N_B>>recombine, B0<<recombine, longBlocks);
	l32i.n	a10, sp, 40	# %sfp,
	l32i	a5, sp, 76	# %sfp,
	l32i.n	a2, sp, 48	# %sfp,
	ssl	a10	#
	sll	a4, a12	#, B
	ssr	a10	#
	sra	a3, a14	#, N_B
	call0	deinterleave_hadamard		#
	j	.L178		#
.L202:
# @OPUS@\upstream\celt\bands.c:1213:          interleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i.n	a11, sp, 40	# %sfp,
	ssl	a11	#
	sll	a5, a12	# _29, B
	ssr	a11	#
	sra	a13, a14	# _28, N_B
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	mull	a8, a13, a5	#, _28, _29
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a5, sp, 80	#,
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 16	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	l32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i.n	a3, sp, 20	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	s32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a5, sp, 80	#,
	bnez.n	a10, .L179	#,
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	blti	a5, 1, .L180	# _29,,
	blti	a13, 1, .L180	# _28,,
	slli	a6, a13, 1	# tmp454, _28,
	l32i.n	a11, sp, 44	# %sfp,
	mov.n	a10, a6	# tmp457, tmp454
	slli	a4, a5, 1	# _927, _29,
	slli	a9, a13, 2	# tmp475, _28,
	add.n	a6, a11, a6	# ivtmp$328,, tmp454
	mov.n	a7, a2	# ivtmp$327,
	add.n	a11, a4, a2	# _920, _927,
	neg	a10, a10	# tmp458, tmp457
	neg	a9, a9	# tmp476, tmp475
	j	.L182		#
.L179:
# @OPUS@\upstream\celt\bands.c:625:       const int *ordery = ordery_table+stride-2;
	l32r	a2, .LC18	#, tmp459
	add.n	a6, a5, a2	# _300, _29, tmp459
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	blti	a5, 1, .L180	# _29,,
	blti	a13, 1, .L180	# _28,,
	l32r	a3, .LC19	#, tmp461
	slli	a9, a5, 3	# tmp464, _29,
	slli	a6, a6, 2	# tmp460, _300,
	addi	a2, a3, -8	# tmp462, tmp461,
	slli	a4, a5, 1	# _1021, _29,
	add.n	a6, a6, a3	# ivtmp$317, tmp460, tmp461
	l32i.n	a7, sp, 36	# %sfp, ivtmp$319
	add.n	a9, a2, a9	# _976, tmp462, tmp464
	l32i.n	a5, sp, 44	# %sfp, X
	j	.L184		#
.L185:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l16si	a8, a2, 0	# MEM[base: _1007, offset: 0B], _318
	addi.n	a2, a2, 2	# ivtmp$313, ivtmp$313,
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	s16i	a8, a3, 0	# MEM[base: _1006, offset: 0B], _318
	add.n	a3, a3, a4	# ivtmp$314, ivtmp$314, _1021
# @OPUS@\upstream\celt\bands.c:627:          for (j=0;j<N0;j++)
	bne	a10, a2, .L185	# _993, ivtmp$313,
	addi.n	a6, a6, 4	# ivtmp$317, ivtmp$317,
	addi.n	a7, a7, 2	# ivtmp$319, ivtmp$319,
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	beq	a9, a6, .L180	# _976, ivtmp$317,
.L184:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l32i.n	a2, a6, 0	# MEM[base: _981, offset: 0B], MEM[base: _981, offset: 0B]
	mov.n	a3, a7	# ivtmp$314, ivtmp$319
	mull	a2, a13, a2	# _1027, _28, MEM[base: _981, offset: 0B]
	add.n	a10, a13, a2	# tmp469, _28, _1027
	slli	a10, a10, 1	# tmp470, tmp469,
	slli	a2, a2, 1	# tmp468, _1027,
	add.n	a2, a5, a2	# ivtmp$313, X, tmp468
	add.n	a10, a5, a10	# _993, X, tmp470
	j	.L185		#
.L186:
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	l16si	a5, a2, 0	# MEM[base: _954, offset: 0B], _333
	addi.n	a2, a2, 2	# ivtmp$322, ivtmp$322,
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	s16i	a5, a3, 0	# MEM[base: _953, offset: 0B], _333
	add.n	a3, a3, a4	# ivtmp$323, ivtmp$323, _927
# @OPUS@\upstream\celt\bands.c:631:          for (j=0;j<N0;j++)
	bne	a6, a2, .L186	# ivtmp$328, ivtmp$322,
	addi.n	a7, a7, 2	# ivtmp$327, ivtmp$327,
	sub	a6, a8, a9	# ivtmp$328, _917, tmp476
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	beq	a11, a7, .L180	# _920, ivtmp$327,
.L182:
	add.n	a8, a10, a6	# _917, tmp458, ivtmp$328
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	mov.n	a3, a7	# ivtmp$323, ivtmp$327
	mov.n	a2, a8	# ivtmp$322, _917
	j	.L186		#
.L180:
# @OPUS@\upstream\celt\bands.c:634:    OPUS_COPY(X, tmp, N);
	l32i.n	a3, sp, 36	# %sfp,
	l32i.n	a2, sp, 44	# %sfp,
	l32i.n	a4, sp, 48	# %sfp,
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:635:    RESTORE_STACK;
	l32i.n	a2, sp, 16	# _saved_stack,
	l32i.n	a3, sp, 20	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
.L203:
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i.n	a8, sp, 32	# %sfp,
	blti	a8, 1, .L187	#,,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	movi.n	a13, 0	# k,
.L192:
# @OPUS@\upstream\celt\bands.c:1220:          B >>= 1;
	srai	a12, a12, 1	# B, B,
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	slli	a14, a14, 1	# N_B, N_B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	ssr	a12	# B
	srl	a2, a15	# _30, <retval>
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	or	a15, a15, a2	# <retval>, <retval>, _30
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	srai	a10, a14, 1	# N0, N_B,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a12, 1, .L188	# B,,
	blti	a10, 1, .L188	# N0,,
	l32i.n	a3, sp, 44	# %sfp, ivtmp$306
	slli	a11, a12, 1	# _1036, B,
	add.n	a2, a11, a3	#, _1036, ivtmp$306
	s32i.n	a2, sp, 36	# %sfp,
	slli	a9, a12, 2	# _1066, B,
	j	.L190		#
.L191:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a6, a4, 0	# MEM[base: _1051, offset: 0B],
	l32r	a11, .LC16	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a8, a5, 0	# MEM[base: _1049, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a6, a6, a11	# tmp1, MEM[base: _1051, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a8, a8, a11	# tmp2, MEM[base: _1049, offset: 0B], tmp2
	addmi	a2, a6, 0x4000	# _532, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a6, a8, a2	# tmp482, tmp2, _532
	srai	a6, a6, 15	# tmp483, tmp482,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp484, _532, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a6, a4, 0	# MEM[base: _1051, offset: 0B], tmp483
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp485, tmp484,
	s16i	a2, a5, 0	# MEM[base: _1049, offset: 0B], tmp485
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a7, a7, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$301, ivtmp$301, _1066
	add.n	a5, a5, a9	# ivtmp$302, ivtmp$302, _1066
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a10, a7, .L191	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	l32i.n	a4, sp, 36	# %sfp,
	addi.n	a3, a3, 2	# ivtmp$306, ivtmp$306,
	l32i.n	a11, sp, 48	# %sfp, _1036
	beq	a4, a3, .L188	#, ivtmp$306,
.L190:
	add.n	a5, a11, a3	# ivtmp$302, _1036, ivtmp$306
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	mov.n	a4, a3	# ivtmp$301, ivtmp$306
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a7, 0	# j,
	s32i.n	a11, sp, 48	# %sfp, _1036
	j	.L191		#
.L188:
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	addi.n	a13, a13, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bne	a13, a8, .L192	# k,,
.L187:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i.n	a10, sp, 40	# %sfp,
	beqz.n	a10, .L193	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i.n	a12, sp, 32	# %sfp, B
	l32r	a14, .LC16	#, tmp527
	l32i.n	a12, sp, 44	# %sfp, X
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a7, 0	# k,
.L198:
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l32r	a11, .LC20	#,
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	add.n	a15, a11, a15	# tmp487,, <retval>
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	movi.n	a11, 1	#,
	ssr	a7	# k
	sra	a10, a8	# tmp489,
	ssl	a7	# k
	sll	a13, a11	# _33,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l8ui	a15, a15, 0	# bit_deinterleave_table, <retval>
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a11	#
	sra	a10, a10	# N0, tmp489
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a13, a11, .L194	# _33,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a10, a11, .L195	# N0,,
	j	.L194		#
.L197:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a7	# k
	sll	a2, a3	# tmp490, j
	slli	a2, a2, 1	# tmp491, tmp490,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a7	# k
	sll	a8, a4	# tmp494, ivtmp$293
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp492, tmp491, i
	slli	a2, a2, 1	# tmp493, tmp492,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a8, a8, a5	# tmp495, tmp494, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a12, a2	# _376, X, tmp493
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a8, a8, 1	# tmp496, tmp495,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a9, a6, 0	# *_376,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a8, a12, a8	# _386, X, tmp496
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a11, a8, 0	# *_386,
	l32r	a2, .LC16	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a9, a9, a14	# tmp1, *_376, tmp527
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a11, a11, a2	# tmp2, *_386,
	addmi	a2, a9, 0x4000	# _534, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a9, a11, a2	# tmp502, tmp2, _534
	srai	a9, a9, 15	# tmp503, tmp502,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a11	# tmp504, _534, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a9, a6, 0	# *_376, tmp503
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp505, tmp504,
	s16i	a2, a8, 0	# *_386, tmp505
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$293, ivtmp$293,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a10, a3, .L197	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a13, a5, .L194	# _33, i,
.L195:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$293,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	j	.L197		#
.L194:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	addi.n	a7, a7, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	bne	a7, a8, .L198	# k,,
	l32i.n	a12, sp, 32	# %sfp, B
.L193:
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	l32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:1238:       if (lowband_out)
	l32i	a11, sp, 132	# lowband_out,
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	ssl	a10	#
	sll	a12, a12	# B, B
# @OPUS@\upstream\celt\bands.c:1238:       if (lowband_out)
	bnez.n	a11, .L199	#,
.L200:
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	movi.n	a2, 1	# tmp506,
	ssl	a12	# B
	sll	a2, a2	# tmp507, tmp506
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	addi.n	a2, a2, -1	# tmp508, tmp507,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	and	a15, a15, a2	# <retval>, <retval>, tmp508
	j	.L135		#
.L199:
# @OPUS@\upstream\celt\bands.c:1242:          n = celt_sqrt(SHL32(EXTEND32(N0),22));
	l32i.n	a14, sp, 52	# %sfp,
	slli	a2, a14, 22	#,,
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\bands.c:1242:          n = celt_sqrt(SHL32(EXTEND32(N0),22));
	slli	a2, a2, 16	# tmp510,,
	srai	a5, a2, 16	# n, tmp510,
# @OPUS@\upstream\celt\bands.c:1243:          for (j=0;j<N0;j++)
	blti	a14, 1, .L200	#,,
	l32i.n	a3, sp, 44	# %sfp, ivtmp$288
	slli	a6, a14, 1	# tmp511,,
	l32i	a4, sp, 132	# lowband_out, ivtmp$289
	add.n	a6, a3, a6	# _1085, ivtmp$288, tmp511
.L201:
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	l16ui	a2, a3, 0	# MEM[base: _54, offset: 0B],
	addi.n	a3, a3, 2	# ivtmp$288, ivtmp$288,
	mul16s	a2, a2, a5	# tmp512, MEM[base: _54, offset: 0B], n
	srai	a2, a2, 15	# tmp514, tmp512,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	s16i	a2, a4, 0	# MEM[base: _1091, offset: 0B], tmp514
	addi.n	a4, a4, 2	# ivtmp$289, ivtmp$289,
# @OPUS@\upstream\celt\bands.c:1243:          for (j=0;j<N0;j++)
	bne	a3, a6, .L201	# ivtmp$288, _1085,
	j	.L200		#
.L178:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	l32i	a8, sp, 72	# %sfp,
	l32i	a10, sp, 128	# LM,
	l32i.n	a7, sp, 48	# %sfp,
	l32i	a5, sp, 68	# %sfp,
	l32i.n	a4, sp, 52	# %sfp,
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a2, sp, 56	# %sfp,
	s32i.n	a13, sp, 8	#, fill
	s32i.n	a8, sp, 4	#,
	s32i.n	a10, sp, 0	#,
	mov.n	a6, a12	#, B
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	mov.n	a15, a2	# <retval>,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, a11, 4	# ctx_92(D)->resynth, ctx_92(D)->resynth
	beqz.n	a2, .L135	# ctx_92(D)->resynth,
	j	.L202		#
.L176:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	l32i	a8, sp, 72	# %sfp,
	l32i	a10, sp, 128	# LM,
	l32i.n	a7, sp, 48	# %sfp,
	l32i	a5, sp, 68	# %sfp,
	l32i.n	a4, sp, 52	# %sfp,
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a2, sp, 56	# %sfp,
	s32i.n	a13, sp, 8	#, fill
	s32i.n	a8, sp, 4	#,
	s32i.n	a10, sp, 0	#,
	mov.n	a6, a12	#, B
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	mov.n	a15, a2	# <retval>,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, a11, 4	# ctx_92(D)->resynth, ctx_92(D)->resynth
	bnez.n	a2, .L203	# ctx_92(D)->resynth,
	j	.L135		#
.L152:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	l32i	a12, sp, 72	# %sfp,
	l32i	a14, sp, 128	# LM,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a6, sp, 60	# %sfp,
	l32i	a5, sp, 68	# %sfp,
	l32i.n	a4, sp, 52	# %sfp,
	l32i.n	a3, sp, 44	# %sfp,
	l32i.n	a2, sp, 56	# %sfp,
	s32i.n	a12, sp, 4	#,
	s32i.n	a13, sp, 8	#, fill
	s32i.n	a14, sp, 0	#,
	s32i	a8, sp, 80	#,
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a10, sp, 56	# %sfp,
	l32i	a8, sp, 80	#,
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	mov.n	a15, a2	# <retval>,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, a10, 4	# ctx_92(D)->resynth, ctx_92(D)->resynth
	s32i.n	a8, sp, 40	# %sfp, _1015
	l32i.n	a12, sp, 60	# %sfp, B
	bnez.n	a2, .L193	# ctx_92(D)->resynth,
	j	.L135		#
.L159:
	l32i.n	a9, sp, 32	# %sfp, lowband
# @OPUS@\upstream\celt\bands.c:1174:       if (lowband)
	bnez.n	a9, .L204	# lowband,
	j	.L156		#
.L170:
# @OPUS@\upstream\celt\bands.c:1186:       if (lowband)
	l32i.n	a11, sp, 48	# %sfp,
	bnez.n	a11, .L205	#,
	j	.L167		#
.L135:
# @OPUS@\upstream\celt\bands.c:1249: }
	l32i	a0, sp, 124	#,
	movi	a9, 0x80	#,
	mov.n	a2, a15	#, <retval>
	l32i	a12, sp, 120	#,
	l32i	a13, sp, 116	#,
	l32i	a14, sp, 112	#,
	l32i	a15, sp, 108	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	quant_band, .-quant_band
	.section	.text.hysteresis_decision,"ax",@progbits
	.literal_position
	.align	4
	.global	hysteresis_decision
	.type	hysteresis_decision, @function
# Function: hysteresis_decision
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "quant_bands.h"
# C context: #include "pitch.h"
# C context:
# C context: int hysteresis_decision(opus_val16 val, const opus_val16 *thresholds, const opus_val16 *hysteresis, int N, int prev)
# C context: {
# C context: int i;
# C context: for (i=0;i<N;i++)
# C context: {
hysteresis_decision:
# @OPUS@\upstream\celt\bands.c:47: {
	slli	a2, a2, 16	# tmp72, val,
	srai	a9, a2, 16	# val, tmp72,
# @OPUS@\upstream\celt\bands.c:49:    for (i=0;i<N;i++)
	blti	a5, 1, .L274	# N,,
# @OPUS@\upstream\celt\bands.c:51:       if (val < thresholds[i])
	l16si	a2, a3, 0	# *thresholds_31(D), tmp77
	blt	a9, a2, .L274	# val, tmp77,
	addi.n	a7, a3, 2	# ivtmp$370, thresholds,
# @OPUS@\upstream\celt\bands.c:49:    for (i=0;i<N;i++)
	movi.n	a2, 0	# <retval>,
	j	.L269		#
.L270:
# @OPUS@\upstream\celt\bands.c:51:       if (val < thresholds[i])
	l16si	a8, a8, 0	# MEM[base: _37, offset: 0B], tmp81
	blt	a9, a8, .L268	# val, tmp81,
.L269:
	addi.n	a7, a7, 2	# ivtmp$370, ivtmp$370,
# @OPUS@\upstream\celt\bands.c:49:    for (i=0;i<N;i++)
	addi.n	a2, a2, 1	# <retval>, <retval>,
# @OPUS@\upstream\celt\bands.c:51:       if (val < thresholds[i])
	addi	a8, a7, -2	# tmp80, ivtmp$370,
# @OPUS@\upstream\celt\bands.c:49:    for (i=0;i<N;i++)
	bne	a5, a2, .L270	# N, <retval>,
	j	.L268		#
.L274:
# @OPUS@\upstream\celt\bands.c:49:    for (i=0;i<N;i++)
	movi.n	a2, 0	# <retval>,
.L268:
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	bge	a6, a2, .L271	# prev, <retval>,
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	slli	a5, a6, 1	# _7, prev,
	add.n	a7, a3, a5	# tmp84, thresholds, _7
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	add.n	a5, a4, a5	# tmp88, hysteresis, _7
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	l16si	a7, a7, 0	# *_8, tmp85
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	l16si	a5, a5, 0	# *_12, tmp89
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	add.n	a5, a7, a5	# tmp92, tmp85, tmp89
# @OPUS@\upstream\celt\bands.c:54:    if (i>prev && val < thresholds[prev]+hysteresis[prev])
	blt	a9, a5, .L276	# val, tmp92,
.L271:
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	bge	a2, a6, .L267	# <retval>, prev,
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	slli	a5, a6, 1	# tmp93, prev,
	addi	a5, a5, -2	# _19, tmp93,
	add.n	a3, a3, a5	# tmp95, thresholds, _19
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	add.n	a4, a4, a5	# tmp99, hysteresis, _19
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	l16si	a3, a3, 0	# *_20, tmp96
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	l16si	a4, a4, 0	# *_23, tmp100
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	sub	a3, a3, a4	# tmp103, tmp96, tmp100
# @OPUS@\upstream\celt\bands.c:56:    if (i<prev && val > thresholds[prev-1]-hysteresis[prev-1])
	blt	a3, a9, .L276	# tmp103, val,
	j	.L267		#
.L276:
	mov.n	a2, a6	# <retval>, prev
.L267:
# @OPUS@\upstream\celt\bands.c:59: }
	ret.n
	.size	hysteresis_decision, .-hysteresis_decision
	.section	.text.celt_lcg_rand,"ax",@progbits
	.literal_position
	.literal .LC22, 1664525
	.literal .LC23, 1013904223
	.align	4
	.global	celt_lcg_rand
	.type	celt_lcg_rand, @function
# Function: celt_lcg_rand
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return i;
# C context: }
# C context:
# C context: opus_uint32 celt_lcg_rand(opus_uint32 seed)
# C context: {
# C context: return 1664525 * seed + 1013904223;
# C context: }
# C context:
celt_lcg_rand:
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	l32r	a3, .LC22	#, tmp47
	mull	a2, a2, a3	# tmp46, seed, tmp47
# @OPUS@\upstream\celt\bands.c:64: }
	l32r	a3, .LC23	#, tmp48
	add.n	a2, a2, a3	#, tmp46, tmp48
	ret.n
	.size	celt_lcg_rand, .-celt_lcg_rand
	.section	.text.bitexact_cos,"ax",@progbits
	.literal_position
	.literal .LC24, 8277
	.literal .LC25, -7651
	.align	4
	.global	bitexact_cos
	.type	bitexact_cos, @function
# Function: bitexact_cos
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* This is a cos() approximation designed to be bit-exact on any platform. Bit exactness
# C context: with this approximation is important because it has an impact on the bit allocation */
# C context: opus_int16 bitexact_cos(opus_int16 x)
# C context: {
# C context: opus_int32 tmp;
# C context: opus_int16 x2;
# C context: tmp = (4096+((opus_int32)(x)*(x)))>>13;
bitexact_cos:
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	mul16s	a2, a2, a2	# tmp65, x, x
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	l32r	a4, .LC24	#, tmp76
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	addmi	a2, a2, 0x1000	# tmp66, tmp65,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a2, a2, 3	# tmp68, tmp66,
	srai	a3, a2, 16	# x2, tmp68,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	movi	a2, -0x272	# tmp70,
	mul16s	a2, a2, a3	# tmp71, tmp70, x2
	addmi	a2, a2, 0x4000	# tmp72, tmp71,
	srai	a2, a2, 15	# tmp73, tmp72,
	add.n	a2, a2, a4	# tmp75, tmp73, tmp76
	mul16s	a2, a2, a3	# tmp77, tmp75, x2
	l32r	a4, .LC25	#, tmp82
	addmi	a2, a2, 0x4000	# tmp78, tmp77,
	srai	a2, a2, 15	# tmp79, tmp78,
	add.n	a2, a2, a4	# tmp81, tmp79, tmp82
	mul16s	a2, a2, a3	# tmp83, tmp81, x2
	addmi	a2, a2, 0x4000	# tmp84, tmp83,
	srai	a2, a2, 15	# tmp85, tmp84,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a2, a2, a3	# tmp86, tmp85, x2
	addmi	a2, a2, -0x8000	# tmp90, tmp86,
	slli	a2, a2, 16	# tmp92, tmp90,
# @OPUS@\upstream\celt\bands.c:78: }
	srai	a2, a2, 16	#, tmp92,
	ret.n
	.size	bitexact_cos, .-bitexact_cos
	.section	.text.bitexact_log2tan,"ax",@progbits
	.literal_position
	.literal .LC27, -2597
	.literal .LC28, 7932
	.align	4
	.global	bitexact_log2tan
	.type	bitexact_log2tan, @function
# Function: bitexact_log2tan
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return 1+x2;
# C context: }
# C context:
# C context: int bitexact_log2tan(int isin,int icos)
# C context: {
# C context: int lc;
# C context: int ls;
# C context: lc=EC_ILOG(icos);
bitexact_log2tan:
# @OPUS@\upstream\celt\bands.c:85:    ls=EC_ILOG(isin);
	nsau	a5, a2	# _4, isin
# @OPUS@\upstream\celt\bands.c:84:    lc=EC_ILOG(icos);
	nsau	a4, a3	# _2, icos
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	addi	a7, a5, -17	# tmp74, _4,
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	ssl	a7	# tmp74
	sll	a7, a2	# isin, isin
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	addi	a6, a4, -17	# tmp77, _2,
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	ssl	a6	# tmp77
	sll	a6, a3	# icos, icos
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	slli	a7, a7, 16	# tmp76, isin,
	l32r	a3, .LC27	#, tmp82
	srai	a7, a7, 16	# _9, tmp76,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	slli	a6, a6, 16	# tmp79, icos,
	srai	a6, a6, 16	# _21, tmp79,
	mov.n	a2, a3	# tmp95, tmp82
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a3, a7, a3	# tmp81, _9, tmp82
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mul16s	a2, a6, a2	# tmp94, _21, tmp95
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	l32r	a8, .LC28	#, tmp87
	addmi	a3, a3, 0x4000	# tmp83, tmp81,
	srai	a3, a3, 15	# tmp84, tmp83,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a2, a2, 0x4000	# tmp96, tmp94,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a3, a3, a8	# tmp86, tmp84, tmp87
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a2, a2, 15	# tmp97, tmp96,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a3, a3, a7	# tmp88, tmp86, _9
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	add.n	a2, a2, a8	# tmp99, tmp97, tmp87
	mul16s	a2, a2, a6	# tmp101, tmp99, _21
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	sub	a4, a4, a5	# tmp91, _2, _4
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	addmi	a3, a3, 0x4000	# tmp89, tmp88,
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	slli	a4, a4, 11	# tmp92, tmp91,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	srai	a3, a3, 15	# tmp90, tmp89,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a2, a2, 0x4000	# tmp102, tmp101,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a3, a3, a4	# tmp93, tmp90, tmp92
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a2, a2, 15	# tmp103, tmp102,
# @OPUS@\upstream\celt\bands.c:91: }
	sub	a2, a3, a2	#, tmp93, tmp103
	ret.n
	.size	bitexact_log2tan, .-bitexact_log2tan
	.section	.text.compute_band_energies,"ax",@progbits
	.literal_position
	.align	4
	.global	compute_band_energies
	.type	compute_band_energies, @function
# Function: compute_band_energies
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #ifdef FIXED_POINT
# C context: /* Compute the amplitude (sqrt energy) in each of the bands */
# C context: void compute_band_energies(const CELTMode *m, const celt_sig *X, celt_ener *bandE, int end, int C, int LM, int arch)
# C context: {
# C context: int i, c, N;
# C context: const opus_int16 *eBands = m->eBands;
# C context: (void)arch;
compute_band_energies:
	addi	sp, sp, -80	#,,
	s32i	a12, sp, 72	#,
	mov.n	a12, a2	# m, m
# @OPUS@\upstream\celt\bands.c:100:    N = m->shortMdctSize<<LM;
	l32i.n	a2, a2, 36	# m_84(D)->shortMdctSize, m_84(D)->shortMdctSize
# @OPUS@\upstream\celt\bands.c:96: {
	s32i	a14, sp, 64	#,
	mov.n	a14, a3	# X, X
# @OPUS@\upstream\celt\bands.c:98:    const opus_int16 *eBands = m->eBands;
	l32i.n	a3, a12, 24	# m_84(D)->eBands,
# @OPUS@\upstream\celt\bands.c:100:    N = m->shortMdctSize<<LM;
	ssl	a7	# LM
	sll	a2, a2	#, m_84(D)->shortMdctSize
# @OPUS@\upstream\celt\bands.c:96: {
	s32i	a13, sp, 68	#,
	s32i	a0, sp, 76	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\celt\bands.c:96: {
	s32i.n	a5, sp, 8	# %sfp, end
	s32i.n	a4, sp, 12	# %sfp, bandE
	s32i.n	a6, sp, 24	# %sfp, C
# @OPUS@\upstream\celt\bands.c:98:    const opus_int16 *eBands = m->eBands;
	s32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:100:    N = m->shortMdctSize<<LM;
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:96: {
	mov.n	a13, a7	# LM, LM
	blti	a5, 1, .L280	# end,,
# @OPUS@\upstream\celt\bands.c:100:    N = m->shortMdctSize<<LM;
	movi.n	a3, 0	#,
	s32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:101:    c=0; do {
	s32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mathops.h:99:    opus_val32 maxval = 0;
	mov.n	a10, a12	# m, m
.L294:
	l32i.n	a12, sp, 16	# %sfp, ivtmp$386
# @OPUS@\upstream\celt\bands.c:102:       for (i=0;i<end;i++)
	movi.n	a15, 0	# i,
.L293:
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	l16si	a2, a12, 0	# MEM[base: _218, offset: 0B], _7
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	l16si	a9, a12, 2	# MEM[base: _218, offset: 2B], _16
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	ssl	a13	# LM
	sll	a6, a2	# j, _7
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	l32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	sub	a2, a9, a2	# tmp140, _16, _7
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	ssl	a13	# LM
	sll	a2, a2	# _19, tmp140
	slli	a11, a15, 1	# _216, i,
# @OPUS@\upstream\celt\bands.c:108:          maxval = celt_maxabs32(&X[c*N+(eBands[i]<<LM)], (eBands[i+1]-eBands[i])<<LM);
	add.n	a7, a3, a6	# _10,, j
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	blti	a2, 1, .L282	# _19,,
	slli	a4, a7, 2	# tmp141, _10,
	add.n	a7, a2, a7	# tmp142, _19, _10
	add.n	a4, a14, a4	# ivtmp$380, X, tmp141
	slli	a7, a7, 2	# tmp143, tmp142,
# @OPUS@\upstream\celt\mathops.h:100:    opus_val32 minval = 0;
	movi.n	a5, 0	# minval,
	add.n	a7, a14, a7	# _225, X, tmp143
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	mov.n	a2, a4	# ivtmp$383, ivtmp$380
# @OPUS@\upstream\celt\mathops.h:99:    opus_val32 maxval = 0;
	mov.n	a8, a5	# maxval, minval
.L285:
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	l32i.n	a3, a2, 0	# MEM[base: _231, offset: 0B], _110
	addi.n	a2, a2, 4	# ivtmp$383, ivtmp$383,
# @OPUS@\upstream\celt\mathops.h:103:       maxval = MAX32(maxval, x[i]);
	bge	a8, a3, .L283	# maxval, _110,
	mov.n	a8, a3	# maxval, _110
.L283:
# @OPUS@\upstream\celt\mathops.h:104:       minval = MIN32(minval, x[i]);
	bge	a3, a5, .L284	# _110, minval,
	mov.n	a5, a3	# minval, _110
.L284:
# @OPUS@\upstream\celt\mathops.h:101:    for (i=0;i<len;i++)
	bne	a7, a2, .L285	# _225, ivtmp$383,
# @OPUS@\upstream\celt\mathops.h:106:    return MAX32(maxval, -minval);
	neg	a5, a5	# _117, minval
	bge	a5, a8, .L286	# _117, maxval,
	mov.n	a5, a8	# _117, maxval
.L286:
# @OPUS@\upstream\celt\bands.c:109:          if (maxval > 0)
	beqz.n	a5, .L282	# _117,
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	l32i.n	a3, a10, 48	# m_84(D)->logN, m_84(D)->logN
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	addi.n	a2, a13, 1	# tmp153, LM,
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	add.n	a11, a3, a11	# tmp146, m_84(D)->logN, _216
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	l16ui	a3, a11, 0	# *_22,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a5, a5	# _119, _117
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	slli	a3, a3, 16	# tmp149, *_22,
	srai	a3, a3, 19	# tmp151, tmp149,
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	add.n	a2, a3, a2	# tmp154, tmp151, tmp153
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	srai	a2, a2, 1	# tmp155, tmp154,
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	sub	a5, a2, a5	# tmp159, tmp155, _119
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	addi	a2, a5, 31	# _29, tmp159,
	movi.n	a7, 0xe	# tmp161,
# @OPUS@\upstream\celt\bands.c:111:             int shift = celt_ilog2(maxval) - 14 + (((m->logN[i]>>BITRES)+LM+1)>>1);
	addi	a5, a5, 17	# shift, tmp159,
	sub	a7, a7, a2	# _267, tmp161, _29
	ssl	a13	# LM
	sll	a9, a9	# _237, _16
# @OPUS@\upstream\celt\bands.c:106:          opus_val32 sum = 0;
	movi.n	a2, 0	# sum,
# @OPUS@\upstream\celt\bands.c:113:             if (shift>0)
	blti	a5, 1, .L287	# shift,,
.L288:
# @OPUS@\upstream\celt\bands.c:116:                   sum = MAC16_16(sum, EXTRACT16(SHR32(X[j+c*N],shift)),
	l32i.n	a3, a4, 0	# MEM[base: _250, offset: 0B], MEM[base: _250, offset: 0B]
# @OPUS@\upstream\celt\bands.c:118:                } while (++j<eBands[i+1]<<LM);
	addi.n	a6, a6, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:116:                   sum = MAC16_16(sum, EXTRACT16(SHR32(X[j+c*N],shift)),
	ssr	a5	# shift
	sra	a3, a3	# tmp162, MEM[base: _250, offset: 0B]
	mul16s	a3, a3, a3	# tmp165, tmp162, tmp162
	addi.n	a4, a4, 4	# ivtmp$380, ivtmp$380,
# @OPUS@\upstream\celt\bands.c:116:                   sum = MAC16_16(sum, EXTRACT16(SHR32(X[j+c*N],shift)),
	add.n	a2, a2, a3	# sum, sum, tmp165
# @OPUS@\upstream\celt\bands.c:118:                } while (++j<eBands[i+1]<<LM);
	blt	a6, a9, .L288	# j, _237,
	j	.L289		#
.L287:
# @OPUS@\upstream\celt\bands.c:121:                   sum = MAC16_16(sum, EXTRACT16(SHL32(X[j+c*N],-shift)),
	l32i.n	a3, a4, 0	# MEM[base: _242, offset: 0B], MEM[base: _242, offset: 0B]
# @OPUS@\upstream\celt\bands.c:123:                } while (++j<eBands[i+1]<<LM);
	addi.n	a6, a6, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:121:                   sum = MAC16_16(sum, EXTRACT16(SHL32(X[j+c*N],-shift)),
	ssl	a7	# _267
	sll	a3, a3	# tmp166, MEM[base: _242, offset: 0B]
	mul16s	a3, a3, a3	# tmp169, tmp166, tmp166
	addi.n	a4, a4, 4	# ivtmp$380, ivtmp$380,
# @OPUS@\upstream\celt\bands.c:121:                   sum = MAC16_16(sum, EXTRACT16(SHL32(X[j+c*N],-shift)),
	add.n	a2, a2, a3	# sum, sum, tmp169
# @OPUS@\upstream\celt\bands.c:123:                } while (++j<eBands[i+1]<<LM);
	blt	a6, a9, .L287	# j, _237,
.L289:
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	blti	a7, 1, .L290	# _267,,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	s32i.n	a7, sp, 28	#,
	s32i.n	a10, sp, 32	#,
	call0	celt_sqrt		#
	l32i.n	a7, sp, 28	#,
	l32i.n	a10, sp, 32	#,
	ssr	a7	# _267
	sra	a7, a2	# tmp170,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	addi.n	a7, a7, 1	# iftmp$14_78, tmp170,
	j	.L291		#
.L290:
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	s32i.n	a5, sp, 28	#,
	s32i.n	a10, sp, 32	#,
	call0	celt_sqrt		#
	l32i.n	a5, sp, 28	#,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	l32i.n	a10, sp, 32	#,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	ssl	a5	# shift
	sll	a2, a2	# tmp171,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	addi.n	a7, a2, 1	# iftmp$14_78, tmp171,
.L291:
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	l32i.n	a2, a10, 8	# m_84(D)->nbEBands, m_84(D)->nbEBands
	l32i.n	a3, sp, 0	# %sfp,
	mull	a2, a3, a2	# tmp172,, m_84(D)->nbEBands
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	add.n	a2, a2, a15	# tmp174, tmp172, i
# @OPUS@\upstream\celt\bands.c:126:             bandE[i+c*m->nbEBands] = EPSILON+VSHR32(EXTEND32(celt_sqrt(sum)),-shift);
	slli	a2, a2, 2	# tmp175, tmp174,
	add.n	a2, a3, a2	# tmp176,, tmp175
	s32i.n	a7, a2, 0	# *_64, iftmp$14_78
	j	.L292		#
.L282:
# @OPUS@\upstream\celt\bands.c:128:             bandE[i+c*m->nbEBands] = EPSILON;
	l32i.n	a2, a10, 8	# m_84(D)->nbEBands, m_84(D)->nbEBands
	l32i.n	a3, sp, 0	# %sfp,
	mull	a2, a3, a2	# tmp177,, m_84(D)->nbEBands
# @OPUS@\upstream\celt\bands.c:128:             bandE[i+c*m->nbEBands] = EPSILON;
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\celt\bands.c:128:             bandE[i+c*m->nbEBands] = EPSILON;
	add.n	a2, a2, a15	# tmp179, tmp177, i
# @OPUS@\upstream\celt\bands.c:128:             bandE[i+c*m->nbEBands] = EPSILON;
	slli	a2, a2, 2	# tmp180, tmp179,
	add.n	a2, a3, a2	# tmp181,, tmp180
	movi.n	a3, 1	# tmp182,
	s32i.n	a3, a2, 0	# *_70, tmp182
.L292:
# @OPUS@\upstream\celt\bands.c:102:       for (i=0;i<end;i++)
	l32i.n	a2, sp, 8	# %sfp,
# @OPUS@\upstream\celt\bands.c:102:       for (i=0;i<end;i++)
	addi.n	a15, a15, 1	# i, i,
	addi.n	a12, a12, 2	# ivtmp$386, ivtmp$386,
# @OPUS@\upstream\celt\bands.c:102:       for (i=0;i<end;i++)
	bne	a2, a15, .L293	#, i,
# @OPUS@\upstream\celt\bands.c:132:    } while (++c<C);
	l32i.n	a3, sp, 0	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	addi.n	a3, a3, 1	#,,
	s32i.n	a3, sp, 0	# %sfp,
	l32i.n	a3, sp, 4	# %sfp,
	add.n	a3, a3, a2	#,,
	s32i.n	a3, sp, 4	# %sfp,
	l32i.n	a2, sp, 24	# %sfp,
	l32i.n	a3, sp, 0	# %sfp,
	blt	a3, a2, .L294	#,,
.L280:
# @OPUS@\upstream\celt\bands.c:134: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	compute_band_energies, .-compute_band_energies
	.section	.text.normalise_bands,"ax",@progbits
	.literal_position
	.align	4
	.global	normalise_bands
	.type	normalise_bands, @function
# Function: normalise_bands
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Normalise each band such that the energy is one. */
# C context: void normalise_bands(const CELTMode *m, const celt_sig * OPUS_RESTRICT freq, celt_norm * OPUS_RESTRICT X, const celt_ener *bandE, int end, int C, int M)
# C context: {
# C context: int i, c, N;
# C context: const opus_int16 *eBands = m->eBands;
# C context: N = M*m->shortMdctSize;
normalise_bands:
	addi	sp, sp, -80	#,,
# @OPUS@\upstream\celt\bands.c:141:    N = M*m->shortMdctSize;
	movi.n	a8, 0	#,
# @OPUS@\upstream\celt\bands.c:138: {
	s32i	a14, sp, 64	#,
	mov.n	a14, a2	# m, m
# @OPUS@\upstream\celt\bands.c:141:    N = M*m->shortMdctSize;
	s32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:138: {
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\celt\bands.c:140:    const opus_int16 *eBands = m->eBands;
	l32i.n	a8, a14, 24	# *m_66(D).eBands,
# @OPUS@\upstream\celt\bands.c:138: {
	l32i	a15, sp, 80	# M, M
# @OPUS@\upstream\celt\bands.c:141:    N = M*m->shortMdctSize;
	l32i.n	a2, a2, 36	# *m_66(D).shortMdctSize, *m_66(D).shortMdctSize
# @OPUS@\upstream\celt\bands.c:140:    const opus_int16 *eBands = m->eBands;
	s32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\celt\bands.c:141:    N = M*m->shortMdctSize;
	mull	a2, a15, a2	#, M, *m_66(D).shortMdctSize
# @OPUS@\upstream\celt\bands.c:142:    c=0; do {
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:138: {
	s32i	a13, sp, 68	#,
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
# @OPUS@\upstream\celt\bands.c:141:    N = M*m->shortMdctSize;
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:138: {
	s32i.n	a3, sp, 16	# %sfp, freq
	s32i.n	a4, sp, 20	# %sfp, X
	s32i.n	a5, sp, 8	# %sfp, bandE
	s32i.n	a6, sp, 12	# %sfp, end
	s32i.n	a7, sp, 32	# %sfp, C
# @OPUS@\upstream\celt\bands.c:142:    c=0; do {
	s32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	mov.n	a13, a15	# M, M
.L313:
	l32i.n	a9, sp, 24	# %sfp, ivtmp$404
# @OPUS@\upstream\celt\bands.c:143:       i=0; do {
	mov.n	a10, a13	# M, M
	movi.n	a12, 0	# i,
	mov.n	a15, a14	# m, m
	mov.n	a13, a9	# ivtmp$404, ivtmp$404
.L312:
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	l32i.n	a2, a15, 8	# *m_66(D).nbEBands, *m_66(D).nbEBands
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	l32i.n	a8, sp, 8	# %sfp,
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	mull	a2, a3, a2	# tmp123,, *m_66(D).nbEBands
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	add.n	a2, a2, a12	# tmp125, tmp123, i
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	slli	a2, a2, 2	# tmp126, tmp125,
	add.n	a2, a8, a2	# tmp127,, tmp126
	l32i.n	a4, a2, 0	# *_7, _173
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	blti	a4, 1, .L314	# _173,,
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	movi.n	a2, 0x1f	# tmp131,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a5, a4	# _88, _173
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	sub	a5, a2, a5	# _9, tmp131, _88
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	addi	a3, a5, -13	# shift, _9,
# @OPUS@\upstream\celt\bands.c:148:          E = VSHR32(bandE[i+c*m->nbEBands], shift);
	ssr	a3	# shift
	sra	a2, a4	# tmp133, _173
# @OPUS@\upstream\celt\bands.c:148:          E = VSHR32(bandE[i+c*m->nbEBands], shift);
	slli	a2, a2, 16	# tmp134, tmp133,
	addi	a14, a5, -14	# _196, _9,
	srai	a2, a2, 16	# iftmp$18_60, tmp134,
	bgei	a3, 1, .L307	# shift,,
	movi.n	a6, 0xd	#,
	sub	a2, a6, a5	# prephitmp_193,, _9
	j	.L305		#
.L314:
# @OPUS@\upstream\celt\mathops.h:191:    return x <= 0 ? 0 : celt_ilog2(x);
	movi.n	a14, -0xe	# _196,
	movi.n	a2, 0xd	# prephitmp_193,
# @OPUS@\upstream\celt\bands.c:147:          shift = celt_zlog2(bandE[i+c*m->nbEBands])-13;
	movi.n	a3, -0xd	# shift,
.L305:
# @OPUS@\upstream\celt\bands.c:148:          E = VSHR32(bandE[i+c*m->nbEBands], shift);
	ssl	a2	# prephitmp_193
	sll	a2, a4	# tmp135, _173
# @OPUS@\upstream\celt\bands.c:148:          E = VSHR32(bandE[i+c*m->nbEBands], shift);
	slli	a2, a2, 16	# tmp136, tmp135,
	srai	a2, a2, 16	# iftmp$18_60, tmp136,
.L307:
# @OPUS@\upstream\celt\bands.c:149:          g = EXTRACT16(celt_rcp(SHL32(E,3)));
	slli	a2, a2, 3	#, iftmp$18_60,
	s32i.n	a3, sp, 36	#,
	s32i.n	a10, sp, 40	#,
	call0	celt_rcp		#
# @OPUS@\upstream\celt\bands.c:150:          j=M*eBands[i]; do {
	l32i.n	a10, sp, 40	#,
# @OPUS@\upstream\celt\bands.c:150:          j=M*eBands[i]; do {
	l16si	a4, a13, 0	# MEM[base: _129, offset: 0B], tmp139
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:150:          j=M*eBands[i]; do {
	mull	a4, a4, a10	# j, tmp139, M
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	l16si	a7, a13, 2	# MEM[base: _129, offset: 2B], tmp142
	add.n	a5, a8, a4	# _40,, j
# @OPUS@\upstream\celt\bands.c:149:          g = EXTRACT16(celt_rcp(SHL32(E,3)));
	slli	a2, a2, 16	# tmp138,,
	slli	a6, a5, 2	# tmp145, _40,
	srai	a2, a2, 16	# g, tmp138,
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	mull	a7, a7, a10	# _56, tmp142, M
	l32i.n	a3, sp, 36	#,
	slli	a5, a5, 1	# tmp146, _40,
	bgei	a14, 1, .L308	# _196,,
	l32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	movi.n	a14, 1	# tmp147,
	add.n	a6, a8, a6	# ivtmp$395,, tmp145
	l32i.n	a8, sp, 20	# %sfp,
	sub	a14, a14, a3	# tmp148, tmp147, shift
	add.n	a5, a8, a5	# ivtmp$396,, tmp146
.L309:
	l32i.n	a3, a6, 0	# MEM[base: _158, offset: 0B], MEM[base: _158, offset: 0B]
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	ssl	a14	# tmp148
	sll	a3, a3	# tmp149, MEM[base: _158, offset: 0B]
	mul16s	a3, a3, a2	# tmp151, tmp149, g
	addi.n	a6, a6, 4	# ivtmp$395, ivtmp$395,
	srai	a3, a3, 15	# tmp152, tmp151,
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	s16i	a3, a5, 0	# MEM[base: _157, offset: 0B], tmp152
	addi.n	a5, a5, 2	# ivtmp$396, ivtmp$396,
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	blt	a4, a7, .L309	# j, _56,
	j	.L310		#
.L308:
	l32i.n	a3, sp, 16	# %sfp,
	l32i.n	a8, sp, 20	# %sfp,
	add.n	a6, a3, a6	# ivtmp$400,, tmp153
	add.n	a5, a8, a5	# ivtmp$401,, tmp154
.L311:
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	l32i.n	a3, a6, 0	# MEM[base: _134, offset: 0B], MEM[base: _134, offset: 0B]
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	ssr	a14	# _196
	sra	a3, a3	# tmp155, MEM[base: _134, offset: 0B]
	mul16s	a3, a3, a2	# tmp157, tmp155, g
	addi.n	a6, a6, 4	# ivtmp$400, ivtmp$400,
	srai	a3, a3, 15	# tmp158, tmp157,
# @OPUS@\upstream\celt\bands.c:151:             X[j+c*N] = MULT16_16_Q15(VSHR32(freq[j+c*N],shift-1),g);
	s16i	a3, a5, 0	# MEM[base: _133, offset: 0B], tmp158
	addi.n	a5, a5, 2	# ivtmp$401, ivtmp$401,
# @OPUS@\upstream\celt\bands.c:152:          } while (++j<M*eBands[i+1]);
	blt	a4, a7, .L311	# j, _56,
.L310:
# @OPUS@\upstream\celt\bands.c:153:       } while (++i<end);
	l32i.n	a3, sp, 12	# %sfp,
	addi.n	a12, a12, 1	# i, i,
	addi.n	a13, a13, 2	# ivtmp$404, ivtmp$404,
	blt	a12, a3, .L312	# i,,
# @OPUS@\upstream\celt\bands.c:154:    } while (++c<C);
	l32i.n	a6, sp, 0	# %sfp,
	l32i.n	a8, sp, 4	# %sfp,
	l32i.n	a2, sp, 28	# %sfp,
	addi.n	a6, a6, 1	#,,
	add.n	a8, a8, a2	#,,
	l32i.n	a3, sp, 32	# %sfp,
	s32i.n	a6, sp, 0	# %sfp,
	s32i.n	a8, sp, 4	# %sfp,
	mov.n	a14, a15	# m, m
	mov.n	a13, a10	# M, M
	blt	a6, a3, .L313	#,,
# @OPUS@\upstream\celt\bands.c:155: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	normalise_bands, .-normalise_bands
	.section	.text.denormalise_bands,"ax",@progbits
	.literal_position
	.literal .LC29, 16384
	.literal .LC30, eMeans
	.literal .LC31, 32767
	.literal .LC32, -32768
	.literal .LC33, 10204
	.literal .LC34, 14819
	.literal .LC35, 22804
	.literal .LC36, 16383
	.align	4
	.global	denormalise_bands
	.type	denormalise_bands, @function
# Function: denormalise_bands
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif /* FIXED_POINT */
# C context:
# C context: /* De-normalise the energy to produce the synthesis from the unit-energy bands */
# C context: void denormalise_bands(const CELTMode *m, const celt_norm * OPUS_RESTRICT X,
# C context: celt_sig * OPUS_RESTRICT freq, const opus_val16 *bandLogE, int start,
# C context: int end, int M, int downsample, int silence)
# C context: {
# C context: int i, N;
denormalise_bands:
	addi	sp, sp, -80	#,,
# @OPUS@\upstream\celt\bands.c:205:    N = M*m->shortMdctSize;
	l32i.n	a11, a2, 36	# *m_83(D).shortMdctSize, *m_83(D).shortMdctSize
# @OPUS@\upstream\celt\bands.c:199: {
	s32i	a14, sp, 64	#,
	s32i.n	a15, sp, 60	#,
	l32i	a14, sp, 80	# M, M
# @OPUS@\upstream\celt\bands.c:204:    const opus_int16 *eBands = m->eBands;
	l32i.n	a15, a2, 24	# *m_83(D).eBands, eBands
# @OPUS@\upstream\celt\bands.c:199: {
	s32i.n	a7, sp, 4	# %sfp, end
# @OPUS@\upstream\celt\bands.c:206:    bound = M*eBands[end];
	slli	a7, a7, 1	#, end,
	add.n	a8, a15, a7	# tmp162, eBands,
# @OPUS@\upstream\celt\bands.c:205:    N = M*m->shortMdctSize;
	mull	a11, a14, a11	#, M, *m_83(D).shortMdctSize
# @OPUS@\upstream\celt\bands.c:206:    bound = M*eBands[end];
	l16si	a8, a8, 0	# *_4, tmp163
# @OPUS@\upstream\celt\bands.c:199: {
	l32i	a2, sp, 84	# downsample, downsample
	s32i	a13, sp, 68	#,
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
# @OPUS@\upstream\celt\bands.c:206:    bound = M*eBands[end];
	s32i.n	a7, sp, 8	# %sfp,
# @OPUS@\upstream\celt\bands.c:199: {
	s32i.n	a5, sp, 16	# %sfp, bandLogE
# @OPUS@\upstream\celt\bands.c:205:    N = M*m->shortMdctSize;
	s32i.n	a11, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:199: {
	mov.n	a10, a3	# X, X
	mov.n	a13, a4	# freq, freq
# @OPUS@\upstream\celt\bands.c:206:    bound = M*eBands[end];
	mull	a8, a8, a14	# bound, tmp163, M
# @OPUS@\upstream\celt\bands.c:207:    if (downsample!=1)
	beqi	a2, 1, .L320	# downsample,,
# @OPUS@\upstream\celt\bands.c:208:       bound = IMIN(bound, N/downsample);
	mov.n	a3, a2	#, downsample
	mov.n	a2, a11	#,
	s32i.n	a6, sp, 32	#,
	s32i.n	a8, sp, 28	#,
	s32i.n	a10, sp, 20	#,
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:208:       bound = IMIN(bound, N/downsample);
	l32i.n	a8, sp, 28	#,
	l32i.n	a6, sp, 32	#,
	l32i.n	a10, sp, 20	#,
	bge	a2, a8, .L320	# tmp169, bound,
	mov.n	a8, a2	# bound, tmp169
.L320:
# @OPUS@\upstream\celt\bands.c:209:    if (silence)
	l32i	a7, sp, 88	# silence,
	bnez.n	a7, .L322	#,
	slli	a7, a6, 1	# tmp170, start,
	add.n	a12, a15, a7	# _229, eBands, tmp170
# @OPUS@\upstream\celt\bands.c:215:    x = X+M*eBands[start];
	l16si	a3, a12, 0	# *_229, tmp172
	slli	a11, a8, 2	# tmp171, bound,
# @OPUS@\upstream\celt\bands.c:215:    x = X+M*eBands[start];
	mull	a3, a3, a14	# _14, tmp172, M
# @OPUS@\upstream\celt\bands.c:218:    OPUS_CLEAR(f, M*eBands[start]);
	mov.n	a2, a13	#, freq
# @OPUS@\upstream\celt\bands.c:215:    x = X+M*eBands[start];
	slli	a5, a3, 1	# tmp175, _14,
# @OPUS@\upstream\celt\bands.c:215:    x = X+M*eBands[start];
	add.n	a5, a10, a5	# x, X, tmp175
	add.n	a11, a13, a11	#, freq, tmp171
# @OPUS@\upstream\celt\bands.c:218:    OPUS_CLEAR(f, M*eBands[start]);
	movi.n	a4, 4	#,
	s32i.n	a5, sp, 20	#,
	s32i.n	a6, sp, 32	#,
	s32i.n	a7, sp, 24	#,
	s32i.n	a8, sp, 28	#,
	s32i.n	a11, sp, 12	# %sfp,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\bands.c:219:    f += M*eBands[start];
	l16si	a2, a12, 0	# *_229, tmp176
	l32i.n	a8, sp, 28	#,
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:219:    f += M*eBands[start];
	mull	a2, a2, a14	# tmp179, tmp176, M
	sub	a3, a3, a8	#,, bound
# @OPUS@\upstream\celt\bands.c:224:    for (i=start;i<end;i++)
	l32i.n	a6, sp, 32	#,
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:219:    f += M*eBands[start];
	slli	a2, a2, 2	# tmp180, tmp179,
	s32i.n	a3, sp, 0	# %sfp,
	add.n	a9, a13, a2	# f, freq, tmp180
# @OPUS@\upstream\celt\bands.c:224:    for (i=start;i<end;i++)
	l32i.n	a5, sp, 20	#,
	l32i.n	a7, sp, 24	#,
	blt	a6, a8, .L323	# start,,
.L331:
# @OPUS@\upstream\celt\bands.c:270:    OPUS_CLEAR(&freq[bound], N-bound);
	l32i.n	a3, sp, 0	# %sfp,
	l32i.n	a2, sp, 12	# %sfp,
	movi.n	a4, 4	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\bands.c:271: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
.L323:
	l32i.n	a8, sp, 16	# %sfp,
	l32r	a2, .LC30	#, tmp181
	add.n	a13, a8, a7	# ivtmp$432,, tmp170
	l32i.n	a8, sp, 8	# %sfp,
	l32r	a10, .LC31	#, tmp243
	add.n	a6, a6, a2	# ivtmp$433, start, tmp181
	add.n	a7, a15, a8	# _222, eBands,
.L330:
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	l8ui	a4, a6, 0	# MEM[base: _240, offset: 0B],
	l16si	a2, a13, 0	# MEM[base: _241, offset: 0B], _32
	slli	a4, a4, 24	# tmp193, MEM[base: _240, offset: 0B],
# @OPUS@\upstream\celt\bands.c:232:       j=M*eBands[i];
	l16si	a3, a12, 0	# MEM[base: _242, offset: 0B], tmp183
# @OPUS@\upstream\celt\bands.c:233:       band_end = M*eBands[i+1];
	l16si	a11, a12, 2	# MEM[base: _242, offset: 2B], tmp186
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	srai	a4, a4, 18	# _36, tmp193,
	add.n	a2, a2, a4	# tmp244, _32, _36
# @OPUS@\upstream\celt\bands.c:232:       j=M*eBands[i];
	mull	a3, a3, a14	# j, tmp183, M
# @OPUS@\upstream\celt\bands.c:233:       band_end = M*eBands[i+1];
	mull	a11, a11, a14	# band_end, tmp186, M
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	blt	a10, a2, .L332	# tmp243, tmp244,
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	l32r	a4, .LC32	#,
	blt	a2, a4, .L334	# tmp244,,
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	slli	a2, a2, 16	# tmp198, tmp244,
# @OPUS@\upstream\celt\bands.c:239:       shift = 16-(lg>>DB_SHIFT);
	srai	a15, a2, 26	# tmp200, tmp198,
# @OPUS@\upstream\celt\bands.c:239:       shift = 16-(lg>>DB_SHIFT);
	movi.n	a8, 0x10	#,
	sub	a15, a8, a15	# shift,, tmp200
# @OPUS@\upstream\celt\bands.c:240:       if (shift>31)
	movi.n	a4, 0x1f	#,
# @OPUS@\upstream\celt\bands.c:234:       lg = SATURATE16(ADD32(bandLogE[i], SHL32((opus_val32)eMeans[i],6)));
	ssr	a8	#
	sra	a2, a2	# iftmp$31_102, tmp198
# @OPUS@\upstream\celt\bands.c:240:       if (shift>31)
	blt	a4, a15, .L334	#, shift,
	l32r	a8, .LC33	#,
	extui	a2, a2, 0, 10	# tmp206, iftmp$31_102,
	slli	a2, a2, 4	# _294, tmp206,
	mull	a4, a2, a8	# tmp207, _294,
	l32r	a8, .LC34	#,
	srai	a4, a4, 15	# tmp209, tmp207,
	add.n	a4, a4, a8	# tmp211, tmp209,
	slli	a4, a4, 16	# tmp214, tmp211,
	srai	a4, a4, 16	# tmp213, tmp214,
	mull	a4, a4, a2	# tmp215, tmp213, _294
	l32r	a8, .LC35	#,
	srai	a4, a4, 15	# tmp216, tmp215,
	add.n	a4, a4, a8	# tmp218, tmp216,
	slli	a4, a4, 16	# tmp221, tmp218,
	srai	a4, a4, 16	# tmp220, tmp221,
	mull	a4, a4, a2	# tmp222, tmp220, _294
	l32r	a2, .LC36	#,
	srai	a4, a4, 15	# tmp223, tmp222,
	add.n	a4, a4, a2	# tmp225, tmp223,
	slli	a4, a4, 16	# tmp227, tmp225,
	srai	a4, a4, 16	# _322, tmp227,
# @OPUS@\upstream\celt\bands.c:249:       if (shift<0)
	bgez	a15, .L325	# shift,
# @OPUS@\upstream\celt\bands.c:254:          if (shift <= -2)
	bnei	a15, -1, .L335	# shift,,
	movi.n	a15, 1	# prephitmp_329,
	j	.L324		#
.L332:
	movi.n	a15, 2	# prephitmp_329,
	l32r	a4, .LC29	#, _327
	j	.L324		#
.L335:
	l32r	a4, .LC29	#, _327
	movi.n	a15, 2	# prephitmp_329,
.L324:
	mov.n	a8, a9	# ivtmp$420, f
	mov.n	a2, a5	# ivtmp$422, x
.L327:
# @OPUS@\upstream\celt\bands.c:260:             *f++ = SHL32(MULT16_16(*x++, g), -shift);
	l16si	a2, a2, 0	# MEM[base: _268, offset: 0B], tmp228
	addi.n	a5, a5, 2	# x, x,
	mull	a2, a2, a4	# tmp231, tmp228, _327
	addi.n	a9, a9, 4	# f, f,
	ssl	a15	# prephitmp_329
	sll	a2, a2	# tmp232, tmp231
# @OPUS@\upstream\celt\bands.c:260:             *f++ = SHL32(MULT16_16(*x++, g), -shift);
	s32i.n	a2, a8, 0	# MEM[base: _267, offset: 0B], tmp232
# @OPUS@\upstream\celt\bands.c:261:          } while (++j<band_end);
	addi.n	a3, a3, 1	# j, j,
	mov.n	a8, a9	# ivtmp$420, f
	mov.n	a2, a5	# ivtmp$422, x
	blt	a3, a11, .L327	# j, band_end,
	j	.L328		#
.L334:
	l32i	a4, sp, 88	# silence, _283
# @OPUS@\upstream\celt\bands.c:242:          shift=0;
	mov.n	a15, a4	# shift, _283
.L325:
	mov.n	a8, a9	# ivtmp$411, f
	mov.n	a2, a5	# ivtmp$413, x
.L329:
# @OPUS@\upstream\celt\bands.c:266:             *f++ = SHR32(MULT16_16(*x++, g), shift);
	l16si	a2, a2, 0	# MEM[base: _280, offset: 0B], tmp233
	addi.n	a5, a5, 2	# x, x,
	mull	a2, a2, a4	# tmp236, tmp233, _283
	addi.n	a9, a9, 4	# f, f,
	ssr	a15	# shift
	sra	a2, a2	# tmp237, tmp236
# @OPUS@\upstream\celt\bands.c:266:             *f++ = SHR32(MULT16_16(*x++, g), shift);
	s32i.n	a2, a8, 0	# MEM[base: _279, offset: 0B], tmp237
# @OPUS@\upstream\celt\bands.c:267:          } while (++j<band_end);
	addi.n	a3, a3, 1	# j, j,
	mov.n	a8, a9	# ivtmp$411, f
	mov.n	a2, a5	# ivtmp$413, x
	blt	a3, a11, .L329	# j, band_end,
.L328:
	addi.n	a12, a12, 2	# ivtmp$431, ivtmp$431,
	addi.n	a13, a13, 2	# ivtmp$432, ivtmp$432,
	addi.n	a6, a6, 1	# ivtmp$433, ivtmp$433,
# @OPUS@\upstream\celt\bands.c:224:    for (i=start;i<end;i++)
	bne	a7, a12, .L330	# _222, ivtmp$431,
	j	.L331		#
.L322:
# @OPUS@\upstream\celt\bands.c:215:    x = X+M*eBands[start];
	l16si	a3, a15, 0	# *eBands_84, tmp238
# @OPUS@\upstream\celt\bands.c:218:    OPUS_CLEAR(f, M*eBands[start]);
	movi.n	a4, 4	#,
	mull	a3, a3, a14	#, tmp238, M
	mov.n	a2, a13	#, freq
	call0	yoradio_opus_clear		#
	s32i.n	a13, sp, 12	# %sfp, freq
	j	.L331		#
	.size	denormalise_bands, .-denormalise_bands
	.section	.text.anti_collapse,"ax",@progbits
	.literal_position
	.literal .LC37, 16383
	.literal .LC38, 8388480
	.literal .LC39, 10204
	.literal .LC40, 14819
	.literal .LC41, 22804
	.literal .LC42, 32767
	.literal .LC43, 23169
	.literal .LC44, 23170
	.literal .LC45, 1664525
	.literal .LC46, 1013904223
	.literal .LC47, 32768
	.align	4
	.global	anti_collapse
	.type	anti_collapse, @function
# Function: anti_collapse
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* This prevents energy collapse for transients with multiple short MDCTs */
# C context: void anti_collapse(const CELTMode *m, celt_norm *X_, unsigned char *collapse_masks, int LM, int C, int size,
# C context: int start, int end, const opus_val16 *logE, const opus_val16 *prev1logE,
# C context: const opus_val16 *prev2logE, const int *pulses, opus_uint32 seed, int arch)
# C context: {
# C context: int c, i, j, k;
anti_collapse:
	addi	sp, sp, -112	#,,
	s32i.n	a2, sp, 16	# %sfp, m
	s32i.n	a3, sp, 36	# %sfp, X_
# @OPUS@\upstream\celt\bands.c:279:    for (i=start;i<end;i++)
	l32i	a2, sp, 112	# start,
	l32i	a3, sp, 116	# end,
# @OPUS@\upstream\celt\bands.c:277: {
	s32i	a14, sp, 96	#,
	s32i.n	a7, sp, 40	# %sfp, size
	s32i	a0, sp, 108	#,
	s32i	a12, sp, 104	#,
	s32i	a13, sp, 100	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\celt\bands.c:277: {
	s32i.n	a6, sp, 12	# %sfp, C
	mov.n	a14, a5	# LM, LM
	l32i	a7, sp, 136	# seed, seed
# @OPUS@\upstream\celt\bands.c:279:    for (i=start;i<end;i++)
	bge	a2, a3, .L343	#,,
	mov.n	a5, a2	#,
	slli	a3, a5, 2	# tmp264,,
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	movi.n	a5, 1	# tmp263,
	ssl	a14	# LM
	sll	a5, a5	#, tmp263
	mull	a2, a2, a6	# tmp265,, C
	s32i.n	a5, sp, 0	# %sfp,
	l32i	a5, sp, 132	# pulses, pulses
	add.n	a2, a4, a2	#, collapse_masks, tmp265
	add.n	a3, a5, a3	#, pulses, tmp264
	s32i.n	a3, sp, 56	# %sfp,
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	mov.n	a12, a7	# seed, seed
.L369:
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	l32i	a6, sp, 112	# start,
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	addi.n	a6, a6, 1	#,,
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	l32i.n	a2, a7, 24	# m_135(D)->eBands, _1
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	slli	a3, a6, 1	# _4,,
	s32i	a6, sp, 64	# %sfp,
	addi	a6, a3, -2	#, _4,
# @OPUS@\upstream\celt\bands.c:292:       depth = celt_udiv(1+pulses[i], (m->eBands[i+1]-m->eBands[i]))>>LM;
	l32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	add.n	a3, a2, a3	# tmp267, _1, _4
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	add.n	a2, a2, a6	# tmp271, _1,
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	l16si	a3, a3, 0	# *_5, tmp268
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	l16si	a15, a2, 0	# *_11, tmp272
# @OPUS@\upstream\celt\bands.c:292:       depth = celt_udiv(1+pulses[i], (m->eBands[i+1]-m->eBands[i]))>>LM;
	l32i.n	a2, a7, 0	# MEM[base: _591, offset: 0B], MEM[base: _591, offset: 0B]
# @OPUS@\upstream\celt\bands.c:289:       N0 = m->eBands[i+1]-m->eBands[i];
	sub	a15, a3, a15	# N0, tmp268, tmp272
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a15	#, N0
	addi.n	a2, a2, 1	#, MEM[base: _591, offset: 0B],
	s32i.n	a6, sp, 24	# %sfp,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:295:       thresh32 = SHR32(celt_exp2(-SHL16(depth, 10-BITRES)),1);
	l32r	a3, .LC38	#,
# @OPUS@\upstream\celt\bands.c:292:       depth = celt_udiv(1+pulses[i], (m->eBands[i+1]-m->eBands[i]))>>LM;
	ssr	a14	# LM
	srl	a2, a2	# depth,
# @OPUS@\upstream\celt\bands.c:295:       thresh32 = SHR32(celt_exp2(-SHL16(depth, 10-BITRES)),1);
	slli	a2, a2, 7	# tmp282, depth,
	and	a2, a2, a3	# tmp283, tmp282,
	neg	a2, a2	# tmp286, tmp283
# @OPUS@\upstream\celt\mathops.h:245:    if (integer>14)
	l32r	a4, .LC37	#,
# @OPUS@\upstream\celt\bands.c:295:       thresh32 = SHR32(celt_exp2(-SHL16(depth, 10-BITRES)),1);
	slli	a2, a2, 16	# tmp287, tmp286,
# @OPUS@\upstream\celt\mathops.h:244:    integer = SHR16(x,10);
	srai	a3, a2, 26	# _184, tmp287,
# @OPUS@\upstream\celt\mathops.h:245:    if (integer>14)
	s32i.n	a4, sp, 44	# %sfp,
	movi.n	a5, 0xe	#,
# @OPUS@\upstream\celt\bands.c:295:       thresh32 = SHR32(celt_exp2(-SHL16(depth, 10-BITRES)),1);
	srai	a2, a2, 16	# _26, tmp287,
# @OPUS@\upstream\celt\mathops.h:245:    if (integer>14)
	blt	a5, a3, .L345	#, _184,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	movi.n	a6, 0	#,
	movi.n	a4, -0xf	# tmp294,
	s32i.n	a6, sp, 44	# %sfp,
	blt	a3, a4, .L345	# _184, tmp294,
# @OPUS@\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	extui	a4, a3, 0, 16	# _184, _184
	slli	a4, a4, 10	# tmp297, _184,
# @OPUS@\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	sub	a2, a2, a4	# tmp299, _26, tmp297
# @OPUS@\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	slli	a2, a2, 20	# tmp302, tmp299,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	l32r	a4, .LC39	#, tmp304
# @OPUS@\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	srai	a2, a2, 16	# frac, tmp302,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	mul16s	a4, a2, a4	# tmp303, frac, tmp304
	l32r	a5, .LC40	#, tmp308
	srai	a4, a4, 15	# tmp305, tmp303,
	add.n	a4, a4, a5	# tmp307, tmp305, tmp308
	mul16s	a4, a4, a2	# tmp309, tmp307, frac
	l32r	a5, .LC41	#, tmp313
	srai	a4, a4, 15	# tmp310, tmp309,
	add.n	a4, a4, a5	# tmp312, tmp310, tmp313
	mul16s	a2, a4, a2	# tmp314, tmp312, frac
	l32r	a7, .LC37	#,
	srai	a2, a2, 15	# tmp315, tmp314,
	add.n	a2, a2, a7	# tmp317, tmp315,
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	movi.n	a4, -2	# tmp320,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	slli	a2, a2, 16	# tmp319, tmp317,
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	sub	a4, a4, a3	# _211, tmp320, _184
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	srai	a2, a2, 16	# _209, tmp319,
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	blti	a4, 1, .L347	# _211,,
	ssr	a4	# _211
	sra	a2, a2	# iftmp$51_212, _209
# @OPUS@\upstream\celt\bands.c:296:       thresh = MULT16_32_Q15(QCONST16(0.5f, 15), MIN32(32767,thresh32));
	srai	a3, a2, 17	# tmp325, iftmp$51_212,
	slli	a3, a3, 15	# tmp327, tmp325,
	extui	a2, a2, 2, 15	# tmp324, iftmp$51_212,,
	add.n	a2, a2, a3	# tmp330, tmp324, tmp327
	slli	a2, a2, 16	# tmp331, tmp330,
	srai	a2, a2, 16	#, tmp331,
	s32i.n	a2, sp, 44	# %sfp,
	j	.L345		#
.L347:
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	addi.n	a3, a3, 2	# tmp332, _184,
	ssl	a3	# tmp332
	sll	a2, a2	# tmp333, _209
# @OPUS@\upstream\celt\bands.c:296:       thresh = MULT16_32_Q15(QCONST16(0.5f, 15), MIN32(32767,thresh32));
	l32r	a4, .LC42	#, tmp506
# @OPUS@\upstream\celt\bands.c:295:       thresh32 = SHR32(celt_exp2(-SHL16(depth, 10-BITRES)),1);
	srai	a2, a2, 1	# thresh32, tmp333,
# @OPUS@\upstream\celt\bands.c:296:       thresh = MULT16_32_Q15(QCONST16(0.5f, 15), MIN32(32767,thresh32));
	mov.n	a3, a2	# thresh32, thresh32
	bge	a4, a2, .L348	# tmp506, thresh32,
	mov.n	a3, a4	# thresh32, tmp506
.L348:
	srai	a3, a3, 16	# tmp340, thresh32,
	slli	a3, a3, 31	# tmp343, tmp340,
	srai	a3, a3, 16	# _36, tmp343,
	bge	a4, a2, .L349	# tmp506, thresh32,
	l32r	a4, .LC37	#,
	add.n	a2, a3, a4	# tmp345, _36,
	slli	a2, a2, 16	# tmp347, tmp345,
	srai	a2, a2, 16	#, tmp347,
	s32i.n	a2, sp, 44	# %sfp,
	j	.L345		#
.L349:
	extui	a2, a2, 1, 15	# tmp350, thresh32,,
	add.n	a2, a3, a2	# tmp352, _36, tmp350
	slli	a2, a2, 16	# tmp353, tmp352,
	srai	a2, a2, 16	#, tmp353,
	s32i.n	a2, sp, 44	# %sfp,
.L345:
# @OPUS@\upstream\celt\bands.c:299:          t = N0<<LM;
	ssl	a14	# LM
	sll	a6, a15	#, N0
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a6	# _147,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a2, 0x1f	# tmp354,
	sub	a2, a2, a3	# tmp356, tmp354, _147
# @OPUS@\upstream\celt\bands.c:300:          shift = celt_ilog2(t)>>1;
	slli	a2, a2, 16	# tmp358, tmp356,
# @OPUS@\upstream\celt\bands.c:300:          shift = celt_ilog2(t)>>1;
	srai	a2, a2, 17	#, tmp358,
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:301:          t = SHL32(t, (7-shift)<<1);
	l32i.n	a7, sp, 20	# %sfp,
	movi.n	a2, 7	# tmp361,
	sub	a2, a2, a7	# tmp362, tmp361,
	slli	a2, a2, 1	# tmp363, tmp362,
# @OPUS@\upstream\celt\bands.c:302:          sqrt_1 = celt_rsqrt_norm(t);
	ssl	a2	# tmp363
	sll	a2, a6	#,
# @OPUS@\upstream\celt\bands.c:299:          t = N0<<LM;
	s32i.n	a6, sp, 48	# %sfp,
# @OPUS@\upstream\celt\bands.c:302:          sqrt_1 = celt_rsqrt_norm(t);
	call0	celt_rsqrt_norm		#
	l32i.n	a7, sp, 44	# %sfp,
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	movi.n	a2, -0x10	# tmp582,
# @OPUS@\upstream\celt\bands.c:302:          sqrt_1 = celt_rsqrt_norm(t);
	movi.n	a6, 0	#,
	slli	a7, a7, 16	#,,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	slli	a2, a2, 16	#, tmp582,
# @OPUS@\upstream\celt\bands.c:302:          sqrt_1 = celt_rsqrt_norm(t);
	l32i.n	a13, sp, 60	# %sfp, ivtmp$444
	s32i.n	a6, sp, 8	# %sfp,
# @OPUS@\upstream\celt\bands.c:309:       c=0; do
	s32i.n	a6, sp, 4	# %sfp,
	s32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	s32i.n	a2, sp, 52	# %sfp,
.L368:
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l32i.n	a6, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l32i.n	a3, a2, 8	# m_135(D)->nbEBands, _43
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l32i	a7, sp, 112	# start,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	mull	a2, a3, a6	# tmp366, _43,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l32i	a6, sp, 124	# prev1logE,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	add.n	a2, a2, a7	# tmp367, tmp366,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	slli	a2, a2, 1	# _47, tmp367,
# @OPUS@\upstream\celt\bands.c:318:          prev2 = prev2logE[c*m->nbEBands+i];
	l32i	a7, sp, 128	# prev2logE,
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	add.n	a4, a6, a2	# tmp368,, _47
# @OPUS@\upstream\celt\bands.c:319:          if (C==1)
	l32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\celt\bands.c:318:          prev2 = prev2logE[c*m->nbEBands+i];
	add.n	a5, a7, a2	# tmp371,, _47
# @OPUS@\upstream\celt\bands.c:317:          prev1 = prev1logE[c*m->nbEBands+i];
	l16si	a4, a4, 0	# *_48, prev1
# @OPUS@\upstream\celt\bands.c:318:          prev2 = prev2logE[c*m->nbEBands+i];
	l16si	a5, a5, 0	# *_49, prev2
# @OPUS@\upstream\celt\bands.c:319:          if (C==1)
	bnei	a6, 1, .L350	#,,
# @OPUS@\upstream\celt\bands.c:321:             prev1 = MAX16(prev1,prev1logE[m->nbEBands+i]);
	l32i	a7, sp, 112	# start,
	add.n	a3, a3, a7	# tmp374, _43,
	l32i	a7, sp, 124	# prev1logE,
	slli	a3, a3, 1	# _52, tmp374,
	add.n	a6, a7, a3	# tmp376,, _52
# @OPUS@\upstream\celt\bands.c:321:             prev1 = MAX16(prev1,prev1logE[m->nbEBands+i]);
	l16ui	a6, a6, 0	# *_53,
	slli	a6, a6, 16	# tmp502, *_53,
	srai	a7, a6, 16	# tmp378, tmp502,
	bge	a7, a4, .L351	# tmp378, prev1,
	slli	a6, a4, 16	# tmp502, prev1,
.L351:
# @OPUS@\upstream\celt\bands.c:322:             prev2 = MAX16(prev2,prev2logE[m->nbEBands+i]);
	l32i	a7, sp, 128	# prev2logE,
# @OPUS@\upstream\celt\bands.c:321:             prev1 = MAX16(prev1,prev1logE[m->nbEBands+i]);
	srai	a4, a6, 16	# prev1, tmp502,
# @OPUS@\upstream\celt\bands.c:322:             prev2 = MAX16(prev2,prev2logE[m->nbEBands+i]);
	add.n	a3, a7, a3	# tmp384,, _52
# @OPUS@\upstream\celt\bands.c:322:             prev2 = MAX16(prev2,prev2logE[m->nbEBands+i]);
	l16ui	a3, a3, 0	# *_55,
	slli	a3, a3, 16	# tmp503, *_55,
	srai	a6, a3, 16	# tmp386, tmp503,
	bge	a6, a5, .L352	# tmp386, prev2,
	slli	a3, a5, 16	# tmp503, prev2,
.L352:
	srai	a5, a3, 16	# prev2, tmp503,
.L350:
# @OPUS@\upstream\celt\bands.c:324:          Ediff = EXTEND32(logE[c*m->nbEBands+i])-EXTEND32(MIN16(prev1,prev2));
	l32i	a6, sp, 120	# logE,
	add.n	a2, a6, a2	# tmp391,, _47
	l16si	a3, a2, 0	# *_57, tmp392
# @OPUS@\upstream\celt\bands.c:324:          Ediff = EXTEND32(logE[c*m->nbEBands+i])-EXTEND32(MIN16(prev1,prev2));
	mov.n	a2, a4	# prev1, prev1
	bge	a5, a4, .L353	# prev2, prev1,
	mov.n	a2, a5	# prev1, prev2
.L353:
	slli	a2, a2, 16	# tmp402, prev1,
	srai	a2, a2, 16	# tmp401, tmp402,
# @OPUS@\upstream\celt\bands.c:328:          if (Ediff < 16384)
	l32r	a7, .LC37	#,
# @OPUS@\upstream\celt\bands.c:324:          Ediff = EXTEND32(logE[c*m->nbEBands+i])-EXTEND32(MIN16(prev1,prev2));
	sub	a3, a3, a2	# Ediff, tmp392, tmp401
# @OPUS@\upstream\celt\bands.c:333:             r = 0;
	movi.n	a2, 0	# r,
# @OPUS@\upstream\celt\bands.c:328:          if (Ediff < 16384)
	blt	a7, a3, .L354	#, Ediff,
# @OPUS@\upstream\celt\bands.c:325:          Ediff = MAX32(0, Ediff);
	movgez	a2, a3, a3	# Ediff, Ediff, Ediff
# @OPUS@\upstream\celt\bands.c:330:             opus_val32 r32 = SHR32(celt_exp2(-EXTRACT16(Ediff)),1);
	neg	a2, a2	# tmp407, Ediff
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	l32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\bands.c:330:             opus_val32 r32 = SHR32(celt_exp2(-EXTRACT16(Ediff)),1);
	slli	a2, a2, 16	# tmp408, tmp407,
# @OPUS@\upstream\celt\mathops.h:244:    integer = SHR16(x,10);
	srai	a3, a2, 26	# _219, tmp408,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	srai	a4, a6, 16	# tmp412,,
# @OPUS@\upstream\celt\bands.c:330:             opus_val32 r32 = SHR32(celt_exp2(-EXTRACT16(Ediff)),1);
	srai	a5, a2, 16	# _64, tmp408,
# @OPUS@\upstream\celt\mathops.h:247:    else if (integer < -15)
	movi.n	a2, 0	# r,
	beq	a3, a4, .L354	# _219, tmp412,
# @OPUS@\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	extui	a2, a3, 0, 16	# _219, _219
	slli	a2, a2, 10	# tmp415, _219,
# @OPUS@\upstream\celt\mathops.h:249:    frac = celt_exp2_frac(x-SHL16(integer,10));
	sub	a2, a5, a2	# tmp417, _64, tmp415
# @OPUS@\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	slli	a2, a2, 20	# tmp420, tmp417,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	l32r	a4, .LC39	#, tmp422
# @OPUS@\upstream\celt\mathops.h:230:    frac = SHL16(x, 4);
	srai	a2, a2, 16	# frac, tmp420,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	mul16s	a4, a2, a4	# tmp421, frac, tmp422
	l32r	a5, .LC40	#, tmp426
	srai	a4, a4, 15	# tmp423, tmp421,
	add.n	a4, a4, a5	# tmp425, tmp423, tmp426
	mul16s	a4, a4, a2	# tmp427, tmp425, frac
	l32r	a5, .LC41	#, tmp431
	srai	a4, a4, 15	# tmp428, tmp427,
	add.n	a4, a4, a5	# tmp430, tmp428, tmp431
	mul16s	a2, a4, a2	# tmp432, tmp430, frac
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	movi.n	a4, -2	# tmp438,
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	srai	a2, a2, 15	# tmp433, tmp432,
	add.n	a2, a2, a7	# tmp435, tmp433,
	slli	a2, a2, 16	# tmp437, tmp435,
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	sub	a4, a4, a3	# _246, tmp438, _219
# @OPUS@\upstream\celt\mathops.h:231:    return ADD16(D0, MULT16_16_Q15(frac, ADD16(D1, MULT16_16_Q15(frac, ADD16(D2 , MULT16_16_Q15(D3,frac))))));
	srai	a2, a2, 16	# _244, tmp437,
# @OPUS@\upstream\celt\mathops.h:250:    return VSHR32(EXTEND32(frac), -integer-2);
	blti	a4, 1, .L356	# _246,,
	ssr	a4	# _246
	sra	a2, a2	# tmp439, _244
	srai	a2, a2, 1	# tmp440, tmp439,
	slli	a2, a2, 1	# r, tmp440,
	j	.L354		#
.L356:
	addi.n	a3, a3, 2	# tmp445, _219,
	ssl	a3	# tmp445
	sll	a2, a2	# tmp446, _244
	srai	a2, a2, 1	# tmp444, tmp446,
	bge	a7, a2, .L357	#, tmp444,
	mov.n	a2, a7	# tmp444,
.L357:
	slli	a2, a2, 17	# tmp454, tmp444,
	srai	a2, a2, 16	# r, tmp454,
.L354:
# @OPUS@\upstream\celt\bands.c:335:          if (LM==3)
	bnei	a14, 3, .L358	# LM,,
# @OPUS@\upstream\celt\bands.c:336:             r = MULT16_16_Q14(23170, MIN32(23169, r));
	l32r	a4, .LC43	#, tmp456
	mov.n	a3, a2	# r, r
	slli	a4, a4, 16	# tmp460, tmp456,
	srai	a4, a4, 16	# tmp459, tmp460,
	bge	a4, a2, .L359	# tmp459, r,
	l32r	a3, .LC43	#, r
.L359:
	l32r	a2, .LC44	#, tmp462
	mul16s	a2, a3, a2	# tmp461, r, tmp462
# @OPUS@\upstream\celt\bands.c:336:             r = MULT16_16_Q14(23170, MIN32(23169, r));
	slli	a2, a2, 2	# tmp463, tmp461,
	srai	a2, a2, 16	# r, tmp463,
.L358:
# @OPUS@\upstream\celt\bands.c:337:          r = SHR16(MIN16(thresh, r),1);
	l32i.n	a6, sp, 32	# %sfp,
	mov.n	a3, a2	# r, r
	srai	a4, a6, 16	# tmp468,,
	bge	a4, a2, .L360	# tmp468, r,
	l32i.n	a7, sp, 44	# %sfp,
	mov.n	a3, a7	# r,
.L360:
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	l32i.n	a4, sp, 16	# %sfp,
	l32i.n	a6, sp, 24	# %sfp,
	l32i.n	a2, a4, 24	# m_135(D)->eBands, m_135(D)->eBands
# @OPUS@\upstream\celt\bands.c:337:          r = SHR16(MIN16(thresh, r),1);
	slli	a7, a3, 16	# tmp471, r,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	add.n	a2, a2, a6	# tmp477, m_135(D)->eBands,
# @OPUS@\upstream\celt\bands.c:338:          r = SHR32(MULT16_16_Q15(sqrt_1, r),shift);
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:337:          r = SHR16(MIN16(thresh, r),1);
	srai	a7, a7, 17	# tmp472, tmp471,
# @OPUS@\upstream\celt\bands.c:338:          r = SHR32(MULT16_16_Q15(sqrt_1, r),shift);
	mull	a7, a7, a6	# tmp473, tmp472,
	l32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	l16si	a2, a2, 0	# *_84, tmp478
# @OPUS@\upstream\celt\bands.c:338:          r = SHR32(MULT16_16_Q15(sqrt_1, r),shift);
	srai	a7, a7, 15	# tmp474, tmp473,
	ssr	a6	#
	sra	a7, a7	# _80, tmp474
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	l32i.n	a6, sp, 8	# %sfp,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	ssl	a14	# LM
	sll	a2, a2	# tmp481, tmp478
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	add.n	a2, a2, a6	# tmp482, tmp481,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	l32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	l32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:338:          r = SHR32(MULT16_16_Q15(sqrt_1, r),shift);
	slli	a11, a7, 16	# tmp475, _80,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	slli	a2, a2, 1	# tmp483, tmp482,
# @OPUS@\upstream\celt\bands.c:338:          r = SHR32(MULT16_16_Q15(sqrt_1, r),shift);
	srai	a11, a11, 16	# r, tmp475,
# @OPUS@\upstream\celt\bands.c:348:          X = X_+c*size+(m->eBands[i]<<LM);
	add.n	a2, a3, a2	# X,, tmp483
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	blti	a6, 1, .L361	#,,
# @OPUS@\upstream\celt\bands.c:316:          int renormalize=0;
	movi.n	a3, 0	# renormalize,
	l32r	a10, .LC45	#, tmp577
	l32r	a9, .LC46	#, tmp578
	l32r	a8, .LC47	#, tmp579
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	mov.n	a6, a3	# k, renormalize
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	neg	a7, a7	# tmp580, _80
.L367:
# @OPUS@\upstream\celt\bands.c:352:             if (!(collapse_masks[i*C+c]&1<<k))
	l8ui	a4, a13, 0	# MEM[base: _100, offset: 0B], MEM[base: _100, offset: 0B]
# @OPUS@\upstream\celt\bands.c:352:             if (!(collapse_masks[i*C+c]&1<<k))
	ssr	a6	# k
	sra	a4, a4	# tmp485, MEM[base: _100, offset: 0B]
	extui	a4, a4, 0, 1	# j, tmp485,
# @OPUS@\upstream\celt\bands.c:352:             if (!(collapse_masks[i*C+c]&1<<k))
	bnez.n	a4, .L362	# j,
# @OPUS@\upstream\celt\bands.c:355:                for (j=0;j<N0;j++)
	blti	a15, 1, .L375	# N0,,
.L366:
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	ssl	a14	# LM
	sll	a3, a4	# tmp491, j
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	mull	a12, a12, a10	# tmp486, seed, tmp577
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	add.n	a3, a3, a6	# tmp492, tmp491, k
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	slli	a3, a3, 1	# tmp493, tmp492,
# @OPUS@\upstream\celt\bands.c:63:    return 1664525 * seed + 1013904223;
	add.n	a12, a12, a9	# seed, tmp486, tmp578
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	add.n	a3, a2, a3	# tmp494, X, tmp493
	bany	a12, a8, .L363	# seed, tmp579,
	s16i	a7, a3, 0	# *_16, tmp580
# @OPUS@\upstream\celt\bands.c:355:                for (j=0;j<N0;j++)
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:355:                for (j=0;j<N0;j++)
	bne	a4, a15, .L366	# j, N0,
	j	.L375		#
.L363:
# @OPUS@\upstream\celt\bands.c:358:                   X[(j<<LM)+k] = (seed&0x8000 ? r : -r);
	s16i	a11, a3, 0	# *_602, r
# @OPUS@\upstream\celt\bands.c:355:                for (j=0;j<N0;j++)
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:355:                for (j=0;j<N0;j++)
	bne	a15, a4, .L366	# N0, j,
.L375:
# @OPUS@\upstream\celt\bands.c:360:                renormalize = 1;
	movi.n	a3, 1	# renormalize,
.L362:
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	addi.n	a6, a6, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:349:          for (k=0;k<1<<LM;k++)
	bne	a4, a6, .L367	#, k,
# @OPUS@\upstream\celt\bands.c:364:          if (renormalize)
	beqz.n	a3, .L361	# renormalize,
# @OPUS@\upstream\celt\bands.c:365:             renormalise_vector(X, N0<<LM, Q15ONE, arch);
	l32r	a4, .LC42	#,
	l32i	a5, sp, 140	# arch,
	l32i.n	a3, sp, 48	# %sfp,
	call0	renormalise_vector		#
.L361:
# @OPUS@\upstream\celt\bands.c:366:       } while (++c<C);
	l32i.n	a6, sp, 4	# %sfp,
	l32i.n	a7, sp, 8	# %sfp,
	addi.n	a6, a6, 1	#,,
	s32i.n	a6, sp, 4	# %sfp,
	l32i.n	a6, sp, 40	# %sfp,
	addi.n	a13, a13, 1	# ivtmp$444, ivtmp$444,
	add.n	a7, a7, a6	#,,
	s32i.n	a7, sp, 8	# %sfp,
	l32i.n	a6, sp, 12	# %sfp,
	l32i.n	a7, sp, 4	# %sfp,
	blt	a7, a6, .L368	#,,
	l32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\celt\bands.c:279:    for (i=start;i<end;i++)
	l32i	a7, sp, 64	# %sfp,
	addi.n	a6, a6, 4	#,,
	s32i	a7, sp, 112	# start,
	s32i.n	a6, sp, 56	# %sfp,
	l32i.n	a7, sp, 60	# %sfp,
	l32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\celt\bands.c:279:    for (i=start;i<end;i++)
	l32i	a2, sp, 112	# start,
	add.n	a7, a7, a6	#,,
	s32i.n	a7, sp, 60	# %sfp,
	l32i	a7, sp, 116	# end,
	bne	a7, a2, .L369	#,,
.L343:
# @OPUS@\upstream\celt\bands.c:368: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	anti_collapse, .-anti_collapse
	.section	.text.spreading_decision,"ax",@progbits
	.literal_position
	.align	4
	.global	spreading_decision
	.type	spreading_decision, @function
# Function: spreading_decision
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Decide whether we should spread the pulses in the current frame */
# C context: int spreading_decision(const CELTMode *m, const celt_norm *X, int *average,
# C context: int last_decision, int *hf_average, int *tapset_decision, int update_hf,
# C context: int end, int C, int M, const int *spread_weight)
# C context: {
# C context: int i, c, N0;
spreading_decision:
# @OPUS@\upstream\celt\bands.c:491:    const opus_int16 * OPUS_RESTRICT eBands = m->eBands;
	l32i.n	a8, a2, 24	# m_118(D)->eBands,
# @OPUS@\upstream\celt\bands.c:488: {
	addi	sp, sp, -112	#,,
# @OPUS@\upstream\celt\bands.c:491:    const opus_int16 * OPUS_RESTRICT eBands = m->eBands;
	s32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	l32i	a8, sp, 116	# end,
# @OPUS@\upstream\celt\bands.c:488: {
	s32i.n	a2, sp, 16	# %sfp, m
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	slli	a2, a8, 1	# _3,,
	l32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\celt\bands.c:488: {
	l32i	a10, sp, 124	# M, M
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	add.n	a2, a8, a2	# tmp154,, _3
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	addi	a8, a2, -2	# tmp159, tmp154,
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	l16si	a9, a2, 0	# *_4, tmp155
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	l16si	a2, a8, 0	# *_10, tmp160
# @OPUS@\upstream\celt\bands.c:488: {
	s32i	a0, sp, 108	#,
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	sub	a2, a9, a2	# tmp163, tmp155, tmp160
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	mull	a9, a2, a10	# tmp164, tmp163, M
# @OPUS@\upstream\celt\bands.c:488: {
	s32i	a12, sp, 104	#,
	s32i	a13, sp, 100	#,
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	movi.n	a8, 8	# tmp165,
# @OPUS@\upstream\celt\bands.c:488: {
	s32i.n	a3, sp, 8	# %sfp, X
	s32i.n	a4, sp, 36	# %sfp, average
	s32i.n	a5, sp, 44	# %sfp, last_decision
	s32i.n	a6, sp, 48	# %sfp, hf_average
	s32i.n	a7, sp, 40	# %sfp, tapset_decision
# @OPUS@\upstream\celt\bands.c:500:       return SPREAD_NONE;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\celt\bands.c:499:    if (M*(eBands[end]-eBands[end-1]) <= 8)
	bge	a8, a9, .L382	# tmp165, tmp164,
# @OPUS@\upstream\celt\bands.c:497:    N0 = M*m->shortMdctSize;
	l32i.n	a4, sp, 16	# %sfp,
	s32i.n	a2, sp, 12	# %sfp, <retval>
	l32i.n	a3, a4, 36	# m_118(D)->shortMdctSize, m_118(D)->shortMdctSize
# @OPUS@\upstream\celt\bands.c:493:    int hf_sum=0;
	s32i.n	a2, sp, 20	# %sfp, <retval>
# @OPUS@\upstream\celt\bands.c:497:    N0 = M*m->shortMdctSize;
	mull	a3, a10, a3	#, M, m_118(D)->shortMdctSize
# @OPUS@\upstream\celt\bands.c:490:    int sum = 0, nbBands=0;
	s32i.n	a2, sp, 4	# %sfp, <retval>
# @OPUS@\upstream\celt\bands.c:497:    N0 = M*m->shortMdctSize;
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\bands.c:490:    int sum = 0, nbBands=0;
	s32i.n	a2, sp, 0	# %sfp, <retval>
# @OPUS@\upstream\celt\bands.c:501:    c=0; do {
	s32i.n	a2, sp, 24	# %sfp, <retval>
# @OPUS@\upstream\celt\bands.c:516:             if (x2N < QCONST16(0.25f,13))
	movi	a6, 0x7ff	# tmp460,
# @OPUS@\upstream\celt\bands.c:518:             if (x2N < QCONST16(0.0625f,13))
	movi	a9, 0x1ff	# tmp461,
# @OPUS@\upstream\celt\bands.c:520:             if (x2N < QCONST16(0.015625f,13))
	movi	a7, 0x7f	# tmp462,
	mov.n	a8, a10	# M, M
.L393:
# @OPUS@\upstream\celt\bands.c:502:       for (i=0;i<end;i++)
	l32i	a5, sp, 116	# end,
	blti	a5, 1, .L384	#,,
	l32i.n	a4, sp, 28	# %sfp, ivtmp$458
# @OPUS@\upstream\celt\bands.c:502:       for (i=0;i<end;i++)
	movi.n	a5, 0	# i,
.L392:
# @OPUS@\upstream\celt\bands.c:506:          const celt_norm * OPUS_RESTRICT x = X+M*eBands[i]+c*N0;
	l16si	a3, a4, 0	# MEM[base: _42, offset: 0B], _19
# @OPUS@\upstream\celt\bands.c:507:          N = M*(eBands[i+1]-eBands[i]);
	l16si	a12, a4, 2	# MEM[base: _42, offset: 2B], tmp169
# @OPUS@\upstream\celt\bands.c:508:          if (N<=8)
	movi.n	a2, 8	#,
# @OPUS@\upstream\celt\bands.c:507:          N = M*(eBands[i+1]-eBands[i]);
	sub	a12, a12, a3	# tmp172, tmp169, _19
# @OPUS@\upstream\celt\bands.c:507:          N = M*(eBands[i+1]-eBands[i]);
	mull	a12, a12, a8	# N, tmp172, M
# @OPUS@\upstream\celt\bands.c:508:          if (N<=8)
	bge	a2, a12, .L385	#, N,
# @OPUS@\upstream\celt\bands.c:506:          const celt_norm * OPUS_RESTRICT x = X+M*eBands[i]+c*N0;
	l32i.n	a2, sp, 12	# %sfp,
# @OPUS@\upstream\celt\bands.c:506:          const celt_norm * OPUS_RESTRICT x = X+M*eBands[i]+c*N0;
	mull	a3, a3, a8	# tmp174, _19, M
# @OPUS@\upstream\celt\bands.c:505:          int tcount[3] = {0,0,0};
	movi.n	a13, 0	# tcount$2,
# @OPUS@\upstream\celt\bands.c:506:          const celt_norm * OPUS_RESTRICT x = X+M*eBands[i]+c*N0;
	add.n	a3, a3, a2	# _24, tmp174,
	add.n	a10, a3, a12	# tmp177, _24, N
	l32i.n	a2, sp, 8	# %sfp,
	slli	a11, a12, 16	# tmp175, N,
	slli	a3, a3, 1	# tmp176, _24,
	slli	a10, a10, 1	# tmp178, tmp177,
	srai	a11, a11, 16	# _307, tmp175,
	add.n	a3, a2, a3	# ivtmp$455,, tmp176
	add.n	a10, a2, a10	# _38,, tmp178
# @OPUS@\upstream\celt\bands.c:505:          int tcount[3] = {0,0,0};
	mov.n	a15, a13	# tcount$1, tcount$2
	mov.n	a14, a13	# tcount$0, tcount$2
.L387:
# @OPUS@\upstream\celt\bands.c:515:             x2N = MULT16_16(MULT16_16_Q15(x[j], x[j]), N);
	l16si	a2, a3, 0	# MEM[base: _35, offset: 0B], _337
	addi.n	a3, a3, 2	# ivtmp$455, ivtmp$455,
	mull	a2, a2, a2	# tmp181, _337, _337
	srai	a2, a2, 15	# tmp182, tmp181,
# @OPUS@\upstream\celt\bands.c:515:             x2N = MULT16_16(MULT16_16_Q15(x[j], x[j]), N);
	mul16s	a2, a2, a11	# x2N, tmp182, _307
# @OPUS@\upstream\celt\bands.c:516:             if (x2N < QCONST16(0.25f,13))
	blt	a6, a2, .L386	# tmp460, x2N,
# @OPUS@\upstream\celt\bands.c:517:                tcount[0]++;
	addi.n	a14, a14, 1	# tcount$0, tcount$0,
# @OPUS@\upstream\celt\bands.c:518:             if (x2N < QCONST16(0.0625f,13))
	blt	a9, a2, .L386	# tmp461, x2N,
# @OPUS@\upstream\celt\bands.c:519:                tcount[1]++;
	addi.n	a15, a15, 1	# tcount$1, tcount$1,
# @OPUS@\upstream\celt\bands.c:520:             if (x2N < QCONST16(0.015625f,13))
	blt	a7, a2, .L386	# tmp462, x2N,
# @OPUS@\upstream\celt\bands.c:521:                tcount[2]++;
	addi.n	a13, a13, 1	# tcount$2, tcount$2,
.L386:
# @OPUS@\upstream\celt\bands.c:511:          for (j=0;j<N;j++)
	bne	a10, a3, .L387	# _38, ivtmp$455,
# @OPUS@\upstream\celt\bands.c:525:          if (i>m->nbEBands-4)
	l32i.n	a3, sp, 16	# %sfp,
	l32i.n	a2, a3, 8	# m_118(D)->nbEBands, m_118(D)->nbEBands
	addi	a2, a2, -4	# tmp186, m_118(D)->nbEBands,
# @OPUS@\upstream\celt\bands.c:525:          if (i>m->nbEBands-4)
	bge	a2, a5, .L388	# tmp186, i,
# @OPUS@\upstream\celt\bands.c:526:             hf_sum += celt_udiv(32*(tcount[1]+tcount[0]), N);
	add.n	a2, a15, a14	# tmp188, tcount$1, tcount$0
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a12	#, N
	slli	a2, a2, 5	#, tmp188,
	s32i	a4, sp, 64	#,
	s32i	a5, sp, 68	#,
	s32i.n	a6, sp, 52	#,
	s32i.n	a7, sp, 60	#,
	s32i	a8, sp, 72	#,
	s32i.n	a9, sp, 56	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:526:             hf_sum += celt_udiv(32*(tcount[1]+tcount[0]), N);
	l32i.n	a3, sp, 20	# %sfp,
	l32i.n	a9, sp, 56	#,
	add.n	a3, a2, a3	#,,
	l32i	a8, sp, 72	#,
	l32i.n	a7, sp, 60	#,
	l32i.n	a6, sp, 52	#,
	l32i	a5, sp, 68	#,
	l32i	a4, sp, 64	#,
	s32i.n	a3, sp, 20	# %sfp,
.L388:
# @OPUS@\upstream\celt\bands.c:528:          sum += tmp*spread_weight[i];
	l32i	a3, sp, 128	# spread_weight,
	slli	a2, a5, 2	# tmp194, i,
	add.n	a2, a3, a2	# tmp195,, tmp194
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	slli	a13, a13, 1	# tmp196, tcount$2,
# @OPUS@\upstream\celt\bands.c:528:          sum += tmp*spread_weight[i];
	l32i.n	a3, a2, 0	# MEM[base: _46, offset: 0B], _68
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	movi.n	a2, 1	# tmp197,
	bge	a13, a12, .L389	# tmp196, N,
	movi.n	a2, 0	# tmp197,
.L389:
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	slli	a15, a15, 1	# tmp199, tcount$1,
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	movi.n	a10, 1	# tmp200,
	bge	a15, a12, .L390	# tmp199, N,
	movi.n	a10, 0	# tmp200,
.L390:
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	slli	a14, a14, 1	# tmp203, tcount$0,
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	add.n	a2, a2, a10	# tmp202, tmp197, tmp200
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	movi.n	a10, 1	# tmp204,
	bge	a14, a12, .L391	# tmp203, N,
	movi.n	a10, 0	# tmp204,
.L391:
# @OPUS@\upstream\celt\bands.c:527:          tmp = (2*tcount[2] >= N) + (2*tcount[1] >= N) + (2*tcount[0] >= N);
	add.n	a10, a2, a10	# tmp, tmp202, tmp204
# @OPUS@\upstream\celt\bands.c:529:          nbBands+=spread_weight[i];
	l32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:528:          sum += tmp*spread_weight[i];
	mull	a10, a10, a3	# tmp207, tmp, _68
# @OPUS@\upstream\celt\bands.c:529:          nbBands+=spread_weight[i];
	add.n	a2, a2, a3	#,, _68
# @OPUS@\upstream\celt\bands.c:528:          sum += tmp*spread_weight[i];
	l32i.n	a3, sp, 0	# %sfp,
# @OPUS@\upstream\celt\bands.c:529:          nbBands+=spread_weight[i];
	s32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\bands.c:528:          sum += tmp*spread_weight[i];
	add.n	a3, a3, a10	#,, tmp207
	s32i.n	a3, sp, 0	# %sfp,
.L385:
# @OPUS@\upstream\celt\bands.c:502:       for (i=0;i<end;i++)
	l32i	a2, sp, 116	# end,
# @OPUS@\upstream\celt\bands.c:502:       for (i=0;i<end;i++)
	addi.n	a5, a5, 1	# i, i,
	addi.n	a4, a4, 2	# ivtmp$458, ivtmp$458,
# @OPUS@\upstream\celt\bands.c:502:       for (i=0;i<end;i++)
	bne	a2, a5, .L392	#, i,
.L384:
# @OPUS@\upstream\celt\bands.c:531:    } while (++c<C);
	l32i.n	a4, sp, 24	# %sfp,
	l32i.n	a5, sp, 12	# %sfp,
	addi.n	a4, a4, 1	#,,
	s32i.n	a4, sp, 24	# %sfp,
	l32i.n	a4, sp, 32	# %sfp,
	add.n	a5, a5, a4	#,,
	s32i.n	a5, sp, 12	# %sfp,
	l32i	a4, sp, 120	# C,
	l32i.n	a5, sp, 24	# %sfp,
	blt	a5, a4, .L393	#,,
# @OPUS@\upstream\celt\bands.c:533:    if (update_hf)
	l32i	a5, sp, 112	# update_hf,
	beqz.n	a5, .L394	#,
# @OPUS@\upstream\celt\bands.c:535:       if (hf_sum)
	l32i.n	a8, sp, 20	# %sfp,
	beqz.n	a8, .L395	#,
# @OPUS@\upstream\celt\bands.c:536:          hf_sum = celt_udiv(hf_sum, C*(4-m->nbEBands+end));
	l32i.n	a8, sp, 16	# %sfp,
	l32i.n	a2, a8, 8	# m_118(D)->nbEBands, m_118(D)->nbEBands
	l32i	a8, sp, 116	# end,
	addi.n	a3, a8, 4	# tmp208,,
	sub	a3, a3, a2	# tmp209, tmp208, m_118(D)->nbEBands
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mull	a3, a3, a4	#, tmp209,
	l32i.n	a2, sp, 20	# %sfp,
	call0	__udivsi3		#
	s32i.n	a2, sp, 20	# %sfp,
.L395:
# @OPUS@\upstream\celt\bands.c:537:       *hf_average = (*hf_average+hf_sum)>>1;
	l32i.n	a4, sp, 48	# %sfp,
	l32i.n	a5, sp, 20	# %sfp,
	l32i.n	a2, a4, 0	# *hf_average_142(D), *hf_average_142(D)
# @OPUS@\upstream\celt\bands.c:539:       if (*tapset_decision==2)
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\celt\bands.c:537:       *hf_average = (*hf_average+hf_sum)>>1;
	add.n	a2, a5, a2	# tmp215,, *hf_average_142(D)
# @OPUS@\upstream\celt\bands.c:537:       *hf_average = (*hf_average+hf_sum)>>1;
	srai	a2, a2, 1	# _79, tmp215,
# @OPUS@\upstream\celt\bands.c:537:       *hf_average = (*hf_average+hf_sum)>>1;
	s32i.n	a2, a4, 0	# *hf_average_142(D), _79
# @OPUS@\upstream\celt\bands.c:539:       if (*tapset_decision==2)
	l32i.n	a3, a8, 0	# *tapset_decision_145(D), _80
# @OPUS@\upstream\celt\bands.c:539:       if (*tapset_decision==2)
	bnei	a3, 2, .L396	# _80,,
# @OPUS@\upstream\celt\bands.c:540:          hf_sum += 4;
	addi.n	a2, a2, 4	# _79, _79,
	j	.L397		#
.L396:
# @OPUS@\upstream\celt\bands.c:542:          hf_sum -= 4;
	addi	a4, a2, -4	# tmp295, _79,
	moveqz	a2, a4, a3	# _79, tmp295, _80
.L397:
# @OPUS@\upstream\celt\bands.c:543:       if (hf_sum > 22)
	movi.n	a3, 0x16	# tmp217,
	bge	a3, a2, .L398	# tmp217, _79,
# @OPUS@\upstream\celt\bands.c:544:          *tapset_decision=2;
	l32i.n	a4, sp, 40	# %sfp,
	movi.n	a2, 2	# tmp218,
	s32i.n	a2, a4, 0	# *tapset_decision_145(D), tmp218
	j	.L394		#
.L398:
# @OPUS@\upstream\celt\bands.c:545:       else if (hf_sum > 18)
	movi.n	a3, 0x12	# tmp219,
	bge	a3, a2, .L399	# tmp219, _79,
# @OPUS@\upstream\celt\bands.c:546:          *tapset_decision=1;
	l32i.n	a5, sp, 40	# %sfp,
	movi.n	a2, 1	# tmp220,
	s32i.n	a2, a5, 0	# *tapset_decision_145(D), tmp220
	j	.L394		#
.L399:
# @OPUS@\upstream\celt\bands.c:548:          *tapset_decision=0;
	l32i.n	a8, sp, 40	# %sfp,
	movi.n	a2, 0	# tmp221,
	s32i.n	a2, a8, 0	# *tapset_decision_145(D), tmp221
.L394:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a4, sp, 0	# %sfp,
	l32i.n	a3, sp, 4	# %sfp,
	slli	a2, a4, 8	#,,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:555:    sum = (sum+*average)>>1;
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	l32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\bands.c:555:    sum = (sum+*average)>>1;
	l32i.n	a3, a8, 0	# *average_153(D), *average_153(D)
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	movi.n	a4, 3	# tmp227,
# @OPUS@\upstream\celt\bands.c:555:    sum = (sum+*average)>>1;
	add.n	a2, a2, a3	# _87,, *average_153(D)
# @OPUS@\upstream\celt\bands.c:555:    sum = (sum+*average)>>1;
	srai	a2, a2, 1	# sum, _87,
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	sub	a3, a4, a5	# tmp228, tmp227,
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	slli	a3, a3, 7	# tmp229, tmp228,
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	slli	a5, a2, 1	# tmp232, sum,
	add.n	a5, a5, a2	# tmp233, tmp232, sum
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	addi	a3, a3, 66	# tmp230, tmp229,
	add.n	a3, a3, a5	# _92, tmp230, tmp233
# @OPUS@\upstream\celt\bands.c:556:    *average = sum;
	s32i.n	a2, a8, 0	# *average_153(D), sum
# @OPUS@\upstream\celt\bands.c:558:    sum = (3*sum + (((3-last_decision)<<7) + 64) + 2)>>2;
	srai	a3, a3, 2	# sum, _92,
# @OPUS@\upstream\celt\bands.c:559:    if (sum < 80)
	movi.n	a5, 0x4f	# tmp234,
# @OPUS@\upstream\celt\bands.c:561:       decision = SPREAD_AGGRESSIVE;
	mov.n	a2, a4	# <retval>, tmp227
# @OPUS@\upstream\celt\bands.c:559:    if (sum < 80)
	bge	a5, a3, .L382	# tmp234, sum,
# @OPUS@\upstream\celt\bands.c:562:    } else if (sum < 256)
	movi	a4, 0xff	# tmp235,
# @OPUS@\upstream\celt\bands.c:564:       decision = SPREAD_NORMAL;
	movi.n	a2, 2	# <retval>,
# @OPUS@\upstream\celt\bands.c:562:    } else if (sum < 256)
	bge	a4, a3, .L382	# tmp235, sum,
# @OPUS@\upstream\celt\bands.c:565:    } else if (sum < 384)
	movi	a4, 0x17f	# tmp238,
	movi.n	a2, 1	# tmp236,
	bge	a4, a3, .L382	# tmp238, sum,
	movi.n	a2, 0	# tmp236,
.L382:
# @OPUS@\upstream\celt\bands.c:576: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	spreading_decision, .-spreading_decision
	.section	.text.haar1,"ax",@progbits
	.literal_position
	.literal .LC48, 23170
	.align	4
	.global	haar1
	.type	haar1, @function
# Function: haar1
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: RESTORE_STACK;
# C context: }
# C context:
# C context: void haar1(celt_norm *X, int N0, int stride)
# C context: {
# C context: int i, j;
# C context: N0 >>= 1;
# C context: for (i=0;i<stride;i++)
haar1:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	srai	a3, a3, 1	# N0, N0,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a4, 1, .L413	# stride,,
	blti	a3, 1, .L413	# N0,,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l32r	a10, .LC48	#, tmp77
	slli	a12, a4, 1	# _89, stride,
	add.n	a13, a2, a12	# _87, ivtmp$472, _89
	slli	a9, a4, 2	# _118, stride,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mov.n	a11, a10	# tmp78, tmp77
	j	.L416		#
.L417:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a5, a6, 0	# MEM[base: _97, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a4, a7, 0	# MEM[base: _95, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a5, a5, a11	# tmp1, MEM[base: _97, offset: 0B], tmp78
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a14, a4, a10	# tmp2, MEM[base: _95, offset: 0B], tmp77
	addmi	a4, a5, 0x4000	# _29, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a5, a4, a14	# tmp73, _29, tmp2
	srai	a5, a5, 15	# tmp74, tmp73,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a4, a4, a14	# tmp75, _29, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a5, a6, 0	# MEM[base: _97, offset: 0B], tmp74
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a4, a4, 15	# tmp76, tmp75,
	s16i	a4, a7, 0	# MEM[base: _95, offset: 0B], tmp76
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a8, a8, 1	# j, j,
	add.n	a6, a6, a9	# ivtmp$467, ivtmp$467, _118
	add.n	a7, a7, a9	# ivtmp$468, ivtmp$468, _118
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a3, a8, .L417	# N0, j,
	addi.n	a2, a2, 2	# ivtmp$472, ivtmp$472,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a13, a2, .L413	# _87, ivtmp$472,
.L416:
	add.n	a7, a12, a2	# ivtmp$468, _89, ivtmp$472
# @OPUS@\upstream\celt\bands.c:639: {
	mov.n	a6, a2	# ivtmp$467, ivtmp$472
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a8, 0	# j,
	j	.L417		#
.L413:
# @OPUS@\upstream\celt\bands.c:651: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	haar1, .-haar1
	.section	.text.quant_all_bands,"ax",@progbits
	.literal_position
	.literal .LC49, 16384
	.literal .LC50, -16384
	.literal .LC51, 32767
	.literal .LC52, 2147483647
	.literal .LC53, 16383
	.literal .LC54, exp2_table8$4166
	.literal .LC55, 8192
	.literal .LC56, -32767
	.literal .LC57, 23170
	.literal .LC58, 8277
	.literal .LC59, -7651
	.literal .LC60, -32768
	.literal .LC61, -2597
	.literal .LC62, 7932
	.literal .LC63, -16385
	.literal .LC64, bit_interleave_table$4327
	.literal .LC65, 1664525
	.literal .LC66, 1013904223
	.literal .LC67, 32768
	.literal .LC68, 1073741822
	.literal .LC69, ordery_table
	.literal .LC70, bit_deinterleave_table$4337
	.literal .LC71, 8388608
	.literal .LC72, 161060
	.align	4
	.global	quant_all_bands
	.type	quant_all_bands, @function
# Function: quant_all_bands
# Module: upstream/celt/bands.c
# CELT spectral-band decoding, allocation and recursive pulse vector processing.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: void quant_all_bands(int encode, const CELTMode *m, int start, int end,
# C context: celt_norm *X_, celt_norm *Y_, unsigned char *collapse_masks,
# C context: const celt_ener *bandE, int *pulses, int shortBlocks, int spread,
# C context: int dual_stereo, int intensity, int *tf_res, opus_int32 total_bits,
# C context: opus_int32 balance, ec_ctx *ec, int LM, int codedBands,
quant_all_bands:
	movi	a9, 0x180	#,
	sub	sp, sp, a9	#,,
	movi.n	a8, 0	# tmp1560,
# @OPUS@\upstream\celt\bands.c:1437:    const opus_int16 * OPUS_RESTRICT eBands = m->eBands;
	l32i.n	a9, a3, 24	# m_265(D)->eBands,
# @OPUS@\upstream\celt\bands.c:1426: {
	s32i	a13, sp, 372	#,
	s32i	a14, sp, 368	#,
	mov.n	a13, a2	# encode, encode
	movi.n	a14, 1	# tmp1559,
	mov.n	a2, a8	# tmp1558, tmp1560
	moveqz	a2, a14, a13	# tmp1558, tmp1559, encode
	s32i	a4, sp, 224	# %sfp, start
	s32i	a0, sp, 380	#,
	s32i	a12, sp, 376	#,
	s32i	a15, sp, 364	#,
# @OPUS@\upstream\celt\bands.c:1426: {
	s32i	a3, sp, 232	# %sfp, m
	s32i	a7, sp, 176	# %sfp, Y_
	s32i	a5, sp, 244	# %sfp, end
	s32i	a6, sp, 292	# %sfp, X_
# @OPUS@\upstream\celt\bands.c:1437:    const opus_int16 * OPUS_RESTRICT eBands = m->eBands;
	s32i	a9, sp, 280	# %sfp,
	extui	a4, a2, 0, 8	# prephitmp_4238, tmp1558
# @OPUS@\upstream\celt\bands.c:1452:    int C = Y_ != NULL ? 2 : 1;
	beq	a7, a8, .L421	# Y_,,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	beq	a13, a8, .L700	# encode,,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	l32i	a10, sp, 404	# dual_stereo,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	l32i	a11, sp, 440	# complexity,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	mov.n	a2, a8	# tmp1562, tmp1560
	moveqz	a2, a14, a10	# tmp1562, tmp1559,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	bgei	a11, 8, .L423	#,,
	mov.n	a14, a8	# tmp1565, tmp1560
.L423:
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	and	a14, a2, a14	# iftmp$66_247, tmp1562, tmp1565
	or	a12, a14, a4	#, iftmp$66_247, prephitmp_4238
# @OPUS@\upstream\celt\bands.c:1452:    int C = Y_ != NULL ? 2 : 1;
	movi.n	a8, 2	#,
	s32i	a12, sp, 220	# %sfp,
	s32i	a8, sp, 204	# %sfp,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	movi.n	a12, 1	# _601,
	j	.L422		#
.L700:
# @OPUS@\upstream\celt\bands.c:1452:    int C = Y_ != NULL ? 2 : 1;
	movi.n	a9, 2	#,
	s32i	a4, sp, 220	# %sfp, prephitmp_4238
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	mov.n	a14, a13	# iftmp$66_247, encode
# @OPUS@\upstream\celt\bands.c:1452:    int C = Y_ != NULL ? 2 : 1;
	s32i	a9, sp, 204	# %sfp,
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	mov.n	a12, a13	# _601, encode
.L422:
# @OPUS@\upstream\celt\bands.c:1461:    SAVE_STACK;
	s32i	a4, sp, 348	#,
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\celt\bands.c:1464:    B = shortBlocks ? M : 1;
	l32i	a10, sp, 396	# shortBlocks,
# @OPUS@\upstream\celt\bands.c:1461:    SAVE_STACK;
	s32i	a2, sp, 100	# _saved_stack,
	s32i	a3, sp, 104	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:1464:    B = shortBlocks ? M : 1;
	l32i	a4, sp, 348	#,
	beqz.n	a10, .L701	#,
# @OPUS@\upstream\celt\bands.c:1463:    M = 1<<LM;
	l32i	a11, sp, 428	# LM,
	movi.n	a2, 1	# tmp1570,
	ssl	a11	#
	sll	a11, a2	#, tmp1570
	s32i	a11, sp, 180	# %sfp,
	bgei	a11, 2, .L425	#,,
	movi.n	a2, 0	# tmp1571,
.L425:
	extui	a2, a2, 0, 8	#, tmp1571
	s32i	a2, sp, 296	# %sfp,
	s32i	a2, sp, 396	# shortBlocks,
	j	.L424		#
.L701:
# @OPUS@\upstream\celt\bands.c:1464:    B = shortBlocks ? M : 1;
	movi.n	a8, 1	#,
	s32i	a10, sp, 296	# %sfp, tmp5
	s32i	a8, sp, 180	# %sfp,
.L424:
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	l32i	a9, sp, 232	# %sfp,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	l32i	a10, sp, 224	# %sfp,
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	l32i.n	a2, a9, 8	# m_265(D)->nbEBands, m_265(D)->nbEBands
	l32r	a11, .LC52	#,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	l32i	a8, sp, 280	# %sfp,
	slli	a10, a10, 1	#,,
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	add.n	a2, a2, a11	# tmp1576, m_265(D)->nbEBands,
	l32i	a9, sp, 280	# %sfp,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	add.n	a8, a8, a10	#,,
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	slli	a2, a2, 1	# tmp1579, tmp1576,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	s32i	a10, sp, 308	# %sfp,
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	add.n	a2, a9, a2	# tmp1580,, tmp1579
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	l32i	a10, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	l16si	a3, a8, 0	# *_12, tmp1573
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	l16si	a5, a2, 0	# *_19, tmp1581
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	ssl	a10	#
	sll	a3, a3	#, tmp1573
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	ssl	a10	#
	sll	a5, a5	# tmp1584, tmp1581
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	s32i	a8, sp, 288	# %sfp,
# @OPUS@\upstream\celt\bands.c:1465:    norm_offset = M*eBands[start];
	s32i	a3, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1470:       int norm_size = M*eBands[m->nbEBands-1]-norm_offset;
	sub	a15, a5, a3	# norm_size, tmp1584,
# @OPUS@\upstream\celt\bands.c:1472:                          norm_size > 0 && norm2_scratch_size >= norm_size;
	beqz.n	a4, .L702	# prephitmp_4238,
# @OPUS@\upstream\celt\bands.c:1472:                          norm_size > 0 && norm2_scratch_size >= norm_size;
	srai	a2, a15, 31	# tmp1587, norm_size,
# @OPUS@\upstream\celt\bands.c:1472:                          norm_size > 0 && norm2_scratch_size >= norm_size;
	l32i	a11, sp, 456	# norm2_scratch_size,
# @OPUS@\upstream\celt\bands.c:1472:                          norm_size > 0 && norm2_scratch_size >= norm_size;
	sub	a2, a2, a15	# tmp1588, tmp1587, norm_size
	extui	a2, a2, 31, 1	# tmp1589, tmp1588,
# @OPUS@\upstream\celt\bands.c:1472:                          norm_size > 0 && norm2_scratch_size >= norm_size;
	movi.n	a3, 1	# tmp1590,
	bge	a11, a15, .L429	#, norm_size,
	movi.n	a3, 0	# tmp1590,
.L429:
	bnone	a2, a3, .L745	# tmp1589, tmp1590,
	l32i	a8, sp, 452	# norm2_scratch,
	bnez.n	a8, .L427	#,
.L745:
	movi.n	a2, 2	# iftmp$70_2697,
	j	.L426		#
.L702:
	l32i	a2, sp, 204	# %sfp, iftmp$70_2697
.L426:
# @OPUS@\upstream\celt\bands.c:1475:       ALLOC(_norm, (borrow_norm2 ? 1 : C)*norm_size, celt_norm);
	mull	a2, a15, a2	#, norm_size, iftmp$70_2697
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1477:       norm2 = borrow_norm2 ? norm2_scratch : norm + norm_size;
	slli	a5, a15, 1	# tmp1601, norm_size,
# @OPUS@\upstream\celt\bands.c:1477:       norm2 = borrow_norm2 ? norm2_scratch : norm + norm_size;
	add.n	a5, a2, a5	#,, tmp1601
# @OPUS@\upstream\celt\bands.c:1475:       ALLOC(_norm, (borrow_norm2 ? 1 : C)*norm_size, celt_norm);
	s32i	a2, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1477:       norm2 = borrow_norm2 ? norm2_scratch : norm + norm_size;
	s32i	a5, sp, 452	# norm2_scratch,
# @OPUS@\upstream\celt\bands.c:1488:    if (encode && resynth)
	beqz.n	a12, .L432	# _601,
	l32i	a9, sp, 220	# %sfp,
	bnez.n	a9, .L430	#,
	j	.L432		#
.L427:
# @OPUS@\upstream\celt\bands.c:1475:       ALLOC(_norm, (borrow_norm2 ? 1 : C)*norm_size, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a15	#, norm_size
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 184	# %sfp,
.L432:
# @OPUS@\upstream\celt\bands.c:1492:    ALLOC(_lowband_scratch, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	l32i	a10, sp, 232	# %sfp,
	l32r	a11, .LC52	#,
	l32i.n	a2, a10, 12	# m_265(D)->effEBands, m_265(D)->effEBands
	l32i	a8, sp, 280	# %sfp,
	add.n	a2, a2, a11	# tmp1602, m_265(D)->effEBands,
	slli	a2, a2, 1	# tmp1605, tmp1602,
	add.n	a2, a8, a2	# tmp1606,, tmp1605
	l16si	a2, a2, 0	# *_51, tmp1607
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	l32i	a9, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	l32i	a10, sp, 292	# %sfp,
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	ssl	a9	#
	sll	a2, a2	# tmp1610, tmp1607
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	slli	a2, a2, 1	# tmp1611, tmp1610,
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	add.n	a2, a10, a2	#,, tmp1611
# @OPUS@\upstream\celt\bands.c:1492:    ALLOC(_lowband_scratch, resynth_alloc, celt_norm);
	movi.n	a12, 0	# resynth_alloc$73_605,
# @OPUS@\upstream\celt\bands.c:1496:       lowband_scratch = X_+M*eBands[m->effEBands-1];
	s32i	a2, sp, 168	# %sfp,
	j	.L433		#
.L430:
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	l32i	a11, sp, 232	# %sfp,
	l32i	a12, sp, 280	# %sfp,
	l32i.n	a2, a11, 8	# m_265(D)->nbEBands, m_265(D)->nbEBands
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	l32i	a8, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	slli	a2, a2, 1	# _36, m_265(D)->nbEBands,
	add.n	a2, a12, a2	# tmp1613,, _36
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	addi	a3, a2, -2	# tmp1618, tmp1613,
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	l16si	a12, a2, 0	# *_37, tmp1614
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	l16si	a2, a3, 0	# *_42, tmp1619
# @OPUS@\upstream\celt\bands.c:1492:    ALLOC(_lowband_scratch, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	sub	a12, a12, a2	# tmp1622, tmp1614, tmp1619
# @OPUS@\upstream\celt\bands.c:1489:       resynth_alloc = M*(eBands[m->nbEBands]-eBands[m->nbEBands-1]);
	ssl	a8	#
	sll	a12, a12	# resynth_alloc$73_605, tmp1622
# @OPUS@\upstream\celt\bands.c:1492:    ALLOC(_lowband_scratch, resynth_alloc, celt_norm);
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 168	# %sfp,
.L433:
# @OPUS@\upstream\celt\bands.c:1497:    ALLOC(X_save, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1498:    ALLOC(Y_save, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1499:    ALLOC(X_save2, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1500:    ALLOC(Y_save2, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1501:    ALLOC(norm_save2, resynth_alloc, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a12	#, resynth_alloc$73_605
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:1504:    ctx.bandE = bandE;
	l32i	a3, sp, 388	# bandE, bandE
# @OPUS@\upstream\celt\bands.c:1509:    ctx.seed = *seed;
	l32i	a9, sp, 436	# seed,
# @OPUS@\upstream\celt\bands.c:1504:    ctx.bandE = bandE;
	s32i	a3, sp, 68	# ctx.bandE, bandE
# @OPUS@\upstream\celt\bands.c:1511:    ctx.arch = arch;
	l32i	a3, sp, 444	# arch, arch
# @OPUS@\upstream\celt\bands.c:1505:    ctx.ec = ec;
	l32i	a10, sp, 424	# ec,
# @OPUS@\upstream\celt\bands.c:1507:    ctx.intensity = intensity;
	l32i	a11, sp, 408	# intensity,
# @OPUS@\upstream\celt\bands.c:1509:    ctx.seed = *seed;
	l32i.n	a4, a9, 0	# *seed_309(D), pretmp_5341
# @OPUS@\upstream\celt\bands.c:1508:    ctx.m = m;
	l32i	a12, sp, 232	# %sfp,
# @OPUS@\upstream\celt\bands.c:1510:    ctx.spread = spread;
	l32i	a5, sp, 400	# spread,
# @OPUS@\upstream\celt\bands.c:1511:    ctx.arch = arch;
	s32i	a3, sp, 76	# ctx.arch, arch
# @OPUS@\upstream\celt\bands.c:1513:    ctx.resynth = resynth;
	l32i	a8, sp, 220	# %sfp,
# @OPUS@\upstream\celt\bands.c:1512:    ctx.disable_inv = disable_inv;
	l32i	a3, sp, 448	# disable_inv, disable_inv
# @OPUS@\upstream\celt\bands.c:1516:    ctx.avoid_split_noise = B > 1;
	l32i	a9, sp, 396	# shortBlocks,
# @OPUS@\upstream\celt\bands.c:1514:    ctx.theta_round = 0;
	movi.n	a2, 0	# tmp1623,
# @OPUS@\upstream\celt\bands.c:1505:    ctx.ec = ec;
	s32i.n	a10, sp, 60	# ctx.ec,
# @OPUS@\upstream\celt\bands.c:1507:    ctx.intensity = intensity;
	s32i.n	a11, sp, 48	# ctx.intensity,
# @OPUS@\upstream\celt\bands.c:1517:    for (i=start;i<end;i++)
	l32i	a10, sp, 224	# %sfp,
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\bands.c:1506:    ctx.encode = encode;
	s32i.n	a13, sp, 32	# ctx.encode, encode
# @OPUS@\upstream\celt\bands.c:1508:    ctx.m = m;
	s32i.n	a12, sp, 40	# ctx.m,
# @OPUS@\upstream\celt\bands.c:1509:    ctx.seed = *seed;
	s32i	a4, sp, 72	# ctx.seed, pretmp_5341
# @OPUS@\upstream\celt\bands.c:1510:    ctx.spread = spread;
	s32i.n	a5, sp, 52	# ctx.spread,
# @OPUS@\upstream\celt\bands.c:1512:    ctx.disable_inv = disable_inv;
	s32i	a3, sp, 84	# ctx.disable_inv, disable_inv
# @OPUS@\upstream\celt\bands.c:1513:    ctx.resynth = resynth;
	s32i.n	a8, sp, 36	# ctx.resynth,
# @OPUS@\upstream\celt\bands.c:1514:    ctx.theta_round = 0;
	s32i	a2, sp, 80	# ctx.theta_round, tmp1623
# @OPUS@\upstream\celt\bands.c:1516:    ctx.avoid_split_noise = B > 1;
	s32i	a9, sp, 88	# ctx.avoid_split_noise,
# @OPUS@\upstream\celt\bands.c:1517:    for (i=start;i<end;i++)
	bge	a10, a11, .L434	#,,
# @OPUS@\upstream\celt\bands.c:1603:          x_cm = y_cm = (1<<B)-1;
	l32i	a8, sp, 180	# %sfp,
	movi.n	a4, 1	# tmp1624,
	l32i	a12, sp, 204	# %sfp,
	ssl	a8	#
	sll	a3, a4	# tmp1625, tmp1624
	mull	a12, a10, a12	#,,
	l32i	a9, sp, 204	# %sfp,
# @OPUS@\upstream\celt\bands.c:1603:          x_cm = y_cm = (1<<B)-1;
	addi.n	a3, a3, -1	#, tmp1625,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	l32i	a11, sp, 308	# %sfp,
# @OPUS@\upstream\celt\bands.c:1603:          x_cm = y_cm = (1<<B)-1;
	s32i	a3, sp, 208	# %sfp,
	s32i	a12, sp, 248	# %sfp,
	add.n	a6, a9, a12	# _4568,,
	mov.n	a15, a10	# i,
	slli	a3, a10, 2	# tmp1630,,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	addi.n	a11, a11, 2	#,,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	l32i	a10, sp, 180	# %sfp,
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	l32i	a12, sp, 308	# %sfp,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	l32i	a9, sp, 208	# %sfp,
# @OPUS@\upstream\celt\bands.c:1503:    lowband_offset = 0;
	s32i	a2, sp, 192	# %sfp, tmp1623
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	s32i	a11, sp, 328	# %sfp,
	addi.n	a2, a8, -1	# tmp3025,,
	l32i	a11, sp, 244	# %sfp,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l32i	a8, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1451:    int update_lowband = 1;
	mov.n	a7, a4	# update_lowband, tmp1624
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	ssl	a10	#
	sll	a9, a9	#,
	xor	a4, a14, a4	#, iftmp$66_247, tmp1624
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	addi.n	a12, a12, 4	#,,
	s32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	slli	a8, a8, 3	#,,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	s32i	a9, sp, 336	# %sfp,
	addi.n	a11, a11, -1	#,,
	l32i	a12, sp, 432	# codedBands,
	s32i	a4, sp, 284	# %sfp,
	l32i	a14, sp, 224	# %sfp,
	l32i	a9, sp, 384	# collapse_masks,
	l32i	a10, sp, 248	# %sfp,
	l32i	a4, sp, 392	# pulses, pulses
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	s32i	a8, sp, 320	# %sfp,
	s32i	a11, sp, 200	# %sfp,
	l32i	a8, sp, 288	# %sfp,
# @OPUS@\upstream\celt\bands.c:1570:          if (Y_!=NULL)
	l32i	a11, sp, 184	# %sfp,
	addi.n	a12, a12, -1	#,,
	add.n	a14, a14, a7	#,,
	add.n	a9, a9, a10	#,,
	add.n	a3, a4, a3	#, pulses, tmp1630
	addi.n	a6, a6, -1	#, _4568,
	s32i	a14, sp, 260	# %sfp,
	s32i	a12, sp, 264	# %sfp,
	s32i	a8, sp, 144	# %sfp,
	s32i	a9, sp, 156	# %sfp,
	s32i	a3, sp, 164	# %sfp,
	s32i	a6, sp, 268	# %sfp,
	s32i	a11, sp, 300	# %sfp,
# @OPUS@\upstream\celt\bands.c:1579:       if (lowband_offset != 0 && (spread!=SPREAD_AGGRESSIVE || B>1 || tf_change<0))
	l32i	a12, sp, 192	# %sfp,
	l32i	a14, sp, 192	# %sfp,
	addi	a5, a5, -3	# tmp3023, tmp10,
	moveqz	a14, a7, a2	#, update_lowband, tmp3025
	movnez	a12, a7, a5	#, update_lowband, tmp3023
	s32i	a14, sp, 324	# %sfp,
	s32i	a12, sp, 304	# %sfp,
	mov.n	a14, a7	# update_lowband, update_lowband
	s32i	a15, sp, 116	# %sfp, i
.L670:
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	l32i	a10, sp, 116	# %sfp,
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	l16si	a2, a8, 0	# MEM[base: _4590, offset: 0B], _66
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	l32i	a9, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	l32i	a11, sp, 200	# %sfp,
# @OPUS@\upstream\celt\bands.c:1538:       N = M*eBands[i+1]-M*eBands[i];
	l16si	a3, a8, 2	# MEM[base: _4590, offset: 2B], tmp1639
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	sub	a12, a10, a11	# tmp1633,,
# @OPUS@\upstream\celt\bands.c:1535:          Y = Y_+M*eBands[i];
	l32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	ssl	a9	#
	sll	a13, a2	# tmp1638, _66
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	movi.n	a5, 1	#,
	movi.n	a4, 0	#,
	moveqz	a4, a5, a12	#,, tmp1633
# @OPUS@\upstream\celt\bands.c:1530:       ctx.i = i;
	s32i.n	a10, sp, 44	# ctx.i,
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	slli	a13, a13, 1	# _69, tmp1638,
# @OPUS@\upstream\celt\bands.c:1538:       N = M*eBands[i+1]-M*eBands[i];
	l32i	a10, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	mov.n	a12, a4	# tmp1632,
# @OPUS@\upstream\celt\bands.c:1538:       N = M*eBands[i+1]-M*eBands[i];
	sub	a3, a3, a2	# tmp1642, tmp1639, _66
# @OPUS@\upstream\celt\bands.c:1535:          Y = Y_+M*eBands[i];
	add.n	a4, a8, a13	# tmp2745,, _69
# @OPUS@\upstream\celt\bands.c:1540:       tell = ec_tell_frac(ec);
	l32i	a2, sp, 424	# ec,
# @OPUS@\upstream\celt\bands.c:1535:          Y = Y_+M*eBands[i];
	movi.n	a9, 0	#,
	movnez	a9, a4, a8	#, tmp2745,
# @OPUS@\upstream\celt\bands.c:1538:       N = M*eBands[i+1]-M*eBands[i];
	ssl	a10	#
	sll	a3, a3	#, tmp1642
# @OPUS@\upstream\celt\bands.c:1535:          Y = Y_+M*eBands[i];
	mov.n	a15, a9	# Y,
# @OPUS@\upstream\celt\bands.c:1538:       N = M*eBands[i+1]-M*eBands[i];
	s32i	a3, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:1540:       tell = ec_tell_frac(ec);
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:1543:       if (i != start)
	l32i	a11, sp, 224	# %sfp,
	l32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\celt\bands.c:1540:       tell = ec_tell_frac(ec);
	s32i	a2, sp, 160	# %sfp,
# @OPUS@\upstream\celt\bands.c:1531:       last = (i==end-1);
	extui	a12, a12, 0, 8	# _61, tmp1632
# @OPUS@\upstream\celt\bands.c:1543:       if (i != start)
	beq	a11, a8, .L436	#,,
# @OPUS@\upstream\celt\bands.c:1544:          balance -= tell;
	l32i	a9, sp, 420	# balance,
	sub	a9, a9, a2	#,,
	s32i	a9, sp, 420	# balance,
.L436:
# @OPUS@\upstream\celt\bands.c:1545:       remaining_bits = total_bits-tell-1;
	l32i	a10, sp, 416	# total_bits,
	l32i	a11, sp, 160	# %sfp,
# @OPUS@\upstream\celt\bands.c:1552:          b = 0;
	movi.n	a8, 0	#,
# @OPUS@\upstream\celt\bands.c:1545:       remaining_bits = total_bits-tell-1;
	sub	a4, a10, a11	# _77,,
# @OPUS@\upstream\celt\bands.c:1545:       remaining_bits = total_bits-tell-1;
	addi.n	a2, a4, -1	# remaining_bits, _77,
# @OPUS@\upstream\celt\bands.c:1547:       if (i <= codedBands-1)
	l32i	a9, sp, 264	# %sfp,
	l32i	a10, sp, 116	# %sfp,
# @OPUS@\upstream\celt\bands.c:1546:       ctx.remaining_bits = remaining_bits;
	s32i	a2, sp, 64	# ctx.remaining_bits, remaining_bits
# @OPUS@\upstream\celt\bands.c:1552:          b = 0;
	s32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:1547:       if (i <= codedBands-1)
	blt	a9, a10, .L437	#,,
# @OPUS@\upstream\celt\bands.c:1549:          curr_balance = celt_sudiv(balance, IMIN(3, codedBands-i));
	l32i	a11, sp, 432	# codedBands,
	sub	a3, a11, a10	# tmp1644,,
	blti	a3, 4, .L438	# tmp1644,,
	movi.n	a3, 3	# tmp1644,
.L438:
# @OPUS@\upstream\celt\entcode.h:148:    return n/d;
	l32i	a2, sp, 420	# balance,
	s32i	a4, sp, 348	#,
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:1550:          b = IMAX(0, IMIN(16383, IMIN(remaining_bits+1,pulses[i]+curr_balance)));
	l32i	a8, sp, 164	# %sfp,
	l32r	a5, .LC53	#, tmp1658
	l32i.n	a3, a8, 0	# MEM[base: _4563, offset: 0B], MEM[base: _4563, offset: 0B]
	l32i	a4, sp, 348	#,
	add.n	a2, a2, a3	# tmp1651,, MEM[base: _4563, offset: 0B]
	bge	a5, a4, .L439	# tmp1658, _77,
	mov.n	a4, a5	# _77, tmp1658
.L439:
	s32i	a2, sp, 136	# %sfp, tmp1651
	bge	a4, a2, .L440	# _77, tmp1651,
	s32i	a4, sp, 136	# %sfp, _77
.L440:
	l32i	a10, sp, 136	# %sfp,
	movi.n	a9, 0	#,
	movgez	a9, a10, a10	#,,
	s32i	a9, sp, 136	# %sfp,
.L437:
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a11, sp, 220	# %sfp,
	beqz.n	a11, .L441	#,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a9, sp, 288	# %sfp,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a10, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l16si	a2, a8, 0	# MEM[base: _4590, offset: 0B], tmp1660
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l16si	a3, a9, 0	# *_12, tmp1665
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	ssl	a10	#
	sll	a2, a2	# tmp1663, tmp1660
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	sub	a2, a2, a11	# tmp1664, tmp1663,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	ssl	a10	#
	sll	a3, a3	# tmp1668, tmp1665
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	bge	a2, a3, .L442	# tmp1664, tmp1668,
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a8, sp, 116	# %sfp,
	l32i	a9, sp, 260	# %sfp,
	bne	a8, a9, .L444	#,,
	j	.L443		#
.L442:
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a10, sp, 192	# %sfp,
	beqz.n	a10, .L746	#,
	bbci	a14, 0, .L441	# update_lowband,,
.L746:
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a11, sp, 116	# %sfp,
	s32i	a11, sp, 192	# %sfp,
.L441:
# @OPUS@\upstream\celt\bands.c:1558:       if (i == start+1)
	l32i	a14, sp, 116	# %sfp,
	l32i	a8, sp, 260	# %sfp,
	bne	a14, a8, .L444	#,,
.L688:
# @OPUS@\upstream\celt\bands.c:1559:          special_hybrid_folding(m, norm, norm2, start, M, dual_stereo);
	l32i	a9, sp, 232	# %sfp,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	l32i	a10, sp, 328	# %sfp,
# @OPUS@\upstream\celt\bands.c:1559:          special_hybrid_folding(m, norm, norm2, start, M, dual_stereo);
	l32i.n	a3, a9, 24	# MEM[(const opus_int16 * *)m_265(D) + 24B], _376
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	l32i	a11, sp, 308	# %sfp,
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	add.n	a2, a3, a11	# tmp1681, _376,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	add.n	a4, a3, a10	# tmp1678, _376,
	l16si	a4, a4, 0	# *_381, _383
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	l16si	a14, a2, 0	# *_385, tmp1682
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	add.n	a3, a3, a8	# tmp1686, _376,
	l16si	a2, a3, 0	# *_392, tmp1687
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	l32i	a9, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	sub	a14, a4, a14	# tmp1685, _383, tmp1682
# @OPUS@\upstream\celt\bands.c:1406:    n1 = M*(eBands[start+1]-eBands[start]);
	ssl	a9	#
	sll	a14, a14	# n1, tmp1685
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	sub	a2, a2, a4	# tmp1690, tmp1687, _383
# @OPUS@\upstream\celt\bands.c:1410:    OPUS_COPY(&norm[n1], &norm[2*n1 - n2], n2-n1);
	slli	a7, a14, 1	# _398, n1,
# @OPUS@\upstream\celt\bands.c:1407:    n2 = M*(eBands[start+2]-eBands[start+1]);
	ssl	a9	#
	sll	a2, a2	# n2, tmp1690
# @OPUS@\upstream\celt\bands.c:1410:    OPUS_COPY(&norm[n1], &norm[2*n1 - n2], n2-n1);
	sub	a6, a7, a2	# tmp1692, _398, n2
	l32i	a10, sp, 184	# %sfp,
	slli	a6, a6, 1	# _403, tmp1692,
	sub	a14, a2, a14	# _406, n2, n1
	add.n	a3, a10, a6	#,, _403
	add.n	a2, a10, a7	#,, _398
	movi.n	a5, 2	#,
	mov.n	a4, a14	#, _406
	s32i	a6, sp, 344	#,
	s32i	a7, sp, 340	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:1411:    if (dual_stereo)
	l32i	a11, sp, 404	# dual_stereo,
	l32i	a6, sp, 344	#,
	l32i	a7, sp, 340	#,
	beqz.n	a11, .L444	#,
# @OPUS@\upstream\celt\bands.c:1412:       OPUS_COPY(&norm2[n1], &norm2[2*n1 - n2], n2-n1);
	mov.n	a4, a14	#, _406
	l32i	a14, sp, 452	# norm2_scratch,
	movi.n	a5, 2	#,
	add.n	a3, a14, a6	#,, _403
	add.n	a2, a14, a7	#,, _398
	call0	yoradio_opus_copy		#
.L444:
# @OPUS@\upstream\celt\bands.c:1565:       tf_change = tf_res[i];
	l32i	a8, sp, 116	# %sfp,
	l32i	a9, sp, 412	# tf_res,
	slli	a2, a8, 2	# tmp1697,,
	add.n	a2, a9, a2	# tmp1698,, tmp1697
# @OPUS@\upstream\celt\bands.c:1567:       if (i>=m->effEBands)
	l32i	a10, sp, 232	# %sfp,
# @OPUS@\upstream\celt\bands.c:1565:       tf_change = tf_res[i];
	l32i.n	a2, a2, 0	# MEM[base: _4560, offset: 0B], tf_change
# @OPUS@\upstream\celt\bands.c:1567:       if (i>=m->effEBands)
	l32i.n	a3, a10, 12	# m_265(D)->effEBands, m_265(D)->effEBands
# @OPUS@\upstream\celt\bands.c:1566:       ctx.tf_change = tf_change;
	s32i.n	a2, sp, 56	# ctx.tf_change, tf_change
# @OPUS@\upstream\celt\bands.c:1567:       if (i>=m->effEBands)
	bge	a8, a3, .L446	#, m_265(D)->effEBands,
# @OPUS@\upstream\celt\bands.c:1533:       X = X_+M*eBands[i];
	l32i	a11, sp, 292	# %sfp,
	add.n	a13, a11, a13	#,, _69
	s32i	a13, sp, 172	# %sfp,
	j	.L447		#
.L446:
# @OPUS@\upstream\celt\bands.c:1570:          if (Y_!=NULL)
	l32i	a14, sp, 176	# %sfp,
	l32i	a8, sp, 184	# %sfp,
	l32i	a9, sp, 300	# %sfp,
	movi.n	a10, 0	#,
	movnez	a15, a8, a14	# Y,,
	s32i	a9, sp, 172	# %sfp,
	s32i	a10, sp, 168	# %sfp,
.L447:
# @OPUS@\upstream\celt\bands.c:1574:       if (last && !theta_rdo)
	beqz.n	a12, .L448	# _61,
# @OPUS@\upstream\celt\bands.c:1575:          lowband_scratch = NULL;
	l32i	a14, sp, 168	# %sfp,
	l32i	a12, sp, 284	# %sfp,
	movi.n	a11, 0	#,
	moveqz	a11, a14, a12	#,,
	s32i	a11, sp, 168	# %sfp,
.L448:
# @OPUS@\upstream\celt\bands.c:1579:       if (lowband_offset != 0 && (spread!=SPREAD_AGGRESSIVE || B>1 || tf_change<0))
	l32i	a8, sp, 192	# %sfp,
	beqz.n	a8, .L708	#,
# @OPUS@\upstream\celt\bands.c:1579:       if (lowband_offset != 0 && (spread!=SPREAD_AGGRESSIVE || B>1 || tf_change<0))
	l32i	a9, sp, 296	# %sfp,
	l32i	a10, sp, 304	# %sfp,
	or	a3, a9, a10	# tmp1707,,
	bnez.n	a3, .L747	# tmp1707,
	bgez	a2, .L708	# tf_change,
.L747:
# @OPUS@\upstream\celt\bands.c:1585:          effective_lowband = IMAX(0, M*eBands[lowband_offset]-norm_offset-N);
	l32i	a11, sp, 192	# %sfp,
	l32i	a12, sp, 280	# %sfp,
	slli	a5, a11, 1	# tmp1712,,
	add.n	a5, a12, a5	# _107,, tmp1712
	l32i	a14, sp, 212	# %sfp,
	l32i	a8, sp, 128	# %sfp,
	l32i	a9, sp, 428	# LM,
	l16si	a7, a5, 0	# *_107, tmp1713
	add.n	a13, a14, a8	# tmp1717,,
	ssl	a9	#
	sll	a7, a7	# tmp1716, tmp1713
	sub	a13, a7, a13	# effective_lowband, tmp1716, tmp1717
	addi.n	a3, a11, -1	# fold_end,,
# @OPUS@\upstream\celt\bands.c:1585:          effective_lowband = IMAX(0, M*eBands[lowband_offset]-norm_offset-N);
	movi.n	a10, 0	#,
	movltz	a13, a10, a13	# effective_lowband,, effective_lowband
	slli	a7, a3, 1	# tmp1719, fold_end,
	add.n	a6, a14, a13	# _5314,, effective_lowband
	add.n	a7, a12, a7	# ivtmp$729,, tmp1719
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	mov.n	a2, a11	# fold_start,
	mov.n	a8, a9	# LM,
.L452:
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	l16si	a4, a7, 0	# MEM[base: _4623, offset: 0B], tmp1720
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	addi.n	a2, a2, -1	# fold_start, fold_start,
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	ssl	a8	# LM
	sll	a4, a4	# _118, tmp1720
	addi	a7, a7, -2	# ivtmp$729, ivtmp$729,
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	blt	a6, a4, .L452	# _5314, _118,
# @OPUS@\upstream\celt\bands.c:1590:          while(++fold_end < i && M*eBands[fold_end] < effective_lowband+norm_offset+N);
	l32i	a11, sp, 128	# %sfp,
	l32i	a7, sp, 116	# %sfp, i
	l32i	a8, sp, 428	# LM, LM
	add.n	a6, a11, a6	# tmp3021,, _5314
.L454:
# @OPUS@\upstream\celt\bands.c:1590:          while(++fold_end < i && M*eBands[fold_end] < effective_lowband+norm_offset+N);
	addi.n	a3, a3, 1	# fold_end, fold_end,
	bge	a3, a7, .L453	# fold_end, i,
# @OPUS@\upstream\celt\bands.c:1590:          while(++fold_end < i && M*eBands[fold_end] < effective_lowband+norm_offset+N);
	l16si	a4, a5, 0	# MEM[base: _4631, offset: 0B], tmp1723
	addi.n	a5, a5, 2	# ivtmp$724, ivtmp$724,
# @OPUS@\upstream\celt\bands.c:1590:          while(++fold_end < i && M*eBands[fold_end] < effective_lowband+norm_offset+N);
	ssl	a8	# LM
	sll	a4, a4	# _125, tmp1723
# @OPUS@\upstream\celt\bands.c:1590:          while(++fold_end < i && M*eBands[fold_end] < effective_lowband+norm_offset+N);
	blt	a4, a6, .L454	# _125, tmp3021,
.L453:
	l32i	a12, sp, 204	# %sfp,
	l32i	a10, sp, 384	# collapse_masks,
	mull	a9, a2, a12	# _4654, fold_start,
# @OPUS@\upstream\celt\bands.c:1587:          while(M*eBands[--fold_start] > effective_lowband+norm_offset);
	movi.n	a14, 0	# y_cm,
	add.n	a8, a12, a9	# _4645,, _4654
	add.n	a4, a10, a9	# ivtmp$717,, _4654
	mov.n	a6, a14	# x_cm, y_cm
	addi.n	a8, a8, -1	# tmp2725, _4645,
	mov.n	a10, a12	# iftmp$65_606,
.L455:
# @OPUS@\upstream\celt\bands.c:1597:            y_cm |= collapse_masks[fold_i*C+C-1];
	sub	a5, a4, a9	# tmp1728, ivtmp$717, _4654
	add.n	a5, a5, a8	# tmp1730, tmp1728, tmp2725
# @OPUS@\upstream\celt\bands.c:1596:            x_cm |= collapse_masks[fold_i*C+0];
	l8ui	a7, a4, 0	# MEM[base: _4652, offset: 0B], MEM[base: _4652, offset: 0B]
# @OPUS@\upstream\celt\bands.c:1597:            y_cm |= collapse_masks[fold_i*C+C-1];
	l8ui	a5, a5, 0	# MEM[base: _4642, offset: 0B], MEM[base: _4642, offset: 0B]
# @OPUS@\upstream\celt\bands.c:1597:            y_cm |= collapse_masks[fold_i*C+C-1];
	addi.n	a2, a2, 1	# fold_start, fold_start,
# @OPUS@\upstream\celt\bands.c:1596:            x_cm |= collapse_masks[fold_i*C+0];
	or	a6, a6, a7	# x_cm, x_cm, MEM[base: _4652, offset: 0B]
# @OPUS@\upstream\celt\bands.c:1597:            y_cm |= collapse_masks[fold_i*C+C-1];
	or	a14, a14, a5	# y_cm, y_cm, MEM[base: _4642, offset: 0B]
	add.n	a4, a4, a10	# ivtmp$717, ivtmp$717, iftmp$65_606
# @OPUS@\upstream\celt\bands.c:1598:          } while (++fold_i<fold_end);
	blt	a2, a3, .L455	# fold_start, fold_end,
	j	.L450		#
.L708:
# @OPUS@\upstream\celt\bands.c:1603:          x_cm = y_cm = (1<<B)-1;
	l32i	a14, sp, 208	# %sfp, y_cm
# @OPUS@\upstream\celt\bands.c:1523:       int effective_lowband=-1;
	movi.n	a13, -1	# effective_lowband,
# @OPUS@\upstream\celt\bands.c:1603:          x_cm = y_cm = (1<<B)-1;
	mov.n	a6, a14	# x_cm, y_cm
.L450:
# @OPUS@\upstream\celt\bands.c:1605:       if (dual_stereo && i==intensity)
	l32i	a11, sp, 404	# dual_stereo,
	beqz.n	a11, .L456	#,
	l32i	a12, sp, 408	# intensity,
	l32i	a8, sp, 116	# %sfp,
	bne	a12, a8, .L456	#,,
# @OPUS@\upstream\celt\bands.c:1611:          if (resynth)
	l32i	a9, sp, 220	# %sfp,
	beqz.n	a9, .L457	#,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	l32i	a10, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	l32i	a11, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	l16si	a2, a10, 0	# MEM[base: _4590, offset: 0B], tmp1743
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	l32i	a12, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	ssl	a11	#
	sll	a2, a2	# tmp1746, tmp1743
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	sub	a2, a2, a12	# tmp1747, tmp1746,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	blti	a2, 1, .L457	# tmp1747,,
	l32i	a3, sp, 184	# %sfp, ivtmp$711
	l32i	a5, sp, 452	# norm2_scratch, ivtmp$712
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	movi.n	a4, 0	# j,
	mov.n	a7, a12	# norm_offset,
	mov.n	a8, a10	# ivtmp$734,
	mov.n	a9, a11	# LM,
.L458:
# @OPUS@\upstream\celt\bands.c:1613:                norm[j] = HALF32(norm[j]+norm2[j]);
	l16si	a2, a3, 0	# MEM[base: _4669, offset: 0B], tmp1748
	l16si	a10, a5, 0	# MEM[base: _4667, offset: 0B], tmp1751
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\bands.c:1613:                norm[j] = HALF32(norm[j]+norm2[j]);
	add.n	a2, a2, a10	# tmp1754, tmp1748, tmp1751
	srai	a2, a2, 1	# tmp1755, tmp1754,
# @OPUS@\upstream\celt\bands.c:1613:                norm[j] = HALF32(norm[j]+norm2[j]);
	s16i	a2, a3, 0	# MEM[base: _4669, offset: 0B], tmp1755
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	l16si	a2, a8, 0	# MEM[base: _4590, offset: 0B], tmp1756
	addi.n	a3, a3, 2	# ivtmp$711, ivtmp$711,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	ssl	a9	# LM
	sll	a2, a2	# tmp1759, tmp1756
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	sub	a2, a2, a7	# tmp1760, tmp1759, norm_offset
	addi.n	a5, a5, 2	# ivtmp$712, ivtmp$712,
# @OPUS@\upstream\celt\bands.c:1612:             for (j=0;j<M*eBands[i]-norm_offset;j++)
	blt	a4, a2, .L458	# j, tmp1760,
	j	.L457		#
.L456:
# @OPUS@\upstream\celt\bands.c:1615:       if (dual_stereo)
	l32i	a8, sp, 404	# dual_stereo,
	beqz.n	a8, .L457	#,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32i	a9, sp, 136	# %sfp,
	srai	a8, a9, 1	# _159,,
	beqi	a13, -1, .L459	# effective_lowband,,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32i	a10, sp, 184	# %sfp,
	l32i	a11, sp, 116	# %sfp,
	l32i	a12, sp, 200	# %sfp,
# @OPUS@\upstream\celt\bands.c:1618:                effective_lowband != -1 ? norm+effective_lowband : NULL, LM,
	slli	a13, a13, 1	# tmp1761, effective_lowband,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	add.n	a7, a10, a13	# iftmp$96_350,, tmp1761
	beq	a11, a12, .L460	#,,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32r	a9, .LC51	#,
	l32i	a10, sp, 168	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a11, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	s32i.n	a6, sp, 16	#, x_cm
	s32i.n	a10, sp, 12	#,
	s32i.n	a9, sp, 8	#,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l16si	a2, a11, 0	# MEM[base: _4590, offset: 0B], tmp1763
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	s32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a9, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a10, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	ssl	a9	#
	sll	a2, a2	# tmp1766, tmp1763
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	sub	a2, a2, a10	# tmp1767, tmp1766,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32i	a11, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	slli	a2, a2, 1	# tmp1768, tmp1767,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	addi	a12, sp, 32	#,,
	add.n	a2, a11, a2	# tmp1769,, tmp1768
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	s32i.n	a2, sp, 4	#, tmp1769
	s32i.n	a9, sp, 0	#,
	mov.n	a5, a8	#, _159
	mov.n	a2, a12	#,
	s32i	a12, sp, 132	# %sfp,
	s32i	a8, sp, 340	#,
	call0	quant_band		#
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	l32i	a9, sp, 452	# norm2_scratch,
	l32i	a8, sp, 340	#,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	mov.n	a12, a2	# x_cm,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	add.n	a7, a9, a13	# iftmp$102_1679,, tmp1761
.L695:
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	l32i	a10, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	l32i	a11, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	l16si	a2, a10, 0	# MEM[base: _4590, offset: 0B], tmp1771
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	l32i	a9, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	ssl	a11	#
	sll	a2, a2	# tmp1774, tmp1771
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	sub	a2, a2, a9	# tmp1775, tmp1774,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	l32i	a10, sp, 452	# norm2_scratch,
# @OPUS@\upstream\celt\bands.c:1622:                last?NULL:norm2+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, y_cm);
	slli	a2, a2, 1	# tmp1776, tmp1775,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	add.n	a2, a10, a2	# iftmp$104_254,, tmp1776
	mov.n	a9, a11	#,
.L699:
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	s32i.n	a14, sp, 16	#, y_cm
	l32i	a11, sp, 168	# %sfp,
	l32i	a14, sp, 140	# %sfp,
	s32i.n	a2, sp, 4	#, iftmp$104_254
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a2, sp, 132	# %sfp,
	s32i.n	a11, sp, 12	#,
	s32i.n	a14, sp, 8	#,
	s32i.n	a9, sp, 0	#,
	mov.n	a5, a8	#, _159
	mov.n	a3, a15	#, Y
	call0	quant_band		#
	extui	a12, a12, 0, 8	# prephitmp_4270, x_cm
	extui	a2, a2, 0, 8	# _5354,
	j	.L461		#
.L457:
# @OPUS@\upstream\celt\bands.c:1624:          if (Y!=NULL)
	beqz.n	a15, .L462	# Y,
# @OPUS@\upstream\celt\bands.c:1695:                ctx.theta_round = 0;
	movi.n	a10, 0	#,
	s32i	a10, sp, 80	# ctx.theta_round,
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	s32i	a10, sp, 152	# %sfp, tmp11
	beqi	a13, -1, .L463	# effective_lowband,,
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	l32i	a12, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1697:                      effective_lowband != -1 ? norm+effective_lowband : NULL, LM,
	slli	a13, a13, 1	# tmp1779, effective_lowband,
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	add.n	a13, a12, a13	#,, tmp1779
	s32i	a13, sp, 152	# %sfp,
.L463:
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	movi.n	a8, 0	#,
	l32i	a9, sp, 116	# %sfp,
	l32i	a10, sp, 200	# %sfp,
	s32i	a8, sp, 236	# %sfp,
	beq	a9, a10, .L464	#,,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	l32i	a11, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	l32i	a12, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	l16si	a2, a11, 0	# MEM[base: _4590, offset: 0B], tmp1780
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	l32i	a8, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	ssl	a12	#
	sll	a2, a2	# tmp1783, tmp1780
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	sub	a2, a2, a8	# tmp1784, tmp1783,
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	l32i	a9, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	slli	a2, a2, 1	# tmp1785, tmp1784,
# @OPUS@\upstream\celt\bands.c:1696:                x_cm = quant_band_stereo(&ctx, X, Y, N, b, B,
	add.n	a2, a9, a2	#,, tmp1785
	s32i	a2, sp, 236	# %sfp,
.L464:
# @OPUS@\upstream\celt\bands.c:1270:    encode = band_encode(ctx);
	l32i.n	a10, sp, 32	# MEM[(int *)&ctx],
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	or	a14, a6, a14	#, x_cm, y_cm
# @OPUS@\upstream\celt\bands.c:1274:    if (N==1)
	l32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:1698:                      last?NULL:norm+M*eBands[i]-norm_offset, lowband_scratch, x_cm|y_cm);
	s32i	a14, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1270:    encode = band_encode(ctx);
	s32i	a10, sp, 240	# %sfp,
# @OPUS@\upstream\celt\bands.c:1271:    ec = ctx->ec;
	l32i.n	a14, sp, 60	# ctx.ec, ec
# @OPUS@\upstream\celt\bands.c:1274:    if (N==1)
	bnei	a11, 1, .L465	#,,
# @OPUS@\upstream\celt\bands.c:1274:    if (N==1)
	l32i	a12, sp, 172	# %sfp, x
	movi.n	a13, 2	# ivtmp_1797,
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
	bnez.n	a10, .L711	#,
	j	.L474		#
.L713:
# @OPUS@\upstream\celt\bands.c:951:    } while (++c<1+stereo);
	movi.n	a13, 1	# ivtmp_1797,
.L474:
# @OPUS@\upstream\celt\bands.c:937:       if (ctx->remaining_bits>=1<<BITRES)
	bgei	a3, 8, .L467	# ctx.remaining_bits,,
	j	.L935		#
.L470:
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	s16i	a4, a12, 0	# *x_433, iftmp$138_1876
	j	.L469		#
.L472:
	l32r	a4, .LC50	#, iftmp$138_1876
	bnez.n	a2, .L470	# _2532,
	j	.L471		#
.L467:
# @OPUS@\upstream\celt\bands.c:944:             sign = ec_dec_bits(ec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a14	#, ec
	call0	ec_dec_bits		#
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a4, sp, 36	# ctx.resynth, ctx.resynth
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	addi	a3, a3, -8	# ctx.remaining_bits, ctx.remaining_bits,
	s32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	bnez.n	a4, .L472	# ctx.resynth,
	j	.L469		#
.L471:
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	l32r	a4, .LC49	#, iftmp$138_1876
	j	.L470		#
.L935:
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	bnez.n	a2, .L471	# ctx.resynth,
.L469:
	mov.n	a12, a15	# x, Y
# @OPUS@\upstream\celt\bands.c:951:    } while (++c<1+stereo);
	bnei	a13, 1, .L713	# ivtmp_1797,,
	j	.L475		#
.L711:
	mov.n	a5, a14	# ec, ec
	j	.L466		#
.L714:
	movi.n	a13, 1	# ivtmp_5323,
.L466:
# @OPUS@\upstream\celt\bands.c:942:             ec_enc_bits(ec, sign, 1);
	movi.n	a4, 1	#,
	mov.n	a2, a5	#, ec
# @OPUS@\upstream\celt\bands.c:937:       if (ctx->remaining_bits>=1<<BITRES)
	bgei	a3, 8, .L476	# ctx.remaining_bits,,
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	beqz.n	a2, .L478	# ctx.resynth,
.L477:
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	l32r	a2, .LC49	#, iftmp$138_561
	j	.L479		#
.L476:
# @OPUS@\upstream\celt\bands.c:941:             sign = x[0]<0;
	l16si	a14, a12, 0	# *x_550, _551
# @OPUS@\upstream\celt\bands.c:942:             ec_enc_bits(ec, sign, 1);
	s32i	a5, sp, 344	#,
	extui	a3, a14, 31, 1	#, _551,
	call0	ec_enc_bits		#
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
# @OPUS@\upstream\celt\bands.c:946:          ctx->remaining_bits -= 1<<BITRES;
	addi	a3, a3, -8	# ctx.remaining_bits, ctx.remaining_bits,
	s32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
# @OPUS@\upstream\celt\bands.c:948:       if (ctx->resynth)
	l32i	a5, sp, 344	#,
	beqz.n	a2, .L478	# ctx.resynth,
# @OPUS@\upstream\celt\bands.c:949:          x[0] = sign ? -NORM_SCALING : NORM_SCALING;
	bgez	a14, .L477	# _551,
	l32r	a2, .LC50	#, iftmp$138_561
.L479:
	s16i	a2, a12, 0	# *x_550, iftmp$138_561
.L478:
	mov.n	a12, a15	# x, Y
# @OPUS@\upstream\celt\bands.c:951:    } while (++c<1+stereo);
	bnei	a13, 1, .L714	# ivtmp_5323,,
.L475:
# @OPUS@\upstream\celt\bands.c:952:    if (lowband_out)
	l32i	a14, sp, 236	# %sfp,
	movi.n	a12, 1	# prephitmp_4270,
	beqz.n	a14, .L481	#,
# @OPUS@\upstream\celt\bands.c:953:       lowband_out[0] = SHR16(X[0],4);
	l32i	a8, sp, 172	# %sfp,
	l16ui	a2, a8, 0	# *X_233,
	slli	a2, a2, 16	# tmp1801, *X_233,
	srai	a2, a2, 20	# tmp1802, tmp1801,
	s16i	a2, a14, 0	# *iftmp$110_256, tmp1802
	j	.L481		#
.L465:
# @OPUS@\upstream\celt\bands.c:740:    m = ctx->m;
	l32i.n	a9, sp, 40	# ctx.m,
# @OPUS@\upstream\celt\bands.c:741:    i = ctx->i;
	l32i.n	a10, sp, 44	# ctx.i,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l32i.n	a2, a9, 48	# m_569->logN, m_569->logN
	slli	a3, a10, 1	# tmp1804,,
	add.n	a2, a2, a3	# tmp1805, m_569->logN, tmp1804
	l16si	a12, a2, 0	# *_577, tmp1806
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	l32i	a11, sp, 320	# %sfp,
# @OPUS@\upstream\celt\bands.c:744:    bandE = ctx->bandE;
	l32i	a8, sp, 68	# ctx.bandE,
# @OPUS@\upstream\celt\bands.c:740:    m = ctx->m;
	s32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:747:    pulse_cap = m->logN[i]+LM*(1<<BITRES);
	add.n	a12, a12, a11	# pulse_cap, tmp1806,
# @OPUS@\upstream\celt\bands.c:741:    i = ctx->i;
	s32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:744:    bandE = ctx->bandE;
	s32i	a8, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:742:    intensity = ctx->intensity;
	l32i.n	a4, sp, 48	# ctx.intensity, intensity
# ASM intensity: skip unused compute_qn only in the decoder stereo clone.
# Inputs: a10=i, a4=intensity, sp+240=encode; a8 is dead here.
# Preserve a14=ec and all saved m/i/bandE/N/b fields. Entropy is NOT skipped.
	l32i	a8, sp, 240
	bnez	a8, .Lasm_intensity_normal
	blt	a10, a4, .Lasm_intensity_normal
	j	.L980
.Lasm_intensity_normal:
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	srai	a2, a12, 1	# _582, pulse_cap,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	beqi	a9, 2, .L482	#,,
	j	.L936		#
.L687:
# @OPUS@\upstream\celt\bands.c:664:    qb = celt_sudiv(b+N2*offset, N2);
	mull	a2, a3, a2	# tmp1809, N2, offset
# @OPUS@\upstream\celt\entcode.h:148:    return n/d;
	l32i	a10, sp, 136	# %sfp,
	s32i	a4, sp, 348	#,
	add.n	a2, a2, a10	#, tmp1809,
	call0	__divsi3		#
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	l32i	a11, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	l32i	a4, sp, 348	#,
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	sub	a12, a11, a12	# tmp1816,, pulse_cap
	addi	a12, a12, -32	# tmp1817, tmp1816,
# @OPUS@\upstream\celt\bands.c:665:    qb = IMIN(b-pulse_cap-(4<<BITRES), qb);
	bge	a12, a2, .L484	# tmp1817, qb,
	mov.n	a2, a12	# qb, tmp1817
.L484:
# @OPUS@\upstream\celt\bands.c:669:    if (qb<(1<<BITRES>>1)) {
	bgei	a2, 4, .L485	# qb,,
# @OPUS@\upstream\celt\bands.c:750:    if (stereo && i>=intensity)
	l32i	a12, sp, 120	# %sfp,
	bge	a12, a4, .L486	#, intensity,
# @OPUS@\upstream\celt\bands.c:752:    if (encode)
	l32i	a8, sp, 240	# %sfp,
	bnez.n	a8, .L487	#,
	j	.L980		#
.L485:
# @OPUS@\upstream\celt\bands.c:667:    qb = IMIN(8<<BITRES, qb);
	movi.n	a3, 0x40	# tmp1820,
	bge	a3, a2, .L489	# tmp1820, qb,
	mov.n	a2, a3	# qb, tmp1820
.L489:
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	extui	a3, a2, 0, 3	# tmp1822, qb,
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	slli	a5, a3, 1	# tmp1823, tmp1822,
	l32r	a3, .LC54	#, tmp1821
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	srai	a2, a2, 3	# tmp1828, qb,
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	add.n	a3, a3, a5	# tmp1824, tmp1821, tmp1823
	l16si	a12, a3, 0	# exp2_table8, tmp1825
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	movi.n	a3, 0xe	# tmp1829,
	sub	a2, a3, a2	# tmp1830, tmp1829, tmp1828
# @OPUS@\upstream\celt\bands.c:672:       qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));
	ssr	a2	# tmp1830
	sra	a12, a12	# qn, tmp1825
# @OPUS@\upstream\celt\bands.c:750:    if (stereo && i>=intensity)
	l32i	a9, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:673:       qn = (qn+1)>>1<<1;
	addi.n	a12, a12, 1	# _943, qn,
# @OPUS@\upstream\celt\bands.c:673:       qn = (qn+1)>>1<<1;
	movi.n	a13, -2	# tmp1832,
	and	a13, a12, a13	# qn, _943, tmp1832
# @OPUS@\upstream\celt\bands.c:750:    if (stereo && i>=intensity)
	bge	a9, a4, .L486	#, intensity,
# @OPUS@\upstream\celt\bands.c:752:    if (encode)
	l32i	a10, sp, 240	# %sfp,
	bnez.n	a10, .L490	#,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:795:       if (stereo && N>2)
	l32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:795:       if (stereo && N>2)
	blti	a11, 3, .L937	#,,
	j	.L491		#
.L693:
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	addmi	a6, a6, 0x2000	# tmp1833, _5282,
# @OPUS@\upstream\celt\bands.c:767:             itheta = (itheta*(opus_int32)qn+8192)>>14;
	srai	a6, a6, 14	# down, tmp1833,
	j	.L493		#
.L950:
# @OPUS@\upstream\celt\bands.c:785:             int bias = itheta > 8192 ? 32767/qn : -32767/qn;
	l32r	a2, .LC55	#, tmp1834
	bge	a2, a3, .L494	# tmp1834, itheta,
	l32r	a2, .LC51	#,
	mov.n	a3, a13	#, qn
	s32i	a4, sp, 348	#,
	s32i	a6, sp, 344	#,
	call0	__divsi3		#
	l32i	a4, sp, 348	#,
	l32i	a6, sp, 344	#,
	j	.L495		#
.L494:
	l32r	a2, .LC56	#,
	mov.n	a3, a13	#, qn
	s32i	a4, sp, 348	#,
	s32i	a6, sp, 344	#,
	call0	__divsi3		#
	l32i	a6, sp, 344	#,
	l32i	a4, sp, 348	#,
.L495:
# @OPUS@\upstream\celt\bands.c:786:             down = IMIN(qn-1, IMAX(0, (itheta*(opus_int32)qn + bias)>>14));
	add.n	a6, a2, a6	# tmp1842, iftmp$142_673, _5282
	srai	a6, a6, 14	# tmp1841, tmp1842,
	movi.n	a2, 0	#,
	movltz	a6, a2, a6	# tmp1841,, tmp1841
	addi.n	a2, a13, -1	# tmp1844, qn,
# @OPUS@\upstream\celt\bands.c:786:             down = IMIN(qn-1, IMAX(0, (itheta*(opus_int32)qn + bias)>>14));
	bge	a2, a6, .L496	# tmp1844, down,
	mov.n	a6, a2	# down, tmp1844
.L496:
# @OPUS@\upstream\celt\bands.c:790:                itheta = down+1;
	movi.n	a2, -1	# tmp2765,
	xor	a4, a2, a4	# tmp2764, tmp2765, _596
	extui	a4, a4, 31, 1	# tmp2763, tmp2764,
	add.n	a6, a6, a4	# down, down, tmp2763
	j	.L493		#
.L678:
# @OPUS@\upstream\celt\bands.c:804:             ec_encode(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	slli	a3, a6, 1	# tmp1846, down,
	add.n	a3, a3, a6	# iftmp$143_625, tmp1846, down
# @OPUS@\upstream\celt\bands.c:804:             ec_encode(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	addi.n	a4, a3, 3	# iftmp$144_698, iftmp$143_625,
	j	.L497		#
.L947:
# @OPUS@\upstream\celt\bands.c:804:             ec_encode(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	sub	a4, a2, a4	# tmp1848, tmp2643, x0
	add.n	a4, a4, a6	# _693, tmp1848, down
	addi.n	a3, a4, -1	# iftmp$143_625, _693,
.L497:
# @OPUS@\upstream\celt\bands.c:804:             ec_encode(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	mov.n	a2, a14	#, ec
	s32i	a6, sp, 344	#,
	call0	ec_encode		#
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i	a6, sp, 344	#,
	mov.n	a3, a13	#, qn
	slli	a2, a6, 14	#, down,
	call0	__udivsi3		#
	s32i	a2, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:860:          if (itheta==0)
	bnez.n	a2, .L499	#,
	j	.L498		#
.L676:
# @OPUS@\upstream\celt\bands.c:809:                x=fs/p0;
	movi.n	a3, 3	#,
	s32i	a4, sp, 348	#,
	s32i	a5, sp, 344	#,
	s32i	a7, sp, 340	#,
	call0	__divsi3		#
	mov.n	a12, a2	# x,
	l32i	a4, sp, 348	#,
	l32i	a5, sp, 344	#,
	l32i	a7, sp, 340	#,
	j	.L500		#
.L946:
# @OPUS@\upstream\celt\bands.c:811:                x=x0+1+(fs-(x0+1)*p0);
	movi.n	a6, -1	# tmp1857,
	xor	a6, a6, a5	# tmp1856, tmp1857, x0
# @OPUS@\upstream\celt\bands.c:811:                x=x0+1+(fs-(x0+1)*p0);
	slli	a3, a6, 1	# tmp1859, tmp1856,
	add.n	a3, a3, a6	# tmp1860, tmp1859, tmp1856
# @OPUS@\upstream\celt\bands.c:811:                x=x0+1+(fs-(x0+1)*p0);
	add.n	a12, a3, a12	# tmp1861, tmp1860, _1357
	add.n	a12, a12, a2	# x, tmp1861, _706
.L500:
# @OPUS@\upstream\celt\bands.c:812:             ec_dec_update(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	blt	a5, a12, .L501	# x0, x,
# @OPUS@\upstream\celt\bands.c:812:             ec_dec_update(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	slli	a3, a12, 1	# tmp1863, x,
	add.n	a3, a3, a12	# iftmp$147_626, tmp1863, x
# @OPUS@\upstream\celt\bands.c:812:             ec_dec_update(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	addi.n	a4, a3, 3	# iftmp$148_723, iftmp$147_626,
	j	.L502		#
.L501:
# @OPUS@\upstream\celt\bands.c:812:             ec_dec_update(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	sub	a4, a4, a5	# tmp1865, _1358, x0
	add.n	a4, a4, a12	# _718, tmp1865, x
	addi.n	a3, a4, -1	# iftmp$147_626, _718,
.L502:
# @OPUS@\upstream\celt\bands.c:812:             ec_dec_update(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	mov.n	a5, a7	#, ft$146_705
	mov.n	a2, a14	#, ec
	call0	ec_dec_update		#
	j	.L503		#
.L498:
# @OPUS@\upstream\celt\bands.c:861:             intensity_stereo(m, X, Y, bandE, i, N);
	l32i	a8, sp, 124	# %sfp,
	l32i	a7, sp, 128	# %sfp,
	l32i.n	a2, a8, 8	# MEM[(int *)m_569 + 8B],
	l32i	a6, sp, 120	# %sfp,
	l32i	a5, sp, 140	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	mov.n	a4, a15	#, Y
	call0	intensity_stereo$isra$1		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	l32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	sub	a2, a2, a9	#,,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a10, a10, a2	#,,
# @OPUS@\upstream\celt\bands.c:731:    int inv=0;
	movi.n	a11, 0	#,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	s32i	a2, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	s32i	a10, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:731:    int inv=0;
	s32i	a11, sp, 240	# %sfp,
	j	.L504		#
.L499:
	l32i	a12, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:425:       l = MULT16_16(QCONST16(.70710678f, 15), X[j]);
	l32r	a8, .LC57	#, tmp3019
	l32i	a3, sp, 172	# %sfp, ivtmp$706
	slli	a7, a12, 1	# tmp1866,,
	mov.n	a5, a15	# ivtmp$707, Y
	add.n	a7, a7, a3	# _4677, tmp1866, ivtmp$706
# @OPUS@\upstream\celt\bands.c:426:       r = MULT16_16(QCONST16(.70710678f, 15), Y[j]);
	mov.n	a9, a8	# tmp3020, tmp3019
.L505:
# @OPUS@\upstream\celt\bands.c:425:       l = MULT16_16(QCONST16(.70710678f, 15), X[j]);
	l16ui	a2, a3, 0	# MEM[base: _4689, offset: 0B],
# @OPUS@\upstream\celt\bands.c:426:       r = MULT16_16(QCONST16(.70710678f, 15), Y[j]);
	l16ui	a4, a5, 0	# MEM[base: _4687, offset: 0B],
# @OPUS@\upstream\celt\bands.c:425:       l = MULT16_16(QCONST16(.70710678f, 15), X[j]);
	mul16s	a6, a2, a8	# l, MEM[base: _4689, offset: 0B], tmp3019
# @OPUS@\upstream\celt\bands.c:426:       r = MULT16_16(QCONST16(.70710678f, 15), Y[j]);
	mul16s	a2, a4, a9	# r, MEM[base: _4687, offset: 0B], tmp3020
# @OPUS@\upstream\celt\bands.c:427:       X[j] = EXTRACT16(SHR32(ADD32(l, r), 15));
	add.n	a4, a6, a2	# tmp1871, l, r
	srai	a4, a4, 15	# tmp1872, tmp1871,
# @OPUS@\upstream\celt\bands.c:428:       Y[j] = EXTRACT16(SHR32(SUB32(r, l), 15));
	sub	a2, a2, a6	# tmp1873, r, l
# @OPUS@\upstream\celt\bands.c:427:       X[j] = EXTRACT16(SHR32(ADD32(l, r), 15));
	s16i	a4, a3, 0	# MEM[base: _4689, offset: 0B], tmp1872
# @OPUS@\upstream\celt\bands.c:428:       Y[j] = EXTRACT16(SHR32(SUB32(r, l), 15));
	srai	a2, a2, 15	# tmp1874, tmp1873,
	s16i	a2, a5, 0	# MEM[base: _4687, offset: 0B], tmp1874
	addi.n	a3, a3, 2	# ivtmp$706, ivtmp$706,
	addi.n	a5, a5, 2	# ivtmp$707, ivtmp$707,
# @OPUS@\upstream\celt\bands.c:422:    for (j=0;j<N;j++)
	bne	a7, a3, .L505	# _4677, ivtmp$706,
	j	.L506		#
.L682:
# @OPUS@\upstream\celt\bands.c:870:          inv = itheta > 8192 && !ctx->disable_inv;
	l32r	a2, .LC55	#, tmp1875
	bge	a2, a13, .L716	# tmp1875, itheta,
	l32i	a2, sp, 84	# ctx.disable_inv, ctx.disable_inv
	movi.n	a13, 0	# inv,
	bne	a2, a13, .L507	# ctx.disable_inv,,
	l32i	a8, sp, 128	# %sfp,
	mov.n	a2, a15	# ivtmp$703, Y
	slli	a4, a8, 1	# tmp1877,,
	add.n	a4, a4, a15	# _4697, tmp1877, Y
# @OPUS@\upstream\celt\bands.c:874:             for (j=0;j<N;j++)
	bgei	a8, 1, .L509	#,,
.L510:
# @OPUS@\upstream\celt\bands.c:870:          inv = itheta > 8192 && !ctx->disable_inv;
	movi.n	a13, 1	# inv,
	j	.L507		#
.L509:
# @OPUS@\upstream\celt\bands.c:875:                Y[j] = -Y[j];
	l16ui	a3, a2, 0	# MEM[base: _4706, offset: 0B],
	neg	a3, a3	# tmp1879, MEM[base: _4706, offset: 0B]
	s16i	a3, a2, 0	# MEM[base: _4706, offset: 0B], tmp1879
	addi.n	a2, a2, 2	# ivtmp$703, ivtmp$703,
# @OPUS@\upstream\celt\bands.c:874:             for (j=0;j<N;j++)
	bne	a4, a2, .L509	# _4697, ivtmp$703,
	j	.L510		#
.L716:
# @OPUS@\upstream\celt\bands.c:870:          inv = itheta > 8192 && !ctx->disable_inv;
	movi.n	a13, 0	# inv,
.L507:
# @OPUS@\upstream\celt\bands.c:877:          intensity_stereo(m, X, Y, bandE, i, N);
	l32i	a9, sp, 124	# %sfp,
	l32i	a7, sp, 128	# %sfp,
	l32i.n	a2, a9, 8	# MEM[(int *)m_569 + 8B],
	l32i	a6, sp, 120	# %sfp,
	l32i	a5, sp, 140	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	mov.n	a4, a15	#, Y
	call0	intensity_stereo$isra$1		#
.L488:
# @OPUS@\upstream\celt\bands.c:879:       if (*b>2<<BITRES && ctx->remaining_bits > 2<<BITRES)
	l32i	a10, sp, 136	# %sfp,
	movi.n	a2, 0x10	# tmp1880,
	bge	a2, a10, .L718	# tmp1880,,
# @OPUS@\upstream\celt\bands.c:879:       if (*b>2<<BITRES && ctx->remaining_bits > 2<<BITRES)
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
	bge	a2, a3, .L719	# tmp1880, ctx.remaining_bits,
# @OPUS@\upstream\celt\bands.c:881:          if (encode)
	l32i	a11, sp, 240	# %sfp,
	beqz.n	a11, .L512	#,
# @OPUS@\upstream\celt\bands.c:882:             ec_enc_bit_logp(ec, inv, 2);
	movi.n	a4, 2	#,
	mov.n	a3, a13	#, inv
	mov.n	a2, a14	#, ec
	call0	ec_enc_bit_logp		#
	s32i	a13, sp, 240	# %sfp, inv
	j	.L511		#
.L512:
# @OPUS@\upstream\celt\bands.c:884:             inv = ec_dec_bit_logp(ec, 2);
	movi.n	a3, 2	#,
	mov.n	a2, a14	#, ec
	call0	ec_dec_bit_logp		#
	s32i	a2, sp, 240	# %sfp,
	j	.L511		#
.L718:
# @OPUS@\upstream\celt\bands.c:886:          inv = 0;
	movi.n	a8, 0	#,
	s32i	a8, sp, 240	# %sfp,
	j	.L511		#
.L719:
	movi.n	a9, 0	#,
	s32i	a9, sp, 240	# %sfp,
.L511:
# @OPUS@\upstream\celt\bands.c:888:       if (ctx->disable_inv)
	l32i	a2, sp, 84	# ctx.disable_inv, ctx.disable_inv
	bnez.n	a2, .L513	# ctx.disable_inv,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	l32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	sub	a12, a2, a12	#,, _770
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a10, a10, a12	#,,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	s32i	a12, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	s32i	a10, sp, 188	# %sfp,
	j	.L504		#
.L513:
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	l32i	a11, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	sub	a12, a2, a12	#,, _770
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a11, a11, a12	#,,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	s32i	a12, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:889:          inv = 0;
	movi.n	a12, 0	#,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	s32i	a11, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:889:          inv = 0;
	s32i	a12, sp, 240	# %sfp,
	j	.L504		#
.L742:
# @OPUS@\upstream\celt\bands.c:895:    if (itheta == 0)
	movi.n	a14, 0	#,
	s32i	a14, sp, 240	# %sfp,
.L504:
# @OPUS@\upstream\celt\bands.c:899:       *fill &= (1<<B)-1;
	l32i	a9, sp, 208	# %sfp,
	l32i	a10, sp, 112	# %sfp,
	l32r	a8, .LC51	#,
	movi.n	a11, 0	#,
	and	a9, a9, a10	#,,
	s32i	a8, sp, 140	# %sfp,
	s32i	a9, sp, 276	# %sfp,
	s32i	a8, sp, 316	# %sfp,
	s32i	a11, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:898:       iside = 0;
	s32i	a11, sp, 216	# %sfp, tmp12
# @OPUS@\upstream\celt\bands.c:897:       imid = 32767;
	s32i	a8, sp, 272	# %sfp,
# @OPUS@\upstream\celt\bands.c:900:       delta = -16384;
	l32r	a2, .LC50	#, delta
	j	.L514		#
.L675:
# @OPUS@\upstream\celt\bands.c:901:    } else if (itheta == 16384)
	l32r	a2, .LC49	#, tmp1884
	l32i	a8, sp, 196	# %sfp,
	bne	a8, a2, .L515	#, tmp1884,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	l32i	a11, sp, 112	# %sfp,
	l32i	a12, sp, 336	# %sfp,
# @OPUS@\upstream\celt\bands.c:904:       iside = 32767;
	l32r	a9, .LC51	#,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	movi.n	a10, 0	#,
	and	a11, a11, a12	#,,
# @OPUS@\upstream\celt\bands.c:904:       iside = 32767;
	s32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	s32i	a10, sp, 316	# %sfp,
	s32i	a11, sp, 276	# %sfp,
# @OPUS@\upstream\celt\bands.c:906:       delta = 16384;
	mov.n	a2, a8	# delta,
# @OPUS@\upstream\celt\bands.c:905:       *fill &= ((1<<B)-1)<<B;
	s32i	a10, sp, 240	# %sfp, tmp14
# @OPUS@\upstream\celt\bands.c:904:       iside = 32767;
	s32i	a9, sp, 216	# %sfp,
# @OPUS@\upstream\celt\bands.c:903:       imid = 0;
	s32i	a10, sp, 272	# %sfp,
	j	.L514		#
.L515:
# @OPUS@\upstream\celt\bands.c:908:       imid = bitexact_cos((opus_int16)itheta);
	slli	a3, a8, 16	# tmp1885,,
	srai	a3, a3, 16	# _854, tmp1885,
# @OPUS@\upstream\celt\bands.c:909:       iside = bitexact_cos((opus_int16)(16384-itheta));
	sub	a2, a2, a3	# tmp1912, tmp1884, _854
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	mul16s	a2, a2, a2	# tmp1915, tmp1912, tmp1912
	mull	a4, a3, a3	# tmp1886, _854, _854
# @OPUS@\upstream\celt\bands.c:72:    tmp = (4096+((opus_int32)(x)*(x)))>>13;
	addmi	a3, a2, 0x1000	# tmp1916, tmp1915,
	addmi	a4, a4, 0x1000	# tmp1887, tmp1886,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a3, a3, 3	# tmp1918, tmp1916,
	srai	a3, a3, 16	# x2, tmp1918,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	movi	a2, -0x272	# tmp1890,
# @OPUS@\upstream\celt\bands.c:74:    x2 = tmp;
	slli	a4, a4, 3	# tmp1889, tmp1887,
	srai	a4, a4, 16	# x2, tmp1889,
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a5, a2, a3	# tmp1920, tmp1890, x2
	mul16s	a2, a2, a4	# tmp1891, tmp1890, x2
	l32r	a6, .LC58	#, tmp1896
	addmi	a5, a5, 0x4000	# tmp1921, tmp1920,
	addmi	a2, a2, 0x4000	# tmp1892, tmp1891,
	srai	a5, a5, 15	# tmp1922, tmp1921,
	add.n	a5, a5, a6	# tmp1924, tmp1922, tmp1896
	srai	a2, a2, 15	# tmp1893, tmp1892,
	add.n	a2, a2, a6	# tmp1895, tmp1893, tmp1896
	mul16s	a5, a5, a3	# tmp1926, tmp1924, x2
	mul16s	a2, a2, a4	# tmp1897, tmp1895, x2
	l32r	a6, .LC59	#, tmp1902
	addmi	a5, a5, 0x4000	# tmp1927, tmp1926,
	addmi	a2, a2, 0x4000	# tmp1898, tmp1897,
	srai	a5, a5, 15	# tmp1928, tmp1927,
	add.n	a5, a5, a6	# tmp1930, tmp1928, tmp1902
	srai	a2, a2, 15	# tmp1899, tmp1898,
	add.n	a2, a2, a6	# tmp1901, tmp1899, tmp1902
	mul16s	a5, a5, a3	# tmp1932, tmp1930, x2
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	l32r	a6, .LC60	#, tmp1907
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	mul16s	a2, a2, a4	# tmp1903, tmp1901, x2
	addmi	a5, a5, 0x4000	# tmp1933, tmp1932,
	srai	a5, a5, 15	# tmp1934, tmp1933,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a3, a6, a3	# tmp1935, tmp1907, x2
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	addmi	a2, a2, 0x4000	# tmp1904, tmp1903,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	sub	a4, a6, a4	# tmp1906, tmp1907, x2
	add.n	a3, a5, a3	# tmp1939, tmp1934, tmp1935
# @OPUS@\upstream\celt\bands.c:75:    x2 = (32767-x2) + FRAC_MUL16(x2, (-7651 + FRAC_MUL16(x2, (8277 + FRAC_MUL16(-626, x2)))));
	srai	a2, a2, 15	# tmp1905, tmp1904,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	add.n	a2, a2, a4	# tmp1910, tmp1905, tmp1906
	slli	a3, a3, 16	# tmp1940, tmp1939,
	srai	a3, a3, 16	#, tmp1940,
	slli	a2, a2, 16	# tmp1911, tmp1910,
	srai	a2, a2, 16	#, tmp1911,
# @OPUS@\upstream\celt\bands.c:85:    ls=EC_ILOG(isin);
	nsau	a7, a3	# _987,
# @OPUS@\upstream\celt\bands.c:84:    lc=EC_ILOG(icos);
	nsau	a6, a2	# _985,
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	addi	a5, a7, -17	# tmp1941, _987,
# @OPUS@\upstream\celt\bands.c:87:    isin<<=15-ls;
	ssl	a5	# tmp1941
	sll	a5, a3	# isin,
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	addi	a4, a6, -17	# tmp1944, _985,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	s32i	a2, sp, 272	# %sfp,
# @OPUS@\upstream\celt\bands.c:86:    icos<<=15-lc;
	ssl	a4	# tmp1944
	sll	a4, a2	# icos,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	slli	a5, a5, 16	# tmp1943, isin,
	l32r	a2, .LC61	#, tmp1948
	srai	a5, a5, 16	# _996, tmp1943,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	slli	a4, a4, 16	# tmp1946, icos,
	srai	a4, a4, 16	# _1008, tmp1946,
# @OPUS@\upstream\celt\bands.c:77:    return 1+x2;
	s32i	a3, sp, 216	# %sfp,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mov.n	a3, a2	# tmp1961, tmp1948
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a2, a5, a2	# tmp1947, _996, tmp1948
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mul16s	a3, a4, a3	# tmp1960, _1008, tmp1961
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	l32r	a8, .LC62	#, tmp1953
	addmi	a2, a2, 0x4000	# tmp1949, tmp1947,
	srai	a2, a2, 15	# tmp1950, tmp1949,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a3, a3, 0x4000	# tmp1962, tmp1960,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a2, a2, a8	# tmp1952, tmp1950, tmp1953
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a3, a3, 15	# tmp1963, tmp1962,
	add.n	a3, a3, a8	# tmp1965, tmp1963, tmp1953
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	mul16s	a2, a2, a5	# tmp1954, tmp1952, _996
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	mul16s	a4, a3, a4	# tmp1967, tmp1965, _1008
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	addmi	a2, a2, 0x4000	# tmp1955, tmp1954,
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	sub	a6, a6, a7	# tmp1957, _985, _987
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	srai	a2, a2, 15	# tmp1956, tmp1955,
# @OPUS@\upstream\celt\bands.c:88:    return (ls-lc)*(1<<11)
	slli	a6, a6, 11	# tmp1958, tmp1957,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	addmi	a4, a4, 0x4000	# tmp1968, tmp1967,
# @OPUS@\upstream\celt\bands.c:89:          +FRAC_MUL16(isin, FRAC_MUL16(isin, -2597) + 7932)
	add.n	a2, a2, a6	# tmp1959, tmp1956, tmp1958
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	srai	a4, a4, 15	# tmp1969, tmp1968,
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	addi.n	a3, a9, -1	# tmp1971,,
# @OPUS@\upstream\celt\bands.c:90:          -FRAC_MUL16(icos, FRAC_MUL16(icos, -2597) + 7932);
	sub	a2, a2, a4	# tmp1970, tmp1959, tmp1969
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	slli	a3, a3, 7	# tmp1972, tmp1971,
	l32i	a12, sp, 324	# %sfp,
	mul16s	a2, a2, a3	# tmp1973, tmp1970, tmp1972
# @OPUS@\upstream\celt\bands.c:908:       imid = bitexact_cos((opus_int16)itheta);
	l32i	a10, sp, 272	# %sfp,
	l32i	a11, sp, 64	# ctx.remaining_bits,
	extui	a12, a12, 0, 8	#,
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	addmi	a2, a2, 0x4000	# tmp1974, tmp1973,
# @OPUS@\upstream\celt\bands.c:908:       imid = bitexact_cos((opus_int16)itheta);
	s32i	a10, sp, 316	# %sfp,
	s32i	a11, sp, 252	# %sfp,
	s32i	a12, sp, 312	# %sfp,
# @OPUS@\upstream\celt\bands.c:912:       delta = FRAC_MUL16((N-1)<<7,bitexact_log2tan(iside,imid));
	srai	a2, a2, 15	# delta, tmp1974,
# @OPUS@\upstream\celt\bands.c:1299:    if (N==2)
	bnei	a9, 2, .L720	#,,
# @OPUS@\upstream\celt\bands.c:1307:       if (itheta != 0 && itheta != 16384)
	l32r	a2, .LC63	#, tmp1980
# @OPUS@\upstream\celt\bands.c:1307:       if (itheta != 0 && itheta != 16384)
	l32i	a8, sp, 196	# %sfp,
	bany	a8, a2, .L517	#, tmp1980,
	movi.n	a9, 0	#,
	s32i	a9, sp, 240	# %sfp,
	mov.n	a14, a11	#,
	j	.L518		#
.L743:
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	l32i	a10, sp, 172	# %sfp,
	s32i	a15, sp, 228	# %sfp, Y
	s32i	a10, sp, 132	# %sfp,
.L685:
# @OPUS@\upstream\celt\bands.c:1317:          if (encode)
	l32i	a11, sp, 240	# %sfp,
	beqz.n	a11, .L519	#,
# @OPUS@\upstream\celt\bands.c:1320:             sign = x2[0]*y2[1] - x2[1]*y2[0] < 0;
	l32i	a8, sp, 132	# %sfp,
	l32i	a9, sp, 228	# %sfp,
	l16ui	a12, a8, 0	# *iftmp$125_1470,
	l16ui	a4, a9, 2	# MEM[(celt_norm *)iftmp$126_2523 + 2B],
# @OPUS@\upstream\celt\bands.c:1320:             sign = x2[0]*y2[1] - x2[1]*y2[0] < 0;
	l16ui	a3, a9, 0	# *iftmp$126_2523,
	l16ui	a2, a8, 2	# MEM[(celt_norm *)iftmp$125_1470 + 2B],
# @OPUS@\upstream\celt\bands.c:1320:             sign = x2[0]*y2[1] - x2[1]*y2[0] < 0;
	mul16s	a12, a12, a4	# tmp1981, *iftmp$125_1470, MEM[(celt_norm *)iftmp$126_2523 + 2B]
# @OPUS@\upstream\celt\bands.c:1320:             sign = x2[0]*y2[1] - x2[1]*y2[0] < 0;
	mul16s	a2, a2, a3	# tmp1984, MEM[(celt_norm *)iftmp$125_1470 + 2B], *iftmp$126_2523
# @OPUS@\upstream\celt\bands.c:1321:             ec_enc_bits(ec, sign, 1);
	movi.n	a4, 1	#,
# @OPUS@\upstream\celt\bands.c:1320:             sign = x2[0]*y2[1] - x2[1]*y2[0] < 0;
	sub	a12, a12, a2	# _442, tmp1981, tmp1984
# @OPUS@\upstream\celt\bands.c:1321:             ec_enc_bits(ec, sign, 1);
	extui	a3, a12, 31, 1	#, _442,
	mov.n	a2, a14	#, ec
	call0	ec_enc_bits		#
	movi.n	a2, -2	# tmp1989,
	movi.n	a10, 0	#,
	movltz	a10, a2, a12	#, tmp1989, _442
	movi.n	a2, -1	# tmp1992,
	xor	a2, a2, a10	#, tmp1992, tmp1988
	addi.n	a12, a10, 1	#, tmp1988,
	movi.n	a11, 0	#,
	s32i	a2, sp, 252	# %sfp,
	s32i	a12, sp, 256	# %sfp,
	s32i	a11, sp, 240	# %sfp,
	j	.L520		#
.L519:
# @OPUS@\upstream\celt\bands.c:1323:             sign = ec_dec_bits(ec, 1);
	movi.n	a3, 1	#,
	mov.n	a2, a14	#, ec
	call0	ec_dec_bits		#
	slli	a2, a2, 1	# tmp1998,,
	neg	a3, a2	# tmp1999, tmp1998
	addi.n	a3, a3, 1	# tmp2003, tmp1999,
	addi.n	a2, a2, -1	# tmp2000, tmp1998,
	slli	a2, a2, 16	# tmp2002, tmp2000,
	slli	a3, a3, 16	# tmp2004, tmp2003,
	srai	a2, a2, 16	#, tmp2002,
	srai	a3, a3, 16	#, tmp2004,
	s32i	a2, sp, 252	# %sfp,
	s32i	a3, sp, 256	# %sfp,
	j	.L520		#
.L744:
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	l32i	a12, sp, 172	# %sfp,
	movi.n	a14, 1	#,
	movi.n	a8, -1	#,
	s32i	a12, sp, 132	# %sfp,
	s32i	a15, sp, 228	# %sfp, Y
	s32i	a14, sp, 256	# %sfp,
	s32i	a8, sp, 252	# %sfp,
.L520:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i	a3, sp, 180	# %sfp,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	l32i.n	a9, sp, 56	# ctx.tf_change,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	movi.n	a2, 2	#,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	s32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	l32i.n	a10, sp, 32	# MEM[(int *)&ctx],
	l32i	a11, sp, 168	# %sfp,
	l32i	a14, sp, 152	# %sfp,
	movi.n	a12, 1	#,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i	a2, sp, 148	# %sfp,
	movi.n	a3, 0	# tmp2013,
	movi.n	a2, 0	# tmp2009,
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	l32i	a8, sp, 124	# %sfp,
	movnez	a2, a12, a11	# tmp2009,,
	movnez	a3, a12, a14	# tmp2013,,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	s32i	a10, sp, 140	# %sfp,
	and	a2, a2, a3	# _4766, tmp2009, tmp2013
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	bge	a8, a12, .L521	#,,
	l32i	a9, sp, 148	# %sfp,
	movi.n	a12, -1	# tmp2018,
	xor	a12, a12, a9	# tmp2017, tmp2018,
	extui	a3, a8, 31, 1	# tmp2022,,
	and	a12, a12, a3	# _5100, tmp2017, tmp2022
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	bnez.n	a2, .L522	# _4766,
	j	.L938		#
.L521:
	bnez.n	a2, .L524	# _4766,
	mov.n	a11, a14	# lowband,
	j	.L525		#
.L522:
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	bnez.n	a12, .L526	# _5100,
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	l32i	a10, sp, 180	# %sfp,
	blti	a10, 2, .L721	#,,
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	movi.n	a5, 2	#,
	mov.n	a2, a11	#,
	mov.n	a3, a14	#,
	mov.n	a4, a5	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i	a11, sp, 140	# %sfp,
	bnez.n	a11, .L722	#,
	l32i	a12, sp, 168	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	s32i	a11, sp, 124	# %sfp,
	s32i	a12, sp, 152	# %sfp,
	l32i	a13, sp, 180	# %sfp, B
	j	.L529		#
.L526:
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	movi.n	a5, 2	#,
	mov.n	a3, a14	#,
	mov.n	a2, a11	#,
	mov.n	a4, a5	#,
	call0	yoradio_opus_copy		#
	l32i	a14, sp, 168	# %sfp,
	s32i	a14, sp, 152	# %sfp,
	j	.L530		#
.L524:
	movi.n	a5, 2	#,
	mov.n	a2, a11	#,
	mov.n	a3, a14	#,
	mov.n	a4, a5	#,
	call0	yoradio_opus_copy		#
	l32i	a8, sp, 168	# %sfp,
	s32i	a8, sp, 152	# %sfp,
	mov.n	a11, a8	# lowband,
.L525:
	l32r	a10, .LC64	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l32r	a9, .LC57	#, tmp2968
	s32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a5, 0	# k,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mov.n	a10, a9	# tmp2973, tmp2968
	s32i	a15, sp, 276	# %sfp, Y
.L539:
# @OPUS@\upstream\celt\bands.c:1172:       if (encode)
	l32i	a12, sp, 140	# %sfp,
	beqz.n	a12, .L531	#,
# @OPUS@\upstream\celt\bands.c:1173:          haar1(X, N>>k, 1<<k);
	movi.n	a2, 1	#,
	movi.n	a14, 2	#,
	ssr	a5	# k
	sra	a7, a14	# tmp2028,
	ssl	a5	# k
	sll	a8, a2	# _1039,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a2	#
	sra	a7, a7	# N0, tmp2028
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a8, a2, .L532	# _1039,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a6, 0	# i,
	bge	a7, a2, .L953	# N0,,
	j	.L532		#
.L534:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a5	# k
	sll	a2, a11	# tmp2029, j
	slli	a2, a2, 1	# tmp2030, tmp2029,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a5	# k
	sll	a4, a13	# tmp2033, ivtmp$539
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a6	# tmp2031, tmp2030, i
	slli	a2, a2, 1	# tmp2032, tmp2031,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a4, a4, a6	# tmp2034, tmp2033, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a3, a15, a2	# _1155, iftmp$125_1368, tmp2032
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a4, a4, 1	# tmp2035, tmp2034,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a12, a3, 0	# *_1155,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a4, a15, a4	# _1165, iftmp$125_1368, tmp2035
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a14, a4, 0	# *_1165,
	l32r	a2, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a12, a12, a10	# tmp1, *_1155, tmp2973
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a14, a14, a2	# tmp2, *_1165,
	addmi	a2, a12, 0x4000	# _2461, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a12, a14, a2	# tmp2041, tmp2, _2461
	srai	a12, a12, 15	# tmp2042, tmp2041,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a14	# tmp2043, _2461, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a12, a3, 0	# *_1155, tmp2042
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2044, tmp2043,
	s16i	a2, a4, 0	# *_1165, tmp2044
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a11, a11, 1	# j, j,
	addi.n	a13, a13, 2	# ivtmp$539, ivtmp$539,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a7, a11, .L534	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a8, a6, .L535	# _1039, i,
	j	.L533		#
.L953:
	l32i	a15, sp, 132	# %sfp, iftmp$125_1368
	s32i	a11, sp, 196	# %sfp, lowband
.L533:
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a13, 1	# ivtmp$539,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a11, 0	# j,
	j	.L534		#
.L531:
# @OPUS@\upstream\celt\bands.c:1174:       if (lowband)
	beqz.n	a11, .L532	# lowband,
# @OPUS@\upstream\celt\bands.c:1175:          haar1(lowband, N>>k, 1<<k);
	movi.n	a4, 1	#,
	movi.n	a3, 2	#,
	ssr	a5	# k
	sra	a7, a3	# tmp2047,
	ssl	a5	# k
	sll	a8, a4	# _1039,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a4	#
	sra	a7, a7	# N0, tmp2047
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bge	a8, a4, .L536	# _1039,,
	j	.L532		#
.L537:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a5	# k
	sll	a2, a3	# tmp2048, j
	slli	a2, a2, 1	# tmp2049, tmp2048,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a5	# k
	sll	a13, a4	# tmp2052, ivtmp$533
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a6	# tmp2050, tmp2049, i
	slli	a2, a2, 1	# tmp2051, tmp2050,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a13, a13, a6	# tmp2053, tmp2052, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a12, a11, a2	# _1187, lowband, tmp2051
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a13, a13, 1	# tmp2054, tmp2053,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a15, a12, 0	# *_1187,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a13, a11, a13	# _1197, lowband, tmp2054
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a14, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a2, a13, 0	# *_1197,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a14, a15, a14	#, *_1187,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a15, a2, a9	# tmp2, *_1197, tmp2968
	addmi	a2, a14, 0x4000	# _1674,,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a14, a15, a2	# tmp2060, tmp2, _1674
	srai	a14, a14, 15	# tmp2061, tmp2060,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a15	# tmp2062, _1674, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a14, a12, 0	# *_1187, tmp2061
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2063, tmp2062,
	s16i	a2, a13, 0	# *_1197, tmp2063
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$533, ivtmp$533,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a3, a7, .L537	# j, N0,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a6, a8, .L538	# i, _1039,
	j	.L532		#
.L536:
	blti	a7, 1, .L532	# N0,,
.L691:
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# i,
.L538:
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a4, 1	# ivtmp$533,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	j	.L537		#
.L532:
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l32i	a12, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	srai	a2, a8, 4	# tmp2068,,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	extui	a3, a8, 0, 4	# tmp2065,,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a2, a12, a2	# tmp2069,, tmp2068
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a3, a12, a3	# tmp2066,, tmp2065
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a2, a2, 0	# bit_interleave_table, tmp2070
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a3, a3, 0	# bit_interleave_table, _1043
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	slli	a2, a2, 2	# _1047, tmp2070,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	or	a2, a3, a2	#, _1043, _1047
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	l32i	a14, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	addi.n	a5, a5, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	s32i	a2, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	bne	a14, a5, .L539	#, k,
	l32i	a9, sp, 148	# %sfp,
	l32i	a8, sp, 180	# %sfp,
	ssl	a14	#
	sll	a9, a9	#,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a10, 0	#,
	l32i	a15, sp, 276	# %sfp, Y
	ssr	a14	#
	sra	a13, a8	# B,
	s32i	a9, sp, 148	# %sfp,
	s32i	a10, sp, 120	# %sfp,
	j	.L540		#
.L938:
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	beqz.n	a12, .L724	# _5100,
.L530:
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l32r	a12, .LC57	#, tmp2978
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	movi.n	a11, 0	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a15, sp, 196	# %sfp, Y
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	l32i	a13, sp, 180	# %sfp, B
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32i	a15, sp, 148	# %sfp, N_B
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mov.n	a14, a12	# tmp2980, tmp2978
.L548:
# @OPUS@\upstream\celt\bands.c:1184:       if (encode)
	l32i	a6, sp, 140	# %sfp,
	srai	a15, a15, 1	# N_B, N_B,
	slli	a8, a13, 1	# B, B,
	beqz.n	a6, .L541	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bgei	a13, 1, .L939	# B,,
	j	.L542		#
.L939:
	l32i	a3, sp, 132	# %sfp, ivtmp$562
	add.n	a7, a3, a8	# _5167, ivtmp$562, B
	beqi	a15, 1, .L543	# N_B,,
	j	.L542		#
.L543:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a4, a3, 0	# MEM[base: _5177, offset: 0B],
	add.n	a6, a8, a3	# _5175, B, ivtmp$562
	l32r	a9, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a2, a6, 0	# MEM[base: _5175, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a4, a4, a9	# tmp1, MEM[base: _5177, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a5, a2, a14	# tmp2, MEM[base: _5175, offset: 0B], tmp2980
	addmi	a2, a4, 0x4000	# _2452, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a4, a5, a2	# tmp2076, tmp2, _2452
	srai	a4, a4, 15	# tmp2077, tmp2076,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a5	# tmp2078, _2452, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a4, a3, 0	# MEM[base: _5177, offset: 0B], tmp2077
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2079, tmp2078,
	s16i	a2, a6, 0	# MEM[base: _5175, offset: 0B], tmp2079
	addi.n	a3, a3, 2	# ivtmp$562, ivtmp$562,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bne	a7, a3, .L543	# _5167, ivtmp$562,
	j	.L941		#
.L541:
# @OPUS@\upstream\celt\bands.c:1186:       if (lowband)
	l32i	a10, sp, 152	# %sfp,
	beqz.n	a10, .L542	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	bgei	a13, 1, .L545	# B,,
	j	.L542		#
.L546:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a7, a3, 0	# MEM[base: _5209, offset: 0B],
	l32r	a10, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a2, a4, 0	# MEM[base: _5207, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a7, a7, a10	# tmp1, MEM[base: _5209, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a2, a12	# tmp2, MEM[base: _5207, offset: 0B], tmp2978
	addmi	a2, a7, 0x4000	# _460, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a2, a10	# tmp2085, _460, tmp2
	srai	a7, a7, 15	# tmp2086, tmp2085,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2087, _460, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a3, 0	# MEM[base: _5209, offset: 0B], tmp2086
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2088, tmp2087,
	s16i	a2, a4, 0	# MEM[base: _5207, offset: 0B], tmp2088
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a3, a3, a11	# ivtmp$547, ivtmp$547, _5223
	add.n	a4, a4, a11	# ivtmp$548, ivtmp$548, _5223
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bnei	a6, 1, .L546	# j,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a9, a9, 1	# i, i,
	addi.n	a5, a5, 2	# ivtmp$552, ivtmp$552,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a9, a13, .L547	# i, B,
	j	.L542		#
.L545:
	bnei	a15, 1, .L542	# N_B,,
.L692:
	l32i	a5, sp, 152	# %sfp, ivtmp$552
	slli	a11, a13, 2	# _5223, B,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a9, 0	# i,
.L547:
	add.n	a4, a8, a5	# ivtmp$548, B, ivtmp$552
# @OPUS@\upstream\celt\bands.c:1163:       OPUS_COPY(lowband_scratch, lowband, N);
	mov.n	a3, a5	# ivtmp$547, ivtmp$552
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	j	.L546		#
.L542:
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	l32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	l32i	a11, sp, 120	# %sfp,
	l32i	a9, sp, 124	# %sfp,
	addi.n	a11, a11, 1	#,,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	ssl	a13	# B
	sll	a13, a10	# _1055,
	add.n	a2, a11, a9	# _5160,,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	or	a10, a10, a13	#,, _1055
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	movi.n	a11, 1	#,
	xor	a3, a15, a11	# tmp2090, N_B,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	extui	a2, a2, 31, 1	# tmp2094, _5160,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	s32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1189:       B <<= 1;
	mov.n	a13, a8	# B, B
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	bany	a3, a2, .L548	# tmp2090, tmp2094,
	movi.n	a12, 0	#,
	s32i	a15, sp, 148	# %sfp, N_B
	s32i	a12, sp, 124	# %sfp,
	l32i	a15, sp, 196	# %sfp, Y
	j	.L540		#
.L724:
	movi.n	a14, 0	#,
	l32i	a13, sp, 180	# %sfp, B
	s32i	a14, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a12, sp, 120	# %sfp, _5100
.L540:
# @OPUS@\upstream\celt\bands.c:1198:    if (B0>1)
	bgei	a13, 2, .L549	# B,,
	l32i.n	a6, sp, 32	# MEM[(int *)&ctx],
	s32i	a6, sp, 140	# %sfp,
	j	.L550		#
.L721:
	mov.n	a13, a10	# B,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a12, sp, 120	# %sfp, _5100
# @OPUS@\upstream\celt\bands.c:1161:    if (lowband_scratch && lowband && (recombine || ((N_B&1) == 0 && tf_change<0) || B0>1))
	s32i	a12, sp, 124	# %sfp, _5100
	j	.L550		#
.L549:
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i	a8, sp, 140	# %sfp,
	beqz.n	a8, .L551	#,
	j	.L528		#
.L722:
	l32i	a9, sp, 168	# %sfp,
	l32i	a13, sp, 180	# %sfp, B
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a12, sp, 120	# %sfp, _5100
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	s32i	a9, sp, 152	# %sfp,
	s32i	a12, sp, 124	# %sfp, _5100
.L528:
# @OPUS@\upstream\celt\bands.c:1201:          deinterleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a10, sp, 124	# %sfp,
	l32i	a11, sp, 148	# %sfp,
	l32i	a5, sp, 312	# %sfp,
	l32i	a2, sp, 132	# %sfp,
	ssl	a10	#
	sll	a4, a13	#, B
	ssr	a10	#
	sra	a3, a11	#,
	call0	deinterleave_hadamard		#
.L551:
	l32i.n	a12, sp, 32	# MEM[(int *)&ctx],
# @OPUS@\upstream\celt\bands.c:1202:       if (lowband)
	l32i	a14, sp, 152	# %sfp,
	s32i	a12, sp, 140	# %sfp,
	beqz.n	a14, .L550	#,
.L529:
# @OPUS@\upstream\celt\bands.c:1203:          deinterleave_hadamard(lowband, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a8, sp, 124	# %sfp,
	l32i	a9, sp, 148	# %sfp,
	l32i	a5, sp, 312	# %sfp,
	l32i	a2, sp, 152	# %sfp,
	ssl	a8	#
	sll	a4, a13	#, B
	ssr	a8	#
	sra	a3, a9	#,
	call0	deinterleave_hadamard		#
	l32i.n	a10, sp, 32	# MEM[(int *)&ctx],
	s32i	a10, sp, 140	# %sfp,
.L550:
# @OPUS@\upstream\celt\bands.c:981:    m = ctx->m;
	l32i.n	a3, sp, 40	# ctx.m, m
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i	a11, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i.n	a4, a3, 8	# m_1277->nbEBands, m_1277->nbEBands
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	addi.n	a2, a11, 1	# tmp2102,,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	mull	a2, a2, a4	# tmp2103, tmp2102, m_1277->nbEBands
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i.n	a5, sp, 44	# ctx.i, ctx.i
	l32i	a4, a3, 88	# m_1277->cache.index, m_1277->cache.index
	add.n	a2, a2, a5	# tmp2105, tmp2103, ctx.i
	slli	a2, a2, 1	# tmp2108, tmp2105,
	add.n	a2, a4, a2	# tmp2109, m_1277->cache.index, tmp2108
	l16si	a2, a2, 0	# *_1289, _1291
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	l32i	a4, a3, 92	# m_1277->cache.bits, _1281
# @OPUS@\upstream\celt\rate.h:64:    bits--;
	l32i	a12, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:987:    cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];
	add.n	a2, a4, a2	# tmp2727, _1281, _1291
# @OPUS@\upstream\celt\rate.h:63:    hi = cache[0];
	l8ui	a6, a2, 0	# *cache_1292, hi
# @OPUS@\upstream\celt\rate.h:64:    bits--;
	addi.n	a3, a12, -1	# bits,,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a5, a6, 1	# tmp2112, hi,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a5, a5, 1	# mid, tmp2112,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a4, a2, a5	# tmp2113, tmp2727, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a4, a4, 0	# *_2222, *_2222
# @OPUS@\upstream\celt\bands.c:983:    spread = ctx->spread;
	l32i.n	a11, sp, 52	# ctx.spread, spread
# @OPUS@\upstream\celt\bands.c:984:    ec = ctx->ec;
	l32i.n	a10, sp, 60	# ctx.ec, ec
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a4, a3, .L725	# *_2222, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a5	# q, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a5, a6, a5	# mid, hi, mid
	j	.L552		#
.L725:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a6, a5	# hi, mid
# @OPUS@\upstream\celt\rate.h:62:    lo = 0;
	movi.n	a4, 0	# q,
.L552:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a5, a5, 1	# tmp2115, mid,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a5, a5, 1	# hi, tmp2115,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a7, a2, a5	# tmp2116, tmp2727, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a7, a7, 0	# *_2234, *_2234
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a7, a3, .L553	# *_2234, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a5	# q, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a5, a6	# hi, hi
.L553:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a6, a5, a4	# tmp2118, hi, q
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a6, a6, 1	# tmp2119, tmp2118,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a6, a6, 1	# hi, tmp2119,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a7, a2, a6	# tmp2120, tmp2727, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a7, a7, 0	# *_2145, *_2145
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a7, a3, .L554	# *_2145, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a6	# q, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a6, a5	# hi, hi
.L554:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a5, a4, a6	# tmp2122, q, hi
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a5, a5, 1	# tmp2123, tmp2122,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a5, a5, 1	# mid, tmp2123,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a7, a2, a5	# tmp2124, tmp2727, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a7, a7, 0	# *_2159, *_2159
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a7, a3, .L555	# *_2159, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a5	# q, mid
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a5, a6	# mid, hi
.L555:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a8, a4, a5	# tmp2126, q, mid
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a8, a8, 1	# tmp2127, tmp2126,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a8, a8, 1	# hi, tmp2127,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a6, a2, a8	# tmp2128, tmp2727, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a6, a6, 0	# *_2171, *_2171
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a6, a3, .L556	# *_2171, bits,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a8	# q, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a8, a5	# hi, mid
.L556:
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	add.n	a5, a8, a4	# tmp2130, hi, q
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	addi.n	a5, a5, 1	# tmp2131, tmp2130,
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	srai	a5, a5, 1	# hi, tmp2131,
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	add.n	a6, a2, a5	# tmp2132, tmp2727, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	l8ui	a6, a6, 0	# *_1877, _1849
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a7, a5	# mid$228_1847, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	bge	a6, a3, .L557	# _1849, bits,
	add.n	a4, a2, a8	# tmp2133, tmp2727, mid$228_1847
	l8ui	a6, a4, 0	# *_4858, _1849
	mov.n	a7, a8	# mid$228_1847, hi
# @OPUS@\upstream\celt\rate.h:67:       int mid = (lo+hi+1)>>1;
	mov.n	a4, a5	# q, hi
# @OPUS@\upstream\celt\rate.h:69:       if ((int)cache[mid] >= bits)
	mov.n	a5, a8	# hi, mid$228_1847
.L557:
	sub	a6, a6, a3	# _4877, _1849, bits
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	beqz.n	a4, .L558	# q,
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	add.n	a8, a2, a4	# tmp2134, tmp2727, q
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	l8ui	a9, a8, 0	# *_1504, *_1504
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	mov.n	a8, a4	# lo$230_1503, q
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	sub	a3, a3, a9	# tmp2136, bits, *_1504
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	bge	a6, a3, .L559	# _4877, tmp2136,
.L671:
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	bnez.n	a5, .L726	# hi,
	j	.L560		#
.L561:
# @OPUS@\upstream\celt\bands.c:1063:          ctx->remaining_bits += curr_bits;
	add.n	a3, a3, a5	# _1411, _384, curr_bits
# @OPUS@\upstream\celt\bands.c:1064:          q--;
	addi.n	a4, a4, -1	# q, q,
# @OPUS@\upstream\celt\bands.c:1063:          ctx->remaining_bits += curr_bits;
	s32i	a3, sp, 64	# ctx.remaining_bits, _1411
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	add.n	a5, a2, a4	# tmp2137, tmp2727, q
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	beqz.n	a4, .L560	# q,
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	l8ui	a5, a5, 0	# MEM[base: _5231, offset: 0B], MEM[base: _5231, offset: 0B]
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	addi.n	a5, a5, 1	# curr_bits, MEM[base: _5231, offset: 0B],
# @OPUS@\upstream\celt\bands.c:1066:          ctx->remaining_bits -= curr_bits;
	sub	a3, a3, a5	# _384, _1411, curr_bits
	s32i	a3, sp, 64	# ctx.remaining_bits, _384
# @OPUS@\upstream\celt\bands.c:1061:       while (ctx->remaining_bits < 0 && q > 0)
	bltz	a3, .L561	# _384,
.L698:
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	blti	a4, 8, .L562	# q,,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	extui	a2, a4, 0, 3	# tmp2139, q,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	srai	a4, a4, 3	# tmp2141, q,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	addi.n	a2, a2, 8	# tmp2140, tmp2139,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	addi.n	a4, a4, -1	# tmp2142, tmp2141,
# @OPUS@\upstream\celt\rate.h:50:    return i<8 ? i : (8 + (i&7)) << ((i>>3)-1);
	ssl	a4	# tmp2142
	sll	a4, a2	# q, tmp2140
.L562:
# @OPUS@\upstream\celt\bands.c:1074:          if (encode)
	l32i	a14, sp, 140	# %sfp,
	beqz.n	a14, .L563	#,
# @OPUS@\upstream\celt\bands.c:1076:             cm = alg_quant(X, N, K, spread, B, ec, gain, ctx->resynth, ctx->arch);
	l32i	a2, sp, 76	# ctx.arch, ctx.arch
	l32r	a8, .LC51	#,
	s32i.n	a2, sp, 8	#, ctx.arch
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	s32i.n	a8, sp, 0	#,
	s32i.n	a2, sp, 4	#, ctx.resynth
	l32i	a2, sp, 132	# %sfp,
	mov.n	a7, a10	#, ec
	mov.n	a6, a13	#, B
	mov.n	a5, a11	#, spread
	movi.n	a3, 2	#,
	call0	alg_quant		#
	s32i	a2, sp, 112	# %sfp,
	j	.L564		#
.L563:
# @OPUS@\upstream\celt\bands.c:1078:             cm = alg_unquant(X, N, K, spread, B, ec, gain);
	l32r	a9, .LC51	#,
	l32i	a2, sp, 132	# %sfp,
	mov.n	a7, a10	#, ec
	s32i.n	a9, sp, 0	#,
	mov.n	a6, a13	#, B
	mov.n	a5, a11	#, spread
	movi.n	a3, 2	#,
	call0	alg_unquant		#
	s32i	a2, sp, 112	# %sfp,
	j	.L564		#
.L560:
# @OPUS@\upstream\celt\bands.c:1083:          if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	beqz.n	a2, .L727	# ctx.resynth,
# @OPUS@\upstream\celt\bands.c:1088:             cm_mask = (unsigned)(1UL<<B)-1;
	movi.n	a10, 1	#,
# @OPUS@\upstream\celt\bands.c:1089:             fill &= cm_mask;
	l32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1088:             cm_mask = (unsigned)(1UL<<B)-1;
	ssl	a13	# B
	sll	a4, a10	# tmp2149,
# @OPUS@\upstream\celt\bands.c:1088:             cm_mask = (unsigned)(1UL<<B)-1;
	addi.n	a4, a4, -1	# cm_mask, tmp2149,
# @OPUS@\upstream\celt\bands.c:1089:             fill &= cm_mask;
	and	a11, a11, a4	#,, cm_mask
	s32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1090:             if (!fill)
	bnez.n	a11, .L566	#,
# @OPUS@\upstream\celt\bands.c:1092:                OPUS_CLEAR(X, N);
	movi.n	a4, 2	#,
	l32i	a2, sp, 132	# %sfp,
	mov.n	a3, a4	#,
	call0	yoradio_opus_clear		#
	j	.L564		#
.L566:
	l32r	a3, .LC65	#, tmp2152
	l32i	a2, sp, 72	# ctx.seed, ctx.seed
	l32r	a5, .LC66	#, tmp2153
	mull	a2, a2, a3	# tmp2150, ctx.seed, tmp2152
# @OPUS@\upstream\celt\bands.c:1094:                if (lowband == NULL)
	l32i	a12, sp, 152	# %sfp,
	add.n	a2, a2, a5	# _5002, tmp2150, tmp2153
	mull	a3, a2, a3	# tmp2154, _5002, tmp2152
	add.n	a3, a3, a5	# _5004, tmp2154, tmp2153
	beqz.n	a12, .L567	#,
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	l32r	a7, .LC67	#, tmp2720
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	movi.n	a5, -4	# tmp2774,
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	l16ui	a6, a12, 0	# *lowband_5005,
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	and	a2, a2, a7	# tmp2157, _5002, tmp2720
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	movi.n	a4, 4	# tmp2773,
	mov.n	a14, a5	#, tmp2774
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	l32i	a8, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	movnez	a14, a4, a2	#, tmp2773, tmp2157
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	add.n	a2, a14, a6	# tmp2160, iftmp$223_2585, *lowband_5005
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	s16i	a2, a8, 0	# *iftmp$125_1368, tmp2160
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	l16ui	a2, a12, 2	# MEM[(celt_norm *)lowband_5005 + 2B],
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	and	a7, a3, a7	# tmp2161, _5004, tmp2720
# @OPUS@\upstream\celt\bands.c:1111:                      tmp = (ctx->seed)&0x8000 ? tmp : -tmp;
	moveqz	a4, a5, a7	# iftmp$223_2554, tmp2774, tmp2161
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	add.n	a2, a4, a2	# tmp2164, iftmp$223_2554, MEM[(celt_norm *)lowband_5005 + 2B]
# @OPUS@\upstream\celt\bands.c:1108:                      ctx->seed = celt_lcg_rand(ctx->seed);
	s32i	a3, sp, 72	# ctx.seed, _5004
# @OPUS@\upstream\celt\bands.c:1112:                      X[j] = lowband[j]+tmp;
	s16i	a2, a8, 2	# MEM[(celt_norm *)iftmp$125_1368 + 2B], tmp2164
	mov.n	a2, a8	#,
	j	.L570		#
.L567:
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	l32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	srai	a2, a2, 20	# tmp2165, _5002,
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	s16i	a2, a9, 0	# *iftmp$125_1368, tmp2165
# @OPUS@\upstream\celt\bands.c:1099:                      ctx->seed = celt_lcg_rand(ctx->seed);
	s32i	a3, sp, 72	# ctx.seed, _5004
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	srai	a3, a3, 20	# tmp2166, _5004,
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	s16i	a3, a9, 2	# MEM[(celt_norm *)iftmp$125_1368 + 2B], tmp2166
# @OPUS@\upstream\celt\bands.c:1100:                      X[j] = (celt_norm)((opus_int32)ctx->seed>>20);
	s32i	a4, sp, 112	# %sfp, cm_mask
	mov.n	a2, a9	#,
.L570:
# @OPUS@\upstream\celt\bands.c:1116:                renormalise_vector(X, N, gain, ctx->arch);
	l32i	a5, sp, 76	# ctx.arch,
	l32r	a4, .LC51	#,
	movi.n	a3, 2	#,
	call0	renormalise_vector		#
.L564:
	l32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	extui	a12, a10, 0, 8	# prephitmp_4270,
	beqz.n	a2, .L565	# ctx.resynth,
.L571:
# @OPUS@\upstream\celt\bands.c:1212:       if (B0>1)
	blti	a13, 2, .L572	# B,,
# @OPUS@\upstream\celt\bands.c:1213:          interleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a14, sp, 124	# %sfp,
	l32i	a11, sp, 148	# %sfp,
	ssl	a14	#
	sll	a6, a13	# _1075, B
	ssr	a14	#
	sra	a12, a11	# _1074,
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	mull	a8, a12, a6	#, _1074, _1075
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a6, sp, 344	#,
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	s32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 92	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	l32i	a2, sp, 152	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a3, sp, 96	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	mov.n	a14, a2	# tmp,
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a6, sp, 344	#,
	bnez.n	a9, .L573	#,
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	blti	a6, 1, .L574	# _1075,,
	blti	a12, 1, .L574	# _1074,,
	slli	a5, a12, 1	# tmp2170, _1074,
	slli	a11, a12, 2	# tmp2191, _1074,
	l32i	a12, sp, 132	# %sfp,
	mov.n	a10, a5	# tmp2173, tmp2170
	slli	a6, a6, 1	# _5240, _1075,
	mov.n	a7, a2	# ivtmp$522, tmp
	add.n	a5, a12, a5	# ivtmp$523,, tmp2170
	add.n	a9, a6, a2	# _5238, _5240, tmp
	neg	a10, a10	# tmp2174, tmp2173
	neg	a11, a11	# tmp2192, tmp2191
	j	.L575		#
.L573:
# @OPUS@\upstream\celt\bands.c:625:       const int *ordery = ordery_table+stride-2;
	l32r	a2, .LC68	#, tmp2175
	add.n	a7, a6, a2	# _1522, _1075, tmp2175
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	blti	a6, 1, .L574	# _1075,,
	blti	a12, 1, .L574	# _1074,,
	l32r	a3, .LC69	#, tmp2177
	slli	a9, a6, 3	# tmp2180, _1075,
	slli	a7, a7, 2	# tmp2176, _1522,
	addi	a2, a3, -8	# tmp2178, tmp2177,
	add.n	a7, a7, a3	# ivtmp$512, tmp2176, tmp2177
	mov.n	a8, a14	# ivtmp$514, tmp
	add.n	a9, a2, a9	# _5275, tmp2178, tmp2180
	slli	a6, a6, 1	# _5318, _1075,
	l32i	a4, sp, 132	# %sfp, iftmp$125_1368
	j	.L576		#
.L577:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l16si	a5, a2, 0	# MEM[base: _5304, offset: 0B], _1540
	addi.n	a2, a2, 2	# ivtmp$508, ivtmp$508,
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	s16i	a5, a3, 0	# MEM[base: _5303, offset: 0B], _1540
	add.n	a3, a3, a6	# ivtmp$509, ivtmp$509, _5318
# @OPUS@\upstream\celt\bands.c:627:          for (j=0;j<N0;j++)
	bne	a10, a2, .L577	# _5297, ivtmp$508,
	addi.n	a7, a7, 4	# ivtmp$512, ivtmp$512,
	addi.n	a8, a8, 2	# ivtmp$514, ivtmp$514,
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	beq	a9, a7, .L574	# _5275, ivtmp$512,
.L576:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l32i.n	a2, a7, 0	# MEM[base: _5280, offset: 0B], MEM[base: _5280, offset: 0B]
	mov.n	a3, a8	# ivtmp$509, ivtmp$514
	mull	a2, a12, a2	# _1788, _1074, MEM[base: _5280, offset: 0B]
	add.n	a10, a12, a2	# tmp2185, _1074, _1788
	slli	a10, a10, 1	# tmp2186, tmp2185,
	slli	a2, a2, 1	# tmp2184, _1788,
	add.n	a2, a4, a2	# ivtmp$508, iftmp$125_1368, tmp2184
	add.n	a10, a4, a10	# _5297, iftmp$125_1368, tmp2186
	j	.L577		#
.L578:
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	l16si	a4, a2, 0	# MEM[base: _5260, offset: 0B], _1555
	addi.n	a2, a2, 2	# ivtmp$517, ivtmp$517,
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	s16i	a4, a3, 0	# MEM[base: _5259, offset: 0B], _1555
	add.n	a3, a3, a6	# ivtmp$518, ivtmp$518, _5240
# @OPUS@\upstream\celt\bands.c:631:          for (j=0;j<N0;j++)
	bne	a5, a2, .L578	# ivtmp$523, ivtmp$517,
	addi.n	a7, a7, 2	# ivtmp$522, ivtmp$522,
	sub	a5, a8, a11	# ivtmp$523, _5235, tmp2192
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	beq	a9, a7, .L574	# _5238, ivtmp$522,
.L575:
	add.n	a8, a10, a5	# _5235, tmp2174, ivtmp$523
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	mov.n	a3, a7	# ivtmp$518, ivtmp$522
	mov.n	a2, a8	# ivtmp$517, _5235
	j	.L578		#
.L574:
# @OPUS@\upstream\celt\bands.c:634:    OPUS_COPY(X, tmp, N);
	l32i	a2, sp, 132	# %sfp,
	l32i	a4, sp, 152	# %sfp,
	mov.n	a3, a14	#, tmp
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:635:    RESTORE_STACK;
	l32i	a2, sp, 92	# _saved_stack,
	l32i	a3, sp, 96	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
	j	.L572		#
.L958:
	s32i	a15, sp, 152	# %sfp, Y
	mov.n	a15, a2	# k, k
.L582:
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	l32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1220:          B >>= 1;
	srai	a13, a13, 1	# B, B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	ssr	a13	# B
	srl	a2, a9	# _1081,
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	slli	a8, a8, 1	#,,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	or	a9, a9, a2	#,, _1081
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	s32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	s32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	srai	a10, a8, 1	# N0,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a13, 1, .L579	# B,,
	blti	a10, 1, .L579	# N0,,
	l32i	a3, sp, 132	# %sfp, ivtmp$501
	slli	a11, a13, 1	# _2572, B,
	add.n	a12, a11, a3	# _1466, _2572, ivtmp$501
	slli	a9, a13, 2	# _5325, B,
	j	.L580		#
.L581:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16si	a7, a4, 0	# MEM[base: _5339, offset: 0B], tmp2197
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16si	a2, a5, 0	# MEM[base: _290, offset: 0B], tmp2194
	l32r	a11, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mull	a7, a7, a14	# tmp1, tmp2197, tmp2963
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mull	a8, a2, a11	# tmp2, tmp2194,
	addmi	a2, a7, 0x4000	# _1667, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a8, a2	# tmp2198, tmp2, _1667
	srai	a7, a7, 15	# tmp2199, tmp2198,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp2200, _1667, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a4, 0	# MEM[base: _5339, offset: 0B], tmp2199
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2201, tmp2200,
	s16i	a2, a5, 0	# MEM[base: _290, offset: 0B], tmp2201
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$496, ivtmp$496, _5325
	add.n	a5, a5, a9	# ivtmp$497, ivtmp$497, _5325
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a10, a6, .L581	# N0, j,
	addi.n	a3, a3, 2	# ivtmp$501, ivtmp$501,
	l32i	a11, sp, 140	# %sfp, _2572
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a12, a3, .L579	# _1466, ivtmp$501,
.L580:
	add.n	a5, a3, a11	# ivtmp$497, ivtmp$501, _2572
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	mov.n	a4, a3	# ivtmp$496, ivtmp$501
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	s32i	a11, sp, 140	# %sfp, _2572
	j	.L581		#
.L579:
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i	a12, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	addi.n	a15, a15, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bne	a15, a12, .L582	# k,,
	l32i	a15, sp, 152	# %sfp, Y
	j	.L583		#
.L572:
	l32i	a8, sp, 120	# %sfp,
	movi.n	a2, 0	# k,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a14, .LC57	#, tmp2963
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bgei	a8, 1, .L958	#,,
.L583:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a9, sp, 124	# %sfp,
	beqz.n	a9, .L584	#,
	l32r	a10, .LC70	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a15, sp, 120	# %sfp, Y
	l32r	a14, .LC57	#, tmp2959
	l32i	a15, sp, 112	# %sfp, cm
	l32i	a12, sp, 132	# %sfp, iftmp$125_1368
	s32i	a10, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a9, 0	# k,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a13, sp, 152	# %sfp, B
.L588:
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l32i	a11, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	movi.n	a3, 1	#,
	movi.n	a2, 2	#,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	add.n	a15, a11, a15	# tmp2203,, cm
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	ssl	a9	# k
	sll	a13, a3	# _1091,
	ssr	a9	# k
	sra	a11, a2	# tmp2206,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l8ui	a15, a15, 0	# bit_deinterleave_table, cm
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a3	#
	sra	a11, a11	# N0, tmp2206
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a13, a3, .L585	# _1091,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a11, a3, .L586	# N0,,
	j	.L585		#
.L587:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a9	# k
	sll	a2, a3	# tmp2207, j
	slli	a2, a2, 1	# tmp2208, tmp2207,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a9	# k
	sll	a7, a4	# tmp2211, ivtmp$488
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp2209, tmp2208, i
	slli	a2, a2, 1	# tmp2210, tmp2209,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a7, a5	# tmp2212, tmp2211, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a12, a2	# _1598, iftmp$125_1368, tmp2210
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a7, a7, 1	# tmp2213, tmp2212,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a8, a6, 0	# *_1598,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a12, a7	# _1608, iftmp$125_1368, tmp2213
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a7, 0	# *_1608,
	l32r	a2, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a8, a8, a14	# tmp1, *_1598, tmp2959
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a2	# tmp2, *_1608,
	addmi	a2, a8, 0x4000	# _1378, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a8, a2, a10	# tmp2219, _1378, tmp2
	srai	a8, a8, 15	# tmp2220, tmp2219,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2221, _1378, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a8, a6, 0	# *_1598, tmp2220
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2222, tmp2221,
	s16i	a2, a7, 0	# *_1608, tmp2222
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$488, ivtmp$488,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a11, a3, .L587	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a13, a5, .L585	# _1091, i,
.L586:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$488,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	j	.L587		#
.L585:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a8, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	addi.n	a9, a9, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	bne	a9, a8, .L588	# k,,
	s32i	a15, sp, 112	# %sfp, cm
	l32i	a13, sp, 152	# %sfp, B
	l32i	a15, sp, 120	# %sfp, Y
.L584:
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	l32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1238:       if (lowband_out)
	l32i	a10, sp, 236	# %sfp,
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	ssl	a9	#
	sll	a12, a13	# B, B
# @OPUS@\upstream\celt\bands.c:1238:       if (lowband_out)
	beqz.n	a10, .L589	#,
# @OPUS@\upstream\celt\bands.c:1242:          n = celt_sqrt(SHL32(EXTEND32(N0),22));
	l32r	a2, .LC71	#,
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	l32i	a11, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:1242:          n = celt_sqrt(SHL32(EXTEND32(N0),22));
	slli	a2, a2, 16	# tmp2224,,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	l16ui	a3, a11, 0	# *iftmp$125_1368,
# @OPUS@\upstream\celt\bands.c:1242:          n = celt_sqrt(SHL32(EXTEND32(N0),22));
	srai	a4, a2, 16	# n, tmp2224,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	mul16s	a3, a3, a4	# tmp2225, *iftmp$125_1368, n
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	l32i	a14, sp, 236	# %sfp,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	srai	a3, a3, 15	# tmp2227, tmp2225,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	s16i	a3, a14, 0	# *iftmp$110_256, tmp2227
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	l16ui	a2, a11, 2	# MEM[(celt_norm *)iftmp$125_1368 + 2B],
	mul16s	a2, a2, a4	# tmp2228, MEM[(celt_norm *)iftmp$125_1368 + 2B], n
	srai	a2, a2, 15	# tmp2230, tmp2228,
# @OPUS@\upstream\celt\bands.c:1244:             lowband_out[j] = MULT16_16_Q15(n,X[j]);
	s16i	a2, a14, 2	# MEM[(celt_norm *)iftmp$110_256 + 2B], tmp2230
.L589:
# @OPUS@\upstream\celt\bands.c:1333:       y2[0] = -sign*x2[1];
	l32i	a8, sp, 132	# %sfp,
	l32i	a9, sp, 252	# %sfp,
	l16ui	a3, a8, 2	# MEM[(celt_norm *)iftmp$125_1368 + 2B],
	l32i	a11, sp, 228	# %sfp,
	mul16s	a3, a3, a9	# tmp2235, MEM[(celt_norm *)iftmp$125_1368 + 2B],
	l32i.n	a2, sp, 36	# ctx.resynth, pretmp_4878
	s16i	a3, a11, 0	# *iftmp$126_1883, tmp2235
# @OPUS@\upstream\celt\bands.c:1334:       y2[1] = sign*x2[0];
	l16ui	a3, a8, 0	# *iftmp$125_1368,
	l32i	a14, sp, 256	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	movi.n	a10, 1	#,
	ssl	a12	# B
	sll	a12, a10	# tmp2232,
# @OPUS@\upstream\celt\bands.c:1334:       y2[1] = sign*x2[0];
	mul16s	a3, a3, a14	# tmp2237, *iftmp$125_1368,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	l32i	a6, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	addi.n	a12, a12, -1	# tmp2233, tmp2232,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	and	a12, a12, a6	# cm, tmp2233,
# @OPUS@\upstream\celt\bands.c:1334:       y2[1] = sign*x2[0];
	s16i	a3, a11, 2	# MEM[(celt_norm *)iftmp$126_1883 + 2B], tmp2237
	extui	a12, a12, 0, 8	# prephitmp_4270, cm
# @OPUS@\upstream\celt\bands.c:1335:       if (ctx->resynth)
	beqz.n	a2, .L481	# pretmp_4878,
# @OPUS@\upstream\celt\bands.c:1338:          X[0] = MULT16_16_Q15(mid, X[0]);
	l32i	a8, sp, 172	# %sfp,
	l32i	a9, sp, 272	# %sfp,
	l16si	a3, a8, 0	# *X_233, tmp2239
# @OPUS@\upstream\celt\bands.c:1339:          X[1] = MULT16_16_Q15(mid, X[1]);
	l16si	a2, a8, 2	# MEM[(celt_norm *)X_233 + 2B], tmp2244
# @OPUS@\upstream\celt\bands.c:1338:          X[0] = MULT16_16_Q15(mid, X[0]);
	mull	a3, a3, a9	# tmp2242, tmp2239,
# @OPUS@\upstream\celt\bands.c:1339:          X[1] = MULT16_16_Q15(mid, X[1]);
	mull	a2, a2, a9	# tmp2247, tmp2244,
# @OPUS@\upstream\celt\bands.c:1338:          X[0] = MULT16_16_Q15(mid, X[0]);
	srai	a3, a3, 15	# tmp2243, tmp2242,
# @OPUS@\upstream\celt\bands.c:1339:          X[1] = MULT16_16_Q15(mid, X[1]);
	srai	a2, a2, 15	# tmp2248, tmp2247,
# @OPUS@\upstream\celt\bands.c:1338:          X[0] = MULT16_16_Q15(mid, X[0]);
	s16i	a3, a8, 0	# *X_233, tmp2243
# @OPUS@\upstream\celt\bands.c:1339:          X[1] = MULT16_16_Q15(mid, X[1]);
	s16i	a2, a8, 2	# MEM[(celt_norm *)X_233 + 2B], tmp2248
# @OPUS@\upstream\celt\bands.c:1340:          Y[0] = MULT16_16_Q15(side, Y[0]);
	l16si	a2, a15, 0	# *Y_235, tmp2249
	l32i	a10, sp, 216	# %sfp,
# @OPUS@\upstream\celt\bands.c:1341:          Y[1] = MULT16_16_Q15(side, Y[1]);
	l16si	a3, a15, 2	# MEM[(celt_norm *)Y_235 + 2B], tmp2255
# @OPUS@\upstream\celt\bands.c:1340:          Y[0] = MULT16_16_Q15(side, Y[0]);
	mull	a2, a2, a10	# tmp2252, tmp2249,
# @OPUS@\upstream\celt\bands.c:1341:          Y[1] = MULT16_16_Q15(side, Y[1]);
	mull	a3, a3, a10	# tmp2258, tmp2255,
# @OPUS@\upstream\celt\bands.c:1340:          Y[0] = MULT16_16_Q15(side, Y[0]);
	slli	a2, a2, 1	# tmp2254, tmp2252,
	srai	a2, a2, 16	# _476, tmp2254,
# @OPUS@\upstream\celt\bands.c:1341:          Y[1] = MULT16_16_Q15(side, Y[1]);
	srai	a3, a3, 15	# tmp2259, tmp2258,
# @OPUS@\upstream\celt\bands.c:1341:          Y[1] = MULT16_16_Q15(side, Y[1]);
	s16i	a3, a15, 2	# MEM[(celt_norm *)Y_235 + 2B], tmp2259
# @OPUS@\upstream\celt\bands.c:1340:          Y[0] = MULT16_16_Q15(side, Y[0]);
	s16i	a2, a15, 0	# *Y_235, _476
# @OPUS@\upstream\celt\bands.c:1342:          tmp = X[0];
	l16si	a3, a8, 0	# *X_233, tmp
# @OPUS@\upstream\celt\bands.c:1343:          X[0] = SUB16(tmp,Y[0]);
	sub	a2, a3, a2	# tmp2262, tmp, _476
# @OPUS@\upstream\celt\bands.c:1343:          X[0] = SUB16(tmp,Y[0]);
	s16i	a2, a8, 0	# *X_233, tmp2262
# @OPUS@\upstream\celt\bands.c:1344:          Y[0] = ADD16(tmp,Y[0]);
	l16ui	a2, a15, 0	# *Y_235,
# @OPUS@\upstream\celt\bands.c:1346:          X[1] = SUB16(tmp,Y[1]);
	l16ui	a4, a15, 2	# MEM[(celt_norm *)Y_235 + 2B],
# @OPUS@\upstream\celt\bands.c:1344:          Y[0] = ADD16(tmp,Y[0]);
	add.n	a3, a3, a2	# tmp2264, tmp, *Y_235
# @OPUS@\upstream\celt\bands.c:1344:          Y[0] = ADD16(tmp,Y[0]);
	s16i	a3, a15, 0	# *Y_235, tmp2264
# @OPUS@\upstream\celt\bands.c:1345:          tmp = X[1];
	l16si	a2, a8, 2	# MEM[(celt_norm *)X_233 + 2B], tmp
# @OPUS@\upstream\celt\bands.c:1346:          X[1] = SUB16(tmp,Y[1]);
	sub	a3, a2, a4	# tmp2268, tmp, MEM[(celt_norm *)Y_235 + 2B]
# @OPUS@\upstream\celt\bands.c:1346:          X[1] = SUB16(tmp,Y[1]);
	s16i	a3, a8, 2	# MEM[(celt_norm *)X_233 + 2B], tmp2268
# @OPUS@\upstream\celt\bands.c:1347:          Y[1] = ADD16(tmp,Y[1]);
	l16ui	a3, a15, 2	# MEM[(celt_norm *)Y_235 + 2B],
	add.n	a2, a2, a3	# tmp2270, tmp, MEM[(celt_norm *)Y_235 + 2B]
# @OPUS@\upstream\celt\bands.c:1347:          Y[1] = ADD16(tmp,Y[1]);
	s16i	a2, a15, 2	# MEM[(celt_norm *)Y_235 + 2B], tmp2270
	j	.L590		#
.L720:
	l32r	a11, .LC51	#,
# @OPUS@\upstream\celt\bands.c:1299:    if (N==2)
	l32i	a12, sp, 112	# %sfp,
	movi.n	a14, 0	#,
	s32i	a11, sp, 140	# %sfp,
	s32i	a12, sp, 276	# %sfp,
	s32i	a14, sp, 240	# %sfp,
.L516:
# @OPUS@\upstream\celt\bands.c:1353:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	l32i	a8, sp, 188	# %sfp,
	sub	a2, a8, a2	# tmp2271,, delta
	extui	a3, a2, 31, 1	# tmp2273, tmp2271,
	add.n	a2, a3, a2	# tmp2274, tmp2273, tmp2271
	srai	a2, a2, 1	#, tmp2274,
	s32i	a2, sp, 124	# %sfp,
	bge	a8, a2, .L591	#,,
	s32i	a8, sp, 124	# %sfp,
.L591:
# @OPUS@\upstream\celt\bands.c:1353:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	l32i	a10, sp, 124	# %sfp,
	movi.n	a9, 0	#,
	movgez	a9, a10, a10	#,,
# @OPUS@\upstream\celt\bands.c:1355:       ctx->remaining_bits -= qalloc;
	l32i	a12, sp, 228	# %sfp,
	l32i	a11, sp, 252	# %sfp,
# @OPUS@\upstream\celt\bands.c:1354:       sbits = b-mbits;
	l32i	a14, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:1353:       mbits = IMAX(0, IMIN(b, (b-delta)/2));
	s32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1355:       ctx->remaining_bits -= qalloc;
	sub	a2, a11, a12	# tmp2277,,
# @OPUS@\upstream\celt\bands.c:1354:       sbits = b-mbits;
	sub	a14, a14, a9	#,,
	l32i	a8, sp, 276	# %sfp,
	l32i	a9, sp, 180	# %sfp,
# @OPUS@\upstream\celt\bands.c:1358:       if (mbits >= sbits)
	l32i	a10, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1354:       sbits = b-mbits;
	s32i	a14, sp, 256	# %sfp,
# @OPUS@\upstream\celt\bands.c:1355:       ctx->remaining_bits -= qalloc;
	s32i	a2, sp, 64	# ctx.remaining_bits, tmp2277
	ssr	a9	#
	sra	a12, a8	# fill,
# @OPUS@\upstream\celt\bands.c:1358:       if (mbits >= sbits)
	blt	a10, a14, .L592	#,,
# @OPUS@\upstream\celt\bands.c:1362:          cm = quant_band(ctx, X, N, mbits, B, lowband, LM, lowband_out, Q15ONE,
	l32i	a14, sp, 168	# %sfp,
	mov.n	a6, a9	#,
	mov.n	a5, a10	#,
	s32i.n	a8, sp, 16	#,
	l32i	a9, sp, 236	# %sfp,
	l32i	a8, sp, 140	# %sfp,
	l32i	a10, sp, 428	# LM,
	addi	a11, sp, 32	#,,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	l32i	a7, sp, 152	# %sfp,
	s32i.n	a14, sp, 12	#,
	s32i.n	a8, sp, 8	#,
	mov.n	a2, a11	#,
	s32i.n	a9, sp, 4	#,
	s32i.n	a10, sp, 0	#,
	s32i	a11, sp, 132	# %sfp,
	call0	quant_band		#
	s32i	a2, sp, 236	# %sfp,
# @OPUS@\upstream\celt\bands.c:1364:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	l32i	a11, sp, 252	# %sfp,
	l32i	a2, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
	l32i	a14, sp, 228	# %sfp,
	sub	a2, a2, a11	# tmp2279, ctx.remaining_bits,
# @OPUS@\upstream\celt\bands.c:1364:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	l32i	a8, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1364:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	add.n	a4, a2, a14	# _502, tmp2279,
# @OPUS@\upstream\celt\bands.c:1365:          if (rebalance > 3<<BITRES && itheta!=0)
	movi.n	a3, 0x18	# tmp2284,
# @OPUS@\upstream\celt\bands.c:1364:          rebalance = mbits - (rebalance-ctx->remaining_bits);
	add.n	a2, a8, a4	# rebalance,, _502
# @OPUS@\upstream\celt\bands.c:1365:          if (rebalance > 3<<BITRES && itheta!=0)
	bge	a3, a2, .L593	# tmp2284, rebalance,
# @OPUS@\upstream\celt\bands.c:1365:          if (rebalance > 3<<BITRES && itheta!=0)
	l32i	a9, sp, 196	# %sfp,
	beqz.n	a9, .L593	#,
# @OPUS@\upstream\celt\bands.c:1366:             sbits += rebalance - (3<<BITRES);
	l32i	a10, sp, 188	# %sfp,
	addi	a2, a10, -24	# tmp2291,,
	add.n	a2, a2, a4	#, tmp2291, _502
	s32i	a2, sp, 256	# %sfp,
.L593:
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	l32i.n	a11, sp, 56	# ctx.tf_change,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i	a3, sp, 180	# %sfp,
	l32i	a2, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	s32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	call0	__udivsi3		#
	mov.n	a14, a2	# N_B,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	l32i.n	a2, sp, 32	# MEM[(int *)&ctx],
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	s32i	a2, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	blti	a8, 1, .L595	#,,
	l32r	a9, .LC64	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a14, sp, 152	# %sfp, N_B
	s32i	a9, sp, 120	# %sfp,
	l32i	a14, sp, 120	# %sfp, tmp2718
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a9, 0	# k,
.L599:
# @OPUS@\upstream\celt\bands.c:1172:       if (encode)
	l32i	a10, sp, 124	# %sfp,
	beqz.n	a10, .L596	#,
# @OPUS@\upstream\celt\bands.c:1173:          haar1(X, N>>k, 1<<k);
	l32i	a8, sp, 128	# %sfp,
	movi.n	a10, 1	#,
	ssr	a9	# k
	sra	a11, a8	# tmp2296,
	ssl	a9	# k
	sll	a13, a10	# _1639,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a10	#
	sra	a11, a11	# N0, tmp2296
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a13, a10, .L596	# _1639,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a11, a10, .L597	# N0,,
	j	.L596		#
.L598:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a9	# k
	sll	a2, a3	# tmp2297, j
	slli	a2, a2, 1	# tmp2298, tmp2297,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a9	# k
	sll	a7, a4	# tmp2301, ivtmp$620
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp2299, tmp2298, i
	slli	a2, a2, 1	# tmp2300, tmp2299,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a7, a5	# tmp2302, tmp2301, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a15, a2	# _1758, Y, tmp2300
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a7, a7, 1	# tmp2303, tmp2302,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a8, a6, 0	# *_1758,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a15, a7	# _1768, Y, tmp2303
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a12, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a7, 0	# *_1768,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a8, a8, a12	# tmp1, *_1758,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a12	# tmp2, *_1768, tmp2
	addmi	a2, a8, 0x4000	# _688, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a8, a2, a10	# tmp2309, _688, tmp2
	srai	a8, a8, 15	# tmp2310, tmp2309,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2311, _688, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a8, a6, 0	# *_1758, tmp2310
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2312, tmp2311,
	s16i	a2, a7, 0	# *_1768, tmp2312
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$620, ivtmp$620,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a11, a3, .L598	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
	l32i	a12, sp, 120	# %sfp, fill
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a13, a5, .L596	# _1639, i,
.L597:
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$620,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	s32i	a12, sp, 120	# %sfp, fill
	j	.L598		#
.L596:
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	srai	a2, a12, 4	# tmp2317, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a2, a14, a2	# tmp2318, tmp2718, tmp2317
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	extui	a12, a12, 0, 4	# tmp2314, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a12, a14, a12	# tmp2315, tmp2718, tmp2314
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a2, a2, 0	# bit_interleave_table, tmp2319
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a12, a12, 0	# bit_interleave_table, _1646
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	slli	a2, a2, 2	# _1650, tmp2319,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	addi.n	a9, a9, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	or	a12, a12, a2	# fill, _1646, _1650
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	bne	a8, a9, .L599	#, k,
	mov.n	a9, a8	#,
	l32i	a14, sp, 152	# %sfp, N_B
# @OPUS@\upstream\celt\bands.c:1178:    B>>=recombine;
	l32i	a8, sp, 180	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a10, 0	#,
# @OPUS@\upstream\celt\bands.c:1178:    B>>=recombine;
	ssr	a9	#
	sra	a13, a8	# B,
# @OPUS@\upstream\celt\bands.c:1179:    N_B<<=recombine;
	ssl	a9	#
	sll	a14, a14	# N_B, N_B
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a10, sp, 152	# %sfp,
	j	.L601		#
.L595:
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	l32i	a13, sp, 180	# %sfp, B
	bbsi	a14, 0, .L733	# N_B,,
	bgez	a8, .L733	# tmp9,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a10, 0	#,
	s32i	a10, sp, 152	# %sfp,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	s32i	a15, sp, 120	# %sfp, Y
	mov.n	a11, a10	# time_divide,
.L605:
# @OPUS@\upstream\celt\bands.c:1184:       if (encode)
	l32i	a2, sp, 124	# %sfp,
	srai	a14, a14, 1	# N_B, N_B,
	slli	a10, a13, 1	# B, B,
	beqz.n	a2, .L602	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a13, 1, .L602	# B,,
	blti	a14, 1, .L602	# N_B,,
	l32i	a3, sp, 120	# %sfp, ivtmp$633
	slli	a9, a13, 2	# _4957, B,
	add.n	a15, a3, a10	# _4921, ivtmp$633, B
	j	.L603		#
.L604:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a7, a4, 0	# MEM[base: _4936, offset: 0B],
	l32r	a10, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a8, a5, 0	# MEM[base: _4934, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a7, a7, a10	# tmp1, MEM[base: _4936, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a8, a8, a10	# tmp2, MEM[base: _4934, offset: 0B], tmp2
	addmi	a2, a7, 0x4000	# _638, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a2, a8	# tmp2335, _638, tmp2
	srai	a7, a7, 15	# tmp2336, tmp2335,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp2337, _638, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a4, 0	# MEM[base: _4936, offset: 0B], tmp2336
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2338, tmp2337,
	s16i	a2, a5, 0	# MEM[base: _4934, offset: 0B], tmp2338
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$628, ivtmp$628, _4957
	add.n	a5, a5, a9	# ivtmp$629, ivtmp$629, _4957
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a6, a14, .L604	# j, N_B,
	addi.n	a3, a3, 2	# ivtmp$633, ivtmp$633,
	l32i	a10, sp, 140	# %sfp, B
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a15, a3, .L602	# _4921, ivtmp$633,
.L603:
	add.n	a5, a10, a3	# ivtmp$629, B, ivtmp$633
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	mov.n	a4, a3	# ivtmp$628, ivtmp$633
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	s32i	a10, sp, 140	# %sfp, B
	j	.L604		#
.L602:
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	addi.n	a11, a11, 1	# time_divide, time_divide,
	add.n	a2, a11, a8	# _4914, time_divide,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	movi.n	a9, -1	#,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	ssl	a13	# B
	sll	a13, a12	# _1658, fill
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	extui	a2, a2, 31, 1	# tmp2340, _4914,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	xor	a3, a9, a14	# tmp2341,, N_B
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	or	a12, a12, a13	# fill, fill, _1658
# @OPUS@\upstream\celt\bands.c:1189:       B <<= 1;
	mov.n	a13, a10	# B, B
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	bany	a3, a2, .L605	# tmp2341, tmp2340,
# @OPUS@\upstream\celt\bands.c:1137:    int recombine=0;
	movi.n	a10, 0	#,
	l32i	a15, sp, 120	# %sfp, Y
	s32i	a11, sp, 152	# %sfp, time_divide
	s32i	a10, sp, 112	# %sfp,
	j	.L601		#
.L733:
	movi.n	a11, 0	#,
	s32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a11, sp, 152	# %sfp, tmp8
.L601:
# @OPUS@\upstream\celt\bands.c:1198:    if (B0>1)
	blti	a13, 2, .L606	# B,,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i	a9, sp, 124	# %sfp,
	beqz.n	a9, .L607	#,
# @OPUS@\upstream\celt\bands.c:1201:          deinterleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a10, sp, 112	# %sfp,
	l32i	a5, sp, 312	# %sfp,
	ssl	a10	#
	sll	a4, a13	#, B
	ssr	a10	#
	sra	a3, a14	#, N_B
	mov.n	a2, a15	#, Y
	call0	deinterleave_hadamard		#
	j	.L607		#
.L672:
# @OPUS@\upstream\celt\bands.c:1213:          interleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a11, sp, 112	# %sfp,
	ssl	a11	#
	sll	a6, a13	# _1678, B
	ssr	a11	#
	sra	a12, a14	# _1677, N_B
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	mull	a8, a12, a6	#, _1677, _1678
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a6, sp, 344	#,
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	s32i	a8, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 92	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	l32i	a2, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a3, sp, 96	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	s32i	a2, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a6, sp, 344	#,
	bnez.n	a9, .L608	#,
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	blti	a6, 1, .L609	# _1678,,
	blti	a12, 1, .L609	# _1677,,
	slli	a5, a12, 1	# tmp2351, _1677,
	mov.n	a10, a5	# tmp2354, tmp2351
	slli	a6, a6, 1	# _4969, _1678,
	slli	a11, a12, 2	# tmp2372, _1677,
	mov.n	a7, a2	# ivtmp$615,
	add.n	a5, a15, a5	# ivtmp$616, Y, tmp2351
	add.n	a9, a6, a2	# _4967, _4969,
	neg	a10, a10	# tmp2355, tmp2354
	neg	a11, a11	# tmp2373, tmp2372
	j	.L610		#
.L608:
# @OPUS@\upstream\celt\bands.c:625:       const int *ordery = ordery_table+stride-2;
	l32r	a2, .LC68	#, tmp2356
	add.n	a7, a6, a2	# _1882, _1678, tmp2356
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	blti	a6, 1, .L609	# _1678,,
	blti	a12, 1, .L609	# _1677,,
	l32r	a3, .LC69	#, tmp2358
	slli	a9, a6, 3	# tmp2361, _1678,
	slli	a7, a7, 2	# tmp2357, _1882,
	addi	a2, a3, -8	# tmp2359, tmp2358,
	add.n	a7, a7, a3	# ivtmp$605, tmp2357, tmp2358
	l32i	a8, sp, 124	# %sfp, ivtmp$607
	add.n	a9, a2, a9	# _5022, tmp2359, tmp2361
	slli	a6, a6, 1	# _5059, _1678,
	j	.L611		#
.L612:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l16si	a4, a2, 0	# MEM[base: _5047, offset: 0B], _1900
	addi.n	a2, a2, 2	# ivtmp$601, ivtmp$601,
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	s16i	a4, a3, 0	# MEM[base: _5046, offset: 0B], _1900
	add.n	a3, a3, a6	# ivtmp$602, ivtmp$602, _5059
# @OPUS@\upstream\celt\bands.c:627:          for (j=0;j<N0;j++)
	bne	a5, a2, .L612	# _5040, ivtmp$601,
	addi.n	a7, a7, 4	# ivtmp$605, ivtmp$605,
	addi.n	a8, a8, 2	# ivtmp$607, ivtmp$607,
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	beq	a9, a7, .L609	# _5022, ivtmp$605,
.L611:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l32i.n	a2, a7, 0	# MEM[base: _5027, offset: 0B], MEM[base: _5027, offset: 0B]
	mov.n	a3, a8	# ivtmp$602, ivtmp$607
	mull	a2, a12, a2	# _5065, _1677, MEM[base: _5027, offset: 0B]
	add.n	a5, a12, a2	# tmp2366, _1677, _5065
	slli	a5, a5, 1	# tmp2367, tmp2366,
	slli	a2, a2, 1	# tmp2365, _5065,
	add.n	a2, a15, a2	# ivtmp$601, Y, tmp2365
	add.n	a5, a15, a5	# _5040, Y, tmp2367
	j	.L612		#
.L613:
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	l16si	a4, a2, 0	# MEM[base: _4999, offset: 0B], _1915
	addi.n	a2, a2, 2	# ivtmp$610, ivtmp$610,
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	s16i	a4, a3, 0	# MEM[base: _4998, offset: 0B], _1915
	add.n	a3, a3, a6	# ivtmp$611, ivtmp$611, _4969
# @OPUS@\upstream\celt\bands.c:631:          for (j=0;j<N0;j++)
	bne	a5, a2, .L613	# ivtmp$616, ivtmp$610,
	addi.n	a7, a7, 2	# ivtmp$615, ivtmp$615,
	sub	a5, a8, a11	# ivtmp$616, _4964, tmp2373
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	beq	a9, a7, .L609	# _4967, ivtmp$615,
.L610:
	add.n	a8, a10, a5	# _4964, tmp2355, ivtmp$616
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	mov.n	a3, a7	# ivtmp$611, ivtmp$615
	mov.n	a2, a8	# ivtmp$610, _4964
	j	.L613		#
.L609:
# @OPUS@\upstream\celt\bands.c:634:    OPUS_COPY(X, tmp, N);
	l32i	a4, sp, 140	# %sfp,
	l32i	a3, sp, 124	# %sfp,
	movi.n	a5, 2	#,
	mov.n	a2, a15	#, Y
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:635:    RESTORE_STACK;
	l32i	a2, sp, 92	# _saved_stack,
	l32i	a3, sp, 96	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
	l32i.n	a10, sp, 36	# ctx.resynth,
	s32i	a10, sp, 132	# %sfp,
	j	.L614		#
.L967:
	s32i	a15, sp, 140	# %sfp, Y
	mov.n	a15, a2	# tmp2990, tmp2990
.L618:
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	l32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1220:          B >>= 1;
	srai	a13, a13, 1	# B, B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	ssr	a13	# B
	srl	a2, a11	# _1684,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	or	a11, a11, a2	#,, _1684
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	slli	a14, a14, 1	# N_B, N_B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	srai	a10, a14, 1	# N0, N_B,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a13, 1, .L615	# B,,
	blti	a10, 1, .L615	# N0,,
	l32i	a3, sp, 140	# %sfp, ivtmp$594
	slli	a11, a13, 1	# _5075, B,
	add.n	a12, a11, a3	# _5073, _5075, ivtmp$594
	slli	a9, a13, 2	# _5113, B,
	j	.L616		#
.L617:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16si	a7, a4, 0	# MEM[base: _5090, offset: 0B], tmp2378
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16si	a2, a5, 0	# MEM[base: _5081, offset: 0B], tmp2375
	l32r	a11, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mull	a7, a7, a15	# tmp1, tmp2378, tmp2990
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mull	a8, a2, a11	# tmp2, tmp2375,
	addmi	a2, a7, 0x4000	# _617, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a2, a8	# tmp2379, _617, tmp2
	srai	a7, a7, 15	# tmp2380, tmp2379,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp2381, _617, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a4, 0	# MEM[base: _5090, offset: 0B], tmp2380
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2382, tmp2381,
	s16i	a2, a5, 0	# MEM[base: _5081, offset: 0B], tmp2382
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$589, ivtmp$589, _5113
	add.n	a5, a5, a9	# ivtmp$590, ivtmp$590, _5113
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a10, a6, .L617	# N0, j,
	addi.n	a3, a3, 2	# ivtmp$594, ivtmp$594,
	l32i	a11, sp, 148	# %sfp, _5075
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a12, a3, .L615	# _5073, ivtmp$594,
.L616:
	add.n	a5, a11, a3	# ivtmp$590, _5075, ivtmp$594
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	mov.n	a4, a3	# ivtmp$589, ivtmp$594
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	s32i	a11, sp, 148	# %sfp, _5075
	j	.L617		#
.L615:
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i	a12, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	addi.n	a12, a12, 1	#,,
	s32i	a12, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bne	a12, a8, .L618	#,,
	l32i	a15, sp, 140	# %sfp, Y
	j	.L619		#
.L614:
	movi.n	a9, 0	#,
	l32i	a10, sp, 152	# %sfp,
	s32i	a9, sp, 124	# %sfp,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a2, .LC57	#, tmp2990
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bgei	a10, 1, .L967	#,,
.L619:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a11, sp, 112	# %sfp,
	beqz.n	a11, .L620	#,
	l32r	a12, .LC70	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a13, sp, 124	# %sfp, B
	l32r	a14, .LC57	#, tmp2986
	l32i	a13, sp, 120	# %sfp, cm
	s32i	a12, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a9, 0	# k,
.L624:
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l32i	a2, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	l32i	a8, sp, 128	# %sfp,
	movi.n	a10, 1	#,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	add.n	a13, a2, a13	# tmp2384,, cm
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	ssr	a9	# k
	sra	a11, a8	# tmp2386,
	ssl	a9	# k
	sll	a12, a10	# _1694,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l8ui	a13, a13, 0	# bit_deinterleave_table, cm
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a10	#
	sra	a11, a11	# N0, tmp2386
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a12, a10, .L621	# _1694,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a11, a10, .L622	# N0,,
	j	.L621		#
.L623:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a9	# k
	sll	a2, a3	# tmp2387, j
	slli	a2, a2, 1	# tmp2388, tmp2387,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a9	# k
	sll	a7, a4	# tmp2391, ivtmp$581
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp2389, tmp2388, i
	slli	a2, a2, 1	# tmp2390, tmp2389,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a7, a5	# tmp2392, tmp2391, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a15, a2	# _1958, Y, tmp2390
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a7, a7, 1	# tmp2393, tmp2392,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a8, a6, 0	# *_1958,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a15, a7	# _1968, Y, tmp2393
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a7, 0	# *_1968,
	l32r	a2, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a8, a8, a14	# tmp1, *_1958, tmp2986
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a2	# tmp2, *_1968,
	addmi	a2, a8, 0x4000	# _1709, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a8, a2, a10	# tmp2399, _1709, tmp2
	srai	a8, a8, 15	# tmp2400, tmp2399,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2401, _1709, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a8, a6, 0	# *_1958, tmp2400
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2402, tmp2401,
	s16i	a2, a7, 0	# *_1968, tmp2402
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$581, ivtmp$581,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a11, a3, .L623	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a12, a5, .L621	# _1694, i,
.L622:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$581,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	j	.L623		#
.L621:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	addi.n	a9, a9, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	bne	a8, a9, .L624	#, k,
	s32i	a13, sp, 120	# %sfp, cm
	l32i	a13, sp, 124	# %sfp, B
.L620:
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	movi.n	a10, 1	#,
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	ssl	a9	#
	sll	a12, a13	# B, B
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	ssl	a12	# B
	sll	a12, a10	# tmp2405,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	l32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	addi.n	a12, a12, -1	# tmp2406, tmp2405,
# @OPUS@\upstream\celt\bands.c:1370:          cm |= quant_band(ctx, Y, N, sbits, B, NULL, LM, NULL, side, NULL, fill>>B);
	l32i	a14, sp, 236	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	and	a12, a12, a11	# cm, tmp2406,
# @OPUS@\upstream\celt\bands.c:1370:          cm |= quant_band(ctx, Y, N, sbits, B, NULL, LM, NULL, side, NULL, fill>>B);
	or	a12, a12, a14	# cm, cm,
	j	.L625		#
.L592:
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	l32i.n	a8, sp, 56	# ctx.tf_change,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i	a2, sp, 128	# %sfp,
	mov.n	a3, a9	#,
# @OPUS@\upstream\celt\bands.c:1145:    tf_change = ctx->tf_change;
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	call0	__udivsi3		#
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	l32i.n	a9, sp, 32	# MEM[(int *)&ctx],
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	l32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1144:    encode = band_encode(ctx);
	s32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a14, a2	# N_B,
# @OPUS@\upstream\celt\bands.c:1157:    if (tf_change>0)
	blti	a10, 1, .L626	#,,
	l32r	a11, .LC64	#,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a9, 0	# k,
	s32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a2, sp, 148	# %sfp, N_B
	mov.n	a14, a11	# tmp2718,
.L630:
# @OPUS@\upstream\celt\bands.c:1172:       if (encode)
	l32i	a2, sp, 132	# %sfp,
	beqz.n	a2, .L627	#,
# @OPUS@\upstream\celt\bands.c:1173:          haar1(X, N>>k, 1<<k);
	l32i	a8, sp, 128	# %sfp,
	movi.n	a10, 1	#,
	ssr	a9	# k
	sra	a11, a8	# tmp2412,
	ssl	a9	# k
	sll	a13, a10	# _1999,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a10	#
	sra	a11, a11	# N0, tmp2412
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a13, a10, .L627	# _1999,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a11, a10, .L628	# N0,,
	j	.L627		#
.L629:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a9	# k
	sll	a2, a3	# tmp2413, j
	slli	a2, a2, 1	# tmp2414, tmp2413,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a9	# k
	sll	a7, a4	# tmp2417, ivtmp$681
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp2415, tmp2414, i
	slli	a2, a2, 1	# tmp2416, tmp2415,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a7, a5	# tmp2418, tmp2417, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a15, a2	# _2118, Y, tmp2416
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a7, a7, 1	# tmp2419, tmp2418,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a8, a6, 0	# *_2118,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a15, a7	# _2128, Y, tmp2419
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a12, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a7, 0	# *_2128,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a8, a8, a12	# tmp1, *_2118,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a12	# tmp2, *_2128, tmp2
	addmi	a2, a8, 0x4000	# _1390, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a8, a2, a10	# tmp2425, _1390, tmp2
	srai	a8, a8, 15	# tmp2426, tmp2425,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2427, _1390, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a8, a6, 0	# *_2118, tmp2426
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2428, tmp2427,
	s16i	a2, a7, 0	# *_2128, tmp2428
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$681, ivtmp$681,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a11, a3, .L629	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
	l32i	a12, sp, 120	# %sfp, fill
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a13, a5, .L627	# _1999, i,
.L628:
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$681,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	s32i	a12, sp, 120	# %sfp, fill
	j	.L629		#
.L627:
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	srai	a2, a12, 4	# tmp2433, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a2, a14, a2	# tmp2434, tmp2718, tmp2433
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	extui	a12, a12, 0, 4	# tmp2430, fill,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	add.n	a12, a14, a12	# tmp2431, tmp2718, tmp2430
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a2, a2, 0	# bit_interleave_table, tmp2435
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	l8ui	a12, a12, 0	# bit_interleave_table, _2006
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	slli	a2, a2, 2	# _2010, tmp2435,
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	addi.n	a9, a9, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1176:       fill = bit_interleave_table[fill&0xF]|bit_interleave_table[fill>>4]<<2;
	or	a12, a12, a2	# fill, _2006, _2010
# @OPUS@\upstream\celt\bands.c:1167:    for (k=0;k<recombine;k++)
	bne	a8, a9, .L630	#, k,
	l32i	a14, sp, 148	# %sfp, N_B
# @OPUS@\upstream\celt\bands.c:1178:    B>>=recombine;
	l32i	a11, sp, 180	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a9, 0	#,
# @OPUS@\upstream\celt\bands.c:1178:    B>>=recombine;
	ssr	a8	#
	sra	a13, a11	# B,
# @OPUS@\upstream\celt\bands.c:1179:    N_B<<=recombine;
	ssl	a8	#
	sll	a14, a14	# N_B, N_B
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a9, sp, 188	# %sfp,
	j	.L632		#
.L626:
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	l32i	a13, sp, 180	# %sfp, B
	bgez	a10, .L737	# tmp9,
	bbsi	a2, 0, .L737	# N_B,,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	movi.n	a10, 0	#,
	s32i	a10, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	s32i	a15, sp, 120	# %sfp, Y
	mov.n	a11, a10	# time_divide,
.L636:
# @OPUS@\upstream\celt\bands.c:1184:       if (encode)
	l32i	a2, sp, 132	# %sfp,
	srai	a14, a14, 1	# N_B, N_B,
	slli	a10, a13, 1	# B, B,
	beqz.n	a2, .L633	#,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a13, 1, .L633	# B,,
	blti	a14, 1, .L633	# N_B,,
	l32i	a3, sp, 120	# %sfp, ivtmp$694
	slli	a9, a13, 2	# _4773, B,
	add.n	a15, a3, a10	# _4720, ivtmp$694, B
	j	.L634		#
.L635:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a7, a4, 0	# MEM[base: _4737, offset: 0B],
	l32r	a10, .LC57	#,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a8, a5, 0	# MEM[base: _4735, offset: 0B],
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a7, a7, a10	# tmp1, MEM[base: _4737, offset: 0B],
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a8, a8, a10	# tmp2, MEM[base: _4735, offset: 0B], tmp2
	addmi	a2, a7, 0x4000	# _2024, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a2, a8	# tmp2451, _2024, tmp2
	srai	a7, a7, 15	# tmp2452, tmp2451,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp2453, _2024, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a4, 0	# MEM[base: _4737, offset: 0B], tmp2452
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2454, tmp2453,
	s16i	a2, a5, 0	# MEM[base: _4735, offset: 0B], tmp2454
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$689, ivtmp$689, _4773
	add.n	a5, a5, a9	# ivtmp$690, ivtmp$690, _4773
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a6, a14, .L635	# j, N_B,
	addi.n	a3, a3, 2	# ivtmp$694, ivtmp$694,
	l32i	a10, sp, 148	# %sfp, B
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a15, a3, .L633	# _4720, ivtmp$694,
.L634:
	add.n	a5, a10, a3	# ivtmp$690, B, ivtmp$694
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	mov.n	a4, a3	# ivtmp$689, ivtmp$694
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	s32i	a10, sp, 148	# %sfp, B
	j	.L635		#
.L633:
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1191:       time_divide++;
	addi.n	a11, a11, 1	# time_divide, time_divide,
	add.n	a2, a11, a8	# _4713, time_divide,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	movi.n	a9, -1	#,
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	ssl	a13	# B
	sll	a13, a12	# _2018, fill
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	extui	a2, a2, 31, 1	# tmp2456, _4713,
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	xor	a3, a9, a14	# tmp2457,, N_B
# @OPUS@\upstream\celt\bands.c:1188:       fill |= fill<<B;
	or	a12, a12, a13	# fill, fill, _2018
# @OPUS@\upstream\celt\bands.c:1189:       B <<= 1;
	mov.n	a13, a10	# B, B
# @OPUS@\upstream\celt\bands.c:1182:    while ((N_B&1) == 0 && tf_change<0)
	bany	a3, a2, .L636	# tmp2457, tmp2456,
# @OPUS@\upstream\celt\bands.c:1137:    int recombine=0;
	movi.n	a10, 0	#,
	l32i	a15, sp, 120	# %sfp, Y
	s32i	a11, sp, 188	# %sfp, time_divide
	s32i	a10, sp, 112	# %sfp,
	j	.L632		#
.L737:
	movi.n	a11, 0	#,
	s32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1136:    int time_divide=0;
	s32i	a11, sp, 188	# %sfp, tmp8
.L632:
# @OPUS@\upstream\celt\bands.c:1198:    if (B0>1)
	blti	a13, 2, .L637	# B,,
# @OPUS@\upstream\celt\bands.c:1200:       if (encode)
	l32i	a9, sp, 132	# %sfp,
	beqz.n	a9, .L638	#,
# @OPUS@\upstream\celt\bands.c:1201:          deinterleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a10, sp, 112	# %sfp,
	l32i	a5, sp, 312	# %sfp,
	ssl	a10	#
	sll	a4, a13	#, B
	ssr	a10	#
	sra	a3, a14	#, N_B
	mov.n	a2, a15	#, Y
	call0	deinterleave_hadamard		#
	j	.L638		#
.L673:
# @OPUS@\upstream\celt\bands.c:1213:          interleave_hadamard(X, N_B>>recombine, B0<<recombine, longBlocks);
	l32i	a11, sp, 112	# %sfp,
	ssl	a11	#
	sll	a6, a13	# _2038, B
	ssr	a11	#
	sra	a12, a14	# _2037, N_B
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	mull	a8, a12, a6	#, _2037, _2038
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a6, sp, 344	#,
# @OPUS@\upstream\celt\bands.c:621:    N = N0*stride;
	s32i	a8, sp, 216	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i	a2, sp, 92	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	l32i	a2, sp, 216	# %sfp,
# @OPUS@\upstream\celt\bands.c:620:    SAVE_STACK;
	s32i	a3, sp, 96	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\celt\bands.c:622:    ALLOC(tmp, N, celt_norm);
	s32i	a2, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:623:    if (hadamard)
	l32i	a6, sp, 344	#,
	bnez.n	a9, .L639	#,
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	blti	a6, 1, .L640	# _2038,,
	blti	a12, 1, .L640	# _2037,,
	slli	a5, a12, 1	# tmp2467, _2037,
	mov.n	a10, a5	# tmp2470, tmp2467
	slli	a6, a6, 1	# _4784, _2038,
	slli	a11, a12, 2	# tmp2488, _2037,
	mov.n	a7, a2	# ivtmp$676,
	add.n	a5, a15, a5	# ivtmp$677, Y, tmp2467
	add.n	a9, a6, a2	# _4782, _4784,
	neg	a10, a10	# tmp2471, tmp2470
	neg	a11, a11	# tmp2489, tmp2488
	j	.L641		#
.L639:
# @OPUS@\upstream\celt\bands.c:625:       const int *ordery = ordery_table+stride-2;
	l32r	a2, .LC68	#, tmp2472
	add.n	a7, a6, a2	# _2242, _2038, tmp2472
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	blti	a6, 1, .L640	# _2038,,
	blti	a12, 1, .L640	# _2037,,
	l32r	a3, .LC69	#, tmp2474
	slli	a9, a6, 3	# tmp2477, _2038,
	slli	a7, a7, 2	# tmp2473, _2242,
	addi	a2, a3, -8	# tmp2475, tmp2474,
	add.n	a7, a7, a3	# ivtmp$666, tmp2473, tmp2474
	l32i	a8, sp, 148	# %sfp, ivtmp$668
	add.n	a9, a2, a9	# _4821, tmp2475, tmp2477
	slli	a6, a6, 1	# _4849, _2038,
	j	.L642		#
.L643:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l16si	a4, a2, 0	# MEM[base: _4844, offset: 0B], _2260
	addi.n	a2, a2, 2	# ivtmp$662, ivtmp$662,
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	s16i	a4, a3, 0	# MEM[base: _4843, offset: 0B], _2260
	add.n	a3, a3, a6	# ivtmp$663, ivtmp$663, _4849
# @OPUS@\upstream\celt\bands.c:627:          for (j=0;j<N0;j++)
	bne	a5, a2, .L643	# _4837, ivtmp$662,
	addi.n	a7, a7, 4	# ivtmp$666, ivtmp$666,
	addi.n	a8, a8, 2	# ivtmp$668, ivtmp$668,
# @OPUS@\upstream\celt\bands.c:626:       for (i=0;i<stride;i++)
	beq	a9, a7, .L640	# _4821, ivtmp$666,
.L642:
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	l32i.n	a2, a7, 0	# MEM[base: _4826, offset: 0B], MEM[base: _4826, offset: 0B]
	mov.n	a3, a8	# ivtmp$663, ivtmp$668
	mull	a2, a12, a2	# _4855, _2037, MEM[base: _4826, offset: 0B]
	add.n	a5, a12, a2	# tmp2482, _2037, _4855
	slli	a5, a5, 1	# tmp2483, tmp2482,
	slli	a2, a2, 1	# tmp2481, _4855,
	add.n	a2, a15, a2	# ivtmp$662, Y, tmp2481
	add.n	a5, a15, a5	# _4837, Y, tmp2483
	j	.L643		#
.L644:
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	l16si	a4, a2, 0	# MEM[base: _4806, offset: 0B], _2275
	addi.n	a2, a2, 2	# ivtmp$671, ivtmp$671,
# @OPUS@\upstream\celt\bands.c:632:             tmp[j*stride+i] = X[i*N0+j];
	s16i	a4, a3, 0	# MEM[base: _4805, offset: 0B], _2275
	add.n	a3, a3, a6	# ivtmp$672, ivtmp$672, _4784
# @OPUS@\upstream\celt\bands.c:631:          for (j=0;j<N0;j++)
	bne	a5, a2, .L644	# ivtmp$677, ivtmp$671,
	addi.n	a7, a7, 2	# ivtmp$676, ivtmp$676,
	sub	a5, a8, a11	# ivtmp$677, _4779, tmp2489
# @OPUS@\upstream\celt\bands.c:630:       for (i=0;i<stride;i++)
	beq	a9, a7, .L640	# _4782, ivtmp$676,
.L641:
	add.n	a8, a10, a5	# _4779, tmp2471, ivtmp$677
# @OPUS@\upstream\celt\bands.c:628:             tmp[j*stride+i] = X[ordery[i]*N0+j];
	mov.n	a3, a7	# ivtmp$672, ivtmp$676
	mov.n	a2, a8	# ivtmp$671, _4779
	j	.L644		#
.L640:
# @OPUS@\upstream\celt\bands.c:634:    OPUS_COPY(X, tmp, N);
	l32i	a3, sp, 148	# %sfp,
	l32i	a4, sp, 216	# %sfp,
	mov.n	a2, a15	#, Y
	movi.n	a5, 2	#,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:635:    RESTORE_STACK;
	l32i	a2, sp, 92	# _saved_stack,
	l32i	a3, sp, 96	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
	j	.L645		#
.L976:
	s32i	a15, sp, 216	# %sfp, Y
	mov.n	a15, a2	# tmp3008, tmp3008
.L649:
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	l32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1220:          B >>= 1;
	srai	a13, a13, 1	# B, B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	ssr	a13	# B
	srl	a2, a10	# _2044,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	or	a10, a10, a2	#,, _2044
# @OPUS@\upstream\celt\bands.c:1221:          N_B <<= 1;
	slli	a14, a14, 1	# N_B, N_B,
# @OPUS@\upstream\celt\bands.c:1222:          cm |= cm>>B;
	s32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	srai	a10, a14, 1	# N0, N_B,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blti	a13, 1, .L646	# B,,
	blti	a10, 1, .L646	# N0,,
	l32i	a3, sp, 216	# %sfp, ivtmp$655
	slli	a11, a13, 1	# _4870, B,
	add.n	a12, a11, a3	# _4868, _4870, ivtmp$655
	slli	a9, a13, 2	# _4901, B,
	j	.L647		#
.L648:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16si	a7, a4, 0	# MEM[base: _4887, offset: 0B], tmp2494
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16si	a2, a5, 0	# MEM[base: _4883, offset: 0B], tmp2491
	l32r	a11, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mull	a7, a7, a15	# tmp1, tmp2494, tmp3008
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mull	a8, a2, a11	# tmp2, tmp2491,
	addmi	a2, a7, 0x4000	# _2066, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a7, a2, a8	# tmp2495, _2066, tmp2
	srai	a7, a7, 15	# tmp2496, tmp2495,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a8	# tmp2497, _2066, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a7, a4, 0	# MEM[base: _4887, offset: 0B], tmp2496
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2498, tmp2497,
	s16i	a2, a5, 0	# MEM[base: _4883, offset: 0B], tmp2498
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a6, a6, 1	# j, j,
	add.n	a4, a4, a9	# ivtmp$650, ivtmp$650, _4901
	add.n	a5, a5, a9	# ivtmp$651, ivtmp$651, _4901
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a10, a6, .L648	# N0, j,
	addi.n	a3, a3, 2	# ivtmp$655, ivtmp$655,
	l32i	a11, sp, 312	# %sfp, _4870
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a12, a3, .L646	# _4868, ivtmp$655,
.L647:
	add.n	a5, a11, a3	# ivtmp$651, _4870, ivtmp$655
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	mov.n	a4, a3	# ivtmp$650, ivtmp$655
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a6, 0	# j,
	s32i	a11, sp, 312	# %sfp, _4870
	j	.L648		#
.L646:
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i	a12, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	l32i	a8, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	addi.n	a12, a12, 1	#,,
	s32i	a12, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bne	a8, a12, .L649	#,,
	l32i	a15, sp, 216	# %sfp, Y
	j	.L650		#
.L645:
	movi.n	a9, 0	#,
	l32i	a10, sp, 188	# %sfp,
	s32i	a9, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l32r	a2, .LC57	#, tmp3008
# @OPUS@\upstream\celt\bands.c:1218:       for (k=0;k<time_divide;k++)
	bgei	a10, 1, .L976	#,,
.L650:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a11, sp, 112	# %sfp,
	beqz.n	a11, .L651	#,
	l32r	a12, .LC70	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	s32i	a13, sp, 188	# %sfp, B
	l32r	a14, .LC57	#, tmp3004
	l32i	a13, sp, 120	# %sfp, cm
	s32i	a12, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a9, 0	# k,
.L655:
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l32i	a2, sp, 148	# %sfp,
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	l32i	a8, sp, 128	# %sfp,
	movi.n	a10, 1	#,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	add.n	a13, a2, a13	# tmp2500,, cm
# @OPUS@\upstream\celt\bands.c:1233:          haar1(X, N0>>k, 1<<k);
	ssr	a9	# k
	sra	a11, a8	# tmp2502,
	ssl	a9	# k
	sll	a12, a10	# _2054,
# @OPUS@\upstream\celt\bands.c:1232:          cm = bit_deinterleave_table[cm];
	l8ui	a13, a13, 0	# bit_deinterleave_table, cm
# @OPUS@\upstream\celt\bands.c:641:    N0 >>= 1;
	ssr	a10	#
	sra	a11, a11	# N0, tmp2502
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	blt	a12, a10, .L652	# _2054,,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	movi.n	a5, 0	# i,
	bge	a11, a10, .L653	# N0,,
	j	.L652		#
.L654:
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	ssl	a9	# k
	sll	a2, a3	# tmp2503, j
	slli	a2, a2, 1	# tmp2504, tmp2503,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	ssl	a9	# k
	sll	a7, a4	# tmp2507, ivtmp$642
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a2, a2, a5	# tmp2505, tmp2504, i
	slli	a2, a2, 1	# tmp2506, tmp2505,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a7, a5	# tmp2508, tmp2507, i
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	add.n	a6, a15, a2	# _2318, Y, tmp2506
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	slli	a7, a7, 1	# tmp2509, tmp2508,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	l16ui	a8, a6, 0	# *_2318,
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	add.n	a7, a15, a7	# _2328, Y, tmp2509
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	l16ui	a10, a7, 0	# *_2328,
	l32r	a2, .LC57	#,
# @OPUS@\upstream\celt\bands.c:646:          tmp1 = MULT16_16(QCONST16(.70710678f,15), X[stride*2*j+i]);
	mul16s	a8, a8, a14	# tmp1, *_2318, tmp3004
# @OPUS@\upstream\celt\bands.c:647:          tmp2 = MULT16_16(QCONST16(.70710678f,15), X[stride*(2*j+1)+i]);
	mul16s	a10, a10, a2	# tmp2, *_2328,
	addmi	a2, a8, 0x4000	# _621, tmp1,
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	add.n	a8, a2, a10	# tmp2515, _621, tmp2
	srai	a8, a8, 15	# tmp2516, tmp2515,
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	sub	a2, a2, a10	# tmp2517, _621, tmp2
# @OPUS@\upstream\celt\bands.c:648:          X[stride*2*j+i] = EXTRACT16(PSHR32(ADD32(tmp1, tmp2), 15));
	s16i	a8, a6, 0	# *_2318, tmp2516
# @OPUS@\upstream\celt\bands.c:649:          X[stride*(2*j+1)+i] = EXTRACT16(PSHR32(SUB32(tmp1, tmp2), 15));
	srai	a2, a2, 15	# tmp2518, tmp2517,
	s16i	a2, a7, 0	# *_2328, tmp2518
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 2	# ivtmp$642, ivtmp$642,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	bne	a11, a3, .L654	# N0, j,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\bands.c:642:    for (i=0;i<stride;i++)
	beq	a12, a5, .L652	# _2054, i,
.L653:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	movi.n	a4, 1	# ivtmp$642,
# @OPUS@\upstream\celt\bands.c:643:       for (j=0;j<N0;j++)
	movi.n	a3, 0	# j,
	j	.L654		#
.L652:
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	addi.n	a9, a9, 1	# k, k,
# @OPUS@\upstream\celt\bands.c:1226:       for (k=0;k<recombine;k++)
	bne	a8, a9, .L655	#, k,
	s32i	a13, sp, 120	# %sfp, cm
	l32i	a13, sp, 188	# %sfp, B
.L651:
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	movi.n	a10, 1	#,
# @OPUS@\upstream\celt\bands.c:1235:       B<<=recombine;
	ssl	a9	#
	sll	a2, a13	# B, B
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	l32i	a11, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	ssl	a2	# B
	sll	a2, a10	# tmp2521,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	addi.n	a2, a2, -1	# tmp2522, tmp2521,
# @OPUS@\upstream\celt\bands.c:1246:       cm &= (1<<B)-1;
	and	a11, a11, a2	#,, tmp2522
	s32i	a11, sp, 120	# %sfp,
.L674:
# @OPUS@\upstream\celt\bands.c:1375:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
	l32i	a12, sp, 252	# %sfp,
	l32i	a14, sp, 228	# %sfp,
	sub	a3, a3, a12	# tmp2523, ctx.remaining_bits,
# @OPUS@\upstream\celt\bands.c:1375:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	l32i	a8, sp, 256	# %sfp,
# @OPUS@\upstream\celt\bands.c:1375:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	add.n	a3, a3, a14	# tmp2525, tmp2523,
# @OPUS@\upstream\celt\bands.c:1376:          if (rebalance > 3<<BITRES && itheta!=16384)
	movi.n	a2, 0x18	# tmp2528,
# @OPUS@\upstream\celt\bands.c:1375:          rebalance = sbits - (rebalance-ctx->remaining_bits);
	add.n	a3, a3, a8	# rebalance, tmp2525,
# @OPUS@\upstream\celt\bands.c:1376:          if (rebalance > 3<<BITRES && itheta!=16384)
	bge	a2, a3, .L656	# tmp2528, rebalance,
# @OPUS@\upstream\celt\bands.c:1376:          if (rebalance > 3<<BITRES && itheta!=16384)
	l32i	a9, sp, 196	# %sfp,
	addmi	a2, a9, -0x4000	# tmp2532,,
# @OPUS@\upstream\celt\bands.c:1376:          if (rebalance > 3<<BITRES && itheta!=16384)
	beqz.n	a2, .L656	# tmp2532,
	l32i	a10, sp, 124	# %sfp,
	addi	a2, a10, -24	# _2016,,
# @OPUS@\upstream\celt\bands.c:1377:             mbits += rebalance - (3<<BITRES);
	add.n	a2, a3, a2	#, rebalance, _2016
	s32i	a2, sp, 124	# %sfp,
.L656:
# @OPUS@\upstream\celt\bands.c:1380:          cm |= quant_band(ctx, X, N, mbits, B, lowband, LM, lowband_out, Q15ONE,
	l32i	a11, sp, 276	# %sfp,
	l32i	a12, sp, 168	# %sfp,
	l32i	a14, sp, 140	# %sfp,
	l32i	a8, sp, 236	# %sfp,
	l32i	a9, sp, 428	# LM,
	l32i	a7, sp, 152	# %sfp,
	l32i	a6, sp, 180	# %sfp,
	l32i	a5, sp, 124	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	l32i	a2, sp, 132	# %sfp,
	s32i.n	a11, sp, 16	#,
	s32i.n	a12, sp, 12	#,
	s32i.n	a14, sp, 8	#,
	s32i.n	a8, sp, 4	#,
	s32i.n	a9, sp, 0	#,
	call0	quant_band		#
# @OPUS@\upstream\celt\bands.c:1380:          cm |= quant_band(ctx, X, N, mbits, B, lowband, LM, lowband_out, Q15ONE,
	l32i	a10, sp, 120	# %sfp,
	l32i.n	a11, sp, 36	# ctx.resynth,
	or	a12, a2, a10	# cm,,
	s32i	a11, sp, 132	# %sfp,
	j	.L625		#
.L684:
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	l32i	a14, sp, 128	# %sfp,
	blti	a14, 1, .L740	#,,
	slli	a9, a14, 1	# tmp2537,,
# @OPUS@\upstream\celt\pitch.h:142:    opus_val32 xy02=0;
	movi.n	a7, 0	# xy02,
	l32i	a5, sp, 172	# %sfp, ivtmp$577
	mov.n	a2, a15	# ivtmp$576, Y
	add.n	a9, a9, a15	# _5119, tmp2537, Y
# @OPUS@\upstream\celt\pitch.h:141:    opus_val32 xy01=0;
	mov.n	a6, a7	# xy01, xy02
.L659:
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	l16si	a4, a2, 0	# MEM[base: _5131, offset: 0B], _2347
	l16ui	a3, a5, 0	# MEM[base: _5130, offset: 0B],
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	mull	a8, a4, a4	# tmp2542, _2347, _2347
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	mul16s	a3, a3, a4	# tmp2540, MEM[base: _5130, offset: 0B], _2347
	addi.n	a2, a2, 2	# ivtmp$576, ivtmp$576,
# @OPUS@\upstream\celt\pitch.h:145:       xy01 = MAC16_16(xy01, x[i], y01[i]);
	add.n	a6, a6, a3	# xy01, xy01, tmp2540
# @OPUS@\upstream\celt\pitch.h:146:       xy02 = MAC16_16(xy02, x[i], y02[i]);
	add.n	a7, a7, a8	# xy02, xy02, tmp2542
	addi.n	a5, a5, 2	# ivtmp$577, ivtmp$577,
# @OPUS@\upstream\celt\pitch.h:143:    for (i=0;i<N;i++)
	bne	a9, a2, .L659	# _5119, ivtmp$576,
	l32i	a8, sp, 272	# %sfp,
	srai	a3, a6, 16	# tmp2543, xy01,
	extui	a2, a6, 0, 16	# tmp2546, xy01,
	mull	a3, a3, a8	# tmp2544, tmp2543,
	mull	a2, a2, a8	# tmp2547, tmp2546,
	slli	a3, a3, 1	# tmp2545, tmp2544,
	srai	a2, a2, 15	# tmp2548, tmp2547,
	add.n	a2, a3, a2	# _4353, tmp2545, tmp2548
	slli	a4, a2, 1	# tmp2551, _4353,
	neg	a4, a4	# _4355, tmp2551
	slli	a2, a2, 1	# _4357, _4353,
	j	.L658		#
.L740:
	movi.n	a4, 0	# _4355,
	mov.n	a2, a4	# _4357, _4355
# @OPUS@\upstream\celt\pitch.h:142:    opus_val32 xy02=0;
	mov.n	a7, a4	# xy02, _4355
.L658:
# @OPUS@\upstream\celt\bands.c:448:    mid2 = SHR16(mid, 1);
	l32i	a9, sp, 316	# %sfp,
# @OPUS@\upstream\celt\bands.c:451:    if (Er < QCONST32(6e-4f, 28) || El < QCONST32(6e-4f, 28))
	l32r	a5, .LC72	#, tmp2724
# @OPUS@\upstream\celt\bands.c:448:    mid2 = SHR16(mid, 1);
	srai	a3, a9, 1	# mid2,,
# @OPUS@\upstream\celt\bands.c:449:    El = MULT16_16(mid2, mid2) + side - 2*xp;
	mull	a3, a3, a3	# tmp2555, mid2, mid2
	add.n	a7, a3, a7	# _602, tmp2555, xy02
# @OPUS@\upstream\celt\bands.c:450:    Er = MULT16_16(mid2, mid2) + side + 2*xp;
	add.n	a6, a7, a2	# Er, _602, _4357
# @OPUS@\upstream\celt\bands.c:449:    El = MULT16_16(mid2, mid2) + side - 2*xp;
	add.n	a7, a7, a4	# El, _602, _4355
# @OPUS@\upstream\celt\bands.c:451:    if (Er < QCONST32(6e-4f, 28) || El < QCONST32(6e-4f, 28))
	bge	a5, a6, .L748	# tmp2724, Er,
# @OPUS@\upstream\celt\bands.c:451:    if (Er < QCONST32(6e-4f, 28) || El < QCONST32(6e-4f, 28))
	bge	a5, a7, .L748	# tmp2724, El,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a7	# _2387, El
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a2, 0x1f	# tmp2564,
	sub	a3, a2, a3	# tmp2566, tmp2564, _2387
# @OPUS@\upstream\celt\bands.c:458:    kl = celt_ilog2(El)>>1;
	slli	a3, a3, 16	# tmp2568, tmp2566,
# @OPUS@\upstream\celt\bands.c:458:    kl = celt_ilog2(El)>>1;
	srai	a3, a3, 17	# kl, tmp2568,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a13, a6	# _2393, Er
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	sub	a13, a2, a13	# tmp2573, tmp2564, _2393
# @OPUS@\upstream\celt\bands.c:461:    t = VSHR32(El, (kl-7)<<1);
	addi	a2, a3, -7	# tmp2578, kl,
	slli	a2, a2, 1	# tmp2579, tmp2578,
# @OPUS@\upstream\celt\bands.c:462:    lgain = celt_rsqrt_norm(t);
	ssr	a2	# tmp2579
	sra	a2, a7	#, El
# @OPUS@\upstream\celt\bands.c:459:    kr = celt_ilog2(Er)>>1;
	slli	a13, a13, 16	# tmp2575, tmp2573,
# @OPUS@\upstream\celt\bands.c:462:    lgain = celt_rsqrt_norm(t);
	s32i	a3, sp, 340	#,
	s32i	a6, sp, 344	#,
# @OPUS@\upstream\celt\bands.c:459:    kr = celt_ilog2(Er)>>1;
	srai	a13, a13, 17	# kr, tmp2575,
# @OPUS@\upstream\celt\bands.c:462:    lgain = celt_rsqrt_norm(t);
	call0	celt_rsqrt_norm		#
# @OPUS@\upstream\celt\bands.c:464:    rgain = celt_rsqrt_norm(t);
	l32i	a6, sp, 344	#,
# @OPUS@\upstream\celt\bands.c:462:    lgain = celt_rsqrt_norm(t);
	mov.n	a14, a2	# _2401,
# @OPUS@\upstream\celt\bands.c:463:    t = VSHR32(Er, (kr-7)<<1);
	addi	a2, a13, -7	# tmp2582, kr,
	slli	a2, a2, 1	# tmp2583, tmp2582,
# @OPUS@\upstream\celt\bands.c:464:    rgain = celt_rsqrt_norm(t);
	ssr	a2	# tmp2583
	sra	a2, a6	#, Er
	call0	celt_rsqrt_norm		#
# @OPUS@\upstream\celt\bands.c:473:    for (j=0;j<N;j++)
	l32i	a10, sp, 128	# %sfp,
	l32i	a3, sp, 340	#,
	bgei	a10, 1, .L944	#,,
	j	.L481		#
.L748:
# @OPUS@\upstream\celt\bands.c:453:       OPUS_COPY(Y, X, N);
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	movi.n	a5, 2	#,
	mov.n	a2, a15	#, Y
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\bands.c:1391:       if (inv)
	l32i	a11, sp, 240	# %sfp,
	bnez.n	a11, .L664	#,
	j	.L481		#
.L944:
	mov.n	a4, a10	#,
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	addi.n	a7, a3, 1	# _2423, kl,
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	addi.n	a11, a13, 1	# _2432, kr,
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	movi.n	a3, 1	#,
	l32i	a13, sp, 172	# %sfp, ivtmp$571
	ssl	a7	# _2423
	sll	a10, a3	# tmp2587,
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	ssl	a11	# _2432
	sll	a9, a3	# tmp2589,
	ssl	a3	#
	sll	a8, a4	# tmp2590,
	mov.n	a5, a15	# ivtmp$572, Y
	s32i	a15, sp, 112	# %sfp, Y
	l32i	a15, sp, 272	# %sfp, imid
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	ssr	a3	#
	sra	a10, a10	# _2425, tmp2587
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	ssr	a3	#
	sra	a9, a9	# _2434, tmp2589
	add.n	a8, a13, a8	# _5139, ivtmp$571, tmp2590
.L665:
# @OPUS@\upstream\celt\bands.c:477:       l = MULT16_16_P15(mid, X[j]);
	l16si	a3, a13, 0	# MEM[base: _5146, offset: 0B], tmp2591
# @OPUS@\upstream\celt\bands.c:478:       r = Y[j];
	l16si	a6, a5, 0	# MEM[base: _5144, offset: 0B], r
# @OPUS@\upstream\celt\bands.c:477:       l = MULT16_16_P15(mid, X[j]);
	mull	a3, a3, a15	# tmp2594, tmp2591, imid
	addmi	a3, a3, 0x4000	# tmp2595, tmp2594,
# @OPUS@\upstream\celt\bands.c:477:       l = MULT16_16_P15(mid, X[j]);
	slli	a3, a3, 1	# tmp2597, tmp2595,
	srai	a3, a3, 16	# l, tmp2597,
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	sub	a4, a3, a6	# tmp2600, l, r
	mul16s	a4, a4, a14	# tmp2601, tmp2600, _2401
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	add.n	a3, a3, a6	# tmp2604, l, r
	mul16s	a3, a3, a2	# tmp2605, tmp2604, _2406
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	add.n	a4, a4, a10	# tmp2602, tmp2601, _2425
	ssr	a7	# _2423
	sra	a4, a4	# tmp2603, tmp2602
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	add.n	a3, a3, a9	# tmp2606, tmp2605, _2434
# @OPUS@\upstream\celt\bands.c:479:       X[j] = EXTRACT16(PSHR32(MULT16_16(lgain, SUB16(l,r)), kl+1));
	s16i	a4, a13, 0	# MEM[base: _5146, offset: 0B], tmp2603
# @OPUS@\upstream\celt\bands.c:480:       Y[j] = EXTRACT16(PSHR32(MULT16_16(rgain, ADD16(l,r)), kr+1));
	ssr	a11	# _2432
	sra	a3, a3	# tmp2607, tmp2606
	s16i	a3, a5, 0	# MEM[base: _5144, offset: 0B], tmp2607
	addi.n	a13, a13, 2	# ivtmp$571, ivtmp$571,
	addi.n	a5, a5, 2	# ivtmp$572, ivtmp$572,
# @OPUS@\upstream\celt\bands.c:473:    for (j=0;j<N;j++)
	bne	a8, a13, .L665	# _5139, ivtmp$571,
	l32i	a15, sp, 112	# %sfp, Y
	j	.L590		#
.L664:
# @OPUS@\upstream\celt\bands.c:1394:          for (j=0;j<N;j++)
	l32i	a8, sp, 128	# %sfp,
	blti	a8, 1, .L481	#,,
.L690:
	l32i	a9, sp, 128	# %sfp,
	mov.n	a2, a15	# ivtmp$485, Y
	slli	a4, a9, 1	# tmp2608,,
	add.n	a4, a15, a4	# _5335, ivtmp$485, tmp2608
.L666:
# @OPUS@\upstream\celt\bands.c:1395:             Y[j] = -Y[j];
	l16ui	a3, a2, 0	# MEM[base: _1805, offset: 0B],
	neg	a3, a3	# tmp2610, MEM[base: _1805, offset: 0B]
	s16i	a3, a2, 0	# MEM[base: _1805, offset: 0B], tmp2610
	addi.n	a2, a2, 2	# ivtmp$485, ivtmp$485,
# @OPUS@\upstream\celt\bands.c:1394:          for (j=0;j<N;j++)
	bne	a2, a4, .L666	# ivtmp$485, _5335,
.L481:
	movi.n	a10, 0	#,
	mov.n	a2, a12	# _5354, prephitmp_4270
	s32i	a10, sp, 404	# dual_stereo,
	j	.L461		#
.L462:
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	movi.n	a7, 0	# iftmp$113_257,
	beqi	a13, -1, .L667	# effective_lowband,,
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	l32i	a11, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1702:                   effective_lowband != -1 ? norm+effective_lowband : NULL, LM,
	slli	a13, a13, 1	# tmp2611, effective_lowband,
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	add.n	a7, a11, a13	# iftmp$113_257,, tmp2611
.L667:
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	l32i	a12, sp, 116	# %sfp,
	l32i	a8, sp, 200	# %sfp,
	beq	a12, a8, .L668	#,,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	l32i	a9, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	l32i	a10, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	l16si	a2, a9, 0	# MEM[base: _4590, offset: 0B], tmp2612
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	l32i	a11, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	ssl	a10	#
	sll	a2, a2	# tmp2615, tmp2612
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	sub	a2, a2, a11	# tmp2616, tmp2615,
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	l32i	a12, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	slli	a2, a2, 1	# tmp2617, tmp2616,
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	add.n	a15, a12, a2	# Y,, tmp2617
.L668:
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	l32r	a8, .LC51	#,
	l32i	a9, sp, 168	# %sfp,
	l32i	a10, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1703:                   last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm|y_cm);
	or	a14, a6, a14	# _201, x_cm, y_cm
# @OPUS@\upstream\celt\bands.c:1701:             x_cm = quant_band(&ctx, X, N, b, B,
	l32i	a5, sp, 136	# %sfp,
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	s32i.n	a14, sp, 16	#, _201
	s32i.n	a9, sp, 12	#,
	s32i.n	a8, sp, 8	#,
	s32i.n	a15, sp, 4	#, Y
	s32i.n	a10, sp, 0	#,
	addi	a2, sp, 32	#,,
	call0	quant_band		#
	extui	a12, a2, 0, 8	# prephitmp_4270,
	movi.n	a11, 0	#,
	mov.n	a2, a12	# _5354, prephitmp_4270
	s32i	a11, sp, 404	# dual_stereo,
.L461:
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	l32i	a14, sp, 156	# %sfp,
	l32i	a8, sp, 248	# %sfp,
	l32i	a9, sp, 268	# %sfp,
	sub	a3, a14, a8	# tmp2619,,
# @OPUS@\upstream\celt\bands.c:1707:       collapse_masks[i*C+0] = (unsigned char)x_cm;
	s8i	a12, a14, 0	# MEM[base: _4575, offset: 0B], prephitmp_4270
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	add.n	a3, a3, a9	# tmp2621, tmp2619,
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	l32i	a10, sp, 164	# %sfp,
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	s8i	a2, a3, 0	# MEM[base: _4565, offset: 0B], _5354
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	l32i.n	a2, a10, 0	# MEM[base: _4564, offset: 0B], MEM[base: _4564, offset: 0B]
	l32i	a12, sp, 160	# %sfp,
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	l32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	l32i	a8, sp, 420	# balance,
# @OPUS@\upstream\celt\bands.c:1712:       update_lowband = b>(N<<BITRES);
	l32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	add.n	a2, a12, a2	# tmp2622,, MEM[base: _4564, offset: 0B]
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	addi.n	a14, a14, 1	#,,
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	add.n	a8, a8, a2	#,, tmp2622
# @OPUS@\upstream\celt\bands.c:1712:       update_lowband = b>(N<<BITRES);
	l32i	a9, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:1708:       collapse_masks[i*C+C-1] = (unsigned char)y_cm;
	s32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\celt\bands.c:1712:       update_lowband = b>(N<<BITRES);
	slli	a3, a11, 3	# tmp2624,,
# @OPUS@\upstream\celt\bands.c:1709:       balance += pulses[i] + tell;
	s32i	a8, sp, 420	# balance,
# @OPUS@\upstream\celt\bands.c:1712:       update_lowband = b>(N<<BITRES);
	movi.n	a14, 1	# tmp2625,
	blt	a3, a9, .L669	# tmp2624,,
	movi.n	a14, 0	# tmp2625,
.L669:
	l32i	a11, sp, 144	# %sfp,
	l32i	a12, sp, 156	# %sfp,
	l32i	a9, sp, 164	# %sfp,
	l32i	a8, sp, 204	# %sfp,
# @OPUS@\upstream\celt\bands.c:1715:       ctx.avoid_split_noise = 0;
	movi.n	a10, 0	#,
	addi.n	a11, a11, 2	#,,
	s32i	a10, sp, 88	# ctx.avoid_split_noise,
	s32i	a11, sp, 144	# %sfp,
	add.n	a12, a12, a8	#,,
	addi.n	a9, a9, 4	#,,
# @OPUS@\upstream\celt\bands.c:1517:    for (i=start;i<end;i++)
	l32i	a10, sp, 116	# %sfp,
	l32i	a11, sp, 244	# %sfp,
	s32i	a12, sp, 156	# %sfp,
	s32i	a9, sp, 164	# %sfp,
	bne	a10, a11, .L670	#,,
	l32i	a4, sp, 72	# ctx.seed, pretmp_5341
.L434:
# @OPUS@\upstream\celt\bands.c:1717:    *seed = ctx.seed;
	l32i	a12, sp, 436	# seed,
# @OPUS@\upstream\celt\bands.c:1719:    RESTORE_STACK;
	l32i	a2, sp, 100	# _saved_stack,
	l32i	a3, sp, 104	# _saved_stack,
# @OPUS@\upstream\celt\bands.c:1717:    *seed = ctx.seed;
	s32i.n	a4, a12, 0	# *seed_309(D), pretmp_5341
# @OPUS@\upstream\celt\bands.c:1719:    RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\bands.c:1720: }
	l32i	a0, sp, 380	#,
	movi	a9, 0x180	#,
	l32i	a12, sp, 376	#,
	l32i	a13, sp, 372	#,
	l32i	a14, sp, 368	#,
	l32i	a15, sp, 364	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L558:
# @OPUS@\upstream\celt\rate.h:74:    if (bits- (lo == 0 ? -1 : (int)cache[lo]) <= (int)cache[hi]-bits)
	l32i	a14, sp, 188	# %sfp,
	bge	a6, a14, .L560	# _4877,,
	j	.L671		#
.L607:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	l32i	a8, sp, 216	# %sfp,
	l32i	a9, sp, 428	# LM,
	l32i	a5, sp, 256	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a2, sp, 132	# %sfp,
	s32i.n	a12, sp, 8	#, fill
	s32i.n	a8, sp, 4	#,
	s32i.n	a9, sp, 0	#,
	movi.n	a7, 0	#,
	mov.n	a6, a13	#, B
	mov.n	a3, a15	#, Y
	call0	quant_partition		#
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	bnez.n	a2, .L672	# ctx.resynth,
# @OPUS@\upstream\celt\bands.c:1370:          cm |= quant_band(ctx, Y, N, sbits, B, NULL, LM, NULL, side, NULL, fill>>B);
	l32i	a10, sp, 236	# %sfp,
	l32i	a11, sp, 120	# %sfp,
	or	a12, a10, a11	# cm,,
	extui	a12, a12, 0, 8	# prephitmp_4270, cm
	j	.L481		#
.L606:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	s32i.n	a12, sp, 8	#, fill
	l32i	a8, sp, 428	# LM,
	l32i	a12, sp, 216	# %sfp,
	l32i	a5, sp, 256	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a2, sp, 132	# %sfp,
	s32i.n	a12, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	movi.n	a7, 0	#,
	mov.n	a6, a13	#, B
	mov.n	a3, a15	#, Y
	call0	quant_partition		#
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a9, sp, 36	# ctx.resynth,
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	s32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	bnez.n	a9, .L614	#,
# @OPUS@\upstream\celt\bands.c:1370:          cm |= quant_band(ctx, Y, N, sbits, B, NULL, LM, NULL, side, NULL, fill>>B);
	l32i	a10, sp, 236	# %sfp,
	or	a12, a10, a2	# cm,,
	extui	a12, a12, 0, 8	# prephitmp_4270, cm
	j	.L481		#
.L638:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	s32i.n	a12, sp, 8	#, fill
	l32i	a8, sp, 428	# LM,
	l32i	a12, sp, 216	# %sfp,
	addi	a11, sp, 32	#,,
	l32i	a5, sp, 256	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	s32i.n	a12, sp, 4	#,
	s32i.n	a8, sp, 0	#,
	movi.n	a7, 0	#,
	mov.n	a6, a13	#, B
	mov.n	a3, a15	#, Y
	mov.n	a2, a11	#,
	s32i	a11, sp, 132	# %sfp,
	call0	quant_partition		#
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	beqz.n	a2, .L674	# ctx.resynth,
	j	.L673		#
.L637:
# @OPUS@\upstream\celt\bands.c:1206:    cm = quant_partition(ctx, X, N, b, B, lowband, LM, gain, fill);
	l32i	a10, sp, 216	# %sfp,
	l32i	a11, sp, 428	# LM,
	addi	a9, sp, 32	#,,
	l32i	a5, sp, 256	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	s32i.n	a12, sp, 8	#, fill
	s32i.n	a10, sp, 4	#,
	s32i.n	a11, sp, 0	#,
	movi.n	a7, 0	#,
	mov.n	a6, a13	#, B
	mov.n	a3, a15	#, Y
	mov.n	a2, a9	#,
	s32i	a9, sp, 132	# %sfp,
	call0	quant_partition		#
	s32i	a2, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:1209:    if (ctx->resynth)
	l32i.n	a2, sp, 36	# ctx.resynth, ctx.resynth
	bnez.n	a2, .L645	# ctx.resynth,
	j	.L674		#
.L506:
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i	a12, sp, 132	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	sub	a2, a2, a12	#,,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a8, a8, a2	#,,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	s32i	a2, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	s32i	a8, sp, 188	# %sfp,
	j	.L675		#
.L503:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a13	#, qn
	slli	a2, a12, 14	#, x,
	call0	__udivsi3		#
	s32i	a2, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	l32i	a9, sp, 120	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	l32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	sub	a2, a2, a9	#,,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	sub	a10, a10, a2	#,,
# @OPUS@\upstream\celt\bands.c:895:    if (itheta == 0)
	l32i	a11, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:892:    qalloc = ec_tell_frac(ec) - tell;
	s32i	a2, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:893:    *b -= qalloc;
	s32i	a10, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:895:    if (itheta == 0)
	bnez.n	a11, .L675	#,
	j	.L742		#
.L949:
# @OPUS@\upstream\celt\bands.c:422:    for (j=0;j<N;j++)
	l32i	a12, sp, 128	# %sfp,
	bgei	a12, 1, .L499	#,,
	j	.L506		#
.L491:
# @OPUS@\upstream\celt\bands.c:799:          int x0 = qn/2;
	srai	a5, a12, 1	# x0, _943,
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	addi.n	a12, a5, 1	# _1357, x0,
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	slli	a4, a12, 1	# tmp2638, _1357,
	add.n	a4, a4, a12	# _1358, tmp2638, _1357
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	add.n	a7, a5, a4	# ft$146_705, x0, _1358
# @OPUS@\upstream\celt\bands.c:807:             fs=ec_decode(ec,ft);
	mov.n	a3, a7	#, ft$146_705
	mov.n	a2, a14	#, ec
	s32i	a4, sp, 348	#,
	s32i	a5, sp, 344	#,
	s32i	a7, sp, 340	#,
	call0	ec_decode		#
# @OPUS@\upstream\celt\bands.c:808:             if (fs<(x0+1)*p0)
	l32i	a4, sp, 348	#,
	l32i	a5, sp, 344	#,
	l32i	a7, sp, 340	#,
	blt	a2, a4, .L676	# _706, _1358,
	j	.L946		#
.L680:
# @OPUS@\upstream\celt\bands.c:799:          int x0 = qn/2;
	srai	a4, a12, 1	# x0, _943,
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	addi.n	a3, a4, 1	# tmp2640, x0,
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	slli	a2, a3, 1	# tmp2642, tmp2640,
	add.n	a2, a2, a3	# tmp2643, tmp2642, tmp2640
# @OPUS@\upstream\celt\bands.c:800:          int ft = p0*(x0+1) + x0;
	add.n	a5, a2, a4	# ft, tmp2643, x0
# @OPUS@\upstream\celt\bands.c:804:             ec_encode(ec,x<=x0?p0*x:(x-1-x0)+(x0+1)*p0,x<=x0?p0*(x+1):(x-x0)+(x0+1)*p0,ft);
	bge	a4, a6, .L678	# x0, down,
	j	.L947		#
.L493:
# @OPUS@\upstream\celt\bands.c:795:       if (stereo && N>2)
	l32i	a8, sp, 128	# %sfp,
	bgei	a8, 3, .L680	#,,
	j	.L948		#
.L486:
# @OPUS@\upstream\celt\bands.c:752:    if (encode)
	l32i	a9, sp, 240	# %sfp,
	bnez.n	a9, .L487	#,
.L980:
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
	mov.n	a12, a2	# _770,
# @OPUS@\upstream\celt\bands.c:731:    int inv=0;
	movi.n	a13, 0	# inv,
	j	.L488		#
.L421:
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	l32i	a12, sp, 176	# %sfp, tmp2645
	s32i	a4, sp, 220	# %sfp, prephitmp_4238
	l32i	a4, sp, 176	# %sfp, prephitmp_4238
	movnez	a12, a14, a13	# tmp2645, tmp1559, encode
# @OPUS@\upstream\celt\bands.c:1452:    int C = Y_ != NULL ? 2 : 1;
	s32i	a14, sp, 204	# %sfp, tmp1559
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	extui	a12, a12, 0, 8	# _601, tmp2645
# @OPUS@\upstream\celt\bands.c:1454:    int theta_rdo = encode && Y_!=NULL && !dual_stereo && complexity>=8;
	mov.n	a14, a4	# iftmp$66_247, prephitmp_4238
	j	.L422		#
.L625:
# @OPUS@\upstream\celt\bands.c:1387:    if (ctx->resynth)
	l32i	a10, sp, 132	# %sfp,
	extui	a12, a12, 0, 8	# prephitmp_4270, cm
	beqz.n	a10, .L481	#,
	j	.L684		#
.L517:
# @OPUS@\upstream\celt\bands.c:1309:       mbits -= sbits;
	l32i	a9, sp, 188	# %sfp,
	mov.n	a10, a8	#,
# @OPUS@\upstream\celt\bands.c:1311:       ctx->remaining_bits -= qalloc+sbits;
	l32i	a8, sp, 228	# %sfp,
	addi	a12, a11, -8	# tmp2648,,
	sub	a12, a12, a8	# tmp2649, tmp2648,
# @OPUS@\upstream\celt\bands.c:1309:       mbits -= sbits;
	addi	a9, a9, -8	#,,
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	l32r	a2, .LC55	#, tmp2650
# @OPUS@\upstream\celt\bands.c:1311:       ctx->remaining_bits -= qalloc+sbits;
	s32i	a12, sp, 64	# ctx.remaining_bits, tmp2649
# @OPUS@\upstream\celt\bands.c:1309:       mbits -= sbits;
	s32i	a9, sp, 188	# %sfp,
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	bge	a2, a10, .L743	# tmp2650,,
	l32i	a11, sp, 172	# %sfp,
	s32i	a15, sp, 132	# %sfp, Y
	s32i	a11, sp, 228	# %sfp,
	j	.L685		#
.L518:
# @OPUS@\upstream\celt\bands.c:1311:       ctx->remaining_bits -= qalloc+sbits;
	l32i	a8, sp, 228	# %sfp,
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	l32r	a2, .LC55	#, tmp2652
# @OPUS@\upstream\celt\bands.c:1311:       ctx->remaining_bits -= qalloc+sbits;
	sub	a12, a14, a8	# tmp2651,,
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	l32i	a9, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:1311:       ctx->remaining_bits -= qalloc+sbits;
	s32i	a12, sp, 64	# ctx.remaining_bits, tmp2651
# @OPUS@\upstream\celt\bands.c:1313:       x2 = c ? Y : X;
	bge	a2, a9, .L744	# tmp2652,,
	l32i	a10, sp, 172	# %sfp,
	movi.n	a11, 1	#,
	movi.n	a12, -1	#,
	s32i	a15, sp, 132	# %sfp, Y
	s32i	a10, sp, 228	# %sfp,
	s32i	a11, sp, 256	# %sfp,
	s32i	a12, sp, 252	# %sfp,
	j	.L520		#
.L948:
# @OPUS@\upstream\celt\bands.c:818:             ec_enc_uint(ec, itheta, qn+1);
	mov.n	a3, a6	#, down
	addi.n	a4, a13, 1	#, qn,
	mov.n	a2, a14	#, ec
	s32i	a6, sp, 344	#,
	call0	ec_enc_uint		#
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i	a6, sp, 344	#,
	mov.n	a3, a13	#, qn
	slli	a2, a6, 14	#, down,
	call0	__udivsi3		#
	s32i	a2, sp, 196	# %sfp,
# @OPUS@\upstream\celt\bands.c:860:          if (itheta==0)
	bnez.n	a2, .L949	#,
	j	.L498		#
.L937:
# @OPUS@\upstream\celt\bands.c:820:             itheta = ec_dec_uint(ec, qn+1);
	addi.n	a3, a13, 1	#, qn,
	mov.n	a2, a14	#, ec
	call0	ec_dec_uint		#
	mov.n	a12, a2	# x,
	j	.L503		#
.L482:
	mov.n	a3, a9	# N2,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	addi	a2, a2, -16	# offset, _582,
	j	.L687		#
.L936:
# @OPUS@\upstream\celt\bands.c:658:    int N2 = 2*N-1;
	slli	a3, a9, 1	# tmp2659, tmp10,
# @OPUS@\upstream\celt\bands.c:748:    offset = (pulse_cap>>1) - (stereo&&N==2 ? QTHETA_OFFSET_TWOPHASE : QTHETA_OFFSET);
	addi	a2, a2, -4	# offset, _582,
# @OPUS@\upstream\celt\bands.c:658:    int N2 = 2*N-1;
	addi.n	a3, a3, -1	# N2, tmp2659,
	j	.L687		#
.L443:
# @OPUS@\upstream\celt\bands.c:1556:       if (resynth && (M*eBands[i]-N >= M*eBands[start] || i==start+1) && (update_lowband || lowband_offset==0))
	l32i	a11, sp, 192	# %sfp,
	beqz.n	a11, .L749	#,
	bbci	a14, 0, .L688	# update_lowband,,
.L749:
	l32i	a14, sp, 260	# %sfp,
	s32i	a14, sp, 192	# %sfp,
	j	.L688		#
.L590:
# @OPUS@\upstream\celt\bands.c:1391:       if (inv)
	l32i	a8, sp, 240	# %sfp,
	beqz.n	a8, .L481	#,
	j	.L690		#
.L727:
# @OPUS@\upstream\celt\bands.c:1083:          if (ctx->resynth)
	movi.n	a12, 0	# prephitmp_4270,
.L565:
# @OPUS@\upstream\celt\bands.c:1333:       y2[0] = -sign*x2[1];
	l32i	a9, sp, 132	# %sfp,
	l32i	a10, sp, 252	# %sfp,
	l16ui	a2, a9, 2	# MEM[(celt_norm *)iftmp$125_1368 + 2B],
	l32i	a11, sp, 228	# %sfp,
	mul16s	a2, a2, a10	# tmp2669, MEM[(celt_norm *)iftmp$125_1368 + 2B],
# @OPUS@\upstream\celt\bands.c:1334:       y2[1] = sign*x2[0];
	l32i	a14, sp, 256	# %sfp,
# @OPUS@\upstream\celt\bands.c:1333:       y2[0] = -sign*x2[1];
	s16i	a2, a11, 0	# *iftmp$126_1883, tmp2669
# @OPUS@\upstream\celt\bands.c:1334:       y2[1] = sign*x2[0];
	l16ui	a2, a9, 0	# *iftmp$125_1368,
	mul16s	a2, a2, a14	# tmp2671, *iftmp$125_1368,
	s16i	a2, a11, 2	# MEM[(celt_norm *)iftmp$126_1883 + 2B], tmp2671
	j	.L481		#
.L535:
	l32i	a11, sp, 196	# %sfp, lowband
# @OPUS@\upstream\celt\bands.c:1174:       if (lowband)
	bnez.n	a11, .L691	# lowband,
	j	.L532		#
.L941:
# @OPUS@\upstream\celt\bands.c:1186:       if (lowband)
	l32i	a9, sp, 152	# %sfp,
	bnez.n	a9, .L692	#,
	j	.L542		#
.L514:
	l32i	a11, sp, 324	# %sfp,
	l32i	a10, sp, 64	# ctx.remaining_bits,
	extui	a11, a11, 0, 8	#,
# @OPUS@\upstream\celt\bands.c:1299:    if (N==2)
	l32i	a12, sp, 128	# %sfp,
	s32i	a10, sp, 252	# %sfp,
	s32i	a11, sp, 312	# %sfp,
	mov.n	a14, a10	#,
	beqi	a12, 2, .L518	#,,
	j	.L516		#
.L490:
# @OPUS@\upstream\celt\bands.c:758:       itheta = stereo_itheta(X, Y, stereo, N, ctx->arch);
	l32i	a6, sp, 76	# ctx.arch,
	l32i	a5, sp, 128	# %sfp,
	l32i	a2, sp, 172	# %sfp,
	movi.n	a4, 1	#,
	mov.n	a3, a15	#, Y
	call0	stereo_itheta		#
	mov.n	a3, a2	# itheta,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	mov.n	a2, a14	#, ec
	s32i	a3, sp, 340	#,
	call0	ec_tell_frac		#
	l32i	a3, sp, 340	#,
# @OPUS@\upstream\celt\bands.c:765:          if (!stereo || ctx->theta_round == 0)
	l32i	a4, sp, 80	# ctx.theta_round, _596
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	s32i	a2, sp, 132	# %sfp,
	mull	a6, a13, a3	# _5282, qn, itheta
# @OPUS@\upstream\celt\bands.c:765:          if (!stereo || ctx->theta_round == 0)
	beqz.n	a4, .L693	# _596,
	j	.L950		#
.L487:
# @OPUS@\upstream\celt\bands.c:758:       itheta = stereo_itheta(X, Y, stereo, N, ctx->arch);
	l32i	a6, sp, 76	# ctx.arch,
	l32i	a5, sp, 128	# %sfp,
	l32i	a2, sp, 172	# %sfp,
	movi.n	a4, 1	#,
	mov.n	a3, a15	#, Y
	call0	stereo_itheta		#
	mov.n	a13, a2	# itheta,
# @OPUS@\upstream\celt\bands.c:760:    tell = ec_tell_frac(ec);
	mov.n	a2, a14	#, ec
	call0	ec_tell_frac		#
	mov.n	a12, a2	# _770,
	j	.L682		#
.L696:
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32r	a9, .LC51	#,
	l32i	a10, sp, 168	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a11, sp, 144	# %sfp,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	s32i.n	a6, sp, 16	#, x_cm
	s32i.n	a10, sp, 12	#,
	s32i.n	a9, sp, 8	#,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l16si	a2, a11, 0	# MEM[base: _4590, offset: 0B], tmp2679
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	s32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a9, sp, 428	# LM,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	l32i	a10, sp, 212	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	ssl	a9	#
	sll	a2, a2	# tmp2682, tmp2679
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	sub	a2, a2, a10	# tmp2683, tmp2682,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32i	a11, sp, 184	# %sfp,
# @OPUS@\upstream\celt\bands.c:1619:                last?NULL:norm+M*eBands[i]-norm_offset, Q15ONE, lowband_scratch, x_cm);
	slli	a2, a2, 1	# tmp2684, tmp2683,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	addi	a12, sp, 32	#,,
	add.n	a2, a11, a2	# tmp2685,, tmp2684
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	s32i.n	a2, sp, 4	#, tmp2685
	movi.n	a7, 0	#,
	mov.n	a5, a8	#, _159
	mov.n	a2, a12	#,
	s32i.n	a9, sp, 0	#,
	s32i	a12, sp, 132	# %sfp,
	s32i	a8, sp, 340	#,
	call0	quant_band		#
	mov.n	a12, a2	# x_cm,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	movi.n	a7, 0	# iftmp$102_1679,
	l32i	a8, sp, 340	#,
	j	.L695		#
.L459:
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32i	a12, sp, 116	# %sfp,
	l32i	a9, sp, 200	# %sfp,
	bne	a12, a9, .L696	#,,
	j	.L951		#
.L726:
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	mov.n	a8, a7	# lo$230_1503, mid$228_1847
	mov.n	a4, a5	# q, hi
.L559:
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	add.n	a8, a2, a8	# tmp2687, tmp2727, lo$230_1503
	l8ui	a5, a8, 0	# *_4210, *_4210
# @OPUS@\upstream\celt\bands.c:1058:       ctx->remaining_bits -= curr_bits;
	l32i	a3, sp, 64	# ctx.remaining_bits, ctx.remaining_bits
# @OPUS@\upstream\celt\rate.h:86:    return pulses == 0 ? 0 : cache[pulses]+1;
	addi.n	a5, a5, 1	# curr_bits, *_4210,
# @OPUS@\upstream\celt\bands.c:1058:       ctx->remaining_bits -= curr_bits;
	sub	a3, a3, a5	# _384, ctx.remaining_bits, curr_bits
	s32i	a3, sp, 64	# ctx.remaining_bits, _384
# @OPUS@\upstream\celt\bands.c:1061:       while (ctx->remaining_bits < 0 && q > 0)
	bltz	a3, .L561	# _384,
	j	.L698		#
.L460:
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32r	a10, .LC51	#,
	l32i	a12, sp, 168	# %sfp,
	l32i	a9, sp, 428	# LM,
	addi	a11, sp, 32	#,,
	s32i.n	a6, sp, 16	#, x_cm
	movi.n	a2, 0	#,
	l32i	a6, sp, 180	# %sfp,
	l32i	a4, sp, 128	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	s32i.n	a12, sp, 12	#,
	s32i.n	a10, sp, 8	#,
	s32i.n	a2, sp, 4	#,
	s32i.n	a9, sp, 0	#,
	mov.n	a5, a8	#, _159
	mov.n	a2, a11	#,
	s32i	a10, sp, 140	# %sfp,
	s32i	a8, sp, 340	#,
	s32i	a11, sp, 132	# %sfp,
	call0	quant_band		#
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	l32i	a10, sp, 452	# norm2_scratch,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	mov.n	a12, a2	# x_cm,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	add.n	a7, a10, a13	# iftmp$102_1679,, tmp1761
	movi.n	a2, 0	# iftmp$104_254,
	l32i	a8, sp, 340	#,
	l32i	a9, sp, 428	# LM,
	j	.L699		#
.L951:
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	l32r	a11, .LC51	#,
	l32i	a9, sp, 168	# %sfp,
	s32i	a11, sp, 140	# %sfp,
	s32i.n	a11, sp, 8	#,
	l32i	a11, sp, 428	# LM,
	addi	a12, sp, 32	#,,
	movi.n	a10, 0	#,
	s32i.n	a6, sp, 16	#, x_cm
	l32i	a4, sp, 128	# %sfp,
	l32i	a6, sp, 180	# %sfp,
	l32i	a3, sp, 172	# %sfp,
	s32i.n	a9, sp, 12	#,
	mov.n	a7, a10	#,
	mov.n	a5, a8	#, _159
	mov.n	a2, a12	#,
	s32i.n	a10, sp, 4	#,
	s32i.n	a11, sp, 0	#,
	s32i	a12, sp, 132	# %sfp,
	s32i	a8, sp, 340	#,
	call0	quant_band		#
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	movi.n	a7, 0	# iftmp$102_1679,
# @OPUS@\upstream\celt\bands.c:1617:          x_cm = quant_band(&ctx, X, N, b/2, B,
	mov.n	a12, a2	# x_cm,
	l32i	a8, sp, 340	#,
# @OPUS@\upstream\celt\bands.c:1620:          y_cm = quant_band(&ctx, Y, N, b/2, B,
	mov.n	a2, a7	# iftmp$104_254, iftmp$102_1679
	l32i	a9, sp, 428	# LM,
	j	.L699		#
	.size	quant_all_bands, .-quant_all_bands
	.section	.rodata.bit_deinterleave_table$4337,"a"
	.align	4
	.type	bit_deinterleave_table$4337, @object
	.size	bit_deinterleave_table$4337, 16
bit_deinterleave_table$4337:
	.byte	0
	.byte	3
	.byte	12
	.byte	15
	.byte	48
	.byte	51
	.byte	60
	.byte	63
	.byte	-64
	.byte	-61
	.byte	-52
	.byte	-49
	.byte	-16
	.byte	-13
	.byte	-4
	.byte	-1
	.section	.rodata.bit_interleave_table$4327,"a"
	.align	4
	.type	bit_interleave_table$4327, @object
	.size	bit_interleave_table$4327, 16
bit_interleave_table$4327:
	.byte	0
	.byte	1
	.byte	1
	.byte	1
	.byte	2
	.byte	3
	.byte	3
	.byte	3
	.byte	2
	.byte	3
	.byte	3
	.byte	3
	.byte	2
	.byte	3
	.byte	3
	.byte	3
	.section	.rodata.exp2_table8$4166,"a"
	.align	4
	.type	exp2_table8$4166, @object
	.size	exp2_table8$4166, 16
exp2_table8$4166:
	.short	16384
	.short	17866
	.short	19483
	.short	21247
	.short	23170
	.short	25267
	.short	27554
	.short	30048
	.section	.rodata.ordery_table,"a"
	.align	4
	.type	ordery_table, @object
	.size	ordery_table, 120
ordery_table:
	.word	1
	.word	0
	.word	3
	.word	0
	.word	2
	.word	1
	.word	7
	.word	0
	.word	4
	.word	3
	.word	6
	.word	1
	.word	5
	.word	2
	.word	15
	.word	0
	.word	8
	.word	7
	.word	12
	.word	3
	.word	11
	.word	4
	.word	14
	.word	1
	.word	9
	.word	6
	.word	13
	.word	2
	.word	10
	.word	5
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
