# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/vq.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"vq.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\vq.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\vq.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\vq.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\vq.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\vq.c.s.raw
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
	.section	.text.exp_rotation1,"ax",@progbits
	.literal_position
	.align	4
	.type	exp_rotation1, @function
# Function: exp_rotation1
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context: #ifndef OVERRIDE_vq_exp_rotation1
# C context: static void exp_rotation1(celt_norm *X, int len, int stride, opus_val16 c, opus_val16 s)
# C context: {
# C context: int i;
# C context: opus_val16 ms;
# C context: celt_norm *Xptr;
exp_rotation1:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\vq.c:64:    ms = NEG16(s);
	neg	a9, a6	# tmp105, s
	slli	a9, a9, 16	# tmp106, tmp105,
# @OPUS@\upstream\celt\vq.c:52: {
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	sub	a3, a3, a4	# _82, len, stride
# @OPUS@\upstream\celt\vq.c:64:    ms = NEG16(s);
	srai	a9, a9, 16	# ms, tmp106,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bgei	a3, 1, .L2	# _82,,
.L6:
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	sub	a3, a3, a4	# _25, _82, stride
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	slli	a7, a3, 1	# tmp107, _25,
	addi	a7, a7, -2	# tmp109, tmp107,
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	add.n	a2, a2, a7	# Xptr, X, tmp109
# @OPUS@\upstream\celt\vq.c:78:       x2 = Xptr[stride];
	slli	a4, a4, 1	# tmp126, stride,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a8, a3, -1	# i, _25,
	add.n	a7, a2, a4	# ivtmp$66, Xptr, tmp126
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a8, .L7	# i,
	j	.L1		#
.L2:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	slli	a8, a4, 1	# tmp110, stride,
	slli	a12, a3, 1	# tmp111, _82,
	mov.n	a7, a2	# ivtmp$73, X
	add.n	a8, a2, a8	# ivtmp$74, X, tmp110
	add.n	a12, a12, a2	# _136, tmp111, X
.L5:
# @OPUS@\upstream\celt\vq.c:68:       x1 = Xptr[0];
	l16si	a10, a7, 0	# MEM[base: _147, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a13, a8, 0	# MEM[base: _145, offset: 0B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a14, a10, a6	# tmp117, x1, s
	mull	a11, a13, a5	# tmp116, x2, c
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a10, a10, a5	# tmp121, x1, c
	mull	a13, a13, a9	# tmp122, x2, ms
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a11, a11, a14	# tmp118, tmp116, tmp117
	addmi	a11, a11, 0x4000	# tmp119, tmp118,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a10, a10, a13	# tmp123, tmp121, tmp122
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a11, a11, 15	# tmp120, tmp119,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a10, a10, 0x4000	# tmp124, tmp123,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a11, a8, 0	# MEM[base: _145, offset: 0B], tmp120
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a10, a10, 15	# tmp125, tmp124,
	s16i	a10, a7, 0	# MEM[base: _147, offset: 0B], tmp125
	addi.n	a7, a7, 2	# ivtmp$73, ivtmp$73,
	addi.n	a8, a8, 2	# ivtmp$74, ivtmp$74,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a12, a7, .L5	# _136, ivtmp$73,
	j	.L6		#
.L7:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a3, a2, 0	# MEM[base: Xptr_86, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:78:       x2 = Xptr[stride];
	l16si	a10, a7, 0	# MEM[base: _156, offset: 0B], x2
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a4, a3, a6	# tmp131, x1, s
	mull	a11, a10, a5	# tmp133, x2, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a3, a5	# tmp136, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a4, a4, 0x4000	# tmp132, tmp131,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a10, a10, a9	# tmp138, x2, ms
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a4, a4, a11	# tmp134, tmp132, tmp133
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp137, tmp136,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a4, a4, 15	# tmp135, tmp134,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a10	# tmp139, tmp137, tmp138
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a4, a7, 0	# MEM[base: _156, offset: 0B], tmp135
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a2, a2, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp140, tmp139,
	s16i	a3, a2, 2	# MEM[base: Xptr_73, offset: 2B], tmp140
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a8, a8, -1	# i, i,
	addi	a7, a7, -2	# ivtmp$66, ivtmp$66,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a8, -1, .L7	# i,,
.L1:
# @OPUS@\upstream\celt\vq.c:82: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	exp_rotation1, .-exp_rotation1
	.global	__udivsi3
	.section	.text.exp_rotation,"ax",@progbits
	.literal_position
	.literal .LC1, SPREAD_FACTOR$3797
	.literal .LC2, 32767
	.align	4
	.global	exp_rotation
	.type	exp_rotation, @function
# Function: exp_rotation
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif /* OVERRIDE_vq_exp_rotation1 */
# C context:
# C context: void exp_rotation(celt_norm *X, int len, int dir, int stride, int K, int spread)
# C context: {
# C context: static const int SPREAD_FACTOR[3]={15,10,5};
# C context: int i;
# C context: opus_val16 c, s;
exp_rotation:
	addi	sp, sp, -80	#,,
	s32i	a13, sp, 68	#,
	s32i	a14, sp, 64	#,
	mov.n	a13, a3	# len, len
	s32i	a0, sp, 76	#,
	s32i	a12, sp, 72	#,
	s32i.n	a15, sp, 60	#,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	slli	a3, a6, 1	# tmp186, K,
# @OPUS@\upstream\celt\vq.c:86: {
	s32i.n	a4, sp, 8	# %sfp, dir
	s32i.n	a5, sp, 0	# %sfp, stride
	mov.n	a14, a2	# X, X
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	bge	a3, a13, .L12	# tmp186, len,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	movi.n	a3, 1	# tmp192,
	movi.n	a9, 0	# tmp189,
	moveqz	a9, a3, a7	# tmp191, tmp192, spread
	extui	a12, a9, 0, 8	# tmp194, tmp191
	bnez.n	a12, .L12	# tmp194,
# @OPUS@\upstream\celt\vq.c:96:    factor = SPREAD_FACTOR[spread-1];
	l32r	a2, .LC1	#, tmp199
	addi.n	a7, a7, -1	# tmp200, spread,
	slli	a7, a7, 2	# tmp201, tmp200,
	add.n	a7, a2, a7	# tmp202, tmp199, tmp201
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	l32i.n	a15, a7, 0	# SPREAD_FACTOR, tmp204
	slli	a7, a13, 16	# tmp195, len,
	mull	a6, a6, a15	# tmp203, K, tmp204
	srai	a4, a7, 16	# _13, tmp195,
	add.n	a15, a6, a13	# _20, tmp203, len
	slli	a7, a4, 15	# tmp197, _13,
	sub	a7, a7, a4	# tmp198, tmp197, _13
	mov.n	a2, a15	#, _20
	s32i.n	a3, sp, 36	#,
	s32i.n	a7, sp, 44	#,
	call0	celt_rcp		#
	mov.n	a4, a2	# _21,
	mov.n	a2, a15	#, _20
	s32i.n	a4, sp, 32	#,
	call0	celt_rcp		#
	mov.n	a5, a2	# _29,
	mov.n	a2, a15	#, _20
	s32i.n	a5, sp, 28	#,
	call0	celt_rcp		#
	l32i.n	a7, sp, 44	#,
	l32i.n	a5, sp, 28	#,
	l32i.n	a4, sp, 32	#,
	srai	a6, a7, 16	# _16, tmp198,
	srai	a15, a2, 16	# tmp205,,
	extui	a7, a7, 0, 16	# tmp211, tmp198
	extui	a5, a5, 0, 16	# tmp214, _29,
	mull	a15, a15, a7	# tmp212, tmp205, tmp211
	mull	a5, a5, a6	# tmp215, tmp214, _16
	srai	a4, a4, 16	# tmp220, _21,
	mull	a4, a4, a6	# tmp221, tmp220, _16
	srai	a5, a5, 15	# tmp216, tmp215,
	srai	a15, a15, 15	# tmp213, tmp212,
	slli	a4, a4, 1	# tmp222, tmp221,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a15, a15, a5	# tmp219, tmp213, tmp216
	add.n	a15, a15, a4	# tmp225, tmp219, tmp222
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	mul16s	a15, a15, a15	# tmp227, tmp225, tmp225
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	s32i.n	a12, sp, 40	#, tmp9
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	srai	a15, a15, 16	# _48, tmp227,
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	mov.n	a2, a15	#, _48
	call0	celt_cos_norm		#
	mov.n	a12, a2	# c,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	l32r	a2, .LC2	#, tmp230
	sub	a2, a2, a15	#, tmp230, _48
	call0	celt_cos_norm		#
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	mov.n	a7, a2	# s,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	slli	a2, a4, 3	# tmp232,,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a3, sp, 36	#,
	l32i.n	a9, sp, 40	#,
	blt	a13, a2, .L16	# len, tmp232,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	srai	a5, a4, 2	# _59,,
# @OPUS@\upstream\celt\vq.c:106:       stride2 = 1;
	mov.n	a9, a3	# stride2, tmp192
	mov.n	a6, a4	# stride, ivtmp$120
	j	.L17		#
.L37:
# @OPUS@\upstream\celt\vq.c:110:          stride2++;
	mov.n	a9, a3	# stride2, stride2
.L17:
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	addi.n	a3, a9, 1	# stride2, stride2,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	mull	a2, a4, a3	# tmp233, ivtmp$120, stride2
	add.n	a4, a4, a6	# ivtmp$120, ivtmp$120, stride
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	add.n	a2, a2, a5	# _60, tmp233, _59
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	blt	a2, a13, .L37	# _60, len,
.L16:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a3, sp, 0	# %sfp,
	mov.n	a2, a13	#, len
	s32i.n	a7, sp, 44	#,
	s32i.n	a9, sp, 40	#,
	call0	__udivsi3		#
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a2, sp, 0	# %sfp,
	l32i.n	a7, sp, 44	#,
	l32i.n	a9, sp, 40	#,
	blti	a2, 1, .L12	#,,
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	l32i.n	a3, sp, 20	# %sfp,
	neg	a15, a7	# tmp240, s
	slli	a2, a3, 1	# tmp237,,
	addi	a2, a2, -6	#, tmp237,
	addi.n	a8, a2, 6	# _362,,
	s32i.n	a2, sp, 12	# %sfp,
	slli	a15, a15, 16	# tmp241, tmp240,
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	neg	a2, a12	# tmp309, c
	srai	a15, a15, 16	# _419, tmp241,
	slli	a2, a2, 16	#, tmp309,
	addi	a13, a14, -2	# tmp242, ivtmp$109,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	addi.n	a4, a3, -1	#,,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi	a11, a3, -3	# i,,
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	s32i.n	a2, sp, 24	# %sfp,
	mov.n	a2, a15	# _419, _419
	s32i.n	a9, sp, 4	# %sfp, stride2
	mov.n	a15, a7	# s, s
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	s32i.n	a4, sp, 16	# %sfp,
	add.n	a13, a13, a8	# ivtmp$113, tmp242, _362
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	movi.n	a10, 0	# i,
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	mov.n	a9, a11	# i, i
	mov.n	a7, a2	# _419, _419
.L35:
# @OPUS@\upstream\celt\vq.c:117:       if (dir < 0)
	l32i.n	a2, sp, 8	# %sfp,
	bgez	a2, .L19	#,
# @OPUS@\upstream\celt\vq.c:119:          if (stride2)
	l32i.n	a3, sp, 4	# %sfp,
	beqz.n	a3, .L20	#,
# @OPUS@\upstream\celt\vq.c:120:             exp_rotation1(X+i*len, len, stride2, s, c);
	mov.n	a4, a3	#,
	l32i.n	a3, sp, 20	# %sfp,
	mov.n	a6, a12	#, c
	mov.n	a5, a15	#, s
	mov.n	a2, a14	#, ivtmp$109
	s32i.n	a7, sp, 44	#,
	s32i.n	a8, sp, 32	#,
	s32i.n	a9, sp, 40	#,
	s32i.n	a10, sp, 28	#,
	call0	exp_rotation1		#
	l32i.n	a10, sp, 28	#,
	l32i.n	a9, sp, 40	#,
	l32i.n	a8, sp, 32	#,
	l32i.n	a7, sp, 44	#,
.L20:
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	l32i.n	a4, sp, 16	# %sfp,
	bgei	a4, 1, .L21	#,,
.L25:
	l32i.n	a2, sp, 12	# %sfp,
	add.n	a4, a2, a14	# Xptr,, ivtmp$109
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a9, .L22	# i,
	j	.L26		#
.L21:
	l16si	a2, a14, 0	# MEM[base: _351, offset: 0B], Xptr__lsm0$76
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	mov.n	a4, a14	# ivtmp$92, ivtmp$109
.L24:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a5, a4, 2	# MEM[base: _379, offset: 2B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a2, a15	# tmp247, Xptr__lsm0$76, s
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a2, a12	# tmp253, Xptr__lsm0$76, c
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a6, a5, a12	# tmp249, x2, c
	addmi	a2, a11, 0x4000	# tmp248, tmp247,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a7	# tmp255, x2, _419
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a2, a2, a6	# tmp250, tmp248, tmp249
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp254, tmp253,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	slli	a2, a2, 1	# tmp252, tmp250,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a5	# tmp256, tmp254, tmp255
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a2, a2, 16	# _114, tmp252,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp257, tmp256,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a2, a4, 2	# MEM[base: _379, offset: 2B], _114
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a3, a4, 0	# MEM[base: _379, offset: 0B], tmp257
	addi.n	a4, a4, 2	# ivtmp$92, ivtmp$92,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a13, a4, .L24	# ivtmp$113, ivtmp$92,
	j	.L25		#
.L22:
	addi	a2, a13, -2	# tmp258, ivtmp$113,
	l16si	a2, a2, 0	# MEM[base: _328, offset: 0B], Xptr__lsm0$75
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	mov.n	a6, a9	# i, i
.L27:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a5, a4, 0	# MEM[base: Xptr_121, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a3, a2, a12	# tmp263, Xptr__lsm0$75, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a2, a2, a7	# tmp268, Xptr__lsm0$75, _419
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a5, a15	# tmp265, x1, s
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a12	# tmp270, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a3, a3, 0x4000	# tmp264, tmp263,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a2, a2, 0x4000	# tmp269, tmp268,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a3, a3, a11	# tmp266, tmp264, tmp265
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a2, a2, a5	# tmp271, tmp269, tmp270
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a3, a3, 15	# tmp267, tmp266,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	slli	a2, a2, 1	# tmp273, tmp271,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a3, a4, 2	# MEM[base: Xptr_121, offset: 2B], tmp267
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a2, a2, 16	# Xptr__lsm0$75, tmp273,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a4, a4, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a2, a4, 2	# MEM[base: Xptr_155, offset: 2B], Xptr__lsm0$75
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a6, a6, -1	# i, i,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a6, -1, .L27	# i,,
	j	.L26		#
.L19:
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	l32i.n	a3, sp, 16	# %sfp,
	bgei	a3, 1, .L28	#,,
.L32:
	l32i.n	a2, sp, 12	# %sfp,
	add.n	a4, a2, a14	# Xptr,, ivtmp$109
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a9, .L29	# i,
	j	.L30		#
.L28:
	l16si	a2, a14, 0	# MEM[base: _351, offset: 0B], Xptr__lsm0$78
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	mov.n	a4, a14	# ivtmp$103, ivtmp$109
.L31:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a5, a4, 2	# MEM[base: _366, offset: 2B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a7, a2	# tmp278, _419, Xptr__lsm0$78
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a2, a12	# tmp284, Xptr__lsm0$78, c
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a6, a5, a12	# tmp280, x2, c
	addmi	a2, a11, 0x4000	# tmp279, tmp278,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a15	# tmp286, x2, s
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a2, a2, a6	# tmp281, tmp279, tmp280
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp285, tmp284,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	slli	a2, a2, 1	# tmp283, tmp281,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a5	# tmp287, tmp285, tmp286
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a2, a2, 16	# _179, tmp283,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp288, tmp287,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a2, a4, 2	# MEM[base: _366, offset: 2B], _179
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a3, a4, 0	# MEM[base: _366, offset: 0B], tmp288
	addi.n	a4, a4, 2	# ivtmp$103, ivtmp$103,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a13, a4, .L31	# ivtmp$113, ivtmp$103,
	j	.L32		#
