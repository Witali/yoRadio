# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/celt.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"celt.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\celt.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\celt.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\celt.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\celt.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\celt.c.s.raw
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
	.section	.text.resampling_factor,"ax",@progbits
	.literal_position
	.literal .LC0, 16000
	.literal .LC1, 8000
	.literal .LC2, 12000
	.literal .LC3, 24000
	.literal .LC4, 48000
	.align	4
	.global	resampling_factor
	.type	resampling_factor, @function
# Function: resampling_factor
# Module: upstream/celt/celt.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context:
# C context: int resampling_factor(opus_int32 rate)
# C context: {
# C context: int ret;
# C context: switch (rate)
# C context: {
resampling_factor:
# @OPUS@\upstream\celt\celt.c:65:    switch (rate)
	l32r	a3, .LC0	#, tmp44
	beq	a2, a3, .L4	# rate, tmp44,
	blt	a3, a2, .L3	# tmp44, rate,
	l32r	a4, .LC1	#, tmp46
# @OPUS@\upstream\celt\celt.c:80:       ret = 6;
	movi.n	a3, 6	# <retval>,
# @OPUS@\upstream\celt\celt.c:65:    switch (rate)
	beq	a2, a4, .L1	# rate, tmp46,
# @OPUS@\upstream\celt\celt.c:86:       ret = 0;
	l32r	a3, .LC2	#, tmp47
	movi.n	a4, 0	# tmp62,
	sub	a2, a2, a3	# tmp63, rate, tmp47
	movi.n	a3, 4	# tmp61,
	movnez	a3, a4, a2	# <retval>, tmp62, tmp63
	j	.L1		#
.L3:
# @OPUS@\upstream\celt\celt.c:65:    switch (rate)
	l32r	a4, .LC3	#, tmp48
# @OPUS@\upstream\celt\celt.c:71:       ret = 2;
	movi.n	a3, 2	# <retval>,
# @OPUS@\upstream\celt\celt.c:65:    switch (rate)
	beq	a2, a4, .L1	# rate, tmp48,
# @OPUS@\upstream\celt\celt.c:86:       ret = 0;
	l32r	a3, .LC4	#, tmp49
	movi.n	a4, 0	# tmp67,
	sub	a2, a2, a3	# tmp65, rate, tmp49
	movi.n	a3, 1	# tmp66,
	movnez	a3, a4, a2	# <retval>, tmp67, tmp65
	j	.L1		#
.L4:
# @OPUS@\upstream\celt\celt.c:74:       ret = 3;
	movi.n	a3, 3	# <retval>,
.L1:
# @OPUS@\upstream\celt\celt.c:90: }
	mov.n	a2, a3	#, <retval>
	ret.n
	.size	resampling_factor, .-resampling_factor
	.section	.text.comb_filter,"ax",@progbits
	.literal_position
	.literal .LC5, gains$3933
	.literal .LC6, 32767
	.literal .LC7, -300000000
	.literal .LC8, 300000000
	.align	4
	.global	comb_filter
	.type	comb_filter, @function
# Function: comb_filter
# Module: upstream/celt/celt.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context: #ifndef OVERRIDE_comb_filter
# C context: void comb_filter(opus_val32 *y, opus_val32 *x, int T0, int T1, int N,
# C context: opus_val16 g0, opus_val16 g1, int tapset0, int tapset1,
# C context: const opus_val16 *window, int overlap, int arch)
# C context: {
# C context: int i;
comb_filter:
	movi	a9, 0xa0	#,
	sub	sp, sp, a9	#,,
	l16si	a8, sp, 160	# g1,
	slli	a7, a7, 16	# tmp313, g0,
	srai	a7, a7, 16	# g0, tmp313,
	s32i	a15, sp, 140	#,
	s32i	a8, sp, 84	# %sfp,
	s32i	a3, sp, 80	# %sfp, x
	s32i	a0, sp, 156	#,
	s32i	a12, sp, 152	#,
	s32i	a13, sp, 148	#,
	s32i	a14, sp, 144	#,
# @OPUS@\upstream\celt\celt.c:203:    if (g0==0 && g1==0)
	or	a8, a7, a8	# tmp324, g0,
# @OPUS@\upstream\celt\celt.c:193: {
	s32i	a2, sp, 88	# %sfp, y
	s32i	a6, sp, 92	# %sfp, N
	l32i	a15, sp, 164	# tapset0, tapset0
	l32i	a3, sp, 168	# tapset1, tapset1
# @OPUS@\upstream\celt\celt.c:203:    if (g0==0 && g1==0)
	bnez.n	a8, .L11	# tmp324,
# @OPUS@\upstream\celt\celt.c:206:       if (x!=y)
	l32i	a9, sp, 80	# %sfp,
	beq	a9, a2, .L10	#, y,
# @OPUS@\upstream\celt\celt.c:207:          OPUS_MOVE(y, x, N);
	movi.n	a5, 4	#,
	mov.n	a4, a6	#, N
	mov.n	a3, a9	#,
	call0	yoradio_opus_copy		#
	j	.L10		#
