# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/schur_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"schur_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\schur_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur_FIX.c.s.raw
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
	.section	.text.silk_schur,"ax",@progbits
	.literal_position
	.literal .LC0, -32440
	.literal .LC1, 32440
	.literal .LC2, -32768
	.literal .LC3, 32767
	.align	4
	.global	silk_schur
	.type	silk_schur, @function
# Function: silk_schur
# Module: upstream/silk/fixed/schur_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Faster than schur64(), but much less accurate.                       */
# C context: /* uses SMLAWB(), requiring armv5E and higher.                          */
# C context: opus_int32 silk_schur(                              /* O    Returns residual energy                                     */
# C context: opus_int16                  *rc_Q15,            /* O    reflection coefficients [order] Q15                         */
# C context: const opus_int32            *c,                 /* I    correlations [order+1]                                      */
# C context: const opus_int32            order               /* I    prediction order                                            */
# C context: )
silk_schur:
	movi	a9, 0x100	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:49:     lz = silk_CLZ32( c[ 0 ] );
	l32i.n	a5, a3, 0	# *c_85(D), _1
# @OPUS@\upstream\silk\fixed\schur_FIX.c:41: {
	s32i	a0, sp, 252	#,
	s32i	a12, sp, 248	#,
	s32i	a13, sp, 244	#,
	s32i	a14, sp, 240	#,
	s32i	a15, sp, 236	#,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:41: {
	s32i	a2, sp, 216	# %sfp, rc_Q15
	s32i	a4, sp, 208	# %sfp, order
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L23	# _1,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a5, a5	# iftmp$12_101, _1
# @OPUS@\upstream\silk\fixed\schur_FIX.c:53:     if( lz < 2 ) {
	bgei	a5, 2, .L3	# iftmp$12_101,,
	mov.n	a5, sp	# ivtmp$35,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:52:     k = 0;
	movi.n	a6, 0	# k,
.L4:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:56:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_RSHIFT( c[ k ], 1 );
	l32i.n	a2, a3, 0	# MEM[base: _233, offset: 0B], MEM[base: _233, offset: 0B]
# @OPUS@\upstream\silk\fixed\schur_FIX.c:57:         } while( ++k <= order );
	addi.n	a6, a6, 1	# k, k,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:56:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_RSHIFT( c[ k ], 1 );
	srai	a2, a2, 1	# _6, MEM[base: _233, offset: 0B],
# @OPUS@\upstream\silk\fixed\schur_FIX.c:56:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_RSHIFT( c[ k ], 1 );
	s32i.n	a2, a5, 4	# MEM[base: _230, offset: 4B], _6
# @OPUS@\upstream\silk\fixed\schur_FIX.c:56:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_RSHIFT( c[ k ], 1 );
	s32i.n	a2, a5, 0	# MEM[base: _230, offset: 0B], _6
	addi.n	a3, a3, 4	# ivtmp$34, ivtmp$34,
	addi.n	a5, a5, 8	# ivtmp$35, ivtmp$35,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:57:         } while( ++k <= order );
	bge	a4, a6, .L4	# order, k,
	j	.L5		#
.L3:
	addi	a7, a5, -2	# _297, iftmp$12_101,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:58:     } else if( lz > 2 ) {
	bnei	a5, 2, .L2	# iftmp$12_101,,
	j	.L6		#
.L23:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a7, 0x1e	# _297,
.L2:
	mov.n	a5, sp	# ivtmp$41,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:52:     k = 0;
	movi.n	a6, 0	# k,
.L7:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:62:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_LSHIFT( c[ k ], lz );
	l32i.n	a2, a3, 0	# MEM[base: _223, offset: 0B], MEM[base: _223, offset: 0B]
# @OPUS@\upstream\silk\fixed\schur_FIX.c:63:         } while( ++k <= order );
	addi.n	a6, a6, 1	# k, k,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:62:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_LSHIFT( c[ k ], lz );
	ssl	a7	# _297
	sll	a2, a2	# _14, MEM[base: _223, offset: 0B]
