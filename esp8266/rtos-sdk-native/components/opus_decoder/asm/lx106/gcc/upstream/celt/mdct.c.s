# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/mdct.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"mdct.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\mdct.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\mdct.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\mdct.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\mdct.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\mdct.c.s.raw
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
	.section	.text.clt_mdct_forward_c,"ax",@progbits
	.literal_position
	.literal .LC0, 1073741823
	.align	4
	.global	clt_mdct_forward_c
	.type	clt_mdct_forward_c, @function
# Function: clt_mdct_forward_c
# Module: upstream/celt/mdct.c
# Modified discrete cosine transform and overlap synthesis.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /* Forward MDCT trashes the input array */
# C context: #ifndef OVERRIDE_clt_mdct_forward
# C context: void clt_mdct_forward_c(const mdct_lookup *l, kiss_fft_scalar *in, kiss_fft_scalar * OPUS_RESTRICT out,
# C context: const opus_val16 *window, int overlap, int shift, int stride, int arch)
# C context: {
# C context: int i;
# C context: int N, N2, N4;
clt_mdct_forward_c:
	addi	sp, sp, -112	#,,
	s32i	a14, sp, 96	#,
	mov.n	a14, a2	# l, l
# @OPUS@\upstream\celt\mdct.c:126:    const kiss_fft_state *st = l->kfft[shift];
	slli	a2, a7, 2	# tmp340, shift,
	add.n	a2, a14, a2	# tmp341, l, tmp340
	l32i.n	a2, a2, 8	# *l_296(D).kfft,
# @OPUS@\upstream\celt\mdct.c:121: {
	s32i	a12, sp, 104	#,
# @OPUS@\upstream\celt\mdct.c:126:    const kiss_fft_state *st = l->kfft[shift];
	s32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\celt\mdct.c:132:    int scale_shift = st->scale_shift-1;
	l32i.n	a2, a2, 8	# *st_298.scale_shift, *st_298.scale_shift
# @OPUS@\upstream\celt\mdct.c:121: {
	s32i	a13, sp, 100	#,
# @OPUS@\upstream\celt\mdct.c:132:    int scale_shift = st->scale_shift-1;
	addi.n	a2, a2, -1	#, *st_298.scale_shift,
# @OPUS@\upstream\celt\mdct.c:121: {
	s32i	a15, sp, 92	#,
	s32i	a0, sp, 108	#,
# @OPUS@\upstream\celt\mdct.c:121: {
	mov.n	a15, a5	# window, window
	mov.n	a13, a7	# shift, shift
	mov.n	a12, a3	# in, in
	s32i.n	a4, sp, 24	# %sfp, out
	s32i.n	a6, sp, 32	# %sfp, overlap
# @OPUS@\upstream\celt\mdct.c:132:    int scale_shift = st->scale_shift-1;
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\mdct.c:134:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\celt\mdct.c:136:    scale = st->scale;
	l32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\celt\mdct.c:138:    N = l->n;
	l32i.n	a5, a14, 0	# *l_296(D).n, N
# @OPUS@\upstream\celt\mdct.c:136:    scale = st->scale;
	l16si	a2, a2, 4	# *st_298.scale,
# @OPUS@\upstream\celt\mdct.c:139:    trig = l->trig;
	l32i.n	a14, a14, 24	# *l_296(D).trig,
# @OPUS@\upstream\celt\mdct.c:134:    SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\mdct.c:136:    scale = st->scale;
	s32i.n	a2, sp, 56	# %sfp,
# @OPUS@\upstream\celt\mdct.c:139:    trig = l->trig;
	s32i.n	a14, sp, 48	# %sfp,
# @OPUS@\upstream\celt\mdct.c:140:    for (i=0;i<shift;i++)
	blti	a13, 1, .L2	# shift,,
# @OPUS@\upstream\celt\mdct.c:140:    for (i=0;i<shift;i++)
	movi.n	a2, 0	# i,
	mov.n	a3, a14	# trig,
.L3:
# @OPUS@\upstream\celt\mdct.c:142:       N >>= 1;
	srai	a5, a5, 1	# N, N,
# @OPUS@\upstream\celt\mdct.c:143:       trig += N;
	slli	a4, a5, 1	# tmp347, N,
# @OPUS@\upstream\celt\mdct.c:140:    for (i=0;i<shift;i++)
	addi.n	a2, a2, 1	# i, i,
# @OPUS@\upstream\celt\mdct.c:143:       trig += N;
	add.n	a3, a3, a4	# trig, trig, tmp347
# @OPUS@\upstream\celt\mdct.c:140:    for (i=0;i<shift;i++)
	bne	a13, a2, .L3	# shift, i,
	s32i.n	a3, sp, 48	# %sfp, trig
.L2:
# @OPUS@\upstream\celt\mdct.c:145:    N2 = N>>1;
	srai	a6, a5, 1	#, N,
# @OPUS@\upstream\celt\mdct.c:148:    ALLOC(f, N2, kiss_fft_scalar);
	mov.n	a2, a6	#,
# @OPUS@\upstream\celt\mdct.c:146:    N4 = N>>2;
	srai	a5, a5, 2	#, N,
# @OPUS@\upstream\celt\mdct.c:148:    ALLOC(f, N2, kiss_fft_scalar);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
# @OPUS@\upstream\celt\mdct.c:145:    N2 = N>>1;
	s32i.n	a6, sp, 40	# %sfp,
# @OPUS@\upstream\celt\mdct.c:146:    N4 = N>>2;
	s32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mdct.c:148:    ALLOC(f, N2, kiss_fft_scalar);
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 52	# %sfp,
# @OPUS@\upstream\celt\mdct.c:149:    ALLOC(f2, N4, kiss_fft_cpx);
	l32i.n	a2, sp, 28	# %sfp,
	movi.n	a3, 8	#,
	movi.n	a4, 1	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	l32i.n	a5, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	l32r	a3, .LC0	#, tmp350
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	srai	a7, a5, 1	# _7,,
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	l32i.n	a6, sp, 40	# %sfp,
	add.n	a3, a7, a3	# tmp349, _7, tmp350
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	addi.n	a9, a5, 3	# tmp354,,
# @OPUS@\upstream\celt\mdct.c:158:       const opus_val16 * OPUS_RESTRICT wp1 = window+(overlap>>1);
	slli	a10, a7, 1	# _16, _7,
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	add.n	a3, a3, a6	# tmp351, tmp349,
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	srai	a9, a9, 2	#, tmp354,
# @OPUS@\upstream\celt\mdct.c:159:       const opus_val16 * OPUS_RESTRICT wp2 = window+(overlap>>1)-1;
	addi	a14, a10, -2	# tmp353, _16,
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	slli	a7, a7, 2	# tmp348, _7,
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	slli	a3, a3, 2	# tmp352, tmp351,
# @OPUS@\upstream\celt\mdct.c:149:    ALLOC(f2, N4, kiss_fft_cpx);
	s32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	s32i.n	a9, sp, 16	# %sfp,
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	add.n	a7, a12, a7	# xp1, in, tmp348
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	add.n	a3, a12, a3	# xp2, in, tmp352
# @OPUS@\upstream\celt\mdct.c:158:       const opus_val16 * OPUS_RESTRICT wp1 = window+(overlap>>1);
	add.n	a10, a15, a10	# wp1, window, _16
# @OPUS@\upstream\celt\mdct.c:159:       const opus_val16 * OPUS_RESTRICT wp2 = window+(overlap>>1)-1;
	add.n	a14, a15, a14	# wp2, window, tmp353
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	blti	a9, 1, .L16	#,,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	slli	a4, a6, 2	# tmp357,,
	slli	a2, a9, 2	# tmp359,,
	l32i.n	a13, sp, 52	# %sfp, ivtmp$113
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	mov.n	a11, a7	# xp1, xp1
	s32i.n	a7, sp, 60	# %sfp, xp1
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	neg	a9, a4	# tmp358, tmp357
	add.n	a8, a10, a2	# _814, wp1, tmp359
