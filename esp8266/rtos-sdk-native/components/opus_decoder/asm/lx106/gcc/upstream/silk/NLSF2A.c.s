# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF2A.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF2A.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF2A.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF2A.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF2A.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF2A.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF2A.c.s.raw
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
	.section	.text.silk_NLSF2A,"ax",@progbits
	.literal_position
	.literal .LC0, ordering16$3185
	.literal .LC1, ordering10$3186
	.literal .LC2, 65536
	.literal .LC3, silk_LSFCosTab_FIX_Q12
	.literal .LC5, 1073741822
	.align	4
	.global	silk_NLSF2A
	.type	silk_NLSF2A, @function
# Function: silk_NLSF2A
# Module: upstream/silk/NLSF2A.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* compute whitening filter coefficients from normalized line spectral frequencies */
# C context: void silk_NLSF2A(
# C context: opus_int16                  *a_Q12,             /* O    monic whitening filter coefficients in Q12,  [ d ]          */
# C context: const opus_int16            *NLSF,              /* I    normalized line spectral frequencies in Q15, [ d ]          */
# C context: const opus_int              d,                  /* I    filter order (should be even)                               */
# C context: int                         arch                /* I    Run-time architecture                                       */
silk_NLSF2A:
	movi	a9, 0x190	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 396	#,
	s32i	a12, sp, 392	#,
	s32i	a13, sp, 388	#,
	s32i	a14, sp, 384	#,
	s32i	a15, sp, 380	#,
# @OPUS@\upstream\silk\NLSF2A.c:72: {
	s32i	a4, sp, 336	# %sfp, d
	s32i	a2, sp, 344	# %sfp, a_Q12
# @OPUS@\upstream\silk\NLSF2A.c:92:     ordering = d == 16 ? ordering16 : ordering10;
	beqi	a4, 16, .L38	# d,,
# @OPUS@\upstream\silk\NLSF2A.c:92:     ordering = d == 16 ? ordering16 : ordering10;
	l32r	a7, .LC1	#, iftmp$0_194
# @OPUS@\upstream\silk\NLSF2A.c:93:     for( k = 0; k < d; k++ ) {
	bgei	a4, 1, .L2	# d,,
.L6:
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	l32i	a2, sp, 96	# MEM[(const opus_int32 *)&cos_LSF_QA], MEM[(const opus_int32 *)&cos_LSF_QA]
# @OPUS@\upstream\silk\NLSF2A.c:113:     dd = silk_RSHIFT( d, 1 );
	l32i	a6, sp, 336	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	neg	a2, a2	# tmp453, MEM[(const opus_int32 *)&cos_LSF_QA]
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	s32i	a2, sp, 248	# MEM[(opus_int32 *)&P + 4B], tmp453
	l32i	a2, sp, 100	# MEM[(const opus_int32 *)&cos_LSF_QA + 4B], MEM[(const opus_int32 *)&cos_LSF_QA + 4B]
# @OPUS@\upstream\silk\NLSF2A.c:53:     out[0] = silk_LSHIFT( 1, QA );
	l32r	a7, .LC2	#,
# @OPUS@\upstream\silk\NLSF2A.c:113:     dd = silk_RSHIFT( d, 1 );
	srai	a6, a6, 1	#,,
	neg	a2, a2	#, MEM[(const opus_int32 *)&cos_LSF_QA + 4B]
	s32i	a6, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:53:     out[0] = silk_LSHIFT( 1, QA );
	s32i	a7, sp, 244	# MEM[(opus_int32 *)&P],
	s32i	a2, sp, 348	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	bgei	a6, 2, .L3	#,,
	j	.L60		#
.L38:
# @OPUS@\upstream\silk\NLSF2A.c:92:     ordering = d == 16 ? ordering16 : ordering10;
	l32r	a7, .LC0	#, iftmp$0_194
.L2:
	l32r	a6, .LC3	#, tmp1093
# @OPUS@\upstream\silk\NLSF2A.c:92:     ordering = d == 16 ? ordering16 : ordering10;
	l32i	a8, sp, 336	# %sfp, d
	movi.n	a5, 0	# k,
.L5:
# @OPUS@\upstream\silk\NLSF2A.c:97:         f_int = silk_RSHIFT( NLSF[k], 15 - 7 );
	l16ui	a4, a3, 0	# MEM[base: _844, offset: 0B],
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	add.n	a11, a7, a5	# tmp465, iftmp$0_194, k
# @OPUS@\upstream\silk\NLSF2A.c:97:         f_int = silk_RSHIFT( NLSF[k], 15 - 7 );
	slli	a4, a4, 16	# tmp457, MEM[base: _844, offset: 0B],
	srai	a9, a4, 24	# _5, tmp457,
# @OPUS@\upstream\silk\NLSF2A.c:107:         delta   = silk_LSFCosTab_FIX_Q12[ f_int + 1 ] - cos_val;  /* Q12, with a range of 0..200 */
	addi.n	a2, a9, 1	# tmp471, _5,
# @OPUS@\upstream\silk\NLSF2A.c:106:         cos_val = silk_LSFCosTab_FIX_Q12[ f_int ];                /* Q12 */
	slli	a10, a9, 1	# tmp461, _5,
# @OPUS@\upstream\silk\NLSF2A.c:107:         delta   = silk_LSFCosTab_FIX_Q12[ f_int + 1 ] - cos_val;  /* Q12, with a range of 0..200 */
	slli	a2, a2, 1	# tmp472, tmp471,
# @OPUS@\upstream\silk\NLSF2A.c:106:         cos_val = silk_LSFCosTab_FIX_Q12[ f_int ];                /* Q12 */
	add.n	a10, a6, a10	# tmp462, tmp1093, tmp461
# @OPUS@\upstream\silk\NLSF2A.c:107:         delta   = silk_LSFCosTab_FIX_Q12[ f_int + 1 ] - cos_val;  /* Q12, with a range of 0..200 */
	add.n	a2, a6, a2	# tmp473, tmp1093, tmp472
# @OPUS@\upstream\silk\NLSF2A.c:106:         cos_val = silk_LSFCosTab_FIX_Q12[ f_int ];                /* Q12 */
	l16si	a10, a10, 0	# silk_LSFCosTab_FIX_Q12, _10
# @OPUS@\upstream\silk\NLSF2A.c:107:         delta   = silk_LSFCosTab_FIX_Q12[ f_int + 1 ] - cos_val;  /* Q12, with a range of 0..200 */
	l16si	a2, a2, 0	# silk_LSFCosTab_FIX_Q12, tmp474
# @OPUS@\upstream\silk\NLSF2A.c:97:         f_int = silk_RSHIFT( NLSF[k], 15 - 7 );
	srai	a4, a4, 16	# _4, tmp457,
# @OPUS@\upstream\silk\NLSF2A.c:100:         f_frac = NLSF[k] - silk_LSHIFT( f_int, 15 - 7 );
	slli	a9, a9, 8	# tmp478, _5,
