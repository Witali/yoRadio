/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: envelope_application @ ram:430021d8
 * Types and parameter counts are inferred; verify against disassembly. */

void envelope_application
               (int param_1,int param_2,int *param_3,int *param_4,int *param_5,uint *param_6,
               int *param_7,int *param_8,int *param_9,int *param_10,int *param_11,int *param_12,
               int param_13,uint *param_14,uint *param_15,int param_16,uint param_17,int param_18,
               int param_19,int param_20,int param_21,int param_22)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  uint uVar15;
  int *piVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
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
    iVar19 = *piVar21;
    iVar29 = iVar19 * 2;
    if (iVar29 < *piVar26 << 1) {
      iVar23 = param_21 * 4;
      piVar28 = param_9 + param_21;
      piVar8 = param_11 + param_21;
      piVar7 = param_12 + param_21;
      piVar21 = param_10 + param_21;
      iVar4 = param_21 - param_22;
      iVar19 = iVar19 * 0x180;
      iVar3 = 0;
      iVar6 = param_18 << 2;
      piVar27 = (int *)(param_2 + iVar19);
      piVar25 = (int *)(param_1 + iVar19);
      do {
        if (param_21 < iVar3) {
          if (param_18 < 1) {
            *param_14 = *param_14 + 1 & 3;
          }
          else {
LAB_ram_4300268e:
            iVar19 = 0;
            piVar1 = piVar25;
            piVar9 = piVar27;
            puVar31 = param_6;
            piVar24 = param_5;
            piVar30 = param_4;
            piVar32 = param_3;
            do {
              if (param_22 == 0) {
                iVar13 = *piVar32;
                iVar18 = *piVar30;
                iVar10 = *piVar24;
                uVar22 = *puVar31;
              }
              else {
                iVar14 = iVar19 * 4;
                iVar18 = *(int *)(*piVar21 + iVar14);
                uVar22 = *(uint *)(*piVar7 + iVar14);
                piVar2 = param_12 + iVar4;
                piVar5 = param_10 + iVar4;
                uVar12 = uVar22;
                iVar10 = iVar18;
                if (iVar4 < param_21) {
                  do {
                    piVar16 = piVar5 + 1;
                    if (iVar10 < *(int *)(*piVar5 + iVar14)) {
                      iVar10 = *(int *)(*piVar5 + iVar14);
                    }
                    if ((int)uVar12 < (int)*(uint *)(*piVar2 + iVar14)) {
                      uVar12 = *(uint *)(*piVar2 + iVar14);
                    }
                    piVar2 = piVar2 + 1;
                    piVar5 = piVar16;
                  } while (piVar21 != piVar16);
                  uVar11 = iVar10 - iVar18;
                  uVar15 = uVar12 - uVar22;
                  uVar22 = uVar12;
                  iVar18 = iVar10;
                }
                else {
                  uVar15 = 0;
                  uVar11 = 0;
                }
                iVar13 = ((int)(((uint)(*(int *)(param_9[iVar4 + 3] + iVar14) * 0x134bd280) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_9[iVar4 + 3] + iVar14) * 0x134bd280
                                       ) >> 0x20) * 4) >>
                         (iVar18 - *(int *)(param_10[iVar4 + 3] + iVar14) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(param_9[iVar4 + 2] + iVar14) * 0xdf67d30) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_9[iVar4 + 2] + iVar14) * 0xdf67d30)
                                      >> 0x20) * 4) >>
                         (iVar18 - *(int *)(param_10[iVar4 + 2] + iVar14) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(param_9[iVar4] + iVar14) * 0x20982cc) >> 0x1e) +
                               (int)((ulonglong)
                                     ((longlong)*(int *)(param_9[iVar4] + iVar14) * 0x20982cc) >>
                                    0x20) * 4) >>
                         (iVar18 - *(int *)(param_10[iVar4] + iVar14) & 0x1fU)) +
                         ((int)(((uint)(*(int *)(*piVar28 + iVar14) * 0x15555560) >> 0x1e) +
                               (int)((ulonglong)((longlong)*(int *)(*piVar28 + iVar14) * 0x15555560)
                                    >> 0x20) * 4) >> (uVar11 & 0x1f)) +
                         ((int)(((uint)(*(int *)(param_9[iVar4 + 1] + iVar14) * 0x75ed820) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_9[iVar4 + 1] + iVar14) * 0x75ed820)
                                      >> 0x20) * 4) >>
                         (iVar18 - *(int *)(param_10[iVar4 + 1] + iVar14) & 0x1fU));
                iVar10 = ((int)(((uint)(*(int *)(param_11[iVar4 + 3] + iVar14) * 0x134bd280) >> 0x1e
                                ) + (int)((ulonglong)
                                          ((longlong)*(int *)(param_11[iVar4 + 3] + iVar14) *
                                          0x134bd280) >> 0x20) * 4) >>
                         (uVar22 - *(int *)(param_12[iVar4 + 3] + iVar14) & 0x1f)) +
                         ((int)(((uint)(*(int *)(param_11[iVar4 + 2] + iVar14) * 0xdf67d30) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_11[iVar4 + 2] + iVar14) * 0xdf67d30
                                       ) >> 0x20) * 4) >>
                         (uVar22 - *(int *)(param_12[iVar4 + 2] + iVar14) & 0x1f)) +
                         ((int)(((uint)(*(int *)(param_11[iVar4 + 1] + iVar14) * 0x75ed820) >> 0x1e)
                               + (int)((ulonglong)
                                       ((longlong)*(int *)(param_11[iVar4 + 1] + iVar14) * 0x75ed820
                                       ) >> 0x20) * 4) >>
                         (uVar22 - *(int *)(param_12[iVar4 + 1] + iVar14) & 0x1f)) +
                         ((int)(((uint)(*(int *)(param_11[iVar4] + iVar14) * 0x20982cc) >> 0x1e) +
                               (int)((ulonglong)
                                     ((longlong)*(int *)(param_11[iVar4] + iVar14) * 0x20982cc) >>
                                    0x20) * 4) >>
                         (uVar22 - *(int *)(param_12[iVar4] + iVar14) & 0x1f)) +
                         ((int)(((uint)(*(int *)(*piVar8 + iVar14) * 0x15555560) >> 0x1e) +
                               (int)((ulonglong)((longlong)*(int *)(*piVar8 + iVar14) * 0x15555560)
                                    >> 0x20) * 4) >> (uVar15 & 0x1f));
              }
              iVar14 = iVar18 + 0x20;
              iVar20 = (int)((ulonglong)((longlong)iVar13 * (longlong)*piVar1) >> 0x20);
              iVar13 = (int)((ulonglong)((longlong)iVar13 * (longlong)*piVar9) >> 0x20);
              if (iVar14 < 0) {
                if (-0x20 < iVar14) {
                  if (-10 < iVar14) goto LAB_ram_430026f8;
                  *piVar1 = iVar20 >> (-iVar14 - 10U & 0x1f);
                  *piVar9 = iVar13 >> (-iVar14 - 10U & 0x1f);
                }
              }
              else {
LAB_ram_430026f8:
                *piVar1 = iVar20 << (iVar18 + 0x2aU & 0x1f);
                *piVar9 = iVar13 << (iVar18 + 0x2aU & 0x1f);
              }
              uVar12 = *param_15 + 1 & 0x1ff;
              *param_15 = uVar12;
              if (param_19 == 0) {
                iVar18 = uVar22 + 1;
                iVar14 = (int)((ulonglong)
                               ((longlong)(int)(*(uint *)(rPxx + uVar12 * 4) & 0xffff0000) *
                               (longlong)iVar10) >> 0x20);
                iVar10 = (int)((ulonglong)
                               ((longlong)(int)(*(uint *)(rPxx + uVar12 * 4) << 0x10) *
                               (longlong)iVar10) >> 0x20);
                if (iVar18 < 0) {
                  if (-0x20 < iVar18) {
                    if (iVar18 < -9) {
                      *piVar1 = (iVar14 >> (-iVar18 - 10U & 0x1f)) + *piVar1;
                      *piVar9 = (iVar10 >> (-iVar18 - 10U & 0x1f)) + *piVar9;
                    }
                    else {
                      *piVar1 = (iVar14 << (uVar22 + 0xb & 0x1f)) + *piVar1;
                      *piVar9 = (iVar10 << (uVar22 + 0xb & 0x1f)) + *piVar9;
                    }
                  }
                }
                else {
                  *piVar1 = *piVar1 + (iVar14 << (uVar22 + 0xb & 0x1f));
                  *piVar9 = *piVar9 + (iVar10 << (uVar22 + 0xb & 0x1f));
                }
              }
              iVar19 = iVar19 + 1;
              piVar1 = piVar1 + 1;
              piVar9 = piVar9 + 1;
              piVar32 = piVar32 + 1;
              piVar30 = piVar30 + 1;
              piVar24 = piVar24 + 1;
              puVar31 = puVar31 + 1;
            } while (iVar19 < param_18);
            *param_14 = *param_14 + 1 & 3;
            if (iVar3 < param_21) goto LAB_ram_43002df0;
          }
        }
        else {
          memmove(*piVar28,param_3,iVar6);
          memmove(*piVar21,param_4,iVar6);
          memmove(*piVar8,param_5,iVar6);
          memmove(*piVar7,param_6,iVar6);
          if (0 < param_18) goto LAB_ram_4300268e;
          *param_14 = *param_14 + 1 & 3;
          if (param_21 <= iVar3) goto LAB_ram_4300278a;
LAB_ram_43002df0:
          iVar10 = *param_9;
          iVar19 = *param_11;
          piVar1 = param_11;
          piVar9 = param_9;
          if (param_11 < param_9 + param_21 + 1 && param_9 + 1 < param_11 + param_21 ||
              param_9 < param_11 + param_21 + 1 && param_11 < piVar28) {
            do {
              piVar24 = piVar9 + 1;
              *piVar9 = piVar9[1];
              *piVar1 = piVar1[1];
              piVar1 = piVar1 + 1;
              piVar9 = piVar24;
            } while (piVar28 != piVar24);
          }
          else {
            memmove(param_9,param_9 + 1,iVar23);
            memmove(param_11,param_11 + 1,iVar23);
          }
          *piVar28 = iVar10;
          *piVar8 = iVar19;
          iVar10 = *param_10;
          iVar19 = *param_12;
          piVar1 = param_12;
          piVar9 = param_10;
          if (param_10 < param_12 + param_21 + 1 && param_12 < piVar21 ||
              param_12 < param_10 + param_21 + 1 && param_10 + 1 < param_12 + param_21) {
            do {
              piVar24 = piVar9 + 1;
              *piVar9 = piVar9[1];
              *piVar1 = piVar1[1];
              piVar1 = piVar1 + 1;
              piVar9 = piVar24;
            } while (piVar21 != piVar24);
          }
          else {
            memmove(param_10,param_10 + 1,iVar23);
            memmove(param_12,param_12 + 1,iVar23);
          }
          *piVar21 = iVar10;
          *piVar7 = iVar19;
        }
