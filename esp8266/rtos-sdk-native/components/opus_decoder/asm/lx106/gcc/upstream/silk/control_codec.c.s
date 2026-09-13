# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/control_codec.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"control_codec.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\control_codec.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\control_codec.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\control_codec.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\control_codec.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\control_codec.c.s.raw
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
	.section	.text.silk_setup_resamplers,"ax",@progbits
	.literal_position
	.literal .LC0, 5776
	.literal .LC1, 7184
	.align	4
	.type	silk_setup_resamplers, @function
# Function: silk_setup_resamplers
# Module: upstream/silk/control_codec.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #include "tuning_parameters.h"
# C context: #include "pitch_est_defines.h"
# C context:
# C context: static opus_int silk_setup_resamplers(
# C context: silk_encoder_state_Fxx          *psEnc,             /* I/O                      */
# C context: opus_int                        fs_kHz              /* I                        */
# C context: );
# C context:
silk_setup_resamplers:
	addi	sp, sp, -64	#,,
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a14, sp, 48	#,
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	addmi	a12, a2, 0x1100	# tmp128, psEnc,
# @OPUS@\upstream\silk\control_codec.c:138: {
	s32i.n	a0, sp, 60	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\control_codec.c:138: {
	mov.n	a14, a2	# psEnc, psEnc
	mov.n	a13, a3	# fs_kHz, fs_kHz
# @OPUS@\upstream\silk\control_codec.c:140:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	l32i	a9, a12, 224	# psEnc_30(D)->sCmn.fs_kHz, _1
# @OPUS@\upstream\silk\control_codec.c:140:     SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	bne	a9, a13, .L2	# _1, fs_kHz,
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	l32i	a4, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz, prephitmp_61
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	l32i	a2, a12, 208	# psEnc_30(D)->sCmn.prev_API_fs_Hz, psEnc_30(D)->sCmn.prev_API_fs_Hz
# @OPUS@\upstream\silk\control_codec.c:139:     opus_int   ret = SILK_NO_ERROR;
	movi.n	a15, 0	# <retval>,
# @OPUS@\upstream\silk\control_codec.c:142:     if( psEnc->sCmn.fs_kHz != fs_kHz || psEnc->sCmn.prev_API_fs_Hz != psEnc->sCmn.API_fs_Hz )
	beq	a2, a4, .L3	# psEnc_30(D)->sCmn.prev_API_fs_Hz, prephitmp_61,
.L2:
	l32r	a6, .LC0	#, tmp83
	add.n	a6, a14, a6	# pretmp_60, psEnc, tmp83
# @OPUS@\upstream\silk\control_codec.c:144:         if( psEnc->sCmn.fs_kHz == 0 ) {
	bnez.n	a9, .L4	# _1,
# @OPUS@\upstream\silk\control_codec.c:146:             ret += silk_resampler_init( &psEnc->sCmn.resampler_state, psEnc->sCmn.API_fs_Hz, fs_kHz * 1000, 1 );
	slli	a4, a13, 5	# tmp85, fs_kHz,
	sub	a4, a4, a13	# tmp86, tmp85, fs_kHz
	slli	a4, a4, 2	# tmp87, tmp86,
	add.n	a4, a4, a13	# tmp88, tmp87, fs_kHz
	l32i	a3, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz,
	slli	a4, a4, 3	#, tmp88,
	movi.n	a5, 1	#,
	mov.n	a2, a6	#, pretmp_60
	call0	silk_resampler_init		#
	mov.n	a15, a2	# <retval>,
	l32i	a4, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz, prephitmp_61
	j	.L3		#
.L4:
# @OPUS@\upstream\silk\control_codec.c:160:             buf_length_ms = silk_LSHIFT( psEnc->sCmn.nb_subfr * 5, 1 ) + LA_SHAPE_MS;
	l32i	a2, a12, 228	# psEnc_30(D)->sCmn.nb_subfr, psEnc_30(D)->sCmn.nb_subfr
# @OPUS@\upstream\silk\control_codec.c:151:             opus_int16 *x_bufFIX = psEnc->x_buf;
	l32r	a5, .LC1	#, tmp92
# @OPUS@\upstream\silk\control_codec.c:160:             buf_length_ms = silk_LSHIFT( psEnc->sCmn.nb_subfr * 5, 1 ) + LA_SHAPE_MS;
	slli	a15, a2, 2	# tmp96, psEnc_30(D)->sCmn.nb_subfr,
	add.n	a15, a15, a2	# tmp97, tmp96, psEnc_30(D)->sCmn.nb_subfr
	slli	a15, a15, 1	# tmp98, tmp97,
# @OPUS@\upstream\silk\control_codec.c:160:             buf_length_ms = silk_LSHIFT( psEnc->sCmn.nb_subfr * 5, 1 ) + LA_SHAPE_MS;
	addi.n	a15, a15, 5	# buf_length_ms, tmp98,
# @OPUS@\upstream\silk\control_codec.c:161:             old_buf_samples = buf_length_ms * psEnc->sCmn.fs_kHz;
	mull	a9, a9, a15	# old_buf_samples, _1, buf_length_ms
# @OPUS@\upstream\silk\control_codec.c:171:             ALLOC( temp_resampler_state, 1, silk_resampler_state_struct );
	movi.n	a4, 0	#,
	movi	a3, 0x12c	#,
	movi.n	a2, 1	#,
	s32i.n	a6, sp, 28	#,
	s32i.n	a9, sp, 24	#,
# @OPUS@\upstream\silk\control_codec.c:151:             opus_int16 *x_bufFIX = psEnc->x_buf;
	add.n	a14, a14, a5	# x_bufFIX, psEnc, tmp92
# @OPUS@\upstream\silk\control_codec.c:171:             ALLOC( temp_resampler_state, 1, silk_resampler_state_struct );
	call0	yoradio_opus_scratch_alloc		#
	mov.n	a10, a2	# temp_resampler_state,
# @OPUS@\upstream\silk\control_codec.c:172:             ret += silk_resampler_init( temp_resampler_state, silk_SMULBB( psEnc->sCmn.fs_kHz, 1000 ), psEnc->sCmn.API_fs_Hz, 0 );
	l16si	a2, a12, 224	# psEnc_30(D)->sCmn.fs_kHz, tmp102
	l32i	a4, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz,
	slli	a3, a2, 5	# tmp105, tmp102,
	sub	a3, a3, a2	# tmp106, tmp105, tmp102
	slli	a3, a3, 2	# tmp107, tmp106,
	add.n	a3, a3, a2	# tmp108, tmp107, tmp102
	movi.n	a5, 0	#,
	mov.n	a2, a10	#, temp_resampler_state
	slli	a3, a3, 3	#, tmp108,
	s32i.n	a10, sp, 16	#,
	call0	silk_resampler_init		#
	mov.n	a8, a2	# _40,
# @OPUS@\upstream\silk\control_codec.c:175:             api_buf_samples = buf_length_ms * silk_DIV32_16( psEnc->sCmn.API_fs_Hz, 1000 );
	l32i	a2, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz,
	movi	a3, 0x3e8	#,
	s32i.n	a8, sp, 20	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\control_codec.c:175:             api_buf_samples = buf_length_ms * silk_DIV32_16( psEnc->sCmn.API_fs_Hz, 1000 );
	mull	a15, a2, a15	# api_buf_samples,, buf_length_ms
# @OPUS@\upstream\silk\control_codec.c:178:             ALLOC( x_buf_API_fs_Hz, api_buf_samples, opus_int16 );
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a15	#, api_buf_samples
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\control_codec.c:179:             ret += silk_resampler( temp_resampler_state, x_buf_API_fs_Hz, x_bufFIX, old_buf_samples );
	l32i.n	a10, sp, 16	#,
	l32i.n	a9, sp, 24	#,
# @OPUS@\upstream\silk\control_codec.c:178:             ALLOC( x_buf_API_fs_Hz, api_buf_samples, opus_int16 );
	mov.n	a7, a2	# x_buf_API_fs_Hz,
# @OPUS@\upstream\silk\control_codec.c:179:             ret += silk_resampler( temp_resampler_state, x_buf_API_fs_Hz, x_bufFIX, old_buf_samples );
	mov.n	a5, a9	#, old_buf_samples
	mov.n	a3, a2	#, x_buf_API_fs_Hz
	mov.n	a4, a14	#, x_bufFIX
	mov.n	a2, a10	#, temp_resampler_state
	s32i.n	a7, sp, 16	#,
	call0	silk_resampler		#
# @OPUS@\upstream\silk\control_codec.c:182:             ret += silk_resampler_init( &psEnc->sCmn.resampler_state, psEnc->sCmn.API_fs_Hz, silk_SMULBB( fs_kHz, 1000 ), 1 );
	slli	a4, a13, 16	# tmp117, fs_kHz,
	srai	a4, a4, 16	# tmp116, tmp117,
	slli	a13, a4, 5	# tmp119, tmp116,
	sub	a13, a13, a4	# tmp120, tmp119, tmp116
# @OPUS@\upstream\silk\control_codec.c:179:             ret += silk_resampler( temp_resampler_state, x_buf_API_fs_Hz, x_bufFIX, old_buf_samples );
	l32i.n	a8, sp, 20	#,
# @OPUS@\upstream\silk\control_codec.c:182:             ret += silk_resampler_init( &psEnc->sCmn.resampler_state, psEnc->sCmn.API_fs_Hz, silk_SMULBB( fs_kHz, 1000 ), 1 );
	l32i.n	a6, sp, 28	#,
	slli	a13, a13, 2	# tmp121, tmp120,
	add.n	a4, a13, a4	# tmp122, tmp121, tmp116
	l32i	a3, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz,
# @OPUS@\upstream\silk\control_codec.c:179:             ret += silk_resampler( temp_resampler_state, x_buf_API_fs_Hz, x_bufFIX, old_buf_samples );
	add.n	a13, a8, a2	# ret, _40,
# @OPUS@\upstream\silk\control_codec.c:182:             ret += silk_resampler_init( &psEnc->sCmn.resampler_state, psEnc->sCmn.API_fs_Hz, silk_SMULBB( fs_kHz, 1000 ), 1 );
	movi.n	a5, 1	#,
	slli	a4, a4, 3	#, tmp122,
	mov.n	a2, a6	#, pretmp_60
	call0	silk_resampler_init		#
# @OPUS@\upstream\silk\control_codec.c:185:             ret += silk_resampler( &psEnc->sCmn.resampler_state, x_bufFIX, x_buf_API_fs_Hz, api_buf_samples );
	l32i.n	a7, sp, 16	#,
	l32i.n	a6, sp, 28	#,
# @OPUS@\upstream\silk\control_codec.c:182:             ret += silk_resampler_init( &psEnc->sCmn.resampler_state, psEnc->sCmn.API_fs_Hz, silk_SMULBB( fs_kHz, 1000 ), 1 );
	add.n	a13, a13, a2	# ret, ret,
# @OPUS@\upstream\silk\control_codec.c:185:             ret += silk_resampler( &psEnc->sCmn.resampler_state, x_bufFIX, x_buf_API_fs_Hz, api_buf_samples );
	mov.n	a5, a15	#, api_buf_samples
	mov.n	a4, a7	#, x_buf_API_fs_Hz
	mov.n	a3, a14	#, x_bufFIX
	mov.n	a2, a6	#, pretmp_60
	call0	silk_resampler		#
	l32i	a4, a12, 204	# psEnc_30(D)->sCmn.API_fs_Hz, prephitmp_61
# @OPUS@\upstream\silk\control_codec.c:185:             ret += silk_resampler( &psEnc->sCmn.resampler_state, x_bufFIX, x_buf_API_fs_Hz, api_buf_samples );
	add.n	a15, a13, a2	# <retval>, ret,
.L3:
# @OPUS@\upstream\silk\control_codec.c:195:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\control_codec.c:193:     psEnc->sCmn.prev_API_fs_Hz = psEnc->sCmn.API_fs_Hz;
	s32i	a4, a12, 208	# psEnc_30(D)->sCmn.prev_API_fs_Hz, prephitmp_61
# @OPUS@\upstream\silk\control_codec.c:195:     RESTORE_STACK;
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\control_codec.c:197: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a15	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_setup_resamplers, .-silk_setup_resamplers
	.section	.text.silk_control_encoder,"ax",@progbits
	.literal_position
	.literal .LC2, silk_pitch_contour_10_ms_iCDF
	.literal .LC3, silk_pitch_contour_iCDF
	.literal .LC4, silk_NLSF_CB_NB_MB
	.literal .LC5, silk_NLSF_CB_WB
	.literal .LC6, silk_pitch_contour_10_ms_NB_iCDF
	.literal .LC7, silk_pitch_contour_NB_iCDF
	.literal .LC8, 4352
	.literal .LC9, 4500
	.literal .LC10, 65536
	.literal .LC11, silk_uniform8_iCDF
	.literal .LC12, silk_uniform6_iCDF
	.literal .LC13, silk_uniform4_iCDF
	.literal .LC14, 52429
	.literal .LC15, 49807
	.literal .LC16, 48497
	.literal .LC17, 47186
	.literal .LC18, 45875
	.literal .LC19, -13107
	.align	4
	.global	silk_control_encoder
	.type	silk_control_encoder, @function
# Function: silk_control_encoder
# Module: upstream/silk/control_codec.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context:
# C context: /* Control encoder */
# C context: opus_int silk_control_encoder(
# C context: silk_encoder_state_Fxx          *psEnc,                                 /* I/O  Pointer to Silk encoder state                                               */
# C context: silk_EncControlStruct           *encControl,                            /* I    Control structure                                                           */
# C context: const opus_int                  allow_bw_switch,                        /* I    Flag to allow switching audio bandwidth                                     */
# C context: const opus_int                  channelNb,                              /* I    Channel number                                                              */
silk_control_encoder:
	addi	sp, sp, -64	#,,
	s32i.n	a14, sp, 48	#,
	mov.n	a14, a3	# encControl, encControl
# @OPUS@\upstream\silk\control_codec.c:75:     psEnc->sCmn.useDTX                 = encControl->useDTX;
	l32i.n	a3, a3, 52	# encControl_24(D)->useDTX, encControl_24(D)->useDTX
# @OPUS@\upstream\silk\control_codec.c:72: {
	s32i.n	a12, sp, 56	#,
	s32i.n	a13, sp, 52	#,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\silk\control_codec.c:76:     psEnc->sCmn.useCBR                 = encControl->useCBR;
	l32i.n	a9, a14, 56	# encControl_24(D)->useCBR, encControl_24(D)->useCBR
# @OPUS@\upstream\silk\control_codec.c:72: {
	s32i.n	a0, sp, 60	#,
# @OPUS@\upstream\silk\control_codec.c:72: {
	mov.n	a8, a2	# psEnc, psEnc
# @OPUS@\upstream\silk\control_codec.c:75:     psEnc->sCmn.useDTX                 = encControl->useDTX;
	addmi	a7, a2, 0x1700	# tmp457, psEnc,
# @OPUS@\upstream\silk\control_codec.c:79:     psEnc->sCmn.minInternal_fs_Hz      = encControl->minInternalSampleRate;
	l32i.n	a10, a14, 16	# encControl_24(D)->minInternalSampleRate, encControl_24(D)->minInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:75:     psEnc->sCmn.useDTX                 = encControl->useDTX;
	s32i	a3, a7, 188	# psEnc_25(D)->sCmn.useDTX, encControl_24(D)->useDTX
# @OPUS@\upstream\silk\control_codec.c:77:     psEnc->sCmn.API_fs_Hz              = encControl->API_sampleRate;
	l32i.n	a2, a14, 8	# encControl_24(D)->API_sampleRate, _3
# @OPUS@\upstream\silk\control_codec.c:80:     psEnc->sCmn.desiredInternal_fs_Hz  = encControl->desiredInternalSampleRate;
	l32i.n	a3, a14, 20	# encControl_24(D)->desiredInternalSampleRate, encControl_24(D)->desiredInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:78:     psEnc->sCmn.maxInternal_fs_Hz      = encControl->maxInternalSampleRate;
	l32i.n	a11, a14, 12	# encControl_24(D)->maxInternalSampleRate, encControl_24(D)->maxInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:76:     psEnc->sCmn.useCBR                 = encControl->useCBR;
	addmi	a12, a8, 0x1200	# tmp454, psEnc,
	s32i	a9, a12, 68	# psEnc_25(D)->sCmn.useCBR, encControl_24(D)->useCBR
# @OPUS@\upstream\silk\control_codec.c:77:     psEnc->sCmn.API_fs_Hz              = encControl->API_sampleRate;
	addmi	a13, a8, 0x1100	# tmp456, psEnc,
# @OPUS@\upstream\silk\control_codec.c:81:     psEnc->sCmn.useInBandFEC           = encControl->useInBandFEC;
	l32i.n	a9, a14, 40	# encControl_24(D)->useInBandFEC, encControl_24(D)->useInBandFEC
# @OPUS@\upstream\silk\control_codec.c:79:     psEnc->sCmn.minInternal_fs_Hz      = encControl->minInternalSampleRate;
	s32i	a10, a13, 216	# psEnc_25(D)->sCmn.minInternal_fs_Hz, encControl_24(D)->minInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:80:     psEnc->sCmn.desiredInternal_fs_Hz  = encControl->desiredInternalSampleRate;
	s32i	a3, a13, 220	# psEnc_25(D)->sCmn.desiredInternal_fs_Hz, encControl_24(D)->desiredInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:82:     psEnc->sCmn.nChannelsAPI           = encControl->nChannelsAPI;
	l32i.n	a10, a14, 0	# encControl_24(D)->nChannelsAPI, encControl_24(D)->nChannelsAPI
# @OPUS@\upstream\silk\control_codec.c:83:     psEnc->sCmn.nChannelsInternal      = encControl->nChannelsInternal;
	l32i.n	a3, a14, 4	# encControl_24(D)->nChannelsInternal, encControl_24(D)->nChannelsInternal
# @OPUS@\upstream\silk\control_codec.c:77:     psEnc->sCmn.API_fs_Hz              = encControl->API_sampleRate;
	s32i	a2, a13, 204	# psEnc_25(D)->sCmn.API_fs_Hz, _3
# @OPUS@\upstream\silk\control_codec.c:78:     psEnc->sCmn.maxInternal_fs_Hz      = encControl->maxInternalSampleRate;
	s32i	a11, a13, 212	# psEnc_25(D)->sCmn.maxInternal_fs_Hz, encControl_24(D)->maxInternalSampleRate
# @OPUS@\upstream\silk\control_codec.c:81:     psEnc->sCmn.useInBandFEC           = encControl->useInBandFEC;
	s32i	a9, a7, 200	# psEnc_25(D)->sCmn.useInBandFEC, encControl_24(D)->useInBandFEC
# @OPUS@\upstream\silk\control_codec.c:82:     psEnc->sCmn.nChannelsAPI           = encControl->nChannelsAPI;
	addmi	a9, a8, 0x1600	# tmp455, psEnc,
# @OPUS@\upstream\silk\control_codec.c:83:     psEnc->sCmn.nChannelsInternal      = encControl->nChannelsInternal;
	s32i	a3, a9, 124	# psEnc_25(D)->sCmn.nChannelsInternal, encControl_24(D)->nChannelsInternal
# @OPUS@\upstream\silk\control_codec.c:82:     psEnc->sCmn.nChannelsAPI           = encControl->nChannelsAPI;
	s32i	a10, a9, 120	# psEnc_25(D)->sCmn.nChannelsAPI, encControl_24(D)->nChannelsAPI
# @OPUS@\upstream\silk\control_codec.c:84:     psEnc->sCmn.allow_bandwidth_switch = allow_bw_switch;
	s32i	a4, a13, 184	# psEnc_25(D)->sCmn.allow_bandwidth_switch, allow_bw_switch
# @OPUS@\upstream\silk\control_codec.c:87:     if( psEnc->sCmn.controlled_since_last_payload != 0 && psEnc->sCmn.prefillFlag == 0 ) {
	l32i.n	a3, a12, 60	# psEnc_25(D)->sCmn.controlled_since_last_payload, psEnc_25(D)->sCmn.controlled_since_last_payload
# @OPUS@\upstream\silk\control_codec.c:85:     psEnc->sCmn.channelNb              = channelNb;
	s32i	a5, a9, 128	# psEnc_25(D)->sCmn.channelNb, channelNb
# @OPUS@\upstream\silk\control_codec.c:72: {
	mov.n	a15, a6	# force_fs_kHz, force_fs_kHz
# @OPUS@\upstream\silk\control_codec.c:87:     if( psEnc->sCmn.controlled_since_last_payload != 0 && psEnc->sCmn.prefillFlag == 0 ) {
	beqz.n	a3, .L8	# psEnc_25(D)->sCmn.controlled_since_last_payload,
# @OPUS@\upstream\silk\control_codec.c:87:     if( psEnc->sCmn.controlled_since_last_payload != 0 && psEnc->sCmn.prefillFlag == 0 ) {
	l32i	a5, a12, 72	# psEnc_25(D)->sCmn.prefillFlag, <retval>
# @OPUS@\upstream\silk\control_codec.c:87:     if( psEnc->sCmn.controlled_since_last_payload != 0 && psEnc->sCmn.prefillFlag == 0 ) {
	bnez.n	a5, .L8	# <retval>,
# @OPUS@\upstream\silk\control_codec.c:88:         if( psEnc->sCmn.API_fs_Hz != psEnc->sCmn.prev_API_fs_Hz && psEnc->sCmn.fs_kHz > 0 ) {
	l32i	a3, a13, 208	# psEnc_25(D)->sCmn.prev_API_fs_Hz, psEnc_25(D)->sCmn.prev_API_fs_Hz
	beq	a2, a3, .L7	# _3, psEnc_25(D)->sCmn.prev_API_fs_Hz,
# @OPUS@\upstream\silk\control_codec.c:88:         if( psEnc->sCmn.API_fs_Hz != psEnc->sCmn.prev_API_fs_Hz && psEnc->sCmn.fs_kHz > 0 ) {
	l32i	a3, a13, 224	# psEnc_25(D)->sCmn.fs_kHz, _13
# @OPUS@\upstream\silk\control_codec.c:88:         if( psEnc->sCmn.API_fs_Hz != psEnc->sCmn.prev_API_fs_Hz && psEnc->sCmn.fs_kHz > 0 ) {
	blti	a3, 1, .L7	# _13,,
# @OPUS@\upstream\silk\control_codec.c:90:             ret += silk_setup_resamplers( psEnc, psEnc->sCmn.fs_kHz );
	mov.n	a2, a8	#, psEnc
	call0	silk_setup_resamplers		#
	mov.n	a5, a2	# <retval>,
	j	.L7		#
.L8:
# @OPUS@\upstream\silk\control_codec.c:100:     fs_kHz = silk_control_audio_bandwidth( &psEnc->sCmn, encControl );
	mov.n	a3, a14	#, encControl
	mov.n	a2, a8	#, psEnc
	s32i.n	a7, sp, 20	#,
	s32i.n	a9, sp, 16	#,
	s32i.n	a8, sp, 12	#,
	call0	silk_control_audio_bandwidth		#
# @OPUS@\upstream\silk\control_codec.c:107:     ret += silk_setup_resamplers( psEnc, fs_kHz );
	l32i.n	a8, sp, 12	#,
# @OPUS@\upstream\silk\control_codec.c:101:     if( force_fs_kHz ) {
	moveqz	a15, a2, a15	# fs_kHz,, force_fs_kHz
# @OPUS@\upstream\silk\control_codec.c:107:     ret += silk_setup_resamplers( psEnc, fs_kHz );
	mov.n	a3, a15	#, fs_kHz
	mov.n	a2, a8	#, psEnc
	call0	silk_setup_resamplers		#
	mov.n	a5, a2	# <retval>,
# @OPUS@\upstream\silk\control_codec.c:112:     ret += silk_setup_fs( psEnc, fs_kHz, encControl->payloadSize_ms );
	l32i.n	a4, a14, 24	# encControl_24(D)->payloadSize_ms, _15
# @OPUS@\upstream\silk\control_codec.c:208:     if( PacketSize_ms != psEnc->sCmn.PacketSize_ms ) {
	l32i.n	a2, a12, 4	# psEnc_25(D)->sCmn.PacketSize_ms, psEnc_25(D)->sCmn.PacketSize_ms
	l32i.n	a7, sp, 20	#,
	l32i.n	a8, sp, 12	#,
	l32i.n	a9, sp, 16	#,
	bne	a4, a2, .L11	# _15, psEnc_25(D)->sCmn.PacketSize_ms,
	l32i	a6, a13, 224	# psEnc_25(D)->sCmn.fs_kHz, prephitmp_46
	j	.L12		#
.L11:
# @OPUS@\upstream\silk\control_codec.c:209:         if( ( PacketSize_ms !=  10 ) &&
	beqi	a4, 10, .L13	# _15,,
# @OPUS@\upstream\silk\control_codec.c:210:             ( PacketSize_ms !=  20 ) &&
	addi	a2, a4, -20	# tmp153, _15,
# @OPUS@\upstream\silk\control_codec.c:209:         if( ( PacketSize_ms !=  10 ) &&
	beqz.n	a2, .L13	# tmp153,
# @OPUS@\upstream\silk\control_codec.c:211:             ( PacketSize_ms !=  40 ) &&
	addi	a2, a4, -40	# tmp159, _15,
# @OPUS@\upstream\silk\control_codec.c:211:             ( PacketSize_ms !=  40 ) &&
	beqz.n	a2, .L14	# tmp159,
# @OPUS@\upstream\silk\control_codec.c:212:             ( PacketSize_ms !=  60 ) ) {
	addi	a2, a4, -60	# tmp165, _15,
	addi	a3, a5, -103	# tmp458, <retval>,
	movnez	a5, a3, a2	# <retval>, tmp458, tmp165
	j	.L14		#
.L13:
# @OPUS@\upstream\silk\control_codec.c:215:         if( PacketSize_ms <= 10 ) {
	movi.n	a2, 0xa	# tmp169,
	blt	a2, a4, .L15	# tmp169, _15,
# @OPUS@\upstream\silk\control_codec.c:216:             psEnc->sCmn.nFramesPerPacket = 1;
	movi.n	a2, 1	# tmp171,
# @OPUS@\upstream\silk\control_codec.c:217:             psEnc->sCmn.nb_subfr = PacketSize_ms == 10 ? 2 : 1;
	addi	a3, a4, -10	# tmp472, _15,
	movi.n	a6, 2	# tmp470,
# @OPUS@\upstream\silk\control_codec.c:216:             psEnc->sCmn.nFramesPerPacket = 1;
	s32i	a2, a9, 112	# psEnc_25(D)->sCmn.nFramesPerPacket, tmp171
# @OPUS@\upstream\silk\control_codec.c:217:             psEnc->sCmn.nb_subfr = PacketSize_ms == 10 ? 2 : 1;
	moveqz	a2, a6, a3	# tmp171, tmp470, tmp472
	mov.n	a3, a2	# iftmp$1_100, tmp171
.L16:
# @OPUS@\upstream\silk\control_codec.c:218:             psEnc->sCmn.frame_length = silk_SMULBB( PacketSize_ms, fs_kHz );
	slli	a2, a15, 16	# tmp173, fs_kHz,
	srai	a6, a2, 16	# _103, tmp173,
# @OPUS@\upstream\silk\control_codec.c:219:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS_2_SF, fs_kHz );
	slli	a2, a6, 3	# tmp178, _103,
# @OPUS@\upstream\silk\control_codec.c:218:             psEnc->sCmn.frame_length = silk_SMULBB( PacketSize_ms, fs_kHz );
	mul16s	a10, a4, a6	# tmp175, _15, _103
# @OPUS@\upstream\silk\control_codec.c:219:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS_2_SF, fs_kHz );
	sub	a2, a2, a6	# tmp179, tmp178, _103
	slli	a2, a2, 1	# tmp180, tmp179,
# @OPUS@\upstream\silk\control_codec.c:220:             if( psEnc->sCmn.fs_kHz == 8 ) {
	l32i	a6, a13, 224	# psEnc_25(D)->sCmn.fs_kHz, prephitmp_46
# @OPUS@\upstream\silk\control_codec.c:217:             psEnc->sCmn.nb_subfr = PacketSize_ms == 10 ? 2 : 1;
	s32i	a3, a13, 228	# psEnc_25(D)->sCmn.nb_subfr, iftmp$1_100
# @OPUS@\upstream\silk\control_codec.c:218:             psEnc->sCmn.frame_length = silk_SMULBB( PacketSize_ms, fs_kHz );
	s32i	a10, a13, 232	# psEnc_25(D)->sCmn.frame_length, tmp175
# @OPUS@\upstream\silk\control_codec.c:219:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS_2_SF, fs_kHz );
	s32i	a2, a13, 196	# psEnc_25(D)->sCmn.pitch_LPC_win_length, tmp180
# @OPUS@\upstream\silk\control_codec.c:220:             if( psEnc->sCmn.fs_kHz == 8 ) {
	bnei	a6, 8, .L17	# prephitmp_46,,
# @OPUS@\upstream\silk\control_codec.c:221:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_10_ms_NB_iCDF;
	l32r	a2, .LC6	#, tmp183
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, tmp183
	j	.L18		#
.L17:
# @OPUS@\upstream\silk\control_codec.c:223:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_10_ms_iCDF;
	l32r	a2, .LC2	#, tmp185
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, tmp185
	j	.L18		#
.L15:
# @OPUS@\upstream\silk\control_codec.c:226:             psEnc->sCmn.nFramesPerPacket = silk_DIV32_16( PacketSize_ms, MAX_FRAME_LENGTH_MS );
	movi.n	a3, 0x14	#,
	mov.n	a2, a4	#, _15
	s32i.n	a4, sp, 4	#,
	s32i.n	a5, sp, 8	#,
	s32i.n	a7, sp, 20	#,
	s32i.n	a8, sp, 12	#,
	s32i.n	a9, sp, 16	#,
	call0	__divsi3		#
# @OPUS@\upstream\silk\control_codec.c:228:             psEnc->sCmn.frame_length = silk_SMULBB( 20, fs_kHz );
	slli	a3, a15, 16	# tmp192, fs_kHz,
	srai	a3, a3, 16	# _109, tmp192,
# @OPUS@\upstream\silk\control_codec.c:226:             psEnc->sCmn.nFramesPerPacket = silk_DIV32_16( PacketSize_ms, MAX_FRAME_LENGTH_MS );
	l32i.n	a9, sp, 16	#,
# @OPUS@\upstream\silk\control_codec.c:228:             psEnc->sCmn.frame_length = silk_SMULBB( 20, fs_kHz );
	slli	a10, a3, 2	# tmp195, _109,
# @OPUS@\upstream\silk\control_codec.c:229:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS, fs_kHz );
	slli	a6, a3, 1	# tmp200, _109,
# @OPUS@\upstream\silk\control_codec.c:228:             psEnc->sCmn.frame_length = silk_SMULBB( 20, fs_kHz );
	add.n	a10, a10, a3	# tmp196, tmp195, _109
# @OPUS@\upstream\silk\control_codec.c:229:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS, fs_kHz );
	add.n	a3, a6, a3	# tmp201, tmp200, _109
# @OPUS@\upstream\silk\control_codec.c:226:             psEnc->sCmn.nFramesPerPacket = silk_DIV32_16( PacketSize_ms, MAX_FRAME_LENGTH_MS );
	s32i	a2, a9, 112	# psEnc_25(D)->sCmn.nFramesPerPacket,
# @OPUS@\upstream\silk\control_codec.c:228:             psEnc->sCmn.frame_length = silk_SMULBB( 20, fs_kHz );
	slli	a10, a10, 2	# tmp197, tmp196,
# @OPUS@\upstream\silk\control_codec.c:229:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS, fs_kHz );
	slli	a3, a3, 3	# tmp202, tmp201,
# @OPUS@\upstream\silk\control_codec.c:227:             psEnc->sCmn.nb_subfr = MAX_NB_SUBFR;
	movi.n	a2, 4	# tmp191,
# @OPUS@\upstream\silk\control_codec.c:230:             if( psEnc->sCmn.fs_kHz == 8 ) {
	l32i	a6, a13, 224	# psEnc_25(D)->sCmn.fs_kHz, prephitmp_46
# @OPUS@\upstream\silk\control_codec.c:227:             psEnc->sCmn.nb_subfr = MAX_NB_SUBFR;
	s32i	a2, a13, 228	# psEnc_25(D)->sCmn.nb_subfr, tmp191
# @OPUS@\upstream\silk\control_codec.c:228:             psEnc->sCmn.frame_length = silk_SMULBB( 20, fs_kHz );
	s32i	a10, a13, 232	# psEnc_25(D)->sCmn.frame_length, tmp197
# @OPUS@\upstream\silk\control_codec.c:229:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS, fs_kHz );
	s32i	a3, a13, 196	# psEnc_25(D)->sCmn.pitch_LPC_win_length, tmp202
# @OPUS@\upstream\silk\control_codec.c:230:             if( psEnc->sCmn.fs_kHz == 8 ) {
	l32i.n	a4, sp, 4	#,
	l32i.n	a5, sp, 8	#,
	l32i.n	a7, sp, 20	#,
	l32i.n	a8, sp, 12	#,
	bnei	a6, 8, .L19	# prephitmp_46,,
# @OPUS@\upstream\silk\control_codec.c:231:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_NB_iCDF;
	l32r	a2, .LC7	#, tmp205
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, tmp205
	j	.L18		#
.L19:
# @OPUS@\upstream\silk\control_codec.c:233:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_iCDF;
	l32r	a2, .LC3	#, tmp207
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, tmp207
.L18:
# @OPUS@\upstream\silk\control_codec.c:237:         psEnc->sCmn.TargetRate_bps = 0;         /* trigger new SNR computation */
	movi.n	a2, 0	# tmp210,
# @OPUS@\upstream\silk\control_codec.c:236:         psEnc->sCmn.PacketSize_ms  = PacketSize_ms;
	s32i.n	a4, a12, 4	# psEnc_25(D)->sCmn.PacketSize_ms, _15
# @OPUS@\upstream\silk\control_codec.c:237:         psEnc->sCmn.TargetRate_bps = 0;         /* trigger new SNR computation */
	s32i.n	a2, a12, 0	# psEnc_25(D)->sCmn.TargetRate_bps, tmp210
.L12:
# @OPUS@\upstream\silk\control_codec.c:243:     if( psEnc->sCmn.fs_kHz != fs_kHz ) {
	bne	a15, a6, .L20	# fs_kHz, prephitmp_46,
	slli	a2, a6, 2	# tmp212, prephitmp_46,
	add.n	a2, a2, a6	# prephitmp_266, tmp212, prephitmp_46
	j	.L21		#
.L20:
# @OPUS@\upstream\silk\control_codec.c:245:         silk_memset( &psEnc->sShape,               0, sizeof( psEnc->sShape ) );
	addmi	a6, a8, 0x1c00	# tmp214, psEnc,
	movi.n	a4, 0x10	#,
	movi.n	a3, 0	#,
	mov.n	a2, a6	#, tmp214
	s32i.n	a5, sp, 8	#,
	s32i.n	a7, sp, 20	#,
	s32i.n	a9, sp, 16	#,
	s32i.n	a8, sp, 12	#,
	call0	memset		#
# @OPUS@\upstream\silk\control_codec.c:246:         silk_memset( &psEnc->sCmn.sNSQ,            0, sizeof( psEnc->sCmn.sNSQ ) );
	l32i.n	a8, sp, 12	#,
# @OPUS@\upstream\silk\control_codec.c:245:         silk_memset( &psEnc->sShape,               0, sizeof( psEnc->sShape ) );
	mov.n	a6, a2	# tmp214,
# @OPUS@\upstream\silk\control_codec.c:246:         silk_memset( &psEnc->sCmn.sNSQ,            0, sizeof( psEnc->sCmn.sNSQ ) );
	l32r	a4, .LC8	#,
	movi	a2, 0x94	# tmp219,
	movi.n	a3, 0	#,
	add.n	a2, a8, a2	#, psEnc, tmp219
	s32i.n	a6, sp, 4	#,
	call0	memset		#
# @OPUS@\upstream\silk\control_codec.c:247:         silk_memset( psEnc->sCmn.prev_NLSFq_Q15,   0, sizeof( psEnc->sCmn.prev_NLSFq_Q15 ) );
	l32i.n	a8, sp, 12	#,
	l32r	a2, .LC9	#, tmp226
	movi.n	a4, 0x20	#,
	movi.n	a3, 0	#,
	add.n	a2, a8, a2	#, psEnc, tmp226
	call0	memset		#
# @OPUS@\upstream\silk\control_codec.c:248:         silk_memset( &psEnc->sCmn.sLP.In_LP_State, 0, sizeof( psEnc->sCmn.sLP.In_LP_State ) );
	l32i.n	a8, sp, 12	#,
	movi.n	a2, 0	# tmp233,
	s8i	a2, a8, 16	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 17	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 18	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 19	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 20	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 21	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 22	# MEM[(void *)psEnc_25(D) + 16B], tmp233
	s8i	a2, a8, 23	# MEM[(void *)psEnc_25(D) + 16B], tmp233
# @OPUS@\upstream\silk\control_codec.c:249:         psEnc->sCmn.inputBufIx                  = 0;
	l32i.n	a9, sp, 16	#,
	movi.n	a2, 0	# tmp242,
	s32i	a2, a9, 108	# psEnc_25(D)->sCmn.inputBufIx, tmp242
# @OPUS@\upstream\silk\control_codec.c:250:         psEnc->sCmn.nFramesEncoded              = 0;
	s32i	a2, a9, 116	# psEnc_25(D)->sCmn.nFramesEncoded, tmp242
# @OPUS@\upstream\silk\control_codec.c:251:         psEnc->sCmn.TargetRate_bps              = 0;     /* trigger new SNR computation */
	s32i.n	a2, a12, 0	# psEnc_25(D)->sCmn.TargetRate_bps, tmp242
# @OPUS@\upstream\silk\control_codec.c:254:         psEnc->sCmn.prevLag                     = 100;
	movi	a3, 0x64	# tmp248,
# @OPUS@\upstream\silk\control_codec.c:256:         psEnc->sShape.LastGainIndex             = 10;
	l32i.n	a6, sp, 4	#,
# @OPUS@\upstream\silk\control_codec.c:254:         psEnc->sCmn.prevLag                     = 100;
	s32i	a3, a13, 192	# psEnc_25(D)->sCmn.prevLag, tmp248
# @OPUS@\upstream\silk\control_codec.c:255:         psEnc->sCmn.first_frame_after_reset     = 1;
	movi.n	a4, 1	# tmp250,
	s32i.n	a4, a12, 56	# psEnc_25(D)->sCmn.first_frame_after_reset, tmp250
# @OPUS@\upstream\silk\control_codec.c:256:         psEnc->sShape.LastGainIndex             = 10;
	movi.n	a4, 0xa	# tmp252,
	s8i	a4, a6, 0	# psEnc_25(D)->sShape.LastGainIndex, tmp252
# @OPUS@\upstream\silk\control_codec.c:257:         psEnc->sCmn.sNSQ.lagPrev                = 100;
	s32i	a3, a13, 124	# psEnc_25(D)->sCmn.sNSQ.lagPrev, tmp248
# @OPUS@\upstream\silk\control_codec.c:258:         psEnc->sCmn.sNSQ.prev_gain_Q16          = 65536;
	l32r	a3, .LC10	#, tmp256
# @OPUS@\upstream\silk\control_codec.c:259:         psEnc->sCmn.prevSignalType              = TYPE_NO_VOICE_ACTIVITY;
	s8i	a2, a13, 189	# psEnc_25(D)->sCmn.prevSignalType, tmp242
# @OPUS@\upstream\silk\control_codec.c:258:         psEnc->sCmn.sNSQ.prev_gain_Q16          = 65536;
	s32i	a3, a13, 140	# psEnc_25(D)->sCmn.sNSQ.prev_gain_Q16, tmp256
# @OPUS@\upstream\silk\control_codec.c:261:         psEnc->sCmn.fs_kHz = fs_kHz;
	s32i	a15, a13, 224	# psEnc_25(D)->sCmn.fs_kHz, fs_kHz
	l32i	a8, a13, 228	# psEnc_25(D)->sCmn.nb_subfr, pretmp_289
# @OPUS@\upstream\silk\control_codec.c:262:         if( psEnc->sCmn.fs_kHz == 8 ) {
	l32i.n	a5, sp, 8	#,
	l32i.n	a7, sp, 20	#,
	bnei	a15, 8, .L22	# fs_kHz,,
# @OPUS@\upstream\silk\control_codec.c:264:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_NB_iCDF;
	l32r	a2, .LC7	#, cstore_305
# @OPUS@\upstream\silk\control_codec.c:263:             if( psEnc->sCmn.nb_subfr == MAX_NB_SUBFR ) {
	beqi	a8, 4, .L24	# pretmp_289,,
# @OPUS@\upstream\silk\control_codec.c:266:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_10_ms_NB_iCDF;
	l32r	a2, .LC6	#, cstore_305
	j	.L24		#
.L22:
# @OPUS@\upstream\silk\control_codec.c:272:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_10_ms_iCDF;
	l32r	a2, .LC2	#, cstore_306
# @OPUS@\upstream\silk\control_codec.c:269:             if( psEnc->sCmn.nb_subfr == MAX_NB_SUBFR ) {
	bnei	a8, 4, .L25	# pretmp_289,,
# @OPUS@\upstream\silk\control_codec.c:270:                 psEnc->sCmn.pitch_contour_iCDF = silk_pitch_contour_iCDF;
	l32r	a2, .LC3	#, cstore_306
.L25:
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, cstore_306
# @OPUS@\upstream\silk\control_codec.c:275:         if( psEnc->sCmn.fs_kHz == 8 || psEnc->sCmn.fs_kHz == 12 ) {
	beqi	a15, 12, .L45	# fs_kHz,,
# @OPUS@\upstream\silk\control_codec.c:279:             psEnc->sCmn.predictLPCOrder = MAX_LPC_ORDER;
	movi.n	a2, 0x10	#,
# @OPUS@\upstream\silk\control_codec.c:280:             psEnc->sCmn.psNLSF_CB  = &silk_NLSF_CB_WB;
	l32r	a11, .LC5	#, cstore_313
# @OPUS@\upstream\silk\control_codec.c:279:             psEnc->sCmn.predictLPCOrder = MAX_LPC_ORDER;
	s32i.n	a2, sp, 0	# %sfp,
	j	.L26		#
.L45:
# @OPUS@\upstream\silk\control_codec.c:276:             psEnc->sCmn.predictLPCOrder = MIN_LPC_ORDER;
	movi.n	a2, 0xa	#,
# @OPUS@\upstream\silk\control_codec.c:277:             psEnc->sCmn.psNLSF_CB  = &silk_NLSF_CB_NB_MB;
	l32r	a11, .LC4	#, cstore_313
# @OPUS@\upstream\silk\control_codec.c:276:             psEnc->sCmn.predictLPCOrder = MIN_LPC_ORDER;
	s32i.n	a2, sp, 0	# %sfp,
.L26:
# @OPUS@\upstream\silk\control_codec.c:284:         psEnc->sCmn.ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	slli	a3, a15, 16	# tmp270, fs_kHz,
	srai	a3, a3, 16	# _131, tmp270,
# @OPUS@\upstream\silk\control_codec.c:282:         psEnc->sCmn.subfr_length   = SUB_FRAME_LENGTH_MS * fs_kHz;
	slli	a2, a15, 2	# tmp265, fs_kHz,
	s32i	a11, a12, 84	# psEnc_25(D)->sCmn.psNLSF_CB, cstore_313
	add.n	a2, a2, a15	# prephitmp_266, tmp265, fs_kHz
# @OPUS@\upstream\silk\control_codec.c:286:         psEnc->sCmn.max_pitch_lag  = silk_SMULBB( 18, fs_kHz );
	slli	a4, a3, 3	# tmp280, _131,
	l32i.n	a11, sp, 0	# %sfp,
# @OPUS@\upstream\silk\control_codec.c:284:         psEnc->sCmn.ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	slli	a6, a3, 2	# tmp273, _131,
# @OPUS@\upstream\silk\control_codec.c:286:         psEnc->sCmn.max_pitch_lag  = silk_SMULBB( 18, fs_kHz );
	add.n	a9, a4, a3	# tmp281, tmp280, _131
# @OPUS@\upstream\silk\control_codec.c:283:         psEnc->sCmn.frame_length   = silk_SMULBB( psEnc->sCmn.subfr_length, psEnc->sCmn.nb_subfr );
	mul16s	a10, a2, a8	# tmp269, prephitmp_266, pretmp_289
# @OPUS@\upstream\silk\control_codec.c:284:         psEnc->sCmn.ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	add.n	a6, a6, a3	# tmp274, tmp273, _131
	s32i.n	a11, a12, 32	# psEnc_25(D)->sCmn.predictLPCOrder,
	slli	a6, a6, 2	# tmp275, tmp274,
# @OPUS@\upstream\silk\control_codec.c:285:         psEnc->sCmn.la_pitch       = silk_SMULBB( LA_PITCH_MS, fs_kHz );
	slli	a11, a3, 1	# tmp277, _131,
# @OPUS@\upstream\silk\control_codec.c:286:         psEnc->sCmn.max_pitch_lag  = silk_SMULBB( 18, fs_kHz );
	slli	a9, a9, 1	# tmp282, tmp281,
# @OPUS@\upstream\silk\control_codec.c:290:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS_2_SF, fs_kHz );
	sub	a4, a4, a3	# tmp289, tmp280, _131
# @OPUS@\upstream\silk\control_codec.c:282:         psEnc->sCmn.subfr_length   = SUB_FRAME_LENGTH_MS * fs_kHz;
	s32i	a2, a13, 236	# psEnc_25(D)->sCmn.subfr_length, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:283:         psEnc->sCmn.frame_length   = silk_SMULBB( psEnc->sCmn.subfr_length, psEnc->sCmn.nb_subfr );
	s32i	a10, a13, 232	# psEnc_25(D)->sCmn.frame_length, tmp269
# @OPUS@\upstream\silk\control_codec.c:284:         psEnc->sCmn.ltp_mem_length = silk_SMULBB( LTP_MEM_LENGTH_MS, fs_kHz );
	s32i	a6, a13, 240	# psEnc_25(D)->sCmn.ltp_mem_length, tmp275
# @OPUS@\upstream\silk\control_codec.c:285:         psEnc->sCmn.la_pitch       = silk_SMULBB( LA_PITCH_MS, fs_kHz );
	s32i	a11, a13, 244	# psEnc_25(D)->sCmn.la_pitch, tmp277
# @OPUS@\upstream\silk\control_codec.c:286:         psEnc->sCmn.max_pitch_lag  = silk_SMULBB( 18, fs_kHz );
	s32i	a9, a13, 200	# psEnc_25(D)->sCmn.max_pitch_lag, tmp282
# @OPUS@\upstream\silk\control_codec.c:290:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS_2_SF, fs_kHz );
	slli	a4, a4, 1	# _137, tmp289,
# @OPUS@\upstream\silk\control_codec.c:287:         if( psEnc->sCmn.nb_subfr == MAX_NB_SUBFR ) {
	bnei	a8, 4, .L28	# pretmp_289,,
# @OPUS@\upstream\silk\control_codec.c:288:             psEnc->sCmn.pitch_LPC_win_length = silk_SMULBB( FIND_PITCH_LPC_WIN_MS, fs_kHz );
	add.n	a4, a11, a3	# tmp285, tmp277, _131
	slli	a4, a4, 3	# _137, tmp285,
.L28:
	s32i	a4, a13, 196	# psEnc_25(D)->sCmn.pitch_LPC_win_length, _137
# @OPUS@\upstream\silk\control_codec.c:293:             psEnc->sCmn.pitch_lag_low_bits_iCDF = silk_uniform8_iCDF;
	mov.n	a6, a15	# prephitmp_46, fs_kHz
# @OPUS@\upstream\silk\control_codec.c:292:         if( psEnc->sCmn.fs_kHz == 16 ) {
	bnei	a15, 16, .L29	# fs_kHz,,
# @OPUS@\upstream\silk\control_codec.c:293:             psEnc->sCmn.pitch_lag_low_bits_iCDF = silk_uniform8_iCDF;
	l32r	a2, .LC11	#, tmp293
	s32i	a2, a12, 76	# psEnc_25(D)->sCmn.pitch_lag_low_bits_iCDF, tmp293
	movi.n	a2, 0x50	# prephitmp_266,
	j	.L21		#
.L29:
# @OPUS@\upstream\silk\control_codec.c:294:         } else if( psEnc->sCmn.fs_kHz == 12 ) {
	bnei	a15, 12, .L30	# fs_kHz,,
# @OPUS@\upstream\silk\control_codec.c:295:             psEnc->sCmn.pitch_lag_low_bits_iCDF = silk_uniform6_iCDF;
	l32r	a2, .LC12	#, tmp295
	s32i	a2, a12, 76	# psEnc_25(D)->sCmn.pitch_lag_low_bits_iCDF, tmp295
	movi.n	a2, 0x3c	# prephitmp_266,
	j	.L21		#
.L30:
# @OPUS@\upstream\silk\control_codec.c:297:             psEnc->sCmn.pitch_lag_low_bits_iCDF = silk_uniform4_iCDF;
	l32r	a3, .LC13	#, tmp297
	s32i	a3, a12, 76	# psEnc_25(D)->sCmn.pitch_lag_low_bits_iCDF, tmp297
.L21:
# @OPUS@\upstream\silk\control_codec.c:117:     ret += silk_setup_complexity( &psEnc->sCmn, encControl->complexity  );
	l32i.n	a4, a14, 36	# encControl_24(D)->complexity, _16
# @OPUS@\upstream\silk\control_codec.c:316:     if( Complexity < 1 ) {
	bgei	a4, 1, .L31	# _16,,
# @OPUS@\upstream\silk\control_codec.c:318:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.8, 16 );
	l32r	a9, .LC14	#, tmp301
# @OPUS@\upstream\silk\control_codec.c:317:         psEncC->pitchEstimationComplexity       = SILK_PE_MIN_COMPLEX;
	movi.n	a8, 0	# tmp299,
# @OPUS@\upstream\silk\control_codec.c:321:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	slli	a3, a6, 1	# tmp305, prephitmp_46,
# @OPUS@\upstream\silk\control_codec.c:318:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.8, 16 );
	s32i.n	a9, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp301
# @OPUS@\upstream\silk\control_codec.c:320:         psEncC->shapingLPCOrder                 = 12;
	movi.n	a9, 0xc	# tmp303,
# @OPUS@\upstream\silk\control_codec.c:317:         psEncC->pitchEstimationComplexity       = SILK_PE_MIN_COMPLEX;
	s32i.n	a8, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp299
# @OPUS@\upstream\silk\control_codec.c:321:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	add.n	a3, a3, a6	# _69, tmp305, prephitmp_46
# @OPUS@\upstream\silk\control_codec.c:320:         psEncC->shapingLPCOrder                 = 12;
	s32i.n	a9, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp303
# @OPUS@\upstream\silk\control_codec.c:321:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	s32i	a3, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, _69
# @OPUS@\upstream\silk\control_codec.c:322:         psEncC->nStatesDelayedDecision          = 1;
	movi.n	a6, 1	# tmp309,
	s32i.n	a6, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, tmp309
# @OPUS@\upstream\silk\control_codec.c:324:         psEncC->NLSF_MSVQ_Survivors             = 2;
	movi.n	a6, 2	# tmp313,
# @OPUS@\upstream\silk\control_codec.c:323:         psEncC->useInterpolatedNLSFs            = 0;
	s32i.n	a8, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp299
# @OPUS@\upstream\silk\control_codec.c:325:         psEncC->warping_Q16                     = 0;
	s32i	a8, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp299
# @OPUS@\upstream\silk\control_codec.c:324:         psEncC->NLSF_MSVQ_Survivors             = 2;
	s32i.n	a6, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp313
# @OPUS@\upstream\silk\control_codec.c:325:         psEncC->warping_Q16                     = 0;
	movi.n	a8, 6	# prephitmp_299,
	j	.L32		#
.L31:
# @OPUS@\upstream\silk\control_codec.c:326:     } else if( Complexity < 2 ) {
	bnei	a4, 1, .L33	# _16,,
# @OPUS@\upstream\silk\control_codec.c:328:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.76, 16 );
	l32r	a3, .LC15	#, tmp319
# @OPUS@\upstream\silk\control_codec.c:327:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	s32i.n	a4, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, _16
# @OPUS@\upstream\silk\control_codec.c:328:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.76, 16 );
	s32i.n	a3, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp319
# @OPUS@\upstream\silk\control_codec.c:330:         psEncC->shapingLPCOrder                 = 14;
	movi.n	a3, 0xe	# tmp321,
	s32i.n	a3, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp321
# @OPUS@\upstream\silk\control_codec.c:331:         psEncC->la_shape                        = 5 * psEncC->fs_kHz;
	s32i	a2, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:333:         psEncC->useInterpolatedNLSFs            = 0;
	movi.n	a3, 0	# tmp326,
# @OPUS@\upstream\silk\control_codec.c:334:         psEncC->NLSF_MSVQ_Survivors             = 3;
	movi.n	a6, 3	# tmp328,
# @OPUS@\upstream\silk\control_codec.c:333:         psEncC->useInterpolatedNLSFs            = 0;
	s32i.n	a3, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp326
# @OPUS@\upstream\silk\control_codec.c:335:         psEncC->warping_Q16                     = 0;
	s32i	a3, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp326
# @OPUS@\upstream\silk\control_codec.c:332:         psEncC->nStatesDelayedDecision          = 1;
	s32i.n	a4, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, _16
# @OPUS@\upstream\silk\control_codec.c:334:         psEncC->NLSF_MSVQ_Survivors             = 3;
	s32i.n	a6, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp328
# @OPUS@\upstream\silk\control_codec.c:335:         psEncC->warping_Q16                     = 0;
	mov.n	a3, a2	# _69, prephitmp_266
	movi.n	a8, 8	# prephitmp_299,
	j	.L32		#
.L33:
# @OPUS@\upstream\silk\control_codec.c:336:     } else if( Complexity < 3 ) {
	bnei	a4, 2, .L34	# _16,,
# @OPUS@\upstream\silk\control_codec.c:338:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.8, 16 );
	l32r	a9, .LC14	#, tmp334
# @OPUS@\upstream\silk\control_codec.c:337:         psEncC->pitchEstimationComplexity       = SILK_PE_MIN_COMPLEX;
	movi.n	a8, 0	# tmp332,
# @OPUS@\upstream\silk\control_codec.c:338:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.8, 16 );
	s32i.n	a9, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp334
# @OPUS@\upstream\silk\control_codec.c:341:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	slli	a3, a6, 1	# tmp338, prephitmp_46,
# @OPUS@\upstream\silk\control_codec.c:340:         psEncC->shapingLPCOrder                 = 12;
	movi.n	a9, 0xc	# tmp336,
# @OPUS@\upstream\silk\control_codec.c:337:         psEncC->pitchEstimationComplexity       = SILK_PE_MIN_COMPLEX;
	s32i.n	a8, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp332
# @OPUS@\upstream\silk\control_codec.c:340:         psEncC->shapingLPCOrder                 = 12;
	s32i.n	a9, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp336
# @OPUS@\upstream\silk\control_codec.c:341:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	add.n	a3, a3, a6	# _69, tmp338, prephitmp_46
# @OPUS@\upstream\silk\control_codec.c:341:         psEncC->la_shape                        = 3 * psEncC->fs_kHz;
	s32i	a3, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, _69
# @OPUS@\upstream\silk\control_codec.c:343:         psEncC->useInterpolatedNLSFs            = 0;
	s32i.n	a8, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp332
# @OPUS@\upstream\silk\control_codec.c:345:         psEncC->warping_Q16                     = 0;
	s32i	a8, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp332
# @OPUS@\upstream\silk\control_codec.c:342:         psEncC->nStatesDelayedDecision          = 2;
	s32i.n	a4, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, _16
# @OPUS@\upstream\silk\control_codec.c:344:         psEncC->NLSF_MSVQ_Survivors             = 2;
	s32i.n	a4, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, _16
# @OPUS@\upstream\silk\control_codec.c:345:         psEncC->warping_Q16                     = 0;
	movi.n	a8, 6	# prephitmp_299,
	j	.L32		#
.L34:
# @OPUS@\upstream\silk\control_codec.c:346:     } else if( Complexity < 4 ) {
	bnei	a4, 3, .L35	# _16,,
# @OPUS@\upstream\silk\control_codec.c:347:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	movi.n	a3, 1	# tmp350,
	s32i.n	a3, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp350
# @OPUS@\upstream\silk\control_codec.c:348:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.76, 16 );
	l32r	a3, .LC15	#, tmp352
# @OPUS@\upstream\silk\control_codec.c:352:         psEncC->nStatesDelayedDecision          = 2;
	movi.n	a6, 2	# tmp357,
# @OPUS@\upstream\silk\control_codec.c:348:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.76, 16 );
	s32i.n	a3, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp352
# @OPUS@\upstream\silk\control_codec.c:350:         psEncC->shapingLPCOrder                 = 14;
	movi.n	a3, 0xe	# tmp354,
	s32i.n	a3, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp354
# @OPUS@\upstream\silk\control_codec.c:351:         psEncC->la_shape                        = 5 * psEncC->fs_kHz;
	s32i	a2, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:353:         psEncC->useInterpolatedNLSFs            = 0;
	movi.n	a3, 0	# tmp359,
# @OPUS@\upstream\silk\control_codec.c:352:         psEncC->nStatesDelayedDecision          = 2;
	s32i.n	a6, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, tmp357
# @OPUS@\upstream\silk\control_codec.c:354:         psEncC->NLSF_MSVQ_Survivors             = 4;
	movi.n	a6, 4	# tmp361,
# @OPUS@\upstream\silk\control_codec.c:353:         psEncC->useInterpolatedNLSFs            = 0;
	s32i.n	a3, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp359
# @OPUS@\upstream\silk\control_codec.c:355:         psEncC->warping_Q16                     = 0;
	s32i	a3, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp359
# @OPUS@\upstream\silk\control_codec.c:354:         psEncC->NLSF_MSVQ_Survivors             = 4;
	s32i.n	a6, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp361
# @OPUS@\upstream\silk\control_codec.c:355:         psEncC->warping_Q16                     = 0;
	mov.n	a3, a2	# _69, prephitmp_266
	movi.n	a8, 8	# prephitmp_299,
	j	.L32		#
.L35:
	slli	a3, a6, 5	# tmp365, prephitmp_46,
	sub	a3, a3, a6	# tmp366, tmp365, prephitmp_46
	slli	a3, a3, 2	# tmp367, tmp366,
	sub	a3, a3, a6	# tmp368, tmp367, prephitmp_46
	slli	a3, a3, 3	# tmp369, tmp368,
	sub	a3, a3, a6	# tmp370, tmp369, prephitmp_46
# @OPUS@\upstream\silk\control_codec.c:356:     } else if( Complexity < 6 ) {
	bgei	a4, 6, .L36	# _16,,
# @OPUS@\upstream\silk\control_codec.c:358:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.74, 16 );
	l32r	a8, .LC16	#, tmp374
# @OPUS@\upstream\silk\control_codec.c:357:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	movi.n	a6, 1	# tmp372,
# @OPUS@\upstream\silk\control_codec.c:358:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.74, 16 );
	s32i.n	a8, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp374
# @OPUS@\upstream\silk\control_codec.c:360:         psEncC->shapingLPCOrder                 = 16;
	movi.n	a8, 0x10	# tmp376,
# @OPUS@\upstream\silk\control_codec.c:357:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	s32i.n	a6, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp372
# @OPUS@\upstream\silk\control_codec.c:360:         psEncC->shapingLPCOrder                 = 16;
	s32i.n	a8, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp376
# @OPUS@\upstream\silk\control_codec.c:361:         psEncC->la_shape                        = 5 * psEncC->fs_kHz;
	s32i	a2, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:362:         psEncC->nStatesDelayedDecision          = 2;
	movi.n	a8, 2	# tmp379,
# @OPUS@\upstream\silk\control_codec.c:363:         psEncC->useInterpolatedNLSFs            = 1;
	s32i.n	a6, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp372
# @OPUS@\upstream\silk\control_codec.c:364:         psEncC->NLSF_MSVQ_Survivors             = 6;
	movi.n	a6, 6	# tmp383,
# @OPUS@\upstream\silk\control_codec.c:362:         psEncC->nStatesDelayedDecision          = 2;
	s32i.n	a8, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, tmp379
# @OPUS@\upstream\silk\control_codec.c:365:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	s32i	a3, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp370
# @OPUS@\upstream\silk\control_codec.c:364:         psEncC->NLSF_MSVQ_Survivors             = 6;
	s32i.n	a6, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp383
# @OPUS@\upstream\silk\control_codec.c:365:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	mov.n	a3, a2	# _69, prephitmp_266
	movi.n	a8, 0xa	# prephitmp_299,
	j	.L32		#
.L36:
# @OPUS@\upstream\silk\control_codec.c:366:     } else if( Complexity < 8 ) {
	bgei	a4, 8, .L37	# _16,,
# @OPUS@\upstream\silk\control_codec.c:368:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.72, 16 );
	l32r	a8, .LC17	#, tmp388
# @OPUS@\upstream\silk\control_codec.c:367:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	movi.n	a6, 1	# tmp386,
# @OPUS@\upstream\silk\control_codec.c:368:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.72, 16 );
	s32i.n	a8, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp388
# @OPUS@\upstream\silk\control_codec.c:370:         psEncC->shapingLPCOrder                 = 20;
	movi.n	a8, 0x14	# tmp390,
# @OPUS@\upstream\silk\control_codec.c:367:         psEncC->pitchEstimationComplexity       = SILK_PE_MID_COMPLEX;
	s32i.n	a6, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp386
# @OPUS@\upstream\silk\control_codec.c:370:         psEncC->shapingLPCOrder                 = 20;
	s32i.n	a8, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp390
# @OPUS@\upstream\silk\control_codec.c:371:         psEncC->la_shape                        = 5 * psEncC->fs_kHz;
	s32i	a2, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:372:         psEncC->nStatesDelayedDecision          = 3;
	movi.n	a8, 3	# tmp393,
# @OPUS@\upstream\silk\control_codec.c:373:         psEncC->useInterpolatedNLSFs            = 1;
	s32i.n	a6, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp386
# @OPUS@\upstream\silk\control_codec.c:374:         psEncC->NLSF_MSVQ_Survivors             = 8;
	movi.n	a6, 8	# tmp397,
# @OPUS@\upstream\silk\control_codec.c:372:         psEncC->nStatesDelayedDecision          = 3;
	s32i.n	a8, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, tmp393
# @OPUS@\upstream\silk\control_codec.c:375:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	s32i	a3, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp370
# @OPUS@\upstream\silk\control_codec.c:374:         psEncC->NLSF_MSVQ_Survivors             = 8;
	s32i.n	a6, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp397
# @OPUS@\upstream\silk\control_codec.c:375:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	mov.n	a3, a2	# _69, prephitmp_266
	movi.n	a8, 0xc	# prephitmp_299,
	j	.L32		#
.L37:
# @OPUS@\upstream\silk\control_codec.c:377:         psEncC->pitchEstimationComplexity       = SILK_PE_MAX_COMPLEX;
	movi.n	a6, 2	# tmp400,
	s32i.n	a6, a12, 36	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationComplexity, tmp400
# @OPUS@\upstream\silk\control_codec.c:378:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.7, 16 );
	l32r	a6, .LC18	#, tmp402
# @OPUS@\upstream\silk\control_codec.c:384:         psEncC->NLSF_MSVQ_Survivors             = 16;
	movi.n	a8, 0x10	# tmp411,
# @OPUS@\upstream\silk\control_codec.c:378:         psEncC->pitchEstimationThreshold_Q16    = SILK_FIX_CONST( 0.7, 16 );
	s32i.n	a6, a12, 44	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationThreshold_Q16, tmp402
# @OPUS@\upstream\silk\control_codec.c:380:         psEncC->shapingLPCOrder                 = 24;
	movi.n	a6, 0x18	# tmp404,
	s32i.n	a6, a12, 28	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapingLPCOrder, tmp404
# @OPUS@\upstream\silk\control_codec.c:381:         psEncC->la_shape                        = 5 * psEncC->fs_kHz;
	s32i	a2, a13, 248	# MEM[(struct silk_encoder_state *)psEnc_25(D)].la_shape, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:382:         psEncC->nStatesDelayedDecision          = MAX_DEL_DEC_STATES;
	movi.n	a6, 4	# tmp407,
	s32i.n	a6, a12, 20	# MEM[(struct silk_encoder_state *)psEnc_25(D)].nStatesDelayedDecision, tmp407
# @OPUS@\upstream\silk\control_codec.c:383:         psEncC->useInterpolatedNLSFs            = 1;
	movi.n	a6, 1	# tmp409,
# @OPUS@\upstream\silk\control_codec.c:385:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	s32i	a3, a12, 64	# MEM[(struct silk_encoder_state *)psEnc_25(D)].warping_Q16, tmp370
# @OPUS@\upstream\silk\control_codec.c:383:         psEncC->useInterpolatedNLSFs            = 1;
	s32i.n	a6, a12, 24	# MEM[(struct silk_encoder_state *)psEnc_25(D)].useInterpolatedNLSFs, tmp409
# @OPUS@\upstream\silk\control_codec.c:384:         psEncC->NLSF_MSVQ_Survivors             = 16;
	s32i.n	a8, a12, 52	# MEM[(struct silk_encoder_state *)psEnc_25(D)].NLSF_MSVQ_Survivors, tmp411
# @OPUS@\upstream\silk\control_codec.c:385:         psEncC->warping_Q16                     = psEncC->fs_kHz * SILK_FIX_CONST( WARPING_MULTIPLIER, 16 );
	mov.n	a3, a2	# _69, prephitmp_266
.L32:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:548:     return (((a) < (b)) ? (a) : (b));
	l32i.n	a6, a12, 32	# MEM[(struct silk_encoder_state *)psEnc_25(D)].predictLPCOrder, MEM[(struct silk_encoder_state *)psEnc_25(D)].predictLPCOrder
	bge	a8, a6, .L38	# prephitmp_299, MEM[(struct silk_encoder_state *)psEnc_25(D)].predictLPCOrder,
	mov.n	a6, a8	# MEM[(struct silk_encoder_state *)psEnc_25(D)].predictLPCOrder, prephitmp_299
.L38:
# @OPUS@\upstream\silk\control_codec.c:390:     psEncC->shapeWinLength          = SUB_FRAME_LENGTH_MS * psEncC->fs_kHz + 2 * psEncC->la_shape;
	slli	a3, a3, 1	# tmp421, _69,
# @OPUS@\upstream\silk\control_codec.c:389:     psEncC->pitchEstimationLPCOrder = silk_min_int( psEncC->pitchEstimationLPCOrder, psEncC->predictLPCOrder );
	s32i.n	a6, a12, 40	# MEM[(struct silk_encoder_state *)psEnc_25(D)].pitchEstimationLPCOrder, MEM[(struct silk_encoder_state *)psEnc_25(D)].predictLPCOrder
# @OPUS@\upstream\silk\control_codec.c:390:     psEncC->shapeWinLength          = SUB_FRAME_LENGTH_MS * psEncC->fs_kHz + 2 * psEncC->la_shape;
	add.n	a2, a3, a2	# tmp422, tmp421, prephitmp_266
# @OPUS@\upstream\silk\control_codec.c:122:     psEnc->sCmn.PacketLoss_perc = encControl->packetLossPercentage;
	l32i.n	a6, a14, 32	# encControl_24(D)->packetLossPercentage, _17
# @OPUS@\upstream\silk\control_codec.c:390:     psEncC->shapeWinLength          = SUB_FRAME_LENGTH_MS * psEncC->fs_kHz + 2 * psEncC->la_shape;
	s32i	a2, a13, 252	# MEM[(struct silk_encoder_state *)psEnc_25(D)].shapeWinLength, tmp422
# @OPUS@\upstream\silk\control_codec.c:391:     psEncC->Complexity              = Complexity;
	s32i.n	a4, a12, 16	# MEM[(struct silk_encoder_state *)psEnc_25(D)].Complexity, _16
# @OPUS@\upstream\silk\control_codec.c:122:     psEnc->sCmn.PacketLoss_perc = encControl->packetLossPercentage;
	s32i.n	a6, a12, 8	# psEnc_25(D)->sCmn.PacketLoss_perc, _17
# @OPUS@\upstream\silk\control_codec.c:127:     ret += silk_setup_LBRR( &psEnc->sCmn, encControl );
	l32i.n	a2, a14, 48	# MEM[(int *)encControl_24(D) + 48B], _54
# @OPUS@\upstream\silk\control_codec.c:410:     LBRR_in_previous_packet = psEncC->LBRR_enabled;
	l32i	a3, a7, 204	# MEM[(struct silk_encoder_state *)psEnc_25(D)].LBRR_enabled, LBRR_in_previous_packet
# @OPUS@\upstream\silk\control_codec.c:411:     psEncC->LBRR_enabled = encControl->LBRR_coded;
	s32i	a2, a7, 204	# MEM[(struct silk_encoder_state *)psEnc_25(D)].LBRR_enabled, _54
# @OPUS@\upstream\silk\control_codec.c:412:     if( psEncC->LBRR_enabled ) {
	beqz.n	a2, .L39	# _54,
# @OPUS@\upstream\silk\control_codec.c:414:         if( LBRR_in_previous_packet == 0 ) {
	bnez.n	a3, .L40	# LBRR_in_previous_packet,
# @OPUS@\upstream\silk\control_codec.c:416:             psEncC->LBRR_GainIncreases = 7;
	movi.n	a2, 7	# tmp428,
	s32i	a2, a7, 208	# MEM[(struct silk_encoder_state *)psEnc_25(D)].LBRR_GainIncreases, tmp428
	j	.L39		#
.L40:
# @OPUS@\upstream\silk\control_codec.c:418:             psEncC->LBRR_GainIncreases = silk_max_int( 7 - silk_SMULWB( (opus_int32)psEncC->PacketLoss_perc, SILK_FIX_CONST( 0.2, 16 ) ), 3 );
	extui	a2, a6, 0, 16	# tmp434, _17,
	slli	a3, a2, 1	# tmp436, tmp434,
	add.n	a3, a3, a2	# tmp437, tmp436, tmp434
	slli	a2, a3, 4	# tmp438, tmp437,
	add.n	a3, a3, a2	# tmp439, tmp437, tmp438
	srai	a2, a6, 16	# tmp430, _17,
	l32r	a6, .LC19	#, tmp432
	slli	a4, a3, 8	# tmp440, tmp439,
	mull	a2, a2, a6	# tmp431, tmp430, tmp432
	add.n	a3, a3, a4	# tmp441, tmp439, tmp440
# @OPUS@\upstream\silk\control_codec.c:418:             psEncC->LBRR_GainIncreases = silk_max_int( 7 - silk_SMULWB( (opus_int32)psEncC->PacketLoss_perc, SILK_FIX_CONST( 0.2, 16 ) ), 3 );
	addi.n	a2, a2, 7	# tmp433, tmp431,
# @OPUS@\upstream\silk\control_codec.c:418:             psEncC->LBRR_GainIncreases = silk_max_int( 7 - silk_SMULWB( (opus_int32)psEncC->PacketLoss_perc, SILK_FIX_CONST( 0.2, 16 ) ), 3 );
	srai	a3, a3, 16	# tmp442, tmp441,
# @OPUS@\upstream\silk\control_codec.c:418:             psEncC->LBRR_GainIncreases = silk_max_int( 7 - silk_SMULWB( (opus_int32)psEncC->PacketLoss_perc, SILK_FIX_CONST( 0.2, 16 ) ), 3 );
	sub	a2, a2, a3	# tmp444, tmp433, tmp442
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\upstream\silk\sigproc_fix.h:566:     return (((a) > (b)) ? (a) : (b));
	bgei	a2, 3, .L41	# tmp444,,
	movi.n	a2, 3	# tmp444,
.L41:
# @OPUS@\upstream\silk\control_codec.c:418:             psEncC->LBRR_GainIncreases = silk_max_int( 7 - silk_SMULWB( (opus_int32)psEncC->PacketLoss_perc, SILK_FIX_CONST( 0.2, 16 ) ), 3 );
	s32i	a2, a7, 208	# MEM[(struct silk_encoder_state *)psEnc_25(D)].LBRR_GainIncreases, tmp444
.L39:
# @OPUS@\upstream\silk\control_codec.c:129:     psEnc->sCmn.controlled_since_last_payload = 1;
	movi.n	a2, 1	# tmp448,
	s32i.n	a2, a12, 60	# psEnc_25(D)->sCmn.controlled_since_last_payload, tmp448
# @OPUS@\upstream\silk\control_codec.c:131:     return ret;
	j	.L7		#
.L24:
	s32i	a2, a12, 80	# psEnc_25(D)->sCmn.pitch_contour_iCDF, cstore_305
# @OPUS@\upstream\silk\control_codec.c:276:             psEnc->sCmn.predictLPCOrder = MIN_LPC_ORDER;
	movi.n	a2, 0xa	#,
# @OPUS@\upstream\silk\control_codec.c:277:             psEnc->sCmn.psNLSF_CB  = &silk_NLSF_CB_NB_MB;
	l32r	a11, .LC4	#, cstore_313
# @OPUS@\upstream\silk\control_codec.c:276:             psEnc->sCmn.predictLPCOrder = MIN_LPC_ORDER;
	s32i.n	a2, sp, 0	# %sfp,
	j	.L26		#
.L42:
# @OPUS@\upstream\silk\control_codec.c:216:             psEnc->sCmn.nFramesPerPacket = 1;
	movi.n	a3, 1	# tmp452,
	s32i	a3, a9, 112	# psEnc_25(D)->sCmn.nFramesPerPacket, tmp452
	j	.L16		#
.L14:
# @OPUS@\upstream\silk\control_codec.c:215:         if( PacketSize_ms <= 10 ) {
	movi.n	a2, 0xa	# tmp453,
	bge	a2, a4, .L42	# tmp453, _15,
	j	.L15		#
.L7:
# @OPUS@\upstream\silk\control_codec.c:132: }
	l32i.n	a0, sp, 60	#,
	mov.n	a2, a5	#, <retval>
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	silk_control_encoder, .-silk_control_encoder
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
