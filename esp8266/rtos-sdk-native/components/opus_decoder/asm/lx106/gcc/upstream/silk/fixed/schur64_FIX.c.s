# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/schur64_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"schur64_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur64_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur64_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur64_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\schur64_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\schur64_FIX.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_schur64,"ax",@progbits
	.literal_position
	.literal .LC0, -64881
	.literal .LC1, 64881
	.literal .LC2, 536870911
	.literal .LC3, -2147483648
	.literal .LC4, 2147483647
	.align	4
	.global	silk_schur64
	.type	silk_schur64, @function
# Function: silk_schur64
# Module: upstream/silk/fixed/schur64_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Slower than schur(), but more accurate.                              */
# C context: /* Uses SMULL(), available on armv4                                     */
# C context: opus_int32 silk_schur64(                            /* O    returns residual energy                                     */
# C context: opus_int32                  rc_Q16[],           /* O    Reflection coefficients [order] Q16                         */
# C context: const opus_int32            c[],                /* I    Correlations [order+1]                                      */
# C context: opus_int32                  order               /* I    Prediction order                                            */
# C context: )
silk_schur64:
	movi	a9, 0x120	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:49:     if( c[ 0 ] <= 0 ) {
	l32i.n	a5, a3, 0	# *c_69(D), *c_69(D)
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:41: {
	s32i	a0, sp, 284	#,
	s32i	a12, sp, 280	#,
	s32i	a13, sp, 276	#,
	s32i	a14, sp, 272	#,
	s32i	a15, sp, 268	#,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:41: {
	s32i	a2, sp, 232	# %sfp, rc_Q16
	s32i	a4, sp, 220	# %sfp, order
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:49:     if( c[ 0 ] <= 0 ) {
	bgei	a5, 1, .L2	# *c_69(D),,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:50:         silk_memset( rc_Q16, 0, order * sizeof( opus_int32 ) );
	slli	a4, a4, 2	#, order,
	movi.n	a3, 0	#,
	call0	memset		#
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:51:         return 0;
	movi.n	a2, 0	# <retval>,
	j	.L1		#
.L2:
	mov.n	a6, a4	# order, order
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:49:     if( c[ 0 ] <= 0 ) {
	mov.n	a2, sp	# ivtmp$37,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:54:     k = 0;
	movi.n	a4, 0	# k,
.L4:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:56:         C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	l32i.n	a5, a3, 0	# MEM[base: _351, offset: 0B], _7
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:57:     } while( ++k <= order );
	addi.n	a4, a4, 1	# k, k,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:56:         C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	s32i.n	a5, a2, 4	# MEM[base: _349, offset: 4B], _7
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:56:         C[ k ][ 0 ] = C[ k ][ 1 ] = c[ k ];
	s32i.n	a5, a2, 0	# MEM[base: _349, offset: 0B], _7
	addi.n	a3, a3, 4	# ivtmp$36, ivtmp$36,
	addi.n	a2, a2, 8	# ivtmp$37, ivtmp$37,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:57:     } while( ++k <= order );
	bge	a6, a4, .L4	# order, k,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:59:     for( k = 0; k < order; k++ ) {
	l32i	a2, sp, 220	# %sfp,
	l32i.n	a9, sp, 4	# C, _151
	blti	a2, 1, .L11	#,,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	l32i.n	a6, sp, 8	# C, _10
	srai	a2, a6, 31	# tmp174, _10,
	xor	a2, a2, a6	# tmp175, tmp174, _10
	extui	a3, a6, 31, 1	# tmp176, _10,
	add.n	a2, a2, a3	# tmp177, tmp175, tmp176
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	blt	a2, a9, .L33	# tmp177, _151,
	j	.L27		#
.L25:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	addi.n	a3, a3, 1	#,,
	slli	a2, a3, 3	# tmp178,,
	add.n	a2, sp, a2	# tmp179,, tmp178
	l32i.n	a6, a2, 0	# MEM[base: _370, offset: 0B], _10
	l32i	a4, sp, 216	# %sfp,
	l32i	a5, sp, 208	# %sfp,
	srai	a2, a6, 31	# tmp180, _10,
	s32i	a3, sp, 212	# %sfp,
	addi.n	a4, a4, 4	#,,
	xor	a2, a2, a6	# tmp181, tmp180, _10
	extui	a3, a6, 31, 1	# tmp182, _10,
	addi	a5, a5, -8	#,,
	s32i	a4, sp, 216	# %sfp,
	add.n	a2, a2, a3	# tmp183, tmp181, tmp182
	s32i	a5, sp, 208	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	blt	a2, a9, .L8	# tmp183, _151,
	l32i	a3, sp, 228	# %sfp,
	l32i	a4, sp, 232	# %sfp,
	slli	a2, a3, 2	# tmp184,,
	add.n	a2, a4, a2	# _409,, tmp184
	j	.L6		#
.L27:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	movi.n	a5, 1	#,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	l32i	a2, sp, 232	# %sfp, _409
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	s32i	a5, sp, 212	# %sfp,
.L6:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:62:            if ( C[ k + 1 ][ 0 ] > 0 ) {
	blti	a6, 1, .L9	# _10,,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:63:               rc_Q16[ k ] = -SILK_FIX_CONST( .99f, 16 );
	l32r	a3, .LC0	#, tmp185
	s32i.n	a3, a2, 0	# *prephitmp_412, tmp185
.L12:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:88:     for(; k < order; k++ ) {
	l32i	a2, sp, 212	# %sfp,
	l32i	a3, sp, 220	# %sfp,
	blt	a2, a3, .L10	#,,
	j	.L11		#
.L9:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:65:               rc_Q16[ k ] = SILK_FIX_CONST( .99f, 16 );
	l32r	a3, .LC1	#, tmp186
	s32i.n	a3, a2, 0	# *prephitmp_412, tmp186
	j	.L12		#
.L33:
	l32i	a4, sp, 220	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:61:         if (silk_abs_int32(C[ k + 1 ][ 0 ]) >= C[ 0 ][ 1 ]) {
	movi.n	a2, 1	#,
	slli	a14, a4, 3	# tmp187,,
	l32i	a5, sp, 232	# %sfp,
	add.n	a14, a14, sp	#, tmp187,
	add.n	a3, a4, a2	#,,
	s32i	a5, sp, 216	# %sfp,
	s32i	a14, sp, 208	# %sfp,
	s32i	a2, sp, 212	# %sfp,
	s32i	a3, sp, 224	# %sfp,
.L8:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:72:         rc_tmp_Q31 = silk_DIV32_varQ( -C[ k + 1 ][ 0 ], C[ 0 ][ 1 ], 31 );
	neg	a13, a6	# _26, _10
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a13, .L28	# _26,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a6, a6	# tmp188, _10
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a6	# iftmp$14_92, tmp188
	addi	a12, a15, -2	# _314, iftmp$14_92,
	addi.n	a3, a15, -1	# _316, iftmp$14_92,
	j	.L13		#
.L28:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a3, 0x1f	# _316,
	movi.n	a12, 0x1e	# _314,
	movi.n	a15, 0x20	# iftmp$14_92,
.L13:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a3	# _316
	sll	a13, a13	# _96, _26
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a9, .L29	# _151,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a10, a9	# tmp189, _151
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a14, a10	# iftmp$14_100, tmp189
	addi.n	a11, a14, -1	# _354, iftmp$14_100,
	j	.L14		#
.L29:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a11, 0x1f	# _354,
	movi.n	a14, 0x20	# iftmp$14_100,
.L14:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a11	# _354
	sll	a11, a9	# b32_nrm, _151
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC2	#,
	srai	a3, a11, 16	#, b32_nrm,
	s32i	a9, sp, 240	#,
	s32i	a11, sp, 236	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp195,,
	srai	a8, a2, 16	# _110, tmp195,
	extui	a7, a13, 0, 16	# tmp196, _96,
	mull	a7, a7, a8	# tmp197, tmp196, _110
	srai	a2, a13, 16	# tmp199, _96,
	mull	a2, a2, a8	# tmp200, tmp199, _110
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a11, sp, 236	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a7, a7, 16	# tmp198, tmp197,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a2	# result, tmp198, tmp200
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a7	#, result
	srai	a5, a7, 31	#, result,
	mov.n	a2, a11	#, b32_nrm
	srai	a3, a11, 31	#, b32_nrm,
	s32i	a7, sp, 244	#,
	s32i	a8, sp, 236	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp207,,
	sub	a13, a13, a3	# a32_nrm, _96, tmp207
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a8, sp, 236	#,
	srai	a2, a13, 16	# tmp208, a32_nrm,
	extui	a13, a13, 0, 16	# tmp210, a32_nrm,
	mull	a2, a2, a8	# tmp209, tmp208, _110
	l32i	a7, sp, 244	#,
	mull	a8, a13, a8	# tmp211, tmp210, _110
	add.n	a2, a2, a7	# _8, tmp209, result
	srai	a7, a8, 16	# tmp212, tmp211,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a7, a7, a2	# result, tmp212, _8
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a2, a12, a14	# lshift, _314, iftmp$14_100
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a2	# lshift
	sra	a12, a7	# _148, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a9, sp, 240	#,
	bgez	a2, .L22	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	movi.n	a4, 2	#,
	sub	a12, a4, a15	# tmp214,, iftmp$14_92
	l32r	a5, .LC3	#,
	l32r	a4, .LC4	#,
	add.n	a12, a12, a14	# _136, tmp214, iftmp$14_100
	ssr	a12	# _136
	sra	a2, a5	# _137,
	ssr	a12	# _136
	sra	a3, a4	# _138,
	bge	a3, a2, .L16	# _138, _137,
	bge	a2, a7, .L17	# _137, result,
	j	.L34		#
.L17:
	bge	a7, a3, .L18	# iftmp$12_139, _138,
	j	.L35		#
.L16:
	bge	a3, a7, .L20	# _138, result,
.L35:
	mov.n	a7, a3	# iftmp$12_139, _138
	j	.L18		#
.L20:
	bge	a7, a2, .L18	# iftmp$12_139, _137,
.L34:
	mov.n	a7, a2	# iftmp$12_139, _137
.L18:
	ssl	a12	# _136
	sll	a12, a7	# _148, iftmp$12_139
.L22:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:75:         rc_Q16[ k ] = silk_RSHIFT_ROUND( rc_tmp_Q31, 15 );
	srai	a2, a12, 14	# tmp217, _148,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:78:         for( n = 0; n < order - k; n++ ) {
	l32i	a4, sp, 212	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:75:         rc_Q16[ k ] = silk_RSHIFT_ROUND( rc_tmp_Q31, 15 );
	addi.n	a2, a2, 1	# tmp218, tmp217,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:75:         rc_Q16[ k ] = silk_RSHIFT_ROUND( rc_tmp_Q31, 15 );
	l32i	a5, sp, 216	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:78:         for( n = 0; n < order - k; n++ ) {
	l32i	a3, sp, 224	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:75:         rc_Q16[ k ] = silk_RSHIFT_ROUND( rc_tmp_Q31, 15 );
	srai	a2, a2, 1	# tmp219, tmp218,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:75:         rc_Q16[ k ] = silk_RSHIFT_ROUND( rc_tmp_Q31, 15 );
	s32i.n	a2, a5, 0	# MEM[base: _369, offset: 0B], tmp219
	s32i	a4, sp, 228	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:78:         for( n = 0; n < order - k; n++ ) {
	sub	a2, a3, a4	# tmp221,,
	blti	a2, 1, .L23	# tmp221,,
	slli	a9, a4, 3	# tmp223,,
	srai	a13, a12, 31	# _393, _148,
	add.n	a14, a9, sp	# ivtmp$18, tmp223,
	mov.n	a15, sp	# ivtmp$21,
.L24:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:80:             Ctmp2_Q30 = C[ n ][ 1 ];
	l32i.n	a6, a15, 4	# MEM[base: _387, offset: 4B], Ctmp2_Q30
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:79:             Ctmp1_Q30 = C[ n + k + 1 ][ 0 ];
	l32i.n	a7, a14, 0	# MEM[base: _389, offset: 0B], Ctmp1_Q30
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:83:             C[ n + k + 1 ][ 0 ] = Ctmp1_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp2_Q30, 1 ), rc_tmp_Q31 );
	slli	a3, a6, 1	# tmp224, Ctmp2_Q30,
	mov.n	a4, a12	#, _148
	mov.n	a5, a13	#, _393
	mov.n	a2, a3	#, tmp224
	srai	a3, a3, 31	#, tmp224,
	s32i	a6, sp, 236	#,
	s32i	a7, sp, 244	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:84:             C[ n ][ 1 ]         = Ctmp2_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp1_Q30, 1 ), rc_tmp_Q31 );
	l32i	a7, sp, 244	#,
	mov.n	a5, a13	#, _393
	slli	a9, a7, 1	# tmp230, Ctmp1_Q30,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:83:             C[ n + k + 1 ][ 0 ] = Ctmp1_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp2_Q30, 1 ), rc_tmp_Q31 );
	add.n	a7, a7, a3	# tmp229, Ctmp1_Q30,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:83:             C[ n + k + 1 ][ 0 ] = Ctmp1_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp2_Q30, 1 ), rc_tmp_Q31 );
	s32i.n	a7, a14, 0	# MEM[base: _389, offset: 0B], tmp229
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:84:             C[ n ][ 1 ]         = Ctmp2_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp1_Q30, 1 ), rc_tmp_Q31 );
	mov.n	a4, a12	#, _148
	mov.n	a2, a9	#, tmp230
	srai	a3, a9, 31	#, tmp230,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:84:             C[ n ][ 1 ]         = Ctmp2_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp1_Q30, 1 ), rc_tmp_Q31 );
	l32i	a6, sp, 236	#,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:78:         for( n = 0; n < order - k; n++ ) {
	l32i	a5, sp, 208	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:84:             C[ n ][ 1 ]         = Ctmp2_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp1_Q30, 1 ), rc_tmp_Q31 );
	add.n	a3, a6, a3	# tmp235, Ctmp2_Q30,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:84:             C[ n ][ 1 ]         = Ctmp2_Q30 + silk_SMMUL( silk_LSHIFT( Ctmp1_Q30, 1 ), rc_tmp_Q31 );
	s32i.n	a3, a15, 4	# MEM[base: _387, offset: 4B], tmp235
	addi.n	a15, a15, 8	# ivtmp$21, ivtmp$21,
	addi.n	a14, a14, 8	# ivtmp$18, ivtmp$18,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:78:         for( n = 0; n < order - k; n++ ) {
	bne	a5, a15, .L24	#, ivtmp$21,
	l32i.n	a9, sp, 4	# C, _151
