# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/sort.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"sort.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\sort.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\sort.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\sort.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\sort.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\sort.c.s.raw
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
	.section	.text.silk_insertion_sort_increasing,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_insertion_sort_increasing
	.type	silk_insertion_sort_increasing, @function
# Function: silk_insertion_sort_increasing
# Module: upstream/silk/sort.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #include "SigProc_FIX.h"
# C context:
# C context: void silk_insertion_sort_increasing(
# C context: opus_int32           *a,             /* I/O   Unsorted / Sorted vector               */
# C context: opus_int             *idx,           /* O     Index vector for the sorted elements   */
# C context: const opus_int       L,              /* I     Vector length                          */
# C context: const opus_int       K               /* I     Number of correctly sorted positions   */
silk_insertion_sort_increasing:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
	mov.n	a7, a3	# ivtmp$88, idx
# @OPUS@\upstream\silk\sort.c:56:     for( i = 0; i < K; i++ ) {
	movi.n	a6, 0	# i,
# @OPUS@\upstream\silk\sort.c:56:     for( i = 0; i < K; i++ ) {
	bgei	a5, 1, .L5	# K,,
	j	.L13		#
.L30:
	addi.n	a12, a2, 4	# ivtmp$81, a,
	mov.n	a14, a3	# ivtmp$83, idx
# @OPUS@\upstream\silk\sort.c:61:     for( i = 1; i < K; i++ ) {
	movi.n	a13, 1	# i,
# @OPUS@\upstream\silk\sort.c:61:     for( i = 1; i < K; i++ ) {
	bgei	a5, 2, .L12	# K,,
	j	.L13		#
.L5:
# @OPUS@\upstream\silk\sort.c:57:         idx[ i ] = i;
	s32i.n	a6, a7, 0	# MEM[base: _147, offset: 0B], i
# @OPUS@\upstream\silk\sort.c:56:     for( i = 0; i < K; i++ ) {
	addi.n	a6, a6, 1	# i, i,
	addi.n	a7, a7, 4	# ivtmp$88, ivtmp$88,
# @OPUS@\upstream\silk\sort.c:56:     for( i = 0; i < K; i++ ) {
	bne	a5, a6, .L5	# K, i,
	j	.L30		#
.L13:
# @OPUS@\upstream\silk\sort.c:73:     for( i = K; i < L; i++ ) {
	blt	a5, a4, .L7	# K, L,
	j	.L1		#
.L12:
# @OPUS@\upstream\silk\sort.c:62:         value = a[ i ];
	l32i.n	a11, a12, 0	# MEM[base: _160, offset: 0B], value
	addi	a8, a12, -4	# ivtmp$69, ivtmp$81,
	mov.n	a6, a14	# ivtmp$71, ivtmp$83
	mov.n	a7, a12	# ivtmp$70, ivtmp$81
	j	.L9		#
.L11:
# @OPUS@\upstream\silk\sort.c:64:             a[ j + 1 ]   = a[ j ];       /* Shift value */
	s32i.n	a9, a7, 0	# MEM[base: _156, offset: 0B], _16
# @OPUS@\upstream\silk\sort.c:65:             idx[ j + 1 ] = idx[ j ];     /* Shift index */
	l32i.n	a9, a6, 0	# MEM[base: _54, offset: 0B], MEM[base: _54, offset: 0B]
	addi	a7, a10, -4	# ivtmp$70, _156,
	s32i.n	a9, a6, 4	# MEM[base: _54, offset: 4B], MEM[base: _54, offset: 0B]
	addi	a8, a8, -4	# ivtmp$69, ivtmp$69,
	addi	a6, a6, -4	# ivtmp$71, ivtmp$71,
# @OPUS@\upstream\silk\sort.c:63:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	beq	a2, a7, .L18	# a, ivtmp$70,
.L9:
# @OPUS@\upstream\silk\sort.c:63:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	l32i.n	a9, a8, 0	# MEM[base: _57, offset: 0B], _16
	mov.n	a10, a7	# _156, ivtmp$70
	addi.n	a15, a6, 4	# _82, ivtmp$71,
# @OPUS@\upstream\silk\sort.c:63:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	blt	a11, a9, .L11	# value, _16,
	j	.L10		#
.L18:
	mov.n	a15, a3	# _82, idx
	mov.n	a10, a2	# _156, a
.L10:
# @OPUS@\upstream\silk\sort.c:67:         a[ j + 1 ]   = value;   /* Write value */
	s32i.n	a11, a10, 0	# *prephitmp_161, value
