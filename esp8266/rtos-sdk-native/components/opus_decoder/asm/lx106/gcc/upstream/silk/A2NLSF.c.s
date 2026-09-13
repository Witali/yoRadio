# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/A2NLSF.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"A2NLSF.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\A2NLSF.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\A2NLSF.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\A2NLSF.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\A2NLSF.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\A2NLSF.c.s.raw
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
	.section	.text.silk_A2NLSF,"ax",@progbits
	.literal_position
	.literal .LC0, 65536
	.literal .LC1, 1073741822
	.literal .LC2, silk_LSFCosTab_FIX_Q12
	.literal .LC4, 65535
	.literal .LC5, 131070
	.literal .LC6, 32767
	.literal .LC7, 32768
	.align	4
	.global	silk_A2NLSF
	.type	silk_A2NLSF, @function
# Function: silk_A2NLSF
# Module: upstream/silk/A2NLSF.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Compute Normalized Line Spectral Frequencies (NLSFs) from whitening filter coefficients      */
# C context: /* If not all roots are found, the a_Q16 coefficients are bandwidth expanded until convergence. */
# C context: void silk_A2NLSF(
# C context: opus_int16                  *NLSF,              /* O    Normalized Line Spectral Frequencies in Q15 (0..2^15-1) [d] */
# C context: opus_int32                  *a_Q16,             /* I/O  Monic whitening filter coefficients in Q16 [d]              */
# C context: const opus_int              d                   /* I    Filter order (must be even)                                 */
# C context: )
silk_A2NLSF:
	movi	a9, 0x130	#,
	sub	sp, sp, a9	#,,
	s32i	a15, sp, 284	#,
# @OPUS@\upstream\silk\A2NLSF.c:146:     dd = silk_RSHIFT( d, 1 );
	srai	a15, a4, 1	# dd, d,
# @OPUS@\upstream\silk\A2NLSF.c:143:     PQ[ 0 ] = P;
	addi	a5, sp, 52	#,,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	slli	a6, a15, 2	#, dd,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	l32r	a10, .LC0	#,
# @OPUS@\upstream\silk\A2NLSF.c:132: {
	s32i	a0, sp, 300	#,
	s32i	a12, sp, 296	#,
	s32i	a13, sp, 292	#,
	s32i	a14, sp, 288	#,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	add.n	a7, a5, a6	#, tmp7,
# @OPUS@\upstream\silk\A2NLSF.c:106:     Q[dd] = silk_LSHIFT( 1, 16 );
	add.n	a8, sp, a6	#,,
# @OPUS@\upstream\silk\A2NLSF.c:132: {
	s32i	a4, sp, 180	# %sfp, d
# @OPUS@\upstream\silk\A2NLSF.c:143:     PQ[ 0 ] = P;
	s32i	a5, sp, 112	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	s32i	a6, sp, 200	# %sfp,
	s32i	a7, sp, 188	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:106:     Q[dd] = silk_LSHIFT( 1, 16 );
	s32i	a8, sp, 208	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:143:     PQ[ 0 ] = P;
	s32i	a5, sp, 104	# PQ, tmp9
# @OPUS@\upstream\silk\A2NLSF.c:144:     PQ[ 1 ] = Q;
	s32i	sp, sp, 108	# PQ,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	s32i.n	a10, a7, 0	# *_265,
# @OPUS@\upstream\silk\A2NLSF.c:106:     Q[dd] = silk_LSHIFT( 1, 16 );
	s32i.n	a10, a8, 0	# *_266,
# @OPUS@\upstream\silk\A2NLSF.c:132: {
	s32i	a2, sp, 204	# %sfp, NLSF
	s32i	a3, sp, 192	# %sfp, a_Q16
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	bgei	a15, 1, .L2	# dd,,
	j	.L3		#
.L186:
	l32i	a7, sp, 188	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	blti	a15, 2, .L3	# dd,,
	j	.L4		#
.L2:
	mov.n	a5, a3	#, a_Q16
	addi	a3, a6, -4	# _1407, tmp11,
	add.n	a8, a5, a6	# ivtmp$261,, tmp11
	add.n	a4, a5, a3	# ivtmp$259,, _1407
	mov.n	a7, sp	# ivtmp$263,
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	addi	a6, sp, 52	# ivtmp$262,,
	mov.n	a11, a5	# a_Q16,
	j	.L5		#
.L108:
	mov.n	a4, a10	# ivtmp$259, ivtmp$259
.L5:
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	l32i.n	a2, a8, 0	# MEM[base: _1372, offset: 0B], _279
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	l32i.n	a9, a4, 0	# MEM[base: _1373, offset: 0B], _273
	addi	a10, a4, -4	# ivtmp$259, ivtmp$259,
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	add.n	a5, a9, a2	# tmp1040, _273, _279
	neg	a5, a5	# tmp1041, tmp1040
# @OPUS@\upstream\silk\A2NLSF.c:109:         Q[ k ] = -a_Q16[ dd - k - 1 ] + a_Q16[ dd + k ];    /* Q16 */
	sub	a2, a2, a9	# tmp1042, _279, _273
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	s32i.n	a5, a6, 0	# MEM[base: _1371, offset: 0B], tmp1041
# @OPUS@\upstream\silk\A2NLSF.c:109:         Q[ k ] = -a_Q16[ dd - k - 1 ] + a_Q16[ dd + k ];    /* Q16 */
	s32i.n	a2, a7, 0	# MEM[base: _1370, offset: 0B], tmp1042
	addi.n	a8, a8, 4	# ivtmp$261, ivtmp$261,
	addi.n	a6, a6, 4	# ivtmp$262, ivtmp$262,
	addi.n	a7, a7, 4	# ivtmp$263, ivtmp$263,
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	bne	a11, a4, .L108	# a_Q16, ivtmp$259,
	l32i	a7, sp, 200	# %sfp,
	addi	a6, sp, 52	#,,
	l32i	a8, sp, 208	# %sfp,
	add.n	a2, a6, a7	# tmp1045,,
	l32i.n	a4, a2, 0	# *_2217, D__lsm0$26
	l32i.n	a5, a8, 0	# *_2222, D__lsm0$25
	add.n	a2, a6, a3	# ivtmp$250,, _1407
	l32i	a9, sp, 112	# %sfp,
	add.n	a3, sp, a3	# ivtmp$252,, _1407
	j	.L6		#
.L109:
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	mov.n	a2, a6	# ivtmp$250, ivtmp$250
.L6:
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	l32i.n	a6, a3, 0	# MEM[base: _1396, offset: 0B], MEM[base: _1396, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	l32i.n	a7, a2, 0	# MEM[base: _1398, offset: 0B], MEM[base: _1398, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	add.n	a5, a5, a6	# D__lsm0$25, D__lsm0$25, MEM[base: _1396, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	sub	a4, a7, a4	# D__lsm0$26, MEM[base: _1398, offset: 0B], D__lsm0$26
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	s32i.n	a5, a3, 0	# MEM[base: _1396, offset: 0B], D__lsm0$25
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	s32i.n	a4, a2, 0	# MEM[base: _1398, offset: 0B], D__lsm0$26
	addi	a6, a2, -4	# ivtmp$250, ivtmp$250,
	addi	a3, a3, -4	# ivtmp$252, ivtmp$252,
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	bne	a9, a2, .L109	#, ivtmp$250,
	j	.L186		#
.L154:
	mov.n	a10, a12	# _265, _265
	l32i.n	a8, a11, 0	# MEM[(opus_int32 *)_265 + 4294967292B(OVF)], D__lsm1$30
	l32i.n	a9, a12, 0	# *_265, D__lsm0$29
	mov.n	a2, a15	# n, dd
	mov.n	a12, a15	# dd, dd
	mov.n	a4, a13	# ivtmp$235, ivtmp$235
	s32i	a11, sp, 120	# %sfp, tmp1757
	mov.n	a15, a10	# _265, _265
.L8:
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	l32i.n	a11, a4, 4	# MEM[base: _1425, offset: 4B],
	addi	a10, a2, -3	# tmp1053, _1434,
	sub	a9, a11, a9	# D__lsm0$29,, D__lsm0$29
	l32i.n	a11, a4, 0	# MEM[base: _1425, offset: 0B],
	s32i.n	a9, a4, 4	# MEM[base: _1425, offset: 4B], D__lsm0$29
	sub	a8, a11, a8	# D__lsm1$30,, D__lsm1$30
	s32i.n	a8, a4, 0	# MEM[base: _1425, offset: 0B], D__lsm1$30
	addi	a2, a2, -2	# n, n,
	addi	a4, a4, -8	# ivtmp$235, ivtmp$235,
	blt	a7, a10, .L8	# k, tmp1053,
	mov.n	a4, a15	# _265, _265
	l32i	a11, sp, 120	# %sfp, tmp1757
	mov.n	a15, a12	# dd, dd
	mov.n	a12, a4	# _265, _265
.L22:
	l32i	a8, sp, 116	# %sfp,
	addi	a9, sp, 52	#,,
	add.n	a4, a2, a8	# tmp1055, n,
	slli	a4, a4, 2	# tmp1057, tmp1055,
	add.n	a4, a9, a4	# ivtmp$226,, tmp1057
.L9:
	l32i.n	a8, a4, 0	# MEM[base: _1452, offset: 0B], MEM[base: _1452, offset: 0B]
	l32i.n	a9, a4, 8	# MEM[base: _1452, offset: 8B], MEM[base: _1452, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	addi.n	a2, a2, -1	# n, n,
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	sub	a8, a8, a9	# tmp1058, MEM[base: _1452, offset: 0B], MEM[base: _1452, offset: 8B]
	s32i.n	a8, a4, 0	# MEM[base: _1452, offset: 0B], tmp1058
	addi	a4, a4, -4	# ivtmp$226, ivtmp$226,
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	blt	a3, a2, .L9	# k, n,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a3, a5, 8	# MEM[base: _1417, offset: 8B], MEM[base: _1417, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a2, a5, 0	# MEM[base: _1417, offset: 0B], MEM[base: _1417, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a3, a3, 1	# tmp1061, MEM[base: _1417, offset: 8B],
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a2, a2, a3	# tmp1063, MEM[base: _1417, offset: 0B], tmp1061
	s32i.n	a2, a5, 0	# MEM[base: _1417, offset: 0B], tmp1063
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	mov.n	a3, a7	# k, k
	addi.n	a5, a5, 4	# ivtmp$243, ivtmp$243,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	blt	a7, a14, .L10	# k, _2022,
	j	.L187		#
.L14:
	slli	a4, a3, 2	# _1749, k,
	addi	a10, sp, 52	#,,
	add.n	a2, a10, a4	# _1748,, _1749
	addi	a7, a2, -8	# tmp1067, _1748,
	addi	a5, a2, -4	# tmp1069, _1748,
	addi	a4, a4, -8	# tmp1071, _1749,
	l32i.n	a2, a7, 0	# MEM[(opus_int32 *)_1748 + 4294967288B], D__lsm0$43
	l32i.n	a7, a5, 0	# MEM[(opus_int32 *)_1748 + 4294967292B], D__lsm1$44
	add.n	a4, a10, a4	# ivtmp$218,, tmp1071
.L12:
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a5, a4, 8	# MEM[base: _1473, offset: 8B], _2035
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a3, a3, 1	# k, k,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a8, a5, 1	# tmp1072, _2035,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a2, a2, a8	# tmp1073, D__lsm0$43, tmp1072
	s32i.n	a2, a4, 0	# MEM[base: _1473, offset: 0B], tmp1073
	mov.n	a2, a7	# D__lsm0$43, D__lsm1$44
	addi.n	a4, a4, 4	# ivtmp$218, ivtmp$218,
	mov.n	a7, a5	# D__lsm1$44, _2035
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	bge	a15, a3, .L12	# dd, k,
	j	.L13		#
.L187:
	bge	a15, a7, .L14	# dd, k,
.L13:
	bgei	a15, 3, .L15	# dd,,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a3, 2	# k,
	j	.L16		#
.L4:
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a3, 2	# k,
	addi.n	a6, a15, -1	# _278, dd,
	blti	a15, 3, .L14	# dd,,
	addi.n	a14, a15, 1	# _2022, dd,
	bge	a15, a14, .L17	# dd, _2022,
	mov.n	a14, a15	# _2022, dd
.L17:
	l32i	a11, sp, 200	# %sfp,
	l32r	a12, .LC1	#, tmp1729
	l32i	a7, sp, 188	# %sfp,
	addi	a13, a11, -12	# tmp1076,,
	addi	a5, sp, 52	# ivtmp$243,,
	s32i	a12, sp, 116	# %sfp, tmp1729
	add.n	a13, a5, a13	# ivtmp$235, ivtmp$243, tmp1076
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a3, 2	# k,
	addi.n	a6, a15, -1	# _278, dd,
	addi	a11, a7, -4	# tmp1757,,
	mov.n	a12, a7	# _265,
.L10:
	addi.n	a7, a3, 1	# k, k,
	blt	a6, a3, .L125	# _278, k,
	blt	a7, a6, .L154	# k, _278,
.L125:
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	mov.n	a2, a15	# n, dd
	j	.L22		#
.L155:
	l32i.n	a9, a13, 0	# *_266, D__lsm0$27
	l32i.n	a8, a11, 0	# MEM[(opus_int32 *)_266 + 4294967292B(OVF)], D__lsm1$28
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	mov.n	a2, a15	# n, dd
	s32i	a15, sp, 120	# %sfp, dd
	mov.n	a4, a12	# ivtmp$203, ivtmp$203
	mov.n	a15, a3	# k, k
.L23:
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	l32i.n	a10, a4, 4	# MEM[base: _1505, offset: 4B],
	addi	a3, a2, -3	# tmp1087, _1514,
	sub	a9, a10, a9	# D__lsm0$27,, D__lsm0$27
	l32i.n	a10, a4, 0	# MEM[base: _1505, offset: 0B],
	s32i.n	a9, a4, 4	# MEM[base: _1505, offset: 4B], D__lsm0$27
	sub	a8, a10, a8	# D__lsm1$28,, D__lsm1$28
	s32i.n	a8, a4, 0	# MEM[base: _1505, offset: 0B], D__lsm1$28
	addi	a2, a2, -2	# n, n,
	addi	a4, a4, -8	# ivtmp$203, ivtmp$203,
	blt	a7, a3, .L23	# k, tmp1087,
	mov.n	a3, a15	# k, k
	l32i	a15, sp, 120	# %sfp, dd