.L30:
# @OPUS@\upstream\celt\vq.c:124:          if (stride2)
	l32i.n	a3, sp, 4	# %sfp,
	beqz.n	a3, .L26	#,
	j	.L33		#
.L29:
	addi	a2, a13, -2	# tmp289, ivtmp$113,
	l16si	a2, a2, 0	# MEM[base: _335, offset: 0B], Xptr__lsm0$77
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	mov.n	a6, a9	# i, i
.L34:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a5, a4, 0	# MEM[base: Xptr_170, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a3, a2, a12	# tmp294, Xptr__lsm0$77, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a2, a2, a15	# tmp299, Xptr__lsm0$77, s
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a7, a5	# tmp296, _419, x1
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a12	# tmp301, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a3, a3, 0x4000	# tmp295, tmp294,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a2, a2, 0x4000	# tmp300, tmp299,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a3, a3, a11	# tmp297, tmp295, tmp296
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a2, a2, a5	# tmp302, tmp300, tmp301
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a3, a3, 15	# tmp298, tmp297,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	slli	a2, a2, 1	# tmp304, tmp302,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a3, a4, 2	# MEM[base: Xptr_170, offset: 2B], tmp298
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a2, a2, 16	# Xptr__lsm0$77, tmp304,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a4, a4, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a2, a4, 2	# MEM[base: Xptr_220, offset: 2B], Xptr__lsm0$77
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a6, a6, -1	# i, i,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a6, -1, .L34	# i,,
	j	.L30		#
.L33:
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	l32i.n	a4, sp, 24	# %sfp,
	l32i.n	a3, sp, 20	# %sfp,
	srai	a6, a4, 16	#,,
	l32i.n	a4, sp, 4	# %sfp,
	mov.n	a5, a15	#, s
	mov.n	a2, a14	#, ivtmp$109
	s32i.n	a7, sp, 44	#,
	s32i.n	a8, sp, 32	#,
	s32i.n	a9, sp, 40	#,
	s32i.n	a10, sp, 28	#,
	call0	exp_rotation1		#
	l32i.n	a10, sp, 28	#,
	l32i.n	a9, sp, 40	#,
	l32i.n	a8, sp, 32	#,
	l32i.n	a7, sp, 44	#,
.L26:
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	addi.n	a10, a10, 1	# i, i,
	add.n	a14, a14, a8	# ivtmp$109, ivtmp$109, _362
	add.n	a13, a13, a8	# ivtmp$113, ivtmp$113, _362
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	bne	a2, a10, .L35	#, i,
.L12:
# @OPUS@\upstream\celt\vq.c:128: }
	l32i	a0, sp, 76	#,
	l32i	a12, sp, 72	#,
	l32i	a13, sp, 68	#,
	l32i	a14, sp, 64	#,
	l32i.n	a15, sp, 60	#,
	addi	sp, sp, 80	#,,
	ret.n
	.size	exp_rotation, .-exp_rotation
	.section	.text.op_pvq_search_c,"ax",@progbits
	.literal_position
	.literal .LC4, 16384
	.align	4
	.global	op_pvq_search_c
	.type	op_pvq_search_c, @function
# Function: op_pvq_search_c
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return collapse_mask;
# C context: }
# C context:
# C context: opus_val16 op_pvq_search_c(celt_norm *X, int *iy, int K, int N, int arch)
# C context: {
# C context: VARDECL(celt_norm, y);
# C context: VARDECL(int, signx);
# C context: int i, j;
op_pvq_search_c:
	addi	sp, sp, -96	#,,
	s32i	a0, sp, 92	#,
	s32i	a13, sp, 84	#,
	s32i	a15, sp, 76	#,
	mov.n	a13, a5	# N, N
	s32i.n	a4, sp, 16	# %sfp, K
	s32i	a12, sp, 88	#,
	s32i	a14, sp, 80	#,
# @OPUS@\upstream\celt\vq.c:177: {
	s32i.n	a2, sp, 20	# %sfp, X
	s32i.n	a3, sp, 28	# %sfp, iy
# @OPUS@\upstream\celt\vq.c:185:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:188:    ALLOC(y, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a13	#, N
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:189:    ALLOC(signx, N, int);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	mov.n	a2, a13	#, N
	call0	yoradio_opus_scratch_alloc		#
	l32i.n	a5, sp, 28	# %sfp,
	l32i.n	a6, sp, 20	# %sfp, ivtmp$140
	l32i.n	a15, sp, 24	# %sfp, ivtmp$142
# @OPUS@\upstream\celt\vq.c:193:    j=0; do {
	movi.n	a4, 0	# j,
	s32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\vq.c:189:    ALLOC(signx, N, int);
	mov.n	a7, a5	# ivtmp$151,
	s32i.n	a2, sp, 44	# %sfp,
	mov.n	a8, a15	# ivtmp$152, ivtmp$142
	mov.n	a5, a2	# ivtmp$150,
	mov.n	a3, a6	# ivtmp$149, ivtmp$140
# @OPUS@\upstream\celt\vq.c:197:       iy[j] = 0;
	mov.n	a9, a4	# tmp186, j
.L48:
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	l16si	a2, a3, 0	# MEM[base: _139, offset: 0B], _6
# @OPUS@\upstream\celt\vq.c:199:    } while (++j<N);
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	extui	a10, a2, 31, 1	# tmp184, _6,
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	s32i.n	a10, a5, 0	# MEM[base: _135, offset: 0B], tmp184
# @OPUS@\upstream\celt\vq.c:196:       X[j] = ABS16(X[j]);
	abs	a2, a2	# tmp185, _6
# @OPUS@\upstream\celt\vq.c:196:       X[j] = ABS16(X[j]);
	s16i	a2, a3, 0	# MEM[base: _139, offset: 0B], tmp185
# @OPUS@\upstream\celt\vq.c:197:       iy[j] = 0;
	s32i.n	a9, a7, 0	# MEM[base: _121, offset: 0B], tmp186
# @OPUS@\upstream\celt\vq.c:198:       y[j] = 0;
	s16i	a9, a8, 0	# MEM[base: _73, offset: 0B], tmp186
	addi.n	a3, a3, 2	# ivtmp$149, ivtmp$149,
	addi.n	a5, a5, 4	# ivtmp$150, ivtmp$150,
	addi.n	a7, a7, 4	# ivtmp$151, ivtmp$151,
	addi.n	a8, a8, 2	# ivtmp$152, ivtmp$152,
# @OPUS@\upstream\celt\vq.c:199:    } while (++j<N);
	blt	a4, a13, .L48	# j, N,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	l32i.n	a7, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	srai	a2, a13, 1	# tmp188, N,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	bge	a2, a7, .L62	# tmp188,,
# @OPUS@\upstream\celt\vq.c:192:    sum = 0;
	movi.n	a12, 0	# sum,
	l32i.n	a3, sp, 20	# %sfp, ivtmp$146
# @OPUS@\upstream\celt\vq.c:209:       j=0; do {
	mov.n	a2, a12	# j, sum
.L50:
# @OPUS@\upstream\celt\vq.c:210:          sum += X[j];
	l16si	a4, a3, 0	# MEM[base: _186, offset: 0B], tmp189
# @OPUS@\upstream\celt\vq.c:211:       }  while (++j<N);
	addi.n	a2, a2, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:210:          sum += X[j];
	add.n	a12, a12, a4	# sum, sum, tmp189
	addi.n	a3, a3, 2	# ivtmp$146, ivtmp$146,
# @OPUS@\upstream\celt\vq.c:211:       }  while (++j<N);
	blt	a2, a13, .L50	# j, N,
# @OPUS@\upstream\celt\vq.c:215:       if (sum <= K)
	l32i.n	a5, sp, 16	# %sfp,
	blt	a5, a12, .L51	#, sum,
# @OPUS@\upstream\celt\vq.c:222:          X[0] = QCONST16(1.f,14);
	l32r	a12, .LC4	#, sum
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:224:             X[j]=0;
	movi.n	a4, 2	# tmp198,
# @OPUS@\upstream\celt\vq.c:222:          X[0] = QCONST16(1.f,14);
	s16i	a12, a7, 0	# *X_157(D), sum
# @OPUS@\upstream\celt\vq.c:224:             X[j]=0;
	blt	a13, a4, .L53	# N,,
	slli	a4, a13, 1	# tmp199, N,
	addi	a4, a4, -2	# tmp198, tmp199,
.L53:
	l32i.n	a5, sp, 20	# %sfp,
	movi.n	a3, 0	#,
	addi.n	a2, a5, 2	#,,
	s32i.n	a6, sp, 52	#,
	call0	memset		#
# @OPUS@\upstream\celt\vq.c:226:          sum = QCONST16(1.f,14);
	l32i.n	a6, sp, 52	#,
.L51:
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	l32i.n	a7, sp, 16	# %sfp,
	mov.n	a2, a12	#, sum
	slli	a14, a7, 16	# tmp205,,
	s32i.n	a6, sp, 52	#,
	call0	celt_rcp		#
	srai	a14, a14, 16	# _27, tmp205,
	srai	a2, a2, 16	# tmp206,,
	mul16s	a3, a2, a14	# tmp207, tmp206, _27
	mov.n	a2, a12	#, sum
	slli	a12, a3, 16	# tmp208, tmp207,
	call0	celt_rcp		#
	extui	a11, a2, 0, 16	# tmp209,
	mull	a11, a11, a14	# tmp210, tmp209, _27
	srai	a12, a12, 16	# _31, tmp208,
	srai	a11, a11, 16	# tmp211, tmp210,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	add.n	a11, a12, a11	# tmp213, _31, tmp211
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	movi.n	a14, 0	# <retval>,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	slli	a11, a11, 16	# tmp214, tmp213,
	l32i.n	a10, sp, 28	# %sfp, ivtmp$141
	l32i.n	a9, sp, 16	# %sfp, pulsesLeft
# @OPUS@\upstream\celt\vq.c:234:       j=0; do {
	l32i.n	a6, sp, 52	#,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	srai	a11, a11, 16	# rcp, tmp214,
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	mov.n	a5, a14	# xy, <retval>
# @OPUS@\upstream\celt\vq.c:234:       j=0; do {
	mov.n	a8, a14	# j, <retval>
.L54:
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	l16ui	a3, a6, 0	# MEM[base: _94, offset: 0B],
# @OPUS@\upstream\celt\vq.c:246:       }  while (++j<N);
	addi.n	a8, a8, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	mul16s	a3, a3, a11	# tmp215, MEM[base: _94, offset: 0B], rcp
	srai	a3, a3, 15	# _46, tmp215,
# @OPUS@\upstream\celt\vq.c:241:          y[j] = (celt_norm)iy[j];
	slli	a2, a3, 16	# tmp217, _46,
	srai	a2, a2, 16	# _48, tmp217,
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	s32i.n	a3, a10, 0	# MEM[base: _184, offset: 0B], _46
# @OPUS@\upstream\celt\vq.c:241:          y[j] = (celt_norm)iy[j];
	s16i	a2, a15, 0	# MEM[base: _204, offset: 0B], _48
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	l16ui	a7, a6, 0	# MEM[base: _94, offset: 0B],
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	mull	a4, a2, a2	# tmp218, _48, _48
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	mul16s	a7, a7, a2	# tmp222, MEM[base: _94, offset: 0B], _48
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	add.n	a4, a14, a4	# tmp220, <retval>, tmp218
# @OPUS@\upstream\celt\vq.c:244:          y[j] *= 2;
	slli	a2, a2, 1	# tmp224, _48,
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	slli	a4, a4, 16	# tmp221, tmp220,
# @OPUS@\upstream\celt\vq.c:244:          y[j] *= 2;
	s16i	a2, a15, 0	# MEM[base: _204, offset: 0B], tmp224
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	srai	a14, a4, 16	# <retval>, tmp221,
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	add.n	a5, a5, a7	# xy, xy, tmp222
# @OPUS@\upstream\celt\vq.c:245:          pulsesLeft -= iy[j];
	sub	a9, a9, a3	# pulsesLeft, pulsesLeft, _46
	addi.n	a6, a6, 2	# ivtmp$140, ivtmp$140,
	addi.n	a10, a10, 4	# ivtmp$141, ivtmp$141,
	addi.n	a15, a15, 2	# ivtmp$142, ivtmp$142,
# @OPUS@\upstream\celt\vq.c:246:       }  while (++j<N);
	blt	a8, a13, .L54	# j, N,
	j	.L49		#
.L62:
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	movi.n	a14, 0	# <retval>,
	mov.n	a9, a7	# pulsesLeft,
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	mov.n	a5, a14	# xy, <retval>
.L49:
# @OPUS@\upstream\celt\vq.c:255:    if (pulsesLeft > N+3)
	addi.n	a2, a13, 3	# tmp225, N,
# @OPUS@\upstream\celt\vq.c:255:    if (pulsesLeft > N+3)
	blt	a2, a9, .L55	# tmp225, pulsesLeft,
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	bgei	a9, 1, .L56	# pulsesLeft,,
	j	.L57		#
.L55:
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	l32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	l16ui	a2, a5, 0	# *y_153,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	l32i.n	a3, a6, 0	# *iy_160(D), *iy_160(D)
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	add.n	a2, a9, a2	# tmp228, pulsesLeft, *y_153
	mul16s	a2, a9, a2	# tmp229, pulsesLeft, tmp228
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	add.n	a9, a3, a9	# tmp233, *iy_160(D), pulsesLeft
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	add.n	a14, a14, a2	# tmp231, <retval>, tmp229
	slli	a14, a14, 16	# tmp232, tmp231,
	srai	a14, a14, 16	# <retval>, tmp232,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	s32i.n	a9, a6, 0	# *iy_160(D), tmp233
	j	.L57		#
.L56:
	l32i.n	a7, sp, 16	# %sfp,
	l32i.n	a3, sp, 24	# %sfp,
	addi.n	a2, a7, 1	# tmp235,,
	sub	a2, a2, a9	#, tmp235, pulsesLeft
	add.n	a9, a9, a2	#, pulsesLeft,
	s32i.n	a2, sp, 16	# %sfp,
	l32i.n	a2, sp, 20	# %sfp,
	addi.n	a3, a3, 2	#,,
	addi.n	a2, a2, 2	#,,
	s32i.n	a9, sp, 32	# %sfp,
	s32i.n	a2, sp, 40	# %sfp,
	s32i.n	a3, sp, 36	# %sfp,
.L60:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	l32i.n	a4, sp, 16	# %sfp,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a6, 0x1f	#,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a9, a4	# _440,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	sub	a9, a6, a9	# tmp238,, _440
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	l16si	a8, a7, 0	# *X_157(D), tmp243
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	slli	a9, a9, 16	# tmp240, tmp238,
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	srai	a9, a9, 16	# tmp239, tmp240,
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	addi.n	a9, a9, 1	# rshift, tmp239,
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	addi.n	a14, a14, 1	# tmp241, <retval>,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	add.n	a8, a8, a5	# tmp246, tmp243, xy
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	l16ui	a12, a6, 0	# *y_153,
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	slli	a14, a14, 16	# tmp242, tmp241,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	ssr	a9	# rshift
	sra	a8, a8	# tmp247, tmp246
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	srai	a14, a14, 16	# yy, tmp242,
# @OPUS@\upstream\celt\vq.c:291:       Rxy = MULT16_16_Q15(Rxy,Rxy);
	mul16s	a8, a8, a8	# tmp252, tmp247, tmp247
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	add.n	a12, a14, a12	# tmp250, yy, *y_153
	slli	a12, a12, 16	# tmp251, tmp250,
# @OPUS@\upstream\celt\vq.c:293:       best_num = Rxy;
	slli	a8, a8, 1	# tmp253, tmp252,
	l32i.n	a7, sp, 40	# %sfp, ivtmp$129
	l32i.n	a6, sp, 36	# %sfp, ivtmp$131
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	srai	a12, a12, 16	# best_den, tmp251,
# @OPUS@\upstream\celt\vq.c:293:       best_num = Rxy;
	srai	a8, a8, 16	# best_num, tmp253,
