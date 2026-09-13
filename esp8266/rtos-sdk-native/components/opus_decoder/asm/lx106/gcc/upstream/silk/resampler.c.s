# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler.c.s.raw
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
	.section	.text.silk_resampler_init,"ax",@progbits
	.literal_position
	.literal .LC0, -8000
	.literal .LC1, -12000
	.literal .LC2, -16000
	.literal .LC3, -24000
	.literal .LC4, -48000
	.literal .LC5, delay_matrix_enc
	.literal .LC6, 16000
	.literal .LC7, 24000
	.literal .LC8, delay_matrix_dec
	.literal .LC9, silk_Resampler_3_4_COEFS
	.literal .LC10, silk_Resampler_2_3_COEFS
	.literal .LC11, silk_Resampler_1_2_COEFS
	.literal .LC12, silk_Resampler_1_3_COEFS
	.literal .LC13, silk_Resampler_1_4_COEFS
	.literal .LC14, silk_Resampler_1_6_COEFS
	.align	4
	.global	silk_resampler_init
	.type	silk_resampler_init, @function
# Function: silk_resampler_init
# Module: upstream/silk/resampler.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define USE_silk_resampler_private_down_FIR         (3)
# C context:
# C context: /* Initialize/reset the resampler state for a given pair of input/output sampling rates */
# C context: opus_int silk_resampler_init(
# C context: silk_resampler_state_struct *S,                 /* I/O  Resampler state                                             */
# C context: opus_int32                  Fs_Hz_in,           /* I    Input sampling rate (Hz)                                    */
# C context: opus_int32                  Fs_Hz_out,          /* I    Output sampling rate (Hz)                                   */
# C context: opus_int                    forEnc              /* I    If 1: encoder; if 0: decoder                                */
silk_resampler_init:
	addi	sp, sp, -32	#,,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
	mov.n	a14, a4	# Fs_Hz_out, Fs_Hz_out
	mov.n	a15, a3	# Fs_Hz_in, Fs_Hz_in
# @OPUS@\upstream\silk\resampler.c:88:     silk_memset( S, 0, sizeof( silk_resampler_state_struct ) );
	movi	a4, 0x12c	#,
	movi.n	a3, 0	#,
# @OPUS@\upstream\silk\resampler.c:84: {
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a0, sp, 28	#,
# @OPUS@\upstream\silk\resampler.c:84: {
	mov.n	a13, a5	# forEnc, forEnc
	mov.n	a12, a2	# S, S
# @OPUS@\upstream\silk\resampler.c:88:     silk_memset( S, 0, sizeof( silk_resampler_state_struct ) );
	call0	memset		#
	l32r	a2, .LC0	#, tmp382
	movi.n	a7, 0	# tmp162,
	movi.n	a5, 1	# tmp161,
	add.n	a3, a15, a2	# tmp159, Fs_Hz_in, tmp382
	l32r	a6, .LC1	#, tmp383
	mov.n	a8, a7	#, tmp162
	movnez	a8, a5, a3	#, tmp161, tmp159
	mov.n	a3, a8	# tmp158,
	add.n	a4, a15, a6	# tmp165, Fs_Hz_in, tmp383
	mov.n	a8, a7	#, tmp162
	movnez	a8, a5, a4	#, tmp161, tmp165
	and	a3, a3, a8	# _196, tmp158, tmp164
# @OPUS@\upstream\silk\resampler.c:91:     if( forEnc ) {
	beq	a13, a7, .L2	# forEnc,,
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	beq	a3, a7, .L3	# _196,,
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	l32r	a4, .LC2	#, tmp173
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	l32r	a3, .LC3	#, tmp179
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	add.n	a4, a15, a4	# tmp172, Fs_Hz_in, tmp173
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	add.n	a3, a15, a3	# tmp178, Fs_Hz_in, tmp179
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	mov.n	a8, a7	#, tmp162
	movnez	a8, a5, a4	#, tmp161, tmp172
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	moveqz	a5, a7, a3	# tmp177, tmp162, tmp178
# @OPUS@\upstream\silk\resampler.c:92:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 && Fs_Hz_in  != 24000 && Fs_Hz_in  != 48000 ) ||
	bnone	a8, a5, .L3	# tmp171, tmp177,
	l32r	a3, .LC4	#, tmp188
	add.n	a3, a15, a3	# tmp187, Fs_Hz_in, tmp188
	beq	a3, a7, .L3	# tmp187,,
.L5:
# @OPUS@\upstream\silk\resampler.c:95:             return -1;
	movi.n	a2, -1	# <retval>,
	j	.L1		#
.L3:
# @OPUS@\upstream\silk\resampler.c:93:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 ) ) {
	movi.n	a3, 0	# tmp197,
	movi.n	a4, 1	# tmp196,
	mov.n	a5, a3	#, tmp197
	add.n	a2, a14, a2	# tmp194, Fs_Hz_out, tmp382
