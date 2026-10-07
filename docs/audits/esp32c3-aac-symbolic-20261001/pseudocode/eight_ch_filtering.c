/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: eight_ch_filtering @ ram:4300c920
 * Types and parameter counts are inferred; verify against disassembly. */

void eight_ch_filtering(int *param_1,int *param_2,int *param_3,int *param_4,int *param_5)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
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
  iVar4 = ((uint)(param_1[4] * -0x23c9b4c) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[4] * -0x23c9b4c) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[0xc] * 0x159bdee) >> 0x20);
  iVar6 = ((uint)(param_2[4] * -0x23c9b4c) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[4] * -0x23c9b4c) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[0xc] * 0x159bdee) >> 0x20);
  param_3[2] = iVar6 - iVar4;
  param_4[2] = -(iVar6 + iVar4);
  iVar4 = ((uint)(param_1[3] * -0x2533d74) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[3] * -0x2533d74) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[0xb] * 0x5cff170) >> 0x20);
  iVar6 = ((uint)(param_2[3] * -0x2533d74) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[3] * -0x2533d74) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[0xb] * 0x5cff170) >> 0x20);
  param_3[3] = ((uint)(iVar6 * 0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar6 * 0x1d906bc0) >> 0x20) * 8 +
               ((uint)(iVar4 * -0xc3ef150) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar4 * -0xc3ef150) >> 0x20) * 8;
  param_4[3] = ((uint)(iVar6 * -0xc3ef150) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar6 * -0xc3ef150) >> 0x20) * 8 +
               ((uint)(iVar4 * -0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar4 * -0x1d906bc0) >> 0x20) * 8;
  param_4[4] = (int)((ulonglong)((longlong)(param_1[2] - param_1[10]) * 0xba3d580) >> 0x20);
  param_3[4] = (int)((ulonglong)((longlong)(param_2[10] - param_2[2]) * 0xba3d580) >> 0x20);
  iVar6 = ((uint)(param_1[1] * -0xb9fe2e) >> 0x1d) +
          (int)((ulonglong)((longlong)param_1[1] * -0xb9fe2e) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[9] * 0x1299eba0) >> 0x20);
  iVar4 = ((uint)(param_2[1] * -0xb9fe2e) >> 0x1d) +
          (int)((ulonglong)((longlong)param_2[1] * -0xb9fe2e) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[9] * 0x1299eba0) >> 0x20);
  param_3[5] = ((uint)(iVar4 * 0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar4 * 0x1d906bc0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)iVar6 * 0x61f78a80) >> 0x20);
  param_4[5] = ((uint)(iVar6 * -0x1d906bc0) >> 0x1d) +
               (int)((ulonglong)((longlong)iVar6 * -0x1d906bc0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)iVar4 * 0x61f78a80) >> 0x20);
  iVar6 = ((uint)(*param_1 * -0x2b37be) >> 0x1d) +
          (int)((ulonglong)((longlong)*param_1 * -0x2b37be) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_1[8] * 0x11e4da60) >> 0x20);
  iVar4 = ((uint)(*param_2 * -0x2b37be) >> 0x1d) +
          (int)((ulonglong)((longlong)*param_2 * -0x2b37be) >> 0x20) * 8 +
          (int)((ulonglong)((longlong)param_2[8] * 0x11e4da60) >> 0x20);
  param_3[6] = iVar4 + iVar6;
  param_4[6] = iVar4 - iVar6;
  param_3[7] = (int)((ulonglong)((longlong)param_2[7] * 0xb8dcf00) >> 0x20) +
               (int)((ulonglong)((longlong)param_1[7] * 0x1be4c800) >> 0x20);
  param_4[7] = ((uint)(param_1[7] * -0x171b9e0) >> 0x1d) +
               (int)((ulonglong)((longlong)param_1[7] * -0x171b9e0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)param_2[7] * 0x1be4c800) >> 0x20);
  *param_3 = param_1[6] >> 3;
  *param_4 = param_2[6] >> 3;
  param_3[1] = ((uint)(param_2[5] * -0x171b9e0) >> 0x1d) +
               (int)((ulonglong)((longlong)param_2[5] * -0x171b9e0) >> 0x20) * 8 +
               (int)((ulonglong)((longlong)param_1[5] * 0x1be4c800) >> 0x20);
  param_4[1] = (int)((ulonglong)((longlong)param_2[5] * 0x1be4c800) >> 0x20) +
               (int)((ulonglong)((longlong)param_1[5] * 0xb8dcf00) >> 0x20);
  iVar4 = *param_3 + param_3[4];
  iVar20 = *param_4 + param_4[4];
  iVar17 = *param_3 - param_3[4];
  iVar6 = *param_4 - param_4[4];
  *param_5 = iVar4;
  param_5[2] = iVar17;
  param_5[1] = iVar20;
  param_5[3] = iVar6;
  iVar11 = param_3[5];
  iVar8 = param_4[5];
  iVar7 = param_3[1];
  iVar5 = param_4[1];
  iVar18 = iVar7 + iVar11;
  iVar16 = iVar5 + iVar8;
  param_5[4] = iVar18;
  param_5[5] = iVar16;
  iVar5 = iVar5 - iVar8;
  iVar7 = iVar7 - iVar11;
  iVar12 = param_3[2] + param_3[6];
  iVar11 = param_4[2] + param_4[6];
  iVar19 = param_3[2] - param_3[6];
  iVar8 = param_4[6] - param_4[2];
  param_5[6] = iVar12;
  param_5[9] = iVar19;
  param_5[7] = iVar11;
  param_5[8] = iVar8;
  iVar14 = param_3[3] - param_3[7];
  iVar15 = iVar7 - iVar14;
  iVar9 = param_3[3] + param_3[7];
  iVar1 = param_4[3] - param_4[7];
  iVar13 = iVar5 - iVar1;
  iVar5 = iVar5 + iVar1;
  iVar7 = iVar7 + iVar14;
  iVar1 = param_4[3] + param_4[7];
  iVar14 = ((uint)(iVar15 * 0x16a09e60) >> 0x1d) +
           (int)((ulonglong)((longlong)iVar15 * 0x16a09e60) >> 0x20) * 8;
  param_5[0xb] = iVar1;
  param_5[10] = iVar9;
  piVar10 = param_5 + 0x18;
  param_5[0xc] = iVar14;
  param_5[0x10] = iVar4 + iVar12;
  param_5[0x14] = iVar4 - iVar12;
  param_5[0x11] = iVar20 + iVar11;
  param_5[0x15] = iVar20 - iVar11;
  param_5[0x12] = iVar17 + iVar8;
  param_5[0x16] = iVar17 - iVar8;
  param_5[0x13] = iVar6 + iVar19;
  param_5[0x17] = iVar6 - iVar19;
  iVar6 = ((uint)(iVar13 * 0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar13 * 0x16a09e60) >> 0x20) * 8;
  param_5[0xd] = iVar6;
  param_5[0x18] = iVar18 + iVar9;
  param_5[0x1d] = iVar18 - iVar9;
  param_5[0x19] = iVar16 + iVar1;
  param_5[0x1c] = iVar1 - iVar16;
  iVar4 = ((uint)(iVar5 * -0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar5 * -0x16a09e60) >> 0x20) * 8;
  param_5[0xe] = iVar4;
  param_5[0x1a] = iVar4 + iVar14;
  param_5[0x1e] = iVar4 - iVar14;
  iVar4 = ((uint)(iVar7 * 0x16a09e60) >> 0x1d) +
          (int)((ulonglong)((longlong)iVar7 * 0x16a09e60) >> 0x20) * 8;
  param_5[0xf] = iVar4;
  param_5[0x1b] = iVar4 + iVar6;
  param_5[0x1f] = iVar4 - iVar6;
  piVar2 = param_3;
  do {
    iVar6 = piVar10[-8];
    iVar11 = *piVar10;
    iVar8 = piVar10[-7];
    piVar3 = piVar2 + 1;
    iVar4 = piVar10[1];
    *piVar2 = iVar6 + iVar11;
    *param_4 = iVar8 + iVar4;
    piVar2[4] = iVar6 - iVar11;
    param_4[4] = iVar8 - iVar4;
    piVar10 = piVar10 + 2;
    piVar2 = piVar3;
    param_4 = param_4 + 1;
  } while (param_3 + 4 != piVar3);
  return;
}
