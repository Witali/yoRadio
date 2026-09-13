# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_stabilize.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_stabilize.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_stabilize.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_stabilize.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_stabilize.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_stabilize.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_stabilize.c.s.raw
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
	.section	.text.silk_NLSF_stabilize,"ax",@progbits
	.literal_position
	.literal .LC0, 32768
	.literal .LC1, 32767
	.literal .LC2, -32768
	.align	4
	.global	silk_NLSF_stabilize
	.type	silk_NLSF_stabilize, @function
# Function: silk_NLSF_stabilize
# Module: upstream/silk/NLSF_stabilize.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define MAX_LOOPS        20
# C context:
# C context: /* NLSF stabilizer, for a single input data vector */
# C context: void silk_NLSF_stabilize(
# C context: opus_int16            *NLSF_Q15,          /* I/O   Unstable/stabilized normalized LSF vector in Q15 [L]       */
# C context: const opus_int16            *NDeltaMin_Q15,     /* I     Min distance vector, NDeltaMin_Q15[L] must be >= 1 [L+1]   */
# C context: const opus_int              L                   /* I     Number of NLSF parameters in the input vector              */
# C context: )
silk_NLSF_stabilize:
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	slli	a5, a4, 1	# tmp183, L,
	addi	a5, a5, -2	#, tmp183,
