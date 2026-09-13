# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/burg_modified_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"burg_modified_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\burg_modified_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\burg_modified_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\burg_modified_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\burg_modified_FIX.c.s.raw
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
	.global	__divsi3
	.section	.text.silk_burg_modified_c,"ax",@progbits
	.literal_position
	.literal .LC0, 1073741824
	.literal .LC1, 2147483647, 0
	.literal .LC2, 2147483647
	.literal .LC3, -2147483648, -1
	.literal .LC4, -2147483648
	.literal .LC5, 0, 0
	.literal .LC6, 65536
	.literal .LC7, 32768
	.literal .LC8, 46214
	.literal .LC9, 42950, 0
	.literal .LC10, 536870911
	.align	4
	.global	silk_burg_modified_c
	.type	silk_burg_modified_c, @function
# Function: silk_burg_modified_c
# Module: upstream/silk/fixed/burg_modified_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define MAX_RSHIFTS                 (32 - QA)
# C context:
# C context: /* Compute reflection coefficients from input signal */
# C context: void silk_burg_modified_c(
# C context: opus_int32                  *res_nrg,           /* O    Residual energy                                             */
# C context: opus_int                    *res_nrg_Q,         /* O    Residual energy Q value                                     */
# C context: opus_int32                  A_Q16[],            /* O    Prediction coefficients (length order)                      */
# C context: const opus_int16            x[],                /* I    Input signal, length: nb_subfr * ( D + subfr_length )       */
silk_burg_modified_c:
	movi	a9, 0x330	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:71:     C0_64 = silk_inner_prod16( x, x, subfr_length*nb_subfr, arch );
	l32i	a8, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:56: {
	s32i	a4, sp, 752	# %sfp, A_Q16
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:71:     C0_64 = silk_inner_prod16( x, x, subfr_length*nb_subfr, arch );
	mull	a4, a7, a8	#, subfr_length,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:56: {
	s32i	a2, sp, 744	# %sfp, res_nrg
	s32i	a3, sp, 748	# %sfp, res_nrg_Q
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:71:     C0_64 = silk_inner_prod16( x, x, subfr_length*nb_subfr, arch );
	mov.n	a2, a5	#, x
	mov.n	a3, a5	#, tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:56: {
	s32i	a15, sp, 796	#,
	s32i	a0, sp, 812	#,
	s32i	a12, sp, 808	#,
	s32i	a13, sp, 804	#,
	s32i	a14, sp, 800	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:56: {
	s32i	a7, sp, 636	# %sfp, subfr_length
	s32i	a5, sp, 716	# %sfp, x
	s32i	a6, sp, 720	# %sfp, minInvGain_Q30
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:71:     C0_64 = silk_inner_prod16( x, x, subfr_length*nb_subfr, arch );
	call0	silk_inner_prod16_c		#
	mov.n	a15, a3	# C0_64,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:46:     if (in_upper == 0) {
	bnez.n	a3, .L2	# C0_64,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a2, .L85	# C0_64,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a4, a2	# iftmp$15_514, C0_64
	movi.n	a3, 4	# tmp720,
	sub	a3, a3, a4	#, tmp720, iftmp$15_514
	s32i	a3, sp, 712	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:75:     if (rshifts < MIN_RSHIFTS) rshifts = MIN_RSHIFTS;
	l32i	a9, sp, 712	# %sfp,
	movi.n	a3, -0x10	# tmp721,
	bge	a9, a3, .L129	#, tmp721,
	j	.L86		#
.L2:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a3, a3	# iftmp$15_653, C0_64
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:73:     rshifts = 32 + 1 + N_BITS_HEAD_ROOM - lz;
	movi.n	a4, 0x24	# tmp722,
	sub	a4, a4, a3	#, tmp722, iftmp$15_653
	s32i	a4, sp, 712	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:74:     if (rshifts > MAX_RSHIFTS) rshifts = MAX_RSHIFTS;
	bgei	a4, 8, .L87	#,,
	j	.L130		#
.L129:
	addi	a4, a4, -4	#, iftmp$15_514,
	s32i	a4, sp, 680	# %sfp,
	mov.n	a14, a9	#,
	mov.n	a8, a9	#, tmp14
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:77:     if (rshifts > 0) {
	bgei	a9, 1, .L5	# tmp14,,
	j	.L3		#
.L87:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:74:     if (rshifts > MAX_RSHIFTS) rshifts = MAX_RSHIFTS;
	movi.n	a9, 7	#,
	movi.n	a8, -7	#,
	s32i	a8, sp, 680	# %sfp,
	s32i	a9, sp, 712	# %sfp,
	mov.n	a14, a9	#,
	mov.n	a8, a9	#,
.L5:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:78:         C0 = (opus_int32)silk_RSHIFT64(C0_64, rshifts );
	movi.n	a12, -1	# tmp728,
	xor	a4, a14, a12	# tmp729,, tmp728
	slli	a3, a15, 1	# tmp727, C0_64,
	ssl	a4	# tmp729
	sll	a3, a3	# tmp730, tmp727
	ssr	a14	#
	srl	a2, a2	# tmp1165, C0_64
	movi.n	a14, 0x20	# tmp724,
	and	a14, a8, a14	# tmp725,, tmp724
	ssr	a8	#
	sra	a15, a15	# tmp1166, C0_64
	or	a2, a3, a2	# tmp1165, tmp730, tmp1165
	movnez	a2, a15, a14	# tmp1165, tmp1166, tmp725
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	srai	a9, a2, 31	#, tmp1165,
	l32r	a4, .LC9	#,
	l32r	a5, .LC9+4	#,
	mov.n	a3, a9	#,
	s32i	a9, sp, 740	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:78:         C0 = (opus_int32)silk_RSHIFT64(C0_64, rshifts );
	s32i	a2, sp, 724	# %sfp, tmp1165
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32i	a8, sp, 724	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i	a3, sp, 736	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	addi.n	a2, a8, 1	# tmp735,,
	add.n	a2, a2, a3	#, tmp735,
	s32i	a2, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32i	a9, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:84:     silk_memset( C_first_row, 0, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	movi	a2, 0x1e8	# tmp736,
	movi	a4, 0x60	#,
	movi.n	a3, 0	#,
	add.n	a2, sp, a2	#,, tmp736
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i	a9, sp, 100	# CAf,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i.n	a9, sp, 0	# CAb,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:84:     silk_memset( C_first_row, 0, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	call0	memset		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
	bgei	a8, 1, .L7	#,,
	j	.L8		#
.L85:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a9, 0x10	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:75:     if (rshifts < MIN_RSHIFTS) rshifts = MIN_RSHIFTS;
	movi.n	a14, -0x10	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	s32i	a9, sp, 680	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:75:     if (rshifts < MIN_RSHIFTS) rshifts = MIN_RSHIFTS;
	s32i	a14, sp, 712	# %sfp,
	j	.L3		#
.L86:
	movi.n	a8, 0x10	#,
	s32i	a8, sp, 680	# %sfp,
	s32i	a3, sp, 712	# %sfp, tmp721
.L3:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:80:         C0 = silk_LSHIFT32((opus_int32)C0_64, -rshifts );
	l32i	a9, sp, 680	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32r	a4, .LC9	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:80:         C0 = silk_LSHIFT32((opus_int32)C0_64, -rshifts );
	ssl	a9	#
	sll	a2, a2	#, C0_64
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	srai	a14, a2, 31	#,,
	l32r	a5, .LC9+4	#,
	mov.n	a3, a14	#,
	s32i	a14, sp, 740	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:80:         C0 = silk_LSHIFT32((opus_int32)C0_64, -rshifts );
	s32i	a2, sp, 724	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32i	a8, sp, 724	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i	a3, sp, 736	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	addi.n	a2, a8, 1	# tmp745,,
	add.n	a2, a2, a3	#, tmp745, tmp9
	s32i	a2, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32i	a14, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:84:     silk_memset( C_first_row, 0, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	movi	a2, 0x1e8	#,
	movi	a4, 0x60	#,
	movi.n	a3, 0	#,
	add.n	a2, a2, sp	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i	a14, sp, 100	# CAf,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:83:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i.n	a14, sp, 0	# CAb,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:84:     silk_memset( C_first_row, 0, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	call0	memset		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
	bgei	a8, 1, .L9	#,,
	j	.L8		#
.L7:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:88:             for( n = 1; n < D + 1; n++ ) {
	l32i	a9, sp, 820	# D,
	addi.n	a2, a9, 1	# tmp751,,
	blti	a2, 2, .L8	# tmp751,,
	movi.n	a2, -1	#,
	xor	a15, a2, a9	# tmp753,,
	l32i	a5, sp, 636	# %sfp,
	l32i	a6, sp, 716	# %sfp,
	l32i	a8, sp, 636	# %sfp,
	l32i	a9, sp, 636	# %sfp,
	slli	a5, a5, 1	#,,
	addi.n	a6, a6, 2	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	movi.n	a7, 0	#,
	add.n	a8, a8, a2	#,,
	add.n	a9, a15, a9	#, tmp753,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	s32i	a14, sp, 616	# %sfp, tmp725
	l32i	a14, sp, 712	# %sfp, rshifts
	s32i	a5, sp, 632	# %sfp,
	s32i	a6, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	s32i	a7, sp, 624	# %sfp,
	s32i	a8, sp, 648	# %sfp,
	s32i	a9, sp, 612	# %sfp,
.L11:
	l32i	a5, sp, 620	# %sfp,
	l32i	a15, sp, 620	# %sfp, ivtmp$209
	addi	a5, a5, -2	#,,
	l32i	a13, sp, 648	# %sfp, ivtmp$211
	s32i	a5, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	movi.n	a6, -1	#,
	movi	a5, 0x1e8	# tmp752,
	add.n	a12, sp, a5	# ivtmp$213,, tmp752
	xor	a6, a14, a6	#, rshifts,
	mov.n	a2, a15	# ivtmp$209, ivtmp$209
	s32i	a6, sp, 608	# %sfp,
	mov.n	a15, a12	# ivtmp$213, ivtmp$213
	mov.n	a12, a13	# ivtmp$211, ivtmp$211
	mov.n	a13, a14	# rshifts, rshifts
	mov.n	a14, a2	# ivtmp$209, ivtmp$209
	j	.L10		#
.L133:
	l32i	a8, sp, 620	# %sfp,
	l32i	a9, sp, 632	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a7, sp, 624	# %sfp,
	add.n	a8, a8, a9	#,,
	addi.n	a7, a7, 1	#,,
	s32i	a8, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	s32i	a7, sp, 624	# %sfp,
	mov.n	a14, a13	# rshifts, rshifts
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:86:         for( s = 0; s < nb_subfr; s++ ) {
	bne	a8, a7, .L11	#,,
	j	.L8		#
.L10:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	l32i	a2, sp, 604	# %sfp,
	mov.n	a4, a12	#, ivtmp$211
	mov.n	a3, a14	#, ivtmp$209
	call0	silk_inner_prod16_c		#
	l32i	a5, sp, 608	# %sfp,
	slli	a9, a3, 1	# tmp759, _20,
	ssl	a5	#
	sll	a9, a9	# tmp762, tmp759
	ssr	a13	# rshifts
	srl	a2, a2	# tmp1179,
	l32i	a6, sp, 616	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	l32i.n	a4, a15, 0	# MEM[base: _2306, offset: 0B], MEM[base: _2306, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	or	a2, a9, a2	# tmp1179, tmp762, tmp1179
	ssr	a13	# rshifts
	sra	a3, a3	# tmp1180, _20
	movnez	a2, a3, a6	# tmp1179, tmp1180,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	add.n	a2, a4, a2	# tmp763, MEM[base: _2306, offset: 0B], tmp1179
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:88:             for( n = 1; n < D + 1; n++ ) {
	l32i	a7, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:89:                 C_first_row[ n - 1 ] += (opus_int32)silk_RSHIFT64(
	s32i.n	a2, a15, 0	# MEM[base: _2306, offset: 0B], tmp763
	addi.n	a12, a12, -1	# ivtmp$211, ivtmp$211,
	addi.n	a14, a14, 2	# ivtmp$209, ivtmp$209,
	addi.n	a15, a15, 4	# ivtmp$213, ivtmp$213,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:88:             for( n = 1; n < D + 1; n++ ) {
	bne	a7, a12, .L10	#, ivtmp$211,
	j	.L133		#
.L9:
	l32i	a9, sp, 820	# D,
	l32i	a8, sp, 636	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:99:             for( n = 1; n < D + 1; n++ ) {
	addi.n	a14, a9, 1	#,,
	sub	a8, a8, a9	#,,
	s32i	a8, sp, 616	# %sfp,
	l32i	a8, sp, 636	# %sfp,
	l32i	a9, sp, 616	# %sfp,
	slli	a8, a8, 1	#,,
	s32i	a8, sp, 608	# %sfp,
	l32i	a8, sp, 820	# D,
	s32i	a14, sp, 620	# %sfp,
	slli	a13, a9, 1	# tmp765,,
	slli	a14, a8, 2	# tmp767,,
	l32i	a9, sp, 716	# %sfp, ivtmp$201
	l32i	a8, sp, 608	# %sfp,
	movi	a2, 0x1e8	#,
	l32i	a3, sp, 620	# %sfp,
	l32i	a4, sp, 616	# %sfp,
	add.n	a12, a9, a8	# ivtmp$203, ivtmp$201,
	add.n	a13, a13, a9	# ivtmp$204, tmp765, ivtmp$201
	add.n	a2, a2, sp	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	s32i	a15, sp, 612	# %sfp, C0_64
	s32i	a9, sp, 604	# %sfp, ivtmp$201
	mov.n	a9, a15	# C0_64, C0_64
	l32i	a15, sp, 636	# %sfp, subfr_length
	add.n	a14, a14, a2	# _2393, tmp767,
	add.n	a8, a3, a4	# _2347,,
.L14:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:98:             celt_pitch_xcorr(x_ptr, x_ptr + 1, xcorr, subfr_length - D, D, arch );
	l32i	a2, sp, 604	# %sfp,
	l32i	a7, sp, 824	# arch,
	l32i	a6, sp, 820	# D,
	l32i	a5, sp, 616	# %sfp,
	movi	a4, 0xc8	#,
	addi.n	a3, a2, 2	#,,
	add.n	a4, a4, sp	#,,
	s32i	a8, sp, 772	#,
	s32i	a9, sp, 776	#,
	call0	celt_pitch_xcorr_c		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:99:             for( n = 1; n < D + 1; n++ ) {
	l32i	a3, sp, 620	# %sfp,
	l32i	a8, sp, 772	#,
	l32i	a9, sp, 776	#,
	bgei	a3, 2, .L13	#,,
.L19:
	l32i	a6, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a4, sp, 612	# %sfp,
	l32i	a5, sp, 604	# %sfp,
	addi.n	a4, a4, 1	#,,
	add.n	a5, a5, a6	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	l32i	a7, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	s32i	a4, sp, 612	# %sfp,
	s32i	a5, sp, 604	# %sfp,
	add.n	a12, a12, a6	# ivtmp$203, ivtmp$203,
	add.n	a13, a13, a6	# ivtmp$204, ivtmp$204,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:94:         for( s = 0; s < nb_subfr; s++ ) {
	bne	a7, a4, .L14	#,,
	j	.L8		#
.L13:
	l32i	a2, sp, 616	# %sfp,
	movi	a11, 0xc8	# ivtmp$181,
	add.n	a11, a11, sp	# ivtmp$181, ivtmp$181,
	addi.n	a10, a2, 1	# ivtmp$192,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:99:             for( n = 1; n < D + 1; n++ ) {
	mov.n	a7, a11	# ivtmp$194, ivtmp$181
	movi.n	a6, -2	# ivtmp$197,
.L17:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:100:                for ( i = n + subfr_length - D, d = 0; i < subfr_length; i++ )
	bge	a10, a15, .L88	# ivtmp$192, subfr_length,
	sub	a2, a13, a6	# ivtmp$186, ivtmp$204, ivtmp$197
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:100:                for ( i = n + subfr_length - D, d = 0; i < subfr_length; i++ )
	mov.n	a4, a9	# d, C0_64
.L16:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:101:                   d = MAC16_16( d, x_ptr[ i ], x_ptr[ i - n ] );
	add.n	a3, a2, a6	# tmp773, ivtmp$186, ivtmp$197
	l16ui	a5, a2, 0	# MEM[base: _2373, offset: 0B],
	l16ui	a3, a3, 0	# MEM[base: _2369, offset: 0B],
	addi.n	a2, a2, 2	# ivtmp$186, ivtmp$186,
	mul16s	a3, a3, a5	# tmp774, MEM[base: _2369, offset: 0B], MEM[base: _2373, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:101:                   d = MAC16_16( d, x_ptr[ i ], x_ptr[ i - n ] );
	add.n	a4, a4, a3	# d, d, tmp774
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:100:                for ( i = n + subfr_length - D, d = 0; i < subfr_length; i++ )
	bne	a12, a2, .L16	# ivtmp$203, ivtmp$186,
	j	.L15		#
.L88:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:100:                for ( i = n + subfr_length - D, d = 0; i < subfr_length; i++ )
	mov.n	a4, a9	# d, C0_64
.L15:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:102:                xcorr[ n - 1 ] += d;
	l32i.n	a2, a7, 0	# MEM[base: _2352, offset: 0B], MEM[base: _2352, offset: 0B]
	addi.n	a10, a10, 1	# ivtmp$192, ivtmp$192,
	add.n	a4, a2, a4	# tmp777, MEM[base: _2352, offset: 0B], d
	s32i.n	a4, a7, 0	# MEM[base: _2352, offset: 0B], tmp777
	addi	a6, a6, -2	# ivtmp$197, ivtmp$197,
	addi.n	a7, a7, 4	# ivtmp$194, ivtmp$194,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:99:             for( n = 1; n < D + 1; n++ ) {
	bne	a8, a10, .L17	# _2347, ivtmp$192,
	movi	a2, 0x1e8	# ivtmp$180,
	l32i	a5, sp, 680	# %sfp, prephitmp_1993
	add.n	a2, a2, sp	# ivtmp$180, ivtmp$180,
.L18:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:105:                 C_first_row[ n - 1 ] += silk_LSHIFT32( xcorr[ n - 1 ], -rshifts );
	l32i.n	a4, a11, 0	# MEM[base: _2397, offset: 0B], MEM[base: _2397, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:105:                 C_first_row[ n - 1 ] += silk_LSHIFT32( xcorr[ n - 1 ], -rshifts );
	l32i.n	a3, a2, 0	# MEM[base: _2399, offset: 0B], MEM[base: _2399, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:105:                 C_first_row[ n - 1 ] += silk_LSHIFT32( xcorr[ n - 1 ], -rshifts );
	ssl	a5	# prephitmp_1993
	sll	a4, a4	# tmp779, MEM[base: _2397, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:105:                 C_first_row[ n - 1 ] += silk_LSHIFT32( xcorr[ n - 1 ], -rshifts );
	add.n	a3, a3, a4	# tmp781, MEM[base: _2399, offset: 0B], tmp779
	s32i.n	a3, a2, 0	# MEM[base: _2399, offset: 0B], tmp781
	addi.n	a2, a2, 4	# ivtmp$180, ivtmp$180,
	addi.n	a11, a11, 4	# ivtmp$181, ivtmp$181,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:104:             for( n = 1; n < D + 1; n++ ) {
	bne	a14, a2, .L18	# _2393, ivtmp$180,
	j	.L19		#
.L8:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:109:     silk_memcpy( C_last_row, C_first_row, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	movi	a7, 0x188	#,
	movi	a6, 0x1e8	#,
	add.n	a6, sp, a6	#,,
	add.n	a5, sp, a7	# tmp787,,
	mov.n	a2, a5	#, tmp787
	movi	a4, 0x60	#,
	mov.n	a3, a6	#,
	s32i	a6, sp, 600	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:112:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	l32i	a8, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	l32i	a9, sp, 820	# D,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:112:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i	a8, sp, 100	# CAf,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:112:     CAb[ 0 ] = CAf[ 0 ] = C0 + silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ) + 1;                                /* Q(-rshifts) */
	s32i.n	a8, sp, 0	# CAb,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:109:     silk_memcpy( C_last_row, C_first_row, SILK_MAX_ORDER_LPC * sizeof( opus_int32 ) );
	mov.n	a5, a2	# tmp787,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	blti	a9, 1, .L89	#,,
	l32i	a14, sp, 636	# %sfp,
	l32r	a2, .LC2	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	l32i	a8, sp, 720	# %sfp,
	add.n	a3, a14, a2	# tmp795,,
	abs	a2, a8	# tmp1331,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a2	#, tmp1331
	s32i	a2, sp, 728	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	movi	a2, 0x188	#,
	slli	a3, a3, 1	#, tmp795,
	add.n	a2, a2, sp	#,,
	l32i	a7, sp, 728	# %sfp,
	addi.n	a14, a3, 2	#,,
	movi	a9, 0x128	#,
	s32i	a3, sp, 668	# %sfp,
	s32i	a2, sp, 696	# %sfp,
	movi	a3, 0x1e8	#,
	l32i	a2, sp, 628	# %sfp, pretmp_2648
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:114:     invGain_Q30 = (opus_int32)1 << 30;
	l32r	a4, .LC0	#,
	add.n	a9, sp, a9	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	add.n	a3, a3, sp	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	movi.n	a6, 0	#,
	addi.n	a7, a7, -1	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	s32i	a3, sp, 700	# %sfp,
	s32i	a5, sp, 592	# %sfp, tmp787
	s32i	a9, sp, 684	# %sfp,
	s32i	sp, sp, 596	# %sfp,
	s32i	a14, sp, 648	# %sfp,
	s32i	a9, sp, 704	# %sfp,
	s32i	sp, sp, 692	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:114:     invGain_Q30 = (opus_int32)1 << 30;
	s32i	a4, sp, 708	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	s32i	a6, sp, 664	# %sfp,
	s32i	a7, sp, 732	# %sfp,
	mov.n	a3, a2	# pretmp_2649, pretmp_2648
.L74:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:121:         if( rshifts > -2 ) {
	l32i	a8, sp, 712	# %sfp,
	bgei	a8, -1, .L21	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a9, sp, 816	# nb_subfr,
	bgei	a9, 1, .L22	#,,
	j	.L23		#
.L21:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a14, sp, 816	# nb_subfr,
	blti	a14, 1, .L23	#,,
	l32i	a2, sp, 664	# %sfp,
	l32i	a14, sp, 716	# %sfp,
	slli	a2, a2, 1	#,,
	s32i	a2, sp, 688	# %sfp,
	movi.n	a2, 0x10	# tmp797,
	sub	a2, a2, a8	#, tmp797,
	s32i	a2, sp, 672	# %sfp,
	movi.n	a2, 7	# tmp798,
	sub	a2, a2, a8	#, tmp798,
	s32i	a2, sp, 676	# %sfp,
	l32i	a9, sp, 688	# %sfp,
	l32i	a2, sp, 668	# %sfp,
	add.n	a9, a9, a14	#,,
	add.n	a2, a14, a2	#,,
	addi	a3, a14, -2	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	movi.n	a4, 0	#,
	s32i	a9, sp, 656	# %sfp,
	s32i	a2, sp, 652	# %sfp,
	s32i	a3, sp, 620	# %sfp,
	s32i	a4, sp, 660	# %sfp,
.L27:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:124:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    16 - rshifts );        /* Q(16-rshifts) */
	l32i	a5, sp, 620	# %sfp,
	l32i	a6, sp, 688	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:125:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], 16 - rshifts );        /* Q(16-rshifts) */
	l32i	a7, sp, 668	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:124:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    16 - rshifts );        /* Q(16-rshifts) */
	add.n	a3, a5, a6	# tmp799,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:125:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], 16 - rshifts );        /* Q(16-rshifts) */
	add.n	a2, a5, a7	# tmp803,,
	l16si	a4, a2, 2	# MEM[base: _2549, offset: 2B], _84
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:124:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    16 - rshifts );        /* Q(16-rshifts) */
	l16si	a5, a3, 2	# MEM[base: _2552, offset: 2B], _74
	l32i	a8, sp, 672	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:128:                 for( k = 0; k < n; k++ ) {
	l32i	a9, sp, 664	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:124:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    16 - rshifts );        /* Q(16-rshifts) */
	ssl	a8	#
	sll	a3, a5	# tmp802, _74
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:125:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], 16 - rshifts );        /* Q(16-rshifts) */
	ssl	a8	#
	sll	a2, a4	# tmp806, _84
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:126:                 tmp1 = silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    QA - 16 );             /* Q(QA-16) */
	slli	a5, a5, 9	#, _74,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:127:                 tmp2 = silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], QA - 16 );             /* Q(QA-16) */
	slli	a4, a4, 9	#, _84,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:126:                 tmp1 = silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    QA - 16 );             /* Q(QA-16) */
	s32i	a5, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:127:                 tmp2 = silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], QA - 16 );             /* Q(QA-16) */
	s32i	a4, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:124:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    16 - rshifts );        /* Q(16-rshifts) */
	neg	a3, a3	# x1, tmp802
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:125:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], 16 - rshifts );        /* Q(16-rshifts) */
	neg	a2, a2	# x2, tmp806
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:128:                 for( k = 0; k < n; k++ ) {
	beqz.n	a9, .L24	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	srai	a14, a3, 16	#, x1,
	l32i	a5, sp, 656	# %sfp,
	l32i	a6, sp, 652	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	srai	a4, a2, 16	#, x2,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	s32i	a14, sp, 624	# %sfp,
	extui	a3, a3, 0, 16	#, x1,
	extui	a2, a2, 0, 16	#, x2,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	movi	a10, 0x188	# ivtmp$86,
	movi	a9, 0x1e8	# ivtmp$83,
	l32i	a14, sp, 684	# %sfp, ivtmp$88
	s32i	a4, sp, 628	# %sfp,
	s32i	a3, sp, 632	# %sfp,
	s32i	a2, sp, 636	# %sfp,
	addi	a11, a5, -2	# ivtmp$84,,
	addi.n	a15, a6, 2	# ivtmp$87,,
	add.n	a10, a10, sp	# ivtmp$86, ivtmp$86,
	add.n	a9, a9, sp	# ivtmp$83, ivtmp$83,
.L25:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l16si	a4, a11, 0	# MEM[base: _2591, offset: 0B], _97
	l32i	a5, sp, 624	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l16si	a3, a15, 0	# MEM[base: _2581, offset: 0B], _111
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	mull	a7, a5, a4	# tmp809,, _97
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l32i	a5, sp, 628	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:131:                     Atmp_QA = Af_QA[ k ];
	l32i.n	a8, a14, 0	# MEM[base: _2580, offset: 0B], Atmp_QA
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	mull	a12, a5, a3	# tmp817,, _111
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l32i	a6, sp, 632	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l32i	a5, sp, 636	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	extui	a2, a8, 0, 16	# _120, Atmp_QA,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	mull	a13, a4, a6	# tmp812, _97,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	mull	a6, a3, a5	# tmp820, _111,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	mull	a5, a4, a2	#, _97, _120
	srai	a8, a8, 16	# _118, Atmp_QA,
	s32i	a5, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l32i.n	a5, a9, 0	# MEM[base: _2593, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	mull	a2, a3, a2	# tmp827, _111, _120
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	add.n	a7, a7, a5	# tmp810, tmp809,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	mull	a4, a4, a8	# tmp825, _97, _118
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l32i.n	a5, a10, 0	# MEM[base: _2583, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	mull	a3, a3, a8	# tmp829, _111, _118
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	l32i	a8, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	srai	a2, a2, 16	# tmp828, tmp827,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	add.n	a12, a12, a5	# tmp818, tmp817,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	add.n	a3, a2, a3	# tmp830, tmp828, tmp829
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	srai	a5, a8, 16	# tmp824,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	l32i	a2, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	add.n	a4, a5, a4	# tmp826, tmp824, tmp825
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	add.n	a2, a2, a4	#,, tmp826
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	l32i	a4, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	srai	a13, a13, 16	# tmp813, tmp812,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	srai	a6, a6, 16	# tmp821, tmp820,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	add.n	a7, a7, a13	# tmp814, tmp810, tmp813
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	add.n	a6, a12, a6	# tmp822, tmp818, tmp821
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	add.n	a4, a4, a3	#,, tmp830
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:128:                 for( k = 0; k < n; k++ ) {
	l32i	a5, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:129:                     C_first_row[ k ] = silk_SMLAWB( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	s32i.n	a7, a9, 0	# MEM[base: _2593, offset: 0B], tmp814
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:130:                     C_last_row[ k ]  = silk_SMLAWB( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	s32i.n	a6, a10, 0	# MEM[base: _2583, offset: 0B], tmp822
	addi	a11, a11, -2	# ivtmp$84, ivtmp$84,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:132:                     tmp1 = silk_SMLAWB( tmp1, Atmp_QA, x_ptr[ n - k - 1 ]            );                 /* Q(QA-16) */
	s32i	a2, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:133:                     tmp2 = silk_SMLAWB( tmp2, Atmp_QA, x_ptr[ subfr_length - n + k ] );                 /* Q(QA-16) */
	s32i	a4, sp, 608	# %sfp,
	addi.n	a9, a9, 4	# ivtmp$83, ivtmp$83,
	addi.n	a10, a10, 4	# ivtmp$86, ivtmp$86,
	addi.n	a15, a15, 2	# ivtmp$87, ivtmp$87,
	addi.n	a14, a14, 4	# ivtmp$88, ivtmp$88,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:128:                 for( k = 0; k < n; k++ ) {
	bne	a5, a11, .L25	#, ivtmp$84,
.L24:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:135:                 tmp1 = silk_LSHIFT32( -tmp1, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	l32i	a6, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:136:                 tmp2 = silk_LSHIFT32( -tmp2, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	l32i	a7, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:135:                 tmp1 = silk_LSHIFT32( -tmp1, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	l32i	a8, sp, 676	# %sfp,
	neg	a10, a6	# tmp831,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:136:                 tmp2 = silk_LSHIFT32( -tmp2, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	neg	a9, a7	# tmp832,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:135:                 tmp1 = silk_LSHIFT32( -tmp1, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	ssl	a8	#
	sll	a10, a10	# _131, tmp831
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:136:                 tmp2 = silk_LSHIFT32( -tmp2, 32 - QA - rshifts );                                       /* Q(16-rshifts) */
	ssl	a8	#
	sll	a9, a9	# _134, tmp832
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	l32i	a11, sp, 652	# %sfp, ivtmp$78
	l32i	a6, sp, 656	# %sfp, ivtmp$76
	l32i	a15, sp, 620	# %sfp, ivtmp$97
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	srai	a13, a10, 16	# _136, _131,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	srai	a12, a9, 16	# _150, _134,
	extui	a10, a10, 0, 16	# _2625, _131,
	extui	a9, a9, 0, 16	# _2635, _134,
	addi	a8, sp, 100	# ivtmp$75,,
	mov.n	a7, sp	# ivtmp$77,
.L26:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	l16si	a3, a6, 0	# MEM[base: _2641, offset: 0B], _142
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	l16si	a2, a11, 0	# MEM[base: _2638, offset: 0B], _157
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	l32i.n	a5, a8, 0	# MEM[base: _2643, offset: 0B], MEM[base: _2643, offset: 0B]
	mull	a14, a13, a3	# tmp835, _136, _142
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	mull	a4, a12, a2	# tmp843, _150, _157
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	add.n	a5, a14, a5	# tmp836, tmp835, MEM[base: _2643, offset: 0B]
	mull	a3, a3, a10	# tmp838, _142, _2625
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	l32i.n	a14, a7, 0	# MEM[base: _2640, offset: 0B],
	mull	a2, a2, a9	# tmp846, _157, _2635
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	srai	a3, a3, 16	# tmp839, tmp838,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	add.n	a4, a4, a14	# tmp844, tmp843,
	srai	a2, a2, 16	# tmp847, tmp846,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	add.n	a5, a5, a3	# tmp840, tmp836, tmp839
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	add.n	a2, a4, a2	# tmp848, tmp844, tmp847
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:138:                     CAf[ k ] = silk_SMLAWB( CAf[ k ], tmp1, x_ptr[ n - k ]                    );        /* Q( -rshift ) */
	s32i.n	a5, a8, 0	# MEM[base: _2643, offset: 0B], tmp840
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:139:                     CAb[ k ] = silk_SMLAWB( CAb[ k ], tmp2, x_ptr[ subfr_length - n + k - 1 ] );        /* Q( -rshift ) */
	s32i.n	a2, a7, 0	# MEM[base: _2640, offset: 0B], tmp848
	addi	a6, a6, -2	# ivtmp$76, ivtmp$76,
	addi.n	a8, a8, 4	# ivtmp$75, ivtmp$75,
	addi.n	a7, a7, 4	# ivtmp$77, ivtmp$77,
	addi.n	a11, a11, 2	# ivtmp$78, ivtmp$78,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:137:                 for( k = 0; k <= n; k++ ) {
	bne	a15, a6, .L26	# ivtmp$97, ivtmp$76,
	l32i	a6, sp, 648	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a2, sp, 660	# %sfp,
	l32i	a3, sp, 656	# %sfp,
	l32i	a7, sp, 652	# %sfp,
	l32i	a8, sp, 620	# %sfp,
	addi.n	a2, a2, 1	#,,
	add.n	a3, a3, a6	#,,
	add.n	a7, a7, a6	#,,
	add.n	a8, a8, a6	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a9, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	s32i	a2, sp, 660	# %sfp,
	s32i	a3, sp, 656	# %sfp,
	s32i	a7, sp, 652	# %sfp,
	s32i	a8, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:122:             for( s = 0; s < nb_subfr; s++ ) {
	bne	a9, a2, .L27	#,,
	j	.L134		#
.L22:
	l32i	a14, sp, 664	# %sfp,
	l32i	a9, sp, 716	# %sfp,
	slli	a14, a14, 1	#,,
	add.n	a9, a14, a9	#,,
	s32i	a14, sp, 652	# %sfp,
	movi.n	a2, -1	# tmp849,
	l32i	a14, sp, 716	# %sfp,
	l32i	a6, sp, 668	# %sfp,
	xor	a2, a2, a8	#, tmp849,
	l32i	a8, sp, 716	# %sfp,
	add.n	a14, a14, a6	#,,
	s32i	a9, sp, 632	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	movi.n	a9, 0	#,
	s32i	a14, sp, 628	# %sfp,
	s32i	a2, sp, 656	# %sfp,
	addi	a14, a8, -2	# ivtmp$127,,
	s32i	a9, sp, 636	# %sfp,
.L31:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:145:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    -rshifts );            /* Q( -rshifts ) */
	l32i	a2, sp, 652	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:146:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], -rshifts );            /* Q( -rshifts ) */
	l32i	a6, sp, 668	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:145:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    -rshifts );            /* Q( -rshifts ) */
	add.n	a3, a14, a2	# tmp850, ivtmp$127,
	l16si	a10, a3, 2	# MEM[base: _2458, offset: 2B], _171
	l32i	a7, sp, 680	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:146:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], -rshifts );            /* Q( -rshifts ) */
	add.n	a2, a14, a6	# tmp853, ivtmp$127,
	l16si	a9, a2, 2	# MEM[base: _2455, offset: 2B], _181
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:145:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    -rshifts );            /* Q( -rshifts ) */
	ssl	a7	#
	sll	a7, a10	#, _171
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:146:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], -rshifts );            /* Q( -rshifts ) */
	l32i	a8, sp, 680	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:149:                 for( k = 0; k < n; k++ ) {
	l32i	a6, sp, 664	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:145:                 x1  = -silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    -rshifts );            /* Q( -rshifts ) */
	s32i	a7, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:146:                 x2  = -silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], -rshifts );            /* Q( -rshifts ) */
	ssl	a8	#
	sll	a15, a9	# _183, _181
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:147:                 tmp1 = silk_LSHIFT32( (opus_int32)x_ptr[ n ],                    17 );                  /* Q17 */
	slli	a10, a10, 17	# tmp1, _171,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:148:                 tmp2 = silk_LSHIFT32( (opus_int32)x_ptr[ subfr_length - n - 1 ], 17 );                  /* Q17 */
	slli	a9, a9, 17	# tmp2, _181,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:149:                 for( k = 0; k < n; k++ ) {
	beqz.n	a6, .L28	#,
	l32i	a7, sp, 632	# %sfp,
	l32i	a8, sp, 628	# %sfp,
	addi	a6, a7, -2	# ivtmp$114,,
	addi.n	a11, a8, 2	# ivtmp$117,,
	movi.n	a3, 0	# ivtmp$119,
	s32i	a14, sp, 604	# %sfp, ivtmp$127