.L11:
# @OPUS@\upstream\celt\celt.c:212:    T0 = IMAX(T0, COMBFILTER_MINPERIOD);
	movi.n	a2, 0xf	# tmp330,
	bge	a4, a2, .L14	# T0, tmp330,
	mov.n	a4, a2	# T0, tmp330
.L14:
# @OPUS@\upstream\celt\celt.c:213:    T1 = IMAX(T1, COMBFILTER_MINPERIOD);
	movi.n	a2, 0xf	# tmp335,
	bge	a5, a2, .L15	# T1, tmp335,
	mov.n	a5, a2	# T1, tmp335
.L15:
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	slli	a2, a3, 1	# tmp373, tapset1,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	l32r	a8, .LC5	#, tmp336
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	add.n	a2, a2, a3	# tmp374, tmp373, tapset1
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	slli	a6, a15, 1	# tmp338, tapset0,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	slli	a2, a2, 1	# tmp375, tmp374,
	add.n	a2, a8, a2	# tmp376, tmp336, tmp375
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	add.n	a6, a6, a15	# tmp339, tmp338, tapset0
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	l32i	a10, sp, 84	# %sfp,
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	l16ui	a14, a2, 4	# gains,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	slli	a6, a6, 1	# tmp340, tmp339,
	add.n	a6, a8, a6	# tmp341, tmp336, tmp340
	l16ui	a12, a6, 0	# gains,
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	l16ui	a11, a6, 2	# gains,
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	l16ui	a9, a6, 4	# gains,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	l16ui	a8, a2, 0	# gains,
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	l16ui	a6, a2, 2	# gains,
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	mul16s	a14, a14, a10	# tmp401, tmp402,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	slli	a2, a5, 2	# tmp408, T1,
	neg	a2, a2	#, tmp408
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	movi.n	a13, 1	# tmp413,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	s32i.n	a2, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	addmi	a14, a14, 0x4000	# tmp403, tmp401,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	sub	a2, a4, a5	# tmp412, T0, T1
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	ssl	a13	#
	sll	a5, a14	# tmp405, tmp403
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	l32i.n	a14, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	mul16s	a8, a8, a10	# tmp377, tmp378,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	addi.n	a14, a14, 4	#,,
	s32i	a14, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	l32i.n	a14, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	mul16s	a11, a11, a7	# tmp354, tmp355, g0
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	addi	a14, a14, -4	#,,
	s32i	a14, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	mul16s	a12, a12, a7	# tmp342, tmp343, g0
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	mul16s	a9, a9, a7	# tmp366, tmp367, g0
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	addmi	a11, a11, 0x4000	# tmp356, tmp354,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	addmi	a8, a8, 0x4000	# tmp379, tmp377,
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	l32i.n	a14, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	mul16s	a6, a6, a10	# tmp389, tmp390,
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	ssl	a13	#
	sll	a11, a11	# tmp358, tmp356
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	ssl	a13	#
	sll	a8, a8	# tmp381, tmp379
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	movi.n	a10, 0	# tmp414,
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	addi	a14, a14, -8	#,,
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	srai	a11, a11, 16	#, tmp358,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	srai	a8, a8, 16	#, tmp381,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	addmi	a12, a12, 0x4000	# tmp344, tmp342,
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	addmi	a9, a9, 0x4000	# tmp368, tmp366,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	ssl	a13	#
	sll	a12, a12	# tmp346, tmp344
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	ssl	a13	#
	sll	a9, a9	# tmp370, tmp368
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	s32i	a14, sp, 104	# %sfp,
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	addmi	a6, a6, 0x4000	# tmp391, tmp389,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	mov.n	a14, a10	#, tmp414
# @OPUS@\upstream\celt\celt.c:215:    g01 = MULT16_16_P15(g0, gains[tapset0][1]);
	s32i	a11, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt.c:217:    g10 = MULT16_16_P15(g1, gains[tapset1][0]);
	s32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	l32i	a11, sp, 96	# %sfp,
	l32i	a8, sp, 80	# %sfp,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	moveqz	a14, a13, a2	#, tmp413, tmp412
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	ssl	a13	#
	sll	a6, a6	# tmp393, tmp391
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	srai	a12, a12, 16	#, tmp346,
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	srai	a9, a9, 16	#, tmp370,
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	srai	a5, a5, 16	#, tmp405,
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	srai	a6, a6, 16	#, tmp393,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	sub	a3, a15, a3	# tmp417, tapset0, tapset1
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	mov.n	a2, a14	# tmp411,
# @OPUS@\upstream\celt\celt.c:214:    g00 = MULT16_16_P15(g0, gains[tapset0][0]);
	s32i.n	a12, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	l32i	a14, sp, 80	# %sfp,
# @OPUS@\upstream\celt\celt.c:216:    g02 = MULT16_16_P15(g0, gains[tapset0][2]);
	s32i	a9, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt.c:219:    g12 = MULT16_16_P15(g1, gains[tapset1][2]);
	s32i.n	a5, sp, 56	# %sfp,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	add.n	a9, a8, a11	# _39,,
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	l32i	a5, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt.c:221:    x2 = x[-T1  ];
	l32i.n	a12, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	l32i	a11, sp, 104	# %sfp,
