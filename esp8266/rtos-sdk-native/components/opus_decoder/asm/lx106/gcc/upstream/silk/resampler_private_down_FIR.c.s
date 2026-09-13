# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_private_down_FIR.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_private_down_FIR.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_down_FIR.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_down_FIR.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_down_FIR.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_private_down_FIR.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_private_down_FIR.c.s.raw
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
	.section	.text.silk_resampler_private_down_FIR,"ax",@progbits
	.literal_position
	.literal .LC0, 32767
	.literal .LC1, -32768
	.align	4
	.global	silk_resampler_private_down_FIR
	.type	silk_resampler_private_down_FIR, @function
# Function: silk_resampler_private_down_FIR
# Module: upstream/silk/resampler_private_down_FIR.c
# Fixed-point Opus SILK processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /* Resample with a 2nd order AR filter followed by FIR interpolation */
# C context: void silk_resampler_private_down_FIR(
# C context: void                            *SS,            /* I/O  Resampler state             */
# C context: opus_int16                      out[],          /* O    Output signal               */
# C context: const opus_int16                in[],           /* I    Input signal                */
# C context: opus_int32                      inLen           /* I    Number of input samples     */
silk_resampler_private_down_FIR:
	movi	a9, 0xf0	#,
	sub	sp, sp, a9	#,,
	s32i	a0, sp, 236	#,
	s32i	a12, sp, 232	#,
	s32i	a14, sp, 224	#,
	s32i	a5, sp, 116	# %sfp, inLen
	s32i	a4, sp, 124	# %sfp, in
	s32i	a13, sp, 228	#,
	s32i	a15, sp, 220	#,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:151: {
	s32i	a2, sp, 96	# %sfp, SS
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:157:     SAVE_STACK;
	s32i	a3, sp, 184	#, tmp7
	call0	yoradio_opus_scratch_mark		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:159:     ALLOC( buf, S->batchSize + S->FIR_Order, opus_int32 );
	l32i	a8, sp, 96	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:157:     SAVE_STACK;
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:159:     ALLOC( buf, S->batchSize + S->FIR_Order, opus_int32 );
	l32i	a5, a8, 276	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order
	l32i	a6, a8, 268	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].batchSize, MEM[(struct silk_resampler_state_struct *)SS_37(D)].batchSize
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:157:     SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:159:     ALLOC( buf, S->batchSize + S->FIR_Order, opus_int32 );
	add.n	a2, a6, a5	#, MEM[(struct silk_resampler_state_struct *)SS_37(D)].batchSize, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order
	movi.n	a4, 0	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:162:     silk_memcpy( buf, S->sFIR.i32, S->FIR_Order * sizeof( opus_int32 ) );
	l32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:159:     ALLOC( buf, S->batchSize + S->FIR_Order, opus_int32 );
	s32i	a2, sp, 92	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:162:     silk_memcpy( buf, S->sFIR.i32, S->FIR_Order * sizeof( opus_int32 ) );
	l32i	a4, a9, 276	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order
	addi	a10, a9, 24	#,,
	slli	a4, a4, 2	#, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order,
	mov.n	a3, a10	#,
	s32i	a10, sp, 180	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:164:     FIR_Coefs = &S->Coefs[ 2 ];
	l32i	a11, sp, 96	# %sfp,
	l32i	a7, sp, 184	#,
	l32i	a12, a11, 296	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].Coefs, _9
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:167:     index_increment_Q16 = S->invRatio_Q16;
	l32i	a14, a11, 272	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].invRatio_Q16,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:164:     FIR_Coefs = &S->Coefs[ 2 ];
	addi.n	a8, a12, 4	#, _9,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:167:     index_increment_Q16 = S->invRatio_Q16;
	s32i	a14, sp, 120	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:164:     FIR_Coefs = &S->Coefs[ 2 ];
	s32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:164:     FIR_Coefs = &S->Coefs[ 2 ];
	mov.n	a5, a12	# pretmp_1699, _9
	s32i.n	a7, sp, 56	# %sfp, out
	mov.n	a9, a11	#,
.L16:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:169:         nSamplesIn = silk_min( inLen, S->batchSize );
	l32i	a9, a9, 268	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].batchSize,
	l32i	a10, sp, 116	# %sfp,
	s32i	a9, sp, 72	# %sfp,
	bge	a10, a9, .L2	#,,
	s32i	a10, sp, 72	# %sfp,
