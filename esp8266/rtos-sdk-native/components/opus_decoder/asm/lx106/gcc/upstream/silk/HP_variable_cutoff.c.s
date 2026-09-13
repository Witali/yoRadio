# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/HP_variable_cutoff.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"HP_variable_cutoff.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\HP_variable_cutoff.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\HP_variable_cutoff.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\HP_variable_cutoff.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\HP_variable_cutoff.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\HP_variable_cutoff.c.s.raw
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
	.section	.text.silk_HP_variable_cutoff,"ax",@progbits
	.literal_position
	.literal .LC0, 3932160
	.literal .LC1, 6554
	.align	4
	.global	silk_HP_variable_cutoff
	.type	silk_HP_variable_cutoff, @function
# Function: silk_HP_variable_cutoff
# Module: upstream/silk/HP_variable_cutoff.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "tuning_parameters.h"
# C context:
# C context: /* High-pass filter with cutoff frequency adaptation based on pitch lag statistics */
# C context: void silk_HP_variable_cutoff(
# C context: silk_encoder_state_Fxx          state_Fxx[]                         /* I/O  Encoder states                              */
# C context: )
# C context: {
# C context: opus_int   quality_Q15;
silk_HP_variable_cutoff:
	addi	sp, sp, -48	#,,
	s32i.n	a13, sp, 36	#,
	s32i.n	a0, sp, 44	#,
	s32i.n	a12, sp, 40	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:48:    if( psEncC1->prevSignalType == TYPE_VOICED ) {
	addmi	a4, a2, 0x1100	# tmp222, state_Fxx,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:42: {
	mov.n	a13, a2	# state_Fxx, state_Fxx
# @OPUS@\upstream\silk\HP_variable_cutoff.c:48:    if( psEncC1->prevSignalType == TYPE_VOICED ) {
	l8ui	a2, a4, 189	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].prevSignalType, tmp142
	bnei	a2, 2, .L1	# tmp142,,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:50:       pitch_freq_Hz_Q16 = silk_DIV32_16( silk_LSHIFT( silk_MUL( psEncC1->fs_kHz, 1000 ), 16 ), psEncC1->prevLag );
	l32i	a5, a4, 224	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].fs_kHz, MEM[(struct silk_encoder_state *)state_Fxx_98(D)].fs_kHz
# @OPUS@\upstream\silk\HP_variable_cutoff.c:50:       pitch_freq_Hz_Q16 = silk_DIV32_16( silk_LSHIFT( silk_MUL( psEncC1->fs_kHz, 1000 ), 16 ), psEncC1->prevLag );
	l32i	a3, a4, 192	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].prevLag,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:50:       pitch_freq_Hz_Q16 = silk_DIV32_16( silk_LSHIFT( silk_MUL( psEncC1->fs_kHz, 1000 ), 16 ), psEncC1->prevLag );
	slli	a2, a5, 5	# tmp148, MEM[(struct silk_encoder_state *)state_Fxx_98(D)].fs_kHz,
	sub	a2, a2, a5	# tmp149, tmp148, MEM[(struct silk_encoder_state *)state_Fxx_98(D)].fs_kHz
	slli	a2, a2, 2	# tmp150, tmp149,
	add.n	a2, a2, a5	# tmp151, tmp150, MEM[(struct silk_encoder_state *)state_Fxx_98(D)].fs_kHz
# @OPUS@\upstream\silk\HP_variable_cutoff.c:50:       pitch_freq_Hz_Q16 = silk_DIV32_16( silk_LSHIFT( silk_MUL( psEncC1->fs_kHz, 1000 ), 16 ), psEncC1->prevLag );
	slli	a2, a2, 19	#, tmp151,
	s32i.n	a4, sp, 4	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\HP_variable_cutoff.c:51:       pitch_freq_log_Q7 = silk_lin2log( pitch_freq_Hz_Q16 ) - ( 16 << 7 );
	call0	silk_lin2log		#
# @OPUS@\upstream\silk\HP_variable_cutoff.c:54:       quality_Q15 = psEncC1->input_quality_bands_Q15[ 0 ];
	addmi	a3, a13, 0x1200	# tmp159, state_Fxx,
	l32i	a14, a3, 88	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].input_quality_bands_Q15, quality_Q15
