/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_envelope @ ram:430030b2
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_envelope(aac_sbr_frame_abi_t *frame,undefined4 param_2,undefined4 param_3,int *param_4
                      ,int *param_5,int param_6,int param_7,int param_8,undefined4 param_9,
                      undefined4 param_10,undefined4 *param_11,int param_12,int *param_13,
                      int param_14,int param_15,undefined4 *param_16,undefined4 *param_17,
                      undefined4 *param_18,undefined4 *param_19,int param_20,undefined4 *param_21,
                      int param_22,int param_23)

{
  bool bVar1;
  int iVar2;
  bool bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int32_t *piVar8;
  int iVar9;
  int32_t *piVar10;
  undefined4 *puVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  aac_analysis_harmonics_t *paVar16;
  int *piVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  int iVar23;
  uint uVar24;
  int *piVar25;
  int iVar26;
  int iVar27;
  int iVar28;
  int iVar29;
  int iVar30;
  int iVar31;
  int iVar32;
  int iVar33;
  int iVar34;
  int iVar35;
  int *piVar36;
  int iVar37;
  uint uVar38;
  int iVar39;
  undefined4 *puVar40;
  int iVar41;
  undefined4 *puVar42;
  undefined4 uVar43;
  int32_t *piVar44;
  int iVar45;
  int iVar46;
  uint *puVar47;
  int *piVar48;
  int iVar49;
  int *piVar50;
  int32_t *piVar51;
  int iStack_260;
  int iStack_25c;
  uint uStack_224;
  uint uStack_220;
  int iStack_21c;
  uint uStack_210;
  int32_t *piStack_1f4;
  int iStack_1d8;
  int32_t *piStack_1d0;
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
  iVar12 = (frame->frame_control).frame_info[0];
  piVar8 = (frame->frame_control).frame_info;
  iVar27 = piVar8[iVar12 * 2 + 2];
  iVar28 = param_20 + 0xa00;
  iVar29 = (frame->header).interpolate_frequency;
  iVar30 = (frame->header).limiter_gains;
  iVar39 = param_4[*param_5];
  iVar41 = (frame->header).smoothing_mode;
  iVar9 = (frame->header).limiter_bands;
  iVar31 = *param_4;
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
  memset(iVar28,0,0x100);
  iVar21 = param_5[1];
  if (iVar21 != 0) {
    paVar16 = &frame->harmonics_and_envelopes;
    iVar32 = param_4[0x3b];
    piVar17 = param_4 + 0x3c;
    do {
      iVar13 = *piVar17;
      iVar21 = iVar21 + -1;
      *(int32_t *)(((iVar32 + iVar13 >> 1) - iVar31) * 4 + iVar28) = paVar16->add_harmonics[0];
      paVar16 = (aac_analysis_harmonics_t *)(paVar16->add_harmonics + 1);
      iVar32 = iVar13;
      piVar17 = piVar17 + 1;
    } while (iVar21 != 0);
  }
  if (iVar12 < 1) {
LAB_ram_430039fc:
    iStack_1d8 = iVar31 * 4;
    memcpy(param_12 + iStack_1d8,iVar28,(0x40 - iVar31) * 4);
    (frame->frame_control).previous_short_envelope = -(uint)(iVar12 != iVar27);
    return;
  }
  uVar22 = iVar39 - iVar31 >> 0x1f ^ iVar39 - iVar31;
  iVar39 = param_20 + 0x900;
  iVar21 = param_20 + 0x100;
  iVar32 = param_20 + 0x400;
  iVar13 = param_20 + 0x500;
  iVar33 = param_20 + 0x600;
  iVar34 = param_20 + 0x700;
  if (0x40 < (int)uVar22) {
    uVar22 = 0x40;
  }
  piVar17 = (int *)(param_15 + iVar9 * 4);
  piStack_1f4 = (frame->frame_control).frame_info + iVar12 + -4;
  piStack_1d0 = (frame->frame_control).frame_info;
  iVar46 = uVar22 << 2;
  iStack_21c = 0;
  uStack_224 = 0;
  uStack_220 = 0;
  iStack_1b0 = -1;
  iStack_1b4 = 0;
  iStack_1c4 = 0;
LAB_ram_430032a0:
  piStack_1d0 = piStack_1d0 + 1;
  if (*piStack_1d0 == piVar8[iVar12 * 2 + 4 + iStack_1b4]) {
    iStack_1b4 = iStack_1b4 + 1;
    iStack_1b0 = iStack_1b0 + 1;
  }
  if ((iVar27 == iStack_21c) || ((frame->frame_control).previous_short_envelope == iStack_21c)) {
    iVar4 = 1;
    iVar23 = piStack_1f4[6];
    uVar43 = 0;
    iVar35 = param_5[iVar23];
  }
  else {
    iVar4 = 0;
    uVar43 = (&smoothLengths)[iVar41];
    iVar23 = piStack_1f4[6];
    iVar35 = param_5[iVar23];
  }
  if (0 < iVar35) {
    piVar51 = (frame->envelope_and_noise).envelope_mantissa + iStack_1c4;
    iStack_260 = 0x3fffffff;
    iStack_25c = 0;
    iVar35 = 0;
    iVar45 = 1;
    uStack_210 = 0;
    iVar18 = 0;
    iVar5 = param_4[iVar23 * 0x3b];
    iVar49 = iVar5;
    do {
      iVar18 = iVar18 + 1;
      piVar36 = (int *)(iVar45 * 4 + param_6);
      iVar19 = param_4[iVar23 * 0x3b + iVar18];
      uVar38 = iVar19 - iVar49;
      if (iVar49 < iVar19) {
        piVar48 = (int *)(param_12 + (iVar35 + iVar31) * 4);
        piVar50 = (int *)(iVar35 * 4 + iVar28);
        iVar6 = (iVar35 - iVar49) + iVar19;
        iVar23 = iVar35;
        bVar3 = false;
        do {
          while( true ) {
            bVar1 = bVar3;
            iVar37 = iVar23;
            iVar23 = ((iVar49 - iVar5) - iVar35) + iVar37;
            if (param_23 == 1) {
              energy_estimation_LC
                        (param_2,param_20,iVar21,piVar8,iStack_21c,iVar23,iVar37,*piStack_1d0 << 1);
            }
            else {
              energy_estimation(param_2,param_3,param_20,iVar21,piVar8,iStack_21c,iVar23,iVar37,
                                *piStack_1d0 << 1);
            }
            if (*piVar50 != 0) break;
LAB_ram_430033da:
            piVar48 = piVar48 + 1;
            piVar50 = piVar50 + 1;
            iVar23 = iVar37 + 1;
            bVar3 = bVar1;
            if (iVar6 == iVar37 + 1) goto LAB_ram_43003426;
          }
          if (iStack_21c < iVar27) {
            bVar1 = (bool)(bVar1 | *piVar48 != 0);
            goto LAB_ram_430033da;
          }
          bVar1 = true;
          piVar48 = piVar48 + 1;
          piVar50 = piVar50 + 1;
          iVar23 = iVar37 + 1;
          bVar3 = true;
        } while (iVar6 != iVar37 + 1);
LAB_ram_43003426:
        iVar35 = iVar37 + 1;
        iVar23 = *piVar36;
        iVar6 = iVar6 - uVar38;
        if (iVar29 == 0) {
LAB_ram_4300363a:
          iVar6 = iVar35 - uVar38;
          if (iVar6 < iVar35) {
            piVar48 = (int *)(iVar6 * 4 + param_20);
            piVar50 = (int *)(iVar35 * 4 + param_20);
            uStack_224 = 0xffffff9c;
            piVar36 = piVar48;
            do {
              puVar47 = (uint *)(piVar36 + 0x40);
              piVar36 = piVar36 + 1;
              if ((int)uStack_224 < (int)*puVar47) {
                uStack_224 = *puVar47;
              }
            } while (piVar50 != piVar36);
            uStack_220 = 0;
            do {
              piVar36 = piVar48 + 0x40;
              iVar35 = *piVar48;
              piVar48 = piVar48 + 1;
              uStack_220 = uStack_220 + (iVar35 >> (uStack_224 - *piVar36 & 0x1f));
            } while (piVar50 != piVar48);
            uStack_220 = uStack_220 / uVar38;
          }
          else {
            uStack_220 = 0;
            uStack_224 = 0xffffff9c;
          }
        }
        iVar35 = iVar6;
        if (0 < (int)uVar38) {
          piVar36 = (int *)((iVar31 + iVar35) * 4 + param_12);
          puVar7 = auStack_140 + (iVar49 - iVar31);
          puVar47 = (uint *)(param_20 + 0x800 + iVar35 * 4);
          iVar37 = param_22 + 0x40;
          iVar6 = iVar45;
          do {
            iVar45 = iVar6;
            if (iVar23 <= iVar49) {
              iVar45 = iVar6 + 1;
              iStack_25c = iVar6;
            }
            iVar23 = *(int *)(iVar45 * 4 + param_6);
            if (iVar29 == 0) {
              puVar47[-0x200] = uStack_220;
              puVar47[-0x1c0] = uStack_224;
            }
            if (param_23 == 1) {
              puVar47[-0x1c0] = puVar47[-0x1c0] + 1;
              if (bVar1) {
                *puVar7 = 1;
              }
              else {
                *puVar7 = 0;
              }
            }
            puVar47[-0x180] = *piVar51;
            iVar6 = iStack_1b0 * param_7 + iStack_25c;
            puVar47[-0x140] = piVar51[0x122];
            piVar44 = (frame->envelope_and_noise).noise_exponent + iVar6;
            uVar14 = *piVar44;
            piVar10 = (frame->envelope_and_noise).noise_mantissa + iVar6;
            iVar6 = *piVar10;
            if ((int)uVar14 < 0) {
              iVar6 = iVar6 >> (-uVar14 & 0x1f);
              pv_div(iVar6,iVar6 + 0x3fffffff,&iStack_150);
            }
            else {
              pv_div(iVar6,(0x3fffffff >> (uVar14 & 0x1f)) + iVar6,&iStack_150);
            }
            uVar14 = puVar47[-0x180];
            iVar6 = iStack_150 >> (uStack_14c & 0x1f);
            iVar15 = puVar47[-0x200] + 1;
            iVar6 = (int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar14) >> 0x20) * 4 +
                    (iVar6 * uVar14 >> 0x1e);
            if (bVar1) {
              pv_div(iVar6,iVar15,&iStack_150);
              pv_sqrt(iStack_150,((puVar47[-0x140] - puVar47[-0x1c0]) - uStack_14c) + -0x1e,
                      &uStack_148,param_22 + 0x10);
              puVar47[-0x100] = uStack_148;
              puVar47[-0xc0] = uStack_144;
              if ((puVar47[0x80] == 0) || ((iStack_21c < iVar27 && (*piVar36 == 0)))) {
                uVar14 = 0;
                *puVar47 = 0;
              }
              else {
                uVar14 = *piVar44;
                if ((int)uVar14 < 0) {
                  pv_div(puVar47[-0x180],(*piVar10 >> (-uVar14 & 0x1f)) + 0x3fffffff,&iStack_150);
                  uVar14 = 0;
                }
                else {
                  pv_div(puVar47[-0x180],(0x3fffffff >> (uVar14 & 0x1f)) + *piVar10,&iStack_150);
                }
                pv_sqrt(iStack_150,(puVar47[-0x140] - uVar14) - uStack_14c,&uStack_148,
                        param_22 + 0x20);
                *puVar47 = uStack_148;
                uVar14 = uStack_144;
              }
            }
            else {
              if (iVar4 == 0) {
                iVar26 = iStack_260;
                iVar20 = iVar37;
                if (puVar47[-0x200] != 0) {
                  uVar24 = *piVar44;
                  if ((int)uVar24 < 0) {
                    if (-10 < (int)uVar24) {
                      iVar26 = (*piVar10 >> (-uVar24 & 0x1f)) + 0x3fffffff;
                      iVar15 = (int)((ulonglong)((longlong)iVar26 * (longlong)iVar15) >> 0x20) * 4 +
                               ((uint)(iVar26 * iVar15) >> 0x1e);
                    }
                    pv_div(uVar14,iVar15,&iStack_150);
                    iVar15 = (puVar47[-0x140] - uStack_14c) + -0x1e;
                    if (puVar47[-0x200] != 0) {
                      iVar15 = iVar15 - puVar47[-0x1c0];
                    }
                    goto LAB_ram_43003596;
                  }
                  iVar26 = 0x3fffffff >> (uVar24 & 0x1f);
                }
                pv_div(uVar14,((uint)((iVar26 + *piVar10) * iVar15) >> 0x1e) +
                              (int)((ulonglong)((longlong)(iVar26 + *piVar10) * (longlong)iVar15) >>
                                   0x20) * 4,&iStack_150);
                iVar15 = (((puVar47[-0x140] - puVar47[-0x1c0]) - uStack_14c) + -0x1e) - *piVar44;
              }
              else {
                pv_div(uVar14,iVar15,&iStack_150);
                iVar15 = ((puVar47[-0x140] - puVar47[-0x1c0]) - uStack_14c) + -0x1e;
                iVar20 = param_22 + 0x30;
              }
LAB_ram_43003596:
              pv_sqrt(iStack_150,iVar15,&uStack_148,iVar20);
              *puVar47 = 0;
              puVar47[-0xc0] = uStack_144;
              puVar47[-0x100] = uStack_148;
              uVar14 = 0xffffff9c;
            }
            puVar47[0x40] = uVar14;
            uStack_210 = uStack_210 | *puVar47;
            pv_sqrt(iVar6,puVar47[-0x140],&uStack_148,param_22 + 0x50);
            puVar47[-0x80] = uStack_148;
            puVar47[-0x40] = uStack_144;
            iVar49 = iVar49 + 1;
            piVar36 = piVar36 + 1;
            puVar7 = puVar7 + 1;
            puVar47 = puVar47 + 1;
            iVar6 = iVar45;
          } while (iVar19 != iVar49);
          iVar23 = piStack_1f4[6];
          iVar35 = uVar38 + iVar35;
          goto LAB_ram_4300360e;
        }
        iVar23 = piStack_1f4[6];
        iVar49 = param_5[iVar23];
      }
      else {
        if (iVar29 == 0) {
          iVar23 = *piVar36;
          bVar1 = false;
          goto LAB_ram_4300363a;
        }
        iVar35 = iVar35 - uVar38;
LAB_ram_4300360e:
        iVar49 = param_5[iVar23];
      }
      if (iVar49 <= iVar18) goto LAB_ram_4300369a;
      piVar51 = piVar51 + 1;
      iVar49 = param_4[iVar23 * 0x3b + iVar18];
    } while( true );
  }
  uStack_210 = 0;
  goto LAB_ram_430036a8;