# @OPUS@\upstream\silk\NLSF2A.c:107:         delta   = silk_LSFCosTab_FIX_Q12[ f_int + 1 ] - cos_val;  /* Q12, with a range of 0..200 */
	sub	a2, a2, a10	# delta, tmp474, _10
# @OPUS@\upstream\silk\NLSF2A.c:100:         f_frac = NLSF[k] - silk_LSHIFT( f_int, 15 - 7 );
	sub	a4, a4, a9	# f_frac, _4, tmp478
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	mull	a2, a2, a4	# tmp480, delta, f_frac
	slli	a10, a10, 8	# tmp481, _10,
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	l8ui	a4, a11, 0	# MEM[base: _846, offset: 0B], MEM[base: _846, offset: 0B]
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	add.n	a2, a2, a10	# tmp482, tmp480, tmp481
	srai	a2, a2, 3	# tmp483, tmp482,
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	slli	a4, a4, 2	# tmp467, MEM[base: _846, offset: 0B],
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	addi.n	a2, a2, 1	# tmp484, tmp483,
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	add.n	a4, sp, a4	# tmp468,, tmp467
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	srai	a2, a2, 1	# tmp485, tmp484,
# @OPUS@\upstream\silk\NLSF2A.c:110:         cos_LSF_QA[ordering[k]] = silk_RSHIFT_ROUND( silk_LSHIFT( cos_val, 8 ) + silk_MUL( delta, f_frac ), 20 - QA ); /* QA */
	s32i	a2, a4, 96	# cos_LSF_QA, tmp485
# @OPUS@\upstream\silk\NLSF2A.c:93:     for( k = 0; k < d; k++ ) {
	addi.n	a5, a5, 1	# k, k,
	addi.n	a3, a3, 2	# ivtmp$91, ivtmp$91,
# @OPUS@\upstream\silk\NLSF2A.c:93:     for( k = 0; k < d; k++ ) {
	blt	a5, a8, .L5	# k, d,
	j	.L6		#
.L3:
	movi	a2, 0xf4	# tmp486,
	add.n	a2, sp, a2	# tmp487,, tmp486
	addi	a9, sp, 96	#,,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	movi.n	a8, 1	#,
	addi	a10, a2, -8	#, tmp487,
	s32i	a8, sp, 308	# %sfp,
	s32i	a9, sp, 328	# %sfp,
	s32i	a10, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	s32i	a9, sp, 320	# %sfp,
	s32i	a2, sp, 304	# %sfp, tmp487
.L9:
# @OPUS@\upstream\silk\NLSF2A.c:56:         ftmp = cLSF[2*k];            /* QA*/
	l32i	a11, sp, 320	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a7, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:56:         ftmp = cLSF[2*k];            /* QA*/
	l32i.n	a12, a11, 8	# MEM[base: _830, offset: 8B], ftmp
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i.n	a6, a7, 12	# MEM[base: _832, offset: 12B], D__lsm0$20
	srai	a13, a12, 31	# _152, ftmp,
	mov.n	a4, a12	#, ftmp
	mov.n	a5, a13	#, _152
	mov.n	a2, a6	#, D__lsm0$20
	srai	a3, a6, 31	#, D__lsm0$20,
	s32i	a6, sp, 352	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	slli	a4, a3, 17	# tmp494, tmp1015,
	srli	a2, a2, 15	# tmp1016,,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i.n	a15, a8, 8	# MEM[base: _832, offset: 8B], D__lsm1$21
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	or	a2, a4, a2	# tmp1016, tmp494, tmp1016
	addi.n	a4, a2, 1	# tmp1018, tmp1016,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	slli	a7, a15, 1	# tmp489, D__lsm1$21,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	srai	a3, a3, 15	# tmp1017, tmp1015,
	movi.n	a5, 1	# tmp497,
	l32i	a6, sp, 352	#,
	bltu	a4, a2, .L7	# tmp1018, tmp1016,
	movi.n	a5, 0	# tmp497,
.L7:
	add.n	a5, a5, a3	# tmp499, tmp497, tmp1017
	slli	a5, a5, 31	# tmp501, tmp499,
	srli	a2, a4, 1	# tmp1020, tmp1018,
	or	a2, a5, a2	# tmp1020, tmp501, tmp1020
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	sub	a2, a7, a2	# tmp502, tmp489, tmp1020
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	l32i	a10, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	s32i.n	a2, a9, 16	# MEM[base: _832, offset: 16B], tmp502
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	bnei	a10, 1, .L8	#,,
.L17:
# @OPUS@\upstream\silk\NLSF2A.c:61:         out[1] -= ftmp;
	l32i	a2, sp, 248	# MEM[(opus_int32 *)&P + 4B], MEM[(opus_int32 *)&P + 4B]
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	l32i	a11, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:61:         out[1] -= ftmp;
	sub	a12, a2, a12	# tmp503, MEM[(opus_int32 *)&P + 4B], ftmp
	l32i	a6, sp, 312	# %sfp,
	s32i	a12, sp, 248	# MEM[(opus_int32 *)&P + 4B], tmp503
	l32i	a12, sp, 320	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	addi.n	a11, a11, 1	#,,
	addi.n	a12, a12, 8	#,,
	addi.n	a6, a6, 4	#,,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	l32i	a7, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	s32i	a11, sp, 308	# %sfp,
	s32i	a12, sp, 320	# %sfp,
	s32i	a6, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	bne	a7, a11, .L9	#,,
	j	.L61		#
.L8:
	addi.n	a2, a10, -1	# tmp505, tmp8,
	bltui	a2, 3, .L40	# tmp505,,
	mov.n	a14, a9	# ivtmp$76,
	addi	a2, a10, -4	# tmp507, tmp8,
	movi.n	a9, -2	#,
	addi	a3, a10, -2	# tmp506, tmp8,
	and	a2, a2, a9	# tmp509, tmp507,
	sub	a2, a3, a2	#, tmp506, tmp509
	s32i	a2, sp, 340	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	s32i	a10, sp, 316	# %sfp, tmp8
	s32i	a12, sp, 324	# %sfp, ftmp
.L14:
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i	a4, sp, 324	# %sfp,
	mov.n	a5, a13	#, _152
	mov.n	a2, a15	#, D__lsm1$21
	srai	a3, a15, 31	#, D__lsm1$21,
	s32i	a6, sp, 352	#,
	call0	__muldi3		#
	l32i	a7, sp, 316	# %sfp,
	mov.n	a8, a3	# tmp1025,
	srli	a9, a2, 15	# tmp1026,,
	slli	a3, a3, 17	# tmp515, tmp1025,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a12, a14, 4	# MEM[base: _822, offset: 4B], _174
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	or	a9, a3, a9	# tmp1026, tmp515, tmp1026
	addi	a7, a7, -2	#,,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i	a6, sp, 352	#,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	addi.n	a11, a9, 1	# tmp1028, tmp1026,
	s32i	a7, sp, 316	# %sfp,
	l32i	a4, sp, 324	# %sfp,
	mov.n	a5, a13	#, _152
	mov.n	a2, a12	#, _174
	srai	a3, a12, 31	#, _174,
	srli	a10, a11, 1	# tmp1030, tmp1028,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a6, a12, a6	# tmp510, _174, D__lsm0$20
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	srai	a8, a8, 15	# tmp1027, tmp1025,
	movi.n	a7, 1	# k,
	bltu	a11, a9, .L12	# tmp1028, tmp1026,
	movi.n	a7, 0	# k,