# @OPUS@\upstream\silk\resampler.c:93:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 ) ) {
	add.n	a6, a14, a6	# tmp200, Fs_Hz_out, tmp383
# @OPUS@\upstream\silk\resampler.c:93:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 ) ) {
	movnez	a5, a4, a2	#, tmp196, tmp194
# @OPUS@\upstream\silk\resampler.c:93:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 ) ) {
	movnez	a3, a4, a6	# tmp197, tmp196, tmp200
# @OPUS@\upstream\silk\resampler.c:93:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 ) ) {
	bnone	a5, a3, .L30	# tmp193, tmp199,
	l32r	a2, .LC2	#, tmp210
	add.n	a2, a14, a2	# tmp209, Fs_Hz_out, tmp210
	bnez.n	a2, .L5	# tmp209,
.L30:
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	l32r	a5, .LC6	#, tmp385
	srai	a2, a15, 12	# tmp215, Fs_Hz_in,
	movi.n	a3, 1	# tmp216,
	blt	a5, a15, .L7	# tmp385, Fs_Hz_in,
	movi.n	a3, 0	# tmp216,
.L7:
	l32r	a4, .LC7	#, tmp386
	sub	a2, a2, a3	# tmp219, tmp215, tmp216
	movi.n	a3, 1	# tmp220,
	blt	a4, a15, .L8	# tmp386, Fs_Hz_in,
	movi.n	a3, 0	# tmp220,
.L8:
	ssr	a3	# tmp220
	sra	a2, a2	# tmp223, tmp219
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	addi.n	a2, a2, -1	# tmp224, tmp223,
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	srai	a3, a14, 12	# tmp225, Fs_Hz_out,
	movi.n	a6, 1	# tmp226,
	blt	a5, a14, .L9	# tmp385, Fs_Hz_out,
	movi.n	a6, 0	# tmp226,
.L9:
	sub	a3, a3, a6	# tmp229, tmp225, tmp226
	movi.n	a5, 1	# tmp230,
	blt	a4, a14, .L10	# tmp386, Fs_Hz_out,
	movi.n	a5, 0	# tmp230,
.L10:
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	slli	a4, a2, 1	# tmp235, tmp224,
	add.n	a4, a4, a2	# tmp236, tmp235, tmp224
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	ssr	a5	# tmp230
	sra	a3, a3	# tmp233, tmp229
# @OPUS@\upstream\silk\resampler.c:97:         S->inputDelay = delay_matrix_enc[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	l32r	a2, .LC5	#, tmp214
	j	.L57		#
.L2:
# @OPUS@\upstream\silk\resampler.c:99:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 ) ||
	l32r	a7, .LC2	#, tmp384
	add.n	a4, a15, a7	# tmp245, Fs_Hz_in, tmp384
	movnez	a13, a5, a4	# forEnc, tmp161, tmp245
	extui	a4, a13, 0, 8	# tmp249, tmp244
	beqz.n	a4, .L31	# tmp249,
	bnez.n	a3, .L5	# _196,
.L31:
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	add.n	a2, a14, a2	# tmp252, Fs_Hz_out, tmp382
	movi.n	a3, 0	# tmp255,
	movi.n	a4, 1	# tmp254,
# @OPUS@\upstream\silk\resampler.c:99:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 ) ||
	beq	a2, a3, .L13	# tmp252,,
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	add.n	a6, a14, a6	# tmp259, Fs_Hz_out, tmp383
# @OPUS@\upstream\silk\resampler.c:99:         if( ( Fs_Hz_in  != 8000 && Fs_Hz_in  != 12000 && Fs_Hz_in  != 16000 ) ||
	beq	a6, a3, .L13	# tmp259,,
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	l32r	a2, .LC3	#, tmp273
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	mov.n	a8, a3	#, tmp255
	add.n	a7, a14, a7	# tmp266, Fs_Hz_out, tmp384
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	add.n	a2, a14, a2	# tmp272, Fs_Hz_out, tmp273
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	movnez	a8, a4, a7	#, tmp254, tmp266
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	movnez	a3, a4, a2	# tmp255, tmp254, tmp272
# @OPUS@\upstream\silk\resampler.c:100:             ( Fs_Hz_out != 8000 && Fs_Hz_out != 12000 && Fs_Hz_out != 16000 && Fs_Hz_out != 24000 && Fs_Hz_out != 48000 ) ) {
	bnone	a8, a3, .L13	# tmp265, tmp271,
	l32r	a2, .LC4	#, tmp282
	add.n	a2, a14, a2	# tmp281, Fs_Hz_out, tmp282
	bnez.n	a2, .L5	# tmp281,