.L2:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	l32i	a11, sp, 96	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	l32i	a14, sp, 92	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	l32i	a3, a11, 276	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	l32i	a6, sp, 72	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	slli	a3, a3, 2	# tmp676, MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:172:         silk_resampler_private_AR2( S->sIIR, &buf[ S->FIR_Order ], in, S->Coefs, nSamplesIn );
	l32i	a4, sp, 124	# %sfp,
	mov.n	a2, a11	#,
	add.n	a3, a14, a3	#,, tmp676
	call0	silk_resampler_private_AR2		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:177:         out = silk_resampler_private_down_FIR_INTERPOL( out, buf, FIR_Coefs, S->FIR_Order,
	l32i	a7, sp, 96	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:174:         max_index_Q16 = silk_LSHIFT32( nSamplesIn, 16 );
	l32i	a8, sp, 72	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:177:         out = silk_resampler_private_down_FIR_INTERPOL( out, buf, FIR_Coefs, S->FIR_Order,
	l32i	a7, a7, 276	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Order,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:174:         max_index_Q16 = silk_LSHIFT32( nSamplesIn, 16 );
	slli	a8, a8, 16	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:177:         out = silk_resampler_private_down_FIR_INTERPOL( out, buf, FIR_Coefs, S->FIR_Order,
	s32i	a7, sp, 104	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:51:     switch( FIR_Order ) {
	movi.n	a2, 0x18	# tmp679,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:174:         max_index_Q16 = silk_LSHIFT32( nSamplesIn, 16 );
	s32i	a8, sp, 112	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:51:     switch( FIR_Order ) {
	beq	a7, a2, .L3	#, tmp679,
	movi.n	a2, 0x24	# tmp680,
	beq	a7, a2, .L4	#, tmp680,
	movi.n	a2, 0x12	# tmp681,
	bne	a7, a2, .L6	#, tmp681,
	j	.L5		#
.L4:
	l32i.n	a9, sp, 56	# %sfp,
	l32r	a10, .LC0	#,
	s32i	a9, sp, 172	# %sfp,
	s32i	a10, sp, 76	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	movi.n	a13, 0	# index_Q16,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	bgei	a8, 1, .L14	# tmp11,,
	j	.L6		#
.L3:
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	movi.n	a10, 0	# index_Q16,
	s32i	a14, sp, 100	# %sfp,
	mov.n	a13, a10	# index_Q16, index_Q16
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	bgei	a8, 1, .L12	# tmp2,,
	j	.L6		#
.L5:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blti	a8, 1, .L6	# tmp3,,
	l32i	a7, sp, 96	# %sfp,
	l32r	a9, .LC0	#,
	l32i	a2, a7, 280	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Fracs, _20
	l16si	a8, a7, 280	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].FIR_Fracs,
	l32i.n	a10, sp, 56	# %sfp,
	addi.n	a2, a2, -1	#, _20,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	movi.n	a11, 0	#,
	s32i	a8, sp, 80	# %sfp,
	s32i	a9, sp, 76	# %sfp,
	s32i	a2, sp, 84	# %sfp,
	s32i	a10, sp, 68	# %sfp,
	s32i.n	a11, sp, 16	# %sfp,
	s32i	a12, sp, 88	# %sfp, _9
.L10:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:58:                 interpol_ind = silk_SMULWB( index_Q16 & 0xFFFF, FIR_Fracs );
	l32i.n	a14, sp, 16	# %sfp,
	l32i	a2, sp, 80	# %sfp,
	extui	a10, a14, 0, 16	# tmp685,,
	mull	a10, a10, a2	# tmp686, tmp685,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:55:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	l32i	a7, sp, 92	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:58:                 interpol_ind = silk_SMULWB( index_Q16 & 0xFFFF, FIR_Fracs );
	srai	a10, a10, 16	# interpol_ind, tmp686,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:55:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	srai	a5, a14, 16	# tmp683,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:61:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * interpol_ind ];
	slli	a3, a10, 3	# tmp688, interpol_ind,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:61:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * interpol_ind ];
	l32i	a8, sp, 176	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:61:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * interpol_ind ];
	add.n	a3, a3, a10	# tmp689, tmp688, interpol_ind
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:55:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	slli	a5, a5, 2	# tmp684, tmp683,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:55:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	add.n	a5, a7, a5	# buf_ptr,, tmp684
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:61:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * interpol_ind ];
	slli	a3, a3, 1	# tmp690, tmp689,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:61:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * interpol_ind ];
	add.n	a3, a8, a3	# interpol_ptr,, tmp690
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	l32i.n	a9, a5, 4	# MEM[(opus_int32 *)buf_ptr_1685 + 4B],
	l16si	a12, a3, 2	# MEM[(const opus_int16 *)interpol_ptr_1679 + 2B], _1667
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	l32i.n	a14, a5, 0	# *buf_ptr_1685,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	l32i.n	a2, a5, 8	# MEM[(opus_int32 *)buf_ptr_1685 + 8B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	l16si	a13, a3, 0	# *interpol_ptr_1679, _1675
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	l16si	a11, a3, 4	# MEM[(const opus_int16 *)interpol_ptr_1679 + 4B], _1658
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	srai	a4, a9, 16	# tmp732,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	srai	a6, a14, 16	# tmp734,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	mull	a14, a4, a12	# tmp733, tmp732, _1667
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	srai	a4, a2, 16	# tmp737,,
	mull	a15, a4, a11	# tmp738, tmp737, _1658
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	mull	a6, a6, a13	# tmp735, tmp734, _1675
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	l32i.n	a4, a5, 12	# MEM[(opus_int32 *)buf_ptr_1685 + 12B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	l16si	a8, a3, 8	# MEM[(const opus_int16 *)interpol_ptr_1679 + 8B], _1640
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	srai	a2, a4, 16	# tmp740,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a4, a14, a6	# tmp736, tmp733, tmp735
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	l32i.n	a6, a5, 16	# MEM[(opus_int32 *)buf_ptr_1685 + 16B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	l16si	a9, a3, 6	# MEM[(const opus_int16 *)interpol_ptr_1679 + 6B], _1649
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	srai	a14, a6, 16	# tmp743,,
	mull	a14, a14, a8	#, tmp743, _1640
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	mull	a2, a2, a9	#, tmp740, _1649
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	s32i.n	a14, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	l32i.n	a14, a5, 20	# MEM[(opus_int32 *)buf_ptr_1685 + 20B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	l16si	a7, a3, 10	# MEM[(const opus_int16 *)interpol_ptr_1679 + 10B], _1631
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	l16si	a6, a3, 12	# MEM[(const opus_int16 *)interpol_ptr_1679 + 12B], _1622
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	l16si	a2, a3, 14	# MEM[(const opus_int16 *)interpol_ptr_1679 + 14B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	l16si	a3, a3, 16	# MEM[(const opus_int16 *)interpol_ptr_1679 + 16B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a4, a4, a15	# tmp739, tmp736, tmp738
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	srai	a15, a14, 16	# tmp746,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	l32i.n	a14, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	s32i.n	a3, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	l32i.n	a3, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a4, a14	# tmp742, tmp739,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	mull	a4, a15, a7	# tmp747, tmp746, _1631
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	l32i.n	a14, a5, 24	# MEM[(opus_int32 *)buf_ptr_1685 + 24B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a3	# tmp745, tmp742,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	l32i.n	a3, a5, 28	# MEM[(opus_int32 *)buf_ptr_1685 + 28B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a4	# tmp748, tmp745, tmp747
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	l32i.n	a4, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	srai	a15, a14, 16	# tmp749,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	srai	a14, a3, 16	# tmp752,,
	mull	a14, a14, a4	#, tmp752,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	mull	a15, a15, a6	# tmp750, tmp749, _1622
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	s32i.n	a14, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	l32i.n	a14, a5, 32	# MEM[(opus_int32 *)buf_ptr_1685 + 32B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a15	# tmp751, tmp748, tmp750
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	srai	a4, a14, 16	# tmp755,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	l32i.n	a14, a5, 0	# *buf_ptr_1685,
	extui	a3, a14, 0, 16	# tmp758,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	l32i.n	a14, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	mull	a3, a3, a13	# tmp759, tmp758, _1675
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	mull	a4, a4, a14	# tmp756, tmp755,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	l32i.n	a14, a5, 4	# MEM[(opus_int32 *)buf_ptr_1685 + 4B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:62:                 res_Q6 = silk_SMULWB(         buf_ptr[ 0 ], interpol_ptr[ 0 ] );
	srai	a3, a3, 16	# tmp760, tmp759,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	extui	a13, a14, 0, 16	# tmp762,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	l32i.n	a14, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	mull	a13, a13, a12	# tmp763, tmp762, _1667
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a14	# tmp754, tmp751,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	l32i.n	a14, a5, 8	# MEM[(opus_int32 *)buf_ptr_1685 + 8B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a4	# tmp757, tmp754, tmp756
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	extui	a12, a14, 0, 16	# tmp766,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a3	# tmp761, tmp757, tmp760
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	l32i	a14, sp, 84	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	l32i.n	a3, a5, 16	# MEM[(opus_int32 *)buf_ptr_1685 + 16B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	l32i.n	a4, a5, 12	# MEM[(opus_int32 *)buf_ptr_1685 + 12B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	sub	a10, a14, a10	# tmp709,, interpol_ind
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	extui	a14, a3, 0, 16	# tmp774,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	extui	a15, a4, 0, 16	# tmp770,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	mull	a11, a12, a11	# tmp767, tmp766, _1658
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	mull	a8, a14, a8	# tmp775, tmp774, _1640
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	l32i.n	a14, a5, 20	# MEM[(opus_int32 *)buf_ptr_1685 + 20B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:63:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 1 ], interpol_ptr[ 1 ] );
	srai	a13, a13, 16	# tmp764, tmp763,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	mull	a9, a15, a9	# tmp771, tmp770, _1649
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	extui	a4, a14, 0, 16	# tmp778,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a13	# tmp765, tmp761, tmp764
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:64:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 2 ], interpol_ptr[ 2 ] );
	srai	a11, a11, 16	# tmp768, tmp767,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	mull	a7, a4, a7	# tmp779, tmp778, _1631
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	slli	a15, a10, 3	# tmp711, tmp709,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	l32i.n	a4, a5, 24	# MEM[(opus_int32 *)buf_ptr_1685 + 24B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a11	# tmp769, tmp765, tmp768
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:65:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 3 ], interpol_ptr[ 3 ] );
	srai	a9, a9, 16	# tmp772, tmp771,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	l32i	a11, sp, 176	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	add.n	a10, a15, a10	# tmp712, tmp711, tmp709
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a9	# tmp773, tmp769, tmp772
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:66:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 4 ], interpol_ptr[ 4 ] );
	srai	a8, a8, 16	# tmp776, tmp775,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	l32i.n	a9, a5, 28	# MEM[(opus_int32 *)buf_ptr_1685 + 28B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	extui	a3, a4, 0, 16	# tmp782,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a8	# tmp777, tmp773, tmp776
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:67:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 5 ], interpol_ptr[ 5 ] );
	srai	a4, a7, 16	# tmp780, tmp779,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	l32i.n	a8, a5, 32	# MEM[(opus_int32 *)buf_ptr_1685 + 32B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	slli	a10, a10, 1	# tmp713, tmp712,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:71:                 interpol_ptr = &FIR_Coefs[ RESAMPLER_DOWN_ORDER_FIR0 / 2 * ( FIR_Fracs - 1 - interpol_ind ) ];
	add.n	a10, a11, a10	# interpol_ptr,, tmp713
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i	a14, a5, 68	# MEM[(opus_int32 *)buf_ptr_1685 + 68B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a4	# tmp781, tmp777, tmp780
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	mull	a6, a3, a6	# tmp783, tmp782, _1622
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	l32i.n	a4, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	extui	a3, a9, 0, 16	# tmp786,,
	mull	a3, a3, a7	# tmp787, tmp786,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l16si	a9, a10, 0	# *interpol_ptr_1586,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	l16si	a7, a10, 2	# MEM[(const opus_int16 *)interpol_ptr_1586 + 2B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	extui	a11, a8, 0, 16	# tmp790,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	s32i.n	a14, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	mull	a11, a11, a4	# tmp791, tmp790,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	l32i	a14, a5, 64	# MEM[(opus_int32 *)buf_ptr_1685 + 64B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:68:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 6 ], interpol_ptr[ 6 ] );
	srai	a6, a6, 16	# tmp784, tmp783,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a8, a5, 60	# MEM[(opus_int32 *)buf_ptr_1685 + 60B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	s32i.n	a9, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	s32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i.n	a9, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a7, a2, a6	# tmp785, tmp781, tmp784
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:69:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 7 ], interpol_ptr[ 7 ] );
	srai	a6, a3, 16	# tmp788, tmp787,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l32i.n	a2, a5, 56	# MEM[(opus_int32 *)buf_ptr_1685 + 56B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	s32i.n	a14, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a6, a7, a6	# tmp789, tmp785, tmp788
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l16si	a14, a10, 4	# MEM[(const opus_int16 *)interpol_ptr_1586 + 4B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:70:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 8 ], interpol_ptr[ 8 ] );
	srai	a7, a11, 16	# tmp792, tmp791,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l16si	a11, a10, 6	# MEM[(const opus_int16 *)interpol_ptr_1586 + 6B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	s32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	srai	a8, a9, 16	# tmp794,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	l32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	mull	a3, a8, a4	# tmp795, tmp794,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	s32i.n	a2, sp, 28	# %sfp,
	s32i.n	a11, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	s32i.n	a14, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	l32i.n	a14, a5, 52	# MEM[(opus_int32 *)buf_ptr_1685 + 52B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	l32i.n	a4, sp, 40	# %sfp,
	srai	a8, a9, 16	# tmp797,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a7, a6, a7	# tmp793, tmp789, tmp792
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	mull	a2, a8, a4	# tmp798, tmp797,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a7, a7, a3	# tmp796, tmp793, tmp795
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l32i.n	a11, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	srai	a8, a6, 16	# tmp800,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	s32i.n	a14, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	mull	a6, a8, a9	# tmp801, tmp800,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a8, a7, a2	# tmp799, tmp796, tmp798
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	l32i.n	a4, a5, 48	# MEM[(opus_int32 *)buf_ptr_1685 + 48B], _1540
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	srai	a9, a11, 16	# tmp803,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	l32i.n	a11, sp, 20	# %sfp,
	l16si	a14, a10, 8	# MEM[(const opus_int16 *)interpol_ptr_1586 + 8B], _1546
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	l16si	a13, a10, 10	# MEM[(const opus_int16 *)interpol_ptr_1586 + 10B], _1537
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	l32i.n	a3, a5, 44	# MEM[(opus_int32 *)buf_ptr_1685 + 44B], _1531
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	mull	a9, a9, a2	# tmp804, tmp803,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	l16si	a12, a10, 12	# MEM[(const opus_int16 *)interpol_ptr_1586 + 12B], _1528
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	srai	a2, a4, 16	# tmp809, _1540,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	srai	a7, a11, 16	# tmp806,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a8, a8, a6	# tmp802, tmp799, tmp801
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	mull	a7, a7, a14	# tmp807, tmp806, _1546
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a8, a8, a9	# tmp805, tmp802, tmp804
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	mull	a9, a2, a13	# tmp810, tmp809, _1537
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	srai	a2, a3, 16	# tmp812, _1531,
	mull	a2, a2, a12	#, tmp812, _1528
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a8, a8, a7	# tmp808, tmp805, tmp807
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i.n	a7, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a8, a9	# tmp811, tmp808, tmp810
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	extui	a8, a7, 0, 16	# tmp821,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	l32i.n	a7, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	l32i.n	a6, a5, 40	# MEM[(opus_int32 *)buf_ptr_1685 + 40B], _1522
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a7	# tmp814, tmp811,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	l16si	a11, a10, 14	# MEM[(const opus_int16 *)interpol_ptr_1586 + 14B], _1519
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	mull	a8, a8, a7	#, tmp821,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	l32i.n	a5, a5, 36	# MEM[(opus_int32 *)buf_ptr_1685 + 36B], _1513
	l16si	a10, a10, 16	# MEM[(const opus_int16 *)interpol_ptr_1586 + 16B], _1510
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	srai	a15, a6, 16	# tmp815, _1522,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	mull	a15, a15, a11	# tmp816, tmp815, _1519
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	srai	a9, a5, 16	# tmp818, _1513,
	mull	a9, a9, a10	# tmp819, tmp818, _1510
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	extui	a7, a8, 0, 16	# tmp825,,
	l32i.n	a8, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a15	# tmp817, tmp814, tmp816
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	mull	a7, a7, a8	# tmp826, tmp825,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a9	# tmp820, tmp817, tmp819
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	l32i.n	a9, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	extui	a15, a8, 0, 16	# tmp829,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:72:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 17 ], interpol_ptr[ 0 ] );
	srai	a8, a9, 16	# tmp823,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a8	# tmp824, tmp820, tmp823
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	mull	a9, a15, a9	#, tmp829,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	s32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	l32i.n	a9, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:73:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 16 ], interpol_ptr[ 1 ] );
	srai	a7, a7, 16	# tmp827, tmp826,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	extui	a15, a9, 0, 16	# tmp833,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	l32i.n	a9, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a7	# tmp828, tmp824, tmp827
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	l32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	mull	a15, a15, a8	# tmp834, tmp833,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	extui	a8, a9, 0, 16	# tmp837,,
	mull	a14, a8, a14	# tmp838, tmp837, _1546
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:74:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 15 ], interpol_ptr[ 2 ] );
	srai	a9, a7, 16	# tmp831,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	extui	a4, a4, 0, 16	# tmp841, _1540,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a9	# tmp832, tmp828, tmp831
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:75:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 14 ], interpol_ptr[ 3 ] );
	srai	a15, a15, 16	# tmp835, tmp834,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	mull	a4, a4, a13	# tmp842, tmp841, _1537
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	extui	a3, a3, 0, 16	# tmp845, _1531,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a15	# tmp836, tmp832, tmp835
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:76:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 13 ], interpol_ptr[ 4 ] );
	srai	a14, a14, 16	# tmp839, tmp838,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	mull	a3, a3, a12	# tmp846, tmp845, _1528
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	extui	a6, a6, 0, 16	# tmp849, _1522,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a14	# tmp840, tmp836, tmp839
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:77:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 12 ], interpol_ptr[ 5 ] );
	srai	a4, a4, 16	# tmp843, tmp842,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	mull	a6, a6, a11	# tmp850, tmp849, _1519
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	extui	a5, a5, 0, 16	# tmp853, _1513,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:78:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 11 ], interpol_ptr[ 6 ] );
	srai	a3, a3, 16	# tmp847, tmp846,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a4	# tmp844, tmp840, tmp843
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	mull	a5, a5, a10	# tmp854, tmp853, _1510
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a3	# tmp848, tmp844, tmp847
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:79:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[ 10 ], interpol_ptr[ 7 ] );
	srai	a6, a6, 16	# tmp851, tmp850,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a6	# tmp852, tmp848, tmp851
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	srai	a5, a5, 16	# tmp855, tmp854,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:80:                 res_Q6 = silk_SMLAWB( res_Q6, buf_ptr[  9 ], interpol_ptr[ 8 ] );
	add.n	a2, a2, a5	# res_Q6, tmp852, tmp855
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 5	# tmp857, res_Q6,
	addi.n	a2, a2, 1	# tmp858, tmp857,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32i	a3, sp, 76	# %sfp, iftmp$4_1491
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 1	# _1493, tmp858,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	blt	a3, a2, .L9	# iftmp$4_1491, _1493,
	l32r	a3, .LC1	#, iftmp$4_1491
	blt	a2, a3, .L9	# _1493, tmp8,
	slli	a2, a2, 16	# tmp861, _1493,
	srai	a3, a2, 16	# iftmp$4_1491, tmp861,
