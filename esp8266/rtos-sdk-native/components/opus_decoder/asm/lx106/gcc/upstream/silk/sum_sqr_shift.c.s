# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/sum_sqr_shift.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"sum_sqr_shift.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\sum_sqr_shift.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\sum_sqr_shift.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\sum_sqr_shift.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\sum_sqr_shift.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\sum_sqr_shift.c.s.raw
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
	.section	.text.silk_sum_sqr_shift,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_sum_sqr_shift
	.type	silk_sum_sqr_shift, @function
# Function: silk_sum_sqr_shift
# Module: upstream/silk/sum_sqr_shift.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Compute number of bits to right shift the sum of squares of a vector */
# C context: /* of int16s to make it fit in an int32                                 */
# C context: void silk_sum_sqr_shift(
# C context: opus_int32                  *energy,            /* O   Energy of x, after shifting to the right                     */
# C context: opus_int                    *shift,             /* O   Number of bits right shift applied to energy                 */
# C context: const opus_int16            *x,                 /* I   Input vector                                                 */
# C context: opus_int                    len                 /* I   Length of input vector                                       */
silk_sum_sqr_shift:
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	addi.n	a8, a5, -1	# _144, len,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a5, .L9	# len,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a6, a5	# iftmp$16_76, len
# @OPUS@\upstream\silk\sum_sqr_shift.c:48:     shft = 31-silk_CLZ32(len);
	movi.n	a11, 0x1f	# tmp100,
	movi.n	a12, 0x22	# tmp101,
	sub	a11, a11, a6	# shft, tmp100, iftmp$16_76
	sub	a12, a12, a6	# _181, tmp101, iftmp$16_76
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	blti	a8, 1, .L10	# _144,,
	mov.n	a7, a4	# ivtmp$28, x
	mov.n	a10, a5	# nrg, len
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	movi.n	a9, 0	# i,
.L4:
# @OPUS@\upstream\silk\sum_sqr_shift.c:52:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	l16si	a13, a7, 0	# MEM[base: _172, offset: 0B], _4
# @OPUS@\upstream\silk\sum_sqr_shift.c:53:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	l16si	a6, a7, 2	# MEM[base: _172, offset: 2B], _10
# @OPUS@\upstream\silk\sum_sqr_shift.c:52:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	mull	a13, a13, a13	# nrg_tmp, _4, _4
# @OPUS@\upstream\silk\sum_sqr_shift.c:53:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	mull	a6, a6, a6	# tmp106, _10, _10
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	addi.n	a9, a9, 2	# i, i,
# @OPUS@\upstream\silk\sum_sqr_shift.c:53:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	add.n	a6, a6, a13	# nrg_tmp, tmp106, nrg_tmp
# @OPUS@\upstream\silk\sum_sqr_shift.c:54:         nrg = (opus_int32)silk_ADD_RSHIFT_uint( nrg, nrg_tmp, shft );
	ssr	a11	# shft
	srl	a6, a6	# tmp108, nrg_tmp
	add.n	a10, a6, a10	# nrg, tmp108, nrg
	addi.n	a7, a7, 4	# ivtmp$28, ivtmp$28,
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	blt	a9, a8, .L4	# i, _144,
	j	.L3		#
.L10:
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	mov.n	a10, a5	# nrg, len
# @OPUS@\upstream\silk\sum_sqr_shift.c:51:     for( i = 0; i < len - 1; i += 2 ) {
	movi.n	a9, 0	# i,
.L3:
# @OPUS@\upstream\silk\sum_sqr_shift.c:56:     if( i < len ) {
	bge	a9, a5, .L5	# i, len,
# @OPUS@\upstream\silk\sum_sqr_shift.c:58:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	slli	a9, a9, 1	# tmp109, i,
	add.n	a9, a4, a9	# tmp110, x, tmp109
	l16si	a6, a9, 0	# *_20, _21
	mull	a6, a6, a6	# nrg_tmp, _21, _21
# @OPUS@\upstream\silk\sum_sqr_shift.c:59:         nrg = (opus_int32)silk_ADD_RSHIFT_uint( nrg, nrg_tmp, shft );
	ssr	a11	# shft
	srl	a11, a6	# tmp114, nrg_tmp
	add.n	a10, a11, a10	# nrg, tmp114, nrg
.L5:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a10, a10	# iftmp$16_90, nrg
# @OPUS@\upstream\silk\sum_sqr_shift.c:64:     shft = silk_max_32(0, shft+3 - silk_CLZ32(nrg));
	sub	a12, a12, a10	# _88, _181, iftmp$16_90
