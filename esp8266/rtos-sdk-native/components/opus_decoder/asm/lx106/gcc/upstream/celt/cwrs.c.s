# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/cwrs.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"cwrs.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\cwrs.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\cwrs.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\cwrs.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\cwrs.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\cwrs.c.s.raw
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
	.section	.text.encode_pulses,"ax",@progbits
	.literal_position
	.literal .LC0, CELT_PVQ_U_ROW
	.align	4
	.global	encode_pulses
	.type	encode_pulses, @function
# Function: encode_pulses
# Module: upstream/celt/cwrs.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return i;
# C context: }
# C context:
# C context: void encode_pulses(const int *_y,int _n,int _k,ec_enc *_enc){
# C context: celt_assert(_k>0);
# C context: ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
# C context: }
# C context:
encode_pulses:
# @OPUS@\upstream\celt\cwrs.c:446:   i=_y[j]<0;
	addi.n	a6, a3, -1	# tmp96, _n,
	slli	a6, a6, 2	# tmp97, tmp96,
	add.n	a6, a2, a6	# tmp98, _y, tmp97
	l32i.n	a7, a6, 0	# *_31, _32
	addi	a8, a3, -2	# tmp100, _n,
# @OPUS@\upstream\celt\cwrs.c:458: void encode_pulses(const int *_y,int _n,int _k,ec_enc *_enc){
	addi	sp, sp, -16	#,,
	slli	a8, a8, 2	# _98, tmp100,
	l32r	a9, .LC0	#, tmp127
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\celt\cwrs.c:446:   i=_y[j]<0;
	extui	a12, a7, 31, 1	# i, _32,
# @OPUS@\upstream\celt\cwrs.c:458: void encode_pulses(const int *_y,int _n,int _k,ec_enc *_enc){
	s32i.n	a0, sp, 12	#,
	s32i.n	a14, sp, 0	#,
# @OPUS@\upstream\celt\cwrs.c:447:   k=abs(_y[j]);
	abs	a7, a7	# k, _32
	add.n	a10, a2, a8	# ivtmp$41, _y, _98
	movi.n	a13, 8	# ivtmp$39,
	movi.n	a6, 2	# ivtmp$37,
.L7:
# @OPUS@\upstream\celt\cwrs.c:450:     i+=CELT_PVQ_U(_n-j,k);
	mov.n	a2, a6	# _38, ivtmp$37
	bge	a7, a6, .L2	# k, ivtmp$37,
	mov.n	a2, a7	# _38, k
.L2:
	slli	a2, a2, 2	# tmp103, _38,
	add.n	a2, a9, a2	# tmp104, tmp127, tmp103
	l32i.n	a2, a2, 0	# CELT_PVQ_U_ROW, _41
	mov.n	a11, a13	# iftmp$7_45, ivtmp$39
	blt	a7, a6, .L3	# k, ivtmp$37,
	slli	a11, a7, 2	# iftmp$7_45, k,
.L3:
	add.n	a2, a2, a11	# tmp105, _41, iftmp$7_45
# @OPUS@\upstream\celt\cwrs.c:451:     k+=abs(_y[j]);
	l32i.n	a11, a10, 0	# MEM[base: _91, offset: 0B], _54
# @OPUS@\upstream\celt\cwrs.c:450:     i+=CELT_PVQ_U(_n-j,k);
	l32i.n	a14, a2, 0	# *_47, *_47
# @OPUS@\upstream\celt\cwrs.c:451:     k+=abs(_y[j]);
	abs	a2, a11	# tmp107, _54
# @OPUS@\upstream\celt\cwrs.c:450:     i+=CELT_PVQ_U(_n-j,k);
	add.n	a12, a12, a14	# i, i, *_47
# @OPUS@\upstream\celt\cwrs.c:451:     k+=abs(_y[j]);
	add.n	a7, a7, a2	# k, k, tmp107
# @OPUS@\upstream\celt\cwrs.c:452:     if(_y[j]<0)i+=CELT_PVQ_U(_n-j,k+1);
	bgez	a11, .L4	# _54,
# @OPUS@\upstream\celt\cwrs.c:452:     if(_y[j]<0)i+=CELT_PVQ_U(_n-j,k+1);
	addi.n	a2, a7, 1	# _57, k,
	mov.n	a11, a6	# _38, ivtmp$37
	bge	a2, a6, .L5	# _57, ivtmp$37,
	mov.n	a11, a2	# _38, _57
.L5:
	slli	a11, a11, 2	# tmp110, _38,
	add.n	a11, a9, a11	# tmp111, tmp127, tmp110
	l32i.n	a11, a11, 0	# CELT_PVQ_U_ROW, _59
	mov.n	a14, a13	# iftmp$11_63, ivtmp$39
	blt	a2, a6, .L6	# _57, ivtmp$37,
	slli	a14, a2, 2	# iftmp$11_63, _57,
.L6:
	add.n	a2, a11, a14	# tmp112, _59, iftmp$11_63
# @OPUS@\upstream\celt\cwrs.c:452:     if(_y[j]<0)i+=CELT_PVQ_U(_n-j,k+1);
	l32i.n	a2, a2, 0	# *_65, *_65
	add.n	a12, a12, a2	# i, i, *_65
.L4:
# @OPUS@\upstream\celt\cwrs.c:454:   while(j>0);
	sub	a2, a3, a6	# j, _n, ivtmp$37
	addi.n	a13, a13, 4	# ivtmp$39, ivtmp$39,
	addi.n	a6, a6, 1	# ivtmp$37, ivtmp$37,
	addi	a10, a10, -4	# ivtmp$41, ivtmp$41,
	bgei	a2, 1, .L7	# j,,
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	mov.n	a2, a3	# _n, _n
	bge	a4, a3, .L8	# _k, _n,
	mov.n	a2, a4	# _n, _k
.L8:
	slli	a2, a2, 2	# tmp117, _n,
	add.n	a2, a9, a2	# tmp118, tmp127, tmp117
	l32i.n	a2, a2, 0	# CELT_PVQ_U_ROW, _3
	slli	a6, a4, 2	# iftmp$0_16, _k,
	bge	a4, a3, .L10	# _k, _n,
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	addi.n	a6, a8, 8	# iftmp$0_16, _98,
.L10:
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	add.n	a2, a2, a6	# tmp119, _3, iftmp$0_16
	addi.n	a4, a4, 1	# _8, _k,
	l32i.n	a6, a2, 0	# *_6, _7
	mov.n	a2, a4	# _8, _8
	bge	a3, a4, .L11	# _n, _8,
	mov.n	a2, a3	# _8, _n