# @OPUS@\upstream\celt\vq.c:276:       best_id = 0;
	movi.n	a15, 0	# best_id,
# @OPUS@\upstream\celt\vq.c:294:       j=1;
	movi.n	a4, 1	# j,
.L59:
# @OPUS@\upstream\celt\vq.c:297:          Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[j])),rshift));
	l16si	a2, a7, 0	# MEM[base: _405, offset: 0B], tmp254
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	l16ui	a3, a6, 0	# MEM[base: _396, offset: 0B],
# @OPUS@\upstream\celt\vq.c:297:          Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[j])),rshift));
	add.n	a2, a2, a5	# tmp257, tmp254, xy
	ssr	a9	# rshift
	sra	a2, a2	# tmp258, tmp257
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	mul16s	a2, a2, a2	# tmp263, tmp258, tmp258
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	add.n	a3, a14, a3	# tmp261, yy, MEM[base: _396, offset: 0B]
	slli	a3, a3, 16	# tmp262, tmp261,
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	slli	a2, a2, 1	# tmp264, tmp263,
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	srai	a3, a3, 16	# Ryy, tmp262,
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	srai	a2, a2, 16	# Rxy, tmp264,
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	mull	a11, a3, a8	# tmp265, Ryy, best_num
	mull	a10, a2, a12	# tmp266, Rxy, best_den
	addi.n	a7, a7, 2	# ivtmp$129, ivtmp$129,
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	bge	a11, a10, .L58	# tmp265, tmp266,
	mov.n	a15, a4	# best_id, j
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	mov.n	a12, a3	# best_den, Ryy
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	mov.n	a8, a2	# best_num, Rxy
.L58:
# @OPUS@\upstream\celt\vq.c:316:       } while (++j<N);
	addi.n	a4, a4, 1	# j, j,
	addi.n	a6, a6, 2	# ivtmp$131, ivtmp$131,
	blt	a4, a13, .L59	# j, N,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	l32i.n	a7, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	slli	a3, a15, 1	# _369, best_id,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	add.n	a4, a7, a3	# _364,, _369
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	l32i.n	a7, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	l16si	a2, a4, 0	# *_364, _363
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	slli	a15, a15, 2	# tmp276, best_id,
	add.n	a15, a6, a15	# _358,, tmp276
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	add.n	a3, a7, a3	# tmp267,, _369
	l16si	a3, a3, 0	# *_368, tmp268
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	l32i.n	a6, a15, 0	# *_358, *_358
# @OPUS@\upstream\celt\vq.c:325:       y[best_id] += 2;
	addi.n	a7, a2, 2	# tmp275, _363,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	add.n	a14, a2, a14	# tmp273, _363, yy
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:325:       y[best_id] += 2;
	s16i	a7, a4, 0	# *_364, tmp275
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	addi.n	a6, a6, 1	# tmp277, *_358,
	addi.n	a2, a2, 1	#,,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	add.n	a5, a5, a3	# xy, xy, tmp268
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	slli	a14, a14, 16	# tmp274, tmp273,
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	s32i.n	a6, a15, 0	# *_358, tmp277
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	srai	a14, a14, 16	# <retval>, tmp274,
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	bne	a3, a2, .L60	#,,
.L57:
# @OPUS@\upstream\celt\vq.c:330:    j=0;
	l32i.n	a4, sp, 48	# %sfp, ivtmp$123
	l32i.n	a5, sp, 44	# %sfp, ivtmp$124
	movi.n	a3, 0	# j,
.L61:
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	l32i.n	a6, a5, 0	# MEM[base: _417, offset: 0B], _112
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	l32i.n	a7, a4, 0	# MEM[base: _422, offset: 0B], MEM[base: _422, offset: 0B]
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	neg	a2, a6	# tmp279, _112
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	xor	a2, a2, a7	# tmp280, tmp279, MEM[base: _422, offset: 0B]
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	add.n	a2, a2, a6	# tmp282, tmp280, _112
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	s32i.n	a2, a4, 0	# MEM[base: _422, offset: 0B], tmp282
# @OPUS@\upstream\celt\vq.c:336:    } while (++j<N);
	addi.n	a3, a3, 1	# j, j,
	addi.n	a4, a4, 4	# ivtmp$123, ivtmp$123,
	addi.n	a5, a5, 4	# ivtmp$124, ivtmp$124,
	blt	a3, a13, .L61	# j, N,
# @OPUS@\upstream\celt\vq.c:337:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\vq.c:339: }
	l32i	a0, sp, 92	#,
	mov.n	a2, a14	#, <retval>
	l32i	a12, sp, 88	#,
	l32i	a13, sp, 84	#,
	l32i	a14, sp, 80	#,
	l32i	a15, sp, 76	#,
	addi	sp, sp, 96	#,,
	ret.n
	.size	op_pvq_search_c, .-op_pvq_search_c
	.section	.text.alg_quant,"ax",@progbits
	.literal_position
	.literal .LC6, 16384
	.literal .LC7, SPREAD_FACTOR$3797
	.literal .LC8, 32767
	.align	4
	.global	alg_quant
	.type	alg_quant, @function
# Function: alg_quant
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return yy;
# C context: }
# C context:
# C context: unsigned alg_quant(celt_norm *X, int N, int K, int spread, int B, ec_enc *enc,
# C context: opus_val16 gain, int resynth, int arch)
# C context: {
# C context: VARDECL(int, iy);
# C context: opus_val16 yy;
alg_quant:
	addi	sp, sp, -128	#,,
	s32i.n	a2, sp, 24	# %sfp, X
	l16si	a2, sp, 128	# gain,
	s32i	a15, sp, 108	#,
	mov.n	a15, a3	# N, N
# @OPUS@\upstream\celt\vq.c:353:    ALLOC(iy, N+3, int);
	addi.n	a3, a3, 3	#, N,
# @OPUS@\upstream\celt\vq.c:343: {
	s32i	a0, sp, 124	#,
	s32i.n	a4, sp, 48	# %sfp, K
	s32i.n	a5, sp, 60	# %sfp, spread
	s32i.n	a6, sp, 44	# %sfp, B
	s32i	a7, sp, 68	# %sfp, enc
	s32i	a12, sp, 120	#,
	s32i	a13, sp, 116	#,
	s32i	a14, sp, 112	#,
# @OPUS@\upstream\celt\vq.c:343: {
	s32i	a2, sp, 72	# %sfp,
# @OPUS@\upstream\celt\vq.c:353:    ALLOC(iy, N+3, int);
	s32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\vq.c:347:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 8	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:353:    ALLOC(iy, N+3, int);
	l32i.n	a2, sp, 32	# %sfp,
# @OPUS@\upstream\celt\vq.c:347:    SAVE_STACK;
	s32i.n	a3, sp, 12	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:353:    ALLOC(iy, N+3, int);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	l32i.n	a4, sp, 48	# %sfp,
# @OPUS@\upstream\celt\vq.c:353:    ALLOC(iy, N+3, int);
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	slli	a3, a4, 1	# tmp434,,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	movi.n	a2, 1	# tmp435,
	bge	a3, a15, .L70	# tmp434, N,
	movi.n	a2, 0	# tmp435,
.L70:
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	l32i.n	a5, sp, 60	# %sfp,
	movi.n	a14, 1	# tmp439,
	movi.n	a9, 0	# tmp440,
	moveqz	a9, a14, a5	# tmp438, tmp439,
	or	a9, a9, a2	# tmp441, tmp438, tmp435
	extui	a9, a9, 0, 8	#, tmp441
	s32i.n	a9, sp, 56	# %sfp,
	beqz.n	a9, .L71	#,
.L75:
# @OPUS@\upstream\celt\vq.c:185:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:188:    ALLOC(y, N, celt_norm);
	movi.n	a4, 0	#,
	movi.n	a3, 2	#,
	mov.n	a2, a15	#, N
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:189:    ALLOC(signx, N, int);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	mov.n	a2, a15	#, N
	call0	yoradio_opus_scratch_alloc		#
	s32i.n	a2, sp, 52	# %sfp,
	l32i.n	a6, sp, 24	# %sfp,
	l32i.n	a2, sp, 28	# %sfp,
	l32i.n	a14, sp, 20	# %sfp, ivtmp$217
# @OPUS@\upstream\celt\vq.c:193:    j=0; do {
	movi.n	a4, 0	# j,
	s32i	a6, sp, 76	# %sfp,
	s32i	a2, sp, 64	# %sfp,
# @OPUS@\upstream\celt\vq.c:189:    ALLOC(signx, N, int);
	mov.n	a7, a14	# ivtmp$227, ivtmp$217
	mov.n	a6, a2	# ivtmp$226,
	l32i.n	a5, sp, 52	# %sfp, ivtmp$225
	l32i.n	a3, sp, 24	# %sfp, ivtmp$224
# @OPUS@\upstream\celt\vq.c:197:       iy[j] = 0;
	mov.n	a8, a4	# tmp530, j
	j	.L72		#
.L71:
# @OPUS@\upstream\celt\vq.c:96:    factor = SPREAD_FACTOR[spread-1];
	addi.n	a2, a5, -1	# tmp448, tmp3,
	slli	a3, a2, 2	# tmp449, tmp448,
	l32r	a2, .LC7	#, tmp447
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\vq.c:96:    factor = SPREAD_FACTOR[spread-1];
	add.n	a2, a2, a3	# tmp450, tmp447, tmp449
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	l32i.n	a3, a2, 0	# SPREAD_FACTOR, tmp452
	slli	a4, a15, 16	# tmp443, N,
	mull	a3, a5, a3	# tmp451,, tmp452
	srai	a4, a4, 16	# _56, tmp443,
	add.n	a13, a3, a15	# _63, tmp451, N
	slli	a12, a4, 15	# tmp445, _56,
	mov.n	a2, a13	#, _63
	sub	a12, a12, a4	# tmp446, tmp445, _56
	call0	celt_rcp		#
	mov.n	a5, a2	# _64,
	mov.n	a2, a13	#, _63
	s32i	a5, sp, 84	#,
	call0	celt_rcp		#
	mov.n	a4, a2	# _72,
	mov.n	a2, a13	#, _63
	s32i	a4, sp, 80	#,
	call0	celt_rcp		#
	l32i	a4, sp, 80	#,
	l32i	a5, sp, 84	#,
	srai	a3, a12, 16	# _59, tmp446,
	srai	a2, a2, 16	# tmp453,,
	extui	a12, a12, 0, 16	# tmp459, tmp446
	extui	a4, a4, 0, 16	# tmp462, _72,
	mull	a12, a2, a12	# tmp460, tmp453, tmp459
	mull	a4, a4, a3	# tmp463, tmp462, _59
	srai	a2, a5, 16	# tmp468, _64,
	mull	a2, a2, a3	# tmp469, tmp468, _59
	srai	a13, a12, 15	# tmp461, tmp460,
	srai	a3, a4, 15	# tmp464, tmp463,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a13, a13, a3	# tmp467, tmp461, tmp464
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	slli	a2, a2, 1	# tmp470, tmp469,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a13, a13, a2	# tmp473, tmp467, tmp470
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	mul16s	a13, a13, a13	# tmp475, tmp473, tmp473
# @OPUS@\upstream\celt\vq.c:91:    int stride2=0;
	l32i.n	a6, sp, 56	# %sfp,
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	srai	a13, a13, 16	# _91, tmp475,
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	mov.n	a2, a13	#, _91
# @OPUS@\upstream\celt\vq.c:91:    int stride2=0;
	s32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	call0	celt_cos_norm		#
	mov.n	a12, a2	# c,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	l32r	a2, .LC8	#, tmp478
	sub	a2, a2, a13	#, tmp478, _91
	call0	celt_cos_norm		#
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	mov.n	a13, a2	# s,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	slli	a2, a3, 3	# tmp480,,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	blt	a15, a2, .L73	# N, tmp480,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	srai	a4, a3, 2	# _102,,
# @OPUS@\upstream\celt\vq.c:106:       stride2 = 1;
	s32i.n	a14, sp, 16	# %sfp, tmp439
	mov.n	a6, a14	# stride2, tmp439
	mov.n	a7, a3	# B, ivtmp$256
	j	.L74		#
.L118:
# @OPUS@\upstream\celt\vq.c:110:          stride2++;
	mov.n	a6, a5	# stride2, stride2
.L74:
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	addi.n	a5, a6, 1	# stride2, stride2,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	mull	a2, a3, a5	# tmp481, ivtmp$256, stride2
	add.n	a3, a3, a7	# ivtmp$256, ivtmp$256, B
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	add.n	a2, a2, a4	# _103, tmp481, _102
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	blt	a2, a15, .L118	# _103, N,
	s32i.n	a6, sp, 16	# %sfp, stride2
.L73:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a3, sp, 44	# %sfp,
	mov.n	a2, a15	#, N
	call0	__udivsi3		#
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i.n	a2, sp, 40	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	blti	a4, 1, .L75	#,,
	mov.n	a6, a2	#,
	mov.n	a4, a2	#,
	l32i.n	a5, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	slli	a2, a2, 1	# tmp485,,
	addi	a2, a2, -6	#, tmp485,
	addi.n	a11, a2, 6	# _1054,,
	s32i.n	a2, sp, 20	# %sfp,
	neg	a14, a13	# tmp488, s
	addi	a3, a5, -2	# tmp490,,
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	neg	a2, a12	# tmp757, c
	slli	a14, a14, 16	# tmp489, tmp488,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	addi.n	a6, a6, -1	#,,
	add.n	a10, a3, a11	# ivtmp$250, tmp490, _1054
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	slli	a2, a2, 16	#, tmp757,
	s32i	a15, sp, 64	# %sfp, N
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	s32i.n	a6, sp, 36	# %sfp,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi	a9, a4, -3	# i,,
	srai	a14, a14, 16	# _1241, tmp489,
	mov.n	a7, a5	# ivtmp$246,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	movi.n	a8, 0	# i,
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	s32i.n	a2, sp, 52	# %sfp,
	mov.n	a15, a10	# ivtmp$250, ivtmp$250
.L84:
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	l32i.n	a5, sp, 36	# %sfp,
	bgei	a5, 1, .L76	#,,
.L80:
	l32i.n	a6, sp, 20	# %sfp,
	add.n	a4, a6, a7	# Xptr,, ivtmp$246
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a9, .L77	# i,
	j	.L78		#
.L76:
	l16si	a2, a7, 0	# MEM[base: _125, offset: 0B], Xptr__lsm0$156
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	mov.n	a4, a7	# ivtmp$243, ivtmp$246
.L79:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a5, a4, 2	# MEM[base: _1058, offset: 2B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a10, a2, a14	# tmp495, Xptr__lsm0$156, _1241
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a2, a12	# tmp501, Xptr__lsm0$156, c
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a6, a5, a12	# tmp497, x2, c
	addmi	a2, a10, 0x4000	# tmp496, tmp495,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a13	# tmp503, x2, s
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a2, a2, a6	# tmp498, tmp496, tmp497
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp502, tmp501,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	slli	a2, a2, 1	# tmp500, tmp498,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a5	# tmp504, tmp502, tmp503
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a2, a2, 16	# _222, tmp500,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp505, tmp504,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a2, a4, 2	# MEM[base: _1058, offset: 2B], _222
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a3, a4, 0	# MEM[base: _1058, offset: 0B], tmp505
	addi.n	a4, a4, 2	# ivtmp$243, ivtmp$243,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a15, a4, .L79	# ivtmp$250, ivtmp$243,
	j	.L80		#
.L78:
# @OPUS@\upstream\celt\vq.c:124:          if (stride2)
	l32i.n	a2, sp, 16	# %sfp,
	beqz.n	a2, .L82	#,
	j	.L81		#
