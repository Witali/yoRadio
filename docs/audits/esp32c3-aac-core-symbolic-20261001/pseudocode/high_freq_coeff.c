/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: high_freq_coeff @ ram:4301216a
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_coeff(int param_1,int param_2,int *param_3,int *param_4,int *param_5)

{
  bool bVar1;
  longlong lVar2;
  longlong lVar3;
  longlong lVar4;
  longlong lVar5;
  longlong lVar6;
  longlong lVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  uint uVar15;
  uint uVar16;
  int *piVar17;
  uint uVar18;
  int *piVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  aac_analysis_fraction_t aStack_5c;
  aac_analysis_autocorrelation_t aStack_54;

  gp = &__global_pointer_;
  iVar21 = 1;
  if (1 < *param_5) {
    do {
      calc_auto_corr(&aStack_54,param_1,param_2,iVar21,0x26);
      iVar20 = iVar21 * 4;
      if (aStack_54.determinant < 1) {
        iVar8 = param_4[1];
        iVar9 = 0;
        *(undefined4 *)(param_3[1] + iVar20) = 0;
        *(undefined4 *)(iVar8 + iVar20) = 0;
        iVar8 = 0;
        bVar1 = false;
        if (aStack_54.r11_real != 0) goto LAB_ram_43012308;
LAB_ram_430121bc:
        iVar10 = *param_3;
        iVar11 = *param_4;
        *(undefined4 *)(iVar10 + iVar20) = 0;
        *(undefined4 *)(iVar11 + iVar20) = 0;
LAB_ram_430121d4:
        iVar8 = iVar8 >> 2;
        iVar9 = iVar9 >> 2;
        if ((0xfffffff <
             (int)(((uint)(iVar9 * iVar9) >> 0x1c) +
                   (int)((ulonglong)((longlong)iVar9 * (longlong)iVar9) >> 0x20) * 0x10 +
                  ((uint)(iVar8 * iVar8) >> 0x1c) +
                  (int)((ulonglong)((longlong)iVar8 * (longlong)iVar8) >> 0x20) * 0x10)) || (bVar1))
        {
          piVar19 = (int *)(iVar10 + iVar20);
          piVar17 = (int *)(iVar11 + iVar20);
          goto LAB_ram_43012204;
        }
      }
      else {
        uVar15 = aStack_54.r12_imag * aStack_54.r01_real;
        lVar2 = (longlong)aStack_54.r12_imag;
        lVar5 = (longlong)aStack_54.r01_real;
        uVar18 = aStack_54.r11_real * aStack_54.r02_imag;
        lVar3 = (longlong)aStack_54.r11_real;
        lVar6 = (longlong)aStack_54.r02_imag;
        uVar16 = aStack_54.r01_imag * aStack_54.r12_real;
        lVar4 = (longlong)aStack_54.r01_imag;
        lVar7 = (longlong)aStack_54.r12_real;
        pv_div(((((uint)(aStack_54.r01_real * aStack_54.r12_real) >> 0x1d) +
                (int)((ulonglong)((longlong)aStack_54.r01_real * (longlong)aStack_54.r12_real) >>
                     0x20) * 8) -
               (((uint)(aStack_54.r01_imag * aStack_54.r12_imag) >> 0x1d) +
               (int)((ulonglong)((longlong)aStack_54.r01_imag * (longlong)aStack_54.r12_imag) >>
                    0x20) * 8)) -
               (((uint)(aStack_54.r11_real * aStack_54.r02_real) >> 0x1d) +
               (int)((ulonglong)((longlong)aStack_54.r11_real * (longlong)aStack_54.r02_real) >>
                    0x20) * 8),aStack_54.determinant,&aStack_5c);
        iVar8 = aStack_5c.mantissa >> (aStack_5c.exponent + 2U & 0x1f);
        pv_div((((uVar15 >> 0x1d) + (int)((ulonglong)(lVar2 * lVar5) >> 0x20) * 8) -
               ((uVar18 >> 0x1d) + (int)((ulonglong)(lVar3 * lVar6) >> 0x20) * 8)) +
               (uVar16 >> 0x1d) + (int)((ulonglong)(lVar4 * lVar7) >> 0x20) * 8,
               aStack_54.determinant,&aStack_5c);
        iVar13 = param_4[1];
        *(int *)(param_3[1] + iVar20) = iVar8;
        iVar9 = aStack_5c.mantissa >> (aStack_5c.exponent + 2U & 0x1f);
        *(int *)(iVar13 + iVar20) = iVar9;
        bVar1 = aStack_5c.exponent < -2;
        if (aStack_54.r11_real == 0) goto LAB_ram_430121bc;
LAB_ram_43012308:
        uVar15 = aStack_54.r12_imag * iVar8;
        iVar13 = aStack_54.r01_imag +
                 ((uint)(iVar9 * aStack_54.r12_real) >> 0x1c) +
                 (int)((ulonglong)((longlong)iVar9 * (longlong)aStack_54.r12_real) >> 0x20) * 0x10;
        lVar2 = (longlong)aStack_54.r12_imag;
        pv_div(-(aStack_54.r01_real +
                 ((uint)(iVar8 * aStack_54.r12_real) >> 0x1c) +
                 (int)((ulonglong)((longlong)iVar8 * (longlong)aStack_54.r12_real) >> 0x20) * 0x10 +
                ((uint)(iVar9 * aStack_54.r12_imag) >> 0x1c) +
                (int)((ulonglong)((longlong)iVar9 * (longlong)aStack_54.r12_imag) >> 0x20) * 0x10),
               aStack_54.r11_real,&aStack_5c);
        iVar22 = aStack_5c.mantissa >> (aStack_5c.exponent + 2U & 0x1f);
        pv_div(((uVar15 >> 0x1c) + (int)((ulonglong)(lVar2 * iVar8) >> 0x20) * 0x10) - iVar13,
               aStack_54.r11_real,&aStack_5c);
        iVar10 = *param_3;
        iVar11 = *param_4;
        iVar13 = aStack_5c.mantissa >> (aStack_5c.exponent + 2U & 0x1f);
        iVar12 = iVar13 >> 2;
        piVar19 = (int *)(iVar10 + iVar20);
        iVar14 = iVar22 >> 2;
        piVar17 = (int *)(iVar11 + iVar20);
        *piVar19 = iVar22;
        *piVar17 = iVar13;
        if ((int)(((uint)(iVar12 * iVar12) >> 0x1c) +
                  (int)((ulonglong)((longlong)iVar12 * (longlong)iVar12) >> 0x20) * 0x10 +
                 ((uint)(iVar14 * iVar14) >> 0x1c) +
                 (int)((ulonglong)((longlong)iVar14 * (longlong)iVar14) >> 0x20) * 0x10) <
            0x10000000) {
          bVar1 = aStack_5c.exponent < -2;
          goto LAB_ram_430121d4;
        }
LAB_ram_43012204:
        iVar8 = param_3[1];
        iVar9 = param_4[1];
        *piVar19 = 0;
        *(undefined4 *)(iVar8 + iVar20) = 0;
        *piVar17 = 0;
        *(undefined4 *)(iVar9 + iVar20) = 0;
      }
      iVar21 = iVar21 + 1;
    } while (iVar21 < *param_5);
  }
  return;
}
