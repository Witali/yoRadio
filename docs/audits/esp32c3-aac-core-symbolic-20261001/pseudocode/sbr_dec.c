/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: sbr_dec @ ram:43010770
 * Types and parameter counts are inferred; verify against disassembly. */

/* WARNING: Type propagation algorithm not settling */

void sbr_dec(int param_1,int *param_2,aac_sbr_frame_abi_t *frame,int param_4,
            aac_sbr_control_abi_t *control,int *param_6,aac_ps_abi_t *ps,aac_analysis_core_t *core)

{
  undefined4 *puVar1;
  int32_t iVar2;
  int32_t *piVar3;
  uint32_t uVar4;
  aac_analysis_scratch_t *scratch;
  int iVar5;
  aac_analysis_scratch_t *paVar6;
  aac_analysis_scratch_t *paVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  int32_t (*paiVar14) [32];
  int *piVar15;
  int32_t *piVar16;
  uint uVar17;
  int32_t *piVar18;
  int32_t (*paiVar19) [48];
  int iVar20;
  undefined4 *puVar21;
  undefined4 *puVar22;
  int32_t (*paiVar23) [32];
  int32_t *piVar24;
  int32_t *piVar25;
  aac_analysis_envelope_workspace_t *paVar26;
  uint uVar27;
  int iVar28;
  aac_analysis_core_channel_t *paVar29;
  int iVar30;
  int iVar31;
  int iVar32;
  int32_t iVar33;
  aac_analysis_patch_t aStack_60;

  gp = &__global_pointer_;
  scratch = core->scratch;
  iVar2 = 0x20;
  if (param_4 != 0) {
    iVar2 = control->low_subband;
  }
  paiVar19 = frame->high_real_history;
  memmove(frame->high_real,paiVar19,0x480);
  iVar20 = control->low_complexity;
  if (iVar20 == 0) {
    memmove(frame->high_imag,frame->high_imag_history,0x480);
    iVar20 = control->low_complexity;
  }
  iVar28 = param_1 + 0x27e;
  iVar30 = 0;
  while( true ) {
    iVar5 = control->write_offset + iVar30;
    if (iVar20 == 1) {
      calc_sbr_anafilterbank_LC(frame->low_real + iVar5,iVar28,scratch,iVar2);
    }
    else {
      calc_sbr_anafilterbank(frame->low_real + iVar5,frame->low_imag + iVar5,iVar28,scratch,iVar2);
    }
    if (iVar30 == 0x1f) break;
    iVar30 = iVar30 + 1;
    iVar20 = control->low_complexity;
    iVar28 = iVar28 + 0x40;
  }
  uVar10 = 0x20;
  if (core->ltp_buffer_state == 0) {
    puVar21 = (undefined4 *)(param_1 + 0x800);
    puVar22 = (undefined4 *)(param_1 + 0xa40);
    do {
      uVar8 = *puVar21;
      uVar9 = puVar21[1];
      puVar22[2] = puVar21[2];
      *puVar22 = uVar8;
      puVar22[1] = uVar9;
      puVar1 = puVar21 + 3;
      puVar21 = puVar21 + 4;
      puVar22[3] = *puVar1;
      puVar22 = puVar22 + 4;
    } while (puVar21 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 != 0) goto LAB_ram_43010876;
LAB_ram_43010dd4:
    iVar20 = 0;
    do {
      memset((int)frame->high_real + iVar20,0,0xc0);
      iVar28 = (int)frame->high_imag + iVar20;
      iVar20 = iVar20 + 0xc0;
      memset(iVar28,0,0xc0);
    } while (iVar20 != 0x1c80);
  }
  else {
    puVar21 = (undefined4 *)(param_1 + 0x800);
    puVar22 = (undefined4 *)(param_1 + -0xa40);
    do {
      uVar8 = *puVar21;
      uVar9 = puVar21[1];
      puVar22[2] = puVar21[2];
      *puVar22 = uVar8;
      puVar22[1] = uVar9;
      puVar1 = puVar21 + 3;
      puVar21 = puVar21 + 4;
      puVar22[3] = *puVar1;
      puVar22 = puVar22 + 4;
    } while (puVar21 != (undefined4 *)(param_1 + 0xa40));
    if (param_4 == 0) goto LAB_ram_43010dd4;
LAB_ram_43010876:
    iVar20 = control->read_offset;
    iVar2 = (control->remaining).noise_band_count;
    iVar33 = (control->remaining).master_band_count;
    piVar3 = (frame->frame_control).frame_info;
    if (control->low_complexity == 1) {
      sbr_generate_high_freq
                (frame->low_real + iVar20,0,frame->high_real,0,
                 (frame->domain_and_inverse_filter).inverse_filter_mode,
                 (frame->domain_and_inverse_filter).previous_inverse_filter_mode,
                 (control->remaining).noise_bands + 1,iVar2,control->low_subband,
                 (control->remaining).master_bands,iVar33,control->output_rate,piVar3,
                 frame->alias_degree,scratch,frame->bandwidth,frame->previous_bandwidth,
                 &(control->remaining).patch_count,1,&control->high_subband);
      aStack_60.count = (control->remaining).patch_count;
      aStack_60.start_band[0] = (control->remaining).patch_start_band[0];
      aStack_60.start_band[1] = (control->remaining).patch_start_band[1];
      aStack_60.start_band[2] = (control->remaining).patch_start_band[2];
      aStack_60.start_band[3] = (control->remaining).patch_start_band[3];
      aStack_60.start_band[4] = (control->remaining).patch_start_band[4];
      aStack_60.start_band[5] = (control->remaining).patch_start_band[5];
      calc_sbr_envelope(frame,frame->high_real,0,(int *)&control->remaining,
                        (control->remaining).band_count,(int)(control->remaining).noise_bands,
                        (control->remaining).noise_band_count,(frame->frame_control).reset,
                        frame->alias_degree,&(frame->harmonics_and_envelopes).harmonic_index,
                        &(frame->harmonics_and_envelopes).phase_index,
                        (int)(frame->harmonics_and_envelopes).previous_harmonics,&frame->startup,
                        (int)(control->remaining).limiter_bands,(int)(control->remaining).gate_mode,
                        (undefined4 *)0x0,(undefined4 *)0x0,(undefined4 *)0x0,(undefined4 *)0x0,
                        (aac_analysis_envelope_workspace_t *)&scratch->program,&aStack_60,
                        (aac_analysis_sqrt_cache_t *)(control->remaining).sqrt_cache,
                        control->low_complexity);
    }
    else {
      sbr_generate_high_freq
                (frame->low_real + iVar20,frame->low_imag + iVar20,frame->high_real,frame->high_imag
                 ,(frame->domain_and_inverse_filter).inverse_filter_mode,
                 (frame->domain_and_inverse_filter).previous_inverse_filter_mode,
                 (control->remaining).noise_bands + 1,iVar2,control->low_subband,
                 (control->remaining).master_bands,iVar33,control->output_rate,piVar3,0,scratch,
                 frame->bandwidth,frame->previous_bandwidth,&(control->remaining).patch_count,
                 control->low_complexity,&control->high_subband);
      aStack_60.count = (control->remaining).patch_count;
      aStack_60.start_band[0] = (control->remaining).patch_start_band[0];
      aStack_60.start_band[1] = (control->remaining).patch_start_band[1];
      aStack_60.start_band[2] = (control->remaining).patch_start_band[2];
      aStack_60.start_band[3] = (control->remaining).patch_start_band[3];
      aStack_60.start_band[4] = (control->remaining).patch_start_band[4];
      aStack_60.start_band[5] = (control->remaining).patch_start_band[5];
      calc_sbr_envelope(frame,frame->high_real,frame->high_imag,(int *)&control->remaining,
                        (control->remaining).band_count,(int)(control->remaining).noise_bands,
                        (control->remaining).noise_band_count,(frame->frame_control).reset,0,
                        &(frame->harmonics_and_envelopes).harmonic_index,
                        &(frame->harmonics_and_envelopes).phase_index,
                        (int)(frame->harmonics_and_envelopes).previous_harmonics,&frame->startup,
                        (int)(control->remaining).limiter_bands,(int)(control->remaining).gate_mode,
                        (undefined4 *)(frame + 1),frame[1].domain_and_inverse_filter.envelope_domain
                        ,frame[1].harmonics_and_envelopes.add_harmonics + 0x21,
                        frame[1].harmonics_and_envelopes.add_harmonics + 0x61,
                        (aac_analysis_envelope_workspace_t *)&scratch->program,&aStack_60,
                        (aac_analysis_sqrt_cache_t *)(control->remaining).sqrt_cache,
                        control->low_complexity);
    }
    if (((core->mc).ps_present != 0) && (ps != (aac_ps_abi_t *)0x0)) {
      paVar29 = core->channel + 1;
      piVar3 = core->spectral[0].coefficients + 0x53;
      ps->qmf_real = (int32_t (*) [64])paVar29;
      ps->qmf_imag = (int32_t (*) [64])piVar3;
      iVar20 = 0;
      do {
        if (iVar20 < (frame->frame_control).frame_info[1] << 1) {
          uVar27 = control->previous_low_subband;
        }
        else {
          uVar27 = control->low_subband;
        }
        iVar28 = control->high_subband;
        piVar25 = (int32_t *)((int)paVar29->ltp_history + iVar20 * 0x40 * 4);
        piVar3 = piVar3 + iVar20 * 0x40;
        if (iVar28 < (int)uVar27) {
          iVar30 = 0x80;
          uVar27 = uVar10;
LAB_ram_43010a24:
          iVar28 = control->read_offset + iVar20;
          paiVar23 = frame->low_real + iVar28;
          paiVar14 = frame->low_imag + iVar28;
          iVar28 = 0;
          piVar18 = piVar25;
          piVar24 = piVar3;
          do {
            iVar5 = (*paiVar23)[0];
            iVar28 = iVar28 + 1;
            paiVar23 = (int32_t (*) [32])(*paiVar23 + 1);
            uVar12 = iVar5 << 1;
            if ((int)uVar12 >> 1 != iVar5) {
              uVar12 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *piVar18 = uVar12;
            iVar5 = (*paiVar14)[0];
            piVar18 = piVar18 + 1;
            paiVar14 = (int32_t (*) [32])(*paiVar14 + 1);
            uVar12 = iVar5 << 1;
            if ((int)uVar12 >> 1 != iVar5) {
              uVar12 = iVar5 >> 0x1f ^ 0x7fffffff;
            }
            *piVar24 = uVar12;
            piVar24 = piVar24 + 1;
          } while (iVar28 < (int)uVar27);
          iVar28 = control->high_subband;
        }
        else {
          iVar30 = uVar27 << 2;
          if (0 < (int)uVar27) goto LAB_ram_43010a24;
        }
        memcpy((int)piVar25 + iVar30,frame->high_real + iVar20 * 0x30,(iVar28 - uVar27) * 4);
        memcpy((int)piVar3 + iVar30,frame->high_imag + iVar20 * 0x30,
               (control->high_subband - uVar27) * 4);
        memset(piVar25 + control->high_subband,0,(0x40 - control->high_subband) * 4);
        iVar20 = iVar20 + 1;
        memset(piVar3 + control->high_subband,0,(0x40 - control->high_subband) * 4);
        paVar29 = (aac_analysis_core_channel_t *)ps->qmf_real;
        piVar3 = *ps->qmf_imag;
      } while (iVar20 != 0x20);
      piVar3 = piVar3 + 0x805;
      piVar25 = paVar29->overlap + 0x2e0;
      iVar20 = 0x20;
      do {
        paiVar23 = frame->low_imag + control->read_offset + iVar20;
        piVar18 = piVar25;
        piVar24 = piVar3 + -5;
        do {
          piVar16 = piVar24;
          iVar28 = paiVar23[-0x28][0];
          uVar10 = iVar28 << 1;
          if ((int)uVar10 >> 1 != iVar28) {
            uVar10 = iVar28 >> 0x1f ^ 0x7fffffff;
          }
          *piVar18 = uVar10;
          iVar28 = (*paiVar23)[0];
          piVar18 = piVar18 + 1;
          paiVar23 = (int32_t (*) [32])(*paiVar23 + 1);
          uVar10 = iVar28 << 1;
          if ((int)uVar10 >> 1 != iVar28) {
            uVar10 = iVar28 >> 0x1f ^ 0x7fffffff;
          }
          *piVar16 = uVar10;
          piVar24 = piVar16 + 1;
        } while (piVar16 + 1 != piVar3);
        iVar20 = iVar20 + 1;
        piVar3 = piVar16 + 0x41;
        piVar25 = piVar25 + 0x40;
      } while (iVar20 != 0x26);
      paiVar23 = frame->low_real;
      iVar20 = 0;
      if (0 < control->write_offset) {
        do {
          iVar28 = control->columns + iVar20;
          memmove(paiVar23,frame->low_real + iVar28,0x80);
          memmove(paiVar23 + 0x28,frame->low_imag + iVar28,0x80);
          iVar20 = iVar20 + 1;
          paiVar23 = paiVar23 + 1;
        } while (iVar20 < control->write_offset);
      }
      memmove(paiVar19,frame->high_real + 0x600,0x480);
      memmove(frame->high_imag_history,frame->high_imag + 0x600,0x480);
      piVar3 = scratch->words + 0x40;
      if ((core->mc).downsampled_sbr == 0) {
        memmove((int32_t *)((int)scratch + 0x2700),frame->synthesis,0x900);
      }
      else {
        memmove((int32_t *)((int)scratch + 0x1700),frame->synthesis,0x500);
      }
      iVar20 = 0;
      piVar25 = scratch->words + 0xcc;
      do {
        memmove(piVar25 + -0x2c,*(undefined4 *)((int)ps->hybrid->real_history + iVar20),0x30);
        puVar22 = (undefined4 *)((int)ps->hybrid->imag_history + iVar20);
        iVar20 = iVar20 + 4;
        memmove(piVar25,*puVar22,0x30);
        piVar25 = piVar25 + 0x58;
      } while (iVar20 != 0xc);
      memset((int)scratch + ps->upper_subband * 4,0,(0x40 - ps->upper_subband) * 4);
      memset(piVar3 + ps->upper_subband,0,(0x40 - ps->upper_subband) * 4);
      piVar25 = (int32_t *)((int)scratch + 0x1680);
      iVar28 = 0;
      uVar4 = 0;
      iVar20 = 0;
      do {
        iVar30 = iVar20;
        if ((ps->parameters).envelope_borders[iVar20] == uVar4) {
          iVar30 = iVar20 + 1;
          ps_init_stereo_mixing(ps,iVar20,control->high_subband);
        }
        ps_applied(ps,(int)*ps->qmf_real + iVar28,(int)*ps->qmf_imag + iVar28,scratch->words,piVar3,
                   (int32_t *)((int)scratch + 0x200));
        iVar20 = (int)*ps->qmf_real + iVar28;
        iVar5 = (int)*ps->qmf_imag + iVar28;
        if ((core->mc).downsampled_sbr == 0) {
          if ((int)uVar4 < 0x10) {
            iVar11 = *param_2;
            iVar32 = iVar28;
          }
          else {
            iVar11 = param_2[1];
            iVar32 = iVar28 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar20,iVar5,iVar11 + iVar32,(int)scratch + (0x2600 - iVar28),0);
        }
        else {
          calc_sbr_synfilterbank(iVar20,iVar5,uVar4 * 0x80 + *param_2,piVar25,1);
        }
        memmove((int)*ps->qmf_real + iVar28,scratch,0x100);
        uVar4 = uVar4 + 1;
        memmove((int)*ps->qmf_imag + iVar28,piVar3,0x100);
        iVar28 = iVar28 + 0x100;
        piVar25 = piVar25 + -0x20;
        iVar20 = iVar30;
      } while (uVar4 != 0x20);
      iVar20 = 0;
      piVar3 = scratch->words + 0xec;
      do {
        memmove(*(undefined4 *)((int)ps->hybrid->real_history + iVar20),piVar3 + -0x2c,0x30);
        puVar22 = (undefined4 *)((int)ps->hybrid->imag_history + iVar20);
        iVar20 = iVar20 + 4;
        memmove(*puVar22,piVar3,0x30);
        piVar3 = piVar3 + 0x58;
      } while (iVar20 != 0xc);
      memmove(frame->synthesis,scratch->words + 0x1c0,0x900);
      if ((core->mc).downsampled_sbr == 0) {
        memmove((int32_t *)((int)scratch + 0x2500),ps->right_synthesis,0x900);
      }
      else {
        memmove((int32_t *)((int)scratch + 0x1500),ps->right_synthesis,0x500);
      }
      piVar3 = (int32_t *)((int)scratch + 0x1480);
      iVar20 = 0;
      iVar28 = 0;
      do {
        iVar30 = (int)*ps->qmf_real + iVar20;
        iVar5 = (int)*ps->qmf_imag + iVar20;
        if ((core->mc).downsampled_sbr == 0) {
          if (iVar28 < 0x10) {
            iVar11 = *param_6;
            iVar32 = iVar20;
          }
          else {
            iVar11 = param_6[1];
            iVar32 = iVar20 + -0x1000;
          }
          calc_sbr_synfilterbank(iVar30,iVar5,iVar11 + iVar32,(int)scratch + (0x2400 - iVar20),0);
        }
        else {
          calc_sbr_synfilterbank(iVar30,iVar5,iVar28 * 0x80 + *param_6,piVar3,1);
        }
        iVar28 = iVar28 + 1;
        iVar20 = iVar20 + 0x100;
        piVar3 = piVar3 + -0x20;
      } while (iVar28 != 0x20);
      if ((core->mc).downsampled_sbr == 0) {
        memmove(ps->right_synthesis,scratch->words + 0x140,0x900);
        iVar2 = control->low_subband;
        (frame->frame_control).reset = 0;
        control->previous_low_subband = iVar2;
        return;
      }
      memmove(ps->right_synthesis,scratch->words + 0x140,0x500);
      (frame->frame_control).reset = 0;
      goto LAB_ram_4301128c;
    }
  }
  piVar3 = (scratch->program).side.tag + 0xb;
  if ((core->mc).downsampled_sbr == 0) {
    memmove((int32_t *)((int)scratch + 0x2200),frame->synthesis,0x900);
  }
  else {
    memmove((int32_t *)((int)scratch + 0x1200),frame->synthesis,0x500);
  }
  paVar26 = (aac_analysis_envelope_workspace_t *)((int)scratch + 0x2100);
  piVar25 = (int32_t *)((int)scratch + 0x1180);
  iVar20 = 0;
  iVar28 = 0;
  iVar30 = 0;
  do {
    iVar5 = control->low_complexity;
    iVar32 = control->read_offset + iVar30;
    paiVar14 = frame->low_real + iVar32;
    paVar6 = scratch;
    paiVar23 = paiVar14;
    if (param_4 == 0) {
      control->high_subband = 0x20;
      if (iVar5 != 1) goto LAB_ram_43010ea6;
LAB_ram_4301113e:
      uVar12 = 0;
      iVar31 = 0x10;
      iVar5 = iVar31;
      uVar27 = uVar10;
LAB_ram_4301114a:
      do {
        paVar6->words[0] = (*paiVar23)[0] >> 9;
        iVar31 = iVar31 + -1;
        paVar6->words[1] = (*paiVar23)[1] >> 9;
        paVar6 = (aac_analysis_scratch_t *)(paVar6->words + 2);
        paiVar23 = (int32_t (*) [32])(*paiVar23 + 2);
      } while (iVar31 != 0);
      paiVar14 = (int32_t (*) [32])(*paiVar14 + iVar5 * 2);
      paVar6 = (aac_analysis_scratch_t *)((int)scratch + (iVar5 + -1) * 8 + 8);
LAB_ram_43011172:
      paVar7 = paVar6;
      if (uVar12 != 0) {
        paVar7 = (aac_analysis_scratch_t *)(paVar6->words + 1);
        paVar6->words[0] = (*paiVar14)[0] >> 9;
      }
      iVar5 = control->high_subband;
      if ((int)uVar27 < iVar5) {
        piVar15 = (int *)((int)frame->high_real + iVar20);
        paVar6 = paVar7;
        do {
          paVar7 = (aac_analysis_scratch_t *)(paVar6->words + 1);
          uVar27 = uVar27 + 1;
          paVar6->words[0] = *piVar15 << 1;
          iVar5 = control->high_subband;
          piVar15 = piVar15 + 1;
          paVar6 = paVar7;
        } while ((int)uVar27 < iVar5);
      }
      memset(paVar7,0,(0x40 - iVar5) * 4);
      if ((core->mc).downsampled_sbr == 0) {
        if (iVar30 < 0x10) {
          iVar32 = *param_2;
          iVar5 = iVar28;
        }
        else {
          iVar32 = param_2[1];
          iVar5 = iVar28 + -0x1000;
        }
        calc_sbr_synfilterbank_LC(scratch,iVar32 + iVar5,paVar26,0);
      }
      else {
        calc_sbr_synfilterbank_LC(scratch,iVar30 * 0x80 + *param_2,piVar25,1);
      }
    }
    else {
      if (iVar30 < (frame->frame_control).frame_info[1] << 1) {
        uVar27 = control->previous_low_subband;
      }
      else {
        uVar27 = control->low_subband;
      }
      iVar11 = control->high_subband;
      if (iVar11 < (int)uVar27) {
        if (iVar5 == 1) goto LAB_ram_4301113e;
LAB_ram_43010ea6:
        uVar12 = 0;
        iVar31 = 0x10;
        iVar5 = 0x80;
        uVar27 = uVar10;
        uVar13 = uVar10;
LAB_ram_43010eb4:
        do {
          iVar11 = (*paiVar14)[0];
          paiVar14 = (int32_t (*) [32])(*paiVar14 + 1);
          uVar27 = uVar27 - 1;
          uVar17 = iVar11 << 1;
          if ((int)uVar17 >> 1 != iVar11) {
            uVar17 = iVar11 >> 0x1f ^ 0x7fffffff;
          }
          paVar6->words[0] = uVar17;
          paVar6 = (aac_analysis_scratch_t *)(paVar6->words + 1);
        } while (uVar27 != 0);
        iVar11 = control->high_subband;
        uVar27 = uVar13;
      }
      else {
        iVar31 = (int)uVar27 >> 1;
        uVar12 = uVar27 & 1;
        if (iVar5 == 1) {
          iVar5 = iVar31;
          if (iVar31 != 0) goto LAB_ram_4301114a;
          goto LAB_ram_43011172;
        }
        iVar5 = uVar27 << 2;
        uVar13 = uVar27;
        if (uVar27 != 0) goto LAB_ram_43010eb4;
        iVar31 = 0;
        uVar12 = 0;
        iVar5 = 0;
      }
      puVar22 = (undefined4 *)((int)scratch + iVar5);
      if ((int)uVar27 < iVar11) {
        puVar21 = (undefined4 *)((int)frame->high_real + iVar20);
        uVar13 = uVar27;
        do {
          uVar8 = *puVar21;
          uVar13 = uVar13 + 1;
          puVar21 = puVar21 + 1;
          *puVar22 = uVar8;
          iVar11 = control->high_subband;
          puVar22 = puVar22 + 1;
        } while ((int)uVar13 < iVar11);
      }
      memset(puVar22,0,(0x40 - iVar11) * 4);
      paiVar14 = frame->low_imag + iVar32;
      iVar32 = iVar31;
      paiVar23 = paiVar14;
      piVar18 = piVar3;
      if (iVar31 != 0) {
        do {
          iVar11 = (*paiVar23)[0];
          iVar32 = iVar32 + -1;
          uVar13 = iVar11 << 1;
          if ((int)uVar13 >> 1 != iVar11) {
            uVar13 = iVar11 >> 0x1f ^ 0x7fffffff;
          }
          *piVar18 = uVar13;
          iVar11 = (*paiVar23)[1];
          uVar13 = iVar11 << 1;
          if ((int)uVar13 >> 1 != iVar11) {
            uVar13 = iVar11 >> 0x1f ^ 0x7fffffff;
          }
          piVar18[1] = uVar13;
          paiVar23 = (int32_t (*) [32])(*paiVar23 + 2);
          piVar18 = piVar18 + 2;
        } while (iVar32 != 0);
        paiVar14 = (int32_t (*) [32])(*paiVar14 + iVar31 * 2);
        piVar18 = (int32_t *)((int)scratch + (iVar31 + -1) * 8 + 0x108);
      }
      if (uVar12 != 0) {
        iVar32 = (*paiVar14)[0];
        uVar12 = iVar32 << 1;
        if (iVar32 != (int)uVar12 >> 1) {
          uVar12 = iVar32 >> 0x1f ^ 0x7fffffff;
        }
        *piVar18 = uVar12;
      }
      iVar32 = control->high_subband;
      puVar22 = (undefined4 *)((int)piVar3 + iVar5);
      if ((int)uVar27 < iVar32) {
        puVar21 = (undefined4 *)((int)frame->high_imag + iVar20);
        do {
          uVar8 = *puVar21;
          uVar27 = uVar27 + 1;
          puVar21 = puVar21 + 1;
          *puVar22 = uVar8;
          iVar32 = control->high_subband;
          puVar22 = puVar22 + 1;
        } while ((int)uVar27 < iVar32);
      }
      memset(puVar22,0,(0x40 - iVar32) * 4);
      if ((core->mc).downsampled_sbr == 0) {
        if (iVar30 < 0x10) {
          iVar32 = *param_2;
          iVar5 = iVar28;
        }
        else {
          iVar32 = param_2[1];
          iVar5 = iVar28 + -0x1000;
        }
        calc_sbr_synfilterbank(scratch,piVar3,iVar32 + iVar5,paVar26,0);
      }
      else {
        calc_sbr_synfilterbank(scratch,piVar3,iVar30 * 0x80 + *param_2,piVar25,1);
      }
    }
    iVar30 = iVar30 + 1;
    iVar28 = iVar28 + 0x100;
    paVar26 = (aac_analysis_envelope_workspace_t *)((int)(paVar26 + 0xffffffff) + 0xf00);
    piVar25 = piVar25 + -0x20;
    iVar20 = iVar20 + 0xc0;
  } while (iVar30 != 0x20);
  if ((core->mc).downsampled_sbr == 0) {
    memmove(frame->synthesis,scratch->words + 0x80,0x900);
  }
  else {
    memmove(frame->synthesis,scratch->words + 0x80,0x500);
  }
  paiVar23 = frame->low_real;
  iVar20 = 0;
  if (0 < control->write_offset) {
    do {
      iVar28 = memmove(paiVar23,frame->low_real + control->columns + iVar20,0x80);
      iVar20 = iVar20 + 1;
      paiVar23 = (int32_t (*) [32])(iVar28 + 0x80);
    } while (iVar20 < control->write_offset);
  }
  memmove(paiVar19,frame->high_real + 0x600,0x480);
  if (control->low_complexity == 0) {
    paiVar23 = frame->low_imag;
    iVar20 = 0;
    if (0 < control->write_offset) {
      do {
        iVar28 = memmove(paiVar23,frame->low_imag + control->columns + iVar20,0x80);
        iVar20 = iVar20 + 1;
        paiVar23 = (int32_t (*) [32])(iVar28 + 0x80);
      } while (iVar20 < control->write_offset);
    }
    memmove(frame->high_imag_history,frame->high_imag + 0x600,0x480);
  }
  (frame->frame_control).reset = 0;
  if (param_4 == 0) {
    return;
  }
LAB_ram_4301128c:
  control->previous_low_subband = control->low_subband;
  return;
}