.L13:
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	l32r	a5, .LC6	#, tmp385
	srai	a2, a15, 12	# tmp287, Fs_Hz_in,
	movi.n	a3, 1	# tmp288,
	blt	a5, a15, .L15	# tmp385, Fs_Hz_in,
	movi.n	a3, 0	# tmp288,
.L15:
	l32r	a4, .LC7	#, tmp386
	sub	a2, a2, a3	# tmp291, tmp287, tmp288
	movi.n	a3, 1	# tmp292,
	blt	a4, a15, .L16	# tmp386, Fs_Hz_in,
	movi.n	a3, 0	# tmp292,
.L16:
	ssr	a3	# tmp292
	sra	a2, a2	# tmp295, tmp291
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	addi.n	a2, a2, -1	# tmp296, tmp295,
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	srai	a3, a14, 12	# tmp297, Fs_Hz_out,
	movi.n	a6, 1	# tmp298,
	blt	a5, a14, .L17	# tmp385, Fs_Hz_out,
	movi.n	a6, 0	# tmp298,
.L17:
	sub	a3, a3, a6	# tmp301, tmp297, tmp298
	movi.n	a5, 1	# tmp302,
	blt	a4, a14, .L18	# tmp386, Fs_Hz_out,
	movi.n	a5, 0	# tmp302,
.L18:
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	slli	a4, a2, 2	# tmp307, tmp296,
	add.n	a4, a4, a2	# tmp308, tmp307, tmp296
	l32r	a2, .LC8	#, tmp286
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	ssr	a5	# tmp302
	sra	a3, a3	# tmp305, tmp301
.L57:
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	add.n	a2, a2, a4	# tmp309, tmp286, tmp308
	add.n	a2, a2, a3	# tmp310, tmp309, tmp305
	addi.n	a2, a2, -1	# tmp311, tmp310,
	l8ui	a2, a2, 0	#,
# @OPUS@\upstream\silk\resampler.c:107:     S->Fs_in_kHz  = silk_DIV32_16( Fs_Hz_in,  1000 );
	movi	a3, 0x3e8	#,
# @OPUS@\upstream\silk\resampler.c:104:         S->inputDelay = delay_matrix_dec[ rateID( Fs_Hz_in ) ][ rateID( Fs_Hz_out ) ];
	slli	a2, a2, 24	# tmp314, tmp313,
	srai	a2, a2, 24	# tmp312, tmp314,
	s32i	a2, a12, 292	# S_97(D)->inputDelay, tmp312
# @OPUS@\upstream\silk\resampler.c:107:     S->Fs_in_kHz  = silk_DIV32_16( Fs_Hz_in,  1000 );
	mov.n	a2, a15	#, Fs_Hz_in
	call0	__divsi3		#
	mov.n	a13, a2	# tmp317,
# @OPUS@\upstream\silk\resampler.c:107:     S->Fs_in_kHz  = silk_DIV32_16( Fs_Hz_in,  1000 );
	s32i	a2, a12, 284	# S_97(D)->Fs_in_kHz, tmp317
# @OPUS@\upstream\silk\resampler.c:108:     S->Fs_out_kHz = silk_DIV32_16( Fs_Hz_out, 1000 );
	movi	a3, 0x3e8	#,
	mov.n	a2, a14	#, Fs_Hz_out
	call0	__divsi3		#
# @OPUS@\upstream\silk\resampler.c:111:     S->batchSize = S->Fs_in_kHz * RESAMPLER_MAX_BATCH_SIZE_MS;
	slli	a3, a13, 2	# tmp322, tmp317,
	add.n	a3, a3, a13	# tmp323, tmp322, tmp317
	slli	a3, a3, 1	# tmp324, tmp323,
# @OPUS@\upstream\silk\resampler.c:108:     S->Fs_out_kHz = silk_DIV32_16( Fs_Hz_out, 1000 );
	s32i	a2, a12, 288	# S_97(D)->Fs_out_kHz,
# @OPUS@\upstream\silk\resampler.c:111:     S->batchSize = S->Fs_in_kHz * RESAMPLER_MAX_BATCH_SIZE_MS;
	s32i	a3, a12, 268	# S_97(D)->batchSize, tmp324
# @OPUS@\upstream\silk\resampler.c:115:     if( Fs_Hz_out > Fs_Hz_in ) {
	bge	a15, a14, .L19	# Fs_Hz_in, Fs_Hz_out,
# @OPUS@\upstream\silk\resampler.c:117:         if( Fs_Hz_out == silk_MUL( Fs_Hz_in, 2 ) ) {                            /* Fs_out : Fs_in = 2 : 1 */
	slli	a2, a15, 1	# tmp325, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:117:         if( Fs_Hz_out == silk_MUL( Fs_Hz_in, 2 ) ) {                            /* Fs_out : Fs_in = 2 : 1 */
	bne	a2, a14, .L20	# tmp325, Fs_Hz_out,
