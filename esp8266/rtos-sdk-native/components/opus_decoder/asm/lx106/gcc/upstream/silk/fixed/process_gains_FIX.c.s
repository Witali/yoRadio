# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/process_gains_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"process_gains_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\process_gains_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\process_gains_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\process_gains_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\process_gains_FIX.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_process_gains_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, 46214
	.literal .LC2, 32768
	.literal .LC3, 2147418112
	.literal .LC4, 8894
	.literal .LC5, 21627
	.literal .LC6, 4736
	.literal .LC7, 32766
	.literal .LC8, 32767
	.literal .LC9, 65127
	.literal .LC10, 64718
	.literal .LC11, 13108
	.literal .LC12, silk_Quantization_Offsets_Q10
	.literal .LC13, 52429
	.align	4
	.global	silk_process_gains_FIX
	.type	silk_process_gains_FIX, @function
# Function: silk_process_gains_FIX
# Module: upstream/silk/fixed/process_gains_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "tuning_parameters.h"
# C context:
# C context: /* Processing of gains */
# C context: void silk_process_gains_FIX(
# C context: silk_encoder_state_FIX          *psEnc,                                 /* I/O  Encoder state                                                               */
# C context: silk_encoder_control_FIX        *psEncCtrl,                             /* I/O  Encoder control                                                             */
# C context: opus_int                        condCoding                              /* I    The type of conditional coding to use                                       */
# C context: )
silk_process_gains_FIX:
	addi	sp, sp, -80	#,,
	s32i	a12, sp, 72	#,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:47:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	addmi	a9, a2, 0x1200	#, psEnc,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:41: {
	s32i	a0, sp, 76	#,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:41: {
	s32i.n	a2, sp, 8	# %sfp, psEnc
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:47:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l8ui	a2, a9, 157	# psEnc_143(D)->sCmn.indices.signalType, tmp259
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:47:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	s32i.n	a9, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:41: {
	s32i.n	a4, sp, 24	# %sfp, condCoding
	mov.n	a12, a3	# psEncCtrl, psEncCtrl
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:47:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	beqi	a2, 2, .L2	# tmp259,,
	l32i.n	a9, sp, 8	# %sfp,
	addmi	a9, a9, 0x1100	#,,
	s32i.n	a9, sp, 4	# %sfp,
.L5:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:57:     InvMaxSqrVal_Q16 = silk_DIV32_16( silk_log2lin(
	l32i.n	a9, sp, 0	# %sfp,
	l32r	a3, .LC4	#, tmp263
	l32i	a2, a9, 108	# psEnc_143(D)->sCmn.SNR_dB_Q7, psEnc_143(D)->sCmn.SNR_dB_Q7
	l32r	a4, .LC5	#, tmp267
	sub	a3, a3, a2	# _21, tmp263, psEnc_143(D)->sCmn.SNR_dB_Q7
	extui	a2, a3, 0, 16	# tmp265, _21,
	mull	a2, a2, a4	# tmp266, tmp265, tmp267
	srai	a3, a3, 16	# tmp269, _21,
	mull	a3, a3, a4	# tmp270, tmp269, tmp267
	srai	a2, a2, 16	# tmp268, tmp266,
	add.n	a2, a2, a3	#, tmp268, tmp270
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:57:     InvMaxSqrVal_Q16 = silk_DIV32_16( silk_log2lin(
	l32i.n	a9, sp, 4	# %sfp,
	l32i	a3, a9, 236	# psEnc_143(D)->sCmn.subfr_length,
	call0	__divsi3		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:60:     for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	l32i.n	a9, sp, 4	# %sfp,
	l32i	a4, a9, 228	# psEnc_143(D)->sCmn.nb_subfr, _269
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:60:     for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	bgei	a4, 1, .L3	# _269,,
	slli	a4, a4, 2	#, _269,
	s32i.n	a4, sp, 20	# %sfp,
	j	.L4		#
.L2:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:49:         s_Q16 = -silk_sigm_Q15( silk_RSHIFT_ROUND( psEncCtrl->LTPredCodGain_Q7 - SILK_FIX_CONST( 12.0, 7 ), 4 ) );
	l32i	a2, a3, 396	# psEncCtrl_146(D)->LTPredCodGain_Q7, psEncCtrl_146(D)->LTPredCodGain_Q7
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	l32i.n	a9, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:49:         s_Q16 = -silk_sigm_Q15( silk_RSHIFT_ROUND( psEncCtrl->LTPredCodGain_Q7 - SILK_FIX_CONST( 12.0, 7 ), 4 ) );
	addmi	a2, a2, -0x600	# tmp278, psEncCtrl_146(D)->LTPredCodGain_Q7,
	srai	a2, a2, 3	# tmp280, tmp278,
	addi.n	a2, a2, 1	# tmp281, tmp280,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	addmi	a9, a9, 0x1100	#,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:49:         s_Q16 = -silk_sigm_Q15( silk_RSHIFT_ROUND( psEncCtrl->LTPredCodGain_Q7 - SILK_FIX_CONST( 12.0, 7 ), 4 ) );
	srai	a2, a2, 1	#, tmp281,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	s32i.n	a9, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:49:         s_Q16 = -silk_sigm_Q15( silk_RSHIFT_ROUND( psEncCtrl->LTPredCodGain_Q7 - SILK_FIX_CONST( 12.0, 7 ), 4 ) );
	call0	silk_sigm_Q15		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	l32i.n	a9, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:49:         s_Q16 = -silk_sigm_Q15( silk_RSHIFT_ROUND( psEncCtrl->LTPredCodGain_Q7 - SILK_FIX_CONST( 12.0, 7 ), 4 ) );
	neg	a2, a2	# s_Q16,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	l32i	a4, a9, 228	# psEnc_143(D)->sCmn.nb_subfr, _216
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	blti	a4, 1, .L5	# _216,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	l32i.n	a6, a12, 0	# psEncCtrl_146(D)->Gains_Q16, _470
	slli	a2, a2, 16	# tmp284, s_Q16,
	srai	a2, a2, 16	# _550, tmp284,
	extui	a3, a6, 0, 16	# tmp285, _470,
	srai	a5, a6, 16	# tmp288, _470,
	mull	a3, a3, a2	# tmp286, tmp285, _550
	mull	a5, a5, a2	# tmp289, tmp288, _550
	srai	a3, a3, 16	# tmp287, tmp286,
	add.n	a5, a5, a6	# tmp290, tmp289, _470
	add.n	a3, a3, a5	# tmp291, tmp287, tmp290
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	s32i.n	a3, a12, 0	# psEncCtrl_146(D)->Gains_Q16, tmp291
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	beqi	a4, 1, .L5	# _216,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	l32i.n	a6, a12, 4	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 4B], _484
	extui	a3, a6, 0, 16	# tmp292, _484,
	srai	a5, a6, 16	# tmp295, _484,
	mull	a3, a3, a2	# tmp293, tmp292, _550
	mull	a5, a5, a2	# tmp296, tmp295, _550
	srai	a3, a3, 16	# tmp294, tmp293,
	add.n	a5, a5, a6	# tmp297, tmp296, _484
	add.n	a3, a3, a5	# tmp298, tmp294, tmp297
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	s32i.n	a3, a12, 4	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 4B], tmp298
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	beqi	a4, 2, .L5	# _216,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	l32i.n	a6, a12, 8	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 8B], _502
	extui	a3, a6, 0, 16	# tmp299, _502,
	srai	a5, a6, 16	# tmp302, _502,
	mull	a3, a3, a2	# tmp300, tmp299, _550
	mull	a5, a5, a2	# tmp303, tmp302, _550
	srai	a3, a3, 16	# tmp301, tmp300,
	add.n	a5, a5, a6	# tmp304, tmp303, _502
	add.n	a3, a3, a5	# tmp305, tmp301, tmp304
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	s32i.n	a3, a12, 8	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 8B], tmp305
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:50:         for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	beqi	a4, 3, .L5	# _216,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	l32i.n	a5, a12, 12	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 12B], _8
	extui	a3, a5, 0, 16	# tmp306, _8,
	srai	a4, a5, 16	# tmp309, _8,
	mull	a3, a3, a2	# tmp307, tmp306, _550
	mull	a4, a4, a2	# tmp310, tmp309, _550
	srai	a2, a3, 16	# tmp308, tmp307,
	add.n	a3, a4, a5	# tmp311, tmp310, _8
	add.n	a2, a2, a3	# tmp312, tmp308, tmp311
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:51:             psEncCtrl->Gains_Q16[ k ] = silk_SMLAWB( psEncCtrl->Gains_Q16[ k ], psEncCtrl->Gains_Q16[ k ], s_Q16 );
	s32i.n	a2, a12, 12	# MEM[(struct silk_encoder_control_FIX *)psEncCtrl_146(D) + 12B], tmp312
	j	.L5		#
.L4:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:90:     silk_memcpy( psEncCtrl->GainsUnq_Q16, psEncCtrl->Gains_Q16, psEnc->sCmn.nb_subfr * sizeof( opus_int32 ) );
	l32i.n	a4, sp, 20	# %sfp,
	movi	a2, 0x1b0	# tmp313,
	mov.n	a3, a12	#, psEncCtrl
	add.n	a2, a12, a2	#, psEncCtrl, tmp313
	call0	memcpy		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:91:     psEncCtrl->lastGainIndexPrev = psShapeSt->LastGainIndex;
	l32i.n	a9, sp, 8	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:94:     silk_gains_quant( psEnc->sCmn.indices.GainsIndices, psEncCtrl->Gains_Q16,
	l32i.n	a6, sp, 24	# %sfp,
	movi.n	a8, 0	# tmp328,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:91:     psEncCtrl->lastGainIndexPrev = psShapeSt->LastGainIndex;
	addmi	a4, a9, 0x1c00	# tmp321,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:94:     silk_gains_quant( psEnc->sCmn.indices.GainsIndices, psEncCtrl->Gains_Q16,
	movi.n	a7, 1	# tmp327,
	addi	a5, a6, -2	# tmp326,,
	mov.n	a9, a8	#, tmp328
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:91:     psEncCtrl->lastGainIndexPrev = psShapeSt->LastGainIndex;
	l8ui	a3, a4, 0	# MEM[(struct silk_shape_state_FIX *)psEnc_143(D) + 7168B].LastGainIndex,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:94:     silk_gains_quant( psEnc->sCmn.indices.GainsIndices, psEncCtrl->Gains_Q16,
	moveqz	a9, a7, a5	#, tmp327, tmp326
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:91:     psEncCtrl->lastGainIndexPrev = psShapeSt->LastGainIndex;
	addmi	a2, a12, 0x100	# tmp320, psEncCtrl,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:94:     silk_gains_quant( psEnc->sCmn.indices.GainsIndices, psEncCtrl->Gains_Q16,
	mov.n	a5, a9	# tmp325,
	l32i.n	a9, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:91:     psEncCtrl->lastGainIndexPrev = psShapeSt->LastGainIndex;
	s8i	a3, a2, 192	# psEncCtrl_146(D)->lastGainIndexPrev, MEM[(struct silk_shape_state_FIX *)psEnc_143(D) + 7168B].LastGainIndex
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:94:     silk_gains_quant( psEnc->sCmn.indices.GainsIndices, psEncCtrl->Gains_Q16,
	l32i	a6, a9, 228	# psEnc_143(D)->sCmn.nb_subfr,
	l32r	a2, .LC6	#, tmp331
	l32i.n	a9, sp, 8	# %sfp,
	mov.n	a3, a12	#, psEncCtrl
	add.n	a2, a9, a2	#,, tmp331
	s32i.n	a7, sp, 32	#,
	s32i.n	a8, sp, 36	#,
	call0	silk_gains_quant		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:98:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l32i.n	a9, sp, 0	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:98:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l32i.n	a7, sp, 32	#,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:98:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l8ui	a2, a9, 157	# psEnc_143(D)->sCmn.indices.signalType, _93
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:98:     if( psEnc->sCmn.indices.signalType == TYPE_VOICED ) {
	l32i.n	a8, sp, 36	#,
	slli	a4, a2, 24	# tmp498, _93,
	bnei	a2, 2, .L45	# _93,,
	j	.L6		#
.L3:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:63:         ResNrgPart = silk_SMULWW( ResNrg, InvMaxSqrVal_Q16 );
	srai	a3, a2, 15	# tmp335, tmp276,
	slli	a4, a4, 2	#, _269,
	addi.n	a3, a3, 1	# tmp336, tmp335,
	slli	a2, a2, 16	# tmp337, tmp276,
	srai	a14, a2, 16	# _378, tmp337,
	mov.n	a15, a12	# ivtmp$21, psEncCtrl
	add.n	a6, a12, a4	#, psEncCtrl,
	srai	a3, a3, 1	#, tmp336,
	s32i.n	a12, sp, 28	# %sfp, psEncCtrl
	s32i.n	a4, sp, 20	# %sfp,
	mov.n	a12, a14	# _378, _378
	s32i.n	a3, sp, 12	# %sfp,
	s32i.n	a6, sp, 16	# %sfp,
	mov.n	a14, a15	# ivtmp$21, ivtmp$21
.L24:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:62:         ResNrg     = psEncCtrl->ResNrg[ k ];
	l32i	a2, a14, 400	# MEM[base: _514, offset: 400B], ResNrg
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:63:         ResNrgPart = silk_SMULWW( ResNrg, InvMaxSqrVal_Q16 );
	l32i.n	a9, sp, 12	# %sfp,
	srai	a10, a2, 16	# tmp339, ResNrg,
	extui	a6, a2, 0, 16	# tmp343, ResNrg,
	l32i.n	a15, a14, 0	# MEM[base: _514, offset: 0B], pretmp_552
	mull	a2, a9, a2	# tmp341,, ResNrg
	mull	a10, a10, a12	# tmp340, tmp339, _378
	mull	a6, a6, a12	# tmp344, tmp343, _378
	add.n	a10, a10, a2	# tmp342, tmp340, tmp341
	srai	a3, a15, 31	# tmp346, pretmp_552,
	srai	a6, a6, 16	# tmp345, tmp344,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:63:         ResNrgPart = silk_SMULWW( ResNrg, InvMaxSqrVal_Q16 );
	add.n	a6, a10, a6	# ResNrgPart, tmp342, tmp345
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:64:         if( psEncCtrl->ResNrgQ[ k ] > 0 ) {
	l32i	a13, a14, 416	# MEM[base: _514, offset: 416B], _42
	mov.n	a4, a15	#, pretmp_552
	mov.n	a5, a3	#, tmp346
	mov.n	a2, a15	#, pretmp_552
	s32i.n	a6, sp, 32	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:64:         if( psEncCtrl->ResNrgQ[ k ] > 0 ) {
	l32i.n	a6, sp, 32	#,
	blti	a13, 1, .L8	# _42,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:65:             ResNrgPart = silk_RSHIFT_ROUND( ResNrgPart, psEncCtrl->ResNrgQ[ k ] );
	bnei	a13, 1, .L9	# _42,,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:65:             ResNrgPart = silk_RSHIFT_ROUND( ResNrgPart, psEncCtrl->ResNrgQ[ k ] );
	extui	a13, a6, 0, 1	# tmp349, ResNrgPart,
	srai	a2, a6, 1	# tmp348, ResNrgPart,
	add.n	a6, a2, a13	# ResNrgPart, tmp348, tmp349
	mov.n	a13, a6	# ResNrgPart$3_195, ResNrgPart
	j	.L10		#
.L9:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:65:             ResNrgPart = silk_RSHIFT_ROUND( ResNrgPart, psEncCtrl->ResNrgQ[ k ] );
	addi.n	a13, a13, -1	# tmp350, _42,
	ssr	a13	# tmp350
	sra	a6, a6	# tmp351, ResNrgPart
	addi.n	a6, a6, 1	# tmp352, tmp351,
	srai	a6, a6, 1	# ResNrgPart, tmp352,
	mov.n	a13, a6	# ResNrgPart$3_195, ResNrgPart
	j	.L10		#
.L8:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:67:             if( ResNrgPart >= silk_RSHIFT( silk_int32_MAX, -psEncCtrl->ResNrgQ[ k ] ) ) {
	l32r	a4, .LC0	#,
	neg	a13, a13	# _48, _42
	ssr	a13	# _48
	sra	a2, a4	# tmp353,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:67:             if( ResNrgPart >= silk_RSHIFT( silk_int32_MAX, -psEncCtrl->ResNrgQ[ k ] ) ) {
	bge	a6, a2, .L11	# ResNrgPart, tmp353,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:70:                 ResNrgPart = silk_LSHIFT( ResNrgPart, -psEncCtrl->ResNrgQ[ k ] );
	ssl	a13	# _48
	sll	a13, a6	# ResNrgPart$3_195, ResNrgPart
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:70:                 ResNrgPart = silk_LSHIFT( ResNrgPart, -psEncCtrl->ResNrgQ[ k ] );
	mov.n	a6, a13	# ResNrgPart, ResNrgPart$3_195
.L10:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:74:         gain_squared = silk_ADD_SAT32( ResNrgPart, silk_SMMUL( gain, gain ) );
	add.n	a2, a13, a3	# tmp355, ResNrgPart$3_195, tmp497
	bltz	a2, .L12	# tmp355,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:74:         gain_squared = silk_ADD_SAT32( ResNrgPart, silk_SMMUL( gain, gain ) );
	and	a2, a6, a3	# tmp356, ResNrgPart, tmp497
	bltz	a2, .L13	# tmp356,
	j	.L48		#
.L12:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:74:         gain_squared = silk_ADD_SAT32( ResNrgPart, silk_SMMUL( gain, gain ) );
	or	a4, a6, a3	# tmp357, ResNrgPart, tmp497
	l32r	a2, .LC3	#, _438
	bgez	a4, .L15	# tmp357,
.L48:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:75:         if( gain_squared < silk_int16_MAX ) {
	l32r	a2, .LC7	#, tmp358
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:74:         gain_squared = silk_ADD_SAT32( ResNrgPart, silk_SMMUL( gain, gain ) );
	add.n	a6, a6, a3	# iftmp$2_135, ResNrgPart, tmp497
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:75:         if( gain_squared < silk_int16_MAX ) {
	blt	a2, a6, .L16	# tmp358, iftmp$2_135,
.L13:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:77:             gain_squared = silk_SMLAWW( silk_LSHIFT( ResNrgPart, 16 ), gain, gain );
	slli	a4, a15, 16	# tmp359, pretmp_552,
	srai	a2, a15, 15	# tmp360, pretmp_552,
	srai	a4, a4, 16	# _67, tmp359,
	addi.n	a2, a2, 1	# tmp361, tmp360,
	extui	a3, a15, 0, 16	# tmp364, pretmp_552,
	mull	a3, a3, a4	# tmp365, tmp364, _67
	srai	a2, a2, 1	# tmp362, tmp361,
	mull	a2, a2, a15	# tmp363, tmp362, pretmp_552
	srai	a5, a15, 16	# tmp368, pretmp_552,
	srai	a7, a3, 16	# tmp366, tmp365,
	mull	a4, a5, a4	# tmp369, tmp368, _67
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:77:             gain_squared = silk_SMLAWW( silk_LSHIFT( ResNrgPart, 16 ), gain, gain );
	add.n	a7, a2, a7	# tmp367, tmp363, tmp366
	add.n	a7, a7, a4	# tmp370, tmp367, tmp369
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:77:             gain_squared = silk_SMLAWW( silk_LSHIFT( ResNrgPart, 16 ), gain, gain );
	slli	a13, a13, 16	# tmp371, ResNrgPart$3_195,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:77:             gain_squared = silk_SMLAWW( silk_LSHIFT( ResNrgPart, 16 ), gain, gain );
	add.n	a13, a7, a13	# gain_squared, tmp370, tmp371
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	movi.n	a2, 0	# _493,
	blti	a13, 1, .L15	# gain_squared,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a13	# iftmp$17_180, gain_squared
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a5, 0x18	#,
	sub	a3, a5, a2	# _181,, iftmp$17_180
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:403:     if( rot == 0 ) {
	beqz.n	a3, .L18	# _181,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a3	# _181
	src	a4, a13, a13	# _189, gain_squared
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:405:     } else if( rot < 0 ) {
	bgez	a3, .L20	# _181,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a4, a2, -24	# m, iftmp$17_180,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a4	# m
	src	a4, a13, a13	# _189, gain_squared
.L20:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a13, a4, 0, 7	# _191, _189,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:82:         y = 32768;
	l32r	a5, .LC2	#, tmp504
	l32r	a4, .LC1	#, tmp505
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a3, a2, 0, 1	# tmp374, iftmp$17_180,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:82:         y = 32768;
	movnez	a4, a5, a3	# y, tmp504, tmp374
	j	.L21		#
.L28:
	l32r	a2, .LC2	#, tmp375
	l32r	a6, .LC8	#,
	ssr	a5	# _531
	sra	a4, a2	# _414, tmp375
	mull	a2, a4, a3	# tmp377, _414, _534
	srai	a2, a2, 16	# tmp378, tmp377,
	add.n	a2, a2, a4	# tmp376, tmp378, _414
	bge	a6, a2, .L27	#, tmp376,
	mov.n	a2, a6	# tmp376,
	j	.L27		#
.L22:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:60:     for( k = 0; k < psEnc->sCmn.nb_subfr; k++ ) {
	l32i.n	a9, sp, 16	# %sfp,
	addi.n	a14, a14, 4	# ivtmp$21, ivtmp$21,
	bne	a14, a9, .L24	# ivtmp$21,,
	l32i.n	a12, sp, 28	# %sfp, psEncCtrl
	j	.L4		#
.L45:
	l8ui	a7, a9, 158	# psEnc_143(D)->sCmn.indices.quantOffsetType,
	slli	a7, a7, 24	# tmp386, psEnc_143(D)->sCmn.indices.quantOffsetType,
	srai	a7, a7, 24	# _547, tmp386,
	j	.L25		#
.L6:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:99:         if( psEncCtrl->LTPredCodGain_Q7 + silk_RSHIFT( psEnc->sCmn.input_tilt_Q15, 8 ) > SILK_FIX_CONST( 1.0, 7 ) ) {
	l32i	a2, a9, 104	# psEnc_143(D)->sCmn.input_tilt_Q15, psEnc_143(D)->sCmn.input_tilt_Q15
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:99:         if( psEncCtrl->LTPredCodGain_Q7 + silk_RSHIFT( psEnc->sCmn.input_tilt_Q15, 8 ) > SILK_FIX_CONST( 1.0, 7 ) ) {
	l32i	a3, a12, 396	# psEncCtrl_146(D)->LTPredCodGain_Q7, psEncCtrl_146(D)->LTPredCodGain_Q7
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:99:         if( psEncCtrl->LTPredCodGain_Q7 + silk_RSHIFT( psEnc->sCmn.input_tilt_Q15, 8 ) > SILK_FIX_CONST( 1.0, 7 ) ) {
	srai	a2, a2, 8	# tmp388, psEnc_143(D)->sCmn.input_tilt_Q15,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:99:         if( psEncCtrl->LTPredCodGain_Q7 + silk_RSHIFT( psEnc->sCmn.input_tilt_Q15, 8 ) > SILK_FIX_CONST( 1.0, 7 ) ) {
	add.n	a2, a2, a3	# tmp390, tmp388, psEncCtrl_146(D)->LTPredCodGain_Q7
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:99:         if( psEncCtrl->LTPredCodGain_Q7 + silk_RSHIFT( psEnc->sCmn.input_tilt_Q15, 8 ) > SILK_FIX_CONST( 1.0, 7 ) ) {
	movi	a3, 0x80	# tmp392,
	bge	a3, a2, .L26	# tmp392, tmp390,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:100:             psEnc->sCmn.indices.quantOffsetType = 0;
	s8i	a8, a9, 158	# psEnc_143(D)->sCmn.indices.quantOffsetType, tmp328
	mov.n	a7, a8	# _547, tmp328
	j	.L25		#
.L26:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:102:             psEnc->sCmn.indices.quantOffsetType = 1;
	s8i	a7, a9, 158	# psEnc_143(D)->sCmn.indices.quantOffsetType, tmp327
.L25:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:111:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_INPUT_QUALITY,     12 ), psEncCtrl->input_quality_Q14       )
	l16si	a5, a12, 384	# psEncCtrl_146(D)->input_quality_Q14, _116
	l32r	a3, .LC9	#, tmp405
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:112:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_CODING_QUALITY,    12 ), psEncCtrl->coding_quality_Q14      )
	l16si	a2, a12, 388	# psEncCtrl_146(D)->coding_quality_Q14, _123
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:109:                           + silk_SMULBB( SILK_FIX_CONST( LAMBDA_DELAYED_DECISIONS, 10 ), psEnc->sCmn.nStatesDelayedDecision )
	l32i.n	a8, a9, 20	# psEnc_143(D)->sCmn.nStatesDelayedDecision, psEnc_143(D)->sCmn.nStatesDelayedDecision
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:112:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_CODING_QUALITY,    12 ), psEncCtrl->coding_quality_Q14      )
	l32r	a6, .LC10	#, tmp412
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:110:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_SPEECH_ACT,        18 ), psEnc->sCmn.speech_activity_Q8     )
	l32i.n	a9, sp, 4	# %sfp,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	srai	a4, a4, 25	# tmp429, tmp498,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:111:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_INPUT_QUALITY,     12 ), psEncCtrl->input_quality_Q14       )
	mull	a3, a5, a3	# tmp404, _116, tmp405
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	slli	a4, a4, 1	# tmp431, tmp429,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a5, a5, a2	# tmp407, _116, _123
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	add.n	a4, a4, a7	# tmp432, tmp431, _547
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:112:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_CODING_QUALITY,    12 ), psEncCtrl->coding_quality_Q14      )
	mull	a2, a2, a6	# tmp411, _123, tmp412
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:110:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_SPEECH_ACT,        18 ), psEnc->sCmn.speech_activity_Q8     )
	l16si	a7, a9, 180	# psEnc_143(D)->sCmn.speech_activity_Q8, _108
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	l32r	a6, .LC12	#, tmp425
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	movi	a9, 0x4cd	# tmp408,
	sub	a9, a9, a5	# tmp409, tmp408, tmp407
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	slli	a4, a4, 1	# tmp433, tmp432,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:111:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_INPUT_QUALITY,     12 ), psEncCtrl->input_quality_Q14       )
	srai	a3, a3, 16	# tmp406, tmp404,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	add.n	a4, a6, a4	# tmp434, tmp425, tmp433
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a3, a3, a9	# tmp410, tmp406, tmp409
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:110:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_SPEECH_ACT,        18 ), psEnc->sCmn.speech_activity_Q8     )
	l32r	a5, .LC11	#, tmp422
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:112:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_CODING_QUALITY,    12 ), psEncCtrl->coding_quality_Q14      )
	srai	a2, a2, 16	# tmp413, tmp411,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:109:                           + silk_SMULBB( SILK_FIX_CONST( LAMBDA_DELAYED_DECISIONS, 10 ), psEnc->sCmn.nStatesDelayedDecision )
	movi	a6, -0x32	# tmp417,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:107:     quant_offset_Q10 = silk_Quantization_Offsets_Q10[ psEnc->sCmn.indices.signalType >> 1 ][ psEnc->sCmn.indices.quantOffsetType ];
	l16si	a4, a4, 0	# silk_Quantization_Offsets_Q10, quant_offset_Q10
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a2, a3, a2	# tmp414, tmp410, tmp413
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:109:                           + silk_SMULBB( SILK_FIX_CONST( LAMBDA_DELAYED_DECISIONS, 10 ), psEnc->sCmn.nStatesDelayedDecision )
	mul16s	a6, a6, a8	# tmp418, tmp417, psEnc_143(D)->sCmn.nStatesDelayedDecision
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	l32r	a3, .LC13	#, tmp439
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:110:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_SPEECH_ACT,        18 ), psEnc->sCmn.speech_activity_Q8     )
	mul16s	a5, a7, a5	# tmp421, _108, tmp422
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	mull	a3, a4, a3	# tmp438, quant_offset_Q10, tmp439
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a2, a2, a6	# tmp419, tmp414, tmp418
	sub	a2, a2, a7	# tmp420, tmp419, _108
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:110:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_SPEECH_ACT,        18 ), psEnc->sCmn.speech_activity_Q8     )
	srai	a4, a5, 16	# tmp423, tmp421,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a2, a2, a4	# tmp424, tmp420, tmp423
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	srai	a3, a3, 16	# tmp440, tmp438,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:117: }
	l32i	a0, sp, 76	#,
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:113:                           + silk_SMULWB( SILK_FIX_CONST( LAMBDA_QUANT_OFFSET,      16 ), quant_offset_Q10                   );
	add.n	a2, a2, a3	# tmp441, tmp424, tmp440
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:108:     psEncCtrl->Lambda_Q10 = SILK_FIX_CONST( LAMBDA_OFFSET, 10 )
	s32i	a2, a12, 380	# psEncCtrl_146(D)->Lambda_Q10, tmp441
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:117: }
	l32i	a13, sp, 68	#,
	l32i	a12, sp, 72	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
