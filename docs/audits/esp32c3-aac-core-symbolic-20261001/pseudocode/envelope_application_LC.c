/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: envelope_application_LC @ ram:430019d0
 * Types and parameter counts are inferred; verify against disassembly. */

void envelope_application_LC
               (int param_1,int *param_2,uint *param_3,int *param_4,uint *param_5,int *param_6,
               int *param_7,int param_8,int param_9,uint *param_10,uint *param_11,int param_12,
               uint param_13,int param_14,int param_15)

{
  uint uVar1;
  uint *puVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint *puVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint *puVar14;
  int *piVar15;
  int *piVar16;
  int *piVar17;
  int *piVar18;
  uint uVar19;
  int *piVar20;
  int iStack_3c;

  gp = &__global_pointer_;
  if (param_8 == 0) {
    if (0 < param_14) {
      puVar2 = param_5;
      puVar14 = param_3;
      do {
        uVar1 = *puVar14;
        puVar10 = puVar2 + 1;
        *puVar2 = *puVar2 + 1;
        *puVar14 = uVar1 + 0x1c;
        puVar14 = puVar14 + 1;
        puVar2 = puVar10;
      } while (param_5 + param_14 != puVar10);
    }
    iVar11 = (param_12 + 1) * 4;
    piVar4 = (int *)(iVar11 + 4 + param_9);
    iVar12 = *(int *)(iVar11 + param_9);
    iVar11 = iVar12 * 2;
    if (iVar11 < *piVar4 << 1) {
      piVar17 = (int *)(param_1 + (iVar12 * 0x60 + param_14) * 4);
      do {
        iVar12 = 0;
        piVar15 = piVar17 + -param_14;
        if (0 < param_14) {
          do {
            while( true ) {
              uVar1 = *(uint *)((int)param_3 + iVar12);
              iVar13 = ((uint)(*(int *)((int)param_2 + iVar12) * *piVar15) >> 0x1c) +
                       (int)((ulonglong)
                             ((longlong)*(int *)((int)param_2 + iVar12) * (longlong)*piVar15) >>
                            0x20) * 0x10;
              if ((int)uVar1 < 0) {
                if (-0x1f < (int)uVar1) {
                  *piVar15 = iVar13 >> (-uVar1 & 0x1f);
                }
              }
              else {
                *piVar15 = iVar13 << (uVar1 & 0x1f);
              }
              uVar1 = *param_11 + 1 & 0x1ff;
              *param_11 = uVar1;
              if (param_15 == 0) break;
LAB_ram_43001ab0:
              piVar15 = piVar15 + 1;
              iVar12 = iVar12 + 4;
              if (piVar15 == piVar17) goto LAB_ram_43001dca;
            }
            uVar7 = *(uint *)((int)param_5 + iVar12);
            iVar13 = (int)((ulonglong)
                           ((longlong)((int)*(short *)(rP_LCx + uVar1 * 2) << 0x10) *
                           (longlong)*(int *)((int)param_4 + iVar12)) >> 0x20);
            if (-1 < (int)uVar7) {
              *piVar15 = (iVar13 << (uVar7 & 0x1f)) + *piVar15;
              goto LAB_ram_43001ab0;
            }
            if ((int)uVar7 < -0x1e) goto LAB_ram_43001ab0;
            piVar3 = piVar15 + 1;
            *piVar15 = (iVar13 >> (-uVar7 & 0x1f)) + *piVar15;
            iVar12 = iVar12 + 4;
            piVar15 = piVar3;
          } while (piVar3 != piVar17);
        }
LAB_ram_43001dca:
        iVar11 = iVar11 + 1;
        piVar17 = piVar17 + 0x30;
        *param_10 = *param_10 + 1 & 3;
        if (*piVar4 << 1 <= iVar11) {
          return;
        }
      } while( true );
    }
  }
  else {
    if (0 < param_14) {
      puVar2 = param_3;
      piVar4 = param_7;
      puVar14 = param_5;
      piVar17 = param_6;
      do {
        piVar15 = piVar4 + 1;
        iVar11 = *piVar17 >> (-*piVar4 & 0x1fU);
        *piVar17 = iVar11;
        piVar17 = piVar17 + 1;
        *piVar4 = (int)((ulonglong)((longlong)iVar11 * 0x2160000) >> 0x20);
        *puVar14 = *puVar14 + 1;
        *puVar2 = *puVar2 + 0x1c;
        puVar2 = puVar2 + 1;
        piVar4 = piVar15;
        puVar14 = puVar14 + 1;
      } while (param_7 + param_14 != piVar15);
    }
    iVar11 = (param_12 + 1) * 4;
    piVar4 = (int *)(param_9 + iVar11 + 4);
    iVar11 = *(int *)(iVar11 + param_9);
    iVar12 = iVar11 * 2;
    if (iVar12 < *piVar4 << 1) {
      piVar17 = (int *)(param_1 + iVar11 * 0x180);
      iVar13 = param_14 + -1;
      piVar15 = (int *)((iVar11 * 0x60 + param_14) * 4 + param_1);
      uVar1 = *param_10;
      do {
        while (uVar7 = uVar1 + 1 & 3, (uVar1 + 1 & 1) == 0) {
          uVar19 = *param_3;
          iVar11 = ((uint)(*piVar17 * *param_2) >> 0x1c) +
                   (int)((ulonglong)((longlong)*piVar17 * (longlong)*param_2) >> 0x20) * 0x10;
          if ((int)uVar19 < 0) {
            if (-0x20 < (int)uVar19) {
              *piVar17 = iVar11 >> (-uVar19 & 0x1f);
            }
          }
          else {
            *piVar17 = iVar11 << (uVar19 & 0x1f);
          }
          *param_11 = *param_11 + 1 & 0x1ff;
          iVar11 = *param_7;
          iVar9 = param_7[1];
          if ((uint)(uVar7 != 0) == (param_13 & 1)) {
            iVar9 = -iVar9;
          }
          else {
            iVar11 = -iVar11;
          }
          iVar9 = *piVar17 + iVar9;
          *piVar17 = iVar9;
          piVar17[-1] = piVar17[-1] + iVar11;
          if (param_15 == 0 && *param_6 == 0) {
            uVar19 = *param_5;
            iVar11 = (int)((ulonglong)
                           ((longlong)((int)*(short *)(rP_LCx + *param_11 * 2) << 0x10) *
                           (longlong)*param_4) >> 0x20);
            if ((int)uVar19 < 0) {
              if (-0x20 < (int)uVar19) {
                *piVar17 = (iVar11 >> (-uVar19 & 0x1f)) + iVar9;
              }
            }
            else {
              *piVar17 = (iVar11 << (uVar19 & 0x1f)) + iVar9;
            }
            iVar11 = 0;
            iVar9 = 0;
            if (param_14 < 3) goto LAB_ram_43001faa;
LAB_ram_43001ea8:
            iVar11 = iVar9;
            iVar9 = 1;
            piVar6 = param_7;
            puVar2 = param_3;
            piVar3 = param_2;
            piVar18 = piVar17;
            puVar14 = param_5;
            piVar16 = param_4;
            piVar20 = param_6;
            do {
              piVar20 = piVar20 + 1;
              piVar16 = piVar16 + 1;
              puVar14 = puVar14 + 1;
              piVar18 = piVar18 + 1;
              piVar3 = piVar3 + 1;
              puVar2 = puVar2 + 1;
              uVar19 = *puVar2;
              iVar5 = ((uint)(*piVar18 * *piVar3) >> 0x1c) +
                      (int)((ulonglong)((longlong)*piVar18 * (longlong)*piVar3) >> 0x20) * 0x10;
              if ((int)uVar19 < 0) {
                if (-0x20 < (int)uVar19) {
                  *piVar18 = iVar5 >> (-uVar19 & 0x1f);
                }
              }
              else {
                *piVar18 = iVar5 << (uVar19 & 0x1f);
              }
              *param_11 = *param_11 + 1 & 0x1ff;
              if (iVar11 < 0x10) {
                if ((uint)(uVar7 != 0) == ((param_13 + 1 & 1 ^ 1) + iVar9 & 1)) {
                  *piVar18 = (*piVar6 - piVar6[2]) + *piVar18;
                }
                else {
                  *piVar18 = *piVar18 - (*piVar6 - piVar6[2]);
                }
              }
              if (param_15 == 0 && *piVar20 == 0) {
                uVar19 = *puVar14;
                iVar5 = (int)((ulonglong)
                              ((longlong)((int)*(short *)(rP_LCx + *param_11 * 2) << 0x10) *
                              (longlong)*piVar16) >> 0x20);
                if ((int)uVar19 < 0) {
                  if (-0x20 < (int)uVar19) {
                    *piVar18 = *piVar18 + (iVar5 >> (-uVar19 & 0x1f));
                  }
                }
                else {
                  *piVar18 = *piVar18 + (iVar5 << (uVar19 & 0x1f));
                }
              }
              else {
                iVar11 = iVar11 + 1;
              }
              iVar9 = iVar9 + 1;
              piVar6 = piVar6 + 1;
            } while (iVar9 != iVar13);
            piVar3 = piVar17 + iVar13;
            iVar9 = iVar13 * 4;
            iStack_3c = iVar13;
          }
          else {
            iVar11 = 1;
            iVar9 = 1;
            if (2 < param_14) goto LAB_ram_43001ea8;
LAB_ram_43001faa:
            piVar3 = piVar17 + 1;
            iStack_3c = 1;
            iVar9 = 4;
          }
          uVar19 = *(uint *)((int)param_3 + iVar9);
          iVar5 = ((uint)(*(int *)((int)param_2 + iVar9) * *piVar3) >> 0x1c) +
                  (int)((ulonglong)((longlong)*(int *)((int)param_2 + iVar9) * (longlong)*piVar3) >>
                       0x20) * 0x10;
          if ((int)uVar19 < 0) {
            if (-0x1f < (int)uVar19) {
              *piVar3 = iVar5 >> (-uVar19 & 0x1f);
            }
          }
          else {
            *piVar3 = iVar5 << (uVar19 & 0x1f);
          }
          *param_11 = *param_11 + 1 & 0x1ff;
          if (iVar11 < 0x10) {
            uVar19 = param_13 + iStack_3c;
            iVar11 = *(int *)((int)param_7 + iVar9);
            if ((uVar1 - 1 & 3) >> 1 == (uVar19 & 1)) {
              *piVar3 = *piVar3 - param_7[iStack_3c + 0x3fffffff];
              if ((int)uVar19 < 0x3e) {
                piVar3[1] = piVar3[1] + iVar11;
              }
            }
            else {
              *piVar3 = *piVar3 + param_7[iStack_3c + 0x3fffffff];
              if ((int)uVar19 < 0x3e) {
                piVar3[1] = piVar3[1] - iVar11;
              }
            }
          }
          if (param_15 != 0 || *(int *)((int)param_6 + iVar9) != 0) goto LAB_ram_43001bd0;
          uVar1 = *(uint *)(iVar9 + (int)param_5);
          iVar11 = (int)((ulonglong)
                         ((longlong)((int)*(short *)(rP_LCx + *param_11 * 2) << 0x10) *
                         (longlong)*(int *)((int)param_4 + iVar9)) >> 0x20);
          if (-1 < (int)uVar1) {
            *piVar3 = (iVar11 << (uVar1 & 0x1f)) + *piVar3;
            goto LAB_ram_43001bd0;
          }
          if ((int)uVar1 < -0x1e) goto LAB_ram_43001bd0;
          iVar12 = iVar12 + 1;
          piVar15 = piVar15 + 0x30;
          *piVar3 = *piVar3 + (iVar11 >> (-uVar1 & 0x1f));
          *param_10 = uVar7;
          piVar17 = piVar17 + 0x30;
          uVar1 = uVar7;
          if (*piVar4 << 1 <= iVar12) {
            return;
          }
        }
        iVar11 = 0;
        piVar3 = param_6;
        piVar18 = piVar17;
        if (0 < param_14) {
          do {
            uVar1 = *(uint *)((int)param_3 + iVar11);
            iVar9 = ((uint)(*(int *)((int)param_2 + iVar11) * *piVar18) >> 0x1c) +
                    (int)((ulonglong)
                          ((longlong)*(int *)((int)param_2 + iVar11) * (longlong)*piVar18) >> 0x20)
                    * 0x10;
            if ((int)uVar1 < 0) {
              if (-0x20 < (int)uVar1) {
                *piVar18 = iVar9 >> (-uVar1 & 0x1f);
              }
            }
            else {
              *piVar18 = iVar9 << (uVar1 & 0x1f);
            }
            uVar1 = *param_11 + 1 & 0x1ff;
            *param_11 = uVar1;
            iVar9 = *piVar3;
            iVar5 = *piVar18;
            if (iVar9 == 0 && param_15 == 0) {
              iVar8 = (int)((ulonglong)
                            ((longlong)((int)*(short *)(rP_LCx + uVar1 * 2) << 0x10) *
                            (longlong)*(int *)((int)param_4 + iVar11)) >> 0x20);
              uVar1 = *(uint *)((int)param_5 + iVar11);
              if ((int)uVar1 < 0) {
                iVar9 = 0;
                if (-0x20 < (int)uVar1) {
                  iVar5 = iVar5 + (iVar8 >> (-uVar1 & 0x1f));
                  *piVar18 = iVar5;
                  iVar9 = *piVar3;
                }
              }
              else {
                iVar5 = iVar5 + (iVar8 << (uVar1 & 0x1f));
                *piVar18 = iVar5;
                iVar9 = *piVar3;
              }
            }
            if (*param_10 != 0) {
              iVar9 = -iVar9;
            }
            *piVar18 = iVar5 + iVar9;
            piVar18 = piVar18 + 1;
            iVar11 = iVar11 + 4;
            piVar3 = piVar3 + 1;
          } while (piVar18 != piVar15);
        }
LAB_ram_43001bd0:
        *param_10 = uVar7;
        iVar12 = iVar12 + 1;
        piVar15 = piVar15 + 0x30;
        piVar17 = piVar17 + 0x30;
        uVar1 = uVar7;
        if (*piVar4 << 1 <= iVar12) {
          return;
        }
      } while( true );
    }
  }
  return;
}
