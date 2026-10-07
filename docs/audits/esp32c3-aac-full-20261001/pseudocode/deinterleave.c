/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: deinterleave @ ram:430055e4
 * Types and parameter counts are inferred; verify against disassembly. */

void deinterleave(int param_1,int param_2,int param_3)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar5 = *(int *)(param_3 + 0x294);
  iVar9 = param_3;
  if (0 < iVar5) {
    do {
      iVar7 = *(int *)(iVar9 + 0x30);
      iVar10 = param_1;
      if (0 < iVar7) {
        piVar2 = *(int **)(param_3 + 0x90);
        iVar8 = 0;
        do {
          iVar1 = *(int *)(iVar9 + 0x298);
          iVar4 = *piVar2;
          if (0 < iVar1) {
            iVar3 = iVar4 << 1;
            iVar6 = iVar8 * 2 + param_2;
            do {
              iVar6 = memcpy(iVar6,iVar10,iVar3);
              iVar4 = *piVar2;
              iVar1 = iVar1 + -1;
              iVar6 = iVar6 + 0x100;
              iVar3 = iVar4 * 2;
              iVar10 = iVar10 + iVar3;
            } while (iVar1 != 0);
          }
          iVar7 = iVar7 + -1;
          piVar2 = piVar2 + 1;
          iVar8 = iVar8 + iVar4;
        } while (iVar7 != 0);
        param_2 = param_2 + (iVar10 - param_1);
      }
      iVar9 = iVar9 + 4;
      param_1 = iVar10;
    } while (iVar9 != iVar5 * 4 + param_3);
  }
  return;
}
