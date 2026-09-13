# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/celt/entenc.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"entenc.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\celt\entenc.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\celt\entenc.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\celt\entenc.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\celt\entenc.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\celt\entenc.c.s.raw
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
	.section	.text.ec_enc_init,"ax",@progbits
	.literal_position
	.literal .LC0, -2147483648
	.align	4
	.global	ec_enc_init
	.type	ec_enc_init, @function
# Function: ec_enc_init
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context: }
# C context:
# C context: void ec_enc_init(ec_enc *_this,unsigned char *_buf,opus_uint32 _size){
# C context: _this->buf=_buf;
# C context: _this->end_offs=0;
# C context: _this->end_window=0;
# C context: _this->nend_bits=0;
ec_enc_init:
# @OPUS@\upstream\celt\entenc.c:113:   _this->buf=_buf;
	s32i.n	a3, a2, 0	# _this_2(D)->buf, _buf
# @OPUS@\upstream\celt\entenc.c:118:   _this->nbits_total=EC_CODE_BITS+1;
	movi.n	a3, 0x21	# tmp48,
	s32i.n	a3, a2, 20	# _this_2(D)->nbits_total, tmp48
# @OPUS@\upstream\celt\entenc.c:120:   _this->rng=EC_CODE_TOP;
	l32r	a3, .LC0	#, tmp50
# @OPUS@\upstream\celt\entenc.c:114:   _this->end_offs=0;
	movi.n	a5, 0	# tmp45,
# @OPUS@\upstream\celt\entenc.c:120:   _this->rng=EC_CODE_TOP;
	s32i.n	a3, a2, 28	# _this_2(D)->rng, tmp50
# @OPUS@\upstream\celt\entenc.c:121:   _this->rem=-1;
	movi.n	a3, -1	# tmp51,
# @OPUS@\upstream\celt\entenc.c:114:   _this->end_offs=0;
	s32i.n	a5, a2, 8	# _this_2(D)->end_offs, tmp45
# @OPUS@\upstream\celt\entenc.c:115:   _this->end_window=0;
	s32i.n	a5, a2, 12	# _this_2(D)->end_window, tmp45
# @OPUS@\upstream\celt\entenc.c:116:   _this->nend_bits=0;
	s32i.n	a5, a2, 16	# _this_2(D)->nend_bits, tmp45
# @OPUS@\upstream\celt\entenc.c:119:   _this->offs=0;
	s32i.n	a5, a2, 24	# _this_2(D)->offs, tmp45
# @OPUS@\upstream\celt\entenc.c:121:   _this->rem=-1;
	s32i.n	a3, a2, 40	# _this_2(D)->rem, tmp51
# @OPUS@\upstream\celt\entenc.c:122:   _this->val=0;
	s32i.n	a5, a2, 32	# _this_2(D)->val, tmp45
# @OPUS@\upstream\celt\entenc.c:123:   _this->ext=0;
	s32i.n	a5, a2, 36	# _this_2(D)->ext, tmp45
# @OPUS@\upstream\celt\entenc.c:124:   _this->storage=_size;
	s32i.n	a4, a2, 4	# _this_2(D)->storage, _size
# @OPUS@\upstream\celt\entenc.c:125:   _this->error=0;
	s32i.n	a5, a2, 44	# _this_2(D)->error, tmp45
# @OPUS@\upstream\celt\entenc.c:126: }
	ret.n
	.size	ec_enc_init, .-ec_enc_init
	.global	__udivsi3
	.section	.text.ec_encode,"ax",@progbits
	.literal_position
	.literal .LC1, 8388608
	.literal .LC2, 2147483647
	.align	4
	.global	ec_encode
	.type	ec_encode, @function
# Function: ec_encode
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: _this->error=0;
# C context: }
# C context:
# C context: void ec_encode(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _ft){
# C context: opus_uint32 r;
# C context: r=celt_udiv(_this->rng,_ft);
# C context: if(_fl>0){
# C context: _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
ec_encode:
	addi	sp, sp, -48	#,,
	s32i.n	a14, sp, 32	#,
# @OPUS@\upstream\celt\entenc.c:130:   r=celt_udiv(_this->rng,_ft);
	l32i.n	a14, a2, 28	# _this_14(D)->rng, _1
# @OPUS@\upstream\celt\entenc.c:128: void ec_encode(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	s32i.n	a13, sp, 36	#,
	mov.n	a13, a5	# _ft, _ft
	s32i.n	a12, sp, 40	#,
	mov.n	a5, a3	# _fl, _fl
	mov.n	a12, a2	# _this, _this
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	mov.n	a3, a13	#, _ft
	mov.n	a2, a14	#, _1
# @OPUS@\upstream\celt\entenc.c:128: void ec_encode(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	s32i.n	a15, sp, 28	#,
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	s32i.n	a5, sp, 0	#,
# @OPUS@\upstream\celt\entenc.c:128: void ec_encode(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	s32i.n	a0, sp, 44	#,
# @OPUS@\upstream\celt\entenc.c:128: void ec_encode(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _ft){
	mov.n	a15, a4	# _fh, _fh
# @OPUS@\upstream\celt\entcode.h:136:    return n/d;
	call0	__udivsi3		#
# @OPUS@\upstream\celt\entenc.c:131:   if(_fl>0){
	l32i.n	a5, sp, 0	#,
	beqz.n	a5, .L4	# _fl,
# @OPUS@\upstream\celt\entenc.c:132:     _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
	l32i.n	a3, a12, 32	# _this_14(D)->val, _this_14(D)->val
# @OPUS@\upstream\celt\entenc.c:132:     _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
	sub	a13, a13, a5	# tmp97, _ft, _fl
	mull	a13, a13, a2	# tmp98, tmp97, tmp94
# @OPUS@\upstream\celt\entenc.c:132:     _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
	add.n	a3, a14, a3	# tmp95, _1, _this_14(D)->val
# @OPUS@\upstream\celt\entenc.c:133:     _this->rng=IMUL32(r,(_fh-_fl));
	sub	a15, a15, a5	# tmp100, _fh, _fl
# @OPUS@\upstream\celt\entenc.c:132:     _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
	sub	a3, a3, a13	# tmp99, tmp95, tmp98
# @OPUS@\upstream\celt\entenc.c:133:     _this->rng=IMUL32(r,(_fh-_fl));
	mull	a13, a15, a2	# _11, tmp100, tmp94
# @OPUS@\upstream\celt\entenc.c:132:     _this->val+=_this->rng-IMUL32(r,(_ft-_fl));
	s32i.n	a3, a12, 32	# _this_14(D)->val, tmp99
.L6:
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	l32r	a6, .LC1	#, tmp128
	s32i.n	a13, a12, 28	# _this_14(D)->rng, _11
	bgeu	a6, a13, .L5	# tmp128, _11,
	j	.L3		#
.L4:
# @OPUS@\upstream\celt\entenc.c:135:   else _this->rng-=IMUL32(r,(_ft-_fh));
	sub	a13, a13, a15	# tmp102, _ft, _fh
	mull	a13, a13, a2	# tmp103, tmp102, tmp94
# @OPUS@\upstream\celt\entenc.c:135:   else _this->rng-=IMUL32(r,(_ft-_fh));
	sub	a13, a14, a13	# _11, _1, tmp103
	j	.L6		#
.L5:
	l32i.n	a2, a12, 32	# _this_14(D)->val, _30
	l32r	a8, .LC2	#, tmp130
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a7, 0xff	# tmp104,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a9, -1	# tmp133,
.L16:
# @OPUS@\upstream\celt\entenc.c:104:     ec_enc_carry_out(_this,(int)(_this->val>>EC_CODE_SHIFT));
	extui	a5, a2, 23, 9	# _24, _30,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a5, a7, .L7	# _24, tmp104,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	l32i.n	a3, a12, 40	# _this_14(D)->rem, _37
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a10, a5, 8	# carry, _24,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a3, .L8	# _37,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a2, a12, 24	# _this_14(D)->offs, _53
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a4, a12, 8	# _this_14(D)->end_offs, _this_14(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a11, a12, 4	# _this_14(D)->storage, _this_14(D)->storage
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a4, a2, a4	# tmp105, _53, _this_14(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a3, a10, a3	# _38, carry, _37
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a4, a11, .L18	# tmp105, _this_14(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a4, a12, 0	# _this_14(D)->buf, _43
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a11, a2, 1	# tmp108, _53,
	s32i.n	a11, a12, 24	# _this_14(D)->offs, tmp108
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a4, a2	# tmp109, _43, _53
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a3, a2, 0	# *_45, _38
	l32i.n	a2, a12, 44	# _this_14(D)->error, pretmp_154
	j	.L9		#
.L18:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a2, a9	# pretmp_154, tmp133
.L9:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a2, a12, 44	# _this_14(D)->error, pretmp_154
.L8:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a3, a12, 36	# _this_14(D)->ext, _142
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a3, .L10	# _142,
.L14:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a5, a5, 0, 8	# tmp110, _24,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a5, a12, 40	# _this_14(D)->rem, tmp110
	l32i.n	a2, a12, 32	# _this_14(D)->val, _30
	j	.L11		#
.L10:
	l32i.n	a2, a12, 24	# _this_14(D)->offs, _53
	l32i.n	a4, a12, 8	# _this_14(D)->end_offs, _this_14(D)->end_offs
	l32i.n	a11, a12, 4	# _this_14(D)->storage, _this_14(D)->storage
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a10, a10, a7	# _52, carry, tmp104
.L15:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a14, a2, a4	# tmp112, _53, _this_14(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a13, a2, 1	# tmp115, _53,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a14, a11, .L12	# tmp112, _this_14(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a3, a12, 0	# _this_14(D)->buf, _57
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a13, a12, 24	# _this_14(D)->offs, tmp115
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a3, a2	# tmp116, _57, _53
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a10, a2, 0	# *_59, _52
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a3, a12, 36	# _this_14(D)->ext, _this_14(D)->ext
	addi.n	a3, a3, -1	# _142, _this_14(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a3, a12, 36	# _this_14(D)->ext, _142
	beqz.n	a3, .L14	# _142,
	l32i.n	a2, a12, 24	# _this_14(D)->offs, _53
	l32i.n	a4, a12, 8	# _this_14(D)->end_offs, _this_14(D)->end_offs
	l32i.n	a11, a12, 4	# _this_14(D)->storage, _this_14(D)->storage
	j	.L15		#
.L12:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a3, a3, -1	# _142, _142,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a9, a12, 44	# _this_14(D)->error, tmp133
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a3, a12, 36	# _this_14(D)->ext, _142
	bnez.n	a3, .L15	# _142,
	j	.L14		#
