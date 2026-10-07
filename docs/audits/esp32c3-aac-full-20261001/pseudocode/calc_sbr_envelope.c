/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_envelope @ ram:430030b2
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
  int iVar21;
  uint uVar22;
  int *piVar23;
  int iVar24;
  int iVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  int iVar30;
  int iVar31;
  int iVar32;
  int iVar33;
  int *piVar34;
  int iVar35;
  uint uVar36;
  int iVar37;
  undefined4 *puVar38;
  int iVar39;
  undefined4 *puVar40;
  undefined4 uVar41;
  uint *puVar42;
  int iVar43;
  int iVar44;
  uint *puVar45;
  int *piVar46;
  int iVar47;
  int *piVar48;
  uint *puVar49;
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
  iVar25 = *(int *)(iVar10 * 8 + iVar7 + 8);
  iVar26 = param_20 + 0xa00;
  iVar27 = *(int *)(param_1 + 0xf8);
  iVar28 = *(int *)(param_1 + 0xf4);
  iVar37 = param_4[*param_5];
  iVar39 = *(int *)(param_1 + 0xfc);
  iVar8 = *(int *)(param_1 + 0xf0);
  iVar29 = *param_4;
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
  memset(iVar26,0,0x100);
  iVar19 = param_5[1];
  if (iVar19 != 0) {
    puVar14 = (undefined4 *)(param_1 + 0x17c);
    iVar30 = param_4[0x3b];
    piVar15 = param_4 + 0x3c;
    do {
      iVar11 = *piVar15;
      iVar19 = iVar19 + -1;
      *(undefined4 *)(((iVar30 + iVar11 >> 1) - iVar29) * 4 + iVar26) = *puVar14;
      puVar14 = puVar14 + 1;
      iVar30 = iVar11;
      piVar15 = piVar15 + 1;
    } while (iVar19 != 0);
  }
  if (iVar10 < 1) {
LAB_ram_430039fc:
    iStack_1d8 = iVar29 * 4;
    memcpy(param_12 + iStack_1d8,iVar26,(0x40 - iVar29) * 4);
    *(uint *)(param_1 + 0xb8) = -(uint)(iVar10 != iVar25);
    return;
  }
  uVar20 = iVar37 - iVar29 >> 0x1f ^ iVar37 - iVar29;
  iVar37 = param_20 + 0x900;
  iVar19 = param_20 + 0x100;
  iVar30 = param_20 + 0x400;
  iVar11 = param_20 + 0x500;
  iVar31 = param_20 + 0x600;
  iVar32 = param_20 + 0x700;
  if (0x40 < (int)uVar20) {
    uVar20 = 0x40;
  }
  piVar15 = (int *)(param_15 + iVar8 * 4);
  iStack_1f4 = iVar10 * 4 + param_1;
  piStack_1d0 = (int *)(param_1 + 0x14);
  iVar44 = uVar20 << 2;
  iStack_21c = 0;
  uStack_224 = 0;
  uStack_220 = 0;
  iStack_1b0 = -1;
  iStack_1b4 = 0;
  iStack_1c4 = 0;