# @OPUS@\upstream\celt\celt.c:218:    g11 = MULT16_16_P15(g1, gains[tapset1][1]);
	s32i.n	a6, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	movnez	a13, a10, a3	# tmp413, tmp414, tmp417
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	add.n	a6, a14, a5	# _43,,
# @OPUS@\upstream\celt\celt.c:221:    x2 = x[-T1  ];
	add.n	a8, a8, a12	# _40,,
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	add.n	a5, a14, a11	# _45,,
# @OPUS@\upstream\celt\celt.c:225:    if (g0==g1 && T0==T1 && tapset0==tapset1)
	bnone	a2, a13, .L30	# tmp411, tmp416,
	l32i	a12, sp, 84	# %sfp,
	beq	a7, a12, .L26	# g0,,
.L30:
# @OPUS@\upstream\celt\celt.c:227:    for (i=0;i<overlap;i++)
	l32i	a14, sp, 176	# overlap,
	blti	a14, 1, .L27	#,,
	l32i	a2, sp, 172	# window,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	l32i.n	a9, a9, 0	# *_39,
	s32i.n	a2, sp, 4	# %sfp,
# @OPUS@\upstream\celt\celt.c:221:    x2 = x[-T1  ];
	l32i.n	a8, a8, 0	# *_40,
# @OPUS@\upstream\celt\celt.c:220:    x1 = x[-T1+1];
	s32i.n	a9, sp, 32	# %sfp,
	l32i	a7, sp, 80	# %sfp,
	l32i.n	a9, sp, 4	# %sfp,
	slli	a3, a4, 2	# tmp431, T0,
	slli	a2, a14, 1	# tmp434,,
# @OPUS@\upstream\celt\celt.c:221:    x2 = x[-T1  ];
	s32i.n	a8, sp, 8	# %sfp,
# @OPUS@\upstream\celt\celt.c:222:    x3 = x[-T1-1];
	l32i.n	a6, a6, 0	# *_43,
	l32i	a8, sp, 88	# %sfp,
	l32r	a10, .LC7	#,
	l32r	a11, .LC8	#,
	slli	a4, a4, 2	#, T0,
	sub	a3, a7, a3	# tmp433,, tmp431
	add.n	a2, a9, a2	#,, tmp434
	s32i	a4, sp, 76	# %sfp,
	s32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\celt\celt.c:223:    x4 = x[-T1-2];
	l32i.n	a5, a5, 0	# *_45, x4
	s32i.n	a8, sp, 12	# %sfp,
	addi	a14, a3, -8	# ivtmp$46, tmp433,
	s32i	a2, sp, 72	# %sfp,
	s32i.n	a10, sp, 36	# %sfp,
	s32i.n	a11, sp, 40	# %sfp,
	mov.n	a4, a9	#,
	l32i.n	a12, sp, 32	# %sfp,
	j	.L20		#
.L28:
	l32i.n	a12, sp, 8	# %sfp,
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\celt.c:243:       x1=x0;
	l32i.n	a3, sp, 28	# %sfp,
	s32i.n	a12, sp, 24	# %sfp,
	s32i.n	a2, sp, 8	# %sfp,
	s32i.n	a3, sp, 32	# %sfp,
	mov.n	a4, a6	#,
	mov.n	a12, a3	#,
.L20:
# @OPUS@\upstream\celt\celt.c:231:       f = MULT16_16_Q15(window[i],window[i]);
	l16si	a3, a4, 0	# MEM[base: _799, offset: 0B], _57
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	l32r	a8, .LC6	#,
# @OPUS@\upstream\celt\celt.c:231:       f = MULT16_16_Q15(window[i],window[i]);
	mull	a3, a3, a3	# tmp439, _57, _57
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	l32i.n	a10, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt.c:231:       f = MULT16_16_Q15(window[i],window[i]);
	slli	a3, a3, 1	# tmp441, tmp439,
	srai	a3, a3, 16	# f, tmp441,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	sub	a4, a8, a3	# tmp442,, f
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	mull	a8, a3, a10	# tmp454, f,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	l32i	a6, sp, 76	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	l32i.n	a11, sp, 52	# %sfp,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	l32i.n	a7, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	slli	a8, a8, 1	# tmp456, tmp454,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	add.n	a2, a6, a14	# tmp435,, ivtmp$46
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	srai	a8, a8, 16	#, tmp456,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	mull	a6, a3, a11	# tmp457, f,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	add.n	a9, a2, a7	# tmp436, tmp435,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	l32i.n	a10, sp, 24	# %sfp,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	s32i.n	a8, sp, 16	# %sfp,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	slli	a4, a4, 16	# tmp444, tmp442,
	l32i.n	a8, sp, 60	# %sfp,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	l32i.n	a9, a9, 16	# MEM[base: _800, offset: 16B],
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	srai	a4, a4, 16	# _64, tmp444,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	slli	a6, a6, 1	# tmp459, tmp457,
	add.n	a7, a12, a10	# tmp468,,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	mull	a15, a4, a8	# tmp445, _64,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	l32i.n	a12, sp, 8	# %sfp,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	l32i	a8, sp, 64	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	srai	a6, a6, 16	#, tmp459,
