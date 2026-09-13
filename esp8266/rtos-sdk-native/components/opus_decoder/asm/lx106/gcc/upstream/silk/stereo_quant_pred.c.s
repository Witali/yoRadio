# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_quant_pred.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_quant_pred.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_quant_pred.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_quant_pred.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_quant_pred.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_quant_pred.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_quant_pred.c.s.raw
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
	.section	.text.silk_stereo_quant_pred,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, silk_stereo_pred_quant_Q13
	.literal .LC2, 6554
	.align	4
	.global	silk_stereo_quant_pred
	.type	silk_stereo_quant_pred, @function
# Function: silk_stereo_quant_pred
# Module: upstream/silk/stereo_quant_pred.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Quantize mid/side predictors */
# C context: void silk_stereo_quant_pred(
# C context: opus_int32                  pred_Q13[],                     /* I/O  Predictors (out: quantized)                 */
# C context: opus_int8                   ix[ 2 ][ 3 ]                    /* O    Quantization indices                        */
# C context: )
# C context: {
silk_stereo_quant_pred:
	addi	sp, sp, -48	#,,
	s32i.n	a13, sp, 36	#,
	s32i.n	a2, sp, 0	# %sfp, pred_Q13
	mov.n	a13, a2	# ivtmp$26, pred_Q13
	l32r	a2, .LC1	#,
	addi.n	a4, a3, 6	#, ivtmp$25,
	l16si	a2, a2, 0	# MEM[(short int *)&silk_stereo_pred_quant_Q13],
	s32i.n	a12, sp, 40	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a0, sp, 44	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\stereo_quant_pred.c:39: {
	mov.n	a12, a3	# ivtmp$25, ix
# @OPUS@\upstream\silk\stereo_quant_pred.c:41:     opus_int32 low_Q13, step_Q13, lvl_Q13, err_min_Q13, err_Q13, quant_pred_Q13 = 0;
	movi.n	a14, 0	# quant_pred_Q13,
	s32i.n	a4, sp, 4	# %sfp,
	s32i.n	a2, sp, 8	# %sfp,
	l32r	a11, .LC2	#, tmp138
	j	.L2		#
.L5:
# @OPUS@\upstream\silk\stereo_quant_pred.c:48:             low_Q13 = silk_stereo_pred_quant_Q13[ i ];
	mov.n	a4, a7	# low_Q13, silk_stereo_pred_quant_Q13_I_lsm0$9
# @OPUS@\upstream\silk\stereo_quant_pred.c:49:             step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ i + 1 ] - low_Q13,
	l16si	a7, a8, 2	# MEM[base: _162, offset: 2B], silk_stereo_pred_quant_Q13_I_lsm0$9
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	l32i.n	a9, a13, 0	# MEM[base: _46, offset: 0B], MEM[base: _46, offset: 0B]
# @OPUS@\upstream\silk\stereo_quant_pred.c:49:             step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ i + 1 ] - low_Q13,
	sub	a5, a7, a4	# _5, silk_stereo_pred_quant_Q13_I_lsm0$9, low_Q13
	extui	a2, a5, 0, 16	# tmp97, _5,
	mull	a2, a2, a11	# tmp98, tmp97, tmp138
	srai	a5, a5, 16	# tmp101, _5,
	mull	a5, a5, a11	# tmp102, tmp101, tmp138
	srai	a2, a2, 16	# tmp100, tmp98,
# @OPUS@\upstream\silk\stereo_quant_pred.c:49:             step_Q13 = silk_SMULWB( silk_stereo_pred_quant_Q13[ i + 1 ] - low_Q13,
	add.n	a2, a2, a5	# step_Q13, tmp100, tmp102
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	slli	a5, a2, 1	# slsr_138, step_Q13,
	add.n	a2, a4, a2	# lvl_Q13, low_Q13, step_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	sub	a9, a9, a2	# tmp104, MEM[base: _46, offset: 0B], lvl_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	abs	a4, a9	# err_Q13, tmp104
# @OPUS@\upstream\silk\stereo_quant_pred.c:57:                     ix[ n ][ 0 ] = i;
	extui	a15, a6, 0, 8	# prephitmp_25, ivtmp$10
	addi.n	a6, a6, 1	# ivtmp$10, ivtmp$10,
# @OPUS@\upstream\silk\stereo_quant_pred.c:54:                 if( err_Q13 < err_min_Q13 ) {
	blt	a4, a3, .L3	# err_Q13, err_min_Q13,
	l8ui	a15, a12, 0	# MEM[base: _97, offset: 0B], prephitmp_25
	j	.L4		#
.L3:
# @OPUS@\upstream\silk\stereo_quant_pred.c:58:                     ix[ n ][ 1 ] = j;
	movi.n	a3, 0	#,
	s8i	a3, a12, 1	# MEM[base: _78, offset: 1B],
# @OPUS@\upstream\silk\stereo_quant_pred.c:57:                     ix[ n ][ 0 ] = i;
	s8i	a15, a12, 0	# MEM[base: _78, offset: 0B], prephitmp_25
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	l32i.n	a3, a13, 0	# MEM[base: _46, offset: 0B], MEM[base: _46, offset: 0B]
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	add.n	a14, a2, a5	# quant_pred_Q13, lvl_Q13, slsr_138
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	sub	a3, a3, a14	# tmp107, MEM[base: _46, offset: 0B], quant_pred_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	add.n	a9, a14, a5	# lvl_Q13, quant_pred_Q13, slsr_138
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	abs	a3, a3	# err_Q13, tmp107
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	add.n	a10, a9, a5	# lvl_Q13, lvl_Q13, slsr_138
# @OPUS@\upstream\silk\stereo_quant_pred.c:54:                 if( err_Q13 < err_min_Q13 ) {
	bge	a3, a4, .L7	# err_Q13, err_Q13,
# @OPUS@\upstream\silk\stereo_quant_pred.c:58:                     ix[ n ][ 1 ] = j;
	movi.n	a4, 1	#,
	s8i	a4, a12, 1	# MEM[base: _78, offset: 1B],
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	l32i.n	a2, a13, 0	# MEM[base: _46, offset: 0B], MEM[base: _46, offset: 0B]
	addi.n	a8, a8, 2	# ivtmp$16, ivtmp$16,
	sub	a2, a2, a9	# tmp110, MEM[base: _46, offset: 0B], lvl_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	abs	a2, a2	# err_Q13, tmp110
# @OPUS@\upstream\silk\stereo_quant_pred.c:54:                 if( err_Q13 < err_min_Q13 ) {
	bge	a2, a3, .L4	# err_Q13, err_Q13,
# @OPUS@\upstream\silk\stereo_quant_pred.c:58:                     ix[ n ][ 1 ] = j;
	movi.n	a3, 2	#,
	s8i	a3, a12, 1	# MEM[base: _78, offset: 1B],
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	l32i.n	a4, a13, 0	# MEM[base: _46, offset: 0B], MEM[base: _46, offset: 0B]
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	add.n	a14, a5, a10	# quant_pred_Q13, slsr_138, lvl_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	sub	a4, a4, a10	# tmp113, MEM[base: _46, offset: 0B], lvl_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	abs	a4, a4	# err_Q13, tmp113
# @OPUS@\upstream\silk\stereo_quant_pred.c:54:                 if( err_Q13 < err_min_Q13 ) {
	bge	a4, a2, .L8	# err_Q13, err_Q13,
# @OPUS@\upstream\silk\stereo_quant_pred.c:58:                     ix[ n ][ 1 ] = j;
	movi.n	a2, 3	#,
	s8i	a2, a12, 1	# MEM[base: _78, offset: 1B],
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	l32i.n	a3, a13, 0	# MEM[base: _46, offset: 0B], MEM[base: _46, offset: 0B]
	sub	a3, a3, a14	# tmp116, MEM[base: _46, offset: 0B], quant_pred_Q13
# @OPUS@\upstream\silk\stereo_quant_pred.c:53:                 err_Q13 = silk_abs( pred_Q13[ n ] - lvl_Q13 );
	abs	a3, a3	# err_min_Q13, tmp116
# @OPUS@\upstream\silk\stereo_quant_pred.c:54:                 if( err_Q13 < err_min_Q13 ) {
	bge	a3, a4, .L9	# err_min_Q13, err_Q13,
# @OPUS@\upstream\silk\stereo_quant_pred.c:58:                     ix[ n ][ 1 ] = j;
	movi.n	a4, 4	#,
	s8i	a4, a12, 1	# MEM[base: _78, offset: 1B],
# @OPUS@\upstream\silk\stereo_quant_pred.c:47:         for( i = 0; i < STEREO_QUANT_TAB_SIZE - 1; i++ ) {
	movi.n	a2, 0xf	#,
	bne	a6, a2, .L5	# ivtmp$10,,
	j	.L4		#
.L7:
# @OPUS@\upstream\silk\stereo_quant_pred.c:52:                 lvl_Q13 = silk_SMLABB( low_Q13, step_Q13, 2 * j + 1 );
	mov.n	a14, a2	# quant_pred_Q13, lvl_Q13
	j	.L4		#
.L8:
	mov.n	a14, a9	# quant_pred_Q13, lvl_Q13
	j	.L4		#
.L9:
	mov.n	a14, a10	# quant_pred_Q13, lvl_Q13
.L4:
# @OPUS@\upstream\silk\stereo_quant_pred.c:66:         ix[ n ][ 2 ]  = silk_DIV32_16( ix[ n ][ 0 ], 3 );
	slli	a2, a15, 24	# tmp122, prephitmp_25,
	movi.n	a3, 3	#,
	srai	a2, a2, 24	#, tmp122,
	s32i.n	a11, sp, 12	#,
	call0	__divsi3		#
	extui	a2, a2, 0, 8	# _32,
# @OPUS@\upstream\silk\stereo_quant_pred.c:67:         ix[ n ][ 0 ] -= ix[ n ][ 2 ] * 3;
	slli	a3, a2, 2	# tmp128, _32,
	sub	a3, a2, a3	# tmp130, _32, tmp128
# @OPUS@\upstream\silk\stereo_quant_pred.c:67:         ix[ n ][ 0 ] -= ix[ n ][ 2 ] * 3;
	add.n	a15, a3, a15	# tmp133, tmp130, prephitmp_25
# @OPUS@\upstream\silk\stereo_quant_pred.c:66:         ix[ n ][ 2 ]  = silk_DIV32_16( ix[ n ][ 0 ], 3 );
	s8i	a2, a12, 2	# MEM[base: _56, offset: 2B], _32
# @OPUS@\upstream\silk\stereo_quant_pred.c:67:         ix[ n ][ 0 ] -= ix[ n ][ 2 ] * 3;
	s8i	a15, a12, 0	# MEM[base: _56, offset: 0B], tmp133
# @OPUS@\upstream\silk\stereo_quant_pred.c:44:     for( n = 0; n < 2; n++ ) {
	l32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\silk\stereo_quant_pred.c:68:         pred_Q13[ n ] = quant_pred_Q13;
	s32i.n	a14, a13, 0	# MEM[base: _46, offset: 0B], quant_pred_Q13
	addi.n	a12, a12, 3	# ivtmp$25, ivtmp$25,
	addi.n	a13, a13, 4	# ivtmp$26, ivtmp$26,
# @OPUS@\upstream\silk\stereo_quant_pred.c:44:     for( n = 0; n < 2; n++ ) {
	l32i.n	a11, sp, 12	#,
	beq	a4, a12, .L6	#, ivtmp$25,
.L2:
	l32r	a8, .LC1	#, ivtmp$16
# @OPUS@\upstream\silk\stereo_quant_pred.c:39: {
	l32i.n	a7, sp, 8	# %sfp, silk_stereo_pred_quant_Q13_I_lsm0$9
	movi.n	a6, 0	# ivtmp$10,
# @OPUS@\upstream\silk\stereo_quant_pred.c:46:         err_min_Q13 = silk_int32_MAX;
	l32r	a3, .LC0	#, err_min_Q13
	j	.L5		#
.L6:
# @OPUS@\upstream\silk\stereo_quant_pred.c:72:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\stereo_quant_pred.c:73: }
	l32i.n	a0, sp, 44	#,
# @OPUS@\upstream\silk\stereo_quant_pred.c:72:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	l32i.n	a2, a4, 0	# *pred_Q13_57(D), *pred_Q13_57(D)
	l32i.n	a3, a4, 4	# MEM[(opus_int32 *)pred_Q13_57(D) + 4B], MEM[(opus_int32 *)pred_Q13_57(D) + 4B]
# @OPUS@\upstream\silk\stereo_quant_pred.c:73: }
	l32i.n	a12, sp, 40	#,
# @OPUS@\upstream\silk\stereo_quant_pred.c:72:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	sub	a2, a2, a3	# tmp134, *pred_Q13_57(D), MEM[(opus_int32 *)pred_Q13_57(D) + 4B]
# @OPUS@\upstream\silk\stereo_quant_pred.c:73: }
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\stereo_quant_pred.c:72:     pred_Q13[ 0 ] -= pred_Q13[ 1 ];
	s32i.n	a2, a4, 0	# *pred_Q13_57(D), tmp134
# @OPUS@\upstream\silk\stereo_quant_pred.c:73: }
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_stereo_quant_pred, .-silk_stereo_quant_pred
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
