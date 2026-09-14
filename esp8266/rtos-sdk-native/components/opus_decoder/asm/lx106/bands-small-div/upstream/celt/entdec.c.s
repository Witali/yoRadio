# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/entdec.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"entdec.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\entdec.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\entdec.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\entdec.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\entdec.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\entdec.c.s.raw
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
	.section	.text.ec_dec_init,"ax",@progbits
	.literal_position
	.literal .LC0, 32768
	.literal .LC1, 8388608
	.literal .LC2, -2147483648
	.align	4
	.global	ec_dec_init
	.type	ec_dec_init, @function
# Function: ec_dec_init
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void ec_dec_init(ec_dec *_this,unsigned char *_buf,opus_uint32 _storage){
# C context: _this->buf=_buf;
# C context: _this->storage=_storage;
# C context: _this->end_offs=0;
# C context: _this->end_window=0;
ec_dec_init:
# @OPUS@\upstream\celt\entdec.c:131:   _this->nbits_total=EC_CODE_BITS+1
	movi.n	a5, 9	# tmp94,
# @OPUS@\upstream\celt\entdec.c:125:   _this->end_offs=0;
	movi.n	a7, 0	# tmp91,
# @OPUS@\upstream\celt\entdec.c:131:   _this->nbits_total=EC_CODE_BITS+1
	s32i.n	a5, a2, 20	# _this_5(D)->nbits_total, tmp94
# @OPUS@\upstream\celt\entdec.c:134:   _this->rng=1U<<EC_CODE_EXTRA;
	movi	a5, 0x80	# tmp96,
# @OPUS@\upstream\celt\entdec.c:123:   _this->buf=_buf;
	s32i.n	a3, a2, 0	# _this_5(D)->buf, _buf
# @OPUS@\upstream\celt\entdec.c:124:   _this->storage=_storage;
	s32i.n	a4, a2, 4	# _this_5(D)->storage, _storage
# @OPUS@\upstream\celt\entdec.c:125:   _this->end_offs=0;
	s32i.n	a7, a2, 8	# _this_5(D)->end_offs, tmp91
# @OPUS@\upstream\celt\entdec.c:126:   _this->end_window=0;
	s32i.n	a7, a2, 12	# _this_5(D)->end_window, tmp91
# @OPUS@\upstream\celt\entdec.c:127:   _this->nend_bits=0;
	s32i.n	a7, a2, 16	# _this_5(D)->nend_bits, tmp91
# @OPUS@\upstream\celt\entdec.c:133:   _this->offs=0;
	s32i.n	a7, a2, 24	# _this_5(D)->offs, tmp91
# @OPUS@\upstream\celt\entdec.c:134:   _this->rng=1U<<EC_CODE_EXTRA;
	s32i.n	a5, a2, 28	# _this_5(D)->rng, tmp96
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	beq	a4, a7, .L2	# _storage,,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	movi.n	a8, 1	# tmp97,
	s32i.n	a8, a2, 24	# _this_5(D)->offs, tmp97
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a6, a3, 0	# *_buf_6(D), iftmp$0_21
	movi	a9, 0x7f	# tmp99,
	ssr	a8	#
	sra	a5, a6	# tmp98, iftmp$0_21
	sub	a9, a9, a5	# prephitmp_25, tmp99, tmp98
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	movi.n	a5, 0x11	# tmp101,
	s32i.n	a5, a2, 20	# _this_5(D)->nbits_total, tmp101
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	l32r	a5, .LC0	#, tmp102
# @OPUS@\upstream\celt\entdec.c:135:   _this->rem=ec_read_byte(_this);
	s32i.n	a6, a2, 40	# _this_5(D)->rem, iftmp$0_21
# @OPUS@\upstream\celt\entdec.c:136:   _this->val=_this->rng-1-(_this->rem>>(EC_SYM_BITS-EC_CODE_EXTRA));
	s32i.n	a9, a2, 32	# _this_5(D)->val, prephitmp_25
# @OPUS@\upstream\celt\entdec.c:137:   _this->error=0;
	s32i.n	a7, a2, 44	# _this_5(D)->error, tmp91
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a5, a2, 28	# _this_5(D)->rng, tmp102
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bltui	a4, 2, .L3	# _storage,,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	movi.n	a8, 2	# tmp103,
	s32i.n	a8, a2, 24	# _this_5(D)->offs, tmp103
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a7, a3, 1	# MEM[(unsigned char *)_buf_6(D) + 1B], iftmp$0_31
.L3:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a5, a6, 8	# tmp104, iftmp$0_21,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a5, a5, a7	# tmp105, tmp104, iftmp$0_31
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a5, a5, 1	# sym, tmp105,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a6, -1	# tmp108,
	xor	a5, a6, a5	# tmp107, tmp108, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a9, a9, 8	# tmp110, prephitmp_25,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a5, a5, 0, 8	# tmp109, tmp107,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a5, a9	# _70, tmp109, tmp110
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	movi.n	a9, 0x19	# tmp111,
	s32i.n	a9, a2, 20	# _this_5(D)->nbits_total, tmp111
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	l32r	a9, .LC1	#, tmp112
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a7, a2, 40	# _this_5(D)->rem, iftmp$0_31
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_5(D)->val, _70
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a9, a2, 28	# _this_5(D)->rng, tmp112
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a8, a4, .L4	# prephitmp_19, _storage,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a10, a8, 1	# _99, prephitmp_19,
	s32i.n	a10, a2, 24	# _this_5(D)->offs, _99
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a9, a3, a8	# tmp113, _buf, prephitmp_19
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a9, a9, 0	# *_101, iftmp$0_103
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a7, a7, 8	# tmp114, iftmp$0_31,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a7, a7, a9	# tmp115, tmp114, iftmp$0_103
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a7, a7, 1	# sym, tmp115,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a6, a6, a7	# tmp117, tmp108, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a6, a6, 0, 8	# tmp119, tmp117,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a5, a5, 8	# tmp120, _70,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a6, a5	# _115, tmp119, tmp120
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	movi.n	a6, 0x21	# tmp121,
	s32i.n	a6, a2, 20	# _this_5(D)->nbits_total, tmp121
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	l32r	a6, .LC2	#, tmp122
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a9, a2, 40	# _this_5(D)->rem, iftmp$0_103
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_5(D)->val, _115
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a6, a2, 28	# _this_5(D)->rng, tmp122
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bltu	a10, a4, .L5	# _99, _storage,
.L7:
	movi.n	a7, 0	# iftmp$0_36,
	j	.L6		#
.L5:
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a8, a8, 2	# tmp123, prephitmp_19,
	s32i.n	a8, a2, 24	# _this_5(D)->offs, tmp123
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a3, a3, a10	# tmp124, _buf, _99
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a7, a3, 0	# *_34, iftmp$0_36
.L6:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a3, a9, 8	# tmp125, iftmp$0_103,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a3, a3, a7	# tmp126, tmp125, iftmp$0_36
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a4, a3, 1	# sym, tmp126,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a3, -1	# tmp129,
	xor	a3, a3, a4	# tmp128, tmp129, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a3, a3, 0, 8	# tmp130, tmp128,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a5, a5, 8	# tmp131, _115,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a3, a5	# tmp132, tmp130, tmp131
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a7, a2, 40	# _this_5(D)->rem, iftmp$0_36
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_5(D)->val, tmp132
# @OPUS@\upstream\celt\entdec.c:140: }
	ret.n
.L2:
# @OPUS@\upstream\celt\entdec.c:137:   _this->error=0;
	s32i.n	a4, a2, 44	# _this_5(D)->error, _storage
	mov.n	a8, a4	# prephitmp_19, _storage
	movi	a9, 0x7f	# prephitmp_25,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a6, a4	# iftmp$0_21, _storage
	mov.n	a7, a4	# iftmp$0_31, _storage
	j	.L3		#
.L4:
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	movi.n	a3, 0x21	# tmp140,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a7, a7, 7	# sym, iftmp$0_31,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a7, a6, a7	# tmp136, tmp108, sym
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a3, a2, 20	# _this_5(D)->nbits_total, tmp140
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	l32r	a3, .LC2	#, tmp141
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a7, a7, 0, 8	# tmp138, tmp136,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a5, a5, 8	# tmp139, _70,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a7, a5	# _115, tmp138, tmp139
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a3, a2, 28	# _this_5(D)->rng, tmp141
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	movi.n	a9, 0	# iftmp$0_103,
	j	.L7		#
	.size	ec_dec_init, .-ec_dec_init
	.global	__udivsi3
	.section	.text.ec_decode,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_decode
	.type	ec_decode, @function
# Function: ec_decode
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_dec_normalize(_this);
# C context: }
# C context:
# C context: unsigned ec_decode(ec_dec *_this,unsigned _ft){
# C context: unsigned s;
# C context: _this->ext=celt_udiv(_this->rng,_ft);
# C context: s=(unsigned)(_this->val/_this->ext);
# C context: return _ft-EC_MINI(s+1,_ft);
ec_decode:
	addi	sp, sp, -16	#,,
	s32i.n	a13, sp, 4	#,
	mov.n	a13, a2	# _this, _this
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	l32i.n	a2, a2, 28	# _this_14(D)->rng,
# @OPUS@\upstream\celt\entdec.c:142: unsigned ec_decode(ec_dec *_this,unsigned _ft){
	s32i.n	a0, sp, 12	#,
	s32i.n	a12, sp, 8	#,
# @OPUS@\upstream\celt\entdec.c:142: unsigned ec_decode(ec_dec *_this,unsigned _ft){
	mov.n	a12, a3	# _ft, _ft
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	call0	yoradio_opus_small_udiv		#
	mov.n	a3, a2	# tmp58,
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	l32i.n	a2, a13, 32	# _this_14(D)->val,
# @OPUS@\upstream\celt\entdec.c:144:   _this->ext=celt_udiv(_this->rng,_ft);
	s32i.n	a3, a13, 36	# _this_14(D)->ext, tmp58
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	call0	__udivsi3		#
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	addi.n	a4, a2, 1	# tmp63, s,
	movi.n	a3, 1	# tmp64,
	bltu	a12, a4, .L12	# _ft, tmp63,
	movi.n	a3, 0	# tmp64,
.L12:
	addi.n	a12, a12, -1	# tmp67, _ft,
# @OPUS@\upstream\celt\entdec.c:147: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	sub	a2, a12, a2	# tmp68, tmp67, s
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	addi.n	a3, a3, -1	# tmp66, tmp64,
# @OPUS@\upstream\celt\entdec.c:147: }
	and	a2, a3, a2	#, tmp66, tmp68
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_decode, .-ec_decode
	.section	.text.ec_decode_bin,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_decode_bin
	.type	ec_decode_bin, @function
# Function: ec_decode_bin
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return _ft-EC_MINI(s+1,_ft);
# C context: }
# C context:
# C context: unsigned ec_decode_bin(ec_dec *_this,unsigned _bits){
# C context: unsigned s;
# C context: _this->ext=_this->rng>>_bits;
# C context: s=(unsigned)(_this->val/_this->ext);
# C context: return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
ec_decode_bin:
	mov.n	a4, a2	# _this, _this
# @OPUS@\upstream\celt\entdec.c:151:    _this->ext=_this->rng>>_bits;
	l32i.n	a2, a2, 28	# _this_16(D)->rng, _this_16(D)->rng
# @OPUS@\upstream\celt\entdec.c:149: unsigned ec_decode_bin(ec_dec *_this,unsigned _bits){
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 8	#,
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\entdec.c:149: unsigned ec_decode_bin(ec_dec *_this,unsigned _bits){
	mov.n	a12, a3	# _bits, _bits
# @OPUS@\upstream\celt\entdec.c:151:    _this->ext=_this->rng>>_bits;
	ssr	a3	# _bits
	srl	a3, a2	# _2, _this_16(D)->rng
# @OPUS@\upstream\celt\entdec.c:152:    s=(unsigned)(_this->val/_this->ext);
	l32i.n	a2, a4, 32	# _this_16(D)->val,
# @OPUS@\upstream\celt\entdec.c:151:    _this->ext=_this->rng>>_bits;
	s32i.n	a3, a4, 36	# _this_16(D)->ext, _2
# @OPUS@\upstream\celt\entdec.c:152:    s=(unsigned)(_this->val/_this->ext);
	call0	__udivsi3		#
# @OPUS@\upstream\celt\entdec.c:153:    return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
	movi.n	a3, 1	# tmp61,
	ssl	a12	# _bits
	sll	a12, a3	# _4, tmp61
# @OPUS@\upstream\celt\entdec.c:153:    return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
	add.n	a4, a2, a3	# tmp63, s,
	bltu	a12, a4, .L14	# _4, tmp63,
	movi.n	a3, 0	# tmp64,
.L14:
	addi.n	a12, a12, -1	# tmp67, _4,
# @OPUS@\upstream\celt\entdec.c:154: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\entdec.c:153:    return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
	sub	a2, a12, a2	# tmp68, tmp67, s
# @OPUS@\upstream\celt\entdec.c:153:    return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
	addi.n	a3, a3, -1	# tmp66, tmp64,
# @OPUS@\upstream\celt\entdec.c:154: }
	and	a2, a3, a2	#, tmp66, tmp68
	l32i.n	a12, sp, 8	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_decode_bin, .-ec_decode_bin
	.section	.text.ec_dec_update,"ax",@progbits
	.literal_position
	.literal .LC3, 8388608
	.literal .LC4, 2147483647
	.align	4
	.global	ec_dec_update
	.type	ec_dec_update, @function
# Function: ec_dec_update
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return (1U<<_bits)-EC_MINI(s+1U,1U<<_bits);
# C context: }
# C context:
# C context: void ec_dec_update(ec_dec *_this,unsigned _fl,unsigned _fh,unsigned _ft){
# C context: opus_uint32 s;
# C context: s=IMUL32(_this->ext,_ft-_fh);
# C context: _this->val-=s;
# C context: _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
ec_dec_update:
# @OPUS@\upstream\celt\entdec.c:158:   s=IMUL32(_this->ext,_ft-_fh);
	l32i.n	a6, a2, 36	# _this_9(D)->ext, _1
	sub	a5, a5, a4	# tmp81, _ft, _fh
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	l32i.n	a7, a2, 32	# _this_9(D)->val, _this_9(D)->val
# @OPUS@\upstream\celt\entdec.c:158:   s=IMUL32(_this->ext,_ft-_fh);
	mull	a5, a5, a6	# s, tmp81, _1
# @OPUS@\upstream\celt\entdec.c:156: void ec_dec_update(ec_dec *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	sub	a7, a7, a5	# _43, _this_9(D)->val, s
# @OPUS@\upstream\celt\entdec.c:156: void ec_dec_update(ec_dec *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
	s32i.n	a15, sp, 0	#,
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	s32i.n	a7, a2, 32	# _this_9(D)->val, _43
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	beqz.n	a3, .L16	# _fl,
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	sub	a3, a4, a3	# tmp83, _fh, _fl
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	mull	a3, a3, a6	# _22, tmp83, _1
	j	.L17		#
.L16:
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	l32i.n	a3, a2, 28	# _this_9(D)->rng, _this_9(D)->rng
	sub	a3, a3, a5	# _22, _this_9(D)->rng, s
.L17:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a9, .LC3	#, tmp108
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	s32i.n	a3, a2, 28	# _this_9(D)->rng, _22
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a9, a3, .L15	# tmp108, _22,
	l32i.n	a5, a2, 20	# _this_9(D)->nbits_total, _this_9(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a14, a2, 4	# _this_9(D)->storage, _25
	l32i.n	a6, a2, 40	# _this_9(D)->rem, pretmp_65
	l32i.n	a8, a2, 24	# _this_9(D)->offs, prephitmp_18
	l32r	a13, .LC4	#, tmp109
	addi.n	a5, a5, 8	# ivtmp$12, _this_9(D)->nbits_total,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a12, 0	# tmp110,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a11, -1	# tmp111,
.L22:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a4, a6, 8	# tmp88, pretmp_65,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a6, a4, 1	# sym, tmp99,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a6, a11, a6	# tmp101, tmp111, sym
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a3, a3, 8	# _22, _22,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a15, a7, 8	# tmp94, _43,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a6, a6, 0, 8	# tmp103, tmp101,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a5, a2, 20	# _this_9(D)->nbits_total, ivtmp$12
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a3, a2, 28	# _this_9(D)->rng, _22
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a10, a8, 1	# _27, prephitmp_18,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a7, a6, a15	# tmp105, tmp103, tmp104
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a8, a14, .L19	# prephitmp_18, _25,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a6, a2, 0	# _this_9(D)->buf, _26
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a10, a2, 24	# _this_9(D)->offs, _27
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a8, a6, a8	# tmp87, _26, prephitmp_18
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a6, a8, 0	# *_28, iftmp$0_30
	addi.n	a5, a5, 8	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a7, a4, a6	# tmp89, tmp88, iftmp$0_30
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a7, a7, 1	# sym, tmp89,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a7, a11, a7	# tmp91, tmp111, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a7, a7, 0, 8	# tmp93, tmp91,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a7, a7, a15	# tmp95, tmp93, tmp94
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a7, a7, a13	# _43, tmp95, tmp109
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a6, a2, 40	# _this_9(D)->rem, iftmp$0_30
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a7, a2, 32	# _this_9(D)->val, _43
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a9, a3, .L23	# tmp108, _22,
	j	.L15		#
.L19:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a7, a7, a13	# _43, tmp105, tmp109
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a12, a2, 40	# _this_9(D)->rem, tmp110
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a7, a2, 32	# _this_9(D)->val, _43
	addi.n	a5, a5, 8	# ivtmp$12, ivtmp$12,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a9, a3, .L15	# tmp108, _22,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a6, a12	# iftmp$0_30, tmp110
	j	.L22		#
.L23:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a8, a10	# prephitmp_18, _27
	j	.L22		#
.L15:
# @OPUS@\upstream\celt\entdec.c:162: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	l32i.n	a15, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_dec_update, .-ec_dec_update
	.section	.text.ec_dec_bit_logp,"ax",@progbits
	.literal_position
	.literal .LC5, 8388608
	.literal .LC6, 2147483647
	.align	4
	.global	ec_dec_bit_logp
	.type	ec_dec_bit_logp, @function
# Function: ec_dec_bit_logp
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /*The probability of having a "one" is 1/(1<<_logp).*/
# C context: int ec_dec_bit_logp(ec_dec *_this,unsigned _logp){
# C context: opus_uint32 r;
# C context: opus_uint32 d;
# C context: opus_uint32 s;
# C context: int         ret;
ec_dec_bit_logp:
# @OPUS@\upstream\celt\entdec.c:170:   r=_this->rng;
	l32i.n	a5, a2, 28	# _this_6(D)->rng, r
# @OPUS@\upstream\celt\entdec.c:165: int ec_dec_bit_logp(ec_dec *_this,unsigned _logp){
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entdec.c:171:   d=_this->val;
	l32i.n	a4, a2, 32	# _this_6(D)->val, d
# @OPUS@\upstream\celt\entdec.c:165: int ec_dec_bit_logp(ec_dec *_this,unsigned _logp){
	s32i.n	a13, sp, 8	#,
	s32i.n	a12, sp, 12	#,
	s32i.n	a14, sp, 4	#,
	s32i.n	a15, sp, 0	#,
# @OPUS@\upstream\celt\entdec.c:172:   s=r>>_logp;
	ssr	a3	# _logp
	srl	a3, a5	# s, r
# @OPUS@\upstream\celt\entdec.c:173:   ret=d<s;
	movi.n	a13, 1	# tmp76,
	bltu	a4, a3, .L25	# d, s,
	movi.n	a13, 0	# tmp76,
.L25:
# @OPUS@\upstream\celt\entdec.c:174:   if(!ret)_this->val=d-s;
	bltu	a4, a3, .L26	# d, s,
# @OPUS@\upstream\celt\entdec.c:174:   if(!ret)_this->val=d-s;
	sub	a4, a4, a3	# d, d, s
# @OPUS@\upstream\celt\entdec.c:174:   if(!ret)_this->val=d-s;
	s32i.n	a4, a2, 32	# _this_6(D)->val, d
# @OPUS@\upstream\celt\entdec.c:175:   _this->rng=ret?s:r-s;
	sub	a3, a5, a3	# s, r, s
.L26:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a9, .LC5	#, tmp102
# @OPUS@\upstream\celt\entdec.c:175:   _this->rng=ret?s:r-s;
	s32i.n	a3, a2, 28	# _this_6(D)->rng, s
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a9, a3, .L24	# tmp102, s,
	l32i.n	a8, a2, 20	# _this_6(D)->nbits_total, _this_6(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a15, a2, 4	# _this_6(D)->storage, _22
	l32i.n	a5, a2, 40	# _this_6(D)->rem, pretmp_64
	l32i.n	a7, a2, 24	# _this_6(D)->offs, prephitmp_46
	addi.n	a8, a8, 8	# ivtmp$17, _this_6(D)->nbits_total,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a12, 0	# tmp121,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a11, -1	# tmp122,
.L31:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a14, a5, 8	# tmp82, pretmp_64,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a5, a14, 1	# sym, tmp93,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a5, a11, a5	# tmp95, tmp122, sym
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a3, a3, 8	# s, s,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a10, a4, 8	# tmp88, d,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a5, a5, 0, 8	# tmp97, tmp95,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a8, a2, 20	# _this_6(D)->nbits_total, ivtmp$17
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a3, a2, 28	# _this_6(D)->rng, s
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a6, a7, 1	# _24, prephitmp_46,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a4, a5, a10	# tmp99, tmp97, tmp98
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a7, a15, .L28	# prephitmp_46, _22,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a4, a2, 0	# _this_6(D)->buf, _23
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a6, a2, 24	# _this_6(D)->offs, _24
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a7, a4, a7	# tmp81, _23, prephitmp_46
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a5, a7, 0	# *_25, iftmp$0_27
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	l32r	a7, .LC6	#,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a4, a14, a5	# tmp83, tmp82, iftmp$0_27
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a4, a4, 1	# sym, tmp83,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a4, a11, a4	# tmp85, tmp122, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a4, a4, 0, 8	# tmp87, tmp85,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a4, a4, a10	# tmp89, tmp87, tmp88
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a4, a4, a7	# d, tmp89,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a5, a2, 40	# _this_6(D)->rem, iftmp$0_27
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a4, a2, 32	# _this_6(D)->val, d
	addi.n	a8, a8, 8	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a9, a3, .L32	# tmp102, s,
	j	.L24		#
.L28:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	l32r	a5, .LC6	#,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a12, a2, 40	# _this_6(D)->rem, tmp121
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a4, a4, a5	# d, tmp99,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a4, a2, 32	# _this_6(D)->val, d
	addi.n	a8, a8, 8	# ivtmp$17, ivtmp$17,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a9, a3, .L24	# tmp102, s,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a5, a12	# iftmp$0_27, tmp121
	j	.L31		#
.L32:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a7, a6	# prephitmp_46, _24
	j	.L31		#
.L24:
# @OPUS@\upstream\celt\entdec.c:178: }
	mov.n	a2, a13	#, tmp76
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	l32i.n	a15, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_dec_bit_logp, .-ec_dec_bit_logp
	.section	.text.ec_dec_icdf,"ax",@progbits
	.literal_position
	.literal .LC7, -1075838976
	.literal .LC8, 1048575
	.literal .LC9, 8388608
	.literal .LC10, 2147483647
	.align	4
	.global	ec_dec_icdf
	.type	ec_dec_icdf, @function
# Function: ec_dec_icdf
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return ret;
# C context: }
# C context:
# C context: int ec_dec_icdf(ec_dec *_this,const unsigned char *_icdf,unsigned _ftb){
# C context: opus_uint32 r;
# C context: opus_uint32 d;
# C context: opus_uint32 s;
# C context: opus_uint32 t;
ec_dec_icdf:
# @OPUS@\upstream\celt\entdec.c:193:   if((uintptr_t)_icdf>=YORADIO_OPUS_FLASH_BEGIN &&
	l32r	a6, .LC7	#, tmp95
# @OPUS@\upstream\celt\entdec.c:180: int ec_dec_icdf(ec_dec *_this,const unsigned char *_icdf,unsigned _ftb){
	addi	sp, sp, -32	#,,
# @OPUS@\upstream\celt\entdec.c:186:   s=_this->rng;
	l32i.n	a9, a2, 28	# _this_21(D)->rng, t
# @OPUS@\upstream\celt\entdec.c:193:   if((uintptr_t)_icdf>=YORADIO_OPUS_FLASH_BEGIN &&
	l32r	a7, .LC8	#, tmp96
# @OPUS@\upstream\celt\entdec.c:180: int ec_dec_icdf(ec_dec *_this,const unsigned char *_icdf,unsigned _ftb){
	s32i.n	a12, sp, 28	#,
	s32i.n	a13, sp, 24	#,
	s32i.n	a14, sp, 20	#,
	s32i.n	a15, sp, 16	#,
# @OPUS@\upstream\celt\entdec.c:193:   if((uintptr_t)_icdf>=YORADIO_OPUS_FLASH_BEGIN &&
	add.n	a6, a3, a6	# tmp94, _icdf, tmp95
# @OPUS@\upstream\celt\entdec.c:187:   d=_this->val;
	l32i.n	a5, a2, 32	# _this_21(D)->val, d
# @OPUS@\upstream\celt\entdec.c:188:   r=s>>_ftb;
	ssr	a4	# _ftb
	srl	a4, a9	# r, t
# @OPUS@\upstream\celt\entdec.c:189:   ret=-1;
	movi.n	a8, -1	# <retval>,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:125:     const void *aligned = (const void *)(address & ~(uintptr_t)3U);
	movi.n	a10, -4	# tmp98,
# @OPUS@\upstream\celt\entdec.c:193:   if((uintptr_t)_icdf>=YORADIO_OPUS_FLASH_BEGIN &&
	bgeu	a7, a6, .L36	# tmp96, tmp94,
	j	.L35		#
.L44:
	mov.n	a9, a6	# t, s
.L36:
# @OPUS@\upstream\celt\entdec.c:200:       s=IMUL32(r,yoradio_opus_icdf_flash_read8(_icdf+(++ret)));
	addi.n	a8, a8, 1	# <retval>, <retval>,
	add.n	a7, a3, a8	# _120, _icdf, <retval>
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:125:     const void *aligned = (const void *)(address & ~(uintptr_t)3U);
	and	a6, a7, a10	# aligned, _120, tmp98
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:70:     __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
#APP
# 70 "c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h" 1
	l32i a6, a6, 0	# value, aligned
# 0 "" 2
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:140:     return (unsigned char)(value >> ((address & 3U) * 8U));
#NO_APP
	extui	a7, a7, 0, 2	# tmp100, _120,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:140:     return (unsigned char)(value >> ((address & 3U) * 8U));
	slli	a7, a7, 3	# tmp101, tmp100,
# c:\work\yoradio\.worktree\esp8266-opus-asm\esp8266\rtos-sdk-native\components\opus_decoder\opus_memory.h:140:     return (unsigned char)(value >> ((address & 3U) * 8U));
	ssr	a7	# tmp101
	srl	a6, a6	# tmp102, value
# @OPUS@\upstream\celt\entdec.c:200:       s=IMUL32(r,yoradio_opus_icdf_flash_read8(_icdf+(++ret)));
	extui	a6, a6, 0, 8	# tmp103, tmp102,
	mull	a6, a6, a4	# s, tmp103, r
# @OPUS@\upstream\celt\entdec.c:202:     while(d<s);
	bltu	a5, a6, .L44	# d, s,
	j	.L37		#
.L45:
	mov.n	a9, a6	# t, s
.L35:
# @OPUS@\upstream\celt\entdec.c:212:       s=IMUL32(r,_icdf[++ret]);
	addi.n	a8, a8, 1	# <retval>, <retval>,
# @OPUS@\upstream\celt\entdec.c:212:       s=IMUL32(r,_icdf[++ret]);
	add.n	a6, a3, a8	# tmp104, _icdf, <retval>
	l8ui	a6, a6, 0	# MEM[base: _118, offset: 0B], MEM[base: _118, offset: 0B]
# @OPUS@\upstream\celt\entdec.c:212:       s=IMUL32(r,_icdf[++ret]);
	mull	a6, a6, a4	# s, MEM[base: _118, offset: 0B], r
# @OPUS@\upstream\celt\entdec.c:214:     while(d<s);
	bltu	a5, a6, .L45	# d, s,
.L37:
# @OPUS@\upstream\celt\entdec.c:216:   _this->val=d-s;
	sub	a5, a5, a6	# _99, d, s
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a11, .LC9	#, tmp131
# @OPUS@\upstream\celt\entdec.c:217:   _this->rng=t-s;
	sub	a6, a9, a6	# _46, t, s
# @OPUS@\upstream\celt\entdec.c:216:   _this->val=d-s;
	s32i.n	a5, a2, 32	# _this_21(D)->val, _99
# @OPUS@\upstream\celt\entdec.c:217:   _this->rng=t-s;
	s32i.n	a6, a2, 28	# _this_21(D)->rng, _46
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a11, a6, .L34	# tmp131, _46,
	l32i.n	a9, a2, 20	# _this_21(D)->nbits_total, _this_21(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a4, a2, 4	# _this_21(D)->storage, _49
	l32i.n	a3, a2, 40	# _this_21(D)->rem, pretmp_125
	l32i.n	a7, a2, 24	# _this_21(D)->offs, prephitmp_96
	l32r	a13, .LC10	#, tmp130
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a8, sp, 0	# %sfp, <retval>
	addi.n	a9, a9, 8	# ivtmp$21, _this_21(D)->nbits_total,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a15, 0	# tmp132,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a12, -1	# tmp133,
	mov.n	a8, a4	# _49, _49
.L42:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a4, a3, 8	# tmp110, pretmp_125,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a3, a4, 1	# sym, tmp121,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a3, a12, a3	# tmp123, tmp133, sym
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a6, a6, 8	# _46, _46,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a14, a5, 8	# tmp116, _99,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a3, a3, 0, 8	# tmp125, tmp123,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a9, a2, 20	# _this_21(D)->nbits_total, ivtmp$21
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a6, a2, 28	# _this_21(D)->rng, _46
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a10, a7, 1	# _51, prephitmp_96,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a3, a14	# tmp127, tmp125, tmp126
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a7, a8, .L39	# prephitmp_96, _49,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a3, a2, 0	# _this_21(D)->buf, _50
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a10, a2, 24	# _this_21(D)->offs, _51
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a7, a3, a7	# tmp109, _50, prephitmp_96
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a3, a7, 0	# *_52, iftmp$0_54
	addi.n	a9, a9, 8	# ivtmp$21, ivtmp$21,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a5, a4, a3	# tmp111, tmp110, iftmp$0_54
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a5, a5, 1	# sym, tmp111,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a5, a12, a5	# tmp113, tmp133, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a5, a5, 0, 8	# tmp115, tmp113,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a5, a5, a14	# tmp117, tmp115, tmp116
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a5, a5, a13	# _99, tmp117, tmp130
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a3, a2, 40	# _this_21(D)->rem, iftmp$0_54
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_21(D)->val, _99
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a11, a6, .L46	# tmp131, _46,
	j	.L47		#
.L39:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a5, a5, a13	# _99, tmp127, tmp130
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a15, a2, 40	# _this_21(D)->rem, tmp132
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_21(D)->val, _99
	addi.n	a9, a9, 8	# ivtmp$21, ivtmp$21,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a11, a6, .L47	# tmp131, _46,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a3, a15	# iftmp$0_54, tmp132
	j	.L42		#
.L46:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a7, a10	# prephitmp_96, _51
	j	.L42		#
.L47:
	l32i.n	a8, sp, 0	# %sfp, <retval>
.L34:
# @OPUS@\upstream\celt\entdec.c:220: }
	mov.n	a2, a8	#, <retval>
	l32i.n	a12, sp, 28	#,
	l32i.n	a13, sp, 24	#,
	l32i.n	a14, sp, 20	#,
	l32i.n	a15, sp, 16	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	ec_dec_icdf, .-ec_dec_icdf
	.section	.text.ec_dec_icdf16,"ax",@progbits
	.literal_position
	.literal .LC11, 8388608
	.literal .LC12, 2147483647
	.align	4
	.global	ec_dec_icdf16
	.type	ec_dec_icdf16, @function
# Function: ec_dec_icdf16
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return ret;
# C context: }
# C context:
# C context: int ec_dec_icdf16(ec_dec *_this,const opus_uint16 *_icdf,unsigned _ftb){
# C context: opus_uint32 r;
# C context: opus_uint32 d;
# C context: opus_uint32 s;
# C context: opus_uint32 t;
ec_dec_icdf16:
# @OPUS@\upstream\celt\entdec.c:228:   s=_this->rng;
	l32i.n	a7, a2, 28	# _this_11(D)->rng, s
# @OPUS@\upstream\celt\entdec.c:222: int ec_dec_icdf16(ec_dec *_this,const opus_uint16 *_icdf,unsigned _ftb){
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
	s32i.n	a15, sp, 0	#,
# @OPUS@\upstream\celt\entdec.c:229:   d=_this->val;
	l32i.n	a8, a2, 32	# _this_11(D)->val, d
# @OPUS@\upstream\celt\entdec.c:230:   r=s>>_ftb;
	ssr	a4	# _ftb
	srl	a4, a7	# r, s
# @OPUS@\upstream\celt\entdec.c:231:   ret=-1;
	movi.n	a9, -1	# <retval>,
	j	.L49		#
.L55:
	mov.n	a7, a5	# s, s
.L49:
# @OPUS@\upstream\celt\entdec.c:234:     s=IMUL32(r,_icdf[++ret]);
	l16ui	a5, a3, 0	# MEM[base: _86, offset: 0B], MEM[base: _86, offset: 0B]
# @OPUS@\upstream\celt\entdec.c:234:     s=IMUL32(r,_icdf[++ret]);
	addi.n	a9, a9, 1	# <retval>, <retval>,
	mull	a5, a5, a4	# s, MEM[base: _86, offset: 0B], r
	addi.n	a3, a3, 2	# ivtmp$36, ivtmp$36,
# @OPUS@\upstream\celt\entdec.c:236:   while(d<s);
	bltu	a8, a5, .L55	# d, s,
# @OPUS@\upstream\celt\entdec.c:237:   _this->val=d-s;
	sub	a4, a8, a5	# _69, d, s
# @OPUS@\upstream\celt\entdec.c:238:   _this->rng=t-s;
	sub	a6, a7, a5	# _24, s, s
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a13, .LC11	#, tmp108
# @OPUS@\upstream\celt\entdec.c:237:   _this->val=d-s;
	s32i.n	a4, a2, 32	# _this_11(D)->val, _69
# @OPUS@\upstream\celt\entdec.c:238:   _this->rng=t-s;
	s32i.n	a6, a2, 28	# _this_11(D)->rng, _24
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a13, a6, .L48	# tmp108, _24,
	l32i.n	a8, a2, 20	# _this_11(D)->nbits_total, _this_11(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a14, a2, 4	# _this_11(D)->storage, _31
	l32i.n	a3, a2, 40	# _this_11(D)->rem, iftmp$0_70
	l32i.n	a7, a2, 24	# _this_11(D)->offs, prephitmp_66
	addi.n	a8, a8, 8	# ivtmp$31, _this_11(D)->nbits_total,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a15, 0	# tmp110,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a11, -1	# tmp111,
.L54:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a5, a3, 8	# tmp88, iftmp$0_70,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a3, a5, 1	# sym, tmp99,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a3, a11, a3	# tmp101, tmp111, sym
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a6, a6, 8	# _24, _24,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a12, a4, 8	# tmp94, _69,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a3, a3, 0, 8	# tmp103, tmp101,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a8, a2, 20	# _this_11(D)->nbits_total, ivtmp$31
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a6, a2, 28	# _this_11(D)->rng, _24
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a10, a7, 1	# _33, prephitmp_66,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a4, a3, a12	# tmp105, tmp103, tmp104
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a7, a14, .L51	# prephitmp_66, _31,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a3, a2, 0	# _this_11(D)->buf, _32
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a10, a2, 24	# _this_11(D)->offs, _33
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a7, a3, a7	# tmp87, _32, prephitmp_66
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a3, a7, 0	# *_34, iftmp$0_36
	addi.n	a8, a8, 8	# ivtmp$31, ivtmp$31,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a4, a5, a3	# tmp89, tmp88, iftmp$0_36
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a4, a4, 1	# sym, tmp89,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a4, a11, a4	# tmp91, tmp111, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a4, a4, 0, 8	# tmp93, tmp91,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	l32r	a5, .LC12	#,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a4, a4, a12	# tmp95, tmp93, tmp94
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a4, a4, a5	# _69, tmp95,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a3, a2, 40	# _this_11(D)->rem, iftmp$0_36
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a4, a2, 32	# _this_11(D)->val, _69
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a13, a6, .L56	# tmp108, _24,
	j	.L48		#
.L51:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	l32r	a3, .LC12	#,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a15, a2, 40	# _this_11(D)->rem, tmp110
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a4, a4, a3	# _69, tmp105,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a4, a2, 32	# _this_11(D)->val, _69
	addi.n	a8, a8, 8	# ivtmp$31, ivtmp$31,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a13, a6, .L48	# tmp108, _24,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a3, a15	# iftmp$0_70, tmp110
	j	.L54		#
.L56:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a7, a10	# prephitmp_66, _33
	j	.L54		#
.L48:
# @OPUS@\upstream\celt\entdec.c:241: }
	mov.n	a2, a9	#, <retval>
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	l32i.n	a15, sp, 0	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_dec_icdf16, .-ec_dec_icdf16
	.section	.text.ec_dec_uint,"ax",@progbits
	.literal_position
	.literal .LC13, 8388608
	.literal .LC14, 2147483647
	.align	4
	.global	ec_dec_uint
	.type	ec_dec_uint, @function
# Function: ec_dec_uint
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: return ret;
# C context: }
# C context:
# C context: opus_uint32 ec_dec_uint(ec_dec *_this,opus_uint32 _ft){
# C context: unsigned ft;
# C context: unsigned s;
# C context: int      ftb;
# C context: /*In order to optimize EC_ILOG(), it is undefined for the value 0.*/
ec_dec_uint:
	addi	sp, sp, -64	#,,
	s32i.n	a15, sp, 44	#,
# @OPUS@\upstream\celt\entdec.c:249:   _ft--;
	addi.n	a15, a3, -1	# _ft, _ft,
# @OPUS@\upstream\celt\entdec.c:243: opus_uint32 ec_dec_uint(ec_dec *_this,opus_uint32 _ft){
	s32i.n	a12, sp, 56	#,
	mov.n	a5, a3	# _ft, _ft
	mov.n	a12, a2	# _this, _this
# @OPUS@\upstream\celt\entdec.c:250:   ftb=EC_ILOG(_ft);
	nsau	a3, a15	# _1, _ft
# @OPUS@\upstream\celt\entdec.c:250:   ftb=EC_ILOG(_ft);
	movi.n	a2, 0x20	# tmp153,
# @OPUS@\upstream\celt\entdec.c:243: opus_uint32 ec_dec_uint(ec_dec *_this,opus_uint32 _ft){
	s32i.n	a14, sp, 48	#,
	s32i.n	a0, sp, 60	#,
	s32i.n	a13, sp, 52	#,
# @OPUS@\upstream\celt\entdec.c:250:   ftb=EC_ILOG(_ft);
	sub	a2, a2, a3	# ftb, tmp153, _1
# @OPUS@\upstream\celt\entdec.c:251:   if(ftb>EC_UINT_BITS){
	movi.n	a6, 8	# tmp155,
	l32i.n	a4, a12, 28	# _this_14(D)->rng, pretmp_211
	l32i.n	a14, a12, 32	# _this_14(D)->val, pretmp_212
	bge	a6, a2, .L59	# tmp155, ftb,
# @OPUS@\upstream\celt\entdec.c:253:     ftb-=EC_UINT_BITS;
	movi.n	a6, 0x18	# tmp156,
	sub	a6, a6, a3	# ftb, tmp156, _1
# @OPUS@\upstream\celt\entdec.c:254:     ft=(unsigned)(_ft>>ftb)+1;
	ssr	a6	# ftb
	srl	a5, a15	# _2, _ft
# @OPUS@\upstream\celt\entdec.c:254:     ft=(unsigned)(_ft>>ftb)+1;
	addi.n	a7, a5, 1	# ft, _2,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a7	#, ft
	mov.n	a2, a4	#, pretmp_211
	s32i.n	a4, sp, 28	#,
	s32i.n	a5, sp, 24	#,
	s32i.n	a6, sp, 16	#,
	s32i.n	a7, sp, 20	#,
	call0	yoradio_opus_small_udiv		#
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	mov.n	a3, a2	#, _21
# @OPUS@\upstream\celt\entdec.c:144:   _this->ext=celt_udiv(_this->rng,_ft);
	s32i.n	a2, a12, 36	# _this_14(D)->ext, _21
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a13, a2	# _21,
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	mov.n	a2, a14	#, pretmp_212
	call0	__udivsi3		#
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	l32i.n	a7, sp, 20	#,
	addi.n	a8, a2, 1	# tmp163, s,
	movi.n	a3, 1	# tmp164,
	l32i.n	a4, sp, 28	#,
	l32i.n	a5, sp, 24	#,
	l32i.n	a6, sp, 16	#,
	bltu	a7, a8, .L60	# ft, tmp163,
	movi.n	a3, 0	# tmp164,
.L60:
	sub	a7, a5, a2	# tmp167, _2, s
	neg	a3, a3	# tmp166, tmp164
	and	a3, a3, a7	# tmp168, tmp166, tmp167
	add.n	a2, a3, a2	# _32, tmp168, s
# @OPUS@\upstream\celt\entdec.c:158:   s=IMUL32(_this->ext,_ft-_fh);
	mull	a3, a13, a2	# s, _21, _32
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	sub	a2, a5, a2	#, _2, _32
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	sub	a4, a4, a3	# tmp260, pretmp_211, s
	moveqz	a13, a4, a2	# _21, tmp260,
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	sub	a3, a14, a3	# _194, pretmp_212, s
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC13	#, tmp241
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	s32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	s32i.n	a3, a12, 32	# _this_14(D)->val, _194
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	s32i.n	a13, a12, 28	# _this_14(D)->rng, _21
	l32i.n	a9, a12, 20	# _this_14(D)->nbits_total, _94
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a7, a13, .L62	# tmp241, _21,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a2, a12, 4	# _this_14(D)->storage,
	l32i.n	a4, a12, 40	# _this_14(D)->rem, pretmp_230
	l32i.n	a5, a12, 24	# _this_14(D)->offs, prephitmp_187
	l32r	a11, .LC14	#, tmp242
	s32i.n	a2, sp, 4	# %sfp,
	addi.n	a8, a9, 8	# ivtmp$42, _94,
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a14, 0	# tmp315,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a2, -1	# tmp316,
	s32i.n	a15, sp, 8	# %sfp, _ft
	s32i.n	a6, sp, 12	# %sfp, ftb
.L65:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a6, a4, 8	# tmp171, pretmp_230,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a4, a6, 1	# sym, tmp182,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a4, a2, a4	# tmp184, tmp316, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a4, a4, 0, 8	# tmp186, tmp184,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a15, a3, 8	# tmp177, _194,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a3, a4, a15	# tmp188, tmp186, tmp187
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a13, a13, 8	# _21, _21,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a4, sp, 4	# %sfp,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a8, a12, 20	# _this_14(D)->nbits_total, ivtmp$42
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a13, a12, 28	# _this_14(D)->rng, _21
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a10, a5, 1	# _101, prephitmp_187,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	mov.n	a9, a8	# _94, ivtmp$42
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a5, a4, .L63	# prephitmp_187,,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a3, a12, 0	# _this_14(D)->buf, _100
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a10, a12, 24	# _this_14(D)->offs, _101
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a5, a3, a5	# tmp170, _100, prephitmp_187
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a4, a5, 0	# *_102, iftmp$0_104
	addi.n	a8, a8, 8	# ivtmp$42, ivtmp$42,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a3, a6, a4	# tmp172, tmp171, iftmp$0_104
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a3, a3, 1	# sym, tmp172,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a3, a2, a3	# tmp174, tmp316, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a3, a3, 0, 8	# tmp176, tmp174,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a3, a3, a15	# tmp178, tmp176, tmp177
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a3, a3, a11	# _194, tmp178, tmp242
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a4, a12, 40	# _this_14(D)->rem, iftmp$0_104
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a3, a12, 32	# _this_14(D)->val, _194
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a13, .L75	# tmp241, _21,
	j	.L78		#
.L63:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a3, a3, a11	# _194, tmp188, tmp242
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a14, a12, 40	# _this_14(D)->rem, tmp315
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a3, a12, 32	# _this_14(D)->val, _194
	addi.n	a8, a8, 8	# ivtmp$42, ivtmp$42,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a7, a13, .L78	# tmp241, _21,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a4, a14	# iftmp$0_104, tmp315
	j	.L65		#
.L75:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a5, a10	# prephitmp_187, _101
	j	.L65		#
.L78:
	l32i.n	a15, sp, 8	# %sfp, _ft
	l32i.n	a6, sp, 12	# %sfp, ftb
.L62:
# @OPUS@\upstream\celt\entdec.c:257:     t=(opus_uint32)s<<ftb|ec_dec_bits(_this,ftb);
	l32i.n	a2, sp, 0	# %sfp,
# @OPUS@\upstream\celt\entdec.c:275:   available=_this->nend_bits;
	l32i.n	a3, a12, 16	# _this_14(D)->nend_bits, available
# @OPUS@\upstream\celt\entdec.c:257:     t=(opus_uint32)s<<ftb|ec_dec_bits(_this,ftb);
	ssl	a6	# ftb
	sll	a8, a2	# _3,
# @OPUS@\upstream\celt\entdec.c:274:   window=_this->end_window;
	l32i.n	a10, a12, 12	# _this_14(D)->end_window, window
# @OPUS@\upstream\celt\entdec.c:276:   if((unsigned)available<_bits){
	bgeu	a3, a6, .L66	# available, ftb,
# @OPUS@\upstream\celt\entdec.c:99:   return _this->end_offs<_this->storage?
	l32i.n	a4, a12, 4	# _this_14(D)->storage, _56
	l32i.n	a5, a12, 8	# _this_14(D)->end_offs, prephitmp_254
# @OPUS@\upstream\celt\entdec.c:281:     while(available<=EC_WINDOW_SIZE-EC_SYM_BITS);
	movi.n	a11, 0x18	# tmp195,
.L68:
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	bgeu	a5, a4, .L67	# prephitmp_254, _56,
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	addi.n	a5, a5, 1	# prephitmp_254, prephitmp_254,
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	l32i.n	a2, a12, 0	# _this_14(D)->buf, _57
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	sub	a7, a4, a5	# tmp191, _56, prephitmp_254
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	s32i.n	a5, a12, 8	# _this_14(D)->end_offs, prephitmp_254
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	add.n	a2, a2, a7	# tmp192, _57, tmp191
	l8ui	a2, a2, 0	# *_60, *_60
	ssl	a3	# available
	sll	a2, a2	# tmp194, *_60
	or	a10, a10, a2	# window, window, tmp194
.L67:
# @OPUS@\upstream\celt\entdec.c:279:       available+=EC_SYM_BITS;
	addi.n	a3, a3, 8	# available, available,
# @OPUS@\upstream\celt\entdec.c:281:     while(available<=EC_WINDOW_SIZE-EC_SYM_BITS);
	bge	a11, a3, .L68	# tmp195, available,
.L66:
# @OPUS@\upstream\celt\entdec.c:283:   ret=(opus_uint32)window&(((opus_uint32)1<<_bits)-1U);
	movi.n	a4, -1	# tmp199,
	ssl	a6	# ftb
	sll	a2, a4	# tmp200, tmp199
	xor	a2, a4, a2	# tmp201, tmp199, tmp200
# @OPUS@\upstream\celt\entdec.c:285:   available-=_bits;
	sub	a3, a3, a6	# available, available, ftb
# @OPUS@\upstream\celt\entdec.c:284:   window>>=_bits;
	ssr	a6	# ftb
	srl	a4, a10	# window, window
# @OPUS@\upstream\celt\entdec.c:283:   ret=(opus_uint32)window&(((opus_uint32)1<<_bits)-1U);
	and	a2, a2, a10	# ret, tmp201, window
# @OPUS@\upstream\celt\entdec.c:288:   _this->nbits_total+=_bits;
	add.n	a6, a9, a6	# tmp198, _94, ftb
# @OPUS@\upstream\celt\entdec.c:286:   _this->end_window=window;
	s32i.n	a4, a12, 12	# _this_14(D)->end_window, window
# @OPUS@\upstream\celt\entdec.c:287:   _this->nend_bits=available;
	s32i.n	a3, a12, 16	# _this_14(D)->nend_bits, available
# @OPUS@\upstream\celt\entdec.c:288:   _this->nbits_total+=_bits;
	s32i.n	a6, a12, 20	# _this_14(D)->nbits_total, tmp198
# @OPUS@\upstream\celt\entdec.c:257:     t=(opus_uint32)s<<ftb|ec_dec_bits(_this,ftb);
	or	a2, a2, a8	# <retval>, ret, _3
# @OPUS@\upstream\celt\entdec.c:258:     if(t<=_ft)return t;
	bgeu	a15, a2, .L58	# _ft, <retval>,
# @OPUS@\upstream\celt\entdec.c:259:     _this->error=1;
	movi.n	a2, 1	# tmp204,
	s32i.n	a2, a12, 44	# _this_14(D)->error, tmp204
# @OPUS@\upstream\celt\entdec.c:260:     return _ft;
	mov.n	a2, a15	# <retval>, _ft
	j	.L58		#
.L59:
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a5	#, _ft
	mov.n	a2, a4	#, pretmp_211
	s32i.n	a4, sp, 28	#,
	s32i.n	a5, sp, 24	#,
	call0	yoradio_opus_small_udiv		#
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	mov.n	a3, a2	#, _16
# @OPUS@\upstream\celt\entdec.c:144:   _this->ext=celt_udiv(_this->rng,_ft);
	s32i.n	a2, a12, 36	# _this_14(D)->ext, _16
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a13, a2	# _16,
# @OPUS@\upstream\celt\entdec.c:145:   s=(unsigned)(_this->val/_this->ext);
	mov.n	a2, a14	#, pretmp_212
	call0	__udivsi3		#
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	l32i.n	a5, sp, 24	#,
	addi.n	a6, a2, 1	# tmp211, s,
	movi.n	a3, 1	# tmp212,
	l32i.n	a4, sp, 28	#,
	bltu	a5, a6, .L70	# _ft, tmp211,
	movi.n	a3, 0	# tmp212,
.L70:
	sub	a5, a15, a2	# tmp215, _ft, s
	neg	a3, a3	# tmp214, tmp212
	and	a3, a3, a5	# tmp216, tmp214, tmp215
	add.n	a2, a3, a2	# _47, tmp216, s
# @OPUS@\upstream\celt\entdec.c:158:   s=IMUL32(_this->ext,_ft-_fh);
	mull	a3, a13, a2	# s, _16, _47
# @OPUS@\upstream\celt\entdec.c:146:   return _ft-EC_MINI(s+1,_ft);
	sub	a2, a15, a2	# <retval>, _ft, _47
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	sub	a4, a4, a3	# tmp279, pretmp_211, s
	moveqz	a13, a4, a2	# _16, tmp279, <retval>
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	sub	a3, a14, a3	# _192, pretmp_212, s
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC13	#, tmp241
# @OPUS@\upstream\celt\entdec.c:159:   _this->val-=s;
	s32i.n	a3, a12, 32	# _this_14(D)->val, _192
# @OPUS@\upstream\celt\entdec.c:160:   _this->rng=_fl>0?IMUL32(_this->ext,_fh-_fl):_this->rng-s;
	s32i.n	a13, a12, 28	# _this_14(D)->rng, _16
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a7, a13, .L58	# tmp241, _16,
	l32i.n	a8, a12, 20	# _this_14(D)->nbits_total, _this_14(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a15, a12, 4	# _this_14(D)->storage, _132
	l32i.n	a5, a12, 40	# _this_14(D)->rem, pretmp_215
	l32i.n	a6, a12, 24	# _this_14(D)->offs, prephitmp_189
	l32r	a11, .LC14	#, tmp242
	addi.n	a8, a8, 8	# ivtmp$46, _this_14(D)->nbits_total,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	movi.n	a10, -1	# tmp318,
.L74:
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	slli	a14, a5, 8	# tmp220, pretmp_215,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a5, a14, 1	# sym, tmp231,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a5, a10, a5	# tmp233, tmp318, sym
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	slli	a13, a13, 8	# _16, _16,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	slli	a9, a3, 8	# tmp226, _192,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a5, a5, 0, 8	# tmp235, tmp233,
# @OPUS@\upstream\celt\entdec.c:109:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a8, a12, 20	# _this_14(D)->nbits_total, ivtmp$46
# @OPUS@\upstream\celt\entdec.c:110:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a13, a12, 28	# _this_14(D)->rng, _16
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	addi.n	a4, a6, 1	# _134, prephitmp_189,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a3, a5, a9	# tmp237, tmp235, tmp236
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	bgeu	a6, a15, .L72	# prephitmp_189, _132,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l32i.n	a3, a12, 0	# _this_14(D)->buf, _133
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	s32i.n	a4, a12, 24	# _this_14(D)->offs, _134
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	add.n	a6, a3, a6	# tmp219, _133, prephitmp_189
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	l8ui	a5, a6, 0	# *_135, iftmp$0_137
	addi.n	a8, a8, 8	# ivtmp$46, ivtmp$46,
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	or	a3, a14, a5	# tmp221, tmp220, iftmp$0_137
# @OPUS@\upstream\celt\entdec.c:116:     sym=(sym<<EC_SYM_BITS|_this->rem)>>(EC_SYM_BITS-EC_CODE_EXTRA);
	srai	a3, a3, 1	# sym, tmp221,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	xor	a3, a10, a3	# tmp223, tmp318, sym
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	extui	a3, a3, 0, 8	# tmp225, tmp223,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	add.n	a3, a3, a9	# tmp227, tmp225, tmp226
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a3, a3, a11	# _192, tmp227, tmp242
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	s32i.n	a5, a12, 40	# _this_14(D)->rem, iftmp$0_137
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a3, a12, 32	# _this_14(D)->val, _192
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a13, .L76	# tmp241, _16,
	j	.L58		#
.L72:
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	and	a3, a3, a11	# _192, tmp237, tmp242
# @OPUS@\upstream\celt\entdec.c:114:     _this->rem=ec_read_byte(_this);
	movi.n	a4, 0	#,
	s32i.n	a4, a12, 40	# _this_14(D)->rem,
# @OPUS@\upstream\celt\entdec.c:118:     _this->val=((_this->val<<EC_SYM_BITS)+(EC_SYM_MAX&~sym))&(EC_CODE_TOP-1);
	s32i.n	a3, a12, 32	# _this_14(D)->val, _192
	addi.n	a8, a8, 8	# ivtmp$46, ivtmp$46,
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	bltu	a7, a13, .L58	# tmp241, _16,
# @OPUS@\upstream\celt\entdec.c:95:   return _this->offs<_this->storage?_this->buf[_this->offs++]:0;
	mov.n	a5, a4	# iftmp$0_137,
	j	.L74		#
.L76:
# @OPUS@\upstream\celt\entdec.c:107:   while(_this->rng<=EC_CODE_BOT){
	mov.n	a6, a4	# prephitmp_189, _134
	j	.L74		#
.L58:
# @OPUS@\upstream\celt\entdec.c:268: }
	l32i.n	a0, sp, 60	#,
	l32i.n	a12, sp, 56	#,
	l32i.n	a13, sp, 52	#,
	l32i.n	a14, sp, 48	#,
	l32i.n	a15, sp, 44	#,
	addi	sp, sp, 64	#,,
	ret.n
	.size	ec_dec_uint, .-ec_dec_uint
	.section	.text.ec_dec_bits,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_dec_bits
	.type	ec_dec_bits, @function
# Function: ec_dec_bits
# Module: upstream/celt/entdec.c
# Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ft=(unsigned)(_ft>>ftb)+1;
# C context: s=ec_decode(_this,ft);
# C context: ec_dec_update(_this,s,s+1,ft);
# C context: t=(opus_uint32)s<<ftb|ec_dec_bits(_this,ftb);
# C context: if(t<=_ft)return t;
# C context: _this->error=1;
# C context: return _ft;
# C context: }
ec_dec_bits:
# @OPUS@\upstream\celt\entdec.c:275:   available=_this->nend_bits;
	l32i.n	a4, a2, 16	# _this_18(D)->nend_bits, available
# @OPUS@\upstream\celt\entdec.c:274:   window=_this->end_window;
	l32i.n	a7, a2, 12	# _this_18(D)->end_window, window
# @OPUS@\upstream\celt\entdec.c:276:   if((unsigned)available<_bits){
	bgeu	a4, a3, .L81	# available, _bits,
# @OPUS@\upstream\celt\entdec.c:99:   return _this->end_offs<_this->storage?
	l32i.n	a8, a2, 4	# _this_18(D)->storage, _32
	l32i.n	a5, a2, 8	# _this_18(D)->end_offs, prephitmp_63
# @OPUS@\upstream\celt\entdec.c:281:     while(available<=EC_WINDOW_SIZE-EC_SYM_BITS);
	movi.n	a9, 0x18	# tmp69,
.L83:
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	bgeu	a5, a8, .L82	# prephitmp_63, _32,
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	addi.n	a5, a5, 1	# prephitmp_63, prephitmp_63,
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	l32i.n	a6, a2, 0	# _this_18(D)->buf, _33
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	sub	a10, a8, a5	# tmp65, _32, prephitmp_63
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	s32i.n	a5, a2, 8	# _this_18(D)->end_offs, prephitmp_63
# @OPUS@\upstream\celt\entdec.c:100:    _this->buf[_this->storage-++(_this->end_offs)]:0;
	add.n	a6, a6, a10	# tmp66, _33, tmp65
	l8ui	a6, a6, 0	# *_36, *_36
	ssl	a4	# available
	sll	a6, a6	# tmp68, *_36
	or	a7, a7, a6	# window, window, tmp68
.L82:
# @OPUS@\upstream\celt\entdec.c:279:       available+=EC_SYM_BITS;
	addi.n	a4, a4, 8	# available, available,
# @OPUS@\upstream\celt\entdec.c:281:     while(available<=EC_WINDOW_SIZE-EC_SYM_BITS);
	bge	a9, a4, .L83	# tmp69, available,
.L81:
# @OPUS@\upstream\celt\entdec.c:288:   _this->nbits_total+=_bits;
	l32i.n	a6, a2, 20	# _this_18(D)->nbits_total, _this_18(D)->nbits_total
# @OPUS@\upstream\celt\entdec.c:283:   ret=(opus_uint32)window&(((opus_uint32)1<<_bits)-1U);
	movi.n	a5, -1	# tmp75,
	ssl	a3	# _bits
	sll	a9, a5	# tmp76, tmp75
# @OPUS@\upstream\celt\entdec.c:284:   window>>=_bits;
	ssr	a3	# _bits
	srl	a8, a7	# window, window
# @OPUS@\upstream\celt\entdec.c:285:   available-=_bits;
	sub	a4, a4, a3	# available, available, _bits
# @OPUS@\upstream\celt\entdec.c:283:   ret=(opus_uint32)window&(((opus_uint32)1<<_bits)-1U);
	xor	a5, a5, a9	# tmp77, tmp75, tmp76
# @OPUS@\upstream\celt\entdec.c:288:   _this->nbits_total+=_bits;
	add.n	a3, a6, a3	# tmp72, _this_18(D)->nbits_total, _bits
# @OPUS@\upstream\celt\entdec.c:286:   _this->end_window=window;
	s32i.n	a8, a2, 12	# _this_18(D)->end_window, window
# @OPUS@\upstream\celt\entdec.c:287:   _this->nend_bits=available;
	s32i.n	a4, a2, 16	# _this_18(D)->nend_bits, available
# @OPUS@\upstream\celt\entdec.c:288:   _this->nbits_total+=_bits;
	s32i.n	a3, a2, 20	# _this_18(D)->nbits_total, tmp72
# @OPUS@\upstream\celt\entdec.c:290: }
	and	a2, a5, a7	#, tmp77, window
	ret.n
	.size	ec_dec_bits, .-ec_dec_bits
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"

# Exact small-div overlay; original GCC snapshot remains unchanged.

	.section .text.yoradio_opus_small_udiv,"ax",@progbits
	.literal_position
	.literal .Ly_small_table, yoradio_opus_small_div_table
	.literal .Ly_small_fallback, __udivsi3
	.align 4
	.global yoradio_opus_small_udiv
	.type yoradio_opus_small_udiv,@function
# Exact unsigned n/d: a2=n, a3=d, result a2. LX106 call0 leaf.
# Clobbers a2..a11/SAR, preserves a0/a1/a12..a15, no stack or writable RAM.
# For d=0 or d>256, tail-call the original __udivsi3 with original a2/a3.
# d=2^t*odd; q=high32((n>>t)*floor(2^32/odd)), then exact remainder fix.
# odd=1 uses UINT32_MAX, hence the same correction. q never exceeds n/d.
# All products below are 16x16 unsigned except the final exact q*d.
# Mid sum <= 65535^2+65534+65535 = UINT32_MAX-1, so no carry is lost.
yoradio_opus_small_udiv:
	movi a4,256
	bltu a4,a3,.Ly_small_slow
	beqz a3,.Ly_small_slow
	beqi a3,1,.Ly_small_ret
	neg a4,a3
	and a4,a4,a3
	nsau a4,a4
	movi a5,31
	sub a4,a5,a4
	ssr a4
	srl a5,a2
	srl a6,a3
	srli a6,a6,1
	l32r a7,.Ly_small_table
	addx4 a6,a6,a7
	l32i a6,a6,0
	extui a7,a5,0,16
	srli a5,a5,16
	extui a8,a6,0,16
	srli a6,a6,16
	mul16u a9,a7,a8
	srli a9,a9,16
	mul16u a10,a5,a8
	add a9,a9,a10
	mul16u a10,a7,a6
	extui a11,a10,0,16
	add a9,a9,a11
	srli a9,a9,16
	srli a10,a10,16
	mul16u a5,a5,a6
	add a5,a5,a9
	add a5,a5,a10
	mull a6,a5,a3
	sub a6,a2,a6
	addi a2,a5,1
	bgeu a6,a3,.Ly_small_ret
	mov a2,a5
.Ly_small_ret:
	ret.n
.Ly_small_slow:
	l32r a4,.Ly_small_fallback
	jx a4
	.size yoradio_opus_small_udiv,.-yoradio_opus_small_udiv
	.section .rodata.yoradio_opus_small_div_table,"a",@progbits
	.balign 4
	.type yoradio_opus_small_div_table,@object
yoradio_opus_small_div_table:
	.word 0xffffffff
	.word 0x55555555
	.word 0x33333333
	.word 0x24924924
	.word 0x1c71c71c
	.word 0x1745d174
	.word 0x13b13b13
	.word 0x11111111
	.word 0x0f0f0f0f
	.word 0x0d79435e
	.word 0x0c30c30c
	.word 0x0b21642c
	.word 0x0a3d70a3
	.word 0x097b425e
	.word 0x08d3dcb0
	.word 0x08421084
	.word 0x07c1f07c
	.word 0x07507507
	.word 0x06eb3e45
	.word 0x06906906
	.word 0x063e7063
	.word 0x05f417d0
	.word 0x05b05b05
	.word 0x0572620a
	.word 0x05397829
	.word 0x05050505
	.word 0x04d4873e
	.word 0x04a7904a
	.word 0x047dc11f
	.word 0x0456c797
	.word 0x04325c53
	.word 0x04104104
	.word 0x03f03f03
	.word 0x03d22635
	.word 0x03b5cc0e
	.word 0x039b0ad1
	.word 0x0381c0e0
	.word 0x0369d036
	.word 0x03531dec
	.word 0x033d91d2
	.word 0x0329161f
	.word 0x03159721
	.word 0x03030303
	.word 0x02f14990
	.word 0x02e05c0b
	.word 0x02d02d02
	.word 0x02c0b02c
	.word 0x02b1da46
	.word 0x02a3a0fd
	.word 0x0295fad4
	.word 0x0288df0c
	.word 0x027c4597
	.word 0x02702702
	.word 0x02647c69
	.word 0x02593f69
	.word 0x024e6a17
	.word 0x0243f6f0
	.word 0x0239e0d5
	.word 0x02302302
	.word 0x0226b902
	.word 0x021d9ead
	.word 0x0214d021
	.word 0x020c49ba
	.word 0x02040810
	.word 0x01fc07f0
	.word 0x01f44659
	.word 0x01ecc07b
	.word 0x01e573ac
	.word 0x01de5d6e
	.word 0x01d77b65
	.word 0x01d0cb58
	.word 0x01ca4b30
	.word 0x01c3f8f0
	.word 0x01bdd2b8
	.word 0x01b7d6c3
	.word 0x01b20364
	.word 0x01ac5701
	.word 0x01a6d01a
	.word 0x01a16d3f
	.word 0x019c2d14
	.word 0x01970e4f
	.word 0x01920fb4
	.word 0x018d3018
	.word 0x01886e5f
	.word 0x0183c977
	.word 0x017f405f
	.word 0x017ad220
	.word 0x01767dce
	.word 0x01724287
	.word 0x016e1f76
	.word 0x016a13cd
	.word 0x01661ec6
	.word 0x01623fa7
	.word 0x015e75bb
	.word 0x015ac056
	.word 0x01571ed3
	.word 0x01539094
	.word 0x01501501
	.word 0x014cab88
	.word 0x0149539e
	.word 0x01460cbc
	.word 0x0142d662
	.word 0x013fb013
	.word 0x013c995a
	.word 0x013991c2
	.word 0x013698df
	.word 0x0133ae45
	.word 0x0130d190
	.word 0x012e025c
	.word 0x012b404a
	.word 0x01288b01
	.word 0x0125e227
	.word 0x01234567
	.word 0x0120b470
	.word 0x011e2ef3
	.word 0x011bb4a4
	.word 0x01194538
	.word 0x0116e068
	.word 0x011485f0
	.word 0x0112358e
	.word 0x010fef01
	.word 0x010db20a
	.word 0x010b7e6e
	.word 0x010953f3
	.word 0x01073260
	.word 0x0105197f
	.word 0x0103091b
	.word 0x01010101
	.word 0x00000000
	.size yoradio_opus_small_div_table,.-yoradio_opus_small_div_table
