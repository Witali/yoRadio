/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: calc_sbr_envelope @ ram:430030b2
 * Types and parameter counts are inferred; verify against disassembly. */

void calc_sbr_envelope(aac_sbr_frame_abi_t *frame,undefined4 param_2,undefined4 param_3,int *param_4
                      ,int *param_5,int param_6,int param_7,int param_8,undefined4 param_9,
                      undefined4 param_10,undefined4 *param_11,int param_12,int *param_13,
                      int param_14,int param_15,undefined4 *param_16,undefined4 *param_17,
                      undefined4 *param_18,undefined4 *param_19,
                      aac_analysis_envelope_workspace_t *scratch,aac_analysis_patch_t *patch,
                      aac_analysis_sqrt_cache_t *sqrt_cache,int param_23)

{
  uint *puVar1;
  bool bVar2;
  int iVar3;
  bool bVar4;
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
  int32_t *piVar19;
  int iVar20;
  aac_analysis_sqrt_cache_t *paVar21;
  int iVar22;
  uint uVar23;
  int iVar24;
  uint uVar25;
  int iVar26;
  int iVar27;
  int32_t *piVar28;
  int iVar29;
  int iVar30;
  int iVar31;
  int32_t *piVar32;
  int32_t *piVar33;
  int32_t *piVar34;
  int32_t *piVar35;
  int32_t *piVar36;
  int32_t *piVar37;
  int *piVar38;
  aac_analysis_sqrt_cache_t *paVar39;
  uint uVar40;
  int iVar41;
  undefined4 *puVar42;
  int iVar43;
  undefined4 *puVar44;
  undefined4 uVar45;
  int32_t *piVar46;
  int iVar47;
  int *piVar48;
  int32_t *piVar49;
  int iVar50;
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
  aac_analysis_patch_t aStack_170;
  aac_analysis_fraction_t aStack_150;
  aac_analysis_fraction_t aStack_148;
  undefined4 auStack_140 [67];

  iVar3 = smoothLengths;
  gp = &__global_pointer_;
  iVar12 = (frame->frame_control).frame_info[0];
  piVar8 = (frame->frame_control).frame_info;
  iVar27 = piVar8[iVar12 * 2 + 2];
  piVar28 = scratch->harmonics;
  iVar29 = (frame->header).interpolate_frequency;
  iVar30 = (frame->header).limiter_gains;
  iVar41 = param_4[*param_5];
  iVar43 = (frame->header).smoothing_mode;
  iVar9 = (frame->header).limiter_bands;
  iVar31 = *param_4;
  if (param_8 != 0) {
    aStack_170.count = patch->count;
    *param_13 = 1;
    aStack_170.start_band[0] = patch->start_band[0];
    aStack_170.start_band[1] = patch->start_band[1];
    *param_11 = 0;
    aStack_170.start_band[2] = patch->start_band[2];
    aStack_170.start_band[3] = patch->start_band[3];
    aStack_170.start_band[4] = patch->start_band[4];
    aStack_170.start_band[5] = patch->start_band[5];
    sbr_create_limiter_bands((int *)param_14,(int *)param_15,param_4,&aStack_170,*param_5);
  }
  memset(piVar28,0,0x100);
  iVar22 = param_5[1];
  if (iVar22 != 0) {
    paVar16 = &frame->harmonics_and_envelopes;
    iVar24 = param_4[0x3b];
    piVar17 = param_4 + 0x3c;
    do {
      iVar13 = *piVar17;
      iVar22 = iVar22 + -1;
      piVar28[(iVar24 + iVar13 >> 1) - iVar31] = paVar16->add_harmonics[0];
      paVar16 = (aac_analysis_harmonics_t *)(paVar16->add_harmonics + 1);
      iVar24 = iVar13;
      piVar17 = piVar17 + 1;
    } while (iVar22 != 0);
  }
  if (iVar12 < 1) {
LAB_ram_430039fc:
    iStack_1d8 = iVar31 * 4;
    memcpy(param_12 + iStack_1d8,piVar28,(0x40 - iVar31) * 4);
    (frame->frame_control).previous_short_envelope = -(uint)(iVar12 != iVar27);
    return;
  }
  uVar23 = iVar41 - iVar31 >> 0x1f ^ iVar41 - iVar31;
  piVar32 = scratch->tone_exponent;
  piVar33 = scratch->estimated_exponent;
  piVar34 = scratch->gain_mantissa;
  piVar35 = scratch->gain_exponent;
  piVar36 = scratch->noise_mantissa;
  piVar37 = scratch->noise_exponent;
  if (0x40 < (int)uVar23) {
    uVar23 = 0x40;
  }
  piVar17 = (int *)(param_15 + iVar9 * 4);
  piStack_1f4 = (frame->frame_control).frame_info + iVar12 + -4;
  piStack_1d0 = (frame->frame_control).frame_info;
  iVar41 = uVar23 << 2;
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
    iVar22 = 1;
    iVar24 = piStack_1f4[6];
    uVar45 = 0;
    iVar13 = param_5[iVar24];
  }
  else {
    iVar22 = 0;
    uVar45 = (&smoothLengths)[iVar43];
    iVar24 = piStack_1f4[6];
    iVar13 = param_5[iVar24];
  }
  if (0 < iVar13) {
    piVar19 = (frame->envelope_and_noise).envelope_mantissa + iStack_1c4;
    iStack_260 = 0x3fffffff;
    iStack_25c = 0;
    iVar13 = 0;
    iVar47 = 1;
    uStack_210 = 0;
    iVar18 = 0;
    iVar5 = param_4[iVar24 * 0x3b];
    iVar50 = iVar5;
    do {
      iVar18 = iVar18 + 1;
      piVar38 = (int *)(iVar47 * 4 + param_6);
      iVar20 = param_4[iVar24 * 0x3b + iVar18];
      uVar40 = iVar20 - iVar50;
      if (iVar50 < iVar20) {
        piVar48 = (int *)(param_12 + (iVar13 + iVar31) * 4);
        piVar49 = piVar28 + iVar13;
        iVar6 = (iVar13 - iVar50) + iVar20;
        iVar24 = iVar13;
        bVar4 = false;
        do {
          while( true ) {
            bVar2 = bVar4;
            iVar15 = iVar24;
            iVar24 = ((iVar50 - iVar5) - iVar13) + iVar15;
            if (param_23 == 1) {
              energy_estimation_LC
                        (param_2,scratch,piVar33,piVar8,iStack_21c,iVar24,iVar15,*piStack_1d0 << 1);
            }
            else {
              energy_estimation(param_2,param_3,scratch,piVar33,piVar8,iStack_21c,iVar24,iVar15,
                                *piStack_1d0 << 1);
            }
            if (*piVar49 != 0) break;
LAB_ram_430033da:
            piVar48 = piVar48 + 1;
            piVar49 = piVar49 + 1;
            iVar24 = iVar15 + 1;
            bVar4 = bVar2;
            if (iVar6 == iVar15 + 1) goto LAB_ram_43003426;
          }
          if (iStack_21c < iVar27) {
            bVar2 = (bool)(bVar2 | *piVar48 != 0);
            goto LAB_ram_430033da;
          }
          bVar2 = true;
          piVar48 = piVar48 + 1;
          piVar49 = piVar49 + 1;
          iVar24 = iVar15 + 1;
          bVar4 = true;
        } while (iVar6 != iVar15 + 1);
LAB_ram_43003426:
        iVar13 = iVar15 + 1;
        iVar24 = *piVar38;
        iVar6 = iVar6 - uVar40;
        if (iVar29 == 0) {
LAB_ram_4300363a:
          iVar6 = iVar13 - uVar40;
          if (iVar6 < iVar13) {
            piVar48 = (int *)(iVar6 * 4 + (int)scratch);
            uStack_224 = 0xffffff9c;
            piVar38 = piVar48;
            do {
              puVar1 = (uint *)(piVar38 + 0x40);
              piVar38 = piVar38 + 1;
              if ((int)uStack_224 < (int)*puVar1) {
                uStack_224 = *puVar1;
              }
            } while (scratch->estimated_mantissa + iVar13 != piVar38);
            uStack_220 = 0;
            do {
              piVar38 = piVar48 + 0x40;
              iVar15 = *piVar48;
              piVar48 = piVar48 + 1;
              uStack_220 = uStack_220 + (iVar15 >> (uStack_224 - *piVar38 & 0x1f));
            } while (scratch->estimated_mantissa + iVar13 != piVar48);
            uStack_220 = uStack_220 / uVar40;
          }
          else {
            uStack_220 = 0;
            uStack_224 = 0xffffff9c;
          }
        }
        iVar13 = iVar6;
        if (0 < (int)uVar40) {
          piVar38 = (int *)((iVar31 + iVar13) * 4 + param_12);
          puVar7 = auStack_140 + (iVar50 - iVar31);
          piVar49 = scratch->tone_mantissa + iVar13;
          paVar39 = sqrt_cache + 4;
          iVar6 = iVar47;
          do {
            iVar47 = iVar6;
            if (iVar24 <= iVar50) {
              iVar47 = iVar6 + 1;
              iStack_25c = iVar6;
            }
            iVar24 = *(int *)(iVar47 * 4 + param_6);
            if (iVar29 == 0) {
              ((aac_analysis_envelope_workspace_t *)(piVar49 + -0x200))->estimated_mantissa[0] =
                   uStack_220;
              piVar49[-0x1c0] = uStack_224;
            }
            if (param_23 == 1) {
              piVar49[-0x1c0] = piVar49[-0x1c0] + 1;
              if (bVar2) {
                *puVar7 = 1;
              }
              else {
                *puVar7 = 0;
              }
            }
            piVar49[-0x180] = *piVar19;
            iVar6 = iStack_1b0 * param_7 + iStack_25c;
            piVar49[-0x140] = piVar19[0x122];
            piVar46 = (frame->envelope_and_noise).noise_exponent + iVar6;
            uVar14 = *piVar46;
            piVar10 = (frame->envelope_and_noise).noise_mantissa + iVar6;
            iVar6 = *piVar10;
            if ((int)uVar14 < 0) {
              iVar6 = iVar6 >> (-uVar14 & 0x1f);
              pv_div(iVar6,iVar6 + 0x3fffffff,&aStack_150);
            }
            else {
              pv_div(iVar6,(0x3fffffff >> (uVar14 & 0x1f)) + iVar6,&aStack_150);
            }
            uVar14 = piVar49[-0x180];
            iVar6 = aStack_150.mantissa >> (aStack_150.exponent & 0x1fU);
            iVar15 = ((aac_analysis_envelope_workspace_t *)(piVar49 + -0x200))->estimated_mantissa
                     [0] + 1;
            iVar6 = (int)((ulonglong)((longlong)iVar6 * (longlong)(int)uVar14) >> 0x20) * 4 +
                    (iVar6 * uVar14 >> 0x1e);
            if (bVar2) {
              pv_div(iVar6,iVar15,&aStack_150);
              pv_sqrt(aStack_150.mantissa,
                      ((piVar49[-0x140] - piVar49[-0x1c0]) - aStack_150.exponent) - 0x1e,&aStack_148
                      ,sqrt_cache + 1);
              piVar49[-0x100] = aStack_148.mantissa;
              piVar49[-0xc0] = aStack_148.exponent;
              if ((piVar49[0x80] == 0) || ((iStack_21c < iVar27 && (*piVar38 == 0)))) {
                uVar14 = 0;
                *piVar49 = 0;
              }
              else {
                uVar14 = *piVar46;
                if ((int)uVar14 < 0) {
                  pv_div(piVar49[-0x180],(*piVar10 >> (-uVar14 & 0x1f)) + 0x3fffffff,&aStack_150);
                  uVar14 = 0;
                }
                else {
                  pv_div(piVar49[-0x180],(0x3fffffff >> (uVar14 & 0x1f)) + *piVar10,&aStack_150);
                }
                pv_sqrt(aStack_150.mantissa,(piVar49[-0x140] - uVar14) - aStack_150.exponent,
                        &aStack_148,sqrt_cache + 2);
                *piVar49 = aStack_148.mantissa;
                uVar14 = aStack_148.exponent;
              }
            }
            else {
              if (iVar22 == 0) {
                iVar26 = iStack_260;
                paVar21 = paVar39;
                if (((aac_analysis_envelope_workspace_t *)(piVar49 + -0x200))->estimated_mantissa[0]
                    != 0) {
                  uVar25 = *piVar46;
                  if ((int)uVar25 < 0) {
                    if (-10 < (int)uVar25) {
                      iVar26 = (*piVar10 >> (-uVar25 & 0x1f)) + 0x3fffffff;
                      iVar15 = (int)((ulonglong)((longlong)iVar26 * (longlong)iVar15) >> 0x20) * 4 +
                               ((uint)(iVar26 * iVar15) >> 0x1e);
                    }
                    pv_div(uVar14,iVar15,&aStack_150);
                    uVar14 = (piVar49[-0x140] - aStack_150.exponent) - 0x1e;
                    if (((aac_analysis_envelope_workspace_t *)(piVar49 + -0x200))->
                        estimated_mantissa[0] != 0) {
                      uVar14 = uVar14 - piVar49[-0x1c0];
                    }
                    goto LAB_ram_43003596;
                  }
                  iVar26 = 0x3fffffff >> (uVar25 & 0x1f);
                }
                pv_div(uVar14,((uint)((iVar26 + *piVar10) * iVar15) >> 0x1e) +
                              (int)((ulonglong)((longlong)(iVar26 + *piVar10) * (longlong)iVar15) >>
                                   0x20) * 4,&aStack_150);
                uVar14 = (((piVar49[-0x140] - piVar49[-0x1c0]) - aStack_150.exponent) + -0x1e) -
                         *piVar46;
              }
              else {
                pv_div(uVar14,iVar15,&aStack_150);
                uVar14 = ((piVar49[-0x140] - piVar49[-0x1c0]) - aStack_150.exponent) - 0x1e;
                paVar21 = sqrt_cache + 3;
              }
LAB_ram_43003596:
              pv_sqrt(aStack_150.mantissa,uVar14,&aStack_148,paVar21);
              *piVar49 = 0;
              piVar49[-0xc0] = aStack_148.exponent;
              piVar49[-0x100] = aStack_148.mantissa;
              uVar14 = 0xffffff9c;
            }
            piVar49[0x40] = uVar14;
            uStack_210 = uStack_210 | *piVar49;
            pv_sqrt(iVar6,piVar49[-0x140],&aStack_148,sqrt_cache + 5);
            piVar49[-0x80] = aStack_148.mantissa;
            piVar49[-0x40] = aStack_148.exponent;
            iVar50 = iVar50 + 1;
            piVar38 = piVar38 + 1;
            puVar7 = puVar7 + 1;
            piVar49 = piVar49 + 1;
            iVar6 = iVar47;
          } while (iVar20 != iVar50);
          iVar24 = piStack_1f4[6];
          iVar13 = uVar40 + iVar13;
          goto LAB_ram_4300360e;
        }
        iVar24 = piStack_1f4[6];
        iVar50 = param_5[iVar24];
      }
      else {
        if (iVar29 == 0) {
          iVar24 = *piVar38;
          bVar2 = false;
          goto LAB_ram_4300363a;
        }
        iVar13 = iVar13 - uVar40;
LAB_ram_4300360e:
        iVar50 = param_5[iVar24];
      }
      if (iVar50 <= iVar18) goto LAB_ram_4300369a;
      piVar19 = piVar19 + 1;
      iVar50 = param_4[iVar24 * 0x3b + iVar18];
    } while( true );
  }
  uStack_210 = 0;
  goto LAB_ram_430036a8;