.L12:
	add.n	a7, a7, a8	# tmp520, k, tmp1027
	slli	a7, a7, 31	# tmp522, tmp520,
	or	a10, a7, a10	# tmp1030, tmp522, tmp1030
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a6, a6, a10	# tmp523, tmp510, tmp1030
	s32i.n	a6, a14, 12	# MEM[base: _822, offset: 12B], tmp523
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	call0	__muldi3		#
	slli	a4, a3, 17	# tmp529, tmp1035,
	srli	a2, a2, 15	# tmp1036,,
	or	a2, a4, a2	# tmp1036, tmp529, tmp1036
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a5, a14, 0	# MEM[base: _822, offset: 0B], _345
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	addi.n	a7, a2, 1	# tmp1038, tmp1036,
	srli	a6, a7, 1	# tmp1040, tmp1038,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a15, a5, a15	# tmp524, _345, D__lsm1$21
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	movi.n	a4, 1	# k,
	srai	a3, a3, 15	# tmp1037, tmp1035,
	bltu	a7, a2, .L13	# tmp1038, tmp1036,
	movi.n	a4, 0	# k,
.L13:
	add.n	a4, a4, a3	# tmp534, k, tmp1037
	slli	a4, a4, 31	# tmp536, tmp534,
	or	a6, a4, a6	# tmp1040, tmp536, tmp1040
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a15, a15, a6	# tmp537, tmp524, tmp1040
	l32i	a8, sp, 316	# %sfp,
	l32i	a9, sp, 340	# %sfp,
	s32i.n	a15, a14, 8	# MEM[base: _822, offset: 8B], tmp537
	mov.n	a6, a12	# D__lsm0$20, _174
	addi	a14, a14, -8	# ivtmp$76, ivtmp$76,
	mov.n	a15, a5	# D__lsm1$21, _345
	bne	a8, a9, .L14	#,,
	l32i	a12, sp, 324	# %sfp, ftmp
	mov.n	a11, a8	#,
	j	.L11		#
.L40:
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	s32i	a10, sp, 316	# %sfp,
	mov.n	a11, a10	#,
.L11:
	l32r	a2, .LC5	#,
	movi	a3, 0xf4	#,
	add.n	a14, a11, a2	# tmp540,,
	slli	a14, a14, 2	# tmp542, tmp540,
	add.n	a3, a3, sp	#,,
	add.n	a14, a3, a14	# ivtmp$64,, tmp542
	j	.L16		#
.L41:
	mov.n	a14, a2	# ivtmp$64, ivtmp$64
.L16:
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a3, a14, 4	# MEM[base: _797, offset: 4B], MEM[base: _797, offset: 4B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a6, a14, 8	# MEM[base: _797, offset: 8B], MEM[base: _797, offset: 8B]
	l32i.n	a15, a14, 0	# MEM[base: _797, offset: 0B], MEM[base: _797, offset: 0B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	mov.n	a4, a12	#, ftmp
	mov.n	a5, a13	#, _152
	mov.n	a2, a3	#, MEM[base: _797, offset: 4B]
	srai	a3, a3, 31	#, MEM[base: _797, offset: 4B],
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a15, a15, a6	# tmp544, MEM[base: _797, offset: 0B], MEM[base: _797, offset: 8B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	call0	__muldi3		#
	slli	a4, a3, 17	# tmp552, tmp1045,
	srli	a2, a2, 15	# tmp1046,,
	or	a2, a4, a2	# tmp1046, tmp552, tmp1046
	addi.n	a6, a2, 1	# tmp1048, tmp1046,
	srli	a5, a6, 1	# tmp1050, tmp1048,
	movi.n	a4, 1	# k,
	srai	a3, a3, 15	# tmp1047, tmp1045,
	bltu	a6, a2, .L15	# tmp1048, tmp1046,
	movi.n	a4, 0	# k,
.L15:
	add.n	a4, a4, a3	# tmp557, k, tmp1047
	slli	a4, a4, 31	# tmp559, tmp557,
	or	a5, a4, a5	# tmp1050, tmp559, tmp1050
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a15, a15, a5	# tmp560, tmp544, tmp1050
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	l32i	a6, sp, 304	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	s32i.n	a15, a14, 8	# MEM[base: _797, offset: 8B], tmp560
	addi	a2, a14, -4	# ivtmp$64, ivtmp$64,
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	bne	a14, a6, .L41	# ivtmp$64,,
	j	.L17		#
.L20:
# @OPUS@\upstream\silk\NLSF2A.c:56:         ftmp = cLSF[2*k];            /* QA*/
	l32i	a7, sp, 328	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:56:         ftmp = cLSF[2*k];            /* QA*/
	l32i.n	a12, a7, 12	# MEM[base: _778, offset: 12B], ftmp
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i.n	a6, a8, 12	# MEM[base: _780, offset: 12B], D__lsm0$18
	srai	a13, a12, 31	# _98, ftmp,
	mov.n	a4, a12	#, ftmp
	mov.n	a5, a13	#, _98
	mov.n	a2, a6	#, D__lsm0$18
	srai	a3, a6, 31	#, D__lsm0$18,
	s32i	a6, sp, 352	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a9, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	slli	a4, a3, 17	# tmp567, tmp1055,
	srli	a2, a2, 15	# tmp1056,,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i.n	a15, a9, 8	# MEM[base: _780, offset: 8B], D__lsm1$19
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	or	a2, a4, a2	# tmp1056, tmp567, tmp1056
	addi.n	a4, a2, 1	# tmp1058, tmp1056,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	slli	a7, a15, 1	# tmp562, D__lsm1$19,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	srai	a3, a3, 15	# tmp1057, tmp1055,
	movi.n	a5, 1	# tmp570,
	l32i	a6, sp, 352	#,
	bltu	a4, a2, .L18	# tmp1058, tmp1056,
	movi.n	a5, 0	# tmp570,
.L18:
	add.n	a5, a5, a3	# tmp572, tmp570, tmp1057
	slli	a5, a5, 31	# tmp574, tmp572,
	srli	a2, a4, 1	# tmp1060, tmp1058,
	or	a2, a5, a2	# tmp1060, tmp574, tmp1060
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	l32i	a10, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	sub	a2, a7, a2	# tmp575, tmp562, tmp1060
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	l32i	a11, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:57:         out[k+1] = silk_LSHIFT( out[k-1], 1 ) - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[k] ), QA );
	s32i.n	a2, a10, 16	# MEM[base: _780, offset: 16B], tmp575
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	bnei	a11, 1, .L19	#,,
.L28:
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	l32i	a6, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:61:         out[1] -= ftmp;
	l32i	a2, sp, 196	# MEM[(opus_int32 *)&Q + 4B], MEM[(opus_int32 *)&Q + 4B]
	l32i	a7, sp, 328	# %sfp,
	l32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	addi.n	a6, a6, 1	#,,