.L77:
	addi	a2, a15, -2	# tmp506, ivtmp$250,
	l16si	a2, a2, 0	# MEM[base: _1038, offset: 0B], Xptr__lsm0$155
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	mov.n	a6, a9	# i, i
.L83:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a5, a4, 0	# MEM[base: Xptr_606, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a3, a2, a12	# tmp511, Xptr__lsm0$155, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a2, a2, a13	# tmp516, Xptr__lsm0$155, s
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a10, a5, a14	# tmp513, x1, _1241
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a12	# tmp518, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a3, a3, 0x4000	# tmp512, tmp511,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a2, a2, 0x4000	# tmp517, tmp516,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a3, a3, a10	# tmp514, tmp512, tmp513
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a2, a2, a5	# tmp519, tmp517, tmp518
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a3, a3, 15	# tmp515, tmp514,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	slli	a2, a2, 1	# tmp521, tmp519,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a3, a4, 2	# MEM[base: Xptr_606, offset: 2B], tmp515
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a2, a2, 16	# Xptr__lsm0$155, tmp521,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a4, a4, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a2, a4, 2	# MEM[base: Xptr_263, offset: 2B], Xptr__lsm0$155
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a6, a6, -1	# i, i,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a6, -1, .L83	# i,,
	j	.L78		#
.L81:
# @OPUS@\upstream\celt\vq.c:125:             exp_rotation1(X+i*len, len, stride2, s, -c);
	l32i.n	a3, sp, 52	# %sfp,
	mov.n	a4, a2	#,
	srai	a6, a3, 16	#,,
	l32i.n	a3, sp, 40	# %sfp,
	mov.n	a2, a7	#, ivtmp$246
	mov.n	a5, a13	#, s
	s32i	a7, sp, 88	#,
	s32i	a8, sp, 84	#,
	s32i	a9, sp, 92	#,
	s32i	a11, sp, 80	#,
	call0	exp_rotation1		#
	l32i	a11, sp, 80	#,
	l32i	a9, sp, 92	#,
	l32i	a8, sp, 84	#,
	l32i	a7, sp, 88	#,
.L82:
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	addi.n	a8, a8, 1	# i, i,
	add.n	a7, a7, a11	# ivtmp$246, ivtmp$246, _1054
	add.n	a15, a15, a11	# ivtmp$250, ivtmp$250, _1054
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	bne	a4, a8, .L84	#, i,
	l32i	a15, sp, 64	# %sfp, N
	j	.L75		#
.L72:
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	l16si	a2, a3, 0	# MEM[base: _1072, offset: 0B], _274
# @OPUS@\upstream\celt\vq.c:199:    } while (++j<N);
	addi.n	a4, a4, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	extui	a9, a2, 31, 1	# tmp528, _274,
# @OPUS@\upstream\celt\vq.c:194:       signx[j] = X[j]<0;
	s32i.n	a9, a5, 0	# MEM[base: _1070, offset: 0B], tmp528
# @OPUS@\upstream\celt\vq.c:196:       X[j] = ABS16(X[j]);
	abs	a2, a2	# tmp529, _274
# @OPUS@\upstream\celt\vq.c:196:       X[j] = ABS16(X[j]);
	s16i	a2, a3, 0	# MEM[base: _1072, offset: 0B], tmp529
# @OPUS@\upstream\celt\vq.c:197:       iy[j] = 0;
	s32i.n	a8, a6, 0	# MEM[base: _1069, offset: 0B], tmp530
# @OPUS@\upstream\celt\vq.c:198:       y[j] = 0;
	s16i	a8, a7, 0	# MEM[base: _1068, offset: 0B], tmp530
	addi.n	a3, a3, 2	# ivtmp$224, ivtmp$224,
	addi.n	a5, a5, 4	# ivtmp$225, ivtmp$225,
	addi.n	a6, a6, 4	# ivtmp$226, ivtmp$226,
	addi.n	a7, a7, 2	# ivtmp$227, ivtmp$227,
# @OPUS@\upstream\celt\vq.c:199:    } while (++j<N);
	blt	a4, a15, .L72	# j, N,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	l32i.n	a5, sp, 48	# %sfp,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	srai	a2, a15, 1	# tmp532, N,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	bge	a2, a5, .L119	# tmp532,,
# @OPUS@\upstream\celt\vq.c:192:    sum = 0;
	movi.n	a13, 0	# sum,
# @OPUS@\upstream\celt\vq.c:206:    if (K > (N>>1))
	l32i.n	a3, sp, 24	# %sfp, ivtmp$221
# @OPUS@\upstream\celt\vq.c:209:       j=0; do {
	mov.n	a2, a13	# j, sum
.L86:
# @OPUS@\upstream\celt\vq.c:210:          sum += X[j];
	l16si	a4, a3, 0	# MEM[base: _1085, offset: 0B], tmp533
# @OPUS@\upstream\celt\vq.c:211:       }  while (++j<N);
	addi.n	a2, a2, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:210:          sum += X[j];
	add.n	a13, a13, a4	# sum, sum, tmp533
	addi.n	a3, a3, 2	# ivtmp$221, ivtmp$221,
# @OPUS@\upstream\celt\vq.c:211:       }  while (++j<N);
	blt	a2, a15, .L86	# j, N,
# @OPUS@\upstream\celt\vq.c:215:       if (sum <= K)
	l32i.n	a6, sp, 48	# %sfp,
	blt	a6, a13, .L87	#, sum,
# @OPUS@\upstream\celt\vq.c:222:          X[0] = QCONST16(1.f,14);
	l32r	a13, .LC6	#, sum
	l32i.n	a2, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:224:             X[j]=0;
	movi.n	a4, 2	# tmp542,
# @OPUS@\upstream\celt\vq.c:222:          X[0] = QCONST16(1.f,14);
	s16i	a13, a2, 0	# *X_11(D), sum
# @OPUS@\upstream\celt\vq.c:224:             X[j]=0;
	blt	a15, a4, .L89	# N,,
	slli	a4, a15, 1	# tmp543, N,
	addi	a4, a4, -2	# tmp542, tmp543,
.L89:
	l32i.n	a5, sp, 24	# %sfp,
	movi.n	a3, 0	#,
	addi.n	a2, a5, 2	#,,
	call0	memset		#
.L87:
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	l32i.n	a6, sp, 48	# %sfp,
	mov.n	a2, a13	#, sum
	slli	a12, a6, 16	# tmp549,,
	call0	celt_rcp		#
	srai	a12, a12, 16	# _301, tmp549,
	srai	a2, a2, 16	# tmp550,,
	mul16s	a3, a2, a12	# tmp551, tmp550, _301
	mov.n	a2, a13	#, sum
	slli	a3, a3, 16	# tmp552, tmp551,
	srai	a3, a3, 16	# _306, tmp552,
	s32i	a3, sp, 80	#,
	call0	celt_rcp		#
	extui	a10, a2, 0, 16	# tmp553,
	mull	a10, a10, a12	# tmp554, tmp553, _301
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	l32i	a3, sp, 80	#,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	srai	a10, a10, 16	# tmp555, tmp554,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	add.n	a10, a3, a10	# tmp557, _306, tmp555
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	movi.n	a13, 0	# yy,
# @OPUS@\upstream\celt\vq.c:229:       rcp = EXTRACT16(MULT16_32_Q16(K, celt_rcp(sum)));
	slli	a10, a10, 16	# tmp558, tmp557,
	l32i.n	a8, sp, 28	# %sfp, ivtmp$216
	l32i.n	a5, sp, 24	# %sfp, ivtmp$215
	l32i.n	a9, sp, 48	# %sfp, pulsesLeft
	srai	a10, a10, 16	# rcp, tmp558,
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	mov.n	a12, a13	# xy, yy
# @OPUS@\upstream\celt\vq.c:234:       j=0; do {
	mov.n	a7, a13	# j, yy
.L90:
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	l16ui	a3, a5, 0	# MEM[base: _1093, offset: 0B],
# @OPUS@\upstream\celt\vq.c:246:       }  while (++j<N);
	addi.n	a7, a7, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	mul16s	a3, a3, a10	# tmp559, MEM[base: _1093, offset: 0B], rcp
	srai	a3, a3, 15	# _324, tmp559,
# @OPUS@\upstream\celt\vq.c:241:          y[j] = (celt_norm)iy[j];
	slli	a2, a3, 16	# tmp561, _324,
	srai	a2, a2, 16	# _326, tmp561,
# @OPUS@\upstream\celt\vq.c:237:          iy[j] = MULT16_16_Q15(X[j],rcp);
	s32i.n	a3, a8, 0	# MEM[base: _1091, offset: 0B], _324
# @OPUS@\upstream\celt\vq.c:241:          y[j] = (celt_norm)iy[j];
	s16i	a2, a14, 0	# MEM[base: _1090, offset: 0B], _326
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	l16ui	a6, a5, 0	# MEM[base: _1093, offset: 0B],
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	mull	a4, a2, a2	# tmp562, _326, _326
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	mul16s	a6, a6, a2	# tmp566, MEM[base: _1093, offset: 0B], _326
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	add.n	a4, a13, a4	# tmp564, yy, tmp562
# @OPUS@\upstream\celt\vq.c:244:          y[j] *= 2;
	slli	a2, a2, 1	# tmp568, _326,
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	slli	a4, a4, 16	# tmp565, tmp564,
# @OPUS@\upstream\celt\vq.c:244:          y[j] *= 2;
	s16i	a2, a14, 0	# MEM[base: _1090, offset: 0B], tmp568
# @OPUS@\upstream\celt\vq.c:242:          yy = MAC16_16(yy, y[j],y[j]);
	srai	a13, a4, 16	# yy, tmp565,
# @OPUS@\upstream\celt\vq.c:243:          xy = MAC16_16(xy, X[j],y[j]);
	add.n	a12, a12, a6	# xy, xy, tmp566
# @OPUS@\upstream\celt\vq.c:245:          pulsesLeft -= iy[j];
	sub	a9, a9, a3	# pulsesLeft, pulsesLeft, _324
	addi.n	a5, a5, 2	# ivtmp$215, ivtmp$215,
	addi.n	a8, a8, 4	# ivtmp$216, ivtmp$216,
	addi.n	a14, a14, 2	# ivtmp$217, ivtmp$217,
# @OPUS@\upstream\celt\vq.c:246:       }  while (++j<N);
	blt	a7, a15, .L90	# j, N,
	j	.L85		#
.L119:
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	movi.n	a13, 0	# yy,
	mov.n	a9, a5	# pulsesLeft,
# @OPUS@\upstream\celt\vq.c:201:    xy = yy = 0;
	mov.n	a12, a13	# xy, yy
.L85:
# @OPUS@\upstream\celt\vq.c:255:    if (pulsesLeft > N+3)
	l32i.n	a2, sp, 32	# %sfp,
	blt	a2, a9, .L91	#, pulsesLeft,
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	bgei	a9, 1, .L92	# pulsesLeft,,
	j	.L93		#
.L91:
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	l32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	l32i.n	a6, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	l16ui	a2, a5, 0	# *y_268,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	l32i.n	a3, a6, 0	# *iy_10, *iy_10
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	add.n	a2, a9, a2	# tmp571, pulsesLeft, *y_268
	mul16s	a2, a9, a2	# tmp572, pulsesLeft, tmp571
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	add.n	a9, a3, a9	# tmp576, *iy_10, pulsesLeft
# @OPUS@\upstream\celt\vq.c:259:       yy = MAC16_16(yy, tmp, y[0]);
	add.n	a13, a13, a2	# tmp574, yy, tmp572
	slli	a13, a13, 16	# tmp575, tmp574,
	srai	a13, a13, 16	# yy, tmp575,
# @OPUS@\upstream\celt\vq.c:260:       iy[0] += pulsesLeft;
	s32i.n	a9, a6, 0	# *iy_10, tmp576
	j	.L93		#
.L92:
	l32i.n	a3, sp, 48	# %sfp,
	l32i.n	a4, sp, 24	# %sfp,
	addi.n	a2, a3, 1	# tmp578,,
	l32i.n	a5, sp, 20	# %sfp,
	sub	a2, a2, a9	#, tmp578, pulsesLeft
	add.n	a9, a9, a2	#, pulsesLeft,
	addi.n	a4, a4, 2	#,,
	addi.n	a5, a5, 2	#,,
	s32i.n	a2, sp, 16	# %sfp,
	s32i.n	a9, sp, 32	# %sfp,
	s32i.n	a4, sp, 36	# %sfp,
	s32i.n	a5, sp, 40	# %sfp,
.L96:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	l32i.n	a6, sp, 16	# %sfp,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a2, 0x1f	#,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a8, a6	# _1268,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	l32i.n	a3, sp, 24	# %sfp,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	sub	a8, a2, a8	# tmp581,, _1268
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	slli	a8, a8, 16	# tmp583, tmp581,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	l16si	a7, a3, 0	# *X_11(D), tmp586
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	l32i.n	a5, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	srai	a8, a8, 16	# tmp582, tmp583,
# @OPUS@\upstream\celt\vq.c:274:       rshift = 1+celt_ilog2(K-pulsesLeft+i+1);
	addi.n	a8, a8, 1	# rshift, tmp582,
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	addi.n	a13, a13, 1	# tmp584, yy,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	add.n	a7, a7, a12	# tmp589, tmp586, xy
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	l16ui	a9, a5, 0	# *y_268,
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	slli	a13, a13, 16	# tmp585, tmp584,
# @OPUS@\upstream\celt\vq.c:285:       Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[0])),rshift));
	ssr	a8	# rshift
	sra	a7, a7	# tmp590, tmp589
# @OPUS@\upstream\celt\vq.c:279:       yy = ADD16(yy, 1);
	srai	a13, a13, 16	# yy, tmp585,
# @OPUS@\upstream\celt\vq.c:291:       Rxy = MULT16_16_Q15(Rxy,Rxy);
	mul16s	a7, a7, a7	# tmp595, tmp590, tmp590
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	add.n	a9, a13, a9	# tmp593, yy, *y_268
	slli	a9, a9, 16	# tmp594, tmp593,
# @OPUS@\upstream\celt\vq.c:293:       best_num = Rxy;
	slli	a7, a7, 1	# tmp596, tmp595,
	l32i.n	a6, sp, 36	# %sfp, ivtmp$204
	l32i.n	a5, sp, 40	# %sfp, ivtmp$206
# @OPUS@\upstream\celt\vq.c:287:       Ryy = ADD16(yy, y[0]);
	srai	a9, a9, 16	# best_den, tmp594,
# @OPUS@\upstream\celt\vq.c:293:       best_num = Rxy;
	srai	a7, a7, 16	# best_num, tmp596,
# @OPUS@\upstream\celt\vq.c:276:       best_id = 0;
	movi.n	a14, 0	# best_id,
# @OPUS@\upstream\celt\vq.c:294:       j=1;
	movi.n	a4, 1	# j,
.L95:
# @OPUS@\upstream\celt\vq.c:297:          Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[j])),rshift));
	l16si	a2, a6, 0	# MEM[base: _414, offset: 0B], tmp597
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	l16ui	a3, a5, 0	# MEM[base: _415, offset: 0B],
# @OPUS@\upstream\celt\vq.c:297:          Rxy = EXTRACT16(SHR32(ADD32(xy, EXTEND32(X[j])),rshift));
	add.n	a2, a2, a12	# tmp600, tmp597, xy
	ssr	a8	# rshift
	sra	a2, a2	# tmp601, tmp600
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	mul16s	a2, a2, a2	# tmp606, tmp601, tmp601
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	add.n	a3, a13, a3	# tmp604, yy, MEM[base: _415, offset: 0B]
	slli	a3, a3, 16	# tmp605, tmp604,
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	slli	a2, a2, 1	# tmp607, tmp606,
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	srai	a3, a3, 16	# Ryy, tmp605,
# @OPUS@\upstream\celt\vq.c:303:          Rxy = MULT16_16_Q15(Rxy,Rxy);
	srai	a2, a2, 16	# Rxy, tmp607,
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	mull	a11, a3, a7	# tmp608, Ryy, best_num
	mull	a10, a2, a9	# tmp609, Rxy, best_den
	addi.n	a6, a6, 2	# ivtmp$204, ivtmp$204,
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	bge	a11, a10, .L94	# tmp608, tmp609,
	mov.n	a14, a4	# best_id, j