# @OPUS@\upstream\celt\celt.c:230:       x0=x[i-T1+2];
	s32i.n	a9, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	s32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	l32i.n	a11, sp, 56	# %sfp,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	mull	a13, a4, a8	# tmp448, _64,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	extui	a6, a12, 0, 16	# tmp463,,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	l32i.n	a8, sp, 20	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	l32i.n	a12, sp, 28	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	extui	a9, a7, 0, 16	# tmp469, tmp468
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	l32i.n	a10, a14, 4	# MEM[base: _798, offset: 4B], _99
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a5, a12, a5	# tmp478,, x4
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	l32i.n	a2, a2, 8	# MEM[base: _794, offset: 8B],
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	l32i.n	a12, sp, 16	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	mull	a3, a3, a11	# tmp460, f,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	mull	a9, a9, a8	# tmp470, tmp469,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	l32i.n	a11, a14, 12	# MEM[base: _798, offset: 12B], _95
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	l32i.n	a8, a14, 8	# MEM[base: _798, offset: 8B],
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	s32i	a2, sp, 108	# %sfp,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	mull	a6, a6, a12	# tmp464, tmp463,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	add.n	a2, a11, a10	# tmp489, _95, _99
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	l32i	a12, sp, 68	# %sfp,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	extui	a11, a8, 0, 16	# tmp483,,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	l32i.n	a10, a14, 16	# MEM[base: _798, offset: 16B],
	l32i.n	a8, a14, 0	# MEM[base: _798, offset: 0B],
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	slli	a15, a15, 1	# tmp447, tmp445,
	srai	a15, a15, 16	# _70, tmp447,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	slli	a3, a3, 1	# tmp462, tmp460,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	add.n	a10, a10, a8	#,,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	mull	a11, a11, a15	#, tmp483, _70
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	srai	a3, a3, 16	# _190, tmp462,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	mull	a4, a4, a12	# tmp451, _64,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	srai	a9, a9, 15	# tmp471, tmp470,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	extui	a12, a5, 0, 16	# tmp479, tmp478
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	srai	a6, a6, 15	# tmp465, tmp464,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	s32i.n	a10, sp, 0	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a9	# tmp472, tmp465, tmp471
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	mull	a12, a12, a3	# tmp480, tmp479, _190
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	l32i	a9, sp, 108	# %sfp,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	s32i	a11, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	l32i.n	a11, sp, 0	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a9	# tmp474, tmp472,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	srai	a12, a12, 15	# tmp481, tmp480,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	slli	a13, a13, 1	# tmp450, tmp448,
	srai	a13, a13, 16	# _91, tmp450,
	extui	a10, a2, 0, 16	# tmp490, tmp489
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	extui	a9, a11, 0, 16	# tmp497,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a12	# tmp482, tmp474, tmp481
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	l32i.n	a11, sp, 8	# %sfp,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	l32i	a12, sp, 112	# %sfp,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	slli	a4, a4, 1	# tmp453, tmp451,
	srai	a4, a4, 16	# _121, tmp453,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	mull	a10, a10, a13	# tmp491, tmp490, _91
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	srai	a8, a11, 16	# tmp501,,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	mull	a9, a9, a4	# tmp498, tmp497, _121
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	srai	a11, a12, 15	# tmp485,,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a11	# tmp486, tmp482, tmp485
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	srai	a10, a10, 15	# tmp492, tmp491,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	l32i.n	a11, sp, 16	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	srai	a12, a7, 16	# tmp506, tmp468,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a10	# tmp493, tmp486, tmp492
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	srai	a9, a9, 15	# tmp499, tmp498,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	mull	a8, a8, a11	# tmp502, tmp501,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a9	# tmp500, tmp493, tmp499
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	l32i.n	a9, a14, 8	# MEM[base: _798, offset: 8B],
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	mull	a12, a12, a7	# tmp507, tmp506,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	srai	a5, a5, 16	# tmp511, tmp478,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	srai	a11, a9, 16	# tmp515,,
# @OPUS@\upstream\celt\celt.c:236:                + MULT16_32_Q15(MULT16_16_Q15(f,g10),x2)
	slli	a8, a8, 1	# tmp503, tmp502,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	mull	a5, a5, a3	# tmp512, tmp511, _190
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	l32i.n	a10, sp, 0	# %sfp,
# @OPUS@\upstream\celt\celt.c:237:                + MULT16_32_Q15(MULT16_16_Q15(f,g11),ADD32(x1,x3))
	slli	a12, a12, 1	# tmp508, tmp507,
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	mull	a15, a11, a15	# tmp516, tmp515, _70
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a8	# tmp504, tmp500, tmp503
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	srai	a2, a2, 16	# tmp520, tmp489,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a12	# tmp509, tmp504, tmp508
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	slli	a5, a5, 1	# tmp513, tmp512,
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	mull	a2, a2, a13	# tmp521, tmp520, _91
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	srai	a7, a10, 16	# tmp525,,
	l32i.n	a11, sp, 4	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a5	# tmp514, tmp509, tmp513