LAB_ram_4300369a:
  iStack_1c4 = iStack_1c4 + iVar18;
LAB_ram_430036a8:
  iVar23 = *piVar17;
  if (0 < iVar23) {
    iVar35 = 0;
    piVar36 = (int *)(iVar9 * 0x34 + param_14);
    do {
      piVar48 = piVar36 + 1;
      iVar45 = *piVar36;
      iVar49 = *piVar48;
      iVar35 = iVar35 + 1;
      if (iVar45 < iVar49) {
        iVar18 = iVar45 * 4;
        iVar5 = -100;
        iVar19 = param_20 + iVar18;
        iVar23 = -100;
        do {
          if (iVar23 < *(int *)(iVar19 + 0x300)) {
            iVar23 = *(int *)(iVar19 + 0x300);
          }
          piVar50 = (int *)(iVar19 + 0x100);
          iVar19 = iVar19 + 4;
          if (iVar5 < *piVar50) {
            iVar5 = *piVar50;
          }
        } while (param_20 + iVar49 * 4 != iVar19);
        iVar19 = iVar49 - iVar45;
        if (iVar49 != iVar45) {
          do {
            iVar19 = iVar19 >> 1;
            iVar23 = iVar23 + 1;
          } while (iVar19 != 0);
        }
        piVar50 = (int *)(param_20 + iVar18);
        iVar19 = 0;
        iVar6 = 0;
        do {
          piVar25 = piVar50 + 0x40;
          iVar6 = iVar6 + (piVar50[0x80] >> (iVar23 - piVar50[0xc0] & 0x1fU));
          iVar37 = *piVar50;
          piVar50 = piVar50 + 1;
          iVar19 = iVar19 + (iVar37 >> (iVar5 - *piVar25 & 0x1fU));
        } while ((int *)(iVar49 * 4 + param_20) != piVar50);
        uVar38 = 0x10;
        iVar37 = 0x186a0000;
        if (iVar19 == 0) {
LAB_ram_43003756:
          iVar5 = param_20 + iVar18;
          do {
            while( true ) {
              uVar24 = *(uint *)(iVar5 + 0x500);
              uVar14 = uVar24;
              if ((int)uVar24 < (int)uVar38) {
                uVar14 = uVar38;
              }
              if (*(int *)(iVar5 + 0x400) >> (uVar14 - uVar24 & 0x1f) <
                  iVar37 >> (uVar14 - uVar38 & 0x1f)) break;
              iVar45 = iVar45 + 1;
              pv_div(((uint)(iVar37 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                     (int)((ulonglong)((longlong)iVar37 * (longlong)*(int *)(iVar5 + 0x600)) >> 0x20
                          ) * 0x10,*(int *)(iVar5 + 0x400),&iStack_150);
              *(int *)(iVar5 + 0x400) = iVar37;
              *(int *)(iVar5 + 0x600) = iStack_150 >> 2;
              *(uint *)(iVar5 + 0x700) =
                   ((*(int *)(iVar5 + 0x700) + uVar38) - uStack_14c) - *(int *)(iVar5 + 0x500);
              *(uint *)(iVar5 + 0x500) = uVar38;
              iVar49 = *piVar48;
              iVar5 = iVar5 + 4;
              if (iVar49 <= iVar45) goto LAB_ram_430037dc;
            }
            iVar45 = iVar45 + 1;
            iVar5 = iVar5 + 4;
          } while (iVar45 < iVar49);
LAB_ram_430037dc:
          iVar45 = *piVar36;
          if (iVar45 < iVar49) {
            iVar18 = iVar45 * 4;
            piVar25 = (int *)(iVar39 + iVar18);
            piVar50 = (int *)(iVar39 + iVar49 * 4);
            iVar5 = -100;
            do {
              while( true ) {
                iVar19 = piVar25[-0x100] * 2 + piVar25[-0x200] + 0x1c;
                if (iVar5 < iVar19) {
                  iVar5 = iVar19;
                }
                if (piVar25[-0x40] == 0) break;
                iVar19 = *piVar25 << 1;
                if (iVar5 < *piVar25 << 1) goto LAB_ram_43003c72;
LAB_ram_4300381c:
                piVar25 = piVar25 + 1;
                if (piVar50 == piVar25) goto LAB_ram_43003822;
              }
              if ((iVar4 != 0) || (iVar19 = piVar25[-0x80] << 1, piVar25[-0x80] << 1 <= iVar5))
              goto LAB_ram_4300381c;
LAB_ram_43003c72:
              iVar5 = iVar19;
              piVar25 = piVar25 + 1;
            } while (piVar50 != piVar25);
LAB_ram_43003822:
            iVar5 = iVar5 + 1;
            piVar25 = (int *)(iVar49 * 4 + param_20 + 0x800);
            piVar50 = (int *)(param_20 + 0x800 + iVar18);
            iVar19 = 0;
            do {
              while( true ) {
                iVar37 = piVar50[-0xc0] * 2 + piVar50[-0x1c0];
                if (iVar5 - iVar37 < 0x3b) {
                  iVar15 = piVar50[-0x100];
                  iVar15 = ((uint)(iVar15 * iVar15) >> 0x1c) +
                           (int)((ulonglong)((longlong)iVar15 * (longlong)iVar15) >> 0x20) * 0x10;
                  iVar19 = iVar19 + ((int)(((uint)(piVar50[-0x200] * iVar15) >> 0x1c) +
                                          (int)((ulonglong)
                                                ((longlong)piVar50[-0x200] * (longlong)iVar15) >>
                                               0x20) * 0x10) >> (iVar5 - (iVar37 + 0x1c) & 0x1fU));
                }
                iVar37 = *piVar50;
                if (iVar37 == 0) break;
                uVar38 = iVar5 + piVar50[0x40] * -2;
                if ((int)uVar38 < 0x1f) {
                  iVar19 = iVar19 + ((int)(((uint)(iVar37 * iVar37) >> 0x1c) +
                                          (int)((ulonglong)((longlong)iVar37 * (longlong)iVar37) >>
                                               0x20) * 0x10) >> (uVar38 & 0x1f));
                }
LAB_ram_43003858:
                piVar50 = piVar50 + 1;
                if (piVar25 == piVar50) goto LAB_ram_430038dc;
              }
              if ((iVar4 != 0) || (uVar38 = iVar5 + piVar50[-0x40] * -2, 0x1e < (int)uVar38))
              goto LAB_ram_43003858;
              iVar37 = piVar50[-0x80];
              piVar50 = piVar50 + 1;
              iVar19 = iVar19 + ((int)(((uint)(iVar37 * iVar37) >> 0x1c) +
                                      (int)((ulonglong)((longlong)iVar37 * (longlong)iVar37) >> 0x20
                                           ) * 0x10) >> (uVar38 & 0x1f));
            } while (piVar25 != piVar50);
LAB_ram_430038dc:
            if (iVar19 == 0) {
              iVar23 = 0x195bb900;
              if (uStack_210 == 0) {
LAB_ram_43003c7c:
                iVar5 = iVar45 * 4 + param_20;
                if (iVar45 < iVar49) {
                  do {
                    iVar45 = iVar45 + 1;
                    *(uint *)(iVar5 + 0x400) =
                         ((uint)(iVar23 * *(int *)(iVar5 + 0x400)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar23 * (longlong)*(int *)(iVar5 + 0x400)) >>
                              0x20) * 0x10;
                    *(uint *)(iVar5 + 0x600) =
                         ((uint)(iVar23 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar23 * (longlong)*(int *)(iVar5 + 0x600)) >>
                              0x20) * 0x10;
                    iVar5 = iVar5 + 4;
                  } while (iVar45 < *piVar48);
                  iVar23 = *piVar17;
                  goto LAB_ram_43003944;
                }
              }
              else {
LAB_ram_430038ee:
                piVar36 = (int *)(iVar18 + iVar32);
                do {
                  iVar45 = iVar45 + 1;
                  *piVar36 = ((uint)(iVar23 * *piVar36) >> 0x1c) +
                             (int)((ulonglong)((longlong)iVar23 * (longlong)*piVar36) >> 0x20) *
                             0x10;
                  piVar36[0x80] =
                       ((uint)(iVar23 * piVar36[0x80]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar23 * (longlong)piVar36[0x80]) >> 0x20) * 0x10
                  ;
                  piVar36[0x100] =
                       ((uint)(iVar23 * piVar36[0x100]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar23 * (longlong)piVar36[0x100]) >> 0x20) *
                       0x10;
                  piVar36 = piVar36 + 1;
                } while (iVar45 < *piVar48);
              }
            }
            else {
              pv_div(iVar6,iVar19,&iStack_150);
              pv_sqrt(iStack_150,((iVar23 - iVar5) + -0x3a) - uStack_14c,&uStack_148,param_22 + 0x70
                     );
              if ((int)uStack_144 < -0x1b) {
                iVar23 = (int)uStack_148 >> (-uStack_144 - 0x1c & 0x1f);
              }
              else {
                iVar23 = uStack_148 << (uStack_144 + 0x1c & 0x1f);
              }
              uVar38 = uStack_144;
              if ((int)uStack_144 < -0x1c) {
                uVar38 = 0xffffffe4;
              }
              iVar45 = *piVar36;
              iVar49 = *piVar48;
              if (0x195bb900 >> (uVar38 + 0x1c & 0x1f) <
                  (int)uStack_148 >> (uVar38 - uStack_144 & 0x1f)) {
                iVar23 = 0x195bb900;
              }
              if (uStack_210 == 0) goto LAB_ram_43003c7c;
              iVar18 = iVar45 << 2;
              if (iVar45 < iVar49) goto LAB_ram_430038ee;
            }
          }
        }
        else {
          pv_div(iVar6,iVar19,&iStack_150);
          pv_sqrt(iStack_150,((iVar23 + -0x1e) - iVar5) - uStack_14c,&uStack_148,param_22 + 0x60);
          iVar37 = (int)((ulonglong)
                         ((longlong)(int)uStack_148 * (longlong)*(int *)(limGains + iVar30 * 4)) >>
                        0x20) * 4 + (uStack_148 * *(int *)(limGains + iVar30 * 4) >> 0x1e);
          uVar38 = limGains._16_4_;
          if (iVar30 != 3) {
            uVar38 = uStack_144;
          }
          uVar14 = uVar38;
          if ((int)uVar38 < 0x10) {
            uVar14 = 0x10;
          }
          iVar45 = *piVar36;
          iVar49 = *piVar48;
          if (0x186a0000 >> (uVar14 - 0x10 & 0x1f) < iVar37 >> (uVar14 - uVar38 & 0x1f)) {
            iVar37 = 0x186a0000;
            uVar38 = 0x10;
          }
          iVar18 = iVar45 << 2;
          if (iVar45 < iVar49) goto LAB_ram_43003756;
        }
        iVar23 = *piVar17;
      }
LAB_ram_43003944:
      piVar36 = piVar48;
    } while (iVar35 < iVar23);
  }
  if (param_23 == 1) {
    sbr_aliasing_reduction
              (param_9,iVar32,iVar13,param_20,iVar21,auStack_140,uVar22,iVar31,param_22,
               param_20 + 0x300);
    if (*param_13 != 0) {
      *param_13 = 0;
    }
    envelope_application_LC
              (param_2,iVar32,iVar13,iVar33,iVar34,param_20 + 0x800,iVar39,uStack_210,piVar8,
               param_10,param_11,iStack_21c,iVar31,uVar22,iVar4);
  }
  else {
    if (*param_13 != 0) {
      puVar7 = param_19;
      puVar11 = param_17;
      puVar40 = param_18;
      puVar42 = param_16;
      if (0 < iVar2) {
        do {
          memcpy(*puVar42,iVar32,iVar46);
          memcpy(*puVar40,iVar33,iVar46);
          memcpy(*puVar11,iVar13,iVar46);
          puVar42 = puVar42 + 1;
          memcpy(*puVar7,iVar34,iVar46);
          puVar7 = puVar7 + 1;
          puVar11 = puVar11 + 1;
          puVar40 = puVar40 + 1;
        } while (param_16 + iVar2 != puVar42);
      }
      *param_13 = 0;
    }
    envelope_application
              (param_2,param_3,iVar32,iVar13,iVar33,iVar34,param_20 + 0x800,iVar39,param_16,param_17
               ,param_18,param_19,piVar8,param_10,param_11,iStack_21c,iVar31,uVar22,iVar4,uStack_210
               ,iVar2,uVar43);
  }
  iStack_21c = iStack_21c + 1;
  piStack_1f4 = piStack_1f4 + 1;
  if (iVar12 == iStack_21c) goto LAB_ram_430039fc;
  goto LAB_ram_430032a0;
}