# @OPUS@\upstream\silk\sort.c:68:         idx[ j + 1 ] = i;       /* Write index */
	s32i.n	a13, a15, 0	# *prephitmp_162, i
# @OPUS@\upstream\silk\sort.c:61:     for( i = 1; i < K; i++ ) {
	addi.n	a13, a13, 1	# i, i,
	addi.n	a12, a12, 4	# ivtmp$81, ivtmp$81,
	addi.n	a14, a14, 4	# ivtmp$83, ivtmp$83,
# @OPUS@\upstream\silk\sort.c:61:     for( i = 1; i < K; i++ ) {
	bne	a5, a13, .L12	# K, i,
	j	.L13		#
.L7:
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	addi	a15, a5, -2	# j, K,
	addi	a12, a5, -3	# tmp105, K,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	slli	a13, a15, 2	# _94, j,
	slli	a12, a12, 2	# _166, tmp105,
	add.n	a6, a2, a13	#, a, _94
# @OPUS@\upstream\silk\sort.c:75:         if( value < a[ K - 1 ] ) {
	slli	a14, a5, 2	# tmp102, K,
	addi	a14, a14, -4	# tmp104, tmp102,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	s32i.n	a6, sp, 0	# %sfp,
	add.n	a6, a2, a12	#, a, _166
# @OPUS@\upstream\silk\sort.c:75:         if( value < a[ K - 1 ] ) {
	add.n	a14, a2, a14	# _28, a, tmp104
	s32i.n	a6, sp, 4	# %sfp,
	addi.n	a12, a12, 8	# tmp117, _166,
.L17:
# @OPUS@\upstream\silk\sort.c:74:         value = a[ i ];
	slli	a6, a5, 2	# tmp106, K,
	add.n	a6, a2, a6	# tmp107, a, tmp106
	l32i.n	a10, a6, 0	# MEM[base: _126, offset: 0B], value
# @OPUS@\upstream\silk\sort.c:75:         if( value < a[ K - 1 ] ) {
	l32i.n	a6, a14, 0	# *_28, *_28
	bge	a10, a6, .L14	# value, *_28,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	bltz	a15, .L20	# j,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	l32i.n	a6, sp, 0	# %sfp,
	l32i.n	a9, a6, 0	# *_88, _41
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	bge	a10, a9, .L20	# value, _41,
	l32i.n	a8, sp, 4	# %sfp, ivtmp$54
	add.n	a7, a3, a13	# ivtmp$51, idx, _94
	mov.n	a6, a15	# j, j
.L16:
# @OPUS@\upstream\silk\sort.c:77:                 a[ j + 1 ]   = a[ j ];       /* Shift value */
	s32i.n	a9, a8, 8	# MEM[base: _151, offset: 8B], _41
# @OPUS@\upstream\silk\sort.c:78:                 idx[ j + 1 ] = idx[ j ];     /* Shift index */
	l32i.n	a11, a7, 0	# MEM[base: _150, offset: 0B], _37
# @OPUS@\upstream\silk\sort.c:78:                 idx[ j + 1 ] = idx[ j ];     /* Shift index */
	sub	a9, a7, a13	# tmp109, ivtmp$51, _94
	add.n	a9, a9, a12	# tmp111, tmp109, tmp117
	s32i.n	a11, a9, 0	# MEM[base: _130, offset: 0B], _37
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	addi.n	a6, a6, -1	# j, j,
	mov.n	a11, a6	# _152, j
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	beqi	a6, -1, .L15	# j,,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	l32i.n	a9, a8, 0	# MEM[base: _151, offset: 0B], _41
	addi	a7, a7, -4	# ivtmp$51, ivtmp$51,
	addi	a8, a8, -4	# ivtmp$54, ivtmp$54,
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	blt	a10, a9, .L16	# value, _41,
	j	.L15		#
.L20:
# @OPUS@\upstream\silk\sort.c:76:             for( j = K - 2; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	mov.n	a11, a15	# _152, j
.L15:
# @OPUS@\upstream\silk\sort.c:80:             a[ j + 1 ]   = value;   /* Write value */
	addi.n	a11, a11, 1	# tmp112, _152,
	slli	a11, a11, 2	# _44, tmp112,
# @OPUS@\upstream\silk\sort.c:80:             a[ j + 1 ]   = value;   /* Write value */
	add.n	a6, a2, a11	# tmp113, a, _44
	s32i.n	a10, a6, 0	# *_45, value
# @OPUS@\upstream\silk\sort.c:81:             idx[ j + 1 ] = i;       /* Write index */
	add.n	a11, a3, a11	# tmp114, idx, _44
	s32i.n	a5, a11, 0	# *_46, K
