# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/bwexpander_32.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"bwexpander_32.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\bwexpander_32.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\bwexpander_32.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\bwexpander_32.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\bwexpander_32.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\bwexpander_32.c.s.raw
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
	.section	.text.silk_bwexpander_32,"ax",@progbits
	.literal_position
	.literal .LC0, -65536
	.align	4
	.global	silk_bwexpander_32
	.type	silk_bwexpander_32, @function
# Function: silk_bwexpander_32
# Module: upstream/silk/bwexpander_32.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Chirp (bandwidth expand) LP AR filter.
# C context: This logic is reused in _celt_lpc(). Any bug fixes should also be applied there. */
# C context: void silk_bwexpander_32(
# C context: opus_int32                  *ar,                /* I/O  AR filter to be expanded (without leading 1)                */
# C context: const opus_int              d,                  /* I    Length of ar                                                */
# C context: opus_int32                  chirp_Q16           /* I    Chirp factor in Q16                                         */
# C context: )
silk_bwexpander_32:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\silk\bwexpander_32.c:43:     opus_int32 chirp_minus_one_Q16 = chirp_Q16 - 65536;
	l32r	a8, .LC0	#, tmp89
# @OPUS@\upstream\silk\bwexpander_32.c:41: {
	s32i.n	a12, sp, 12	#,
# @OPUS@\upstream\silk\bwexpander_32.c:45:     for( i = 0; i < d - 1; i++ ) {
	addi.n	a5, a3, -1	# tmp90, d,
# @OPUS@\upstream\silk\bwexpander_32.c:43:     opus_int32 chirp_minus_one_Q16 = chirp_Q16 - 65536;
	add.n	a8, a4, a8	# chirp_minus_one_Q16, chirp_Q16, tmp89
# @OPUS@\upstream\silk\bwexpander_32.c:45:     for( i = 0; i < d - 1; i++ ) {
	blti	a5, 1, .L2	# tmp90,,
	addi	a7, a2, -4	# tmp91, ar,
	slli	a5, a3, 2	# tmp92, d,
	mov.n	a6, a2	# ivtmp$10, ar
	add.n	a7, a7, a5	# _111, tmp91, tmp92
.L3:
# @OPUS@\upstream\silk\bwexpander_32.c:46:         ar[ i ]    = silk_SMULWW( chirp_Q16, ar[ i ] );
	l32i.n	a5, a6, 0	# MEM[base: _121, offset: 0B], _5
	l16si	a11, a6, 0	# MEM[base: _121, offset: 0B], _7
	srai	a5, a5, 15	# tmp94, _5,
	extui	a10, a4, 0, 16	# tmp98, chirp_Q16,
	addi.n	a5, a5, 1	# tmp95, tmp94,
	mull	a10, a10, a11	# tmp99, tmp98, _7
	srai	a5, a5, 1	# tmp96, tmp95,
	mull	a5, a5, a4	# tmp97, tmp96, chirp_Q16
	srai	a12, a4, 16	# tmp102, chirp_Q16,
# @OPUS@\upstream\silk\bwexpander_32.c:47:         chirp_Q16 += silk_RSHIFT_ROUND( silk_MUL( chirp_Q16, chirp_minus_one_Q16 ), 16 );
	mull	a9, a8, a4	# tmp105, chirp_minus_one_Q16, chirp_Q16
# @OPUS@\upstream\silk\bwexpander_32.c:46:         ar[ i ]    = silk_SMULWW( chirp_Q16, ar[ i ] );
	srai	a10, a10, 16	# tmp100, tmp99,
	mull	a11, a12, a11	# tmp103, tmp102, _7
	add.n	a5, a5, a10	# tmp101, tmp97, tmp100
# @OPUS@\upstream\silk\bwexpander_32.c:47:         chirp_Q16 += silk_RSHIFT_ROUND( silk_MUL( chirp_Q16, chirp_minus_one_Q16 ), 16 );
	srai	a9, a9, 15	# tmp106, tmp105,
# @OPUS@\upstream\silk\bwexpander_32.c:46:         ar[ i ]    = silk_SMULWW( chirp_Q16, ar[ i ] );
	add.n	a5, a5, a11	# tmp104, tmp101, tmp103
# @OPUS@\upstream\silk\bwexpander_32.c:47:         chirp_Q16 += silk_RSHIFT_ROUND( silk_MUL( chirp_Q16, chirp_minus_one_Q16 ), 16 );
	addi.n	a9, a9, 1	# tmp107, tmp106,
# @OPUS@\upstream\silk\bwexpander_32.c:46:         ar[ i ]    = silk_SMULWW( chirp_Q16, ar[ i ] );
	s32i.n	a5, a6, 0	# MEM[base: _121, offset: 0B], tmp104
# @OPUS@\upstream\silk\bwexpander_32.c:47:         chirp_Q16 += silk_RSHIFT_ROUND( silk_MUL( chirp_Q16, chirp_minus_one_Q16 ), 16 );
	srai	a5, a9, 1	# _21, tmp107,
	addi.n	a6, a6, 4	# ivtmp$10, ivtmp$10,
# @OPUS@\upstream\silk\bwexpander_32.c:47:         chirp_Q16 += silk_RSHIFT_ROUND( silk_MUL( chirp_Q16, chirp_minus_one_Q16 ), 16 );
	add.n	a4, a4, a5	# chirp_Q16, chirp_Q16, _21
# @OPUS@\upstream\silk\bwexpander_32.c:45:     for( i = 0; i < d - 1; i++ ) {
	bne	a7, a6, .L3	# _111, ivtmp$10,
.L2:
# @OPUS@\upstream\silk\bwexpander_32.c:49:     ar[ d - 1 ] = silk_SMULWW( chirp_Q16, ar[ d - 1 ] );
	slli	a3, a3, 2	# tmp108, d,
	addi	a3, a3, -4	# tmp110, tmp108,
	add.n	a2, a2, a3	# _27, ar, tmp110
	l32i.n	a5, a2, 0	# *_27, _28
	l16si	a7, a2, 0	# *_27, _30
	srai	a5, a5, 15	# tmp112, _28,
	addi.n	a5, a5, 1	# tmp113, tmp112,
	srai	a6, a4, 16	# tmp116, chirp_Q16,
	extui	a3, a4, 0, 16	# tmp119, chirp_Q16,
	srai	a5, a5, 1	# tmp114, tmp113,
	mull	a4, a5, a4	# tmp115, tmp114, chirp_Q16
	mull	a6, a6, a7	# tmp117, tmp116, _30
	mull	a3, a3, a7	# tmp120, tmp119, _30
	add.n	a4, a4, a6	# tmp118, tmp115, tmp117
	srai	a3, a3, 16	# tmp121, tmp120,
	add.n	a4, a4, a3	# tmp122, tmp118, tmp121
# @OPUS@\upstream\silk\bwexpander_32.c:50: }
	l32i.n	a12, sp, 12	#,
# @OPUS@\upstream\silk\bwexpander_32.c:49:     ar[ d - 1 ] = silk_SMULWW( chirp_Q16, ar[ d - 1 ] );
	s32i.n	a4, a2, 0	# *_27, tmp122
# @OPUS@\upstream\silk\bwexpander_32.c:50: }
	addi	sp, sp, 16	#,,
	ret.n
	.size	silk_bwexpander_32, .-silk_bwexpander_32
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
