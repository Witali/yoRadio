# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/encode_pulses.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"encode_pulses.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\encode_pulses.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\encode_pulses.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\encode_pulses.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\encode_pulses.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\encode_pulses.c.s.raw
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
	.section	.text.silk_encode_pulses,"ax",@progbits
	.literal_position
	.literal .LC0, 2147483647
	.literal .LC1, silk_max_pulses_table
	.literal .LC2, silk_pulses_per_block_BITS_Q5
	.literal .LC3, silk_rate_levels_BITS_Q5
	.literal .LC4, silk_rate_levels_iCDF
	.literal .LC5, silk_pulses_per_block_iCDF
	.literal .LC6, silk_pulses_per_block_iCDF+162
	.literal .LC7, silk_lsb_iCDF
	.align	4
	.global	silk_encode_pulses
	.type	silk_encode_pulses, @function
# Function: silk_encode_pulses
# Module: upstream/silk/encode_pulses.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Encode quantization indices of excitation */
# C context: void silk_encode_pulses(
# C context: ec_enc                      *psRangeEnc,                    /* I/O  compressor data structure                   */
# C context: const opus_int              signalType,                     /* I    Signal type                                 */
# C context: const opus_int              quantOffsetType,                /* I    quantOffsetType                             */
# C context: opus_int8                   pulses[],                       /* I    quantization indices                        */
silk_encode_pulses:
	movi	a9, 0xe0	#,
	sub	sp, sp, a9	#,,
	s32i	a6, sp, 176	# %sfp, frame_length
# @OPUS@\upstream\silk\encode_pulses.c:87:     iter = silk_RSHIFT( frame_length, LOG2_SHELL_CODEC_FRAME_LENGTH );
	srai	a6, a6, 4	#, frame_length,
# @OPUS@\upstream\silk\encode_pulses.c:67: {
	s32i	a12, sp, 216	#,
	s32i	a5, sp, 172	# %sfp, pulses
	s32i	a0, sp, 220	#,
	s32i	a13, sp, 212	#,
	s32i	a14, sp, 208	#,
	s32i	a15, sp, 204	#,
# @OPUS@\upstream\silk\encode_pulses.c:67: {
	s32i	a2, sp, 160	# %sfp, psRangeEnc
	s32i	a3, sp, 180	# %sfp, signalType
	s32i	a4, sp, 184	# %sfp, quantOffsetType
# @OPUS@\upstream\silk\encode_pulses.c:87:     iter = silk_RSHIFT( frame_length, LOG2_SHELL_CODEC_FRAME_LENGTH );
	s32i	a6, sp, 148	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:78:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\encode_pulses.c:88:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	l32i	a7, sp, 148	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:80:     silk_memset( pulses_comb, 0, 8 * sizeof( opus_int ) ); /* Fixing Valgrind reported problem*/
	movi.n	a5, 0	# tmp238,
# @OPUS@\upstream\silk\encode_pulses.c:88:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	l32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:78:     SAVE_STACK;
	s32i.n	a2, sp, 32	# _saved_stack,
	s32i.n	a3, sp, 36	# _saved_stack,
# @OPUS@\upstream\silk\encode_pulses.c:80:     silk_memset( pulses_comb, 0, 8 * sizeof( opus_int ) ); /* Fixing Valgrind reported problem*/
	s32i.n	a5, sp, 0	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 4	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 8	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 12	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 16	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 20	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 24	# MEM[(void *)&pulses_comb], tmp238
	s32i.n	a5, sp, 28	# MEM[(void *)&pulses_comb], tmp238
# @OPUS@\upstream\silk\encode_pulses.c:88:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	slli	a12, a7, 4	# _1,,
# @OPUS@\upstream\silk\encode_pulses.c:88:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	bge	a12, a8, .L2	# _1,,
# @OPUS@\upstream\silk\encode_pulses.c:91:         silk_memset( &pulses[ frame_length ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof(opus_int8));
	l32i	a9, sp, 172	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:90:         iter++;
	addi.n	a7, a7, 1	#,,
# @OPUS@\upstream\silk\encode_pulses.c:91:         silk_memset( &pulses[ frame_length ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof(opus_int8));
	movi.n	a4, 0x10	#,
	mov.n	a3, a5	#, tmp238
	add.n	a2, a9, a8	#,,
# @OPUS@\upstream\silk\encode_pulses.c:90:         iter++;
	s32i	a7, sp, 148	# %sfp,
	addi	a12, a12, 16	# _1, _1,
# @OPUS@\upstream\silk\encode_pulses.c:91:         silk_memset( &pulses[ frame_length ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof(opus_int8));
	call0	memset		#
