# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/code_signs.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"code_signs.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\code_signs.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\code_signs.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\code_signs.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\code_signs.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\code_signs.c.s.raw
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
	.section	.text.silk_encode_signs,"ax",@progbits
	.literal_position
	.literal .LC0, silk_sign_iCDF
	.align	4
	.global	silk_encode_signs
	.type	silk_encode_signs, @function
# Function: silk_encode_signs
# Module: upstream/silk/code_signs.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define silk_dec_map(a)                  ( silk_LSHIFT( (a),  1 ) - 1 )
# C context:
# C context: /* Encodes signs of excitation */
# C context: void silk_encode_signs(
# C context: ec_enc                      *psRangeEnc,                        /* I/O  Compressor data structure                   */
# C context: const opus_int8             pulses[],                           /* I    pulse signal                                */
# C context: opus_int                    length,                             /* I    length of input                             */
# C context: const opus_int              signalType,                         /* I    Signal type                                 */
silk_encode_signs:
# @OPUS@\upstream\silk\code_signs.c:57:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	slli	a5, a5, 1	# tmp134, signalType,
	add.n	a5, a5, a6	# tmp137, tmp134, quantOffsetType
# @OPUS@\upstream\silk\code_signs.c:57:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	slli	a5, a5, 16	# tmp139, tmp137,
	srai	a5, a5, 16	# tmp138, tmp139,
	slli	a8, a5, 3	# tmp141, tmp138,
# @OPUS@\upstream\silk\code_signs.c:49: {
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\silk\code_signs.c:59:     length = silk_RSHIFT( length + SHELL_CODEC_FRAME_LENGTH/2, LOG2_SHELL_CODEC_FRAME_LENGTH );
	addi.n	a4, a4, 8	# _7, length,
# @OPUS@\upstream\silk\code_signs.c:55:     icdf[ 1 ] = 0;
	movi.n	a6, 0	# tmp133,
# @OPUS@\upstream\silk\code_signs.c:57:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	sub	a8, a8, a5	#, tmp141, tmp138
# @OPUS@\upstream\silk\code_signs.c:49: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a15, sp, 44	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\silk\code_signs.c:55:     icdf[ 1 ] = 0;
	s8i	a6, sp, 1	# icdf, tmp133
# @OPUS@\upstream\silk\code_signs.c:59:     length = silk_RSHIFT( length + SHELL_CODEC_FRAME_LENGTH/2, LOG2_SHELL_CODEC_FRAME_LENGTH );
	srai	a4, a4, 4	# length, _7,
# @OPUS@\upstream\silk\code_signs.c:57:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	s32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\silk\code_signs.c:49: {
	mov.n	a13, a2	# psRangeEnc, psRangeEnc
	mov.n	a15, a3	# pulses, pulses
# @OPUS@\upstream\silk\code_signs.c:60:     for( i = 0; i < length; i++ ) {
	blti	a4, 1, .L1	# length,,
	slli	a4, a4, 4	# tmp143, length,
	mov.n	a12, a7	# ivtmp$18, sum_pulses
	add.n	a14, a3, a4	# _213, pulses, tmp143
.L22:
# @OPUS@\upstream\silk\code_signs.c:61:         p = sum_pulses[ i ];
	l32i.n	a2, a12, 0	# MEM[base: _216, offset: 0B], p
# @OPUS@\upstream\silk\code_signs.c:62:         if( p > 0 ) {
	blti	a2, 1, .L4	# p,,
# @OPUS@\upstream\silk\code_signs.c:63:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	extui	a2, a2, 0, 5	# tmp144, p,
	movi.n	a3, 6	# iftmp$2_24,
	bge	a2, a3, .L5	# tmp144,,
# @OPUS@\upstream\silk\code_signs.c:63:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	mov.n	a3, a2	# iftmp$2_24, tmp144
.L5:
# @OPUS@\upstream\silk\code_signs.c:63:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	l32r	a2, .LC0	#,
	add.n	a3, a2, a3	# tmp146,, iftmp$2_24
	l32i.n	a2, sp, 16	# %sfp,
	add.n	a3, a3, a2	# tmp147, tmp146,
