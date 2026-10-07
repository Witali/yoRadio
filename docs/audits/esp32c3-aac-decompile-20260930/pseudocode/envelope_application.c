/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: envelope_application @ ram:42042464
 * Types and parameter counts are inferred; verify against disassembly. */

void envelope_application
               (int param_1,int param_2,int *param_3,int *param_4,int *param_5,uint *param_6,
               int *param_7,int *param_8,int *param_9,int *param_10,int *param_11,int *param_12,
               int param_13,uint *param_14,uint *param_15,int param_16,uint param_17,int param_18,
               int param_19,int param_20,int param_21,int param_22)

{
  int *piVar1;
  int *piVar2;
  size_t sVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  int *piVar15;
  int *piVar16;
  int iVar17;
  int iVar18;
  size_t sVar19;
  int iVar20;
  int *piVar21;
  uint uVar22;
  int iVar23;
  int *piVar24;
  int *piVar25;
  int *piVar26;
  int *piVar27;
  int *piVar28;
  int iVar29;
  int *piVar30;
  uint *puVar31;
  int *piVar32;

  gp = &__global_pointer_;
  iVar29 = (param_16 + 1) * 4;
  piVar26 = (int *)(param_13 + iVar29 + 4);
  piVar21 = (int *)(param_13 + iVar29);
  if (param_20 == 0) {
    iVar18 = *piVar21;
    iVar29 = iVar18 * 2;
    if (iVar29 < *piVar26 << 1) {
      sVar3 = param_21 * 4;
      piVar28 = param_9 + param_21;
      piVar7 = param_11 + param_21;
      piVar6 = param_12 + param_21;
      piVar21 = param_10 + param_21;
      iVar23 = param_21 - param_22;
      iVar18 = iVar18 * 0x180;
      iVar5 = 0;
      sVar19 = param_18 << 2;
      piVar27 = (int *)(param_2 + iVar18);
      piVar25 = (int *)(param_1 + iVar18);
      do {
        if (param_21 < iVar5) {
          if (param_18 < 1) {
            *param_14 = *param_14 + 1 & 3;
          }
          else {
LAB_ram_4204291a:
            iVar18 = 0;
            piVar1 = piVar25;
            piVar8 = piVar27;
            puVar31 = param_6;
            piVar24 = param_5;
            piVar30 = param_4;
            piVar32 = param_3;
            do {
              if (param_22 == 0) {
                iVar12 = *piVar32;
                iVar17 = *piVar30;
                iVar9 = *piVar24;
                uVar22 = *puVar31;
              }
              else {
                iVar13 = iVar18 * 4;
                iVar17 = *(int *)(*piVar21 + iVar13);
                uVar22 = *(uint *)(*piVar6 + iVar13);
                piVar2 = param_12 + iVar23;
                piVar4 = param_10 + iVar23;
                uVar11 = uVar22;
                iVar9 = iVar17;
                if (iVar23 < param_21) {
                  do {
                    piVar15 = piVar4 + 1;
                    if (iVar9 < *(int *)(*piVar4 + iVar13)) {
                      iVar9 = *(int *)(*piVar4 + iVar13);
                    }
                    if ((int)uVar11 < (int)*(uint *)(*piVar2 + iVar13)) {
                      uVar11 = *(uint *)(*piVar2 + iVar13);
                    }
                    piVar2 = piVar2 + 1;
                    piVar4 = piVar15;
                  } while (piVar21 != piVar15);
                  uVar10 = iVar9 - iVar17;
                  uVar14 = uVar11 - uVar22;
                  uVar22 = uVar11;
                  iVar17 = iVar9;
                }
                else {
                  uVar14 = 0;
                  uVar10 = 0;
                }
                iVar12 = ((int)(((uint)(*(int *)(param_9[iVar23 + 3] + iVar13) * 0x134bd280) >> 0x1e
                                ) + (int)((ulonglong)
                                          ((longlong)*(int *)(param_9[iVar23 + 3] + iVar13) *
                                          0x134bd280) >> 0x20) * 4) >>
                         (iVar17 - *(int *)(param_10[iVar23 + 3] + iVar13) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(param_9[iVar23 + 2] + iVar13) * 0xdf67d30) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_9[iVar23 + 2] + iVar13) * 0xdf67d30
                                       ) >> 0x20) * 4) >>
                         (iVar17 - *(int *)(param_10[iVar23 + 2] + iVar13) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(param_9[iVar23] + iVar13) * 0x20982cc) >> 0x1e) +
                               (int)((ulonglong)
                                     ((longlong)*(int *)(param_9[iVar23] + iVar13) * 0x20982cc) >>
                                    0x20) * 4) >>
                         (iVar17 - *(int *)(param_10[iVar23] + iVar13) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(*piVar28 + iVar13) * 0x15555560) >> 0x1e) +
                               (int)((ulonglong)((longlong)*(int *)(*piVar28 + iVar13) * 0x15555560)
                                    >> 0x20) * 4) >> (uVar10 & 0x1f)) +
                         ((int)(((uint)(*(int *)(param_9[iVar23 + 1] + iVar13) * 0x75ed820) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_9[iVar23 + 1] + iVar13) * 0x75ed820
                                       ) >> 0x20) * 4) >>
                         (iVar17 - *(int *)(param_10[iVar23 + 1] + iVar13) & 0x1fU));
                iVar9 = ((int)(((uint)(*(int *)(param_11[iVar23 + 3] + iVar13) * 0x134bd280) >> 0x1e
                               ) + (int)((ulonglong)
                                         ((longlong)*(int *)(param_11[iVar23 + 3] + iVar13) *
                                         0x134bd280) >> 0x20) * 4) >>
                        (uVar22 - *(int *)(param_12[iVar23 + 3] + iVar13) & 0x1f)) +
                        ((int)(((uint)(*(int *)(param_11[iVar23 + 2] + iVar13) * 0xdf67d30) >> 0x1e)
                              + (int)((ulonglong)
                                      ((longlong)*(int *)(param_11[iVar23 + 2] + iVar13) * 0xdf67d30
                                      ) >> 0x20) * 4) >>
                        (uVar22 - *(int *)(param_12[iVar23 + 2] + iVar13) & 0x1f)) +
                        ((int)(((uint)(*(int *)(param_11[iVar23 + 1] + iVar13) * 0x75ed820) >> 0x1e)
                              + (int)((ulonglong)
                                      ((longlong)*(int *)(param_11[iVar23 + 1] + iVar13) * 0x75ed820
                                      ) >> 0x20) * 4) >>
                        (uVar22 - *(int *)(param_12[iVar23 + 1] + iVar13) & 0x1f)) +
                        ((int)(((uint)(*(int *)(param_11[iVar23] + iVar13) * 0x20982cc) >> 0x1e) +
                              (int)((ulonglong)
                                    ((longlong)*(int *)(param_11[iVar23] + iVar13) * 0x20982cc) >>
                                   0x20) * 4) >>
                        (uVar22 - *(int *)(param_12[iVar23] + iVar13) & 0x1f)) +
                        ((int)(((uint)(*(int *)(*piVar7 + iVar13) * 0x15555560) >> 0x1e) +
                              (int)((ulonglong)((longlong)*(int *)(*piVar7 + iVar13) * 0x15555560)
                                   >> 0x20) * 4) >> (uVar14 & 0x1f));
              }
              iVar13 = iVar17 + 0x20;
              iVar20 = (int)((ulonglong)((longlong)iVar12 * (longlong)*piVar1) >> 0x20);
              iVar12 = (int)((ulonglong)((longlong)iVar12 * (longlong)*piVar8) >> 0x20);
              if (iVar13 < 0) {
                if (-0x20 < iVar13) {
                  if (-10 < iVar13) goto LAB_ram_42042984;
                  *piVar1 = iVar20 >> (-iVar13 - 10U & 0x1f);
                  *piVar8 = iVar12 >> (-iVar13 - 10U & 0x1f);
                }
              }
              else {
LAB_ram_42042984:
                *piVar1 = iVar20 << (iVar17 + 0x2aU & 0x1f);
                *piVar8 = iVar12 << (iVar17 + 0x2aU & 0x1f);
              }
              uVar11 = *param_15 + 1 & 0x1ff;
              *param_15 = uVar11;
              if (param_19 == 0) {
                iVar17 = uVar22 + 1;
                iVar13 = (int)((ulonglong)
                               ((longlong)(int)(*(uint *)(rPxx + uVar11 * 4) & 0xffff0000) *
                               (longlong)iVar9) >> 0x20);
                iVar9 = (int)((ulonglong)
                              ((longlong)(int)(*(uint *)(rPxx + uVar11 * 4) << 0x10) *
                              (longlong)iVar9) >> 0x20);
                if (iVar17 < 0) {
                  if (-0x20 < iVar17) {
                    if (iVar17 < -9) {
                      *piVar1 = (iVar13 >> (-iVar17 - 10U & 0x1f)) + *piVar1;
                      *piVar8 = (iVar9 >> (-iVar17 - 10U & 0x1f)) + *piVar8;
                    }
                    else {
                      *piVar1 = (iVar13 << (uVar22 + 0xb & 0x1f)) + *piVar1;
                      *piVar8 = (iVar9 << (uVar22 + 0xb & 0x1f)) + *piVar8;
                    }
                  }
                }
                else {
                  *piVar1 = *piVar1 + (iVar13 << (uVar22 + 0xb & 0x1f));
                  *piVar8 = *piVar8 + (iVar9 << (uVar22 + 0xb & 0x1f));
                }
              }
              iVar18 = iVar18 + 1;
              piVar1 = piVar1 + 1;
              piVar8 = piVar8 + 1;
              piVar32 = piVar32 + 1;
              piVar30 = piVar30 + 1;
              piVar24 = piVar24 + 1;
              puVar31 = puVar31 + 1;
            } while (iVar18 < param_18);
            *param_14 = *param_14 + 1 & 3;
            if (iVar5 < param_21) goto LAB_ram_4204307c;
          }
        }
        else {
          memmove((void *)*piVar28,param_3,sVar19);
          memmove((void *)*piVar21,param_4,sVar19);
          memmove((void *)*piVar7,param_5,sVar19);
          memmove((void *)*piVar6,param_6,sVar19);
          if (0 < param_18) goto LAB_ram_4204291a;
          *param_14 = *param_14 + 1 & 3;
          if (param_21 <= iVar5) goto LAB_ram_42042a16;
LAB_ram_4204307c:
          iVar9 = *param_9;
          iVar18 = *param_11;
          piVar1 = param_11;
          piVar8 = param_9;
          if (param_11 < param_9 + param_21 + 1 && param_9 + 1 < param_11 + param_21 ||
              param_9 < param_11 + param_21 + 1 && param_11 < piVar28) {
            do {
              piVar24 = piVar8 + 1;
              *piVar8 = piVar8[1];
              *piVar1 = piVar1[1];
              piVar1 = piVar1 + 1;
              piVar8 = piVar24;
            } while (piVar28 != piVar24);
          }
          else {
            memmove(param_9,param_9 + 1,sVar3);
            memmove(param_11,param_11 + 1,sVar3);
          }
          *piVar28 = iVar9;
          *piVar7 = iVar18;
          iVar9 = *param_10;
          iVar18 = *param_12;
          piVar1 = param_12;
          piVar8 = param_10;
          if (param_10 < param_12 + param_21 + 1 && param_12 < piVar21 ||
              param_12 < param_10 + param_21 + 1 && param_10 + 1 < param_12 + param_21) {
            do {
              piVar24 = piVar8 + 1;
              *piVar8 = piVar8[1];
              *piVar1 = piVar1[1];
              piVar1 = piVar1 + 1;
              piVar8 = piVar24;
            } while (piVar21 != piVar24);
          }
          else {
            memmove(param_10,param_10 + 1,sVar3);
            memmove(param_12,param_12 + 1,sVar3);
          }
          *piVar21 = iVar9;
          *piVar6 = iVar18;
        }