.L14:
# @OPUS@\upstream\silk\sort.c:73:     for( i = K; i < L; i++ ) {
	addi.n	a5, a5, 1	# K, K,
# @OPUS@\upstream\silk\sort.c:73:     for( i = K; i < L; i++ ) {
	bne	a4, a5, .L17	# L, K,
.L1:
# @OPUS@\upstream\silk\sort.c:84: }
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_insertion_sort_increasing, .-silk_insertion_sort_increasing
	.section	.text.silk_insertion_sort_decreasing_int16,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_insertion_sort_decreasing_int16
	.type	silk_insertion_sort_decreasing_int16, @function
# Function: silk_insertion_sort_decreasing_int16
# Module: upstream/silk/sort.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #ifdef FIXED_POINT
# C context: /* This function is only used by the fixed-point build */
# C context: void silk_insertion_sort_decreasing_int16(
# C context: opus_int16                  *a,                 /* I/O   Unsorted / Sorted vector                                   */
# C context: opus_int                    *idx,               /* O     Index vector for the sorted elements                       */
# C context: const opus_int              L,                  /* I     Vector length                                              */
# C context: const opus_int              K                   /* I     Number of correctly sorted positions                       */
silk_insertion_sort_decreasing_int16:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
	mov.n	a7, a3	# ivtmp$132, idx
# @OPUS@\upstream\silk\sort.c:104:     for( i = 0; i < K; i++ ) {
	movi.n	a6, 0	# i,
# @OPUS@\upstream\silk\sort.c:104:     for( i = 0; i < K; i++ ) {
	bgei	a5, 1, .L39	# K,,
	j	.L47		#
.L64:
	mov.n	a13, a3	# ivtmp$128, idx
# @OPUS@\upstream\silk\sort.c:109:     for( i = 1; i < K; i++ ) {
	mov.n	a12, a2	# ivtmp$127, a
# @OPUS@\upstream\silk\sort.c:109:     for( i = 1; i < K; i++ ) {
	movi.n	a11, 1	# i,
# @OPUS@\upstream\silk\sort.c:109:     for( i = 1; i < K; i++ ) {
	bgei	a5, 2, .L46	# K,,
	j	.L47		#
.L39:
# @OPUS@\upstream\silk\sort.c:105:         idx[ i ] = i;
	s32i.n	a6, a7, 0	# MEM[base: _99, offset: 0B], i
# @OPUS@\upstream\silk\sort.c:104:     for( i = 0; i < K; i++ ) {
	addi.n	a6, a6, 1	# i, i,
	addi.n	a7, a7, 4	# ivtmp$132, ivtmp$132,
# @OPUS@\upstream\silk\sort.c:104:     for( i = 0; i < K; i++ ) {
	bne	a5, a6, .L39	# K, i,
	j	.L64		#
.L47:
# @OPUS@\upstream\silk\sort.c:121:     for( i = K; i < L; i++ ) {
	blt	a5, a4, .L41	# K, L,
	j	.L35		#
.L46:
# @OPUS@\upstream\silk\sort.c:110:         value = a[ i ];
	l16si	a10, a12, 2	# MEM[base: _116, offset: 2B], _7
	mov.n	a7, a13	# ivtmp$116, ivtmp$128
	mov.n	a6, a12	# ivtmp$114, ivtmp$127
	j	.L43		#
.L45:
# @OPUS@\upstream\silk\sort.c:113:             idx[ j + 1 ] = idx[ j ];   /* Shift index */
	l32i.n	a9, a7, 0	# MEM[base: _126, offset: 0B], MEM[base: _126, offset: 0B]
# @OPUS@\upstream\silk\sort.c:112:             a[ j + 1 ]   = a[ j ];     /* Shift value */
	s16i	a8, a6, 2	# MEM[base: _128, offset: 2B], _19
# @OPUS@\upstream\silk\sort.c:113:             idx[ j + 1 ] = idx[ j ];   /* Shift index */
	s32i.n	a9, a7, 4	# MEM[base: _126, offset: 4B], MEM[base: _126, offset: 0B]
	addi	a8, a6, -2	# ivtmp$114, ivtmp$114,
	addi	a7, a7, -4	# ivtmp$116, ivtmp$116,
# @OPUS@\upstream\silk\sort.c:111:         for( j = i - 1; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	beq	a2, a6, .L52	# a, ivtmp$114,
	mov.n	a6, a8	# ivtmp$114, ivtmp$114
.L43:
# @OPUS@\upstream\silk\sort.c:111:         for( j = i - 1; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	l16si	a8, a6, 0	# MEM[base: _128, offset: 0B], _19
	addi.n	a14, a6, 2	# _131, ivtmp$114,
	addi.n	a9, a7, 4	# _129, ivtmp$116,
