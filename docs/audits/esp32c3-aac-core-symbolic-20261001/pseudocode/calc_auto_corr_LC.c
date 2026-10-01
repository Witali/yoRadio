/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_auto_corr_LC @ ram:43000c16
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_auto_corr_LC(aac_analysis_autocorrelation_t *correlation,int param_2,int param_3,
                      int param_4)

{
  longlong lVar1;
  longlong lVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int *piVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;

  gp = &__global_pointer_;
  piVar12 = (int *)(param_3 * 4 + param_2);
  uVar6 = piVar12[-0x20];
  uVar17 = piVar12[-0x40];
  uVar3 = (int)uVar6 >> 2;
  uVar23 = (int)uVar17 >> 2;
  uVar20 = uVar3 * uVar23;
  uVar14 = *piVar12 >> 2;
  iVar5 = (int)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar3) >> 0x20);
  uVar16 = uVar3 * uVar3;
  uVar19 = (uint)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar23) >> 0x20);
  uVar21 = uVar23 * uVar23;
  lVar1 = (longlong)(int)uVar23;
  lVar2 = (longlong)(int)uVar23;
  if (param_4 < 2) {
    uVar22 = 0;
    iVar8 = 0;
    uVar13 = 0;
    iVar9 = 0;
  }
  else {
    piVar12 = piVar12 + 0x20;
    iVar8 = 0;
    iVar9 = 0;
    uVar6 = uVar3;
    uVar17 = 0;
    uVar4 = uVar16;
    uVar7 = 0;
    uVar10 = uVar23;
    do {
      uVar3 = uVar14;
      uVar23 = uVar6;
      iVar11 = *piVar12;
      piVar12 = piVar12 + 0x20;
      uVar14 = iVar11 >> 2;
      uVar13 = uVar3 * uVar23 + uVar17;
      uVar22 = uVar10 * uVar3 + uVar7;
      uVar16 = uVar3 * uVar3 + uVar4;
      iVar8 = iVar8 + (int)((ulonglong)((longlong)(int)uVar10 * (longlong)(int)uVar3) >> 0x20) +
              (uint)(uVar22 < uVar7);
      iVar9 = (uint)(uVar13 < uVar17) +
              (int)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar23) >> 0x20) + iVar9;
      iVar5 = (uint)(uVar16 < uVar4) +
              (int)((ulonglong)((longlong)(int)uVar3 * (longlong)(int)uVar3) >> 0x20) + iVar5;
      uVar6 = uVar3;
      uVar17 = uVar13;
      uVar4 = uVar16;
      uVar7 = uVar22;
      uVar10 = uVar23;
    } while (piVar12 != (int *)(param_2 + (param_4 * 0x20 + param_3) * 4));
    uVar19 = uVar19 + iVar9 + (uint)(uVar20 + uVar13 < uVar20);
    uVar20 = uVar20 + uVar13;
    uVar17 = uVar23;
  }
  uVar15 = -uVar3;
  uVar18 = uVar21 + uVar16;
  uVar13 = uVar14 * uVar3 + uVar13;
  uVar10 = (int)uVar19 >> 0x1f ^ uVar19;
  uVar7 = (uint)(uVar13 < uVar14 * uVar3) +
          ((int)uVar14 >> 0x1f) * uVar3 + ((int)uVar6 >> 0x1f) * uVar14 +
          (int)((ulonglong)uVar14 * (ulonglong)uVar3 >> 0x20) + iVar9;
  uVar4 = (int)uVar7 >> 0x1f ^ uVar7;
  uVar22 = uVar14 * uVar23 + uVar22;
  uVar17 = (uint)(uVar22 < uVar14 * uVar23) +
           ((int)uVar14 >> 0x1f) * uVar23 + ((int)uVar17 >> 0x1f) * uVar14 +
           (int)((ulonglong)uVar14 * (ulonglong)uVar23 >> 0x20) + iVar8;
  uVar14 = (int)uVar17 >> 0x1f ^ uVar17;
  uVar23 = uVar18 + uVar15 * uVar3;
  iVar8 = (uint)(uVar23 < uVar15 * uVar3) +
          ((int)uVar15 >> 0x1f) * uVar3 + ((int)uVar6 >> 0x1f) * uVar15 +
          (int)((ulonglong)uVar15 * (ulonglong)uVar3 >> 0x20) +
          (uint)(uVar18 < uVar21) + (int)((ulonglong)(lVar1 * lVar2) >> 0x20) + iVar5;
  uVar6 = (int)uVar19 >> 0x1f ^ uVar20 | uVar16 | uVar23 | (int)uVar7 >> 0x1f ^ uVar13 |
          (int)uVar17 >> 0x1f ^ uVar22;
  if (uVar6 == 0 && ((((uVar10 == 0 && iVar5 == 0) && iVar8 == 0) && uVar4 == 0) && uVar14 == 0)) {
    correlation->r11_real = 0;
    correlation->r01_real = 0;
    correlation->r02_real = 0;
    correlation->r12_real = 0;
    correlation->r22_real = 0;
    correlation->r01_imag = 0;
    correlation->r02_imag = 0;
    correlation->r12_imag = 0;
    correlation->determinant = 0;
    return;
  }
  if ((((uVar10 == 0 && iVar5 == 0) && iVar8 == 0) && uVar4 == 0) && uVar14 == 0) {
    iVar9 = pv_normalize(uVar6 >> 1);
    uVar6 = iVar9 - 2;
    if ((int)uVar6 < 1) {
      uVar3 = -iVar9 + 2;
      uVar6 = -iVar9 - 0x1e;
      uVar14 = (int)uVar7 >> (uVar6 & 0x1f);
      if ((int)uVar6 < 0) {
        uVar14 = (uVar13 >> (uVar3 & 0x1f)) + (uVar7 * 2 << (0x1f - uVar3 & 0x1f));
      }
      uVar21 = (int)uVar17 >> (uVar6 & 0x1f);
      if ((int)uVar6 < 0) {
        uVar21 = (uVar22 >> (uVar3 & 0x1f)) + (uVar17 * 2 << (0x1f - uVar3 & 0x1f));
        uVar17 = (uVar16 >> (uVar3 & 0x1f)) + ((iVar5 << 1) << (0x1f - uVar3 & 0x1f));
        uVar19 = (uVar20 >> (uVar3 & 0x1f)) + ((uVar19 << 1) << (0x1f - uVar3 & 0x1f));
        uVar3 = (uVar23 >> (uVar3 & 0x1f)) + (iVar8 * 2 << (0x1f - uVar3 & 0x1f));
      }
      else {
        uVar17 = iVar5 >> (uVar6 & 0x1f);
        uVar19 = (int)uVar19 >> (uVar6 & 0x1f);
        uVar3 = iVar8 >> (uVar6 & 0x1f);
      }
    }
    else {
      uVar3 = iVar9 + -0x22 >> 0x1f;
      uVar14 = uVar13 << (uVar6 & 0x1f) & uVar3;
      uVar21 = uVar22 << (uVar6 & 0x1f) & uVar3;
      uVar17 = uVar16 << (uVar6 & 0x1f) & uVar3;
      uVar19 = uVar20 << (uVar6 & 0x1f) & uVar3;
      uVar3 = uVar23 << (uVar6 & 0x1f) & uVar3;
    }
    goto LAB_ram_43000dfa;
  }
  iVar9 = pv_normalize();
  uVar6 = -iVar9 + 0x21;
  uVar3 = -iVar9 + 1;
  uVar14 = (int)uVar7 >> (uVar3 & 0x1f);
  if ((int)uVar3 < 0) {
    uVar14 = (uVar13 >> (uVar6 & 0x1f)) + (uVar7 * 2 << (0x1f - uVar6 & 0x1f));
    if ((int)uVar3 < 0) goto LAB_ram_43000efe;
LAB_ram_43000de2:
    uVar21 = (int)uVar17 >> (uVar3 & 0x1f);
    if (-1 < (int)uVar3) goto LAB_ram_43000de6;
LAB_ram_43000ebe:
    uVar17 = (uVar16 >> (uVar6 & 0x1f)) + ((iVar5 << 1) << (0x1f - uVar6 & 0x1f));
    if ((int)uVar3 < 0) goto LAB_ram_43000ed4;
LAB_ram_43000dee:
    uVar19 = (int)uVar19 >> (uVar3 & 0x1f);
  }
  else {
    if (-1 < (int)uVar3) goto LAB_ram_43000de2;
LAB_ram_43000efe:
    uVar21 = (uVar22 >> (uVar6 & 0x1f)) + (uVar17 * 2 << (0x1f - uVar6 & 0x1f));
    if ((int)uVar3 < 0) goto LAB_ram_43000ebe;
LAB_ram_43000de6:
    uVar17 = iVar5 >> (uVar3 & 0x1f);
    if (-1 < (int)uVar3) goto LAB_ram_43000dee;
LAB_ram_43000ed4:
    uVar19 = (uVar20 >> (uVar6 & 0x1f)) + ((uVar19 << 1) << (0x1f - uVar6 & 0x1f));
  }
  if ((int)uVar3 < 0) {
    uVar3 = (uVar23 >> (uVar6 & 0x1f)) + (iVar8 * 2 << (0x1f - uVar6 & 0x1f));
  }
  else {
    uVar3 = iVar8 >> (uVar3 & 0x1f);
  }
LAB_ram_43000dfa:
  correlation->r12_real = uVar19;
  correlation->r11_real = uVar17;
  correlation->r22_real = uVar3;
  correlation->r01_real = uVar14;
  correlation->r02_real = uVar21;
  iVar5 = (uVar19 * uVar19 >> 0x1e) +
          (int)((ulonglong)((longlong)(int)uVar19 * (longlong)(int)uVar19) >> 0x20) * 4;
  correlation->determinant =
       ((uVar17 * uVar3 >> 0x1e) +
       (int)((ulonglong)((longlong)(int)uVar17 * (longlong)(int)uVar3) >> 0x20) * 4) -
       (iVar5 - (iVar5 >> 0x14));
  return;
}