# @OPUS@\upstream\silk\NLSF2A.c:61:         out[1] -= ftmp;
	sub	a12, a2, a12	# tmp576, MEM[(opus_int32 *)&Q + 4B], ftmp
	addi.n	a7, a7, 8	#,,
	addi.n	a8, a8, 4	#,,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	l32i	a9, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	s32i	a6, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:61:         out[1] -= ftmp;
	s32i	a12, sp, 196	# MEM[(opus_int32 *)&Q + 4B], tmp576
	s32i	a7, sp, 328	# %sfp,
	s32i	a8, sp, 312	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	bne	a9, a6, .L20	#,,
	j	.L63		#
.L19:
	addi.n	a2, a11, -1	# tmp578, tmp10,
	mov.n	a10, a11	#,
	bltui	a2, 3, .L42	# tmp578,,
	addi	a2, a11, -4	# tmp580, tmp10,
	addi	a3, a11, -2	# tmp579, tmp10,
	movi.n	a11, -2	#,
	and	a2, a2, a11	# tmp582, tmp580,
	sub	a2, a3, a2	#, tmp579, tmp582
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	l32i	a14, sp, 312	# %sfp, ivtmp$46
	s32i	a2, sp, 324	# %sfp,
	s32i	a10, sp, 316	# %sfp,
	s32i	a12, sp, 320	# %sfp, ftmp
.L25:
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i	a4, sp, 320	# %sfp,
	mov.n	a5, a13	#, _98
	mov.n	a2, a15	#, D__lsm1$19
	srai	a3, a15, 31	#, D__lsm1$19,
	s32i	a6, sp, 352	#,
	call0	__muldi3		#
	l32i	a7, sp, 316	# %sfp,
	mov.n	a8, a3	# tmp1065,
	srli	a9, a2, 15	# tmp1066,,
	slli	a3, a3, 17	# tmp588, tmp1065,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a12, a14, 4	# MEM[base: _770, offset: 4B], _120
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	or	a9, a3, a9	# tmp1066, tmp588, tmp1066
	addi	a7, a7, -2	#,,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i	a6, sp, 352	#,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	addi.n	a11, a9, 1	# tmp1068, tmp1066,
	s32i	a7, sp, 316	# %sfp,
	l32i	a4, sp, 320	# %sfp,
	mov.n	a5, a13	#, _98
	mov.n	a2, a12	#, _120
	srai	a3, a12, 31	#, _120,
	srli	a10, a11, 1	# tmp1070, tmp1068,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a6, a12, a6	# tmp583, _120, D__lsm0$18
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	srai	a8, a8, 15	# tmp1067, tmp1065,
	movi.n	a7, 1	# tmp591,
	bltu	a11, a9, .L23	# tmp1068, tmp1066,
	movi.n	a7, 0	# tmp591,
.L23:
	add.n	a7, a7, a8	# tmp593, tmp591, tmp1067
	slli	a7, a7, 31	# tmp595, tmp593,
	or	a10, a7, a10	# tmp1070, tmp595, tmp1070
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a6, a6, a10	# tmp596, tmp583, tmp1070
	s32i.n	a6, a14, 12	# MEM[base: _770, offset: 12B], tmp596
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	call0	__muldi3		#
	slli	a4, a3, 17	# tmp602, tmp1075,
	srli	a2, a2, 15	# tmp1076,,
	or	a2, a4, a2	# tmp1076, tmp602, tmp1076
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a5, a14, 0	# MEM[base: _770, offset: 0B], _413
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	addi.n	a7, a2, 1	# tmp1078, tmp1076,
	srli	a6, a7, 1	# tmp1080, tmp1078,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a15, a5, a15	# tmp597, _413, D__lsm1$19
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	movi.n	a4, 1	# tmp605,
	srai	a3, a3, 15	# tmp1077, tmp1075,
	bltu	a7, a2, .L24	# tmp1078, tmp1076,
	movi.n	a4, 0	# tmp605,
.L24:
	add.n	a4, a4, a3	# tmp607, tmp605, tmp1077
	slli	a4, a4, 31	# tmp609, tmp607,
	or	a6, a4, a6	# tmp1080, tmp609, tmp1080
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a15, a15, a6	# tmp610, tmp597, tmp1080
	l32i	a8, sp, 316	# %sfp,
	l32i	a9, sp, 324	# %sfp,
	s32i.n	a15, a14, 8	# MEM[base: _770, offset: 8B], tmp610
	mov.n	a6, a12	# D__lsm0$18, _120
	addi	a14, a14, -8	# ivtmp$46, ivtmp$46,
	mov.n	a15, a5	# D__lsm1$19, _413
	bne	a8, a9, .L25	#,,
	l32i	a12, sp, 320	# %sfp, ftmp
	mov.n	a11, a8	#,
	j	.L22		#
.L42:
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	s32i	a11, sp, 316	# %sfp, tmp10
.L22:
	l32r	a2, .LC5	#,
	movi	a3, 0xc0	#,
	add.n	a14, a11, a2	# tmp613,,
	slli	a14, a14, 2	# tmp615, tmp613,
	add.n	a3, a3, sp	#,,
	add.n	a14, a3, a14	# ivtmp$34,, tmp615
	j	.L27		#
.L43:
	mov.n	a14, a2	# ivtmp$34, ivtmp$34
.L27:
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a3, a14, 4	# MEM[base: _745, offset: 4B], MEM[base: _745, offset: 4B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	l32i.n	a6, a14, 8	# MEM[base: _745, offset: 8B], MEM[base: _745, offset: 8B]
	l32i.n	a15, a14, 0	# MEM[base: _745, offset: 0B], MEM[base: _745, offset: 0B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	mov.n	a4, a12	#, ftmp
	mov.n	a5, a13	#, _98
	mov.n	a2, a3	#, MEM[base: _745, offset: 4B]
	srai	a3, a3, 31	#, MEM[base: _745, offset: 4B],
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	add.n	a15, a15, a6	# tmp617, MEM[base: _745, offset: 0B], MEM[base: _745, offset: 8B]
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	call0	__muldi3		#
	slli	a4, a3, 17	# tmp625, tmp1085,
	srli	a2, a2, 15	# tmp1086,,
	or	a2, a4, a2	# tmp1086, tmp625, tmp1086
	addi.n	a6, a2, 1	# tmp1088, tmp1086,
	srli	a5, a6, 1	# tmp1090, tmp1088,
	movi.n	a4, 1	# tmp628,
	srai	a3, a3, 15	# tmp1087, tmp1085,
	bltu	a6, a2, .L26	# tmp1088, tmp1086,
	movi.n	a4, 0	# tmp628,