# @OPUS@\upstream\silk\code_signs.c:63:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	l8ui	a3, a3, 0	# *_13,
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 0	# MEM[base: q_ptr_73, offset: 0B], _52
# @OPUS@\upstream\silk\code_signs.c:63:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	s8i	a3, sp, 0	# icdf, *_13
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L6	# _52,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp150, _52,
	srai	a3, a2, 31	# tmp151, tmp150,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp151,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L6:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 1	# MEM[base: q_ptr_73, offset: 1B], _63
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L7	# _63,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp154, _63,
	srai	a3, a2, 31	# tmp155, tmp154,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp155,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L7:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 2	# MEM[base: q_ptr_73, offset: 2B], _74
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L8	# _74,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp158, _74,
	srai	a3, a2, 31	# tmp159, tmp158,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp159,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L8:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 3	# MEM[base: q_ptr_73, offset: 3B], _85
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L9	# _85,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp162, _85,
	srai	a3, a2, 31	# tmp163, tmp162,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp163,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L9:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 4	# MEM[base: q_ptr_73, offset: 4B], _96
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L10	# _96,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp166, _96,
	srai	a3, a2, 31	# tmp167, tmp166,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp167,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L10:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 5	# MEM[base: q_ptr_73, offset: 5B], _107
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L11	# _107,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp170, _107,
	srai	a3, a2, 31	# tmp171, tmp170,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp171,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L11:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 6	# MEM[base: q_ptr_73, offset: 6B], _118
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L12	# _118,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp174, _118,
	srai	a3, a2, 31	# tmp175, tmp174,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp175,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L12:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 7	# MEM[base: q_ptr_73, offset: 7B], _129
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L13	# _129,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp178, _129,
	srai	a3, a2, 31	# tmp179, tmp178,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp179,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L13:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 8	# MEM[base: q_ptr_73, offset: 8B], _140
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L14	# _140,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp182, _140,
	srai	a3, a2, 31	# tmp183, tmp182,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp183,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L14:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 9	# MEM[base: q_ptr_73, offset: 9B], _151
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L15	# _151,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp186, _151,
	srai	a3, a2, 31	# tmp187, tmp186,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp187,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L15:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 10	# MEM[base: q_ptr_73, offset: 10B], _162
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L16	# _162,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp190, _162,
	srai	a3, a2, 31	# tmp191, tmp190,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp191,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L16:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 11	# MEM[base: q_ptr_73, offset: 11B], _173
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L17	# _173,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp194, _173,
	srai	a3, a2, 31	# tmp195, tmp194,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp195,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L17:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 12	# MEM[base: q_ptr_73, offset: 12B], _184
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L18	# _184,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp198, _184,
	srai	a3, a2, 31	# tmp199, tmp198,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp199,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L18:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 13	# MEM[base: q_ptr_73, offset: 13B], _195
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L19	# _195,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp202, _195,
	srai	a3, a2, 31	# tmp203, tmp202,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp203,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L19:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 14	# MEM[base: q_ptr_73, offset: 14B], _206
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L20	# _206,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp206, _206,
	srai	a3, a2, 31	# tmp207, tmp206,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp207,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L20:
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	l8ui	a2, a15, 15	# MEM[base: q_ptr_73, offset: 15B], _217
# @OPUS@\upstream\silk\code_signs.c:65:                 if( q_ptr[ j ] != 0 ) {
	beqz.n	a2, .L4	# _217,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	slli	a2, a2, 24	# tmp210, _217,
	srai	a3, a2, 31	# tmp211, tmp210,
# @OPUS@\upstream\silk\code_signs.c:66:                     ec_enc_icdf( psRangeEnc, silk_enc_map( q_ptr[ j ]), icdf, 8 );
	movi.n	a5, 8	#,
	mov.n	a4, sp	#,
	addi.n	a3, a3, 1	#, tmp211,
	mov.n	a2, a13	#, psRangeEnc
	call0	ec_enc_icdf		#
.L4:
# @OPUS@\upstream\silk\code_signs.c:70:         q_ptr += SHELL_CODEC_FRAME_LENGTH;
	addi	a15, a15, 16	# pulses, pulses,
	addi.n	a12, a12, 4	# ivtmp$18, ivtmp$18,
# @OPUS@\upstream\silk\code_signs.c:60:     for( i = 0; i < length; i++ ) {
	bne	a15, a14, .L22	# pulses, _213,
