# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_parameters.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_parameters.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_parameters.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_parameters.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_parameters.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_parameters.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_parameters.c.s.raw
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
	.section	.text.silk_decode_parameters,"ax",@progbits
	.literal_position
	.literal .LC0, 63570
	.literal .LC1, silk_LTPScales_table_Q14
	.literal .LC2, silk_LTP_vq_ptrs_Q7
	.align	4
	.global	silk_decode_parameters
	.type	silk_decode_parameters, @function
# Function: silk_decode_parameters
# Module: upstream/silk/decode_parameters.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Decode parameters from payload */
# C context: void silk_decode_parameters(
# C context: silk_decoder_state          *psDec,                         /* I/O  State                                       */
# C context: silk_decoder_control        *psDecCtrl,                     /* I/O  Decoder control                             */
# C context: opus_int                    condCoding                      /* I    The type of conditional coding to use       */
# C context: )
silk_decode_parameters:
	addi	sp, sp, -112	#,,
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
	mov.n	a14, a2	# psDec, psDec
# @OPUS@\upstream\silk\decode_parameters.c:46:     silk_gains_dequant( psDecCtrl->Gains_Q16, psDec->indices.GainsIndices,
	addmi	a15, a2, 0x400	# tmp826, psDec,
	addi	a4, a4, -2	# tmp392, condCoding,
	movi.n	a2, 1	# tmp393,
	movi.n	a5, 0	# tmp394,
	moveqz	a5, a2, a4	# tmp391, tmp393, tmp392
	l32i.n	a6, a15, 24	# psDec_83(D)->nb_subfr,
# @OPUS@\upstream\silk\decode_parameters.c:40: {
	s32i	a12, sp, 104	#,
# @OPUS@\upstream\silk\decode_parameters.c:46:     silk_gains_dequant( psDecCtrl->Gains_Q16, psDec->indices.GainsIndices,
	movi	a4, 0x40c	# tmp395,
# @OPUS@\upstream\silk\decode_parameters.c:40: {
	mov.n	a12, a3	# psDecCtrl, psDecCtrl
# @OPUS@\upstream\silk\decode_parameters.c:46:     silk_gains_dequant( psDecCtrl->Gains_Q16, psDec->indices.GainsIndices,
	movi	a3, 0x5b4	# tmp397,
	add.n	a4, a14, a4	#, psDec, tmp395
	add.n	a3, a14, a3	#, psDec, tmp397
	addi	a2, a12, 16	#, psDecCtrl,
# @OPUS@\upstream\silk\decode_parameters.c:40: {
	s32i	a0, sp, 108	#,
	s32i	a13, sp, 100	#,
# @OPUS@\upstream\silk\decode_parameters.c:46:     silk_gains_dequant( psDecCtrl->Gains_Q16, psDec->indices.GainsIndices,
	call0	silk_gains_dequant		#
# @OPUS@\upstream\silk\decode_parameters.c:52:     silk_NLSF_decode( pNLSF_Q15, psDec->indices.NLSFIndices, psDec->psNLSF_CB );
	addmi	a13, a14, 0x500	# tmp827, psDec,
	l32i	a4, a13, 176	# psDec_83(D)->psNLSF_CB,
# @OPUS@\upstream\silk\decode_parameters.c:52:     silk_NLSF_decode( pNLSF_Q15, psDec->indices.NLSFIndices, psDec->psNLSF_CB );
	movi	a3, 0x5bc	# tmp401,
# @OPUS@\upstream\silk\decode_parameters.c:52:     silk_NLSF_decode( pNLSF_Q15, psDec->indices.NLSFIndices, psDec->psNLSF_CB );
	add.n	a3, a14, a3	#, psDec, tmp401
	addi	a2, sp, 32	#,,
	call0	silk_NLSF_decode		#
# @OPUS@\upstream\silk\decode_parameters.c:55:     silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 1 ], pNLSF_Q15, psDec->LPC_order, psDec->arch );
	addi	a3, a12, 64	#, psDecCtrl,
# @OPUS@\upstream\silk\decode_parameters.c:55:     silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 1 ], pNLSF_Q15, psDec->LPC_order, psDec->arch );
	addmi	a2, a14, 0xb00	#, psDec,
