/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: mapLowResEnergyVal @ ram:43011720
 * Types and parameter counts are inferred; verify against disassembly. */

void mapLowResEnergyVal(undefined4 param_1,int param_2,int param_3,int param_4,int param_5)

{
  undefined4 *puVar1;

  gp = &__global_pointer_;
  if (param_5 != 0) {
    *(undefined4 *)(param_2 + param_4 * 4) = param_1;
    return;
  }
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
