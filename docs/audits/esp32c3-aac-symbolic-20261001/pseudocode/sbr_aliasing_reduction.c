/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_aliasing_reduction @ ram:4300fd10
 * Types and parameter counts are inferred; verify against disassembly. */

void sbr_aliasing_reduction
               (int param_1,int param_2,int param_3,int param_4,int param_5,int *param_6,int param_7
               ,int param_8,undefined4 param_9,int *param_10)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int *piVar15;
  int *piVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
  int *piVar20;
  int iVar21;
  int iVar22;
  int *piStack_84;
  int iStack_80;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  int iStack_44;

  gp = &__global_pointer_;
  if (0 < param_7 + -1) {
    iVar22 = param_7 + param_8;
    iVar3 = param_8 * 4 + param_1;
    iVar14 = param_8 + 1;
    iVar21 = 0;
    bVar1 = false;
LAB_ram_4300fd58:
    do {
      if ((*(int *)(iVar3 + 4) == 0) || (*param_6 != 0)) {
        piVar4 = param_10 + iVar21;
        if (bVar1) {
          *piVar4 = iVar14 + -1;
          iVar21 = iVar21 + 1;
          bVar1 = false;
          if (*param_6 == 0) {
            *piVar4 = iVar14;
            iVar14 = iVar14 + 1;
            iVar3 = iVar3 + 4;
            param_6 = param_6 + 1;
            bVar2 = false;
            if (iVar22 == iVar14) break;
            goto LAB_ram_4300fd58;
          }
        }
      }
      else if (!bVar1) {
        param_10[iVar21] = iVar14 + -1;
        iVar21 = iVar21 + 1;
        bVar1 = true;
      }
      iVar14 = iVar14 + 1;
      iVar3 = iVar3 + 4;
      param_6 = param_6 + 1;
      bVar2 = bVar1;
    } while (iVar22 != iVar14);
    if (bVar2) {
      param_10[iVar21] = iVar22;
      iVar21 = iVar21 + 1;
    }
    if (0 < iVar21 >> 1) {
      piStack_84 = param_10;
      iStack_80 = 0;
      do {
        iVar14 = *piStack_84;
        iVar22 = piStack_84[1];
        iVar3 = iVar14 - param_8;
        if (iVar14 < iVar22) {
          iVar18 = iVar3 * 4;
          iVar6 = -100;
          piVar17 = (int *)(param_5 + iVar18);
          iVar19 = -100;
          piVar16 = (int *)(param_3 + iVar18);
          iVar5 = iVar22 - param_8;
          piVar4 = piVar17;
          piVar7 = piVar16;
          iVar11 = iVar3;
          do {
            iVar8 = *piVar4;
            iVar11 = iVar11 + 1;
            piVar4 = piVar4 + 1;
            if (iVar19 < iVar8) {
              iVar19 = iVar8;
            }
            iVar12 = *piVar7;
            piVar7 = piVar7 + 1;
            iVar8 = iVar12 * 2 + iVar8;
            if (iVar6 < iVar8) {
              iVar6 = iVar8;
            }
          } while (iVar11 < iVar5);
          iVar11 = 0;
          if (iVar14 < iVar22) {
            iVar11 = (iVar5 + -1) - iVar3;
          }
          iVar11 = iVar11 + 1;
          iVar8 = pv_normalize(iVar11);
          iVar6 = (0x3b - iVar8) + iVar6;
          piVar15 = (int *)(param_4 + iVar18);
          iVar12 = 0;
          iVar9 = 0;
          piVar4 = piVar17;
          piVar7 = piVar16;
          piVar20 = (int *)(param_2 + iVar18);
          iVar8 = iVar3;
          do {
            iVar8 = iVar8 + 1;
            iVar9 = iVar9 + (*piVar15 >> (iVar19 - *piVar4 & 0x1fU));
            if (iVar6 - (*piVar7 * 2 + *piVar4) < 0x3c) {
              iVar13 = *piVar20;
              *piVar20 = ((uint)(iVar13 * iVar13) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar13 * (longlong)iVar13) >> 0x20) * 0x10;
              iVar13 = *piVar7 * 2 + 0x1c;
              *piVar7 = iVar13;
              iVar12 = iVar12 + ((int)(((uint)(*piVar20 * *piVar15) >> 0x1c) +
                                      (int)((ulonglong)((longlong)*piVar20 * (longlong)*piVar15) >>
                                           0x20) * 0x10) >> (iVar6 - (iVar13 + *piVar4) & 0x1fU));
            }
            piVar15 = piVar15 + 1;
            piVar4 = piVar4 + 1;
            piVar7 = piVar7 + 1;
            piVar20 = piVar20 + 1;
          } while (iVar8 < iVar5);
          pv_div(iVar12,iVar9,&iStack_50);
          iVar8 = (-iStack_4c - iVar19) + -2 + iVar6;
          piVar20 = (int *)(iVar14 * 4 + param_1);
          piVar4 = piVar16;
          piVar7 = (int *)(param_2 + iVar18);
          iVar19 = iVar3;
          do {
            iVar9 = *piVar20;
            if ((iVar19 < param_7 + -1) && (iVar9 < piVar20[1])) {
              iVar9 = piVar20[1];
            }
            iVar10 = *piVar4;
            iVar19 = iVar19 + 1;
            iVar13 = iVar10;
            if (iVar10 < iVar8) {
              iVar13 = iVar8;
            }
            iVar13 = iVar13 + 1;
            piVar20 = piVar20 + 1;
            *piVar7 = ((int)(((uint)((0x40000000 - iVar9) * *piVar7) >> 0x1e) +
                            (int)((ulonglong)((longlong)(0x40000000 - iVar9) * (longlong)*piVar7) >>
                                 0x20) * 4) >> (iVar13 - iVar10 & 0x1fU)) +
                      ((int)(((uint)(iVar9 * iStack_50) >> 0x1e) +
                            (int)((ulonglong)((longlong)iVar9 * (longlong)iStack_50) >> 0x20) * 4)
                      >> (iVar13 - iVar8 & 0x1fU));
            *piVar4 = iVar13;
            piVar4 = piVar4 + 1;
            piVar7 = piVar7 + 1;
          } while (iVar19 < iVar5);
          iVar19 = -100;
          iVar8 = iVar3;
          do {
            iVar9 = *piVar16;
            iVar8 = iVar8 + 1;
            piVar16 = piVar16 + 1;
            if (iVar19 < iVar9 + *piVar17) {
              iVar19 = iVar9 + *piVar17;
            }
            piVar17 = piVar17 + 1;
          } while (iVar8 < iVar5);
          for (; iVar11 != 0; iVar11 = iVar11 >> 1) {
            iVar19 = iVar19 + 1;
          }
          iVar8 = 0;
          piVar17 = (int *)(param_4 + iVar18);
          piVar4 = (int *)(param_2 + iVar18);
          piVar7 = (int *)(param_5 + iVar18);
          piVar16 = (int *)(param_3 + iVar18);
          iVar11 = iVar3;
          do {
            iVar10 = *piVar17;
            iVar13 = *piVar4;
            iVar9 = *piVar16;
            iVar11 = iVar11 + 1;
            piVar4 = piVar4 + 1;
            piVar17 = piVar17 + 1;
            piVar16 = piVar16 + 1;
            iVar8 = iVar8 + ((int)(((uint)(iVar13 * iVar10) >> 0x1c) +
                                  (int)((ulonglong)((longlong)iVar13 * (longlong)iVar10) >> 0x20) *
                                  0x10) >> ((iVar19 - iVar9) - *piVar7 & 0x1fU));
            piVar7 = piVar7 + 1;
          } while (iVar11 < iVar5);
          if (iVar8 == 0) goto LAB_ram_4301000c;
          pv_div(iVar12,iVar8,&iStack_50);
          iVar14 = iStack_50;
          iVar22 = (iVar6 - iVar19) - iStack_4c;
          piVar4 = (int *)(param_3 + iVar18);
          piVar7 = (int *)(param_2 + iVar18);
          do {
            iVar3 = iVar3 + 1;
            pv_sqrt(((uint)(iVar14 * *piVar7) >> 0x1e) +
                    (int)((ulonglong)((longlong)iVar14 * (longlong)*piVar7) >> 0x20) * 4,
                    *piVar4 + iVar22 + 0x1e,&iStack_48,param_9);
            *piVar7 = iStack_48;
            *piVar4 = iStack_44;
            piVar4 = piVar4 + 1;
            piVar7 = piVar7 + 1;
          } while (iVar3 < iVar5);
        }
        else {
          pv_normalize(0);
          pv_div(0,0,&iStack_50);
LAB_ram_4301000c:
          memset(param_2 + iVar3 * 4,0,(iVar22 - iVar14) * 4);
          memset(param_3 + iVar3 * 4,0,(iVar22 - iVar14) * 4);
        }
        iStack_80 = iStack_80 + 1;
        piStack_84 = piStack_84 + 2;
      } while (iVar21 >> 1 != iStack_80);
    }
  }
  return;
}
