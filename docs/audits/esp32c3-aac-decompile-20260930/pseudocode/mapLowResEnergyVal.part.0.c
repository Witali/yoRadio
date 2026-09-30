/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: mapLowResEnergyVal.part.0 @ ram:420292ae
 * Types and parameter counts are inferred; verify against disassembly. */

void mapLowResEnergyVal_part_0(undefined4 param_1,int param_2,int param_3,int param_4)

{
  undefined4 *puVar1;

  gp = &__global_pointer_;
  if (param_3 < 0) {
    if (param_4 < -param_3) {
      puVar1 = (undefined4 *)(param_2 + param_4 * 0xc);
      *puVar1 = param_1;
      puVar1[1] = param_1;
      puVar1[2] = param_1;
      return;
    }
  }
  else if (param_4 < param_3) {
    *(undefined4 *)(param_2 + param_4 * 4) = param_1;
    return;
  }
  puVar1 = (undefined4 *)(param_2 + (param_4 * 2 - param_3) * 4);
  *puVar1 = param_1;
  puVar1[1] = param_1;
  return;
}