LAB_ram_430032a0:
  if (*piStack_1d0 == *(int *)((iVar10 * 2 + 4 + iStack_1b4) * 4 + iVar7)) {
    iStack_1b4 = iStack_1b4 + 1;
    iStack_1b0 = iStack_1b0 + 1;
  }
  if ((iVar25 == iStack_21c) || (*(int *)(param_1 + 0xb8) == iStack_21c)) {
    iVar4 = 1;
    iVar21 = *(int *)(iStack_1f4 + 0x18);
    uVar41 = 0;
    iVar33 = param_5[iVar21];
  }
  else {
    iVar4 = 0;
    uVar41 = (&smoothLengths)[iVar39];
    iVar21 = *(int *)(iStack_1f4 + 0x18);
    iVar33 = param_5[iVar21];
  }
  if (0 < iVar33) {
    puVar49 = (uint *)(iStack_1c4 * 4 + param_1 + 0x710);
    iStack_260 = 0x3fffffff;
    iStack_25c = 0;
    iVar33 = 0;
    iVar43 = 1;
    uStack_210 = 0;
    iVar16 = 0;
    iVar5 = param_4[iVar21 * 0x3b];
    iVar47 = iVar5;
    do {
      iVar16 = iVar16 + 1;
      piVar34 = (int *)(iVar43 * 4 + param_6);
      iVar17 = param_4[iVar21 * 0x3b + iVar16];
      uVar36 = iVar17 - iVar47;
      if (iVar47 < iVar17) {
        piVar46 = (int *)(param_12 + (iVar33 + iVar29) * 4);
        piVar48 = (int *)(iVar33 * 4 + iVar26);
        iVar6 = (iVar33 - iVar47) + iVar17;
        iVar21 = iVar33;
        bVar3 = false;
        do {
          while( true ) {
            bVar1 = bVar3;
            iVar35 = iVar21;
            iVar21 = ((iVar47 - iVar5) - iVar33) + iVar35;
            if (param_23 == 1) {
              energy_estimation_LC
                        (param_2,param_20,iVar19,iVar7,iStack_21c,iVar21,iVar35,*piStack_1d0 << 1);
            }
            else {
              energy_estimation(param_2,param_3,param_20,iVar19,iVar7,iStack_21c,iVar21,iVar35,
                                *piStack_1d0 << 1);
            }
            if (*piVar48 != 0) break;
LAB_ram_430033da:
            piVar46 = piVar46 + 1;
            piVar48 = piVar48 + 1;
            iVar21 = iVar35 + 1;
            bVar3 = bVar1;
            if (iVar6 == iVar35 + 1) goto LAB_ram_43003426;
          }
          if (iStack_21c < iVar25) {
            bVar1 = (bool)(bVar1 | *piVar46 != 0);
            goto LAB_ram_430033da;
          }
          bVar1 = true;
          piVar46 = piVar46 + 1;
          piVar48 = piVar48 + 1;
          iVar21 = iVar35 + 1;
          bVar3 = true;
        } while (iVar6 != iVar35 + 1);
LAB_ram_43003426:
        iVar33 = iVar35 + 1;
        iVar21 = *piVar34;
        iVar6 = iVar6 - uVar36;
        if (iVar27 == 0) {
LAB_ram_4300363a:
          iVar6 = iVar33 - uVar36;
          if (iVar6 < iVar33) {
            piVar46 = (int *)(iVar6 * 4 + param_20);
            piVar48 = (int *)(iVar33 * 4 + param_20);
            uStack_224 = 0xffffff9c;
            piVar34 = piVar46;
            do {
              puVar45 = (uint *)(piVar34 + 0x40);
              piVar34 = piVar34 + 1;
              if ((int)uStack_224 < (int)*puVar45) {
                uStack_224 = *puVar45;
              }
            } while (piVar48 != piVar34);
            uStack_220 = 0;
            do {
              piVar34 = piVar46 + 0x40;
              iVar33 = *piVar46;
              piVar46 = piVar46 + 1;
              uStack_220 = uStack_220 + (iVar33 >> (uStack_224 - *piVar34 & 0x1f));
            } while (piVar48 != piVar46);
            uStack_220 = uStack_220 / uVar36;
          }
          else {
            uStack_220 = 0;
            uStack_224 = 0xffffff9c;
          }
        }
        iVar33 = iVar6;
        if (0 < (int)uVar36) {
          piVar34 = (int *)((iVar29 + iVar33) * 4 + param_12);
          puVar14 = auStack_140 + (iVar47 - iVar29);
          puVar45 = (uint *)(param_20 + 0x800 + iVar33 * 4);
          iVar35 = param_22 + 0x40;
          iVar6 = iVar43;
          do {
            iVar43 = iVar6;
            if (iVar21 <= iVar47) {
              iVar43 = iVar6 + 1;
              iStack_25c = iVar6;
            }
            iVar21 = *(int *)(iVar43 * 4 + param_6);
            if (iVar27 == 0) {
              puVar45[-0x200] = uStack_220;
              puVar45[-0x1c0] = uStack_224;
            }
            if (param_23 == 1) {
              puVar45[-0x1c0] = puVar45[-0x1c0] + 1;
              if (bVar1) {
                *puVar14 = 1;
              }
              else {
                *puVar14 = 0;
              }
            }
            puVar45[-0x180] = *puVar49;
            iVar6 = (iStack_1b0 * param_7 + iStack_25c) * 4;
            puVar45[-0x140] = puVar49[0x122];
            puVar42 = (uint *)(param_1 + 0x1130 + iVar6);
            uVar12 = *puVar42;
            piVar46 = (int *)(iVar6 + param_1 + 0x1108);
            iVar6 = *piVar46;
            if ((int)uVar12 < 0) {
              iVar6 = iVar6 >> (-uVar12 & 0x1f);
              pv_div(iVar6,iVar6 + 0x3fffffff,&iStack_150);
            }
            else {
              pv_div(iVar6,(0x3fffffff >> (uVar12 & 0x1f)) + iVar6,&iStack_150);
            }
            uVar12 = puVar45[-0x180];
            iVar6 = iStack_150 >> (uStack_14c & 0x1f);
            iVar13 = puVar45[-0x200] + 1;
            iVar6 = (int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar12) >> 0x20) * 4 +
                    (iVar6 * uVar12 >> 0x1e);
            if (bVar1) {
              pv_div(iVar6,iVar13,&iStack_150);
              pv_sqrt(iStack_150,((puVar45[-0x140] - puVar45[-0x1c0]) - uStack_14c) + -0x1e,
                      &uStack_148,param_22 + 0x10);
              puVar45[-0x100] = uStack_148;
              puVar45[-0xc0] = uStack_144;
              if ((puVar45[0x80] == 0) || ((iStack_21c < iVar25 && (*piVar34 == 0)))) {
                uVar12 = 0;
                *puVar45 = 0;
              }
              else {
                uVar12 = *puVar42;
                if ((int)uVar12 < 0) {
                  pv_div(puVar45[-0x180],(*piVar46 >> (-uVar12 & 0x1f)) + 0x3fffffff,&iStack_150);
                  uVar12 = 0;
                }
                else {
                  pv_div(puVar45[-0x180],(0x3fffffff >> (uVar12 & 0x1f)) + *piVar46,&iStack_150);
                }
                pv_sqrt(iStack_150,(puVar45[-0x140] - uVar12) - uStack_14c,&uStack_148,
                        param_22 + 0x20);
                *puVar45 = uStack_148;
                uVar12 = uStack_144;
              }
            }
            else {
              if (iVar4 == 0) {
                iVar24 = iStack_260;
                iVar18 = iVar35;
                if (puVar45[-0x200] != 0) {
                  uVar22 = *puVar42;
                  if ((int)uVar22 < 0) {
                    if (-10 < (int)uVar22) {
                      iVar24 = (*piVar46 >> (-uVar22 & 0x1f)) + 0x3fffffff;
                      iVar13 = (int)((ulonglong)((longlong)iVar24 * (longlong)iVar13) >> 0x20) * 4 +
                               ((uint)(iVar24 * iVar13) >> 0x1e);
                    }
                    pv_div(uVar12,iVar13,&iStack_150);
                    iVar13 = (puVar45[-0x140] - uStack_14c) + -0x1e;
                    if (puVar45[-0x200] != 0) {
                      iVar13 = iVar13 - puVar45[-0x1c0];
                    }
                    goto LAB_ram_43003596;
                  }
                  iVar24 = 0x3fffffff >> (uVar22 & 0x1f);
                }
                pv_div(uVar12,((uint)((iVar24 + *piVar46) * iVar13) >> 0x1e) +
                              (int)((ulonglong)((longlong)(iVar24 + *piVar46) * (longlong)iVar13) >>
                                   0x20) * 4,&iStack_150);
                iVar13 = (((puVar45[-0x140] - puVar45[-0x1c0]) - uStack_14c) + -0x1e) - *puVar42;
              }
              else {
                pv_div(uVar12,iVar13,&iStack_150);
                iVar13 = ((puVar45[-0x140] - puVar45[-0x1c0]) - uStack_14c) + -0x1e;
                iVar18 = param_22 + 0x30;
              }
LAB_ram_43003596:
              pv_sqrt(iStack_150,iVar13,&uStack_148,iVar18);
              *puVar45 = 0;
              puVar45[-0xc0] = uStack_144;
              puVar45[-0x100] = uStack_148;
              uVar12 = 0xffffff9c;
            }
            puVar45[0x40] = uVar12;
            uStack_210 = uStack_210 | *puVar45;
            pv_sqrt(iVar6,puVar45[-0x140],&uStack_148,param_22 + 0x50);
            puVar45[-0x80] = uStack_148;
            puVar45[-0x40] = uStack_144;
            iVar47 = iVar47 + 1;
            piVar34 = piVar34 + 1;
            puVar14 = puVar14 + 1;
            puVar45 = puVar45 + 1;
            iVar6 = iVar43;
          } while (iVar17 != iVar47);
          iVar21 = *(int *)(iStack_1f4 + 0x18);
          iVar33 = uVar36 + iVar33;
          goto LAB_ram_4300360e;
        }
        iVar21 = *(int *)(iStack_1f4 + 0x18);
        iVar47 = param_5[iVar21];
      }
      else {
        if (iVar27 == 0) {
          iVar21 = *piVar34;
          bVar1 = false;
          goto LAB_ram_4300363a;
        }
        iVar33 = iVar33 - uVar36;
LAB_ram_4300360e:
        iVar47 = param_5[iVar21];
      }
      if (iVar47 <= iVar16) goto LAB_ram_4300369a;
      puVar49 = puVar49 + 1;
      iVar47 = param_4[iVar21 * 0x3b + iVar16];
    } while( true );
  }
  uStack_210 = 0;
  goto LAB_ram_430036a8;