.L7:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a3, a12, 36	# _this_14(D)->ext, _this_14(D)->ext
	addi.n	a3, a3, 1	# tmp119, _this_14(D)->ext,
	s32i.n	a3, a12, 36	# _this_14(D)->ext, tmp119
.L11:
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	l32i.n	a3, a12, 28	# _this_14(D)->rng, _this_14(D)->rng
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	l32i.n	a4, a12, 20	# _this_14(D)->nbits_total, _this_14(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a2, a2, 8	# tmp121, _30,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a2, a2, a8	# _30, tmp121, tmp130
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	slli	a3, a3, 8	# _32, _this_14(D)->rng,
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	addi.n	a4, a4, 8	# tmp124, _this_14(D)->nbits_total,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	s32i.n	a2, a12, 32	# _this_14(D)->val, _30
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a3, a12, 28	# _this_14(D)->rng, _32
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a4, a12, 20	# _this_14(D)->nbits_total, tmp124
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a6, a3, .L16	# tmp128, _32,
.L3:
# @OPUS@\upstream\celt\entenc.c:137: }
	l32i.n	a0, sp, 44	#,
	l32i.n	a12, sp, 40	#,
	l32i.n	a13, sp, 36	#,
	l32i.n	a14, sp, 32	#,
	l32i.n	a15, sp, 28	#,
	addi	sp, sp, 48	#,,
	ret.n
	.size	ec_encode, .-ec_encode
	.section	.text.ec_encode_bin,"ax",@progbits
	.literal_position
	.literal .LC3, 8388608
	.literal .LC4, 2147483647
	.align	4
	.global	ec_encode_bin
	.type	ec_encode_bin, @function
# Function: ec_encode_bin
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_enc_normalize(_this);
# C context: }
# C context:
# C context: void ec_encode_bin(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _bits){
# C context: opus_uint32 r;
# C context: r=_this->rng>>_bits;
# C context: if(_fl>0){
# C context: _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
ec_encode_bin:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entenc.c:141:   r=_this->rng>>_bits;
	l32i.n	a7, a2, 28	# _this_16(D)->rng, _1
	movi.n	a6, 1	# tmp93,
# @OPUS@\upstream\celt\entenc.c:139: void ec_encode_bin(ec_enc *_this,unsigned _fl,unsigned _fh,unsigned _bits){
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:141:   r=_this->rng>>_bits;
	ssr	a5	# _bits
	srl	a8, a7	# r, _1
	ssl	a5	# _bits
	sll	a6, a6	# _123, tmp93
# @OPUS@\upstream\celt\entenc.c:142:   if(_fl>0){
	beqz.n	a3, .L25	# _fl,
# @OPUS@\upstream\celt\entenc.c:143:     _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
	l32i.n	a5, a2, 32	# _this_16(D)->val, _this_16(D)->val
# @OPUS@\upstream\celt\entenc.c:143:     _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
	sub	a6, a6, a3	# tmp96, _123, _fl
	mull	a6, a6, a8	# tmp97, tmp96, r
# @OPUS@\upstream\celt\entenc.c:143:     _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
	add.n	a7, a7, a5	# tmp94, _1, _this_16(D)->val
# @OPUS@\upstream\celt\entenc.c:144:     _this->rng=IMUL32(r,(_fh-_fl));
	sub	a4, a4, a3	# tmp99, _fh, _fl
# @OPUS@\upstream\celt\entenc.c:143:     _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
	sub	a7, a7, a6	# tmp98, tmp94, tmp97
# @OPUS@\upstream\celt\entenc.c:144:     _this->rng=IMUL32(r,(_fh-_fl));
	mull	a6, a4, a8	# _13, tmp99, r
# @OPUS@\upstream\celt\entenc.c:143:     _this->val+=_this->rng-IMUL32(r,((1U<<_bits)-_fl));
	s32i.n	a7, a2, 32	# _this_16(D)->val, tmp98
.L27:
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC3	#, tmp129
	s32i.n	a6, a2, 28	# _this_16(D)->rng, _13
	bgeu	a7, a6, .L26	# tmp129, _13,
	j	.L24		#
.L25:
# @OPUS@\upstream\celt\entenc.c:146:   else _this->rng-=IMUL32(r,((1U<<_bits)-_fh));
	sub	a6, a6, a4	# tmp101, _123, _fh
	mull	a6, a6, a8	# tmp102, tmp101, r
# @OPUS@\upstream\celt\entenc.c:146:   else _this->rng-=IMUL32(r,((1U<<_bits)-_fh));
	sub	a6, a7, a6	# _13, _1, tmp102
	j	.L27		#
.L26:
	l32i.n	a3, a2, 32	# _this_16(D)->val, _32
	l32r	a9, .LC4	#, tmp130
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a8, 0xff	# tmp103,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a10, -1	# tmp132,
.L37:
# @OPUS@\upstream\celt\entenc.c:104:     ec_enc_carry_out(_this,(int)(_this->val>>EC_CODE_SHIFT));
	extui	a6, a3, 23, 9	# _26, _32,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a6, a8, .L28	# _26, tmp103,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	l32i.n	a4, a2, 40	# _this_16(D)->rem, _39
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a11, a6, 8	# carry, _26,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a4, .L29	# _39,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a2, 24	# _this_16(D)->offs, _55
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a5, a2, 8	# _this_16(D)->end_offs, _this_16(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a12, a2, 4	# _this_16(D)->storage, _this_16(D)->storage
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a5, a3, a5	# tmp104, _55, _this_16(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a4, a11, a4	# _40, carry, _39
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a5, a12, .L39	# tmp104, _this_16(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a5, a2, 0	# _this_16(D)->buf, _45
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a12, a3, 1	# tmp107, _55,
	s32i.n	a12, a2, 24	# _this_16(D)->offs, tmp107
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a5, a3	# tmp108, _45, _55
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a4, a3, 0	# *_47, _40
	l32i.n	a3, a2, 44	# _this_16(D)->error, pretmp_157
	j	.L30		#
.L39:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a3, a10	# pretmp_157, tmp132
.L30:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a3, a2, 44	# _this_16(D)->error, pretmp_157
.L29:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a4, a2, 36	# _this_16(D)->ext, _145
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a4, .L31	# _145,
.L35:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a6, a6, 0, 8	# tmp109, _26,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a6, a2, 40	# _this_16(D)->rem, tmp109
	l32i.n	a3, a2, 32	# _this_16(D)->val, _32
	j	.L32		#
.L31:
	l32i.n	a3, a2, 24	# _this_16(D)->offs, _55
	l32i.n	a5, a2, 8	# _this_16(D)->end_offs, _this_16(D)->end_offs
	l32i.n	a12, a2, 4	# _this_16(D)->storage, _this_16(D)->storage
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a11, a11, a8	# _54, carry, tmp103
.L36:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a14, a3, a5	# tmp111, _55, _this_16(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a13, a3, 1	# tmp114, _55,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a14, a12, .L33	# tmp111, _this_16(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a4, a2, 0	# _this_16(D)->buf, _59
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a13, a2, 24	# _this_16(D)->offs, tmp114
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a4, a3	# tmp115, _59, _55
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a11, a3, 0	# *_61, _54
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a4, a2, 36	# _this_16(D)->ext, _this_16(D)->ext
	addi.n	a4, a4, -1	# _145, _this_16(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_16(D)->ext, _145
	beqz.n	a4, .L35	# _145,
	l32i.n	a3, a2, 24	# _this_16(D)->offs, _55
	l32i.n	a5, a2, 8	# _this_16(D)->end_offs, _this_16(D)->end_offs
	l32i.n	a12, a2, 4	# _this_16(D)->storage, _this_16(D)->storage
	j	.L36		#
.L33:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a4, a4, -1	# _145, _145,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a10, a2, 44	# _this_16(D)->error, tmp132
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_16(D)->ext, _145
	bnez.n	a4, .L36	# _145,
	j	.L35		#
.L28:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a4, a2, 36	# _this_16(D)->ext, _this_16(D)->ext
	addi.n	a4, a4, 1	# tmp118, _this_16(D)->ext,
	s32i.n	a4, a2, 36	# _this_16(D)->ext, tmp118
.L32:
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	l32i.n	a4, a2, 28	# _this_16(D)->rng, _this_16(D)->rng
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	l32i.n	a5, a2, 20	# _this_16(D)->nbits_total, _this_16(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a3, a3, 8	# tmp120, _32,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a3, a3, a9	# _32, tmp120, tmp130
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	slli	a4, a4, 8	# _34, _this_16(D)->rng,
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	addi.n	a5, a5, 8	# tmp123, _this_16(D)->nbits_total,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	s32i.n	a3, a2, 32	# _this_16(D)->val, _32
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a4, a2, 28	# _this_16(D)->rng, _34
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a5, a2, 20	# _this_16(D)->nbits_total, tmp123
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a4, .L37	# tmp129, _34,
.L24:
# @OPUS@\upstream\celt\entenc.c:148: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_encode_bin, .-ec_encode_bin
	.section	.text.ec_enc_bit_logp,"ax",@progbits
	.literal_position
	.literal .LC5, 8388608
	.literal .LC6, 2147483647
	.align	4
	.global	ec_enc_bit_logp
	.type	ec_enc_bit_logp, @function
# Function: ec_enc_bit_logp
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: }
# C context:
# C context: /*The probability of having a "one" is 1/(1<<_logp).*/
# C context: void ec_enc_bit_logp(ec_enc *_this,int _val,unsigned _logp){
# C context: opus_uint32 r;
# C context: opus_uint32 s;
# C context: opus_uint32 l;
# C context: r=_this->rng;
ec_enc_bit_logp:
# @OPUS@\upstream\celt\entenc.c:155:   r=_this->rng;
	l32i.n	a6, a2, 28	# _this_5(D)->rng, r
# @OPUS@\upstream\celt\entenc.c:151: void ec_enc_bit_logp(ec_enc *_this,int _val,unsigned _logp){
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entenc.c:157:   s=r>>_logp;
	ssr	a4	# _logp
	srl	a4, a6	# s, r
# @OPUS@\upstream\celt\entenc.c:151: void ec_enc_bit_logp(ec_enc *_this,int _val,unsigned _logp){
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:156:   l=_this->val;
	l32i.n	a5, a2, 32	# _this_5(D)->val, l
# @OPUS@\upstream\celt\entenc.c:158:   r-=s;
	sub	a6, a6, a4	# iftmp$1_2, r, s
