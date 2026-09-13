# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/decoder_set_fs.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"decoder_set_fs.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\decoder_set_fs.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\decoder_set_fs.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\decoder_set_fs.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\decoder_set_fs.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\decoder_set_fs.c.s.raw
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
	.section	.text.silk_decoder_set_fs,"ax",@progbits
	.literal_position
	.literal .LC0, silk_pitch_contour_iCDF
	.literal .LC1, silk_pitch_contour_10_ms_iCDF
	.literal .LC2, silk_pitch_contour_NB_iCDF
	.literal .LC3, silk_pitch_contour_10_ms_NB_iCDF
	.literal .LC4, silk_uniform8_iCDF
	.literal .LC5, silk_NLSF_CB_NB_MB
	.literal .LC6, silk_uniform4_iCDF
	.literal .LC7, silk_uniform6_iCDF
	.literal .LC8, silk_NLSF_CB_WB
	.align	4
	.global	silk_decoder_set_fs
	.type	silk_decoder_set_fs, @function
# Function: silk_decoder_set_fs
# Module: upstream/silk/decoder_set_fs.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "main.h"
# C context:
# C context: /* Set decoder sampling rate */
# C context: opus_int silk_decoder_set_fs(
# C context: silk_decoder_state          *psDec,                         /* I/O  Decoder state pointer                       */
# C context: opus_int                    fs_kHz,                         /* I    Sampling frequency (kHz)                    */
# C context: opus_int32                  fs_API_Hz                       /* I    API Sampling frequency (Hz)                 */
# C context: )
silk_decoder_set_fs:
	addi	sp, sp, -48	#,,
	s32i.n	a13, sp, 36	#,
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	slli	a13, a3, 16	# tmp65, fs_kHz,
# @OPUS@\upstream\silk\decoder_set_fs.c:40: {
	s32i.n	a12, sp, 40	#,
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	srai	a13, a13, 16	# _1, tmp65,
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	addmi	a12, a2, 0x400	# tmp141, psDec,
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	slli	a8, a13, 2	# tmp140, _1,
# @OPUS@\upstream\silk\decoder_set_fs.c:48:     frame_length = silk_SMULBB( psDec->nb_subfr, psDec->subfr_length );
	l32i.n	a5, a12, 24	# psDec_33(D)->nb_subfr, psDec_33(D)->nb_subfr
# @OPUS@\upstream\silk\decoder_set_fs.c:40: {
	s32i.n	a15, sp, 28	#,
	mov.n	a15, a2	# psDec, psDec
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	add.n	a2, a8, a13	# tmp68, tmp140, _1
# @OPUS@\upstream\silk\decoder_set_fs.c:48:     frame_length = silk_SMULBB( psDec->nb_subfr, psDec->subfr_length );
	mul16s	a5, a5, a2	#, psDec_33(D)->nb_subfr, tmp68