# @OPUS@\upstream\silk\fixed\schur_FIX.c:62:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_LSHIFT( c[ k ], lz );
	s32i.n	a2, a5, 4	# MEM[base: _221, offset: 4B], _14
# @OPUS@\upstream\silk\fixed\schur_FIX.c:62:             C[ k ][ 0 ] = C[ k ][ 1 ] = silk_LSHIFT( c[ k ], lz );
	s32i.n	a2, a5, 0	# MEM[base: _221, offset: 0B], _14
	addi.n	a3, a3, 4	# ivtmp$40, ivtmp$40,
	addi.n	a5, a5, 8	# ivtmp$41, ivtmp$41,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:63:         } while( ++k <= order );
	bge	a4, a6, .L7	# order, k,
	j	.L5		#
.L6:
	mov.n	a6, a4	# order, order
	mov.n	a2, sp	# ivtmp$47,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:52:     k = 0;
	movi.n	a5, 0	# k,
.L8:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:67:             C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	l32i.n	a4, a3, 0	# MEM[base: _214, offset: 0B], _18
# @OPUS@\upstream\silk\fixed\schur_FIX.c:68:         } while( ++k <= order );
	addi.n	a5, a5, 1	# k, k,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:67:             C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	s32i.n	a4, a2, 4	# MEM[base: _212, offset: 4B], _18
# @OPUS@\upstream\silk\fixed\schur_FIX.c:67:             C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	s32i.n	a4, a2, 0	# MEM[base: _212, offset: 0B], _18
	addi.n	a3, a3, 4	# ivtmp$46, ivtmp$46,
	addi.n	a2, a2, 8	# ivtmp$47, ivtmp$47,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:68:         } while( ++k <= order );
	bge	a6, a5, .L8	# order, k,
	j	.L5		#
.L17:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	addi.n	a14, a14, 1	# _20, _20,
	slli	a2, a14, 3	# tmp144, _20,
	add.n	a2, sp, a2	# tmp145,, tmp144
	l32i.n	a2, a2, 0	# MEM[base: _254, offset: 0B], _21
	addi.n	a12, a12, 2	# ivtmp$25, ivtmp$25,
	srai	a3, a2, 31	# tmp146, _21,
	xor	a3, a3, a2	# tmp147, tmp146, _21
	extui	a6, a2, 31, 1	# tmp148, _21,
	add.n	a3, a3, a6	# tmp149, tmp147, tmp148
	addi	a15, a15, -8	# ivtmp$30, ivtmp$30,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	blt	a3, a13, .L9	# tmp149, _133,
	l32i	a5, sp, 216	# %sfp,
	slli	a3, a4, 1	# tmp150, _260,
	mov.n	a12, a13	# _133, _133
	add.n	a3, a5, a3	# _289,, tmp150
	j	.L19		#