LAB_ram_42042a16:
        iVar5 = iVar5 + 1;
        piVar25 = piVar25 + 0x30;
        piVar27 = piVar27 + 0x30;
      } while (iVar29 + iVar5 < *piVar26 << 1);
    }
  }
  else {
    if (0 < param_18) {
      iVar18 = *param_8;
      iVar29 = *param_7;
      iVar23 = 0;
      piVar28 = param_7;
      do {
        param_8 = param_8 + 1;
        *piVar28 = iVar29 >> (-iVar18 & 0x1fU);
        iVar18 = *param_8;
        iVar23 = iVar23 + 1;
        piVar28 = piVar28 + 1;
        iVar29 = *piVar28;
      } while (param_18 != iVar23);
    }
    iVar18 = *piVar21;
    iVar29 = iVar18 * 2;
    if (iVar29 < *piVar26 << 1) {
      sVar3 = param_21 * 4;
      piVar6 = param_9 + param_21;
      piVar25 = param_11 + param_21;
      piVar7 = param_12 + param_21;
      piVar27 = param_10 + param_21;
      iVar5 = param_21 - param_22;
      iVar18 = iVar18 * 0x180;
      piVar28 = (int *)(param_2 + iVar18);
      iVar23 = 0;
      piVar21 = (int *)(param_1 + iVar18);
      sVar19 = param_18 << 2;
      if (-1 < param_21) goto LAB_ram_42042f36;
LAB_ram_4204265a:
      if (param_18 < 1) {
        *param_14 = *param_14 + 1 & 3;
        goto LAB_ram_42042f16;
      }
      do {
        iVar18 = 0;
        piVar1 = param_3;
        piVar8 = piVar28;
        piVar24 = piVar21;
        piVar30 = param_7;
        puVar31 = param_6;
        piVar32 = param_5;
        piVar2 = param_4;
        do {
          if (param_22 == 0) {
            iVar12 = *piVar1;
            iVar17 = *piVar2;
            iVar9 = *piVar32;
            uVar22 = *puVar31;
          }
          else {
            iVar13 = iVar18 * 4;
            iVar17 = *(int *)(*piVar27 + iVar13);
            uVar22 = *(uint *)(*piVar7 + iVar13);
            piVar4 = param_12 + iVar5;
            piVar15 = param_10 + iVar5;
            iVar9 = iVar17;
            uVar11 = uVar22;
            if (iVar5 < param_21) {
              do {
                piVar16 = piVar15 + 1;
                if (iVar9 < *(int *)(*piVar15 + iVar13)) {
                  iVar9 = *(int *)(*piVar15 + iVar13);
                }
                if ((int)uVar11 < (int)*(uint *)(*piVar4 + iVar13)) {
                  uVar11 = *(uint *)(*piVar4 + iVar13);
                }
                piVar4 = piVar4 + 1;
                piVar15 = piVar16;
              } while (piVar27 != piVar16);
              uVar10 = iVar9 - iVar17;
              uVar14 = uVar11 - uVar22;
              iVar17 = iVar9;
              uVar22 = uVar11;
            }
            else {
              uVar14 = 0;
              uVar10 = 0;
            }
            iVar12 = ((int)(((uint)(*(int *)(param_9[iVar5 + 3] + iVar13) * 0x134bd280) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar5 + 3] + iVar13) * 0x134bd280) >>
                                0x20) * 4) >>
                     (iVar17 - *(int *)(param_10[iVar5 + 3] + iVar13) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(param_9[iVar5 + 2] + iVar13) * 0xdf67d30) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar5 + 2] + iVar13) * 0xdf67d30) >>
                                0x20) * 4) >>
                     (iVar17 - *(int *)(param_10[iVar5 + 2] + iVar13) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(param_9[iVar5] + iVar13) * 0x20982cc) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar5] + iVar13) * 0x20982cc) >> 0x20)
                           * 4) >> (iVar17 - *(int *)(param_10[iVar5] + iVar13) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(*piVar6 + iVar13) * 0x15555560) >> 0x1e) +
                           (int)((ulonglong)((longlong)*(int *)(*piVar6 + iVar13) * 0x15555560) >>
                                0x20) * 4) >> (uVar10 & 0x1f)) +
                     ((int)(((uint)(*(int *)(param_9[iVar5 + 1] + iVar13) * 0x75ed820) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar5 + 1] + iVar13) * 0x75ed820) >>
                                0x20) * 4) >>
                     (iVar17 - *(int *)(param_10[iVar5 + 1] + iVar13) & 0x1fU));
            iVar9 = ((int)(((uint)(*(int *)(param_11[iVar5 + 3] + iVar13) * 0x134bd280) >> 0x1e) +
                          (int)((ulonglong)
                                ((longlong)*(int *)(param_11[iVar5 + 3] + iVar13) * 0x134bd280) >>
                               0x20) * 4) >>
                    (uVar22 - *(int *)(param_12[iVar5 + 3] + iVar13) & 0x1f)) +
                    ((int)(((uint)(*(int *)(param_11[iVar5 + 2] + iVar13) * 0xdf67d30) >> 0x1e) +
                          (int)((ulonglong)
                                ((longlong)*(int *)(param_11[iVar5 + 2] + iVar13) * 0xdf67d30) >>
                               0x20) * 4) >>
                    (uVar22 - *(int *)(param_12[iVar5 + 2] + iVar13) & 0x1f)) +
                    ((int)(((uint)(*(int *)(param_11[iVar5 + 1] + iVar13) * 0x75ed820) >> 0x1e) +
                          (int)((ulonglong)
                                ((longlong)*(int *)(param_11[iVar5 + 1] + iVar13) * 0x75ed820) >>
                               0x20) * 4) >>
                    (uVar22 - *(int *)(param_12[iVar5 + 1] + iVar13) & 0x1f)) +
                    ((int)(((uint)(*(int *)(param_11[iVar5] + iVar13) * 0x20982cc) >> 0x1e) +
                          (int)((ulonglong)
                                ((longlong)*(int *)(param_11[iVar5] + iVar13) * 0x20982cc) >> 0x20)
                          * 4) >> (uVar22 - *(int *)(param_12[iVar5] + iVar13) & 0x1f)) +
                    ((int)(((uint)(*(int *)(*piVar25 + iVar13) * 0x15555560) >> 0x1e) +
                          (int)((ulonglong)((longlong)*(int *)(*piVar25 + iVar13) * 0x15555560) >>
                               0x20) * 4) >> (uVar14 & 0x1f));
          }
          uVar11 = iVar17 + 0x20;
          iVar20 = (int)((ulonglong)((longlong)iVar12 * (longlong)*piVar24) >> 0x20);
          iVar13 = (int)((ulonglong)((longlong)iVar12 * (longlong)*piVar8) >> 0x20);
          if ((int)uVar11 < 0) {
            if (-0x40 < iVar17) {
              *piVar24 = iVar20 >> (-iVar17 - 0x20U & 0x1f);
              *piVar8 = iVar13 >> (-iVar17 - 0x20U & 0x1f);
            }
          }
          else {
            *piVar24 = iVar20 << (uVar11 & 0x1f);
            *piVar8 = iVar13 << (uVar11 & 0x1f);
          }
          uVar11 = *param_15 + 1 & 0x1ff;
          *param_15 = uVar11;
          iVar17 = *piVar30;
          if (param_19 == 0 && iVar17 == 0) {
            uVar14 = uVar22 + 1;
            iVar13 = (int)((ulonglong)
                           ((longlong)(int)(*(uint *)(rPxx + uVar11 * 4) & 0xffff0000) *
                           (longlong)iVar9) >> 0x20);
            iVar9 = (int)((ulonglong)
                          ((longlong)(int)(*(uint *)(rPxx + uVar11 * 4) << 0x10) * (longlong)iVar9)
                         >> 0x20);
            if ((int)uVar14 < 0) {
              iVar17 = 0;
              if (-0x20 < (int)uVar14) {
                *piVar24 = *piVar24 + (iVar13 >> (~uVar22 & 0x1f));
                *piVar8 = *piVar8 + (iVar9 >> (~uVar22 & 0x1f));
                iVar17 = *piVar30;
              }
            }
            else {
              *piVar24 = *piVar24 + (iVar13 << (uVar14 & 0x1f));
              *piVar8 = *piVar8 + (iVar9 << (uVar14 & 0x1f));
              iVar17 = *piVar30;
            }
          }
          uVar11 = *param_14;
          if ((uVar11 & 1) == 0) {
            if (uVar11 != 0) {
              iVar17 = -iVar17;
            }
            iVar17 = *piVar24 + iVar17;
          }
          else if ((uint)(uVar11 != 1) == ((param_17 & 1) - iVar18 & 1)) {
            *piVar8 = *piVar8 + iVar17;
            iVar17 = *piVar24;
          }
          else {
            *piVar8 = *piVar8 - iVar17;
            iVar17 = *piVar24;
          }
          *piVar24 = iVar17 << 10;
          iVar18 = iVar18 + 1;
          *piVar8 = *piVar8 << 10;
          piVar30 = piVar30 + 1;
          piVar1 = piVar1 + 1;
          piVar2 = piVar2 + 1;
          piVar32 = piVar32 + 1;
          puVar31 = puVar31 + 1;
          piVar8 = piVar8 + 1;
          piVar24 = piVar24 + 1;
        } while (iVar18 < param_18);
        *param_14 = *param_14 + 1 & 3;
        while( true ) {
          if (iVar23 < param_21) {
            iVar9 = *param_9;
            iVar18 = *param_11;
            piVar1 = param_11;
            piVar8 = param_9;
            if (param_11 < param_9 + param_21 + 1 && param_9 + 1 < param_11 + param_21 ||
                param_9 < param_11 + param_21 + 1 && param_11 < piVar6) {
              do {
                piVar24 = piVar8 + 1;
                *piVar8 = piVar8[1];
                *piVar1 = piVar1[1];
                piVar1 = piVar1 + 1;
                piVar8 = piVar24;
              } while (piVar6 != piVar24);
            }
            else {
              memmove(param_9,param_9 + 1,sVar3);
              memmove(param_11,param_11 + 1,sVar3);
            }
            *piVar6 = iVar9;
            *piVar25 = iVar18;
            iVar9 = *param_10;
            iVar18 = *param_12;
            piVar1 = param_12;
            piVar8 = param_10;
            if (param_10 < param_12 + param_21 + 1 && param_12 < piVar27 ||
                param_12 < param_10 + param_21 + 1 && param_10 + 1 < param_12 + param_21) {
              do {
                piVar24 = piVar8 + 1;
                *piVar8 = piVar8[1];
                *piVar1 = piVar1[1];
                piVar1 = piVar1 + 1;
                piVar8 = piVar24;
              } while (piVar27 != piVar24);
            }
            else {
              memmove(param_10,param_10 + 1,sVar3);
              memmove(param_12,param_12 + 1,sVar3);
            }
            *piVar27 = iVar9;
            *piVar7 = iVar18;
          }
LAB_ram_42042f16:
          iVar23 = iVar23 + 1;
          piVar21 = piVar21 + 0x30;
          piVar28 = piVar28 + 0x30;
          if (*piVar26 << 1 <= iVar29 + iVar23) {
            return;
          }
          if (param_21 < iVar23) goto LAB_ram_4204265a;
LAB_ram_42042f36:
          memmove((void *)*piVar6,param_3,sVar19);
          memmove((void *)*piVar27,param_4,sVar19);
          memmove((void *)*piVar25,param_5,sVar19);
          memmove((void *)*piVar7,param_6,sVar19);
          if (0 < param_18) break;
          *param_14 = *param_14 + 1 & 3;
        }
      } while( true );
    }
  }
  return;
}
