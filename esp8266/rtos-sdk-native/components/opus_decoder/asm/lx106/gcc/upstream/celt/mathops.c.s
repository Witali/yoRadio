# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/mathops.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"mathops.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\mathops.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\mathops.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\mathops.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\mathops.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\mathops.c.s.raw
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
	.section	.text.isqrt32,"ax",@progbits
	.literal_position
	.align	4
	.global	isqrt32
	.type	isqrt32, @function
# Function: isqrt32
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: /*Compute floor(sqrt(_val)) with exact arithmetic.
# C context: _val must be greater than 0.
# C context: This has been tested on all possible 32-bit inputs greater than 0.*/
# C context: unsigned isqrt32(opus_uint32 _val){
# C context: unsigned b;
# C context: unsigned g;
# C context: int      bshift;
# C context: /*Uses the second method from
isqrt32:
# @OPUS@\upstream\celt\mathops.c:52:   bshift=(EC_ILOG(_val)-1)>>1;
	nsau	a3, a2	# _1, _val
# @OPUS@\upstream\celt\mathops.c:52:   bshift=(EC_ILOG(_val)-1)>>1;
	movi.n	a4, 0x1f	# tmp122,
	sub	a4, a4, a3	# tmp123, tmp122, _1
# @OPUS@\upstream\celt\mathops.c:52:   bshift=(EC_ILOG(_val)-1)>>1;
	srai	a4, a4, 1	# bshift, tmp123,
# @OPUS@\upstream\celt\mathops.c:53:   b=1U<<bshift;
	movi.n	a5, 1	# tmp124,
	ssl	a4	# bshift
	sll	a5, a5	# b, tmp124
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a4	# bshift
	sll	a6, a5	# t, b
# @OPUS@\upstream\celt\mathops.c:51:   g=0;
	movi.n	a3, 0	# <retval>,
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L2	# _val, t,
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	mov.n	a3, a5	# <retval>, b
.L2:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi.n	a7, a4, -1	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 1	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	bltz	a7, .L1	# bshift,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp125, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp126, tmp125, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp126
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L4	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L4:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -2	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 2	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp127, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp128, tmp127, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp128
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L5	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L5:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -3	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 3	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp129, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp130, tmp129, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp130
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L6	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L6:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -4	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 4	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp131, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp132, tmp131, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp132
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L7	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L7:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -5	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 5	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp133, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp134, tmp133, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp134
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L8	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L8:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -6	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 6	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp135, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp136, tmp135, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp136
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L9	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L9:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -7	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 7	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp137, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp138, tmp137, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp138
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L10	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L10:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -8	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 8	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp139, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp140, tmp139, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp140
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L11	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L11:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -9	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 9	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp141, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp142, tmp141, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp142
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L12	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L12:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -10	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 10	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp143, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp144, tmp143, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp144
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L13	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L13:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -11	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 11	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp145, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp146, tmp145, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp146
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L14	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L14:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -12	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 12	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp147, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp148, tmp147, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp148
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L15	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L15:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -13	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 13	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp149, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp150, tmp149, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp150
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L16	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L16:
# @OPUS@\upstream\celt\mathops.c:62:     bshift--;
	addi	a7, a4, -14	# bshift, bshift,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	srli	a8, a5, 14	# b, b,
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	beqi	a7, -1, .L1	# bshift,,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a6, a3, 1	# tmp151, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a6, a6, a8	# tmp152, tmp151, b
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	ssl	a7	# bshift
	sll	a6, a6	# t, tmp152
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a6, .L17	# _val, t,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a8	# <retval>, <retval>, b
# @OPUS@\upstream\celt\mathops.c:59:       _val-=t;
	sub	a2, a2, a6	# _val, _val, t
.L17:
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	movi.n	a6, 0xf	# tmp153,
# @OPUS@\upstream\celt\mathops.c:61:     b>>=1;
	ssr	a6	#
	srl	a5, a5	# b, b
# @OPUS@\upstream\celt\mathops.c:64:   while(bshift>=0);
	bne	a4, a6, .L1	# bshift, tmp153,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	slli	a4, a3, 1	# tmp154, <retval>,
# @OPUS@\upstream\celt\mathops.c:56:     t=(((opus_uint32)g<<1)+b)<<bshift;
	add.n	a4, a4, a5	# tmp155, tmp154, b
# @OPUS@\upstream\celt\mathops.c:57:     if(t<=_val){
	bltu	a2, a4, .L1	# _val, tmp155,
# @OPUS@\upstream\celt\mathops.c:58:       g+=b;
	add.n	a3, a3, a5	# <retval>, <retval>, b
