/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: calc_sbr_envelope @ ram:42043336
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_envelope(int param_1,undefined4 param_2,undefined4 param_3,int *param_4,int *param_5,
                      int param_6,int param_7,int param_8,undefined4 param_9,undefined4 param_10,
                      undefined4 *param_11,int param_12,int *param_13,int param_14,int param_15,
                      undefined4 *param_16,undefined4 *param_17,undefined4 *param_18,
                      undefined4 *param_19,int param_20,undefined4 *param_21,int param_22,
                      int param_23)

{
  bool bVar1;
  int iVar2;
  bool bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  undefined4 *puVar14;
  int *piVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  uint uVar20;
  uint uVar21;
  int *piVar22;
  int iVar23;
  int iVar24;
  void *bb;
  int iVar25;
  int iVar26;
  int iVar27;
  void *bb_00;
  void *bb_01;
  void *bb_02;
  void *bb_03;
  int iVar28;
  int *piVar29;
  int iVar30;
  uint uVar31;
  int iVar32;
  undefined4 *puVar33;
  int iVar34;
  undefined4 *puVar35;
  undefined4 uVar36;
  uint *puVar37;
  int iVar38;
  size_t n;
  uint *puVar39;
  int *piVar40;
  int iVar41;
  int *piVar42;
  uint *puVar43;
  int iStack_260;
  int iStack_25c;
  uint uStack_224;
  uint uStack_220;
  int iStack_21c;
  uint uStack_210;
  int iStack_1f4;
  int iStack_1d8;
  int *piStack_1d0;
  int iStack_1c4;
  int iStack_1b4;
  int iStack_1b0;
  undefined4 uStack_170;
  undefined4 uStack_16c;
  undefined4 uStack_168;
  undefined4 uStack_164;
  undefined4 uStack_160;
  undefined4 uStack_15c;
  undefined4 uStack_158;
  int iStack_150;
  uint uStack_14c;
  uint uStack_148;
  uint uStack_144;
  undefined4 auStack_140 [67];

  iVar2 = smoothLengths;
  gp = &__global_pointer_;
  iVar10 = *(int *)(param_1 + 0x10);
  iVar7 = param_1 + 0x10;
  iVar24 = *(int *)(iVar10 * 8 + iVar7 + 8);
  bb = (void *)(param_20 + 0xa00);
  iVar25 = *(int *)(param_1 + 0xf8);
  iVar26 = *(int *)(param_1 + 0xf4);
  iVar32 = param_4[*param_5];
  iVar34 = *(int *)(param_1 + 0xfc);
  iVar8 = *(int *)(param_1 + 0xf0);
  iVar27 = *param_4;
  if (param_8 != 0) {
    uStack_170 = *param_21;
    *param_13 = 1;
    uStack_16c = param_21[1];
    uStack_168 = param_21[2];
    *param_11 = 0;
    uStack_164 = param_21[3];
    uStack_160 = param_21[4];
    uStack_15c = param_21[5];
    uStack_158 = param_21[6];
    sbr_create_limiter_bands(param_14,param_15,param_4,&uStack_170,*param_5);
  }
  memset(bb,0,0x100);
  iVar19 = param_5[1];
  if (iVar19 != 0) {
    puVar14 = (undefined4 *)(param_1 + 0x17c);
    iVar4 = param_4[0x3b];
    piVar15 = param_4 + 0x3c;
    do {
      iVar11 = *piVar15;
      iVar19 = iVar19 + -1;
      *(undefined4 *)(((iVar4 + iVar11 >> 1) - iVar27) * 4 + (int)bb) = *puVar14;
      puVar14 = puVar14 + 1;
      iVar4 = iVar11;
      piVar15 = piVar15 + 1;
    } while (iVar19 != 0);
  }
  if (iVar10 < 1) {
LAB_ram_42043c60:
    iStack_1d8 = iVar27 * 4;
    memcpy((void *)(param_12 + iStack_1d8),bb,(0x40 - iVar27) * 4);
    *(uint *)(param_1 + 0xb8) = -(uint)(iVar10 != iVar24);
    return;
  }
  uVar20 = iVar32 - iVar27 >> 0x1f ^ iVar32 - iVar27;
  iVar32 = param_20 + 0x900;
  iVar19 = param_20 + 0x100;
  bb_00 = (void *)(param_20 + 0x400);
  bb_01 = (void *)(param_20 + 0x500);
  bb_02 = (void *)(param_20 + 0x600);
  bb_03 = (void *)(param_20 + 0x700);
  if (0x40 < (int)uVar20) {
    uVar20 = 0x40;
  }
  piVar15 = (int *)(param_15 + iVar8 * 4);
  iStack_1f4 = iVar10 * 4 + param_1;
  piStack_1d0 = (int *)(param_1 + 0x14);
  n = uVar20 << 2;
  iStack_21c = 0;
  uStack_224 = 0;
  uStack_220 = 0;
  iStack_1b0 = -1;
  iStack_1b4 = 0;
  iStack_1c4 = 0;
LAB_ram_42043524:
  if (*piStack_1d0 == *(int *)((iVar10 * 2 + 4 + iStack_1b4) * 4 + iVar7)) {
    iStack_1b4 = iStack_1b4 + 1;
    iStack_1b0 = iStack_1b0 + 1;
  }
  if ((iVar24 == iStack_21c) || (*(int *)(param_1 + 0xb8) == iStack_21c)) {
    iVar4 = 1;
    iVar11 = *(int *)(iStack_1f4 + 0x18);
    uVar36 = 0;
    iVar28 = param_5[iVar11];
  }
  else {
    iVar4 = 0;
    uVar36 = (&smoothLengths)[iVar34];
    iVar11 = *(int *)(iStack_1f4 + 0x18);
    iVar28 = param_5[iVar11];
  }
  if (0 < iVar28) {
    puVar43 = (uint *)(iStack_1c4 * 4 + param_1 + 0x710);
    iStack_260 = 0x3fffffff;
    iStack_25c = 0;
    iVar28 = 0;
    iVar38 = 1;
    uStack_210 = 0;
    iVar16 = 0;
    iVar5 = param_4[iVar11 * 0x3b];
    iVar41 = iVar5;
    do {
      iVar16 = iVar16 + 1;
      piVar29 = (int *)(iVar38 * 4 + param_6);
      iVar17 = param_4[iVar11 * 0x3b + iVar16];
      uVar31 = iVar17 - iVar41;
      if (iVar41 < iVar17) {
        piVar40 = (int *)(param_12 + (iVar28 + iVar27) * 4);
        piVar42 = (int *)(iVar28 * 4 + (int)bb);
        iVar6 = (iVar28 - iVar41) + iVar17;
        iVar11 = iVar28;
        bVar3 = false;
        do {
          while( true ) {
            bVar1 = bVar3;
            iVar30 = iVar11;
            iVar11 = ((iVar41 - iVar5) - iVar28) + iVar30;
            if (param_23 == 1) {
              energy_estimation_LC
                        (param_2,param_20,iVar19,iVar7,iStack_21c,iVar11,iVar30,*piStack_1d0 << 1);
            }
            else {
              energy_estimation(param_2,param_3,param_20,iVar19,iVar7,iStack_21c,iVar11,iVar30,
                                *piStack_1d0 << 1);
            }
            if (*piVar42 != 0) break;
LAB_ram_4204365a:
            piVar40 = piVar40 + 1;
            piVar42 = piVar42 + 1;
            iVar11 = iVar30 + 1;
            bVar3 = bVar1;
            if (iVar6 == iVar30 + 1) goto LAB_ram_420436a2;
          }
          if (iStack_21c < iVar24) {
            bVar1 = (bool)(bVar1 | *piVar40 != 0);
            goto LAB_ram_4204365a;
          }
          bVar1 = true;
          piVar40 = piVar40 + 1;
          piVar42 = piVar42 + 1;
          iVar11 = iVar30 + 1;
          bVar3 = true;
        } while (iVar6 != iVar30 + 1);
LAB_ram_420436a2:
        iVar28 = iVar30 + 1;
        iVar11 = *piVar29;
        iVar6 = iVar6 - uVar31;
        if (iVar25 == 0) {
LAB_ram_420438a6:
          iVar6 = iVar28 - uVar31;
          if (iVar6 < iVar28) {
            piVar40 = (int *)(iVar6 * 4 + param_20);
            piVar42 = (int *)(iVar28 * 4 + param_20);
            uStack_224 = 0xffffff9c;
            piVar29 = piVar40;
            do {
              puVar39 = (uint *)(piVar29 + 0x40);
              piVar29 = piVar29 + 1;
              if ((int)uStack_224 < (int)*puVar39) {
                uStack_224 = *puVar39;
              }
            } while (piVar42 != piVar29);
            uStack_220 = 0;
            do {
              piVar29 = piVar40 + 0x40;
              iVar28 = *piVar40;
              piVar40 = piVar40 + 1;
              uStack_220 = uStack_220 + (iVar28 >> (uStack_224 - *piVar29 & 0x1f));
            } while (piVar42 != piVar40);
            uStack_220 = uStack_220 / uVar31;
          }
          else {
            uStack_220 = 0;
            uStack_224 = 0xffffff9c;
          }
        }
        iVar28 = iVar6;
        if (0 < (int)uVar31) {
          piVar29 = (int *)((iVar27 + iVar28) * 4 + param_12);
          puVar14 = auStack_140 + (iVar41 - iVar27);
          puVar39 = (uint *)(param_20 + 0x800 + iVar28 * 4);
          iVar30 = param_22 + 0x40;
          iVar6 = iVar38;
          do {
            iVar38 = iVar6;
            if (iVar11 <= iVar41) {
              iVar38 = iVar6 + 1;
              iStack_25c = iVar6;
            }
            iVar11 = *(int *)(iVar38 * 4 + param_6);
            if (iVar25 == 0) {
              puVar39[-0x200] = uStack_220;
              puVar39[-0x1c0] = uStack_224;
            }
            if (param_23 == 1) {
              puVar39[-0x1c0] = puVar39[-0x1c0] + 1;
              if (bVar1) {
                *puVar14 = 1;
              }
              else {
                *puVar14 = 0;
              }
            }
            puVar39[-0x180] = *puVar43;
            iVar6 = (iStack_1b0 * param_7 + iStack_25c) * 4;
            puVar39[-0x140] = puVar43[0x122];
            puVar37 = (uint *)(param_1 + 0x1130 + iVar6);
            uVar12 = *puVar37;
            piVar40 = (int *)(iVar6 + param_1 + 0x1108);
            iVar6 = *piVar40;
            if ((int)uVar12 < 0) {
              iVar6 = iVar6 >> (-uVar12 & 0x1f);
              pv_div(iVar6,iVar6 + 0x3fffffff,&iStack_150);
            }
            else {
              pv_div(iVar6,(0x3fffffff >> (uVar12 & 0x1f)) + iVar6,&iStack_150);
            }
            uVar12 = puVar39[-0x180];
            iVar6 = iStack_150 >> (uStack_14c & 0x1f);
            iVar13 = puVar39[-0x200] + 1;
            iVar6 = (int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar12) >> 0x20) * 4 +
                    (iVar6 * uVar12 >> 0x1e);
            if (bVar1) {
              pv_div(iVar6,iVar13,&iStack_150);
              pv_sqrt(iStack_150,((puVar39[-0x140] - puVar39[-0x1c0]) - uStack_14c) + -0x1e,
                      &uStack_148,param_22 + 0x10);
              puVar39[-0x100] = uStack_148;
              puVar39[-0xc0] = uStack_144;
              if ((puVar39[0x80] == 0) || ((iStack_21c < iVar24 && (*piVar29 == 0)))) {
                uVar12 = 0;
                *puVar39 = 0;
              }
              else {
                uVar12 = *puVar37;
                if ((int)uVar12 < 0) {
                  pv_div(puVar39[-0x180],(*piVar40 >> (-uVar12 & 0x1f)) + 0x3fffffff,&iStack_150);
                  uVar12 = 0;
                }
                else {
                  pv_div(puVar39[-0x180],(0x3fffffff >> (uVar12 & 0x1f)) + *piVar40,&iStack_150);
                }
                pv_sqrt(iStack_150,(puVar39[-0x140] - uVar12) - uStack_14c,&uStack_148,
                        param_22 + 0x20);
                *puVar39 = uStack_148;
                uVar12 = uStack_144;
              }
            }
            else {
              if (iVar4 == 0) {
                iVar23 = iStack_260;
                iVar18 = iVar30;
                if (puVar39[-0x200] != 0) {
                  uVar21 = *puVar37;
                  if ((int)uVar21 < 0) {
                    if (-10 < (int)uVar21) {
                      iVar23 = (*piVar40 >> (-uVar21 & 0x1f)) + 0x3fffffff;
                      iVar13 = (int)((ulonglong)((longlong)iVar23 * (longlong)iVar13) >> 0x20) * 4 +
                               ((uint)(iVar23 * iVar13) >> 0x1e);
                    }
                    pv_div(uVar12,iVar13,&iStack_150);
                    iVar13 = (puVar39[-0x140] - uStack_14c) + -0x1e;
                    if (puVar39[-0x200] != 0) {
                      iVar13 = iVar13 - puVar39[-0x1c0];
                    }
                    goto LAB_ram_4204380a;
                  }
                  iVar23 = 0x3fffffff >> (uVar21 & 0x1f);
                }
                pv_div(uVar12,((uint)((iVar23 + *piVar40) * iVar13) >> 0x1e) +
                              (int)((ulonglong)((longlong)(iVar23 + *piVar40) * (longlong)iVar13) >>
                                   0x20) * 4,&iStack_150);
                iVar13 = (((puVar39[-0x140] - puVar39[-0x1c0]) - uStack_14c) + -0x1e) - *puVar37;
              }
              else {
                pv_div(uVar12,iVar13,&iStack_150);
                iVar13 = ((puVar39[-0x140] - puVar39[-0x1c0]) - uStack_14c) + -0x1e;
                iVar18 = param_22 + 0x30;
              }
LAB_ram_4204380a:
              pv_sqrt(iStack_150,iVar13,&uStack_148,iVar18);
              *puVar39 = 0;
              puVar39[-0xc0] = uStack_144;
              puVar39[-0x100] = uStack_148;
              uVar12 = 0xffffff9c;
            }
            puVar39[0x40] = uVar12;
            uStack_210 = uStack_210 | *puVar39;
            pv_sqrt(iVar6,puVar39[-0x140],&uStack_148,param_22 + 0x50);
            puVar39[-0x80] = uStack_148;
            puVar39[-0x40] = uStack_144;
            iVar41 = iVar41 + 1;
            piVar29 = piVar29 + 1;
            puVar14 = puVar14 + 1;
            puVar39 = puVar39 + 1;
            iVar6 = iVar38;
          } while (iVar17 != iVar41);
          iVar11 = *(int *)(iStack_1f4 + 0x18);
          iVar28 = uVar31 + iVar28;
          goto LAB_ram_4204387a;
        }
        iVar11 = *(int *)(iStack_1f4 + 0x18);
        iVar41 = param_5[iVar11];
      }
      else {
        if (iVar25 == 0) {
          iVar11 = *piVar29;
          bVar1 = false;
          goto LAB_ram_420438a6;
        }
        iVar28 = iVar28 - uVar31;
LAB_ram_4204387a:
        iVar41 = param_5[iVar11];
      }
      if (iVar41 <= iVar16) goto LAB_ram_42043906;
      puVar43 = puVar43 + 1;
      iVar41 = param_4[iVar11 * 0x3b + iVar16];
    } while( true );
  }
  uStack_210 = 0;
  goto LAB_ram_42043914;