# @OPUS@\upstream\silk\sort.c:111:         for( j = i - 1; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	blt	a8, a10, .L45	# _19, _7,
	j	.L44		#
.L52:
	mov.n	a9, a3	# _129, idx
	mov.n	a14, a2	# _131, a
.L44:
# @OPUS@\upstream\silk\sort.c:115:         a[ j + 1 ]   = value;   /* Write value */
	s16i	a10, a14, 0	# *prephitmp_183, _7
# @OPUS@\upstream\silk\sort.c:116:         idx[ j + 1 ] = i;       /* Write index */
	s32i.n	a11, a9, 0	# *prephitmp_185, i
# @OPUS@\upstream\silk\sort.c:109:     for( i = 1; i < K; i++ ) {
	addi.n	a11, a11, 1	# i, i,
	addi.n	a12, a12, 2	# ivtmp$127, ivtmp$127,
	addi.n	a13, a13, 4	# ivtmp$128, ivtmp$128,
# @OPUS@\upstream\silk\sort.c:109:     for( i = 1; i < K; i++ ) {
	bne	a5, a11, .L46	# K, i,
	j	.L47		#
.L41:
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	addi	a14, a5, -2	# j, K,
	addi	a6, a5, -3	# tmp112, K,
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	slli	a15, a14, 1	# _90, j,
# @OPUS@\upstream\silk\sort.c:123:         if( value > a[ K - 1 ] ) {
	slli	a13, a5, 1	# tmp107, K,
	slli	a7, a14, 2	# tmp111, j,
	slli	a6, a6, 1	# tmp113, tmp112,
	addi.n	a12, a15, 4	# tmp110, _90,
	addi	a13, a13, -2	# tmp109, tmp107,
	add.n	a7, a3, a7	#, idx, tmp111
	add.n	a6, a2, a6	#, a, tmp113
	add.n	a13, a2, a13	# _33, a, tmp109
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	add.n	a15, a2, a15	# _97, a, _90
	add.n	a12, a2, a12	# ivtmp$107, a, tmp110
	s32i.n	a7, sp, 0	# %sfp,
	s32i.n	a6, sp, 4	# %sfp,
.L51:
# @OPUS@\upstream\silk\sort.c:122:         value = a[ i ];
	l16si	a10, a12, 0	# MEM[base: _147, offset: 0B], _29
# @OPUS@\upstream\silk\sort.c:123:         if( value > a[ K - 1 ] ) {
	l16si	a6, a13, 0	# *_33, tmp116
	bge	a6, a10, .L48	# tmp116, _29,
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	bltz	a14, .L54	# j,
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	l16si	a9, a15, 0	# *_97, _48
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	bge	a9, a10, .L54	# _48, _29,
	l32i.n	a8, sp, 4	# %sfp, ivtmp$100
	l32i.n	a7, sp, 0	# %sfp, ivtmp$96
	mov.n	a6, a14	# j, j
.L50:
# @OPUS@\upstream\silk\sort.c:126:                 idx[ j + 1 ] = idx[ j ];   /* Shift index */
	l32i.n	a11, a7, 0	# MEM[base: _170, offset: 0B], MEM[base: _170, offset: 0B]
# @OPUS@\upstream\silk\sort.c:125:                 a[ j + 1 ]   = a[ j ];     /* Shift value */
	s16i	a9, a8, 4	# MEM[base: _171, offset: 4B], _48
# @OPUS@\upstream\silk\sort.c:126:                 idx[ j + 1 ] = idx[ j ];   /* Shift index */
	s32i.n	a11, a7, 4	# MEM[base: _170, offset: 4B], MEM[base: _170, offset: 0B]
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	addi.n	a6, a6, -1	# j, j,
	mov.n	a11, a6	# _172, j
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	beqi	a6, -1, .L49	# j,,
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	l16si	a9, a8, 0	# MEM[base: _171, offset: 0B], _48
	addi	a7, a7, -4	# ivtmp$96, ivtmp$96,
	addi	a8, a8, -2	# ivtmp$100, ivtmp$100,
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	blt	a9, a10, .L50	# _48, _29,
	j	.L49		#
.L54:
# @OPUS@\upstream\silk\sort.c:124:             for( j = K - 2; ( j >= 0 ) && ( value > a[ j ] ); j-- ) {
	mov.n	a11, a14	# _172, j
.L49:
# @OPUS@\upstream\silk\sort.c:128:             a[ j + 1 ]   = value;   /* Write value */
	addi.n	a11, a11, 1	# _50, _172,