# @OPUS@\upstream\celt\mdct.c:156:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+N2-1+(overlap>>1);
	mov.n	a12, a3	# xp2, xp2
# @OPUS@\upstream\celt\mdct.c:155:       const kiss_fft_scalar * OPUS_RESTRICT xp1 = in+(overlap>>1);
	mov.n	a7, a4	# _22, _22
	s32i	a3, sp, 64	# %sfp, xp2
	s32i	a15, sp, 68	# %sfp, window
.L5:
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	add.n	a3, a11, a7	# tmp362, xp1, _22
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	l32i.n	a2, a12, 0	# MEM[base: xp2_400, offset: 0B], _37
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	l32i.n	a3, a3, 0	# MEM[base: _819, offset: 0B], _24
	l16si	a5, a14, 0	# MEM[base: wp2_392, offset: 0B], _21
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	l16si	a6, a10, 0	# MEM[base: wp1_386, offset: 0B], _36
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	extui	a15, a3, 0, 16	# tmp365, _24,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	extui	a4, a2, 0, 16	# tmp368, _37,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	mull	a15, a15, a5	# tmp366, tmp365, _21
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	mull	a4, a4, a6	# tmp369, tmp368, _36
	srai	a2, a2, 16	# tmp372, _37,
	mull	a2, a2, a6	# tmp373, tmp372, _36
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	srai	a3, a3, 16	# tmp376, _24,
	srai	a15, a15, 15	# tmp367, tmp366,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	srai	a4, a4, 15	# tmp370, tmp369,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	mull	a3, a3, a5	# tmp377, tmp376, _21
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	add.n	a4, a15, a4	# tmp371, tmp367, tmp370
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	slli	a2, a2, 1	# tmp374, tmp373,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	add.n	a4, a4, a2	# tmp375, tmp371, tmp374
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	slli	a3, a3, 1	# tmp378, tmp377,
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	add.n	a4, a4, a3	# tmp379, tmp375, tmp378
# @OPUS@\upstream\celt\mdct.c:163:          *yp++ = MULT16_32_Q15(*wp2, xp1[N2]) + MULT16_32_Q15(*wp1,*xp2);
	s32i.n	a4, a13, 0	# MEM[base: _818, offset: 0B], tmp379
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	add.n	a2, a12, a9	# tmp380, xp2, tmp358
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	l32i.n	a4, a11, 0	# MEM[base: xp1_405, offset: 0B], _49
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	l32i.n	a3, a2, 0	# MEM[base: _817, offset: 0B], _62
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	srai	a15, a4, 16	# tmp381, _49,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	extui	a2, a3, 0, 16	# tmp384, _62,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	mull	a15, a15, a6	# tmp382, tmp381, _36
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	mull	a2, a2, a5	# tmp385, tmp384, _21
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	extui	a4, a4, 0, 16	# tmp388, _49,
	mull	a4, a4, a6	# tmp389, tmp388, _36
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	srai	a3, a3, 16	# tmp392, _62,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	slli	a15, a15, 1	# tmp383, tmp382,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	srai	a2, a2, 15	# tmp386, tmp385,
	mull	a3, a3, a5	# tmp393, tmp392, _21
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	sub	a15, a15, a2	# tmp387, tmp383, tmp386
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	srai	a4, a4, 15	# tmp390, tmp389,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	add.n	a4, a15, a4	# tmp391, tmp387, tmp390
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	slli	a3, a3, 1	# tmp394, tmp393,
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	sub	a3, a4, a3	# tmp395, tmp391, tmp394
# @OPUS@\upstream\celt\mdct.c:164:          *yp++ = MULT16_32_Q15(*wp1, *xp1)    - MULT16_32_Q15(*wp2, xp2[-N2]);
	s32i.n	a3, a13, 4	# MEM[base: _818, offset: 4B], tmp395
# @OPUS@\upstream\celt\mdct.c:167:          wp1+=2;
	addi.n	a10, a10, 4	# wp1, wp1,
# @OPUS@\upstream\celt\mdct.c:165:          xp1+=2;
	addi.n	a11, a11, 8	# xp1, xp1,
# @OPUS@\upstream\celt\mdct.c:166:          xp2-=2;
	addi	a12, a12, -8	# xp2, xp2,
# @OPUS@\upstream\celt\mdct.c:168:          wp2-=2;
	addi	a14, a14, -4	# wp2, wp2,
	addi.n	a13, a13, 8	# ivtmp$113, ivtmp$113,
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	bne	a10, a8, .L5	# wp1, _814,
	l32i.n	a4, sp, 16	# %sfp,
	l32i.n	a7, sp, 60	# %sfp, xp1
	l32i	a3, sp, 64	# %sfp, xp2
	l32i.n	a5, sp, 52	# %sfp,
	slli	a2, a4, 3	# _871,,
	l32i	a15, sp, 68	# %sfp, window
	add.n	a11, a5, a2	# yp,, _871
	add.n	a7, a7, a2	# xp1, xp1, _871
	sub	a3, a3, a2	# xp2, xp2, tmp398
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	l32i.n	a12, sp, 16	# %sfp, i
	j	.L4		#
.L16:
# @OPUS@\upstream\celt\mdct.c:157:       kiss_fft_scalar * OPUS_RESTRICT yp = f;
	l32i.n	a11, sp, 52	# %sfp, yp
# @OPUS@\upstream\celt\mdct.c:160:       for(i=0;i<((overlap+3)>>2);i++)
	movi.n	a12, 0	# i,
.L4:
# @OPUS@\upstream\celt\mdct.c:171:       wp2 = window+overlap-1;
	l32i.n	a6, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mdct.c:171:       wp2 = window+overlap-1;
	slli	a10, a6, 1	# tmp400,,
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\mdct.c:171:       wp2 = window+overlap-1;
	addi	a10, a10, -2	# tmp402, tmp400,
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	sub	a9, a5, a6	# _130,,
# @OPUS@\upstream\celt\mdct.c:171:       wp2 = window+overlap-1;
	add.n	a10, a15, a10	# wp2, window, tmp402
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	bge	a12, a9, .L6	# i, _130,
	mov.n	a2, a11	# ivtmp$99, yp
	mov.n	a6, a3	# xp2, xp2
	mov.n	a5, a7	# xp1, xp1
	mov.n	a4, a12	# i, i
.L7:
# @OPUS@\upstream\celt\mdct.c:175:          *yp++ = *xp2;
	l32i.n	a8, a6, 0	# MEM[base: xp2_397, offset: 0B], _80
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	addi.n	a4, a4, 1	# i, i,
# @OPUS@\upstream\celt\mdct.c:175:          *yp++ = *xp2;
	s32i.n	a8, a2, 0	# MEM[base: _824, offset: 0B], _80
# @OPUS@\upstream\celt\mdct.c:176:          *yp++ = *xp1;
	l32i.n	a8, a5, 0	# MEM[base: xp1_390, offset: 0B], _82
# @OPUS@\upstream\celt\mdct.c:178:          xp2-=2;
	addi	a6, a6, -8	# xp2, xp2,
# @OPUS@\upstream\celt\mdct.c:176:          *yp++ = *xp1;
	s32i.n	a8, a2, 4	# MEM[base: _824, offset: 4B], _82
# @OPUS@\upstream\celt\mdct.c:177:          xp1+=2;
	addi.n	a5, a5, 8	# xp1, xp1,
	addi.n	a2, a2, 8	# ivtmp$99, ivtmp$99,
# @OPUS@\upstream\celt\mdct.c:172:       for(;i<N4-((overlap+3)>>2);i++)
	bne	a9, a4, .L7	# _130, i,
	sub	a9, a9, a12	# _894, _130, i
	slli	a2, a9, 3	# _893, _894,
	add.n	a11, a11, a2	# yp, yp, _893
	add.n	a7, a7, a2	# xp1, xp1, _893
	sub	a3, a3, a2	# xp2, xp2, tmp405
	add.n	a12, a12, a9	# i, i, _894
