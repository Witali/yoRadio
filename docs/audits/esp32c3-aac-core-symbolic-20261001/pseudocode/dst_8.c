/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: dst_8 @ ram:430059a2
 * Types and parameter counts are inferred; verify against disassembly. */

void dst_8(int *param_1)

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

  gp = &__global_pointer_;
  iVar7 = (int)((ulonglong)((longlong)param_1[3] * 0x4cf90000) >> 0x20);
  iVar1 = (int)((ulonglong)((longlong)param_1[5] * 0x73320000) >> 0x20);
  iVar9 = iVar1 + iVar7;
  iVar1 = iVar1 - iVar7;
  iVar3 = (int)((ulonglong)((longlong)param_1[1] * 0x41410000) >> 0x20);
  iVar2 = (int)((ulonglong)((longlong)param_1[7] * 0x1480d9d00) >> 0x20);
  iVar4 = iVar3 - iVar2;
  iVar7 = (int)((ulonglong)((longlong)(param_1[6] << 1) * 0x539f0000) >> 0x20);
  iVar5 = ((uint)(iVar9 * 0x29cf5d40) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar9 * 0x29cf5d40) >> 0x20) * 8;
  iVar2 = (int)((ulonglong)((longlong)((iVar2 + iVar3) * 2) * 0x45460000) >> 0x20);
  iVar3 = (int)((ulonglong)((longlong)param_1[2] * 0x45460000) >> 0x20);
  iVar9 = iVar2 - iVar5;
  iVar2 = (int)((ulonglong)((longlong)((iVar5 + iVar2) * 2) * 0x5a820000) >> 0x20);
  iVar6 = (int)((ulonglong)((longlong)((iVar7 + iVar3) * 2) * 0x5a827980) >> 0x20);
  iVar8 = iVar4 + iVar1 + iVar2 + iVar9;
  iVar5 = (iVar3 - iVar7) + iVar6;
  iVar3 = (int)((ulonglong)((longlong)param_1[4] * 0x5a820000) >> 0x20);
  iVar7 = (int)((ulonglong)((longlong)((iVar4 - iVar1) * 2) * 0x5a820000) >> 0x20) + iVar2;
  iVar9 = iVar9 + iVar7;
  iVar1 = iVar5 - iVar3;
  iVar5 = iVar5 + iVar3;
  param_1[5] = iVar9 - iVar1;
  param_1[2] = iVar1 + iVar9;
  param_1[4] = iVar8 - (iVar6 - iVar3);
  param_1[3] = (iVar6 - iVar3) + iVar8;
  param_1[7] = iVar2 - (iVar3 + iVar6);
  *param_1 = iVar3 + iVar6 + iVar2;
  param_1[6] = iVar7 - iVar5;
  param_1[1] = iVar5 + iVar7;
  return;
}