LAB_ram_4300369a:
  iStack_1c4 = iStack_1c4 + iVar18;
LAB_ram_430036a8:
  iVar24 = *piVar17;
  if (0 < iVar24) {
    iVar13 = 0;
    piVar38 = (int *)(iVar9 * 0x34 + param_14);
    do {
      piVar48 = piVar38 + 1;
      iVar47 = *piVar38;
      iVar50 = *piVar48;
      iVar13 = iVar13 + 1;
      if (iVar47 < iVar50) {
        iVar18 = iVar47 * 4;
        iVar5 = -100;
        piVar19 = scratch->estimated_mantissa + iVar47;
        iVar24 = -100;
        do {
          if (iVar24 < piVar19[0xc0]) {
            iVar24 = piVar19[0xc0];
          }
          piVar49 = piVar19 + 0x40;
          piVar19 = piVar19 + 1;
          if (iVar5 < *piVar49) {
            iVar5 = *piVar49;
          }
        } while (scratch->estimated_mantissa + iVar50 != piVar19);
        iVar20 = iVar50 - iVar47;
        if (iVar50 != iVar47) {
          do {
            iVar20 = iVar20 >> 1;
            iVar24 = iVar24 + 1;
          } while (iVar20 != 0);
        }
        piVar19 = scratch->estimated_mantissa + iVar47;
        iVar20 = 0;
        iVar6 = 0;
        do {
          piVar49 = piVar19 + 0x40;
          iVar6 = iVar6 + (piVar19[0x80] >> (iVar24 - piVar19[0xc0] & 0x1fU));
          iVar15 = *piVar19;
          piVar19 = piVar19 + 1;
          iVar20 = iVar20 + (iVar15 >> (iVar5 - *piVar49 & 0x1fU));
        } while (scratch->estimated_mantissa + iVar50 != piVar19);
        uVar40 = 0x10;
        iVar15 = 0x186a0000;
        if (iVar20 == 0) {
LAB_ram_43003756:
          iVar5 = (int)scratch->estimated_mantissa + iVar18;
          do {
            while( true ) {
              uVar25 = *(uint *)(iVar5 + 0x500);
              uVar14 = uVar25;
              if ((int)uVar25 < (int)uVar40) {
                uVar14 = uVar40;
              }
              if (*(int *)(iVar5 + 0x400) >> (uVar14 - uVar25 & 0x1f) <
                  iVar15 >> (uVar14 - uVar40 & 0x1f)) break;
              iVar47 = iVar47 + 1;
              pv_div(((uint)(iVar15 * *(int *)(iVar5 + 0x600)) >> 0x1c) +
                     (int)((ulonglong)((longlong)iVar15 * (longlong)*(int *)(iVar5 + 0x600)) >> 0x20
                          ) * 0x10,*(int *)(iVar5 + 0x400),&aStack_150);
              *(int *)(iVar5 + 0x400) = iVar15;
              *(int32_t *)(iVar5 + 0x600) = aStack_150.mantissa >> 2;
              *(uint *)(iVar5 + 0x700) =
                   ((*(int *)(iVar5 + 0x700) + uVar40) - aStack_150.exponent) -
                   *(int *)(iVar5 + 0x500);
              *(uint *)(iVar5 + 0x500) = uVar40;
              iVar50 = *piVar48;
              iVar5 = iVar5 + 4;
              if (iVar50 <= iVar47) goto LAB_ram_430037dc;
            }
            iVar47 = iVar47 + 1;
            iVar5 = iVar5 + 4;
          } while (iVar47 < iVar50);
LAB_ram_430037dc:
          iVar47 = *piVar38;
          if (iVar47 < iVar50) {
            iVar18 = iVar47 * 4;
            piVar19 = piVar32 + iVar47;
            iVar5 = -100;
            do {
              while( true ) {
                iVar20 = piVar19[-0x100] * 2 + piVar19[-0x200] + 0x1c;
                if (iVar5 < iVar20) {
                  iVar5 = iVar20;
                }
                if (piVar19[-0x40] == 0) break;
                iVar20 = *piVar19 << 1;
                if (iVar5 < *piVar19 << 1) goto LAB_ram_43003c72;
LAB_ram_4300381c:
                piVar19 = piVar19 + 1;
                if (piVar32 + iVar50 == piVar19) goto LAB_ram_43003822;
              }
              if ((iVar22 != 0) || (iVar20 = piVar19[-0x80] << 1, piVar19[-0x80] << 1 <= iVar5))
              goto LAB_ram_4300381c;
LAB_ram_43003c72:
              iVar5 = iVar20;
              piVar19 = piVar19 + 1;
            } while (piVar32 + iVar50 != piVar19);
LAB_ram_43003822:
            iVar5 = iVar5 + 1;
            piVar19 = scratch->tone_mantissa + iVar47;
            iVar20 = 0;
            do {
              while( true ) {
                iVar15 = piVar19[-0xc0] * 2 + piVar19[-0x1c0];
                if (iVar5 - iVar15 < 0x3b) {
                  iVar26 = piVar19[-0x100];
                  iVar26 = ((uint)(iVar26 * iVar26) >> 0x1c) +
                           (int)((ulonglong)((longlong)iVar26 * (longlong)iVar26) >> 0x20) * 0x10;
                  iVar20 = iVar20 + ((int)(((uint)(((aac_analysis_envelope_workspace_t *)
                                                   (piVar19 + -0x200))->estimated_mantissa[0] *
                                                  iVar26) >> 0x1c) +
                                          (int)((ulonglong)
                                                ((longlong)
                                                 ((aac_analysis_envelope_workspace_t *)
                                                 (piVar19 + -0x200))->estimated_mantissa[0] *
                                                (longlong)iVar26) >> 0x20) * 0x10) >>
                                    (iVar5 - (iVar15 + 0x1c) & 0x1fU));
                }
                iVar15 = *piVar19;
                if (iVar15 == 0) break;
                uVar40 = iVar5 + piVar19[0x40] * -2;
                if ((int)uVar40 < 0x1f) {
                  iVar20 = iVar20 + ((int)(((uint)(iVar15 * iVar15) >> 0x1c) +
                                          (int)((ulonglong)((longlong)iVar15 * (longlong)iVar15) >>
                                               0x20) * 0x10) >> (uVar40 & 0x1f));
                }
LAB_ram_43003858:
                piVar19 = piVar19 + 1;
                if (scratch->tone_mantissa + iVar50 == piVar19) goto LAB_ram_430038dc;
              }
              if ((iVar22 != 0) || (uVar40 = iVar5 + piVar19[-0x40] * -2, 0x1e < (int)uVar40))
              goto LAB_ram_43003858;
              iVar15 = piVar19[-0x80];
              piVar19 = piVar19 + 1;
              iVar20 = iVar20 + ((int)(((uint)(iVar15 * iVar15) >> 0x1c) +
                                      (int)((ulonglong)((longlong)iVar15 * (longlong)iVar15) >> 0x20
                                           ) * 0x10) >> (uVar40 & 0x1f));
            } while (scratch->tone_mantissa + iVar50 != piVar19);
LAB_ram_430038dc:
            if (iVar20 == 0) {
              iVar24 = 0x195bb900;
              if (uStack_210 == 0) {
LAB_ram_43003c7c:
                piVar19 = scratch->estimated_mantissa + iVar47;
                if (iVar47 < iVar50) {
                  do {
                    iVar47 = iVar47 + 1;
                    piVar19[0x100] =
                         ((uint)(iVar24 * piVar19[0x100]) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar24 * (longlong)piVar19[0x100]) >> 0x20) *
                         0x10;
                    piVar19[0x180] =
                         ((uint)(iVar24 * piVar19[0x180]) >> 0x1c) +
                         (int)((ulonglong)((longlong)iVar24 * (longlong)piVar19[0x180]) >> 0x20) *
                         0x10;
                    piVar19 = piVar19 + 1;
                  } while (iVar47 < *piVar48);
                  iVar24 = *piVar17;
                  goto LAB_ram_43003944;
                }
              }
              else {
LAB_ram_430038ee:
                piVar38 = (int *)(iVar18 + (int)piVar34);
                do {
                  iVar47 = iVar47 + 1;
                  *piVar38 = ((uint)(iVar24 * *piVar38) >> 0x1c) +
                             (int)((ulonglong)((longlong)iVar24 * (longlong)*piVar38) >> 0x20) *
                             0x10;
                  piVar38[0x80] =
                       ((uint)(iVar24 * piVar38[0x80]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar24 * (longlong)piVar38[0x80]) >> 0x20) * 0x10
                  ;
                  piVar38[0x100] =
                       ((uint)(iVar24 * piVar38[0x100]) >> 0x1c) +
                       (int)((ulonglong)((longlong)iVar24 * (longlong)piVar38[0x100]) >> 0x20) *
                       0x10;
                  piVar38 = piVar38 + 1;
                } while (iVar47 < *piVar48);
              }
            }
            else {
              pv_div(iVar6,iVar20,&aStack_150);
              pv_sqrt(aStack_150.mantissa,((iVar24 - iVar5) + -0x3a) - aStack_150.exponent,
                      &aStack_148,sqrt_cache + 7);
              if (aStack_148.exponent < -0x1b) {
                iVar24 = aStack_148.mantissa >> (-aStack_148.exponent - 0x1cU & 0x1f);
              }
              else {
                iVar24 = aStack_148.mantissa << (aStack_148.exponent + 0x1cU & 0x1f);
              }
              uVar40 = aStack_148.exponent;
              if (aStack_148.exponent < -0x1c) {
                uVar40 = 0xffffffe4;
              }
              iVar47 = *piVar38;
              iVar50 = *piVar48;
              if (0x195bb900 >> (uVar40 + 0x1c & 0x1f) <
                  aStack_148.mantissa >> (uVar40 - aStack_148.exponent & 0x1f)) {
                iVar24 = 0x195bb900;
              }
              if (uStack_210 == 0) goto LAB_ram_43003c7c;
              iVar18 = iVar47 << 2;
              if (iVar47 < iVar50) goto LAB_ram_430038ee;
            }
          }
        }
        else {
          pv_div(iVar6,iVar20,&aStack_150);
          pv_sqrt(aStack_150.mantissa,((iVar24 + -0x1e) - iVar5) - aStack_150.exponent,&aStack_148,
                  sqrt_cache + 6);
          iVar15 = (int)((ulonglong)
                         ((longlong)aStack_148.mantissa * (longlong)*(int *)(limGains + iVar30 * 4))
                        >> 0x20) * 4 +
                   ((uint)(aStack_148.mantissa * *(int *)(limGains + iVar30 * 4)) >> 0x1e);
          uVar40 = limGains._16_4_;
          if (iVar30 != 3) {
            uVar40 = aStack_148.exponent;
          }
          uVar14 = uVar40;
          if ((int)uVar40 < 0x10) {
            uVar14 = 0x10;
          }
          iVar47 = *piVar38;
          iVar50 = *piVar48;
          if (0x186a0000 >> (uVar14 - 0x10 & 0x1f) < iVar15 >> (uVar14 - uVar40 & 0x1f)) {
            iVar15 = 0x186a0000;
            uVar40 = 0x10;
          }
          iVar18 = iVar47 << 2;
          if (iVar47 < iVar50) goto LAB_ram_43003756;
        }
        iVar24 = *piVar17;
      }
LAB_ram_43003944:
      piVar38 = piVar48;
    } while (iVar13 < iVar24);
  }
  if (param_23 == 1) {
    sbr_aliasing_reduction
              (param_9,piVar34,piVar35,scratch,piVar33,auStack_140,uVar23,iVar31,sqrt_cache,
               scratch->reference_exponent);
    if (*param_13 != 0) {
      *param_13 = 0;
    }
    envelope_application_LC
              (param_2,piVar34,piVar35,piVar36,piVar37,scratch->tone_mantissa,piVar32,uStack_210,
               piVar8,param_10,param_11,iStack_21c,iVar31,uVar23,iVar22);
  }
  else {
    if (*param_13 != 0) {
      puVar7 = param_19;
      puVar11 = param_17;
      puVar42 = param_18;
      puVar44 = param_16;
      if (0 < iVar3) {
        do {
          memcpy(*puVar44,piVar34,iVar41);
          memcpy(*puVar42,piVar36,iVar41);
          memcpy(*puVar11,piVar35,iVar41);
          puVar44 = puVar44 + 1;
          memcpy(*puVar7,piVar37,iVar41);
          puVar7 = puVar7 + 1;
          puVar11 = puVar11 + 1;
          puVar42 = puVar42 + 1;
        } while (param_16 + iVar3 != puVar44);
      }
      *param_13 = 0;
    }
    envelope_application
              (param_2,param_3,piVar34,piVar35,piVar36,piVar37,scratch->tone_mantissa,piVar32,
               param_16,param_17,param_18,param_19,piVar8,param_10,param_11,iStack_21c,iVar31,uVar23
               ,iVar22,uStack_210,iVar3,uVar45);
  }
  iStack_21c = iStack_21c + 1;
  piStack_1f4 = piStack_1f4 + 1;
  if (iVar12 == iStack_21c) goto LAB_ram_430039fc;
  goto LAB_ram_430032a0;
}