# @OPUS@\upstream\silk\resampler.c:119:             S->resampler_function = USE_silk_resampler_private_up2_HQ_wrapper;
	movi.n	a2, 1	# tmp326,
	s32i	a2, a12, 264	# S_97(D)->resampler_function, tmp326
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L20:
# @OPUS@\upstream\silk\resampler.c:122:             S->resampler_function = USE_silk_resampler_private_IIR_FIR;
	movi.n	a2, 2	# tmp327,
	s32i	a2, a12, 264	# S_97(D)->resampler_function, tmp327
# @OPUS@\upstream\silk\resampler.c:123:             up2x = 1;
	movi.n	a13, 1	# up2x,
# @OPUS@\upstream\silk\resampler.c:122:             S->resampler_function = USE_silk_resampler_private_IIR_FIR;
	movi.n	a2, 0xf	# prephitmp_197,
	j	.L21		#
.L19:
# @OPUS@\upstream\silk\resampler.c:125:     } else if ( Fs_Hz_out < Fs_Hz_in ) {
	bge	a14, a15, .L22	# Fs_Hz_out, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:127:          S->resampler_function = USE_silk_resampler_private_down_FIR;
	movi.n	a3, 3	# tmp328,
# @OPUS@\upstream\silk\resampler.c:128:         if( silk_MUL( Fs_Hz_out, 4 ) == silk_MUL( Fs_Hz_in, 3 ) ) {             /* Fs_out : Fs_in = 3 : 4 */
	slli	a2, a15, 1	# tmp330, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:127:          S->resampler_function = USE_silk_resampler_private_down_FIR;
	s32i	a3, a12, 264	# S_97(D)->resampler_function, tmp328
# @OPUS@\upstream\silk\resampler.c:128:         if( silk_MUL( Fs_Hz_out, 4 ) == silk_MUL( Fs_Hz_in, 3 ) ) {             /* Fs_out : Fs_in = 3 : 4 */
	slli	a4, a14, 2	# _59, Fs_Hz_out,
# @OPUS@\upstream\silk\resampler.c:128:         if( silk_MUL( Fs_Hz_out, 4 ) == silk_MUL( Fs_Hz_in, 3 ) ) {             /* Fs_out : Fs_in = 3 : 4 */
	add.n	a5, a2, a15	# tmp331, tmp330, Fs_Hz_in
# @OPUS@\upstream\silk\resampler.c:128:         if( silk_MUL( Fs_Hz_out, 4 ) == silk_MUL( Fs_Hz_in, 3 ) ) {             /* Fs_out : Fs_in = 3 : 4 */
	bne	a4, a5, .L23	# _59, tmp331,
# @OPUS@\upstream\silk\resampler.c:130:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR0;
	movi.n	a2, 0x12	# tmp333,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp333
# @OPUS@\upstream\silk\resampler.c:131:             S->Coefs = silk_Resampler_3_4_COEFS;
	l32r	a2, .LC9	#, tmp334
# @OPUS@\upstream\silk\resampler.c:129:             S->FIR_Fracs = 3;
	s32i	a3, a12, 280	# S_97(D)->FIR_Fracs, tmp328
# @OPUS@\upstream\silk\resampler.c:131:             S->Coefs = silk_Resampler_3_4_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp334
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L23:
# @OPUS@\upstream\silk\resampler.c:132:         } else if( silk_MUL( Fs_Hz_out, 3 ) == silk_MUL( Fs_Hz_in, 2 ) ) {      /* Fs_out : Fs_in = 2 : 3 */
	slli	a5, a14, 1	# tmp336, Fs_Hz_out,
	add.n	a3, a5, a14	# tmp337, tmp336, Fs_Hz_out
# @OPUS@\upstream\silk\resampler.c:132:         } else if( silk_MUL( Fs_Hz_out, 3 ) == silk_MUL( Fs_Hz_in, 2 ) ) {      /* Fs_out : Fs_in = 2 : 3 */
	bne	a3, a2, .L24	# tmp337, tmp330,
# @OPUS@\upstream\silk\resampler.c:133:             S->FIR_Fracs = 2;
	movi.n	a2, 2	# tmp339,
	s32i	a2, a12, 280	# S_97(D)->FIR_Fracs, tmp339
# @OPUS@\upstream\silk\resampler.c:134:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR0;
	movi.n	a2, 0x12	# tmp340,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp340