.L1:
# @OPUS@\upstream\celt\mathops.c:66: }
	mov.n	a2, a3	#, <retval>
	ret.n
	.size	isqrt32, .-isqrt32
	.section	.text.celt_rsqrt_norm,"ax",@progbits
	.literal_position
	.literal .LC0, -13490
	.literal .LC1, 23557
	.align	4
	.global	celt_rsqrt_norm
	.type	celt_rsqrt_norm, @function
# Function: celt_rsqrt_norm
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /** Reciprocal sqrt approximation in the range [0.25,1) (Q16 in, Q14 out) */
# C context: opus_val16 celt_rsqrt_norm(opus_val32 x)
# C context: {
# C context: opus_val16 n;
# C context: opus_val16 r;
# C context: opus_val16 r2;
celt_rsqrt_norm:
# @OPUS@\upstream\celt\mathops.c:98:    n = x-32768;
	addmi	a3, a2, -0x8000	# tmp77, x,
	slli	a3, a3, 16	# tmp78, tmp77,
	srai	a3, a3, 16	# n, tmp78,
# @OPUS@\upstream\celt\mathops.c:103:    r = ADD16(23557, MULT16_16_Q15(n, ADD16(-13490, MULT16_16_Q15(n, 6713))));
	slli	a2, a3, 4	# tmp80, n,
	sub	a2, a2, a3	# tmp81, tmp80, n
	slli	a2, a2, 6	# tmp82, tmp81,
	sub	a4, a2, a3	# tmp83, tmp82, n
	slli	a2, a4, 3	# tmp84, tmp83,
	sub	a2, a2, a4	# tmp85, tmp84, tmp83
	l32r	a4, .LC0	#, tmp89
	srai	a2, a2, 15	# tmp86, tmp85,
	add.n	a2, a2, a4	# tmp88, tmp86, tmp89
	mul16s	a2, a2, a3	# tmp90, tmp88, n
# @OPUS@\upstream\celt\mathops.c:103:    r = ADD16(23557, MULT16_16_Q15(n, ADD16(-13490, MULT16_16_Q15(n, 6713))));
	l32r	a4, .LC1	#, tmp94
# @OPUS@\upstream\celt\mathops.c:103:    r = ADD16(23557, MULT16_16_Q15(n, ADD16(-13490, MULT16_16_Q15(n, 6713))));
	srai	a2, a2, 15	# tmp91, tmp90,
# @OPUS@\upstream\celt\mathops.c:103:    r = ADD16(23557, MULT16_16_Q15(n, ADD16(-13490, MULT16_16_Q15(n, 6713))));
	add.n	a2, a2, a4	# tmp93, tmp91, tmp94
	slli	a2, a2, 16	# tmp95, tmp93,
	srai	a2, a2, 16	# r, tmp95,
# @OPUS@\upstream\celt\mathops.c:108:    r2 = MULT16_16_Q15(r, r);
	mull	a4, a2, a2	# tmp96, r, r
# @OPUS@\upstream\celt\mathops.c:108:    r2 = MULT16_16_Q15(r, r);
	slli	a4, a4, 1	# tmp98, tmp96,
	srai	a4, a4, 16	# r2, tmp98,
# @OPUS@\upstream\celt\mathops.c:109:    y = SHL16(SUB16(ADD16(MULT16_16_Q15(r2, n), r2), 16384), 1);
	mull	a3, a3, a4	# tmp99, n, r2
	addmi	a4, a4, -0x4000	# tmp101, r2,
	srai	a3, a3, 15	# tmp100, tmp99,
	add.n	a3, a3, a4	# tmp104, tmp100, tmp101
# @OPUS@\upstream\celt\mathops.c:109:    y = SHL16(SUB16(ADD16(MULT16_16_Q15(r2, n), r2), 16384), 1);
	slli	a3, a3, 17	# tmp107, tmp104,
	srai	a3, a3, 16	# y, tmp107,
# @OPUS@\upstream\celt\mathops.c:114:    return ADD16(r, MULT16_16_Q15(r, MULT16_16_Q15(y,
	slli	a4, a3, 1	# tmp110, y,
	add.n	a4, a4, a3	# tmp111, tmp110, y
	srai	a4, a4, 3	# tmp113, tmp111,
	addmi	a4, a4, -0x4000	# tmp115, tmp113,
	mul16s	a3, a4, a3	# tmp116, tmp115, y
	srai	a3, a3, 15	# tmp117, tmp116,
	mull	a3, a3, a2	# tmp118, tmp117, r
	srai	a3, a3, 15	# tmp119, tmp118,
	add.n	a2, a2, a3	# tmp121, r, tmp119
	slli	a2, a2, 16	# tmp123, tmp121,
