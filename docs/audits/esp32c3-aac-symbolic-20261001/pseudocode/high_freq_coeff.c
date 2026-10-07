/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: high_freq_coeff @ ram:4301216a
 * Types and parameter counts are inferred; verify against disassembly. */

void high_freq_coeff(undefined4 param_1,undefined4 param_2,int *param_3,int *param_4,int *param_5)

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
  int iStack_5c;
  int iStack_58;
  int iStack_54;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  int iStack_40;
  int iStack_3c;
  int iStack_38;
  int iStack_34;

  gp = &__global_pointer_;
  iVar21 = 1;
  if (1 < *param_5) {
    do {
      calc_auto_corr(&iStack_54,param_1,param_2,iVar21,0x26);
      iVar20 = iVar21 * 4;
      if (iStack_34 < 1) {
        iVar8 = param_4[1];
        iVar9 = 0;
        *(undefined4 *)(param_3[1] + iVar20) = 0;
        *(undefined4 *)(iVar8 + iVar20) = 0;
        iVar8 = 0;
        bVar1 = false;
        if (iStack_54 != 0) goto LAB_ram_43012308;
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
        uVar15 = iStack_38 * iStack_50;
        lVar2 = (longlong)iStack_38;
        lVar5 = (longlong)iStack_50;
        uVar18 = iStack_54 * iStack_3c;
        lVar3 = (longlong)iStack_54;
        lVar6 = (longlong)iStack_3c;
        uVar16 = iStack_40 * iStack_48;
        lVar4 = (longlong)iStack_40;
        lVar7 = (longlong)iStack_48;
        pv_div(((((uint)(iStack_50 * iStack_48) >> 0x1d) +
                (int)((ulonglong)((longlong)iStack_50 * (longlong)iStack_48) >> 0x20) * 8) -
               (((uint)(iStack_40 * iStack_38) >> 0x1d) +
               (int)((ulonglong)((longlong)iStack_40 * (longlong)iStack_38) >> 0x20) * 8)) -
               (((uint)(iStack_54 * iStack_4c) >> 0x1d) +
               (int)((ulonglong)((longlong)iStack_54 * (longlong)iStack_4c) >> 0x20) * 8),iStack_34,
               &iStack_5c);
        iVar8 = iStack_5c >> (iStack_58 + 2U & 0x1f);
        pv_div((((uVar15 >> 0x1d) + (int)((ulonglong)(lVar2 * lVar5) >> 0x20) * 8) -
               ((uVar18 >> 0x1d) + (int)((ulonglong)(lVar3 * lVar6) >> 0x20) * 8)) +
               (uVar16 >> 0x1d) + (int)((ulonglong)(lVar4 * lVar7) >> 0x20) * 8,iStack_34,&iStack_5c
              );
        iVar13 = param_4[1];
        *(int *)(param_3[1] + iVar20) = iVar8;
        iVar9 = iStack_5c >> (iStack_58 + 2U & 0x1f);
        *(int *)(iVar13 + iVar20) = iVar9;
        bVar1 = iStack_58 < -2;
        if (iStack_54 == 0) goto LAB_ram_430121bc;
LAB_ram_43012308:
        uVar15 = iStack_38 * iVar8;
        iVar13 = iStack_40 +
                 ((uint)(iVar9 * iStack_48) >> 0x1c) +
                 (int)((ulonglong)((longlong)iVar9 * (longlong)iStack_48) >> 0x20) * 0x10;
        lVar2 = (longlong)iStack_38;
        pv_div(-(iStack_50 +
                 ((uint)(iVar8 * iStack_48) >> 0x1c) +
                 (int)((ulonglong)((longlong)iVar8 * (longlong)iStack_48) >> 0x20) * 0x10 +
                ((uint)(iVar9 * iStack_38) >> 0x1c) +
                (int)((ulonglong)((longlong)iVar9 * (longlong)iStack_38) >> 0x20) * 0x10),iStack_54,
               &iStack_5c);
        iVar22 = iStack_5c >> (iStack_58 + 2U & 0x1f);
        pv_div(((uVar15 >> 0x1c) + (int)((ulonglong)(lVar2 * iVar8) >> 0x20) * 0x10) - iVar13,
               iStack_54,&iStack_5c);
        iVar10 = *param_3;
        iVar11 = *param_4;
        iVar13 = iStack_5c >> (iStack_58 + 2U & 0x1f);
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
          bVar1 = iStack_58 < -2;
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