.L24:
	l32i	a3, sp, 216	# %sfp, _289
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	movi.n	a14, 1	# _20,
.L19:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:74:            if ( C[ k + 1 ][ 0 ] > 0 ) {
	blti	a2, 1, .L10	# _21,,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:75:               rc_Q15[ k ] = -SILK_FIX_CONST( .99f, 15 );
	l32r	a2, .LC0	#,
	s16i	a2, a3, 0	# *prephitmp_292,
	j	.L11		#
.L10:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:77:               rc_Q15[ k ] = SILK_FIX_CONST( .99f, 15 );
	l32r	a4, .LC1	#,
	s16i	a4, a3, 0	# *prephitmp_292,
	j	.L11		#
.L30:
	slli	a13, a4, 3	# tmp153, tmp5,
	l32i	a15, sp, 216	# %sfp, ivtmp$25
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	movi.n	a14, 1	# _20,
	add.n	a13, sp, a13	# ivtmp$30,, tmp153
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	mov.n	a3, a12	# _133, _133
	add.n	a4, a4, a14	#, tmp5,
	mov.n	a12, a15	# ivtmp$25, ivtmp$25
	s32i	a4, sp, 212	# %sfp,
	mov.n	a15, a13	# ivtmp$30, ivtmp$30
	mov.n	a13, a3	# _133, _133
.L9:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:84:         rc_tmp_Q15 = -silk_DIV32_16( C[ k + 1 ][ 0 ], silk_max_32( silk_RSHIFT( C[ 0 ][ 1 ], 15 ), 1 ) );
	srai	a3, a13, 15	# tmp154, _133,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	bgei	a3, 1, .L12	# tmp154,,
	movi.n	a3, 1	# tmp154,
.L12:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:84:         rc_tmp_Q15 = -silk_DIV32_16( C[ k + 1 ][ 0 ], silk_max_32( silk_RSHIFT( C[ 0 ][ 1 ], 15 ), 1 ) );
	call0	__divsi3		#
# @OPUS@\upstream\silk\fixed\schur_FIX.c:87:         rc_tmp_Q15 = silk_SAT16( rc_tmp_Q15 );
	l32r	a5, .LC2	#,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:84:         rc_tmp_Q15 = -silk_DIV32_16( C[ k + 1 ][ 0 ], silk_max_32( silk_RSHIFT( C[ 0 ][ 1 ], 15 ), 1 ) );
	neg	a2, a2	# iftmp$5_79,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:87:         rc_tmp_Q15 = silk_SAT16( rc_tmp_Q15 );
	bge	a2, a5, .L13	# iftmp$5_79,,
	mov.n	a2, a5	# iftmp$5_79,
.L13:
	l32r	a3, .LC3	#,
	bge	a3, a2, .L14	#, iftmp$5_79,
	mov.n	a2, a3	# iftmp$5_79,
.L14:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:93:         for( n = 0; n < order - k; n++ ) {
	l32i	a4, sp, 212	# %sfp,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:90:         rc_Q15[ k ] = (opus_int16)rc_tmp_Q15;
	s16i	a2, a12, 0	# MEM[base: _262, offset: 0B], iftmp$5_79
# @OPUS@\upstream\silk\fixed\schur_FIX.c:93:         for( n = 0; n < order - k; n++ ) {
	sub	a3, a4, a14	# tmp172,, _20
	mov.n	a4, a14	# _260, _20
	blti	a3, 1, .L15	# tmp172,,
	slli	a9, a14, 3	# tmp173, _20,
	add.n	a9, a9, sp	# ivtmp$16, tmp173,
	mov.n	a8, sp	# ivtmp$19,
.L16:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:95:             Ctmp2 = C[ n ][ 1 ];
	l32i.n	a10, a8, 4	# MEM[base: _283, offset: 4B], Ctmp2
# @OPUS@\upstream\silk\fixed\schur_FIX.c:94:             Ctmp1 = C[ n + k + 1 ][ 0 ];
	l32i.n	a11, a9, 0	# MEM[base: _285, offset: 0B], Ctmp1
# @OPUS@\upstream\silk\fixed\schur_FIX.c:96:             C[ n + k + 1 ][ 0 ] = silk_SMLAWB( Ctmp1, silk_LSHIFT( Ctmp2, 1 ), rc_tmp_Q15 );
	slli	a3, a10, 1	# _45, Ctmp2,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	slli	a13, a11, 1	# _56, Ctmp1,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:96:             C[ n + k + 1 ][ 0 ] = silk_SMLAWB( Ctmp1, silk_LSHIFT( Ctmp2, 1 ), rc_tmp_Q15 );
	extui	a7, a3, 0, 16	# tmp174, _45,
	srai	a3, a3, 16	# tmp177, _45,
	mull	a5, a3, a2	# tmp178, tmp177, iftmp$5_79
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	srai	a6, a13, 16	# tmp181, _56,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:96:             C[ n + k + 1 ][ 0 ] = silk_SMLAWB( Ctmp1, silk_LSHIFT( Ctmp2, 1 ), rc_tmp_Q15 );
	mull	a7, a7, a2	# tmp175, tmp174, iftmp$5_79
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	extui	a13, a13, 0, 16	# tmp184, _56,
	mull	a6, a6, a2	# tmp182, tmp181, iftmp$5_79
	mull	a3, a13, a2	# tmp185, tmp184, iftmp$5_79
# @OPUS@\upstream\silk\fixed\schur_FIX.c:96:             C[ n + k + 1 ][ 0 ] = silk_SMLAWB( Ctmp1, silk_LSHIFT( Ctmp2, 1 ), rc_tmp_Q15 );
	srai	a7, a7, 16	# tmp176, tmp175,
	add.n	a5, a5, a11	# tmp179, tmp178, Ctmp1
	add.n	a5, a7, a5	# tmp180, tmp176, tmp179
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	add.n	a6, a6, a10	# tmp183, tmp182, Ctmp2
	srai	a3, a3, 16	# tmp186, tmp185,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:96:             C[ n + k + 1 ][ 0 ] = silk_SMLAWB( Ctmp1, silk_LSHIFT( Ctmp2, 1 ), rc_tmp_Q15 );
	s32i.n	a5, a9, 0	# MEM[base: _285, offset: 0B], tmp180
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	add.n	a3, a6, a3	# tmp187, tmp183, tmp186
# @OPUS@\upstream\silk\fixed\schur_FIX.c:97:             C[ n ][ 1 ]         = silk_SMLAWB( Ctmp2, silk_LSHIFT( Ctmp1, 1 ), rc_tmp_Q15 );
	s32i.n	a3, a8, 4	# MEM[base: _283, offset: 4B], tmp187
	addi.n	a8, a8, 8	# ivtmp$19, ivtmp$19,
	addi.n	a9, a9, 8	# ivtmp$16, ivtmp$16,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:93:         for( n = 0; n < order - k; n++ ) {
	bne	a15, a8, .L16	# ivtmp$30, ivtmp$19,
	l32i.n	a13, sp, 4	# C, _133
.L15:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:71:     for( k = 0; k < order; k++ ) {
	l32i	a5, sp, 208	# %sfp,
	bne	a5, a14, .L17	#, _20,
	mov.n	a12, a13	# _133, _133
	j	.L18		#
.L5:
	l32i	a4, sp, 208	# %sfp,
	l32i.n	a12, sp, 4	# C, _133
	blti	a4, 1, .L18	#,,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	l32i.n	a2, sp, 8	# C, _21
	srai	a3, a2, 31	# tmp188, _21,
	xor	a3, a3, a2	# tmp189, tmp188, _21
	extui	a6, a2, 31, 1	# tmp190, _21,
	add.n	a3, a3, a6	# tmp191, tmp189, tmp190
# @OPUS@\upstream\silk\fixed\schur_FIX.c:73:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	blt	a3, a12, .L30	# tmp191, _133,
	j	.L24		#
.L21:
	l32i	a5, sp, 216	# %sfp,
# @OPUS@\upstream\silk\fixed\schur_FIX.c:102:        rc_Q15[ k ] = 0;
	sub	a4, a4, a14	# tmp192, tmp5, _20
	slli	a2, a14, 1	# tmp194, _20,
	slli	a4, a4, 1	#, tmp192,
	movi.n	a3, 0	#,
	add.n	a2, a5, a2	#,, tmp194
	call0	memset		#
	j	.L18		#
.L11:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:101:     for(; k < order; k++ ) {
	l32i	a4, sp, 208	# %sfp,
	blt	a14, a4, .L21	# _20,,
.L18:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	mov.n	a2, a12	# _133, _133
	bgei	a12, 1, .L22	# _133,,
	movi.n	a2, 1	# _133,
.L22:
# @OPUS@\upstream\silk\fixed\schur_FIX.c:107: }
	l32i	a0, sp, 252	#,
	movi	a9, 0x100	#,
	l32i	a12, sp, 248	#,
	l32i	a13, sp, 244	#,
	l32i	a14, sp, 240	#,
	l32i	a15, sp, 236	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_schur, .-silk_schur
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