.L6:
# @OPUS@\upstream\celt\mdct.c:180:       for(;i<N4;i++)
	l32i.n	a5, sp, 28	# %sfp,
	bge	a12, a5, .L8	# i,,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	l32i.n	a6, sp, 40	# %sfp,
	sub	a12, a5, a12	# tmp411,, i
	slli	a13, a6, 2	# tmp409,,
	slli	a12, a12, 2	# tmp412, tmp411,
	neg	a13, a13	# tmp410, tmp409
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	slli	a14, a6, 2	# _125,,
	add.n	a12, a15, a12	# _829, window, tmp412
.L9:
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	add.n	a2, a7, a13	# tmp417, xp1, tmp410
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	l32i.n	a8, a3, 0	# MEM[base: xp2_389, offset: 0B], _87
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	l32i.n	a2, a2, 0	# MEM[base: _836, offset: 0B], _102
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	l16si	a6, a10, 0	# MEM[base: wp2_398, offset: 0B], _86
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	l16si	a5, a15, 0	# MEM[base: wp1_382, offset: 0B], _99
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	srai	a4, a8, 16	# tmp418, _87,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	extui	a9, a2, 0, 16	# tmp421, _102,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	mull	a4, a4, a6	# tmp419, tmp418, _86
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	mull	a9, a9, a5	# tmp422, tmp421, _99
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	extui	a8, a8, 0, 16	# tmp425, _87,
	mull	a8, a8, a6	# tmp426, tmp425, _86
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	srai	a2, a2, 16	# tmp429, _102,
	srai	a9, a9, 15	# tmp423, tmp422,
	mull	a2, a2, a5	# tmp430, tmp429, _99
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	slli	a4, a4, 1	# tmp420, tmp419,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	sub	a4, a4, a9	# tmp424, tmp420, tmp423
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	srai	a8, a8, 15	# tmp427, tmp426,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	add.n	a4, a4, a8	# tmp428, tmp424, tmp427
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	slli	a2, a2, 1	# tmp431, tmp430,
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	sub	a4, a4, a2	# tmp432, tmp428, tmp431
# @OPUS@\upstream\celt\mdct.c:183:          *yp++ =  -MULT16_32_Q15(*wp1, xp1[-N2]) + MULT16_32_Q15(*wp2, *xp2);
	s32i.n	a4, a11, 0	# MEM[base: _835, offset: 0B], tmp432
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	add.n	a2, a3, a14	# tmp433, xp2, _125
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	l32i.n	a9, a7, 0	# MEM[base: xp1_394, offset: 0B], _114
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	l32i.n	a8, a2, 0	# MEM[base: _834, offset: 0B], _127
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	extui	a2, a9, 0, 16	# tmp434, _114,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	extui	a4, a8, 0, 16	# tmp437, _127,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	mull	a2, a2, a6	# tmp435, tmp434, _86
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	mull	a4, a4, a5	# tmp438, tmp437, _99
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	srai	a9, a9, 16	# tmp441, _114,
	mull	a6, a9, a6	# tmp442, tmp441, _86
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	srai	a8, a8, 16	# tmp445, _127,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	srai	a2, a2, 15	# tmp436, tmp435,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	srai	a4, a4, 15	# tmp439, tmp438,
	mull	a5, a8, a5	# tmp446, tmp445, _99
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	add.n	a2, a2, a4	# tmp440, tmp436, tmp439
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	slli	a6, a6, 1	# tmp443, tmp442,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	add.n	a2, a2, a6	# tmp444, tmp440, tmp443
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	slli	a5, a5, 1	# tmp447, tmp446,
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	add.n	a2, a2, a5	# tmp448, tmp444, tmp447
# @OPUS@\upstream\celt\mdct.c:184:          *yp++ = MULT16_32_Q15(*wp2, *xp1)     + MULT16_32_Q15(*wp1, xp2[N2]);
	s32i.n	a2, a11, 4	# MEM[base: _835, offset: 4B], tmp448
# @OPUS@\upstream\celt\mdct.c:187:          wp1+=2;
	addi.n	a15, a15, 4	# window, window,
# @OPUS@\upstream\celt\mdct.c:185:          xp1+=2;
	addi.n	a7, a7, 8	# xp1, xp1,
# @OPUS@\upstream\celt\mdct.c:186:          xp2-=2;
	addi	a3, a3, -8	# xp2, xp2,
# @OPUS@\upstream\celt\mdct.c:188:          wp2-=2;
	addi	a10, a10, -4	# wp2, wp2,
	addi.n	a11, a11, 8	# ivtmp$81, ivtmp$81,
# @OPUS@\upstream\celt\mdct.c:180:       for(;i<N4;i++)
	bne	a15, a12, .L9	# window, _829,
.L11:
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	l32i.n	a5, sp, 20	# %sfp,
	movi.n	a15, 1	# tmp449,
	l32i.n	a4, sp, 28	# %sfp,
	ssl	a5	#
	sll	a15, a15	# tmp450, tmp449
	l32i.n	a6, sp, 44	# %sfp,
	srai	a15, a15, 1	# _193, tmp450,
	slli	a4, a4, 1	#,,
	l32i.n	a11, sp, 52	# %sfp, ivtmp$63
	l32i.n	a10, sp, 48	# %sfp, ivtmp$64
	l32i.n	a14, a6, 48	# *st_298.bitrev, ivtmp$66
	s32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	movi.n	a13, 0	# i,
	s32i.n	a15, sp, 16	# %sfp, _193
	l32i.n	a12, sp, 56	# %sfp, scale
	j	.L10		#
.L8:
# @OPUS@\upstream\celt\mdct.c:195:       for(i=0;i<N4;i++)
	blti	a5, 1, .L23	#,,
	j	.L11		#
.L10:
# @OPUS@\upstream\celt\mdct.c:201:          t1 = t[N4+i];
	l32i.n	a6, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:202:          re = *yp++;
	l32i.n	a2, a11, 0	# MEM[base: _842, offset: 0B], re
# @OPUS@\upstream\celt\mdct.c:203:          im = *yp++;
	l32i.n	a5, a11, 4	# MEM[base: _842, offset: 4B], im
# @OPUS@\upstream\celt\mdct.c:201:          t1 = t[N4+i];
	add.n	a3, a10, a6	# tmp453, ivtmp$64,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	l16si	a4, a10, 0	# MEM[base: _847, offset: 0B], _148
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	l16si	a9, a3, 0	# MEM[base: _843, offset: 0B], _159
	extui	a6, a5, 0, 16	# _347, im,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	srai	a3, a2, 16	# _149, re,
	extui	a2, a2, 0, 16	# _345, re,
	mull	a15, a4, a3	# tmp456, _148, _149
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	srai	a5, a5, 16	# _160, im,
	mull	a8, a9, a6	# tmp458, _159, _347
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	mull	a7, a9, a2	# tmp468, _159, _345
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	mull	a6, a4, a6	# tmp466, _148, _347
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	mull	a2, a4, a2	# tmp461, _148, _345
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	mull	a4, a4, a5	# tmp471, _148, _160
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	srai	a7, a7, 15	# tmp469, tmp468,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	slli	a15, a15, 1	# tmp457, tmp456,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	srai	a8, a8, 15	# tmp459, tmp458,
	mull	a5, a9, a5	# tmp464, _159, _160
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	srai	a6, a6, 15	# tmp467, tmp466,
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	mull	a3, a3, a9	# tmp474, _149, _159
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	add.n	a6, a6, a7	# tmp470, tmp467, tmp469
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	slli	a4, a4, 1	# tmp472, tmp471,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	sub	a8, a15, a8	# tmp460, tmp457, tmp459
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	srai	a2, a2, 15	# tmp462, tmp461,
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	add.n	a6, a6, a4	# tmp473, tmp470, tmp472
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	slli	a5, a5, 1	# tmp465, tmp464,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	add.n	a2, a8, a2	# tmp463, tmp460, tmp462
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	slli	a3, a3, 1	# tmp475, tmp474,
# @OPUS@\upstream\celt\mdct.c:204:          yr = S_MUL(re,t0)  -  S_MUL(im,t1);
	sub	a2, a2, a5	# yr, tmp463, tmp465
