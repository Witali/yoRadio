/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_gsfb_table @ ram:43001760
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_gsfb_table(int param_1,int *param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int *piVar10;
  int *piVar11;

  gp = &__global_pointer_;
  piVar1 = (int *)memset(param_1 + 0x94,0,0x200);
  iVar4 = 0;
  piVar10 = (int *)(param_1 + 0x298);
  iVar7 = 0;
  do {
    iVar6 = iVar7;
    *piVar10 = *param_2 - iVar4;
    iVar4 = *param_2;
    iVar7 = iVar6 + 1;
    param_2 = param_2 + 1;
    piVar10 = piVar10 + 1;
  } while (iVar4 < 8);
  piVar11 = *(int **)(param_1 + 0x90);
  *(int *)(param_1 + 0x294) = iVar7;
  piVar10 = (int *)(param_1 + 0x30);
  iVar7 = 0;
  do {
    iVar4 = *piVar10;
    if (0 < iVar4) {
      iVar2 = piVar10[0x9a];
      iVar3 = iVar4;
      piVar5 = piVar11;
      piVar8 = piVar1;
      do {
        iVar9 = *piVar5;
        iVar3 = iVar3 + -1;
        piVar5 = piVar5 + 1;
        iVar7 = iVar7 + iVar2 * iVar9;
        *piVar8 = iVar7;
        piVar8 = piVar8 + 1;
      } while (iVar3 != 0);
      piVar1 = piVar1 + iVar4;
    }
    piVar10 = piVar10 + 1;
  } while (piVar10 != (int *)(param_1 + 0x34 + iVar6 * 4));
  return;
}