.L34:
	l32i	a8, sp, 116	# %sfp,
	add.n	a4, a2, a8	# tmp1088, n,
	slli	a4, a4, 2	# tmp1090, tmp1088,
	add.n	a4, sp, a4	# ivtmp$194,, tmp1090
.L24:
	l32i.n	a8, a4, 0	# MEM[base: _1522, offset: 0B], MEM[base: _1522, offset: 0B]
	l32i.n	a9, a4, 8	# MEM[base: _1522, offset: 8B], MEM[base: _1522, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	addi.n	a2, a2, -1	# n, n,
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	sub	a8, a8, a9	# tmp1091, MEM[base: _1522, offset: 0B], MEM[base: _1522, offset: 8B]
	s32i.n	a8, a4, 0	# MEM[base: _1522, offset: 0B], tmp1091
	addi	a4, a4, -4	# ivtmp$194, ivtmp$194,
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	blt	a3, a2, .L24	# k, n,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a3, a5, 8	# MEM[base: _1494, offset: 8B], MEM[base: _1494, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a2, a5, 0	# MEM[base: _1494, offset: 0B], MEM[base: _1494, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a3, a3, 1	# tmp1094, MEM[base: _1494, offset: 8B],
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a2, a2, a3	# tmp1096, MEM[base: _1494, offset: 0B], tmp1094
	s32i.n	a2, a5, 0	# MEM[base: _1494, offset: 0B], tmp1096
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	mov.n	a3, a7	# k, k
	addi.n	a5, a5, 4	# ivtmp$211, ivtmp$211,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	blt	a7, a14, .L25	# k, _2060,
	j	.L188		#
.L16:
	slli	a4, a3, 2	# _1760, k,
	add.n	a2, sp, a4	# _1759,, _1760
	addi	a7, a2, -8	# tmp1099, _1759,
	addi	a5, a2, -4	# tmp1101, _1759,
	addi	a4, a4, -8	# tmp1102, _1760,
	l32i.n	a2, a7, 0	# MEM[(opus_int32 *)_1759 + 4294967288B], D__lsm0$41
	l32i.n	a7, a5, 0	# MEM[(opus_int32 *)_1759 + 4294967292B], D__lsm1$42
	add.n	a4, sp, a4	# ivtmp$186,, tmp1102
.L27:
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a5, a4, 8	# MEM[base: _1533, offset: 8B], _2072
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a3, a3, 1	# k, k,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a8, a5, 1	# tmp1103, _2072,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a2, a2, a8	# tmp1104, D__lsm0$41, tmp1103
	s32i.n	a2, a4, 0	# MEM[base: _1533, offset: 0B], tmp1104
	mov.n	a2, a7	# D__lsm0$41, D__lsm1$42
	addi.n	a4, a4, 4	# ivtmp$186, ivtmp$186,
	mov.n	a7, a5	# D__lsm1$42, _2072
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	bge	a15, a3, .L27	# dd, k,
	j	.L28		#
.L15:
	addi.n	a14, a15, 1	# _2060, dd,
	bge	a15, a14, .L29	# dd, _2060,
	mov.n	a14, a15	# _2060, dd
.L29:
	l32i	a9, sp, 200	# %sfp,
	l32r	a12, .LC1	#, tmp1729
	l32i	a10, sp, 208	# %sfp,
	addi	a13, a9, -12	# tmp1106,,
	add.n	a13, sp, a13	# ivtmp$203,, tmp1106
	s32i	a12, sp, 116	# %sfp, tmp1729
	mov.n	a5, sp	# ivtmp$211,
	mov.n	a12, a13	# ivtmp$203, ivtmp$203
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a3, 2	# k,
	addi	a11, a10, -4	# tmp1756,,
	mov.n	a13, a10	# tmp1722,
.L25:
	addi.n	a7, a3, 1	# k, k,
	blt	a6, a3, .L126	# _278, k,
	blt	a7, a6, .L155	# k, _278,
.L126:
	mov.n	a2, a15	# n, dd
	j	.L34		#
.L188:
	bge	a15, a7, .L16	# dd, k,
	j	.L28		#
.L3:
# @OPUS@\upstream\silk\A2NLSF.c:153:     xlo = silk_LSFCosTab_FIX_Q12[ 0 ]; /* Q12*/
	l32r	a11, .LC2	#,
	addi.n	a5, a15, -1	#, dd,
	l16si	a6, a11, 0	# silk_LSFCosTab_FIX_Q12,
	s32i	a11, sp, 184	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:73:     x_Q16 = silk_LSHIFT( x, 4 );
	slli	a8, a6, 4	# _343,,
	srai	a2, a8, 15	# tmp1116, _343,
	addi.n	a2, a2, 1	# tmp1117, tmp1116,
	srai	a2, a2, 1	#, tmp1117,
	s32i	a5, sp, 168	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:153:     xlo = silk_LSFCosTab_FIX_Q12[ 0 ]; /* Q12*/
	s32i	a6, sp, 220	# %sfp,
	s32i	a2, sp, 132	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i.n	a13, a7, 0	# *_265, ylo
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bnez.n	a5, .L189	#,
	j	.L111		#
.L107:
	mov.n	a10, a2	#,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	slli	a2, a9, 20	# tmp1118,,
	srai	a2, a2, 16	# _158, tmp1118,
	l32i	a6, sp, 80	# MEM[(opus_int32 *)&P + 28B], MEM[(opus_int32 *)&P + 28B]
	extui	a3, a14, 0, 16	# tmp1119, prephitmp_1669,
	mull	a4, a10, a14	# tmp1121,, prephitmp_1669
	srai	a5, a14, 16	# tmp1124, prephitmp_1669,
	mull	a5, a5, a2	# tmp1125, tmp1124, _158
	mull	a3, a3, a2	# tmp1120, tmp1119, _158
	add.n	a4, a4, a6	# tmp1122, tmp1121, MEM[(opus_int32 *)&P + 28B]
	add.n	a4, a4, a5	# _1117, tmp1122, tmp1125
	srai	a3, a3, 16	# _162, tmp1120,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a3, a3, a4	# y32, _162, _1117
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	mull	a6, a3, a10	# tmp1128, y32,
	extui	a4, a3, 0, 16	# tmp1126, y32,
	l32i	a5, sp, 76	# MEM[(opus_int32 *)&P + 24B], MEM[(opus_int32 *)&P + 24B]
	srai	a3, a3, 16	# tmp1131, y32,
	mull	a3, a3, a2	# tmp1132, tmp1131, _158
	mull	a4, a4, a2	# tmp1127, tmp1126, _158
	add.n	a5, a6, a5	# tmp1129, tmp1128, MEM[(opus_int32 *)&P + 24B]
	add.n	a5, a5, a3	# _1115, tmp1129, tmp1132
	srai	a4, a4, 16	# _175, tmp1127,
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a4, a4, a5	# y32, _175, _1115
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	mull	a6, a4, a10	# tmp1135, y32,
	extui	a3, a4, 0, 16	# tmp1133, y32,
	l32i	a5, sp, 72	# MEM[(opus_int32 *)&P + 20B], MEM[(opus_int32 *)&P + 20B]
	srai	a4, a4, 16	# tmp1138, y32,
	mull	a3, a3, a2	# tmp1134, tmp1133, _158
	mull	a4, a4, a2	# tmp1139, tmp1138, _158
	add.n	a5, a6, a5	# tmp1136, tmp1135, MEM[(opus_int32 *)&P + 20B]
	srai	a3, a3, 16	# _185, tmp1134,
	add.n	a4, a5, a4	# _1113, tmp1136, tmp1139
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _185, _1113
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	mull	a6, a4, a10	# tmp1142, y32,
	extui	a5, a4, 0, 16	# tmp1140, y32,
	l32i	a3, sp, 68	# MEM[(opus_int32 *)&P + 16B], MEM[(opus_int32 *)&P + 16B]
	srai	a4, a4, 16	# tmp1145, y32,
	mull	a5, a5, a2	# tmp1141, tmp1140, _158
	mull	a4, a4, a2	# tmp1146, tmp1145, _158
	add.n	a3, a6, a3	# tmp1143, tmp1142, MEM[(opus_int32 *)&P + 16B]
	srai	a5, a5, 16	# _195, tmp1141,
	add.n	a4, a3, a4	# _64, tmp1143, tmp1146
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a4, a4, a5	# y32, _64, _195
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	mull	a6, a4, a10	# tmp1149, y32,
	extui	a3, a4, 0, 16	# tmp1147, y32,
	l32i	a5, sp, 64	# MEM[(opus_int32 *)&P + 12B], MEM[(opus_int32 *)&P + 12B]
	srai	a4, a4, 16	# tmp1152, y32,
	mull	a3, a3, a2	# tmp1148, tmp1147, _158
	mull	a4, a4, a2	# tmp1153, tmp1152, _158
	add.n	a5, a6, a5	# tmp1150, tmp1149, MEM[(opus_int32 *)&P + 12B]
	srai	a3, a3, 16	# _205, tmp1148,
	add.n	a4, a5, a4	# _1059, tmp1150, tmp1153
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _205, _1059
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	mull	a6, a4, a10	# tmp1156, y32,
	extui	a3, a4, 0, 16	# tmp1154, y32,
	l32i.n	a5, sp, 60	# MEM[(opus_int32 *)&P + 8B], MEM[(opus_int32 *)&P + 8B]
	srai	a4, a4, 16	# tmp1159, y32,
	mull	a3, a3, a2	# tmp1155, tmp1154, _158
	mull	a4, a4, a2	# tmp1160, tmp1159, _158
	add.n	a5, a6, a5	# tmp1157, tmp1156, MEM[(opus_int32 *)&P + 8B]
	srai	a3, a3, 16	# _215, tmp1155,
	add.n	a4, a5, a4	# _828, tmp1157, tmp1160
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _215, _828
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	mull	a6, a4, a10	# tmp1163, y32,
	extui	a3, a4, 0, 16	# tmp1161, y32,
	l32i.n	a5, sp, 56	# MEM[(opus_int32 *)&P + 4B], MEM[(opus_int32 *)&P + 4B]
	srai	a4, a4, 16	# tmp1166, y32,
	mull	a4, a4, a2	# tmp1167, tmp1166, _158
	mull	a3, a3, a2	# tmp1162, tmp1161, _158
	add.n	a5, a6, a5	# tmp1164, tmp1163, MEM[(opus_int32 *)&P + 4B]
	add.n	a5, a5, a4	# _848, tmp1164, tmp1167
	srai	a3, a3, 16	# _225, tmp1162,
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a3, a3, a5	# y32, _225, _848
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	extui	a4, a3, 0, 16	# tmp1168, y32,
	mull	a6, a3, a10	# tmp1170, y32,
	l32i.n	a5, sp, 52	# MEM[(opus_int32 *)&P], MEM[(opus_int32 *)&P]
	srai	a3, a3, 16	# tmp1173, y32,
	mull	a4, a4, a2	# tmp1169, tmp1168, _158
	mull	a3, a3, a2	# tmp1174, tmp1173, _158
	add.n	a5, a6, a5	# tmp1171, tmp1170, MEM[(opus_int32 *)&P]
	srai	a4, a4, 16	# _235, tmp1169,
	add.n	a5, a5, a3	# _52, tmp1171, tmp1174
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a13, a5, a4	# ylo, _52, _235
# @OPUS@\upstream\silk\A2NLSF.c:156:     if( ylo < 0 ) {
	bltz	a13, .L37	# ylo,
	movi.n	a11, 7	#,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	movi.n	a4, 0	#,
	movi.n	a5, 0x1c	#,
# @OPUS@\upstream\silk\A2NLSF.c:156:     if( ylo < 0 ) {
	s32i	a11, sp, 168	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	s32i	a4, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:151:     p = P;                          /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
	s32i	a5, sp, 212	# %sfp,
	j	.L38		#
.L111:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a14, a13	# prephitmp_1669, ylo
	mov.n	a6, a5	#,
.L35:
	slli	a6, a6, 2	#,,
	slli	a9, a8, 16	# tmp1721, _343,
	addi	a7, sp, 52	#,,
	s32i	a6, sp, 212	# %sfp,
	add.n	a4, a7, a6	# ivtmp$179,,
	srai	a5, a9, 16	# _2208, tmp1721,
	mov.n	a13, a14	# ylo, prephitmp_1669
	l32i	a6, sp, 132	# %sfp, _290
	l32i	a10, sp, 112	# %sfp,
	j	.L39		#
.L112:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	mov.n	a4, a7	# ivtmp$179, ivtmp$179
.L39:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a13, 16	# tmp1180, ylo,
	extui	a3, a13, 0, 16	# tmp1178, ylo,
	l32i.n	a7, a4, 0	# MEM[base: _1543, offset: 0B], MEM[base: _1543, offset: 0B]
	mull	a2, a2, a5	# tmp1181, tmp1180, _2208
	mull	a13, a6, a13	# tmp1184, _290, ylo
	mull	a3, a3, a5	# tmp1179, tmp1178, _2208
	add.n	a2, a2, a7	# tmp1182, tmp1181, MEM[base: _1543, offset: 0B]
	srai	a3, a3, 16	# _253, tmp1179,
	add.n	a2, a2, a13	# _271, tmp1182, tmp1184
	addi	a7, a4, -4	# ivtmp$179, ivtmp$179,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a13, a3, a2	# ylo, _253, _271
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a10, a4, .L112	#, ivtmp$179,
# @OPUS@\upstream\silk\A2NLSF.c:156:     if( ylo < 0 ) {
	bltz	a13, .L40	# ylo,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	movi.n	a4, 0	#,
# @OPUS@\upstream\silk\A2NLSF.c:151:     p = P;                          /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	s32i	a4, sp, 136	# %sfp,
	j	.L38		#