.L9:
	l32i.n	a9, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i.n	a11, sp, 16	# %sfp,
	l32i	a14, sp, 120	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32i	a10, sp, 68	# %sfp,
	addi.n	a9, a9, 2	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	add.n	a11, a11, a14	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i	a2, sp, 112	# %sfp,
	s32i.n	a9, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:83:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	s16i	a3, a10, 0	# MEM[base: _1314, offset: 0B], iftmp$4_1491
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	s32i.n	a11, sp, 16	# %sfp,
	s32i	a9, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:53:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blt	a11, a2, .L10	#,,
	l32i	a12, sp, 88	# %sfp, _9
	j	.L6		#
.L12:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:89:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	l32i	a7, sp, 92	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:89:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	srai	a4, a13, 16	# tmp862, index_Q16,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:89:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	slli	a4, a4, 2	# tmp863, tmp862,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:89:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	add.n	a4, a7, a4	# buf_ptr,, tmp863
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	l32i	a3, a4, 92	# MEM[(opus_int32 *)buf_ptr_1473 + 92B], MEM[(opus_int32 *)buf_ptr_1473 + 92B]
	l32i.n	a10, a4, 0	# *buf_ptr_1473, *buf_ptr_1473
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	l32i	a8, a4, 84	# MEM[(opus_int32 *)buf_ptr_1473 + 84B], MEM[(opus_int32 *)buf_ptr_1473 + 84B]
	l32i.n	a5, a4, 8	# MEM[(opus_int32 *)buf_ptr_1473 + 8B], MEM[(opus_int32 *)buf_ptr_1473 + 8B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	l32i	a2, a4, 88	# MEM[(opus_int32 *)buf_ptr_1473 + 88B], MEM[(opus_int32 *)buf_ptr_1473 + 88B]
	l32i.n	a9, a4, 4	# MEM[(opus_int32 *)buf_ptr_1473 + 4B], MEM[(opus_int32 *)buf_ptr_1473 + 4B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	add.n	a10, a3, a10	#, MEM[(opus_int32 *)buf_ptr_1473 + 92B], *buf_ptr_1473
	s32i	a10, sp, 88	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	add.n	a5, a8, a5	#, MEM[(opus_int32 *)buf_ptr_1473 + 84B], MEM[(opus_int32 *)buf_ptr_1473 + 8B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	add.n	a9, a2, a9	#, MEM[(opus_int32 *)buf_ptr_1473 + 88B], MEM[(opus_int32 *)buf_ptr_1473 + 4B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	s32i	a5, sp, 64	# %sfp,
	l16si	a2, a12, 8	# MEM[(const opus_int16 *)_9 + 8B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	l32i	a5, sp, 88	# %sfp,
	l16si	a11, a12, 4	# MEM[(const opus_int16 *)_9 + 4B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	l16si	a14, a12, 6	# MEM[(const opus_int16 *)_9 + 6B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i	a15, a4, 80	# MEM[(opus_int32 *)buf_ptr_1473 + 80B], MEM[(opus_int32 *)buf_ptr_1473 + 80B]
	l32i.n	a10, a4, 12	# MEM[(opus_int32 *)buf_ptr_1473 + 12B], MEM[(opus_int32 *)buf_ptr_1473 + 12B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l32i.n	a7, a4, 16	# MEM[(opus_int32 *)buf_ptr_1473 + 16B], MEM[(opus_int32 *)buf_ptr_1473 + 16B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	srai	a3, a9, 16	# tmp912,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	s32i.n	a2, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	srai	a6, a5, 16	# tmp914,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l32i	a2, a4, 76	# MEM[(opus_int32 *)buf_ptr_1473 + 76B], MEM[(opus_int32 *)buf_ptr_1473 + 76B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	mull	a5, a3, a14	# tmp913, tmp912,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	mull	a6, a6, a11	# tmp915, tmp914,
	s32i	a11, sp, 84	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	s32i	a14, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	l32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l16si	a14, a12, 12	# MEM[(const opus_int16 *)_9 + 12B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l16si	a8, a12, 10	# MEM[(const opus_int16 *)_9 + 10B],
	add.n	a10, a15, a10	#, MEM[(opus_int32 *)buf_ptr_1473 + 80B], MEM[(opus_int32 *)buf_ptr_1473 + 12B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	add.n	a7, a2, a7	#, MEM[(opus_int32 *)buf_ptr_1473 + 76B], MEM[(opus_int32 *)buf_ptr_1473 + 16B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	srai	a3, a11, 16	# tmp917,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	s32i	a9, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i.n	a11, a4, 24	# MEM[(opus_int32 *)buf_ptr_1473 + 24B], MEM[(opus_int32 *)buf_ptr_1473 + 24B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i	a9, a4, 72	# MEM[(opus_int32 *)buf_ptr_1473 + 72B], MEM[(opus_int32 *)buf_ptr_1473 + 72B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	s32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	s32i.n	a14, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a10, a4, 20	# MEM[(opus_int32 *)buf_ptr_1473 + 20B], MEM[(opus_int32 *)buf_ptr_1473 + 20B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	s32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i	a7, a4, 68	# MEM[(opus_int32 *)buf_ptr_1473 + 68B], MEM[(opus_int32 *)buf_ptr_1473 + 68B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	l32i.n	a8, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	add.n	a10, a9, a10	#, MEM[(opus_int32 *)buf_ptr_1473 + 72B], MEM[(opus_int32 *)buf_ptr_1473 + 20B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	mull	a2, a3, a8	# tmp918, tmp917,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l16si	a3, a12, 14	# MEM[(const opus_int16 *)_9 + 14B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i.n	a14, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	s32i.n	a3, sp, 32	# %sfp,
	s32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a5, a6	# tmp916, tmp913, tmp915
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l32i.n	a10, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i.n	a6, sp, 48	# %sfp,
	srai	a8, a14, 16	# tmp920,,
	mull	a5, a8, a6	# tmp921, tmp920,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	srai	a8, a10, 16	# tmp923,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l16si	a6, a12, 16	# MEM[(const opus_int16 *)_9 + 16B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	s32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	mull	a6, a8, a10	# tmp924, tmp923,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	l16si	a8, a12, 18	# MEM[(const opus_int16 *)_9 + 18B],
	l32i	a9, a4, 64	# MEM[(opus_int32 *)buf_ptr_1473 + 64B], MEM[(opus_int32 *)buf_ptr_1473 + 64B]
	l32i.n	a14, a4, 28	# MEM[(opus_int32 *)buf_ptr_1473 + 28B], MEM[(opus_int32 *)buf_ptr_1473 + 28B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	add.n	a11, a7, a11	#, MEM[(opus_int32 *)buf_ptr_1473 + 68B], MEM[(opus_int32 *)buf_ptr_1473 + 24B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a2	# tmp919, tmp916, tmp918
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	s32i.n	a11, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	l32i.n	a7, a4, 60	# MEM[(opus_int32 *)buf_ptr_1473 + 60B], MEM[(opus_int32 *)buf_ptr_1473 + 60B]
	l32i.n	a11, a4, 32	# MEM[(opus_int32 *)buf_ptr_1473 + 32B], MEM[(opus_int32 *)buf_ptr_1473 + 32B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	s32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a8, a3, a5	# tmp922, tmp919, tmp921
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	l16si	a3, a12, 20	# MEM[(const opus_int16 *)_9 + 20B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	srai	a10, a2, 16	# tmp926,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	add.n	a2, a9, a14	# _1394, MEM[(opus_int32 *)buf_ptr_1473 + 64B], MEM[(opus_int32 *)buf_ptr_1473 + 28B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i.n	a14, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	add.n	a7, a7, a11	# _1383, MEM[(opus_int32 *)buf_ptr_1473 + 60B], MEM[(opus_int32 *)buf_ptr_1473 + 32B]
	s32i	a3, sp, 76	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	l32i.n	a11, a4, 56	# MEM[(opus_int32 *)buf_ptr_1473 + 56B],
	l32i.n	a3, a4, 36	# MEM[(opus_int32 *)buf_ptr_1473 + 36B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a8, a8, a6	# tmp925, tmp922, tmp924
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	mull	a10, a10, a9	# tmp927, tmp926,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	srai	a9, a14, 16	# tmp929,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a5, a4, 52	# MEM[(opus_int32 *)buf_ptr_1473 + 52B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	mull	a9, a9, a6	# tmp930, tmp929,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	add.n	a6, a11, a3	# _1372,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	l16si	a11, a12, 24	# MEM[(const opus_int16 *)_9 + 24B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	l16si	a14, a12, 22	# MEM[(const opus_int16 *)_9 + 22B], _1369
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a8, a8, a10	# tmp928, tmp925, tmp927
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	s32i	a5, sp, 108	# %sfp,
	s32i.n	a11, sp, 16	# %sfp,
	l32i.n	a5, a4, 40	# MEM[(opus_int32 *)buf_ptr_1473 + 40B], MEM[(opus_int32 *)buf_ptr_1473 + 40B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	l32i.n	a11, a4, 48	# MEM[(opus_int32 *)buf_ptr_1473 + 48B], MEM[(opus_int32 *)buf_ptr_1473 + 48B]
	l32i.n	a4, a4, 44	# MEM[(opus_int32 *)buf_ptr_1473 + 44B], MEM[(opus_int32 *)buf_ptr_1473 + 44B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	l32i.n	a3, sp, 20	# %sfp,
	srai	a15, a2, 16	# tmp932, _1394,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a9, a8, a9	# tmp931, tmp928, tmp930
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	l32i	a8, sp, 76	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	mull	a15, a15, a3	# tmp933, tmp932,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	srai	a10, a7, 16	# tmp935, _1383,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	l32i	a3, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	mull	a10, a10, a8	# tmp936, tmp935,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a9, a9, a15	# tmp934, tmp931, tmp933
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	add.n	a5, a3, a5	# _1361,, MEM[(opus_int32 *)buf_ptr_1473 + 40B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a9, a9, a10	# tmp937, tmp934, tmp936
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a10, sp, 16	# %sfp,
	srai	a8, a5, 16	# tmp941, _1361,
	mull	a8, a8, a10	#, tmp941,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	srai	a3, a6, 16	# tmp938, _1372,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	s32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	mull	a3, a3, a14	# tmp939, tmp938, _1369
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	l32i	a8, sp, 88	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a9, a3	# tmp940, tmp937, tmp939
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	extui	a10, a8, 0, 16	# tmp947,,
	l32i	a9, sp, 84	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	mull	a10, a10, a9	# tmp948, tmp947,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	extui	a9, a8, 0, 16	# tmp951,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	l32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a4, a11, a4	# _1350, MEM[(opus_int32 *)buf_ptr_1473 + 48B], MEM[(opus_int32 *)buf_ptr_1473 + 44B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a8	# tmp943, tmp940,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	l32i	a8, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	l16si	a11, a12, 26	# MEM[(const opus_int16 *)_9 + 26B], _1347
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	mull	a9, a9, a8	#, tmp951,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	srai	a15, a4, 16	# tmp944, _1350,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	s32i	a9, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	l32i	a9, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	mull	a15, a15, a11	# tmp945, tmp944, _1347
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	extui	a8, a9, 0, 16	# tmp955,,
	l32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a15	# tmp946, tmp943, tmp945
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	mull	a8, a8, a9	#, tmp955,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:92:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 23 ] ), FIR_Coefs[  0 ] );
	srai	a10, a10, 16	# tmp949, tmp948,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	s32i.n	a8, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a10	# tmp950, tmp946, tmp949
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i.n	a8, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	l32i	a10, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	extui	a15, a8, 0, 16	# tmp959,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:93:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 22 ] ), FIR_Coefs[  1 ] );
	srai	a9, a10, 16	# tmp953,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	l32i.n	a10, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	mull	a8, a15, a8	#, tmp959,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	extui	a15, a10, 0, 16	# tmp963,,
	l32i.n	a10, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a9	# tmp954, tmp950, tmp953
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	mull	a15, a15, a10	# tmp964, tmp963,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	l32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a10, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:94:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 21 ] ), FIR_Coefs[  2 ] );
	srai	a8, a9, 16	# tmp957,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	extui	a9, a10, 0, 16	# tmp967,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	l32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a8	# tmp958, tmp954, tmp957
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:95:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 20 ] ), FIR_Coefs[  3 ] );
	srai	a8, a10, 16	# tmp961,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a10, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a8	# tmp962, tmp958, tmp961
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	mull	a9, a9, a10	#, tmp967,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	s32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	l32i.n	a9, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:96:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 19 ] ), FIR_Coefs[  4 ] );
	srai	a15, a15, 16	# tmp965, tmp964,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	extui	a10, a9, 0, 16	# tmp971,,
	mull	a10, a10, a8	# tmp972, tmp971,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	l32i.n	a8, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a15	# tmp966, tmp962, tmp965
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:97:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 18 ] ), FIR_Coefs[  5 ] );
	srai	a9, a8, 16	# tmp969,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	l32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a9	# tmp970, tmp966, tmp969
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	extui	a2, a2, 0, 16	# tmp975, _1394,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	l32i	a9, sp, 76	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:98:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 17 ] ), FIR_Coefs[  6 ] );
	srai	a10, a10, 16	# tmp973, tmp972,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	mull	a2, a2, a8	# tmp976, tmp975,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	extui	a7, a7, 0, 16	# tmp979, _1383,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a10	# tmp974, tmp970, tmp973
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	mull	a7, a7, a9	# tmp980, tmp979,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	extui	a6, a6, 0, 16	# tmp983, _1372,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:99:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 16 ] ), FIR_Coefs[  7 ] );
	srai	a2, a2, 16	# tmp977, tmp976,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	mull	a6, a6, a14	# tmp984, tmp983, _1369
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	extui	a5, a5, 0, 16	# tmp987, _1361,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a3, a3, a2	# tmp978, tmp974, tmp977
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:100:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 15 ] ), FIR_Coefs[  8 ] );
	srai	a7, a7, 16	# tmp981, tmp980,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	mull	a5, a5, a10	# tmp988, tmp987,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	extui	a4, a4, 0, 16	# tmp991, _1350,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a2, a3, a7	# tmp982, tmp978, tmp981
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:101:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 14 ] ), FIR_Coefs[  9 ] );
	srai	a6, a6, 16	# tmp985, tmp984,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	mull	a11, a4, a11	# tmp992, tmp991, _1347
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a2, a2, a6	# tmp986, tmp982, tmp985
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:102:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 13 ] ), FIR_Coefs[ 10 ] );
	srai	a5, a5, 16	# tmp989, tmp988,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a2, a2, a5	# tmp990, tmp986, tmp989
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	srai	a11, a11, 16	# tmp993, tmp992,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:103:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 12 ] ), FIR_Coefs[ 11 ] );
	add.n	a2, a2, a11	# res_Q6, tmp990, tmp993
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 5	# tmp995, res_Q6,
	addi.n	a2, a2, 1	# tmp996, tmp995,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32r	a3, .LC0	#, iftmp$7_1325
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 1	# _1327, tmp996,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	blt	a3, a2, .L11	# tmp11, _1327,
	l32r	a3, .LC1	#, iftmp$7_1325
	blt	a2, a3, .L11	# _1327, iftmp$7_1325,
	slli	a2, a2, 16	# tmp999, _1327,
	srai	a3, a2, 16	# iftmp$7_1325, tmp999,