# @OPUS@\upstream\celt\mdct.c:205:          yi = S_MUL(im,t0)  +  S_MUL(re,t1);
	add.n	a3, a6, a3	# yi, tmp473, tmp475
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	extui	a4, a3, 0, 16	# tmp488, yi,
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	extui	a6, a2, 0, 16	# tmp480, yr,
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	srai	a3, a3, 16	# tmp491, yi,
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	srai	a2, a2, 16	# tmp483, yr,
	l32i.n	a5, sp, 16	# %sfp,
	mull	a2, a2, a12	# tmp484, tmp483, scale
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	mull	a3, a3, a12	# tmp492, tmp491, scale
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	l16si	a7, a14, 0	# MEM[base: _841, offset: 0B], tmp476
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	add.n	a2, a2, a5	# tmp485, tmp484,
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	add.n	a3, a3, a5	# tmp493, tmp492,
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	mull	a6, a6, a12	# tmp481, tmp480, scale
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	l32i.n	a5, sp, 36	# %sfp,
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	mull	a4, a4, a12	# tmp489, tmp488, scale
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	slli	a7, a7, 3	# tmp479, tmp476,
	add.n	a7, a5, a7	# _210,, tmp479
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	srai	a6, a6, 16	# tmp482, tmp481,
	l32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	srai	a4, a4, 16	# tmp490, tmp489,
# @OPUS@\upstream\celt\mdct.c:208:          yc.r = PSHR32(MULT16_32_Q16(scale, yc.r), scale_shift);
	add.n	a6, a6, a2	# tmp486, tmp482, tmp485
	ssr	a5	#
	sra	a6, a6	# tmp487, tmp486
# @OPUS@\upstream\celt\mdct.c:209:          yc.i = PSHR32(MULT16_32_Q16(scale, yc.i), scale_shift);
	add.n	a4, a4, a3	# tmp494, tmp490, tmp493
	ssr	a5	#
	sra	a4, a4	# tmp495, tmp494
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	s32i.n	a6, a7, 0	# MEM[(struct kiss_fft_cpx *)_210], tmp487
# @OPUS@\upstream\celt\mdct.c:195:       for(i=0;i<N4;i++)
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mdct.c:210:          f2[st->bitrev[i]] = yc;
	s32i.n	a4, a7, 4	# MEM[(struct kiss_fft_cpx *)_210 + 4B], tmp495
# @OPUS@\upstream\celt\mdct.c:195:       for(i=0;i<N4;i++)
	addi.n	a13, a13, 1	# i, i,
	addi.n	a11, a11, 8	# ivtmp$63, ivtmp$63,
	addi.n	a10, a10, 2	# ivtmp$64, ivtmp$64,
	addi.n	a14, a14, 2	# ivtmp$66, ivtmp$66,
# @OPUS@\upstream\celt\mdct.c:195:       for(i=0;i<N4;i++)
	blt	a13, a6, .L10	# i,,
	j	.L24		#
.L14:
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	l32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	l32i.n	a2, a13, 4	# MEM[base: fp_401, offset: 4B], _221
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	l32i.n	a10, a13, 0	# MEM[base: fp_401, offset: 0B], _237
	add.n	a4, a6, a3	# tmp498, ivtmp$54,
	l16si	a11, a4, 0	# MEM[base: _857, offset: 0B], _236
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	l16si	a3, a6, 0	# MEM[base: _861, offset: 0B], _220
	srai	a4, a2, 16	# _222, _221,
	extui	a5, a10, 0, 16	# _318, _237,
	mull	a15, a3, a4	# tmp501, _220, _222
	extui	a2, a2, 0, 16	# _304, _221,
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	mull	a9, a11, a5	# tmp503, _236, _318
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	mull	a8, a3, a2	# tmp506, _220, _304
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	srai	a10, a10, 16	# _238, _237,
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	mull	a5, a3, a5	# tmp512, _220, _318
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	mull	a2, a11, a2	# tmp514, _236, _304
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	slli	a15, a15, 1	# tmp502, tmp501,
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	srai	a9, a9, 15	# tmp504, tmp503,
	mull	a7, a11, a10	# tmp509, _236, _238
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	mull	a3, a3, a10	# tmp517, _220, _238
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	srai	a2, a2, 15	# tmp515, tmp514,
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	sub	a9, a15, a9	# tmp505, tmp502, tmp504
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	srai	a8, a8, 15	# tmp507, tmp506,
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	srai	a5, a5, 15	# tmp513, tmp512,
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	mull	a4, a4, a11	# tmp520, _222, _236
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	add.n	a5, a5, a2	# tmp516, tmp513, tmp515
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	slli	a3, a3, 1	# tmp518, tmp517,
# @OPUS@\upstream\celt\mdct.c:230:          *yp1 = yr;
	l32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	add.n	a9, a9, a8	# tmp508, tmp505, tmp507
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	slli	a7, a7, 1	# tmp510, tmp509,
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	add.n	a5, a5, a3	# tmp519, tmp516, tmp518
# @OPUS@\upstream\celt\mdct.c:228:          yr = S_MUL(fp->i,t[N4+i]) - S_MUL(fp->r,t[i]);
	sub	a9, a9, a7	# yr, tmp508, tmp510
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	slli	a4, a4, 1	# tmp521, tmp520,
# @OPUS@\upstream\celt\mdct.c:233:          yp1 += 2*stride;
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:229:          yi = S_MUL(fp->r,t[N4+i]) + S_MUL(fp->i,t[i]);
	add.n	a4, a5, a4	# yi, tmp519, tmp521
# @OPUS@\upstream\celt\mdct.c:230:          *yp1 = yr;
	s32i.n	a9, a2, 0	# MEM[base: yp1_403, offset: 0B], yr
# @OPUS@\upstream\celt\mdct.c:231:          *yp2 = yi;
	s32i.n	a4, a12, 0	# MEM[base: yp2_385, offset: 0B], yi
# @OPUS@\upstream\celt\mdct.c:233:          yp1 += 2*stride;
	add.n	a2, a2, a3	#,,
# @OPUS@\upstream\celt\mdct.c:234:          yp2 -= 2*stride;
	l32i.n	a4, sp, 20	# %sfp,
# @OPUS@\upstream\celt\mdct.c:225:       for(i=0;i<N4;i++)
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mdct.c:225:       for(i=0;i<N4;i++)
	addi.n	a14, a14, 1	# i, i,
# @OPUS@\upstream\celt\mdct.c:233:          yp1 += 2*stride;
	s32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\celt\mdct.c:232:          fp++;
	addi.n	a13, a13, 8	# f2, f2,
# @OPUS@\upstream\celt\mdct.c:234:          yp2 -= 2*stride;
	add.n	a12, a12, a4	# yp2, yp2,
	addi.n	a6, a6, 2	# ivtmp$54, ivtmp$54,
# @OPUS@\upstream\celt\mdct.c:225:       for(i=0;i<N4;i++)
	blt	a14, a5, .L14	# i,,
.L15:
# @OPUS@\upstream\celt\mdct.c:237:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\mdct.c:238: }
	l32i	a0, sp, 108	#,
	l32i	a12, sp, 104	#,
	l32i	a13, sp, 100	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
.L23:
# @OPUS@\upstream\celt\mdct.c:215:    opus_fft_impl(st, f2);
	l32i.n	a3, sp, 36	# %sfp,
	l32i.n	a2, sp, 44	# %sfp,
	call0	opus_fft_impl		#
	j	.L15		#
.L24:
	l32i.n	a3, sp, 36	# %sfp,
	l32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\celt\mdct.c:225:       for(i=0;i<N4;i++)
	movi.n	a14, 0	# i,
# @OPUS@\upstream\celt\mdct.c:215:    opus_fft_impl(st, f2);
	call0	opus_fft_impl		#
# @OPUS@\upstream\celt\mdct.c:222:       kiss_fft_scalar * OPUS_RESTRICT yp2 = out+stride*(N2-1);
	l32i	a5, sp, 112	# stride,
	l32i.n	a6, sp, 40	# %sfp,
