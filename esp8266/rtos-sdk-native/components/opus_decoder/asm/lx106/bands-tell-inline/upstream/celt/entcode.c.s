# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/entcode.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"entcode.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\entcode.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\entcode.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\entcode.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\entcode.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\entcode.c.s.raw
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
	.section	.text.ec_tell_frac,"ax",@progbits
	.literal_position
	.literal .LC0, correction$2307
	.align	4
	.global	ec_tell_frac
	.type	ec_tell_frac, @function
# Function: ec_tell_frac
# Module: upstream/celt/entcode.c
# Entropy bit accounting and integer arithmetic shared by decoder modules.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: #endif
# C context:
# C context: #if 1
# C context: /* This is a faster version of ec_tell_frac() that takes advantage
# C context: of the low (1/8 bit) resolution to use just a linear function
# C context: followed by a lookup to determine the exact transition thresholds. */
# C context: opus_uint32 ec_tell_frac(ec_ctx *_this){
# C context: static const unsigned correction[8] =
ec_tell_frac:
# @OPUS@\upstream\celt\entcode.c:78:   l=EC_ILOG(_this->rng);
	l32i.n	a5, a2, 28	# _this_14(D)->rng, _3
# @OPUS@\upstream\celt\entcode.c:79:   r=_this->rng>>(l-16);
	movi.n	a4, 0x10	# tmp61,
# @OPUS@\upstream\celt\entcode.c:78:   l=EC_ILOG(_this->rng);
	nsau	a3, a5	# _4, _3
# @OPUS@\upstream\celt\entcode.c:79:   r=_this->rng>>(l-16);
	sub	a4, a4, a3	# tmp62, tmp61, _4
# @OPUS@\upstream\celt\entcode.c:77:   nbits=_this->nbits_total<<BITRES;
	l32i.n	a2, a2, 20	# _this_14(D)->nbits_total, _this_14(D)->nbits_total
# @OPUS@\upstream\celt\entcode.c:79:   r=_this->rng>>(l-16);
	ssr	a4	# tmp62
	srl	a4, a5	# r, _3
# @OPUS@\upstream\celt\entcode.c:80:   b = (r>>12)-8;
	srli	a5, a4, 12	# tmp63, r,
# @OPUS@\upstream\celt\entcode.c:80:   b = (r>>12)-8;
	addi	a5, a5, -8	# b, tmp63,
# @OPUS@\upstream\celt\entcode.c:78:   l=EC_ILOG(_this->rng);
	add.n	a3, a3, a2	# l, _4, _this_14(D)->nbits_total
# @OPUS@\upstream\celt\entcode.c:81:   b += r>correction[b];
	l32r	a2, .LC0	#, tmp72
	slli	a6, a5, 2	# tmp73, b,
	add.n	a2, a2, a6	# tmp74, tmp72, tmp73
# @OPUS@\upstream\celt\entcode.c:82:   l = (l<<3)+b;
	addi	a3, a3, -32	# tmp69, l,
# @OPUS@\upstream\celt\entcode.c:81:   b += r>correction[b];
	l32i.n	a6, a2, 0	# correction, tmp78
# @OPUS@\upstream\celt\entcode.c:83:   return nbits-l;
	slli	a3, a3, 3	# tmp70, tmp69,
	sub	a3, a3, a5	# tmp71, tmp70, b
# @OPUS@\upstream\celt\entcode.c:81:   b += r>correction[b];
	movi.n	a2, 1	# tmp75,
	bltu	a6, a4, .L2	# tmp78, r,
	movi.n	a2, 0	# tmp75,
.L2:
# @OPUS@\upstream\celt\entcode.c:84: }
	sub	a2, a3, a2	#, tmp71, tmp75
	ret.n
	.size	ec_tell_frac, .-ec_tell_frac
	.section	.rodata.correction$2307,"a"
	.align	4
	.type	correction$2307, @object
	.size	correction$2307, 32
correction$2307:
	.word	35733
	.word	38967
	.word	42495
	.word	46340
	.word	50535
	.word	55109
	.word	60097
	.word	65535
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"

# Address-only alias; the original 32-byte table is not duplicated.
	.global y_opus_tell_correction
	.set y_opus_tell_correction, correction$2307
