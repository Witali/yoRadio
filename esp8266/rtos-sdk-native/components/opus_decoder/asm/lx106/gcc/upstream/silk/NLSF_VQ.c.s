# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_VQ.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_VQ.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_VQ.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_VQ.c.s.raw
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
	.section	.text.silk_NLSF_VQ,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_NLSF_VQ
	.type	silk_NLSF_VQ, @function
# Function: silk_NLSF_VQ
# Module: upstream/silk/NLSF_VQ.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Compute quantization errors for an LPC_order element input vector for a VQ codebook */
# C context: void silk_NLSF_VQ(
# C context: opus_int32                  err_Q24[],                      /* O    Quantization errors [K]                     */
# C context: const opus_int16            in_Q15[],                       /* I    Input vectors to be quantized [LPC_order]   */
# C context: const opus_uint8            pCB_Q8[],                       /* I    Codebook vectors [K*LPC_order]              */
# C context: const opus_int16            pWght_Q9[],                     /* I    Codebook weights [K*LPC_order]              */
silk_NLSF_VQ:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 44	#,
	s32i.n	a13, sp, 40	#,
	s32i.n	a14, sp, 36	#,
	s32i.n	a15, sp, 32	#,
# @OPUS@\upstream\silk\NLSF_VQ.c:54:     for( i = 0; i < K; i++ ) {
	blti	a6, 1, .L1	# K,,
# @OPUS@\upstream\silk\NLSF_VQ.c:57:         for( m = LPC_order-2; m >= 0; m -= 2 ) {
	addi	a8, a7, -2	#, LPC_order,
	s32i.n	a8, sp, 0	# %sfp,
	l32i.n	a11, sp, 0	# %sfp,
	slli	a9, a8, 1	# _171,,
	add.n	a8, a3, a9	# tmp115, in_Q15, _171
	srli	a10, a11, 1	# tmp118,,
	mov.n	a13, a2	# ivtmp$39, err_Q24
	slli	a6, a6, 2	# tmp113, K,
	slli	a2, a10, 2	# tmp119, tmp118,
	addi	a8, a8, -4	# tmp116, tmp115,
# @OPUS@\upstream\silk\NLSF_VQ.c:74:         w_Q9_ptr += LPC_order;
	slli	a10, a7, 1	#, LPC_order,
	add.n	a6, a13, a6	#, ivtmp$39, tmp113
	add.n	a3, a3, a9	#, in_Q15, _171
	s32i.n	a10, sp, 4	# %sfp,
	add.n	a15, a4, a11	# ivtmp$40, pCB_Q8,
	add.n	a14, a5, a9	# ivtmp$42, pWght_Q9, _171
	s32i.n	a6, sp, 8	# %sfp,
	s32i.n	a3, sp, 12	# %sfp,
	sub	a12, a8, a2	# _188, tmp116, tmp119
.L5:
# @OPUS@\upstream\silk\NLSF_VQ.c:57:         for( m = LPC_order-2; m >= 0; m -= 2 ) {
	l32i.n	a11, sp, 0	# %sfp,
	bltz	a11, .L6	#,
# @OPUS@\upstream\silk\NLSF_VQ.c:56:         pred_Q24 = 0;
	movi.n	a9, 0	# pred_Q24,
# @OPUS@\upstream\silk\NLSF_VQ.c:57:         for( m = LPC_order-2; m >= 0; m -= 2 ) {
	l32i.n	a3, sp, 12	# %sfp, ivtmp$19
	mov.n	a5, a14	# ivtmp$21, ivtmp$42
	mov.n	a4, a15	# ivtmp$15, ivtmp$40
# @OPUS@\upstream\silk\NLSF_VQ.c:55:         sum_error_Q24 = 0;
	mov.n	a10, a9	# sum_error_Q24, pred_Q24
	s32i.n	a13, sp, 16	# %sfp, ivtmp$39
.L4:
# @OPUS@\upstream\silk\NLSF_VQ.c:59:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m + 1 ], (opus_int32)cb_Q8_ptr[ m + 1 ], 7 ); /* range: [ -32767 : 32767 ]*/
	l8ui	a2, a4, 1	# MEM[base: _187, offset: 1B], MEM[base: _187, offset: 1B]
	l16si	a11, a3, 2	# MEM[base: _202, offset: 2B], tmp120
# @OPUS@\upstream\silk\NLSF_VQ.c:65:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m ], (opus_int32)cb_Q8_ptr[ m ], 7 ); /* range: [ -32767 : 32767 ]*/
	l8ui	a8, a4, 0	# MEM[base: _187, offset: 0B], MEM[base: _187, offset: 0B]
# @OPUS@\upstream\silk\NLSF_VQ.c:60:             diffw_Q24 = silk_SMULBB( diff_Q15, w_Q9_ptr[ m + 1 ] );
	l16ui	a13, a5, 2	# MEM[base: _200, offset: 2B],
# @OPUS@\upstream\silk\NLSF_VQ.c:59:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m + 1 ], (opus_int32)cb_Q8_ptr[ m + 1 ], 7 ); /* range: [ -32767 : 32767 ]*/
	slli	a2, a2, 7	# tmp124, MEM[base: _187, offset: 1B],
# @OPUS@\upstream\silk\NLSF_VQ.c:65:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m ], (opus_int32)cb_Q8_ptr[ m ], 7 ); /* range: [ -32767 : 32767 ]*/
	l16si	a6, a3, 0	# MEM[base: _202, offset: 0B], tmp129
