/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: mdst_32 @ ram:420597aa
 * Types and parameter counts are inferred; verify against disassembly. */

void mdst_32(int *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *piVar9;
  int iVar10;

  gp = &__global_pointer_;
  iVar10 = *param_1;
  iVar2 = param_1[1];
  piVar3 = param_1 + 1;
  do {
    iVar8 = piVar3[1];
    iVar4 = piVar3[2];
    iVar5 = piVar3[3];
    iVar6 = piVar3[4];
    iVar1 = iVar2 + iVar10;
    iVar10 = piVar3[5];
    *piVar3 = iVar1;
    piVar3[1] = iVar2 + iVar8;
    piVar3[2] = iVar8 + iVar4;
    piVar3[3] = iVar4 + iVar5;
    piVar3[4] = iVar5 + iVar6;
    piVar9 = piVar3 + 6;
    piVar3[5] = iVar6 + iVar10;
    iVar2 = *piVar9;
    piVar3 = piVar9;
  } while (piVar9 != param_1 + 0x1f);
  param_1[0x1f] = iVar10 + iVar2;
  dst_32();
  piVar3 = param_1;
  piVar9 = &CosTable_32;
  do {
    *piVar3 = (int)((ulonglong)((longlong)(*piVar3 * 2 + iVar2) * (longlong)*piVar9) >> 0x20);
    piVar7 = piVar3 + 4;
    piVar3[1] = (int)((ulonglong)((longlong)(piVar3[1] * 2 - iVar2) * (longlong)piVar9[1]) >> 0x20);
    piVar3[2] = (int)((ulonglong)((longlong)(piVar3[2] * 2 + iVar2) * (longlong)piVar9[2]) >> 0x20);
    piVar3[3] = (int)((ulonglong)((longlong)(piVar3[3] * 2 - iVar2) * (longlong)piVar9[3]) >> 0x20);
    piVar3 = piVar7;
    piVar9 = piVar9 + 4;
  } while (param_1 + 0x14 != piVar7);
  iVar2 = iVar2 >> 1;
  piVar3 = &DAT_ram_3c1300f4;
  piVar9 = param_1 + 0x14;
  do {
    piVar7 = piVar9 + 4;
    *piVar9 = ((uint)((*piVar9 + iVar2) * *piVar3) >> 0x1b) +
              (int)((ulonglong)((longlong)(*piVar9 + iVar2) * (longlong)*piVar3) >> 0x20) * 0x20;
    piVar9[1] = ((uint)((piVar9[1] - iVar2) * piVar3[1]) >> 0x1b) +
                (int)((ulonglong)((longlong)(piVar9[1] - iVar2) * (longlong)piVar3[1]) >> 0x20) *
                0x20;
    piVar9[2] = ((uint)((piVar9[2] + iVar2) * piVar3[2]) >> 0x1b) +
                (int)((ulonglong)((longlong)(piVar9[2] + iVar2) * (longlong)piVar3[2]) >> 0x20) *
                0x20;
    iVar10 = ((uint)((piVar9[3] - iVar2) * piVar3[3]) >> 0x1b) +
             (int)((ulonglong)((longlong)(piVar9[3] - iVar2) * (longlong)piVar3[3]) >> 0x20) * 0x20;
    piVar9[3] = iVar10;
    piVar3 = piVar3 + 4;
    piVar9 = piVar7;
  } while (piVar7 != param_1 + 0x20);
  param_1[0x1f] = iVar10 * 2;
  return;
}