# @OPUS@\upstream\silk\SigProc_FIX.h:574:     return (((a) > (b)) ? (a) : (b));
	movi.n	a10, 0	# tmp115,
	movltz	a12, a10, a12	# _88, tmp115, _88
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	blti	a8, 1, .L12	# _144,,
	mov.n	a9, a4	# ivtmp$21, x
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	mov.n	a11, a10	# i, nrg
.L7:
# @OPUS@\upstream\silk\sum_sqr_shift.c:67:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	l16si	a7, a9, 0	# MEM[base: _177, offset: 0B], _37
# @OPUS@\upstream\silk\sum_sqr_shift.c:68:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	l16si	a6, a9, 2	# MEM[base: _177, offset: 2B], _43
# @OPUS@\upstream\silk\sum_sqr_shift.c:67:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	mull	a7, a7, a7	# nrg_tmp, _37, _37
# @OPUS@\upstream\silk\sum_sqr_shift.c:68:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	mull	a6, a6, a6	# tmp120, _43, _43
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	addi.n	a11, a11, 2	# i, i,
# @OPUS@\upstream\silk\sum_sqr_shift.c:68:         nrg_tmp = silk_SMLABB_ovflw( nrg_tmp, x[ i + 1 ], x[ i + 1 ] );
	add.n	a6, a6, a7	# nrg_tmp, tmp120, nrg_tmp
# @OPUS@\upstream\silk\sum_sqr_shift.c:69:         nrg = (opus_int32)silk_ADD_RSHIFT_uint( nrg, nrg_tmp, shft );
	ssr	a12	# _88
	srl	a6, a6	# tmp122, nrg_tmp
	add.n	a10, a6, a10	# nrg, tmp122, nrg
# @OPUS@\upstream\silk\sum_sqr_shift.c:69:         nrg = (opus_int32)silk_ADD_RSHIFT_uint( nrg, nrg_tmp, shft );
	mov.n	a6, a10	# _49, nrg
	addi.n	a9, a9, 4	# ivtmp$21, ivtmp$21,
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	blt	a11, a8, .L7	# i, _144,
	j	.L2		#
.L9:
# @OPUS@\upstream\silk\SigProc_FIX.h:574:     return (((a) > (b)) ? (a) : (b));
	mov.n	a12, a5	# _88, len
# @OPUS@\upstream\silk\sum_sqr_shift.c:65:     nrg = 0;
	mov.n	a10, a5	# nrg, len
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	mov.n	a11, a5	# i, len
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	mov.n	a6, a5	# _49, len
	j	.L2		#
.L12:
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	mov.n	a6, a10	# _49, tmp115
# @OPUS@\upstream\silk\sum_sqr_shift.c:66:     for( i = 0 ; i < len - 1; i += 2 ) {
	mov.n	a11, a10	# i, _49
.L2:
# @OPUS@\upstream\silk\sum_sqr_shift.c:71:     if( i < len ) {
	bge	a11, a5, .L8	# i, len,
# @OPUS@\upstream\silk\sum_sqr_shift.c:73:         nrg_tmp = silk_SMULBB( x[ i ], x[ i ] );
	slli	a11, a11, 1	# tmp123, i,
	add.n	a11, a4, a11	# tmp124, x, tmp123
	l16si	a10, a11, 0	# *_52, _53
	mull	a10, a10, a10	# nrg_tmp, _53, _53
# @OPUS@\upstream\silk\sum_sqr_shift.c:74:         nrg = (opus_int32)silk_ADD_RSHIFT_uint( nrg, nrg_tmp, shft );
	ssr	a12	# _88
	srl	a10, a10	# tmp128, nrg_tmp
	add.n	a10, a10, a6	# nrg, tmp128, _49
.L8:
# @OPUS@\upstream\silk\sum_sqr_shift.c:80:     *shift  = shft;
	s32i.n	a12, a3, 0	# *shift_84(D), _88
# @OPUS@\upstream\silk\sum_sqr_shift.c:82: }
	l32i.n	a13, sp, 8	#,
	l32i.n	a12, sp, 12	#,
# @OPUS@\upstream\silk\sum_sqr_shift.c:81:     *energy = nrg;
	s32i.n	a10, a2, 0	# *energy_86(D), nrg
# @OPUS@\upstream\silk\sum_sqr_shift.c:82: }
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_sum_sqr_shift, .-silk_sum_sqr_shift
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