.L113:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	mov.n	a4, a9	# ivtmp$172, ivtmp$172
.L41:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a13, 16	# tmp1187, ylo,
	extui	a3, a13, 0, 16	# tmp1185, ylo,
	l32i.n	a9, a4, 0	# MEM[base: _1553, offset: 0B], MEM[base: _1553, offset: 0B]
	mull	a2, a2, a5	# tmp1188, tmp1187, _2220
	mull	a13, a7, a13	# tmp1191, _290, ylo
	mull	a3, a3, a5	# tmp1186, tmp1185, _2220
	add.n	a2, a2, a9	# tmp1189, tmp1188, MEM[base: _1553, offset: 0B]
	srai	a3, a3, 16	# _463, tmp1186,
	add.n	a2, a2, a13	# _286, tmp1189, tmp1191
	addi	a9, a4, -4	# ivtmp$172, ivtmp$172,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a13, a2, a3	# ylo, _286, _463
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a6, a4, .L113	# _1552, ivtmp$172,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	movi.n	a5, 1	#,
# @OPUS@\upstream\silk\A2NLSF.c:159:         p = Q;                      /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	s32i	a5, sp, 136	# %sfp,
.L38:
	l32i	a6, sp, 184	# %sfp,
	slli	a3, a15, 2	# tmp1195, dd,
	mov.n	a5, a3	# _1584, tmp1195
	l16si	a6, a6, 2	# silk_LSFCosTab_FIX_Q12,
	l32i	a9, sp, 192	# %sfp,
	add.n	a10, sp, a5	#,, _1584
	slli	a2, a8, 16	# tmp1754, _343,
	l32i	a8, sp, 192	# %sfp,
	addi	a4, a3, -12	# tmp1202, tmp1195,
	add.n	a9, a9, a5	#,, _1584
	addi	a3, a3, -4	# _1590, tmp1195,
	s32i	a6, sp, 196	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	movi.n	a7, 0	#,
	s32i	a10, sp, 176	# %sfp,
	addi	a6, sp, 52	#,,
	l32i	a10, sp, 212	# %sfp,
	add.n	a8, a8, a3	#,, _1590
	add.n	a6, a6, a5	#,, _1584
	s32i	a7, sp, 144	# %sfp,
	s32i	a9, sp, 224	# %sfp,
	addi	a7, sp, 52	#,,
	addi	a9, sp, 52	#,,
	add.n	a7, a7, a3	#,, _1590
	add.n	a9, a9, a10	#,,
	s32i	a8, sp, 228	# %sfp,
	s32i	a6, sp, 172	# %sfp,
	addi	a8, sp, 52	#,,
	l32i	a6, sp, 196	# %sfp,
	add.n	a8, a8, a4	#,, tmp1202
	s32i	a7, sp, 236	# %sfp,
	s32i	a9, sp, 248	# %sfp,
	l32i	a7, sp, 220	# %sfp,
	l32i	a9, sp, 144	# %sfp,
	add.n	a5, sp, a10	#,,
	add.n	a3, sp, a3	#,, _1590
	s32i	a8, sp, 240	# %sfp,
	add.n	a4, sp, a4	#,, tmp1202
	movi.n	a8, 1	#,
	slli	a10, a6, 4	#,,
	srai	a2, a2, 16	#, tmp1754,
	s32i	a3, sp, 232	# %sfp,
	s32i	a4, sp, 244	# %sfp,
	s32i	a5, sp, 252	# %sfp,
	s32i	a6, sp, 128	# %sfp,
	s32i	a7, sp, 140	# %sfp,
	s32i	a8, sp, 120	# %sfp,
	s32i	a9, sp, 164	# %sfp,
	s32i	a10, sp, 152	# %sfp,
	s32i	a2, sp, 124	# %sfp,
	j	.L42		#
.L62:
	l32i	a5, sp, 184	# %sfp,
	slli	a2, a10, 1	# tmp1207, tmp4,
	add.n	a2, a5, a2	# tmp1208,, tmp1207
	l16si	a2, a2, 0	# silk_LSFCosTab_FIX_Q12,
