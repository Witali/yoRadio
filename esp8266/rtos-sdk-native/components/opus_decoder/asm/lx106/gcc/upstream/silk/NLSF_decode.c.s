# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_decode.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_decode.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_decode.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_decode.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_decode.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_decode.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_decode.c.s.raw
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
	.section	.text.silk_NLSF_decode,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.align	4
	.global	silk_NLSF_decode
	.type	silk_NLSF_decode, @function
# Function: silk_NLSF_decode
# Module: upstream/silk/NLSF_decode.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /***********************/
# C context: /* NLSF vector decoder */
# C context: /***********************/
# C context: void silk_NLSF_decode(
# C context: opus_int16            *pNLSF_Q15,                     /* O    Quantized NLSF vector [ LPC_ORDER ]         */
# C context: opus_int8             *NLSFIndices,                   /* I    Codebook path vector [ LPC_ORDER + 1 ]      */
# C context: const silk_NLSF_CB_struct   *psNLSF_CB                      /* I    Codebook object                             */
# C context: )
silk_NLSF_decode:
	movi	a9, 0x90	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 136	#,
	s32i	a13, sp, 132	#,
	s32i	a0, sp, 140	#,
	s32i	a14, sp, 128	#,
	s32i	a15, sp, 124	#,
# @OPUS@\upstream\silk\NLSF_decode.c:78:     silk_NLSF_unpack( ec_ix, pred_Q8, psNLSF_CB, NLSFIndices[ 0 ] );
	l8ui	a5, a3, 0	# *NLSFIndices_40(D),
	addi	a12, sp, 64	# tmp129,,
	slli	a5, a5, 24	# tmp128, *NLSFIndices_40(D),
# @OPUS@\upstream\silk\NLSF_decode.c:68: {
	s32i	a2, sp, 92	# %sfp, pNLSF_Q15
	mov.n	a13, a3	# NLSFIndices, NLSFIndices
# @OPUS@\upstream\silk\NLSF_decode.c:78:     silk_NLSF_unpack( ec_ix, pred_Q8, psNLSF_CB, NLSFIndices[ 0 ] );
	addi	a2, sp, 32	#,,
	srai	a5, a5, 24	#, tmp128,
	mov.n	a3, a12	#, tmp129
# @OPUS@\upstream\silk\NLSF_decode.c:68: {
	s32i	a4, sp, 80	# %sfp, psNLSF_CB
# @OPUS@\upstream\silk\NLSF_decode.c:78:     silk_NLSF_unpack( ec_ix, pred_Q8, psNLSF_CB, NLSFIndices[ 0 ] );
	call0	silk_NLSF_unpack		#
# @OPUS@\upstream\silk\NLSF_decode.c:81:     silk_NLSF_residual_dequant( res_Q10, &NLSFIndices[ 1 ], pred_Q8, psNLSF_CB->quantStepSize_Q16, psNLSF_CB->order );
	l32i	a2, sp, 80	# %sfp,
	l16si	a9, a2, 2	# psNLSF_CB_41(D)->order, _6
# @OPUS@\upstream\silk\NLSF_decode.c:81:     silk_NLSF_residual_dequant( res_Q10, &NLSFIndices[ 1 ], pred_Q8, psNLSF_CB->quantStepSize_Q16, psNLSF_CB->order );
	l16si	a11, a2, 4	# psNLSF_CB_41(D)->quantStepSize_Q16, _5
# @OPUS@\upstream\silk\NLSF_decode.c:46:     for( i = order-1; i >= 0; i-- ) {
	addi.n	a7, a9, -1	# i, _6,
# @OPUS@\upstream\silk\NLSF_decode.c:81:     silk_NLSF_residual_dequant( res_Q10, &NLSFIndices[ 1 ], pred_Q8, psNLSF_CB->quantStepSize_Q16, psNLSF_CB->order );
	mov.n	a4, a9	# _95, _6
# @OPUS@\upstream\silk\NLSF_decode.c:46:     for( i = order-1; i >= 0; i-- ) {
	bgez	a7, .L2	# i,
.L8:
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	l8ui	a13, a13, 0	# *NLSFIndices_40(D),
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	l32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	slli	a13, a13, 24	# tmp138, *NLSFIndices_40(D),
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	l32i.n	a3, a3, 8	# psNLSF_CB_41(D)->CB1_NLSF_Q8,
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	srai	a13, a13, 24	# tmp136, tmp138,
	mul16s	a13, a13, a9	#, tmp136, _6
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	s32i	a3, sp, 88	# %sfp,
# @OPUS@\upstream\silk\NLSF_decode.c:85:     pCB_Wght_Q9 = &psNLSF_CB->CB1_Wght_Q9[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	l32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\silk\NLSF_decode.c:84:     pCB_element = &psNLSF_CB->CB1_NLSF_Q8[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	s32i	a13, sp, 84	# %sfp,
# @OPUS@\upstream\silk\NLSF_decode.c:85:     pCB_Wght_Q9 = &psNLSF_CB->CB1_Wght_Q9[ NLSFIndices[ 0 ] * psNLSF_CB->order ];
	l32i.n	a2, a3, 12	# psNLSF_CB_41(D)->CB1_Wght_Q9, _15
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	bgei	a9, 1, .L3	# _6,,
	j	.L4		#
