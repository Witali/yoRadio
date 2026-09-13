# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/shell_coder.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"shell_coder.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\shell_coder.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\shell_coder.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\shell_coder.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\shell_coder.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\shell_coder.c.s.raw
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
	.section	.text.silk_shell_encoder,"ax",@progbits
	.literal_position
	.literal .LC0, silk_shell_code_table_offsets
	.literal .LC1, silk_shell_code_table3
	.literal .LC2, silk_shell_code_table2
	.literal .LC3, silk_shell_code_table1
	.literal .LC4, silk_shell_code_table0
	.align	4
	.global	silk_shell_encoder
	.type	silk_shell_encoder, @function
# Function: silk_shell_encoder
# Module: upstream/silk/shell_coder.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Shell encoder, operates on one shell code frame of 16 pulses */
# C context: void silk_shell_encoder(
# C context: ec_enc                      *psRangeEnc,                    /* I/O  compressor data structure                   */
# C context: const opus_int              *pulses0                        /* I    data: nonnegative pulse amplitudes          */
# C context: )
# C context: {
silk_shell_encoder:
	addi	sp, sp, -112	#,,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	l32i.n	a10, a3, 24	# MEM[(const int *)pulses0_25(D) + 24B], MEM[(const int *)pulses0_25(D) + 24B]
	l32i.n	a4, a3, 40	# MEM[(const int *)pulses0_25(D) + 40B], MEM[(const int *)pulses0_25(D) + 40B]
	l32i.n	a6, a3, 4	# MEM[(const int *)pulses0_25(D) + 4B], MEM[(const int *)pulses0_25(D) + 4B]
	l32i.n	a7, a3, 0	# *pulses0_25(D), *pulses0_25(D)
	l32i.n	a8, a3, 8	# MEM[(const int *)pulses0_25(D) + 8B], MEM[(const int *)pulses0_25(D) + 8B]
	l32i.n	a11, a3, 16	# MEM[(const int *)pulses0_25(D) + 16B], MEM[(const int *)pulses0_25(D) + 16B]
	l32i.n	a9, a3, 28	# MEM[(const int *)pulses0_25(D) + 28B], MEM[(const int *)pulses0_25(D) + 28B]
	l32i.n	a5, a3, 36	# MEM[(const int *)pulses0_25(D) + 36B], MEM[(const int *)pulses0_25(D) + 36B]
# @OPUS@\upstream\silk\shell_coder.c:82: {
	s32i	a12, sp, 104	#,
	s32i	a13, sp, 100	#,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	l32i.n	a12, a3, 12	# MEM[(const int *)pulses0_25(D) + 12B], MEM[(const int *)pulses0_25(D) + 12B]
# @OPUS@\upstream\silk\shell_coder.c:82: {
	mov.n	a13, a3	# pulses0, pulses0
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	l32i.n	a14, a3, 32	# MEM[(const int *)pulses0_25(D) + 32B], MEM[(const int *)pulses0_25(D) + 32B]
	l32i.n	a15, a3, 20	# MEM[(const int *)pulses0_25(D) + 20B], MEM[(const int *)pulses0_25(D) + 20B]
	l32i.n	a3, a3, 44	# MEM[(const int *)pulses0_25(D) + 44B], MEM[(const int *)pulses0_25(D) + 44B]
	add.n	a9, a10, a9	#, MEM[(const int *)pulses0_25(D) + 24B], MEM[(const int *)pulses0_25(D) + 28B]
	add.n	a3, a4, a3	#, MEM[(const int *)pulses0_25(D) + 40B], MEM[(const int *)pulses0_25(D) + 44B]
	s32i.n	a3, sp, 52	# %sfp,
	l32i.n	a4, a13, 52	# MEM[(const int *)pulses0_25(D) + 52B],
	l32i.n	a3, a13, 48	# MEM[(const int *)pulses0_25(D) + 48B],
	s32i.n	a9, sp, 48	# %sfp,
	add.n	a3, a3, a4	#,,
	s32i.n	a3, sp, 32	# %sfp,
	l32i.n	a4, a13, 60	# MEM[(const int *)pulses0_25(D) + 60B],
	l32i.n	a3, a13, 56	# MEM[(const int *)pulses0_25(D) + 56B],
	add.n	a15, a15, a11	# _99, MEM[(const int *)pulses0_25(D) + 20B], MEM[(const int *)pulses0_25(D) + 16B]
	add.n	a3, a3, a4	#,,
	s32i.n	a3, sp, 36	# %sfp,
	l32i.n	a4, sp, 52	# %sfp,
	l32i.n	a3, sp, 48	# %sfp,
	add.n	a14, a14, a5	# _23, MEM[(const int *)pulses0_25(D) + 32B], MEM[(const int *)pulses0_25(D) + 36B]
	add.n	a3, a15, a3	#, _99,
	add.n	a4, a14, a4	#, _23,
	s32i.n	a3, sp, 56	# %sfp,
	s32i.n	a4, sp, 40	# %sfp,
	l32i.n	a3, sp, 32	# %sfp,
	l32i.n	a4, sp, 36	# %sfp,
	add.n	a8, a12, a8	# _232, MEM[(const int *)pulses0_25(D) + 12B], MEM[(const int *)pulses0_25(D) + 8B]
	add.n	a3, a3, a4	#,,
	add.n	a7, a6, a7	# _176, MEM[(const int *)pulses0_25(D) + 4B], *pulses0_25(D)