.L26:
	add.n	a4, a4, a3	# tmp630, tmp628, tmp1087
	slli	a4, a4, 31	# tmp632, tmp630,
	or	a5, a4, a5	# tmp1090, tmp632, tmp1090
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	sub	a15, a15, a5	# tmp633, tmp617, tmp1090
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	l32i	a6, sp, 304	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:59:             out[n] += out[n-2] - (opus_int32)silk_RSHIFT_ROUND64( silk_SMULL( ftmp, out[n-1] ), QA );
	s32i.n	a15, a14, 8	# MEM[base: _745, offset: 8B], tmp633
	addi	a2, a14, -4	# ivtmp$34, ivtmp$34,
# @OPUS@\upstream\silk\NLSF2A.c:58:         for( n = k; n > 1; n-- ) {
	bne	a14, a6, .L43	# ivtmp$34,,
	j	.L28		#
.L63:
	l32i	a8, sp, 336	# %sfp,
	addi.n	a6, a9, -1	# _228, tmp7,
	addi.n	a3, a8, -1	# _222,,
	blti	a6, 2, .L64	# _228,,
	l32i	a9, sp, 192	# MEM[(int *)&Q], _559
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a2, sp, 248	# P, _471
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a4, sp, 244	# MEM[(int *)&P], MEM[(int *)&P]
	mov.n	a11, a8	#,
	add.n	a4, a2, a4	# Ptmp, _471, MEM[(int *)&P]
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a5, sp, 200	# Q, _455
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a9, a12	# tmp638, _559, tmp576
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a7, sp, 252	# P, _463
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a8, a4	# tmp639, tmp638, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a10, a3, 2	# tmp640, _222,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a9, a12, a9	# Qtmp, tmp576, _559
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a8, sp, 0	# a32_QA1, tmp639
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a2, a7, a2	# Ptmp, _463, _471
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a9, a9, a4	# tmp643, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a10, sp, a10	# tmp641,, tmp640
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a12, a5	# tmp647, tmp576, _455
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a11, -2	# tmp649,,
	s32i.n	a9, a10, 0	# a32_QA1, tmp643
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a8, a2	# tmp648, tmp647, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp650, tmp649,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a13, a5, a12	# Qtmp, _455, tmp576
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a8, sp, 4	# a32_QA1, tmp648
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp651,, tmp650
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a13, a2	# tmp653, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a2, a4, 0	# a32_QA1, tmp653
	blti	a6, 4, .L45	# _228,,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a2, sp, 204	# Q, _598
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a9, sp, 256	# P, _594
	mov.n	a12, a11	#,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a7, a7, a9	# Ptmp, _463, _594
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a5, a2	# tmp657, _455, _598
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a8, sp, 208	# Q, _613
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a12, -3	# tmp659,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a10, sp, 260	# P, _609
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a7	# tmp658, tmp657, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a5, a2, a5	# Qtmp, _598, _455
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp660, tmp659,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, sp, 8	# a32_QA1, tmp658
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a9, a10	# Ptmp, _594, _609
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a11, sp, a4	# tmp661,, tmp660
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a5, a7	# tmp663, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a12, -4	# tmp669,,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a2, a8	# tmp667, _598, _613
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a11, 0	# a32_QA1, tmp663
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a5, a9	# tmp668, tmp667, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp670, tmp669,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a2, a8, a2	# Qtmp, _613, _598
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a5, sp, 12	# a32_QA1, tmp668
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp671,, tmp670
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a2, a9	# tmp673, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a2, a4, 0	# a32_QA1, tmp673
	blti	a6, 6, .L46	# _228,,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a2, sp, 212	# Q, _634
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a7, sp, 264	# P, _630
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a8, a2	# tmp677, _613, _634
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a10, a10, a7	# Ptmp, _609, _630
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a4, sp, 216	# Q, _649
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a5, a12, -5	# tmp679,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a9, sp, 268	# P, _645
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a10	# tmp678, tmp677, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a8, a2, a8	# Qtmp, _634, _613
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp680, tmp679,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, sp, 16	# a32_QA1, tmp678
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a7, a7, a9	# Ptmp, _630, _645
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a11, sp, a5	# tmp681,, tmp680
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a8, a10	# tmp683, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a5, a12, -6	# tmp689,,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a2, a4	# tmp687, _634, _649
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp683
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a8, a8, a7	# tmp688, tmp687, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp690, tmp689,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a2, a4, a2	# Qtmp, _649, _634
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a8, sp, 20	# a32_QA1, tmp688
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp691,, tmp690
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a2, a7	# tmp693, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a2, a5, 0	# a32_QA1, tmp693
	blti	a6, 8, .L47	# _228,,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a2, sp, 220	# Q, _670
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a8, sp, 272	# P, _666
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a4, a2	# tmp697, _649, _670
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a9, a8	# Ptmp, _645, _666
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a5, sp, 224	# Q, _685
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a7, a12, -7	# tmp699,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a10, sp, 276	# P, _681
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a9	# tmp698, tmp697, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a4, a2, a4	# Qtmp, _670, _649
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a7, a7, 2	# tmp700, tmp699,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, sp, 24	# a32_QA1, tmp698
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a8, a10	# Ptmp, _666, _681
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a7, sp, a7	# tmp701,, tmp700
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a9, a4, a9	# tmp703, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a2, a5	# tmp707, _670, _685
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a12, -8	# tmp709,,
	s32i.n	a9, a7, 0	# a32_QA1, tmp703
	slli	a4, a4, 2	# tmp710, tmp709,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a11, a8	# tmp708, tmp707, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a2, a5, a2	# Qtmp, _685, _670
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a2, a8	# tmp713, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, sp, 28	# a32_QA1, tmp708
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp711,, tmp710
	s32i.n	a2, a4, 0	# a32_QA1, tmp713
	movi.n	a2, 9	# tmp714,
	bge	a2, a6, .L48	# tmp714, _228,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a2, sp, 228	# Q, _706
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a8, sp, 280	# P, _702
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a5, a2	# tmp718, _685, _706
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a10, a10, a8	# Ptmp, _681, _702
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a7, sp, 232	# Q, _721
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a12, -9	# tmp720,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a9, sp, 284	# P, _717
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a10	# tmp719, tmp718, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a5, a2, a5	# Qtmp, _706, _685
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp721, tmp720,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, sp, 32	# a32_QA1, tmp719
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a8, a9	# Ptmp, _702, _717
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a11, sp, a4	# tmp722,, tmp721
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a5, a10	# tmp724, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a4, a12, -10	# tmp730,,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a2, a7	# tmp728, _706, _721
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp724
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a5, a8	# tmp729, tmp728, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp731, tmp730,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a2, a7, a2	# Qtmp, _721, _706
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a2, a8	# tmp734, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a5, sp, 36	# a32_QA1, tmp729
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp732,, tmp731
	s32i.n	a2, a4, 0	# a32_QA1, tmp734
	movi.n	a2, 0xb	# tmp735,
	bge	a2, a6, .L49	# tmp735, _228,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a6, sp, 236	# Q, _28
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a5, sp, 288	# P, _26
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a4, sp, 240	# Q, _524
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a5, a9	# Ptmp, _26, _717
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a7, a6	# tmp739, _721, _28
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a8, a12, -11	# tmp741,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i	a10, sp, 292	# P, P
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a2, a9	# tmp740, tmp739, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _28, _721
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a8, a8, 2	# tmp742, tmp741,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a2, sp, 40	# a32_QA1, tmp740
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a5, a5, a10	# Ptmp, _26, P
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a9, a7, a9	# tmp745, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a8, sp, a8	# tmp743,, tmp742
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a6, a4	# tmp750, _28, _524
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	addi	a2, a12, -12	# tmp752,,
	s32i.n	a9, a8, 0	# a32_QA1, tmp745
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a5	# tmp751, tmp750, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a2, a2, 2	# tmp753, tmp752,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a4, a4, a6	# Qtmp, _524, _28
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a2, sp, a2	# tmp754,, tmp753
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, sp, 44	# a32_QA1, tmp751
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a4, a5	# tmp756, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a4, a2, 0	# a32_QA1, tmp756
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi.n	a2, 0xc	# _563,
	j	.L29		#
