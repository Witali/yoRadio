# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_down2_3.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_down2_3.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2_3.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2_3.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2_3.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_down2_3.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_down2_3.c.s.raw
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
	.section	.text.silk_resampler_down2_3,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.literal .LC2, silk_Resampler_2_3_COEFS_LQ
	.align	4
	.global	silk_resampler_down2_3
	.type	silk_resampler_down2_3, @function
# Function: silk_resampler_down2_3
# Module: upstream/silk/resampler_down2_3.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #define ORDER_FIR                   4
# C context:
# C context: /* Downsample by a factor 2/3, low quality */
# C context: void silk_resampler_down2_3(
# C context: opus_int32                  *S,                 /* I/O  State vector [ 6 ]                                          */
# C context: opus_int16                  *out,               /* O    Output signal [ floor(2*inLen/3) ]                          */
# C context: const opus_int16            *in,                /* I    Input signal [ inLen ]                                      */
# C context: opus_int32                  inLen               /* I    Number of input samples                                     */
silk_resampler_down2_3:
	addi	sp, sp, -96	#,,
	s32i	a0, sp, 92	#,
	s32i.n	a5, sp, 40	# %sfp, inLen
	s32i	a12, sp, 88	#,
	s32i	a13, sp, 84	#,
	s32i.n	a4, sp, 44	# %sfp, in
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:45: {
	s32i.n	a2, sp, 60	# %sfp, S
	mov.n	a13, a3	# out, out
# @OPUS@\upstream\silk\resampler_down2_3.c:49:     SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\resampler_down2_3.c:51:     ALLOC( buf, RESAMPLER_MAX_BATCH_SIZE_IN + ORDER_FIR, opus_int32 );
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	movi	a2, 0x1e4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\resampler_down2_3.c:54:     silk_memcpy( buf, S, ORDER_FIR * sizeof( opus_int32 ) );
	l32i.n	a3, sp, 60	# %sfp,
	movi.n	a4, 0x10	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:51:     ALLOC( buf, RESAMPLER_MAX_BATCH_SIZE_IN + ORDER_FIR, opus_int32 );
	s32i.n	a2, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:54:     silk_memcpy( buf, S, ORDER_FIR * sizeof( opus_int32 ) );
	call0	memcpy		#
	l32i.n	a7, sp, 60	# %sfp,
	l32i.n	a8, sp, 48	# %sfp,
	addi	a7, a7, 16	#,,
	addi	a8, a8, 16	#,,
	l32r	a12, .LC0	#, tmp254
	s32i.n	a7, sp, 52	# %sfp,
	s32i.n	a8, sp, 56	# %sfp,
.L8:
# @OPUS@\upstream\silk\resampler_down2_3.c:58:         nSamplesIn = silk_min( inLen, RESAMPLER_MAX_BATCH_SIZE_IN );
	l32i.n	a11, sp, 40	# %sfp,
	movi	a2, 0x1e0	# tmp132,
	s32i.n	a11, sp, 36	# %sfp,
	bge	a2, a11, .L2	# tmp132,,
	s32i.n	a2, sp, 36	# %sfp, tmp132
.L2:
# @OPUS@\upstream\silk\resampler_down2_3.c:61:         silk_resampler_private_AR2( &S[ ORDER_FIR ], &buf[ ORDER_FIR ], in,
	l32i.n	a6, sp, 36	# %sfp,
	l32r	a5, .LC2	#,
	l32i.n	a4, sp, 44	# %sfp,
	l32i.n	a3, sp, 56	# %sfp,
	l32i.n	a2, sp, 52	# %sfp,
	call0	silk_resampler_private_AR2		#
# @OPUS@\upstream\silk\resampler_down2_3.c:67:         while( counter > 2 ) {
	l32i.n	a14, sp, 40	# %sfp,
	blti	a14, 3, .L3	#,,
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	l32r	a2, .LC2	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	l32r	a3, .LC2	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	l32r	a4, .LC2	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32r	a5, .LC2	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	l16si	a2, a2, 4	# silk_Resampler_2_3_COEFS_LQ,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	l16si	a3, a3, 6	# silk_Resampler_2_3_COEFS_LQ,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	l16si	a4, a4, 10	# silk_Resampler_2_3_COEFS_LQ,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l16si	a5, a5, 8	# silk_Resampler_2_3_COEFS_LQ,
# @OPUS@\upstream\silk\resampler_down2_3.c:66:         counter = nSamplesIn;
	l32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32i.n	a6, sp, 48	# %sfp, buf_ptr
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	s32i.n	a3, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	s32i.n	a5, sp, 24	# %sfp,
	mov.n	a10, a13	# ivtmp$18, out
# @OPUS@\upstream\silk\resampler_down2_3.c:66:         counter = nSamplesIn;
	s32i.n	a7, sp, 28	# %sfp,
.L6:
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	l32i.n	a4, a6, 0	# MEM[base: buf_ptr_207, offset: 0B], _205
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	l32i.n	a3, a6, 4	# MEM[base: buf_ptr_207, offset: 4B], _199
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32i.n	a5, a6, 12	# MEM[base: buf_ptr_207, offset: 12B], _186
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	srai	a14, a4, 16	# tmp151, _205,
	mull	a14, a14, a7	# tmp152, tmp151,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	l32i.n	a7, sp, 20	# %sfp,
	srai	a2, a3, 16	# _198, _199,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	srai	a11, a5, 16	# _185, _186,
# @OPUS@\upstream\silk\resampler_down2_3.c:79:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	mull	a15, a7, a11	# tmp173,, _185
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	mull	a9, a7, a2	# tmp153,, _198
# @OPUS@\upstream\silk\resampler_down2_3.c:77:             res_Q6 = silk_SMULWB(         buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	extui	a4, a4, 0, 16	# tmp157, _205,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	mull	a11, a7, a11	# tmp155,, _185
# @OPUS@\upstream\silk\resampler_down2_3.c:77:             res_Q6 = silk_SMULWB(         buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	mull	a2, a7, a2	# tmp174,, _198
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a9, a14, a9	# tmp154, tmp152, tmp153
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	mull	a4, a4, a7	# tmp158, tmp157,
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	l32i.n	a14, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:77:             res_Q6 = silk_SMULWB(         buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	l32i.n	a8, a6, 8	# MEM[base: buf_ptr_207, offset: 8B], _193
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	extui	a3, a3, 0, 16	# _196, _199,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	extui	a5, a5, 0, 16	# _183, _186,
# @OPUS@\upstream\silk\resampler_down2_3.c:77:             res_Q6 = silk_SMULWB(         buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	mull	a13, a7, a3	# tmp179,, _196
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a9, a9, a11	# tmp156, tmp154, tmp155
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	mull	a3, a14, a3	# tmp161,, _196
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	add.n	a2, a15, a2	# tmp175, tmp173, tmp174
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	l32i.n	a11, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:79:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	mull	a15, a14, a5	# tmp182,, _183
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	l32i.n	a14, sp, 32	# %sfp,
	extui	a7, a8, 0, 16	# tmp146, _193,
	mull	a7, a7, a14	# tmp147, tmp146,
# @OPUS@\upstream\silk\resampler_down2_3.c:69:             res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	srai	a4, a4, 16	# tmp159, tmp158,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	srai	a8, a8, 16	# tmp149, _193,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	mull	a5, a11, a5	# tmp164,, _183
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	mull	a8, a8, a14	# tmp150, tmp149,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a9, a9, a4	# tmp160, tmp156, tmp159
# @OPUS@\upstream\silk\resampler_down2_3.c:70:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	srai	a3, a3, 16	# tmp162, tmp161,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	srai	a7, a7, 16	# tmp148, tmp147,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a9, a9, a3	# tmp163, tmp160, tmp162
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	srai	a5, a5, 16	# tmp165, tmp164,
# @OPUS@\upstream\silk\resampler_down2_3.c:71:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], silk_Resampler_2_3_COEFS_LQ[ 5 ] );
	add.n	a7, a7, a8	# _187, tmp148, tmp150
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a3, a9, a5	# tmp166, tmp163, tmp165
# @OPUS@\upstream\silk\resampler_down2_3.c:86:             counter -= 3;
	l32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:72:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	add.n	a3, a3, a7	# res_Q6, tmp166, _187
# @OPUS@\upstream\silk\resampler_down2_3.c:75:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a3, a3, 5	# tmp168, res_Q6,
# @OPUS@\upstream\silk\resampler_down2_3.c:86:             counter -= 3;
	addi	a4, a4, -3	#,,
# @OPUS@\upstream\silk\resampler_down2_3.c:75:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	addi.n	a3, a3, 1	# tmp169, tmp168,
# @OPUS@\upstream\silk\resampler_down2_3.c:86:             counter -= 3;
	s32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:75:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a3, a3, 1	# _172, tmp169,
# @OPUS@\upstream\silk\resampler_down2_3.c:77:             res_Q6 = silk_SMULWB(         buf_ptr[ 1 ], silk_Resampler_2_3_COEFS_LQ[ 4 ] );
	srai	a13, a13, 16	# tmp180, tmp179,
# @OPUS@\upstream\silk\resampler_down2_3.c:79:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], silk_Resampler_2_3_COEFS_LQ[ 3 ] );
	srai	a14, a15, 16	# tmp183, tmp182,
# @OPUS@\upstream\silk\resampler_down2_3.c:75:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	mov.n	a4, a12	# iftmp$0_170, tmp254
	blt	a12, a3, .L4	# tmp254, _172,
	l32r	a4, .LC1	#, iftmp$0_170
	slli	a5, a3, 16	# tmp172, _172,
	blt	a3, a4, .L4	# _172, tmp8,
	srai	a4, a5, 16	# iftmp$0_170, tmp172,
.L4:
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	l32i.n	a3, a6, 16	# MEM[base: buf_ptr_207, offset: 16B], _162
	l32i.n	a11, sp, 16	# %sfp,
	srai	a15, a3, 16	# tmp176, _162,
	mull	a15, a15, a11	# tmp177, tmp176,
	extui	a3, a3, 0, 16	# tmp185, _162,
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	add.n	a15, a2, a15	# tmp178, tmp175, tmp177
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	mull	a3, a3, a11	# tmp186, tmp185,
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	add.n	a13, a15, a13	# tmp181, tmp178, tmp180
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	srai	a8, a3, 16	# tmp187, tmp186,
# @OPUS@\upstream\silk\resampler_down2_3.c:80:             res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], silk_Resampler_2_3_COEFS_LQ[ 2 ] );
	add.n	a15, a13, a14	# tmp184, tmp181, tmp183
	add.n	a8, a15, a8	# tmp188, tmp184, tmp187
	add.n	a7, a8, a7	# res_Q6, tmp188, _187
# @OPUS@\upstream\silk\resampler_down2_3.c:83:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a7, a7, 5	# tmp190, res_Q6,
	addi.n	a7, a7, 1	# tmp191, tmp190,
# @OPUS@\upstream\silk\resampler_down2_3.c:75:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	s16i	a4, a10, 0	# MEM[base: _110, offset: 0B], iftmp$0_170
# @OPUS@\upstream\silk\resampler_down2_3.c:83:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a7, a7, 1	# _148, tmp191,
	mov.n	a3, a10	# _110, ivtmp$18
# @OPUS@\upstream\silk\resampler_down2_3.c:83:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	mov.n	a2, a12	# iftmp$3_146, tmp254
	addi.n	a10, a10, 4	# ivtmp$18, ivtmp$18,
	blt	a12, a7, .L5	# tmp254, _148,
	l32r	a2, .LC1	#, iftmp$3_146
	slli	a4, a7, 16	# tmp194, _148,
	blt	a7, a2, .L5	# _148, tmp14,
	srai	a2, a4, 16	# iftmp$3_146, tmp194,
.L5:
# @OPUS@\upstream\silk\resampler_down2_3.c:83:             *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	s16i	a2, a3, 2	# MEM[base: _110, offset: 2B], iftmp$3_146
# @OPUS@\upstream\silk\resampler_down2_3.c:67:         while( counter > 2 ) {
	l32i.n	a2, sp, 28	# %sfp,
	mov.n	a13, a10	# out, ivtmp$18
# @OPUS@\upstream\silk\resampler_down2_3.c:85:             buf_ptr += 3;
	addi.n	a6, a6, 12	# buf_ptr, buf_ptr,
# @OPUS@\upstream\silk\resampler_down2_3.c:67:         while( counter > 2 ) {
	bgei	a2, 3, .L6	#,,
.L3:
# @OPUS@\upstream\silk\resampler_down2_3.c:89:         in += nSamplesIn;
	l32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:90:         inLen -= nSamplesIn;
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:89:         in += nSamplesIn;
	l32i.n	a11, sp, 44	# %sfp,
	slli	a2, a7, 1	# tmp195,,
# @OPUS@\upstream\silk\resampler_down2_3.c:90:         inLen -= nSamplesIn;
	sub	a8, a8, a7	#,,
# @OPUS@\upstream\silk\resampler_down2_3.c:89:         in += nSamplesIn;
	add.n	a11, a11, a2	#,, tmp195
	l32i.n	a14, sp, 48	# %sfp,
	slli	a3, a7, 2	# tmp196,,
# @OPUS@\upstream\silk\resampler_down2_3.c:90:         inLen -= nSamplesIn;
	s32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_down2_3.c:89:         in += nSamplesIn;
	s32i.n	a11, sp, 44	# %sfp,
	add.n	a3, a14, a3	# _228,, tmp196
# @OPUS@\upstream\silk\resampler_down2_3.c:94:             silk_memcpy( buf, &buf[ nSamplesIn ], ORDER_FIR * sizeof( opus_int32 ) );
	movi.n	a4, 0x10	#,
# @OPUS@\upstream\silk\resampler_down2_3.c:92:         if( inLen > 0 ) {
	blti	a8, 1, .L7	#,,
# @OPUS@\upstream\silk\resampler_down2_3.c:94:             silk_memcpy( buf, &buf[ nSamplesIn ], ORDER_FIR * sizeof( opus_int32 ) );
	mov.n	a2, a14	#,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_down2_3.c:58:         nSamplesIn = silk_min( inLen, RESAMPLER_MAX_BATCH_SIZE_IN );
	j	.L8		#
.L7:
# @OPUS@\upstream\silk\resampler_down2_3.c:101:     silk_memcpy( S, &buf[ nSamplesIn ], ORDER_FIR * sizeof( opus_int32 ) );
	l32i.n	a2, sp, 60	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_down2_3.c:102:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\resampler_down2_3.c:103: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	silk_resampler_down2_3, .-silk_resampler_down2_3
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