# @OPUS@\upstream\celt\vq.c:299:          Ryy = ADD16(yy, y[j]);
	mov.n	a9, a3	# best_den, Ryy
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	mov.n	a7, a2	# best_num, Rxy
.L94:
# @OPUS@\upstream\celt\vq.c:316:       } while (++j<N);
	addi.n	a4, a4, 1	# j, j,
	addi.n	a5, a5, 2	# ivtmp$206, ivtmp$206,
	blt	a4, a15, .L95	# j, N,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	l32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	slli	a3, a14, 1	# _1203, best_id,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	add.n	a4, a6, a3	# _1198,, _1203
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	l32i.n	a5, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	l32i.n	a6, sp, 24	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	l16si	a2, a4, 0	# *_1198, _1197
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	slli	a14, a14, 2	# tmp619, best_id,
	add.n	a14, a5, a14	# _1183,, tmp619
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	add.n	a3, a6, a3	# tmp610,, _1203
	l16si	a3, a3, 0	# *_1202, tmp611
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	l32i.n	a5, a14, 0	# *_1183, *_1183
# @OPUS@\upstream\celt\vq.c:325:       y[best_id] += 2;
	addi.n	a6, a2, 2	# tmp618, _1197,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	add.n	a13, a2, a13	# tmp616, _1197, yy
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:325:       y[best_id] += 2;
	s16i	a6, a4, 0	# *_1198, tmp618
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	addi.n	a5, a5, 1	# tmp620, *_1183,
	addi.n	a2, a2, 1	#,,
# @OPUS@\upstream\celt\vq.c:319:       xy = ADD32(xy, EXTEND32(X[best_id]));
	add.n	a12, a12, a3	# xy, xy, tmp611
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	l32i.n	a3, sp, 32	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	slli	a13, a13, 16	# tmp617, tmp616,
# @OPUS@\upstream\celt\vq.c:326:       iy[best_id]++;
	s32i.n	a5, a14, 0	# *_1183, tmp620
	s32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:321:       yy = ADD16(yy, y[best_id]);
	srai	a13, a13, 16	# yy, tmp617,
# @OPUS@\upstream\celt\vq.c:264:    for (i=0;i<pulsesLeft;i++)
	bne	a3, a2, .L96	#,,
.L93:
# @OPUS@\upstream\celt\vq.c:310:          if (opus_unlikely(MULT16_16(best_den, Rxy) > MULT16_16(Ryy, best_num)))
	l32i.n	a3, sp, 28	# %sfp, ivtmp$198
# @OPUS@\upstream\celt\vq.c:330:    j=0;
	l32i.n	a5, sp, 52	# %sfp, ivtmp$199
	movi.n	a4, 0	# j,
.L97:
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	l32i.n	a6, a5, 0	# MEM[base: _405, offset: 0B], _428
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	l32i.n	a7, a3, 0	# MEM[base: _438, offset: 0B], MEM[base: _438, offset: 0B]
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	neg	a2, a6	# tmp622, _428
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	xor	a2, a2, a7	# tmp623, tmp622, MEM[base: _438, offset: 0B]
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	add.n	a2, a2, a6	# tmp625, tmp623, _428
# @OPUS@\upstream\celt\vq.c:335:       iy[j] = (iy[j]^-signx[j]) + signx[j];
	s32i.n	a2, a3, 0	# MEM[base: _438, offset: 0B], tmp625
# @OPUS@\upstream\celt\vq.c:336:    } while (++j<N);
	addi.n	a4, a4, 1	# j, j,
	addi.n	a3, a3, 4	# ivtmp$198, ivtmp$198,
	addi.n	a5, a5, 4	# ivtmp$199, ivtmp$199,
	blt	a4, a15, .L97	# j, N,
# @OPUS@\upstream\celt\vq.c:337:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\vq.c:359:    encode_pulses(iy, N, K, enc);
	l32i.n	a4, sp, 48	# %sfp,
	l32i	a5, sp, 68	# %sfp,
	l32i.n	a2, sp, 28	# %sfp,
	mov.n	a3, a15	#, N
	call0	encode_pulses		#
# @OPUS@\upstream\celt\vq.c:361:    if (resynth)
	l32i	a4, sp, 132	# resynth,
	bnez.n	a4, .L98	#,
.L104:
# @OPUS@\upstream\celt\vq.c:159:    if (B<=1)
	l32i.n	a5, sp, 44	# %sfp,
# @OPUS@\upstream\celt\vq.c:160:       return 1;
	movi.n	a12, 1	# <retval>,
# @OPUS@\upstream\celt\vq.c:159:    if (B<=1)
	bgei	a5, 2, .L142	#,,
	j	.L99		#
.L98:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a2, a13	# _442, yy
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a5, 0x1f	# tmp626,
	sub	a5, a5, a2	# tmp628, tmp626, _442
# @OPUS@\upstream\celt\vq.c:143:    k = celt_ilog2(Ryy)>>1;
	slli	a5, a5, 16	# tmp630, tmp628,
# @OPUS@\upstream\celt\vq.c:143:    k = celt_ilog2(Ryy)>>1;
	srai	a12, a5, 17	# k, tmp630,
# @OPUS@\upstream\celt\vq.c:145:    t = VSHR32(Ryy, 2*(k-7));
	addi	a2, a12, -7	# tmp633, k,
	slli	a2, a2, 1	# _448, tmp633,
	blti	a2, 1, .L101	# _448,,
	ssr	a2	# _448
	sra	a2, a13	# iftmp$44_449, yy
	j	.L102		#
.L101:
	movi.n	a2, 7	# tmp634,
	sub	a2, a2, a12	# tmp635, tmp634, k
	slli	a2, a2, 1	# tmp636, tmp635,
	ssl	a2	# tmp636
	sll	a2, a13	# iftmp$44_449, yy
.L102:
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	call0	celt_rsqrt_norm		#
	l32i	a3, sp, 72	# %sfp,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	addi.n	a5, a12, 1	# _471, k,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	mull	a6, a3, a2	# tmp638,,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	movi.n	a7, 1	# tmp642,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	addmi	a6, a6, 0x4000	# tmp639, tmp638,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	slli	a6, a6, 1	# tmp641, tmp639,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	ssl	a5	# _471
	sll	a7, a7	# tmp643, tmp642
	l32i.n	a4, sp, 24	# %sfp, ivtmp$195
	l32i.n	a8, sp, 28	# %sfp, ivtmp$194
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	srai	a6, a6, 16	# g, tmp641,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	srai	a7, a7, 1	# _473, tmp643,
# @OPUS@\upstream\celt\vq.c:148:    i=0;
	movi.n	a3, 0	# i,
.L103:
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	l32i.n	a2, a8, 0	# MEM[base: _391, offset: 0B], MEM[base: _391, offset: 0B]
# @OPUS@\upstream\celt\vq.c:151:    while (++i < N);
	addi.n	a3, a3, 1	# i, i,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	mul16s	a2, a2, a6	# tmp645, MEM[base: _391, offset: 0B], g
	addi.n	a8, a8, 4	# ivtmp$194, ivtmp$194,
	add.n	a2, a2, a7	# tmp646, tmp645, _473
	ssr	a5	# _471
	sra	a2, a2	# tmp647, tmp646
	s16i	a2, a4, 0	# MEM[base: _392, offset: 0B], tmp647
	addi.n	a4, a4, 2	# ivtmp$195, ivtmp$195,
# @OPUS@\upstream\celt\vq.c:151:    while (++i < N);
	blt	a3, a15, .L103	# i, N,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	l32i.n	a4, sp, 56	# %sfp,
	bnez.n	a4, .L104	#,
# @OPUS@\upstream\celt\vq.c:96:    factor = SPREAD_FACTOR[spread-1];
	l32i.n	a5, sp, 60	# %sfp,
	l32r	a3, .LC7	#, tmp652
	addi.n	a2, a5, -1	# tmp653,,
	slli	a2, a2, 2	# tmp654, tmp653,
	add.n	a2, a3, a2	# tmp655, tmp652, tmp654
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	l32i.n	a6, sp, 48	# %sfp,
	l32i.n	a12, a2, 0	# SPREAD_FACTOR, tmp657
	slli	a3, a15, 16	# tmp648, N,
	mull	a12, a6, a12	# tmp656,, tmp657
	srai	a3, a3, 16	# _482, tmp648,
	slli	a4, a3, 15	# tmp650, _482,
	add.n	a12, a12, a15	# _489, tmp656, N
	sub	a3, a4, a3	# tmp651, tmp650, _482
	mov.n	a2, a12	#, _489
	s32i	a3, sp, 80	#,
	call0	celt_rcp		#
	mov.n	a13, a2	# _490,
	mov.n	a2, a12	#, _489
	call0	celt_rcp		#
	mov.n	a14, a2	# _498,
	mov.n	a2, a12	#, _489
	call0	celt_rcp		#
	l32i	a3, sp, 80	#,
	srai	a12, a2, 16	# tmp658,,
	srai	a4, a3, 16	# _485, tmp651,
	extui	a2, a3, 0, 16	# tmp664, tmp651
	extui	a14, a14, 0, 16	# tmp667, _498,
	mull	a14, a14, a4	# tmp668, tmp667, _485
	mull	a12, a12, a2	# tmp665, tmp658, tmp664
	srai	a2, a13, 16	# tmp673, _490,
	mull	a2, a2, a4	# tmp674, tmp673, _485
	srai	a3, a14, 15	# tmp669, tmp668,
	srai	a12, a12, 15	# tmp666, tmp665,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a12, a12, a3	# tmp672, tmp666, tmp669
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	slli	a2, a2, 1	# tmp675, tmp674,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a12, a12, a2	# tmp678, tmp672, tmp675
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	mul16s	a12, a12, a12	# tmp680, tmp678, tmp678
# @OPUS@\upstream\celt\vq.c:91:    int stride2=0;
	l32i.n	a9, sp, 56	# %sfp, stride2
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	srai	a12, a12, 16	# _517, tmp680,
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	mov.n	a2, a12	#, _517
	s32i	a9, sp, 92	#,
	call0	celt_cos_norm		#
	mov.n	a13, a2	# c,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	l32r	a2, .LC8	#, tmp683
	sub	a2, a2, a12	#, tmp683, _517
	call0	celt_cos_norm		#
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	mov.n	a14, a2	# s,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	slli	a2, a3, 3	# tmp685,,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i	a9, sp, 92	#,
	blt	a15, a2, .L105	# N, tmp685,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	srai	a5, a3, 2	# _528,,
# @OPUS@\upstream\celt\vq.c:106:       stride2 = 1;
	movi.n	a9, 1	# stride2,
	mov.n	a6, a3	# B, ivtmp$191
	j	.L106		#
.L122:
# @OPUS@\upstream\celt\vq.c:110:          stride2++;
	mov.n	a9, a4	# stride2, _525
.L106:
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	addi.n	a4, a9, 1	# _525, stride2,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	mull	a2, a3, a4	# tmp686, ivtmp$191, _525
	add.n	a3, a3, a6	# ivtmp$191, ivtmp$191, B
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	add.n	a2, a2, a5	# _529, tmp686, _528
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	blt	a2, a15, .L122	# _529, N,
.L105:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a3, sp, 44	# %sfp,
	mov.n	a2, a15	#, N
	s32i	a9, sp, 92	#,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a4, sp, 44	# %sfp,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i	a9, sp, 92	#,
	blti	a4, 1, .L123	#,,
	mov.n	a3, a2	#,
	mov.n	a4, a2	#,
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	slli	a2, a2, 1	# tmp690,,
	addi	a2, a2, -6	#, tmp690,
	s32i.n	a2, sp, 20	# %sfp,
	l32i.n	a6, sp, 24	# %sfp,
	neg	a2, a14	# tmp693, s
	l32i.n	a5, sp, 20	# %sfp,
	slli	a2, a2, 16	# tmp694, tmp693,
	addi.n	a10, a5, 6	# _369,,
	addi	a12, a6, -2	# tmp695,,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	addi.n	a3, a3, -1	#,,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi	a4, a4, -3	#,,
	srai	a11, a2, 16	# _1146, tmp694,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i	a8, sp, 76	# %sfp, ivtmp$184
	s32i.n	a9, sp, 16	# %sfp, stride2
	s32i.n	a15, sp, 32	# %sfp, N
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	s32i.n	a3, sp, 24	# %sfp,
	add.n	a12, a12, a10	# ivtmp$185, tmp695, _369
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	movi.n	a7, 0	# i,
	mov.n	a9, a4	# i,
	mov.n	a15, a11	# _1146, _1146
.L113:
# @OPUS@\upstream\celt\vq.c:119:          if (stride2)
	l32i.n	a5, sp, 16	# %sfp,
	beqz.n	a5, .L107	#,
# @OPUS@\upstream\celt\vq.c:120:             exp_rotation1(X+i*len, len, stride2, s, c);
	l32i.n	a3, sp, 28	# %sfp,
	mov.n	a4, a5	#,
	mov.n	a2, a8	#, ivtmp$184
	mov.n	a6, a13	#, c
	mov.n	a5, a14	#, s
	s32i	a7, sp, 88	#,
	s32i	a8, sp, 84	#,
	s32i	a9, sp, 92	#,
	s32i	a10, sp, 80	#,
	call0	exp_rotation1		#
	l32i	a10, sp, 80	#,
	l32i	a9, sp, 92	#,
	l32i	a8, sp, 84	#,
	l32i	a7, sp, 88	#,
.L107:
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	l32i.n	a6, sp, 24	# %sfp,
	bgei	a6, 1, .L108	#,,
.L112:
	l32i.n	a2, sp, 20	# %sfp,
	add.n	a4, a8, a2	# Xptr, ivtmp$184,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a9, .L109	# i,
	j	.L110		#
.L108:
	l16si	a2, a8, 0	# MEM[base: _1150, offset: 0B], Xptr__lsm0$158
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	mov.n	a4, a8	# ivtmp$175, ivtmp$184
.L111:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a5, a4, 2	# MEM[base: _364, offset: 2B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a2, a14	# tmp700, Xptr__lsm0$158, s
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a2, a13	# tmp706, Xptr__lsm0$158, c
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a6, a5, a13	# tmp702, x2, c
	addmi	a2, a11, 0x4000	# tmp701, tmp700,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a15	# tmp708, x2, _1146
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a2, a2, a6	# tmp703, tmp701, tmp702
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp707, tmp706,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	slli	a2, a2, 1	# tmp705, tmp703,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a5	# tmp709, tmp707, tmp708
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a2, a2, 16	# _583, tmp705,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp710, tmp709,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a2, a4, 2	# MEM[base: _364, offset: 2B], _583
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a3, a4, 0	# MEM[base: _364, offset: 0B], tmp710
	addi.n	a4, a4, 2	# ivtmp$175, ivtmp$175,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a4, a12, .L111	# ivtmp$175, ivtmp$185,
	j	.L112		#
.L110:
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a3, sp, 44	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	addi.n	a7, a7, 1	# i, i,
	add.n	a8, a8, a10	# ivtmp$184, ivtmp$184, _369
	add.n	a12, a12, a10	# ivtmp$185, ivtmp$185, _369
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	bne	a3, a7, .L113	#, i,
	l32i.n	a15, sp, 32	# %sfp, N
	j	.L104		#
.L109:
	addi	a2, a12, -2	# tmp711, ivtmp$185,
	l16si	a2, a2, 0	# MEM[base: _379, offset: 0B], Xptr__lsm0$157
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	mov.n	a6, a9	# i, i
.L114:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a5, a4, 0	# MEM[base: Xptr_595, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a3, a2, a13	# tmp716, Xptr__lsm0$157, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a2, a2, a15	# tmp721, Xptr__lsm0$157, _1146
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a5, a14	# tmp718, x1, s
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a13	# tmp723, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a3, a3, 0x4000	# tmp717, tmp716,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a2, a2, 0x4000	# tmp722, tmp721,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a3, a3, a11	# tmp719, tmp717, tmp718
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a2, a2, a5	# tmp724, tmp722, tmp723
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a3, a3, 15	# tmp720, tmp719,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	slli	a2, a2, 1	# tmp726, tmp724,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a3, a4, 2	# MEM[base: Xptr_595, offset: 2B], tmp720
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a2, a2, 16	# Xptr__lsm0$157, tmp726,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a4, a4, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a2, a4, 2	# MEM[base: Xptr_624, offset: 2B], Xptr__lsm0$157
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a6, a6, -1	# i, i,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a6, -1, .L114	# i,,
	j	.L110		#