.L21:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a3, a13, 3	# tmp445, _191,
	add.n	a3, a13, a3	# tmp447, _191, tmp445
	slli	a3, a3, 3	# tmp449, tmp447,
	sub	a13, a3, a13	# tmp451, tmp449, _191
	slli	a3, a13, 2	# tmp453, tmp451,
	sub	a3, a3, a13	# tmp456, tmp453, tmp451
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a2, a2, 1	# tmp442, iftmp$17_180,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a3, a3, 16	# tmp458, tmp456,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a2	# tmp442
	sra	a2, a4	# y, y
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a3, a3, 16	# tmp457, tmp458,
	mull	a3, a3, a2	# tmp459, tmp457, y
	srai	a3, a3, 16	# _267, tmp459,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a2, a2, a3	# y, y, _267
	slli	a2, a2, 8	# _493, y,
	j	.L15		#
.L47:
	l32r	a2, .LC1	#, tmp461
	ssr	a5	# _531
	sra	a4, a2	# _424, tmp461
	mull	a2, a4, a3	# tmp463, _424, _534
	l32r	a3, .LC8	#,
	srai	a2, a2, 16	# tmp464, tmp463,
	add.n	a2, a2, a4	# tmp462, tmp464, _424
	bge	a3, a2, .L27	#, tmp462,
	mov.n	a2, a3	# tmp462,
