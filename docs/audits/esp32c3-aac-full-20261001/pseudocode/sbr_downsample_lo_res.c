/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_downsample_lo_res @ ram:43011796
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_downsample_lo_res(undefined4 *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int local_74 [29];

  gp = &__global_pointer_;
  local_74[0] = 0;
  if (param_4 < 1) {
    iVar1 = 0;
  }
  else {
    piVar2 = local_74;
    iVar4 = 0;
    iVar1 = 0;
    do {
      piVar2 = piVar2 + 1;
      iVar3 = param_4 / (param_2 - iVar1);
      iVar1 = iVar1 + 1;
      iVar4 = iVar4 + iVar3;
      *piVar2 = iVar4;
      param_4 = param_4 - iVar3;
    } while (0 < param_4);
  }
  piVar2 = local_74;
  do {
    iVar4 = *piVar2;
    piVar2 = piVar2 + 1;
    *param_1 = *(undefined4 *)(iVar4 * 4 + param_3);
    param_1 = param_1 + 1;
  } while (piVar2 != local_74 + iVar1 + 1);
  return;
}