# @OPUS@\upstream\celt\mdct.c:233:          yp1 += 2*stride;
	slli	a15, a5, 3	# _263,,
# @OPUS@\upstream\celt\mdct.c:222:       kiss_fft_scalar * OPUS_RESTRICT yp2 = out+stride*(N2-1);
	addi.n	a12, a6, -1	# tmp523,,
	l32i.n	a6, sp, 28	# %sfp,
	mull	a12, a12, a5	# tmp524, tmp523,
# @OPUS@\upstream\celt\mdct.c:234:          yp2 -= 2*stride;
	neg	a4, a15	#, _263
	slli	a2, a6, 1	# tmp528,,
# @OPUS@\upstream\celt\mdct.c:222:       kiss_fft_scalar * OPUS_RESTRICT yp2 = out+stride*(N2-1);
	l32i.n	a3, sp, 24	# %sfp,
# @OPUS@\upstream\celt\mdct.c:234:          yp2 -= 2*stride;
	s32i.n	a4, sp, 20	# %sfp,
	l32i.n	a5, sp, 48	# %sfp,
	l32i.n	a4, sp, 32	# %sfp,
# @OPUS@\upstream\celt\mdct.c:222:       kiss_fft_scalar * OPUS_RESTRICT yp2 = out+stride*(N2-1);
	slli	a12, a12, 2	# tmp525, tmp524,
	neg	a2, a2	#, tmp528
# @OPUS@\upstream\celt\mdct.c:222:       kiss_fft_scalar * OPUS_RESTRICT yp2 = out+stride*(N2-1);
	add.n	a12, a3, a12	# yp2,, tmp525
	add.n	a6, a5, a4	# ivtmp$54,,
	s32i.n	a2, sp, 16	# %sfp,
	s32i.n	a15, sp, 32	# %sfp, _263
	l32i.n	a13, sp, 36	# %sfp, f2
	j	.L14		#
	.size	clt_mdct_forward_c, .-clt_mdct_forward_c
	.section	.text.clt_mdct_backward_c,"ax",@progbits
	.literal_position
	.literal .LC2, 1073741822
	.align	4
	.global	clt_mdct_backward_c
	.type	clt_mdct_backward_c, @function
# Function: clt_mdct_backward_c
# Module: upstream/celt/mdct.c
# Modified discrete cosine transform and overlap synthesis.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif /* OVERRIDE_clt_mdct_forward */
# C context:
# C context: #ifndef OVERRIDE_clt_mdct_backward
# C context: void clt_mdct_backward_c(const mdct_lookup *l, kiss_fft_scalar *in, kiss_fft_scalar * OPUS_RESTRICT out,
# C context: const opus_val16 * OPUS_RESTRICT window, int overlap, int shift, int stride, int arch)
# C context: {
# C context: int i;
# C context: int N, N2, N4;
clt_mdct_backward_c:
	addi	sp, sp, -96	#,,
	s32i.n	a5, sp, 60	# %sfp, window
# @OPUS@\upstream\celt\mdct.c:251:    trig = l->trig;
	l32i.n	a5, a2, 24	# *l_248(D).trig,
# @OPUS@\upstream\celt\mdct.c:244: {
	s32i.n	a4, sp, 44	# %sfp, out
	s32i	a0, sp, 92	#,
	s32i	a12, sp, 88	#,
	s32i	a13, sp, 84	#,
	s32i	a14, sp, 80	#,
	s32i	a15, sp, 76	#,
# @OPUS@\upstream\celt\mdct.c:244: {
	s32i.n	a6, sp, 36	# %sfp, overlap
