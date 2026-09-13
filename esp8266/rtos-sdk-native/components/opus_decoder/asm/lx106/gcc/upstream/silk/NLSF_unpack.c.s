# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/NLSF_unpack.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"NLSF_unpack.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_unpack.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_unpack.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_unpack.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\NLSF_unpack.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\NLSF_unpack.c.s.raw
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
	.section	.text.silk_NLSF_unpack,"ax",@progbits
	.literal_position
	.align	4
	.global	silk_NLSF_unpack
	.type	silk_NLSF_unpack, @function
# Function: silk_NLSF_unpack
# Module: upstream/silk/NLSF_unpack.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Unpack predictor values and indices for entropy coding tables */
# C context: void silk_NLSF_unpack(
# C context: opus_int16            ec_ix[],                        /* O    Indices to entropy tables [ LPC_ORDER ]     */
# C context: opus_uint8            pred_Q8[],                      /* O    LSF predictor [ LPC_ORDER ]                 */
# C context: const silk_NLSF_CB_struct   *psNLSF_CB,                     /* I    Codebook object                             */
# C context: const opus_int              CB1_index                       /* I    Index of vector in first LSF codebook       */
silk_NLSF_unpack:
# @OPUS@\upstream\silk\NLSF_unpack.c:46:     ec_sel_ptr = &psNLSF_CB->ec_sel[ CB1_index * psNLSF_CB->order / 2 ];
	l16si	a7, a4, 2	# psNLSF_CB_49(D)->order, _3
# @OPUS@\upstream\silk\NLSF_unpack.c:46:     ec_sel_ptr = &psNLSF_CB->ec_sel[ CB1_index * psNLSF_CB->order / 2 ];
	l32i.n	a8, a4, 24	# psNLSF_CB_49(D)->ec_sel, psNLSF_CB_49(D)->ec_sel
# @OPUS@\upstream\silk\NLSF_unpack.c:46:     ec_sel_ptr = &psNLSF_CB->ec_sel[ CB1_index * psNLSF_CB->order / 2 ];
	mull	a5, a7, a5	# tmp96, _3, CB1_index
# @OPUS@\upstream\silk\NLSF_unpack.c:46:     ec_sel_ptr = &psNLSF_CB->ec_sel[ CB1_index * psNLSF_CB->order / 2 ];
	extui	a6, a5, 31, 1	# tmp98, tmp96,
	add.n	a5, a6, a5	# tmp99, tmp98, tmp96
	srai	a5, a5, 1	# tmp100, tmp99,
# @OPUS@\upstream\silk\NLSF_unpack.c:46:     ec_sel_ptr = &psNLSF_CB->ec_sel[ CB1_index * psNLSF_CB->order / 2 ];
	add.n	a8, a8, a5	# ec_sel_ptr, psNLSF_CB_49(D)->ec_sel, tmp100
# @OPUS@\upstream\silk\NLSF_unpack.c:47:     for( i = 0; i < psNLSF_CB->order; i += 2 ) {
	blti	a7, 1, .L1	# _3,,
# @OPUS@\upstream\silk\NLSF_unpack.c:47:     for( i = 0; i < psNLSF_CB->order; i += 2 ) {
	movi.n	a7, 0	# i,
.L3:
# @OPUS@\upstream\silk\NLSF_unpack.c:48:         entry = *ec_sel_ptr++;
	l8ui	a5, a8, 0	# MEM[base: _87, offset: 0B], entry
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	l32i.n	a6, a4, 20	# psNLSF_CB_49(D)->pred_Q8, psNLSF_CB_49(D)->pred_Q8
# @OPUS@\upstream\silk\NLSF_unpack.c:49:         ec_ix  [ i     ] = silk_SMULBB( silk_RSHIFT( entry, 1 ) & 7, 2 * NLSF_QUANT_MAX_AMPLITUDE + 1 );
	extui	a9, a5, 1, 3	# tmp106, entry,,
	slli	a10, a9, 3	# tmp108, tmp106,
	add.n	a9, a9, a10	# tmp110, tmp106, tmp108
	s16i	a9, a2, 0	# MEM[base: _86, offset: 0B], tmp110
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	l16si	a9, a4, 2	# psNLSF_CB_49(D)->order, tmp111
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	extui	a10, a5, 0, 1	# tmp116, entry,
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	addi.n	a9, a9, -1	# tmp114, tmp111,
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	mull	a9, a9, a10	# tmp117, tmp114, tmp116
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	add.n	a6, a6, a7	# tmp119, psNLSF_CB_49(D)->pred_Q8, i
	add.n	a6, a6, a9	# tmp120, tmp119, tmp117
	l8ui	a10, a6, 0	# *_21, _23
