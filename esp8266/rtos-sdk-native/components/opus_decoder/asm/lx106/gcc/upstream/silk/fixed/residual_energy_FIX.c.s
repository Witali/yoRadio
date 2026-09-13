# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/residual_energy_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"residual_energy_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\residual_energy_FIX.c.s.raw
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
	.section	.text.silk_residual_energy_FIX,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_residual_energy_FIX
	.type	silk_residual_energy_FIX, @function
# Function: silk_residual_energy_FIX
# Module: upstream/silk/fixed/residual_energy_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Calculates residual energies of input subframes where all subframes have LPC_order   */
# C context: /* of preceding samples                                                                 */
# C context: void silk_residual_energy_FIX(
# C context: opus_int32                nrgs[ MAX_NB_SUBFR ],                   /* O    Residual energy per subframe                                                */
# C context: opus_int                  nrgsQ[ MAX_NB_SUBFR ],                  /* O    Q value per subframe                                                        */
# C context: const opus_int16                x[],                                    /* I    Input signal                                                                */
# C context: opus_int16                a_Q12[ 2 ][ MAX_LPC_ORDER ],            /* I    AR coefs for each frame half                                                */
silk_residual_energy_FIX:
	addi	sp, sp, -96	#,,
	s32i	a13, sp, 84	#,
	mov.n	a13, a7	# subfr_length, subfr_length
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:57:     offset = LPC_order + subfr_length;
	l32i	a7, sp, 100	# LPC_order,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:57:     offset = LPC_order + subfr_length;
	add.n	a15, a7, a13	# offset,, subfr_length
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	s32i.n	a2, sp, 40	# %sfp, nrgs
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:60:     ALLOC( LPC_res, ( MAX_NB_SUBFR >> 1 ) * offset, opus_int16 );
	slli	a2, a15, 1	#, offset,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	s32i	a0, sp, 92	#,
	s32i	a14, sp, 80	#,
	s32i.n	a6, sp, 48	# %sfp, gains
	mov.n	a14, a5	# a_Q12, a_Q12
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:54:     SAVE_STACK;
	s32i.n	a4, sp, 52	#, tmp10
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	s32i	a12, sp, 88	#,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	s32i.n	a3, sp, 44	# %sfp, nrgsQ
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:60:     ALLOC( LPC_res, ( MAX_NB_SUBFR >> 1 ) * offset, opus_int16 );
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:54:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:60:     ALLOC( LPC_res, ( MAX_NB_SUBFR >> 1 ) * offset, opus_int16 );
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:54:     SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:60:     ALLOC( LPC_res, ( MAX_NB_SUBFR >> 1 ) * offset, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:62:     for( i = 0; i < nb_subfr >> 1; i++ ) {
	l32i	a3, sp, 96	# nb_subfr,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:60:     ALLOC( LPC_res, ( MAX_NB_SUBFR >> 1 ) * offset, opus_int16 );
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:62:     for( i = 0; i < nb_subfr >> 1; i++ ) {
	srai	a2, a3, 1	# _103,,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:62:     for( i = 0; i < nb_subfr >> 1; i++ ) {
	l32i.n	a10, sp, 52	#,
	blti	a2, 1, .L2	# _103,,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:67:         LPC_res_ptr = LPC_res + LPC_order;
	l32i	a4, sp, 100	# LPC_order,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:67:         LPC_res_ptr = LPC_res + LPC_order;
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:67:         LPC_res_ptr = LPC_res + LPC_order;
	slli	a3, a4, 1	# tmp111,,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:67:         LPC_res_ptr = LPC_res + LPC_order;
	add.n	a3, a7, a3	#,, tmp111
	s32i.n	a3, sp, 24	# %sfp,
	l32i.n	a12, sp, 40	# %sfp, ivtmp$26
	l32i.n	a4, sp, 24	# %sfp,
	l32i.n	a7, sp, 16	# %sfp,
	slli	a2, a2, 3	# tmp112, _103,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:79:         x_ptr += ( MAX_NB_SUBFR >> 1 ) * offset;
	slli	a3, a15, 2	#, offset,
	add.n	a2, a2, a12	#, tmp112, ivtmp$26
	add.n	a4, a4, a7	#,,
	l32i.n	a15, sp, 44	# %sfp, ivtmp$27
	s32i.n	a3, sp, 28	# %sfp,
	s32i.n	a2, sp, 32	# %sfp,
	s32i.n	a4, sp, 36	# %sfp,
.L3:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:64:         silk_LPC_analysis_filter( LPC_res, x_ptr, a_Q12[ i ], ( MAX_NB_SUBFR >> 1 ) * offset, LPC_order, arch );
	l32i	a7, sp, 104	# arch,
	l32i	a6, sp, 100	# LPC_order,
	l32i.n	a5, sp, 16	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	mov.n	a3, a10	#, x
	mov.n	a4, a14	#, ivtmp$25
	s32i.n	a10, sp, 52	#,
	call0	silk_LPC_analysis_filter		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:70:             silk_sum_sqr_shift( &nrgs[ i * ( MAX_NB_SUBFR >> 1 ) + j ], &rshift, LPC_res_ptr, subfr_length );
	l32i.n	a4, sp, 24	# %sfp,
	mov.n	a2, a12	#, ivtmp$26
	mov.n	a5, a13	#, subfr_length
	addi.n	a3, sp, 8	#,,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	l32i.n	a3, sp, 8	# rshift, rshift
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:70:             silk_sum_sqr_shift( &nrgs[ i * ( MAX_NB_SUBFR >> 1 ) + j ], &rshift, LPC_res_ptr, subfr_length );
	l32i.n	a4, sp, 36	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	neg	a3, a3	# tmp114, rshift
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:70:             silk_sum_sqr_shift( &nrgs[ i * ( MAX_NB_SUBFR >> 1 ) + j ], &rshift, LPC_res_ptr, subfr_length );
	addi.n	a2, a12, 4	#, ivtmp$26,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	s32i.n	a3, a15, 0	# MEM[base: _37, offset: 0B], tmp114
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:70:             silk_sum_sqr_shift( &nrgs[ i * ( MAX_NB_SUBFR >> 1 ) + j ], &rshift, LPC_res_ptr, subfr_length );
	mov.n	a5, a13	#, subfr_length
	addi.n	a3, sp, 8	#,,
	call0	silk_sum_sqr_shift		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	l32i.n	a2, sp, 8	# rshift, rshift
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:79:         x_ptr += ( MAX_NB_SUBFR >> 1 ) * offset;
	l32i.n	a10, sp, 52	#,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	neg	a2, a2	# tmp119, rshift
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:73:             nrgsQ[ i * ( MAX_NB_SUBFR >> 1 ) + j ] = -rshift;
	s32i.n	a2, a15, 4	# MEM[base: _37, offset: 4B], tmp119
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:62:     for( i = 0; i < nb_subfr >> 1; i++ ) {
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:79:         x_ptr += ( MAX_NB_SUBFR >> 1 ) * offset;
	l32i.n	a2, sp, 28	# %sfp,
	addi.n	a12, a12, 8	# ivtmp$26, ivtmp$26,
	add.n	a10, a10, a2	# x, x,
	addi	a14, a14, 32	# ivtmp$25, ivtmp$25,
	addi.n	a15, a15, 8	# ivtmp$27, ivtmp$27,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:62:     for( i = 0; i < nb_subfr >> 1; i++ ) {
	bne	a12, a3, .L3	# ivtmp$26,,
.L5:
	l32i.n	a6, sp, 44	# %sfp, ivtmp$16
	l32i.n	a14, sp, 48	# %sfp, ivtmp$17
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:48: {
	movi.n	a15, 0	# i,
	mov.n	a12, a15	# i, i
	l32i.n	a7, sp, 40	# %sfp, ivtmp$15
	mov.n	a13, a14	# ivtmp$17, ivtmp$17
	mov.n	a15, a6	# ivtmp$16, ivtmp$16
	j	.L4		#
.L2:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:83:     for( i = 0; i < nb_subfr; i++ ) {
	beqi	a3, 1, .L5	# tmp4,,
.L8:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:97:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:98: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
.L4:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:85:         lz1 = silk_CLZ32( nrgs[  i ] ) - 1;
	l32i.n	a9, a7, 0	# MEM[base: _75, offset: 0B], _161
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a14, 0x1f	# prephitmp_158,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a2, a9	# iftmp$11_160, _161
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a9, .L6	# _161,
	addi.n	a14, a2, -1	# prephitmp_158, iftmp$11_160,
.L6:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:86:         lz2 = silk_CLZ32( gains[ i ] ) - 1;
	l32i.n	a2, a13, 0	# MEM[base: _173, offset: 0B], _155
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a3, a2	# iftmp$11_148, _155
	addi.n	a3, a3, -1	# prephitmp_133, iftmp$11_148,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a2, .L10	# _155,
	slli	a4, a3, 1	#, prephitmp_133,
	s32i.n	a4, sp, 16	# %sfp,
	j	.L7		#
.L10:
	movi.n	a4, 0x3e	#,
	movi.n	a3, 0x1f	# prephitmp_133,
	s32i.n	a4, sp, 16	# %sfp,
.L7:
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:88:         tmp32 = silk_LSHIFT32( gains[ i ], lz2 );
	ssl	a3	# prephitmp_133
	sll	a2, a2	# tmp32, _155
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:91:         tmp32 = silk_SMMUL( tmp32, tmp32 ); /* Q( 2 * lz2 - 32 )*/
	srai	a3, a2, 31	# tmp122, tmp32,
	mov.n	a4, a2	#, tmp32
	mov.n	a5, a3	#, tmp122
	s32i.n	a7, sp, 56	#,
	s32i.n	a9, sp, 52	#,
	call0	__muldi3		#
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:94:         nrgs[ i ] = silk_SMMUL( tmp32, silk_LSHIFT32( nrgs[ i ], lz1 ) ); /* Q( nrgsQ[ i ] + lz1 + 2 * lz2 - 32 - 32 )*/
	l32i.n	a9, sp, 52	#,
	mov.n	a2, a3	#, tmp137
	ssl	a14	# prephitmp_158
	sll	a5, a9	# tmp125, _161
	mov.n	a4, a5	#, tmp125
	srai	a3, a3, 31	#, tmp137,
	srai	a5, a5, 31	#, tmp125,
	call0	__muldi3		#
	l32i.n	a7, sp, 56	#,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:83:     for( i = 0; i < nb_subfr; i++ ) {
	l32i	a4, sp, 96	# nb_subfr,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:94:         nrgs[ i ] = silk_SMMUL( tmp32, silk_LSHIFT32( nrgs[ i ], lz1 ) ); /* Q( nrgsQ[ i ] + lz1 + 2 * lz2 - 32 - 32 )*/
	s32i.n	a3, a7, 0	# MEM[base: _75, offset: 0B],
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:95:         nrgsQ[ i ] += lz1 + 2 * lz2 - 32 - 32;
	l32i.n	a2, a15, 0	# MEM[base: _94, offset: 0B], MEM[base: _94, offset: 0B]
	l32i.n	a3, sp, 16	# %sfp,
	addi	a2, a2, -64	# tmp130, MEM[base: _94, offset: 0B],
	add.n	a2, a2, a14	# tmp132, tmp130, prephitmp_158
	add.n	a2, a2, a3	# tmp133, tmp132,
	s32i.n	a2, a15, 0	# MEM[base: _94, offset: 0B], tmp133
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:83:     for( i = 0; i < nb_subfr; i++ ) {
	addi.n	a12, a12, 1	# i, i,
	addi.n	a7, a7, 4	# ivtmp$15, ivtmp$15,
	addi.n	a15, a15, 4	# ivtmp$16, ivtmp$16,
	addi.n	a13, a13, 4	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\silk\fixed\residual_energy_FIX.c:83:     for( i = 0; i < nb_subfr; i++ ) {
	blt	a12, a4, .L4	# i,,
	j	.L8		#
	.size	silk_residual_energy_FIX, .-silk_residual_energy_FIX
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