.L1:
# @OPUS@\upstream\silk\code_signs.c:72: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_encode_signs, .-silk_encode_signs
	.section	.text.silk_decode_signs,"ax",@progbits
	.literal_position
	.literal .LC1, silk_sign_iCDF
	.align	4
	.global	silk_decode_signs
	.type	silk_decode_signs, @function
# Function: silk_decode_signs
# Module: upstream/silk/code_signs.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Decodes signs of excitation */
# C context: void silk_decode_signs(
# C context: ec_dec                      *psRangeDec,                        /* I/O  Compressor data structure                   */
# C context: opus_int16                  pulses[],                           /* I/O  pulse signal                                */
# C context: opus_int                    length,                             /* I    length of input                             */
# C context: const opus_int              signalType,                         /* I    Signal type                                 */
silk_decode_signs:
# @OPUS@\upstream\silk\code_signs.c:91:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	slli	a5, a5, 1	# tmp214, signalType,
	add.n	a6, a5, a6	# tmp217, tmp214, quantOffsetType
# @OPUS@\upstream\silk\code_signs.c:91:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	slli	a6, a6, 16	# tmp219, tmp217,
	srai	a6, a6, 16	# tmp218, tmp219,
	slli	a8, a6, 3	# tmp221, tmp218,
# @OPUS@\upstream\silk\code_signs.c:83: {
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\silk\code_signs.c:93:     length = silk_RSHIFT( length + SHELL_CODEC_FRAME_LENGTH/2, LOG2_SHELL_CODEC_FRAME_LENGTH );
	addi.n	a4, a4, 8	# _7, length,
# @OPUS@\upstream\silk\code_signs.c:89:     icdf[ 1 ] = 0;
	movi.n	a5, 0	# tmp213,
# @OPUS@\upstream\silk\code_signs.c:91:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	sub	a8, a8, a6	#, tmp221, tmp218
# @OPUS@\upstream\silk\code_signs.c:83: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a15, sp, 44	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a12, sp, 56	#,
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\silk\code_signs.c:89:     icdf[ 1 ] = 0;
	s8i	a5, sp, 1	# icdf, tmp213
# @OPUS@\upstream\silk\code_signs.c:93:     length = silk_RSHIFT( length + SHELL_CODEC_FRAME_LENGTH/2, LOG2_SHELL_CODEC_FRAME_LENGTH );
	srai	a4, a4, 4	# length, _7,