.L142:
	mov.n	a3, a5	#,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a2, a15	#, N
	mov.n	a13, a5	# B,
	call0	__udivsi3		#
# @OPUS@\upstream\celt\vq.c:165:    i=0; do {
	movi.n	a7, 0	# i,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	l32i	a11, sp, 64	# %sfp, ivtmp$164
	slli	a10, a2, 2	# _145, tmp729,
# @OPUS@\upstream\celt\vq.c:164:    collapse_mask = 0;
	mov.n	a12, a7	# <retval>, i
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	movi.n	a9, 1	# tmp733,
	mov.n	a8, a7	# tmp734, i
.L116:
# @OPUS@\upstream\celt\vq.c:167:       unsigned tmp=0;
	movi.n	a5, 0	# tmp,
# @OPUS@\upstream\celt\vq.c:164:    collapse_mask = 0;
	mov.n	a4, a11	# ivtmp$161, ivtmp$164
# @OPUS@\upstream\celt\vq.c:168:       j=0; do {
	mov.n	a3, a5	# j, tmp
.L115:
# @OPUS@\upstream\celt\vq.c:169:          tmp |= iy[i*N0+j];
	l32i.n	a6, a4, 0	# MEM[base: _1208, offset: 0B], MEM[base: _1208, offset: 0B]
# @OPUS@\upstream\celt\vq.c:170:       } while (++j<N0);
	addi.n	a3, a3, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:169:          tmp |= iy[i*N0+j];
	or	a5, a5, a6	# tmp, tmp, MEM[base: _1208, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$161, ivtmp$161,
# @OPUS@\upstream\celt\vq.c:170:       } while (++j<N0);
	blt	a3, a2, .L115	# j, tmp729,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	mov.n	a4, a8	#, tmp734
	movnez	a4, a9, a5	#, tmp733, tmp
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	ssl	a7	# i
	sll	a5, a4	# tmp735, tmp732
# @OPUS@\upstream\celt\vq.c:172:    } while (++i<B);
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	or	a12, a12, a5	# <retval>, <retval>, tmp735
	add.n	a11, a11, a10	# ivtmp$164, ivtmp$164, _145
# @OPUS@\upstream\celt\vq.c:172:    } while (++i<B);
	bne	a13, a7, .L116	# B, i,
	j	.L99		#
.L123:
# @OPUS@\upstream\celt\vq.c:160:       return 1;
	movi.n	a12, 1	# <retval>,
.L99:
# @OPUS@\upstream\celt\vq.c:368:    RESTORE_STACK;
	l32i.n	a2, sp, 8	# _saved_stack,
	l32i.n	a3, sp, 12	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\vq.c:370: }
	l32i	a0, sp, 124	#,
	movi	a9, 0x80	#,
	mov.n	a2, a12	#, <retval>
	l32i	a13, sp, 116	#,
	l32i	a12, sp, 120	#,
	l32i	a14, sp, 112	#,
	l32i	a15, sp, 108	#,
	add.n	sp, sp, a9	#,,
	ret.n
	.size	alg_quant, .-alg_quant
	.section	.text.alg_unquant,"ax",@progbits
	.literal_position
	.literal .LC11, SPREAD_FACTOR$3797
	.literal .LC12, 32767
	.align	4
	.global	alg_unquant
	.type	alg_unquant, @function
# Function: alg_unquant
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: /** Decode pulse vector and combine the result with the pitch vector to produce
# C context: the final normalised signal in the current band. */
# C context: unsigned alg_unquant(celt_norm *X, int N, int K, int spread, int B,
# C context: ec_dec *dec, opus_val16 gain)
# C context: {
# C context: opus_val32 Ryy;
# C context: unsigned collapse_mask;
alg_unquant:
	addi	sp, sp, -112	#,,
	mov.n	a9, a6	# B, B
	l16si	a6, sp, 112	# gain,
# @OPUS@\upstream\celt\vq.c:380:    SAVE_STACK;
	s32i	a9, sp, 68	#,
# @OPUS@\upstream\celt\vq.c:376: {
	s32i.n	a6, sp, 20	# %sfp,
	s32i	a0, sp, 108	#,
	s32i.n	a5, sp, 24	# %sfp, spread
	s32i	a12, sp, 104	#,
	s32i	a13, sp, 100	#,
	s32i	a14, sp, 96	#,
	s32i	a15, sp, 92	#,
# @OPUS@\upstream\celt\vq.c:376: {
	mov.n	a14, a4	# K, K
	mov.n	a15, a7	# dec, dec
	s32i.n	a3, sp, 16	# %sfp, N
	mov.n	a12, a2	# X, X
# @OPUS@\upstream\celt\vq.c:380:    SAVE_STACK;
	call0	yoradio_opus_scratch_mark		#
	s32i.n	a2, sp, 0	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:384:    ALLOC(iy, N, int);
	l32i.n	a2, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:380:    SAVE_STACK;
	s32i.n	a3, sp, 4	# _saved_stack,
# @OPUS@\upstream\celt\vq.c:384:    ALLOC(iy, N, int);
	movi.n	a4, 1	#,
	movi.n	a3, 4	#,
	call0	yoradio_opus_scratch_alloc		#
# @OPUS@\upstream\celt\vq.c:385:    Ryy = decode_pulses(iy, N, K, dec);
	l32i.n	a3, sp, 16	# %sfp,
	mov.n	a5, a15	#, dec
	mov.n	a4, a14	#, K
# @OPUS@\upstream\celt\vq.c:384:    ALLOC(iy, N, int);
	mov.n	a13, a2	# iy,
# @OPUS@\upstream\celt\vq.c:385:    Ryy = decode_pulses(iy, N, K, dec);
	call0	decode_pulses		#
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a2	# _48, Ryy
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a6, 0x1f	# tmp201,
	sub	a6, a6, a3	# tmp203, tmp201, _48
# @OPUS@\upstream\celt\vq.c:143:    k = celt_ilog2(Ryy)>>1;
	slli	a6, a6, 16	# tmp205, tmp203,
# @OPUS@\upstream\celt\vq.c:143:    k = celt_ilog2(Ryy)>>1;
	srai	a15, a6, 17	# k, tmp205,
# @OPUS@\upstream\celt\vq.c:145:    t = VSHR32(Ryy, 2*(k-7));
	addi	a3, a15, -7	# tmp208, k,
	slli	a3, a3, 1	# _54, tmp208,
	l32i	a9, sp, 68	#,
	blti	a3, 1, .L144	# _54,,
	ssr	a3	# _54
	sra	a2, a2	# iftmp$44_55, Ryy
	j	.L145		#
.L144:
	movi.n	a3, 7	# tmp209,
	sub	a3, a3, a15	# tmp210, tmp209, k
	slli	a3, a3, 1	# tmp211, tmp210,
	ssl	a3	# tmp211
	sll	a2, a2	# iftmp$44_55, Ryy
.L145:
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	s32i	a9, sp, 68	#,
	call0	celt_rsqrt_norm		#
	l32i.n	a6, sp, 20	# %sfp,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	movi.n	a11, 1	# tmp217,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	mull	a10, a6, a2	# tmp213,,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	addi.n	a6, a15, 1	# _77, k,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	addmi	a10, a10, 0x4000	# tmp214, tmp213,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	slli	a10, a10, 1	# tmp216, tmp214,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	ssl	a6	# _77
	sll	a11, a11	# tmp218, tmp217
# @OPUS@\upstream\celt\vq.c:148:    i=0;
	l32i.n	a8, sp, 16	# %sfp, N
	l32i	a9, sp, 68	#,
# @OPUS@\upstream\celt\vq.c:146:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	srai	a10, a10, 16	# g, tmp216,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	srai	a11, a11, 1	# _79, tmp218,
	mov.n	a7, a12	# ivtmp$284, X
	mov.n	a5, a12	# ivtmp$295, X
	mov.n	a4, a13	# ivtmp$294, ivtmp$264
# @OPUS@\upstream\celt\vq.c:148:    i=0;
	movi.n	a3, 0	# i,
.L146:
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	l32i.n	a2, a4, 0	# MEM[base: _329, offset: 0B], MEM[base: _329, offset: 0B]
# @OPUS@\upstream\celt\vq.c:151:    while (++i < N);
	addi.n	a3, a3, 1	# i, i,
# @OPUS@\upstream\celt\vq.c:150:       X[i] = EXTRACT16(PSHR32(MULT16_16(g, iy[i]), k+1));
	mul16s	a2, a2, a10	# tmp220, MEM[base: _329, offset: 0B], g
	addi.n	a4, a4, 4	# ivtmp$294, ivtmp$294,
	add.n	a2, a2, a11	# tmp221, tmp220, _79
	ssr	a6	# _77
	sra	a2, a2	# tmp222, tmp221
	s16i	a2, a5, 0	# MEM[base: _328, offset: 0B], tmp222
	addi.n	a5, a5, 2	# ivtmp$295, ivtmp$295,
# @OPUS@\upstream\celt\vq.c:151:    while (++i < N);
	blt	a3, a8, .L146	# i, N,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	l32i.n	a3, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	slli	a2, a14, 1	# tmp223, K,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	bge	a2, a3, .L161	# tmp223,,
# @OPUS@\upstream\celt\vq.c:94:    if (2*K>=len || spread==SPREAD_NONE)
	l32i.n	a6, sp, 24	# %sfp,
	movi.n	a3, 1	# tmp229,
	movi.n	a4, 0	# tmp226,
	moveqz	a4, a3, a6	# tmp228, tmp229,
	extui	a4, a4, 0, 8	# tmp231, tmp228
	beqz.n	a4, .L147	# tmp231,
.L161:
# @OPUS@\upstream\celt\vq.c:160:       return 1;
	movi.n	a12, 1	# <retval>,
# @OPUS@\upstream\celt\vq.c:159:    if (B<=1)
	bgei	a9, 2, .L179	# B,,
	j	.L150		#
.L147:
# @OPUS@\upstream\celt\vq.c:96:    factor = SPREAD_FACTOR[spread-1];
	l32r	a5, .LC11	#, tmp236
	addi.n	a2, a6, -1	# tmp237,,
	slli	a2, a2, 2	# tmp238, tmp237,
	add.n	a2, a5, a2	# tmp239, tmp236, tmp238
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	l32i.n	a6, sp, 16	# %sfp,
	l32i.n	a2, a2, 0	# SPREAD_FACTOR, tmp241
	slli	a5, a6, 16	# tmp232,,
	mull	a14, a14, a2	# tmp240, K, tmp241
	srai	a5, a5, 16	# _88, tmp232,
	add.n	a14, a14, a6	# _95, tmp240,
	slli	a11, a5, 15	# tmp234, _88,
	sub	a11, a11, a5	# tmp235, tmp234, _88
	mov.n	a2, a14	#, _95
	s32i.n	a3, sp, 60	#,
	s32i	a7, sp, 64	#,
	s32i	a9, sp, 68	#,
	s32i.n	a4, sp, 52	#,
	s32i.n	a11, sp, 56	#,
	call0	celt_rcp		#
	mov.n	a5, a2	# _96,
	mov.n	a2, a14	#, _95
	s32i.n	a5, sp, 48	#,
	call0	celt_rcp		#
	mov.n	a6, a2	# _104,
	mov.n	a2, a14	#, _95
	s32i.n	a6, sp, 44	#,
	call0	celt_rcp		#
	l32i.n	a11, sp, 56	#,
	l32i.n	a6, sp, 44	#,
	l32i.n	a5, sp, 48	#,
	srai	a10, a11, 16	# _91, tmp235,
	srai	a15, a2, 16	# tmp242,,
	extui	a11, a11, 0, 16	# tmp248, tmp235
	extui	a6, a6, 0, 16	# tmp251, _104,
	mull	a15, a15, a11	# tmp249, tmp242, tmp248
	mull	a6, a6, a10	# tmp252, tmp251, _91
	srai	a2, a5, 16	# tmp257, _96,
	mull	a2, a2, a10	# tmp258, tmp257, _91
	srai	a5, a6, 15	# tmp253, tmp252,
	srai	a15, a15, 15	# tmp250, tmp249,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a15, a15, a5	# tmp256, tmp250, tmp253
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	slli	a2, a2, 1	# tmp259, tmp258,
# @OPUS@\upstream\celt\vq.c:98:    gain = celt_div((opus_val32)MULT16_16(Q15_ONE,len),(opus_val32)(len+factor*K));
	add.n	a15, a15, a2	# tmp262, tmp256, tmp259
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	mul16s	a15, a15, a15	# tmp264, tmp262, tmp262
# @OPUS@\upstream\celt\vq.c:91:    int stride2=0;
	l32i.n	a4, sp, 52	#,
# @OPUS@\upstream\celt\vq.c:99:    theta = HALF16(MULT16_16_Q15(gain,gain));
	srai	a15, a15, 16	# _123, tmp264,
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	mov.n	a2, a15	#, _123
# @OPUS@\upstream\celt\vq.c:91:    int stride2=0;
	s32i.n	a4, sp, 20	# %sfp, tmp231
# @OPUS@\upstream\celt\vq.c:101:    c = celt_cos_norm(EXTEND32(theta));
	call0	celt_cos_norm		#
	mov.n	a14, a2	# c,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	l32r	a2, .LC12	#, tmp267
	sub	a2, a2, a15	#, tmp267, _123
	call0	celt_cos_norm		#
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i	a9, sp, 68	#,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a4, sp, 16	# %sfp,
# @OPUS@\upstream\celt\vq.c:102:    s = celt_cos_norm(EXTEND32(SUB16(Q15ONE,theta))); /*  sin(theta) */
	mov.n	a15, a2	# s,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	slli	a2, a9, 3	# tmp269, B,
# @OPUS@\upstream\celt\vq.c:104:    if (len>=8*stride)
	l32i.n	a3, sp, 60	#,
	l32i	a7, sp, 64	#,
	blt	a4, a2, .L152	#, tmp269,
	mov.n	a8, a4	# N,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	srai	a5, a9, 2	# _134, B,
	mov.n	a4, a9	# ivtmp$291, B
# @OPUS@\upstream\celt\vq.c:106:       stride2 = 1;
	s32i.n	a3, sp, 20	# %sfp, tmp229
	mov.n	a6, a3	# stride2,
	j	.L153		#
.L167:
# @OPUS@\upstream\celt\vq.c:110:          stride2++;
	mov.n	a6, a3	# stride2, stride2
.L153:
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	addi.n	a3, a6, 1	# stride2, stride2,
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	mull	a2, a4, a3	# tmp270, ivtmp$291, stride2
	add.n	a4, a4, a9	# ivtmp$291, ivtmp$291, B
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	add.n	a2, a2, a5	# _135, tmp270, _134
# @OPUS@\upstream\celt\vq.c:109:       while ((stride2*stride2+stride2)*stride + (stride>>2) < len)
	blt	a2, a8, .L167	# _135, N,
	s32i.n	a6, sp, 20	# %sfp, stride2
.L152:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a2, sp, 16	# %sfp,
	mov.n	a3, a9	#, B
	s32i	a7, sp, 64	#,
	s32i	a9, sp, 68	#,
# ASM block division: a2=unsigned N, a3=unsigned B; result a2.
# a4/a5 are call-clobbered; no extra stack, loads or interrupt masking.
# Normal B=1,2,4,8 (TF may change it). Non-powers/zero retain libgcc.
	beqz	a3, .Lasm_block_alg_unquant_0_fallback
	addi	a4, a3, -1
	and	a4, a4, a3
	bnez	a4, .Lasm_block_alg_unquant_0_fallback
	nsau	a4, a3
	movi	a5, 31
	sub	a4, a5, a4
	ssr	a4
	srl	a2, a2
	j	.Lasm_block_alg_unquant_0_done
.Lasm_block_alg_unquant_0_fallback:
	call0	__udivsi3		#