# @OPUS@\upstream\silk\sort.c:128:             a[ j + 1 ]   = value;   /* Write value */
	slli	a6, a11, 1	# tmp124, _50,
	add.n	a6, a2, a6	# tmp125, a, tmp124
# @OPUS@\upstream\silk\sort.c:129:             idx[ j + 1 ] = i;       /* Write index */
	slli	a11, a11, 2	# tmp126, _50,
# @OPUS@\upstream\silk\sort.c:128:             a[ j + 1 ]   = value;   /* Write value */
	s16i	a10, a6, 0	# *_52, _29
# @OPUS@\upstream\silk\sort.c:129:             idx[ j + 1 ] = i;       /* Write index */
	add.n	a11, a3, a11	# tmp127, idx, tmp126
	s32i.n	a5, a11, 0	# *_54, K
.L48:
# @OPUS@\upstream\silk\sort.c:121:     for( i = K; i < L; i++ ) {
	addi.n	a5, a5, 1	# K, K,
	addi.n	a12, a12, 2	# ivtmp$107, ivtmp$107,
# @OPUS@\upstream\silk\sort.c:121:     for( i = K; i < L; i++ ) {
	bne	a4, a5, .L51	# L, K,
.L35:
# @OPUS@\upstream\silk\sort.c:132: }
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	silk_insertion_sort_decreasing_int16, .-silk_insertion_sort_decreasing_int16
	.section	.text.silk_insertion_sort_increasing_all_values_int16,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_insertion_sort_increasing_all_values_int16
	.type	silk_insertion_sort_increasing_all_values_int16, @function
# Function: silk_insertion_sort_increasing_all_values_int16
# Module: upstream/silk/sort.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif
# C context:
# C context: void silk_insertion_sort_increasing_all_values_int16(
# C context: opus_int16                 *a,                 /* I/O   Unsorted / Sorted vector                                   */
# C context: const opus_int             L                   /* I     Vector length                                              */
# C context: )
# C context: {
silk_insertion_sort_increasing_all_values_int16:
# @OPUS@\upstream\silk\sort.c:147:     for( i = 1; i < L; i++ ) {
	blti	a3, 2, .L68	# L,,
	addi	a6, a2, -2	# _55, a,
	slli	a3, a3, 1	# tmp62, L,
	addi	a2, a2, -4	# tmp61, a,
	mov.n	a7, a6	# ivtmp$149, _55
	add.n	a8, a2, a3	# _29, tmp61, tmp62
.L72:
# @OPUS@\upstream\silk\sort.c:148:         value = a[ i ];
	l16si	a4, a7, 4	# MEM[base: _20, offset: 4B], _4
# @OPUS@\upstream\silk\sort.c:149:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	l16si	a3, a7, 2	# MEM[base: _20, offset: 2B], _12
	addi.n	a5, a7, 4	# _65, ivtmp$149,
# @OPUS@\upstream\silk\sort.c:149:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	bge	a4, a3, .L70	# _4, _12,
	mov.n	a2, a7	# ivtmp$141, ivtmp$149
.L71:
# @OPUS@\upstream\silk\sort.c:150:             a[ j + 1 ] = a[ j ]; /* Shift value */
	s16i	a3, a2, 4	# MEM[base: _64, offset: 4B], _12
	addi.n	a5, a2, 2	# _65, ivtmp$141,
# @OPUS@\upstream\silk\sort.c:149:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	beq	a6, a2, .L70	# _55, ivtmp$141,
	addi	a2, a2, -2	# ivtmp$141, ivtmp$141,
# @OPUS@\upstream\silk\sort.c:149:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	l16si	a3, a2, 2	# MEM[base: _54, offset: 2B], _12
# @OPUS@\upstream\silk\sort.c:149:         for( j = i - 1; ( j >= 0 ) && ( value < a[ j ] ); j-- ) {
	blt	a4, a3, .L71	# _4, _12,
.L70:
# @OPUS@\upstream\silk\sort.c:152:         a[ j + 1 ] = value; /* Write value */
	s16i	a4, a5, 0	# *prephitmp_85, _4
	addi.n	a7, a7, 2	# ivtmp$149, ivtmp$149,
# @OPUS@\upstream\silk\sort.c:147:     for( i = 1; i < L; i++ ) {
	bne	a8, a7, .L72	# _29, ivtmp$149,
.L68:
# @OPUS@\upstream\silk\sort.c:154: }
	ret.n
	.size	silk_insertion_sort_increasing_all_values_int16, .-silk_insertion_sort_increasing_all_values_int16
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
