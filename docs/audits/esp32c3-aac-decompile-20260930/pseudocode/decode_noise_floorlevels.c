/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: decode_noise_floorlevels @ ram:42044128
 * Types and parameter counts are inferred; verify against disassembly. */

void decode_noise_floorlevels(int param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar5 = *(int *)(*(int *)(param_1 + 0x10) * 8 + param_1 + 0x1c);
  if (iVar5 < 1) {
    return;
  }
  iVar10 = *(int *)(param_1 + 0xa4);
  iVar1 = param_1 + iVar5 * 4;
  piVar7 = (int *)(param_1 + 0x1108);
  iVar5 = param_1;
LAB_ram_42044166:
  if (*(int *)(iVar5 + 0x114) != 0) {
    iVar2 = iVar5;
    if (0 < iVar10) goto LAB_ram_420441ac;
    do {
      if (iVar2 + 4 == iVar1) {
        return;
      }
      if (*(int *)(iVar2 + 0x118) == 0) {
        iVar5 = *piVar7;
        piVar7 = piVar7 + 1;
        *(int *)(param_1 + 0x1158) = iVar5;
      }
      if (iVar1 == iVar2 + 8) {
        return;
      }
      iVar5 = iVar2 + 8;
      piVar4 = (int *)(iVar2 + 0x11c);
      iVar2 = iVar5;
    } while (*piVar4 != 0);
  }
  do {
    *(int *)(param_1 + 0x1158) = *piVar7;
    piVar3 = piVar7 + 1;
    piVar4 = piVar7;
    iVar2 = iVar5;
    while( true ) {
      piVar7 = piVar3;
      if (iVar10 < 2) {
        iVar5 = iVar2 + 4;
        if (iVar5 == iVar1) {
          return;
        }
        goto LAB_ram_42044166;
      }
      piVar3 = (int *)(param_1 + 0x115c);
      piVar8 = piVar7;
      do {
        iVar5 = *piVar8;
        piVar9 = piVar8 + 1;
        *piVar8 = iVar5 + piVar8[-1];
        *piVar3 = iVar5 + piVar8[-1];
        piVar3 = piVar3 + 1;
        piVar8 = piVar9;
      } while (piVar9 != piVar4 + iVar10);
      iVar5 = iVar2 + 4;
      if (iVar5 == iVar1) {
        return;
      }
      piVar7 = piVar7 + iVar10 + -1;
      if (*(int *)(iVar2 + 0x118) == 0) break;
LAB_ram_420441ac:
      do {
        piVar3 = piVar7 + iVar10;
        piVar4 = (int *)(param_1 + 0x1158);
        do {
          piVar8 = piVar7;
          iVar6 = *piVar8;
          iVar2 = *piVar4;
          piVar7 = piVar8 + 1;
          *piVar8 = iVar6 + iVar2;
          *piVar4 = iVar6 + iVar2;
          piVar4 = piVar4 + 1;
        } while (piVar7 != piVar3);
        iVar2 = iVar5 + 4;
        if (iVar1 == iVar2) {
          return;
        }
        piVar4 = (int *)(iVar5 + 0x118);
        iVar5 = iVar2;
      } while (*piVar4 != 0);
      *(int *)(param_1 + 0x1158) = *piVar7;
      piVar3 = piVar8 + 2;
      piVar4 = piVar7;
    }
  } while( true );
}
