# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/LTP_scale_ctrl_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"LTP_scale_ctrl_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_scale_ctrl_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_scale_ctrl_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_scale_ctrl_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\LTP_scale_ctrl_FIX.c.s.raw
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
	.section	.text.silk_LTP_scale_ctrl_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 3796
	.literal .LC1, 4796
	.literal .LC2, silk_LTPScales_table_Q14
	.align	4
	.global	silk_LTP_scale_ctrl_FIX
	.type	silk_LTP_scale_ctrl_FIX, @function
# Function: silk_LTP_scale_ctrl_FIX
# Module: upstream/silk/fixed/LTP_scale_ctrl_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main_FIX.h"
# C context:
# C context: /* Calculation of LTP state scaling */
# C context: void silk_LTP_scale_ctrl_FIX(
# C context: silk_encoder_state_FIX          *psEnc,                                 /* I/O  encoder state                                                               */
# C context: silk_encoder_control_FIX        *psEncCtrl,                             /* I/O  encoder control                                                             */
# C context: opus_int                        condCoding                              /* I    The type of conditional coding to use                                       */
# C context: )
silk_LTP_scale_ctrl_FIX:
	addi	sp, sp, -32	#,,
	s32i.n	a13, sp, 20	#,
	s32i.n	a0, sp, 28	#,
	s32i.n	a12, sp, 24	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:40: {
	mov.n	a13, a3	# psEncCtrl, psEncCtrl
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:43:     if( condCoding == CODE_INDEPENDENTLY ) {
	bnez.n	a4, .L2	# condCoding,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:45:         round_loss = psEnc->sCmn.PacketLoss_perc * psEnc->sCmn.nFramesPerPacket;
	addmi	a14, a2, 0x1200	# tmp127, psEnc,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:45:         round_loss = psEnc->sCmn.PacketLoss_perc * psEnc->sCmn.nFramesPerPacket;
	addmi	a2, a2, 0x1600	# tmp79, psEnc,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:45:         round_loss = psEnc->sCmn.PacketLoss_perc * psEnc->sCmn.nFramesPerPacket;
	l32i	a3, a2, 112	# psEnc_38(D)->sCmn.nFramesPerPacket, psEnc_38(D)->sCmn.nFramesPerPacket
	l32i.n	a12, a14, 8	# psEnc_38(D)->sCmn.PacketLoss_perc, psEnc_38(D)->sCmn.PacketLoss_perc
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:46:         if ( psEnc->sCmn.LBRR_flag ) {
	l8ui	a2, a14, 115	# psEnc_38(D)->sCmn.LBRR_flag, tmp87
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:45:         round_loss = psEnc->sCmn.PacketLoss_perc * psEnc->sCmn.nFramesPerPacket;
	mull	a12, a12, a3	# round_loss, psEnc_38(D)->sCmn.PacketLoss_perc, psEnc_38(D)->sCmn.nFramesPerPacket
	slli	a12, a12, 16	# tmp83, round_loss,
	srai	a12, a12, 16	# _61, tmp83,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:46:         if ( psEnc->sCmn.LBRR_flag ) {
	beqz.n	a2, .L3	# tmp87,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:49:             round_loss = 2 + silk_SMULBB( round_loss, round_loss ) / 100;
	mull	a2, a12, a12	#, _61, _61
	movi	a3, 0x64	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:49:             round_loss = 2 + silk_SMULBB( round_loss, round_loss ) / 100;
	addi.n	a12, a2, 2	# round_loss,,
	slli	a12, a12, 16	# tmp94, round_loss,
	srai	a12, a12, 16	# _61, tmp94,
.L3:
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	l32r	a3, .LC0	#, tmp100
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	l16si	a15, a13, 396	# psEncCtrl_41(D)->LTPredCodGain_Q7, tmp96
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	l32i	a2, a14, 108	# psEnc_38(D)->sCmn.SNR_dB_Q7, psEnc_38(D)->sCmn.SNR_dB_Q7
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	mull	a15, a15, a12	# _13, tmp96, _61
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	sub	a2, a3, a2	#, tmp100, psEnc_38(D)->sCmn.SNR_dB_Q7
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	movi.n	a3, 1	# tmp104,
	blt	a2, a15, .L4	#, _13,
	movi.n	a3, 0	# tmp104,
.L4:
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:51:         psEnc->sCmn.indices.LTP_scaleIndex = silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 2900-psEnc->sCmn.SNR_dB_Q7 );
	s8i	a3, a14, 161	# psEnc_38(D)->sCmn.indices.LTP_scaleIndex, tmp104
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	l16si	a3, a13, 396	# psEncCtrl_41(D)->LTPredCodGain_Q7, tmp106
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	l32i	a2, a14, 108	# psEnc_38(D)->sCmn.SNR_dB_Q7, psEnc_38(D)->sCmn.SNR_dB_Q7
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	mull	a12, a3, a12	# _22, tmp106, _61
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	l32r	a3, .LC1	#, tmp110
	sub	a2, a3, a2	#, tmp110, psEnc_38(D)->sCmn.SNR_dB_Q7
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	movi.n	a4, 1	# tmp113,
	blt	a2, a12, .L5	#, _22,
	movi.n	a4, 0	# tmp113,
.L5:
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:52:         psEnc->sCmn.indices.LTP_scaleIndex += silk_SMULBB( psEncCtrl->LTPredCodGain_Q7, round_loss ) > silk_log2lin( 128*7 + 3900-psEnc->sCmn.SNR_dB_Q7 );
	l8ui	a3, a14, 161	# psEnc_38(D)->sCmn.indices.LTP_scaleIndex,
	add.n	a3, a3, a4	# tmp116, psEnc_38(D)->sCmn.indices.LTP_scaleIndex, tmp113
	extui	a3, a3, 0, 8	# _29, tmp116
	slli	a2, a3, 24	# tmp118, _29,
	s8i	a3, a14, 161	# psEnc_38(D)->sCmn.indices.LTP_scaleIndex, _29
	srai	a2, a2, 24	# _58, tmp118,
	j	.L6		#
.L2:
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:55:         psEnc->sCmn.indices.LTP_scaleIndex = 0;
	addmi	a2, a2, 0x1200	# tmp119, psEnc,
	movi.n	a3, 0	# tmp120,
	s8i	a3, a2, 161	# psEnc_38(D)->sCmn.indices.LTP_scaleIndex, tmp120
	movi.n	a2, 0	# _58,
.L6:
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:57:     psEncCtrl->LTP_scale_Q14 = silk_LTPScales_table_Q14[ psEnc->sCmn.indices.LTP_scaleIndex ];
	l32r	a3, .LC2	#, tmp121
	slli	a2, a2, 1	# tmp122, _58,
	add.n	a2, a3, a2	# tmp123, tmp121, tmp122
	l16si	a2, a2, 0	# silk_LTPScales_table_Q14, tmp124
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:58: }
	l32i.n	a0, sp, 28	#,
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:57:     psEncCtrl->LTP_scale_Q14 = silk_LTPScales_table_Q14[ psEnc->sCmn.indices.LTP_scaleIndex ];
	s32i	a2, a13, 120	# psEncCtrl_41(D)->LTP_scale_Q14, tmp124
# @OPUS@\upstream\silk\fixed\LTP_scale_ctrl_FIX.c:58: }
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_LTP_scale_ctrl_FIX, .-silk_LTP_scale_ctrl_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