.L45:
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi.n	a2, 2	# _563,
	j	.L29		#
.L46:
	movi.n	a2, 4	# _563,
	j	.L29		#
.L47:
	movi.n	a2, 6	# _563,
	j	.L29		#
.L48:
	movi.n	a2, 8	# _563,
	j	.L29		#
.L49:
	movi.n	a2, 0xa	# _563,
.L29:
	addi.n	a5, a2, 1	# _554, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a6, 0xf4	#,
	add.n	a6, a6, sp	#,,
	slli	a8, a5, 2	# tmp760, _554,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	slli	a4, a2, 2	# tmp765, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a6, a8	# tmp761,, tmp760
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a12, sp, a4	# tmp773,, tmp765
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a8, sp, a8	# tmp769,, tmp760
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a4, a6, a4	# tmp766,, tmp765
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a7, a12, 192	# Q, _424
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	l32i	a6, a8, 192	# Q, _423
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a10, a9, 0	# P, _555
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a9, a4, 0	# P, tmp767
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a7, a6	# tmp778, _424, _423
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a10, a9	# Ptmp, _555, tmp767
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a2	# tmp780, _222, _563
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a9	# tmp779, tmp778, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp781, tmp780,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _423, _424
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a9	# tmp784, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, a12, 0	# a32_QA1, tmp779
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp782,, tmp781
	s32i.n	a7, a4, 0	# a32_QA1, tmp784
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a7, sp, 332	# %sfp,
	bge	a5, a7, .L30	# _554,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a4, a2, 2	# _322, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a11, 0xf4	#,
	slli	a12, a4, 2	# tmp788, _322,
	add.n	a11, a11, sp	#,,
	add.n	a9, a11, a12	# tmp789,, tmp788
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a12, sp, a12	# tmp791,, tmp788
	l32i	a7, a12, 192	# Q, _318
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a9, a9, 0	# P, _321
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a6, a7	# tmp796, _423, _318
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a10, a9, a10	# Ptmp, _321, _555
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a3, a5	# tmp798, _222, _554
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a10	# tmp797, tmp796, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp799, tmp798,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a6, a7, a6	# Qtmp, _318, _423
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a6, a6, a10	# tmp802, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, a8, 0	# a32_QA1, tmp797
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp800,, tmp799
	s32i.n	a6, a5, 0	# a32_QA1, tmp802
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a6, sp, 332	# %sfp,
	bge	a4, a6, .L30	# _322,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a5, a2, 3	# _307, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a10, 0xf4	#,
	slli	a11, a5, 2	# tmp806, _307,
	add.n	a10, a10, sp	#,,
	add.n	a8, a10, a11	# tmp807,, tmp806
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a11, sp, a11	# tmp809,, tmp806
	l32i	a6, a11, 192	# Q, _303
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a8, a8, 0	# P, _306
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a7, a6	# tmp814, _318, _303
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a8, a9	# Ptmp, _306, _321
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a4	# tmp816, _222, _322
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a9	# tmp815, tmp814, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp817, tmp816,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _303, _318
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a12, 0	# a32_QA1, tmp815
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp818,, tmp817
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a9	# tmp820, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a4, 0	# a32_QA1, tmp820
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a5, a12, .L30	# _307,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a4, a2, 4	# _292, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a7, 0xf4	#,
	slli	a12, a4, 2	# tmp824, _292,
	add.n	a7, a7, sp	#,,
	add.n	a9, a7, a12	# tmp825,, tmp824
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a12, sp, a12	# tmp827,, tmp824
	l32i	a7, a12, 192	# Q, _288
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a9, a9, 0	# P, _291
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a6, a7	# tmp832, _303, _288
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a9, a8	# Ptmp, _291, _306
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a3, a5	# tmp834, _222, _307
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a8	# tmp833, tmp832, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp835, tmp834,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a6, a7, a6	# Qtmp, _288, _303
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a6, a6, a8	# tmp838, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp833
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp836,, tmp835
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a6, a5, 0	# a32_QA1, tmp838
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a4, a8, .L30	# _292,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a5, a2, 5	# _277, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a10, 0xf4	#,
	slli	a11, a5, 2	# tmp842, _277,
	add.n	a10, a10, sp	#,,
	add.n	a8, a10, a11	# tmp843,, tmp842
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a11, sp, a11	# tmp845,, tmp842
	l32i	a6, a11, 192	# Q, _273
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a8, a8, 0	# P, _276
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a7, a6	# tmp850, _288, _273
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a8, a9	# Ptmp, _276, _291
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a4	# tmp852, _222, _292
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a9	# tmp851, tmp850, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp853, tmp852,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _273, _288
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a12, 0	# a32_QA1, tmp851
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp854,, tmp853
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a9	# tmp856, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a4, 0	# a32_QA1, tmp856
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a5, a12, .L30	# _277,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a4, a2, 6	# _262, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a7, 0xf4	#,
	slli	a12, a4, 2	# tmp860, _262,
	add.n	a7, a7, sp	#,,
	add.n	a9, a7, a12	# tmp861,, tmp860
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a12, sp, a12	# tmp863,, tmp860
	l32i	a7, a12, 192	# Q, _258
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a9, a9, 0	# P, _261
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a6, a7	# tmp868, _273, _258
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a9, a8	# Ptmp, _261, _276
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a3, a5	# tmp870, _222, _277
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a8	# tmp869, tmp868, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp871, tmp870,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a6, a7, a6	# Qtmp, _258, _273
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a6, a6, a8	# tmp874, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp869
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp872,, tmp871
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a6, a5, 0	# a32_QA1, tmp874
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a4, a8, .L30	# _262,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a5, a2, 7	# _247, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a10, 0xf4	#,
	slli	a11, a5, 2	# tmp878, _247,
	add.n	a10, a10, sp	#,,
	add.n	a8, a10, a11	# tmp879,, tmp878
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a11, sp, a11	# tmp881,, tmp878
	l32i	a6, a11, 192	# Q, _243
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a8, a8, 0	# P, _246
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a7, a6	# tmp886, _258, _243
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a8, a9	# Ptmp, _246, _261
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a4	# tmp888, _222, _262
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a9	# tmp887, tmp886, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp889, tmp888,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _243, _258
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a12, 0	# a32_QA1, tmp887
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp890,, tmp889
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a9	# tmp892, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a4, 0	# a32_QA1, tmp892
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a5, a12, .L30	# _247,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a4, a2, 8	# _209, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a7, 0xf4	#,
	slli	a12, a4, 2	# tmp896, _209,
	add.n	a7, a7, sp	#,,
	add.n	a9, a7, a12	# tmp897,, tmp896
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a12, sp, a12	# tmp899,, tmp896
	l32i	a7, a12, 192	# Q, _185
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a9, a9, 0	# P, _208
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a6, a7	# tmp904, _243, _185
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a9, a8	# Ptmp, _208, _246
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a3, a5	# tmp906, _222, _247
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a8	# tmp905, tmp904, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp907, tmp906,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a6, a7, a6	# Qtmp, _185, _243
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a6, a6, a8	# tmp910, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp905
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp908,, tmp907
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a6, a5, 0	# a32_QA1, tmp910
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a4, a8, .L30	# _209,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a5, a2, 9	# _47, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a10, 0xf4	#,
	slli	a11, a5, 2	# tmp914, _47,
	add.n	a10, a10, sp	#,,
	add.n	a8, a10, a11	# tmp915,, tmp914
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a11, sp, a11	# tmp917,, tmp914
	l32i	a6, a11, 192	# Q, _552
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a8, a8, 0	# P, _32
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a7, a6	# tmp922, _185, _552
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a9, a8, a9	# Ptmp, _32, _208
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a4	# tmp924, _222, _209
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a9	# tmp923, tmp922, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp925, tmp924,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a6, a7	# Qtmp, _552, _185
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a12, 0	# a32_QA1, tmp923
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp926,, tmp925
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a9	# tmp928, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a4, 0	# a32_QA1, tmp928
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a5, a12, .L30	# _47,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a4, a2, 10	# _533, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a7, 0xf4	#,
	slli	a9, a4, 2	# tmp1092, _533,
	add.n	a7, a7, sp	#,,
	add.n	a10, a7, a9	# tmp933,, tmp1092
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a7, sp, a9	# tmp935,, tmp1092
	l32i	a7, a7, 192	# Q, _532
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a12, a10, 0	# P, _527
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a3, a5	# tmp942, _222, _47
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a8, a8, a12	# Ptmp, _32, _527
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a6, a7	# tmp940, _552, _532
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a10, a10, a8	# tmp941, tmp940, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a5, a5, 2	# tmp943, tmp942,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a6, a7, a6	# Qtmp, _532, _552
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a6, a6, a8	# tmp946, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a10, a11, 0	# a32_QA1, tmp941
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a5, sp, a5	# tmp944,, tmp943
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a8, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a6, a5, 0	# a32_QA1, tmp946
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a4, a8, .L30	# _533,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a5, a2, 11	# _504, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a11, 0xf4	#,
	slli	a6, a5, 2	# tmp950, _504,
	add.n	a11, a11, sp	#,,
	add.n	a10, a11, a6	# tmp951,, tmp950
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a6, sp, a6	# tmp953,, tmp950
	l32i	a8, a6, 192	# Q, _498
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a10, a10, 0	# P, _505
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a7, a8	# tmp958, _532, _498
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a12, a10, a12	# Ptmp, _505, _527
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a4, a3, a4	# tmp960, _222, _533
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a11, a11, a12	# tmp959, tmp958, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	add.n	a9, sp, a9	# tmp957,, tmp1092
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a4, a4, 2	# tmp961, tmp960,
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a7, a8, a7	# Qtmp, _498, _532
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a7, a12	# tmp964, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a11, a9, 0	# a32_QA1, tmp959
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a4, sp, a4	# tmp962,, tmp961
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	l32i	a12, sp, 332	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a7, a4, 0	# a32_QA1, tmp964
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bge	a5, a12, .L30	# _504,,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	addi.n	a2, a2, 12	# _576, _563,
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	movi	a4, 0xf4	#,
	slli	a2, a2, 2	# tmp968, _576,
	add.n	a4, a4, sp	#,,
	add.n	a7, a4, a2	# tmp969,, tmp968
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	add.n	a2, sp, a2	# tmp972,, tmp968
	l32i	a4, a2, 192	# Q, _572
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	l32i.n	a2, a7, 0	# P, tmp970
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a7, a8, a4	# tmp977, _498, _572
# @OPUS@\upstream\silk\NLSF2A.c:121:         Ptmp = P[ k+1 ] + P[ k ];
	add.n	a10, a10, a2	# Ptmp, _505, tmp970
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a2, a3, a5	# tmp979, _222, _504
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	slli	a2, a2, 2	# tmp980, tmp979,
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	sub	a5, a7, a10	# tmp978, tmp977, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:122:         Qtmp = Q[ k+1 ] - Q[ k ];
	sub	a3, a4, a8	# Qtmp, _572, _498
