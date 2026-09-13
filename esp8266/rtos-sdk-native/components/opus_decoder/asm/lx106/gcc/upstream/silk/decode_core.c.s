# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decode_core.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decode_core.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decode_core.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decode_core.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decode_core.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decode_core.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decode_core.c.s.raw
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
	.global	__muldi3
	.section	.text.silk_decode_core,"ax",@progbits
	.literal_position
	.literal .LC0, 65536
	.literal .LC1, -2147483648
	.literal .LC2, 2147483632
	.literal .LC3, -32768
	.literal .LC4, 32767
	.literal .LC5, 2147483647
	.literal .LC6, silk_Quantization_Offsets_Q10
	.literal .LC7, 196314165
	.literal .LC8, 907633515
	.literal .LC9, 536870911
	.literal .LC10, 536870912
	.literal .LC11, 4096
	.literal .LC13, 134217727
	.literal .LC14, -134217728
	.align	4
	.global	silk_decode_core
	.type	silk_decode_core, @function
# Function: silk_decode_core
# Module: upstream/silk/decode_core.c
# SILK short/long-term prediction and PCM synthesis.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /**********************************************************/
# C context: /* Core decoder. Performs inverse NSQ operation LTP + LPC */
# C context: /**********************************************************/
# C context: void silk_decode_core(
# C context: silk_decoder_state          *psDec,                         /* I/O  Decoder state                               */
# C context: silk_decoder_control        *psDecCtrl,                     /* I    Decoder control                             */
# C context: opus_int16                  xq[],                           /* O    Decoded speech                              */
# C context: const opus_int16            pulses[ MAX_FRAME_LENGTH ],     /* I    Pulse signal                                */
silk_decode_core:
	movi	a9, 0x150	#,
	sub	sp, sp, a9	#,,
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	addmi	a8, a2, 0x400	#, psDec,
# @OPUS@\upstream\silk\decode_core.c:45: {
	s32i	a0, sp, 332	#,
	s32i	a6, sp, 260	# %sfp, arch
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:45: {
	s32i	a12, sp, 328	#,
	s32i	a14, sp, 320	#,
	mov.n	a12, a5	# pulses, pulses
	s32i	a4, sp, 252	# %sfp, xq
	s32i	a13, sp, 324	#,
	s32i	a15, sp, 316	#,
# @OPUS@\upstream\silk\decode_core.c:45: {
	s32i	a2, sp, 136	# %sfp, psDec
	s32i	a3, sp, 160	# %sfp, psDecCtrl
# @OPUS@\upstream\silk\decode_core.c:54:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:54:     SAVE_STACK;
	s32i.n	a2, sp, 32	# _saved_stack,
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	l32i.n	a2, a9, 36	# psDec_483(D)->ltp_mem_length,
# @OPUS@\upstream\silk\decode_core.c:54:     SAVE_STACK;
	s32i.n	a3, sp, 36	# _saved_stack,
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\decode_core.c:62:     sLTP_Q15 = yoradio_opus_scratch_alloc(psDec->ltp_mem_length + psDec->frame_length, sizeof(opus_int32), 1);
	l32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:58:     ALLOC( sLTP, psDec->ltp_mem_length, opus_int16 );
	s32i	a2, sp, 248	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:62:     sLTP_Q15 = yoradio_opus_scratch_alloc(psDec->ltp_mem_length + psDec->frame_length, sizeof(opus_int32), 1);
	l32i.n	a5, a10, 36	# psDec_483(D)->ltp_mem_length, psDec_483(D)->ltp_mem_length
	l32i.n	a2, a10, 28	# psDec_483(D)->frame_length, psDec_483(D)->frame_length
# @OPUS@\upstream\silk\decode_core.c:62:     sLTP_Q15 = yoradio_opus_scratch_alloc(psDec->ltp_mem_length + psDec->frame_length, sizeof(opus_int32), 1);
	movi.n	a4, 1	#,
	add.n	a2, a5, a2	#, psDec_483(D)->ltp_mem_length, psDec_483(D)->frame_length
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\decode_core.c:63:     res_Q14 = yoradio_opus_scratch_alloc(psDec->subfr_length, sizeof(opus_int32), 1);
	l32i	a14, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:62:     sLTP_Q15 = yoradio_opus_scratch_alloc(psDec->ltp_mem_length + psDec->frame_length, sizeof(opus_int32), 1);
	s32i	a2, sp, 184	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:63:     res_Q14 = yoradio_opus_scratch_alloc(psDec->subfr_length, sizeof(opus_int32), 1);
	l32i.n	a2, a14, 32	# psDec_483(D)->subfr_length,
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
	s32i	a2, sp, 168	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:68:     ALLOC( sLPC_Q14, psDec->subfr_length + MAX_LPC_ORDER, opus_int32 );
	l32i.n	a2, a14, 32	# psDec_483(D)->subfr_length, psDec_483(D)->subfr_length
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	addmi	a8, a8, 0x500	#,,
# @OPUS@\upstream\silk\decode_core.c:68:     ALLOC( sLPC_Q14, psDec->subfr_length + MAX_LPC_ORDER, opus_int32 );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	addi	a2, a2, 16	#, psDec_483(D)->subfr_length,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	s32i	a8, sp, 156	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:68:     ALLOC( sLPC_Q14, psDec->subfr_length + MAX_LPC_ORDER, opus_int32 );
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	l32i	a9, sp, 156	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:68:     ALLOC( sLPC_Q14, psDec->subfr_length + MAX_LPC_ORDER, opus_int32 );
	s32i	a2, sp, 116	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	l8ui	a2, a9, 209	# psDec_483(D)->indices.signalType,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	l8ui	a4, a9, 210	# psDec_483(D)->indices.quantOffsetType,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	slli	a2, a2, 24	# tmp818, psDec_483(D)->indices.signalType,
	srai	a2, a2, 25	# tmp820, tmp818,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	slli	a4, a4, 24	# tmp825, psDec_483(D)->indices.quantOffsetType,
	srai	a4, a4, 24	# tmp823, tmp825,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	slli	a2, a2, 1	# tmp826, tmp820,
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	l8ui	a3, a9, 211	# psDec_483(D)->indices.NLSFInterpCoef_Q2,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	add.n	a2, a2, a4	# tmp827, tmp826, tmp823
	l32r	a4, .LC6	#, tmp814
	slli	a2, a2, 1	# tmp828, tmp827,
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	slli	a3, a3, 24	# tmp840, psDec_483(D)->indices.NLSFInterpCoef_Q2,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	add.n	a2, a4, a2	# tmp829, tmp814, tmp828
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	srai	a3, a3, 24	# tmp838, tmp840,
# @OPUS@\upstream\silk\decode_core.c:70:     offset_Q10 = silk_Quantization_Offsets_Q10[ psDec->indices.signalType >> 1 ][ psDec->indices.quantOffsetType ];
	l16si	a7, a2, 0	# silk_Quantization_Offsets_Q10, offset_Q10
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	movi.n	a2, 1	# tmp833,
	blti	a3, 4, .L2	# tmp838,,
	movi.n	a2, 0	# tmp833,
.L2:
# @OPUS@\upstream\silk\decode_core.c:79:     rand_seed = psDec->indices.Seed;
	l32i	a10, sp, 156	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i	a14, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:79:     rand_seed = psDec->indices.Seed;
	l8ui	a3, a10, 214	# psDec_483(D)->indices.Seed,
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	extui	a2, a2, 0, 8	#, tmp833
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i.n	a4, a14, 28	# psDec_483(D)->frame_length, psDec_483(D)->frame_length
# @OPUS@\upstream\silk\decode_core.c:79:     rand_seed = psDec->indices.Seed;
	slli	a3, a3, 24	# tmp843, psDec_483(D)->indices.Seed,
# @OPUS@\upstream\silk\decode_core.c:72:     if( psDec->indices.NLSFInterpCoef_Q2 < 1 << 2 ) {
	s32i	a2, sp, 256	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:79:     rand_seed = psDec->indices.Seed;
	srai	a3, a3, 24	# rand_seed, tmp843,
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	bgei	a4, 1, .L3	# psDec_483(D)->frame_length,,
.L10:
# @OPUS@\upstream\silk\decode_core.c:108:     silk_memcpy( sLPC_Q14, psDec->sLPC_Q14_buf, MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a8, sp, 136	# %sfp,
	l32i	a2, sp, 116	# %sfp,
	addi.n	a8, a8, 8	#,,
	movi.n	a4, 0x40	#,
	mov.n	a3, a8	#,
	s32i	a8, sp, 244	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i	a9, sp, 112	# %sfp,
	l32i.n	a2, a9, 24	# psDec_483(D)->nb_subfr, psDec_483(D)->nb_subfr
	bgei	a2, 1, .L4	# psDec_483(D)->nb_subfr,,
	j	.L5		#
.L3:
# @OPUS@\upstream\silk\decode_core.c:87:         excitation += offset_Q10 << 4;
	slli	a7, a7, 4	# _29, offset_Q10,
	mov.n	a5, a12	# ivtmp$122, pulses
	l32r	a10, .LC7	#, tmp1469
	l32r	a9, .LC8	#, tmp1470
	l32i	a12, sp, 136	# %sfp, psDec
	mov.n	a13, a14	# tmp1465,
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	movi.n	a6, 0	# i,
	addmi	a8, a7, 0x500	# tmp1543, _29,
	addmi	a11, a7, -0x500	# tmp1544, _29,
.L9:
# @OPUS@\upstream\silk\decode_core.c:84:         opus_int32 excitation = silk_LSHIFT((opus_int32)pulses[i], 14);
	l16si	a4, a5, 0	# MEM[base: _2808, offset: 0B], tmp855
# @OPUS@\upstream\silk\decode_core.c:81:         rand_seed = silk_RAND( rand_seed );
	mull	a3, a3, a10	# tmp852, rand_seed, tmp1469
# @OPUS@\upstream\silk\decode_core.c:84:         opus_int32 excitation = silk_LSHIFT((opus_int32)pulses[i], 14);
	slli	a4, a4, 14	# excitation, tmp855,
	mov.n	a2, a7	# excitation, _29
	add.n	a15, a8, a4	# tmp1550, tmp1543, excitation
# @OPUS@\upstream\silk\decode_core.c:81:         rand_seed = silk_RAND( rand_seed );
	add.n	a14, a3, a9	# _22, tmp852, tmp1470
# @OPUS@\upstream\silk\decode_core.c:85:         if (excitation > 0) excitation -= QUANT_LEVEL_ADJUST_Q10 << 4;
	blti	a4, 1, .L6	# excitation,,
	add.n	a2, a11, a4	# excitation, tmp1544, excitation
	j	.L7		#
.L6:
	movnez	a2, a15, a4	# excitation, tmp1550, excitation
.L7:
# @OPUS@\upstream\silk\decode_core.c:89:         yoradio_opus_store32(&psDec->exc_Q14[i], excitation);
	l32i.n	a4, a12, 0	# psDec_483(D)->exc_Q14, psDec_483(D)->exc_Q14
# @OPUS@\upstream\silk\decode_core.c:88:         if (rand_seed < 0) excitation = -excitation;
	neg	a15, a2	# tmp1481, excitation
# @OPUS@\upstream\silk\decode_core.c:89:         yoradio_opus_store32(&psDec->exc_Q14[i], excitation);
	slli	a3, a6, 2	# tmp860, i,
# @OPUS@\upstream\silk\decode_core.c:88:         if (rand_seed < 0) excitation = -excitation;
	movltz	a2, a15, a14	# excitation, tmp1481, _22
# @OPUS@\upstream\silk\decode_core.c:89:         yoradio_opus_store32(&psDec->exc_Q14[i], excitation);
	add.n	a4, a4, a3	# tmp861, psDec_483(D)->exc_Q14, tmp860
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:78:     __asm__ volatile ("s32i %1, %0, 0" : : "a" (p), "a" (value) : "memory");
#APP
# 78 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	s32i a2, a4, 0	# excitation, tmp861
# 0 "" 2
# @OPUS@\upstream\silk\decode_core.c:104:         rand_seed = silk_ADD32_ovflw( rand_seed, pulses[ i ] );
#NO_APP
	l16si	a3, a5, 0	# MEM[base: _2808, offset: 0B], tmp863
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	l32i.n	a2, a13, 28	# psDec_483(D)->frame_length, psDec_483(D)->frame_length
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	addi.n	a6, a6, 1	# i, i,
# @OPUS@\upstream\silk\decode_core.c:104:         rand_seed = silk_ADD32_ovflw( rand_seed, pulses[ i ] );
	add.n	a3, a3, a14	# rand_seed, tmp863, _22
	addi.n	a5, a5, 2	# ivtmp$122, ivtmp$122,
# @OPUS@\upstream\silk\decode_core.c:80:     for( i = 0; i < psDec->frame_length; i++ ) {
	blt	a6, a2, .L9	# i, psDec_483(D)->frame_length,
	j	.L10		#
.L5:
# @OPUS@\upstream\silk\decode_core.c:270:     silk_memcpy( psDec->sLPC_Q14_buf, sLPC_Q14, MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a3, sp, 116	# %sfp,
	l32i	a2, sp, 244	# %sfp,
	movi.n	a4, 0x40	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_core.c:271:     RESTORE_STACK;
	l32i.n	a2, sp, 32	# _saved_stack,
	l32i.n	a3, sp, 36	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\decode_core.c:272: }
	l32i	a0, sp, 332	#,
	movi	a9, 0x150	#,
	l32i	a12, sp, 328	#,
	l32i	a13, sp, 324	#,
	l32i	a14, sp, 320	#,
	l32i	a15, sp, 316	#,
	add.n	sp, sp, a9	#,,
	ret.n