# @OPUS@\upstream\celt\mathops.c:116: }
	srai	a2, a2, 16	#, tmp123,
	ret.n
	.size	celt_rsqrt_norm, .-celt_rsqrt_norm
	.section	.text.celt_sqrt,"ax",@progbits
	.literal_position
	.literal .LC2, 32767
	.literal .LC3, 1073741823
	.literal .LC4, -3011
	.literal .LC5, 11561
	.literal .LC6, 23175
	.align	4
	.global	celt_sqrt
	.type	celt_sqrt, @function
# Function: celt_sqrt
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /** Sqrt approximation (QX input, QX/2 output) */
# C context: opus_val32 celt_sqrt(opus_val32 x)
# C context: {
# C context: int k;
# C context: opus_val16 n;
# C context: opus_val32 rt;
celt_sqrt:
# @OPUS@\upstream\celt\mathops.c:120: {
	mov.n	a3, a2	# x, x
# @OPUS@\upstream\celt\mathops.c:126:       return 0;
	movi.n	a2, 0	# <retval>,
# @OPUS@\upstream\celt\mathops.c:125:    if (x==0)
	beq	a3, a2, .L61	# x,,
# @OPUS@\upstream\celt\mathops.c:127:    else if (x>=1073741824)
	l32r	a4, .LC3	#, tmp78
# @OPUS@\upstream\celt\mathops.c:128:       return 32767;
	l32r	a2, .LC2	#, <retval>
# @OPUS@\upstream\celt\mathops.c:127:    else if (x>=1073741824)
	blt	a4, a3, .L61	# tmp78, x,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a2, a3	# _43, x
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	movi.n	a4, 0x1f	# tmp79,
	sub	a4, a4, a2	# tmp81, tmp79, _43
# @OPUS@\upstream\celt\mathops.c:129:    k = (celt_ilog2(x)>>1)-7;
	slli	a4, a4, 16	# tmp83, tmp81,
	srai	a4, a4, 17	# _2, tmp83,
# @OPUS@\upstream\celt\mathops.c:129:    k = (celt_ilog2(x)>>1)-7;
	addi	a5, a4, -7	# k, _2,
# @OPUS@\upstream\celt\mathops.c:130:    x = VSHR32(x, 2*k);
	slli	a2, a5, 1	# _3, k,
	blti	a2, 1, .L63	# _3,,
# @OPUS@\upstream\celt\mathops.c:130:    x = VSHR32(x, 2*k);
	ssr	a2	# _3
	sra	a3, a3	# iftmp$6_32, x
	j	.L64		#
.L63:
# @OPUS@\upstream\celt\mathops.c:130:    x = VSHR32(x, 2*k);
	slli	a2, a5, 1	# tmp88, k,
	neg	a2, a2	# tmp89, tmp88
	ssl	a2	# tmp89
	sll	a3, a3	# iftmp$6_32, x
.L64:
# @OPUS@\upstream\celt\mathops.c:131:    n = x-32768;
	addmi	a3, a3, -0x8000	# tmp91, iftmp$6_32,
	slli	a3, a3, 16	# tmp92, tmp91,
	srai	a2, a3, 16	# n, tmp92,
# @OPUS@\upstream\celt\mathops.c:132:    rt = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2],
	movi	a3, -0x298	# tmp93,
	mul16s	a3, a3, a2	# tmp94, tmp93, n
	movi	a6, 0x6a3	# tmp96,
	srai	a3, a3, 15	# tmp95, tmp94,
	add.n	a3, a3, a6	# tmp98, tmp95, tmp96
	mul16s	a3, a3, a2	# tmp99, tmp98, n
	l32r	a6, .LC4	#, tmp103
	srai	a3, a3, 15	# tmp100, tmp99,
	add.n	a3, a3, a6	# tmp102, tmp100, tmp103
	mul16s	a3, a3, a2	# tmp104, tmp102, n
	l32r	a6, .LC5	#, tmp108
	srai	a3, a3, 15	# tmp105, tmp104,
	add.n	a3, a3, a6	# tmp107, tmp105, tmp108
	mul16s	a3, a3, a2	# tmp109, tmp107, n
	l32r	a2, .LC6	#, tmp113
	srai	a3, a3, 15	# tmp110, tmp109,
	add.n	a3, a3, a2	# tmp112, tmp110, tmp113
# @OPUS@\upstream\celt\mathops.c:134:    rt = VSHR32(rt,7-k);
	movi.n	a2, 7	# tmp115,
# @OPUS@\upstream\celt\mathops.c:132:    rt = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2],
	slli	a3, a3, 16	# tmp114, tmp112,
# @OPUS@\upstream\celt\mathops.c:134:    rt = VSHR32(rt,7-k);
	sub	a5, a2, a5	# _27, tmp115, k
