/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: set_mc_info @ ram:43013c92
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
set_mc_info(int *param_1,int param_2,int param_3,int param_4,undefined4 param_5,undefined4 param_6)

{
  int iVar1;
  undefined4 uVar2;

  gp = &__global_pointer_;
  if (param_1[7] == param_2) {
    param_1[0xe] = param_3;
    param_1[0xf] = param_4;
    *param_1 = param_4 + 1;
    if (param_4 != 0) {
      param_1[0x14] = 1;
    }
    return 0;
  }
  param_1[7] = param_2;
  iVar1 = infoinit(param_2,param_5,param_6);
  uVar2 = 1;
  if (iVar1 == 0) {
    param_1[0xe] = param_3;
    param_1[0xf] = param_4;
    *param_1 = param_4 + 1;
    if (param_4 != 0) {
      param_1[0x14] = 1;
    }
    uVar2 = 0;
  }
  return uVar2;
}
