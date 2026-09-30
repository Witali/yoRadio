/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: calc_sbr_anafilterbank_LC @ ram:42041a92
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_anafilterbank_LC(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  gp = &__global_pointer_;
  calc_sbr_anafilterbank_LC_core(param_2,param_3);
  analysis_sub_band_LC(param_3,param_1,param_4,param_3 + 0x100);
  return;
}
