/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: synthesis_sub_band_LC_core1 @ ram:4204e754
 * Types and parameter counts are inferred; verify against disassembly. */

void synthesis_sub_band_LC_core1(int param_1,int *param_2,short *param_3)

{
  int iVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  short sVar10;
  int *piVar11;
  short *psVar12;
  short *psVar13;
  short sVar14;
  int *piVar15;
  short sVar16;
  short sVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  int iVar26;

  gp = &__global_pointer_;
  iVar9 = *(int *)(param_1 + 0x7c);
  iVar19 = param_2[0x2f];
  iVar5 = *(int *)(param_1 + 0x78);
  piVar11 = (int *)(param_1 + 0x74);
  piVar15 = param_2 + 0xf;
  param_3[0x5f] = (short)((ulonglong)((longlong)iVar9 * 0x4ccccd0) >> 0x20);
  param_3[0x5e] = (short)((ulonglong)((longlong)iVar19 * 0x4ccccd0) >> 0x20);
  psVar12 = param_3 + 0x5d;
  do {
    iVar25 = piVar15[0x1f];
    iVar18 = piVar15[0x1e];
    iVar20 = *piVar15;
    iVar4 = *piVar11;
    iVar26 = piVar11[-1];
    iVar1 = piVar15[-1];
    iVar24 = piVar11[-2];
    iVar3 = piVar11[-3];
    iVar22 = iVar9 + iVar5;
    iVar9 = piVar11[-4];
    iVar23 = piVar15[-2];
    iVar21 = iVar25 + iVar19;
    iVar19 = piVar15[0x1d];
    iVar7 = iVar4 + iVar5;
    iVar5 = piVar11[-5];
    piVar11 = piVar11 + -6;
    piVar15 = piVar15 + -3;
    *psVar12 = (short)((ulonglong)((longlong)iVar22 * 0x4ccccd0) >> 0x20);
    psVar12[-3] = (short)((ulonglong)((longlong)iVar21 * 0x4ccccd0) >> 0x20);
    psVar12[-1] = (short)((ulonglong)((longlong)iVar20 * 0x4ccccd0) >> 0x20);
    psVar12[-2] = (short)((ulonglong)((longlong)iVar7 * 0x4ccccd0) >> 0x20);
    psVar12[-4] = (short)((ulonglong)((longlong)(iVar4 + iVar26) * 0x4ccccd0) >> 0x20);
    psVar12[-5] = (short)((ulonglong)((longlong)iVar1 * 0x4ccccd0) >> 0x20);
    psVar12[-6] = (short)((ulonglong)((longlong)(iVar26 + iVar24) * 0x4ccccd0) >> 0x20);
    psVar12[-7] = (short)((ulonglong)((longlong)(iVar25 + iVar18) * 0x4ccccd0) >> 0x20);
    psVar12[-8] = (short)((ulonglong)((longlong)(iVar24 + iVar3) * 0x4ccccd0) >> 0x20);
    psVar12[-9] = (short)((ulonglong)((longlong)iVar23 * 0x4ccccd0) >> 0x20);
    psVar12[-10] = (short)((ulonglong)((longlong)(iVar3 + iVar9) * 0x4ccccd0) >> 0x20);
    psVar12[-0xb] = (short)((ulonglong)((longlong)(iVar18 + iVar19) * 0x4ccccd0) >> 0x20);
    psVar12 = psVar12 + -0xc;
  } while (piVar11 != (int *)(param_1 + -4));
  iVar19 = *param_2;
  sVar14 = param_3[0x5f];
  sVar6 = param_3[0x5e];
  sVar8 = param_3[0x5d];
  sVar16 = param_3[0x5c];
  param_3[0x60] = 0;
  psVar13 = param_3 + 0x61;
  param_3[0x21] = (short)((ulonglong)((longlong)(iVar9 + iVar5) * 0x4ccccd0) >> 0x20);
  param_3[0x20] = (short)((ulonglong)((longlong)iVar19 * 0x4ccccd0) >> 0x20);
  psVar12 = param_3 + 0x5b;
  do {
    *psVar13 = -sVar14;
    psVar13[1] = -sVar6;
    psVar13[2] = -sVar8;
    psVar13[3] = -sVar16;
    sVar14 = *psVar12;
    sVar6 = psVar12[-1];
    sVar8 = psVar12[-2];
    psVar13 = psVar13 + 4;
    sVar16 = psVar12[-3];
    psVar12 = psVar12 + -4;
  } while (psVar13 != param_3 + 0x7d);
  *param_3 = sVar16;
  sVar16 = param_3[0x3f];
  sVar2 = param_3[0x3e];
  sVar17 = param_3[0x3d];
  sVar10 = param_3[0x3c];
  param_3[0x7f] = -sVar8;
  param_3[0x7d] = -sVar14;
  param_3[0x7e] = -sVar6;
  psVar13 = param_3 + 1;
  psVar12 = param_3 + 0x3b;
  do {
    *psVar13 = sVar16;
    psVar13[1] = sVar2;
    psVar13[2] = sVar17;
    psVar13[3] = sVar10;
    sVar16 = *psVar12;
    sVar2 = psVar12[-1];
    sVar17 = psVar12[-2];
    psVar13 = psVar13 + 4;
    sVar10 = psVar12[-3];
    psVar12 = psVar12 + -4;
  } while (psVar13 != param_3 + 0x1d);
  param_3[0x1d] = sVar16;
  param_3[0x1e] = sVar2;
  param_3[0x1f] = sVar17;
  param_3[0x20] = sVar10;
  return;
}