# @OPUS@\upstream\silk\NLSF2A.c:125:         a32_QA1[ k ]     = -Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a5, a6, 0	# a32_QA1, tmp978
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	add.n	a2, sp, a2	# tmp981,, tmp980
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	sub	a3, a3, a10	# tmp983, Qtmp, Ptmp
# @OPUS@\upstream\silk\NLSF2A.c:126:         a32_QA1[ d-k-1 ] =  Qtmp - Ptmp;        /* QA+1 */
	s32i.n	a3, a2, 0	# a32_QA1, tmp983
.L30:
# @OPUS@\upstream\silk\NLSF2A.c:130:     silk_LPC_fit( a_Q12, a32_QA1, 12, QA + 1, d );
	l32i	a6, sp, 336	# %sfp,
	l32i	a2, sp, 344	# %sfp,
	movi.n	a5, 0x11	#,
	movi.n	a4, 0xc	#,
	mov.n	a3, sp	#,
	call0	silk_LPC_fit		#
	l32i	a7, sp, 336	# %sfp,
	l32i	a8, sp, 344	# %sfp,
	slli	a12, a7, 1	# tmp984,,
	add.n	a12, a12, a8	# _736, tmp984,
# @OPUS@\upstream\silk\NLSF2A.c:132:     for( i = 0; silk_LPC_inverse_pred_gain( a_Q12, d, arch ) == 0 && i < MAX_LPC_STABILIZE_ITERATIONS; i++ ) {
	movi.n	a13, 0	# i,
	mov.n	a15, a8	# a_Q12,
	mov.n	a14, a7	# d,