# @OPUS@\upstream\celt\mathops.c:132:    rt = ADD16(C[0], MULT16_16_Q15(n, ADD16(C[1], MULT16_16_Q15(n, ADD16(C[2],
	srai	a2, a3, 16	# _26, tmp114,
# @OPUS@\upstream\celt\mathops.c:134:    rt = VSHR32(rt,7-k);
	blti	a5, 1, .L65	# _27,,
# @OPUS@\upstream\celt\mathops.c:134:    rt = VSHR32(rt,7-k);
	ssr	a5	# _27
	sra	a2, a2	# <retval>, _26
	j	.L61		#
.L65:
# @OPUS@\upstream\celt\mathops.c:134:    rt = VSHR32(rt,7-k);
	addi	a4, a4, -14	# tmp116, _2,
	ssl	a4	# tmp116
	sll	a2, a2	# <retval>, _26
.L61:
# @OPUS@\upstream\celt\mathops.c:136: }
	ret.n
	.size	celt_sqrt, .-celt_sqrt
	.section	.text.celt_cos_norm,"ax",@progbits
	.literal_position
	.literal .LC7, -32767
	.literal .LC8, 32767
	.literal .LC9, 131071
	.literal .LC10, 65536
	.literal .LC11, 131072
	.literal .LC12, 8277
	.literal .LC13, -7651
	.literal .LC14, 32766
	.align	4
	.global	celt_cos_norm
	.type	celt_cos_norm, @function
# Function: celt_cos_norm
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #undef L3
# C context: #undef L4
# C context:
# C context: opus_val16 celt_cos_norm(opus_val32 x)
# C context: {
# C context: x = x&0x0001ffff;
# C context: if (x>SHL32(EXTEND32(1), 16))
# C context: x = SUB32(SHL32(EXTEND32(1), 17),x);
celt_cos_norm:
# @OPUS@\upstream\celt\mathops.c:159:    x = x&0x0001ffff;
	l32r	a3, .LC9	#, tmp98
# @OPUS@\upstream\celt\mathops.c:160:    if (x>SHL32(EXTEND32(1), 16))
	l32r	a4, .LC10	#, tmp99
# @OPUS@\upstream\celt\mathops.c:159:    x = x&0x0001ffff;
	and	a3, a2, a3	# x, x, tmp98
# @OPUS@\upstream\celt\mathops.c:160:    if (x>SHL32(EXTEND32(1), 16))
	bge	a4, a3, .L70	# tmp99, x,
# @OPUS@\upstream\celt\mathops.c:161:       x = SUB32(SHL32(EXTEND32(1), 17),x);
	l32r	a2, .LC11	#, tmp100
	sub	a3, a2, a3	# x, tmp100, x
# @OPUS@\upstream\celt\mathops.c:162:    if (x&0x00007fff)
	extui	a2, a3, 0, 15	# tmp101, x,
# @OPUS@\upstream\celt\mathops.c:162:    if (x&0x00007fff)
	bnez.n	a2, .L71	# tmp101,
	j	.L72		#
.L70:
# @OPUS@\upstream\celt\mathops.c:162:    if (x&0x00007fff)
	extui	a4, a2, 0, 15	# tmp102, x,
# @OPUS@\upstream\celt\mathops.c:162:    if (x&0x00007fff)
	beqz.n	a4, .L73	# tmp102,
.L71:
# @OPUS@\upstream\celt\mathops.c:164:       if (x<SHL32(EXTEND32(1), 15))
	l32r	a2, .LC8	#, tmp103
	blt	a2, a3, .L74	# tmp103, x,
# @OPUS@\upstream\celt\mathops.c:147:    x2 = MULT16_16_P15(x,x);
	mull	a4, a3, a3	# tmp104, x, x
# @OPUS@\upstream\celt\mathops.c:148:    return ADD16(1,MIN16(32766,ADD32(SUB16(L1,x2), MULT16_16_P15(x2, ADD32(L2, MULT16_16_P15(x2, ADD32(L3, MULT16_16_P15(L4, x2
	movi	a5, -0x272	# tmp106,
# @OPUS@\upstream\celt\mathops.c:147:    x2 = MULT16_16_P15(x,x);
	addmi	a4, a4, 0x4000	# tmp105, tmp104,
	srai	a4, a4, 15	# _24, tmp105,
