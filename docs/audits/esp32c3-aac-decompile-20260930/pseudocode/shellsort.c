/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: shellsort @ ram:4202aeb4
 * Types and parameter counts are inferred; verify against disassembly. */

void shellsort(int param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar7 = 1;
  do {
    iVar7 = iVar7 * 3 + 1;
  } while (iVar7 <= param_2);
  do {
    iVar2 = iVar7 / 3;
    iVar10 = iVar2 + 1;
    piVar9 = (int *)(param_1 + iVar2 * 4);
    if (iVar10 <= param_2) {
      do {
        iVar8 = *piVar9;
        piVar4 = piVar9;
        iVar5 = iVar10;
        piVar3 = piVar9 + -iVar2;
        do {
          piVar6 = piVar3;
          iVar5 = iVar5 - iVar2;
          if (*piVar6 <= iVar8) {
            *piVar4 = iVar8;
            goto joined_r0x4202af28;
          }
          *piVar4 = *piVar6;
          piVar4 = piVar4 + -iVar2;
          piVar3 = piVar6 + -iVar2;
        } while (iVar2 < iVar5);
        *piVar6 = iVar8;
joined_r0x4202af28:
        piVar9 = piVar9 + 1;
        iVar10 = iVar10 + 1;
      } while (iVar10 != param_2 + 1);
    }
    bVar1 = iVar7 < 6;
    iVar7 = iVar2;
    if (bVar1) {
      return;
    }
  } while( true );
}
