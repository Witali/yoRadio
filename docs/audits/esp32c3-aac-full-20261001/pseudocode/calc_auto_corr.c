/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_auto_corr @ ram:43000fe0
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_auto_corr(uint *param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int *piVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  uint uVar25;
  uint uVar26;
  uint uVar27;
  int iVar28;
  uint uVar29;
  uint uStack_7c;
  int iStack_78;
  int iStack_74;
  int iStack_70;
  int iStack_6c;
  uint uStack_68;
  uint uStack_5c;
  int iStack_58;
  uint uStack_54;
  uint uStack_50;
  uint uStack_4c;

  gp = &__global_pointer_;
  iVar28 = param_4 * 4;
  piVar8 = (int *)(param_3 + iVar28);
  piVar12 = (int *)(param_2 + iVar28);
  uVar24 = piVar12[-0x20];
  uVar10 = piVar8[-0x20];
  uVar9 = piVar8[-0x40];
  uVar2 = piVar12[-0x40];
  uVar3 = (int)uVar9 >> 2;
  uVar16 = (int)uVar24 >> 2;
  uVar18 = (int)uVar10 >> 2;
  uVar5 = (int)uVar2 >> 2;
  uStack_54 = uVar18 * uVar3 + uVar16 * uVar5;
  uVar22 = *piVar8 >> 2;
  uVar20 = *piVar12 >> 2;
  uStack_68 = (uint)(uStack_54 < uVar18 * uVar3) +
              (int)((ulonglong)((longlong)(int)uVar18 * (longlong)(int)uVar3) >> 0x20) +
              (int)((ulonglong)((longlong)(int)uVar16 * (longlong)(int)uVar5) >> 0x20);
  uStack_4c = uVar5 * uVar5 + uVar3 * uVar3;
  iStack_58 = (uint)(uStack_4c < uVar5 * uVar5) +
              (int)((ulonglong)((longlong)(int)uVar5 * (longlong)(int)uVar5) >> 0x20) +
              (int)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar3) >> 0x20);
  uStack_50 = uVar18 * uVar5 - uVar16 * uVar3;
  uStack_5c = ((int)((ulonglong)((longlong)(int)uVar18 * (longlong)(int)uVar5) >> 0x20) -
              (int)((ulonglong)((longlong)(int)uVar16 * (longlong)(int)uVar3) >> 0x20)) -
              (uint)(uVar18 * uVar5 < uStack_50);
  if (param_5 < 2) {
    uVar25 = 0;
    iVar28 = 0;
    uVar27 = 0;
    iVar6 = 0;
    uVar23 = 0;
    iVar1 = 0;
    uStack_7c = 0;
    iVar14 = 0;
    uVar29 = 0;
    iVar7 = 0;
  }
  else {
    piVar8 = (int *)(param_3 + 0x80 + iVar28);
    piVar12 = piVar12 + 0x20;
    uVar25 = 0;
    iVar28 = 0;
    uVar27 = 0;
    iVar6 = 0;
    uVar23 = 0;
    iVar1 = 0;
    uStack_7c = 0;
    iVar14 = 0;
    uVar29 = 0;
    iVar7 = 0;
    uVar10 = uVar3;
    uVar24 = uVar5;
    uVar9 = uVar16;
    uVar2 = uVar18;
    do {
      uVar18 = uVar22;
      uVar16 = uVar20;
      uVar3 = uVar2;
      uVar5 = uVar9;
      iVar11 = -uVar16;
      iVar4 = *piVar12;
      piVar12 = piVar12 + 0x20;
      uVar20 = iVar4 >> 2;
      uVar22 = *piVar8 >> 2;
      piVar8 = piVar8 + 0x20;
      uVar9 = uVar5 * uVar5 + uVar29;
      uVar29 = uVar3 * uVar3 + uVar9;
      iVar7 = (int)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar3) >> 0x20) +
              (uint)(uVar9 < uVar5 * uVar5) +
              (int)((ulonglong)((longlong)(int)uVar5 * (longlong)(int)uVar5) >> 0x20) + iVar7 +
              (uint)(uVar29 < uVar9);
      uVar9 = uStack_7c + uVar16 * uVar5;
      uStack_7c = uVar18 * uVar3 + uVar9;
      iVar14 = (uint)(uVar9 < uVar16 * uVar5) +
               (int)((ulonglong)((longlong)(int)uVar16 * (longlong)(int)uVar5) >> 0x20) + iVar14 +
               (int)((ulonglong)((longlong)(int)uVar18 * (longlong)(int)uVar3) >> 0x20) +
               (uint)(uStack_7c < uVar9);
      uVar2 = uVar23 + uVar18 * uVar5;
      uVar9 = uVar24 * uVar16 + uVar27;
      uVar27 = uVar10 * uVar18 + uVar9;
      iVar6 = (uint)(uVar27 < uVar9) +
              (int)((ulonglong)((longlong)(int)uVar24 * (longlong)(int)uVar16) >> 0x20) + iVar6 +
              (uint)(uVar9 < uVar24 * uVar16) +
              (int)((ulonglong)((longlong)(int)uVar10 * (longlong)(int)uVar18) >> 0x20);
      uVar23 = iVar11 * uVar3 + uVar2;
      iVar1 = (int)((ulonglong)((longlong)iVar11 * (longlong)(int)uVar3) >> 0x20) +
              (int)((ulonglong)((longlong)(int)uVar18 * (longlong)(int)uVar5) >> 0x20) + iVar1 +
              (uint)(uVar2 < uVar18 * uVar5) + (uint)(uVar23 < uVar2);
      uVar9 = uVar24 * uVar18 + uVar25;
      uVar25 = uVar10 * iVar11 + uVar9;
      iVar28 = (uint)(uVar25 < uVar9) +
               (int)((ulonglong)((longlong)(int)uVar24 * (longlong)(int)uVar18) >> 0x20) + iVar28 +
               (uint)(uVar9 < uVar24 * uVar18) +
               (int)((ulonglong)((longlong)(int)uVar10 * (longlong)iVar11) >> 0x20);
      uVar10 = uVar3;
      uVar24 = uVar5;
      uVar9 = uVar16;
      uVar2 = uVar18;
    } while (piVar12 != (int *)((param_5 * 0x20 + param_4) * 4 + param_2));
    uStack_68 = uStack_68 + iVar14 + (uint)(uStack_54 + uStack_7c < uStack_54);
    uStack_5c = (uint)(uStack_50 + uVar23 < uStack_50) + uStack_5c + iVar1;
    iStack_58 = (uint)(uStack_4c + uVar29 < uStack_4c) + iStack_58 + iVar7;
    uStack_54 = uStack_54 + uStack_7c;
    uStack_50 = uStack_50 + uVar23;
    uStack_4c = uStack_4c + uVar29;
    uVar10 = uVar18;
    uVar24 = uVar16;
    uVar9 = uVar3;
    uVar2 = uVar5;
  }
  iStack_6c = (int)uVar2 >> 0x1f;
  iStack_70 = (int)uVar9 >> 0x1f;
  iStack_74 = (int)uVar24 >> 0x1f;
  iStack_78 = (int)uVar10 >> 0x1f;
  iVar4 = (int)uVar22 >> 0x1f;
  uVar24 = -uVar20;
  uVar25 = uVar25 + uVar22 * uVar5;
  uVar21 = (int)uStack_68 >> 0x1f ^ uStack_68;
  uVar15 = uVar25 + uVar24 * uVar3;
  uVar9 = ((int)uVar24 >> 0x1f) * uVar3 + iStack_70 * uVar24 +
          (int)((ulonglong)uVar24 * (ulonglong)uVar3 >> 0x20) +
          (uint)(uVar25 < uVar22 * uVar5) +
          iVar4 * uVar5 + iStack_6c * uVar22 + (int)((ulonglong)uVar22 * (ulonglong)uVar5 >> 0x20) +
          iVar28 + (uint)(uVar15 < uVar25);
  uVar27 = uVar27 + uVar20 * uVar5;
  uVar17 = (int)uStack_5c >> 0x1f ^ uStack_5c;
  uVar13 = uVar27 + uVar22 * uVar3;
  uVar10 = (uint)(uVar13 < uVar27) +
           (int)((ulonglong)uVar22 * (ulonglong)uVar3 >> 0x20) + iVar4 * uVar3 + iStack_70 * uVar22
           + (uint)(uVar27 < uVar20 * uVar5) +
             ((int)uVar20 >> 0x1f) * uVar5 + iStack_6c * uVar20 +
             (int)((ulonglong)uVar20 * (ulonglong)uVar5 >> 0x20) + iVar6;
  uVar25 = (int)uVar9 >> 0x1f ^ uVar9;
  uVar23 = uVar23 + uVar22 * uVar16;
  uVar26 = (int)uVar10 >> 0x1f ^ uVar10;
  uVar19 = uVar23 + uVar24 * uVar18;
  uVar2 = (uint)(uVar19 < uVar23) +
          (uint)(uVar23 < uVar22 * uVar16) +
          (int)((ulonglong)uVar22 * (ulonglong)uVar16 >> 0x20) + iStack_74 * uVar22 + iVar4 * uVar16
          + iVar1 + iStack_78 * uVar24 + ((int)uVar24 >> 0x1f) * uVar18 +
                    (int)((ulonglong)uVar24 * (ulonglong)uVar18 >> 0x20);
  uVar5 = (int)uVar2 >> 0x1f ^ uVar2;
  uVar29 = uVar29 + uVar16 * uVar16;
  uVar3 = uVar18 * uVar18 + uVar29;
  iVar28 = (uint)(uVar3 < uVar29) +
           iStack_78 * uVar18 * 2 + (int)((ulonglong)uVar18 * (ulonglong)uVar18 >> 0x20) +
           (uint)(uVar29 < uVar16 * uVar16) +
           iStack_74 * uVar16 * 2 + (int)((ulonglong)uVar16 * (ulonglong)uVar16 >> 0x20) + iVar7;
  uStack_7c = uStack_7c + uVar20 * uVar16;
  uVar27 = uVar22 * uVar18 + uStack_7c;
  uVar24 = (uint)(uVar27 < uStack_7c) +
           iVar4 * uVar18 + iStack_78 * uVar22 +
           (int)((ulonglong)uVar22 * (ulonglong)uVar18 >> 0x20) +
           (uint)(uStack_7c < uVar20 * uVar16) +
           iStack_74 * uVar20 + ((int)uVar20 >> 0x1f) * uVar16 +
           (int)((ulonglong)uVar20 * (ulonglong)uVar16 >> 0x20) + iVar14;
  uVar22 = (int)uVar24 >> 0x1f ^ uVar24;
  uVar20 = (int)uStack_68 >> 0x1f ^ uStack_54 | (int)uStack_5c >> 0x1f ^ uStack_50 | uStack_4c |
           uVar3 | (int)uVar9 >> 0x1f ^ uVar15 | (int)uVar10 >> 0x1f ^ uVar13 |
           (int)uVar2 >> 0x1f ^ uVar19 | (int)uVar24 >> 0x1f ^ uVar27;
  if (uVar20 == 0 &&
      (((((((uVar21 == 0 && uVar17 == 0) && iStack_58 == 0) && iVar28 == 0) && uVar25 == 0) &&
        uVar26 == 0) && uVar5 == 0) && uVar22 == 0)) {
    *param_1 = 0;
    param_1[1] = 0;
    param_1[2] = 0;
    param_1[3] = 0;
    param_1[4] = 0;
    param_1[5] = 0;
    param_1[6] = 0;
    param_1[7] = 0;
    param_1[8] = 0;
    gp = &__global_pointer_;
    return;
  }
  if (((((((uVar21 == 0 && uVar17 == 0) && iStack_58 == 0) && iVar28 == 0) && uVar25 == 0) &&
       uVar26 == 0) && uVar5 == 0) && uVar22 == 0) {
    iVar6 = pv_normalize(uVar20 >> 1);
    uVar20 = iVar6 - 3;
    if ((int)uVar20 < 1) {
      uVar22 = -iVar6 + 3;
      uVar20 = -iVar6 - 0x1d;
      if ((int)uVar20 < 0) {
        uVar16 = (uVar3 >> (uVar22 & 0x1f)) + (iVar28 * 2 << (0x1f - uVar22 & 0x1f));
        uVar24 = (uVar27 >> (uVar22 & 0x1f)) + (uVar24 * 2 << (0x1f - uVar22 & 0x1f));
        uVar2 = (uVar19 >> (uVar22 & 0x1f)) + (uVar2 * 2 << (0x1f - uVar22 & 0x1f));
        uVar10 = (uVar13 >> (uVar22 & 0x1f)) + (uVar10 * 2 << (0x1f - uVar22 & 0x1f));
        uVar9 = (uVar15 >> (uVar22 & 0x1f)) + (uVar9 * 2 << (0x1f - uVar22 & 0x1f));
        uStack_68 = (uStack_54 >> (uVar22 & 0x1f)) + ((uStack_68 << 1) << (0x1f - uVar22 & 0x1f));
        uStack_5c = (uStack_50 >> (uVar22 & 0x1f)) + ((uStack_5c << 1) << (0x1f - uVar22 & 0x1f));
        uVar22 = (uStack_4c >> (uVar22 & 0x1f)) + ((iStack_58 << 1) << (0x1f - uVar22 & 0x1f));
      }
      else {
        uVar16 = iVar28 >> (uVar20 & 0x1f);
        uVar24 = (int)uVar24 >> (uVar20 & 0x1f);
        uVar2 = (int)uVar2 >> (uVar20 & 0x1f);
        uVar10 = (int)uVar10 >> (uVar20 & 0x1f);
        uVar9 = (int)uVar9 >> (uVar20 & 0x1f);
        uStack_68 = (int)uStack_68 >> (uVar20 & 0x1f);
        uStack_5c = (int)uStack_5c >> (uVar20 & 0x1f);
        uVar22 = iStack_58 >> (uVar20 & 0x1f);
      }
    }
    else {
      uVar22 = iVar6 + -0x23 >> 0x1f;
      uVar16 = uVar3 << (uVar20 & 0x1f) & uVar22;
      uVar24 = uVar27 << (uVar20 & 0x1f) & uVar22;
      uVar2 = uVar19 << (uVar20 & 0x1f) & uVar22;
      uVar10 = uVar13 << (uVar20 & 0x1f) & uVar22;
      uVar9 = uVar15 << (uVar20 & 0x1f) & uVar22;
      uStack_68 = uStack_54 << (uVar20 & 0x1f) & uVar22;
      uStack_5c = uStack_50 << (uVar20 & 0x1f) & uVar22;
      uVar22 = uStack_4c << (uVar20 & 0x1f) & uVar22;
    }
    goto LAB_ram_4300149c;
  }
  iVar6 = pv_normalize();
  uVar20 = -iVar6 + 0x22;
  uVar22 = -iVar6 + 2;
  if ((int)uVar22 < 0) {
    uVar16 = (uVar3 >> (uVar20 & 0x1f)) + (iVar28 * 2 << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_43001462;
LAB_ram_430015a4:
    uVar24 = (uVar27 >> (uVar20 & 0x1f)) + (uVar24 * 2 << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_4300146a;
LAB_ram_430015ba:
    uVar2 = (uVar19 >> (uVar20 & 0x1f)) + (uVar2 * 2 << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_43001472;
LAB_ram_430015d0:
    uVar10 = (uVar13 >> (uVar20 & 0x1f)) + (uVar10 * 2 << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_4300147a;
LAB_ram_430015e6:
    uVar9 = (uVar15 >> (uVar20 & 0x1f)) + (uVar9 * 2 << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_43001482;
LAB_ram_430015fc:
    uStack_68 = (uStack_54 >> (uVar20 & 0x1f)) + ((uStack_68 << 1) << (0x1f - uVar20 & 0x1f));
    if (-1 < (int)uVar22) goto LAB_ram_4300148c;
LAB_ram_43001614:
    uStack_5c = (uStack_50 >> (uVar20 & 0x1f)) + ((uStack_5c << 1) << (0x1f - uVar20 & 0x1f));
  }
  else {
    uVar16 = iVar28 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_430015a4;
LAB_ram_43001462:
    uVar24 = (int)uVar24 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_430015ba;
LAB_ram_4300146a:
    uVar2 = (int)uVar2 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_430015d0;
LAB_ram_43001472:
    uVar10 = (int)uVar10 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_430015e6;
LAB_ram_4300147a:
    uVar9 = (int)uVar9 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_430015fc;
LAB_ram_43001482:
    uStack_68 = (int)uStack_68 >> (uVar22 & 0x1f);
    if ((int)uVar22 < 0) goto LAB_ram_43001614;
LAB_ram_4300148c:
    uStack_5c = (int)uStack_5c >> (uVar22 & 0x1f);
  }
  if ((int)uVar22 < 0) {
    uVar22 = (uStack_4c >> (uVar20 & 0x1f)) + ((iStack_58 << 1) << (0x1f - uVar20 & 0x1f));
  }
  else {
    uVar22 = iStack_58 >> (uVar22 & 0x1f);
  }
LAB_ram_4300149c:
  param_1[3] = uStack_68;
  param_1[7] = uStack_5c;
  *param_1 = uVar16;
  param_1[4] = uVar22;
  param_1[1] = uVar24;
  param_1[5] = uVar2;
  param_1[2] = uVar10;
  param_1[6] = uVar9;
  iVar28 = (uStack_68 * uStack_68 >> 0x1d) +
           (int)((ulonglong)((longlong)(int)uStack_68 * (longlong)(int)uStack_68) >> 0x20) * 8 +
           (uStack_5c * uStack_5c >> 0x1d) +
           (int)((ulonglong)((longlong)(int)uStack_5c * (longlong)(int)uStack_5c) >> 0x20) * 8;
  param_1[8] = ((uVar16 * uVar22 >> 0x1d) +
               (int)((ulonglong)((longlong)(int)uVar16 * (longlong)(int)uVar22) >> 0x20) * 8) -
               (iVar28 - (iVar28 >> 0x14));
  return;
}
