/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: cumSum.part.0 @ ram:43013914
 * Types and parameter counts are inferred; verify against disassembly. */

void cumSum_part_0(int param_1,int *param_2,uint param_3,int *param_4)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int *piVar6;

  gp = &__global_pointer_;
  *param_4 = param_1;
  iVar1 = (int)param_3 >> 1;
  piVar6 = param_4 + 1;
  piVar2 = piVar6;
  piVar3 = param_2;
  iVar4 = iVar1;
  if (iVar1 != 0) {
    do {
      iVar5 = *piVar3;
      *piVar2 = param_1 + iVar5;
      iVar4 = iVar4 + -1;
      param_1 = param_1 + iVar5 + piVar3[1];
      piVar2[1] = param_1;
      piVar2 = piVar2 + 2;
      piVar3 = piVar3 + 2;
    } while (iVar4 != 0);
    iVar1 = iVar1 + -1;
    piVar6 = piVar6 + iVar1 * 2 + 2;
    param_2 = param_2 + iVar1 * 2 + 2;
    param_4 = param_4 + iVar1 * 2 + 2;
  }
  if ((param_3 & 1) != 0) {
    *piVar6 = *param_4 + *param_2;
  }
  return;
}