# @OPUS@\upstream\silk\shell_coder.c:82: {
	s32i	a0, sp, 108	#,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	s32i.n	a3, sp, 60	# %sfp,
	l32i.n	a3, sp, 56	# %sfp,
	add.n	a9, a7, a8	# _205, _176, _232
	add.n	a10, a9, a3	# _175, _205,
	l32i.n	a4, sp, 40	# %sfp,
	l32i.n	a3, sp, 60	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	s32i.n	a7, sp, 0	# MEM[(int *)&pulses1], _176
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	add.n	a4, a4, a3	#,,
	s32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	l32i.n	a4, sp, 48	# %sfp,
	l32i.n	a3, sp, 52	# %sfp,
	s32i.n	a4, sp, 12	# MEM[(int *)&pulses1 + 12B],
	l32i.n	a4, sp, 32	# %sfp,
	s32i.n	a3, sp, 20	# MEM[(int *)&pulses1 + 20B],
	s32i.n	a4, sp, 24	# MEM[(int *)&pulses1 + 24B],
	l32i.n	a3, sp, 36	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	s32i.n	a3, sp, 28	# MEM[(int *)&pulses1 + 28B],
	s32i.n	a8, sp, 4	# MEM[(int *)&pulses1 + 4B], _232
	s32i.n	a15, sp, 8	# MEM[(int *)&pulses1 + 8B], _99
	s32i.n	a14, sp, 16	# MEM[(int *)&pulses1 + 16B], _23
# @OPUS@\upstream\silk\shell_coder.c:44:         out[ k ] = in[ 2 * k ] + in[ 2 * k + 1 ];
	add.n	a3, a10, a4	# _107, _175,
# @OPUS@\upstream\silk\shell_coder.c:82: {
	mov.n	a12, a2	# psRangeEnc, psRangeEnc
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a3, 1, .L2	# _107,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp144
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC1	#, tmp148
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a3, a2, a3	# tmp145, tmp144, _107
	l8ui	a2, a3, 0	# silk_shell_code_table_offsets, tmp146
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a5, 8	#,
	add.n	a4, a4, a2	#, tmp148, tmp146
	mov.n	a3, a10	#, _175
	mov.n	a2, a12	#, psRangeEnc
	s32i	a7, sp, 72	#,
	s32i	a8, sp, 76	#,
	s32i	a9, sp, 68	#,
	s32i	a10, sp, 64	#,
	call0	ec_enc_icdf		#
	l32i	a10, sp, 64	#,
	l32i	a9, sp, 68	#,
	l32i	a8, sp, 76	#,
	l32i	a7, sp, 72	#,