LAB_ram_4300369a:
  iStack_1c4 = iStack_1c4 + iVar16;
LAB_ram_430036a8:
  iVar21 = *piVar15;
  if (0 < iVar21) {
    iVar33 = 0;
    piVar34 = (int *)(iVar8 * 0x34 + param_14);
    do {
      piVar46 = piVar34 + 1;
      iVar43 = *piVar34;
      iVar47 = *piVar46;
      iVar33 = iVar33 + 1;
      if (iVar43 < iVar47) {
        iVar16 = iVar43 * 4;
        iVar5 = -100;
        iVar17 = param_20 + iVar16;
        iVar21 = -100;
        do {
          if (iVar21 < *(int *)(iVar17 + 0x300)) {
            iVar21 = *(int *)(iVar17 + 0x300);
          }
          piVar48 = (int *)(iVar17 + 0x100);
          iVar17 = iVar17 + 4;
          if (iVar5 < *piVar48) {
            iVar5 = *piVar48;
          }
        } while (param_20 + iVar47 * 4 != iVar17);
        iVar17 = iVar47 - iVar43;
        if (iVar47 != iVar43) {
          do {
            iVar17 = iVar17 >> 1;
            iVar21 = iVar21 + 1;
          } while (iVar17 != 0);
        }
        piVar48 = (int *)(param_20 + iVar16);
        iVar17 = 0;
        iVar6 = 0;
        do {
          piVar23 = piVar48 + 0x40;
          iVar6 = iVar6 + (piVar48[0x80] >> (iVar21 - piVar48[0xc0] & 0x1fU));
          iVar35 = *piVar48;
          piVar48 = piVar48 + 1;
          iVar17 = iVar17 + (iVar35 >> (iVar5 - *piVar23 & 0x1fU));
        } while ((int *)(iVar47 * 4 + param_20) != piVar48);
        uVar36 = 0x10;
        iVar35 = 0x186a0000;
        if (iVar17 == 0) {
LAB_ram_43003756:
          iVar5 = param_20 + iVar16;
          do {
            while( true ) {
              uVar22 = *(uint *)(iVar5 + 0x500);
              uVar12 = uVar22;
              if ((int)uVar22 < (int)uVar36) {
                uVar12 = uVar36;
              }
              if (*(int *)(iVar5 + 0x400) >> (uVar12 - uVar22 & 0x1f) <
                  iVar35 >> (uVar12 - uVar36 & 0x1f)) break;
              iVar43 = iVar43 + 1;
              pv_div(((uint)(iVar35 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                     (int)((ulonglong)((longlong)iVar35 * (longlong)*(int *)(iVar5 + 0x600)) >> 0x20
                          ) * 0x10,*(int *)(iVar5 + 0x400),&iStack_150);
              *(int *)(iVar5 + 0x400) = iVar35;
              *(int *)(iVar5 + 0x600) = iStack_150 >> 2;
              *(uint *)(iVar5 + 0x700) =
                   ((*(int *)(iVar5 + 0x700) + uVar36) - uStack_14c) - *(int *)(iVar5 + 0x500);
              *(uint *)(iVar5 + 0x500) = uVar36;
              iVar47 = *piVar46;
              iVar5 = iVar5 + 4;
              if (iVar47 <= iVar43) goto LAB_ram_430037dc;
            }
            iVar43 = iVar43 + 1;
            iVar5 = iVar5 + 4;
          } while (iVar43 < iVar47);
LAB_ram_430037dc:
          iVar43 = *piVar34;
          if (iVar43 < iVar47) {
            iVar16 = iVar43 * 4;
            piVar23 = (int *)(iVar37 + iVar16);
            piVar48 = (int *)(iVar37 + iVar47 * 4);
            iVar5 = -100;
            do {
              while( true ) {
                iVar17 = piVar23[-0x100] * 2 + piVar23[-0x200] + 0x1c;
                if (iVar5 < iVar17) {
                  iVar5 = iVar17;
                }
                if (piVar23[-0x40] == 0) break;
                iVar17 = *piVar23 << 1;
                if (iVar5 < *piVar23 << 1) goto LAB_ram_43003c72;
LAB_ram_4300381c:
                piVar23 = piVar23 + 1;
                if (piVar48 == piVar23) goto LAB_ram_43003822;
              }
              if ((iVar4 != 0) || (iVar17 = piVar23[-0x80] << 1, piVar23[-0x80] << 1 <= iVar5))
              goto LAB_ram_4300381c;
LAB_ram_43003c72:
              iVar5 = iVar17;
              piVar23 = piVar23 + 1;
            } while (piVar48 != piVar23);
LAB_ram_43003822:
            iVar5 = iVar5 + 1;
            piVar23 = (int *)(iVar47 * 4 + param_20 + 0x800);
            piVar48 = (int *)(param_20 + 0x800 + iVar16);
            iVar17 = 0;
            do {
              while( true ) {
                iVar35 = piVar48[-0xc0] * 2 + piVar48[-0x1c0];
                if (iVar5 - iVar35 < 0x3b) {
                  iVar13 = piVar48[-0x100];
                  iVar13 = ((uint)(iVar13 * iVar13) >> 0x1c) +
                           (int)((ulonglong)((longlong)iVar13 * (longlong)iVar13) >> 0x20) * 0x10;
                  iVar17 = iVar17 + ((int)(((uint)(piVar48[-0x200] * iVar13) >> 0x1c) +
                                          (int)((ulonglong)
                                                ((longlong)piVar48[-0x200] * (longlong)iVar13) >>
                                               0x20) * 0x10) >> (iVar5 - (iVar35 + 0x1c) & 0x1fU));
                }
                iVar35 = *piVar48;
                if (iVar35 == 0) break;
                uVar36 = iVar5 + piVar48[0x40] * -2;
                if ((int)uVar36 < 0x1f) {
                  iVar17 = iVar17 + ((int)(((uint)(iVar35 * iVar35) >> 0x1c) +
                                          (int)((ulonglong)((longlong)iVar35 * (longlong)iVar35) >>
                                               0x20) * 0x10) >> (uVar36 & 0x1f));
                }
LAB_ram_43003858:
                piVar48 = piVar48 + 1;
                if (piVar23 == piVar48) goto LAB_ram_430038dc;
              }
              if ((iVar4 != 0) || (uVar36 = iVar5 + piVar48[-0x40] * -2, 0x1e < (int)uVar36))
              goto LAB_ram_43003858;
              iVar35 = piVar48[-0x80];
              piVar48 = piVar48 + 1;
              iVar17 = iVar17 + ((int)(((uint)(iVar35 * iVar35) >> 0x1c) +
                                      (int)((ulonglong)((longlong)iVar35 * (longlong)iVar35) >> 0x20
                                           ) * 0x10) >> (uVar36 & 0x1f));
            } while (piVar23 != piVar48);
LAB_ram_430038dc:
            if (iVar17 == 0) {
              iVar21 = 0x195bb900;
              if (uStack_210 == 0) {
LAB_ram_43003c7c:
                iVar5 = iVar43 * 4 + param_20;
                if (iVar43 < iVar47) {
                  do {
                    iVar43 = iVar43 + 1;
                    *(uint *)(iVar5 + 0x400) =
                         ((uint)(iVar21 * *(int *)(iVar5 + 0x400)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar21 * (longlong)*(int *)(iVar5 + 0x400)) >>
                              0x20) * 0x10;
                    *(uint *)(iVar5 + 0x600) =
                         ((uint)(iVar21 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar21 * (longlong)*(int *)(iVar5 + 0x600)) >>
                              0x20) * 0x10;
                    iVar5 = iVar5 + 4;
                  } while (iVar43 < *piVar46);
                  iVar21 = *piVar15;
                  goto LAB_ram_43003944;
                }
              }
              else {
LAB_ram_430038ee:
                piVar34 = (int *)(iVar16 + iVar30);
                do {
                  iVar43 = iVar43 + 1;
                  *piVar34 = ((uint)(iVar21 * *piVar34) >> 0x1c) +
                             (int)((ulonglong)((longlong)iVar21 * (longlong)*piVar34) >> 0x20) *
                             0x10;
                  piVar34[0x80] =
                       ((uint)(iVar21 * piVar34[0x80]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar21 * (longlong)piVar34[0x80]) >> 0x20) * 0x10
                  ;
                  piVar34[0x100] =
                       ((uint)(iVar21 * piVar34[0x100]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar21 * (longlong)piVar34[0x100]) >> 0x20) *
                       0x10;
                  piVar34 = piVar34 + 1;
                } while (iVar43 < *piVar46);
              }
            }
            else {
              pv_div(iVar6,iVar17,&iStack_150);
              pv_sqrt(iStack_150,((iVar21 - iVar5) + -0x3a) - uStack_14c,&uStack_148,param_22 + 0x70
                     );
              if ((int)uStack_144 < -0x1b) {
                iVar21 = (int)uStack_148 >> (-uStack_144 - 0x1c & 0x1f);
              }
              else {
                iVar21 = uStack_148 << (uStack_144 + 0x1c & 0x1f);
              }
              uVar36 = uStack_144;
              if ((int)uStack_144 < -0x1c) {
                uVar36 = 0xffffffe4;
              }
              iVar43 = *piVar34;
              iVar47 = *piVar46;
              if (0x195bb900 >> (uVar36 + 0x1c & 0x1f) <
                  (int)uStack_148 >> (uVar36 - uStack_144 & 0x1f)) {
                iVar21 = 0x195bb900;
              }
              if (uStack_210 == 0) goto LAB_ram_43003c7c;
              iVar16 = iVar43 << 2;
              if (iVar43 < iVar47) goto LAB_ram_430038ee;
            }
          }
        }
        else {
          pv_div(iVar6,iVar17,&iStack_150);
          pv_sqrt(iStack_150,((iVar21 + -0x1e) - iVar5) - uStack_14c,&uStack_148,param_22 + 0x60);
          iVar35 = (int)((ulonglong)
                         ((longlong)(int)uStack_148 * (longlong)*(int *)(limGains + iVar28 * 4)) >>
                        0x20) * 4 + (uStack_148 * *(int *)(limGains + iVar28 * 4) >> 0x1e);
          uVar36 = limGains._16_4_;
          if (iVar28 != 3) {
            uVar36 = uStack_144;
          }
          uVar12 = uVar36;
          if ((int)uVar36 < 0x10) {
            uVar12 = 0x10;
          }
          iVar43 = *piVar34;
          iVar47 = *piVar46;
          if (0x186a0000 >> (uVar12 - 0x10 & 0x1f) < iVar35 >> (uVar12 - uVar36 & 0x1f)) {
            iVar35 = 0x186a0000;
            uVar36 = 0x10;
          }
          iVar16 = iVar43 << 2;
          if (iVar43 < iVar47) goto LAB_ram_43003756;
        }
        iVar21 = *piVar15;
      }
LAB_ram_43003944:
      piVar34 = piVar46;
    } while (iVar33 < iVar21);
  }
  if (param_23 == 1) {
    sbr_aliasing_reduction
              (param_9,iVar30,iVar11,param_20,iVar19,auStack_140,uVar20,iVar29,param_22,
               param_20 + 0x300);
    if (*param_13 != 0) {
      *param_13 = 0;
    }
    envelope_application_LC
              (param_2,iVar30,iVar11,iVar31,iVar32,param_20 + 0x800,iVar37,uStack_210,iVar7,param_10
               ,param_11,iStack_21c,iVar29,uVar20,iVar4);
  }
  else {
    if (*param_13 != 0) {
      puVar14 = param_19;
      puVar9 = param_17;
      puVar38 = param_18;
      puVar40 = param_16;
      if (0 < iVar2) {
        do {
          memcpy(*puVar40,iVar30,iVar44);
          memcpy(*puVar38,iVar31,iVar44);
          memcpy(*puVar9,iVar11,iVar44);
          puVar40 = puVar40 + 1;
          memcpy(*puVar14,iVar32,iVar44);
          puVar14 = puVar14 + 1;
          puVar9 = puVar9 + 1;
          puVar38 = puVar38 + 1;
        } while (param_16 + iVar2 != puVar40);
      }
      *param_13 = 0;
    }
    envelope_application
              (param_2,param_3,iVar30,iVar11,iVar31,iVar32,param_20 + 0x800,iVar37,param_16,param_17
               ,param_18,param_19,iVar7,param_10,param_11,iStack_21c,iVar29,uVar20,iVar4,uStack_210,
               iVar2,uVar41);
  }
  iStack_21c = iStack_21c + 1;
  piStack_1d0 = piStack_1d0 + 1;
  iStack_1f4 = iStack_1f4 + 4;
  if (iVar10 == iStack_21c) goto LAB_ram_430039fc;
  goto LAB_ram_430032a0;
}
