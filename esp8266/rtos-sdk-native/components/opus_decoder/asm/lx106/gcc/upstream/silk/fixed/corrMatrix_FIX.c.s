# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/corrMatrix_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"corrMatrix_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\corrMatrix_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\corrMatrix_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\corrMatrix_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\corrMatrix_FIX.c.s.raw
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
	.section	.text.silk_corrVector_FIX,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_corrVector_FIX
	.type	silk_corrVector_FIX, @function
# Function: silk_corrVector_FIX
# Module: upstream/silk/fixed/corrMatrix_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main_FIX.h"
# C context:
# C context: /* Calculates correlation vector X'*t */
# C context: void silk_corrVector_FIX(
# C context: const opus_int16                *x,                                     /* I    x vector [L + order - 1] used to form data matrix X                         */
# C context: const opus_int16                *t,                                     /* I    Target vector [L]                                                           */
# C context: const opus_int                  L,                                      /* I    Length of vectors                                                           */
# C context: const opus_int                  order,                                  /* I    Max lag for correlation                                                     */
silk_corrVector_FIX:
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:53:     ptr1 = &x[ order - 1 ]; /* Points to first sample of column 0 of X: X[:,0] */
	slli	a10, a5, 1	# tmp77, order,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:48: {
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:53:     ptr1 = &x[ order - 1 ]; /* Points to first sample of column 0 of X: X[:,0] */
	addi	a10, a10, -2	# _3, tmp77,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:48: {
	s32i.n	a0, sp, 44	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:48: {
	mov.n	a13, a3	# t, t
	mov.n	a12, a4	# L, L
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:53:     ptr1 = &x[ order - 1 ]; /* Points to first sample of column 0 of X: X[:,0] */
	add.n	a14, a2, a10	# ptr1, x, _3
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:56:     if( rshifts > 0 ) {
	bgei	a7, 1, .L2	# rshifts,,
	slli	a2, a5, 2	# tmp89, order,
	add.n	a2, a6, a2	#, ivtmp$37, tmp89
	s32i.n	a2, sp, 0	# %sfp,
	mov.n	a15, a6	# ivtmp$37, Xt
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:68:         for( lag = 0; lag < order; lag++ ) {
	bgei	a5, 1, .L9	# order,,
	j	.L1		#
.L2:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:58:         for( lag = 0; lag < order; lag++ ) {
	blti	a5, 1, .L1	# order,,
	slli	a9, a4, 1	# _54, L,
	addi.n	a10, a10, 2	# tmp79, _3,
	sub	a10, a9, a10	# tmp80, _54, tmp79
	mov.n	a11, a9	# tmp83, _54
	add.n	a10, a10, a14	# _26, tmp80, ptr1
	add.n	a9, a14, a9	# ivtmp$31, ptr1, _54
	neg	a11, a11	# tmp84, tmp83
	j	.L5		#
.L6:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:61:                 inner_prod = silk_ADD_RSHIFT32( inner_prod, silk_SMULBB( ptr1[ i ], ptr2[i] ), rshifts );
	l16ui	a2, a3, 0	# MEM[base: _85, offset: 0B],
	l16ui	a8, a4, 0	# MEM[base: _84, offset: 0B],
	addi.n	a3, a3, 2	# ivtmp$21, ivtmp$21,
	mul16s	a2, a2, a8	# tmp85, MEM[base: _85, offset: 0B], MEM[base: _84, offset: 0B]
	addi.n	a4, a4, 2	# ivtmp$22, ivtmp$22,
	ssr	a7	# rshifts
	sra	a2, a2	# tmp88, tmp85
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:61:                 inner_prod = silk_ADD_RSHIFT32( inner_prod, silk_SMULBB( ptr1[ i ], ptr2[i] ), rshifts );
	add.n	a5, a5, a2	# inner_prod, inner_prod, tmp88
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:60:             for( i = 0; i < L; i++ ) {
	bne	a9, a3, .L6	# ivtmp$31, ivtmp$21,
.L8:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:63:             Xt[ lag ] = inner_prod; /* X[:,lag]'*t */
	s32i.n	a5, a6, 0	# MEM[base: _52, offset: 0B], inner_prod
	addi	a9, a9, -2	# ivtmp$31, ivtmp$31,
	addi.n	a6, a6, 4	# ivtmp$30, ivtmp$30,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:58:         for( lag = 0; lag < order; lag++ ) {
	beq	a10, a9, .L1	# _26, ivtmp$31,
.L5:
	add.n	a3, a11, a9	# ivtmp$21, tmp84, ivtmp$31
	mov.n	a4, a13	# ivtmp$22, t
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:59:             inner_prod = 0;
	movi.n	a5, 0	# inner_prod,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:60:             for( i = 0; i < L; i++ ) {
	bgei	a12, 1, .L6	# L,,
	j	.L8		#
.L9:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:69:             Xt[ lag ] = silk_inner_prod_aligned( ptr1, ptr2, L, arch ); /* X[:,lag]'*t */
	l32i.n	a5, sp, 48	# arch,
	mov.n	a2, a14	#, ptr1
	mov.n	a4, a12	#, L
	mov.n	a3, a13	#, t
	call0	silk_inner_prod_aligned		#
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:69:             Xt[ lag ] = silk_inner_prod_aligned( ptr1, ptr2, L, arch ); /* X[:,lag]'*t */
	s32i.n	a2, a15, 0	# MEM[base: _90, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:68:         for( lag = 0; lag < order; lag++ ) {
	l32i.n	a2, sp, 0	# %sfp,
	addi.n	a15, a15, 4	# ivtmp$37, ivtmp$37,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:70:             ptr1--; /* Go to next column of X */
	addi	a14, a14, -2	# ptr1, ptr1,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:68:         for( lag = 0; lag < order; lag++ ) {
	bne	a15, a2, .L9	# ivtmp$37,,
.L1:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:73: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_corrVector_FIX, .-silk_corrVector_FIX
	.section	.text.silk_corrMatrix_FIX,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_corrMatrix_FIX
	.type	silk_corrMatrix_FIX, @function
# Function: silk_corrMatrix_FIX
# Module: upstream/silk/fixed/corrMatrix_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Calculates correlation matrix X'*X */
# C context: void silk_corrMatrix_FIX(
# C context: const opus_int16                *x,                                     /* I    x vector [L + order - 1] used to form data matrix X                         */
# C context: const opus_int                  L,                                      /* I    Length of vectors                                                           */
# C context: const opus_int                  order,                                  /* I    Max lag for correlation                                                     */
# C context: opus_int32                      *XX,                                    /* O    Pointer to X'*X correlation matrix [ order x order ]                        */
silk_corrMatrix_FIX:
	addi	sp, sp, -96	#,,
	s32i	a15, sp, 76	#,
	addi.n	a15, a4, -1	# _134, order,
	mov.n	a8, a5	# XX, XX
	s32i	a12, sp, 88	#,
	s32i	a14, sp, 80	#,
	s32i.n	a3, sp, 28	# %sfp, L
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:91:     silk_sum_sqr_shift( nrg, rshifts, x, L + order - 1 );
	add.n	a5, a15, a3	#, _134, L
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:85: {
	mov.n	a14, a4	# order, order
	mov.n	a12, a2	# x, x
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:91:     silk_sum_sqr_shift( nrg, rshifts, x, L + order - 1 );
	mov.n	a4, a2	#, x
	mov.n	a3, a7	#, rshifts
	mov.n	a2, a6	#, nrg
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:85: {
	s32i	a13, sp, 84	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:91:     silk_sum_sqr_shift( nrg, rshifts, x, L + order - 1 );
	s32i.n	a6, sp, 52	#,
	s32i.n	a8, sp, 48	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:85: {
	s32i	a0, sp, 92	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:85: {
	mov.n	a13, a7	# rshifts, rshifts
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:91:     silk_sum_sqr_shift( nrg, rshifts, x, L + order - 1 );
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:92:     energy = *nrg;
	l32i.n	a6, sp, 52	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:96:     for( i = 0; i < order - 1; i++ ) {
	l32i.n	a8, sp, 48	#,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:92:     energy = *nrg;
	l32i.n	a4, a6, 0	# *nrg_154(D), energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:96:     for( i = 0; i < order - 1; i++ ) {
	blti	a15, 1, .L16	# _134,,
	addi	a2, a12, -2	# tmp195, x,
	slli	a5, a14, 1	# tmp196, order,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:97:         energy -= silk_RSHIFT32( silk_SMULBB( x[ i ], x[ i ] ), *rshifts );
	l32i.n	a6, a13, 0	# *rshifts_155(D), _9
	mov.n	a3, a12	# ivtmp$134, x
	add.n	a5, a2, a5	# _140, tmp195, tmp196
.L17:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:97:         energy -= silk_RSHIFT32( silk_SMULBB( x[ i ], x[ i ] ), *rshifts );
	l16si	a2, a3, 0	# MEM[base: _173, offset: 0B], _6
	addi.n	a3, a3, 2	# ivtmp$134, ivtmp$134,
	mull	a2, a2, a2	# tmp199, _6, _6
	ssr	a6	# _9
	sra	a2, a2	# tmp200, tmp199
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:97:         energy -= silk_RSHIFT32( silk_SMULBB( x[ i ], x[ i ] ), *rshifts );
	sub	a4, a4, a2	# energy, energy, tmp200
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:96:     for( i = 0; i < order - 1; i++ ) {
	bne	a5, a3, .L17	# _140, ivtmp$134,
.L16:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:104:     ptr1 = &x[ order - 1 ]; /* First sample of column 0 of X */
	slli	a2, a14, 1	# tmp201, order,
	addi	a3, a2, -4	# tmp203, tmp201,
	add.n	a3, a12, a3	#, x, tmp203
	addi	a2, a2, -2	# _14, tmp201,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:102:     matrix_ptr( XX, 0, 0, order ) = energy;
	s32i.n	a4, a8, 0	# *XX_161(D), energy
	s32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:104:     ptr1 = &x[ order - 1 ]; /* First sample of column 0 of X */
	add.n	a11, a12, a2	# ptr1, x, _14
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:105:     for( j = 1; j < order; j++ ) {
	blti	a14, 2, .L15	# order,,
	l32i.n	a5, sp, 28	# %sfp,
	addi.n	a3, a5, -1	# tmp204,,
	slli	a3, a3, 1	#, tmp204,
	s32i.n	a3, sp, 32	# %sfp,
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:108:         matrix_ptr( XX, j, j, order ) = energy;
	addi.n	a3, a14, 1	#, order,
	add.n	a5, a11, a5	#, ptr1,
	s32i.n	a5, sp, 36	# %sfp,
	slli	a12, a3, 2	# _242,,
	l32i.n	a5, sp, 28	# %sfp,
	s32i.n	a3, sp, 0	# %sfp,
	l32i.n	a3, sp, 32	# %sfp,
	slli	a10, a5, 1	# tmp209,,
	sub	a9, a3, a2	# tmp206,, _14
	l32i.n	a5, sp, 36	# %sfp, ivtmp$126
	addi.n	a3, a3, 2	#,,
	addi.n	a2, a2, 2	#, _14,
	add.n	a6, a8, a12	# ivtmp$130, XX, _242
	s32i.n	a3, sp, 4	# %sfp,
	s32i.n	a2, sp, 24	# %sfp,
	add.n	a9, a9, a11	# _196, tmp206, ptr1
	neg	a10, a10	# tmp210, tmp209
.L19:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:107:         energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr1[ -j ] ), *rshifts ) );
	add.n	a2, a5, a10	# tmp213, ivtmp$126, tmp210
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:106:         energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr1[ L - j ] ), *rshifts ) );
	l16si	a3, a5, 0	# MEM[base: _236, offset: 0B], _19
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:107:         energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr1[ -j ] ), *rshifts ) );
	l16si	a2, a2, 0	# MEM[base: _208, offset: 0B], _27
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:106:         energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr1[ L - j ] ), *rshifts ) );
	l32i.n	a7, a13, 0	# *rshifts_155(D), _22
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:107:         energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr1[ -j ] ), *rshifts ) );
	mull	a2, a2, a2	# tmp216, _27, _27
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:106:         energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr1[ L - j ] ), *rshifts ) );
	mull	a3, a3, a3	# tmp218, _19, _19
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:107:         energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr1[ -j ] ), *rshifts ) );
	ssr	a7	# _22
	sra	a2, a2	# tmp217, tmp216
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:106:         energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr1[ L - j ] ), *rshifts ) );
	ssr	a7	# _22
	sra	a3, a3	# tmp219, tmp218
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:107:         energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr1[ -j ] ), *rshifts ) );
	sub	a2, a2, a3	# tmp220, tmp217, tmp219
	add.n	a4, a4, a2	# energy, energy, tmp220
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:108:         matrix_ptr( XX, j, j, order ) = energy;
	s32i.n	a4, a6, 0	# MEM[base: _207, offset: 0B], energy
	addi	a5, a5, -2	# ivtmp$126, ivtmp$126,
	add.n	a6, a6, a12	# ivtmp$130, ivtmp$130, _242
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:105:     for( j = 1; j < order; j++ ) {
	bne	a9, a5, .L19	# _196, ivtmp$126,
	j	.L44		#
.L27:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:120:                 energy += silk_RSHIFT32( silk_SMULBB( ptr1[ i ], ptr2[i] ), *rshifts );
	l32i.n	a8, a13, 0	# *rshifts_155(D), _49
	l32i.n	a5, sp, 12	# %sfp, ivtmp$61
	l32i.n	a4, sp, 44	# %sfp, ivtmp$60
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:118:             energy = 0;
	movi.n	a3, 0	# energy,
.L21:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:120:                 energy += silk_RSHIFT32( silk_SMULBB( ptr1[ i ], ptr2[i] ), *rshifts );
	l16ui	a2, a4, 0	# MEM[base: _404, offset: 0B],
	l16ui	a6, a5, 0	# MEM[base: _403, offset: 0B],
	addi.n	a4, a4, 2	# ivtmp$60, ivtmp$60,
	mul16s	a2, a2, a6	# tmp221, MEM[base: _404, offset: 0B], MEM[base: _403, offset: 0B]
	addi.n	a5, a5, 2	# ivtmp$61, ivtmp$61,
	ssr	a8	# _49
	sra	a2, a2	# tmp224, tmp221
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:120:                 energy += silk_RSHIFT32( silk_SMULBB( ptr1[ i ], ptr2[i] ), *rshifts );
	add.n	a3, a3, a2	# energy, energy, tmp224
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:119:             for( i = 0; i < L; i++ ) {
	bne	a11, a4, .L21	# _399, ivtmp$60,
.L28:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:123:             matrix_ptr( XX, lag, 0, order ) = energy;
	l32i.n	a4, sp, 20	# %sfp,
	l32i.n	a8, sp, 12	# %sfp,
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:124:             matrix_ptr( XX, 0, lag, order ) = energy;
	l32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:123:             matrix_ptr( XX, lag, 0, order ) = energy;
	s32i.n	a3, a4, 0	# MEM[base: _347, offset: 0B], energy
	add.n	a6, a8, a2	# ivtmp$43,,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:125:             for( j = 1; j < ( order - lag ); j++ ) {
	l32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:124:             matrix_ptr( XX, 0, lag, order ) = energy;
	s32i.n	a3, a5, 0	# MEM[base: _346, offset: 0B], energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:125:             for( j = 1; j < ( order - lag ); j++ ) {
	l32i.n	a4, sp, 36	# %sfp, ivtmp$41
	add.n	a5, a5, a12	# ivtmp$51, tmp4, _242
	bgei	a8, 2, .L47	#,,
.L26:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:131:             ptr2--; /* Update pointer to first sample of next column (lag) in X */
	l32i.n	a2, sp, 12	# %sfp,
	l32i.n	a3, sp, 20	# %sfp,
	l32i.n	a4, sp, 24	# %sfp,
	l32i.n	a5, sp, 8	# %sfp,
	l32i.n	a8, sp, 16	# %sfp,
	addi	a2, a2, -2	#,,
	s32i.n	a2, sp, 12	# %sfp,
	add.n	a3, a3, a4	#,,
	addi.n	a5, a5, 4	#,,
	addi.n	a8, a8, -1	#,,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:116:         for( lag = 1; lag < order; lag++ ) {
	l32i.n	a2, sp, 40	# %sfp,
	addi	a7, a7, -4	# ivtmp$78, ivtmp$78,
	s32i.n	a3, sp, 20	# %sfp,
	s32i.n	a5, sp, 8	# %sfp,
	s32i.n	a8, sp, 16	# %sfp,
	add.n	a14, a14, a4	# ivtmp$80, ivtmp$80,
	addi.n	a15, a15, 2	# ivtmp$81, ivtmp$81,
	bne	a2, a7, .L23	#, ivtmp$78,
	j	.L15		#
.L47:
	s32i.n	a11, sp, 0	# %sfp, _399
.L25:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:127:                 energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr2[ -j ] ), *rshifts ) );
	add.n	a8, a6, a10	# tmp226, ivtmp$43, tmp210
	add.n	a2, a4, a10	# tmp225, ivtmp$41, tmp210
	l16ui	a9, a8, 0	# MEM[base: _440, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:126:                 energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ), *rshifts ) );
	l16ui	a11, a6, 0	# MEM[base: _459, offset: 0B],
	l16ui	a8, a4, 0	# MEM[base: _460, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:127:                 energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr2[ -j ] ), *rshifts ) );
	l16ui	a2, a2, 0	# MEM[base: _444, offset: 0B],
	addi	a4, a4, -2	# ivtmp$41, ivtmp$41,
	mul16s	a2, a2, a9	# tmp227, MEM[base: _444, offset: 0B], MEM[base: _440, offset: 0B]
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:126:                 energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ), *rshifts ) );
	mul16s	a9, a8, a11	# tmp231,,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:127:                 energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr2[ -j ] ), *rshifts ) );
	l32i.n	a8, a13, 0	# *rshifts_155(D),
	addi	a6, a6, -2	# ivtmp$43, ivtmp$43,
	ssr	a8	#
	sra	a2, a2	# tmp230, tmp227
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:126:                 energy = silk_SUB32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ), *rshifts ) );
	ssr	a8	#
	sra	a9, a9	# tmp234, tmp231
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:127:                 energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr2[ -j ] ), *rshifts ) );
	sub	a2, a2, a9	# tmp235, tmp230, tmp234
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:128:                 matrix_ptr( XX, lag + j, j, order ) = energy;
	add.n	a8, a7, a5	# tmp236, ivtmp$78, ivtmp$51
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:127:                 energy = silk_ADD32( energy, silk_RSHIFT32( silk_SMULBB( ptr1[ -j ], ptr2[ -j ] ), *rshifts ) );
	add.n	a3, a3, a2	# energy, energy, tmp235
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:128:                 matrix_ptr( XX, lag + j, j, order ) = energy;
	add.n	a2, a8, a14	# tmp237, tmp236, ivtmp$80
	s32i.n	a3, a2, 0	# MEM[base: _429, offset: 0B], energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:129:                 matrix_ptr( XX, j, lag + j, order ) = energy;
	s32i.n	a3, a5, 0	# MEM[base: _428, offset: 0B], energy
	add.n	a5, a5, a12	# ivtmp$51, ivtmp$51, _242
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:125:             for( j = 1; j < ( order - lag ); j++ ) {
	bne	a4, a15, .L25	# ivtmp$41, ivtmp$81,
	l32i.n	a11, sp, 0	# %sfp, _399
	j	.L26		#
.L31:
	addi	a4, a12, -4	#, _242,
	s32i.n	a4, sp, 24	# %sfp,
	l32i.n	a5, sp, 0	# %sfp,
	l32i.n	a4, sp, 4	# %sfp,
	slli	a2, a15, 1	# tmp243, tmp3,
	slli	a7, a5, 2	# tmp241,,
	sub	a3, a4, a2	# tmp244,, tmp243
	l32i.n	a5, sp, 24	# %sfp,
	slli	a2, a14, 3	# tmp247, order,
	mov.n	a14, a2	# ivtmp$80, tmp247
	neg	a2, a2	#, tmp247
	add.n	a5, a8, a5	#, XX,
	s32i.n	a2, sp, 40	# %sfp,
	addi.n	a8, a8, 4	#, XX,
	add.n	a2, a11, a4	# _399, ptr1,
	s32i.n	a15, sp, 16	# %sfp, _134
	s32i.n	a11, sp, 44	# %sfp, ptr1
	add.n	a15, a11, a3	# ivtmp$81, ptr1, tmp244
	s32i.n	a5, sp, 20	# %sfp,
	s32i.n	a8, sp, 8	# %sfp,
	neg	a7, a7	# ivtmp$78, tmp241
	mov.n	a11, a2	# _399, _399
.L23:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:119:             for( i = 0; i < L; i++ ) {
	l32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:118:             energy = 0;
	movi.n	a3, 0	# energy,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:119:             for( i = 0; i < L; i++ ) {
	blti	a8, 1, .L28	#,,
	j	.L27		#
.L46:
	l32i.n	a4, sp, 0	# %sfp,
	addi	a2, a12, -4	#, _242,
	add.n	a3, a8, a2	#, XX,
	l32i.n	a5, sp, 24	# %sfp,
	slli	a7, a4, 2	# tmp252,,
	l32i.n	a4, sp, 12	# %sfp,
	s32i.n	a3, sp, 20	# %sfp,
	sub	a3, a4, a5	# _267,,
	slli	a4, a14, 3	# tmp260, order,
	l32i.n	a5, sp, 20	# %sfp,
	s32i.n	a2, sp, 8	# %sfp,
	mov.n	a6, a4	# ivtmp$119, tmp260
	slli	a2, a15, 1	# tmp256, tmp5,
	neg	a4, a4	#, tmp260
	addi.n	a3, a3, 2	#, _267,
	addi.n	a8, a8, 4	#, XX,
	s32i.n	a15, sp, 4	# %sfp, _134
	s32i.n	a12, sp, 40	# %sfp, _242
	s32i.n	a5, sp, 0	# %sfp,
	neg	a15, a7	# ivtmp$117, tmp252
	neg	a14, a2	# ivtmp$120, tmp256
	s32i.n	a4, sp, 12	# %sfp,
	s32i.n	a3, sp, 24	# %sfp,
	s32i.n	a8, sp, 36	# %sfp,
	mov.n	a12, a11	# ptr1, ptr1
.L33:
	l32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:136:             energy = silk_inner_prod_aligned( ptr1, ptr2, L, arch );
	l32i	a5, sp, 96	# arch,
	sub	a13, a8, a14	# _263,, ivtmp$120
	l32i.n	a4, sp, 28	# %sfp,
	mov.n	a3, a13	#, _263
	mov.n	a2, a12	#, ptr1
	s32i.n	a6, sp, 52	#,
	call0	silk_inner_prod_aligned		#
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:138:             matrix_ptr( XX, 0, lag, order ) = energy;
	l32i.n	a11, sp, 12	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:137:             matrix_ptr( XX, lag, 0, order ) = energy;
	l32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:138:             matrix_ptr( XX, 0, lag, order ) = energy;
	sub	a3, a11, a15	# tmp263,, ivtmp$117
	l32i.n	a11, sp, 20	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:137:             matrix_ptr( XX, lag, 0, order ) = energy;
	s32i.n	a2, a8, 0	# MEM[base: _262, offset: 0B], energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:138:             matrix_ptr( XX, 0, lag, order ) = energy;
	add.n	a3, a11, a3	# tmp264,, tmp263
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:140:             for( j = 1; j < ( order - lag ); j++ ) {
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:138:             matrix_ptr( XX, 0, lag, order ) = energy;
	s32i.n	a2, a3, 0	# MEM[base: _257, offset: 0B], energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:140:             for( j = 1; j < ( order - lag ); j++ ) {
	l32i.n	a6, sp, 52	#,
	beqi	a8, 1, .L15	#,,
	l32i.n	a11, sp, 36	# %sfp,
	l32i.n	a5, sp, 32	# %sfp, ivtmp$101
	l32i.n	a7, sp, 40	# %sfp, _242
	sub	a8, a11, a15	# ivtmp$97,, ivtmp$117
	movi.n	a4, -2	# ivtmp$100,
.L29:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:142:                 energy = silk_SMLABB( energy, ptr1[ -j ], ptr2[ -j ] );
	add.n	a11, a12, a4	# tmp266, ptr1, ivtmp$100
	add.n	a9, a13, a4	# tmp267, _263, ivtmp$100
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:141:                 energy = silk_SUB32( energy, silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ) );
	add.n	a10, a12, a5	# tmp271, ptr1, ivtmp$101
	add.n	a3, a13, a5	# tmp272, _263, ivtmp$101
	l16ui	a3, a3, 0	# MEM[base: _315, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:142:                 energy = silk_SMLABB( energy, ptr1[ -j ], ptr2[ -j ] );
	l16ui	a11, a11, 0	# MEM[base: _314, offset: 0B],
	l16ui	a9, a9, 0	# MEM[base: _313, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:141:                 energy = silk_SUB32( energy, silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ) );
	l16ui	a10, a10, 0	# MEM[base: _316, offset: 0B],
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:142:                 energy = silk_SMLABB( energy, ptr1[ -j ], ptr2[ -j ] );
	mul16s	a9, a11, a9	# tmp268, MEM[base: _314, offset: 0B], MEM[base: _313, offset: 0B]
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:141:                 energy = silk_SUB32( energy, silk_SMULBB( ptr1[ L - j ], ptr2[ L - j ] ) );
	mul16s	a10, a10, a3	# tmp273, MEM[base: _316, offset: 0B], MEM[base: _315, offset: 0B]
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:143:                 matrix_ptr( XX, lag + j, j, order ) = energy;
	add.n	a3, a15, a8	# tmp277, ivtmp$117, ivtmp$97
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:142:                 energy = silk_SMLABB( energy, ptr1[ -j ], ptr2[ -j ] );
	sub	a9, a9, a10	# tmp276, tmp268, tmp273
	add.n	a2, a2, a9	# energy, energy, tmp276
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:143:                 matrix_ptr( XX, lag + j, j, order ) = energy;
	add.n	a3, a3, a6	# tmp278, tmp277, ivtmp$119
	s32i.n	a2, a3, 0	# MEM[base: _302, offset: 0B], energy
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:144:                 matrix_ptr( XX, j, lag + j, order ) = energy;
	s32i.n	a2, a8, 0	# MEM[base: _301, offset: 0B], energy
	addi	a4, a4, -2	# ivtmp$100, ivtmp$100,
	add.n	a8, a8, a7	# ivtmp$97, ivtmp$97, _242
	addi	a5, a5, -2	# ivtmp$101, ivtmp$101,
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:140:             for( j = 1; j < ( order - lag ); j++ ) {
	bne	a14, a4, .L29	# ivtmp$120, ivtmp$100,
	j	.L45		#
.L44:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:114:     if( *rshifts > 0 ) {
	l32i.n	a2, a13, 0	# *rshifts_155(D), *rshifts_155(D)
	bgei	a2, 1, .L31	# *rshifts_155(D),,
	j	.L46		#
.L45:
	l32i.n	a8, sp, 0	# %sfp,
	l32i.n	a11, sp, 8	# %sfp,
	addi	a15, a15, -4	# ivtmp$117, ivtmp$117,
	add.n	a8, a8, a11	#,,
	s32i.n	a8, sp, 0	# %sfp,
	l32i.n	a8, sp, 4	# %sfp,
	add.n	a6, a6, a11	# ivtmp$119, ivtmp$119,
	addi.n	a8, a8, -1	#,,
	s32i.n	a8, sp, 4	# %sfp,
	addi.n	a14, a14, 2	# ivtmp$120, ivtmp$120,
	j	.L33		#
.L15:
# @OPUS@\upstream\silk\fixed\corrMatrix_FIX.c:149: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	silk_corrMatrix_FIX, .-silk_corrMatrix_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