# @OPUS@\upstream\silk\decoder_set_fs.c:40: {
	s32i.n	a14, sp, 32	#,
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\silk\decoder_set_fs.c:40: {
	mov.n	a14, a3	# fs_kHz, fs_kHz
# @OPUS@\upstream\silk\decoder_set_fs.c:51:     if( psDec->fs_kHz != fs_kHz || psDec->fs_API_hz != fs_API_Hz ) {
	l32i.n	a3, a12, 16	# psDec_33(D)->fs_kHz, psDec_33(D)->fs_kHz
# @OPUS@\upstream\silk\decoder_set_fs.c:47:     psDec->subfr_length = silk_SMULBB( SUB_FRAME_LENGTH_MS, fs_kHz );
	s32i.n	a2, a12, 32	# psDec_33(D)->subfr_length, tmp68
# @OPUS@\upstream\silk\decoder_set_fs.c:48:     frame_length = silk_SMULBB( psDec->nb_subfr, psDec->subfr_length );
	s32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\silk\decoder_set_fs.c:40: {
	mov.n	a7, a4	# fs_API_Hz, fs_API_Hz
# @OPUS@\upstream\silk\decoder_set_fs.c:51:     if( psDec->fs_kHz != fs_kHz || psDec->fs_API_hz != fs_API_Hz ) {
	bne	a3, a14, .L2	# psDec_33(D)->fs_kHz, fs_kHz,
# @OPUS@\upstream\silk\decoder_set_fs.c:51:     if( psDec->fs_kHz != fs_kHz || psDec->fs_API_hz != fs_API_Hz ) {
	l32i.n	a2, a12, 20	# psDec_33(D)->fs_API_hz, psDec_33(D)->fs_API_hz
	beq	a2, a4, .L17	# psDec_33(D)->fs_API_hz, fs_API_Hz,
.L2:
# @OPUS@\upstream\silk\decoder_set_fs.c:53:         ret += silk_resampler_init( &psDec->resampler_state, silk_SMULBB( fs_kHz, 1000 ), fs_API_Hz, 0 );
	slli	a3, a13, 5	# tmp77, _1,
	sub	a3, a3, a13	# tmp78, tmp77, _1
	slli	a3, a3, 2	# tmp79, tmp78,
	add.n	a3, a3, a13	# tmp80, tmp79, _1
	movi	a2, 0x484	# tmp82,
	movi.n	a5, 0	#,
	mov.n	a4, a7	#, fs_API_Hz
	slli	a3, a3, 3	#, tmp80,
	add.n	a2, a15, a2	#, psDec, tmp82
	s32i.n	a7, sp, 4	#,
	s32i.n	a8, sp, 8	#,
	call0	silk_resampler_init		#
# @OPUS@\upstream\silk\decoder_set_fs.c:55:         psDec->fs_API_hz = fs_API_Hz;
	l32i.n	a7, sp, 4	#,
# @OPUS@\upstream\silk\decoder_set_fs.c:53:         ret += silk_resampler_init( &psDec->resampler_state, silk_SMULBB( fs_kHz, 1000 ), fs_API_Hz, 0 );
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\silk\decoder_set_fs.c:58:     if( psDec->fs_kHz != fs_kHz || frame_length != psDec->frame_length ) {
	l32i.n	a2, a12, 16	# psDec_33(D)->fs_kHz, _13
# @OPUS@\upstream\silk\decoder_set_fs.c:55:         psDec->fs_API_hz = fs_API_Hz;
	s32i.n	a7, a12, 20	# psDec_33(D)->fs_API_hz, fs_API_Hz
# @OPUS@\upstream\silk\decoder_set_fs.c:58:     if( psDec->fs_kHz != fs_kHz || frame_length != psDec->frame_length ) {
	l32i.n	a8, sp, 8	#,
	bne	a2, a14, .L4	# _13, fs_kHz,
	j	.L3		#
.L17:
# @OPUS@\upstream\silk\decoder_set_fs.c:41:     opus_int frame_length, ret = 0;
	movi.n	a5, 0	# <retval>,
.L3:
# @OPUS@\upstream\silk\decoder_set_fs.c:58:     if( psDec->fs_kHz != fs_kHz || frame_length != psDec->frame_length ) {
	l32i.n	a2, a12, 28	# psDec_33(D)->frame_length, psDec_33(D)->frame_length
	l32i.n	a3, sp, 0	# %sfp,
	beq	a2, a3, .L1	# psDec_33(D)->frame_length,,
	mov.n	a2, a14	# _13, fs_kHz
.L4:
	l32i.n	a3, a12, 24	# psDec_33(D)->nb_subfr, pretmp_20
# @OPUS@\upstream\silk\decoder_set_fs.c:59:         if( fs_kHz == 8 ) {
	bnei	a14, 8, .L6	# fs_kHz,,
# @OPUS@\upstream\silk\decoder_set_fs.c:61:                 psDec->pitch_contour_iCDF = silk_pitch_contour_NB_iCDF;
	l32r	a4, .LC2	#, cstore_89
# @OPUS@\upstream\silk\decoder_set_fs.c:60:             if( psDec->nb_subfr == MAX_NB_SUBFR ) {
	beqi	a3, 4, .L7	# pretmp_20,,
# @OPUS@\upstream\silk\decoder_set_fs.c:63:                 psDec->pitch_contour_iCDF = silk_pitch_contour_10_ms_NB_iCDF;
	l32r	a4, .LC3	#, cstore_89
	j	.L7		#
.L6:
# @OPUS@\upstream\silk\decoder_set_fs.c:67:                 psDec->pitch_contour_iCDF = silk_pitch_contour_iCDF;
	l32r	a4, .LC0	#, cstore_96
# @OPUS@\upstream\silk\decoder_set_fs.c:66:             if( psDec->nb_subfr == MAX_NB_SUBFR ) {
	beqi	a3, 4, .L8	# pretmp_20,,
# @OPUS@\upstream\silk\decoder_set_fs.c:69:                 psDec->pitch_contour_iCDF = silk_pitch_contour_10_ms_iCDF;
	l32r	a4, .LC1	#, cstore_96
.L8:
	s32i	a4, a12, 84	# psDec_33(D)->pitch_contour_iCDF, cstore_96
# @OPUS@\upstream\silk\decoder_set_fs.c:72:         if( psDec->fs_kHz != fs_kHz ) {
	beq	a14, a2, .L10	# fs_kHz, _13,
# @OPUS@\upstream\silk\decoder_set_fs.c:73:             psDec->ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	add.n	a13, a8, a13	# tmp93, tmp140, _1
	slli	a13, a13, 2	# tmp94, tmp93,
# @OPUS@\upstream\silk\decoder_set_fs.c:73:             psDec->ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	s32i.n	a13, a12, 36	# psDec_33(D)->ltp_mem_length, tmp94
# @OPUS@\upstream\silk\decoder_set_fs.c:74:             if( fs_kHz == 8 || fs_kHz == 12 ) {
	bnei	a14, 12, .L22	# fs_kHz,,
	j	.L11		#
.L16:
# @OPUS@\upstream\silk\decoder_set_fs.c:82:                 psDec->pitch_lag_low_bits_iCDF = silk_uniform8_iCDF;
	l32r	a2, .LC4	#, tmp96
	s32i	a2, a12, 80	# psDec_33(D)->pitch_lag_low_bits_iCDF, tmp96
.L13:
# @OPUS@\upstream\silk\decoder_set_fs.c:91:             psDec->first_frame_after_reset = 1;
	movi.n	a2, 1	# tmp98,
	s32i	a2, a12, 76	# psDec_33(D)->first_frame_after_reset, tmp98
# @OPUS@\upstream\silk\decoder_set_fs.c:92:             psDec->lagPrev                 = 100;
	movi	a2, 0x64	# tmp100,
	s32i.n	a2, a12, 8	# psDec_33(D)->lagPrev, tmp100
# @OPUS@\upstream\silk\decoder_set_fs.c:93:             psDec->LastGainIndex           = 10;
	movi.n	a2, 0xa	# tmp102,
	s8i	a2, a12, 12	# psDec_33(D)->LastGainIndex, tmp102
# @OPUS@\upstream\silk\decoder_set_fs.c:94:             psDec->prevSignalType          = TYPE_NO_VOICE_ACTIVITY;
	movi.n	a13, 0	# tmp104,
	addmi	a2, a15, 0xb00	# tmp103, psDec,
	s32i	a13, a2, 72	# psDec_33(D)->prevSignalType, tmp104
# @OPUS@\upstream\silk\decoder_set_fs.c:95:             silk_memset( psDec->outBuf, 0, sizeof(psDec->outBuf));
	movi	a4, 0x3c0	#,
	mov.n	a3, a13	#, tmp104
	addi	a2, a15, 72	#, psDec,
	s32i.n	a5, sp, 4	#,
	call0	memset		#
# @OPUS@\upstream\silk\decoder_set_fs.c:96:             silk_memset( psDec->sLPC_Q14_buf, 0, sizeof(psDec->sLPC_Q14_buf) );
	movi.n	a4, 0x40	#,
	mov.n	a3, a13	#, tmp104
	addi.n	a2, a15, 8	#, psDec,
	call0	memset		#
	l32i.n	a5, sp, 4	#,
.L10:
# @OPUS@\upstream\silk\decoder_set_fs.c:100:         psDec->frame_length = frame_length;
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\silk\decoder_set_fs.c:99:         psDec->fs_kHz       = fs_kHz;
	s32i.n	a14, a12, 16	# psDec_33(D)->fs_kHz, fs_kHz
# @OPUS@\upstream\silk\decoder_set_fs.c:100:         psDec->frame_length = frame_length;
	s32i.n	a2, a12, 28	# psDec_33(D)->frame_length,
# @OPUS@\upstream\silk\decoder_set_fs.c:106:     return ret;
	j	.L1		#
.L14:
# @OPUS@\upstream\silk\decoder_set_fs.c:73:             psDec->ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	add.n	a13, a8, a13	# tmp121, tmp140, _1
	slli	a13, a13, 2	# tmp122, tmp121,
	l32r	a3, .LC5	#, tmp124
	addmi	a2, a15, 0x500	# tmp123, psDec,
# @OPUS@\upstream\silk\decoder_set_fs.c:73:             psDec->ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	s32i.n	a13, a12, 36	# psDec_33(D)->ltp_mem_length, tmp122
	s32i	a3, a2, 176	# psDec_33(D)->psNLSF_CB, tmp124
	movi.n	a2, 0xa	# tmp126,
	s32i.n	a2, a12, 40	# psDec_33(D)->LPC_order, tmp126
# @OPUS@\upstream\silk\decoder_set_fs.c:86:                 psDec->pitch_lag_low_bits_iCDF = silk_uniform4_iCDF;
	l32r	a2, .LC6	#, tmp128
	s32i	a2, a12, 80	# psDec_33(D)->pitch_lag_low_bits_iCDF, tmp128
	j	.L13		#
.L7:
	s32i	a4, a12, 84	# psDec_33(D)->pitch_contour_iCDF, cstore_89
# @OPUS@\upstream\silk\decoder_set_fs.c:72:         if( psDec->fs_kHz != fs_kHz ) {
	bnei	a2, 8, .L14	# _13,,
	j	.L10		#
.L11:
	l32r	a3, .LC5	#, tmp131
	addmi	a2, a15, 0x500	# tmp130, psDec,
	s32i	a3, a2, 176	# psDec_33(D)->psNLSF_CB, tmp131
	movi.n	a2, 0xa	# tmp133,
	s32i.n	a2, a12, 40	# psDec_33(D)->LPC_order, tmp133
# @OPUS@\upstream\silk\decoder_set_fs.c:84:                 psDec->pitch_lag_low_bits_iCDF = silk_uniform6_iCDF;
	l32r	a2, .LC7	#, tmp135
	s32i	a2, a12, 80	# psDec_33(D)->pitch_lag_low_bits_iCDF, tmp135
	j	.L13		#
.L22:
	l32r	a3, .LC8	#, tmp137
	addmi	a2, a15, 0x500	# tmp136, psDec,
	s32i	a3, a2, 176	# psDec_33(D)->psNLSF_CB, tmp137
	movi.n	a2, 0x10	# tmp139,
	s32i.n	a2, a12, 40	# psDec_33(D)->LPC_order, tmp139
# @OPUS@\upstream\silk\decoder_set_fs.c:81:             if( fs_kHz == 16 ) {
	bne	a14, a2, .L13	# fs_kHz,,
	j	.L16		#
.L1:
# @OPUS@\upstream\silk\decoder_set_fs.c:107: }
	l32i.n	a0, sp, 44	#,
	mov.n	a2, a5	#, <retval>
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	silk_decoder_set_fs, .-silk_decoder_set_fs
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
