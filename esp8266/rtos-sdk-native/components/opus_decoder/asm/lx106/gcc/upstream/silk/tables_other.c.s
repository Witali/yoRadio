# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.
# Origin: upstream/silk/tables_other.c; upstream licenses remain in upstream/COPYING and source headers.
# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.
	.file	"tables_other.c"
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
# -MMD @OPUS@\asm\lx106\gcc\upstream\silk\tables_other.c.s.d
# -MF @OPUS@\asm\lx106\gcc\upstream\silk\tables_other.c.s.raw.d
# -MQ @OPUS@\asm\lx106\gcc\upstream\silk\tables_other.c.s.raw
# -D USING_IBUS_FASTER_GET -D YORADIO_OPUS_BOUNDED=1
# -D YORADIO_OPUS_FIR_FLASH_WORD=1 -D YORADIO_OPUS_ICDF_FLASH_WORD=1
# -D YORADIO_OPUS_PROFILE_STAGE=0 -D YORADIO_OPUS_WORD_ASM=1
# -D __ESP_FILE__=__FILE__ -D _GNU_SOURCE -D IDF_VER="v3.4"
# -D GCC_NOT_5_2_0 -D ESP_PLATFORM
# @OPUS@\upstream\silk\tables_other.c
# -mlongcalls
# -auxbase-strip @OPUS@\asm\lx106\gcc\upstream\silk\tables_other.c.s.raw
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
	.global	silk_Transition_LP_A_Q28
	.section	.rodata.silk_Transition_LP_A_Q28,"a"
	.align	4
	.type	silk_Transition_LP_A_Q28, @object
	.size	silk_Transition_LP_A_Q28, 40
silk_Transition_LP_A_Q28:
	.word	506393414
	.word	239854379
	.word	411067935
	.word	169683996
	.word	306733530
	.word	116694253
	.word	185807084
	.word	77959395
	.word	35497197
	.word	57401098
	.global	silk_Transition_LP_B_Q28
	.section	.rodata.silk_Transition_LP_B_Q28,"a"
	.align	4
	.type	silk_Transition_LP_B_Q28, @object
	.size	silk_Transition_LP_B_Q28, 60
silk_Transition_LP_B_Q28:
	.word	250767114
	.word	501534038
	.word	250767114
	.word	209867381
	.word	419732057
	.word	209867381
	.word	170987846
	.word	341967853
	.word	170987846
	.word	131531482
	.word	263046905
	.word	131531482
	.word	89306658
	.word	178584282
	.word	89306658
	.global	silk_NLSF_EXT_iCDF
	.section	.rodata.silk_NLSF_EXT_iCDF,"a"
	.align	4
	.type	silk_NLSF_EXT_iCDF, @object
	.size	silk_NLSF_EXT_iCDF, 7
silk_NLSF_EXT_iCDF:
	.byte	100
	.byte	40
	.byte	16
	.byte	7
	.byte	3
	.byte	1
	.byte	0
	.global	silk_uniform8_iCDF
	.section	.rodata.silk_uniform8_iCDF,"a"
	.align	4
	.type	silk_uniform8_iCDF, @object
	.size	silk_uniform8_iCDF, 8
silk_uniform8_iCDF:
	.byte	-32
	.byte	-64
	.byte	-96
	.byte	-128
	.byte	96
	.byte	64
	.byte	32
	.byte	0
	.global	silk_uniform6_iCDF
	.section	.rodata.silk_uniform6_iCDF,"a"
	.align	4
	.type	silk_uniform6_iCDF, @object
	.size	silk_uniform6_iCDF, 6
silk_uniform6_iCDF:
	.byte	-43
	.byte	-85
	.byte	-128
	.byte	85
	.byte	43
	.byte	0
	.global	silk_uniform5_iCDF
	.section	.rodata.silk_uniform5_iCDF,"a"
	.align	4
	.type	silk_uniform5_iCDF, @object
	.size	silk_uniform5_iCDF, 5
silk_uniform5_iCDF:
	.byte	-51
	.byte	-102
	.byte	102
	.byte	51
	.byte	0
	.global	silk_uniform4_iCDF
	.section	.rodata.silk_uniform4_iCDF,"a"
	.align	4
	.type	silk_uniform4_iCDF, @object
	.size	silk_uniform4_iCDF, 4
silk_uniform4_iCDF:
	.byte	-64
	.byte	-128
	.byte	64
	.byte	0
	.global	silk_uniform3_iCDF
	.section	.rodata.silk_uniform3_iCDF,"a"
	.align	4
	.type	silk_uniform3_iCDF, @object
	.size	silk_uniform3_iCDF, 3
silk_uniform3_iCDF:
	.byte	-85
	.byte	85
	.byte	0
	.global	silk_LTPScales_table_Q14
	.section	.rodata.silk_LTPScales_table_Q14,"a"
	.align	4
	.type	silk_LTPScales_table_Q14, @object
	.size	silk_LTPScales_table_Q14, 6
silk_LTPScales_table_Q14:
	.short	15565
	.short	12288
	.short	8192
	.global	silk_Quantization_Offsets_Q10
	.section	.rodata.silk_Quantization_Offsets_Q10,"a"
	.align	4
	.type	silk_Quantization_Offsets_Q10, @object
	.size	silk_Quantization_Offsets_Q10, 8