# @OPUS@\upstream\silk\resampler.c:135:             S->Coefs = silk_Resampler_2_3_COEFS;
	l32r	a2, .LC10	#, tmp341
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
# @OPUS@\upstream\silk\resampler.c:135:             S->Coefs = silk_Resampler_2_3_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp341
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L24:
# @OPUS@\upstream\silk\resampler.c:136:         } else if( silk_MUL( Fs_Hz_out, 2 ) == Fs_Hz_in ) {                     /* Fs_out : Fs_in = 1 : 2 */
	bne	a5, a15, .L25	# tmp336, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:137:             S->FIR_Fracs = 1;
	movi.n	a2, 1	# tmp343,
	s32i	a2, a12, 280	# S_97(D)->FIR_Fracs, tmp343
# @OPUS@\upstream\silk\resampler.c:138:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR1;
	movi.n	a2, 0x18	# tmp344,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp344
# @OPUS@\upstream\silk\resampler.c:139:             S->Coefs = silk_Resampler_1_2_COEFS;
	l32r	a2, .LC11	#, tmp345
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
# @OPUS@\upstream\silk\resampler.c:139:             S->Coefs = silk_Resampler_1_2_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp345
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L25:
# @OPUS@\upstream\silk\resampler.c:140:         } else if( silk_MUL( Fs_Hz_out, 3 ) == Fs_Hz_in ) {                     /* Fs_out : Fs_in = 1 : 3 */
	bne	a3, a15, .L26	# tmp337, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:141:             S->FIR_Fracs = 1;
	movi.n	a2, 1	# tmp346,
	s32i	a2, a12, 280	# S_97(D)->FIR_Fracs, tmp346
# @OPUS@\upstream\silk\resampler.c:142:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR2;
	movi.n	a2, 0x24	# tmp347,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp347
# @OPUS@\upstream\silk\resampler.c:143:             S->Coefs = silk_Resampler_1_3_COEFS;
	l32r	a2, .LC12	#, tmp348
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
# @OPUS@\upstream\silk\resampler.c:143:             S->Coefs = silk_Resampler_1_3_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp348
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L26:
# @OPUS@\upstream\silk\resampler.c:144:         } else if( silk_MUL( Fs_Hz_out, 4 ) == Fs_Hz_in ) {                     /* Fs_out : Fs_in = 1 : 4 */
	bne	a4, a15, .L27	# _59, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:145:             S->FIR_Fracs = 1;
	movi.n	a2, 1	# tmp349,
	s32i	a2, a12, 280	# S_97(D)->FIR_Fracs, tmp349
# @OPUS@\upstream\silk\resampler.c:146:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR2;
	movi.n	a2, 0x24	# tmp350,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp350
# @OPUS@\upstream\silk\resampler.c:147:             S->Coefs = silk_Resampler_1_4_COEFS;
	l32r	a2, .LC13	#, tmp351
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
# @OPUS@\upstream\silk\resampler.c:147:             S->Coefs = silk_Resampler_1_4_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp351
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L27:
# @OPUS@\upstream\silk\resampler.c:148:         } else if( silk_MUL( Fs_Hz_out, 6 ) == Fs_Hz_in ) {                     /* Fs_out : Fs_in = 1 : 6 */
	slli	a3, a3, 1	# tmp355, tmp337,
# @OPUS@\upstream\silk\resampler.c:148:         } else if( silk_MUL( Fs_Hz_out, 6 ) == Fs_Hz_in ) {                     /* Fs_out : Fs_in = 1 : 6 */
	bne	a3, a15, .L5	# tmp355, Fs_Hz_in,
# @OPUS@\upstream\silk\resampler.c:149:             S->FIR_Fracs = 1;
	movi.n	a2, 1	# tmp356,
	s32i	a2, a12, 280	# S_97(D)->FIR_Fracs, tmp356
# @OPUS@\upstream\silk\resampler.c:150:             S->FIR_Order = RESAMPLER_DOWN_ORDER_FIR2;
	movi.n	a2, 0x24	# tmp357,
	s32i	a2, a12, 276	# S_97(D)->FIR_Order, tmp357
# @OPUS@\upstream\silk\resampler.c:151:             S->Coefs = silk_Resampler_1_6_COEFS;
	l32r	a2, .LC14	#, tmp358
# @OPUS@\upstream\silk\resampler.c:114:     up2x = 0;
	movi.n	a13, 0	# up2x,
# @OPUS@\upstream\silk\resampler.c:151:             S->Coefs = silk_Resampler_1_6_COEFS;
	s32i	a2, a12, 296	# S_97(D)->Coefs, tmp358
	movi.n	a2, 0xe	# prephitmp_197,
	j	.L21		#
.L22:
# @OPUS@\upstream\silk\resampler.c:159:         S->resampler_function = USE_silk_resampler_copy;
	movi.n	a13, 0	# tmp359,
	s32i	a13, a12, 264	# S_97(D)->resampler_function, tmp359
	movi.n	a2, 0xe	# prephitmp_197,