.L27:
	slli	a2, a2, 16	# _438, tmp462,
.L15:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:85:             psEncCtrl->Gains_Q16[ k ] = silk_LSHIFT_SAT32( gain, 16 );  /* Q16  */
	s32i.n	a2, a14, 0	# MEM[base: _514, offset: 0B], _438
	j	.L22		#
.L16:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a4, a6	# iftmp$17_282, iftmp$2_135
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a5, 0x18	#,
	sub	a3, a5, a4	# r,, iftmp$17_282
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a3	# r
	src	a6, a6, a6	# tmp472, iftmp$2_135
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a6, a6, 0, 7	# tmp473, tmp472,
	slli	a3, a6, 3	# tmp476, tmp473,
	add.n	a3, a6, a3	# tmp478, tmp473, tmp476
	slli	a3, a3, 3	# tmp480, tmp478,
	sub	a6, a3, a6	# tmp482, tmp480, tmp473
	slli	a3, a6, 2	# tmp484, tmp482,
	sub	a3, a3, a6	# tmp487, tmp484, tmp482
	slli	a3, a3, 16	# tmp488, tmp487,
	srai	a5, a4, 1	# _531, iftmp$17_282,
	srai	a3, a3, 16	# _534, tmp488,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	bbci	a4, 0, .L47	# iftmp$17_282,,
	j	.L28		#
.L18:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a13, a13, 0, 7	# _191, gain_squared,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a4, .LC1	#, y
	j	.L21		#
.L11:
# @OPUS@\upstream\silk\fixed\process_gains_FIX.c:74:         gain_squared = silk_ADD_SAT32( ResNrgPart, silk_SMMUL( gain, gain ) );
	add.n	a2, a3, a4	# tmp490, tmp497, tmp6
	mov.n	a6, a4	#,
	mov.n	a13, a4	# ResNrgPart$3_195, ResNrgPart
	bgez	a2, .L48	# tmp490,
	j	.L12		#
	.size	silk_process_gains_FIX, .-silk_process_gains_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