.L2:
	slli	a8, a7, 1	# tmp140, i,
	add.n	a10, a13, a9	# ivtmp$22, NLSFIndices, _6
	add.n	a7, a12, a7	# ivtmp$20, tmp129, i
	add.n	a8, sp, a8	# ivtmp$23,, tmp140
# @OPUS@\upstream\silk\NLSF_decode.c:45:     out_Q10 = 0;
	movi.n	a5, 0	# pred_Q10,
	j	.L7		#
.L11:
# @OPUS@\upstream\silk\NLSF_decode.c:46:     for( i = order-1; i >= 0; i-- ) {
	mov.n	a7, a2	# ivtmp$20, ivtmp$20
.L7:
# @OPUS@\upstream\silk\NLSF_decode.c:48:         out_Q10  = silk_LSHIFT( indices[ i ], 10 );
	l8ui	a3, a10, 0	# MEM[base: _63, offset: 0B],
# @OPUS@\upstream\silk\NLSF_decode.c:47:         pred_Q10 = silk_RSHIFT( silk_SMULBB( out_Q10, (opus_int16)pred_coef_Q8[ i ] ), 8 );
	l8ui	a2, a7, 0	# MEM[base: _62, offset: 0B], MEM[base: _62, offset: 0B]
# @OPUS@\upstream\silk\NLSF_decode.c:48:         out_Q10  = silk_LSHIFT( indices[ i ], 10 );
	slli	a3, a3, 24	# tmp146, MEM[base: _63, offset: 0B],
	srai	a3, a3, 14	# out_Q10, tmp146,
# @OPUS@\upstream\silk\NLSF_decode.c:47:         pred_Q10 = silk_RSHIFT( silk_SMULBB( out_Q10, (opus_int16)pred_coef_Q8[ i ] ), 8 );
	mul16s	a5, a2, a5	# tmp143, MEM[base: _62, offset: 0B], pred_Q10
# @OPUS@\upstream\silk\NLSF_decode.c:50:             out_Q10 = silk_SUB16( out_Q10, SILK_FIX_CONST( NLSF_QUANT_LEVEL_ADJ, 10 ) );
	addi	a2, a3, -102	# out_Q10, out_Q10,
	extui	a6, a2, 0, 16	# tmp147, out_Q10,
	srai	a2, a2, 16	# tmp150, out_Q10,
	mull	a6, a6, a11	# tmp148, tmp147, _5
	mull	a2, a2, a11	# tmp151, tmp150, _5
# @OPUS@\upstream\silk\NLSF_decode.c:47:         pred_Q10 = silk_RSHIFT( silk_SMULBB( out_Q10, (opus_int16)pred_coef_Q8[ i ] ), 8 );
	srai	a5, a5, 8	# pred_Q10, tmp143,
	srai	a6, a6, 16	# tmp149, tmp148,
	add.n	a2, a2, a5	# tmp152, tmp151, pred_Q10
# @OPUS@\upstream\silk\NLSF_decode.c:49:         if( out_Q10 > 0 ) {
	blti	a3, 1, .L5	# out_Q10,,
	j	.L18		#
.L5:
# @OPUS@\upstream\silk\NLSF_decode.c:52:             out_Q10 = silk_ADD16( out_Q10, SILK_FIX_CONST( NLSF_QUANT_LEVEL_ADJ, 10 ) );
	addi	a2, a3, 102	# out_Q10, out_Q10,
	extui	a6, a2, 0, 16	# tmp153, out_Q10,
	srai	a2, a2, 16	# tmp156, out_Q10,
	mull	a6, a6, a11	# tmp154, tmp153, _5
	mull	a2, a2, a11	# tmp157, tmp156, _5
	srai	a6, a6, 16	# tmp155, tmp154,
	add.n	a2, a2, a5	# tmp158, tmp157, pred_Q10
# @OPUS@\upstream\silk\NLSF_decode.c:51:         } else if( out_Q10 < 0 ) {
	beqz.n	a3, .L6	# out_Q10,
.L18:
	add.n	a5, a6, a2	# pred_Q10, tmp155, tmp158
.L6:
# @OPUS@\upstream\silk\NLSF_decode.c:55:         x_Q10[ i ] = out_Q10;
	s16i	a5, a8, 0	# MEM[base: _64, offset: 0B], pred_Q10
	addi.n	a2, a7, -1	# ivtmp$20, ivtmp$20,
	addi.n	a10, a10, -1	# ivtmp$22, ivtmp$22,
	addi	a8, a8, -2	# ivtmp$23, ivtmp$23,