# @OPUS@\upstream\celt\entenc.c:159:   if(_val)_this->val=l+r;
	beqz.n	a3, .L46	# _val,
# @OPUS@\upstream\celt\entenc.c:159:   if(_val)_this->val=l+r;
	add.n	a5, a5, a6	# l, l, iftmp$1_2
# @OPUS@\upstream\celt\entenc.c:159:   if(_val)_this->val=l+r;
	s32i.n	a5, a2, 32	# _this_5(D)->val, l
# @OPUS@\upstream\celt\entenc.c:160:   _this->rng=_val?s:r;
	mov.n	a6, a4	# iftmp$1_2, s
.L46:
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC5	#, tmp109
# @OPUS@\upstream\celt\entenc.c:160:   _this->rng=_val?s:r;
	s32i.n	a6, a2, 28	# _this_5(D)->rng, iftmp$1_2
	l32r	a9, .LC6	#, tmp111
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a8, 0xff	# tmp84,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a10, -1	# tmp113,
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bltu	a7, a6, .L45	# tmp109, iftmp$1_2,
.L47:
# @OPUS@\upstream\celt\entenc.c:104:     ec_enc_carry_out(_this,(int)(_this->val>>EC_CODE_SHIFT));
	extui	a6, a5, 23, 9	# _16, l,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a6, a8, .L48	# _16, tmp84,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	l32i.n	a4, a2, 40	# _this_5(D)->rem, _29
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a11, a6, 8	# carry, _16,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a4, .L49	# _29,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a2, 24	# _this_5(D)->offs, _45
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a5, a2, 8	# _this_5(D)->end_offs, _this_5(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a12, a2, 4	# _this_5(D)->storage, _this_5(D)->storage
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a5, a3, a5	# tmp85, _45, _this_5(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a4, a11, a4	# _30, carry, _29
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a5, a12, .L58	# tmp85, _this_5(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a5, a2, 0	# _this_5(D)->buf, _35
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a12, a3, 1	# tmp88, _45,
	s32i.n	a12, a2, 24	# _this_5(D)->offs, tmp88
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a5, a3	# tmp89, _35, _45
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a4, a3, 0	# *_37, _30
	l32i.n	a3, a2, 44	# _this_5(D)->error, pretmp_145
	j	.L50		#
.L58:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a3, a10	# pretmp_145, tmp113
.L50:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a3, a2, 44	# _this_5(D)->error, pretmp_145
.L49:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a4, a2, 36	# _this_5(D)->ext, _137
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a4, .L51	# _137,
.L55:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a6, a6, 0, 8	# tmp90, _16,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a6, a2, 40	# _this_5(D)->rem, tmp90
	l32i.n	a5, a2, 32	# _this_5(D)->val, l
	j	.L52		#
.L51:
	l32i.n	a3, a2, 24	# _this_5(D)->offs, _45
	l32i.n	a5, a2, 8	# _this_5(D)->end_offs, _this_5(D)->end_offs
	l32i.n	a12, a2, 4	# _this_5(D)->storage, _this_5(D)->storage
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a11, a11, a8	# _44, carry, tmp84
.L56:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a14, a3, a5	# tmp92, _45, _this_5(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a13, a3, 1	# tmp95, _45,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a14, a12, .L53	# tmp92, _this_5(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a4, a2, 0	# _this_5(D)->buf, _49
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a13, a2, 24	# _this_5(D)->offs, tmp95
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a4, a3	# tmp96, _49, _45
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a11, a3, 0	# *_51, _44
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a4, a2, 36	# _this_5(D)->ext, _this_5(D)->ext
	addi.n	a4, a4, -1	# _137, _this_5(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_5(D)->ext, _137
	beqz.n	a4, .L55	# _137,
	l32i.n	a3, a2, 24	# _this_5(D)->offs, _45
	l32i.n	a5, a2, 8	# _this_5(D)->end_offs, _this_5(D)->end_offs
	l32i.n	a12, a2, 4	# _this_5(D)->storage, _this_5(D)->storage
	j	.L56		#
.L53:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a4, a4, -1	# _137, _137,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a10, a2, 44	# _this_5(D)->error, tmp113
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_5(D)->ext, _137
	bnez.n	a4, .L56	# _137,
	j	.L55		#
.L48:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a3, a2, 36	# _this_5(D)->ext, _this_5(D)->ext
	addi.n	a3, a3, 1	# tmp99, _this_5(D)->ext,
	s32i.n	a3, a2, 36	# _this_5(D)->ext, tmp99
.L52:
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	l32i.n	a3, a2, 28	# _this_5(D)->rng, _this_5(D)->rng
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	l32i.n	a4, a2, 20	# _this_5(D)->nbits_total, _this_5(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a5, a5, 8	# tmp101, l,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a5, a5, a9	# l, tmp101, tmp111
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	slli	a3, a3, 8	# _24, _this_5(D)->rng,
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	addi.n	a4, a4, 8	# tmp104, _this_5(D)->nbits_total,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	s32i.n	a5, a2, 32	# _this_5(D)->val, l
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a3, a2, 28	# _this_5(D)->rng, _24
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a4, a2, 20	# _this_5(D)->nbits_total, tmp104
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a3, .L47	# tmp109, _24,
.L45:
# @OPUS@\upstream\celt\entenc.c:162: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_enc_bit_logp, .-ec_enc_bit_logp
	.section	.text.ec_enc_icdf,"ax",@progbits
	.literal_position
	.literal .LC7, 8388608
	.literal .LC8, 2147483647
	.align	4
	.global	ec_enc_icdf
	.type	ec_enc_icdf, @function
# Function: ec_enc_icdf
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_enc_normalize(_this);
# C context: }
# C context:
# C context: void ec_enc_icdf(ec_enc *_this,int _s,const unsigned char *_icdf,unsigned _ftb){
# C context: opus_uint32 r;
# C context: r=_this->rng>>_ftb;
# C context: if(_s>0){
# C context: _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
ec_enc_icdf:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entenc.c:166:   r=_this->rng>>_ftb;
	l32i.n	a6, a2, 28	# _this_27(D)->rng, _1
# @OPUS@\upstream\celt\entenc.c:164: void ec_enc_icdf(ec_enc *_this,int _s,const unsigned char *_icdf,unsigned _ftb){
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:166:   r=_this->rng>>_ftb;
	ssr	a5	# _ftb
	srl	a5, a6	# r, _1
	add.n	a8, a4, a3	# _136, _icdf, _s
# @OPUS@\upstream\celt\entenc.c:167:   if(_s>0){
	blti	a3, 1, .L70	# _s,,
# @OPUS@\upstream\celt\entenc.c:168:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	addi.n	a3, a3, -1	# tmp103, _s,
	add.n	a3, a4, a3	# _5, _icdf, tmp103
	l8ui	a7, a3, 0	# *_5, *_5
# @OPUS@\upstream\celt\entenc.c:168:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	l32i.n	a4, a2, 32	# _this_27(D)->val, _this_27(D)->val
# @OPUS@\upstream\celt\entenc.c:168:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	mull	a7, a7, a5	# tmp107, *_5, r
# @OPUS@\upstream\celt\entenc.c:168:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	add.n	a4, a6, a4	# tmp104, _1, _this_27(D)->val
	sub	a4, a4, a7	# tmp108, tmp104, tmp107
	s32i.n	a4, a2, 32	# _this_27(D)->val, tmp108
# @OPUS@\upstream\celt\entenc.c:169:     _this->rng=IMUL32(r,_icdf[_s-1]-_icdf[_s]);
	l8ui	a6, a3, 0	# *_5, *_5
	l8ui	a3, a8, 0	# *_136, *_136
	sub	a6, a6, a3	# tmp111, *_5, *_136
	mull	a6, a6, a5	# _18, tmp111, r
# @OPUS@\upstream\celt\entenc.c:169:     _this->rng=IMUL32(r,_icdf[_s-1]-_icdf[_s]);
	s32i.n	a6, a2, 28	# _this_27(D)->rng, _18
	j	.L71		#
.L70:
# @OPUS@\upstream\celt\entenc.c:171:   else _this->rng-=IMUL32(r,_icdf[_s]);
	l8ui	a3, a8, 0	# *_136, *_136
	mull	a5, a3, a5	# tmp113, *_136, r
# @OPUS@\upstream\celt\entenc.c:171:   else _this->rng-=IMUL32(r,_icdf[_s]);
	sub	a6, a6, a5	# _18, _1, tmp113
	s32i.n	a6, a2, 28	# _this_27(D)->rng, _18
.L71:
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC7	#, tmp138
	bltu	a7, a6, .L69	# tmp138, _18,
	l32i.n	a3, a2, 32	# _this_27(D)->val, _43
	l32r	a9, .LC8	#, tmp140
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a8, 0xff	# tmp115,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a10, -1	# tmp144,
.L82:
# @OPUS@\upstream\celt\entenc.c:104:     ec_enc_carry_out(_this,(int)(_this->val>>EC_CODE_SHIFT));
	extui	a6, a3, 23, 9	# _37, _43,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a6, a8, .L73	# _37, tmp115,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	l32i.n	a4, a2, 40	# _this_27(D)->rem, _50
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a11, a6, 8	# carry, _37,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a4, .L74	# _50,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a2, 24	# _this_27(D)->offs, _66
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a5, a2, 8	# _this_27(D)->end_offs, _this_27(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a12, a2, 4	# _this_27(D)->storage, _this_27(D)->storage
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a5, a3, a5	# tmp116, _66, _this_27(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a4, a11, a4	# _51, carry, _50
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a5, a12, .L84	# tmp116, _this_27(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a5, a2, 0	# _this_27(D)->buf, _56
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a12, a3, 1	# tmp119, _66,
	s32i.n	a12, a2, 24	# _this_27(D)->offs, tmp119
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a5, a3	# tmp120, _56, _66
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a4, a3, 0	# *_58, _51
	l32i.n	a3, a2, 44	# _this_27(D)->error, pretmp_170
	j	.L75		#
.L84:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a3, a10	# pretmp_170, tmp144
.L75:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a3, a2, 44	# _this_27(D)->error, pretmp_170
.L74:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a4, a2, 36	# _this_27(D)->ext, _161
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a4, .L76	# _161,
.L80:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a6, a6, 0, 8	# tmp121, _37,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a6, a2, 40	# _this_27(D)->rem, tmp121
	l32i.n	a3, a2, 32	# _this_27(D)->val, _43
	j	.L77		#