silk_Quantization_Offsets_Q10:
	.short	100
	.short	240
	.short	32
	.short	100
	.global	silk_NLSF_interpolation_factor_iCDF
	.section	.rodata.silk_NLSF_interpolation_factor_iCDF,"a"
	.align	4
	.type	silk_NLSF_interpolation_factor_iCDF, @object
	.size	silk_NLSF_interpolation_factor_iCDF, 5
silk_NLSF_interpolation_factor_iCDF:
	.byte	-13
	.byte	-35
	.byte	-64
	.byte	-75
	.byte	0
	.global	silk_type_offset_no_VAD_iCDF
	.section	.rodata.silk_type_offset_no_VAD_iCDF,"a"
	.align	4
	.type	silk_type_offset_no_VAD_iCDF, @object
	.size	silk_type_offset_no_VAD_iCDF, 2
silk_type_offset_no_VAD_iCDF:
	.byte	-26
	.byte	0
	.global	silk_type_offset_VAD_iCDF
	.section	.rodata.silk_type_offset_VAD_iCDF,"a"
	.align	4
	.type	silk_type_offset_VAD_iCDF, @object
	.size	silk_type_offset_VAD_iCDF, 4
silk_type_offset_VAD_iCDF:
	.byte	-24
	.byte	-98
	.byte	10
	.byte	0
	.global	silk_LTPscale_iCDF
	.section	.rodata.silk_LTPscale_iCDF,"a"
	.align	4
	.type	silk_LTPscale_iCDF, @object
	.size	silk_LTPscale_iCDF, 3
silk_LTPscale_iCDF:
	.byte	-128
	.byte	64
	.byte	0
	.global	silk_lsb_iCDF
	.section	.rodata.silk_lsb_iCDF,"a"
	.align	4
	.type	silk_lsb_iCDF, @object
	.size	silk_lsb_iCDF, 2
silk_lsb_iCDF:
	.byte	120
	.byte	0
	.global	silk_LBRR_flags_iCDF_ptr
	.section	.rodata.silk_LBRR_flags_iCDF_ptr,"a"
	.align	4
	.type	silk_LBRR_flags_iCDF_ptr, @object
	.size	silk_LBRR_flags_iCDF_ptr, 8
silk_LBRR_flags_iCDF_ptr:
	.word	silk_LBRR_flags_2_iCDF
	.word	silk_LBRR_flags_3_iCDF
	.section	.rodata.silk_LBRR_flags_3_iCDF,"a"
	.align	4
	.type	silk_LBRR_flags_3_iCDF, @object
	.size	silk_LBRR_flags_3_iCDF, 7
silk_LBRR_flags_3_iCDF:
	.byte	-41
	.byte	-61
	.byte	-90
	.byte	125
	.byte	110
	.byte	82
	.byte	0
	.section	.rodata.silk_LBRR_flags_2_iCDF,"a"
	.align	4
	.type	silk_LBRR_flags_2_iCDF, @object
	.size	silk_LBRR_flags_2_iCDF, 3
silk_LBRR_flags_2_iCDF:
	.byte	-53
	.byte	-106
	.byte	0
	.global	silk_stereo_only_code_mid_iCDF
	.section	.rodata.silk_stereo_only_code_mid_iCDF,"a"
	.align	4
	.type	silk_stereo_only_code_mid_iCDF, @object
	.size	silk_stereo_only_code_mid_iCDF, 2
silk_stereo_only_code_mid_iCDF:
	.byte	64
	.byte	0
	.global	silk_stereo_pred_joint_iCDF
	.section	.rodata.silk_stereo_pred_joint_iCDF,"a"
	.align	4
	.type	silk_stereo_pred_joint_iCDF, @object
	.size	silk_stereo_pred_joint_iCDF, 25
silk_stereo_pred_joint_iCDF:
	.byte	-7
	.byte	-9
	.byte	-10
	.byte	-11
	.byte	-12
	.byte	-22
	.byte	-46
	.byte	-54
	.byte	-55
	.byte	-56
	.byte	-59
	.byte	-82
	.byte	82
	.byte	59
	.byte	56
	.byte	55
	.byte	54
	.byte	46
	.byte	22
	.byte	12
	.byte	11
	.byte	10
	.byte	9
	.byte	7
	.byte	0
	.global	silk_stereo_pred_quant_Q13
	.section	.rodata.silk_stereo_pred_quant_Q13,"a"
	.align	4
	.type	silk_stereo_pred_quant_Q13, @object
	.size	silk_stereo_pred_quant_Q13, 32
silk_stereo_pred_quant_Q13:
	.short	-13732
	.short	-10050
	.short	-8266
	.short	-7526
	.short	-6500
	.short	-5000
	.short	-2950
	.short	-820
	.short	820
	.short	2950
	.short	5000
	.short	6500
	.short	7526
	.short	8266
	.short	10050
	.short	13732
	.ident	"GCC: (crosstool-NG esp-2020r3-49-gd5524c1) 8.4.0"