.L29:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:152:                     Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 17 );                                   /* Q17 */
	movi	a14, 0x128	#,
	add.n	a14, a14, sp	#,,
	add.n	a2, a14, a3	# tmp872,, ivtmp$119
	l32i.n	a2, a2, 0	# MEM[base: _2486, offset: 0B], MEM[base: _2486, offset: 0B]
	movi	a7, 0x1e8	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l16si	a5, a6, 0	# MEM[base: _2490, offset: 0B], _192
	add.n	a7, a7, sp	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l32i	a14, sp, 612	# %sfp,
	movi	a8, 0x188	#,
	add.n	a13, a7, a3	# _2492,, ivtmp$119
	add.n	a8, a8, sp	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:152:                     Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 17 );                                   /* Q17 */
	srai	a2, a2, 7	# tmp873, MEM[base: _2486, offset: 0B],
	add.n	a12, a8, a3	# _2489,, ivtmp$119
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:151:                     C_last_row[ k ]  = silk_MLA( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l16si	a4, a11, 0	# MEM[base: _2487, offset: 0B], _201
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	mull	a8, a5, a14	# tmp860, _192,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:152:                     Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 17 );                                   /* Q17 */
	addi.n	a2, a2, 1	# tmp875, tmp873,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	l32i.n	a14, a13, 0	# MEM[base: _2492, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:152:                     Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 17 );                                   /* Q17 */
	srai	a2, a2, 1	# Atmp1$6_209, tmp875,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	sub	a8, a14, a8	# tmp861,, tmp860
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:156:                     tmp1 = silk_MLA_ovflw( tmp1, x_ptr[ n - k - 1 ],            Atmp1 );                      /* Q17 */
	mull	a5, a5, a2	# tmp876, _192, Atmp1$6_209
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:151:                     C_last_row[ k ]  = silk_MLA( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	l32i.n	a14, a12, 0	# MEM[base: _2489, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:157:                     tmp2 = silk_MLA_ovflw( tmp2, x_ptr[ subfr_length - n + k ], Atmp1 );                      /* Q17 */
	mull	a2, a4, a2	# tmp877, _201, Atmp1$6_209
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:151:                     C_last_row[ k ]  = silk_MLA( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	mull	a7, a4, a15	# tmp867, _201, _183
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:157:                     tmp2 = silk_MLA_ovflw( tmp2, x_ptr[ subfr_length - n + k ], Atmp1 );                      /* Q17 */
	add.n	a9, a2, a9	# tmp2, tmp877, tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:151:                     C_last_row[ k ]  = silk_MLA( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	sub	a7, a14, a7	# tmp868,, tmp867
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:149:                 for( k = 0; k < n; k++ ) {
	l32i	a2, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:150:                     C_first_row[ k ] = silk_MLA( C_first_row[ k ], x1, x_ptr[ n - k - 1 ]            ); /* Q( -rshifts ) */
	s32i.n	a8, a13, 0	# MEM[base: _2492, offset: 0B], tmp861
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:151:                     C_last_row[ k ]  = silk_MLA( C_last_row[ k ],  x2, x_ptr[ subfr_length - n + k ] ); /* Q( -rshifts ) */
	s32i.n	a7, a12, 0	# MEM[base: _2489, offset: 0B], tmp868
	addi	a6, a6, -2	# ivtmp$114, ivtmp$114,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:156:                     tmp1 = silk_MLA_ovflw( tmp1, x_ptr[ n - k - 1 ],            Atmp1 );                      /* Q17 */
	add.n	a10, a5, a10	# tmp1, tmp876, tmp1
	addi.n	a11, a11, 2	# ivtmp$117, ivtmp$117,
	addi.n	a3, a3, 4	# ivtmp$119, ivtmp$119,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:149:                 for( k = 0; k < n; k++ ) {
	bne	a2, a6, .L29	#, ivtmp$114,
	mov.n	a14, a2	# ivtmp$127,
.L28:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:160:                 tmp2 = -tmp2;                                                                           /* Q17 */
	neg	a9, a9	# tmp2, tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:159:                 tmp1 = -tmp1;                                                                           /* Q17 */
	neg	a10, a10	# tmp1, tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	srai	a15, a9, 16	# _242, tmp2,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	srai	a3, a10, 16	#, tmp1,
	extui	a4, a10, 0, 16	#, tmp1,
	extui	a5, a9, 0, 16	#, tmp2,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	s32i	a15, sp, 624	# %sfp, _242
	l32i	a13, sp, 628	# %sfp, ivtmp$108
	l32i	a8, sp, 632	# %sfp, ivtmp$106
	l32i	a15, sp, 656	# %sfp, _2653
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	s32i	a3, sp, 612	# %sfp,
	s32i	a4, sp, 616	# %sfp,
	s32i	a5, sp, 620	# %sfp,
	addi	a12, sp, 100	# ivtmp$105,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	mov.n	a11, sp	# ivtmp$107,
	s32i	a9, sp, 604	# %sfp, tmp2
.L30:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	l16si	a3, a8, 0	# MEM[base: _2525, offset: 0B], tmp878
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	l16si	a2, a13, 0	# MEM[base: _2522, offset: 0B], tmp893
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	ssl	a15	# _2653
	sll	a3, a3	# _226, tmp878
	slli	a5, a3, 16	# tmp881, _226,
	l32i	a6, sp, 612	# %sfp,
	l32i	a9, sp, 616	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	ssl	a15	# _2653
	sll	a2, a2	# _250, tmp893
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	srai	a5, a5, 16	# _228, tmp881,
	mull	a7, a6, a5	# tmp882,, _228
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	slli	a4, a2, 16	# tmp896, _250,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	mull	a5, a5, a9	# tmp885, _228,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	l32i	a9, sp, 624	# %sfp,
	srai	a4, a4, 16	# _252, tmp896,
	mull	a6, a9, a4	# tmp897,, _252
	l32i	a9, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	srai	a3, a3, 15	# tmp888, _226,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	mull	a4, a4, a9	# tmp900, _252,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	l32i.n	a9, a12, 0	# MEM[base: _2527, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	srai	a2, a2, 15	# tmp903, _250,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	add.n	a7, a7, a9	# tmp883, tmp882,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	l32i.n	a9, a11, 0	# MEM[base: _2524, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	addi.n	a3, a3, 1	# tmp889, tmp888,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	add.n	a6, a6, a9	# tmp898, tmp897,
	addi.n	a2, a2, 1	# tmp904, tmp903,
	l32i	a9, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	srai	a3, a3, 1	# tmp890, tmp889,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	srai	a2, a2, 1	# tmp905, tmp904,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	srai	a5, a5, 16	# tmp886, tmp885,
	mull	a3, a3, a10	# tmp891, tmp890, tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	srai	a4, a4, 16	# tmp901, tmp900,
	mull	a2, a2, a9	# tmp906, tmp905,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	add.n	a7, a7, a5	# tmp887, tmp883, tmp886
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	add.n	a6, a6, a4	# tmp902, tmp898, tmp901
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	add.n	a3, a7, a3	# tmp892, tmp887, tmp891
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	add.n	a2, a6, a2	# tmp907, tmp902, tmp906
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:162:                     CAf[ k ] = silk_SMLAWW( CAf[ k ], tmp1,
	s32i.n	a3, a12, 0	# MEM[base: _2527, offset: 0B], tmp892
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:164:                     CAb[ k ] = silk_SMLAWW( CAb[ k ], tmp2,
	s32i.n	a2, a11, 0	# MEM[base: _2524, offset: 0B], tmp907
	addi	a8, a8, -2	# ivtmp$106, ivtmp$106,
	addi.n	a12, a12, 4	# ivtmp$105, ivtmp$105,
	addi.n	a11, a11, 4	# ivtmp$107, ivtmp$107,
	addi.n	a13, a13, 2	# ivtmp$108, ivtmp$108,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:161:                 for( k = 0; k <= n; k++ ) {
	bne	a14, a8, .L30	# ivtmp$127, ivtmp$106,
	l32i	a6, sp, 648	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a2, sp, 636	# %sfp,
	l32i	a3, sp, 632	# %sfp,
	l32i	a7, sp, 628	# %sfp,
	addi.n	a2, a2, 1	#,,
	add.n	a3, a3, a6	#,,
	add.n	a7, a7, a6	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	s32i	a2, sp, 636	# %sfp,
	s32i	a3, sp, 632	# %sfp,
	s32i	a7, sp, 628	# %sfp,
	add.n	a14, a14, a6	# ivtmp$127, ivtmp$127,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:143:             for( s = 0; s < nb_subfr; s++ ) {
	bne	a8, a2, .L31	#,,
.L134:
	l32i.n	a2, sp, 0	# CAb, pretmp_2648
	l32i	a3, sp, 100	# CAf, pretmp_2649
.L23:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:171:         tmp1 = C_first_row[ n ];                                                                        /* Q( -rshifts ) */
	l32i	a9, sp, 700	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:172:         tmp2 = C_last_row[ n ];                                                                         /* Q( -rshifts ) */
	l32i	a14, sp, 696	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:171:         tmp1 = C_first_row[ n ];                                                                        /* Q( -rshifts ) */
	l32i.n	a9, a9, 0	# MEM[base: _2425, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:172:         tmp2 = C_last_row[ n ];                                                                         /* Q( -rshifts ) */
	l32i.n	a14, a14, 0	# MEM[base: _2424, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	l32i	a6, sp, 664	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:171:         tmp1 = C_first_row[ n ];                                                                        /* Q( -rshifts ) */
	s32i	a9, sp, 624	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:172:         tmp2 = C_last_row[ n ];                                                                         /* Q( -rshifts ) */
	s32i	a14, sp, 616	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:174:         nrg  = silk_ADD32( CAb[ 0 ], CAf[ 0 ] );                                                        /* Q( 1-rshifts ) */
	add.n	a7, a2, a3	# nrg, pretmp_2648, pretmp_2649
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	beqz.n	a6, .L90	#,
	l32i	a6, sp, 700	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:173:         num  = 0;                                                                                       /* Q( -rshifts ) */
	movi.n	a8, 0	#,
	l32i	a14, sp, 696	# %sfp,
	s32i	a8, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	l32i	a15, sp, 692	# %sfp, ivtmp$63
	addi	a8, a6, -4	# ivtmp$61,,
	l32i	a6, sp, 684	# %sfp, ivtmp$58
	addi	a9, a14, -4	# ivtmp$59,,
	addi	a14, sp, 100	#,,
	s32i	a14, sp, 604	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	s32i	a8, sp, 612	# %sfp, ivtmp$61
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	s32i	sp, sp, 608	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	mov.n	a8, a7	# nrg, nrg
	mov.n	a14, a15	# ivtmp$63, ivtmp$63
	mov.n	a7, a6	# ivtmp$58, ivtmp$58
.L35:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:176:             Atmp_QA = Af_QA[ k ];
	l32i.n	a6, a7, 0	# MEM[base: _2681, offset: 0B], Atmp_QA
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:177:             lz = silk_CLZ32( silk_abs( Atmp_QA ) ) - 1;
	abs	a2, a6	# tmp908, Atmp_QA
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a2	# iftmp$15_2833, tmp908
	addi.n	a2, a2, -1	# _473, iftmp$15_2833,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a6, .L91	# Atmp_QA,
	blti	a2, 8, .L34	# _473,,
	movi.n	a2, 7	# _473,
.L34:
	movi.n	a3, 7	#,
	sub	a12, a3, a2	# _613,, _473
	j	.L33		#
.L91:
	movi.n	a12, 0	# _613,
	movi.n	a2, 7	# _473,
.L33:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i.n	a3, a9, 0	# MEM[base: _2680, offset: 0B], MEM[base: _2680, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:179:             Atmp1 = silk_LSHIFT32( Atmp_QA, lz );                                                       /* Q( QA + lz ) */
	ssl	a2	# _473
	sll	a15, a6	# Atmp1, Atmp_QA
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	srai	a13, a15, 31	# tmp913, Atmp1,
	mov.n	a4, a15	#, Atmp1
	mov.n	a5, a13	#, tmp913
	mov.n	a2, a3	#, MEM[base: _2680, offset: 0B]
	srai	a3, a3, 31	#, MEM[base: _2680, offset: 0B],
	s32i	a7, sp, 756	#,
	s32i	a8, sp, 772	#,
	s32i	a9, sp, 776	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i	a6, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	ssl	a12	# _613
	sll	a11, a3	# tmp919,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i.n	a10, a6, 0	# MEM[base: _2679, offset: 0B], MEM[base: _2679, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i	a6, sp, 624	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	mov.n	a4, a15	#, Atmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	add.n	a6, a6, a11	#,, tmp919
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	mov.n	a5, a13	#, tmp913
	mov.n	a2, a10	#, MEM[base: _2679, offset: 0B]
	srai	a3, a10, 31	#, MEM[base: _2679, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:181:             tmp1 = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( C_last_row[  n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	s32i	a6, sp, 624	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i.n	a10, a14, 0	# MEM[base: _2678, offset: 0B], MEM[base: _2678, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i	a6, sp, 616	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	ssl	a12	# _613
	sll	a11, a3	# tmp925,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	add.n	a6, a6, a11	#,, tmp925
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	mov.n	a4, a15	#, Atmp1
	mov.n	a5, a13	#, tmp913
	mov.n	a2, a10	#, MEM[base: _2678, offset: 0B]
	srai	a3, a10, 31	#, MEM[base: _2678, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:182:             tmp2 = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( C_first_row[ n - k - 1 ], Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	s32i	a6, sp, 616	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	l32i	a6, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	ssl	a12	# _613
	sll	a10, a3	# tmp931,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	l32i.n	a2, a6, 4	# MEM[base: _2676, offset: 4B], MEM[base: _2676, offset: 4B]
	l32i	a6, sp, 608	# %sfp,
	mov.n	a5, a13	#, tmp913
	l32i.n	a4, a6, 4	# MEM[base: _2677, offset: 4B], MEM[base: _2677, offset: 4B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	l32i	a6, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	add.n	a3, a2, a4	# tmp932, MEM[base: _2676, offset: 4B], MEM[base: _2677, offset: 4B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	add.n	a6, a6, a10	#,, tmp931
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	mov.n	a2, a3	#, tmp932
	mov.n	a4, a15	#, Atmp1
	srai	a3, a3, 31	#, tmp932,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:183:             num  = silk_ADD_LSHIFT32( num,  silk_SMMUL( CAb[ n - k ],             Atmp1 ), 32 - QA - lz );  /* Q( -rshifts ) */
	s32i	a6, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	call0	__muldi3		#
	l32i	a6, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	l32i	a8, sp, 772	#,
	addi	a6, a6, -4	#,,
	s32i	a6, sp, 612	# %sfp,
	l32i	a6, sp, 608	# %sfp,
	l32i	a7, sp, 756	#,
	addi.n	a6, a6, 4	#,,
	s32i	a6, sp, 608	# %sfp,
	l32i	a6, sp, 604	# %sfp,
	l32i	a9, sp, 776	#,
	addi.n	a6, a6, 4	#,,
	s32i	a6, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	l32i	a6, sp, 596	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	ssl	a12	# _613
	sll	a3, a3	# tmp939,
	addi	a14, a14, -4	# ivtmp$63, ivtmp$63,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:184:             nrg  = silk_ADD_LSHIFT32( nrg,  silk_SMMUL( silk_ADD32( CAb[ k + 1 ], CAf[ k + 1 ] ),
	add.n	a8, a8, a3	# nrg, nrg, tmp939
	addi.n	a7, a7, 4	# ivtmp$58, ivtmp$58,
	addi	a9, a9, -4	# ivtmp$59, ivtmp$59,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:175:         for( k = 0; k < n; k++ ) {
	bne	a6, a14, .L35	#, ivtmp$63,
	mov.n	a7, a8	# nrg, nrg
	l32i	a14, sp, 616	# %sfp,
	l32i	a8, sp, 620	# %sfp,
	add.n	a9, a8, a14	# _2115,,
	j	.L32		#
.L90:
	mov.n	a9, a14	# _2115,
.L32:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	l32i	a6, sp, 664	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	addi	a14, sp, 100	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	addi.n	a6, a6, 1	#,,
	slli	a8, a6, 2	#,,
	s32i	a6, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	l32i	a6, sp, 624	# %sfp,
	add.n	a2, a14, a8	# tmp941,,
	s32i	a8, sp, 612	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:188:         CAb[ n + 1 ] = tmp2;                                                                            /* Q( -rshifts ) */
	l32i	a14, sp, 616	# %sfp,
	l32i	a8, sp, 692	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:190:         num = silk_LSHIFT32( -num, 1 );                                                                 /* Q( 1-rshifts ) */
	neg	a9, a9	# tmp942, _2115
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	s32i.n	a6, a2, 0	# MEM[base: _2429, offset: 0B],
	l32i	a6, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:188:         CAb[ n + 1 ] = tmp2;                                                                            /* Q( -rshifts ) */
	s32i.n	a14, a8, 4	# MEM[base: _2428, offset: 4B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:190:         num = silk_LSHIFT32( -num, 1 );                                                                 /* Q( 1-rshifts ) */
	slli	a9, a9, 1	# num, tmp942,
	l32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:193:         if( silk_abs( num ) < nrg ) {
	abs	a14, a9	# _309, num
	s32i	a6, sp, 624	# %sfp,
	srai	a10, a8, 31	# _2881,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:193:         if( silk_abs( num ) < nrg ) {
	bge	a14, a7, .L36	# _309, nrg,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a9, .L92	# num,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a14, a14	# iftmp$15_661, _309
	addi.n	a12, a14, -1	# tmp944, iftmp$15_661,
	ssl	a12	# tmp944
	sll	a12, a9	# _2384, num
	addi	a11, a14, -2	# _2380, iftmp$15_661,
	srai	a4, a12, 16	# _2388, _2384,
	extui	a13, a12, 0, 16	# _2390, _2384,
	j	.L37		#
.L92:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	mov.n	a13, a9	# _2390, num
	mov.n	a4, a9	# _2388, num
	mov.n	a12, a9	# _2384, num
	movi.n	a11, 0x1e	# _2380,
	movi.n	a14, 0x20	# iftmp$15_661,
.L37:
	beqz.n	a7, .L93	# nrg,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a6, a7	# tmp945, nrg
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a6, a6	# iftmp$15_669, tmp945
	addi.n	a8, a6, -1	# _2426, iftmp$15_669,
	j	.L38		#
.L93:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a8, 0x1f	# _2426,
	movi.n	a6, 0x20	# iftmp$15_669,
.L38:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a8	# _2426
	sll	a8, a7	# b32_nrm, nrg
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC10	#,
	srai	a3, a8, 16	#, b32_nrm,
	s32i	a6, sp, 768	#,
	s32i	a9, sp, 776	#,
	s32i	a10, sp, 764	#,
	s32i	a11, sp, 760	#,
	s32i	a4, sp, 756	#,
	s32i	a8, sp, 772	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp951,,
	srai	a15, a2, 16	# _679, tmp951,
	l32i	a4, sp, 756	#,
	mull	a13, a15, a13	# tmp952, _679, _2390
	mull	a4, a15, a4	# tmp954, _679, _2388
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a8, sp, 772	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a13, a13, 16	# tmp953, tmp952,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a13, a13, a4	# result, tmp953, tmp954
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a13	#, result
	srai	a5, a13, 31	#, result,
	mov.n	a2, a8	#, b32_nrm
	srai	a3, a8, 31	#, b32_nrm,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp961,,
	sub	a12, a12, a3	# a32_nrm, _2384, tmp961
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	extui	a2, a12, 0, 16	# tmp964, a32_nrm,
	srai	a3, a12, 16	# tmp962, a32_nrm,
	mull	a12, a3, a15	# tmp963, tmp962, _679
	mull	a2, a2, a15	# tmp965, tmp964, _679
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a6, sp, 768	#,
	l32i	a11, sp, 760	#,
	add.n	a12, a12, a13	# _456, tmp963, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a2, a2, 16	# tmp966, tmp965,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a7, a11, a6	# lshift, _2380, iftmp$15_669
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a12, a2, a12	# result, tmp966, _456
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a9, sp, 776	#,
	l32i	a10, sp, 764	#,
	bgez	a7, .L39	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a2, a6, a14	# tmp968, iftmp$15_669, iftmp$15_661
	l32r	a3, .LC4	#, tmp969
	l32r	a14, .LC2	#,
	addi.n	a2, a2, 2	# _705, tmp968,
	ssr	a2	# _705
	sra	a3, a3	# _706, tmp969
	ssr	a2	# _705
	sra	a4, a14	# _707,
	bge	a4, a3, .L40	# _707, _706,
	bge	a3, a12, .L41	# _706, result,
	j	.L135		#
.L41:
	bge	a12, a4, .L42	# iftmp$21_708, _707,
	j	.L136		#
.L40:
	bge	a4, a12, .L44	# _707, result,
.L136:
	mov.n	a12, a4	# iftmp$21_708, _707
	j	.L42		#
.L44:
	bge	a12, a3, .L42	# iftmp$21_708, _706,
.L135:
	mov.n	a12, a3	# iftmp$21_708, _706
.L42:
	ssl	a2	# _705
	sll	a12, a12	# rc_Q31, iftmp$21_708
	srai	a2, a12, 31	#, rc_Q31,
	s32i	a2, sp, 644	# %sfp,
	s32i	a12, sp, 640	# %sfp, rc_Q31
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
	mov.n	a2, a4	#,
	mov.n	a3, a5	#,
	s32i	a9, sp, 776	#,
	s32i	a10, sp, 764	#,
	call0	__muldi3		#
	l32r	a4, .LC0	#,
	sub	a3, a4, a3	# tmp974,,
	j	.L137		#
.L39:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a7	# lshift
	sra	a12, a12	# rc_Q31, result
	srai	a5, a12, 31	#, rc_Q31,
	s32i	a12, sp, 640	# %sfp, rc_Q31
	s32i	a5, sp, 644	# %sfp,
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
	mov.n	a2, a4	#,
	mov.n	a3, a5	#,
	s32i	a9, sp, 776	#,
	s32i	a10, sp, 764	#,
	call0	__muldi3		#
	l32r	a6, .LC0	#,
	sub	a3, a6, a3	# tmp983,,
.L137:
	l32i	a10, sp, 764	#,
	l32i	a4, sp, 708	# %sfp,
	mov.n	a2, a3	#, tmp983
	mov.n	a5, a10	#, _2881
	srai	a3, a3, 31	#, tmp983,
	call0	__muldi3		#
	slli	a3, a3, 2	# _2159,,
	l32i	a9, sp, 776	#,
	j	.L46		#
.L36:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:196:             rc_Q31 = ( num > 0 ) ? silk_int32_MAX : silk_int32_MIN;
	blti	a9, 1, .L94	# num,,
	l32r	a4, .LC1	#,
	l32r	a5, .LC1+4	#,
	slli	a3, a10, 2	# _2159, _2881,
	s32i	a4, sp, 640	# %sfp,
	s32i	a5, sp, 644	# %sfp,
	l32r	a12, .LC2	#, rc_Q31
	j	.L46		#
.L94:
	l32r	a6, .LC3	#,
	l32r	a7, .LC3+4	#,
	l32r	a12, .LC4	#, rc_Q31
	movi.n	a3, 0	# _2159,
	s32i	a6, sp, 640	# %sfp,
	s32i	a7, sp, 644	# %sfp,
.L46:
	l32i	a7, sp, 608	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:202:         if( tmp1 <= minInvGain_Q30 ) {
	l32i	a8, sp, 720	# %sfp,
	srai	a7, a7, 1	#,,
	s32i	a7, sp, 604	# %sfp,
	blt	a8, a3, .L47	#, _2159,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a14, sp, 732	# %sfp,
	movi.n	a15, 0x1f	# tmp1342,
	l32i	a13, sp, 728	# %sfp, iftmp$15_747
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	l32i	a6, sp, 708	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movnez	a15, a14, a8	# _2245,,
	movi.n	a2, 0x20	# tmp1341,
	moveqz	a13, a2, a8	# iftmp$15_747, tmp1341,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a15	# _2245
	sll	a12, a8	# _751,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a6, .L96	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:112:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a8, a6	# tmp991,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a8, a8	# iftmp$15_755, tmp991
	addi.n	a7, a8, -1	# _2283, iftmp$15_755,
	mov.n	a14, a6	#,
	j	.L49		#
.L96:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a7, 0x1f	# _2283,
	movi.n	a8, 0x20	# iftmp$15_755,
	mov.n	a14, a6	#,
.L49:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:113:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                  */
	ssl	a7	# _2283
	sll	a7, a14	# b32_nrm,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:116:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm        */
	l32r	a2, .LC10	#,
	srai	a3, a7, 16	#, b32_nrm,
	s32i	a8, sp, 772	#,
	s32i	a9, sp, 776	#,
	s32i	a7, sp, 756	#,
	call0	__divsi3		#
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	slli	a2, a2, 16	# tmp997,,
	srai	a6, a2, 16	# _765, tmp997,
	extui	a14, a12, 0, 16	# tmp998, _751,
	mull	a14, a14, a6	# tmp999, tmp998, _765
	srai	a2, a12, 16	# tmp1001, _751,
	mull	a2, a2, a6	# tmp1002, tmp1001, _765
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	l32i	a7, sp, 756	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	srai	a14, a14, 16	# tmp1000, tmp999,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a14, a14, a2	# result, tmp1000, tmp1002
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a14	#, result
	srai	a5, a14, 31	#, result,
	mov.n	a2, a7	#, b32_nrm
	srai	a3, a7, 31	#, b32_nrm,
	s32i	a6, sp, 768	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp1009,,
	sub	a12, a12, a3	# a32_nrm, _751, tmp1009
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	l32i	a6, sp, 768	#,
	srai	a3, a12, 16	# tmp1010, a32_nrm,
	extui	a2, a12, 0, 16	# tmp1012, a32_nrm,
	mull	a3, a3, a6	# tmp1011, tmp1010, _765
	mull	a2, a2, a6	# tmp1013, tmp1012, _765
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a8, sp, 772	#,
	add.n	a14, a3, a14	# _502, tmp1011, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a2, a2, 16	# tmp1014, tmp1013,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a2, a2, a14	# result, tmp1014, _502
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a15, a15, a8	# lshift, _2245, iftmp$15_755
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a15	# lshift
	sra	a3, a2	# _803, result
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	l32i	a9, sp, 776	#,
	bgez	a15, .L57	# lshift,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	sub	a3, a8, a13	# tmp1016, iftmp$15_755, iftmp$15_747
	l32r	a4, .LC4	#, tmp1017
	l32r	a6, .LC2	#,
	addi.n	a3, a3, 1	# _791, tmp1016,
	ssr	a3	# _791
	sra	a4, a4	# _792, tmp1017
	ssr	a3	# _791
	sra	a5, a6	# _793,
	bge	a5, a4, .L51	# _793, _792,
	bge	a4, a2, .L52	# _792, result,
	j	.L138		#
.L52:
	bge	a2, a5, .L53	# iftmp$21_794, _793,
	j	.L139		#
.L51:
	bge	a5, a2, .L55	# _793, result,
.L139:
	mov.n	a2, a5	# iftmp$21_794, _793
	j	.L53		#
.L55:
	bge	a2, a4, .L53	# iftmp$21_794, _792,
.L138:
	mov.n	a2, a4	# iftmp$21_794, _792
.L53:
	ssl	a3	# _791
	sll	a3, a2	# _803, iftmp$21_794
.L57:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:204:             tmp2 = ( (opus_int32)1 << 30 ) - silk_DIV32_varQ( minInvGain_Q30, invGain_Q30, 30 );            /* Q30 */
	l32r	a7, .LC0	#,
	sub	a2, a7, a3	# tmp2,, _803
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:75:     if( x <= 0 ) {
	blti	a2, 1, .L58	# tmp2,,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a12, a2	# iftmp$15_720, tmp2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	movi.n	a3, 0x18	# tmp1020,
	sub	a3, a3, a12	# _721, tmp1020, iftmp$15_720
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:403:     if( rot == 0 ) {
	beqz.n	a3, .L59	# _721,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:408:         return (opus_int32) ((x << (32 - r)) | (x >> r));
	ssr	a3	# _721
	src	a4, a2, a2	# _729, tmp2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:405:     } else if( rot < 0 ) {
	bgez	a3, .L61	# _721,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:402:     opus_uint32 m = (opus_uint32) -rot;
	addi	a4, a12, -24	# m, iftmp$15_720,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:406:         return (opus_int32) ((x << m) | (x >> (32 - m)));
	ssl	a4	# m
	src	a4, a2, a2	# _729, tmp2
.L61:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a6, .LC8	#, tmp1299
	l32r	a3, .LC7	#, tmp1300
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:81:     if( lz & 1 ) {
	extui	a5, a12, 0, 1	# tmp1022, iftmp$15_720,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	moveqz	a3, a6, a5	# tmp1300, tmp1299, tmp1022
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a4, a4, 0, 7	# _475, _729,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	mov.n	a5, a3	# y, tmp1300
	j	.L62		#
.L82:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:212:                     rc_Q31 = -rc_Q31;
	neg	a2, a2	# rc_Q31, _324
	srai	a8, a2, 6	#, rc_Q31,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a9, sp, 604	# %sfp,
	s32i	a8, sp, 616	# %sfp,
	bnez.n	a9, .L64	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	l32i	a14, sp, 664	# %sfp,
	addmi	a3, sp, 0x100	#,,
	slli	a2, a14, 2	# tmp1024,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	movi.n	a6, 1	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	add.n	a2, a3, a2	# tmp1025,, tmp1024
	s32i.n	a8, a2, 40	# Af_QA,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	s32i	a6, sp, 608	# %sfp,
	mov.n	a8, a6	#,
	j	.L65		#
.L47:
	mov.n	a8, a7	#,
	srai	a12, a12, 6	#, rc_Q31,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	movi.n	a7, 0	#,
	s32i	a12, sp, 616	# %sfp,
	s32i	a3, sp, 708	# %sfp, _2159
	s32i	a7, sp, 620	# %sfp,
	bne	a8, a7, .L66	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	l32i	a9, sp, 704	# %sfp,
	s32i.n	a12, a9, 0	# MEM[base: _2434, offset: 0B],
	j	.L67		#
.L58:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a14, sp, 604	# %sfp,
	bnez.n	a14, .L99	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	l32i	a6, sp, 664	# %sfp,
	addmi	a7, sp, 0x100	#,,
	slli	a2, a6, 2	# tmp1028,,
	add.n	a2, a7, a2	# tmp1029,, tmp1028
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	movi.n	a8, 1	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	s32i.n	a14, a2, 40	# Af_QA,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	s32i	a8, sp, 608	# %sfp,
	j	.L65		#
.L64:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a9, sp, 720	# %sfp,
	s32i	a2, sp, 640	# %sfp, rc_Q31
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	movi.n	a14, 1	#,
	srai	a2, a2, 31	#, rc_Q31,
	s32i	a2, sp, 644	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	s32i	a9, sp, 708	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	s32i	a14, sp, 620	# %sfp,
	j	.L66		#
.L99:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a8, sp, 720	# %sfp,
	l32r	a2, .LC5	#,
	l32r	a3, .LC5+4	#,
	movi.n	a9, 0	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	movi.n	a6, 1	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	s32i	a8, sp, 708	# %sfp,
	s32i	a9, sp, 616	# %sfp,
	s32i	a2, sp, 640	# %sfp,
	s32i	a3, sp, 644	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	s32i	a6, sp, 620	# %sfp,
.L66:
	l32i	a7, sp, 704	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	movi.n	a12, 0	# k,
	addi	a14, a7, -4	# ivtmp$54,,
	mov.n	a2, a14	# ivtmp$54, ivtmp$54
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	l32i	a15, sp, 684	# %sfp, ivtmp$53
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	mov.n	a14, a12	# k, k
	mov.n	a12, a2	# ivtmp$54, ivtmp$54
.L68:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:224:             tmp2 = Af_QA[ n - k - 1 ];                                                          /* QA */
	l32i.n	a13, a12, 0	# MEM[base: _2712, offset: 0B], tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:225:             Af_QA[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );      /* QA */
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
	mov.n	a2, a13	#, tmp2
	srai	a3, a13, 31	#, tmp2,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:223:             tmp1 = Af_QA[ k ];                                                                  /* QA */
	l32i.n	a10, a15, 0	# MEM[base: _2721, offset: 0B], tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:225:             Af_QA[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );      /* QA */
	slli	a3, a3, 1	# tmp1037,,
	add.n	a8, a3, a10	# tmp1038, tmp1037, tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:226:             Af_QA[ n - k - 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );      /* QA */
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:225:             Af_QA[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );      /* QA */
	s32i.n	a8, a15, 0	# MEM[base: _2721, offset: 0B], tmp1038
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:226:             Af_QA[ n - k - 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );      /* QA */
	mov.n	a2, a10	#, tmp1
	srai	a3, a10, 31	#, tmp1,
	call0	__muldi3		#
	slli	a3, a3, 1	# tmp1043,,
	add.n	a3, a3, a13	# tmp1044, tmp1043, tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a8, sp, 604	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:226:             Af_QA[ n - k - 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );      /* QA */
	s32i.n	a3, a12, 0	# MEM[base: _2712, offset: 0B], tmp1044
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	addi.n	a14, a14, 1	# k, k,
	addi.n	a15, a15, 4	# ivtmp$53, ivtmp$53,
	addi	a12, a12, -4	# ivtmp$54, ivtmp$54,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	blt	a14, a8, .L68	# k,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	l32i	a14, sp, 616	# %sfp,
	l32i	a9, sp, 704	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:230:         if( reached_max_gain ) {
	l32i	a6, sp, 620	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	s32i.n	a14, a9, 0	# MEM[base: _2433, offset: 0B],
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:230:         if( reached_max_gain ) {
	beqz.n	a6, .L67	#,
	l32i	a7, sp, 708	# %sfp,
	l32i	a8, sp, 608	# %sfp,
	s32i	a7, sp, 720	# %sfp,
.L65:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:232:             for( k = n + 1; k < D; k++ ) {
	l32i	a9, sp, 820	# D,
	blt	a8, a9, .L69	#,,
.L71:
	l32i	a14, sp, 820	# D,
	l32i	a9, sp, 752	# %sfp, ivtmp$37
	slli	a3, a14, 2	# tmp1045,,
	add.n	a3, a9, a3	# _273, ivtmp$37, tmp1045
	l32i	a4, sp, 684	# %sfp, ivtmp$41
	j	.L70		#
.L69:
	mov.n	a8, a9	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:233:                 Af_QA[ k ] = 0;
	l32i	a9, sp, 624	# %sfp,
	l32i	a6, sp, 612	# %sfp,
	movi	a14, 0x128	#,
	sub	a4, a8, a9	# tmp1046,,
	add.n	a14, a14, sp	#,,
	slli	a4, a4, 2	#, tmp1046,
	movi.n	a3, 0	#,
	add.n	a2, a14, a6	#,,
	call0	memset		#
	j	.L71		#
.L67:
	l32i	a7, sp, 692	# %sfp,
	addi	a13, sp, 100	# ivtmp$48,,
	addi.n	a7, a7, 4	#,,
	s32i	a7, sp, 692	# %sfp,
	mov.n	a15, a13	# ivtmp$48, ivtmp$48
	mov.n	a14, a7	# ivtmp$49, ivtmp$49
	j	.L72		#
.L100:
	mov.n	a14, a2	# ivtmp$49, ivtmp$49
.L72:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:241:             tmp2 = CAb[ n - k + 1 ];                                                            /* Q( -rshifts ) */
	l32i.n	a12, a14, 0	# MEM[base: _301, offset: 0B], tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:242:             CAf[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
	mov.n	a2, a12	#, tmp2
	srai	a3, a12, 31	#, tmp2,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:240:             tmp1 = CAf[ k ];                                                                    /* Q( -rshifts ) */
	l32i.n	a8, a15, 0	# MEM[base: _299, offset: 0B], tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:242:             CAf[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	slli	a3, a3, 1	# tmp1058,,
	add.n	a7, a3, a8	# tmp1059, tmp1058, tmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:243:             CAb[ n - k + 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	l32i	a4, sp, 640	# %sfp,
	l32i	a5, sp, 644	# %sfp,
	mov.n	a2, a8	#, tmp1
	srai	a3, a8, 31	#, tmp1,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:242:             CAf[ k ]         = silk_ADD_LSHIFT32( tmp1, silk_SMMUL( tmp2, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	s32i.n	a7, a15, 0	# MEM[base: _299, offset: 0B], tmp1059
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:243:             CAb[ n - k + 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	call0	__muldi3		#
	slli	a3, a3, 1	# tmp1064,,
	add.n	a3, a3, a12	# tmp1065, tmp1064, tmp2
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:239:         for( k = 0; k <= n + 1; k++ ) {
	l32i	a8, sp, 596	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:243:             CAb[ n - k + 1 ] = silk_ADD_LSHIFT32( tmp2, silk_SMMUL( tmp1, rc_Q31 ), 1 );        /* Q( -rshifts ) */
	s32i.n	a3, a14, 0	# MEM[base: _301, offset: 0B], tmp1065
	addi	a2, a14, -4	# ivtmp$49, ivtmp$49,
	addi.n	a15, a15, 4	# ivtmp$48, ivtmp$48,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:239:         for( k = 0; k <= n + 1; k++ ) {
	bne	a14, a8, .L100	# ivtmp$49,,
	l32i	a9, sp, 704	# %sfp,
	l32i	a14, sp, 700	# %sfp,
	l32i	a6, sp, 696	# %sfp,
	l32i	a7, sp, 668	# %sfp,
	addi.n	a9, a9, 4	#,,
	s32i	a9, sp, 704	# %sfp,
	addi.n	a14, a14, 4	#,,
	addi.n	a6, a6, 4	#,,
	addi	a7, a7, -2	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	l32i	a8, sp, 608	# %sfp,
	l32i	a9, sp, 820	# D,
	s32i	a14, sp, 700	# %sfp,
	s32i	a6, sp, 696	# %sfp,
	s32i	a7, sp, 668	# %sfp,
	l32i	a3, sp, 100	# CAf, pretmp_2649
	beq	a8, a9, .L73	#,,
	l32i.n	a2, sp, 0	# CAb, pretmp_2648
	s32i	a8, sp, 664	# %sfp,
	j	.L74		#
.L70:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:250:             A_Q16[ k ] = -silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );
	l32i.n	a2, a4, 0	# MEM[base: _269, offset: 0B], MEM[base: _269, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$41, ivtmp$41,
	srai	a2, a2, 8	# tmp1066, MEM[base: _269, offset: 0B],
	addi.n	a2, a2, 1	# tmp1068, tmp1066,
	srai	a2, a2, 1	# tmp1069, tmp1068,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:250:             A_Q16[ k ] = -silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );
	neg	a2, a2	# tmp1070, tmp1069
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:250:             A_Q16[ k ] = -silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );
	s32i.n	a2, a9, 0	# MEM[base: _586, offset: 0B], tmp1070
	addi.n	a9, a9, 4	# ivtmp$37, ivtmp$37,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:248:         for( k = 0; k < D; k++ ) {
	bne	a3, a9, .L70	# _273, ivtmp$37,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:253:         if( rshifts > 0 ) {
	l32i	a14, sp, 712	# %sfp,
	bgei	a14, 1, .L75	#,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:259:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
	l32i	a12, sp, 716	# %sfp, ivtmp$33
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:259:             for( s = 0; s < nb_subfr; s++ ) {
	movi.n	a13, 0	# s,
	mov.n	a15, a8	# nb_subfr,
	l32i	a14, sp, 724	# %sfp, C0
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:259:             for( s = 0; s < nb_subfr; s++ ) {
	bgei	a8, 1, .L79	#,,
	j	.L77		#
.L75:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:254:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a9, sp, 816	# nb_subfr,
	blti	a9, 1, .L77	#,,
	mov.n	a8, a14	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:256:                 C0 -= (opus_int32)silk_RSHIFT64( silk_inner_prod16( x_ptr, x_ptr, D, arch ), rshifts );
	movi.n	a13, 0x20	# tmp1072,
	l32i	a14, sp, 716	# %sfp, ivtmp$29
	and	a13, a8, a13	# tmp1073,, tmp1072
	movi.n	a12, -1	# tmp1076,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:254:             for( s = 0; s < nb_subfr; s++ ) {
	movi.n	a15, 0	# s,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:256:                 C0 -= (opus_int32)silk_RSHIFT64( silk_inner_prod16( x_ptr, x_ptr, D, arch ), rshifts );
	xor	a12, a8, a12	# tmp1077,, tmp1076
	mov.n	a2, a14	# ivtmp$29, ivtmp$29
	s32i	a13, sp, 604	# %sfp, tmp1073
	l32i	a13, sp, 724	# %sfp, C0
	mov.n	a14, a15	# s, s
	s32i	a12, sp, 608	# %sfp, tmp1077
	mov.n	a15, a2	# ivtmp$29, ivtmp$29
	mov.n	a12, a8	# rshifts,
.L78:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:256:                 C0 -= (opus_int32)silk_RSHIFT64( silk_inner_prod16( x_ptr, x_ptr, D, arch ), rshifts );
	l32i	a4, sp, 820	# D,
	mov.n	a3, a15	#, ivtmp$29
	mov.n	a2, a15	#, ivtmp$29
	call0	silk_inner_prod16_c		#
	l32i	a9, sp, 608	# %sfp,
	slli	a4, a3, 1	# tmp1075, _372,
	ssl	a9	#
	sll	a4, a4	# tmp1078, tmp1075
	ssr	a12	# rshifts
	srl	a2, a2	# tmp1267,
	l32i	a5, sp, 604	# %sfp,
	or	a2, a4, a2	# tmp1267, tmp1078, tmp1267
	ssr	a12	# rshifts
	sra	a3, a3	# tmp1268, _372
	l32i	a6, sp, 648	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:254:             for( s = 0; s < nb_subfr; s++ ) {
	l32i	a8, sp, 816	# nb_subfr,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:256:                 C0 -= (opus_int32)silk_RSHIFT64( silk_inner_prod16( x_ptr, x_ptr, D, arch ), rshifts );
	movnez	a2, a3, a5	# tmp1267, tmp1268,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:254:             for( s = 0; s < nb_subfr; s++ ) {
	addi.n	a14, a14, 1	# s, s,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:256:                 C0 -= (opus_int32)silk_RSHIFT64( silk_inner_prod16( x_ptr, x_ptr, D, arch ), rshifts );
	sub	a13, a13, a2	# C0, C0, tmp1267
	add.n	a15, a15, a6	# ivtmp$29, ivtmp$29,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:254:             for( s = 0; s < nb_subfr; s++ ) {
	bne	a8, a14, .L78	#, s,
	srai	a9, a13, 31	#, C0,
	s32i	a13, sp, 724	# %sfp, C0
	s32i	a9, sp, 740	# %sfp,
	j	.L77		#
.L79:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:261:                 C0 -= silk_LSHIFT32( silk_inner_prod_aligned( x_ptr, x_ptr, D, arch), -rshifts);
	l32i	a5, sp, 824	# arch,
	l32i	a4, sp, 820	# D,
	mov.n	a3, a12	#, ivtmp$33
	mov.n	a2, a12	#, ivtmp$33
	call0	silk_inner_prod_aligned		#
	l32i	a8, sp, 680	# %sfp,
	l32i	a9, sp, 648	# %sfp,
	ssl	a8	#
	sll	a2, a2	# tmp1079,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:259:             for( s = 0; s < nb_subfr; s++ ) {
	addi.n	a13, a13, 1	# s, s,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:261:                 C0 -= silk_LSHIFT32( silk_inner_prod_aligned( x_ptr, x_ptr, D, arch), -rshifts);
	sub	a14, a14, a2	# C0, C0, tmp1079
	add.n	a12, a12, a9	# ivtmp$33, ivtmp$33,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:259:             for( s = 0; s < nb_subfr; s++ ) {
	bne	a15, a13, .L79	# nb_subfr, s,
	s32i	a14, sp, 724	# %sfp, C0
	srai	a14, a14, 31	#, C0,
	s32i	a14, sp, 740	# %sfp,
.L77:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:265:         *res_nrg = silk_LSHIFT( silk_SMMUL( invGain_Q30, C0 ), 2 );
	l32i	a2, sp, 720	# %sfp,
	l32i	a4, sp, 724	# %sfp,
	l32i	a5, sp, 740	# %sfp,
	srai	a3, a2, 31	#,,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:265:         *res_nrg = silk_LSHIFT( silk_SMMUL( invGain_Q30, C0 ), 2 );
	l32i	a8, sp, 744	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:265:         *res_nrg = silk_LSHIFT( silk_SMMUL( invGain_Q30, C0 ), 2 );
	slli	a3, a3, 2	# tmp1086,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:266:         *res_nrg_Q = -rshifts;
	l32i	a14, sp, 680	# %sfp,
	l32i	a9, sp, 748	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:265:         *res_nrg = silk_LSHIFT( silk_SMMUL( invGain_Q30, C0 ), 2 );
	s32i.n	a3, a8, 0	# *res_nrg_633(D), tmp1086
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:266:         *res_nrg_Q = -rshifts;
	s32i.n	a14, a9, 0	# *res_nrg_Q_635(D),
	j	.L1		#
.L73:
	l32i	a6, sp, 612	# %sfp,
	l32i	a9, sp, 752	# %sfp, ivtmp$44
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:270:         tmp1 = (opus_int32)1 << 16;                                                                             /* Q16 */
	l32r	a11, .LC6	#, tmp1
	add.n	a13, a9, a6	# _289, ivtmp$44,
	l32i	a6, sp, 684	# %sfp, ivtmp$41
	s32i	a3, sp, 628	# %sfp, pretmp_2649
	addi	a12, sp, 104	# ivtmp$42,,
	mov.n	a7, a3	# pretmp_2649, pretmp_2649
.L81:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:272:             Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );                                       /* Q16 */
	l32i.n	a2, a6, 0	# MEM[base: _284, offset: 0B], MEM[base: _284, offset: 0B]
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	l32i.n	a3, a12, 0	# MEM[base: _285, offset: 0B], _393
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:272:             Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );                                       /* Q16 */
	srai	a2, a2, 8	# tmp1089, MEM[base: _284, offset: 0B],
	addi.n	a2, a2, 1	# _391, tmp1089,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:272:             Atmp1 = silk_RSHIFT_ROUND( Af_QA[ k ], QA - 16 );                                       /* Q16 */
	srai	a5, a2, 1	# Atmp1, _391,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	srai	a4, a2, 16	# tmp1092, _391,
	slli	a8, a5, 16	# tmp1091, Atmp1,
	addi.n	a4, a4, 1	# tmp1093, tmp1092,
	srai	a8, a8, 16	# _396, tmp1091,
	srai	a4, a4, 1	# _405, tmp1093,
	srai	a14, a3, 16	# tmp1094, _393,
	extui	a10, a3, 0, 16	# tmp1098, _393,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	srai	a2, a2, 17	# tmp1102, _391,
	extui	a15, a5, 0, 16	# tmp1106, Atmp1,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	mull	a3, a3, a4	# tmp1096, _393, _405
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	mull	a2, a2, a8	# tmp1103, tmp1102, _396
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	mull	a14, a14, a8	# tmp1095, tmp1094, _396
	mull	a10, a10, a8	# tmp1099, tmp1098, _396
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	mull	a4, a4, a5	# tmp1104, _405, Atmp1
	mull	a8, a15, a8	# tmp1107, tmp1106, _396
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	add.n	a14, a14, a3	# tmp1097, tmp1095, tmp1096
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	srai	a10, a10, 16	# tmp1100, tmp1099,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	add.n	a3, a2, a4	# tmp1105, tmp1103, tmp1104
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	srai	a8, a8, 16	# tmp1108, tmp1107,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:275:             A_Q16[ k ] = -Atmp1;
	neg	a2, a5	# tmp1110, Atmp1
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	add.n	a4, a14, a10	# tmp1101, tmp1097, tmp1100
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	add.n	a3, a3, a8	# tmp1109, tmp1105, tmp1108
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:275:             A_Q16[ k ] = -Atmp1;
	s32i.n	a2, a9, 0	# MEM[base: _286, offset: 0B], tmp1110
	addi.n	a9, a9, 4	# ivtmp$44, ivtmp$44,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:273:             nrg  = silk_SMLAWW( nrg, CAf[ k + 1 ], Atmp1 );                                         /* Q( -rshifts ) */
	add.n	a7, a7, a4	# pretmp_2649, pretmp_2649, tmp1101
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:274:             tmp1 = silk_SMLAWW( tmp1, Atmp1, Atmp1 );                                               /* Q16 */
	add.n	a11, a11, a3	# tmp1, tmp1, tmp1109
	addi.n	a6, a6, 4	# ivtmp$41, ivtmp$41,
	addi.n	a12, a12, 4	# ivtmp$42, ivtmp$42,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:271:         for( k = 0; k < D; k++ ) {
	bne	a9, a13, .L81	# ivtmp$44, _289,
	l32i	a8, sp, 736	# %sfp,
	neg	a11, a11	# tmp1112, tmp1
	slli	a4, a11, 16	# tmp1113, tmp1112,
	srai	a4, a4, 16	# _2794, tmp1113,
	extui	a2, a8, 0, 16	# tmp1115,,
	mull	a2, a2, a4	# tmp1116, tmp1115, _2794
	srai	a3, a11, 15	# tmp1118, tmp1112,
	srai	a5, a8, 16	# tmp1114,,
	addi.n	a3, a3, 1	# tmp1119, tmp1118,
	mull	a5, a5, a4	# _2797, tmp1114, _2794
	s32i	a7, sp, 628	# %sfp, pretmp_2649
	srai	a4, a2, 16	# _2802, tmp1116,
	srai	a3, a3, 1	# _2810, tmp1119,
	mov.n	a9, a7	#, pretmp_2649
	mov.n	a14, a8	#,
	j	.L20		#
.L89:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:116:     for( n = 0; n < D; n++ ) {
	movi.n	a4, 0	# _2802,
	l32i	a14, sp, 736	# %sfp,
	movi.n	a3, -1	# _2810,
	mov.n	a5, a4	# _2797, _2802
	mov.n	a9, a8	#,
.L20:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:277:         *res_nrg = silk_SMLAWW( nrg, silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ), -tmp1 );/* Q( -rshifts ) */
	add.n	a2, a9, a5	# tmp1120,, _2797
	mull	a3, a14, a3	# tmp1122,, _2810
	add.n	a2, a2, a4	# tmp1121, tmp1120, _2802
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:277:         *res_nrg = silk_SMLAWW( nrg, silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ), -tmp1 );/* Q( -rshifts ) */
	l32i	a8, sp, 744	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:277:         *res_nrg = silk_SMLAWW( nrg, silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ), -tmp1 );/* Q( -rshifts ) */
	add.n	a2, a2, a3	# tmp1123, tmp1121, tmp1122
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:278:         *res_nrg_Q = -rshifts;
	l32i	a14, sp, 680	# %sfp,
	l32i	a9, sp, 748	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:277:         *res_nrg = silk_SMLAWW( nrg, silk_SMMUL( SILK_FIX_CONST( FIND_LPC_COND_FAC, 32 ), C0 ), -tmp1 );/* Q( -rshifts ) */
	s32i.n	a2, a8, 0	# *res_nrg_633(D), tmp1123
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:278:         *res_nrg_Q = -rshifts;
	s32i.n	a14, a9, 0	# *res_nrg_Q_635(D),
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:280: }
	j	.L1		#
.L62:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a3, a4, 3	# tmp1127, _475,
	add.n	a3, a4, a3	# tmp1129, _475, tmp1127
	slli	a3, a3, 3	# tmp1131, tmp1129,
	sub	a4, a3, a4	# tmp1133, tmp1131, _475
	slli	a3, a4, 2	# tmp1135, tmp1133,
	sub	a3, a3, a4	# tmp1138, tmp1135, tmp1133
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	srai	a12, a12, 1	# tmp1124, iftmp$15_720,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	slli	a3, a3, 16	# tmp1140, tmp1138,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:88:     y >>= silk_RSHIFT(lz, 1);
	ssr	a12	# tmp1124
	sra	a12, a5	# y, y
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a3, a3, 16	# tmp1139, tmp1140,
	mull	a3, a3, a12	# tmp1141, tmp1139, y
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:208:                 rc_Q31 = silk_RSHIFT32( rc_Q31 + silk_DIV32( tmp2, rc_Q31 ), 1 );                       /* Q15 */
	s32i	a9, sp, 776	#,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	srai	a3, a3, 16	# _906, tmp1141,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:91:     y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));
	add.n	a12, a12, a3	# y, y, _906
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:208:                 rc_Q31 = silk_RSHIFT32( rc_Q31 + silk_DIV32( tmp2, rc_Q31 ), 1 );                       /* Q15 */
	mov.n	a3, a12	#, y
	call0	__divsi3		#
	add.n	a2, a2, a12	# tmp1146,, y
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:210:                 if( num < 0 ) {
	l32i	a9, sp, 776	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:208:                 rc_Q31 = silk_RSHIFT32( rc_Q31 + silk_DIV32( tmp2, rc_Q31 ), 1 );                       /* Q15 */
	srai	a2, a2, 1	# rc_Q31, tmp1146,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:209:                 rc_Q31 = silk_LSHIFT32( rc_Q31, 16 );                                                   /* Q31 */
	slli	a2, a2, 16	# _324, rc_Q31,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:210:                 if( num < 0 ) {
	bltz	a9, .L82	# num,
	srai	a6, a2, 6	#, _324,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	l32i	a7, sp, 604	# %sfp,
	s32i	a6, sp, 616	# %sfp,
	beqz.n	a7, .L83	#,
	l32i	a8, sp, 720	# %sfp,
	s32i	a2, sp, 640	# %sfp, _324
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	movi.n	a9, 1	#,
	srai	a2, a2, 31	#, _324,
	s32i	a2, sp, 644	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:222:         for( k = 0; k < (n + 1) >> 1; k++ ) {
	s32i	a8, sp, 708	# %sfp,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:216:             reached_max_gain = 1;
	s32i	a9, sp, 620	# %sfp,
	j	.L66		#
.L83:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	l32i	a14, sp, 664	# %sfp,
	addmi	a3, sp, 0x100	#,,
	slli	a2, a14, 2	# tmp1150,,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	movi.n	a7, 1	#,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:228:         Af_QA[ n ] = silk_RSHIFT32( rc_Q31, 31 - QA );                                          /* QA */
	add.n	a2, a3, a2	# tmp1151,, tmp1150
	s32i.n	a6, a2, 40	# Af_QA,
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:187:         CAf[ n + 1 ] = tmp1;                                                                            /* Q( -rshifts ) */
	s32i	a7, sp, 608	# %sfp,
	mov.n	a8, a7	#,
	j	.L65		#
.L59:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:65:     * frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
	extui	a4, a2, 0, 7	# _475, tmp2,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\Inlines.h:84:         y = 46214;        /* 46214 = sqrt(2) * 32768 */
	l32r	a5, .LC8	#, y
	j	.L62		#
.L130:
	addi	a3, a3, -36	#, iftmp$15_653,
	s32i	a3, sp, 680	# %sfp,
	mov.n	a14, a4	#,
	mov.n	a8, a4	#,
	j	.L5		#
.L1:
# @OPUS@\upstream\silk\fixed\burg_modified_FIX.c:280: }
	l32i	a0, sp, 812	#,
	movi	a9, 0x330	#,
	l32i	a12, sp, 808	#,
	l32i	a13, sp, 804	#,
	l32i	a14, sp, 800	#,
	l32i	a15, sp, 796	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_burg_modified_c, .-silk_burg_modified_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