.L4:
# @OPUS@\upstream\silk\decode_core.c:110:     pexc_Q14 = psDec->exc_Q14;
	l32i	a12, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	movi.n	a10, 0	#,
# @OPUS@\upstream\silk\decode_core.c:110:     pexc_Q14 = psDec->exc_Q14;
	l32i.n	a12, a12, 0	# psDec_483(D)->exc_Q14,
	l32i	a8, sp, 160	# %sfp,
	s32i	a12, sp, 144	# %sfp,
	l32i	a12, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:112:     sLTP_buf_idx = psDec->ltp_mem_length;
	l32i.n	a14, a9, 36	# psDec_483(D)->ltp_mem_length,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	s32i	a10, sp, 128	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:111:     pxq      = xq;
	l32i	a10, sp, 252	# %sfp,
	addi	a9, a8, 96	#,,
	addmi	a12, a12, 0xb00	#,,
# @OPUS@\upstream\silk\decode_core.c:112:     sLTP_buf_idx = psDec->ltp_mem_length;
	s32i	a14, sp, 180	# %sfp,
	s32i	a8, sp, 132	# %sfp,
	s32i	a9, sp, 152	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:111:     pxq      = xq;
	s32i	a10, sp, 148	# %sfp,
	s32i	a12, sp, 164	# %sfp,
.L51:
# @OPUS@\upstream\silk\decode_core.c:116:         A_Q12 = psDecCtrl->PredCoef_Q12[ k >> 1 ];
	l32i	a14, sp, 128	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:119:         silk_memcpy( A_Q12_tmp, A_Q12, psDec->LPC_order * sizeof( opus_int16 ) );
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:116:         A_Q12 = psDecCtrl->PredCoef_Q12[ k >> 1 ];
	srai	a2, a14, 1	# tmp873,,
# @OPUS@\upstream\silk\decode_core.c:116:         A_Q12 = psDecCtrl->PredCoef_Q12[ k >> 1 ];
	l32i	a9, sp, 160	# %sfp,
	addi.n	a2, a2, 1	# tmp874, tmp873,
# @OPUS@\upstream\silk\decode_core.c:119:         silk_memcpy( A_Q12_tmp, A_Q12, psDec->LPC_order * sizeof( opus_int16 ) );
	l32i.n	a4, a8, 40	# psDec_483(D)->LPC_order, psDec_483(D)->LPC_order
# @OPUS@\upstream\silk\decode_core.c:116:         A_Q12 = psDecCtrl->PredCoef_Q12[ k >> 1 ];
	slli	a2, a2, 5	# tmp875, tmp874,
	add.n	a2, a9, a2	#,, tmp875
	s32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:119:         silk_memcpy( A_Q12_tmp, A_Q12, psDec->LPC_order * sizeof( opus_int16 ) );
	mov.n	a3, a2	#,
	slli	a4, a4, 1	#, psDec_483(D)->LPC_order,
	mov.n	a2, sp	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_core.c:123:         Gain_Q10     = silk_RSHIFT( psDecCtrl->Gains_Q16[ k ], 6 );
	l32i	a10, sp, 132	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:121:         signalType   = psDec->indices.signalType;
	l32i	a12, sp, 156	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:123:         Gain_Q10     = silk_RSHIFT( psDecCtrl->Gains_Q16[ k ], 6 );
	l32i.n	a10, a10, 16	# MEM[base: _2818, offset: 16B],
# @OPUS@\upstream\silk\decode_core.c:121:         signalType   = psDec->indices.signalType;
	l8ui	a12, a12, 209	# psDec_483(D)->indices.signalType,
# @OPUS@\upstream\silk\decode_core.c:123:         Gain_Q10     = silk_RSHIFT( psDecCtrl->Gains_Q16[ k ], 6 );
	srai	a14, a10, 6	#,,
# @OPUS@\upstream\silk\decode_core.c:123:         Gain_Q10     = silk_RSHIFT( psDecCtrl->Gains_Q16[ k ], 6 );
	s32i	a10, sp, 68	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:121:         signalType   = psDec->indices.signalType;
	s32i	a12, sp, 76	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:123:         Gain_Q10     = silk_RSHIFT( psDecCtrl->Gains_Q16[ k ], 6 );
	s32i	a14, sp, 64	# %sfp,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a10, .L59	#,
# @OPUS@\upstream\silk\Inlines.h:155:     b_headrm = silk_CLZ32( silk_abs(b32) ) - 1;
	abs	a15, a10	# tmp884,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a15, a15	# iftmp$76_587, tmp884
	movi.n	a4, 0xf	# tmp885,
	addi.n	a14, a15, -1	# _2110, iftmp$76_587,
	sub	a4, a4, a15	# _2112, tmp885, iftmp$76_587
	mov.n	a8, a10	#,
	j	.L11		#
.L59:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a4, -0x11	# _2112,
	movi.n	a14, 0x1f	# _2110,
	movi.n	a15, 0x20	# iftmp$76_587,
	mov.n	a8, a10	#,
.L11:
# @OPUS@\upstream\silk\Inlines.h:156:     b32_nrm = silk_LSHIFT(b32, b_headrm);                                       /* Q: b_headrm                */
	ssl	a14	# _2110
	sll	a14, a8	# b32_nrm,
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	srai	a12, a14, 16	# _593, b32_nrm,
# @OPUS@\upstream\silk\Inlines.h:159:     b32_inv = silk_DIV32_16( silk_int32_MAX >> 2, silk_RSHIFT(b32_nrm, 16) );   /* Q: 29 + 16 - b_headrm    */
	l32r	a2, .LC9	#,
	mov.n	a3, a12	#, _593
	s32i	a4, sp, 272	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a5, a2, 16	# tmp889, tmp888,
	srai	a13, a5, 16	# _599, tmp889,
	extui	a3, a14, 0, 16	# tmp893, b32_nrm,
	mull	a12, a12, a13	# tmp890, _593, _599
	mull	a3, a3, a13	# tmp894, tmp893, _599
	l32r	a9, .LC10	#,
	srai	a3, a3, 16	# tmp895, tmp894,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	srai	a2, a2, 15	# tmp897, tmp888,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	sub	a12, a9, a12	# tmp891,, tmp890
	sub	a12, a12, a3	# tmp896, tmp891, tmp895
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	addi.n	a3, a2, 1	# tmp898, tmp897,
	srai	a3, a3, 1	# tmp899, tmp898,
# @OPUS@\upstream\silk\Inlines.h:165:     err_Q32 = silk_LSHIFT( ((opus_int32)1<<29) - silk_SMULWB(b32_nrm, b32_inv), 3 );        /* Q32                        */
	slli	a2, a12, 3	# err_Q32, tmp896,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	mull	a3, a3, a2	# tmp900, tmp899, err_Q32
	srai	a6, a2, 16	# tmp903, err_Q32,
	extui	a2, a2, 0, 16	# tmp905, err_Q32,
	mull	a6, a6, a13	# tmp904, tmp903, _599
	mull	a2, a2, a13	# tmp906, tmp905, _599
	add.n	a3, a3, a5	# tmp902, tmp900, tmp889
	add.n	a6, a3, a6	# _845, tmp902, tmp904
	srai	a2, a2, 16	# tmp907, tmp906,
# @OPUS@\upstream\silk\Inlines.h:176:             return silk_RSHIFT(result, lshift);
	l32i	a4, sp, 272	#,
# @OPUS@\upstream\silk\Inlines.h:168:     result = silk_SMLAWW(result, err_Q32, b32_inv);                             /* Q: 61 - b_headrm            */
	add.n	a2, a2, a6	# result, tmp907, _845
# @OPUS@\upstream\silk\Inlines.h:176:             return silk_RSHIFT(result, lshift);
	ssr	a4	# _2112
	sra	a10, a2	#, result
	s32i.n	a10, sp, 56	# %sfp,
# @OPUS@\upstream\silk\Inlines.h:172:     if( lshift <= 0 ) {
	bgei	a4, 1, .L19	# _2112,,
# @OPUS@\upstream\silk\Inlines.h:173:         return silk_LSHIFT_SAT32(result, -lshift);
	l32r	a5, .LC5	#, tmp1468
	l32r	a3, .LC1	#, tmp908
	addi	a4, a15, -15	# _623, iftmp$76_587,
	ssr	a4	# _623
	sra	a3, a3	# _624, tmp908
	ssr	a4	# _623
	sra	a5, a5	# _625, tmp1468
	bge	a5, a3, .L13	# _625, _624,
	bge	a3, a2, .L14	# _624, result,
	j	.L89		#
.L14:
	bge	a2, a5, .L15	# iftmp$74_626, _625,
	j	.L90		#
.L13:
	bge	a5, a2, .L17	# _625, result,
.L90:
	mov.n	a2, a5	# iftmp$74_626, _625
	j	.L15		#
.L17:
	bge	a2, a3, .L15	# iftmp$74_626, _624,
.L89:
	mov.n	a2, a3	# iftmp$74_626, _624
.L15:
	ssl	a4	# _623
	sll	a2, a2	#, iftmp$74_626
	s32i.n	a2, sp, 56	# %sfp,