# @OPUS@\upstream\silk\decode_parameters.c:55:     silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 1 ], pNLSF_Q15, psDec->LPC_order, psDec->arch );
	s32i	a3, sp, 68	# %sfp,
# @OPUS@\upstream\silk\decode_parameters.c:55:     silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 1 ], pNLSF_Q15, psDec->LPC_order, psDec->arch );
	s32i	a2, sp, 64	# %sfp,
	l32i	a5, a2, 76	# psDec_83(D)->arch,
	l32i.n	a4, a15, 40	# psDec_83(D)->LPC_order,
	l32i	a2, sp, 68	# %sfp,
	addi	a3, sp, 32	#,,
	call0	silk_NLSF2A		#
# @OPUS@\upstream\silk\decode_parameters.c:59:     if( psDec->first_frame_after_reset == 1 ) {
	l32i	a2, a15, 76	# psDec_83(D)->first_frame_after_reset, psDec_83(D)->first_frame_after_reset
	bnei	a2, 1, .L2	# psDec_83(D)->first_frame_after_reset,,
# @OPUS@\upstream\silk\decode_parameters.c:60:         psDec->indices.NLSFInterpCoef_Q2 = 4;
	movi.n	a2, 4	# tmp410,
	s8i	a2, a13, 211	# psDec_83(D)->indices.NLSFInterpCoef_Q2, tmp410
	j	.L3		#
.L2:
# @OPUS@\upstream\silk\decode_parameters.c:63:     if( psDec->indices.NLSFInterpCoef_Q2 < 4 ) {
	l8ui	a2, a13, 211	# psDec_83(D)->indices.NLSFInterpCoef_Q2, _13
	l32i.n	a4, a15, 40	# psDec_83(D)->LPC_order, pretmp_222
# @OPUS@\upstream\silk\decode_parameters.c:63:     if( psDec->indices.NLSFInterpCoef_Q2 < 4 ) {
	slli	a2, a2, 24	# tmp414, _13,
	srai	a2, a2, 24	# tmp413, tmp414,
	bgei	a2, 4, .L3	# tmp413,,
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	bgei	a4, 1, .L4	# pretmp_222,,
.L6:
# @OPUS@\upstream\silk\decode_parameters.c:72:         silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 0 ], pNLSF0_Q15, psDec->LPC_order, psDec->arch );
	l32i	a3, sp, 64	# %sfp,
# @OPUS@\upstream\silk\decode_parameters.c:72:         silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 0 ], pNLSF0_Q15, psDec->LPC_order, psDec->arch );
	addi	a2, a12, 32	#, psDecCtrl,
# @OPUS@\upstream\silk\decode_parameters.c:72:         silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 0 ], pNLSF0_Q15, psDec->LPC_order, psDec->arch );
	l32i	a5, a3, 76	# psDec_83(D)->arch,
	mov.n	a3, sp	#,
# @OPUS@\upstream\silk\decode_parameters.c:72:         silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 0 ], pNLSF0_Q15, psDec->LPC_order, psDec->arch );
	s32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_parameters.c:72:         silk_NLSF2A( psDecCtrl->PredCoef_Q12[ 0 ], pNLSF0_Q15, psDec->LPC_order, psDec->arch );
	call0	silk_NLSF2A		#
	j	.L5		#
