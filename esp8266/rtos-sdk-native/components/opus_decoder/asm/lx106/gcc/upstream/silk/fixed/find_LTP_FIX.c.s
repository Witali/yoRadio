# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/find_LTP_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"find_LTP_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LTP_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LTP_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LTP_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\find_LTP_FIX.c.s.raw
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
	.global	__divdi3
	.section	.text.silk_find_LTP_FIX,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_find_LTP_FIX
	.type	silk_find_LTP_FIX, @function
# Function: silk_find_LTP_FIX
# Module: upstream/silk/fixed/find_LTP_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main_FIX.h"
# C context: #include "tuning_parameters.h"
# C context:
# C context: void silk_find_LTP_FIX(
# C context: opus_int32                      XXLTP_Q17[ MAX_NB_SUBFR * LTP_ORDER * LTP_ORDER ], /* O    Correlation matrix                                               */
# C context: opus_int32                      xXLTP_Q17[ MAX_NB_SUBFR * LTP_ORDER ],  /* O    Correlation vector                                                          */
# C context: const opus_int16                r_ptr[],                                /* I    Residual signal after LPC                                                   */
# C context: const opus_int                  lag[ MAX_NB_SUBFR ],                    /* I    LTP lags                                                                    */
silk_find_LTP_FIX:
	addi	sp, sp, -96	#,,
	s32i	a0, sp, 92	#,
	s32i	a12, sp, 88	#,
	s32i	a13, sp, 84	#,
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:44: {
	s32i.n	a3, sp, 32	# %sfp, xXLTP_Q17
	s32i.n	a4, sp, 36	# %sfp, r_ptr
	s32i.n	a6, sp, 44	# %sfp, subfr_length
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a7, 1, .L1	# nb_subfr,,
	slli	a7, a7, 2	# tmp126, nb_subfr,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:95:         r_ptr         += subfr_length;
	slli	a3, a6, 1	#, subfr_length,
	addi.n	a4, a6, 5	#, subfr_length,
	add.n	a7, a5, a7	#, lag, tmp126
	s32i.n	a5, sp, 40	# %sfp, lag
	s32i.n	a3, sp, 52	# %sfp,
	s32i.n	a4, sp, 56	# %sfp,
	addi	a12, a2, 100	# ivtmp$35, XXLTP_Q17,
	s32i.n	a7, sp, 48	# %sfp,
.L8:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:54:         lag_ptr = r_ptr - ( lag[ k ] + LTP_ORDER / 2 );
	l32i.n	a2, sp, 40	# %sfp,
	l32i.n	a3, sp, 36	# %sfp,
	l32i.n	a13, a2, 0	# MEM[base: _48, offset: 0B], MEM[base: _48, offset: 0B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:56:         silk_sum_sqr_shift( &xx, &xx_shifts, r_ptr, subfr_length + LTP_ORDER );                            /* xx in Q( -xx_shifts ) */
	l32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:54:         lag_ptr = r_ptr - ( lag[ k ] + LTP_ORDER / 2 );
	slli	a13, a13, 1	# tmp130, MEM[base: _48, offset: 0B],
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:56:         silk_sum_sqr_shift( &xx, &xx_shifts, r_ptr, subfr_length + LTP_ORDER );                            /* xx in Q( -xx_shifts ) */
	mov.n	a4, a3	#,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:54:         lag_ptr = r_ptr - ( lag[ k ] + LTP_ORDER / 2 );
	sub	a13, a3, a13	# tmp132,, tmp130
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:56:         silk_sum_sqr_shift( &xx, &xx_shifts, r_ptr, subfr_length + LTP_ORDER );                            /* xx in Q( -xx_shifts ) */
	addi	a2, sp, 20	#,,
	addi	a3, sp, 28	#,,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:57:         silk_corrMatrix_FIX( lag_ptr, subfr_length, LTP_ORDER, XXLTP_Q17_ptr, &nrg, &XX_shifts, arch );    /* XXLTP_Q17_ptr and nrg in Q( -XX_shifts ) */
	l32i	a4, sp, 96	# arch,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:54:         lag_ptr = r_ptr - ( lag[ k ] + LTP_ORDER / 2 );
	addi	a13, a13, -4	# lag_ptr, tmp132,
	addi	a15, a12, -100	# ivtmp$20, ivtmp$35,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:57:         silk_corrMatrix_FIX( lag_ptr, subfr_length, LTP_ORDER, XXLTP_Q17_ptr, &nrg, &XX_shifts, arch );    /* XXLTP_Q17_ptr and nrg in Q( -XX_shifts ) */
	l32i.n	a3, sp, 44	# %sfp,
	addi	a7, sp, 24	#,,
	s32i.n	a4, sp, 0	#,
	mov.n	a2, a13	#, lag_ptr
	movi.n	a4, 5	#,
	addi	a6, sp, 16	#,,
	mov.n	a5, a15	#, ivtmp$20
	call0	silk_corrMatrix_FIX		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:58:         extra_shifts = xx_shifts - XX_shifts;
	l32i.n	a7, sp, 28	# xx_shifts, xX_shifts
	l32i.n	a2, sp, 24	# XX_shifts, XX_shifts$2_10
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:58:         extra_shifts = xx_shifts - XX_shifts;
	sub	a4, a7, a2	# extra_shifts, xX_shifts, XX_shifts$2_10
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:59:         if( extra_shifts > 0 ) {
	blti	a4, 1, .L3	# extra_shifts,,
	mov.n	a2, a15	# ivtmp$27, ivtmp$20
.L4:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:63:                 XXLTP_Q17_ptr[ i ] = silk_RSHIFT32( XXLTP_Q17_ptr[ i ], extra_shifts );              /* Q( -xX_shifts ) */
	l32i.n	a3, a2, 0	# MEM[base: _104, offset: 0B], MEM[base: _104, offset: 0B]
	ssr	a4	# extra_shifts
	sra	a3, a3	# tmp136, MEM[base: _104, offset: 0B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:63:                 XXLTP_Q17_ptr[ i ] = silk_RSHIFT32( XXLTP_Q17_ptr[ i ], extra_shifts );              /* Q( -xX_shifts ) */
	s32i.n	a3, a2, 0	# MEM[base: _104, offset: 0B], tmp136
	addi.n	a2, a2, 4	# ivtmp$27, ivtmp$27,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:62:             for( i = 0; i < LTP_ORDER * LTP_ORDER; i++ ) {
	bne	a12, a2, .L4	# ivtmp$35, ivtmp$27,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:65:             nrg = silk_RSHIFT32( nrg, extra_shifts );                                                /* Q( -xX_shifts ) */
	l32i.n	a2, sp, 16	# nrg, nrg
	ssr	a4	# extra_shifts
	sra	a4, a2	# tmp138, nrg
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:65:             nrg = silk_RSHIFT32( nrg, extra_shifts );                                                /* Q( -xX_shifts ) */
	s32i.n	a4, sp, 16	# nrg, tmp138
	j	.L5		#
.L3:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:66:         } else if( extra_shifts < 0 ) {
	beqz.n	a4, .L5	# extra_shifts,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:69:             xx = silk_RSHIFT32( xx, -extra_shifts );                                                 /* Q( -xX_shifts ) */
	l32i.n	a3, sp, 20	# xx, xx
	sub	a7, a2, a7	# tmp140, XX_shifts$2_10, xX_shifts
	ssr	a7	# tmp140
	sra	a7, a3	# tmp141, xx
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:69:             xx = silk_RSHIFT32( xx, -extra_shifts );                                                 /* Q( -xX_shifts ) */
	s32i.n	a7, sp, 20	# xx, tmp141
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:68:             xX_shifts = XX_shifts;
	mov.n	a7, a2	# xX_shifts, XX_shifts$2_10
.L5:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:73:         silk_corrVector_FIX( lag_ptr, r_ptr, subfr_length, LTP_ORDER, xXLTP_Q17_ptr, xX_shifts, arch );    /* xXLTP_Q17_ptr in Q( -xX_shifts ) */
	l32i	a2, sp, 96	# arch,
	l32i.n	a4, sp, 44	# %sfp,
	l32i.n	a3, sp, 36	# %sfp,
	l32i.n	a6, sp, 32	# %sfp,
	s32i.n	a2, sp, 0	#,
	movi.n	a5, 5	#,
	mov.n	a2, a13	#, lag_ptr
	call0	silk_corrVector_FIX		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:76:         temp = silk_SMLAWB( 1, nrg, SILK_FIX_CONST( LTP_CORR_INV_MAX, 16 ) );
	l32i.n	a2, sp, 16	# nrg, nrg$7_21
	movi	a4, 0x7ae	#,
	extui	a3, a2, 0, 16	# tmp143, nrg$7_21,
	srai	a2, a2, 16	# tmp147, nrg$7_21,
	mull	a3, a3, a4	# tmp145, tmp143,
	mull	a2, a2, a4	# tmp149, tmp147,
	srai	a3, a3, 16	# tmp146, tmp145,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:76:         temp = silk_SMLAWB( 1, nrg, SILK_FIX_CONST( LTP_CORR_INV_MAX, 16 ) );
	addi.n	a2, a2, 1	# tmp150, tmp149,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:77:         temp = silk_max( temp, xx );
	l32i.n	a13, sp, 20	# xx, temp
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:76:         temp = silk_SMLAWB( 1, nrg, SILK_FIX_CONST( LTP_CORR_INV_MAX, 16 ) );
	add.n	a2, a3, a2	# temp, tmp146, tmp150
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:77:         temp = silk_max( temp, xx );
	bge	a13, a2, .L6	# temp, temp,
	mov.n	a13, a2	# temp, temp
.L6:
	srai	a14, a13, 31	# _111, temp,
.L7:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:88:             XXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)XXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a2, a15, 0	# MEM[base: _127, offset: 0B], MEM[base: _127, offset: 0B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:88:             XXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)XXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:88:             XXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)XXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a2, 31	# tmp159, MEM[base: _127, offset: 0B],
	srli	a6, a2, 15	# tmp161, MEM[base: _127, offset: 0B],
	slli	a3, a3, 17	# tmp217, tmp159,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:88:             XXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)XXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
	slli	a2, a2, 17	#, MEM[base: _127, offset: 0B],
	or	a3, a6, a3	#, tmp161, tmp217
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:88:             XXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)XXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a15, 0	# MEM[base: _127, offset: 0B],
	addi.n	a15, a15, 4	# ivtmp$20, ivtmp$20,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:87:         for( i = 0; i < LTP_ORDER * LTP_ORDER; i++ ) {
	bne	a12, a15, .L7	# ivtmp$35, ivtmp$20,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a2, a3, 0	# MEM[base: xXLTP_Q17_ptr_52, offset: 0B], MEM[base: xXLTP_Q17_ptr_52, offset: 0B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a2, 31	# tmp168, MEM[base: xXLTP_Q17_ptr_52, offset: 0B],
	srli	a6, a2, 15	# tmp170, MEM[base: xXLTP_Q17_ptr_52, offset: 0B],
	slli	a3, a3, 17	# tmp223, tmp168,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	or	a3, a6, a3	#, tmp170, tmp223
	slli	a2, a2, 17	#, MEM[base: xXLTP_Q17_ptr_52, offset: 0B],
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a6, a4, 4	# MEM[base: xXLTP_Q17_ptr_52, offset: 4B], MEM[base: xXLTP_Q17_ptr_52, offset: 4B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a4, 0	# MEM[base: xXLTP_Q17_ptr_52, offset: 0B],
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a6, 31	# tmp177, MEM[base: xXLTP_Q17_ptr_52, offset: 4B],
	srli	a7, a6, 15	# tmp179, MEM[base: xXLTP_Q17_ptr_52, offset: 4B],
	slli	a3, a3, 17	# tmp229, tmp177,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
	slli	a2, a6, 17	#, MEM[base: xXLTP_Q17_ptr_52, offset: 4B],
	or	a3, a7, a3	#, tmp179, tmp229
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a6, a3, 8	# MEM[base: xXLTP_Q17_ptr_52, offset: 8B], MEM[base: xXLTP_Q17_ptr_52, offset: 8B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a3, 4	# MEM[base: xXLTP_Q17_ptr_52, offset: 4B],
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a6, 31	# tmp186, MEM[base: xXLTP_Q17_ptr_52, offset: 8B],
	srli	a7, a6, 15	# tmp188, MEM[base: xXLTP_Q17_ptr_52, offset: 8B],
	slli	a3, a3, 17	# tmp235, tmp186,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
	slli	a2, a6, 17	#, MEM[base: xXLTP_Q17_ptr_52, offset: 8B],
	or	a3, a7, a3	#, tmp188, tmp235
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a6, a4, 12	# MEM[base: xXLTP_Q17_ptr_52, offset: 12B], MEM[base: xXLTP_Q17_ptr_52, offset: 12B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a4, 8	# MEM[base: xXLTP_Q17_ptr_52, offset: 8B],
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a6, 31	# tmp195, MEM[base: xXLTP_Q17_ptr_52, offset: 12B],
	srli	a7, a6, 15	# tmp197, MEM[base: xXLTP_Q17_ptr_52, offset: 12B],
	slli	a3, a3, 17	# tmp241, tmp195,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
	slli	a2, a6, 17	#, MEM[base: xXLTP_Q17_ptr_52, offset: 12B],
	or	a3, a7, a3	#, tmp197, tmp241
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a4, a13	#, temp
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a6, a3, 16	# MEM[base: xXLTP_Q17_ptr_52, offset: 16B], MEM[base: xXLTP_Q17_ptr_52, offset: 16B]
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a3, 12	# MEM[base: xXLTP_Q17_ptr_52, offset: 12B],
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	srai	a3, a6, 31	# tmp204, MEM[base: xXLTP_Q17_ptr_52, offset: 16B],
	srli	a7, a6, 15	# tmp206, MEM[base: xXLTP_Q17_ptr_52, offset: 16B],
	slli	a3, a3, 17	# tmp247, tmp204,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	mov.n	a5, a14	#, _111
	slli	a2, a6, 17	#, MEM[base: xXLTP_Q17_ptr_52, offset: 16B],
	or	a3, a7, a3	#, tmp206, tmp247
	call0	__divdi3		#
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	l32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:95:         r_ptr         += subfr_length;
	l32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:91:             xXLTP_Q17_ptr[ i ] = (opus_int32)( silk_LSHIFT64( (opus_int64)xXLTP_Q17_ptr[ i ], 17 ) / temp );
	s32i.n	a2, a4, 16	# MEM[base: xXLTP_Q17_ptr_52, offset: 16B],
	l32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:95:         r_ptr         += subfr_length;
	l32i.n	a4, sp, 52	# %sfp,
	addi.n	a2, a2, 4	#,,
	s32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:97:         xXLTP_Q17_ptr += LTP_ORDER;
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:95:         r_ptr         += subfr_length;
	add.n	a3, a3, a4	#,,
	s32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:97:         xXLTP_Q17_ptr += LTP_ORDER;
	addi	a2, a2, 20	#,,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	l32i.n	a3, sp, 48	# %sfp,
	l32i.n	a4, sp, 40	# %sfp,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:97:         xXLTP_Q17_ptr += LTP_ORDER;
	s32i.n	a2, sp, 32	# %sfp,
	addi	a12, a12, 100	# ivtmp$35, ivtmp$35,
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:53:     for( k = 0; k < nb_subfr; k++ ) {
	bne	a3, a4, .L8	#,,
.L1:
# @OPUS@\upstream\silk\fixed\find_LTP_FIX.c:99: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	silk_find_LTP_FIX, .-silk_find_LTP_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