.L2:
# @OPUS@\upstream\silk\encode_pulses.c:95:     ALLOC( abs_pulses, iter * SHELL_CODEC_FRAME_LENGTH, opus_int );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	mov.n	a2, a12	#, _1
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 168	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:97:     for( i = 0; i < iter * SHELL_CODEC_FRAME_LENGTH; i+=4 ) {
	bgei	a12, 1, .L3	# _1,,
.L7:
# @OPUS@\upstream\silk\encode_pulses.c:105:     ALLOC( sum_pulses, iter, opus_int );
	l32i	a2, sp, 148	# %sfp,
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 156	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:106:     ALLOC( nRshifts, iter, opus_int );
	l32i	a2, sp, 148	# %sfp,
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\encode_pulses.c:108:     for( i = 0; i < iter; i++ ) {
	l32i	a12, sp, 148	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:106:     ALLOC( nRshifts, iter, opus_int );
	s32i	a2, sp, 144	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:108:     for( i = 0; i < iter; i++ ) {
	bgei	a12, 1, .L4	#,,
	slli	a6, a12, 2	#,,
	s32i	a6, sp, 164	# %sfp,
	j	.L8		#
.L3:
	slli	a5, a12, 2	# tmp251, _1,
	l32i	a4, sp, 172	# %sfp, ivtmp$100
	mov.n	a3, a2	# ivtmp$101,
	add.n	a5, a2, a5	# _507, ivtmp$101, tmp251
.L6:
# @OPUS@\upstream\silk\encode_pulses.c:98:         abs_pulses[i+0] = ( opus_int )silk_abs( pulses[ i + 0 ] );
	l8ui	a2, a4, 0	# MEM[base: _616, offset: 0B],
	slli	a2, a2, 24	# tmp256, MEM[base: _616, offset: 0B],
	srai	a2, a2, 24	# tmp254, tmp256,
# @OPUS@\upstream\silk\encode_pulses.c:98:         abs_pulses[i+0] = ( opus_int )silk_abs( pulses[ i + 0 ] );
	abs	a2, a2	# tmp257, tmp254
# @OPUS@\upstream\silk\encode_pulses.c:98:         abs_pulses[i+0] = ( opus_int )silk_abs( pulses[ i + 0 ] );
	s32i.n	a2, a3, 0	# MEM[base: _548, offset: 0B], tmp257
# @OPUS@\upstream\silk\encode_pulses.c:99:         abs_pulses[i+1] = ( opus_int )silk_abs( pulses[ i + 1 ] );
	l8ui	a2, a4, 1	# MEM[base: _616, offset: 1B],
	slli	a2, a2, 24	# tmp260, MEM[base: _616, offset: 1B],
	srai	a2, a2, 24	# tmp258, tmp260,
# @OPUS@\upstream\silk\encode_pulses.c:99:         abs_pulses[i+1] = ( opus_int )silk_abs( pulses[ i + 1 ] );
	abs	a2, a2	# tmp261, tmp258
# @OPUS@\upstream\silk\encode_pulses.c:99:         abs_pulses[i+1] = ( opus_int )silk_abs( pulses[ i + 1 ] );
	s32i.n	a2, a3, 4	# MEM[base: _548, offset: 4B], tmp261
# @OPUS@\upstream\silk\encode_pulses.c:100:         abs_pulses[i+2] = ( opus_int )silk_abs( pulses[ i + 2 ] );
	l8ui	a2, a4, 2	# MEM[base: _616, offset: 2B],
	slli	a2, a2, 24	# tmp264, MEM[base: _616, offset: 2B],
	srai	a2, a2, 24	# tmp262, tmp264,
# @OPUS@\upstream\silk\encode_pulses.c:100:         abs_pulses[i+2] = ( opus_int )silk_abs( pulses[ i + 2 ] );
	abs	a2, a2	# tmp265, tmp262
# @OPUS@\upstream\silk\encode_pulses.c:100:         abs_pulses[i+2] = ( opus_int )silk_abs( pulses[ i + 2 ] );
	s32i.n	a2, a3, 8	# MEM[base: _548, offset: 8B], tmp265
# @OPUS@\upstream\silk\encode_pulses.c:101:         abs_pulses[i+3] = ( opus_int )silk_abs( pulses[ i + 3 ] );
	l8ui	a2, a4, 3	# MEM[base: _616, offset: 3B],
	addi.n	a4, a4, 4	# ivtmp$100, ivtmp$100,
	slli	a2, a2, 24	# tmp268, MEM[base: _616, offset: 3B],
	srai	a2, a2, 24	# tmp266, tmp268,
# @OPUS@\upstream\silk\encode_pulses.c:101:         abs_pulses[i+3] = ( opus_int )silk_abs( pulses[ i + 3 ] );
	abs	a2, a2	# tmp269, tmp266
# @OPUS@\upstream\silk\encode_pulses.c:101:         abs_pulses[i+3] = ( opus_int )silk_abs( pulses[ i + 3 ] );
	s32i.n	a2, a3, 12	# MEM[base: _548, offset: 12B], tmp269
	addi	a3, a3, 16	# ivtmp$101, ivtmp$101,
# @OPUS@\upstream\silk\encode_pulses.c:97:     for( i = 0; i < iter * SHELL_CODEC_FRAME_LENGTH; i+=4 ) {
	bne	a5, a3, .L6	# _507, ivtmp$101,
	j	.L7		#
.L4:
# @OPUS@\upstream\silk\encode_pulses.c:113:             scale_down = combine_and_check( pulses_comb, abs_pulses_ptr, silk_max_pulses_table[ 0 ], 8 );
	l32r	a2, .LC1	#, tmp270
	slli	a8, a12, 2	#, tmp8,
# @OPUS@\upstream\silk\encode_pulses.c:115:             scale_down += combine_and_check( pulses_comb, pulses_comb, silk_max_pulses_table[ 1 ], 4 );
	l8ui	a12, a2, 1	# silk_max_pulses_table,
# @OPUS@\upstream\silk\encode_pulses.c:119:             scale_down += combine_and_check( &sum_pulses[ i ], pulses_comb, silk_max_pulses_table[ 3 ], 1 );
	movi.n	a7, 0	#,
# @OPUS@\upstream\silk\encode_pulses.c:115:             scale_down += combine_and_check( pulses_comb, pulses_comb, silk_max_pulses_table[ 1 ], 4 );
	s32i	a12, sp, 68	# %sfp,
	l32i	a12, sp, 144	# %sfp, ivtmp$94
# @OPUS@\upstream\silk\encode_pulses.c:119:             scale_down += combine_and_check( &sum_pulses[ i ], pulses_comb, silk_max_pulses_table[ 3 ], 1 );
	s32i	a7, sp, 128	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:113:             scale_down = combine_and_check( pulses_comb, abs_pulses_ptr, silk_max_pulses_table[ 0 ], 8 );
	l8ui	a9, a2, 0	# silk_max_pulses_table,
# @OPUS@\upstream\silk\encode_pulses.c:117:             scale_down += combine_and_check( pulses_comb, pulses_comb, silk_max_pulses_table[ 2 ], 2 );
	l8ui	a3, a2, 2	# silk_max_pulses_table,
	add.n	a7, a12, a8	#, ivtmp$94,
	s32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:119:             scale_down += combine_and_check( &sum_pulses[ i ], pulses_comb, silk_max_pulses_table[ 3 ], 1 );
	l8ui	a2, a2, 3	# silk_max_pulses_table,
	l32i	a8, sp, 128	# %sfp,
	l32i	a6, sp, 156	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:107:     abs_pulses_ptr = abs_pulses;
	l32i	a11, sp, 168	# %sfp, abs_pulses_ptr
# @OPUS@\upstream\silk\encode_pulses.c:113:             scale_down = combine_and_check( pulses_comb, abs_pulses_ptr, silk_max_pulses_table[ 0 ], 8 );
	s32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:117:             scale_down += combine_and_check( pulses_comb, pulses_comb, silk_max_pulses_table[ 2 ], 2 );
	s32i	a3, sp, 96	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:119:             scale_down += combine_and_check( &sum_pulses[ i ], pulses_comb, silk_max_pulses_table[ 3 ], 1 );
	s32i	a2, sp, 124	# %sfp,
	s32i.n	a6, sp, 60	# %sfp,
	s32i	a7, sp, 152	# %sfp,
	s32i	a8, sp, 120	# %sfp,
	s32i	a8, sp, 140	# %sfp,
	s32i	a8, sp, 116	# %sfp,
	s32i	a8, sp, 136	# %sfp,
	s32i	a8, sp, 108	# %sfp,
	s32i	a8, sp, 132	# %sfp,
	s32i	a8, sp, 104	# %sfp,
	s32i	a8, sp, 112	# %sfp,
	s32i	a8, sp, 80	# %sfp,
	s32i	a8, sp, 100	# %sfp,
	s32i	a8, sp, 76	# %sfp,
	s32i	a8, sp, 92	# %sfp,
	s32i	a8, sp, 84	# %sfp,
	s32i	a8, sp, 88	# %sfp,
	s32i	a8, sp, 72	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	mov.n	a10, a12	# ivtmp$94, ivtmp$94
.L18:
# @OPUS@\upstream\silk\encode_pulses.c:109:         nRshifts[ i ] = 0;
	movi.n	a9, 0	#,
	s32i.n	a9, a10, 0	# MEM[base: _238, offset: 0B],
	l32i.n	a3, a11, 4	# MEM[base: abs_pulses_ptr_463, offset: 4B], _270
	l32i.n	a6, a11, 0	# MEM[base: abs_pulses_ptr_463, offset: 0B], _261
	mov.n	a2, a3	# _270, _270
	mov.n	a3, a6	# _261, _261
	mov.n	a6, a2	# _270, _270
.L16:
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	l32i	a12, sp, 64	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	add.n	a6, a6, a3	# pulses_comb__lsm$30, _270, _261
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a6, .L49	#, pulses_comb__lsm$30,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a3, a11, 8	# MEM[base: abs_pulses_ptr_463, offset: 8B], MEM[base: abs_pulses_ptr_463, offset: 8B]
	l32i.n	a2, a11, 12	# MEM[base: abs_pulses_ptr_463, offset: 12B], MEM[base: abs_pulses_ptr_463, offset: 12B]
	add.n	a3, a3, a2	# pulses_comb__lsm$32, MEM[base: abs_pulses_ptr_463, offset: 8B], MEM[base: abs_pulses_ptr_463, offset: 12B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a3, .L50	#, pulses_comb__lsm$32,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a4, a11, 16	# MEM[base: abs_pulses_ptr_463, offset: 16B], MEM[base: abs_pulses_ptr_463, offset: 16B]
	l32i.n	a2, a11, 20	# MEM[base: abs_pulses_ptr_463, offset: 20B], MEM[base: abs_pulses_ptr_463, offset: 20B]
	add.n	a4, a4, a2	# pulses_comb__lsm$34, MEM[base: abs_pulses_ptr_463, offset: 16B], MEM[base: abs_pulses_ptr_463, offset: 20B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a4, .L51	#, pulses_comb__lsm$34,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a5, a11, 24	# MEM[base: abs_pulses_ptr_463, offset: 24B], MEM[base: abs_pulses_ptr_463, offset: 24B]
	l32i.n	a2, a11, 28	# MEM[base: abs_pulses_ptr_463, offset: 28B], MEM[base: abs_pulses_ptr_463, offset: 28B]
	add.n	a5, a5, a2	# pulses_comb__lsm$36, MEM[base: abs_pulses_ptr_463, offset: 24B], MEM[base: abs_pulses_ptr_463, offset: 28B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a5, .L52	#, pulses_comb__lsm$36,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a7, a11, 32	# MEM[base: abs_pulses_ptr_463, offset: 32B], MEM[base: abs_pulses_ptr_463, offset: 32B]
	l32i.n	a2, a11, 36	# MEM[base: abs_pulses_ptr_463, offset: 36B], MEM[base: abs_pulses_ptr_463, offset: 36B]
	add.n	a2, a7, a2	# sum, MEM[base: abs_pulses_ptr_463, offset: 32B], MEM[base: abs_pulses_ptr_463, offset: 36B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a2, .L53	#, sum,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a8, a11, 40	# MEM[base: abs_pulses_ptr_463, offset: 40B], MEM[base: abs_pulses_ptr_463, offset: 40B]
	l32i.n	a7, a11, 44	# MEM[base: abs_pulses_ptr_463, offset: 44B], MEM[base: abs_pulses_ptr_463, offset: 44B]
	add.n	a7, a8, a7	# sum, MEM[base: abs_pulses_ptr_463, offset: 40B], MEM[base: abs_pulses_ptr_463, offset: 44B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a7, .L54	#, sum,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a9, a11, 48	# MEM[base: abs_pulses_ptr_463, offset: 48B], MEM[base: abs_pulses_ptr_463, offset: 48B]
	l32i.n	a8, a11, 52	# MEM[base: abs_pulses_ptr_463, offset: 52B], MEM[base: abs_pulses_ptr_463, offset: 52B]
	add.n	a8, a9, a8	# sum, MEM[base: abs_pulses_ptr_463, offset: 48B], MEM[base: abs_pulses_ptr_463, offset: 52B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a8, .L55	#, sum,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i.n	a12, a11, 60	# MEM[base: abs_pulses_ptr_463, offset: 60B], MEM[base: abs_pulses_ptr_463, offset: 60B]
	l32i.n	a9, a11, 56	# MEM[base: abs_pulses_ptr_463, offset: 56B], MEM[base: abs_pulses_ptr_463, offset: 56B]
	add.n	a9, a9, a12	# sum, MEM[base: abs_pulses_ptr_463, offset: 56B], MEM[base: abs_pulses_ptr_463, offset: 60B]
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	l32i	a12, sp, 64	# %sfp,
	bge	a12, a9, .L56	#, sum,
	s32i	a2, sp, 104	# %sfp, sum
	movi.n	a2, 1	#,
	s32i	a8, sp, 116	# %sfp, sum
	s32i	a7, sp, 108	# %sfp, sum
	movi.n	a9, 2	# prephitmp_597,
	s32i	a2, sp, 140	# %sfp,
	s32i	a2, sp, 136	# %sfp, tmp7
	s32i	a2, sp, 132	# %sfp, tmp8
	s32i	a2, sp, 112	# %sfp, tmp12
	s32i	a2, sp, 100	# %sfp,
	s32i	a2, sp, 92	# %sfp, tmp7
	s32i	a2, sp, 88	# %sfp, tmp8
	j	.L9		#
.L49:
	l32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	l32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	l32i	a3, sp, 84	# %sfp, pulses_comb__lsm$32
	l32i	a6, sp, 72	# %sfp, pulses_comb__lsm$30
	movi.n	a9, 2	# prephitmp_597,
# @OPUS@\upstream\silk\encode_pulses.c:51:             return 1;
	movi.n	a2, 1	# _246,
	j	.L9		#
.L50:
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	movi.n	a12, 1	#,
	l32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	l32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	l32i	a3, sp, 84	# %sfp, pulses_comb__lsm$32
	movi.n	a9, 2	# prephitmp_597,
	s32i	a12, sp, 88	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:51:             return 1;
	mov.n	a2, a12	# _246,
	j	.L9		#
.L51:
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	movi.n	a2, 1	#,
	l32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	l32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	movi.n	a9, 2	# prephitmp_597,
	s32i	a2, sp, 92	# %sfp,
	s32i	a2, sp, 88	# %sfp, tmp7
	j	.L9		#
.L52:
	l32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	movi.n	a9, 2	# prephitmp_597,
	movi.n	a8, 1	#,
	j	.L101		#
.L53:
	movi.n	a7, 1	#,
	movi.n	a9, 2	# prephitmp_597,
	s32i	a7, sp, 112	# %sfp,
	mov.n	a8, a7	#,
.L101:
	s32i	a8, sp, 100	# %sfp,
	s32i	a8, sp, 92	# %sfp, tmp12
	mov.n	a2, a8	#, tmp12
	s32i	a8, sp, 88	# %sfp, tmp2
	j	.L9		#
.L54:
	movi.n	a7, 1	#,
	s32i	a2, sp, 104	# %sfp, sum
	movi.n	a9, 2	# prephitmp_597,
	s32i	a7, sp, 132	# %sfp,
	s32i	a7, sp, 112	# %sfp, tmp8
	s32i	a7, sp, 100	# %sfp, tmp12
	mov.n	a2, a7	#, tmp12
	s32i	a7, sp, 92	# %sfp, tmp2
	s32i	a7, sp, 88	# %sfp,
	j	.L9		#
.L55:
	movi.n	a8, 1	#,
	s32i	a2, sp, 104	# %sfp, sum
	s32i	a7, sp, 108	# %sfp, sum
	movi.n	a9, 2	# prephitmp_597,
	s32i	a8, sp, 136	# %sfp,
	s32i	a8, sp, 132	# %sfp, tmp12
	mov.n	a2, a8	#, tmp12
	s32i	a8, sp, 112	# %sfp, tmp2
	s32i	a8, sp, 100	# %sfp, tmp7
	s32i	a8, sp, 92	# %sfp,
	s32i	a8, sp, 88	# %sfp, tmp12
	j	.L9		#
.L56:
	s32i	a2, sp, 104	# %sfp, sum
	movi.n	a2, 1	#,
	s32i	a9, sp, 120	# %sfp, sum
	s32i	a2, sp, 128	# %sfp,
	mov.n	a9, a2	# prephitmp_597,
	s32i	a2, sp, 140	# %sfp, tmp7
	s32i	a2, sp, 136	# %sfp, tmp8
	s32i	a2, sp, 132	# %sfp, tmp12
	s32i	a2, sp, 112	# %sfp,
	s32i	a2, sp, 100	# %sfp, tmp7
	s32i	a2, sp, 92	# %sfp, tmp8
	s32i	a2, sp, 88	# %sfp, tmp12
	s32i	a8, sp, 116	# %sfp, sum
	s32i	a7, sp, 108	# %sfp, sum
# @OPUS@\upstream\silk\encode_pulses.c:56:     return 0;
	movi.n	a2, 0	# _246,
.L9:
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	l32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	add.n	a7, a3, a6	# sum, pulses_comb__lsm$32, pulses_comb__lsm$30
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a8, a7, .L57	#, sum,
	mov.n	a12, a8	#,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	add.n	a8, a4, a5	# pulses_comb__lsm$32, pulses_comb__lsm$34, pulses_comb__lsm$36
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	bge	a12, a8, .L11	#, pulses_comb__lsm$32,
	add.n	a2, a3, a7	#, pulses_comb__lsm$32, sum
	mov.n	a8, a3	# pulses_comb__lsm$32, pulses_comb__lsm$32
	movi.n	a3, 1	#,
	s32i	a2, sp, 72	# %sfp,
	s32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	mov.n	a2, a9	# _246, prephitmp_597
	s32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	s32i	a3, sp, 88	# %sfp,
	j	.L10		#
.L11:
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i	a12, sp, 108	# %sfp,
	l32i	a6, sp, 104	# %sfp,
	add.n	a3, a7, a8	#, sum, pulses_comb__lsm$32
	add.n	a6, a6, a12	#,,
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	l32i	a12, sp, 68	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	s32i	a6, sp, 76	# %sfp,
	s32i	a3, sp, 72	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	blt	a12, a6, .L58	#,,
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i	a3, sp, 116	# %sfp,
	l32i	a4, sp, 120	# %sfp,
	add.n	a3, a3, a4	#,,
	s32i	a3, sp, 80	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	bge	a12, a3, .L59	#,,
	s32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	mov.n	a2, a9	# _246, prephitmp_597
	movi.n	a5, 1	#,
	j	.L102		#
.L57:
	s32i	a7, sp, 72	# %sfp, sum
	mov.n	a2, a9	# _246, prephitmp_597
	s32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	s32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	mov.n	a8, a3	# pulses_comb__lsm$32, pulses_comb__lsm$32
	mov.n	a7, a6	# sum, pulses_comb__lsm$30
	j	.L10		#
.L58:
	movi.n	a12, 1	#,
	mov.n	a2, a9	# _246, prephitmp_597
	s32i	a5, sp, 80	# %sfp, pulses_comb__lsm$36
	s32i	a4, sp, 76	# %sfp, pulses_comb__lsm$34
	s32i	a12, sp, 92	# %sfp,
	s32i	a12, sp, 88	# %sfp, tmp3
	j	.L10		#
.L59:
	movi.n	a4, 1	#,
	s32i	a4, sp, 112	# %sfp,
	mov.n	a5, a4	#,
.L102:
	s32i	a5, sp, 100	# %sfp,
	s32i	a5, sp, 92	# %sfp, tmp6
	s32i	a5, sp, 88	# %sfp, tmp9
.L10:
	l32i	a12, sp, 96	# %sfp,
	l32i	a3, sp, 72	# %sfp,
	bge	a12, a3, .L12	#,,
	addi.n	a2, a2, 1	# _246, _246,
	s32i	a8, sp, 84	# %sfp, pulses_comb__lsm$32
	s32i	a7, sp, 72	# %sfp, sum
	j	.L13		#
.L12:
# @OPUS@\upstream\silk\encode_pulses.c:49:         sum = pulses_in[ 2 * k ] + pulses_in[ 2 * k + 1 ];
	l32i	a4, sp, 76	# %sfp,
	l32i	a5, sp, 80	# %sfp,
	add.n	a4, a4, a5	#,,
	s32i	a4, sp, 84	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:50:         if( sum > max_pulses ) {
	bge	a12, a4, .L14	# tmp6,,
	add.n	a3, a8, a3	# prephitmp_560, pulses_comb__lsm$32, tmp7
	s32i	a8, sp, 84	# %sfp, pulses_comb__lsm$32
	movi.n	a8, 1	#,
	addi.n	a2, a2, 1	# _246, _246,
	s32i	a8, sp, 88	# %sfp,
	j	.L13		#
.L14:
	add.n	a3, a4, a3	# prephitmp_560, tmp9, tmp12
	movi.n	a4, 1	#,
	s32i	a4, sp, 92	# %sfp,
	s32i	a4, sp, 88	# %sfp, tmp5
.L13:
	l32i	a6, sp, 124	# %sfp,
	bge	a6, a3, .L15	#, prephitmp_560,
.L17:
# @OPUS@\upstream\silk\encode_pulses.c:123:                 nRshifts[ i ]++;
	l32i.n	a2, a10, 0	# MEM[base: _238, offset: 0B], MEM[base: _238, offset: 0B]
	addi.n	a2, a2, 1	# tmp290, MEM[base: _238, offset: 0B],
	s32i.n	a2, a10, 0	# MEM[base: _238, offset: 0B], tmp290
# @OPUS@\upstream\silk\encode_pulses.c:125:                     abs_pulses_ptr[ k ] = silk_RSHIFT( abs_pulses_ptr[ k ], 1 );
	l32i.n	a8, a11, 40	# MEM[base: abs_pulses_ptr_463, offset: 40B], MEM[base: abs_pulses_ptr_463, offset: 40B]
	l32i.n	a2, a11, 24	# MEM[base: abs_pulses_ptr_463, offset: 24B], MEM[base: abs_pulses_ptr_463, offset: 24B]
	l32i.n	a5, a11, 32	# MEM[base: abs_pulses_ptr_463, offset: 32B], MEM[base: abs_pulses_ptr_463, offset: 32B]
	srai	a8, a8, 1	#, MEM[base: abs_pulses_ptr_463, offset: 40B],
	srai	a2, a2, 1	#, MEM[base: abs_pulses_ptr_463, offset: 24B],
	s32i.n	a8, a11, 40	# MEM[base: abs_pulses_ptr_463, offset: 40B],
	l32i.n	a8, a11, 44	# MEM[base: abs_pulses_ptr_463, offset: 44B],
	s32i.n	a2, a11, 24	# MEM[base: abs_pulses_ptr_463, offset: 24B],
	srai	a5, a5, 1	#, MEM[base: abs_pulses_ptr_463, offset: 32B],
	l32i.n	a2, a11, 52	# MEM[base: abs_pulses_ptr_463, offset: 52B],
	l32i.n	a3, a11, 0	# MEM[base: abs_pulses_ptr_463, offset: 0B], MEM[base: abs_pulses_ptr_463, offset: 0B]
	l32i.n	a6, a11, 4	# MEM[base: abs_pulses_ptr_463, offset: 4B], MEM[base: abs_pulses_ptr_463, offset: 4B]
	l32i.n	a15, a11, 8	# MEM[base: abs_pulses_ptr_463, offset: 8B], MEM[base: abs_pulses_ptr_463, offset: 8B]
	l32i.n	a14, a11, 12	# MEM[base: abs_pulses_ptr_463, offset: 12B], MEM[base: abs_pulses_ptr_463, offset: 12B]
	l32i.n	a13, a11, 16	# MEM[base: abs_pulses_ptr_463, offset: 16B], MEM[base: abs_pulses_ptr_463, offset: 16B]
	l32i.n	a12, a11, 20	# MEM[base: abs_pulses_ptr_463, offset: 20B], MEM[base: abs_pulses_ptr_463, offset: 20B]
	l32i.n	a9, a11, 28	# MEM[base: abs_pulses_ptr_463, offset: 28B], MEM[base: abs_pulses_ptr_463, offset: 28B]
	l32i.n	a7, a11, 36	# MEM[base: abs_pulses_ptr_463, offset: 36B], MEM[base: abs_pulses_ptr_463, offset: 36B]
	l32i.n	a4, a11, 48	# MEM[base: abs_pulses_ptr_463, offset: 48B], MEM[base: abs_pulses_ptr_463, offset: 48B]
	s32i.n	a5, a11, 32	# MEM[base: abs_pulses_ptr_463, offset: 32B],
	srai	a5, a8, 1	# tmp312,,
	l32i.n	a8, a11, 56	# MEM[base: abs_pulses_ptr_463, offset: 56B],
	srai	a2, a2, 1	#,,
	s32i.n	a2, a11, 52	# MEM[base: abs_pulses_ptr_463, offset: 52B],
	srai	a3, a3, 1	# _261, MEM[base: abs_pulses_ptr_463, offset: 0B],
	srai	a2, a8, 1	# tmp318,,
	srai	a6, a6, 1	# _270, MEM[base: abs_pulses_ptr_463, offset: 4B],
	srai	a15, a15, 1	# tmp294, MEM[base: abs_pulses_ptr_463, offset: 8B],
	srai	a14, a14, 1	# tmp296, MEM[base: abs_pulses_ptr_463, offset: 12B],
	srai	a13, a13, 1	# tmp298, MEM[base: abs_pulses_ptr_463, offset: 16B],
	srai	a12, a12, 1	# tmp300, MEM[base: abs_pulses_ptr_463, offset: 20B],
	srai	a9, a9, 1	# tmp304, MEM[base: abs_pulses_ptr_463, offset: 28B],
	srai	a7, a7, 1	# tmp308, MEM[base: abs_pulses_ptr_463, offset: 36B],
	srai	a4, a4, 1	# tmp314, MEM[base: abs_pulses_ptr_463, offset: 48B],
# @OPUS@\upstream\silk\encode_pulses.c:125:                     abs_pulses_ptr[ k ] = silk_RSHIFT( abs_pulses_ptr[ k ], 1 );
	s32i.n	a3, a11, 0	# MEM[base: abs_pulses_ptr_463, offset: 0B], _261
	s32i.n	a6, a11, 4	# MEM[base: abs_pulses_ptr_463, offset: 4B], _270
	s32i.n	a15, a11, 8	# MEM[base: abs_pulses_ptr_463, offset: 8B], tmp294
	s32i.n	a14, a11, 12	# MEM[base: abs_pulses_ptr_463, offset: 12B], tmp296
	s32i.n	a13, a11, 16	# MEM[base: abs_pulses_ptr_463, offset: 16B], tmp298
	s32i.n	a12, a11, 20	# MEM[base: abs_pulses_ptr_463, offset: 20B], tmp300
	s32i.n	a9, a11, 28	# MEM[base: abs_pulses_ptr_463, offset: 28B], tmp304
	s32i.n	a7, a11, 36	# MEM[base: abs_pulses_ptr_463, offset: 36B], tmp308
	s32i.n	a5, a11, 44	# MEM[base: abs_pulses_ptr_463, offset: 44B], tmp312
	s32i.n	a4, a11, 48	# MEM[base: abs_pulses_ptr_463, offset: 48B], tmp314
	s32i.n	a2, a11, 56	# MEM[base: abs_pulses_ptr_463, offset: 56B], tmp318
# @OPUS@\upstream\silk\encode_pulses.c:125:                     abs_pulses_ptr[ k ] = silk_RSHIFT( abs_pulses_ptr[ k ], 1 );
	l32i.n	a2, a11, 60	# MEM[base: abs_pulses_ptr_463, offset: 60B], MEM[base: abs_pulses_ptr_463, offset: 60B]
	srai	a2, a2, 1	# tmp320, MEM[base: abs_pulses_ptr_463, offset: 60B],
# @OPUS@\upstream\silk\encode_pulses.c:125:                     abs_pulses_ptr[ k ] = silk_RSHIFT( abs_pulses_ptr[ k ], 1 );
	s32i.n	a2, a11, 60	# MEM[base: abs_pulses_ptr_463, offset: 60B], tmp320
	j	.L16		#
.L15:
# @OPUS@\upstream\silk\encode_pulses.c:53:         pulses_comb[ k ] = sum;
	l32i.n	a9, sp, 60	# %sfp,
	s32i.n	a3, a9, 0	# MEM[base: _221, offset: 0B], prephitmp_560
# @OPUS@\upstream\silk\encode_pulses.c:121:             if( scale_down ) {
	bnez.n	a2, .L17	# _246,
	addi.n	a9, a9, 4	#,,
# @OPUS@\upstream\silk\encode_pulses.c:108:     for( i = 0; i < iter; i++ ) {
	l32i	a12, sp, 152	# %sfp,
	addi.n	a10, a10, 4	# ivtmp$94, ivtmp$94,
	s32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:132:         abs_pulses_ptr += SHELL_CODEC_FRAME_LENGTH;
	addi	a11, a11, 64	# abs_pulses_ptr, abs_pulses_ptr,
# @OPUS@\upstream\silk\encode_pulses.c:108:     for( i = 0; i < iter; i++ ) {
	bne	a12, a10, .L18	#, ivtmp$94,
	l32i	a2, sp, 88	# %sfp,
	beqz.n	a2, .L19	#,
	l32i	a3, sp, 72	# %sfp,
	s32i.n	a3, sp, 0	# MEM[(int *)&pulses_comb],
.L19:
	l32i	a4, sp, 92	# %sfp,
	beqz.n	a4, .L20	#,
	l32i	a5, sp, 84	# %sfp,
	s32i.n	a5, sp, 4	# MEM[(int *)&pulses_comb + 4B],
.L20:
	l32i	a6, sp, 100	# %sfp,
	beqz.n	a6, .L21	#,
	l32i	a7, sp, 76	# %sfp,
	s32i.n	a7, sp, 8	# MEM[(int *)&pulses_comb + 8B],
.L21:
	l32i	a8, sp, 112	# %sfp,
	beqz.n	a8, .L22	#,
	l32i	a9, sp, 80	# %sfp,
	s32i.n	a9, sp, 12	# MEM[(int *)&pulses_comb + 12B],
.L22:
	l32i	a12, sp, 132	# %sfp,
	beqz.n	a12, .L23	#,
	l32i	a2, sp, 104	# %sfp,
	s32i.n	a2, sp, 16	# MEM[(int *)&pulses_comb + 16B],
.L23:
	l32i	a3, sp, 136	# %sfp,
	beqz.n	a3, .L24	#,
	l32i	a4, sp, 108	# %sfp,
	s32i.n	a4, sp, 20	# MEM[(int *)&pulses_comb + 20B],
.L24:
	l32i	a5, sp, 140	# %sfp,
	beqz.n	a5, .L25	#,
	l32i	a6, sp, 116	# %sfp,
	s32i.n	a6, sp, 24	# MEM[(int *)&pulses_comb + 24B],
.L25:
	l32i	a7, sp, 128	# %sfp,
	beqz.n	a7, .L8	#,
	l32i	a8, sp, 120	# %sfp,
	s32i.n	a8, sp, 28	# MEM[(int *)&pulses_comb + 28B],
.L8:
# @OPUS@\upstream\silk\encode_pulses.c:142:         sumBits_Q5 = silk_rate_levels_BITS_Q5[ signalType >> 1 ][ k ];
	l32i	a9, sp, 180	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:68:     opus_int   i, k, j, iter, bit, nLS, scale_down, RateLevelIndex = 0;
	movi.n	a12, 0	# RateLevelIndex,
# @OPUS@\upstream\silk\encode_pulses.c:142:         sumBits_Q5 = silk_rate_levels_BITS_Q5[ signalType >> 1 ][ k ];
	srai	a2, a9, 1	# tmp322,,
	slli	a4, a2, 3	# tmp324, tmp322,
	l32r	a7, .LC2	#, ivtmp$87
# @OPUS@\upstream\silk\encode_pulses.c:139:     minSumBits_Q5 = silk_int32_MAX;
	l32r	a9, .LC0	#, minSumBits_Q5
	l32r	a11, .LC3	#, tmp364
# @OPUS@\upstream\silk\encode_pulses.c:140:     for( k = 0; k < N_RATE_LEVELS - 1; k++ ) {
	l32i	a13, sp, 156	# %sfp, sum_pulses
	l32i	a14, sp, 144	# %sfp, nRshifts
	l32i	a15, sp, 164	# %sfp, _294
	add.n	a4, a4, a2	# _282, tmp324, tmp322
# @OPUS@\upstream\silk\encode_pulses.c:140:     for( k = 0; k < N_RATE_LEVELS - 1; k++ ) {
	mov.n	a8, a12	# k, RateLevelIndex
# @OPUS@\upstream\silk\encode_pulses.c:140:     for( k = 0; k < N_RATE_LEVELS - 1; k++ ) {
	movi.n	a10, 9	# tmp336,
.L31:
# @OPUS@\upstream\silk\encode_pulses.c:142:         sumBits_Q5 = silk_rate_levels_BITS_Q5[ signalType >> 1 ][ k ];
	add.n	a2, a8, a4	# tmp326, k, _282
# @OPUS@\upstream\silk\encode_pulses.c:143:         for( i = 0; i < iter; i++ ) {
	l32i	a6, sp, 148	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:142:         sumBits_Q5 = silk_rate_levels_BITS_Q5[ signalType >> 1 ][ k ];
	add.n	a2, a11, a2	# tmp327, tmp364, tmp326
# @OPUS@\upstream\silk\encode_pulses.c:142:         sumBits_Q5 = silk_rate_levels_BITS_Q5[ signalType >> 1 ][ k ];
	l8ui	a3, a2, 0	# MEM[base: _275, offset: 0B], sumBits_Q5
# @OPUS@\upstream\silk\encode_pulses.c:143:         for( i = 0; i < iter; i++ ) {
	blti	a6, 1, .L26	#,,
	movi.n	a2, 0	# ivtmp$79,
.L29:
# @OPUS@\upstream\silk\encode_pulses.c:144:             if( nRshifts[ i ] > 0 ) {
	add.n	a5, a14, a2	# tmp329, nRshifts, ivtmp$79
# @OPUS@\upstream\silk\encode_pulses.c:144:             if( nRshifts[ i ] > 0 ) {
	l32i.n	a5, a5, 0	# MEM[base: _300, offset: 0B], MEM[base: _300, offset: 0B]
# @OPUS@\upstream\silk\encode_pulses.c:147:                 sumBits_Q5 += nBits_ptr[ sum_pulses[ i ] ];
	add.n	a6, a13, a2	# tmp332, sum_pulses, ivtmp$79
# @OPUS@\upstream\silk\encode_pulses.c:144:             if( nRshifts[ i ] > 0 ) {
	blti	a5, 1, .L27	# MEM[base: _300, offset: 0B],,
# @OPUS@\upstream\silk\encode_pulses.c:145:                 sumBits_Q5 += nBits_ptr[ SILK_MAX_PULSES + 1 ];
	l8ui	a5, a7, 17	# MEM[base: nBits_ptr_166, offset: 17B], MEM[base: nBits_ptr_166, offset: 17B]
# @OPUS@\upstream\silk\encode_pulses.c:145:                 sumBits_Q5 += nBits_ptr[ SILK_MAX_PULSES + 1 ];
	add.n	a3, a3, a5	# sumBits_Q5, sumBits_Q5, MEM[base: nBits_ptr_166, offset: 17B]
	j	.L28		#
.L27:
# @OPUS@\upstream\silk\encode_pulses.c:147:                 sumBits_Q5 += nBits_ptr[ sum_pulses[ i ] ];
	l32i.n	a5, a6, 0	# MEM[base: _293, offset: 0B], MEM[base: _293, offset: 0B]
	add.n	a5, a7, a5	# tmp334, ivtmp$87, MEM[base: _293, offset: 0B]
	l8ui	a5, a5, 0	# *_66, *_66
# @OPUS@\upstream\silk\encode_pulses.c:147:                 sumBits_Q5 += nBits_ptr[ sum_pulses[ i ] ];
	add.n	a3, a3, a5	# sumBits_Q5, sumBits_Q5, *_66
.L28:
	addi.n	a2, a2, 4	# ivtmp$79, ivtmp$79,
# @OPUS@\upstream\silk\encode_pulses.c:143:         for( i = 0; i < iter; i++ ) {
	bne	a15, a2, .L29	# _294, ivtmp$79,
.L26:
# @OPUS@\upstream\silk\encode_pulses.c:150:         if( sumBits_Q5 < minSumBits_Q5 ) {
	bge	a3, a9, .L30	# sumBits_Q5, minSumBits_Q5,
	mov.n	a9, a3	# minSumBits_Q5, sumBits_Q5
	mov.n	a12, a8	# RateLevelIndex, k
.L30:
# @OPUS@\upstream\silk\encode_pulses.c:140:     for( k = 0; k < N_RATE_LEVELS - 1; k++ ) {
	addi.n	a8, a8, 1	# k, k,
	addi	a7, a7, 18	# ivtmp$87, ivtmp$87,
# @OPUS@\upstream\silk\encode_pulses.c:140:     for( k = 0; k < N_RATE_LEVELS - 1; k++ ) {
	bne	a8, a10, .L31	# k, tmp336,
# @OPUS@\upstream\silk\encode_pulses.c:155:     ec_enc_icdf( psRangeEnc, RateLevelIndex, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	l32r	a2, .LC4	#, tmp338
	mov.n	a3, a12	#, RateLevelIndex
	add.n	a4, a2, a4	#, tmp338, _282
	l32i	a2, sp, 160	# %sfp,
	movi.n	a5, 8	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_pulses.c:160:     cdf_ptr = silk_pulses_per_block_iCDF[ RateLevelIndex ];
	slli	a2, a12, 3	# tmp340, RateLevelIndex,
	add.n	a2, a2, a12	# tmp341, tmp340, RateLevelIndex
	l32r	a3, .LC5	#, tmp343
	slli	a2, a2, 1	# tmp342, tmp341,
	add.n	a3, a2, a3	#, tmp342, tmp343
# @OPUS@\upstream\silk\encode_pulses.c:161:     for( i = 0; i < iter; i++ ) {
	l32i	a7, sp, 148	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:160:     cdf_ptr = silk_pulses_per_block_iCDF[ RateLevelIndex ];
	s32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:161:     for( i = 0; i < iter; i++ ) {
	bgei	a7, 1, .L32	#,,
.L42:
# @OPUS@\upstream\silk\encode_pulses.c:204:     silk_encode_signs( psRangeEnc, pulses, frame_length, signalType, quantOffsetType, sum_pulses );
	l32i	a3, sp, 172	# %sfp,
	l32i	a2, sp, 160	# %sfp,
	l32i	a7, sp, 156	# %sfp,
	l32i	a6, sp, 184	# %sfp,
	l32i	a5, sp, 180	# %sfp,
	l32i	a4, sp, 176	# %sfp,
	call0	silk_encode_signs		#
# @OPUS@\upstream\silk\encode_pulses.c:205:     RESTORE_STACK;
	l32i.n	a2, sp, 32	# _saved_stack,
	l32i.n	a3, sp, 36	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\encode_pulses.c:206: }
	l32i	a0, sp, 220	#,
	movi	a9, 0xe0	#,
	l32i	a12, sp, 216	#,
	l32i	a13, sp, 212	#,
	l32i	a14, sp, 208	#,
	l32i	a15, sp, 204	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L32:
	l32i	a8, sp, 144	# %sfp,
	l32i	a9, sp, 164	# %sfp,
	l32i	a15, sp, 156	# %sfp, ivtmp$66
	add.n	a8, a8, a9	#,,
# @OPUS@\upstream\silk\encode_pulses.c:161:     for( i = 0; i < iter; i++ ) {
	l32i	a12, sp, 144	# %sfp, ivtmp$72
	l32i	a14, sp, 160	# %sfp, psRangeEnc
	s32i.n	a8, sp, 52	# %sfp,
	mov.n	a13, a15	# ivtmp$73, ivtmp$66
	s32i.n	a15, sp, 60	# %sfp, ivtmp$66
.L37:
# @OPUS@\upstream\silk\encode_pulses.c:162:         if( nRshifts[ i ] == 0 ) {
	l32i.n	a2, a12, 0	# MEM[base: _320, offset: 0B], MEM[base: _320, offset: 0B]
	bnez.n	a2, .L33	# MEM[base: _320, offset: 0B],
# @OPUS@\upstream\silk\encode_pulses.c:163:             ec_enc_icdf( psRangeEnc, sum_pulses[ i ], cdf_ptr, 8 );
	l32i.n	a3, a13, 0	# MEM[base: _309, offset: 0B],
	l32i.n	a4, sp, 48	# %sfp,
	movi.n	a5, 8	#,
	mov.n	a2, a14	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L34		#
.L33:
# @OPUS@\upstream\silk\encode_pulses.c:165:             ec_enc_icdf( psRangeEnc, SILK_MAX_PULSES + 1, cdf_ptr, 8 );
	l32i.n	a4, sp, 48	# %sfp,
	movi.n	a3, 0x11	#,
	mov.n	a2, a14	#, psRangeEnc
	movi.n	a5, 8	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	l32i.n	a2, a12, 0	# MEM[base: _320, offset: 0B], MEM[base: _320, offset: 0B]
	l32r	a3, .LC6	#,
	addi.n	a2, a2, -1	# tmp345, MEM[base: _320, offset: 0B],
	s32i.n	a3, sp, 56	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	movi.n	a15, 0	# k,
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	bgei	a2, 1, .L35	# tmp345,,
.L36:
# @OPUS@\upstream\silk\encode_pulses.c:169:             ec_enc_icdf( psRangeEnc, sum_pulses[ i ], silk_pulses_per_block_iCDF[ N_RATE_LEVELS - 1 ], 8 );
	l32i.n	a3, a13, 0	# MEM[base: _308, offset: 0B],
	l32i.n	a4, sp, 56	# %sfp,
	movi.n	a5, 8	#,
	mov.n	a2, a14	#, psRangeEnc
	call0	ec_enc_icdf		#
	j	.L34		#
.L35:
# @OPUS@\upstream\silk\encode_pulses.c:167:                 ec_enc_icdf( psRangeEnc, SILK_MAX_PULSES + 1, silk_pulses_per_block_iCDF[ N_RATE_LEVELS - 1 ], 8 );
	l32r	a4, .LC6	#,
	mov.n	a2, a14	#, psRangeEnc
	movi.n	a5, 8	#,
	movi.n	a3, 0x11	#,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	l32i.n	a2, a12, 0	# MEM[base: _320, offset: 0B], MEM[base: _320, offset: 0B]
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	addi.n	a15, a15, 1	# k, k,
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	addi.n	a2, a2, -1	# tmp349, MEM[base: _320, offset: 0B],
# @OPUS@\upstream\silk\encode_pulses.c:166:             for( k = 0; k < nRshifts[ i ] - 1; k++ ) {
	blt	a15, a2, .L35	# k, tmp349,
	j	.L36		#
.L34:
# @OPUS@\upstream\silk\encode_pulses.c:161:     for( i = 0; i < iter; i++ ) {
	l32i.n	a6, sp, 52	# %sfp,
	addi.n	a12, a12, 4	# ivtmp$72, ivtmp$72,
	addi.n	a13, a13, 4	# ivtmp$73, ivtmp$73,
	bne	a6, a12, .L37	#, ivtmp$72,
	l32i	a7, sp, 156	# %sfp,
	l32i	a8, sp, 164	# %sfp,
	l32i.n	a15, sp, 60	# %sfp, ivtmp$66
	l32i	a13, sp, 168	# %sfp, ivtmp$67
	l32i	a14, sp, 160	# %sfp, psRangeEnc
	add.n	a12, a7, a8	# _427,,
.L39:
# @OPUS@\upstream\silk\encode_pulses.c:177:         if( sum_pulses[ i ] > 0 ) {
	l32i.n	a4, a15, 0	# MEM[base: _435, offset: 0B], MEM[base: _435, offset: 0B]
# @OPUS@\upstream\silk\encode_pulses.c:178:             silk_shell_encoder( psRangeEnc, &abs_pulses[ i * SHELL_CODEC_FRAME_LENGTH ] );
	mov.n	a3, a13	#, ivtmp$67
	addi.n	a15, a15, 4	# ivtmp$66, ivtmp$66,
	mov.n	a2, a14	#, psRangeEnc
# @OPUS@\upstream\silk\encode_pulses.c:177:         if( sum_pulses[ i ] > 0 ) {
	blti	a4, 1, .L38	# MEM[base: _435, offset: 0B],,
# @OPUS@\upstream\silk\encode_pulses.c:178:             silk_shell_encoder( psRangeEnc, &abs_pulses[ i * SHELL_CODEC_FRAME_LENGTH ] );
	call0	silk_shell_encoder		#
.L38:
	addi	a13, a13, 64	# ivtmp$67, ivtmp$67,
# @OPUS@\upstream\silk\encode_pulses.c:176:     for( i = 0; i < iter; i++ ) {
	bne	a12, a15, .L39	# _427, ivtmp$66,
	l32i	a9, sp, 172	# %sfp,
	l32i	a12, sp, 148	# %sfp,
	addi	a9, a9, 16	#,,
	slli	a2, a12, 4	# tmp352,,
	add.n	a2, a2, a9	#, tmp352,
# @OPUS@\upstream\silk\encode_pulses.c:193:                     ec_enc_icdf( psRangeEnc, bit, silk_lsb_iCDF, 8 );
	l32i	a14, sp, 160	# %sfp, psRangeEnc
	s32i.n	a9, sp, 56	# %sfp,
	s32i.n	a2, sp, 60	# %sfp,
	movi.n	a15, 8	# tmp392,
.L41:
# @OPUS@\upstream\silk\encode_pulses.c:186:         if( nRshifts[ i ] > 0 ) {
	l32i	a6, sp, 144	# %sfp,
	l32i.n	a2, a6, 0	# MEM[base: _459, offset: 0B], _91
# @OPUS@\upstream\silk\encode_pulses.c:186:         if( nRshifts[ i ] > 0 ) {
	bgei	a2, 1, .L40	# _91,,
.L47:
	l32i.n	a7, sp, 56	# %sfp,
	l32i	a8, sp, 144	# %sfp,
	addi	a7, a7, 16	#,,
	addi.n	a8, a8, 4	#,,
# @OPUS@\upstream\silk\encode_pulses.c:185:     for( i = 0; i < iter; i++ ) {
	l32i.n	a9, sp, 60	# %sfp,
	s32i.n	a7, sp, 56	# %sfp,
	s32i	a8, sp, 144	# %sfp,
	bne	a9, a7, .L41	#,,
	j	.L42		#
.L40:
	l32i.n	a12, sp, 56	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:188:             nLS = nRshifts[ i ] - 1;
	addi.n	a2, a2, -1	#, _91,
	addi	a12, a12, -16	#,,
	s32i.n	a2, sp, 52	# %sfp,
	s32i.n	a12, sp, 48	# %sfp,
.L46:
# @OPUS@\upstream\silk\encode_pulses.c:190:                 abs_q = (opus_int8)silk_abs( pulses_ptr[ k ] );
	l32i.n	a6, sp, 48	# %sfp,
	l8ui	a2, a6, 0	# MEM[base: _517, offset: 0B], _97
# @OPUS@\upstream\silk\encode_pulses.c:190:                 abs_q = (opus_int8)silk_abs( pulses_ptr[ k ] );
	slli	a12, a2, 24	# tmp354, _97,
	srai	a12, a12, 24	# tmp353, tmp354,
	bgei	a12, 1, .L44	# tmp353,,
# @OPUS@\upstream\silk\encode_pulses.c:190:                 abs_q = (opus_int8)silk_abs( pulses_ptr[ k ] );
	neg	a12, a2	# tmp357, _97
	slli	a12, a12, 24	# tmp358, tmp357,
	srai	a12, a12, 24	# iftmp$25_121, tmp358,
.L44:
# @OPUS@\upstream\silk\encode_pulses.c:191:                 for( j = nLS; j > 0; j-- ) {
	l32i.n	a13, sp, 52	# %sfp, j
	bnez.n	a13, .L45	# j,
.L48:
	l32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\silk\encode_pulses.c:196:                 ec_enc_icdf( psRangeEnc, bit, silk_lsb_iCDF, 8 );
	l32r	a4, .LC7	#,
	addi.n	a7, a7, 1	#,,
	mov.n	a5, a15	#, tmp392
	extui	a3, a12, 0, 1	#, iftmp$25_121,
	mov.n	a2, a14	#, psRangeEnc
	s32i.n	a7, sp, 48	# %sfp,
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_pulses.c:189:             for( k = 0; k < SHELL_CODEC_FRAME_LENGTH; k++ ) {
	l32i.n	a8, sp, 56	# %sfp,
	l32i.n	a9, sp, 48	# %sfp,
	bne	a8, a9, .L46	#,,
	j	.L47		#
.L45:
# @OPUS@\upstream\silk\encode_pulses.c:192:                     bit = silk_RSHIFT( abs_q, j ) & 1;
	ssr	a13	# j
	sra	a3, a12	# tmp362, iftmp$25_121
# @OPUS@\upstream\silk\encode_pulses.c:193:                     ec_enc_icdf( psRangeEnc, bit, silk_lsb_iCDF, 8 );
	l32r	a4, .LC7	#,
# @OPUS@\upstream\silk\encode_pulses.c:191:                 for( j = nLS; j > 0; j-- ) {
	addi.n	a13, a13, -1	# j, j,
# @OPUS@\upstream\silk\encode_pulses.c:193:                     ec_enc_icdf( psRangeEnc, bit, silk_lsb_iCDF, 8 );
	mov.n	a5, a15	#, tmp392
	extui	a3, a3, 0, 1	#, tmp362,
	mov.n	a2, a14	#, psRangeEnc
	call0	ec_enc_icdf		#
# @OPUS@\upstream\silk\encode_pulses.c:191:                 for( j = nLS; j > 0; j-- ) {
	bnez.n	a13, .L45	# j,
	j	.L48		#
	.size	silk_encode_pulses, .-silk_encode_pulses
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