.L11:
	l32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32i	a2, sp, 100	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i	a7, sp, 120	# %sfp,
	addi.n	a14, a14, 2	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i	a8, sp, 112	# %sfp,
	s32i.n	a14, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:106:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	s16i	a3, a2, 0	# MEM[base: _423, offset: 0B], iftmp$7_1325
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	add.n	a13, a13, a7	# index_Q16, index_Q16,
	s32i	a14, sp, 100	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:87:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blt	a13, a8, .L12	# index_Q16,,
	j	.L6		#
.L14:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:112:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	l32i	a9, sp, 92	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:112:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	srai	a4, a13, 16	# tmp1000, index_Q16,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:112:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	slli	a4, a4, 2	# tmp1001, tmp1000,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:112:                 buf_ptr = buf + silk_RSHIFT( index_Q16, 16 );
	add.n	a4, a9, a4	# buf_ptr,, tmp1001
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	l32i	a7, a4, 136	# MEM[(opus_int32 *)buf_ptr_1307 + 136B], MEM[(opus_int32 *)buf_ptr_1307 + 136B]
	l32i.n	a3, a4, 4	# MEM[(opus_int32 *)buf_ptr_1307 + 4B], MEM[(opus_int32 *)buf_ptr_1307 + 4B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a2, a4, 140	# MEM[(opus_int32 *)buf_ptr_1307 + 140B], MEM[(opus_int32 *)buf_ptr_1307 + 140B]
	l32i.n	a8, a4, 0	# *buf_ptr_1307, *buf_ptr_1307
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	add.n	a3, a7, a3	#, MEM[(opus_int32 *)buf_ptr_1307 + 136B], MEM[(opus_int32 *)buf_ptr_1307 + 4B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	l32i	a15, a4, 132	# MEM[(opus_int32 *)buf_ptr_1307 + 132B], MEM[(opus_int32 *)buf_ptr_1307 + 132B]
	l32i.n	a5, a4, 8	# MEM[(opus_int32 *)buf_ptr_1307 + 8B], MEM[(opus_int32 *)buf_ptr_1307 + 8B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	s32i	a3, sp, 160	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i	a9, a4, 128	# MEM[(opus_int32 *)buf_ptr_1307 + 128B], MEM[(opus_int32 *)buf_ptr_1307 + 128B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	add.n	a8, a2, a8	#, MEM[(opus_int32 *)buf_ptr_1307 + 140B], *buf_ptr_1307
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i.n	a3, a4, 12	# MEM[(opus_int32 *)buf_ptr_1307 + 12B], MEM[(opus_int32 *)buf_ptr_1307 + 12B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	l32i	a2, sp, 160	# %sfp,
	l16si	a11, a12, 6	# MEM[(const opus_int16 *)_9 + 6B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	l16si	a14, a12, 8	# MEM[(const opus_int16 *)_9 + 8B],
	add.n	a5, a15, a5	#, MEM[(opus_int32 *)buf_ptr_1307 + 132B], MEM[(opus_int32 *)buf_ptr_1307 + 8B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l16si	a10, a12, 4	# MEM[(const opus_int16 *)_9 + 4B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l32i.n	a15, a4, 16	# MEM[(opus_int32 *)buf_ptr_1307 + 16B], MEM[(opus_int32 *)buf_ptr_1307 + 16B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	s32i	a8, sp, 168	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	s32i	a5, sp, 152	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l32i	a8, a4, 124	# MEM[(opus_int32 *)buf_ptr_1307 + 124B], MEM[(opus_int32 *)buf_ptr_1307 + 124B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	srai	a7, a2, 16	# tmp1074,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	add.n	a3, a9, a3	#, MEM[(opus_int32 *)buf_ptr_1307 + 128B], MEM[(opus_int32 *)buf_ptr_1307 + 12B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a5, sp, 168	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l16si	a6, a12, 10	# MEM[(const opus_int16 *)_9 + 10B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	s32i	a11, sp, 156	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	s32i	a14, sp, 148	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	s32i	a3, sp, 144	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l16si	a14, a12, 12	# MEM[(const opus_int16 *)_9 + 12B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	mull	a3, a7, a11	# tmp1075, tmp1074,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	l32i	a11, sp, 152	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	s32i	a10, sp, 164	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	add.n	a8, a8, a15	#, MEM[(opus_int32 *)buf_ptr_1307 + 124B], MEM[(opus_int32 *)buf_ptr_1307 + 16B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a9, a4, 120	# MEM[(opus_int32 *)buf_ptr_1307 + 120B], MEM[(opus_int32 *)buf_ptr_1307 + 120B]
	l32i.n	a10, a4, 20	# MEM[(opus_int32 *)buf_ptr_1307 + 20B], MEM[(opus_int32 *)buf_ptr_1307 + 20B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a7, sp, 164	# %sfp,
	srai	a2, a5, 16	# tmp1076,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	s32i	a6, sp, 140	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	s32i	a14, sp, 132	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	srai	a6, a11, 16	# tmp1079,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	s32i	a8, sp, 136	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i	a11, a4, 116	# MEM[(opus_int32 *)buf_ptr_1307 + 116B], MEM[(opus_int32 *)buf_ptr_1307 + 116B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	l32i	a5, sp, 148	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	mull	a2, a2, a7	# tmp1077, tmp1076,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	mull	a8, a6, a5	# tmp1080, tmp1079,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l16si	a7, a12, 14	# MEM[(const opus_int16 *)_9 + 14B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i	a6, sp, 144	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i.n	a14, a4, 24	# MEM[(opus_int32 *)buf_ptr_1307 + 24B], MEM[(opus_int32 *)buf_ptr_1307 + 24B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	s32i	a7, sp, 108	# %sfp,
	add.n	a10, a9, a10	#, MEM[(opus_int32 *)buf_ptr_1307 + 120B], MEM[(opus_int32 *)buf_ptr_1307 + 20B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a7, a3, a2	# tmp1078, tmp1075, tmp1077
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	srai	a5, a6, 16	# tmp1082,,
	l32i	a2, sp, 140	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l16si	a6, a12, 16	# MEM[(const opus_int16 *)_9 + 16B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a9, a4, 112	# MEM[(opus_int32 *)buf_ptr_1307 + 112B], MEM[(opus_int32 *)buf_ptr_1307 + 112B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	s32i	a10, sp, 128	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l32i	a3, sp, 136	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i.n	a10, a4, 28	# MEM[(opus_int32 *)buf_ptr_1307 + 28B], MEM[(opus_int32 *)buf_ptr_1307 + 28B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	add.n	a14, a11, a14	#, MEM[(opus_int32 *)buf_ptr_1307 + 116B], MEM[(opus_int32 *)buf_ptr_1307 + 24B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	mull	a5, a5, a2	# tmp1083, tmp1082,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i	a11, a4, 108	# MEM[(opus_int32 *)buf_ptr_1307 + 108B], MEM[(opus_int32 *)buf_ptr_1307 + 108B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	s32i	a6, sp, 88	# %sfp,
	s32i	a14, sp, 100	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a6, a7, a8	# tmp1081, tmp1078, tmp1080
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i.n	a14, a4, 32	# MEM[(opus_int32 *)buf_ptr_1307 + 32B], MEM[(opus_int32 *)buf_ptr_1307 + 32B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l32i	a7, sp, 132	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a8, sp, 128	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	add.n	a10, a9, a10	#, MEM[(opus_int32 *)buf_ptr_1307 + 112B], MEM[(opus_int32 *)buf_ptr_1307 + 28B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	srai	a2, a3, 16	# tmp1085,,
	mull	a2, a2, a7	# tmp1086, tmp1085,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	s32i	a10, sp, 84	# %sfp,
	l16si	a7, a12, 18	# MEM[(const opus_int16 *)_9 + 18B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a10, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	add.n	a14, a11, a14	#, MEM[(opus_int32 *)buf_ptr_1307 + 108B], MEM[(opus_int32 *)buf_ptr_1307 + 32B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a6, a6, a5	# tmp1084, tmp1081, tmp1083
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i	a5, sp, 100	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	srai	a3, a8, 16	# tmp1088,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	s32i	a14, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i	a14, sp, 88	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	s32i	a7, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	mull	a7, a3, a10	# tmp1089, tmp1088,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	srai	a3, a5, 16	# tmp1091,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i	a8, a4, 104	# MEM[(opus_int32 *)buf_ptr_1307 + 104B], MEM[(opus_int32 *)buf_ptr_1307 + 104B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	mull	a5, a3, a14	# tmp1092, tmp1091,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a9, a4, 36	# MEM[(opus_int32 *)buf_ptr_1307 + 36B], MEM[(opus_int32 *)buf_ptr_1307 + 36B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l16si	a10, a12, 20	# MEM[(const opus_int16 *)_9 + 20B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a3, sp, 84	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a11, a4, 40	# MEM[(opus_int32 *)buf_ptr_1307 + 40B], MEM[(opus_int32 *)buf_ptr_1307 + 40B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a6, a6, a2	# tmp1087, tmp1084, tmp1086
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	add.n	a9, a8, a9	#, MEM[(opus_int32 *)buf_ptr_1307 + 104B], MEM[(opus_int32 *)buf_ptr_1307 + 36B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	s32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	srai	a2, a3, 16	# tmp1094,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i	a10, a4, 100	# MEM[(opus_int32 *)buf_ptr_1307 + 100B], MEM[(opus_int32 *)buf_ptr_1307 + 100B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l16si	a14, a12, 22	# MEM[(const opus_int16 *)_9 + 22B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l16si	a3, a12, 24	# MEM[(const opus_int16 *)_9 + 24B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	s32i.n	a9, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i	a9, sp, 68	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	s32i.n	a3, sp, 44	# %sfp,
	add.n	a11, a10, a11	#, MEM[(opus_int32 *)buf_ptr_1307 + 100B], MEM[(opus_int32 *)buf_ptr_1307 + 40B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a3, a6, a7	# tmp1090, tmp1087, tmp1089
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i	a10, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	l32i	a6, a4, 96	# MEM[(opus_int32 *)buf_ptr_1307 + 96B], MEM[(opus_int32 *)buf_ptr_1307 + 96B]
	l32i.n	a7, a4, 44	# MEM[(opus_int32 *)buf_ptr_1307 + 44B], MEM[(opus_int32 *)buf_ptr_1307 + 44B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	s32i.n	a14, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	mull	a2, a2, a8	# tmp1095, tmp1094,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	srai	a15, a9, 16	# tmp1097,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	s32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a11, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	add.n	a7, a6, a7	#, MEM[(opus_int32 *)buf_ptr_1307 + 96B], MEM[(opus_int32 *)buf_ptr_1307 + 44B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a3, a3, a5	# tmp1093, tmp1090, tmp1092
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	mull	a5, a15, a10	# tmp1098, tmp1097,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	s32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	srai	a15, a11, 16	# tmp1100,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l32i	a7, a4, 88	# MEM[(opus_int32 *)buf_ptr_1307 + 88B], MEM[(opus_int32 *)buf_ptr_1307 + 88B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	l16si	a14, a12, 26	# MEM[(const opus_int16 *)_9 + 26B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l32i.n	a10, a4, 52	# MEM[(opus_int32 *)buf_ptr_1307 + 52B], MEM[(opus_int32 *)buf_ptr_1307 + 52B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a3, a3, a2	# tmp1096, tmp1093, tmp1095
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a11, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i	a8, a4, 92	# MEM[(opus_int32 *)buf_ptr_1307 + 92B], MEM[(opus_int32 *)buf_ptr_1307 + 92B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	mull	a2, a15, a6	# tmp1101, tmp1100,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a9, a4, 48	# MEM[(opus_int32 *)buf_ptr_1307 + 48B], MEM[(opus_int32 *)buf_ptr_1307 + 48B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a15, a3, a5	# tmp1099, tmp1096, tmp1098
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	add.n	a10, a7, a10	#, MEM[(opus_int32 *)buf_ptr_1307 + 88B], MEM[(opus_int32 *)buf_ptr_1307 + 52B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	s32i.n	a14, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l16si	a7, a12, 30	# MEM[(const opus_int16 *)_9 + 30B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	srai	a6, a11, 16	# tmp1103,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l16si	a14, a12, 28	# MEM[(const opus_int16 *)_9 + 28B],
	add.n	a9, a8, a9	#, MEM[(opus_int32 *)buf_ptr_1307 + 92B], MEM[(opus_int32 *)buf_ptr_1307 + 48B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	mull	a6, a6, a3	# tmp1104, tmp1103,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	l32i.n	a5, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	l32i.n	a11, a4, 56	# MEM[(opus_int32 *)buf_ptr_1307 + 56B], MEM[(opus_int32 *)buf_ptr_1307 + 56B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	s32i.n	a9, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	s32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	l32i	a9, a4, 84	# MEM[(opus_int32 *)buf_ptr_1307 + 84B], MEM[(opus_int32 *)buf_ptr_1307 + 84B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	l32i	a10, a4, 80	# MEM[(opus_int32 *)buf_ptr_1307 + 80B], MEM[(opus_int32 *)buf_ptr_1307 + 80B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	s32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a15, a15, a2	# tmp1102, tmp1099, tmp1101
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	s32i.n	a14, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	l32i.n	a14, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	srai	a8, a5, 16	# tmp1106,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a15, a15, a6	# tmp1105, tmp1102, tmp1104
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	mull	a2, a8, a14	# tmp1107, tmp1106,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	srai	a8, a3, 16	# tmp1109,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	add.n	a3, a9, a11	# _1151, MEM[(opus_int32 *)buf_ptr_1307 + 84B], MEM[(opus_int32 *)buf_ptr_1307 + 56B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	mull	a9, a8, a6	# tmp1110, tmp1109,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l32i.n	a8, sp, 24	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	l16si	a14, a12, 32	# MEM[(const opus_int16 *)_9 + 32B], _1148
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	srai	a7, a8, 16	# tmp1112,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	l32i.n	a8, a4, 60	# MEM[(opus_int32 *)buf_ptr_1307 + 60B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	l32i	a11, a4, 76	# MEM[(opus_int32 *)buf_ptr_1307 + 76B], MEM[(opus_int32 *)buf_ptr_1307 + 76B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	add.n	a6, a10, a8	# _1140, MEM[(opus_int32 *)buf_ptr_1307 + 80B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a8, a15, a2	# tmp1108, tmp1105, tmp1107
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	l16si	a10, a12, 34	# MEM[(const opus_int16 *)_9 + 34B],
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	mull	a7, a7, a2	# tmp1113, tmp1112,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	srai	a2, a3, 16	# tmp1115, _1151,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	s32i.n	a10, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	mull	a2, a2, a14	#, tmp1115, _1148
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a8, a8, a9	# tmp1111, tmp1108, tmp1110
	add.n	a8, a8, a7	# tmp1114, tmp1111, tmp1113
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	s32i	a2, sp, 188	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	srai	a2, a6, 16	# tmp1118, _1140,
	mull	a2, a2, a7	#, tmp1118,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	l32i	a9, sp, 188	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a7, sp, 168	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	s32i	a2, sp, 192	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a8, a9	# tmp1117, tmp1114,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	extui	a8, a7, 0, 16	# tmp1127,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	l32i	a7, sp, 192	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	l32i	a5, a4, 64	# MEM[(opus_int32 *)buf_ptr_1307 + 64B], MEM[(opus_int32 *)buf_ptr_1307 + 64B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a7	# tmp1120, tmp1117,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a7, sp, 164	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	l32i	a10, a4, 72	# MEM[(opus_int32 *)buf_ptr_1307 + 72B], MEM[(opus_int32 *)buf_ptr_1307 + 72B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	mull	a8, a8, a7	#, tmp1127,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	l32i	a4, a4, 68	# MEM[(opus_int32 *)buf_ptr_1307 + 68B], MEM[(opus_int32 *)buf_ptr_1307 + 68B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	s32i	a8, sp, 164	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	l32i	a8, sp, 160	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	add.n	a5, a11, a5	# _1129, MEM[(opus_int32 *)buf_ptr_1307 + 76B], MEM[(opus_int32 *)buf_ptr_1307 + 64B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	extui	a7, a8, 0, 16	# tmp1131,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	l16si	a11, a12, 36	# MEM[(const opus_int16 *)_9 + 36B], _1126
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	l32i	a8, sp, 156	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a4, a10, a4	# _1118, MEM[(opus_int32 *)buf_ptr_1307 + 72B], MEM[(opus_int32 *)buf_ptr_1307 + 68B]
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	srai	a15, a5, 16	# tmp1121, _1129,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	l16si	a10, a12, 38	# MEM[(const opus_int16 *)_9 + 38B], _1115
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	mull	a7, a7, a8	#, tmp1131,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	mull	a15, a15, a11	# tmp1122, tmp1121, _1126
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	srai	a9, a4, 16	# tmp1124, _1118,
	mull	a9, a9, a10	# tmp1125, tmp1124, _1115
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	s32i	a7, sp, 156	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a15	# tmp1123, tmp1120, tmp1122
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	l32i	a7, sp, 152	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a9	# tmp1126, tmp1123, tmp1125
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	l32i	a9, sp, 164	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	extui	a15, a7, 0, 16	# tmp1135,,
	l32i	a7, sp, 148	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:115:                 res_Q6 = silk_SMULWB(         silk_ADD32( buf_ptr[  0 ], buf_ptr[ 35 ] ), FIR_Coefs[  0 ] );
	srai	a8, a9, 16	# tmp1129,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	mull	a15, a15, a7	# tmp1136, tmp1135,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a8	# tmp1130, tmp1126, tmp1129
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i	a7, sp, 144	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	l32i	a8, sp, 156	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	extui	a9, a7, 0, 16	# tmp1139,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:116:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  1 ], buf_ptr[ 34 ] ), FIR_Coefs[  1 ] );
	srai	a7, a8, 16	# tmp1133,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i	a8, sp, 140	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a7	# tmp1134, tmp1130, tmp1133
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	mull	a9, a9, a8	#, tmp1139,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:117:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  2 ], buf_ptr[ 33 ] ), FIR_Coefs[  2 ] );
	srai	a7, a15, 16	# tmp1137, tmp1136,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	s32i	a9, sp, 140	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	l32i	a9, sp, 136	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a7, a2, a7	# tmp1138, tmp1134, tmp1137
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	extui	a8, a9, 0, 16	# tmp1143,,
	l32i	a9, sp, 132	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	l32i	a2, sp, 140	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	mull	a15, a8, a9	# tmp1144, tmp1143,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a9, sp, 128	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:119:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  4 ], buf_ptr[ 31 ] ), FIR_Coefs[  4 ] );
	srai	a15, a15, 16	# tmp1145, tmp1144,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	extui	a8, a9, 0, 16	# tmp1147,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:118:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  3 ], buf_ptr[ 32 ] ), FIR_Coefs[  3 ] );
	srai	a9, a2, 16	# tmp1141,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a7, a9	# tmp1142, tmp1138, tmp1141
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	mull	a8, a8, a2	#, tmp1147,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i	a7, sp, 88	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	s32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	l32i	a8, sp, 100	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a15	# tmp1146, tmp1142, tmp1145
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	extui	a2, a8, 0, 16	# tmp1151,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a8, sp, 84	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	mull	a2, a2, a7	# tmp1152, tmp1151,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	extui	a7, a8, 0, 16	# tmp1155,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	l32i	a8, sp, 108	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	extui	a3, a3, 0, 16	# tmp1183, _1151,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:120:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  5 ], buf_ptr[ 30 ] ), FIR_Coefs[  5 ] );
	srai	a15, a8, 16	# tmp1149,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a15	# tmp1150, tmp1146, tmp1149
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	mull	a7, a7, a8	#, tmp1155,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:121:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  6 ], buf_ptr[ 29 ] ), FIR_Coefs[  6 ] );
	srai	a15, a2, 16	# tmp1153, tmp1152,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	s32i	a7, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i	a7, sp, 68	# %sfp,
	l32i	a2, sp, 64	# %sfp,
	extui	a8, a7, 0, 16	# tmp1159,,
	mull	a8, a8, a2	#, tmp1159,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a7, sp, 60	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	s32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	extui	a2, a7, 0, 16	# tmp1163,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a7, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a15	# tmp1154, tmp1150, tmp1153
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	mull	a2, a2, a7	#, tmp1163,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:122:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  7 ], buf_ptr[ 28 ] ), FIR_Coefs[  7 ] );
	srai	a15, a8, 16	# tmp1157,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	extui	a8, a8, 0, 16	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	l32i	a2, sp, 64	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	s32i.n	a8, sp, 48	# %sfp,
	l32i.n	a7, sp, 48	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:123:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  8 ], buf_ptr[ 27 ] ), FIR_Coefs[  8 ] );
	srai	a8, a2, 16	# tmp1161,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a15	# tmp1158, tmp1154, tmp1157
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	mull	a7, a7, a2	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	l32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	s32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	l32i.n	a7, sp, 40	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a8	# tmp1162, tmp1158, tmp1161
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	extui	a15, a7, 0, 16	# tmp1171,,
	l32i.n	a7, sp, 36	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:124:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[  9 ], buf_ptr[ 26 ] ), FIR_Coefs[  9 ] );
	srai	a8, a2, 16	# tmp1165,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	mull	a15, a15, a7	# tmp1172, tmp1171,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a8	# tmp1166, tmp1162, tmp1165
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a7, sp, 32	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	extui	a2, a7, 0, 16	# tmp1175,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:125:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 10 ], buf_ptr[ 25 ] ), FIR_Coefs[ 10 ] );
	srai	a7, a8, 16	# tmp1169,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a8, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a7	# tmp1170, tmp1166, tmp1169
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	mull	a2, a2, a8	#, tmp1175,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	mull	a3, a3, a14	# tmp1184, tmp1183, _1148
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	l32i.n	a2, sp, 24	# %sfp,
	l32i.n	a7, sp, 20	# %sfp,
	extui	a8, a2, 0, 16	# tmp1179,,
	mull	a8, a8, a7	# tmp1180, tmp1179,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	l32i.n	a7, sp, 28	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:126:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 11 ], buf_ptr[ 24 ] ), FIR_Coefs[ 11 ] );
	srai	a15, a15, 16	# tmp1173, tmp1172,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	l32i.n	a14, sp, 16	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:127:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 12 ], buf_ptr[ 23 ] ), FIR_Coefs[ 12 ] );
	srai	a2, a7, 16	# tmp1177,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a15	# tmp1174, tmp1170, tmp1173
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	extui	a6, a6, 0, 16	# tmp1187, _1140,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a2	# tmp1178, tmp1174, tmp1177
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:128:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 13 ], buf_ptr[ 22 ] ), FIR_Coefs[ 13 ] );
	srai	a8, a8, 16	# tmp1181, tmp1180,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	mull	a6, a6, a14	# tmp1188, tmp1187,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	extui	a5, a5, 0, 16	# tmp1191, _1129,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:129:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 14 ], buf_ptr[ 21 ] ), FIR_Coefs[ 14 ] );
	srai	a3, a3, 16	# tmp1185, tmp1184,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a8	# tmp1182, tmp1178, tmp1181
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	mull	a5, a5, a11	# tmp1192, tmp1191, _1126
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	extui	a4, a4, 0, 16	# tmp1195, _1118,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a9, a9, a3	# tmp1186, tmp1182, tmp1185
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:130:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 15 ], buf_ptr[ 20 ] ), FIR_Coefs[ 15 ] );
	srai	a2, a6, 16	# tmp1189, tmp1188,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	mull	a4, a4, a10	# tmp1196, tmp1195, _1115
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a9, a2	# tmp1190, tmp1186, tmp1189
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:131:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 16 ], buf_ptr[ 19 ] ), FIR_Coefs[ 16 ] );
	srai	a5, a5, 16	# tmp1193, tmp1192,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a5	# tmp1194, tmp1190, tmp1193
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	srai	a4, a4, 16	# tmp1197, tmp1196,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:132:                 res_Q6 = silk_SMLAWB( res_Q6, silk_ADD32( buf_ptr[ 17 ], buf_ptr[ 18 ] ), FIR_Coefs[ 17 ] );
	add.n	a2, a2, a4	# res_Q6, tmp1194, tmp1197
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 5	# tmp1199, res_Q6,
	addi.n	a2, a2, 1	# tmp1200, tmp1199,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32i	a3, sp, 76	# %sfp, iftmp$10_1087
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	srai	a2, a2, 1	# _1089, tmp1200,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	blt	a3, a2, .L13	# iftmp$10_1087, _1089,
	l32r	a3, .LC1	#, iftmp$10_1087
	blt	a2, a3, .L13	# _1089, iftmp$10_1087,
	slli	a2, a2, 16	# tmp1203, _1089,
	srai	a3, a2, 16	# iftmp$10_1087, tmp1203,