.L23:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:59:     for( k = 0; k < order; k++ ) {
	l32i	a2, sp, 220	# %sfp,
	l32i	a3, sp, 212	# %sfp,
	bne	a2, a3, .L25	#,,
	j	.L11		#
.L10:
	l32i	a5, sp, 232	# %sfp,
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:89:        rc_Q16[ k ] = 0;
	sub	a4, a3, a2	# tmp236, tmp5,
	slli	a2, a2, 2	# tmp238,,
	slli	a4, a4, 2	#, tmp236,
	movi.n	a3, 0	#,
	add.n	a2, a5, a2	#,, tmp238
	s32i	a9, sp, 240	#,
	call0	memset		#
	l32i	a9, sp, 240	#,
.L11:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:574:     return (((a) > (b)) ? (a) : (b));
	mov.n	a2, a9	# <retval>, _151
	bgei	a9, 1, .L1	# <retval>,,
	movi.n	a2, 1	# <retval>,
.L1:
# @OPUS@\upstream\silk\fixed\schur64_FIX.c:93: }
	l32i	a0, sp, 284	#,
	movi	a9, 0x120	#,
	l32i	a12, sp, 280	#,
	l32i	a13, sp, 276	#,
	l32i	a14, sp, 272	#,
	l32i	a15, sp, 268	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_schur64, .-silk_schur64
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
