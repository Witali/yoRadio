# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_pulses.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_pulses.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_pulses.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_pulses.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_pulses.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_pulses.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_pulses.c.s.raw
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
	.section	.text.silk_decode_pulses,"ax",@progbits
	.literal_position
	.literal .LC0, silk_rate_levels_iCDF
	.literal .LC1, silk_pulses_per_block_iCDF
	.literal .LC2, silk_pulses_per_block_iCDF+163
	.literal .LC3, silk_pulses_per_block_iCDF+162
	.literal .LC4, silk_lsb_iCDF
	.align	4
	.global	silk_decode_pulses
	.type	silk_decode_pulses, @function
# Function: silk_decode_pulses
# Module: upstream/silk/decode_pulses.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /*********************************************/
# C context: /* Decode quantization indices of excitation */
# C context: /*********************************************/
# C context: void silk_decode_pulses(
# C context: ec_dec                      *psRangeDec,                    /* I/O  Compressor data structure                   */
# C context: opus_int16                  pulses[],                       /* O    Excitation signal                           */
# C context: const opus_int              signalType,                     /* I    Sigtype                                     */
# C context: const opus_int              quantOffsetType,                /* I    quantOffsetType                             */
silk_decode_pulses:
	movi	a9, 0xf0	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	srai	a7, a4, 1	# tmp96, signalType,
# @OPUS@\upstream\silk\decode_pulses.c:44: {
	s32i	a4, sp, 188	# %sfp, signalType
	s32i	a3, sp, 180	# %sfp, pulses
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	slli	a4, a7, 3	# tmp98, tmp96,
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	l32r	a3, .LC0	#, tmp101
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	add.n	a7, a4, a7	# tmp99, tmp98, tmp96
# @OPUS@\upstream\silk\decode_pulses.c:44: {
	s32i	a6, sp, 184	# %sfp, frame_length
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	movi.n	a4, 8	#,
# @OPUS@\upstream\silk\decode_pulses.c:57:     iter = silk_RSHIFT( frame_length, LOG2_SHELL_CODEC_FRAME_LENGTH );
	srai	a6, a6, 4	#, frame_length,
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	add.n	a3, a3, a7	#, tmp101, tmp99
# @OPUS@\upstream\silk\decode_pulses.c:44: {
	s32i	a15, sp, 220	#,