# @OPUS@\upstream\silk\NLSF_stabilize.c:52: {
	addi	sp, sp, -64	#,,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	addi.n	a6, a5, 2	#,,
	s32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	add.n	a6, a2, a5	#, NLSF_Q15,
	s32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	l32i.n	a6, sp, 12	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:52: {
	s32i.n	a12, sp, 56	#,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	add.n	a6, a3, a6	#, NDeltaMin_Q15,
# @OPUS@\upstream\silk\NLSF_stabilize.c:52: {
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	s32i.n	a5, sp, 8	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:52: {
	mov.n	a13, a2	# NLSF_Q15, NLSF_Q15
	mov.n	a12, a3	# NDeltaMin_Q15, NDeltaMin_Q15
# @OPUS@\upstream\silk\NLSF_stabilize.c:68:         for( i = 1; i <= L-1; i++ ) {
	addi.n	a10, a4, -1	# _225, L,
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	s32i.n	a6, sp, 4	# %sfp,
	movi.n	a14, 0x14	# ivtmp_494,
.L21:
# @OPUS@\upstream\silk\NLSF_stabilize.c:65:         min_diff_Q15 = NLSF_Q15[0] - NDeltaMin_Q15[0];
	l16si	a2, a13, 0	# *NLSF_Q15_162(D), D__lsm0$64
# @OPUS@\upstream\silk\NLSF_stabilize.c:65:         min_diff_Q15 = NLSF_Q15[0] - NDeltaMin_Q15[0];
	l16si	a15, a12, 0	# *NDeltaMin_Q15_163(D), _3
# @OPUS@\upstream\silk\NLSF_stabilize.c:65:         min_diff_Q15 = NLSF_Q15[0] - NDeltaMin_Q15[0];
	sub	a9, a2, a15	# min_diff_Q15, D__lsm0$64, _3
# @OPUS@\upstream\silk\NLSF_stabilize.c:68:         for( i = 1; i <= L-1; i++ ) {
	blti	a10, 1, .L34	# _225,,
	addi.n	a6, a13, 2	# ivtmp$97, NLSF_Q15,
	addi.n	a5, a12, 2	# ivtmp$99, NDeltaMin_Q15,
# @OPUS@\upstream\silk\NLSF_stabilize.c:66:         I = 0;
	movi.n	a11, 0	# I,
# @OPUS@\upstream\silk\NLSF_stabilize.c:68:         for( i = 1; i <= L-1; i++ ) {
	movi.n	a3, 1	# i,
.L4:
# @OPUS@\upstream\silk\NLSF_stabilize.c:69:             diff_Q15 = NLSF_Q15[i] - ( NLSF_Q15[i-1] + NDeltaMin_Q15[i] );
	l16si	a7, a6, 0	# MEM[base: _389, offset: 0B], _421
# @OPUS@\upstream\silk\NLSF_stabilize.c:69:             diff_Q15 = NLSF_Q15[i] - ( NLSF_Q15[i-1] + NDeltaMin_Q15[i] );
	l16si	a8, a5, 0	# MEM[base: _388, offset: 0B], tmp192
# @OPUS@\upstream\silk\NLSF_stabilize.c:69:             diff_Q15 = NLSF_Q15[i] - ( NLSF_Q15[i-1] + NDeltaMin_Q15[i] );
	sub	a2, a7, a2	# tmp191, _421, D__lsm0$64
	sub	a2, a2, a8	# diff_Q15, tmp191, tmp192
# @OPUS@\upstream\silk\NLSF_stabilize.c:70:             if( diff_Q15 < min_diff_Q15 ) {
	bge	a2, a9, .L3	# diff_Q15, min_diff_Q15,
	mov.n	a11, a3	# I, i
	mov.n	a9, a2	# min_diff_Q15, diff_Q15
.L3:
# @OPUS@\upstream\silk\NLSF_stabilize.c:68:         for( i = 1; i <= L-1; i++ ) {
	addi.n	a3, a3, 1	# i, i,
	addi.n	a6, a6, 2	# ivtmp$97, ivtmp$97,
	addi.n	a5, a5, 2	# ivtmp$99, ivtmp$99,
	mov.n	a2, a7	# D__lsm0$64, _421
# @OPUS@\upstream\silk\NLSF_stabilize.c:68:         for( i = 1; i <= L-1; i++ ) {
	bge	a10, a3, .L4	# _225, i,
	j	.L2		#
.L34:
# @OPUS@\upstream\silk\NLSF_stabilize.c:66:         I = 0;
	movi.n	a11, 0	# I,
.L2:
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	l32i.n	a6, sp, 4	# %sfp,
	l16si	a3, a6, 0	# *_27, _28
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	l32i.n	a6, sp, 0	# %sfp,
	l16si	a5, a6, 0	# *_23, tmp199
# @OPUS@\upstream\silk\NLSF_stabilize.c:76:         diff_Q15 = ( 1 << 15 ) - ( NLSF_Q15[L-1] + NDeltaMin_Q15[L] );
	l32r	a6, .LC0	#,
	sub	a2, a6, a3	# tmp197,, _28
	sub	a2, a2, a5	# diff_Q15, tmp197, tmp199
# @OPUS@\upstream\silk\NLSF_stabilize.c:77:         if( diff_Q15 < min_diff_Q15 ) {
	bge	a2, a9, .L5	# diff_Q15, min_diff_Q15,
	mov.n	a9, a2	# min_diff_Q15, diff_Q15
	mov.n	a11, a4	# I, L
.L5:
# @OPUS@\upstream\silk\NLSF_stabilize.c:85:         if( min_diff_Q15 >= 0 ) {
	bgez	a9, .L1	# min_diff_Q15,
# @OPUS@\upstream\silk\NLSF_stabilize.c:89:         if( I == 0 ) {
	bnez.n	a11, .L7	# I,
# @OPUS@\upstream\silk\NLSF_stabilize.c:91:             NLSF_Q15[0] = NDeltaMin_Q15[0];
	s16i	a15, a13, 0	# *NLSF_Q15_162(D), _3
	j	.L8		#
.L7:
# @OPUS@\upstream\silk\NLSF_stabilize.c:93:         } else if( I == L) {
	beq	a11, a4, .L9	# I, L,
# @OPUS@\upstream\silk\NLSF_stabilize.c:99:             min_center_Q15 = 0;
	movi.n	a3, 0	# min_center_Q15,
	slli	a15, a11, 1	# _38, I,
# @OPUS@\upstream\silk\NLSF_stabilize.c:100:             for( k = 0; k < I; k++ ) {
	blti	a11, 1, .L11	# I,,
	j	.L10		#
.L9:
# @OPUS@\upstream\silk\NLSF_stabilize.c:95:             NLSF_Q15[L-1] = ( 1 << 15 ) - NDeltaMin_Q15[L];
	l32r	a2, .LC2	#,
# @OPUS@\upstream\silk\NLSF_stabilize.c:95:             NLSF_Q15[L-1] = ( 1 << 15 ) - NDeltaMin_Q15[L];
	l32i.n	a6, sp, 0	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:95:             NLSF_Q15[L-1] = ( 1 << 15 ) - NDeltaMin_Q15[L];
	sub	a3, a2, a3	# tmp202,, _28
# @OPUS@\upstream\silk\NLSF_stabilize.c:95:             NLSF_Q15[L-1] = ( 1 << 15 ) - NDeltaMin_Q15[L];
	s16i	a3, a6, 0	# *_23, tmp202
	j	.L8		#
.L10:
	slli	a15, a11, 1	# _38, I,
	mov.n	a2, a12	# ivtmp$93, NDeltaMin_Q15
	add.n	a6, a12, a15	# _398, NDeltaMin_Q15, _38
# @OPUS@\upstream\silk\NLSF_stabilize.c:99:             min_center_Q15 = 0;
	movi.n	a3, 0	# min_center_Q15,
.L12:
# @OPUS@\upstream\silk\NLSF_stabilize.c:101:                 min_center_Q15 += NDeltaMin_Q15[k];
	l16si	a5, a2, 0	# MEM[base: _402, offset: 0B], tmp205
	addi.n	a2, a2, 2	# ivtmp$93, ivtmp$93,
# @OPUS@\upstream\silk\NLSF_stabilize.c:101:                 min_center_Q15 += NDeltaMin_Q15[k];
	add.n	a3, a3, a5	# min_center_Q15, min_center_Q15, tmp205
# @OPUS@\upstream\silk\NLSF_stabilize.c:100:             for( k = 0; k < I; k++ ) {
	bne	a6, a2, .L12	# _398, ivtmp$93,
.L11:
# @OPUS@\upstream\silk\NLSF_stabilize.c:103:             min_center_Q15 += silk_RSHIFT( NDeltaMin_Q15[I], 1 );
	add.n	a6, a12, a15	# _39, NDeltaMin_Q15, _38
	l16ui	a7, a6, 0	# *_39,
	slli	a7, a7, 16	# tmp210, *_39,
	srai	a7, a7, 17	# _41, tmp210,
# @OPUS@\upstream\silk\NLSF_stabilize.c:103:             min_center_Q15 += silk_RSHIFT( NDeltaMin_Q15[I], 1 );
	add.n	a3, a7, a3	# min_center_Q15, _41, min_center_Q15
# @OPUS@\upstream\silk\NLSF_stabilize.c:107:             for( k = L; k > I; k-- ) {
	bge	a11, a4, .L35	# I, L,
	l32i.n	a5, sp, 4	# %sfp, ivtmp$90
# @OPUS@\upstream\silk\NLSF_stabilize.c:106:             max_center_Q15 = 1 << 15;
	l32r	a2, .LC0	#, max_center_Q15
.L14:
# @OPUS@\upstream\silk\NLSF_stabilize.c:108:                 max_center_Q15 -= NDeltaMin_Q15[k];
	l16si	a8, a5, 0	# MEM[base: _214, offset: 0B], tmp213
	addi	a5, a5, -2	# ivtmp$90, ivtmp$90,
# @OPUS@\upstream\silk\NLSF_stabilize.c:108:                 max_center_Q15 -= NDeltaMin_Q15[k];
	sub	a2, a2, a8	# max_center_Q15, max_center_Q15, tmp213
# @OPUS@\upstream\silk\NLSF_stabilize.c:107:             for( k = L; k > I; k-- ) {
	bne	a6, a5, .L14	# _39, ivtmp$90,
	j	.L13		#
.L35:
# @OPUS@\upstream\silk\NLSF_stabilize.c:106:             max_center_Q15 = 1 << 15;
	l32r	a2, .LC0	#, max_center_Q15
.L13:
	addi	a8, a15, -2	# tmp216, _38,
	add.n	a8, a13, a8	# _502, NLSF_Q15, tmp216
	add.n	a15, a13, a15	# _499, NLSF_Q15, _38
	l16si	a9, a15, 0	# *_499, pretmp_505
	l16si	a5, a8, 0	# *_502, pretmp_503
# @OPUS@\upstream\silk\NLSF_stabilize.c:110:             max_center_Q15 -= silk_RSHIFT( NDeltaMin_Q15[I], 1 );
	sub	a2, a2, a7	# max_center_Q15, max_center_Q15, _41
	add.n	a5, a5, a9	# tmp221, pretmp_503, pretmp_505
	srai	a11, a5, 1	# _508, tmp221,
	extui	a5, a5, 0, 1	# tmp299, tmp221,
	add.n	a9, a5, a11	# _513, tmp299, _508
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	bge	a2, a3, .L15	# max_center_Q15, min_center_Q15,
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	bge	a3, a9, .L16	# min_center_Q15, _513,
	j	.L46		#
.L16:
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	bge	a9, a2, .L20	# _513, max_center_Q15,
	j	.L45		#
.L15:
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	bge	a2, a9, .L19	# max_center_Q15, _513,
	j	.L45		#
.L19:
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	bge	a9, a3, .L20	# _513, min_center_Q15,
.L46:
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	slli	a2, a3, 16	# tmp235, min_center_Q15,
	srai	a2, a2, 16	# iftmp$11_153, tmp235,
	j	.L17		#
.L20:
# @OPUS@\upstream\silk\NLSF_stabilize.c:113:             center_freq_Q15 = (opus_int16)silk_LIMIT_32( silk_RSHIFT_ROUND( (opus_int32)NLSF_Q15[I-1] + (opus_int32)NLSF_Q15[I], 1 ),
	add.n	a2, a5, a11	# tmp239, tmp299, _508
.L45:
	slli	a2, a2, 16	# tmp240, tmp239,
	srai	a2, a2, 16	# iftmp$11_153, tmp240,
.L17:
# @OPUS@\upstream\silk\NLSF_stabilize.c:115:             NLSF_Q15[I-1] = center_freq_Q15 - silk_RSHIFT( NDeltaMin_Q15[I], 1 );
	sub	a2, a2, a7	# tmp241, iftmp$11_153, _41
	slli	a2, a2, 16	# tmp242, tmp241,
	srai	a2, a2, 16	# _83, tmp242,
# @OPUS@\upstream\silk\NLSF_stabilize.c:115:             NLSF_Q15[I-1] = center_freq_Q15 - silk_RSHIFT( NDeltaMin_Q15[I], 1 );
	s16i	a2, a8, 0	# *_502, _83
# @OPUS@\upstream\silk\NLSF_stabilize.c:116:             NLSF_Q15[I] = NLSF_Q15[I-1] + NDeltaMin_Q15[I];
	l16ui	a3, a6, 0	# *_39,
	add.n	a2, a2, a3	# tmp244, _83, *_39
# @OPUS@\upstream\silk\NLSF_stabilize.c:116:             NLSF_Q15[I] = NLSF_Q15[I-1] + NDeltaMin_Q15[I];
	s16i	a2, a15, 0	# *_499, tmp244
.L8:
	addi.n	a14, a14, -1	# ivtmp_494, ivtmp_494,
# @OPUS@\upstream\silk\NLSF_stabilize.c:60:     for( loops = 0; loops < MAX_LOOPS; loops++ ) {
	bnez.n	a14, .L21	# ivtmp_494,
# @OPUS@\upstream\silk\NLSF_stabilize.c:126:         silk_insertion_sort_increasing_all_values_int16( &NLSF_Q15[0], L );
	mov.n	a3, a4	#, L
	mov.n	a2, a13	#, NLSF_Q15
	s32i.n	a4, sp, 16	#,
	call0	silk_insertion_sort_increasing_all_values_int16		#
# @OPUS@\upstream\silk\NLSF_stabilize.c:129:         NLSF_Q15[0] = silk_max_int( NLSF_Q15[0], NDeltaMin_Q15[0] );
	l16si	a3, a12, 0	# *NDeltaMin_Q15_163(D), tmp249
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	l16si	a2, a13, 0	# *NLSF_Q15_162(D), tmp245
	l32i.n	a4, sp, 16	#,
	bge	a2, a3, .L22	# tmp245, tmp249,
	mov.n	a2, a3	# tmp245, tmp249
.L22:
# @OPUS@\upstream\silk\NLSF_stabilize.c:129:         NLSF_Q15[0] = silk_max_int( NLSF_Q15[0], NDeltaMin_Q15[0] );
	s16i	a2, a13, 0	# *NLSF_Q15_162(D), D__lsm0$63
	addi	a5, a4, -2	# i, L,
# @OPUS@\upstream\silk\NLSF_stabilize.c:132:         for( i = 1; i < L; i++ )
	blti	a4, 2, .L23	# L,,
	l32i.n	a4, sp, 12	# %sfp,
	l32r	a8, .LC1	#, tmp298
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	l32r	a10, .LC2	#, tmp355
	addi.n	a3, a13, 2	# ivtmp$80, NLSF_Q15,
	addi.n	a6, a12, 2	# ivtmp$82, NDeltaMin_Q15,
	add.n	a9, a13, a4	# _11, NLSF_Q15,
.L26:
	l16si	a4, a6, 0	# MEM[base: _7, offset: 0B], _452
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	l16si	a7, a3, 0	# MEM[base: _5, offset: 0B], _468
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	add.n	a4, a4, a2	# _450, _452, D__lsm0$63
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	mov.n	a2, a8	# iftmp$46_447, tmp298
	blt	a8, a4, .L24	# tmp298, _450,
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	slli	a11, a4, 16	# tmp260, _450,
	mov.n	a2, a10	# iftmp$46_447, tmp355
	blt	a4, a10, .L24	# _450, tmp355,
	srai	a2, a11, 16	# iftmp$46_447, tmp260,
.L24:
# @OPUS@\upstream\silk\SigProc_FIX.h:566:     return (((a) > (b)) ? (a) : (b));
	bge	a2, a7, .L25	# iftmp$46_447, _468,
	mov.n	a2, a7	# iftmp$46_447, _468
.L25:
# @OPUS@\upstream\silk\NLSF_stabilize.c:133:             NLSF_Q15[i] = silk_max_int( NLSF_Q15[i], silk_ADD_SAT16( NLSF_Q15[i-1], NDeltaMin_Q15[i] ) );
	slli	a2, a2, 16	# tmp262, iftmp$46_447,
	srai	a2, a2, 16	# D__lsm0$63, tmp262,
	s16i	a2, a3, 0	# MEM[base: _5, offset: 0B], D__lsm0$63
	addi.n	a3, a3, 2	# ivtmp$80, ivtmp$80,
	addi.n	a6, a6, 2	# ivtmp$82, ivtmp$82,
# @OPUS@\upstream\silk\NLSF_stabilize.c:132:         for( i = 1; i < L; i++ )
	bne	a9, a3, .L26	# _11, ivtmp$80,
	j	.L44		#
.L23:
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a6, sp, 4	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l16si	a2, a6, 0	# *_27, tmp264
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	l32r	a6, .LC0	#,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l16si	a3, a4, 0	# *_23, tmp269
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	sub	a2, a6, a2	# tmp263,, tmp264
	bge	a3, a2, .L28	# tmp269, tmp263,
	mov.n	a2, a3	# tmp263, tmp269
.L28:
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a4, sp, 0	# %sfp,
	s16i	a2, a4, 0	# *_23, tmp263
# @OPUS@\upstream\silk\NLSF_stabilize.c:139:         for( i = L-2; i >= 0; i-- )
	bltz	a5, .L1	# i,
.L33:
	l32i.n	a6, sp, 0	# %sfp,
	l32i.n	a4, sp, 8	# %sfp,
	slli	a3, a5, 1	# tmp276, i,
	l16si	a2, a6, 0	# MEM[(opus_int16 *)_428 + 2B(OVF)], D__lsm0$62
	add.n	a13, a13, a3	# ivtmp$70, NLSF_Q15, tmp276
	add.n	a12, a12, a4	# ivtmp$72, NDeltaMin_Q15,
.L31:
# @OPUS@\upstream\silk\NLSF_stabilize.c:140:             NLSF_Q15[i] = silk_min_int( NLSF_Q15[i], NLSF_Q15[i+1] - NDeltaMin_Q15[i+1] );
	l16si	a4, a12, 0	# MEM[base: _429, offset: 0B], tmp278
# @OPUS@\upstream\silk\NLSF_stabilize.c:140:             NLSF_Q15[i] = silk_min_int( NLSF_Q15[i], NLSF_Q15[i+1] - NDeltaMin_Q15[i+1] );
	l16si	a3, a13, 0	# MEM[base: _440, offset: 0B], tmp282
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	sub	a2, a2, a4	# tmp277, D__lsm0$62, tmp278
# @OPUS@\upstream\silk\NLSF_stabilize.c:139:         for( i = L-2; i >= 0; i-- )
	addi.n	a5, a5, -1	# i, i,
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	bge	a3, a2, .L30	# tmp282, tmp277,
	mov.n	a2, a3	# tmp277, tmp282
.L30:
# @OPUS@\upstream\silk\NLSF_stabilize.c:140:             NLSF_Q15[i] = silk_min_int( NLSF_Q15[i], NLSF_Q15[i+1] - NDeltaMin_Q15[i+1] );
	slli	a2, a2, 16	# tmp285, tmp277,
	srai	a2, a2, 16	# D__lsm0$62, tmp285,
	s16i	a2, a13, 0	# MEM[base: _440, offset: 0B], D__lsm0$62
	addi	a12, a12, -2	# ivtmp$72, ivtmp$72,
	addi	a13, a13, -2	# ivtmp$70, ivtmp$70,
# @OPUS@\upstream\silk\NLSF_stabilize.c:139:         for( i = L-2; i >= 0; i-- )
	bnei	a5, -1, .L31	# i,,
	j	.L1		#
.L44:
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a6, sp, 4	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l16si	a2, a6, 0	# *_27, tmp287
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	l32r	a6, .LC0	#,
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l16si	a3, a4, 0	# *_23, tmp292
# @OPUS@\upstream\silk\SigProc_FIX.h:548:     return (((a) < (b)) ? (a) : (b));
	sub	a2, a6, a2	# tmp286,, tmp287
	bge	a3, a2, .L32	# tmp292, tmp286,
	mov.n	a2, a3	# tmp286, tmp292
.L32:
# @OPUS@\upstream\silk\NLSF_stabilize.c:136:         NLSF_Q15[L-1] = silk_min_int( NLSF_Q15[L-1], (1<<15) - NDeltaMin_Q15[L] );
	l32i.n	a4, sp, 0	# %sfp,
	s16i	a2, a4, 0	# *_23, tmp286
	j	.L33		#
.L1:
# @OPUS@\upstream\silk\NLSF_stabilize.c:142: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_NLSF_stabilize, .-silk_NLSF_stabilize
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
