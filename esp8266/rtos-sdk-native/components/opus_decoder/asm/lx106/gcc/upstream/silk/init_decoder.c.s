# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/init_decoder.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"init_decoder.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\init_decoder.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\init_decoder.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\init_decoder.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\init_decoder.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\init_decoder.c.s.raw
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
	.section	.text.silk_reset_decoder,"ax",@progbits
	.literal_position
	.literal .LC0, 2988
	.literal .LC1, 65536
	.align	4
	.global	silk_reset_decoder
	.type	silk_reset_decoder, @function
# Function: silk_reset_decoder
# Module: upstream/silk/init_decoder.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /************************/
# C context: /* Reset Decoder State  */
# C context: /************************/
# C context: opus_int silk_reset_decoder(
# C context: silk_decoder_state          *psDec                          /* I/O  Decoder state pointer                       */
# C context: )
# C context: {
# C context: /* Clear the entire encoder state, except anything copied */
silk_reset_decoder:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	l32r	a4, .LC0	#,
# @OPUS@\upstream\silk\init_decoder.c:49: {
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	movi.n	a3, 0	#,
# @OPUS@\upstream\silk\init_decoder.c:49: {
	mov.n	a12, a2	# psDec, psDec
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	addi.n	a2, a2, 4	#, psDec,
# @OPUS@\upstream\silk\init_decoder.c:49: {
	s32i.n	a0, sp, 12	#,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	call0	memset		#
# @OPUS@\upstream\silk\init_decoder.c:53:     yoradio_opus_clear(psDec->exc_Q14, MAX_FRAME_LENGTH, sizeof(opus_int32));
	l32i.n	a2, a12, 0	# psDec_3(D)->exc_Q14,
	movi.n	a4, 4	#,
	movi	a3, 0x140	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\silk\init_decoder.c:57:     psDec->first_frame_after_reset = 1;
	addmi	a2, a12, 0x400	# tmp51, psDec,
	movi.n	a3, 1	# tmp52,
	s32i	a3, a2, 76	# psDec_3(D)->first_frame_after_reset, tmp52
# @OPUS@\upstream\silk\init_decoder.c:58:     psDec->prev_gain_Q16 = 65536;
	l32r	a2, .LC1	#, tmp53
# @OPUS@\upstream\silk\init_decoder.c:59:     psDec->arch = opus_select_arch();
	movi.n	a13, 0	# tmp55,
# @OPUS@\upstream\silk\init_decoder.c:58:     psDec->prev_gain_Q16 = 65536;
	s32i.n	a2, a12, 4	# psDec_3(D)->prev_gain_Q16, tmp53
# @OPUS@\upstream\silk\init_decoder.c:59:     psDec->arch = opus_select_arch();
	addmi	a2, a12, 0xb00	# tmp54, psDec,
	s32i	a13, a2, 76	# psDec_3(D)->arch, tmp55
# @OPUS@\upstream\silk\init_decoder.c:62:     silk_CNG_Reset( psDec );
	mov.n	a2, a12	#, psDec
	call0	silk_CNG_Reset		#
# @OPUS@\upstream\silk\init_decoder.c:65:     silk_PLC_Reset( psDec );
	mov.n	a2, a12	#, psDec
	call0	silk_PLC_Reset		#
# @OPUS@\upstream\silk\init_decoder.c:73: }
	l32i.n	a0, sp, 12	#,
	mov.n	a2, a13	#, tmp55
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_reset_decoder, .-silk_reset_decoder
	.section	.text.silk_init_decoder,"ax",@progbits
	.literal_position
	.literal .LC2, 2992
	.literal .LC3, 2988
	.literal .LC4, 65536
	.align	4
	.global	silk_init_decoder
	.type	silk_init_decoder, @function
# Function: silk_init_decoder
# Module: upstream/silk/init_decoder.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /************************/
# C context: /* Init Decoder State   */
# C context: /************************/
# C context: opus_int silk_init_decoder(
# C context: silk_decoder_state          *psDec                          /* I/O  Decoder state pointer                       */
# C context: )
# C context: {
# C context: #ifdef YORADIO_OPUS_BOUNDED
silk_init_decoder:
# @OPUS@\upstream\silk\init_decoder.c:89:     silk_memset( psDec, 0, sizeof( silk_decoder_state ) );
	l32r	a4, .LC2	#,
# @OPUS@\upstream\silk\init_decoder.c:82: {
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\init_decoder.c:89:     silk_memset( psDec, 0, sizeof( silk_decoder_state ) );
	movi.n	a3, 0	#,
# @OPUS@\upstream\silk\init_decoder.c:82: {
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\silk\init_decoder.c:82: {
	mov.n	a12, a2	# psDec, psDec
# @OPUS@\upstream\silk\init_decoder.c:86:     opus_int32 *exc = psDec->exc_Q14;
	l32i.n	a13, a2, 0	# psDec_2(D)->exc_Q14, exc
# @OPUS@\upstream\silk\init_decoder.c:89:     silk_memset( psDec, 0, sizeof( silk_decoder_state ) );
	call0	memset		#
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	l32r	a4, .LC3	#,
# @OPUS@\upstream\silk\init_decoder.c:91:     psDec->exc_Q14 = exc;
	s32i.n	a13, a12, 0	# psDec_2(D)->exc_Q14, exc
# @OPUS@\upstream\silk\init_decoder.c:51:     silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
	movi.n	a3, 0	#,
	addi.n	a2, a12, 4	#, psDec,
	call0	memset		#
# @OPUS@\upstream\silk\init_decoder.c:53:     yoradio_opus_clear(psDec->exc_Q14, MAX_FRAME_LENGTH, sizeof(opus_int32));
	movi.n	a4, 4	#,
	mov.n	a2, a13	#, exc
	movi	a3, 0x140	#,
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\silk\init_decoder.c:57:     psDec->first_frame_after_reset = 1;
	addmi	a2, a12, 0x400	# tmp54, psDec,
	movi.n	a3, 1	# tmp55,
	s32i	a3, a2, 76	# psDec_2(D)->first_frame_after_reset, tmp55
# @OPUS@\upstream\silk\init_decoder.c:58:     psDec->prev_gain_Q16 = 65536;
	l32r	a2, .LC4	#, tmp56
# @OPUS@\upstream\silk\init_decoder.c:59:     psDec->arch = opus_select_arch();
	movi.n	a13, 0	# tmp58,
# @OPUS@\upstream\silk\init_decoder.c:58:     psDec->prev_gain_Q16 = 65536;
	s32i.n	a2, a12, 4	# psDec_2(D)->prev_gain_Q16, tmp56
# @OPUS@\upstream\silk\init_decoder.c:59:     psDec->arch = opus_select_arch();
	addmi	a2, a12, 0xb00	# tmp57, psDec,
	s32i	a13, a2, 76	# psDec_2(D)->arch, tmp58
# @OPUS@\upstream\silk\init_decoder.c:62:     silk_CNG_Reset( psDec );
	mov.n	a2, a12	#, psDec
	call0	silk_CNG_Reset		#
# @OPUS@\upstream\silk\init_decoder.c:65:     silk_PLC_Reset( psDec );
	mov.n	a2, a12	#, psDec
	call0	silk_PLC_Reset		#
# @OPUS@\upstream\silk\init_decoder.c:97: }
	l32i.n	a0, sp, 12	#,
	mov.n	a2, a13	#, tmp58
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_init_decoder, .-silk_init_decoder
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
