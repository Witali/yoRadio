# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/gain_quant.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"gain_quant.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\gain_quant.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\gain_quant.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\gain_quant.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\gain_quant.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\gain_quant.c.s.raw
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
	.section	.text.silk_gains_quant,"ax",@progbits
	.literal_position
	.literal .LC0, 3923
	.literal .LC1, -2090
	.literal .LC2, 2251
	.literal .LC3, 2090
	.literal .LC4, 3967
	.align	4
	.global	silk_gains_quant
	.type	silk_gains_quant, @function
# Function: silk_gains_quant
# Module: upstream/silk/gain_quant.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define INV_SCALE_Q16           ( ( 65536 * ( ( ( MAX_QGAIN_DB - MIN_QGAIN_DB ) * 128 ) / 6 ) ) / ( N_LEVELS_QGAIN - 1 ) )
# C context:
# C context: /* Gain scalar quantization with hysteresis, uniform on log scale */
# C context: void silk_gains_quant(
# C context: opus_int8                   ind[ MAX_NB_SUBFR ],            /* O    gain indices                                */
# C context: opus_int32                  gain_Q16[ MAX_NB_SUBFR ],       /* I/O  gains (quantized out)                       */
# C context: opus_int8                   *prev_ind,                      /* I/O  last index in previous frame                */
# C context: const opus_int              conditional,                    /* I    first gain is delta coded if 1              */
silk_gains_quant:
	addi	sp, sp, -48	#,,
	s32i.n	a13, sp, 36	#,
	s32i.n	a0, sp, 44	#,
	s32i.n	a12, sp, 40	#,
	s32i.n	a14, sp, 32	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\gain_quant.c:46: {
	s32i.n	a6, sp, 4	# %sfp, nb_subfr
	s32i.n	a5, sp, 8	# %sfp, conditional
	mov.n	a13, a4	# prev_ind, prev_ind
# @OPUS@\upstream\silk\gain_quant.c:49:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a6, 1, .L1	# nb_subfr,,
	movi.n	a4, 0x3f	#,
# @OPUS@\upstream\silk\gain_quant.c:49:     for( k = 0; k < nb_subfr; k++ ) {
	movi.n	a15, 0	# k,
	and	a4, a4, a4	#,,
	mov.n	a14, a15	# k, k
	mov.n	a12, a3	# ivtmp$42, gain_Q16
	s32i.n	a4, sp, 0	# %sfp,
	mov.n	a15, a2	# ivtmp$43, ivtmp$43
.L17:
# @OPUS@\upstream\silk\gain_quant.c:51:         ind[ k ] = silk_SMULWB( SCALE_Q16, silk_lin2log( gain_Q16[ k ] ) - OFFSET );
	l32i.n	a2, a12, 0	# MEM[base: _116, offset: 0B],
	call0	silk_lin2log		#
	l32i.n	a2, a12, 0	# MEM[base: _116, offset: 0B],
	call0	silk_lin2log		#
	l32r	a4, .LC1	#,
	l32r	a3, .LC2	#, tmp114
	add.n	a2, a2, a4	# tmp111,,
	mul16s	a2, a2, a3	# tmp113, tmp111, tmp114
# @OPUS@\upstream\silk\gain_quant.c:51:         ind[ k ] = silk_SMULWB( SCALE_Q16, silk_lin2log( gain_Q16[ k ] ) - OFFSET );
	extui	a2, a2, 16, 8	# _13, tmp113,,
	s8i	a2, a15, 0	# MEM[base: _115, offset: 0B], _13
# @OPUS@\upstream\silk\gain_quant.c:54:         if( ind[ k ] < *prev_ind ) {
	l8ui	a3, a13, 0	# *prev_ind_72(D),
	slli	a7, a2, 24	# tmp232, _13,
	slli	a3, a3, 24	# tmp118, *prev_ind_72(D),
	bge	a7, a3, .L3	# tmp232, tmp118,
# @OPUS@\upstream\silk\gain_quant.c:55:             ind[ k ]++;
	addi.n	a2, a2, 1	# tmp122, _13,
	extui	a2, a2, 0, 8	# _13, tmp122
	slli	a7, a2, 24	# tmp232, _13,
.L3:
# @OPUS@\upstream\silk\gain_quant.c:57:         ind[ k ] = silk_LIMIT_int( ind[ k ], 0, N_LEVELS_QGAIN - 1 );
	bgez	a7, .L4	# tmp232,
	movi.n	a2, 0	# _13,
.L4:
	slli	a3, a2, 24	# tmp128, _13,
	l32i.n	a4, sp, 0	# %sfp,
	srai	a3, a3, 24	# tmp127, tmp128,
	bge	a4, a3, .L5	#, tmp127,
	movi.n	a2, 0x3f	# _13,
.L5:
# @OPUS@\upstream\silk\gain_quant.c:60:         if( k == 0 && conditional == 0 ) {
	l32i.n	a4, sp, 8	# %sfp,
# @OPUS@\upstream\silk\gain_quant.c:57:         ind[ k ] = silk_LIMIT_int( ind[ k ], 0, N_LEVELS_QGAIN - 1 );
	s8i	a2, a15, 0	# MEM[base: _115, offset: 0B], _13
# @OPUS@\upstream\silk\gain_quant.c:60:         if( k == 0 && conditional == 0 ) {
	or	a3, a4, a14	# tmp131,, k
	extui	a7, a2, 0, 8	# iftmp$5_86, _13
	bnez.n	a3, .L6	# tmp131,
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	l8ui	a2, a13, 0	# *prev_ind_72(D),
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	movi.n	a3, 0x3f	# tmp135,
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	slli	a2, a2, 24	# tmp134, *prev_ind_72(D),
	srai	a2, a2, 24	# tmp132, tmp134,
	addi	a2, a2, -4	# _19, tmp132,
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	blt	a3, a2, .L19	# tmp135, _19,
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	slli	a3, a7, 24	# tmp137, iftmp$5_86,
	srai	a3, a3, 24	# _21, tmp137,
	bge	a3, a2, .L8	# _21, _19,
	mov.n	a3, a2	# _21, _19
.L8:
	slli	a7, a3, 3	# tmp139, _21,
	sub	a7, a7, a3	# tmp140, tmp139, _21
	slli	a2, a7, 6	# tmp141, tmp140,
	add.n	a2, a7, a2	# tmp142, tmp140, tmp141
	slli	a2, a2, 4	# tmp143, tmp142,
	slli	a7, a7, 2	# tmp149, tmp140,
	l32r	a8, .LC3	#, tmp152
	add.n	a2, a2, a3	# tmp144, tmp143, _21
	add.n	a7, a7, a3	# tmp150, tmp149, _21
	srai	a2, a2, 16	# tmp145, tmp144,
	add.n	a7, a7, a8	# tmp151, tmp150, tmp152
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	extui	a3, a3, 0, 8	# iftmp$9_57, _21
	add.n	a2, a2, a7	# prephitmp_147, tmp145, tmp151
	j	.L7		#
.L19:
	l32r	a2, .LC0	#, prephitmp_147
.L7:
# @OPUS@\upstream\silk\gain_quant.c:62:             ind[ k ] = silk_LIMIT_int( ind[ k ], *prev_ind + MIN_DELTA_GAIN_QUANT, N_LEVELS_QGAIN - 1 );
	s8i	a3, a15, 0	# MEM[base: _115, offset: 0B], iftmp$9_57
# @OPUS@\upstream\silk\gain_quant.c:63:             *prev_ind = ind[ k ];
	s8i	a3, a13, 0	# *prev_ind_72(D), iftmp$9_57
	j	.L9		#
.L6:
# @OPUS@\upstream\silk\gain_quant.c:66:             ind[ k ] = ind[ k ] - *prev_ind;
	l8ui	a3, a13, 0	# *prev_ind_72(D),
	sub	a2, a2, a3	# tmp155, _13, *prev_ind_72(D)
	extui	a2, a2, 0, 8	# _23, tmp155
# @OPUS@\upstream\silk\gain_quant.c:66:             ind[ k ] = ind[ k ] - *prev_ind;
	s8i	a2, a15, 0	# MEM[base: _115, offset: 0B], _23
# @OPUS@\upstream\silk\gain_quant.c:69:             double_step_size_threshold = 2 * MAX_DELTA_GAIN_QUANT - N_LEVELS_QGAIN + *prev_ind;
	l8ui	a8, a13, 0	# *prev_ind_72(D), _24
# @OPUS@\upstream\silk\gain_quant.c:70:             if( ind[ k ] > double_step_size_threshold ) {
	slli	a9, a2, 24	# tmp230, _23,
# @OPUS@\upstream\silk\gain_quant.c:69:             double_step_size_threshold = 2 * MAX_DELTA_GAIN_QUANT - N_LEVELS_QGAIN + *prev_ind;
	slli	a3, a8, 24	# tmp157, _24,
	srai	a3, a3, 24	# tmp156, tmp157,
# @OPUS@\upstream\silk\gain_quant.c:69:             double_step_size_threshold = 2 * MAX_DELTA_GAIN_QUANT - N_LEVELS_QGAIN + *prev_ind;
	addi.n	a3, a3, 8	# double_step_size_threshold, tmp156,
# @OPUS@\upstream\silk\gain_quant.c:70:             if( ind[ k ] > double_step_size_threshold ) {
	srai	a7, a9, 24	# _26, tmp230,
# @OPUS@\upstream\silk\gain_quant.c:70:             if( ind[ k ] > double_step_size_threshold ) {
	bge	a3, a7, .L10	# double_step_size_threshold, _26,
# @OPUS@\upstream\silk\gain_quant.c:71:                 ind[ k ] = double_step_size_threshold + silk_RSHIFT( ind[ k ] - double_step_size_threshold + 1, 1 );
	sub	a2, a7, a3	# tmp160, _26, double_step_size_threshold
	addi.n	a2, a2, 1	# tmp161, tmp160,
	srai	a2, a2, 1	# tmp162, tmp161,
# @OPUS@\upstream\silk\gain_quant.c:71:                 ind[ k ] = double_step_size_threshold + silk_RSHIFT( ind[ k ] - double_step_size_threshold + 1, 1 );
	addi.n	a7, a8, 8	# tmp164, _24,
	add.n	a2, a2, a7	# tmp167, tmp162, tmp164
	extui	a2, a2, 0, 8	# _23, tmp167
	slli	a9, a2, 24	# tmp230, _23,
.L10:
# @OPUS@\upstream\silk\gain_quant.c:74:             ind[ k ] = silk_LIMIT_int( ind[ k ], MIN_DELTA_GAIN_QUANT, MAX_DELTA_GAIN_QUANT );
	srai	a9, a9, 24	# tmp170, tmp230,
	movi.n	a7, -4	# tmp172,
	bge	a9, a7, .L11	# tmp170, tmp172,
	movi.n	a2, -4	# _23,
.L11:
	movi.n	a9, 0x24	# tmp174,
	slli	a7, a2, 24	# tmp176, _23,
	srai	a7, a7, 24	# tmp175, tmp176,
	extui	a10, a9, 0, 8	# tmp177, tmp174
	bge	a10, a7, .L12	# tmp177, tmp175,
	mov.n	a2, a9	# _23, tmp174
.L12:
# @OPUS@\upstream\silk\gain_quant.c:77:             if( ind[ k ] > double_step_size_threshold ) {
	slli	a7, a2, 24	# tmp180, _23,
# @OPUS@\upstream\silk\gain_quant.c:74:             ind[ k ] = silk_LIMIT_int( ind[ k ], MIN_DELTA_GAIN_QUANT, MAX_DELTA_GAIN_QUANT );
	s8i	a2, a15, 0	# MEM[base: _115, offset: 0B], _23
# @OPUS@\upstream\silk\gain_quant.c:77:             if( ind[ k ] > double_step_size_threshold ) {
	srai	a7, a7, 24	# tmp179, tmp180,
# @OPUS@\upstream\silk\gain_quant.c:77:             if( ind[ k ] > double_step_size_threshold ) {
	bge	a3, a7, .L13	# double_step_size_threshold, tmp179,
# @OPUS@\upstream\silk\gain_quant.c:78:                 *prev_ind += silk_LSHIFT( ind[ k ], 1 ) - double_step_size_threshold;
	l8ui	a2, a13, 0	# *prev_ind_72(D),
# @OPUS@\upstream\silk\gain_quant.c:78:                 *prev_ind += silk_LSHIFT( ind[ k ], 1 ) - double_step_size_threshold;
	slli	a7, a7, 1	# tmp189, tmp179,
# @OPUS@\upstream\silk\gain_quant.c:78:                 *prev_ind += silk_LSHIFT( ind[ k ], 1 ) - double_step_size_threshold;
	addi	a2, a2, -8	# tmp183, *prev_ind_72(D),
	sub	a2, a2, a8	# tmp186, tmp183, _24
	add.n	a2, a2, a7	# tmp192, tmp186, tmp189
# @OPUS@\upstream\silk\gain_quant.c:79:                 *prev_ind = silk_min_int( *prev_ind, N_LEVELS_QGAIN - 1 );
	slli	a3, a2, 24	# tmp195, tmp192,
	l32i.n	a4, sp, 0	# %sfp,
	srai	a3, a3, 24	# tmp194, tmp195,
	bge	a4, a3, .L21	#, tmp194,
	movi.n	a2, 0x3f	# tmp181,
	j	.L21		#
.L13:
# @OPUS@\upstream\silk\gain_quant.c:81:                 *prev_ind += ind[ k ];
	l8ui	a3, a13, 0	# *prev_ind_72(D),
	add.n	a2, a3, a2	# tmp200, *prev_ind_72(D), _23
.L21:
	extui	a2, a2, 0, 8	# _42, tmp200
	s8i	a2, a13, 0	# *prev_ind_72(D), _42
# @OPUS@\upstream\silk\gain_quant.c:85:             ind[ k ] -= MIN_DELTA_GAIN_QUANT;
	l8ui	a2, a15, 0	# MEM[base: _115, offset: 0B],
	l32r	a8, .LC3	#, tmp224
	addi.n	a2, a2, 4	# tmp202, MEM[base: _115, offset: 0B],
	s8i	a2, a15, 0	# MEM[base: _115, offset: 0B], tmp202
	l8ui	a2, a13, 0	# *prev_ind_72(D), pretmp_128
	l32r	a7, .LC4	#, tmp229
	slli	a2, a2, 24	# tmp204, pretmp_128,
	srai	a9, a2, 24	# tmp203, tmp204,
	slli	a3, a9, 3	# tmp206, tmp203,
	sub	a3, a3, a9	# tmp207, tmp206, tmp203
	slli	a2, a3, 6	# tmp208, tmp207,
	add.n	a2, a3, a2	# tmp209, tmp207, tmp208
	slli	a2, a2, 4	# tmp210, tmp209,
	slli	a3, a3, 2	# tmp221, tmp220,
	add.n	a2, a2, a9	# tmp211, tmp210, tmp203
	add.n	a3, a3, a9	# tmp222, tmp221, tmp216
	srai	a2, a2, 16	# tmp212, tmp211,
	add.n	a3, a3, a8	# tmp223, tmp222, tmp224
	add.n	a2, a2, a3	# prephitmp_147, tmp212, tmp223
	bge	a7, a2, .L9	# tmp229, prephitmp_147,
	mov.n	a2, a7	# prephitmp_147, tmp229
.L9:
# @OPUS@\upstream\silk\gain_quant.c:89:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\gain_quant.c:89:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	s32i.n	a2, a12, 0	# MEM[base: _116, offset: 0B],
# @OPUS@\upstream\silk\gain_quant.c:49:     for( k = 0; k < nb_subfr; k++ ) {
	l32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\silk\gain_quant.c:49:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a14, a14, 1	# k, k,
	addi.n	a12, a12, 4	# ivtmp$42, ivtmp$42,
	addi.n	a15, a15, 1	# ivtmp$43, ivtmp$43,
# @OPUS@\upstream\silk\gain_quant.c:49:     for( k = 0; k < nb_subfr; k++ ) {
	bne	a2, a14, .L17	#, k,
.L1:
# @OPUS@\upstream\silk\gain_quant.c:91: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_gains_quant, .-silk_gains_quant
	.section	.text.silk_gains_dequant,"ax",@progbits
	.literal_position
	.literal .LC5, 2090
	.align	4
	.global	silk_gains_dequant
	.type	silk_gains_dequant, @function
# Function: silk_gains_dequant
# Module: upstream/silk/gain_quant.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Gains scalar dequantization, uniform on log scale */
# C context: void silk_gains_dequant(
# C context: opus_int32                  gain_Q16[ MAX_NB_SUBFR ],       /* O    quantized gains                             */
# C context: const opus_int8             ind[ MAX_NB_SUBFR ],            /* I    gain indices                                */
# C context: opus_int8                   *prev_ind,                      /* I/O  last index in previous frame                */
# C context: const opus_int              conditional,                    /* I    first gain is delta coded if 1              */
silk_gains_dequant:
	addi	sp, sp, -48	#,,
	s32i.n	a15, sp, 28	#,
	mov.n	a15, a4	# prev_ind, prev_ind
	movi.n	a4, 0x3f	#,
	s32i.n	a13, sp, 36	#,
	and	a4, a4, a4	#,,
# @OPUS@\upstream\silk\gain_quant.c:104:     for( k = 0; k < nb_subfr; k++ ) {
	movi.n	a13, 0	# k,
# @OPUS@\upstream\silk\gain_quant.c:101: {
	s32i.n	a14, sp, 32	#,
	s32i.n	a0, sp, 44	#,
	s32i.n	a12, sp, 40	#,
# @OPUS@\upstream\silk\gain_quant.c:101: {
	s32i.n	a3, sp, 0	# %sfp, ind
	s32i.n	a5, sp, 4	# %sfp, conditional
# @OPUS@\upstream\silk\gain_quant.c:120:         *prev_ind = silk_LIMIT_int( *prev_ind, 0, N_LEVELS_QGAIN - 1 );
	s8i	a13, sp, 12	# %sfp, k
	s32i.n	a4, sp, 8	# %sfp,
	mov.n	a14, a2	# ivtmp$47, gain_Q16
# @OPUS@\upstream\silk\gain_quant.c:104:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a6, 1, .L23	# nb_subfr,,
	mov.n	a12, a13	# k, k
	mov.n	a13, a14	# ivtmp$47, ivtmp$47
	mov.n	a14, a6	# nb_subfr, nb_subfr
.L31:
	l8ui	a2, a15, 0	# *prev_ind_42(D), pretmp_118
# @OPUS@\upstream\silk\gain_quant.c:105:         if( k == 0 && conditional == 0 ) {
	l32i.n	a5, sp, 4	# %sfp,
	slli	a4, a2, 24	# tmp79, pretmp_118,
	or	a3, a5, a12	# tmp80,, k
	srai	a4, a4, 24	# _120, tmp79,
	bnez.n	a3, .L25	# tmp80,
# @OPUS@\upstream\silk\gain_quant.c:107:             *prev_ind = silk_max_int( ind[ k ], *prev_ind - 16 );
	l32i.n	a2, sp, 0	# %sfp,
	addi	a4, a4, -16	# tmp85, _120,
	l8ui	a3, a2, 0	# *ind_41(D),
	slli	a3, a3, 24	# tmp84, *ind_41(D),
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	srai	a3, a3, 24	# tmp81, tmp84,
	bge	a3, a4, .L35	# tmp81, tmp85,
	mov.n	a3, a4	# tmp81, tmp85
	j	.L35		#
.L25:
# @OPUS@\upstream\silk\gain_quant.c:110:             ind_tmp = ind[ k ] + MIN_DELTA_GAIN_QUANT;
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\silk\gain_quant.c:113:             double_step_size_threshold = 2 * MAX_DELTA_GAIN_QUANT - N_LEVELS_QGAIN + *prev_ind;
	addi.n	a4, a4, 8	# double_step_size_threshold, _120,
# @OPUS@\upstream\silk\gain_quant.c:110:             ind_tmp = ind[ k ] + MIN_DELTA_GAIN_QUANT;
	add.n	a3, a5, a12	# tmp86,, k
	l8ui	a9, a3, 0	# MEM[base: _112, offset: 0B], _10
	slli	a8, a9, 24	# tmp88, _10,
	srai	a8, a8, 24	# tmp87, tmp88,
# @OPUS@\upstream\silk\gain_quant.c:110:             ind_tmp = ind[ k ] + MIN_DELTA_GAIN_QUANT;
	addi	a8, a8, -4	# ind_tmp, tmp87,
# @OPUS@\upstream\silk\gain_quant.c:114:             if( ind_tmp > double_step_size_threshold ) {
	bge	a4, a8, .L28	# double_step_size_threshold, ind_tmp,
# @OPUS@\upstream\silk\gain_quant.c:115:                 *prev_ind += silk_LSHIFT( ind_tmp, 1 ) - double_step_size_threshold;
	slli	a3, a8, 1	# tmp90, ind_tmp,
# @OPUS@\upstream\silk\gain_quant.c:115:                 *prev_ind += silk_LSHIFT( ind_tmp, 1 ) - double_step_size_threshold;
	addi	a3, a3, -8	# tmp92, tmp90,
	extui	a3, a3, 0, 8	# _7, tmp92
	j	.L27		#
.L28:
# @OPUS@\upstream\silk\gain_quant.c:117:                 *prev_ind += ind_tmp;
	addi	a3, a2, -4	# tmp94, pretmp_118,
	add.n	a3, a3, a9	# tmp97, tmp94, _10
.L35:
	extui	a3, a3, 0, 8	# _7, tmp97
.L27:
# @OPUS@\upstream\silk\gain_quant.c:120:         *prev_ind = silk_LIMIT_int( *prev_ind, 0, N_LEVELS_QGAIN - 1 );
	slli	a2, a3, 24	# tmp100, _7,
	bgez	a2, .L29	# tmp100,
	l8ui	a3, sp, 12	# %sfp,
.L29:
	slli	a2, a3, 24	# tmp103, _7,
	l32i.n	a4, sp, 8	# %sfp,
	srai	a2, a2, 24	# tmp102, tmp103,
	bge	a4, a2, .L30	#, tmp102,
	movi.n	a3, 0x3f	# _7,
.L30:
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	slli	a4, a3, 24	# tmp108, _7,
	srai	a4, a4, 24	# tmp107, tmp108,
	slli	a8, a4, 3	# tmp121, tmp107,
	mov.n	a2, a4	# tmp109, tmp107
	sub	a4, a8, a4	# tmp122, tmp121, tmp109
	slli	a9, a4, 6	# tmp123, tmp122,
	mov.n	a8, a4	# tmp113, tmp122
	add.n	a4, a4, a9	# tmp124, tmp122, tmp123
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	l32r	a5, .LC5	#,
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	slli	a8, a8, 2	# tmp114, tmp113,
	slli	a4, a4, 4	# tmp125, tmp124,
	add.n	a8, a8, a2	# tmp115, tmp114, tmp109
	add.n	a4, a4, a2	# tmp126, tmp125, tmp109
	srai	a4, a4, 16	# tmp127, tmp126,
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	add.n	a2, a8, a5	# tmp116, tmp115,
# @OPUS@\upstream\silk\gain_quant.c:120:         *prev_ind = silk_LIMIT_int( *prev_ind, 0, N_LEVELS_QGAIN - 1 );
	s8i	a3, a15, 0	# *prev_ind_42(D), _7
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	add.n	a2, a2, a4	#, tmp116, tmp127
	call0	silk_log2lin		#
# @OPUS@\upstream\silk\gain_quant.c:123:         gain_Q16[ k ] = silk_log2lin( silk_min_32( silk_SMULWB( INV_SCALE_Q16, *prev_ind ) + OFFSET, 3967 ) ); /* 3967 = 31 in Q7 */
	s32i.n	a2, a13, 0	# MEM[base: _114, offset: 0B],
# @OPUS@\upstream\silk\gain_quant.c:104:     for( k = 0; k < nb_subfr; k++ ) {
	addi.n	a12, a12, 1	# k, k,
	addi.n	a13, a13, 4	# ivtmp$47, ivtmp$47,
# @OPUS@\upstream\silk\gain_quant.c:104:     for( k = 0; k < nb_subfr; k++ ) {
	bne	a14, a12, .L31	# nb_subfr, k,
.L23:
# @OPUS@\upstream\silk\gain_quant.c:125: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_gains_dequant, .-silk_gains_dequant
	.section	.text.silk_gains_ID,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_gains_ID
	.type	silk_gains_ID, @function
# Function: silk_gains_ID
# Module: upstream/silk/gain_quant.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Compute unique identifier of gain indices vector */
# C context: opus_int32 silk_gains_ID(                                       /* O    returns unique identifier of gains          */
# C context: const opus_int8             ind[ MAX_NB_SUBFR ],            /* I    gain indices                                */
# C context: const opus_int              nb_subfr                        /* I    number of subframes                         */
# C context: )
# C context: {
silk_gains_ID:
# @OPUS@\upstream\silk\gain_quant.c:137:     for( k = 0; k < nb_subfr; k++ ) {
	blti	a3, 1, .L39	# nb_subfr,,
	mov.n	a5, a2	# ivtmp$51, ind
	add.n	a3, a2, a3	# _23, ivtmp$51, nb_subfr
# @OPUS@\upstream\silk\gain_quant.c:136:     gainsID = 0;
	movi.n	a2, 0	# <retval>,
.L38:
# @OPUS@\upstream\silk\gain_quant.c:138:         gainsID = silk_ADD_LSHIFT32( ind[ k ], gainsID, 8 );
	l8ui	a4, a5, 0	# MEM[base: _32, offset: 0B],
	slli	a2, a2, 8	# _7, <retval>,
	slli	a4, a4, 24	# tmp56, MEM[base: _32, offset: 0B],
	srai	a4, a4, 24	# tmp54, tmp56,
	addi.n	a5, a5, 1	# ivtmp$51, ivtmp$51,
# @OPUS@\upstream\silk\gain_quant.c:138:         gainsID = silk_ADD_LSHIFT32( ind[ k ], gainsID, 8 );
	add.n	a2, a4, a2	# <retval>, tmp54, _7
# @OPUS@\upstream\silk\gain_quant.c:137:     for( k = 0; k < nb_subfr; k++ ) {
	bne	a3, a5, .L38	# _23, ivtmp$51,
	j	.L36		#
.L39:
# @OPUS@\upstream\silk\gain_quant.c:136:     gainsID = 0;
	movi.n	a2, 0	# <retval>,
.L36:
# @OPUS@\upstream\silk\gain_quant.c:142: }
	ret.n
	.size	silk_gains_ID, .-silk_gains_ID
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
