/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: inv_long_complex_rot @ ram:42045944
 * Types and parameter counts are inferred; verify against disassembly. */

int inv_long_complex_rot(short *param_1,undefined4 param_2)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int *piVar9;
  short *psVar10;
  int iVar11;
  uint *puVar12;
  uint uVar13;
  int iVar14;
  int iVar15;
  short *psVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
  int *piVar20;
  int iVar21;
  int iVar22;
  uint uVar23;
  int iVar24;
  uint uVar25;
  uint uVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  uint *puVar30;

  gp = &__global_pointer_;
  iVar11 = pv_normalize(param_2);
  piVar20 = (int *)(param_1 + 0x600);
  uVar7 = 0xf - iVar11;
  puVar12 = (uint *)&DAT_ram_3c129bec;
  puVar30 = (uint *)&DAT_ram_3c129be8;
  piVar9 = piVar20;
  piVar17 = (int *)(param_1 + 0x5fc);
  do {
    iVar18 = piVar9[-0x200];
    iVar21 = piVar17[1];
    iVar19 = *piVar17;
    iVar22 = piVar9[-0x1ff];
    iVar24 = *puVar12 << 0x10;
    uVar13 = *puVar30 & 0xffff0000;
    uVar5 = *puVar12 & 0xffff0000;
    iVar29 = *puVar30 << 0x10;
    iVar14 = *piVar9;
    iVar8 = piVar9[1];
    uVar26 = puVar30[-1];
    uVar25 = puVar12[1] & 0xffff0000;
    iVar28 = puVar12[1] << 0x10;
    iVar15 = piVar17[-0x200];
    puVar30 = puVar30 + -2;
    puVar12 = puVar12 + 2;
    *(short *)((int)piVar17 + 6) =
         (short)((int)((ulonglong)((longlong)iVar22 * (longlong)(int)uVar5) >> 0x20) +
                 (int)((ulonglong)((longlong)-iVar18 * (longlong)iVar24) >> 0x20) >> (uVar7 & 0x1f))
    ;
    iVar6 = piVar17[-0x1ff];
    uVar23 = uVar26 & 0xffff0000;
    iVar27 = uVar26 << 0x10;
    *(short *)(piVar17 + 1) =
         (short)((int)((ulonglong)((longlong)iVar19 * (longlong)(int)uVar13) >> 0x20) +
                 (int)((ulonglong)((longlong)iVar21 * (longlong)iVar29) >> 0x20) >> (uVar7 & 0x1f));
    *(short *)piVar9 =
         (short)((int)((ulonglong)((longlong)iVar18 * (longlong)(int)uVar5) >> 0x20) +
                 (int)((ulonglong)((longlong)iVar22 * (longlong)iVar24) >> 0x20) >> (uVar7 & 0x1f));
    *(short *)((int)piVar9 + 2) =
         (short)((int)((ulonglong)((longlong)iVar21 * (longlong)(int)uVar13) >> 0x20) +
                 (int)((ulonglong)((longlong)-iVar19 * (longlong)iVar29) >> 0x20) >> (uVar7 & 0x1f))
    ;
    *(short *)((int)piVar17 + 2) =
         (short)((int)((ulonglong)((longlong)iVar8 * (longlong)(int)uVar25) >> 0x20) +
                 (int)((ulonglong)((longlong)-iVar14 * (longlong)iVar28) >> 0x20) >> (uVar7 & 0x1f))
    ;
    *(short *)(piVar9 + 1) =
         (short)((int)((ulonglong)((longlong)iVar14 * (longlong)(int)uVar25) >> 0x20) +
                 (int)((ulonglong)((longlong)iVar8 * (longlong)iVar28) >> 0x20) >> (uVar7 & 0x1f));
    *(short *)((int)piVar9 + 6) =
         (short)((int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar23) >> 0x20) +
                 (int)((ulonglong)((longlong)-iVar15 * (longlong)iVar27) >> 0x20) >> (uVar7 & 0x1f))
    ;
    *(short *)piVar17 =
         (short)((int)((ulonglong)((longlong)iVar15 * (longlong)(int)uVar23) >> 0x20) +
                 (int)((ulonglong)((longlong)iVar6 * (longlong)iVar27) >> 0x20) >> (uVar7 & 0x1f));
    piVar9 = piVar9 + 2;
    piVar17 = piVar17 + -2;
  } while (puVar30 != (uint *)(codebook + 0x1c));
  psVar16 = param_1 + 0x3ff;
  psVar10 = param_1;
  do {
    sVar1 = psVar16[0x1ff];
    sVar2 = psVar16[0x1fe];
    sVar3 = psVar16[0x1fd];
    *psVar16 = psVar16[0x200];
    psVar16[-1] = sVar1;
    psVar16[-2] = sVar2;
    psVar16[-3] = sVar3;
    *psVar10 = -psVar16[0x200];
    psVar10[1] = -sVar1;
    psVar10[2] = -sVar2;
    psVar16 = psVar16 + -4;
    psVar10[3] = -sVar3;
    psVar10 = psVar10 + 4;
  } while (psVar16 != param_1 + 0x1ff);
  piVar9 = (int *)(param_1 + 0x400);
  piVar17 = piVar20;
  do {
    iVar6 = *piVar17;
    iVar8 = piVar17[1];
    piVar9[2] = piVar17[2];
    *piVar9 = iVar6;
    piVar9[1] = iVar8;
    piVar4 = piVar17 + 3;
    piVar17 = piVar17 + 4;
    piVar9[3] = *piVar4;
    piVar9 = piVar9 + 4;
  } while (piVar17 != (int *)(param_1 + 0x800));
  piVar9 = (int *)(param_1 + 0x400);
  psVar10 = param_1 + 0x7ff;
  do {
    sVar1 = *(short *)((int)piVar9 + 2);
    iVar6 = piVar9[1];
    piVar17 = piVar9 + 2;
    sVar2 = *(short *)((int)piVar9 + 6);
    *psVar10 = (short)*piVar9;
    psVar10[-1] = sVar1;
    psVar10[-2] = (short)iVar6;
    psVar10[-3] = sVar2;
    piVar9 = piVar17;
    psVar10 = psVar10 + -4;
  } while (piVar20 != piVar17);
  return 0x10 - iVar11;
}