# @OPUS@\upstream\silk\HP_variable_cutoff.c:55:       pitch_freq_log_Q7 = silk_SMLAWB( pitch_freq_log_Q7, silk_SMULWB( silk_LSHIFT( -quality_Q15, 2 ), quality_Q15 ),
	l32r	a15, .LC0	#, tmp168
	neg	a3, a14	# tmp160, quality_Q15
	slli	a3, a3, 2	# _12, tmp160,
	slli	a14, a14, 16	# tmp161, quality_Q15,
	srai	a14, a14, 16	# _15, tmp161,
	extui	a5, a3, 0, 16	# tmp162, _12,
	mull	a5, a5, a14	# tmp163, tmp162, _15
	srai	a3, a3, 16	# tmp165, _12,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:51:       pitch_freq_log_Q7 = silk_lin2log( pitch_freq_Hz_Q16 ) - ( 16 << 7 );
	addmi	a6, a2, -0x800	# pitch_freq_log_Q7,,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:55:       pitch_freq_log_Q7 = silk_SMLAWB( pitch_freq_log_Q7, silk_SMULWB( silk_LSHIFT( -quality_Q15, 2 ), quality_Q15 ),
	mull	a3, a3, a14	# tmp166, tmp165, _15
	slli	a12, a6, 16	# tmp167, pitch_freq_log_Q7,
	srai	a14, a5, 16	# tmp164, tmp163,
	mov.n	a2, a15	#, tmp168
	add.n	a14, a14, a3	# _20, tmp164, tmp166
	s32i.n	a6, sp, 0	#,
	srai	a12, a12, 16	# _22, tmp167,
	call0	silk_lin2log		#
	sub	a3, a12, a2	# tmp170, _22,
	addmi	a3, a3, 0x800	# tmp172, tmp170,
	slli	a3, a3, 16	# tmp174, tmp172,
	srai	a5, a14, 16	# tmp175, _20,
	srai	a3, a3, 16	# tmp173, tmp174,
	mov.n	a2, a15	#, tmp168
	mull	a15, a3, a5	# _28, tmp173, tmp175
	call0	silk_lin2log		#
	sub	a2, a12, a2	# tmp178, _22,
	addmi	a2, a2, 0x800	# tmp180, tmp178,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:59:       delta_freq_Q7 = pitch_freq_log_Q7 - silk_RSHIFT( psEncC1->variable_HP_smth1_Q15, 8 );
	l32i.n	a5, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, _38
# @OPUS@\upstream\silk\HP_variable_cutoff.c:55:       pitch_freq_log_Q7 = silk_SMLAWB( pitch_freq_log_Q7, silk_SMULWB( silk_LSHIFT( -quality_Q15, 2 ), quality_Q15 ),
	slli	a2, a2, 16	# tmp182, tmp180,
	srai	a2, a2, 16	# tmp181, tmp182,
	extui	a14, a14, 0, 16	# tmp183, _20,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:59:       delta_freq_Q7 = pitch_freq_log_Q7 - silk_RSHIFT( psEncC1->variable_HP_smth1_Q15, 8 );
	l32i.n	a6, sp, 0	#,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:55:       pitch_freq_log_Q7 = silk_SMLAWB( pitch_freq_log_Q7, silk_SMULWB( silk_LSHIFT( -quality_Q15, 2 ), quality_Q15 ),
	mull	a2, a2, a14	# tmp184, tmp181, tmp183
# @OPUS@\upstream\silk\HP_variable_cutoff.c:59:       delta_freq_Q7 = pitch_freq_log_Q7 - silk_RSHIFT( psEncC1->variable_HP_smth1_Q15, 8 );
	srai	a3, a5, 8	# tmp186, _38,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:59:       delta_freq_Q7 = pitch_freq_log_Q7 - silk_RSHIFT( psEncC1->variable_HP_smth1_Q15, 8 );
	sub	a6, a6, a3	# tmp187, pitch_freq_log_Q7, tmp186
# @OPUS@\upstream\silk\HP_variable_cutoff.c:55:       pitch_freq_log_Q7 = silk_SMLAWB( pitch_freq_log_Q7, silk_SMULWB( silk_LSHIFT( -quality_Q15, 2 ), quality_Q15 ),
	srai	a2, a2, 16	# tmp185, tmp184,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:59:       delta_freq_Q7 = pitch_freq_log_Q7 - silk_RSHIFT( psEncC1->variable_HP_smth1_Q15, 8 );
	add.n	a15, a6, a15	# tmp188, tmp187, _28
	add.n	a2, a2, a15	# delta_freq_Q7, tmp185, tmp188