# @OPUS@\upstream\celt\mathops.c:148:    return ADD16(1,MIN16(32766,ADD32(SUB16(L1,x2), MULT16_16_P15(x2, ADD32(L2, MULT16_16_P15(x2, ADD32(L3, MULT16_16_P15(L4, x2
	mull	a5, a4, a5	# tmp107, _24, tmp106
	l32r	a3, .LC12	#, tmp112
	addmi	a5, a5, 0x4000	# tmp108, tmp107,
	srai	a5, a5, 15	# tmp109, tmp108,
	add.n	a5, a5, a3	# tmp111, tmp109, tmp112
	slli	a5, a5, 16	# tmp114, tmp111,
	srai	a5, a5, 16	# tmp113, tmp114,
	mull	a5, a5, a4	# tmp115, tmp113, _24
	l32r	a3, .LC13	#, tmp120
	addmi	a5, a5, 0x4000	# tmp116, tmp115,
	srai	a5, a5, 15	# tmp117, tmp116,
	add.n	a5, a5, a3	# tmp119, tmp117, tmp120
	slli	a5, a5, 16	# tmp122, tmp119,
	srai	a5, a5, 16	# tmp121, tmp122,
	mull	a5, a5, a4	# tmp123, tmp121, _24
	sub	a3, a2, a4	# tmp125, tmp103, _24
	addmi	a5, a5, 0x4000	# tmp124, tmp123,
	srai	a5, a5, 15	# _41, tmp124,
	l32r	a6, .LC14	#, tmp128
	add.n	a3, a3, a5	# tmp127, tmp125, _41
	blt	a6, a3, .L72	# tmp128, tmp127,
	sub	a2, a5, a4	# tmp130, _41, _24
	addmi	a2, a2, -0x8000	# tmp134, tmp130,
	slli	a2, a2, 16	# tmp135, tmp134,
	srai	a2, a2, 16	# <retval>, tmp135,
	j	.L72		#
.L74:
# @OPUS@\upstream\celt\mathops.c:168:          return NEG16(_celt_cos_pi_2(EXTRACT16(65536-x)));
	neg	a4, a3	# tmp137, x
# @OPUS@\upstream\celt\mathops.c:147:    x2 = MULT16_16_P15(x,x);
	mul16s	a4, a4, a4	# tmp139, tmp137, tmp137
# @OPUS@\upstream\celt\mathops.c:148:    return ADD16(1,MIN16(32766,ADD32(SUB16(L1,x2), MULT16_16_P15(x2, ADD32(L2, MULT16_16_P15(x2, ADD32(L3, MULT16_16_P15(L4, x2
	movi	a5, -0x272	# tmp143,
# @OPUS@\upstream\celt\mathops.c:147:    x2 = MULT16_16_P15(x,x);
	addmi	a4, a4, 0x4000	# tmp140, tmp139,
# @OPUS@\upstream\celt\mathops.c:147:    x2 = MULT16_16_P15(x,x);
	slli	a4, a4, 1	# tmp142, tmp140,
	srai	a4, a4, 16	# x2, tmp142,
# @OPUS@\upstream\celt\mathops.c:148:    return ADD16(1,MIN16(32766,ADD32(SUB16(L1,x2), MULT16_16_P15(x2, ADD32(L2, MULT16_16_P15(x2, ADD32(L3, MULT16_16_P15(L4, x2
	mul16s	a5, a5, a4	# tmp144, tmp143, x2
	l32r	a3, .LC12	#, tmp149
	addmi	a5, a5, 0x4000	# tmp145, tmp144,
	srai	a5, a5, 15	# tmp146, tmp145,
	add.n	a5, a5, a3	# tmp148, tmp146, tmp149
	mul16s	a5, a5, a4	# tmp150, tmp148, x2
	l32r	a3, .LC13	#, tmp155
	addmi	a5, a5, 0x4000	# tmp151, tmp150,
	srai	a5, a5, 15	# tmp152, tmp151,
	add.n	a5, a5, a3	# tmp154, tmp152, tmp155
	mul16s	a5, a5, a4	# tmp156, tmp154, x2
	sub	a2, a2, a4	# tmp158, tmp103, x2
	addmi	a5, a5, 0x4000	# tmp157, tmp156,
	srai	a5, a5, 15	# _69, tmp157,
	l32r	a6, .LC14	#, tmp161
	add.n	a3, a2, a5	# tmp160, tmp158, _69
	l32r	a2, .LC7	#, <retval>
	blt	a6, a3, .L72	# tmp161, tmp160,
	sub	a2, a5, a4	# tmp162, _69, x2
	addmi	a2, a2, -0x8000	# tmp166, tmp162,
	neg	a2, a2	# tmp168, tmp166
	slli	a2, a2, 16	# tmp169, tmp168,
	srai	a2, a2, 16	# <retval>, tmp169,
	j	.L72		#
.L73:
# @OPUS@\upstream\celt\mathops.c:171:       if (x&0x0000ffff)
	extui	a2, a2, 0, 16	# tmp170, x,
