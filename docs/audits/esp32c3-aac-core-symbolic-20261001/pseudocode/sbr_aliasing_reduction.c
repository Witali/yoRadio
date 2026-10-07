/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_aliasing_reduction @ ram:4300fd10
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_aliasing_reduction
               (int param_1,int param_2,int param_3,int param_4,int param_5,int *param_6,int param_7
               ,int param_8,aac_analysis_sqrt_cache_t *param_9,int *param_10)

{
  bool bVar1;
  bool bVar2;
  int32_t iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int *piVar16;
  int *piVar17;
  int *piVar18;
  int iVar19;
  int iVar20;
  int *piVar21;
  int iVar22;
  int iVar23;
  int *piStack_84;
  int iStack_80;
  aac_analysis_fraction_t aStack_50;
  aac_analysis_fraction_t aaStack_48 [2];

  gp = &__global_pointer_;
  if (0 < param_7 + -1) {
    iVar23 = param_7 + param_8;
    iVar4 = param_8 * 4 + param_1;
    iVar15 = param_8 + 1;
    iVar22 = 0;
    bVar1 = false;
LAB_ram_4300fd58:
    do {
      if ((*(int *)(iVar4 + 4) == 0) || (*param_6 != 0)) {
        piVar5 = param_10 + iVar22;
        if (bVar1) {
          *piVar5 = iVar15 + -1;
          iVar22 = iVar22 + 1;
          bVar1 = false;
          if (*param_6 == 0) {
            *piVar5 = iVar15;
            iVar15 = iVar15 + 1;
            iVar4 = iVar4 + 4;
            param_6 = param_6 + 1;
            bVar2 = false;
            if (iVar23 == iVar15) break;
            goto LAB_ram_4300fd58;
          }
        }
      }
      else if (!bVar1) {
        param_10[iVar22] = iVar15 + -1;
        iVar22 = iVar22 + 1;
        bVar1 = true;
      }
      iVar15 = iVar15 + 1;
      iVar4 = iVar4 + 4;
      param_6 = param_6 + 1;
      bVar2 = bVar1;
    } while (iVar23 != iVar15);
    if (bVar2) {
      param_10[iVar22] = iVar23;
      iVar22 = iVar22 + 1;
    }
    if (0 < iVar22 >> 1) {
      piStack_84 = param_10;
      iStack_80 = 0;
      do {
        iVar15 = *piStack_84;
        iVar23 = piStack_84[1];
        iVar4 = iVar15 - param_8;
        if (iVar15 < iVar23) {
          iVar19 = iVar4 * 4;
          iVar7 = -100;
          piVar18 = (int *)(param_5 + iVar19);
          iVar20 = -100;
          piVar17 = (int *)(param_3 + iVar19);
          iVar6 = iVar23 - param_8;
          piVar5 = piVar18;
          piVar8 = piVar17;
          iVar12 = iVar4;
          do {
            iVar9 = *piVar5;
            iVar12 = iVar12 + 1;
            piVar5 = piVar5 + 1;
            if (iVar20 < iVar9) {
              iVar20 = iVar9;
            }
            iVar13 = *piVar8;
            piVar8 = piVar8 + 1;
            iVar9 = iVar13 * 2 + iVar9;
            if (iVar7 < iVar9) {
              iVar7 = iVar9;
            }
          } while (iVar12 < iVar6);
          iVar12 = 0;
          if (iVar15 < iVar23) {
            iVar12 = (iVar6 + -1) - iVar4;
          }
          iVar12 = iVar12 + 1;
          iVar9 = pv_normalize(iVar12);
          iVar7 = (0x3b - iVar9) + iVar7;
          piVar16 = (int *)(param_4 + iVar19);
          iVar13 = 0;
          iVar10 = 0;
          piVar5 = piVar18;
          piVar8 = piVar17;
          piVar21 = (int *)(param_2 + iVar19);
          iVar9 = iVar4;
          do {
            iVar9 = iVar9 + 1;
            iVar10 = iVar10 + (*piVar16 >> (iVar20 - *piVar5 & 0x1fU));
            if (iVar7 - (*piVar8 * 2 + *piVar5) < 0x3c) {
              iVar14 = *piVar21;
              *piVar21 = ((uint)(iVar14 * iVar14) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar14 * (longlong)iVar14) >> 0x20) * 0x10;
              iVar14 = *piVar8 * 2 + 0x1c;
              *piVar8 = iVar14;
              iVar13 = iVar13 + ((int)(((uint)(*piVar21 * *piVar16) >> 0x1c) +
                                      (int)((ulonglong)((longlong)*piVar21 * (longlong)*piVar16) >>
                                           0x20) * 0x10) >> (iVar7 - (iVar14 + *piVar5) & 0x1fU));
            }
            piVar16 = piVar16 + 1;
            piVar5 = piVar5 + 1;
            piVar8 = piVar8 + 1;
            piVar21 = piVar21 + 1;
          } while (iVar9 < iVar6);
          pv_div(iVar13,iVar10,&aStack_50);
          iVar9 = (-aStack_50.exponent - iVar20) + -2 + iVar7;
          piVar21 = (int *)(iVar15 * 4 + param_1);
          piVar5 = piVar17;
          piVar8 = (int *)(param_2 + iVar19);
          iVar20 = iVar4;
          do {
            iVar10 = *piVar21;
            if ((iVar20 < param_7 + -1) && (iVar10 < piVar21[1])) {
              iVar10 = piVar21[1];
            }
            iVar11 = *piVar5;
            iVar20 = iVar20 + 1;
            iVar14 = iVar11;
            if (iVar11 < iVar9) {
              iVar14 = iVar9;
            }
            iVar14 = iVar14 + 1;
            piVar21 = piVar21 + 1;
            *piVar8 = ((int)(((uint)((0x40000000 - iVar10) * *piVar8) >> 0x1e) +
                            (int)((ulonglong)((longlong)(0x40000000 - iVar10) * (longlong)*piVar8)
                                 >> 0x20) * 4) >> (iVar14 - iVar11 & 0x1fU)) +
                      ((int)(((uint)(iVar10 * aStack_50.mantissa) >> 0x1e) +
                            (int)((ulonglong)((longlong)iVar10 * (longlong)aStack_50.mantissa) >>
                                 0x20) * 4) >> (iVar14 - iVar9 & 0x1fU));
            *piVar5 = iVar14;
            piVar5 = piVar5 + 1;
            piVar8 = piVar8 + 1;
          } while (iVar20 < iVar6);
          iVar20 = -100;
          iVar9 = iVar4;
          do {
            iVar10 = *piVar17;
            iVar9 = iVar9 + 1;
            piVar17 = piVar17 + 1;
            if (iVar20 < iVar10 + *piVar18) {
              iVar20 = iVar10 + *piVar18;
            }
            piVar18 = piVar18 + 1;
          } while (iVar9 < iVar6);
          for (; iVar12 != 0; iVar12 = iVar12 >> 1) {
            iVar20 = iVar20 + 1;
          }
          iVar9 = 0;
          piVar18 = (int *)(param_4 + iVar19);
          piVar5 = (int *)(param_2 + iVar19);
          piVar8 = (int *)(param_5 + iVar19);
          piVar17 = (int *)(param_3 + iVar19);
          iVar12 = iVar4;
          do {
            iVar11 = *piVar18;
            iVar14 = *piVar5;
            iVar10 = *piVar17;
            iVar12 = iVar12 + 1;
            piVar5 = piVar5 + 1;
            piVar18 = piVar18 + 1;
            piVar17 = piVar17 + 1;
            iVar9 = iVar9 + ((int)(((uint)(iVar14 * iVar11) >> 0x1c) +
                                  (int)((ulonglong)((longlong)iVar14 * (longlong)iVar11) >> 0x20) *
                                  0x10) >> ((iVar20 - iVar10) - *piVar8 & 0x1fU));
            piVar8 = piVar8 + 1;
          } while (iVar12 < iVar6);
          if (iVar9 == 0) goto LAB_ram_4301000c;
          pv_div(iVar13,iVar9,&aStack_50);
          iVar3 = aStack_50.mantissa;
          iVar15 = (iVar7 - iVar20) - aStack_50.exponent;
          piVar5 = (int *)(param_3 + iVar19);
          piVar8 = (int *)(param_2 + iVar19);
          do {
            iVar4 = iVar4 + 1;
            pv_sqrt(((uint)(iVar3 * *piVar8) >> 0x1e) +
                    (int)((ulonglong)((longlong)iVar3 * (longlong)*piVar8) >> 0x20) * 4,
                    *piVar5 + iVar15 + 0x1e,aaStack_48,param_9);
            *piVar8 = aaStack_48[0].mantissa;
            *piVar5 = aaStack_48[0].exponent;
            piVar5 = piVar5 + 1;
            piVar8 = piVar8 + 1;
          } while (iVar4 < iVar6);
        }
        else {
          pv_normalize(0);
          pv_div(0,0,&aStack_50);
LAB_ram_4301000c:
          memset(param_2 + iVar4 * 4,0,(iVar23 - iVar15) * 4);
          memset(param_3 + iVar4 * 4,0,(iVar23 - iVar15) * 4);
        }
        iStack_80 = iStack_80 + 1;
        piStack_84 = piStack_84 + 2;
      } while (iVar22 >> 1 != iStack_80);
    }
  }
  return;
}
