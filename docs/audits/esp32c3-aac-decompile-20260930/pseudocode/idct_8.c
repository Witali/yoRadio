/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: idct_8 @ ram:4205cbcc
 * Types and parameter counts are inferred; verify against disassembly. */

void idct_8(int *param_1)

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

  gp = &__global_pointer_;
  iVar6 = (int)((ulonglong)((longlong)(param_1[3] << 1) * 0x4cf90000) >> 0x20);
  iVar8 = (int)((ulonglong)((longlong)(param_1[1] << 1) * 0x41410000) >> 0x20);
  iVar1 = ((uint)(param_1[7] * 0x52036780) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[7] * 0x52036780) >> 0x20) * 8;
  iVar3 = (int)((ulonglong)((longlong)(param_1[5] << 1) * 0x73320000) >> 0x20);
  iVar2 = iVar1 + iVar8;
  iVar4 = iVar6 - iVar3;
  iVar3 = iVar3 + iVar6;
  iVar4 = ((uint)(iVar4 * 0x29cf5d40) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar4 * 0x29cf5d40) >> 0x20) * 8;
  iVar8 = (int)((ulonglong)((longlong)((iVar8 - iVar1) * 2) * 0x45460000) >> 0x20);
  iVar5 = ((uint)(param_1[6] * 0x29cf5d40) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[6] * 0x29cf5d40) >> 0x20) * 8;
  iVar10 = (int)((ulonglong)((longlong)(param_1[2] << 1) * 0x45460000) >> 0x20);
  iVar6 = (int)((ulonglong)((longlong)((iVar8 - iVar4) * 2) * 0x5a820000) >> 0x20);
  iVar1 = (int)((ulonglong)((longlong)((iVar10 - iVar5) * 2) * 0x5a820000) >> 0x20);
  iVar7 = iVar4 + iVar8 + iVar6;
  iVar4 = iVar2 + iVar3 + iVar7;
  iVar8 = (int)((ulonglong)((longlong)(param_1[4] << 1) * 0x5a820000) >> 0x20);
  iVar5 = iVar5 + iVar10 + iVar1;
  iVar2 = (int)((ulonglong)((longlong)((iVar2 - iVar3) * 2) * 0x5a820000) >> 0x20);
  iVar3 = *param_1 + iVar8;
  iVar8 = *param_1 - iVar8;
  iVar9 = iVar3 + iVar5;
  iVar10 = iVar8 + iVar1;
  iVar3 = iVar3 - iVar5;
  iVar8 = iVar8 - iVar1;
  iVar7 = iVar7 + iVar2;
  iVar2 = iVar2 + iVar6;
  param_1[7] = iVar9 - iVar4;
  *param_1 = iVar9 + iVar4;
  param_1[6] = iVar10 - iVar7;
  param_1[1] = iVar10 + iVar7;
  param_1[5] = iVar8 - iVar2;
  param_1[2] = iVar8 + iVar2;
  param_1[4] = iVar3 - iVar6;
  param_1[3] = iVar3 + iVar6;
  return;
}