.L11:
	slli	a2, a2, 2	# tmp122, _8,
	add.n	a9, a9, a2	# tmp123, tmp127, tmp122
	l32i.n	a2, a9, 0	# CELT_PVQ_U_ROW, _10
	addi.n	a8, a8, 8	# iftmp$3_17, _98,
	blt	a4, a3, .L13	# _8, _n,
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	slli	a8, a4, 2	# iftmp$3_17, _8,
.L13:
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	add.n	a8, a2, a8	# tmp124, _10, iftmp$3_17
# @OPUS@\upstream\celt\cwrs.c:460:   ec_enc_uint(_enc,icwrs(_n,_y),CELT_PVQ_V(_n,_k));
	l32i.n	a4, a8, 0	# *_13, *_13
	mov.n	a3, a12	#, i
	add.n	a4, a6, a4	#, _7, *_13
	mov.n	a2, a5	#, _enc
	call0	ec_enc_uint		#
# @OPUS@\upstream\celt\cwrs.c:461: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	l32i.n	a14, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	encode_pulses, .-encode_pulses
	.section	.text.decode_pulses,"ax",@progbits
	.literal_position
	.literal .LC1, CELT_PVQ_U_ROW
	.align	4
	.global	decode_pulses
	.type	decode_pulses, @function