.L2:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a10, 1, .L3	# _175,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp149
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC2	#, tmp153
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a10, a2, a10	# tmp150, tmp149, _175
	l8ui	a2, a10, 0	# silk_shell_code_table_offsets, tmp151
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	mov.n	a3, a9	#, _205
	add.n	a4, a4, a2	#, tmp153, tmp151
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	s32i	a7, sp, 72	#,
	s32i	a8, sp, 76	#,
	s32i	a9, sp, 68	#,
	call0	ec_enc_icdf		#
	l32i	a9, sp, 68	#,
	l32i	a8, sp, 76	#,
	l32i	a7, sp, 72	#,
.L3:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a9, 1, .L4	# _205,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp154
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC3	#, tmp158
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a9, a2, a9	# tmp155, tmp154, _205
	l8ui	a2, a9, 0	# silk_shell_code_table_offsets, tmp156
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	mov.n	a3, a7	#, _176
	add.n	a4, a4, a2	#, tmp158, tmp156
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	s32i	a7, sp, 72	#,
	s32i	a8, sp, 76	#,
	call0	ec_enc_icdf		#
	l32i	a8, sp, 76	#,
	l32i	a7, sp, 72	#,
.L4:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a7, 1, .L5	# _176,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp159
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp163
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a7, a2, a7	# tmp160, tmp159, _176
	l8ui	a2, a7, 0	# silk_shell_code_table_offsets, tmp161
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 0	# *pulses0_25(D),
	add.n	a4, a4, a2	#, tmp163, tmp161
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	s32i	a8, sp, 76	#,
	call0	ec_enc_icdf		#
	l32i	a8, sp, 76	#,
.L5:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a8, 1, .L6	# _232,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp164
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp168
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a8, a2, a8	# tmp165, tmp164, _232
	l8ui	a2, a8, 0	# silk_shell_code_table_offsets, tmp166
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 8	# MEM[(const int *)pulses0_25(D) + 8B],
	add.n	a4, a4, a2	#, tmp168, tmp166
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L6:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a2, sp, 56	# %sfp,
	blti	a2, 1, .L7	#,,
	mov.n	a3, a2	#,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp169
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC3	#, tmp173
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a3	# tmp170, tmp169,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp171
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a5, 8	#,
	add.n	a4, a4, a2	#, tmp173, tmp171
	mov.n	a3, a15	#, _99
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L7:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a15, 1, .L8	# _99,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp174
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp178
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a15, a2, a15	# tmp175, tmp174, _99
	l8ui	a2, a15, 0	# silk_shell_code_table_offsets, tmp176
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 16	# MEM[(const int *)pulses0_25(D) + 16B],
	add.n	a4, a4, a2	#, tmp178, tmp176
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L8:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a4, sp, 48	# %sfp,
	blti	a4, 1, .L9	#,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp179
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 24	# MEM[(const int *)pulses0_25(D) + 24B],
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a4	# tmp180, tmp179,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp181
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp183
	movi.n	a5, 8	#,
	add.n	a4, a4, a2	#, tmp183, tmp181
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L9:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a2, sp, 44	# %sfp,
	blti	a2, 1, .L10	#,,
	mov.n	a3, a2	#,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp184
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC2	#, tmp188
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a3	# tmp185, tmp184,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp186
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, sp, 40	# %sfp,
	add.n	a4, a4, a2	#, tmp188, tmp186
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L10:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a4, sp, 40	# %sfp,
	blti	a4, 1, .L11	#,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp189
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a5, 8	#,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a4	# tmp190, tmp189,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp191
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC3	#, tmp193
	mov.n	a3, a14	#, _23
	add.n	a4, a4, a2	#, tmp193, tmp191
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L11:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	blti	a14, 1, .L12	# _23,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp194
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp198
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a14, a2, a14	# tmp195, tmp194, _23
	l8ui	a2, a14, 0	# silk_shell_code_table_offsets, tmp196
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 32	# MEM[(const int *)pulses0_25(D) + 32B],
	add.n	a4, a4, a2	#, tmp198, tmp196
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L12:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a2, sp, 52	# %sfp,
	blti	a2, 1, .L13	#,,
	mov.n	a3, a2	#,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp199
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp203
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a3	# tmp200, tmp199,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp201
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 40	# MEM[(const int *)pulses0_25(D) + 40B],
	add.n	a4, a4, a2	#, tmp203, tmp201
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L13:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a4, sp, 60	# %sfp,
	blti	a4, 1, .L14	#,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp204
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a4	# tmp205, tmp204,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp206
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC3	#, tmp208
	movi.n	a5, 8	#,
	add.n	a4, a4, a2	#, tmp208, tmp206
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L14:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a2, sp, 32	# %sfp,
	blti	a2, 1, .L15	#,,
	mov.n	a3, a2	#,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp209
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp213
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a3	# tmp210, tmp209,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp211
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 48	# MEM[(const int *)pulses0_25(D) + 48B],
	add.n	a4, a4, a2	#, tmp213, tmp211
	movi.n	a5, 8	#,
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L15:
# @OPUS@\upstream\silk\shell_coder.c:55:     if( p > 0 ) {
	l32i.n	a4, sp, 36	# %sfp,
	blti	a4, 1, .L1	#,,
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a2, .LC0	#, tmp214
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32i.n	a3, a13, 56	# MEM[(const int *)pulses0_25(D) + 56B],
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a2, a4	# tmp215, tmp214,
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp216
# @OPUS@\upstream\silk\shell_coder.c:56:         ec_enc_icdf( psRangeEnc, p_child1, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a4, .LC4	#, tmp218
	movi.n	a5, 8	#,
	add.n	a4, a4, a2	#, tmp218, tmp216
	mov.n	a2, a12	#, psRangeEnc
	call0	ec_enc_icdf		#