# @OPUS@\upstream\silk\code_signs.c:91:     i = silk_SMULBB( 7, silk_ADD_LSHIFT( quantOffsetType, signalType, 1 ) );
	s32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\silk\code_signs.c:83: {
	mov.n	a13, a2	# psRangeDec, psRangeDec
	mov.n	a15, a3	# pulses, pulses
# @OPUS@\upstream\silk\code_signs.c:94:     for( i = 0; i < length; i++ ) {
	blti	a4, 1, .L74	# length,,
	slli	a4, a4, 5	# tmp223, length,
	mov.n	a12, a7	# ivtmp$25, sum_pulses
	add.n	a14, a3, a4	# _95, pulses, tmp223
.L95:
# @OPUS@\upstream\silk\code_signs.c:95:         p = sum_pulses[ i ];
	l32i.n	a2, a12, 0	# MEM[base: _293, offset: 0B], p
# @OPUS@\upstream\silk\code_signs.c:96:         if( p > 0 ) {
	blti	a2, 1, .L77	# p,,
# @OPUS@\upstream\silk\code_signs.c:97:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	extui	a2, a2, 0, 5	# tmp224, p,
	movi.n	a3, 6	# iftmp$8_29,
	bge	a2, a3, .L78	# tmp224,,
# @OPUS@\upstream\silk\code_signs.c:97:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	mov.n	a3, a2	# iftmp$8_29, tmp224
.L78:
# @OPUS@\upstream\silk\code_signs.c:97:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	l32r	a2, .LC1	#,
	add.n	a3, a2, a3	# tmp226,, iftmp$8_29
	l32i.n	a2, sp, 16	# %sfp,
	add.n	a3, a3, a2	# tmp227, tmp226,
# @OPUS@\upstream\silk\code_signs.c:97:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	l8ui	a3, a3, 0	# *_13,
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 0	# MEM[base: q_ptr_149, offset: 0B], tmp229
# @OPUS@\upstream\silk\code_signs.c:97:             icdf[ 0 ] = icdf_ptr[ silk_min( p & 0x1F, 6 ) ];
	s8i	a3, sp, 0	# icdf, *_13
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	blti	a2, 1, .L79	# tmp229,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 0	# MEM[base: q_ptr_149, offset: 0B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp232,,
	addi.n	a2, a2, -1	# tmp233, tmp232,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp234, MEM[base: q_ptr_149, offset: 0B], tmp233
	s16i	a3, a15, 0	# MEM[base: q_ptr_149, offset: 0B], tmp234
.L79:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 2	# MEM[base: q_ptr_149, offset: 2B], tmp236
	blti	a2, 1, .L80	# tmp236,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 2	# MEM[base: q_ptr_149, offset: 2B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp239,,
	addi.n	a2, a2, -1	# tmp240, tmp239,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp241, MEM[base: q_ptr_149, offset: 2B], tmp240
	s16i	a3, a15, 2	# MEM[base: q_ptr_149, offset: 2B], tmp241
.L80:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 4	# MEM[base: q_ptr_149, offset: 4B], tmp243
	blti	a2, 1, .L81	# tmp243,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 4	# MEM[base: q_ptr_149, offset: 4B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp246,,
	addi.n	a2, a2, -1	# tmp247, tmp246,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp248, MEM[base: q_ptr_149, offset: 4B], tmp247
	s16i	a3, a15, 4	# MEM[base: q_ptr_149, offset: 4B], tmp248
.L81:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 6	# MEM[base: q_ptr_149, offset: 6B], tmp250
	blti	a2, 1, .L82	# tmp250,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 6	# MEM[base: q_ptr_149, offset: 6B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp253,,
	addi.n	a2, a2, -1	# tmp254, tmp253,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp255, MEM[base: q_ptr_149, offset: 6B], tmp254
	s16i	a3, a15, 6	# MEM[base: q_ptr_149, offset: 6B], tmp255
.L82:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 8	# MEM[base: q_ptr_149, offset: 8B], tmp257
	blti	a2, 1, .L83	# tmp257,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 8	# MEM[base: q_ptr_149, offset: 8B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp260,,
	addi.n	a2, a2, -1	# tmp261, tmp260,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp262, MEM[base: q_ptr_149, offset: 8B], tmp261
	s16i	a3, a15, 8	# MEM[base: q_ptr_149, offset: 8B], tmp262
.L83:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 10	# MEM[base: q_ptr_149, offset: 10B], tmp264
	blti	a2, 1, .L84	# tmp264,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 10	# MEM[base: q_ptr_149, offset: 10B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp267,,
	addi.n	a2, a2, -1	# tmp268, tmp267,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp269, MEM[base: q_ptr_149, offset: 10B], tmp268
	s16i	a3, a15, 10	# MEM[base: q_ptr_149, offset: 10B], tmp269
.L84:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 12	# MEM[base: q_ptr_149, offset: 12B], tmp271
	blti	a2, 1, .L85	# tmp271,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 12	# MEM[base: q_ptr_149, offset: 12B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp274,,
	addi.n	a2, a2, -1	# tmp275, tmp274,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp276, MEM[base: q_ptr_149, offset: 12B], tmp275
	s16i	a3, a15, 12	# MEM[base: q_ptr_149, offset: 12B], tmp276
.L85:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 14	# MEM[base: q_ptr_149, offset: 14B], tmp278
	blti	a2, 1, .L86	# tmp278,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 14	# MEM[base: q_ptr_149, offset: 14B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp281,,
	addi.n	a2, a2, -1	# tmp282, tmp281,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp283, MEM[base: q_ptr_149, offset: 14B], tmp282
	s16i	a3, a15, 14	# MEM[base: q_ptr_149, offset: 14B], tmp283
.L86:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 16	# MEM[base: q_ptr_149, offset: 16B], tmp285
	blti	a2, 1, .L87	# tmp285,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 16	# MEM[base: q_ptr_149, offset: 16B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp288,,
	addi.n	a2, a2, -1	# tmp289, tmp288,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp290, MEM[base: q_ptr_149, offset: 16B], tmp289
	s16i	a3, a15, 16	# MEM[base: q_ptr_149, offset: 16B], tmp290
.L87:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 18	# MEM[base: q_ptr_149, offset: 18B], tmp292
	blti	a2, 1, .L88	# tmp292,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 18	# MEM[base: q_ptr_149, offset: 18B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp295,,
	addi.n	a2, a2, -1	# tmp296, tmp295,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp297, MEM[base: q_ptr_149, offset: 18B], tmp296
	s16i	a3, a15, 18	# MEM[base: q_ptr_149, offset: 18B], tmp297
.L88:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 20	# MEM[base: q_ptr_149, offset: 20B], tmp299
	blti	a2, 1, .L89	# tmp299,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 20	# MEM[base: q_ptr_149, offset: 20B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp302,,
	addi.n	a2, a2, -1	# tmp303, tmp302,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp304, MEM[base: q_ptr_149, offset: 20B], tmp303
	s16i	a3, a15, 20	# MEM[base: q_ptr_149, offset: 20B], tmp304
.L89:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 22	# MEM[base: q_ptr_149, offset: 22B], tmp306
	blti	a2, 1, .L90	# tmp306,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 22	# MEM[base: q_ptr_149, offset: 22B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp309,,
	addi.n	a2, a2, -1	# tmp310, tmp309,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp311, MEM[base: q_ptr_149, offset: 22B], tmp310
	s16i	a3, a15, 22	# MEM[base: q_ptr_149, offset: 22B], tmp311
.L90:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 24	# MEM[base: q_ptr_149, offset: 24B], tmp313
	blti	a2, 1, .L91	# tmp313,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 24	# MEM[base: q_ptr_149, offset: 24B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp316,,
	addi.n	a2, a2, -1	# tmp317, tmp316,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp318, MEM[base: q_ptr_149, offset: 24B], tmp317
	s16i	a3, a15, 24	# MEM[base: q_ptr_149, offset: 24B], tmp318
.L91:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 26	# MEM[base: q_ptr_149, offset: 26B], tmp320
	blti	a2, 1, .L92	# tmp320,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 26	# MEM[base: q_ptr_149, offset: 26B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp323,,
	addi.n	a2, a2, -1	# tmp324, tmp323,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp325, MEM[base: q_ptr_149, offset: 26B], tmp324
	s16i	a3, a15, 26	# MEM[base: q_ptr_149, offset: 26B], tmp325
.L92:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 28	# MEM[base: q_ptr_149, offset: 28B], tmp327
	blti	a2, 1, .L93	# tmp327,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 28	# MEM[base: q_ptr_149, offset: 28B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp330,,
	addi.n	a2, a2, -1	# tmp331, tmp330,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp332, MEM[base: q_ptr_149, offset: 28B], tmp331
	s16i	a3, a15, 28	# MEM[base: q_ptr_149, offset: 28B], tmp332
.L93:
# @OPUS@\upstream\silk\code_signs.c:99:                 if( q_ptr[ j ] > 0 ) {
	l16si	a2, a15, 30	# MEM[base: q_ptr_149, offset: 30B], tmp334
	blti	a2, 1, .L77	# tmp334,,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mov.n	a3, sp	#,
	movi.n	a4, 8	#,
	mov.n	a2, a13	#, psRangeDec
	call0	ec_dec_icdf		#
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	l16ui	a3, a15, 30	# MEM[base: q_ptr_149, offset: 30B],
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	slli	a2, a2, 1	# tmp337,,
	addi.n	a2, a2, -1	# tmp338, tmp337,
# @OPUS@\upstream\silk\code_signs.c:108:                     q_ptr[ j ] *= silk_dec_map( ec_dec_icdf( psRangeDec, icdf, 8 ) );
	mul16s	a3, a3, a2	# tmp339, MEM[base: q_ptr_149, offset: 30B], tmp338
	s16i	a3, a15, 30	# MEM[base: q_ptr_149, offset: 30B], tmp339
.L77:
# @OPUS@\upstream\silk\code_signs.c:113:         q_ptr += SHELL_CODEC_FRAME_LENGTH;
	addi	a15, a15, 32	# pulses, pulses,
	addi.n	a12, a12, 4	# ivtmp$25, ivtmp$25,
# @OPUS@\upstream\silk\code_signs.c:94:     for( i = 0; i < length; i++ ) {
	bne	a15, a14, .L95	# pulses, _95,
.L74:
# @OPUS@\upstream\silk\code_signs.c:115: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_decode_signs, .-silk_decode_signs
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