.L76:
	l32i.n	a3, a2, 24	# _this_27(D)->offs, _66
	l32i.n	a5, a2, 8	# _this_27(D)->end_offs, _this_27(D)->end_offs
	l32i.n	a12, a2, 4	# _this_27(D)->storage, _this_27(D)->storage
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a11, a11, a8	# _65, carry, tmp115
.L81:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a14, a3, a5	# tmp123, _66, _this_27(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a13, a3, 1	# tmp126, _66,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a14, a12, .L78	# tmp123, _this_27(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a4, a2, 0	# _this_27(D)->buf, _70
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a13, a2, 24	# _this_27(D)->offs, tmp126
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a4, a3	# tmp127, _70, _66
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a11, a3, 0	# *_72, _65
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a4, a2, 36	# _this_27(D)->ext, _this_27(D)->ext
	addi.n	a4, a4, -1	# _161, _this_27(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_27(D)->ext, _161
	beqz.n	a4, .L80	# _161,
	l32i.n	a3, a2, 24	# _this_27(D)->offs, _66
	l32i.n	a5, a2, 8	# _this_27(D)->end_offs, _this_27(D)->end_offs
	l32i.n	a12, a2, 4	# _this_27(D)->storage, _this_27(D)->storage
	j	.L81		#
.L78:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a4, a4, -1	# _161, _161,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a10, a2, 44	# _this_27(D)->error, tmp144
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_27(D)->ext, _161
	bnez.n	a4, .L81	# _161,
	j	.L80		#
.L73:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a4, a2, 36	# _this_27(D)->ext, _this_27(D)->ext
	addi.n	a4, a4, 1	# tmp130, _this_27(D)->ext,
	s32i.n	a4, a2, 36	# _this_27(D)->ext, tmp130
.L77:
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	l32i.n	a4, a2, 28	# _this_27(D)->rng, _this_27(D)->rng
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	l32i.n	a5, a2, 20	# _this_27(D)->nbits_total, _this_27(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a3, a3, 8	# tmp132, _43,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a3, a3, a9	# _43, tmp132, tmp140
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	slli	a4, a4, 8	# _45, _this_27(D)->rng,
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	addi.n	a5, a5, 8	# tmp135, _this_27(D)->nbits_total,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	s32i.n	a3, a2, 32	# _this_27(D)->val, _43
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a4, a2, 28	# _this_27(D)->rng, _45
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a5, a2, 20	# _this_27(D)->nbits_total, tmp135
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a4, .L82	# tmp138, _45,
.L69:
# @OPUS@\upstream\celt\entenc.c:173: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_enc_icdf, .-ec_enc_icdf
	.section	.text.ec_enc_icdf16,"ax",@progbits
	.literal_position
	.literal .LC9, 8388608
	.literal .LC10, 2147483647
	.align	4
	.global	ec_enc_icdf16
	.type	ec_enc_icdf16, @function
# Function: ec_enc_icdf16
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_enc_normalize(_this);
# C context: }
# C context:
# C context: void ec_enc_icdf16(ec_enc *_this,int _s,const opus_uint16 *_icdf,unsigned _ftb){
# C context: opus_uint32 r;
# C context: r=_this->rng>>_ftb;
# C context: if(_s>0){
# C context: _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
ec_enc_icdf16:
	addi	sp, sp, -16	#,,
	slli	a6, a3, 1	# _137, _s,
# @OPUS@\upstream\celt\entenc.c:177:   r=_this->rng>>_ftb;
	l32i.n	a7, a2, 28	# _this_29(D)->rng, _1
	add.n	a4, a4, a6	# tmp102, _icdf, _137
# @OPUS@\upstream\celt\entenc.c:175: void ec_enc_icdf16(ec_enc *_this,int _s,const opus_uint16 *_icdf,unsigned _ftb){
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:177:   r=_this->rng>>_ftb;
	ssr	a5	# _ftb
	srl	a5, a7	# r, _1
	l16ui	a6, a4, 0	# *_138, pretmp_139
# @OPUS@\upstream\celt\entenc.c:178:   if(_s>0){
	blti	a3, 1, .L91	# _s,,
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	addi	a4, a4, -2	# tmp104, tmp102,
	l16ui	a3, a4, 0	# *_6, _7
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	l32i.n	a8, a2, 32	# _this_29(D)->val, _this_29(D)->val
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	mull	a4, a3, a5	# tmp107, _7, r
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	add.n	a7, a7, a8	# tmp105, _1, _this_29(D)->val
# @OPUS@\upstream\celt\entenc.c:180:     _this->rng=IMUL32(r,_icdf[_s-1]-_icdf[_s]);
	sub	a3, a3, a6	# tmp109, _7, pretmp_139
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	sub	a7, a7, a4	# tmp108, tmp105, tmp107
# @OPUS@\upstream\celt\entenc.c:180:     _this->rng=IMUL32(r,_icdf[_s-1]-_icdf[_s]);
	mull	a5, a3, a5	# _19, tmp109, r
# @OPUS@\upstream\celt\entenc.c:179:     _this->val+=_this->rng-IMUL32(r,_icdf[_s-1]);
	s32i.n	a7, a2, 32	# _this_29(D)->val, tmp108
.L93:
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	l32r	a7, .LC9	#, tmp135
	s32i.n	a5, a2, 28	# _this_29(D)->rng, _19
	bgeu	a7, a5, .L92	# tmp135, _19,
	j	.L90		#
.L91:
# @OPUS@\upstream\celt\entenc.c:182:   else _this->rng-=IMUL32(r,_icdf[_s]);
	mull	a5, a6, a5	# tmp111, pretmp_139, r
# @OPUS@\upstream\celt\entenc.c:182:   else _this->rng-=IMUL32(r,_icdf[_s]);
	sub	a5, a7, a5	# _19, _1, tmp111
	j	.L93		#
.L92:
	l32i.n	a3, a2, 32	# _this_29(D)->val, _45
	l32r	a9, .LC10	#, tmp138
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a8, 0xff	# tmp112,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a10, -1	# tmp141,
.L103:
# @OPUS@\upstream\celt\entenc.c:104:     ec_enc_carry_out(_this,(int)(_this->val>>EC_CODE_SHIFT));
	extui	a6, a3, 23, 9	# _39, _45,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a6, a8, .L94	# _39, tmp112,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	l32i.n	a4, a2, 40	# _this_29(D)->rem, _52
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a11, a6, 8	# carry, _39,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a4, .L95	# _52,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a2, 24	# _this_29(D)->offs, _68
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a5, a2, 8	# _this_29(D)->end_offs, _this_29(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a12, a2, 4	# _this_29(D)->storage, _this_29(D)->storage
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a5, a3, a5	# tmp113, _68, _this_29(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a4, a11, a4	# _53, carry, _52
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a5, a12, .L105	# tmp113, _this_29(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a5, a2, 0	# _this_29(D)->buf, _58
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a12, a3, 1	# tmp116, _68,
	s32i.n	a12, a2, 24	# _this_29(D)->offs, tmp116
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a5, a3	# tmp117, _58, _68
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a4, a3, 0	# *_60, _53
	l32i.n	a3, a2, 44	# _this_29(D)->error, pretmp_173
	j	.L96		#
.L105:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a3, a10	# pretmp_173, tmp141
.L96:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a3, a2, 44	# _this_29(D)->error, pretmp_173
.L95:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a4, a2, 36	# _this_29(D)->ext, _164
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a4, .L97	# _164,
.L101:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a6, a6, 0, 8	# tmp118, _39,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a6, a2, 40	# _this_29(D)->rem, tmp118
	l32i.n	a3, a2, 32	# _this_29(D)->val, _45
	j	.L98		#
.L97:
	l32i.n	a3, a2, 24	# _this_29(D)->offs, _68
	l32i.n	a5, a2, 8	# _this_29(D)->end_offs, _this_29(D)->end_offs
	l32i.n	a12, a2, 4	# _this_29(D)->storage, _this_29(D)->storage
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a11, a11, a8	# _67, carry, tmp112
.L102:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a14, a3, a5	# tmp120, _68, _this_29(D)->end_offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a13, a3, 1	# tmp123, _68,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a14, a12, .L99	# tmp120, _this_29(D)->storage,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a4, a2, 0	# _this_29(D)->buf, _72
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a13, a2, 24	# _this_29(D)->offs, tmp123
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a3, a4, a3	# tmp124, _72, _68
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a11, a3, 0	# *_74, _67
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a4, a2, 36	# _this_29(D)->ext, _this_29(D)->ext
	addi.n	a4, a4, -1	# _164, _this_29(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_29(D)->ext, _164
	beqz.n	a4, .L101	# _164,
	l32i.n	a3, a2, 24	# _this_29(D)->offs, _68
	l32i.n	a5, a2, 8	# _this_29(D)->end_offs, _this_29(D)->end_offs
	l32i.n	a12, a2, 4	# _this_29(D)->storage, _this_29(D)->storage
	j	.L102		#
.L99:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a4, a4, -1	# _164, _164,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a10, a2, 44	# _this_29(D)->error, tmp141
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a4, a2, 36	# _this_29(D)->ext, _164
	bnez.n	a4, .L102	# _164,
	j	.L101		#
.L94:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a4, a2, 36	# _this_29(D)->ext, _this_29(D)->ext
	addi.n	a4, a4, 1	# tmp127, _this_29(D)->ext,
	s32i.n	a4, a2, 36	# _this_29(D)->ext, tmp127
.L98:
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	l32i.n	a4, a2, 28	# _this_29(D)->rng, _this_29(D)->rng
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	l32i.n	a5, a2, 20	# _this_29(D)->nbits_total, _this_29(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a3, a3, 8	# tmp129, _45,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a3, a3, a9	# _45, tmp129, tmp138
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	slli	a4, a4, 8	# _47, _this_29(D)->rng,
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	addi.n	a5, a5, 8	# tmp132, _this_29(D)->nbits_total,
# @OPUS@\upstream\celt\entenc.c:106:     _this->val=(_this->val<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	s32i.n	a3, a2, 32	# _this_29(D)->val, _45
# @OPUS@\upstream\celt\entenc.c:107:     _this->rng<<=EC_SYM_BITS;
	s32i.n	a4, a2, 28	# _this_29(D)->rng, _47
# @OPUS@\upstream\celt\entenc.c:108:     _this->nbits_total+=EC_SYM_BITS;
	s32i.n	a5, a2, 20	# _this_29(D)->nbits_total, tmp132
# @OPUS@\upstream\celt\entenc.c:103:   while(_this->rng<=EC_CODE_BOT){
	bgeu	a7, a4, .L103	# tmp135, _47,