# @OPUS@\upstream\celt\celt.c:233:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g00),x[i-T0])
	slli	a15, a15, 1	# tmp517, tmp516,
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	mull	a7, a7, a4	# tmp526, tmp525, _121
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a15	# tmp518, tmp514, tmp517
# @OPUS@\upstream\celt\celt.c:234:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g01),ADD32(x[i-T0+1],x[i-T0-1]))
	slli	a2, a2, 1	# tmp522, tmp521,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a2	# tmp523, tmp518, tmp522
# @OPUS@\upstream\celt\celt.c:235:                + MULT16_32_Q15(MULT16_16_Q15((Q15ONE-f),g02),ADD32(x[i-T0+2],x[i-T0-2]))
	slli	a7, a7, 1	# tmp527, tmp526,
	addi.n	a11, a11, 2	#,,
# @OPUS@\upstream\celt\celt.c:239:       y[i] = SATURATE(y[i], SIG_SAT);
	l32i.n	a12, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt.c:238:                + MULT16_32_Q15(MULT16_16_Q15(f,g12),ADD32(x0,x4));
	add.n	a6, a6, a7	# tmp529, tmp523, tmp527
	s32i.n	a11, sp, 4	# %sfp,
# @OPUS@\upstream\celt\celt.c:239:       y[i] = SATURATE(y[i], SIG_SAT);
	bge	a6, a12, .L18	# tmp529,,
	mov.n	a6, a12	# tmp529,
.L18:
# @OPUS@\upstream\celt\celt.c:239:       y[i] = SATURATE(y[i], SIG_SAT);
	l32i.n	a2, sp, 40	# %sfp,
	bge	a2, a6, .L19	#, tmp535,
	mov.n	a6, a2	# tmp535,
.L19:
	l32i.n	a3, sp, 12	# %sfp,
# @OPUS@\upstream\celt\celt.c:227:    for (i=0;i<overlap;i++)
	l32i	a4, sp, 72	# %sfp,
# @OPUS@\upstream\celt\celt.c:239:       y[i] = SATURATE(y[i], SIG_SAT);
	s32i.n	a6, a3, 0	# MEM[base: _790, offset: 0B], tmp535
	addi.n	a3, a3, 4	#,,
# @OPUS@\upstream\celt\celt.c:227:    for (i=0;i<overlap;i++)
	l32i.n	a6, sp, 4	# %sfp,
	s32i.n	a3, sp, 12	# %sfp,
	l32i.n	a5, sp, 24	# %sfp, x4
	addi.n	a14, a14, 4	# ivtmp$46, ivtmp$46,
	bne	a4, a6, .L28	#,,
	l32i	a2, sp, 176	# overlap, i
	j	.L16		#
.L26:
# @OPUS@\upstream\celt\celt.c:227:    for (i=0;i<overlap;i++)
	s32i	a10, sp, 176	# overlap, tmp414
# @OPUS@\upstream\celt\celt.c:226:       overlap=0;
	mov.n	a2, a10	# i, tmp414
	j	.L16		#
.L27:
# @OPUS@\upstream\celt\celt.c:227:    for (i=0;i<overlap;i++)
	movi.n	a2, 0	# i,
.L16:
# @OPUS@\upstream\celt\celt.c:246:    if (g1==0)
	l32i	a7, sp, 84	# %sfp,
	bnez.n	a7, .L21	#,
# @OPUS@\upstream\celt\celt.c:249:       if (x!=y)
	l32i	a8, sp, 80	# %sfp,
	l32i	a9, sp, 88	# %sfp,
	beq	a8, a9, .L10	#,,
# @OPUS@\upstream\celt\celt.c:250:          OPUS_MOVE(y+overlap, x+overlap, N-overlap);
	l32i	a10, sp, 176	# overlap,
	l32i	a11, sp, 92	# %sfp,
	slli	a2, a10, 2	# _210,,
	add.n	a3, a8, a2	#,, _210
	movi.n	a5, 4	#,
	sub	a4, a11, a10	#,,
	add.n	a2, a9, a2	#,, _210
	call0	yoradio_opus_copy		#
	j	.L10		#
.L21:
# @OPUS@\upstream\celt\celt.c:255:    comb_filter_const(y+i, x+i, T1, N-i, g10, g11, g12, arch);
	l32i	a12, sp, 80	# %sfp,
	slli	a10, a2, 2	# _216, i,
# @OPUS@\upstream\celt\celt.c:168:    x3 = x[-T-1];
	l32i	a4, sp, 100	# %sfp,
# @OPUS@\upstream\celt\celt.c:170:    x1 = x[-T+1];
	l32i	a9, sp, 96	# %sfp,
