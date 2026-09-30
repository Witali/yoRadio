/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_applied @ ram:42046dee
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_applied(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
               undefined4 param_5,undefined4 param_6)

{
  gp = &__global_pointer_;
  ps_hybrid_analysis(param_2,param_3,*(undefined4 *)(param_1 + 0x1ec),
                     *(undefined4 *)(param_1 + 0x1f0),*(undefined4 *)(param_1 + 0x1fc));
  ps_decorrelate(param_1,param_2,param_3,param_4,param_5,param_6);
  ps_stereo_processing(param_1,param_2,param_3,param_4,param_5);
  ps_hybrid_synthesis(*(undefined4 *)(param_1 + 0x1ec),*(undefined4 *)(param_1 + 0x1f0),param_2,
                      param_3,*(undefined4 *)(param_1 + 0x1fc));
  ps_hybrid_synthesis(*(undefined4 *)(param_1 + 500),*(undefined4 *)(param_1 + 0x1f8),param_4,
                      param_5,*(undefined4 *)(param_1 + 0x1fc));
  return;
}