.Lasm_block_alg_unquant_0_done:
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i	a9, sp, 68	#,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i.n	a2, sp, 36	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i	a7, sp, 64	#,
	blti	a9, 1, .L168	# B,,
	mov.n	a6, a2	#,
	mov.n	a3, a2	#,
# @OPUS@\upstream\celt\vq.c:73:    Xptr = &X[len-2*stride-1];
	slli	a2, a2, 1	# tmp274,,
	addi	a2, a2, -6	#, tmp274,
	s32i.n	a2, sp, 24	# %sfp,
	l32i.n	a5, sp, 24	# %sfp,
	addi	a10, a12, -2	# tmp279, X,
	addi.n	a11, a5, 6	# _368,,
	neg	a2, a15	# tmp277, s
	add.n	a10, a10, a11	# ivtmp$285, tmp279, _368
	slli	a2, a2, 16	# tmp278, tmp277,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	addi.n	a6, a6, -1	#,,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi	a3, a3, -3	#,,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	s32i.n	a13, sp, 40	# %sfp, ivtmp$264
	s32i.n	a9, sp, 28	# %sfp, B
	mov.n	a13, a10	# ivtmp$285, ivtmp$285
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	s32i.n	a6, sp, 32	# %sfp,
	srai	a12, a2, 16	# _385, tmp278,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	movi.n	a8, 0	# i,
	mov.n	a10, a3	# i,
	mov.n	a9, a11	# _368, _368
.L160:
# @OPUS@\upstream\celt\vq.c:119:          if (stride2)
	l32i.n	a4, sp, 20	# %sfp,
	beqz.n	a4, .L154	#,
# @OPUS@\upstream\celt\vq.c:120:             exp_rotation1(X+i*len, len, stride2, s, c);
	l32i.n	a3, sp, 36	# %sfp,
	mov.n	a2, a7	#, ivtmp$284
	mov.n	a6, a14	#, c
	mov.n	a5, a15	#, s
	s32i	a7, sp, 64	#,
	s32i.n	a8, sp, 44	#,
	s32i	a9, sp, 68	#,
	s32i.n	a10, sp, 48	#,
	call0	exp_rotation1		#
	l32i.n	a10, sp, 48	#,
	l32i	a9, sp, 68	#,
	l32i.n	a8, sp, 44	#,
	l32i	a7, sp, 64	#,
.L154:
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	l32i.n	a5, sp, 32	# %sfp,
	bgei	a5, 1, .L155	#,,
.L159:
	l32i.n	a6, sp, 24	# %sfp,
	add.n	a4, a6, a7	# Xptr,, ivtmp$284
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bgez	a10, .L156	# i,
	j	.L157		#
.L155:
	l16si	a2, a7, 0	# MEM[base: _389, offset: 0B], Xptr__lsm0$258
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	mov.n	a4, a7	# ivtmp$275, ivtmp$284
.L158:
# @OPUS@\upstream\celt\vq.c:69:       x2 = Xptr[stride];
	l16si	a5, a4, 2	# MEM[base: _372, offset: 2B], x2
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a2, a15	# tmp284, Xptr__lsm0$258, s
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a3, a2, a14	# tmp290, Xptr__lsm0$258, c
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a6, a5, a14	# tmp286, x2, c
	addmi	a2, a11, 0x4000	# tmp285, tmp284,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a12	# tmp292, x2, _385
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a2, a2, a6	# tmp287, tmp285, tmp286
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a3, a3, 0x4000	# tmp291, tmp290,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	slli	a2, a2, 1	# tmp289, tmp287,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a3, a3, a5	# tmp293, tmp291, tmp292
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a2, a2, 16	# _189, tmp289,
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a3, a3, 15	# tmp294, tmp293,
# @OPUS@\upstream\celt\vq.c:70:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a2, a4, 2	# MEM[base: _372, offset: 2B], _189
# @OPUS@\upstream\celt\vq.c:71:       *Xptr++      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a3, a4, 0	# MEM[base: _372, offset: 0B], tmp294
	addi.n	a4, a4, 2	# ivtmp$275, ivtmp$275,
# @OPUS@\upstream\celt\vq.c:65:    for (i=0;i<len-stride;i++)
	bne	a13, a4, .L158	# ivtmp$285, ivtmp$275,
	j	.L159		#
.L157:
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	l32i.n	a2, sp, 28	# %sfp,
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	addi.n	a8, a8, 1	# i, i,
	add.n	a7, a7, a9	# ivtmp$284, ivtmp$284, _368
	add.n	a13, a13, a9	# ivtmp$285, ivtmp$285, _368
# @OPUS@\upstream\celt\vq.c:115:    for (i=0;i<stride;i++)
	bne	a2, a8, .L160	#, i,
	l32i.n	a13, sp, 40	# %sfp, ivtmp$264
	mov.n	a9, a2	# B,
	j	.L161		#
.L156:
	addi	a2, a13, -2	# tmp295, ivtmp$285,
	l16si	a2, a2, 0	# MEM[base: _341, offset: 0B], Xptr__lsm0$257
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	mov.n	a6, a10	# i, i
.L162:
# @OPUS@\upstream\celt\vq.c:77:       x1 = Xptr[0];
	l16si	a5, a4, 0	# MEM[base: Xptr_180, offset: 0B], x1
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a3, a2, a14	# tmp300, Xptr__lsm0$257, c
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a2, a2, a12	# tmp305, Xptr__lsm0$257, _385
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	mull	a11, a5, a15	# tmp302, x1, s
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	mull	a5, a5, a14	# tmp307, x1, c
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	addmi	a3, a3, 0x4000	# tmp301, tmp300,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addmi	a2, a2, 0x4000	# tmp306, tmp305,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	add.n	a3, a3, a11	# tmp303, tmp301, tmp302
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	add.n	a2, a2, a5	# tmp308, tmp306, tmp307
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	srai	a3, a3, 15	# tmp304, tmp303,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	slli	a2, a2, 1	# tmp310, tmp308,
# @OPUS@\upstream\celt\vq.c:79:       Xptr[stride] = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x2),  s, x1), 15));
	s16i	a3, a4, 2	# MEM[base: Xptr_180, offset: 2B], tmp304
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	srai	a2, a2, 16	# Xptr__lsm0$257, tmp310,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	addi	a4, a4, -2	# Xptr, Xptr,
# @OPUS@\upstream\celt\vq.c:80:       *Xptr--      = EXTRACT16(PSHR32(MAC16_16(MULT16_16(c, x1), ms, x2), 15));
	s16i	a2, a4, 2	# MEM[base: Xptr_230, offset: 2B], Xptr__lsm0$257
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	addi.n	a6, a6, -1	# i, i,
# @OPUS@\upstream\celt\vq.c:74:    for (i=len-2*stride-1;i>=0;i--)
	bnei	a6, -1, .L162	# i,,
	j	.L157		#
.L179:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a2, sp, 16	# %sfp,
	mov.n	a3, a9	#, B
	s32i	a9, sp, 68	#,
# ASM block division: a2=unsigned N, a3=unsigned B; result a2.
# a4/a5 are call-clobbered; no extra stack, loads or interrupt masking.
# Normal B=1,2,4,8 (TF may change it). Non-powers/zero retain libgcc.
	beqz	a3, .Lasm_block_alg_unquant_1_fallback
	addi	a4, a3, -1
	and	a4, a4, a3
	bnez	a4, .Lasm_block_alg_unquant_1_fallback
	nsau	a4, a3
	movi	a5, 31
	sub	a4, a5, a4
	ssr	a4
	srl	a2, a2
	j	.Lasm_block_alg_unquant_1_done
.Lasm_block_alg_unquant_1_fallback:
	call0	__udivsi3		#
.Lasm_block_alg_unquant_1_done:
# @OPUS@\upstream\celt\vq.c:165:    i=0; do {
	movi.n	a7, 0	# i,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	l32i	a9, sp, 68	#,
	slli	a11, a2, 2	# _401, tmp313,
# @OPUS@\upstream\celt\vq.c:164:    collapse_mask = 0;
	mov.n	a12, a7	# <retval>, i
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	movi.n	a10, 1	# tmp317,
	mov.n	a8, a7	# tmp318, i
.L164:
# @OPUS@\upstream\celt\vq.c:167:       unsigned tmp=0;
	movi.n	a5, 0	# tmp,
# @OPUS@\upstream\celt\vq.c:164:    collapse_mask = 0;
	mov.n	a4, a13	# ivtmp$261, ivtmp$264
# @OPUS@\upstream\celt\vq.c:168:       j=0; do {
	mov.n	a3, a5	# j, tmp
.L163:
# @OPUS@\upstream\celt\vq.c:169:          tmp |= iy[i*N0+j];
	l32i.n	a6, a4, 0	# MEM[base: _405, offset: 0B], MEM[base: _405, offset: 0B]
# @OPUS@\upstream\celt\vq.c:170:       } while (++j<N0);
	addi.n	a3, a3, 1	# j, j,
# @OPUS@\upstream\celt\vq.c:169:          tmp |= iy[i*N0+j];
	or	a5, a5, a6	# tmp, tmp, MEM[base: _405, offset: 0B]
	addi.n	a4, a4, 4	# ivtmp$261, ivtmp$261,
# @OPUS@\upstream\celt\vq.c:170:       } while (++j<N0);
	blt	a3, a2, .L163	# j, tmp313,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	mov.n	a3, a8	#, tmp318
	movnez	a3, a10, a5	#, tmp317, tmp
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	ssl	a7	# i
	sll	a5, a3	# tmp319, tmp316
# @OPUS@\upstream\celt\vq.c:172:    } while (++i<B);
	addi.n	a7, a7, 1	# i, i,
# @OPUS@\upstream\celt\vq.c:171:       collapse_mask |= (tmp!=0)<<i;
	or	a12, a12, a5	# <retval>, <retval>, tmp319
	add.n	a13, a13, a11	# ivtmp$264, ivtmp$264, _401
# @OPUS@\upstream\celt\vq.c:172:    } while (++i<B);
	bne	a9, a7, .L164	# B, i,
	j	.L150		#
.L168:
# @OPUS@\upstream\celt\vq.c:160:       return 1;
	movi.n	a12, 1	# <retval>,
.L150:
# @OPUS@\upstream\celt\vq.c:389:    RESTORE_STACK;
	l32i.n	a2, sp, 0	# _saved_stack,
	l32i.n	a3, sp, 4	# _saved_stack,
	call0	yoradio_opus_scratch_restore		#
# @OPUS@\upstream\celt\vq.c:391: }
	l32i	a0, sp, 108	#,
	mov.n	a2, a12	#, <retval>
	l32i	a13, sp, 100	#,
	l32i	a12, sp, 104	#,
	l32i	a14, sp, 96	#,
	l32i	a15, sp, 92	#,
	addi	sp, sp, 112	#,,
	ret.n
	.size	alg_unquant, .-alg_unquant
	.section	.text.renormalise_vector,"ax",@progbits
	.literal_position
	.literal .LC14, 16384
	.align	4
	.global	renormalise_vector
	.type	renormalise_vector, @function