# @OPUS@\upstream\silk\HP_variable_cutoff.c:60:       if( delta_freq_Q7 < 0 ) {
	l32i.n	a4, sp, 4	#,
	bgez	a2, .L3	# delta_freq_Q7,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:62:          delta_freq_Q7 = silk_MUL( delta_freq_Q7, 3 );
	slli	a3, a2, 1	# tmp190, delta_freq_Q7,
	add.n	a2, a3, a2	# delta_freq_Q7, tmp190, delta_freq_Q7
.L3:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:66:       delta_freq_Q7 = silk_LIMIT_32( delta_freq_Q7, -SILK_FIX_CONST( VARIABLE_HP_MAX_DELTA_FREQ, 7 ), SILK_FIX_CONST( VARIABLE_HP_MAX_DELTA_FREQ, 7 ) );
	movi	a3, -0x33	# tmp197,
	bge	a2, a3, .L4	# delta_freq_Q7, tmp197,
	mov.n	a2, a3	# delta_freq_Q7, tmp197
.L4:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:69:       psEncC1->variable_HP_smth1_Q15 = silk_SMLAWB( psEncC1->variable_HP_smth1_Q15,
	movi.n	a3, 0x33	# tmp202,
	bge	a3, a2, .L5	# tmp202, delta_freq_Q7,
	mov.n	a2, a3	# delta_freq_Q7, tmp202
.L5:
	l16si	a3, a4, 180	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].speech_activity_Q8, tmp205
	l32r	a6, .LC1	#, tmp209
	mull	a3, a2, a3	# _45, delta_freq_Q7, tmp205
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi.n	a2, 0x3c	#,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:69:       psEncC1->variable_HP_smth1_Q15 = silk_SMLAWB( psEncC1->variable_HP_smth1_Q15,
	extui	a4, a3, 0, 16	# tmp207, _45,
	srai	a3, a3, 16	# tmp211, _45,
	mull	a4, a4, a6	# tmp208, tmp207, tmp209
	mull	a3, a3, a6	# tmp212, tmp211, tmp209
	srai	a4, a4, 16	# tmp210, tmp208,
	add.n	a3, a3, a5	# tmp214, tmp212, _38
	add.n	a3, a4, a3	# tmp215, tmp210, tmp214
# @OPUS@\upstream\silk\HP_variable_cutoff.c:69:       psEncC1->variable_HP_smth1_Q15 = silk_SMLAWB( psEncC1->variable_HP_smth1_Q15,
	s32i.n	a3, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, tmp215
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	call0	silk_lin2log		#
	mov.n	a12, a2	# _53,
	movi	a2, 0x64	#,
	call0	silk_lin2log		#
	slli	a2, a2, 8	# tmp217,,
	slli	a12, a12, 8	# tmp216, _53,
	bge	a2, a12, .L6	# tmp217, tmp216,
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi.n	a2, 0x3c	#,
	l32i.n	a12, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, _61
	call0	silk_lin2log		#
	slli	a2, a2, 8	# tmp218,,
	bge	a2, a12, .L7	# tmp218, _61,
	j	.L13		#
.L7:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi	a2, 0x64	#,
	l32i.n	a12, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, _69
	call0	silk_lin2log		#
	slli	a2, a2, 8	# tmp219,,
	bge	a12, a2, .L11	# _69, tmp219,
	j	.L12		#
.L6:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi	a2, 0x64	#,
	l32i.n	a12, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, _77
	call0	silk_lin2log		#
	slli	a2, a2, 8	# tmp220,,
	bge	a2, a12, .L10	# tmp220, _77,
.L12:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi	a2, 0x64	#,
	call0	silk_lin2log		#
	slli	a2, a2, 8	# iftmp$1_95,,
	j	.L8		#
.L10:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi.n	a2, 0x3c	#,
	l32i.n	a12, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, _85
	call0	silk_lin2log		#
	slli	a2, a2, 8	# tmp221,,
	bge	a12, a2, .L11	# _85, tmp221,
.L13:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	movi.n	a2, 0x3c	#,
	call0	silk_lin2log		#
	slli	a2, a2, 8	# iftmp$1_95,,
	j	.L8		#
.L11:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	l32i.n	a2, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, iftmp$1_95
.L8:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:73:       psEncC1->variable_HP_smth1_Q15 = silk_LIMIT_32( psEncC1->variable_HP_smth1_Q15,
	s32i.n	a2, a13, 8	# MEM[(struct silk_encoder_state *)state_Fxx_98(D)].variable_HP_smth1_Q15, iftmp$1_95
.L1:
# @OPUS@\upstream\silk\HP_variable_cutoff.c:77: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_HP_variable_cutoff, .-silk_HP_variable_cutoff
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