# @OPUS@\upstream\celt\mathops.c:171:       if (x&0x0000ffff)
	bnez.n	a2, .L78	# tmp170,
# @OPUS@\upstream\celt\mathops.c:174:          return -32767;
	l32r	a2, .LC7	#, tmp172
	l32r	a4, .LC8	#, tmp173
	moveqz	a2, a4, a3	# <retval>, tmp173, x
	j	.L72		#
.L78:
# @OPUS@\upstream\celt\mathops.c:172:          return 0;
	mov.n	a2, a4	# <retval>, tmp102
.L72:
# @OPUS@\upstream\celt\mathops.c:178: }
	ret.n
	.size	celt_cos_norm, .-celt_cos_norm
	.section	.text.celt_rcp,"ax",@progbits
	.literal_position
	.literal .LC16, -15420
	.literal .LC17, 30840
	.align	4
	.global	celt_rcp
	.type	celt_rcp, @function
# Function: celt_rcp
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: a = VSHR32(a,shift);
# C context: b = VSHR32(b,shift);
# C context: /* 16-bit reciprocal */
# C context: rcp = ROUND16(celt_rcp(ROUND16(b,16)),3);
# C context: result = MULT16_32_Q15(rcp, a);
# C context: rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
# C context: result = ADD32(result, SHL32(MULT16_32_Q15(rcp, rem),2));
# C context: if (result >= 536870912)       /*  2^29 */
celt_rcp:
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a3, a2	# _50, x
# @OPUS@\upstream\celt\mathops.c:187:    i = celt_ilog2(x);
	movi.n	a5, 0x1f	# tmp87,
	sub	a5, a5, a3	# i, tmp87, _50
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	addi	a4, a5, -15	# _1, i,
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	blti	a4, 1, .L81	# _1,,
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	ssr	a4	# _1
	sra	a4, a2	# tmp88, x
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	addmi	a4, a4, -0x8000	# tmp90, tmp88,
	slli	a4, a4, 16	# tmp91, tmp90,
	srai	a4, a4, 16	# iftmp$11_37, tmp91,
	j	.L82		#
.L81:
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	movi.n	a4, 0xf	# tmp92,
	sub	a4, a4, a5	# tmp93, tmp92, i
	ssl	a4	# tmp93
	sll	a4, a2	# tmp94, x
# @OPUS@\upstream\celt\mathops.c:189:    n = VSHR32(x,i-15)-32768;
	addmi	a4, a4, -0x8000	# tmp96, tmp94,
	slli	a4, a4, 16	# tmp97, tmp96,
	srai	a4, a4, 16	# iftmp$11_37, tmp97,
.L82:
# @OPUS@\upstream\celt\mathops.c:193:    r = ADD16(30840, MULT16_16_Q15(-15420, n));
	l32r	a6, .LC16	#, tmp99
# @OPUS@\upstream\celt\mathops.c:193:    r = ADD16(30840, MULT16_16_Q15(-15420, n));
	l32r	a3, .LC17	#, tmp103
# @OPUS@\upstream\celt\mathops.c:193:    r = ADD16(30840, MULT16_16_Q15(-15420, n));
	mul16s	a6, a4, a6	# tmp98, iftmp$11_37, tmp99
# @OPUS@\upstream\celt\mathops.c:197:    r = SUB16(r, MULT16_16_Q15(r,
	movi	a7, -0x788	# tmp107,
# @OPUS@\upstream\celt\mathops.c:193:    r = ADD16(30840, MULT16_16_Q15(-15420, n));
	slli	a6, a6, 1	# tmp101, tmp98,
	srai	a6, a6, 16	# _10, tmp101,
# @OPUS@\upstream\celt\mathops.c:193:    r = ADD16(30840, MULT16_16_Q15(-15420, n));
	add.n	a3, a6, a3	# tmp102, _10, tmp103
	slli	a3, a3, 16	# tmp104, tmp102,
	srai	a3, a3, 16	# r, tmp104,
# @OPUS@\upstream\celt\mathops.c:197:    r = SUB16(r, MULT16_16_Q15(r,
	mull	a2, a4, a3	# tmp105, iftmp$11_37, r
	add.n	a6, a6, a7	# tmp108, _10, tmp107
	srai	a2, a2, 15	# tmp106, tmp105,
	add.n	a2, a2, a6	# tmp111, tmp106, tmp108
	mul16s	a2, a2, a3	# tmp112, tmp111, r
# @OPUS@\upstream\celt\mathops.c:206:    return VSHR32(EXTEND32(r),i-16);
	addi	a6, a5, -16	# _32, i,