.L13:
	l32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	l32i	a8, sp, 172	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i	a9, sp, 120	# %sfp,
	addi.n	a7, a7, 2	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	l32i	a10, sp, 112	# %sfp,
	s32i.n	a7, sp, 56	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:135:                 *out++ = (opus_int16)silk_SAT16( silk_RSHIFT_ROUND( res_Q6, 6 ) );
	s16i	a3, a8, 0	# MEM[base: _429, offset: 0B], iftmp$10_1087
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	add.n	a13, a13, a9	# index_Q16, index_Q16,
	s32i	a7, sp, 172	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:110:             for( index_Q16 = 0; index_Q16 < max_index_Q16; index_Q16 += index_increment_Q16 ) {
	blt	a13, a10, .L14	# index_Q16,,
.L6:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:180:         in += nSamplesIn;
	l32i	a11, sp, 72	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:181:         inLen -= nSamplesIn;
	l32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:180:         in += nSamplesIn;
	l32i	a7, sp, 124	# %sfp,
	slli	a2, a11, 1	# tmp1204,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:181:         inLen -= nSamplesIn;
	sub	a14, a14, a11	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:180:         in += nSamplesIn;
	add.n	a7, a7, a2	#,, tmp1204
	l32i	a8, sp, 92	# %sfp,
	l32i	a9, sp, 104	# %sfp,
	slli	a3, a11, 2	# tmp1205,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:181:         inLen -= nSamplesIn;
	s32i	a14, sp, 116	# %sfp,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:180:         in += nSamplesIn;
	s32i	a7, sp, 124	# %sfp,
	add.n	a3, a8, a3	# _1702,, tmp1205
	slli	a4, a9, 2	# _1704,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:183:         if( inLen > 1 ) {
	blti	a14, 2, .L15	#,,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:185:             silk_memcpy( buf, &buf[ nSamplesIn ], S->FIR_Order * sizeof( opus_int32 ) );
	mov.n	a2, a8	#,
	call0	memcpy		#
	l32i	a10, sp, 96	# %sfp,
	l32i	a5, a10, 296	# MEM[(struct silk_resampler_state_struct *)SS_37(D)].Coefs, pretmp_1699
	mov.n	a9, a10	#,
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:169:         nSamplesIn = silk_min( inLen, S->batchSize );
	j	.L16		#
.L15:
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:192:     silk_memcpy( S->sFIR.i32, &buf[ nSamplesIn ], S->FIR_Order * sizeof( opus_int32 ) );
	l32i	a2, sp, 180	# %sfp,
	call0	memcpy		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:193:     RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\silk\resampler_private_down_FIR.c:194: }
	l32i	a0, sp, 236	#,
	movi	a9, 0xf0	#,
	l32i	a12, sp, 232	#,
	l32i	a13, sp, 228	#,
	l32i	a14, sp, 224	#,
	l32i	a15, sp, 220	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	silk_resampler_private_down_FIR, .-silk_resampler_private_down_FIR
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
