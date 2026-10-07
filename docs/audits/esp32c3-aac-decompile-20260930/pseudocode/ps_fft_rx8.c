/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: ps_fft_rx8 @ ram:4205a1d6
 * Types and parameter counts are inferred; verify against disassembly. */

void ps_fft_rx8(int *param_1,int *param_2,int *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int *piVar10;
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

  gp = &__global_pointer_;
  iVar1 = *param_1 + param_1[4];
  iVar20 = *param_2 + param_2[4];
  iVar17 = *param_1 - param_1[4];
  iVar2 = *param_2 - param_2[4];
  *param_3 = iVar1;
  param_3[2] = iVar17;
  param_3[1] = iVar20;
  param_3[3] = iVar2;
  iVar11 = param_1[5];
  iVar8 = param_2[5];
  iVar7 = param_1[1];
  iVar6 = param_2[1];
  iVar18 = iVar7 + iVar11;
  iVar16 = iVar6 + iVar8;
  param_3[4] = iVar18;
  param_3[5] = iVar16;
  iVar6 = iVar6 - iVar8;
  iVar7 = iVar7 - iVar11;
  iVar12 = param_1[2] + param_1[6];
  iVar11 = param_2[2] + param_2[6];
  iVar19 = param_1[2] - param_1[6];
  iVar8 = param_2[6] - param_2[2];
  param_3[6] = iVar12;
  param_3[9] = iVar19;
  param_3[7] = iVar11;
  param_3[8] = iVar8;
  iVar14 = param_1[3] - param_1[7];
  iVar15 = iVar7 - iVar14;
  iVar9 = param_1[3] + param_1[7];
  iVar3 = param_2[3] - param_2[7];
  iVar13 = iVar6 - iVar3;
  iVar6 = iVar6 + iVar3;
  iVar7 = iVar7 + iVar14;
  iVar3 = param_2[3] + param_2[7];
  iVar14 = ((uint)(iVar15 * 0x16a09e60) >> 0x1d) +
           (int)((ulonglong)((longlong)iVar15 * 0x16a09e60) >> 0x20) * 8;
  param_3[0xb] = iVar3;
  param_3[10] = iVar9;
  piVar10 = param_3 + 0x18;
  param_3[0xc] = iVar14;
  param_3[0x10] = iVar1 + iVar12;
  param_3[0x14] = iVar1 - iVar12;
  param_3[0x11] = iVar20 + iVar11;
  param_3[0x15] = iVar20 - iVar11;
  param_3[0x12] = iVar17 + iVar8;
  param_3[0x16] = iVar17 - iVar8;
  param_3[0x13] = iVar2 + iVar19;
  param_3[0x17] = iVar2 - iVar19;
  iVar2 = ((uint)(iVar13 * 0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar13 * 0x16a09e60) >> 0x20) * 8;
  param_3[0xd] = iVar2;
  param_3[0x18] = iVar18 + iVar9;
  param_3[0x1d] = iVar18 - iVar9;
  param_3[0x19] = iVar16 + iVar3;
  param_3[0x1c] = iVar3 - iVar16;
  iVar1 = ((uint)(iVar6 * -0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar6 * -0x16a09e60) >> 0x20) * 8;
  param_3[0xe] = iVar1;
  param_3[0x1a] = iVar1 + iVar14;
  param_3[0x1e] = iVar1 - iVar14;
  iVar1 = ((uint)(iVar7 * 0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar7 * 0x16a09e60) >> 0x20) * 8;
  param_3[0xf] = iVar1;
  param_3[0x1b] = iVar1 + iVar2;
  param_3[0x1f] = iVar1 - iVar2;
  piVar4 = param_1;
  do {
    iVar2 = piVar10[-8];
    iVar11 = *piVar10;
    iVar8 = piVar10[-7];
    piVar5 = piVar4 + 1;
    iVar1 = piVar10[1];
    *piVar4 = iVar2 + iVar11;
    *param_2 = iVar8 + iVar1;
    piVar4[4] = iVar2 - iVar11;
    param_2[4] = iVar8 - iVar1;
    piVar10 = piVar10 + 2;
    piVar4 = piVar5;
    param_2 = param_2 + 1;
  } while (param_1 + 4 != piVar5);
  return;
}