# Function: decode_pulses
# Module: upstream/celt/cwrs.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return yy;
# C context: }
# C context:
# C context: opus_val32 decode_pulses(int *_y,int _n,int _k,ec_dec *_dec){
# C context: return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
# C context: }
# C context:
# C context: #else /* SMALL_FOOTPRINT */
decode_pulses:
	addi	sp, sp, -48	#,,
	s32i.n	a12, sp, 40	#,
	s32i.n	a13, sp, 36	#,
	s32i.n	a14, sp, 32	#,
	mov.n	a13, a3	# _n, _n
	s32i.n	a2, sp, 4	# %sfp, _y
	s32i.n	a0, sp, 44	#,
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\celt\cwrs.c:539: opus_val32 decode_pulses(int *_y,int _n,int _k,ec_dec *_dec){
	mov.n	a12, a4	# _k, _k
	mov.n	a2, a5	# _dec, _dec
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	l32r	a14, .LC1	#, tmp450
	mov.n	a3, a4	# _k, _k
	bge	a13, a4, .L19	# _n, _k,
	mov.n	a3, a13	# _k, _n
.L19:
	slli	a3, a3, 2	# tmp252, _k,
	add.n	a3, a14, a3	# tmp253, tmp450, tmp252
	l32i.n	a3, a3, 0	# CELT_PVQ_U_ROW, _2
	slli	a4, a12, 2	# iftmp$12_16, _k,
	bge	a12, a13, .L21	# _k, _n,
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	slli	a4, a13, 2	# iftmp$12_16, _n,
.L21:
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	add.n	a3, a3, a4	# tmp254, _2, iftmp$12_16
	addi.n	a15, a12, 1	# tmp449, _k,
	l32i.n	a3, a3, 0	# *_5, _6
	mov.n	a4, a15	# _7, tmp449
	bge	a13, a15, .L22	# _n, tmp449,
	mov.n	a4, a13	# _7, _n
.L22:
	slli	a4, a4, 2	# tmp257, _7,
	add.n	a4, a14, a4	# tmp258, tmp450, tmp257
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, _9
	slli	a5, a13, 2	# iftmp$15_17, _n,
	blt	a15, a13, .L24	# tmp449, _n,
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	slli	a5, a15, 2	# iftmp$15_17, tmp449,
.L24:
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	add.n	a4, a4, a5	# tmp259, _9, iftmp$15_17
# @OPUS@\upstream\celt\cwrs.c:540:   return cwrsi(_n,_k,ec_dec_uint(_dec,CELT_PVQ_V(_n,_k)),_y);
	l32i.n	a4, a4, 0	# *_12, *_12
	add.n	a3, a3, a4	#, _6, *_12
	call0	ec_dec_uint		#
# @OPUS@\upstream\celt\cwrs.c:471:   while(_n>2){
	blti	a13, 3, .L25	# _n,,
	slli	a3, a13, 2	# tmp262, _n,
	l32i.n	a4, sp, 4	# %sfp,
	addi	a3, a3, -60	#, tmp262,
	s32i.n	a3, sp, 8	# %sfp,
# @OPUS@\upstream\celt\cwrs.c:468:   opus_val32  yy=0;
	movi.n	a10, 0	# yy,
	s32i.n	a4, sp, 0	# %sfp,
	add.n	a7, a14, a3	# ivtmp$73, tmp450,
	slli	a9, a12, 16	# tmp451, _k,
.L38:
	slli	a3, a13, 2	# _529, _n,
	srai	a5, a9, 16	# _714, tmp451,
# @OPUS@\upstream\celt\cwrs.c:474:     if(_k>=_n){
	blt	a12, a13, .L26	# _k, _n,
# @OPUS@\upstream\celt\cwrs.c:476:       row=CELT_PVQ_U_ROW[_n];
	l32i.n	a6, a7, 60	# MEM[base: _483, offset: 60B], row
# @OPUS@\upstream\celt\cwrs.c:478:       p=row[_k+1];
	slli	a15, a15, 2	# _35, tmp449,
# @OPUS@\upstream\celt\cwrs.c:478:       p=row[_k+1];
	add.n	a15, a6, a15	# tmp446, row, _35
	l32i.n	a8, a15, 0	# *_36, p
# @OPUS@\upstream\celt\cwrs.c:479:       s=-(_i>=p);
	movi.n	a4, 1	# tmp268,
	bgeu	a2, a8, .L27	# _i, p,
	movi.n	a4, 0	# tmp268,
.L27:
# @OPUS@\upstream\celt\cwrs.c:479:       s=-(_i>=p);
	neg	a4, a4	# s, tmp268
# @OPUS@\upstream\celt\cwrs.c:483:       q=row[_n];
	add.n	a11, a6, a3	# tmp271, row, _529
# @OPUS@\upstream\celt\cwrs.c:480:       _i-=p&s;
	and	a8, a4, a8	# tmp270, s, p
# @OPUS@\upstream\celt\cwrs.c:484:       if(q>_i){
	l32i.n	a11, a11, 0	# *_47, *_47
# @OPUS@\upstream\celt\cwrs.c:480:       _i-=p&s;
	sub	a2, a2, a8	# _i, _i, tmp270
# @OPUS@\upstream\celt\cwrs.c:484:       if(q>_i){
	bgeu	a2, a11, .L28	# _i, *_47,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a6, a7, 56	# MEM[base: _483, offset: 56B], MEM[base: _483, offset: 56B]
	addi.n	a12, a13, -1	# _k, _n,
	add.n	a6, a6, a3	# tmp274, MEM[base: _483, offset: 56B], _529
	l32i.n	a8, a6, 0	# *_695, p
	mov.n	a6, a12	# _n, _k
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 52	# MEM[base: _483, offset: 52B], MEM[base: _483, offset: 52B]
	addi	a12, a13, -2	# _k, _n,
	add.n	a8, a8, a3	# tmp276, MEM[base: _483, offset: 52B], _529
	l32i.n	a8, a8, 0	# *_688, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 48	# MEM[base: _483, offset: 48B], MEM[base: _483, offset: 48B]
	addi	a12, a13, -3	# _k, _n,
	add.n	a8, a8, a3	# tmp278, MEM[base: _483, offset: 48B], _529
	l32i.n	a8, a8, 0	# *_677, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 44	# MEM[base: _483, offset: 44B], MEM[base: _483, offset: 44B]
	addi	a12, a13, -4	# _k, _n,
	add.n	a8, a8, a3	# tmp280, MEM[base: _483, offset: 44B], _529
	l32i.n	a8, a8, 0	# *_672, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 40	# MEM[base: _483, offset: 40B], MEM[base: _483, offset: 40B]
	addi	a12, a13, -5	# _k, _n,
	add.n	a8, a8, a3	# tmp282, MEM[base: _483, offset: 40B], _529
	l32i.n	a8, a8, 0	# *_667, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 36	# MEM[base: _483, offset: 36B], MEM[base: _483, offset: 36B]
	addi	a12, a13, -6	# _k, _n,
	add.n	a8, a8, a3	# tmp284, MEM[base: _483, offset: 36B], _529
	l32i.n	a8, a8, 0	# *_662, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 32	# MEM[base: _483, offset: 32B], MEM[base: _483, offset: 32B]
	addi	a12, a13, -7	# _k, _n,
	add.n	a8, a8, a3	# tmp286, MEM[base: _483, offset: 32B], _529
	l32i.n	a8, a8, 0	# *_657, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 28	# MEM[base: _483, offset: 28B], MEM[base: _483, offset: 28B]
	addi	a12, a13, -8	# _k, _n,
	add.n	a8, a8, a3	# tmp288, MEM[base: _483, offset: 28B], _529
	l32i.n	a8, a8, 0	# *_652, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 24	# MEM[base: _483, offset: 24B], MEM[base: _483, offset: 24B]
	addi	a12, a13, -9	# _k, _n,
	add.n	a8, a8, a3	# tmp290, MEM[base: _483, offset: 24B], _529
	l32i.n	a8, a8, 0	# *_647, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 20	# MEM[base: _483, offset: 20B], MEM[base: _483, offset: 20B]
	addi	a12, a13, -10	# _k, _n,
	add.n	a8, a8, a3	# tmp292, MEM[base: _483, offset: 20B], _529
	l32i.n	a8, a8, 0	# *_642, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 16	# MEM[base: _483, offset: 16B], MEM[base: _483, offset: 16B]
	addi	a12, a13, -11	# _k, _n,
	add.n	a8, a8, a3	# tmp294, MEM[base: _483, offset: 16B], _529
	l32i.n	a8, a8, 0	# *_637, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 12	# MEM[base: _483, offset: 12B], MEM[base: _483, offset: 12B]
	addi	a12, a13, -12	# _k, _n,
	add.n	a8, a8, a3	# tmp296, MEM[base: _483, offset: 12B], _529
	l32i.n	a8, a8, 0	# *_632, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 8	# MEM[base: _483, offset: 8B], MEM[base: _483, offset: 8B]
	addi	a12, a13, -13	# _k, _n,
	add.n	a8, a8, a3	# tmp298, MEM[base: _483, offset: 8B], _529
	l32i.n	a8, a8, 0	# *_627, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 4	# MEM[base: _483, offset: 4B], MEM[base: _483, offset: 4B]
	addi	a12, a13, -14	# _k, _n,
	add.n	a8, a8, a3	# tmp300, MEM[base: _483, offset: 4B], _529
	l32i.n	a8, a8, 0	# *_622, p
# @OPUS@\upstream\celt\cwrs.c:488:         while(p>_i);
	bgeu	a2, a8, .L29	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:487:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a8, a7, 0	# MEM[base: _483, offset: 0B], MEM[base: _483, offset: 0B]
	addi	a12, a13, -15	# _k, _n,
	add.n	a3, a8, a3	# tmp302, MEM[base: _483, offset: 0B], _529
	l32i.n	a8, a3, 0	# *_52, p
	j	.L29		#
.L28:
# @OPUS@\upstream\celt\cwrs.c:490:       else for(p=row[_k];p>_i;p=row[_k])_k--;
	addi	a15, a15, -4	# tmp304, tmp446,
	l32i.n	a8, a15, 0	# *_55, p
# @OPUS@\upstream\celt\cwrs.c:490:       else for(p=row[_k];p>_i;p=row[_k])_k--;
	bgeu	a2, a8, .L42	# _i, p,
	addi.n	a3, a12, -1	# _k, _k,
	slli	a8, a3, 2	# tmp306, _k,
	add.n	a6, a6, a8	# ivtmp$48, row, tmp306
.L31:
	addi	a6, a6, -4	# ivtmp$48, ivtmp$48,
# @OPUS@\upstream\celt\cwrs.c:490:       else for(p=row[_k];p>_i;p=row[_k])_k--;
	l32i.n	a8, a6, 4	# MEM[base: _544, offset: 4B], p
# @OPUS@\upstream\celt\cwrs.c:490:       else for(p=row[_k];p>_i;p=row[_k])_k--;
	mov.n	a12, a3	# _k, _k
# @OPUS@\upstream\celt\cwrs.c:490:       else for(p=row[_k];p>_i;p=row[_k])_k--;
	bgeu	a2, a8, .L68	# _i, p,
	addi.n	a3, a3, -1	# _k, _k,
	j	.L31		#
.L68:
	slli	a9, a3, 16	# tmp451, _k,
	srai	a11, a9, 16	# _716, tmp451,
	addi.n	a6, a13, -1	# _n, _n,
	j	.L30		#
.L29:
	slli	a9, a12, 16	# tmp451, _k,
	srai	a11, a9, 16	# _716, tmp451,
	j	.L30		#
.L42:
	mov.n	a11, a5	# _716, _714
	addi.n	a6, a13, -1	# _n, _n,
.L30:
# @OPUS@\upstream\celt\cwrs.c:492:       val=(k0-_k+s)^s;
	slli	a4, a4, 16	# tmp309, s,
	srai	a4, a4, 16	# _70, tmp309,
	add.n	a3, a4, a5	# tmp310, _70, _714
	sub	a3, a3, a11	# tmp312, tmp310, _716
# @OPUS@\upstream\celt\cwrs.c:492:       val=(k0-_k+s)^s;
	xor	a3, a4, a3	# tmp314, _70, tmp312
	slli	a3, a3, 16	# tmp315, tmp314,
	srai	a3, a3, 16	# val, tmp315,
# @OPUS@\upstream\celt\cwrs.c:494:       yy=MAC16_16(yy,val,val);
	mull	a4, a3, a3	# tmp316, val, val
# @OPUS@\upstream\celt\cwrs.c:493:       *_y++=val;
	l32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\cwrs.c:491:       _i-=p;
	sub	a2, a2, a8	# _i, _i, p
# @OPUS@\upstream\celt\cwrs.c:493:       *_y++=val;
	s32i.n	a3, a5, 0	# MEM[base: _531, offset: 0B], val
# @OPUS@\upstream\celt\cwrs.c:494:       yy=MAC16_16(yy,val,val);
	add.n	a10, a10, a4	# yy, yy, tmp316
	j	.L32		#
.L26:
# @OPUS@\upstream\celt\cwrs.c:499:       p=CELT_PVQ_U_ROW[_k][_n];
	slli	a4, a12, 2	# tmp318, _k,
	add.n	a4, a14, a4	# tmp319, tmp450, tmp318
# @OPUS@\upstream\celt\cwrs.c:499:       p=CELT_PVQ_U_ROW[_k][_n];
	l32i.n	a6, a4, 0	# CELT_PVQ_U_ROW, tmp320
# @OPUS@\upstream\celt\cwrs.c:500:       q=CELT_PVQ_U_ROW[_k+1][_n];
	slli	a15, a15, 2	# tmp324, tmp449,
	add.n	a15, a14, a15	# tmp325, tmp450, tmp324
# @OPUS@\upstream\celt\cwrs.c:499:       p=CELT_PVQ_U_ROW[_k][_n];
	add.n	a6, a6, a3	# tmp321, tmp320, _529
# @OPUS@\upstream\celt\cwrs.c:500:       q=CELT_PVQ_U_ROW[_k+1][_n];
	l32i.n	a4, a15, 0	# CELT_PVQ_U_ROW, tmp326
# @OPUS@\upstream\celt\cwrs.c:499:       p=CELT_PVQ_U_ROW[_k][_n];
	l32i.n	a6, a6, 0	# *_82, p
# @OPUS@\upstream\celt\cwrs.c:500:       q=CELT_PVQ_U_ROW[_k+1][_n];
	add.n	a4, a4, a3	# tmp327, tmp326, _529
	l32i.n	a4, a4, 0	# *_86, q
# @OPUS@\upstream\celt\cwrs.c:501:       if(p<=_i&&_i<q){
	bltu	a2, a6, .L33	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:501:       if(p<=_i&&_i<q){
	bgeu	a2, a4, .L33	# _i, q,
# @OPUS@\upstream\celt\cwrs.c:503:         *_y++=0;
	l32i.n	a3, sp, 0	# %sfp,
	movi.n	a4, 0	#,
# @OPUS@\upstream\celt\cwrs.c:502:         _i-=p;
	sub	a2, a2, a6	# _i, _i, p
# @OPUS@\upstream\celt\cwrs.c:503:         *_y++=0;
	mov.n	a11, a5	# _716, _714
	s32i.n	a4, a3, 0	# MEM[base: _533, offset: 0B],
	addi.n	a6, a13, -1	# _n, _n,
	mov.n	a5, a3	#,
	j	.L32		#
.L33:
# @OPUS@\upstream\celt\cwrs.c:507:         s=-(_i>=q);
	movi.n	a6, 1	# tmp335,
	bgeu	a2, a4, .L36	# _i, q,
	movi.n	a6, 0	# tmp335,
.L36:
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi.n	a8, a12, -1	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a9, a8, 2	# tmp339, _k,
	add.n	a9, a14, a9	# tmp340, tmp450, tmp339
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a11, a9, 0	# CELT_PVQ_U_ROW, tmp341
# @OPUS@\upstream\celt\cwrs.c:507:         s=-(_i>=q);
	neg	a6, a6	# s, tmp335
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	add.n	a11, a11, a3	# tmp342, tmp341, _529
# @OPUS@\upstream\celt\cwrs.c:508:         _i-=q&s;
	and	a9, a6, a4	# tmp337, s, q
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a11, 0	# *_617, p
# @OPUS@\upstream\celt\cwrs.c:508:         _i-=q&s;
	sub	a2, a2, a9	# _i, _i, tmp337
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -2	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp344, _k,
	add.n	a4, a14, a4	# tmp345, tmp450, tmp344
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp346
	add.n	a4, a4, a3	# tmp347, tmp346, _529
	l32i.n	a4, a4, 0	# *_612, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -3	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp349, _k,
	add.n	a4, a14, a4	# tmp350, tmp450, tmp349
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp351
	add.n	a4, a4, a3	# tmp352, tmp351, _529
	l32i.n	a4, a4, 0	# *_607, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -4	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp354, _k,
	add.n	a4, a14, a4	# tmp355, tmp450, tmp354
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp356
	add.n	a4, a4, a3	# tmp357, tmp356, _529
	l32i.n	a4, a4, 0	# *_602, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -5	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp359, _k,
	add.n	a4, a14, a4	# tmp360, tmp450, tmp359
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp361
	add.n	a4, a4, a3	# tmp362, tmp361, _529
	l32i.n	a4, a4, 0	# *_597, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -6	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp364, _k,
	add.n	a4, a14, a4	# tmp365, tmp450, tmp364
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp366
	add.n	a4, a4, a3	# tmp367, tmp366, _529
	l32i.n	a4, a4, 0	# *_592, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -7	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp369, _k,
	add.n	a4, a14, a4	# tmp370, tmp450, tmp369
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp371
	add.n	a4, a4, a3	# tmp372, tmp371, _529
	l32i.n	a4, a4, 0	# *_587, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -8	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp374, _k,
	add.n	a4, a14, a4	# tmp375, tmp450, tmp374
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp376
	add.n	a4, a4, a3	# tmp377, tmp376, _529
	l32i.n	a4, a4, 0	# *_582, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -9	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp379, _k,
	add.n	a4, a14, a4	# tmp380, tmp450, tmp379
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp381
	add.n	a4, a4, a3	# tmp382, tmp381, _529
	l32i.n	a4, a4, 0	# *_577, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -10	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp384, _k,
	add.n	a4, a14, a4	# tmp385, tmp450, tmp384
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp386
	add.n	a4, a4, a3	# tmp387, tmp386, _529
	l32i.n	a4, a4, 0	# *_572, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -11	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp389, _k,
	add.n	a4, a14, a4	# tmp390, tmp450, tmp389
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp391
	add.n	a4, a4, a3	# tmp392, tmp391, _529
	l32i.n	a4, a4, 0	# *_567, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -12	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp394, _k,
	add.n	a4, a14, a4	# tmp395, tmp450, tmp394
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp396
	add.n	a4, a4, a3	# tmp397, tmp396, _529
	l32i.n	a4, a4, 0	# *_562, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -13	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp399, _k,
	add.n	a4, a14, a4	# tmp400, tmp450, tmp399
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp401
	add.n	a4, a4, a3	# tmp402, tmp401, _529
	l32i.n	a4, a4, 0	# *_557, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a8, a12, -14	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a8, 2	# tmp404, _k,
	add.n	a4, a14, a4	# tmp405, tmp450, tmp404
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp406
	add.n	a4, a4, a3	# tmp407, tmp406, _529
	l32i.n	a4, a4, 0	# *_552, p
# @OPUS@\upstream\celt\cwrs.c:512:         while(p>_i);
	bgeu	a2, a4, .L56	# _i, p,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	addi	a12, a12, -15	# _k, _k,
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	slli	a4, a12, 2	# tmp409, _k,
	add.n	a4, a14, a4	# tmp410, tmp450, tmp409
# @OPUS@\upstream\celt\cwrs.c:511:         do p=CELT_PVQ_U_ROW[--_k][_n];
	l32i.n	a4, a4, 0	# CELT_PVQ_U_ROW, tmp411
	add.n	a3, a4, a3	# tmp412, tmp411, _529
	l32i.n	a4, a3, 0	# *_102, p
	j	.L37		#
.L56:
	mov.n	a12, a8	# _k, _k
.L37:
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	slli	a3, a6, 16	# tmp414, s,
	srai	a3, a3, 16	# _110, tmp414,
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	slli	a9, a12, 16	# tmp451, _k,
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	add.n	a5, a3, a5	# tmp415, _110, _714
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	srai	a11, a9, 16	# _716, tmp451,
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	sub	a5, a5, a11	# tmp417, tmp415, _716
# @OPUS@\upstream\celt\cwrs.c:514:         val=(k0-_k+s)^s;
	xor	a3, a3, a5	# tmp419, _110, tmp417
	slli	a3, a3, 16	# tmp420, tmp419,
	srai	a3, a3, 16	# val, tmp420,
# @OPUS@\upstream\celt\cwrs.c:516:         yy=MAC16_16(yy,val,val);
	mull	a5, a3, a3	# tmp421, val, val
# @OPUS@\upstream\celt\cwrs.c:513:         _i-=p;
	sub	a2, a2, a4	# _i, _i, p
# @OPUS@\upstream\celt\cwrs.c:515:         *_y++=val;
	l32i.n	a4, sp, 0	# %sfp,
# @OPUS@\upstream\celt\cwrs.c:516:         yy=MAC16_16(yy,val,val);
	add.n	a10, a10, a5	# yy, yy, tmp421
# @OPUS@\upstream\celt\cwrs.c:515:         *_y++=val;
	s32i.n	a3, a4, 0	# MEM[base: _532, offset: 0B], val
	addi.n	a6, a13, -1	# _n, _n,
	mov.n	a5, a4	#,
.L32:
	addi.n	a5, a5, 4	#,,
	s32i.n	a5, sp, 0	# %sfp,
# @OPUS@\upstream\celt\cwrs.c:519:     _n--;
	mov.n	a13, a6	# _n, _n
	addi	a7, a7, -4	# ivtmp$73, ivtmp$73,
# @OPUS@\upstream\celt\cwrs.c:471:   while(_n>2){
	beqi	a6, 2, .L69	# _n,,
	addi.n	a15, a12, 1	# tmp449, _k,
	j	.L38		#
.L69:
	l32i.n	a4, sp, 8	# %sfp,
	addi	a3, a4, 52	# tmp422,,
	l32i.n	a4, sp, 4	# %sfp,
	add.n	a4, a4, a3	#,, tmp422
	s32i.n	a4, sp, 4	# %sfp,
	j	.L39		#
.L25:
	slli	a11, a12, 16	# tmp423, _k,
	srai	a11, a11, 16	# _716, tmp423,
# @OPUS@\upstream\celt\cwrs.c:468:   opus_val32  yy=0;
	movi.n	a10, 0	# yy,
.L39:
# @OPUS@\upstream\celt\cwrs.c:522:   p=2*_k+1;
	slli	a12, a12, 1	# tmp424, _k,
# @OPUS@\upstream\celt\cwrs.c:522:   p=2*_k+1;
	addi.n	a12, a12, 1	# p, tmp424,
# @OPUS@\upstream\celt\cwrs.c:523:   s=-(_i>=p);
	movi.n	a4, 1	# tmp425,
	bgeu	a2, a12, .L40	# _i, p,
	movi.n	a4, 0	# tmp425,
.L40:
# @OPUS@\upstream\celt\cwrs.c:523:   s=-(_i>=p);
	neg	a4, a4	# s, tmp425
# @OPUS@\upstream\celt\cwrs.c:524:   _i-=p&s;
	and	a12, a4, a12	# tmp427, s, p
# @OPUS@\upstream\celt\cwrs.c:524:   _i-=p&s;
	sub	a12, a2, a12	# _i, _i, tmp427
# @OPUS@\upstream\celt\cwrs.c:526:   _k=(_i+1)>>1;
	addi.n	a2, a12, 1	# _129, _i,
# @OPUS@\upstream\celt\cwrs.c:526:   _k=(_i+1)>>1;
	srli	a3, a2, 1	# _130, _129,
# @OPUS@\upstream\celt\cwrs.c:527:   if(_k)_i-=2*_k-1;
	beqz.n	a3, .L41	# _130,
# @OPUS@\upstream\celt\cwrs.c:527:   if(_k)_i-=2*_k-1;
	slli	a12, a3, 1	# tmp428, _130,
# @OPUS@\upstream\celt\cwrs.c:527:   if(_k)_i-=2*_k-1;
	sub	a12, a2, a12	# _i, _129, tmp428
.L41:
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	slli	a4, a4, 16	# tmp430, s,
	srai	a4, a4, 16	# _139, tmp430,
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	slli	a3, a3, 16	# tmp429, _130,
	srai	a3, a3, 16	# _137, tmp429,
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	add.n	a11, a4, a11	# tmp431, _139, _716
# @OPUS@\upstream\celt\cwrs.c:532:   s=-(int)_i;
	neg	a12, a12	# s, _i
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	sub	a11, a11, a3	# tmp433, tmp431, _137
# @OPUS@\upstream\celt\cwrs.c:533:   val=(_k+s)^s;
	slli	a12, a12, 16	# tmp439, s,
	srai	a12, a12, 16	# _150, tmp439,
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	xor	a4, a4, a11	# tmp435, _139, tmp433
# @OPUS@\upstream\celt\cwrs.c:533:   val=(_k+s)^s;
	add.n	a3, a3, a12	# tmp440, _137, _150
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	slli	a4, a4, 16	# tmp436, tmp435,
# @OPUS@\upstream\celt\cwrs.c:533:   val=(_k+s)^s;
	xor	a3, a12, a3	# tmp442, _150, tmp440
# @OPUS@\upstream\celt\cwrs.c:528:   val=(k0-_k+s)^s;
	srai	a4, a4, 16	# val, tmp436,
# @OPUS@\upstream\celt\cwrs.c:530:   yy=MAC16_16(yy,val,val);
	mull	a5, a4, a4	# tmp437, val, val
# @OPUS@\upstream\celt\cwrs.c:533:   val=(_k+s)^s;
	slli	a3, a3, 16	# tmp443, tmp442,
	srai	a3, a3, 16	# val, tmp443,
# @OPUS@\upstream\celt\cwrs.c:530:   yy=MAC16_16(yy,val,val);
	add.n	a10, a5, a10	# yy, tmp437, yy
# @OPUS@\upstream\celt\cwrs.c:535:   yy=MAC16_16(yy,val,val);
	mull	a2, a3, a3	# tmp445, val, val
# @OPUS@\upstream\celt\cwrs.c:529:   *_y++=val;
	l32i.n	a5, sp, 4	# %sfp,
# @OPUS@\upstream\celt\cwrs.c:541: }
	l32i.n	a0, sp, 44	#,
	add.n	a2, a2, a10	#, tmp445, yy
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
# @OPUS@\upstream\celt\cwrs.c:529:   *_y++=val;
	s32i.n	a4, a5, 0	# *_y_184, val
# @OPUS@\upstream\celt\cwrs.c:534:   *_y=val;
	s32i.n	a3, a5, 4	# MEM[(int *)_y_184 + 4B], val
# @OPUS@\upstream\celt\cwrs.c:541: }
	addi	sp, sp, 48	#,,
	ret.n
	.size	decode_pulses, .-decode_pulses
	.section	.rodata.CELT_PVQ_U_ROW,"a"
	.align	4
	.type	CELT_PVQ_U_ROW, @object
	.size	CELT_PVQ_U_ROW, 60
CELT_PVQ_U_ROW:
	.word	CELT_PVQ_U_DATA
	.word	CELT_PVQ_U_DATA+704
	.word	CELT_PVQ_U_DATA+1404
	.word	CELT_PVQ_U_DATA+2100
	.word	CELT_PVQ_U_DATA+2792
	.word	CELT_PVQ_U_DATA+3480
	.word	CELT_PVQ_U_DATA+4164
	.word	CELT_PVQ_U_DATA+4524
	.word	CELT_PVQ_U_DATA+4712
	.word	CELT_PVQ_U_DATA+4828
	.word	CELT_PVQ_U_DATA+4904
	.word	CELT_PVQ_U_DATA+4960
	.word	CELT_PVQ_U_DATA+4992
	.word	CELT_PVQ_U_DATA+5016
	.word	CELT_PVQ_U_DATA+5028
	.section	.rodata.CELT_PVQ_U_DATA,"a"
	.align	4
	.type	CELT_PVQ_U_DATA, @object
	.size	CELT_PVQ_U_DATA, 5088
CELT_PVQ_U_DATA:
	.word	1
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	0
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	1
	.word	3
	.word	5
	.word	7
	.word	9
	.word	11
	.word	13
	.word	15
	.word	17
	.word	19
	.word	21
	.word	23
	.word	25
	.word	27
	.word	29
	.word	31
	.word	33
	.word	35
	.word	37
	.word	39
	.word	41
	.word	43
	.word	45
	.word	47
	.word	49
	.word	51
	.word	53
	.word	55
	.word	57
	.word	59
	.word	61
	.word	63
	.word	65
	.word	67
	.word	69
	.word	71
	.word	73
	.word	75
	.word	77
	.word	79
	.word	81
	.word	83
	.word	85
	.word	87
	.word	89
	.word	91
	.word	93
	.word	95
	.word	97
	.word	99
	.word	101
	.word	103
	.word	105
	.word	107
	.word	109
	.word	111
	.word	113
	.word	115
	.word	117
	.word	119
	.word	121
	.word	123
	.word	125
	.word	127
	.word	129
	.word	131
	.word	133
	.word	135
	.word	137
	.word	139
	.word	141
	.word	143
	.word	145
	.word	147
	.word	149
	.word	151
	.word	153
	.word	155
	.word	157
	.word	159
	.word	161
	.word	163
	.word	165
	.word	167
	.word	169
	.word	171
	.word	173
	.word	175
	.word	177
	.word	179
	.word	181
	.word	183
	.word	185
	.word	187
	.word	189
	.word	191
	.word	193
	.word	195
	.word	197
	.word	199
	.word	201
	.word	203
	.word	205
	.word	207
	.word	209
	.word	211
	.word	213
	.word	215
	.word	217
	.word	219
	.word	221
	.word	223
	.word	225
	.word	227
	.word	229
	.word	231
	.word	233
	.word	235
	.word	237
	.word	239
	.word	241
	.word	243
	.word	245
	.word	247
	.word	249
	.word	251
	.word	253
	.word	255
	.word	257
	.word	259
	.word	261
	.word	263
	.word	265
	.word	267
	.word	269
	.word	271
	.word	273
	.word	275
	.word	277
	.word	279
	.word	281
	.word	283
	.word	285
	.word	287
	.word	289
	.word	291
	.word	293
	.word	295
	.word	297
	.word	299
	.word	301
	.word	303
	.word	305
	.word	307
	.word	309
	.word	311
	.word	313
	.word	315
	.word	317
	.word	319
	.word	321
	.word	323
	.word	325
	.word	327
	.word	329
	.word	331
	.word	333
	.word	335
	.word	337
	.word	339
	.word	341
	.word	343
	.word	345
	.word	347
	.word	349
	.word	351
	.word	13
	.word	25
	.word	41
	.word	61
	.word	85
	.word	113
	.word	145
	.word	181
	.word	221
	.word	265
	.word	313
	.word	365
	.word	421
	.word	481
	.word	545
	.word	613
	.word	685
	.word	761
	.word	841
	.word	925
	.word	1013
	.word	1105
	.word	1201
	.word	1301
	.word	1405
	.word	1513
	.word	1625
	.word	1741
	.word	1861
	.word	1985
	.word	2113
	.word	2245
	.word	2381
	.word	2521
	.word	2665
	.word	2813
	.word	2965
	.word	3121
	.word	3281
	.word	3445
	.word	3613
	.word	3785
	.word	3961
	.word	4141
	.word	4325
	.word	4513
	.word	4705
	.word	4901
	.word	5101
	.word	5305
	.word	5513
	.word	5725
	.word	5941
	.word	6161
	.word	6385
	.word	6613
	.word	6845
	.word	7081
	.word	7321
	.word	7565
	.word	7813
	.word	8065
	.word	8321
	.word	8581
	.word	8845
	.word	9113
	.word	9385
	.word	9661
	.word	9941
	.word	10225
	.word	10513
	.word	10805
	.word	11101
	.word	11401
	.word	11705
	.word	12013
	.word	12325
	.word	12641
	.word	12961
	.word	13285
	.word	13613
	.word	13945
	.word	14281
	.word	14621
	.word	14965
	.word	15313
	.word	15665
	.word	16021
	.word	16381
	.word	16745
	.word	17113
	.word	17485
	.word	17861
	.word	18241
	.word	18625
	.word	19013
	.word	19405
	.word	19801
	.word	20201
	.word	20605
	.word	21013
	.word	21425
	.word	21841
	.word	22261
	.word	22685
	.word	23113
	.word	23545
	.word	23981
	.word	24421
	.word	24865
	.word	25313
	.word	25765
	.word	26221
	.word	26681
	.word	27145
	.word	27613
	.word	28085
	.word	28561
	.word	29041
	.word	29525
	.word	30013
	.word	30505
	.word	31001
	.word	31501
	.word	32005
	.word	32513
	.word	33025
	.word	33541
	.word	34061
	.word	34585
	.word	35113
	.word	35645
	.word	36181
	.word	36721
	.word	37265
	.word	37813
	.word	38365
	.word	38921
	.word	39481
	.word	40045
	.word	40613
	.word	41185
	.word	41761
	.word	42341
	.word	42925
	.word	43513
	.word	44105
	.word	44701
	.word	45301
	.word	45905
	.word	46513
	.word	47125
	.word	47741
	.word	48361
	.word	48985
	.word	49613
	.word	50245
	.word	50881
	.word	51521
	.word	52165
	.word	52813
	.word	53465
	.word	54121
	.word	54781
	.word	55445
	.word	56113
	.word	56785
	.word	57461
	.word	58141
	.word	58825
	.word	59513
	.word	60205
	.word	60901
	.word	61601
	.word	63
	.word	129
	.word	231
	.word	377
	.word	575
	.word	833
	.word	1159
	.word	1561
	.word	2047
	.word	2625
	.word	3303
	.word	4089
	.word	4991
	.word	6017
	.word	7175
	.word	8473
	.word	9919
	.word	11521
	.word	13287
	.word	15225
	.word	17343
	.word	19649
	.word	22151
	.word	24857
	.word	27775
	.word	30913
	.word	34279
	.word	37881
	.word	41727
	.word	45825
	.word	50183
	.word	54809
	.word	59711
	.word	64897
	.word	70375
	.word	76153
	.word	82239
	.word	88641
	.word	95367
	.word	102425
	.word	109823
	.word	117569
	.word	125671
	.word	134137
	.word	142975
	.word	152193
	.word	161799
	.word	171801
	.word	182207
	.word	193025
	.word	204263
	.word	215929
	.word	228031
	.word	240577
	.word	253575
	.word	267033
	.word	280959
	.word	295361
	.word	310247
	.word	325625
	.word	341503
	.word	357889
	.word	374791
	.word	392217
	.word	410175
	.word	428673
	.word	447719
	.word	467321
	.word	487487
	.word	508225
	.word	529543
	.word	551449
	.word	573951
	.word	597057
	.word	620775
	.word	645113
	.word	670079
	.word	695681
	.word	721927
	.word	748825
	.word	776383
	.word	804609
	.word	833511
	.word	863097
	.word	893375
	.word	924353
	.word	956039
	.word	988441
	.word	1021567
	.word	1055425
	.word	1090023
	.word	1125369
	.word	1161471
	.word	1198337
	.word	1235975
	.word	1274393
	.word	1313599
	.word	1353601
	.word	1394407
	.word	1436025
	.word	1478463
	.word	1521729
	.word	1565831
	.word	1610777
	.word	1656575
	.word	1703233
	.word	1750759
	.word	1799161
	.word	1848447
	.word	1898625
	.word	1949703
	.word	2001689
	.word	2054591
	.word	2108417
	.word	2163175
	.word	2218873
	.word	2275519
	.word	2333121
	.word	2391687
	.word	2451225
	.word	2511743
	.word	2573249
	.word	2635751
	.word	2699257
	.word	2763775
	.word	2829313
	.word	2895879
	.word	2963481
	.word	3032127
	.word	3101825
	.word	3172583
	.word	3244409
	.word	3317311
	.word	3391297
	.word	3466375
	.word	3542553
	.word	3619839
	.word	3698241
	.word	3777767
	.word	3858425
	.word	3940223
	.word	4023169
	.word	4107271
	.word	4192537
	.word	4278975
	.word	4366593
	.word	4455399
	.word	4545401
	.word	4636607
	.word	4729025
	.word	4822663
	.word	4917529
	.word	5013631
	.word	5110977
	.word	5209575
	.word	5309433
	.word	5410559
	.word	5512961
	.word	5616647
	.word	5721625
	.word	5827903
	.word	5935489
	.word	6044391
	.word	6154617
	.word	6266175
	.word	6379073
	.word	6493319
	.word	6608921
	.word	6725887
	.word	6844225
	.word	6963943
	.word	7085049
	.word	7207551
	.word	321
	.word	681
	.word	1289
	.word	2241
	.word	3649
	.word	5641
	.word	8361
	.word	11969
	.word	16641
	.word	22569
	.word	29961
	.word	39041
	.word	50049
	.word	63241
	.word	78889
	.word	97281
	.word	118721
	.word	143529
	.word	172041
	.word	204609
	.word	241601
	.word	283401
	.word	330409
	.word	383041
	.word	441729
	.word	506921
	.word	579081
	.word	658689
	.word	746241
	.word	842249
	.word	947241
	.word	1061761
	.word	1186369
	.word	1321641
	.word	1468169
	.word	1626561
	.word	1797441
	.word	1981449
	.word	2179241
	.word	2391489
	.word	2618881
	.word	2862121
	.word	3121929
	.word	3399041
	.word	3694209
	.word	4008201
	.word	4341801
	.word	4695809
	.word	5071041
	.word	5468329
	.word	5888521
	.word	6332481
	.word	6801089
	.word	7295241
	.word	7815849
	.word	8363841
	.word	8940161
	.word	9545769
	.word	10181641
	.word	10848769
	.word	11548161
	.word	12280841
	.word	13047849
	.word	13850241
	.word	14689089
	.word	15565481
	.word	16480521
	.word	17435329
	.word	18431041
	.word	19468809
	.word	20549801
	.word	21675201
	.word	22846209
	.word	24064041
	.word	25329929
	.word	26645121
	.word	28010881
	.word	29428489
	.word	30899241
	.word	32424449
	.word	34005441
	.word	35643561
	.word	37340169
	.word	39096641
	.word	40914369
	.word	42794761
	.word	44739241
	.word	46749249
	.word	48826241
	.word	50971689
	.word	53187081
	.word	55473921
	.word	57833729
	.word	60268041
	.word	62778409
	.word	65366401
	.word	68033601
	.word	70781609
	.word	73612041
	.word	76526529
	.word	79526721
	.word	82614281
	.word	85790889
	.word	89058241
	.word	92418049
	.word	95872041
	.word	99421961
	.word	103069569
	.word	106816641
	.word	110664969
	.word	114616361
	.word	118672641
	.word	122835649
	.word	127107241
	.word	131489289
	.word	135983681
	.word	140592321
	.word	145317129
	.word	150160041
	.word	155123009
	.word	160208001
	.word	165417001
	.word	170752009
	.word	176215041
	.word	181808129
	.word	187533321
	.word	193392681
	.word	199388289
	.word	205522241
	.word	211796649
	.word	218213641
	.word	224775361
	.word	231483969
	.word	238341641
	.word	245350569
	.word	252512961
	.word	259831041
	.word	267307049
	.word	274943241
	.word	282741889
	.word	290705281
	.word	298835721
	.word	307135529
	.word	315607041
	.word	324252609
	.word	333074601
	.word	342075401
	.word	351257409
	.word	360623041
	.word	370174729
	.word	379914921
	.word	389846081
	.word	399970689
	.word	410291241
	.word	420810249
	.word	431530241
	.word	442453761
	.word	453583369
	.word	464921641
	.word	476471169
	.word	488234561
	.word	500214441
	.word	512413449
	.word	524834241
	.word	537479489
	.word	550351881
	.word	563454121
	.word	576788929
	.word	590359041
	.word	604167209
	.word	618216201
	.word	632508801
	.word	1683
	.word	3653
	.word	7183
	.word	13073
	.word	22363
	.word	36365
	.word	56695
	.word	85305
	.word	124515
	.word	177045
	.word	246047
	.word	335137
	.word	448427
	.word	590557
	.word	766727
	.word	982729
	.word	1244979
	.word	1560549
	.word	1937199
	.word	2383409
	.word	2908411
	.word	3522221
	.word	4235671
	.word	5060441
	.word	6009091
	.word	7095093
	.word	8332863
	.word	9737793
	.word	11326283
	.word	13115773
	.word	15124775
	.word	17372905
	.word	19880915
	.word	22670725
	.word	25765455
	.word	29189457
	.word	32968347
	.word	37129037
	.word	41699767
	.word	46710137
	.word	52191139
	.word	58175189
	.word	64696159
	.word	71789409
	.word	79491819
	.word	87841821
	.word	96879431
	.word	106646281
	.word	117185651
	.word	128542501
	.word	140763503
	.word	153897073
	.word	167993403
	.word	183104493
	.word	199284183
	.word	216588185
	.word	235074115
	.word	254801525
	.word	275831935
	.word	298228865
	.word	322057867
	.word	347386557
	.word	374284647
	.word	402823977
	.word	433078547
	.word	465124549
	.word	499040399
	.word	534906769
	.word	572806619
	.word	612825229
	.word	655050231
	.word	699571641
	.word	746481891
	.word	795875861
	.word	847850911
	.word	902506913
	.word	959946283
	.word	1020274013
	.word	1083597703
	.word	1150027593
	.word	1219676595
	.word	1292660325
	.word	1369097135
	.word	1449108145
	.word	1532817275
	.word	1620351277
	.word	1711839767
	.word	1807415257
	.word	1907213187
	.word	2011371957
	.word	2120032959
	.word	8989
	.word	19825
	.word	40081
	.word	75517
	.word	134245
	.word	227305
	.word	369305
	.word	579125
	.word	880685
	.word	1303777
	.word	1884961
	.word	2668525
	.word	3707509
	.word	5064793
	.word	6814249
	.word	9041957
	.word	11847485
	.word	15345233
	.word	19665841
	.word	24957661
	.word	31388293
	.word	39146185
	.word	48442297
	.word	59511829
	.word	72616013
	.word	88043969
	.word	106114625
	.word	127178701
	.word	151620757
	.word	179861305
	.word	212358985
	.word	249612805
	.word	292164445
	.word	340600625
	.word	395555537
	.word	457713341
	.word	527810725
	.word	606639529
	.word	695049433
	.word	793950709
	.word	904317037
	.word	1027188385
	.word	1163673953
	.word	1314955181
	.word	1482288821
	.word	1667010073
	.word	1870535785
	.word	2094367717
	.word	48639
	.word	108545
	.word	224143
	.word	433905
	.word	795455
	.word	1392065
	.word	2340495
	.word	3800305
	.word	5984767
	.word	9173505
	.word	13726991
	.word	20103025
	.word	28875327
	.word	40754369
	.word	56610575
	.word	77500017
	.word	104692735
	.word	139703809
	.word	184327311
	.word	240673265
	.word	311207743
	.word	398796225
	.word	506750351
	.word	638878193
	.word	799538175
	.word	993696769
	.word	1226990095
	.word	1505789553
	.word	1837271615
	.word	-2065475391
	.word	265729
	.word	598417
	.word	1256465
	.word	2485825
	.word	4673345
	.word	8405905
	.word	14546705
	.word	24331777
	.word	39490049
	.word	62390545
	.word	96220561
	.word	145198913
	.word	214828609
	.word	312193553
	.word	446304145
	.word	628496897
	.word	872893441
	.word	1196924561
	.word	1621925137
	.word	-2121161151
	.word	1462563
	.word	3317445
	.word	7059735
	.word	14218905
	.word	27298155
	.word	50250765
	.word	89129247
	.word	152951073
	.word	254831667
	.word	413442773
	.word	654862247
	.word	1014889769
	.word	1541911931
	.word	-1994557667
	.word	-919756625
	.word	8097453
	.word	18474633
	.word	39753273
	.word	81270333
	.word	158819253
	.word	298199265
	.word	540279585
	.word	948062325
	.word	1616336765
	.word	45046719
	.word	103274625
	.word	224298231
	.word	464387817
	.word	921406335
	.word	1759885185
	.word	-1046740201
	.word	251595969
	.word	579168825
	.word	1267854873
	.word	-1641318271
	.word	1409933619
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
