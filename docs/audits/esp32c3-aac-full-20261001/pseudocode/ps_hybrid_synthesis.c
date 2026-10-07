/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: ps_hybrid_synthesis @ ram:4300d696
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_hybrid_synthesis(int *param_1,int *param_2,int *param_3,int *param_4,int *param_5)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int iVar10;
  uint uVar11;
  int iVar12;

  gp = &__global_pointer_;
  if (*param_5 < 1) {
    return;
  }
  piVar7 = (int *)param_5[1];
  iVar6 = 0;
  do {
    iVar4 = *piVar7;
    iVar12 = *param_1 + param_1[1];
    piVar8 = param_1 + 2;
    iVar10 = *param_2 + param_2[1];
    piVar9 = param_2 + 2;
    if (6 < iVar4) {
      iVar4 = 6;
    }
    uVar5 = iVar4 - 2U >> 1;
    uVar11 = uVar5;
    if (uVar5 != 0) {
      do {
        iVar3 = *piVar8;
        iVar4 = *piVar9;
        uVar11 = uVar11 - 1;
        piVar1 = piVar8 + 1;
        piVar2 = piVar9 + 1;
        piVar8 = piVar8 + 2;
        piVar9 = piVar9 + 2;
        iVar12 = iVar3 + iVar12 + *piVar1;
        iVar10 = iVar10 + iVar4 + *piVar2;
      } while (uVar11 != 0);
      piVar9 = param_2 + (uVar5 - 1) * 2 + 4;
      piVar8 = param_1 + (uVar5 - 1) * 2 + 4;
    }
    *param_3 = iVar12;
    *param_4 = iVar10;
    iVar6 = iVar6 + 1;
    param_3 = param_3 + 1;
    param_4 = param_4 + 1;
    piVar7 = piVar7 + 1;
    param_1 = piVar8;
    param_2 = piVar9;
  } while (iVar6 < *param_5);
  return;
}