.L21:
# @OPUS@\upstream\silk\resampler.c:163:     S->invRatio_Q16 = silk_LSHIFT32( silk_DIV32( silk_LSHIFT32( Fs_Hz_in, 14 + up2x ), Fs_Hz_out ), 2 );
	mov.n	a3, a14	#, Fs_Hz_out
	ssl	a2	# prephitmp_197
	sll	a2, a15	#, Fs_Hz_in
	call0	__divsi3		#
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	srai	a8, a14, 15	# tmp366, Fs_Hz_out,
# @OPUS@\upstream\silk\resampler.c:163:     S->invRatio_Q16 = silk_LSHIFT32( silk_DIV32( silk_LSHIFT32( Fs_Hz_in, 14 + up2x ), Fs_Hz_out ), 2 );
	slli	a2, a2, 2	# _72,,
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	slli	a6, a14, 16	# tmp365, Fs_Hz_out,
	addi.n	a8, a8, 1	# tmp367, tmp366,
	srai	a6, a6, 16	# _140, tmp365,
	srai	a8, a8, 1	# _131, tmp367,
	extui	a3, a2, 0, 16	# tmp368, _72,
	srai	a4, a2, 16	# tmp371, _72,
	mull	a7, a2, a8	# _138, _72, _131
	mull	a3, a3, a6	# tmp369, tmp368, _140
	mull	a4, a4, a6	# tmp372, tmp371, _140
	srai	a3, a3, 16	# tmp370, tmp369,
	add.n	a4, a4, a7	# tmp373, tmp372, _138
# @OPUS@\upstream\silk\resampler.c:163:     S->invRatio_Q16 = silk_LSHIFT32( silk_DIV32( silk_LSHIFT32( Fs_Hz_in, 14 + up2x ), Fs_Hz_out ), 2 );
	s32i	a2, a12, 272	# S_97(D)->invRatio_Q16, _72
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	ssl	a13	# up2x
	sll	a13, a15	# _136, Fs_Hz_in
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	add.n	a3, a3, a4	# tmp374, tmp370, tmp373
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	bge	a3, a13, .L29	# tmp374, _136,
	addi.n	a2, a2, 1	# ivtmp$9, _72,
	add.n	a7, a8, a7	# ivtmp$11, _131, _138
.L28:
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	extui	a4, a2, 0, 16	# tmp375, ivtmp$9,
	srai	a5, a2, 16	# tmp378, ivtmp$9,
	mull	a4, a4, a6	# tmp376, tmp375, _140
	mull	a5, a5, a6	# tmp379, tmp378, _140
	srai	a4, a4, 16	# tmp377, tmp376,
	add.n	a5, a5, a7	# tmp380, tmp379, ivtmp$11
	add.n	a4, a4, a5	# _87, tmp377, tmp380
# @OPUS@\upstream\silk\resampler.c:166:         S->invRatio_Q16++;
	mov.n	a3, a2	# _73, ivtmp$9
	add.n	a7, a7, a8	# ivtmp$11, ivtmp$11, _131
	addi.n	a2, a2, 1	# ivtmp$9, ivtmp$9,
# @OPUS@\upstream\silk\resampler.c:165:     while( silk_SMULWW( S->invRatio_Q16, Fs_Hz_out ) < silk_LSHIFT32( Fs_Hz_in, up2x ) ) {
	blt	a4, a13, .L28	# _87, _136,
	s32i	a3, a12, 272	# S_97(D)->invRatio_Q16, _73
# @OPUS@\upstream\silk\resampler.c:169:     return 0;
	movi.n	a2, 0	# <retval>,
	j	.L1		#
.L29:
	movi.n	a2, 0	# <retval>,
.L1:
# @OPUS@\upstream\silk\resampler.c:170: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_resampler_init, .-silk_resampler_init
	.section	.text.silk_resampler,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_resampler
	.type	silk_resampler, @function
# Function: silk_resampler
# Module: upstream/silk/resampler.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Resampler: convert from one sampling rate to another */
# C context: /* Input and output sampling rate are at most 48000 Hz  */
# C context: opus_int silk_resampler(
# C context: silk_resampler_state_struct *S,                 /* I/O  Resampler state                                             */
# C context: opus_int16                  out[],              /* O    Output signal                                               */
# C context: const opus_int16            in[],               /* I    Input signal                                                */
# C context: opus_int32                  inLen               /* I    Number of input samples                                     */
silk_resampler:
	addi	sp, sp, -48	#,,
# @OPUS@\upstream\silk\resampler.c:188:     nSamples = S->Fs_in_kHz - S->inputDelay;
	l32i	a6, a2, 292	# S_57(D)->inputDelay, _2
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a13, sp, 36	#,
# @OPUS@\upstream\silk\resampler.c:188:     nSamples = S->Fs_in_kHz - S->inputDelay;
	l32i	a13, a2, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a12, sp, 40	#,