# Function: renormalise_vector
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: #ifndef OVERRIDE_renormalise_vector
# C context: void renormalise_vector(celt_norm *X, int N, opus_val16 gain, int arch)
# C context: {
# C context: int i;
# C context: #ifdef FIXED_POINT
# C context: int k;
renormalise_vector:
	addi	sp, sp, -32	#,,
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	slli	a4, a4, 16	# tmp89, gain,
	s32i.n	a0, sp, 28	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\celt\vq.c:395: {
	mov.n	a12, a2	# X, X
	srai	a13, a4, 16	# gain, tmp89,
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	blti	a3, 1, .L181	# N,,
	slli	a14, a3, 1	# tmp126, N,
	mov.n	a6, a2	# ivtmp$303, X
	add.n	a3, a2, a14	# _102, X, tmp126
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	movi.n	a2, 0	# xy,
.L182:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16si	a5, a6, 0	# MEM[base: _106, offset: 0B], _48
	addi.n	a6, a6, 2	# ivtmp$303, ivtmp$303,
	mull	a5, a5, a5	# tmp94, _48, _48
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a2, a2, a5	# xy, xy, tmp94
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a3, a6, .L182	# _102, ivtmp$303,
# @OPUS@\upstream\celt\vq.c:404:    E = EPSILON + celt_inner_prod(X, X, N, arch);
	addi.n	a2, a2, 1	# E, xy,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a15, a2	# _30, E
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a5, 0x1f	# tmp95,
	sub	a5, a5, a15	# tmp97, tmp95, _30
# @OPUS@\upstream\celt\vq.c:406:    k = celt_ilog2(E)>>1;
	slli	a5, a5, 16	# tmp99, tmp97,
# @OPUS@\upstream\celt\vq.c:406:    k = celt_ilog2(E)>>1;
	srai	a15, a5, 17	# k, tmp99,
# @OPUS@\upstream\celt\vq.c:408:    t = VSHR32(E, 2*(k-7));
	addi	a3, a15, -7	# tmp102, k,
	slli	a3, a3, 1	# _3, tmp102,
	blti	a3, 1, .L183	# _3,,
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	ssr	a3	# _3
	sra	a2, a2	#, E
	j	.L189		#
.L183:
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	movi.n	a3, 7	# tmp109,
	sub	a3, a3, a15	# tmp110, tmp109, k
	slli	a3, a3, 1	# tmp111, tmp110,
	ssl	a3	# tmp111
	sll	a2, a2	#, E
.L189:
	call0	celt_rsqrt_norm		#
	mull	a4, a13, a2	# tmp114, gain,
# @OPUS@\upstream\celt\vq.c:414:       *xptr = EXTRACT16(PSHR32(MULT16_16(g, *xptr), k+1));
	addi.n	a5, a15, 1	# _17, k,
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	addmi	a4, a4, 0x4000	# tmp115, tmp114,
# @OPUS@\upstream\celt\vq.c:414:       *xptr = EXTRACT16(PSHR32(MULT16_16(g, *xptr), k+1));
	movi.n	a6, 1	# tmp118,
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	slli	a4, a4, 1	# tmp117, tmp115,
# @OPUS@\upstream\celt\vq.c:414:       *xptr = EXTRACT16(PSHR32(MULT16_16(g, *xptr), k+1));
	ssl	a5	# _17
	sll	a6, a6	# tmp119, tmp118
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	srai	a4, a4, 16	# g, tmp117,
# @OPUS@\upstream\celt\vq.c:414:       *xptr = EXTRACT16(PSHR32(MULT16_16(g, *xptr), k+1));
	srai	a6, a6, 1	# _19, tmp119,
	add.n	a14, a12, a14	# _114, X, tmp126
.L185:
# @OPUS@\upstream\celt\vq.c:414:       *xptr = EXTRACT16(PSHR32(MULT16_16(g, *xptr), k+1));
	l16ui	a2, a12, 0	# MEM[base: xptr_60, offset: 0B],
	mul16s	a2, a2, a4	# tmp121, MEM[base: xptr_60, offset: 0B], g
	add.n	a2, a2, a6	# tmp123, tmp121, _19
	ssr	a5	# _17
	sra	a2, a2	# tmp124, tmp123
	s16i	a2, a12, 0	# MEM[base: xptr_60, offset: 0B], tmp124
# @OPUS@\upstream\celt\vq.c:415:       xptr++;
	addi.n	a12, a12, 2	# X, X,
# @OPUS@\upstream\celt\vq.c:412:    for (i=0;i<N;i++)
	bne	a12, a14, .L185	# X, _114,
	j	.L180		#
.L181:
# @OPUS@\upstream\celt\vq.c:409:    g = MULT16_16_P15(celt_rsqrt_norm(t),gain);
	l32r	a2, .LC14	#,
	call0	celt_rsqrt_norm		#
.L180:
# @OPUS@\upstream\celt\vq.c:418: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	renormalise_vector, .-renormalise_vector
	.section	.text.stereo_itheta,"ax",@progbits
	.literal_position
	.literal .LC15, 32767
	.literal .LC16, 4936
	.literal .LC17, -11943
	.literal .LC18, 25736
	.literal .LC19, 20861
	.align	4
	.global	stereo_itheta
	.type	stereo_itheta, @function
# Function: stereo_itheta
# Module: upstream/celt/vq.c
# CELT pulse-vector normalization, rotations and collapse masks.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: #endif /* OVERRIDE_renormalise_vector */
# C context:
# C context: int stereo_itheta(const celt_norm *X, const celt_norm *Y, int stereo, int N, int arch)
# C context: {
# C context: int i;
# C context: int itheta;
# C context: opus_val16 mid, side;
stereo_itheta:
	addi	sp, sp, -32	#,,
	s32i.n	a0, sp, 28	#,
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\celt\vq.c:429:    if (stereo)
	bnez.n	a4, .L191	# stereo,
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bgei	a5, 1, .L192	# N,,
	j	.L203		#
.L191:
# @OPUS@\upstream\celt\vq.c:431:       for (i=0;i<N;i++)
	blti	a5, 1, .L203	# N,,
	slli	a5, a5, 1	# tmp177, N,
# @OPUS@\upstream\celt\vq.c:428:    Emid = Eside = EPSILON;
	movi.n	a12, 1	# Eside,
	mov.n	a6, a2	# ivtmp$306, X
	add.n	a8, a2, a5	# _222, ivtmp$306, tmp177
# @OPUS@\upstream\celt\vq.c:428:    Emid = Eside = EPSILON;
	mov.n	a2, a12	# Emid, Eside
.L195:
# @OPUS@\upstream\celt\vq.c:434:          m = ADD16(SHR16(X[i],1),SHR16(Y[i],1));
	l16ui	a5, a6, 0	# MEM[base: _227, offset: 0B],
	l16ui	a7, a3, 0	# MEM[base: _226, offset: 0B],
	slli	a5, a5, 16	# tmp180, MEM[base: _227, offset: 0B],
	slli	a7, a7, 16	# tmp185, MEM[base: _226, offset: 0B],
	srai	a5, a5, 17	# _5, tmp180,
	srai	a7, a7, 17	# _8, tmp185,
# @OPUS@\upstream\celt\vq.c:434:          m = ADD16(SHR16(X[i],1),SHR16(Y[i],1));
	add.n	a4, a5, a7	# m, _5, _8
# @OPUS@\upstream\celt\vq.c:435:          s = SUB16(SHR16(X[i],1),SHR16(Y[i],1));
	sub	a5, a5, a7	# s, _5, _8
# @OPUS@\upstream\celt\vq.c:436:          Emid = MAC16_16(Emid, m, m);
	mull	a4, a4, a4	# tmp192, m, m
# @OPUS@\upstream\celt\vq.c:437:          Eside = MAC16_16(Eside, s, s);
	mull	a5, a5, a5	# tmp193, s, s
	addi.n	a6, a6, 2	# ivtmp$306, ivtmp$306,
# @OPUS@\upstream\celt\vq.c:436:          Emid = MAC16_16(Emid, m, m);
	add.n	a2, a2, a4	# Emid, Emid, tmp192
# @OPUS@\upstream\celt\vq.c:437:          Eside = MAC16_16(Eside, s, s);
	add.n	a12, a12, a5	# Eside, Eside, tmp193
	addi.n	a3, a3, 2	# ivtmp$307, ivtmp$307,
# @OPUS@\upstream\celt\vq.c:431:       for (i=0;i<N;i++)
	bne	a8, a6, .L195	# _222, ivtmp$306,
	j	.L194		#
.L192:
	slli	a5, a5, 1	# _203, N,
	add.n	a8, a2, a5	# _201, ivtmp$314, _203
# @OPUS@\upstream\celt\pitch.h:163:    opus_val32 xy=0;
	mov.n	a7, a4	# xy, stereo
.L196:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16si	a6, a2, 0	# MEM[base: _205, offset: 0B], _57
	addi.n	a2, a2, 2	# ivtmp$314, ivtmp$314,
	mull	a6, a6, a6	# tmp196, _57, _57
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a7, a7, a6	# xy, xy, tmp196
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a8, a2, .L196	# _201, ivtmp$314,
	j	.L207		#
.L198:
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	l16si	a5, a3, 0	# MEM[base: _213, offset: 0B], _47
	addi.n	a3, a3, 2	# ivtmp$311, ivtmp$311,
	mull	a5, a5, a5	# tmp199, _47, _47
# @OPUS@\upstream\celt\pitch.h:165:       xy = MAC16_16(xy, x[i], y[i]);
	add.n	a4, a4, a5	# stereo, stereo, tmp199
# @OPUS@\upstream\celt\pitch.h:164:    for (i=0;i<N;i++)
	bne	a6, a3, .L198	# _209, ivtmp$311,
	addi.n	a12, a4, 1	# Eside, stereo,
	j	.L194		#
.L203:
# @OPUS@\upstream\celt\vq.c:428:    Emid = Eside = EPSILON;
	movi.n	a12, 1	# Eside,
# @OPUS@\upstream\celt\vq.c:428:    Emid = Eside = EPSILON;
	mov.n	a2, a12	# Emid, Eside
.L194:
# @OPUS@\upstream\celt\vq.c:443:    mid = celt_sqrt(Emid);
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\vq.c:443:    mid = celt_sqrt(Emid);
	slli	a3, a2, 16	# tmp200,,
# @OPUS@\upstream\celt\vq.c:444:    side = celt_sqrt(Eside);
	mov.n	a2, a12	#, Eside
# @OPUS@\upstream\celt\vq.c:443:    mid = celt_sqrt(Emid);
	srai	a12, a3, 16	# mid, tmp200,
# @OPUS@\upstream\celt\vq.c:444:    side = celt_sqrt(Eside);
	call0	celt_sqrt		#
# @OPUS@\upstream\celt\vq.c:444:    side = celt_sqrt(Eside);
	slli	a2, a2, 16	# tmp201,,
	srai	a13, a2, 16	# side, tmp201,
# @OPUS@\upstream\celt\mathops.h:289:    if (y < x)
	bge	a13, a12, .L199	# side, mid,
# @OPUS@\upstream\celt\mathops.h:292:       arg = celt_div(SHL32(EXTEND32(y),15),x);
	mov.n	a2, a12	#, mid
	call0	celt_rcp		#
	mov.n	a14, a2	# _74,
	mov.n	a2, a12	#, mid
	call0	celt_rcp		#
	mov.n	a15, a2	# _82,
	mov.n	a2, a12	#, mid
	call0	celt_rcp		#
	slli	a13, a13, 15	# _68, side,
	srai	a4, a13, 16	# _70, _68,
	srai	a2, a2, 16	# tmp202,,
	extui	a13, a13, 0, 16	# tmp203, _68,
	extui	a15, a15, 0, 16	# tmp206, _82,
	mull	a15, a15, a4	# tmp207, tmp206, _70
	mull	a13, a2, a13	# tmp204, tmp202, tmp203
	srai	a3, a14, 16	# tmp210, _74,
	mull	a3, a3, a4	# tmp211, tmp210, _70
	srai	a2, a13, 15	# tmp205, tmp204,
	srai	a15, a15, 15	# tmp208, tmp207,
# @OPUS@\upstream\celt\mathops.h:292:       arg = celt_div(SHL32(EXTEND32(y),15),x);
	add.n	a2, a2, a15	# tmp209, tmp205, tmp208
# @OPUS@\upstream\celt\mathops.h:292:       arg = celt_div(SHL32(EXTEND32(y),15),x);
	slli	a3, a3, 1	# tmp212, tmp211,
# @OPUS@\upstream\celt\mathops.h:295:       return SHR16(celt_atan01(EXTRACT16(arg)),1);
	l32r	a4, .LC15	#, tmp294
# @OPUS@\upstream\celt\mathops.h:292:       arg = celt_div(SHL32(EXTEND32(y),15),x);
	add.n	a2, a2, a3	# arg, tmp209, tmp212
# @OPUS@\upstream\celt\mathops.h:295:       return SHR16(celt_atan01(EXTRACT16(arg)),1);
	bge	a4, a2, .L200	# tmp294, arg,
	mov.n	a2, a4	# arg, tmp294
.L200:
	slli	a3, a2, 16	# tmp219, arg,
# @OPUS@\upstream\celt\mathops.h:278:    return MULT16_16_P15(x, ADD32(M1, MULT16_16_P15(x, ADD32(M2, MULT16_16_P15(x, ADD32(M3, MULT16_16_P15(M4, x)))))));
	l32r	a2, .LC16	#, tmp221
# @OPUS@\upstream\celt\mathops.h:295:       return SHR16(celt_atan01(EXTRACT16(arg)),1);
	srai	a3, a3, 16	# _97, tmp219,
# @OPUS@\upstream\celt\mathops.h:278:    return MULT16_16_P15(x, ADD32(M1, MULT16_16_P15(x, ADD32(M2, MULT16_16_P15(x, ADD32(M3, MULT16_16_P15(M4, x)))))));
	mul16s	a2, a3, a2	# tmp220, _97, tmp221
	l32r	a5, .LC17	#, tmp226
	addmi	a2, a2, 0x4000	# tmp222, tmp220,
	srai	a2, a2, 15	# tmp223, tmp222,
	add.n	a2, a2, a5	# tmp225, tmp223, tmp226
	mul16s	a2, a2, a3	# tmp227, tmp225, _97
	addmi	a2, a2, 0x4000	# tmp228, tmp227,
	srai	a2, a2, 15	# tmp229, tmp228,
	addi	a2, a2, -21	# tmp231, tmp229,
	mul16s	a2, a2, a3	# tmp232, tmp231, _97
	addmi	a2, a2, 0x4000	# tmp233, tmp232,
	srai	a2, a2, 15	# tmp234, tmp233,
	add.n	a2, a2, a4	# tmp236, tmp234, tmp294
	mul16s	a2, a2, a3	# tmp238, tmp236, _97
	addmi	a2, a2, 0x4000	# tmp239, tmp238,
# @OPUS@\upstream\celt\mathops.h:295:       return SHR16(celt_atan01(EXTRACT16(arg)),1);
	slli	a2, a2, 1	# tmp242, tmp239,
	srai	a2, a2, 17	# _121, tmp242,
	j	.L201		#
.L199:
# @OPUS@\upstream\celt\mathops.h:298:       arg = celt_div(SHL32(EXTEND32(x),15),y);
	mov.n	a2, a13	#, side
	call0	celt_rcp		#
	mov.n	a14, a2	# _129,
	mov.n	a2, a13	#, side
	call0	celt_rcp		#
	mov.n	a15, a2	# _137,
	mov.n	a2, a13	#, side
	call0	celt_rcp		#
	slli	a12, a12, 15	# _123, mid,
	srai	a4, a12, 16	# _125, _123,
	srai	a2, a2, 16	# tmp245,,
	extui	a12, a12, 0, 16	# tmp246, _123,
	extui	a15, a15, 0, 16	# tmp249, _137,
	mull	a15, a15, a4	# tmp250, tmp249, _125
	mull	a2, a2, a12	# tmp247, tmp245, tmp246
	srai	a3, a14, 16	# tmp253, _129,
	mull	a3, a3, a4	# tmp254, tmp253, _125
	srai	a2, a2, 15	# tmp248, tmp247,
	srai	a15, a15, 15	# tmp251, tmp250,
# @OPUS@\upstream\celt\mathops.h:298:       arg = celt_div(SHL32(EXTEND32(x),15),y);
	add.n	a2, a2, a15	# tmp252, tmp248, tmp251
# @OPUS@\upstream\celt\mathops.h:298:       arg = celt_div(SHL32(EXTEND32(x),15),y);
	slli	a3, a3, 1	# tmp255, tmp254,
# @OPUS@\upstream\celt\mathops.h:301:       return 25736-SHR16(celt_atan01(EXTRACT16(arg)),1);
	l32r	a4, .LC15	#, tmp294
# @OPUS@\upstream\celt\mathops.h:298:       arg = celt_div(SHL32(EXTEND32(x),15),y);
	add.n	a2, a2, a3	# arg, tmp252, tmp255
# @OPUS@\upstream\celt\mathops.h:301:       return 25736-SHR16(celt_atan01(EXTRACT16(arg)),1);
	bge	a4, a2, .L202	# tmp294, arg,
	mov.n	a2, a4	# arg, tmp294
.L202:
	slli	a3, a2, 16	# tmp262, arg,
# @OPUS@\upstream\celt\mathops.h:278:    return MULT16_16_P15(x, ADD32(M1, MULT16_16_P15(x, ADD32(M2, MULT16_16_P15(x, ADD32(M3, MULT16_16_P15(M4, x)))))));
	l32r	a2, .LC16	#, tmp264
# @OPUS@\upstream\celt\mathops.h:301:       return 25736-SHR16(celt_atan01(EXTRACT16(arg)),1);
	srai	a3, a3, 16	# _152, tmp262,
# @OPUS@\upstream\celt\mathops.h:278:    return MULT16_16_P15(x, ADD32(M1, MULT16_16_P15(x, ADD32(M2, MULT16_16_P15(x, ADD32(M3, MULT16_16_P15(M4, x)))))));
	mul16s	a2, a3, a2	# tmp263, _152, tmp264
	l32r	a5, .LC17	#, tmp269
	addmi	a2, a2, 0x4000	# tmp265, tmp263,
	srai	a2, a2, 15	# tmp266, tmp265,
	add.n	a2, a2, a5	# tmp268, tmp266, tmp269
	mul16s	a2, a2, a3	# tmp270, tmp268, _152
	addmi	a2, a2, 0x4000	# tmp271, tmp270,
	srai	a2, a2, 15	# tmp272, tmp271,
	addi	a2, a2, -21	# tmp274, tmp272,
	mul16s	a2, a2, a3	# tmp275, tmp274, _152
	addmi	a2, a2, 0x4000	# tmp276, tmp275,
	srai	a2, a2, 15	# tmp277, tmp276,
	add.n	a2, a2, a4	# tmp279, tmp277, tmp294
	mul16s	a2, a2, a3	# tmp281, tmp279, _152
	addmi	a2, a2, 0x4000	# tmp282, tmp281,
# @OPUS@\upstream\celt\mathops.h:301:       return 25736-SHR16(celt_atan01(EXTRACT16(arg)),1);
	slli	a2, a2, 1	# tmp285, tmp282,
	srai	a3, a2, 17	# tmp286, tmp285,
	l32r	a2, .LC18	#, tmp289
	sub	a2, a2, a3	# tmp288, tmp289, tmp286
	slli	a2, a2, 16	# tmp290, tmp288,
	srai	a2, a2, 16	# _121, tmp290,
.L201:
# @OPUS@\upstream\celt\vq.c:447:    itheta = MULT16_16_Q15(QCONST16(0.63662f,15),celt_atan2p(side, mid));
	l32r	a3, .LC19	#, tmp293
# @OPUS@\upstream\celt\vq.c:453: }
	l32i.n	a0, sp, 28	#,
# @OPUS@\upstream\celt\vq.c:447:    itheta = MULT16_16_Q15(QCONST16(0.63662f,15),celt_atan2p(side, mid));
	mul16s	a2, a2, a3	# tmp292, _121, tmp293
# @OPUS@\upstream\celt\vq.c:453: }
	l32i.n	a12, sp, 24	#,
# @OPUS@\upstream\celt\vq.c:447:    itheta = MULT16_16_Q15(QCONST16(0.63662f,15),celt_atan2p(side, mid));
	srai	a2, a2, 15	# itheta, tmp292,
# @OPUS@\upstream\celt\vq.c:453: }
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
.L207:
# @OPUS@\upstream\celt\vq.c:440:       Emid += celt_inner_prod(X, X, N, arch);
	addi.n	a2, a7, 1	# Emid, xy,
	add.n	a6, a3, a5	# _209, ivtmp$311, _203
	j	.L198		#
	.size	stereo_itheta, .-stereo_itheta
	.section	.rodata.SPREAD_FACTOR$3797,"a"
	.align	4
	.type	SPREAD_FACTOR$3797, @object
	.size	SPREAD_FACTOR$3797, 12
SPREAD_FACTOR$3797:
	.word	15
	.word	10
	.word	5
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
