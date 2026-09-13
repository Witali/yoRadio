# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/residual_energy16_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"residual_energy16_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy16_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy16_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy16_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy16_FIX.c.s.raw
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
	.section	.text.silk_residual_energy16_covar_FIX,"ax",@progbits
	.literal_position
	.literal .LC0, 1073741823
	.literal .LC1, 2147483647
	.align	4
	.global	silk_residual_energy16_covar_FIX
	.type	silk_residual_energy16_covar_FIX, @function
# Function: silk_residual_energy16_covar_FIX
# Module: upstream/silk/fixed/residual_energy16_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main_FIX.h"
# C context:
# C context: /* Residual energy: nrg = wxx - 2 * wXx * c + c' * wXX * c */
# C context: opus_int32 silk_residual_energy16_covar_FIX(
# C context: const opus_int16                *c,                                     /* I    Prediction vector                                                           */
# C context: const opus_int32                *wXX,                                   /* I    Correlation matrix                                                          */
# C context: const opus_int32                *wXx,                                   /* I    Correlation vector                                                          */
# C context: opus_int32                      wxx,                                    /* I    Signal energy                                                               */
silk_residual_energy16_covar_FIX:
	addi	sp, sp, -80	#,,
	s32i	a12, sp, 76	#,
	s32i	a13, sp, 72	#,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:55:     lshifts = 16 - cQ;
	movi.n	a12, 0x10	# tmp550,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:43: {
	s32i	a14, sp, 68	#,
	s32i	a15, sp, 64	#,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:55:     lshifts = 16 - cQ;
	sub	a7, a12, a7	# lshifts, tmp550, cQ
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:59:     for( i = 0; i < D; i++ ) {
	blti	a6, 1, .L18	# D,,
	slli	a11, a6, 1	# tmp551, D,
	mov.n	a9, a2	# ivtmp$33, c
	add.n	a11, a11, a2	# _918, tmp551, c
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:58:     c_max = 0;
	movi.n	a10, 0	# c_max,
.L4:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:60:         c_max = silk_max_32( c_max, silk_abs( (opus_int32)c[ i ] ) );
	l16si	a8, a9, 0	# MEM[base: _914, offset: 0B], tmp552
	addi.n	a9, a9, 2	# ivtmp$33, ivtmp$33,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:60:         c_max = silk_max_32( c_max, silk_abs( (opus_int32)c[ i ] ) );
	abs	a8, a8	# tmp555, tmp552
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	bge	a10, a8, .L3	# c_max, tmp555,
	mov.n	a10, a8	# c_max, tmp555
.L3:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:59:     for( i = 0; i < D; i++ ) {
	bne	a9, a11, .L4	# ivtmp$33, _918,
	slli	a11, a10, 16	# tmp556, c_max,
	srai	a11, a11, 16	# prephitmp_332, tmp556,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a9, 0xf	# _325,
	beqz.n	a10, .L2	# c_max,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a10, a10	# iftmp$10_139, c_max
	addi	a9, a10, -17	# _325, iftmp$10_139,
	j	.L2		#
.L18:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:59:     for( i = 0; i < D; i++ ) {
	movi.n	a11, 0	# prephitmp_332,
	movi.n	a9, 0xf	# _325,
.L2:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:548:     return (((a) < (b)) ? (a) : (b));
	mov.n	a8, a7	# _137, lshifts
	bge	a9, a7, .L5	# _325, lshifts,
	mov.n	a8, a9	# _137, _325
.L5:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:64:     w_max = silk_max_32( wXX[ 0 ], wXX[ D * D - 1 ] );
	l32r	a10, .LC0	#,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:64:     w_max = silk_max_32( wXX[ 0 ], wXX[ D * D - 1 ] );
	mull	a9, a6, a6	# tmp557, D, D
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	l32i.n	a12, a3, 0	# *wXX_115(D), *wXX_115(D)
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:64:     w_max = silk_max_32( wXX[ 0 ], wXX[ D * D - 1 ] );
	add.n	a9, a9, a10	# tmp558, tmp557,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:64:     w_max = silk_max_32( wXX[ 0 ], wXX[ D * D - 1 ] );
	slli	a9, a9, 2	# tmp560, tmp558,
	add.n	a9, a3, a9	# tmp561, wXX, tmp560
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	l32i.n	a10, a9, 0	# *_14, _111
	bge	a10, a12, .L6	# _111, *wXX_115(D),
	mov.n	a10, a12	# _111, *wXX_115(D)
.L6:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:65:     Qxtra = silk_min_int( Qxtra, silk_CLZ32( silk_MUL( D, silk_RSHIFT( silk_SMULWB( w_max, c_max ), 4 ) ) ) - 5 );
	extui	a9, a10, 0, 16	# tmp567, _111,
	mull	a9, a9, a11	# tmp568, tmp567, prephitmp_332
	srai	a10, a10, 16	# tmp570, _111,
	mull	a10, a10, a11	# tmp571, tmp570, prephitmp_332
	srai	a9, a9, 16	# tmp569, tmp568,
	add.n	a9, a9, a10	# tmp572, tmp569, tmp571
	srai	a9, a9, 4	# tmp573, tmp572,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:65:     Qxtra = silk_min_int( Qxtra, silk_CLZ32( silk_MUL( D, silk_RSHIFT( silk_SMULWB( w_max, c_max ), 4 ) ) ) - 5 );
	mull	a9, a9, a6	# _27, tmp573, D
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a10, 0x1b	# _346,
	beqz.n	a9, .L7	# _27,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a9, a9	# iftmp$10_114, _27
	addi	a10, a9, -5	# _346, iftmp$10_114,
.L7:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a10, a8, .L8	# _346, _118,
	mov.n	a8, a10	# _118, _346
.L8:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:566:     return (((a) > (b)) ? (a) : (b));
	movi.n	a9, 0	# tmp574,
	movltz	a8, a9, a8	# _118, tmp574, _118
	sub	a12, a7, a8	# _349, lshifts, _118
	addi.n	a13, a12, 1	# _350, _349,
	ssr	a13	# _350
	sra	a5, a5	# _436, wxx
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	blti	a6, 1, .L9	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a7, a2, 0	# *c_110(D), tmp575
	ssl	a8	# _118
	sll	a7, a7	# _645, tmp575
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a7, sp, 0	# cn, _645
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 1, .L10	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 2	# MEM[(const opus_int16 *)c_110(D) + 2B], tmp578
	ssl	a8	# _118
	sll	a9, a9	# tmp581, tmp578
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 4	# cn, tmp581
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 2, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 4	# MEM[(const opus_int16 *)c_110(D) + 4B], tmp582
	ssl	a8	# _118
	sll	a9, a9	# tmp585, tmp582
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 8	# cn, tmp585
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 3, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 6	# MEM[(const opus_int16 *)c_110(D) + 6B], tmp586
	ssl	a8	# _118
	sll	a9, a9	# tmp589, tmp586
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 12	# cn, tmp589
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 4, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 8	# MEM[(const opus_int16 *)c_110(D) + 8B], tmp590
	ssl	a8	# _118
	sll	a9, a9	# tmp593, tmp590
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 16	# cn, tmp593
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 5, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 10	# MEM[(const opus_int16 *)c_110(D) + 10B], tmp594
	ssl	a8	# _118
	sll	a9, a9	# tmp597, tmp594
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 20	# cn, tmp597
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 6, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 12	# MEM[(const opus_int16 *)c_110(D) + 12B], tmp598
	ssl	a8	# _118
	sll	a9, a9	# tmp601, tmp598
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 24	# cn, tmp601
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 7, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 14	# MEM[(const opus_int16 *)c_110(D) + 14B], tmp602
	ssl	a8	# _118
	sll	a9, a9	# tmp605, tmp602
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 28	# cn, tmp605
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 8, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 16	# MEM[(const opus_int16 *)c_110(D) + 16B], tmp606
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	movi.n	a10, 9	# tmp610,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	ssl	a8	# _118
	sll	a9, a9	# tmp609, tmp606
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 32	# cn, tmp609
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beq	a6, a10, .L11	# D, tmp610,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 18	# MEM[(const opus_int16 *)c_110(D) + 18B], tmp611
	ssl	a8	# _118
	sll	a9, a9	# tmp614, tmp611
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 36	# cn, tmp614
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 10, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 20	# MEM[(const opus_int16 *)c_110(D) + 20B], tmp615
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	movi.n	a10, 0xb	# tmp619,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	ssl	a8	# _118
	sll	a9, a9	# tmp618, tmp615
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 40	# cn, tmp618
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beq	a6, a10, .L11	# D, tmp619,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 22	# MEM[(const opus_int16 *)c_110(D) + 22B], tmp620
	ssl	a8	# _118
	sll	a9, a9	# tmp623, tmp620
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 44	# cn, tmp623
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beqi	a6, 12, .L11	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 24	# MEM[(const opus_int16 *)c_110(D) + 24B], tmp624
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	movi.n	a10, 0xd	# tmp628,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	ssl	a8	# _118
	sll	a9, a9	# tmp627, tmp624
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 48	# cn, tmp627
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beq	a6, a10, .L11	# D, tmp628,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 26	# MEM[(const opus_int16 *)c_110(D) + 26B], tmp629
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	movi.n	a10, 0xe	# tmp633,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	ssl	a8	# _118
	sll	a9, a9	# tmp632, tmp629
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 52	# cn, tmp632
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beq	a6, a10, .L11	# D, tmp633,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a9, a2, 28	# MEM[(const opus_int16 *)c_110(D) + 28B], tmp634
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	movi.n	a10, 0xf	# tmp638,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	ssl	a8	# _118
	sll	a9, a9	# tmp637, tmp634
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a9, sp, 56	# cn, tmp637
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:67:     for( i = 0; i < D; i++ ) {
	beq	a6, a10, .L11	# D, tmp638,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	l16si	a2, a2, 30	# MEM[(const opus_int16 *)c_110(D) + 30B], tmp639
	ssl	a8	# _118
	sll	a8, a2	# tmp642, tmp639
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:68:         cn[ i ] = silk_LSHIFT( ( opus_int )c[ i ], Qxtra );
	s32i.n	a8, sp, 60	# cn, tmp642
	j	.L11		#
.L17:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 8	# MEM[(const opus_int32 *)wXx_123(D) + 8B], _328
	l16si	a8, sp, 8	# cn, _8
	srai	a7, a2, 16	# tmp645, _328,
	extui	a2, a2, 0, 16	# tmp647, _328,
	mull	a7, a7, a8	# tmp646, tmp645, _8
	mull	a2, a2, a8	# tmp648, tmp647, _8
	add.n	a7, a7, a9	# _309, tmp646, tmp
	srai	a9, a2, 16	# tmp649, tmp648,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp649, _309
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 3, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 12	# MEM[(const opus_int32 *)wXx_123(D) + 12B], _88
	l16si	a8, sp, 12	# cn, _443
	srai	a7, a2, 16	# tmp652, _88,
	extui	a2, a2, 0, 16	# tmp654, _88,
	mull	a7, a7, a8	# tmp653, tmp652, _443
	mull	a2, a2, a8	# tmp655, tmp654, _443
	add.n	a7, a7, a9	# _336, tmp653, tmp
	srai	a9, a2, 16	# tmp656, tmp655,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp656, _336
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 4, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 16	# MEM[(const opus_int32 *)wXx_123(D) + 16B], _456
	l16si	a8, sp, 16	# cn, _460
	srai	a7, a2, 16	# tmp659, _456,
	extui	a2, a2, 0, 16	# tmp661, _456,
	mull	a7, a7, a8	# tmp660, tmp659, _460
	mull	a2, a2, a8	# tmp662, tmp661, _460
	add.n	a7, a7, a9	# _337, tmp660, tmp
	srai	a9, a2, 16	# tmp663, tmp662,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp663, _337
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 5, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 20	# MEM[(const opus_int32 *)wXx_123(D) + 20B], _473
	l16si	a8, sp, 20	# cn, _477
	srai	a7, a2, 16	# tmp666, _473,
	extui	a2, a2, 0, 16	# tmp668, _473,
	mull	a7, a7, a8	# tmp667, tmp666, _477
	mull	a2, a2, a8	# tmp669, tmp668, _477
	add.n	a7, a7, a9	# _338, tmp667, tmp
	srai	a9, a2, 16	# tmp670, tmp669,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp670, _338
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 6, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 24	# MEM[(const opus_int32 *)wXx_123(D) + 24B], _490
	l16si	a8, sp, 24	# cn, _494
	srai	a7, a2, 16	# tmp673, _490,
	extui	a2, a2, 0, 16	# tmp675, _490,
	mull	a7, a7, a8	# tmp674, tmp673, _494
	mull	a2, a2, a8	# tmp676, tmp675, _494
	add.n	a7, a7, a9	# _366, tmp674, tmp
	srai	a9, a2, 16	# tmp677, tmp676,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp677, _366
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 7, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 28	# MEM[(const opus_int32 *)wXx_123(D) + 28B], _507
	l16si	a8, sp, 28	# cn, _511
	srai	a7, a2, 16	# tmp680, _507,
	extui	a2, a2, 0, 16	# tmp682, _507,
	mull	a7, a7, a8	# tmp681, tmp680, _511
	mull	a2, a2, a8	# tmp683, tmp682, _511
	add.n	a7, a7, a9	# _367, tmp681, tmp
	srai	a9, a2, 16	# tmp684, tmp683,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp684, _367
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 8, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 32	# MEM[(const opus_int32 *)wXx_123(D) + 32B], _524
	l16si	a8, sp, 32	# cn, _528
	srai	a7, a2, 16	# tmp687, _524,
	extui	a2, a2, 0, 16	# tmp689, _524,
	mull	a2, a2, a8	# tmp690, tmp689, _528
	mull	a7, a7, a8	# tmp688, tmp687, _528
	add.n	a7, a7, a9	# _368, tmp688, tmp
	srai	a9, a2, 16	# tmp691, tmp690,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	movi.n	a2, 9	# tmp692,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp691, _368
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beq	a6, a2, .L12	# D, tmp692,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 36	# MEM[(const opus_int32 *)wXx_123(D) + 36B], _541
	l16si	a8, sp, 36	# cn, _545
	srai	a7, a2, 16	# tmp695, _541,
	extui	a2, a2, 0, 16	# tmp697, _541,
	mull	a7, a7, a8	# tmp696, tmp695, _545
	mull	a2, a2, a8	# tmp698, tmp697, _545
	add.n	a7, a7, a9	# _394, tmp696, tmp
	srai	a9, a2, 16	# tmp699, tmp698,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp699, _394
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 10, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 40	# MEM[(const opus_int32 *)wXx_123(D) + 40B], _558
	l16si	a8, sp, 40	# cn, _562
	srai	a7, a2, 16	# tmp702, _558,
	extui	a2, a2, 0, 16	# tmp704, _558,
	mull	a2, a2, a8	# tmp705, tmp704, _562
	mull	a7, a7, a8	# tmp703, tmp702, _562
	add.n	a7, a7, a9	# _395, tmp703, tmp
	srai	a9, a2, 16	# tmp706, tmp705,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	movi.n	a2, 0xb	# tmp707,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp706, _395
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beq	a6, a2, .L12	# D, tmp707,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 44	# MEM[(const opus_int32 *)wXx_123(D) + 44B], _575
	l16si	a8, sp, 44	# cn, _579
	srai	a7, a2, 16	# tmp710, _575,
	extui	a2, a2, 0, 16	# tmp712, _575,
	mull	a7, a7, a8	# tmp711, tmp710, _579
	mull	a2, a2, a8	# tmp713, tmp712, _579
	add.n	a7, a7, a9	# _396, tmp711, tmp
	srai	a9, a2, 16	# tmp714, tmp713,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp714, _396
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beqi	a6, 12, .L12	# D,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 48	# MEM[(const opus_int32 *)wXx_123(D) + 48B], _592
	l16si	a8, sp, 48	# cn, _596
	srai	a7, a2, 16	# tmp717, _592,
	extui	a2, a2, 0, 16	# tmp719, _592,
	mull	a2, a2, a8	# tmp720, tmp719, _596
	mull	a7, a7, a8	# tmp718, tmp717, _596
	add.n	a7, a7, a9	# _411, tmp718, tmp
	srai	a9, a2, 16	# tmp721, tmp720,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	movi.n	a2, 0xd	# tmp722,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp721, _411
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beq	a6, a2, .L12	# D, tmp722,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 52	# MEM[(const opus_int32 *)wXx_123(D) + 52B], _609
	l16si	a8, sp, 52	# cn, _613
	srai	a7, a2, 16	# tmp725, _609,
	extui	a2, a2, 0, 16	# tmp727, _609,
	mull	a2, a2, a8	# tmp728, tmp727, _613
	mull	a7, a7, a8	# tmp726, tmp725, _613
	add.n	a7, a7, a9	# _412, tmp726, tmp
	srai	a9, a2, 16	# tmp729, tmp728,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	movi.n	a2, 0xe	# tmp730,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp729, _412
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beq	a6, a2, .L12	# D, tmp730,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 56	# MEM[(const opus_int32 *)wXx_123(D) + 56B], _626
	l16si	a8, sp, 56	# cn, _630
	srai	a7, a2, 16	# tmp733, _626,
	extui	a2, a2, 0, 16	# tmp735, _626,
	mull	a2, a2, a8	# tmp736, tmp735, _630
	mull	a7, a7, a8	# tmp734, tmp733, _630
	add.n	a7, a7, a9	# _413, tmp734, tmp
	srai	a9, a2, 16	# tmp737, tmp736,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	movi.n	a2, 0xf	# tmp738,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a7	# tmp, tmp737, _413
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	beq	a6, a2, .L12	# D, tmp738,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 60	# MEM[(const opus_int32 *)wXx_123(D) + 60B], _39
	l16si	a7, sp, 60	# cn, _43
	srai	a4, a2, 16	# tmp741, _39,
	extui	a2, a2, 0, 16	# tmp743, _39,
	mull	a4, a4, a7	# tmp742, tmp741, _43
	mull	a2, a2, a7	# tmp744, tmp743, _43
	add.n	a4, a4, a9	# _428, tmp742, tmp
	srai	a9, a2, 16	# tmp745, tmp744,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a4	# tmp, tmp745, _428
	j	.L12		#
.L15:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	addi.n	a5, a4, 1	# j, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a5, a6, .L21	# j, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a2, a5, 2	# tmp746, j,
	l32i.n	a7, a3, 4	# MEM[base: _811, offset: 4B], _427
	add.n	a2, sp, a2	# tmp747,, tmp746
	l16si	a14, a2, 0	# cn, _423
	extui	a2, a7, 0, 16	# tmp750, _427,
	mull	a2, a2, a14	# tmp751, tmp750, _423
	srai	a7, a7, 16	# tmp753, _427,
	mull	a7, a7, a14	# tmp754, tmp753, _423
	srai	a2, a2, 16	# tmp752, tmp751,
	addi.n	a14, a4, 2	# _835, i,
	add.n	a2, a2, a7	# tmp, tmp752, tmp754
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a14, a6, .L13	# _835, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a14, 2	# tmp755, _835,
	l32i.n	a7, a3, 8	# MEM[base: _811, offset: 8B], _410
	add.n	a14, sp, a14	# tmp756,, tmp755
	l16si	a15, a14, 0	# cn, _406
	extui	a14, a7, 0, 16	# tmp759, _410,
	srai	a7, a7, 16	# tmp762, _410,
	mull	a14, a14, a15	# tmp760, tmp759, _406
	mull	a7, a7, a15	# tmp763, tmp762, _406
	srai	a15, a14, 16	# tmp761, tmp760,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a7, a2	# tmp764, tmp763, tmp
	addi.n	a14, a4, 3	# _841, i,
	add.n	a2, a15, a2	# tmp, tmp761, tmp764
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a14, a6, .L13	# _841, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a14, 2	# tmp765, _841,
	l32i.n	a7, a3, 12	# MEM[base: _811, offset: 12B], _393
	add.n	a14, sp, a14	# tmp766,, tmp765
	l16si	a15, a14, 0	# cn, _389
	srai	a14, a7, 16	# tmp769, _393,
	extui	a7, a7, 0, 16	# tmp771, _393,
	mull	a14, a14, a15	# tmp770, tmp769, _389
	mull	a7, a7, a15	# tmp772, tmp771, _389
	add.n	a15, a14, a2	# _438, tmp770, tmp
	srai	a2, a7, 16	# tmp773, tmp772,
	addi.n	a14, a4, 4	# _847, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a15	# tmp, tmp773, _438
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a14, a6, .L13	# _847, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a14, 2	# tmp774, _847,
	l32i.n	a7, a3, 16	# MEM[base: _811, offset: 16B], _365
	add.n	a14, sp, a14	# tmp775,, tmp774
	l16si	a15, a14, 0	# cn, _357
	srai	a14, a7, 16	# tmp778, _365,
	extui	a7, a7, 0, 16	# tmp780, _365,
	mull	a14, a14, a15	# tmp779, tmp778, _357
	mull	a7, a7, a15	# tmp781, tmp780, _357
	add.n	a15, a14, a2	# _55, tmp779, tmp
	srai	a2, a7, 16	# tmp782, tmp781,
	addi.n	a14, a4, 5	# _853, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a15	# tmp, tmp782, _55
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a14, a6, .L13	# _853, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a14, 2	# tmp783, _853,
	l32i.n	a7, a3, 20	# MEM[base: _811, offset: 20B], _335
	add.n	a14, sp, a14	# tmp784,, tmp783
	l16si	a15, a14, 0	# cn, _323
	srai	a14, a7, 16	# tmp787, _335,
	extui	a7, a7, 0, 16	# tmp789, _335,
	mull	a7, a7, a15	# tmp790, tmp789, _323
	mull	a14, a14, a15	# tmp788, tmp787, _323
	add.n	a14, a14, a2	# _68, tmp788, tmp
	srai	a2, a7, 16	# tmp791, tmp790,
	addi.n	a7, a4, 6	# _859, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp791, _68
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _859, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a7, a7, 2	# tmp792, _859,
	l32i.n	a14, a3, 24	# MEM[base: _811, offset: 24B], _306
	add.n	a7, sp, a7	# tmp793,, tmp792
	l16si	a15, a7, 0	# cn, _302
	srai	a7, a14, 16	# tmp796, _306,
	extui	a14, a14, 0, 16	# tmp798, _306,
	mull	a7, a7, a15	# tmp797, tmp796, _302
	mull	a14, a14, a15	# tmp799, tmp798, _302
	add.n	a15, a7, a2	# _128, tmp797, tmp
	srai	a2, a14, 16	# tmp800, tmp799,
	addi.n	a7, a4, 7	# _865, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a15	# tmp, tmp800, _128
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _865, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp801, _865,
	add.n	a14, sp, a14	# tmp802,, tmp801
	l32i.n	a7, a3, 28	# MEM[base: _811, offset: 28B], _289
	l16si	a15, a14, 0	# cn, _285
	srai	a14, a7, 16	# tmp805, _289,
	extui	a7, a7, 0, 16	# tmp807, _289,
	mull	a7, a7, a15	# tmp808, tmp807, _285
	mull	a14, a14, a15	# tmp806, tmp805, _285
	add.n	a14, a14, a2	# _53, tmp806, tmp
	srai	a2, a7, 16	# tmp809, tmp808,
	addi.n	a7, a4, 8	# _871, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp809, _53
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _871, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp810, _871,
	add.n	a14, sp, a14	# tmp811,, tmp810
	l32i.n	a7, a3, 32	# MEM[base: _811, offset: 32B], _272
	l16si	a15, a14, 0	# cn, _268
	srai	a14, a7, 16	# tmp814, _272,
	extui	a7, a7, 0, 16	# tmp816, _272,
	mull	a7, a7, a15	# tmp817, tmp816, _268
	mull	a14, a14, a15	# tmp815, tmp814, _268
	add.n	a14, a14, a2	# _54, tmp815, tmp
	srai	a2, a7, 16	# tmp818, tmp817,
	addi.n	a7, a4, 9	# _877, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp818, _54
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _877, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp819, _877,
	add.n	a14, sp, a14	# tmp820,, tmp819
	l32i.n	a7, a3, 36	# MEM[base: _811, offset: 36B], _255
	l16si	a15, a14, 0	# cn, _251
	srai	a14, a7, 16	# tmp823, _255,
	extui	a7, a7, 0, 16	# tmp825, _255,
	mull	a7, a7, a15	# tmp826, tmp825, _251
	mull	a14, a14, a15	# tmp824, tmp823, _251
	add.n	a14, a14, a2	# _67, tmp824, tmp
	srai	a2, a7, 16	# tmp827, tmp826,
	addi.n	a7, a4, 10	# _883, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp827, _67
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _883, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp828, _883,
	add.n	a14, sp, a14	# tmp829,, tmp828
	l32i.n	a7, a3, 40	# MEM[base: _811, offset: 40B], _238
	l16si	a15, a14, 0	# cn, _234
	srai	a14, a7, 16	# tmp832, _238,
	extui	a7, a7, 0, 16	# tmp834, _238,
	mull	a7, a7, a15	# tmp835, tmp834, _234
	mull	a14, a14, a15	# tmp833, tmp832, _234
	add.n	a14, a14, a2	# _52, tmp833, tmp
	srai	a2, a7, 16	# tmp836, tmp835,
	addi.n	a7, a4, 11	# _889, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp836, _52
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _889, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp837, _889,
	add.n	a14, sp, a14	# tmp838,, tmp837
	l32i.n	a7, a3, 44	# MEM[base: _811, offset: 44B], _221
	l16si	a15, a14, 0	# cn, _217
	srai	a14, a7, 16	# tmp841, _221,
	extui	a7, a7, 0, 16	# tmp843, _221,
	mull	a7, a7, a15	# tmp844, tmp843, _217
	mull	a14, a14, a15	# tmp842, tmp841, _217
	add.n	a14, a14, a2	# _51, tmp842, tmp
	srai	a2, a7, 16	# tmp845, tmp844,
	addi.n	a7, a4, 12	# _895, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp845, _51
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _895, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp846, _895,
	add.n	a14, sp, a14	# tmp847,, tmp846
	l32i.n	a7, a3, 48	# MEM[base: _811, offset: 48B], _204
	l16si	a15, a14, 0	# cn, _200
	srai	a14, a7, 16	# tmp850, _204,
	extui	a7, a7, 0, 16	# tmp852, _204,
	mull	a7, a7, a15	# tmp853, tmp852, _200
	mull	a14, a14, a15	# tmp851, tmp850, _200
	add.n	a14, a14, a2	# _3, tmp851, tmp
	srai	a2, a7, 16	# tmp854, tmp853,
	addi.n	a7, a4, 13	# _901, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp854, _3
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _901, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp855, _901,
	add.n	a14, sp, a14	# tmp856,, tmp855
	l32i.n	a7, a3, 52	# MEM[base: _811, offset: 52B], _187
	l16si	a15, a14, 0	# cn, _183
	srai	a14, a7, 16	# tmp859, _187,
	extui	a7, a7, 0, 16	# tmp861, _187,
	mull	a7, a7, a15	# tmp862, tmp861, _183
	mull	a14, a14, a15	# tmp860, tmp859, _183
	add.n	a14, a14, a2	# _112, tmp860, tmp
	srai	a2, a7, 16	# tmp863, tmp862,
	addi.n	a7, a4, 14	# _907, i,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp863, _112
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a7, a6, .L13	# _907, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a14, a7, 2	# tmp864, _907,
	add.n	a14, sp, a14	# tmp865,, tmp864
	l32i.n	a7, a3, 56	# MEM[base: _811, offset: 56B], _170
	l16si	a15, a14, 0	# cn, _166
	srai	a14, a7, 16	# tmp868, _170,
	extui	a7, a7, 0, 16	# tmp870, _170,
	mull	a14, a14, a15	# tmp869, tmp868, _166
	mull	a7, a7, a15	# tmp871, tmp870, _166
	add.n	a14, a14, a2	# _2, tmp869, tmp
	addi.n	a4, a4, 15	# _829, i,
	srai	a2, a7, 16	# tmp872, tmp871,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a14	# tmp, tmp872, _2
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:85:         for( j = i + 1; j < D; j++ ) {
	bge	a4, a6, .L13	# _829, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	slli	a4, a4, 2	# tmp873, _829,
	l32i.n	a7, a3, 60	# MEM[base: _811, offset: 60B], _57
	add.n	a4, sp, a4	# tmp874,, tmp873
	l16si	a14, a4, 0	# cn, _61
	srai	a4, a7, 16	# tmp877, _57,
	extui	a7, a7, 0, 16	# tmp879, _57,
	mull	a4, a4, a14	# tmp878, tmp877, _61
	mull	a7, a7, a14	# tmp880, tmp879, _61
	add.n	a4, a4, a2	# _1, tmp878, tmp
	srai	a2, a7, 16	# tmp881, tmp880,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:86:             tmp = silk_SMLAWB( tmp, pRow[ j ], cn[ j ] );
	add.n	a2, a2, a4	# tmp, tmp881, _1
	j	.L13		#
.L21:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:83:         tmp = 0;
	movi.n	a2, 0	# tmp,
.L13:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:88:         tmp  = silk_SMLAWB( tmp,  silk_RSHIFT( pRow[ i ], 1 ), cn[ i ] );
	l32i.n	a14, a3, 0	# MEM[base: _810, offset: 0B], _70
	l16si	a7, a8, 0	# MEM[base: _826, offset: 0B], _74
	extui	a4, a14, 1, 16	# tmp885, _70,,
	mull	a4, a4, a7	# tmp886, tmp885, _74
	srai	a14, a14, 17	# tmp888, _70,
	mull	a14, a14, a7	# tmp889, tmp888, _74
	srai	a4, a4, 16	# tmp887, tmp886,
	add.n	a4, a4, a14	# tmp890, tmp887, tmp889
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:88:         tmp  = silk_SMLAWB( tmp,  silk_RSHIFT( pRow[ i ], 1 ), cn[ i ] );
	add.n	a2, a4, a2	# tmp, tmp890, tmp
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:89:         tmp2 = silk_SMLAWB( tmp2, tmp,                        cn[ i ] );
	extui	a4, a2, 0, 16	# tmp891, tmp,
	mull	a4, a4, a7	# tmp892, tmp891, _74
	srai	a2, a2, 16	# tmp894, tmp,
	mull	a2, a2, a7	# tmp895, tmp894, _74
	srai	a4, a4, 16	# tmp893, tmp892,
	add.n	a2, a4, a2	# tmp896, tmp893, tmp895
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:89:         tmp2 = silk_SMLAWB( tmp2, tmp,                        cn[ i ] );
	add.n	a10, a10, a2	# tmp2, tmp2, tmp896
	add.n	a3, a3, a11	# ivtmp$14, ivtmp$14, _805
	addi.n	a8, a8, 4	# ivtmp$15, ivtmp$15,
	mov.n	a4, a5	# i, j
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:82:     for( i = 0; i < D; i++ ) {
	bne	a6, a5, .L15	# D, i,
	ssl	a12	# _349
	sll	a5, a10	# tmp897, tmp2
	add.n	a5, a5, a9	# _436, tmp897, nrg
.L9:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:95:         nrg = 1;
	movi.n	a2, 1	# <retval>,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:94:     if( nrg < 1 ) {
	blt	a5, a2, .L1	# _436,,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:96:     } else if( nrg > silk_RSHIFT( silk_int32_MAX, lshifts + 2 ) ) {
	l32r	a3, .LC1	#, tmp900
	addi.n	a12, a12, 2	# tmp898, _349,
	ssr	a12	# tmp898
	sra	a3, a3	# tmp899, tmp900
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:97:         nrg = silk_int32_MAX >> 1;
	l32r	a2, .LC0	#, <retval>
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:96:     } else if( nrg > silk_RSHIFT( silk_int32_MAX, lshifts + 2 ) ) {
	blt	a3, a5, .L1	# tmp899, _436,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:99:         nrg = silk_LSHIFT( nrg, lshifts + 1 );                           /* Q0 */
	ssl	a13	# _350
	sll	a2, a5	# <retval>, _436
	j	.L1		#
.L12:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:81:     tmp2 = 0;
	movi.n	a10, 0	# tmp2,
	addi.n	a11, a6, 1	# tmp902, D,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:78:     nrg = silk_RSHIFT( wxx, 1 + lshifts ) - tmp;                         /* Q: -lshifts - 1 */
	sub	a9, a5, a9	# nrg, _436, tmp
	slli	a11, a11, 2	# _805, tmp902,
	mov.n	a8, sp	# ivtmp$15,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:82:     for( i = 0; i < D; i++ ) {
	mov.n	a4, a10	# i, tmp2
	j	.L15		#
.L10:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	l32i.n	a2, a4, 0	# *wXx_123(D), _924
	slli	a4, a7, 16	# tmp903, _645,
	srai	a4, a4, 16	# _928, tmp903,
	extui	a9, a2, 0, 16	# tmp904, _924,
	mull	a9, a9, a4	# tmp905, tmp904, _928
	srai	a2, a2, 16	# tmp907, _924,
	mull	a2, a2, a4	# tmp908, tmp907, _928
	srai	a9, a9, 16	# tmp906, tmp905,
	add.n	a9, a9, a2	# tmp, tmp906, tmp908
	j	.L12		#
.L11:
	l32i.n	a8, a4, 0	# *wXx_123(D), _940
	slli	a7, a7, 16	# tmp909, _645,
	srai	a7, a7, 16	# _944, tmp909,
	l32i.n	a2, a4, 4	# MEM[(const opus_int32 *)wXx_123(D) + 4B], _382
	extui	a9, a8, 0, 16	# tmp912, _940,
	l16si	a10, sp, 4	# cn, _362
	mull	a9, a9, a7	# tmp913, tmp912, _944
	srai	a8, a8, 16	# tmp915, _940,
	mull	a7, a8, a7	# tmp916, tmp915, _944
	srai	a8, a2, 16	# tmp918, _382,
	extui	a2, a2, 0, 16	# tmp921, _382,
	srai	a9, a9, 16	# tmp914, tmp913,
	mull	a8, a8, a10	# tmp919, tmp918, _362
	mull	a2, a2, a10	# tmp922, tmp921, _362
	add.n	a9, a9, a7	# tmp917, tmp914, tmp916
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a8	# tmp920, tmp917, tmp919
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	srai	a2, a2, 16	# tmp923, tmp922,
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:76:         tmp = silk_SMLAWB( tmp, wXx[ i ], cn[ i ] );
	add.n	a9, a9, a2	# tmp, tmp920, tmp923
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:75:     for( i = 0; i < D; i++ ) {
	bnei	a6, 2, .L17	# D,,
	j	.L12		#
.L1:
# @OPUS@\upstream\silk\fixed\residual_energy16_FIX.c:103: }
	l32i	a12, sp, 76	#,
	l32i	a13, sp, 72	#,
	l32i	a14, sp, 68	#,
	l32i	a15, sp, 64	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	silk_residual_energy16_covar_FIX, .-silk_residual_energy16_covar_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
