/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: set_mc_info @ ram:43013c92
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
set_mc_info(aac_analysis_mc_t *mc,int param_2,int param_3,int param_4,
           aac_analysis_window_t **window_map,int *param_6)

{
  int iVar1;
  undefined4 uVar2;

  gp = &__global_pointer_;
  if (mc->sample_rate_index == param_2) {
    mc->channel[0].tag = param_3;
    mc->channel[0].is_pair = param_4;
    mc->channels = param_4 + 1;
    if (param_4 != 0) {
      mc->channel[1].is_pair = 1;
    }
    return 0;
  }
  mc->sample_rate_index = param_2;
  iVar1 = infoinit(param_2,window_map,param_6);
  uVar2 = 1;
  if (iVar1 == 0) {
    mc->channel[0].tag = param_3;
    mc->channel[0].is_pair = param_4;
    mc->channels = param_4 + 1;
    if (param_4 != 0) {
      mc->channel[1].is_pair = 1;
    }
    uVar2 = 0;
  }
  return uVar2;
}
