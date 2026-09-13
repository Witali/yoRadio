# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_pitch.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_pitch.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_pitch.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_pitch.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_pitch.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_pitch.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_pitch.c.s.raw
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
	.section	.text.silk_decode_pitch,"ax",@progbits
	.literal_position
	.literal .LC0, silk_CB_lags_stage3_10_ms
	.literal .LC1, silk_CB_lags_stage2_10_ms
	.literal .LC2, silk_CB_lags_stage2
	.literal .LC3, silk_CB_lags_stage3
	.align	4
	.global	silk_decode_pitch
	.type	silk_decode_pitch, @function
# Function: silk_decode_pitch
# Module: upstream/silk/decode_pitch.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "SigProc_FIX.h"
# C context: #include "pitch_est_defines.h"
# C context:
# C context: void silk_decode_pitch(
# C context: opus_int16                  lagIndex,           /* I                                                                */
# C context: opus_int8                   contourIndex,       /* O                                                                */
# C context: opus_int                    pitch_lags[],       /* O    4 pitch values                                              */
# C context: const opus_int              Fs_kHz,             /* I    sampling frequency (kHz)                                    */
silk_decode_pitch:
# @OPUS@\upstream\silk\decode_pitch.c:45: {
	slli	a2, a2, 16	# tmp80, lagIndex,
	srai	a2, a2, 16	# lagIndex, tmp80,
	extui	a3, a3, 0, 8	# contourIndex, contourIndex
# @OPUS@\upstream\silk\decode_pitch.c:49:     if( Fs_kHz == 8 ) {
	bnei	a5, 8, .L2	# Fs_kHz,,
# @OPUS@\upstream\silk\decode_pitch.c:50:         if( nb_subfr == PE_MAX_NB_SUBFR ) {
	bnei	a6, 4, .L22	# nb_subfr,,
	j	.L18		#
.L2:
# @OPUS@\upstream\silk\decode_pitch.c:59:         if( nb_subfr == PE_MAX_NB_SUBFR ) {
	beqi	a6, 4, .L19	# nb_subfr,,
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	slli	a5, a5, 16	# tmp86, Fs_kHz,
	srai	a5, a5, 16	# _1, tmp86,
# @OPUS@\upstream\silk\decode_pitch.c:70:     max_lag = silk_SMULBB( PE_MAX_LAG_MS, Fs_kHz );
	slli	a7, a5, 3	# tmp88, _1,
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	slli	a8, a5, 1	# min_lag, _1,
# @OPUS@\upstream\silk\decode_pitch.c:70:     max_lag = silk_SMULBB( PE_MAX_LAG_MS, Fs_kHz );
	add.n	a5, a7, a5	# tmp89, tmp88, _1
	slli	a5, a5, 1	# max_lag, tmp89,
# @OPUS@\upstream\silk\decode_pitch.c:71:     lag = min_lag + lagIndex;
	add.n	a7, a2, a8	# lag, lagIndex, min_lag
# @OPUS@\upstream\silk\decode_pitch.c:64:             Lag_CB_ptr = &silk_CB_lags_stage3_10_ms[ 0 ][ 0 ];
	l32r	a10, .LC0	#, Lag_CB_ptr
# @OPUS@\upstream\silk\decode_pitch.c:65:             cbk_size   = PE_NB_CBKS_STAGE3_10MS;
	movi.n	a9, 0xc	# cbk_size,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a6, 1, .L1	# nb_subfr,,
.L5:
	blt	a5, a8, .L6	# max_lag, min_lag,
	j	.L17		#
.L21:
# @OPUS@\upstream\silk\decode_pitch.c:55:             Lag_CB_ptr = &silk_CB_lags_stage2_10_ms[ 0 ][ 0 ];
	l32r	a10, .LC1	#, Lag_CB_ptr
# @OPUS@\upstream\silk\decode_pitch.c:56:             cbk_size   = PE_NB_CBKS_STAGE2_10MS;
	movi.n	a9, 3	# cbk_size,
# @OPUS@\upstream\silk\decode_pitch.c:70:     max_lag = silk_SMULBB( PE_MAX_LAG_MS, Fs_kHz );
	movi	a5, 0x90	# max_lag,
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	movi.n	a8, 0x10	# min_lag,
.L17:
	slli	a3, a3, 24	# tmp92, contourIndex,
	srai	a3, a3, 24	# tmp91, tmp92,
	add.n	a3, a10, a3	# ivtmp$11, Lag_CB_ptr, tmp91
	movi.n	a10, 0	# k,
.L11:
# @OPUS@\upstream\silk\decode_pitch.c:74:         pitch_lags[ k ] = lag + matrix_ptr( Lag_CB_ptr, k, contourIndex, cbk_size );
	l8ui	a2, a3, 0	# MEM[base: _10, offset: 0B],
	slli	a2, a2, 24	# tmp95, MEM[base: _10, offset: 0B],
	srai	a2, a2, 24	# tmp93, tmp95,
# @OPUS@\upstream\silk\decode_pitch.c:74:         pitch_lags[ k ] = lag + matrix_ptr( Lag_CB_ptr, k, contourIndex, cbk_size );
	add.n	a2, a2, a7	# _50, tmp93, lag
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	mov.n	a11, a2	# _50, _50
	blt	a5, a2, .L7	# max_lag, _50,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a10, a10, 1	# k, k,
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	bge	a2, a8, .L8	# _50, min_lag,
	mov.n	a11, a8	# _50, min_lag
