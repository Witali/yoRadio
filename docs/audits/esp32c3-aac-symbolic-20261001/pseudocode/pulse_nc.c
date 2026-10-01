/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: pulse_nc @ ram:4300e2d8
 * Types and parameter counts are inferred; verify against disassembly. */

void pulse_nc(short *param_1,int param_2,int param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;

  gp = &__global_pointer_;
  if (0 < *(int *)(param_2 + 8)) {
    param_1 = param_1 + *(short *)(*(int *)(param_2 + 8) * 2 + *(int *)(param_3 + 0x70) + -2);
  }
  iVar2 = *(int *)(param_2 + 4);
  piVar1 = (int *)(param_2 + 0xc);
  if (0 < iVar2) {
    do {
      iVar3 = *piVar1;
      iVar4 = piVar1[4];
      piVar1 = piVar1 + 1;
      param_1 = param_1 + iVar3;
      iVar3 = (int)*param_1;
      iVar6 = *param_4;
      iVar5 = iVar3 + iVar4;
      if (iVar3 < 1) {
        *param_1 = *param_1 - (short)iVar4;
        if (iVar6 < iVar4 - iVar3) {
          *param_4 = iVar4 - iVar3;
        }
      }
      else {
        *param_1 = (short)iVar5;
        if (iVar6 < iVar5) {
          *param_4 = iVar5;
        }
      }
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    return;
  }
  return;
}