# @OPUS@\upstream\silk\resampler.c:188:     nSamples = S->Fs_in_kHz - S->inputDelay;
	sub	a13, a13, a6	# nSamples, S_57(D)->Fs_in_kHz, _2
# @OPUS@\upstream\silk\resampler.c:180: {
	mov.n	a12, a2	# S, S
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	addi	a2, a6, 84	# tmp100, _2,
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a14, sp, 32	#,
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	slli	a13, a13, 1	# _5, nSamples,
# @OPUS@\upstream\silk\resampler.c:180: {
	mov.n	a14, a4	# in, in
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	slli	a2, a2, 1	# tmp101, tmp100,
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	mov.n	a4, a13	#, _5
# @OPUS@\upstream\silk\resampler.c:180: {
	mov.n	a15, a3	# out, out
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	add.n	a2, a12, a2	#, S, tmp101
	mov.n	a3, a14	#, in
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\silk\resampler.c:180: {
	s32i.n	a5, sp, 0	# %sfp, inLen
# @OPUS@\upstream\silk\resampler.c:191:     silk_memcpy( &S->delayBuf[ S->inputDelay ], in, nSamples * sizeof( opus_int16 ) );
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler.c:193:     switch( S->resampler_function ) {
	l32i	a2, a12, 264	# S_57(D)->resampler_function, _6
	movi	a6, 0xa8	# tmp107,
	add.n	a6, a12, a6	# pretmp_95, S, tmp107
	add.n	a13, a14, a13	# _96, in, _5
# @OPUS@\upstream\silk\resampler.c:193:     switch( S->resampler_function ) {
	beqi	a2, 2, .L60	# _6,,
	beqi	a2, 3, .L61	# _6,,
	bnei	a2, 1, .L62	# _6,,
# @OPUS@\upstream\silk\resampler.c:195:             silk_resampler_private_up2_HQ_wrapper( S, out, S->delayBuf, S->Fs_in_kHz );
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz,
	mov.n	a4, a6	#, pretmp_95
	mov.n	a3, a15	#, out
	mov.n	a2, a12	#, S
	s32i.n	a6, sp, 4	#,
	call0	silk_resampler_private_up2_HQ_wrapper		#
# @OPUS@\upstream\silk\resampler.c:196:             silk_resampler_private_up2_HQ_wrapper( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i	a3, a12, 288	# S_57(D)->Fs_out_kHz, S_57(D)->Fs_out_kHz
# @OPUS@\upstream\silk\resampler.c:196:             silk_resampler_private_up2_HQ_wrapper( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i.n	a2, sp, 0	# %sfp,
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
# @OPUS@\upstream\silk\resampler.c:196:             silk_resampler_private_up2_HQ_wrapper( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	slli	a3, a3, 1	# tmp110, S_57(D)->Fs_out_kHz,
# @OPUS@\upstream\silk\resampler.c:196:             silk_resampler_private_up2_HQ_wrapper( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	sub	a5, a2, a5	#,, S_57(D)->Fs_in_kHz
	mov.n	a4, a13	#, _96
	add.n	a3, a15, a3	#, out, tmp110
	mov.n	a2, a12	#, S
	call0	silk_resampler_private_up2_HQ_wrapper		#
# @OPUS@\upstream\silk\resampler.c:197:             break;
	l32i.n	a6, sp, 4	#,
	j	.L63		#
.L60:
# @OPUS@\upstream\silk\resampler.c:199:             silk_resampler_private_IIR_FIR( S, out, S->delayBuf, S->Fs_in_kHz );
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz,
	mov.n	a4, a6	#, pretmp_95
	mov.n	a3, a15	#, out
	mov.n	a2, a12	#, S
	s32i.n	a6, sp, 4	#,
	call0	silk_resampler_private_IIR_FIR		#
# @OPUS@\upstream\silk\resampler.c:200:             silk_resampler_private_IIR_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i	a3, a12, 288	# S_57(D)->Fs_out_kHz, S_57(D)->Fs_out_kHz
# @OPUS@\upstream\silk\resampler.c:200:             silk_resampler_private_IIR_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i.n	a2, sp, 0	# %sfp,
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
# @OPUS@\upstream\silk\resampler.c:200:             silk_resampler_private_IIR_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	slli	a3, a3, 1	# tmp115, S_57(D)->Fs_out_kHz,
# @OPUS@\upstream\silk\resampler.c:200:             silk_resampler_private_IIR_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	sub	a5, a2, a5	#,, S_57(D)->Fs_in_kHz
	mov.n	a4, a13	#, _96
	add.n	a3, a15, a3	#, out, tmp115
	mov.n	a2, a12	#, S
	call0	silk_resampler_private_IIR_FIR		#
# @OPUS@\upstream\silk\resampler.c:201:             break;
	l32i.n	a6, sp, 4	#,
	j	.L63		#
.L61:
# @OPUS@\upstream\silk\resampler.c:203:             silk_resampler_private_down_FIR( S, out, S->delayBuf, S->Fs_in_kHz );
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz,
	mov.n	a4, a6	#, pretmp_95
	mov.n	a3, a15	#, out
	mov.n	a2, a12	#, S
	s32i.n	a6, sp, 4	#,
	call0	silk_resampler_private_down_FIR		#
# @OPUS@\upstream\silk\resampler.c:204:             silk_resampler_private_down_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i	a3, a12, 288	# S_57(D)->Fs_out_kHz, S_57(D)->Fs_out_kHz
# @OPUS@\upstream\silk\resampler.c:204:             silk_resampler_private_down_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	l32i.n	a2, sp, 0	# %sfp,
	l32i	a5, a12, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
# @OPUS@\upstream\silk\resampler.c:204:             silk_resampler_private_down_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	slli	a3, a3, 1	# tmp120, S_57(D)->Fs_out_kHz,
# @OPUS@\upstream\silk\resampler.c:204:             silk_resampler_private_down_FIR( S, &out[ S->Fs_out_kHz ], &in[ nSamples ], inLen - S->Fs_in_kHz );
	sub	a5, a2, a5	#,, S_57(D)->Fs_in_kHz
	mov.n	a4, a13	#, _96
	add.n	a3, a15, a3	#, out, tmp120
	mov.n	a2, a12	#, S
	call0	silk_resampler_private_down_FIR		#
# @OPUS@\upstream\silk\resampler.c:205:             break;
	l32i.n	a6, sp, 4	#,
	j	.L63		#
.L62:
# @OPUS@\upstream\silk\resampler.c:207:             silk_memcpy( out, S->delayBuf, S->Fs_in_kHz * sizeof( opus_int16 ) );
	l32i	a4, a12, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
	mov.n	a3, a6	#, pretmp_95
	slli	a4, a4, 1	#, S_57(D)->Fs_in_kHz,
	mov.n	a2, a15	#, out
	s32i.n	a6, sp, 4	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler.c:208:             silk_memcpy( &out[ S->Fs_out_kHz ], &in[ nSamples ], ( inLen - S->Fs_in_kHz ) * sizeof( opus_int16 ) );
	l32i.n	a3, sp, 0	# %sfp,
	l32i	a2, a12, 288	# S_57(D)->Fs_out_kHz, S_57(D)->Fs_out_kHz
	l32i	a4, a12, 284	# S_57(D)->Fs_in_kHz, S_57(D)->Fs_in_kHz
	slli	a2, a2, 1	# tmp129, S_57(D)->Fs_out_kHz,
	sub	a4, a3, a4	# tmp132,, S_57(D)->Fs_in_kHz
	slli	a4, a4, 1	#, tmp132,
	mov.n	a3, a13	#, _96
	add.n	a2, a15, a2	#, out, tmp129
	call0	memcpy		#
	l32i.n	a6, sp, 4	#,
.L63:
# @OPUS@\upstream\silk\resampler.c:212:     silk_memcpy( S->delayBuf, &in[ inLen - S->inputDelay ], S->inputDelay * sizeof( opus_int16 ) );
	l32i	a4, a12, 292	# S_57(D)->inputDelay, _48
	l32i.n	a5, sp, 0	# %sfp,
	mov.n	a2, a6	#, pretmp_95
	sub	a3, a5, a4	# tmp140,, _48
	slli	a3, a3, 1	# tmp141, tmp140,
	add.n	a3, a14, a3	#, in, tmp141
	slli	a4, a4, 1	#, _48,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler.c:215: }
	l32i.n	a0, sp, 44	#,
	movi.n	a2, 0	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_resampler, .-silk_resampler
	.section	.rodata.delay_matrix_dec,"a"
	.align	4
	.type	delay_matrix_dec, @object
	.size	delay_matrix_dec, 15
delay_matrix_dec:
	.byte	4
	.byte	0
	.byte	2
	.byte	0
	.byte	0
	.byte	0
	.byte	9
	.byte	4
	.byte	7
	.byte	4
	.byte	0
	.byte	3
	.byte	12
	.byte	7
	.byte	7
	.section	.rodata.delay_matrix_enc,"a"
	.align	4
	.type	delay_matrix_enc, @object
	.size	delay_matrix_enc, 15
delay_matrix_enc:
	.byte	6
	.byte	0
	.byte	3
	.byte	0
	.byte	7
	.byte	3
	.byte	0
	.byte	1
	.byte	10
	.byte	0
	.byte	2
	.byte	6
	.byte	18
	.byte	10
	.byte	12
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