.L8:
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	s32i.n	a11, a4, 0	# MEM[base: _76, offset: 0B], _50
	add.n	a3, a3, a9	# ivtmp$11, ivtmp$11, cbk_size
	addi.n	a4, a4, 4	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	blt	a10, a6, .L11	# k, nb_subfr,
	j	.L1		#
.L7:
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	s32i.n	a5, a4, 0	# MEM[base: _11, offset: 0B], max_lag
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a10, a10, 1	# k, k,
	add.n	a3, a3, a9	# ivtmp$11, ivtmp$11, cbk_size
	addi.n	a4, a4, 4	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	blt	a10, a6, .L11	# k, nb_subfr,
	j	.L1		#
.L6:
	slli	a3, a3, 24	# tmp98, contourIndex,
	srai	a3, a3, 24	# tmp97, tmp98,
	add.n	a3, a10, a3	# ivtmp$16, Lag_CB_ptr, tmp97
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	movi.n	a10, 0	# k,
.L12:
# @OPUS@\upstream\silk\decode_pitch.c:74:         pitch_lags[ k ] = lag + matrix_ptr( Lag_CB_ptr, k, contourIndex, cbk_size );
	l8ui	a2, a3, 0	# MEM[base: _83, offset: 0B],
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	mov.n	a11, a5	# max_lag, max_lag
# @OPUS@\upstream\silk\decode_pitch.c:74:         pitch_lags[ k ] = lag + matrix_ptr( Lag_CB_ptr, k, contourIndex, cbk_size );
	slli	a2, a2, 24	# tmp101, MEM[base: _83, offset: 0B],
	srai	a2, a2, 24	# tmp99, tmp101,
# @OPUS@\upstream\silk\decode_pitch.c:74:         pitch_lags[ k ] = lag + matrix_ptr( Lag_CB_ptr, k, contourIndex, cbk_size );
	add.n	a2, a2, a7	# _92, tmp99, lag
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	blt	a8, a2, .L14	# min_lag, _92,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a10, a10, 1	# k, k,
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	bge	a5, a2, .L15	# max_lag, _92,
	mov.n	a11, a2	# max_lag, _92
.L15:
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	s32i.n	a11, a4, 0	# MEM[base: _59, offset: 0B], max_lag
	add.n	a3, a3, a9	# ivtmp$16, ivtmp$16, cbk_size
	addi.n	a4, a4, 4	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	blt	a10, a6, .L12	# k, nb_subfr,
	j	.L1		#
.L14:
# @OPUS@\upstream\silk\decode_pitch.c:75:         pitch_lags[ k ] = silk_LIMIT( pitch_lags[ k ], min_lag, max_lag );
	s32i.n	a8, a4, 0	# MEM[base: _75, offset: 0B], min_lag
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a10, a10, 1	# k, k,
	add.n	a3, a3, a9	# ivtmp$16, ivtmp$16, cbk_size
	addi.n	a4, a4, 4	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	blt	a10, a6, .L12	# k, nb_subfr,
	j	.L1		#
.L18:
# @OPUS@\upstream\silk\decode_pitch.c:51:             Lag_CB_ptr = &silk_CB_lags_stage2[ 0 ][ 0 ];
	l32r	a10, .LC2	#, Lag_CB_ptr
# @OPUS@\upstream\silk\decode_pitch.c:52:             cbk_size   = PE_NB_CBKS_STAGE2_EXT;
	movi.n	a9, 0xb	# cbk_size,
	j	.L3		#
.L19:
# @OPUS@\upstream\silk\decode_pitch.c:60:             Lag_CB_ptr = &silk_CB_lags_stage3[ 0 ][ 0 ];
	l32r	a10, .LC3	#, Lag_CB_ptr
# @OPUS@\upstream\silk\decode_pitch.c:61:             cbk_size   = PE_NB_CBKS_STAGE3_MAX;
	movi.n	a9, 0x22	# cbk_size,
.L3:
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	slli	a5, a5, 16	# tmp103, Fs_kHz,
	srai	a5, a5, 16	# _34, tmp103,
# @OPUS@\upstream\silk\decode_pitch.c:70:     max_lag = silk_SMULBB( PE_MAX_LAG_MS, Fs_kHz );
	slli	a7, a5, 3	# tmp105, _34,
# @OPUS@\upstream\silk\decode_pitch.c:69:     min_lag = silk_SMULBB( PE_MIN_LAG_MS, Fs_kHz );
	slli	a8, a5, 1	# min_lag, _34,
# @OPUS@\upstream\silk\decode_pitch.c:70:     max_lag = silk_SMULBB( PE_MAX_LAG_MS, Fs_kHz );
	add.n	a5, a7, a5	# tmp106, tmp105, _34
	slli	a5, a5, 1	# max_lag, tmp106,
# @OPUS@\upstream\silk\decode_pitch.c:71:     lag = min_lag + lagIndex;
	add.n	a7, a2, a8	# lag, lagIndex, min_lag
	j	.L5		#
.L22:
	addi	a7, a2, 16	# lag, lagIndex,
# @OPUS@\upstream\silk\decode_pitch.c:73:     for( k = 0; k < nb_subfr; k++ ) {
	bgei	a6, 1, .L21	# nb_subfr,,
.L1:
# @OPUS@\upstream\silk\decode_pitch.c:77: }
	ret.n
	.size	silk_decode_pitch, .-silk_decode_pitch
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