LAB_ram_4300278a:
        iVar3 = iVar3 + 1;
        piVar25 = piVar25 + 0x30;
        piVar27 = piVar27 + 0x30;
      } while (iVar29 + iVar3 < *piVar26 << 1);
    }
  }
  else {
    if (0 < param_18) {
      iVar19 = *param_8;
      iVar29 = *param_7;
      iVar23 = 0;
      piVar28 = param_7;
      do {
        param_8 = param_8 + 1;
        *piVar28 = iVar29 >> (-iVar19 & 0x1fU);
        iVar19 = *param_8;
        iVar23 = iVar23 + 1;
        piVar28 = piVar28 + 1;
        iVar29 = *piVar28;
      } while (param_18 != iVar23);
    }
    iVar19 = *piVar21;
    iVar29 = iVar19 * 2;
    if (iVar29 < *piVar26 << 1) {
      iVar4 = param_21 * 4;
      piVar7 = param_9 + param_21;
      piVar25 = param_11 + param_21;
      piVar8 = param_12 + param_21;
      piVar27 = param_10 + param_21;
      iVar6 = param_21 - param_22;
      iVar19 = iVar19 * 0x180;
      piVar28 = (int *)(param_2 + iVar19);
      iVar23 = 0;
      piVar21 = (int *)(param_1 + iVar19);
      iVar19 = param_18 << 2;
      if (-1 < param_21) goto LAB_ram_43002caa;
LAB_ram_430023ce:
      if (param_18 < 1) {
        *param_14 = *param_14 + 1 & 3;
        goto LAB_ram_43002c8a;
      }
      do {
        iVar3 = 0;
        piVar1 = param_3;
        piVar9 = piVar28;
        piVar24 = piVar21;
        piVar30 = param_7;
        puVar31 = param_6;
        piVar32 = param_5;
        piVar2 = param_4;
        do {
          if (param_22 == 0) {
            iVar13 = *piVar1;
            iVar18 = *piVar2;
            iVar10 = *piVar32;
            uVar22 = *puVar31;
          }
          else {
            iVar14 = iVar3 * 4;
            iVar18 = *(int *)(*piVar27 + iVar14);
            uVar22 = *(uint *)(*piVar8 + iVar14);
            piVar5 = param_12 + iVar6;
            piVar16 = param_10 + iVar6;
            iVar10 = iVar18;
            uVar12 = uVar22;
            if (iVar6 < param_21) {
              do {
                piVar17 = piVar16 + 1;
                if (iVar10 < *(int *)(*piVar16 + iVar14)) {
                  iVar10 = *(int *)(*piVar16 + iVar14);
                }
                if ((int)uVar12 < (int)*(uint *)(*piVar5 + iVar14)) {
                  uVar12 = *(uint *)(*piVar5 + iVar14);
                }
                piVar5 = piVar5 + 1;
                piVar16 = piVar17;
              } while (piVar27 != piVar17);
              uVar11 = iVar10 - iVar18;
              uVar15 = uVar12 - uVar22;
              iVar18 = iVar10;
              uVar22 = uVar12;
            }
            else {
              uVar15 = 0;
              uVar11 = 0;
            }
            iVar13 = ((int)(((uint)(*(int *)(param_9[iVar6 + 3] + iVar14) * 0x134bd280) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar6 + 3] + iVar14) * 0x134bd280) >>
                                0x20) * 4) >>
                     (iVar18 - *(int *)(param_10[iVar6 + 3] + iVar14) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(param_9[iVar6 + 2] + iVar14) * 0xdf67d30) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar6 + 2] + iVar14) * 0xdf67d30) >>
                                0x20) * 4) >>
                     (iVar18 - *(int *)(param_10[iVar6 + 2] + iVar14) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(param_9[iVar6] + iVar14) * 0x20982cc) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar6] + iVar14) * 0x20982cc) >> 0x20)
                           * 4) >> (iVar18 - *(int *)(param_10[iVar6] + iVar14) & 0x1fU)) +
                     ((int)(((uint)(*(int *)(*piVar7 + iVar14) * 0x15555560) >> 0x1e) +
                           (int)((ulonglong)((longlong)*(int *)(*piVar7 + iVar14) * 0x15555560) >>
                                0x20) * 4) >> (uVar11 & 0x1f)) +
                     ((int)(((uint)(*(int *)(param_9[iVar6 + 1] + iVar14) * 0x75ed820) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_9[iVar6 + 1] + iVar14) * 0x75ed820) >>
                                0x20) * 4) >>
                     (iVar18 - *(int *)(param_10[iVar6 + 1] + iVar14) & 0x1fU));
            iVar10 = ((int)(((uint)(*(int *)(param_11[iVar6 + 3] + iVar14) * 0x134bd280) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_11[iVar6 + 3] + iVar14) * 0x134bd280) >>
                                0x20) * 4) >>
                     (uVar22 - *(int *)(param_12[iVar6 + 3] + iVar14) & 0x1f)) +
                     ((int)(((uint)(*(int *)(param_11[iVar6 + 2] + iVar14) * 0xdf67d30) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_11[iVar6 + 2] + iVar14) * 0xdf67d30) >>
                                0x20) * 4) >>
                     (uVar22 - *(int *)(param_12[iVar6 + 2] + iVar14) & 0x1f)) +
                     ((int)(((uint)(*(int *)(param_11[iVar6 + 1] + iVar14) * 0x75ed820) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_11[iVar6 + 1] + iVar14) * 0x75ed820) >>
                                0x20) * 4) >>
                     (uVar22 - *(int *)(param_12[iVar6 + 1] + iVar14) & 0x1f)) +
                     ((int)(((uint)(*(int *)(param_11[iVar6] + iVar14) * 0x20982cc) >> 0x1e) +
                           (int)((ulonglong)
                                 ((longlong)*(int *)(param_11[iVar6] + iVar14) * 0x20982cc) >> 0x20)
                           * 4) >> (uVar22 - *(int *)(param_12[iVar6] + iVar14) & 0x1f)) +
                     ((int)(((uint)(*(int *)(*piVar25 + iVar14) * 0x15555560) >> 0x1e) +
                           (int)((ulonglong)((longlong)*(int *)(*piVar25 + iVar14) * 0x15555560) >>
                                0x20) * 4) >> (uVar15 & 0x1f));
          }
          uVar12 = iVar18 + 0x20;
          iVar20 = (int)((ulonglong)((longlong)iVar13 * (longlong)*piVar24) >> 0x20);
          iVar14 = (int)((ulonglong)((longlong)iVar13 * (longlong)*piVar9) >> 0x20);
          if ((int)uVar12 < 0) {
            if (-0x40 < iVar18) {
              *piVar24 = iVar20 >> (-iVar18 - 0x20U & 0x1f);
              *piVar9 = iVar14 >> (-iVar18 - 0x20U & 0x1f);
            }
          }
          else {
            *piVar24 = iVar20 << (uVar12 & 0x1f);
            *piVar9 = iVar14 << (uVar12 & 0x1f);
          }
          uVar12 = *param_15 + 1 & 0x1ff;
          *param_15 = uVar12;
          iVar18 = *piVar30;
          if (param_19 == 0 && iVar18 == 0) {
            uVar15 = uVar22 + 1;
            iVar14 = (int)((ulonglong)
                           ((longlong)(int)(*(uint *)(rPxx + uVar12 * 4) & 0xffff0000) *
                           (longlong)iVar10) >> 0x20);
            iVar10 = (int)((ulonglong)
                           ((longlong)(int)(*(uint *)(rPxx + uVar12 * 4) << 0x10) * (longlong)iVar10
                           ) >> 0x20);
            if ((int)uVar15 < 0) {
              iVar18 = 0;
              if (-0x20 < (int)uVar15) {
                *piVar24 = *piVar24 + (iVar14 >> (~uVar22 & 0x1f));
                *piVar9 = *piVar9 + (iVar10 >> (~uVar22 & 0x1f));
                iVar18 = *piVar30;
              }
            }
            else {
              *piVar24 = *piVar24 + (iVar14 << (uVar15 & 0x1f));
              *piVar9 = *piVar9 + (iVar10 << (uVar15 & 0x1f));
              iVar18 = *piVar30;
            }
          }
          uVar12 = *param_14;
          if ((uVar12 & 1) == 0) {
            if (uVar12 != 0) {
              iVar18 = -iVar18;
            }
            iVar18 = *piVar24 + iVar18;
          }
          else if ((uint)(uVar12 != 1) == ((param_17 & 1) - iVar3 & 1)) {
            *piVar9 = *piVar9 + iVar18;
            iVar18 = *piVar24;
          }
          else {
            *piVar9 = *piVar9 - iVar18;
            iVar18 = *piVar24;
          }
          *piVar24 = iVar18 << 10;
          iVar3 = iVar3 + 1;
          *piVar9 = *piVar9 << 10;
          piVar30 = piVar30 + 1;
          piVar1 = piVar1 + 1;
          piVar2 = piVar2 + 1;
          piVar32 = piVar32 + 1;
          puVar31 = puVar31 + 1;
          piVar9 = piVar9 + 1;
          piVar24 = piVar24 + 1;
        } while (iVar3 < param_18);
        *param_14 = *param_14 + 1 & 3;
        while( true ) {
          if (iVar23 < param_21) {
            iVar10 = *param_9;
            iVar3 = *param_11;
            piVar1 = param_11;
            piVar9 = param_9;
            if (param_11 < param_9 + param_21 + 1 && param_9 + 1 < param_11 + param_21 ||
                param_9 < param_11 + param_21 + 1 && param_11 < piVar7) {
              do {
                piVar24 = piVar9 + 1;
                *piVar9 = piVar9[1];
                *piVar1 = piVar1[1];
                piVar1 = piVar1 + 1;
                piVar9 = piVar24;
              } while (piVar7 != piVar24);
            }
            else {
              memmove(param_9,param_9 + 1,iVar4);
              memmove(param_11,param_11 + 1,iVar4);
            }
            *piVar7 = iVar10;
            *piVar25 = iVar3;
            iVar10 = *param_10;
            iVar3 = *param_12;
            piVar1 = param_12;
            piVar9 = param_10;
            if (param_10 < param_12 + param_21 + 1 && param_12 < piVar27 ||
                param_12 < param_10 + param_21 + 1 && param_10 + 1 < param_12 + param_21) {
              do {
                piVar24 = piVar9 + 1;
                *piVar9 = piVar9[1];
                *piVar1 = piVar1[1];
                piVar1 = piVar1 + 1;
                piVar9 = piVar24;
              } while (piVar27 != piVar24);
            }
            else {
              memmove(param_10,param_10 + 1,iVar4);
              memmove(param_12,param_12 + 1,iVar4);
            }
            *piVar27 = iVar10;
            *piVar8 = iVar3;
          }
LAB_ram_43002c8a:
          iVar23 = iVar23 + 1;
          piVar21 = piVar21 + 0x30;
          piVar28 = piVar28 + 0x30;
          if (*piVar26 << 1 <= iVar29 + iVar23) {
            return;
          }
          if (param_21 < iVar23) goto LAB_ram_430023ce;
LAB_ram_43002caa:
          memmove(*piVar7,param_3,iVar19);
          memmove(*piVar27,param_4,iVar19);
          memmove(*piVar25,param_5,iVar19);
          memmove(*piVar8,param_6,iVar19);
          if (0 < param_18) break;
          *param_14 = *param_14 + 1 & 3;
        }
      } while( true );
    }
  }
  return;
}
