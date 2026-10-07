/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: dct_16 @ ram:420567d0
 * Types and parameter counts are inferred; verify against disassembly. */

void dct_16(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;

  gp = &__global_pointer_;
  iVar5 = *param_1;
  iVar12 = param_1[3] + param_1[0xc];
  iVar4 = param_1[4] + param_1[0xb];
  iVar19 = param_1[2] + param_1[0xd];
  iVar8 = iVar5 + param_1[0xf];
  iVar22 = param_1[5] + param_1[10];
  iVar16 = param_1[7] + param_1[8];
  iVar6 = param_1[1] + param_1[0xe];
  iVar1 = param_1[6] + param_1[9];
  iVar9 = iVar8 + iVar16;
  iVar2 = iVar1 + iVar6;
  iVar20 = iVar19 + iVar22;
  iVar13 = iVar12 + iVar4;
  iVar10 = iVar9 + iVar13;
  iVar3 = iVar2 + iVar20;
  *param_1 = iVar10 + iVar3 >> 1;
  iVar14 = (int)((ulonglong)((longlong)((iVar2 - iVar20) * 2) * 0x539f0000) >> 0x20);
  iVar18 = (int)((ulonglong)((longlong)((param_1[7] - param_1[8]) * 8) * 0x519e4e00) >> 0x20);
  iVar15 = (int)((ulonglong)((longlong)((param_1[6] - param_1[9]) * 2) * 0x6e3d0000) >> 0x20);
  iVar7 = (int)((ulonglong)((longlong)((param_1[5] - param_1[10]) * 2) * 0x43e20000) >> 0x20);
  iVar5 = (int)((ulonglong)((longlong)(iVar5 - param_1[0xf]) * 0x404f0000) >> 0x20);
  iVar20 = (int)((ulonglong)((longlong)(param_1[1] - param_1[0xe]) * 0x42e10000) >> 0x20);
  iVar17 = (int)((ulonglong)((longlong)(param_1[2] - param_1[0xd]) * 0x48920000) >> 0x20);
  iVar21 = (int)((ulonglong)((longlong)(param_1[3] - param_1[0xc]) * 0x52cb0000) >> 0x20);
  iVar11 = (int)((ulonglong)((longlong)(param_1[4] - param_1[0xb]) * 0x64e20000) >> 0x20);
  iVar2 = (int)((ulonglong)((longlong)(iVar9 - iVar13) * 0x45460000) >> 0x20);
  param_1[8] = (int)((ulonglong)((longlong)(iVar10 - iVar3) * 0x5a820000) >> 0x20);
  iVar3 = (int)((ulonglong)((longlong)((iVar2 - iVar14) * 2) * 0x5a820000) >> 0x20);
  iVar8 = (int)((ulonglong)((longlong)(iVar8 - iVar16) * 0x41410000) >> 0x20);
  param_1[0xc] = iVar3;
  param_1[4] = iVar14 + iVar2 + iVar3;
  iVar2 = (int)((ulonglong)((longlong)((iVar12 - iVar4) * 4) * 0x52036780) >> 0x20);
  iVar13 = iVar2 + iVar8;
  iVar3 = (int)((ulonglong)((longlong)(iVar6 - iVar1) * 0x4cf90000) >> 0x20);
  iVar1 = (int)((ulonglong)((longlong)(iVar19 - iVar22) * 0x73320000) >> 0x20);
  iVar9 = (int)((ulonglong)((longlong)((iVar8 - iVar2) * 2) * 0x45460000) >> 0x20);
  iVar2 = iVar1 + iVar3;
  iVar6 = iVar11 + iVar21;
  iVar12 = iVar18 + iVar5;
  iVar8 = (int)((ulonglong)((longlong)((iVar3 - iVar1) * 4) * 0x539eba80) >> 0x20);
  iVar10 = iVar15 + iVar20;
  iVar4 = iVar7 + iVar17;
  iVar3 = (int)((ulonglong)((longlong)((iVar9 - iVar8) * 2) * 0x5a820000) >> 0x20);
  iVar1 = (int)((ulonglong)((longlong)((iVar13 - iVar2) * 2) * 0x5a820000) >> 0x20);
  iVar9 = iVar8 + iVar3 + iVar9;
  param_1[0xe] = iVar3;
  param_1[2] = iVar13 + iVar2 + iVar9;
  param_1[6] = iVar9 + iVar1;
  param_1[10] = iVar3 + iVar1;
  iVar1 = (int)((ulonglong)((longlong)((iVar21 - iVar11) * 8) * 0x52036780) >> 0x20);
  iVar3 = (int)((ulonglong)((longlong)((iVar5 - iVar18) * 2) * 0x41410000) >> 0x20);
  iVar2 = (int)((ulonglong)((longlong)((iVar20 - iVar15) * 2) * 0x4cf90000) >> 0x20);
  iVar5 = (int)((ulonglong)((longlong)((iVar17 - iVar7) * 2) * 0x73320000) >> 0x20);
  if (param_2 == 0) {
    iVar12 = -iVar12;
    iVar3 = -iVar3;
    iVar10 = -iVar10;
    iVar2 = -iVar2;
    iVar4 = -iVar4;
    iVar5 = -iVar5;
    iVar6 = -iVar6;
    iVar1 = -iVar1;
  }
  iVar8 = (int)((ulonglong)((longlong)((iVar2 - iVar5) * 4) * 0x539eba80) >> 0x20);
  iVar20 = (int)((ulonglong)((longlong)((iVar3 - iVar1) * 2) * 0x45460000) >> 0x20);
  iVar11 = (int)((ulonglong)((longlong)((iVar20 - iVar8) * 2) * 0x5a827980) >> 0x20);
  iVar7 = (int)((ulonglong)((longlong)((iVar10 - iVar4) * 4) * 0x539eba80) >> 0x20);
  iVar9 = iVar8 + iVar20 + iVar11;
  iVar8 = iVar1 + iVar3 + iVar2 + iVar5 + iVar9;
  param_1[0xf] = iVar11;
  iVar20 = (int)((ulonglong)((longlong)((iVar12 - iVar6) * 2) * 0x45460000) >> 0x20);
  iVar3 = (int)((ulonglong)((longlong)(((iVar1 + iVar3) - (iVar2 + iVar5)) * 2) * 0x5a827980) >>
               0x20);
  param_1[1] = iVar10 + iVar4 + iVar6 + iVar12 + iVar8;
  iVar1 = (int)((ulonglong)((longlong)((iVar20 - iVar7) * 2) * 0x5a827980) >> 0x20);
  iVar9 = iVar9 + iVar3;
  iVar3 = iVar3 + iVar11;
  iVar4 = (int)((ulonglong)((longlong)(((iVar6 + iVar12) - (iVar10 + iVar4)) * 2) * 0x5a827980) >>
               0x20);
  iVar2 = iVar20 + iVar7 + iVar1;
  param_1[0xd] = iVar11 + iVar1;
  param_1[3] = iVar8 + iVar2;
  param_1[5] = iVar2 + iVar9;
  param_1[0xb] = iVar1 + iVar3;
  param_1[7] = iVar9 + iVar4;
  param_1[9] = iVar3 + iVar4;
  return;
}