.L4:
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 44	# psDec_83(D)->prevNLSF_Q15, _293
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 32	# pNLSF_Q15, tmp420
	sub	a3, a3, a5	# tmp423, tmp420, _293
	mull	a3, a3, a2	# tmp424, tmp423, tmp413
	srai	a3, a3, 2	# tmp425, tmp424,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp427, _293, tmp425
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 0	# pNLSF0_Q15, tmp427
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 1, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 46	# psDec_83(D)->prevNLSF_Q15, _306
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 34	# pNLSF_Q15, tmp431
	sub	a3, a3, a5	# tmp434, tmp431, _306
	mull	a3, a3, a2	# tmp435, tmp434, tmp413
	srai	a3, a3, 2	# tmp436, tmp435,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp438, _306, tmp436
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 2	# pNLSF0_Q15, tmp438
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 2, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 48	# psDec_83(D)->prevNLSF_Q15, _319
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 36	# pNLSF_Q15, tmp442
	sub	a3, a3, a5	# tmp445, tmp442, _319
	mull	a3, a3, a2	# tmp446, tmp445, tmp413
	srai	a3, a3, 2	# tmp447, tmp446,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp449, _319, tmp447
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 4	# pNLSF0_Q15, tmp449
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 3, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 50	# psDec_83(D)->prevNLSF_Q15, _332
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 38	# pNLSF_Q15, tmp453
	sub	a3, a3, a5	# tmp456, tmp453, _332
	mull	a3, a3, a2	# tmp457, tmp456, tmp413
	srai	a3, a3, 2	# tmp458, tmp457,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp460, _332, tmp458
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 6	# pNLSF0_Q15, tmp460
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 4, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 52	# psDec_83(D)->prevNLSF_Q15, _345
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 40	# pNLSF_Q15, tmp464
	sub	a3, a3, a5	# tmp467, tmp464, _345
	mull	a3, a3, a2	# tmp468, tmp467, tmp413
	srai	a3, a3, 2	# tmp469, tmp468,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp471, _345, tmp469
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 8	# pNLSF0_Q15, tmp471
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 5, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 54	# psDec_83(D)->prevNLSF_Q15, _358
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 42	# pNLSF_Q15, tmp475
	sub	a3, a3, a5	# tmp478, tmp475, _358
	mull	a3, a3, a2	# tmp479, tmp478, tmp413
	srai	a3, a3, 2	# tmp480, tmp479,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp482, _358, tmp480
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 10	# pNLSF0_Q15, tmp482
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 6, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 56	# psDec_83(D)->prevNLSF_Q15, _371
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 44	# pNLSF_Q15, tmp486
	sub	a3, a3, a5	# tmp489, tmp486, _371
	mull	a3, a3, a2	# tmp490, tmp489, tmp413
	srai	a3, a3, 2	# tmp491, tmp490,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp493, _371, tmp491
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 12	# pNLSF0_Q15, tmp493
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 7, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 58	# psDec_83(D)->prevNLSF_Q15, _384
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 46	# pNLSF_Q15, tmp497
	sub	a3, a3, a5	# tmp500, tmp497, _384
	mull	a3, a3, a2	# tmp501, tmp500, tmp413
	srai	a3, a3, 2	# tmp502, tmp501,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp504, _384, tmp502
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 14	# pNLSF0_Q15, tmp504
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 8, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 60	# psDec_83(D)->prevNLSF_Q15, _397
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 48	# pNLSF_Q15, tmp508
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a6, 9	# tmp516,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	sub	a3, a3, a5	# tmp511, tmp508, _397
	mull	a3, a3, a2	# tmp512, tmp511, tmp413
	srai	a3, a3, 2	# tmp513, tmp512,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp515, _397, tmp513
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 16	# pNLSF0_Q15, tmp515
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a6, .L6	# pretmp_222, tmp516,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 62	# psDec_83(D)->prevNLSF_Q15, _410
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 50	# pNLSF_Q15, tmp520
	sub	a3, a3, a5	# tmp523, tmp520, _410
	mull	a3, a3, a2	# tmp524, tmp523, tmp413
	srai	a3, a3, 2	# tmp525, tmp524,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp527, _410, tmp525
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 18	# pNLSF0_Q15, tmp527
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 10, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 64	# psDec_83(D)->prevNLSF_Q15, _423
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 52	# pNLSF_Q15, tmp531
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a6, 0xb	# tmp539,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	sub	a3, a3, a5	# tmp534, tmp531, _423
	mull	a3, a3, a2	# tmp535, tmp534, tmp413
	srai	a3, a3, 2	# tmp536, tmp535,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp538, _423, tmp536
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 20	# pNLSF0_Q15, tmp538
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a6, .L6	# pretmp_222, tmp539,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 66	# psDec_83(D)->prevNLSF_Q15, _436
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 54	# pNLSF_Q15, tmp543
	sub	a3, a3, a5	# tmp546, tmp543, _436
	mull	a3, a3, a2	# tmp547, tmp546, tmp413
	srai	a3, a3, 2	# tmp548, tmp547,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp550, _436, tmp548
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 22	# pNLSF0_Q15, tmp550
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beqi	a4, 12, .L6	# pretmp_222,,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 68	# psDec_83(D)->prevNLSF_Q15, _449
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 56	# pNLSF_Q15, tmp554
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a6, 0xd	# tmp562,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	sub	a3, a3, a5	# tmp557, tmp554, _449
	mull	a3, a3, a2	# tmp558, tmp557, tmp413
	srai	a3, a3, 2	# tmp559, tmp558,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp561, _449, tmp559
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 24	# pNLSF0_Q15, tmp561
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a6, .L6	# pretmp_222, tmp562,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 70	# psDec_83(D)->prevNLSF_Q15, _462
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 58	# pNLSF_Q15, tmp566
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a6, 0xe	# tmp574,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	sub	a3, a3, a5	# tmp569, tmp566, _462
	mull	a3, a3, a2	# tmp570, tmp569, tmp413
	srai	a3, a3, 2	# tmp571, tmp570,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp573, _462, tmp571
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 26	# pNLSF0_Q15, tmp573
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a6, .L6	# pretmp_222, tmp574,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 72	# psDec_83(D)->prevNLSF_Q15, _475
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 60	# pNLSF_Q15, tmp578
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	movi.n	a6, 0xf	# tmp586,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	sub	a3, a3, a5	# tmp581, tmp578, _475
	mull	a3, a3, a2	# tmp582, tmp581, tmp413
	srai	a3, a3, 2	# tmp583, tmp582,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a3, a5, a3	# tmp585, _475, tmp583
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a3, sp, 28	# pNLSF0_Q15, tmp585
# @OPUS@\upstream\silk\decode_parameters.c:66:         for( i = 0; i < psDec->LPC_order; i++ ) {
	beq	a4, a6, .L6	# pretmp_222, tmp586,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a5, a15, 74	# psDec_83(D)->prevNLSF_Q15, _14
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	l16si	a3, sp, 62	# pNLSF_Q15, tmp590
	sub	a3, a3, a5	# tmp593, tmp590, _14
	mull	a2, a3, a2	# tmp594, tmp593, tmp413
	srai	a2, a2, 2	# tmp595, tmp594,
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	add.n	a2, a5, a2	# tmp597, _14, tmp595
# @OPUS@\upstream\silk\decode_parameters.c:67:             pNLSF0_Q15[ i ] = psDec->prevNLSF_Q15[ i ] + silk_RSHIFT( silk_MUL( psDec->indices.NLSFInterpCoef_Q2,
	s16i	a2, sp, 30	# pNLSF0_Q15, tmp597
	j	.L6		#