.L1:
# @OPUS@\upstream\silk\shell_coder.c:115: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	silk_shell_encoder, .-silk_shell_encoder
	.section	.text.silk_shell_decoder,"ax",@progbits
	.literal_position
	.literal .LC5, silk_shell_code_table_offsets
	.literal .LC6, silk_shell_code_table3
	.literal .LC7, silk_shell_code_table2
	.literal .LC8, silk_shell_code_table1
	.literal .LC9, silk_shell_code_table0
	.align	4
	.global	silk_shell_decoder
	.type	silk_shell_decoder, @function
# Function: silk_shell_decoder
# Module: upstream/silk/shell_coder.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context:
# C context: /* Shell decoder, operates on one shell code frame of 16 pulses */
# C context: void silk_shell_decoder(
# C context: opus_int16                  *pulses0,                       /* O    data: nonnegative pulse amplitudes          */
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: const opus_int              pulses4                         /* I    number of pulses per pulse-subframe         */
# C context: )
silk_shell_decoder:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a15, sp, 44	#,
	s32i.n	a0, sp, 60	#,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	movi.n	a15, 0	# prephitmp_22,
# @OPUS@\upstream\silk\shell_coder.c:124: {
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\silk\shell_coder.c:124: {
	s32i.n	a3, sp, 0	# %sfp, psRangeDec
	mov.n	a6, a4	# pulses4, pulses4
	mov.n	a13, a2	# pulses0, pulses0
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	mov.n	a12, a15	# pulses3$2, prephitmp_22
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a4, 1, .L19	# pulses4,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a14, .LC5	#, tmp150
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC6	#, tmp154
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a4	# tmp151, tmp150, pulses4
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp152
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp154, tmp152
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a6, sp, 16	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp155,,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	srai	a15, a2, 16	# _115, tmp155,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a12, a6, a15	# tmp157, pulses4, _115
	slli	a12, a12, 16	# tmp158, tmp157,
	srai	a12, a12, 16	# pulses3$2, tmp158,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a15, 1, .L20	# _115,,
	mov.n	a15, a12	# prephitmp_22, pulses3$2
	j	.L19		#
.L20:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a15	# tmp160, tmp150, _115
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp161
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC7	#, tmp163
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp163, tmp161
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp164,,
	srai	a6, a2, 16	# _122, tmp164,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a15, a15, a6	# tmp165, _115, _122
	slli	a15, a15, 16	# tmp166, tmp165,
	srai	a2, a15, 16	#, tmp166,
	s32i.n	a2, sp, 4	# %sfp,
	mov.n	a15, a12	# prephitmp_22, pulses3$2
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a6, 1, .L21	# _122,,
	j	.L48		#
.L19:
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	movi.n	a7, 0	# prephitmp_34,
	s32i.n	a7, sp, 4	# %sfp, prephitmp_34
	j	.L23		#
.L21:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a6	# tmp168, tmp150, _122
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp169
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC8	#, tmp171
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp171, tmp169
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a6, sp, 16	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp172,,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	srai	a8, a2, 16	# _129, tmp172,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a6, a6, a8	# tmp173, _122, _129
	slli	a6, a6, 16	# tmp174, tmp173,
	srai	a6, a6, 16	# pulses1$2, tmp174,
	l32i.n	a7, sp, 4	# %sfp, prephitmp_34
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a8, 1, .L24	# _129,,
	j	.L49		#
.L48:
	l32i.n	a7, sp, 4	# %sfp, prephitmp_34
.L23:
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	movi.n	a2, 0	# prephitmp_16,
	mov.n	a6, a2	# pulses1$2, prephitmp_16
	j	.L26		#
.L24:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a14, a14, a8	# tmp176, tmp150, _129
	l8ui	a2, a14, 0	# silk_shell_code_table_offsets, tmp177
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp179
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp179, tmp177
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a6, sp, 16	#,
	s32i.n	a7, sp, 12	#,
	s32i.n	a8, sp, 8	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a8, sp, 8	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp180,,
	srai	a2, a2, 16	# _136, tmp180,
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a8, a8, a2	# tmp181, _129, _136
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 0	# *pulses0_47(D), _136
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a8, a13, 2	# MEM[(opus_int16 *)pulses0_47(D) + 2B], tmp181
	mov.n	a2, a6	# prephitmp_16, pulses1$2
	l32i.n	a7, sp, 12	#,
	j	.L27		#
.L49:
	mov.n	a2, a6	# prephitmp_16, pulses1$2
.L26:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a3, 0	# tmp182,
	s16i	a3, a13, 0	# *pulses0_47(D), tmp182
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a3, a13, 2	# MEM[(opus_int16 *)pulses0_47(D) + 2B], tmp182
.L27:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a2, 1, .L28	# prephitmp_16,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC5	#, tmp184
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a3, a2	# tmp185, tmp184, prephitmp_16
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp186
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp188
	s32i.n	a6, sp, 16	#,
	add.n	a3, a3, a2	#, tmp188, tmp186
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a7, sp, 12	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp189,,
	srai	a2, a2, 16	# _143, tmp189,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a6, a6, a2	# tmp190, pulses1$2, _143
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 4	# MEM[(opus_int16 *)pulses0_47(D) + 4B], _143
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a6, a13, 6	# MEM[(opus_int16 *)pulses0_47(D) + 6B], tmp190
	l32i.n	a7, sp, 12	#,
	j	.L29		#
.L28:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp191,
	s16i	a2, a13, 4	# MEM[(opus_int16 *)pulses0_47(D) + 4B], tmp191
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 6	# MEM[(opus_int16 *)pulses0_47(D) + 6B], tmp191
.L29:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a7, 1, .L30	# prephitmp_34,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a14, .LC5	#, tmp289
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC8	#, tmp197
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a7	# tmp194, tmp289, prephitmp_34
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp195
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp197, tmp195
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp198,,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a3, sp, 4	# %sfp,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	srai	a6, a2, 16	# _150, tmp198,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a2, a3, a6	# tmp199,, _150
	slli	a2, a2, 16	# tmp200, tmp199,
	srai	a7, a2, 16	# _152, tmp200,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a6, 1, .L31	# _150,,
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp201,
	s16i	a2, a13, 8	# MEM[(opus_int16 *)pulses0_47(D) + 8B], tmp201
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 10	# MEM[(opus_int16 *)pulses0_47(D) + 10B], tmp201
	j	.L32		#
.L31:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a6	# tmp204, tmp289, _150
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp205
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp207
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp207, tmp205
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a6, sp, 16	#,
	s32i.n	a7, sp, 12	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp208,,
	srai	a2, a2, 16	# _157, tmp208,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a6, a6, a2	# tmp209, _150, _157
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 8	# MEM[(opus_int16 *)pulses0_47(D) + 8B], _157
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a6, a13, 10	# MEM[(opus_int16 *)pulses0_47(D) + 10B], tmp209
	l32i.n	a7, sp, 12	#,
	j	.L32		#
.L30:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp210,
	s16i	a2, a13, 8	# MEM[(opus_int16 *)pulses0_47(D) + 8B], tmp210
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 10	# MEM[(opus_int16 *)pulses0_47(D) + 10B], tmp210
	j	.L33		#
.L32:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a7, 1, .L33	# _152,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a14, a14, a7	# tmp213, tmp289, _152
	l8ui	a2, a14, 0	# silk_shell_code_table_offsets, tmp214
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp216
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp216, tmp214
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a7, sp, 12	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a7, sp, 12	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp217,,
	srai	a3, a2, 16	# _164, tmp217,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a2, a7, a3	# tmp218, _152, _164
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a3, a13, 12	# MEM[(opus_int16 *)pulses0_47(D) + 12B], _164
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a2, a13, 14	# MEM[(opus_int16 *)pulses0_47(D) + 14B], tmp218
	j	.L34		#
.L33:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp219,
	s16i	a2, a13, 12	# MEM[(opus_int16 *)pulses0_47(D) + 12B], tmp219
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 14	# MEM[(opus_int16 *)pulses0_47(D) + 14B], tmp219
.L34:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a15, 1, .L35	# prephitmp_22,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a14, .LC5	#, tmp289
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC7	#, tmp225
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a15, a14, a15	# tmp222, tmp289, prephitmp_22
	l8ui	a2, a15, 0	# silk_shell_code_table_offsets, tmp223
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp225, tmp223
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp226,,
	srai	a15, a2, 16	# _171, tmp226,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a12, a12, a15	# tmp227, pulses3$2, _171
	slli	a12, a12, 16	# tmp228, tmp227,
	srai	a12, a12, 16	# _173, tmp228,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a15, 1, .L36	# _171,,
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp229,
	s16i	a2, a13, 16	# MEM[(opus_int16 *)pulses0_47(D) + 16B], tmp229
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 18	# MEM[(opus_int16 *)pulses0_47(D) + 18B], tmp229
	j	.L37		#
.L36:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a15	# tmp232, tmp289, _171
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp233
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC8	#, tmp235
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp235, tmp233
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp236,,
	srai	a6, a2, 16	# _178, tmp236,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a15, a15, a6	# tmp237, _171, _178
	slli	a15, a15, 16	# tmp238, tmp237,
	srai	a15, a15, 16	# _180, tmp238,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a6, 1, .L38	# _178,,
	j	.L50		#
.L35:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp239,
	s16i	a2, a13, 16	# MEM[(opus_int16 *)pulses0_47(D) + 16B], tmp239
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 18	# MEM[(opus_int16 *)pulses0_47(D) + 18B], tmp239
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	s16i	a2, a13, 20	# MEM[(opus_int16 *)pulses0_47(D) + 20B], tmp239
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 22	# MEM[(opus_int16 *)pulses0_47(D) + 22B], tmp239
	j	.L40		#
.L38:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a6	# tmp244, tmp289, _178
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp245
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp247
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp247, tmp245
	l32i.n	a2, sp, 0	# %sfp,
	s32i.n	a6, sp, 16	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	l32i.n	a6, sp, 16	#,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp248,,
	srai	a2, a2, 16	# _185, tmp248,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a6, a6, a2	# tmp249, _178, _185
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 16	# MEM[(opus_int16 *)pulses0_47(D) + 16B], _185
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a6, a13, 18	# MEM[(opus_int16 *)pulses0_47(D) + 18B], tmp249
	j	.L41		#
.L50:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp250,
	s16i	a2, a13, 16	# MEM[(opus_int16 *)pulses0_47(D) + 16B], tmp250
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 18	# MEM[(opus_int16 *)pulses0_47(D) + 18B], tmp250
.L41:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a15, 1, .L37	# _180,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a15	# tmp253, tmp289, _180
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp254
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp256
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp256, tmp254
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp257,,
	srai	a2, a2, 16	# _192, tmp257,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a15, a15, a2	# tmp258, _180, _192
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 20	# MEM[(opus_int16 *)pulses0_47(D) + 20B], _192
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a15, a13, 22	# MEM[(opus_int16 *)pulses0_47(D) + 22B], tmp258
	j	.L42		#
.L37:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp259,
	s16i	a2, a13, 20	# MEM[(opus_int16 *)pulses0_47(D) + 20B], tmp259
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 22	# MEM[(opus_int16 *)pulses0_47(D) + 22B], tmp259
.L42:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a12, 1, .L40	# _173,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a12	# tmp262, tmp289, _173
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp263
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC8	#, tmp265
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp265, tmp263
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp266,,
	srai	a15, a2, 16	# _199, tmp266,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a12, a12, a15	# tmp267, _173, _199
	slli	a12, a12, 16	# tmp268, tmp267,
	srai	a12, a12, 16	# _201, tmp268,
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	bgei	a15, 1, .L43	# _199,,
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp269,
	s16i	a2, a13, 24	# MEM[(opus_int16 *)pulses0_47(D) + 24B], tmp269
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 26	# MEM[(opus_int16 *)pulses0_47(D) + 26B], tmp269
	j	.L44		#
.L43:
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a2, a14, a15	# tmp272, tmp289, _199
	l8ui	a2, a2, 0	# silk_shell_code_table_offsets, tmp273
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp275
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp275, tmp273
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp276,,
	srai	a2, a2, 16	# _206, tmp276,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a3, a15, a2	# tmp277, _199, _206
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 24	# MEM[(opus_int16 *)pulses0_47(D) + 24B], _206
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a3, a13, 26	# MEM[(opus_int16 *)pulses0_47(D) + 26B], tmp277
	j	.L44		#
.L40:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp278,
	s16i	a2, a13, 24	# MEM[(opus_int16 *)pulses0_47(D) + 24B], tmp278
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 26	# MEM[(opus_int16 *)pulses0_47(D) + 26B], tmp278
	j	.L45		#
.L44:
# @OPUS@\upstream\silk\shell_coder.c:68:     if( p > 0 ) {
	blti	a12, 1, .L45	# _201,,
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	add.n	a14, a14, a12	# tmp281, tmp289, _201
	l8ui	a2, a14, 0	# silk_shell_code_table_offsets, tmp282
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	l32r	a3, .LC9	#, tmp284
	movi.n	a4, 8	#,
	add.n	a3, a3, a2	#, tmp284, tmp282
	l32i.n	a2, sp, 0	# %sfp,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	slli	a2, a2, 16	# tmp285,,
	srai	a2, a2, 16	# _213, tmp285,
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	sub	a12, a12, a2	# tmp286, _201, _213
# @OPUS@\upstream\silk\shell_coder.c:69:         p_child1[ 0 ] = ec_dec_icdf( psRangeDec, &shell_table[ silk_shell_code_table_offsets[ p ] ], 8 );
	s16i	a2, a13, 28	# MEM[(opus_int16 *)pulses0_47(D) + 28B], _213
# @OPUS@\upstream\silk\shell_coder.c:70:         p_child2[ 0 ] = p - p_child1[ 0 ];
	s16i	a12, a13, 30	# MEM[(opus_int16 *)pulses0_47(D) + 30B], tmp286
	j	.L18		#
.L45:
# @OPUS@\upstream\silk\shell_coder.c:72:         p_child1[ 0 ] = 0;
	movi.n	a2, 0	# tmp287,
	s16i	a2, a13, 28	# MEM[(opus_int16 *)pulses0_47(D) + 28B], tmp287
# @OPUS@\upstream\silk\shell_coder.c:73:         p_child2[ 0 ] = 0;
	s16i	a2, a13, 30	# MEM[(opus_int16 *)pulses0_47(D) + 30B], tmp287
.L18:
# @OPUS@\upstream\silk\shell_coder.c:151: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_shell_decoder, .-silk_shell_decoder
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