# @OPUS@\upstream\silk\decode_pulses.c:57:     iter = silk_RSHIFT( frame_length, LOG2_SHELL_CODEC_FRAME_LENGTH );
	s32i	a6, sp, 172	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:44: {
	s32i	a0, sp, 236	#,
	s32i	a12, sp, 232	#,
	s32i	a13, sp, 228	#,
	s32i	a14, sp, 224	#,
# @OPUS@\upstream\silk\decode_pulses.c:44: {
	mov.n	a15, a2	# psRangeDec, psRangeDec
	s32i	a5, sp, 192	# %sfp, quantOffsetType
# @OPUS@\upstream\silk\decode_pulses.c:53:     RateLevelIndex = ec_dec_icdf( psRangeDec, silk_rate_levels_iCDF[ signalType >> 1 ], 8 );
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_pulses.c:58:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	l32i	a6, sp, 172	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:58:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	l32i	a4, sp, 184	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:58:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	slli	a3, a6, 4	# tmp102,,
# @OPUS@\upstream\silk\decode_pulses.c:58:     if( iter * SHELL_CODEC_FRAME_LENGTH < frame_length ) {
	bge	a3, a4, .L2	# tmp102,,
# @OPUS@\upstream\silk\decode_pulses.c:60:         iter++;
	addi.n	a6, a6, 1	#,,
	s32i	a6, sp, 172	# %sfp,
.L2:
# @OPUS@\upstream\silk\decode_pulses.c:66:     cdf_ptr = silk_pulses_per_block_iCDF[ RateLevelIndex ];
	slli	a3, a2, 3	# tmp104, RateLevelIndex,
	add.n	a2, a3, a2	# tmp105, tmp104, RateLevelIndex
	l32r	a3, .LC1	#, tmp107
	slli	a2, a2, 1	# tmp106, tmp105,
	add.n	a3, a2, a3	#, tmp106, tmp107
# @OPUS@\upstream\silk\decode_pulses.c:67:     for( i = 0; i < iter; i++ ) {
	l32i	a6, sp, 172	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:66:     cdf_ptr = silk_pulses_per_block_iCDF[ RateLevelIndex ];
	s32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:67:     for( i = 0; i < iter; i++ ) {
	bgei	a6, 1, .L3	#,,
	addi	a6, sp, 80	#,,
	s32i	a6, sp, 176	# %sfp,
.L17:
# @OPUS@\upstream\silk\decode_pulses.c:114:     silk_decode_signs( psRangeDec, pulses, frame_length, signalType, quantOffsetType, sum_pulses );
	l32i	a7, sp, 176	# %sfp,
	l32i	a6, sp, 192	# %sfp,
	l32i	a5, sp, 188	# %sfp,
	l32i	a4, sp, 184	# %sfp,
	l32i	a3, sp, 180	# %sfp,
	mov.n	a2, a15	#, psRangeDec
	call0	silk_decode_signs		#
# @OPUS@\upstream\silk\decode_pulses.c:115: }
	l32i	a0, sp, 236	#,
	movi	a9, 0xf0	#,
	l32i	a12, sp, 232	#,
	l32i	a13, sp, 228	#,
	l32i	a14, sp, 224	#,
	l32i	a15, sp, 220	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L3:
	addi	a6, sp, 80	#,,
	s32i	a6, sp, 176	# %sfp,
	l32i	a6, sp, 172	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:67:     for( i = 0; i < iter; i++ ) {
	l32i	a14, sp, 176	# %sfp, ivtmp$30
	slli	a2, a6, 2	# tmp109,,
	add.n	a2, a2, sp	#, tmp109,
	mov.n	a13, sp	# ivtmp$29,
	s32i	a2, sp, 168	# %sfp,
.L5:
# @OPUS@\upstream\silk\decode_pulses.c:69:         sum_pulses[ i ] = ec_dec_icdf( psRangeDec, cdf_ptr, 8 );
	l32i	a3, sp, 164	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:68:         nLshifts[ i ] = 0;
	movi.n	a5, 0	# tmp110,
# @OPUS@\upstream\silk\decode_pulses.c:69:         sum_pulses[ i ] = ec_dec_icdf( psRangeDec, cdf_ptr, 8 );
	movi.n	a4, 8	#,
	mov.n	a2, a15	#, psRangeDec
# @OPUS@\upstream\silk\decode_pulses.c:68:         nLshifts[ i ] = 0;
	s32i.n	a5, a13, 0	# MEM[base: _131, offset: 0B], tmp110
# @OPUS@\upstream\silk\decode_pulses.c:69:         sum_pulses[ i ] = ec_dec_icdf( psRangeDec, cdf_ptr, 8 );
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_pulses.c:69:         sum_pulses[ i ] = ec_dec_icdf( psRangeDec, cdf_ptr, 8 );
	s32i.n	a2, a14, 0	# MEM[base: _133, offset: 0B], _4
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	movi.n	a3, 0x11	# tmp111,
	s32i	a2, sp, 160	# %sfp, _4
	movi.n	a12, 1	# ivtmp$26,
	beq	a2, a3, .L4	# _4, tmp111,
.L9:
# @OPUS@\upstream\silk\decode_pulses.c:67:     for( i = 0; i < iter; i++ ) {
	l32i	a6, sp, 168	# %sfp,
	addi.n	a13, a13, 4	# ivtmp$29, ivtmp$29,
	addi.n	a14, a14, 4	# ivtmp$30, ivtmp$30,
	bne	a13, a6, .L5	# ivtmp$29,,
	j	.L27		#
.L4:
# @OPUS@\upstream\silk\decode_pulses.c:73:             nLshifts[ i ]++;
	s32i.n	a12, a13, 0	# MEM[base: _131, offset: 0B], ivtmp$26
# @OPUS@\upstream\silk\decode_pulses.c:75:             sum_pulses[ i ] = ec_dec_icdf( psRangeDec,
	movi.n	a4, 8	#,
	l32r	a3, .LC3	#,
	mov.n	a2, a15	#, psRangeDec
	bnei	a12, 10, .L7	# ivtmp$26,,
	l32r	a3, .LC2	#,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:75:             sum_pulses[ i ] = ec_dec_icdf( psRangeDec,
	s32i.n	a2, a14, 0	# MEM[base: _133, offset: 0B], _97
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	beq	a2, a6, .L19	# _97,,
	j	.L9		#
.L7:
# @OPUS@\upstream\silk\decode_pulses.c:75:             sum_pulses[ i ] = ec_dec_icdf( psRangeDec,
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:75:             sum_pulses[ i ] = ec_dec_icdf( psRangeDec,
	s32i.n	a2, a14, 0	# MEM[base: _133, offset: 0B], _7
	addi.n	a12, a12, 1	# ivtmp$26, ivtmp$26,
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	beq	a2, a6, .L4	# _7,,
	j	.L9		#
.L19:
# @OPUS@\upstream\silk\decode_pulses.c:72:         while( sum_pulses[ i ] == SILK_MAX_PULSES + 1 ) {
	movi.n	a12, 0xb	# ivtmp$26,
	j	.L4		#
.L27:
	l32i	a6, sp, 172	# %sfp,
	l32i	a2, sp, 180	# %sfp,
	slli	a6, a6, 5	#,,
	add.n	a12, a6, a2	# _111,,
# @OPUS@\upstream\silk\decode_pulses.c:87:             silk_memset( &pulses[ silk_SMULBB( i, SHELL_CODEC_FRAME_LENGTH ) ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof( pulses[0] ) );
	s32i	a12, sp, 160	# %sfp, _111
	l32i	a12, sp, 176	# %sfp, ivtmp$23
	s32i	a6, sp, 168	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:67:     for( i = 0; i < iter; i++ ) {
	mov.n	a13, a2	# ivtmp$24,
# @OPUS@\upstream\silk\decode_pulses.c:87:             silk_memset( &pulses[ silk_SMULBB( i, SHELL_CODEC_FRAME_LENGTH ) ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof( pulses[0] ) );
	movi.n	a14, 0x20	# tmp140,
.L12:
# @OPUS@\upstream\silk\decode_pulses.c:84:         if( sum_pulses[ i ] > 0 ) {
	l32i.n	a6, a12, 0	# MEM[base: _116, offset: 0B], _9
# @OPUS@\upstream\silk\decode_pulses.c:85:             silk_shell_decoder( &pulses[ silk_SMULBB( i, SHELL_CODEC_FRAME_LENGTH ) ], psRangeDec, sum_pulses[ i ] );
	mov.n	a3, a15	#, psRangeDec
	mov.n	a4, a6	#, _9
	mov.n	a2, a13	#, ivtmp$24
# @OPUS@\upstream\silk\decode_pulses.c:84:         if( sum_pulses[ i ] > 0 ) {
	blti	a6, 1, .L10	# _9,,
# @OPUS@\upstream\silk\decode_pulses.c:85:             silk_shell_decoder( &pulses[ silk_SMULBB( i, SHELL_CODEC_FRAME_LENGTH ) ], psRangeDec, sum_pulses[ i ] );
	call0	silk_shell_decoder		#
	j	.L11		#
.L10:
# @OPUS@\upstream\silk\decode_pulses.c:87:             silk_memset( &pulses[ silk_SMULBB( i, SHELL_CODEC_FRAME_LENGTH ) ], 0, SHELL_CODEC_FRAME_LENGTH * sizeof( pulses[0] ) );
	mov.n	a4, a14	#, tmp140
	movi.n	a3, 0	#,
	call0	memset		#
.L11:
# @OPUS@\upstream\silk\decode_pulses.c:83:     for( i = 0; i < iter; i++ ) {
	l32i	a6, sp, 160	# %sfp,
	addi	a13, a13, 32	# ivtmp$24, ivtmp$24,
	addi.n	a12, a12, 4	# ivtmp$23, ivtmp$23,
	bne	a6, a13, .L12	#, ivtmp$24,
	l32i	a6, sp, 180	# %sfp,
	l32i	a2, sp, 168	# %sfp,
	addi	a6, a6, 32	#,,
	s32i	a6, sp, 164	# %sfp,
	add.n	a6, a6, a2	#,,
	s32i	a6, sp, 172	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:83:     for( i = 0; i < iter; i++ ) {
	movi.n	a6, 0	#,
	s32i	a6, sp, 168	# %sfp,
	addi	a6, sp, 80	#,,
	s32i	a6, sp, 176	# %sfp,
.L16:
# @OPUS@\upstream\silk\decode_pulses.c:95:         if( nLshifts[ i ] > 0 ) {
	l32i	a6, sp, 168	# %sfp,
	add.n	a2, sp, a6	# tmp119,,
	l32i.n	a12, a2, 0	# MEM[base: _44, offset: 0B], _20
# @OPUS@\upstream\silk\decode_pulses.c:95:         if( nLshifts[ i ] > 0 ) {
	blti	a12, 1, .L13	# _20,,
	l32i	a6, sp, 164	# %sfp,
	addi	a6, a6, -32	#,,
	s32i	a6, sp, 160	# %sfp,
.L15:
# @OPUS@\upstream\silk\decode_pulses.c:99:                 abs_q = pulses_ptr[ k ];
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:100:                 for( j = 0; j < nLS; j++ ) {
	movi.n	a14, 0	# j,
# @OPUS@\upstream\silk\decode_pulses.c:99:                 abs_q = pulses_ptr[ k ];
	l16si	a5, a6, 0	# MEM[base: _117, offset: 0B], abs_q
# @OPUS@\upstream\silk\decode_pulses.c:100:                 for( j = 0; j < nLS; j++ ) {
	mov.n	a13, a5	# abs_q, abs_q
.L14:
# @OPUS@\upstream\silk\decode_pulses.c:102:                     abs_q += ec_dec_icdf( psRangeDec, silk_lsb_iCDF, 8 );
	l32r	a3, .LC4	#,
	movi.n	a4, 8	#,
	mov.n	a2, a15	#, psRangeDec
# @OPUS@\upstream\silk\decode_pulses.c:101:                     abs_q = silk_LSHIFT( abs_q, 1 );
	slli	a13, a13, 1	# _30, abs_q,
# @OPUS@\upstream\silk\decode_pulses.c:102:                     abs_q += ec_dec_icdf( psRangeDec, silk_lsb_iCDF, 8 );
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\decode_pulses.c:100:                 for( j = 0; j < nLS; j++ ) {
	addi.n	a14, a14, 1	# j, j,
# @OPUS@\upstream\silk\decode_pulses.c:102:                     abs_q += ec_dec_icdf( psRangeDec, silk_lsb_iCDF, 8 );
	add.n	a13, a13, a2	# abs_q, _30,
# @OPUS@\upstream\silk\decode_pulses.c:100:                 for( j = 0; j < nLS; j++ ) {
	bne	a12, a14, .L14	# _20, j,
# @OPUS@\upstream\silk\decode_pulses.c:104:                 pulses_ptr[ k ] = abs_q;
	l32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:98:             for( k = 0; k < SHELL_CODEC_FRAME_LENGTH; k++ ) {
	l32i	a2, sp, 164	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:104:                 pulses_ptr[ k ] = abs_q;
	s16i	a13, a6, 0	# MEM[base: _117, offset: 0B], abs_q
	addi.n	a6, a6, 2	#,,
	s32i	a6, sp, 160	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:98:             for( k = 0; k < SHELL_CODEC_FRAME_LENGTH; k++ ) {
	bne	a2, a6, .L15	#,,
	l32i	a2, sp, 168	# %sfp,
	l32i	a6, sp, 176	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:107:             sum_pulses[ i ] |= nLS << 5;
	slli	a12, a12, 5	# tmp124, _20,
	add.n	a3, a6, a2	# _21,,
# @OPUS@\upstream\silk\decode_pulses.c:107:             sum_pulses[ i ] |= nLS << 5;
	l32i.n	a2, a3, 0	# MEM[base: _21, offset: 0B], MEM[base: _21, offset: 0B]
	or	a12, a2, a12	# tmp125, MEM[base: _21, offset: 0B], tmp124
	s32i.n	a12, a3, 0	# MEM[base: _21, offset: 0B], tmp125
.L13:
	l32i	a6, sp, 164	# %sfp,
	addi	a6, a6, 32	#,,
	s32i	a6, sp, 164	# %sfp,
	l32i	a6, sp, 168	# %sfp,
# @OPUS@\upstream\silk\decode_pulses.c:94:     for( i = 0; i < iter; i++ ) {
	l32i	a2, sp, 164	# %sfp,
	addi.n	a6, a6, 4	#,,
	s32i	a6, sp, 168	# %sfp,
	l32i	a6, sp, 172	# %sfp,
	bne	a6, a2, .L16	#,,
	j	.L17		#
	.size	silk_decode_pulses, .-silk_decode_pulses
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