LAB_ram_42043906:
  iStack_1c4 = iStack_1c4 + iVar16;
LAB_ram_42043914:
  iVar11 = *piVar15;
  if (0 < iVar11) {
    iVar28 = 0;
    piVar29 = (int *)(iVar8 * 0x34 + param_14);
    do {
      piVar40 = piVar29 + 1;
      iVar38 = *piVar29;
      iVar41 = *piVar40;
      iVar28 = iVar28 + 1;
      if (iVar38 < iVar41) {
        iVar16 = iVar38 * 4;
        iVar5 = -100;
        iVar17 = param_20 + iVar16;
        iVar11 = -100;
        do {
          if (iVar11 < *(int *)(iVar17 + 0x300)) {
            iVar11 = *(int *)(iVar17 + 0x300);
          }
          piVar42 = (int *)(iVar17 + 0x100);
          iVar17 = iVar17 + 4;
          if (iVar5 < *piVar42) {
            iVar5 = *piVar42;
          }
        } while (param_20 + iVar41 * 4 != iVar17);
        iVar17 = iVar41 - iVar38;
        if (iVar41 != iVar38) {
          do {
            iVar17 = iVar17 >> 1;
            iVar11 = iVar11 + 1;
          } while (iVar17 != 0);
        }
        piVar42 = (int *)(param_20 + iVar16);
        iVar17 = 0;
        iVar6 = 0;
        do {
          piVar22 = piVar42 + 0x40;
          iVar6 = iVar6 + (piVar42[0x80] >> (iVar11 - piVar42[0xc0] & 0x1fU));
          iVar30 = *piVar42;
          piVar42 = piVar42 + 1;
          iVar17 = iVar17 + (iVar30 >> (iVar5 - *piVar22 & 0x1fU));
        } while ((int *)(iVar41 * 4 + param_20) != piVar42);
        uVar31 = 0x10;
        iVar30 = 0x186a0000;
        if (iVar17 == 0) {
LAB_ram_420439c2:
          iVar5 = param_20 + iVar16;
          do {
            while( true ) {
              uVar21 = *(uint *)(iVar5 + 0x500);
              uVar12 = uVar21;
              if ((int)uVar21 < (int)uVar31) {
                uVar12 = uVar31;
              }
              if (*(int *)(iVar5 + 0x400) >> (uVar12 - uVar21 & 0x1f) <
                  iVar30 >> (uVar12 - uVar31 & 0x1f)) break;
              iVar38 = iVar38 + 1;
              pv_div(((uint)(iVar30 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                     (int)((ulonglong)((longlong)iVar30 * (longlong)*(int *)(iVar5 + 0x600)) >> 0x20
                          ) * 0x10,*(int *)(iVar5 + 0x400),&iStack_150);
              *(int *)(iVar5 + 0x400) = iVar30;
              *(int *)(iVar5 + 0x600) = iStack_150 >> 2;
              *(uint *)(iVar5 + 0x700) =
                   ((*(int *)(iVar5 + 0x700) + uVar31) - uStack_14c) - *(int *)(iVar5 + 0x500);
              *(uint *)(iVar5 + 0x500) = uVar31;
              iVar41 = *piVar40;
              iVar5 = iVar5 + 4;
              if (iVar41 <= iVar38) goto LAB_ram_42043a44;
            }
            iVar38 = iVar38 + 1;
            iVar5 = iVar5 + 4;
          } while (iVar38 < iVar41);
LAB_ram_42043a44:
          iVar38 = *piVar29;
          if (iVar38 < iVar41) {
            iVar16 = iVar38 * 4;
            piVar22 = (int *)(iVar32 + iVar16);
            piVar42 = (int *)(iVar32 + iVar41 * 4);
            iVar5 = -100;
            do {
              while( true ) {
                iVar17 = piVar22[-0x100] * 2 + piVar22[-0x200] + 0x1c;
                if (iVar5 < iVar17) {
                  iVar5 = iVar17;
                }
                if (piVar22[-0x40] == 0) break;
                iVar17 = *piVar22 << 1;
                if (iVar5 < *piVar22 << 1) goto LAB_ram_42043eae;
LAB_ram_42043a84:
                piVar22 = piVar22 + 1;
                if (piVar42 == piVar22) goto LAB_ram_42043a8a;
              }
              if ((iVar4 != 0) || (iVar17 = piVar22[-0x80] << 1, piVar22[-0x80] << 1 <= iVar5))
              goto LAB_ram_42043a84;
LAB_ram_42043eae:
              iVar5 = iVar17;
              piVar22 = piVar22 + 1;
            } while (piVar42 != piVar22);
LAB_ram_42043a8a:
            iVar5 = iVar5 + 1;
            piVar22 = (int *)(iVar41 * 4 + param_20 + 0x800);
            piVar42 = (int *)(param_20 + 0x800 + iVar16);
            iVar17 = 0;
            do {
              while( true ) {
                iVar30 = piVar42[-0xc0] * 2 + piVar42[-0x1c0];
                if (iVar5 - iVar30 < 0x3b) {
                  iVar13 = piVar42[-0x100];
                  iVar13 = ((uint)(iVar13 * iVar13) >> 0x1c) +
                           (int)((ulonglong)((longlong)iVar13 * (longlong)iVar13) >> 0x20) * 0x10;
                  iVar17 = iVar17 + ((int)(((uint)(piVar42[-0x200] * iVar13) >> 0x1c) +
                                          (int)((ulonglong)
                                                ((longlong)piVar42[-0x200] * (longlong)iVar13) >>
                                               0x20) * 0x10) >> (iVar5 - (iVar30 + 0x1c) & 0x1fU));
                }
                iVar30 = *piVar42;
                if (iVar30 == 0) break;
                uVar31 = iVar5 + piVar42[0x40] * -2;
                if ((int)uVar31 < 0x1f) {
                  iVar17 = iVar17 + ((int)(((uint)(iVar30 * iVar30) >> 0x1c) +
                                          (int)((ulonglong)((longlong)iVar30 * (longlong)iVar30) >>
                                               0x20) * 0x10) >> (uVar31 & 0x1f));
                }
LAB_ram_42043ac0:
                piVar42 = piVar42 + 1;
                if (piVar22 == piVar42) goto LAB_ram_42043b44;
              }
              if ((iVar4 != 0) || (uVar31 = iVar5 + piVar42[-0x40] * -2, 0x1e < (int)uVar31))
              goto LAB_ram_42043ac0;
              iVar30 = piVar42[-0x80];
              piVar42 = piVar42 + 1;
              iVar17 = iVar17 + ((int)(((uint)(iVar30 * iVar30) >> 0x1c) +
                                      (int)((ulonglong)((longlong)iVar30 * (longlong)iVar30) >> 0x20
                                           ) * 0x10) >> (uVar31 & 0x1f));
            } while (piVar22 != piVar42);
LAB_ram_42043b44:
            if (iVar17 == 0) {
              iVar11 = 0x195bb900;
              if (uStack_210 == 0) {
LAB_ram_42043eb8:
                iVar5 = iVar38 * 4 + param_20;
                if (iVar38 < iVar41) {
                  do {
                    iVar38 = iVar38 + 1;
                    *(uint *)(iVar5 + 0x400) =
                         ((uint)(iVar11 * *(int *)(iVar5 + 0x400)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar11 * (longlong)*(int *)(iVar5 + 0x400)) >>
                              0x20) * 0x10;
                    *(uint *)(iVar5 + 0x600) =
                         ((uint)(iVar11 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar11 * (longlong)*(int *)(iVar5 + 0x600)) >>
                              0x20) * 0x10;
                    iVar5 = iVar5 + 4;
                  } while (iVar38 < *piVar40);
                  iVar11 = *piVar15;
                  goto LAB_ram_42043bac;
                }
              }
              else {
LAB_ram_42043b56:
                piVar29 = (int *)(iVar16 + (int)bb_00);
                do {
                  iVar38 = iVar38 + 1;
                  *piVar29 = ((uint)(iVar11 * *piVar29) >> 0x1c) +
                             (int)((ulonglong)((longlong)iVar11 * (longlong)*piVar29) >> 0x20) *
                             0x10;
                  piVar29[0x80] =
                       ((uint)(iVar11 * piVar29[0x80]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar11 * (longlong)piVar29[0x80]) >> 0x20) * 0x10
                  ;
                  piVar29[0x100] =
                       ((uint)(iVar11 * piVar29[0x100]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar11 * (longlong)piVar29[0x100]) >> 0x20) *
                       0x10;
                  piVar29 = piVar29 + 1;
                } while (iVar38 < *piVar40);
              }
            }
            else {
              pv_div(iVar6,iVar17,&iStack_150);
              pv_sqrt(iStack_150,((iVar11 - iVar5) + -0x3a) - uStack_14c,&uStack_148,param_22 + 0x70
                     );
              if ((int)uStack_144 < -0x1b) {
                iVar11 = (int)uStack_148 >> (-uStack_144 - 0x1c & 0x1f);
              }
              else {
                iVar11 = uStack_148 << (uStack_144 + 0x1c & 0x1f);
              }
              uVar31 = uStack_144;
              if ((int)uStack_144 < -0x1c) {
                uVar31 = 0xffffffe4;
              }
              iVar38 = *piVar29;
              iVar41 = *piVar40;
              if (0x195bb900 >> (uVar31 + 0x1c & 0x1f) <
                  (int)uStack_148 >> (uVar31 - uStack_144 & 0x1f)) {
                iVar11 = 0x195bb900;
              }
              if (uStack_210 == 0) goto LAB_ram_42043eb8;
              iVar16 = iVar38 << 2;
              if (iVar38 < iVar41) goto LAB_ram_42043b56;
            }
          }
        }
        else {
          pv_div(iVar6,iVar17,&iStack_150);
          pv_sqrt(iStack_150,((iVar11 + -0x1e) - iVar5) - uStack_14c,&uStack_148,param_22 + 0x60);
          iVar30 = (int)((ulonglong)
                         ((longlong)(int)uStack_148 * (longlong)*(int *)(limGains + iVar26 * 4)) >>
                        0x20) * 4 + (uStack_148 * *(int *)(limGains + iVar26 * 4) >> 0x1e);
          uVar31 = limGains._16_4_;
          if (iVar26 != 3) {
            uVar31 = uStack_144;
          }
          uVar12 = uVar31;
          if ((int)uVar31 < 0x10) {
            uVar12 = 0x10;
          }
          iVar38 = *piVar29;
          iVar41 = *piVar40;
          if (0x186a0000 >> (uVar12 - 0x10 & 0x1f) < iVar30 >> (uVar12 - uVar31 & 0x1f)) {
            iVar30 = 0x186a0000;
            uVar31 = 0x10;
          }
          iVar16 = iVar38 << 2;
          if (iVar38 < iVar41) goto LAB_ram_420439c2;
        }
        iVar11 = *piVar15;
      }
LAB_ram_42043bac:
      piVar29 = piVar40;
    } while (iVar28 < iVar11);
  }
  if (param_23 == 1) {
    sbr_aliasing_reduction
              (param_9,bb_00,bb_01,param_20,iVar19,auStack_140,uVar20,iVar27,param_22,
               param_20 + 0x300);
    if (*param_13 != 0) {
      *param_13 = 0;
    }
    envelope_application_LC
              (param_2,bb_00,bb_01,bb_02,bb_03,param_20 + 0x800,iVar32,uStack_210,iVar7,param_10,
               param_11,iStack_21c,iVar27,uVar20,iVar4);
  }
  else {
    if (*param_13 != 0) {
      puVar14 = param_19;
      puVar9 = param_17;
      puVar33 = param_18;
      puVar35 = param_16;
      if (0 < iVar2) {
        do {
          memcpy((void *)*puVar35,bb_00,n);
          memcpy((void *)*puVar33,bb_02,n);
          memcpy((void *)*puVar9,bb_01,n);
          puVar35 = puVar35 + 1;
          memcpy((void *)*puVar14,bb_03,n);
          puVar14 = puVar14 + 1;
          puVar9 = puVar9 + 1;
          puVar33 = puVar33 + 1;
        } while (param_16 + iVar2 != puVar35);
      }
      *param_13 = 0;
    }
    envelope_application
              (param_2,param_3,bb_00,bb_01,bb_02,bb_03,param_20 + 0x800,iVar32,param_16,param_17,
               param_18,param_19,iVar7,param_10,param_11,iStack_21c,iVar27,uVar20,iVar4,uStack_210,
               iVar2,uVar36);
  }
  iStack_21c = iStack_21c + 1;
  piStack_1d0 = piStack_1d0 + 1;
  iStack_1f4 = iStack_1f4 + 4;
  if (iVar10 == iStack_21c) goto LAB_ram_42043c60;
  goto LAB_ram_42043524;
}
