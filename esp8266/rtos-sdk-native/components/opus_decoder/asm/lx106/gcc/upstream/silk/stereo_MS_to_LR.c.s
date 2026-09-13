# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/stereo_MS_to_LR.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"stereo_MS_to_LR.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\stereo_MS_to_LR.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\stereo_MS_to_LR.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\stereo_MS_to_LR.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\stereo_MS_to_LR.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\stereo_MS_to_LR.c.s.raw
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
	.section	.text.silk_stereo_MS_to_LR,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, 65536
	.align	4
	.global	silk_stereo_MS_to_LR
	.type	silk_stereo_MS_to_LR, @function
# Function: silk_stereo_MS_to_LR
# Module: upstream/silk/stereo_MS_to_LR.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Convert adaptive Mid/Side representation to Left/Right stereo signal */
# C context: void silk_stereo_MS_to_LR(
# C context: stereo_dec_state            *state,                         /* I/O  State                                       */
# C context: opus_int16                  x1[],                           /* I/O  Left input signal, becomes mid signal       */
# C context: opus_int16                  x2[],                           /* I/O  Right input signal, becomes side signal     */
# C context: const opus_int32            pred_Q13[],                     /* I    Predictors                                  */
silk_stereo_MS_to_LR:
	addi	sp, sp, -64	#,,
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:48:     silk_memcpy( x1, state->sMid,  2 * sizeof( opus_int16 ) );
	l8ui	a9, a2, 4	# MEM[(void *)_1],
	addi.n	a8, a2, 4	# _1, state,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:43: {
	s32i.n	a2, sp, 4	# %sfp, state
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:48:     silk_memcpy( x1, state->sMid,  2 * sizeof( opus_int16 ) );
	l8ui	a2, a2, 5	# MEM[(void *)_1],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:43: {
	mov.n	a13, a3	# x1, x1
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:48:     silk_memcpy( x1, state->sMid,  2 * sizeof( opus_int16 ) );
	s8i	a9, a3, 0	# MEM[(void *)x1_141(D)], MEM[(void *)_1]
	l8ui	a3, a8, 2	# MEM[(void *)_1],
	s8i	a2, a13, 1	# MEM[(void *)x1_141(D)], MEM[(void *)_1]
	l8ui	a2, a8, 3	# MEM[(void *)_1],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:49:     silk_memcpy( x2, state->sSide, 2 * sizeof( opus_int16 ) );
	l32i.n	a10, sp, 4	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:48:     silk_memcpy( x1, state->sMid,  2 * sizeof( opus_int16 ) );
	s8i	a2, a13, 3	# MEM[(void *)x1_141(D)], MEM[(void *)_1]
	s8i	a3, a13, 2	# MEM[(void *)x1_141(D)], MEM[(void *)_1]
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:49:     silk_memcpy( x2, state->sSide, 2 * sizeof( opus_int16 ) );
	l8ui	a9, a10, 8	# MEM[(void *)_2],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:43: {
	s32i.n	a4, sp, 0	# %sfp, x2
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:49:     silk_memcpy( x2, state->sSide, 2 * sizeof( opus_int16 ) );
	l8ui	a3, a10, 9	# MEM[(void *)_2],
	l32i.n	a11, sp, 0	# %sfp,
	s8i	a9, a4, 0	# MEM[(void *)x2_143(D)], MEM[(void *)_2]
	l8ui	a4, a10, 10	# MEM[(void *)_2],
	s8i	a3, a11, 1	# MEM[(void *)x2_143(D)], MEM[(void *)_2]
	l8ui	a3, a10, 11	# MEM[(void *)_2],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:43: {
	s32i.n	a7, sp, 16	# %sfp, frame_length
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:50:     silk_memcpy( state->sMid,  &x1[ frame_length ], 2 * sizeof( opus_int16 ) );
	slli	a7, a7, 1	#, frame_length,
	add.n	a9, a13, a7	#, x1,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:49:     silk_memcpy( x2, state->sSide, 2 * sizeof( opus_int16 ) );
	s8i	a4, a11, 2	# MEM[(void *)x2_143(D)], MEM[(void *)_2]
	s8i	a3, a11, 3	# MEM[(void *)x2_143(D)], MEM[(void *)_2]
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:50:     silk_memcpy( state->sMid,  &x1[ frame_length ], 2 * sizeof( opus_int16 ) );
	l8ui	a4, a9, 0	# MEM[(void *)_5],
	l8ui	a3, a9, 1	# MEM[(void *)_5],
	s32i.n	a9, sp, 12	# %sfp,
	s8i	a4, a10, 4	# MEM[(void *)_1], MEM[(void *)_5]
	s32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:49:     silk_memcpy( x2, state->sSide, 2 * sizeof( opus_int16 ) );
	addi.n	a2, a10, 8	# _2,,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:50:     silk_memcpy( state->sMid,  &x1[ frame_length ], 2 * sizeof( opus_int16 ) );
	l8ui	a7, a9, 2	# MEM[(void *)_5],
	s8i	a3, a8, 1	# MEM[(void *)_1], MEM[(void *)_5]
	l8ui	a4, a9, 3	# MEM[(void *)_5],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:51:     silk_memcpy( state->sSide, &x2[ frame_length ], 2 * sizeof( opus_int16 ) );
	l32i.n	a10, sp, 20	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:50:     silk_memcpy( state->sMid,  &x1[ frame_length ], 2 * sizeof( opus_int16 ) );
	s8i	a7, a8, 2	# MEM[(void *)_1], MEM[(void *)_5]
	s8i	a4, a8, 3	# MEM[(void *)_1], MEM[(void *)_5]
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:51:     silk_memcpy( state->sSide, &x2[ frame_length ], 2 * sizeof( opus_int16 ) );
	add.n	a3, a11, a10	# tmp206,,
	l8ui	a4, a3, 0	# MEM[(void *)_6],
	l32i.n	a11, sp, 4	# %sfp,
	l8ui	a7, a3, 1	# MEM[(void *)_6],
	s8i	a4, a11, 8	# MEM[(void *)_2], MEM[(void *)_6]
	l8ui	a4, a3, 2	# MEM[(void *)_6],
	s8i	a7, a2, 1	# MEM[(void *)_2], MEM[(void *)_6]
	l8ui	a3, a3, 3	# MEM[(void *)_6],
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:56:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	slli	a12, a6, 3	# _9, fs_kHz,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:51:     silk_memcpy( state->sSide, &x2[ frame_length ], 2 * sizeof( opus_int16 ) );
	s8i	a4, a2, 2	# MEM[(void *)_2], MEM[(void *)_6]
	s8i	a3, a2, 3	# MEM[(void *)_2], MEM[(void *)_6]
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:56:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	l32r	a2, .LC2	#,
	mov.n	a3, a12	#, _9
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:43: {
	mov.n	a15, a5	# pred_Q13, pred_Q13
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:54:     pred0_Q13  = state->pred_prev_Q13[ 0 ];
	l16si	a14, a11, 0	# state_139(D)->pred_prev_Q13, pred0_Q13
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:56:     denom_Q16  = silk_DIV32_16( (opus_int32)1 << 16, STEREO_INTERP_LEN_MS * fs_kHz );
	call0	__divsi3		#
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	l16si	a9, a15, 0	# *pred_Q13_152(D),
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:55:     pred1_Q13  = state->pred_prev_Q13[ 1 ];
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	slli	a2, a2, 16	# tmp221,,
	srai	a4, a2, 16	# _14, tmp221,
	sub	a3, a9, a14	# tmp222,, pred0_Q13
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:55:     pred1_Q13  = state->pred_prev_Q13[ 1 ];
	l16si	a10, a8, 2	# state_139(D)->pred_prev_Q13, pred1_Q13
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:58:     delta1_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	l16si	a11, a15, 4	# MEM[(const opus_int32 *)pred_Q13_152(D) + 4B], _20
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	mul16s	a3, a3, a4	# tmp223, tmp222, _14
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:58:     delta1_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	sub	a2, a11, a10	# tmp228, _20, pred1_Q13
	mul16s	a2, a2, a4	# tmp229, tmp228, _14
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	srai	a3, a3, 15	# tmp224, tmp223,
	addi.n	a3, a3, 1	# tmp225, tmp224,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:58:     delta1_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	srai	a2, a2, 15	# tmp230, tmp229,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	srai	a3, a3, 1	#, tmp225,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	s32i.n	a9, sp, 24	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:58:     delta1_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	addi.n	a2, a2, 1	# tmp231, tmp230,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:57:     delta0_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 0 ] - state->pred_prev_Q13[ 0 ], denom_Q16 ), 16 );
	s32i.n	a3, sp, 8	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:58:     delta1_Q13 = silk_RSHIFT_ROUND( silk_SMULBB( pred_Q13[ 1 ] - state->pred_prev_Q13[ 1 ], denom_Q16 ), 16 );
	srai	a2, a2, 1	# delta1_Q13, tmp231,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:59:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	movi.n	a9, 0	# n,
	l32r	a5, .LC0	#, tmp319
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:59:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	bgei	a12, 1, .L27	# _9,,
.L6:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:69:     for( n = STEREO_INTERP_LEN_MS * fs_kHz; n < frame_length; n++ ) {
	l32i.n	a10, sp, 16	# %sfp,
	blt	a12, a10, .L3	# _9,,
	j	.L4		#
.L27:
	s32i.n	a11, sp, 28	# %sfp, _20
	mov.n	a15, a2	# delta1_Q13, delta1_Q13
.L2:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:62:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	slli	a2, a9, 1	# _320, n,
	addi.n	a4, a2, 2	# _309, _320,
	add.n	a3, a13, a4	# tmp232, x1, _309
	add.n	a2, a13, a2	# tmp235, x1, _320
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:63:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	l32i.n	a11, sp, 0	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:62:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	l16si	a6, a2, 0	# *_319, tmp241
	l16si	a3, a3, 0	# *_308, _306
	l16si	a8, a2, 4	# *_314, tmp237
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:63:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	add.n	a4, a11, a4	# _299,, _309
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:61:         pred1_Q13 += delta1_Q13;
	add.n	a10, a10, a15	# pred1_Q13, pred1_Q13, delta1_Q13
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:60:         pred0_Q13 += delta0_Q13;
	l32i.n	a11, sp, 8	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	slli	a2, a3, 11	# _286, _306,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:62:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	add.n	a8, a8, a6	# tmp244, tmp237, tmp241
	slli	a3, a3, 1	# tmp245, _306,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	slli	a6, a10, 16	# tmp250, pred1_Q13,
	srai	a6, a6, 16	# _283, tmp250,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:60:         pred0_Q13 += delta0_Q13;
	add.n	a14, a14, a11	# pred0_Q13, pred0_Q13,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:62:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	add.n	a3, a8, a3	# tmp246, tmp244, tmp245
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	srai	a11, a2, 16	# tmp251, _286,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:63:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	l16si	a7, a4, 0	# *_299, tmp253
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	extui	a2, a2, 0, 16	# tmp258, _286,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:62:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	slli	a3, a3, 9	# sum, tmp246,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	mull	a11, a11, a6	# tmp252, tmp251, _283
	mull	a2, a2, a6	# tmp259, tmp258, _283
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:63:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	slli	a8, a14, 16	# tmp247, pred0_Q13,
	srai	a8, a8, 16	# _292, tmp247,
	extui	a6, a3, 0, 16	# tmp248, sum,
	slli	a7, a7, 8	# tmp256, tmp253,
	srai	a3, a3, 16	# tmp262, sum,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	srai	a2, a2, 16	# tmp260, tmp259,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:63:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	mull	a3, a3, a8	# tmp263, tmp262, _292
	mull	a6, a6, a8	# tmp249, tmp248, _292
	add.n	a7, a11, a7	# tmp257, tmp252, tmp256
	add.n	a7, a7, a2	# tmp261, tmp257, tmp260
	add.n	a2, a7, a3	# _276, tmp261, tmp263
	srai	a6, a6, 16	# _288, tmp249,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:64:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	add.n	a2, a2, a6	# sum, _276, _288
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:65:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	srai	a2, a2, 7	# tmp265, sum,
	addi.n	a2, a2, 1	# tmp266, tmp265,
	srai	a2, a2, 1	# _272, tmp266,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:59:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	addi.n	a9, a9, 1	# n, n,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:65:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	mov.n	a3, a5	# iftmp$8_270, tmp319
	blt	a5, a2, .L5	# tmp319, _272,
	l32r	a3, .LC1	#, iftmp$8_270
	slli	a6, a2, 16	# tmp269, _272,
	blt	a2, a3, .L5	# _272, iftmp$8_270,
	srai	a3, a6, 16	# iftmp$8_270, tmp269,
.L5:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:65:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	s16i	a3, a4, 0	# *_299, iftmp$8_270
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:59:     for( n = 0; n < STEREO_INTERP_LEN_MS * fs_kHz; n++ ) {
	blt	a9, a12, .L2	# n, _9,
	l32i.n	a11, sp, 28	# %sfp, _20
	j	.L6		#
.L4:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:75:     state->pred_prev_Q13[ 0 ] = pred_Q13[ 0 ];
	l32i.n	a8, sp, 4	# %sfp,
	l32i.n	a9, sp, 24	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:79:     for( n = 0; n < frame_length; n++ ) {
	l32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:75:     state->pred_prev_Q13[ 0 ] = pred_Q13[ 0 ];
	s16i	a9, a8, 0	# state_139(D)->pred_prev_Q13,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:76:     state->pred_prev_Q13[ 1 ] = pred_Q13[ 1 ];
	s16i	a11, a8, 2	# state_139(D)->pred_prev_Q13, _20
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:79:     for( n = 0; n < frame_length; n++ ) {
	bgei	a10, 1, .L7	#,,
	j	.L1		#
.L3:
	addi.n	a7, a12, 1	# tmp271, _9,
	l32i.n	a4, sp, 0	# %sfp,
	slli	a7, a7, 1	# tmp272, tmp271,
	slli	a12, a12, 1	# tmp270, _9,
	add.n	a7, a4, a7	# ivtmp$43,, tmp272
	l32r	a5, .LC0	#, tmp319
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:73:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	l32r	a9, .LC1	#, tmp351
	l32i.n	a3, sp, 24	# %sfp, _11
	l32i.n	a4, sp, 12	# %sfp, _74
	add.n	a12, a13, a12	# ivtmp$42, x1, tmp270
.L10:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:70:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	l16si	a2, a12, 2	# MEM[base: _399, offset: 2B], _369
	l16si	a6, a12, 0	# MEM[base: _399, offset: 0B], tmp278
	l16si	a8, a12, 4	# MEM[base: _399, offset: 4B], tmp275
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:72:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	slli	a10, a2, 11	# _351, _369,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:70:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	add.n	a8, a8, a6	# tmp281, tmp275, tmp278
	slli	a6, a2, 1	# tmp282, _369,
	add.n	a8, a8, a6	# tmp283, tmp281, tmp282
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:71:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	l16si	a2, a7, 0	# MEM[base: _176, offset: 0B], tmp288
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:72:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	srai	a6, a10, 16	# tmp286, _351,
	extui	a10, a10, 0, 16	# tmp293, _351,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:70:         sum = silk_LSHIFT( silk_ADD_LSHIFT32( x1[ n ] + (opus_int32)x1[ n + 2 ], x1[ n + 1 ], 1 ), 9 );       /* Q11 */
	slli	a8, a8, 9	# sum, tmp283,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:72:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	mull	a6, a6, a11	# tmp287, tmp286, _20
	mull	a10, a10, a11	# tmp294, tmp293, _20
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:71:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	extui	a14, a8, 0, 16	# tmp284, sum,
	slli	a2, a2, 8	# tmp291, tmp288,
	srai	a8, a8, 16	# tmp297, sum,
	add.n	a6, a6, a2	# tmp292, tmp287, tmp291
	mull	a14, a14, a3	# tmp285, tmp284, _11
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:72:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	srai	a2, a10, 16	# tmp295, tmp294,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:71:         sum = silk_SMLAWB( silk_LSHIFT( (opus_int32)x2[ n + 1 ], 8 ), sum, pred0_Q13 );         /* Q8  */
	mull	a8, a8, a3	# tmp298, tmp297, _11
	add.n	a2, a6, a2	# tmp296, tmp292, tmp295
	srai	a14, a14, 16	# _353, tmp285,
	add.n	a2, a2, a8	# _343, tmp296, tmp298
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:72:         sum = silk_SMLAWB( sum, silk_LSHIFT( (opus_int32)x1[ n + 1 ], 11 ), pred1_Q13 );        /* Q8  */
	add.n	a2, a2, a14	# sum, _343, _353
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:73:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	srai	a2, a2, 7	# tmp300, sum,
	addi.n	a2, a2, 1	# tmp301, tmp300,
	srai	a2, a2, 1	# _339, tmp301,
	addi.n	a12, a12, 2	# ivtmp$42, ivtmp$42,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:73:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	mov.n	a6, a5	# iftmp$17_337, tmp319
	blt	a5, a2, .L9	# tmp319, _339,
	slli	a8, a2, 16	# tmp304, _339,
	mov.n	a6, a9	# iftmp$17_337, tmp351
	blt	a2, a9, .L9	# _339, tmp351,
	srai	a6, a8, 16	# iftmp$17_337, tmp304,
.L9:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:73:         x2[ n + 1 ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( sum, 8 ) );
	s16i	a6, a7, 0	# MEM[base: _176, offset: 0B], iftmp$17_337
	addi.n	a7, a7, 2	# ivtmp$43, ivtmp$43,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:69:     for( n = STEREO_INTERP_LEN_MS * fs_kHz; n < frame_length; n++ ) {
	bne	a4, a12, .L10	# _74, ivtmp$42,
	j	.L4		#
.L7:
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:82:         x1[ n + 1 ] = (opus_int16)silk_SAT16( sum );
	l32r	a9, .LC1	#, tmp346
	l32i.n	a8, sp, 0	# %sfp,
	addi.n	a2, a7, 2	# tmp305,,
	l32r	a5, .LC0	#, tmp319
	addi.n	a3, a13, 2	# ivtmp$32, x1,
	addi.n	a4, a8, 2	# ivtmp$34,,
	add.n	a13, a13, a2	# _173, x1, tmp305
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:83:         x2[ n + 1 ] = (opus_int16)silk_SAT16( diff );
	mov.n	a10, a9	# tmp348, tmp346
.L13:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:80:         sum  = x1[ n + 1 ] + (opus_int32)x2[ n + 1 ];
	l16si	a2, a3, 0	# MEM[base: _121, offset: 0B], _419
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:80:         sum  = x1[ n + 1 ] + (opus_int32)x2[ n + 1 ];
	l16si	a7, a4, 0	# MEM[base: _123, offset: 0B], _416
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:82:         x1[ n + 1 ] = (opus_int16)silk_SAT16( sum );
	mov.n	a8, a5	# iftmp$24_411, tmp319
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:80:         sum  = x1[ n + 1 ] + (opus_int32)x2[ n + 1 ];
	add.n	a6, a7, a2	# sum, _416, _419
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:81:         diff = x1[ n + 1 ] - (opus_int32)x2[ n + 1 ];
	sub	a2, a2, a7	# tmp320, _419, _416
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:82:         x1[ n + 1 ] = (opus_int16)silk_SAT16( sum );
	blt	a5, a6, .L11	# tmp319, sum,
	slli	a7, a6, 16	# tmp313, sum,
	mov.n	a8, a9	# iftmp$24_411, tmp346
	blt	a6, a9, .L11	# sum, tmp346,
	srai	a8, a7, 16	# iftmp$24_411, tmp313,
.L11:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:82:         x1[ n + 1 ] = (opus_int16)silk_SAT16( sum );
	s16i	a8, a3, 0	# MEM[base: _121, offset: 0B], iftmp$24_411
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:83:         x2[ n + 1 ] = (opus_int16)silk_SAT16( diff );
	mov.n	a6, a5	# iftmp$27_408, tmp319
	addi.n	a3, a3, 2	# ivtmp$32, ivtmp$32,
	blt	a5, a2, .L12	# tmp319, tmp320,
	slli	a7, a2, 16	# tmp317, tmp320,
	mov.n	a6, a10	# iftmp$27_408, tmp348
	blt	a2, a10, .L12	# tmp320, tmp348,
	srai	a6, a7, 16	# iftmp$27_408, tmp317,
.L12:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:83:         x2[ n + 1 ] = (opus_int16)silk_SAT16( diff );
	s16i	a6, a4, 0	# MEM[base: _123, offset: 0B], iftmp$27_408
	addi.n	a4, a4, 2	# ivtmp$34, ivtmp$34,
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:79:     for( n = 0; n < frame_length; n++ ) {
	bne	a13, a3, .L13	# _173, ivtmp$32,
.L1:
# @OPUS@\upstream\silk\stereo_MS_to_LR.c:85: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_stereo_MS_to_LR, .-silk_stereo_MS_to_LR
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
