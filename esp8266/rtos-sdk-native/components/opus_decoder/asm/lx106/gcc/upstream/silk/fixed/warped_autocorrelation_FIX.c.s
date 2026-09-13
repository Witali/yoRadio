# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/warped_autocorrelation_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"warped_autocorrelation_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\warped_autocorrelation_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\warped_autocorrelation_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\warped_autocorrelation_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\warped_autocorrelation_FIX.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_warped_autocorrelation_FIX_c,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_warped_autocorrelation_FIX_c
	.type	silk_warped_autocorrelation_FIX_c, @function
# Function: silk_warped_autocorrelation_FIX_c
# Module: upstream/silk/fixed/warped_autocorrelation_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Autocorrelations for a warped frequency axis */
# C context: #ifndef OVERRIDE_silk_warped_autocorrelation_FIX_c
# C context: void silk_warped_autocorrelation_FIX_c(
# C context: opus_int32                *corr,                                  /* O    Result [order + 1]                                                          */
# C context: opus_int                  *scale,                                 /* O    Scaling of the correlation vector                                           */
# C context: const opus_int16                *input,                                 /* I    Input data to correlate                                                     */
# C context: const opus_int                  warping_Q16,                            /* I    Warping coefficient                                                         */
silk_warped_autocorrelation_FIX_c:
	movi	a9, 0x180	#,
	sub	sp, sp, a9	#,,
	s32i	a12, sp, 376	#,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:52:     opus_int32 state_QS[ MAX_SHAPE_LPC_ORDER + 1 ] = { 0 };
	movi	a12, 0xc8	# tmp145,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:49: {
	s32i	a15, sp, 364	#,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:52:     opus_int32 state_QS[ MAX_SHAPE_LPC_ORDER + 1 ] = { 0 };
	add.n	a15, sp, a12	# tmp146,, tmp145
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:49: {
	s32i	a13, sp, 372	#,
	s32i	a2, sp, 340	# %sfp, corr
	s32i	a3, sp, 336	# %sfp, scale
	mov.n	a13, a4	# input, input
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:52:     opus_int32 state_QS[ MAX_SHAPE_LPC_ORDER + 1 ] = { 0 };
	movi.n	a3, 0	#,
	movi	a4, 0x64	#,
	mov.n	a2, a15	#, tmp146
	s32i	a6, sp, 348	#,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:49: {
	s32i	a0, sp, 380	#,
	s32i	a14, sp, 368	#,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:49: {
	s32i	a7, sp, 312	# %sfp, order
	mov.n	a14, a5	# warping_Q16, warping_Q16
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:52:     opus_int32 state_QS[ MAX_SHAPE_LPC_ORDER + 1 ] = { 0 };
	call0	memset		#
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:53:     opus_int64 corr_QC[  MAX_SHAPE_LPC_ORDER + 1 ] = { 0 };
	mov.n	a4, a12	#, tmp145
	movi.n	a3, 0	#,
	mov.n	a2, sp	#,
	call0	memset		#
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:60:     for( n = 0; n < length; n++ ) {
	l32i	a6, sp, 348	#,
	blti	a6, 1, .L2	# length,,
	l32i	a8, sp, 312	# %sfp,
	slli	a3, a14, 16	# tmp374, warping_Q16,
	addi.n	a2, a8, -1	# tmp154,,
	srli	a2, a2, 1	# tmp155, tmp154,
	slli	a8, a8, 2	#,,
	s32i	a8, sp, 332	# %sfp,
	slli	a2, a2, 4	# tmp156, tmp155,
	addi	a8, sp, 16	#,,
	add.n	a8, a2, a8	#, tmp156,
	s32i	a8, sp, 304	# %sfp,
	l32i	a8, sp, 312	# %sfp,
	slli	a6, a6, 1	# tmp153, length,
	slli	a8, a8, 3	#,,
	s32i	a8, sp, 324	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:73:         state_QS[ order ] = tmp1_QS;
	l32i	a8, sp, 332	# %sfp,
	add.n	a6, a13, a6	#, input, tmp153
	srai	a3, a3, 16	#, tmp374,
	add.n	a8, a15, a8	#, tmp377,
	s32i	a13, sp, 308	# %sfp, input
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a14, a15	# tmp377, tmp146
	s32i	a6, sp, 316	# %sfp,
	s32i	a3, sp, 328	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:73:         state_QS[ order ] = tmp1_QS;
	s32i	a8, sp, 320	# %sfp,
.L8:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:61:         tmp1_QS = silk_LSHIFT32( (opus_int32)input[ n ], QS );
	l32i	a8, sp, 308	# %sfp,
	l16si	a6, a8, 0	# MEM[base: _156, offset: 0B], tmp158
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:63:         for( i = 0; i < order; i += 2 ) {
	l32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:61:         tmp1_QS = silk_LSHIFT32( (opus_int32)input[ n ], QS );
	slli	a6, a6, 13	# tmp1_QS, tmp158,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:63:         for( i = 0; i < order; i += 2 ) {
	blti	a8, 1, .L3	#,,
	l32i	a12, sp, 200	# MEM[(int *)&state_QS], state_QS_I_lsm0$7
	movi	a2, 0xc8	#,
	add.n	a13, sp, a2	# ivtmp$20,,
	mov.n	a10, a12	# state_QS_I_lsm0$7, state_QS_I_lsm0$7
	mov.n	a12, a13	# ivtmp$20, ivtmp$20
	l32i	a13, sp, 328	# %sfp, _199
	mov.n	a15, sp	# ivtmp$21,
.L6:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:65:             tmp2_QS = silk_SMLAWB( state_QS[ i ], state_QS[ i + 1 ] - tmp1_QS, warping_Q16 );
	l32i.n	a11, a12, 4	# MEM[base: _172, offset: 4B], _9
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:66:             state_QS[ i ]  = tmp1_QS;
	s32i.n	a6, a12, 0	# MEM[base: _172, offset: 0B], tmp1_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:65:             tmp2_QS = silk_SMLAWB( state_QS[ i ], state_QS[ i + 1 ] - tmp1_QS, warping_Q16 );
	sub	a2, a11, a6	# _10, _9, tmp1_QS
	extui	a8, a2, 0, 16	# tmp163, _10,
	srai	a2, a2, 16	# tmp166, _10,
	mull	a8, a8, a13	# tmp164, tmp163, _199
	mull	a7, a2, a13	# tmp167, tmp166, _199
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a3, a14, 0	# state_QS, state_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:65:             tmp2_QS = silk_SMLAWB( state_QS[ i ], state_QS[ i + 1 ] - tmp1_QS, warping_Q16 );
	add.n	a10, a7, a10	# tmp168, tmp167, state_QS_I_lsm0$7
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:65:             tmp2_QS = silk_SMLAWB( state_QS[ i ], state_QS[ i + 1 ] - tmp1_QS, warping_Q16 );
	srai	a7, a8, 16	# tmp165, tmp164,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a4, a6	#, tmp1_QS
	srai	a5, a6, 31	#, tmp1_QS,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:65:             tmp2_QS = silk_SMLAWB( state_QS[ i ], state_QS[ i + 1 ] - tmp1_QS, warping_Q16 );
	add.n	a7, a7, a10	# tmp2_QS, tmp165, tmp168
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a2, a3	#, state_QS
	srai	a3, a3, 31	#, state_QS,
	s32i	a7, sp, 348	#,
	s32i	a11, sp, 344	#,
	call0	__muldi3		#
	slli	a8, a3, 16	# tmp179, tmp280,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a6, a15, 0	# MEM[base: _169, offset: 0B], MEM[base: _169, offset: 0B]
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	extui	a2, a2, 16, 16	# tmp281,,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i	a7, sp, 348	#,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	or	a2, a8, a2	# tmp281, tmp179, tmp281
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a9, a15, 4	# MEM[base: _169, offset: 0B], tmp284
	add.n	a8, a6, a2	# tmp285, MEM[base: _169, offset: 0B], tmp281
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	srai	a3, a3, 16	# tmp282, tmp280,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	add.n	a2, a9, a3	# tmp286, tmp284, tmp282
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a4, a7	#, tmp2_QS
	srai	a5, a7, 31	#, tmp2_QS,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	movi.n	a9, 1	# tmp182,
	l32i	a11, sp, 344	#,
	bltu	a8, a6, .L4	# tmp285, MEM[base: _169, offset: 0B],
	movi.n	a9, 0	# tmp182,
.L4:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:69:             tmp1_QS = silk_SMLAWB( state_QS[ i + 1 ], state_QS[ i + 2 ] - tmp2_QS, warping_Q16 );
	l32i.n	a10, a12, 8	# MEM[base: _172, offset: 8B], state_QS_I_lsm0$7
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:70:             state_QS[ i + 1 ]  = tmp2_QS;
	s32i.n	a7, a12, 4	# MEM[base: _172, offset: 4B], tmp2_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:69:             tmp1_QS = silk_SMLAWB( state_QS[ i + 1 ], state_QS[ i + 2 ] - tmp2_QS, warping_Q16 );
	sub	a7, a10, a7	# _30, state_QS_I_lsm0$7, tmp2_QS
	extui	a6, a7, 0, 16	# tmp185, _30,
	srai	a7, a7, 16	# tmp188, _30,
	mull	a6, a6, a13	# tmp186, tmp185, _199
	mull	a7, a7, a13	# tmp189, tmp188, _199
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a3, a14, 0	# state_QS, state_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	add.n	a9, a9, a2	# tmp184, tmp182, tmp286
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:69:             tmp1_QS = silk_SMLAWB( state_QS[ i + 1 ], state_QS[ i + 2 ] - tmp2_QS, warping_Q16 );
	add.n	a7, a7, a11	# tmp190, tmp189, _9
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:69:             tmp1_QS = silk_SMLAWB( state_QS[ i + 1 ], state_QS[ i + 2 ] - tmp2_QS, warping_Q16 );
	srai	a6, a6, 16	# tmp187, tmp186,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:69:             tmp1_QS = silk_SMLAWB( state_QS[ i + 1 ], state_QS[ i + 2 ] - tmp2_QS, warping_Q16 );
	add.n	a6, a6, a7	# tmp1_QS, tmp187, tmp190
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:67:             corr_QC[  i ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	s32i.n	a8, a15, 0	# MEM[base: _169, offset: 0B], tmp285
	s32i.n	a9, a15, 4	# MEM[base: _169, offset: 0B], tmp184
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a2, a3	#, state_QS
	srai	a3, a3, 31	#, state_QS,
	s32i	a6, sp, 348	#,
	s32i	a10, sp, 344	#,
	call0	__muldi3		#
	slli	a4, a3, 16	# tmp201, tmp292,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a7, a15, 8	# MEM[base: _169, offset: 8B], MEM[base: _169, offset: 8B]
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	extui	a2, a2, 16, 16	# tmp293,,
	or	a2, a4, a2	# tmp293, tmp201, tmp293
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a5, a15, 12	# MEM[base: _169, offset: 8B], tmp296
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	srai	a3, a3, 16	# tmp294, tmp292,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	add.n	a2, a7, a2	# tmp297, MEM[base: _169, offset: 8B], tmp293
	movi.n	a4, 1	# tmp204,
	add.n	a3, a5, a3	# tmp298, tmp296, tmp294
	l32i	a6, sp, 348	#,
	l32i	a10, sp, 344	#,
	bltu	a2, a7, .L5	# tmp297, MEM[base: _169, offset: 8B],
	movi.n	a4, 0	# tmp204,
.L5:
	add.n	a4, a4, a3	# tmp206, tmp204, tmp298
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:63:         for( i = 0; i < order; i += 2 ) {
	l32i	a8, sp, 304	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:71:             corr_QC[  i + 1 ] += silk_RSHIFT64( silk_SMULL( tmp2_QS, state_QS[ 0 ] ), 2 * QS - QC );
	s32i.n	a2, a15, 8	# MEM[base: _169, offset: 8B], tmp297
	s32i.n	a4, a15, 12	# MEM[base: _169, offset: 8B], tmp206
	addi	a15, a15, 16	# ivtmp$21, ivtmp$21,
	addi.n	a12, a12, 8	# ivtmp$20, ivtmp$20,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:63:         for( i = 0; i < order; i += 2 ) {
	bne	a8, a15, .L6	#, ivtmp$21,
.L3:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:73:         state_QS[ order ] = tmp1_QS;
	l32i	a8, sp, 320	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	mov.n	a4, a6	#, tmp1_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:73:         state_QS[ order ] = tmp1_QS;
	s32i.n	a6, a8, 0	# state_QS, tmp1_QS
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a3, a14, 0	# state_QS, state_QS
	srai	a5, a6, 31	#, tmp1_QS,
	mov.n	a2, a3	#, state_QS
	srai	a3, a3, 31	#, state_QS,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i	a8, sp, 324	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	slli	a6, a3, 16	# tmp224, tmp304,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	add.n	a4, sp, a8	# tmp213,,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	extui	a2, a2, 16, 16	# tmp305,,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a5, a4, 0	# corr_QC, tmp307
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	or	a2, a6, a2	# tmp305, tmp224, tmp305
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	add.n	a5, a2, a5	# tmp309, tmp305, tmp307
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	srai	a3, a3, 16	# tmp306, tmp304,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	l32i.n	a7, a4, 4	# corr_QC, tmp308
	movi.n	a6, 1	# tmp229,
	bltu	a5, a2, .L7	# tmp309, tmp305,
	movi.n	a6, 0	# tmp229,
.L7:
	l32i	a8, sp, 308	# %sfp,
	add.n	a3, a3, a7	# tmp310, tmp306, tmp308
	add.n	a3, a6, a3	# tmp231, tmp229, tmp310
	addi.n	a8, a8, 2	#,,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:60:     for( n = 0; n < length; n++ ) {
	l32i	a2, sp, 316	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:74:         corr_QC[  order ] += silk_RSHIFT64( silk_SMULL( tmp1_QS, state_QS[ 0 ] ), 2 * QS - QC );
	s32i.n	a5, a4, 0	# corr_QC, tmp309
	s32i.n	a3, a4, 4	# corr_QC, tmp231
	s32i	a8, sp, 308	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:60:     for( n = 0; n < length; n++ ) {
	bne	a2, a8, .L8	#,,
	l32i.n	a2, sp, 4	# corr_QC, pretmp_201
	l32i.n	a3, sp, 0	# corr_QC, pretmp_201
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:46:     if (in_upper == 0) {
	bnez.n	a2, .L9	# pretmp_201,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	bnez.n	a3, .L10	# pretmp_201,
.L2:
	l32i	a8, sp, 312	# %sfp,
	addi.n	a2, a8, 1	# _64,,
	j	.L11		#
.L10:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a3, a3	# iftmp$4_112, pretmp_201
	l32i	a8, sp, 312	# %sfp,
	addi	a5, a3, -3	# iftmp$1_104, iftmp$4_112,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:78:     lsh = silk_LIMIT( lsh, -12 - QC, 30 - QC );
	movi.n	a3, 0x14	# tmp234,
	addi.n	a2, a8, 1	# _64,,
	blt	a3, a5, .L11	# tmp234, iftmp$1_104,
	j	.L12		#
.L9:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a2	# iftmp$4_116, pretmp_201
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:77:     lsh = silk_CLZ64( corr_QC[ 0 ] ) - 35;
	addi	a5, a2, -35	# iftmp$1_104, iftmp$4_116,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:78:     lsh = silk_LIMIT( lsh, -12 - QC, 30 - QC );
	movi.n	a2, -0x16	# tmp239,
	bge	a5, a2, .L13	# iftmp$1_104, tmp239,
	mov.n	a5, a2	# iftmp$1_104, tmp239
.L13:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	l32i	a8, sp, 336	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	movi.n	a2, -0xa	# tmp240,
	sub	a2, a2, a5	# tmp241, tmp240, iftmp$1_104
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	s32i.n	a2, a8, 0	# *scale_100(D), tmp241
	l32i	a8, sp, 312	# %sfp,
	addi.n	a2, a8, 1	# _64,,
	j	.L14		#
.L11:
	l32i	a8, sp, 336	# %sfp,
	movi.n	a3, -0x1e	# tmp242,
	s32i.n	a3, a8, 0	# *scale_100(D), tmp242
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:78:     lsh = silk_LIMIT( lsh, -12 - QC, 30 - QC );
	movi.n	a5, 0x14	# iftmp$1_104,
	j	.L15		#
.L12:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	movi.n	a3, -0xa	# tmp243,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	l32i	a8, sp, 336	# %sfp,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	sub	a3, a3, a5	# tmp244, tmp243, iftmp$1_104
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:79:     *scale = -( QC + lsh );
	s32i.n	a3, a8, 0	# *scale_100(D), tmp244
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:81:     if( lsh >= 0 ) {
	bgez	a5, .L15	# iftmp$1_104,
.L14:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:86:         for( i = 0; i < order + 1; i++ ) {
	bgei	a2, 1, .L16	# _64,,
	j	.L1		#
.L15:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:82:         for( i = 0; i < order + 1; i++ ) {
	blti	a2, 1, .L1	# _64,,
	l32i	a4, sp, 340	# %sfp, ivtmp$11
	slli	a2, a2, 2	# tmp245, _64,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:83:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_LSHIFT64( corr_QC[ i ], lsh ) );
	movi.n	a7, 0x20	# tmp247,
	mov.n	a6, sp	# ivtmp$10,
	add.n	a3, a4, a2	# _211, ivtmp$11, tmp245
	and	a7, a5, a7	# tmp248, iftmp$1_104, tmp247
	movi.n	a8, 0	# tmp249,
.L18:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:83:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_LSHIFT64( corr_QC[ i ], lsh ) );
	l32i.n	a2, a6, 0	# MEM[base: _223, offset: 0B], MEM[base: _223, offset: 0B]
	addi.n	a6, a6, 8	# ivtmp$10, ivtmp$10,
	ssl	a5	# iftmp$1_104
	sll	a2, a2	# tmp311, MEM[base: _223, offset: 0B]
	movnez	a2, a8, a7	# tmp311, tmp249, tmp248
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:83:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_LSHIFT64( corr_QC[ i ], lsh ) );
	s32i.n	a2, a4, 0	# MEM[base: _222, offset: 0B], tmp311
	addi.n	a4, a4, 4	# ivtmp$11, ivtmp$11,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:82:         for( i = 0; i < order + 1; i++ ) {
	bne	a3, a4, .L18	# _211, ivtmp$11,
	j	.L1		#
.L16:
	l32i	a4, sp, 340	# %sfp, ivtmp$16
	l32i	a8, sp, 332	# %sfp,
	addi.n	a10, a4, 4	# tmp257, ivtmp$16,
	neg	a5, a5	# _232, iftmp$1_104
	add.n	a10, a10, a8	# _181, tmp257,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:87:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_RSHIFT64( corr_QC[ i ], -lsh ) );
	movi.n	a9, 0x20	# tmp260,
	movi.n	a8, -1	# tmp266,
	mov.n	a6, sp	# ivtmp$15,
	and	a9, a5, a9	# tmp261, _232, tmp260
	xor	a8, a5, a8	# tmp267, _232, tmp266
.L19:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:87:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_RSHIFT64( corr_QC[ i ], -lsh ) );
	l32i.n	a3, a6, 4	# MEM[base: _192, offset: 0B], MEM[base: _192, offset: 0B]
	l32i.n	a2, a6, 0	# MEM[base: _192, offset: 0B], MEM[base: _192, offset: 0B]
	slli	a7, a3, 1	# tmp264, MEM[base: _192, offset: 0B],
	ssl	a8	# tmp267
	sll	a7, a7	# tmp268, tmp264
	ssr	a5	# _232
	srl	a2, a2	# tmp313, MEM[base: _192, offset: 0B]
	or	a2, a7, a2	# tmp313, tmp268, tmp313
	ssr	a5	# _232
	sra	a3, a3	# tmp314, MEM[base: _192, offset: 0B]
	movnez	a2, a3, a9	# tmp313, tmp314, tmp261
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:87:             corr[ i ] = (opus_int32)silk_CHECK_FIT32( silk_RSHIFT64( corr_QC[ i ], -lsh ) );
	s32i.n	a2, a4, 0	# MEM[base: _191, offset: 0B], tmp313
	addi.n	a4, a4, 4	# ivtmp$16, ivtmp$16,
	addi.n	a6, a6, 8	# ivtmp$15, ivtmp$15,
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:86:         for( i = 0; i < order + 1; i++ ) {
	bne	a10, a4, .L19	# _181, ivtmp$16,
.L1:
# @OPUS@\upstream\silk\fixed\warped_autocorrelation_FIX.c:91: }
	l32i	a0, sp, 380	#,
	movi	a9, 0x180	#,
	l32i	a12, sp, 376	#,
	l32i	a13, sp, 372	#,
	l32i	a14, sp, 368	#,
	l32i	a15, sp, 364	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_warped_autocorrelation_FIX_c, .-silk_warped_autocorrelation_FIX_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