# @OPUS@\upstream\silk\NLSF_VQ.c:59:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m + 1 ], (opus_int32)cb_Q8_ptr[ m + 1 ], 7 ); /* range: [ -32767 : 32767 ]*/
	sub	a2, a11, a2	# diff_Q15, tmp120, tmp124
# @OPUS@\upstream\silk\NLSF_VQ.c:60:             diffw_Q24 = silk_SMULBB( diff_Q15, w_Q9_ptr[ m + 1 ] );
	mul16s	a11, a13, a2	# diffw_Q24,, diff_Q15
# @OPUS@\upstream\silk\NLSF_VQ.c:65:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m ], (opus_int32)cb_Q8_ptr[ m ], 7 ); /* range: [ -32767 : 32767 ]*/
	slli	a8, a8, 7	# tmp133, MEM[base: _187, offset: 0B],
# @OPUS@\upstream\silk\NLSF_VQ.c:66:             diffw_Q24 = silk_SMULBB( diff_Q15, w_Q9_ptr[ m ] );
	l16ui	a2, a5, 0	# MEM[base: _200, offset: 0B],
# @OPUS@\upstream\silk\NLSF_VQ.c:65:             diff_Q15 = silk_SUB_LSHIFT32( in_Q15[ m ], (opus_int32)cb_Q8_ptr[ m ], 7 ); /* range: [ -32767 : 32767 ]*/
	sub	a6, a6, a8	# diff_Q15, tmp129, tmp133
# @OPUS@\upstream\silk\NLSF_VQ.c:61:             sum_error_Q24 = silk_ADD32( sum_error_Q24, silk_abs( silk_SUB_RSHIFT32( diffw_Q24, pred_Q24, 1 ) ) );
	srai	a8, a9, 1	# tmp127, pred_Q24,
# @OPUS@\upstream\silk\NLSF_VQ.c:66:             diffw_Q24 = silk_SMULBB( diff_Q15, w_Q9_ptr[ m ] );
	mul16s	a9, a2, a6	# pred_Q24,, diff_Q15
# @OPUS@\upstream\silk\NLSF_VQ.c:67:             sum_error_Q24 = silk_ADD32( sum_error_Q24, silk_abs( silk_SUB_RSHIFT32( diffw_Q24, pred_Q24, 1 ) ) );
	srai	a2, a11, 1	# tmp136, diffw_Q24,
	sub	a2, a9, a2	# tmp137, pred_Q24, tmp136
# @OPUS@\upstream\silk\NLSF_VQ.c:61:             sum_error_Q24 = silk_ADD32( sum_error_Q24, silk_abs( silk_SUB_RSHIFT32( diffw_Q24, pred_Q24, 1 ) ) );
	sub	a11, a11, a8	# tmp128, diffw_Q24, tmp127
	abs	a11, a11	# _19, tmp128
# @OPUS@\upstream\silk\NLSF_VQ.c:67:             sum_error_Q24 = silk_ADD32( sum_error_Q24, silk_abs( silk_SUB_RSHIFT32( diffw_Q24, pred_Q24, 1 ) ) );
	abs	a2, a2	# tmp138, tmp137
# @OPUS@\upstream\silk\NLSF_VQ.c:67:             sum_error_Q24 = silk_ADD32( sum_error_Q24, silk_abs( silk_SUB_RSHIFT32( diffw_Q24, pred_Q24, 1 ) ) );
	add.n	a2, a2, a11	# tmp139, tmp138, _19
	addi	a3, a3, -4	# ivtmp$19, ivtmp$19,
	add.n	a10, a10, a2	# sum_error_Q24, sum_error_Q24, tmp139
	addi	a4, a4, -2	# ivtmp$15, ivtmp$15,
	addi	a5, a5, -4	# ivtmp$21, ivtmp$21,
# @OPUS@\upstream\silk\NLSF_VQ.c:57:         for( m = LPC_order-2; m >= 0; m -= 2 ) {
	bne	a12, a3, .L4	# _188, ivtmp$19,
	l32i.n	a13, sp, 16	# %sfp, ivtmp$39
	j	.L3		#
.L6:
# @OPUS@\upstream\silk\NLSF_VQ.c:55:         sum_error_Q24 = 0;
	movi.n	a10, 0	# sum_error_Q24,
.L3:
# @OPUS@\upstream\silk\NLSF_VQ.c:72:         err_Q24[ i ] = sum_error_Q24;
	s32i.n	a10, a13, 0	# MEM[base: _169, offset: 0B], sum_error_Q24
	l32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\silk\NLSF_VQ.c:54:     for( i = 0; i < K; i++ ) {
	l32i.n	a10, sp, 8	# %sfp,
	addi.n	a13, a13, 4	# ivtmp$39, ivtmp$39,
	add.n	a15, a15, a7	# ivtmp$40, ivtmp$40, LPC_order
	add.n	a14, a14, a8	# ivtmp$42, ivtmp$42,
	bne	a10, a13, .L5	#, ivtmp$39,
.L1:
# @OPUS@\upstream\silk\NLSF_VQ.c:76: }
	l32i.n	a12, sp, 44	#,
	l32i.n	a13, sp, 40	#,
	l32i.n	a14, sp, 36	#,
	l32i.n	a15, sp, 32	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_NLSF_VQ, .-silk_NLSF_VQ
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