# @OPUS@\upstream\celt\celt.c:255:    comb_filter_const(y+i, x+i, T1, N-i, g10, g11, g12, arch);
	l32i	a11, sp, 92	# %sfp,
# @OPUS@\upstream\celt\celt.c:167:    x4 = x[-T-2];
	l32i	a14, sp, 104	# %sfp,
# @OPUS@\upstream\celt\celt.c:169:    x2 = x[-T];
	l32i.n	a8, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:255:    comb_filter_const(y+i, x+i, T1, N-i, g10, g11, g12, arch);
	add.n	a3, a12, a10	# _218,, _216
# @OPUS@\upstream\celt\celt.c:168:    x3 = x[-T-1];
	add.n	a7, a3, a4	# tmp545, _218,
# @OPUS@\upstream\celt\celt.c:167:    x4 = x[-T-2];
	add.n	a5, a3, a14	# tmp544, _218,
# @OPUS@\upstream\celt\celt.c:170:    x1 = x[-T+1];
	add.n	a4, a3, a9	# tmp547, _218,
# @OPUS@\upstream\celt\celt.c:169:    x2 = x[-T];
	add.n	a6, a3, a8	# tmp546, _218,
# @OPUS@\upstream\celt\celt.c:255:    comb_filter_const(y+i, x+i, T1, N-i, g10, g11, g12, arch);
	sub	a2, a11, a2	# _219,, i
# @OPUS@\upstream\celt\celt.c:167:    x4 = x[-T-2];
	l32i.n	a5, a5, 0	# *_274, x4
# @OPUS@\upstream\celt\celt.c:168:    x3 = x[-T-1];
	l32i.n	a12, a7, 0	# *_278, x3
# @OPUS@\upstream\celt\celt.c:169:    x2 = x[-T];
	l32i.n	a9, a6, 0	# *_280, x3
# @OPUS@\upstream\celt\celt.c:170:    x1 = x[-T+1];
	l32i.n	a11, a4, 0	# *_283, x1
# @OPUS@\upstream\celt\celt.c:171:    for (i=0;i<N;i++)
	blti	a2, 1, .L10	# _219,,
	l32i	a14, sp, 88	# %sfp,
	slli	a2, a2, 2	# tmp548, _219,
	add.n	a10, a14, a10	# ivtmp$35,, _216
	l32r	a4, .LC8	#,
	add.n	a14, a3, a2	# _821, ivtmp$34, tmp548
	l32r	a2, .LC7	#,
	s32i.n	a14, sp, 4	# %sfp, _821
	s32i.n	a2, sp, 36	# %sfp,
	s32i.n	a4, sp, 40	# %sfp,
	l32i.n	a15, sp, 56	# %sfp, g12
	l32i.n	a14, sp, 52	# %sfp, g11
	j	.L25		#
.L29:
	mov.n	a12, a9	# x3, x3
	mov.n	a9, a2	# x3, x2
.L25:
# @OPUS@\upstream\celt\celt.c:173:       x0=x[i-T+2];
	l32i.n	a6, sp, 44	# %sfp,
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	l32i.n	a8, sp, 48	# %sfp,
# @OPUS@\upstream\celt\celt.c:173:       x0=x[i-T+2];
	add.n	a2, a3, a6	# tmp549, ivtmp$34,
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	extui	a7, a9, 0, 16	# tmp550, x3,
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	add.n	a4, a12, a11	# tmp559, x3, x1
# @OPUS@\upstream\celt\celt.c:173:       x0=x[i-T+2];
	l32i.n	a13, a2, 8	# MEM[base: _827, offset: 8B], x0
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	mull	a7, a7, a8	# tmp551, tmp550,
	srai	a6, a9, 16	# tmp555, x3,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	l32i.n	a2, a3, 0	# MEM[base: _831, offset: 0B], MEM[base: _831, offset: 0B]
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	mull	a6, a6, a8	# tmp556, tmp555,
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	srai	a8, a4, 16	# tmp560, tmp559,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a5, a13, a5	# tmp571, x0, x4
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	srai	a7, a7, 15	# tmp552, tmp551,
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	mull	a8, a8, a14	# tmp561, tmp560, g11
	extui	a4, a4, 0, 16	# tmp567, tmp559
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a7, a7, a2	# tmp553, tmp552, MEM[base: _831, offset: 0B]
# @OPUS@\upstream\celt\celt.c:175:                + MULT16_32_Q15(g10,x2)
	slli	a6, a6, 1	# tmp557, tmp556,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	srai	a2, a5, 16	# tmp572, tmp571,
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	mull	a4, a4, a14	# tmp568, tmp567, g11
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a6, a7, a6	# tmp558, tmp553, tmp557
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	slli	a8, a8, 1	# tmp562, tmp561,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	mull	a2, a2, a15	# tmp573, tmp572, g12
	extui	a5, a5, 0, 16	# tmp579, tmp571
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a6, a6, a8	# tmp563, tmp558, tmp562
# @OPUS@\upstream\celt\celt.c:176:                + MULT16_32_Q15(g11,ADD32(x1,x3))
	srai	a4, a4, 15	# tmp569, tmp568,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	mull	a5, a5, a15	# tmp580, tmp579, g12
	slli	a2, a2, 1	# tmp574, tmp573,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a6, a6, a4	# tmp570, tmp563, tmp569
	add.n	a6, a6, a2	# tmp575, tmp570, tmp574
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	srai	a5, a5, 15	# tmp581, tmp580,
# @OPUS@\upstream\celt\celt.c:178:       y[i] = SATURATE(y[i], SIG_SAT);
	l32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\celt.c:177:                + MULT16_32_Q15(g12,ADD32(x0,x4));
	add.n	a6, a6, a5	# tmp583, tmp575, tmp581
	addi.n	a3, a3, 4	# ivtmp$34, ivtmp$34,