.L19:
# @OPUS@\upstream\silk\decode_core.c:127:         if( psDecCtrl->Gains_Q16[ k ] != psDec->prev_gain_Q16 ) {
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:127:         if( psDecCtrl->Gains_Q16[ k ] != psDec->prev_gain_Q16 ) {
	l32i	a9, sp, 68	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:127:         if( psDecCtrl->Gains_Q16[ k ] != psDec->prev_gain_Q16 ) {
	l32i.n	a12, a8, 4	# psDec_483(D)->prev_gain_Q16, _45
# @OPUS@\upstream\silk\decode_core.c:127:         if( psDecCtrl->Gains_Q16[ k ] != psDec->prev_gain_Q16 ) {
	beq	a9, a12, .L60	#, _45,
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	beqz.n	a12, .L61	# _45,
# @OPUS@\upstream\silk\Inlines.h:110:     a_headrm = silk_CLZ32( silk_abs(a32) ) - 1;
	abs	a7, a12	# tmp910, _45
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	nsau	a7, a7	# iftmp$76_639, tmp910
	addi.n	a2, a7, -1	# _2472, iftmp$76_639,
	j	.L21		#
.L61:
# @OPUS@\upstream\silk\macros.h:122:     return in32 ? 32 - EC_ILOG(in32) : 32;
	movi.n	a2, 0x1f	# _2472,
	movi.n	a7, 0x20	# iftmp$76_639,
.L21:
# @OPUS@\upstream\silk\Inlines.h:111:     a32_nrm = silk_LSHIFT(a32, a_headrm);                                       /* Q: a_headrm                  */
	ssl	a2	# _2472
	sll	a12, a12	# _643, _45
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	extui	a6, a12, 0, 16	# tmp911, _643,
	mull	a6, a6, a13	# tmp912, tmp911, _599
	srai	a2, a12, 16	# tmp914, _643,
	mull	a2, a2, a13	# tmp915, tmp914, _599
	srai	a6, a6, 16	# tmp913, tmp912,
# @OPUS@\upstream\silk\Inlines.h:119:     result = silk_SMULWB(a32_nrm, b32_inv);                                     /* Q: 29 + a_headrm - b_headrm  */
	add.n	a6, a6, a2	# result, tmp913, tmp915
# @OPUS@\upstream\silk\Inlines.h:123:     a32_nrm = silk_SUB32_ovflw(a32_nrm, silk_LSHIFT_ovflw( silk_SMMUL(b32_nrm, result), 3 ));  /* Q: a_headrm   */
	mov.n	a4, a6	#, result
	srai	a5, a6, 31	#, result,
	mov.n	a2, a14	#, b32_nrm
	srai	a3, a14, 31	#, b32_nrm,
	s32i	a6, sp, 276	#,
	s32i	a7, sp, 272	#,
	call0	__muldi3		#
	slli	a3, a3, 3	# tmp922,,
	sub	a12, a12, a3	# a32_nrm, _643, tmp922
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a3, a12, 16	# tmp923, a32_nrm,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	l32i	a7, sp, 272	#,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	extui	a12, a12, 0, 16	# tmp925, a32_nrm,
	mull	a3, a3, a13	# tmp924, tmp923, _599
	l32i	a6, sp, 276	#,
	mull	a13, a12, a13	# tmp926, tmp925, _599
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	sub	a2, a7, a15	# tmp929, iftmp$76_639, iftmp$76_587
	add.n	a6, a3, a6	# _862, tmp924, result
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	srai	a13, a13, 16	# tmp927, tmp926,
# @OPUS@\upstream\silk\Inlines.h:129:     lshift = 29 + a_headrm - b_headrm - Qres;
	addi.n	a2, a2, 13	# lshift, tmp929,
# @OPUS@\upstream\silk\Inlines.h:126:     result = silk_SMLAWB(result, a32_nrm, b32_inv);                             /* Q: 29 + a_headrm - b_headrm  */
	add.n	a13, a13, a6	# result, tmp927, _862
# @OPUS@\upstream\silk\Inlines.h:130:     if( lshift < 0 ) {
	bgez	a2, .L22	# lshift,
# @OPUS@\upstream\silk\Inlines.h:131:         return silk_LSHIFT_SAT32(result, -lshift);
	addi	a15, a15, -13	# tmp930, iftmp$76_587,
	l32r	a5, .LC5	#, tmp1468
	l32r	a2, .LC1	#, tmp931
	sub	a7, a15, a7	# _683, tmp930, iftmp$76_639
	ssr	a7	# _683
	sra	a2, a2	# _684, tmp931
	ssr	a7	# _683
	sra	a5, a5	# _685, tmp1468
	bge	a5, a2, .L23	# _685, _684,
	bge	a2, a13, .L24	# _684, result,
	j	.L91		#
.L24:
	bge	a13, a5, .L25	# iftmp$82_686, _685,
	j	.L92		#
.L23:
	bge	a5, a13, .L27	# _685, result,
.L92:
	mov.n	a13, a5	# iftmp$82_686, _685
	j	.L25		#
.L27:
	bge	a13, a2, .L25	# iftmp$82_686, _684,
.L91:
	mov.n	a13, a2	# iftmp$82_686, _684
.L25:
	ssl	a7	# _683
	sll	a14, a13	# gain_adj_Q16, iftmp$82_686
	srai	a11, a14, 16	# prephitmp_2130, gain_adj_Q16,
	extui	a13, a14, 0, 16	# prephitmp_2131, gain_adj_Q16,
	j	.L29		#
.L22:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a3, 0x1f	# tmp933,
	blt	a3, a2, .L62	# tmp933, lshift,
# @OPUS@\upstream\silk\Inlines.h:134:             return silk_RSHIFT(result, lshift);
	ssr	a2	# lshift
	sra	a14, a13	# gain_adj_Q16, result
	srai	a11, a14, 16	# prephitmp_2130, gain_adj_Q16,
	extui	a13, a14, 0, 16	# prephitmp_2131, gain_adj_Q16,
	j	.L29		#
.L62:
# @OPUS@\upstream\silk\Inlines.h:133:         if( lshift < 32){
	movi.n	a13, 0	# prephitmp_2131,
	mov.n	a11, a13	# prephitmp_2130, prephitmp_2131
# @OPUS@\upstream\silk\Inlines.h:137:             return 0;
	mov.n	a14, a13	# gain_adj_Q16, prephitmp_2130
.L29:
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	l32i	a12, sp, 116	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	l32i.n	a10, a12, 0	# *sLPC_Q14_491, _700
	l32i.n	a3, a12, 4	# MEM[(opus_int32 *)sLPC_Q14_491 + 4B], _721
	l32i.n	a2, a12, 8	# MEM[(opus_int32 *)sLPC_Q14_491 + 8B], _742
	l32i.n	a6, a12, 12	# MEM[(opus_int32 *)sLPC_Q14_491 + 12B], _763
	l32i.n	a5, a12, 16	# MEM[(opus_int32 *)sLPC_Q14_491 + 16B], _784
	l32i.n	a4, a12, 20	# MEM[(opus_int32 *)sLPC_Q14_491 + 20B], _805
	l32i.n	a9, a8, 28	# MEM[(opus_int32 *)sLPC_Q14_491 + 28B], _847
	l32i.n	a15, a8, 32	# MEM[(opus_int32 *)sLPC_Q14_491 + 32B], _868
	l32i.n	a7, a8, 36	# MEM[(opus_int32 *)sLPC_Q14_491 + 36B], _889
	l32i.n	a12, a12, 24	# MEM[(opus_int32 *)sLPC_Q14_491 + 24B], _826
	l32i.n	a8, a8, 40	# MEM[(opus_int32 *)sLPC_Q14_491 + 40B],
	srai	a12, a12, 15	#, _826,
	s32i	a8, sp, 268	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	s32i	a12, sp, 92	# %sfp,
	srai	a12, a15, 15	#, _868,
	l16si	a8, a8, 0	# *sLPC_Q14_491,
	s32i	a12, sp, 88	# %sfp,
	l32i	a12, sp, 116	# %sfp,
	s32i.n	a8, sp, 48	# %sfp,
	l16si	a12, a12, 4	# MEM[(opus_int32 *)sLPC_Q14_491 + 4B],
	l32i	a8, sp, 116	# %sfp,
	s32i.n	a12, sp, 52	# %sfp,
	l16si	a8, a8, 8	# MEM[(opus_int32 *)sLPC_Q14_491 + 8B],
	l32i	a12, sp, 116	# %sfp,
	s32i.n	a8, sp, 60	# %sfp,
	l16si	a12, a12, 12	# MEM[(opus_int32 *)sLPC_Q14_491 + 12B],
	l32i	a8, sp, 116	# %sfp,
	s32i	a12, sp, 80	# %sfp,
	l16si	a8, a8, 16	# MEM[(opus_int32 *)sLPC_Q14_491 + 16B],
	l32i	a12, sp, 116	# %sfp,
	s32i	a8, sp, 84	# %sfp,
	l16si	a15, a12, 20	# MEM[(opus_int32 *)sLPC_Q14_491 + 20B], _807
	l16si	a8, a12, 24	# MEM[(opus_int32 *)sLPC_Q14_491 + 24B],
	srai	a7, a7, 15	# tmp1025, _889,
	s32i	a8, sp, 96	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	addi.n	a7, a7, 1	# tmp1026, tmp1025,
	l16si	a8, a8, 32	# MEM[(opus_int32 *)sLPC_Q14_491 + 32B],
	srai	a7, a7, 1	#, tmp1026,
	s32i	a8, sp, 100	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	s32i	a7, sp, 228	# %sfp,
	l16si	a8, a8, 36	# MEM[(opus_int32 *)sLPC_Q14_491 + 36B],
	srai	a3, a3, 15	# tmp945, _721,
	s32i	a8, sp, 104	# %sfp,
	l32i	a8, sp, 92	# %sfp,
	addi.n	a3, a3, 1	# tmp946, tmp945,
	addi.n	a8, a8, 1	#,,
	s32i	a8, sp, 92	# %sfp,
	l32i	a8, sp, 88	# %sfp,
	srai	a3, a3, 1	# tmp947, tmp946,
	addi.n	a8, a8, 1	#,,
	s32i	a8, sp, 120	# %sfp,
	l32i	a8, sp, 268	# %sfp,
	mull	a3, a3, a14	#, tmp947, gain_adj_Q16
	srai	a8, a8, 15	#,,
	s32i	a8, sp, 108	# %sfp,
	l32i	a8, sp, 116	# %sfp,
	l32i	a7, sp, 108	# %sfp,
	l16si	a8, a8, 40	# MEM[(opus_int32 *)sLPC_Q14_491 + 40B],
	addi.n	a7, a7, 1	#,,
	s32i	a8, sp, 88	# %sfp,
	l32i	a8, sp, 92	# %sfp,
	s32i	a7, sp, 176	# %sfp,
	srai	a8, a8, 1	#,,
	s32i	a8, sp, 172	# %sfp,
	l32i	a8, sp, 120	# %sfp,
	l32i.n	a7, sp, 48	# %sfp,
	srai	a8, a8, 1	#,,
	s32i	a8, sp, 224	# %sfp,
	mull	a8, a7, a11	# tmp939,, prephitmp_2130
	mull	a7, a7, a13	#,, prephitmp_2131
	s32i	a3, sp, 108	# %sfp,
	srai	a2, a2, 15	# tmp955, _742,
	l32i.n	a3, sp, 52	# %sfp,
	s32i.n	a7, sp, 48	# %sfp,
	addi.n	a2, a2, 1	# tmp956, tmp955,
	l32i.n	a7, sp, 52	# %sfp,
	mull	a3, a3, a11	#,, prephitmp_2130
	srai	a5, a5, 15	# tmp975, _784,
	srai	a2, a2, 1	# tmp957, tmp956,
	mull	a7, a7, a13	#,, prephitmp_2131
	mull	a2, a2, a14	#, tmp957, gain_adj_Q16
	addi.n	a5, a5, 1	# tmp976, tmp975,
	s32i	a3, sp, 120	# %sfp,
	srai	a5, a5, 1	# tmp977, tmp976,
	l16si	a12, a12, 28	# MEM[(opus_int32 *)sLPC_Q14_491 + 28B], _849
	mull	a5, a5, a14	#, tmp977, gain_adj_Q16
	s32i.n	a7, sp, 52	# %sfp,
	s32i	a2, sp, 124	# %sfp,
	l32i.n	a3, sp, 60	# %sfp,
	l32i.n	a2, sp, 60	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	mull	a2, a2, a11	#,, prephitmp_2130
	mull	a3, a3, a13	#,, prephitmp_2131
	s32i	a5, sp, 280	# %sfp,
	l32i	a5, sp, 84	# %sfp,
	s32i	a2, sp, 140	# %sfp,
	s32i	a3, sp, 188	# %sfp,
	mull	a2, a7, a11	# tmp969,, prephitmp_2130
	mull	a3, a7, a13	#,, prephitmp_2131
	mull	a5, a5, a11	#,, prephitmp_2130
	l32i	a7, sp, 84	# %sfp,
	s32i	a5, sp, 196	# %sfp,
	mull	a7, a7, a13	#,, prephitmp_2131
	l32i	a5, sp, 172	# %sfp,
	s32i	a3, sp, 80	# %sfp,
	s32i	a7, sp, 84	# %sfp,
	mull	a3, a15, a11	#, _807, prephitmp_2130
	mull	a5, a5, a14	#,, gain_adj_Q16
	l32i	a7, sp, 96	# %sfp,
	s32i	a3, sp, 204	# %sfp,
	s32i	a5, sp, 172	# %sfp,
	mull	a7, a7, a11	#,, prephitmp_2130
	mull	a5, a12, a11	#, _849, prephitmp_2130
	l32i	a3, sp, 96	# %sfp,
	s32i	a7, sp, 284	# %sfp,
	mull	a3, a3, a13	#,, prephitmp_2131
	l32i	a7, sp, 224	# %sfp,
	s32i	a5, sp, 216	# %sfp,
	l32i	a5, sp, 100	# %sfp,
	s32i	a3, sp, 208	# %sfp,
	mull	a7, a7, a14	#,, gain_adj_Q16
	l32i	a3, sp, 100	# %sfp,
	mull	a5, a5, a13	#,, prephitmp_2131
	s32i	a7, sp, 224	# %sfp,
	mull	a3, a3, a11	#,, prephitmp_2130
	l32i	a7, sp, 228	# %sfp,
	s32i	a5, sp, 292	# %sfp,
	l32i	a5, sp, 104	# %sfp,
	s32i	a3, sp, 288	# %sfp,
	mull	a5, a5, a11	#,, prephitmp_2130
	mull	a3, a7, a14	# tmp1028,, gain_adj_Q16
	l32i	a7, sp, 104	# %sfp,
	s32i	a5, sp, 228	# %sfp,
	mull	a7, a7, a13	#,, prephitmp_2131
	l32i	a5, sp, 176	# %sfp,
	s32i	a7, sp, 232	# %sfp,
	srai	a7, a5, 1	# tmp1037,,
	mull	a7, a7, a14	#, tmp1037, gain_adj_Q16
	srai	a10, a10, 15	# tmp935, _700,
	s32i	a7, sp, 176	# %sfp,
	addi.n	a10, a10, 1	# tmp936, tmp935,
	l32i	a7, sp, 88	# %sfp,
	l32i	a5, sp, 88	# %sfp,
	srai	a6, a6, 15	# tmp965, _763,
	srai	a10, a10, 1	# tmp937, tmp936,
	mull	a10, a10, a14	# tmp938, tmp937, gain_adj_Q16
	mull	a7, a7, a11	#,, prephitmp_2130
	mull	a5, a5, a13	#,, prephitmp_2131
	addi.n	a6, a6, 1	# tmp966, tmp965,
	srai	a6, a6, 1	# tmp967, tmp966,
	add.n	a8, a10, a8	#, tmp938, tmp939
	mull	a6, a6, a14	# tmp968, tmp967, gain_adj_Q16
	s32i	a7, sp, 236	# %sfp,
	s32i	a5, sp, 240	# %sfp,
	l32i.n	a7, sp, 48	# %sfp,
	l32i.n	a5, sp, 52	# %sfp,
	l32i	a10, sp, 120	# %sfp,
	s32i	a8, sp, 92	# %sfp,
	l32i	a8, sp, 108	# %sfp,
	add.n	a2, a6, a2	#, tmp968, tmp969
	srai	a7, a7, 16	#,,
	l32i	a6, sp, 80	# %sfp,
	srai	a5, a5, 16	#,,
	srai	a4, a4, 15	# tmp985, _805,
	add.n	a8, a8, a10	#,,
	s32i.n	a7, sp, 48	# %sfp,
	l32i	a10, sp, 140	# %sfp,
	l32i	a7, sp, 124	# %sfp,
	s32i.n	a5, sp, 52	# %sfp,
	addi.n	a4, a4, 1	# tmp986, tmp985,
	l32i	a5, sp, 188	# %sfp,
	srai	a6, a6, 16	#,,
	srai	a4, a4, 1	# tmp987, tmp986,
	s32i	a8, sp, 108	# %sfp,
	s32i	a2, sp, 124	# %sfp,
	add.n	a8, a7, a10	# tmp960,,
	l32i	a2, sp, 196	# %sfp,
	srai	a7, a5, 16	# tmp962,,
	s32i	a6, sp, 80	# %sfp,
	l32i	a5, sp, 84	# %sfp,
	l32i	a10, sp, 280	# %sfp,
	l32i	a6, sp, 204	# %sfp,
	srai	a9, a9, 15	# tmp1005, _847,
	mull	a4, a4, a14	# tmp988, tmp987, gain_adj_Q16
	addi.n	a9, a9, 1	# tmp1006, tmp1005,
	add.n	a10, a10, a2	#,,
	add.n	a4, a4, a6	#, tmp988,
	srai	a5, a5, 16	#,,
	srai	a9, a9, 1	# tmp1007, tmp1006,
	l32i	a2, sp, 284	# %sfp,
	s32i	a10, sp, 140	# %sfp,
	s32i	a5, sp, 84	# %sfp,
	l32i	a10, sp, 172	# %sfp,
	l32i	a5, sp, 216	# %sfp,
	s32i	a4, sp, 96	# %sfp,
	mull	a9, a9, a14	# tmp1008, tmp1007, gain_adj_Q16
	l32i	a4, sp, 208	# %sfp,
	add.n	a10, a10, a2	#,,
	add.n	a9, a9, a5	#, tmp1008,
	srai	a4, a4, 16	#,,
	mull	a12, a12, a13	# tmp1011, _849, prephitmp_2131
	s32i	a10, sp, 172	# %sfp,
	s32i	a4, sp, 100	# %sfp,
	s32i	a9, sp, 104	# %sfp,
	l32i	a6, sp, 224	# %sfp,
	l32i	a9, sp, 288	# %sfp,
	l32i	a2, sp, 228	# %sfp,
	srai	a5, a12, 16	# tmp1012, tmp1011,
	add.n	a12, a6, a9	# tmp1020,,
	l32i	a6, sp, 232	# %sfp,
	l32i	a10, sp, 292	# %sfp,
	l32i	a9, sp, 92	# %sfp,
	add.n	a3, a3, a2	# tmp1030, tmp1028,
	l32i.n	a2, sp, 48	# %sfp,
	srai	a6, a6, 16	#,,
	s32i	a6, sp, 88	# %sfp,
	srai	a4, a10, 16	# tmp1022,,
	l32i	a6, sp, 108	# %sfp,
	add.n	a10, a9, a2	# tmp943,,
	l32i.n	a9, sp, 52	# %sfp,
	add.n	a7, a8, a7	#, tmp960, tmp962
	add.n	a6, a6, a9	#,,
	s32i	a6, sp, 300	# %sfp,
	s32i	a7, sp, 296	# %sfp,
	l32i	a6, sp, 124	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i	a8, sp, 140	# %sfp,
	l32i	a9, sp, 84	# %sfp,
	mull	a15, a15, a13	# tmp991, _807, prephitmp_2131
	add.n	a2, a6, a7	# tmp973,,
	add.n	a7, a8, a9	# tmp983,,
	l32i	a6, sp, 96	# %sfp,
	l32i	a8, sp, 172	# %sfp,
	l32i	a9, sp, 100	# %sfp,
	srai	a15, a15, 16	# tmp992, tmp991,
	add.n	a15, a6, a15	# tmp993,, tmp992
	add.n	a6, a8, a9	# tmp1003,,
	l32i	a8, sp, 104	# %sfp,
	add.n	a4, a12, a4	# tmp1023, tmp1020, tmp1022
	add.n	a5, a8, a5	# tmp1013,, tmp1012
	l32i	a9, sp, 88	# %sfp,
	l32i	a8, sp, 236	# %sfp,
	l32i	a12, sp, 176	# %sfp,
	add.n	a3, a3, a9	# tmp1033, tmp1030,
	add.n	a12, a12, a8	#,,
	l32i	a9, sp, 240	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	l32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	s32i.n	a12, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	s32i.n	a10, a8, 0	# *sLPC_Q14_491, tmp943
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	srai	a12, a9, 16	# tmp1042,,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	l32i	a10, sp, 296	# %sfp,
	l32i	a9, sp, 300	# %sfp,
	s32i.n	a10, a8, 8	# MEM[(opus_int32 *)sLPC_Q14_491 + 8B],
	s32i.n	a9, a8, 4	# MEM[(opus_int32 *)sLPC_Q14_491 + 4B],
	s32i.n	a2, a8, 12	# MEM[(opus_int32 *)sLPC_Q14_491 + 12B], tmp973
	s32i.n	a7, a8, 16	# MEM[(opus_int32 *)sLPC_Q14_491 + 16B], tmp983
	s32i.n	a3, a8, 36	# MEM[(opus_int32 *)sLPC_Q14_491 + 36B], tmp1033
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	l32i.n	a3, sp, 48	# %sfp,
	l16si	a10, a8, 44	# MEM[(opus_int32 *)sLPC_Q14_491 + 44B], _933
	add.n	a2, a3, a12	# tmp1043,, tmp1042
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	s32i.n	a15, a8, 20	# MEM[(opus_int32 *)sLPC_Q14_491 + 20B], tmp993
	s32i.n	a5, a8, 28	# MEM[(opus_int32 *)sLPC_Q14_491 + 28B], tmp1013
	s32i.n	a4, a8, 32	# MEM[(opus_int32 *)sLPC_Q14_491 + 32B], tmp1023
	s32i.n	a2, a8, 40	# MEM[(opus_int32 *)sLPC_Q14_491 + 40B], tmp1043
	s32i.n	a6, a8, 24	# MEM[(opus_int32 *)sLPC_Q14_491 + 24B], tmp1003
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	mov.n	a12, a8	#,
	l16si	a9, a8, 48	# MEM[(opus_int32 *)sLPC_Q14_491 + 48B], _954
	l16si	a7, a12, 56	# MEM[(opus_int32 *)sLPC_Q14_491 + 56B], _996
	l16si	a6, a12, 60	# MEM[(opus_int32 *)sLPC_Q14_491 + 60B], _1017
	mull	a12, a10, a11	#, _933, prephitmp_2130
	l32i.n	a15, a8, 44	# MEM[(opus_int32 *)sLPC_Q14_491 + 44B], _931
	l32i.n	a5, a8, 56	# MEM[(opus_int32 *)sLPC_Q14_491 + 56B], _994
	s32i.n	a12, sp, 48	# %sfp,
	mull	a12, a10, a13	# tmp1051, _933, prephitmp_2131
	mull	a10, a9, a11	#, _954, prephitmp_2130
	l32i.n	a3, a8, 48	# MEM[(opus_int32 *)sLPC_Q14_491 + 48B], _952
	l32i.n	a2, a8, 52	# MEM[(opus_int32 *)sLPC_Q14_491 + 52B], _973
	l32i.n	a4, a8, 60	# MEM[(opus_int32 *)sLPC_Q14_491 + 60B], _1015
	mull	a9, a9, a13	#, _954, prephitmp_2131
	l16si	a8, a8, 52	# MEM[(opus_int32 *)sLPC_Q14_491 + 52B], _975
	srai	a15, a15, 15	# tmp1045, _931,
	srai	a5, a5, 15	# tmp1075, _994,
	s32i.n	a10, sp, 52	# %sfp,
	addi.n	a15, a15, 1	# tmp1046, tmp1045,
	mull	a10, a7, a11	#, _996, prephitmp_2130
	addi.n	a5, a5, 1	# tmp1076, tmp1075,
	mull	a7, a7, a13	#, _996, prephitmp_2131
	s32i	a9, sp, 88	# %sfp,
	srai	a3, a3, 15	# tmp1055, _952,
	mull	a9, a8, a11	#, _975, prephitmp_2130
	srai	a15, a15, 1	# tmp1047, tmp1046,
	mull	a8, a8, a13	#, _975, prephitmp_2131
	srai	a5, a5, 1	# tmp1077, tmp1076,
	mull	a5, a5, a14	#, tmp1077, gain_adj_Q16
	s32i	a7, sp, 104	# %sfp,
	addi.n	a3, a3, 1	# tmp1056, tmp1055,
	l32i.n	a7, sp, 48	# %sfp,
	mull	a15, a15, a14	# tmp1048, tmp1047, gain_adj_Q16
	s32i	a8, sp, 92	# %sfp,
	srai	a2, a2, 15	# tmp1065, _973,
	srai	a3, a3, 1	# tmp1057, tmp1056,
	s32i	a5, sp, 96	# %sfp,
	l32i.n	a8, sp, 52	# %sfp,
	mull	a5, a6, a11	#, _1017, prephitmp_2130
	s32i	a10, sp, 100	# %sfp,
	add.n	a15, a15, a7	# tmp1050, tmp1048,
	srai	a10, a12, 16	# tmp1052, tmp1051,
	l32i	a7, sp, 92	# %sfp,
	l32i	a12, sp, 88	# %sfp,
	addi.n	a2, a2, 1	# tmp1066, tmp1065,
	mull	a3, a3, a14	# tmp1058, tmp1057, gain_adj_Q16
	s32i.n	a9, sp, 60	# %sfp,
	srai	a2, a2, 1	# tmp1067, tmp1066,
	srai	a9, a12, 16	# tmp1062,,
	s32i	a5, sp, 80	# %sfp,
	l32i	a12, sp, 96	# %sfp,
	l32i.n	a5, sp, 60	# %sfp,
	add.n	a3, a3, a8	# tmp1060, tmp1058,
	mull	a2, a2, a14	# tmp1068, tmp1067, gain_adj_Q16
	srai	a8, a7, 16	# tmp1072,,
	l32i	a7, sp, 100	# %sfp,
	srai	a4, a4, 15	# tmp1085, _1015,
	add.n	a2, a2, a5	# tmp1070, tmp1068,
	addi.n	a4, a4, 1	# tmp1086, tmp1085,
	add.n	a5, a12, a7	# tmp1080,,
	l32i	a12, sp, 104	# %sfp,
	srai	a4, a4, 1	# tmp1087, tmp1086,
	srai	a7, a12, 16	# tmp1082,,
	mull	a4, a4, a14	# tmp1088, tmp1087, gain_adj_Q16
	l32i	a12, sp, 80	# %sfp,
	mull	a6, a6, a13	# tmp1091, _1017, prephitmp_2131
	add.n	a4, a4, a12	# tmp1090, tmp1088,
	add.n	a2, a2, a8	# tmp1073, tmp1070, tmp1072
	srai	a6, a6, 16	# tmp1092, tmp1091,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	l32i	a8, sp, 116	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	add.n	a3, a3, a9	# tmp1063, tmp1060, tmp1062
	add.n	a15, a15, a10	# tmp1053, tmp1050, tmp1052
	add.n	a5, a5, a7	# tmp1083, tmp1080, tmp1082
	add.n	a4, a4, a6	# tmp1093, tmp1090, tmp1092
	l32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:132:                 sLPC_Q14[ i ] = silk_SMULWW( gain_adj_Q16, sLPC_Q14[ i ] );
	s32i.n	a15, a8, 44	# MEM[(opus_int32 *)sLPC_Q14_491 + 44B], tmp1053
	s32i.n	a3, a8, 48	# MEM[(opus_int32 *)sLPC_Q14_491 + 48B], tmp1063
	s32i.n	a2, a8, 52	# MEM[(opus_int32 *)sLPC_Q14_491 + 52B], tmp1073
	s32i.n	a5, a8, 56	# MEM[(opus_int32 *)sLPC_Q14_491 + 56B], tmp1083
	s32i.n	a4, a8, 60	# MEM[(opus_int32 *)sLPC_Q14_491 + 60B], tmp1093
	l32i.n	a12, a9, 16	# MEM[base: _2818, offset: 16B], _45
	j	.L20		#
.L60:
# @OPUS@\upstream\silk\decode_core.c:135:             gain_adj_Q16 = (opus_int32)1 << 16;
	l32r	a14, .LC0	#, gain_adj_Q16
	movi.n	a13, 0	# prephitmp_2131,
	movi.n	a11, 1	# prephitmp_2130,
.L20:
# @OPUS@\upstream\silk\decode_core.c:143:         if( psDec->lossCnt && psDec->prevSignalType == TYPE_VOICED &&
	l32i	a10, sp, 164	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:140:         psDec->prev_gain_Q16 = psDecCtrl->Gains_Q16[ k ];
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:143:         if( psDec->lossCnt && psDec->prevSignalType == TYPE_VOICED &&
	l32i	a2, a10, 68	# psDec_483(D)->lossCnt, psDec_483(D)->lossCnt
# @OPUS@\upstream\silk\decode_core.c:140:         psDec->prev_gain_Q16 = psDecCtrl->Gains_Q16[ k ];
	s32i.n	a12, a8, 4	# psDec_483(D)->prev_gain_Q16, _45
# @OPUS@\upstream\silk\decode_core.c:143:         if( psDec->lossCnt && psDec->prevSignalType == TYPE_VOICED &&
	beqz.n	a2, .L30	# psDec_483(D)->lossCnt,
# @OPUS@\upstream\silk\decode_core.c:143:         if( psDec->lossCnt && psDec->prevSignalType == TYPE_VOICED &&
	l32i	a2, a10, 72	# psDec_483(D)->prevSignalType, psDec_483(D)->prevSignalType
	bnei	a2, 2, .L30	# psDec_483(D)->prevSignalType,,
# @OPUS@\upstream\silk\decode_core.c:143:         if( psDec->lossCnt && psDec->prevSignalType == TYPE_VOICED &&
	l32i	a9, sp, 156	# %sfp,
	l8ui	a2, a9, 209	# psDec_483(D)->indices.signalType, tmp1100
# @OPUS@\upstream\silk\decode_core.c:144:             psDec->indices.signalType != TYPE_VOICED && k < MAX_NB_SUBFR/2 ) {
	beqi	a2, 2, .L30	# tmp1100,,
	l32i	a10, sp, 128	# %sfp,
	bgei	a10, 2, .L30	#,,
# @OPUS@\upstream\silk\decode_core.c:146:             silk_memset( B_Q14, 0, LTP_ORDER * sizeof( opus_int16 ) );
	l32i	a12, sp, 152	# %sfp,
	movi.n	a2, 0	# tmp1111,
# @OPUS@\upstream\silk\decode_core.c:150:             psDecCtrl->pitchL[ k ] = psDec->lagPrev;
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:146:             silk_memset( B_Q14, 0, LTP_ORDER * sizeof( opus_int16 ) );
	s8i	a2, a12, 0	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 1	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 2	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 3	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 6	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 7	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 8	# MEM[(void *)B_Q14_510], tmp1111
	s8i	a2, a12, 9	# MEM[(void *)B_Q14_510], tmp1111
# @OPUS@\upstream\silk\decode_core.c:147:             B_Q14[ LTP_ORDER/2 ] = SILK_FIX_CONST( 0.25, 14 );
	l32r	a10, .LC11	#,
	l32i	a9, sp, 152	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:150:             psDecCtrl->pitchL[ k ] = psDec->lagPrev;
	l32i.n	a12, a8, 8	# psDec_483(D)->lagPrev, pretmp_2376
# @OPUS@\upstream\silk\decode_core.c:150:             psDecCtrl->pitchL[ k ] = psDec->lagPrev;
	l32i	a8, sp, 132	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:147:             B_Q14[ LTP_ORDER/2 ] = SILK_FIX_CONST( 0.25, 14 );
	s16i	a10, a9, 4	# MEM[base: B_Q14_510, offset: 4B],
# @OPUS@\upstream\silk\decode_core.c:150:             psDecCtrl->pitchL[ k ] = psDec->lagPrev;
	s32i.n	a12, a8, 0	# MEM[base: _2818, offset: 0B], pretmp_2376
	j	.L32		#
.L30:
# @OPUS@\upstream\silk\decode_core.c:153:         if( signalType == TYPE_VOICED ) {
	l32i	a9, sp, 76	# %sfp,
	bnei	a9, 2, .L33	#,,
	l32i	a10, sp, 132	# %sfp,
	l32i.n	a12, a10, 0	# MEM[base: _2818, offset: 0B], pretmp_2376
.L32:
# @OPUS@\upstream\silk\decode_core.c:158:             if( k == 0 || ( k == 2 && NLSF_interpolation_flag ) ) {
	l32i	a8, sp, 128	# %sfp,
	beqz.n	a8, .L34	#,
# @OPUS@\upstream\silk\decode_core.c:158:             if( k == 0 || ( k == 2 && NLSF_interpolation_flag ) ) {
	bnei	a8, 2, .L37	#,,
	l32i	a9, sp, 256	# %sfp,
	beqz.n	a9, .L37	#,
	j	.L35		#
.L57:
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	addi.n	a7, a12, 2	# tmp1131, pretmp_2376,
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	blti	a7, 1, .L38	# tmp1131,,
	l32i	a10, sp, 180	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:176:                     sLTP_Q15[ sLTP_buf_idx - i - 1 ] = silk_SMULWB( inv_gain_Q31, sLTP[ psDec->ltp_mem_length - i - 1 ] );
	l32i.n	a14, sp, 56	# %sfp,
	slli	a6, a10, 2	# tmp1132,,
	l32i	a10, sp, 184	# %sfp,
	addi	a6, a6, -4	# tmp1134, tmp1132,
	add.n	a6, a10, a6	# ivtmp$104,, tmp1134
	l32r	a5, .LC5	#, tmp1468
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	l32i	a3, sp, 248	# %sfp, sLTP
	l32i	a10, sp, 112	# %sfp, tmp1465
# @OPUS@\upstream\silk\decode_core.c:176:                     sLTP_Q15[ sLTP_buf_idx - i - 1 ] = silk_SMULWB( inv_gain_Q31, sLTP[ psDec->ltp_mem_length - i - 1 ] );
	srai	a8, a14, 16	# _100,,
	extui	a9, a14, 0, 16	# _2463,,
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	movi.n	a4, 0	# i,
.L39:
# @OPUS@\upstream\silk\decode_core.c:176:                     sLTP_Q15[ sLTP_buf_idx - i - 1 ] = silk_SMULWB( inv_gain_Q31, sLTP[ psDec->ltp_mem_length - i - 1 ] );
	l32i.n	a2, a10, 36	# psDec_483(D)->ltp_mem_length, psDec_483(D)->ltp_mem_length
	addi	a6, a6, -4	# ivtmp$104, ivtmp$104,
	sub	a2, a2, a4	# tmp1135, psDec_483(D)->ltp_mem_length, i
	add.n	a2, a2, a5	# tmp1138, tmp1135, tmp1468
	slli	a2, a2, 1	# tmp1140, tmp1138,
	add.n	a2, a3, a2	# tmp1141, sLTP, tmp1140
	l16si	a11, a2, 0	# *_106, _108
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	addi.n	a4, a4, 1	# i, i,
# @OPUS@\upstream\silk\decode_core.c:176:                     sLTP_Q15[ sLTP_buf_idx - i - 1 ] = silk_SMULWB( inv_gain_Q31, sLTP[ psDec->ltp_mem_length - i - 1 ] );
	mull	a2, a11, a9	# tmp1144, _108, _2463
	mull	a11, a8, a11	# tmp1146, _100, _108
	srai	a2, a2, 16	# tmp1145, tmp1144,
	add.n	a2, a2, a11	# tmp1147, tmp1145, tmp1146
# @OPUS@\upstream\silk\decode_core.c:176:                     sLTP_Q15[ sLTP_buf_idx - i - 1 ] = silk_SMULWB( inv_gain_Q31, sLTP[ psDec->ltp_mem_length - i - 1 ] );
	s32i.n	a2, a6, 4	# MEM[base: _2848, offset: 0B], tmp1147
# @OPUS@\upstream\silk\decode_core.c:175:                 for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	bne	a4, a7, .L39	# i, tmp1131,
	j	.L38		#
.L37:
# @OPUS@\upstream\silk\decode_core.c:180:                 if( gain_adj_Q16 != (opus_int32)1 << 16 ) {
	l32r	a2, .LC0	#, tmp1148
	beq	a14, a2, .L38	# gain_adj_Q16, tmp1148,
# @OPUS@\upstream\silk\decode_core.c:181:                     for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	addi.n	a2, a12, 2	# tmp1149, pretmp_2376,
# @OPUS@\upstream\silk\decode_core.c:181:                     for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	blti	a2, 1, .L38	# tmp1149,,
	l32i	a8, sp, 180	# %sfp,
	l32i	a9, sp, 184	# %sfp,
	slli	a4, a8, 2	# tmp1150,,
	addi	a4, a4, -4	# _2839, tmp1150,
	add.n	a2, a9, a4	# tmp1153,, _2839
	addi	a2, a2, -8	# tmp1154, tmp1153,
	slli	a6, a12, 2	# tmp1155, pretmp_2376,
	add.n	a4, a9, a4	# ivtmp$108,, _2839
	sub	a6, a2, a6	# _2829, tmp1154, tmp1155
.L40:
# @OPUS@\upstream\silk\decode_core.c:186:                         const opus_int32 previous = *(const volatile opus_int32 *)&sLTP_Q15[sLTP_buf_idx - i - 1];
	memw
	l32i.n	a2, a4, 0	# MEM[(const opus_int32 *)_124], previous
	addi	a4, a4, -4	# ivtmp$108, ivtmp$108,
# @OPUS@\upstream\silk\decode_core.c:187:                         sLTP_Q15[sLTP_buf_idx - i - 1] = silk_SMULWW(gain_adj_Q16, previous);
	slli	a3, a2, 16	# tmp1156, previous,
	srai	a2, a2, 15	# tmp1157, previous,
	srai	a3, a3, 16	# _127, tmp1156,
	addi.n	a2, a2, 1	# tmp1158, tmp1157,
	mull	a5, a3, a13	# tmp1161, _127, prephitmp_2131
	srai	a2, a2, 1	# tmp1159, tmp1158,
	mull	a2, a2, a14	# tmp1160, tmp1159, gain_adj_Q16
	srai	a5, a5, 16	# tmp1162, tmp1161,
	mull	a3, a3, a11	# tmp1164, _127, prephitmp_2130
	add.n	a2, a2, a5	# tmp1163, tmp1160, tmp1162
	add.n	a2, a2, a3	# tmp1165, tmp1163, tmp1164
# @OPUS@\upstream\silk\decode_core.c:187:                         sLTP_Q15[sLTP_buf_idx - i - 1] = silk_SMULWW(gain_adj_Q16, previous);
	s32i.n	a2, a4, 4	# MEM[base: _124, offset: 0B], tmp1165
# @OPUS@\upstream\silk\decode_core.c:181:                     for( i = 0; i < lag + LTP_ORDER/2; i++ ) {
	bne	a6, a4, .L40	# _2829, ivtmp$108,
	j	.L38		#
.L56:
	l32i	a8, sp, 184	# %sfp,
	mov.n	a10, a14	#,
	slli	a2, a14, 2	# tmp1166, tmp10,
	l32i	a14, sp, 144	# %sfp, ivtmp$98
	add.n	a13, a8, a2	# ivtmp$100,, tmp1166
	addi	a12, a12, -16	# tmp1167, _142,
	addi.n	a9, a10, 1	#,,
	mov.n	a15, a14	# ivtmp$98, ivtmp$98
	mov.n	a14, a13	# ivtmp$100, ivtmp$100
	l32i	a13, sp, 152	# %sfp, ivtmp$116
	add.n	a12, a8, a12	# ivtmp$101,, tmp1167
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	movi.n	a11, 0	# i,
	s32i	a9, sp, 80	# %sfp,
.L41:
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	l16si	a5, a13, 4	# MEM[base: B_Q14_510, offset: 4B],
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	l16si	a10, a13, 0	# MEM[base: B_Q14_510, offset: 0B],
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	l16si	a3, a13, 2	# MEM[base: B_Q14_510, offset: 2B],
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	l16si	a8, a13, 6	# MEM[base: B_Q14_510, offset: 6B],
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	l16si	a9, a13, 8	# MEM[base: B_Q14_510, offset: 8B],
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	s32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	l32i.n	a4, a12, 16	# MEM[base: _2864, offset: 16B], _143
	s32i	a10, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	l32i.n	a2, a12, 12	# MEM[base: _2864, offset: 12B], _152
	s32i	a3, sp, 76	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	l32i.n	a7, a12, 8	# MEM[base: _2864, offset: 8B], _161
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	l32i.n	a6, a12, 4	# MEM[base: _2864, offset: 4B], _170
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	l32i.n	a5, a12, 0	# MEM[base: _2864, offset: 0B], _181
	s32i.n	a9, sp, 52	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a10, a15, 0	#, ivtmp$98
# 0 "" 2
#NO_APP
	s32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	l32i	a9, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	l32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	srai	a3, a4, 16	# tmp1179, _143,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	srai	a8, a2, 16	# tmp1181, _152,
	mull	a8, a8, a10	# tmp1182, tmp1181,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	mull	a3, a3, a9	# tmp1180, tmp1179,
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	srai	a10, a7, 16	# tmp1185, _161,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a3, a3, a8	# tmp1183, tmp1180, tmp1182
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	l32i.n	a8, sp, 56	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	addi.n	a3, a3, 2	# tmp1184, tmp1183,
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	mull	a10, a10, a8	# tmp1186, tmp1185,
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	l32i.n	a8, sp, 48	# %sfp,
	srai	a9, a6, 16	# tmp1188, _170,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a3, a3, a10	# tmp1187, tmp1184, tmp1186
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	l32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	mull	a9, a9, a8	# tmp1189, tmp1188,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	srai	a8, a5, 16	# tmp1191, _181,
	mull	a8, a8, a10	# tmp1192, tmp1191,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	l32i	a10, sp, 72	# %sfp,
	extui	a4, a4, 0, 16	# tmp1194, _143,
	mull	a4, a4, a10	# tmp1195, tmp1194,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a3, a3, a9	# tmp1190, tmp1187, tmp1189
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	l32i	a9, sp, 76	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a3, a3, a8	# tmp1193, tmp1190, tmp1192
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	l32i.n	a10, sp, 56	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	extui	a2, a2, 0, 16	# tmp1198, _152,
# @OPUS@\upstream\silk\decode_core.c:204:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[  0 ], B_Q14[ 0 ] );
	srai	a4, a4, 16	# tmp1196, tmp1195,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	mull	a2, a2, a9	# tmp1199, tmp1198,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a4, a3, a4	# tmp1197, tmp1193, tmp1196
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	extui	a7, a7, 0, 16	# tmp1202, _161,
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	l32i.n	a3, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	mull	a7, a7, a10	# tmp1203, tmp1202,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	extui	a6, a6, 0, 16	# tmp1206, _170,
# @OPUS@\upstream\silk\decode_core.c:205:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -1 ], B_Q14[ 1 ] );
	srai	a2, a2, 16	# tmp1200, tmp1199,
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	mull	a6, a6, a3	# tmp1207, tmp1206,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	extui	a5, a5, 0, 16	# tmp1210, _181,
	mull	a5, a5, a8	# tmp1211, tmp1210,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a4, a4, a2	# tmp1201, tmp1197, tmp1200
# @OPUS@\upstream\silk\decode_core.c:206:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -2 ], B_Q14[ 2 ] );
	srai	a7, a7, 16	# tmp1204, tmp1203,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a2, a4, a7	# tmp1205, tmp1201, tmp1204
# @OPUS@\upstream\silk\decode_core.c:207:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -3 ], B_Q14[ 3 ] );
	srai	a6, a6, 16	# tmp1208, tmp1207,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a2, a2, a6	# tmp1209, tmp1205, tmp1208
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	srai	a5, a5, 16	# tmp1212, tmp1211,
# @OPUS@\upstream\silk\decode_core.c:213:                 pres_Q14[i] = silk_ADD_LSHIFT32(yoradio_opus_load32(&pexc_Q14[i]), LTP_pred_Q13, 1);
	l32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:208:                 LTP_pred_Q13 = silk_SMLAWB( LTP_pred_Q13, pred_lag_ptr[ -4 ], B_Q14[ 4 ] );
	add.n	a2, a2, a5	# LTP_pred_Q13, tmp1209, tmp1212
# @OPUS@\upstream\silk\decode_core.c:213:                 pres_Q14[i] = silk_ADD_LSHIFT32(yoradio_opus_load32(&pexc_Q14[i]), LTP_pred_Q13, 1);
	l32i	a10, sp, 168	# %sfp,
	slli	a3, a11, 2	# tmp1215, i,
# @OPUS@\upstream\silk\decode_core.c:213:                 pres_Q14[i] = silk_ADD_LSHIFT32(yoradio_opus_load32(&pexc_Q14[i]), LTP_pred_Q13, 1);
	slli	a2, a2, 1	# tmp1214, LTP_pred_Q13,
	add.n	a2, a2, a9	# _198, tmp1214,
# @OPUS@\upstream\silk\decode_core.c:213:                 pres_Q14[i] = silk_ADD_LSHIFT32(yoradio_opus_load32(&pexc_Q14[i]), LTP_pred_Q13, 1);
	add.n	a3, a10, a3	# tmp1216,, tmp1215
	s32i.n	a2, a3, 0	# MEM[base: _2861, offset: 0B], _198
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:219:                 sLTP_Q15[ sLTP_buf_idx ] = silk_LSHIFT( pres_Q14[ i ], 1 );
	slli	a2, a2, 1	# tmp1217, _198,
# @OPUS@\upstream\silk\decode_core.c:219:                 sLTP_Q15[ sLTP_buf_idx ] = silk_LSHIFT( pres_Q14[ i ], 1 );
	s32i.n	a2, a14, 0	# MEM[base: _2860, offset: 0B], tmp1217
	l32i	a9, sp, 80	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i.n	a3, a8, 32	# psDec_483(D)->subfr_length, pretmp_2139
	add.n	a2, a9, a11	# sLTP_buf_idx,, i
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	addi.n	a11, a11, 1	# i, i,
	addi.n	a15, a15, 4	# ivtmp$98, ivtmp$98,
	addi.n	a14, a14, 4	# ivtmp$100, ivtmp$100,
	addi.n	a12, a12, 4	# ivtmp$101, ivtmp$101,
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	blt	a11, a3, .L41	# i, pretmp_2139,
	s32i	a2, sp, 180	# %sfp, sLTP_buf_idx
# @OPUS@\upstream\silk\decode_core.c:115:         pres_Q14 = res_Q14;
	mov.n	a4, a10	# pres_Q14,
	j	.L42		#
.L33:
	l32i	a10, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:153:         if( signalType == TYPE_VOICED ) {
	l32i	a4, sp, 144	# %sfp, pres_Q14
	l32i.n	a3, a10, 32	# psDec_483(D)->subfr_length, pretmp_2139
.L42:
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	blti	a3, 1, .L43	# pretmp_2139,,
	l32i	a12, sp, 64	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	l32i	a14, sp, 68	# %sfp,
	slli	a2, a12, 16	# tmp1223,,
	srai	a2, a2, 16	#, tmp1223,
	s32i	a2, sp, 120	# %sfp,
	l32i	a5, sp, 120	# %sfp,
	srai	a3, a14, 21	# tmp1221,,
	slli	a2, a2, 16	# tmp1225,,
	addi.n	a3, a3, 1	# tmp1222, tmp1221,
	sub	a2, a2, a5	# tmp1226, tmp1225,
	l32i	a8, sp, 148	# %sfp,
	srai	a3, a3, 1	#, tmp1222,
	srai	a2, a2, 16	#, tmp1226,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	movi.n	a9, 0	#,
	l32i	a15, sp, 116	# %sfp, ivtmp$86
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	s32i	a3, sp, 124	# %sfp,
	s32i	a8, sp, 72	# %sfp,
	s32i	a4, sp, 76	# %sfp, pres_Q14
	s32i	a2, sp, 140	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	s32i	a9, sp, 68	# %sfp,
.L50:
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	l32i.n	a10, a15, 60	# MEM[base: _2885, offset: 60B],
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	l32i.n	a12, a15, 56	# MEM[base: _2885, offset: 56B],
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	l16si	a14, sp, 0	# A_Q12_tmp, _214
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	l16si	a13, sp, 2	# A_Q12_tmp, _226
# @OPUS@\upstream\silk\decode_core.c:230:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	srai	a5, a10, 16	# tmp1248,,
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	srai	a2, a12, 16	# tmp1250,,
# @OPUS@\upstream\silk\decode_core.c:230:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	l32i.n	a8, a8, 40	# psDec_483(D)->LPC_order,
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	mull	a5, a5, a14	# tmp1249, tmp1248, _214
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	mull	a2, a2, a13	# tmp1251, tmp1250, _226
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	l16si	a10, sp, 8	# A_Q12_tmp,
	add.n	a6, a5, a2	# tmp1252, tmp1249, tmp1251
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	l32i.n	a9, a15, 52	# MEM[base: _2885, offset: 52B],
# @OPUS@\upstream\silk\decode_core.c:230:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	srai	a5, a8, 1	# LPC_pred_Q10,,
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	l16si	a3, sp, 4	# A_Q12_tmp,
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	s32i	a10, sp, 96	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	l32i.n	a2, a15, 48	# MEM[base: _2885, offset: 48B],
	add.n	a5, a6, a5	# tmp1254, tmp1252, LPC_pred_Q10
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	l32i.n	a6, a15, 44	# MEM[base: _2885, offset: 44B],
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	l16si	a12, sp, 6	# A_Q12_tmp, _250
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:230:             LPC_pred_Q10 = silk_RSHIFT( psDec->LPC_order, 1 );
	s32i	a8, sp, 264	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	srai	a4, a9, 16	# tmp1255,,
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	l32i.n	a8, a15, 40	# MEM[base: _2885, offset: 40B],
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	s32i	a3, sp, 64	# %sfp,
	mull	a4, a4, a3	# tmp1256, tmp1255,
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	l16si	a11, sp, 10	# A_Q12_tmp, _274
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	srai	a3, a2, 16	# tmp1258,,
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	srai	a2, a6, 16	# tmp1261,,
	mull	a6, a2, a7	# tmp1262, tmp1261,
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	mull	a3, a3, a12	# tmp1259, tmp1258, _250
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	srai	a2, a8, 16	# tmp1264,,
	add.n	a5, a5, a4	# tmp1257, tmp1254, tmp1256
	mull	a4, a2, a11	# tmp1265, tmp1264, _274
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	l32i.n	a2, a15, 36	# MEM[base: _2885, offset: 36B],
	add.n	a5, a5, a3	# tmp1260, tmp1257, tmp1259
	srai	a3, a2, 16	# tmp1267,,
	add.n	a2, a5, a6	# tmp1263, tmp1260, tmp1262
	add.n	a2, a2, a4	# tmp1266, tmp1263, tmp1265
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	l32i.n	a5, a15, 32	# MEM[base: _2885, offset: 32B],
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	l32i.n	a4, a15, 28	# MEM[base: _2885, offset: 28B],
	l16si	a8, sp, 16	# A_Q12_tmp, _310
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	srai	a6, a5, 16	# tmp1270,,
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	srai	a5, a4, 16	# tmp1273,,
	mull	a5, a5, a8	#, tmp1273, _310
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	l16si	a10, sp, 12	# A_Q12_tmp, _286
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	l16si	a9, sp, 14	# A_Q12_tmp, _298
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	s32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	l32i.n	a5, a15, 24	# MEM[base: _2885, offset: 24B],
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	mull	a3, a3, a10	# tmp1268, tmp1267, _286
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	mull	a6, a6, a9	# tmp1271, tmp1270, _298
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	srai	a4, a5, 16	# tmp1276,,
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	l32i.n	a5, a15, 60	# MEM[base: _2885, offset: 60B],
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	l16si	a7, sp, 18	# A_Q12_tmp, _322
	add.n	a2, a2, a3	# tmp1269, tmp1266, tmp1268
	add.n	a2, a2, a6	# tmp1272, tmp1269, tmp1271
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	extui	a3, a5, 0, 16	# tmp1279,,
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	l32i.n	a6, a15, 56	# MEM[base: _2885, offset: 56B],
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	mull	a4, a4, a7	# tmp1277, tmp1276, _322
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	mull	a3, a3, a14	# tmp1280, tmp1279, _214
	add.n	a2, a2, a5	# tmp1275, tmp1272,
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	extui	a14, a6, 0, 16	# tmp1283,,
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	l32i.n	a6, a15, 52	# MEM[base: _2885, offset: 52B],
	add.n	a2, a2, a4	# tmp1278, tmp1275, tmp1277
	l32i	a4, sp, 64	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	mull	a14, a14, a13	# tmp1284, tmp1283, _226
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	extui	a13, a6, 0, 16	# tmp1287,,
	mull	a5, a13, a4	# tmp1288, tmp1287,
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	l32i.n	a4, a15, 48	# MEM[base: _2885, offset: 48B],
# @OPUS@\upstream\silk\decode_core.c:231:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  1 ], A_Q12_tmp[ 0 ] );
	srai	a3, a3, 16	# tmp1281, tmp1280,
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	extui	a6, a4, 0, 16	# tmp1291,,
	add.n	a2, a2, a3	# tmp1282, tmp1278, tmp1281
# @OPUS@\upstream\silk\decode_core.c:232:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  2 ], A_Q12_tmp[ 1 ] );
	srai	a14, a14, 16	# tmp1285, tmp1284,
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	mull	a12, a6, a12	# tmp1292, tmp1291, _250
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	l32i.n	a6, a15, 44	# MEM[base: _2885, offset: 44B],
# @OPUS@\upstream\silk\decode_core.c:233:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  3 ], A_Q12_tmp[ 2 ] );
	srai	a13, a5, 16	# tmp1289, tmp1288,
	add.n	a2, a2, a14	# tmp1286, tmp1282, tmp1285
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	l32i.n	a5, a15, 40	# MEM[base: _2885, offset: 40B],
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	l32i	a14, sp, 96	# %sfp,
	extui	a4, a6, 0, 16	# tmp1295,,
	add.n	a2, a2, a13	# tmp1290, tmp1286, tmp1289
# @OPUS@\upstream\silk\decode_core.c:234:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  4 ], A_Q12_tmp[ 3 ] );
	srai	a12, a12, 16	# tmp1293, tmp1292,
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	l32i.n	a6, a15, 36	# MEM[base: _2885, offset: 36B],
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	extui	a3, a5, 0, 16	# tmp1299,,
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	mull	a4, a4, a14	# tmp1296, tmp1295,
	add.n	a2, a2, a12	# tmp1294, tmp1290, tmp1293
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	l32i.n	a12, a15, 32	# MEM[base: _2885, offset: 32B],
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	mull	a11, a3, a11	# tmp1300, tmp1299, _274
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	l32i.n	a14, a15, 28	# MEM[base: _2885, offset: 28B],
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	extui	a3, a6, 0, 16	# tmp1303,,
# @OPUS@\upstream\silk\decode_core.c:235:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  5 ], A_Q12_tmp[ 4 ] );
	srai	a4, a4, 16	# tmp1297, tmp1296,
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	mull	a10, a3, a10	# tmp1304, tmp1303, _286
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	extui	a5, a12, 0, 16	# tmp1307,,
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	l32i.n	a3, a15, 24	# MEM[base: _2885, offset: 24B],
	add.n	a2, a2, a4	# tmp1298, tmp1294, tmp1297
# @OPUS@\upstream\silk\decode_core.c:236:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  6 ], A_Q12_tmp[ 5 ] );
	srai	a11, a11, 16	# tmp1301, tmp1300,
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	mull	a9, a5, a9	# tmp1308, tmp1307, _298
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	extui	a6, a14, 0, 16	# tmp1311,,
	add.n	a2, a2, a11	# tmp1302, tmp1298, tmp1301
# @OPUS@\upstream\silk\decode_core.c:237:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  7 ], A_Q12_tmp[ 6 ] );
	srai	a10, a10, 16	# tmp1305, tmp1304,
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	mull	a8, a6, a8	# tmp1312, tmp1311, _310
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	extui	a13, a3, 0, 16	# tmp1314,,
	add.n	a2, a2, a10	# tmp1306, tmp1302, tmp1305
# @OPUS@\upstream\silk\decode_core.c:238:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  8 ], A_Q12_tmp[ 7 ] );
	srai	a9, a9, 16	# tmp1309, tmp1308,
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	mull	a13, a13, a7	# tmp1315, tmp1314, _322
	add.n	a2, a2, a9	# tmp1310, tmp1306, tmp1309
# @OPUS@\upstream\silk\decode_core.c:239:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i -  9 ], A_Q12_tmp[ 8 ] );
	srai	a8, a8, 16	# tmp1313, tmp1312,
# @OPUS@\upstream\silk\decode_core.c:241:             if( psDec->LPC_order == 16 ) {
	l32i	a4, sp, 264	# %sfp,
	add.n	a8, a2, a8	# _800, tmp1310, tmp1313
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	srai	a7, a13, 16	# tmp1316, tmp1315,
# @OPUS@\upstream\silk\decode_core.c:240:             LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 10 ], A_Q12_tmp[ 9 ] );
	add.n	a7, a7, a8	# LPC_pred_Q10, tmp1316, _800
# @OPUS@\upstream\silk\decode_core.c:241:             if( psDec->LPC_order == 16 ) {
	bnei	a4, 16, .L44	#,,
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	l32i.n	a3, a15, 20	# MEM[base: _2885, offset: 20B], _331
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	l32i.n	a5, a15, 16	# MEM[base: _2885, offset: 16B],
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	l16si	a13, sp, 20	# A_Q12_tmp, _334
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	l16si	a12, sp, 22	# A_Q12_tmp, _346
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	srai	a2, a3, 16	# tmp1329, _331,
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	srai	a14, a5, 16	# tmp1331,,
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	l32i.n	a6, a15, 12	# MEM[base: _2885, offset: 12B],
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	mull	a5, a2, a13	# tmp1330, tmp1329, _334
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	mull	a14, a14, a12	# tmp1332, tmp1331, _346
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	l16si	a11, sp, 24	# A_Q12_tmp, _358
	srai	a2, a6, 16	# tmp1334,,
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	l32i.n	a8, a15, 8	# MEM[base: _2885, offset: 8B],
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	mull	a4, a2, a11	# tmp1335, tmp1334, _358
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	l16si	a10, sp, 26	# A_Q12_tmp, _370
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a5, a14	# tmp1333, tmp1330, tmp1332
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	l32i.n	a14, a15, 4	# MEM[base: _2885, offset: 4B],
	l16si	a9, sp, 28	# A_Q12_tmp, _382
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	srai	a6, a8, 16	# tmp1337,,
	mull	a6, a6, a10	# tmp1338, tmp1337, _370
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	srai	a5, a14, 16	# tmp1340,,
	mull	a5, a5, a9	# tmp1341, tmp1340, _382
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a4	# tmp1336, tmp1333, tmp1335
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	l32i.n	a14, a15, 0	# MEM[base: _2885, offset: 0B],
	l16si	a8, sp, 30	# A_Q12_tmp, _393
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a6	# tmp1339, tmp1336, tmp1338
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	l32i.n	a6, a15, 16	# MEM[base: _2885, offset: 16B],
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	srai	a4, a14, 16	# tmp1343,,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a5	# tmp1342, tmp1339, tmp1341
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	extui	a3, a3, 0, 16	# tmp1346, _331,
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	l32i.n	a5, a15, 12	# MEM[base: _2885, offset: 12B],
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	mull	a4, a4, a8	# tmp1344, tmp1343, _393
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	extui	a14, a6, 0, 16	# tmp1350,,
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	mull	a3, a3, a13	# tmp1347, tmp1346, _334
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	mull	a12, a14, a12	# tmp1351, tmp1350, _346
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	extui	a14, a5, 0, 16	# tmp1354,,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a4	# tmp1345, tmp1342, tmp1344
# @OPUS@\upstream\silk\decode_core.c:242:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 11 ], A_Q12_tmp[ 10 ] );
	srai	a3, a3, 16	# tmp1348, tmp1347,
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	mull	a11, a14, a11	# tmp1355, tmp1354, _358
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	l32i.n	a14, a15, 8	# MEM[base: _2885, offset: 8B],
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a3	# tmp1349, tmp1345, tmp1348
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	l32i.n	a3, a15, 4	# MEM[base: _2885, offset: 4B],
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	extui	a6, a14, 0, 16	# tmp1358,,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	l32i.n	a4, a15, 0	# MEM[base: _2885, offset: 0B],
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	extui	a5, a3, 0, 16	# tmp1362,,
# @OPUS@\upstream\silk\decode_core.c:243:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 12 ], A_Q12_tmp[ 11 ] );
	srai	a12, a12, 16	# tmp1352, tmp1351,
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	mull	a10, a6, a10	# tmp1359, tmp1358, _370
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a12	# tmp1353, tmp1349, tmp1352
# @OPUS@\upstream\silk\decode_core.c:244:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 13 ], A_Q12_tmp[ 12 ] );
	srai	a11, a11, 16	# tmp1356, tmp1355,
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	mull	a9, a5, a9	# tmp1363, tmp1362, _382
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	extui	a13, a4, 0, 16	# tmp1366,,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a11	# tmp1357, tmp1353, tmp1356
# @OPUS@\upstream\silk\decode_core.c:245:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 14 ], A_Q12_tmp[ 13 ] );
	srai	a10, a10, 16	# tmp1360, tmp1359,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	mull	a8, a13, a8	# tmp1367, tmp1366, _393
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a2, a2, a10	# tmp1361, tmp1357, tmp1360
# @OPUS@\upstream\silk\decode_core.c:246:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 15 ], A_Q12_tmp[ 14 ] );
	srai	a5, a9, 16	# tmp1364, tmp1363,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a5, a2, a5	# tmp1365, tmp1361, tmp1364
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	srai	a8, a8, 16	# tmp1368, tmp1367,
# @OPUS@\upstream\silk\decode_core.c:247:                 LPC_pred_Q10 = silk_SMLAWB( LPC_pred_Q10, sLPC_Q14[ MAX_LPC_ORDER + i - 16 ], A_Q12_tmp[ 15 ] );
	add.n	a5, a5, a8	# tmp1369, tmp1365, tmp1368
	add.n	a7, a7, a5	# LPC_pred_Q10, LPC_pred_Q10, tmp1369
.L44:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
	l32i	a5, sp, 76	# %sfp,
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a3, a5, 0	# value,
# 0 "" 2
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
#NO_APP
	l32r	a6, .LC13	#,
	blt	a6, a7, .L45	#, LPC_pred_Q10,
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	l32r	a8, .LC14	#,
	blt	a7, a8, .L46	# LPC_pred_Q10,,
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	slli	a7, a7, 4	# iftmp$50_562, LPC_pred_Q10,
	add.n	a4, a7, a3	# tmp1373, iftmp$50_562, value
	mov.n	a2, a7	# iftmp$61_468, iftmp$50_562
	bltz	a4, .L55	# tmp1373,
.L52:
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	and	a2, a7, a3	# tmp1374, iftmp$54_467, value
	bltz	a2, .L63	# tmp1374,
.L54:
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	add.n	a7, a3, a7	# iftmp$48_465, value, iftmp$54_467
	l32i	a9, sp, 120	# %sfp,
	extui	a3, a7, 0, 16	# tmp1375, iftmp$48_465,
	mull	a3, a3, a9	# tmp1376, tmp1375,
	srai	a2, a7, 16	# _2342, iftmp$48_465,
	srai	a3, a3, 16	# _2358, tmp1376,
	j	.L48		#
.L55:
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	or	a4, a2, a3	# tmp1377, iftmp$61_468, value
	bgez	a4, .L64	# tmp1377,
.L53:
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	add.n	a7, a3, a2	# iftmp$48_465, value, iftmp$61_468
	l32i	a10, sp, 120	# %sfp,
	extui	a3, a7, 0, 16	# tmp1378, iftmp$48_465,
	mull	a3, a3, a10	# tmp1379, tmp1378,
	srai	a2, a7, 16	# _2342, iftmp$48_465,
	srai	a3, a3, 16	# _2358, tmp1379,
	j	.L48		#
.L63:
	movi.n	a3, 0	# _2358,
	l32r	a2, .LC3	#, _2342
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	l32r	a7, .LC1	#, iftmp$48_465
	j	.L48		#
.L64:
	l32i	a3, sp, 140	# %sfp, _2358
	l32r	a2, .LC4	#, _2342
	l32r	a7, .LC5	#, iftmp$48_465
.L48:
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	l32i	a12, sp, 120	# %sfp,
	l32i	a14, sp, 124	# %sfp,
	mull	a2, a12, a2	# tmp1380,, _2342
	mull	a4, a14, a7	# tmp1381,, iftmp$48_465
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	s32i	a7, a15, 64	# MEM[base: _2885, offset: 64B], iftmp$48_465
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	add.n	a2, a2, a4	# tmp1382, tmp1380, tmp1381
	add.n	a2, a2, a3	# tmp1383, tmp1382, _2358
	srai	a2, a2, 7	# tmp1384, tmp1383,
	addi.n	a2, a2, 1	# tmp1385, tmp1384,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	l32r	a4, .LC4	#, iftmp$67_469
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	srai	a2, a2, 1	# _429, tmp1385,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	blt	a4, a2, .L49	# tmp3, _429,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	l32r	a4, .LC3	#, iftmp$67_469
	blt	a2, a4, .L49	# _429, tmp5,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	slli	a2, a2, 16	# tmp1388, _429,
	srai	a4, a2, 16	# iftmp$67_469, tmp1388,
.L49:
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	l32i	a9, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i	a10, sp, 68	# %sfp,
	l32i	a12, sp, 76	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	addi.n	a10, a10, 1	#,,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i.n	a3, a8, 32	# psDec_483(D)->subfr_length, pretmp_2139
	addi.n	a12, a12, 4	#,,
# @OPUS@\upstream\silk\decode_core.c:260:             pxq[ i ] = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( silk_SMULWW( sLPC_Q14[ MAX_LPC_ORDER + i ], Gain_Q10 ), 8 ) );
	s16i	a4, a9, 0	# MEM[base: _2883, offset: 0B], iftmp$67_469
	addi.n	a9, a9, 2	#,,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	s32i	a10, sp, 68	# %sfp,
	s32i	a9, sp, 72	# %sfp,
	s32i	a12, sp, 76	# %sfp,
	addi.n	a15, a15, 4	# ivtmp$86, ivtmp$86,
# @OPUS@\upstream\silk\decode_core.c:226:         for( i = 0; i < psDec->subfr_length; i++ ) {
	blt	a10, a3, .L50	#, pretmp_2139,
.L43:
# @OPUS@\upstream\silk\decode_core.c:264:         silk_memcpy( sLPC_Q14, &sLPC_Q14[ psDec->subfr_length ], MAX_LPC_ORDER * sizeof( opus_int32 ) );
	l32i	a14, sp, 116	# %sfp,
	slli	a3, a3, 2	# tmp1390, pretmp_2139,
	add.n	a3, a14, a3	#,, tmp1390
	movi.n	a4, 0x40	#,
	mov.n	a2, a14	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	l32i.n	a2, a8, 32	# psDec_483(D)->subfr_length, _437
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	l32i	a10, sp, 144	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:266:         pxq      += psDec->subfr_length;
	l32i	a12, sp, 148	# %sfp,
	l32i	a14, sp, 132	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	l32i.n	a3, a8, 24	# psDec_483(D)->nb_subfr, psDec_483(D)->nb_subfr
	l32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	slli	a4, a2, 2	# tmp1397, _437,
# @OPUS@\upstream\silk\decode_core.c:266:         pxq      += psDec->subfr_length;
	slli	a2, a2, 1	# tmp1398, _437,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	addi.n	a9, a9, 1	#,,
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	add.n	a10, a10, a4	#,, tmp1397
# @OPUS@\upstream\silk\decode_core.c:266:         pxq      += psDec->subfr_length;
	add.n	a12, a12, a2	#,, tmp1398
	addi.n	a14, a14, 4	#,,
	addi.n	a8, a8, 10	#,,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	s32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:265:         pexc_Q14 += psDec->subfr_length;
	s32i	a10, sp, 144	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:266:         pxq      += psDec->subfr_length;
	s32i	a12, sp, 148	# %sfp,
	s32i	a14, sp, 132	# %sfp,
	s32i	a8, sp, 152	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:114:     for( k = 0; k < psDec->nb_subfr; k++ ) {
	blt	a9, a3, .L51	#, psDec_483(D)->nb_subfr,
	j	.L5		#
.L46:
# @OPUS@\upstream\silk\decode_core.c:254:             sLPC_Q14[MAX_LPC_ORDER + i] = silk_ADD_SAT32(excitation, silk_LSHIFT_SAT32(LPC_pred_Q10, 4));
	l32r	a9, .LC1	#,
	add.n	a2, a3, a9	# tmp1401, value,
	mov.n	a7, a9	# iftmp$54_467,
	bgez	a2, .L52	# tmp1401,
	mov.n	a2, a9	# iftmp$61_468,
	j	.L53		#
.L45:
	l32r	a10, .LC2	#,
	add.n	a2, a3, a10	# tmp1403, value,
	mov.n	a7, a10	# iftmp$54_467,
	bgez	a2, .L54	# tmp1403,
	mov.n	a2, a10	# iftmp$61_468,
	j	.L55		#
.L38:
# @OPUS@\upstream\silk\decode_core.c:199:             pred_lag_ptr = &sLTP_Q15[ sLTP_buf_idx - lag + LTP_ORDER / 2 ];
	l32i	a14, sp, 180	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:199:             pred_lag_ptr = &sLTP_Q15[ sLTP_buf_idx - lag + LTP_ORDER / 2 ];
	sub	a12, a14, a12	# tmp1405,, pretmp_2376
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	l32i.n	a3, a8, 32	# psDec_483(D)->subfr_length, pretmp_2139
# @OPUS@\upstream\silk\decode_core.c:199:             pred_lag_ptr = &sLTP_Q15[ sLTP_buf_idx - lag + LTP_ORDER / 2 ];
	addi.n	a12, a12, 2	# tmp1406, tmp1405,
	slli	a12, a12, 2	# _142, tmp1406,
# @OPUS@\upstream\silk\decode_core.c:200:             for( i = 0; i < psDec->subfr_length; i++ ) {
	bgei	a3, 1, .L56	# pretmp_2139,,
	j	.L43		#
.L35:
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i	a9, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:164:                     silk_memcpy( &psDec->outBuf[ psDec->ltp_mem_length ], xq, 2 * psDec->subfr_length * sizeof( opus_int16 ) );
	l32i	a10, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i.n	a5, a9, 36	# psDec_483(D)->ltp_mem_length, _444
# @OPUS@\upstream\silk\decode_core.c:164:                     silk_memcpy( &psDec->outBuf[ psDec->ltp_mem_length ], xq, 2 * psDec->subfr_length * sizeof( opus_int16 ) );
	l32i.n	a4, a9, 32	# psDec_483(D)->subfr_length, psDec_483(D)->subfr_length
	addi	a2, a5, 36	# tmp1411, _444,
	l32i	a3, sp, 252	# %sfp,
	slli	a2, a2, 1	# tmp1412, tmp1411,
	slli	a4, a4, 2	#, psDec_483(D)->subfr_length,
	add.n	a2, a10, a2	#,, tmp1412
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i.n	a15, a9, 40	# psDec_483(D)->LPC_order, _825
	addi	a14, a5, -2	# _1010, _444,
# @OPUS@\upstream\silk\decode_core.c:164:                     silk_memcpy( &psDec->outBuf[ psDec->ltp_mem_length ], xq, 2 * psDec->subfr_length * sizeof( opus_int16 ) );
	call0	memcpy		#
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	sub	a13, a14, a15	# tmp1410, _1010, _825
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i.n	a3, a8, 32	# psDec_483(D)->subfr_length, psDec_483(D)->subfr_length
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	sub	a13, a13, a12	# start_idx, tmp1410, pretmp_2376
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i.n	a2, a8, 36	# psDec_483(D)->ltp_mem_length, psDec_483(D)->ltp_mem_length
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	slli	a3, a3, 1	# tmp1428, psDec_483(D)->subfr_length,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	add.n	a3, a3, a13	# tmp1430, tmp1428, start_idx
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	add.n	a2, a15, a2	# tmp1423, _825, psDec_483(D)->ltp_mem_length
	l32i	a9, sp, 136	# %sfp,
	l32i	a10, sp, 248	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	addi	a3, a3, 36	# tmp1431, tmp1430,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	sub	a5, a2, a14	# tmp1425, tmp1423, _1010
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	slli	a3, a3, 1	# tmp1432, tmp1431,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	slli	a2, a13, 1	# tmp1434, start_idx,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i.n	a6, a8, 40	# psDec_483(D)->LPC_order,
	l32i	a7, sp, 260	# %sfp,
	l32i	a4, sp, 72	# %sfp,
	add.n	a5, a5, a12	#, tmp1425, pretmp_2376
	add.n	a3, a9, a3	#,, tmp1432
	add.n	a2, a10, a2	#,, tmp1434
	call0	silk_LPC_analysis_filter		#
	j	.L57		#
.L34:
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i	a14, sp, 112	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i.n	a2, a14, 36	# psDec_483(D)->ltp_mem_length, psDec_483(D)->ltp_mem_length
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	l32i.n	a6, a14, 40	# psDec_483(D)->LPC_order, _454
# @OPUS@\upstream\silk\decode_core.c:160:                 start_idx = psDec->ltp_mem_length - lag - psDec->LPC_order - LTP_ORDER / 2;
	addi	a2, a2, -2	# tmp1438, psDec_483(D)->ltp_mem_length,
	sub	a2, a2, a6	# tmp1440, tmp1438, _454
	sub	a2, a2, a12	# start_idx$9_79, tmp1440, pretmp_2376
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	addi	a3, a2, 36	# tmp1443, start_idx$9_79,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i	a9, sp, 248	# %sfp,
	addi.n	a5, a6, 2	# tmp1441, _454,
	l32i	a4, sp, 72	# %sfp,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	slli	a3, a3, 1	# tmp1444, tmp1443,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	slli	a2, a2, 1	# tmp1446, start_idx$9_79,
# @OPUS@\upstream\silk\decode_core.c:167:                 silk_LPC_analysis_filter( &sLTP[ start_idx ], &psDec->outBuf[ start_idx + k * psDec->subfr_length ],
	l32i	a7, sp, 260	# %sfp,
	add.n	a3, a8, a3	#,, tmp1444
	add.n	a2, a9, a2	#,, tmp1446
	add.n	a5, a5, a12	#, tmp1441, pretmp_2376
	call0	silk_LPC_analysis_filter		#
# @OPUS@\upstream\silk\decode_core.c:173:                     inv_gain_Q31 = silk_LSHIFT( silk_SMULWB( inv_gain_Q31, psDecCtrl->LTP_scale_Q14 ), 2 );
	l32i	a10, sp, 160	# %sfp,
	l32i.n	a14, sp, 56	# %sfp,
	l16si	a4, a10, 136	# psDecCtrl_507(D)->LTP_scale_Q14, _92
	extui	a2, a14, 0, 16	# tmp1450,,
	srai	a3, a14, 16	# tmp1453,,
	mull	a2, a2, a4	# tmp1451, tmp1450, _92
	mull	a3, a3, a4	# tmp1454, tmp1453, _92
	srai	a2, a2, 16	# tmp1452, tmp1451,
	add.n	a2, a2, a3	# tmp1455, tmp1452, tmp1454
	slli	a2, a2, 2	#, tmp1455,
	s32i.n	a2, sp, 56	# %sfp,
	j	.L57		#
	.size	silk_decode_core, .-silk_decode_core
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