# @OPUS@\upstream\silk\NLSF_decode.c:46:     for( i = order-1; i >= 0; i-- ) {
	bne	a12, a7, .L11	# tmp129, ivtmp$20,
	j	.L8		#
.L3:
	slli	a6, a13, 1	# tmp159, tmp4,
	l32i	a13, sp, 92	# %sfp, ivtmp$13
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	movi.n	a15, 0	# i,
	mov.n	a12, sp	# ivtmp$10,
	add.n	a14, a2, a6	# ivtmp$11, _15, tmp159
.L10:
# @OPUS@\upstream\silk\NLSF_decode.c:87:         NLSF_Q15_tmp = silk_ADD_LSHIFT32( silk_DIV32_16( silk_LSHIFT( (opus_int32)res_Q10[ i ], 14 ), pCB_Wght_Q9[ i ] ), (opus_int16)pCB_element[ i ], 7 );
	l32i	a4, sp, 84	# %sfp,
	l16si	a2, a12, 0	# MEM[base: _23, offset: 0B], tmp164
	add.n	a3, a15, a4	# tmp160, i,
	l32i	a4, sp, 88	# %sfp,
	slli	a2, a2, 14	#, tmp164,
	add.n	a3, a4, a3	# tmp161,, tmp160
	l8ui	a4, a3, 0	# MEM[base: _28, offset: 0B], MEM[base: _28, offset: 0B]
	l16si	a3, a14, 0	# MEM[base: _24, offset: 0B],
	slli	a4, a4, 7	# tmp163, MEM[base: _28, offset: 0B],
	s32i	a4, sp, 96	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\NLSF_decode.c:87:         NLSF_Q15_tmp = silk_ADD_LSHIFT32( silk_DIV32_16( silk_LSHIFT( (opus_int32)res_Q10[ i ], 14 ), pCB_Wght_Q9[ i ] ), (opus_int16)pCB_element[ i ], 7 );
	l32i	a4, sp, 96	#,
# @OPUS@\upstream\silk\NLSF_decode.c:88:         pNLSF_Q15[ i ] = (opus_int16)silk_LIMIT( NLSF_Q15_tmp, 0, 32767 );
	l32r	a3, .LC0	#, iftmp$2_169
# @OPUS@\upstream\silk\NLSF_decode.c:87:         NLSF_Q15_tmp = silk_ADD_LSHIFT32( silk_DIV32_16( silk_LSHIFT( (opus_int32)res_Q10[ i ], 14 ), pCB_Wght_Q9[ i ] ), (opus_int16)pCB_element[ i ], 7 );
	add.n	a2, a4, a2	# NLSF_Q15_tmp, tmp163,
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	addi.n	a15, a15, 1	# i, i,
# @OPUS@\upstream\silk\NLSF_decode.c:88:         pNLSF_Q15[ i ] = (opus_int16)silk_LIMIT( NLSF_Q15_tmp, 0, 32767 );
	blt	a3, a2, .L9	# tmp4, NLSF_Q15_tmp,
	movi.n	a3, 0	# iftmp$2_169,
	slli	a4, a2, 16	# tmp176, NLSF_Q15_tmp,
	blt	a2, a3, .L9	# NLSF_Q15_tmp,,
	srai	a3, a4, 16	# iftmp$2_169, tmp176,
.L9:
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	l32i	a2, sp, 80	# %sfp,
# @OPUS@\upstream\silk\NLSF_decode.c:88:         pNLSF_Q15[ i ] = (opus_int16)silk_LIMIT( NLSF_Q15_tmp, 0, 32767 );
	s16i	a3, a13, 0	# MEM[base: _29, offset: 0B], iftmp$2_169
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	l16si	a4, a2, 2	# psNLSF_CB_41(D)->order, _95
	addi.n	a12, a12, 2	# ivtmp$10, ivtmp$10,
	addi.n	a14, a14, 2	# ivtmp$11, ivtmp$11,
	addi.n	a13, a13, 2	# ivtmp$13, ivtmp$13,
# @OPUS@\upstream\silk\NLSF_decode.c:86:     for( i = 0; i < psNLSF_CB->order; i++ ) {
	blt	a15, a4, .L10	# i, _95,
.L4:
# @OPUS@\upstream\silk\NLSF_decode.c:92:     silk_NLSF_stabilize( pNLSF_Q15, psNLSF_CB->deltaMin_Q15, psNLSF_CB->order );
	l32i	a2, sp, 80	# %sfp,
	l32i.n	a3, a2, 36	# psNLSF_CB_41(D)->deltaMin_Q15,
	l32i	a2, sp, 92	# %sfp,
	call0	silk_NLSF_stabilize		#
# @OPUS@\upstream\silk\NLSF_decode.c:93: }
	l32i	a0, sp, 140	#,
	movi	a9, 0x90	#,
	l32i	a12, sp, 136	#,
	l32i	a13, sp, 132	#,
	l32i	a14, sp, 128	#,
	l32i	a15, sp, 124	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_NLSF_decode, .-silk_NLSF_decode
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