# @OPUS@\upstream\celt\celt.c:178:       y[i] = SATURATE(y[i], SIG_SAT);
	bge	a6, a2, .L23	# tmp583,,
	mov.n	a6, a2	# tmp583,
.L23:
# @OPUS@\upstream\celt\celt.c:178:       y[i] = SATURATE(y[i], SIG_SAT);
	l32i.n	a4, sp, 40	# %sfp,
	bge	a4, a6, .L24	#, tmp589,
	mov.n	a6, a4	# tmp589,
.L24:
	s32i.n	a6, a10, 0	# MEM[base: _825, offset: 0B], tmp589
# @OPUS@\upstream\celt\celt.c:171:    for (i=0;i<N;i++)
	l32i.n	a6, sp, 4	# %sfp,
	mov.n	a2, a11	# x2, x1
	mov.n	a5, a12	# x4, x3
	addi.n	a10, a10, 4	# ivtmp$35, ivtmp$35,
# @OPUS@\upstream\celt\celt.c:182:       x1=x0;
	mov.n	a11, a13	# x1, x0
# @OPUS@\upstream\celt\celt.c:171:    for (i=0;i<N;i++)
	bne	a6, a3, .L29	#, ivtmp$34,
.L10:
# @OPUS@\upstream\celt\celt.c:256: }
	l32i	a0, sp, 156	#,
	movi	a9, 0xa0	#,
	l32i	a12, sp, 152	#,
	l32i	a13, sp, 148	#,
	l32i	a14, sp, 144	#,
	l32i	a15, sp, 140	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	comb_filter, .-comb_filter
	.section	.text.init_caps,"ax",@progbits
	.literal_position
	.align	4
	.global	init_caps
	.type	init_caps, @function
# Function: init_caps
# Module: upstream/celt/celt.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: };
# C context:
# C context:
# C context: void init_caps(const CELTMode *m,int *cap,int LM,int C)
# C context: {
# C context: int i;
# C context: for (i=0;i<m->nbEBands;i++)
# C context: {
init_caps:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	l32i.n	a11, a2, 8	# m_33(D)->nbEBands, _29
# @OPUS@\upstream\celt\celt.c:273: {
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	blti	a11, 1, .L34	# _29,,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	slli	a9, a4, 1	# tmp73, LM,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	addi.n	a6, a5, -1	# tmp74, C,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	l32i	a10, a2, 96	# m_33(D)->cache.caps, _13
	l32i.n	a8, a2, 24	# m_33(D)->eBands, ivtmp$51
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	add.n	a9, a9, a6	# _16, tmp73, tmp74
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	movi.n	a7, 0	# i,
.L36:
# @OPUS@\upstream\celt\celt.c:278:       N=(m->eBands[i+1]-m->eBands[i])<<LM;
	l16si	a6, a8, 2	# MEM[base: _78, offset: 2B], tmp75
# @OPUS@\upstream\celt\celt.c:278:       N=(m->eBands[i+1]-m->eBands[i])<<LM;
	l16si	a13, a8, 0	# MEM[base: _78, offset: 0B], tmp78
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	mull	a12, a9, a11	# tmp84, _16, _29
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	add.n	a11, a10, a7	# tmp85, _13, i
# @OPUS@\upstream\celt\celt.c:278:       N=(m->eBands[i+1]-m->eBands[i])<<LM;
	sub	a6, a6, a13	# tmp81, tmp75, tmp78
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	add.n	a11, a11, a12	# tmp86, tmp85, tmp84
	l8ui	a11, a11, 0	# *_20, *_20
# @OPUS@\upstream\celt\celt.c:278:       N=(m->eBands[i+1]-m->eBands[i])<<LM;
	ssl	a4	# LM
	sll	a6, a6	# N, tmp81
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	mull	a6, a6, a5	# tmp83, N, C
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	addi	a11, a11, 64	# tmp88, *_20,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	mull	a6, a6, a11	# tmp89, tmp83, tmp88
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	srai	a6, a6, 2	# tmp90, tmp89,
# @OPUS@\upstream\celt\celt.c:279:       cap[i] = (m->cache.caps[m->nbEBands*(2*LM+C-1)+i]+64)*C*N>>2;
	s32i.n	a6, a3, 0	# MEM[base: _79, offset: 0B], tmp90
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	l32i.n	a11, a2, 8	# m_33(D)->nbEBands, _29
	addi.n	a8, a8, 2	# ivtmp$51, ivtmp$51,
	addi.n	a3, a3, 4	# ivtmp$52, ivtmp$52,