# @OPUS@\upstream\celt\mdct.c:251:    trig = l->trig;
	s32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\mdct.c:244: {
	l32i	a4, sp, 96	# stride, stride
# @OPUS@\upstream\celt\mdct.c:250:    N = l->n;
	l32i.n	a9, a2, 0	# *l_248(D).n, N
# @OPUS@\upstream\celt\mdct.c:252:    for (i=0;i<shift;i++)
	blti	a7, 1, .L28	# shift,,
	mov.n	a6, a5	# trig,
# @OPUS@\upstream\celt\mdct.c:252:    for (i=0;i<shift;i++)
	movi.n	a5, 0	# i,
.L29:
# @OPUS@\upstream\celt\mdct.c:254:       N >>= 1;
	srai	a9, a9, 1	# N, N,
# @OPUS@\upstream\celt\mdct.c:255:       trig += N;
	slli	a8, a9, 1	# tmp342, N,
# @OPUS@\upstream\celt\mdct.c:252:    for (i=0;i<shift;i++)
	addi.n	a5, a5, 1	# i, i,
# @OPUS@\upstream\celt\mdct.c:255:       trig += N;
	add.n	a6, a6, a8	# trig, trig, tmp342
# @OPUS@\upstream\celt\mdct.c:252:    for (i=0;i<shift;i++)
	bne	a7, a5, .L29	# shift, i,
	s32i.n	a6, sp, 48	# %sfp, trig
.L28:
# @OPUS@\upstream\celt\mdct.c:257:    N2 = N>>1;
	srai	a6, a9, 1	#, N,
	s32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\mdct.c:265:       kiss_fft_scalar * OPUS_RESTRICT yp = out+(overlap>>1);
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\mdct.c:264:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+stride*(N2-1);
	l32i.n	a10, sp, 52	# %sfp,
# @OPUS@\upstream\celt\mdct.c:265:       kiss_fft_scalar * OPUS_RESTRICT yp = out+(overlap>>1);
	srai	a6, a8, 1	# _8,,
# @OPUS@\upstream\celt\mdct.c:264:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+stride*(N2-1);
	addi.n	a8, a10, -1	# tmp343,,
	mull	a8, a8, a4	# tmp344, tmp343, stride
	l32r	a5, .LC2	#, tmp350
	slli	a8, a8, 2	# tmp345, tmp344,
	add.n	a5, a6, a5	# tmp349, _8, tmp350
# @OPUS@\upstream\celt\mdct.c:264:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+stride*(N2-1);
	add.n	a8, a3, a8	#, in, tmp345
	slli	a7, a7, 2	# tmp347, shift,
	add.n	a7, a2, a7	#, l, tmp347
# @OPUS@\upstream\celt\mdct.c:258:    N4 = N>>2;
	srai	a9, a9, 2	#, N,
	add.n	a5, a5, a10	# tmp351, tmp349,
# @OPUS@\upstream\celt\mdct.c:264:       const kiss_fft_scalar * OPUS_RESTRICT xp2 = in+stride*(N2-1);
	s32i.n	a8, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:265:       kiss_fft_scalar * OPUS_RESTRICT yp = out+(overlap>>1);
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\mdct.c:267:       const opus_int16 * OPUS_RESTRICT bitrev = l->kfft[shift]->bitrev;
	l32i.n	a2, a7, 8	# MEM[(const struct mdct_lookup *)_739 + 8B], _10
	s32i.n	a7, sp, 56	# %sfp,
	slli	a5, a5, 2	# tmp352, tmp351,
# @OPUS@\upstream\celt\mdct.c:265:       kiss_fft_scalar * OPUS_RESTRICT yp = out+(overlap>>1);
	slli	a7, a6, 2	# tmp346, _8,
	addi.n	a6, a9, 1	# tmp348,,
	srai	a6, a6, 1	#, tmp348,
	add.n	a5, a8, a5	#,, tmp352
# @OPUS@\upstream\celt\mdct.c:258:    N4 = N>>2;
	s32i.n	a9, sp, 40	# %sfp,
	s32i.n	a6, sp, 20	# %sfp,
	s32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mdct.c:265:       kiss_fft_scalar * OPUS_RESTRICT yp = out+(overlap>>1);
	add.n	a15, a8, a7	# yp,, tmp346
# @OPUS@\upstream\celt\mdct.c:267:       const opus_int16 * OPUS_RESTRICT bitrev = l->kfft[shift]->bitrev;
	l32i.n	a12, a2, 48	# _10->bitrev, bitrev
# @OPUS@\upstream\celt\mdct.c:268:       for(i=0;i<N4;i++)
	blti	a9, 1, .L30	#,,
	slli	a9, a9, 1	#,,
# @OPUS@\upstream\celt\mdct.c:287:          xp1+=2*stride;
	slli	a4, a4, 3	#, stride,
	l32i.n	a5, sp, 48	# %sfp,
	s32i.n	a4, sp, 8	# %sfp,
	add.n	a6, a12, a9	#, ivtmp$163,
# @OPUS@\upstream\celt\mdct.c:288:          xp2-=2*stride;
	neg	a4, a4	#,
	neg	a2, a9	#, tmp355
	s32i.n	a9, sp, 16	# %sfp,
	s32i.n	a4, sp, 24	# %sfp,
	add.n	a13, a5, a9	# ivtmp$166,,
	s32i.n	a6, sp, 28	# %sfp,
	s32i.n	a2, sp, 32	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
	s32i.n	a15, sp, 12	# %sfp, yp
.L37:
	l32i.n	a7, sp, 32	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a8, -4	#,
	add.n	a4, a7, a13	# _715,, ivtmp$166
	and	a10, a4, a8	# tmp359, _715,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a10, 0	# value, tmp359
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a9, 2	#,
	slli	a10, a2, 16	# tmp364, value,
	srai	a10, a10, 16	# _329, tmp364,
	bnone	a4, a9, .L32	# _715,,
	srai	a10, a2, 16	# _329, value,
	j	.L32		#
.L32:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a2, -4	#,
	and	a9, a13, a2	# tmp367, ivtmp$166,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a9, 0	# value, tmp367
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a4, 2	#,
	slli	a9, a2, 16	# tmp372, value,
	srai	a9, a9, 16	# _321, tmp372,
	bnone	a13, a4, .L34	# ivtmp$166,,
	srai	a9, a2, 16	# _321, value,
	j	.L34		#
.L34:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a5, -4	#,
	and	a6, a12, a5	# tmp375, ivtmp$163,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a2, a6, 0	# value, tmp375
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a7, 2	#,
	slli	a6, a2, 16	# tmp380, value,
	srai	a6, a6, 16	# _313, tmp380,
	bnone	a12, a7, .L36	# ivtmp$163,,
	srai	a6, a2, 16	# _313, value,
	j	.L36		#
.L36:
# @OPUS@\upstream\celt\mdct.c:276:          yr = ADD32_ovflw(S_MUL(*xp2, t0), S_MUL(*xp1, t1));
	l32i.n	a8, sp, 4	# %sfp,
	l32i.n	a5, a3, 0	# MEM[base: xp1_403, offset: 0B], _32
	l32i.n	a2, a8, 0	# MEM[base: xp2_392, offset: 0B], _19
	srai	a4, a5, 16	# _33, _32,
	srai	a8, a2, 16	# _20, _19,
	extui	a5, a5, 0, 16	# _386, _32,
	extui	a2, a2, 0, 16	# _280, _19,
	mull	a7, a10, a8	# tmp383, _329, _20
	mull	a15, a10, a2	# tmp385, _329, _280
	mull	a11, a9, a4	# tmp388, _321, _33
	mull	a14, a9, a5	# tmp390, _321, _386
# @OPUS@\upstream\celt\mdct.c:277:          yi = SUB32_ovflw(S_MUL(*xp1, t0), S_MUL(*xp2, t1));
	mull	a4, a10, a4	# tmp395, _329, _33
	mull	a5, a10, a5	# tmp397, _329, _386
	mull	a8, a8, a9	# tmp400, _20, _321
	mull	a2, a9, a2	# tmp402, _321, _280
	srai	a5, a5, 15	# tmp398, tmp397,
	srai	a2, a2, 15	# tmp403, tmp402,
	slli	a4, a4, 1	# tmp396, tmp395,
	slli	a8, a8, 1	# tmp401, tmp400,
# @OPUS@\upstream\celt\mdct.c:284:          yp[2*rev+1] = yr;
	l32i.n	a9, sp, 12	# %sfp,
# @OPUS@\upstream\celt\mdct.c:277:          yi = SUB32_ovflw(S_MUL(*xp1, t0), S_MUL(*xp2, t1));
	add.n	a4, a4, a5	# tmp399, tmp396, tmp398
	add.n	a8, a8, a2	# tmp404, tmp401, tmp403
# @OPUS@\upstream\celt\mdct.c:284:          yp[2*rev+1] = yr;
	slli	a6, a6, 3	# _63, _313,
# @OPUS@\upstream\celt\mdct.c:284:          yp[2*rev+1] = yr;
	add.n	a6, a9, a6	# tmp381,, _63
# @OPUS@\upstream\celt\mdct.c:277:          yi = SUB32_ovflw(S_MUL(*xp1, t0), S_MUL(*xp2, t1));
	sub	a4, a4, a8	# yi, tmp399, tmp404
# @OPUS@\upstream\celt\mdct.c:288:          xp2-=2*stride;
	l32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:276:          yr = ADD32_ovflw(S_MUL(*xp2, t0), S_MUL(*xp1, t1));
	slli	a7, a7, 1	# tmp384, tmp383,
	srai	a15, a15, 15	# tmp386, tmp385,
	slli	a11, a11, 1	# tmp389, tmp388,
	srai	a14, a14, 15	# tmp391, tmp390,
# @OPUS@\upstream\celt\mdct.c:285:          yp[2*rev] = yi;
	s32i.n	a4, a6, 0	# *_66, yi
# @OPUS@\upstream\celt\mdct.c:288:          xp2-=2*stride;
	l32i.n	a4, sp, 24	# %sfp,
# @OPUS@\upstream\celt\mdct.c:276:          yr = ADD32_ovflw(S_MUL(*xp2, t0), S_MUL(*xp1, t1));
	add.n	a7, a7, a15	# tmp387, tmp384, tmp386
	add.n	a11, a11, a14	# tmp392, tmp389, tmp391
	add.n	a7, a7, a11	# yr, tmp387, tmp392
# @OPUS@\upstream\celt\mdct.c:287:          xp1+=2*stride;
	l32i.n	a10, sp, 8	# %sfp,
# @OPUS@\upstream\celt\mdct.c:288:          xp2-=2*stride;
	add.n	a2, a2, a4	#,,
# @OPUS@\upstream\celt\mdct.c:268:       for(i=0;i<N4;i++)
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\mdct.c:284:          yp[2*rev+1] = yr;
	s32i.n	a7, a6, 4	# *_65, yr
	addi.n	a12, a12, 2	# ivtmp$163, ivtmp$163,
# @OPUS@\upstream\celt\mdct.c:288:          xp2-=2*stride;
	s32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:287:          xp1+=2*stride;
	add.n	a3, a3, a10	# in, in,
	addi.n	a13, a13, 2	# ivtmp$166, ivtmp$166,
# @OPUS@\upstream\celt\mdct.c:268:       for(i=0;i<N4;i++)
	bne	a5, a12, .L37	#, ivtmp$163,
# @OPUS@\upstream\celt\mdct.c:292:    opus_fft_impl(l->kfft[shift], (kiss_fft_cpx*)(out+(overlap>>1)));
	l32i.n	a3, sp, 56	# %sfp,
	mov.n	a15, a9	# yp,
	l32i.n	a2, a3, 8	# MEM[(const struct mdct_lookup *)_739 + 8B],
	mov.n	a3, a9	#, yp
	call0	opus_fft_impl		#
	j	.L39		#
.L30:
	mov.n	a3, a15	#, yp
	call0	opus_fft_impl		#
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	l32i.n	a6, sp, 20	# %sfp,
	blti	a6, 1, .L51	#,,
	l32i.n	a7, sp, 40	# %sfp,
	slli	a7, a7, 1	#,,
	s32i.n	a7, sp, 16	# %sfp,
	j	.L39		#
.L51:
# @OPUS@\upstream\celt\mdct.c:344:       kiss_fft_scalar * OPUS_RESTRICT xp1 = out+overlap-1;
	l32i.n	a8, sp, 36	# %sfp,
# @OPUS@\upstream\celt\mdct.c:344:       kiss_fft_scalar * OPUS_RESTRICT xp1 = out+overlap-1;
	l32i.n	a9, sp, 44	# %sfp,
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	extui	a2, a8, 31, 1	# tmp412,,
	add.n	a2, a2, a8	# tmp413, tmp412,
# @OPUS@\upstream\celt\mdct.c:347:       const opus_val16 * OPUS_RESTRICT wp2 = window+overlap-1;
	l32i.n	a10, sp, 60	# %sfp,
# @OPUS@\upstream\celt\mdct.c:344:       kiss_fft_scalar * OPUS_RESTRICT xp1 = out+overlap-1;
	slli	a12, a8, 2	# tmp406,,
# @OPUS@\upstream\celt\mdct.c:347:       const opus_val16 * OPUS_RESTRICT wp2 = window+overlap-1;
	slli	a11, a8, 1	# tmp409,,
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	srai	a2, a2, 1	#, tmp413,
# @OPUS@\upstream\celt\mdct.c:344:       kiss_fft_scalar * OPUS_RESTRICT xp1 = out+overlap-1;
	addi	a12, a12, -4	# tmp408, tmp406,
# @OPUS@\upstream\celt\mdct.c:347:       const opus_val16 * OPUS_RESTRICT wp2 = window+overlap-1;
	addi	a11, a11, -2	# tmp411, tmp409,
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	s32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:344:       kiss_fft_scalar * OPUS_RESTRICT xp1 = out+overlap-1;
	add.n	a12, a9, a12	# xp1,, tmp408
	mov.n	a4, a9	# ivtmp$133,
# @OPUS@\upstream\celt\mdct.c:347:       const opus_val16 * OPUS_RESTRICT wp2 = window+overlap-1;
	add.n	a11, a10, a11	# wp2,, tmp411
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	movi.n	a15, 0	# i,
	mov.n	a9, a10	# window,
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	bgei	a8, 2, .L56	#,,
	j	.L27		#
.L39:
	l32i.n	a9, sp, 48	# %sfp, ivtmp$144
	l32i.n	a4, sp, 40	# %sfp,
	l32i.n	a5, sp, 52	# %sfp,
	add.n	a3, a9, a4	# tmp415, ivtmp$144,
	add.n	a2, a9, a5	# tmp416, ivtmp$144,
	slli	a3, a3, 1	# _734, tmp415,
	slli	a2, a2, 1	# _741, tmp416,
# @OPUS@\upstream\celt\mdct.c:252:    for (i=0;i<shift;i++)
	movi.n	a6, 0	#,
	addi	a3, a3, -2	#, _734,
	addi	a2, a2, -2	#, _741,
	s32i.n	a6, sp, 4	# %sfp,
	s32i.n	a3, sp, 8	# %sfp,
	s32i.n	a2, sp, 12	# %sfp,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a12, -4	# tmp418,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
	movi.n	a11, 2	# tmp420,
.L50:
# @OPUS@\upstream\celt\mdct.c:307:          re = yp0[1];
	l32i.n	a4, a15, 4	# MEM[base: yp0_406, offset: 4B], re
# @OPUS@\upstream\celt\mdct.c:308:          im = yp0[0];
	l32i.n	a3, a15, 0	# MEM[base: yp0_406, offset: 0B], im
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a5, a9, a12	# tmp419, ivtmp$144, tmp418
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a5, 0	# value, tmp419
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bnone	a9, a11, .L42	# ivtmp$144, tmp420,
	j	.L65		#
.L42:
	slli	a5, a5, 16	# tmp424, value,
.L65:
	l32i.n	a7, sp, 16	# %sfp,
	srai	a5, a5, 16	# _361, tmp424,
	add.n	a2, a7, a9	# _727,, ivtmp$144
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a6, a2, a12	# tmp427, _727, tmp418
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a6, a6, 0	# value, tmp427
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bnone	a2, a11, .L44	# _727, tmp420,
	j	.L66		#
.L44:
	slli	a6, a6, 16	# tmp432, value,
.L66:
	srai	a6, a6, 16	# _353, tmp432,
# @OPUS@\upstream\celt\mdct.c:317:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	srai	a7, a4, 16	# _84, re,
	srai	a2, a3, 16	# _96, im,
	extui	a4, a4, 0, 16	# _295, re,
	extui	a3, a3, 0, 16	# _297, im,
	mull	a10, a5, a7	# tmp433, _361, _84
	mull	a14, a5, a4	# tmp435, _361, _295
	mull	a13, a6, a2	# tmp438, _353, _96
	mull	a8, a6, a3	# tmp440, _353, _297
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	mull	a2, a5, a2	# tmp449, _361, _96
	mull	a3, a5, a3	# tmp451, _361, _297
# @OPUS@\upstream\celt\mdct.c:317:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	srai	a14, a14, 15	# tmp436, tmp435,
	srai	a8, a8, 15	# tmp441, tmp440,
	slli	a10, a10, 1	# tmp434, tmp433,
	slli	a13, a13, 1	# tmp439, tmp438,
	add.n	a13, a13, a8	# tmp442, tmp439, tmp441
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	mull	a7, a7, a6	# tmp444, _84, _353
# @OPUS@\upstream\celt\mdct.c:320:          re = yp1[1];
	l32i.n	a8, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	mull	a4, a6, a4	# tmp446, _353, _295
# @OPUS@\upstream\celt\mdct.c:317:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	add.n	a10, a10, a14	# tmp437, tmp434, tmp436
	add.n	a10, a10, a13	# yr, tmp437, tmp442
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	srai	a3, a3, 15	# tmp452, tmp451,
	slli	a2, a2, 1	# tmp450, tmp449,
	add.n	a2, a2, a3	# tmp453, tmp450, tmp452
# @OPUS@\upstream\celt\mdct.c:320:          re = yp1[1];
	l32i.n	a13, a8, 4	# MEM[base: yp1_407, offset: 4B], re
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	srai	a4, a4, 15	# tmp447, tmp446,
# @OPUS@\upstream\celt\mdct.c:321:          im = yp1[0];
	l32i.n	a3, a8, 0	# MEM[base: yp1_407, offset: 0B], im
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	slli	a7, a7, 1	# tmp445, tmp444,
# @OPUS@\upstream\celt\mdct.c:322:          yp0[0] = yr;
	s32i.n	a10, a15, 0	# MEM[base: yp0_406, offset: 0B], yr
	l32i.n	a10, sp, 8	# %sfp,
# @OPUS@\upstream\celt\mdct.c:318:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	add.n	a7, a7, a4	# tmp448, tmp445, tmp447
	sub	a7, a7, a2	# yi, tmp448, tmp453
	sub	a2, a10, a9	# _731,, ivtmp$144
# @OPUS@\upstream\celt\mdct.c:323:          yp1[1] = yi;
	s32i.n	a7, a8, 4	# MEM[base: yp1_407, offset: 4B], yi
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a4, a2, a12	# tmp458, _731, tmp418
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a4, a4, 0	# value, tmp458
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bnone	a2, a11, .L46	# _731, tmp420,
	j	.L67		#
.L46:
	slli	a4, a4, 16	# tmp463, value,
.L67:
	l32i.n	a2, sp, 12	# %sfp,
	srai	a4, a4, 16	# _345, tmp463,
	sub	a6, a2, a9	# _738,, ivtmp$144
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a5, a6, a12	# tmp467, _738, tmp418
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a5, 0	# value, tmp467
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	bnone	a6, a11, .L48	# _738, tmp420,
	j	.L68		#
.L48:
	slli	a5, a5, 16	# tmp472, value,
.L68:
	srai	a5, a5, 16	# _337, tmp472,
# @OPUS@\upstream\celt\mdct.c:333:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	srai	a8, a13, 16	# _136, re,
	extui	a2, a13, 0, 16	# _301, re,
	srai	a6, a3, 16	# _148, im,
	extui	a3, a3, 0, 16	# _391, im,
	mull	a7, a4, a8	# tmp473, _345, _136
	mull	a14, a4, a2	# tmp475, _345, _301
	mull	a13, a5, a6	# tmp478, _337, _148
	mull	a10, a5, a3	# tmp480, _337, _391
# @OPUS@\upstream\celt\mdct.c:334:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	mull	a8, a8, a5	# tmp484, _136, _337
	mull	a2, a5, a2	# tmp486, _337, _301
	mull	a6, a4, a6	# tmp489, _345, _148
	mull	a3, a4, a3	# tmp491, _345, _391
# @OPUS@\upstream\celt\mdct.c:333:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	slli	a7, a7, 1	# tmp474, tmp473,
	srai	a14, a14, 15	# tmp476, tmp475,
	slli	a13, a13, 1	# tmp479, tmp478,
	srai	a10, a10, 15	# tmp481, tmp480,
# @OPUS@\upstream\celt\mdct.c:335:          yp1[0] = yr;
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mdct.c:333:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	add.n	a7, a7, a14	# tmp477, tmp474, tmp476
	add.n	a13, a13, a10	# tmp482, tmp479, tmp481
# @OPUS@\upstream\celt\mdct.c:334:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	slli	a8, a8, 1	# tmp485, tmp484,
	srai	a2, a2, 15	# tmp487, tmp486,
	slli	a6, a6, 1	# tmp490, tmp489,
	srai	a3, a3, 15	# tmp492, tmp491,
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	l32i.n	a5, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:333:          yr = ADD32_ovflw(S_MUL(re,t0), S_MUL(im,t1));
	add.n	a7, a7, a13	# yr, tmp477, tmp482
# @OPUS@\upstream\celt\mdct.c:334:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	add.n	a8, a8, a2	# tmp488, tmp485, tmp487
	add.n	a6, a6, a3	# tmp493, tmp490, tmp492
# @OPUS@\upstream\celt\mdct.c:335:          yp1[0] = yr;
	s32i.n	a7, a4, 0	# MEM[base: yp1_407, offset: 0B], yr
# @OPUS@\upstream\celt\mdct.c:334:          yi = SUB32_ovflw(S_MUL(re,t1), S_MUL(im,t0));
	sub	a6, a8, a6	# yi, tmp488, tmp493
# @OPUS@\upstream\celt\mdct.c:336:          yp0[1] = yi;
	s32i.n	a6, a15, 4	# MEM[base: yp0_406, offset: 4B], yi
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	addi.n	a5, a5, 1	#,,
# @OPUS@\upstream\celt\mdct.c:338:          yp1 -= 2;
	addi	a4, a4, -8	#,,
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	l32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	s32i.n	a5, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:338:          yp1 -= 2;
	s32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\mdct.c:337:          yp0 += 2;
	addi.n	a15, a15, 8	# yp, yp,
	addi.n	a9, a9, 2	# ivtmp$144, ivtmp$144,
# @OPUS@\upstream\celt\mdct.c:302:       for(i=0;i<(N4+1)>>1;i++)
	blt	a5, a6, .L50	#,,
	j	.L51		#
.L56:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a7, -4	#,
# @OPUS@\upstream\celt\mdct.c:352:          x1 = *xp1;
	l32i.n	a2, a12, 0	# MEM[base: xp1_408, offset: 0B], x1
# @OPUS@\upstream\celt\mdct.c:353:          x2 = *yp1;
	l32i.n	a3, a4, 0	# MEM[base: _751, offset: 0B], x2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	and	a8, a9, a7	# tmp497, window,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a8, 0	# value, tmp497
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a10, 2	#,
	slli	a8, a5, 16	# tmp502, value,
	srai	a8, a8, 16	# _377, tmp502,
	bnone	a9, a10, .L53	# window,,
	srai	a8, a5, 16	# _377, value,
	j	.L53		#
.L53:
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:109:         yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
	movi.n	a5, -4	#,
	and	a7, a11, a5	# tmp505, wp2,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a5, a7, 0	# value, tmp505
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:110:     return address & 2U ? value.half[1] : value.half[0];
#NO_APP
	movi.n	a6, 2	#,
	slli	a7, a5, 16	# tmp510, value,
	srai	a7, a7, 16	# _369, tmp510,
	bnone	a11, a6, .L55	# wp2,,
	srai	a7, a5, 16	# _369, value,
	j	.L55		#
.L55:
# @OPUS@\upstream\celt\mdct.c:357:          *yp1++ = SUB32_ovflw(MULT16_32_Q15(w2, x2), MULT16_32_Q15(w1, x1));
	srai	a5, a2, 16	# _197, x1,
	mull	a10, a8, a5	#, _377, _197
	extui	a2, a2, 0, 16	# _259, x1,
	s32i.n	a10, sp, 8	# %sfp,
	mull	a10, a8, a2	#, _377, _259
	srai	a14, a3, 16	# _185, x2,
	s32i.n	a10, sp, 0	# %sfp,
	extui	a3, a3, 0, 16	# _251, x2,
	mull	a13, a7, a14	# tmp511, _369, _185
	mull	a6, a7, a3	# tmp513, _369, _251
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	mull	a14, a14, a8	# tmp522, _185, _377
	mull	a3, a8, a3	# tmp524, _377, _251
	mull	a5, a7, a5	# tmp527, _369, _197
	mull	a2, a7, a2	# tmp529, _369, _259
# @OPUS@\upstream\celt\mdct.c:357:          *yp1++ = SUB32_ovflw(MULT16_32_Q15(w2, x2), MULT16_32_Q15(w1, x1));
	l32i.n	a8, sp, 0	# %sfp,
	l32i.n	a7, sp, 8	# %sfp,
	slli	a13, a13, 1	# tmp512, tmp511,
	slli	a10, a7, 1	# tmp517,,
	srai	a6, a6, 15	# tmp514, tmp513,
	srai	a7, a8, 15	# tmp519,,
	add.n	a10, a10, a7	# tmp520, tmp517, tmp519
	add.n	a13, a13, a6	# tmp515, tmp512, tmp514
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	slli	a14, a14, 1	# tmp523, tmp522,
	srai	a3, a3, 15	# tmp525, tmp524,
	slli	a5, a5, 1	# tmp528, tmp527,
	srai	a2, a2, 15	# tmp530, tmp529,
# @OPUS@\upstream\celt\mdct.c:357:          *yp1++ = SUB32_ovflw(MULT16_32_Q15(w2, x2), MULT16_32_Q15(w1, x1));
	sub	a13, a13, a10	# tmp521, tmp515, tmp520
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	add.n	a14, a14, a3	# tmp526, tmp523, tmp525
	add.n	a5, a5, a2	# tmp531, tmp528, tmp530
# @OPUS@\upstream\celt\mdct.c:357:          *yp1++ = SUB32_ovflw(MULT16_32_Q15(w2, x2), MULT16_32_Q15(w1, x1));
	s32i.n	a13, a4, 0	# MEM[base: _751, offset: 0B], tmp521
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	addi	a12, a12, -4	# xp1, xp1,
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	add.n	a5, a14, a5	# tmp532, tmp526, tmp531
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	l32i.n	a10, sp, 4	# %sfp,
# @OPUS@\upstream\celt\mdct.c:358:          *xp1-- = ADD32_ovflw(MULT16_32_Q15(w1, x2), MULT16_32_Q15(w2, x1));
	s32i.n	a5, a12, 4	# MEM[base: xp1_304, offset: 4B], tmp532
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	addi.n	a15, a15, 1	# i, i,
# @OPUS@\upstream\celt\mdct.c:363:          wp1++;
	addi.n	a9, a9, 2	# window, window,
# @OPUS@\upstream\celt\mdct.c:364:          wp2--;
	addi	a11, a11, -2	# wp2, wp2,
	addi.n	a4, a4, 4	# ivtmp$133, ivtmp$133,
# @OPUS@\upstream\celt\mdct.c:349:       for(i = 0; i < overlap/2; i++)
	blt	a15, a10, .L56	# i,,
.L27:
# @OPUS@\upstream\celt\mdct.c:367: }
	l32i	a0, sp, 92	#,
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	clt_mdct_backward_c, .-clt_mdct_backward_c
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