.L90:
# @OPUS@\upstream\celt\entenc.c:184: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_enc_icdf16, .-ec_enc_icdf16
	.section	.text.ec_enc_uint,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_enc_uint
	.type	ec_enc_uint, @function
# Function: ec_enc_uint
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ec_enc_normalize(_this);
# C context: }
# C context:
# C context: void ec_enc_uint(ec_enc *_this,opus_uint32 _fl,opus_uint32 _ft){
# C context: unsigned  ft;
# C context: unsigned  fl;
# C context: int       ftb;
# C context: /*In order to optimize EC_ILOG(), it is undefined for the value 0.*/
ec_enc_uint:
	addi	sp, sp, -32	#,,
# @OPUS@\upstream\celt\entenc.c:192:   _ft--;
	addi.n	a6, a4, -1	# _ft, _ft,
# @OPUS@\upstream\celt\entenc.c:186: void ec_enc_uint(ec_enc *_this,opus_uint32 _fl,opus_uint32 _ft){
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\celt\entenc.c:193:   ftb=EC_ILOG(_ft);
	nsau	a5, a6	# _1, _ft
# @OPUS@\upstream\celt\entenc.c:193:   ftb=EC_ILOG(_ft);
	movi.n	a15, 0x20	# tmp79,
# @OPUS@\upstream\celt\entenc.c:186: void ec_enc_uint(ec_enc *_this,opus_uint32 _fl,opus_uint32 _ft){
	s32i.n	a12, sp, 24	#,
	s32i.n	a13, sp, 20	#,
	s32i.n	a0, sp, 28	#,
	s32i.n	a14, sp, 16	#,
# @OPUS@\upstream\celt\entenc.c:193:   ftb=EC_ILOG(_ft);
	sub	a7, a15, a5	# ftb, tmp79, _1
# @OPUS@\upstream\celt\entenc.c:194:   if(ftb>EC_UINT_BITS){
	movi.n	a8, 8	# tmp81,
# @OPUS@\upstream\celt\entenc.c:186: void ec_enc_uint(ec_enc *_this,opus_uint32 _fl,opus_uint32 _ft){
	mov.n	a12, a2	# _this, _this
	mov.n	a13, a3	# _fl, _fl
# @OPUS@\upstream\celt\entenc.c:194:   if(ftb>EC_UINT_BITS){
	bge	a8, a7, .L112	# tmp81, ftb,
# @OPUS@\upstream\celt\entenc.c:195:     ftb-=EC_UINT_BITS;
	movi.n	a14, 0x18	# tmp82,
	sub	a14, a14, a5	# ftb, tmp82, _1
# @OPUS@\upstream\celt\entenc.c:197:     fl=(unsigned)(_fl>>ftb);
	ssr	a14	# ftb
	srl	a3, a3	# fl, _fl
# @OPUS@\upstream\celt\entenc.c:196:     ft=(_ft>>ftb)+1;
	ssr	a14	# ftb
	srl	a5, a6	# tmp83, _ft
# @OPUS@\upstream\celt\entenc.c:198:     ec_encode(_this,fl,fl+1,ft);
	addi.n	a4, a3, 1	#, fl,
	addi.n	a5, a5, 1	#, tmp83,
	call0	ec_encode		#
# @OPUS@\upstream\celt\entenc.c:199:     ec_enc_bits(_this,_fl&(((opus_uint32)1<<ftb)-1U),ftb);
	movi.n	a2, -1	# tmp86,
# @OPUS@\upstream\celt\entenc.c:208:   used=_this->nend_bits;
	l32i.n	a3, a12, 16	# _this_17(D)->nend_bits, used
# @OPUS@\upstream\celt\entenc.c:199:     ec_enc_bits(_this,_fl&(((opus_uint32)1<<ftb)-1U),ftb);
	ssl	a14	# ftb
	sll	a4, a2	# tmp87, tmp86
	xor	a4, a2, a4	# tmp88, tmp86, tmp87
# @OPUS@\upstream\celt\entenc.c:210:   if(used+_bits>EC_WINDOW_SIZE){
	add.n	a5, a3, a14	# _25, used, ftb
# @OPUS@\upstream\celt\entenc.c:199:     ec_enc_bits(_this,_fl&(((opus_uint32)1<<ftb)-1U),ftb);
	and	a13, a4, a13	# _4, tmp88, _fl
# @OPUS@\upstream\celt\entenc.c:207:   window=_this->end_window;
	l32i.n	a6, a12, 12	# _this_17(D)->end_window, window
# @OPUS@\upstream\celt\entenc.c:210:   if(used+_bits>EC_WINDOW_SIZE){
	bgeu	a15, a5, .L113	# tmp79, _25,
	l32i.n	a5, a12, 8	# _this_17(D)->end_offs, _27
	l32i.n	a4, a12, 4	# _this_17(D)->storage, _29
	l32i.n	a8, a12, 24	# _this_17(D)->offs, _this_17(D)->offs
# @OPUS@\upstream\celt\entenc.c:212:       _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	mov.n	a9, a2	# tmp104, tmp86
.L117:
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	addi.n	a7, a5, 1	# _31, _27,
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a2, a5, a8	# tmp91, _27, _this_17(D)->offs
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	sub	a10, a4, a7	# tmp93, _29, _31
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a2, a4, .L114	# tmp91, _29,
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	l32i.n	a2, a12, 0	# _this_17(D)->buf, _30
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s32i.n	a7, a12, 8	# _this_17(D)->end_offs, _31
	add.n	a2, a2, a10	# tmp94, _30, tmp93
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s8i	a6, a2, 0	# *_33, window
# @OPUS@\upstream\celt\entenc.c:214:       used-=EC_SYM_BITS;
	addi	a3, a3, -8	# used, used,
# @OPUS@\upstream\celt\entenc.c:213:       window>>=EC_SYM_BITS;
	srli	a6, a6, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:216:     while(used>=EC_SYM_BITS);
	blti	a3, 8, .L116	# used,,
	l32i.n	a5, a12, 8	# _this_17(D)->end_offs, _27
	l32i.n	a4, a12, 4	# _this_17(D)->storage, _29
	l32i.n	a8, a12, 24	# _this_17(D)->offs, _this_17(D)->offs
	j	.L117		#
.L114:
# @OPUS@\upstream\celt\entenc.c:212:       _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	s32i.n	a9, a12, 44	# _this_17(D)->error, tmp104
# @OPUS@\upstream\celt\entenc.c:214:       used-=EC_SYM_BITS;
	addi	a3, a3, -8	# used, used,
# @OPUS@\upstream\celt\entenc.c:213:       window>>=EC_SYM_BITS;
	srli	a6, a6, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:216:     while(used>=EC_SYM_BITS);
	bgei	a3, 8, .L117	# used,,
.L116:
	add.n	a5, a3, a14	# _25, used, ftb
.L113:
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	l32i.n	a2, a12, 20	# _this_17(D)->nbits_total, _this_17(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:218:   window|=(ec_window)_fl<<used;
	ssl	a3	# used
	sll	a13, a13	# tmp96, _4
# @OPUS@\upstream\celt\entenc.c:218:   window|=(ec_window)_fl<<used;
	or	a13, a13, a6	# window, tmp96, window
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	add.n	a14, a2, a14	# tmp98, _this_17(D)->nbits_total, ftb
# @OPUS@\upstream\celt\entenc.c:220:   _this->end_window=window;
	s32i.n	a13, a12, 12	# _this_17(D)->end_window, window
# @OPUS@\upstream\celt\entenc.c:221:   _this->nend_bits=used;
	s32i.n	a5, a12, 16	# _this_17(D)->nend_bits, _25
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	s32i.n	a14, a12, 20	# _this_17(D)->nbits_total, tmp98
	j	.L111		#
.L112:
# @OPUS@\upstream\celt\entenc.c:201:   else ec_encode(_this,_fl,_fl+1,_ft+1);
	mov.n	a5, a4	#, _ft
	addi.n	a4, a3, 1	#, _fl,
	call0	ec_encode		#
.L111:
# @OPUS@\upstream\celt\entenc.c:202: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	ec_enc_uint, .-ec_enc_uint
	.section	.text.ec_enc_bits,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_enc_bits
	.type	ec_enc_bits, @function
# Function: ec_enc_bits
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: ft=(_ft>>ftb)+1;
# C context: fl=(unsigned)(_fl>>ftb);
# C context: ec_encode(_this,fl,fl+1,ft);
# C context: ec_enc_bits(_this,_fl&(((opus_uint32)1<<ftb)-1U),ftb);
# C context: }
# C context: else ec_encode(_this,_fl,_fl+1,_ft+1);
# C context: }
# C context:
ec_enc_bits:
# @OPUS@\upstream\celt\entenc.c:208:   used=_this->nend_bits;
	l32i.n	a6, a2, 16	# _this_19(D)->nend_bits, used