# @OPUS@\upstream\silk\NLSF_unpack.c:51:         ec_ix  [ i + 1 ] = silk_SMULBB( silk_RSHIFT( entry, 5 ) & 7, 2 * NLSF_QUANT_MAX_AMPLITUDE + 1 );
	srli	a6, a5, 5	# tmp123, entry,
	slli	a9, a6, 3	# tmp125, tmp123,
# @OPUS@\upstream\silk\NLSF_unpack.c:50:         pred_Q8[ i     ] = psNLSF_CB->pred_Q8[ i + ( entry & 1 ) * ( psNLSF_CB->order - 1 ) ];
	s8i	a10, a3, 0	# MEM[base: _85, offset: 0B], _23
# @OPUS@\upstream\silk\NLSF_unpack.c:51:         ec_ix  [ i + 1 ] = silk_SMULBB( silk_RSHIFT( entry, 5 ) & 7, 2 * NLSF_QUANT_MAX_AMPLITUDE + 1 );
	add.n	a6, a6, a9	# tmp127, tmp123, tmp125
	s16i	a6, a2, 2	# MEM[base: _86, offset: 2B], tmp127
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	l16si	a9, a4, 2	# psNLSF_CB_49(D)->order, tmp132
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	l32i.n	a6, a4, 20	# psNLSF_CB_49(D)->pred_Q8, psNLSF_CB_49(D)->pred_Q8
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	extui	a5, a5, 4, 1	# tmp131, entry,,
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	addi.n	a9, a9, -1	# tmp135, tmp132,
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	mull	a5, a5, a9	# tmp136, tmp131, tmp135
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	add.n	a6, a6, a7	# tmp138, psNLSF_CB_49(D)->pred_Q8, i
	add.n	a5, a6, a5	# tmp139, tmp138, tmp136
	l8ui	a5, a5, 1	# *_40, _42
# @OPUS@\upstream\silk\NLSF_unpack.c:47:     for( i = 0; i < psNLSF_CB->order; i += 2 ) {
	addi.n	a7, a7, 2	# i, i,
# @OPUS@\upstream\silk\NLSF_unpack.c:52:         pred_Q8[ i + 1 ] = psNLSF_CB->pred_Q8[ i + ( silk_RSHIFT( entry, 4 ) & 1 ) * ( psNLSF_CB->order - 1 ) + 1 ];
	s8i	a5, a3, 1	# MEM[base: _85, offset: 1B], _42
# @OPUS@\upstream\silk\NLSF_unpack.c:47:     for( i = 0; i < psNLSF_CB->order; i += 2 ) {
	l16si	a5, a4, 2	# psNLSF_CB_49(D)->order, tmp141
	addi.n	a8, a8, 1	# ivtmp$9, ivtmp$9,
	addi.n	a2, a2, 4	# ivtmp$10, ivtmp$10,
	addi.n	a3, a3, 2	# ivtmp$11, ivtmp$11,
# @OPUS@\upstream\silk\NLSF_unpack.c:47:     for( i = 0; i < psNLSF_CB->order; i += 2 ) {
	blt	a7, a5, .L3	# i, tmp141,
.L1:
# @OPUS@\upstream\silk\NLSF_unpack.c:54: }
	ret.n
	.size	silk_NLSF_unpack, .-silk_NLSF_unpack
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
