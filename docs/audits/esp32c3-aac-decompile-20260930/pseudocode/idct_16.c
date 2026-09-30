/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: idct_16 @ ram:4205ca5e
 * Types and parameter counts are inferred; verify against disassembly. */

void idct_16(int *param_1,int *param_2)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int *piVar10;
  int iVar11;

  gp = &__global_pointer_;
  *param_2 = *param_1;
  *param_1 = param_1[1];
  iVar11 = param_1[1];
  piVar3 = param_1 + 1;
  piVar9 = param_2 + 1;
  piVar1 = param_1 + 2;
  do {
    piVar5 = piVar1;
    piVar2 = piVar9;
    piVar8 = piVar3;
    piVar9 = piVar2 + 2;
    *piVar2 = *piVar5;
    iVar4 = piVar5[1];
    piVar2[1] = piVar5[2];
    iVar6 = piVar5[3];
    *piVar8 = iVar11 + iVar4;
    piVar8[1] = iVar4 + iVar6;
    iVar11 = iVar6;
    piVar3 = piVar8 + 2;
    piVar1 = piVar5 + 4;
  } while (piVar9 != param_2 + 5);
  *piVar9 = piVar5[4];
  iVar11 = piVar5[5];
  piVar2[3] = piVar5[6];
  iVar4 = piVar5[7];
  piVar8[2] = iVar6 + iVar11;
  piVar8[3] = iVar11 + iVar4;
  piVar2[4] = piVar5[8];
  piVar8[4] = piVar5[9] + iVar4;
  idct_8(param_2);
  idct_8(param_1);
  iVar11 = param_2[7];
  piVar3 = param_1 + 7;
  piVar9 = param_1 + 8;
  piVar1 = param_2 + 4;
  piVar8 = (int *)(CosTable_8i + 0x1c);
  do {
    piVar10 = piVar8;
    piVar7 = piVar1;
    piVar5 = piVar9;
    piVar2 = piVar3;
    iVar6 = piVar7[2];
    piVar3 = piVar2 + -2;
    iVar4 = ((uint)(*piVar2 * *piVar10) >> 0x1c) +
            (int)((ulonglong)((longlong)*piVar2 * (longlong)*piVar10) >> 0x20) * 0x10;
    *piVar5 = iVar11 - iVar4;
    *piVar2 = iVar4 + iVar11;
    iVar11 = piVar7[1];
    iVar4 = ((uint)(piVar10[-1] * piVar2[-1]) >> 0x1c) +
            (int)((ulonglong)((longlong)piVar10[-1] * (longlong)piVar2[-1]) >> 0x20) * 0x10;
    piVar5[1] = iVar6 - iVar4;
    piVar2[-1] = iVar6 + iVar4;
    piVar9 = piVar5 + 2;
    piVar1 = piVar7 + -2;
    piVar8 = piVar10 + -2;
  } while (param_2 != piVar7 + -2);
  iVar4 = *piVar7;
  iVar6 = (int)((ulonglong)((longlong)*piVar3 * (longlong)piVar10[-2]) >> 0x20);
  piVar5[2] = iVar11 + iVar6 * -2;
  *piVar3 = iVar6 * 2 + iVar11;
  iVar11 = piVar7[-1];
  iVar6 = (int)((ulonglong)((longlong)piVar2[-3] * (longlong)piVar10[-3]) >> 0x20);
  piVar5[3] = iVar4 + iVar6 * -2;
  piVar2[-3] = iVar4 + iVar6 * 2;
  iVar4 = piVar7[-2];
  iVar6 = (int)((ulonglong)((longlong)piVar2[-4] * (longlong)piVar10[-4]) >> 0x20);
  piVar5[4] = iVar11 + iVar6 * -2;
  piVar2[-4] = iVar11 + iVar6 * 2;
  iVar11 = (int)((ulonglong)((longlong)piVar2[-5] * (longlong)piVar10[-5]) >> 0x20);
  piVar5[5] = iVar4 + iVar11 * -2;
  piVar2[-5] = iVar4 + iVar11 * 2;
  return;
}