.L3:
# @OPUS@\upstream\silk\decode_parameters.c:75:         silk_memcpy( psDecCtrl->PredCoef_Q12[ 0 ], psDecCtrl->PredCoef_Q12[ 1 ], psDec->LPC_order * sizeof( opus_int16 ) );
	l32i.n	a4, a15, 40	# psDec_83(D)->LPC_order, psDec_83(D)->LPC_order
	l32i	a3, sp, 68	# %sfp,
	addi	a2, a12, 32	#, psDecCtrl,
	slli	a4, a4, 1	#, psDec_83(D)->LPC_order,
	s32i	a2, sp, 72	# %sfp,
	call0	memcpy		#
.L5:
# @OPUS@\upstream\silk\decode_parameters.c:78:     silk_memcpy( psDec->prevNLSF_Q15, pNLSF_Q15, psDec->LPC_order * sizeof( opus_int16 ) );
	l32i.n	a5, a15, 40	# psDec_83(D)->LPC_order, _33
	movi	a2, 0x42c	# tmp606,
	slli	a4, a5, 1	#, _33,
	addi	a3, sp, 32	#,,
	add.n	a2, a14, a2	#, psDec, tmp606
	s32i	a5, sp, 76	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_parameters.c:81:     if( psDec->lossCnt ) {
	l32i	a3, sp, 64	# %sfp,
	l32i	a5, sp, 76	#,
	l32i	a2, a3, 68	# psDec_83(D)->lossCnt, psDec_83(D)->lossCnt
	beqz.n	a2, .L7	# psDec_83(D)->lossCnt,
# @OPUS@\upstream\silk\decode_parameters.c:82:         silk_bwexpander( psDecCtrl->PredCoef_Q12[ 0 ], psDec->LPC_order, BWE_AFTER_LOSS_Q16 );
	l32r	a14, .LC0	#, tmp616
	l32i	a2, sp, 72	# %sfp,
	mov.n	a3, a5	#, _33
	mov.n	a4, a14	#, tmp616
	call0	silk_bwexpander		#
# @OPUS@\upstream\silk\decode_parameters.c:83:         silk_bwexpander( psDecCtrl->PredCoef_Q12[ 1 ], psDec->LPC_order, BWE_AFTER_LOSS_Q16 );
	l32i.n	a3, a15, 40	# psDec_83(D)->LPC_order,
	l32i	a2, sp, 68	# %sfp,
	mov.n	a4, a14	#, tmp616
	call0	silk_bwexpander		#
.L7:
# @OPUS@\upstream\silk\decode_parameters.c:86:     if( psDec->indices.signalType == TYPE_VOICED ) {
	l8ui	a2, a13, 209	# psDec_83(D)->indices.signalType, tmp621
	l32i.n	a6, a15, 24	# psDec_83(D)->nb_subfr, pretmp_202
	bnei	a2, 2, .L8	# tmp621,,
# @OPUS@\upstream\silk\decode_parameters.c:92:         silk_decode_pitch( psDec->indices.lagIndex, psDec->indices.contourIndex, psDecCtrl->pitchL, psDec->fs_kHz, psDec->nb_subfr );
	l8ui	a3, a13, 208	# psDec_83(D)->indices.contourIndex,
	l16si	a2, a13, 206	# psDec_83(D)->indices.lagIndex,
	l32i.n	a5, a15, 16	# psDec_83(D)->fs_kHz,
	slli	a3, a3, 24	# tmp628, psDec_83(D)->indices.contourIndex,
	mov.n	a4, a12	#, psDecCtrl
	srai	a3, a3, 24	#, tmp628,
	call0	silk_decode_pitch		#
# @OPUS@\upstream\silk\decode_parameters.c:95:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ psDec->indices.PERIndex ]; /* set pointer to start of codebook */
	l8ui	a2, a13, 212	# psDec_83(D)->indices.PERIndex,
# @OPUS@\upstream\silk\decode_parameters.c:97:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i.n	a4, a15, 24	# psDec_83(D)->nb_subfr, _154
# @OPUS@\upstream\silk\decode_parameters.c:95:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ psDec->indices.PERIndex ]; /* set pointer to start of codebook */
	slli	a2, a2, 24	# tmp635, psDec_83(D)->indices.PERIndex,
	srai	a2, a2, 24	# _48, tmp635,
# @OPUS@\upstream\silk\decode_parameters.c:97:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	bgei	a4, 1, .L9	# _154,,
.L11:
# @OPUS@\upstream\silk\decode_parameters.c:107:         Ix = psDec->indices.LTP_scaleIndex;
	l8ui	a2, a13, 213	# psDec_83(D)->indices.LTP_scaleIndex,
# @OPUS@\upstream\silk\decode_parameters.c:108:         psDecCtrl->LTP_scale_Q14 = silk_LTPScales_table_Q14[ Ix ];
	l32r	a3, .LC1	#, tmp637
# @OPUS@\upstream\silk\decode_parameters.c:107:         Ix = psDec->indices.LTP_scaleIndex;
	slli	a2, a2, 24	# tmp641, psDec_83(D)->indices.LTP_scaleIndex,
# @OPUS@\upstream\silk\decode_parameters.c:108:         psDecCtrl->LTP_scale_Q14 = silk_LTPScales_table_Q14[ Ix ];
	srai	a2, a2, 23	# tmp642, tmp641,
	add.n	a2, a3, a2	# tmp643, tmp637, tmp642
	l16si	a2, a2, 0	# silk_LTPScales_table_Q14, tmp644
	s32i	a2, a12, 136	# psDecCtrl_82(D)->LTP_scale_Q14, tmp644
	j	.L1		#
.L9:
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a13, 184	# psDec_83(D)->indices.LTPIndex,
# @OPUS@\upstream\silk\decode_parameters.c:95:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ psDec->indices.PERIndex ]; /* set pointer to start of codebook */
	l32r	a5, .LC2	#, tmp647
	slli	a2, a2, 2	# tmp648, _48,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	slli	a3, a3, 24	# tmp654, psDec_83(D)->indices.LTPIndex,
	srai	a3, a3, 24	# tmp655, tmp654,
# @OPUS@\upstream\silk\decode_parameters.c:95:         cbk_ptr_Q7 = silk_LTP_vq_ptrs_Q7[ psDec->indices.PERIndex ]; /* set pointer to start of codebook */
	add.n	a2, a5, a2	# tmp649, tmp647, tmp648
	l32i.n	a5, a2, 0	# silk_LTP_vq_ptrs_Q7, cbk_ptr_Q7
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	slli	a2, a3, 2	# tmp658, tmp655,
	add.n	a2, a2, a3	# tmp659, tmp658, tmp655
	add.n	a2, a5, a2	# tmp660, cbk_ptr_Q7, tmp659
	l8ui	a3, a2, 0	# *_228,
	slli	a3, a3, 24	# tmp663, *_228,
	srai	a3, a3, 17	# tmp664, tmp663,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 96	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 96B], tmp664
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 1	# *_216,
	slli	a3, a3, 24	# tmp669, *_216,
	srai	a3, a3, 17	# tmp670, tmp669,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 98	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 98B], tmp670
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 2	# *_199,
	slli	a3, a3, 24	# tmp675, *_199,
	srai	a3, a3, 17	# tmp676, tmp675,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 100	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 100B], tmp676
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 3	# *_189,
	slli	a3, a3, 24	# tmp681, *_189,
	srai	a3, a3, 17	# tmp682, tmp681,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 102	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 102B], tmp682
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a2, 4	# *_180,
	slli	a2, a2, 24	# tmp687, *_180,
	srai	a2, a2, 17	# tmp688, tmp687,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 104	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 104B], tmp688
# @OPUS@\upstream\silk\decode_parameters.c:97:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	beqi	a4, 1, .L11	# _154,,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a13, 185	# psDec_83(D)->indices.LTPIndex,
	slli	a2, a2, 24	# tmp693, psDec_83(D)->indices.LTPIndex,
	srai	a2, a2, 24	# tmp694, tmp693,
	slli	a3, a2, 2	# tmp697, tmp694,
	add.n	a2, a3, a2	# tmp698, tmp697, tmp694
	add.n	a2, a5, a2	# tmp699, cbk_ptr_Q7, tmp698
	l8ui	a3, a2, 0	# *_113,
	slli	a3, a3, 24	# tmp702, *_113,
	srai	a3, a3, 17	# tmp703, tmp702,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 106	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 106B], tmp703
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 1	# *_73,
	slli	a3, a3, 24	# tmp708, *_73,
	srai	a3, a3, 17	# tmp709, tmp708,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 108	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 108B], tmp709
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 2	# *_53,
	slli	a3, a3, 24	# tmp714, *_53,
	srai	a3, a3, 17	# tmp715, tmp714,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 110	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 110B], tmp715
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 3	# *_207,
	slli	a3, a3, 24	# tmp720, *_207,
	srai	a3, a3, 17	# tmp721, tmp720,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 112	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 112B], tmp721
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a2, 4	# *_44,
	slli	a2, a2, 24	# tmp726, *_44,
	srai	a2, a2, 17	# tmp727, tmp726,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 114	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 114B], tmp727
# @OPUS@\upstream\silk\decode_parameters.c:97:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	beqi	a4, 2, .L11	# _154,,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a13, 186	# psDec_83(D)->indices.LTPIndex,
	slli	a2, a2, 24	# tmp732, psDec_83(D)->indices.LTPIndex,
	srai	a2, a2, 24	# tmp733, tmp732,
	slli	a3, a2, 2	# tmp736, tmp733,
	add.n	a2, a3, a2	# tmp737, tmp736, tmp733
	add.n	a2, a5, a2	# tmp738, cbk_ptr_Q7, tmp737
	l8ui	a3, a2, 0	# *_247,
	slli	a3, a3, 24	# tmp741, *_247,
	srai	a3, a3, 17	# tmp742, tmp741,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 116	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 116B], tmp742
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 1	# *_256,
	slli	a3, a3, 24	# tmp747, *_256,
	srai	a3, a3, 17	# tmp748, tmp747,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 118	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 118B], tmp748
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 2	# *_265,
	slli	a3, a3, 24	# tmp753, *_265,
	srai	a3, a3, 17	# tmp754, tmp753,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 120	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 120B], tmp754
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a3, a2, 3	# *_274,
	slli	a3, a3, 24	# tmp759, *_274,
	srai	a3, a3, 17	# tmp760, tmp759,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a3, a12, 122	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 122B], tmp760
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a2, 4	# *_283,
	slli	a2, a2, 24	# tmp765, *_283,
	srai	a2, a2, 17	# tmp766, tmp765,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 124	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 124B], tmp766
# @OPUS@\upstream\silk\decode_parameters.c:97:         for( k = 0; k < psDec->nb_subfr; k++ ) {
	beqi	a4, 3, .L11	# _154,,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a13, 187	# psDec_83(D)->indices.LTPIndex,
	slli	a2, a2, 24	# tmp771, psDec_83(D)->indices.LTPIndex,
	srai	a2, a2, 24	# tmp772, tmp771,
	slli	a3, a2, 2	# tmp775, tmp772,
	add.n	a2, a3, a2	# tmp776, tmp775, tmp772
	add.n	a5, a5, a2	# tmp777, cbk_ptr_Q7, tmp776
	l8ui	a2, a5, 0	# *_115,
	slli	a2, a2, 24	# tmp780, *_115,
	srai	a2, a2, 17	# tmp781, tmp780,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 126	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 126B], tmp781
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a5, 1	# *_129,
	slli	a2, a2, 24	# tmp786, *_129,
	srai	a2, a2, 17	# tmp787, tmp786,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 128	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 128B], tmp787
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a5, 2	# *_143,
	slli	a2, a2, 24	# tmp792, *_143,
	srai	a2, a2, 17	# tmp793, tmp792,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 130	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 130B], tmp793
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a5, 3	# *_157,
	slli	a2, a2, 24	# tmp798, *_157,
	srai	a2, a2, 17	# tmp799, tmp798,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 132	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 132B], tmp799
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	l8ui	a2, a5, 4	# *_171,
	slli	a2, a2, 24	# tmp804, *_171,
	srai	a2, a2, 17	# tmp805, tmp804,
# @OPUS@\upstream\silk\decode_parameters.c:100:                 psDecCtrl->LTPCoef_Q14[ k * LTP_ORDER + i ] = silk_LSHIFT( cbk_ptr_Q7[ Ix * LTP_ORDER + i ], 7 );
	s16i	a2, a12, 134	# MEM[(struct silk_decoder_control *)psDecCtrl_82(D) + 134B], tmp805
	j	.L11		#
.L8:
# @OPUS@\upstream\silk\decode_parameters.c:110:         silk_memset( psDecCtrl->pitchL,      0,             psDec->nb_subfr * sizeof( opus_int   ) );
	slli	a4, a6, 2	#, pretmp_202,
	movi.n	a3, 0	#,
	mov.n	a2, a12	#, psDecCtrl
	call0	memset		#
# @OPUS@\upstream\silk\decode_parameters.c:111:         silk_memset( psDecCtrl->LTPCoef_Q14, 0, LTP_ORDER * psDec->nb_subfr * sizeof( opus_int16 ) );
	l32i.n	a2, a15, 24	# psDec_83(D)->nb_subfr, psDec_83(D)->nb_subfr
	movi.n	a3, 0	#,
	slli	a4, a2, 2	# tmp813, psDec_83(D)->nb_subfr,
	add.n	a4, a4, a2	# tmp814, tmp813, psDec_83(D)->nb_subfr
	slli	a4, a4, 1	#, tmp814,
	addi	a2, a12, 96	#, psDecCtrl,
	call0	memset		#
# @OPUS@\upstream\silk\decode_parameters.c:112:         psDec->indices.PERIndex  = 0;
	movi.n	a2, 0	# tmp822,
	s8i	a2, a13, 212	# psDec_83(D)->indices.PERIndex, tmp822
# @OPUS@\upstream\silk\decode_parameters.c:113:         psDecCtrl->LTP_scale_Q14 = 0;
	movi.n	a2, 0	# tmp823,
	s32i	a2, a12, 136	# psDecCtrl_82(D)->LTP_scale_Q14, tmp823
.L1:
# @OPUS@\upstream\silk\decode_parameters.c:115: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	silk_decode_parameters, .-silk_decode_parameters
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
