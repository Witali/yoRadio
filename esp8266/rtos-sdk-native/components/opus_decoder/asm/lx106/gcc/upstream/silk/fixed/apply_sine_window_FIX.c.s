# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/fixed/apply_sine_window_FIX.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"apply_sine_window_FIX.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\fixed\apply_sine_window_FIX.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\fixed\apply_sine_window_FIX.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\fixed\apply_sine_window_FIX.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\fixed\apply_sine_window_FIX.c.s.raw
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
	.section	.text.silk_apply_sine_window,"ax",@progbits
	.literal_position
	.literal .LC0, 65536
	.literal .LC1, freq_table_Q16
	.align	4
	.global	silk_apply_sine_window
	.type	silk_apply_sine_window, @function
# Function: silk_apply_sine_window
# Module: upstream/silk/fixed/apply_sine_window_FIX.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: 2313,    2214,    2123,    2038,    1961,    1889,    1822,    1760,    1702,
# C context: };
# C context:
# C context: void silk_apply_sine_window(
# C context: opus_int16                  px_win[],           /* O    Pointer to windowed signal                                  */
# C context: const opus_int16            px[],               /* I    Pointer to input signal                                     */
# C context: const opus_int              win_type,           /* I    Selects a window type                                       */
# C context: const opus_int              length              /* I    Window length, multiple of 4                                */
silk_apply_sine_window:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:67:     k = ( length >> 2 ) - 4;
	srai	a6, a5, 2	# tmp137, length,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:69:     f_Q16 = (opus_int)freq_table_Q16[ k ];
	l32r	a7, .LC1	#, tmp136
	addi	a6, a6, -4	# tmp138, tmp137,
	slli	a6, a6, 1	# tmp139, tmp138,
	add.n	a6, a7, a6	# tmp140, tmp136, tmp139
	l16ui	a7, a6, 0	# freq_table_Q16,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:56: {
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:69:     f_Q16 = (opus_int)freq_table_Q16[ k ];
	slli	a7, a7, 16	# tmp142, tmp141,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:72:     c_Q16 = silk_SMULWB( (opus_int32)f_Q16, -f_Q16 );
	srai	a6, a7, 16	# _2, tmp142,
	neg	a9, a7	# tmp145, tmp142
	srai	a9, a9, 16	# _7, tmp145,
	extui	a8, a6, 0, 16	# tmp146, _2,
	mull	a8, a8, a9	# tmp147, tmp146, _7
	srai	a7, a7, 31	# tmp149, tmp142,
	mull	a7, a7, a9	# tmp150, tmp149, _7
	srai	a8, a8, 16	# tmp148, tmp147,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:56: {
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
	s32i.n	a15, sp, 0	#,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:72:     c_Q16 = silk_SMULWB( (opus_int32)f_Q16, -f_Q16 );
	add.n	a8, a8, a7	# c_Q16, tmp148, tmp150
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:76:     if( win_type == 1 ) {
	bnei	a4, 1, .L2	# win_type,,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:80:         S1_Q16 = f_Q16 + silk_RSHIFT( length, 3 );
	srai	a4, a5, 3	# tmp151, length,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:80:         S1_Q16 = f_Q16 + silk_RSHIFT( length, 3 );
	add.n	a6, a4, a6	# S1_Q16, tmp151, _2
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:78:         S0_Q16 = 0;
	movi.n	a4, 0	# S0_Q16,
.L4:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:90:     for( k = 0; k < length; k += 4 ) {
	bgei	a5, 1, .L3	# length,,
	j	.L1		#
.L2:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:85:         S1_Q16 = ( (opus_int32)1 << 16 ) + silk_RSHIFT( c_Q16, 1 ) + silk_RSHIFT( length, 4 );
	l32r	a9, .LC0	#, tmp217
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:85:         S1_Q16 = ( (opus_int32)1 << 16 ) + silk_RSHIFT( c_Q16, 1 ) + silk_RSHIFT( length, 4 );
	srai	a6, a5, 4	# tmp152, length,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:85:         S1_Q16 = ( (opus_int32)1 << 16 ) + silk_RSHIFT( c_Q16, 1 ) + silk_RSHIFT( length, 4 );
	srai	a4, a8, 1	# tmp155, c_Q16,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:85:         S1_Q16 = ( (opus_int32)1 << 16 ) + silk_RSHIFT( c_Q16, 1 ) + silk_RSHIFT( length, 4 );
	add.n	a6, a6, a9	# tmp153, tmp152, tmp217
	add.n	a6, a6, a4	# S1_Q16, tmp153, tmp155
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:83:         S0_Q16 = ( (opus_int32)1 << 16 );
	mov.n	a4, a9	# S0_Q16, tmp217
	j	.L4		#
.L3:
	slli	a8, a8, 16	# tmp156, c_Q16,
	l32r	a9, .LC0	#, tmp217
	srai	a8, a8, 16	# _291, tmp156,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:90:     for( k = 0; k < length; k += 4 ) {
	movi.n	a10, 0	# k,
	movi.n	a11, 1	# tmp177,
.L7:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	l16si	a13, a3, 0	# MEM[base: _327, offset: 0B], _23
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	add.n	a12, a4, a6	# _17, S0_Q16, S1_Q16
	extui	a7, a12, 1, 16	# tmp160, _17,,
	mull	a7, a7, a13	# tmp161, tmp160, _23
	srai	a12, a12, 17	# tmp163, _17,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	mul16s	a12, a12, a13	# tmp164, tmp163, _23
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	srai	a7, a7, 16	# tmp162, tmp161,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	add.n	a7, a7, a12	# tmp167, tmp162, tmp164
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:91:         px_win[ k ]     = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k ] );
	s16i	a7, a2, 0	# MEM[base: _323, offset: 0B], tmp167
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	l16si	a15, a3, 2	# MEM[base: _327, offset: 2B], _38
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	srai	a12, a6, 16	# _33, S1_Q16,
	extui	a7, a6, 0, 16	# _40, S1_Q16,
	mull	a14, a15, a7	# tmp170, _38, _40
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:93:         S0_Q16 = silk_SMULWB( S1_Q16, c_Q16 ) + silk_LSHIFT( S1_Q16, 1 ) - S0_Q16 + 1;
	mull	a13, a12, a8	# tmp176, _33, _291
	mull	a7, a7, a8	# tmp180, _40, _291
	sub	a4, a11, a4	# tmp178, tmp177, S0_Q16
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	mul16s	a12, a12, a15	# tmp172, _33, _38
	add.n	a13, a13, a4	# tmp179, tmp176, tmp178
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	srai	a14, a14, 16	# tmp171, tmp170,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:93:         S0_Q16 = silk_SMULWB( S1_Q16, c_Q16 ) + silk_LSHIFT( S1_Q16, 1 ) - S0_Q16 + 1;
	srai	a7, a7, 16	# tmp181, tmp180,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:93:         S0_Q16 = silk_SMULWB( S1_Q16, c_Q16 ) + silk_LSHIFT( S1_Q16, 1 ) - S0_Q16 + 1;
	slli	a4, a6, 1	# tmp182, S1_Q16,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	add.n	a12, a14, a12	# tmp175, tmp171, tmp172
	add.n	a7, a13, a7	# _101, tmp179, tmp181
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:92:         px_win[ k + 1 ] = (opus_int16)silk_SMULWB( S1_Q16, px[ k + 1] );
	s16i	a12, a2, 2	# MEM[base: _323, offset: 2B], tmp175
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:93:         S0_Q16 = silk_SMULWB( S1_Q16, c_Q16 ) + silk_LSHIFT( S1_Q16, 1 ) - S0_Q16 + 1;
	add.n	a4, a4, a7	# S0_Q16, tmp182, _101
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:90:     for( k = 0; k < length; k += 4 ) {
	addi.n	a10, a10, 4	# k, k,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:94:         S0_Q16 = silk_min( S0_Q16, ( (opus_int32)1 << 16 ) );
	bge	a9, a4, .L5	# tmp217, S0_Q16,
	mov.n	a4, a9	# S0_Q16, tmp217
.L5:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	l16si	a13, a3, 4	# MEM[base: _327, offset: 4B], _64
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	add.n	a12, a4, a6	# _58, S0_Q16, S1_Q16
	extui	a7, a12, 1, 16	# tmp191, _58,,
	mull	a7, a7, a13	# tmp192, tmp191, _64
	srai	a12, a12, 17	# tmp194, _58,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	mul16s	a12, a12, a13	# tmp195, tmp194, _64
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	srai	a7, a7, 16	# tmp193, tmp192,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	add.n	a7, a7, a12	# tmp198, tmp193, tmp195
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:96:         px_win[ k + 2 ] = (opus_int16)silk_SMULWB( silk_RSHIFT( S0_Q16 + S1_Q16, 1 ), px[ k + 2] );
	s16i	a7, a2, 4	# MEM[base: _323, offset: 4B], tmp198
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	l16si	a15, a3, 6	# MEM[base: _327, offset: 6B], _79
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	srai	a12, a4, 16	# _74, S0_Q16,
	extui	a7, a4, 0, 16	# _81, S0_Q16,
	mull	a13, a15, a7	# tmp201, _79, _81
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:98:         S1_Q16 = silk_SMULWB( S0_Q16, c_Q16 ) + silk_LSHIFT( S0_Q16, 1 ) - S1_Q16;
	mull	a14, a12, a8	# tmp209, _74, _291
	mull	a7, a7, a8	# tmp207, _81, _291
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	mul16s	a12, a12, a15	# tmp203, _74, _79
	sub	a14, a14, a6	# tmp210, tmp209, S1_Q16
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	srai	a13, a13, 16	# tmp202, tmp201,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:98:         S1_Q16 = silk_SMULWB( S0_Q16, c_Q16 ) + silk_LSHIFT( S0_Q16, 1 ) - S1_Q16;
	srai	a6, a7, 16	# tmp208, tmp207,
	add.n	a7, a6, a14	# _124, tmp208, tmp210
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	add.n	a12, a13, a12	# tmp206, tmp202, tmp203
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:98:         S1_Q16 = silk_SMULWB( S0_Q16, c_Q16 ) + silk_LSHIFT( S0_Q16, 1 ) - S1_Q16;
	slli	a6, a4, 1	# tmp211, S0_Q16,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:97:         px_win[ k + 3 ] = (opus_int16)silk_SMULWB( S0_Q16, px[ k + 3 ] );
	s16i	a12, a2, 6	# MEM[base: _323, offset: 6B], tmp206
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:98:         S1_Q16 = silk_SMULWB( S0_Q16, c_Q16 ) + silk_LSHIFT( S0_Q16, 1 ) - S1_Q16;
	add.n	a6, a6, a7	# S1_Q16, tmp211, _124
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:99:         S1_Q16 = silk_min( S1_Q16, ( (opus_int32)1 << 16 ) );
	bge	a9, a6, .L6	# tmp217, S1_Q16,
	mov.n	a6, a9	# S1_Q16, tmp217
.L6:
	addi.n	a3, a3, 8	# ivtmp$17, ivtmp$17,
	addi.n	a2, a2, 8	# ivtmp$18, ivtmp$18,
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:90:     for( k = 0; k < length; k += 4 ) {
	blt	a10, a5, .L7	# k, length,
.L1:
# @OPUS@\upstream\silk\fixed\apply_sine_window_FIX.c:101: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	l32i.n	a15, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_apply_sine_window, .-silk_apply_sine_window
	.section	.rodata.freq_table_Q16,"a"
	.align	4
	.type	freq_table_Q16, @object
	.size	freq_table_Q16, 54
freq_table_Q16:
	.short	12111
	.short	9804
	.short	8235
	.short	7100
	.short	6239
	.short	5565
	.short	5022
	.short	4575
	.short	4202
	.short	3885
	.short	3612
	.short	3375
	.short	3167
	.short	2984
	.short	2820
	.short	2674
	.short	2542
	.short	2422
	.short	2313
	.short	2214
	.short	2123
	.short	2038
	.short	1961
	.short	1889
	.short	1822
	.short	1760
	.short	1702
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
