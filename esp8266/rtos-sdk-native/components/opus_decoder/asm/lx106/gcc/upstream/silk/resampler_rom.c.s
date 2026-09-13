# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/resampler_rom.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"resampler_rom.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\resampler_rom.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\resampler_rom.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\resampler_rom.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\resampler_rom.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\resampler_rom.c.s.raw
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
	.global	silk_resampler_frac_FIR_12
	.section	.rodata.silk_resampler_frac_FIR_12,"a"
	.align	4
	.type	silk_resampler_frac_FIR_12, @object
	.size	silk_resampler_frac_FIR_12, 96
silk_resampler_frac_FIR_12:
	.short	189
	.short	-600
	.short	617
	.short	30567
	.short	117
	.short	-159
	.short	-1070
	.short	29704
	.short	52
	.short	221
	.short	-2392
	.short	28276
	.short	-4
	.short	529
	.short	-3350
	.short	26341
	.short	-48
	.short	758
	.short	-3956
	.short	23973
	.short	-80
	.short	905
	.short	-4235
	.short	21254
	.short	-99
	.short	972
	.short	-4222
	.short	18278
	.short	-107
	.short	967
	.short	-3957
	.short	15143
	.short	-103
	.short	896
	.short	-3487
	.short	11950
	.short	-91
	.short	773
	.short	-2865
	.short	8798
	.short	-71
	.short	611
	.short	-2143
	.short	5784
	.short	-46
	.short	425
	.short	-1375
	.short	2996
	.global	silk_Resampler_2_3_COEFS_LQ
	.section	.rodata.silk_Resampler_2_3_COEFS_LQ,"a"
	.align	4
	.type	silk_Resampler_2_3_COEFS_LQ, @object
	.size	silk_Resampler_2_3_COEFS_LQ, 12
silk_Resampler_2_3_COEFS_LQ:
	.short	-2797
	.short	-6507
	.short	4697
	.short	10739
	.short	1567
	.short	8276
	.global	silk_Resampler_1_6_COEFS
	.section	.rodata.silk_Resampler_1_6_COEFS,"a"
	.align	4
	.type	silk_Resampler_1_6_COEFS, @object
	.size	silk_Resampler_1_6_COEFS, 40
silk_Resampler_1_6_COEFS:
	.short	27540
	.short	-15257
	.short	17
	.short	12
	.short	8
	.short	1
	.short	-10
	.short	-22
	.short	-30
	.short	-32
	.short	-22
	.short	3
	.short	44
	.short	100
	.short	168
	.short	243
	.short	317
	.short	381
	.short	429
	.short	455
	.global	silk_Resampler_1_4_COEFS
	.section	.rodata.silk_Resampler_1_4_COEFS,"a"
	.align	4
	.type	silk_Resampler_1_4_COEFS, @object
	.size	silk_Resampler_1_4_COEFS, 40
silk_Resampler_1_4_COEFS:
	.short	22500
	.short	-15099
	.short	3
	.short	-14
	.short	-20
	.short	-15
	.short	2
	.short	25
	.short	37
	.short	25
	.short	-16
	.short	-71
	.short	-107
	.short	-79
	.short	50
	.short	292
	.short	623
	.short	982
	.short	1288
	.short	1464
	.global	silk_Resampler_1_3_COEFS
	.section	.rodata.silk_Resampler_1_3_COEFS,"a"
	.align	4
	.type	silk_Resampler_1_3_COEFS, @object
	.size	silk_Resampler_1_3_COEFS, 40
silk_Resampler_1_3_COEFS:
	.short	16102
	.short	-15162
	.short	-13
	.short	0
	.short	20
	.short	26
	.short	5
	.short	-31
	.short	-43
	.short	-4
	.short	65
	.short	90
	.short	7
	.short	-157
	.short	-248
	.short	-44
	.short	593
	.short	1583
	.short	2612
	.short	3271
	.global	silk_Resampler_1_2_COEFS
	.section	.rodata.silk_Resampler_1_2_COEFS,"a"
	.align	4
	.type	silk_Resampler_1_2_COEFS, @object
	.size	silk_Resampler_1_2_COEFS, 28
silk_Resampler_1_2_COEFS:
	.short	616
	.short	-14323
	.short	-10
	.short	39
	.short	58
	.short	-46
	.short	-84
	.short	120
	.short	184
	.short	-315
	.short	-541
	.short	1284
	.short	5380
	.short	9024
	.global	silk_Resampler_2_3_COEFS
	.section	.rodata.silk_Resampler_2_3_COEFS,"a"
	.align	4
	.type	silk_Resampler_2_3_COEFS, @object
	.size	silk_Resampler_2_3_COEFS, 40
silk_Resampler_2_3_COEFS:
	.short	-14457
	.short	-14019
	.short	64
	.short	128
	.short	-122
	.short	36
	.short	310
	.short	-768
	.short	584
	.short	9267
	.short	17733
	.short	12
	.short	128
	.short	18
	.short	-142
	.short	288
	.short	-117
	.short	-865
	.short	4123
	.short	14459
	.global	silk_Resampler_3_4_COEFS
	.section	.rodata.silk_Resampler_3_4_COEFS,"a"
	.align	4
	.type	silk_Resampler_3_4_COEFS, @object
	.size	silk_Resampler_3_4_COEFS, 58
silk_Resampler_3_4_COEFS:
	.short	-20694
	.short	-13867
	.short	-49
	.short	64
	.short	17
	.short	-157
	.short	353
	.short	-496
	.short	163
	.short	11047
	.short	22205
	.short	-39
	.short	6
	.short	91
	.short	-170
	.short	186
	.short	23
	.short	-896
	.short	6336
	.short	19928
	.short	-19
	.short	-36
	.short	102
	.short	-89
	.short	-24
	.short	328
	.short	-951
	.short	2568
	.short	15909
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