# @OPUS@\upstream\celt\celt.c:275:    for (i=0;i<m->nbEBands;i++)
	blt	a7, a11, .L36	# i, _29,
.L34:
# @OPUS@\upstream\celt\celt.c:281: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	init_caps, .-init_caps
	.section	.rodata.opus_strerror.str1.4,"aMS",@progbits,1
	.align	4
.LC9:
	.string	"unknown error"
	.section	.text.opus_strerror,"ax",@progbits
	.literal_position
	.literal .LC10, .LC9
	.literal .LC11, error_strings$3953
	.align	4
	.global	opus_strerror
	.type	opus_strerror, @function
# Function: opus_strerror
# Module: upstream/celt/celt.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context:
# C context:
# C context: const char *opus_strerror(int error)
# C context: {
# C context: static const char * const error_strings[8] = {
# C context: "success",
# C context: "invalid argument",
opus_strerror:
# @OPUS@\upstream\celt\celt.c:297:    if (error > 0 || error < -7)
	addi.n	a4, a2, 7	# tmp47, error,
# @OPUS@\upstream\celt\celt.c:298:       return "unknown error";
	l32r	a3, .LC10	#, <retval>
# @OPUS@\upstream\celt\celt.c:297:    if (error > 0 || error < -7)
	bgeui	a4, 8, .L38	# tmp47,,
# @OPUS@\upstream\celt\celt.c:300:       return error_strings[-error];
	l32r	a3, .LC11	#, tmp48
	slli	a2, a2, 2	# tmp50, error,
	sub	a2, a3, a2	# tmp51, tmp48, tmp50
	l32i.n	a3, a2, 0	# error_strings, <retval>
.L38:
# @OPUS@\upstream\celt\celt.c:301: }
	mov.n	a2, a3	#, <retval>
	ret.n
	.size	opus_strerror, .-opus_strerror
	.section	.rodata.opus_get_version_string.str1.4,"aMS",@progbits,1
	.align	4
.LC12:
	.string	"libopus 1.5.2-fixed"
	.section	.text.opus_get_version_string,"ax",@progbits
	.literal_position
	.literal .LC13, .LC12
	.align	4
	.global	opus_get_version_string
	.type	opus_get_version_string, @function
# Function: opus_get_version_string
# Module: upstream/celt/celt.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return error_strings[-error];
# C context: }
# C context:
# C context: const char *opus_get_version_string(void)
# C context: {
# C context: return "libopus " PACKAGE_VERSION
# C context: /* Applications may rely on the presence of this substring in the version
# C context: string to determine if they have a fixed-point or floating-point build
opus_get_version_string:
# @OPUS@\upstream\celt\celt.c:316: }
	l32r	a2, .LC13	#,
	ret.n
	.size	opus_get_version_string, .-opus_get_version_string
	.section	.rodata.str1.4,"aMS",@progbits,1
	.align	4
.LC14:
	.string	"success"
	.align	4
.LC15:
	.string	"invalid argument"
	.align	4
.LC16:
	.string	"buffer too small"
	.align	4
.LC17:
	.string	"internal error"
	.align	4
.LC18:
	.string	"corrupted stream"
	.align	4
.LC19:
	.string	"request not implemented"
	.align	4
.LC20:
	.string	"invalid state"
	.align	4
.LC21:
	.string	"memory allocation failed"
	.section	.rodata.error_strings$3953,"a"
	.align	4
	.type	error_strings$3953, @object
	.size	error_strings$3953, 32
error_strings$3953:
	.word	.LC14
	.word	.LC15
	.word	.LC16
	.word	.LC17
	.word	.LC18
	.word	.LC19
	.word	.LC20
	.word	.LC21
	.section	.rodata.gains$3933,"a"
	.align	4
	.type	gains$3933, @object
	.size	gains$3933, 18
gains$3933:
	.short	10048
	.short	7112
	.short	4248
	.short	15200
	.short	8784
	.short	0
	.short	26208
	.short	3280
	.short	0
	.global	tf_select_table
	.section	.rodata.tf_select_table,"a"
	.align	4
	.type	tf_select_table, @object
	.size	tf_select_table, 32
tf_select_table:
	.byte	0
	.byte	-1
	.byte	0
	.byte	-1
	.byte	0
	.byte	-1
	.byte	0
	.byte	-1
	.byte	0
	.byte	-1
	.byte	0
	.byte	-2
	.byte	1
	.byte	0
	.byte	1
	.byte	-1
	.byte	0
	.byte	-2
	.byte	0
	.byte	-3
	.byte	2
	.byte	0
	.byte	1
	.byte	-1
	.byte	0
	.byte	-2
	.byte	0
	.byte	-3
	.byte	3
	.byte	0
	.byte	1
	.byte	-1
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