# @OPUS@\upstream\celt\entenc.c:204: void ec_enc_bits(ec_enc *_this,opus_uint32 _fl,unsigned _bits){
	addi	sp, sp, -16	#,,
	s32i.n	a12, sp, 12	#,
	s32i.n	a13, sp, 8	#,
	s32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:210:   if(used+_bits>EC_WINDOW_SIZE){
	add.n	a8, a6, a4	# _2, used, _bits
# @OPUS@\upstream\celt\entenc.c:210:   if(used+_bits>EC_WINDOW_SIZE){
	movi.n	a5, 0x20	# tmp66,
# @OPUS@\upstream\celt\entenc.c:207:   window=_this->end_window;
	l32i.n	a7, a2, 12	# _this_19(D)->end_window, window
# @OPUS@\upstream\celt\entenc.c:210:   if(used+_bits>EC_WINDOW_SIZE){
	bgeu	a5, a8, .L121	# tmp66, _2,
	l32i.n	a9, a2, 8	# _this_19(D)->end_offs, _33
	l32i.n	a8, a2, 4	# _this_19(D)->storage, _35
	l32i.n	a12, a2, 24	# _this_19(D)->offs, _this_19(D)->offs
# @OPUS@\upstream\celt\entenc.c:212:       _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	movi.n	a14, -1	# tmp79,
.L125:
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	addi.n	a10, a9, 1	# _37, _33,
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a11, a9, a12	# tmp67, _33, _this_19(D)->offs
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	sub	a13, a8, a10	# tmp69, _35, _37
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a11, a8, .L122	# tmp67, _35,
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	l32i.n	a5, a2, 0	# _this_19(D)->buf, _36
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s32i.n	a10, a2, 8	# _this_19(D)->end_offs, _37
	add.n	a5, a5, a13	# tmp70, _36, tmp69
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s8i	a7, a5, 0	# *_39, window
# @OPUS@\upstream\celt\entenc.c:214:       used-=EC_SYM_BITS;
	addi	a6, a6, -8	# used, used,
# @OPUS@\upstream\celt\entenc.c:213:       window>>=EC_SYM_BITS;
	srli	a7, a7, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:216:     while(used>=EC_SYM_BITS);
	blti	a6, 8, .L124	# used,,
	l32i.n	a9, a2, 8	# _this_19(D)->end_offs, _33
	l32i.n	a8, a2, 4	# _this_19(D)->storage, _35
	l32i.n	a12, a2, 24	# _this_19(D)->offs, _this_19(D)->offs
	j	.L125		#
.L122:
# @OPUS@\upstream\celt\entenc.c:212:       _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	s32i.n	a14, a2, 44	# _this_19(D)->error, tmp79
# @OPUS@\upstream\celt\entenc.c:214:       used-=EC_SYM_BITS;
	addi	a6, a6, -8	# used, used,
# @OPUS@\upstream\celt\entenc.c:213:       window>>=EC_SYM_BITS;
	srli	a7, a7, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:216:     while(used>=EC_SYM_BITS);
	bgei	a6, 8, .L125	# used,,
.L124:
	add.n	a8, a6, a4	# _2, used, _bits
.L121:
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	l32i.n	a5, a2, 20	# _this_19(D)->nbits_total, _this_19(D)->nbits_total
# @OPUS@\upstream\celt\entenc.c:218:   window|=(ec_window)_fl<<used;
	ssl	a6	# used
	sll	a6, a3	# tmp72, _fl
# @OPUS@\upstream\celt\entenc.c:218:   window|=(ec_window)_fl<<used;
	or	a7, a6, a7	# window, tmp72, window
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	add.n	a4, a5, a4	# tmp74, _this_19(D)->nbits_total, _bits
# @OPUS@\upstream\celt\entenc.c:223: }
	l32i.n	a12, sp, 12	#,
	l32i.n	a13, sp, 8	#,
	l32i.n	a14, sp, 4	#,
# @OPUS@\upstream\celt\entenc.c:220:   _this->end_window=window;
	s32i.n	a7, a2, 12	# _this_19(D)->end_window, window
# @OPUS@\upstream\celt\entenc.c:221:   _this->nend_bits=used;
	s32i.n	a8, a2, 16	# _this_19(D)->nend_bits, _2
# @OPUS@\upstream\celt\entenc.c:222:   _this->nbits_total+=_bits;
	s32i.n	a4, a2, 20	# _this_19(D)->nbits_total, tmp74
# @OPUS@\upstream\celt\entenc.c:223: }
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_enc_bits, .-ec_enc_bits
	.section	.text.ec_enc_patch_initial_bits,"ax",@progbits
	.literal_position
	.literal .LC11, -2147483648
	.align	4
	.global	ec_enc_patch_initial_bits
	.type	ec_enc_patch_initial_bits, @function
# Function: ec_enc_patch_initial_bits
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: _this->nbits_total+=_bits;
# C context: }
# C context:
# C context: void ec_enc_patch_initial_bits(ec_enc *_this,unsigned _val,unsigned _nbits){
# C context: int      shift;
# C context: unsigned mask;
# C context: celt_assert(_nbits<=EC_SYM_BITS);
# C context: shift=EC_SYM_BITS-_nbits;
ec_enc_patch_initial_bits:
# @OPUS@\upstream\celt\entenc.c:230:   mask=((1<<_nbits)-1)<<shift;
	movi.n	a5, 1	# tmp77,
	ssl	a4	# _nbits
	sll	a5, a5	# tmp78, tmp77
# @OPUS@\upstream\celt\entenc.c:229:   shift=EC_SYM_BITS-_nbits;
	movi.n	a8, 8	# tmp76,
# @OPUS@\upstream\celt\entenc.c:231:   if(_this->offs>0){
	l32i.n	a7, a2, 24	# _this_35(D)->offs, _this_35(D)->offs
# @OPUS@\upstream\celt\entenc.c:229:   shift=EC_SYM_BITS-_nbits;
	sub	a8, a8, a4	# shift, tmp76, _nbits
# @OPUS@\upstream\celt\entenc.c:230:   mask=((1<<_nbits)-1)<<shift;
	addi.n	a5, a5, -1	# tmp79, tmp78,
# @OPUS@\upstream\celt\entenc.c:230:   mask=((1<<_nbits)-1)<<shift;
	ssl	a8	# shift
	sll	a5, a5	# _4, tmp79
# @OPUS@\upstream\celt\entenc.c:231:   if(_this->offs>0){
	beqz.n	a7, .L128	# _this_35(D)->offs,
# @OPUS@\upstream\celt\entenc.c:233:     _this->buf[0]=(unsigned char)((_this->buf[0]&~mask)|_val<<shift);
	l32i.n	a7, a2, 0	# _this_35(D)->buf, _6
# @OPUS@\upstream\celt\entenc.c:233:     _this->buf[0]=(unsigned char)((_this->buf[0]&~mask)|_val<<shift);
	movi.n	a2, -1	# tmp83,
	l8ui	a4, a7, 0	# *_6,
	xor	a5, a2, a5	# tmp82, tmp83, _4
	and	a5, a5, a4	# tmp86, tmp82, *_6
# @OPUS@\upstream\celt\entenc.c:233:     _this->buf[0]=(unsigned char)((_this->buf[0]&~mask)|_val<<shift);
	ssl	a8	# shift
	sll	a4, a3	# tmp87, _val
# @OPUS@\upstream\celt\entenc.c:233:     _this->buf[0]=(unsigned char)((_this->buf[0]&~mask)|_val<<shift);
	or	a5, a5, a4	# tmp90, tmp86, tmp87
# @OPUS@\upstream\celt\entenc.c:233:     _this->buf[0]=(unsigned char)((_this->buf[0]&~mask)|_val<<shift);
	s8i	a5, a7, 0	# *_6, tmp90
	j	.L127		#
.L128:
# @OPUS@\upstream\celt\entenc.c:235:   else if(_this->rem>=0){
	l32i.n	a7, a2, 40	# _this_35(D)->rem, _14
# @OPUS@\upstream\celt\entenc.c:235:   else if(_this->rem>=0){
	bltz	a7, .L130	# _14,
# @OPUS@\upstream\celt\entenc.c:237:     _this->rem=(_this->rem&~mask)|_val<<shift;
	movi.n	a6, -1	# tmp92,
	xor	a5, a6, a5	# tmp91, tmp92, _4
# @OPUS@\upstream\celt\entenc.c:237:     _this->rem=(_this->rem&~mask)|_val<<shift;
	and	a6, a5, a7	# tmp93, tmp91, _14
# @OPUS@\upstream\celt\entenc.c:237:     _this->rem=(_this->rem&~mask)|_val<<shift;
	ssl	a8	# shift
	sll	a4, a3	# tmp94, _val
# @OPUS@\upstream\celt\entenc.c:237:     _this->rem=(_this->rem&~mask)|_val<<shift;
	or	a6, a6, a4	# tmp95, tmp93, tmp94
# @OPUS@\upstream\celt\entenc.c:237:     _this->rem=(_this->rem&~mask)|_val<<shift;
	s32i.n	a6, a2, 40	# _this_35(D)->rem, tmp95
	j	.L127		#
.L130:
# @OPUS@\upstream\celt\entenc.c:239:   else if(_this->rng<=(EC_CODE_TOP>>_nbits)){
	l32r	a6, .LC11	#, tmp97
# @OPUS@\upstream\celt\entenc.c:239:   else if(_this->rng<=(EC_CODE_TOP>>_nbits)){
	l32i.n	a7, a2, 28	# _this_35(D)->rng, _this_35(D)->rng
# @OPUS@\upstream\celt\entenc.c:239:   else if(_this->rng<=(EC_CODE_TOP>>_nbits)){
	ssr	a4	# _nbits
	srl	a4, a6	# tmp96, tmp97
# @OPUS@\upstream\celt\entenc.c:239:   else if(_this->rng<=(EC_CODE_TOP>>_nbits)){
	bltu	a4, a7, .L131	# tmp96, _this_35(D)->rng,
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	l32i.n	a6, a2, 32	# _this_35(D)->val, _this_35(D)->val
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	slli	a7, a5, 23	# tmp99, _4,
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	movi.n	a5, -1	# tmp101,
	xor	a5, a5, a7	# tmp100, tmp101, tmp99
# @OPUS@\upstream\celt\entenc.c:242:      (opus_uint32)_val<<(EC_CODE_SHIFT+shift);
	addi	a4, a8, 23	# tmp104, shift,
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	and	a5, a5, a6	# tmp102, tmp100, _this_35(D)->val
# @OPUS@\upstream\celt\entenc.c:242:      (opus_uint32)_val<<(EC_CODE_SHIFT+shift);
	ssl	a4	# tmp104
	sll	a4, a3	# tmp105, _val
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	or	a4, a5, a4	# tmp106, tmp102, tmp105
# @OPUS@\upstream\celt\entenc.c:241:     _this->val=(_this->val&~((opus_uint32)mask<<EC_CODE_SHIFT))|
	s32i.n	a4, a2, 32	# _this_35(D)->val, tmp106
	j	.L127		#
.L131:
# @OPUS@\upstream\celt\entenc.c:245:   else _this->error=-1;
	movi.n	a3, -1	# tmp107,
	s32i.n	a3, a2, 44	# _this_35(D)->error, tmp107
.L127:
# @OPUS@\upstream\celt\entenc.c:246: }
	ret.n
	.size	ec_enc_patch_initial_bits, .-ec_enc_patch_initial_bits
	.section	.text.ec_enc_shrink,"ax",@progbits
	.literal_position
	.align	4
	.global	ec_enc_shrink
	.type	ec_enc_shrink, @function
# Function: ec_enc_shrink
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: else _this->error=-1;
# C context: }
# C context:
# C context: void ec_enc_shrink(ec_enc *_this,opus_uint32 _size){
# C context: celt_assert(_this->offs+_this->end_offs<=_size);
# C context: OPUS_MOVE(_this->buf+_size-_this->end_offs,
# C context: _this->buf+_this->storage-_this->end_offs,_this->end_offs);
# C context: _this->storage=_size;
ec_enc_shrink:
	addi	sp, sp, -16	#,,
# @OPUS@\upstream\celt\entenc.c:250:   OPUS_MOVE(_this->buf+_size-_this->end_offs,
	l32i.n	a4, a2, 8	# _this_9(D)->end_offs, _2
	l32i.n	a5, a2, 4	# _this_9(D)->storage, _this_9(D)->storage
# @OPUS@\upstream\celt\entenc.c:248: void ec_enc_shrink(ec_enc *_this,opus_uint32 _size){
	s32i.n	a12, sp, 8	#,
	s32i.n	a13, sp, 4	#,
	mov.n	a12, a2	# _this, _this
	mov.n	a13, a3	# _size, _size
# @OPUS@\upstream\celt\entenc.c:250:   OPUS_MOVE(_this->buf+_size-_this->end_offs,
	l32i.n	a2, a2, 0	# _this_9(D)->buf, _1
	sub	a3, a5, a4	# tmp51, _this_9(D)->storage, _2
	sub	a6, a13, a4	# tmp54, _size, _2
	add.n	a3, a2, a3	#, _1, tmp51
	movi.n	a5, 1	#,
	add.n	a2, a2, a6	#, _1, tmp54
# @OPUS@\upstream\celt\entenc.c:248: void ec_enc_shrink(ec_enc *_this,opus_uint32 _size){
	s32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\entenc.c:250:   OPUS_MOVE(_this->buf+_size-_this->end_offs,
	call0	yoradio_opus_copy		#
# @OPUS@\upstream\celt\entenc.c:253: }
	l32i.n	a0, sp, 12	#,
# @OPUS@\upstream\celt\entenc.c:252:   _this->storage=_size;
	s32i.n	a13, a12, 4	# _this_9(D)->storage, _size
# @OPUS@\upstream\celt\entenc.c:253: }
	l32i.n	a12, sp, 8	#,
	l32i.n	a13, sp, 4	#,
	addi	sp, sp, 16	#,,
	ret.n
	.size	ec_enc_shrink, .-ec_enc_shrink
	.section	.text.ec_enc_done,"ax",@progbits
	.literal_position
	.literal .LC12, 2147483647
	.align	4
	.global	ec_enc_done
	.type	ec_enc_done, @function
# Function: ec_enc_done
# Module: upstream/celt/entenc.c
# Fixed-point Opus CELT/support processing; see C source context below.
# ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).
# Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.
# GCC-specialized clones may remove/reorder arguments: use annotated operands below.
# Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.
# C context: _this->storage=_size;
# C context: }
# C context:
# C context: void ec_enc_done(ec_enc *_this){
# C context: ec_window   window;
# C context: int         used;
# C context: opus_uint32 msk;
# C context: opus_uint32 end;
ec_enc_done:
# @OPUS@\upstream\celt\entenc.c:263:   l=EC_CODE_BITS-EC_ILOG(_this->rng);
	l32i.n	a3, a2, 28	# _this_52(D)->rng, _1
# @OPUS@\upstream\celt\entenc.c:255: void ec_enc_done(ec_enc *_this){
	addi	sp, sp, -32	#,,
# @OPUS@\upstream\celt\entenc.c:264:   msk=(EC_CODE_TOP-1)>>l;
	l32r	a10, .LC12	#, tmp231
# @OPUS@\upstream\celt\entenc.c:265:   end=(_this->val+msk)&~msk;
	l32i.n	a6, a2, 32	# _this_52(D)->val, _2
# @OPUS@\upstream\celt\entenc.c:255: void ec_enc_done(ec_enc *_this){
	s32i.n	a13, sp, 20	#,
# @OPUS@\upstream\celt\entenc.c:263:   l=EC_CODE_BITS-EC_ILOG(_this->rng);
	nsau	a13, a3	# l, _1
# @OPUS@\upstream\celt\entenc.c:255: void ec_enc_done(ec_enc *_this){
	s32i.n	a12, sp, 24	#,
	mov.n	a12, a2	# _this, _this
# @OPUS@\upstream\celt\entenc.c:264:   msk=(EC_CODE_TOP-1)>>l;
	ssr	a13	# l
	srl	a2, a10	# msk, tmp231
# @OPUS@\upstream\celt\entenc.c:265:   end=(_this->val+msk)&~msk;
	add.n	a4, a6, a2	# _3, _2, msk
# @OPUS@\upstream\celt\entenc.c:255: void ec_enc_done(ec_enc *_this){
	s32i.n	a0, sp, 28	#,
	s32i.n	a14, sp, 16	#,
	s32i.n	a15, sp, 12	#,
# @OPUS@\upstream\celt\entenc.c:266:   if((end|msk)>=_this->val+_this->rng){
	or	a7, a4, a2	# tmp151, _3, msk
# @OPUS@\upstream\celt\entenc.c:266:   if((end|msk)>=_this->val+_this->rng){
	add.n	a3, a3, a6	# tmp152, _1, _2
	l32i.n	a5, a12, 40	# _this_52(D)->rem, prephitmp_265
# @OPUS@\upstream\celt\entenc.c:266:   if((end|msk)>=_this->val+_this->rng){
	bltu	a7, a3, .L134	# tmp151, tmp152,
# @OPUS@\upstream\celt\entenc.c:268:     msk>>=1;
	srli	a2, a2, 1	# msk, msk,
# @OPUS@\upstream\celt\entenc.c:269:     end=(_this->val+msk)&~msk;
	movi.n	a3, -1	# tmp155,
# @OPUS@\upstream\celt\entenc.c:269:     end=(_this->val+msk)&~msk;
	add.n	a6, a6, a2	# tmp153, _2, msk
# @OPUS@\upstream\celt\entenc.c:269:     end=(_this->val+msk)&~msk;
	xor	a2, a3, a2	# tmp154, tmp155, msk
# @OPUS@\upstream\celt\entenc.c:267:     l++;
	addi.n	a13, a13, 1	# l, l,
# @OPUS@\upstream\celt\entenc.c:269:     end=(_this->val+msk)&~msk;
	and	a6, a6, a2	# end, tmp153, tmp154
	j	.L135		#
.L134:
# @OPUS@\upstream\celt\entenc.c:271:   while(l>0){
	beqz.n	a13, .L136	# l,
# @OPUS@\upstream\celt\entenc.c:265:   end=(_this->val+msk)&~msk;
	movi.n	a6, -1	# tmp157,
	xor	a6, a6, a2	# tmp156, tmp157, msk
# @OPUS@\upstream\celt\entenc.c:265:   end=(_this->val+msk)&~msk;
	and	a6, a6, a4	# end, tmp156, _3
.L135:
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	movi	a9, 0xff	# tmp158,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a11, -1	# tmp237,
.L146:
# @OPUS@\upstream\celt\entenc.c:272:     ec_enc_carry_out(_this,(int)(end>>EC_CODE_SHIFT));
	extui	a8, a6, 23, 9	# _12, end,
# @OPUS@\upstream\celt\entenc.c:83:   if(_c!=EC_SYM_MAX){
	beq	a8, a9, .L137	# _12, tmp158,
# @OPUS@\upstream\celt\entenc.c:86:     carry=_c>>EC_SYM_BITS;
	srai	a7, a8, 8	# carry, _12,
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	bltz	a5, .L138	# prephitmp_265,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a3, a2, a3	# tmp159, _this_52(D)->offs, _77
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	add.n	a5, a7, a5	# _95, carry, prephitmp_265
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a3, a4, .L168	# tmp159, _79,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a3, a12, 0	# _this_52(D)->buf, _100
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a4, a2, 1	# tmp162, _this_52(D)->offs,
	s32i.n	a4, a12, 24	# _this_52(D)->offs, tmp162
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a3, a2	# tmp163, _100, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a5, a2, 0	# *_102, _95
	l32i.n	a2, a12, 44	# _this_52(D)->error, pretmp_276
	j	.L139		#
.L168:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	mov.n	a2, a11	# pretmp_276, tmp237
.L139:
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a2, a12, 44	# _this_52(D)->error, pretmp_276
.L138:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a5, a12, 36	# _this_52(D)->ext, _234
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a5, .L140	# _234,
.L144:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	extui	a5, a8, 0, 8	# prephitmp_265, _12,
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	s32i.n	a5, a12, 40	# _this_52(D)->rem, prephitmp_265
	j	.L141		#
.L140:
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
# @OPUS@\upstream\celt\entenc.c:92:       sym=(EC_SYM_MAX+carry)&EC_SYM_MAX;
	add.n	a7, a7, a9	# _109, carry, tmp158
.L145:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a15, a2, a3	# tmp165, _this_52(D)->offs, _77
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a14, a2, 1	# tmp168, _this_52(D)->offs,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a15, a4, .L142	# tmp165, _79,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a3, a12, 0	# _this_52(D)->buf, _114
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a14, a12, 24	# _this_52(D)->offs, tmp168
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a3, a2	# tmp169, _114, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a7, a2, 0	# *_116, _109
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	addi.n	a5, a5, -1	# _234, _this_52(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a5, a12, 36	# _this_52(D)->ext, _234
	beqz.n	a5, .L144	# _234,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
	j	.L145		#
.L142:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a5, a5, -1	# _234, _234,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a11, a12, 44	# _this_52(D)->error, tmp237
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a5, a12, 36	# _this_52(D)->ext, _234
	bnez.n	a5, .L145	# _234,
	j	.L144		#
.L137:
# @OPUS@\upstream\celt\entenc.c:98:   else _this->ext++;
	l32i.n	a2, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	addi.n	a2, a2, 1	# tmp172, _this_52(D)->ext,
	s32i.n	a2, a12, 36	# _this_52(D)->ext, tmp172
.L141:
# @OPUS@\upstream\celt\entenc.c:273:     end=(end<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	slli	a6, a6, 8	# _14, end,
# @OPUS@\upstream\celt\entenc.c:274:     l-=EC_SYM_BITS;
	addi	a13, a13, -8	# l, l,
# @OPUS@\upstream\celt\entenc.c:273:     end=(end<<EC_SYM_BITS)&(EC_CODE_TOP-1);
	and	a6, a6, a10	# end, _14, tmp231
# @OPUS@\upstream\celt\entenc.c:271:   while(l>0){
	bgei	a13, 1, .L146	# l,,
.L136:
# @OPUS@\upstream\celt\entenc.c:277:   if(_this->rem>=0||_this->ext>0)ec_enc_carry_out(_this,0);
	bgez	a5, .L147	# prephitmp_265,
# @OPUS@\upstream\celt\entenc.c:277:   if(_this->rem>=0||_this->ext>0)ec_enc_carry_out(_this,0);
	l32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	beqz.n	a5, .L148	# _this_52(D)->ext,
.L151:
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	movi.n	a9, -1	# tmp234,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	mov.n	a8, a9	# tmp235, tmp234
	j	.L149		#
.L147:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a3, a2, a3	# tmp176, _this_52(D)->offs, _77
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a3, a4, .L169	# tmp176, _79,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a3, a12, 0	# _this_52(D)->buf, _131
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a4, a2, 1	# tmp179, _this_52(D)->offs,
	s32i.n	a4, a12, 24	# _this_52(D)->offs, tmp179
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a3, a2	# tmp180, _131, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s8i	a5, a2, 0	# *_133, prephitmp_265
	l32i.n	a2, a12, 44	# _this_52(D)->error, pretmp_253
	j	.L150		#
.L169:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	movi.n	a2, -1	# pretmp_253,
.L150:
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	l32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
# @OPUS@\upstream\celt\entenc.c:89:     if(_this->rem>=0)_this->error|=ec_write_byte(_this,_this->rem+carry);
	s32i.n	a2, a12, 44	# _this_52(D)->error, pretmp_253
# @OPUS@\upstream\celt\entenc.c:90:     if(_this->ext>0){
	bnez.n	a5, .L151	# _this_52(D)->ext,
.L154:
# @OPUS@\upstream\celt\entenc.c:96:     _this->rem=_c&EC_SYM_MAX;
	movi.n	a2, 0	# tmp182,
	s32i.n	a2, a12, 40	# _this_52(D)->rem, tmp182
	j	.L148		#
.L149:
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a6, a2, a3	# tmp183, _this_52(D)->offs, _77
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	addi.n	a7, a2, 1	# tmp186, _this_52(D)->offs,
# @OPUS@\upstream\celt\entenc.c:61:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a6, a4, .L152	# tmp183, _79,
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	l32i.n	a3, a12, 0	# _this_52(D)->buf, _145
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	s32i.n	a7, a12, 24	# _this_52(D)->offs, tmp186
# @OPUS@\upstream\celt\entenc.c:62:   _this->buf[_this->offs++]=(unsigned char)_value;
	add.n	a2, a3, a2	# tmp187, _145, _this_52(D)->offs
	s8i	a8, a2, 0	# *_147, tmp235
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	l32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	addi.n	a5, a5, -1	# _this_52(D)->ext, _this_52(D)->ext,
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	beqz.n	a5, .L154	# _this_52(D)->ext,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
	j	.L149		#
.L152:
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	addi.n	a5, a5, -1	# _this_52(D)->ext, _this_52(D)->ext,
# @OPUS@\upstream\celt\entenc.c:93:       do _this->error|=ec_write_byte(_this,sym);
	s32i.n	a9, a12, 44	# _this_52(D)->error, tmp234
# @OPUS@\upstream\celt\entenc.c:94:       while(--(_this->ext)>0);
	s32i.n	a5, a12, 36	# _this_52(D)->ext, _this_52(D)->ext
	bnez.n	a5, .L149	# _this_52(D)->ext,
	j	.L154		#
.L148:
# @OPUS@\upstream\celt\entenc.c:280:   used=_this->nend_bits;
	l32i.n	a15, a12, 16	# _this_52(D)->nend_bits, used
# @OPUS@\upstream\celt\entenc.c:279:   window=_this->end_window;
	l32i.n	a14, a12, 12	# _this_52(D)->end_window, window
# @OPUS@\upstream\celt\entenc.c:281:   while(used>=EC_SYM_BITS){
	blti	a15, 8, .L155	# used,,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
	mov.n	a6, a15	# used, used
# @OPUS@\upstream\celt\entenc.c:282:     _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	movi.n	a9, -1	# tmp233,
.L159:
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	addi.n	a5, a3, 1	# _81, _77,
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	add.n	a7, a3, a2	# tmp192, _77, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	sub	a8, a4, a5	# tmp194, _79, _81
# @OPUS@\upstream\celt\entenc.c:67:   if(_this->offs+_this->end_offs>=_this->storage)return -1;
	bgeu	a7, a4, .L156	# tmp192, _79,
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	l32i.n	a2, a12, 0	# _this_52(D)->buf, _80
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s32i.n	a5, a12, 8	# _this_52(D)->end_offs, _81
	add.n	a2, a2, a8	# tmp195, _80, tmp194
# @OPUS@\upstream\celt\entenc.c:68:   _this->buf[_this->storage-++(_this->end_offs)]=(unsigned char)_value;
	s8i	a14, a2, 0	# *_83, window
# @OPUS@\upstream\celt\entenc.c:284:     used-=EC_SYM_BITS;
	addi	a6, a6, -8	# used, used,
	l32i.n	a2, a12, 44	# _this_52(D)->error, prephitmp_119
# @OPUS@\upstream\celt\entenc.c:283:     window>>=EC_SYM_BITS;
	srli	a14, a14, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:281:   while(used>=EC_SYM_BITS){
	blti	a6, 8, .L158	# used,,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _77
	l32i.n	a4, a12, 4	# _this_52(D)->storage, _79
	j	.L159		#
.L156:
# @OPUS@\upstream\celt\entenc.c:282:     _this->error|=ec_write_byte_at_end(_this,(unsigned)window&EC_SYM_MAX);
	s32i.n	a9, a12, 44	# _this_52(D)->error, tmp233
# @OPUS@\upstream\celt\entenc.c:284:     used-=EC_SYM_BITS;
	addi	a6, a6, -8	# used, used,
# @OPUS@\upstream\celt\entenc.c:283:     window>>=EC_SYM_BITS;
	srli	a14, a14, 8	# window, window,
# @OPUS@\upstream\celt\entenc.c:281:   while(used>=EC_SYM_BITS){
	bgei	a6, 8, .L159	# used,,
	movi.n	a2, -1	# prephitmp_119,
.L158:
	extui	a15, a15, 0, 3	# used, used,
	j	.L160		#
.L155:
	l32i.n	a2, a12, 44	# _this_52(D)->error, prephitmp_119
.L160:
# @OPUS@\upstream\celt\entenc.c:287:   if(!_this->error){
	bnez.n	a2, .L133	# prephitmp_119,
# @OPUS@\upstream\celt\entenc.c:288:     OPUS_CLEAR(_this->buf+_this->offs,
	l32i.n	a2, a12, 24	# _this_52(D)->offs, _21
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _this_52(D)->end_offs
	l32i.n	a6, a12, 4	# _this_52(D)->storage, _this_52(D)->storage
	l32i.n	a5, a12, 0	# _this_52(D)->buf, _this_52(D)->buf
	add.n	a3, a2, a3	# tmp203, _21, _this_52(D)->end_offs
	movi.n	a4, 1	#,
	sub	a3, a6, a3	#, _this_52(D)->storage, tmp203
	add.n	a2, a5, a2	#, _this_52(D)->buf, _21
	call0	yoradio_opus_clear		#
# @OPUS@\upstream\celt\entenc.c:290:     if(used>0){
	blti	a15, 1, .L133	# used,,
# @OPUS@\upstream\celt\entenc.c:292:       if(_this->end_offs>=_this->storage)_this->error=-1;
	l32i.n	a3, a12, 8	# _this_52(D)->end_offs, _27
# @OPUS@\upstream\celt\entenc.c:292:       if(_this->end_offs>=_this->storage)_this->error=-1;
	l32i.n	a2, a12, 4	# _this_52(D)->storage, _28
# @OPUS@\upstream\celt\entenc.c:292:       if(_this->end_offs>=_this->storage)_this->error=-1;
	bltu	a3, a2, .L164	# _27, _28,
# @OPUS@\upstream\celt\entenc.c:292:       if(_this->end_offs>=_this->storage)_this->error=-1;
	movi.n	a2, -1	# tmp209,
	s32i.n	a2, a12, 44	# _this_52(D)->error, tmp209
	j	.L133		#
.L164:
# @OPUS@\upstream\celt\entenc.c:297:         if(_this->offs+_this->end_offs>=_this->storage&&l<used){
	l32i.n	a4, a12, 24	# _this_52(D)->offs, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:294:         l=-l;
	neg	a13, a13	# l, l
# @OPUS@\upstream\celt\entenc.c:297:         if(_this->offs+_this->end_offs>=_this->storage&&l<used){
	add.n	a4, a3, a4	# tmp210, _27, _this_52(D)->offs
# @OPUS@\upstream\celt\entenc.c:297:         if(_this->offs+_this->end_offs>=_this->storage&&l<used){
	bltu	a4, a2, .L165	# tmp210, _28,
# @OPUS@\upstream\celt\entenc.c:297:         if(_this->offs+_this->end_offs>=_this->storage&&l<used){
	bge	a13, a15, .L165	# l, used,
# @OPUS@\upstream\celt\entenc.c:298:           window&=(1<<l)-1;
	movi.n	a4, 1	# tmp218,
	ssl	a13	# l
	sll	a13, a4	# tmp219, tmp218
# @OPUS@\upstream\celt\entenc.c:298:           window&=(1<<l)-1;
	addi.n	a4, a13, -1	# tmp220, tmp219,
# @OPUS@\upstream\celt\entenc.c:298:           window&=(1<<l)-1;
	and	a14, a14, a4	# window, window, tmp220
# @OPUS@\upstream\celt\entenc.c:299:           _this->error=-1;
	movi.n	a4, -1	# tmp221,
	s32i.n	a4, a12, 44	# _this_52(D)->error, tmp221
.L165:
# @OPUS@\upstream\celt\entenc.c:301:         _this->buf[_this->storage-_this->end_offs-1]|=(unsigned char)window;
	l32i.n	a4, a12, 0	# _this_52(D)->buf, _this_52(D)->buf
	addi.n	a2, a2, -1	# tmp222, _28,
	sub	a2, a2, a3	# tmp223, tmp222, _27
	add.n	a3, a4, a2	# _37, _this_52(D)->buf, tmp223
	l8ui	a2, a3, 0	# *_37,
	or	a2, a14, a2	# tmp227, window, *_37
	s8i	a2, a3, 0	# *_37, tmp227
.L133:
# @OPUS@\upstream\celt\entenc.c:305: }
	l32i.n	a0, sp, 28	#,
	l32i.n	a12, sp, 24	#,
	l32i.n	a13, sp, 20	#,
	l32i.n	a14, sp, 16	#,
	l32i.n	a15, sp, 12	#,
	addi	sp, sp, 32	#,,
	ret.n
	.size	ec_enc_done, .-ec_enc_done
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