# @OPUS@\upstream\silk\A2NLSF.c:232:             xlo = xhi;
	l32i	a6, sp, 116	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a7, 0	#,
	slli	a8, a2, 4	#,,
	s32i	a2, sp, 128	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:236:             if( k > LSF_COS_TAB_SZ_FIX ) {
	mov.n	a13, a3	# ylo, yhi
# @OPUS@\upstream\silk\A2NLSF.c:232:             xlo = xhi;
	s32i	a6, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a7, sp, 144	# %sfp,
	s32i	a8, sp, 152	# %sfp,
.L42:
# @OPUS@\upstream\silk\A2NLSF.c:170:         xhi = silk_LSFCosTab_FIX_Q12[ k ]; /* Q12 */
	l32i	a9, sp, 128	# %sfp,
	s32i	a9, sp, 116	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:75:     if ( opus_likely( 8 == dd ) )
	bnei	a15, 8, .L43	# dd,,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	l32i	a10, sp, 152	# %sfp,
	slli	a4, a9, 20	# tmp1211,,
	srai	a4, a4, 16	# _486, tmp1211,
	srai	a2, a10, 15	# tmp1212,,
	srai	a5, a14, 16	# tmp1214, prephitmp_1669,
	extui	a3, a14, 0, 16	# tmp1218, prephitmp_1669,
	l32i.n	a6, a11, 28	# MEM[(opus_int32 *)p_85 + 28B], MEM[(opus_int32 *)p_85 + 28B]
	addi.n	a2, a2, 1	# tmp1213, tmp1212,
	mull	a5, a5, a4	# tmp1215, tmp1214, _486
	mull	a3, a3, a4	# tmp1219, tmp1218, _486
	srai	a2, a2, 1	# _495, tmp1213,
	add.n	a5, a5, a6	# tmp1216, tmp1215, MEM[(opus_int32 *)p_85 + 28B]
	srai	a3, a3, 16	# tmp1220, tmp1219,
	mull	a6, a2, a14	# tmp1222, _495, prephitmp_1669
	add.n	a3, a5, a3	# tmp1221, tmp1216, tmp1220
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a3, a3, a6	# y32, tmp1221, tmp1222
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	mull	a5, a2, a3	# tmp1225, _495, y32
	extui	a6, a3, 0, 16	# tmp1223, y32,
	l32i.n	a7, a11, 24	# MEM[(opus_int32 *)p_85 + 24B], MEM[(opus_int32 *)p_85 + 24B]
	srai	a3, a3, 16	# tmp1228, y32,
	mull	a6, a6, a4	# tmp1224, tmp1223, _486
	mull	a3, a3, a4	# tmp1229, tmp1228, _486
	add.n	a5, a5, a7	# tmp1226, tmp1225, MEM[(opus_int32 *)p_85 + 24B]
	srai	a6, a6, 16	# _503, tmp1224,
	add.n	a3, a5, a3	# _68, tmp1226, tmp1229
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a3, a3, a6	# y32, _68, _503
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	mull	a7, a2, a3	# tmp1232, _495, y32
	extui	a8, a3, 0, 16	# tmp1230, y32,
	l32i.n	a6, a11, 20	# MEM[(opus_int32 *)p_85 + 20B], MEM[(opus_int32 *)p_85 + 20B]
	srai	a3, a3, 16	# tmp1235, y32,
	mull	a3, a3, a4	# tmp1236, tmp1235, _486
	mull	a8, a8, a4	# tmp1231, tmp1230, _486
	add.n	a7, a7, a6	# tmp1233, tmp1232, MEM[(opus_int32 *)p_85 + 20B]
	add.n	a6, a7, a3	# _805, tmp1233, tmp1236
	srai	a8, a8, 16	# _513, tmp1231,
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a6, a8, a6	# y32, _513, _805
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	mull	a3, a2, a6	# tmp1239, _495, y32
	extui	a9, a6, 0, 16	# tmp1237, y32,
	l32i.n	a5, a11, 16	# MEM[(opus_int32 *)p_85 + 16B], MEM[(opus_int32 *)p_85 + 16B]
	srai	a6, a6, 16	# tmp1242, y32,
	mull	a6, a6, a4	# tmp1243, tmp1242, _486
	mull	a9, a9, a4	# tmp1238, tmp1237, _486
	add.n	a3, a3, a5	# tmp1240, tmp1239, MEM[(opus_int32 *)p_85 + 16B]
	add.n	a5, a3, a6	# _74, tmp1240, tmp1243
	srai	a9, a9, 16	# _523, tmp1238,
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a5, a5, a9	# y32, _74, _523
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	mull	a3, a2, a5	# tmp1246, _495, y32
	extui	a7, a5, 0, 16	# tmp1244, y32,
	l32i.n	a6, a11, 12	# MEM[(opus_int32 *)p_85 + 12B], MEM[(opus_int32 *)p_85 + 12B]
	srai	a5, a5, 16	# tmp1249, y32,
	mull	a5, a5, a4	# tmp1250, tmp1249, _486
	mull	a7, a7, a4	# tmp1245, tmp1244, _486
	add.n	a3, a3, a6	# tmp1247, tmp1246, MEM[(opus_int32 *)p_85 + 12B]
	add.n	a6, a3, a5	# _1015, tmp1247, tmp1250
	srai	a7, a7, 16	# _533, tmp1245,
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a6, a7, a6	# y32, _533, _1015
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	mull	a3, a2, a6	# tmp1253, _495, y32
	extui	a8, a6, 0, 16	# tmp1251, y32,
	l32i.n	a5, a11, 8	# MEM[(opus_int32 *)p_85 + 8B], MEM[(opus_int32 *)p_85 + 8B]
	srai	a6, a6, 16	# tmp1256, y32,
	mull	a6, a6, a4	# tmp1257, tmp1256, _486
	mull	a8, a8, a4	# tmp1252, tmp1251, _486
	add.n	a3, a3, a5	# tmp1254, tmp1253, MEM[(opus_int32 *)p_85 + 8B]
	add.n	a5, a3, a6	# _104, tmp1254, tmp1257
	srai	a8, a8, 16	# _543, tmp1252,
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a5, a5, a8	# y32, _104, _543
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	mull	a3, a2, a5	# tmp1260, _495, y32
	extui	a6, a5, 0, 16	# tmp1258, y32,
	l32i.n	a7, a11, 4	# MEM[(opus_int32 *)p_85 + 4B], MEM[(opus_int32 *)p_85 + 4B]
	srai	a5, a5, 16	# tmp1263, y32,
	mull	a6, a6, a4	# tmp1259, tmp1258, _486
	mull	a5, a5, a4	# tmp1264, tmp1263, _486
	add.n	a3, a3, a7	# tmp1261, tmp1260, MEM[(opus_int32 *)p_85 + 4B]
	add.n	a3, a3, a5	# _126, tmp1261, tmp1264
	srai	a6, a6, 16	# _553, tmp1259,
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a6, a3, a6	# y32, _126, _553
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	extui	a7, a6, 0, 16	# tmp1265, y32,
	mull	a2, a2, a6	# tmp1267, _495, y32
	l32i.n	a3, a11, 0	# *p_85, *p_85
	srai	a6, a6, 16	# tmp1270, y32,
	mull	a7, a7, a4	# tmp1266, tmp1265, _486
	mull	a6, a6, a4	# tmp1271, tmp1270, _486
	add.n	a2, a2, a3	# tmp1268, tmp1267, *p_85
	srai	a7, a7, 16	# _563, tmp1266,
	add.n	a6, a2, a6	# _285, tmp1268, tmp1271
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a3, a6, a7	# yhi, _285, _563
	j	.L44		#
.L43:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	l32i	a5, sp, 168	# %sfp,
	bltz	a5, .L114	#,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	l32i	a6, sp, 152	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a3, a14	# yhi, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a7, a6, 15	# tmp1272,,
	slli	a6, a9, 20	# tmp1274, tmp8,
	l32i	a9, sp, 212	# %sfp,
	addi.n	a7, a7, 1	# tmp1273, tmp1272,
	srai	a7, a7, 1	# _586, tmp1273,
	srai	a6, a6, 16	# _2198, tmp1274,
	add.n	a5, a11, a9	# ivtmp$165, p,
	j	.L45		#
.L115:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	mov.n	a5, a8	# ivtmp$165, ivtmp$165
.L45:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a3, 16	# tmp1277, yhi,
	extui	a4, a3, 0, 16	# tmp1275, yhi,
	l32i.n	a8, a5, 0	# MEM[base: _1563, offset: 0B], MEM[base: _1563, offset: 0B]
	mull	a2, a2, a6	# tmp1278, tmp1277, _2198
	mull	a3, a3, a7	# tmp1281, yhi, _586
	mull	a4, a4, a6	# tmp1276, tmp1275, _2198
	add.n	a2, a2, a8	# tmp1279, tmp1278, MEM[base: _1563, offset: 0B]
	srai	a4, a4, 16	# _581, tmp1276,
	add.n	a2, a2, a3	# _269, tmp1279, tmp1281
	addi	a8, a5, -4	# ivtmp$165, ivtmp$165,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a3, a2, a4	# yhi, _269, _581
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a11, a5, .L115	# p, ivtmp$165,
	j	.L44		#
.L114:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a3, a14	# yhi, prephitmp_1669
.L44:
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	addi.n	a7, a13, -1	# tmp1726, ylo,
	or	a2, a13, a7	# tmp1285, ylo, tmp1726
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	bgez	a2, .L127	# tmp1285,
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	l32i	a10, sp, 144	# %sfp,
	bge	a3, a10, .L46	# yhi,,
.L127:
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	bltz	a13, .L49	# ylo,
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	l32i	a4, sp, 144	# %sfp,
	neg	a2, a4	# tmp1291,
# @OPUS@\upstream\silk\A2NLSF.c:174:         if( ( ylo <= 0 && yhi >= thr ) || ( ylo >= 0 && yhi <= -thr ) ) {
	blt	a2, a3, .L49	# tmp1291, yhi,
.L46:
	l32i	a6, sp, 212	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:175:             if( yhi == 0 ) {
	movi.n	a9, 0	# tmp1295,
	movi.n	a2, 1	# tmp1294,
	movnez	a2, a9, a3	# tmp1294, tmp1295, yhi
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	srai	a5, a14, 16	#, prephitmp_1669,
	add.n	a6, a11, a6	#, p,
# @OPUS@\upstream\silk\A2NLSF.c:183:             ffrac = -256;
	movi	a8, -0x100	#,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	extui	a10, a14, 0, 16	#, prephitmp_1669,
# @OPUS@\upstream\silk\A2NLSF.c:175:             if( yhi == 0 ) {
	s32i	a2, sp, 144	# %sfp, tmp1294
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	s32i	a5, sp, 156	# %sfp,
	s32i	a6, sp, 216	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:183:             ffrac = -256;
	s32i	a8, sp, 148	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	s32i	a10, sp, 160	# %sfp,
.L56:
# @OPUS@\upstream\silk\A2NLSF.c:186:                 xmid = silk_RSHIFT_ROUND( xlo + xhi, 1 );
	l32i	a4, sp, 140	# %sfp,
	l32i	a5, sp, 116	# %sfp,
	add.n	a2, a4, a5	# _7,,
	srai	a6, a2, 1	# tmp1296, _7,
	extui	a2, a2, 0, 1	# tmp1297, _7,
# @OPUS@\upstream\silk\A2NLSF.c:186:                 xmid = silk_RSHIFT_ROUND( xlo + xhi, 1 );
	add.n	a6, a6, a2	# xmid, tmp1296, tmp1297
# @OPUS@\upstream\silk\A2NLSF.c:73:     x_Q16 = silk_LSHIFT( x, 4 );
	slli	a2, a6, 4	# _596, xmid,
# @OPUS@\upstream\silk\A2NLSF.c:75:     if ( opus_likely( 8 == dd ) )
	bnei	a15, 8, .L50	# dd,,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	l32i	a8, sp, 160	# %sfp,
	l32i	a10, sp, 156	# %sfp,
	slli	a5, a6, 20	# tmp1298, xmid,
	srai	a5, a5, 16	# _604, tmp1298,
	srai	a2, a2, 15	# tmp1299, _596,
	mull	a4, a8, a5	# tmp1302,, _604
	addi.n	a2, a2, 1	# tmp1300, tmp1299,
	mull	a8, a10, a5	# tmp1304,, _604
	l32i.n	a10, a11, 28	# MEM[(opus_int32 *)p_85 + 28B], MEM[(opus_int32 *)p_85 + 28B]
	srai	a2, a2, 1	# _613, tmp1300,
	srai	a4, a4, 16	# tmp1303, tmp1302,
	add.n	a8, a8, a10	# tmp1305, tmp1304, MEM[(opus_int32 *)p_85 + 28B]
	mull	a10, a2, a14	# tmp1308, _613, prephitmp_1669
	add.n	a8, a4, a8	# tmp1307, tmp1303, tmp1305
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a8, a8, a10	# y32, tmp1307, tmp1308
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	mull	a4, a2, a8	# tmp1311, _613, y32
	extui	a10, a8, 0, 16	# tmp1309, y32,
	l32i.n	a12, a11, 24	# MEM[(opus_int32 *)p_85 + 24B], MEM[(opus_int32 *)p_85 + 24B]
	srai	a8, a8, 16	# tmp1314, y32,
	mull	a8, a8, a5	# tmp1315, tmp1314, _604
	mull	a10, a10, a5	# tmp1310, tmp1309, _604
	add.n	a4, a4, a12	# tmp1312, tmp1311, MEM[(opus_int32 *)p_85 + 24B]
	srai	a10, a10, 16	# _621, tmp1310,
	add.n	a4, a4, a8	# _1060, tmp1312, tmp1315
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a4, a10, a4	# y32, _621, _1060
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	mull	a12, a2, a4	# tmp1318, _613, y32
	extui	a8, a4, 0, 16	# tmp1316, y32,
	l32i.n	a10, a11, 20	# MEM[(opus_int32 *)p_85 + 20B], MEM[(opus_int32 *)p_85 + 20B]
	srai	a4, a4, 16	# tmp1321, y32,
	mull	a4, a4, a5	# tmp1322, tmp1321, _604
	mull	a8, a8, a5	# tmp1317, tmp1316, _604
	add.n	a12, a12, a10	# tmp1319, tmp1318, MEM[(opus_int32 *)p_85 + 20B]
	add.n	a10, a12, a4	# _1095, tmp1319, tmp1322
	srai	a8, a8, 16	# _631, tmp1317,
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a10, a8, a10	# y32, _631, _1095
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	mull	a4, a2, a10	# tmp1325, _613, y32
	extui	a12, a10, 0, 16	# tmp1323, y32,
	l32i.n	a8, a11, 16	# MEM[(opus_int32 *)p_85 + 16B], MEM[(opus_int32 *)p_85 + 16B]
	srai	a10, a10, 16	# tmp1328, y32,
	mull	a10, a10, a5	# tmp1329, tmp1328, _604
	mull	a12, a12, a5	# tmp1324, tmp1323, _604
	add.n	a4, a4, a8	# tmp1326, tmp1325, MEM[(opus_int32 *)p_85 + 16B]
	add.n	a8, a4, a10	# _1105, tmp1326, tmp1329
	srai	a12, a12, 16	# _641, tmp1324,
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a8, a12, a8	# y32, _641, _1105
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	mull	a4, a2, a8	# tmp1332, _613, y32
	extui	a12, a8, 0, 16	# tmp1330, y32,
	l32i.n	a10, a11, 12	# MEM[(opus_int32 *)p_85 + 12B], MEM[(opus_int32 *)p_85 + 12B]
	srai	a8, a8, 16	# tmp1335, y32,
	mull	a8, a8, a5	# tmp1336, tmp1335, _604
	mull	a12, a12, a5	# tmp1331, tmp1330, _604
	add.n	a4, a4, a10	# tmp1333, tmp1332, MEM[(opus_int32 *)p_85 + 12B]
	add.n	a10, a4, a8	# _1102, tmp1333, tmp1336
	srai	a12, a12, 16	# _651, tmp1331,
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a10, a12, a10	# y32, _651, _1102
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	mull	a4, a2, a10	# tmp1339, _613, y32
	extui	a12, a10, 0, 16	# tmp1337, y32,
	l32i.n	a8, a11, 8	# MEM[(opus_int32 *)p_85 + 8B], MEM[(opus_int32 *)p_85 + 8B]
	srai	a10, a10, 16	# tmp1342, y32,
	mull	a10, a10, a5	# tmp1343, tmp1342, _604
	mull	a12, a12, a5	# tmp1338, tmp1337, _604
	add.n	a4, a4, a8	# tmp1340, tmp1339, MEM[(opus_int32 *)p_85 + 8B]
	add.n	a8, a4, a10	# _75, tmp1340, tmp1343
	srai	a12, a12, 16	# _661, tmp1338,
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a8, a8, a12	# y32, _75, _661
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	mull	a4, a2, a8	# tmp1346, _613, y32
	extui	a10, a8, 0, 16	# tmp1344, y32,
	l32i.n	a12, a11, 4	# MEM[(opus_int32 *)p_85 + 4B], MEM[(opus_int32 *)p_85 + 4B]
	srai	a8, a8, 16	# tmp1349, y32,
	mull	a10, a10, a5	# tmp1345, tmp1344, _604
	mull	a8, a8, a5	# tmp1350, tmp1349, _604
	add.n	a4, a4, a12	# tmp1347, tmp1346, MEM[(opus_int32 *)p_85 + 4B]
	add.n	a4, a4, a8	# _124, tmp1347, tmp1350
	srai	a10, a10, 16	# _671, tmp1345,
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a10, a4, a10	# y32, _124, _671
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	extui	a12, a10, 0, 16	# tmp1351, y32,
	mull	a2, a2, a10	# tmp1353, _613, y32
	l32i.n	a4, a11, 0	# *p_85, *p_85
	srai	a10, a10, 16	# tmp1356, y32,
	mull	a12, a12, a5	# tmp1352, tmp1351, _604
	mull	a10, a10, a5	# tmp1357, tmp1356, _604
	add.n	a2, a2, a4	# tmp1354, tmp1353, *p_85
	srai	a12, a12, 16	# _681, tmp1352,
	add.n	a10, a2, a10	# _1090, tmp1354, tmp1357
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a4, a12, a10	# y32, _681, _1090
	j	.L51		#
.L50:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	l32i	a5, sp, 168	# %sfp,
	bltz	a5, .L116	#,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a2, 15	# tmp1358, _596,
	addi.n	a2, a2, 1	# tmp1359, tmp1358,
	slli	a12, a6, 20	# tmp1360, xmid,
	srai	a2, a2, 1	# _704, tmp1359,
	srai	a12, a12, 16	# _1890, tmp1360,
	l32i	a10, sp, 216	# %sfp, ivtmp$56
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a4, a14	# y32, prephitmp_1669
	s32i	a9, sp, 256	# %sfp, m
	j	.L52		#
.L117:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	mov.n	a10, a8	# ivtmp$56, ivtmp$56
.L52:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a8, a4, 16	# tmp1363, y32,
	extui	a5, a4, 0, 16	# tmp1361, y32,
	mull	a8, a8, a12	# tmp1364, tmp1363, _1890
	l32i.n	a9, a10, 0	# MEM[base: _1739, offset: 0B],
	mull	a4, a2, a4	# tmp1367, _704, y32
	mull	a5, a5, a12	# tmp1362, tmp1361, _1890
	add.n	a8, a8, a9	# tmp1365, tmp1364,
	add.n	a4, a8, a4	# _268, tmp1365, tmp1367
	srai	a5, a5, 16	# _699, tmp1362,
	addi	a8, a10, -4	# ivtmp$56, ivtmp$56,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a4, a4, a5	# y32, _268, _699
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a11, a10, .L117	# p, ivtmp$56,
	l32i	a9, sp, 256	# %sfp, m
	j	.L51		#
.L116:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a4, a14	# y32, prephitmp_1669
.L51:
# @OPUS@\upstream\silk\A2NLSF.c:190:                 if( ( ylo <= 0 && ymid >= 0 ) || ( ylo >= 0 && ymid <= 0 ) ) {
	or	a7, a13, a7	# tmp1371, ylo, tmp1726
# @OPUS@\upstream\silk\A2NLSF.c:190:                 if( ( ylo <= 0 && ymid >= 0 ) || ( ylo >= 0 && ymid <= 0 ) ) {
	bgez	a7, .L128	# tmp1371,
	bgez	a4, .L119	# y32,
.L128:
# @OPUS@\upstream\silk\A2NLSF.c:190:                 if( ( ylo <= 0 && ymid >= 0 ) || ( ylo >= 0 && ymid <= 0 ) ) {
	bltz	a13, .L129	# ylo,
# @OPUS@\upstream\silk\A2NLSF.c:190:                 if( ( ylo <= 0 && ymid >= 0 ) || ( ylo >= 0 && ymid <= 0 ) ) {
	addi.n	a2, a4, -1	# tmp1388, y32,
	or	a2, a4, a2	# tmp1389, y32, tmp1388
# @OPUS@\upstream\silk\A2NLSF.c:190:                 if( ( ylo <= 0 && ymid >= 0 ) || ( ylo >= 0 && ymid <= 0 ) ) {
	bltz	a2, .L119	# tmp1389,
.L129:
# @OPUS@\upstream\silk\A2NLSF.c:198:                     ffrac = silk_ADD_RSHIFT( ffrac, 128, m );
	l32i	a5, sp, 148	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:198:                     ffrac = silk_ADD_RSHIFT( ffrac, 128, m );
	movi	a10, 0x80	#,
	ssr	a9	# m
	sra	a2, a10	# tmp1393,
# @OPUS@\upstream\silk\A2NLSF.c:198:                     ffrac = silk_ADD_RSHIFT( ffrac, 128, m );
	add.n	a5, a5, a2	#,, tmp1393
	s32i	a5, sp, 148	# %sfp,
	mov.n	a13, a4	# ylo, y32
# @OPUS@\upstream\silk\A2NLSF.c:196:                     xlo = xmid;
	s32i	a6, sp, 140	# %sfp, xmid
	j	.L53		#
.L119:
	mov.n	a3, a4	# yhi, y32
# @OPUS@\upstream\silk\A2NLSF.c:192:                     xhi = xmid;
	s32i	a6, sp, 116	# %sfp, xmid
.L53:
# @OPUS@\upstream\silk\A2NLSF.c:184:             for( m = 0; m < BIN_DIV_STEPS_A2NLSF_FIX; m++ ) {
	addi.n	a9, a9, 1	# m, m,
# @OPUS@\upstream\silk\A2NLSF.c:184:             for( m = 0; m < BIN_DIV_STEPS_A2NLSF_FIX; m++ ) {
	beqi	a9, 3, .L190	# m,,
	addi.n	a7, a13, -1	# tmp1726, ylo,
	j	.L56		#
.L190:
# @OPUS@\upstream\silk\A2NLSF.c:203:             if( silk_abs( ylo ) < 65536 ) {
	l32r	a2, .LC4	#, tmp1395
# @OPUS@\upstream\silk\A2NLSF.c:203:             if( silk_abs( ylo ) < 65536 ) {
	l32r	a4, .LC5	#, tmp1396
# @OPUS@\upstream\silk\A2NLSF.c:203:             if( silk_abs( ylo ) < 65536 ) {
	add.n	a2, a13, a2	# tmp1394, ylo, tmp1395
	sub	a3, a13, a3	# _1887, ylo, yhi
# @OPUS@\upstream\silk\A2NLSF.c:203:             if( silk_abs( ylo ) < 65536 ) {
	bltu	a4, a2, .L57	# tmp1396, tmp1394,
# @OPUS@\upstream\silk\A2NLSF.c:207:                 if( den != 0 ) {
	beqz.n	a3, .L58	# _1887,
# @OPUS@\upstream\silk\A2NLSF.c:206:                 nom = silk_LSHIFT( ylo, 8 - BIN_DIV_STEPS_A2NLSF_FIX ) + silk_RSHIFT( den, 1 );
	srai	a4, a3, 1	# tmp1398, _1887,
# @OPUS@\upstream\silk\A2NLSF.c:206:                 nom = silk_LSHIFT( ylo, 8 - BIN_DIV_STEPS_A2NLSF_FIX ) + silk_RSHIFT( den, 1 );
	slli	a2, a13, 5	# tmp1397, ylo,
# @OPUS@\upstream\silk\A2NLSF.c:208:                     ffrac += silk_DIV32( nom, den );
	add.n	a2, a2, a4	#, tmp1397, tmp1398
	call0	__divsi3		#
# @OPUS@\upstream\silk\A2NLSF.c:208:                     ffrac += silk_DIV32( nom, den );
	l32i	a6, sp, 148	# %sfp,
	add.n	a6, a6, a2	#,,
	s32i	a6, sp, 148	# %sfp,
	j	.L58		#
.L57:
# @OPUS@\upstream\silk\A2NLSF.c:212:                 ffrac += silk_DIV32( ylo, silk_RSHIFT( ylo - yhi, 8 - BIN_DIV_STEPS_A2NLSF_FIX ) );
	srai	a3, a3, 5	#, _1887,
	mov.n	a2, a13	#, ylo
	call0	__divsi3		#
# @OPUS@\upstream\silk\A2NLSF.c:212:                 ffrac += silk_DIV32( ylo, silk_RSHIFT( ylo - yhi, 8 - BIN_DIV_STEPS_A2NLSF_FIX ) );
	l32i	a7, sp, 148	# %sfp,
	add.n	a7, a7, a2	#,,
	s32i	a7, sp, 148	# %sfp,
.L58:
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	l32i	a8, sp, 120	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	l32i	a9, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	l32i	a10, sp, 148	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	slli	a2, a8, 8	# tmp1412,,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	l32i	a11, sp, 204	# %sfp,
# @OPUS@\upstream\silk\SigProc_FIX.h:556:     return (((a) < (b)) ? (a) : (b));
	l32r	a4, .LC6	#, tmp1417
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	slli	a3, a9, 1	# tmp1409,,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	add.n	a2, a2, a10	# tmp1411, tmp1412,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	add.n	a3, a11, a3	# tmp1410,, tmp1409
# @OPUS@\upstream\silk\SigProc_FIX.h:556:     return (((a) < (b)) ? (a) : (b));
	bge	a4, a2, .L59	# tmp1417, tmp1411,
	mov.n	a2, a4	# tmp1411, tmp1417
.L59:
# @OPUS@\upstream\silk\A2NLSF.c:218:             root_ix++;        /* Next root */
	l32i	a4, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:219:             if( root_ix >= d ) {
	l32i	a5, sp, 180	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:218:             root_ix++;        /* Next root */
	addi.n	a4, a4, 1	#,,
# @OPUS@\upstream\silk\A2NLSF.c:214:             NLSF[ root_ix ] = (opus_int16)silk_min_32( silk_LSHIFT( (opus_int32)k, 8 ) + ffrac, silk_int16_MAX );
	s16i	a2, a3, 0	# *_34, tmp1411
# @OPUS@\upstream\silk\A2NLSF.c:218:             root_ix++;        /* Next root */
	s32i	a4, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:219:             if( root_ix >= d ) {
	bge	a4, a5, .L1	#,,
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	l32i	a6, sp, 120	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:224:             p = PQ[ root_ix & 1 ];
	extui	a2, a4, 0, 1	# tmp1418,,
	mov.n	a7, a4	#,
# @OPUS@\upstream\silk\A2NLSF.c:224:             p = PQ[ root_ix & 1 ];
	slli	a2, a2, 2	# tmp1419, tmp1418,
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	addi.n	a4, a6, -1	# tmp1423,,
	l32i	a8, sp, 184	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:224:             p = PQ[ root_ix & 1 ];
	add.n	a2, sp, a2	# tmp1420,, tmp1419
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	slli	a4, a4, 1	# tmp1424, tmp1423,
# @OPUS@\upstream\silk\A2NLSF.c:224:             p = PQ[ root_ix & 1 ];
	l32i	a11, a2, 104	# PQ, p
# @OPUS@\upstream\silk\A2NLSF.c:228:             ylo = silk_LSHIFT( 1 - ( root_ix & 2 ), 12 );
	movi.n	a13, 2	# tmp1428,
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	add.n	a4, a8, a4	# tmp1425,, tmp1424
	l32i	a9, sp, 200	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:228:             ylo = silk_LSHIFT( 1 - ( root_ix & 2 ), 12 );
	and	a2, a7, a13	# tmp1429,, tmp1428
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	l16si	a4, a4, 0	# silk_LSFCosTab_FIX_Q12,
# @OPUS@\upstream\silk\A2NLSF.c:228:             ylo = silk_LSHIFT( 1 - ( root_ix & 2 ), 12 );
	movi.n	a13, 1	# tmp1430,
	sub	a13, a13, a2	# tmp1431, tmp1430, tmp1429
	add.n	a3, a11, a9	# tmp1432, p,
# @OPUS@\upstream\silk\A2NLSF.c:227:             xlo = silk_LSFCosTab_FIX_Q12[ k - 1 ]; /* Q12*/
	s32i	a4, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:228:             ylo = silk_LSHIFT( 1 - ( root_ix & 2 ), 12 );
	slli	a13, a13, 12	# ylo, tmp1431,
	l32i.n	a14, a3, 0	# *_2172, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:228:             ylo = silk_LSHIFT( 1 - ( root_ix & 2 ), 12 );
	j	.L42		#
.L49:
# @OPUS@\upstream\silk\A2NLSF.c:231:             k++;
	l32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:236:             if( k > LSF_COS_TAB_SZ_FIX ) {
	movi	a2, 0x80	# tmp1433,
# @OPUS@\upstream\silk\A2NLSF.c:231:             k++;
	addi.n	a10, a10, 1	#,,
	s32i	a10, sp, 120	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:236:             if( k > LSF_COS_TAB_SZ_FIX ) {
	bge	a2, a10, .L62	# tmp1433,,
# @OPUS@\upstream\silk\A2NLSF.c:237:                 i++;
	l32i	a11, sp, 164	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:238:                 if( i > MAX_ITERATIONS_A2NLSF_FIX ) {
	movi.n	a2, 0x10	# tmp1434,
# @OPUS@\upstream\silk\A2NLSF.c:237:                 i++;
	addi.n	a11, a11, 1	#,,
	s32i	a11, sp, 164	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:238:                 if( i > MAX_ITERATIONS_A2NLSF_FIX ) {
	bge	a2, a11, .L63	# tmp1434,,
# @OPUS@\upstream\silk\A2NLSF.c:240:                     NLSF[ 0 ] = (opus_int16)silk_DIV32_16( 1 << 15, d + 1 );
	l32i	a5, sp, 180	# %sfp,
	l32r	a2, .LC7	#,
	addi.n	a3, a5, 1	#,,
	call0	__divsi3		#
# @OPUS@\upstream\silk\A2NLSF.c:240:                     NLSF[ 0 ] = (opus_int16)silk_DIV32_16( 1 << 15, d + 1 );
	slli	a2, a2, 16	# tmp1440,,
# @OPUS@\upstream\silk\A2NLSF.c:240:                     NLSF[ 0 ] = (opus_int16)silk_DIV32_16( 1 << 15, d + 1 );
	l32i	a6, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:240:                     NLSF[ 0 ] = (opus_int16)silk_DIV32_16( 1 << 15, d + 1 );
	srai	a2, a2, 16	# _45, tmp1440,
# @OPUS@\upstream\silk\A2NLSF.c:241:                     for( k = 1; k < d; k++ ) {
	l32i	a7, sp, 180	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:240:                     NLSF[ 0 ] = (opus_int16)silk_DIV32_16( 1 << 15, d + 1 );
	s16i	a2, a6, 0	# *NLSF_103(D), _45
# @OPUS@\upstream\silk\A2NLSF.c:241:                     for( k = 1; k < d; k++ ) {
	blti	a7, 2, .L1	#,,
# @OPUS@\upstream\silk\A2NLSF.c:242:                         NLSF[ k ] = (opus_int16)silk_ADD16( NLSF[ k-1 ], NLSF[ 0 ] );
	slli	a3, a2, 1	# tmp1441, _45,
# @OPUS@\upstream\silk\A2NLSF.c:242:                         NLSF[ k ] = (opus_int16)silk_ADD16( NLSF[ k-1 ], NLSF[ 0 ] );
	s16i	a3, a6, 2	# MEM[(opus_int16 *)NLSF_103(D) + 2B], tmp1441
# @OPUS@\upstream\silk\A2NLSF.c:241:                     for( k = 1; k < d; k++ ) {
	beqi	a7, 2, .L1	#,,
	slli	a2, a2, 17	# tmp1443, _45,
	slli	a5, a7, 1	# tmp1444,,
	srai	a2, a2, 16	# D__lsm0$24, tmp1443,
	addi.n	a4, a6, 4	# ivtmp$48,,
	add.n	a5, a6, a5	# _2017,, tmp1444
.L65:
# @OPUS@\upstream\silk\A2NLSF.c:242:                         NLSF[ k ] = (opus_int16)silk_ADD16( NLSF[ k-1 ], NLSF[ 0 ] );
	l16ui	a3, a6, 0	# *NLSF_103(D),
	add.n	a2, a2, a3	# tmp1446, D__lsm0$24, *NLSF_103(D)
	slli	a2, a2, 16	# tmp1447, tmp1446,
	srai	a2, a2, 16	# D__lsm0$24, tmp1447,
# @OPUS@\upstream\silk\A2NLSF.c:242:                         NLSF[ k ] = (opus_int16)silk_ADD16( NLSF[ k-1 ], NLSF[ 0 ] );
	s16i	a2, a4, 0	# MEM[base: _1800, offset: 0B], D__lsm0$24
	addi.n	a4, a4, 2	# ivtmp$48, ivtmp$48,
# @OPUS@\upstream\silk\A2NLSF.c:241:                     for( k = 1; k < d; k++ ) {
	bne	a4, a5, .L65	# ivtmp$48, _2017,
	j	.L1		#
.L63:
# @OPUS@\upstream\silk\A2NLSF.c:248:                 silk_bwexpander_32( a_Q16, d, 65536 - silk_LSHIFT( 1, i ) );
	l32r	a9, .LC0	#,
# @OPUS@\upstream\silk\A2NLSF.c:248:                 silk_bwexpander_32( a_Q16, d, 65536 - silk_LSHIFT( 1, i ) );
	movi.n	a4, 1	# tmp1448,
	ssl	a11	# tmp8
	sll	a4, a4	# tmp1449, tmp1448
# @OPUS@\upstream\silk\A2NLSF.c:248:                 silk_bwexpander_32( a_Q16, d, 65536 - silk_LSHIFT( 1, i ) );
	l32i	a3, sp, 180	# %sfp,
	l32i	a2, sp, 192	# %sfp,
	sub	a4, a9, a4	#,, tmp1449
	call0	silk_bwexpander_32		#
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	l32r	a11, .LC0	#,
	l32i	a10, sp, 188	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:106:     Q[dd] = silk_LSHIFT( 1, 16 );
	l32i	a5, sp, 208	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:105:     P[dd] = silk_LSHIFT( 1, 16 );
	s32i.n	a11, a10, 0	# *_265,
# @OPUS@\upstream\silk\A2NLSF.c:106:     Q[dd] = silk_LSHIFT( 1, 16 );
	s32i.n	a11, a5, 0	# *_266,
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	bgei	a15, 1, .L66	# dd,,
	j	.L67		#
.L191:
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	bgei	a15, 2, .L68	# dd,,
.L67:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a6, sp, 188	# %sfp,
	l32i.n	a14, a6, 0	# *_265, prephitmp_1669
	j	.L69		#
.L66:
	mov.n	a7, sp	# ivtmp$159,
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	addi	a6, sp, 52	# ivtmp$158,,
	l32i	a5, sp, 224	# %sfp, ivtmp$157
	l32i	a3, sp, 228	# %sfp, ivtmp$155
	l32i	a10, sp, 192	# %sfp, a_Q16
	j	.L70		#
.L120:
	mov.n	a3, a9	# ivtmp$155, ivtmp$155
.L70:
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	l32i.n	a2, a5, 0	# MEM[base: _1575, offset: 0B], _843
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	l32i.n	a8, a3, 0	# MEM[base: _1576, offset: 0B], _837
	addi	a9, a3, -4	# ivtmp$155, ivtmp$155,
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	add.n	a4, a8, a2	# tmp1454, _837, _843
	neg	a4, a4	# tmp1455, tmp1454
# @OPUS@\upstream\silk\A2NLSF.c:109:         Q[ k ] = -a_Q16[ dd - k - 1 ] + a_Q16[ dd + k ];    /* Q16 */
	sub	a2, a2, a8	# tmp1456, _843, _837
# @OPUS@\upstream\silk\A2NLSF.c:108:         P[ k ] = -a_Q16[ dd - k - 1 ] - a_Q16[ dd + k ];    /* Q16 */
	s32i.n	a4, a6, 0	# MEM[base: _1574, offset: 0B], tmp1455
# @OPUS@\upstream\silk\A2NLSF.c:109:         Q[ k ] = -a_Q16[ dd - k - 1 ] + a_Q16[ dd + k ];    /* Q16 */
	s32i.n	a2, a7, 0	# MEM[base: _1573, offset: 0B], tmp1456
	addi.n	a5, a5, 4	# ivtmp$157, ivtmp$157,
	addi.n	a6, a6, 4	# ivtmp$158, ivtmp$158,
	addi.n	a7, a7, 4	# ivtmp$159, ivtmp$159,
# @OPUS@\upstream\silk\A2NLSF.c:107:     for( k = 0; k < dd; k++ ) {
	bne	a10, a3, .L120	# a_Q16, ivtmp$155,
	l32i	a7, sp, 176	# %sfp,
	l32i	a8, sp, 172	# %sfp,
	l32i.n	a5, a7, 0	# *_1931, D__lsm0$31
	l32i.n	a4, a8, 0	# *_1917, D__lsm0$32
	l32i	a3, sp, 232	# %sfp, ivtmp$148
	l32i	a2, sp, 236	# %sfp, ivtmp$146
	l32i	a9, sp, 112	# %sfp,
	j	.L71		#
.L121:
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	mov.n	a2, a6	# ivtmp$146, ivtmp$146
.L71:
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	l32i.n	a6, a3, 0	# MEM[base: _1599, offset: 0B], MEM[base: _1599, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	l32i.n	a7, a2, 0	# MEM[base: _1601, offset: 0B], MEM[base: _1601, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	add.n	a5, a5, a6	# D__lsm0$31, D__lsm0$31, MEM[base: _1599, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	sub	a4, a7, a4	# D__lsm0$32, MEM[base: _1601, offset: 0B], D__lsm0$32
# @OPUS@\upstream\silk\A2NLSF.c:117:         Q[ k - 1 ] += Q[ k ];
	s32i.n	a5, a3, 0	# MEM[base: _1599, offset: 0B], D__lsm0$31
# @OPUS@\upstream\silk\A2NLSF.c:116:         P[ k - 1 ] -= P[ k ];
	s32i.n	a4, a2, 0	# MEM[base: _1601, offset: 0B], D__lsm0$32
	addi	a6, a2, -4	# ivtmp$146, ivtmp$146,
	addi	a3, a3, -4	# ivtmp$148, ivtmp$148,
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	bne	a9, a2, .L121	#, ivtmp$146,
	j	.L191		#
.L156:
	l32i.n	a8, a12, 0	# *_1838, D__lsm0$35
	l32i.n	a7, a14, 0	# MEM[(opus_int32 *)_1838 + 4294967292B(OVF)], D__lsm1$36
	mov.n	a3, a15	# n, dd
	s32i	a15, sp, 116	# %sfp, dd
	mov.n	a4, a11	# ivtmp$131, ivtmp$131
	mov.n	a15, a10	# _278, _278
.L73:
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	l32i.n	a10, a4, 4	# MEM[base: _1626, offset: 4B],
	addi	a9, a3, -3	# tmp1463, _1635,
	sub	a8, a10, a8	# D__lsm0$35,, D__lsm0$35
	l32i.n	a10, a4, 0	# MEM[base: _1626, offset: 0B],
	s32i.n	a8, a4, 4	# MEM[base: _1626, offset: 4B], D__lsm0$35
	sub	a7, a10, a7	# D__lsm1$36,, D__lsm1$36
	s32i.n	a7, a4, 0	# MEM[base: _1626, offset: 0B], D__lsm1$36
	addi	a3, a3, -2	# n, n,
	addi	a4, a4, -8	# ivtmp$131, ivtmp$131,
	blt	a6, a9, .L73	# ivtmp$138, tmp1463,
	mov.n	a4, a15	# _278, _278
	l32i	a15, sp, 116	# %sfp, dd
	mov.n	a10, a4	# _278, _278
.L87:
	l32i	a7, sp, 128	# %sfp,
	addi	a8, sp, 52	#,,
	add.n	a4, a3, a7	# tmp1465, n,
	slli	a4, a4, 2	# tmp1467, tmp1465,
	add.n	a4, a8, a4	# ivtmp$122,, tmp1467
.L74:
	l32i.n	a7, a4, 0	# MEM[base: _1643, offset: 0B], MEM[base: _1643, offset: 0B]
	l32i.n	a8, a4, 8	# MEM[base: _1643, offset: 8B], MEM[base: _1643, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	addi.n	a3, a3, -1	# n, n,
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	sub	a7, a7, a8	# tmp1468, MEM[base: _1643, offset: 0B], MEM[base: _1643, offset: 8B]
	s32i.n	a7, a4, 0	# MEM[base: _1643, offset: 0B], tmp1468
	addi	a4, a4, -4	# ivtmp$122, ivtmp$122,
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	blt	a2, a3, .L74	# k, n,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a4, a5, 8	# MEM[base: _1618, offset: 8B], MEM[base: _1618, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a3, a5, 0	# MEM[base: _1618, offset: 0B], MEM[base: _1618, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a4, a4, 1	# tmp1471, MEM[base: _1618, offset: 8B],
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a3, a3, a4	# tmp1473, MEM[base: _1618, offset: 0B], tmp1471
	s32i.n	a3, a5, 0	# MEM[base: _1618, offset: 0B], tmp1473
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a2, a2, 1	# k, k,
	addi.n	a6, a6, 1	# ivtmp$138, ivtmp$138,
	addi.n	a5, a5, 4	# ivtmp$139, ivtmp$139,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	blt	a2, a13, .L75	# k, _2097,
	j	.L192		#
.L79:
	slli	a4, a2, 2	# _1773, k,
	addi	a9, sp, 52	#,,
	add.n	a3, a9, a4	# _1770,, _1773
	addi	a6, a3, -8	# tmp1477, _1770,
	addi	a5, a3, -4	# tmp1479, _1770,
	addi	a4, a4, -8	# tmp1481, _1773,
	l32i.n	a3, a6, 0	# MEM[(opus_int32 *)_1770 + 4294967288B], D__lsm0$39
	l32i.n	a6, a5, 0	# MEM[(opus_int32 *)_1770 + 4294967292B], D__lsm1$40
	add.n	a4, a9, a4	# ivtmp$114,, tmp1481
.L77:
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a5, a4, 8	# MEM[base: _1654, offset: 8B], _2110
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a2, a2, 1	# k, k,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a7, a5, 1	# tmp1482, _2110,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a3, a3, a7	# tmp1483, D__lsm0$39, tmp1482
	s32i.n	a3, a4, 0	# MEM[base: _1654, offset: 0B], tmp1483
	mov.n	a3, a6	# D__lsm0$39, D__lsm1$40
	addi.n	a4, a4, 4	# ivtmp$114, ivtmp$114,
	mov.n	a6, a5	# D__lsm1$40, _2110
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	bge	a15, a2, .L77	# dd, k,
	j	.L78		#
.L192:
	bge	a15, a2, .L79	# dd, k,
.L78:
	bgei	a15, 3, .L80	# dd,,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a2, 2	# k,
	j	.L81		#
.L68:
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a2, 2	# k,
	blti	a15, 3, .L79	# dd,,
	addi.n	a13, a15, 1	# _2097, dd,
	bge	a15, a13, .L82	# dd, _2097,
	mov.n	a13, a15	# _2097, dd
.L82:
	l32i	a10, sp, 172	# %sfp,
	l32r	a9, .LC1	#, tmp1729
	addi	a14, a10, -4	# tmp1753,,
	l32i	a11, sp, 240	# %sfp, ivtmp$131
	l32i	a10, sp, 168	# %sfp, _278
	l32i	a12, sp, 172	# %sfp, _1917
	addi	a5, sp, 52	# ivtmp$139,,
	movi.n	a6, 3	# ivtmp$138,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a2, 2	# k,
	s32i	a9, sp, 128	# %sfp, tmp1729
.L75:
	blt	a10, a2, .L130	# _278, k,
	blt	a6, a10, .L156	# ivtmp$138, _278,
.L130:
# @OPUS@\upstream\silk\A2NLSF.c:115:     for( k = dd; k > 0; k-- ) {
	mov.n	a3, a15	# n, dd
	j	.L87		#
.L157:
	l32i.n	a8, a12, 0	# *_1898, D__lsm0$33
	l32i.n	a7, a14, 0	# MEM[(opus_int32 *)_1898 + 4294967292B(OVF)], D__lsm1$34
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	mov.n	a3, a15	# n, dd
	s32i	a15, sp, 116	# %sfp, dd
	mov.n	a4, a11	# ivtmp$99, ivtmp$99
	mov.n	a15, a10	# _278, _278
.L88:
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	l32i.n	a10, a4, 4	# MEM[base: _1681, offset: 4B],
	addi	a9, a3, -3	# tmp1495, _1690,
	sub	a8, a10, a8	# D__lsm0$33,, D__lsm0$33
	l32i.n	a10, a4, 0	# MEM[base: _1681, offset: 0B],
	s32i.n	a8, a4, 4	# MEM[base: _1681, offset: 4B], D__lsm0$33
	sub	a7, a10, a7	# D__lsm1$34,, D__lsm1$34
	s32i.n	a7, a4, 0	# MEM[base: _1681, offset: 0B], D__lsm1$34
	addi	a3, a3, -2	# n, n,
	addi	a4, a4, -8	# ivtmp$99, ivtmp$99,
	blt	a6, a9, .L88	# ivtmp$106, tmp1495,
	mov.n	a4, a15	# _278, _278
	l32i	a15, sp, 116	# %sfp, dd
	mov.n	a10, a4	# _278, _278
.L99:
	l32i	a7, sp, 128	# %sfp,
	add.n	a4, a3, a7	# tmp1496, n,
	slli	a4, a4, 2	# tmp1498, tmp1496,
	add.n	a4, sp, a4	# ivtmp$90,, tmp1498
.L89:
	l32i.n	a7, a4, 0	# MEM[base: _1698, offset: 0B], MEM[base: _1698, offset: 0B]
	l32i.n	a8, a4, 8	# MEM[base: _1698, offset: 8B], MEM[base: _1698, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	addi.n	a3, a3, -1	# n, n,
# @OPUS@\upstream\silk\A2NLSF.c:56:             p[ n - 2 ] -= p[ n ];
	sub	a7, a7, a8	# tmp1499, MEM[base: _1698, offset: 0B], MEM[base: _1698, offset: 8B]
	s32i.n	a7, a4, 0	# MEM[base: _1698, offset: 0B], tmp1499
	addi	a4, a4, -4	# ivtmp$90, ivtmp$90,
# @OPUS@\upstream\silk\A2NLSF.c:55:         for( n = dd; n > k; n-- ) {
	blt	a2, a3, .L89	# k, n,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a4, a5, 8	# MEM[base: _1673, offset: 8B], MEM[base: _1673, offset: 8B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a3, a5, 0	# MEM[base: _1673, offset: 0B], MEM[base: _1673, offset: 0B]
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a4, a4, 1	# tmp1502, MEM[base: _1673, offset: 8B],
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a3, a3, a4	# tmp1504, MEM[base: _1673, offset: 0B], tmp1502
	s32i.n	a3, a5, 0	# MEM[base: _1673, offset: 0B], tmp1504
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a2, a2, 1	# k, k,
	addi.n	a6, a6, 1	# ivtmp$106, ivtmp$106,
	addi.n	a5, a5, 4	# ivtmp$107, ivtmp$107,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	blt	a2, a13, .L90	# k, _2139,
	j	.L193		#
.L81:
	slli	a4, a2, 2	# _1784, k,
	add.n	a3, sp, a4	# _1783,, _1784
	addi	a6, a3, -8	# tmp1507, _1783,
	addi	a5, a3, -4	# tmp1509, _1783,
	addi	a4, a4, -8	# tmp1510, _1784,
	l32i.n	a3, a6, 0	# MEM[(opus_int32 *)_1783 + 4294967288B], D__lsm0$37
	l32i.n	a6, a5, 0	# MEM[(opus_int32 *)_1783 + 4294967292B], D__lsm1$38
	add.n	a4, sp, a4	# ivtmp$82,, tmp1510
.L92:
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	l32i.n	a5, a4, 8	# MEM[base: _1709, offset: 8B], _2202
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	addi.n	a2, a2, 1	# k, k,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	slli	a7, a5, 1	# tmp1511, _2202,
# @OPUS@\upstream\silk\A2NLSF.c:58:         p[ k - 2 ] -= silk_LSHIFT( p[ k ], 1 );
	sub	a3, a3, a7	# tmp1512, D__lsm0$37, tmp1511
	s32i.n	a3, a4, 0	# MEM[base: _1709, offset: 0B], tmp1512
	mov.n	a3, a6	# D__lsm0$37, D__lsm1$38
	addi.n	a4, a4, 4	# ivtmp$82, ivtmp$82,
	mov.n	a6, a5	# D__lsm1$38, _2202
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	bge	a15, a2, .L92	# dd, k,
	j	.L93		#
.L80:
	addi.n	a13, a15, 1	# _2139, dd,
	bge	a15, a13, .L94	# dd, _2139,
	mov.n	a13, a15	# _2139, dd
.L94:
	l32i	a8, sp, 176	# %sfp,
	l32r	a9, .LC1	#, tmp1729
	l32i	a10, sp, 168	# %sfp, _278
	l32i	a11, sp, 244	# %sfp, ivtmp$99
	mov.n	a5, sp	# ivtmp$107,
# @OPUS@\upstream\silk\A2NLSF.c:54:     for( k = 2; k <= dd; k++ ) {
	movi.n	a6, 3	# ivtmp$106,
	movi.n	a2, 2	# k,
	addi	a14, a8, -4	# tmp1752,,
	mov.n	a12, a8	# _1931,
	s32i	a9, sp, 128	# %sfp, tmp1729
.L90:
	blt	a10, a2, .L131	# _278, k,
	blt	a6, a10, .L157	# ivtmp$106, _278,
.L131:
	mov.n	a3, a15	# n, dd
	j	.L99		#
.L193:
	bge	a15, a2, .L81	# dd, k,
.L93:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a9, sp, 188	# %sfp,
	l32i.n	a14, a9, 0	# *_265, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:75:     if ( opus_likely( 8 == dd ) )
	bnei	a15, 8, .L69	# dd,,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	l32i	a10, sp, 132	# %sfp,
	l32i	a11, sp, 124	# %sfp,
	l32i	a5, sp, 80	# MEM[(opus_int32 *)&P + 28B], MEM[(opus_int32 *)&P + 28B]
	extui	a3, a14, 0, 16	# tmp1521, prephitmp_1669,
	mull	a2, a14, a10	# tmp1523, prephitmp_1669,
	srai	a4, a14, 16	# tmp1526, prephitmp_1669,
	mull	a4, a4, a11	# tmp1527, tmp1526,
	mull	a3, a3, a11	# tmp1522, tmp1521,
	add.n	a2, a2, a5	# tmp1524, tmp1523, MEM[(opus_int32 *)&P + 28B]
	add.n	a2, a2, a4	# _1039, tmp1524, tmp1527
	srai	a3, a3, 16	# _726, tmp1522,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a3, a3, a2	# y32, _726, _1039
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	extui	a2, a3, 0, 16	# tmp1528, y32,
	mull	a4, a3, a10	# tmp1530, y32,
	l32i	a5, sp, 76	# MEM[(opus_int32 *)&P + 24B], MEM[(opus_int32 *)&P + 24B]
	srai	a3, a3, 16	# tmp1533, y32,
	mull	a2, a2, a11	# tmp1529, tmp1528,
	mull	a3, a3, a11	# tmp1534, tmp1533,
	add.n	a4, a4, a5	# tmp1531, tmp1530, MEM[(opus_int32 *)&P + 24B]
	add.n	a3, a4, a3	# _1040, tmp1531, tmp1534
	srai	a2, a2, 16	# _739, tmp1529,
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a2, a2, a3	# y32, _739, _1040
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	extui	a3, a2, 0, 16	# tmp1535, y32,
	mull	a4, a2, a10	# tmp1537, y32,
	l32i	a5, sp, 72	# MEM[(opus_int32 *)&P + 20B], MEM[(opus_int32 *)&P + 20B]
	srai	a2, a2, 16	# tmp1540, y32,
	mull	a3, a3, a11	# tmp1536, tmp1535,
	mull	a2, a2, a11	# tmp1541, tmp1540,
	add.n	a4, a4, a5	# tmp1538, tmp1537, MEM[(opus_int32 *)&P + 20B]
	add.n	a2, a4, a2	# _1092, tmp1538, tmp1541
	srai	a3, a3, 16	# _749, tmp1536,
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a3, a3, a2	# y32, _749, _1092
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	extui	a4, a3, 0, 16	# tmp1542, y32,
	mull	a2, a3, a10	# tmp1544, y32,
	l32i	a5, sp, 68	# MEM[(opus_int32 *)&P + 16B], MEM[(opus_int32 *)&P + 16B]
	srai	a3, a3, 16	# tmp1547, y32,
	mull	a3, a3, a11	# tmp1548, tmp1547,
	mull	a4, a4, a11	# tmp1543, tmp1542,
	add.n	a2, a2, a5	# tmp1545, tmp1544, MEM[(opus_int32 *)&P + 16B]
	srai	a4, a4, 16	# _759, tmp1543,
	add.n	a2, a2, a3	# _246, tmp1545, tmp1548
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a2, a2, a4	# y32, _246, _759
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	extui	a3, a2, 0, 16	# tmp1549, y32,
	mull	a4, a2, a10	# tmp1551, y32,
	l32i	a5, sp, 64	# MEM[(opus_int32 *)&P + 12B], MEM[(opus_int32 *)&P + 12B]
	srai	a2, a2, 16	# tmp1554, y32,
	mull	a3, a3, a11	# tmp1550, tmp1549,
	mull	a2, a2, a11	# tmp1555, tmp1554,
	add.n	a4, a4, a5	# tmp1552, tmp1551, MEM[(opus_int32 *)&P + 12B]
	srai	a3, a3, 16	# _769, tmp1550,
	add.n	a2, a4, a2	# _1091, tmp1552, tmp1555
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a2, a3, a2	# y32, _769, _1091
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	extui	a4, a2, 0, 16	# tmp1556, y32,
	mull	a3, a2, a10	# tmp1558, y32,
	l32i.n	a5, sp, 60	# MEM[(opus_int32 *)&P + 8B], MEM[(opus_int32 *)&P + 8B]
	srai	a2, a2, 16	# tmp1561, y32,
	mull	a2, a2, a11	# tmp1562, tmp1561,
	mull	a4, a4, a11	# tmp1557, tmp1556,
	add.n	a3, a3, a5	# tmp1559, tmp1558, MEM[(opus_int32 *)&P + 8B]
	srai	a4, a4, 16	# _779, tmp1557,
	add.n	a3, a3, a2	# _456, tmp1559, tmp1562
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a3, a3, a4	# y32, _456, _779
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	extui	a4, a3, 0, 16	# tmp1563, y32,
	mull	a2, a3, a10	# tmp1565, y32,
	l32i.n	a5, sp, 56	# MEM[(opus_int32 *)&P + 4B], MEM[(opus_int32 *)&P + 4B]
	srai	a3, a3, 16	# tmp1568, y32,
	mull	a3, a3, a11	# tmp1569, tmp1568,
	mull	a4, a4, a11	# tmp1564, tmp1563,
	add.n	a2, a2, a5	# tmp1566, tmp1565, MEM[(opus_int32 *)&P + 4B]
	srai	a4, a4, 16	# _789, tmp1564,
	add.n	a2, a2, a3	# _718, tmp1566, tmp1569
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a2, a2, a4	# y32, _718, _789
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	extui	a3, a2, 0, 16	# tmp1570, y32,
	mull	a13, a2, a10	# tmp1572, y32,
	l32i.n	a4, sp, 52	# MEM[(opus_int32 *)&P], MEM[(opus_int32 *)&P]
	srai	a2, a2, 16	# tmp1575, y32,
	mull	a3, a3, a11	# tmp1571, tmp1570,
	mull	a2, a2, a11	# tmp1576, tmp1575,
	add.n	a13, a13, a4	# tmp1573, tmp1572, MEM[(opus_int32 *)&P]
	srai	a3, a3, 16	# _799, tmp1571,
	add.n	a2, a13, a2	# _574, tmp1573, tmp1576
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a13, a2, a3	# ylo, _574, _799
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	bltz	a13, .L100	# ylo,
	l32i	a5, sp, 196	# %sfp,
	l32i	a6, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a4, 0	#,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	movi.n	a7, 1	#,
	slli	a8, a5, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a4, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	s32i	a5, sp, 128	# %sfp,
	s32i	a6, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:251:                 p = P;                            /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
# @OPUS@\upstream\silk\A2NLSF.c:261:                     root_ix = 0;                  /* Index of current root */
	s32i	a4, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a7, sp, 120	# %sfp,
	s32i	a8, sp, 152	# %sfp,
	j	.L42		#
.L69:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	l32i	a9, sp, 168	# %sfp,
	bltz	a9, .L101	#,
	l32i	a5, sp, 248	# %sfp, ivtmp$75
	mov.n	a13, a14	# ylo, prephitmp_1669
	l32i	a6, sp, 132	# %sfp, _290
	l32i	a4, sp, 124	# %sfp, _2122
	l32i	a10, sp, 112	# %sfp,
	j	.L102		#
.L123:
	mov.n	a5, a7	# ivtmp$75, ivtmp$75
.L102:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a13, 16	# tmp1580, ylo,
	extui	a3, a13, 0, 16	# tmp1578, ylo,
	l32i.n	a7, a5, 0	# MEM[base: _1719, offset: 0B], MEM[base: _1719, offset: 0B]
	mull	a2, a2, a4	# tmp1581, tmp1580, _2122
	mull	a13, a13, a6	# tmp1584, ylo, _290
	mull	a3, a3, a4	# tmp1579, tmp1578, _2122
	add.n	a2, a2, a7	# tmp1582, tmp1581, MEM[base: _1719, offset: 0B]
	srai	a3, a3, 16	# _817, tmp1579,
	add.n	a2, a2, a13	# _276, tmp1582, tmp1584
	addi	a7, a5, -4	# ivtmp$75, ivtmp$75,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a13, a2, a3	# ylo, _276, _817
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a10, a5, .L123	#, ivtmp$75,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	bltz	a13, .L103	# ylo,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a11, 0	#,
	s32i	a11, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	l32i	a5, sp, 196	# %sfp,
	l32i	a6, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:261:                     root_ix = 0;                  /* Index of current root */
	l32i	a7, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	movi.n	a8, 1	#,
	slli	a9, a5, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	s32i	a5, sp, 128	# %sfp,
	s32i	a6, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:251:                 p = P;                            /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
# @OPUS@\upstream\silk\A2NLSF.c:261:                     root_ix = 0;                  /* Index of current root */
	s32i	a7, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a8, sp, 120	# %sfp,
	s32i	a9, sp, 152	# %sfp,
	j	.L42		#
.L124:
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	mov.n	a5, a8	# ivtmp$68, ivtmp$68
.L104:
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	srai	a2, a13, 16	# tmp1587, ylo,
	extui	a3, a13, 0, 16	# tmp1585, ylo,
	l32i.n	a8, a5, 0	# MEM[base: _1729, offset: 0B], MEM[base: _1729, offset: 0B]
	mull	a2, a2, a4	# tmp1588, tmp1587, _2122
	mull	a13, a13, a6	# tmp1591, ylo, _290
	mull	a3, a3, a4	# tmp1586, tmp1585, _2122
	add.n	a2, a2, a8	# tmp1589, tmp1588, MEM[base: _1729, offset: 0B]
	srai	a3, a3, 16	# _1027, tmp1586,
	add.n	a2, a2, a13	# _281, tmp1589, tmp1591
	addi	a8, a5, -4	# ivtmp$68, ivtmp$68,
# @OPUS@\upstream\silk\A2NLSF.c:89:             y32 = silk_SMLAWW( p[ n ], y32, x_Q16 );    /* Q16 */
	add.n	a13, a2, a3	# ylo, _281, _1027
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	bne	a7, a5, .L124	# _1728, ivtmp$68,
	l32i	a7, sp, 196	# %sfp,
	l32i	a11, sp, 196	# %sfp,
	l32i	a5, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	movi.n	a10, 1	#,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a6, 0	#,
	slli	a7, a7, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	s32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	s32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:88:         for( n = dd - 1; n >= 0; n-- ) {
	s32i	a5, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:257:                     p = Q;                        /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a6, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a10, sp, 120	# %sfp,
	s32i	a7, sp, 152	# %sfp,
	j	.L42		#
.L100:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a8, sp, 208	# %sfp,
	mov.n	a9, a10	#,
	l32i.n	a14, a8, 0	# *_266, prephitmp_1669
	l32i.n	a5, sp, 28	# MEM[(opus_int32 *)&Q + 28B], MEM[(opus_int32 *)&Q + 28B]
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	mull	a2, a14, a10	# tmp1595, prephitmp_1669, tmp9
	l32i	a10, sp, 124	# %sfp,
	extui	a3, a14, 0, 16	# tmp1593, prephitmp_1669,
	srai	a4, a14, 16	# tmp1598, prephitmp_1669,
	mull	a4, a4, a10	# tmp1599, tmp1598,
	mull	a3, a3, a10	# tmp1594, tmp1593,
	add.n	a2, a2, a5	# tmp1596, tmp1595, MEM[(opus_int32 *)&Q + 28B]
	srai	a3, a3, 16	# _936, tmp1594,
	add.n	a2, a2, a4	# _692, tmp1596, tmp1599
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a2, a2, a3	# y32, _692, _936
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	mull	a3, a2, a9	# tmp1602, y32,
	extui	a4, a2, 0, 16	# tmp1600, y32,
	l32i.n	a5, sp, 24	# MEM[(opus_int32 *)&Q + 24B], MEM[(opus_int32 *)&Q + 24B]
	srai	a2, a2, 16	# tmp1605, y32,
	mull	a2, a2, a10	# tmp1606, tmp1605,
	mull	a4, a4, a10	# tmp1601, tmp1600,
	add.n	a3, a3, a5	# tmp1603, tmp1602, MEM[(opus_int32 *)&Q + 24B]
	srai	a4, a4, 16	# _949, tmp1601,
	add.n	a3, a3, a2	# _89, tmp1603, tmp1606
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a3, a3, a4	# y32, _89, _949
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	mull	a2, a3, a9	# tmp1609, y32,
	extui	a4, a3, 0, 16	# tmp1607, y32,
	l32i.n	a5, sp, 20	# MEM[(opus_int32 *)&Q + 20B], MEM[(opus_int32 *)&Q + 20B]
	srai	a3, a3, 16	# tmp1612, y32,
	mull	a3, a3, a10	# tmp1613, tmp1612,
	mull	a4, a4, a10	# tmp1608, tmp1607,
	add.n	a2, a2, a5	# tmp1610, tmp1609, MEM[(opus_int32 *)&Q + 20B]
	srai	a4, a4, 16	# _959, tmp1608,
	add.n	a2, a2, a3	# _90, tmp1610, tmp1613
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a2, a2, a4	# y32, _90, _959
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	mull	a4, a2, a9	# tmp1616, y32,
	extui	a3, a2, 0, 16	# tmp1614, y32,
	l32i.n	a5, sp, 16	# MEM[(opus_int32 *)&Q + 16B], MEM[(opus_int32 *)&Q + 16B]
	srai	a2, a2, 16	# tmp1619, y32,
	mull	a3, a3, a10	# tmp1615, tmp1614,
	mull	a2, a2, a10	# tmp1620, tmp1619,
	add.n	a4, a4, a5	# tmp1617, tmp1616, MEM[(opus_int32 *)&Q + 16B]
	add.n	a2, a4, a2	# _1081, tmp1617, tmp1620
	srai	a3, a3, 16	# _969, tmp1615,
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a3, a3, a2	# y32, _969, _1081
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	mull	a4, a3, a9	# tmp1623, y32,
	extui	a2, a3, 0, 16	# tmp1621, y32,
	l32i.n	a5, sp, 12	# MEM[(opus_int32 *)&Q + 12B], MEM[(opus_int32 *)&Q + 12B]
	srai	a3, a3, 16	# tmp1626, y32,
	mull	a2, a2, a10	# tmp1622, tmp1621,
	mull	a3, a3, a10	# tmp1627, tmp1626,
	add.n	a4, a4, a5	# tmp1624, tmp1623, MEM[(opus_int32 *)&Q + 12B]
	add.n	a3, a4, a3	# _1043, tmp1624, tmp1627
	srai	a2, a2, 16	# _979, tmp1622,
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a2, a2, a3	# y32, _979, _1043
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	mull	a4, a2, a9	# tmp1630, y32,
	extui	a3, a2, 0, 16	# tmp1628, y32,
	l32i.n	a5, sp, 8	# MEM[(opus_int32 *)&Q + 8B], MEM[(opus_int32 *)&Q + 8B]
	srai	a2, a2, 16	# tmp1633, y32,
	mull	a3, a3, a10	# tmp1629, tmp1628,
	mull	a2, a2, a10	# tmp1634, tmp1633,
	add.n	a4, a4, a5	# tmp1631, tmp1630, MEM[(opus_int32 *)&Q + 8B]
	add.n	a2, a4, a2	# _1044, tmp1631, tmp1634
	srai	a3, a3, 16	# _989, tmp1629,
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a3, a3, a2	# y32, _989, _1044
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	mull	a4, a3, a9	# tmp1637, y32,
	extui	a2, a3, 0, 16	# tmp1635, y32,
	l32i.n	a5, sp, 4	# MEM[(opus_int32 *)&Q + 4B], MEM[(opus_int32 *)&Q + 4B]
	srai	a3, a3, 16	# tmp1640, y32,
	mull	a2, a2, a10	# tmp1636, tmp1635,
	mull	a3, a3, a10	# tmp1641, tmp1640,
	add.n	a4, a4, a5	# tmp1638, tmp1637, MEM[(opus_int32 *)&Q + 4B]
	add.n	a3, a4, a3	# _1047, tmp1638, tmp1641
	srai	a2, a2, 16	# _999, tmp1636,
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a2, a2, a3	# y32, _999, _1047
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	mull	a4, a2, a9	# tmp1644, y32,
	extui	a13, a2, 0, 16	# tmp1642, y32,
	srai	a2, a2, 16	# tmp1647, y32,
	mull	a3, a2, a10	# tmp1648, tmp1647,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	movi.n	a11, 1	#,
	l32i.n	a2, sp, 0	# MEM[(opus_int32 *)&Q], MEM[(opus_int32 *)&Q]
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	mull	a13, a13, a10	# tmp1643, tmp1642,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	s32i	a11, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	l32i	a6, sp, 196	# %sfp,
	add.n	a2, a4, a2	# tmp1645, tmp1644, MEM[(opus_int32 *)&Q]
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	l32i	a5, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	l32i	a7, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	l32i	a9, sp, 136	# %sfp,
	add.n	a3, a2, a3	# _1048, tmp1645, tmp1648
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	srai	a13, a13, 16	# _1009, tmp1643,
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	movi.n	a2, 0	# tmp1592,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a8, 0	#,
	slli	a10, a6, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	s16i	a2, a5, 0	# *NLSF_103(D), tmp1592
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a13, a13, a3	# ylo, _1009, _1048
	s32i	a6, sp, 128	# %sfp,
	s32i	a7, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:257:                     p = Q;                        /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a9, sp, 120	# %sfp,
	s32i	a10, sp, 152	# %sfp,
	j	.L42		#
.L105:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a11, sp, 208	# %sfp,
	l32i	a6, sp, 196	# %sfp,
	l32i.n	a14, a11, 0	# *_266, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	l32i	a5, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a7, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	movi.n	a4, 1	#,
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	movi.n	a2, 0	# tmp1649,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a8, 0	#,
	slli	a9, a6, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:259:                     root_ix = 1;                  /* Index of current root */
	s32i	a4, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	s16i	a2, a5, 0	# *NLSF_103(D), tmp1649
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a13, a14	# ylo, prephitmp_1669
	s32i	a6, sp, 128	# %sfp,
	s32i	a7, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:257:                     p = Q;                        /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a8, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a4, sp, 120	# %sfp,
	s32i	a9, sp, 152	# %sfp,
	j	.L42		#
.L101:
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	bltz	a14, .L105	# prephitmp_1669,
	l32i	a7, sp, 196	# %sfp,
	l32i	a11, sp, 196	# %sfp,
	l32i	a5, sp, 220	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	movi.n	a10, 0	#,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	movi.n	a6, 1	#,
	slli	a7, a7, 4	#,,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	s32i	a11, sp, 128	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:234:             thr = 0;
	s32i	a10, sp, 144	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:254:                 if( ylo < 0 ) {
	mov.n	a13, a14	# ylo, prephitmp_1669
	s32i	a5, sp, 140	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:251:                 p = P;                            /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
# @OPUS@\upstream\silk\A2NLSF.c:261:                     root_ix = 0;                  /* Index of current root */
	s32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:263:                 k = 1;                            /* Reset loop counter */
	s32i	a6, sp, 120	# %sfp,
	s32i	a7, sp, 152	# %sfp,
	j	.L42		#
.L106:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a9, sp, 208	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	l32i	a10, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i.n	a13, a9, 0	# *_266, ylo
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	movi.n	a2, 0	# tmp1650,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	movi.n	a4, 1	#,
	slli	a5, a5, 2	#,,
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	s16i	a2, a10, 0	# *NLSF_103(D), tmp1650
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a14, a13	# prephitmp_1669, ylo
# @OPUS@\upstream\silk\A2NLSF.c:159:         p = Q;                      /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	s32i	a4, sp, 136	# %sfp,
	s32i	a5, sp, 212	# %sfp,
	j	.L38		#
.L189:
# @OPUS@\upstream\silk\A2NLSF.c:156:     if( ylo < 0 ) {
	bltz	a13, .L106	# ylo,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	movi.n	a6, 0	#,
	slli	a7, a5, 2	#, tmp7,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a14, a13	# prephitmp_1669, ylo
# @OPUS@\upstream\silk\A2NLSF.c:151:     p = P;                          /* Pointer to polynomial */
	addi	a11, sp, 52	# p,,
# @OPUS@\upstream\silk\A2NLSF.c:163:         root_ix = 0;                /* Index of current root */
	s32i	a6, sp, 136	# %sfp,
	s32i	a7, sp, 212	# %sfp,
	j	.L38		#
.L37:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a9, sp, 208	# %sfp,
	l32i.n	a4, sp, 28	# MEM[(opus_int32 *)&Q + 28B], MEM[(opus_int32 *)&Q + 28B]
	l32i.n	a14, a9, 0	# *_266, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	l32i	a11, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	extui	a3, a14, 0, 16	# tmp1652, prephitmp_1669,
	mull	a6, a10, a14	# tmp1654,, prephitmp_1669
	srai	a5, a14, 16	# tmp1657, prephitmp_1669,
	mull	a5, a5, a2	# tmp1658, tmp1657, _158
	mull	a3, a3, a2	# tmp1653, tmp1652, _158
	add.n	a6, a6, a4	# tmp1655, tmp1654, MEM[(opus_int32 *)&Q + 28B]
	add.n	a4, a6, a5	# _928, tmp1655, tmp1658
	srai	a3, a3, 16	# _372, tmp1653,
# @OPUS@\upstream\silk\A2NLSF.c:77:         y32 = silk_SMLAWW( p[ 7 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _372, _928
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1661,, y32
	extui	a3, a4, 0, 16	# tmp1659, y32,
	l32i.n	a5, sp, 24	# MEM[(opus_int32 *)&Q + 24B], MEM[(opus_int32 *)&Q + 24B]
	srai	a4, a4, 16	# tmp1664, y32,
	mull	a3, a3, a2	# tmp1660, tmp1659, _158
	mull	a4, a4, a2	# tmp1665, tmp1664, _158
	add.n	a5, a6, a5	# tmp1662, tmp1661, MEM[(opus_int32 *)&Q + 24B]
	srai	a3, a3, 16	# _385, tmp1660,
	add.n	a4, a5, a4	# _926, tmp1662, tmp1665
# @OPUS@\upstream\silk\A2NLSF.c:78:         y32 = silk_SMLAWW( p[ 6 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _385, _926
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1668,, y32
	extui	a3, a4, 0, 16	# tmp1666, y32,
	l32i.n	a5, sp, 20	# MEM[(opus_int32 *)&Q + 20B], MEM[(opus_int32 *)&Q + 20B]
	srai	a4, a4, 16	# tmp1671, y32,
	mull	a3, a3, a2	# tmp1667, tmp1666, _158
	mull	a4, a4, a2	# tmp1672, tmp1671, _158
	add.n	a5, a6, a5	# tmp1669, tmp1668, MEM[(opus_int32 *)&Q + 20B]
	srai	a3, a3, 16	# _395, tmp1667,
	add.n	a4, a5, a4	# _1061, tmp1669, tmp1672
# @OPUS@\upstream\silk\A2NLSF.c:79:         y32 = silk_SMLAWW( p[ 5 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _395, _1061
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1675,, y32
	extui	a3, a4, 0, 16	# tmp1673, y32,
	l32i.n	a5, sp, 16	# MEM[(opus_int32 *)&Q + 16B], MEM[(opus_int32 *)&Q + 16B]
	srai	a4, a4, 16	# tmp1678, y32,
	mull	a3, a3, a2	# tmp1674, tmp1673, _158
	mull	a4, a4, a2	# tmp1679, tmp1678, _158
	add.n	a5, a6, a5	# tmp1676, tmp1675, MEM[(opus_int32 *)&Q + 16B]
	srai	a3, a3, 16	# _405, tmp1674,
	add.n	a4, a5, a4	# _1086, tmp1676, tmp1679
# @OPUS@\upstream\silk\A2NLSF.c:80:         y32 = silk_SMLAWW( p[ 4 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _405, _1086
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1682,, y32
	extui	a3, a4, 0, 16	# tmp1680, y32,
	l32i.n	a5, sp, 12	# MEM[(opus_int32 *)&Q + 12B], MEM[(opus_int32 *)&Q + 12B]
	srai	a4, a4, 16	# tmp1685, y32,
	mull	a3, a3, a2	# tmp1681, tmp1680, _158
	mull	a4, a4, a2	# tmp1686, tmp1685, _158
	add.n	a5, a6, a5	# tmp1683, tmp1682, MEM[(opus_int32 *)&Q + 12B]
	srai	a3, a3, 16	# _415, tmp1681,
	add.n	a4, a5, a4	# _1037, tmp1683, tmp1686
# @OPUS@\upstream\silk\A2NLSF.c:81:         y32 = silk_SMLAWW( p[ 3 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _415, _1037
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1689,, y32
	extui	a3, a4, 0, 16	# tmp1687, y32,
	l32i.n	a5, sp, 8	# MEM[(opus_int32 *)&Q + 8B], MEM[(opus_int32 *)&Q + 8B]
	srai	a4, a4, 16	# tmp1692, y32,
	mull	a3, a3, a2	# tmp1688, tmp1687, _158
	mull	a4, a4, a2	# tmp1693, tmp1692, _158
	add.n	a5, a6, a5	# tmp1690, tmp1689, MEM[(opus_int32 *)&Q + 8B]
	srai	a3, a3, 16	# _425, tmp1688,
	add.n	a4, a5, a4	# _1038, tmp1690, tmp1693
# @OPUS@\upstream\silk\A2NLSF.c:82:         y32 = silk_SMLAWW( p[ 2 ], y32, x_Q16 );
	add.n	a4, a3, a4	# y32, _425, _1038
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	mull	a6, a10, a4	# tmp1696,, y32
	extui	a3, a4, 0, 16	# tmp1694, y32,
	l32i.n	a5, sp, 4	# MEM[(opus_int32 *)&Q + 4B], MEM[(opus_int32 *)&Q + 4B]
	srai	a4, a4, 16	# tmp1699, y32,
	mull	a4, a4, a2	# tmp1700, tmp1699, _158
	mull	a3, a3, a2	# tmp1695, tmp1694, _158
	add.n	a5, a6, a5	# tmp1697, tmp1696, MEM[(opus_int32 *)&Q + 4B]
	add.n	a5, a5, a4	# _1041, tmp1697, tmp1700
	srai	a3, a3, 16	# _435, tmp1695,
# @OPUS@\upstream\silk\A2NLSF.c:83:         y32 = silk_SMLAWW( p[ 1 ], y32, x_Q16 );
	add.n	a3, a3, a5	# y32, _435, _1041
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	mull	a5, a10, a3	# tmp1703,, y32
	extui	a4, a3, 0, 16	# tmp1701, y32,
	srai	a3, a3, 16	# tmp1706, y32,
	mull	a3, a3, a2	# tmp1707, tmp1706, _158
	mull	a4, a4, a2	# tmp1702, tmp1701, _158
	l32i.n	a2, sp, 0	# MEM[(opus_int32 *)&Q], MEM[(opus_int32 *)&Q]
	srai	a4, a4, 16	# _445, tmp1702,
	add.n	a2, a5, a2	# tmp1704, tmp1703, MEM[(opus_int32 *)&Q]
	add.n	a2, a2, a3	# _1042, tmp1704, tmp1707
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	movi.n	a5, 7	#,
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	movi.n	a3, 0	# tmp1651,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	movi.n	a6, 1	#,
	movi.n	a7, 0x1c	#,
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	s16i	a3, a11, 0	# *NLSF_103(D), tmp1651
# @OPUS@\upstream\silk\A2NLSF.c:84:         y32 = silk_SMLAWW( p[ 0 ], y32, x_Q16 );
	add.n	a13, a4, a2	# ylo, _445, _1042
	s32i	a5, sp, 168	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:159:         p = Q;                      /* Pointer to polynomial */
	mov.n	a11, sp	# p,
# @OPUS@\upstream\silk\A2NLSF.c:161:         root_ix = 1;                /* Index of current root */
	s32i	a6, sp, 136	# %sfp,
	s32i	a7, sp, 212	# %sfp,
	j	.L38		#
.L103:
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a8, sp, 208	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	l32i	a9, sp, 204	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i.n	a14, a8, 0	# *_266, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:256:                     NLSF[ 0 ] = 0;
	movi.n	a2, 0	# tmp1708,
	s16i	a2, a9, 0	# *NLSF_103(D), tmp1708
	mov.n	a7, sp	# _1728,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a5, sp, 252	# %sfp, ivtmp$68
	mov.n	a13, a14	# ylo, prephitmp_1669
	l32i	a6, sp, 132	# %sfp, _290
	l32i	a4, sp, 124	# %sfp, _2122
	j	.L104		#
.L40:
	l32i	a10, sp, 208	# %sfp,
	l32i	a6, sp, 212	# %sfp,
	l32i.n	a14, a10, 0	# *_266, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:158:         NLSF[ 0 ] = 0;
	l32i	a11, sp, 204	# %sfp,
	movi.n	a2, 0	# tmp1710,
	add.n	a4, sp, a6	# ivtmp$172,,
	s16i	a2, a11, 0	# *NLSF_103(D), tmp1710
	srai	a5, a9, 16	# _2220, tmp1721,
	mov.n	a6, sp	# _1552,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	mov.n	a13, a14	# ylo, prephitmp_1669
	l32i	a7, sp, 132	# %sfp, _290
	j	.L41		#
.L28:
# @OPUS@\upstream\silk\A2NLSF.c:153:     xlo = silk_LSFCosTab_FIX_Q12[ 0 ]; /* Q12*/
	l32r	a7, .LC2	#,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i	a8, sp, 188	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:153:     xlo = silk_LSFCosTab_FIX_Q12[ 0 ]; /* Q12*/
	l16si	a9, a7, 0	# silk_LSFCosTab_FIX_Q12,
# @OPUS@\upstream\silk\A2NLSF.c:72:     y32 = p[ dd ];                                  /* Q16 */
	l32i.n	a14, a8, 0	# *_265, prephitmp_1669
# @OPUS@\upstream\silk\A2NLSF.c:73:     x_Q16 = silk_LSHIFT( x, 4 );
	slli	a8, a9, 4	# _343,,
	srai	a2, a8, 15	# tmp1716, _343,
	addi.n	a2, a2, 1	# tmp1717, tmp1716,
	srai	a2, a2, 1	#, tmp1717,
# @OPUS@\upstream\silk\A2NLSF.c:153:     xlo = silk_LSFCosTab_FIX_Q12[ 0 ]; /* Q12*/
	s32i	a7, sp, 184	# %sfp,
	s32i	a9, sp, 220	# %sfp,
	s32i	a6, sp, 168	# %sfp, _278
	s32i	a2, sp, 132	# %sfp,
# @OPUS@\upstream\silk\A2NLSF.c:75:     if ( opus_likely( 8 == dd ) )
	beqi	a15, 8, .L107	# dd,,
	j	.L35		#
.L1:
# @OPUS@\upstream\silk\A2NLSF.c:267: }
	l32i	a0, sp, 300	#,
	movi	a9, 0x130	#,
	l32i	a12, sp, 296	#,
	l32i	a13, sp, 292	#,
	l32i	a14, sp, 288	#,
	l32i	a15, sp, 284	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_A2NLSF, .-silk_A2NLSF
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