# @OPUS@\upstream\celt\mathops.c:197:    r = SUB16(r, MULT16_16_Q15(r,
	slli	a2, a2, 1	# tmp114, tmp112,
	srai	a2, a2, 16	# _20, tmp114,
# @OPUS@\upstream\celt\mathops.c:197:    r = SUB16(r, MULT16_16_Q15(r,
	sub	a3, a3, a2	# tmp115, r, _20
	slli	a3, a3, 16	# tmp116, tmp115,
	srai	a3, a3, 16	# r, tmp116,
# @OPUS@\upstream\celt\mathops.c:201:    r = SUB16(r, ADD16(1, MULT16_16_Q15(r,
	mull	a4, a4, a3	# tmp117, iftmp$11_37, r
	addmi	a2, a3, -0x8000	# tmp119, r,
	srai	a4, a4, 15	# tmp118, tmp117,
	add.n	a4, a4, a2	# tmp122, tmp118, tmp119
	mul16s	a4, a4, a3	# tmp123, tmp122, r
	addi.n	a2, a3, -1	# tmp126, r,
	slli	a3, a4, 1	# tmp125, tmp123,
	srai	a3, a3, 16	# _30, tmp125,
# @OPUS@\upstream\celt\mathops.c:201:    r = SUB16(r, ADD16(1, MULT16_16_Q15(r,
	sub	a2, a2, a3	# tmp128, tmp126, _30
	slli	a2, a2, 16	# tmp129, tmp128,
	srai	a2, a2, 16	# r, tmp129,
# @OPUS@\upstream\celt\mathops.c:206:    return VSHR32(EXTEND32(r),i-16);
	blti	a6, 1, .L83	# _32,,
# @OPUS@\upstream\celt\mathops.c:206:    return VSHR32(EXTEND32(r),i-16);
	ssr	a6	# _32
	sra	a2, a2	# <retval>, r
	j	.L80		#
.L83:
# @OPUS@\upstream\celt\mathops.c:206:    return VSHR32(EXTEND32(r),i-16);
	movi.n	a3, 0x10	# tmp130,
	sub	a5, a3, a5	# tmp131, tmp130, i
	ssl	a5	# tmp131
	sll	a2, a2	# <retval>, r
.L80:
# @OPUS@\upstream\celt\mathops.c:207: }
	ret.n
	.size	celt_rcp, .-celt_rcp
	.section	.text.frac_div32,"ax",@progbits
	.literal_position
	.literal .LC18, 2147483647
	.literal .LC19, -2147483647
	.literal .LC20, 32768
	.literal .LC21, 536870911
	.literal .LC22, -536870911
	.align	4
	.global	frac_div32
	.type	frac_div32, @function
# Function: frac_div32
# Module: upstream/celt/mathops.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context:
# C context: #ifdef FIXED_POINT
# C context:
# C context: opus_val32 frac_div32(opus_val32 a, opus_val32 b)
# C context: {
# C context: opus_val16 rcp;
# C context: opus_val32 result, rem;
# C context: int shift = celt_ilog2(b)-29;
frac_div32:
	addi	sp, sp, -16	#,,
	s32i.n	a13, sp, 4	#,
# @OPUS@\upstream\celt\mathops.c:74:    int shift = celt_ilog2(b)-29;
	movi.n	a4, 0x1f	# tmp108,
# @OPUS@\upstream\celt\mathops.h:183:    return EC_ILOG(x)-1;
	nsau	a13, a3	# _63, b
# @OPUS@\upstream\celt\mathops.c:74:    int shift = celt_ilog2(b)-29;
	sub	a4, a4, a13	# _2, tmp108, _63
# @OPUS@\upstream\celt\mathops.c:71: {
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\celt\mathops.c:74:    int shift = celt_ilog2(b)-29;
	addi	a5, a4, -29	# shift, _2,
# @OPUS@\upstream\celt\mathops.c:75:    a = VSHR32(a,shift);
	blti	a5, 1, .L86	# shift,,
# @OPUS@\upstream\celt\mathops.c:75:    a = VSHR32(a,shift);
	ssr	a5	# shift
	sra	a12, a2	# iftmp$0_66, a
# @OPUS@\upstream\celt\mathops.c:76:    b = VSHR32(b,shift);
	ssr	a5	# shift
	sra	a13, a3	# iftmp$2_59, b
	j	.L87		#
.L86:
# @OPUS@\upstream\celt\mathops.c:75:    a = VSHR32(a,shift);
	movi.n	a13, 0x1d	# tmp109,
	sub	a13, a13, a4	# _4, tmp109, _2
	ssl	a13	# _4
	sll	a12, a2	# iftmp$0_66, a