# @OPUS@\upstream\silk\NLSF2A.c:132:     for( i = 0; silk_LPC_inverse_pred_gain( a_Q12, d, arch ) == 0 && i < MAX_LPC_STABILIZE_ITERATIONS; i++ ) {
	j	.L31		#
.L35:
# @OPUS@\upstream\silk\NLSF2A.c:135:         silk_bwexpander_32( a32_QA1, d, 65536 - silk_LSHIFT( 2, i ) );
	l32r	a9, .LC2	#,
# @OPUS@\upstream\silk\NLSF2A.c:135:         silk_bwexpander_32( a32_QA1, d, 65536 - silk_LSHIFT( 2, i ) );
	movi.n	a4, 2	# tmp985,
	ssl	a13	# i
	sll	a4, a4	# tmp986, tmp985
# @OPUS@\upstream\silk\NLSF2A.c:135:         silk_bwexpander_32( a32_QA1, d, 65536 - silk_LSHIFT( 2, i ) );
	sub	a4, a9, a4	#,, tmp986
	mov.n	a3, a14	#, d
	mov.n	a2, sp	#,
	call0	silk_bwexpander_32		#
	mov.n	a4, sp	# ivtmp$24,
# @OPUS@\upstream\silk\NLSF2A.c:136:         for( k = 0; k < d; k++ ) {
	mov.n	a3, a15	# ivtmp$25, a_Q12
	bgei	a14, 1, .L33	# d,,
.L34:
# @OPUS@\upstream\silk\NLSF2A.c:132:     for( i = 0; silk_LPC_inverse_pred_gain( a_Q12, d, arch ) == 0 && i < MAX_LPC_STABILIZE_ITERATIONS; i++ ) {
	addi.n	a13, a13, 1	# i, i,
	j	.L31		#
.L33:
# @OPUS@\upstream\silk\NLSF2A.c:137:             a_Q12[ k ] = (opus_int16)silk_RSHIFT_ROUND( a32_QA1[ k ], QA + 1 - 12 );            /* QA+1 -> Q12 */
	l32i.n	a2, a4, 0	# MEM[base: _492, offset: 0B], MEM[base: _492, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$24, ivtmp$24,
	srai	a2, a2, 4	# tmp989, MEM[base: _492, offset: 0B],
	addi.n	a2, a2, 1	# tmp991, tmp989,
	srai	a2, a2, 1	# tmp992, tmp991,
# @OPUS@\upstream\silk\NLSF2A.c:137:             a_Q12[ k ] = (opus_int16)silk_RSHIFT_ROUND( a32_QA1[ k ], QA + 1 - 12 );            /* QA+1 -> Q12 */
	s16i	a2, a3, 0	# MEM[base: _732, offset: 0B], tmp992
	addi.n	a3, a3, 2	# ivtmp$25, ivtmp$25,
# @OPUS@\upstream\silk\NLSF2A.c:136:         for( k = 0; k < d; k++ ) {
	bne	a3, a12, .L33	# ivtmp$25, _736,
	j	.L34		#
.L31:
# @OPUS@\upstream\silk\NLSF2A.c:132:     for( i = 0; silk_LPC_inverse_pred_gain( a_Q12, d, arch ) == 0 && i < MAX_LPC_STABILIZE_ITERATIONS; i++ ) {
	mov.n	a3, a14	#, d
	mov.n	a2, a15	#, a_Q12
	call0	silk_LPC_inverse_pred_gain_c		#
# @OPUS@\upstream\silk\NLSF2A.c:132:     for( i = 0; silk_LPC_inverse_pred_gain( a_Q12, d, arch ) == 0 && i < MAX_LPC_STABILIZE_ITERATIONS; i++ ) {
	beqi	a13, 16, .L1	# i,,
	beqz.n	a2, .L35	# _46,
	j	.L1		#
.L60:
# @OPUS@\upstream\silk\NLSF2A.c:53:     out[0] = silk_LSHIFT( 1, QA );
	s32i	a7, sp, 192	# MEM[(opus_int32 *)&Q], tmp10
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	s32i	a2, sp, 196	# MEM[(opus_int32 *)&Q + 4B], tmp11
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	bnei	a6, 1, .L30	# tmp12,,
	j	.L37		#
.L61:
	movi	a9, 0xc0	#,
# @OPUS@\upstream\silk\NLSF2A.c:53:     out[0] = silk_LSHIFT( 1, QA );
	l32r	a7, .LC2	#,
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	l32i	a8, sp, 348	# %sfp,
	add.n	a9, a9, sp	#,,
	movi	a10, 0xc0	#,
# @OPUS@\upstream\silk\NLSF2A.c:55:     for( k = 1; k < dd; k++ ) {
	movi.n	a6, 1	#,
	addi	a9, a9, -8	#,,
	add.n	a10, a10, sp	#,,
	s32i	a6, sp, 308	# %sfp,
# @OPUS@\upstream\silk\NLSF2A.c:53:     out[0] = silk_LSHIFT( 1, QA );
	s32i	a7, sp, 192	# MEM[(opus_int32 *)&Q],
# @OPUS@\upstream\silk\NLSF2A.c:54:     out[1] = -cLSF[0];
	s32i	a8, sp, 196	# MEM[(opus_int32 *)&Q + 4B],
	s32i	a9, sp, 312	# %sfp,
	s32i	a10, sp, 304	# %sfp,
	j	.L20		#
.L37:
	l32i	a11, sp, 336	# %sfp,
	addi.n	a3, a11, -1	# _222,,
.L64:
# @OPUS@\upstream\silk\NLSF2A.c:120:     for( k = 0; k < dd; k++ ) {
	movi.n	a2, 0	# _563,
	j	.L29		#
.L1:
# @OPUS@\upstream\silk\NLSF2A.c:140: }
	l32i	a0, sp, 396	#,
	movi	a9, 0x190	#,
	l32i	a12, sp, 392	#,
	l32i	a13, sp, 388	#,
	l32i	a14, sp, 384	#,
	l32i	a15, sp, 380	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_NLSF2A, .-silk_NLSF2A
	.section	.rodata.ordering10$3186,"a"
	.align	4
	.type	ordering10$3186, @object
	.size	ordering10$3186, 10
ordering10$3186:
	.byte	0
	.byte	9
	.byte	6
	.byte	3
	.byte	4
	.byte	5
	.byte	8
	.byte	1
	.byte	2
	.byte	7
	.section	.rodata.ordering16$3185,"a"
	.align	4
	.type	ordering16$3185, @object
	.size	ordering16$3185, 16
ordering16$3185:
	.byte	0
	.byte	15
	.byte	8
	.byte	7
	.byte	4
	.byte	11
	.byte	12
	.byte	3
	.byte	2
	.byte	13
	.byte	10
	.byte	5
	.byte	6
	.byte	9
	.byte	14
	.byte	1
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
