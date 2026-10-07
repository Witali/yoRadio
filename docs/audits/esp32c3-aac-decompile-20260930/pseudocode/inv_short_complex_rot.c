/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: inv_short_complex_rot @ ram:42045b62
 * Types and parameter counts are inferred; verify against disassembly. */

int inv_short_complex_rot(int param_1,short *param_2,undefined4 param_3)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  uint *puVar5;
  short *psVar6;
  int iVar7;
  int iVar8;
  short *psVar9;
  int *piVar10;
  short *psVar11;
  int iVar12;
  short *psVar13;
  uint uVar14;
  short *psVar15;
  short *psVar16;
  uint uVar17;
  int iVar18;

  gp = &__global_pointer_;
  psVar6 = param_2 + 0x100;
  psVar16 = param_2 + 0x140;
  iVar7 = pv_normalize(param_3);
  if (iVar7 < 0x11) {
    iVar8 = 0x10 - iVar7;
    uVar17 = 0xf - iVar7;
  }
  else {
    uVar17 = 0xffffffff;
    iVar8 = 0;
  }
  puVar5 = &exp_rotation_N_256;
  psVar9 = &digit_reverse_64;
  psVar11 = psVar6;
  do {
    piVar10 = (int *)(*psVar9 * 4 + param_1);
    iVar12 = *piVar10;
    iVar7 = piVar10[1];
    iVar18 = *puVar5 << 0x10;
    uVar14 = *puVar5 & 0xffff0000;
    psVar9 = psVar9 + 1;
    puVar5 = puVar5 + 1;
    *psVar11 = (short)((int)((ulonglong)((longlong)iVar7 * (longlong)(int)uVar14) >> 0x20) +
                       (int)((ulonglong)((longlong)-iVar12 * (longlong)iVar18) >> 0x20) >>
                      (uVar17 & 0x1f));
    psVar11[0x40] =
         (short)((int)((ulonglong)((longlong)iVar12 * (longlong)(int)uVar14) >> 0x20) +
                 (int)((ulonglong)((longlong)iVar7 * (longlong)iVar18) >> 0x20) >> (uVar17 & 0x1f));
    psVar11 = psVar11 + 1;
  } while (psVar9 != (short *)CosTable_16);
  psVar9 = param_2 + 0x17f;
  psVar15 = param_2 + 0xc0;
  psVar13 = param_2 + 0x120;
  psVar11 = param_2 + 0xbf;
  do {
    sVar1 = *psVar6;
    sVar2 = *psVar9;
    sVar3 = psVar6[1];
    sVar4 = psVar9[-1];
    *psVar11 = sVar1;
    psVar11[-2] = sVar3;
    psVar11[-1] = sVar2;
    psVar11[-3] = sVar4;
    psVar15[2] = sVar3;
    *psVar15 = sVar1;
    psVar15[1] = sVar2;
    psVar6 = psVar6 + 2;
    psVar15[3] = sVar4;
    psVar9 = psVar9 + -2;
    psVar15 = psVar15 + 4;
    psVar11 = psVar11 + -4;
  } while (psVar6 != psVar13);
  psVar11 = param_2 + 0x15f;
  psVar6 = param_2 + 0x7f;
  do {
    sVar1 = *psVar13;
    sVar2 = *psVar11;
    sVar3 = psVar13[1];
    sVar4 = psVar11[-1];
    *psVar6 = sVar1;
    psVar6[-2] = sVar3;
    psVar6[-1] = sVar2;
    psVar6[-3] = sVar4;
    param_2[2] = -sVar3;
    *param_2 = -sVar1;
    param_2[1] = -sVar2;
    psVar13 = psVar13 + 2;
    param_2[3] = -sVar4;
    psVar11 = psVar11 + -2;
    param_2 = param_2 + 4;
    psVar6 = psVar6 + -4;
  } while (psVar16 != psVar13);
  return iVar8;
}