# @OPUS@\upstream\celt\mathops.c:76:    b = VSHR32(b,shift);
	ssl	a13	# _4
	sll	a13, a3	# iftmp$2_59, b
.L87:
# @OPUS@\upstream\celt\mathops.c:78:    rcp = ROUND16(celt_rcp(ROUND16(b,16)),3);
	l32r	a2, .LC20	#, tmp111
	add.n	a2, a13, a2	# tmp110, iftmp$2_59, tmp111
	srai	a2, a2, 16	#, tmp110,
	call0	celt_rcp		#
	addi.n	a5, a2, 4	# tmp113,,
# @OPUS@\upstream\celt\mathops.c:79:    result = MULT16_32_Q15(rcp, a);
	slli	a5, a5, 13	# tmp115, tmp113,
	srai	a5, a5, 16	# _15, tmp115,
	srai	a4, a12, 16	# tmp116, iftmp$0_66,
	extui	a2, a12, 0, 16	# tmp119, iftmp$0_66,
	mull	a4, a4, a5	# tmp117, tmp116, _15
	mull	a2, a2, a5	# tmp120, tmp119, _15
	slli	a4, a4, 1	# tmp118, tmp117,
	srai	a2, a2, 15	# tmp121, tmp120,
# @OPUS@\upstream\celt\mathops.c:79:    result = MULT16_32_Q15(rcp, a);
	add.n	a4, a4, a2	# result, tmp118, tmp121
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	srai	a7, a13, 16	# _30, iftmp$2_59,
	srai	a3, a4, 16	# _27, result,
	extui	a13, a13, 0, 16	# tmp124, iftmp$2_59,
	extui	a6, a4, 0, 16	# tmp127, result,
	mull	a13, a13, a3	# tmp125, tmp124, _27
	mull	a6, a6, a7	# tmp128, tmp127, _30
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	addi.n	a2, a12, 2	# tmp122, iftmp$0_66,
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	mull	a3, a3, a7	# tmp132, _27, _30
	srai	a13, a13, 15	# tmp126, tmp125,
	srai	a12, a6, 15	# tmp129, tmp128,
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	add.n	a12, a13, a12	# tmp130, tmp126, tmp129
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	srai	a2, a2, 2	# tmp123, tmp122,
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	sub	a2, a2, a12	# tmp131, tmp123, tmp130
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	slli	a12, a3, 1	# tmp133, tmp132,
# @OPUS@\upstream\celt\mathops.c:80:    rem = PSHR32(a,2)-MULT32_32_Q31(result, b);
	sub	a12, a2, a12	# rem, tmp131, tmp133
# @OPUS@\upstream\celt\mathops.c:81:    result = ADD32(result, SHL32(MULT16_32_Q15(rcp, rem),2));
	srai	a2, a12, 16	# tmp134, rem,
	extui	a12, a12, 0, 16	# tmp137, rem,
	mull	a2, a2, a5	# tmp135, tmp134, _15
	mull	a12, a12, a5	# tmp138, tmp137, _15
	slli	a2, a2, 1	# tmp136, tmp135,
	srai	a12, a12, 15	# tmp139, tmp138,
	add.n	a12, a2, a12	# tmp140, tmp136, tmp139
	slli	a12, a12, 2	# tmp141, tmp140,
# @OPUS@\upstream\celt\mathops.c:82:    if (result >= 536870912)       /*  2^29 */
	l32r	a3, .LC21	#, tmp142
# @OPUS@\upstream\celt\mathops.c:81:    result = ADD32(result, SHL32(MULT16_32_Q15(rcp, rem),2));
	add.n	a12, a12, a4	# result, tmp141, result
# @OPUS@\upstream\celt\mathops.c:83:       return 2147483647;          /*  2^31 - 1 */
	l32r	a2, .LC18	#, <retval>
# @OPUS@\upstream\celt\mathops.c:82:    if (result >= 536870912)       /*  2^29 */
	blt	a3, a12, .L85	# tmp142, result,
# @OPUS@\upstream\celt\mathops.c:84:    else if (result <= -536870912) /* -2^29 */
	l32r	a2, .LC22	#, tmp143
	blt	a12, a2, .L90	# result, tmp143,
# @OPUS@\upstream\celt\mathops.c:87:       return SHL32(result, 2);
	slli	a2, a12, 2	# <retval>, result,
	j	.L85		#
.L90:
# @OPUS@\upstream\celt\mathops.c:85:       return -2147483647;         /* -2^31 */
	l32r	a2, .LC19	#, <retval>
.L85:
# @OPUS@\upstream\celt\mathops.c:88: }
	l32i.n	a0, sp, 12	#,
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	frac_div32, .-frac_div32
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
